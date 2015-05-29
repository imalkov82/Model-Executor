__author__ = 'imalkov'

import logging
import multiprocessing
import subprocess
import os
import timeit
import time
import socket

from modeltools.inputgroup.toporule import TopoInput
from inputgroup.faultrule import FaultInput


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

# def runcmd(cmd):
#     sys.stdout.flush()
#     proc = os.popen(cmd)
#     s = ""
#     while True:
#         line = proc.readline()
#         if line != '':
#             print(line.strip())
#             s += line
#             sys.stdout.flush()
#         else:
#             print("------------ completed -----------")
#             break
#     return s

def run_exeshcmd(arr3):
    print('run_exeshcmd --->')
    mdpath,shcommand = arr3
    print(mdpath)
    err_ans = []
    out_ans = []
    pdir = os.getcwd()
    os.chdir(mdpath)

    s = '\nexecute path: {0}'.format(mdpath)

    start_time = timeit.default_timer()
# code you want to evaluate
    p = subprocess.Popen(shcommand, stdin=subprocess.PIPE,stderr = subprocess.PIPE,stdout = subprocess.PIPE)
    if shcommand.find('Vtk') != -1:
        time.sleep(2)
        p.stdin.write(b'peout')
        # print >>p.stdin,'peout' # Python2.7
        p.stdin.close()
    p.wait()
    s += '\nfinished in {0} sec'.format(int(timeit.default_timer() - start_time))

    os.chdir(pdir)
    for line in iter(p.stderr.readline, b''):
        err_ans.append(line)
    for line in iter(p.stdout.readline, b''):
        out_ans.append(line)

    if err_ans == []:
        s+= "\n status: SUCCESS!"
    else:
        s+= '\n status: ERROR! {0}\n '.format('\n'.join(err_ans))
    logging.info(s)
    print('<--- run_exeshcmd')


def topo_input_stats(fpath):
    t = TopoInput(fpath)

def fault_input_stats(fpath):
    f = FaultInput(fpath)

def data_stats(fpath):
    pass

def collect_stats(root_path):
    s = ''
    input_path = os.path.join(root_path,'input')
    s += topo_input_stats(os.path.join(input_path, 'topo_parameters.txt'))
    s += fault_input_stats(os.path.join(input_path, 'fault_parameters.txt'))
    data_path =  os.path.join(root_path,'data')
    for step in os.listdir(data_path):
        s += '{0} stats: \n {1}'.format(step, data_stats(os.path.join(data_path, step)))
    logging.info(s)

def rundirs(plist, logfile, cmnd, dry_run = False, max_psize = 3):
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    logging.info('logger started')
    logging.info('max pool size = {0}'.format(max_psize))
    if socket.gethostname() == 'IMALKOV-PC' and 'Pecube' in cmnd:
        logging.error('Cannot execute {0} task on Home machine\n exit'.format(cmnd))
        return
    logging.info('cmd = {0}'.format(cmnd))
    try:
        for arr3 in list(chunks(sorted(plist), max_psize)):
            # p_stats = multiprocessing.Pool(psize)
            print('execute dir list: \n\t{0}'.format('\n\t'.join(arr3)))
            psize  = min(max_psize, len(arr3))
            if dry_run is False:
                logging.info('generate pool size = {0}'.format(psize))
                p = multiprocessing.Pool(psize)
                p.map(run_exeshcmd, zip(arr3, [cmnd] * len(arr3)))
    except TypeError as te:
        logging.error('run fail on Type Error! \n msg: {0} \n args: {1}'.format(te, '\n\t'.join(te.args)))
    except Exception as e:
        logging.error('run fail {0} , with error type {1}'.format(e , type(e)))