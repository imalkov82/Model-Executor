__author__ = 'imalkov'

import runcmd
import os
import pandas as pnd
from argparse import ArgumentParser

#
# node2_dir =  os.path.join(main_dir, 'NODE02')
# node3_dir =  os.path.join(main_dir, 'NODE03')
#
# l1 = [os.path.join(node3_dir, el) for el in os.listdir(node3_dir)]
# l2 = [os.path.join(node2_dir,d) for d in ['Session1D','Session1E','Session1F','Session2A','Session2B','Session2C']]
# runcmd.rundirs(l1+l2, os.path.join(main_dir,'log{0}.txt'.format(os.getpid())), cmnd = "./bin/Pecube")



def main(model_name):
    main_dir = '{0}/Dropbox/M.s/Research/DATA/SESSION_TREE/'.format(os.environ['HOME'])
    topo_data = pnd.read_csv('{0}/Dropbox/M.s/Research/DOCS/peconfig.csv'.format(os.environ['HOME']), names = ['execution_directory','col_num','row_num','step0','step1','step2', 'env', 'Test', 'Pecube'])

    work_data = topo_data[topo_data[model_name] == 0]
    work_data['execution_directory'] = work_data['execution_directory'].apply(lambda x : x.replace('~', os.environ['HOME']))
    wrk_list = [p for i, p in work_data['execution_directory'].iteritems()]
    log_name = 'log_{0}.txt'.format(os.getpid())
    log_path = os.path.join(main_dir,log_name)
    print('log: {0}'.format(log_path))
    runcmd.rundirs(wrk_list, log_path, cmnd = "./bin/{0}".format(model_name))

if __name__ == '__main__':
    parser = ArgumentParser()
    #set rules
    parser.add_argument( "-m", dest="model", help="model for execution", default= '')
    kvargs = parser.parse_args()

    main(kvargs.model)
