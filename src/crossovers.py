# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
crossovers.py -- support for DNA crossovers, modelled at various levels

$Id$
"""
__author__ = "bruce"

### TODO:
##    change cmd name to interior caps
##    it's really more like Situational Perceiver...
##     say so in cmt...
##    btw we do want one for "any two Pl" to perceive whether to offer make or break of the crossover...
##
##    rename RecognizerError -- but to what? it's not even an error, more like "this attr is not well defined" or so...
##
##    define some nim functions like bonded_atoms line 233 or whatever
##     (or find correct func -- i bet it is just the wrong name)


from constants import noop, average_value
from bonds import atoms_are_bonded, find_bond, bond_atoms, V_SINGLE, bond_atoms_faster, bond_direction
from HistoryWidget import redmsg, greenmsg, orangemsg, quote_html
from debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True, Choice
import env

from elements import PeriodicTable
Element_Sj = PeriodicTable.getElement('Sj')
Element_Ss = PeriodicTable.getElement('Ss')


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
    
    # maybe add a "Make Crossover" command
    if make_crossover_ok(twoPls):
        Pl1, Pl2 = twoPls
        text = "Make Crossover (%s - %s)" % (Pl1.atom, Pl2.atom) #e or print the Pl_recognizer objects in the menu text??
        cmdname = "Make Crossover" ###k for undo -- maybe it figures this out itself due to those parens?? evidently not.
        command = (lambda twoPls = twoPls: make_crossover(twoPls))
        res.append((text, command)) ###e how to include cmdname?? or kluge this by having text include a prefix-separator?

    #e maybe package up those two related functions (make_crossover and make_crossover_ok)
    # into a class for the potential command -- sort of a twoPl-recognizer, i guess
    
    # maybe add an "Unmake Crossover" command
        # should we call this Break or Unmake or Delete? It leaves the atoms, patches things up... reverses effect of Make...
        # so Unmake seems best... not sure.
    if unmake_crossover_ok(twoPls):
        Pl1, Pl2 = twoPls
        text = "Unmake Crossover (%s - %s)" % (Pl1.atom, Pl2.atom)
        cmdname = "Unmake Crossover"
        command = (lambda twoPls = twoPls: unmake_crossover(twoPls))
        res.append((text, command))
    
    return res

def make_crossover_ok(twoPls): ##### NEED TO MAKE THIS A RECOGNIZER so it can easily be told to print why it's not saying it's ok.
    Pl1, Pl2 = twoPls
    if Pl1.in_only_one_helix and Pl2.in_only_one_helix:
        involved1, involved2 = map( lambda pl: pl.involved_atoms_for_make_crossover, twoPls)
        if not sets_overlap(involved1, involved2):
            return True
    return False

def unmake_crossover_ok(twoPls): ###STUB
    when = debug_pref("Offer Unmake Crossover...",
                      Choice(["never", "always (even when incorrect)"]),
                      non_debug = True, prefs_key = True )
    return when != 'never'

# ==

# set functions; sets must be dicts whose keys and values are the same
###e get some of these from the Set or set module??

def union(set1, set2): 
    res = dict(set1)
    res.update(set2)
    return res

def sets_overlap(set1, set2): #e could be varargs, report whether there's any overlap (same alg)
    "Say whether set1 and set2 overlap. (Return a boolean.)"
    return len(set1) + len(set2) > len(union(set1, set2))

# ==

class RecognizerError(Exception): #k superclass?
    pass # for now

DEBUG_RecognizerError = True # for now; turn off before real use, will be verbose when no errors ####

class StaticRecognizer:
    """Superclass for pattern and local-structure recognizer classes
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
    def __getattr__(self, attr):
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


class Base_recognizer(StaticRecognizer):
    """StaticRecognizer for a base of pseudo-DNA (represented by its Ss or Sj atom).
       WARNING: it's an error to call this on any other kind of atom, and the constructor raises an exception if you do.
       Note: it's *not* an error to call it on a legal kind of atom, regardless of that atom's surroundings.
    Any structural errors detected around that atom (or on it, e.g. its valence)
    should not cause exceptions from the constructor or from any attr accesses,
    but only the use of fallback values for computed attrs, and/or the setting of an error flag,
    and (in the future) the tracking of errors and warnings into the dynenv.
    """
    def __init__(self, atom):
        self.atom = atom
        assert atom.element.symbol in ('Ss','Sj')
            #e other possibilities for init args might be added later (we might become a polymorphic constructor).
##        self.check()
##    def check(self):
##        "make sure self counts as a legitimate base"
##            #e if not, does constructor fail, or construct an obj that knows it's wrong?
##            # (Maybe require __init__ flag to do the latter?)
##        self.axis_atom
##        pass
    def _C_axis_atom(self):
        """[compute method for self.axis_atom]
        Return our sole Ax neighbor;
        on error or if our valence is wrong, raise RecognizerError
        (which means the computed value will be None).
        """
        nn = self.atom.neighbors()
        if not len(nn) == 3:
            raise RecognizerError("%s should have exactly three neighbor atoms" % self.atom)
        axes = filter( element_matcher('Ax'), nn)
        if not len(axes) == 1:
            raise RecognizerError("%s should have exactly one Ax neighbor" % self.atom)
        return axes[0]
    def _C_in_helix(self):
        """[compute method for self.in_helix]
        Are we resident in a helix? (Interpreted as: do we have an Ax atom --
        the other base on the same Ax (presumably on the other backbone strand)
        is not looked for and might be missing.)
        """
        return self.axis_atom is not None
    pass


def bases_are_stacked(bases):
    """Say whether two Base_recognizers' bases are in helices, and stacked (one to the other).
    For now, this means they have Ax (axis) pseudoatoms which are directly bonded.
    """
    try:
        len(bases)
    except:
        print "following exception concerns bases == %r" % (bases,)
    assert len(bases) == 2, "bases == %r should be a sequence of length 2" % (bases,)
    for b in bases:
        assert isinstance(b, Base_recognizer)
    for b in bases:
        if not b.in_helix:
            return False
    b1, b2 = bases
    return atoms_are_bonded(b1.axis_atom, b2.axis_atom)


class Pl_recognizer(StaticRecognizer):
    """StaticRecognizer for surroundings of a Pl atom in pseudo-DNA.
    """
    def __init__(self, atom):
        self.atom = atom
        assert atom.element.symbol == 'Pl'
    def _C_unordered_bases(self):
        """[compute method for self.unordered_bases]
        Require self.atom to have exactly two neighbors, and for them to be Ss or Sj.
        Then return those atoms, wrapped in Base_recognizer objects (which may or may not be .in_helix).
           Note that the bases are arbitrarily ordered; see also _C_ordered_bases.
           WARNING: value will be None (not a sequence) if a RecognizerError was raised.
        [###REVIEW: should we pass through that exception, instead, for this attr? Or assign a different error value?]
        """
        nn = self.atom.neighbors()
        if not len(nn) == 2:
            raise RecognizerError("Pl should have exactly two neighbor atoms")
        for n1 in nn:
            if not n1.element.symbol in ('Ss','Sj'):
                raise RecognizerError("Pl neighbor %s should be Ss or Sj" % n1)
        bases = map(Base_recognizer, nn) # should always succeed
        return bases
    def _C_ordered_bases(self):
        """[compute method for self.ordered_bases]
        Return our two bases (as Base_recognizer objects, which may or may not be .in_helix),
        in an order consistent with backbone bond direction,
        which we require to be locally defined in a consistent way.
           WARNING: value will be None (not a sequence) if a RecognizerError was raised.
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
    def _C_in_crossover(self):
        "Say whether we bridge bases in different double helices"
        # hmm, that's not enough to "be in a crossover"! but it's necessary. rename? just let caller use not thing.in_only_one_helix?
        nim
    def _C_in_only_one_helix(self):
        """[compute method for self.in_only_one_helix]
        Say whether we're in one helix.
        (And return that helix? No -- we don't yet have anything to represent it with.
         Maybe return the involved atoms? For that, see _C_involved_atoms_for_create_crossover.)
        """
        ###REVIEW: is it good for self.unordered_bases to be None (not a sequence) on certain kinds of error?
        # And, when that happens, is it right for this to return False (not True, not an exception)?
        return self.unordered_bases is not None and bases_are_stacked(self.unordered_bases)
    def _C_involved_atoms_for_make_crossover(self):
        """[compute method for self.involved_atoms_for_make_crossover]
        Compute a set of atoms directly involved in using self to make a new crossover.
        Two Pl atoms will only be allowed to be in a newly made crossover
        if (among other things) their sets of involved atoms don't overlap.
           Require that these atoms are each in one helix.
        """
        if not self.in_only_one_helix:
            raise RecognizerError("Pl atom must be in_only_one_helix")
        res = {}
        def include(atom):
            res[atom] = atom
        include(self.atom)
        for b in self.unordered_bases:
            include(b.atom)
            assert b.axis_atom is not None # otherwise not self.in_only_one_helix
            include(b.axis_atom)
        if not len(res) == 5: # can this ever fail do to a structural error?? actually it can -- Ax atoms can be the same
            raise RecognizerError("structural error (two bases on one Pl and one Ax??)")
        return res
    pass # Pl_recognizer

def unmake_crossover(twoPls):### NOT YET CALLED
    assert len(twoPls) == 2
    for pl in twoPls:
        assert isinstance(pl, Pl_recognizer)
    assert unmake_crossover_ok(twoPls) ###IMPLEM
    
    make_or_unmake_crossover(twoPls, make = False, cmdname = "Unmake Crossover")
    return

def make_crossover(twoPls):
    assert len(twoPls) == 2
    for pl in twoPls:
        assert isinstance(pl, Pl_recognizer)
    assert make_crossover_ok(twoPls)
    
    make_or_unmake_crossover(twoPls, make = True, cmdname = "Make Crossover")
    return

def make_or_unmake_crossover(twoPls, make = True, cmdname = None):
    "Make or Unmake (according to make option) a crossover, given Pl_recognizers for its two Pl atoms."

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
    # or only "per Pl"? hmm... ###e

    assert cmdname
    
    for pl in twoPls:
        if pl.ordered_bases is None:
            ###BUG: this could have various causes, not only the one reported below! Somehow we need access to the
            # message supplied to the RecognizerError, for use here.
            ###REVIEW: Does that mean it should pass through compute methods (probably in a controlled way)
            # rather than making computed values None?
            # Or, should the value not be None, but a "frozen" examinable and reraisable version of the error exception??
            msg = "%s: Error: bond direction is locally undefined or inconsistent around %s" % (cmdname, pl.atom) ###UNTESTED
            env.history.message( redmsg( quote_html( msg)))
            return
    
    Pl1, Pl2 = twoPls
    a,b = Pl1.ordered_bases
    d,c = Pl2.ordered_bases # note: we use d,c rather than c,d so that the atom arrangement is as shown in the diagram below.
    #
    # Note: the geometric arrangement is initially:
    #
    # c <-- Pl2 <-- d
    #
    # a --> Pl1 --> b
    #
    # and it ends up being (where dot means arrowhead, to show bond direction):
    #
    # c        d
    #  .      /
    #   \    .
    #  Pl1  Pl2
    #   .    \
    #  /      .
    # a        b
    #
    Pl_atoms = Pl1.atom, Pl2.atom

    if 1 or debug_pref("Make Crossover: trigger Undo bug", Choice_boolean_False, prefs_key = True):
        ## print "Use the original code to break and remake all 4 bonds"
        #
        # Use the original code to break and remake all 4 bonds -- this encounters a bug in Undo
        # if you try to Undo or Redo the result. Guess: Undo gets confused if you break one bond
        # and then make a new bond between the same two atoms, in the same undoable operation.

        # update 070602 8:30pm PT: the bug is fixed now, in chem.py (see comments there marked 070602),
        # for both the latest code below and this original code (but still using an extra transmute kluge below).
        # After I commit the fix plus all this debug code, I'll clean it up and recommit the cleanest/safest version only.
        for pl in Pl_atoms:
            for bond in pl.bonds[:]:
                bond.bust(make_bondpoints = False)

        # make a-Pl1-c bonds, etc -- using Pl1 or Pl2 first is an arbitrary choice (either way, Make then Unmake is a noop ###k)
        for obj1, obj2 in [(a, Pl1), (Pl1, c), (d, Pl2), (Pl2, b)]:
            assert not atoms_are_bonded(obj1.atom, obj2.atom) ###e we should make bond_atoms do this itself, or maybe tolerate it (or does it?)
            bond = bond_atoms_faster(obj1.atom, obj2.atom, V_SINGLE)
                # WARNING: bond_atoms without the 3rd arg doesn't remove the extra singlets from the broken bonds above.
                # Even with it, it doesn't seem to remove enough of them... so I'm using make_bondpoints = False in bust, above.
                # But even that fails, so I'm reverting here to bond_atoms_faster. But even that fails -- maybe Transmute is adding them?
                # Just do it after this instead of before... that worked. Note that the extras were on Pl and/or Sj in different cases
                # I tried.
            bond.set_bond_direction_from(obj1.atom, 1)
    elif 0:
        # Use different code to try to work around the (putative) Undo bug mentioned above --
        # reuse the same bonds between a --> Pl1 and Pl2 <-- d rather than breaking them and making equivalent ones.
        # (But do still set their direction, in case it was not set before -- possible, if some but not all directions
        #  were set in the part of a strand whose directions we look at.)
        # BUT IT DOESN'T WORK!
        # [bruce 070602]

        # break the bonds we no longer want
        for obj1, obj2 in [(Pl1, b), (Pl2, c)]:
            bond = find_bond(obj1.atom, obj2.atom)
            bond.bust(make_bondpoints = False)
        # make the bonds we want and didn't already have 
        for obj1, obj2 in [(Pl1, c), (Pl2, b)]:
            bond_atoms_faster(obj1.atom, obj2.atom, V_SINGLE)
        # set directions of all 4 bonds
        for obj1, obj2 in [(a, Pl1), (Pl1, c), (d, Pl2), (Pl2, b)]:
            bond = find_bond(obj1.atom, obj2.atom)
            bond.set_bond_direction_from(obj1.atom, 1)
    else:
        # try something else... this time make and kill singlets... still doesn't work.
        # then try bond_atoms with V_SINGLE - still no.
        # then try bond_atoms_oldversion (ie leave out vnew) since it has more invals - still no.
        # then try not doing transmute or set_dir in case it's involved --- this exposes a bug - x2 not killed,
        #   transmute did it i guess -- but undo works this time!
        # try explicit x2.kill, still no transmute or set_dir -- but now the undo bug is back!!!
        # So the bug has something to do with the lack of intermediate singlets?? if they're killed later we're ok!
        # WHER I AM:
        # - try killing x1, x2 down below, before transmute
        # - try leaving them for transmute to kill -- DOING THIS NOW #####
        #       (before transmute back on, 4 extra x, undo works) (with transmute on, -- only kills 2 x's, undo still works)...###
        # - print the internal undo diffs??
        # - full invals on all atoms and bonds involved??
        # - is the bug in the mashng og diff r state back into the model? evidence:
        #   - missing valence error indicators #####
        #   - previously seen bond drawing bugs
        #   - undo does set assy modified back to no
        #   ddebug this by watching it to that mashingfor these bnds
        
        
        
        # break the bonds we no longer want; kluge: save singlets to kill later, after making other bonds
        kill_later = []
        for obj1, obj2 in [(Pl1, b), (Pl2, c)]:
            bond = find_bond(obj1.atom, obj2.atom)
            ## obj1._crossovers__singlet_KLUGE__ =
            x1, x2 = bond.bust()
            assert x1.is_singlet()
##            x1.kill() # on a Pl - try this now 325p -- can't do it, triggers undo bug -- is it the one left over? yes... zap it later
            assert x2.is_singlet()
##            x2.kill()
            kill_later.append(x1)
            kill_later.append(x2)
        # make the bonds we want and didn't already have 
        for obj1, obj2 in [(Pl1, c), (Pl2, b)]:
            ## bond_atoms_faster(obj1.atom, obj2.atom, V_SINGLE) ### These bonds fail to be deleted when we Undo. Do we need an inval?
            bond_atoms(obj1.atom, obj2.atom)
##        # set directions of all 4 bonds
##        for obj1, obj2 in [(a, Pl1), (Pl1, c), (d, Pl2), (Pl2, b)]:
##            bond = find_bond(obj1.atom, obj2.atom)
##            bond.set_bond_direction_from(obj1.atom, 1)
##        for x in kill_later:
##            x.kill() ### 328p no, this triggers the undo bug again

    # WARNING: after that rebonding, don't use our Pl_recognizers in ways that depend on Pl bonding,
    # since it's not well defined whether they think about the old or new bonding to
    # give their answers.
    del Pl1, Pl2, twoPls

    # transmute base sugars to Sj or Ss as appropriate
    want = make and Element_Sj or Element_Ss
    for obj in (a,b,c,d):
        obj.atom.Transmute(want) # Note: we do this after the bond making/breaking so it doesn't add singlets which mess us up

##    for x in kill_later: # some already dead, should be ok
##        x.kill() ### 329p try here... no, this also triggers the bug.

##    # 330p try this kluge: transmute the pls to their own elts... no, the bug is still there, as if any means of zapping the singlets
##    # is what makes the bug show up, which does suggest a state mashing bug or undo diffing bug.
    for pl in Pl_atoms:
        pl.Transmute(pl.element)
    # 332p HOW ARE atom.bonds lists diffed? could they seem the same but not be? i don't really see how....
    # ok, time to debug those missing valence indicators, etc.
    
    # move Pl atoms into better positions
    # (someday, consider using local minimize; for now, just place them directly between their new neighbor atoms,
    #  hopefully we leave them selected so user can easily do their own local minimize.)
    for pl in Pl_atoms:
        pl.setposn( average_value( map( lambda neighbor: neighbor.posn() , pl.neighbors() ))) ###k average_value correct 

    env.history.message( greenmsg( quote_html( cmdname + ": " + "Done (%s and %s)" % tuple(Pl_atoms) )))

    ###e need anything like assy.changed()?
    
    return # from make_or_unmake_crossover

### BUGS:

# - recognizer compute methods should probably have their own error exception class rather than using assert

# WARNING: in this code, the recognizers don't notice changes in mutable input structures,
# such as transmutes or even bonding changes. But they compute derived attributes lazily
# using current (not cached on __init__) values of their input attrs.
#
# That means that the values of their derived attributes, after a mutable
# change in an input structure, depends on whether those attrs (or intermediate attrs
# used to compute them) were also computed before the input change.


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
