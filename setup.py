import argparse
import sys
import subprocess
import os.path

parser = argparse.ArgumentParser(description='Set up a provisioned environment',
                                 add_help=True)
parser.add_argument('--test-dir', required=True, help='The directory containing the performance test')
args = parser.parse_args(sys.argv[1:])

test_dir = args.test_dir
if not os.path.isdir(test_dir):
    sys.exit(f'exiting because "{test_dir}" is not a valid directory.')

test_dir = os.path.abspath(test_dir)

result = subprocess.run("inventory install java",shell=True, cwd=test_dir)
print("Installed java on the test environment")
if result.returncode != 0:
    sys.exit('A failure occurred while installing java on the test environment')

result = subprocess.run("inventory install simulator",shell=True, cwd=test_dir)
print("Installed simulator on the test environment")
if result.returncode != 0:
    sys.exit('A failure occurred while installing simulator on the test environment')

print('Environment setup succeeded')
