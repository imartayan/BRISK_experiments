from util import *
import os


def build(fasta_file, **params):
    k = params["k"]
    s = params["jellyfish_size"]
    threads = params["threads"]
    _, mem, out, _ = measure_time_output(
        f"./jellyfish/bin/jellyfish count -m {k} -s {s} -t {threads} -C {fasta_file} --timing=/dev/stdout -o /dev/null",
        **params
    )
    t0 = float(out.splitlines()[0].split()[-1].strip())
    t1 = float(out.splitlines()[1].split()[-1].strip())
    return t0 + t1, mem
