# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_event_methods.py

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

bruce 080910 split this out of class GLPane
"""

import time

from PyQt4.Qt import QEvent
from PyQt4.Qt import QMouseEvent
from PyQt4.Qt import QHelpEvent
from PyQt4.Qt import QPoint
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL, QTimer

from PyQt4.QtOpenGL import QGLWidget

from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import glReadPixelsf

from OpenGL.GLU import gluUnProject

from geometry.VQT import V, A, norm
from geometry.VQT import planeXline, ptonline

from Numeric import dot

import foundation.env as env

from utilities import debug_flags
from utilities.debug import print_compact_traceback

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice
from utilities.debug_prefs import Choice_boolean_False

from utilities.constants import GL_FAR_Z
from utilities.constants import MULTIPANE_GUI

from utilities.GlobalPreferences import DEBUG_BAREMOTION
import utilities.qt4transition as qt4transition

from platform_dependent.PlatformDependent import fix_event_helper
from platform_dependent.PlatformDependent import wrap_key_event

from widgets.menu_helpers import makemenu_helper
from widgets.DebugMenuMixin import DebugMenuMixin

from graphics.widgets.DynamicTip import DynamicTip

from ne1_ui.cursors import createCompositeCursor

# ==

## button_names = {0:None, 1:'LMB', 2:'RMB', 4:'MMB'} 
button_names = {Qt.NoButton:None, Qt.LeftButton:'LMB', Qt.RightButton:'RMB', Qt.MidButton:'MMB'}
    #bruce 070328 renamed this from 'button' (only in Qt4 branch), and changed the dict keys from ints to symbolic constants,
    # and changed the usage from dict lookup to iteration over items, to fix some cursor icon bugs.
    # For the constants, see http://www.riverbankcomputing.com/Docs/PyQt4/html/qmouseevent.html
    # [Note: if there is an import of GLPane.button elsewhere, that'll crash now due to the renaming. Unfortunately, for such
    #  a common word, it's not practical to find out except by renaming it and seeing if that causes bugs.]

# ==

class GLPane_event_methods(object, DebugMenuMixin):
    """
    """
    # bruce 041220: handle keys in GLPane (see also setFocusPolicy, above).
    # Also call these from MWsemantics whenever it has the focus. This fixes
    # some key-focus-related bugs. We also wrap the Qt events with our own
    # type, to help fix Qt's Mac-specific Delete key bug (bug 93), and (in the
    # future) for other reasons. The fact that clicking in the GLPane now gives
    # it the focus (due to the setFocusPolicy, above) is also required to fully
    # fix bug 93.

    def _init_GLPane_event_methods(self):
        """
        """

        DebugMenuMixin._init1(self) # provides self.debug_event() [might provide or require more things too... #doc]

        # Current coordinates of the mouse (public attribute for event handlers;
        # they can set it by calling SaveMouse)
        self.MousePos = V(0, 0)

        # Selection lock state of the mouse for this glpane.
        # Public attribute for read and modification by external
        # event handling code.
        # See selectionLock() in the ops_select_Mixin class for details.
        self.mouse_selection_lock_enabled = False

        # not selecting anything currently
        # [I think this is for region selection --bruce 080912 guess]
        # [as of 050418 (and before), this is used in BuildCrystal_Command and selectMode]
        self.shape = None

        # Cursor position of the last timer event. Mark 060818
        self.timer_event_last_xy = (0, 0)

        self.setMouseTracking(True)

        # bruce 041220 let the GLPane have the keyboard focus, to fix bugs.
        # See comments above our keyPressEvent method.
        ###e I did not yet review  the choice of StrongFocus in the Qt docs,
        # just copied it from MWsemantics.
        self.setFocusPolicy(Qt.StrongFocus)

##        self.singlet = None #bruce 060220 zapping this, seems to be old and to no longer be used
        self.selatom = None # josh 10/11/04 supports BuildAtoms_Command

        self.jigSelectionEnabled = True # mark 060312

        self.triggerBareMotionEvent = True 
            # Supports timerEvent() to minimize calls to bareMotion(). Mark 060814.
        self.wheelHighlight = False
            # russ 080527: Fix Bug 2606 (highlighting not turned on after wheel event.)
            # Indicates handling bareMotion for highlighting after a mousewheel event.

        self.cursorMotionlessStartTime = time.time() #bruce 070110 fix bug when debug_pref turns off glpane timer from startup

        # Triple-click Timer: for the purpose of implementing a triple-click
        #                     event handler, which is not supported by Qt.
        #
        # See: mouseTripleClickEvent()

        self.tripleClick       =  False
        self.tripleClickTimer  =  QTimer(self)
        self.tripleClickTimer.setSingleShot(True)
        self.connect(self.tripleClickTimer, SIGNAL('timeout()'), self._tripleClickTimeout)

        self.dynamicToolTip = DynamicTip(self)

        return

    # == related to DebugMenuMixin
    
    def makemenu(self, menu_spec, menu = None):
        # this overrides the one from DebugMenuMixin (with the same code), but that's ok,
        # since we want to be self-contained in case someone later removes that mixin class;
        # this method is called by our modes to make their context menus.
        # [bruce 050418 comment]
        return makemenu_helper(self, menu_spec, menu)

    def debug_menu_items(self): #bruce 050515
        """
        [overrides method from DebugMenuMixin]
        """
        usual = DebugMenuMixin.debug_menu_items(self)
            # list of (text, callable) pairs, None for separator
        ours = list(usual)
        try:
            # submenu for available custom modes [bruce 050515]
            # todo [080209]: just include this submenu in the DebugMenuMixin version
            # (no reason it ought to be specific to glpane)
            modemenu = self.win.commandSequencer.custom_modes_menuspec()
            if modemenu:
                ours.append(("custom modes", modemenu))
        except:
            print_compact_traceback("exception ignored: ")
        return ours

    # == related to key events

    def keyPressEvent(self, e):
        #e future: also track these to match releases with presses, to fix
        # dialogs intercepting keyRelease? Maybe easier if they just pass it on.
        mc = env.begin_op("(keypress)") #bruce 060127
            # Note: we have to wrap press and release separately; later, we might pass them tags
            # to help the diffs connect up for merging
            # (same as in drags and maybe as in commands doing recursive event processing).
            # [bruce 060127]
        try:
            #print "GLPane.keyPressEvent(): self.in_drag=",self.in_drag
            if not self.in_drag:
                #bruce 060220 new code; should make it unnecessary (and incorrect)
                # for modes to track mod key press/release for cursor,
                # once update_modkeys calls a cursor updating routine
                #but = e.stateAfter()
                #self.update_modkeys(but)
                self.update_modkeys(e.modifiers())
            self.graphicsMode.keyPressEvent( wrap_key_event(e) )
        finally:
            env.end_op(mc)
        return

    def keyReleaseEvent(self, e):
        mc = env.begin_op("(keyrelease)") #bruce 060127
        try:
            if not self.in_drag:
                #bruce 060220 new code; see comment in keyPressEvent
                #but = e.stateAfter()
                #self.update_modkeys(but)
                self.update_modkeys(e.modifiers())
            self.graphicsMode.keyReleaseEvent( wrap_key_event(e) )
        finally:
            env.end_op(mc)
        return

    # ==

    def makeCurrent(self):
        QGLWidget.makeCurrent(self)
        # also tell the MainWindow that my PartWindow is the active one
        # REVIEW: when Qt calls makeCurrent before calling e.g. resizeGL,
        # does it call this method, or just QGLWidget.makeCurrent?
        # [bruce 080912 question]
        if MULTIPANE_GUI:
            pw = self.partWindow
            pw.parent._activepw = pw
        return
    
    # ==

    _cursorWithoutSelectionLock = None #bruce 080918 added def, made private
    
    def setCursor(self, inCursor = None):
        """
        Sets the cursor for the glpane.

        This method is also responsible for adding special symbols to the 
        cursor that should be persistent as cursors change (i.e. the selection
        lock symbol). That's controlled by attrs of self, not by arguments.

        @param inCursor: Either a cursor or a list of 2 cursors (one for a dark
                         background, one for a light background). 
                         If cursor is None, reset the cursor to the
                         most recent version without the selection lock symbol.
        @type  inCursor: U{B{QCursor}<http://doc.trolltech.com/4/qcursor.html>} or
                         a list of two {B{QCursors}<http://doc.trolltech.com/4/qcursor.html>}
                         (but None can be used in place of any QCursor).
        """
        # If inCursor is a list (of a dark and light bg cursor), set
        # cursor to one or the other based on the current background.
        if isinstance(inCursor, list):
            if self.is_background_dark():
                cursor = inCursor[0] # dark bg cursor
            else:
                cursor = inCursor[1] # light bg cursor
            pass
        else:
            cursor = inCursor

        # Cache unmodified version of cursor,
        # or use the cached cursor if None is provided.
        if not cursor:
            cursor = self._cursorWithoutSelectionLock
        self._cursorWithoutSelectionLock = cursor

        if not cursor: #bruce 080918
            print "BUG: can't set cursor from %r -- no cached cursor so far" % (inCursor,) 
            return None
        
        # Apply modifications before setting cursor.
        # (review: also cache modified cursors as optim? Or does the subr do that? [bruce 080918 Q])
        if self.mouse_selection_lock_enabled:
            # Add the selection lock symbol.
            cursor = createCompositeCursor(cursor,
                                           self.win.selectionLockSymbol,
                                           offsetX = 2, offsetY = 19)
        return QGLWidget.setCursor(self, cursor) # review: retval used? ever not None? [bruce 080918 Q]

    # ==

    #bruce 060220 changes related to supporting self.modkeys, self.in_drag.
    # These changes are unfinished in the following ways: ###@@@
    # - need to fix the known bugs in fix_event_helper, listed below
    # - update_modkeys needs to call some sort of self.graphicsMode.updateCursor routine
    # - then the modes which update the cursor for key press/release of modkeys need to stop doing that
    #   and instead just define that updateCursor routine properly
    # - ideally we'd capture mouseEnter and call both update_modkeys and the same updateCursor routine
    # - (and once the cursor works for drags between widgets, we might as well fix the statusbar text for that too)

    modkeys = None
    in_drag = False
    button = None
    mouse_event_handler = None # None, or an object to handle mouse events and related queries instead of self.graphicsMode
        # [bruce 070405, new feature for confirmation corner support, and for any other overlay widgets which are handled
        #  mostly independently of the current mode -- and in particular which are not allowed to depend on the recent APIs
        #  added to selectMode, and/or which might need to be active even if current mode is doing xor-mode OpenGL drawing.]

    _last_event_wXwY = (-1, -1) #bruce 070626

    def fix_event(self, event, when, target): #bruce 060220 added support for self.modkeys
        """
        [For most documentation, see fix_event_helper. Argument <when> is one of 'press', 'release', or 'move'.
         We also set self.modkeys to replace the obsolete mode.modkey variable.
         This only works if we're called for all event types which want to look at that variable.]
        """
        qt4transition.qt4todo('reconcile state and stateAfter')
        # fyi: for info about event methods button and buttons (related to state and stateAfter in Qt3) see
        # http://www.riverbankcomputing.com/Docs/PyQt4/html/qmouseevent.html#button
        # [bruce 070328]
        but, mod = fix_event_helper(self, event, when, target)
            # fix_event_helper has several known bugs as of 060220, including:
            # - target is not currently used, and it's not clear what it might be for
            #   [in this method, it's self.mode ###REVIEW WHAT IT IS]
            # - it's overly bothered by dialogs that capture press and not release;
            # - maybe it can't be called for key events, but self.modkeys needs update then [might be fixed using in_drag #k];
            # - not sure it's always ok when user moves from one widget to another during a drag;
            # - confused if user releases two mouse buttons at different times to end a drag (thinks the first one ended it).
            # All these can be fixed straightforwardly when they become important enough. [bruce 060220]

        # How we'll update self.mouse_event_handler, so its new value can handle this event after we return
        # (and handle queries by update_cursor and the like, either after we return or in this same method call):
        # - press: change based on current point (event position in window coords)
        # - move: if in_drag, leave unchanged, else (bareMotion) change based on current point.
        # - release: leave unchanged (since release is part of the ongoing drag).
        # We can't do this all now, since we don't know in_drag yet,
        # nor all later, since that would be after a call of update_cursor -- except that
        # in that case, we're not changing it, so (as a kluge) we can ignore that issue
        # and do it all later.

        wX = event.pos().x()
        wY = self.height - event.pos().y()
        self._last_event_wXwY = wX, wY #bruce 070626 for use by mouse_event_handler (needed for confcorner)

        if when == 'release':
            self.in_drag = False
            self.button = None
            # leave self.mouse_event_handler unchanged, so it can process the release if it was handling the drag
            self.graphicsMode.update_cursor()
        else:
            #bruce 070328 adding some debug code/comments to this (for some Qt4 or Qt4/Mac specific bugs), and bugfixing it.
            olddrag = self.in_drag
            self.in_drag = but & (Qt.LeftButton|Qt.MidButton|Qt.RightButton) # Qt4 note: this is a PyQt4.QtCore.MouseButtons object
                # you can also use this to see which mouse buttons are involved.
                # WARNING: that would only work in Qt4 if you use the symbolic constants listed in button_names.keys().
            if not olddrag: # this test seems to still work in Qt4 (apparently MouseButtons.__nonzero__ is sensibly defined)
                #bruce 070328 revised algorithm, since PyQt evidently forgot to make MouseButtons constants work as dict keys.
                # It works now for bareMotion (None), real buttons (LMB or RMB), and simulated MMB (option+LMB).
                # In the latter case I think it fixes a bug, by displaying the rotate cursor during option+LMB drag.
                for lhs, rhs in button_names.iteritems():
                    if self.in_drag == lhs:
                        self.button = rhs
                        break
                    continue
                # Note: if two mouse buttons were pressed at the same time (I think -- bruce 070328), we leave self.button unchanged.

            if when == 'press' or (when == 'move' and not self.in_drag):
                new_meh = self.graphicsMode.mouse_event_handler_for_event_position( wX, wY)
                self.set_mouse_event_handler( new_meh) # includes update_cursor if handler is different
                pass

        self.update_modkeys(mod)
            # need to call this when drag starts; ok to call it during drag too,
            # since retval is what came from fix_event
        return but, mod

    def set_mouse_event_handler(self, mouse_event_handler): #bruce 070628 (related to fixing bug 2476 (leftover CC Done cursor))
        """
        [semi-private]
        Set self.mouse_event_handler (to a handler meeting the MouseEventHandler_API, or to None)
        and do some related updates.
        """
        if self.mouse_event_handler is not mouse_event_handler:
            self.mouse_event_handler = mouse_event_handler
            self.graphicsMode.update_cursor()
            #e more updates?
            # - maybe tell the old mouse_event_handler it's no longer active
            #   (i.e. give it a "leave event" if when == 'move')
            #   and/or tell the new one it is (i.e. give it an "enter event" if when == 'move') --
            #   not needed for now [bruce 070405]
            # - maybe do an incremental gl_update, i.e. gl_update_confcorner?
        return

    def update_modkeys(self, mod):
        """
        Call this whenever you have some modifier key flags from an event (as returned from fix_event,
        or found directly on the event as stateAfter in events not passed to fix_event).
        Exception: don't call it during a drag, except on values returned from fix_event, or bugs will occur.
        There is not yet a good way to follow this advice. This method and/or fix_event should provide one. ###e

        This method updates self.modkeys, setting it to None, 'Shift', 'Control' or 'Shift+Control'.
        (All uses of the obsolete mode.modkey variable should be replaced by this one.)
        """
        shift_control_flags = mod & (Qt.ShiftModifier | Qt.ControlModifier)
        oldmodkeys = self.modkeys
        if shift_control_flags == Qt.ShiftModifier:
            self.modkeys = 'Shift'
        elif shift_control_flags == Qt.ControlModifier:
            self.modkeys = 'Control'
        elif shift_control_flags == (Qt.ShiftModifier | Qt.ControlModifier):
            self.modkeys = 'Shift+Control'
        else:
            self.modkeys = None
        if self.modkeys != oldmodkeys:
            # This would be a good place to tell the GraphicsMode it might want to update the cursor,
            # based on all state it knows about, including self.modkeys and what the mouse is over,
            # but it's not enough, since it doesn't cover mouseEnter (or mode Enter),
            # where we need that even if modkeys didn't change. [bruce 060220]
            self.graphicsMode.update_cursor()
            highlighting_enabled = self.graphicsMode.command.isHighlightingEnabled()
            if self.selobj and highlighting_enabled:
                if self.modkeys == 'Shift+Control' or oldmodkeys == 'Shift+Control':
                    # If something is highlighted under the cursor and we just pressed or released 
                    # "Shift+Control", repaint to update its correct highlight color.
                    self.gl_update_highlight()
        return

    def begin_select_cmd(self):
        """
        #doc
        [to be called near the beginning of certain event handlers]
        """
        # Warning: same named method exists in assembly, GLPane, and ops_select, with different implems.
        # More info in comments in assembly version. [bruce 051031]
        if self.assy:
            self.assy.begin_select_cmd()
        return

    def _tripleClickTimeout(self):
        """
        [private method]

        This method is called whenever the tripleClickTimer expires.
        """
        return

    def mouseTripleClickEvent(self, event):
        """
        Triple-click event handler for the L{GLPane}.

        Code can check I{self.tripleClick} to determine if an event is a
        triple click.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}

        @see: L{ops_connected_Mixin.getConnectedAtoms()} for an example of use.
        """
        # Implementation: We start a <tripleClickTimer> (a single shot timer)
        # whenever we get a double-click mouse event, but only if there is no 
        # other active tripleClickTimer.
        # If we get another mousePressEvent() before <tripleClickTimer> expires,
        # then we consider that event a triple-click event and mousePressEvent()
        # sends the event here.
        #
        # We then set instance variable <tripleClick> to True and send the 
        # event to mouseDoubleClickEvent(). After mouseDoubleClickEvent() 
        # processes the event and returns, we reset <tripleClick> to False.
        # Code can check <tripleClick> to determine if an event is a
        # triple click.
        #
        # For an example, see ops_connected_Mixin.getConnectedAtoms()
        #
        # Note: This does not fully implement a triple-click event handler
        # (i.e. include mode.left/middle/rightTriple() methods),
        # but it does provides the guts for one. I intend to discuss this with
        # Bruce to see if it would be worth adding these mode methods.
        # Since we only need this to implement NFR 2516 (i.e. select all 
        # connected PAM5 atoms when the user triple-clicks a PAM5 atom), 
        # it isn't necessary.
        #
        # See: mouseDoubleClickEvent(), mousePressEvent(), _tripleClickTimeout()

        #print "Got TRIPLE-CLICK"
        self.tripleClick = True
        try:
            self.mouseDoubleClickEvent(event)
        finally:
            self.tripleClick = False
        return

    def mouseDoubleClickEvent(self, event):
        """
        Double-click event handler for the L{GLPane}.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        if not self.tripleClickTimer.isActive(): # See mouseTripleClickEvent(). 
            self.tripleClickTimer.start( 200 )   # 200-millisecond singleshot timer.

        # (note: mouseDoubleClickEvent and mousePressEvent share a lot of code)
        self.makeCurrent() #bruce 060129 precaution, presumably needed for same reasons as in mousePressEvent
        self.begin_select_cmd() #bruce 060129 bugfix (needed now that this can select atoms in BuildAtoms_Command)

        self.debug_event(event, 'mouseDoubleClickEvent')

        but, mod_unused = self.fix_event(event, 'press', self.graphicsMode)
        ## but = event.stateAfter()
        #k I'm guessing this event comes in place of a mousePressEvent;
        # need to test this, and especially whether a releaseEvent then comes
        # [bruce 040917 & 060124]
        ## print "Double clicked: ", but

        self.checkpoint_before_drag(event, but) #bruce 060323 for bug 1747 (caused by no Undo checkpoint for doubleclick)
            # Q. Why didn't that bug show up earlier??
            # A. guess: modelTree treeChanged signal, or (unlikely) GLPane paintGL, was providing a checkpoint
            # which made up for the 'checkpoint_after_drag' that this one makes happen (by setting self.__flag_and_begin_retval).
            # But I recently removed the checkpoint caused by treeChanged, and (unlikely cause) fiddled with code related to after_op.
            #   Now I'm thinking that checkpoint_after_drag should do one whether or not checkpoint_before_drag
            # was ever called. Maybe that would fix other bugs... but not cmenu op bugs like 1411 (or new ones the above-mentioned
            # change also caused), since in those, the checkpoint_before_drag happens, but the cmenu swallows up the
            # releaseEvent so the checkpoint_after_drag never has a chance to run. Instead, I'm fixing those by wrapping
            # _paintGL_drawing in its own begin/end checkpoints, and (unlike the obs after_op) putting them after
            # env.postevent_updates (see its call to find them). But I might do the lone-releaseEvent checkpoint too. [bruce 060323]
            # Update, 060326: reverting the _paintGL_drawing checkpointing, since it caused bug 1759 (more info there).

        handler = self.mouse_event_handler # updated by fix_event [bruce 070405]
        if handler is not None:
            handler.mouseDoubleClickEvent(event)
            return

        if but & Qt.LeftButton:
            self.graphicsMode.leftDouble(event)
        if but & Qt.MidButton:
            self.graphicsMode.middleDouble(event)
        if but & Qt.RightButton:
            self.graphicsMode.rightDouble(event)

        return

    __pressEvent = None #bruce 060124 for Undo
    __flag_and_begin_retval = None

    def checkpoint_before_drag(self, event, but): #bruce 060124; split out of caller, 060126
        if but & (Qt.LeftButton|Qt.MidButton|Qt.RightButton):
            # Do undo_checkpoint_before_command if possible.
            #
            #bruce 060124 for Undo; will need cleanup of begin-end matching with help of fix_event;
            # also, should make redraw close the begin if no releaseEvent came by then (but don't
            #  forget about recursive event processing) [done in a different way in redraw, bruce 060323]
            if self.__pressEvent is not None and debug_flags.atom_debug:
                # this happens whenever I put up a context menu in GLPane, so don't print it unless atom_debug ###@@@
                print "atom_debug: bug: pressEvent didn't get release:", self.__pressEvent
            self.__pressEvent = event
            self.__flag_and_begin_retval = None
            ##e we could simplify the following code using newer funcs external_begin_cmd_checkpoint etc in undo_manager
            if self.assy:
                begin_retval = self.assy.undo_checkpoint_before_command("(mouse)") # text was "(press)" before 060126 eve
                    # this command name should be replaced sometime during the command
                self.__flag_and_begin_retval = True, begin_retval
            pass
        return

    def mousePressEvent(self, event):
        """
        Mouse press event handler for the L{GLPane}. It dispatches mouse press
        events depending on B{Shift} and B{Control} key state.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        if self.tripleClickTimer.isActive():
            # This event is a triple-click event.
            self.mouseTripleClickEvent(event)
            return

        # (note: mouseDoubleClickEvent and mousePressEvent share a lot of code)

        self.makeCurrent()
            ## Huaicai 2/25/05. This is to fix item 2 of bug 400: make this rendering context
            ## as current, otherwise, the first event will get wrong coordinates

        self.begin_select_cmd() #bruce 051031
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            #e would using fix_event here help to avoid those "release without press" messages,
            # or fix bugs from mouse motion? or should we set some other flag to skip subsequent
            # drag/release events until the next press? [bruce 060126 questions]
            return
        ## but = event.stateAfter()
        but, mod = self.fix_event(event, 'press', self.graphicsMode)
            # Notes [bruce 070328]:
            # but = <PyQt4.QtCore.MouseButtons object at ...>,
            # mod = <PyQt4.QtCore.KeyboardModifiers object at ...>.
            # for doc on these objects see http://www.riverbankcomputing.com/Docs/PyQt4/html/qt-mousebuttons.html
            # and for info about event methods button and buttons (related to state and stateAfter in Qt3) see
            # http://www.riverbankcomputing.com/Docs/PyQt4/html/qmouseevent.html#button

        # (I hope fix_event makes sure at most one button flag remains; if not,
        #  following if/if/if should be given some elifs. ###k
        #  Note that same applies to mouseReleaseEvent; mouseMoveEvent already does if/elif.
        #  It'd be better to normalize it all in fix_event, though, in case user changes buttons
        #  without releasing them all, during the drag. Some old bug reports are about that. #e
        #  [bruce 060124-26 comment])

        self.checkpoint_before_drag(event, but)

        self.current_stereo_image = self.stereo_image_hit_by_event(event)
            # note: self.current_stereo_image will remain unchanged until the
            # next mouse press event. (Thus even drags into the other image
            # of a left/right pair will not change it.)
            ### REVIEW: even bareMotion won't change it -- will this cause
            # trouble for highlighting when the mouse crosses the boundary?
            # [bruce 080911 question]

        handler = self.mouse_event_handler # updated by fix_event [bruce 070405]
        if handler is not None:
            handler.mousePressEvent(event)
            return

        if but & Qt.LeftButton:
            if mod & Qt.ShiftModifier:
                self.graphicsMode.leftShiftDown(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.leftCntlDown(event)
            else:
                self.graphicsMode.leftDown(event)

        if but & Qt.MidButton:
            if mod & Qt.ShiftModifier and mod & Qt.ControlModifier: # mark 060228.
                self.graphicsMode.middleShiftCntlDown(event)
            elif mod & Qt.ShiftModifier:
                self.graphicsMode.middleShiftDown(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.middleCntlDown(event)
            else:
                self.graphicsMode.middleDown(event)

        if but & Qt.RightButton:
            if mod & Qt.ShiftModifier:
                self.graphicsMode.rightShiftDown(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.rightCntlDown(event)
            else:
                self.graphicsMode.rightDown(event)         

        return

    def mouseReleaseEvent(self, event):
        """
        The mouse release event handler for the L{GLPane}.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        self.debug_event(event, 'mouseReleaseEvent')
        ## but = event.state()
        but, mod = self.fix_event(event, 'release', self.graphicsMode)
        ## print "Button released: ", but

        handler = self.mouse_event_handler # updated by fix_event [bruce 070405]
        if handler is not None:
            handler.mouseReleaseEvent(event)
            self.checkpoint_after_drag(event)
            return

        try:
            if but & Qt.LeftButton:
                if mod & Qt.ShiftModifier:
                    self.graphicsMode.leftShiftUp(event)
                elif mod & Qt.ControlModifier:
                    self.graphicsMode.leftCntlUp(event)
                else:
                    self.graphicsMode.leftUp(event)

            if but & Qt.MidButton:
                if mod & Qt.ShiftModifier and mod & Qt.ControlModifier: # mark 060228.
                    self.graphicsMode.middleShiftCntlUp(event)
                elif mod & Qt.ShiftModifier:
                    self.graphicsMode.middleShiftUp(event)
                elif mod & Qt.ControlModifier:
                    self.graphicsMode.middleCntlUp(event)
                else:
                    self.graphicsMode.middleUp(event)

            if but & Qt.RightButton:
                if mod & Qt.ShiftModifier:
                    self.graphicsMode.rightShiftUp(event)
                elif mod & Qt.ControlModifier:
                    self.graphicsMode.rightCntlUp(event)
                else:
                    self.graphicsMode.rightUp(event)
        except:
            print_compact_traceback("exception in mode's mouseReleaseEvent handler (bug, ignored): ") #bruce 060126

        # piotr 080320:
        # "fast manipulation" mode where the external bonds are not displayed
        # the glpane has to be redrawn after mouse button is released
        # to show the bonds again
        #
        # this has to be moved to GlobalPreferences (this debug_pref is
        # also called in chunk.py) piotr 080325
        if debug_pref("GLPane: suppress external bonds when dragging?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True
                      ):
            self.gl_update()

        self.checkpoint_after_drag(event) #bruce 060126 moved this later, to fix bug 1384, and split it out, for clarity
        return

    def checkpoint_after_drag(self, event): #bruce 060124; split out of caller, 060126 (and called it later, to fix bug 1384)
        """
        Do undo_checkpoint_after_command(), if a prior press event did an 
        undo_checkpoint_before_command() to match.

        @note: This should only be called *after* calling the mode-specific 
               event handler for this event!
        """
        del event
        # (What if there's recursive event processing inside the event handler... when it's entered it'll end us, then begin us...
        #  so an end-checkpoint is still appropriate; not clear it should be passed same begin-retval -- most likely,
        #  the __attrs here should all be moved into env and used globally by all event handlers. I'll solve that when I get to
        #  the other forms of recursive event processing. ###@@@
        #  So for now, I'll assume recursive event processing never happens in the event handler
        #  (called just before this method is called) -- then the simplest
        #  scheme for this code is to do it all entirely after the mode's event handler (as done in this routine),
        #  rather than checking __attrs before the handlers and using the values afterwards. [bruce 060126])

        # Maybe we should simulate a pressEvent's checkpoint here, if there wasn't one, to fix hypothetical bugs from a
        # missing one. Seems like a good idea, but save it for later (maybe the next commit, maybe a bug report). [bruce 060323]

        if self.__pressEvent is not None: ###@@@ and if no buttons are still pressed, according to fix_event?
            self.__pressEvent = None
            if self.__flag_and_begin_retval:
                flagjunk, begin_retval = self.__flag_and_begin_retval
                self.__flag_and_begin_retval = None
                if self.assy:
                    #k should always be true, and same assy as before
                    # (even for file-closing cmds? I bet not, but:
                    #  - unlikely as effect of a mouse-click or drag in GLPane;
                    #  - probably no harm from these checkpoints getting into different assys
                    #  But even so, when solution is developed (elsewhere, for toolbuttons), bring it here
                    #  or (better) put it into these checkpoint methods. ###@@@)
                    self.assy.undo_checkpoint_after_command( begin_retval)
        return

    def mouseMoveEvent(self, event):
        """
        Mouse move event handler for the L{GLPane}. It dispatches mouse motion
        events depending on B{Shift} and B{Control} key state.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        ## Huaicai 8/4/05. 
        self.makeCurrent()

        ##self.debug_event(event, 'mouseMoveEvent')
        ## but = event.state()
        but, mod = self.fix_event(event, 'move', self.graphicsMode)

        handler = self.mouse_event_handler # updated by fix_event [bruce 070405]
        if handler is not None:
            handler.mouseMoveEvent(event)
            return

        if but & Qt.LeftButton:
            if mod & Qt.ShiftModifier:
                self.graphicsMode.leftShiftDrag(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.leftCntlDrag(event)
            else:
                self.graphicsMode.leftDrag(event)

        elif but & Qt.MidButton:
            if mod & Qt.ShiftModifier and mod & Qt.ControlModifier: # mark 060228.
                self.graphicsMode.middleShiftCntlDrag(event)
            elif mod & Qt.ShiftModifier:
                self.graphicsMode.middleShiftDrag(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.middleCntlDrag(event)
            else:
                self.graphicsMode.middleDrag(event)

        elif but & Qt.RightButton:
            if mod & Qt.ShiftModifier:
                self.graphicsMode.rightShiftDrag(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.rightCntlDrag(event)
            else:
                self.graphicsMode.rightDrag(event)

        else:
            self.graphicsMode.bareMotion(event)
        return

    def wheelEvent(self, event):
        """
        Mouse wheel event handler for the L{GLPane}.

        @param event: A Qt mouse wheel event.
        @type  event: U{B{QWheelEvent}<http://doc.trolltech.com/4/qwheelevent.html>}
        """
        self.debug_event(event, 'wheelEvent')
        if not self.in_drag:
            #but = event.buttons() # I think this event has no stateAfter() [bruce 060220]
            self.update_modkeys(event.modifiers()) #bruce 060220
        self.graphicsMode.Wheel(event) # mode bindings use modkeys from event; maybe this is ok?
            # Or would it be better to ignore this completely during a drag? [bruce 060220 questions]

        # russ 080527: Fix Bug 2606 (highlighting not turned on after wheel event.)
        self.wheelHighlight = True

        return


    #== Timer helper methods

    highlightTimer = None #bruce 070110 (was not needed before)

    def _timer_debug_pref(self):
        #bruce 070110 split this out and revised it
        #bruce 080129 removed non_debug and changed prefs_key
        # (so all developer settings for this will start from scratch),
        # since behavior has changed since it was first implemented
        # in a way that makes it likely that changing this will cause bugs.
        res = debug_pref("GLPane: timer interval",
                         Choice([100, 0, 5000, None]),
                         # NOTE: the default value defined here (100)
                         # determines the usual timer behavior,
                         # not just debug pref behavior.
                         ## non_debug = True,
                         prefs_key = "A10 devel/glpane timer interval"
                         )
        if res is not None and type(res) is not type(1):
            # support prefs values stored by future versions (or by a brief bug workaround which stored "None")
            res = None
        return res

    #russ 080505: Treat focusIn/focusOut events the same as enter/leave events.
    # On the Mac at least, Cmd-Tabbing to another app window that pops up on top
    # of our pane doesn't deliver a leave event, but does deliver a focusOut.
    # Unless we handle it as a leave, the timer is left active, and a highlight
    # draw can occur.  This steals the focus from the upper window, popping NE1
    # on top of it, which is very annoying to the user.
    def focusInEvent(self, event):
        if DEBUG_BAREMOTION:
            print "focusInEvent"
            pass
        self.enterEvent(event)

    def focusOutEvent(self, event):
        if DEBUG_BAREMOTION:
            print "focusOutEvent"
            pass
        self.leaveEvent(event)

    def enterEvent(self, event): # Mark 060806. [minor revisions by bruce 070110]
        """
        Event handler for when the cursor enters the GLPane.

        @param event: The mouse event after entering the GLpane.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        del event
        if DEBUG_BAREMOTION:
            print "enterEvent"
            pass
        choice = self._timer_debug_pref()
        if choice is None:
            if not env.seen_before("timer is turned off"):
                print "warning: GLPane's timer is turned off by a debug_pref"
            if self.highlightTimer:
                self.killTimer(self.highlightTimer)
                if DEBUG_BAREMOTION:
                    print "  Killed highlight timer %r"% self.highlightTimer
                    pass
                pass
            self.highlightTimer = None
            return
        if not self.highlightTimer:
            interval = int(choice)
            self.highlightTimer = self.startTimer(interval) # Milliseconds interval.
            if DEBUG_BAREMOTION:
                print "  Started highlight timer %r"% self.highlightTimer
                pass
            pass
        return

    def leaveEvent(self, event): # Mark 060806. [minor revisions by bruce 070110]
        """
        Event handler for when the cursor leaves the GLPane.

        @param event: The last mouse event before leaving the GLpane.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        del event
        if DEBUG_BAREMOTION:
            print "leaveEvent"
            pass
        # If an object is "hover highlighted", unhighlight it when leaving the GLpane.
        if self.selobj is not None:
            ## self.selobj = None # REVIEW: why not set_selobj?
            self.set_selobj(None) #bruce 080508 bugfix (turn off MT highlight)
            self.gl_update_highlight() # REVIEW: this redraw can be slow -- is it worthwhile?
            pass

        # Kill timer when the cursor leaves the GLpane.
        # It is (re)started in enterEvent() above.
        if self.highlightTimer:
            self.killTimer(self.highlightTimer)
            if DEBUG_BAREMOTION:
                print "  Killed highlight timer %r"% self.highlightTimer
                pass
            self.highlightTimer = None
            pass
        return

    def timerEvent(self, event): # Mark 060806.
        """
        When the GLpane's timer expires, a signal is generated calling this
        slot method. The timer is started in L{enterEvent()} and killed in 
        L{leaveEvent()}, so the timer is only active when the cursor is in 
        the GLpane.

        This method is part of a hover highlighting optimization and works in
        concert with mouse_exceeded_distance(), which is called from
        L{selectMode.bareMotion()}. It works by creating a 'MouseMove' event
        using the current cursor position and sending it to 
        L{mode.bareMotion()} whenever the mouse hasn't moved since the previous
        timer event.

        @see: L{enterEvent()}, L{leaveEvent()}, 
              L{selectMode.mouse_exceeded_distance()}, and 
              L{selectMode.bareMotion()}
        """
        del event
        if not self.highlightTimer or (self._timer_debug_pref() is None): #bruce 070110
            if debug_flags.atom_debug or DEBUG_BAREMOTION:
                print "note (not a bug unless happens a lot): GLPane got timerEvent but has no timer"
                    # should happen once when we turn it off or maybe when mouse leaves -- not other times, not much
            #e should we do any of the following before returning??
            return

        # Get the x, y position of the cursor and store as tuple in <xy_now>.
        cursor = self.cursor()
        cursorPos = self.mapFromGlobal(cursor.pos()) # mapFromGlobal() maps from screen coords to GLpane coords.
        xy_now = (cursorPos.x(), cursorPos.y()) # Current cursor position
        xy_last = self.timer_event_last_xy # Cursor position from last timer event.

        # If this cursor position hasn't changed since the last timer event, and no mouse button is
        # being pressed, create a 'MouseMove' mouse event and pass it to mode.bareMotion().
        # This event is intended only for eventual use in selectMode.mouse_exceeded_distance
        # by certain graphicsModes, but is sent to all graphicsModes.
        if (xy_now == xy_last and self.button == None) or self.wheelHighlight:
            # Only pass a 'MouseMove" mouse event once to bareMotion() when the mouse stops 
            # and hasn't moved since the last timer event.

            if self.triggerBareMotionEvent or self.wheelHighlight:
                #print "Calling bareMotion. xy_now = ", xy_now
                mouseEvent = QMouseEvent( QEvent.MouseMove, cursorPos, Qt.NoButton, Qt.NoButton, Qt.NoModifier)
                                #Qt.NoButton & Qt.MouseButtonMask,
                                #Qt.NoButton & Qt.KeyButtonMask )
                if DEBUG_BAREMOTION:
                    #bruce 080129 re highlighting bug 2606 reported by Paul
                    print "debug fyi: calling %r.bareMotion with fake zero-motion event" % (self.graphicsMode,)

                # russ 080527: Fix Bug 2606 (highlighting not turned on after wheel event.)
                # Keep generating fake zero-motion events until one is handled rather than discarded.
                discarded = self.graphicsMode.bareMotion(mouseEvent)
                if not discarded:
                    self.triggerBareMotionEvent = False
                    self.wheelHighlight = False

            # The cursor hasn't moved since the last timer event. See if we should display the tooltip now.
            # REVIEW:
            # - is it really necessary to call this 10x/second?
            # - Does doing so waste significant cpu time?
            # [bruce 080129 questions]
            helpEvent = QHelpEvent(QEvent.ToolTip, QPoint(cursorPos), QPoint(cursor.pos()) )
            if self.dynamicToolTip: # Probably always True. Mark 060818.
                self.dynamicToolTip.maybeTip(helpEvent) # maybeTip() is responsible for displaying the tooltip.

        else:

            self.cursorMotionlessStartTime = time.time()
                # Reset the cursor motionless start time to "zero" (now).
                # Used by maybeTip() to support the display of dynamic tooltips.

            self.triggerBareMotionEvent = True

        self.timer_event_last_xy = xy_now
        return

    #== end of Timer helper methods

    def mousepoints(self, event, just_beyond = 0.0):
        """
        @return: a pair (2-tuple) of points (Numeric arrays of x,y,z in model
                 coordinates) that lie under the mouse pointer. The first point
                 lies at (or just beyond) the near clipping plane; the other
                 point lies in the plane of the center of view.
        @rtype: (point, point)

        @param just_beyond: how far beyond the near clipping plane
                            the first point should lie. Default value of 0.0
                            means on the near plane; 1.0 would mean on the
                            far plane. Callers often pass 0.01 for this.
                            Some callers pass this positionally, and some as
                            a keyword argument.
        @type just_beyond: float

        If stereo is enabled, self.current_stereo_image determines which
        stereo image's coordinate system is used to get the mousepoints
        (even if the mouse pointer is not inside that image now).
        (Note that self.current_stereo_image is set (by other code in self)
        based on the mouse position in each mouse press event. It's not affected
        by mouse position in mouse drag, release, or bareMotion events.)
        """
        x = event.pos().x()
        y = self.height - event.pos().y()
        
        # modify modelview matrix in side-by-side stereo view modes [piotr 080529]
        # REVIEW: does no_clipping disable enough? especially in anaglyph mode,
        # we might want to disable even more side effects, for efficiency.
        # [bruce 080912 comment]
        self._enable_stereo(self.current_stereo_image, no_clipping = True)

        p1 = A(gluUnProject(x, y, just_beyond))
        p2 = A(gluUnProject(x, y, 1.0))

        self._disable_stereo()

        los = self.lineOfSight

        k = dot(los, -self.pov - p1) / dot(los, p2 - p1)

        p2 = p1 + k*(p2-p1)
        return (p1, p2)

    def SaveMouse(self, event):
        """
        Extracts the mouse position from event and saves it in the I{MousePos}
        property. (localizes the API-specific code for extracting the info)

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        self.MousePos = V(event.pos().x(), event.pos().y())

    def dragstart_using_GL_DEPTH(self, 
                                 event, 
                                 more_info = False,
                                 always_use_center_of_view = False): #bruce 061206 added more_info option
        """
        Use the OpenGL depth buffer pixel at the coordinates of event
        (which works correctly only if the proper GL context (of self) is current -- caller is responsible for this)
        to guess the 3D point that was visually clicked on.
        If that was too far away to be correct, use a point under the mouse and in the plane of the center of view.
           By default, return (False, point) when point came from the depth buffer, or (True, point) when point came from the
        plane of the center of view. Callers should typically do further sanity checks on point and the "farQ" flag (the first
        value in the returned tuple),
        perhaps replacing point with an object's center, projected onto the mousepoints line, if point is an unrealistic
        dragpoint for the object which will be dragged. [#e there should be a canned routine for doing that to our retval]
           If the optional flag more_info is true, then return a larger tuple (whose first two members are the same as in the
        2-tuple we return by default). The larger tuple is (farQ, point, wX, wY, depth, farZ) where wX, wY are the OpenGL window
        coordinates of event within self (note that Y is 0 on the bottom, unlike in Qt window coordinates; glpane.height minus
        wY gives the Qt window coordinate of the event), and depth is the current depth buffer value at the position of the event --
        larger values are deeper; 0.0 is the nearest possible value; depths of farZ or greater are considered "background",
        even though they might be less than 1.0 due to drawing of a background rectangle. (In the current implementation,
        farZ is always GL_FAR_Z, a public global constant defined in constants.py, but in principle it might depend on the
        GLPane and/or vary with differently drawn frames.)
        @param always_use_center_of_view: If True it always uses the depth of the
             center of view (returned by self.mousepoints) . This is used by
             Line_GraphicsMode.leftDown(). 

        """
        #@NOTE: Argument  always_use_center_of_view added on April 20, 2008 to 
        #fix a bug for Mark's Demo.
        #at FNANO08 -- This was the bug: In CPK display style,, start drawing 
        #a duplex,. When the rubberbandline draws 20 basepairs, move the cursor 
        #just over the last sphere drawn and click to finish duplex creation
        #Switch the view to left view -- the duplex axis is not vertical 

        wX = event.pos().x()
        wY = self.height - event.pos().y()
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        depth = wZ[0][0]
        farZ = GL_FAR_Z

        if depth >= farZ or always_use_center_of_view:
            junk, point = self.mousepoints(event)
            farQ = True
        else:
            point = A(gluUnProject(wX, wY, depth))
            farQ = False

        if more_info:
            return farQ, point, wX, wY, depth, farZ
        return farQ, point

    def dragstart_using_plane_depth(self, 
                                    event, 
                                    plane = None,
                                    planeAxis = None,
                                    planePoint = None ):
        """
        Returns the 3D point on a specified plane, at the coordinates of event
              
        @param plane: The point is computed such that it lies on this Plane 
                      at the given event coordinates. 
                     
        @see: Line_GraphicsMode.leftDown()
        @see: InsertDna_GraphicsMode.
        
        @TODO: There will be some cases where the intersection of the mouseray 
        and the given plane is not possible or returns a very large number.
        Need to discuss this. 
        """
                
        # TODO: refactor this so the caller extracts Plane attributes,
        # and this method only receives geometric parameters (more general).
        # [bruce 080912 comment]
        
        #First compute the intersection point of the mouseray with the plane        
        p1, p2     = self.mousepoints(event)
        linePoint  = p2
        lineVector = norm(p2 - p1)
        
        if plane is not None:
            planeAxis  = plane.getaxis()
            planeNorm  = norm(planeAxis)        
            planePoint = plane.center        
        else:
            assert not (planeAxis is None or planePoint is None)
            planeNorm = norm(planeAxis)              
            
        
        #Find out intersection of the mouseray with the plane. 
        intersection = planeXline(planePoint, planeNorm, linePoint, lineVector)
        if intersection is None:
            intersection =  ptonline(planePoint, linePoint, lineVector)

        point = intersection

        return point

    def rescale_around_point(self, factor, point = None): #bruce 060829; 070402 moved user prefs functionality into caller
        """
        Rescale around point (or center of view == - self.pov, if point is not supplied),
        by multiplying self.scale by factor (and shifting center of view if point is supplied).
           Note: factor < 1 means zooming in, since self.scale is the model distance from screen center
        to edge in plane of center of view.
           Note: not affected by zoom in vs. zoom out, or by user prefs.
        For that, see callers such as basicMode.rescale_around_point_re_user_prefs.
           Note that point need not be in the plane of the center of view, and if it's not, the depth
        of the center of view will change. If callers wish to avoid this, they can project point onto
        the plane of the center of view.
        """
        self.gl_update() #bruce 070402 precaution
        self.scale *= factor
            ###e The scale variable needs to set a limit, otherwise, it will set self.near = self.far = 0.0
            ###  because of machine precision, which will cause OpenGL Error. [needed but NIM] [Huaicai comment 10/18/04]
            # [I'm not sure that comment is still correct -- nothing is actually changing self.near and self.far.
            #  But it may be referring to the numbers made from them and fed to the glu projection routines;
            #  if so, it might still apply. [bruce 060829]]
        # Now use point, so that it, not center of view, gets preserved in screen x,y position and "apparent depth" (between near/far).
        # Method: we're going to move point, in eyespace, relative to center of view (aka cov == -self.pov)
        # from oldscale * (point - cov) to newscale * (point - cov), in units of oldscale (since we're in them now),
        # so we're moving it by (factor - 1) * (point - cov), so translate back, by moving cov the other way (why the other way??):
        # cov -= (factor - 1) * (point - cov). I think this will work the same in ortho and perspective, and can ignore self.quat.
        # Test shows that works; but I don't yet understand why I needed to move cov in the opposite direction as I assumed.
        # But I worry about whether it will work if more than one Wheel event occurs between redraws (which rewrite depth buffer).
        # [bruce 060829]
        if point is not None:
            self.pov += (factor - 1) * (point - (-self.pov))
        return

    pass

# end

