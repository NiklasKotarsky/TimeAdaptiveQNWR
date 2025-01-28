#!/bin/bash
set -e -u

python3 ../heatCoupling.py -n -Tol 0.0001 -which steel -nbrSteps -1

close_log