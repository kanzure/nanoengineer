# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
build_utils.py -- some utilities for Build mode.

@author: Josh
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

Original code written by Josh in depositMode.py.

Bruce moved it into this separate file, 050510,
and added superstructure, in preparation for extending it to atom types
with new bonding patterns. And did some of that extension, 050511.
[It's ongoing.]
"""

from geometry.VQT import norm
from model.chem import Atom

from utilities.debug import print_compact_traceback

class DepositionTool:
    "#doc"
    pass

class PastableDepositionTool(DepositionTool): # not yet filled in (with code from depositMode.py) or used
    def __init__(self, pastable):
        self.pastable = pastable
        return
    def attach_to(self, singlet, autobond = True): # NIM (in PastableDepositionTool)
        assert 0, "nim"
    pass

class AtomTypeDepositionTool(DepositionTool):
    """
    DepositionTool for depositing atoms of a given type (element and bonding pattern).
    """
    #bruce 050510 made this from some methods in depositMode, and extended it for atomtypes.
    def __init__(self, atomtype):
        self.atomtype = atomtype
        return

    ###################################################################
    #  Oh, ye acolytes of klugedom, feast your eyes on the following  #
    ###################################################################

    # [comment initially by josh, revised by bruce circa 041115-041215, 050510]
    # singlet is supposedly the lit-up singlet we're pointing to.
    # make a new atom of [our atomtype].
    # bond the new atom to singlet, and to any other singlets around which you'd
    # expect it to form bonds with (for now this might be based solely on nearness ###@@@).
    # Also make new singlets to reach desired total number of bonds.
    #   Note that these methods don't use self except to
    # find each other... so they could be turned into functions for general use. #e
    #   To help fix bug 131 I'm [bruce circa 041215] splitting each of the old code's methods
    # bond1 - bond4 into a new method to position and make the new atom (for any number of bonds)
    # and methods moved to class atom to add more singlets as needed.

    # bruce 041123 new features:
    # return the new atom and a description of it, or None and the reason we made nothing.

    def attach_to( self, singlet, autobond = True, autobond_msg = True): # in AtomTypeDepositionTool
        # [bruce 050831 added autobond option; 050901 added autobond_msg]
        """
        [public method]
        Deposit a new atom of self.atomtype onto the given singlet,
        and (if autobond is true) make other bonds (to other near-enough atoms with singlets)
        as appropriate. (But never more than one bond per other real atom.)

        @return: a 2-tuple consisting of either the new atom and a description
                 of it, or None and the reason we made nothing.

        ###@@@ should worry about bond direction! at least as a filter!
           If autobond_msg is true, mention the autobonding done or not done (depending on autobond option),
        in the returned message, if any atoms were near enough for autobonding to be done.
        This option is independent from the autobond option.
        [As of 050901 not all combos of these options have been tested. ###@@@]
        """
        atype = self.atomtype
        if not atype.numbonds:
            whynot = "%s makes no bonds; can't attach one to an open bond" % atype.fullname_for_msg()
            return None, whynot
        if not atype.can_bond_to(singlet.singlet_neighbor(), singlet):
            #bruce 080502 new feature
            whynot = "%s bond to %r is not allowed" % (atype.fullname_for_msg(), singlet.singlet_neighbor())
                # todo: return whynot from same routine
            return None, whynot
        spot = self.findSpot(singlet)
        pl = [(singlet, spot)] # will grow to a list of pairs (s, its spot)
            # bruce change 041215: always include this one in the list
            # (probably no effect, but gives later code less to worry about;
            #  before this there was no guarantee singlet was in the list
            #  (tho it probably always was), or even that the list was nonempty,
            #  without analyzing the subrs in more detail than I'd like!)

        if autobond or autobond_msg: #bruce 050831 added this condition; 050901 added autobond_msg
            # extend pl to make additional bonds, by adding more (singlet, spot) pairs
            rl = [singlet.singlet_neighbor()]
                # list of real neighbors of singlets in pl [for bug 232 fix]
            ## mol = singlet.molecule
            cr = atype.rcovalent
            # bruce 041215: might as well fix the bug about searching for open bonds
            # in other mols too, since it's easy; search in this one first, and stop
            # when you find enough atoms to bond to.
            searchmols = list(singlet.molecule.part.molecules) #bruce 050510 revised this
            searchmols.remove(singlet.molecule)
            searchmols.insert(0, singlet.molecule)
            # max number of real bonds we can make (now this can be more than 4)
            maxpl = atype.numbonds

            for mol in searchmols:
                for s in mol.nearSinglets(spot, cr * 1.9):
                        #bruce 041216 changed 1.5 to 1.9 above (it's a heuristic);
                        # see email discussion (ninad, bruce, josh)
                    #bruce 041203 quick fix for bug 232:
                    # don't include two singlets on the same real atom!
                    # (It doesn't matter which one we pick, in terms of which atom we'll
                    #  bond to, but it might affect the computation in the bonding
                    #  method of where to put the new atom, so ideally we'd do something
                    #  more principled than just using the findSpot output from the first
                    #  singlet in the list for a given real atom -- e.g. maybe we should
                    #  average the spots computed for all singlets of the same real atom.
                    #  But this is good enough for now.)
                    #bruce 050510 adds: worse, the singlets are in an arb position... 
                    # really we should just ask if it makes sense to bond to each nearby *atom*, 
                    # for the ones too near to comfortably *not* be bonded to. ###@@@
                    ###@@@ bruce 050221: bug 372: sometimes s is not a singlet. how can this be??
                    # guess: mol.singlets is not always invalidated when it should be. But even that theory
                    # doesn't seem to fully explain the bug report... so let's find out a bit more, at least:
                    try:
                        real = s.singlet_neighbor() 
                    except:
                        print_compact_traceback("bug 372 caught red-handed: ")
                        print "bug 372-related data: mol = %r, mol.singlets = %r" % (mol, mol.singlets)
                        continue
                    if real not in rl and atype.can_bond_to(real, s, auto = True):
                        # checking can_bond_to is bruce 080502 new feature
                        pl += [(s, self.findSpot(s))]
                        rl += [real]
                # after we're done with each mol (but not in the middle of any mol),
                # stop if we have as many open bonds as we can use
                if len(pl) >= maxpl:
                    break
            del mol, s, real

        n = min(atype.numbonds, len(pl)) # number of real bonds to make (if this was computed above); always >= 1
        pl = pl[0:n] # discard the extra pairs (old code did this too, implicitly)
        if autobond_msg and not autobond:
            pl = pl[0:1] # don't actually make the bonds we only wanted to tell the user we *might* have made
        # now pl tells which bonds to actually make, and (if autobond_msg) n tells how many we might have made.

        # bruce 041215 change: for n > 4, old code gave up now;
        # new code makes all n bonds for any n, tho it won't add singlets
        # for n > 4. (Both old and new code don't know how to add enough
        # singlets for n >= 3 and numbonds > 4. They might add some, tho.)
        # Note: _new_bonded_n uses len(pl) as its n. As of 050901 this might differ from the variable n.
        atm = self._new_bonded_n( pl)
        atm.make_enough_bondpoints() # (tries its best, but doesn't always make enough)
        desc = "%r (in %r)" % (atm, atm.molecule.name)
        #e what if caller renames atm.molecule??
        if n > 1: #e really: if n > (number of singlets clicked on at once)
            if autobond:
                msg = " (%d bond(s) made)" % n
            else:
                msg = " (%d bond(s) NOT made, since autobond is off)" % (n-1) #bruce 050901 new feature
            from platform_dependent.PlatformDependent import fix_plurals
            msg = fix_plurals(msg)
            desc += msg
        return atm, desc

    # given self.atomtype and a singlet, find the place an atom of that type
    # would like to be if bonded at that singlet,
    # assuming the bond direction should not change.
    #e (Should this be an AtomType method?)
    def findSpot(self, singlet):
        obond = singlet.bonds[0]
        a1 = obond.other(singlet)
        cr = self.atomtype.rcovalent
        pos = singlet.posn() + cr*norm(singlet.posn()-a1.posn())
        return pos

    def _new_bonded_n( self, lis):
        """
        [private method]

        Make and return an atom (of self.atomtype) bonded to the base atoms
        of the n bondpoints in lis, in place of those bondpoints,
        which is a list of n pairs (singlet, pos), where each pos is the ideal
        position for a new atom bonded to its singlet alone.
        The new atom will always have n real bonds and no bondpoints,
        and be positioned at the average of the positions passed as pos.
        We don't check whether n is too many bonds for self.atomtype, nor do we care what
        kind of bond positions it would prefer. (This is up to the caller, if
        it matters; since the bondpoints typically already existed, there's not
        a lot that could be done about the bonding pattern, anyway, though we
        could imagine finding a position that better matched it. #e)
        """
        # bruce 041215 made this from the first parts of the older methods bond1
        # through bond4; the rest of each of those have become atom methods like
        # make_bondpoints_when_2_bonds.
        # The caller (self.attach [now renamed self.attach_to]) has been revised
        # to use these, and the result is (I think) equivalent to the old code,
        # except when el.numbonds > 4 [later: caller's new subrs now use atomtype not el],
        # when it does what it can rather than
        # doing nothing. The purpose was to fix bug 131 by using the new atom
        # methods by themselves.
        s1, p1 = lis[0]
        mol = s1.molecule # (same as its realneighbor's mol)
        totpos = + p1 # (copy it, so += can be safely used below)
        for sk, pk in lis[1:]: # 0 or more pairs after the first
            totpos += pk # warning: += can modify a mutable totpos
        pos = totpos / (0.0 + len(lis)) # use average of ideal positions
        atm = Atom(self.atomtype, pos, mol)
        for sk, pk in lis:
            sk.bonds[0].rebond(sk, atm)
        return atm

    pass # end of class AtomTypeDepositionTool

# end
