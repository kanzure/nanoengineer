# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
bonds_from_atoms.py -- experimental code for inferring bonds from
atom positions and elements alone

@author: Dr. K. Eric Drexler
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050906 translated into Python some Lisp code
contributed by Dr. K. Eric Drexler.

bruce 071030 moved inferBonds interface to that code (probably by Will) here,
from bonds.py.

TODO: make this directly accessible as one or more user operations.
(As of 071030 it's only used when importing some PDB files.)
"""

# Translation into Python of Lisp code contributed by Dr. K. Eric Drexler.
# Some comments are from contributed code, perhaps paraphrased.

#e Plans: for efficiency, we'll further translate this into Pyrex or C, and/or combine
# with atom-position hashtable rather than scanning all pairs of atoms.
# This implem is just for testing and experimentation.

# This code does not yet consider the possibility of non-sp3 atomtypes,
# and will need changes to properly handle those.
# For now it ignores existing atomtypes and creates new bonds appropriate for sp3
# perhaps plus some extra too-long bonds at the end, if permitted by valence.

import math

from geometry.VQT import vlen
from geometry.VQT import atom_angle_radians

import foundation.env as env

from model.bonds import bond_atoms_faster
from geometry.NeighborhoodGenerator import NeighborhoodGenerator

from model.bond_constants import atoms_are_bonded # was: from bonds import bonded
from model.bond_constants import V_SINGLE
from model.bond_constants import bond_params

# constants; angles are in radians

degrees = math.pi / 180

TARGET_ANGLE = 114 * degrees  #e this will probably need to be generalized for non-sp3 atoms
MIN_BOND_ANGLE = 30 * degrees # accepts moderately distorted three-membered rings
ANGLE_ACCEPT_DIST = 0.9       # ignore angle cutoff below this distance (in Angstroms)
MAX_DIST_RATIO_HUNGRY = 2.0   # prohibit bonds way longer than their proper length
MAX_DIST_RATIO_NON_HUNGRY = 1.4   # prohibit bonds a little longer than their proper length
DIST_COST_FACTOR = 5.0        # multiplier on square of distance-ratio beyond optimal

# (utilities used by contributed code, defined differently for nE-1)

def atm_distance(atom1, atom2):
    return vlen(atom1.posn() - atom2.posn())

atm_angle = atom_angle_radians # args are three atoms

# utility for creating mutable linked lists in Python
def linked_list( lis1, func = None ):
    """
    Given a list of 0 or more elements (e.g. [a,b,c,d]),
    return a "python mutable linked list" of the form [a, [b, [c, [d, None]]]].
       If func is supplied, apply it to each element of the original list
    (e.g. return [f(a),[f(b),[f(c),[f(d),None]]]] for f = func).
       Note that we terminate the resulting linked list with None, not [] or f(None).
    It might be easier for some applications (which want to append elements to the result,
    leaving it in linked list form) if we terminated with [], so this is a possible future change in API.
    """
    assert type(lis1) == type([])
    lis1.reverse()
    res = None # correct result for 0-length lis1
    for elt in lis1:
        if func is not None:
            elt = func(elt)
        res = [elt, res]
    return res

#e unlink_list?

def idealBondLength(atm1, atm2):
    """
    Return the ideal length of a single bond between atm1 and atm2,
    assuming they have their current elements but their default atomtypes
    (ignoring their current atomtypes).

    @see: similar function, ideal_bond_length in bond_constants.py
          (not directly useable by this function)
    """
    # don't use getEquilibriumDistanceForBond directly, in case pyrex sim (ND-1)
    # is not available [bruce 060620]
    r1, r2 = bond_params(atm1.element.atomtypes[0], atm2.element.atomtypes[0], V_SINGLE)
    return r1 + r2

def max_atom_bonds(atom, special_cases={'H':  1,
                                        'B':  4,
                                        'C':  4,
                                        'N':  4,
                                        'O':  2,
                                        'F':  1,
                                        'Si': 4,
                                        'P':  5,
                                        'S':  4,
                                        'Cl': 1}):   # coded differently for nE-1
    """
    Return max number of bonds permitted on this atom, based only on its element
    (for any atomtype, ignoring current atomtype of atom). (Returns 0 for noble gases.)
    """
    elt = atom.element
    sym = elt.symbol
    if special_cases.has_key(sym):
        return special_cases[sym]
    else:
        maxbonds = 0
        for atype in elt.atomtypes:
            if atype.numbonds > maxbonds:
                maxbonds = atype.numbonds
        return maxbonds

def min_atom_bonds(atom): # coded differently for nE-1
    """
    Return min number of bonds permitted on this atom, based only on its element
    (for any atomtype, ignoring current atomtype of atom). (Returns 0 for noble gases.)
    That is, find the atomtype with the smallest number of bonds (e.g. sp for carbon,
    which can have just two double bonds) and return that number of bonds. This is the
    smallest number of bonds that could possibly make this element happy.
    """
    minbonds = 10000
    for atype in atom.element.atomtypes:
        if atype.numbonds < minbonds:
            minbonds = atype.numbonds
    return minbonds

"""
Eric D writes: If the bond-number limit for each atom is based on its
atom-type, rather than on its element-type, there should be no
problem. Or, if atom-types are unknown, then we can use the maximum
valence for that atom that occurs in non-exotic chemistry. Damian
should cross-check this, but I'd use:

H  1
B  4
C  4
N  4
O  2
F  1
Si 4
P  5
S  4
Cl 1

Many elements can have any one of several atomtypes based on
hybridization. Our concepts of these appear in the _mendeleev table in
elements.py. So for each element there is a minimum number of possible
bonds and a maximum number of possible bonds; for carbon these are
respectively 2 (two double bonds for sp hybridization) and 4 (sp3).

There are two things that could be the independent variable. Either
you derive the atomtype from the number of bonds, or you hold the
atomtype fixed and permit only the number of bonds it allows.

Currently max_atom_bonds() is looking at
atom.element.atomtypes[0].numbonds to determine how many bonds are OK
for this atom. That presumes the first atomtype permits the most bonds,
which is presently [and still, 071101] true, but it would be better
to take an explicit maximum.

So we DO want the maximum number of bonds for ANY atomtype for this
element, with the presumption that somebody else will later
rehybridize the atom to get the right atomtype. We don't need to do
that here.

The other messy thing is this: If we know we don't have enough bonds
for the element (i.e. fewer than the smallest number of bonds for any
of its atomtypes) then we should use MAX_DIST_RATIO = 2.0 because we
are hungry for more bonds. When we get enough for the minimum, we
reduce MAX_DIST_RATIO to 1.4 because we're not so hungry any more.

MAX_DIST_RATIO is used in two places. One is in list_potential_bonds,
where we clearly want this policy. (Complication: there are two
atoms involved - we will use the smaller value only when BOTH are
non-hungry.) The other place is atm_distance_cost, another case
where there are two atoms involved. I think it applies there too.
"""

def max_dist_ratio(atm1, atm2):
    def is_hungry(atm):
        return len(atm.realNeighbors()) < min_atom_bonds(atm)
    if is_hungry(atm1) or is_hungry(atm2):
        return MAX_DIST_RATIO_HUNGRY
    else:
        return MAX_DIST_RATIO_NON_HUNGRY

def bondable_atm(atom): # coded differently for nE-1 due to open bonds
    """
    Could this atom accept any more bonds
    (assuming it could have any of its atomtypes,
     and ignoring positions and elements of atoms it's already bonded to,
     and ignoring open bonds,
     and treating all existing bonds as single bonds)?
    """
    #e len(atom.bonds) would be faster but would not ignore open bonds;
    # entire alg could be recoded to avoid ever letting open bonds exist,
    # and then this could be speeded up.
    return len(atom.realNeighbors()) < max_atom_bonds(atom)

def bond_angle_cost(angle, accept, bond_length_ratio):
    """
    Return the cost of the given angle, or None if that cost is infinite.
    Note that the return value can be 0.0, so callers should only
    test it for "is None", not for its boolean value.
       If accept is true, don't use the minimum-angle cutoff (i.e. no angle
    is too small to be accepted).
    """
    # if bond is too short, bond angle constraint changes
    if not (accept or angle > MIN_BOND_ANGLE * 1.0 + (2.0 * max(0.0, bond_length_ratio - 1.0)**2)):
        return None
    diff = min(0.0, angle - TARGET_ANGLE) # for heuristic cost, treat all angles as approximately tetrahedral
    square = diff * diff
    if 0.0 < diff:
        # wide angle
        return square
    else:
        # tight angle -- larger quadratic penalty
        return 2.0 * square

def atm_angle_cost(atm1, atm2, ratio):
    """
    Return total cost of all bond-angles which include the atm1-atm2 bond
    (where one bond angle is said to include the two bonds whose angle it describes);
    None means infinite cost.
    """
    accept = atm_distance(atm1, atm2) < ANGLE_ACCEPT_DIST
    sum = 0.0
    for atm in atm1.realNeighbors():
        cost = bond_angle_cost( atm_angle(atm, atm1, atm2), accept, ratio)
        if cost is None: # cost can be 0.0, so don't use a boolean test here [bruce 050906]
            return None
        sum += cost
    for atm in atm2.realNeighbors():
        # note different order of atm2, atm1
        cost = bond_angle_cost( atm_angle(atm, atm2, atm1), accept, ratio)
        if cost is None:
            return None
        sum += cost
    return sum

covrad_table = dict( [
    # from webelements.com (via contributed code)
    ('H',  0.37),
    ('C',  0.77), ('N', 0.75), ('O', 0.73), ('F',  0.72),
    ('Si', 1.11), ('P', 1.06), ('S', 1.02), ('Cl', 0.99),
 ])

def covalent_radius(atm):
    """
    Return atm's covalent radius (assuming default atomtype, not its current one), always as a float.
    """
    try:
        return float( covrad_table[atm.element.symbol] ) # use radius from contributed code, if defined
    except KeyError:
        print "fyi: covalent radius not in table:",atm.element.symbol # make sure I didn't misspell any symbol names
        return float( atm.element.atomtypes[0].rcovalent ) # otherwise use nE-1 radius
    pass

def atm_distance_cost(atm1, atm2, ratio):
    """
    Return cost (due to length alone) of a hypothetical bond between two atoms; None means infinite
    """
    if not (ratio < max_dist_ratio(atm1, atm2)):
        return None
    if ratio < 1.0:
        # short bond
        return ratio * 0.01 # weak preference for smallest of small distances
    else:
        # long bond -- note, long and short bond cost is the same, where they join at ratio == 1.0
        return 0.01 + DIST_COST_FACTOR * (ratio - 1.0) ** 2 # quadratic penalty for long bonds
    pass

_enegs = ['F', 'Cl', 'O', 'S', 'N', 'P']

def bond_element_cost(atm1, atm2, _enegs=_enegs):
    """
    Avoid bonding a pair of electronegative atoms
    """
    if atm1.element.symbol in _enegs and atm2.element.symbol in _enegs:
        return 1.0
    else:
        return 0.0

def bond_cost(atm1, atm2):
    """
    Return total cost of hypothetical new bond between two atoms, or None if bond is not permitted or already there
    """
    if not (bondable_atm(atm1) and bondable_atm(atm2)): # check valence of existing bonds
        return None
    if atoms_are_bonded(atm1, atm2): # already bonded? (redundant after list-potential-bonds) ###
        return None
    distance = atm_distance(atm1, atm2)
    # note the assumption that we are talking about SINGLE bonds, which runs throughout this code
    # some day we should consider the possibility of higher-order bonds; a stab in this direction
    # is the bondtyp argument in make_bonds(), but that's really a kludge
    best_dist = idealBondLength(atm1, atm2)
    # previously: best_dist = covalent_radius(atm1) + covalent_radius(atm2)
    if not best_dist:
        return None # avoid ZeroDivision exception from pondering a He-He bond
    ratio = distance / best_dist # best_dist is always a float, so this is never "integer division"
    dc = atm_distance_cost(atm1, atm2, ratio)
    if dc is None:
        return None
    ac = atm_angle_cost(atm1, atm2, ratio)
    if ac is None:
        return None
    ec = bond_element_cost(atm1, atm2)
    return ac + dc + ec

def list_potential_bonds(atmlist0):
    """
    Given a list of atoms, return a list of triples (cost, atm1, atm2) for all bondable pairs of atoms in the list.
    Each pair of atoms is considered separately, as if only it would be bonded, in addition to all existing bonds.
    In other words, the returned bonds can't necessarily all be made (due to atom valence), but any one alone can be made,
    in addition to whatever bonds the atoms currently have.
       Warning: the current implementation takes quadratic time in len(atmlist0). The return value will have reasonable
    size for physically realistic atmlists, but could be quadratic in size for unrealistic ones (e.g. if all atom
    positions were compressed into a small region of space).
    """
    atmlist = filter( bondable_atm, atmlist0 )
    lst = []
    maxBondLength = 2.0
    ngen = NeighborhoodGenerator(atmlist, maxBondLength)
    for atm1 in atmlist:
        key1 = atm1.key
        pos1 = atm1.posn()
        for atm2 in ngen.region(pos1):
            bondLen = vlen(pos1 - atm2.posn())
            idealBondLen = idealBondLength(atm1, atm2)
            if atm2.key < key1 and bondLen < max_dist_ratio(atm1, atm2) * idealBondLen:
                # i.e. for each pair (atm1, atm2) of bondable atoms
                cost = bond_cost(atm1, atm2)
                if cost is not None:
                    lst.append((cost, atm1, atm2))
    lst.sort() # least cost first
    return lst

def make_bonds(atmlist, bondtyp = V_SINGLE):
    """
    Make some bonds between the given atoms. At any moment make the cheapest permitted unmade bond;
    stop only when no more bonds are permitted (i.e. all potential bonds have infinite cost).
       Assume that newly made bonds can never decrease the cost of potential bonds.
    (This is needed to justify the algorithm, which moves potential bonds later in an ordered list
    when their cost has increased since last checked;
    it's true since the bond cost (as defined elsewhere in this module) is a sum of terms,
    and adding a bond can add new terms but doesn't change the value of any existing terms.)
       Return the number of bonds created.
    """
    # Implementation note: the only way I know of to do this efficiently is to use a linked list
    # (as the Lisp code did), even though this is less natural in Python.
    bondlst0 = list_potential_bonds(atmlist) # a list of triples (cost, atm1, atm2)
    bondlst = linked_list(bondlst0, list) # arg2 (list) is a function to turn the triple (cost, atm1, atm2) into a list.
        # value is a list [[cost, atm1, atm2], next]; needs to be mutable in next and cost elements
        # (Note: Lisp code used a Lisp linked list of triples, (cost atm1 atm2 . next), but all Lisp lists are mutable.)
    res = 0
    while bondlst:
        entry, bondlst = bondlst
            # original code assumed this was too early to change bondlst -- we might insert a new element right after entry;
            # but I think that's not possible, so we can move forward now [bruce 050906]
        oldcostjunk, atm1, atm2 = entry
        cost = bond_cost(atm1, atm2) # might be different than last recorded cost
            #e optim: could invalidate changed costs, avoid recomputing some of them, incrementally adjust others
        if cost is not None:
            if (bondlst is None) or bondlst[0][0] >= cost:
                # if there's no next-best bond, or its cost is no better than this one's, make this bond
                bond_atoms_faster(atm1, atm2, bondtyp) # optimized bond_atoms, and doesn't make any open bonds
                res += 1
            else:
                # cost has increased beyond next bond in list -- update entry and move it down list
                entry[0] = cost
                curr = bondlst # loop variable - next possible list element after which we might insert entry
                while 1:
                    # (at this point, we know curr is not None, and we already compared cost to curr[0][0])
                    junk, next = curr
                    if (next is None) or next[0][0] >= cost:
                        break # found insertion point: right after curr, before next (next might be None)
                    curr = next
                assert curr[1] is next #e remove when works
                # insert entry after curr, before next
                curr[1] = [entry, next]
            pass
        pass
    return res

# end of translation of contributed code

# ==

def inferBonds(mol): # [probably by Will; TODO: needs docstring]

    #bruce 071030 moved this from bonds.py to bonds_from_atoms.py

    # not sure how big a margin we should have for "coincident"
    maxBondLength = 2.0
    # first remove any coincident singlets
    singlets = filter(lambda a: a.is_singlet(), mol.atoms.values())
    removable = { }
    sngen = NeighborhoodGenerator(singlets, maxBondLength)
    for sing1 in singlets:
        key1 = sing1.key
        pos1 = sing1.posn()
        for sing2 in sngen.region(pos1):
            key2 = sing2.key
            dist = vlen(pos1 - sing2.posn())
            if key1 != key2:
                removable[key1] = sing1
                removable[key2] = sing2
    for badGuy in removable.values():
        badGuy.kill()
    from operations.bonds_from_atoms import make_bonds
    make_bonds(mol.atoms.values())
    return

# ==

from utilities.debug import register_debug_menu_command

def remake_bonds_in_selection( glpane ):
    """
    Remake all bonds between selected atoms (or between atoms in selected chunks),
    in the given Selection object (produced by e.g. selection_from_part),
    by destroying all old bonds between selected atoms and all open bonds on them,
    changing all selected atoms to their default atomtype,
    and creating new single bonds using Eric Drexler's greedy algorithm which considers
    bond lengths and angles for sp3 atoms.
       Note: bonds between selected and unselected atoms are not altered, but are noticed
    when deciding what new bonds to make.
       Note: the current algorithm might make additional stretched bonds, in cases when
    it ought to infer non-sp3 atomtypes and make fewer bonds.
    """
    #bruce 071030 fixed several bugs in this function I wrote long ago;
    # evidently it never worked -- was it finished?? Now it works, at least
    # for the trivial test case of 2 nearby C(sp3) atoms.
    atmlist = glpane.assy.getSelectedAtoms()
        # notes: this includes atoms inside selected chunks;
        # it also includes a selected jig's atoms, unlike most atom operations.
    atmdict = dict([(atm.key, atm) for atm in atmlist]) # for efficiency of membership test below
    n_bonds_destroyed = 0
    n_atomtypes_changed = 0
    n_atoms = len(atmlist)
    for atm in atmlist:
        if atm.atomtype is not atm.element.atomtypes[0]:
            n_atomtypes_changed += 1 # this assume all atoms will be changed to default atomtype, not an inferred one
            # count them all before changing them or destroying any bonds,
            # in case some atomtypes weren't initialized yet
            # (since their getattr method looks at number of bonds)
    for atm in atmlist:
        for b in atm.bonds[:]:
            atm2 = b.other(atm)
            if atm2.key in atmdict:
                ###e to also zap singlets we'd need "or atm2.element is Singlet" and to prevent b.bust from remaking them!
                # (singlets can't be selected)
                b.bust()
                n_bonds_destroyed += 1 # (count real bonds only)
        atm.set_atomtype(atm.element.atomtypes[0]) ###k this might remake singlets if it changes atomtype
        #e future optim: revise above to also destroy singlets and bonds to them
        # (btw I think make_bonds doesn't make any singlets as it runs)
    n_bonds_made = make_bonds(atmlist)
        #e it would be nice to figure out how many of these are the same as the ones we destroyed, etc
    for atm in atmlist:
        atm.remake_bondpoints()
    env.history.message(
        "on %d selected atoms, replaced %d old bond(s) with %d new (or same) bond(s); changed %d atomtype(s) to default" %
        (n_atoms, n_bonds_destroyed, n_bonds_made, n_atomtypes_changed)
     )
    #e note, present implem marks lots of atoms as changed (from destroying and remaking bonds) which did not change;
    # this only matters much for redrawing speed (of unchanged chunks) and since file is always marked as changed
    # even if nothing changed at all.
    return

register_debug_menu_command( "Remake Bonds", remake_bonds_in_selection )

#end
