#!/bin/bash

# configuration
MIN_B=4
MAX_B=400
MIN_N=2
MAX_N=50

TCL_SCRIPT="fifo_behav.tcl"

N=$(( RANDOM % (MAX_N - MIN_N + 1) + MIN_N ))
echo "Generated N = $N"

B=$(( RANDOM % (MAX_B - MIN_B + 1) + MIN_B ))
echo "Generated B = $B"

# run vivado in batch mode
vivado -mode batch -source "$TCL_SCRIPT" -tclargs "$N" "$B" -nolog -nojournal

# clean up generated dirs
rm -rf xsim.dir
