# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
test_statearray_3.py

Note: contains DragBehavior_AlongLine, which needs refiling
since it may soon be used in real code.

@author: bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

test code for one kind of constrained dragging

used in testexpr_35b thru 35d in exprs/test.py

the DragBehavior in this file improves on the one in test_statearray_2.py:
- uses its own coordsys, not the one in the Highlightable
- computes the translation from the height (for internal and external use)
- has a range limit

But it needs a refactoring; see comments herein about "refactoring".

"""

from exprs.Column import SimpleColumn, SimpleRow

from exprs.Rect import Rect, Line

from exprs.Highlightable import Highlightable, SavedCoordsys

from exprs.images import Image

from exprs.controls import ActionButton ##, PrintAction

from exprs.geometry_exprs import Ray

from exprs.transforms import Translate

from exprs.Overlay import Overlay

from constants import white

from exprs.Exprs import call_Expr, tuple_Expr
from exprs.statearray import StateArrayRefs, StateArrayRefs_getitem_as_stateref
from exprs.iterator_exprs import MapListToExpr, KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.attr_decl_macros import Arg, Option, Instance
from exprs.ExprsConstants import StateRef, ORIGIN, DX, Width, Vector
from exprs.py_utils import sorted_items
from exprs.__Symbols__ import _self, Anything


from exprs.DragBehavior import DragBehavior


# == example 3 

# 070318: now that DraggablyBoxed resizer works, I'll revise example 2 in some related ways,
# including using a saved_coordsys as in SimpleDragBehavior. This new example has the same intent
# as example 2, but cleaner code, and could entirely replace it once it works --
# but now they both work (except for different lbox effects) so for now I'll keep them both around.

class DragBehavior_AlongLine(DragBehavior): #070318 (compare to SimpleDragBehavior) ###e rename to DragBehavior_AlongLine & refile when it works
    """
    a drag behavior which moves the original hitpoint along a line,
    storing only its 1d-position-offset along the line's direction
    [noting that the hitpoint is not necessarily equal to the moved object's origin]
    [#doc better]
    """
    # args [#e replace 'height' with 'posn_parameter' or 'posn_param' in these comments & docstrings]
    highlightable = Arg(Anything) ###e is there a way we can require that we're passed an Instance rather than making it ourselves?
        # I suspect that violating that caused the bug in example 2.
        # (A way that would work: a specialcase check in _init_instance.
        #  But I'd rather have an option on Arg to do that. require_already_instance?? Or ArgInstance? that latter invites confusion
        #  since it's not analogous to ArgExpr.)
    posn_parameter_ref = Arg(StateRef, doc = "where the variable height is stored")
    constrain_to_line = Arg(Ray, doc = "the line/ray on which the height is interpreted as a position")
        ###e rename: constraint_line? line_to_constrain_to? constrain_to_this_line?
        # note: the position of the height on this line is typically used as the position of the drawn movable object's origin;
        # we shouldn't assume the drag startpoint is on the line, since the drawn movable object might be touched at any of its points.
        ##e rename Ray -> MarkedLine? (a line, with real number markings on it) ParametricLine? (no, suggests they can be distorted/curved)
    range = Option(tuple_Expr, None, doc = "range limit of height")#nim
    ##e drag event object can be passed to us... as a delegate! [In recent code, it seems like the Highlightable is taking this role.]
        
    # (if this delegates or supers to something that knows all about the drag in a lower level way,
    #  then maybe it's not so bad to be getting dragevent info from self rather than a dragevent arg... hmm.
    #  An argument in favor of that: self is storing state related to one drag anyway, so nothing is lost
    #  by assuming some other level of self stores some other level of that state. So maybe we create a standard
    #  DragHandling object, then create a behavior-specific delegate to it, to which *it* delegates on_press etc;
    #  and we also get it to delegate state-modifying calls to some external object -- or maybe that's not needed
    #  if things like this one's stateref are enough. ##k)
    #
    # related: Maybe DraggableObject gets split into the MovableObject and the DragBehavior...

    # same as in SimpleDragBehavior: saved_coordsys & current_event_mousepoint
    
    # state:
    saved_coordsys = Instance( SavedCoordsys() ) # provides transient state for saving a fixed coordsys to use throughout a drag

    # helper methods (these probably belong in a superclass):
    def current_event_mousepoint(self, *args, **kws): #e zap this and inline it, for clarity? or move it into DragBehavior superclass??
        return self.saved_coordsys.current_event_mousepoint(*args, **kws)

    def current_event_mouseray(self):
        p0 = self.current_event_mousepoint(depth = 0.0) # nearest depth ###k
        p1 = self.current_event_mousepoint(depth = 1.0) # farthest depth ###k
        return Ray(p0, p1 - p0) #e passing just p1 should be ok too, but both forms can't work unless p0,p1 are typed objects...

    # specific methods
    def _C__translation(self): ### WARNING: used externally too -- rename to be not private if we decide that's ok ###e
        """
        compute self._translation from the externally stored height
        """
        k = self.posn_parameter_ref.value
        return self.constrain_to_line.posn_from_params(k) #e review renaming, since we are asking it for a 3-tuple
    
    def on_press(self):
        self.saved_coordsys.copy_from( self.highlightable) # needed before using current_event_mousepoint or current_event_mouseray
            # (since self.highlightable's coordsys changes during the drag)
        self.startpoint = self.current_event_mousepoint() # the touched point on the visible object (hitpoint)
        self.offset = self.startpoint - (ORIGIN + self._translation) #k maybe ok for now, but check whether sensible in long run
        self.line = self.constrain_to_line + self.offset # the line the hitpoint is on (and constrained to, if handle is rigid)
            # (this is parallel to self.constrain_to_line and intersects the hitpoint) 
    def on_drag(self):
        # Note: we can assume this is a "real drag" (not one which is too short to count), due to how we are called.
        mouseray = self.current_event_mouseray()
        k = self.line.closest_pt_params_to_ray(mouseray)
            #
            # BUG: for lines with a lot of Z direction, in perspective view,
            # this is wrong -- we want the closest point on the screen,
            # not in space. The current code (closest point in space)
            # would tend to come up with a point too near the screen,
            # if the constraint line and the mouseray are diverging away
            # from each other (in model space) with depth.
            #
            # TODO: fix this. Possible fixes include:
            # - common code, using a projection matrix & its inverse (seems hard)
            # - separate code for Ortho vs Perspective case (needs eyepoint)
            #   (might be clearest & simplest; it might turn out we'd want other
            #    behavior tweaks which differed in these cases -- for example,
            #    stop dragging and turn the handle red when it gets so far away
            #    in model space (near the "point at infinity" visible on the screen
            #    for an infinite line -- aka the "point of convergence" for a family
            #    of parallel lines) that its motion would be too sensitive, since
            #    the constraint line is too close to perpendicular to the screen)
            # - save the initial mouseray too, since it gives us enough info
            #   (along with current one) to know the entire projection
            #   (except when they coincide, in which case no motion is needed).
            #   Alg for this is not yet worked out. Q: is an ortho projection
            #   along initial mouseray a good approximation? Probably not,
            #   if we approach the "point at infinity".
            #
            # Also we need a refactoring, so that one external object can store
            # both the geometric info about the constraint, and the state of the
            # dragpoint along it, accessible as parameter-along-line or point or both,
            # with either being the underlying state. (Unless nothing less than a
            # DragBehavior can actually do all those things, in which case,
            # we need variants depending on whether the point or the parameter
            # is the underlying state. But more likely, we want a DragState which
            # knows how to make the underlying state convenient, and a DragBehavior
            # which knows how to connect that to mouse gestures, so these can vary
            # separately.)
            #
            # [bruce 070913 comment]
            #
        if k is not None:
            # store k, after range-limiting
            range = self.range # don't use the python builtin of the same name, in this method! (#e or rename the option?)
            if range is not None:
                low, high = range
                if low is not None and k < low:
                    k = low
                if high is not None and k > high:
                    k = high
            self.posn_parameter_ref.value = k ##e by analogy with DraggableObject, should we perhaps save this side effect until the end?
        return
    def on_release(self):
        pass
    pass # end of class DragBehavior_AlongLine

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
                Image("blueflake.jpg"), ###e needs an option to be visible from both sides (default True, probably)
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
