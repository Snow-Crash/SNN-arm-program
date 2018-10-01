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

// /dev/mem file id
int fd;	



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
		while(isFIFOFull(csrPointer))
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
		while(isFIFOEmpty(csrPointer))
		{
			printf("fifo is empty, wait \n");
		}
	}

	DATATYPE data = *(readPointer);
	return data;
}
	
int main(void)
{

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
	FIFO_write_status_ptr = (unsigned int *)(h2p_lw_virtual_base);
	// From Qsys, second FIFO is 0x20
	FIFO_read_status_ptr = (unsigned int *)(h2p_lw_virtual_base + 0x20); //0x20
	
	// ===========================================

	// FIFO write addr 
	h2p_virtual_base = mmap( NULL, FIFO_SPAN, ( PROT_READ | PROT_WRITE ), MAP_SHARED, fd, FIFO_BASE); 	
	
	if( h2p_virtual_base == MAP_FAILED ) {
		printf( "ERROR: mmap3() failed...\n" );
		close( fd );
		return(1);
	}
    // Get the address that maps to the FIFO read/write ports
	FIFO_write_ptr =(unsigned int *)(h2p_virtual_base);
	FIFO_read_ptr = (unsigned int *)(h2p_virtual_base + 0x10); //0x10
	
	//============================================
	int N ;
	int data[1024] ;
	int i ;
	
	while(1) 
	{
		printf("\n\r enter N=");
		scanf("%d", &N);
		if (N>500) N = 1 ;
		if (N<1) N = 1 ;
		
		// generate a sequence
		for (i=0; i<N; i++){
			data[i] = i + 1 ;
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
	} // end while(1)
} // end main

//////////////////////////////////////////////////////////////////
/// end /////////////////////////////////////