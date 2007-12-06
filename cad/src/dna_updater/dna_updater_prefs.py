# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_prefs.py - access to preferences settings affecting the dna updater

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False

import env

from utilities.Log import orangemsg

# ==

def initialize_prefs():
    # make debug prefs appear in debug menu
    pref_fix_deprecated_PAM3_atoms()
    pref_fix_deprecated_PAM5_atoms()
    
    pref_fix_bare_PAM3_atoms()
    pref_fix_bare_PAM5_atoms()
    return

# ==

def pref_fix_deprecated_PAM3_atoms():
    res = debug_pref("DNA: fix deprecated PAM3 atoms?",
                     Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_prefs )
    return res

def pref_fix_deprecated_PAM5_atoms():
    res = debug_pref("DNA: fix deprecated PAM5 atoms?",
                     Choice_boolean_False,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_prefs )
    return res

def pref_fix_bare_PAM3_atoms():
    res = debug_pref("DNA: fix bare PAM3 atoms?",
                     Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_prefs )
    return res

def pref_fix_bare_PAM5_atoms():
    res = debug_pref("DNA: fix bare PAM5 atoms?",
                     Choice_boolean_False,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_prefs )
    return res

# ==

def _changed_prefs(val):
    if val:
        msg = "Note: to use new DNA prefs value on existing atoms, " \
              "run \"DNA: rescan all atoms\" in debug->other menu."
        env.history.message(orangemsg(msg))
    return


# end
