from read_data import read_densmap, read_flowmap
from save_data import save_densmap, save_flowmap
from util import construct_filename, reset_fields

def fix_maps_in_system(system, frames, save_to_folder):
    """Adjusts maps in system to correct values for given frames."""

    densmap = {}; flowmap = {};
    densmap_prev = {}; flowmap_prev = {};
    densmap_corrected = {}; flowmap_corrected = {};

    densbase_strip = system['densbase'].rsplit('/', maxsplit = 1)[-1]
    flowbase_strip = system['flowbase'].rsplit('/', maxsplit = 1)[-1]
    save_to_densbase = save_to_folder + densbase_strip
    save_to_flowbase = save_to_folder + flowbase_strip

    print("%s -> %s" % (system['densbase'], save_to_densbase))
    print("%s -> %s" % (system['flowbase'], save_to_flowbase))

    for i, frame in enumerate(frames):
        print("\rFrame %d (%d of %d) ..." % (frame, i + 1, len(frames)), 
                end = ' ')
        densmap['filename'] = construct_filename(system['densbase'], frame)
        flowmap['filename'] = construct_filename(system['flowbase'], frame)
        read_densmap(densmap, print = False)
        read_flowmap(flowmap, print = False)

        flowmap = fill_flowmap(flowmap, densmap)

        if i > 0:
            densmap_corrected = correct_densmap(densmap, densmap_prev)
            flowmap_corrected = correct_flowmap(flowmap, flowmap_prev,
                    densmap, densmap_prev, densmap_corrected)
        else:
            densmap_corrected = densmap
            flowmap_corrected = flowmap

        save_to_dens = construct_filename(save_to_densbase, frame)
        save_to_flow = construct_filename(save_to_flowbase, frame)
        save_densmap(densmap_corrected, save_to_dens)
        save_flowmap(flowmap_corrected, save_to_flow)

        densmap_prev = densmap.copy()
        flowmap_prev = flowmap.copy()

    print("Done.")

    return None

def correct_densmap(densmap, densmap_prev):
    """Corrects densmap using densmap_prev, returning in densmap_corrected."""

    densmap_corrected = {}
    reset_fields(densmap_corrected, {'X', 'Y', 'N', 'T', 'M'})

    for i in range(len(densmap['X'])):
        densmap_corrected['X'].append(densmap['X'][i])
        densmap_corrected['Y'].append(densmap['Y'][i])
        densmap_corrected['N'].append(densmap['N'][i] - densmap_prev['N'][i])
        densmap_corrected['M'].append(densmap['M'][i] - densmap_prev['M'][i])

        if densmap_corrected['N'][i] > 0.0:
            T_corrected = ( densmap['T'][i] * densmap['N'][i] - \
                    densmap_prev['T'][i] * densmap_prev['N'][i] )
            densmap_corrected['T'].append(T_corrected / \
                    densmap_corrected['N'][i])
        else:
            densmap_corrected['T'].append(0.0)

    return densmap_corrected

def correct_flowmap(flowmap, flowmap_prev, densmap, densmap_prev, 
        densmap_corrected):
    """Corrects flowmap using flowmap_prev and corresponding density maps,
    returning in flowmap_corrected."""

    flowmap_corrected = {}
    reset_fields(flowmap_corrected, {'X', 'Y', 'U', 'V'})

    for i in range(len(flowmap['X'])):
        if densmap_corrected['M'][i] > 0.0:
            flowmap_corrected['X'].append(flowmap['X'][i])
            flowmap_corrected['Y'].append(flowmap['Y'][i])

            U_corrected = (flowmap['U'][i] * densmap['M'][i] - \
                    flowmap_prev['U'][i] * densmap_prev['M'][i])
            V_corrected = (flowmap['V'][i] * densmap['M'][i] - \
                    flowmap_prev['V'][i] * densmap_prev['M'][i])

            flowmap_corrected['U'].append(U_corrected / \
                    densmap_corrected['M'][i])
            flowmap_corrected['V'].append(V_corrected / \
                    densmap_corrected['M'][i])

    return flowmap_corrected

def fill_flowmap(flowmap, densmap):
    """Fills empty cells in flowmap by comparison with densmap. Flow set to 
    zero in new cells. New map is returned."""

    fields = {'X', 'Y', 'U', 'V'}
    values = {field : 0 for field in fields}
    flowmap_filled = {}
    reset_fields(flowmap_filled, fields)

    j = 0
    for i in range(len(densmap['X'])):
        values['X'] = densmap['X'][i]
        values['Y'] = densmap['Y'][i]

        if j < len(flowmap['X']) and values['X'] == flowmap['X'][j] and \
        values['Y'] == flowmap['Y'][j]:
            values['U'] = flowmap['U'][j]
            values['V'] = flowmap['V'][j]
            j += 1
        else:
            values['U'] = 0.0
            values['V'] = 0.0
        
        for field in fields:
            flowmap_filled[field].append(values[field])

    return flowmap_filled
