#!/bin/bash

set -e

sol=./solutions/thinice_brute.optbin

for t in $(ls tests/*.txt)
do
    echo $sol $t
    tans=$(echo $t | sed -e 's:.txt:.ans:')
    $sol <$t >$tans
done
