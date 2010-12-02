# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DragHandler.py -- API (and default method implems) for an interface
from selectMode to hover-highlighted objects that know how they want
to handle their own click/drag/release mouse events (unlike Atom,
Bond, and Jig, whose behavior is hardcoded into selectMode).

$Id$
"""

__author__ = "bruce"

class DragHandler_API: #bruce 070602 moved this from exprs/Highlightable.py to DragHandler.py, and renamed it
    """Document the drag_handler interface (implemented by selectMode and its subclasses),
    and provide default implems for its methods. [### need an overview and more details here]
    WARNING: API details (method names, arglists) are subject to change.
    """
    # example subclasses: class Highlightable in exprs.Highlightable; some in cad/src
    # Q: how does this relate to the selobj interface?
    # (Note: the "selobj interface" is an informal interface implemented by GLPane.py
    #  for hover-highlightable objects. It has some documentation in exprs/Highlightable.py and GLPane.py.)
    # A: a drag-handler and selobj are often the same object, but obeying a different API;
    # drag_handlers are retvals from a selobj-interface method (which typically returns self).
    def handles_updates(self):
        """Return True if you will do mt and glpane updates as needed,
        False if you want client mode to guess when to do them for you
        (it will probably guess: do both, on mouse down, drag, up;
         but do neither, on baremotion == move, except when selobj changes)
        """
        return False # otherwise subclass is likely to forget to do them
    def DraggedOn(self, event, mode):
        pass
    def ReleasedOn(self, selobj, event, mode):
        pass
    def leftDouble(self, event, mode):#070324 added this method to the interface (note: the call is implemented only in testmode)
        pass
    pass

# end
