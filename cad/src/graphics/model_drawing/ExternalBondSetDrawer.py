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
from graphics.drawing.ColorSorter import ColorSortedDisplayList # not yet used?

# ==

class ExternalBondSetDrawer(TransformedDisplayListsDrawer):
    """
    """
    def __init__(self, ebset):
        # review: GL context not current now... could revise caller so it was
        self.ebset = ebset # the ExternalBondSet we'll draw
    
    def destroy(self):
        """
        remove cyclic refs, free display lists, etc
        """
        self.ebset = None

    def _ok_to_deallocate_displist(self): #bruce 071103
        """
        Say whether it's ok to deallocate self's OpenGL display list
        right now (assuming our OpenGL context is current).

        [overrides TransformedDisplayListsDrawer method]
        """
        return self.ebset.empty()
            # conservative -- maybe they're in a style that doesn't draw them --
            # otoh, current code would still try to use a display list then
            # (once it supports DLs at all -- not yet as of 090213)

    def draw(self, glpane, disp, color, drawLevel): # selected? highlighted?
        # initial testing stub -- just draw in immediate mode, in the same way
        # as if we were not being used.
        # (notes for a future implem: 
        #  displist still valid (self.ebset._invalid)? culled?)


        ##### note: does not yet ever call superclass TransformedDisplayListsDrawer.draw, as of before 090211
        

        # modified from Chunk._draw_external_bonds:
        
        use_outer_colorsorter = True # not sure whether/why this is needed
        
        if use_outer_colorsorter:
            ColorSorter.start(None)

        for bond in self.ebset._bonds.itervalues():
            bond.draw(glpane, disp, color, drawLevel)
        
        if use_outer_colorsorter:
            ColorSorter.finish()

        return

    def _draw_into_displist(self, glpane, disp, drawLevel): # not yet called
        color = None ###k
        for bond in self.ebset._bonds.itervalues():
            bond.draw(glpane, disp, color, drawLevel)
        return

    def invalidate_display_lists(self):
        # we don't yet have any display lists, so do nothing
        
        # note, this is called even if we didn't turn on the debug_pref to draw using this object!
        # at present [090213] it's called at least once per external bond when dna is being rigidly dragged.
        # once TransformNode works well enough, it won't be called for rigid drag.
        
        ## print "called invalidate_display_lists in", self # happens a lot when dragging one end of ext bond (good)
        return

    pass # end of class

# end
