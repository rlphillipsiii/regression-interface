#!/bin/sh

cd $REGRESSION_INT
source unit_tests/setup

$REGRESSION_INT/scripts/regressions.py -l -r &> $COMPARE/l_option.out
if [[ "$1" == "-u" ]]; then
    mv $COMPARE/l_option.out $GOLDEN
    echo "Golden updated"

    exit 0
fi

out=$( diff $COMPARE/l_option.out $GOLDEN/l_option.out )
if [[ "$out" == "" ]]; then
    echo "-l option test passed"
    rm $COMPARE/l_option.out
else
    echo "-l option test failed"
fi
