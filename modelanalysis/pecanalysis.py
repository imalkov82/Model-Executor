__author__ = 'imalkov'

import pandas as pnd
import os
import numpy as np
import matplotlib.pylab as plt
from argparse import ArgumentParser
from functools import reduce


def df_ea_riv(frame1):
    fd1 = frame1[frame1['Points:2'] < max(frame1['Points:2'])]
    fd  = fd1[fd1['ApatiteHeAge'] >= 1]
    s = fd[fd['Points:2'] == min(fd['Points:2'])]['arc_length']
    res_df = fd[fd['arc_length'] >= s[s.index[:]].mean()]
    res_df['Elevation'] = res_df['Points:2'] - min(frame1['Points:2'])
    return res_df

def df_ea_esc(frame1):
    fd1 = frame1[(frame1['Points:2'] < max(frame1['Points:2']))
                 & (frame1['Points:2'] > min(frame1['Points:2']))]
    fd  = fd1[fd1['ApatiteHeAge'] >= 1]
    fd['Elevation'] = fd['Points:2'] - min(frame1['Points:2'])
    return fd

def ea_finder(root_dir):
    arr = []
    name = 'Age-Elevation0.csv'
    for dirpath, dirname, filename in os.walk(root_dir):
        if name in filename:
            arr.append(os.path.join(dirpath, name))
    return arr

def collect_to_dict(tup_arr):
    loc_dict = {}
    for el, path in tup_arr:
        arr = []
        if el in loc_dict:
            arr = loc_dict[el]
        arr.append(path)
        loc_dict[el] = arr
    return loc_dict

def name_dst_file(fname, dst_path, suf):
    node_loc = fname.find('NODE') + len('NODE')
    s_loc = fname.find('csv') - 3
    pref = 'n{0}s{1}'.format(fname[node_loc:node_loc + 2], fname[s_loc:s_loc + 2])
    return '{0}{1}'.format(os.path.join(dst_path,pref), suf)

def plot_ea(frame1, filt_df, dst_path, uplift_rate):
    f = plt.figure()
    ax = filt_df.plot(x='ApatiteHeAge', y='Elevation', style='o-', ax=f.gca())

    plt.title('Age-Elevation')
    plt.xlabel('ApatiteHeAge [Ma]')
    plt.ylabel('Elevation [Km]')

    #tread line
    sup_age = find_max_treadline(filt_df, uplift_rate * np.sin(np.deg2rad(60)))
    x = filt_df[filt_df['ApatiteHeAge'] < sup_age]['ApatiteHeAge']
    y = filt_df[filt_df['ApatiteHeAge'] < sup_age]['Points:2']
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)

    # plt.legend(point_lables, loc='best', fontsize=10)
    # n = np.linspace(min(frame1[frame1['Points:2'] > min(frame1['Points:2'])]['ApatiteHeAge']), max(frame1['ApatiteHeAge']), 21)
    n = np.linspace(min(filt_df[filt_df['Points:2'] >= min(filt_df['Points:2'])]['ApatiteHeAge']), max(filt_df['ApatiteHeAge']), 21)
    plt.plot(n, p(n) - min(frame1['Points:2']),'-r')
    ax.text(np.mean(n), np.mean(p(n) - min(frame1['Points:2'])), 'y=%.6fx + b'%(z[0]), fontsize = 20)

    txs = np.linspace(np.round(min(filt_df['Elevation'])), np.ceil(max(filt_df['Elevation'])), 11)
    lebs = ['0'] + [str(i) for i in txs[1:]]
    plt.yticks(txs, list(reversed(lebs)))
    plt.savefig(dst_path)

# TODO: optimize using pecinputstats.csv
def find_max_treadline(data_frame, opt_tread):
    pnd_ds = data_frame['ApatiteHeAge']
    ds = np.array(pnd_ds)
    max_age = 0
    min_tol = 1
    for sup_age in sorted(ds)[1:]:
        x = data_frame[data_frame['ApatiteHeAge'] < sup_age]['ApatiteHeAge']
        y = data_frame[data_frame['ApatiteHeAge'] < sup_age]['Points:2']
        z = np.polyfit(x, y, 1)
        if abs(opt_tread - z[0]) < min_tol:
            min_tol = abs(opt_tread - z[0])
            max_age = sup_age
    return max_age

def uplift_from_fime_name(fname):
    s_loc = fname.find('csv') - 3
    return int(fname[s_loc :s_loc + 1]) * 0.1

def plot_age_elevation(src_path, dst_path):
    for ea in ea_finder(src_path):
        print(ea)
        cols = ['ApatiteHeAge','Points:2', 'arc_length']
        frame1 = pnd.read_csv(ea, header=0, usecols = cols)
        if ea.find('riv') != -1:
            pic_name = name_dst_file(ea, dst_path, '_riv_ea.png')
            df_res = df_ea_riv(frame1)
        else:
            pic_name = name_dst_file(ea, dst_path, '_esc_ea.png')
            df_res = df_ea_esc(frame1)
        try:
            plot_ea(frame1, df_res, pic_name, uplift_from_fime_name(ea))
        except Exception as e:
            print('error in file={0}, error msg = {1}'.format(ea, e))

############### TEMPERATURE ###################################################
def gen_geoth_mean(fs, col_name_arr, riv_type):
    res = []
    for tn in col_name_arr:
        if riv_type is False:
            sm = 10
        else:
            s = fs[fs[tn] == min(fs[tn])]['arc_length']
            sm = s[s.index[:]].mean()
        res_fs = fs[(fs['arc_length'] >= (sm - abs(sm * 0.1))) & (fs['arc_length'] < (sm + abs(sm * 0.1)))]
        res.append(-1 * res_fs[tn].mean())
    return res


def group_finder(root_dir):
    return temperature_finder(root_dir,'group')

def temperature_finder(root_dir, name='Temperature'):
    arr = []
    for dirpath, dirname, filename in os.walk(root_dir):
        for f in filename:
            if f.find(name) != -1:
                arr.append((dirpath, f))
    return collect_to_dict(arr)

def temperature_from_files(k, v , on_point_func = lambda x : x):
    res = []
    for i,t in enumerate(v):
        tmp_df = pnd.read_csv(os.path.join(k,t), usecols = ['arc_length','Points:2'])
        tmp_df[t] = on_point_func(tmp_df['Points:2'])
        tmp_df.drop('Points:2', axis= 1 , inplace= True)
        res.append(tmp_df)
    return reduce(lambda f1, f2: pnd.merge(f1, f2, on='arc_length', how='outer'), res)

def plot_temperature(src_path, dst_path, mean_flag):
    for k,v in temperature_finder(src_path).items():
        print(k)
        max_high = max(pnd.read_csv('{0}/Age-Elevation0.csv'.format(k), header = 0, usecols=['Points:2'])['Points:2'])
        fs = temperature_from_files(k, v, on_point_func=lambda x:  x - max_high)

        f = plt.figure()
        ax = f.gca()
        try:
            for tn in v:
                ax = fs.plot(x='arc_length', y=tn, ax=ax)

            leg_list = list(reversed(["{0}C".format((int((os.path.splitext(t)[0])[-1]) + 1) * 25) for i,t in enumerate(v)]))
            plt.title('BLOCK GEOTHREMA', fontsize = 12)
            plt.legend(leg_list , loc='best', fontsize=10)
            plt.xlabel('Length [km]')
            plt.ylabel('Depth [Km]')

            mn = [min(fs[i]) for i in v]
            txs = np.linspace(-np.ceil(- min(mn)), 0, np.ceil(- min(mn)) + 1)
            lebs = [str(-i) for i in txs[:-1]] + ['0']
            plt.yticks(txs, lebs)

            if k.find('riv') != -1:
                pic_name = name_dst_file(k, dst_path, '_riv_geot.png')
            else:
                pic_name = name_dst_file(k, dst_path, '_esc_geot.png')
            plt.savefig(pic_name)

            if mean_flag is True:
                with open(os.path.join(os.getcwd(), 'geo_mean.txt'), 'a+') as f:
                        riv_type = False
                        if k.find('riv') != -1:
                            riv_type = True
                        tl = ['{0}={1}'.format(tt,vv) for tt, vv in zip(leg_list, gen_geoth_mean(fs, v, riv_type))]
                        f.write('{0}: {1}\n'.format(os.path.split(pic_name)[1],','.join(list(reversed(tl)))))

        except Exception as e:
            print('error in file={0}, error msg = {1}'.format(k, e))

def convert_names(src_dir):
    count = 1
    for k,v in group_finder(src_dir).items():
        # print('key={0}: val={1}'.format(k, ' '.join(sorted(v))))
        for p in v:
            convert_name = ''
            fileName, _ = os.path.splitext(p)
            with open(os.path.join(k,p),'r') as file:
                l = file.readline()
                if l.find('ApatiteHeAge') != -1:
                    convert_name = 'Age-Elevation0.csv'
                else:
                    convert_name = 'Temperature{0}.csv'.format(int(fileName[-1])-1)
            cmd = 'cp {0} {1}'.format(os.path.join(k,p),os.path.join(k,convert_name))
            # print(cmd)
            os.popen(cmd)

# TODO: refuctor to OO
if __name__ == '__main__':
    parser = ArgumentParser()
    #set rules
    parser.add_argument( "-i", dest="soure_path", help="source directory")
    parser.add_argument( "-o", dest="dest_path", help="destination directory")
    parser.add_argument( "-e", action="store_true", dest="aeflag", help="age elevation plot", default=False)
    parser.add_argument( "-tp", action="store_true", dest="tflag", help="temperature plot", default=False)
    parser.add_argument( "-ta", action="store_true", dest="tmean", help="temperature mean", default=False)
    parser.add_argument( "-c", action="store_true", dest="convert_name", help="converts group files to Temperature and Age-Elevation", default=False)

    kvargs = parser.parse_args()

    if kvargs.convert_name is True:
        print("converting files")
        convert_names(kvargs.soure_path)

    if kvargs.aeflag is True:
        print("Age Elevation plot")
        plot_age_elevation(kvargs.soure_path, kvargs.dest_path)
    if kvargs.tflag is True:
        print("Geotherma plot")
        plot_temperature(kvargs.soure_path, kvargs.dest_path, kvargs.tmean)
