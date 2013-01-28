"""Tools for combining maps and frames."""

from fix_maps import fill_flowmap
from read_data import read_densmap, read_flowmap, read_datamap
from save_data import save_datamap
from util import construct_filename, parse_kwargs, reset_fields

def combine_maps_in_time(frames, **kwargs):
    """Combines a number of frames into one single. The base map name is given
    as base = path to base, the base to save to as save_to = path to new base.
    The number of frames that will be combined is given as num = number of 
    frames.
    
    If number of frames and number to combine do not even out, the end of the
    frame list will be ignored."""

    opts = {'base' : None, 'save_to' : None, 'num' : None}
    parse_kwargs(opts, kwargs)

    print("Combining datamaps of different frames.")

    # Find number of frames in final result
    num_frames_final = len(frames) // opts['num']

    # Create list of frames to combine
    frames_comb = list(range(opts['num']))

    # Allocate datamaps for all frames
    datamap = {}
    datamaps_comb = {}
    for frame in frames_comb:
        datamaps_comb[frame] = {}

    # Read file positions from first frame
    print("Finding cell positions ...", end = ' ', flush = True)
    filename_data = construct_filename(opts['base'], frames[0])
    read_datamap(datamaps_comb[0], filename = filename_data, print = None)
    fill_positions(datamap, datamaps_comb)
    print("Done.")
    
    for i in list(range(num_frames_final)):
        # Reset fields 
        reset_fields(datamap, {'N', 'T', 'M', 'U', 'V'})

        # Calculate frame number
        new_frame = int((frames[0] + 1) / opts['num']) + 1 + i

        # Frame base for reading
        frame_base = frames[0] + i * opts['num']

        # Print current frame information
        print("\rFrames %d-%d -> %d (%d of %d)."
                % (frame_base, frame_base + frames_comb[-1], new_frame,
                    i + 1, num_frames_final), end = ' ')

        # Read datamaps to combine
        for frame in frames_comb:
            frame_read = frame_base + frame
            filename_data = construct_filename(opts['base'], frame_read)
            read_datamap(datamaps_comb[frame], filename = filename_data, 
                    print = False)

        # Combine frames into datamap
        combine_mass(datamap, datamaps_comb)
        combine_flow(datamap, datamaps_comb)
        combine_num(datamap, datamaps_comb)
        combine_temp(datamap, datamaps_comb)

        # Construct filename to save in, and save
        save_to_filename = construct_filename(opts['save_to'], new_frame)
        save_datamap(datamap, save_to_filename)

    print("Done.")

    return None

def fill_positions(datamap, datamaps_comb):
    """Fills cell positions into datamap."""

    datamap['X'] = datamaps_comb[0]['X'].copy()
    datamap['Y'] = datamaps_comb[0]['Y'].copy()

    return None

def combine_temp(datamap, datamaps_comb):
    """Combines the temperatures of cells between frames."""

    cells = list(range(len(datamap['X'])))

    for i in cells:
        # Reset sums
        N_cell = 0
        T_cell = 0

        # Add upp contributions from datamaps, multiplied by number of atoms
        for frame in datamaps_comb.keys():
            N_cell += datamaps_comb[frame]['N'][i]
            T_cell += datamaps_comb[frame]['T'][i] * \
                    datamaps_comb[frame]['N'][i]

        # Average over number of atoms again
        if N_cell > 0:
            T_cell /= N_cell
        else:
            T_cell = 0.0

        # Append to datamap
        datamap['T'].append(T_cell)

    return None

def combine_num(datamap, datamaps_comb):
    """Combines the number of atoms in cells in datamaps into new."""

    cells = list(range(len(datamap['X'])))

    for i in cells:
        # Reset sum
        N_cell = 0

        # Add upp contributions from datamaps
        for frame in datamaps_comb.keys():
            N_cell += datamaps_comb[frame]['N'][i]

        # Average over frames
        N_cell /= len(datamaps_comb)

        # Append to datamap
        datamap['N'].append(int(round(N_cell)))

    return None

def combine_mass(datamap, datamaps_comb):
    """Combines the mass of cells in datamaps into new."""

    cells = list(range(len(datamap['X'])))
    
    for i in cells:
        # Reset sum
        M_cell = 0

        # Add up contributions from datamaps
        for frame in datamaps_comb.keys():
            M_cell += datamaps_comb[frame]['M'][i]

        # Average over frames
        M_cell /= len(datamaps_comb)

        # Append to datamap
        datamap['M'].append(M_cell)

    return None

def combine_flow(datamap, datamaps_comb):
    """Combines the flow of datamaps in dict datamaps into dict datamap."""

    cells = list(range(len(datamap['X'])))

    for i in cells:
        # Reset sum
        M_cell = 0
        U_cell = 0
        V_cell = 0

        # Add up contributions from datamaps
        for frame in datamaps_comb.keys():
            M_cell += datamaps_comb[frame]['M'][i]
            U_cell += datamaps_comb[frame]['M'][i] * \
                    datamaps_comb[frame]['U'][i]
            V_cell += datamaps_comb[frame]['M'][i] * \
                    datamaps_comb[frame]['V'][i]

        # Average over new mass (total for all frames)
        if M_cell > 0:
            U_cell /= M_cell
            V_cell /= M_cell
        else:
            U_cell = 0.0
            V_cell = 0.0

        # Append to datamap
        datamap['U'].append(U_cell)
        datamap['V'].append(V_cell)
    
    return None

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
