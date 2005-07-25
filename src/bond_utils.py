# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
bond_utils.py

Helper functions for bonds, including UI code.

$Id$

History:

created by bruce 050705 to help with higher-order bonds for Alpha6.
'''
__author__ = "bruce"


from VQT import Q
from constants import noop
from bond_constants import *

def intersect_sequences(s1, s2):
    return filter( lambda s: s in s2, s1)

def possible_bond_types(bond):
    """Return a list of names of possible bond types for the given bond,
    based on its atoms' current elements and atomtypes.
       This list is never empty since single bonds are always possible
    (even if they always induce valence errors, e.g. for H bonded to O(sp2) or in O2).
       For warnings about some choices of bond type (e.g. S=S), see the function bond_type_warning.
       [###e we might extend this to optionally also permit bonds requiring other atomtypes
    if those are reachable by altering only open bonds on this bond's actual atoms.]
       Warning: this ignores geometric issues, so it permits double bonds even if they
    would be excessively twisted, and it ignores bond length, bond arrangement in space
    around each atom, etc.
    """
    s1 = bond.atom1.atomtype.permitted_v6_list
    s2 = bond.atom2.atomtype.permitted_v6_list
    s12 = intersect_sequences( s1, s2 )
        #e could be faster (since these lists are prefixes of a standard order), but doesn't need to be
    return map( btype_from_v6, s12)
    
#obs, partly:
#e should we put element rules into the above possible_bond_types, or do them separately?
# and should bonds they disallow be shown disabled, or not even included in the list?
# and should "unknown" be explicitly in the list?

def bond_type_warning(bond, btype): # 050707
    """Return a warning (short text suitable to be added to menu item text), or "" for no warning,
    about the use of btype (bond type name) for bond.
    This can be based on its atomtypes or perhaps on more info about the surroundings
    (#e we might need to add arguments to pass such info).
       Presently, this only warns about S=S being unstable, and about bonds whose type could not
    permit both atoms (using their current atomtypes) to have the right valence
    regardless of their other bonds (which only happens now when they have no other bonds).
       This might return warnings for illegal btypes, even though it's not presently called
    for illegal btypes for the given bond. It doesn't need to return any warning for illegal btypes.
    """
    atype1 = bond.atom1.atomtype
    atype2 = bond.atom2.atomtype
    if btype == 'double' and atype1.is_S_sp2 and atype2.is_S_sp2:
        return "unstable"
    elif btype == 'single' and (atype1.bond1_is_bad or atype2.bond1_is_bad):
        return "bad valence"
    elif btype != 'triple' and (atype1.is_N_sp or atype2.is_N_sp):
        return "bad valence"
    # if there are any other numbonds=1 atoms which show up here, they should be valence-checked too (generalizing the above)
    # (which might be easiest if atomtype stores a "valence-permitted btypes" when numbonds is 1), but I don't think there are others
    return ""
    
def bond_menu_section(bond, quat = Q(1,0,0,0)):
    """Return a menu_spec subsection for displaying info about a highlighted bond,
    changing its bond_type, offering commands about it, etc.
    If given, use the quat describing the rotation used for displaying it
    to order the atoms in the bond left-to-right (e.g. in text strings).
    """
    res = []
    res.append(( bonded_atoms_summary(bond, quat = quat), noop, 'disabled' ))
    ## res.append( bond_type_submenu_spec(bond) )
    res.extend( bond_type_menu_section(bond) )
    return res

def bond_type_menu_section(bond): #bruce 050716; replaces bond_type_submenu_spec for Alpha6
    """Return a menu_spec for changing the bond_type of this bond
    (as one or more checkmark items, one per permitted bond-type given the atomtypes),
    or if the bond-type is unchangeable, a disabled menu item for displaying the type
    (which looks the same as when the bond type is changeable, except for being disabled).
    (If the current bond type is not permitted, it's still present and checked, but disabled,
     and it might have a warning saying it's illegal.)
    """
    v6 = bond.v6
    btype_now = btype_from_v6(v6)
    poss = possible_bond_types(bond) # a list of strings which are bond-type names
    ##e could put weird ones (graphitic, carbomeric) last and/or in parens, in subtext below
    types = list(poss)
    if btype_now not in poss:
        types.append(btype_now) # put this one last, since it's illegal; warning for it is computed later
    assert len(types) > 0
    # types is the list of bond types for which to make menu items, in order;
    # now make them, and figure out which ones are checked and/or disabled;
    # we disable even legal ones iff there is only one bond type in types
    # (which means, if current type is illegal, the sole legal type is enabled).
    disable_legal_types = (len(types) == 1)
    res = []
    for btype in types: # include current value even if it's illegal
        subtext = "%s bond" % btype # this string might be extended below
        checked = (btype == btype_now)
        command = ( lambda arg1=None, arg2=None, btype=btype, bond=bond: apply_btype_to_bond(btype, bond) )
        if btype not in poss:
            # illegal btype (note: it will be the current one, and thus be the only checked one)
            warning = "illegal"
            disabled = True
        else:
            # legal btype
            warning = bond_type_warning(bond, btype) # might be "" (or None??) for no warning
            disabled = disable_legal_types
                # might change this if some neighbor bonds are locked, or if we want to show non-possible choices
        if warning:
            subtext += " (%s)" % warning
        res.append(( subtext, command,
                         disabled and 'disabled' or None,
                         checked and 'checked' or None ))
    ##e if >1 legal value, maybe we should add a toggleable checkmark item to permit "locking" the bond to its current bond type
    return res

def bond_type_submenu_spec(bond): #bruce 050705 (#e add options??); probably not used in Alpha6
    """Return a menu_spec for changing the bond_type of this bond,
    or if that is unchangeable, a disabled menu item for displaying the type.
    """
    v6 = bond.v6
    btype0 = btype_from_v6(v6)
    poss = possible_bond_types(bond) # a list of strings which are bond-type names
    ##e could put weird ones (graphitic, carbomeric) last and/or in parens, in subtext below
    maintext = 'Bond Type: %s' % btype0
    if btype0 not in poss or len(poss) > 1:
        # use the menu
        submenu = []
        for btype in poss: # don't include current value if it's illegal
            subtext = btype
            warning = bond_type_warning(bond, btype)
            if warning:
                subtext += " (%s)" % warning
            command = ( lambda arg1=None, arg2=None, btype=btype, bond=bond: apply_btype_to_bond(btype, bond) )
            checked = (btype == btype0)
            disabled = False # might change this if some neighbor bonds are locked, or if we want to show non-possible choices
            submenu.append(( subtext, command,
                             disabled and 'disabled' or None,
                             checked and 'checked' or None ))
        ##e if >1 legal value could add checkmark item to permit "locking" this bond type
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
    bond.changed()
    return

# end
