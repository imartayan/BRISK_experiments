from util import get_basename, get_filesize, run_cmd
import os
import json
import run_bifrost
import run_brisk
import run_cbl
import run_hashmap
import run_jellyfish


DATA_FOLDER = "data"
CLI = {
    "Bifrost": run_bifrost,
    "Brisk": run_brisk,
    "CBL": run_cbl,
    "HashMap": run_hashmap,
    "Jellyfish": run_jellyfish,
}
TOOLS = {
    "build": ["Brisk", "Jellyfish", "HashMap", "CBL"],
}


def update_data(json_file, field=None, **kwargs):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            data = json.load(f)
        if field:
            if field in data:
                data[field] |= kwargs
            else:
                data[field] = kwargs
        else:
            data |= kwargs
        with open(json_file, "w") as f:
            json.dump(data, f)
    else:
        if field:
            data = {field: kwargs}
        else:
            data = kwargs
        with open(json_file, "w+") as f:
            json.dump(data, f)


def build_filename(prefix, fasta_file, **params):
    k = params["k"]
    m = params["m"]
    basename = get_basename(fasta_file)
    size = get_filesize(fasta_file)
    return f"{DATA_FOLDER}/{prefix}_{k}_{m}_{size}_{basename}.json"


def build(fasta_file, **params):
    output = build_filename("build", fasta_file, **params)
    run_cmd(f"cd kmer_count && K={params['k']} cargo build --release")
    out, _ = run_cmd(f"./kmer_count/target/release/kmer_count {fasta_file}")
    update_data(
        output,
        file=fasta_file,
        bytes=get_filesize(fasta_file),
        k=params["k"],
        m=params["m"],
        b=params["b"],
        prefix_bits=params["prefix_bits"],
        kmers=int(out),
    )
    for tool in TOOLS["build"]:
        time, mem = CLI[tool].build(fasta_file, **params)
        if time and mem:
            update_data(output, field=tool, time=time, mem=mem)
