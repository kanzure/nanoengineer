# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
exprs.Arrow.py
@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-03-02: Created
"""
from exprs.widget2d import Widget2D
from exprs.attr_decl_macros import ArgOrOption
from exprs.attr_decl_macros import Option
from exprs.ExprsConstants import Color, Position, ORIGIN, DX

from utilities.constants import gray

from exprs.__Symbols__ import Anything

from graphics.drawing.CS_draw_primitives import drawDirectionArrow

class Arrow(Widget2D):
    """
    Arrow class provides a 3D arrow with a 'tail' and an arrow head.
    @see: B{DnaSegment_ResizeHandle} where this is used to draw a resize handle
          while editing a DnaSegment.
    @see: exprs.Rect.py which defines some other 3 D objects.
    @see: DirectionArrow.py -- Don't confuse it with this class.
    """
    color = ArgOrOption(Color, gray)
    tailPoint = ArgOrOption(Position, ORIGIN)
    arrowBasePoint = ArgOrOption(Position, ORIGIN + 2*DX)
    scale = ArgOrOption(float, 10.0)
    tailRadius = ArgOrOption(float, 0.4)
    #tailRadiusLimits ensure a min and max size for the arrow (including arrow
    #tail and arrow head. drawDirectionArrow method uses tailRadius as a reference
    #to derive other params such as arrowhead base radius etc. Thats why this arg
    #is named this way.
    #@See DnaSegment_ResizeHandle to see how these limits are defined.
    tailRadiusLimits = ArgOrOption(tuple, ())
    glpane = ArgOrOption(Anything, None)
    scale_to_glpane = Option(bool, False)

    def draw(self):
        drawDirectionArrow(
            self.color,
            self.tailPoint,
            self.arrowBasePoint,
            self.tailRadius,
            self.scale,
            tailRadiusLimits = self.tailRadiusLimits,
            numberOfSides = 6,
            glpane = self.glpane,
            scale_to_glpane = self.scale_to_glpane
        )


