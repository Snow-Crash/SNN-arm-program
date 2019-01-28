#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 14:31:31 2019

@author: haowen
"""

from Tkinter import *
import ttk
#from ttk inport *
import new_raster_plot
import random

CANVAS_WIDTH = 800
IN_CANVAS_HEIGHT = 400
OUT_CANVAS_HEIGHT = 200
WINDOW = 100
DEMO_INTERVAL = 2000

CANVAS_BG = "white"
FRAME_BG = "#CDCDCD"

def draw_point(canvas_obj, x, y):
    '''draw a point at given x and y'''
    canvas_obj.create_oval(x-1.5, y-1.5, x+1.5, y+1.5, fill = '#011638', outline="")

def plot_raster(canvas_obj, neuron_idx_list, spike_time_list, x_interval, y_interval):
    '''
    plot spike raster, x axis represents time, y axis represents neuron idx
    canvas_obj: a canvas object
    neuron_idx_list: a list, contains neuron index
    spike_time_list: a list, contains spike time of corresponding neuron in neuron_idx_list
    x_interval: interval between two continuous time point
    y_interval: interval between two rows
    
    '''

    spike_number = len(spike_time_list)
    for i in range(spike_number):
        x = x_interval * spike_time_list[i]
        y = y_interval * neuron_idx_list[i]
        draw_point(canvas_obj, x, y)

def plot_x_axis(canvas_obj, canvas_width, canvas_height, ticks):
    '''
    plot a horizontal line and ticks
    canvas_width: width of canvas, line will be same length
    ticks: a list of ticks
    '''
    
    tick_number = len(ticks)
#    draw a horizontal line at bottom of canvas
    canvas_obj.create_line(0, 1,
                           canvas_width, 1, width = 2)
    
    #calculate interval between two ticks
    interval = canvas_width / float(tick_number-1)

#    draw ticks and calculate position
    for i in range(tick_number):
        x1 = interval*i + 2
        y1 = 0
        x2 = interval*i + 2
        y2 = 5
        
        # because in create_text function, x and y are the center of text,
        # first and last tick are not completely inside canvas, so shift them 
        if i == 0:
            x1+= 10
            x2+= 10
        elif i == tick_number-1:
            x1-=20
            x2-=20
        
#        canvas_obj.create_line(x1, y1, 
#                           x2, y2, width = 2)
        canvas_obj.create_text(x1, 10, text=ticks[i])

def plot_y_axis(canvas_obj, canvas_width, canvas_height, ticks):
    '''
    draw y axis
    '''
    tick_number = len(ticks)
    
#    draw a vertical line at bottom of canvas
    canvas_obj.create_line(canvas_width, 0,
                           canvas_width, canvas_height, width = 1)
    
    interval = canvas_height / float(tick_number-1)
    
    #draw ticks and calculate position
    for i in range(tick_number):
        y1 = interval*i + 2
        x1 = 10
        y2 = interval*i + 2
        x2 = 20
        
        if i == 0:
            y1+= 10
            y2+= 10
        elif i == tick_number-1:
            y1-=20
            y2-=20
            
        canvas_obj.create_text(10, y1, text=ticks[i])
    
def classify(*args):
    try:

        inputclass = int(sign_input.get())

        if inputclass>50:
            print 'input out of range'
        else:
            ##call C function with argument 'inputclass' and get output class (with rasterplot info)
            outputclass, in_spiketime, out_spiketime = new_raster_plot.get_output(inputclass)
            sign_output.set(outputclass)
            
            #clear all canvas
            cv_inp.delete("all")
            cv_out.delete("all")
            cv_in_x_axis.delete("all")
            cv_in_y_axis.delete("all")
            cv_out_x_axis.delete("all")
            cv_out_y_axis.delete("all")
            

            x_interval = CANVAS_WIDTH/100.0
            y_interval = IN_CANVAS_HEIGHT/128.0
            
            #plot input spike raster
            plot_raster(cv_inp,in_spiketime[0], in_spiketime[1],x_interval,y_interval)
            
            y_interval = OUT_CANVAS_HEIGHT/50.0
            #plot output spike raster
            plot_raster(cv_out,out_spiketime[0], out_spiketime[1],x_interval,y_interval)
            
            #plot ticks of input spike
            x_ticks = [0,10,20,30,40,50,60,70,80,90,100]
            plot_x_axis(cv_in_x_axis, CANVAS_WIDTH, 20, x_ticks)
            #plot ticks of output spike
            plot_x_axis(cv_out_x_axis, CANVAS_WIDTH, 20, x_ticks)
            
            #plot y axis of output spike
            out_y_ticks = [0,10,20,30,40,50]
            plot_y_axis(cv_out_y_axis, 20, OUT_CANVAS_HEIGHT, out_y_ticks)
            
            print("input class id:", inputclass)
            print("classified")

    except:

        sign_output.set("Error!")

#function to run automatically
def auto_demo():
    #first check auto_demo_mode checkbox, if it's 1, execute classify function
    if (auto_demo_mode.get()==1):
        #randomly determine a class id
        rand_class = random.randint(0,50)
        
        #set value of sign input
        sign_input.set(rand_class)
        classify()
        print("demo")
    #call its self, tkinter after only execute once, so it should always call itself
    master.after(DEMO_INTERVAL,auto_demo)
    

#main window
master = Tk()

#create a frame to contain button and textbox
frm_control = Frame(master, height = 200, width = 200, bd = 0, relief=SUNKEN,
                    background=FRAME_BG)

#set position and make the size fill from top to down
frm_control.grid(column = 0, row = 0, sticky=(N, S))

#create a label above input field
Label(frm_control, text="Input class id", background=FRAME_BG).grid(column=0, row=0, pady = 5)

#create button, button will execute classify function once clicked
Button(frm_control, text="Classify", command=classify, background=FRAME_BG).grid(column=1, row=1, padx = 10)

#variable to get input class id
sign_input = StringVar()
#variable to get output class id
sign_output = StringVar()

#create input field, input value is assigned to sign_input
input_field = Entry(frm_control, width=7, textvariable=sign_input)
input_field.grid(column=0, row=1, sticky=(W,E))

#label to display  classification result
Label(frm_control, text="Classification result:", background=FRAME_BG).grid(column=0, row=2, pady = 5)
#label displays value of sign_output
Label(frm_control, textvariable=sign_output, background=FRAME_BG).grid(column=1, row=2)

#set auto demo mode, set default value to 1
auto_demo_mode = IntVar(value=1)
#create a checkbox, assign value to auto_demo_mode
auto_demo_check = Checkbutton(frm_control, text="Auto demo", variable=auto_demo_mode,
                              background=FRAME_BG, borderwidth=0)
auto_demo_check.grid(row=3, column = 0)

#create a frame for drawing output
frm_display = Frame(master, bd = 1, relief=SUNKEN,
                    background=CANVAS_BG)
frm_display.grid(column = 1, row = 0)

#title for input canvas
ttk.Label(frm_display, text="input raster",background=CANVAS_BG).grid(column=1, row=0, pady = 5)

#create canvas to draw input raster
cv_inp = Canvas(frm_display, width = CANVAS_WIDTH, height = IN_CANVAS_HEIGHT)
cv_inp.grid(column = 1, row = 1)
cv_inp.configure(background=CANVAS_BG)

#draw x axis and ticks on cv_inp is ok, but calculating correct coordinate of point is complicated
#so create a seperate canvas
cv_in_x_axis = Canvas(frm_display, width = CANVAS_WIDTH, height = 20,bd=0)
cv_in_x_axis.grid(column = 1, row = 2)
cv_in_x_axis.configure(background=CANVAS_BG)

cv_in_y_axis = Canvas(frm_display, width = 20, height = IN_CANVAS_HEIGHT)
cv_in_y_axis.grid(column = 0, row = 1)
cv_in_y_axis.configure(background=CANVAS_BG)

#create title for output canvas
ttk.Label(frm_display, text="output raster",background=CANVAS_BG).grid(column=1, row=3, pady = 5)
#create canvas to draw output raster
cv_out = Canvas(frm_display, width = CANVAS_WIDTH, height = OUT_CANVAS_HEIGHT)
cv_out.grid(column = 1, row = 4)
cv_out.configure(background=CANVAS_BG)

#create canvas to draw x and y axis for cv_out
cv_out_x_axis = Canvas(frm_display, width = CANVAS_WIDTH, height = 20,bd=0)
cv_out_x_axis.grid(column = 1, row = 5)
cv_out_x_axis.configure(background=CANVAS_BG)

cv_out_y_axis = Canvas(frm_display, width = 20, height = OUT_CANVAS_HEIGHT)
cv_out_y_axis.grid(column = 0, row = 4)
cv_out_y_axis.configure(background=CANVAS_BG)


#execute auto_demo once
master.after(DEMO_INTERVAL, auto_demo)


master.geometry('1050x720')
mainloop()