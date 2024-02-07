#!/bin/bash
set -euxo pipefail

cd Brisk
mkdir -p build
cd build
cmake ..
make -j
