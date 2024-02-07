from util import *
import os


def build(fasta_file, **params):
    k = params["k"]
    s = params["jellyfish_size"]
    threads = params["threads"]
    return measure_time(
        f"./jellyfish/bin/jellyfish count -m {k} -s {s} -t {threads} -C {fasta_file} --timing=/dev/stdout -o /dev/null",
        **params
    )
