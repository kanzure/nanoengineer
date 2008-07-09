# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_commands.py - UI commands offered directly by the dna updater.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.debug import register_debug_menu_command

from model.global_model_changedicts import _changed_structure_Atoms

import foundation.env as env

from platform_dependent.PlatformDependent import fix_plurals

from utilities.Log import greenmsg

from dna.model.pam3plus5_ops import add_basepair_handles_to_atoms #k import ok?

# ==

def initialize_commands():
    _register_our_debug_menu_commands()
    return

# ==

def rescan_atoms_in_current_part(assy, only_selected = False):
    oldlen = len(_changed_structure_Atoms)
    for mol in assy.molecules:
        for atom in mol.atoms.itervalues():
            if not only_selected or atom.picked or \
               (atom.is_singlet() and atom.singlet_neighbor().picked):
                _changed_structure_Atoms[atom.key] = atom
    newlen = len(_changed_structure_Atoms)
    msg = "len(_changed_structure_Atoms) %d -> %d" % (oldlen, newlen)
    env.history.message(greenmsg( "DNA debug command:") + " " + msg)
    assy.w.win_update() #bruce 080312 bugfix
    return

def rescan_all_atoms(glpane):
    rescan_atoms_in_current_part( glpane.assy)

def rescan_selected_atoms(glpane):
    rescan_atoms_in_current_part( glpane.assy, only_selected = True)

def add_basepair_handles_to_selected_atoms(glpane): #bruce 080515
    assy = glpane.assy
    goodcount, badcount = add_basepair_handles_to_atoms(assy.selatoms.values())
    msg = "adding handles to %d duplex Gv5 atom(s)" % (goodcount,)
    if badcount:
        msg += " (but not %d other selected atom(s))" % (badcount,)
    msg = fix_plurals(msg)
    env.history.message(greenmsg( "Add basepair handles:") + " " + msg)
    assy.w.win_update()
    return

# ==

def _register_our_debug_menu_commands():
    register_debug_menu_command( "DNA: rescan all atoms", rescan_all_atoms )
    register_debug_menu_command( "DNA: rescan selected atoms", rescan_selected_atoms )
    register_debug_menu_command( "DNA: add basepair handles", add_basepair_handles_to_selected_atoms )

# end
