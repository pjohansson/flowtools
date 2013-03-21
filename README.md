flowtools
=========
Scripts and modules in Python for working with data maps from simulations.

# Installation
The tools are written for Python 3.3.

## Requirements
* Python >= 3.3
* matplotlib >= 1.2.0
* numpy >= 1.7.0
* pandas >= 0.10.1
* scipy >= 0.11.0

## Instructions
    $ python setup.py install

# Tools
The suite consists of Modules for handling data and Scripts for running them.

## Modules
* draw - a decorator for creating figures
* datamaps - classes for handling and drawing data maps

## Scripts
* f_collect_spread - collect the spread of a droplet on a substrate
* f_spread_plot - averages and draws spread data with error
* f_flowmaps - draws flow fields of maps

### Legacy
* f_combine_maps - combines old type data maps to new type
* f_spread_delta_t - add time to old type spread maps

# Data format
The data that these tools work on come from a specific output format from my
Gromacs simulations of droplets on substrates.

## Frames
Data from simulations is formatted into frames, each frame representing a
data map collected at a certain time. Frames are spaced equidistant in time.

## Maps
Maps are output from a system having it's domain decomposed into a two
dimensional grid of cells. Cells are of equal size and contain information
about their center position along the system axes, as well as accumulated mass,
number of atoms, temperature and flow velocity (also along the axes).

Output is done column-by-column, a header denoting the written fields and their
positions in each line.

### Output
Currently output is made in plaintext, plans exist to switch to a binary format
for efficiency reasons.

# License
The suite is licensed under the GNU General Public License v3. See LICENSE
for details.
