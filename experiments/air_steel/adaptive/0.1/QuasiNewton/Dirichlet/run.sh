#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol 0.1 -which air -nbrSteps -1

close_log