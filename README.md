# fysikum-slurm-scripts
Scripts to analyze data using Slurm on the fysikum cluster. The scripts are designed to analyze SAXS and XPCS data acquired at beamline ID10 (ESRF-EBS) on the HPC cluster of Fysikum (Stockholm University) but can be modified to process data from various beamlines on other clusters. [Xana](https://github.com/reiserm/Xana) is used for the data processing while [Slurm](https://slurm.schedmd.com/documentation.html) is used to run batch jobs.

## Infos
- Load a python environment with `module load conda`.
- Install requirements with `pip install -r requirements.txt`.

## Starting a Jupyter Lab server 

`ssh` to the cluster and use local port forwarding:

```sh
ssh -L 2903:127.0.0.1:8899 -p 31422 <username>@sol-login.fysik.su.se
```

`-L 2903:127.0.0.1:8899` forwards port `8899` of the server to port `2903` on the local machine, e.g., your laptop. These numbers are more or less arbitrary. Now a Jupyter Lab instance can be started on the server. Make sure that Jupyter Lab is using the second port:

```sh
jupyter lab --no-browser --port=8899
```

**While the SSH session is running** you can connect to the Jupyter Lab session from your local browser by using the address `localhost:2903`, i.e., the first port.
