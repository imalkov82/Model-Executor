__author__ = 'imalkov'

import os

from modeltools.modelinput.pecutils import prepare_to_parse


def eval_prop(f):
    """ DECORATOR: STRIP STR """
    def wrap(*args, **kwargs):
        x = f(*args, **kwargs)
        if isinstance(x, list):
            ll = [l.split(' ') for l in x]
            res = []
            for l in ll:
                res.append([s.strip() for s in l])
            return res
        else:
            return x.strip()
    return wrap

class TopoInput:
    def __init__(self, fpath):
        if os.path.isfile(fpath) and os.path.split(fpath)[1] == 'topo_parameters.txt':
            str_file = prepare_to_parse(fpath)
            pivot = 9 + int(str_file[6])
            self._const_part = str_file[:pivot]
            self._dyn_part = str_file[pivot:]
        else:
            raise IOError('no such file: {0}'.format(fpath))

    def save_to_file(self, fpath = ''):
        ff = self._const_part + self._dyn_part
        with open(fpath, mode='w') as f:
            f.write('\n'.join(ff))

    @property
    @eval_prop
    def nx0(self):
        return self._const_part[2].split(' ')[0]

    @property
    @eval_prop
    def ny0(self):
        return self._const_part[2].split(' ')[1]

    @property
    @eval_prop
    def dlon(self):
        return self._const_part[3].split(' ')[0]

    @property
    @eval_prop
    def dlat(self):
        return self._const_part[3].split(' ')[1]

    @property
    @eval_prop
    def skip(self):
        return self._const_part[4]

    @property
    @eval_prop
    def lon0(self):
        return self._const_part[5].split(' ')[0]

    @property
    @eval_prop
    def lat0(self):
        return self._const_part[5].split(' ')[1]

    @property
    @eval_prop
    def tau(self):
        return self._const_part[7]

    @property
    # @eval_prop
    def duration(self):
        return max([float(l[0]) for l in self.tectosteps])

    @property
    @eval_prop
    def tectosteps(self):
        return self._const_part[- (int(self._const_part[6]) + 1):]

    @property
    def t0(self):
        return self.tectosteps[0][0]

    @property
    def t1(self):
        return self.tectosteps[1][0]

    @property
    def t2(self):
        return self.tectosteps[2][0]

    @property
    @eval_prop
    def f0(self):
        return self._dyn_part[0].split(' ')[0]

    @property
    @eval_prop
    def rc(self):
        s = self._dyn_part[0].split(' ')[1]
        return s.split(',')[0]

    @property
    @eval_prop
    def rm(self):
        return self._dyn_part[0].split(',')[1]

    @property
    @eval_prop
    def E(self):
        return self._dyn_part[0].split(',')[2]

    @property
    @eval_prop
    def n(self):
        return self._dyn_part[0].split(',')[3]

    @property
    @eval_prop
    def L(self):
        return self._dyn_part[0].split(',')[4]

    @property
    @eval_prop
    def nx(self):
        return self._dyn_part[0].split(',')[5]

    @property
    @eval_prop
    def ny(self):
        return self._dyn_part[0].split(',')[6]

    @property
    @eval_prop
    def zl(self):
        return self._dyn_part[1].split(',')[0]

    @property
    @eval_prop
    def nz(self):
        return self._dyn_part[1].split(',')[1]

    @property
    @eval_prop
    def k(self):
        return self._dyn_part[1].split(',')[2]

    @property
    @eval_prop
    def tb(self):
        return self._dyn_part[1].split(',')[3]

    @property
    @eval_prop
    def tt(self):
        return self._dyn_part[1].split(',')[4]

    @property
    @eval_prop
    def la(self):
        return self._dyn_part[1].split(',')[5]

    @property
    @eval_prop
    def pr(self):
        return self._dyn_part[1].split(',')[6]

    #SETTERS
    @nx0.setter
    def nx0(self, val):
        s = self._const_part[2].split(' ')
        s[0] = val
        self._const_part[2] = ' '.join(s)
    @ny0.setter
    def ny0(self, val):
        s = self._const_part[2].split(' ')
        s[1] = val
        self._const_part[2] = ' '.join(s)
    @dlon.setter
    def dlon(self, val):
        s = self._const_part[3].split(' ')
        s[0] = val
        self._const_part[3] = ' '.join(s)
    @dlat.setter
    def dlat(self, val):
        s = self._const_part[3].split(' ')
        s[1] = val
        self._const_part[3] = ' '.join(s)

        # self._const_part[3].split(' ')[1] = val

    @skip.setter
    def skip(self, val):
        self._const_part[4] = val

    @lon0.setter
    def lon0(self, val):
        s = self._const_part[5].split(' ')
        s[0] = val
        self._const_part[5] = ' '.join(s)
        # self._const_part[5].split(' ')[0] = val
    @lat0.setter
    def lat0(self, val):
        s = self._const_part[5].split(' ')
        s[1] = val
        self._const_part[5] = ' '.join(s)
        # self._const_part[5].split(' ')[1] = val

    @tau.setter
    def tau(self, val):
        self._const_part[7] = val

    @duration.setter
    def duration(self, val):
        max([float(l[0]) for l in self.tectosteps])

    @t0.setter
    def t0(self, val):
        s = self.tectosteps
        s[0][0] = val
        self._const_part[- (int(self._const_part[6]) + 1):] = [' '.join(item) for item in s]

    @t1.setter
    def t1(self, val):
        s = self.tectosteps
        s[1][0] = val
        self._const_part[- (int(self._const_part[6]) + 1):] = [' '.join(item) for item in s]

    @t2.setter
    def t2(self, val):
        s = self.tectosteps
        s[2][0] = val
        self._const_part[- (int(self._const_part[6]) + 1):] = [' '.join(item) for item in s]

    @tectosteps.setter
    def tectosteps(self, val):
        self._const_part[- (int(self._const_part[6]) + 1):] = val

    @f0.setter
    def f0(self, val):
        s = self._dyn_part[0].split(' ')
        s[0] = val
        self._dyn_part[0] = ' '.join(s)
        # self._dyn_part[0].split(' ')[0] = val
    @rc.setter
    def rc(self, val):
        #TODO
        s = self._dyn_part[0].split(' ')[1]
        s.split(',')[0]
    @rm.setter
    def rm(self, val):
        self._dyn_part[0].split(',')[1] = val
    @E.setter
    def E(self, val):
        self._dyn_part[0].split(',')[2] = val
    @n.setter
    def n(self, val):
        self._dyn_part[0].split(',')[3] = val
    @L.setter
    def L(self, val):
        self._dyn_part[0].split(',')[4] = val
    @nx.setter
    def nx(self, val):
        self._dyn_part[0].split(',')[5] = val
    @ny.setter
    def ny(self, val):
        self._dyn_part[0].split(',')[6] = val
    @zl.setter
    def zl(self, val):
        self._dyn_part[1].split(',')[0] = val
    @nz.setter
    def nz(self, val):
        self._dyn_part[1].split(',')[1] = val
    @k.setter
    def k(self, val):
        self._dyn_part[1].split(',')[2] = val
    @tb.setter
    def tb(self, val):
        self._dyn_part[1].split(',')[3] = val
    @tt.setter
    def tt(self, val):
        self._dyn_part[1].split(',')[4] = val
    @pr.setter
    def la(self, val):
        self._dyn_part[1].split(',')[5] = val
    @pr.setter
    def pr(self, val):
        self._dyn_part[1].split(',')[6] = val

class TopoParse:
    def __init__(self):
        self._TP_FILE_LINE_NUM = 11

    def __call__(self, str_file):
        str_file = prepare_to_parse(str_file)
        if self._is_valid_line_num(str_file) is False:
            return None
        pivot = 9 + int(str_file[6])
        ll = self.const_parse(str_file[:pivot]) + self.dyn_parse(str_file[pivot:])
        ll = [el if isinstance(el, str) else ",".join(el) for el in ll]
        return ",".join(ll)

    def _is_valid_line_num(self, str_file):
        if len(str_file) <= (self._TP_FILE_LINE_NUM + 1):
            print("FALSE :", str_file)
            return False
        if str.isdigit(str_file[6]) is False:
            print("FALSE :", str_file)
            return False
        return (len(str_file) - (int(str_file[6]) + 1)) == self._TP_FILE_LINE_NUM
    @staticmethod
    def tp_arange(ll):
        ll = [a[0] if len(a) == 1 else a for a in ll]
        # return map(lambda l: l.strip() if isinstance(l, str) else map(str.strip, l), ll)
        return [l.strip() if isinstance(l, str) else [str.strip(s) for s in l] for l in ll]
    @staticmethod
    def dyn_parse(ll):
        if (ll[0].find(' ')) != -1:
            ll[0] = ll[0].replace(' ', ',')
        return TopoParse.tp_arange([a.split(',') for a in ll])
    @staticmethod
    def const_parse(ll):
        return TopoParse.tp_arange([a.split(' ') for a in ll])