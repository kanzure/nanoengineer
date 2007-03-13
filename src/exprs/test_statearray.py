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
from Set import Set ##e move to basic?


import draggable
reload_once(draggable)
from draggable import DraggableObject

import images
reload_once(images)
from images import Image, IconImage, NativeImage, PixelGrabber

import controls
reload_once(controls)
from controls import ActionButton, PrintAction


def StateArrayRefs_getitem_as_stateref(statearrayrefs, index): #070313 renamed getitem_stateref to StateArrayRefs_getitem_as_stateref
    "#doc; args are values not exprs in the present form, but maybe can also be exprs someday, returning an expr..."
    if 'arg1 is a StateArrayRefs, not a StateArray':
        return statearrayrefs[index] # WARNING:
            # this only works due to a bug in the initial stub implem for StateArray --
            # now declared a feature due to its being renamed to StateArrayRefs -- in which self.attr
            # is valued as a dict of LvalForState objects rather than of settable/gettable item values,
            # and *also* because I changed LvalForState to conform to the new StateRefInterface so it actually
            # has a settable/gettable .value attribute.
            ##### When that bug in StateArray is fixed, this code would be WRONG if applied to a real StateArray.
            # What we need is to ask for an lval or stateref for that StateArray at that index!
            # Can we do that using getitem_Expr (re semantics, reasonableness, and efficiency)? ##k
    else:
        return StateRef_from_lvalue( getitem_Expr(statearrayrefs, index))
            ###IMPLEM this getitem_Expr behavior (proposed, not yet decided for sure; easy, see getattr_Expr for how)
            ###IMPLEM StateRef_from_lvalue if I can think of a decent name for it, and if I really want it around
    pass

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
    indices = range(4)
    colors = StateArrayRefs(Color, red)
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

# == example 2

###UNFINISHED in 3 ways (besides the same kluges as in example 1):
# - stores vectors not heights
# - constrain_delta nim, so they'll be dragged in all directions
# + [works now] delta_stateref nim,
#   so dragging these won't actually affect the elements of the StateArray yet, which pretty much bypasses the point.
#   ... done, works, and printit verifies that the statearray values actually change.
# even so, it runs (testexpr_35a).

class _height_dragger(DelegatingInstanceOrExpr):
    # args
    #e coordsystem? for now let x/y be the way it spreads, z be the height
    height_ref = Arg(StateRef, doc = "stateref to a height variable")
    # appearance/behavior
    #e should draw some "walls" too, and maybe limit the height
    delegate = DraggableObject(
        Image("blueflake.jpg"), ###e needs an option to be visible from both sides (default True, probably)
        constrain_delta = _self.constrain_delta, ###IMPLEM constrain_delta in DraggableObject
        delta_stateref = height_ref ###IMPLEM delta_stateref [done] (and rename it); and change this to make height_ref a number not vector;
            ##e and maybe include the constraint in that transform, since it seems implicit in it anyway. ####HOW in semantics?
            # ... = PropertyRef(DZ * height_ref.value, Set( height_ref.value, project_onto_unit_vector( _something, DZ ))
            # ... = TransformStateRef( height_ref, ... ) # funcs? or formula in terms of 1 or 2 vars? with a chance at solving it?? ##e
     )
    def constrain_delta(self, delta):
        not yet - called
        return project_onto_unit_vector( delta, DZ)
    pass

class test_StateArrayRefs_2(DelegatingInstanceOrExpr):
    indices = range(4)
    heights = StateArrayRefs(Width, ORIGIN) ###KLUGE for now: this contains heights * DZ as Vectors, not just heights
    def _height_dragger_for_index(self, index):
        stateref = StateArrayRefs_getitem_as_stateref( self.heights, index )
        newindex = ('_height_dragger_for_index', index) 
        return self.Instance( _height_dragger( stateref), newindex )
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


class x:
    def drag_ray_from_to(self, oldray, newray): # sort of like _cmd_from_to (sp?) in other eg code
        """[part of an interface XXX related to drag behaviors]
        
        """
        k = self.line.closest_pt_params_to_ray(newray)
        #e store k
        #e compute new point from k
        

# ==
