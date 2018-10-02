`timescale 10ns/10ns 
module fsm_tb();


reg CLOCK_50, rst_n;

reg [31:0] command_in, spike_1_in, spike_0_in;

reg command_write, spike_0_write, spike_1_write;


initial
    CLOCK_50 = 1'b0;


always
    #10 CLOCK_50 <= ~CLOCK_50;

initial
begin
    rst_n <= 1'b1;
    command_in <= 0;
    spike_0_in <= 0;
    spike_1_in <= 0;
    command_write <= 1'b0;
    spike_0_write <= 1'b0;
    spike_1_write <= 1'b0;
    #30 rst_n <= 1'b0;
    #20 rst_n <= 1'b1;
    #20 spike_0_in <= 1;
        spike_1_in <= 2;
        spike_0_write <= 1'b1;
        spike_1_write <= 1'b1;
    #20 spike_0_write <= 1'b0;
        spike_1_write <= 1'b0;
    #20 command_in <= 2;
        command_write <= 1'b1;
    #20 command_write <= 1'b0;
    #60 command_write <= 1'b1;
        command_in = 1;
    #30 command_write = 1'b0;
    #200 command_write <= 1'b0;
end


fsm uut
(
.CLOCK_50(CLOCK_50), 
.rst_n(rst_n), 
.command_in(command_in), 
.command_write(command_write), 
.spike_0_in(spike_0_in), 
.spike_1_in(spike_1_in), 
.spike_0_write(spike_0_write), 
.spike_1_write(spike_1_write)
);

endmodule

