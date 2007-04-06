# Copyright (c) 2007 Nanorex, Inc.  All rights reserved.
"""
confirmation_corner.py -- helpers for modes with a confirmation corner
(or other overlay widgets).

$Id$
"""

__author__ = "bruce"

## from exprs.basic import *
from exprs.Highlightable import Highlightable
from exprs.images import Image
from exprs.Overlay import Overlay

## from exprs.test import * # remove when less lazy; may have bad side effects, or crash from thinking we're in testmode ###k


# stuff to set up the env... see what testdraw does

# a place to make instances, new ones have totally fresh state, but only keep one, or let caller supply index...




class MouseEventHandler: #bruce 070405 #e refile #e put implems in subclass #e some methods may need mode and/or glpane arg...
    "interface for objects used as glpane.mouse_event_handler"
    def mouseMoveEvent(self, event):
        ""
    def mouseDoubleClickEvent(self, event):
        ""
    def mousePressEvent(self, event):
        ""
    def mouseReleaseEvent(self, event):
        ""
    def update_cursor(self, mode):
        ""
        self = mode
        self.o.setCursor(self.w.RotateCursor) ###stub for testing
    def want_event_position(self, wX, wY):###stub for testing
        dx = self.o.width - wX
        dy = self.o.height - wY
        if dx + dy <= 100:
            return True
        return False
    pass

class InstanceHolder:
    "A self-contained place to make and hold Instances of exprs, which makes its own drawing env."
    def __init__(self, glpane):
        self.thing = None ####STUB ...
    def Instance(self, *args, **kws):
        return self.thing.Instance(*args, **kws)
    pass
    
def interpret_cctype(cctype, mode):
    "return None or an expr, ..."
    return Rect(green) ###STUB

def find_or_make(cctype, mode):
    "Return a confirmation corner instance for mode, of the given cctype."
    return None ##### STUB
    try:
        place = mode._confirmation_corner__place
    except AttributeError:
        glpane = mode.o
        place = mode._confirmation_corner__place = InstanceHolder(glpane) ###IMPLEM; what about the env, does it have one? etc
    ccexpr = interpret_cctype(cctype, mode) # None or an expr
    if ccexpr is not None:
        # find or make an instance of that expr (caching nothing except the one currently in use)
        ccinstance = place.Instance(ccexpr, 'index', permit_expr_to_vary = True) #####BUG: pass unique ipath, or clear state, or ....
    else:
        ccinstance = None
    return ccinstance
