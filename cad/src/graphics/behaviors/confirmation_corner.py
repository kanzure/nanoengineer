# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
confirmation_corner.py -- helpers for modes with a confirmation corner
(or other overlay widgets).

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

Note: confirmation corners make use of two methods added to the "GraphicsMode API"
(the one used by GLPane to interface to glpane.graphicsMode for mouse and drawing)
for their sake, currently [071015] defined only in basicGraphicsMode:
draw_overlay, and mouse_event_handler_for_event_position. These are general enough
to handle all kinds of overlays, in principle, but the current implem and
some API details may be just barely general enough for the confirmation
corner.

Those method implems assume that Command subclasses (at least those which
can be found by GraphicsMode.draw_overlay -- namely, those which supply their
own PM, as of 080905) override want_confirmation_corner_type
to return the kind of confirmation corner they want at a given moment.
"""

import os

from exprs.ExprsConstants import PIXELS
from exprs.images import Image
from exprs.Overlay import Overlay

from exprs.instance_helpers import get_glpane_InstanceHolder

from exprs.Rect import Rect # needed for Image size option, not just for testing
##from constants import green # only for testing

from exprs.projection import DrawInCorner ##, DrawInCorner_projection
from utilities.prefs_constants import UPPER_RIGHT

from utilities.debug import print_compact_traceback ##, print_compact_stack

from utilities.debug_prefs import debug_pref, Choice_boolean_False

# button region codes (must all be true values;
# these are used as indices in various dicts or functions,
# and are used as components of cctypes like 'Done+Cancel')
BUTTON_CODES = ('Done', 'Cancel', 'Transient-Done')

# ==

class MouseEventHandler_API: #e refile #e some methods may need graphicsMode and/or glpane arg...
    """
    API (and default method implems) for the MouseEventHandler interface
    (for objects used as glpane.mouse_event_handler) [abstract class]
    """
    def mouseMoveEvent(self, event):
        """
        """
        pass
    def mouseDoubleClickEvent(self, event):
        """
        """
        pass
    def mousePressEvent(self, event):
        """
        """
        pass
    def mouseReleaseEvent(self, event):
        """
        """
        pass
    def update_cursor(self, graphicsMode, wpos):
        """
        Perform side effects in graphicsMode (assumed to be a basicGraphicsMode subclass)
        to give it the right cursor for being over self
        at position <wpos> (in OpenGL window coords).
        """
        ###e may need more args (like mod keys, etc),
        # or official access to more info (like glpane.button),
        # to choose the cursor
        pass
    def want_event_position(self, wX, wY):
        """
        Return a true value if self wants to handle mouse events
        at the given OpenGL window coords, false otherwise.

        Note: some implems, in the true case, actually return some data
        indicating what cursor and display state they want to use; it's not
        yet decided whether this is supported in the official API (it's not yet)
        or merely permitted for internal use (it is and always will be).
        """
        pass
    def draw(self):
        """
        """
        pass
    pass

# ==

# exprs for images

# overlay image (command-specific icon)

# This draws a 22 x 22 icon in the upper left corner of the glpane.
# I need to be able to change the origin of the icon so it can be drawn at
# a different location inside the confirmation corner, but I cannot
# figure out how to do this. I will discuss with Bruce soon. -Mark 2008-03-23

_overlay_image = Image(convert = 'RGBA',
                       decal = False,
                       blend = True,
                       #ideal_width = 22,
                       #ideal_height = 22,
                       size = Rect(22 * PIXELS))

from exprs.transforms import Translate
from exprs.Exprs import V_expr
from exprs.Rect import Spacer

def _expr_for_overlay_imagename(imagename, dx = 0, dy = 0):
    # WARNING: this is not optimized (see comment for _expr_for_imagename()).
    image_expr = _overlay_image( imagename )
        # NOTE: If the desired dx,dy depends on other settings,
        # like whether one or two CC buttons are shown,
        # then it's simplest to make more variants of this expr,
        # with dx, dy hardcoded differently in each one.
        # Or if that's not practical, let me know and I'll
        # revise the code that draws this to accomodate that variability.
        # Also make sure to revise the code that calls each one
        # (i.e. a modified copy of _expr_instance_for_overlay_imagename)
        # to use a different "index" even when using the same imagename.
        # (For example, it could include dx,dy in the index.)
        # [bruce 080324]
    return DrawInCorner(corner = UPPER_RIGHT)(
        Overlay(
            Spacer(22 * PIXELS),
            Translate( image_expr, V_expr(dx * PIXELS, dy * PIXELS, 0)),
         )
     )

# ==

# button images

_trans_image = Image(convert = 'RGBA', decal = False, blend = True,
                    # don't need (I think): alpha_test = False
                    shape = 'upper-right-half', #bruce 070628 maybe this will fix bug 2474 (which I can't see on Mac);
                        # note that it has a visible effect on Mac (makes the intended darker edge of the buttons less thick),
                        # but this seems ok.
                    clamp = True, # this removes the artifacts that show the edges of the whole square of the image file
                    ideal_width = 100, ideal_height = 100, size = Rect(100 * PIXELS))

def _expr_for_imagename(imagename):
    # WARNING: this is not optimized -- it recomputes and discards this expr on every access!
    # (But it looks like its caller, _expr_instance_for_imagename, caches the expr instances,
    #  so only the uninstantiated expr itself is recomputed each time, so it's probably ok.
    #  [bruce 080323 comment])

    if '/' not in imagename:
        imagename = os.path.join( "ui/confcorner", imagename)
    image_expr = _trans_image( imagename )
    return DrawInCorner(corner = UPPER_RIGHT)( image_expr )

# ==

# These IMAGENAMES are used only for a preloading optimization.
# If this list is not complete, it will not cause bugs,
# it will just mean the first use of certain images is slower
# (but startup is faster by the same amount).
# [bruce 080324 comment]

IMAGENAMES = """
CancelBig.png
CancelBig_Pressed.png
DoneBig.png
DoneBig_Pressed.png
DoneSmall_Cancel_Pressed.png
DoneSmall.png
DoneSmall_Pressed.png
TransientDoneSmall.png
TransientDoneSmall_Pressed.png
TransientDoneSmall_Cancel_Pressed.png
TransientDoneBig.png
TransientDoneBig_Pressed.png""".split()

# ==

class cc_MouseEventHandler(MouseEventHandler_API): #e rename # an instance can be returned from find_or_make_confcorner_instance
    """
    ###doc
    """

    # initial values of state variables, etc
    _last_button_position = False # False or an element of BUTTON_CODES
    _pressed_button = False # False or an element of BUTTON_CODES; valid regardless of self.glpane.in_drag

    _cctype = -1 # intentionally illegal value, different from any real value

    # review: are self.glpane and self.command, set below, private?
    # if so, should rename them to indicate this. [bruce 080323 comment]

    def __init__(self, glpane):
        self.glpane = glpane
        for imagename in IMAGENAMES:
            self._preload(imagename) # to avoid slowness when each image is first used in real life
        return

    def _preload(self, imagename):
        self._expr_instance_for_imagename(imagename)
        return

    def _expr_instance_for_imagename(self, imagename):
        ih = get_glpane_InstanceHolder(self.glpane)
        index = imagename # might have to be more unique if we start sharing this InstanceHolder with anything else
        expr = _expr_for_imagename(imagename)
        expr_instance = ih.Instance( expr, index, skip_expr_compare = True)
        return expr_instance

    def _expr_instance_for_overlay_imagename(self, imagename, dx = 0, dy = 0):
        ih = get_glpane_InstanceHolder(self.glpane)
        index = 1, imagename # might have to be more unique if we start sharing this InstanceHolder with anything else
        expr = _expr_for_overlay_imagename(imagename, dx, dy)
        expr_instance = ih.Instance( expr, index, skip_expr_compare = True)
        return expr_instance

    def _f_advise_find_args(self, cctype, command):
        """
        [friend method; can be called as often as every time this is drawn;
         cctype can be None or one of a few string constants.]

        Set self._button_codes correctly for cctype and command,
        also saving those in attrs of self of related names.

        self.command is used later for:
        - finding PM buttons for doing actions
        - finding the icon for the Done button, from the PM
        """
        self.command = command
        if self._cctype != cctype:
            # note: no point in updating drawing here if cctype changes,
            # since we're only called within glpane calling graphicsMode.draw_overlay.
            ## self._update_drawing()
            self._cctype = cctype
            if cctype:
                self._button_codes = cctype.split('+')
                assert len(self._button_codes) in (1, 2)
                for bc in self._button_codes:
                    assert bc in BUTTON_CODES
            else:
                self._button_codes = []
        return

    # == event position (internal and _API methods), and other methods ###DESCRIBE better

    def want_event_position(self, wX, wY):
        """
        MouseEventHandler_API method:
        Return False if we don't want to be the handler for this event and immediately after it;
        return a true button-region-code if we do.

        @note: Only called externally when mouse is pressed (glpane.in_drag will already be set then),
        or moves when not pressed (glpane.in_drag will be unset); deprecated for internal calls.
        The current implem does not depend on only being called at those times, AFAIK.
        """
        return self._button_region_for_event_position(wX, wY)

    def _button_region_for_event_position(self, wX, wY):
        """
        Return False if wX, wY is not over self, or a button-region-code
        (whose boolean value is true; an element of BUTTON_CODES) if it is,
        which says which button region of self it's over (regardless of pressed state of self).
        """
        # correct implem, but button-region size & shape is hardcoded
        dx = self.glpane.width - wX
        dy = self.glpane.height - wY
        if dx + dy <= 100:
            # this event is over the CC triangular region; which of our buttons is it over?
            if len(self._button_codes) == 2:
                if -dy >= -dx: # note: not the same as wY >= wX if glpane is not square!
                    return self._button_codes[0] # top half of corner triangle; usually 'Done'
                else:
                    return self._button_codes[1] # right half of corner triangle; usually 'Cancel'
            elif len(self._button_codes) == 1:
                return self._button_codes[0]
            else:
                return False # can this ever happen? I don't know, but if it does, it should work.
        return False

    def _transient_overlay_icon_name(self, imagename):
        """
        Returns the transient overlay icon filename to include in the
        confirmation corner. This is the current command's icon that is used
        in the title of the property manager.

        @param imagename: Confirmation corner imagename.
        @type  imagename: string

        @return: Iconpath of the image to use as an overlay in the confimation
                 corner, delta x and delta y translation for positioning the
                 icon in the confirmation corner.
        @rtype:  string, int, int
        """
        if "Transient" in imagename:
            if "Big" in imagename:
                dx = -46
                dy = -6
            else:
                dx = -51
                dy = -1
            return (self.command.propMgr.iconPath, dx, dy)
        return (None, 0, 0)

    def draw(self):
        """
        MouseEventHandler_API method: draw self. Assume background is already
        correct (so our implem can be the same, whether the incremental drawing
        optim for the rest of the GLPane content is operative or not).
        """
        if 0:
            print "draw CC for cctype %r and state %r, %r" \
                  % (self._cctype,
                     self._pressed_button,
                     self._last_button_position)

        # figure out what image expr to draw

        # NOTE: this is currently not nearly as general as the rest of our
        # logic, regarding what values of self._button_codes are supported.
        # If we need it to be more general, we can split the expr into two
        # triangular pieces, using Image's shape option and Overlay, so its
        # two buttons are independent (as is done in some of the tests in
        # exprs/test.py).

        if self._button_codes == []:
            # the easy case
            return
        elif self._button_codes == ['Cancel']:
            if self._pressed_button == 'Cancel':
                imagename = "CancelBig_Pressed.png"
            else:
                imagename = "CancelBig.png"
        elif self._button_codes == ['Done']:
            if self._pressed_button == 'Done':
                imagename = "DoneBig_Pressed.png"
            else:
                imagename = "DoneBig.png"
        elif self._button_codes == ['Done', 'Cancel']:
            if self._pressed_button == 'Done':
                imagename = "DoneSmall_Pressed.png"
            elif self._pressed_button == 'Cancel':
                imagename = "DoneSmall_Cancel_Pressed.png"
            else:
                imagename = "DoneSmall.png"
        elif self._button_codes == ['Transient-Done', 'Cancel']:
            if self._pressed_button == 'Transient-Done':
                imagename = "TransientDoneSmall_Pressed.png"
            elif self._pressed_button == 'Cancel':
                imagename = "TransientDoneSmall_Cancel_Pressed.png"
            else:
                imagename = "TransientDoneSmall.png"
        elif self._button_codes == ['Transient-Done']:
            if self._pressed_button == 'Transient-Done':
                imagename = "TransientDoneBig_Pressed.png"
            else:
                imagename = "TransientDoneBig.png"
        else:
            assert 0, "unsupported list of buttoncodes: %r" \
                   % (self._button_codes,)

        expr_instance = self._expr_instance_for_imagename(imagename)
            ### REVIEW: worry about value of PIXELS vs perspective?
            ###         worry about depth writes?
        expr_instance.draw()
            # Note: this draws expr_instance in the same coordsys used for
            # drawing the model.

        overlay_imagename, dx, dy = self._transient_overlay_icon_name(imagename)
        if overlay_imagename:
            expr_instance = \
                self._expr_instance_for_overlay_imagename(overlay_imagename,
                                                          dx, dy)
            expr_instance.draw()

        return

    def update_cursor(self, graphicsMode, wpos):
        """
        MouseEventHandler_API method; change cursor based on current state and
        event position
        """
        assert self.glpane is graphicsMode.glpane
        win = graphicsMode.win # for access to cursors
        wX, wY = wpos
        bc = self._button_region_for_event_position(wX, wY)
        # figure out want_cursor (False or a button code; in future there may
        # be other codes for modified cursors)
        if not self._pressed_button:
            # mouse is not down; cursor reflects where we are at the moment
            # (False or a button code)
            want_cursor = bc
        else:
            # a button is pressed; cursor reflects whether this button will act
            # or not (based on whether we're over it now or not)
            # (for now, if the button will act, the cursor does not look any
            # different than if we're hovering over the button, but revising
            # that would be easy)
            if self._pressed_button == bc:
                want_cursor = bc
            else:
                want_cursor = False
        # show the cursor indicated by want_cursor
        if want_cursor:
            assert want_cursor in BUTTON_CODES
            if want_cursor == 'Done':
                cursor = win._confcorner_OKCursor
            elif want_cursor == 'Transient-Done':
                cursor = win.confcorner_TransientDoneCursor
            else:
                cursor = win._confcorner_CancelCursor
            self.glpane.setCursor(cursor)
        else:
            # We want to set a cursor which indicates that we'll do nothing.
            # Modes won't tell us that cursor, but they'll set it as a side
            # effect of graphicsMode.update_cursor_for_no_MB().
            # Actually, they may set the wrong cursor then (e.g. BuildCrystal_Command,
            # which looks at glpane.modkeys, but if we're here with modkeys
            # we're going to ignore them). If that proves to be misleading,
            # we'll revise this.
            self.glpane.setCursor(win.ArrowCursor)
                # in case the following method does nothing (can happen)
            try:
                graphicsMode.update_cursor_for_no_MB()
                    # _no_MB is correct, even though a button is presumably
                    # pressed.
            except:
                print_compact_traceback("bug: exception (ignored) in %r.update_cursor_for_no_MB(): " % (graphicsMode,) )
                pass
        return

    # == mouse event handling (part of the _API)

    def mousePressEvent(self, event):
        # print "meh press"
        wX, wY = wpos = self.glpane._last_event_wXwY
        bc = self._button_region_for_event_position(wX, wY)
        self._last_button_position = bc # this is for knowing when our appearance might change
        self._pressed_button = bc # this and glpane.in_drag serve as our state variables
        if not bc:
            print "bug: not bc in meh.mousePressEvent" # should never happen; if it does, do nothing
        else:
            self._update_drawing()
        return

    def mouseMoveEvent(self, event): ###e should we get but & mod as new args, or from glpane attrs set by fix_event??
        wX, wY = wpos = self.glpane._last_event_wXwY # or we could get these from event
        bc = self._button_region_for_event_position(wX, wY)
        if self._last_button_position != bc:
            self._last_button_position = bc
            self._update_drawing()
            self._do_update_cursor()
        return

    def mouseReleaseEvent(self, event):
        # print "meh rel"
        wX, wY = self.glpane._last_event_wXwY
        bc = self._button_region_for_event_position(wX, wY)
        if self._last_button_position != bc:
            print "unexpected: self._last_button_position != bc in meh.mouseReleaseEvent (should be harmless)" ###
        self._last_button_position = bc
        if self._pressed_button and self._pressed_button == bc:
            #e in future: if action might take time, maybe change drawing appearance to indicate we're "doing it"
            self._do_action(bc)
        self._pressed_button = False
        self._update_drawing() # might be redundant with _do_action (which may need to update even more, I don't know for sure)
            # Note: this might not be needed if no action happens -- depends on nature of highlighting;
            # note that you can press one button and release over the other, and then the other might need to highlight
            # if it has mouseover highlighting (tho in current design, it doesn't).
        self._do_update_cursor() # probably not needed (but should be ok as a precaution)
        return

    # == internal update methods

    def _do_update_cursor(self): ### TODO: REVISE DOCSTRING; it's unclear after recent changes [bruce 070628]
        """
        internal helper for calling our external API method update_cursor with the right arguments --
        but only if we're still responsible for the cursor according to the GLPane --
        otherwise, call the one that is!
        """
        self.glpane.graphicsMode.update_cursor()
            #bruce 070628 revised this as part of fixing bug 2476 (leftover CC Done cursor).
            # Before, it called our own update_cursor, effectively assuming we're still active,
            # wrong after a release and button action. Now, this is redundant in that case, but
            # should be harmless; it might still be needed in the move case (though probably self
            # is always active then).
        return

    def _update_drawing(self):
        ### TODO: figure out if our appearance has changed, and do nothing if not (important optim)
        # (be careful about whether we're the last CC to be drawn, if there's more than one and they get switched around!
        #  we might need those events about enter/leave that the glpane doesn't yet send us; or some about changing the cc) ###
        self.glpane.gl_update_confcorner() # note: as of 070627 this is the same as gl_update -- NEEDS OPTIM to be incremental

    # == internal action methods

    def _do_action(self, buttoncode):
        """
        do the action corresponding to buttoncode (protected from exceptions)
        """
        #e in future: statusbar message?

        # print "_do_action", buttoncode

        ###REVIEW: maybe all the following should be a Command method?
        # Note: it will all get revised and cleaned up once we have a command stack
        # and we can just tell the top command to do Done or Cancel.

        done_button, cancel_button = self.command._KLUGE_visible_PM_buttons()
            # each one is either None, or a QToolButton (a true value) currently displayed on the current PM
        if buttoncode in ['Done', 'Transient-Done']:
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
            # we did the action; now (at least for Done or Cancel), we should inactivate self as mouse_event_handler
            # and then do update_cursor, which the following does (part of fixing bug 2476 (leftover CC Done cursor))
            # [bruce 070628]
            self.glpane.set_mouse_event_handler(None)
            pass
        return

    pass # end of class cc_MouseEventHandler

# ==

def find_or_make_confcorner_instance(cctype, command):
    """
    Return a confirmation corner instance for command, of the given cctype.
    [Public; called from basicGraphicsMode.draw_overlay]
    """
    try:
        command._confirmation_corner__cached_meh
    except AttributeError:
        command._confirmation_corner__cached_meh = cc_MouseEventHandler(command.glpane)
    res = command._confirmation_corner__cached_meh
    res._f_advise_find_args(cctype, command) # in case it wants to store these
        # (especially since it's shared for different values of them)
    return res
    # see also exprs/cc_scratch.py

# end
