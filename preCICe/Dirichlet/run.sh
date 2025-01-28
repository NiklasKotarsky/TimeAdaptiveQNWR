#!/bin/bash
set -e -u

python3 ../heatCoupling.py -d -Tol 1e-5 -which "air"

close_log
