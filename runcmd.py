__author__ = 'imalkov'

import logging
import multiprocessing
import subprocess
import os
import timeit
import time
import socket

def split_by_psize(plist, psize):
    start = 0
    arr = []
    logging.info('split working dir list by size {0}'.format(psize))
    for i in range(psize,len(plist)+1,psize):
        if i >= len(plist):
            arr.append(plist[start:])
        else:
            arr.append(plist[start:i])
        start = i
    return arr

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
    mdpath,shcommand = arr3
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
        print >>p.stdin,'peout'
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

def topo_input_stats(fpath):
    pass

def fault_input_stats(fpath):
    pass

def steps_stats(fpath):
    pass

def collect_stats(root_path):
    s = ''
    input_path = os.path.join(root_path,'input')
    s += topo_input_stats(os.path.join(input_path, 'topo_parameters.txt'))
    s += fault_input_stats(os.path.join(input_path, 'fault_parameters.txt'))
    data_path =  os.path.join(root_path,'data')
    for step in os.listdir(data_path):
        s += '{0} stats: \n {1}'.format(step, steps_stats(os.path.join(data_path, step)))
    logging.info(s)

def rundirs(plist, logfile, cmnd, psize = 3):
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    logging.info('logger started')
    logging.info('generate pool size = {0}'.format(psize))
    if socket.gethostname() == 'IMALKOV-PC' and 'Pecube' in cmnd:
        logging.error('Cannot execute {0} task on Home machine\n exit'.format(cmnd))
        return
    logging.info('cmd = {0}'.format(cmnd))
    try:
        for arr3 in split_by_psize(sorted(plist), psize):
            p_stats = multiprocessing.Pool(psize)
            p = multiprocessing.Pool(psize)
            p.map(run_exeshcmd, zip(arr3 , [cmnd] * len(arr3)))
    except Exception as e:
        logging.error('run fail {0}'.format(e))

