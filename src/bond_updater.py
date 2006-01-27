# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
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

(Much of that is not yet implemented for Alpha6.)

History:

bruce 050627 started this as part of supporting higher-order bonds.
'''

__author__ = 'bruce'


import platform
from debug import print_compact_traceback, print_compact_stack

from bond_constants import *


def update_bonds_after_each_event( _changed_structure_atoms):
    ###@@@ so far this is called by update_parts (eg mode chgs),
    # and near the start of a GLPane repaint event (should be enough),
    # and only when _changed_structure_atoms is nonempty. #k
    # It misses hearing about killed atoms or singlets,
    # but does hear about atoms shown only in the elt selector thumbviews!
    # I guess the latter is good, since that way it can update the bond orders in those views as well!
    # However, debug tests showed that the elt selector thumbviews need a separate redraw to show this...
    # that's ok, they're only supposed to draw single-bond atypes anyway.
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
    bonds_to_fix = {}
    mols_changed = {} #bruce 060126, so atom._changed_structure() doesn't need to call atom.changed() directly
    
    for atm in _changed_structure_atoms.itervalues():
        #e ignore killed atoms -- though at the moment they don't even show up in this list (which is bad but tolerable)
        # for singlets, just look at their base atoms [as of 050707 just look at all bonds of all unkilled atoms]
        #e when info must be recorded for later, do this per-chunk or per-part.
        ##k Do we move existing such info when atoms moved or were killed??
        
        mol = atm.molecule # might be None or nullMol; check later
        mols_changed[id(mol)] = mol
        
        atype = atm.atomtype # make sure this is defined; also it will tell us the permitted bond orders for any bond on this atom
        for bond in atm.bonds:
            v6 = bond.v6
            if v6 != V_SINGLE: # this test is just an optim
                if not atype.permits_v6(v6):
                    # this doesn't notice things like S=S (unstable), only the S= and =S parts (ok taken alone)
                    bonds_to_fix[id(bond)] = bond
                ###e also check legal endcombos for aromatic, graphite (carbomeric?)
                ###e also directly check sp-chain-lengths here, infer double bonds when odd length and connected, etc??

        # Tell perceived structures involving this atom that it changed.
        # (These will include sp-chains and pi-systems, and maybe more. For Alpha6, probably only sp-chains.)
        # For now, these are stored in jigs; one jig might contain just one perceived structure,
        # or all of one kind in one set of atoms (the following code needn't know which).
        if atm.jigs: # most atoms have no jigs, so this initial optim test is worthwhile
            for jig in atm.jigs[:]:
                try:
                    method = jig.changed_structure
                except AttributeError:
                    pass # initial kluge so I don't need to extend class Jig
                else:
                    try:
                        method(atm) # this is permitted to destroy jig and remove it from atm.jigs
                    except:
                        print_compact_traceback("ignoring exception in jig.changed_atom(%r) for %r" % (atm, jig))
                continue
        
        # atom-valence checks can't be done until we fix illegal bond types, below
        # comments about future atom-valence checks:
        #e should we also check atypes against numbonds and total bond valence (in case no bonds need fixing or they don't change)?
        # note: that's the only way we'll ever notice we need to increase any bonds from single, on sp2 atoms!!!
        # Do we need to separately track needed reductions (from atypes) or certainty-increases (A no longer allowed) or increases
        # (from atom valence)??
        # For certainty-increases, should we first figure out the rest before seeing what to change them to? (guess: no, but not sure)
        # (above cmts are obs, see paper notes about the alg)

    for mol in mols_changed.itervalues():
        if mol is not None:
            mol.changed() # should be safe for nullMol (but not for None)
    
    if not bonds_to_fix:
        return # optim [will be wrong once we have atom valence checks below]

    for bond in bonds_to_fix.itervalues():
        # every one of these bonds is wrong, in a direct local way (ie due to its atoms)!
        # figure out what to change it to, and [someday] initiate our scan of changes from each end of each bond.
        new_v6 = best_corrected_v6(bond) ####@@@@ IMPLEM the rest of that... actually this'll all be revised
        bond.set_v6(new_v6) #####@@@@@ ensure this calls _changed_structure on both atoms -- WRONG, needs to call something different,
            # saying it changes bond orders but not bonds themselves (so e.g. sp chains update geom but don't get destroyed).
            # [As of 050725 I think it doesn't do either of those.]
            # WARNING: this might add new atoms to our argument dict, _changed_structure_atoms
            # (and furthermore, we might depend on the fact that it does, for doing valence checks on them!)

    return # from update_bonds_after_each_event

most_permissible_v6_first = ( V_SINGLE, V_DOUBLE, V_AROMATIC, V_GRAPHITE, V_TRIPLE, V_CARBOMERIC ) # not quite true for graphite?
    ####@@@@ review this -- all uses should be considered suspicious [050714 comment]

def best_corrected_v6(bond):
    """This bond has an illegal v6 according to its bonded atomtypes
    (and I guess the atomtypes are what has just changed?? ###k).
    Say how we want to fix it (or perhaps fix the atomtypes?? #e).
    """
    # Given that the set of permissible bond types (for each atomtype, ignoring S=S prohibition and special graphite rules)
    # is some prefix of [single, double, aromatic/graphite, triple, carbomeric],
    # I think it's ok to always take the last permissible element of that list (using relaxed rules for graphite)...
    # no, it depends on prior bond (presumably one the user likes, or at least consented to),
    # but clearly we move to the left in that list. Like this: c -> a, 3 -> max in list? or 2? or depends on other bonds/valences?
    pass # stub... might return a list of legal btypes in order of preference, for inference code (see paper notes)
    v6 = bond.v6
    try:
        lis = corrected_v6_list[v6]
    except KeyError:
        # this happens for illegal v6 values
        return V_SINGLE
    atype1 = bond.atom1.atomtype # fyi, see also possible_bond_types() for similar code
    atype2 = bond.atom2.atomtype
    for v6 in lis:
        if v6 == V_SINGLE or atype1.permits_v6(v6) and atype2.permits_v6(v6):
            return v6
    assert 0, "no legal replacement for v6 = %r in %r" % (v6,self)
    return V_SINGLE

# map a now-illegal v6 to the list of replacements to try (legal ones only, of course; in the order of preference given by the list)
corrected_v6_list = {
    V_DOUBLE: (V_SINGLE,),
    V_TRIPLE: (V_DOUBLE, V_SINGLE),
    V_AROMATIC: (V_SINGLE,),
    V_GRAPHITE: (V_AROMATIC, V_SINGLE),
    V_CARBOMERIC: (V_AROMATIC, V_DOUBLE, V_SINGLE),
 }

# ==

def process_changed_bond_types( _changed_bond_types):
    """Tell whoever needs to know that some bond types changed.
    For now, that means only bond.pi_bond_obj objects on those very bonds.
    """
    for bond in _changed_bond_types.itervalues():
        obj = bond.pi_bond_obj
        if obj is not None:
            obj.changed_bond_type(bond)
    return

# end
