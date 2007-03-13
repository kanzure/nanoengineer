"""
test_statearray.py

$Id$
"""

from basic import *
from basic import _self

import Column
reload_once(Column)
from Column import SimpleColumn, SimpleRow

import Rect
reload_once(Rect)
from Rect import Rect

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable

StateRef = StubType #k

import Boxed
reload_once(Boxed)
from Boxed import Boxed

import Set
reload_once(Set)
from Set import Set ##e move to basic


class _color_toggle(DelegatingInstanceOrExpr): ###UNTESTED
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
    pass

class test_StateArray(DelegatingInstanceOrExpr): ###UNTESTED, and has some WRONGnesses
    indices = range(4)
    colors = StateArray(Color, red)
        #e i want an arg for the index set... maybe even the initial set, or total set, so i can iter over it...
        # NOTE: at least one dictlike class has that feature - review the ones in py_utils, see what _CK_ uses
    # how to turn an index into 
    func = lambda index: colors.lvals[index]
    def _color_toggle_for_index(self, index):#e should we use _CV_ for this?? if not, it must be too hard to use!!!
            #k or is it that it defines a dict rather than a func, but we need a func in MapListToExpr?
        color_stateref = self.colors[index]
            #####KLUGE: this only works due to a bug in the initial stub implem for StateArray, in which self.attr
            # is valued as a dict of LvalForState objects rather than of settable/gettable item values,
            # and *also* because I changed LvalForState to conform to the new StateRefInterface so it actually
            # has a settable/gettable .value attribute.
            ##### When that bug in StateArray is fixed, this code will be WRONG.
            # What we need is to ask for an lval or stateref for that StateArray at that index!
            # Can we do that using getitem_Expr (re semantics, reasonableness, and efficiency)? ##k
        return self.Instance( _color_toggle( color_stateref),
                              ('_color_toggle_for_index', index) ) 
    delegate = MapListToExpr( _self._color_toggle_for_index, ###k _self needed??
                              indices,
                              KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleRow) )
    pass
