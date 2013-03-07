#!/usr/bin/env python

import argparse
import sys

from flowtools.datamaps import Spread
from pandas import Series, DataFrame

parser = argparse.ArgumentParser()

parser.add_argument('-s', '--save', required=True,
        help="save combined data to file")
parser.add_argument('spreading', nargs='+',
        help="list of spreading data files to combine")

args = parser.parse_args()

left = {}
right = DataFrame()
com_left = DataFrame()
com_right = DataFrame()
dist = DataFrame()

for i, _file in enumerate(args.spreading):
    spread = Spread().read(_file)

    left[i] = Series(spread.left, index = spread.times)
    right[i] = Series(spread.right, index = spread.times)
    com_left[i] = Series(spread.com['left'], index = spread.times)
    com_right[i] = Series(spread.com['right'], index = spread.times)
    dist[i] = Series(spread.dist, index = spread.times)

left = DataFrame(left).mean
right = DataFrame(right)
com_left = DataFrame(com_left)
com_right = DataFrame(com_right)
dist = DataFrame(dist)

print(left)
