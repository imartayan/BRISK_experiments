from util import *
import os


def build(fasta_file, **params):
    k = params["k"]
    s = params["jellyfish_size"]
    threads = params["threads"]
    if fasta_file.endswith(".gz"):
        os.makedirs(OUT_FOLDER, exist_ok=True)
        unzipped_file = f"{OUT_FOLDER}/{get_basename(fasta_file)}"
        run_cmd(f"gzip -cd {fasta_file} > {unzipped_file}")
        fasta_file = unzipped_file
    _, mem, out, _ = measure_time_output(
        f"./jellyfish/bin/jellyfish count -m {k} -s {s} -t {threads} -C {fasta_file} --timing=/dev/stdout -o /dev/null",
        **params
    )
    t0 = float(out.splitlines()[0].split()[-1].strip())
    t1 = float(out.splitlines()[1].split()[-1].strip())
    return t0 + t1, mem
