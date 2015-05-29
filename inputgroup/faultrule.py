__author__ = 'imalkov'

from inputgroup.pecutils import prepare_to_parse
import os

class FaultContainer:
    def __init__(self, fpath):
        str_file = prepare_to_parse(fpath)
        self._fault_coord = str_file[1]
        self._arr = []
        fault_str = str_file[2:]
        flt_str_indx = 0
        for i in range(int(str_file[0])):
            self._arr.append(Fault(fault_str[flt_str_indx:]))
            gnum = int(fault_str[flt_str_indx])
            flt_str_indx = gnum + 1 + int(fault_str[gnum + 1]) + 1

    def get_fault(self, n):
        if n < len(self._arr):
            return self._arr[n]
        else:
            raise KeyError('no fault number exist')
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

class FaultInput:
    def __init__(self, fpath):
        if os.path.isfile(fpath) and os.path.split(fpath)[1] == 'fault_parameters.txt':
           self._fc = FaultContainer(fpath)
        else:
            raise IOError('no such file: {0}'.format(fpath))

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

    def get_fault(self, n=0):
        return self._fc.get_fault(n)





class FaultParser():
    def __call__(self, arr_location):
        return ','.join([','.join(el.split(' ')) for el in prepare_to_parse(arr_location)])

fault_parser = FaultParser()