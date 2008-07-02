# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ExternalBondSet.py - keep track of external bonds, to optimize redraw

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""

# plan:
#
# initial test implem: do all bond drawing through this object,
# but do it just as often as right now, in the same way.
#
# see chunk.draw_external_bonds

# for now, we just maintain them but do nothing else with them, as of 080702 noon PT

_DEBUG_EBSET = False # DO NOT COMMIT WITH TRUE

class ExternalBondSet(object):
    """
    Know about all external bonds between two specific chunks,
    and cache info to speed their redrawing, including display lists.
    When the appearance or set of bonds change, we might be invalidated,
    or destroyed and remade, depending on client code.
    """
    def __init__(self, chunk1, chunk2):
        self.chunks = (chunk1, chunk2) # note: not private
        self._bonds = {}
        self._invalid = True # since we have no display list for drawing
        return

    def other_chunk(self, chunk):
        """
        @see: Bond.other_chunk
        """
        c1, c2 = self.chunks
        if chunk is c1:
            return c2
        elif chunk is c2:
            return c1
        assert 0
        return
    
    def add_bond(self, bond):
        """
        Add this bond to self, if not already there.
        It must be a bond between our two chunks (not checked).
        Do appropriate invals within self.
        """
        assert self._correct_bond(bond) # REMOVE WHEN DEVEL IS DONE (for speed)
        if not self._bonds.has_key(id(bond)):
            # test is to avoid needless invalidation (important optim)
            self._invalid = True
            self._bonds[id(bond)] = bond
            if _DEBUG_EBSET:
                print "added bond %r to %r" % (bond, self)
        return

    def empty(self):
        return not self._bonds

    def remove_incorrect_bonds(self):
        """
        Some of our bonds may have been killed, or their atoms have changed,
        or their atom parents (chunks) have changed, so they are no longer
        correctly our members. Remove any such bonds, and do appropriate
        invals within self.
        """
        bad = []
        for bond in self._bonds.itervalues():
            if not self._correct_bond(bond):
                bad.append(bond)
        if bad:
            self._invalid = True # REVIEW: do more, in a method?
            for bond in bad:
                del self._bonds[id(bond)]
                if _DEBUG_EBSET:
                    print "removed bond %r from %r" % (bond, self)
        return

    def _correct_bond(self, bond):
        """
        Is bond, which once belonged in self, still ok to have in self?
        If not, it's because it was killed, or its atoms are not in both
        of self's chunks.
        """
        # bond must not be killed
        if bond.killed():
            return False
        if bond not in bond.atom1.bonds:
            # This ought to be checked by bond.killed, but isn't yet!
            # See comment therein. REVIEW: Hopefully it works now and bond.killed
            # can be fixed to check it. Conversely, if it doesn't work right,
            # this routine will probably have bugs of its own.
            # (Note: it'd be nice if that was faster, but there might be old code that
            # relies on looking at atoms of a killed bond, so we can't just
            # set the atoms to None. OTOH we don't want to waste Undo time & space
            # with a "killed flag" (for now).)
            return False
        # bond's atoms must (still) point to both of our chunks
        c1 = bond.atom1.molecule
        c2 = bond.atom2.molecule
        return (c1, c2) == self.chunks or (c2, c1) == self.chunks # REVIEW: too slow due to == ?

    def destroy(self):
        if not self.chunks:
            return # permit repeated destroy
        if _DEBUG_EBSET:
            print "destroying %r" % self
        for chunk in self.chunks:
            chunk._f_remove_ExternalBondSet(self)
        self.chunks = ()
        self._bonds = () # make len() still work
        ### TODO: other deallocations, e.g. of display lists
        return

    def __repr__(self):
        res = "<%s at %#x with %d bonds for %r>" % \
              (self.__class__.__name__.split('.')[-1],
               id(self),
               len(self._bonds),
               self.chunks # this is () if self is destroyed
              )
        return res

    def draw(self, glpane): # disp? selected? highlighted?
        # still valid?
        # culled?
        # draw...
        nim
        pass
    
    pass

# end
