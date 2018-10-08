# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 11:53:12 2018

@author: hw
"""

import subprocess

class raster_plot():
    
    def __init__(self, width, hight):
        '''
        width is length of a window, hight is numeber of neuron/input
        '''
        self.plot_mat = [x[:] for x in [[0] * width] * hight]
    
    def set_pixel(self, row, col):
        '''
        set the given position element value to 1
        '''
        self.plot_mat[row][col] = 1
    
    def read_input_spike_file(self, file_path):
        '''
        format of input spike file:
        each row is a tick
        each column corresponds to a input axon
        '''
        lines = None
        mat = []
        with open(file_path) as f:
            lines = f.read().splitlines()
        for line in lines:
            mat.append(list(line))
        
        for tick in range(len(mat)):
            for neuron_idx in range(len(mat[tick])):
                if (mat[tick][neuron_idx] == '1'):
                    self.set_pixel(neuron_idx, tick)
        
        
        
    def read_output_spike_file(self, file_path):
        '''
        format of output spike file
        each row is a spike event,
        value before comma is spike neuron
        value after comma is the time
        '''
        with open(file_path) as f:
            lines = f.read().splitlines()
            
        for line in lines:
            splited_line = line.split(',')
            neuron_idx = int(splited_line[0])
            tick = int(splited_line[1])
            self.set_pixel(neuron_idx, tick)
    
    def plot_raster(self, pixel_symbol_off = '.', pixel_symbol_on = '▌'):
        '''
        pixel_symbol_off is shown when the element in plt_mat is 0
         pixel_symbol_on is shown when the element in plt_mat is 1
        '''
        outstr = ''
        for row in range(len(self.plot_mat)):
            for col in range(len(self.plot_mat[row])):
                if (self.plot_mat[row][col] == 0):
                    outstr = outstr + pixel_symbol_off
                else:
                    outstr = outstr + pixel_symbol_on
            outstr = outstr + '\n'
        return outstr


# call demo program
        
# specify arguments
demofile = "./de1_demo"
classidx_int = 1
noise_float = 0.1

classidx = "-class=" + str(classidx_int)
noise = "-noise=" + str(noise_float)

arglist = [demofile, classidx, noise]


#ret = subprocess.call(["./de1_demo", "-class=1"])



inp = raster_plot(100, 128)
inp.read_input_spike_file('D:/de1/test/fifo_test_simplified/arm-program/cpp/input_spike_record.txt')
inpplot = inp.plot_raster()

outp = raster_plot(100, 50)
outp.read_output_spike_file('D:/de1/test/fifo_test_simplified/arm-program/cpp/output_spike_record.txt')
outplot = outp.plot_raster()

print(outplot)

#mat = []
#line = None
#with open('D:/de1/test/fifo_test_simplified/arm-program/cpp/output_spike_record.txt') as f:
#    lines = f.read().splitlines()
#
#for line in lines:
#    mat.append(list(line))
