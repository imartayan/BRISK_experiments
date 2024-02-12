from util import *
import os


def build(fasta_file, **params):
    k = params["k"]
    os.makedirs(OUT_FOLDER, exist_ok=True)
    prefix = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
    hash_file = prefix + ".hash"
    run_cmd(f"cd hashmap && K={k} cargo build --release")
    return measure_time(
        f"./hashmap/target/release/hashmap build {fasta_file} -o {hash_file}", **params
    )
