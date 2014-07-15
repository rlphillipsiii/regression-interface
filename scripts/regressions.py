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
import testsuite
import commandopts as opts

from testsuite import TestSuite
from testsuite import OperationNotImplementedException

help_string = """
Usage: %s [ options ]

    Options:
        -h|--help
            Prints this message and exits.

        -r|--recursive
            Recursively searches for testcases.

        -s|--strict
            Any non-zero exit code will produce a failure as opposed
            to the default which will only produce a failure on 
            non-zero exit codes from the setup and test scripts.

        -q|--quiet
            Surpresses the test suite summary output and the passed
            test messages.

        -e|--exclude <file>
            Specifies a file containing a list of tests that should
            be excluded from the run if they are recursively found.
            The file should contain the name of each test on its
            own line.  In other words, it is a newline separated
            list of test names that should be ignored.
""" % sys.argv[0]

cmdline = opts.Opts()
cmdline.add_option('-h', alternate='--help')
cmdline.add_option('-r', alternate='--recursive')
cmdline.add_option('-s', alternate='--script')
cmdline.add_option('-l', alternate='--list')
cmdline.add_option('-q', alternate='--quiet')
cmdline.add_option('-e', alternate='--exclude', value=True)
cmdline.add_option('-t', alternate='--thread', value=True)
cmdline.add_option('-p', alternate='--process', value=True)

args = cmdline.parse_args(sys.argv)

exclude_file = None

recursive = False
strict    = False
list_only = False
quiet     = False

threads = 0
procs   = 0

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
if '-t' in args:
    threads = int(args['-t'])
if '-p' in args:
    procs = int(args['-p'])
    
tests = testsuite.find_testcases(recursive)
if len(tests) == 0:
    print 'Error: no testcases were found.'
    sys.exit(1)

suite = TestSuite(' '.join(sys.argv), tests=tests)
if exclude_file is not None:
    try:
        names = [ n.lstrip().rstrip() for n in open(exclude_file, 'r').read().lstrip().rstrip().split('\n') ]
        suite.remove_tests(names)
    except OSError as e:
        print 'Warning: an error occurred while parsing the exclude file'
        print e
        
if list_only:
    base = ''
    if recursive and len(tests) > 1:
        base = '%s/' % os.getcwd()
        print 'Base Directory: %s\n' % base

    suite.print_tests(base)
    print 'Test(s) Found: %d' % len(tests)
    
    sys.exit(0)

if threads > 0:
    raise OperationNotImplementedException('Threading not quite ready yet...Sorry')
else if procs > 0:
    raise OperationNotImplementedException('Multiple processes not quite ready yet...Sorry')
else:
    suite.run_suite(strict, quiet)
