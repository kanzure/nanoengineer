# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
bond_utils.py

Helper functions for bonds, including UI code.

$Id$

History:

created by bruce 050705 to help with higher-order bonds for Alpha6.
'''
__author__ = "bruce"


###e needs cvs add

from VQT import Q
from constants import noop
from bonds import bond_type_names, bond_letter_from_v6, v6_from_btype, btype_from_v6, bonded_atoms_summary

def possible_bond_types(bond):
    "Return a list of names of possible bond types for the given bond, based on its atomtypes."
    spX = max( bond.atom1.atomtype.spX, bond.atom2.atomtype.spX )
        # simplest (max) atomtype determines set of possible bond types
    if spX == 3:
        return ['single']
    elif spX == 2:
        return ['single', 'double', 'aromatic', 'graphite']
    elif spX == 1:
        return ['single', 'double', 'aromatic', 'triple', 'carbomer']
    assert 0, "spX should be in range 1-3, not %r, for %r" % (spX, bond)

def bond_menu_section(bond, quat = Q(1,0,0,0)):
    """Return a menu_spec subsection for displaying info about a highlighted bond,
    changing its bond_type, offering commands about it, etc.
    If given, use the quat describing the rotation used for displaying it
    to order the atoms in the bond left-to-right (e.g. in text strings).
    """
    res = []
    res.append(( bonded_atoms_summary(bond, quat = quat), noop, 'disabled' ))
    res.append( bond_type_submenu_spec(bond) )
    return res

def bond_type_submenu_spec(bond): #bruce 050705 (#e add options??)
    """Return a menu_spec for changing the bond_type of this bond,
    or if that is unchangeable, a disabled menu item for displaying the type.
    """
    v6 = bond.v6
    btype0 = btype_from_v6(v6)
    poss = possible_bond_types(bond)
    maintext = 'Bond Type: %s' % btype0
    if btype0 not in poss or len(poss) > 1:
        # use the menu
        submenu = []
        for btype in poss: # don't include current value if it's illegal
            subtext = btype
            command = ( lambda arg1=None, arg2=None, btype=btype, bond=bond: apply_btype_to_bond(btype, bond) )
            checked = (btype == btype0)
            disabled = False # might change this if some neighbor bonds are locked, or if we want to show non-possible choices
            submenu.append(( subtext, command,
                             disabled and 'disabled' or None,
                             checked and 'checked' or None ))
        return ( maintext, submenu)
    else:
        # only one value is possible, and it's the current value -- just show it
        return ( maintext, noop, 'disabled' )
    pass
    
def apply_btype_to_bond(btype, bond):
    """Apply the given legal bond-type name (e.g. 'single') to the given bond, and do whatever inferences are presently allowed.
    [#e should the inference policy and/or some controlling object be another argument? Maybe even a new first arg 'self'?]
    """
    v6 = v6_from_btype(btype)
    bond.set_v6(v6) # this doesn't affect anything else or do any checks ####k #####@@@@@ check that
    ##e now do some more...
    return

# end
