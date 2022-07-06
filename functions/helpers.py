import yaml
import numpy as np

    
def dump_filelist(filelist, filename='filelist.yml', nprocs=16):
    files_per_proc = int(np.ceil(len(filelist)/nprocs))
    iproc = 0
    to_file = {}
    for i in range(len(filelist)):
        if i % files_per_proc == 0:
            if i > 0:
                iproc += 1
            to_file[iproc] = []

        to_file[iproc].append(filelist[i])


    with open(filename, 'w') as f:
        yaml.dump(to_file, f)