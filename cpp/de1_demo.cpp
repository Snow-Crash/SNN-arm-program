///////////////////////////////////////
// FIFO test
// 256 32-bit words read and write
// compile with
// gcc FIFO_2.c -o fifo2  -O3
///////////////////////////////////////
#pragma GCC diagnostic ignored "-Wpointer-arith"
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
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <random>


#define bufSize 1024
#define WINDOW 100
#define INPUT_NUMBER 128
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

using namespace std;

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


void read_rate_file(string filepath, vector<vector<float> >& rates)
{
	ifstream data(filepath);
	string line;
	vector<vector<string> > tempmat;
	while (getline(data, line))
	{

		stringstream lineStream(line);
		string cell;
		vector<string> parsedline;
		while (getline(lineStream, cell, ' '))
			parsedline.push_back(cell);
		tempmat.push_back(parsedline);
	}

	// convert string to float
	//vector<vector<float> > rates;
	for (unsigned int i = 0; i != tempmat.size(); i++)
	{
		vector<float> temprate;
		for (unsigned int j = 0; j != tempmat[i].size(); j++)
		{
			//string::size_type sz;
			float rate = stof(tempmat[i][j]);
			temprate.push_back(rate);
		}
		rates.push_back(temprate);
	}
}

void read_rate_file_line(string filepath, int line_number, vector<float>& rates)
{
	ifstream data(filepath);
	string line;
	vector<string> temprate;
	int linecount = 0;
	while (getline(data, line))
	{
		if (linecount == line_number)
		{
			stringstream lineStream(line);
			string cell;
			//vector<string> parsedline;
			while (getline(lineStream, cell, ' '))
				temprate.push_back(cell);
			//tempmat.push_back(parsedline);
		}
		linecount++;
	}

	for (unsigned int i = 0; i != temprate.size(); i++)
	{

		float rate = stof(temprate[i]);
		rates.push_back(rate);
	}
}

void generate_Spike_Array( vector<float>& rate_array, vector<int> & spike_array)
{
	int idx = 0;
	for (idx = 0; idx != INPUT_NUMBER; idx++)
	{
		float x = (float)rand() / (float)(RAND_MAX);
		if (x < rate_array[idx])
			spike_array[idx] = 1;
	}
}

void plot_input_raster(vector<vector<int> >& input_spike_record)
{
	//vector<string> raster;
	ostringstream buffer; 
	for (unsigned int neuron_idx = 0; neuron_idx != INPUT_NUMBER; neuron_idx++)
	{
		
		for (unsigned tick = 0; tick != WINDOW; tick++)
		{
			if (input_spike_record[tick][neuron_idx] == 1)
				buffer << "|";
			else
				buffer << " ";
		}

		buffer << "\n";
	}

	cout << buffer.str() << "\n";

}

void plot_output_raster(vector<int>& spike_time, vector<int>& spike_neuron_idx)
{
	vector<vector<int> > raster;
	for (int i = 0; i != NEURON_NUMBER; i++)
	{
		vector<int> vec(WINDOW, 0);
		raster.push_back(vec);
	}

	for (unsigned int line = 0; line != spike_time.size(); line++)
	{
		int neuron_idx = spike_neuron_idx[line];
		int neuron_spike_time = spike_time[line];
		raster[neuron_idx][neuron_spike_time] = 1;
	}

	ostringstream buffer;
	for (unsigned int neuron_idx = 0; neuron_idx != raster.size(); neuron_idx++)
	{
		buffer << neuron_idx ;
		for (unsigned int tick = 0; tick != raster[neuron_idx].size(); tick++)
			if (raster[neuron_idx][tick] == 1)
				buffer << "|";
			else
				buffer << ".";
		
		buffer << "\n";
	}

	cout << buffer.str() << "\n";
}

int get_result(vector<int>& neuron_spike_count)
{
	int max = 0;
	int result_idx = 0;
	for (int idx = 0; idx != NEURON_NUMBER; idx++)
	{
		if (neuron_spike_count[idx] > max)
		{
			max = neuron_spike_count[idx];
			result_idx = idx;
		}
	}

	return result_idx;
}

void print_result(vector<int>& neuron_spike_count)
{
	// find the neuron which fires most frequently

	printf("\nspike statistic: \n");
	printf("neuron: ");


	// print 0-24 neuron
	for (int idx = 0; idx != 25; idx++)
	{
		printf("%2d ", idx);
	}

	printf("\n");

	for (int idx = 0; idx != 25; idx++)
	{
		printf("---");
	}

	printf("--------");

	printf("\ncount:  ");

	for (int idx = 0; idx != 25; idx++)
	{
		printf("%2d ", neuron_spike_count[idx]);
	}

	// print 25-49 neuorn
	printf("\n========");
	for (int idx = 0; idx != 25; idx++)
	{
		printf("===");
	}

	printf("\nneuron: ");
	for (int idx = 25; idx !=50; idx++)
	{
		printf("%2d ", idx);
	}

	printf("\n");

	for (int idx = 25; idx != 50; idx++)
	{
		printf("---");
	}
	printf("--------");
	printf("\ncount:  ");

	for (int idx = 25; idx != 50; idx++)
	{
		
		printf("%2d ", neuron_spike_count[idx]);
	}

	int result_idx = get_result(neuron_spike_count);
	printf("\nclassification result: %d\n", result_idx);

}


void doInference(int window_size, vector<float>& rate_array, vector<int>& neuron_spike_count,
vector<int>& spike_neuron_idx, vector<int>& spike_time, vector<vector<int>>& input_spike_record, bool record, bool print_info)
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
		return;
	}
    
	//============================================
    // get virtual addr that maps to physical
	// for light weight bus
	// FIFO status registers
	h2p_lw_virtual_base = mmap( NULL, HW_REGS_SPAN, ( PROT_READ | PROT_WRITE ), MAP_SHARED, fd, HW_REGS_BASE );	
	if( h2p_lw_virtual_base == MAP_FAILED ) {
		printf( "ERROR: mmap1() failed...\n" );
		close( fd );
		return;
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
		return;
	}
    // Get the address that maps to the FIFO read/write ports
	FIFO_write_ptr =(unsigned int *)(h2p_virtual_base + FIFO_HPS_TO_FPGA_IN_BASE);
	FIFO_read_ptr = (unsigned int *)(h2p_virtual_base +FIFO_FPGA_TO_HPS_OUT_BASE); //0x10

	pio_0_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_0_BASE);
	pio_1_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_1_BASE);
	pio_2_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_2_BASE);
	pio_3_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_3_BASE);
	pio_4_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_4_BASE);


	int tick = 0;

	for (int i = 0; i != window_size; i++)
	{

		vector<int> spike_array(INPUT_NUMBER, 0);
		generate_Spike_Array(rate_array, spike_array);

		if (record == true)
			input_spike_record.push_back(spike_array);

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

		if (print_info == true)
		{
			printf("tick %d , input spike array: \n", i);
			int j = 0;
			for(j = 0; j != NEURON_NUMBER; j++)
			{
				printf("%d", spike_array[j]);
				
			}
			printf("\n");
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

		// wait 10 ms
		usleep(1000);

		// after loop 100 times, read fifo until its empty

		if (print_info == true)
		{
			printf("neruons spiked in current tick: \n");
		}

		while (!FIFO_EMPTY(FIFO_read_status_ptr)) 
		{
			unsigned int result = readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true);
			if (result != 0xff000000)
			{
				if ((result & 0xfe000000) == 0xfe000000)
				{
					unsigned int neuron_index = result & 0x000000ff;
					neuron_spike_count[neuron_index]++;

					if (print_info == true)
					{
						printf(" %d ", neuron_index);
					}


					if (record == true)
					{
						spike_neuron_idx.push_back(neuron_index);
						spike_time.push_back(tick);
					}
				}
			}
			usleep(50);
		}

		if (print_info == true)
		{
			printf("\n");
		}

		tick++;
	}





	// write to txt file
	// ofstream myfile;
	// myfile.open ("input_spike.txt");
	// for (unsigned int i = 0; i != input_spike_record.size(); i++)
	// {
	// 	for(int j = 0; j != spike_array_record[i]; j++)
	// 		myfile << input_spike_record[i][j];
	// 	myfile <<"\n";
	// }
	// myfile.close();


	// if( munmap( h2p_virtual_base, HW_REGS_SPAN ) != 0 ) {
	// 	printf( "ERROR: munmap() failed...\n" );
	// 	close( fd );
	// 	return;
	// }

	close( fd );

}

float RandomFloat(float lower, float upper) 
{
    float random = ((float) rand()) / (float) RAND_MAX;
    float diff = upper - lower;
    float r = random * diff;
    return lower + r;
}

void doInferenceWrapper(int class_index, float noise_level, vector<int>& spike_neuron_idx, vector<int>& spike_time, 
vector<vector<int> >& input_spike_record, int& classification_result, bool print_info)
{

	if (print_info == true)
		printf("input class: %d\n", class_index);
	
	// a tabe to store the spike number of each neuron
	vector<int> neuron_spike_count(NEURON_NUMBER, 0);

	// rate of each input

	string filename = "./rates.txt";
	vector<vector<float> > rate_mat;
	read_rate_file(filename, rate_mat);

	//select a test case
	int rate_line_number = 3*class_index + rand() % 3;

	default_random_engine generator;

	normal_distribution<> dist(0, noise_level);

	vector<float> input_with_noise = rate_mat[rate_line_number];
	if (noise_level != 0)
	{
		for (unsigned int idx = 0; idx != input_with_noise.size(); idx++)
		{
			float noise_amplitude = RandomFloat(0, noise_level);
			
			//prinft("noise_amplitude %f", noise_amplitude);

			if ((rand() % 2) == 0)
				noise_amplitude = 0 - noise_amplitude;

				
			//input_with_noise[idx] = input_with_noise[idx] * (1+noise_amplitude);


			float number = dist(generator);
			//printf("%f  ", number);
			input_with_noise[idx] = input_with_noise[idx] + number;		
		}

	}

	//generate_Spike_Array(rate_mat[rate_line_number], spike_array);

	// vector<int> spike_neuron_idx;
	// vector<int> spike_time;
	// vector<vector<int> > input_spike_record;

	doInference(100, input_with_noise, neuron_spike_count, spike_neuron_idx,
	spike_time, input_spike_record, true, print_info);

	// write to txt file
	ofstream myfile;
	myfile.open ("output_spike_record.txt");
	for (unsigned int i = 0; i != spike_neuron_idx.size(); i++)
	{
		myfile << spike_neuron_idx[i] << "," << spike_time[i] << "\n";
	}
	myfile.close();

	ofstream myfile2;
	myfile2.open ("input_spike_record.txt");
	for (unsigned int i = 0; i != input_spike_record.size(); i++)
	{
		for (int j = 0; j != INPUT_NUMBER; j++)
		{
			myfile2 << input_spike_record[i][j];
		}
			
		myfile2 << "\n";
	}
	myfile2.close();

	classification_result = get_result(neuron_spike_count);

	if (print_info == true)
	{

		print_result(neuron_spike_count);

		printf("\n\ninput spike raster:\n");
		plot_input_raster(input_spike_record);


		printf("\noutput spike raster:\n");
		plot_output_raster(spike_time, spike_neuron_idx);

	}

}

int fsmTest()
{
	// the light weight buss base
	void *h2p_lw_virtual_base;
	volatile unsigned int * FIFO_write_status_ptr = NULL ;
	volatile unsigned int * FIFO_read_status_ptr = NULL ;

	// HPS_to_FPGA FIFO write address
	void *h2p_virtual_base;
	volatile unsigned int * FIFO_write_ptr = NULL ;
	volatile unsigned int * FIFO_read_ptr = NULL ;

	volatile unsigned int * pio_0_ptr = NULL;
	volatile unsigned int * pio_1_ptr = NULL;
	volatile unsigned int * pio_2_ptr = NULL;
	volatile unsigned int * pio_3_ptr = NULL;
	volatile unsigned int * pio_4_ptr = NULL;

	// /dev/mem file id
	int fd;	
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

	pio_0_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_0_BASE);
	pio_1_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_1_BASE);
	pio_2_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_2_BASE);
	pio_3_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_3_BASE);
	pio_4_ptr = (unsigned int *)(h2p_lw_virtual_base + PIO_4_BASE);
	

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

		int N;

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

		usleep(100);

		while (!FIFO_EMPTY(FIFO_read_status_ptr))
		{
			int unsigned return_value =  readFIFO(FIFO_read_status_ptr, FIFO_read_ptr, true);
			printf("return HEX: %x, DEC: %d\n", return_value, return_value);
		}
	}


	close( fd );

	return 0;
}


int loopBack()
{
	// the light weight buss base
	void *h2p_lw_virtual_base;
	volatile unsigned int * FIFO_write_status_ptr = NULL ;
	volatile unsigned int * FIFO_read_status_ptr = NULL ;

	// HPS_to_FPGA FIFO write address
	void *h2p_virtual_base;
	volatile unsigned int * FIFO_write_ptr = NULL ;
	volatile unsigned int * FIFO_read_ptr = NULL ;

	// /dev/mem file id
	int fd;	
  
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

	//============================================
	int N ;
	int data[1024] ;
	int i ;

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

	close( fd );

	return 0;
}


void demoEvaluate()
{
	int input_num;
	printf("input numeber of input:");
	scanf("%d", &input_num);

	float error_count = 0;

	float noise_level = 0.09;
	// printf("input noise:");
	// scanf("%f", &noise_level);

	int print_info = 0;
	// printf("print info?:");
	// scanf("%f", &print_info);

	for (int i = 0; i != input_num; i++)
	{	
		int input_class_index = rand() % 50;

		vector<int> spike_neuron_idx;
		vector<int> spike_time;
		vector<vector<int> > input_spike_record;

		int classification_result = -1;

		doInferenceWrapper(input_class_index, noise_level, spike_neuron_idx, spike_time, input_spike_record, classification_result, print_info);
		
		cout << "input class: " << input_class_index << ", classification result: " << classification_result << ", ";

		if (input_class_index != classification_result)
			error_count++;
		
		cout << "acc: " << ((float)(i+1 - error_count)) / (float)(i+1) << " \n";

		usleep(100);
	}
	
}

	
int main(int argc, char *argv[])
{

	srand (time(NULL));

	vector<string> argvec;
	int class_index = 0;
	int input_number = 0;
	float noise = 0;

	// parse command line
	for (int i = 1; i != argc; i++)
	{
		const char* arg = argv[i];
		string argstr(arg);
		//argvec.push_back(argstr);
		if (argstr.find("-class") != std::string::npos) 
		{
			std::size_t pos = 0;
			pos = argstr.find("=");
			string valuestr = argstr.substr(pos+1, argstr.length()-1);
			class_index = stoi(valuestr);
		}
		else if (argstr.find("-number") != std::string::npos)
		{
			std::size_t pos = 0;
			pos = argstr.find("=");
			string valuestr = argstr.substr(pos+1, argstr.length()-1);
			input_number = stoi(valuestr);
		}
		else if (argstr.find("-noise") != std::string::npos)
		{
			std::size_t pos = 0;
			pos = argstr.find("=");
			string valuestr = argstr.substr(pos+1, argstr.length()-1);
			noise = stof(valuestr);
		}
	}

	if (argc == 1)
	{
		int N ;
		
		while(1) 
		{	
			printf("\n");
			printf("select mode(1: loop back, 2: fsm test): \n");
			printf("1: loop back \n");
			printf("2: fsm test \n");
			printf("3: single input demo \n");
			printf("4: multiple input demo \n");
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

				loopBack();

			}
			else if (N == 2)
			{
				
				fsmTest();
			}
			else if (N == 3)
			{
				int input_class_index;

				printf("select class id: \n");

				scanf("%d", &input_class_index);

				// printf("input noise level: \n");
				float noise_level = 0.09;
				//scanf("%f", &noise_level);

				vector<int> spike_neuron_idx;
				vector<int> spike_time;
				vector<vector<int> > input_spike_record;

				int classification_result = -1;

				doInferenceWrapper(input_class_index, noise_level, spike_neuron_idx, spike_time, input_spike_record, classification_result, true);

				cout << "input class: " << input_class_index << ", classification result: " << classification_result << "\n";

			}

			else if (N == 4)
			{
				demoEvaluate();
			}
		}
	}
	else
	{
		vector<int> spike_neuron_idx;
		vector<int> spike_time;
		vector<vector<int> > input_spike_record;
		int classification_result = -1;
		doInferenceWrapper(class_index, noise, spike_neuron_idx, spike_time, input_spike_record, classification_result, false);

		cout << "input class: " << class_index << ", classification result: " << classification_result << "\n";
	}



} // end main

//////////////////////////////////////////////////////////////////
/// end /////////////////////////////////////