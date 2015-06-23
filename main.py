__author__ = 'imalkov'

import os, sys
import ast
from argparse import ArgumentParser
from configparser import ConfigParser

def runcmd(cmd, kls):
    sys.stdout.flush()
    proc = os.popen(cmd)
    s = ""
    while True:
        line = proc.readline()
        if line != '':
            print(line.strip())
            s += line
            sys.stdout.flush()
        else:
            print("------------ completed -----------")
            break

    exec_state = proc.close()
    if exec_state != None or exec_state != 256:
        raise Exception('{0} fail'.format(kls.__name__))

class EnvState:
    def process(self, remaining_arr, mdl_executor):
        cmd = 'python3 modelenv/mdlenv -c'
        runcmd(cmd, EnvState)
        state = remaining_arr[0]
        if state == 'run':
            mdl_executor.state = TestState()
        elif state == 'stat':
            mdl_executor.state = StatisticsState()
        elif state == 'plot':
            mdl_executor.state = GraphState()
        else:
            raise NotImplemented('{0}: state not found', self.__name__)
        return remaining_arr[1:]

class TestState:
    def process(self, remaining_arr, mdl_executor):
        cmd = 'python3 modelexe/mdlexec.py -m Test'
        runcmd(cmd, TestState)
        mdl_executor.state = PecubeState()
        return remaining_arr

class PecubeState:
    def process(self, remaining_arr, mdl_executor):
        cmd = 'python3 modelexe/mdlexec.py -m Pecube'
        runcmd(cmd, PecubeState)
        mdl_executor.state = VtkState()
        return remaining_arr

class VtkState:
    def process(self, remaining_arr, mdl_executor):
        cmd = 'python3 modelexe/mdlexec.py -m Vtk'
        runcmd(cmd, VtkState)
        state = remaining_arr[0]
        if state == 'stat':
            mdl_executor.state = StatisticsState()
        elif state == 'plot':
            mdl_executor.state = GraphState()
        else:
            raise NotImplemented('{0}: state not found', self.__name__)
        return remaining_arr[1:]

class CsvState:
    def process(self, remaining_arr, mdl_executor):
        pass

class GraphState:
    def process(self, remaining_arr, mdl_executor):
        pass

class StatisticsState:
    def process(self, remaining_arr, mdl_executor):
        pass

class InitState:
    def process(self, remaining_arr, mdl_executor):
        strt = remaining_arr[0]
        if strt == 'env':
            mdl_executor.state = EnvState()
        elif strt == 'run':
            pass
        elif strt == 'stat':
            mdl_executor.state = StatisticsState()
        elif strt == 'plot':
            mdl_executor.state = GraphState()
        else:
            raise NotImplemented('{0}: state not found', self.__name__)
        return remaining_arr[1:]


class MdlExecutor:
    def __init__(self, states_arr, config):
        self.states_arr = states_arr
        self.state = InitState()
        self.mdl_conf = config

    def process(self, remaining_arr):
        remaining = self.state.process(remaining_arr, self)
        if remaining != []:
            self.process(remaining)

    def start(self):
        self.process(self.states_arr)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument( "-l", dest="states_list", help="list of states to be executed", default= '[]')

    kvargs = parser.parse_args()
    sl = [n.strip() for n in ast.literal_eval(kvargs.states_list)]

    config = ConfigParser()
    config.read('model.conf')
