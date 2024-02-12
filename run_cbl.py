from util import *
import os


def build(fasta_file, **params):
    k = params["k"]
    prefix_bits = params["prefix_bits"]
    threads = params["threads"]
    if k > 59 or threads > 1:
        return None, None
    run_cmd(
        f"cd CBL && K={k} PREFIX_BITS={prefix_bits} cargo +nightly build --release --examples"
    )
    return measure_time(
        f"./CBL/target/release/examples/cbl build {fasta_file}",
        **params
    )
