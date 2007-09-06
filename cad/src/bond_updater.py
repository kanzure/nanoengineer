# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
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
"""

__author__ = 'bruce'


from debug import print_compact_traceback, print_compact_stack

from bond_constants import V_SINGLE
from bond_constants import V_DOUBLE
from bond_constants import V_AROMATIC
from bond_constants import V_GRAPHITE
from bond_constants import V_TRIPLE
from bond_constants import V_CARBOMERIC

import env

def _update_bonds_after_each_event( changed_structure_atoms):
    ###@@@ so far this is called by update_parts (eg mode chgs),
    # and near the start of a GLPane repaint event (should be enough),
    # and only when changed_structure_atoms is nonempty. #k
    # It misses hearing about killed atoms or singlets,
    # but does hear about atoms shown only in the elt selector thumbviews!
    # I guess the latter is good, since that way it can update the bond orders in those views as well!
    # However, debug tests showed that the elt selector thumbviews need a separate redraw to show this...
    # that's ok, they're only supposed to draw single-bond atypes anyway.
    """[should be called only from env.post_event_updates]
       This should be called at the end of every user event which might affect
    the atomtypes or bond-sets of any atoms or singlets, which are passed as the
    values of the dict changed_structure_atoms, which we should not modify
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
    whenever it thinks a more global update is needed, it will record this fact
    (and the affected atoms) so the user can be advised that a global bond-update is needed.
       It will assume that interpart bonds (if any) have already been broken.
    (#e Or we might decide to extend it to break them itself.)
    """
    bonds_to_fix = {}
    mols_changed = {} #bruce 060126, so atom._changed_structure() doesn't need to call atom.changed() directly
    
    for atm in changed_structure_atoms.values(): #bruce 060405 precaution: itervalues -> values, due to jig.changed_structure calls
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
            # WARNING: this might add new atoms to our argument dict, changed_structure_atoms
            # (and furthermore, we might depend on the fact that it does, for doing valence checks on them!)
            #060306 update: as of long before now, it stores these bonds in changed_bond_types.

    return # from _update_bonds_after_each_event

most_permissible_v6_first = ( V_SINGLE, V_DOUBLE, V_AROMATIC, V_GRAPHITE, V_TRIPLE, V_CARBOMERIC ) # not quite true for graphite?
    ####@@@@ review this -- all uses should be considered suspicious [050714 comment]

def best_corrected_v6(bond):
    """This bond has an illegal v6 according to its bonded atomtypes
    (and I guess the atomtypes are what has just changed?? ###k -- [update 060629:] NOT ALWAYS --
     it might be the bond order (and then the atomtypes), changed automatically by increase_valence_noupdate
     when the user bonds two bondpoints to increase order of existing bond, as in bug 1951).
    Say how we want to fix it (or perhaps fix the atomtypes?? #e [i doubt it, they might have just changed -- 060629]).
    """
    # Given that the set of permissible bond types (for each atomtype, ignoring S=S prohibition and special graphite rules)
    # is some prefix of [single, double, aromatic/graphite, triple, carbomeric],
    # I think it's ok to always take the last permissible element of that list (using relaxed rules for graphite)...
    # no, it depends on prior bond (presumably one the user likes, or at least consented to),
    # [note 060629 -- in bug 1951 the prior bond is carbomeric, but the user never wanted it, they just wanted to increase aromatic
    #  by 1, which numerically gets to carbomeric, but in that bug's example it's not a legal type and they really want double.
    #  So I will change the weird ordering of corrected_v6_list[V_CARBOMERIC] to a decreasing one, to fix that bug.]
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
    assert 0, "no legal replacement for v6 = %r in %r" % (v6,bond)
    return V_SINGLE

# map a now-illegal v6 to the list of replacements to try (legal ones only, of course; in the order of preference given by the list)
corrected_v6_list = {
    V_DOUBLE: (V_SINGLE,),
    V_TRIPLE: (V_DOUBLE, V_SINGLE),
    V_AROMATIC: (V_SINGLE,),
    V_GRAPHITE: (V_AROMATIC, V_SINGLE), # note: this temporarily goes up, then down.
    ## V_CARBOMERIC: (V_AROMATIC, V_DOUBLE, V_SINGLE), # there was a reason for this, but it caused bug 1951, so revising it [bruce 060629]
    V_CARBOMERIC: (V_DOUBLE, V_AROMATIC, V_SINGLE),
        # This monotonic decreasing order ought to fix bug 1951, though ideally we might depend on the last bond type
        # specifically chosen by the user... but at least, fractional bond orders never show up unless the user has one
        # somewhere on some other bond, so always including V_AROMATIC in this list might be ok,
        # even if the user never explicitly chose V_CARBOMERIC. [bruce 060629]
 }

# ==

def _process_changed_bond_types( changed_bond_types):
    """Tell whoever needs to know that some bond types changed.
    For now, that means only bond.pi_bond_obj objects on those very bonds.
    """
    for bond in changed_bond_types.values(): #bruce 060405 precaution: itervalues -> values, due to calls of code we don't control here
        obj = bond.pi_bond_obj
        if obj is not None:
            obj.changed_bond_type(bond)
    return

# dict for atoms or singlets whose element, atomtype, or set of bonds (or neighbors) gets changed [bruce 050627]
#e (doesn't yet include all killed atoms or singlets, but maybe it ought to)
# (changing an atom's bond type does *not* itself update this dict -- see changed_bond_types for that)

changed_structure_atoms = {} # maps atom.key to atom, for atoms or singlets
    # WARNING: there is also a related but different global dict in chem.py, whose spelling differs only in 'A' vs 'a' in Atoms.
    # See the comment there for more info. [bruce 060322]

changed_bond_types = {} # dict for bonds whose bond-type gets changed (need not include newly created bonds) ###k might not be used


# the beginnings of a general change-handling scheme [bruce 050627]

def _bond_updater_post_event_handler( warn_if_needed = False ):
    """
       This should be called at the end of every user event which might have changed
    anything in any loaded model which defers some updates to this function.
       This can also be called at the beginning of user events, such as redraws or saves,
    which want to protect themselves from event-processors which should have called this
    at the end, but forgot to. Those callers should pass warn_if_needed = True, to cause
    a debug-only warning to be emitted if the call was necessary. (This function is designed
    to be very fast when called more times than necessary.)
    """
    #bruce 060127: Note: as of long before now, nothing actually calls this with warn_if_needed = True;
    # the only calls are from GLPane.paintGL and assembly.update_parts.
    # FYI: As of 060127 I'll be calling update_parts (which always calls this method)
    # before every undo checkpoint (begin and end both), so that all resulting changes
    # from both of them (and the effect of calling assy.changed, now often done by this method as of yesterday)
    # get into the same undo diff.) [similar comment is in update_parts]
    #
    #obs? ####@@@@ call this from lots of places, not just update_parts like now; #doc is obs
    #
    #bruce 051011: some older experimental undo code I probably won't use:
##    for class1, classmethodname in _change_recording_classes:
##        try:
##            method = getattr(class1, classmethodname)
##            method() # this can update the global dicts here...
##                #e how that works will be revised later... e.g. we might pass an object to revise
##        except:
##            print "can't yet handle an exception in %r.%r, just reraising it" % (class1, classmethodname)
##            raise
##        pass
    if not (changed_structure_atoms or changed_bond_types):
        #e this will be generalized to: if no changes of any kind, since the last call
        return
    # some changes occurred, so this function needed to be called (even if they turn out to be trivial)
    if warn_if_needed and env.debug():
        # whichever user event handler made these changes forgot to call this function when it was done!
        print "atom_debug: post_event_updates should have been called before, but wasn't!" #e use print_compact_stack??
        pass # (other than printing this, we handle unreported changes normally)
    # handle and clear all changes since the last call
    # (in the proper order, when there might be more than one kind of change #nim)

    # NOTE: reloading won't work the way this code is currently
    # structured.  If reloading is needed, this routine needs to be
    # unregistered prior to the reload, and reregistered afterwards.
    # Also, note that the module would be reloading itself, so be
    # careful.
    #if changed_structure_atoms or changed_bond_types:
        #if 0 and platform.atom_debug: #bruce 060315 disabled this automatic reload (not needed at the moment)
            # during development, reload this module every time it's used
            # (Huaicai says this should not be done by default in the released version,
            #  due to potential problems if reloading from a zip file. He commented it
            #  out completely (7/14/05), and I then replaced it with this debug-only reload.
            #  [bruce 050715])
            #import bond_updater
            #reload(bond_updater)

    if changed_structure_atoms:
        _update_bonds_after_each_event( changed_structure_atoms)
            #bruce 060315 revised following comments:
            # this can modify changed_bond_types (from bond-inference in the future, or from correcting illegal bond types now).
            #e not sure if that routine will need to use or change other similar globals in this module;
            # if it does, passing just that one might be a bit silly (so we could pass none, or all affected ones)
        changed_structure_atoms.clear()
    if changed_bond_types: # warning: this can be modified by above loop which processes changed_structure_atoms...
        _process_changed_bond_types( changed_bond_types)
            ###k our interface to that function needs review if it can recursively add bonds to this dict -- if so, it should .clear
        changed_bond_types.clear()
    return


def initialize():
    env.register_post_event_handler(_bond_updater_post_event_handler)

# end
