"""
modeMixin.py - the Command Sequencer aspect of the GLPane;
will either be replaced by or evolve into the Command Sequencer.
(But until we decide, I kept the old name to avoid a false promise
of good design.)

$Id$

History:

- written by Bruce long ago, in modes.py, mixed into GLPane.py

- split into its own file, bruce 071009

TODO:

roughly: mode -> command or currentCommand, prevMode -> _prevCommand or worse,
glpane -> commandSequencer; and then on to real refactoring. Also, some of the logic
in basicMode is really part of the command sequencer (which basicMode should just
interface to rather than "try to be").
"""

from debug import print_compact_traceback
import platform
import env

from modes import nullMode

# ==

class modeMixin(object):
    """Mixin class for supporting mode-switching. Maintains instance
       attributes mode, nullmode, as well as modetab
       (assumed by mode objects -- we should change that #e).
       Used by GLPane.
    """
    ### TODO: this class will be replaced with an aspect of the command sequencer,
    # and will use self.currentCommand rather than self.mode...
    # so some code which uses glpane.mode is being changed to get commandSequencer
    # from win.commandSequencer (which for now is just the glpane; that will change)
    # and then use commandSequencer.currentCommand. But the command-changing methods
    # like setMode are being left as commandSequencer.setMode until they're better
    # understood. [bruce 071008 comment]
    
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
        self.mode = self.nullmode
        # initial safe values, changed before __init__ ends


    # implement the virtual slot self.currentCommand
    
    def get_currentCommand(self): #bruce 071008, temporary location and implem
        return self.mode

    def set_currentCommand(self, val):
        print "something called set_currentCommand" # not yet used
        self.mode = val
    
    currentCommand = property(get_currentCommand, set_currentCommand)
    

    def _reinit_modes(self): #bruce 050911 revised this
        """[bruce comment 040922, when I split this out from GLPane's
           setAssy method; comment is fairly specific to GLPane:] Call
           this near the end of __init__, and whenever the mode
           objects need to be remade.  Create new mode objects (one
           for each mode, ready to take over mouse-interaction
           whenever that mode is in effect).

           [As of 050911, leave self.mode as nullmode, not the default mode.]

           We redo this whenever
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
        self.mode = self.nullmode # not sure what bgcolor it has, but it won't last long... see also self.use_nullmode
        self.modetab = {}
        # this destroys any mode objects that already existed [note,
        # this name is hardcoded into the mode objects]

        # create new mode objects; they know about our self.modetab
        # member and add themselves to it; they know their own names
        #bruce 050911 revised this: other_mode_classes -> mode_classes (includes class of default mode)
        for mc in self.mode_classes: 
            mc(self) # kluge: new mode object adds itself to self.modetab -- this needs to be cleaned up sometime.

        #bruce 050911 removed this; now we leave it at nullmode,
        # let direct or indirect callers put in the mode they want
        # (since different callers want different modes, and during init
        #  some modes are not ready to be entered anyway)
        ## self.start_using_mode( '$DEFAULT_MODE')
        
        return # from _reinit_modes
    
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
        self.use_nullmode()

    def use_nullmode(self):
        self.mode = self.nullmode
        
    def start_using_mode(self, mode, resuming = False): #bruce 070813 added resuming option
        """Semi-internal method (meant to be called only from self
           (typically a GLPane) or from one of our mode objects):
           Start using the given mode (name or object), ignoring any prior mode.
           If the new mode refuses to become current
           (e.g. if it requires certain kinds of selection which are not present),
           it should emit an appropriate message and return True; we'll then
           start using our default mode, or if that fails, some always-safe mode.

           @param resuming: see _enterMode method.
                  ###TODO: describe it here, and fix rest of docstring re this.
        """
        # note: resuming option often comes from **new_mode_options in callers
        #bruce 050317: do update_parts to insulate new mode from prior one's bugs
        try:
            self.assy.update_parts()
            # Note: this is overkill (only known to be needed when leaving
            # extrude, and really it's a bug that it doesn't do this itself),
            # and potentially too slow (though I doubt it),
            # and not a substitute for doing this at the end of operations
            # that need it (esp. once we have Undo); but doing it here will make things
            # more robust. Ideally we should "assert_this_was_not_needed".
        except:
            print_compact_traceback("bug: update_parts: ")
        else:
            if platform.atom_debug:
                self.assy.checkparts() #bruce 050315 assy/part debug code
        
        #e (Q: If the new mode refuses to start,
        #   would it be better to go back to using the immediately
        #   prior mode, if different? Probably not... if so, we'd need
        #   to split this into the query to the new mode for whether
        #   it will accept, and the switch to it, so the prior mode
        #   needn't worry about its state if the new mode won't even
        #   accept.)
        if not resuming:
            self.use_nullmode()
            # temporary (prevent bug-risk of reentrant event processing by
            # current mode)

        #bruce 050911: we'll try a list of modes in order, but never try to enter the same mode-object more than once.
        modes = [mode, '$DEFAULT_MODE', '$SAFE_MODE']
        del mode
        mode_objects = [] # so we don't try the same object twice
            # Note: we keep objects, not ids, so objects are kept alive so their ids are not recycled.
            # This doesn't matter as of 050911 but it might in the future if mode objects become more transient
            # (though at that point the test might fail to avoid trying some mode-classes twice, so it will need review).
        for mode in modes:
            # mode can be mode name (perhaps symbolic) or mode object
            try:
                entering_msg = "entering/resuming some mode" # only used in case of unlikely bugs
                modename = '???' # in case of exception before (or when) we set it from mode object
                mode = self._find_mode(mode) # figure out which mode object to use
                    # [#k can this ever fail?? should it know default mode?##]
                modename = mode.modename # store this now, so we can handle exceptions later or one from this line
                if id(mode) in map(id, mode_objects):
                    continue
                entering_msg = self.__Entering_Mode_message( mode, resuming = resuming) # value saved only for error messages
                    #bruce 050515: moved this "Entering Mode" message to before _enterMode
                    # so it comes before any history messages that emits. If the new mode
                    # refuses (but has no exception), assume it will emit a message about that.
                    #bruce 050106: added this status/history message about new mode...
                    # I'm not sure this is the best place to put it, but it's the best
                    # existing single place I could find.
                refused = mode._enterMode(resuming = resuming)
                    # let the mode get ready for use; it can assume self.mode
                    # will be set to it, but not that it already has been.  It
                    # should emit a message and return True if it wants to
                    # refuse becoming the new mode.
            except:
                msg = "bug: exception %s" % (entering_msg,)
                print_compact_traceback("%s: " % msg)
                from utilities.Log import redmsg
                env.history.message( redmsg( "internal error entering mode, trying default or safe mode" ))
                    ###TODO: modify message when resuming is true
                    # Emit this whether or not it's too_early!
                    # Assuming not too early, no need to name mode since prior histmsg did so.
                refused = 1
            if not refused:
                # We're in the new mode -- start sending glpane events to it.
                self.mode = mode
                break
                #bruce 050515: this is old location of Entering Mode histmsg, now moved before _enterMode
                # [that comment is from before the for loop existed]
            # exception or refusal: try the next mode in the list (if any)
            continue
        # if even $SAFE_MODE failed (serious bug), we might as well just stick with self.mode being nullMode...
        self.update_after_new_mode()
        return # from start_using_mode
    
    def __Entering_Mode_message(self, mode, resuming = False): #bruce 050911 split this out of its sole caller
        if resuming:
            msg = "Resuming %s" % mode.default_mode_status_text
        else:
            msg = "Entering %s" % mode.default_mode_status_text
            # semi-kluge, since that text starts with "Mode: ..." by convention;
            # also, not clear if we should use get_mode_status_text instead.
        try: # bruce 050112
            # (could be made cleaner by defining too_early in HistoryWidget,
            #  or giving message() a too_early_ok option)
            too_early = env.history.too_early # true when early in init
        except AttributeError: # not defined after init!
            too_early = 0
        if not too_early:
            from utilities.Log import greenmsg
            env.history.message( greenmsg( msg), norepeat_id = msg )
        return msg
    
    def _find_mode(self, modename_or_obj = None): #bruce 050911 and 060403 revised this
        """Internal method: look up the specified internal mode name (e.g. 'MODIFY' for Move mode)
        or mode-role symbolic name (e.g. '$DEFAULT_MODE') in self.modetab, and return the mode object found.
        Or if a mode object is provided, return the same-named object in self.modetab
        (warning if it's not the same object, since this might indicate a bug).
           Exception if requested mode object is not found -- unlike pre-050911 code,
         never return some other mode than asked for -- let caller do that if desired.
        """
        import UserPrefs #bruce 060403
        assert modename_or_obj, "mode arg should be a mode object or mode name, not None or whatever it is here: %r" % (modename_or_obj,)
        if type(modename_or_obj) == type(''):
            # usual case - internal or symbolic modename string
            modename = modename_or_obj
            if modename == '$SAFE_MODE':
                modename = 'SELECTMOLS' #k
            elif modename == '$STARTUP_MODE':
                ## modename = env.prefs[startupMode_prefs_key]
                modename = UserPrefs.startup_modename()
                # Needed when Preferences | Modes | Startup Mode = Default Mode.  
                # Mark 050921.
                if modename == '$DEFAULT_MODE':
                    ## modename = env.prefs[defaultMode_prefs_key]
                    modename = UserPrefs.default_modename()
            elif modename == '$DEFAULT_MODE':
                ## modename = env.prefs[defaultMode_prefs_key]
                modename = UserPrefs.default_modename()
            return self.modetab[ modename]
        else:
            # assume it's a mode object; make sure it's legit
            mode0 = modename_or_obj
            modename = mode0.modename
            mode1 = self.modetab[modename] # the one we'll return
            if mode1 is not mode0:
                # this should never happen
                print "bug: invalid internal mode; using mode %r" % (modename,)
            return mode1
        pass

    # user requests a specific new mode.

    def setMode(self, modename, **options): # in class modeMixin
        """
        This is called (e.g. from methods in MWsemantics.py) when
        the user requests a new mode using a button (or perhaps a menu
        item).  It can also be called by specific modes which want to
        change to another mode (true before, not changed now).  Since
        the current mode might need to clean up before exiting, or
        might even refuse to exit now (before told Done or Cancel), we
        just let the current mode handle this, only doing it here if
        the current mode's attempt to handle it has a bug.
        
        TODO: Probably the tool icons ought to visually indicate the
        current mode, but this doesn't yet seem to be attempted.
        When it is, it'll be done in update_after_new_mode().
        
        The modename argument should be the modename as a string,
        e.g. 'SELECT', 'DEPOSIT', 'COOKIE', or symbolic name,
        e.g. '$DEFAULT_MODE'.
        """
        # don't try to optimize for already being in the same mode --
        # let individual modes do that if (and how) they wish
        try:
            self.mode.userSetMode(modename, **options)

            # REVIEW: the following update_after_new_mode looks redundant with
            # the one at the end of start_using_mode, if that one has always
            # run at this point (which I think, but didn't prove). [bruce 070813 comment]
            
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
                    # (I think that was needed to prevent key events from being sent to
                    #  no-longer-shown mode dashboards. [bruce 041220])
                self.mode.restore_gui()
                    ###REVIEW: restore_gui is probably wrong when options caused
                    # us merely to suspend, not exit, the old mode. [bruce 070814 comment]
            except:
                print "(...even the old mode's restore_gui method, run by itself, had a bug...)"
            self.start_using_mode( '$DEFAULT_MODE' )
        return

    pass # end of class modeMixin

# end
