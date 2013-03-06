from distutils.core import setup

setup(
        name='Flowtools',
        description="Tools for flow maps from modified Gromacs simulations",
        author="Petter Johansson",
        author_email="petter.johansson@scilifelab.se",
        packages=['flowtools'],
        requires=['numpy', 'pylab', 'scipy'],
        scripts=['scripts/collect_spread']
        )
