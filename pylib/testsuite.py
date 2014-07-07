import os
import glob
import subprocess

def is_testcase_dir(path):
    pwd = os.getcwd()

    os.chdir(path)
    files = glob.glob('*')

    for req in ['setup', 'test', 'cleanup']:
        if not req in files and not req+'.bat' in files:
            return False

    return True

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
    proc = subprocess.Popen([script])
    proc.wait()

    return (proc.returncode == 0)

def has_bat_ext(path):
    if os.path.exists(path+'setup.bat'):
        return True
    else:
        return False
        
def write_test_summary(tc):
    pass
    
class TestSuite:
    def __init__(self, tests=[]):
        self.testcases = []
        self.build_testsuite(tests)
        
    def build_testsuite(self, tests):
        for tc in tests:
            self.testcases.append(TestCase(path))

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

        if has_bat_ext(path):
            self.setup = './setup.bat'
            self.test = './test.bat'
            self.cleanup = './cleanup.bat'
        else:
            self.setup = 'setup'
            self.test = 'test'
            self.cleanup = 'cleanup'
            
    def pass_test(self):
        self.status = True

    def fail_test(self, message):
        self.status = False
        self.message = message
        
    def get_status(self):
        return self.status

    def run_test(self, strict):
        pwd = os.getcwd()

        os.chdir(self.path)
        if not run_script(self.setup):
            self.fail_test('Abnormal exit from \'setup\'')
        elif not run_script(self.test):
            self.fail_test('The \'test\' script inidicated a failure')
        elif not run_script(self.cleanup) and strict:
            self.fail_test('Abnormal exit from \'cleanup\'')
        else:
            self.pass_test()

        write_test_summary([self])
        os.chdir(pwd)
