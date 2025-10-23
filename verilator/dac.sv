// HMC HRL Clinic 25-26
// verilog model of DAC

// module model_DAC #(
//     // --- DAC Parameters ---
//     parameter integer DAC_W       = 16,  // Bit width of the DAC
//     parameter real    VREF        = 1.0, // Reference voltage
//     parameter time    SETTLE_TIME = 1ns, // Model for output settling time
//     parameter integer BUFFER_SIZE = 16   // Number of samples to store
// ) (
//     input  wire                  clk,
//     input  wire [DAC_W-1:0]      din,        // Digital input sample
//     output real                  aout
// );

//     real aout_next;
//     real aout_reg = 0.0;

//     real buffer_samples[BUFFER_SIZE];
//     real buffer_times[BUFFER_SIZE];
//     int  wr_ptr = 0;

//     // DAC output
//     assign aout = aout_reg;

//     // Clear buffers
//     initial begin
//         for (int i = 0; i < BUFFER_SIZE; i++) begin
//             buffer_samples[i] = 0.0;
//             buffer_times[i]   = 0.0;
//         end
//     end

//     // DAC Processing and Input Logging
//     always @(posedge clk) begin
//         // Calculate ideal DAC voltage
//         aout_next = VREF * ($signed(din) / 2.0**(DAC_W-1));

//         // Update output register after settling time
//         aout_reg <= #(SETTLE_TIME) aout_next;

//         // Record the input and get current time
//         real t_now = $realtime * 1e-9;

//         // Store the calculated value and time in the buffers
//         buffer_samples[wr_ptr] = aout_next;
//         buffer_times[wr_ptr]   = t_now;
//         wr_ptr = (wr_ptr + 1) % BUFFER_SIZE;
//     end

// endmodule

module dac(
    input  logic              clk,
    input  logic [bits-1:0]   s_axis_tdata,
    output real               aout
);
    parameter real vref = 1.0;
    parameter int bits = 16;    // DAC resolution - 16 bits

    real aout_reg;

    always_ff @(posedge clk) begin
        // Convert digital input to real and scale
        aout_reg <= vref * ($signed(s_axis_tdata)) / (2.0**(bits-1));
    end

    assign aout = aout_reg;

endmodule
