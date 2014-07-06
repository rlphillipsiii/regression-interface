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

    if is_testcase_dir(pwd):
        tests.append(pwd)

    pwd = os.getcwd()
    for item in glob.glob('*'):
        if not os.path.isdir(item):
            continue

        os.chdir(item)
        test += _find_testcases()
        os.chdir(pwd)
        
    return tests
