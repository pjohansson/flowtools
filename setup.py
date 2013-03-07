#!/usr/bin/env python

from distutils.core import setup

setup(
        name="Flowtools",
        description="Tools for flow maps from modified Gromacs simulations",
        long_description="See README.md",
        license='GPLv3',
        version='0.1.1',
        url="https://github.com/pjohansson/flowtools",
        author="Petter Johansson",
        author_email="petter.johansson@scilifelab.se",
        packages=['flowtools'],
        requires=[
            'numpy (>=1.7.0)', 'matplotlib (>=1.2.0)', 'scipy (>=0.11.0)'
            ],
        scripts=['scripts/collect_spread.py', 'scripts/combine_maps.py']
        )
