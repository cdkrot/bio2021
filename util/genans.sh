#!/bin/bash

set -e

sol=./solutions/baseline.optbin

for t in $(ls tests/{1,2,3,5,6}*.txt)
do
    echo $sol $t
    tans=$(echo $t | sed -e 's:.txt:.ans:')
    $sol <$t >$tans
done
