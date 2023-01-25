#!/bin/sh
set -ux
find src examples -name '*.py' | xargs pylint
find src examples -name '*.py' | xargs mypy
