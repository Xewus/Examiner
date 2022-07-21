#!/usr/bin/env python3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

ENV_PATH = os.path.join(current_dir, 'app/')

set_env_path = 'export PYTHONPATH=${PYTHONPATH}:%s' % ENV_PATH

start_app = 'daphne examiner.asgi:application'

command = f'{set_env_path} && {start_app}'

os.system(command=command)
