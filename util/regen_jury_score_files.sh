#!/bin/bash

set -e

rm -f tests/*.lzma

for tst in 70-welcome-approx # 80-big-approx 90-huge-approx
do
    echo $tst
    
    time env test=tests/$tst.txt test_ans=tests/$tst.ans python3 check2.py print_score < tests/$tst.ans 2> tests/$tst.jury_score

    echo "generated jury_score for $tst"

    lzma --keep tests/$tst.ans
    echo "generated $tst.ans.lzma"

    lzma --keep tests/$tst.jury_score
    echo "generated $tst.jury_score.lzma"

    lzma --keep tests/$tst.txt
    echo "generated $tst.txt.lzma"
done
