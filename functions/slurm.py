import os
import time
import numpy as np

def submit_job(func_file, nprocs, args=None, job_dir='./jobs', test=False):

    job_dir = os.path.abspath(job_dir)

    if not os.path.exists(job_dir) and not test:
        os.mkdir(job_dir)

    if args is None:
        args = {}

    if isinstance(args, dict):
        for key, val in list(args.items()):
            if not bool(val):
                args.pop(key)
            elif isinstance(val, (list, tuple)):
                args[key] = " ".join(map(str, val))

        other_args = " ".join(
          [f"--{arg.replace('_','-')} {val}" for arg, val in args.items()]
        )
    elif isinstance(args, (list, tuple)):
        args = list(map(str, args))
        other_args = " ".join(args)
    else:
        raise ValueError('Argument: args not understood.')

    TEMPLATE = """#!/bin/bash
#SBATCH --output={job_file}-%A_%a.out
#SBATCH --error={job_file}-%A_%a.err
#SBATCH --time 06:00:00
#SBATCH --job-name=sdaqs-xpcs
#SBATCH --array=0-{nprocs}

source /cfs/data/pg/sdaqs/esrf-ebs/id10/sc5275/mario/.vapo/bin/activate
echo "SLURM_JOB_ID           $SLURM_JOB_ID"
echo "SLURM_ARRAY_TASK_ID    $SLURM_ARRAY_TASK_ID"

python {func_file} $SLURM_ARRAY_TASK_ID $SLURM_JOB_ID {other_args}

exit
"""

    print(f"With arguments: `{other_args}`")

    timestamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    random_id = np.random.randint(0, 999)
    job_name = f"{timestamp}-{random_id:03}"
    job_file = f"{job_dir}/{job_name}.job"

    job = TEMPLATE.format_map(
      {
          "func_file": func_file,
          "job_file": job_file,
          "nprocs": nprocs-1,
          "other_args": other_args,
      }
    )

    print(f"Generating and submitting sbatch for job {job_name}")

    if not test:
        with open(job_file, "w") as f:
            f.write(job)

        os.system(f"sbatch {job_file}")
    else:
        print(job)

