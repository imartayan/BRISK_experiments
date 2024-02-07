import subprocess
import struct
import sys
import os


GNU_TIME = "/usr/bin/time"
ENV = os.environ.copy()
OUT_FOLDER = "out"


def run_cmd(command, **params):
    timeout = params["timeout"] if "timeout" in params else None
    sys.stderr.write("> " + command + "\n")
    try:
        proc = subprocess.run(
            command,
            shell=True,
            check=True,
            timeout=timeout,
            capture_output=True,
            text=True,
            env=ENV,
        )
        out, err = proc.stdout, proc.stderr
        if out is not None:
            sys.stdout.write(out + "\n")
        if err is not None:
            sys.stderr.write(err + "\n")
        return out, err
    except subprocess.SubprocessError as proc:
        out, err = proc.stdout, proc.stderr
        if isinstance(out, bytes):
            out = out.decode("utf-8")
        if isinstance(out, str):
            sys.stdout.write(out + "\n")
        if isinstance(err, bytes):
            err = err.decode("utf-8")
        if isinstance(err, str):
            sys.stderr.write(err + "\n")
        return None, None


def measure_time(command, **params):
    """
    Measure time (in s) and memory usage (in KB) of a command
    """
    _, err = run_cmd(f"{GNU_TIME} -f '%U %M' {command}", **params)
    try:
        time_s, mem_kb = err.splitlines()[-1].split()
        return float(time_s), int(mem_kb)
    except Exception:
        return float("inf"), float("inf")


def get_basename(filename):
    basename = os.path.basename(filename)
    if basename.endswith(".gz"):
        return basename[:-3]
    return basename


def get_filesize(filename):
    if filename.endswith(".gz"):
        with open(filename, "rb") as f:
            f.seek(-4, 2)
            return struct.unpack("I", f.read(4))[0]
    else:
        return os.path.getsize(filename)
