"""Contains functions that operate on density and flow field maps."""
def readDensmap(fnDensmap):
    """Reads a density map and returns positions X, Y, number of atoms N, 
    temperature T and mass M for individual cells."""
    densmap = open(fnDensmap)
    line = densmap.readline()
    line = densmap.readline()

    while (line != ''):
        words = line.split(' ')

        X.append(float(words[0]))
        Y.append(float(words[1]))
        N.append(float(words[2]))
        T.append(float(words[3]))
        M.append(float(words[4]))

        line = densmap.readline()

    densmap.close()
