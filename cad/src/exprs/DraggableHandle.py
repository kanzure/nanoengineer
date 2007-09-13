# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DraggableHandle.py - some convenience exprs for draggable handles

$Id$

Note about the name: we use DraggableHandle rather than DragHandle,
to avoid confusion with the DragHandler API (which would
otherwise differ by only the final 'r').
"""
__author__ = "bruce"

from constants import white

from exprs.attr_decl_macros import Instance, State, Option
from exprs.If_expr import If_expr 
from exprs.transforms import Translate
from exprs.Center import Center
from exprs.DragBehavior import DragBehavior, SimpleDragBehavior
from exprs.ExprsConstants import StateRef, Color, Width, Vector
from exprs.ExprsConstants import Point, Drawable
from exprs.ExprsConstants import ORIGIN, DY, DX
from exprs.Highlightable import Highlightable
from exprs.Rect import Rect
from exprs.Exprs import tuple_Expr, call_Expr
from exprs.If_expr import If_expr
from exprs.__Symbols__ import _self
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.test_statearray_3 import xxx_drag_behavior_3 ### TODO: refile (DragBehavior.py) and clean up
from exprs.geometry_exprs import Ray

class DraggableHandle_AlongLine(DelegatingInstanceOrExpr): ### TODO: all options might need renaming! replace "height" everywhere.
    """A kind of draggable handle which can be dragged along a line
    to change the value of a single floating point parameter
    (representing position along the line, using a scale and origin
    determined by our arguments).

    ### TODO: add epydoc parameters to this docstring? not sure that will work for a class!
    Maybe we need to synthesize those (from the doc options below) into a fake __init__ method for its sake??
    """
    # == args and options
    
    # options for appearance of handle
    appearance = Option( Drawable,
                         Center(Rect(0.2, 0.2, white)),
                         doc = "our appearance, when not highlighted") ###e take other args of Highlightable?
    appearance_highlighted = Option( Drawable,
                                     appearance,
                                     doc = "our appearance, when highlighted")
    sbar_text = Option(str, "draggable handle", doc = "our statusbar text on mouseover")

    # state variable controlled by dragging
    height_ref = Option(StateRef, doc = "stateref to a height variable") # TODO: rename, redoc

    range = Option(tuple_Expr, None, doc = "range limit of height (tuple)")
        ### MAYBE: RENAME to avoid conflict with python range in this code
        ### TODO: take values from the stateref if this option is not provided

    # line along which to drag it, and how to interpret the state as a position along that line (origin and scale)
    origin = Option( Point, ORIGIN)
    direction = Option( Vector, DX, doc = "vector giving direction and scale")
        # providing a default value is mainly just for testing

    # == internal instances and formulae (modified from test_statearray_3.py)
    
    _drag_handler = Instance( xxx_drag_behavior_3( _self._delegate, height_ref,
                                                  # note: we need call_Expr since Ray is an ordinary class, not an expr! ###FIX
                                                  call_Expr(Ray, origin, direction),
                                                  range = range
                            ))
        ### NOTE: _drag_handler is also being used to compute the translation from the height, even between drags.
    delegate = \
        Highlightable(
            Translate(
                appearance, ### TODO: also use appearance_highlighted
                _drag_handler._translation ###k ok?? only if that thing hangs around even in between drags, i guess!
                    #e #k not sure if this code-commoning is good, but it's tempting. hmm.
             ),
            sbar_text = sbar_text,
            behavior = _drag_handler
         )
    pass # end of class
