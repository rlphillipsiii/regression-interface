import os
import glob
import subprocess
import yaml
import datetime

config_file   = 'test_metadata.conf'
testsuite_log = 'testsuite.log'
testcase_log  = 'testcase.log'

def is_testcase_dir(path):
    pwd = os.getcwd()

    os.chdir(path)
    files = glob.glob('*')

    return (config_file in files)

def find_testcases(recursive):
    if not recursive:
        if is_testcase_dir(os.getcwd()):
            return [os.getcwd()]
        else:
            return []

    return _find_testcases()
    
def _find_testcases():
    tests = []

    pwd = os.getcwd()
    if is_testcase_dir(pwd):
        tests.append(pwd)

    for item in glob.glob('*'):
        if not os.path.isdir(item) or item == 'golden':
            continue

        os.chdir(item)
        tests += _find_testcases()
        os.chdir(pwd)
        
    return tests

def run_script(script):
    print 'Executing Command: %s' % script

    try:
        proc = subprocess.Popen(script)
        proc.wait()

        return (proc.returncode == 0)
    except OSError as e:
        print e
        return False

def run_regression(flags):
    script = os.path.join(os.environ['REGRESSION_INT'], 'scripts')
    script = os.path.join(script, 'regression.py')
    
    proc = subprocess.Popen([script] + flags)
    return proc
    
def validate_configuration(config):
    msg_base = 'The "%s" field is missing from the test case metadata.'
    msg_base += '  The test case will be ignored.'
    
    if not 'name' in config:
        msg = msg_base % 'NAME'
        raise MalformedTestCaseException(msg)

    if not 'setup' in config:
        msg = msg_base % 'SETUP'
        raise MalformedTestCaseException(msg)

    if not 'cleanup' in config:
        msg = msg_base % 'CLEANUP'
        raise MalformedTestCaseException(msg)

    if not 'dotest' in config:
        msg = msg_base % 'DOTEST'
        raise MalformedTestCaseException(msg)

    if '|' in config['name']:
        msg = 'Test name contains illegal characters'
        msg += '  The test case will be ignored'
        raise MalformedTestCaseNameException(msg)

        
class TestSuite:
    def __init__(self, cmd, tests=[]):
        self.cmd = cmd
        self.testcases = []
        self.start_time = datetime.datetime.now()
        
        self.passes = []
        self.failures = []
        
        self.build_testsuite(tests)
        
    def build_testsuite(self, tests):
        for tc in tests:
            try:
                self.testcases.append(TestCase(tc))
            except MalformedTestCaseException as e:
                print 'Error while processing %s' % tc
                print e
            except MalformedTestCaseException as e:
                print 'Illegal test case name in %s' % tc
                print e

    def remove_tests(self, names):
        for name in names:
            index = self.is_in_testcases(name)
            if index == -1:
                continue
                
            del self.testcases[index]

    def is_in_testcases(self, name):
        for i in range(len(self.testcases)):
            if self.testcases[i].matches(name):
                return i

        return -1
        
    def get_tests(self):
        return self.testcases
        
    def add_test(self, test):
        self.testcases.append(test)

    def write_log(self, directory, quiet):
        pwd = os.getcwd()
        
        os.chdir(directory)
        self.write_suite_summary(quiet)
        os.chdir(pwd)

    def print_tests(self, base):
        max_len = 0
        for tc in self.testcases:
            if len(tc.get_name()) > max_len:
                max_len = len(tc.get_name())
                
        for tc in self.testcases:
            print '%s: %s' % (tc.get_name().ljust(max_len+1), tc.get_path().replace(base, ''))
            
    def run_suite(self, strict, quiet):
        for tc in self.testcases:
            if tc.run_test(strict, quiet):
                self.passes.append(tc)
            else:
                self.failures.append(tc)

        self.runtime = (datetime.datetime.now()-self.start_time).total_seconds()
        self.write_log(os.getcwd(), quiet)

    def get_suite_summary(self):
        log =  'TYPE: Suite\n'
        log += 'COMMAND: %s\n' % self.cmd
        log += 'TIME_RUN: %s\n' % self.start_time.strftime('%d %B %Y %H:%M:%S')
        log += 'RUNTIME: %d\n' % self.runtime
        log += 'PASSES: %d\n' % len(self.passes)
        log += 'FAILURES: %d\n' % len(self.failures)
        log += 'TOTAL: %d\n\n' % len(self.testcases)

        log += 'PASS:\n'
        for tc in self.passes:
            log += '    %s|%s\n' % (tc.get_name(), tc.get_path())

        log += '\n'
        log += 'FAIL:\n'
        for tc in self.failures:
            log += '    %s|%s\n' % (tc.get_name(), tc.get_path())

        return log
        
    def write_suite_summary(self, quiet):
        summary = self.get_suite_summary()

        fout = open(testsuite_log, 'w')
        print >> fout, summary
        fout.close()
        
        if not quiet:
            print summary


class TestCase:
    def __init__(self, path, status=None):
        self.path = path
        self.status = None
        self.message = ''

        self.basedir = os.getcwd()
        self.load_configuration()
        
    def load_configuration(self):
        config = None
        
        try:
            config = yaml.load(open(os.path.join(self.path, config_file), 'r').read())
        except:
            msg = 'Failed to parse metadata.  Test case will be ignored'
            raise MalformedTestCaseException(msg)

        validate_configuration(config)
        self.name = config['name'].lstrip().rstrip()
        self.setup = config['setup']
        self.test = config['dotest']
        self.cleanup = config['cleanup']

    def matches(self, name):
        return (self.name == name)
        
    def pass_test(self, quiet):
        if not quiet:
            print 'Test %s passed.' % self.name
            
        self.status = True

    def fail_test(self, message):
        self.status = False

        print 'Test "%s" failed.' % self.name
        print 'Reason: %s' % message
        
        self.message = message

    def get_status(self):
        return self.status

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path
        
    def run_test(self, strict, quiet):
        print 'Running Test: %s' % self.name
        self.start_time = datetime.datetime.now()
        
        os.chdir(self.path)
        if not run_script(self.setup):
            self.fail_test('Abnormal exit from "SETUP".')
        elif not run_script(self.test):
            self.fail_test('The "DOTEST" command exited with a non-zero return code.')
        elif not run_script(self.cleanup) and strict:
            self.fail_test('Abnormal exit from "CLEANUP".')
        else:
            self.pass_test(quiet)

        print ''

        self.write_test_summary()
        os.chdir(self.basedir)
        
        return self.status

    def get_test_summary(self):
        pass
        
    def write_test_summary(self):
        log = self.get_test_summary()
        
class MalformedTestCaseException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Error Message: %s' % self.message

class MalformedTestCaseNameException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Error Message: %s' % self.message

class OperationNotImplementedException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Error Message: %s' % self.message
