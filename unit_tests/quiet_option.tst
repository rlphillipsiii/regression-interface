#!/bin/sh

cd $REGRESSION_INT

name="quiet option"
flags="-q -r"

source unit_tests/common/setup
source unit_tests/common/dotest
