__author__ = 'imalkov'

import shutil
import os
from datetime import datetime
from modeltools.modelinput.faultrule import FaultInput
from modeltools.modelinput.toporule import TopoInput

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
    def __init__(self, path):
        self._root_path = path
        super().__init__(os.path.join(path, 'input'), 0)

    def fill_up_env(self, topo_src, topo_diff, fault_scr, fault_diff):
        #handle topography parameters
        if topo_src != '':
            topo_path = os.path.join(self._path,'topo_parameters.txt')
            if topo_diff != '':
                topo = TopoInput(topo_src)
                #TODO: set parameters and save to file
            else:
                shutil.copyfile(topo_src, topo_path)
            super().attach_child_node(topo_path)

        #handle fault_parameters
        if fault_scr != '':
            fault_path = os.path.join(self._path,'topo_parameters.txt')
            if fault_diff != '':
                fcont = FaultInput(fault_scr)
                #TODO: set parameters and save to file
            else:
                shutil.copyfile(topo_src, os.path.join(self._path,'fault_parameters.txt'))
            super().attach_child_node(fault_path)

class PecubeDataDir(EnvNode):
    def __init__(self, path):
        self._root_path = path
        super().__init__(os.path.join(path, 'data'), 0)
        # super().attach_child_node(topo_file)

    def fill_up_env(self):
        pass

class PecubePEOutDir(EnvNode):
    pass

class PecubeBinDir(EnvNode):
    pass

class PecubeVtkDir(EnvNode):
    pass

class ModelEnv:
    def __init__(self, rootpath):
        self._env_root = EnvNode(rootpath, 0)

    def backup_env(self):
        [env_node.bachup_env() for env_node in self._env_root]

    def generate_env(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

class PecubeEnv(ModelEnv):
    pass

class CascadeEnv(ModelEnv):
    pass
