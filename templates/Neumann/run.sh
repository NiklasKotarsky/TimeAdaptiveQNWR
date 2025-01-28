#!/bin/bash
set -e -u

python3 ../heatCoupling.py -n -Tol {{tol}} -which {{case}} -nbrSteps {{nbrSteps}}

close_log
