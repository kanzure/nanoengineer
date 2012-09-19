# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
chem_patterns.py -- finding simple patterns of bonded atoms

see also ND-1's pattern matching facility, which is faster and more general

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

Todo later:
- really turn O into 8 and reverse rules as needed
- might need to also check bondtypes or atomtypes someday... problematic since they might be wrong to start with.
- might want to also select bad-valence atoms, or have another command for that.
- might need a few more kinds of patterns, like one for just 2 atoms... wait and see what's suggested.
"""

import foundation.env as env
import utilities.debug as debug

from platform_dependent.PlatformDependent import fix_plurals

cmdname = "Select Bad Atoms"

def compile_patterns():
    ## bad_patterns = [('O', 'O', 'O')] # this could be any list of triples of element symbols, and could be an argument.
    bad_patterns_compiled = [(8,8,8)] # corresponding element numbers
        # (easily computed from the above using PeriodicTable.getElement(sym).eltnum)
    # if any are not symmetric, we should compile them in both directions, e.g. if one was OON we'd also put NOO in this table.
    bad_patterns_dict = dict([(p,p) for p in bad_patterns_compiled]) # dict version for fast lookup #e could easily optimize further
    root_eltnums = {}
    other_eltnums = {}
    for o1e,ae,o2e in bad_patterns_compiled:
        other_eltnums[o1e] = o1e
        root_eltnums[ae] = ae
        other_eltnums[o2e] = o2e
    root_eltnums = root_eltnums.values() # a list might be faster to search than a dict, since the list is so short (I don't know)
    other_eltnums = other_eltnums.values()
    return bad_patterns_dict, root_eltnums, other_eltnums

def select_bad_atoms_cmd(widget): #bruce 060615 demo of simple "spelling checker" with hardcoded rules
    """
    Out of the selected atoms or chunks, select the atoms which have "bad spelling".
    """
    from utilities.Log import orangemsg, redmsg, greenmsg
    greencmd = greenmsg("%s: " % cmdname)
    orangecmd = orangemsg("%s: " % cmdname) # used when bad atoms are found, even though no error occurred in the command itself
    win = env.mainwindow()
    assy = win.assy
    # 1. compile the patterns to search for. This could be done only once at init time, but it's fast so it doesn't matter.
    bad_patterns_dict, root_eltnums, other_eltnums = compile_patterns()
    # 2. Find the atoms to search from (all selected atoms, or atoms in selected chunks, are potential root atoms)
    checked_in_what = "selected atoms or chunks"
    contained = "contained"
    atoms = {}
    for m in assy.selmols:
        atoms.update(m.atoms)
    atoms.update(assy.selatoms)
    if 0:
        # do this if you don't like the feature of checking the entire model when nothing is selected.
        if not atoms:
            env.history.message(redmsg("%s: nothing selected to check." % cmdname))
            return
    else:
        # if nothing is selected, work on the entire model.
        if not atoms:
            checked_in_what = "model"
            contained = "contains"
            for m in assy.molecules:
                atoms.update(m.atoms)
            if not atoms:
                env.history.message(redmsg("%s: model contains no atoms." % cmdname))
                return
        pass
    # 3. Do the search.
    bad_triples = [] # list of bad triples of atoms (perhaps with overlap)
    for a in atoms.itervalues():
        ae = a.element.eltnum
        if ae not in root_eltnums:
            continue
        checkbonds = []
        for b in a.bonds:
            o = b.other(a)
            oe = o.element.eltnum
            if oe in other_eltnums:
                checkbonds.append((o,oe))
        nbonds = len(checkbonds)
        if nbonds > 1: #e we could easily optimize the following loop for fixed nbonds like 2,3,4... or code it in pyrex.
            for i in xrange(nbonds-1):
                for j in xrange(i+1,nbonds):
                    if (checkbonds[i][1], ae, checkbonds[j][1]) in bad_patterns_dict:
                        # gotcha!
                        bad_triples.append((checkbonds[i][0], a, checkbonds[j][0]))
    if not bad_triples:
        env.history.message(greencmd + "no bad patterns found in %s." % checked_in_what)
        return
    # done - deselect all, then select bad atoms if any. (Should we also deselect if we found no bad atoms, above??)
    win.glpane.gl_update()
    assy.unpickall_in_GLPane() #bruce 060721; was unpickatoms and unpickparts
    bad_atoms = {}
    for a1,a2,a3 in bad_triples:
        bad_atoms[a1.key] = a1
        bad_atoms[a2.key] = a2
        bad_atoms[a3.key] = a3
    reallypicked = 0
    for a in bad_atoms.itervalues():
        a.pick()
        reallypicked += (not not a.picked) # check for selection filter effect
    env.history.message(orangecmd + fix_plurals(
                        "%s %s %d bad atom(s), in %d bad pattern(s)." % \
                        (checked_in_what, contained, len(bad_atoms), len(bad_triples)) ))
    if reallypicked < len(bad_atoms):
        env.history.message( orangemsg("Warning: ") + fix_plurals(
                             "%d bad atom(s) were/was not selected due to the selection filter." % \
                             (len(bad_atoms) - reallypicked) ))
    win.update_select_mode()
    return

def initialize():
    debug.register_debug_menu_command("%s" % cmdname, select_bad_atoms_cmd)

# end
