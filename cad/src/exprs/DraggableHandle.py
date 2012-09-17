# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
DraggableHandle.py - some convenience exprs for draggable handles

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

Note about the name: we use DraggableHandle rather than DragHandle,
to avoid confusion with the DragHandler API (which would
otherwise differ by only the final 'r').
"""

from utilities.constants import white

from exprs.attr_decl_macros import Instance, Option
from exprs.transforms import Translate
from exprs.Center import Center
from exprs.ExprsConstants import StateRef, Vector
from exprs.attr_decl_macros import State
from exprs.ExprsConstants import Point, Drawable
from exprs.ExprsConstants import ORIGIN, DX ##,DY
from exprs.Highlightable import Highlightable
from exprs.Rect import Rect
from exprs.Exprs import tuple_Expr, call_Expr
from exprs.__Symbols__ import _self
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.DragBehavior_AlongLine import DragBehavior_AlongLine # old todo: clean up
from exprs.geometry_exprs import Ray
from exprs.Set import Action
from exprs.Exprs import call_Expr
from exprs.If_expr import If_expr

class DraggableHandle_AlongLine(DelegatingInstanceOrExpr): ### TODO: all options might need renaming! replace "height" everywhere.
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

    # action options, for Highlightable to do after the ones that come from
    # DragBehavior_AlongLine [new feature of this and Highlightable, 080129]
    on_press = Option(Action)
    on_drag = Option(Action)
    on_release = Option(Action)
    on_release_in = Option(Action, on_release)
    on_release_out = Option(Action, on_release)
    on_doubleclick = Option(Action)

    # line along which to drag it, and how to interpret the state as a position along that line (origin and scale)
    origin = Option( Point, ORIGIN)
    direction = Option( Vector, DX, doc = "vector giving direction and scale")
        # providing a default value is mainly just for testing

    #If this is false, the 'highlightable' object i.e. this handle
    #won't be drawn. The delegate (that defines a Highlightable)
    #We define an If_expr to check whether to draw the highlightable object.
    #[by Ninad]
    # [this should probably be revised, with hasValidParamsForDrawing replaced
    #  with an overridable compute method, for robustness -- current implem
    #  is suspected of causing tracebacks from insufficient update of this
    #  state. Need to review whether methodname needs to be hasValidParamsForDrawing
    #  to conform with any API. -- bruce 080409 comment]
    should_draw = State(bool, True)

    # == internal instances and formulae (modified from test_statearray_3.py)

    _drag_handler = Instance( DragBehavior_AlongLine(
        _self._delegate,
        height_ref,
        call_Expr(Ray, origin, direction),
            # note: we need call_Expr since Ray is an ordinary class, not an expr! ###FIX
        range = range
     ))
    # note: _drag_handler is also being used to compute the translation from the height, even between drags.
    #@see: DnaStrand_ResizeHandle.hasValidParamsForDrawing
    #@see: definition of State attr should_draw
    delegate = \
        If_expr(
            _self.should_draw,
            Highlightable(
                Translate(
                    appearance,
                    _drag_handler._translation #k ok?? only if that thing hangs around even in between drags, i guess!
                        #e #k not sure if this code-commoning is good, but it's tempting. hmm.
                 ),
                highlighted = Translate(
                    appearance_highlighted,
                    _drag_handler._translation
                 ),
                sbar_text = sbar_text,
                behavior = _drag_handler,
                on_press = _self.on_press,
                on_drag = _self.on_drag,
                # (note: no need to pass on_release)
                on_release_in = _self.on_release_in,
                on_release_out = _self.on_release_out,
                on_doubleclick = _self.on_doubleclick
            ) #end of Highlightable
        ) #end of If_expr

    def hasValidParamsForDrawing(self):
        """
        Overridden in subclasses. Default implementation returns True
        if this object (the highlightable) can be drawn without any known
        issues
        @see: DnaStrand_ResizeHandle.hasValidParamsForDrawing for more notes.
        """
        self.should_draw = True
        return self.should_draw

    pass # end of class
