# Copyright 2008-2009 Nanorex, Inc. See LICENSE file for details.
"""
mmp_dispnames.py

@author: Bruce
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 090116 split this out of constants.py
"""

from utilities.GlobalPreferences import debug_pref_write_new_display_names
from utilities.GlobalPreferences import debug_pref_read_new_display_names

### TODO: refile these global variables:
from utilities.constants import new_dispNames, dispNames, remap_atom_dispdefs

from utilities.constants import diDEFAULT, diTUBES 
    # our use of diTUBES under that name is a KLUGE

def get_dispName_for_writemmp(display): #bruce 080324, revised 080328
    """
    Turn a display-style code integer (e.g. diDEFAULT; as stored in
    Atom.display or Chunk.display) into a display-style code string 
    as used in the current writing format for mmp files.
    """
    if debug_pref_write_new_display_names():
        return new_dispNames[display]
    return dispNames[display]

def interpret_dispName(dispname, defaultValue = diDEFAULT, atom = True): 
    """
    Turn a display-style code string (a short string constant used in mmp files
    for encoding atom and chunk display styles) into the corresponding
    display-style code integer (its index in dispNames, as extended at runtime).

    If dispname is not a valid display-style code string, return defaultValue,
    which is diDEFAULT by default.

    If atom is true (the default), only consider "atom display styles" to be
    valid; otherwise, also permit "chunk display styles".
    """
    #bruce 080324
    def _return(res):
        "(how to return res from interpret_dispName)"
        if res > diTUBES and atom and remap_atom_dispdefs.has_key(res):
            # note: the initial res > diTUBES is an optimization kluge
            return defaultValue
        return res

    try:
        res = dispNames.index(dispname)
    except ValueError:
        # not found, in first array (the one with old names, 
        # i.e. the one which gets extended)
        pass
    else:
        return _return(res)

    if debug_pref_read_new_display_names():
        try:
            res = new_dispNames.index(dispname)
        except ValueError:
            # not found, in 2nd array (the one with new names, 
            # which are aliases for old ones)
            pass
        else:
            return _return(res)

    return defaultValue # from interpret_dispName

# end
