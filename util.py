"""Various utilities for density and flow map work."""

def advance_frame(system, densmap, flowmap, frame_stride = 1, **kwargs):
    """Advances the frame number by frame_stride (default is one frame)
    and updates filenames to read. Does not read new maps. Does warn if
    no files found for new frame."""

    new_frame = system['frame'] + frame_stride
    new_densfn, new_flowfn = construct_filename(system, new_frame, **kwargs)
    print(new_densfn, new_flowfn)

    return None

def parse_kwars(opts, kwargs):
    """Gives warning if an input_kwarg does not exist in avail_kwargs."""
    for arg in kwargs.keys():
        if arg in opts.keys():
            opts[arg] = kwargs[arg]

    return None

def reset_fields(data, fields_reset):
    """Resets specified fields in dictionary data."""
    
    for field in fields_reset:
        data[field] = []

    return None
