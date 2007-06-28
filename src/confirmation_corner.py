# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
confirmation_corner.py -- helpers for modes with a confirmation corner
(or other overlay widgets).

$Id$

Note: confirmation corners make use of two methods added to the "mode API"
(the one used by GLPane to interface to glpane.mode for mouse and drawing)
for their sake, currently [070627] defined only in basicMode: draw_overlay
and mouse_event_handler_for_event_position. These are general enough to
handle all kinds of overlays, in principle, but the current implem and
some API details may be just barely general enough for the confirmation
corner.

Those method implems assume that mode subclasses override want_confirmation_corner_type
to return the kind of confirmation corner they want at a given moment.


"""

#### UNFINISHED

__author__ = "bruce"

import os

from exprs.basic import PIXELS
from exprs.images import Image
from exprs.instance_helpers import get_glpane_InstanceHolder

from exprs.Rect import Rect # needed for Image size option, not just for testing
from constants import green # only for testing

from exprs.projection import DrawInCorner_projection, DrawInCorner
from prefs_constants import UPPER_RIGHT

from debug import print_compact_traceback, print_compact_stack

# button region codes (must all be true values;
# these are used as indices in various dicts or functions,
# and are used as components of cctypes like 'Done+Cancel')
BUTTON_CODES = ('Done', 'Cancel')

# ==

class MouseEventHandler_API: #e refile #e some methods may need mode and/or glpane arg...
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

# ==

trans_image = Image(convert = 'RGBA', decal = False, blend = True,
                    # don't need (I think): alpha_test = False, shape = 'upper-right-half' 
                    clamp = True, # this removes the artifacts that show the edges of the whole square of the image file
                    ideal_width = 100, ideal_height = 100, size = Rect(100*PIXELS))

def expr_for_imagename(imagename): ### WARNING: this is not optimized -- it recomputes and discards this expr on every access!
    if '/' not in imagename:
        imagename = os.path.join( "ui/confcorner", imagename)
    image_expr = trans_image( imagename )
    return DrawInCorner(corner = UPPER_RIGHT)( image_expr )

IMAGENAMES = """BigCancel.png
BigCancel_pressed.png
BigOK.png
BigOK_pressed.png
Cancel_pressed.png
OK_Cancel.png
OK_pressed.png""".split()

class cc_MouseEventHandler(MouseEventHandler_API): #e rename # an instance can be returned from find_or_make
    "###doc"
    
    # initial values of state variables, etc
    last_button_position = False # False or an element of BUTTON_CODES
    pressed_button = False # False or an element of BUTTON_CODES; valid regardless of self.glpane.in_drag

    cctype = -1 # intentionally illegal value, different from any real value
    
    def __init__(self, glpane):
        self.glpane = glpane
        for imagename in IMAGENAMES:
            self.preload(imagename) # to avoid slowness when each image is first used in real life
        return

    def preload(imagename):
        self.expr_instance_for_imagename(imagename)
        return

    def expr_instance_for_imagename(self, imagename):
        ih = get_glpane_InstanceHolder(self.glpane)
        index = imagename # might have to be more unique if we start sharing this InstanceHolder with anything else
        expr = expr_for_imagename(imagename)
        expr_instance = ih.Instance( expr, index, skip_expr_compare = True)
        return expr_instance

    def _advise_find_args(self, cctype, mode):
        """private; can be called as often as every time this is drawn;
        cctype can be None or one of a few string constants
        """
        self.mode = mode # used to find buttons for doing actions; not cross-checked with passed or found modes...
        if self.cctype != cctype:
            # note: no point in updating drawing here if cctype changes,
            # since we're only called within glpane calling mode.draw_overlay.
            ## self.update_drawing()
            self.cctype = cctype
            if cctype:
                self.button_codes = cctype.split('+')
                assert len(self.button_codes) in (1,2)
                for bc in self.button_codes:
                    assert bc in BUTTON_CODES
            else:
                self.button_codes = []
        return

    # == event position (internal and _API methods), and other methods ###DESCRIBE better
    
    def want_event_position(self, wX, wY):
        """MouseEventHandler_API method:
        Return False if we don't want to be the handler for this event and immediately after it;
        return a true button-region-code if we do.
           Note: Only called externally when mouse is pressed (glpane.in_drag will already be set then),
        or moves when not pressed (glpane.in_drag will be unset); deprecated for internal calls.
        The current implem does not depend on only being called at those times, AFAIK.
        """
        return self.button_region_for_event_position(wX, wY)
    
    def button_region_for_event_position(self, wX, wY):
        """Return False if wX, wY is not over self, or a button-region-code
        (whose boolean value is true; an element of BUTTON_CODES) if it is,
        which says which button region of self it's over (regardless of pressed state of self).
        """
        # correct implem, but button-region size & shape is hardcoded
        dx = self.glpane.width - wX
        dy = self.glpane.height - wY
        if dx + dy <= 100:
            # this event is over the CC triangular region; which of our buttons is it over?
            if len(self.button_codes) == 2:
                if -dy >= -dx: # note: not the same as wY >= wX if glpane is not square!
                    return self.button_codes[0] # top half of corner triangle; usually 'Done'
                else:
                    return self.button_codes[1] # right half of corner triangle; usually 'Cancel'
            elif len(self.button_codes) == 1:
                return self.button_codes[0]
            else:
                return False # can this ever happen? I don't know, but if it does, it should work.
        return False
    
    def draw(self): ####UNTESTED
        """MouseEventHandler_API method: draw self. Assume background is already correct
        (so our implem can be the same, whether the incremental drawing optim for the rest
        of the GLPane content is operative or not).
        """
        # print "draw CC for cctype %r and state %r, %r" % (self.cctype, self.pressed_button, self.last_button_position)

        # figure out what image expr to draw

        # NOTE: this is currently not nearly as general as the rest of our logic,
        # regarding what values of self.button_codes are supported.
        # If we need it to be more general, we can split the expr into two triangular pieces,
        # using Image's shape option and Overlay, so its two buttons are independent
        # (as is done in some of the tests in exprs/test.py).

        if self.button_codes == ['Cancel']:
            if self.pressed_button == 'Cancel':
                imagename = "BigCancel_pressed.png"
            else:
                imagename = "BigCancel.png"
        elif self.button_codes == ['Done']:
            if self.pressed_button == 'Done':
                imagename = "BigOK_pressed.png"
            else:
                imagename = "BigOK.png"
        elif self.button_codes == ['Done', 'Cancel']:
            if self.pressed_button == 'Done':
                imagename = "OK_pressed.png"
            elif self.pressed_button == 'Cancel':
                imagename = "Cancel_pressed.png"
            else:
                imagename = "OK_Cancel.png"
        else:
            assert 0, "unsupported list of buttoncodes: %r" % (self.button_codes,)

        expr_instance = self.expr_instance_for_imagename(imagename)

            ### REVIEW: worry about value of PIXELS vs perspective? worry about depth writes?
    
        expr_instance.draw() # Note: this draws expr_instance in the same coordsys used for drawing the model.
        
        return
    
    def update_cursor(self, mode, wpos):
        "MouseEventHandler_API method; change cursor based on current state and event position"
        assert self.glpane is mode.o
        win = mode.w # for access to cursors
        wX, wY = wpos
        bc = self.button_region_for_event_position(wX, wY)
        # figure out want_cursor (False or a button code; in future there may be other codes for modified cursors)
        if not self.pressed_button:
            # mouse is not down; cursor reflects where we are at the moment (False or a button code)
            want_cursor = bc 
        else:
            # a button is pressed; cursor reflects whether this button will act or not
            # (based on whether we're over it now or not)
            # (for now, if the button will act, the cursor does not look any different
            #  than if we're hovering over the button, but revising that would be easy)
            if self.pressed_button == bc:
                want_cursor = bc
            else:
                want_cursor = False
        # show the cursor indicated by want_cursor
        if want_cursor:
            assert want_cursor in BUTTON_CODES
            if want_cursor == 'Done':
                cursor = win._confcorner_OKCursor
            else:
                cursor = win._confcorner_CancelCursor
            self.glpane.setCursor(cursor)
        else:
            # We want to set a cursor which indicates that we'll do nothing.
            # Modes won't tell us that cursor, but they'll set it as a side effect of mode.update_cursor_for_no_MB().
            # Actually, they may set the wrong cursor then (e.g. cookieMode, which looks at glpane.modkeys, but if we're
            # here with modkeys we're going to ignore them). If that proves to be misleading, we'll revise this.
            self.glpane.setCursor(win.ArrowCursor) # in case the following method does nothing (can happen)
            try:
                mode.update_cursor_for_no_MB() # _no_MB is correct, even though a button is presumably pressed.
            except:
                print_compact_traceback("bug: exception (ignored) in %r.update_cursor_for_no_MB(): " % (mode,) )
                pass
        return

    # == mouse event handling (part of the _API)
    
    def mousePressEvent(self, event):
        # print "meh press"
        wX, wY = wpos = self.glpane._last_event_wXwY
        bc = self.button_region_for_event_position(wX, wY)
        self.last_button_position = bc # this is for knowing when our appearance might change
        self.pressed_button = bc # this and glpane.in_drag serve as our state variables
        if not bc:
            print "bug: not bc in meh.mousePressEvent" # should never happen; if it does, do nothing
        else:
            self.update_drawing()
        return

    def mouseMoveEvent(self, event): ###e should we get but & mod as new args, or from glpane attrs set by fix_event??
        wX, wY = wpos = self.glpane._last_event_wXwY # or we could get these from event
        bc = self.button_region_for_event_position(wX, wY)
        if self.last_button_position != bc:
            self.last_button_position = bc
            self.update_drawing()
            self.do_update_cursor()
        return

    def mouseReleaseEvent(self, event):
        # print "meh rel"
        wX, wY = self.glpane._last_event_wXwY
        bc = self.button_region_for_event_position(wX, wY)
        if self.last_button_position != bc:
            print "unexpected: self.last_button_position != bc in meh.mouseReleaseEvent (should be harmless)" ###
        self.last_button_position = bc
        if self.pressed_button and self.pressed_button == bc:
            #e in future: if action might take time, maybe change drawing appearance to indicate we're "doing it"
            self.do_action(bc)
        self.pressed_button = False
        self.update_drawing() # might be redundant with do_action (which may need to update even more, I don't know for sure)
            # Note: this might not be needed if no action happens -- depends on nature of highlighting;
            # note that you can press one button and release over the other, and then the other might need to highlight
            # if it has mouseover highlighting (tho in current design, it doesn't).
        self.do_update_cursor()
        return

    # == internal update methods
    
    def do_update_cursor(self):
        "internal helper for calling our external API method update_cursor with the right arguments"
        wpos = self.glpane._last_event_wXwY
        mode = self.glpane.mode # kluge, not sure if always correct
        self.update_cursor( mode, wpos)
        return
    
    def update_drawing(self):
        ### TODO: figure out if our appearance has changed, and do nothing if not (important optim)
        # (be careful about whether we're the last CC to be drawn, if there's more than one and they get switched around!
        #  we might need those events about enter/leave that the glpane doesn't yet send us; or some about changing the cc) ###
        self.glpane.gl_update() # this should work, but NEEDS OPTIM to be incremental ### TODO

    # == internal action methods

    def do_action(self, buttoncode):
        "do the action corresponding to buttoncode (protected from exceptions)"
        #e in future: statusbar message?

        # print "do_action", buttoncode

        ###REVIEW: maybe all the following should be a mode method?
        # Note: it will all get revised and cleaned up once we have a command stack
        # and we can just tell the top command to do Done or Cancel.
        
        done_button, cancel_button = self.mode._KLUGE_visible_PM_buttons()
            # each one is either None, or a QToolButton (a true value) currently displayed on the current PM
        if buttoncode == 'Done':
            button = done_button
        else:
            button = cancel_button
        if not button:
            print "bug (ignored): %r trying to do action for nonexistent %r button" % (self, buttoncode) #e more info?
        else:
            try:
                # print "\nabout to click %r button == %r" % (buttoncode, button)
                button.click()
                    # This should make the button emit the clicked signal -- not sure if it will also emit
                    # the pressed and released signals. The Qt doc (for QAbstractButton.click) just says
                    # "All the usual signals associated with a click are emitted as appropriate."
                    # Our code mostly connects to clicked, but for a few buttons (not the ones we have here, I think)
                    # connects to pressed or released. Search for those words used in a SIGNAL macro to find them.
                    
                # Assume the click handler did whatever updates were required,
                # as it would need to do if the user pressed the button directly,
                # so no updates are needed here. That's good, because only the event handler
                # knows if some are not needed (as an optimization).
                
                # print "did the click"
            except:
                print_compact_traceback("bug: exception (ignored) when using %r button == %r: " % (buttoncode, button,) )
                pass
            pass
        return
    
    pass # end of class cc_MouseEventHandler

# ==

##def interpret_cctype(cctype, mode): # not used, unless perhaps via cc_scratch.py
##    "return None or an expr, ..."
##    return Rect(green) ###STUB

def find_or_make(cctype, mode):
    "Return a confirmation corner instance for mode, of the given cctype. [Called from basicMode.draw_overlay]"
    ##### STUB
    try:
        mode._confirmation_corner__cached_meh
    except AttributeError:
        mode._confirmation_corner__cached_meh = cc_MouseEventHandler(mode.o)
    res = mode._confirmation_corner__cached_meh
    res._advise_find_args(cctype, mode) # in case it wants to store these (especially since it's shared for different values of them)
    return res
    # see also exprs/cc_scratch.py

# end
