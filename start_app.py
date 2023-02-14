#!/usr/bin/env python3
import os
import re
from subprocess import run


current_dir = os.path.dirname(os.path.abspath(__file__))

ENV_PATH = os.path.join(current_dir, 'src/')

set_env_path = 'export PYTHONPATH=${PYTHONPATH}:%s' % ENV_PATH

collect_stattic = f'python3 {ENV_PATH}/manage.py collectstatic --noinput'
start_app = 'daphne examiner.asgi:application'

start = f'{set_env_path} && {start_app}'

output = str(run(('pytest'), capture_output=True).stdout)


if not re.search('FAIL', output):
    os.system(command=collect_stattic)
    os.system(command=start)
else:
    print('Tests failed. App wasn`t started.')
