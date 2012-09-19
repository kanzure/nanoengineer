# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
bond_updater.py

Recompute structural bond orders when necessary.

@author: Bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

This is needed for bonds between atoms whose atomtypes make p orbitals
available for bonding, to check whether pi bonds are formed,
whether they're aromatic or double or triple, to check for
radicals (pi systems containing unpaired electrons),
and to notice graphite.

(Much of the above is not yet implemented.)

History:

bruce 050627 started this as part of supporting higher-order bonds.

bruce 071108 split out the general orchestration and registration
part of this into master_model_updater.py, leaving only the bond-
type- and atom-type- updating code in this file.
"""

from utilities.debug import print_compact_traceback

from model.bond_constants import V_SINGLE
from model.bond_constants import V_DOUBLE
from model.bond_constants import V_AROMATIC
from model.bond_constants import V_GRAPHITE
from model.bond_constants import V_TRIPLE
from model.bond_constants import V_CARBOMERIC

# ==

def update_bonds_after_each_event( changed_structure_atoms):
    """
    [should be called only from _master_model_updater, which is in turn
     called from env.do_post_event_updates]

    This should be called at the end of every user event which might affect
    the atomtypes or bond-sets of any atoms or singlets, which are passed as the
    values of the dict changed_structure_atoms, which we should not modify
    (and which no other code will modify while we use it). (As it happens,
    the caller will clear that dict after we return.)

    This function will either update, or record as needing update, the
    structural bond orders and associated data for all
    real atoms, real bonds, and open bonds which might be in pi systems
    (or which were, but aren't anymore).
    [And it might do more. #k if so, #doc that here.]

    Since it must be fast, it won't do work which leads it away from the actual
    atoms it's passed, and it will leave existing bond orders alone whenever
    they're locally consistent with the current atomtypes. That is, it will only
    act when there are local inconsistencies, and it will only fix them when
    this can be done on just the atoms it was passed (or their bonds), and in
    a reasonably unambiguous way; whenever it thinks a more global update is
    needed, it will record this fact (and the affected atoms) so the user can
    be advised that a global bond-update is needed.

    It will assume that interpart bonds (if any) have already been broken.
    (#e Or we might decide to extend it to break them itself.)
    """
    ###@@@ so far this is called by update_parts (eg mode chgs),
    # and near the start of a GLPane repaint event (should be enough),
    # and only when changed_structure_atoms is nonempty. #k
    # It misses hearing about killed atoms or singlets,
    # but does hear about atoms shown only in the elt selector thumbviews!
    # I guess the latter is good, since that way it can update the bond orders
    # in those views as well! However, debug tests showed that the elt selector
    # thumbviews need a separate redraw to show this... that's ok, they're only
    # supposed to draw single-bond atypes anyway.
    bonds_to_fix = {}
    mols_changed = {} #bruce 060126, so atom._changed_structure() doesn't need
        # to call atom.changed() directly

    for atm in changed_structure_atoms.values():
        #bruce 060405 precaution: itervalues -> values,
        # due to jig.changed_structure calls

        # ignore killed atoms
        # [bruce 071018 bugfix of old bug
        #  "reguess_atomtype of bondpoint with no bonds"]
        if atm._Atom__killed:
            # this inlines atm.killed() for speed, since this will happen a lot
            continue

##        if 'testing kluge':
##            #bruce 071117 -- see if this breaks any of our Python versions.
##            # update 071119: reported to work for Windows- python 2.4,
##            # OS X- python 2.3, Ubuntu- python2.5, so we can assume it
##            # works for all versions unless we find out otherwise.
##            # So this test code is now disabled unless further needed.
##            # I'm commenting it out entirely, so the import from chem can't
##            # mess up our import analysis. Once some real code relies on
##            # class-switching, we can remove this test code entirely.
##            # [bruce 071119]
##            from chem import Atom2, Atom
##            if atm.__class__ is Atom:
##                nc = Atom2
##            else:
##                nc = Atom
##            assert nc is not atm.__class__
##            atm.__class__ = nc
##            print "testing kluge, bruce 071117: set %s.__class__ to %s" % (atm, nc)
##            assert nc is atm.__class__

        # for singlets, just look at their base atoms
        # [I'm not sure where that comment shows up in the code, or whether the
        #  following comment was meant to be a change to it -- bruce 071115]

        # [as of 050707 just look at all bonds of all unkilled atoms]

        #e when info must be recorded for later, do this per-chunk or per-part.
        ##k Do we move existing such info when atoms moved or were killed??

        mol = atm.molecule # might be None or nullMol; check later
        mols_changed[id(mol)] = mol

        atype = atm.atomtype # make sure this is defined; also it will tell us
            # the permitted bond orders for any bond on this atom
        for bond in atm.bonds:
            v6 = bond.v6
            if v6 != V_SINGLE: # this test is just an optim
                if not atype.permits_v6(v6):
                    # this doesn't notice things like S=S (unstable), only the
                    # S= and =S parts (ok taken alone)
                    bonds_to_fix[id(bond)] = bond
                # SOMEDAY: also check legal endcombos for aromatic, graphite
                # (carbomeric?)
                # SOMEDAY: also directly check sp-chain-lengths here,
                # infer double bonds when odd length and connected, etc??

        # Tell perceived structures involving this atom that it changed.
        # (These will include sp-chains and pi-systems, and maybe more.
        #  For Alpha6, probably only sp-chains.)
        # For now, these are stored in jigs; one jig might contain just one
        # perceived structure, or all of one kind in one set of atoms
        # (the following code needn't know which).

        if atm.jigs: # most atoms have no jigs, so initial 'if' is worthwhile
            for jig in atm.jigs[:]: # list copy is necessary, see below
                try:
                    method = jig.changed_structure
                except AttributeError:
                    pass # initial kluge so I don't need to extend class Jig
                         #FIX
                else:
                    try:
                        method(atm)
                            # Note: this is permitted to destroy jig
                            # and (thereby) remove it from atm.jigs
                    except:
                        msg = "ignoring exception in jig.changed_atom(%r) " \
                              "for %r: " % (atm, jig)
                        print_compact_traceback( msg)
                continue

        # atom-valence checks can't be done until we fix illegal bond types,
        # below

        # comments about future atom-valence checks:
        #
        #e should we also check atypes against numbonds and total bond valence
        # (in case no bonds need fixing or they don't change)?
        # note: that's the only way we'll ever notice we need to increase any
        # bonds from single, on sp2 atoms!!!
        # Do we need to separately track needed reductions (from atypes)
        # or certainty-increases (A no longer allowed) or increases
        # (from atom valence)??
        # For certainty-increases, should we first figure out the rest before
        # seeing what to change them to? (guess: no, but not sure)
        #
        # (above cmts are obs, see paper notes about the alg)

    for mol in mols_changed.itervalues():
        if mol is not None:
            mol.changed() # should be safe for nullMol (but not for None)

    if not bonds_to_fix:
        return # optim [will be wrong once we have atom valence checks below]

    for bond in bonds_to_fix.itervalues():
        # every one of these bonds is wrong, in a direct local way
        # (ie due to its atoms)!
        # figure out what to change it to, and [someday] initiate our scan
        # of changes from each end of each bond.
        new_v6 = _best_corrected_v6(bond) ####@@@@ IMPLEM the rest of that...
            # actually this'll all be revised
        bond.set_v6(new_v6) #####@@@@@ ensure this calls _changed_structure
            # on both atoms -- WRONG, needs to call something different,
            # saying it changes bond orders but not bonds themselves
            # (so e.g. sp chains update geom but don't get destroyed).
            # [As of 050725 I think it doesn't do either of those.]
            # WARNING: this might add new atoms to our argument dict,
            # changed_structure_atoms (and furthermore, we might depend on
            # the fact that it does, for doing valence checks on them!)
            #060306 update: as of long before now, it stores these bonds
            # in changed_bond_types.

    return # from update_bonds_after_each_event

##most_permissible_v6_first = ( V_SINGLE, V_DOUBLE, V_AROMATIC, V_GRAPHITE,
##                              V_TRIPLE, V_CARBOMERIC )
##                            # not quite true for graphite?
##    # review this -- all uses should be considered suspicious [050714 comment]
##    # [this seems to be no longer used as of 071108...]

def _best_corrected_v6(bond):
    """
    This bond has an illegal v6 according to its bonded atomtypes
    (and I guess the atomtypes are what has just changed?? ###k --
     [update 060629:] NOT ALWAYS --
     it might be the bond order (and then the atomtypes),
     changed automatically by increase_valence_noupdate
     when the user bonds two bondpoints to increase order of
     existing bond, as in bug 1951).

    Say how we want to fix it (or perhaps fix the atomtypes?? #e
     [i doubt it, they might have just changed -- 060629]).
    """
    # Given that the set of permissible bond types (for each atomtype,
    # ignoring S=S prohibition and special graphite rules)
    # is some prefix of [single, double, aromatic/graphite, triple, carbomeric],
    # I think it's ok to always take the last permissible element of that list
    # (using relaxed rules for graphite)...
    # no, it depends on prior bond (presumably one the user likes, or at least
    # consented to),
    # [note 060629 -- in bug 1951 the prior bond is carbomeric, but the user
    #  never wanted it, they just wanted to increase aromatic
    #  by 1, which numerically gets to carbomeric, but in that bug's example
    #  it's not a legal type and they really want double.
    #  So I will change the weird ordering of _corrected_v6_list[V_CARBOMERIC]
    # to a decreasing one, to fix that bug.]
    # but clearly we move to the left in that list.
    # Like this: c -> a, 3 -> max in list? or 2?
    # or depends on other bonds/valences?
    # ... we might return a list of legal btypes in order of preference,
    # for inference code (see paper notes)

    v6 = bond.v6
    try:
        lis = _corrected_v6_list[v6]
    except KeyError:
        # this happens for illegal v6 values
        return V_SINGLE
    atype1 = bond.atom1.atomtype
        # fyi, see also possible_bond_types() for similar code
    atype2 = bond.atom2.atomtype
    for v6 in lis:
        if v6 == V_SINGLE or atype1.permits_v6(v6) and atype2.permits_v6(v6):
            return v6
    print "bug: no legal replacement for v6 = %r in %r" % (bond.v6, bond)
    return V_SINGLE

# map a now-illegal v6 to the list of replacements to try (legal ones only,
# of course; in the order of preference given by the list)
_corrected_v6_list = {
    V_DOUBLE: (V_SINGLE,),
    V_TRIPLE: (V_DOUBLE, V_SINGLE),
    V_AROMATIC: (V_SINGLE,),
    V_GRAPHITE: (V_AROMATIC, V_SINGLE),
        # note: this temporarily goes up, then down.
    ## V_CARBOMERIC: (V_AROMATIC, V_DOUBLE, V_SINGLE), # there was a reason
        # for this, but it caused bug 1951, so revising it [bruce 060629]
    V_CARBOMERIC: (V_DOUBLE, V_AROMATIC, V_SINGLE),
        # This monotonic decreasing order ought to fix bug 1951,
        # though ideally we might depend on the last bond type
        # specifically chosen by the user... but at least, fractional
        # bond orders never show up unless the user has one
        # somewhere on some other bond, so always including V_AROMATIC
        # in this list might be ok, even if the user never explicitly
        # chose V_CARBOMERIC. [bruce 060629]
 }

# ==

def process_changed_bond_types( changed_bond_types):
    """
    Tell whoever needs to know that some bond types changed.
    For now, that means only bond.pi_bond_obj objects on those very bonds.
    """
    for bond in changed_bond_types.values():
        #bruce 060405 precaution: itervalues -> values, due to calls of code
        # we don't control here
        obj = bond.pi_bond_obj
        if obj is not None:
            obj.changed_bond_type(bond)
    return

# end
