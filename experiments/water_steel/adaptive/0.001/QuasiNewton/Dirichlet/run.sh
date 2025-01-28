#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol 0.001 -which water -nbrSteps -1

close_log