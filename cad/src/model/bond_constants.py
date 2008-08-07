# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
bond_constants.py -- constants and simple functions for use with class Bond
(which can be defined without importing that class).

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

050429 - Started out as part of bonds.py. Gradually extended.

050707 - Split into separate file, largely to avoid recursive import problems
(since these constants need to be imported by many bond-related modules).
Many of them are still imported via bonds module, by code in other modules.

050920 - Full mmp support for Carbomeric bonds.
[FYI: As of today, sim executable reportedly accepts them and uses same params
as for bond2.]
"""

from math import floor, ceil

from geometry.VQT import Q
from utilities.debug import print_compact_traceback    
from utilities import debug_flags
import foundation.env as env
from simulation.PyrexSimulator import thePyrexSimulator

# ==

# Bond valence constants -- exact ints, 6 times the numeric valence they represent.
# If these need an order, their standard order is the same as the order of their numeric valences
# (as in the constant list BOND_VALENCES).

V_SINGLE = 6 * 1
V_GRAPHITE = 6 * 4/3  # (this can't be written 6 * (1+1/3) or 6 * (1+1/3.0) - first one is wrong, second one is not an exact int)
V_AROMATIC = 6 * 3/2
V_DOUBLE = 6 * 2
V_CARBOMERIC = 6 * 5/2 # for the bonds in a carbomer of order 2.5 (which alternate with aromatic bonds); saved as bondc as of 050920
V_TRIPLE = 6 * 3

V_UNKNOWN = 6 * 7/6 # not in most tables here, and not yet used; someday might be used internally by bond-type inference code

BOND_VALENCES = [V_SINGLE, V_GRAPHITE, V_AROMATIC, V_DOUBLE, V_CARBOMERIC, V_TRIPLE]
    # when convenient (e.g. after A8), V_GRAPHITE should be renamed to V_GRAPHITIC [bruce 060629]
BOND_MMPRECORDS = ['bond1', 'bondg', 'bonda', 'bond2', 'bondc', 'bond3']
    # (Some code might assume these all start with "bond".)
    # (These mmp record names are also hardcoded into mmp-reading code in files_mmp.py.)
bond_type_names = {V_SINGLE:'single', V_DOUBLE:'double', V_TRIPLE:'triple',
                   V_AROMATIC:'aromatic', V_GRAPHITE:'graphitic', V_CARBOMERIC:'carbomeric'}

BOND_VALENCES_HIGHEST_FIRST = list(BOND_VALENCES)
BOND_VALENCES_HIGHEST_FIRST.reverse()

V_ZERO_VALENCE = 0 # used as a temporary valence by some code

BOND_LETTERS = ['?'] * (V_TRIPLE+1) # modified just below, to become a string; used in initial Bond.draw method via bond_letter_from_v6

for v6, mmprec in zip( BOND_VALENCES, BOND_MMPRECORDS ):
    BOND_LETTERS[v6] = mmprec[4] # '1','g',etc
    # for this it's useful to also have '?' for in-between values but not for negative or too-high values,
    # so a list or string is more useful than a dict

assert BOND_LETTERS[V_CARBOMERIC] == 'c' # not 'a', not 'b'

BOND_LETTERS[0] = '0' # see comment in bond_letter_from_v6

BOND_LETTERS = "".join(BOND_LETTERS)
    ## print "BOND_LETTERS:",BOND_LETTERS # 0?????1?ga??2?????3

BOND_MIN_VALENCES = [ 999.0] * (V_TRIPLE+1) #bruce 050806; will be modified below
BOND_MAX_VALENCES = [-999.0] * (V_TRIPLE+1)

bond_valence_epsilon = 1.0 / 64 # an exact float; arbitrary, but must be less than 1/(2n) where no atom has more than n bonds

for v6 in BOND_VALENCES:
    if v6 % V_SINGLE == 0: # exact valence
        BOND_MIN_VALENCES[v6] = BOND_MAX_VALENCES[v6] = v6 / 6.0
    else:
        # non-integral (and inexact) valence
        BOND_MIN_VALENCES[v6] = floor(v6 / 6.0) + bond_valence_epsilon
        BOND_MAX_VALENCES[v6] = ceil(v6 / 6.0)  - bond_valence_epsilon
    pass

BOND_MIN_VALENCES[V_UNKNOWN] = 1.0 # guess, not yet used
BOND_MAX_VALENCES[V_UNKNOWN] = 3.0 # ditto

# constants returned as statuscode by Atom.directional_bond_chain_status()
# [bruce 071016]
DIRBOND_CHAIN_MIDDLE = 'middle'
DIRBOND_CHAIN_END = 'end'
DIRBOND_NONE = None
DIRBOND_ERROR = 'error'

# ==

# [Note: the functions atoms_are_bonded and find_bond, were moved
#  from bonds.py to here (to remove an import cycle) by bruce 071216;
#  I also removed the old alias 'bonded' for atoms_are_bonded,
#  since 'bonded' is too generic to be searched for.]

def atoms_are_bonded(a1, a2):
    """
    Are these atoms (or singlets) already directly bonded?
    [AssertionError if they are the same atom.]
    """
    #bruce 041119 #e optimized by bruce 050502 (which indirectly added "assert a1 is not a2")
    ## return a2 in a1.neighbors()
    return not not find_bond(a1, a2)

def find_bond(a1, a2):
    """
    If a1 and a2 are bonded, return their Bond object; if not, return None.
    [AssertionError if they are the same atom.]
    """
    #bruce 050502; there might be an existing function in some other file, to merge this with
    assert a1 is not a2
    for bond in a1.bonds:
        if bond.atom1 is a2 or bond.atom2 is a2:
            return bond
    return None

def find_Pl_bonds(atom1, atom2):
    #bruce 080409 moved this here to clear up an import cycle
    """
    return the two bonds in atom1-Pl5-atom2,
    or (None, None) if that structure is not found.
    """
    for bond1 in atom1.bonds:
        Pl = bond1.other(atom1)
        if Pl.element.symbol == 'Pl5': # avoid import of model.elements
            bond2 = find_bond(Pl, atom2)
            if bond2:
                return bond1, bond2
    return None, None

# ==

def min_max_valences_from_v6(v6):
    return BOND_MIN_VALENCES[v6], BOND_MAX_VALENCES[v6]

def valence_to_v6(valence): #bruce 051215
    """
    Given a valence (int or float, single bond is 1 or 1.0),
    return it as a v6, being careful about rounding errors.
    """
    return int(valence * V_SINGLE + 0.01) # kluge: 0.01 is based on knowledge of scale of V_SINGLE (must be > 0, < 1/V_SINGLE)

def bond_letter_from_v6(v6): #bruce 050705
    """
    Return a bond letter summarizing the given v6,
    which for legal values is one of 1 2 3 a g b,
    and for illegal values is one of - 0 ? +
    """
    try:
        ltr = BOND_LETTERS[v6]
            # includes special case of '0' for v6 == 0,
            # which should only show up for transient states that are never drawn, except in case of bugs
    except IndexError: # should only show up for transient states...
        if v6 < 0:
            ltr = '-'
        else:
            ltr = '+'
    return ltr

def btype_from_v6(v6): #bruce 050705
    """
    Given a legal v6, return 'single', 'double', etc.
    For illegal values, return 'unknown'.
    For V_CARBOMERIC this returns 'carbomeric', not 'aromatic'.
    """
    try:
        return bond_type_names[v6]
    except KeyError:
        if debug_flags.atom_debug:
            print "atom_debug: illegal bond v6 %r, calling it 'unknown'" % (v6,)
        return 'unknown' #e stub for this error return; should it be an error word like this, or single, or closest legal value??
    pass

def invert_dict(dict1): #bruce 050705
    res = {}
    for key, val in dict1.items():
        res[val] = key
    return res

bond_type_names_inverted = invert_dict(bond_type_names)

def v6_from_btype(btype): #bruce 050705
    """
    Return the v6 corresponding to the given bond-type name
    ('single', 'double', etc). Exception if name not legal.
    """
    return bond_type_names_inverted[btype]

_bond_arrows = {
    0: "<- ->".split(),
    1: "-- ->".split(), # from atom1 to atom2, i.e. to the right
   -1: "<- --".split(),
}
    
def bonded_atoms_summary(bond, quat = Q(1,0,0,0)): #bruce 050705; direction feature, bruce 070414. ###e SHOULD CALL bond_left_atom
    """
    Given a bond, and an optional quat describing the orientation it's shown in,
    order the atoms left to right based on that quat,
    and return a text string summarizing the bond
    in the form C26(sp2) <-2-> C34(sp3) or so,
    leaving out the < or > if the bond has a direction.
    """
    a1 = bond.atom1
    a2 = bond.atom2
    direction = bond._direction
    vec = a2.posn() - a1.posn()
    vec = quat.rot(vec)
    if vec[0] < 0.0:
        a1, a2 = a2, a1
        direction = - direction
    a1s = describe_atom_and_atomtype(a1)
    a2s = describe_atom_and_atomtype(a2)
    bondletter = bond_letter_from_v6(bond.v6)
    if bondletter == '1':
        bondletter = ''
    arrows = _bond_arrows.get(direction, ("<-", " (invalid direction) ->"))
    return "%s %s%s%s %s" % (a1s, arrows[0], bondletter, arrows[1], a2s)
    
def bond_left_atom(bond, quat = Q(1,0,0,0)): #bruce 070415, modified from bonded_atoms_summary, which ought to call this now ##e
    # TODO: make this method name clearer: bond_leftmost_atom? bond_get_atom_on_left? [bruce 080807 comment]
    """
    Given a bond, and an optional quat describing the orientation it's shown in,
    order the atoms left to right based on that quat
    (i.e. as the bond would be shown on the screen using it),
    and return the leftmost atom.
    """
    a1 = bond.atom1
    a2 = bond.atom2
    vec = a2.posn() - a1.posn()
    vec = quat.rot(vec)
    if vec[0] < 0.0:
        a1, a2 = a2, a1
    return a1

def describe_atom_and_atomtype(atom): #bruce 050705, revised 050727 #e refile?
    """
    If a standard atom, return a string like C26(sp2) with atom name and
    atom hybridization type, but only include the type if more than one is 
    possible for the atom's element and the atom's type is not the default 
    type for that element.
    
    If a PAM Ss or Sj atom, returns a string like Ss28(A) with atom name
    and dna base name. 
    
    @deprecated: For some purposes use L{Atom.getInformationString()} instead.
                 (But for others, that might not be suitable. Needs review.)
    """
    res = str(atom)
    if atom.atomtype is not atom.element.atomtypes[0]:
        res += "(%s)" % atom.atomtype.name
    if atom.getDnaBaseName():
        res += "(%s)" % atom.getDnaBaseName()
    
    return res

# ==

_bond_params = {} # maps triple of atomtype codes and v6 to (rcov1, rcov2) pairs

def bond_params(atomtype1, atomtype2, v6 = V_SINGLE):
    #bruce 060324 for bug 900; made v6 optional, 080405
    """
    Given two atomtypes and an optional bond order encoded as v6,
    look up or compute the parameters for that kind of bond.
    For now, the return value is just a pair of numbers, rcov1 and rcov2,
    for use as the covalent radii for atom1 and atom2 respectively for this kind of bond
    (with their sum adjusted to the equilibrium bond length if this is known).
    """
    atcode1 = id(atomtype1)
        # maybe: add a small int code attr to atomtype, for efficiency
    atcode2 = id(atomtype2)
    try:
        return _bond_params[(atcode1, atcode2, v6)]
    except KeyError:
        res = _bond_params[(atcode1, atcode2, v6)] = \
              _compute_bond_params(atomtype1, atomtype2, v6)
        return res
    pass

def ideal_bond_length(atom1, atom2, v6 = V_SINGLE): #bruce 080404
    """
    Return the ideal bond length between atom1 and atom2 (using their
    current atomtypes) for a bond of the given order (default V_SINGLE).
    The atoms need not be bonded; if they are, that bond's current order
    is ignored. [review: revise that rule, to use it if they are bonded??]
    
    (Use bond_params, which uses getEquilibriumDistanceForBond if ND-1
     is available.)
    """
    rcov1, rcov2 = bond_params(atom1.atomtype, atom2.atomtype, v6)
    return rcov1 + rcov2

def _compute_bond_params(atomtype1, atomtype2, v6): #bruce 080405 revised this
    """
    [private helper function for bond_params]
    """
    # note: this needn't be fast, since its results for given arguments
    # are cached for the entire session by the caller.
    # (note: as of 041217 rcovalent is always a number; it's 0.0 for Helium,
    #  etc, so for nonsense bonds like He-He the entire bond is drawn as if
    #  "too long". [review: what should we do for a nonsense bond like C-He?])
    rcov1 = atomtype1.rcovalent
    rcov2 = atomtype2.rcovalent
    rcovsum = rcov1 + rcov2 # ideal length according to our .rcovalent tables,
        # used as a fallback if we can't get a better length
    if not rcovsum:
        print "error: _compute_bond_params for nonsense bond:", \
              atomtype1, atomtype2, v6
        rcov1 = rcov2 = 0.5 # arbitrary
        rcovsum = rcov1 + rcov2
    # now adjust rcov1 and rcov2 to make their sum the equilibrium bond length
    # [bruce 060324 re bug 900]
    eltnum1 = atomtype1.element.eltnum
        # note: both atoms and atomtypes have .element
    eltnum2 = atomtype2.element.eltnum
    ltr = bond_letter_from_v6(v6)
    
    # determine ideal bond length (special case for one element being Singlet)
    assert eltnum1 or eltnum2, "can't bond bondpoints to each other"
    if eltnum1 == 0 or eltnum2 == 0:
        # one of them is Singlet (bondpoint); getEquilibriumDistanceForBond
        # doesn't know about those, so work around this by using half the
        # distance for a bond from the non-Singlet atomtype to itself
        eltnum = eltnum1 or eltnum2
        nicelen = _safely_call_getEquilibriumDistanceForBond( eltnum, eltnum, ltr)
        if nicelen:
            nicelen = nicelen / 2.0
    else:
        nicelen = _safely_call_getEquilibriumDistanceForBond( eltnum1, eltnum2, ltr)
    if nicelen is None:
        # the call failed, use our best guess
        nicelen = rcovsum
    assert nicelen > 0.0
    # now adjust rcov1 and rcov2 so their sum equals nicelen
    # (this works even if one of them is 0, presumably for a bondpoint)
    ratio = nicelen / float(rcovsum)
    rcov1 *= ratio
    rcov2 *= ratio
    
    return rcov1, rcov2

def _safely_call_getEquilibriumDistanceForBond( eltnum1, eltnum2, ltr): #bruce 080405 split this out
    """
    #doc
    eg: args for C-C are (6, 6, '1')

    @return: ideal length in Angstroms (as a positive float),
             or None if the call of getEquilibriumDistanceForBond failed
    """
    try:
        pm = thePyrexSimulator().getEquilibriumDistanceForBond(eltnum1,
                                                               eltnum2,
                                                               ltr)
        assert pm > 2.0, "too-low pm %r for getEquilibriumDistanceForBond%r" % \
               (pm, (eltnum1, eltnum2, ltr))
            # 1.0 means an error occurred; 2.0 is still ridiculously low
            # [not as of 070410]; btw what will happen for He-He??
            # update 070410: it's 1.8 for (202, 0, '1').
            # -- but a new sim-params.txt today changes the above to 170
        nicelen = pm / 100.0 # convert picometers to Angstroms
        return nicelen
    except:
        # be fast when this happens a lot (not important now that our retval
        # is cached, actually; even so, don't print too much)
        if not env.seen_before("error in getEquilibriumDistanceForBond"):
            #e include env.redraw_counter to print more often? no.
            msg = "bug: ignoring exceptions when using " \
                  "getEquilibriumDistanceForBond, like this one: "
            print_compact_traceback(msg)
        return None
    pass
    
# ==

# Here's an old long comment which is semi-obsolete now [050707], but which motivates the term "v6".
# Note that I'm gradually replacing the term "bond valence" with whichever of "bond order" or "bond type"
# (related but distinct concepts) is appropriate. Note also that all the bond orders we deal with in this code
# are "structural bond orders" (used by chemists to talk about bonding structure), not "physical bond orders"
# (real numbers related to estimates of occupancy of molecular orbitals by electrons).

#bruce 050429: preliminary plan for higher-valence bonds (might need a better term for that):
#
# - Bond objects continue to compare equal when on same pair of atoms (even if they have a
# different valence), and (partly by means of this -- probably it's a kluge) they continue
# to allow only one Bond between any two atoms (two real atoms, or one real atom and one singlet).
#
# - I don't think we need to change anything basic about "internal vs external bonds",
# coordinates, basic inval/draw schemes (except to properly draw new kinds of bonds),
# etc. (Well, not due to bond valence -- we might change those things for other reasons.)
#
# - Each Bond object has a valence. Atoms often sum the valences of their bonds
# and worry about this, but they no longer "count their bonds" -- at least not as a
# substitute for summing the valences. (To prevent this from being done by accident,
# we might even decide that their list of bonds is not really a list, at least temporarily
# while this is being debugged. #?)
#
# This is the first time bonds have any state that needs to be saved,
# except for their existence between their two atoms. This will affect mmpfile read/write,
# copying of molecules (which needs rewriting anyway, to copy jigs/groups/atomsets too),
# lots of things about depositMode, maybe more.
#
# - Any bond object can have its valence change over time (just as the coords,
# elements, or even identities of its atoms can also change). This makes it a lot
# easier to write code which modifies chemical structures in ways which preserve (some)
# bonding but with altered valence on some bonds.
#
# - Atoms might decide they fit some "bonding pattern" and reorder
# their list of bonds into a definite order to match that pattern (this is undecided #?).
# This might mean that code which replaces one bond with a same-valence bond should do it
# in the same place in the list of bonds (no idea if we even have any such code #k).
#
# - We might also need to "invalidate an atom's bonding pattern" when we change anything
# it might care about, about its bonds or even its neighboring elements (two different flags). #?
#
# - We might need to permit atoms to have valence errors, either temporarily or permanently,
# and keep track of this. We might distinguish between "user-permitted" or even "user-intended"
# valence errors, vs "transient undesired" valence errors which we intend to automatically
# quickly get rid of. If valence errors can be long-lasting, we'll want to draw them somehow.
# 
# - Singlets still require exactly one bond (unless they've been killed), but it can have
# any valence. This might affect how they're drawn, how they consider forming new bonds
# (in extrude, fuse chunks, depositMode, etc), and how they're written into sim-input mmp files.
#
# - We represent the bond valence as an integer (6 times the actual valence), since we don't
# want to worry about roundoff errors when summing and comparing valences. (Nor to pay the speed
# penalty for using exactly summable python objects that pretend to have the correct numeric value.)
#
# An example of what we don't want to have to worry about:
#
#   >>> 1/2.0 + 1/3.0 + 1/6.0
#   0.99999999999999989
#   >>> _ >= 1.0
#   False
#
# We do guarantee to all code using these bond-valence constants that they can be subtracted
# and compared as numbers -- i.e. that they are "proportional" to the numeric valence.
# Some operations transiently create bonds with unsupported values of valence, especially bonds
# to singlets, and this is later cleaned up by the involved atoms when they update their bonding
# patterns, before those bonds are ever drawn. Except for bugs or perhaps during debugging,
# only standard-valence bonds will ever be drawn, or saved in files, or seen by most code.

# ==

# end
