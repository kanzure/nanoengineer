# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
crossovers.py -- support for DNA crossovers, modelled at various levels

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

Includes Make Crossover and Remove Crossover Pl-atom-pair context menu commands.

TODO: make it work for PAM3 as well as PAM5.
"""

###BUGS:
# - Remove Crossover needs to be offered when correct to do so, not otherwise
# - Pl position is wrong after either op, esp. Remove
# - Undo and Feature Help cmdnames are wrong (not working)

from utilities.constants import noop, average_value
from model.bond_constants import V_SINGLE
from model.bond_constants import atoms_are_bonded, find_bond
from model.bonds import bond_atoms_faster, bond_direction ##, bond_atoms
from utilities.Log import redmsg, greenmsg, quote_html ##, orangemsg
##from debug_prefs import debug_pref, Choice
import foundation.env as env

from utilities.GlobalPreferences import dna_updater_is_enabled

from model.elements import PeriodicTable
Element_Sj5 = PeriodicTable.getElement('Sj5')
Element_Ss5 = PeriodicTable.getElement('Ss5')


def crossover_menu_spec(atom, selatoms):
    """
    Make a crossover-related menu_spec list for the two atoms in the
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
        assert a1.element.symbol == 'Pl5'

    # Are these Pl atoms either:
    # - legitimate candidates for making a crossover,
    # - or already in a crossover?

    # They are candidates for making a crossover if:
    # - each one is in a double helix of pseudo-DNA (or locally appears to be) (ignoring Ss/Sj errors, though we'll fix them)
    #   - this means, you can find the 5-ring of Pl5-Ss5-Ax5-Ax5-Ss5-samePl5... probably no more requirements are strictly needed
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

    res = []

    ##e need to protect against exceptions while considering adding each item

    twoPls = map( Pl5_recognizer, atoms)
    Pl1, Pl2 = twoPls

    # Both Make and Remove Crossover need the strand directions to be well-defined,
    # so if they're not, just insert a warning and not the specific commands.
    # (This also simplifies the code for deciding whether to offer Remove Crossover.)

    if not Pl1.strand_direction_well_defined or not Pl2.strand_direction_well_defined: ###IMPLEM

        text = "(strand directions not well-defined)" #e shorten? mention which atom? do it for single selected atom? say how not?
        item = (text, noop, 'disabled')
        res.append(item)

    else:

        # maybe add a "Make Crossover" command
        if make_crossover_ok(twoPls):
            text = "Make Crossover (%s - %s)" % (Pl1.atom, Pl2.atom) #e or print the Pl5_recognizer objects in the menu text??
            cmdname = "Make Crossover" ###k for undo -- maybe it figures this out itself due to those parens?? evidently not.
            command = (lambda twoPls = twoPls: make_crossover(twoPls))
            res.append((text, command)) ###e how to include cmdname?? or kluge this by having text include a prefix-separator?

        #e maybe package up those two related functions (make_crossover and make_crossover_ok)
        # into a class for the potential command -- sort of a twoPl-recognizer, i guess

        # maybe add a "Remove Crossover" command
            # should we call this Break or Unmake or Delete? It leaves the atoms, patches things up... reverses effect of Make...
            # so Unmake seems best of those, but Remove seems better than any of them.
        if remove_crossover_ok(twoPls):
            text = "Remove Crossover (%s - %s)" % (Pl1.atom, Pl2.atom)
            cmdname = "Remove Crossover"
            command = (lambda twoPls = twoPls: remove_crossover(twoPls))
            res.append((text, command))

        # it should never happen that both are ok at once!
        if len(res) > 1:
            print "bug: both Make Crossover and %s are being offered" % text #kluge to ref text to include atom names

        pass

    return res

def make_crossover_ok(twoPls): ##### NEED TO MAKE THIS A RECOGNIZER so it can easily be told to print why it's not saying it's ok.
    """
    figure out whether to offer Make Crossover, assuming bond directions are well-defined
    """

    Pl1, Pl2 = twoPls

    ## if Pl1.in_only_one_helix and Pl2.in_only_one_helix: not enough -- need to make sure the other 4 pairings are not stacked.

    a,b = Pl1.ordered_bases
    d,c = Pl2.ordered_bases # note: we use d,c rather than c,d so that the atom arrangement is as shown in the diagram far below.

    if bases_are_stacked((a, b)) and bases_are_stacked((c, d)) \
       and not bases_are_stacked((a, d)) and not bases_are_stacked((b, c)) \
       and not bases_are_stacked((a, c)) and not bases_are_stacked((b, d)):

        involved1, involved2 = map( lambda pl: pl.involved_atoms_for_make_crossover, twoPls)
        if not sets_overlap(involved1, involved2):
            return True
    return False # from make_crossover_ok

def remove_crossover_ok(twoPls):
    """
    Figure out whether to offer Remove Crossover, assuming bond directions are
    well-defined.
    """

##    when = debug_pref("Offer Remove Crossover...",
##                      Choice(["never", "always (even when incorrect)"]),
##                      non_debug = True, prefs_key = '_debug_pref_key:Offer Unmake Crossover...' )
##    offer = ( when != 'never' )
##    if not offer:
##        return False

    Pl1, Pl2 = twoPls

    a,b = Pl1.ordered_bases
    d,c = Pl2.ordered_bases

    # WARNING: this is different than the similar-looking condition in make_crossover_ok.
    if bases_are_stacked((a, c)) and bases_are_stacked((b, d)) \
       and not bases_are_stacked((a, d)) and not bases_are_stacked((b, c)) \
       and not bases_are_stacked((a, b)) and not bases_are_stacked((d, c)):

        involved1, involved2 = map( lambda pl: pl.involved_atoms_for_remove_crossover, twoPls)
        if not sets_overlap(involved1, involved2):
            return True

    return False # from remove_crossover_ok

# ==

# set functions; sets must be dicts whose keys and values are the same
###e get some of these from the Set or set module??

def union(set1, set2):
    res = dict(set1)
    res.update(set2)
    return res

def sets_overlap(set1, set2): #e could be varargs, report whether there's any overlap (same alg)
    """
    Say whether set1 and set2 overlap. (Return a boolean.)
    """
    return len(set1) + len(set2) > len(union(set1, set2))

# ==

class RecognizerError(Exception): #k superclass?
    pass # for now

DEBUG_RecognizerError = True # for now; maybe turn off before release -- might be verbose when no errors (not sure)

class StaticRecognizer:
    """
    Superclass for pattern and local-structure recognizer classes
    which don't need to invalidate/update their computed attrs as the
    local structure changes.

    Features include:
    - Support _C_attr compute methods, but optionally catch exceptions and "tame" them as error reports,
    and in some cases (declared?) as default values (e.g. False for booleans).

    Missing features include:
    - We don't track changes in inputs, and behavior of computed attrs after such changes
    depends on history of prior attr accesses (of them or any intermediate attrs they depend on,
    including internal accesses by other compute methods) -- in practice that means it's undefined
    whether we get old or new answers then (or a mixture of the two), and *that* means our derived
    (aka computed) attrs should no longer be used after input changes.
    (This limitation is why we are called StaticRecognizer rather than Recognizer.)
    """
    _r_safe = False # subclass should redefine this if they want all their compute methods to stop propogating *all* exceptions
        # (I think that should be rare, but I don't know yet for sure. It does not affect RecognizerError.)
    def __getattr__(self, attr): # in class StaticRecognizer
        if attr.startswith('__') or attr.startswith('_C_'):
            raise AttributeError, attr # must be fast
        methodname = '_C_' + attr
        method = getattr(self, methodname) # compute method
        try:
            answer = method() # WARNING: Answer must be returned, not setattr'd by this method! Error in this is detected below.
        except RecognizerError, e:
            # An exception for use by compute methods, locally reporting errors.
            # When our own methods raise this, we [nim, but needed soon] add basic info like "self" and the attr;
            # when its gets passed on from other methods (does that ever happen?? maybe if they are not _r_safe???),
            # we might someday add some self-related info so it contains its own sort of traceback
            # of the objects and attrs involved in it.
            # FOR NOW, we just treat it as normal, and record the default value;
            # someday we'll record the exception message but for now there is no way of asking for it anyway.
            if DEBUG_RecognizerError:
                print e
            answer = None
        except: # any other exception
            ##e not sure if we should suppress, reraise now only, reraise every time;
            # maybe let this be declared per attr or per class? "safe" attrs or classes would never propogate exceptions in themselves
            # (but what about exceptions coming from other things they try to use? maybe those should be wrapped into a safe form?
            #  no, if they say "the buck stops here" that better include errors from things they use, too.)
            if self._r_safe:
                print "should record error somewhere"###
                answer = None
            else:
                print "fyi, error: reraising an exception from %s.%s" % (self.__class__.__name__, methodname)###
                raise
        # we have the answer
        answer # (make sure we actually have it)
        assert not self.__dict__.has_key(attr), \
               "Bug: %s.%s set %r itself -- should only return it" % (self.__class__.__name__, methodname, attr)
        setattr(self, attr, answer)
        return answer
    pass # end of class StaticRecognizer


def element_matcher(sym):
    def func(atom, sym = sym):
        return atom.element.symbol == sym
    return func


class Base5_recognizer(StaticRecognizer):
    """
    StaticRecognizer for a base of PAM-DNA (represented by its Ss or Sj
    atom).

    @warning: it's an error to call this on any other kind of atom, and the
    constructor raises an exception if you do.

    @note: it's *not* an error to call it on a legal kind of atom, regardless of
    that atom's surroundings. Any structural errors detected around that atom
    (or on it, e.g. its valence) should not cause exceptions from the
    constructor or from any attr accesses, but only the use of fallback values
    for computed attrs, and/or the setting of an error flag, and (in the
    future) the tracking of errors and warnings into the dynenv.
    """
    def __init__(self, atom):
        self.atom = atom
        assert atom.element.symbol in ('Ss5', 'Sj5')
            #e other possibilities for init args might be added later
            #e (we might become a polymorphic constructor).
        return
    def _C_axis_atom(self):
        """[compute method for self.axis_atom]
        Return our sole Ax5 neighbor;
        on error or if our valence is wrong, raise RecognizerError
        (which means the computed value will be None).
        """
        nn = self.atom.neighbors()
        if not len(nn) == 3:
            raise RecognizerError("%s should have exactly three neighbor atoms" % self.atom)
        axes = filter( element_matcher('Ax5'), nn)
        if not len(axes) == 1:
            raise RecognizerError("%s should have exactly one Ax5 neighbor" % self.atom)
        return axes[0]
    def _C_in_helix(self):
        """[compute method for self.in_helix]
        Are we resident in a helix? (Interpreted as: do we have an Ax atom --
        the other base on the same Ax5 (presumably on the other backbone strand)
        is not looked for and might be missing.)
        """
        return self.axis_atom is not None
    pass


def bases_are_stacked(bases):
    """
    Say whether two Base5_recognizers' bases are in helices, and stacked (one to the other).
    For now, this means they have Ax (axis) pseudoatoms which are directly bonded (but not the same atom).

    @warning: This is not a sufficient condition, since it doesn't say whether they're on the same "side" of the helix!
    Unfortunately that is not easy to tell (or even define, in the present model)
    since it does not necessarily mean the same strand (in the case of a crossover at that point).
    I [bruce 070604] think there is no local definition of this property which handles that case.
    I'm not sure whether this leads to any problems with when to offer Make or Remove Crossover --
    maybe the overall conditions end up being sufficient; this needs review.
    Also, I'm not yet sure how big a deficiency it is in our model.
    """
    try:
        len(bases)
    except:
        print "following exception concerns bases == %r" % (bases,)
    assert len(bases) == 2, "bases == %r should be a sequence of length 2" % (bases,)
    for b in bases:
        assert isinstance(b, Base5_recognizer)
    for b in bases:
        if not b.in_helix: # i.e. b.axis_atom is not None
            return False
    b1, b2 = bases
    return b1.axis_atom is not b2.axis_atom and atoms_are_bonded(b1.axis_atom, b2.axis_atom)


class Pl5_recognizer(StaticRecognizer):
    """
    StaticRecognizer for surroundings of a Pl5 atom in pseudo-DNA.
    """
    def __init__(self, atom):
        self.atom = atom
        assert atom.element.symbol == 'Pl5'
    def _C_unordered_bases(self):
        """
        [compute method for self.unordered_bases]
        Require self.atom to have exactly two neighbors, and for them to be
        Ss5 or Sj5. Then return those atoms, wrapped in Base5_recognizer objects
        (which may or may not be .in_helix).

        @note: the bases are arbitrarily ordered; see also _C_ordered_bases.

        @warning: value will be None (not a sequence) if a RecognizerError was
                  raised.
        [###REVIEW: should we pass through that exception, instead, for this
        attr? Or assign a different error value?]
        """
        nn = self.atom.neighbors()
        if not len(nn) == 2:
            raise RecognizerError("Pl5 should have exactly two neighbor atoms")
        for n1 in nn:
            if not n1.element.symbol in ('Ss5','Sj5'):
                raise RecognizerError("Pl5 neighbor %s should be Ss5 or Sj5" % n1)
        bases = map(Base5_recognizer, nn) # should always succeed
        return bases
    def _C_ordered_bases(self):
        """
        [compute method for self.ordered_bases]
        Return our two bases (as Base5_recognizer objects, which may or may not be .in_helix),
        in an order consistent with backbone bond direction,
        which we require to be locally defined in a consistent way.

        @warning: value will be None (not a sequence) if a RecognizerError was
                  raised.
        """
        if self.unordered_bases is None:
            raise RecognizerError("doesn't have two bases")
        bases = list(self.unordered_bases) # we might destructively reverse this later, before returning it
        nn = bases[0].atom, bases[1].atom
        # reverse bases if bond directions go backwards, or complain if not defined or not consistent
        # (Note: the following code is mostly generic for pairs of directional bonds,
        #  so we might package it up into a utility function someday.)

        # BTW, in the future we should improve this as follows:
        # - find directional-bond strands in both directions, including at least one bond not altered
        #   when making/unmaking a crossover, and ending on the first bond with direction defined,
        #   or when you have to end due to error (too far away to stop us) or end of strand.
        # - require that this gave you a direction and was not inconsistent.
        # - when making the crossover later, actually set all those directions you passed over
        #   (not just those of your new bonds).
        dir1 = bond_direction(nn[0], self.atom) # -1 or 0 or 1
        dir2 = bond_direction(self.atom, nn[1])
        dirprod = dir1 * dir2
        if dirprod < 0:
            # both directions are set, and they're inconsistent
            raise RecognizerError("inconsistent bond directions")
                # including self.atom in the message would be redundant -- compute method glue will annotate with self ###DOIT
        elif dirprod > 0:
            # both directions are set, consistently
            if dir1 < 0:
                bases.reverse()
        else: # dirprod == 0
            # at most one direction is set (need a warning if one is set and one not? assume not, for now)
            dir = dir1 + dir2
            if dir < 0:
                bases.reverse()
            elif dir == 0:
                # both directions are unset
                raise RecognizerError("backbone bond direction is locally undefined")
                    ###REVIEW: this should not prevent offering "Make Crossover", only doing it successfully.
        return bases
    def _C_strand_direction_well_defined(self):
        """
        [compute method for self.strand_direction_well_defined]
        ###doc
        """
        return self.ordered_bases is not None
##    def _C_in_crossover(self):
##        "Say whether we bridge bases in different double helices"
##        # hmm, that's not enough to "be in a crossover"! but it's necessary. rename? just let caller use not thing.in_only_one_helix?
##        nim
    def _C_in_only_one_helix(self):
        """
        [compute method for self.in_only_one_helix]
        Say whether we're in one helix.
        (And return that helix? No -- we don't yet have anything to represent it with.
         Maybe return the involved atoms? For that, see _C_involved_atoms_for_create_crossover.)
        """
        ###REVIEW: is it good for self.unordered_bases to be None (not a sequence) on certain kinds of error?
        # And, when that happens, is it right for this to return False (not True, not an exception)?
        return self.unordered_bases is not None and bases_are_stacked(self.unordered_bases)
    def _C_involved_atoms_for_make_crossover(self):
        """
        [compute method for self.involved_atoms_for_make_crossover]
        Compute a set of atoms directly involved in using self to make a new crossover.
        Two Pl atoms will only be allowed to be in a newly made crossover
        if (among other things) their sets of involved atoms don't overlap.

        Require that these atoms are each in one helix.
        """
        if not self.in_only_one_helix:
            raise RecognizerError("Pl5 atom must be in_only_one_helix")
        res = self._involved_atoms_for_make_or_remove_crossover
        if not len(res) == 5: # can this ever fail due to a structural error?? actually it can -- Ax atoms can be the same
            raise RecognizerError("structural error (two bases on one Pl and one Ax??)")
        return res
    def _C_involved_atoms_for_remove_crossover(self): #bruce 070604
        """
        #doc
        """
        # seems like we need to check some of what the other method checks, like len 5 -- not sure -- guess yes for now
        res = self._involved_atoms_for_make_or_remove_crossover
        if not len(res) == 5:
            raise RecognizerError("structural error (two bases on one Pl and one Ax? missing Ax?)")
        return res
    def _C__involved_atoms_for_make_or_remove_crossover(self):
        """
        [private: compute method for private attr, self._involved_atoms_for_make_or_remove_crossover]
        """
        # KLUGE: the answer happens to be the same for both ops. This might change in the future if they check more
        # of the nearby bases (not sure).
        res = {}
        def include(atom):
            res[atom] = atom
        include(self.atom)
        for b in self.unordered_bases:
            include(b.atom)
            if b.axis_atom is not None: # otherwise not self.in_only_one_helix, but for _remove_ case we don't know that
                include(b.axis_atom)
        return res
    pass # Pl5_recognizer

# ==

def remove_crossover(twoPls):
    assert len(twoPls) == 2
    for pl in twoPls:
        assert isinstance(pl, Pl5_recognizer)
    assert remove_crossover_ok(twoPls)

    make_or_remove_crossover(twoPls, make = False, cmdname = "Remove Crossover")
    return

def make_crossover(twoPls):
    assert len(twoPls) == 2
    for pl in twoPls:
        assert isinstance(pl, Pl5_recognizer)
    assert make_crossover_ok(twoPls)

    make_or_remove_crossover(twoPls, make = True, cmdname = "Make Crossover")
    return

def make_or_remove_crossover(twoPls, make = True, cmdname = None):
    """
    Make or Remove (according to make option) a crossover, given Pl5_recognizers for its two Pl atoms.
    """

    # What we are doing is recognizing one local structure and replacing it with another
    # made from the same atoms. It'd sure be easier if I could do the manipulation in an mmp file,
    # save that somewhere, and read those to generate the operation! I'd have two sets of atoms, before and after,
    # and see how bonds and atomtypes got changed.

    # In this case it's not too hard to hand-code... I guess only the Pl atoms and their bonds are affected.
    # We probably do have to look at strand directions -- hmm, probably we should require them to exist before saying it's ok!
    # Or maybe better to give history error message when the command is chosen, saying you need to set them (or repair them) first...
    # Then we have to move the new/moved Pl atoms into a good position...

    # Note: Pl.ordered_bases are ordered by bond direction, to make this easier...
    # but if we want to patch up the directions in the end, do we need to care exactly which ones were defined?
    # or only "per-Pl"? hmm... it's per-Pl for now

    assert cmdname

    for pl in twoPls:
        if pl.ordered_bases is None: # should no longer be possible -- now checked before menu commands are offered [bruce 070604]
            ###BUG: this could have various causes, not only the one reported below! Somehow we need access to the
            # message supplied to the RecognizerError, for use here.
            ###REVIEW: Does that mean it should pass through compute methods (probably in a controlled way)
            # rather than making computed values None?
            # Or, should the value not be None, but a "frozen" examinable and reraisable version of the error exception??
            msg = "%s: Error: bond direction is locally undefined or inconsistent around %s" % (cmdname, pl.atom) ###UNTESTED
            print "should no longer be possible:", msg #bruce 070604
            env.history.message( redmsg( quote_html( msg)))
            return

    Pl1, Pl2 = twoPls
    a,b = Pl1.ordered_bases
    d,c = Pl2.ordered_bases # note: we use d,c rather than c,d so that the atom arrangement is as shown in the diagram below.

    # Note: for either the Make or Remove operation, the geometric arrangement is initially:
    #
    # c <-- Pl2 <-- d
    #
    # a --> Pl1 --> b
    #
    # and it ends up being (where dots indicate arrowheads, to show bond direction):
    #
    # c        d
    #  .      /
    #   \    .
    #  Pl1  Pl2
    #   .    \
    #  /      .
    # a        b
    #
    # Note: Pl1 stays attached to a, and Pl2 to d. Which two opposite bonds to preserve like that
    # is an arbitrary choice -- as long as Make and Remove make the same choice about that,
    # they'll reverse each other's effects precisely (assuming the sugars were initially correct as Ss or Sj).

    # break the bonds we no longer want
    for obj1, obj2 in [(Pl1, b), (Pl2, c)]:
        bond = find_bond(obj1.atom, obj2.atom)
        bond.bust(make_bondpoints = False)

    # make the bonds we want and didn't already have
    for obj1, obj2 in [(Pl1, c), (Pl2, b)]:
        assert not atoms_are_bonded(obj1.atom, obj2.atom)
            ###e we should make bond_atoms do this assert itself, or maybe tolerate it (or does it already??)
        bond_atoms_faster(obj1.atom, obj2.atom, V_SINGLE)

    # set directions of all 4 bonds (even the preserved ones -- it's possible they were not set before,
    #  if some but not all bonds had directions set in the part of a strand whose directions we look at.)
    for obj1, obj2 in [(a, Pl1), (Pl1, c), (d, Pl2), (Pl2, b)]:
        bond = find_bond(obj1.atom, obj2.atom)
        bond.set_bond_direction_from(obj1.atom, 1)

    # WARNING: after that bond rearrangement, don't use our Pl5_recognizers in ways that depend on Pl bonding,
    # since it's not well defined whether they think about the old or new bonding to give their answers.
    Pl_atoms = Pl1.atom, Pl2.atom
    del Pl1, Pl2, twoPls

    # transmute base sugars to Sj or Ss as appropriate
    if dna_updater_is_enabled():
        want = Element_Ss5 #bruce 080320 bugfix
    else:
        want = make and Element_Sj5 or Element_Ss5
    for obj in (a,b,c,d):
        obj.atom.Transmute(want)
        # Note: we do this after the bond making/breaking so it doesn't add singlets which mess us up.

    # move Pl atoms into better positions
    # (someday, consider using local minimize; for now, just place them directly between their new neighbor atoms,
    #  hopefully we leave them selected so user can easily do their own local minimize.)
    for pl in Pl_atoms:
        pl.setposn( average_value( map( lambda neighbor: neighbor.posn() , pl.neighbors() )))

    env.history.message( greenmsg( cmdname + ": ") + quote_html("(%s - %s)" % tuple(Pl_atoms)))

    #e need assy.changed()? evidently not.

    return # from make_or_remove_crossover

# ==

### TODO, someday:
# - rename Recognizer? it's really more like Situational Perceiver...
#
# - btw we do want one for "any two Pl" to perceive whether to offer make or break of the crossover...
#
# -  rename RecognizerError -- but to what? it's not even an error, more like "this attr is not well defined" or so...

# WARNING: in this code, the recognizers don't notice changes in mutable input structures,
# such as transmutes or even bonding changes. But they compute derived attributes lazily
# using current (not cached on __init__) values of their input attrs.
#
# That means that the values of their derived attributes, after a mutable
# change in an input structure, depends on whether those attrs (or intermediate attrs
# used to compute them) were also computed before the input change.


# old design comments:

    # think in terms of 3 base relations: paired base, stacked base, backbone-bonded base. two directions for some, one for other.
    # so, find bases, then look at them for patterns.
    # for phosphate find two bases (ie sugars), know they're backbone-bound, see if stacked or not (in right direction?)

# end
