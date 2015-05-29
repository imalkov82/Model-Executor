__author__ = 'imalkov'


def prepare_to_parse(path):
    res = []
    with open(path) as file:
        lines = file.readlines()
        #remove empty lines and full file comments
        # res = map(lambda line: (line.lstrip())[:-1] ,lines)

        # res = map(lambda line: line.split('$')[0].strip(), res)
        res = [(line.lstrip())[:-1] for line in lines]
        res = filter(lambda line: False if (len(line) == 0 or line[0] in ['$', '\n']) else True, res)
        res = [line.split('$')[0].strip() for line in res]
    return res

# gp = GenParser()
# print gp('/home/imalkov/Dropbox/M.s/Research/DATA/BDFAULTS/TOPO_TYPES2/fault_files/fault_parameters.txt')