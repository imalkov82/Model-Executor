import itertools
import pandas
import matplotlib.pylab as plt
import numpy as np


class ModelPlot:
    def __init__(self, data):
        pass
    def order(self):
        pass
    def add_element(self, other):
        pass
    def remove_element(self, other):
        pass
    def make_plot(self):
        pass

class AgeElevationPlot(ModelPlot):
    pass

class GeothermasPlot(ModelPlot):
    pass





class MakePlot:
    def __init__(self, xcol_name, ycol_name, xlabel, ylabel):
        self.xc

def make_plot(df, pic_name):
    f = plt.figure()
    ax = f.gca()
    for v in range(0, df.shape[1]):
        ax = df.plot(x='arc_length'.format(v), y=v, ax=ax)


    # plt.title('BLOCK GEOTHREMA', fontsize=12)

    plt.legend(list(df['NAME']), loc='best', fontsize=10)
    plt.xlabel('Length [km]')
    plt.ylabel('Depth [Km]')

    mn = [min(fs[i]) for i in v]
    txs = np.linspace(-np.ceil(- min(mn)), 0, np.ceil(- min(mn)) + 1)
    lebs = [str(-i) for i in txs[:-1]] + ['0']
    plt.yticks(txs, lebs)
    plt.savefig(pic_name)
    plt.close()

def var_in_dur(df):
    df_sorted = df.sort(['UPLIFT_RATE', 'EXHUMATION_RATE'], ascending = [1, 0])

    #search for groups


if __name__ == '__main__':
    df_hp = pandas.read_csv('/home/imalkov/Dropbox/M.s/Research/DOCS/heat_plot.csv', header = 0)
    var_in_dur(df_hp)
