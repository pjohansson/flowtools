from flowtools.datamaps import DataMap

try:
    datamap = DataMap('include/new_00160.dat')

except Exception:
    print("Could not read data map.")
    exit()

datamap.flow()
datamap.min_mass()

print(datamap.cells[:,100])


