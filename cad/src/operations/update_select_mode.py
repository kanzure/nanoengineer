# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
update_select_mode.py - change currentCommand or assy.selwhat or selection
to make them consistent

@author: Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Note: this can still have an effect, but ought to be generalized
and refactored. It is accessed as a method on the main window,
but is in its own file since it probably doesn't belong there
after refactoring and since that module is too long.

History:

bruce 050124 wrote this [as a method of the model tree];
should generalize and refile;
should be used for more or for all events

bruce 060403 revised this but didn't update docstring [of method in modeltree];
now it can change from *Chunk modes to Build, only, I think

bruce 081216 moved this out of class ModelTree (where it made no sense)
into its own file, to be called via a same-named method on MWsemantics
"""

from utilities.GlobalPreferences import permit_atom_chunk_coselection

from utilities.constants import SELWHAT_ATOMS
from utilities.constants import SELWHAT_CHUNKS
from utilities.constants import SELWHAT_NAMES

from utilities import debug_flags

def update_select_mode(win):
    """
    Warning: this docstring is partly obsolete.

    This should be called at the end of event handlers which might have
    changed the current internal selection mode (atoms vs chunks),
    to resolve disagreements between that and the visible selection mode
    iff it's one of the Select modes [or more generally, i assume as of 060403,
    if the current mode wants to be ditched if selwhat has to have certain values it dislikes].
       If the current mode is not one of Select Atoms or Select Chunks (or a subclass),
    this routine has no effect.
    (In particular, if selwhat changed but could be changed back to what it was,
    it does nothing to correct that [obs? see end of docstring], and indeed it doesn't know the old value of
    selwhat unless the current mode (being a selectMode) implies that.)
       [We should generalize this so that other modes could constrain the selection
    mode to just one of atoms vs chunks if they wanted to. However, the details of this
    need design, since for those modes we'd change the selection whereas for the
    select modes we change which mode we're in and don't change the selection. ###@@@]
       If possible, we leave the visible mode the same (even changing assy.selwhat
    to fit, if nothing is actually selected [that part was NIM until 050519]).
    But if forced to, by what is currently selected, then we change the visible
    selection mode to fit what is actually selected. (We always assert that selwhat
    permitted whatever was selected to be selected.)
    """
    if permit_atom_chunk_coselection(): #bruce 060721, experimental
        return

    from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command # todo: move to toplevel

    #bruce 050519 revised docstring and totally rewrote code.
    assy = win.assy
    commandSequencer = win.commandSequencer #bruce 071008
    mode = commandSequencer.currentCommand
        #bruce 071008; note, I'm not sure it's right to ask the currentCommand
        # for selwhat_from_mode, as opposed to the current graphicsMode!
        # This whole thing needs total revamping (along with everything
        # related to what can be selected at a given time), so I'm not going
        # to worry about it for now.
    part = assy.part
    # 0. Appraise the situation.
    # 0a: assy.selwhat is what internal code thinks selection restriction is, currently.
    selwhat = assy.selwhat
    assert selwhat in (SELWHAT_CHUNKS, SELWHAT_ATOMS) # any more choices, or change in rules, requires rewriting this method
    # 0b. What does current mode think it needs to be?
    # (Someday we might distinguish modes that constrain this,
    #  vs modes that change to fit it or to fit the actual selection.
    #  For now we only handle modes that change to fit the actual selection.)
    selwhat_from_mode = None # most modes don't care
    if isinstance( mode, SelectChunks_Command):
        # TODO: replace this by a method call or getattr on mode
        selwhat_from_mode = SELWHAT_CHUNKS
    #bruce 060403 commenting out the following, in advance of proposed removal of Select Atoms mode entirely:
##        elif isinstance( mode, SelectAtoms_Command) and mode.commandName == SelectAtoms_Command.commandName:
##            #bruce 060210 added commandName condition to fix bug when current mode is Build (now a subclass of Select Atoms)
##            selwhat_from_mode = SELWHAT_ATOMS
    change_mode_to_fit = (selwhat_from_mode is not None) # used later; someday some modes won't follow this
    # 0c. What does current selection itself think it needs to be?
    # (If its desires are inconsistent, complain and fix them.)
    if assy.selatoms and assy.selmols:
        if debug_flags.atom_debug:
            #bruce 060210 made this debug-only, since what it reports is not too bad, and it happens routinely now in Build mode
            # if atoms are selected and you then select a chunk in MT
            print "atom_debug: bug, fyi: there are both atoms and chunks selected. Deselecting some of them to fit current mode or internal code."
        new_selwhat_influences = ( selwhat_from_mode, selwhat) # old mode has first say in this case, if it wants it
        #e (We could rewrite this (equivalently) to just use the other case with selwhat_from_sel = None.)
    else:
        # figure out what to do, in this priority order: actual selection, old mode, internal code.
        if assy.selatoms:
            selwhat_from_sel = SELWHAT_ATOMS
        elif assy.selmols:
            selwhat_from_sel = SELWHAT_CHUNKS
        else:
            selwhat_from_sel = None
        new_selwhat_influences = ( selwhat_from_sel, selwhat_from_mode, selwhat)
        if selwhat_from_sel is not None and selwhat_from_sel != selwhat:
            # following code will fix this with no harm, so let's not consider it a big deal,
            # but it does indicate a bug -- so just print a debug-only message.
            # (As of 050519 740pm, we get this from the jig cmenu command "select this jig's atoms"
            #  when the current mode is more compatible with selecting chunks. But I think this causes
            #  no harm, so I might as well wait until we further revise selection code to fix it.)
            if debug_flags.atom_debug:
                print "atom_debug: bug, fyi: actual selection (%s) inconsistent " \
                      "with internal variable for that (%s); will fix internal variable" % \
                      (SELWHAT_NAMES[selwhat_from_sel], SELWHAT_NAMES[selwhat])
    # Let the strongest (first listed) influence, of those with an opinion,
    # decide what selmode we'll be in now, and make everything consistent with that.
    for opinion in new_selwhat_influences:
        if opinion is not None:
            # We have our decision. Carry it out (on mode, selection, and assy.selwhat) and return.
            selwhat = opinion
            if change_mode_to_fit and selwhat_from_mode != selwhat:
                #bruce 050520 fix bug 644 by only doing this if needed (i.e. if selwhat_from_mode != selwhat).
                # Without this fix, redundantly changing the mode using these tool buttons
                # immediately cancels (or completes?) any node-renaming-by-dblclick
                # right after it gets initiated (almost too fast to see).
                if selwhat == SELWHAT_CHUNKS:
                    win.toolsSelectMolecules()
                    print "fyi: forced mode to Select Chunks" # should no longer ever happen as of 060403
                elif selwhat == SELWHAT_ATOMS:
                    win.toolsBuildAtoms() #bruce 060403 change: toolsSelectAtoms -> toolsBuildAtoms
                    ## win.toolsSelectAtoms() #bruce 050504 making use of this case for the first time; seems to work
            # that might have fixed the following too, but never mind, we'll just always do it -- sometimes it's needed.
            if selwhat == SELWHAT_CHUNKS:
                part.unpickatoms()
                assy.set_selwhat(SELWHAT_CHUNKS)
            elif selwhat == SELWHAT_ATOMS:
                if assy.selmols: # only if needed (due to a bug), since this also desels Groups and Jigs
                    # (never happens if no bug, since then the actual selection has the strongest say -- as of 050519 anyway)
                    part.unpickparts()
                assy.set_selwhat(SELWHAT_ATOMS) # (this by itself does not deselect anything, as of 050519)
            return
    assert 0, "new_selwhat_influences should not have ended in None: %r" % (new_selwhat_influences,)
    # scratch comments:
    # if we had been fixing selwhat in the past, it would have fixed bug 500 in spite of permit_pick_parts in cm_hide/cm_unhide.
    # So why aren't we? let's find out with some debug code... (now part of the above, in theory)
    return

# end
