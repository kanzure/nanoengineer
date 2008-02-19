# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
GlobalPreferences.py

Routines that test for various global user preferences.

Note: this module is likely to be imported early, and should be
considered a low level support module.  As such, importing it should
not drag in much else.  As of 2007/09/05, that's probably not true
yet.

@author: Eric Messick
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from prefs_constants import permit_atom_chunk_coselection_prefs_key
from debug_prefs import debug_pref, Choice_boolean_False ##, Choice_boolean_True

def enablePyrexAtoms(): #bruce 080218
    """
    Should we try to import atombase (compiled from atombase.pyx)?
    """
    res = debug_pref("Enable pyrex atoms next time",
                     Choice_boolean_False,
                     prefs_key = True)
    return res

# bruce 060721; intended to become constant True for A9
def permit_atom_chunk_coselection():
    res = debug_pref("permit atom/chunk coselection?",
                     ## use Choice_boolean_True once this has no obvious bugs
                     Choice_boolean_False,
                     non_debug = True,
                     prefs_key = permit_atom_chunk_coselection_prefs_key )
    return res

def disable_do_not_draw_open_bonds():
    """
    Whether to disable all behavior which under some conditions
    refrains from drawing open bonds or bondpoints
    which would be drawn according to "traditional" rules
    (those in place before 2007). May also draw the affected
    objects in orange rather than their usual color.

    Can be useful for debugging, if the developer remembers it's enabled.
    """
    res = debug_pref("DNA: draw all open bonds?",
                     Choice_boolean_False,
                     prefs_key = True)
    return res

# ==

DEBUG_BAREMOTION = False #bruce 080129, for bug 2606; should be disabled for commits

DEBUG_BAREMOTION_VERBOSE = False

# end
