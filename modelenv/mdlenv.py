__author__ = 'imalkov'

import shutil
import os
import pandas as pnd
from datetime import datetime
from modeltools.modelinput.faultrule import FaultInput
from modeltools.modelinput.toporule import TopoInput
from configparser import ConfigParser
from modeltools.modelinput.datarule import StepInput

class EnvNode:
    type_dict = {0: 'directory',
                 1: 'file'}

    def __init__(self,  path, node_type):
        self._child_nodes = []
        self._type = node_type
        self._path = path

    def attach_child_node(self, env_node):
        self._child_nodes.append(env_node)

    def backup_env(self):
        for env_node in self._child_nodes:
            if env_node.type == 1:
                shutil.copy2(self._path, '{0}_{1}'.format(self._path, datetime.now().time().replace(':','_')))
            else:
                for child_node in self._child_nodes:
                    child_node.backup_env()
    @property
    def type(self):
        return EnvNode.type_dict[self._type]

class PecubeInputDir(EnvNode):
    def __init__(self, path, topo_src, fault_src, config):
        self._root_path = path
        input_dir = os.path.join(path, 'input')
        if os.path.isdir(input_dir) is False:
            os.mkdir(input_dir)
        super().__init__(input_dir, 0)
        self._fill_up_env(topo_src, fault_src, config)

    def _fill_up_env(self, topo_src, fault_scr, topo_diff , fault_diff):
        topoconf = ConfigParser()
        topoconf.read(topo_diff)

        faultconf = ConfigParser()
        faultconf.read(fault_diff)

        topo_diff = dict(topoconf.items('Default'))
        fault_diff = dict(faultconf.items('Default'))

        #handle topography parameters
        if topo_src != '':
            topo_path = os.path.join(self._path,'topo_parameters.txt')
            if len(topo_diff) != 0:
                topo = TopoInput(topo_src)
                for key,val in topo_diff.items():
                    setattr(topo, key, val)
                topo.save_to_file(topo_path)
            else:
                shutil.copyfile(topo_src, topo_path)
            super().attach_child_node(EnvNode(topo_path, 1))

        #handle fault_parameters
        if fault_scr != '':
            fault_path = os.path.join(self._path,'fault_parameters.txt')
            if len(fault_diff) != 0 :
                fcont = FaultInput(fault_scr)
                for key,val in fault_diff.items():
                    setattr(fcont, key, val)
                    fcont.save_to_file(fault_path)
            else:
                shutil.copyfile(topo_src, fault_path)
            super().attach_child_node(EnvNode(fault_path, 1))

class PecubeDataDir(EnvNode):
    def __init__(self, path, esc_ang, cyn_ang, grid_type, row_num, col_num, steps):
        self._root_path = path
        data_dir = os.path.join(path, 'data')
        if os.path.isdir(data_dir) is False:
            os.mkdir(data_dir)
        super().__init__(data_dir, 0)
        self._fill_up_env(esc_ang, cyn_ang, grid_type, row_num, col_num, steps)

    def _fill_up_env(self, esc_ang, cyn_ang, grid_type, row_num, col_num, steps):
        pass


class PecubePEOutDir(EnvNode):
    pass

class PecubeBinDir(EnvNode):
    pass

class PecubeVtkDir(EnvNode):
    pass

class SessionEnv:
    def __init__(self, root_path, esc_ang, cyn_ang, col_num, row_num, grid_type,
                 steps, topo_input, fault_input, bin_path, fault_diff, topo_diff):
        self._env_root = EnvNode(root_path, 0)
        self._esc_ang = esc_ang
        self._cyn_ang = cyn_ang
        self._bin_path = bin_path
        self._topo_input = topo_input
        self._fault_input = fault_input
        self._fault_diff = fault_diff
        self._topo_diff = topo_diff
        self._steps = steps
        self._col_num = col_num
        self._row_num = row_num
        self._grid_type = grid_type

    def backup_env(self):
        [env_node.backup_env() for env_node in self._env_root]

    def generate_env(self):
        # INPUT
        self._env_root.attach_child_node(PecubeInputDir(self._env_root._path, self._topo_input, self._fault_input,
                                                        self._topo_diff, self._fault_diff))
        # DATA
        self._env_root.attach_child_node(PecubeDataDir(self._env_root._path, self._esc_ang, self._cyn_ang,
                                                       self._grid_type,self._row_num, self._col_num ,self._steps))
        # VTK
        # BIN
        # OUTPUT

    def __call__(self, *args, **kwargs):
        pass

class ModelEnv:
    def __init__(self, rootpath):
        self._sessions = []

    def backup_env(self):
        [session.backup_env() for session in self._sessions]

    def generate_env(self):
        config = ConfigParser()
        config.read('./model.conf')
        #extract data
        pec_file = config['Default']['peconfig']
        topo_data = pnd.read_csv(os.path.join(pec_file, os.environ['HOME']), header=0)

        wrk_data = topo_data[topo_data['env'] == 0]
        wrk_data['execution_directory'] = wrk_data['execution_directory'].apply(lambda x : x.replace('~', os.environ['HOME']))
        #generate sessions
        for _ , s in wrk_data.iterrows():
            rootpath = s['execution_directory']
            if os.path.exists(rootpath) is False:
                os.mkdir(rootpath)
            conf_env = config['Environment']
            self._sessions.append(SessionEnv(s['execution_directory'], conf_env['escarpment_angle'], conf_env['canyon_angle'],
                                             s['col_num'], s['row_num'], s['grid_type'],
                                             [s['step{0}'.format(i)]for i in range(conf_env['steps_num'])],
                                             conf_env['topo_sample'],conf_env['fault_sample'],
                                             conf_env['bin_dir']))
    def __call__(self, *args, **kwargs):
        pass

class PecubeEnv(ModelEnv):
    pass

class CascadeEnv(ModelEnv):
    pass

