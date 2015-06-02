__author__ = 'imalkov'

from modeltools.modelinput.faultrule import FaultInput
from modeltools.modelinput.toporule import TopoInput
import os
import sys
sys.path.append(os.getcwd())
import pandas as pnd
import numpy
from configparser import ConfigParser
from argparse import ArgumentParser

class ModelInputStats:
    """
    will fill the
    """

    def __init__(self, peconf, pestasts):
        self._peconf =  peconf
        self._pestasts = pestasts
        self._res_dict = self._create_dict()

    def _create_dict(self):
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

        return res_dict

    def _populate_topo_params(self, path):
        t = TopoInput('{0}input/topo_parameters.txt'.format(path))

        self._res_dict['topo_nx0'].append(t.nx0)
        self._res_dict['topo_ny0'].append(t.ny0)
        self._res_dict['topo_thickness'].append(t.zl)
        self._res_dict['topo_z_points'].append(t.nz)
        self._res_dict['topo_dlon'].append(t.dlon)
        self._res_dict['topo_dlat'].append(t.dlat)
        self._res_dict['topo_simulation_duration'].append(t.duration)
        self._res_dict['topo_heat_production'].append(t.pr)
        self._res_dict['topo_skip'].append(t.skip)
        return

    def _populate_fault_params(self, path):
        container = FaultInput('{0}input/fault_parameters.txt'.format(path))
        flt_arr = container.faults
        self._res_dict['execution_directory'].append(path)
        self._res_dict['fault_angle'].append(flt_arr[0].angle)
        self._res_dict['fault_simulation_duration'].append(max(flt_arr[0].duration))
        self._res_dict['fault_abs_velocity'].append(max(flt_arr[0].abs_velosity))
        return


    def __call__(self, overide):
        topo_data = pnd.read_csv(self._peconf, header=0, usecols=['execution_directory'])
        stats_data = pnd.read_csv(self._pestasts, header=0)

        if overide is True:
            mask = numpy.logical_not(topo_data.execution_directory.isin(stats_data.execution_directory))
            wrk_list = topo_data[mask].execution_directory
        else:
            wrk_list = topo_data.execution_directory

        for path in [p.replace('~',os.environ['HOME']) for i, p in wrk_list.iteritems()]:
            self._populate_topo_params()
            self._populate_fault_params()
            # del tmp_dict

        frames = [stats_data, pnd.DataFrame(self._res_dict, columns=stats_data.columns)]
        res_df = pnd.concat(frames)
        res_df.to_csv(self._pestasts, index=False)

if __name__ == '__main__':
    parser = ArgumentParser()
    #set rules
    parser.add_argument( "-w", action="store_true", dest="overide", help="overide the stats file. if flag not set the file will updated", default=False)
    kvargs = parser.parse_args()

    config = ConfigParser()
    config.read('./model.conf')
    # config.read('/home/imalkov/Documents/pycharm_workspace/Model-Executor/model.conf')
    stats_kls =  ModelInputStats(config['Default']['peconfig'].replace('~',os.environ['HOME']),
                                 config['Analysis']['pec_input_stats'].replace('~',os.environ['HOME']))

    stats_kls(kvargs.overide)