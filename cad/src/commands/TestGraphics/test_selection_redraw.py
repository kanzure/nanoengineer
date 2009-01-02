# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
test_selection_redraw.py - test case for frequent moving of CSDLs between DrawingSets

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details. 
"""

import random

# most not needed:
from graphics.drawing.DrawingSet import DrawingSet
from graphics.drawing.TransformControl import TransformControl
from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList
from graphics.drawing.CS_draw_primitives import drawsphere

from commands.TestGraphics.GraphicsTestCase import GraphicsTestCase

# ==

_NUM_DRAWINGSETS = 5

_PROBABILITY_OF_MOVE = 0.2

## _NUM_CSDLS_X = 10 # this is now a local variable from a test parameter
## _NUM_CSDLS_Y = 10
_NUM_SPHERES_PER_CSDL = 5

# ==

class CSDL_holder(object):
    """
    Represent a CSDL in a particular DrawingSet.
    
    (CSDL itself can't be used for this, since a CSDL
    can be in more than one DrawingSet at a time.)
    """
    drawingset = None
    def __init__(self, x, y, n):
        self.csdl = ColorSortedDisplayList()
        # draw into it, based on x, y, n
        ColorSorter.start(self.csdl)
        for i in range(n):
            z = i - (_NUM_SPHERES_PER_CSDL - 1) / 2.0
            color = (random.uniform(0.2, 0.8),
                     0,
                     random.uniform(0.2, 0.8))
            pos = (x, y, z)
            radius = 0.25 # 0.5 would be touching the next ones
            drawsphere(color,
                       pos,
                       radius,
                       2 ## DRAWSPHERE_DETAIL_LEVEL
             )
        ColorSorter.finish(draw_now = False)
        return
    def change_drawingset(self, drawingset):
        old = self.drawingset
        new = drawingset
        self.drawingset = new
        if old is not new:
            if old:
                old.removeCSDL(self.csdl) #e remove_csdl?
            if new:
                new.addCSDL(self.csdl) #e add_csdl?
            pass
        return
    pass

class test_selection_redraw(GraphicsTestCase):
    """
    test case for frequent moving of CSDLs between DrawingSets:
    
    Exercise graphics similar to selection/deselection, rapid change of highlighting, etc,
    by moving CSDLs rapidly between several DrawingSets drawn in different styles.
    
    If this is too slow per-frame due to setup cost, we can ignore this at first
    since highlighting can be done differently
    and selection doesn't change during most frames.
    
    But it is still a useful test for correctness,
    and for speed of selection changes that need to be reasonably responsive
    even if not occurring on most frames.
    """
    # test results [bruce 090102, usual Mac]:
    # For my initial parameters of 10 x 10 chunks of 5 spheres, 
    # in 5 drawingsets (one not drawn), changing 20% of styles each time,
    # I get about 20 msec per frame 
    # (or 44 msec if 'Use batched primitive shaders?' is turned off).
    # But this is only 500 spheres, far less than realistic.
    def __init__(self, *params):
        GraphicsTestCase.__init__(self, *params) 
            ### review: split into __init__ and setup methods? or use activate for the following?
        _NUM_CSDLS_X = _NUM_CSDLS_Y = self._params[0]
        # set up a lot of CSDLs, in wrappers that know which DrawingSet they're in (initially None)
        self._csdls = [ CSDL_holder((i % _NUM_CSDLS_X) - (_NUM_CSDLS_X - 1) / 2.0, 
                                    ((i / _NUM_CSDLS_X) % _NUM_CSDLS_Y) - (_NUM_CSDLS_Y - 1) / 2.0,
                                    _NUM_SPHERES_PER_CSDL)
                        for i in range(_NUM_CSDLS_X * _NUM_CSDLS_Y) ]
        # set up our two DrawingSets (deselected first)
        self.drawingsets = [DrawingSet() for i in range(_NUM_DRAWINGSETS)] 
        self.drawingsets[-1] = None # replace the last one with None, for hidden CSDLs
        # put all the CSDLs in the first one
        for csdl in self._csdls:
            csdl.change_drawingset(self.drawingsets[0])
        return
    def activate(self):
        # make sure the correct two DrawingSets will be drawn
        pass # implicit in our def of draw_drawingsets
    def draw(self):
        # move some of the CSDLs from one to another DrawingSet
        # (for now, just put each one into a pseudorandomly chosen DrawingSet, out of all of them)
        num_sets = len(self.drawingsets)
        csdls_to_move = self._csdls
        for csdl in csdls_to_move:
            if random.random() <= _PROBABILITY_OF_MOVE and num_sets > 1:
                # move this csdl to a new drawingset (enforced actually different)
                old = csdl.drawingset # always a DrawingSet (or None, if None is a member of self.drawingsets)
                new = old
                while new is old:
                    new = self.drawingsets[ random.randint(0, num_sets - 1) ]
                csdl.change_drawingset(new)
                pass
            continue
        return
    def _draw_drawingsets(self): 
        # note: called after .draw
        for i in range(_NUM_DRAWINGSETS):
            # choose proper drawing style
            options = {}
            # note: default options are:
            ## options = dict(
            ##     highlighted = False, selected = False,
            ##     patterning = True, highlight_color = None, opacity = 1.0 )
            if i == 0: # todo: encapsulate the options with the DrawingSet
                # plain
                pass
            elif i == 1:
                # selected
                options = dict( selected = True)
            elif i == 2:
                # highlighted
                options = dict( highlighted = True)
            elif i == 3:
                # transparent
                options = dict( opacity = 0.5 )
            else:
                # default options
                pass
            if self.drawingsets[i]:
                self.drawingsets[i].draw(**options)
            continue
        return
    pass

# end
