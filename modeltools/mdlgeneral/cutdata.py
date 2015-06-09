__author__ = 'imalkov'
import numpy

for i in range(3):
    step = numpy.loadtxt('/home/imalkov/Dropbox/M.s/Research/DATA/TEST/hdata/step{0}.txt'.format(i))
    step2 = numpy.reshape(step,[808,453])
    data = step2[:, :226]
    numpy.savetxt('/home/imalkov/Dropbox/M.s/Research/DATA/TEST/data/step{0}.txt'.format(i), data.flatten(),fmt='%d')

