module fsm(CLOCK_50, rst_n, command_in, command_write, spike_0_in, spike_1_in, spike_0_write, spike_1_write);

input CLOCK_50, rst_n;

input [31:0] command_in, spike_1_in, spike_0_in;
input command_write, spike_0_write, spike_1_write;

wire fpga2hps_result_write;
wire [31:0] fpga2hps_result_writedata;


reg [63:0] spike_buffer;

//=======================================================
// spike fifo read fsm
//=======================================================
reg[6:0] spike_cs, spike_ns;

// control signals
reg read_spike_fifo_0, read_spike_fifo_1, load_spike_buffer_0, load_spike_buffer_1, spike_fsm_done;
wire[31:0] spike_fifo_0_readdata, spike_fifo_1_readdata, spike_fifo_0_csr_readdata, spike_fifo_1_csr_readdata;



//=======================================================
// command state machine
//=======================================================
reg [3:0] command_cs, command_ns;
reg [31:0] command_buffer;
reg generate_start, en_spike_fsm, generate_start_done, read_command_fifo, load_command_buffer;
wire [31:0] command_fifo_readdata, command_fifo_csr_readdata;
wire command_empty;

hpsfifo	command_fifo (
	.clock ( CLOCK_50 ),
	.data ( command_in ),
	.rdreq (  read_command_fifo ),
	.wrreq ( command_write ),
	.empty ( command_empty  ),
	.full (   ),
	.q (  command_fifo_readdata )
	);


hpsfifo	spike_0_fifo (
	.clock ( CLOCK_50 ),
	.data ( spike_0_in ),
	.rdreq ( read_spike_fifo_0  ),
	.wrreq ( spike_0_write ),
	.empty (   ),
	.full (   ),
	.q (  spike_fifo_0_readdata  )
	);


hpsfifo	spike_1_fifo (
	.clock ( CLOCK_50 ),
	.data ( spike_1_in ),
	.rdreq (  read_spike_fifo_1 ),
	.wrreq ( spike_1_write ),
	.empty (   ),
	.full (   ),
	.q (  spike_fifo_1_readdata )
	);

hpsfifo	result_fifo (
	.clock ( CLOCK_50 ),
	.data ( fpga2hps_result_writedata  ),
	.rdreq (    ),
	.wrreq ( fpga2hps_result_write ),
	.empty (   ),
	.full (   ),
	.q (   )
	);



always @(posedge CLOCK_50)
begin
	if (~rst_n)
		command_cs <= 0 ;
	else
		command_cs <= command_ns;
end


always @(*)
begin
	
	read_command_fifo = 1'b0;
	load_command_buffer = 1'b0;
	generate_start = 1'b0;
	en_spike_fsm = 1'b0;
	if (command_cs == 0)
	begin
		// command fifo not empty
		if (command_empty != 1)
		begin
			command_ns = 1;
		end
		else
			command_ns = 0;
	end
	else if (command_cs == 1)
	begin
		read_command_fifo = 1'b1;
		command_ns = 2;
	end
	else if (command_cs == 2)
	begin
		
		load_command_buffer = 1'b1;
		command_ns = 4;
	end
	else if (command_cs == 4)
	begin
		// decode command
		if (command_buffer == 32'd1)
			generate_start = 1'b1;
		else if (command_buffer == 32'd2)
			en_spike_fsm = 1'b1;
	
		command_ns = 8;
	end
	else if (command_cs == 8)
	begin
	
		// wait the done signal
		if (spike_fsm_done == 1'b1)
			command_ns = 0;
		else if (generate_start_done == 1'b1)
			command_ns = 0;
		else
			command_ns = 8;
	end
	else
		command_ns = 0;
end

// command buffer
always @(posedge CLOCK_50)
begin
	if (load_command_buffer == 1'b1)
		command_buffer <= command_fifo_readdata;
	
	generate_start_done <= generate_start;
end


assign fpga2hps_result_write = generate_start_done;
assign fpga2hps_result_writedata = spike_buffer[63:32] + spike_buffer[31:0];


//=======================================================
// spike fifo read fsm
//=======================================================
always @(posedge CLOCK_50)
begin
	if (~rst_n)
		spike_cs <= 0 ;
	else
		spike_cs <= spike_ns;
end

always @(*)
begin
	
	spike_fsm_done = 1'b0;
	read_spike_fifo_0 = 1'b0;
	read_spike_fifo_1 = 1'b0;
	spike_fsm_done = 1'b0;
	
	if (spike_cs == 0)
	begin
		if (en_spike_fsm == 1'b1)
			spike_ns = 1;
		else
			spike_ns = 0;
	end
	else if (spike_cs == 1)
	begin
		spike_ns = 2;
		read_spike_fifo_0 = 1'b1;
	end
	else if (spike_cs == 2)
	begin
		spike_ns = 4;
		read_spike_fifo_1 = 1'b1;
	end
	else if (spike_cs == 4)
	// wait the data from fifo
		spike_ns = 8;
	else if ( spike_cs == 8)
	begin
		spike_ns = 0;
		spike_fsm_done = 1'b1;
	end
	else
		spike_ns = 0;

end




always @(posedge CLOCK_50)
begin
	load_spike_buffer_0 <= read_spike_fifo_0;
	load_spike_buffer_1 <= read_spike_fifo_1;
	
	if (load_spike_buffer_0 == 1'b1)
		spike_buffer[31:0] <= spike_fifo_0_readdata;
	
	if (load_spike_buffer_1 == 1'b1)
		spike_buffer[63:32] <= spike_fifo_1_readdata;
		
end

endmodule