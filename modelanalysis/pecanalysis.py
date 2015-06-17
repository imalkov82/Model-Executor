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

# TODO: optimize using pecinputstats.csv
def define_max_age(df1, tot_len, best_tread, riv_case, oldest_age):
    print('best_tread={0}, tot_len={1}, oldest_age={2}'.format(best_tread, tot_len, oldest_age))

    df1 = df1[~pnd.isnull(df1['slope'])]
    df1 = df1[(df1.r_square < 1)]

    df1 = df1.sort(['arr_len'], ascending = [1]).head(np.round(df1.shape[0] * 0.5))
    df1['slope_diff'] = abs(df1['slope'] - best_tread)

    if riv_case is True:
        print('river case')
        df1 = df1.sort(['arr_len'], ascending = [0]).head(np.round(df1.shape[0] * 0.5))
        df1 = df1.sort(['r_square'], ascending = [0]).head(np.round(df1.shape[0] * 0.5))
        riv_fd_by_slope_diff = df1
        df2 = riv_fd_by_slope_diff[riv_fd_by_slope_diff.r_square == riv_fd_by_slope_diff.r_square.max()]
    else:
        print('escarpment case')
        riv_fd_by_slope_diff = df1.sort(['slope_diff'], ascending = [1]).head(np.round(df1.shape[0] * 0.5))
        # df1 = df1.sort(['slope_diff'], ascending = [1]).head(np.round(df1.shape[0] * 0.5))
        # riv_fd_by_slope_diff = df1[df1.sup_age < np.ceil(0.85 * oldest_age)]
        df2 = riv_fd_by_slope_diff[riv_fd_by_slope_diff.slope_diff == riv_fd_by_slope_diff.slope_diff.min()]
    max_age = df2['sup_age'].max()
    print(riv_fd_by_slope_diff)
    print('max_age = {0}'.format(max_age))
    s = df2[df2['sup_age'] == max_age]
    return max_age , s['slope'], s['r_square']

def find_max_treadline(data_frame, opt_tread, riv_case):
    pnd_ds = data_frame['ApatiteHeAge']
    ds = np.array(pnd_ds)

    max_age = 0
    min_tol = 1

    slope_dict = {}
    slope_dict['slope'] = []
    slope_dict['r_square'] = []
    slope_dict['arr_len'] = []
    slope_dict['sup_age'] = []
    slope_dict['max_height'] = []

    for sup_age in sorted(ds)[1:]:
        x = data_frame[data_frame['ApatiteHeAge'] < sup_age]['ApatiteHeAge']
        y = data_frame[data_frame['ApatiteHeAge'] < sup_age]['Points:2']
        minh = data_frame['Points:2'].min()
        slope, intercept, r_value, p_value, std_err = linregress(x, y)

        slope_dict['slope'].append(slope)
        slope_dict['r_square'].append(r_value**2)
        slope_dict['arr_len'].append(len(x))
        slope_dict['sup_age'].append(sup_age)
        slope_dict['max_height'].append(max(y)- minh)

        # if abs(opt_tread - slope) < min_tol:
        #     min_tol = abs(opt_tread - slope)
        #     max_age = sup_age

    pnd_data_frame = pnd.DataFrame(slope_dict, columns = ['slope', 'r_square', 'arr_len', 'sup_age', 'max_height'])
    max_age, slope, r_square = define_max_age(pnd_data_frame, len(ds), opt_tread, riv_case, max(ds))
    return max_age, slope, r_square

def uplift_from_file_name(fname):
    s_loc = fname.find('csv') - 3
    return int(fname[s_loc :s_loc + 1]) * 0.1

def plot_age_elevation(src_path, dst_path):
    for dirname, name in ea_finder(src_path):
        ea = os.path.join(dirname, name)
        root_dir = os.path.split(dirname)[0]
        print(ea)
        cols = ['ApatiteHeAge','Points:2', 'arc_length']
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
            plot_ea(frame1, df_res, pic_name, uplift_from_file_name(ea), riv_case)
        except Exception as e:
            print('error in file={0}, error msg = {1}'.format(ea, e))

############### TEMPERATURE ###################################################
def gen_geoth_mean(fs, col_name_arr, riv_type):
    res = []
    for tn in col_name_arr:
        if riv_type is False:
            print('esc type')
            sm = 5
        else:
            print('riv type')
            s = fs[fs[tn] == min(fs[tn])]['arc_length']
            sm = s[s.index[:]].mean()
        abs_sm___ = fs['arc_length'] >= (sm - abs(sm * 0.1))
        sm_abs_sm___ = fs['arc_length'] < (sm + abs(sm * 0.1))
        res_fs = fs[(abs_sm___) & (sm_abs_sm___)]
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
        max_height = max(pnd.read_csv('{0}/Age-Elevation0.csv'.format(k), header = 0, usecols=['Points:2'])['Points:2'])
        print(max_height)
        fs = temperature_from_files(k, v, on_point_func=lambda x:  x - max_height)

        f = plt.figure()
        ax = f.gca()
        try:
            for tn in v:
                ax = fs.plot(x='arc_length', y=tn, ax=ax)

            t_in_enumerate_v_ = ["{0}C".format((int((os.path.splitext(t)[0])[-1]) + 1) * 25) for i, t in enumerate(v)]
            leg_list = list(reversed(t_in_enumerate_v_))
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
                        riv_type_ = ['{0}={1}'.format(tt, vv) for tt, vv in zip(leg_list, gen_geoth_mean(fs, v, riv_type))]
                        join = ','.join(list(reversed(riv_type_)))
                        n__format = '{0}: {1}\n'.format(os.path.split(pic_name)[1], join)
                        f.write(n__format)
        except Exception as e:
            print('error in file={0}, error msg = {1}'.format(k, e))

def convert_names(src_dir):
    count = 1
    for k,v in group_finder(src_dir).items():
        # print('key={0}: val={1}'.format(k, ' '.join(sorted(v))))
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
