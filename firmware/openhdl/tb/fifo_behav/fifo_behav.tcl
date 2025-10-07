
# ==============================================================================
# 1. Configuration
# ==============================================================================

# Set the name of your top-level testbench
set TOP_LEVEL_TB "tb_fifo_behav"

# Set the path and name of the simulation output waveform file
set WAVEFORM_FILE "waveform.wdb"


# ==============================================================================
# 2. Get Parameters from Command Line
#
#    The first argument will be N, the second will be B.
# ==============================================================================
if { [llength $argv] < 2 } {
  puts "ERROR: Missing command line parameters for N and B."
  exit 1
}
set N [lindex $argv 0]
set B [lindex $argv 1]

puts "Running simulation with N = $N and B = $B"


# ==============================================================================
# 3. Add Sources and Enable XPMs
# ==============================================================================

# List VHDL source files with their relative paths
exec xvhdl -work xil_defaultlib ../../../ip/axis_signal_gen_v5/src/fifo/bram_simple_dp.vhd 
exec xvhdl -work xil_defaultlib ../../../ip/axis_signal_gen_v5/src/fifo/fifo.vhd 

# List SystemVerilog source files with their relative paths
exec xvlog -sv -work xil_defaultlib ../../fifo_behav.sv
exec xvlog -sv -work xil_defaultlib ../../bram_simple_dp_behav.sv
exec xvlog -sv -work xil_defaultlib ../../../hdl/fifo_xpm.sv

# Add the testbench file. The path is relative to the script's location.
exec xvlog -sv -work xil_defaultlib "./${TOP_LEVEL_TB}.sv"

# Auto-detect and enable XPMs for simulation.
auto_detect_xpm

# ==============================================================================
# 4. Elaboration
# ==============================================================================

xelab -debug typical \
      -L xil_defaultlib \
      -L unisims_ver \
      -L unimacro_ver \
      -L secureip \
      -L xpm \
      "${TOP_LEVEL_TB}" \
      -snapshot "${TOP_LEVEL_TB}_sim"

# ==============================================================================
# 5. Simulation and Waveform
# ==============================================================================

xsim "${TOP_LEVEL_TB}_sim" -tclbatch {
    # Start of a TCL batch file for xsim commands
    
    open_wave_config
    log_wave -r *
    
    # Run the simulation until completion, as defined by the testbench.
    run -all
    
    wave_close_all
    save_wave_config $WAVEFORM_FILE
    quit
}

# ==============================================================================
# 6. Review Results
# ==============================================================================

puts "Simulation finished. Waveform saved to ${WAVEFORM_FILE}"

# Launch the waveform viewer to inspect the results.
open_wave $WAVEFORM_FILE
