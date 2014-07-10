#!/bin/sh

cd $REGRESSION_INT

name="strict option"
flags="-s -r"

source unit_tests/common/setup
source unit_tests/common/dotest
