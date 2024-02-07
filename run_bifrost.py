from util import *
import os

BIFROST_LIB = os.path.abspath("bifrost/build/lib")
if "LD_LIBRARY_PATH" in ENV:
    ENV["LD_LIBRARY_PATH"] = BIFROST_LIB + ":" + ENV["LD_LIBRARY_PATH"]
else:
    ENV["LD_LIBRARY_PATH"] = BIFROST_LIB


def index_path(fasta_file):
    prefix = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
    return prefix + ".gfa.gz"


def build(fasta_file, **params):
    k = params["k"]
    os.makedirs(OUT_FOLDER, exist_ok=True)
    prefix = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
    return measure_time(
        f"./bifrost/build/bin/Bifrost build -r {fasta_file} -o {prefix} -k {k} -t 1",
        **params
    )


def query(indexed_file, query_file, **params):
    prefix = f"{OUT_FOLDER}/{get_basename(indexed_file)}"
    gfa_file = prefix + ".gfa.gz"
    updated_prefix = f"{prefix}_query_{get_basename(query_file)}"
    return measure_time(
        f"./bifrost/build/bin/Bifrost query -g {gfa_file} -q {query_file} -o {updated_prefix} -t 1",
        **params
    )


def insert(indexed_file, query_file, **params):
    prefix = f"{OUT_FOLDER}/{get_basename(indexed_file)}"
    gfa_file = prefix + ".gfa.gz"
    updated_prefix = f"{prefix}_add_{get_basename(query_file)}"
    return measure_time(
        f"./bifrost/build/bin/Bifrost update -g {gfa_file} -r {query_file} -o {updated_prefix} -t 1",
        **params
    )
