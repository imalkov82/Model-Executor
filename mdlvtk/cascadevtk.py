__author__ = 'imalkov'

from itertools import dropwhile
import numpy
import pandas

class CascadeTopographyIterator:
    def __init__(self, file):
        self.file = file

    def __iter__(self):
        return self

    def __next__(self):
        l = self.file.readline()
        allstr = ''
        for i in range(0, int(l.split()[2])):
            allstr += self.file.readline()
            if i > 10000:
                print('i to big')
                break
        df = pandas.DataFrame.from_csv(allstr)
        return df

def topo_to_vtk(topo_path):
    with open(topo_path, 'r') as f:
        l = f.readline()
        list1 = list(range(1, int(l.split()[2])))

if __name__ == '__main__':
    topo_path = '/home/imalkov/Documents/CODE/FORTRAN/OriginalModels/Cascade/cascade/cascade/RUN1/topography'
    nstep = 0
    with open(topo_path) as f:
        l = f.readline()
        print(l.split())
        ll = [f.readline().split()[1:] for i in range(0, int(l.split()[2]))]
        arr = numpy.array(ll)
        df1 = pandas.DataFrame(arr)

        # print(type(arr))

