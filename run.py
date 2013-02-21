from flowtools.datamaps import DataMap

try:
    datamap = DataMap('include/data_00160.dat')
except Exception:
    print("Could not read data map.")

info = datamap.information()
datamap.grid(info)
print(datamap.cells[0:100,1])
print(datamap.cells.shape)
