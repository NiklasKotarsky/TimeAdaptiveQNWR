#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol 0.0001 -which water -nbrSteps -1

close_log