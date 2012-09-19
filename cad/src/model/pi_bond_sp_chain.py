# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
pi_bond_sp_chain.py -- geometric info for individual pi bonds, or chains
of them connected by sp atoms.

@author: bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

Note, 070414: it turns out a lot of the same concepts and similar code
ought to be useful for keeping track of chains of "directional bonds"
(such as pseudo-atom DNA backbones) in which direction-inference
and consistency checks should occur. Maybe I'll even create a general class
for perceiving bond-chains (or rings), with subclasses which know
about specific ways of recognizing bonds they apply to; or a class
whose instances hold bond-classifiers and act as perceivers of chains
of bonds of that type. (Once the chain is perceived, by generic code,
it does need specific code for its chain-type to figure out what to
do, though the basic fact of being destroyed when involved-atom-structure
changes is probably common. In the bond direction case, unlike in PiBondSpChain,
destroying the perceived strand will leave behind some persistent state,
namely the per-bond directions themselves; the perceived strand's role
is to help change those directions in an organized way.)
"""

import math
from numpy.oldnumeric import dot

from utilities import debug_flags
from model.jigs import Jig
from geometry.VQT import V, Q, A, cross, vlen, norm, twistor_angle

from operations.bond_chains import grow_bond_chain

from model.bond_constants import V_SINGLE
from model.bond_constants import V_DOUBLE
from model.bond_constants import V_TRIPLE
from model.bond_constants import V_AROMATIC
from model.bond_constants import V_GRAPHITE
from model.bond_constants import V_CARBOMERIC

DFLT_OUT = V(0.0, -0.6, 0.8) # these are rotated from standard out = V(0,0,1), up = V(0,1,0) but still orthonormal
DFLT_UP =  V(0.0,  0.8, 0.6)

# _recompile_counter is useful for development, and is harmless otherwise
try:
    _recompile_counter
except:
    _recompile_counter = 1
else:
    # increment the counter only when the module got recompiled, not just when it got reloaded from the same .pyc file
    if __file__.endswith(".py"):
        _recompile_counter += 1
        print "_recompile_counter incremented to", _recompile_counter
    else:
        pass ## print "_recompile_counter unchanged at", _recompile_counter
    pass

def bond_get_pi_info(bond, **kws):
    """
    #doc; **kws include out, up, abs_coords
    """
    obj = bond.pi_bond_obj
    if obj is not None:
        # let the obj update itself and return the answer.
        # (I think this should always work, since it gets invalled and can remove itself as needed.
        #  If not, it must resort to similar code to remainder of this routine,
        #  since it can't return anything here to tell this routine to do that for it.)
        if obj._recompile_counter != _recompile_counter:
            # it would not be good to do this except when the module got recompiled due to being modified
            # (ie not merely when it got reloaded), since that would defeat persistence of these objects, which we need to debug
            print "destroying %r of obsolete class" % obj # happens when we reload this module at runtime, during development
            obj.destroy()
            obj = None
    # special case for triple bonds [bruce 050728 to fix bug 821]: they are always arbitrarily oriented and not twisted
    if bond.v6 == V_TRIPLE:
        return pi_vectors(bond, **kws)
    # not worth optimizing for single bonds, since we're never called for them for drawing,
    # and if we're called for them when depositing sp2-sp-sp2 to position singlets on last sp2,
    # it would not even be correct to exclude them here!
    if obj is not None:
        return obj.get_pi_info(bond, **kws) # no need to pass an index -- that method can find one on bond if it stored one
    # if the obj is not there, several situations are possible; we only store an obj if the pi bond chain length is >1.
    if not bond.potential_pi_bond():
        return None # note, this does *not* happen for single bonds, if they could in principle be changed to higher bond types
    if pi_bond_alone_in_its_sp_chain_Q(bond):
        # optimize this common case, with simpler code and by not storing an object for it
        # (since too many atoms would need to invalidate it)
        return pi_vectors(bond, **kws)
    obj = bond.pi_bond_obj = make_pi_bond_obj(bond) # make an obj that updates itself as needed when atoms/bonds change or move
    return obj.get_pi_info(bond, **kws)

class PerceivedStructureType(Jig): #e rename, not really a Type (eg not a pattern), more like a set or layer or record
    """
    ... Subclasses are used for specific kinds of perceived structures
    (e.g. sp chains, pi systems, diamond or graphite rings).
    """
    pass

#bruce 060223: How will we (PiBondSpChain) deal with Undo? We could just store every attr in this object, but we don't want to bother.
# We want to think of it as entirely derived from other state (as it in fact is). So if things change, we'd rather invalidate it
# and start over. In theory that should be ok, provided Undo (when changing other atoms & bonds) invals them in all the same
# ways their LL change methods would do, including telling this object they changed (which makes it destroy itself).
# Since this is a Jig, it will at least participate in Jigs' scheme for having atom lists and being on atoms' jig lists,
# and Undo ought to properly handle that... how does that interact with our own policy of destroying ourself as soon as some atom
# we're interested in says it changed? Could that happen with atom->jig and jig->atom connections not yet corresponding?
# Solution to that worry: first let Undo do all its setattrs (so atom->jig and jig->atom connections have all been changed),
# then call all object updaters at once. Ours is our superclass's and does nothing (I think); the one on the first atom we
# encounter will destroy us; this will remove us from an atom's jig list but that should not (I think) invalidate the atom,
# since those are really just "back pointers" rather than properties of the atom (if it did inval it, that would be bad, I think --
# maybe not, since _undo_update is really an inval method and those can in general call other inval methods).
#  So if Atom & Bond _undo_updates are correct, we should be ok. If not, some bugs will be noticed at some point.
#
# One other thing: we're a Jig, but we're not in the node tree (which is why we don't get into mmp files). So Undo will not find us
# as a child object. We'll still get an objkey (I think)... hmm, this might be a problem, since when restoring some atom->jig to us,
# it won't restore our pointer to that atom. Can that ever happen (in light of our atomset being fixed)? I don't know. I think this
# might indeed cause bugs, so we might need to get counted as a child, or be some new undo-kind of object that easily gets
# invalidated by any _undo_update on atoms it touches (maybe we introduce "subscribe to another obj's _undo_update" or to their
# specific attrs?). I think it's easiest to wait and see if bugs happen. If they do, that subscription idea sounds best to me.
# CHANGED MY MIND, I'll just make us an S_CHILD of our bonds... then our atomset should be ok, and we could have _undo_update
# notice it changing too, if we wanted to. Let's do that for safety (maybe we'll never know if it was needed).
# ###@@@

class PiBondSpChain(PerceivedStructureType):
    """
    Records one chain (or ring) of potential-pi-bonds connected by -sp- atoms;
    as a Jig, sits on all atoms whose structure or motion matters for the extent of this chain
    and the geometry of its pi orbitals (ie all atoms in the chain, and the immediate neighbor atoms of the ends).
       Main job is to calculate pi-orbital angles for drawing the pi bonds.
        Someday we might extend this to also infer bond types along the chain, etc.
    """
    ringQ = False # class constant; in the Ring subclass, this is True
    have_geom = False # initial value of instance variable
    def _undo_update(self): #bruce 060223; see long comment above
        """
        our atomset (a member of our superclass Jig) must have changed...
        """
        self.destroy()
        PerceivedStructureType._undo_update(self) # might be pointless after that, but you never know...
        return
    def __init__(self, listb, lista): ### not like Jig init, might be a problem eg for copying it ###@@@ review whether that happens
        """
        Make one, from lists of bonds and atoms (one more atom than bond,
        even for a ring, where 1st and last atoms are same)
        """
        self._recompile_counter = _recompile_counter
        self.listb = listb
        self.lista = lista
        assert len(lista) == 1 + len(listb)
        assert len(listb) > 0
        #e could assert each bond's atoms are same as prior and next corresponding atom in lista
        # now add ourselves into each bond, exclusively (for cleaner code, this should be a separate method, called by init caller #e)
        for i, bond in zip( range(len(listb)), listb ):
            if bond.pi_bond_obj is not None:
                if debug_flags.atom_debug:
                    print "atom_debug: bug: obs pi_bond_obj found (and discarded) on %r" % (bond,)
                bond.pi_bond_obj.destroy()
            bond.pi_bond_obj = self
            bond.pi_obj_memo = i
            # now inval bond?? no, that would be wrong -- this func is part of updating it after smth else invalled it earlier.
        # figure out which atoms we need to monitor, for invalidating our geometric info or our structure.
        all_atoms = list(lista) # atoms in the chain, plus neighbor atoms whose posns matter
        assert len(lista) >= 2
        end1 = lista[0]
        end2 = lista[-1]
        if end1 is not end2: # not a ring
            nn = end1.neighbors()
            nn.remove(lista[1])
            all_atoms.extend(nn) # order doesn't matter
            nn = end2.neighbors()
            nn.remove(lista[-2])
            all_atoms.extend(nn)
        assy = all_atoms[0].molecule.assy #e need to zap the need for assy from Node
        PerceivedStructureType.__init__(self, assy, all_atoms)
        return
    super = PerceivedStructureType # needed for this to work across reloads
    listb = () # permit repeated destroy [bruce 060322]
    _recompile_counter = None # ditto (not sure if needed)
    def destroy(self):
        super = self.super
        for bond in self.listb:
            self.listb = () #bruce 060322 to save RAM (might not be needed)
            if bond.pi_bond_obj is self:
                bond.pi_bond_obj = None
                bond.pi_obj_memo = None # only needed to cause an exception if something tries to misuse it
            elif bond.pi_bond_obj is not None:
                if debug_flags.atom_debug:
                    print "atom_debug: bug: wrong pi_bond_obj %r found (not changed) on %r as we destroy %r" % (bond.pi_bond_obj, bond, self)
        super.destroy(self)
    def changed_structure(self, atom):
        # ideally this should react differently to neighbor atoms and others; but even neighbors might be brought in, eg C(sp3)-C#C;
        # so it's simplest for now to just forget about it and rescan for it when next needed.
        self.destroy() ###k need to make sure it's ok for jigs (Nodes) not in the model tree
        # no point in calling super.changed_structure after self.destroy!
    def moved_atom(self, atom):
        """
        some atom I'm on moved; invalidate my geometric info
        """
        # must be fast, so don't bother calling Jig.moved_atom, since it's a noop
        self.have_geom = False
    def changed_bond_type(self, bond): #bruce 050726
        """
        some bond I'm on changed type (perhaps due to user change
        or to bond inference code); invalidate my geometric info
        """
        # there is no superclass method for this -- it's only called on bond.pi_bond_obj for our own bonds
        ###e it might be worth only invalidating if the bond type differs from what we last used when recomputing
        self.have_geom = False        
    def get_pi_info(self, bond, out = DFLT_OUT, up = DFLT_UP, abs_coords = False):
        if len(self.listb) == 1:
            if debug_flags.atom_debug:
                print "atom_debug: should never happen (but should work if it does): optim for len1 PiBondSpChain object %r" % self
            return pi_vectors(self.listb[0], out = out, up = up, abs_coords = abs_coords)
                # optimization; should never happen since it's done instead of creating this object
        if not self.have_geom:
            self.recompute_geom(out = out, up = up) # always in abs coords
            self.have_geom = True
        ind = bond.pi_obj_memo # this was stored again whenever our structure changed (for now, only in init)
        assert type(ind) == type(1)
        assert 0 <= ind < len(self.listb)
        assert self.listb[ind] is bond
        biL_pvec, biR_pvec = self.pvecs_i( ind, abs_coords = True)
            #bruce 050727 -- abs_coords arg was used both here & below -- wrong, using True here is right (so I fixed it),
            # but I didn't yet see any effect from that presumed bug. It might be that the chunk quat is
            # always Q(1,0,0,0) whenever the pi_info gets updated.
        bond_axis = self.axes[ind]
            ## bond_axis = self.lista[ ind+1 ].posn() - self.lista[ ind ].posn() # order matters, i think
        if bond.atom1 is self.lista[ind]:
            assert bond.atom2 is self.lista[ind+1]
        else:
            # flipped
            assert bond.atom1 is self.lista[ind+1]
            assert bond.atom2 is self.lista[ind]
            bond_axis = - bond_axis
            biL_pvec, biR_pvec = biR_pvec, biL_pvec
        return pi_info_from_abs_pvecs( bond, bond_axis, biL_pvec, biR_pvec, abs_coords = abs_coords) 

    def pvecs_i(self, i, abs_coords = False):
        """
        Use last recomputed geom to get the 2 pvecs for bond i...
        in the coordsys of the bond, or always abs if flag is passed.
        WARNING: pvec order matches atom order in lista, maybe not in bond.
        """
        biL_pvec = biR_pvec = self.quats_cum[i].rot(self.b0L_pvec) # not yet twisted
        axis = self.axes[i]
##        if self.twist90 and i % 2 == 1:
##            biL_pvec = norm(cross(biL_pvec, axis))
##            biR_pvec = norm(cross(biR_pvec, axis))
        twist = self.twist # this is the twist angle (in radians), for each bond; or None or 0 or 0.0 for no twist
        if twist:
            # twist that much times i and i+1 for L and R, respectively, around axes[i]
            theta = twist
            quatL = Q(axis, theta * (i))
            quatR = Q(axis, theta * (i+1))
            biL_pvec = quatL.rot(biL_pvec)
            biR_pvec = quatR.rot(biR_pvec)
        if not abs_coords:
            # put into bond coords (which might be the same as abs coords)
            bond = self.listb[i]
            quat = bond.bond_to_abs_coords_quat()
            biL_pvec = quat.unrot(biL_pvec)
            biR_pvec = quat.unrot(biR_pvec)
        return biL_pvec, biR_pvec # warning: these two vectors might be the same object

    def recompute_geom(self, out = DFLT_OUT, up = DFLT_UP):
        """
        Compute and store enough geometric info for pvecs_i to run (using submethods for various special cases):
        self.quats_cum, self.twist, self.b0L_pvec.
        """
        # put coords on each bond axis, then link these (gauge transform)... start with first and propogate.
        # warning: each bond in turn might have a different coordinate system!
        # (if they alternate external/internal, different chunks)
        # and the geom we compute for each bond should be in that bond's system, to help draw it properly.
        # fortunately they're only linked by rotations... so we should be able to compensate for coord changes.
        # This also means -- when a bond is invalidated, it might be from changing its coord sys, even if no atom motion
        # or structure change. This needs to invalidate it here, too, or (more simply) inval this whole thing.
        # or we could let the pi info be in abs coords and rotate the vecs before use?
        # yes, this is effectively what we ended up doing, except even the abs coords get computed each time they're asked for
        # from the quats stored by this routine.
        
        self.twist = None # default value
        self.axes = self.quats_cum = self.chain_quat_cum = None # invalid values (for catching bugs)

        bonds = self.listb
        lista = self.lista
        
##        # first, do we want that 90-deg offset? Only if double bonds, I think.
##        # (It's just a kluge to avoid returning pi orders of (1,0) for some of them and (0,1) for the others.
##        #  We use it so we can return pi orders of (1,0) for all double bonds.)
##        #
##        # Let's assume bond inference was done, so if one bond is double, they all are.
##        # BUT WAIT, are all the middle atoms C(sp), not some other element?? I think so... ###@@@  check this somewhere,
##        #  and if another is poss, probably don't even make it form a chain like this
##        self.twist90 = ( bonds[0].v6 == V_DOUBLE )

        posns = A( map( lambda atom: atom.posn(), lista ) )
        self.axes = axes = posns[1:] - posns[:-1] # axes along bonds, all in consistent directions & abs coords
        quats_incr = map( lambda (axis1, axis2): Q(axis1, axis2), zip( axes[:-1], axes[1:] ) )
            # how to transform vectors perp to one bond, to those perp to the next
        # cumulative quats (there might be a more compact python notation for this, and/or a way to do more of it in Numeric)
        qq = Q(1,0,0,0)
        quats_cum = [qq] # how to get from bonds[0] to each bonds[i] starting from i == 0, using only bend-projections at atoms
        for qi, i in zip( quats_incr, range(len(quats_incr)) ):
            # qi tells us how to map (perps to axes[i]) to (perps to axes[i+1])
            qq = qq + qi # make a new quat, don't use +=
            ###e ideally we'd now enforce qq turning axes[0] into axes[i], to compensate for cumulative small errors [nim]
            if self.adjacent_double_bonds( i, i+1 ):
                axis = axes[i+1]
                theta = math.pi / 2 # 90 degrees
                qq += Q(axis, theta)
            quats_cum.append(qq)
        assert len(quats_cum) == len(bonds)
        self.quats_cum = quats_cum
        self.chain_quat_cum = quats_cum[-1]
        if self.ringQ:
            # for rings we need to know how to get all the way around the ring, ie from bonds[-1] to bonds[0]
            # (but we won't add these quats to our lists)
            self.ringquat_incr = Q( axes[-1], axes[0] )
            if self.adjacent_double_bonds( -1, 0 ):
                self.ringquat_incr += Q(axes[0], math.pi / 2)
            ## self.ringquat_cum = self.chain_quat_cum + self.ringquat_incr #k probably not used
        # now we know total twist, so we can use code similar to   pi_vectors   function to decide what to do at the ends.
        # BTW all this only mattered if we weren't alternating single-triple bonds... ideally we'd rule that out first.
        # but no harm if we don't.
        # BTW2, at what point should this code do any bond-type inference? and how -- should it take most recently user-changed
        # bond in it, or most recently inferred end-bond, and propogate that, in some cases? btw3, remember it might be a ring.

        # call subclass-specific funcs to do the rest -- compute the twist and start/end p orbital vectors, used later by pvecs_i...
        self.out = out
        self.up = up
        self.recompute_geom_from_quats()
        return # from recompute_geom

    def adjacent_double_bonds( self, i1, i2 ): # replaces self.twist90 code, 050726
        """
        #doc;
        i1 might be -1
        """
        bonds = self.listb
        v1 = bonds[i1].v6 # ok for negative indices i1
        v2 = bonds[i2].v6
        #bruce 050728 kluge bugfix: treat V_SINGLE as V_DOUBLE so this gives user benefit of the doubt if they
        # just haven't yet bothered to put in the correct bondtypes, and so this works from depositmode growing an sp chain
        # when it's making new singlets on an sp2 atom it deposits at the end of the sp chain.
        if v1 == V_SINGLE:
            v1 = V_DOUBLE
        if v2 == V_SINGLE:
            v2 = V_DOUBLE
        # if both are double, or one is double and one is aromatic or graphite (but not carbomeric)
        if v1 == V_DOUBLE and v2 in (V_DOUBLE, V_AROMATIC, V_GRAPHITE):
            return True
        if v2 == V_DOUBLE and v1 in (V_AROMATIC, V_GRAPHITE):
            return True
        return False
    
    def recompute_geom_from_quats(self): # non-ring class
        """
        [not a ring; various possible end situations]
        """
        out = self.out
        up = self.up
        atoms = self.lista
        bonds = self.listb
            # (I wish I could rename these attrs to "atoms" and "bonds",
            #  but self.atoms conflicts with the Jig attr, and self.chain_atoms is too long.)
        # default values:
        self.bm1R_pvec = "not needed" # and bug if used, we hope, unless we later change this value
        self.twist = None
        # Figure out p vectors for atom[0]-end (left end) of bond[0], and atom[-1]-end (right end) of bond[-1].
        # If both are determined from outside this chain (i.e. if the subrs here don't return None),
        # or if we are a ring (so they are forced to be the same, except for the projection due to bond bending at the ring-joining atom),
        # then [using self.recompute_geom_both_ends_constrained()] they must be made to match (up to an arbitrary sign),
        # using a combination of some twist (to be computed here) along each bond,
        # plus a projection and (in some cases, depending on bond types i think -- see self.twist90)
        # 90-degree turn at each bond-bond connection;
        # the projection part for all the bond-bond connections is already accumulated in self.chain_quat_cum.
        
        # note: the following p-vec retvals are in abs coords, as they should be
        #e rename the funcs, since they are not only for sp2, but for any atom that ends our chain of pi bonds
        pvec1 = p_vector_from_sp2_atom(atoms[0], bonds[0], out = out, up = up) # might be None
        pvec2 = p_vector_from_sp2_atom(atoms[-1], bonds[-1], out = out, up = up) # ideally, close to negative or positive of pvec1 ###@@@ handle neg
        # handle one being None (use other one to determine the twist) or both being None (use arb vectors)
        if pvec1 is None:
            if pvec2 is None:
                # use arbitrary vectors on left end of bonds[0], perp to bond and to out; compute differently if bond axis ~= out
                axis = self.axes[0]
                pvec = cross(out, axis)
                lenpvec = vlen(pvec)
                if lenpvec < 0.01:
                    # bond axis is approx parallel to out
                    pvec = cross(up, axis)
                    lenpvec = vlen(pvec) # won't be too small -- bond can't be parallel to both up and out
                pvec /= lenpvec
                self.b0L_pvec = pvec
            else:
                # pvec2 is defined, pvec1 is not. Need to transport pvec2 back to coords of pvec1
                # so our standard code (pvec_i, which wants pvec1, i.e. self.b0L_pvec) can be used.
                self.b0L_pvec = self.chain_quat_cum.unrot(pvec2)
        else:
            if pvec2 is None:
                self.b0L_pvec = pvec1
            else:
                # both vectors not None -- use recompute_geom_both_ends_constrained
                self.b0L_pvec = pvec1
                self.bm1R_pvec = pvec2
                self.recompute_geom_both_ends_constrained()
        return # from non-ring recompute_geom_from_quats

    def recompute_geom_both_ends_constrained(self):
        """
        Using self.b0L_pvec and self.chain_quat_cum and self.bm1R_pvec,
        figure out self.twist...
        [used for rings, and for linear chains with both ends constrained]
        """
        bonds = self.listb
        # what pvec would we have on the right end of the chain, if there were no per-bond twist?
        bm1R_pvec_no_twist = self.chain_quat_cum.rot( self.b0L_pvec ) # note, this is a vector perp to bond[-1]
        axism1 = self.axes[-1]
        # what twist is needed to put that vector over the actual one (or its neg), perhaps with 90-deg offset?
        i = len(bonds) - 1
##        if self.twist90 and i % 2 == 1:
##            bm1R_pvec_no_twist = norm(cross(axism1, bm1R_pvec_no_twist))
        # use negative if that fits better
        if dot(bm1R_pvec_no_twist, self.bm1R_pvec) < 0:
            bm1R_pvec_no_twist = - bm1R_pvec_no_twist
        # total twist is shared over every bond
        # note: we care which direction we rotate around axism1
        total_twist = twistor_angle( axism1, bm1R_pvec_no_twist, self.bm1R_pvec)
            # in radians; angular range is undefined, for now
            # [it's actually +- 2pi, twice what it would need to be in general],
            # so we need to coerce it into the range we want, +- pi/2 (90 degrees); here too we use the fact
            # that in this case, a twist of pi (180 degrees) is the same as 0 twist.
        while total_twist > math.pi/2:
            total_twist -= math.pi
        while total_twist <= - math.pi/2:
            total_twist += math.pi
        self.twist = total_twist / len(bonds)
        return

    pass # end of class PiBondSpChain

class RingPiBondSpChain( PiBondSpChain):
    """
    Class for a perceived ring of =C= or -C# atoms,
    or other 2-bond sp atoms if there are any
    (not sure if there can be)
    """
    ringQ = True
    # Note: I've assumed a ring means no constraints on angles... what if other bonds? but sp2 atoms count as endpoints,
    # so it's ok, this is just ring of sp, so it's true.
    def recompute_geom_from_quats(self): # ring class
        # get arb p-vector for use at bond[-1] right end
        self.bm1R_pvec = arb_perp_unit_vector(self.axes[-1])
        # then project that through ring-joining-atom to a pvec for use at bond[0] left end
        self.b0L_pvec = self.ringquat_incr.rot(self.bm1R_pvec)
        # then use same code as non-ring with constrained pvecs
        self.recompute_geom_both_ends_constrained( ) # fyi: one of several methods to finish up; chains can use this one or others
        return
    pass # end of class RingPiBondSpChain

def make_pi_bond_obj(bond): # see also find_chain_or_ring_from_bond, which generalizes this [bruce 071126]
    """
    #doc ...
    make one for a pi bond, extended over sp atoms in the middle...
    what if sp3-sp-sp3, no pi bonds? then no need for one!
    """
    atom1 = bond.atom1
    atom2 = bond.atom2
    # more atoms to the right? what we need to grow: sp atom, exactly one other bond, it's a pi bond. (and no ring formed)
    ringQ, listb1, lista1 = grow_pi_sp_chain(bond, atom1)
    if ringQ:
        assert atom2 is lista1[-1]
        return RingPiBondSpChain( [bond] + listb1 , [atom2, atom1] + lista1 )
    ringQ, listb2, lista2 = grow_pi_sp_chain(bond, atom2)
    assert not ringQ
    listb1.reverse()
    lista1.reverse()
    return PiBondSpChain( listb1 + [bond] + listb2, lista1 + [atom1, atom2] + lista2 ) # one more atom than bond

def sp_atom_2bonds(atom):
    """
    """
    ## warning: this being true is *not* enough to know that a pi bond containing atom has an sp-chain length > 1.
    return atom.atomtype.is_linear() and len(atom.bonds) == 2 and atom.atomtype.numbonds == 2

def next_bond_in_sp_chain(bond, atom):
    """
    Given a pi bond and one of its atoms, try to grow the chain
    beyond that atom... return next bond, or None.

    @note: This function not returning None (for either atom on the end
    of a potential pi bond) is the definitive condition for that bond
    not being the only one in its sp-chain.
    """
    assert bond.potential_pi_bond()
    if not sp_atom_2bonds(atom):
        return None #k retval
    bonds = atom.bonds
    # len(bonds) == 2, known from subr conds above
    if bond is bonds[0]:
        obond = bonds[1]
    else:
        assert bond is bonds[1]
        obond = bonds[0]
    if obond.potential_pi_bond():
        return obond
    return None

def pi_bond_alone_in_its_sp_chain_Q(bond):
    return next_bond_in_sp_chain(bond, bond.atom1) is None and next_bond_in_sp_chain(bond, bond.atom2) is None

def grow_pi_sp_chain(bond, atom): # WARNING: superceded by grow_pi_sp_chain_NEWER_BETTER, except that one is untested. see its comment.
    """
    Given a potential pi bond and one of its atoms,
    grow the pi-sp-chain containing bond in the direction of atom,
    adding newly found bonds and atoms to respective lists (listb, lista) which we'll return,
    until you can't or until you notice that it came back to bond and formed a ring
    (in which case return as much as possible, but not another ref to bond or atom).
       Return value is the tuple (ringQ, listb, lista) where ringQ says whether a ring was detected
    and len(listb) == len(lista) == number of new (bond, atom) pairs found.
    """
    listb, lista = [], []
    origbond = bond # for detecting a ring
    while 1:
        nextbond = next_bond_in_sp_chain(bond, atom) # this is the main difference from grow_bond_chain
        if nextbond is None:
            return False, listb, lista
        if nextbond is origbond:
            return True, listb, lista
        nextatom = nextbond.other(atom)
        listb.append(nextbond)
        lista.append(nextatom)
        bond, atom = nextbond, nextatom
    pass

def grow_pi_sp_chain_NEWER_BETTER(bond, atom):
    #bruce 070415 -- newer & better implem of grow_pi_sp_chain (equiv,
    # but uses general helper func), but untested. Switch to this one when there's time to test it.
    return grow_bond_chain(bond, atom, next_bond_in_sp_chain)

# ==

def pi_vectors(bond, out = DFLT_OUT, up = DFLT_UP, abs_coords = False): # rename -- pi_info for pi bond in degen sp chain
    # see also PiBondSpChain.get_pi_info
    """
    Given a bond involving some pi orbitals, return the 4-tuple ((a1py, a1pz), (a2py, a2pz), ord_pi_y, ord_pi_z),
    where a1py and a1pz are orthogonal vectors from atom1 giving the direction of its p orbitals for use in drawing
    this bond (for twisted bonds, the details of these might be determined more by graphic design issues than by the
    shapes of the real pi orbitals of the bond, though the goal is to approximate those);
    where a2py and a2pz are the same for atom2 (note that a2py might not be parallel to a1py for twisted bonds);
    and where ord_pi_y and ord_pi_z are order estimates (between 0.0 and 1.0 inclusive) for use in drawing the bond,
    for the pi_y and pi_z orbitals respectively. Note that the choice of how to name the two pi orbitals (pi_y, pi_z)
    is arbitrary and up to this function.
       All returned vectors are in the coordinate system of bond, unless abs_coords is true.
       This should not be called for pi bonds which are part of an "sp chain",
    but it should be equivalent to the code that would be used for a 1-bond sp-chain
    (i.e. it's an optimization of that code, PiBondSpChain.get_pi_info, for that case).
    """
    atom1 = bond.atom1
    atom2 = bond.atom2
    bond_axis = atom2.posn() - atom1.posn() #k not always needed i think
    # following subrs should be renamed, since we routinely call them for sp atoms,
    # e.g. in -C#C- where outer bonds are not potential pi bonds
    pvec1 = p_vector_from_sp2_atom(atom1, bond, out = out, up = up) # might be None
    pvec2 = p_vector_from_sp2_atom(atom2, bond, out = out, up = up) # ideally, close to negative or positive of pvec1
    # handle one being None (use other one in place of it) or both being None (use arb vectors)
    if pvec1 is None:
        if pvec2 is None:
            # use arbitrary vectors perp to the bond; compute differently if bond_axis ~= out [###@@@ make this a subr? dup code?]
            pvec = cross(out, bond_axis)
            lenpvec = vlen(pvec)
            if lenpvec < 0.01:
                pvec = up
            else:
                pvec /= lenpvec
            pvec1 = pvec2 = pvec
        else:
            pvec1 = pvec2
    else:
        if pvec2 is None:
            pvec2 = pvec1
        else:
            # both vectors not None -- use them, but negate pvec2 if this makes them more aligned
            if dot(pvec1, pvec2) < 0:
                pvec2 = - pvec2
    return pi_info_from_abs_pvecs( bond, bond_axis, pvec1, pvec2, abs_coords = abs_coords) 

def pi_info_from_abs_pvecs( bond, bond_axis, pvec1, pvec2, abs_coords = False):
    """
    #doc;
    bond_axis (passed only as an optim) and pvecs are in abs coords; retval is in bond coords unless abs_coords is true
    """
    a1py = pvec1
    a2py = pvec2
    a1pz = norm(cross(bond_axis, pvec1))
    a2pz = norm(cross(bond_axis, pvec2))
    ord_pi_y, ord_pi_z = pi_orders(bond)
    if not abs_coords:
        # put into bond coords (which might be the same as abs coords)
        quat = bond.bond_to_abs_coords_quat()
        a1py = quat.unrot(a1py)
        a2py = quat.unrot(a2py)
        a1pz = quat.unrot(a1pz)
        a2pz = quat.unrot(a2pz)
    return ((a1py, a1pz), (a2py, a2pz), ord_pi_y, ord_pi_z)

def pi_orders(bond):
    try:
        ord_pi_y, ord_pi_z = pi_order_table[bond.v6]
    except:
        if debug_flags.atom_debug:
            print "atom_debug: bug: pi_order_table[bond.v6] for unknown v6 %r in %r" % (bond.v6, bond)
        ord_pi_y, ord_pi_z = 0.5, 0.5 # this combo is not otherwise possible
    return ord_pi_y, ord_pi_z

pi_order_table = {
V_SINGLE:   (0,    0),
V_DOUBLE:   (1,    0), # choice of 1,0 rather than 0,1 is just a convention, but we always use it even for =C=C=C= chains
V_TRIPLE:   (1,    1),
V_AROMATIC: (0.5,  0),
V_GRAPHITE: (0.33, 0),
V_CARBOMERIC: (0.5, 1), # I think the 0.5 should actually be 1-x for adjacent bonds of order x, so it's wrong for graphite ###e
}

# ==
        
def p_vector_from_sp2_atom(atom, bond, out = DFLT_OUT, up = DFLT_UP):
    """
    Given an sp2 atom and a possibly-pi bond to it,
    return its p orbital vector for use in thinking about that pi bond,
    or None if this atom (considering its other bonds) doesn't constrain that direction.
    """
    if not atom.atomtype.is_planar():
        return None # helps make initial stub code simpler
    nbonds = len(atom.bonds)
    if nbonds == 3:
        # we can determine atom's p vector (there is only one) from those bonds
        # (no need to check atomtype -- it can't be sp, and if it was sp3 we should not have been called;
        #  and in case of errors or bugs, maybe the type is not sp2 as we hope, but this code will still "work".)
        return p_vector_from_3_bonds(atom, bond, out = out, up = up)
    elif nbonds == 2:
        return p_vector_from_sp2_2_bonds(atom, bond, out = out, up = up) ### revise to return None if it doesn't know?
    elif nbonds == 1:
        # might be O(sp2); if not for knowing it was sp2, might be open bond or N(sp)... but it won't tell us orientation
        return None
    else:
        assert bond in atom.bonds
        assert len(atom.bonds) <= 3 # will always fail
    pass

def p_vector_from_3_bonds(atom, bond, out = DFLT_OUT, up = DFLT_UP):
    """
    Given an sp2 atom with 3 bonds, and one of those bonds which we assume has pi orbitals in it,
    return a unit vector from atom along its p orbital, guaranteed perpendicular to bond,
    for purposes of drawing the pi orbital component of bond.
    Note that it's arbitrary whether we return a given vector or its opposite.
    [##e should we fix that, using out and up? I don't think we can in a continuous way, so don't bother.]
       We don't verify the atom is sp2, since we don't need to for this code to work,
    though our result would probably not make sense otherwise.
    """
    others = map( lambda bond: bond.other(atom), atom.bonds)
    assert len(others) == 3
    other1 = bond.other(atom)
    others.remove(other1)
    other2, other3 = others
    apos = atom.posn()
    v1 = other1.posn() - apos
    # if v1 has 0 length, we should return some default value here; this might sometimes happen so I better handle it.
    # actually i'm not sure the remaining code would fail in this case! If not, I might revise this.
    if vlen(v1) < 0.01: # in angstroms
        return + up
    v2 = other2.posn() - apos
    v3 = other3.posn() - apos
    # projecting along v1, we hope v2 and v3 are opposite, and then we return something perpendicular to them.
    # if one is zero, just be perp. to the other one alone.
    # (If both zero? Present code returns near-0. Should never happen, but fix. #e)
    # otherwise if they are not opposite, use perps to each one, "averaged",
    # which means (for normalized vectors), normalize the larger of the sum or difference
    # (equivalent to clustering them in the way (of choice of sign for each) that spans the smallest angle).
    # Optim: no need to project them before taking cross products to get the perps to use.
    ## v2 -= v1 * dot(v2,v1)
    ## v3 -= v1 * dot(v3,v1)
    v2p = cross(v2,v1)
    v3p = cross(v3,v1)
    lenv2p = vlen(v2p)
    if lenv2p < 0.01:
        return norm(v3p)
    v2p /= lenv2p
    lenv3p = vlen(v3p)
    if lenv3p < 0.01:
        return v2p # normalized above
    v3p /= lenv3p
    r1 = v2p + v3p
    r2 = v2p - v3p
    lenr1 = vlen(r1)
    lenr2 = vlen(r2)
    if lenr1 > lenr2:
        return r1/lenr1
    else:
        return r2/lenr2
    pass

def p_vector_from_sp2_2_bonds(atom, bond, out = DFLT_OUT, up = DFLT_UP):
    others = map( lambda bond: bond.other(atom), atom.bonds)
    assert len(others) == 2
    other1 = bond.other(atom)
    others.remove(other1)
    other2, = others
    apos = atom.posn()
    v1 = other1.posn() - apos
    if vlen(v1) < 0.01: # in angstroms
        return + up
    v2 = other2.posn() - apos
    
    v2p = cross(v2,v1)
    lenv2p = vlen(v2p)
    if lenv2p < 0.01:
        # this entire case happens rarely or hopefully never (only when 2 sp2 bonds are parallel)
        res = up - v1 * dot(up,v1)
        if vlen(res) >= 0.01:
            return norm(res)
        res = out - v1 * dot(out,v1)
        return norm(out)
    return v2p / lenv2p

# ==

# pure geometry routines, should be refiled:

def arb_non_parallel_vector(vec):
    """
    Given a nonzero vector, return an arbitrary vector not close to
    being parallel to it.
    """
    x,y,z = vec
    if abs(z) < abs(x) > abs(y):
        # x is biggest, use y
        return V(0,1,0)
    else:
        return V(1,0,0)
    pass

def arb_perp_unit_vector(vec):
    """
    Given a nonzero vector, return an arbitrary unit vector
    perpendicular to it.
    """
    vec2 = arb_non_parallel_vector(vec)
    return norm(cross(vec, vec2))

def arb_ortho_pair(vec): #k not presently used # see also some related code in pi_vectors()
    """
    Given a nonzero vector, return an arbitrary pair of unit vectors
    perpendicular to it and to each other.
    """
    res1 = arb_perp_unit_vector(vec)
    res2 = norm(cross(vec, res1))
    return res1, res2

# end
