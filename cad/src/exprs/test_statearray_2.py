# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
test_statearray_2.py

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

test code for one kind of constrained dragging

used in testexpr_35a in exprs/test.py

DEPRECATED -- replaced by test_statearray_3.py

"""

# maybe some of these imports are not needed

from exprs.Column import SimpleColumn, SimpleRow

from exprs.draggable import DraggableObject

from exprs.images import Image

from exprs.controls import ActionButton ##, PrintAction

from exprs.geometry_exprs import Ray

from exprs.statearray import StateArrayRefs, StateArrayRefs_getitem_as_stateref
from exprs.iterator_exprs import MapListToExpr, KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.attr_decl_macros import Arg, Instance
from exprs.ExprsConstants import StateRef, ORIGIN, DY, DX, Width
from exprs.py_utils import sorted_items
from exprs.__Symbols__ import _self


from exprs.DragBehavior import DragBehavior


# == example 2 -- full of kluges, but may finally work now; abandoned 070318 in favor of example 3

# maybe-partly-obs cmt:
###UNFINISHED in 3 ways (besides the same kluges as in example 1):
# - stores vectors not heights
# - constrain_delta nim, so they'll be dragged in all directions
# + [works now] delta_stateref nim,
#   so dragging these won't actually affect the elements of the StateArray yet, which pretty much bypasses the point.
#   ... done, works, and printit verifies that the statearray values actually change.
# even so, it runs (testexpr_35a).

# UNFINISHED aspects of xxx_drag_behavior:
# - its name
# + implem posn_from_params [done now]
# - the logic bug about self.motion -- ignoring for initial kluge test
# + closest_pt_params_to_ray [coded now]
# - how it fits into anything else -- not using DraggableObject is going to be best in the end,
#   but as initial kluge, just pass it in (wrapping DO as a delegator), and it might work.
# Now [cvs rev 1.15 & 1.16, sometime before 070318] it is supposedly coded enough to work using initial kluge test, but it doesn't work,
# but is making 2 highlightables and showing one and trying to drag the other (and failing). No idea why. [fixed now, see below]
# evidence is "saved modelview_matrix is None, not using it" and the reprs in that debug print and in the cmenu. Hmm. #BUG
# [note, an earlier version (not preserved except in earlier cvs revs of these same classes)
#  did partly work, which stored vectors and had no working constraint on the dragging.]
# Now I fixed that bug by passing _delegate not delegate to drag_handler; see code comment.

class xxx_drag_behavior(DragBehavior): # revised 070316; on 070318 removed comments that were copied into version _3
    """a drag behavior which moves the original hitpoint along a line,
    storing only its 1d-position-offset along the line's direction
    [noting that the hitpoint is not necessarily equal to the moved object's origin]
    [#doc better]
    """
    # args
    highlightable = Arg(DraggableObject) # kluge; revised 070316, delegate -> highlightable [works no worse than before [same bug as before]]
        # [but it's misnamed -- it has to be a DraggableObject since we modify its .motion]
        ###e rename, but what is it for?
    posn_parameter_ref = Arg(StateRef, doc = "where the variable height is stored")
        ###e rename
    constrain_to_line = Arg(Ray, Ray(ORIGIN, DY), doc = "the line/ray on which the height is interpreted as a position")
        ###e rename: constraint_line? line_to_constrain_to? constrain_to_this_line?
        # dflt_expr is just for testing #e remove it

    def current_event_mouseray(self):
        p0 = self.highlightable.current_event_mousepoint(depth = 0.0) # nearest depth ###k
        p1 = self.highlightable.current_event_mousepoint(depth = 1.0) # farthest depth ###k
        return Ray(p0, p1 - p0) #e passing just p1 should be ok too, but both forms can't work unless p0,p1 are typed objects...
    def on_press(self):
        self.startpoint = self.highlightable.current_event_mousepoint() # the touched point on the visible object (hitpoint)
        self.offset = self.startpoint - (ORIGIN + self.highlightable.motion) #k maybe ok for now, but check whether sensible in long run
        self.line = self.constrain_to_line + self.offset # the line the hitpoint is on (assuming self.motion already obeyed the constraint)
    def on_drag(self):
        # Note: we can assume this is a "real drag" (not one which is too short to count), due to how we are called.
        mouseray = self.current_event_mouseray()
##        self._cmd_drag_from_to( oldpoint, point) # use Draggable interface cmd on self
            # ie self.delta_stateref.value = self.delta_stateref.value + (p2 - p1)
        ## def drag_mouseray_from_to(self, oldray, newray): # sort of like _cmd_from_to (sp?) in other eg code
        ## "[part of an interface XXX related to drag behaviors]"
        k = self.line.closest_pt_params_to_ray(mouseray)
        if k is not None:
            # store k
            self.posn_parameter_ref.value = k ####e by analogy with DraggableObject, should we perhaps save this side effect until the end?
            # compute new posn from k
            self.highlightable.motion = self.constrain_to_line.posn_from_params(k) #e review renaming, since we are asking it for a 3-tuple
                ####### LOGIC BUG: what causes self.motion to initially come from this formula, not from our own state?
                # maybe don't use DraggableObject at all? [or as initial kluge, just let initial motion and initial height both be 0]
        return
    def on_release(self):
        pass
    pass # end of class xxx_drag_behavior

class _height_dragger(DelegatingInstanceOrExpr):
    # args
    #e coordsystem? for now let x/y be the way it spreads, z be the height
    height_ref = Arg(StateRef, doc = "stateref to a height variable")
    # appearance/behavior
    #e should draw some "walls" too, and maybe limit the height
    # note: the following sets up a cyclic inter-Instance ref ( drag_handler -> delegate -> drag_handler);
    # it works since the actual refs are symbolic (getattr_Expr(_self, 'attr'), not evalled except when used).
    drag_handler = Instance( xxx_drag_behavior( _self._delegate, height_ref, Ray(ORIGIN, DX) )) ### DX for initial test, then DZ
        # note: passing _self._delegate (not _self.delegate) fixed my "undiagnosed bug".
    delegate = DraggableObject(
        Image("blueflake.png"), ###e needs an option to be visible from both sides (default True, probably)
##        constrain_delta = _self.constrain_delta, ###IMPLEM constrain_delta in DraggableObject
##        delta_stateref = height_ref ###IMPLEM delta_stateref [done] (and rename it); and change this to make height_ref a number not vector;
            ##e and maybe include the constraint in that transform, since it seems implicit in it anyway. ####HOW in semantics?
            # ... = PropertyRef(DZ * height_ref.value, Set( height_ref.value, project_onto_unit_vector( _something, DZ ))
            # ... = TransformStateRef( height_ref, ... ) # funcs? or formula in terms of 1 or 2 vars? with a chance at solving it?? ##e
        _kluge_drag_handler = drag_handler
     )
##    def constrain_delta(self, delta):
##        not yet - called
##        return project_onto_unit_vector( delta, DZ)
    pass

class test_StateArrayRefs_2(DelegatingInstanceOrExpr): # testexpr_35a
    indices = range(4)
    ## heights = StateArrayRefs(Width, ORIGIN) ###KLUGE for now: this contains heights * DZ as Vectors, not just heights
    heights = StateArrayRefs(Width, 0.0)
    def _height_dragger_for_index(self, index):
        stateref = StateArrayRefs_getitem_as_stateref( self.heights, index )
            #e change to self.heights.getitem_as_stateref(index)? self.heights._staterefs[index]?? self.heights[index]???
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

# end
