# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
dna_updater_debug.py -- debug code for dna_updater

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities import debug_flags

from graphics.drawing.CS_draw_primitives import drawline

from model.jigs import Jig

import foundation.env as env

from utilities.Log import quote_html

from utilities.debug import register_debug_menu_command

from platform_dependent.PlatformDependent import fix_plurals

from utilities.constants import gensym

from widgets.simple_dialogs import grab_text_using_dialog

# ==

def assert_unique_chain_baseatoms(chains, when = ""):
    if when:
        when = " (%s)" % when
    baseatom_info = {} # maps atom.key to chain
    for chain in chains:
        for atom in chain.baseatoms:
            assert atom.key not in baseatom_info, \
                   "baseatom %r in two chains%s: %r and %r" % \
                   (atom, when, baseatom_info[atom.key], chain)
            baseatom_info[atom.key] = chain
    return

def assert_unique_ladder_baseatoms(ladders, when = ""):
    if when:
        when = " (%s)" % when
    baseatom_info = {} # maps atom.key to (ladder, whichrail, rail, pos)
    for ladder in ladders:
        rails = ladder.all_rail_slots_from_top_to_bottom() # list of rail or None
        lastlength = None
        for whichrail in [0,1,2]:
            rail = rails[whichrail]
            if not rail:
                continue
            length = len(rail)
            if lastlength is not None:
                assert lastlength == length, "rail length mismatch in %r" % ladder
            lastlength = length
            baseatoms = rail.baseatoms
            for pos in range(length):
                atom = baseatoms[pos]
                loc_info = (ladder, whichrail, rail, pos)
                assert atom.key not in baseatom_info, \
                   "baseatom %r in two ladders%s; loc info: %r and %r" % \
                   (atom, when, baseatom_info[atom.key], loc_info)
                baseatom_info[atom.key] = loc_info
    return

def assert_unique_wholechain_baseatoms(wholechains, when = ""):
    if when:
        when = " (%s)" % when
    baseatom_info = {} # maps atom.key to (wholechain, chain)
    for wholechain in wholechains:
        for chain in wholechain.rails():
            for atom in chain.baseatoms:
                loc_info = (wholechain, chain)
                assert atom.key not in baseatom_info, \
                       "baseatom %r in two rails%s; loc info: %r and %r" % \
                       (atom, when, baseatom_info[atom.key], loc_info)
                baseatom_info[atom.key] = loc_info
    return

# ==

# some of the following might be of more general use

def find_atom_by_name(assy, name): # todo: refile to debug or assy
    """
    Find atom in assy by its name (case sensitive) or number.

    @warning: current implementation only works in the current Part.
    """
    name = str(name) # in case it's an int
    # bug: this version only works in the current Part
    for mol in assy.molecules:
        for atom in mol.atoms.itervalues():
            foundname = str(atom)
            foundnumber = str(atom.key)
            if name in (foundname, foundnumber): # bugfix 080227: foundnumber
                return atom
    return None

class VeryVisibleAtomMarker(Jig):
    mmp_record_name = "VeryVisibleAtomMarker" #k ok? note that it has no reading code...
    # todo: mmp reading code; icon
    def _draw_jig(self, glpane, color, highlighted = False):
        length = glpane.scale # approx.
        # print "%r got color = %r" % (self, color,) # it gets gray
        for atom in self.atoms:
            pos = atom.posn()
            drawline(color, pos, - glpane.pov, width = 2)
                # line from center of view, in case far off-screen
            # lines in diagonal directions (more likely to hit screen if off-screen)
            for direction in (glpane.up + glpane.right,
                              glpane.right + glpane.down,
                              glpane.down + glpane.left,
                              glpane.left + glpane.up):
                endpoint = pos + direction * length
                drawline( color, pos, endpoint, width = 2)
        return
    # not needed if default __str__ contains atom name:
    ## def __str__(self):
    ##     pass
    pass

def mark_atom_by_name(assy, name):
    """
    If you can find an atom of the given name, mark it visibly.
    """
    atom = find_atom_by_name(assy, name)
    if atom:
        env.history.message(quote_html("found atom %r: %r, in part %r" % (name, atom, atom.molecule.part)))
        mark_one_atom(atom)
    else:
        env.history.message(quote_html("can't find atom %r (in part %r)" % (name, assy.part,)))
    return

def mark_one_atom(atom):
    assy = atom.molecule.assy
    jig = VeryVisibleAtomMarker(assy, [atom])
    jig.name = "Marked Atom %s" % (atom,) ##k
    assy.place_new_jig(jig)
    # redraw, etc
    assy.win.glpane.gl_update() # this works now to redraw
    if 0:#####
        assy.win.mt.mt_update() # guess this also might be needed, should fix in same way
        # AttributeError: mt_update, but didn't stop it from working to redraw, so only gl_update was needed for that
    # the above did not suffice to redraw. did our debug pref skip the redraw?? need assy.changed? or better checkpoints?
    # or was it assy.glpane attr error, now fixed (how come i didn;t see that vbefore?)
        assy.changed() # see if this helps; if so, should also debug need for this when i have time
    ###BUG - all the above is not enough to redraw it. Another deposit will do it though. @@@
    return

def mark_atoms(atoms):
    assert atoms # a list
    assy = atoms[0].molecule.assy
    for atom in atoms:
        assert atom.molecule.assy is assy # all in same assy
    jig = VeryVisibleAtomMarker(assy, atoms)
    jig.name = gensym("Marked Atoms ", assy)
    assy.place_new_jig(jig)
    # redraw, etc
    assy.win.glpane.gl_update() # this works now to redraw
    #e more updates?
    return

def mark_atom_by_name_command(glpane):
    # review: is this really what the arg always is? i bet it's whatever widget this appeared in...
    ok, text = grab_text_using_dialog( default = "Ss3-564",
                                       title = "Mark atom by name",
                                       label = "atom name or number:" )
    if ok:
        name = text
        assy = glpane.assy
        mark_atom_by_name(assy, name)
    return

# todo: should do this in an initialize function!
register_debug_menu_command( "Mark atom by name...", mark_atom_by_name_command )

#e could also: select multiple atoms by list of names

def select_atoms_with_errors_command(glpane):
    """
    current part only...
    """
    count = 0
    assy = glpane.win.assy
    for mol in assy.molecules: # current part only
        for atom in mol.atoms.itervalues():
            if atom._dna_updater__error:
                count += 1 # whether or not already selected
                atom.pick() # should be safe inside itervalues
                    ### REVIEW: selection filter effect not considered
    msg = "found %d pseudoatom(s) with dna updater errors in %r" % (count, assy.part)
    msg = fix_plurals(msg)
    env.history.message(quote_html(msg))
    return

register_debug_menu_command( "DNA updater: select atoms with errors", select_atoms_with_errors_command )

def mark_selected_atoms_command(glpane): # untested
    """
    current part only...
    """
    assy = glpane.win.assy
    atoms = assy.selatoms.values()
    mark_atoms(atoms)
    msg = "marked %d selected atom(s)" % len(atoms) #e could use part of this string in jig name too
    msg = fix_plurals(msg)
    env.history.message(quote_html(msg))
    return

register_debug_menu_command( "Mark selected atoms", mark_selected_atoms_command )

# ==

##_found = None
##_found_molecule = -1 # impossible value of _found.molecule

# convenience methods -- add code to these locally, to print things
# at start and end of every dna updater run; runcount counts the runs of it
# in one session; changed_atoms should not be modified, has not been filtered at all

def debug_prints_as_dna_updater_starts( runcount, changed_atoms):
    # print "\ndebug_prints_as_dna_updater_starts: %d, len %d\n" % \
    # (runcount, len(changed_atoms))
##    global _found, _found_molecule
##    if _found is None:
##        win = env.mainwindow()
##        _found = find_atom_by_name(win.assy, 37)
##        if _found is not None:
##            print "\nfound atom", _found
##    if _found is not None and _found_molecule is not _found.molecule:
##        print "\nstart %d: %r.molecule = %r" % (runcount, _found, _found.molecule)
##        _found_molecule = _found.molecule
    if debug_flags.DNA_UPDATER_SLOW_ASSERTS:
        win = env.mainwindow()
        win.assy.checkparts("start dna updater %d" % runcount)
    return

def debug_prints_as_dna_updater_ends( runcount):
    # print "\ndebug_prints_as_dna_updater_ends: %d\n" % ( runcount, )
##    global _found, _found_molecule
##    if _found is not None and _found_molecule is not _found.molecule:
##        print "\nend %d: %r.molecule = %r" % (runcount, _found, _found.molecule)
##        _found_molecule = _found.molecule
    if debug_flags.DNA_UPDATER_SLOW_ASSERTS:
        win = env.mainwindow()
        win.assy.checkparts("end dna updater %d" % runcount)
    return

# end
