from util import *
import os


def index_path(fasta_file):
    prefix = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
    return prefix + ".hash"


def build(fasta_file, **params):
    k = params["k"]
    os.makedirs(OUT_FOLDER, exist_ok=True)
    prefix = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
    hash_file = prefix + ".hash"
    run_cmd(f"cd hashmap && K={k} cargo +nightly build --release")
    return measure_time(
        f"./hashmap/target/release/hashmap build {fasta_file} -o {hash_file}", **params
    )


def query(indexed_file, query_file, **params):
    prefix = f"{OUT_FOLDER}/{get_basename(indexed_file)}"
    hash_file = prefix + ".hash"
    return measure_time(
        f"./hashmap/target/release/hashmap query {hash_file} {query_file}", **params
    )


def insert(indexed_file, query_file, **params):
    prefix = f"{OUT_FOLDER}/{get_basename(indexed_file)}"
    hash_file = prefix + ".hash"
    updated_file = f"{prefix}_add_{get_basename(query_file)}.hash"
    return measure_time(
        f"./hashmap/target/release/hashmap insert {hash_file} {query_file} -o {updated_file}",
        **params,
    )


def remove(indexed_file, query_file, **params):
    prefix = f"{OUT_FOLDER}/{get_basename(indexed_file)}"
    hash_file = prefix + ".hash"
    updated_file = f"{prefix}_rem_{get_basename(query_file)}.hash"
    return measure_time(
        f"./hashmap/target/release/hashmap remove {hash_file} {query_file} -o {updated_file}",
        **params,
    )
