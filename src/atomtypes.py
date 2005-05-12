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
"""

# element.atomtypes -> list of atom types usable for that element

# atom.atomtype -> current atomtype for that atom

from VQT import Q
from HistoryWidget import redmsg, orangemsg

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
       Note that (as far as is yet known) more than one identical atomtype object might exist -- so the object itself
    is not an ok place to store definitive mutable per-session info about how to treat that atom type.
       The name of an atomtype might be reused for more than one element (e.g. 'sp2')
    but the atomtype itself is element-specific. (Related atomtype objects might share code or data, of course.)
    """
    def __init__(self, elem, bn_triple, valence):
        """#doc... Set some public members, including element, name, fullname,
        numbonds, valence, rcovalent, bondvectors, base, and quats.
        """
        self.element = elem
        self.valence = valence
        if len(bn_triple) == 3:
            numbonds, rcovalent, bondvectors = bn_triple
            name = None
        else:
            numbonds, rcovalent, bondvectors, name = bn_triple
        self.name = name or "?"
            # default name won't show up except for bugs, provided it's only used for elements with only one atomtype
        self.fullname = elem.name + '/' + self.name #ok? [see also self.fullname_for_msg()]
        # bondvectors might be None or a list of vectors whose length should be numbonds (except for two buggy elements);
        # if None it means the old code would not set self.base and self.quats... not sure all effects or reasons, but imitate for now
        if bondvectors != None:
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
        return
    def apply_to(self, atom): # how is this used? do we transmute the elt too? (why not? why? when would that be called?)
        "change atom to have this atomtype (or emit history warning saying why you can't)"
        ###e need to split out the check for transmute being legal and do it first
        # (so our caller, making menu, can disable illegal cmds)
        ##print "apply_to for self = %r" % self
        atom.Transmute( self.element, atomtype = self)
        if atom.atomtype != self:
            # it didn't work for some reason (clean up way of finding history, and/or get Transmute to say why it failed #e)
            atom.molecule.assy.w.history.message( redmsg( "Can't change %r to %s" % (atom, self.fullname_for_msg()))) #e say why not
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
    pass # end of class AtomType

# end
