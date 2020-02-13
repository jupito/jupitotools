#!/bin/sh
set -ex
python3 setup.py sdist bdist_wheel
pip3 install --user -U dist/jupitotools-0.0.1-py3-none-any.whl
