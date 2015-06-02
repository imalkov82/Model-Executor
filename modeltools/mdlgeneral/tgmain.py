__author__ = 'imalkov'

import os

def replace_input_param():
    arr = []
    name = 'fault_parameters.txt'
    root_dir = '/home/imalkov/Dropbox/M.s/Research/DATA/SESSION_TREE/NODE03'
    for dirpath, dirname, filename in os.walk(root_dir):
        for f in filename:
            if f == name:
                print(os.path.join(dirpath, f))
                newlines = []
                with open(os.path.join(dirpath, f),'r') as my_file:
                    for line in my_file.readlines():
                        # newlines.append(line.replace('41.6', '47.3'))
                        newlines.append(line.replace('47.3','48.0'))

                with open(os.path.join(dirpath, f), 'w') as my_file:
                    for line in newlines:
                        my_file.write(line)

