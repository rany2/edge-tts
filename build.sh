#!/bin/sh
set -x
exec python3 setup.py sdist bdist_wheel
