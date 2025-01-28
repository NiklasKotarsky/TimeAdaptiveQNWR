#!/bin/bash
set -e -u

python3 ../heatCoupling.py -n -Tol 1e-5 -which "water"

close_log
