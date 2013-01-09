#!/usr/bin/env python2
# 
# Takes a flowmap and outputs a quiver plot.
#

from pylab import *
from sys import argv
from mpl_toolkits.mplot3d import Axes3D

def readDensmap(X, Y, N, T, M, fnDensmap):
    densmap = open(fnDensmap)
    line = densmap.readline()
    line = densmap.readline()

    while (line != ''):
        words = line.split(' ')

        X.append(float(words[0]))
        Y.append(float(words[1]))
        N.append(float(words[2]))
        T.append(float(words[3]))
        M.append(float(words[4]))

        line = densmap.readline()

    densmap.close()

program, fnDensmap = argv

X = []; Y = []; N = []; T = []; M = [];
readDensmap(X, Y, N, T, M, fnDensmap)
#ax = figure().gca(projection='2')
#ax.plot_trisurf(X, Y, M)
contour(X,Y,M)
show()
