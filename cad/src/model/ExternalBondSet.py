# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
ExternalBondSet.py - keep track of external bonds, to optimize redraw

@author: Bruce
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 080702 created

bruce 090211 making compatible with TransformNode, though that is unfinished
and not yet actually used.

(Update: as of 090225 TransformNode is abandoned.
However, I'm leaving some comments that refer to TransformNode in place
(in still-active files), since they also help point out the code which any 
other attempt to optimize rigid drags would need to modify. In those comments,
dt and st refer to dynamic transform and static transform, as used in
scratch/TransformNode.py.)

"""

# plan:
#
# initial test implem: do all bond drawing through this object,
# but do it just as often as right now, in the same way.
#
# see chunk._draw_external_bonds

# for now, we just maintain them but do nothing else with them,
# as of 080702 noon PT. update 080707: a debug_pref draws with them,
# false by default since predicted to be a slowdown for now. 
# Retesting this 090126, it seems to work. Put drawing code into
# ExternalBondSetDrawer, but not yet doing any caching there (CSDLs).
# When we do, not yet known how much inval/update code goes there vs. here.


from geometry.VQT import V, vlen

from graphics.model_drawing.ExternalBondSetDrawer import ExternalBondSetDrawer
    # todo: this import shouldn't be needed once we have the right
    # GraphicsRule architecture

_DEBUG_EBSET = False # ok to commit with True, until the debug_pref 
    # that calls us is on by default


class ExternalBondSet(object):
    """
    Know about all external bonds between two specific chunks,
    and cache info to speed their redrawing, including display lists.
    When the appearance or set of bonds change, we might be invalidated,
    or destroyed and remade, depending on client code.
    """
    def __init__(self, chunk1, chunk2):
        self.chunks = (chunk1, chunk2) # note: not private
            # note: our chunks are also called "our nodes",
            # since some of this code would work for them being any TransformNodes
            # WARNING: KLUGE: self.chunks might be reordered inside self.draw.
            # The order has no effect on anything except drawing,
            # and need not remain constant or relate to atom order in our bonds.
        # maybe todo: rename: _f_bonds
        self._bonds = {}
        self._drawer = ExternalBondSetDrawer(self) 
            # review: make on demand? GL context not current now...
            # hopefully ok, since it will only make DL on demand during .draw.
        return

    def __repr__(self):
        res = "<%s at %#x with %d bonds for %r>" % \
              (self.__class__.__name__.split('.')[-1],
               id(self),
               len(self._bonds),
               self.chunks # this is () if self is destroyed
              )
        return res
    
    def is_currently_bridging_dynamic_transforms(self):
        """
        @return: whether not all of our nodes share the same dynamic
                 transform object (counting None as such as object)
        @rtype: boolean
        """
        dt1 = self.chunks[0].dynamic_transform
        for chunk in self.chunks:
            if chunk.dynamic_transform is not dt1:
                return True
        return False

    def invalidate_distortion(self):
        """
        Called when any of our nodes' (chunks') dynamic transforms changes
        transform value (thus moving that node in space), if not all of our
        nodes share the same dynamic transform object, or when any of our nodes
        gets distorted internally (i.e. some of its atoms move, other than by
        all of them moving rigidly).
        """
        self.invalidate_display_lists()
        return
    
    def invalidate_display_lists(self):
        self._drawer.invalidate_display_lists()
        return
        
    def invalidate_display_lists_for_style(self, style): #bruce 090217
        """
        @see: documentation of same method in class Chunk
        """
        self._drawer.invalidate_display_lists_for_style(style)

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
        # removed for speed: assert self._correct_bond(bond)
        if not self._bonds.has_key(id(bond)):
            # test is to avoid needless invalidation (important optim)
            self.invalidate_display_lists()
            self._bonds[id(bond)] = bond
            if _DEBUG_EBSET:
                print "added bond %r to %r" % (bond, self)
        return

    def empty(self): # todo: rename to is_empty
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
            self.invalidate_display_lists()
            for bond in bad:
                del self._bonds[id(bond)]
                if _DEBUG_EBSET:
                    print "removed bond %r from %r" % (bond, self)
        return

    def _correct_bond(self, bond): # REVIEW: might need to speed this up.
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
            # See comment therein. 
            
            # REVIEW: Hopefully it works now and bond.killed can be fixed to
            # check it. Conversely, if it doesn't work right, this routine
            # will probably have bugs of its own.
            
            # (Note: it'd be nice if that was faster, but there might be old
            # code that relies on looking at atoms of a killed bond, so we
            # can't just set the atoms to None. OTOH we don't want to waste
            # Undo time & space with a "killed flag" (for now).)
            return False
        # bond's atoms must (still) point to both of our chunks
        c1 = bond.atom1.molecule
        c2 = bond.atom2.molecule
        return (c1, c2) == self.chunks or (c2, c1) == self.chunks 
            # REVIEW: too slow due to == ? 
            # todo: optimize by sorting these when making bond?
            # (see also the kluge in draw, which can reverse them)
            # [bruce 090126]

    def destroy(self):
        if not self.chunks:
            return # permit repeated destroy
        if _DEBUG_EBSET:
            print "destroying %r" % self
        if self._drawer:
            self._drawer.destroy() # deallocate displists
            self._drawer = None
        for chunk in self.chunks:
            chunk._f_remove_ExternalBondSet(self)
        self.chunks = ()
        self._bonds = () # make len() still work
        ### TODO: other deallocations, e.g. of display lists
        return

    # ==

    # methods needed only for drawing
    
    def bounding_lozenge(self): #bruce 090306 unstubbed this
        # note: return this in abs coords, even after we have a
        # display list and permit relative motion.
        # todo: if this takes time to compute, cache it when
        # we redraw the display list, then
        # transform here into abs coords.
        chunk1, chunk2 = self.chunks
        c1, r1 = chunk1.bounding_sphere()
        c2, r2 = chunk2.bounding_sphere()
        return c1, c2, max(r1, r2)

    def bounding_sphere(self): #bruce 090306 unstubbed this; maybe never called
        # see comments in bounding_lozenge
        c1, c2, r = self.bounding_lozenge()
        return (c1 + c2)/2.0, r + vlen(c2 - c1)/2.0

    def should_draw_as_picked(self):
        """
        Should all the bonds in self be drawn as looking selected?

        @see: same named method in class Bond
        """
        # note: same-named method in class Bond has equivalent code
        # (after implem revised 090227)
        # warning: ChunkDrawer has an optim which depends on this
        # method's semantics; see its selColor assignment.
        return self.chunks[0].picked and self.chunks[1].picked

    def bondcolor(self): #bruce 090227
        """
        Return the color in which to draw all our bonds.
        """
        return self.chunks[0].drawing_color()
            # Note: this choice of bondcolor is flawed, because it depends
            # on which chunk is drawn first of the two that are connected.
            # (The reason it depends on that is because of a kluge in which
            #  we reorder the chunks to match that order, in self.draw().
            #  It would be better if it depended more directly on model tree
            #  order (the same, provided the chunks actually get drawn),
            #  or on something else (e.g. axis vs strand chunks).)
            # I'm leaving this behavior in place, but revising how it works
            # in order to avoid color changes or DL remake when highlighting
            # external bonds within ChunkDrawer.draw_highlighted.
            # [bruce 090227]

    def get_dispdef(self, glpane): #bruce 090227
        """
        Return the display style in which to draw all our bonds.
        """
        # [see comments in def bondcolor about choice of self.chunks[0]]
        # Note: if we ever decide to draw our bonds in both styles,
        # when our chunks disagree, we should revise this method's API
        # to return both disps to overdraw. (Or we might let it return
        # an opacity for each one, and also let users set a style like
        # that directly.)
        return self.chunks[0].get_dispdef(glpane)

    def draw(self, glpane, chunk, drawLevel, highlight_color = None):
        # todo: this method (and perhaps even our self._drawer attribute)
        # won't be needed once we have the right GraphicsRule architecture)
        if not self.chunks:
            # we've been destroyed (should not happen)
            return
        if chunk is not self.chunks[0] and highlight_color is None:
            # KLUGE; see self.bondcolor() comment for explanation.
            # This should happen at most once each time the model tree is
            # reordered (or the first time we're drawn), provided we don't
            # do it during ChunkDrawer.draw_highlighted (as we ensure by
            # testing highlight_color). Note that self (and therefore the
            # state of which chunk comes first) lasts as long as both chunks
            # remain alive. [bruce 090227]
            assert chunk is self.chunks[1]
            self.chunks = (self.chunks[1], self.chunks[0])
            pass
        self._drawer.draw(glpane, drawLevel, highlight_color)
    
    pass # end of class ExternalBondSet

# end
