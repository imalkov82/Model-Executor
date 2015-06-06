__author__ = 'imalkov'

import numpy
import os

class StepsContainer:
    pass

class StepInput:
    def __init__(self, step_name, esc_ang, cyn_ang, grid_type, row_num, col_num, max_high):
        self._step_name = step_name
        self._esc_ang = esc_ang
        self._cyn_ang = cyn_ang
        self._grid_type = grid_type
        self._row_num = row_num
        self._col_num = col_num
        self._high = max_high

    def save_to_file(self, save_path):
        if self._grid_type == 0:
            print('generate topography with canyon')
            zs_func = StepInput.surfcyn_gen_factory(self._row_num,self._col_num, self._esc_ang, self._cyn_ang)
        if self._grid_type == 1:
            print('generate topography')
            zs_func = StepInput.surfgen_factory(self._row_num, self._col_num, self._esc_ang)

        step = zs_func(self._high * numpy.sin(numpy.deg2rad(self._esc_ang)), StepInput.gen_mgsurf)
        print('write topography to file')
        StepInput.write_topo_fname(step,os.path.join(save_path,self._step_name))

    @staticmethod
    def gen_mgsurf(xsize,ysize,foo):
        x  = numpy.linspace(0, xsize, xsize)
        y  = numpy.linspace(0, ysize ,ysize)
        xi,yi = numpy.meshgrid(x,y)
        return foo(xi,yi)

    @staticmethod
    def write_topo_fname(data, ptxt):
        try:
            numpy.savetxt(ptxt, data.flatten(),fmt='%d')
        except Exception as e:
            print("Error in Print" + str(e))

    @staticmethod
    def surfgen_factory(mrow, mcol, esc_angle):
        fylocation = mcol/2
        escarpment_angle = esc_angle
        def surf_generator(fw_maxh, f):
            st2 = f(mrow,fylocation,lambda xi,yi: 101 * numpy.tan(numpy.deg2rad(escarpment_angle)) * yi)
            st2 = numpy.concatenate((numpy.zeros(st2.shape),st2),axis=0)
            st2[st2 > fw_maxh] = fw_maxh # footwall maximum height
            return st2
        return surf_generator

    @staticmethod
    def surfcyn_gen_factory(mrow, mcol, esc_angle, cyn_angle):
        fylocation = mcol/2
        cynlocation = mrow / 2 # canyon location
        canyon_angle = cyn_angle
        escarpment_angle = esc_angle
        def surfcyn_gen(fw_max, f):
            zl = f(cynlocation, fylocation, lambda xi,yi: 101 * numpy.tan(numpy.deg2rad(canyon_angle)) * xi + 101 * numpy.tan(numpy.deg2rad(0)) * yi)
            z = numpy.concatenate((numpy.fliplr(zl),zl),axis=1)
            z = numpy.hstack((z,numpy.zeros((z.shape[0],1))+fw_max)) #add column
            #escarpment
            st2 = f(mrow,fylocation,lambda xi,yi: 101 * numpy.tan(numpy.deg2rad(escarpment_angle)) * yi)
            #final topography
            st2[z<st2] = z[z<st2]
            st2 = numpy.concatenate((numpy.zeros(st2.shape),st2),axis=0)
            st2[st2 > fw_max] = fw_max
            return st2
        return surfcyn_gen


