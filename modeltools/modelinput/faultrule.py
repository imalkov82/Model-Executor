__author__ = 'imalkov'

from modeltools.modelinput.pecutils import prepare_to_parse
import numpy

class FaultInput:
    def __init__(self, fpath):
        str_file = prepare_to_parse(fpath)
        self._faults_num = str_file[0]
        self._fault_coord = str_file[1]
        self._arr = []
        self._fault_str = str_file[2:]
        flt_str_indx = 0
        for i in range(int(self._faults_num)):
            self._arr.append(Fault(self._fault_str[flt_str_indx:]))
            gnum = int(self._fault_str[flt_str_indx])
            flt_str_indx = gnum + 1 + int(self._fault_str[gnum + 1]) + 1

    def save_to_file(self, fpath = ''):
        ff = [self._faults_num] + [self._fault_coord] + [str(f) for f in self._arr]
        # ff = [self._faults_num] + [self._fault_coord] + self._fault_str
        with open(fpath, mode='w') as f:
            f.write('\n'.join(ff))

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
# --------------------------------------------------------
# --------------------------------------------------------
    @property
    def fault0_ts(self):
        return self._arr[0].steps.split(' ')[0]
    @property
    def fault0_te(self):
        return self._arr[0].steps.split(' ')[1]
    @property
    def fault0_velo(self):
        return self._arr[0].steps.split(' ')[2]
# --------------------------------------------------------
    @property
    def fault1_ts(self):
        return self._arr[1].steps.split(' ')[0]
    @property
    def fault1_te(self):
        return self._arr[1].steps.split(' ')[1]
    @property
    def fault1_velo(self):
        return self._arr[1].steps.split(' ')[2]
# --------------------------------------------------------
# --------------------------------------------------------
    @property
    def fault0_geometry_x1(self):
        return self._arr[0].geometry[0].split(' ')[0]
    @property
    def fault0_geometry_y1(self):
        return self._arr[0].geometry[0].split(' ')[1]
    @property
    def fault0_geometry_x2(self):
        return self._arr[0].geometry[1].split(' ')[0]
    @property
    def fault0_geometry_y2(self):
        return self._arr[0].geometry[1].split(' ')[1]
# --------------------------------------------------------
# --------------------------------------------------------
    @property
    def fault1_geometry_x1(self):
        return self._arr[1].geometry[0].split(' ')[0]
    @property
    def fault1_geometry_y1(self):
        return self._arr[1].geometry[0].split(' ')[1]
    @property
    def fault1_geometry_x2(self):
        return self._arr[1].geometry[1].split(' ')[0]
    @property
    def fault1_geometry_y2(self):
        return self._arr[1].geometry[1].split(' ')[1]

    #SETTERS
    @num.setter
    def num(self, val):
        self._faults_num = val
    @x1.setter
    def x1(self, val):
        s = self._fault_coord.split(' ')
        s[0] = val
        self._fault_coord = ' '.join(s)
    @y1.setter
    def y1(self, val):
        s = self._fault_coord.split(' ')
        s[1] = val
        self._fault_coord = ' '.join(s)
    @x2.setter
    def x2(self, val):
        s = self._fault_coord.split(' ')
        s[2] = val
        self._fault_coord = ' '.join(s)
    @y2.setter
    def y2(self, val):
        s = self._fault_coord.split(' ')
        s[3] = val
        self._fault_coord = ' '.join(s)
# --------------------------------------------------------
# --------------------------------------------------------
    @fault0_ts.setter
    def fault0_ts(self, val):
        s = self._arr[0].steps.split(' ')
        s[0] = val
        self._arr[0].steps = ' '.join(s)
    @fault0_te.setter
    def fault0_te(self, val):
        s = self._arr[0].steps.split(' ')
        s[1] = val
        self._arr[0].steps = ' '.join(s)
    @fault0_velo.setter
    def fault0_velo(self, val):
        s = self._arr[0].steps.split(' ')
        s[2] = val
        self._arr[0].steps = ' '.join(s)
# --------------------------------------------------------
# --------------------------------------------------------
    @fault1_ts.setter
    def fault1_ts(self, val):
        s = self._arr[1].steps.split(' ')
        s[0] = val
        self._arr[1].steps = ' '.join(s)
    @fault1_te.setter
    def fault1_te(self, val):
        s = self._arr[1].steps.split(' ')
        s[1] = val
        self._arr[1].steps = ' '.join(s)
    @fault1_velo.setter
    def fault1_velo(self, val):
        s = self._arr[1].steps.split(' ')
        s[2] = val
        self._arr[1].steps = ' '.join(s)
# --------------------------------------------------------
# --------------------------------------------------------
    @fault0_geometry_x1.setter
    def fault0_geometry_x1(self, val):
        g = self._arr[0].geometry
        s = g[0].split(' ')
        s[0] = val
        g[0] = ' '.join(s)
        self._arr[0].geometry = g
    @fault0_geometry_y1.setter
    def fault0_geometry_y1(self, val):
        g = self._arr[0].geometry
        s = g[0].split(' ')
        s[1] = val
        g[0] = ' '.join(s)
        self._arr[0].geometry = g
    @fault0_geometry_x2.setter
    def fault0_geometry_x2(self, val):
        g = self._arr[0].geometry
        s = g[1].split(' ')
        s[0] = val
        g[1] = ' '.join(s)
        self._arr[0].geometry = g
    @fault0_geometry_y2.setter
    def fault0_geometry_y2(self, val):
        g = self._arr[0].geometry
        s = g[1].split(' ')
        s[1] = val
        g[1] = ' '.join(s)
        self._arr[0].geometry = g
# --------------------------------------------------------
# --------------------------------------------------------
    @fault1_geometry_x1.setter
    def fault1_geometry_x1(self, val):
        g = self._arr[1].geometry
        s = g[0].split(' ')
        s[0] = val
        g[0] = ' '.join(s)
        self._arr[1].geometry = g
    @fault1_geometry_y1.setter
    def fault1_geometry_y1(self, val):
        g = self._arr[1].geometry
        s = g[0].split(' ')
        s[1] = val
        g[0] = ' '.join(s)
        self._arr[1].geometry = g
    @fault1_geometry_x2.setter
    def fault1_geometry_x2(self, val):
        g = self._arr[1].geometry
        s = g[1].split(' ')
        s[0] = val
        g[1] = ' '.join(s)
        self._arr[1].geometry = g
    @fault1_geometry_y2.setter
    def fault1_geometry_y2(self, val):
        g = self._arr[1].geometry
        s = g[1].split(' ')
        s[1] = val
        g[1] = ' '.join(s)
        self._arr[1].geometry = g

class Fault:
    def __init__(self, fault_str):
        g_end = 1 + int(fault_str[0])
        self._geometry = fault_str[1:g_end]
        s_start = g_end + 1
        s_end = s_start + int(fault_str[g_end])
        self._time_steps = fault_str[s_start: s_end]
    def __str__(self):
        res = str(len(self._geometry)) + '\n'
        res+= '\n'.join(self._geometry) + '\n'
        res+= str(len(self._time_steps)) + '\n'
        res+= '\n'.join(self._time_steps) + '\n'
        return res
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
    #SETTERS
    @geometry.setter
    def geometry(self, val):
        self._geometry = val
    @steps.setter
    def steps(self, val):
        self._time_steps = val

class FaultParser():
    def __call__(self, arr_location):
        return ','.join([','.join(el.split(' ')) for el in prepare_to_parse(arr_location)])

fault_parser = FaultParser()