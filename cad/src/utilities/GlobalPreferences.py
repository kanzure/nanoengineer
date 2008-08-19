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

from utilities.prefs_constants import permit_atom_chunk_coselection_prefs_key
from utilities.debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True
from utilities.debug import print_compact_traceback

import sys

# ==

DEBUG_BAREMOTION = False #bruce 080129, for bug 2606; should be disabled for commits

DEBUG_BAREMOTION_VERBOSE = False

# ==

_pyrex_atoms_failed = False
_pyrex_atoms_succeeded = False
_pyrex_atoms_unwanted_this_session = False

def usePyrexAtomsAndBonds(): #bruce 080218, revised/renamed 080220
    """
    Should we, and if so can we successfully, import the necessary symbols
    from atombase (compiled from atombase.pyx and associated files)
    for using the "Pyrex atoms" C/Pyrex code to optimize classes Atom and Bond?
    """
    global _pyrex_atoms_failed, _pyrex_atoms_succeeded, _pyrex_atoms_unwanted_this_session

    if _pyrex_atoms_failed or _pyrex_atoms_unwanted_this_session:
        return False
    if _pyrex_atoms_succeeded:
        return True

    res = debug_pref("Enable pyrex atoms in next session?",
                     Choice_boolean_False,
                     ## non_debug = True, # revised this option and menu text (thus prefs key), bruce 080221
                         # make this ATOM_DEBUG only for release (since it's a slowdown), bruce 080408
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
            import foundation.env as env # import cycle??
            # note: in present implem of history [080220], this is printed too
            # early to show up in the widget, but hopefully that will be fixed
            env.history.redmsg("ERROR: unable to use experimental Pyrex Atoms and Bonds from atombase module; see console prints")
            res = False
        else:
            _pyrex_atoms_succeeded = True
            # for now, we need a can't miss note for success, as well (red, though not an error):
            print "\nNOTE: using experimental Pyrex Atoms and Bonds from atombase module\n"
            import foundation.env as env # import cycle??
            env.history.redmsg("NOTE: using experimental Pyrex Atoms and Bonds from atombase module")
        pass

    if not res:
        _pyrex_atoms_unwanted_this_session = True # might be because it failed

    assert _pyrex_atoms_failed or _pyrex_atoms_succeeded or _pyrex_atoms_unwanted_this_session
        # be sure we make up our mind whether to use them only once per session
        # (so debug pref change does not take effect until we rerun NE1)

    return res

def _test_atombase():
    import atombase # this must not be made into a toplevel import!
    from atombase import AtomBase, AtomDictBase, BondBase, BondDictBase
    return

def debug_pyrex_atoms():
    res = debug_pref("debug pyrex atoms?",
                     Choice_boolean_False,
                     ## non_debug = True,
                         # make ATOM_DEBUG only for release (not useful enough
                         # for non_debug), bruce 080408
                     prefs_key = True )
    return res
# ==

# bruce 060721; was intended to become constant True for A9; as of 080320 it's not planned for A10
# but might be good to try to get to afterwards

def permit_atom_chunk_coselection():
    res = debug_pref("permit atom/chunk coselection?",
                     ## use Choice_boolean_True once this has no obvious bugs
                     Choice_boolean_False,
                     ## non_debug = True,
                         # make ATOM_DEBUG only for release (since maybe unsafe,
                         # not useful since unsupported), bruce 080408
                     prefs_key = permit_atom_chunk_coselection_prefs_key )
    return res

# ==

def disable_do_not_draw_open_bonds():
    """
    Whether to disable all behavior which under some conditions
    refrains from drawing open bonds or bondpoints
    which would be drawn according to "traditional" rules
    (those in place before 2007).

    Can be useful for debugging, if the developer remembers it's enabled.
    """
    res = debug_pref("DNA: draw all open bonds?",
                         # the name starts with DNA because the special rules
                         # it turns off only affect DNA
                     Choice_boolean_False,
                     non_debug = True, #bruce 080406
                         # leave this visible w/o ATOM_DEBUG for release [bruce 080408]
                     prefs_key = True)
    return res

# ==

def _debug_pref_use_dna_updater(): #bruce 080320 moved this here from master_model_updater.py, made private
    res = debug_pref("DNA: enable dna updater?", #bruce 080317 revised text
                     Choice_boolean_True, #bruce 080317 False -> True
                     ## non_debug = True,
                         # make ATOM_DEBUG only for release (since unsafe to change (undo bugs),
                         # not useful since off is more and more unsupported), bruce 080408
                     prefs_key = "A10/DNA: enable dna updater?" #bruce 080317 changed prefs_key
                 )
    return res

def dna_updater_is_enabled(): #bruce 080320
    return _debug_pref_use_dna_updater()

# ==

def debug_pref_enable_pam_convert_sticky_ends(): #bruce 080514; remove when this feature fully works
    res = debug_pref("DNA: ghost bases when converting sticky ends to PAM5?", #bruce 080529 revised text
                     Choice_boolean_True, #bruce 080602 revised default value & prefs_key
                     non_debug = True, #bruce 080529
                     prefs_key = "v1.1/DNA: PAM3+5 make ghost bases for sticky ends?"
                    )
    return res

debug_pref_enable_pam_convert_sticky_ends()

def debug_pref_remove_ghost_bases_from_pam3(): #bruce 080602
    res = debug_pref("DNA: remove ghost bases when converting to PAM3?",
                     Choice_boolean_True, # because they mess up DNA ui ops
                     non_debug = True, # because you should keep them for more accurate repeated Minimize
                     prefs_key = "v1.1/DNA: remove ghost bases when converting to PAM3?"
                    )
    return res

debug_pref_remove_ghost_bases_from_pam3()

# ==

def debug_pref_write_bonds_compactly(): #bruce 080328
    # note: reading code for this was made active in same commit, 080328.
    # note: this could be used for non-dna single bond chains too,
    #  so the function name, preks_key, and associated abstract methods
    #  needn't contain the term "dna", though the menu text is clearer
    #  by containing it.
    res = debug_pref("mmp format: write dna bonds compactly?",
                     Choice_boolean_False,
                     # we will change this to True as soon as all developers
                     # have the necessary reading code
                     non_debug = True,
                     prefs_key = "A10/mmp format: write bonds compactly? "
                 )
    return res

def debug_pref_read_bonds_compactly(): #bruce 080328
    res = debug_pref("mmp format: read dna bonds compactly?",
                     Choice_boolean_True, # use False to simulate old reading code for testing
                     ## non_debug = True, # temporary
                         # make ATOM_DEBUG only for release (not useful enough
                         # for non_debug), bruce 080408
                     prefs_key = True # temporary
                 )
    return res

# exercise them, to put them in the menu
debug_pref_write_bonds_compactly()
debug_pref_read_bonds_compactly()

# ==

def debug_pref_write_new_display_names(): #bruce 080328
    # note: reading code for this was made active a few days before 080328;
    # this affects *all* mmp files we write (for save, ND1, NV1)
    res = debug_pref("mmp format: write new display names?",
                     # we will change this to True as soon as all developers
                     # have the necessary reading code... doing that, 080410
                     Choice_boolean_True,
                     non_debug = True,
                     prefs_key = "A10/mmp format: write new display names?"
                 )
    return res

def debug_pref_read_new_display_names(): #bruce 080328
    res = debug_pref("mmp format: read new display names?",
                     Choice_boolean_True, # use False to simulate old reading code for testing
                     ## non_debug = True, # temporary
                         # make ATOM_DEBUG only for release (not useful enough
                         # for non_debug), bruce 080408
                     prefs_key = True # temporary
                 )
    return res

# exercise them, to put them in the menu
debug_pref_write_new_display_names()
debug_pref_read_new_display_names()

# ==

def use_frustum_culling(): #piotr 080401
    """
    If enabled, perform frustum culling in GLPane.
    """
    res = debug_pref("GLPane: enable frustum culling?",
                     Choice_boolean_True,
                     non_debug = True,
                         # leave this visible w/o ATOM_DEBUG for release
                         # [bruce 080408]
                     prefs_key = "A10/GLPane: enable frustum culling?") 

    return res

# ==

def pref_MMKit_include_experimental_PAM_atoms(): #bruce 080412
    res = debug_pref("MMKit: include experimental PAM atoms (next session)?",
                     Choice_boolean_False,
                         # not on by default, and not visible without ATOM_DEBUG,
                         # since these elements would confuse users
                     prefs_key = "A10/MMKit: include experimental PAM atoms?" )
    return res

# ==

def pref_drop_onto_Group_puts_nodes_at_top(): #bruce 080414; added after 1.0.0rc0 was made
    """
    If enabled, nodes dropped directly onto Groups in the Model Tree
    are placed at the beginning of their list of children,
    not at the end as was done before.
    """
    res = debug_pref("Model Tree: drop onto Group puts nodes at top?",
                     Choice_boolean_True, # this default setting fixes a longstanding NFR
                     non_debug = True,
                         # leave this visible w/o ATOM_DEBUG for release
                         # [bruce 080414]
                     prefs_key = "A10/Model Tree: drop onto Group puts nodes at top?")

    return res

pref_drop_onto_Group_puts_nodes_at_top()
    # exercise it at startup to make sure it's in the debug prefs menu
    # TODO: have an init function in this file, run after history is available ###
    # (not sure if first import of this file is after that)

# ==

def _kluge_global_mt_update():
    from foundation import env
        # note: this doesn't cause a module import cycle,
        # but it might be an undesirable inter-package import.
        # (it's also done in a few other places in this file.)
    win = env.mainwindow()
    win.mt.mt_update()
    return
    
def pref_show_node_color_in_MT():
    #bruce 080507, mainly for testing new MT method repaint_some_nodes;
    # won't yet work for internal groups that act like MT leaf nodes
    # such as DnaStrand
    """
    If enabled, show node colors in the Model Tree.
    """
    res = debug_pref("Model Tree: show node colors?",
                     Choice_boolean_False,
                     prefs_key = True,
                     call_with_new_value = (lambda val: _kluge_global_mt_update())
                    )
    return res
    
def pref_show_highlighting_in_MT():
    #bruce 080507
    """
    If enabled, highlighting objects in GLPane causes corresponding
    highlighting in the MT of their containing nodes,
    and (in future) mouseovers in MT may also cause highlighting
    in both places.
    """
    res = debug_pref("Model Tree: show highlighted objects?",
                     Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = (lambda val: _kluge_global_mt_update())
                    )
    return res

# ==

# bondpoint_policy helper function and preferences.
# A future refactoring might make this a method or class,
# but for now it's unclear how to do that (sim_aspect
# needs this before it has a writemmp_mapping to ask it of),
# and there's only one global policy ever used (derived from prefs),
# so this way is easiest for now.
# [bruce 080507/080603]

def pref_minimize_leave_out_PAM_bondpoints(): #bruce 080507
    """
    If enabled, bondpoints on PAM atoms are left out of simulations
    and minimizations, rather than being converted to H (as always occurred
    until now) or anchored (not yet possible) or left unchanged. 

    @warning: not yet fully implemented.
    """
    res = debug_pref("Minimize: leave out PAM bondpoints? (partly nim)",
                     Choice_boolean_False, # not yet safe or tested (and partly nim)
                     ## non_debug = True, # since won't be implemented for v1.1
                     prefs_key = True
                    )
    return res

pref_minimize_leave_out_PAM_bondpoints()

def pref_minimize_leave_PAM_bondpoints_unchanged(): #bruce 080603
    """
    If enabled, bondpoints on PAM atoms are left unchanged during simulations
    and minimizations, rather than being converted to H (as always occurred
    until now) or anchored (not yet possible) or left out (not yet correctly
    implemented).
    """
    res = debug_pref("Minimize: leave PAM bondpoints unchanged?",
                     Choice_boolean_True,
                     non_debug = True, # should be easy to test or change
                     prefs_key = True
                    )
    return res

pref_minimize_leave_PAM_bondpoints_unchanged()

from utilities.constants import BONDPOINT_LEFT_OUT
from utilities.constants import BONDPOINT_UNCHANGED
from utilities.constants import BONDPOINT_ANCHORED # not yet specifiable
from utilities.constants import BONDPOINT_REPLACED_WITH_HYDROGEN

def bondpoint_policy(bondpoint, sim_flag): #bruce 080507/080603
    """
    Determine how to treat the given bondpoint,
    perhaps influenced by debug_prefs and/or whether we're writing
    to a simulation that wants bondpoints modified (sim_flag).

    @return: one of these constants:
             BONDPOINT_LEFT_OUT,
             BONDPOINT_UNCHANGED,
             BONDPOINT_ANCHORED,
             BONDPOINT_REPLACED_WITH_HYDROGEN.

    @see: nsinglets_leftout in class sim_aspect

    @see: sim attribute in class writemmp_mapping
    """
    ## assert bondpoint.element is Singlet # (no need, and avoid import)
    if not sim_flag:
        return BONDPOINT_UNCHANGED
    if len(bondpoint.bonds) != 1:
        # should never happen
        print "bug: %r has %d bonds, namely %r" % \
              (bondpoint, len(bondpoint.bonds), bondpoint.bonds)
        ## someday: return BONDPOINT_LEFT_OUT # or BONDPOINT_UNCHANGED??
        # for now, only this is safe:
        return BONDPOINT_UNCHANGED
    other = bondpoint.bonds[0].other(bondpoint)
    if other.element.pam:
        if pref_minimize_leave_out_PAM_bondpoints():
            return BONDPOINT_LEFT_OUT # BUG: not yet fully implemented by callers
        elif pref_minimize_leave_PAM_bondpoints_unchanged():
            return BONDPOINT_UNCHANGED
        else:
            return BONDPOINT_REPLACED_WITH_HYDROGEN
    else:
        return BONDPOINT_REPLACED_WITH_HYDROGEN
    pass

# ==

def pref_create_pattern_indicators():
    #bruce 080520
    """
    If enabled, each run of Minimize or Simulate
    (in any form, e.g. Adjust or Adjust Atoms too)
    creates graphical pattern indicators,
    and records extra atom and bond tooltip info,
    to show details of how the force field is implemented
    on the current model.
    """
    res = debug_pref("Minimize: force field graphics?",
                     Choice_boolean_False,
                     non_debug = True,
                     prefs_key = True
                    )
    return res

pref_create_pattern_indicators()

# ==

def pref_skip_redraws_requested_only_by_Qt():
    #bruce 080516 moved this here, revised default to be off on Windows
    """
    If enabled, GLPane paintGL calls not requested by our own gl_update calls
    are skipped, as an optimization. See comments where used for details
    and status. Default value depends on platform as of 080516.
    """
    if sys.platform == "win32":
        # Windows -- enabling this causes bugs on at least one system
        choice = Choice_boolean_False
    else:
        # non-Windows -- no known bugs as of 080516
        #bruce 080512 made this True, revised prefs_key
        choice = Choice_boolean_True
    res = debug_pref("GLPane: skip redraws requested only by Qt?",
                      choice,
                      non_debug = True, #bruce 080130
                      prefs_key = "GLPane: skip redraws requested only by Qt?"
                     )
    return res

pref_skip_redraws_requested_only_by_Qt()

# ==

def debug_pref_support_Qt_4point2(): #bruce 080725
    res = debug_pref("support Qt 4.2 (next session)?",
                     Choice_boolean_False,
                     prefs_key = True
                    )
    return res

# ==

def _debug_pref_use_command_stack(): #bruce 080728
    res = debug_pref("use command stack (NIM) (next session)?",
                     Choice_boolean_False,
                     prefs_key = True
                    )
    return res

USE_COMMAND_STACK = _debug_pref_use_command_stack()


#bruce 0808013 moved enableProteins from protein.model.Protein.enableProteins
# to avoid import cycles.
# TODO: rename it to ENABLE_PROTEINS, to fit with coding standard for constants.
enableProteins = debug_pref("Enable Proteins? (next session)",
                             Choice_boolean_False,
                             non_debug = True,
                             prefs_key = True
                            )

MODEL_AND_SIMULATE_PROTEINS = debug_pref("Enable model and simulate protein flyout? (next session)",
    Choice_boolean_False,
    non_debug = True,
    prefs_key = True)

def _debug_pref_keep_signals_always_connected(): #Ninad 2008-08-13
    #-The current code always connects signals while shown a PM and 
    #disconnects those in the close method. The above flag, if True, signals 
    #are connected when PM is created (this is a proposed scheme in the new 
                                      #command stack project)
   #As of 2008-08-13 this is not implemented for - Flyout toolbars , 
   #old commands such as Extrude, Movie. 
    res = debug_pref("Keep signals always connected (NIM) (next session)?",
                     Choice_boolean_False,
                     prefs_key = True
                    )
    return res

KEEP_SIGNALS_ALWAYS_CONNECTED = _debug_pref_keep_signals_always_connected()


def _debug_pref_cseq_is_not_glpane(): #bruce 080813
    res = debug_pref("CommandSequencer is not GLPane (next session)?",
                     Choice_boolean_False,
                     prefs_key = True
                    )
    return res

# todo: XXX = not _debug_pref_cseq_is_not_glpane()



def _debug_pref_break_strands_feature(): #Ninad 2008-08-18
    #debug flag for experimental code Ninad is
#working on (various break strands options). 
#Note that this flag is also used in BreakStrand_Command
#UPDATE 2008-08-19: This preference is set to True by default
    res = debug_pref("DNA: debug new break strands options feature (next session)",
                     Choice_boolean_True,
                     prefs_key = True
                    )
    return res

DEBUG_BREAK_OPTIONS_FEATURE = _debug_pref_break_strands_feature()



# end
