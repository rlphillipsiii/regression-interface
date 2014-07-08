#!/bin/sh
#
""":"
exec $REGRESSION_INT/wrapper/unix/python_setup $0 "$@"
":"""

# native imports
import sys
import os

# pylib imports
import testsuite as ts
import commandopts as opts

from testsuite import TestSuite

help_string = """
Usage: %s [ options ]

    Options:
        -h|--help      - prints this message and exits
        -r|--recursive - recursively searches for testcases
        -s|--strict    - any non-zero exit code will produce a failure
                         as opposed to the default which will only
                         produce a failure on non-zero exit codes from
                         the setup and test scripts
""" % sys.argv[0]

# 

cmdline = opts.Opts()
cmdline.add_option('-h', alternate='--help')
cmdline.add_option('-r', alternate='--recursive')
cmdline.add_option('-e', alternate='--exclude')
cmdline.add_option('-l', alternate='--list')

args = cmdline.parse_args(sys.argv)

recursive = False
strict = False
list_only = False

if '-h' in args:
    print help_string
    sys.exit(0)
if '-r' in args:
    recursive = True
if '-s' in args:
    strict = True
if '-e' in args:
    # TODO: finish the exclude option
    pass
if '-l' in args:
    list_only = True
    
tests = ts.find_testcases(recursive)
if len(tests) == 0:
    print 'Error: no testcases were found.'
    sys.exit(1)

if list_only:
    print '%d Test(s) Found' % len(tests)
    
    base = ''
    if recursive:
        base = os.path.commonprefix(tests)
        print 'Base Directory: %s\n' % base
    
    for tc in tests:
        print tc.replace(base, '')

    sys.exit(0)
    
suite = TestSuite(tests=tests)
suite.run_suite(strict)
