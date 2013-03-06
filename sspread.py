#!/usr/bin/python

import pylab as plt
import sys

from flowtools import datamaps, spread, draw

def add_system():
    """Quick add of system."""
    return datamaps.System(
            min_mass = min_mass, floor = floor, delta_t = delta_t
            )

@draw.draw
def plot(**kwargs):
    lj = collect[2]
    quad10 = collect[0]
    quad1000 = collect[1]

    # L-J
    color = 'blue'

    plt.plot(
            lj.spread['times'], lj.spread['left'],
            color = color, label = 'lj-eps1.8', hold = True
            )
    plt.plot(
            lj.spread['times'], lj.spread['right'],
            color = color, label = '_nolegend_', hold = True
            )

    # Quad 10ps
    color = 'red'

    plt.plot(
            quad10.spread['times'], quad10.spread['left'],
            color = color, label = 'quad-q0.7, tau-10ps', hold = True
            )
    plt.plot(
            quad10.spread['times'], quad10.spread['right'],
            color = color, label = '_nolegend_', hold = True
            )

    # Quad 1000ps
    color = 'red'

    plt.plot(
            quad1000.spread['times'], quad1000.spread['left'],
            color = color, linestyle = 'dashed',
            label = 'quad-q0.7, tau-1000ps', hold = True
            )
    plt.plot(
            quad1000.spread['times'], quad1000.spread['right'],
            color = color, linestyle = 'dashed',
            label = '_nolegend_', hold = True
            )
    plt.legend()
    plt.show()

    return None
system = []

# Global parameters
min_mass = 100.
delta_t = 10

# quad_tau10
base = '/home/petter/Arbete/2013/02/quadf_w100nm/tau-t_10ps/maps/data_'
start = 100
end = 140 # 150
floor = 2
system.append(add_system())
system[-1].datamaps = datamaps.create_filenames(base, list(range(start, end+1)))

# quad_tau1000
base = '/home/petter/Arbete/2013/02/quadf_w100nm/tau-t_1000ps/02/maps/data_'
start = 90
end = 130 # 150
floor = 2
system.append(add_system())
system[-1].datamaps = datamaps.create_filenames(base, list(range(start, end+1)))

# lj_eps1.8
base = '/home/petter/Arbete/2013/02/lj_w100nm/flow/data_'
start = 140
end = 180 # 180
floor = 10
system.append(add_system())
system[-1].datamaps = datamaps.create_filenames(base, list(range(start, end+1)))

# Collect spread
collect = []
for i in system:
    collect.append(spread.Spread(i))
    collect[-1].com()
    collect[-1].times(delta_t = delta_t, relative = True)

# Print figure
title = 'Spreading of droplet on different substrates'
xlabel = 'Time from impact (ps)'
ylabel = 'Positions of edges from center of mass (nm)'
axis = 'normal'
plot(title = title, xlabel = xlabel, ylabel = ylabel, axis = axis)

