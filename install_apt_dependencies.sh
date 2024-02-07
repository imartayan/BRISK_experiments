#!/bin/bash
set -euxo pipefail

sudo apt update

sudo apt install -y python3

# bifrost
sudo apt install -y build-essential cmake zlib1g-dev

# cbl
sudo apt install -y libstdc++-12-dev libclang-dev
