__author__ = 'imalkov'

import pandas
import numpy

class ThermoProfile:
    def __init__(self, csv_path, simulation_duration, vert_velocity, topo_nx0, topo_ny0, max_height):
        self._path = csv_path
        self._data = pandas.read_csv(csv_path, header=0, usecols = ['arc_length','Points:2'])
        self._simulation_duration = simulation_duration
        self._abs_velocity = vert_velocity
        self._topo_nx0 = topo_nx0
        self._topo_ny0 = topo_ny0
        self._max_height = max_height


class EscarpmentProfile(ThermoProfile):
    def __init__(self, csv_path, simulation_duration, vert_velocity, topo_nx0, topo_ny0, max_height):
        super().__init__(csv_path, simulation_duration, vert_velocity, topo_nx0, topo_ny0, max_height)

    @property
    def upper(self):
        raise NotImplemented()
    @property
    def lower(self):
        raise NotImplemented()
    @property
    def slope(self):
        raise NotImplemented()




