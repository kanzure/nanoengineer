# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
modes.py -- provides basicMode, the superclass for all modes, and
modeMixin, for GLPane.

$Id$

==

Originally written by Josh.

Partly rewritten by Bruce 040922-040924. In particular, I changed how
subclasses for specific modes relate to their superclass, basicMode,
and to their glpane object; I also split the part of class GLPane
which interfaces to the modes into a mixin class, modeMixin (in this
file), and extensively revised it.

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
"""

# Note [bruce 040923]: a lot of specific modes import * from us, and
# apparently make use of some of the symbols we import here from other
# modules.  We ought to clean up our subclass modules by making them
# import what they need directly, and then define __all__ =
# ['basicMode', 'modeMixin'] here. ##e

from qt import *
from qtgl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLE import *
import math

import os,sys
from VQT import *
import drawer
from shape import *
from assembly import *
import re
from constants import *
from debug import print_compact_traceback

from platform import *
import platform # not redundant with "from platform import *" -- we need both

# set this to 1 in a debugger, to see certain debug printouts [bruce 040924]
_debug_keys = 0

class anyMode:
    "abstract superclass for all mode objects"
    
    # default values for mode-object attributes.  external code
    # assumes every mode has these attributes, but it should pretend
    # they're read-only; mode-related code (in this file) can override
    # them in subclasses and/or instances, and modify them directly.
    
    backgroundColor = 0.0, 0.0, 0.0
    # internal name of mode, e.g. 'DEPOSIT',
    # only seen by users in "debug" error messages
    modename = "(bug: missing modename 1)" 
    # name of mode to be shown to users, as a phrase, e.g. 'sketch mode'
    msg_modename = "(bug: unknown mode)"

    def get_mode_status_text(self):
        return "(bug: mode status text)"
    # I think this will never be shown [bruce 040927]
    
    pass


class nullMode(anyMode):
    """do-nothing mode (for internal use only) to avoid crashes
    in case of certain bugs during transition between modes"""
    # (this mode is not put into the glpane's modetab)
    modename = 'nullMode'
    msg_modename = 'nullMode'
    # needs no __init__ method; constructor takes no arguments
    def noop_method(self, *args):
        print "fyi: nullMode noop method called -- probably ok, but please tell bruce if this ever happens!" ###
        return None #e print a warning?
    def __getattr__(self, attr):
        if not attr.startswith('_'):
            print "fyi: nullMode.__getattr__(%r) -- probably ok, but please tell bruce if this ever happens!" % attr ###
            return self.noop_method
        else:
            raise AttributeError, attr #e args?
    def Draw(self):
        
        # this happens... is that ok? note: see
        # "self.start_using_mode( self.default_mode)" below -- that
        # might be the cause.  if so, it's ok that it happens and good
        # that we turn it into a noop. [bruce 040924]
        
        pass
    pass ##e maybe needs to have some other specific methods?


class basicMode(anyMode):
    """Subclass this class to provide a new mode of interaction for the GLPane.
    """
    
    # Subclasses should define the following class constants,
    # and normally need no __init__ method.
    # If they have an __init__ method, it must call basicMode.__init__.
    modename = "(bug: missing modename)"
    msg_modename = "(bug: unknown mode)"
    default_mode_status_text = "(bug: missing mode status text)"
    
    def __init__(self, glpane):
        
        """This is called at least once, per type of mode (i.e. per
           specific basicMode subclass), per glpane instance, but can
           be called more often; in fact, it's called once per new
           assembly, since the modes store the assembly internally.
           It sets up that mode to be available (but not yet active)
           in that glpane.
        """
        # init or verify modename and msg_modename
        name = self.modename
        assert not name.startswith('('), \
            "bug: modename class constant missing from subclass %s" % self.__class__.__name__
        if self.msg_modename.startswith('('):
            self.msg_modename = name.lower() + " mode"
            if 0: # bruce 040923 never mind this suggestion
                print "fyi: it might be better to define 'msg_modename = %r' as a class constant in %s" % \
                  (self.msg_modename, self.__class__.__name__)
        # check whether subclasses override methods we don't want them to
        # (after this works I might remove it, we'll see)
        weird_to_override = ['Done', 'Cancel', 'Flush', 'StartOver', 'Restart',
                             'userSetMode', '_exitMode', 'Abandon', '_cleanup']
            # not 'elemSet', 'keyPress', they are normal to override;
            # not 'pickdraw', 'Wheel', they are none of my business;
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
        self.o = glpane
        self.w = glpane.win
        # store ourselves in our glpane's mode table, modetab
        self.o.modetab[self.modename] = self
        
            # bruce comment 040922: current code can overwrite a prior
            # instance of same mode, when setassy called, eg for file
            # open; this might (or might not) cause some bugs; i
            # should fix this but didn't yet do so as of 040923

        ###e bruce 040922: what are these selection things doing here?
        ### i suspect they ought to be mode-specific... not sure.
            
        self.sellist = []
        self.selLassRect = 0

        self.setup_menus()

    def setup_menus(self): # rewritten by bruce 041103
        mod_attrs = ['Menu_spec_shift', 'Menu_spec_control']
        all_attrs = ['Menu_spec'] + mod_attrs + ['debug_Menu_spec']
        for attr in all_attrs + ['Menu1','Menu2','Menu3']:
            if hasattr(self, attr):
                # probably never happens
                del self.__dict__[attr]
        self.makeMenus() # bruce 040923 moved this here, from the subclasses
        # bruce 041103 changed details of what self.makeMenus() should do
        for attr in ['Menu1','Menu2','Menu3']:
            assert not hasattr(self, attr), \
                "obsolete menu attr should not be defined: %r.%s" % (self, attr)
        # makeMenus should have set self.Menu_spec, and maybe some sister attrs
        assert hasattr(self, 'Menu_spec'), "%r.makeMenus() failed to set up" \
               " self.Menu_spec (to be a menu spec list)" % self
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
        import platform
        if platform.atom_debug and self.debug_Menu_spec:
            # put the debug items into the main menu
            self.Menu_spec.extend( [None] + self.debug_Menu_spec )
        
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
        self.Menu1 = self.makemenu(self.Menu_spec)
        self.Menu2 = self.makemenu(self.Menu_spec_shift)
        self.Menu3 = self.makemenu(self.Menu_spec_control)

    def makeMenus(self):
        assert 0, "mode subclass %r must implement makeMenus()" % self.__class__.__name__

    def warning(self, *args, **kws):
        self.o.warning(*args, **kws)

    # entering this mode
    
    def _enterMode(self):
        
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
           
        """
        refused = self.refuseEnter(warn = 1)
        if not refused:
            # do mode-specific entry initialization;
            # this method is still allowed to refuse, as well
            refused = self.Enter() 
            if refused:
                print "fyi: late refusal by %r, better if it had been in refuseEnter" % self # (but sometimes it might be necessary)
        if not refused:
            self.init_gui()
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
        self.picking = False
        # (this seems to be set and used in almost every mode)
        return None

    def init_gui(self):
        "subclasses use this to set up UI stuff like dashboards, cursors, toggle icons, etc."
        pass

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
        
    def get_mode_status_text(self):        
        """##### new method, bruce 040927; doc is tentative [maybe
           already obs?]; btw this overrides an AnyMode method:        
           Return the correct text to show right now in the
           mode-status widget (e.g."Mode: Sketch Atoms",
           "Mode: Select Molecules").           
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

    def status_msg(self, text): #bruce 041018
        """Put a status message (for progress, warnings, etc) into the main
        status widget -- not the mode status widget. In the future this might
        also print or otherwise record the message and a timestamp.
        """
        # extrudeMode.py has its own, fancier version of this... but for now
        # it must remain self-contained, in case Josh grabs another update
        # of that file alone. After the conference I will combine the best
        # features of both versions of this method. [bruce 041018]

        # print first, since if there's a bug, printed output is most important,
        # and otherwise we'll see both messages anyway.
        print "status (%s):" % self.msg_modename, text
        self.w.msgbarLabel.setText(text)

    # methods for changing to some other mode
    
    def userSetMode(self, modename):        
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
        self.Done( new_mode = modename)

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

    def Done(self, new_mode = None):
        """Done tool in dashboard; also called internally (in
           userSetMode and elsewhere) if user asks to start a new mode
           and current mode decides that's ok, without needing an
           explicit Done.  Change [bruce 040922]: Should not be
           overridden in subclasses; instead they should override
           haveNontrivialState and/or StateDone and/or StateCancel as
           appropriate.
        """
        if self.haveNontrivialState(): # use this (tho it should be just an optim), to make sure it's not giving false negatives
            refused = self.StateDone()
            if refused:
                # subclass says not to honor the Done request (and it already emitted an appropriate message)
                return
        self._exitMode( new_mode = new_mode)
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
    
    def Cancel(self, new_mode = None):
        """Cancel tool in dashboard; might also be called internally
           (but is not as of 040922, I think).  Change [bruce 040922]:
           Should not be overridden in subclasses; instead they should
           override haveNontrivialState and/or StateDone and/or
           StateCancel as appropriate.
        """
        if self.haveNontrivialState():
            refused = self.StateCancel()
            if refused:
                # subclass says not to honor the Cancel request (and it already emitted an appropriate message)
                return
        self._exitMode( new_mode = new_mode)

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
    
    def _exitMode(self, new_mode = None):
        """Internal method -- immediately leave this mode, discarding
           any internal state it might have without checking whether
           that's ok (if that check might be needed, we assume it
           already happened).  Ask our glpane to change to new_mode
           (which might be a modename or a mode object), if provided
           (and if that mode accepts being the new mode), otherwise to
           its default mode.  Unlikely to be overridden by subclasses.
           [by bruce 040922]
        """
        self._cleanup()
        if not new_mode:
            new_mode = self.o.default_mode
        #e might be cleaner to pass symbolic mode-name 'default' as new_mode
        self.o.start_using_mode(new_mode)
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
        # stop receiving events from our glpane
        self.restore_gui()
        self.w.setFocus() #bruce 041010 bugfix (needed in two places)
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
           Specific modes should call this within their own Draw method,
           unless they have a good reason not to.
        """
        if self.o.cSysToggleButton: drawer.drawaxes(5, -self.o.pov)
        # bruce 040929/041103 debug code -- for developers who enable this
        # feature, check for bugs in atom.picked and mol.picked for everything
        # in the assembly; print and fix violations. (This might be slow, which
        # is why we don't turn it on by default for regular users.)
        if platform.atom_debug:
            self.o.assy.checkpicked(always_print = 0)

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
        self.w.OldCursor = QCursor(self.o.cursor())
        # save copy of current cursor in OldCursor
        self.o.setCursor(self.w.RotateCursor) # load RotateCursor in glpane
        
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = 0

    def middleDrag(self, event):
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1])
        self.o.quat += q 
        self.o.paintGL()
        self.picking = 0

    def middleUp(self, event):
        self.o.setCursor(self.w.OldCursor) # restore original cursor in glpane
    
    def middleShiftDown(self, event):
        self.w.OldCursor = QCursor(self.o.cursor())
        # save copy of current cursor in OldCursor
        self.o.setCursor(self.w.MoveCursor) # load MoveCursor in glpane
        
        self.o.SaveMouse(event)
        self.picking = 0
    
    def middleShiftDrag(self, event):
        """Move point of view so that objects appear to follow
        the mouse on the screen.
        """
        w=self.o.width+0.0 
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        move = self.o.quat.unrot(self.o.scale * deltaMouse/(h*0.5))
        # bruce comment 040908, about josh code: 'move' is mouse
        # motion in model coords. We want center of view, -self.pov,
        # to move in opposite direction as mouse, so that after
        # recentering view on that point, objects have moved with
        # mouse.
        self.o.pov += move
        self.o.paintGL()
        self.o.SaveMouse(event)
        self.picking = 0
    
    def middleShiftUp(self, event):
        self.o.setCursor(self.w.OldCursor) # restore original cursor in glpane
    
    def middleCntlDown(self, event):
        """ Set up for zooming or rotating
        """
        self.w.OldCursor = QCursor(self.o.cursor())
        # save copy of current cursor in OldCursor
        
        self.o.SaveMouse(event)
        self.Zorg = self.o.MousePos
        self.Zq = Q(self.o.quat)
        self.Zpov = self.o.pov
        # start in ambivalent mode
        self.Zunlocked = 1
        self.ZRot = 0
        self.picking = 0
    
    def middleCntlDrag(self, event):
        """push scene away (mouse goes up) or pull (down)
           rotate around vertical axis (left-right)

        """
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
            self.o.quat = self.Zq + Q(V(0,0,1),2*pi*dx/w)
        else:
            h=self.o.height+0.0
            self.o.pov = self.Zpov-self.o.out*(2.0*dy/h)*self.o.scale
            #The above line of code can't do zoom for orthographic projection, should use the
            # scale variable instead. Huaicai 10/18/04
                
        self.picking = 0
        self.o.paintGL()

    def middleCntlUp(self, event):
        self.o.setCursor(self.w.OldCursor) # restore original cursor in glpane
    
    def middleDouble(self, event):
        pass

    # right button actions... #doc
    
    def rightDown(self, event):
        self.Menu1.exec_loop(event.globalPos(),3)
        # [bruce 041104 comment:] Huaicai says that menu.popup and menu.exec_loop
        # differ in that menu.popup returns immediately, whereas menu.exec_loop
        # returns after the menu is dismissed. What matters most for us is whether
        # the callable in the menu item is called (and returns) just before
        # menu.exec_loop returns, or just after (outside of all event processing).
        # I would guess "just before", in which case we have to worry about order
        # of side effects for any code we run after calling exec_loop, since in
        # general, our Qt event processing functions assume they are called purely
        # sequentially. I also don't know for sure whether the rightUp() method
        # would be called by Qt during or after the exec_loop call. If any of this
        # ever matters, we need to test it. Meanwhile, exec_loop is probably best
        # for context menus, provided we run no code in the same method after it
        # returns, nor in the corresponding mouseUp() method, whose order we don't
        # yet know. (Or at least I don't yet know.)
        #  With either method (popup or exec_loop), the menu stays up if you just
        # click rather than drag (which I don't like); this might be fixable in
        # the corresponding mouseup methods, but that requires worrying about the
        # above-described issues.
    
    def rightDrag(self, event):
        pass
    
    def rightUp(self, event):
        pass
    
    def rightShiftDown(self, event):
        self.Menu2.exec_loop(event.globalPos(),3)

                
    def rightShiftDrag(self, event):
        pass
    
    def rightShiftUp(self, event):
        pass
    
    def rightCntlDown(self, event):
        self.Menu3.exec_loop(event.globalPos(),3)
        
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
        but = event.state()

        dScale = 1.0/1200.0
        if but & shiftButton: dScale *= 0.5
        if but & cntlButton: dScale *= 2.0
        self.o.scale *= 1.0 + dScale * event.delta()
        ##: The scale variable needs to set a limit, otherwise, it will set self.near = self.far = 0.0
        ##  because of machine precision, which will cause OpenGL Error. Huaicai 10/18/04
        self.o.paintGL()

    # [remaining methods not yet analyzed by bruce 040922]
    
    def elemSet(self,elem): # bruce 040923: fyi: overridden in selectMode
        self.w.setElement(elem)

    def keyPress(self,key): # bruce 040923: fyi: overridden in depositMode
        if _debug_keys:
            print "fyi: basicMode.keyPress(%r)" % (key,)
        from platform import filter_key
        key = filter_key(key, debug_keys = _debug_keys)
        # fix platform-specific bugs in keycode
        # (bruce 040929 -- split from here into separate function)
        if key == Qt.Key_Delete:
            if _debug_keys:
                print "fyi: treating that as Qt.Key_Delete"
            self.w.killDo()
    
    def keyRelease(self,key): # mark 2004-10-11
        pass

    def makemenu(self, lis):
        # bruce 040909 moved most of this method into GLPane.
        win = self.o
        return win.makemenu(lis)

    def pickdraw(self):
        """Draw the (possibly unfinished) freehand selection curve.
        """
        color = logicColor(self.selSense)
        pl = zip(self.sellist[:-1],self.sellist[1:])
        for pp in pl:
            drawer.drawline(color,pp[0],pp[1])
        if self.selLassRect:
            drawer.drawrectangle(self.pickLineStart, self.pickLinePrev,
                                 self.o.up, self.o.right, color)

    ######################
    ## some buttons that will vary by mode -- Josh 10/14
    ######################

    # add hydrogen atoms to each dangling bond
    def modifyHydrogenate(self):
        if self.o.assy.selmols:
            self.o.assy.modified = 1
            for m in self.o.assy.selmols:
                m.Hydrogenate()
        elif self.o.assy.selatoms:
            self.o.assy.modified = 1
            for a in self.o.assy.selatoms.values():
                for atm in a.neighbors():
                    atm.Hydrogenate()
        self.o.paintGL()

    # remove hydrogen atoms from each selected atom/molecule
    # (coded by Mark ~10/18/04; bugfixed/optimized/msgd by Bruce same day.
    #  Bruce warns: I did not fully analyze and fix all potential bugs
    #  caused by removing a hydrogen which is in a different molecule than
    #  its neighbor atom, even though I fixed some such bugs, and other bugs.
    #  Also, I'm skeptical this belongs in basicMode; probably it will need
    #  rewriting as soon as some specific mode wants to do it differently.)
    def modifyDehydrogenate(self):
        self.status_msg("Dehydrogenating...")
        from platform import fix_plurals
        fixmols = {}
        if self.o.assy.selmols:
            counta = countm = 0
            for m in self.o.assy.selmols:
                changed = m.Dehydrogenate()
                # note: this might have removed all atoms from m! Fixed below.
                if changed:
                    counta += changed
                    countm += 1
                    fixmols[id(m)] = m
                    ###e In theory, we might have removed an H whose neighbor
                    # is in a different molecule, which therefore might need a
                    # shakedown... I have not tried to fix that, and I'm not
                    # sure it's a bug (since Dehydrogenate did changeapp on it,
                    # and maybe that's enough -- this needs review).
            if counta:
                didwhat = "Dehydrogenate: removed %d atom(s) from %d molecule(s)" \
                          % (counta, countm)
                if len(self.o.assy.selmols) > countm:
                    didwhat += \
                        " (%d selected molecule(s) had no hydrogens)" \
                        % (len(self.o.assy.selmols) - countm)
                didwhat = fix_plurals(didwhat)
            else:
                didwhat = "Dehydrogenate: selected molecules contain no hydrogens"
        elif self.o.assy.selatoms:
            count = 0
            for a in self.o.assy.selatoms.values():
                ma = a.molecule
                for atm in list(a.neighbors()) + [a]:
                    #bruce 041018 semantic change: added [a] as well
                    matm = atm.molecule
                    changed = atm.Dehydrogenate()
                    if changed:
                        count += 1
                        fixmols[id(ma)] = ma # shakedown at most once per mol
                        fixmols[id(matm)] = matm
            if fixmols:
                didwhat = \
                    "Dehydrogenate: removed %d atom(s) from %d molecule(s)" \
                    % (count, len(fixmols))
                didwhat = fix_plurals(didwhat)
                # Technically, we *should* say ", affected" instead of "from"
                # since the count includes mols of neighbors of
                # atoms we removed, not always only mols of atoms we removed.
                # Since that's rare, we word this assuming it didn't happen.
                # [#e needs low-pri fix to be accurate in that rare case;
                #  might as well deliver that as a warning, since that case is
                #  also "dangerous" in some sense.]
            else:
                didwhat = "Dehydrogenate: no hydrogens bonded to selected atoms"
        else:
            didwhat = "Dehydrogenate: nothing selected"
        if fixmols:
            self.o.assy.modified = 1
            for mol in fixmols.values():
                if mol.atoms:
                    mol.shakedown()
                else:
                    mol.kill()
            self.w.update()
        self.status_msg(didwhat)
        return

    def surfset(self, num):
        "stub for setting diamond surface orientation in cookie mode"
        pass
    
    pass # end of class basicMode

# ===

class modeMixin:
    """Mixin class for supporting mode-switching. Maintains instance
       attributes mode, nullmode, default_mode, as well as modetab
       (assumed by mode objects -- we should change that #e). Used by
       GLPane.
    """
    
    mode = None # Note (from point of view of class GLPane):
                # external code expects self.mode to always be a
                # working mode object, which has certain callable
                # methods.  We'll make it one as soon as possible, and
                # make sure it remains one after that -- even during
                # __init__ and during transitions between modes, when
                # no events should come unless there are reentrance
                # bugs in event processing. [bruce 040922]
    
    def _init1(self):
        "call this near the start of __init__"
        self.nullmode = nullMode()
        # a safe place to absorb events that come at the wrong time
        # (in case of bugs)
        self.mode = self.default_mode = self.nullmode
        # initial safe values, changed before __init__ ends

    def _reinit_modes(self):
        """[bruce comment 040922, when I split this out from GLPane's
           setAssy method; comment is fairly specific to GLPane:] Call
           this near the end of __init__, and whenever the mode
           objects need to be remade.  Create new mode objects (one
           for each mode, ready to take over mouse-interaction
           whenever that mode is in effect).  We redo this whenever
           the current assembly changes, since the mode objects store
           the current assembly in some menus they make. (At least
           that's one reason I noticed -- there might be more. None of
           this was documented before now.)  (#e Storing the current
           assembly in the modes might cause trouble, if our
           functionality is extended in certain ways; if we someday
           fix that, the mode objects could be retained for the
           lifetime of their glpane. But there's no reason we need to
           keep them longer, unless they store some other sort of
           state (like user preferences), which is probably also bad
           for them to do. So we can ignore this for now.)
        """
        if self.mode is not self.nullmode:
            ###e need to give current mode a chance to exit cleanly,
            ###or refuse -- but callers have no provision for our
            ###refusing (which is a bug); so for now just abandon
            # work, with a warning if necessary
            try:
                self.mode.Abandon()
            except:
                print "bug, error while abandoning old mode; ignore it if we can..." #e
        self.mode = self.nullmode
        self.modetab = {}
        # this destroys any mode objects that already existed [note,
        # this name is hardcoded into the mode objects]

        # create new mode objects; they know about our self.modetab
        # member and add themselves to it; they know their own names

        self.default_mode = self.default_mode_class(self)
        for mc in self.other_mode_classes:
            mc(self) # new mode object adds itself to self.modetab

        self.start_using_mode( self.default_mode)
            #k ok that it updates, in this call? [find out by trying
            #it... seems to be ok. Is that why we needed
            #nullMode.Draw()??]
    
    # methods for starting to use a given mode (after it's already
    # chosen irrevocably, and any prior mode has been cleaned up)

    def stop_sending_us_events(self, mode):
        """Semi-internal method (called by our specific modes): Stop
           sending events to the given mode (or to any actual mode
           object).
        """
        if self.mode is not mode:
            # we weren't sending you events anyway, what are you
            # talking about?!?" #k not sure this is an error
            print "fyi (for developers): stop_sending_us_events: self.mode is not mode: %r, %r" % (self.mode, mode) ###
        self.mode = self.nullmode
        
    def start_using_mode(self, mode):
        """Semi-internal method (meant to be called only from self or
           from one of our mode objects): Start using the given mode
           (name or object), ignoring any prior mode.  If the new mode
           refuses to become current (e.g. if it requires certain
           kinds of selection which are not present), it should emit
           an appropriate message and return True; then we'll start
           using our default mode.
        """
        #e (Would it be better to go back to using the immediately
        #   prior mode, if different? Probably not... if so, we'd need
        #   to split this into the query to the new mode for whether
        #   it will accept, and the switch to it, so the prior mode
        #   needn't worry about its state if the new mode won't even
        #   accept.)
        self.mode = self.nullmode
        # temporary (prevent bug-risk of reentrant event processing by
        # current mode)
        mode = self._find_mode(mode)
        try:
            refused = mode._enterMode()
        except:
            msg = "bug: exception in _enterMode for mode %r; using default mode" % (mode.modename,)
            print_compact_traceback("%s: " % msg)
            refused = 1
            # let the mode get ready for use; it can assume self.mode
            # will be set to it, but not that it already has been.  It
            # should emit a message and return True if it wants to
            # refuse becoming the new mode.
        if refused:
            # as of 040922 this never happens, but it might be routine
            # for fancier new modes like Extrude
            mode = self.default_mode
            refused1 = mode._enterMode()
            assert not refused1, "default mode should never refuse"
        self.mode = mode # finally it's ok to send events to the new mode
        self.update_after_new_mode()
        
    def _find_mode(self, modename_or_obj = None):
        """internal method: look up the specified mode (name or
           object) which other code wants us to switch to; return mode
           object, or self.nullmode, or self.default_mode, as
           appropriate. [bruce 040922]
        """
        assert modename_or_obj, "mode arg should be a mode object or mode name, not None or whatever it is here: %r" % (modename_or_obj,)
        if type(modename_or_obj) == type(''):
            # this happens whenever a toolbar button, or another mode,
            # asks for some mode by name
            modename = modename_or_obj
            mode = self.modetab.get(modename)
            if not mode:
                mode = self.default_mode
                self.warning("bug: unimplemented mode %r, using default mode %r" % (modename, mode.modename))
            return mode
        else:
            # assume it's a mode object; make sure it's legit
            mode = modename_or_obj
            if not mode in self.modetab.values():
                # this should never happen
                try:
                    modename = mode.modename
                    mode = self.modetab[modename]
                    # try getting the same-named valid mode #e remove
                    # this once i see it's not needed??
                except:
                    mode = self.default_mode
                self.warning("bug: invalid internal mode; using mode %r" % (mode.modename,))
            return mode
        pass

    # user requests a specific new mode.

    def setMode(self, modename): # in class modeMixin
        """[bruce comment 040922; functionality majorly revised then
        too, but conditions when it's called not changed much or at
        all] This is called (e.g. from methods in MWsemantics.py) when
        the user requests a new mode using a button (or perhaps a menu
        item).  It can also be called by specific modes which want to
        change to another mode (true before, not changed now).  Since
        the current mode might need to clean up before exiting, or
        might even refuse to exit now (before told Done or Cancel), we
        just let the current mode handle this, only doing it here if
        the current mode's attempt to handle it has a bug.
        
        #e Probably the tool icons ought to visually indicate the
        #current mode, but this doesn't yet seem to be attempted.
        When it is, it'll be done in update_after_new_mode().
        
        The modename argument should be the modename as a string,
        e.g. 'SELECT', 'DEPOSIT', 'COOKIE'.
        """
        # don't try to optimize for already being in the same mode --
        # let individual modes do that if (and how) they wish
        try:
            self.mode.userSetMode(modename)
            # let current mode decide whether/how to do this
            self.update_after_new_mode()
            # might not be needed if mode didn't change -- that's ok
            ###e revise this redundant comment: Let current mode
            # decide whether to permit the mode change, and either do
            # it (perhaps after cleaning itself up) or emit a warning
            # saying why it won't do it.  We don't need to know which
            # happened -- to do the switch, it just calls the
            # appropriate internal mode-switching methods... #doc like
            # Done or Cancel might do...
        except:
            # should never happen unless there's a bug in some mode --
            # so don't bother trying to get into the user's requested
            # mode, just get into a safe state.
            print_compact_traceback("userSetMode: ")
            print "bug: userSetMode(%r) had bug when in mode %r; changing back to default mode" % (modename, self.mode,)
            # for some bugs, the old mode will have left its toolbar
            # up; we should probably try to call its restore_gui
            # method directly... ok, I added this, though it's
            # untested! ###k It looks safe, and only runs if there's a
            # definite bug anyway. [bruce 040924]
            try:
                self.win.setFocus() #bruce 041010 bugfix (needed in two places)
                self.mode.restore_gui()
            except:
                print "(...even the old mode's restore_gui method, run by itself, had a bug...)"
            self.start_using_mode( self.default_mode)
        return

    pass # end of class modeMixin
