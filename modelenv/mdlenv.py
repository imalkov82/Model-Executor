__author__ = 'imalkov'

import shutil
import os
import sys
sys.path.append(os.getcwd())
import pandas as pnd
from datetime import datetime
from modeltools.modelinput.faultrule import FaultInput
from modeltools.modelinput.toporule import TopoInput
from configparser import ConfigParser
from modeltools.modelinput.datarule import StepInput
from modelexe.mdlruncmd import runcmd
from argparse import ArgumentParser

def parse_to_int(f):
    def wrap(*args, **kwargs):
        args_res = []
        for a in args:
            if isinstance(a, str):
                args_res.append(int(a))
            else:
                args_res.append(a)
        return f(*args_res, **kwargs)
    return wrap

def replace2env(f):
    """ DECORATOR: STRIP STR """
    def wrap(*args, **kwargs):
        args_res = []
        for a in args:
            if isinstance(a, str):
                args_res.append(a.replace('~',os.environ['HOME']))
            else:
                args_res.append(a)

        return f(*args_res, **kwargs)
    return wrap

class EnvNode:
    type_dict = {0: 'directory',
                 1: 'file',
                 2: 'abstract'}

    def __init__(self,  path, node_type, env_context = None, operation = None):
        self._child_nodes = []
        self._type = node_type
        self._path = path
        self._exist = os.path.exists(path)
        self._env_context = env_context
        self._operation = operation

    def attach_child_node(self, env_node):
        self._child_nodes.append(env_node)

    def backup_env(self):
        if self._type == 1:
            if os.path.exists(self._path):
                shutil.move(self._path, '{0}_{1}'.format(self._path, str(datetime.now().time()).replace(':','_')))
                print('backup file:{0}'.format(self._path))
        else:
            [node.backup_env() for node in self._child_nodes]

    def generate_env(self):
        if self._type == 1:
            self._operation(self._env_context, self._path)
        else:
            if self._exist is False and self._type != 2:
                os.mkdir(self._path)
                self._exist = True
            [node.generate_env() for node in self._child_nodes]

    def illustrate(self, tab_str = ''):
        if self._type != 2:
            a, b = os.path.split(self._path)
            if b == '':
                _, b = os.path.split(a)
            print('{2}|{0}({1})'.format(b, self._exist, tab_str))
        if self._type != 1:
            tab_str += '--'
            [node.illustrate(tab_str) for node in self._child_nodes]

    @property
    def env_context(self):
        return self._env_context

    @property
    def type(self):
        return EnvNode.type_dict[self._type]

class PecubeInputDir(EnvNode):
    def __init__(self, path, topo_src, fault_src, topo_diff , fault_diff):
        self._root_path = path
        input_dir = os.path.join(path, 'input')
        super().__init__(input_dir, 0)
        self._map_env(topo_src, fault_src, topo_diff , fault_diff)

    def create_file_factory(self, type):
        type_diff = '{0}_diff'.format(type)
        type_src = '{0}_src'.format(type)
        def create_file(context, out_path):
            for key,val in context[type_diff].items():
                setattr(context[type_src], key, val)
            context[type_src].save_to_file(out_path)
        return create_file

    @replace2env
    def _map_env(self, topo_src, fault_scr, topo_diff , fault_diff):
        try:
            #topo
            topoconf = ConfigParser()
            topoconf.read(topo_diff)
            topo_context = {}
            topo_context['topo_diff'] = dict(topoconf.items('Default'))
            topo_context['topo_src'] = TopoInput(topo_src)

            #fault
            faultconf = ConfigParser()
            faultconf.read(fault_diff)
            fault_context = {}
            fault_context['fault_diff'] = dict(faultconf.items('Default'))
            fault_context['fault_src'] = FaultInput(fault_scr)

            super().attach_child_node(EnvNode(os.path.join(self._path,'topo_parameters.txt'), 1,
                                                           topo_context, self.create_file_factory('topo')))

            super().attach_child_node(EnvNode(os.path.join(self._path,'fault_parameters.txt'), 1,
                                                           fault_context, self.create_file_factory('fault')))

        except Exception as e:
            raise e

class PecubeDataDir(EnvNode):
    def __init__(self, path, esc_ang, cyn_ang, grid_type, row_num, col_num, steps):
        self._root_path = path
        data_dir = os.path.join(path, 'data')
        super().__init__(data_dir, 0)
        self._map_env(esc_ang, cyn_ang, grid_type, row_num, col_num, steps)

    @parse_to_int
    def _map_env(self, esc_ang, cyn_ang, grid_type, row_num, col_num, steps):
        for i, mhigt in enumerate(steps):
            step_name = 'step{0}.txt'.format(i)
            stepi = StepInput(step_name, esc_ang, cyn_ang, grid_type, row_num, col_num, mhigt)
            super().attach_child_node(EnvNode(os.path.join(self._path, step_name), 1, stepi,
                                              lambda env_context, out_path: env_context.save_to_file(out_path)))

class PecubePEOutDir(EnvNode):
    def __init__(self, path, out_name):
        self._root_path = path
        data_dir = os.path.join(path, out_name)
        super().__init__(data_dir, 0)
        self._map_env()

    def _map_env(self):
        dir_names = ['Ages00{0}.txt'.format(i) for i in range(3)]
        dir_names += ['Pecube.out']
        for name in dir_names:
            super().attach_child_node(EnvNode(os.path.join(self._path, name), 1, [],
                                              lambda env_context, out_path: True))


class PecubeBinDir(EnvNode):
    def __init__(self, path, bin_dir):
        self._root_path = path
        data_dir = os.path.join(path, 'bin')
        super().__init__(data_dir, 0)
        self._map_env(bin_dir)

    @staticmethod
    def mksoft_link(env_context, out_dir):
        pdir = os.getcwd()
        p,name = os.path.split(out_dir)
        os.chdir(p)
        runcmd('ln -s {0} {1}'.format(os.path.join(env_context['dir'], name), name))
        os.chdir(pdir)

    @replace2env
    def _map_env(self, bin_dir):
        for name in os.listdir(bin_dir):
            super().attach_child_node(EnvNode(os.path.join(self._path, name), 1,
                                              {'dir':bin_dir}, PecubeBinDir.mksoft_link))

class PecubeVtkDir(EnvNode):
    def __init__(self, path):
        self._root_path = path
        data_dir = os.path.join(path, 'VTK')
        super().__init__(data_dir, 0)

class SessionEnv(EnvNode):
    def __init__(self, root_path, esc_ang, cyn_ang, col_num, row_num, grid_type,
                 steps, topo_input, fault_input, bin_path, topo_diff, fault_diff):

        super().__init__(root_path.replace('~', os.environ['HOME']), 0)

        self._map_env(esc_ang, cyn_ang, col_num, row_num, grid_type,
                      steps, topo_input, fault_input, bin_path, topo_diff, fault_diff)

    def _map_env(self, esc_ang, cyn_ang, col_num, row_num, grid_type,
                      steps, topo_input, fault_input, bin_path, topo_diff, fault_diff):
        # INPUT
        super().attach_child_node(PecubeInputDir(self._path, topo_input, fault_input, topo_diff, fault_diff))
        # DATA
        super().attach_child_node(PecubeDataDir(self._path, esc_ang, cyn_ang, grid_type,
                                                       row_num, col_num ,steps))
        # VTK
        super().attach_child_node(PecubeVtkDir(self._path))
        # BIN
        super().attach_child_node(PecubeBinDir(self._path, bin_path))
        # OUTPUT
        super().attach_child_node(PecubePEOutDir(self._path, 'peout'))



    def __call__(self, *args, **kwargs):
        pass

class ModelEnv(EnvNode):
    def __init__(self, mdl_conf_path):
        super().__init__('', 2)
        self._map_env(mdl_conf_path)

    def _map_env(self, mdl_conf_path):
        config = ConfigParser()
        # config.read('./model.conf')
        config.read(mdl_conf_path)
        conf_env = config['Environment']
        #extract data
        pec_file = config['Default']['peconfig']
        topo_data = pnd.read_csv(pec_file.replace('~', os.environ['HOME']), header=0)

        wrk_data = topo_data[topo_data['env'] == 0]
        wrk_data['execution_directory'] = wrk_data['execution_directory'].apply(lambda x : x.replace('~', os.environ['HOME']))
        #map sessions
        for _ , s in wrk_data.iterrows():
            super().attach_child_node(SessionEnv(s['execution_directory'], conf_env['escarpment_angle'], conf_env['canyon_angle'],
                                             s['col_num'], s['row_num'], s['grid_type'],
                                             [s['step{0}'.format(i)]for i in range(int(conf_env['steps_num']))],
                                             s['sample'] + 'input/topo_parameters.txt', s['sample'] + 'input/fault_parameters.txt',
                                             conf_env['bin_dir'], conf_env['topo_diff'], conf_env['fault_diff']))
    def __call__(self, *args, **kwargs):
        pass

if __name__ == "__main__":
    parser = ArgumentParser()
    #set rules
    parser.add_argument( "-c", action="store_true", dest="create_env", help="create enviroment and overide the existing files", default=False)
    parser.add_argument( "-b", action="store_true", dest="backup_env", help="backup enviroment", default=False)
    parser.add_argument( "-d", action="store_true", dest="env_dbg", help="debug flag", default=False)
    parser.add_argument( "-l", action="store_true", dest="ill_env", help="illusrtate enviroment", default=False)
    kvargs = parser.parse_args()


    if kvargs.env_dbg:
        mdl_env = ModelEnv('../model.conf')
    else:
        mdl_env = ModelEnv('./model.conf')

    if kvargs.ill_env:
        mdl_env.illustrate()
        sys.exit(0)

    if kvargs.backup_env:
        mdl_env.backup_env()

    if kvargs.create_env:
        mdl_env.generate_env()