from Tkinter import *

import ttk

# from raster_plot import *
import raster_plot
# from ctypes import *


def convert(*args):
    try:

        inputclass = int(sign_input.get())

        if inputclass>50:
            print 'input out of range'
        else:
            ##call C function with argument 'inputclass' and get output class (with rasterplot info)
            # sign_output.set(round(lbs / 2.2046, 2))
            # a = cdll.LoadLibrary("/media/dataHD3/amar/sign_snn/csvs/csv_reader.so")
            # outt = a.classify(inputclass)
            outputclass = raster_plot.get_output(inputclass)
            sign_output.set(outputclass)

    except:

        sign_output.set("Error!")


root = Tk()

# Variables

sign_input = StringVar()

sign_output = StringVar()

# Create the main Frame within root

mainframe = ttk.Frame(root, padding="5 5 20 5")

mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

# Create an Entry within the main Frame

input_field = ttk.Entry(mainframe, width=7, textvariable=sign_input)

# Place at grid position 1,1 and make it fill up the entire width

input_field.grid(column=1, row=1, sticky=(W, E))

# The label that we will write the result to

ttk.Label(mainframe, textvariable=sign_output).grid(column=1, row=2)

# The convert button

ttk.Button(mainframe, text="Classify", command=convert).grid(column=2, row=3)

# The sign_input and kilogram labels. Make them stick to the left edge of the cell (W)

ttk.Label(mainframe, text="sign_input").grid(column=2, row=1, sticky=W)

ttk.Label(mainframe, text="sign_output").grid(column=2, row=2, sticky=W)

# Add padding for all elements within the mainframe

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

# focus on the sign_input field

input_field.focus()

# Bind the "Enter/Return" key to the convert action

root.bind('<Return>', convert)

# set the title

root.title("Sign Language Classification")

root.mainloop()