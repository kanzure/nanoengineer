# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
@version: $Id$

TODO: as of 2008-02-12

This is a non-working DragBehavior_AlongCircle class , not called anywhere.
"""
from exprs.Highlightable import SavedCoordsys
from exprs.geometry_exprs import Ray
from exprs.Exprs import tuple_Expr
from exprs.attr_decl_macros import Arg, Option, Instance
from exprs.ExprsConstants import StateRef ##, ORIGIN
from exprs.__Symbols__ import Anything
from exprs.DragBehavior import DragBehavior


class DragBehavior_AlongCircle(DragBehavior):
    """
    A drag behavior which moves the original hitpoint along a line,
    storing only its 1d-position-offset along the line's direction
    [noting that the hitpoint is not necessarily equal to the moved object's origin]
    [#doc better]
    """

    highlightable = Arg(Anything)

    rotation_parameter_ref = Arg(StateRef,
                             doc = "where anything proportional to angle is stored")

    #translation_parameter_ref = Arg(StateRef,
                             #doc = "where translation is stored")
    origin = Arg(StateRef, doc = "handle base point")

    center = Arg(StateRef, doc = "center of the circle")

    axis = Arg(StateRef, doc = "circle axis")

    radiusVector = Arg(StateRef,
                       doc = "radius of circle")


    locked_parameter = Option(tuple_Expr,
                                 None,
                                 doc = "locked parameter")

    range_for_rotation =  Option(tuple_Expr,
                                 None,
                                 doc = "range limit of angle of rotation")

    range_for_translation = Option(tuple_Expr,
                                   None,
                                   doc = "range limit of translation")

    # provides transient state for saving a fixed coordsys to use throughout
    #a drag
    saved_coordsys = Instance( SavedCoordsys() )

    # helper methods (these probably belong in a superclass):
    def current_event_mousepoint(self, *args, **kws):
        return self.saved_coordsys.current_event_mousepoint(*args, **kws)

    def current_event_mouseray(self):
        p0 = self.current_event_mousepoint(depth = 0.0) # nearest depth ###k
        p1 = self.current_event_mousepoint(depth = 1.0) # farthest depth ###k
        return Ray(p0, p1 - p0)

    # specific methods
    def _C__rotation(self):
        """
        Compute self._rotation from the externally stored rotation paramater
        """
        k = self.rotation_parameter_ref.value

        ##rotation = k*self.radiusVector

        #REVISE THIS
        from geometry.VQT import norm
        return  self.origin#self.radiusVector + k*norm(self.radiusVector)

    def on_press(self):
        self.saved_coordsys.copy_from( self.highlightable)
        self.startpoint = self.current_event_mousepoint()
        #Formula needs to be revised.
        ##self.offset = self.startpoint - (ORIGIN + self._rotation)
        ##self.circularPath = self.constrain_to_circle + self.offset

    def on_drag(self):
        mouseray = self.current_event_mouseray()
        ##k = self.circularPath.closest_pt_params_to_ray(mouseray)
        k = None
        if k is not None:
            # store k, after range-limiting

            if self.range_for_rotation is not None:
                low, high = self.range_for_rotation
                if low is not None and k < low:
                    k = low
                if high is not None and k > high:
                    k = high
            self.rotation_parameter_ref.value = k
            ##e by analogy with DraggableObject, should we perhaps save this
            ##side effect until the end?
        return

    def on_release(self):
        pass

