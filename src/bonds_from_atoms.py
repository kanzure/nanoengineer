# Portions copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
bonds_from_atoms.py -- experimental code for inferring bonds from atom positions and elements alone

$Id$

History:

- bruce 050906 translated into Python some Lisp code contributed by Dr. K. Eric Drexler.
'''

# Translation into Python of Lisp code contributed by Dr. K. Eric Drexler.
# Some comments are from contributed code, perhaps paraphrased.

#e Plans: for efficiency, we'll further translate this into Pyrex or C, and/or combine
# with atom-position hashtable rather than scanning all pairs of atoms.
# This implem is just for testing and experimentation.

# This code does not yet consider the possibility of non-sp3 atomtypes,
# and will need changes to properly handle those.
# For now it ignores existing atomtypes and creates new bonds appropriate for sp3
# perhaps plus some extra too-long bonds at the end, if permitted by valence.

from VQT import vlen, pi
from bonds import bonded, bond_atoms_faster, V_SINGLE, neighborhoodGenerator
from chem import atom_angle_radians

# constants; angles are in radians

degrees = pi / 180

TET_ANGLE = 109.4 * degrees   #e this will probably need to be generalized for non-sp3 atoms
MIN_BOND_ANGLE = 40 * degrees # accepts moderately distorted three-membered rings
ANGLE_ACCEPT_DIST = 0.9       # ignore angle cutoff below this distance (in Angstroms)
MIN_DIST_RATIO = 0.8          # prohibit bonds too much shorter than their proper length
MAX_DIST_RATIO = 1.2          # prohibit bonds too much longer than their proper length
DIST_COST_FACTOR = 5.0        # multiplier on square of distance-ratio beyond optimal

# (utilities used by contributed code, defined differently for nE-1)

def atm_distance(atom1, atom2):
    return vlen(atom1.posn() - atom2.posn())

atm_angle = atom_angle_radians # args are three atoms

# utility for creating mutable linked lists in Python
def linked_list( lis1, func = None ):
    """Given a list of 0 or more elements (e.g. [a,b,c,d]),
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

def max_atom_bonds(atom): # coded differently for nE-1
    """Return max number of bonds permitted on this atom, based only on its element
    (for any atomtype, ignoring current atomtype of atom). (Returns 0 for noble gases.)
    """
    return atom.element.atomtypes[0].numbonds

def bondable_atm(atom): # coded differently for nE-1 due to open bonds
    """Could this atom accept any more bonds
    (assuming it could have any of its atomtypes,
     and ignoring positions and elements of atoms it's already bonded to,
     and ignoring open bonds,
     and treating all existing bonds as single bonds)?
    """
    #e len(atom.bonds) would be faster but would not ignore open bonds;
    # entire alg could be recoded to avoid ever letting open bonds exist,
    # and then this could be speeded up.
    #return len(atom.realNeighbors()) < max_atom_bonds(atom)

    # We aren't handling higher-order atomtypes well enough to rule out
    # bonds in this way. So always say yes, for now.  -wware 060613
    return True

def bond_angle_cost(angle, accept):
    """Return the cost of the given angle, or None if that cost is infinite.
    Note that the return value can be 0.0, so callers should only
    test it for "is None", not for its boolean value.
       If accept is true, don't use the minimum-angle cutoff (i.e. no angle
    is too small to be accepted).
    """
    if not (accept or MIN_BOND_ANGLE < angle):
        return None
    diff = angle - TET_ANGLE # for heuristic cost, treat all angles as ideally tetrahedral
    square = diff * diff
    if 0.0 < diff:
        # wide angle
        return square
    else:
        # tight angle -- larger quadratic penalty
        return 2.0 * square

def atm_angle_cost(atm1, atm2):
    """Return total cost of all bond-angles which include the atm1-atm2 bond
    (where one bond angle is said to include the two bonds whose angle it describes);
    None means infinite cost.
    """
    accept = atm_distance(atm1, atm2) < ANGLE_ACCEPT_DIST
    sum = 0.0
    for atm in atm1.realNeighbors():
        cost = bond_angle_cost( atm_angle(atm, atm1, atm2), accept)
        if cost is None: # cost can be 0.0, so don't use a boolean test here [bruce 050906]
            return None
        sum += cost
    for atm in atm2.realNeighbors():
        cost = bond_angle_cost( atm_angle(atm, atm2, atm1), accept) # note different order of atm2, atm1
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
    "Return atm's covalent radius (assuming default atomtype, not its current one), always as a float."
    try:
        return float( covrad_table[atm.element.symbol] ) # use radius from contributed code, if defined
    except KeyError:
        print "fyi: covalent radius not in table:",atm.element.symbol # make sure I didn't misspell any symbol names
        return float( atm.element.atomtypes[0].rcovalent ) # otherwise use nE-1 radius
    pass

def atm_distance_cost(atm1, atm2):
    "Return cost (due to length alone) of a hypothetical bond between two atoms; None means infinite"
    distance = atm_distance(atm1, atm2)
    best_dist = covalent_radius(atm1) + covalent_radius(atm2)
    if not best_dist:
        return None # avoid ZeroDivision exception from pondering a He-He bond
    ratio = distance / best_dist # best_dist is always a float, so this is never "integer division"
    if not (ratio < MAX_DIST_RATIO):
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
    "Avoid bonding a pair of electronegative atoms"
    if atm1.element.symbol in _enegs and atm2.element.symbol in _enegs:
        return 1.0
    else:
        return 0.0

def bond_cost(atm1, atm2):
    "Return total cost of hypothetical new bond between two atoms, or None if bond is not permitted or already there"
    if not (bondable_atm(atm1) and bondable_atm(atm2)): # check valence of existing bonds
        return None
    if bonded(atm1, atm2): # already bonded? (redundant after list-potential-bonds) ###
        return None
    dc = atm_distance_cost(atm1, atm2)
    if dc is None:
        return None
    ac = atm_angle_cost(atm1, atm2)
    if ac is None:
        return None
    ec = bond_element_cost(atm1, atm2)
    return ac + dc + ec

def list_potential_bonds(atmlist0):
    """Given a list of atoms, return a list of triples (cost, atm1, atm2) for all bondable pairs of atoms in the list.
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
    neighborhood = neighborhoodGenerator(atmlist, maxBondLength)
    for atm1 in atmlist:
        key1 = atm1.key
        pos1 = atm1.posn()
        radius1 = atm1.atomtype.rcovalent
        for atm2 in neighborhood(pos1):
            bondLen = vlen(pos1 - atm2.posn())
            idealBondLen = radius1 + atm2.atomtype.rcovalent
            if atm2.key < key1 and MIN_DIST_RATIO * idealBondLen < bondLen < MAX_DIST_RATIO * idealBondLen:
                # i.e. for each pair (atm1, atm2) of bondable atoms
                cost = bond_cost(atm1, atm2)
                if cost is not None:
                    lst.append((cost, atm1, atm2))
    lst.sort() # least cost first
    return lst

def make_bonds(atmlist):
    """Make some bonds between the given atoms. At any moment make the cheapest permitted unmade bond;
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
                bond_atoms_faster(atm1, atm2, V_SINGLE) # optimized bond_atoms, and doesn't make any open bonds
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

# I'm not sure what Bruce intended here, this looks like the closest existing thing.  -Will 060613
#import env
#from env import register_command ###IMPLEM and maybe move
import debug
from debug import register_debug_menu_command

def remake_bonds_in_selection( selection ):
    """Remake all bonds between selected atoms (or between atoms in selected chunks),
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
    atmlist = selection.atomslist()
    n_bonds_destroyed = 0
    n_atomtypes_changed = 0
    n_atoms = len(atmlist)
    for atm in atmlist:
        if atm.atomtype is not atm.elements.atomtypes[0]:
            n_atomtypes_changed += 1 # this assume all atoms will be changed to default atomtype, not an inferred one
            # count them all before changing them or destroying any bonds,
            # in case some atomtypes weren't initialized yet
            # (since their getattr method looks at number of bonds)
    for atm in atmlist:
        for b in atm.bonds[:]:
            atm2 = b.other(atm)
            if selection.contains_atom(atm2): ### implem contains_atom
                ###e to also zap singlets we'd need "or atm2.element is Singlet" and to prevent b.bust from remaking them!
                # (singlets can't be selected)
                b.bust()
                n_bonds_destroyed += 1 # (count real bonds only)
        atm.set_atomtype(atm.elements.atomtypes[0]) ###k this might remake singlets if it changes atomtype
        #e future optim: revise above to also destroy singlets and bonds to them
        # (btw I think make_bonds doesn't make any singlets as it runs)
    n_bonds_made = make_bonds(atmlist)
        #e it would be nice to figure out how many of these are the same as the ones we destroyed, etc
    for atm in atmlist:
        atm.remake_singlets()
    env.history.message(
        "on %d selected atoms, replaced %d old bond(s) with %d new (or same) bond(s); changed %d atomtype(s) to default" %
        (n_atoms, n_bonds_destroyed, n_bonds_made, n_atomtypes_changed)
     )
    #e note, present implem marks lots of atoms as changed (from destroying and remaking bonds) which did not change;
    # this only matters much for redrawing speed (of unchanged chunks) and since file is always marked as changed
    # even if nothing changed at all.
    return

#register_command( "Remake bonds", remake_bonds_in_selection ) ###IMPLEM, and have it add in the initial history message
register_debug_menu_command( "Remake bonds", remake_bonds_in_selection ) ###IMPLEM, and have it add in the initial history message

#end
