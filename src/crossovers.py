# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
crossovers.py -- support for DNA crossovers, modelled at various levels

$Id$
"""
__author__ = "bruce"

from constants import noop

def crossover_menu_spec(atom, selatoms):
    """Make a crossover-related menu_spec list for the two atoms in the
    selatoms dict (atom.key -> atom), both Pl, for use in atom's context menu
    (which must be one of the atoms in selatoms). If no menu commands are needed,
    return [] (a valid empty menu_spec) or None.
       Should be reasonably fast, but needn't be super-fast -- called once
    whenever we construct a context menu for exactly two selected Pl atoms.
    """
    assert len(selatoms) == 2
    atoms = selatoms.values()
    assert atom in atoms
    for a1 in atoms:
        assert a1.element.symbol == 'Pl'

    # Are these Pl atoms either:
    # - legitimate candidates for making a crossover,
    # - or already in a crossover?
    
    # They are candidates for making a crossover if:
    # - each one is in a double helix of pseudo-DNA (or locally appears to be) (ignoring Ss/Sj errors, though we'll fix them)
    #   - this means, you can find the 5-ring of Pl-Ss-Ax-Ax-Ss-samePl... probably no more requirements are strictly needed
    # - the sets of involved atoms for each one don't overlap
    # - we *could* also require they're not nearby in the same helix, but we won't bother
    # - we *could* require geometric constraints, but we probably don't want to (and surely won't bother for now).
    # We'll create an object to figure this out, and we may keep it around to do the crossover-making if that's desired.

    # They're already in a crossover if:
    # - each one bridges two double helices of pseudo-DNA (or locally appears to);
    # - they bridge the same double helices, in neighboring locations.

    # Ideally we'd use a general framework for pattern recognizer objects to look for and remember these patterns,
    # where the patterns would include the basic structure of pseudo-dna bases and helices.
    # For now, we'll probably be simpler here to get started, but then we'll get generalized
    # when the pseudo-dna spelling checker is added, and/or take advantage of the persistent recognizers
    # which that will make use of (rather than creating new recognizer objects for each cmenu request, like we'll do now).
    
##    res = [("crossover stub", noop, 'disabled'),
##            ("crossover stub 2", noop,)
##           ] ###STUB for testing
##    return res

    res = []

    ###e need to protect against exceptions while considering adding each item
    
    twoPls = map( Pl_recognizer, atoms)
    
    # maybe add a Create Crossover command
    if create_crossover_ok(twoPls):
        Pl1, Pl2 = twoPls
        text = "Create crossover from %s and %s" % (Pl1.atom, Pl2.atom) #e or pass the Pl_recognizer objects??
        cmdname = "Create crossover" ###k # for undo
        command = (lambda twoPls = twoPls: create_crossover(twoPls))
        res.append((text, command)) ###e how to include cmdname?? or kluge this by having text include a prefix-separator?
    
    ##e also maybe add a command to break an existing crossover -- break_crossover, break_crossover_ok
    #e maybe package those two related functions up into a class for the potential command -- sort of a twoPl-recognizer, i guess
    
    return res

def create_crossover_ok(twoPls):
    Pl1, Pl2 = twoPls
    if Pl1.in_only_one_helix and Pl2.in_only_one_helix:
        involved1, involved2 = map( involved_atoms_for_create_crossover, twoPls)
        if not sets_overlap(involved1, involved2):
            return True
    return False

# ==

# set functions; sets must be dicts whose keys and values are the same

def union(set1, set2): ###e get this from Set or set module??
    res = dict(set1)
    res.update(set2)
    return res

def sets_overlap(set1, set2): #e could be varargs, report whether there's any overlap (same alg)
    "Say whether set1 and set2 overlap. (Return a boolean.)"
    return len(set1) + len(set2) > len(union(set1, set2))

# ==

class Recognizer:
    """Superclass for pattern and local-environment recognizer classes.
    Features include:
    - Support _C_attr compute methods, but catch exceptions and "tame" them as error reports,
    and in some cases (declared?) as default values (e.g. False for booleans).
    """
    pass


def element_matcher(sym):
    def func(atom, sym = sym):
        return atom.element.symbol == sym
    return func


class Base_recognizer(Recognizer):
    """Recognizer for a base of pseudo-DNA (represented by its Ss or Sj atom).
    """
    def __init__(self, atom):
        self.atom = atom
        assert atom.element.symbol in ('Ss','Sj')
            #e other possibilities for init args might be added later (we might become a polymorphic constructor)
        self.check()
    def check(self):
        "make sure self counts as a legitimate base"
            #e if not, does constructor fail, or construct an obj that knows it's wrong?
            # (Maybe require __init__ flag to do the latter?)
        self.axis_atom
        pass
    def _C_axis_atom(self):
        nn = self.atom.neighbors()
        assert len(nn) == 2, "%s should have exactly three neighbor atoms" % self.atom
        axes = filter( element_matcher('Ax'), nn)
        assert len(axes) == 1, "%s should have exactly one Ax neighbor" % self.atom
        return axes[0]
    pass


def bases_are_stacked(bases):
    """Say whether two base objects are stacked (one to the other).
    For now, this means they have Ax (axis) pseudoatoms which are directly bonded.
    Exceptions are possible if the bases are not fully legitimate themselves.
    """
    assert len(bases) == 2
    for b in bases:
        assert isinstance(b, Base_recognizer)
    b1, b2 = bases
    return bonded_atoms(b1.axis_atom, b2.axis_atom)#k bonded_atoms


class Pl_recognizer(Recognizer):
    """Recognizer for surroundings of a Pl atom in pseudo-DNA.
    """
    def __init__(self, atom):
        self.atom = atom
        assert atom.element.symbol == 'Pl'
    def _C_base1(self):
        return self.bases[0]
    def _C_base2(self):
        return self.bases[1]
    def _C_bases(self):
        """Require self.atom to have exactly two neighbors, and for them to be Ss or Sj.
        Then return those atoms, recognized as representing bases.
        If backbone bond directions are defined and consistent, order the bases in the same direction.
        """
        nn = self.atom.neighbors()
        assert len(nn) == 2, "Pl should have exactly two neighbor atoms"
        for n1 in nn:
            assert n1.element.symbol in ('Ss','Sj'), "Pl neighbor %s should be Ss or Sj" % n1
        # reverse nn if bond directions go backwards
        # the following code is generic for pairs of directional bonds, so we might package it up into a utility function
        dir1 = bond_direction(nn[0], self.atom) # -1 or 0 or 1
        dir2 = bond_direction(self.atom, nn[1]) ###IMPLEM bond_direction function
        dirprod = dir1 * dir2
        if dirprod < 0:
            # both directions are set, and they're inconsistent
            assert "inconsistent bond directions at %s" % self.atom
        elif dirprod > 0:
            # both are set, consistently
            if dir1 < 0:
                nn.reverse()
        else:
            # at most one is set (need a warning if one is set and one not? or, if neither is set?)
            dir = dir1 + dir2
            if dir < 0:
                nn.reverse()
            # else if dir == 0, directions are unset -- worry about this later -- or maybe have error message right here?? ####REVIEW
            ###e but maybe store the facts here to save time later? or return them, ie compute bases and direction at same time?
        bases = map(Base_recognizer, nn) # this might fail, if they don't both look like valid bases (given their surroundings)
        return bases
    def _C_in_crossover(self):
        "Say whether we bridge bases in different double helices"
        nim
    def _C_in_only_one_helix(self):
        """Say whether we're in one helix.
        (And return it? No -- we don't yet have anything to represent it with.
         Maybe return the involved atoms? For that, see _C_involved_atoms_for_create_crossover.)
        """
        return bases_are_stacked(self.bases)
    def _C_involved_atoms_for_create_crossover(self):
        """Compute a set of atoms directly involved in using self to create a crossover.
        Two Pl atoms will only be allowed to create one if their sets of involved atoms
        don't overlap.
        """
        assert self.in_only_one_helix
        res = {}
        def include(atom):
            res[atom] = atom
        include(self.atom)
        for b in self.bases:
            include(b.atom)
            include(b.axis_atom)
        assert len(res) == 5
        return res
    pass # Pl_recognizer

def create_crossover(twoPls):
    assert len(twoPls) == 2
    for pl in twoPls:
        assert isinstance(pl, Pl_recognizer)
    assert create_crossover_ok(twoPls)

    # now do it!
    print "should create crossover from", twoPls

    # What we are doing is recognizing one local structure and replacing it with another
    # made from the same atoms. It'd sure be easier if I could do the manipulation in an mmp file,
    # save that somewhere, and read those to generate the operation! I'd have two sets of atoms, before and after,
    # and see how bonds and atomtypes got changed.

    # In this case it's not too hard to hand-code... I guess only the Pl atoms and their bonds are affected.
    # We probably do have to look at strand directions -- hmm, probably we should require them to exist before saying it's ok!
    # Or maybe better to give history error message when the command is chosen, saying you need to set them (or repair them) first...
    # Then we have to move the new/moved Pl atoms into a good position...

    # Note: Pl.bases are sorted by bond direction, to make this easier...
    # but if we want to patch up the directions in the end, do we need to care exactly which ones were defined?
    # or only "per Pl"? hmm... ###e

    Pl1, Pl2 = twoPls
    a,b = Pl1.bases
    d,c = Pl2.bases
    for pl in twoPls:
        for bond in pl.bonds[:]:
            bond.bust()
    # make a-Pl1-c bonds -- using Pl1 or Pl2 here is an arbitrary choice
    for obj1, obj2 in [(a, Pl1), (Pl1, c), (d, Pl2), (Pl2, b)]:
        bond_atoms(obj1.atom, obj2.atom)
            # and set direction = 1 if enough older directions were defined;
            #e maybe stop earlier and complain if they were not?
    for pl in twoPls:
        print "should move pl.atom into the right position"
            # how? local minimize? is it fast enough? or just guess a pos, leave them selected, let user do local min?
    
    return

    
### BUGS:
# - recognizer compute methods should probably have their own error exception class rather than using assert


# obs cmt?:

##    base1
##    base2
##    axis1
##    axis2
##    bridging = axis1 and axis2 and (axis1 != axis2) #### reexpress as legitimate formula ### WRONG, axis is not an object
        # and even if it was, it's bridging if it connects two diff places on one axis!
    # think in terms of 3 base relations: paired base, stacked base, backbone-bonded base. two directions for some, one for other.
    # so, find bases, then look at them for patterns.
    # for phosphate find two bases (ie sugars), know they're backbone-bound, see if stacked or not (in right direction?)
    
# end
