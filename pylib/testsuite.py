import os
import glob
import subprocess
import yaml

config_file = 'test_metadata.conf'

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
    
    proc = subprocess.Popen(script)
    proc.wait()

    return (proc.returncode == 0)

def validate_configuration(config):
    msg_base = 'The \'%s\' field is missing from the test case metadata.'
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
        
def write_test_summary(tc):
    pass
    
class TestSuite:
    def __init__(self, tests=[]):
        self.testcases = []
        self.build_testsuite(tests)
        
    def build_testsuite(self, tests):
        for tc in tests:
            try:
                self.testcases.append(TestCase(tc))
            except MalformedTestCaseException as e:
                print 'Error while processing %s' % tc
                print e
                
    def get_tests(self):
        return self.testcases
        
    def add_test(self, test):
        self.testcases.append(test)

    def write_log(self, directory):
        pwd = os.getcwd()
        
        os.chdir(directory)
        write_test_summary(self.testcases)
        os.chdir(pwd)

    def run_suite(self, strict):
        for tc in self.testcases:
            tc.run_test(strict)

        self.write_log(os.getcwd())
        
class TestCase:
    def __init__(self, path, status=None):
        self.path = path
        self.status = None
        self.message = ''

        self.load_configuration()
        
    def load_configuration(self):
        config = None
        
        try:
            config = yaml.load(open(os.path.join(self.path, config_file), 'r').read())
        except:
            msg = 'Failed to parse metadata.  Test case will be ignored'
            raise MalformedTestCaseException(msg)

        validate_configuration(config)
        self.name = config['name']
        self.setup = config['setup']
        self.test = config['dotest']
        self.cleanup = config['cleanup']

    def pass_test(self, quiet=False):
        if not quiet:
            print 'Test %s passed.' % self.name
            
        self.status = True

    def fail_test(self, message):
        self.status = False

        print 'Test %s failed.' % self.name
        print 'Reason: %s' % message
        
        self.message = message
        
    def get_status(self):
        return self.status

    def run_test(self, strict):
        pwd = os.getcwd()

        print 'Running Test: %s' % self.name
        
        os.chdir(self.path)
        if not run_script(self.setup):
            self.fail_test('Abnormal exit from \'SETUP\'.')
        elif not run_script(self.test):
            self.fail_test('The \'DOTEST\' command exited with a non-zero return code.')
        elif not run_script(self.cleanup) and strict:
            self.fail_test('Abnormal exit from \'CLEANUP\'.')
        else:
            self.pass_test()

        print ''
        
        write_test_summary([self])
        os.chdir(pwd)

class MalformedTestCaseException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'Error Message: %s' % self.value
