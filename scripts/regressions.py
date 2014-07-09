#!/bin/sh
# -*- mode: Python; -*-
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
        -e|--exclude <file>
""" % sys.argv[0]

# 

cmdline = opts.Opts()
cmdline.add_option('-h', alternate='--help')
cmdline.add_option('-r', alternate='--recursive')
cmdline.add_option('-s', alternate='--script')
cmdline.add_option('-e', alternate='--exclude')
cmdline.add_option('-l', alternate='--list')
cmdline.add_option('-q', alternate='--quiet')

args = cmdline.parse_args(sys.argv)

exclude_file = None

recursive = False
strict = False
list_only = False
quiet = False

if '-h' in args:
    print help_string
    sys.exit(0)
if '-r' in args:
    recursive = True
if '-s' in args:
    strict = True
if '-e' in args:
    exclude_file = args['-e']
if '-l' in args:
    list_only = True
if '-q' in args:
    quiet = True
    
tests = ts.find_testcases(recursive)
if len(tests) == 0:
    print 'Error: no testcases were found.'
    sys.exit(1)

suite = TestSuite(tests=tests)
if list_only:
    base = ''
    if recursive and len(tests) > 1:
        base = '%s/' % os.getcwd()
        print 'Base Directory: %s\n' % base

    suite.print_tests(base)
    print 'Test(s) Found: %d' % len(tests)
    
    sys.exit(0)

suite.run_suite(strict, quiet)
