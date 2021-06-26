#!/bin/bash

set -e

function make_test() {
    echo "Generating $1"
    cat ./bio/mouse.txt >/tmp/wip.txt
    echo $(cat ./bio/examples_clean/$2 | wc -l) | tee -a /tmp/wip.txt >/dev/null

    cat ./bio/examples_clean/$2 | tee -a /tmp/wip.txt >/dev/null

    ./util/cleanify.bin </tmp/wip.txt >tests/$1
}

# make_test 20-mouse-simple-exact.txt ONT.exact.FSM.chr7.tsv
make_test 30-mouse-exact.txt ONT.exact.ISM.chr7.tsv
