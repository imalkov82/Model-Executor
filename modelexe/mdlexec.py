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

    def __init__(self, pec_model, peconf, max_psize, dry_run):
        self._peconf = peconf
        self._dry_run = dry_run
        self._wrk_list = []
        self._pec_model = pec_model
        self._cmd = './bin/{0}'.format(pec_model)
        self._max_psize = max_psize
        self._observers = []
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
        topo_data = pnd.read_csv(self._peconf, names=['execution_directory', 'col_num', 'row_num',
                                                      'step0', 'step1', 'step2', 'env', 'Test', 'Pecube', 'Vtk'],
                                 usecols=['execution_directory', self._pec_model])
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

    # def _runcmd(self):
    #     try:
    #         for arr3 in self._bytask_list:
    #             print('execute dir list: \n\t{0}'.format('\n\t'.join(arr3)))
    #             self._psize = min(self._max_psize, len(arr3))
    #             if self._dry_run is False:
    #                 # logging.info('generate pool size = {0}'.format(psize))
    #                 p = multiprocessing.Pool(self._psize)
    #                 p.map(runcmd.run_exeshcmd, zip(arr3, [self._cmd] * len(arr3)))
    #     except Exception as e:
    #         self._err_str = ('run fail with error: {0} , \n error type {1}'.format(e ,type(e)))
    #     finally:
    #         self._update_observers()

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
#
# node2_dir =  os.path.join(main_dir, 'NODE02')
# node3_dir =  os.path.join(main_dir, 'NODE03')
#
# l1 = [os.path.join(node3_dir, el) for el in os.listdir(node3_dir)]
# l2 = [os.path.join(node2_dir,d) for d in ['Session1D','Session1E','Session1F','Session2A','Session2B','Session2C']]
# runcmd.rundirs(l1+l2, os.path.join(main_dir,'log{0}.txt'.format(os.getpid())), cmnd = "./bin/Pecube")

POOL_SIZE = 3

def main(model_name, dry_run):
    main_dir = '{0}/Dropbox/M.s/Research/DATA/SESSION_TREE/'.format(os.environ['HOME'])
    topo_data = pnd.read_csv('{0}/Dropbox/M.s/Research/DOCS/peconfig.csv'.format(os.environ['HOME']), names = ['execution_directory','col_num','row_num','step0','step1','step2', 'env', 'Test', 'Pecube', 'Vtk'])

    work_data = topo_data[topo_data[model_name] == 0]
    work_data['execution_directory'] = work_data['execution_directory'].apply(lambda x : x.replace('~', os.environ['HOME']))
    wrk_list = [p for i, p in work_data['execution_directory'].iteritems()]
    log_name = 'log{1}_{0}.txt'.format(model_name, os.getpid())
    log_path = os.path.join(main_dir,log_name)
    print('log: {0}'.format(log_path))
    runcmd.rundirs(wrk_list, log_path, cmnd = "./bin/{0}".format(model_name),dry_run=dry_run,  max_psize=min(len(wrk_list),POOL_SIZE))

if __name__ == '__main__':
    parser = ArgumentParser()
    #set rules
    parser.add_argument( "-m", dest="pec_model", help="model for execution", default= '')
    parser.add_argument( "-s", action="store_true", dest="stats", help="collect statistics on model", default= False)
    parser.add_argument( "-r", action="store_true", dest="dry_run", help="dry run", default= False)
    # parser.add_argument( "-l", dest="bin_path_arg", help="source directory of binary files", default= '')
    # parser.add_argument( "-g", action="store_true", dest="gen_env", help="generate environment flag", default=False)
    # parser.add_argument( "-c", action="store_true", dest="cyn_flag", help="generate 3D geomery (default is 2D)", default=False)
    # parser.add_argument( "-p", action="store_true", dest="disp_path", help="display path only (no calculation)", default=False)
    # parser.add_argument( "-w", action="store_true", dest="update_csv", help="update csv file after execution", default=False)
    kvargs = parser.parse_args()

    config = ConfigParser()
    # config.read('{0}/Documents/pycharm_workspace/Model-Executor/model.conf'.format(os.environ['HOME']))
    config.read('./model.conf')
    print(config.sections())
    # modexec = ModelExecutor(kvargs.pec_model, config['Default']['peconfig'].replace('~', os.environ['HOME']), POOL_SIZE, kvargs.dry_run)
    # exe_logger = ExecLogger(modexec)
    # modexec.attach(exe_logger)
    # modexec()
    # main(kvargs.model, kvargs.dry_run)
