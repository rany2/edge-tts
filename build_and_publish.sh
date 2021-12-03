#!/bin/sh
set -e
rm -rf build dist src/*.egg-info
python3 setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build dist src/*.egg-info
