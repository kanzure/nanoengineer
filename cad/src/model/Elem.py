# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Elem.py -- provides class Elem, which represents one element
in NE1's periodic table.

Note that some Elem instances are used only with "pseudoatoms" or
bondpoints, whereas others correspond to actual chemical elements.

@author: Josh
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

Bruce 071101 split class Elem out of elements.py into its own module.

TODO:

In elements.py and Elem.py,
modularize the creation of different kinds of elements,
to help permit specialized modules and Elem/Atom subclasses
for PAM3 and PAM5 (etc). (Should we define new Elem subclasses for them?)
"""

from foundation.state_utils import IdentityCopyMixin

class Elem(IdentityCopyMixin):
    """
    There is exactly one of these objects for each supported element in the periodic table.
    Its identity (as a python object) never changes during the run.
    Instead, if prefs changes are made in color, radius, or perhaps bonding pattern,
    this object's contents will be modified accordingly.
    """
    # bruce 050510 renamed this from 'elem'
    # (not using 'Element' since too common in strings/comments)
    
    # default values of per-instance constants
    bonds_can_be_directional = False #bruce 071015

    # attributes for classifying elements -- tentative in name, meaning, and value-encoding [bruce 071106]
    # (warning: these default values are never used, since __init__ always sets these attrs in self)
    pam = None # name of pseudo-atom model (e.g. MODEL_PAM3 == 'PAM3'), or None;
        # not sure if Singlet and regular elems have same .pam
        # REVIEW: it might be simplest if Singlet had None here, and all others had a true value, e.g. 'PAM3' or 'PAM5' or 'Chem'.
        # If we use that scheme, then we certainly need to rename this. It is an "element class"? "element model"??
    role = None # element role in its pseudo-atom model; for DNA PAM atoms
        # this can be 'strand' or 'axis' or 'unpaired-base'; not sure about Singlet
    deprecated_to = None # symbol of an element to transmute this one to, when reading mmp files; or None, or 'remove' (??)
        # (used for deprecated elements, including simulation-only elements no longer needed when modeling)
    
    def __init__(self, eltnum, sym, name, mass, rvdw, color, bn,
                 pam = None,
                 role = None,
                 deprecated_to = None ):
        """
        Note: this should only be called by class _ElementPeriodicTable
        in elements.py.

        eltnum = atomic number (e.g. H is 1, C is 6); for Singlet this is 0
        sym = (e.g.) "H"
        name = (e.g.) "Hydrogen"
        mass = atomic mass in e-27 kg
        rvdw = van der Waals radius
            [warning: vdw radius is used for display, and is changeable as a display preference!
             If we ever need to use it for chemical purposes, we'll need a separate unchanging copy
             for that!]
        color = color (RGB, 0-1)
        bn = bonding info: list of triples:
             # of bonds in this form
             covalent radius (units of 0.01 Angstrom)
             info about angle between bonds, as an array of vectors
             optional 4th item in the "triple": name of this bonding pattern, if it has one

        Note: self.bonds_can_be_directional is set for some elements
        by the caller. [In the future it may depend on the role option, or be its own option.]
        """
        # bruce 041216 and 050510 modified the above docstring
        self.eltnum = eltnum
        self.symbol = sym
        self.symbol_for_printing = sym #bruce 071106
        if sym[-1].isdigit():
            # separate symbol digits from numeric key
            self.symbol_for_printing += '-'
        self.name = name
        self.color = color
        self.mass = mass
        self.rvdw = rvdw
        # option values
        self.pam = pam
        self.role = role
        self.deprecated_to = deprecated_to
        if not deprecated_to and deprecated_to is not None:
            print "WARNING: we don't yet know what element %r should be deprecated_to" % sym
        self.atomtypes = []
        ## self.bonds = bn # not needed anymore, I hope
#         if not bn: # e.g. Helium
#             bn = [[0, 0, None]]
#         valence = bn[0][0]
#         assert type(valence) == type(1)
#         assert valence in [0,1,2,3,4,5,6,7] # in fact only up to 4 is properly supported
#         self.atomtypes = map( lambda bn_triple: AtomType( self, bn_triple, valence ), bn ) # creates cyclic refs, that's ok
#             # This is a public attr. Client code should not generally modify it!
#             # But if we someday have add_atomtype method, it can append or insert,
#             # as long as it remembers that client code treats index 0 as the default atomtype for this element.
#             # Client code is not allowed to assume a given atomtype's position in this list remains constant!
        return

    def addAtomType(self, aType):
        self.atomtypes += [aType]

    def find_atomtype(self, atomtype_name): #bruce 050511
        """
        Given an atomtype name or fullname (or an atomtype object itself)
        for this element, return the atomtype object.
        
        @param atomTypeName: The atomtype name or fullname (or an atomtype 
                             object itself) for this element. Given None, 
                             return this element's default atomtype object.
        @type  atomTypeName: str or L{AtomType}
        
        @return: The atomtype object.
        @rtype:  L{AtomType}
        
        @raise: Raise an exception (various exception types are possible)
                if no atomtype for this element matches the name (or equals
                the passed object).
        
        """
        if not atomtype_name: # permit None or "" for now
            return self.atomtypes[0]
        for atomtype in self.atomtypes: # in order from [0], though this should not matter since at most one should match
            if atomtype.name == atomtype_name or atomtype.fullname == atomtype_name or atomtype == atomtype_name:
                return atomtype # we're not bothering to optimize for atomtype_name being the same obj we return
        assert 0, "%r is not a valid atomtype name or object for %s" % (atomtype_name, self.name)
    
    def findAtomType(self, atomTypeName):
        """
        Given an atomtype name or fullname (or an atomtype object itself)
        for this element, return the atomtype object.
        
        Same as L{find_atomtype()}, provided for convenience.
        
        @param atomTypeName: The atomtype name or fullname (or an atomtype 
                             object itself) for this element. Given None, 
                             return this element's default atomtype object.
        @type  atomTypeName: str or L{AtomType}
        
        @return: The atomtype object.
        @rtype:  L{AtomType}
        
        @raise: Raise an exception (various exception types are possible)
                if no atomtype for this element matches the name (or equals 
                the passed object).
        """
        return self.find_atomtype(atomTypeName)
        
    def __repr__(self):
        return "<Element: " + self.symbol + "(" + self.name + ")>"

    pass

# end
