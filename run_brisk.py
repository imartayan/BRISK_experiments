from util import *
import os


def build(fasta_file, **params):
    k = params["k"]
    m = params["m"]
    b = params["b"]
    threads = params["threads"]
    _, mem, out, _ = measure_time_output(
        f"./Brisk/counter -f {fasta_file} -k {k} -m {m} -b {b} -t {threads} --mode 1",
        **params
    )
    time = float(out.splitlines()[4].split(":")[1].strip()[:-1])
    return time, mem
