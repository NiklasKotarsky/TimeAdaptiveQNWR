#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol -1 -which water -nbrSteps 64

close_log