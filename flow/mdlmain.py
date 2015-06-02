__author__ = 'imalkov'
from modeltools.modelinput.faultrule import FaultInput
from modeltools.modelinput.toporule import TopoInput

if __name__ == '__main__':
    # container = FaultInput('/home/imalkov/Dropbox/M.s/Research/DATA/SESSION_TREE/NODE03/Session1A/input/fault_parameters.txt')
    # flt_arr = container.faults
    # print(flt_arr[0].geometry)
    # print(flt_arr[0].steps)
    # print(flt_arr[0].angle)
    # print(max(flt_arr[0].abs_velosity))
    # print(max(flt_arr[0].duration))

    t = TopoInput('/home/imalkov/Dropbox/M.s/Research/DATA/SESSION_TREE/NODE03/Session1A/input/topo_parameters.txt')
    print(t.nx0)
    print(t.ny0)

    print(t.dlon)
    print(t.dlat)
    print(t.skip)
    print(t.zl)
    print(t.nz)
    print(t.pr) # heat production
    print(t.duration)
    # print(t.tectosteps)



