# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_prefs.py - access to preferences settings affecting the dna updater

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
from debug_prefs import Choice

import env

from utilities.Log import orangemsg

from utilities import debug_flags

# ==

def initialize_prefs():
    # make debug prefs appear in debug menu
    pref_fix_deprecated_PAM3_atoms()
    pref_fix_deprecated_PAM5_atoms()
    
    pref_fix_bare_PAM3_atoms()
    pref_fix_bare_PAM5_atoms()

    _changed_debug_prefs('arbitrary value')
        # makes them appear, and also sets debug flags
        # to the current pref values
    
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
                     Choice_boolean_True, # False -> True, 080201
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
                     Choice_boolean_True, # False -> True, 080201
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_prefs )
    return res

# ==

def pref_debug_dna_updater(): # 080228
    res = debug_pref("DNA updater: debug prints",
                     Choice(["off", "on", "verbose"], defaultValue = "on"), # todo: revise after debugging
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_debug_prefs )
    return res

def pref_dna_updater_slow_asserts(): # 080228
    res = debug_pref("DNA updater: slow asserts?",
                     Choice_boolean_True, # todo: test speed effect; revise before release if too slow
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_debug_prefs )
    return res

# ==

def _changed_prefs(val):
    if val:
        msg = "Note: to use new DNA prefs value on existing atoms, " \
              "run \"DNA: rescan all atoms\" in debug->other menu."
        env.history.message(orangemsg(msg))
    return

def _changed_debug_prefs(val):
    del val
    # make sure the flags we control are defined in debug_flags
    # (i.e. that we got the right module here, and spelled them correctly)
    # (if not, this will fail the first time it runs)
    debug_flags.DEBUG_DNA_UPDATER
    debug_flags.DEBUG_DNA_UPDATER_VERBOSE
    debug_flags.DNA_UPDATER_SLOW_ASSERTS
    
    # update them all from the debug prefs

    debug_option = pref_debug_dna_updater() # "off", "on", or "verbose"
    
    debug_flags.DEBUG_DNA_UPDATER = (debug_option in ("on", "verbose",))
    debug_flags.DEBUG_DNA_UPDATER_VERBOSE = (debug_option in ("verbose",))
    
    debug_flags.DNA_UPDATER_SLOW_ASSERTS = pref_dna_updater_slow_asserts()
    
    return

# end
