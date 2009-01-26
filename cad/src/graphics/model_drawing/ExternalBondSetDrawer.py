# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
ExternalBondSetDrawer.py - can draw an ExternalBondSet, and keep drawing caches
for it (e.g. display lists, perhaps for multiple drawing styles)

@author: Bruce
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

"""

from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList # not yet used?

# ==

class TransformedDisplayListsDrawer(object): # refile when done and name is stable
    """
    Superclass for drawing classes which make use of one or more display lists
    (actually CSDLs) to be drawn relative to a transform. 
    
    (The specific subclass knows where to get the transform,
    and when to invalidate the display lists.)
    """
    pass

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
    
    def draw(self, glpane, disp, color, drawLevel): # selected? highlighted?
        # initial testing stub -- just draw in immediate mode, in the same way
        # as if we were not being used.
        # (notes for a future implem: 
        #  displist still valid (self.ebset._invalid)? culled?)

        # modified from Chunk._draw_external_bonds:
        
        use_outer_colorsorter = True # not sure whether/why this is needed
        
        if use_outer_colorsorter:
            ColorSorter.start(None)

        for bond in self.ebset._bonds.itervalues():
            bond.draw(glpane, disp, color, drawLevel)
        
        if use_outer_colorsorter:
            ColorSorter.finish()

        return

    pass # end of class

# end
