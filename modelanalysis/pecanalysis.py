__author__ = 'imalkov'

import pandas as pnd
import os
import numpy as np
import matplotlib.pylab as plt
from argparse import ArgumentParser
from functools import reduce
import scipy
import scipy.stats
from scipy.stats import linregress

def say_name(f):
    def wrapper(*args, **kargs):
        print('calling {0}'.format(f.__name__))
        return f(*args, **kargs)
    return wrapper

def df_ea_riv(frame1):
    fd1 = frame1[frame1['Points:2'] < max(frame1['Points:2'])]
    fd = fd1[fd1['ApatiteHeAge'] >= 1]
    s = fd[fd['Points:2'] == min(fd['Points:2'])]['Points:0']
    res_df = fd[fd['Points:0'] >= s[s.index[:]].mean()]
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
            arr.append((dirpath, name))
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

def plot_ea(frame1, filt_df, dst_path, uplift_rate, riv_case):
    f = plt.figure()
    ax = filt_df.plot(x='ApatiteHeAge', y='Elevation', style='o-', ax=f.gca())

    plt.title('Age-Elevation')
    plt.xlabel('ApatiteHeAge [Ma]')
    plt.ylabel('Elevation [Km]')

    #tread line
    sup_age, slope, r_square = find_max_treadline(filt_df, uplift_rate * np.sin(np.deg2rad(60)), riv_case)
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
    plt.close()
    return z[0]

# TODO: optimize using pecinputstats.csv
def define_max_age(df1, tot_len, best_tread, riv_case, oldest_age):
    print('best_tread={0}, tot_len={1}, oldest_age={2}'.format(best_tread, tot_len, oldest_age))

    df1 = df1[~pnd.isnull(df1['slope'])]
    df1 = df1[(df1.r_square < 1)]

    df1 = df1.sort(['arr_len'], ascending = [1]).head(np.round(df1.shape[0] * 0.5))
    df1['slope_diff'] = abs(df1['slope'] - best_tread)

    if riv_case is True:
        # print('river case')
        df1 = df1.sort(['arr_len'], ascending = [0]).head(np.round(df1.shape[0] * 0.5))
        df1 = df1.sort(['r_square'], ascending = [0]).head(np.round(df1.shape[0] * 0.5))
        riv_fd_by_slope_diff = df1
        df2 = riv_fd_by_slope_diff[riv_fd_by_slope_diff.r_square == riv_fd_by_slope_diff.r_square.max()]
    else:
        # print('escarpment case')
        riv_fd_by_slope_diff = df1.sort(['slope_diff'], ascending = [1]).head(np.round(df1.shape[0] * 0.5))
        # df1 = df1.sort(['slope_diff'], ascending = [1]).head(np.round(df1.shape[0] * 0.5))
        # riv_fd_by_slope_diff = df1[df1.sup_age < np.ceil(0.85 * oldest_age)]
        df2 = riv_fd_by_slope_diff[riv_fd_by_slope_diff.slope_diff == riv_fd_by_slope_diff.slope_diff.min()]
    max_age = df2['sup_age'].max()
    print(riv_fd_by_slope_diff)
    print('max_age = {0}'.format(max_age))
    s = df2[df2['sup_age'] == max_age]
    return max_age, s['slope'], s['r_square']

def find_max_treadline(data_frame, opt_tread, riv_case):
    pnd_ds = data_frame['ApatiteHeAge']
    ds = np.array(pnd_ds)
    columns = ['slope', 'r_square', 'arr_len', 'sup_age', 'max_height']
    pnd_data_frame = pnd.DataFrame(data=None, columns=columns)

    for sup_age in sorted(ds)[1:]:
        x = data_frame[data_frame['ApatiteHeAge'] < sup_age]['ApatiteHeAge']
        y = data_frame[data_frame['ApatiteHeAge'] < sup_age]['Points:2']
        minh = data_frame['Points:2'].min()
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        s = pnd.Series(data = [slope, r_value**2, len(x), sup_age, max(y)- minh], index=columns)
        pnd_data_frame = pnd_data_frame.append(s, ignore_index=True)
    max_age, slope, r_square = define_max_age(pnd_data_frame, len(ds), opt_tread, riv_case, max(ds))
    return max_age, slope, r_square

def uplift_from_file_name(fname):
    s_loc = fname.find('csv') - 3
    return int(fname[s_loc :s_loc + 1]) * 0.1

@say_name
def plot_age_elevation(src_path, dst_path):
    ages_to_file = ''
    for dirname, name in ea_finder(src_path):
        ea = os.path.join(dirname, name)
        # root_dir = os.path.split(dirname)[0]
        # print(ea)
        cols = ['ApatiteHeAge','Points:2', 'Points:0']
        frame1 = pnd.read_csv(ea, header=0, usecols = cols)
        if ea.find('riv') != -1:
            riv_case = True
            pic_name = name_dst_file(ea, dst_path, '_riv_ea.png')
            df_res = df_ea_riv(frame1)
        else:
            riv_case = False
            pic_name = name_dst_file(ea, dst_path, '_esc_ea.png')
            df_res = df_ea_esc(frame1)
        try:
            ax = plot_ea(frame1, df_res, pic_name, uplift_from_file_name(ea), riv_case)
            ages_to_file += ','.join([pic_name,str(ax)]) + '\n'
        except Exception as e:
            print('error in file={0}, error msg = {1}'.format(ea, e))
    with open(os.path.join(src_path, 'age-elevation_fit.txt'),'a') as file:
        file.write(ages_to_file)

############### TEMPERATURE ###################################################
@say_name
def gen_geoth_mean(fs, col_name_arr, riv_type, sm):
    res = []
    print('riv_type={0}'.format(riv_type))
    for tn in col_name_arr:
        atr = 'arc_length'
        if riv_type:
            atr = 'Height_{0}'.format(tn)
            s = fs[fs[tn] == min(fs[tn])][atr]
            print(s)
            sm = s[s.index[:]].mean()
        print('sm={0}'.format(sm))
        print('atr={0}'.format(atr))
        abs_sm___ = fs[atr] >= (sm - abs(sm * 0.1))
        sm_abs_sm___ = fs[atr] < (sm + abs(sm * 0.1))
        res_fs = fs[(abs_sm___) & (sm_abs_sm___)]
        res.append(-1 * res_fs[tn].mean())
    return res


def group_finder(root_dir):
    return temperature_finder(root_dir, 'group')

def temperature_finder(root_dir, name='Temperature'):
    arr = []
    for dirpath, dirname, filename in os.walk(root_dir):
        for f in filename:
            if f.find(name) != -1:
                arr.append((dirpath, f))
    return collect_to_dict(arr)

def temperature_from_files(k, v, on_point_func=lambda x: x):
    res = []
    for i,t in enumerate(v):
        # print(t)
        tmp_df = pnd.read_csv(os.path.join(k, t), usecols=['Points:0', 'Points:2', 'arc_length'])
        # print(tmp_df['Points:2'].min())
        tmp_df[t] = on_point_func(tmp_df['Points:2'])
        tmp_df['Height_{0}'.format(t)] = tmp_df['Points:0']

        tmp_df.drop('Points:2', axis=1, inplace=True)
        tmp_df.drop('Points:0', axis=1, inplace=True)
        res.append(tmp_df)
    return reduce(lambda f1, f2: pnd.merge(f1, f2, on='arc_length', how='outer'), res)

@say_name
def geoth_plot(src_path, dst_path):
    print(geoth_plot.__name__)
    for k,v in temperature_finder(src_path).items():
        # print(k)
        fs, leg_list, pic_name, _ = geoth_params(dst_path, k, v)
        try:
            _geoth_plot(fs, leg_list, pic_name, v)
        except Exception as e:
            print('error in file={0}, error msg = {1}'.format(k, e))
@say_name
def geoth_stats(src_path, dst_path ,sm):
    print('sm={0}'.format(sm))
    df_write = pnd.DataFrame(None)
    for k,v in temperature_finder(src_path).items():
        fs, leg_list, pic_name, riv_type = geoth_params(dst_path, k, v)
        pic_name = os.path.split(pic_name)[1]
        pic_name = os.path.splitext(pic_name)[0]
        riv_type_ = gen_geoth_mean(fs, v, riv_type, sm)
        s = pnd.Series(data=[pic_name] + riv_type_ , index=['name'] + leg_list)
        df_write = df_write.append(s, ignore_index=True)
    print('save to: {0}'.format(os.path.join(dst_path,'gmean.csv')))
    df_write.to_csv(os.path.join(dst_path,'gmean.csv'), index=False)

def _geoth_plot(fs, leg_list, pic_name, v):
    f = plt.figure()
    ax = f.gca()

    for tn in v:
        ax = fs.plot(x='arc_length'.format(tn), y=tn, ax=ax)

    plt.title('BLOCK GEOTHREMA', fontsize=12)
    plt.legend(leg_list, loc='best', fontsize=10)
    plt.xlabel('Length [km]')
    plt.ylabel('Depth [Km]')

    mn = [min(fs[i]) for i in v]
    txs = np.linspace(-np.ceil(- min(mn)), 0, np.ceil(- min(mn)) + 1)
    lebs = [str(-i) for i in txs[:-1]] + ['0']
    plt.yticks(txs, lebs)
    plt.savefig(pic_name)
    plt.close()
@say_name
def geoth_params(dst_path, k, v):
    read_csv = pnd.read_csv('{0}/Age-Elevation0.csv'.format(k), header=0, usecols=['Points:2'])
    print(k)
    if k.find('riv') != -1:
        print('riv case')
        pic_name = name_dst_file(k, dst_path, '_riv_geot.png')
        _elevation = min(read_csv['Points:2'])
        riv_type = True
    else:
        print('esc case')
        pic_name = name_dst_file(k, dst_path, '_esc_geot.png')
        riv_type = False
        _elevation = max(read_csv['Points:2'])
    print('_elevation = {0}'.format(_elevation))

    fs = temperature_from_files(k, v, on_point_func=lambda x: x - _elevation)
    leg_list = get_geot_name(v)

    return fs, leg_list, pic_name, riv_type


def get_geot_name(v):
    t_in_enumerate_v_ = ["{0}C".format((int((os.path.splitext(t)[0])[-1]) + 1) * 25) for i, t in enumerate(v)]
    leg_list = list(reversed(t_in_enumerate_v_))
    return leg_list


def convert_names(src_dir):
    for k,v in group_finder(src_dir).items():
        for p in v:
            convert_name = ''
            fileName, fileExtention = os.path.splitext(p)
            if fileExtention.find('csv') == -1:
                print('not csv file: {0}'.format(p))
            with open(os.path.join(k,p),'r') as file:
                l = file.readline()
                if l.find('ApatiteHeAge') != -1:
                    convert_name = 'Age-Elevation0.csv'
                else:
                    try:
                        convert_name = 'Temperature{0}.csv'.format(int(fileName[-1])-1)
                    except ValueError as e:
                        print(e)
                        print('cannot convert file {0}'.format(fileName))

            cmd = 'cp {0} {1}'.format(os.path.join(k,p),os.path.join(k,convert_name))
            os.popen(cmd)

#-----------------------------------------------------
# Nearest neighbour classifier
#-----------------------------------------------------
def distance(p0, p1):
    return np.sum((p0-p1)**2)

def nn_classify(training_set, training_labels, new_example):
    dists = np.array([distance(t, new_example)
        for t in training_set])
    nearest = dists.argmin()
    return training_labels[nearest]

def age_elevation_nn(soure_path, dest_path):
    pass


# TODO: refuctor to OO
if __name__ == '__main__':
    parser = ArgumentParser()
    #set rules
    parser.add_argument( "-i", dest="soure_path", help="source directory")
    parser.add_argument( "-o", dest="dest_path", help="destination directory", default='')
    parser.add_argument( "-e", action="store_true", dest="aeflag", help="age elevation plot", default=False)
    parser.add_argument( "-tp", action="store_true", dest="tflag", help="temperature plot", default=False)
    parser.add_argument( "-ta", action="store_true", dest="tmean", help="temperature mean", default=False)
    parser.add_argument( "-c", action="store_true", dest="convert_name", help="converts group files to Temperature and Age-Elevation", default=False)
    parser.add_argument( "-n", action="store_true", dest="nearest", help="will calculate the nearest neighbour of given data set", default=False)
    parser.add_argument( "-d", dest="esc_dist", help="analysis distanse for escarpment type")


    kvargs = parser.parse_args()

    if kvargs.convert_name: convert_names(kvargs.soure_path)
    if kvargs.aeflag: plot_age_elevation(kvargs.soure_path, kvargs.dest_path)
    if kvargs.tflag: geoth_plot(kvargs.soure_path, kvargs.dest_path)
    if kvargs.tmean: geoth_stats(kvargs.soure_path, kvargs.dest_path, int(kvargs.esc_dist))
    if kvargs.nearest: age_elevation_nn(kvargs.soure_path, kvargs.dest_path)