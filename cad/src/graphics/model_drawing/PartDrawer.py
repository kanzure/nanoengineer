# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
PartDrawer.py -- class PartDrawer, for drawing a Part

@author: Bruce
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.


History:

Written over several years as part of class Part in part.py.

Bruce 090218 split this out of class Part.

TODO: also move part of before_drawing_model, after_drawing_model,
and draw into here from Part; add DrawingSet features...
Oops, changed my mind, this whole class is misguided
and is now being cannibalized.
"""

from graphics.drawing.DrawingSet import DrawingSet

# ==

class PartDrawer(object):
    """
    Drawing code needed by class Part, as a cooperating object.
    """

    def __init__(self, part):
        self._part = part #k needed?
        return

    def destroy(self):
        self._part = None
        return

    # note: the Part methods draw, before_drawing_model, after_drawing_model
    # are not sensible to define here for now, but they can call methods
    # in self.
    

    def draw_drawingsets(self):
        """
        Using info collected in self._part.drawing_frame,
        update our cached DrawingSets for this frame;
        then draw them.
        """
        drawing_frame = self._part.drawing_frame
        for intent, csdls in drawing_frame.get_drawingset_intent_csdl_dicts().items():
            # stub: make drawingset from these csdls, then draw it based on intent.
            # - slow since not incremental
            # - incorrect since transforms are ignored
            #   (they're only present in gl state when csdl is added!)
            selected = intent
            ## print "draw_drawingsets stub: selected = %r, %d csdls" % (selected, len( csdls )) ####
            d = DrawingSet(csdls.itervalues())
            # future: d.addCSDL(csdl), d.removeCSDL(csdl)
            d.draw(selected = selected)
            d.destroy()
        return
    
    pass

# end
