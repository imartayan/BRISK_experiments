from util import get_basename, get_filesize
import os
import json
import run_bifrost
import run_cbl
import run_hashmap


DATA_FOLDER = "data"
CLI = {
    "Bifrost": run_bifrost,
    "CBL": run_cbl,
    "HashMap": run_hashmap,
}
TOOLS = {
    "build": ["CBL", "HashMap", "Bifrost"],
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


def build(fasta_file, **params):
    output = build_filename("build", fasta_file, **params)
    update_data(
        output,
        file=fasta_file,
        bytes=get_filesize(fasta_file),
        k=params["k"],
        prefix_bits=params["prefix_bits"],
    )
    for tool in TOOLS["build"]:
        time, mem = CLI[tool].build(fasta_file, **params)
        update_data(output, field=tool, time=time, mem=mem)
    update_data(output, kmers=run_cbl.count(fasta_file, **params))
