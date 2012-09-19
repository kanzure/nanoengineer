# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from utilities.constants import white

from exprs.attr_decl_macros import Instance, Option
from exprs.transforms import Translate
from exprs.Center import Center
from exprs.ExprsConstants import StateRef, Vector
from exprs.ExprsConstants import Point, Drawable
from exprs.ExprsConstants import ORIGIN, DX ##,DY
from exprs.Highlightable import Highlightable
from exprs.Rect import Rect
from exprs.Exprs import tuple_Expr
from exprs.__Symbols__ import _self
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.DragBehavior_AlongCircle import DragBehavior_AlongCircle
from exprs.Set import Action

class DraggableHandle_AlongCircle(DelegatingInstanceOrExpr):
    """
    A kind of draggable handle which can be dragged along a line
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
                         doc = "appearance, when not highlighted")

    appearance_highlighted = Option( Drawable,
                                     appearance,
                                     doc = "appearance, when highlighted")

    sbar_text = Option(str,
                       "draggable handle along circle",
                       doc = "statusbar text on mouseover")

    # state variable controlled by dragging
    rotationDistanceRef = Option(StateRef,
                                doc = "stateref to a dragged disctance variable")


    # action options, for Highlightable to do after the ones that come from
    # DragBehavior_AlongLine [new feature of this and Highlightable, 080129]
    on_press = Option(Action)
    on_drag = Option(Action)
    on_release = Option(Action)
    on_release_in = Option(Action, on_release)
    on_release_out = Option(Action, on_release)
    on_doubleclick = Option(Action)

    #origin of the handle itself
    origin = Option( Point, ORIGIN)

    # Center of the circle whose perimeter serves as a path along which to
    # drag
    center = Option( Point, ORIGIN)

    #Axis of the circle.
    axis  = Option( Vector, DX, doc = "vector giving direction and scale")

    #radius Vector
    radiusVector = Option( Vector,
                           DX,
                           doc = "vector giving direction and scale")

    #angle range for the rotation
    range_for_rotation = Option(tuple_Expr,
                                None,
                                doc = "range limit of angle (tuple)")


    # == internal instances and formulae (modified from test_statearray_3.py)

    _drag_handler = Instance(
        DragBehavior_AlongCircle(
            _self._delegate,
            rotationDistanceRef,
            origin,
            center,
            axis,
            radiusVector,
            range_for_rotation = range_for_rotation))


    #QUESTION: Should the 'RotateTranslate' transform from exprs.transforms be
    #used here? -- Ninad 2008-02-13
    delegate = \
        Highlightable(
            Translate(
                appearance,
                _drag_handler._rotation #k ok?? only if that thing hangs around even in between drags, i guess!
                    #e #k not sure if this code-commoning is good, but it's tempting. hmm.
             ),
            highlighted = Translate(
                appearance_highlighted,
                _drag_handler._rotation
             ),
            sbar_text = sbar_text,
            behavior = _drag_handler,
            on_press = _self.on_press,
            on_drag = _self.on_drag,
            # (note: no need to pass on_release)
            on_release_in = _self.on_release_in,
            on_release_out = _self.on_release_out,
            on_doubleclick = _self.on_doubleclick,
         )


    pass # end of class
