
import sys, os

# import plotk
from pythonrc import *
from vector import *
# a = fig(1, width=100, height=10000)

# figure(10, 10)
# b = ones(5)
# c = ones(5)
b = [1,2,3]
b = vector(b)
c = [3,6,8]
c = vector(c)
plot(b,c, '.')
# plot(b,c)
draw_now()