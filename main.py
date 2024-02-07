import runner
import os


PARAMS = {"k": 31, "m": 21, "b": 13, "prefix_bits": 28, "jellyfish_size": "10M", "threads": 1, "timeout": 300}
FOF_BUILD = "fof_build.txt"
BUILD = []


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

    for fasta_file in set(BUILD):
        print(f"BUILD {fasta_file}")
        runner.build(fasta_file, **PARAMS)
