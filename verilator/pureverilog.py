#!/usr/bin/env python3
import os, shutil, subprocess, sys, csv

# --- config: tweak if your names/paths differ
TOP          = "dac_top_tb"  # your SV testbench top
SRCS         = ["dac_top_tb.sv", "dac_top.sv", "dac.sv"]
BUILD_DIR    = "build_tb"    # use a no-spaces dir so make is happy
CSV_NAME     = "top_dac.csv" # whatever your TB writes
VERILATOR    = shutil.which("verilator") or "/opt/homebrew/bin/verilator"

def run(cmd, **kw):
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, **kw)

def main():
    # 1) build (verilate + compile) with the TB as top
    cmd = [
        VERILATOR,
        "--binary", "-sv", "-Wall", "--trace-fst",
        "-Mdir", BUILD_DIR,
        "--top-module", TOP,
        *SRCS
    ]
    run(cmd)

    # 2) run the produced binary
    binary = os.path.join(BUILD_DIR, f"V{TOP}")
    if not os.path.exists(binary):
        print(f"error: binary not found at {binary}", file=sys.stderr)
        sys.exit(1)
    run([binary])

    # 3) fetch the CSV (written in the current working directory by your TB)
    csv_path = os.path.join(os.getcwd(), CSV_NAME)
    if not os.path.exists(csv_path):
        print(f"error: expected CSV not found at {csv_path}", file=sys.stderr)
        print("tip: confirm the filename in your TB ($fopen) and the working directory you ran from.")
        sys.exit(2)

    # show a quick preview
    print(f"\nOK: found {csv_path}\nPreview:")
    with open(csv_path, newline="") as f:
        r = csv.reader(f)
        for i, row in enumerate(r):
            print(",".join(row))
            if i >= 10:  # first ~10 lines
                break

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed (exit {e.returncode}): {' '.join(e.cmd)}", file=sys.stderr)
        sys.exit(e.returncode)