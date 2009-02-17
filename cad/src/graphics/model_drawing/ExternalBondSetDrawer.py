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
import foundation.env as env
from utilities.debug import print_compact_traceback

from utilities.debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False ###

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

    def draw(self, glpane, disp, color, drawLevel): # selected? highlighted?
        """
        """
        if 0: ##  debug_pref:
            # initial testing stub -- just draw in immediate mode, in the same way
            # as if we were not being used.

            # modified from Chunk._draw_external_bonds:
            
            use_outer_colorsorter = True # not sure whether/why this is needed
            
            if use_outer_colorsorter:
                ColorSorter.start(None)

            for bond in self._ebset._bonds.itervalues():
                bond.draw(glpane, disp, color, drawLevel)
            
            if use_outer_colorsorter:
                ColorSorter.finish()

            return

        ### note: never calls superclass TransformedDisplayListsDrawer.draw,
        # as of before 090211

        ### DUPLICATED CODE WARNING:
        # the following is similar in many ways to ChunkDrawer.draw.
        # See related comment there.

        del disp, color #### REVIEW, esp when highlighted
        
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

        self.track_use()

        ### REVIEW: need anything like glPushName(some glname) ? maybe one glname for the ebset itself?
        # guess: not needed: in DL case, bond glnames work, and in shader case, they work as colors,
        # implemented in the shaders themselves.

        #### TODO: glPushMatrix() etc, using matrix of chunk1. (here or in a subr)
        # Not needed until our coords are relative (when we optimize drag).

        disp1 = c1.get_dispdef(glpane)
        disp2 = c2.get_dispdef(glpane)
        eltprefs = PeriodicTable.color_change_counter, PeriodicTable.rvdw_change_counter
        matprefs = drawing_globals.glprefs.materialprefs_summary()

        havelist_data = (disp1, disp2, eltprefs, matprefs, drawLevel)
            # note: havelist_data must be boolean true

        # note: in the following, the only difference from the chunk case is:
        # - extra_displists
        # - some exception protection
        # - c1.picked and c2.picked (two places)
        # - args to _draw_for_main_display_list
        # - comments
        # - some error message text
        
        if self.havelist == havelist_data:
            # self.displist is still valid -- use it
            self.displist.draw(selected = c1.picked and c2.picked)
        else:
            # self.displist needs to be remade (and then drawn, or also drawn)
            if not self.havelist:
                self._havelist_inval_counter += 1
                # (probably not needed in this class, but needed in chunk,
                #  so would be in common superclass draw method if we had that)
            self.havelist = 0
            try:
                wantlist = not env.mainwindow().movie_is_playing #bruce 051209
                    # warning: use of env.mainwindow is a KLUGE
                    #### REVIEW: is this a speedup (as intended) or a slowdown?
            except:
                print_compact_traceback("exception (a bug) ignored: ")
                wantlist = True

            if wantlist:
                print "Regenerating display list for %r (%d)" % \
                      (self, env.redraw_counter)
                       ##### remove when works and tested
                match_checking_code = self.begin_tracking_usage()
                ColorSorter.start(self.displist, c1.picked and c2.picked)
                    # not sure whether picked arg needed

            # protect against exceptions while making display list,
            # or OpenGL will be left in an unusable state (due to the lack
            # of a matching glEndList) in which any subsequent glNewList is an
            # invalid operation.
            try:
                self._draw_for_main_display_list(
                    glpane, disp1, disp2, drawLevel,
                    wantlist )
            except:
                msg = "exception in ExternalBondSet._draw_for_main_display_list ignored"
                print_compact_traceback(msg + ": ")

            if wantlist:
                ColorSorter.finish()
                self.end_tracking_usage( match_checking_code, self.invalidate_display_lists )
                self.havelist = havelist_data
                
                # always set the self.havelist flag, even if exception happened,
                # so it doesn't keep happening with every redraw of this Chunk.
                #e (in future it might be safer to remake the display list to contain
                # only a known-safe thing, like a bbox and an indicator of the bug.)
            pass

        return
    
    def _draw_for_main_display_list(self, glpane, disp1, disp2, drawLevel, wantlist): #bruce 090213, working stub
        print "_draw_for_main_display_list in %r (%d)" % (self, env.redraw_counter) #####
        disp = disp1 #### guess: if they differ, draw it twice, or choose max, or treat halves differently
        color = None #### guess: might be needed for override if highlighting, but better to optim that somehow
        for bond in self._ebset._bonds.itervalues():
            bond.draw(glpane, disp, color, drawLevel)
        return

    pass # end of class

# end
