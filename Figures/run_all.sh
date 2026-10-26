#!/usr/bin/env bash
# Redraw every figure from its own folder's data.  Each script is independent;
# this only saves typing.  A folder whose data/ has not been exported yet is
# reported and counted as a failure.
set -uo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-python}
missing=()
for d in Figure01 Figure02 Figure03 Figure04 Figure05 Figure06 Figure07 Figure08 \
         Figure09 Figure10 Figure11 Figure12 Figure13 Figure14 Figure15; do
    if [[ ! -d "$d/data" ]]; then
        echo "$d: no data/ -- run analysis/export_figure_data.py first"
        missing+=("$d"); continue
    fi
    (cd "$d" && "$PY" plot.py) || missing+=("$d")
done
if (( ${#missing[@]} )); then echo "not drawn: ${missing[*]}"; exit 1; fi
echo "all 15 figures drawn"
