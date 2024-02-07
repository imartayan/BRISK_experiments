#!/bin/bash
set -euxo pipefail

cd Brisk
cmake .
make -j
