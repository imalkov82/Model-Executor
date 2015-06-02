__author__ = 'imalkov'

from modeltools.modelinput.faultrule import FaultInput
from modeltools.modelinput.toporule import TopoInput
import os
import sys
sys.path.append(os.getcwd())
import pandas as pnd
import numpy
from configparser import ConfigParser

class ModelInputStats:
    """
    will fill the
    """
    def __init__(self, peconf, pestasts):
        self._peconf =  peconf
        self._pestasts = pestasts

    def __call__(self, *args, **kwargs):
        topo_data = pnd.read_csv(self._peconf, header=0, usecols=['execution_directory'])
        stats_data = pnd.read_csv(self._pestasts, header=0)

        mask = numpy.logical_not(topo_data.execution_directory.isin(stats_data.execution_directory))
        topo_data[mask].execution_directory

        res_dict = {}
        res_dict['execution_directory'] = []
        res_dict['fault_angle']= []
        res_dict['fault_simulation_duration']=[]
        res_dict['fault_abs_velocity']=[]
        res_dict['fault_abs_velocity']=[]

        res_dict['topo_nx0']=[]
        res_dict['topo_ny0']=[]
        res_dict['topo_thickness']=[]
        res_dict['topo_z_points']=[]
        res_dict['topo_dlon']=[]
        res_dict['topo_dlat']=[]
        res_dict['topo_simulation_duration']=[]
        res_dict['topo_heat_production']=[]
        res_dict['topo_skip']=[]

        for path in [p.replace('~',os.environ['HOME']) for i, p in topo_data[mask].execution_directory.iteritems()]:
            container = FaultInput('{0}input/fault_parameters.txt'.format(path))
            flt_arr = container.faults

            res_dict['execution_directory'].append(path)
            res_dict['fault_angle'].append(flt_arr[0].angle)
            res_dict['fault_simulation_duration'].append(max(flt_arr[0].duration))
            res_dict['fault_abs_velocity'].append(max(flt_arr[0].abs_velosity))


            t = TopoInput('{0}input/topo_parameters.txt'.format(path))

            res_dict['topo_nx0'].append(t.nx0)
            res_dict['topo_ny0'].append(t.ny0)
            res_dict['topo_thickness'].append(t.zl)
            res_dict['topo_z_points'].append(t.nz)
            res_dict['topo_dlon'].append(t.dlon)
            res_dict['topo_dlat'].append(t.dlat)
            res_dict['topo_simulation_duration'].append(t.duration)
            res_dict['topo_heat_production'].append(t.pr)
            res_dict['topo_skip'].append(t.skip)

            # del tmp_dict
        frames = [stats_data, pnd.DataFrame(res_dict, columns=stats_data.columns)]
        res_df = pnd.concat(frames)
        res_df.to_csv(self._pestasts, index=False)

if __name__ == '__main__':
    config = ConfigParser()
    # config.read('./model.conf')
    config.read('/home/imalkov/Documents/pycharm_workspace/Model-Executor/model.conf')
    stats_kls =  ModelInputStats(config['Default']['peconfig'].replace('~',os.environ['HOME']),
                                 config['Analysis']['pec_input_stats'].replace('~',os.environ['HOME']))

    stats_kls()