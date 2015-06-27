__author__ = 'imalkov'

import os, sys
import ast
from argparse import ArgumentParser
from configparser import ConfigParser

DEBUG_FLAG = False

def expose_mdlexe(f):
    def wrapper(*args):
        print('calling {0} with {1}'.format(type(args[0]).__name__, args[1]))
        i = 2
        if isinstance(args[0], MdlExecutor):
            i = 0
        print('state: {0}'.format(type(args[i].state).__name__))
        return f(*args)
    return wrapper

def runcmd(cmd, kls):
    global DEBUG_FLAG
    if DEBUG_FLAG is True:
        return
    sys.stdout.flush()
    print('cmd: {0}'.format(cmd))
    proc = os.popen(cmd)
    while True:
        line = proc.readline()
        if line != '':
            print(line.strip())
            sys.stdout.flush()
        else:
            print("------------ completed -----------")
            break
    exec_state = proc.close()
    if exec_state != None and exec_state != 256:
        raise Exception('{0} fail with {1}'.format(type(kls).__name__, exec_state))

class EnvState:
    @expose_mdlexe
    def process(self, remaining_arr, mdl_executor):
        cmd = 'python3 modelenv/mdlenv -c'
        runcmd(cmd, EnvState)
        if remaining_arr != [] and remaining_arr != None:
            state = remaining_arr[0]
            if state == 'run':
                mdl_executor.state = TestState()
            elif state == 'stat':
                mdl_executor.state = StatisticsState()
            elif state == 'plot':
                mdl_executor.state = GraphState()
            elif state == 'end':
                return None
            else:
                raise NotImplemented('{0}: state not found', self.__name__)
            remaining_arr = remaining_arr[1:]
        return remaining_arr

class TestState:
    @expose_mdlexe
    def process(self, remaining_arr, mdl_executor):
        cmd = 'python3 modelexe/mdlexec.py -m Test'
        runcmd(cmd, self)
        mdl_executor.state = PecubeState()
        return remaining_arr

class PecubeState:
    @expose_mdlexe
    def process(self, remaining_arr, mdl_executor):
        cmd = 'python3 modelexe/mdlexec.py -m Pecube'
        runcmd(cmd, self)
        mdl_executor.state = VtkState()
        return remaining_arr

class VtkState:
    @expose_mdlexe
    def process(self, remaining_arr, mdl_executor):
        cmd = 'python3 modelexe/mdlexec.py -m Vtk'
        runcmd(cmd, self)
        if remaining_arr != [] and remaining_arr != None:
            state = remaining_arr[0]
            if state == 'stat':
                mdl_executor.state = StatisticsState()
            elif state == 'plot':
                mdl_executor.state = GraphState()
            elif state == 'end':
                return None
            else:
                raise NotImplemented('{0}: state not found', self.__name__)
            remaining_arr = remaining_arr[1:]
        return remaining_arr

class CsvState:
    @expose_mdlexe
    def process(self, remaining_arr, mdl_executor):
        pass

class GraphState:
    @expose_mdlexe
    def process(self, remaining_arr, mdl_executor):
        data_ = ast.literal_eval(mdl_executor.mdl_conf['sub_data'])
        l = [n.strip() for n in ast.literal_eval(data_)]
        data_path = mdl_executor.mdl_conf['data_root'].replace('~', os.environ['HOME'])
        age_pic =  mdl_executor.mdl_conf['age_pic'].replace('~', os.environ['HOME'])
        geotherm_pic =  mdl_executor.mdl_conf['geoterm_pic'].replace('~', os.environ['HOME'])
        for node_path in [os.path.join(data_path, n) for n in l]:
            #convert files
            cmd = 'python3 modelanalysis/pecanalysis.py -i {0} -c'.format(node_path)
            runcmd(cmd,self)
            #create age-elevation
            cmd = 'python3 modelanalysis/pecanalysis.py -i {0} -o {1} -e'.format(node_path, age_pic)
            runcmd(cmd,self)
            #create temperature
            cmd = 'python3 modelanalysis/pecanalysis.py -i {0} -o {1} -tp'.format(node_path, geotherm_pic)
            runcmd(cmd,self)

        if remaining_arr !=[] and remaining_arr != None:
            state = remaining_arr[0]
            if state == 'stat':
                mdl_executor.state = StatisticsState()
            elif state == 'end':
                return None
            remaining_arr = remaining_arr[1:]
        return remaining_arr

class StatisticsState:
    @expose_mdlexe
    def process(self, remaining_arr, mdl_executor):
        data_ = ast.literal_eval(mdl_executor.mdl_conf['sub_data'])
        l = [n.strip() for n in ast.literal_eval(data_)]
        data_path = mdl_executor.mdl_conf['data_root'].replace('~', os.environ['HOME'])
        for node_path in [os.path.join(data_path,n) for n in l]:
            cmd = 'python3 modelanalysis/pecanalysis.py -i {0} -o {0} -ta'.format(node_path)
            runcmd(cmd, self)
            cmd = 'find {1} -name Age-Elevation0.csv | sort | xargs {0} -n 5 > {1}/age-elevation-stats-{0}.txt'.format('head', node_path)
            runcmd(cmd, self)

        if remaining_arr !=[] and remaining_arr != None:
            state = remaining_arr[0]
            if state == 'plot':
                mdl_executor.state = GraphState()
            elif state == 'end':
                return None
            remaining_arr = remaining_arr[1:]
        return remaining_arr

class InitState:
    @expose_mdlexe
    def process(self, remaining_arr, mdl_executor):
        if remaining_arr !=[] and remaining_arr != None:
            strt = remaining_arr[0]
            if strt == 'env':
                mdl_executor.state = EnvState()
            elif strt == 'run':
                mdl_executor.state = TestState()
            elif strt == 'stat':
                mdl_executor.state = StatisticsState()
            elif strt == 'plot':
                mdl_executor.state = GraphState()
            else:
                raise NotImplemented('{0}: state not found', self.__name__)
            remaining_arr = remaining_arr[1:]
        return remaining_arr

class MdlExecutor:
    def __init__(self, states_arr, config):
        self.states_arr = states_arr
        self.state = InitState()
        self.mdl_conf = config

    @expose_mdlexe
    def process(self, remaining_arr):
        remaining = self.state.process(remaining_arr, self)
        if remaining != [] and remaining != None:
            self.process(remaining)

    def start(self):
        self.process(self.states_arr)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument( "-l", dest="states_list", help="list of states to be executed: env, run, plot, stat", default= '[]')
    parser.add_argument( "-d", action="store_true", dest="debug", help="debug purpose", default= False)

    kvargs = parser.parse_args()
    sl = [n.strip() for n in ast.literal_eval(kvargs.states_list)] + ['end']
    config = ConfigParser()
    config.read('model.conf')
    DEBUG_FLAG = kvargs.debug

    mlexe = MdlExecutor(sl, config['Default'])
    mlexe.start()

