This folder contains the source code of arm program to demo SNN

fifo.c is a simple program test communication between fpga and arm
makefile compiles the fifo.c

DE1_SoC_Computer.v is the top level of entire fpga project, it is used in the quartus project in  ../verilog folder

cpp folder contains the source code for demo program, this is the working version

gui contains a complete working demo including gui and arm executable
advanced_gui is also a complete working demo, contain gui and arm executable. gui supports auto execute

fsm_simulate.v is a fsm. it is the same as fsm implemented in DE1_SoC_Computer.v. Put it in a individual file for modelsim simulation.
fsm_tb is corresponding testbench
