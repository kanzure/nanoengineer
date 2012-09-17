# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
test_statearray_3.py

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

test code for one kind of constrained dragging

used in testexpr_35b thru 35d in exprs/test.py

the DragBehavior in this file [now in its own file, DragBehavior_AlongLine]
improves on the one in test_statearray_2.py:
- uses its own coordsys, not the one in the Highlightable
- computes the translation from the height (for internal and external use)
- has a range limit

But it needs a refactoring; see comments herein about "refactoring".

"""

from exprs.Column import SimpleColumn, SimpleRow

from exprs.Rect import Rect, Line

from exprs.Highlightable import Highlightable

from exprs.images import Image

from exprs.controls import ActionButton ##, PrintAction

from exprs.geometry_exprs import Ray

from exprs.transforms import Translate

from exprs.Overlay import Overlay

from utilities.constants import white

from exprs.Exprs import call_Expr, tuple_Expr
from exprs.statearray import StateArrayRefs, StateArrayRefs_getitem_as_stateref
from exprs.iterator_exprs import MapListToExpr, KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.attr_decl_macros import Arg, Option, Instance
from exprs.ExprsConstants import StateRef, ORIGIN, DX, Width, Vector
from exprs.py_utils import sorted_items
from exprs.__Symbols__ import _self

from exprs.DragBehavior_AlongLine import DragBehavior_AlongLine

# == example 3

# 070318: now that DraggablyBoxed resizer works, I'll revise example 2 in some related ways,
# including using a saved_coordsys as in SimpleDragBehavior. This new example has the same intent
# as example 2, but cleaner code, and could entirely replace it once it works --
# but now they both work (except for different lbox effects) so for now I'll keep them both around.
# [note, that comment is partly about DragBehavior_AlongLine, now in its own file]

class _height_dragger_3(DelegatingInstanceOrExpr):
    # args
    height_ref = Arg(StateRef, doc = "stateref to a height variable")
    direction = Arg(Vector)
    sbar_text = Option(str, "_height_dragger_3")
    range = Option(tuple_Expr, None, doc = "range limit of height")
    # appearance/behavior
    #e should draw some "walls" too, and maybe limit the height
    drag_handler = Instance( DragBehavior_AlongLine(
        _self._delegate,
        height_ref,
        ## Ray(ORIGIN, DX) # works
        ## Ray(ORIGIN, DZ) # works, but only if you trackball it (as expected)...
        ## Ray(ORIGIN, direction) # fails -- Ray is an ordinary class, not an expr! ###FIX
        call_Expr(Ray, ORIGIN, direction), # this workaround fixes it for now.
            # (in prior commit it didn't fix it, but only because of a typo in the testexpr defs
            #  in tests.py, which meant I passed DZ when I thought I passed DX.)
        range = range
     ))
        ### NOTE: drag_handler is also being used to compute the translation from the height, even between drags.
    delegate = Overlay(
        Highlightable(
            Translate(
                Image("blueflake.png"), ###e needs an option to be visible from both sides (default True, probably)
                drag_handler._translation ###k ok?? only if that thing hangs around even in between drags, i guess!
                    #e #k not sure if this code-commoning is good, but it's tempting. hmm.
             ),
            sbar_text = sbar_text,
            behavior = drag_handler
         ),
        Translate(Rect(2), direction * -0.01),
        Line(ORIGIN, ORIGIN + direction * height_ref.value, white)
     )
    pass

class test_StateArrayRefs_3( DelegatingInstanceOrExpr): # testexpr_35b, _35c
    indices = range(3)
    heights = StateArrayRefs(Width, 0.0)
    direction = Arg(Vector, DX, "direction of permitted motion -- DZ is the goal but DX is easier for testing")
        ### DX for initial test (testexpr_35b), then DZ (testexpr_35c)
    range = Option(tuple_Expr, None, doc = "range limit of height")
    msg = Option(str, "drag along a line")
    def _height_dragger_for_index(self, index):
        stateref = StateArrayRefs_getitem_as_stateref( self.heights, index )
            #e change to self.heights.getitem_as_stateref(index)? self.heights._staterefs[index]?? self.heights[index]???
        newindex = ('_height_dragger_3_for_index', index)
        return self.Instance( _height_dragger_3( stateref, self.direction,
                                                 sbar_text = "%s (#%r)" % (self.msg, index,),
                                                 range = self.range
                                                ), newindex )
    delegate = SimpleRow(
        MapListToExpr( _self._height_dragger_for_index, ###k _self needed??
                       indices,
                       KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleColumn) ),
                           #e SimpleGrid? 2d form of MapListToExpr?
        ActionButton( _self.printit, "button: print state") ###e idea: define on special attr, let UI assemble debug info viewer
     )
    def printit(self): #e can PrintAction do this for us?
        print [h.value for i,h in sorted_items(self.heights)] ###KLUGE, assumes they're StateRefs -- maybe just rename StateArray -> StateArrayRefs
    pass

# end
