# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
atomtypes.py -- AtomType object, knows about one bonding pattern for one element.

@author: Josh, Bruce
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 050510 moved some code (originally by Josh)
out of Elem.__init__ into new class AtomType.__init__
and added all the superstructure, as part of supporting
atom types with variable bonding patterns
(and higher-order bonds, though as of 050511 these atoms
don't yet know anything directly about bond-orders
and their .valence attribute is probably not yet used [later: now it's used].)

bruce 050513 replaced some == with 'is' and != with 'is not', to avoid __getattr__
on __xxx__ attrs in python objects.
"""

# element.atomtypes -> list of atom types usable for that element

# atom.atomtype -> current atomtype for that atom

from geometry.VQT import Q
from utilities.Log import redmsg
from utilities import debug_flags
from foundation.state_utils import IdentityCopyMixin
import foundation.env as env

from model.bond_constants import V_SINGLE, V_DOUBLE, V_TRIPLE, V_AROMATIC, V_GRAPHITE, V_CARBOMERIC

class AtomType(IdentityCopyMixin):
    """
    An atom type includes an element and its bonding pattern (and maybe more) --
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
    def __init__(self,
                 elem,
                 name,
                 formalCharge,
                 electronsNeeded,
                 electronsProvided,
                 covalentRadius,
                 bondvectors):
        """
        #doc...
        Set some public members, including element, name, fullname,
        numbonds, valence, rcovalent, bondvectors, base, and quats.
        Also spX, openbond; and for some elements, num_lonepairs (etc),
        num_pi_electrons.
        """
        self.element = elem

        # electronsProvided + formalCharge should equal group number

        # these are shared from another atom (half of an order 1 covalent bond)
        electronsShared = electronsNeeded - electronsProvided

        self.valence = electronsShared # total bond order for all bonds to this atomtype
        self.name = name = name or "?"
            # default name won't show up except for bugs, provided it's only used for elements with only one atomtype
        self.fullname = elem.name + '/' + self.name #ok? [see also self.fullname_for_msg()]
        self.openbond = (elem.eltnum == 0)
        if name.startswith("sp3") or name == "?":
            spX = 3
        elif name.startswith("sp2"): # including sp2 and sp2(graphitic)
            spX = 2
        elif name.startswith("sp") and (name == "sp" or not name[2].isdigit()):
            spX = 1
        else:
            print "warning: bug: atomtype name in %r does not start with sp, sp2, or sp3; assuming sp3 in bonds code" % self.fullname
            spX = 3
        self.spX = spX
        if 0 and debug_flags.atom_debug and (spX != 3 or self.openbond):
            print "atom_debug: fyi: %r has spX == %d" % (self.fullname, spX)
        self.rcovalent = covalentRadius

        self.base = None
        self.quats = [] # ends up one shorter than self.numbonds [bruce 041217]
        if (bondvectors!=None):
            # number of distinct bonds to different other atoms (a
            # double bond is counted as 1)
            self.numbonds = len(bondvectors)

            s = bondvectors[0]
            self.base = s
            for v in bondvectors[1:]:
                self.quats += [Q(s,v)]
            self.bondvectors = bondvectors
        else:
            self.numbonds = 0
            self.bondvectors = None
        #nmz787 self.bondvectors = bondvectors or [] # not sure if [] (in place of None) matters
        
        self.charge = formalCharge
        #self._init_electronic_structure() # this uses self.numbonds, so don't call it too early
        self._init_permitted_v6_list()
        return # from __init__

#     def _init_electronic_structure(self): #bruce 050707
#         """
#         [private method]
#         Figure out situation with valence electrons, etc, and store it in
#         attributes. Only works for low-enough-atomic-number elements.
#         """
#         # Figure out situation with valence electrons (available for pi orbitals), lone pairs, etc.
#         # This might be only supported for non-sp3 atomtypes (which presently go no higher than sulfur) so far.
#         # And for now it might be mostly hardcoded rather than principled. [bruce 050706]

#         _debug = 0
#         if (self.element.eltnum == 15 or self.element.eltnum == 33 or self.element.eltnum == 34):
#             _debug = 1
#             print "_init_electronic_structure(%d)" % self.element.eltnum
#         total_es = self.element.eltnum + self.charge # total number of electrons
#         # shell 1 is 1s, 2 es in all. shell 2 is 2s, 2px, 2py, 2pz, 8 electrons in all. shell 3 starts out 3s, 3px, 3py, 3pz...
#         unassigned_es = total_es
#         for shellsize in [2,8,8,-1]:
#             if shellsize < 0:
#                 return # don't yet bother to figure out any of this for more than 18 electrons
#                     # (should be ok, since this info is only needed for sp2 or sp atomtypes,
#                     #  and those don't yet go above Sulfur (elt 16)
#             if unassigned_es <= shellsize:
#                 num_outer_shell_es = unassigned_es
#                 break
#             # try the next shell
#             unassigned_es -= shellsize
#         del unassigned_es
#         if (_debug): print "num_outer_shell_es: %d" % num_outer_shell_es
#         if (_debug): print "shellsize: %d" % shellsize
#         self.total_es = total_es # not yet used for anything
#         self.num_outer_shell_es = num_outer_shell_es # (this might only be used in this routine)
#         if shellsize != 8:
#             return # don't go beyond this point for H or He.
#             # BTW, H is considered sp3 to simplify the bond-inference code, but technically that's nonsense.
#         spX = self.spX
#         numbonds = self.numbonds # we'll check this for consistency, or maybe use it to distinguish graphitic N from other sp2 N...
#         # now figure out number of lone pairs, available pi electrons
#         nlp = npi = 0 # num_spX_lonepairs (just those in spX orbitals, not p orbitals), num_pi_electrons
#             # 0 is default value for both, but following cases modify one or both values;
#             # then they're stored in attrs before we return.
#         nlp_p = 0 # num_p_lonepairs (number of lone pairs in p orbitals)
#         if spX == 3:
#             # There are 4 available bonding (or LP) positions or AOs (atomic orbitals), hybridized from s,p,p,p.
#             # The first 4 electrons just offer themselves for sigma bonds, one per orbital.
#             # Additional electrons pair up with those one by one to form lone pairs, reducing numbonds.
#             if num_outer_shell_es <= 4:
#                 assert numbonds == num_outer_shell_es
#             else: # 5 thru 8
#                 if (numbonds != shellsize - num_outer_shell_es):
#                     return # this is true for sp3(p) i.e. sp3(phosphate),
                             #currently ok to bail, as none of this is actually 
                             #used.
#                 nlp = num_outer_shell_es - 4
#         elif spX == 2:
#             # There are 3 bonding (or LP) positions,
#             # plus one p orbital which might help form a pi bond or contain an LP or contain nothing.
#             # The first 3 electrons offer themselves for sigma bonds
#             # (I don't know what happens for fewer than 3,
#             #  and we have no non-sp3 atomtypes for those anyway -- maybe they're impossible.)
#             assert 3 <= num_outer_shell_es <= 6 # (the upper limit of 6 is commented on implicitly below)
#             # The 4th electron offers itself for a pi bond (which is not counted in numbonds).
#             # The next one can either pair up with that one (e.g. in N/sp2(graphitic))
#             # or with one of the "sigma electrons" (reducing numbonds).
#             # Likewise, for more electrons, 0 or 1 can pair with the "pi electron",
#             # and the rest reduce numbonds (down to 1 for Oxygen -- any more and I doubt sp2 is possible).
#             # (I don't know how many of those combinations are possible,
#             #  but I don't need to know in this code, since numbonds tells me what happened.)
#             if num_outer_shell_es <= 3:
#                 assert numbonds == num_outer_shell_es
#             else:
#                 npi = 1 # the 4th electron (this value might be changed again below)
#                 if num_outer_shell_es > 4:
#                     # find out what happens to the 5th and optional 6th electrons
#                     more_es = num_outer_shell_es - 4 # (1 or 2 of them)
#                     # some of them (0 to 2, all or all but one) paired with sigma electrons to form lone pairs and reduce numbonds
#                     nlp = 3 - numbonds
#                     leftover = more_es - nlp
#                     assert leftover in [0,1]
#                     # the leftover electron (if any) paired with that 4th "pi electron"
#                     # (forming another lone pair in the p orbital -- I'll store that separately to avoid confusion)
#                     npi -= leftover
#                     nlp_p += leftover
#         else:
#             assert spX == 1
#             # There are two bonding (or LP) positions, plus 2 p orbitals.
#             # I'll use similar code to the above, though I think many combinations of values won't be possible.
#             # In fact, I think 4 <= num_outer_shell_es <= 6, so I won't worry much about correctness of the following outside of that.
#             if num_outer_shell_es <= 2:
#                 assert numbonds == num_outer_shell_es
#             else:
#                 more_es = min(2, num_outer_shell_es - 2) # no higher than 2
#                 # for C(sp), num_outer_shell_es == 4, and these 2 offer themselves for pi bonds
#                 npi += more_es
#                 # now if there are more than 4, what do they pair up with?
#                 # I'm not sure, so figure it out from numbonds (though I suspect only one answer is ever possible).
#                 if num_outer_shell_es > 4:
#                     more_es = num_outer_shell_es - 4
#                     nlp = 2 - numbonds # lone pairs in the sp AOs
#                     leftover = more_es - nlp
#                     assert leftover in [0,1,2] # since only 2 p orbitals (occupied by 1 e each) they can go into
#                     npi -= leftover
#                     nlp_p += leftover
#         self.num_spX_lonepairs = nlp
#         self.num_p_lonepairs = nlp_p
#         self.num_lonepairs = nlp + nlp_p # more useful to the outside code, though not yet used as of 050707
#         self.num_pi_electrons = npi
#         assert 2 * (nlp + nlp_p) + npi + numbonds == num_outer_shell_es # double check all this by counting the electrons
#         if 0 and debug_flags.atom_debug:
#             print "atom_debug: (%d) %s has %d bonds, and %d,%d,%d  pi electrons, LPs in spX, LPs in p" % \
#                   (self.element.eltnum, self.fullname, numbonds, npi, nlp, nlp_p)
#         return # from _init_electronic_structure

    def potential_pi_bond(self):
        """
        Returns true if atoms of this type can be involved in a pi bond.
        """
        return self.spX < 3

    def is_linear(self):
        """
        Returns true if atoms of this type have two bonds in a linear arrangement.
        """
        return self.spX == 1

    def is_planar(self):
        """
        Returns true if atoms of this type have three bonds in a planar arrangement.
        """
        return self.spX == 2
        
    def apply_to(self, atom): # how is this used? do we transmute the elt too? (why not? why? when would that be called?)
        """
        change atom to have this atomtype
        (or emit history warning saying why you can't)
        """
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
        """
        Is it permissible for a bond of the given v6 to connect to this atomtype, ignoring valence issues?
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
        
        res = [] # build a list of bond types to allow
        spX = self.spX

        if (spX == 3):
            if (self.valence > 4):
                res.append(V_DOUBLE)
                res.append(V_AROMATIC)
                res.append(V_GRAPHITE)
                if (self.valence > 5):
                    res.append(V_TRIPLE)
                    res.append(V_CARBOMERIC)
            else:
                return # only single bonds are allowed for sp3 with 4 or fewer bonds

        if (spX ==  2): # currently C, N, O, S
            if (self.valence > 1):
                res.append(V_AROMATIC)
                res.append(V_GRAPHITE)
                if (self.valence > 1.9):
                    res.append(V_DOUBLE)

        if (spX == 1): # currently X, C, N
            if (self.element.symbol == "X"):
                res.append(V_DOUBLE)
                res.append(V_AROMATIC)
                res.append(V_GRAPHITE)
                res.append(V_TRIPLE)
                res.append(V_CARBOMERIC)
            elif (self.element.symbol == "N"):
                res.append(V_TRIPLE)
            elif (self.valence > 1):
                res.append(V_AROMATIC)
                res.append(V_GRAPHITE)
                if (self.valence > 1.9):
                    res.append(V_DOUBLE)
                    if (self.valence > 2.1):
                        res.append(V_CARBOMERIC)
                        if (self.valence > 2.9):
                            res.append(V_TRIPLE)

        if not res:
            return

        if 0 and debug_flags.atom_debug:
            print "atom_debug: (%d) %s permits these v6's besides single(6): %r" % (self.element.eltnum, self.fullname, res)

        res.append(V_SINGLE)
            # Note: we do this even for O(sp2) and S(sp2), even though a bond1 as their sole bond is always a valence error.
            # Valence errors have to be treated separately anyway, so it's probably ok to not catch these special cases here.
            # See also the docstring for a comment about this. See also the function bond_type_warning.
        res.sort()
        self.permitted_v6_list = tuple(res) # in case tuple can be searched faster
        return

    def _classify(self): #bruce 080502
        """
        [private helper for can_bond_to]
        
        @return: one of the following strings, as appropriate for self.
        - 'bondpoint'
        - 'Pl'
        - 'sugar'  (not including Pl)
        - 'axis'
        - 'unpaired-base'
        - 'chem'

        @note: it would be better if our legal return values were int-valued
               named constants for fast lookup in a table of legal pairs,
               and if the classification of self was an attribute of self.
        """
        if self.element.symbol == 'X': # kluge
            return 'bondpoint'
        elif self.element.role == 'strand':
            if self.element.symbol == 'Pl5':
                return 'Pl'
            return 'sugar'
        else:
            return self.element.role or 'chem' # 'axis' or 'unpaired-base' or 'chem'
        pass

    def can_bond_to(self, atom, bondpoint = None, auto = False): #bruce 080502
        """
        Some tool in the UI wants to bond a new atom of atomtype self
        to the given existing atom, in place of the given bondpoint
        if one is provided. If auto is true, this is an "autobonding"
        (just due to nearness of a new atom to an existing bondpoint);
        otherwise it's an explicit bonding attempt by the user.

        Return True if this should be allowed, False if not.

        @note: it would be desirable to improve this API so that the reason
               why not could also be returned.
        """
        # note: this is not yet modular; and it is partly redundant with
        # _fix_atom_or_return_error_info in fix_bond_directions.py.
        
        del bondpoint, auto # not yet used
        
        def check_by_class1(class1, class2):
            # Note: pairs of _classify return values can be made illegal
            # by making this function return false for them in either order.
            # The outer function only returns true if this function
            # accepts a pair in both orders.
            if class1 == 'chem':
                return class2 in ('chem', 'bondpoint')
            elif class1 == 'Pl':
                return class2 in ('sugar', 'bondpoint')
            elif class1 == 'bondpoint':
                return class2 != 'bondpoint'
            return True
        class1 = self._classify()
        class2 = atom.atomtype._classify()
        if not check_by_class1(class1, class2):
            return False
        if not check_by_class1(class2, class1):
            return False
        return True
        
    pass # end of class AtomType

# end

"""
... the maximal sets of end-elements for A6 will be:

aromatic, graphite: C, N, B (B depends on how Damian answers some Qs)

(carbomeric, if we have it, only C -- probably not for A6;
if I didn't make it clear, this only exists in chains of C(sp)
alternating with bonda, where the bond orders are 1.5, 2.5, 1.5, etc)

double: C, N, O, S

triple: C, N
"""
