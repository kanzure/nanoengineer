# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
atomtypes.py -- AtomType object, knows about one bonding pattern for one element.

Owned by bruce while atomtypes and higher-order bonds are being implemented.

$Id$

History:

Bruce 050510 moved some code (originally by Josh)
out of Elem.__init__ into new class AtomType.__init__
and added all the superstructure, as part of supporting
atom types with variable bonding patterns
(and higher-order bonds, though as of 050511 these atoms
don't yet know anything directly about bond-orders
and their .valence attribute is probably not yet used.)

bruce 050513 replaced some == with 'is' and != with 'is not', to avoid __getattr__
on __xxx__ attrs in python objects.

050901 bruce used env.history in some places.
"""

# element.atomtypes -> list of atom types usable for that element

# atom.atomtype -> current atomtype for that atom

from VQT import Q
from HistoryWidget import redmsg, orangemsg
import platform
import env

from bond_constants import *

class AtomType:
    """An atom type includes an element and its bonding pattern (and maybe more) --
    enough info to know how to construct things in Build mode using this element in this bonding pattern,
    something about how the user wants to simulate them or minimize them (externally or wirthin Build mode),
    etc.
       This is designed more for the UI than for the simulator, which might need even finer distinctions
    to properly simulate atoms. The idea is to include in this class whatever the user needs for convenient
    building, and to later infer from the pattern of actual bonds and surrounding atoms (as well as the info
    in this object) how best to simulate an atom using this atomtype object.
       An atomtype object can be used alone to create a free or attached atom,
    and might also be kept around by the atom as its way of remembering its own type -- which might change.
    Or an atom might just remember the *name* of its atomtype
    (and grab this object from a list in the element) -- I don't know yet.
        ###obs, probably wrong: Note that (as far as is yet known) more than one identical atomtype object might exist -- so the object itself
    is not an ok place to store definitive mutable per-session info about how to treat that atom type.
       The name of an atomtype might be reused for more than one element (e.g. 'sp2')
    but the atomtype itself is element-specific. (Related atomtype objects might share code or data, of course.)
    """
    def __init__(self, elem, bn_triple, valence):
        """#doc... Set some public members, including element, name, fullname,
        numbonds, valence, rcovalent, bondvectors, base, and quats.
        Also spX, openbond; and for some elements, num_lonepairs (etc), num_pi_electrons.
        """
        self.element = elem
        self.valence = valence
        if len(bn_triple) == 3:
            numbonds, rcovalent, bondvectors = bn_triple
            name = None
        else:
            numbonds, rcovalent, bondvectors, name = bn_triple
        self.name = name = name or "?"
            # default name won't show up except for bugs, provided it's only used for elements with only one atomtype
        self.fullname = elem.name + '/' + self.name #ok? [see also self.fullname_for_msg()]
        self.openbond = (elem.eltnum == 0)
        if name.startswith("sp3") or name == "?":
            spX = 3
        elif name.startswith("sp2"):
            spX = 2
        elif name.startswith("sp") and (name == "sp" or not name[2].isdigit()):
            spX = 1
        else:
            print "warning: bug: atomtype name in %r does not start with sp, sp2, or sp3; assuming sp3 in bonds code" % self.fullname
            spX = 3
        self.spX = spX
        if 0 and platform.atom_debug and (spX != 3 or self.openbond):
            print "atom_debug: fyi: %r has spX == %d" % (self.fullname, spX)
        
        # bondvectors might be None or a list of vectors whose length should be numbonds (except for two buggy elements);
        # if None it means the old code would not set self.base and self.quats... not sure all effects or reasons, but imitate for now
        if bondvectors is not None:
            ## doesn't work, don't know why: assert type(bondvectors) == type(()) or type(bondvectors) == type([])
            if len(bondvectors) != numbonds:
                if elem.name not in ["Arsenic", "Selenium"]: # known bugs
                    print "warning: len(bondvectors) != numbonds:", bondvectors, numbonds, elem # known to happen for at least 2 elements
                numbonds = len(bondvectors) # fix it up this way for now
        self.numbonds = numbonds
        self.rcovalent = rcovalent/100.0
            # (Note: rcovalent used to be None for nonbonding elements like Helium,
            # which made most uses of it errors (e.g. when drawing bonds to Helium).
            # Once we decided such bonds should be allowed to exist, we made it act
            # like 0.0 in the drawing code, then replaced that with this more
            # general change to 0.0, hoping to avoid possible other (hypothetical)
            # bugs. As far as I know this is ok, but I have not fully analyzed every
            # possible consequence of this change. [bruce 041217])
        self.base = None
        self.quats = [] # ends up one shorter than self.numbonds [bruce 041217]
        self.bondvectors = bondvectors or [] # not sure if [] (in place of None) matters
        if bondvectors:
            s = bondvectors[0]
            self.base = s
            for v in bondvectors[1:]:
                self.quats += [Q(s,v)]
        
        self.charge = 0 # only uncharged atomtypes are supported, for now.
            #e later we'll have some charged atomtypes, but there are some UI issues
            # with how to keep the menus of atomtypes short (separate menus for hybridization and charge), maybe more.
        self._init_electronic_structure() # this uses self.numbonds, so don't call it too early
        self._init_permitted_v6_list()
        return # from __init__

    def _init_electronic_structure(self): #bruce 050707
        "[private method] Figure out situation with valence electrons, etc, and store it in attributes. Only works for low elements."
        # Figure out situation with valence electrons (available for pi orbitals), lone pairs, etc.
        # This might be only supported for non-sp3 atomtypes (which presently go no higher than sulfur) so far.
        # And for now it might be mostly hardcoded rather than principled. [bruce 050706]

        total_es = self.element.eltnum + self.charge # total number of electrons
        # shell 1 is 1s, 2 es in all. shell 2 is 2s, 2px, 2py, 2pz, 8 electrons in all. shell 3 starts out 3s, 3px, 3py, 3pz...
        unassigned_es = total_es
        for shellsize in [2,8,8,-1]:
            if shellsize < 0:
                return # don't yet bother to figure out any of this for more than 18 electrons
                    # (should be ok, since this info is only needed for sp2 or sp atomtypes,
                    #  and those don't yet go above Sulfur (elt 16)
            if unassigned_es <= shellsize:
                num_outer_shell_es = unassigned_es
                break
            # try the next shell
            unassigned_es -= shellsize
        del unassigned_es
        self.total_es = total_es # not yet used for anything
        self.num_outer_shell_es = num_outer_shell_es # (this might only be used in this routine)
        if shellsize != 8:
            return # don't go beyond this point for H or He.
            # BTW, H is considered sp3 to simplify the bond-inference code, but technically that's nonsense.
        spX = self.spX
        numbonds = self.numbonds # we'll check this for consistency, or maybe use it to distinguish graphitic N from other sp2 N...
        # now figure out number of lone pairs, available pi electrons
        nlp = npi = 0 # num_spX_lonepairs (just those in spX orbitals, not p orbitals), num_pi_electrons
            # 0 is default value for both, but following cases modify one or both values;
            # then they're stored in attrs before we return.
        nlp_p = 0 # num_p_lonepairs (number of lone pairs in p orbitals)
        if spX == 3:
            # There are 4 available bonding (or LP) positions or AOs (atomic orbitals), hybridized from s,p,p,p.
            # The first 4 electrons just offer themselves for sigma bonds, one per orbital.
            # Additional electrons pair up with those one by one to form lone pairs, reducing numbonds.
            if num_outer_shell_es <= 4:
                assert numbonds == num_outer_shell_es
            else: # 5 thru 8
                assert numbonds == shellsize - num_outer_shell_es
                nlp = num_outer_shell_es - 4
        elif spX == 2:
            # There are 3 bonding (or LP) positions,
            # plus one p orbital which might help form a pi bond or contain an LP or contain nothing.
            # The first 3 electrons offer themselves for sigma bonds
            # (I don't know what happens for fewer than 3,
            #  and we have no non-sp3 atomtypes for those anyway -- maybe they're impossible.)
            assert 3 <= num_outer_shell_es <= 6 # (the upper limit of 6 is commented on implicitly below)
            # The 4th electron offers itself for a pi bond (which is not counted in numbonds).
            # The next one can either pair up with that one (e.g. in N/sp2(graphitic))
            # or with one of the "sigma electrons" (reducing numbonds).
            # Likewise, for more electrons, 0 or 1 can pair with the "pi electron",
            # and the rest reduce numbonds (down to 1 for Oxygen -- any more and I doubt sp2 is possible).
            # (I don't know how many of those combinations are possible,
            #  but I don't need to know in this code, since numbonds tells me what happened.)
            if num_outer_shell_es <= 3:
                assert numbonds == num_outer_shell_es
            else:
                npi = 1 # the 4th electron (this value might be changed again below)
                if num_outer_shell_es > 4:
                    # find out what happens to the 5th and optional 6th electrons
                    more_es = num_outer_shell_es - 4 # (1 or 2 of them)
                    # some of them (0 to 2, all or all but one) paired with sigma electrons to form lone pairs and reduce numbonds
                    nlp = 3 - numbonds
                    leftover = more_es - nlp
                    assert leftover in [0,1]
                    # the leftover electron (if any) paired with that 4th "pi electron"
                    # (forming another lone pair in the p orbital -- I'll store that separately to avoid confusion)
                    npi -= leftover
                    nlp_p += leftover
        else:
            assert spX == 1
            # There are two bonding (or LP) positions, plus 2 p orbitals.
            # I'll use similar code to the above, though I think many combinations of values won't be possible.
            # In fact, I think 4 <= num_outer_shell_es <= 6, so I won't worry much about correctness of the following outside of that.
            if num_outer_shell_es <= 2:
                assert numbonds == num_outer_shell_es
            else:
                more_es = min(2, num_outer_shell_es - 2) # no higher than 2
                # for C(sp), num_outer_shell_es == 4, and these 2 offer themselves for pi bonds
                npi += more_es
                # now if there are more than 4, what do they pair up with?
                # I'm not sure, so figure it out from numbonds (though I suspect only one answer is ever possible).
                if num_outer_shell_es > 4:
                    more_es = num_outer_shell_es - 4
                    nlp = 2 - numbonds # lone pairs in the sp AOs
                    leftover = more_es - nlp
                    assert leftover in [0,1,2] # since only 2 p orbitals (occupied by 1 e each) they can go into
                    npi -= leftover
                    nlp_p += leftover
        self.num_spX_lonepairs = nlp
        self.num_p_lonepairs = nlp_p
        self.num_lonepairs = nlp + nlp_p # more useful to the outside code, though not yet used as of 050707
        self.num_pi_electrons = npi
        assert 2 * (nlp + nlp_p) + npi + numbonds == num_outer_shell_es # double check all this by counting the electrons
        if 0 and platform.atom_debug:
            print "atom_debug: (%d) %s has %d bonds, and %d,%d,%d  pi electrons, LPs in spX, LPs in p" % \
                  (self.element.eltnum, self.fullname, numbonds, npi, nlp, nlp_p)
        return # from _init_electronic_structure
        
    def apply_to(self, atom): # how is this used? do we transmute the elt too? (why not? why? when would that be called?)
        "change atom to have this atomtype (or emit history warning saying why you can't)"
        ###e need to split out the check for transmute being legal and do it first
        # (so our caller, making menu, can disable illegal cmds)
        ##print "apply_to for self = %r" % self
        atom.Transmute( self.element, atomtype = self)
        if atom.atomtype is not self:
            # it didn't work for some reason (clean up way of finding history, and/or get Transmute to say why it failed #e)
            env.history.message( redmsg( "Can't change %r to %s" % (atom, self.fullname_for_msg()))) #e say why not

    def ok_to_apply_to(self, atom):
        return True
            # stub, see comments above for one way to fix;
            # but it's better to wait til bond valence code is more designed and filled-out
            # and then it'll be transmute calling this method instead of us calling a split out part of it!
            ###@@@

    def __repr__(self):
        return "<%s %r at %#x>" % (self.__class__.__name__, self.fullname, id(self))

    def fullname_for_msg(self): ####@@@@ use this in more places -- check all uses of fullname or of len(elt.atomtypes)
        if len(self.element.atomtypes) > 1: # this changes at runtime, thus this is a method and not a constant
            return "%s(%s)" % (self.element.name, self.name) # not sure good for Nitrogen(sp2(graphitic)) ###e
        else:
            return self.element.name
        pass
    
    def permits_v6(self, v6):
        ###@@@ see also bond_utils.possible_bond_types; maybe they should share some common knowledge
        """Is it permissible for a bond of the given v6 to connect to this atomtype, ignoring valence issues?
        Note: this method should be fast -- it's called (at least) for every non-single bond of every changed atom.
           BTW [#obs, WRONG],
        an order of bond types from most to least permissible is (ignoring special rules for graphite, and sp2 O or S):
        single, double, aromatic/graphite, triple, carbomeric. [See also the constant tuple most_permissible_v6_first.]
        If a type in that list is not permitted for some atomtype, neither are all types beyond it
        (again excepting special recognition-rules for graphite, and sp2 O or S not permitting single bonds).
        [This is wrong because for N(sp) we only permit single (bad valence) and triple, not double.
         That could change if necessary. ###@@@]
           Note: sp2 O and S disallow single bonds only because they have exactly one bond and a valence requirement of 2
        (at least that's one way of thinking about it). So this function permits single bonds for them, so that
        the error in e.g. H-O(sp2) can be considered a valence error on the O rather than a bond-type error.
        This way, the calling code is simpler, since all bonds have legal types just given the elements/atomtypes on them;
        valence errors can be handled separately at a later stage.
           (Similarly, this function would permit both S-S and S=S for diatomic S(sp2), though at later stages,
         neither is error-free, S-S due to valence errors and S=S due to extreme instability. BTW, for code simplicity
         I've decided that both those errors are "permitted but with warnings" (and the warnings might be NIM). That has
         nothing to do with this function specifically, it's just FYI.)
           If this function is used to populate menus of possible bond types, 'single' should probably be disallowed
        or deprecated for sp2 O and S (as a special case, or based on some other attr of this atomtype (#e nim)).
        """
        return (v6 in self.permitted_v6_list)
    
    permitted_v6_list = (V_SINGLE,) # default value of instance attribute; correct value for most atomtypes
        # permitted_v6_list is a public instance attribute, I guess
    
    def _init_permitted_v6_list(self):
        #e not yet correct for charged atomtypes (which is ok since we don't yet have any)...
        # the hardcoded element lists would need revision
        
        # set some public attrs which help with some warnings by external code;
        # some of them are because numbonds == 1 means atom valence determines bond order for the only bond
        self.is_S_sp2 = (self.element.symbol == 'S' and self.spX == 2)
        self.is_O_sp2 = (self.element.symbol == 'O' and self.spX == 2)
        self.bond1_is_bad = (self.is_S_sp2 or self.is_O_sp2)
        self.is_N_sp = (self.element.symbol == 'N' and self.spX == 1) # used for a special case, below
        
        spX = self.spX
        if spX == 3:
            return # only single bonds are allowed for sp3
        res = [] # build a list of bond types to allow
##        if not self.element.symbol in "OS":
##            res.append(V_SINGLE) ## what about H bonded to O(sp2)? no bond type would be legal... need to treat as valence error...
        if self.element.symbol in "CNOSX": # (X means open bond)
            # double bonds are ok for those elements (for either sp or sp2, of the supported atomtypes for them? almost...)
            if not self.is_N_sp:
                res.append(V_DOUBLE)
        if self.element.symbol in "CNX" and spX == 1:
            res.append(V_TRIPLE)
        if self.element.symbol in "CNX": ###@@@ and maybe B too? ok for sp or sp2? almost...
            if not self.is_N_sp:
                res.append(V_AROMATIC)
                res.append(V_GRAPHITE)
        if self.element.symbol in "CX" and spX == 1:
            res.append(V_CARBOMERIC)
        if not res:
            return
        if 0 and platform.atom_debug:
            print "atom_debug: (%d) %s permits these v6's besides single==6: %r" % (self.element.eltnum, self.fullname, res)
        res.append(V_SINGLE)
            # Note: we do this even for O(sp2) and S(sp2), even though a bond1 as their sole bond is always a valence error.
            # Valence errors have to be treated separately anyway, so it's probably ok to not catch these special cases here.
            # See also the docstring for a comment about this. See also the function bond_type_warning.
        res.sort()
        self.permitted_v6_list = tuple(res) # in case tuple can be searched faster
        return
    
    pass # end of class AtomType

# end

'''
... the maximal sets of end-elements for A6 will be:

aromatic, graphite: C, N, B (B depends on how Damian answers some Qs)

(carbomeric, if we have it, only C -- probably not for A6;
if I didn't make it clear, this only exists in chains of C(sp)
alternating with bonda, where the bond orders are 1.5, 2.5, 1.5, etc)

double: C, N, O, S

triple: C, N
'''
