#!/bin/bash
set -e -u

python3 ../heatCoupling.py -n -Tol -1 -which water -nbrSteps 32

close_log