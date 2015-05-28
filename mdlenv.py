__author__ = 'imalkov'

from inputgroup.toporule import TopoInput
from inputgroup.faultrule import FaultInput

class ModelEnv:
    pass

class PecubeEnv(ModelEnv):
    pass

class CascadeEnv(ModelEnv):
    pass

f = FaultInput('/home/imalkov/Dropbox/M.s/Research/DATA/SESSION_TREE/NODE03/Session1A/input/fault_parameters.txt')
flt = f.get_fault(2)
print(flt.geometry)
print(flt.steps)
# t = TopoInput('/home/imalkov/Dropbox/M.s/Research/DATA/SESSION_TREE/NODE03/Session1A/input/topo_parameters.txt')

# print(t.nx0)
# print(t.ny0)
# print(t.dlon)
# print(t.dlat)
# print(t.lon0)
# print(t.lat0)
# print(t.tau)
# print(t.tectosteps)
#
# print(t.f0)
# print(t.rc)
# print(t.rm)
# print(t.E)
# print(t.n)
# print(t.L)
# print(t.nx)
# print(t.ny)
#
# print(t.zl)
# print(t.nz)
# print(t.k)
# print(t.tb)
# print(t.tt)
# print(t.la)
# print(t.pr)
