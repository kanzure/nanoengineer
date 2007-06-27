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

# button region codes (must be true values)
OK = 'OK'
CANCEL = 'CANCEL'

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
    def update_cursor(self, mode, wpos):
        """Perform side effects in mode (assumed to be a basicMode subclass)
        to give it the right cursor for being over self
        at position <wpos> (in OpenGL window coords).
        """
        ###e may need more args (like mod keys, etc),
        # or official access to more info (like glpane.button),
        # to choose the cursor
    def want_event_position(self, wX, wY):
        """Return a true value if self wants to handle mouse events
        at the given OpenGL window coords, false otherwise.
           Note: some implems, in the true case, actually return some data
        indicating what cursor and display state they want to use; it's not
        yet decided whether this is supported in the official API (it's not yet)
        or merely permitted for internal use (it is and always will be).
        """
    def draw(self):
        ""
    pass

class cc_MouseEventHandler(MouseEventHandler_API): #e rename # an instance can be returned from find_or_make for testing...
    "###doc"
    def __init__(self, glpane):
        self.glpane = glpane
    def update_cursor(self, mode, wpos):
         ###stub for testing
        assert self.glpane is mode.o
        win = mode.w # for access to cursors
        wX, wY = wpos
        want = self.want_event_position(wX, wY)
        ###e WRONG -- should notice if we're in_drag, let each half behave like a button then...
        if want:
            if want == OK:
                cursor = win._confcorner_OKCursor
            else:
                cursor = win._confcorner_CancelCursor
            self.glpane.setCursor(cursor)
        else:
            # This only happens during a drag, when we're still the event handler but don't want this position.
            # (After some logic bug fixes above it will also happen whenever we're not over our last-pressed button.)
            # We want to set a cursor which indicates that we'll do nothing.
            # Modes won't tell us that cursor, but they'll set it as a side effect of mode.update_cursor_for_no_MB().
            # Actually, they may set the wrong cursor then (e.g. cookieMode, which looks at glpane.modkeys, but if we're
            # here with modkeys we're going to ignore them). If that proves to be misleading, we'll revise this.
            self.glpane.setCursor(win.ArrowCursor) # in case the following method does nothing (can happen)
            mode.update_cursor_for_no_MB() # _no_MB is correct, even though a button is presumably pressed.
        return
    def want_event_position(self, wX, wY):
        """Return False if we don't want it, and a true button-region-code if we do.
        WARNING: that code does not yet notice whether we're a 1-button or 2-button corner;
        it pretends we're a 2-button corner.
        """
        # correct (for 2-button case), but image size & shape is hardcoded
        dx = self.glpane.width - wX
        dy = self.glpane.height - wY
        if dx + dy <= 100:
            if -dy >= -dx: # note: not the same as wY >= wX if glpane is not square!
                return OK
            else:
                return CANCEL
        return False
    def draw(self):
        pass ###stub
    def mouseMoveEvent(self, event): ###e should we get but & mod as new args, or from glpane attrs set by fix_event??
        wX, wY = wpos = self.glpane._last_event_wXwY # or we could get these from event
        want = self.want_event_position(wX, wY)
        #e should test if want or other state has changed
        mode = self.glpane.mode # kluge, not sure if always correct
        self.update_cursor( mode, wpos)
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
