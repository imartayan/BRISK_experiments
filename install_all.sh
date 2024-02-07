#!/bin/bash
set -euxo pipefail

git submodule update --init --recursive
bash install_apt_dependencies.sh
bash install_bifrost.sh
bash install_brisk.sh
