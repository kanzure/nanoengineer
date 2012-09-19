# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
DragBehavior_AlongLine.py

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.


the DragBehavior in this file improves on the one in test_statearray_2.py:
- uses its own coordsys, not the one in the Highlightable
- computes the translation from the height (for internal and external use)
- has a range limit

TODO:

needs a refactoring; see comments herein about "refactoring"

[following comment came from DragBehavior.py, guessing it was about this class:]
maybe revise how it works for off-line points -- not closest in space
but closest within a plane perp to screen and -- what? ###
"""
from exprs.Highlightable import SavedCoordsys
from exprs.geometry_exprs import Ray
from exprs.Exprs import tuple_Expr
from exprs.attr_decl_macros import Arg, Option, Instance
from exprs.ExprsConstants import StateRef, ORIGIN
from exprs.__Symbols__ import Anything
from exprs.DragBehavior import DragBehavior


class DragBehavior_AlongLine(DragBehavior): #070318 (compare to SimpleDragBehavior)
    """
    A drag behavior which moves the original hitpoint along a line,
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
            range = self.range # don't use the python builtin of the same name,
                               #in this method! (#e or rename the option?)
            if range is not None:
                low, high = range
                if low is not None and k < low:
                    k = low
                if high is not None and k > high:
                    k = high
            self.posn_parameter_ref.value = k
            ##e by analogy with DraggableObject, should we perhaps save this
            ##side effect until the end?
        return
    def on_release(self):
        pass
    pass # end of class DragBehavior_AlongLine

# end
