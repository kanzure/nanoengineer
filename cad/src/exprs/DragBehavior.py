# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
DragBehavior.py - the DragBehavior API and some useful specific behaviors

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

A DragBehavior

is a behavior in response to drag events

that a Drawable (called a "drag handle") can be given
(in addition to whatever highlighting and cursor behavior it has)

and that determines how drag events affect a position or position-determining state

(one which maps to a position, perhaps constrained to a line or plane, and/or a region, and/or quantized)

which this behavior is used to drag, and which usually (in part)
determines the drawn position of the drag handle.
"""

from exprs.instance_helpers import InstanceOrExpr
from exprs.attr_decl_macros import Arg, Instance
from exprs.__Symbols__ import Anything
from exprs.ExprsConstants import StateRef
from exprs.Highlightable import SavedCoordsys


class DragBehavior(InstanceOrExpr):
    """
    abstract class
    [#doc, maybe more defaults]
    """
    # default implems
    def on_press(self):
        pass
    def on_drag(self):
        pass
    def on_release(self):
        pass
    def on_release_in(self):
        self.on_release()
        return
    def on_release_out(self):
        self.on_release()
        return
    pass

# ==

class SimpleDragBehavior(DragBehavior): #works circa 070317; revised 070318
    """
    the simplest kind of DragBehavior -- translate the passed state
    just like the mouse moves (screen-parallel)
    [#doc]
    """
    ##e rename to indicate what it does -- translate, 3d, screen-parallel
    # (no limits, no grid, no constraint -- could add opts for those #e)

    # note: for now, it probably doesn't matter if we are remade per drag event, or live through many of them --
    # we store state during a drag (and left over afterwards) but reset it all when the next one starts --
    # ASSUMING we actually get an on_press event for it -- we don't detect the error of not getting that!
    # OTOH, even if we're newly made per drag, we don't detect or tolerate a missing initial on_press. ###BUG I guess

    # args:
    # a stateref to the translation state we should modify,
    # and something to ask about the drag event (for now, highlightable, but later, a DragEvent object)
    # (best arg order unclear; it may turn out that the DragEvent to ask is our delegate in the future -- so let it come first)

    highlightable = Arg(Anything)
        # for current_event_mousepoint (coordsys) -- will this always be needed? at least a DragEvent will be!
    translation_ref = Arg(StateRef,
                          doc = "ref to translation state, e.g. call_Expr( LvalueFromObjAndAttr, some_obj, 'translation')" )

    # state:
    saved_coordsys = Instance( SavedCoordsys() ) # provides transient state for saving a fixed coordsys to use throughout a drag

    def current_event_mousepoint(self, *args, **kws): #e zap this and inline it, for clarity? or move it into DragBehavior superclass??
        return self.saved_coordsys.current_event_mousepoint(*args, **kws)

    # note: the following methods are heavily modified from the ones in DraggableObject.
    # [They are the methods of some interface, informal so far,
    #  but I don't know if it's exactly the one I've elsewhere called Draggable.]

    def on_press(self):
        self.saved_coordsys.copy_from( self.highlightable) # needed, since self.highlightable's coordsys changes during the drag!
        point = self.current_event_mousepoint() # the touched point on the visible object (hitpoint)
        self.oldpoint = self.startpoint = point

    def on_drag(self):
        # Note (for any on_drag method -- really about the interface it's in [###e refile]):
        # we can assume this is a "real drag",
        # not one which is too short to count (and is therefore treated as a click instead),
        # since the caller is responsible for not calling on_drag until it decides this is a real drag.
        oldpoint = self.oldpoint # was saved by prior on_drag or by on_press
        point = self.current_event_mousepoint(plane = self.startpoint)
        self.translation_ref.value = self.translation_ref.value + (point - oldpoint)
        self.oldpoint = point

    def on_release(self):
        pass

    pass # end of class SimpleDragBehavior

# end
