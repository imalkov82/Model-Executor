__author__ = 'imalkov'

import os
import sys
sys.path.append(os.getcwd())
from argparse import ArgumentParser
from configparser import ConfigParser
import pandas as pnd
import modelexe.mdlruncmd as runcmd
import multiprocessing
from modeltools.modelpursue.peclogger import ExecLogger


################################################
class ModelExecutor:
    model_state_dict = {'INIT': 0,
                        'PEC_PROPS': 1,
                        'BY_TASKS': 2,
                        'POOL_EXE': 3,
                        'EXEC_COMPLETE': 4,
                        'APP_COMPLETE': 5}

    def __init__(self, pec_model, peconf, max_psize, dry_run, single_index):
        self._peconf = peconf
        self._dry_run = dry_run
        self._wrk_list = []
        self._pec_model = pec_model
        self._cmd = './bin/{0}'.format(pec_model)
        self._max_psize = int(max_psize)
        self._observers = []
        self._single_index = int(single_index)
        self._state = ModelExecutor.model_state_dict['INIT']

    @property
    def peconf(self):
        return self._peconf
    @property
    def dry_run(self):
        return self._dry_run
    @property
    def wrk_list(self):
        return self._wrk_list
    @property
    def command(self):
        return self._cmd
    @property
    def pec_model(self):
        return self._pec_model
    @property
    def max_pool_size(self):
        return self._max_psize
    @property
    def bytask_list(self):
        return self._bytask_list

    def attach(self, observer):
        self._observers.append(observer)

    def _update_observers(self):
        for observer in self._observers:
            observer()

    def _get_wrk_list(self):
        self._state = ModelExecutor.model_state_dict['PEC_PROPS']
        topo_data = pnd.read_csv(self._peconf, header=0, usecols=['execution_directory', self._pec_model])
        if self._single_index >= 0:
            work_data = topo_data.iloc[[self._single_index]]
        else:
            work_data = topo_data[topo_data[self._pec_model] == 0]
        work_data['execution_directory'] = work_data['execution_directory'].apply(lambda x: x.replace('~', os.environ['HOME']))
        self._wrk_list = [p for i, p in work_data['execution_directory'].iteritems()]
        self._update_observers()
        return

    def _run_single_cmd(self):
        self._state = ModelExecutor.model_state_dict['POOL_EXE']
        self._psize = min(self._max_psize, len(self._sub_array))
        self._update_observers()
        p = multiprocessing.Pool(self._psize)
        p.map(runcmd.run_exeshcmd, zip(self._sub_array, [self._cmd] * len(self._sub_array)))
        self._state = ModelExecutor.model_state_dict['EXEC_COMPLETE']
        self._update_observers()

    def _split_by_task(self):
        self._state = ModelExecutor.model_state_dict['BY_TASKS']
        self._bytask_list = list(runcmd.chunks(sorted(self._wrk_list), self._max_psize))
        self._update_observers()
        return

    def __call__(self):
        self._update_observers()
        self._get_wrk_list()
        self._split_by_task()
        if self._dry_run is False:
            for sub_array in self._bytask_list:
                self._sub_array = sub_array
                self._run_single_cmd()

        self._state = ModelExecutor.model_state_dict['APP_COMPLETE']
        self._update_observers()

################################################

def main(model_name, dry_run):
    main_dir = '{0}/Dropbox/M.s/Research/DATA/SESSION_TREE/'.format(os.environ['HOME'])
    topo_data = pnd.read_csv('{0}/Dropbox/M.s/Research/DOCS/peconfig.csv'.format(os.environ['HOME']), names = ['execution_directory','col_num','row_num','step0','step1','step2', 'env', 'Test', 'Pecube', 'Vtk'])

    work_data = topo_data[topo_data[model_name] == 0]
    work_data['execution_directory'] = work_data['execution_directory'].apply(lambda x : x.replace('~', os.environ['HOME']))
    wrk_list = [p for i, p in work_data['execution_directory'].iteritems()]
    log_name = 'log{1}_{0}.txt'.format(model_name, os.getpid())
    log_path = os.path.join(main_dir,log_name)
    print('log: {0}'.format(log_path))
    runcmd.rundirs(wrk_list, log_path, cmnd = "./bin/{0}".format(model_name),dry_run=dry_run,  max_psize=min(len(wrk_list),3))

if __name__ == '__main__':
    parser = ArgumentParser()
    #set cmd rules
    parser.add_argument( "-m", dest="pec_model", help="model for execution", default= '')
    parser.add_argument( "-s", action="store_true", dest="stats", help="collect statistics on model", default= False)
    parser.add_argument( "-r", action="store_true", dest="dry_run", help="dry run", default= False)
    parser.add_argument( "-i", dest="single_index", help="single file index", default= -1)
    kvargs = parser.parse_args()
    #set config rules
    config = ConfigParser()
    config.read('./model.conf')

    #execute
    modexec = ModelExecutor(kvargs.pec_model, config['Default']['peconfig'].replace('~', os.environ['HOME']),
                            config['Execute']['max_pool_size'], kvargs.dry_run, kvargs.single_index)
    exe_logger = ExecLogger(modexec)
    modexec.attach(exe_logger)
    modexec()
    # main(kvargs.model, kvargs.dry_run)
