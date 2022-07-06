#!/usr/bin/env python
# coding: utf-8

import os
import sys
import numpy as np
import time
import pickle
import yaml
from glob import glob
from tqdm import tqdm
import pandas as pd
import h5py
import re
from pathlib import Path
import argparse

from Xana import Xana

from functions.helpers import dump_filelist
from functions.metadata import get_rep, get_scan_number
from functions.slurm import submit_job


parser = argparse.ArgumentParser()
parser.add_argument("datafolder", type=str, 
    help='the name of the measurement folder without scan number')
parser.add_argument("datasetnumber", type=int, help="the dataset number")
parser.add_argument('--reps-per-spot', '-reps', type=int, help="number of repetitions per spot", default=1)
parser.add_argument('--proc', action="store_true",  help="activate processing")


def convert2hdf5(xana, filename):
    xana.db = xana.db.sort_values(by='scannumber')
    xpcs_indices = xana.db[xana.db['analysis'] == 'xpcs'].index.values
    nxpcs = len(xpcs_indices)
    xpcs_scans = xana.db.loc[xpcs_indices, 'scannumber'].values
    saxs_indices = xana.db[xana.db['analysis'] == 'saxs'].index.values
    nsaxs = len(saxs_indices)
    saxs_scans = xana.db.loc[saxs_indices, 'scannumber'].values

    qI = xana.get_item(saxs_indices[0])['soq'][:,0]
    nqI = len(qI)
    tmp = xana.get_item(xpcs_indices[0])
    ttc_times = tmp['twotime_xy']
    ntimes = len(ttc_times)
    delay = tmp['corf'][1:,0]
    ndelay = len(delay)
    qv = tmp['qv']
    nq = len(qv)
    twotime_par = tmp['twotime_par']
    nttc = len(twotime_par)
    print((f"{nqI = }, {nq = }, {ntimes = }, {nxpcs = }, {nsaxs = } "
           f"{ndelay = }, {nttc = }"))

    with h5py.File(filename, 'a') as f:
        ttcs = f.create_dataset('/xpcs/ttcs/ttcs', shape=(nxpcs, nttc, ntimes, ntimes), dtype=np.float32, compression="gzip")
        g2s = f.create_dataset('/xpcs/g2s/g2s', shape=(nxpcs, nq, ndelay), dtype=np.float32, compression="gzip")
        I = f.create_dataset('/saxs/I', shape=(nsaxs, nqI), dtype=np.float32, compression="gzip")
        f['/xpcs/g2s/delay'] = delay
        f['/xpcs/g2s/q'] = qv
        f['/xpcs/ttcs/q'] = qv[twotime_par]
        f['/xpcs/ttcs/times'] = ttc_times
        f['/xpcs/scans'] = xpcs_scans
        f['/saxs/q'] = qI
        f['/saxs/scans'] = saxs_scans
        
        for i, xpcs_index in tqdm(enumerate(xpcs_indices), desc='writing XPCS results',  total=len(xpcs_indices)):
            tmp = xana.get_item(xpcs_index)
            ttcs[i] = np.stack(list(tmp['twotime_corf'].values()), axis=0)
            g2s[i] = tmp['corf'][1:,1:].T

        for i, saxs_index in tqdm(enumerate(saxs_indices), desc='writing SAXS results',  total=len(saxs_indices)):
            tmp = xana.get_item(saxs_index)
            I[i] = tmp['soq'][:,1]

if __name__ == "__main__":
    args = parser.parse_args()
    datafolder = args.datafolder
    datasetnumber = args.datasetnumber

    ana_db_files = glob('results/**/analysis_database.pkl', recursive=True)
    xana = Xana()
    for i, f in enumerate(ana_db_files):
        if i == 0:
            xana.load_db(f)
        else:
            xana.append_db(f)

    xana.db['rep'] = xana.db['master'].apply(get_rep, reps_per_spot=args.reps_per_spot)
    xana.db['scannumber'] = xana.db['datdir'].apply(lambda x: get_scan_number(str(x)))
    filename = f"{datafolder}_{datasetnumber:04}"
    xana.db = xana.db[xana.db['datdir'].apply(str).str.contains(filename)]
    print(xana.db.head(10))
    
    if args.proc:
        convert2hdf5(xana, filename + '.h5')

