#!/bin/bash

for sol in thinice_brute.optbin baseline.optbin baseline-worse.optbin
do
    echo "Running $sol"

    time ./solutions/$sol <tests/60-huge-inexact.txt >out_60_$sol.txt
done
