from fix_maps import fill_flowmap
from read_data import read_densmap, read_flowmap
from save_data import save_datamap
from util import construct_filename

def combine_maps_in_system(system, frames, save_to_base):
    """Combines density and flow maps in a system for input frames, saving
    to input base."""

    densmap = {}; flowmap = {};

    print("Combining density and flow maps:")
    print("%s + %s -> %s" % (system['densbase'], system['flowbase'], 
        save_to_base))

    for i, frame in enumerate(frames):
        print("\rFrame %d (%d of %d) ..." % (frame, i + 1, len(frames)), 
                end = ' ', flush = True)

        densmap['filename'] = construct_filename(system['densbase'], frame)
        flowmap['filename'] = construct_filename(system['flowbase'], frame)
        read_densmap(densmap, print = False)
        read_flowmap(flowmap, print = False)

        combined_map = combine_maps(densmap, flowmap)

        save_to_filename = construct_filename(save_to_base, frame)
        save_datamap(combined_map, save_to_filename)

    print("Done.")

    return

def combine_maps(densmap, flowmap):
    """Combines a density and a flow map into a new data map type, 
    which is returned."""

    flowmap = fill_flowmap(flowmap, densmap)

    combined_map = {}
    fields = {'X', 'Y', 'N', 'T', 'M', 'U', 'V'}

    for field in fields:
        if field in densmap.keys():
            combined_map[field] = densmap[field].copy()
        elif field in flowmap.keys():
            combined_map[field] = flowmap[field].copy()

    return combined_map
