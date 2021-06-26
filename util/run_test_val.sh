#!/bin/bash
set -e

for fl in tests/*.txt
do
    echo "validating $fl"
    ./val < $fl
done
