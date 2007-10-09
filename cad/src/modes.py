# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
modes.py -- provides basicMode, the superclass for all modes.

$Id$

History:


Originally written by Josh.


Partly rewritten by Bruce 040922-040924. In particular, I changed how
subclasses for specific modes relate to their superclass, basicMode,
and to their glpane object; I also split the part of class GLPane
which interfaces to the modes into a mixin class, modeMixin (since
then moved into its own file), and extensively revised it.

The old mode methods setMode, Done, and Flush have been renamed to
_enterMode, Done, and Cancel, and these are now only implemented in
basicMode; mode-specific subclasses override specific methods they
call (listed below) rather than those methods themselves. The code
that used to be in the mode-specific overrides of those methods has
been divided up as follows:

Code for entering a specific mode (which used to be in the mode's
setMode method) is now in the methods Enter and init_gui (in the
mode-specific subclass). From the glpane, this is reached via
basicMode._enterMode, called by methods from the glpane's modeMixin.

(Note, init_gui and restore_gui were called show_toolbars and
hide_toolbars before Mark ca. 041004.)

Code for Cancelling a mode (which used to be in the mode's Flush
method) is now divided between the methods haveNontrivialState,
StateCancel, restore_gui, restore_patches, and clear.  Most of these
methods are also used by Cancel. The glpane's modeMixin reaches it via
basicMode.Cancel.

(For specialized uses there is a new related way to reach some of the
Cancelling code, basicMode.Abandon.  It's only used for error
situations that might occur but which external code does not yet
handle correctly; hopefully it can go away when problems in that
external code (e.g. file opening, when current mode has some state)
are fixed. BTW I described these problems in some other comment; I
don't know for sure they're real.)

Code for leaving a mode via Done is now divided between mode-specific
methods haveNontrivialState, StateDone, restore_gui, restore_patches,
and clear. Most of these methods are also used by Done.  The glpane's
modeMixin reaches it via basicMode.Done, as before.

See the method docstrings in this file for details.

A good example for new modes (since it overrides a lot of the subclass
methods) is cookieMode.  But there are few enough modes that you might
as well look at them all.


bruce 050507 moved Hydrogenate and Dehydrogenate into another file

bruce 071009 moved modeMixin into its own file
"""

import math # just for pi
import sys
from Numeric import exp
from Numeric import dot

from PyQt4.Qt import Qt
from PyQt4.Qt import QMenu, QCursor, QToolButton

from OpenGL.GL import GL_FALSE
from OpenGL.GL import glColorMask
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import glReadPixelsf
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glSelectBuffer
from OpenGL.GL import GL_SELECT
from OpenGL.GL import glRenderMode
from OpenGL.GL import glInitNames
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_CLIP_PLANE0
from OpenGL.GL import glClipPlane
from OpenGL.GL import glEnable
from OpenGL.GL import glDisable
from OpenGL.GL import glPopMatrix
from OpenGL.GL import GL_RENDER
from OpenGL.GL import glFlush

from OpenGL.GLU import gluUnProject

from VQT import V, Q, A, vlen, norm, planeXline, ptonline
import drawer

from debug import print_compact_traceback

import platform
from PlatformDependent import shift_name
from PlatformDependent import control_name
from PlatformDependent import context_menu_prefix

import env
from state_utils import StateMixin
from shape import get_selCurve_color

from constants import noop
from constants import SELSHAPE_RECT
from constants import SUBTRACT_FROM_SELECTION
from constants import ADD_TO_SELECTION
from prefs_constants import zoomAboutScreenCenter_prefs_key
from prefs_constants import displayOriginAxis_prefs_key
from prefs_constants import displayOriginAsSmallAxis_prefs_key
from prefs_constants import displayPOVAxis_prefs_key

from Utility import Group
from chem import Atom
from bonds import Bond
from Utility import Node
from jigs import Jig

import time


class anyMode(object, StateMixin): #bruce 060223 renamed mixin class; 071008 added object superclass
    "abstract superclass for all mode objects"
    
    # default values for mode-object attributes.  external code
    # assumes every mode has these attributes, but it should pretend
    # they're read-only; mode-related code (in this file) can override
    # them in subclasses and/or instances, and modify them directly.
    
    # internal name of mode, e.g. 'DEPOSIT',
    # only seen by users in "debug" error messages
    modename = "(bug: missing modename 1)" 
    # name of mode to be shown to users, as a phrase, e.g. 'sketch mode'
    msg_modename = "(bug: unknown mode)"
    
    # Mode's property manager. Subclasses should initialize the propMgr object 
    # if they need one.     
    propMgr = None
    
    def get_mode_status_text(self):
        return "(bug: mode status text)"
    # I think this will never be shown [bruce 040927]

    # (default methods that should be noops in both nullMode and basicMode can be put here instead if desired)
    
    def selobj_highlight_color(self, selobj): #bruce 050612 added this to mode API; see depositMode version for docstring
        return None

    def selobj_still_ok(self, selobj): #bruce 050702 added this to mode API; overridden in basicMode, and docstring is there
        return True

    def mouse_event_handler_for_event_position(self, wX, wY): #bruce 070405
        return None

    def draw_overlay(self): #bruce 070405
        return

    def update_cursor(self): #bruce 070410
        return

    def selection_changed(self): #bruce 070925
        return
    
    def model_changed(self): #bruce 070925
        return

    def state_may_have_changed(self): #bruce 070925
        return

    def isCurrentCommand(self): #bruce 071008
        return False

    def drawHighlightedObjectUnderMouse(self, glpane, selobj, hicolor): #bruce 071008
        pass
    
    pass # end of class anyMode


class nullMode(anyMode):
    """do-nothing mode (for internal use only) to avoid crashes
    in case of certain bugs during transition between modes"""
    # (this mode is not put into the glpane's modetab)
    modename = 'nullMode'
    msg_modename = 'nullMode'
        # this will be overwritten when modes are changing [bruce 050106]
    # needs no __init__ method; constructor takes no arguments
    
    
    def noop_method(self, *args, **kws):
        if platform.atom_debug:
            print "fyi: atom_debug: nullMode noop method called -- probably ok; ignored"
        return None #e print a warning?
    def __getattr__(self, attr): # in class nullMode (not inherited by other mode classes)
        if not attr.startswith('_'):
            if platform.atom_debug:
                print "fyi: atom_debug: nullMode.__getattr__(%r) -- probably ok; returned noop method" % attr
            return self.noop_method
        else:
            raise AttributeError, attr #e args?
    def Draw(self):
        # this happens... is that ok? note: see
        # "self.start_using_mode( '$DEFAULT_MODE')" below -- that
        # might be the cause.  if so, it's ok that it happens and good
        # that we turn it into a noop. [bruce 040924]
        pass
    def Draw_after_highlighting(self):
        pass
    def keyPressEvent(self, e):
        pass
    def keyReleaseEvent(self, e):
        pass
    def bareMotion(self, e):
        pass
    def Done(self, *args, **kws): #bruce 060316 added this to remove frequent harmless debug print
        pass
    render_scene = None #bruce 070406; this tells GLPane to use default method,
        # but removes the harmless debug print for missing nullMode attr
    compass_moved_in_from_corner = False  #bruce 070406
    pass # end of class nullMode ##e maybe needs to have some other specific methods?


class basicMode(anyMode):
    """Subclass this class to provide a new mode of interaction for the GLPane.
    """
    
    # Subclasses should define the following class constants,
    # and normally need no __init__ method.
    # If they have an __init__ method, it must call basicMode.__init__.
    modename = "(bug: missing modename)"
    msg_modename = "(bug: unknown mode)"
    default_mode_status_text = "(bug: missing mode status text)"
    #Initialize clock time during a wheel event to None. Its value is assigned 
    #in self.wheelEvent. This time is used to decide whether to highlight 
    #object under cursor. I.e. when user is scrolling the wheel to zoom in or
    #out, and at the same time the mouse moves slightly, we want to make sure 
    #that the object is not highlighted.See selectMolsMode.bareMotion for an 
    #example. 
    timeAtLastWheelEvent = None
    
    def user_modename(self): #bruce 051130 (apparently this is new; it can be the official user-visible-modename method for now)
        "Return a string such as 'Move Mode' or 'Build Mode' -- the name of this mode for users; or '' if unknown."
        if self.default_mode_status_text.startswith("Mode: "):
            return self.default_mode_status_text[len("Mode: "):] + " Mode"
        if self.default_mode_status_text.startswith("Tool: "): 
            # Added for Pan, Rotate and Zoom Tools. Fixes bug 1298. mark 060323
            return self.default_mode_status_text[len("Tool: "):] + " Tool"
        return ''
    
    def __init__(self, glpane):
        """This is called at least once, per type of mode (i.e. per
           specific basicMode subclass), per glpane instance, but can
           be called more often; in fact, it's called once per new
           assembly, since the modes store the assembly internally.
           It sets up that mode to be available (but not yet active)
           in that glpane.
        """
        
        self.pw = None # pw = part window
        
        # init or verify modename and msg_modename
        name = self.modename
        assert not name.startswith('('), \
            "bug: modename class constant missing from subclass %s" % self.__class__.__name__
        if self.msg_modename.startswith('('):
            self.msg_modename = name[0:1].upper() + name[1:].lower() + ' Mode'
                # Capitalized 'Mode'. Fixes bug 612. mark 060323
                # [bruce 050106 capitalized first letter above]
            if 0: # bruce 040923 never mind this suggestion
                print "fyi: it might be better to define 'msg_modename = %r' as a class constant in %s" % \
                  (self.msg_modename, self.__class__.__name__)
        # check whether subclasses override methods we don't want them to
        # (after this works I might remove it, we'll see)
        ####@@@@ bruce 050130 removing 'Done' temporarily; see PanMode.Done for why.
        # later note: as of 070521, we always get warned "subclass movieMode overrides basicMode._exitMode".
        # I am not sure whether this override is legitimate so I'm not removing the warning for now. [bruce 070521]
        weird_to_override = ['Cancel', 'Flush', 'StartOver', 'Restart',
                             'userSetMode', '_exitMode', 'Abandon', '_cleanup']
            # not 'modifyTransmute', 'keyPress', they are normal to override;
            # not 'draw_selection_curve', 'Wheel', they are none of my business;
            # not 'makemenu' since no relation to new mode changes per se.
            # [bruce 040924]
        for attr in weird_to_override:
            def same_method(m1,m2):
                # m1/m2.im_class will differ (it's the class of the query,
                # not where func is defined), so only test im_func
                return m1.im_func == m2.im_func
            if not same_method( getattr(self,attr) , getattr(basicMode,attr) ):
                print "fyi (for developers): subclass %s overrides basicMode.%s; this is deprecated after mode changes of 040924." % \
                      (self.__class__.__name__, attr)

        # other inits
        self.glpane = glpane
        self.win = glpane.win
        # this doesn't work, since when self is first created during GLPane creation,
        # self.win doesn't yet have this attribute:
        ## self.commandSequencer = self.win.commandSequencer #bruce 070108
        # (note that the exception from this is not very understandable.)
        # So instead, we define a property that does this alias, below.
        
        # Note: the attributes self.o and self.w are deprecated, but often used.
        # New code should use some other attribute, such as self.glpane or
        # self.commandSequencer or self.win, as appropriate. [bruce 070613, 071008]
        self.o = self.glpane
        self.w = self.win
        
        ## self.init_prefs() # no longer needed --
        # Between Alpha 1-8, each mode had its own background color and display mode.
        # For Alpha 9, background color and display mode attrs were moved to the GLPane class where they
        # are global for all modes.
        
        # store ourselves in our glpane's mode table, modetab
        ###REVIEW whether this is used for anything except changing to new mode by name [bruce 070613 comment]
        self.o.modetab[self.modename] = self
            # bruce comment 040922: current code can overwrite a prior
            # instance of same mode, when setassy called, eg for file
            # open; this might (or might not) cause some bugs; i
            # should fix this but didn't yet do so as of 040923
            ###REVIEW whether this is still an issue, or newly one [bruce 070613 comment]

        self.setup_menus_in_init()

        return # from basicMode.__init__

    def get_commandSequencer(self):
        return self.win.commandSequencer #bruce 070108
    
    commandSequencer = property(get_commandSequencer)
    
    def isCurrentCommand(self): #bruce 071008, for Command API
        """
        Return a boolean to indicate whether self is the currently active command.
        Note: this is False even if self is temporarily suspended by e.g. Pan Tool,
        but self's UI is still fully displayed; this needs to be considered when
        this method is used to determine whether UI actions should have an effect.
        """
        return self.commandSequencer.currentCommand is self

    def set_cmdname(self, name): # mark 060220.
        '''Helper method for setting the cmdname to be used by Undo/Redo.
        '''
        self.o.assy.current_command_info(cmdname = name)
        
    #bruce 050416 revised makeMenus-related methods to permit "dynamic context menus",
    # then revised them again 050420 to fix bug 554 which this introduced.

    call_makeMenus_for_each_event = False # default value of class attribute; subclasses can override
    
    def setup_menus_in_init(self):
        if not self.call_makeMenus_for_each_event:
            self.setup_menus( )

    def setup_menus_in_each_cmenu_event(self):
        if self.call_makeMenus_for_each_event:
            self.setup_menus( )

    def setup_menus(self): # rewritten by bruce 041103; slight changes 050416, 050420
        "call self.makeMenus(), postprocess the menu_spec attrs it sets, and turn them into self.Menu1 etc"
        mod_attrs = ['Menu_spec_shift', 'Menu_spec_control']
        all_attrs = ['Menu_spec'] + mod_attrs + ['debug_Menu_spec']
        # delete any Menu_spec attrs previously set (needed when call_makeMenus_for_each_event is true)
        for attr in all_attrs + ['Menu1','Menu2','Menu3']:
            if hasattr(self, attr):
                del self.__dict__[attr]
        #bruce 050416: give it a default menu; for modes we have now, this won't ever be seen unless there are bugs
        #bruce 060407 update: improve the text, re bug 1739 comment #3, since it's now visible for zoom/pan/rotate tools
        self.Menu_spec = [("%s" % self.user_modename(), noop, 'disabled')]
        self.makeMenus() # bruce 040923 moved this here, from the subclasses; for most modes, it replaces self.Menu_spec
        # bruce 041103 changed details of what self.makeMenus() should do
        for attr in ['Menu1','Menu2','Menu3']:
            assert not hasattr(self, attr), \
                "obsolete menu attr should not be defined: %r.%s" % (self, attr)
        # makeMenus should have set self.Menu_spec, and maybe some sister attrs
        assert hasattr(self, 'Menu_spec'), "%r.makeMenus() failed to set up" \
               " self.Menu_spec (to be a menu spec list)" % self # should never happen after 050416
        orig_Menu_spec = list(self.Menu_spec)
            # save a copy for comparisons, before we modify it
        # define the ones not defined by makeMenus;
        # make them all unique lists by copying them,
        # to avoid trouble when we modify them later.
        for attr in mod_attrs:
            if not hasattr(self, attr):
                setattr(self, attr, list(self.Menu_spec))
                # note: spec should be a list (which is copyable)
        for attr in ['debug_Menu_spec']:
            if not hasattr(self, attr):
                setattr(self, attr, [])
        for attr in ['Menu_spec']:
            setattr(self, attr, list(getattr(self, attr)))
        if platform.atom_debug and self.debug_Menu_spec:
            # put the debug items into the main menu
            self.Menu_spec.extend( [None] + self.debug_Menu_spec )
            # [note, bruce 050914, re bug 971: for modes that don't remake their menus on each use,
            #  the user who turns on ATOM-DEBUG won't see the menu items defined by debug_Menu_spec
            #  until they remake all mode objects by opening a new file. This might change if we remake mode objects
            #  more often (like whenever the mode is entered), but the best fix would be to remake all menus on each use.
            #  But this requires review of the menu-spec making code for each mode (for correctness when run often),
            #  so for now, it has to be enabled per-mode by setting self.call_makeMenus_for_each_event for that mode.
            #  It's worth doing this in the modes that define self.debug_Menu_spec.]
        
        # new feature, bruce 041103:
        # add submenus to Menu_spec for each modifier-key menu which is
        # nonempty and different than Menu_spec
        # (was prototyped in extrudeMode.py, bruce 041010]
        doit = []
        for attr, modkeyname in [
                ('Menu_spec_shift', shift_name()),
                ('Menu_spec_control', control_name()) ]:
            submenu_spec = getattr(self,attr)
            if orig_Menu_spec != submenu_spec and submenu_spec:
                doit.append( (modkeyname, submenu_spec) )
        if doit:
            self.Menu_spec.append(None)
            for modkeyname, submenu_spec in doit:
                itemtext = '%s-%s Menu' % (context_menu_prefix(), modkeyname)
                self.Menu_spec.append( (itemtext, submenu_spec) )
            # note: use platform.py functions so names work on Mac or non-Mac,
            # e.g. "Control-Shift Menu" vs. "Right-Shift Menu",
            # or   "Control-Command Menu" vs. "Right-Control Menu".
            # [bruce 041014]
        if isinstance( self.o.selobj, Jig): # NFR 1740. mark 060322
            from wiki_help import wiki_help_menuspec_for_object
            ms = wiki_help_menuspec_for_object( self.o.selobj )
            if ms:
                self.Menu_spec.append( None )
                self.Menu_spec.extend( ms )
        else:
            featurename = self.user_modename()
            if featurename:
                from wiki_help import wiki_help_menuspec_for_featurename
                ms = wiki_help_menuspec_for_featurename( featurename )
                if ms:
                    self.Menu_spec.append( None ) # there's a bug in this separator, for cookiemode...
                    # might this look better before the above submenus, with no separator?
                    ## self.Menu_spec.append( ("web help: " + self.user_modename(), self.menucmd_open_wiki_help_page) )
                    self.Menu_spec.extend( ms )
        self.Menu1 = QMenu()
        self.makemenu(self.Menu_spec, self.Menu1)
        self.Menu2 = QMenu()
        self.makemenu(self.Menu_spec_shift, self.Menu2)
        self.Menu3 = QMenu()
        self.makemenu(self.Menu_spec_control, self.Menu3)

    def makeMenus(self):
        """[Subclasses can override this to assign menu_spec lists (describing
        the context menus they want to have) to self.Menu_specs (and related attributes).
        Depending on a class constant call_makeMenus_for_each_event (default False),
        this will be called once during init (default behavior) or on every mousedown
        that needs to put up a context menu (useful for "dynamic context menus").]
        """
        pass ###e move the default menu_spec to here in case subclasses want to use it?

    # ==

    # confirmation corner methods [bruce 070405-070409, 070627]

    # Note: if we extend the conf. corner to "generators" in the short term,
    # before the "command sequencer" is implemented, some of the following methods
    # may be revised to delegate to the "current generator" or its PM.
    # If so, when doing this, note that many modes currently act as their own PM widget.

    def _KLUGE_current_PM(self): #bruce 070627
        "private, and a kluge; see KLUGE_current_PropertyManager docstring for more info"
        pw = self.w.activePartWindow()
        if not pw:
            # I don't know if pw can be None
            print "fyi: _KLUGE_current_PM sees pw of None" ###
            return None
        try:
            res = pw.KLUGE_current_PropertyManager()
            # print "debug note: _KLUGE_current_PM returns %r" % (res,)
            return res
        except:
            # I don't know if this can happen
            print_compact_traceback("ignoring exception in %r.KLUGE_current_PropertyManager(): " % (pw,))
            return None
        pass

    def _KLUGE_visible_PM_buttons(self): #bruce 070627
        """private (but ok for use by self._ccinstance), and a kluge:
        return the Done and Cancel QToolButtons of the current PM,
        if they are visible, or None for each one that is not visible.
           Used both for deciding what CC buttons to show, and for acting on the buttons
        (assuming they are QToolButtons).
        """
        pm = self._KLUGE_current_PM()
        if not pm:
            return None, None # no CC if no PM is visible
        def examine(buttonname):
            try:
                button = getattr(pm, buttonname)
                assert button
                assert isinstance(button, QToolButton)
                vis = button.isVisibleTo(pm)
                    # note: we use isVisibleTo(pm) rather than isVisible(),
                    # as part of fixing bug 2523 [bruce 070829]
                if vis:
                    res = button
                else:
                    res = None
            except:
                print_compact_traceback("ignoring exception (%r): " % buttonname)
                res = None
            return res
        return ( examine('done_btn'), examine('abort_btn') )

    def want_confirmation_corner_type(self):
        """Subclasses should return the type of confirmation corner they currently want,
        typically computed from their current state. The return value can be one of the
        strings 'Done+Cancel' or 'Done' or 'Cancel', or None (for no conf. corner).
        Later we may add another possible value, 'Exit'.
        [See confirmation_corner.py for related info.]
        [Many subclasses will need to override this; we might also revise the default
         to be computed in a more often correct manner.]
        """
        # What we do:
        # find the current PM (self or an active generator, at the moment -- very klugy),
        # and ask which of these buttons are visible to it (rather than using self.haveNontrivialState()):
        #   pm.done_btn.isVisibleTo(pm)
        #   pm.abort_btn.isVisibleTo(pm).
        # WE also use them to perform the actions (they are QToolButtons). KLUGE: we do this in
        # other code which finds them again redundantly (calling the same kluge helper function).
        from debug_prefs import debug_pref, Choice_boolean_False
        if debug_pref("Conf corner test: use haveNontrivialState", Choice_boolean_False, prefs_key = True):
            # old code, works, but not correct for default mode or when generators active
            if self.haveNontrivialState():
                return 'Done+Cancel'
            else:
                # when would we just return 'Cancel'? only for a generator?
                return 'Done' # in future this will sometimes or always be 'Exit'
        else:
            done_button_vis, cancel_button_vis = self._KLUGE_visible_PM_buttons()
                # each one is either None, or a QToolButton (a true value) currently displayed on the current PM

            res = []
            if done_button_vis:
                res.append('Done')
            if cancel_button_vis:
                res.append('Cancel')
            if not res:
                res = None
            else:
                res = '+'.join(res)
            # print "want cc got", res
            return res
        pass
            
    _ccinstance = None
    
    def draw_overlay(self): #bruce 070405, revised 070627
        "called from GLPane with same drawing coordsys as for model [part of GLPane's drawing interface to modes]"
        # conf corner is enabled by default for A9.1 (070627); requires exprs module and Python Imaging Library
        from debug_prefs import debug_pref, Choice_boolean_True
        if not debug_pref("Enable confirmation corner?", Choice_boolean_True, prefs_key = True):
            return 
        # figure out what kind of confirmation corner we want, and draw it
        import confirmation_corner
        cctype = self.want_confirmation_corner_type()
        self._ccinstance = confirmation_corner.find_or_make(cctype, self)
            # Notes:
            # - we might use an instance cached in self (in an attr private to that helper function);
            # - this might be as specific as both args passed above, or as shared as one instance
            #   for the entire app -- that's up to it;
            # - if one instance is shared for multiple cctypes, it might store the cctype passed above
            #   as a side effect of find_or_make;
            # - self._ccinstance might be None.
        if self._ccinstance is not None:
            # it's an instance we want to draw, and to keep around for mouse event handling
            self._ccinstance.draw()
        return

    def mouse_event_handler_for_event_position(self, wX, wY): #bruce 070405
        """Some mouse events should be handled by special "overlay" widgets
        (e.g. confirmation corner buttons) rather than by the GLPane & mode's
        usual event handling functions. This mode API method is called by the
        GLPane to determine whether a given mouse position (in OpenGL-style
        window coordinates, 0,0 at bottom left) lies over such an overlay widget.
           Its return value is saved in glpane.mouse_event_handler -- a public
        fact, which can be depended on by mode methods such as update_cursor --
        and should be None or an object that obeys the MouseEventHandler interface.
        (Note that modes themselves don't (currently) provide that interface --
        they get their mouse events from GLPane in a more-digested way than that
        interface supplies.)
           Note that this method is not called for all mouse events -- whether
        it's called depends on the event type (and perhaps modkeys). The caller's
        policy as of 070405 (fyi) is that the mouse event handler is not changed
        during a drag, even if the drag goes off the overlay widget, but it is
        changed during bareMotion if the mouse goes on or off of one. But that
        policy is the caller's business, not self's.
           [Subclasses should override this if they show extra or nonstandard
        overlay widgets, but as of the initial implem (070405), that's not likely
        to be needed.]
        """
        if self._ccinstance is not None:
            method = getattr(self._ccinstance, 'want_event_position', None)
            if method:
                if method(wX, wY):
                    return self._ccinstance
            elif platform.atom_debug:
                print "atom_debug: fyi: ccinstance %r with no want_event_position method" % (self._ccinstance,)
        return None

    # ==
    
    def warning(self, *args, **kws):
        self.o.warning(*args, **kws)

    # entering this mode
    
    def _enterMode(self, resuming = False): #bruce 070813 added resuming option, 
        
        """Private method (called only by our glpane) -- immediately
           enter this mode, i.e. prepare it for use, not worrying at
           all about any prior current mode.  Return something false
           (e.g. None) normally, or something true if you want to
           refuse entry to the new mode (see comments in the call to
           this for why you might want to do that).  Note that the
           calling glpane has not yet set its self.mode to point to us
           when it calls this method, and it will never do so unless
           we return something false (as we usually do).  Should not
           be overridden by subclasses.
           
           [by bruce 040922; see head comment of this file for how
           this relates to previous code]

           @param resuming: whether we're resuming this mode (after a completed
                            subcommand); otherwise we're entering it as if anew.
                            This is for use by Subcommands resuming their parent
                            commands.
           @type resuming: bool
        """
        if not resuming:
            refused = self.refuseEnter(warn = 1)
            if not refused:
                # do mode-specific entry initialization;
                # this method is still allowed to refuse, as well
                refused = self.Enter() 
                if refused:
                    print "fyi: late refusal by %r, better if it had been in refuseEnter" % self # (but sometimes it might be necessary)
        else:
            refused = False
        if not refused:
            self.init_gui() ###FIX: perhaps use resume_gui instead, if resuming -- or pass that option.
            self.update_gui() # see also UpdateDashboard
            self.update_mode_status_text()
        # caller (our glpane) will set its self.mode to point to us,
        # but only if we return false
        return refused

    def refuseEnter(self, warn):
        """Subclasses should override this: examine the current
           selection state of your glpane, and anything else you care
           about, and decide whether you would refuse to become the
           new current mode, if asked to. If you would refuse, and if
           warn = true, then emit an error message explaining this.
           In any case, return whether you refuse entry (i.e. true if
           you do, false if you don't).           
           [by bruce 040922. I expect no existing modes to override
           this, but extrude and revolve probably will.]           
        """
        return 0
    
    def Enter(self):
        # bruce 040922 split each subclass setMode into Enter and init_gui
        # -- see file head comment for details
        """Subclasses should override this: first call basicMode.Enter(self).
           Then set whatever internal state you need to upon being entered,
           modify settings in your glpane (self.o) if necessary,
           and return None.           
           If something goes wrong, so that you don't accept being the
           new current mode, emit an error message explaining why
           (perhaps in a dialog or status bar), and return True -- but
           it's better if you can figure this out earlier, in
           refuseEnter().           
           [by bruce 040922; see head comment of this file for how
           this relates to previous code]           
        """
        self.UpdateDashboard() # Added to hide Done button for Default mode. Mark 050922.
        self.picking = False
        self.update_cursor()
        return None

    def init_gui(self):
        # bruce 041124 clarified docstring, revised illegitimate calls.
        """Subclasses should define this to set up UI stuff like dashboards,
        cursors, toggle icons, etc.
           It should be called only once each time the mode is entered.
        Therefore, it should not be called by other code (for that,
        see UpdateDashboard()), nor defined by modes to do things that
        need redoing many times per mode-entry (for that, see
        update_gui()).
        """
        pass

    def update_gui(self): # bruce 041124
        """Subclasses should define this to update their dashboard to reflect state
        that might have changed in the rest of the program, e.g. selection state
        in the model tree. Not intended to be called directly by external code;
        for that, see UpdateDashboard().
        """
        pass

    def UpdateDashboard(self): # bruce 041124
        """Public method, meant to be called only on the current mode object:
           Make sure this mode's dashboard is updated before the processing of
        the current user event is finished.
           External code that might change things which some modes
        need to reflect in their dashboard should call this one or more times
        after any such changes, before the end of the same user event.
           Multiple calls per event are ok (but in the initial implem might
        be slow). Subclasses should not override this; for that, see update_gui().
        """
        # For now, this method just updates the dashboard immediately.
        # This might be too slow if it's called many times per event, so someday
        # we might split this into separate invalidation and update code;
        # this will then be the invalidation routine, in spite of the name.
        # We *don't* also call update_mode_status_text -- that's separate.
        
        # This shows the Done button on the dashboard unless the current mode is the 
        # Default mode. Resolves bug #958 and #959. Mark 050922.
        import UserPrefs
        if self.modename == UserPrefs.default_modename(): #bruce 060403 revised this
            self.w.toolsDoneAction.setVisible(0)
        else:
            self.w.toolsDoneAction.setVisible(1)
        
        if self.now_using_this_mode_object(): #bruce 050122 added this condition
            self.update_gui()
        return

    def now_using_this_mode_object(self): #bruce 050122 moved this here from extrudeMode.py
        """Return true if the glpane is presently using this mode object
        (not just a mode object with the same name!)
           Useful in "slot methods" that receive Qt signals from a dashboard
        to reject signals that are meant for a newer mode object of the same class,
        in case the old mode didn't disconnect those signals from its own methods
        (as it ideally should do).
           Warning: this returns false while a mode is still being entered (i.e.
        during the calls of Enter and init_gui, and the first call of update_gui).
        But it's not a good idea to rely on that behavior -- if you do, you should
        redefine this function to guarantee it, and add suitable comments near the
        places which *could* set self.o.mode to the mode object being entered,
        earlier than they do now.
        """
        return self.o.mode == self
        
    def update_mode_status_text(self):        
        """##### new method, bruce 040927; here is my guess at its doc
           [maybe already obs?]: Update the mode-status widget to show
           the currently correct mode-status text for this mode.
           Subclasses should not override this; its main purpose is to
           know how to do this in the environment of any mode.  This
           is called by the standard mode-entering code when it's sure
           we're entering a new mode, and whenever it suspects the
           correct status text might have changed (e.g. after certain
           user events #nim).  It can also be called by modes
           themselves when they think the correct text might have
           changed.  To actually *specify* that text, they should do
           whatever they need to do (which might differ for each mode)
           to change the value which would be returned by their
           mode-specific method get_mode_status_text().           
        """
        self.w.update_mode_status( mode_obj = self)
            # fyi: this gets the text from self.get_mode_status_text();
            # mode_obj = self is needed in case glpane.mode == nullMode
            #  at the moment.

    def selection_changed(self): #bruce 070925 added this to mode/command API
        """
        Subclasses should extend this (or make sure their self.propMgr defines
        it) to check whether any selection state has changed that should be
        reflected in their UI, and if so, update their UI accordingly.
        It will be called at most approximately once per user mouse or key
        event. The calling code should try not to call it when not needed,
        but needn't guarantee this, so implementations should try to be fast
        when the call was not needed.
           Model state or other selection state should NOT be updated by
        this method -- doing so may cause bugs of a variety of kinds,
        for example in the division of changes into undoable commands
        or in the consistency of state which requires update calls after
        it's changed.
           See also update_gui; this method is typically implemented
        more efficiently and called much more widely, and (together with
        similar new methods for other kinds of state) should eventually
        replace update_gui.
        """
        ### REVIEW: Decide whether highlighting (selobj) is covered by it (guess yes -- all kinds of selection).
        ### maybe TODO: call when entering/resuming the mode, and say so, and document order of call
        # relative to update_gui. And deprecate update_gui or make it more efficient.
        # And add other methods that only use usage-tracked state and are only called as needed.
        if self.propMgr:
            if hasattr( self.propMgr, 'selection_changed'):
                self.propMgr.selection_changed()
        return

    def model_changed(self): #bruce 070925 added this to mode/command API
        """
        Subclasses should extend this (or make sure their self.propMgr defines
        it) to check whether any model state has changed that should be
        reflected in their UI, and if so, update their UI accordingly.
           Model state or selection state should NOT be updated by
        this method.
           See selection_changed docstring for more info.
        """
        ### maybe TODO: same as for selection_changed.
        if self.propMgr:
            if hasattr( self.propMgr, 'model_changed'):
                self.propMgr.model_changed()
        return

    def state_may_have_changed(self): #bruce 070925 added this to mode/command API
        """
        Call model_changed and/or selection_changed as needed, in that order.
        Not normally overridden by subclasses [I hope].
        Called by env.do_post_event_updates.
        """
        ### TODO: call each method only when needed, using assy change counters, and maybe a selobj test.
        self.model_changed()
        self.selection_changed()
        return
    
    def get_mode_status_text(self):        
        """##### new method, bruce 040927; doc is tentative [maybe
           already obs?]; btw this overrides an AnyMode method:        
           Return the correct text to show right now in the
           mode-status widget (e.g."Mode: Build",
           "Mode: Select Chunks").           
           The default implementation is suitable for modes in which this
           text never varies, assuming they properly define the class
           constant default_mode_status_text; other modes will need to
           override this method to compute that text in the correct way,
           and will *also* need to ensure that their update_mode_status_text()
           method is called
           whenever the correct mode status text might have changed,
           if it might not be called often enough by default.           
           [### but how often it's called by default is not yet known
           -- e.g. if we do it after every button or menu event, maybe no
           special calls should be needed... we'll see.]            
        """
        return self.default_mode_status_text

    # methods for changing to some other mode
    
    def userSetMode(self, modename, **options):        
        """User has asked to change to the given modename; we might or
           might not permit this, depending on our own state.  If we
           permit it, do it; if not, show an appropriate error
           message.  Exception: if we're already in that mode, do
           nothing.           
           [bruce 040922]
        """
        if self.modename == modename:
            if self.o.mode == self:
                # changing from the active mode to itself -- do nothing
                # (special case, not equivalent to behavior without it)
                return
            else:
                # I don't think this can happen, but if it does,
                #it's either a bug or we're some fake mode like nullMode. #k
                print "fyi (for developers): self.modename == modename but not self.o.mode == self (probably ok)" ###
                # now change modes in the normal way
        # bruce 041007 removing code for warning about changes and requiring
        # explicit Done or Cancel if self.haveNontrivialState()
        self.Done( modename, **options)
        return

    # methods for leaving this mode (from a dashboard tool or an
    # internal request).

    # Notes on state-accumulating modes, e.g. cookie extrude revolve
    # deposit [bruce 040923]:
    #
    # Each mode which accumulates state, meant to be put into its
    # glpane's assembly in the end, decides how much to put in as it
    # goes -- that part needs to be "undone" (removed from the
    # assembly) to support a Cancel event -- versus how much to retain
    # internally -- that part needs to be "done" (put into in the
    # assembly) upon a Done event.  (BTW, as I write this, I think
    # that only depositMode (so far) puts any state into the assembly
    # before it's Done.)
    #
    # Both kinds of state (stored in the mode or in the assembly)
    # should be considered when overriding self.haveNontrivialState()
    # -- it should say whether Done and Cancel should have different
    # ultimate effects. (Note "should" rather than "would" --
    # i.e. even if Cancel does not yet work, like in depositMode,
    # haveNontrivialState should return True based on what Cancel
    # ought to do, not based on what it actually does. That way the
    # user won't miss a warning message saying that Cancel doesn't
    # work yet.)
    #
    # StateDone should actually put the unsaved state from here into
    # the assembly; StateCancel should remove the state which was
    # already put into the assembly by this mode's operation (but only
    # since the last time it was entered). Either of those can also
    # emit an error message and return True to refuse to do the
    # requested operation of Done or Cancel (they normally return
    # None).  If they return True, we assume they made no changes to
    # the stored state, in the mode or in the assembly (but we have no
    # way of enforcing that; bugs are likely if they get this wrong).
    #
    # I believe that exactly one of StateDone and StateCancel will be
    # called, for any way of leaving a mode, except for Abandon, if
    # self.haveNontrivialState() returns true; if it returns false,
    # neither of them will be called.
    #
    # -- bruce 040923

    def Done(self, new_mode = None, suspend_old_mode = False, **new_mode_options):
        """Done tool in dashboard; also called internally (in
           userSetMode and elsewhere) if user asks to start a new mode
           and current mode decides that's ok, without needing an
           explicit Done.  Change [bruce 040922]: Should not be
           overridden in subclasses; instead they should override
           haveNontrivialState and/or StateDone and/or StateCancel as
           appropriate.
        """
        if not suspend_old_mode:
            if self.haveNontrivialState(): # use this (tho it should be just an optim), to make sure it's not giving false negatives
                refused = self.StateDone()
                if refused:
                    # subclass says not to honor the Done request (and it already emitted an appropriate message)
                    return
        new_mode_options['suspend_old_mode'] = suspend_old_mode
        self._exitMode( new_mode, **new_mode_options)
        return

    def StateDone(self):
        """Mode objects (e.g. cookieMode) which might have accumulated
           state which is not yet put into the model (their glpane's
           assembly) should override this StateDone method to put that
           state into the model, and return None.  If, however, for
           some reason they want to refuse to let the user's Done
           event be honored, they should instead (not changing the
           model) emit an error message and return True.
        """
        assert 0, "bug: mode subclass %r needs custom StateDone method, since its haveNontrivialState() apparently returned True" % \
               self.__class__.__name__
    
    def Cancel(self, new_mode = None, **new_mode_options):
        """Cancel tool in dashboard; might also be called internally
           (but is not as of 040922, I think).  Change [bruce 040922]:
           Should not be overridden in subclasses; instead they should
           override haveNontrivialState and/or StateDone and/or
           StateCancel as appropriate.
        """
        ###REVIEW: any need to support suspend_old_mode here? I doubt it...
        # but maybe complain if it's passed. [bruce 070814]
        if self.haveNontrivialState():
            refused = self.StateCancel()
            if refused:
                # subclass says not to honor the Cancel request (and it already emitted an appropriate message)
                return
        self._exitMode( new_mode, **new_mode_options)

    def StateCancel(self):
        """Mode objects (e.g. depositMode) which might have
           accumulated state directly into the model (their glpane's
           assembly) should override this StateCancel method to undo
           those changes in the model, and return None.
           Alternatively, if they are unable to remove that state from
           the model (e.g. if that code is not yet implemented, or too
           hard to implement correctly), they should warn the user,
           and then either leave all state unchanged (in mode object
           and model) and return True (to refuse to honor the user's
           Cancel request), or go ahead and leave the unwanted state
           in the model, and return None (which honors the Cancel but
           leaves the user with unwanted new state in the model).
           Perhaps, when they warn the user, they would ask which of
           those two things to do.
        """
        return None # this is correct for all existing modes except depositMode
                    # -- bruce 040923
        ## assert 0, "bug: mode subclass %r needs custom StateCancel method, since its haveNontrivialState() apparently returned True" % \
        ##       self.__class__.__name__

    def haveNontrivialState(self):
        """Subclasses which accumulate state (either in the mode
           object or in their glpane's assembly, or both) should
           override this appropriately (see long comment above for
           details).  False positive is annoying, but permitted (its
           only harm is forcing the user to explicitly Cancel or Done
           when switching directly into some other mode); but false
           negative would be a bug, and would cause lost state after
           Done or (for some modes) incorrectly
           uncancelled/un-warned-about state after Cancel.
        """
        return False
    
    def _exitMode(self, new_mode = None, suspend_old_mode = False, **new_mode_options):
        """Internal method -- immediately leave this mode, discarding
           any internal state it might have without checking whether
           that's ok (if that check might be needed, we assume it
           already happened).  Ask our glpane to change to new_mode
           (which might be a modename or a mode object or None), if provided
           (and if that mode accepts being the new mode), otherwise to
           its default mode.  Unlikely to be overridden by subclasses.
           [by bruce 040922]
        """
        if not suspend_old_mode:
            self._cleanup()
        if new_mode is None:
            new_mode = '$DEFAULT_MODE'
        self.o.start_using_mode(new_mode, **new_mode_options)
            ## REVIEW: is suspend_old_mode needed in start_using_mode?
            # Tentative conclusion: its only effect would be how to fall back
            # if using the new mode fails -- it would make us fall back to
            # old mode rather than to default mode. Ideally we'd use a
            # continuation-like style, wrapping new_mode with a fallback
            # mode, and pass that as new_mode. So it's not worth fixing this
            # for now -- save it for when we have a real command-sequencer.
            # [bruce 070814 comment]
        return

    def Abandon(self):
        """This is only used when we are forced to Cancel, whether or not this
           is ok (with the user) to do now -- someday it should never be called.
           Basically, every call of this is by definition a bug -- but
           one that can't be fixed in the mode-related code alone.
           [But it would be easy to fix in the file-opening code, once we
           agree on how.]
        """
        if self.haveNontrivialState():
            msg = "%s with changes is being forced to abandon those changes!\n" \
                  "Sorry, no choice for now." % (self.msg_modename,)
            self.o.warning( msg, bother_user_with_dialog = 1 )
        # don't do self._exitMode(), since it sets a new mode and
        #ultimately asks glpane to update for that... which is
        #premature now.  #e should we extend _exitMode to accept
        #modenames of 'nullMode', and not update? also 'default'?
        #probably not...
        self._cleanup()

    def _cleanup(self):
        # (the following are probably only called together, but it's
        # good to split up their effects as documented in case we
        # someday call them separately, and also just for code
        # clarity. -- bruce 040923)
        self.o.stop_sending_us_events( self)
            # stop receiving events from our glpane (i.e. use nullMode)
        self.restore_gui()
        self.w.setFocus() #bruce 041010 bugfix (needed in two places)
            # (I think that was needed to prevent key events from being sent to
            #  no-longer-shown mode dashboards. [bruce 041220])
        self.restore_patches()
        self.clear() # clear our internal state, if any
        
    def restore_gui(self):
        "subclasses use this to restore UI stuff like dashboards, cursors, toggle icons, etc."
        pass

    def restore_patches(self):
        """subclasses should restore anything they temporarily
        modified in client objects (such as display modes in their
        glpane)"""
        pass
    
    def clear(self):
        """subclasses with internal state should reset it to null
        values (somewhat redundant with Enter; best to clear things
        now)"""
        pass
        
    # [bruce comment 040923]
    
    # The preceding and following methods, StartOver Cancel Backup
    # Done, handle the common tools on the dashboards.  (Before
    # 040923, Cancel was called Flush and StartOver was called
    # Restart. Now the internal names match the user-visible names.)
    #
    # Each dashboard uses instances of the same tools, for a uniform
    # look and action; the tool itself does not know which mode it
    # belongs to -- its action just calls glpane.mode.method for the
    # current glpane and for one of the specified methods (or Flush,
    # the old name of Cancel, until we fix MWSemantics).
    #
    # Of these methods, Done and Cancel should never be customized
    # directly -- rather, subclasses for specific modes should
    # override some of the methods they call, as described in this
    # file's header comment.
    #
    # StartOver should also never be customized, since the generic
    # method here should always work.
    #
    # For Backup, I [bruce 040923] have not yet revised it in any
    # way. Some subclasses override it, but AFAIK mostly don't do so
    # properly yet.

    # other dashboard tools
    
    def StartOver(self):
        # it looks like only cookieMode tried to do this [bruce 040923];
        # now we do it generically here [bruce 040924]
        """Start Over tool in dashboard (used to be called Restart);
        subclasses should NOT override this"""
        self.Cancel(new_mode = self.modename)
#### works, but has wrong error message when nim in sketch mode -- fix later

    def Backup(self):
        # it looks like only cookieMode tries to do this [bruce 040923]
        "Backup tool in dashboard; subclasses should override this"
        print "%s: Backup not implemented yet" % self.msg_modename

    # compatibility methods -- remove these after we fix
    # MWSemantics.py for their new names
    
    def Flush(self):
        self.Cancel() # let old name work for now

    def Restart(self):
        self.StartOver() # let old name work for now

    # ...
    
    def Draw(self):
        """Generic Draw method, with drawing code common to all modes.
           Specific modes should call this somewhere within their own Draw method,
           unless they have a good reason not to. Note: it doesn't draw the model,
           since not all modes want to always draw it.
        """
                
        # Draw the Origin axis.
        if env.prefs[displayOriginAxis_prefs_key]:
            if env.prefs[displayOriginAsSmallAxis_prefs_key]: #ninad060920
                drawer.drawOriginAsSmallAxis(self.o.scale, (0.0,0.0,0.0))
                #ninad060921: note: we are also drawing a dotted origin displayed only when 
                #the solid origin is hidden. See def standard_repaint_0 in GLPane.py
                #ninad060922 passing self.o.scale makes sure that the origin / pov axes are not zoomable
            else:
                drawer.drawaxes(self.o.scale, (0.0,0.0,0.0), coloraxes=True)
            
        if env.prefs[displayPOVAxis_prefs_key]:
            drawer.drawaxes(self.o.scale, -self.o.pov)
        
        # Draw the Point of View axis unless it is at the origin (0,0,0) AND draw origin as cross wire is true ninad060920
        if env.prefs[displayPOVAxis_prefs_key]:
            if not env.prefs[displayOriginAsSmallAxis_prefs_key]:
                if vlen(self.o.pov):
                    drawer.drawaxes(self.o.scale, -self.o.pov)
                else:
                    # POV is at the origin (0,0,0).  Draw it if the Origin axis is not drawn. Fixes bug 735.
                    if not env.prefs[displayOriginAxis_prefs_key]:
                        drawer.drawaxes(self.o.scale, -self.o.pov)
            else:
                drawer.drawaxes(self.o.scale, -self.o.pov)
		                
            
        # bruce 040929/041103 debug code -- for developers who enable this
        # feature, check for bugs in atom.picked and mol.picked for everything
        # in the assembly; print and fix violations. (This might be slow, which
        # is why we don't turn it on by default for regular users.)
        if platform.atom_debug:
            self.o.assy.checkpicked(always_print = 0)
        return

    def _drawESPImage(self, grp, pickCheckOnly):
        '''Draw any member in the Group <grp> if it is an ESP Image. Not consider the order
           of ESP Image objects'''
        from jigs_planes import ESPImage
       
        anythingDrawn = False
    
        try:
            if isinstance(grp, ESPImage):
                anythingDrawn = True
                grp.pickCheckOnly = pickCheckOnly
                grp.draw(self.o, self.o.displayMode)
            elif isinstance(grp, Group):    
                for ob in grp.members[:]:
                    if isinstance(ob, ESPImage):
                        anythingDrawn = True
                        ob.pickCheckOnly = pickCheckOnly
                        ob.draw(self.o, self.o.displayMode)
                    elif isinstance(ob, Group):
                        self._drawESPImage(ob, pickCheckOnly)
                #k Do they actually use dispdef? I know some of them sometimes circumvent it (i.e. look directly at outermost one).
                #e I might like to get them to honor it, and generalize dispdef into "drawing preferences".
                # Or it might be easier for drawing prefs to be separately pushed and popped in the glpane itself...
                # we have to worry about things which are drawn before or after main drawing loop --
                # they might need to figure out their dispdef (and coords) specially, or store them during first pass
                # (like renderpass.py egcode does when it stores modelview matrix for transparent objects).
                # [bruce 050615 comments]
            return anythingDrawn
        except:
            print_compact_traceback("exception in drawing some Group member; skipping to end: ")
            ###k return value?
        pass
    
    def Draw_after_highlighting(self, pickCheckOnly=False): #bruce 050610
        """Do more drawing, after the main drawing code has completed its highlighting/stenciling for selobj.
        Caller will leave glstate in standard form for Draw. Implems are free to turn off depth buffer read or write
        (but must restore standard glstate when done, as for mode.Draw() method).
        Warning: anything implems do to depth or stencil buffers will affect the standard selobj-check in bareMotion
        (presently only used in depositMode).
        [New method in mode API as of bruce 050610. General form not yet defined -- just a hack for Build mode's
         water surface. Could be used for transparent drawing in general.]
        """
        return self._drawESPImage(self.o.assy.part.topnode, pickCheckOnly)
    
    def selobj_still_ok(self, selobj): #bruce 050702 added this to mode API; revised 060724
        """Say whether a highlighted mouseover object from a prior draw (in the same mode) is still ok.
        If the mode's special cases don't hold, we ask the selobj; if that doesn't work, we assume it
        defines .killed (and answer yes unless it's been killed).
        [overrides anyMode method; subclasses might want to override this one]
        """
        try:
            # This sequence of conditionals fix bugs 1648 and 1676. mark 060315.
            # [revised by bruce 060724 -- merged in selobj.killed() condition, dated 050702,
            #  which was part of fix 1 of 2 redundant fixes for bug 716 (both fixes are desirable)]
            if isinstance(selobj, Atom):
                return not selobj.killed() and selobj.molecule.part is self.o.part
            elif isinstance(selobj, Bond):
                return not selobj.killed() and selobj.atom1.molecule.part is self.o.part
            elif isinstance(selobj, Node): # Jig
                return not selobj.killed() and selobj.part is self.o.part
            else:
                #bruce 060724 new feature, related to Drawable API
                try:
                    method = selobj.selobj_still_ok
                except AttributeError:
                    pass
                else:
                    res = method(self.o) # this method would need to compare glpane.part to something in selobj
                        ##e it might be better to require selobj's to return a part, compare that here,
                        # then call this for further conditions
                    if res is None:
                        print "likely bug: %r.selobj_still_ok(glpane) returned None, "\
                              "should return boolean (missing return statement?)" % (selobj,)
                    return res
            if platform.atom_debug:
                print "debug: selobj_still_ok doesn't recognize %r, assuming ok" % (selobj,)
            return True
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: ignoring exception: ")
            return True # let the selobj remain
        pass

    def drawHighlightedObjectUnderMouse(self, glpane, selobj, hicolor): #bruce 071008 for graphics mode API
        """
        Subclasses should override this as needed, though most don't need to:
        
        Draw selobj in highlighted form for being the object under the mouse,
        as appropriate to this graphics mode.
        [TODO: document this properly: Use hicolor as its color
        if you return sensible colors from method XXX.]

        Note: selobj is typically glpane.selobj, but don't assume this.
        """
        selobj.draw_in_abs_coords(glpane, hicolor)
    
    # left mouse button actions -- overridden in modes that respond to them
    def leftDown(self, event):
        pass
    
    def leftDrag(self, event):
        pass
    
    def leftUp(self, event):
        pass
    
    def leftShiftDown(self, event):
        pass
    
    def leftShiftDrag(self, event):
        pass
    
    def leftShiftUp(self, event):
        pass
    
    def leftCntlDown(self, event):
        pass
    
    def leftCntlDrag(self, event):
        pass
    
    def leftCntlUp(self, event):
        pass
    
    def leftDouble(self, event):
        pass

    # middle mouse button actions -- these support a trackball, and
    # are the same for all modes (with a few exceptions)
    def middleDown(self, event):
        """Set up for rotating the view with MMB+Drag.
        """
        self.update_cursor()
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = True
        
        # Turn off hover highlighting while rotating the view with middle mouse button. Fixes bug 1657. Mark 060805.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.

    def middleDrag(self, event):
        """ Rotate the view with MMB+Drag.
        """
        # Huaicai 4/12/05: Originally 'self.picking=0 in both middle*Down
        # and middle*Drag methods. Change it as it is now is to prevent 
        # possible similar bug that happened in the modifyMode where 
        # a *Drag method is called before a *Down() method. This 
        # comment applies to all three *Down/*Drag/*Up methods.
        if not self.picking: return
        
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1])
        self.o.quat += q
        self.o.gl_update()
 
    def middleUp(self, event):
        self.picking = False
        self.update_cursor()

    def dragstart_using_GL_DEPTH(self, event, **kws):
        """Use the OpenGL depth buffer pixel at the coordinates of event
        (which works correctly only if the proper GL context, self.o, is current -- caller is responsible for this)
        to guess the 3D point that was visually clicked on. See GLPane version's docstring for details.
        """
        res = self.o.dragstart_using_GL_DEPTH(event, **kws) # note: res is a tuple whose length depends on **kws
        return res

    def middleShiftDown(self, event):
        """Set up for panning the view with MMB+Shift+Drag.
        """
        self.update_cursor()
        # Setup pan operation
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
            #bruce 060316 replaced equivalent old code with this new method
        self.startpt = self.movingPoint # Used in leftDrag() to compute move offset during drag op.
        
        self.o.SaveMouse(event) #k still needed?? probably yes; might even be useful to help dragto for atoms #e [bruce 060316 comment]
        self.picking = True
        
        # Turn off hover highlighting while panning the view with middle mouse button. Fixes bug 1657. Mark 060808.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.
        
    def middleShiftDown_OBS(self, event):
        self.w.OldCursor = QCursor(self.o.cursor())
        # save copy of current cursor in OldCursor
        self.o.setCursor(self.w.MoveCursor) # load MoveCursor in glpane
        
        self.o.SaveMouse(event)
        self.picking = False

    def dragto(self, point, event, perp = None): #bruce 060316 moving this from selectMode to basicMode and using it more widely
        """Return the point to which we should drag the given point,
        if event is the drag-motion event and we want to drag the point
        parallel to the screen (or perpendicular to the given direction "perp"
        if one is passed in), keeping the point visibly touching the mouse cursor hotspot.
           (This is only correct for extended objects if 'point' (as passed in, and as retval is used)
        is the point on the object surface which was clicked on (not e.g. the center).
        For example, dragto(a.posn(),...) is incorrect code, unless the user happened to
        start the drag with a mousedown right over the center of atom <a>. See jigDrag
        in some subclasses for an example of correct usage.)
        """
        #bruce 041123 split this from two methods, and bugfixed to make dragging
        # parallel to screen. (I don't know if there was a bug report for that.)
        # Should be moved into modes.py and used in modifyMode too. [doing that, 060316]
        p1, p2 = self.o.mousepoints(event)
        if perp is None:
            perp = self.o.out
        point2 = planeXline(point, perp, p1, norm(p2-p1)) # args are (ppt, pv, lpt, lv)
        if point2 is None:
            # should never happen (unless a bad choice of perp is passed in),
            # but use old code as a last resort (it makes sense, and might even be equivalent for default perp)
            if env.debug(): #bruce 060316 added debug print; it should remain indefinitely if we rarely see it
                print "debug: fyi: dragto planeXline failed, fallback to ptonline", point, perp, p1, p2
            point2 = ptonline(point, p1, norm(p2-p1))
        return point2

    def dragto_with_offset(self, point, event, offset): #bruce 060316 for bug 1474
        """Convenience wrapper for dragto:
        Use this to drag objects by points other than their centers,
        when the calling code prefers to think only about the center positions
        (or some other reference position for the object).
        Arguments:
        - <point> should be the current center (or other reference) point of the object.
        - The return value will be a new position for the same reference point as <point> comes from
          (which the caller should move the object to match, perhaps subject to drag-constraints).
        - <event> should be an event whose .pos().x() and .pos.y() supply window coordinates for the mouse
        - <offset> should be a vector (fixed throughout the drag) from the center of the object
          to the actual dragpoint (i.e. to the point in 3d space which should appear to be gripped by the mouse,
          usually the 3d position of a pixel which was drawn when drawing the object
          and which was under the mousedown which started the drag).
        By convention, modes can store self.drag_offset in leftDown and pass it as <offset>.
        Note: we're not designed for objects which rotate while being dragged, as in e.g. dragSinglets,
        though using this routine for them might work better than nothing (untested ##k). In such cases
        it might be better to pass a different <offset> each time (not sure), but the only perfect
        solution is likely to involve custom code which is fully aware of how the object's
        center and its dragpoint differ, and of how the offset between them rotates as the object does.
        """
        return self.dragto(point + offset, event) - offset
    
    def middleShiftDrag(self, event):
        """Pan view with MMB+Shift+Drag. 
        Move point of view so that the model appears to follow the cursor on the screen.
        """
        point = self.dragto( self.movingPoint, event) #bruce 060316 replaced old code with dragto (equivalent)
        self.o.pov += point - self.movingPoint
        self.o.gl_update()
        
    def middleShiftDrag_OBS(self, event):
        """Move point of view so that objects appear to follow
        the mouse on the screen.
        """
        if not self.picking: return
        
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        #move = self.o.quat.unrot(self.o.scale * deltaMouse/(h*0.5))
        
        # bruce comment 040908, about josh code: 'move' is mouse
        # motion in model coords. We want center of view, -self.pov,
        # to move in opposite direction as mouse, so that after
        # recentering view on that point, objects have moved with
        # mouse.
        
        ### Huaicai 1/26/05: delta Xe, delta Ye  depend on Ze, here
        ### Ze is just an estimate, so Xe and Ye are estimates too, but
        ### they seems more accurate than before. To accurately 
        ### calculate it, we need to find a depth value for a point on 
        ### the model.
        Ze = 2.0*self.o.near*self.o.far*self.o.scale/(self.o.near+self.o.far)
        tY = (self.o.zoomFactor*Ze)*2.0/h
        
        move = self.o.quat.unrot(deltaMouse*tY)
        self.o.pov += move
        self.o.gl_update()
        self.o.SaveMouse(event)
        
    
    def middleShiftUp(self, event):
        self.picking = 0
        self.update_cursor()
    
    def middleCntlDown(self, event):
        """Set up for rotating view around POV axis with MMB+Cntl+Drag.
        """
        self.update_cursor()
        self.o.SaveMouse(event)
        self.Zorg = self.o.MousePos
        self.Zq = Q(self.o.quat)
        self.Zpov = self.o.pov
        self.picking = 1
        
        # Turn off hover highlighting while rotating the view with middle mouse button. Mark 060808.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.
    
    def middleCntlDrag(self, event):
        """Rotate around the point of view (POV) axis
        """
        if not self.picking: return
        
        self.o.SaveMouse(event)
        dx,dy = (self.o.MousePos - self.Zorg) * V(1,-1)

        self.o.pov = self.Zpov

        w=self.o.width+0.0
        self.o.quat = self.Zq + Q(V(0,0,1),2*math.pi*dx/w)
 
        self.o.gl_update()
        
    def middleCntlUp(self, event):
        self.picking = 0
        self.update_cursor()
        
    def middleShiftCntlDown(self, event): # mark 060228.
        """ Set up zooming POV in/out
        """
        self.middleCntlDown(event)
        
    def middleShiftCntlDrag(self, event):
        """Zoom (push/pull) point of view (POV) away/nearer
        """
        if not self.picking: return
        
        self.o.SaveMouse(event)
        dx,dy = (self.o.MousePos - self.Zorg) * V(1,-1)
        self.o.quat = Q(self.Zq)
        h=self.o.height+0.0
        self.o.pov = self.Zpov-self.o.out*(2.0*dy/h)*self.o.scale
 
        self.o.gl_update()
        
    def middleShiftCntlUp(self, event):
        self.picking = 0
        self.update_cursor()

    def middleCntlDrag_OBS(self, event):
        """push scene away (mouse goes up) or pull (down)
           rotate around vertical axis (left-right)
        """
        if not self.picking: return
        
        self.o.SaveMouse(event)
        dx,dy = (self.o.MousePos - self.Zorg) * V(1,-1)
        ax,ay = abs(V(dx,dy))
        if self.Zunlocked:
            self.Zunlocked = ax<10 and ay<10
            if ax>ay:
                # rotating
                self.o.setCursor(self.w.RotateZCursor)
                # load RotateZCursor in glpane
                self.o.pov = self.Zpov
                self.ZRot = 1
            else:
                # zooming
                self.o.setCursor(self.w.ZoomCursor)
                # load ZoomCursor in glpane
                self.o.quat = Q(self.Zq)
                self.ZRot = 0
        if self.ZRot:
            w=self.o.width+0.0
            self.o.quat = self.Zq + Q(V(0,0,1),2*math.pi*dx/w)
        else:
            h=self.o.height+0.0
            self.o.pov = self.Zpov-self.o.out*(2.0*dy/h)*self.o.scale
 
        self.o.gl_update()

    def middleDouble(self, event):
        pass

# removed by bruce 041217, having been added by bruce a few days before:
##    def middleDouble(self, event): # overrides the one just above!
##        """ End the current mode """
##        self.Done()
##        return
##        # bruce 041214 put this in, since I recall we agreed to make this work
##        # for all modes (on a conference call months ago). If I'm wrong, you
##        # can remove it. (We also agreed to make leftDouble NOT do this, except
##        # in modifyMode, and it looks like that might be implemented properly,
##        # but I have not reviewed that in detail, or changed it, today.)

    # right button actions... #doc
    
    def rightDown(self, event):
        self.setup_menus_in_each_cmenu_event()
        self.Menu1.exec_(event.globalPos())
        #ninad061009: Qpopupmenu in qt3 is  QMenu in Qt4
	#apparently QMenu._exec does not take option int indexAtPoint.
        # [bruce 041104 comment:] Huaicai says that menu.popup and menu.exec_
        # differ in that menu.popup returns immediately, whereas menu.exec_
        # returns after the menu is dismissed. What matters most for us is whether
        # the callable in the menu item is called (and returns) just before
        # menu.exec_ returns, or just after (outside of all event processing).
        # I would guess "just before", in which case we have to worry about order
        # of side effects for any code we run after calling exec_, since in
        # general, our Qt event processing functions assume they are called purely
        # sequentially. I also don't know for sure whether the rightUp() method
        # would be called by Qt during or after the exec_ call. If any of this
        # ever matters, we need to test it. Meanwhile, exec_ is probably best
        # for context menus, provided we run no code in the same method after it
        # returns, nor in the corresponding mouseUp() method, whose order we don't
        # yet know. (Or at least I don't yet know.)
        #  With either method (popup or exec_), the menu stays up if you just
        # click rather than drag (which I don't like); this might be fixable in
        # the corresponding mouseup methods, but that requires worrying about the
        # above-described issues.
    
    def rightDrag(self, event):
        pass
    
    def rightUp(self, event):
        pass
    
    def rightShiftDown(self, event):
        self.setup_menus_in_each_cmenu_event()
        # Previously we did this:
        # self.Menu2.exec_(event.globalPos(),3)
        # where 3 specified the 4th? action in the list. The exec_ method now
        # needs a pointer to the action itself, not a numerical index. The only
        # ways I can see to do that is with lots of bookkeeping, or if the menu
        # had a listOfActions method. This isn't important enough for the former
        # and Qt does not give us the latter. So forget about the 3.
        self.Menu2.exec_(event.globalPos())

                
    def rightShiftDrag(self, event):
        pass
    
    def rightShiftUp(self, event):
        pass
    
    def rightCntlDown(self, event):
        self.setup_menus_in_each_cmenu_event()
        # see note above
        self.Menu3.exec_(event.globalPos())
        
    def rightCntlDrag(self, event):
        pass
    
    def rightCntlUp(self, event):
        pass
    
    def rightDouble(self, event):
        pass

    # other events
    
    def bareMotion(self, event):
        pass

    def Wheel(self, event):
        #e sometime we need to give this a modifier key binding too;
        # see some email from Josh with a suggested set of them [bruce 041220]
        mod = event.modifiers()
            ###@@@ this might need a fix_buttons call to work the same
            # on the Mac [bruce 041220]
        dScale = 1.0/1200.0
        if mod & Qt.ShiftModifier: dScale *= 2.0
        if mod & Qt.ControlModifier: dScale *= 0.25
            # Switched Shift and Control zoom factors to be more intuitive.
            # Shift + Wheel zooms in quickly (2x), Control + Wheel zooms in slowly (.25x). 
            # mark 060321
        farQ_junk, point = self.dragstart_using_GL_DEPTH( event)
        delta = event.delta()
##        factor = 1.0 + dScale * delta
        factor = exp(dScale * delta)
            #bruce 070402 bugfix: original formula, factor = 1.0 + dScale * delta, was not reversible by inverting delta,
            # so zooming in and then out (or vice versa) would fail to restore original scale precisely,
            # especially for large delta. (Measured deltas: -360 or +360.)
            # Fixed by using an exponential instead.
        self.rescale_around_point_re_user_prefs( factor , point )
            # note: depending on factor < 1.0 and user prefs, point is not always used.
        
        # Turn off hover highlighting while zooming with mouse wheel. Fixes bug 1657. Mark 060805.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.
        
        #Following fixes bug 2536 See also selectMolsMode.bareMotion
        self.timeAtLastWheelEvent = time.clock()
        
        self.o.gl_update()
        return

    def rescale_around_point_re_user_prefs(self, factor, point = None): #bruce 060829; revised/renamed/moved from GLPane, 070402
        """Rescale by factor around point or center of view, depending on zoom direction and user prefs.
        (Factor < 1.0 means zooming in.)
           If point is not supplied, the center of view remains unchanged after the rescaling,
        and user prefs have no effect.
           Note that point need not be in the plane of the center of view, and if it's not, the depth
        of the center of view will change. If callers wish to avoid this, they can project point onto
        the plane of the center of view.
        """
        if point is not None:
            # decide whether to recenter around point (or do nothing, i.e. stay centered on center of view).
            if factor < 1.0:
                # zooming in
                recenter = not env.prefs[zoomAboutScreenCenter_prefs_key]
                    # ninad 060924 Zoom about screen center is disabled by default (so recenter is True by default)
            else:
                # zooming out -- behavior changed for A9 by bruce 070402 on Mark request to not recenter on point.
                # (Old behavior was to use the same pref as for zooming in.)
                #e [Should this be a separate user pref? For now it's a debug pref, just for testing.
                #   We might replace these two prefs with a 3-choice pref which controls them both.]
                from debug_prefs import debug_pref, Choice_boolean_False
                if debug_pref("GLPane: zoom out acts the same as zoom in?", Choice_boolean_False,
                              prefs_key = "A9 devel/GLPane: zoom out same as zoom in?"
                             ):
                    recenter = not env.prefs[zoomAboutScreenCenter_prefs_key]
                else:
                    recenter = False # the new documented behavior
            if not recenter:
                point = None
        glpane = self.o
        glpane.rescale_around_point(factor, point) # note: point might have been modified above
        return
    
    # [remaining methods not yet analyzed by bruce 040922]

    
    # Key event handling revised by bruce 041220 to fix some bugs;
    # see comments in the GLPane methods, which now contain Mac-specific Delete
    # key fixes that used to be done here. For the future: The keyPressEvent and
    # keyReleaseEvent methods must be overridden by any mode which needs to know
    # more about key events than e.key() (which is the same for 'A' and 'a',
    # for example). As of 041220 no existing mode needs to do this.
    
    def keyPressEvent(self, e):
        "some modes will need to override this in the future"
        # Holding down X, Y or Z "modifier keys" in MODIFY and TRANSLATE modes generates
        # autorepeating keyPress and keyRelease events.  For now, ignore autorepeating key events.
        # Later, we may add a flag to determine if we should ignore autorepeating key events.
        # If a mode needs these events, simply override keyPressEvent and keyReleaseEvent.
        # Mark 050412
        #bruce 060516 extending this by adding keyPressAutoRepeating and keyReleaseAutoRepeating,
        # usually but not always ignored.
        if e.isAutoRepeat():
            self.keyPressAutoRepeating(e.key())
        else:
            self.keyPress(e.key())
        return
        
    def keyReleaseEvent(self, e):
        
        # Ignore autorepeating key events.  Read comments in keyPressEvent above for more detail.
        # Mark 050412
        #bruce 060516 extending this; see same comment.
        if e.isAutoRepeat():
            self.keyReleaseAutoRepeating(e.key())
        else:
            self.keyRelease(e.key())
        return

    # the old key event API (for modes which don't override keyPressEvent etc)
    
    def keyPress(self,key): # several modes extend this method, some might replace it
        if key == Qt.Key_Delete:
            self.w.killDo()
        if key == Qt.Key_Escape: # Select None. mark 060129.
                self.o.assy.selectNone()
        # Zoom in (Ctrl/Cmd+.) & out (Ctrl/Cmd+,) for Eric.  Right now, this will work with or without
        # the Ctrl/Cmd key pressed.  We'll fix this later, at the same time we address the issue of
        # more than one modifier key being pressed (see Bruce's notes below). Mark 050923.
        elif key == Qt.Key_Period:
            self.o.scale *= .95
            self.o.gl_update()
        elif key == Qt.Key_Comma: 
            self.o.scale *= 1.05
            self.o.gl_update()
	# comment out wiki help feature until further notice, wware 051101
	# [bruce 051130 revived/revised it, elsewhere in file]
        #if key == Qt.Key_F1:
        #    import webbrowser
        #    # [will 051010 added wiki help feature]
        #    webbrowser.open(self.__WikiHelpPrefix + self.__class__.__name__)
	#bruce 051201: let's see if I can bring this F1 binding back.
        # It works for Mac (only if you hold down "fn" key as well as F1);
        # but I don't know whether it's appropriate for Mac.
        # F1 for help (opening separate window, not usually an external website)
        # is conventional for Windows (I'm told).
        # See bug 1171 for more info about different platforms -- this should be revised to match.
        # Also the menu item should mention this accel key, but doesn't.
        elif key == Qt.Key_F1:
            featurename = self.user_modename()
            if featurename:
                from wiki_help import open_wiki_help_dialog
                open_wiki_help_dialog( featurename)
            pass
        elif 0 and platform.atom_debug:#bruce 051201 -- might be wrong depending on how subclasses call this, so disabled for now
            print "atom_debug: fyi: glpane keyPress ignored:", key
        return

    def keyPressAutoRepeating(self, key): #bruce 060416
        if key in (Qt.Key_Period, Qt.Key_Comma):
            self.keyPress(key)
        return
    
    def keyRelease(self,key): # mark 2004-10-11
        #e bruce comment 041220: lots of modes change cursors on this, but they
        # have bugs when more than one modifier is pressed and then one is
        # released, and perhaps when the focus changes. To fix those, we need to
        # track the set of modifiers and use some sort of inval/update system.
        # (Someday. These are low-priority bugs.)
        pass

    def keyReleaseAutoRepeating(self, key): #bruce 060416
        if key in (Qt.Key_Period, Qt.Key_Comma):
            self.keyRelease(key)
        return
        
    def update_cursor(self): # mark 060227
        """Update the cursor based on the current mouse button and mod keys pressed.
        """
        # print "basicMode.update_cursor(): button = %s, modkeys = %s, mode = %r, handler = %r" % \
        #     ( self.o.button, self.o.modkeys, self, self.o.mouse_event_handler )
        
        handler = self.o.mouse_event_handler # [bruce 070405]
            # Note: use of this attr here is a sign that this method really belongs in class GLPane,
            # and the glpane should decide whether to pass this update call to that attr's value or to the mode.
            # Or, better, maybe the mouse_event_handler should be temporarily on top of the command stack
            # in the command sequencer, overriding the mode below it for some purposes.
            # [bruce 070628 comment]
        
        if handler is not None:
            wX, wY = self.o._last_event_wXwY #bruce 070626
            handler.update_cursor(self, (wX, wY))
            return
        
        if self.o.button is None:
            self.update_cursor_for_no_MB()
        elif self.o.button == 'LMB':
            self.update_cursor_for_LMB()
        elif self.o.button == 'MMB':
            self.update_cursor_for_MMB()
        elif self.o.button == 'RMB':
            self.update_cursor_for_RMB()
        else:
            print "basicMode.update_cursor() button ignored:", self.o.button
        return
        
    def update_cursor_for_no_MB(self): # mark 060228
        '''Update the cursor for operations when no mouse button is pressed
        '''
        pass
    
    def update_cursor_for_LMB(self): # mark 060228
        '''Update the cursor for operations when the left mouse button (LMB) is pressed
        '''
        pass
        
    def update_cursor_for_MMB(self): # mark 060228
        '''Update the cursor for operations when the middle mouse button (MMB) is pressed
        '''
        #print "basicMode.update_cursor_for_MMB(): button=",self.o.button

        if self.o.modkeys is None:
            self.o.setCursor(self.w.RotateCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.MoveCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.RotateZCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.ZoomPOVCursor)
        else:
            print "Error in update_cursor_for_MMB(): Invalid modkey=", self.o.modkeys
        return
        
    def update_cursor_for_RMB(self): # mark 060228
        '''Update the cursor for operations when the right mouse button (RMB) is pressed
        '''
        pass

    def makemenu(self, menu, lis):
        # bruce 040909 moved most of this method into GLPane.
        glpane = self.o
        return glpane.makemenu(menu, lis)

    def draw_selection_curve(self):
        """Draw the (possibly unfinished) freehand selection curve.
        """
        color = get_selCurve_color(self.selSense, self.o.backgroundColor)
        
        pl = zip(self.selCurve_List[:-1],self.selCurve_List[1:])
        for pp in pl: # Draw the selection curve (lasso).
            drawer.drawline(color,pp[0],pp[1])
            
        if self.selShape == SELSHAPE_RECT:  # Draw the selection rectangle.
            drawer.drawrectangle(self.selCurve_StartPt, self.selCurve_PrevPt,
                                 self.o.up, self.o.right, color)

        if platform.atom_debug and 0: # (keep awhile, might be useful)
            # debug code bruce 041214: also draw back of selection curve
            pl = zip(self.o.selArea_List[:-1],self.o.selArea_List[1:])
            for pp in pl:
                drawer.drawline(color,pp[0],pp[1])

    def surfset(self, num):
        "noop method, meant to be overridden in cookieMode for setting diamond surface orientation"
        pass


    def _calibrateZ(self, wX, wY):
        '''Because translucent plane drawing or other special drawing, the depth value may not be accurate. We need to
           redraw them so we'll have correct Z values. 
        '''
        glMatrixMode(GL_MODELVIEW)
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) 
        
        if self.Draw_after_highlighting(pickCheckOnly=True): # Only when we have translucent planes drawn
            self.o.assy.draw(self.o)
        
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
        
        return wZ[0][0]

    def jigGLSelect(self, event, selSense):
        """Use the OpenGL picking/selection to select any jigs. Restore the projection and modelview
           matrices before returning.
        """
        ## [Huaicai 9/22/05]: Moved it from selectMode class, so it can be called in move mode, which
        ## is asked for by Mark, but it's not intended for any other mode.
        #
        ####@@@@ WARNING: The original code for this, in GLPane, has been duplicated and slightly modified
        # in at least three other places (search for glRenderMode to find them). This is bad; common code
        # should be used. Furthermore, I suspect it's sometimes needlessly called more than once per frame;
        # that should be fixed too. [bruce 060721 comment]
        
        from constants import GL_FAR_Z
        
        wX = event.pos().x()
        wY = self.o.height - event.pos().y()
        
        gz = self._calibrateZ(wX, wY) 
        if gz >= GL_FAR_Z:  # Empty space was clicked--This may not be true for translucent face [Huaicai 10/5/05]
            return False  
        
        pxyz = A(gluUnProject(wX, wY, gz))
        pn = self.o.out
        pxyz -= 0.0002*pn
        dp = - dot(pxyz, pn)
        
        # Save project matrix before it's changed
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        
        current_glselect = (wX,wY,3,3) 
        self.o._setup_projection( glselect = current_glselect) 
        
        glSelectBuffer(self.o.glselectBufferSize)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()  ## Save model/view matrix before it's changed
        try:
            glClipPlane(GL_CLIP_PLANE0, (pn[0], pn[1], pn[2], dp))
            glEnable(GL_CLIP_PLANE0)
            self.o.assy.draw(self.o)
            self.Draw_after_highlighting(pickCheckOnly=True)
            glDisable(GL_CLIP_PLANE0)
        except:
            # Restore Model view matrix, select mode to render mode 
            glPopMatrix()
            glRenderMode(GL_RENDER)
            print_compact_traceback("exception in mode.Draw() during GL_SELECT; ignored; restoring modelview matrix: ")
        else: 
            # Restore Model view matrix
            glPopMatrix() 
    
        #Restore project matrix and set matrix mode to Model/View
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glFlush()
        
        hit_records = list(glRenderMode(GL_RENDER))
        if platform.atom_debug and 0:
            print "%d hits" % len(hit_records)
        for (near,far,names) in hit_records: # see example code, renderpass.py
            if platform.atom_debug and 0:
                print "hit record: near,far,names:",near,far,names
                # e.g. hit record: near,far,names: 1439181696 1453030144 (1638426L,)
                # which proves that near/far are too far apart to give actual depth,
                # in spite of the 1-pixel drawing window (presumably they're vertices
                # taken from unclipped primitives, not clipped ones).
            if 1:
                # partial workaround for bug 1527. This can be removed once that bug (in drawer.py)
                # is properly fixed. This exists in two places -- GLPane.py and modes.py. [bruce 060217]
                if names and names[-1] == 0:
                    print "%d(m) partial workaround for bug 1527: removing 0 from end of namestack:" % env.redraw_counter, names
                    names = names[:-1]
##                    if names:
##                        print " new last element maps to %r" % env.obj_with_glselect_name.get(names[-1])
            if names:
                obj = env.obj_with_glselect_name.get(names[-1]) #k should always return an obj
                #self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
                if isinstance(obj, Jig):
                    if selSense == SUBTRACT_FROM_SELECTION: #Ctrl key, unpick picked
                        if obj.picked:  
                            obj.unpick()
                    elif selSense == ADD_TO_SELECTION: #Shift key, Add pick
                        if not obj.picked: 
                            obj.pick()
                    else:               #Without key press, exclusive pick
                        self.o.assy.unpickall_in_GLPane() # was: unpickparts, unpickatoms [bruce 060721]
                        if not obj.picked:
                            obj.pick()
                    return True
        return  False # from jigGLSelect

    pass # end of class basicMode

# end
