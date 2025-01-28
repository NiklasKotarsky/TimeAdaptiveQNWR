#!/bin/bash
set -e -u

python3 ../heatCoupling.py -n -Tol -1 -which steel -nbrSteps 12928

close_log