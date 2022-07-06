from Xana import Xana
import sys
import os
import yaml


def run_analysis(proc_id, slurm_id, maskfile, setupfile, first, last, outdir, *args):
    with open('filelist.yml', 'r') as f:
        folders = yaml.load(f, Loader=yaml.FullLoader)[proc_id]
    
    ana = Xana(fmtstr='ebs_id10_eiger500k',
	       detector='eiger500k',
               maskfile=maskfile,
               setupfile=setupfile)

    outdir = f'./results/{outdir}/p{slurm_id:02d}'
    if not os.path.isdir(outdir):
        os.makedirs(outdir, exist_ok=True)
    ana.mksavdir(outdir)
    
    for folder in folders:
        ana.connect(folder)

    for index in ana.meta.index.values:
        ana.analyze(index, 'saxs',  first=first, last=last)
        if ana.meta.loc[index, 'nframes'] > 100:
            ana.analyze(index, 'xpcs', norm='symmetric', first=first, last=last, twotime_par=[2,4,6],
			saxs=None, nread_procs=1, nprocs=30, chunk_size=250, verbose=False)

if __name__ == '__main__':
    proc_id, slurm_id, maskfile, setupfile, first, last, outdir, *args = sys.argv[1:]
    run_analysis(int(proc_id), int(slurm_id), maskfile, setupfile, int(first), int(last), outdir)

