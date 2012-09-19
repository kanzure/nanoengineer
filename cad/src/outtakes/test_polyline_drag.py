# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
test_polyline_drag.py

@author: Bruce
@version: $Id$

Simple test/example code for making a polyline.
Goal is just to demonstrate intercepting mouse events
to change the usual meaning of a click,
detecting GLPane enter/leave, etc.
Not yet suitable for use as a real example.
Doesn't yet store the polyline anywhere.

Just a stub for now.
"""

from exprs.State_preMixin import State_preMixin

from prototype.test_commands import ExampleCommand

from geometry.VQT import V

from utilities.constants import red

# TODO: import the following from somewhere
DX = V(1,0,0)
DY = V(0,1,0)
ORIGIN = V(0,0,0)

from exprs.attr_decl_macros import Instance, State

from exprs.Rect import Line
from exprs.Rect import Spacer

from exprs.If_expr import If_expr
from exprs.ExprsConstants import Point


NullDrawable = Spacer() # kluge; should refile

class test_polyline_drag(State_preMixin, ExampleCommand):
    # class constants needed by mode API for example commands
    commandName = 'test_polyline_drag-commandName'
    featurename = "Prototype: Example Polyline Drag Command"
##    PM_class = test_polyline_drag_PM

    # tracked state
    rubberBand_enabled = State(bool, False, doc = "whether we're rubberbanding a new segment now")
    # TODO:
    ### grab a polyline object from an example file in exprs ### (the one that has a closed boolean and can draw in 3d)
    ### have a list of them, we're rubberbanding last segment of last one...

    lastSegmentStart = ORIGIN + 6 * DY # stub
    lastSegmentEnd = State( Point, doc = "endpoint of last segment; only meaningful when rubberBand_enabled")
        # note: these might be redundant with some points in a polyline object;
        # should they be aliases into one?

    rubberBandDrawable = If_expr( rubberBand_enabled,
                                  Line( lastSegmentStart, lastSegmentEnd,
                                        red,
                                        thickness = 4
                                        ),
                                  NullDrawable
                                  )

    whatWeDraw = Instance(rubberBandDrawable)

    # init methods

    def __init__(self, glpane):
        # not sure why this method is needed, see comment in test_connectWithState.__init__
        super(test_polyline_drag, self).__init__(glpane)
        ExampleCommand.__init__(self, glpane)
        return

    def Draw(self):
        super(test_polyline_drag, self).Draw() #k
        self.whatWeDraw.draw()
        return

    def leftDown(self, event):
        print "leftDown"
        # TODO:
        # get the point (mouseray in plane)
        # make a real point there (or mark it as real, if we have a point object for it already)
        # (so it has a blue dot of its own)
        # update self.rubberBand_enabled
        # STUB:
        self.rubberBand_enabled = True
        self.lastSegmentEnd = self.lastSegmentStart + 3 * DX
        ExampleCommand.leftDown(self, event)
            ### will this prevent this error in mouse release:
            ## AttributeError: 'test_polyline_drag' object has no attribute 'LMB_press_event'
            ##   [GLPane.py:1805] [selectAtomsMode.py:899]
        return

    pass

# end
