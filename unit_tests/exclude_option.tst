#!/bin/sh

cd $REGRESSION_INT

name="exclude option"
flags="-r -e unit_tests/extras/excluded_tests"

source unit_tests/common/setup
source unit_tests/common/dotest
