#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol 1e-05 -which water -nbrSteps -1

close_log