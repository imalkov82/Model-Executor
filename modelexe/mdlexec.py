__author__ = 'imalkov'

import os
from argparse import ArgumentParser

import pandas as pnd

from modelexe import runcmd


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
    parser.add_argument( "-m", dest="model", help="model for execution", default= '')
    parser.add_argument( "-s", action="store_true", dest="stats", help="collect statistics on model", default= False)
    parser.add_argument( "-r", action="store_true", dest="dry_run", help="dry run", default= False)
    # parser.add_argument( "-l", dest="bin_path_arg", help="source directory of binary files", default= '')
    # parser.add_argument( "-g", action="store_true", dest="gen_env", help="generate environment flag", default=False)
    # parser.add_argument( "-c", action="store_true", dest="cyn_flag", help="generate 3D geomery (default is 2D)", default=False)
    # parser.add_argument( "-p", action="store_true", dest="disp_path", help="display path only (no calculation)", default=False)
    # parser.add_argument( "-w", action="store_true", dest="update_csv", help="update csv file after execution", default=False)

    kvargs = parser.parse_args()

    main(kvargs.model, kvargs.dry_run)
