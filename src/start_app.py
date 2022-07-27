#!/usr/bin/env python3
import os
import re
from subprocess import run
from pprint import pprint


current_dir = os.path.dirname(os.path.abspath(__file__))

ENV_PATH = os.path.join(current_dir, 'app/')

set_env_path = 'export PYTHONPATH=${PYTHONPATH}:%s' % ENV_PATH

start_app = 'daphne examiner.asgi:application'

command = f'{set_env_path} && {start_app}'

output = (run('pytest', capture_output=True).stdout).decode('utf-8').replace('\n', '')


if not re.search('FAIL', str(output)):
    os.system(command=command)
else:
    output = ''.join(output.split('FAILED')[1:])
    pprint(f'Tests failed. App wasn`t started. {output}')
