#!/bin/sh
set -eux
rm -rf build dist src/*.egg-info
python3 setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/* --verbose
