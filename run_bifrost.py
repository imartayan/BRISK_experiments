from util import *
import os

BIFROST_LIB = os.path.abspath("bifrost/build/lib")
if "LD_LIBRARY_PATH" in ENV:
    ENV["LD_LIBRARY_PATH"] = BIFROST_LIB + ":" + ENV["LD_LIBRARY_PATH"]
else:
    ENV["LD_LIBRARY_PATH"] = BIFROST_LIB


def build(fasta_file, **params):
    k = params["k"]
    threads = params["threads"]
    os.makedirs(OUT_FOLDER, exist_ok=True)
    prefix = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
    return measure_time(
        f"./bifrost/build/bin/Bifrost build -r {fasta_file} -o {prefix} -k {k} -t {threads} -N",
        **params
    )
