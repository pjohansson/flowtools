from flowtools.datamaps import DataMap

try:
    datamap = DataMap('include/flowmap_small.dat', 'flow')
except Exception:
    print("Could not read data map.")
