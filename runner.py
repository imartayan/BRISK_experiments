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
    "size": ["CBL", "HashMap", "Bifrost"],
    "query_self": ["CBL", "HashMap", "Bifrost"],
    "query_other": ["CBL", "HashMap", "Bifrost"],
    "insert": ["CBL", "HashMap", "Bifrost"],
    "remove": ["CBL", "HashMap"],
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
    prefix_bits = params["prefix_bits"]
    basename = get_basename(fasta_file)
    size = get_filesize(fasta_file)
    _k = "" if k == 31 and prefix_bits == 24 else f"_{k}"
    _p = "" if prefix_bits == 24 else f"_{prefix_bits}"
    return f"{DATA_FOLDER}/{prefix}{_k}{_p}_{size}_{basename}.json"


def query_filename(prefix, indexed_file, query_file, **params):
    k = params["k"]
    prefix_bits = params["prefix_bits"]
    index_basename = get_basename(indexed_file)
    query_basename = get_basename(query_file)
    size = get_filesize(indexed_file)
    _k = "" if k == 31 and prefix_bits == 24 else f"_{k}"
    _p = "" if prefix_bits == 24 else f"_{prefix_bits}"
    return (
        f"{DATA_FOLDER}/{prefix}{_k}{_p}_{size}_{index_basename}_{query_basename}.json"
    )


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
        if tool in TOOLS["size"]:
            index_file = CLI[tool].index_path(fasta_file)
            if os.path.exists(index_file):
                update_data(output, field=tool, size=get_filesize(index_file))
    update_data(output, kmers=run_cbl.count(fasta_file, **params))


def query_self(indexed_file, **params):
    output = query_filename("query_self", indexed_file, indexed_file, **params)
    update_data(
        output,
        file=indexed_file,
        bytes=get_filesize(indexed_file),
        k=params["k"],
        prefix_bits=params["prefix_bits"],
    )
    for tool in TOOLS["query_self"]:
        if not os.path.exists(CLI[tool].index_path(indexed_file)):
            CLI[tool].build(indexed_file, **params)
        if os.path.exists(CLI[tool].index_path(indexed_file)):
            time, mem = CLI[tool].query(indexed_file, indexed_file, **params)
            update_data(output, field=tool, time=time, mem=mem)
    update_data(output, kmers=run_cbl.count(indexed_file, **params))


def query_other(indexed_file, query_file, **params):
    output = query_filename("query_other", indexed_file, query_file, **params)
    update_data(
        output,
        file=indexed_file,
        query_file=query_file,
        bytes=get_filesize(indexed_file),
        query_bytes=get_filesize(query_file),
        k=params["k"],
        prefix_bits=params["prefix_bits"],
    )
    for tool in TOOLS["query_other"]:
        if not os.path.exists(CLI[tool].index_path(indexed_file)):
            CLI[tool].build(indexed_file, **params)
        if os.path.exists(CLI[tool].index_path(indexed_file)):
            time, mem = CLI[tool].query(indexed_file, query_file, **params)
            update_data(output, field=tool, time=time, mem=mem)
    update_data(
        output,
        kmers=run_cbl.count(indexed_file, **params),
        query_kmers=run_cbl.count_query(indexed_file, query_file, **params),
    )


def insert(indexed_file, query_file, **params):
    output = query_filename("insert", indexed_file, query_file, **params)
    update_data(
        output,
        file=indexed_file,
        query_file=query_file,
        bytes=get_filesize(indexed_file),
        query_bytes=get_filesize(query_file),
        k=params["k"],
        prefix_bits=params["prefix_bits"],
    )
    for tool in TOOLS["insert"]:
        if not os.path.exists(CLI[tool].index_path(indexed_file)):
            CLI[tool].build(indexed_file, **params)
        if os.path.exists(CLI[tool].index_path(indexed_file)):
            time, mem = CLI[tool].insert(indexed_file, query_file, **params)
            update_data(output, field=tool, time=time, mem=mem)
    update_data(
        output,
        kmers=run_cbl.count(indexed_file, **params),
        query_kmers=run_cbl.count_query(indexed_file, query_file, **params),
    )


def remove(indexed_file, query_file, **params):
    output = query_filename("remove", indexed_file, query_file, **params)
    update_data(
        output,
        file=indexed_file,
        query_file=query_file,
        bytes=get_filesize(indexed_file),
        query_bytes=get_filesize(query_file),
        k=params["k"],
        prefix_bits=params["prefix_bits"],
    )
    for tool in TOOLS["remove"]:
        if not os.path.exists(CLI[tool].index_path(indexed_file)):
            CLI[tool].build(indexed_file, **params)
        if os.path.exists(CLI[tool].index_path(indexed_file)):
            time, mem = CLI[tool].remove(indexed_file, query_file, **params)
            update_data(output, field=tool, time=time, mem=mem)
    update_data(
        output,
        kmers=run_cbl.count(indexed_file, **params),
        query_kmers=run_cbl.count_query(indexed_file, query_file, **params),
    )


def merge(indexed_file, other_indexed_file, **params):
    output = query_filename("merge", indexed_file, other_indexed_file, **params)
    update_data(
        output,
        file=indexed_file,
        other_file=other_indexed_file,
        bytes=get_filesize(indexed_file),
        query_bytes=get_filesize(other_indexed_file),
        k=params["k"],
        prefix_bits=params["prefix_bits"],
    )
    for tool in TOOLS["merge"]:
        if not os.path.exists(CLI[tool].index_path(indexed_file)):
            CLI[tool].build(indexed_file, **params)
        if not os.path.exists(CLI[tool].index_path(other_indexed_file)):
            CLI[tool].build(other_indexed_file, **params)
        if os.path.exists(CLI[tool].index_path(indexed_file)) and os.path.exists(
            CLI[tool].index_path(other_indexed_file)
        ):
            time, mem = CLI[tool].merge(indexed_file, other_indexed_file, **params)
            update_data(output, field=tool, time=time, mem=mem)
    update_data(
        output,
        kmers=run_cbl.count(indexed_file, **params),
        query_kmers=run_cbl.count_query(indexed_file, other_indexed_file, **params),
    )


def intersect(indexed_file, other_indexed_file, **params):
    output = query_filename("intersect", indexed_file, other_indexed_file, **params)
    update_data(
        output,
        file=indexed_file,
        other_file=other_indexed_file,
        bytes=get_filesize(indexed_file),
        query_bytes=get_filesize(other_indexed_file),
        k=params["k"],
        prefix_bits=params["prefix_bits"],
    )
    for tool in TOOLS["intersect"]:
        if not os.path.exists(CLI[tool].index_path(indexed_file)):
            CLI[tool].build(indexed_file, **params)
        if not os.path.exists(CLI[tool].index_path(other_indexed_file)):
            CLI[tool].build(other_indexed_file, **params)
        if os.path.exists(CLI[tool].index_path(indexed_file)) and os.path.exists(
            CLI[tool].index_path(other_indexed_file)
        ):
            time, mem = CLI[tool].intersect(indexed_file, other_indexed_file, **params)
            update_data(output, field=tool, time=time, mem=mem)
    update_data(
        output,
        kmers=run_cbl.count(indexed_file, **params),
        query_kmers=run_cbl.count_query(indexed_file, other_indexed_file, **params),
    )
