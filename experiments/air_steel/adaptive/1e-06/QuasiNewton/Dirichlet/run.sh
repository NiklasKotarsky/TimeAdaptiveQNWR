#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol 1e-06 -which air -nbrSteps -1

close_log