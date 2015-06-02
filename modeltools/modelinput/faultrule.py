__author__ = 'imalkov'

from modeltools.modelinput.pecutils import prepare_to_parse
import numpy

class FaultInput:
    def __init__(self, fpath):
        str_file = prepare_to_parse(fpath)
        self._faults_num = str_file[0]
        self._fault_coord = str_file[1]
        self._arr = []
        fault_str = str_file[2:]
        flt_str_indx = 0
        for i in range(int(self._faults_num)):
            self._arr.append(Fault(fault_str[flt_str_indx:]))
            gnum = int(fault_str[flt_str_indx])
            flt_str_indx = gnum + 1 + int(fault_str[gnum + 1]) + 1

    @property
    def num(self):
        return self._faults_num
    @property
    def x1(self):
        return self._fault_coord.split(' ')[0]
    @property
    def y1(self):
        return self._fault_coord.split(' ')[1]
    @property
    def x2(self):
        return self._fault_coord.split(' ')[2]
    @property
    def y2(self):
        return self._fault_coord.split(' ')[3]
    @property
    def faults(self):
        return self._arr

class Fault:
    def __init__(self, fault_str):
        g_end = 1 + int(fault_str[0])
        self._geometry = fault_str[1:g_end]
        s_start = g_end + 1
        s_end = s_start + int(fault_str[g_end])
        self._time_steps = fault_str[s_start: s_end]
    @property
    def geometry(self):
        return self._geometry
    @property
    def steps(self):
        return self._time_steps
    @property
    def angle(self):
        pl = [p.replace(' ',',') for p in self._geometry]
        mat = numpy.matrix(';'.join(pl))
        p =  mat[:, 1] + mat[:, 0]
        return numpy.rad2deg(numpy.arctan(p[0, 0]/p[1, 0]))
    @property
    def abs_velosity(self):
        return [float(i.split(' ')[-1]) for i in self._time_steps]
    @property
    def duration(self):
        return [float(i.split(' ')[0]) for i in self._time_steps]

class FaultParser():
    def __call__(self, arr_location):
        return ','.join([','.join(el.split(' ')) for el in prepare_to_parse(arr_location)])

fault_parser = FaultParser()