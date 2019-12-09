#!/usr/bin/python


def import_readonly():
    """Import readonly channels list from assets/ if available
    
    Returns:
        arr -- Array of readonly channels created from assets/readonly_channels.txt
    """

    try:
        file = open('assets/readonly_channels.txt', 'r')
    except:
        return []
    channels_raw = file.readlines()
    readonly_arr = []

    for c in channels_raw:
        readonly_arr.append(c.strip())

    return readonly_arr


def export_readonly(readonly_arr):
    """Export readonly channels list to assets/
    
    Arguments:
        readonly_arr {str} -- Current readonly channels list
    
    Returns:
        str -- Status output for exported list
    """

    try:
        file = open('assets/readonly_channels.txt', 'w+')
        for c in readonly_arr:
            file.write(c + '\n')
    except Exception as e:
        return 'There was some error writing to the file... {0}'.format(e)

    return 'Successfully exported Read Only channels list.'
