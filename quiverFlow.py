#!/usr/bin/env python
# 
# Takes a flowmap and outputs a quiver plot.
#

from pylab import *
from sys import argv

program, flowmap_filename = argv

# Open given file
flowmap = open(flowmap_filename)

# Skip headers
line = flowmap.readline()

# Allocate arrays
X = []; Y = []; U = []; V = [];

# Until end of file, read values of X, Y, U, V
line = flowmap.readline()
while (line != ''):
    words = line.split(' ')
    X.append(float(words[0]))
    Y.append(float(words[1]))
    U.append(float(words[2]))
    V.append(float(words[3]))

    line = flowmap.readline()
flowmap.close()

figure()
quiver(X, Y, U, V)
ylim(4.0,8.5)
show()
