# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
bond_updater.py

[unfinished]

Recompute structural bond orders when necessary.

$Id$

This is needed for bonds between atoms whose atomtypes make p orbitals
available for bonding, to check whether pi bonds are formed,
whether they're aromatic or double or triple, to check for
radicals (pi systems containing unpaired electrons),
and to notice graphite.

History:

bruce 050627 started this as part of supporting higher-order bonds.
'''

__author__ = 'bruce'


import platform

from op_select_doubly import twoconner

def update_bonds_after_each_event( _changed_structure_atoms):
    """[should be called only from env.post_event_updates]
       This should be called at the end of every user event which might affect
    the atomtypes or bond-sets of any atoms or singlets, which are passed as the
    values of the dict _changed_structure_atoms, which we should not modify
    (and which no other code will modify while we use it). (As it happens,
    the caller will clear that dict after we return.)
       This function will either update, or record as needing update, the
    structural bond orders and associated data for all
    real atoms, real bonds, and open bonds which might be in pi systems
    (or which were, but aren't anymore). [And it might do more. #k if so, #doc that here.]
       Since it must be fast, it won't do work which leads it away from the actual
    atoms it's passed, and it will leave existing bond orders alone whenever they're
    locally consistent with the current atomtypes. That is, it will only act when
    there are local inconsistencies, and it will only fix them when this can be done
    on just the atoms it was passed (or their bonds), and in a reasonably unambiguous way;
    whenever it thinks a more global update it needed, it will record this fact
    (and the affected atoms) so the user can be advised that a global bond-update is needed.
       It will assume that interpart bonds (if any) have already been broken.
    (#e Or we might decide to extend it to break them itself.)
    """
    for atm in _changed_structure_atoms.itervalues():
        #e ignore killed atoms
        # for singlets, just look at their base atoms
        # when info must be recorded for later, do this per-chunk or per-part.
        ##k Do we move existing such info when atoms moved or were killed??
        
        atype = atm.atomtype
        
    if 0 and platform.atom_debug:
        print "atom_debug: update_bonds_after_each_event NIM; "\
              "not yet handling %d atoms or singlets in _changed_structure_atoms." % len(_changed_structure_atoms)
        for atm in _changed_structure_atoms.itervalues():
            print "eg this one",atm # so far, fails to notice atoms created as part of a cookie.
    return

def update_bonds_command(part): # for initial test, put this into debug menu (??)
    """Do a full updating of all possibly-pi bonds in the given part.
    Initial implem keeps no history anywhere, just redoes everything from scratch each time.
    """
    history = part.assy.w.history
    # First, find all the sp2 or sp atoms and open bonds, and understand how they're connected.
    chunks = part.molecules
    nsp2, nsp = 0,0 #####@@@@@ debug only
    for chunk in chunks:
        for atom in chunk.atoms.itervalues(): # includes "singlets" (open bonds); these usually have 'sp' hybridization
            # notice sp2 or sp atoms or open bonds; ignore sp3
            atype = atom.atomtype
            spX = atype.spX
            if spX == 3:
                # usual case, should be fast; just ignore this atom
                continue
            if atype.openbond:
                # sort it depending on max (least fancy) spX of itself (usually 1 for 'sp') and atom it's connected to
                bonds = atom.bonds
                if len(bonds) != 1:
                    # some sort of error -- skip it (should never happen)
                    if platform.atom_debug:
                        print "atom_debug: error: update_bonds_command skipping singlet %r with not exactly one bond" % atom
                    continue 
                spX = max(spX, bonds[0].other(atom).atomtype.spX)
                if spX == 3:
                    continue
            if spX == 2:
                # sp2 atom or open bond
                # ...
                nsp2 += 1
            else:
                assert spX == 1
                # sp atom or open bond
                # ...
                nsp += 1
        pass
    #e print number of various types of atoms found

    #e we might want to count total number of valence e's, and also collect all open bonds
    # (in each 1-connected part) for merge into pseudorings...
    
    msg = "nsp2 = %d, nsp = %d" % (nsp2, nsp)
    print msg
    history.message(msg)
    # scan for connected components of this, and then (in each one) doubly-conn ones but inferring bond order
    # since that scan has to notice atom types anyway, it might be best for above loop to just detect marks from it, not sort by type;
    # but i won't do that, since I want the code to decompose well into layers, where above will become an incremental
    # watcher-for-sp2/sp atoms layer, not always noticing connectedness. So above should record, and then we should rescan.
    pass

class xxx( twoconner): # we'll start this from each open bond. when it reaches another, that's in same conncomp, so pretend a ring.
    # so a cutedge has no open bonds below it and thus has a definite e-parity and inferred bond order when nonradical.
    # and also, for a cutedge we can immediately dive in and infer back inside it, breaking that into smaller no-open-bond
    # systems and inferring their status (I think this has to be effectively recursive, ie not lintime;
    # might be better to do it breadth-first? someday we want it to record enough info to be faster when reseeing the same rings...
    # right now this will happen for a chain of bond2-connected benzenes... actually it might be ok, since it stops at each cutedge.)
    # ... this means: coming out of a cutedge, we know whether other side proves it a radical, and if not, the exact order.
    # (so far this is sp2-only, I haven't thought through sp atoms.)
    """[private]
    Specialized 2-connected-subset-traverser for pi systems -- really only for bonds that might be aromatic, GIVEN INFERRABLE ORDERs.
    Maybe we should infer fixed orders, when possible, during the same traversal that finds 1-conn and 2-conn sets?? ###@@@
    Since otherwise we might see 2-conn sets through bonds which are in fact held to order 1 by e.g. H2C=C< ...
    """
    def neighbors_except(self, N, priornode):
        "Assume N is an atom of aromatic type. Find neighbors across bonds that might be aromatic, except priornode."
        res = []
        for b in N.bonds:
            #e reject bonds held artificially at a fixed integral order (even if >1, I think)
            other = b.other(N)
            if other is priornode: continue
            atype = other.atomtype
            if atype.spX < 3:
                res.append(other)
        return res
    pass


# sp atoms are like this: not counting circles of only them, chains of them have to end,
# and when they end only one of their two overlayed pi-systems can be connected to.
# So, for even-length chains of them, the orders of the other pisystem (in the "resonance form model") go 0,1,0,1,0,
# so we can ignore it and look at the other pi system, x, 1-x, x, whose orders act just like those for CH units.
# For odd-length chains, *both* orders are forced, one to 0,1,0,1, the other to 1,0,1,0, so it's all double bonds.
# For open bonds on sp's, they might get extended by more sp's to any length, then hooked to graphite or each other...
# so just treat them as if hooked to graphite, at any point inside them, regardless of length.
# This is for C(sp)... for 1-valent sp atoms, we know the full story right away (can't be aromatic I think).
# But that can be noticed by order inference rather than being a special case.

# Does this mean I can "start from each open bond" w/o caring whether it's bonded to an sp or sp2 atom?
# I suspect so... but when backing out, I have to count chainlength of sp's, as well as valence e's, rings seen or not, etc.

# end
