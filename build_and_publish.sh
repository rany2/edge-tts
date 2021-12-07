#!/bin/sh

set -ex

./clean.sh

./build.sh
./publish.sh

./clean.sh

exit 0
