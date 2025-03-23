#!/bin/bash
set -euxo pipefail

git submodule update --init --recursive
bash install_apt_dependencies.sh
bash install_bifrost.sh
bash install_brisk.sh
bash install_jellyfish.sh

cd kmer_count
cargo build --release
cd ..

cd hashmap
cargo +nightly build --release
cd ..

cd CBL
cargo +nightly build --release --example cbl
cd ..
