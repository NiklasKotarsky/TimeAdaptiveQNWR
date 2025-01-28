#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol -1 -which air -nbrSteps 34560

close_log