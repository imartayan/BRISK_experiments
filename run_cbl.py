from util import *
import os


def index_path(fasta_file):
    prefix = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
    return prefix + ".cbl"


def build(fasta_file, **params):
    k = params["k"]
    prefix_bits = params["prefix_bits"]
    os.makedirs(OUT_FOLDER, exist_ok=True)
    prefix = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
    cbl_file = prefix + ".cbl"
    run_cmd(
        f"cd CBL && K={k} PREFIX_BITS={prefix_bits} cargo +nightly build --release --examples"
    )
    return measure_time(
        f"./CBL/target/release/examples/cbl build {fasta_file} -o {cbl_file}",
        **params
    )


def count(indexed_file, **params):
    prefix = f"{OUT_FOLDER}/{get_basename(indexed_file)}"
    cbl_file = prefix + ".cbl"
    out, _ = run_cmd(
        f"./CBL/target/release/examples/cbl count {cbl_file} 2>&1 | tail -n 1 | cut -d ' ' -f 3",
        **params
    )
    return int(out)


def count_query(indexed_file, query_file, **params):
    prefix = f"{OUT_FOLDER}/{get_basename(indexed_file)}"
    cbl_file = prefix + ".cbl"
    out, _ = run_cmd(
        f"./CBL/target/release/examples/cbl query {cbl_file} {query_file} 2>&1 | tail -n 2 | head -n 1 | cut -d ' ' -f 3",
        **params
    )
    return int(out)
