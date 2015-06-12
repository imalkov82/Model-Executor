__author__ = 'imalkov'


def prepare_to_parse(path):
    res = []
    with open(path) as file:
        lines = file.readlines()
        #remove empty lines and full file comments
        # res = [(line.lstrip())[:-1] for line in lines]
        res = [(line.lstrip()).replace('\n','') for line in lines]
        res = filter(lambda line: False if (len(line) == 0 or line[0] in ['$', '\n']) else True, res)
        res = [line.split('$')[0].strip() for line in res]
    return res

# print(prepare_to_parse('/home/imalkov/Dropbox/M.s/Research/DATA/SESSION_TREE/NODE02/Session2I/input/topo_parameters.txt'))