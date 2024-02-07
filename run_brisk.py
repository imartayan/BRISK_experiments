from util import *
import os


def build(fasta_file, **params):
    k = params["k"]
    m = params["m"]
    b = params["b"]
    threads = params["threads"]
    return measure_time(
        f"./Brisk/counter -f {fasta_file} -k {k} -m {m} -b {b} -t {threads} --mode 1",
        **params
    )
