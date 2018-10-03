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
		while(FIFO_EMPTY(csrPointer))
		{
			printf("fifo is empty, wait \n");
		}
	}

	DATATYPE data = *(readPointer);
	return data;
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
		scanf("%d", &N);

		if (N == 1)
		{
			printf("Loop back mode:\n");


			printf("\n\r enter N=");
			scanf("%d", &N);
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
		else if (N == 2)
		{
			
			printf("test command decode and write back\n");
			printf("set pio 0 to pio 4 to 1-5\n");
			*pio_0_ptr = 1;
			*pio_1_ptr = 2;
			*pio_2_ptr = 3;
			*pio_3_ptr = 4;
			*pio_4_ptr = 5;

			printf("\n\r input command: 20, 21, 2, 23\n");
			scanf("%d", &N);
		
			writeFIFO(N, FIFO_write_status_ptr, FIFO_write_ptr, true);

			printf("return %d", readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true));

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