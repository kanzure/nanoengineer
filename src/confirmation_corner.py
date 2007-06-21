# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
confirmation_corner.py -- helpers for modes with a confirmation corner
(or other overlay widgets).

$Id$
"""

#### UNFINISHED

__author__ = "bruce"

## from exprs.basic import *
from exprs.Highlightable import Highlightable
from exprs.images import Image
from exprs.Overlay import Overlay


class MouseEventHandler_API: #e refile #e put implems in subclass #e some methods may need mode and/or glpane arg...
    """API (and default method implems) for the MouseEventHandler interface
    (for objects used as glpane.mouse_event_handler) [abstract class]
    """
    def mouseMoveEvent(self, event):
        ""
    def mouseDoubleClickEvent(self, event):
        ""
    def mousePressEvent(self, event):
        ""
    def mouseReleaseEvent(self, event):
        ""
    def update_cursor(self, mode):
        "Perform side effects in mode (assumed to be a basicMode subclass) to give it the right cursor for being over self"
        ###e probably needs more args (like mouse posn, mod keys, etc), or official access to more info (like glpane.button),
        # to choose the cursor
    def want_event_position(self, wX, wY):
        "Return True if self wants to handle mouse events at the given OpenGL window coords, False otherwise"
    def draw(self):
        ""
    pass

class cc_MouseEventHandler(MouseEventHandler_API): #e rename # an instance can be returned from find_or_make for testing...
    "###doc"
    def __init__(self, glpane):
        self.glpane = glpane
    def update_cursor(self, mode):
         ###stub for testing
        assert self.glpane is mode.o
        win = mode.w
        self.glpane.setCursor(win.RotateCursor)
    def want_event_position(self, wX, wY):
        ###stub for testing
        dx = self.glpane.width - wX
        dy = self.glpane.height - wY
        if dx + dy <= 100:
            return True
        return False
    def draw(self):
        pass ###stub
    pass

def interpret_cctype(cctype, mode): # not used, unless perhaps via cc_scratch.py
    "return None or an expr, ..."
    return Rect(green) ###STUB

def find_or_make(cctype, mode):
    "Return a confirmation corner instance for mode, of the given cctype. [Called from basicMode.draw_overlay]"
    ##### STUB
    try:
        mode._confirmation_corner__cached_meh
    except AttributeError:
        mode._confirmation_corner__cached_meh = cc_MouseEventHandler(mode.o)
    return mode._confirmation_corner__cached_meh
    # see exprs/cc_scratch.py

# end
