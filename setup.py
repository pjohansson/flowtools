#!/usr/bin/env python

from distutils.core import setup

setup(
        name='Flowtools',
        description="Tools for flow maps from modified Gromacs simulations",
        version='0.1',
        author="Petter Johansson",
        author_email="petter.johansson@scilifelab.se",
        packages=['flowtools'],
        requires=['numpy', 'pylab', 'scipy'],
        scripts=['scripts/collect_spread.py']
        )
