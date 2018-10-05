///////////////////////////////////////
// FIFO test
// 256 32-bit words read and write
// compile with
// gcc FIFO_2.c -o fifo2  -O3
///////////////////////////////////////
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/ipc.h> 
#include <sys/shm.h> 
#include <sys/mman.h>
#include <sys/time.h> 
#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include "ARM_A9_HPS.h"
#include "hwlib.h"
#include "socal/socal.h"
#include "socal/hps.h"
#include "socal/alt_gpio.h"


#define bufSize 1024
#define WINDOW 100
#define INPUT_NUMBER 150
#define NEURON_NUMBER 50
#define TEST_CASE_NUMBER 1350

// main bus; FIFO write address
#define FIFO_BASE            0xC0000000
#define FIFO_SPAN            0x00001000
// the read and write ports for the FIFOs
// you need to query the status ports before these operations
// PUSH the write FIFO
// POP the read FIFO

/// lw_bus; FIFO status address
#define HW_REGS_BASE          0xff200000
#define HW_REGS_SPAN          0x00005000 
// WAIT looks nicer than just braces
// FIFO status registers
// base address is current fifo fill-level
// base+1 address is status: 
// --bit0 signals "full"
// --bit1 signals "empty"

#define DATATYPE unsigned int

#define FIFO_EMPTY(a) ((*(a+1))& 2 )
#define FIFO_FULL(a) ((*(a+1))& 1 )

#define FIFO_ISTATUS(a) ((*(a+1))& 3 )

bool isFIFOFull(volatile unsigned int *csrPointer)
{
	// csr address: fill level
	// csr address + 1: i_status
	// 				  : bit 0 == 1 if full
	//				  : bit 1 == 1 if empty
	//
	bool full = false;
	if ((*(csrPointer+1) & 1) == 1)
		full = true;
	
	return full;
}

bool isFIFOEmpty(volatile unsigned int *csrPointer)
{
	bool empty = false;
	if ((*(csrPointer+1) & 2) == 1)
		empty = true;

	return empty;
}

unsigned int getFIFOLevel(volatile unsigned int *csrPointer)
{
	return *csrPointer;
}

void writeFIFO(DATATYPE data, volatile unsigned int *csrPointer, volatile DATATYPE *writePointer, bool block)
{
	if (block == true)
	{
		while(FIFO_FULL(csrPointer))
		{
			printf("fifo is full, wait \n");
		}
	}

	(*(writePointer)) = data;
}


DATATYPE readFIFO(volatile unsigned int *csrPointer, volatile DATATYPE *readPointer, bool block)
{
	if (block == true)
	{
		
		if (FIFO_EMPTY(csrPointer))
		{
			int counter = 0;
			printf("fifo is empty, wait \n");
			while(FIFO_EMPTY(csrPointer))
			{
				counter++;
				if (counter > 500)
					{
						printf("time out, read failed\n");
						return 0;
					}
			}
		}

	}

	DATATYPE data = *(readPointer);
	return data;
}

// set a bit to 1
void setBit(unsigned int* val, int index)
{
	*val |= 1UL << index;
}


void readFile(char* filename, int spike_array[WINDOW][INPUT_NUMBER])
{
	FILE *fp;
	char str[1000];
	//char* filename = "D:/de1/csvread/layer_2_class_0_sample_1.csv";


	fp = fopen(filename, "r");
	if (fp == NULL){
		printf("Could not open file %s", filename);
		return;
	}

	int row = 0;
	while (fgets(str, 1000, fp) != NULL)
	{

		int col = 0;
		int idx = 0;

		while (str[idx] != '\0')
		{
			if (str[idx] == '1')
				spike_array[row][col] = 1;
			if (str[idx] == '1' || str[idx] == '0')
				col++;
			idx++;
		}
		row++;
	}
}

void readRateFile(char* filename, float rate_array[TEST_CASE_NUMBER][INPUT_NUMBER])
{
	FILE *fp;
	//char str[1000];
	//char* filename = "D:/de1/csvread/layer_2_class_0_sample_1.csv";

	//char char_spike_array[INPUT_NUMBER] = { "0" };

	fp = fopen(filename, "r");
	if (fp == NULL){
		printf("Could not open file %s", filename);
		return;
	}

	int i = 0;
	int j = 0;
	float rate;
	for (i = 0; i < TEST_CASE_NUMBER; i++)
	{
		for (j = 0; j < INPUT_NUMBER; j++)
		{
			fscanf(fp, "%f", &rate);
			//printf("%.15f ", rate);
			rate_array[i][j] = rate;
		}
		printf("\n");
	}
}


void generateSpikeArray(int test_case_idx, float rate_array[TEST_CASE_NUMBER][INPUT_NUMBER], int spike_array[INPUT_NUMBER])
{
	float x = (float)rand() / (float)(RAND_MAX);
	int idx = 0;
	for (idx = 0; idx != INPUT_NUMBER; idx++)
	{
		if (x < rate_array[test_case_idx][idx])
			spike_array[idx] = 1;
	}
}
	
int main(void)
{
	// the light weight buss base
	void *h2p_lw_virtual_base;
	// HPS_to_FPGA FIFO status address = 0
	volatile unsigned int * FIFO_write_status_ptr = NULL ;
	volatile unsigned int * FIFO_read_status_ptr = NULL ;

	// HPS_to_FPGA FIFO write address
	// main bus addess 0x0000_0000
	void *h2p_virtual_base;
	volatile unsigned int * FIFO_write_ptr = NULL ;
	volatile unsigned int * FIFO_read_ptr = NULL ;

	// volatile unsigned int * spike_FIFO_0_write_pointer = NULL;
	// volatile unsigned int * spike_FIFO_1_write_pointer = NULL;
	// volatile unsigned int * command_FIFO_write_pointer = NULL;
	// volatile unsigned int * result_FIFO_read_pointer = NULL;

	// volatile unsigned int * spike_FIFO_0_write_status_pointer = NULL;
	// volatile unsigned int * spike_FIFO_1_write_status_pointer = NULL;
	// volatile unsigned int * command_FIFO_write_status_pointer = NULL;
	// volatile unsigned int * result_FIFO_read_status_pointer = NULL;

	volatile unsigned int * pio_0_ptr = NULL;
	volatile unsigned int * pio_1_ptr = NULL;
	volatile unsigned int * pio_2_ptr = NULL;
	volatile unsigned int * pio_3_ptr = NULL;
	volatile unsigned int * pio_4_ptr = NULL;

	// /dev/mem file id
	int fd;	

	// Declare volatile pointers to I/O registers (volatile 	
	// means that IO load and store instructions will be used 	
	// to access these pointer locations, 
	// instead of regular memory loads and stores)  
  
	// === get FPGA addresses ==================
    // Open /dev/mem
	if( ( fd = open( "/dev/mem", ( O_RDWR | O_SYNC ) ) ) == -1 ) 	{
		printf( "ERROR: could not open \"/dev/mem\"...\n" );
		return( 1 );
	}
    
	//============================================
    // get virtual addr that maps to physical
	// for light weight bus
	// FIFO status registers
	h2p_lw_virtual_base = mmap( NULL, HW_REGS_SPAN, ( PROT_READ | PROT_WRITE ), MAP_SHARED, fd, HW_REGS_BASE );	
	if( h2p_lw_virtual_base == MAP_FAILED ) {
		printf( "ERROR: mmap1() failed...\n" );
		close( fd );
		return(1);
	}
	// the two status registers
	FIFO_write_status_ptr = (unsigned int *)(h2p_lw_virtual_base + FIFO_HPS_TO_FPGA_IN_CSR_BASE);
	// From Qsys, second FIFO is 0x20
	FIFO_read_status_ptr = (unsigned int *)(h2p_lw_virtual_base + FIFO_FPGA_TO_HPS_OUT_CSR_BASE); //0x20
	
	// ===========================================

	// FIFO write addr 
	h2p_virtual_base = mmap( NULL, FIFO_SPAN, ( PROT_READ | PROT_WRITE ), MAP_SHARED, fd, FIFO_BASE); 	
	
	if( h2p_virtual_base == MAP_FAILED ) {
		printf( "ERROR: mmap3() failed...\n" );
		close( fd );
		return(1);
	}
    // Get the address that maps to the FIFO read/write ports
	FIFO_write_ptr =(unsigned int *)(h2p_virtual_base + FIFO_HPS_TO_FPGA_IN_BASE);
	FIFO_read_ptr = (unsigned int *)(h2p_virtual_base +FIFO_FPGA_TO_HPS_OUT_BASE); //0x10

	// spike_FIFO_0_write_pointer = (unsigned int *)(h2p_virtual_base + FIFO_HPS_TO_FPGA_0_IN_BASE);
	// spike_FIFO_1_write_pointer = (unsigned int *)(h2p_virtual_base + FIFO_HPS_TO_FPGA_1_IN_BASE);
	// command_FIFO_write_pointer = (unsigned int *)(h2p_virtual_base + FIFO_INSTRUCITON_IN_BASE);   
	// result_FIFO_read_pointer = (unsigned int *)(h2p_virtual_base + FIFO_FPGA2HPS_RESULT_OUT_BASE);

	// spike_FIFO_0_write_status_pointer = (unsigned int *)(h2p_lw_virtual_base + FIFO_HPS_TO_FPGA_0_IN_CSR_BASE);
	// spike_FIFO_1_write_status_pointer = (unsigned int *)(h2p_lw_virtual_base + FIFO_HPS_TO_FPGA_1_IN_CSR_BASE);
	// command_FIFO_write_status_pointer = (unsigned int *)(h2p_lw_virtual_base + FIFO_INSTRUCITON_IN_CSR_BASE);
	// result_FIFO_read_status_pointer = (unsigned int *)(h2p_lw_virtual_base + FIFO_FPGA2HPS_RESULT_OUT_CSR_BASE);
	

	pio_0_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_0_BASE);
	pio_1_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_1_BASE);
	pio_2_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_2_BASE);
	pio_3_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_3_BASE);
	pio_4_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_4_BASE);

	//============================================
	int N ;
	int data[1024] ;
	int i ;
	
	while(1) 
	{

		printf("select mode(1: loop back, 2: fsm test): \n");
		printf("1: loop back \n");
		printf("2: fsm test \n");
		scanf("%d", &N);


		// control
		// 0 - 65535: loop back, fpga returns the input value
		// 65536: generate a statr signal, return 0 and 0xff000000
		// 65537: return value of pio 0
		// 65538: return value of pio 1
		// 65539: return value of pio 2
		// 65540: retuen value of pio 3

		if (N == 1)
		{

			while(1)
			{

				printf("Loop back mode:\n");
				printf("88888: quit \n");
				printf("\n\r enter N=");
				scanf("%d", &N);

				if (N == 88888)
					break;

				if (N>500) N = 1 ;
				if (N<1) N = 1 ;
				
				// generate a sequence
				for (i=0; i<N; i++){
					data[i] = i + 1;
				}
				
				// print fill levels
				printf("=====================\n\r");
				printf("fill levels before interleaved write\n\r");
				printf("write=%d read=%d\n\r", getFIFOLevel(FIFO_write_status_ptr), getFIFOLevel(FIFO_read_status_ptr));
				
				
				// ====================================
				// send array to FIFO and read every time
				// ====================================
				for (i=0; i<N; i++){
					// wait for a slot then
					// do the actual FIFO write
					writeFIFO(data[i], FIFO_write_status_ptr, FIFO_write_ptr, true);
					// now read it back
					while (!FIFO_EMPTY(FIFO_read_status_ptr)) {
					//while(!isFIFOEmpty(FIFO_read_status_ptr)){
						printf("return=%d %d %d\n\r", readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true), getFIFOLevel(FIFO_write_status_ptr), getFIFOLevel(FIFO_read_status_ptr)) ; 
					}	
				}
				if(!FIFO_EMPTY(FIFO_read_status_ptr)) printf("delayed last read\n\r");
				// and one last read because
				// for this example occasionally there is one left on the loopback

				while (!FIFO_EMPTY(FIFO_read_status_ptr)) {
					printf("return=%d %d %d\n\r", readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true), getFIFOLevel(FIFO_write_status_ptr), getFIFOLevel(FIFO_read_status_ptr)) ;
				}
				
				// finish timing the transfer
				
				// ======================================
				// send array to FIFO and read entire block
				// ======================================
				// print fill levels
				printf("=====================\n\r");
				printf("fill levels before block write\n\r");
				printf("write=%d read=%d\n\r", getFIFOLevel(FIFO_write_status_ptr), getFIFOLevel(FIFO_read_status_ptr));
				
				// send array to FIFO and read block
				for (i=0; i<N; i++){
					// wait for a slot
					writeFIFO(data[i], FIFO_write_status_ptr, FIFO_write_ptr, true);
				}
				
				printf("fill levels before block read\n\r");
				printf("write=%d read=%d\n\r", getFIFOLevel(FIFO_write_status_ptr), getFIFOLevel(FIFO_read_status_ptr));
				
				// get array from FIFO while there is data in the FIFO
				while (!FIFO_EMPTY(FIFO_read_status_ptr)) {
					// print array from FIFO read port
					printf("return=%d %d %d\n\r", readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true), getFIFOLevel(FIFO_write_status_ptr), getFIFOLevel(FIFO_read_status_ptr)) ; 
				}
				
				// FIFO fill levels
				printf("fill levels after block read\n\r");
				printf("write=%d read=%d\n\r", getFIFOLevel(FIFO_write_status_ptr), getFIFOLevel(FIFO_read_status_ptr));
				printf("=====================\n\r");

			}

		}
		else if (N == 2)
		{


			while(1)
			{
				printf("input command: \n");
				printf("<65536: loop back \n");
				printf("65536: switch hex 1 and  test start signal generation and spike write back \n");
				printf("65537: switch hex 2 and return pio_0 \n");
				printf("65538: switch hex 3 and return pio_1 \n");
				printf("65539: switch hex 4 and return pio_2 \n");
				printf("65540: switch hex 5 and return pio_3 \n");
				printf("88888: quit\n");

				scanf("%d", &N);

				if (N == 88888)
					break;
				
				printf("test command decode and write back\n");
				printf("pio 0 : 1 \n");
				printf("pio 1 : 2 \n");
				printf("pio 2 : 3 \n");
				printf("pio 3 : 4 \n");
				printf("pio 4 : 5 \n");
				*pio_0_ptr = 1;
				*pio_1_ptr = 2;
				*pio_2_ptr = 3;
				*pio_3_ptr = 4;
				*pio_4_ptr = 5;

				printf("send %d \n", N);
			
				writeFIFO(N, FIFO_write_status_ptr, FIFO_write_ptr, true);

				usleep(1000);

				while (!FIFO_EMPTY(FIFO_read_status_ptr))
				{
					int unsigned return_value =  readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true);
					printf("return HEX: %x, DEC: %d\n", return_value, return_value);
				}
					
			}


		}
		else if (N == 3)
		{
			// creata an array to store spikes in current window, initialized as 0
			int spike_array[WINDOW][INPUT_NUMBER];
			int neuron_spike_count[NEURON_NUMBER] = {0};
			memset(spike_array, 0, sizeof(spike_array[0][0]) * WINDOW * INPUT_NUMBER);
			//  index 0 corresponds to 0th axon, 1 corresponds to 1st neuron.


			// read file
			char* filename = "D:/de1/csvread/layer_2_class_0_sample_1.csv";
			readFile(filename, spike_array);


			unsigned int pio_0_value = 0;
			unsigned int pio_1_value = 0;
			unsigned int pio_2_value = 0;
			unsigned int pio_3_value = 0;
			unsigned int pio_4_value = 0;

			// loop 100 ticks
			int row  = 0;
			for (row = 0 ; i != WINDOW; i++)
			{
				// convert binary to unsigned values
				int col = 0;
				for (col = 0; col != INPUT_NUMBER; col++)
				{

					if (spike_array[row][col] == 1)
					{
						if (col< 32)
						// set pio 0
						{
							setBit(&pio_0_value, col);
						}
						else if (col > 31 && col < 64)
						// set pio 2
						{
							setBit(&pio_1_value, col-32);
						}
						else if (col > 63 && col < 96)
						// set pio 3
						{
							setBit(&pio_2_value, col-64);
						}
						else if (col > 95 && col < 128)
						// set pio 4
						{
							setBit(&pio_3_value, col-96);
						}
						else if(col > 127)
						// set pio 5
						{
							setBit(&pio_4_value, col-128);
						}
					}
				}

				// set arm output
				*pio_0_ptr = pio_0_value;
				*pio_1_ptr = pio_1_value;
				*pio_2_ptr = pio_2_value;
				*pio_3_ptr = pio_3_value;
				*pio_4_ptr = pio_4_value;
				
				// wait a while
				usleep(100);

				// send command, 0x10000 generate a start signal
				writeFIFO(0x10000, FIFO_write_status_ptr, FIFO_write_ptr, true);

				// wait 100 ms
				usleep(1000*100);

				// read fifo until its empty
				while (!FIFO_EMPTY(FIFO_read_status_ptr)) 
				{
					unsigned int result = readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true);
					unsigned int neuron_index = result & 0xff;
					neuron_spike_count[neuron_index]++;
				}	

			}


			// pio4, pio3, pio2, pio1, pio0		
		}
		else if (N == 4)
		{
	
			// a tabe to store the spike number of each neuron
			int neuron_spike_count[NEURON_NUMBER] = {0};

			// rate of each input
			float rate_mat[TEST_CASE_NUMBER][INPUT_NUMBER];

			memset(rate_mat, 0, sizeof(rate_mat[0][0]) * TEST_CASE_NUMBER * INPUT_NUMBER);

			char* filename = "D:/de1/test/fifo_test_simplified/arm-program/rates.txt";

			readRateFile(filename, rate_mat);

			//select a test case
			int test_case_idx = 1;

			// loop 100 ticks
			int i = 0;

			for (i = 0; i != WINDOW; i++)
			{
				int spike_array[INPUT_NUMBER] = {0};

				// generate spikes
				 generateSpikeArray(test_case_idx, rate_mat, spike_array);

				// initialize pio values to 0
				unsigned int pio_0_value = 0;
				unsigned int pio_1_value = 0;
				unsigned int pio_2_value = 0;
				unsigned int pio_3_value = 0;
				unsigned int pio_4_value = 0;

				// set each bit of pio

				int axon_id = 0;

				for (axon_id = 0; axon_id != INPUT_NUMBER; axon_id++)
				{
					if (spike_array[axon_id] == 1)
					{
						if (axon_id< 32)
						// set pio 0
						{
							setBit(&pio_0_value, axon_id);
						}
						else if (axon_id > 31 && axon_id < 64)
						// set pio 2
						{
							setBit(&pio_1_value, axon_id-32);
						}
						else if (axon_id > 63 && axon_id < 96)
						// set pio 3
						{
							setBit(&pio_2_value, axon_id-64);
						}
						else if (axon_id > 95 && axon_id < 128)
						// set pio 4
						{
							setBit(&pio_3_value, axon_id-96);
						}
					}
				}

				// set pio value
				*pio_0_ptr = pio_0_value;
				*pio_1_ptr = pio_1_value;
				*pio_2_ptr = pio_2_value;
				*pio_3_ptr = pio_3_value;
				*pio_4_ptr = pio_4_value;

				// wait a while
				usleep(100);

				// send command, 0x10000 generate a start signal
				writeFIFO(0x10000, FIFO_write_status_ptr, FIFO_write_ptr, true);

				// wait 100 ms
				usleep(1000*100);
			}

			// after loop 100 times, read fifo until its empty
				while (!FIFO_EMPTY(FIFO_read_status_ptr)) 
				{
					unsigned int result = readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true);
					unsigned int neuron_index = result & 0xff;
					neuron_spike_count[neuron_index]++;
				}	


		}


		// printf("test state machines\n");
		
		// // usleep( 100*1000 );

		// // write data to spike fifo 0 and fifo 1
		// printf("write 1 word to spike fifo 0 and spike fifo 1 \n");

		// printf("before write \n");
		// printf("spike fifo 0 level: %d, spike fifo 1 level %d \n",  getFIFOLevel(spike_FIFO_0_write_status_pointer), getFIFOLevel(spike_FIFO_1_write_status_pointer));
		// printf("spike fifo 0 csr: %d, spike fifo 1 csr %d \n", FIFO_ISTATUS(spike_FIFO_0_write_status_pointer), FIFO_ISTATUS(spike_FIFO_0_write_status_pointer));

		// writeFIFO(1, spike_FIFO_0_write_status_pointer, spike_FIFO_0_write_pointer, true);
		// writeFIFO(2, spike_FIFO_1_write_status_pointer, spike_FIFO_1_write_pointer, true);

		// printf("after write \n");
		// printf("spike fifo 0 level: %d, spike fifo 1 level %d \n",  getFIFOLevel(spike_FIFO_0_write_status_pointer), getFIFOLevel(spike_FIFO_1_write_status_pointer));
		// printf("spike fifo 0 csr: %d, spike fifo 1 csr %d \n", FIFO_ISTATUS(spike_FIFO_0_write_status_pointer), FIFO_ISTATUS(spike_FIFO_0_write_status_pointer));

		// // test command state machine
		// // commands:
		// //			1: generate spike 
		// //			2: enable spike buffer fsm

		// printf("write command 2(enable spike buffer fsm) to command fifo \n");
		// printf("before write command to command fifo\n");
		// printf("command fifo level: %d , result fifo level: %d \n", getFIFOLevel(command_FIFO_write_status_pointer), getFIFOLevel(result_FIFO_read_status_pointer));
		// printf("command fifo csr: %d , result fifo csr %d \n ", FIFO_ISTATUS(command_FIFO_write_status_pointer), FIFO_ISTATUS(result_FIFO_read_status_pointer));
		
		// // usleep(100);
		// printf("write command 2 to command fifo \n");
		// // write command 2 to command buffer to enable spike buffer fsm
		// writeFIFO(2, command_FIFO_write_status_pointer, command_FIFO_write_pointer, true);

		// // usleep(100);

		// printf("after write command 2 to commanf fifo\n");
		// printf("command fifo level: %d , result fifo level: %d \n", getFIFOLevel(command_FIFO_write_status_pointer), getFIFOLevel(result_FIFO_read_status_pointer));
		// printf("command fifo csr: %d , result fifo csr %d \n ", FIFO_ISTATUS(command_FIFO_write_status_pointer), FIFO_ISTATUS(result_FIFO_read_status_pointer));
		// printf("spike fifo 0 csr: %d , spike fifo 1 csr %d \n ", FIFO_ISTATUS(spike_FIFO_0_write_status_pointer), FIFO_ISTATUS(spike_FIFO_1_write_status_pointer));
		// printf("spike fifo 0 level: %d, spike fifo 1 level %d \n",  getFIFOLevel(spike_FIFO_0_write_status_pointer), getFIFOLevel(spike_FIFO_1_write_status_pointer));

		// //unsigned int result;
		// //result = *result_FIFO_read_pointer;

		// //result =  readFIFO(result_FIFO_read_status_pointer, result_FIFO_read_pointer, true);


		// // printf("result is: %d\n", result);

		// // printf("after read result from result fifo\n");
		// // printf("command fifo level: %d , result fifo level: %d \n", getFIFOLevel(command_FIFO_write_status_pointer), getFIFOLevel(result_FIFO_read_status_pointer));
		// // printf("command fifo csr: %d , result fifo csr %d \n ", FIFO_ISTATUS(command_FIFO_write_status_pointer), FIFO_ISTATUS(result_FIFO_read_status_pointer));

		// printf("set pio 0 to 1\n");
		// *pio_0_ptr = 1;
		// printf("set pio 1 to 2\n");
		// *pio_1_ptr = 2;

		// usleep(100);

		// printf("write to hps2fpga fifo 1\n");

		// writeFIFO(15, FIFO_write_status_ptr, FIFO_write_ptr, true);

		// usleep(100);

		// printf("return=%d %d %d\n\r", readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true), getFIFOLevel(FIFO_write_status_ptr), getFIFOLevel(FIFO_read_status_ptr)) ;

	} // end while(1)
} // end main

//////////////////////////////////////////////////////////////////
/// end /////////////////////////////////////