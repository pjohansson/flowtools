#!/usr/bin/env python

from distutils.core import setup

setup(
        name="flowtools",
        description="Tools for flow maps from modified Gromacs simulations",
        long_description="See README.md",
        license='GPLv3',
        version='0.2.1',
        url="https://github.com/pjohansson/flowtools",
        author="Petter Johansson",
        author_email="petter.johansson@scilifelab.se",
        packages=['flowtools'],
        requires=[
            'numpy (>=1.7.0)',
            'matplotlib (>=1.2.0)',
            'scipy (>=0.11.0)'
            ],
        scripts=[
            'scripts/f_collect_spread.py',
            'scripts/f_combine_maps.py',
            'scripts/f_flowmaps.py',
            'scripts/f_spread_delta_t.py',
            'scripts/f_spread_plot.py'
            ]
        )
