#!/usr/bin/env bash
#SBATCH --job-name=rapid-fig
#SBATCH --output=rapid_fig_%j.log
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-.}/rapid_figures"

export RAPID_FIG_OUTPUT="${RAPID_FIG_OUTPUT:-$PWD/outputs}"
bash cluster/run_compute.sh
bash cluster/run_plot.sh
