#!/bin/bash
#SBATCH -A CFD154
#SBATCH -J MFC-PARAVIEW-1
#SBATCH -N 1
#SBATCH -p gpu
#SBATCH -t 0:05:00

cd $SLURM_SUBMIT_DIR
date

module load paraview/5.10.0-egl

srun -n 28 pvbatch para_example.py
