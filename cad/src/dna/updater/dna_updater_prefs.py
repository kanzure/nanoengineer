# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_prefs.py - access to preferences settings affecting the dna updater

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
from utilities.debug_prefs import Choice

import foundation.env as env

from utilities.Log import orangemsg

from utilities import debug_flags

# ==

def initialize_prefs():
    """
    """
    
    # make debug prefs appear in debug menu
    pref_fix_deprecated_PAM3_atoms()
    pref_fix_deprecated_PAM5_atoms()
    
    pref_fix_bare_PAM3_atoms()
    pref_fix_bare_PAM5_atoms()

    pref_print_bond_direction_errors()
    pref_per_ladder_colors()
    pref_draw_internal_markers()

    pref_dna_updater_convert_to_PAM3plus5()
    pref_mmp_save_convert_to_PAM5()
    pref_renderers_convert_to_PAM5()
    pref_minimizers_convert_to_PAM5()

    _update_our_debug_flags('arbitrary value')
        # makes them appear in the menu,
        # and also sets their debug flags
        # to the current pref values
    
    return

# ==

def pref_fix_deprecated_PAM3_atoms():
    res = debug_pref("DNA: fix deprecated PAM3 atoms?",
                     Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_dna_updater_behavior_pref )
    return res

def pref_fix_deprecated_PAM5_atoms():
    res = debug_pref("DNA: fix deprecated PAM5 atoms?",
                     Choice_boolean_True, # False -> True, 080201
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_dna_updater_behavior_pref )
    return res

def pref_fix_bare_PAM3_atoms():
    res = debug_pref("DNA: fix bare PAM3 atoms?",
                     Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_dna_updater_behavior_pref )
    return res

def pref_fix_bare_PAM5_atoms():
    res = debug_pref("DNA: fix bare PAM5 atoms?",
                     Choice_boolean_True, # False -> True, 080201
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_dna_updater_behavior_pref )
    return res

# ==

def pref_print_bond_direction_errors():
    res = debug_pref( "DNA updater: print bond direction errors?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True,
                     )
    return res

def pref_per_ladder_colors():
    res = debug_pref("DNA: debug: per-ladder colors?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True )
    return res

def pref_draw_internal_markers():
    res = debug_pref("DNA: draw internal markers?",
                     Choice_boolean_False,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = (lambda val: env.mainwindow().glpane.gl_update()) )
    return res

# ==

# PAM3+5 prefs.  [bruce 080312]

# (These will either turn into User Prefs or per-assy settings (perhaps saved in mmp file),
#  or perhaps become finer-grained that that (applicable to portions of the model,
#  e.g. specific base pairs.)

# Note: each minimizer may need a separate pref, since support for each one differs,
# in how it works and how NE1 gets feedback from it that refers to specific atoms and bonds.

# Note: the DNA Generator model choice may also need to change somehow, for this.

def pref_dna_updater_convert_to_PAM3plus5():
    res = debug_pref("DNA: edit as PAM3+5? ",
                      Choice_boolean_False, # soon will be True and I'll remove the ending space
                      non_debug = True,
                      prefs_key = True,
                      call_with_new_value = _changed_dna_updater_behavior_pref )
    return res

def pref_mmp_save_convert_to_PAM5():
    res = debug_pref("DNA: save as PAM5? ",
                      Choice_boolean_False, # soon will be True and I'll remove the ending space
                      non_debug = True,
                      prefs_key = True )
    return res

def pref_renderers_convert_to_PAM5():
    res = debug_pref("DNA: render externally as PAM5?", # e.g. QuteMol, POV-Ray
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True )
    return res

def pref_minimizers_convert_to_PAM5():
    res = debug_pref("DNA: minimize in PAM5? ", # i.e. for ND-1 (GROMACS or not)
                      Choice_boolean_False, # soon will be True and I'll remove the ending space
                      non_debug = True,
                      prefs_key = True )
    return res

# ==

def pref_debug_dna_updater(): # 080228
    res = debug_pref("DNA updater: debug prints",
                     Choice(["off", "minimal", "on", "verbose"],
                            defaultValue = "on"), # todo: revise defaultValue after debugging
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _update_our_debug_flags )
    return res

def pref_dna_updater_slow_asserts(): # 080228
    res = debug_pref("DNA updater: slow asserts?",
                     Choice_boolean_True, # todo: test speed effect; revise before release if too slow
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _update_our_debug_flags )
    return res

# ==

def _changed_dna_updater_behavior_pref(val):
    if val:
        msg = "Note: to apply new DNA prefs value to existing atoms, " \
              "run \"DNA: rescan all atoms\" in debug->other menu."
        env.history.message(orangemsg(msg))
    return

def _changed_dna_updater_behavior_pref_2(val): # rename! but, not currently used.
    _changed_dna_updater_behavior_pref( True) # always print the message

def _update_our_debug_flags(val):
    del val
    # make sure the flags we control are defined in debug_flags
    # (i.e. that we got the right module here, and spelled them correctly)
    # (if not, this will fail the first time it runs)
    debug_flags.DEBUG_DNA_UPDATER
    debug_flags.DEBUG_DNA_UPDATER_VERBOSE
    debug_flags.DNA_UPDATER_SLOW_ASSERTS
    debug_flags.DEBUG_DNA_UPDATER_MINIMAL
    
    # update them all from the debug prefs

    debug_option = pref_debug_dna_updater() # "off", "minimal", "on", or "verbose"

    debug_flags.DEBUG_DNA_UPDATER_MINIMAL = (debug_option in ("minimal", "on", "verbose",))
    debug_flags.DEBUG_DNA_UPDATER         = (debug_option in            ("on", "verbose",))
    debug_flags.DEBUG_DNA_UPDATER_VERBOSE = (debug_option in                  ("verbose",))
    
    debug_flags.DNA_UPDATER_SLOW_ASSERTS = pref_dna_updater_slow_asserts()
    
    return

# end
