a complete demo


raster_plot.py reads in_spike_record.txt  and output_spike_record.txt and plot raster
gui implements gui

plottk, pythonrc, vector are libraries for plotting

de1_demo is the arm executable

in_spike_record.txt is a sample input spike record, each row is a step, each column is a neuron. 1 indicates a spike
output_spike_record.txt is a sample output spike record, each row is a spike event. value before comma is neuron idx, value after comma is spike time
rates.txt is the spike rates of each class. each row corresponds to a class.