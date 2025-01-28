#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol -1 -which air -nbrSteps 32

close_log