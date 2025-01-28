#!/bin/bash
set -e -u

python3 ../heatCoupling.py -n -Tol 1e-05 -which steel -nbrSteps -1

close_log