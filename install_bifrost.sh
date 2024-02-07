#!/bin/bash
set -euxo pipefail

cd bifrost
mkdir -p build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=.
make -j
make install
