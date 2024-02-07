import runner
import os


PARAMS = {"k": 31, "prefix_bits": 28, "timeout": 300}
FOF_BUILD = "fof_build.txt"
FOF_QUERY = "fof_query.txt"
BUILD = []
QUERY = []


if __name__ == "__main__":
    if os.path.exists(FOF_BUILD):
        with open(FOF_BUILD, "r") as f:
            for line in f:
                filename = line.strip()
                if filename:
                    assert os.path.exists(filename), f"Cannot find {filename}"
                    BUILD.append(filename)
    else:
        print(f"Please write the FASTA files to build in {FOF_BUILD}")

    if os.path.exists(FOF_QUERY):
        with open(FOF_QUERY, "r") as f:
            for line in f:
                filename = line.strip()
                if filename:
                    assert os.path.exists(filename), f"Cannot find {filename}"
                    QUERY.append(filename)
    else:
        print(f"Please write the FASTA files to query in {FOF_QUERY}")

    for fasta_file in set(BUILD):
        print(f"BUILD {fasta_file}")
        runner.build(fasta_file, **PARAMS)
        runner.query_self(fasta_file, **PARAMS)

    for indexed_file, query_file in set(zip(BUILD, QUERY)):
        print(f"QUERY {indexed_file} with {query_file}")
        runner.query_other(indexed_file, query_file, **PARAMS)
        runner.insert(indexed_file, query_file, **PARAMS)
        runner.remove(indexed_file, query_file, **PARAMS)
        runner.merge(indexed_file, query_file, **PARAMS)
        runner.intersect(indexed_file, query_file, **PARAMS)
