# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
ExternalBondSetDrawer.py - can draw an ExternalBondSet, and keep drawing caches
for it (e.g. display lists, perhaps for multiple drawing styles)

@author: Bruce
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

"""

from graphics.model_drawing.TransformedDisplayListsDrawer import TransformedDisplayListsDrawer

from graphics.drawing.ColorSorter import ColorSorter

from model.elements import PeriodicTable
import graphics.drawing.drawing_globals as drawing_globals
##import foundation.env as env
from utilities.debug import print_compact_traceback

_DEBUG_DL_REMAKES = False

# ==

class ExternalBondSetDrawer(TransformedDisplayListsDrawer):
    """
    """
    def __init__(self, ebset):
        # review: GL context not current now... could revise caller so it was

        TransformedDisplayListsDrawer.__init__(self)
        
        self._ebset = ebset # the ExternalBondSet we'll draw

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._ebset)
    
    def destroy(self):
        """
        remove cyclic refs, free display lists, etc
        """
        self._ebset = None

    def _ok_to_deallocate_displist(self): #bruce 071103
        """
        Say whether it's ok to deallocate self's OpenGL display list
        right now (assuming our OpenGL context is current).

        [overrides TransformedDisplayListsDrawer method]
        """
        return self._ebset.empty()
            # conservative -- maybe they're in a style that doesn't draw them --
            # otoh, current code would still try to use a display list then
            # (once it supports DLs at all -- not yet as of 090213)

    def invalidate_display_lists_for_style(self, style): #bruce 090217
        """
        @see: documentation of same method in class Chunk

        [overrides superclass method]
        """
        #### TODO: revise this when we can cache display lists even for
        # non-current display styles, to revise any cached style-including
        # display lists, whether or not that's the current style.
        
        # note: this is needed in principle, but might not be needed in
        # practice for the current calls. If it's slow, consider
        # a style-specific optim. [bruce 090217]
        
        c1, c2 = self._ebset.chunks
        if not self.glpane or \
           c1.get_dispdef(self.glpane) == style or \
           c2.get_dispdef(self.glpane) == style:
            self.invalidate_display_lists()
        return

    def draw(self, glpane, drawLevel, highlight_color):
        """
        Draw all our bonds. Make them look selected if our ExternalBondSet
        says it should look selected (and if glpane._remake_display_lists
        is set).
        """

        color = self._ebset.bondcolor()
        disp = self._ebset.get_dispdef(glpane)
        
        if 0: ##  debug_pref:
            # initial testing stub -- just draw in immediate mode, in the same way
            # as if we were not being used.

            # modified from Chunk._draw_external_bonds:
            
            use_outer_colorsorter = True # not sure whether/why this is needed

            if highlight_color is not None:
                color = highlight_color # untested, also questionable cosmetically
            
            if use_outer_colorsorter:
                ColorSorter.start(glpane, None)

            for bond in self._ebset._bonds.itervalues():
                bond.draw(glpane, disp, color, drawLevel)
            
            if use_outer_colorsorter:
                ColorSorter.finish(draw_now = True)

            return

        ### note: never calls superclass TransformedDisplayListsDrawer.draw,
        # as of before 090211

        ### DUPLICATED CODE WARNING:
        # the following is similar in many ways to ChunkDrawer.draw.
        # See related comment there.
        
        # KLUGE: we'll use disp and color below, even though they come
        # from whichever of our chunks gets drawn first (i.e. occurs first
        # in Model Tree order). [After changing how we get them, bruce 090227,
        # that remains true -- it's just also true, now, even when we're
        # highlighted, fixing some bugs, except in rare cases where we were
        # never drawn unhighlighted.] The reasons are:
        #
        # - avoids changing current behavior about which chunk disp and color
        #   gets used (changing that is desirable, but nontrivial to design
        #   the intent);
        #
        # - not easy to recode things to draw bonds with half-colors
        #   (though if disps differ, drawing it both ways would be easy).
        #
        # Note that we'd like to optim color changes, which is probably easy
        # in the DL case but not yet easy in the shader case, so nevermind that
        # for now. (Also disp changes, which would be easier.)
        #
        # We'd also like to use this method for highlighting; that's a separate
        # project which needs its own review; it might motivate us to revise
        # this, but probably not, since CSDL and DrawingSet draw methods
        # implement highlighting themselves, whether or not it's a solid color.
        #
        # [bruce 090217 comments & revisions]
        
        # first, return early if no need to draw self at all

        self.glpane = glpane # needed, for superclass displist deallocation
        
        ebset = self._ebset
        
        if ebset.empty():
            print "fyi: should never happen: drawing when empty: %r" % self
            return

        chunks = ebset.chunks
        c1, c2 = chunks
        
        if c1.hidden and c2.hidden:
            return

        highlighted = highlight_color is not None
        
        # TODO: return if disp (from both chunks) doesn't draw bonds
        # and none of our bonds' atoms
        # have individual display styles set; for now, this situation will result
        # in our having an empty CSDL but drawing it

        
        # TODO: frustum culling:
        #
        # - we don't yet have a bbox;
        #
        # do this when time, before release:
        # - but we could approximate this (well enough, for DNA rung bonds)
        #   as convex hull of our chunks, or more precisely as the round lozenge
        #   which is convex hull of their bounding spheres (using max radius for
        #   both); see ebset bounding methods and their comments for more info,
        #   incl about caching the bounding volume in relative coords when we
        #   use those here.
        #
        # - for now, use the debug_pref which avoids drawing unless when both
        #   chunks get culled (wrong in general; ok for dna unless zoomed inside
        #   a single ladder).


        # make sure self's CSDLs (display lists) are up to date, then draw them

        c1.basepos # for __getattr__ effect (precaution, no idea if needed)
        c2.basepos

        if not highlighted:
            self.track_use()

        ### REVIEW: need anything like glPushName(some glname) ? maybe one glname for the ebset itself?
        # guess: not needed: in DL case, bond glnames work, and in shader case, they work as colors,
        # implemented in the shaders themselves.

        #### TODO: glPushMatrix() etc, using matrix of chunk1. (here or in a subr)
        # Not needed until our coords are relative (when we optimize drag).

        eltprefs = PeriodicTable.color_change_counter, PeriodicTable.rvdw_change_counter
        matprefs = drawing_globals.glprefs.materialprefs_summary()

        # Note: if we change how color and/or disp from our two chunks are combined
        # to determine our appearance, or if color of some bonds can be a combination
        # of color from both chunks, havelist_data might need revision.
        # For now, AFAIK, we draw with a single color and disp, so the following is
        # correct regardless of how they are determined (but the determination
        # ought to be stable to reduce undesirable color changes and DL remakes;
        # this was improved on 090227 re selection and highlighting).
        # See also the KLUGE comment above. [bruce 090217/090227]
        if color is not None:
            color = tuple(color)
                # be sure it's not a Numeric array (so we can avoid bug
                # for '==' without having to use same_vals)
        havelist_data = (disp, color, eltprefs, matprefs, drawLevel)
        
        # note: havelist_data must be boolean true

        # note: in the following, the only difference from the chunk case is:
        # [comment not yet updated after changes of 090227]
        # missing:
        # - extra_displists
        # - some exception protection
        # different:
        # - c1.picked and c2.picked (two places)
        # - args to _draw_for_main_display_list
        # - comments
        # - some error message text
        # - maybe, disp and color

        draw_outside = [] # csdls to draw
        
        if self.havelist == havelist_data:
            # self.displist is still valid -- use it
            draw_outside += [self.displist]
        else:
            # self.displist needs to be remade (and then drawn, or also drawn)
            if _DEBUG_DL_REMAKES:
                print "remaking %r DL since %r -> %r" % \
                      (self, self.havelist, havelist_data)
            if not self.havelist:
                self._havelist_inval_counter += 1
                # (probably not needed in this class, but needed in chunk,
                #  so would be in common superclass draw method if we had that)
            self.havelist = 0
            wantlist = glpane._remake_display_lists
            if wantlist:
                # print "Regenerating display list for %r (%d)" % \
                #       (self, env.redraw_counter)
                match_checking_code = self.begin_tracking_usage()
                ColorSorter.start(glpane, self.displist)
                    # picked arg not needed since draw_now = False in finish

            # protect against exceptions while making display list,
            # or OpenGL will be left in an unusable state (due to the lack
            # of a matching glEndList) in which any subsequent glNewList is an
            # invalid operation.
            try:
                self._draw_for_main_display_list(
                    glpane, disp, color, drawLevel,
                    wantlist )
            except:
                msg = "exception in ExternalBondSet._draw_for_main_display_list ignored"
                print_compact_traceback(msg + ": ")

            if wantlist:
                ColorSorter.finish(draw_now = False)
                draw_outside += [self.displist]
                self.end_tracking_usage( match_checking_code, self.invalidate_display_lists )
                self.havelist = havelist_data
                
                # always set the self.havelist flag, even if exception happened,
                # so it doesn't keep happening with every redraw of this Chunk.
                #e (in future it might be safer to remake the display list to contain
                # only a known-safe thing, like a bbox and an indicator of the bug.)
            pass

        # note: if we ever have a local coordinate system, we may have it in
        # effect above but not below, like in ChunkDrawer; review at that time.

        for csdl in draw_outside:
            glpane.draw_csdl(csdl,
                             selected = self._ebset.should_draw_as_picked(),
                                 # note: if not wantlist, this doesn't run,
                                 # so picked appearance won't happen
                                 # unless caller supplies it in color
                                 # (which is not equivalent)
                             highlight_color = highlight_color)
        return
    
    def _draw_for_main_display_list(self, glpane, disp, color, drawLevel, wantlist):
        """
        Draw graphics primitives into the display list (actually CSDL)
        set up by the caller. (For now, there is only one display list,
        which contains all our drawing under all conditions.)
        """
        #bruce 090213, revised 090217

        # todo: let caller pass (disp, color) pair for each chunk,
        # reorder atoms in each bond to correspond to that order
        # (easy if we always use chunk id sorting for that),
        # and draw things in a sensible way given both (disp, color) pairs.
        # This is mainly waiting for that "sensible way" to be designed. 
        
        for bond in self._ebset._bonds.itervalues():
            bond.draw(glpane, disp, color, drawLevel)
        return

    pass # end of class ExternalBondSetDrawer

# end
