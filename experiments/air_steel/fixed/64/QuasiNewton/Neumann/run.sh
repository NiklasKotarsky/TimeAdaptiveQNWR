#!/bin/bash
set -e -u

python3 ../heatCoupling.py -n -Tol -1 -which steel -nbrSteps 64

close_log