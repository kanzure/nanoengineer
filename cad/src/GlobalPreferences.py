# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GlobalPreferences.py

Routines that test for various global user preferences.

Note: this module is likely to be imported early, and should be
considered a low level support module.  As such, importing it should
not drag in much else.  As of 2007/09/05, that's probably not true
yet.

@author: Eric Messick
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$
"""

from prefs_constants import permit_atom_chunk_coselection_prefs_key
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False

# bruce 060721; intended to become constant True for A9
def permit_atom_chunk_coselection():
    res = debug_pref("permit atom/chunk coselection?",
                     ## use Choice_boolean_True once this has no obvious bugs
                     Choice_boolean_False,
                     non_debug = True,
                     prefs_key = permit_atom_chunk_coselection_prefs_key )
    return res
