# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
GlobalPreferences.py

Routines that test for various global user preferences.

Note: this module is likely to be imported early, and should be
considered a low level support module.  As such, importing it should
not drag in much else.  As of 2007/09/05, that's probably not true
yet. [That goal may be impractical and not really necessary, given
the kinds of things in it so far -- bruce 080220 comment]

@author: Eric Messick
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from prefs_constants import permit_atom_chunk_coselection_prefs_key
from debug_prefs import debug_pref, Choice_boolean_False ##, Choice_boolean_True
from debug import print_compact_traceback

# ==

_pyrex_atoms_failed = False
_pyrex_atoms_succeeded = False

def usePyrexAtomsAndBonds(): #bruce 080218, revised/renamed 080220
    """
    Should we, and if so can we successfully, import the necessary symbols
    from atombase (compiled from atombase.pyx and associated files)
    for using the "Pyrex atoms" C/Pyrex code to optimize classes Atom and Bond?
    """
    global _pyrex_atoms_failed, _pyrex_atoms_succeeded
    
    if _pyrex_atoms_failed:
        return False
    if _pyrex_atoms_succeeded:
        return True
    
    res = debug_pref("Enable pyrex atoms next time",
                     Choice_boolean_False,
                     prefs_key = True)

    # uncomment the following line to temporarily override the above debug_pref,
    # e.g. to recover from trying it out and having it abort NE1 on startup
    # (hypothetical error, not known to happen):
    
    ## res = False # do not commit with this line active
    
    if res:
        # make sure it works, before telling caller to use it
        try:
            _test_atombase()
        except:
            # note: the known possible exceptions would be caught by
            # "except (ImportError, ValueError):"
            _pyrex_atoms_failed = True # don't try it again
            msg = "exception importing atombase as requested -- won't use it: "
            print_compact_traceback(msg)
            import env # import cycle??
            # note: in present implem of history [080220], this is printed too
            # early to show up in the widget, but hopefully that will be fixed
            env.history.redmsg("ERROR: unable to use experimental Pyrex Atoms and Bonds from atombase module; see console prints")
            res = False
        else:
            _pyrex_atoms_succeeded = True
            # for now, we need a can't miss note for success, as well (red, though not an error):
            print "\nNOTE: using experimental Pyrex Atoms and Bonds from atombase module\n"
            import env # import cycle??
            env.history.redmsg("NOTE: using experimental Pyrex Atoms and Bonds from atombase module")
        pass
    return res

def _test_atombase():
    import atombase # this must not be made into a toplevel import!
    from atombase import AtomBase, AtomDictBase, BondBase, BondDictBase
    return

# ==

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
