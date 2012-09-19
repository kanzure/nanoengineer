# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
test_statearray.py

@author: bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

"""

from exprs.Column import SimpleRow

from exprs.Rect import Rect

from exprs.Highlightable import Highlightable

from exprs.Boxed import Boxed

from exprs.Set import Set

from utilities.constants import black, pink

from exprs.Exprs import call_Expr
from exprs.statearray import StateArrayRefs, StateArrayRefs_getitem_as_stateref
from exprs.iterator_exprs import MapListToExpr, KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.attr_decl_macros import Arg
from exprs.ExprsConstants import StateRef, Color

from exprs.__Symbols__ import _self

# == example 1

class _color_toggler(DelegatingInstanceOrExpr):
    ###WRONGnesses:
    # - Q: shouldn't we be toggling a flag or enum or int, and separately mapping that to a color to show?
    #   A: Yes, unless we're for general raw color images -- but as a StateArray test this doesn't matter.
    # args
    color_ref = Arg(StateRef, doc = "stateref to a color variable") ###e can we tell StateRef what the value type should be?
    # appearance/behavior
    delegate = Boxed(
        Highlightable(
            Rect(1, 1, color_ref.value),
            on_press = Set( color_ref.value, call_Expr( _self.toggle_color, color_ref.value) ),
            sbar_text = "click to change color" #e give index in StateArray, let that be an arg? (if so, is it a fancy stateref option?)
         ),
        pixelgap = 0, #e rename -- but to what? bordergap? just gap? (change all gap options to being in pixels?)
        borderwidth = 1, ###BUG: some of these border edges are 2 pixels, depending on pixel alignment with actual screen
        bordercolor = black
     )
    def toggle_color(self, color):
        r,g,b = color
        return (b,r,g) # this permits toggling through the cyclic color sequence red, green, blue in that order
            #e or we could rotate that color-cube on the same diagonal axis but less than 1/3 turn,
            # to get more colors, if we didn't mind renormalizing them etc...
    pass

class test_StateArrayRefs(DelegatingInstanceOrExpr): ### has some WRONGnesses
    indices = range(10)
    colors = StateArrayRefs(Color, pink)
        #e i want an arg for the index set... maybe even the initial set, or total set, so i can iter over it...
        # NOTE: at least one dictlike class has that feature - review the ones in py_utils, see what _CK_ uses
    def _color_toggler_for_index(self, index):#e should we use _CV_ for this?? if not, it must be too hard to use!!!
            #k or is it that it defines a dict rather than a func, but we need a func in MapListToExpr?
        stateref = StateArrayRefs_getitem_as_stateref( self.colors, index )
        newindex = ('_color_toggler_for_index', index)
        return self.Instance( _color_toggler( stateref), newindex )
    delegate = MapListToExpr( _self._color_toggler_for_index, ###k _self needed??
                              indices,
                              KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleRow) )
    pass

# end
