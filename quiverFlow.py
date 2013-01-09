#!/usr/bin/env python2
# 
# Takes a flowmap and outputs a quiver plot.
#

from pylab import *
from sys import argv

program, fnFlowmap = argv

flowmap = open(fnFlowmap)

# Skip headers
line = flowmap.readline()

# Allocate arrays
X = []; Y = []; U = []; V = [];

# Until end of file, read values of X, Y, U, V
line = flowmap.readline()
while (line != ''):
    # Split line into words of values
    words = line.split(' ')

    # Append current values to array
    X.append(float(words[0]))
    Y.append(float(words[1]))
    U.append(float(words[2]))
    V.append(float(words[3]))

    # Read next line
    line = flowmap.readline()

flowmap.close()

figure()
quiver(X, Y, U, V, color='blue')
ylim(4.0, 8.5)
show()
