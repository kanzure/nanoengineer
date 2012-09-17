# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
reposition_baggage.py -- help reposition baggage atoms after real neighbor
atoms have moved

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

import math

from utilities import debug_flags
from geometry.VQT import V, norm, cross, vlen
from model.bond_constants import find_bond
from model.bond_constants import V_SINGLE

from geometry.geometryUtilities import arbitrary_perpendicular

debugprints = False

# geometry of a tetrahedron (for finding sp3 bonding positions)
coef1, coef2 = norm( V( 1, math.sqrt(2) ) )
coef1 = - coef1

def reposition_baggage_0(self, baggage = None, planned_atom_nupos = None):
    """
    Your baggage atoms (or the given subset of them) might no longer
    be sensibly located, since you and/or some neighbor atoms have moved
    (or are about to move, re planned_atom_nupos as explained below),
    so fix up their positions based on your other neighbors' positions,
    using old baggage positions only as hints.

    BUT one of your other neighbors (but not self) might be about to move
    (rather than already having moved) -- if so,

      planned_atom_nupos = (that neighbor, its planned posn),

    and use that posn instead of its actual posn to decide what to do.

    @warning: we assume baggage is a subset of self.baggageNeighbors(),
              but we don't check this except when ATOM_DEBUG is set.
    """
    #bruce 060629 for bondpoint problem -- second guess what caller did so far
    if baggage is None:
        baggage, other = self.baggage_and_other_neighbors()
    else:
        other = -1 # set later if needed
        if debug_flags.atom_debug:
            # assert baggage is a subset of self.baggageNeighbors()
            _bn = map(id, self.baggageNeighbors())
            for atom in baggage:
                assert id(atom) in _bn
            atom = 0
            del _bn, atom

    _reposition_baggage_1(self, baggage, other, planned_atom_nupos)

    if self.element.pam and self.element.role in ('axis', 'strand'):
        # Let the dna updater 3rd-guess this when it has a DnaLadder and can
        # do a better job. REVIEW: are the things already done in _reposition_baggage_1
        # good or bad in this case? At least in most cases, they seem good (by testing).
        # [bruce 080404/080405 new feature / bugfix]
        self._f_dna_updater_should_reposition_baggage = True
        # do it immediately if possible
        ladder = getattr(self.molecule, 'ladder', None) ## self.molecule.ladder
        if ladder and ladder.valid and not ladder.error:
            # usual case, at least when dragging a real neighbor of self;
            # in these cases the dna updater is never running;
            # by test it's clear this is doing more good than harm, usually,
            # as of the late 080405 improvements to this method
            self.reposition_baggage_using_DnaLadder()
        else:
            # don't know if this ever happens
            # (it does happen for ghost bases created within ordinary chunks)
            self._changed_structure() # make sure dna updater runs on self
                # (probably NOT redundant with other changes by caller)
        pass
    return

def _reposition_baggage_1(self, baggage, other, planned_atom_nupos):
    """
    """
    # trivial cases
    len_baggage = len(baggage)
    if not len_baggage:
        return

    # cases handled well enough by calling code (as of 060629),
    # needing no correction here
    len_other = len(self.bonds) - len_baggage

    if not len_other:
        # should never happen, as we are called as of 060629, i think,
        # though if it did, there would be things we could do in theory,
        # like rotate atomtype.bondvecs to best match baggage...
        print "bug?: %r.reposition_baggage(%r) finds no other atoms -- " \
              "nim, not thought to ever happen" % (self, baggage)
        return

    if len_other == 1:
        # the Q(old, new) code in the callers ought to handle it properly --
        # UNLESS other is a pi_bond, and its alignment ought to affect a pair
        # of baggage atoms.
        if self.atomtype.spX == 2: # note: true for sp2 and sp2(graphitic)
            pass # let the main code run, including some other
                 # "if len_other == 1" scattered around
            ##e someday: don't we want to also notice sp, and propogate
             # twisting of a pi_bond through an sp_chain?
            # I recall some code in depositMode for that...
            # I can't remember its scope, thus whether it covers this already...
            # I think not. ###@@@
        else:
            return

    # at least 2 other (except sp2 pi_bond other), and at least one baggage...
    # might as well get other_posns we'll want to use
    # (handling planned_atom_nupos once and for all).
    if other == -1:
        other = []
        baggage_keys = [atom.key for atom in baggage]
        for b in self.bonds:
            atom = b.other(self)
            if atom.key not in baggage_keys:
                other.append(atom)
        if len(other) != len_other:
            # must mean baggage is not a subset of neighbors
            args = (self, baggage, planned_atom_nupos)
            print "bug in reposition_baggage%r: len(other == %r) != len_other %r" % \
                  (args, other, len_other)
            return
    if len_other == 1:
        other0_bond = find_bond(other[0], self)
        if other0_bond.v6 == V_SINGLE:
            # calling code handled this case well enough
            return
    planned_atom, nupos = None, None
    if planned_atom_nupos:
        planned_atom, nupos = planned_atom_nupos
        if planned_atom not in other:
            print "likely bug in reposition_baggage: " \
                  "planned_atom not in other", planned_atom, other
    other_posns = [(atom.posn(), nupos)[atom is planned_atom] for atom in other]
        #e we might later wish we'd kept a list of the bonds to baggage and
        # other, to grab the v6's -- make a dict from atom.key above?
    selfposn = self.posn()
    othervecs = [norm(pos - selfposn) for pos in other_posns]

    bag_posns = [atom.posn() for atom in baggage]
    bagvecs = [norm(pos - selfposn) for pos in bag_posns]

    # The alg is specific to atomtype, and number and sometimes *type* of all
    # bonds involved. We'll code the most important and/or easiest cases first.
    # Someday we might move them into methods of the atomtypes themselves.

    algchoice = (self.atomtype.spX, len_baggage, len_other)
        # len_baggage >= 1, len_other >= 2 (except pi_bond case)
    extra = 0 # might be altered below
    if algchoice == (3, 2, 2) or algchoice == (3, 1, 2):
        # (3, 2, 2) -- e.g. C(sp3) with 2 bp's and 2 real bonds
        # This is not the easiest case, but it's arguably the most important.
        # For alignment purposes we can assume bonds are single.
        # (Due to monovalent atoms being baggage, that doesn't mean the baggage
        #  atoms are equivalent to each other.)
        #
        # (3, 1, 2) -- e.g. N(sp3) with 1 bondpoint and 2 real bonds;
        # use same code and coefs, but pretend a phantom baggage atom is present
        if len_baggage == 1: # (3,1,2)
            extra = 1
            if debugprints:
                print "debug repos baggage: sp3,1,2"
        plane = cross( othervecs[0], othervecs[1] )
        if vlen(plane) < 0.001:
            # othervecs are nearly parallel (same or opposite);
            # could force existing bonds perp to them, at correct angle,
            # as close to existing posns as you can, but this case can be left
            # nim for now since it's rare and probably transient.
            if debugprints:
                print "debug repos baggage: othervecs are nearly parallel; " \
                      "this case is nim", self, other ###@@@
            return
        plane = norm(plane)
        back = norm(othervecs[0] + othervecs[1])
        res = [coef1 * back + coef2 * plane, coef1 * back - coef2 * plane]
        pass # fall thru to assigning res vecs to specific baggage
    elif algchoice == (3, 1, 3):
        back = norm(othervecs[0] + othervecs[1] + othervecs[2])
        if back:
            res = [-back]
            ##e might not be as good as averaging the three crossproducts,
            # after choosing their sign close to -back; or something better,
            # since real goal is just "be repelled from them all";
            # consider case where two othervecs are similar ###@@@
        else:
            plane0 = norm( cross( othervecs[0], othervecs[1] ))
            if plane0:
                if debugprints:
                    print "debug repos baggage: sp3 with 3 real bonds in a plane"
                # pick closest of plane0, -plane0 to existing posn
##                # one way:
##                if dot(plane0, bagvecs[0]) < 0:
##                    res = [-plane0]
##                else:
##                    res = [plane0]
                # another way:
                res = [-plane0, plane0]
                extra = 1
            else:
                # not possible -- if othervecs[0], othervecs[1] are antiparallel,
                # overall sum (in back) can't be zero; if parallel, ditto.
                print "can't happen: back and plane0 vanish", othervecs
                return
            pass
        pass
    elif algchoice == (2, 1, 2): # e.g. C(sp2) with 1 bondpoint and 2 real bonds
        back = norm(othervecs[0] + othervecs[1])
        if back:
            res = [-back] # tested
        else:
            # real bonds are antiparallel; find closest point on equator to
            # existing posn, or arb point on equator
            p0 = cross( bagvecs[0], othervecs[0] )
            if debugprints:
                print "debug repos baggage: antiparallel sp2 1 2 case, " \
                      "not p0 == %r" % (not p0) # untested so far
            if not p0:
                # bagvec is parallel too
                res = [arbitrary_perpendicular(othervecs[0])]
            else:
                # choose closest perpendicular to existing direction
                res0 = - norm( cross(p0, othervecs[0]) )
                #k this ought to be positive of, but might be (buggily)
                # negative of, desired value -- need to test this ###@@@
                # but being too lazy to test it, just make it work either way:
                res = [res0, -res0]
                extra = 1
            pass
        pass
    elif algchoice == (2, 2, 1):
        # This only matters for twisting a pi_bond, and we verified above that
        # we have >single bond. A difficulty: how can we update the geometry,
        # not knowing whether the caller moved all the source atoms yet,
        # and with the bond code not knowing which direction along the bond
        # effects are propogating?
        # BTW, I guess that when you drag singlets, depositMode implems this
        # (along sp_chains too), but when you move chain atoms (let alone
        # their neighbors), I just don't recall.
        if debugprints:
            print "debug repos baggage: sp2 with twisting pi_bond is nim", self ###@@@
        return
    else:
        #bruce 080515 bugfix: fallback case
        # (otherwise following code has UnboundLocalError for 'res')
        print "bug?: reposition_baggage (for %r) can't yet handle this algchoice:" % self, algchoice
        return
    # now work out the best assignment of posns in res to baggage; reorder res
    # to fit bags_ordered
    assert len(res) == len_baggage + extra
    bags_ordered = baggage # in case len(res) == 1
    if len(res) > 1:
        dists = []
        for atom_junk, vec, i in zip(baggage, bagvecs, range(len_baggage)):
            for pos in res:
                dists.append(( vlen(pos - vec), i, pos ))
        dists.sort()
        res0 = res
        res = []
        bags_ordered = []
        bagind_matched = [0 for bag in baggage]
        for dist, bagind, pos in dists:
            # assume not yet done matching, and don't yet know if bagind or pos
            # are still in the running;
            # when a bag matches, set bagind_matched[bagind];
            # when a pos matches, remove it from res0.
            if bagind_matched[bagind] or pos not in res0:
                continue
            # found a match
            res0.remove(pos)
            bagind_matched[bagind] = 1
            res.append(pos)
            bags_ordered.append(baggage[bagind])
            if len(bags_ordered) >= len_baggage:
                break
        assert len(bags_ordered) == len_baggage, \
               "somehow failed to match up some baggage at all, should never happen"
        assert len_baggage == len(res) # whether or not extra > 0
    # now move the atoms, preserving distance from self
    # (assume calling code got that part right)
    for atom, vec in zip(bags_ordered, res):
        dist = vlen( selfposn - atom.posn() )
        if abs(1.0 - vlen(vec)) > 0.00001:
            print "bug in reposition_baggage: vec not len 1:", vec
        atom.setposn( selfposn + norm(vec) * dist )
            # norm(vec) is hoped to slightly reduce accumulated
            # numerical errors...
            ###e ideally we'd correct the bond lengths too, but as of 060630,
            # even Build doesn't get them right (and it can't, unless bond tools
            #  would also change them when at most one real atom would need
            #  moving, which I suppose they ought to...)
    if debugprints and 0:
        print "done"
    return # from _reposition_baggage_1

# end... tested: sp3 2 2, sp2 1 2
# not tested: the others, the extreme cases
# (need try/except in practice since it's hard to test them all;
#  put it in calling code?)

