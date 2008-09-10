# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
CommandSequencer.py - class for sequencing commands and maintaining command stack.

Historically this was a mixin class for the GLPane, named modeMixin.
On 080909 it was renamed to CommandSequencer, and soon the option
to make it a separate object owned by each Assembly will be turned on.

@author: Bruce (partly based on older code by Josh)
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

Bruce 2004 or 2005: written (partly based on older code by Josh),
as class modeMixin in modes.py, mixin class for GLPane

Bruce 071009 split into its own file

Bruce 071030 file (but not class) renamed to CommandSequencer

Bruce 2008 made "not GLPANE_IS_COMMAND_SEQUENCER" work (not yet on by default)

Bruce 2008 (with Ninad working in other files) made USE_COMMAND_STACK work

bruce 080909 class renamed from modeMixin to CommandSequencer

TODO:

turn off GLPANE_IS_COMMAND_SEQUENCER by default; strip out old code

turn on USE_COMMAND_STACK by default; strip out old code

[old comment:]
roughly: mode -> command or currentCommand, prevMode -> _prevCommand or worse...
"""

from utilities.debug import print_compact_traceback, print_compact_stack
from utilities import debug_flags
import foundation.env as env
import os
import sys

from utilities.constants import DEFAULT_COMMAND

from commandSequencer.command_levels import allowed_parent

from command_support.modes import nullMode

from command_support.Command import anyCommand # only for isinstance assertion
from command_support.baseCommand import baseCommand # ditto
from command_support.GraphicsMode_API import GraphicsMode_API # ditto

from utilities.GlobalPreferences import USE_COMMAND_STACK
from utilities.GlobalPreferences import GLPANE_IS_COMMAND_SEQUENCER

_DEBUG_CSEQ_INIT = False # DO NOT COMMIT with True

_SAFE_MODE = DEFAULT_COMMAND

DEBUG_COMMAND_SEQUENCER = False ## USE_COMMAND_STACK # turn this off when USE_COMMAND_STACK becomes the default
DEBUG_COMMAND_SEQUENCER_VERBOSE = False

DEBUG_COMMAND_STACK = False

# ==

# TODO: mode -> command or currentCommand in lots of comments, some method names

class CommandSequencer(object):
    """
    Mixin class for supporting command-switching in GLPane. Basically it's
    a primitive Command Sequencer which for historical reasons lives
    temporarily as a mixin in the GLPane
    (until GLPANE_IS_COMMAND_SEQUENCER is always false).

    External API for changing command stack (will be revised):
    to enter a given command:
    - userEnterCommand
    - userEnterTemporaryCommand (will be replaced with userEnterCommand after refactoring)
    to exit a command (and perhaps then enter a specific new one):
    - command.Done (will be revised; currently calls self.start_using_mode,
      which calls new_command._enterMode, which uses command subclass API directly,
      e.g. Enter)
    other:
    - start_using_initial_mode
    - exit_all_commands
    - stop_sending_us_events
    
    Maintains instance attributes currentCommand, graphicsMode (deprecated
    to access it from here) (both read-only for public access), and mostly private
    attributes for access by command-sequencing code in class Command,
    such as nullmode and _commandTable.

    @note: graphicsMode is also available from GLPane, which gets it from here
           via its assy. Maybe it won't be needed from here at all... so we print
           a console warning whenever it's accessed directly from here.

    Public attributes available during calls of command.command_will_exit:
    
    exit_is_cancel -- whether this exit is caused by Cancel.

    exit_is_forced -- whether this exit is forced to occur (e.g. caused by
    exit_all_commands when closing a model).

    warn_about_abandoned_changes -- when exit_is_forced, whether the user should
    be warned about changes (if any) stored in active commands being exited
    (as opposed to changes stored in the model in assy, as usual) which are
    being discarded unavoidably

    exit_is_implicit -- whether this exit is occuring only as a prerequisite
    of entering some other command
    
    exit_target -- if not None, the goal of the exit is ultimately to exit
    the command of this commandName

    enter_target -- if not None, the goal of the exit is ultimately to enter
    the command of this commandName
    """
    # TODO: turn this into a standalone command sequencer object,
    # which also contains some logic now in class Command
    #
    # older comment: this class will be replaced with an aspect of the command
    # sequencer, and will use self.currentCommand rather than self.mode...
    # so some code which uses glpane.mode is being changed to get
    # commandSequencer from win.commandSequencer (which for now is just the
    # glpane; that will change) and then use commandSequencer.currentCommand.
    # But the command-changing methods like userEnterCommand are being left as
    # commandSequencer.userEnterCommand until they're better understood.
    # [bruce 071008 comment]

    # Note: see "new code" far below for comments and definitions about the
    # attributes of self which we maintain, namely mode, graphicsMode,
    # currentCommand.

    if not USE_COMMAND_STACK:
        prevMode = None #bruce 071011 added this initialization
    else:
        prevMode = property() # hopefully this causes errors on any access of it ### check this
        # doc these:
        exit_is_cancel = False
        exit_is_forced = False
        warn_about_abandoned_changes = True
        exit_is_implicit = False
        exit_target = None
        enter_target = None
        _command_stack_change_counter = 0

    def __init__(self, assy): #bruce 080813
        assert not GLPANE_IS_COMMAND_SEQUENCER
        self.assy = assy
        self.win = assy.win
        assert self.assy
        assert self.win
        self._init_modeMixin()
        return
    
    def _init_modeMixin(self):
        # todo: will be merged into __init__ when this class is no longer a mixin,
        # i.e. when GLPANE_IS_COMMAND_SEQUENCER is always False;
        # used when USE_COMMAND_STACK or not;
        # should try to clean up init code (see docstring) when USE_COMMAND_STACK is always true
        """
        [semi-private]
        
        Call this near the start of __init__ in a subclass that mixes us in
        (i.e. GLPane), or in our own __init__ method (when we're not used as a mixin).

        Subsequent init calls should also be made, namely:
        - _reinit_modes, from glpane.setAssy, from _make_and_init_assy or GLPane.__init__
        - start_using_initial_mode - end of MWsemantics.__init__, or _make_and_init_assy.

        To reuse self "from scratch", perhaps with new command objects (necessary
        if self is reused with a new assy, as happens when GLPANE_IS_COMMAND_SEQUENCER)
        and/or new command classes (e.g. after a developer reloads some of them),
        first call self.exit_all_commands(), then do only the "subsequent init calls"
        mentioned above -- don't call this method again.
        """
        if _DEBUG_CSEQ_INIT:
            print "_DEBUG_CSEQ_INIT: _init_modeMixin"###

        # make sure certain attributes are present (important once we're a
        # standalone object, since external code expects us to have these
        # even if we don't need them ourselves) (but it's ok if they're still None)
        self.win # probably used only in EditCommand and in some methods in self
        self.assy # used in self and in an unknown amount of external code
        
        self._registered_command_classes = {} #bruce 080805

        # When not USE_COMMAND_STACK, these might be noops,
        # but more likely, we need a nullmode then just as we do now
        # (in case of unexpected uses of currentCommand during init).
        # So call them in that case too.
        self._recreate_nullmode()
        self._use_nullmode()
        # see docstring for additional inits needed as external calls
        return

    def _recreate_nullmode(self): # only called from this file, as of 080805
        # REVIEW whether still needed when USE_COMMAND_STACK; presently still used then
        self.nullmode = nullMode()
            # TODO: rename self.nullmode; note that it's semi-public [###REVIEW: what uses it?];
            # it's a safe place to absorb events that come at the wrong time
            # (mainly in case of bugs, but also happens routinely sometimes)
        return
    
    def _reinit_modes(self): #revised, bruce 050911, 080209
        # REVIEW: still ok for USE_COMMAND_STACK? guess yes, for now;
        # and still needed, since it's part of how to init or reset the
        # command sequencer in its current external API
        # (see doc for _init_modeMixin) [bruce 080814, still true 080909]

        # note: as of 080812, not called directly in this file; called from:
        # - GLPane.setAssy (end of function),
        #   which is called from:
        #   - GLPane.__init__ (in partwindow init)
        #   - MWSemantics._make_and_init_assy (fileOpen/fileClose)
        # - extrudeMode.extrude_reload (followed by .start_using_initial_mode( '$DEFAULT_MODE' )).
        # Each call is followed eventually by start_using_initial_mode,
        # but in some cases this is in a different method or not nearby.
        #
        # Maybe todo: encapsulate that pair (_reinit_modes and start_using_initial_mode)
        # into a reset_command_sequencer method, even though it can't yet be used
        # by the main calls of this listed above; and/or make the reinit of
        # command objects lazy (per-command-class), so calling this is optional,
        # at least in methods like extrude_reload.
        """
        [bruce comment 040922, when I split this out from GLPane's
        setAssy method; comment is fairly specific to GLPane:]

        Call this near the end of __init__, and whenever the mode
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
        lifetime of their command sequencer. But there's no reason we need to
        keep them longer, unless they store some other sort of
        state (like user preferences), which is probably also bad
        for them to do. So we can ignore this for now.)
        """
        if _DEBUG_CSEQ_INIT:
            print "_DEBUG_CSEQ_INIT: reinit modes"###

        self.exit_all_commands()

        self._commandTable = {}
            # this discards any mode objects that already existed
            # (it probably doesn't destroy them -- they are likely
            #  to be part of reference cycles)

        # create new mode objects; they know about our method
        # self.store_commandObject, and call it with their modenames and
        # themselves
        #bruce 050911 revised this: now includes class of default mode

        #bruce 080209 change:
        # import the following now, not when GLPane is imported (as was
        # effectively done before today's refactoring split out this new file)
        # (might help with bug 2614?)
        from commandSequencer.builtin_command_loaders import preloaded_command_classes # don't move this import to toplevel!
        for command_class in preloaded_command_classes():
            commandName = command_class.commandName
            assert not self._commandTable.has_key(commandName)
            # use preloaded_command_classes for ordering, even when
            # instantiating registered classes that replace them
            actual_class = self._registered_command_classes.get(
                commandName, command_class )
            if actual_class is not command_class:
                print "fyi: instantiating replacement command %r" % (actual_class,)
                assert actual_class.commandName == commandName
                    # always true, due to how these are stored and looked up
            self._instantiate_cached_command( actual_class)
        # now do the rest of the registered classes
        # (in order of their commandNames, so bugs are more likely
        #  to be deterministic)
        more_items = self._registered_command_classes.items()
        more_items.sort()
        for commandName, actual_class in more_items:
            if not self._commandTable.has_key(commandName):
                print "fyi: instantiating registered non-built-in command %r" % (actual_class,)
                self._instantiate_cached_command( actual_class)

        # todo: something to support lazily loaded/instantiated commands
        # (make self._commandTable a dictlike object that loads on demand?)

        ## self.start_using_initial_mode( '$DEFAULT_MODE')
        #bruce 050911 removed this; now we leave it at nullmode,
        # let direct or indirect callers put in the mode they want
        # (since different callers want different modes, and during init
        #  some modes are not ready to be entered anyway)
        
        return # from _reinit_modes

    def _instantiate_cached_command( self, command_class): #bruce 080805 split this out
        new_command = command_class(self)
            # kluge: new mode object passes itself to
            # self.store_commandObject; it would be better for us to store
            # it ourselves
            # (to implement that, first add code to assert every command
            #  does this in the name we expect)
        assert new_command is self._commandTable[command_class.commandName]
        return new_command

    def store_commandObject(self, commandName, commandObject): #bruce 080209
        """
        Store a command object to use (i.e. enter) for the given commandName.
        (If a prior one is stored for the same commandName, replace it.)

        @note: commands call this in their __init__ methods. (Unfortunately.)
        """
        assert commandObject.commandName == commandName #bruce 080805
        self._commandTable[commandName] = commandObject

    def exit_all_commands(self, warn_about_abandoned_changes = True):
        """
        Exit all currently active commands
        (even the default command, even when USE_COMMAND_STACK),
        and leave the current command as nullMode.

        To do the exiting, use "Abandon", i.e. (when USE_COMMAND_STACK)
        make sure self.exit_is_forced is true when examined by exit-related
        methods in command classes.
        
        @param warn_about_abandoned_changes: if False, unsaved changes (if any)
                                         stored in self's active commands
                                         (as opposed to unsaved changes stored
                                         in the model in self.assy)
                                         can be discarded with no user warning.
                                         (Otherwise they are discarded with a
                                         warning. There is no way for this code
                                         or the user to avoid discarding them.)
                                         Note that it is too late to offer to
                                         not discard them -- caller must do that
                                         separately if desired (and if user
                                         agrees to discard them, caller should
                                         pass True to this option to avoid a
                                         duplicate warning).
                                         This is only needed due to there being
                                         some changes stored in commands but
                                         not in assy, which are not noticed by
                                         assy.has_changed(). Most commands don't
                                         store any such changes.
        @type warn_about_abandoned_changes: boolean
        """
        #bruce 080806 split this out; used in _reinit_modes and extrude_reload
        #bruce 080909 new feature, warn_about_abandoned_changes can be false
        if USE_COMMAND_STACK:
            while self._raw_currentCommand and \
                  not self.currentCommand.is_null and \
                  not self.currentCommand.is_default_command():
                # exit current command
                old_commandName = self.currentCommand.commandName
                try:
                    self._exit_currentCommand_with_flags(
                        forced = True,
                        warn_about_abandoned_changes = warn_about_abandoned_changes
                     )
                except:
                    print_compact_traceback()
                if self._raw_currentCommand and \
                   self.currentCommand.commandName == old_commandName:
                    print "bug: failed to exit", self.currentCommand
                    break
                continue
            # Now we're in the default command. Some callers require us to exit
            # that too. Exiting it in the above loop would fail, but fortunately
            # we can just discard it (unlike for a general command). [Note: this
            # might change if it was given a PM.]
            self._use_nullmode()
            return
        else:
            if not self._raw_currentCommand.is_null:
                # old comment from when this was inlined into _reinit_modes --
                # might be wrong now:
                ###e need to give current mode a chance to exit cleanly,
                ###or refuse -- but callers have no provision for our
                ###refusing (which is a bug); so for now just abandon
                # work, with a warning if necessary
                try:
                    self.currentCommand.Abandon(warn_about_abandoned_changes = \
                                                warn_about_abandoned_changes )
                except:
                    msg = "bug: error while abandoning old mode; trying to ignore"
                    print_compact_traceback( msg + ": " )
            self._use_nullmode()
                # not sure what glpane bgcolor nullmode has, but it won't last long...
            self.prevMode = None #bruce 080806
            return
        pass

    def _exit_currentCommand_with_flags(self,
                                        cancel = False,
                                        forced = False,
                                        warn_about_abandoned_changes = True,
                                        implicit = False,
                                        exit_target = None,
                                        enter_target = None
                                        ): #bruce 080827
        """
        Call self.currentCommand._f_command_do_exit_if_ok
        (and return what it returns)
        while setting attrs on self (only during this call)
        based on the options passed (as documented below).

        @param cancel: value for self.exit_is_cancel, default False
        
        @param forced: value for self.exit_is_forced, default False
                       (only passed as True by exit_all_commands)
        
        @param implicit: value for self.exit_is_implicit, default False
        
        @param exit_target: value for self.exit_target, default None
        
        @param enter_target: value for self.enter_target, default None
        """
        assert USE_COMMAND_STACK
        assert self.currentCommand and self.currentCommand.parentCommand
        # set attrs for telling command_will_exit what side effects to do
        self.exit_is_cancel = cancel
        self.exit_is_forced = forced
        self.warn_about_abandoned_changes = warn_about_abandoned_changes
        self.exit_is_implicit = implicit
        # set attrs to let command_exit methods construct dialog text, etc
        # (when used along with the other attrs)
        self.exit_target = exit_target # a commandName, if we're exiting it as a goal ### FIX to featureName?
        self.enter_target = enter_target # a commandName, if we're entering it as a goal ### FIX to featureName?
        # exit the current command, return whether it worked
        try:
            res = self.currentCommand._f_command_do_exit_if_ok()
        finally:
            #TODO: except clause, protect callers (unless that method does it)
            self.exit_is_cancel = False
            self.exit_is_forced = False
            self.warn_about_abandoned_changes = True
            self.exit_is_implicit = False
            self.exit_target = None
            self.enter_target = None
        return res
    
    def remove_command_object(self, commandName): #bruce 080805
        try:
            del self._commandTable[commandName]
        except KeyError:
            print "fyi: no command object for %r in prepare_to_reload_commandClass" % commandName
        return

    def register_command_class(self, commandName, command_class): #bruce 080805
        """
        Cause this command class to be instantiated by the next call
        of self._reinit_modes, or [nim] the next time something needs
        to look up a command object for commandName.
        """
        assert command_class.commandName == commandName
        self._registered_command_classes[commandName] = command_class
        # REVIEW: also remove_command_object? only safe when it can be recreated lazily.
        return
    
    # methods for starting to use a given mode (after it's already
    # chosen irrevocably, and any prior mode has been cleaned up)

    def stop_sending_us_events(self, command): # note: called only from basicCommand._cleanup as of long before 080805
        """
        Semi-internal method (called by command instances):
        Stop sending events to the given command (or to any actual command
        object besides the nullCommand).
        """
        if USE_COMMAND_STACK:
            ### REVIEW: probably obsolete
            print "stop_sending_us_events doing nothing since USE_COMMAND_STACK"
            return
        else:
            if not self.is_this_command_current(command):
                # we weren't sending you events anyway, what are you
                # talking about?!?" #k not sure this is an error
                # (note: this can happen when a protein or dna subcommand is current
                #  and a non-protein or non-dna command (resp) is directly entered
                #  -- bruce 080812 comment)
                print "fyi (for developers): stop_sending_us_events called " \
                      "from %r which is not currentCommand %r" % \
                      (command, self._raw_currentCommand)
            self._use_nullmode()
            return
        pass

    def _use_nullmode(self):
        """
        [private]
        self._raw_currentCommand = self.nullmode
        """
        # note: 4 calls, all in this file, as of before 080805; making it private
        #
        # Note: when USE_COMMAND_STACK is true, this is only called during
        # exit_all_commands (with current command being default command),
        # and during init or reinit of self (with current command always being
        # nullMode, according to debug prints no longer present).
        # When not USE_COMMAND_STACK, it is also called during most changes
        # from one command to another. [bruce 080814/080909 comment]
        self._raw_currentCommand = self.nullmode

    def is_this_command_current(self, command):
        """
        Semi-private method for use by Command.isCurrentCommand;
        for doc, see that method.
        """
        # We compare to self._raw_currentCommand in case self.currentCommand
        # has been wrapped by an API-enforcement (or any other) proxy.
        return self._raw_currentCommand is command

    def _update_model_between_commands(self): #bruce 080806 split this out
        #bruce 050317: do update_parts to insulate new mode from prior one's bugs
        # WARNING: when USE_COMMAND_STACK, this might be needed (as much as it ever was),
        # but calling it might be NIM [bruce 080909 comment]
        try:
            self.assy.update_parts()
            # Note: this is overkill (only known to be needed when leaving
            # extrude, and really it's a bug that it doesn't do this itself),
            # and potentially too slow (though I doubt it),
            # and not a substitute for doing this at the end of operations
            # that need it (esp. once we have Undo); but doing it here will make
            # things more robust. Ideally we should "assert_this_was_not_needed".
        except:
            print_compact_traceback("bug: update_parts: ")
        else:
            if debug_flags.atom_debug:
                self.assy.checkparts() #bruce 050315 assy/part debug code
        return
        
    def start_using_initial_mode(self, mode): #bruce 080812
        """
        [semi-private]
        Initialize self to the given initial mode,
        just after self is created or _reinit_modes is called.

        @note: this is called, and is part of our external API for init/reinit,
               whether or not USE_COMMAND_STACK. See docstring of _init_modeMixin.

        @see: exit_all_commands
        """
        # as of 080812, this is called from 3 places:
        # - MWsemantics.__init__
        # - _make_and_init_assy
        # - extrude_reload
        assert mode in ('$STARTUP_MODE', '$DEFAULT_MODE')
        if USE_COMMAND_STACK:
            #bruce 080814 guess
            self._raw_currentCommand = None ###??
            command_instance = self._find_command_instance( mode)
                # note: exception if this fails to find command (never returns false)
            entered = command_instance._command_do_enter_if_ok()
            assert entered
            return
        else:
            self.start_using_mode( mode)
            return
        pass
    
    def start_using_mode(self, mode, resuming = False, has_its_own_gui = True):
        """
        Semi-internal method (meant to be called only from self
        (typically a GLPane) or from one of our mode objects,
        but this is not strictly obeyed):
        Start using the given mode (name or object), ignoring any prior mode.
        If the new mode refuses to become current
        (e.g. if it requires certain kinds of selection which are not present),
        it should emit an appropriate message and return True; we'll then
        start using our default mode, or if that fails, some always-safe mode.

        @param resuming: see _enterMode method. ###TODO: describe it here,
                         and fix rest of docstring re this.
        """
        assert not USE_COMMAND_STACK # other case not needed [bruce 080909]
        # as of 080812, this is called from:
        # - start_using_initial_mode
        # - at end of userEnterCommand, in case of bug
        # - basicCommand._exitMode (called from Done & Cancel)
        # Note that it is also called indirectly by userEnterCommand entering
        # its new mode normally, via basicCommand._f_userEnterCommand and Done.
        # It is probably the only way to start using a new current command
        # (aside from nullmode). [### verify]
        if _DEBUG_CSEQ_INIT:
            print "_DEBUG_CSEQ_INIT: start_using_mode", mode ###
        #bruce 070813 added resuming option
        # note: resuming option often comes from **new_mode_options in callers

        self._update_model_between_commands()
        
        #e (Q: If the new mode refuses to start,
        #   would it be better to go back to using the immediately
        #   prior mode, if different? Probably not... if so, we'd need
        #   to split this into the query to the new mode for whether
        #   it will accept, and the switch to it, so the prior mode
        #   needn't worry about its state if the new mode won't even
        #   accept.)
        if not resuming:
            self._use_nullmode()
            # temporary (prevent bug-risk of reentrant event processing by
            # current mode)

        #bruce 050911: we'll try a list of modes in order, but never try to
        # enter the same mode-object more than once.
        modes = [mode, '$DEFAULT_MODE', '$SAFE_MODE']
        del mode
        mode_objects = [] # so we don't try the same object twice
            # Note: we keep objects, not ids, to make sure objects are kept
            # alive, so their ids are not recycled by python.
            # This doesn't matter as of 050911, but it might in the future
            # if mode objects become more transient (though at that point
            # the test might fail to avoid trying some mode-classes twice,
            # so it will need review).
        for mode in modes:
            # mode can be mode name (perhaps symbolic) or mode object
            try:
                entering_msg = "entering/resuming some mode"
                    # only used in case of unlikely bugs
                commandName = '???'
                    # in case of exception before (or when) we set it from
                    # mode object
                mode = self._find_command_instance(mode)
                    # [#k can this ever fail?? should it know default mode?##]
                commandName = mode.commandName
                    # store this now, so we can handle exceptions later,
                    # or get one from this line
                if id(mode) in map(id, mode_objects):
                    continue
                entering_msg = self._Entering_Mode_message( mode,
                                                            resuming = resuming)
                    # return value saved in entering_msg only for error messages
                    #bruce 050515: moved this "Entering Mode" message to before
                    # _enterMode so it comes before any history messages that
                    # emits. If the new mode refuses (but has no exception),
                    # assume it will emit a message about that.
                    #bruce 050106: added this status/history message about new
                    # mode... I'm not sure this is the best place to put it,
                    # but it's the best existing single place I could find.
                refused = mode._enterMode(resuming = resuming, 
                                          has_its_own_gui = has_its_own_gui)
                    # let the mode get ready for use; it can assume
                    # self.currentCommand will be set to it, but not that it
                    # already has been. It should emit a message and return True
                    # if it wants to refuse becoming the new mode.
            except:
                msg = "bug: exception %s" % (entering_msg,)
                print_compact_traceback("%s: " % msg)
                from utilities.Log import redmsg
                msg2 = "internal error entering mode, trying default or safe mode"
                env.history.message( redmsg( msg2 ))
                    ###TODO: modify message when resuming is true
                    # Emit this whether or not it's too_early!
                    # Assuming not too early, no need to name mode
                    # since prior histmsg did so.
                refused = 1
            if not refused:
                # We're in the new command -- start sending glpane events to its
                # graphicsMode, and other events from command sequencer directly
                # to it.
                self._raw_currentCommand = mode
                break
                #bruce 050515: this is old location of Entering Mode histmsg,
                # now moved before _enterMode
                # [that comment is from before the for loop existed]
            # exception or refusal: try the next mode in the list (if any)
            continue
        # if even $SAFE_MODE failed (serious bug), we might as well just stick
        # with self.currentCommand being nullMode...
        self._cseq_update_after_new_mode()
        return # from start_using_mode

    def _cseq_update_after_new_mode(self): # rename?
        """
        Do whatever updates are needed after self.currentCommand (including
        its graphicsMode aspect) might have changed.

        @note: it's ok if this is called more than needed, except it
               might be too slow. In practice, as of 080813 it looks
               like it is usually called twice after most command changes.
               This should be fixed, but it's not urgent.
        """
        #bruce 080813 moved/renamed this from GLPane.update_after_new_mode,
        # and refactored it
        if DEBUG_COMMAND_SEQUENCER:
            print "DEBUG_COMMAND_SEQUENCER: calling _cseq_update_after_new_mode"
        glpane = self.assy.glpane
        glpane.update_GLPane_after_new_command()
            #bruce 080903 moved this before the call of update_after_new_graphicsMode
            # (precaution, in case glpane.scale, which it can alter, affects that)
        glpane.update_after_new_graphicsMode() # includes gl_update

        self.win.win_update() # includes gl_update (redundant calls of that are ok)

        #e also update tool-icon visual state in the toolbar? [presumably done elsewhere now]
        # bruce 041222 [comment revised 050408, 080813]:
        # changed this to a full update (not just a glpane update),
        # and changed MWsemantics to make that safe during our __init__
        # (when that was written, it referred to GLPane.__init__,
        #  which is when self was initialized then).

        return

    def _Entering_Mode_message(self, mode, resuming = False):
        featurename = mode.get_featurename()
        if resuming:
            msg = "Resuming %s" % featurename
        else:
            msg = "Entering %s" % featurename
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

    def _find_command_instance(self, commandName_or_obj = None): # note: only used in this file [080806]
        """
        Internal method: look up the specified commandName
        (e.g. 'MODIFY' for Move)
        or command-role symbolic name (e.g. '$DEFAULT_MODE')
        in self._commandTable, and return the command object found.
        Or if a command object is passed, return it unchanged.

        Exception if requested command object is not found -- unlike
        pre-050911 code, never return some other command than asked for;
        let caller use a different one if desired.
        """
        #bruce 050911 and 060403 revised this;
        # as of 080804, looks ok for USE_COMMAND_STACK but needs renaming/rewrite for terminology mode -> Command ###TODO
        assert commandName_or_obj, "commandName_or_obj arg should be a command object " \
               "or commandName, not None or whatever false value it is here: %r" % \
               (commandName_or_obj,)
        if type(commandName_or_obj) == type(''):
            # usual case - internal or symbolic commandName string
            # TODO: a future refactoring should cause caller to do
            # the symbol replacements, so this is either a commandName
            # or object, since caller will need to match this to currently
            # active commands anyway. [bruce 080806 comment]
            commandName = commandName_or_obj
            if commandName == '$SAFE_MODE':
                commandName = _SAFE_MODE
            if commandName == '$STARTUP_MODE':
                commandName = self.startup_commandName() # might be '$DEFAULT_MODE'
            if commandName == '$DEFAULT_MODE':
                commandName = self.default_commandName()
            # todo: provision for lazy instantiation, if not already in _commandTable
            return self._commandTable[ commandName]
        else:
            # assume it's a command object; make sure it's legit
            command = commandName_or_obj
            commandName = command.commandName # make sure it has this attr
            # (todo: rule out error of it's being a command class)

            #bruce 080806 removed the following:
##            mode1 = self._commandTable[commandName] # the one we'll return
##            if mode1 is not command:
##                # this should never happen
##                print "bug: invalid internal command; using %r" % \
##                      (commandName,)
##            return mode1
            
            return command
        pass

    def _commandName_properties(self, commandName): #bruce 080814
        # STUB -- just use the cached instance for its properties.
        return self._find_command_instance(commandName)
    
    # default and startup command name methods.
    # These were written by bruce 060403 in UserPrefs.py (now Preferences.py)
    # and at some point were settable by user preferences.
    # They were revised to constants by ninad 070501 for A9,
    # then moved into this class by bruce 080709 as a refactoring.
    
    def default_commandName(self):
        """
        Return the commandName string of the user's default mode.
        """
        # note: at one point this made use of env.prefs[ defaultMode_prefs_key].
        return DEFAULT_COMMAND

    def startup_commandName(self):
        """
        Return the commandName string (literal or symbolic, e.g.
        '$DEFAULT_MODE') of the user's startup mode.
        """
        # note: at one point this made use of env.prefs[ startupMode_prefs_key].
        return DEFAULT_COMMAND

    # user requests a specific new command.

    def userEnterCommand_for_USE_COMMAND_STACK(self, want_commandName, always_update = False): # @@@ redirect Done to get here...
        """
        [main public method for changing command stack
         to get into a specified command]
        
        Exit and enter commands as needed, so that the current command
        has the given commandName.
        """
        self._f_assert_command_stack_unlocked()
        
        do_update = always_update # might be set to True below
        del always_update
        
        error = False # might be changed below

        # look up properties of desired command
        want_command = self._commandName_properties(want_commandName)
            # has command properties needed for this...
            # for now, just a command instance, but AFAIK the code
            # only assumes it has a few properties and methods,
            # namely command_level, command_parent, and helper methods
            # for interpreting them.
        
        # exit incompatible commands as needed
        while not error:
            # exit current command, if necessary and possible
            old_commandName = self.currentCommand.commandName
            if old_commandName == want_commandName:
                # maybe: add option to avoid this check, for use on reloaded commands
                break
            if self._need_to_exit(self.currentCommand, want_command):
                do_update = True # even if error
                exited = self._exit_currentCommand_with_flags(implicit = True,
                                                              enter_target = want_commandName)
                assert exited == (old_commandName != self.currentCommand.commandName)
                    # review: zap retval and just use this condition?
                if not exited:
                    error = True
            else:
                break
            continue

        # enter prerequisite parent commands as needed, then the wanted command
        # (note: this code is similar to that in _enterRequestCommand)
        while not error:
            # enter the next command we need to enter, if possible
            old_commandName = self.currentCommand.commandName
            if old_commandName == want_commandName:
                break
            
            next_commandName_to_enter = self._next_commandName_to_enter( self.currentCommand, want_command) ### IMPLEM; might be want_commandName; never None
            assert old_commandName != next_commandName_to_enter
            
            do_update = True # even if error
            command_instance = self._find_command_instance( next_commandName_to_enter)
                # note: exception if this fails to find command (never returns None)
            entered = command_instance._command_do_enter_if_ok()
            assert entered == (old_commandName != self.currentCommand.commandName)
            assert entered == (next_commandName_to_enter == self.currentCommand.commandName)
                # review: zap retval and just use this last condition?
            if not entered:
                error = True
            # review: add direct protection against infinite loop?
            # bugs to protect against include a cycle or infinite series
            # in the return values of _next_commandName_to_enter, or modifications
            # to command stack in unexpected places in this loop.
            continue

        if error:
            print "error trying to enter", want_commandName #e more info
        
        if do_update:
            self._cseq_update_after_new_mode()
            # Q: when do we call the newer update function that replaces model_changed?
            #    (namely, command_post_event_ui_updater, which calls command_update_state,
            #     and some related methods in the current command and/or all active commands)
            # A: after the current user event handler finishes.
            # Q: how do we tell something that it needs to be called?
            # A: we don't, it's always called (after every user event).

        return

    def _enterRequestCommand(self, commandName): #bruce 080904
        """
        [private]

        Immediately enter the specified command, by pushing it on the command
        stack, not changing the command stack in any other ways (e.g. exiting
        commands or checking for required parent commands).

        Do necessary updates from changing the command stack, but not
        _update_model_between_commands (in case it's too slow).

        @see: callRequestCommand, which calls this.
        """
        assert USE_COMMAND_STACK
        
        # note: this code is similar to parts of userEnterCommand
        old_commandName = self.currentCommand.commandName
        command_instance = self._find_command_instance( commandName)
            # note: exception if this fails to find command (never returns None)
        entered = command_instance._command_do_enter_if_ok()
            # note: that method might be overkill, but it's probably ok for now
        assert entered == (old_commandName != self.currentCommand.commandName)
        assert entered == (commandName == self.currentCommand.commandName)
        assert entered, "error trying to enter %r" % commandName
            # neither caller nor this method's API yet tolerates failure to enter
        self._cseq_update_after_new_mode()
            # REVIEW: should this be up to caller, or controlled by an option?
        return

    def _need_to_exit(self, currentCommand, want_command): #bruce 080814 # maybe: rename?
        """
        """
        return not allowed_parent( want_command, currentCommand )
    
    def _next_commandName_to_enter(self, currentCommand, want_command): #bruce 080814
        """
        Assume we need to enter zero or more commands and then enter want_command,
        and are at the given currentCommand (known to not already be want_command).
        Assume that we don't need to exit any commands (caller has already done
        that if it was needed).
        
        Return the commandName of the next command we should try to enter.

        If want_command is nestable, this is always its own commandName.
        Otherwise, it's its own name if currentCommand is its required
        parentCommand, otherwise it's the name of its required parentCommand
        (or perhaps of a required grandparent command, etc, if that can ever happen).

        We never return the name of the default command, since we assume
        it's always on the command stack. [### REVIEW whether that's good or true]
        """
        if not want_command.is_fixed_parent_command():
            # nestable command (partly or fully)
            return want_command.commandName
        else:
            # fixed-parent command
            ### STUB: ASSUME ONLY ONE LEVEL OF REQUIRED PARENT COMMAND IS POSSIBLE (probably ok for now)
            needs_parentName = want_command.command_parent or self.default_commandName()
            if currentCommand.commandName == needs_parentName:
                return want_command.commandName
            # future: check other choices, if more than one level of required
            # parent is possible.
            # note: if this is wrong, nothing is going to verify we're ready
            # to enter this command -- it's just going to get immediately
            # entered (pushed on the command stack).
            return needs_parentName
        pass

    def _f_exit_active_command(self, command, cancel = False, forced = False, implicit = False): #bruce 080827
        """
        Exit the given command (which must be active), after first exiting
        any subcommands it may have.

        Do side effects appropriate to the options passed, by setting
        corresponding attributes in self which can be tested by subclass
        implementations of command_will_exit. For documentation of these
        attributes and their intended effects, see the callers which pass
        them, listed below, and the attributes of related names in
        this class, described in the class docstring.

        @param command: the command it's our ultimate goal to exit.
                        Must be an active command, but may or may not be
                        self.currentCommand. Its commandName is saved as
                        self.exit_target.
        
        @param cancel: @see: baseCommand.command_Cancel and self.exit_is_cancel
        
        @param forced: @see: CommandSequencer.exit_all_commands and self.exit_is_forced
        
        @param implicit: @see: baseCommand.command_Done and self.exit_is_implicit
        """
        assert USE_COMMAND_STACK
        self._f_assert_command_stack_unlocked()
        if DEBUG_COMMAND_SEQUENCER:
            print "DEBUG_COMMAND_SEQUENCER: _f_exit_active_command wants to exit back to", command
        assert command.command_is_active(), "can't exit inactive command: %r" % command
        # exit commands, innermost (current) first, until we fail,
        # or exit the command we were passed (our exit_target).
        error = False
        do_update = False
        while not error:
            old_command = self.currentCommand
            if DEBUG_COMMAND_SEQUENCER:
                print "DEBUG_COMMAND_SEQUENCER: _f_exit_active_command will exit currentCommand", old_command
            exited = self._exit_currentCommand_with_flags( cancel = cancel,
                                                           forced = forced,
                                                           implicit = implicit,
                                                           exit_target = command.commandName )
            if not exited:
                error = True
                break
            else:
                do_update = True
            assert self.currentCommand is not old_command
            if old_command is command:
                # we're done
                break
            continue # exit more commands
        if do_update:
            # note: this can happen even if error is True
            # (when exiting multiple commands at once)
            
            ##### REVIEW: should we call self._update_model_between_commands() like old code did?
            # Note that no calls to it are implemented in USE_COMMAND_STACK case
            # (not for entering commands, either). This might cause new bugs.
            
            self._cseq_update_after_new_mode()
            pass
        
        if DEBUG_COMMAND_SEQUENCER:
            print "DEBUG_COMMAND_SEQUENCER: _f_exit_active_command returns, currentCommand is", self.currentCommand
        return

    _f_command_stack_is_locked = None # None or a reason string
    
    def _f_lock_command_stack(self, why = None):
        assert not self._f_command_stack_is_locked 
        self._f_command_stack_is_locked = why or "for some reason"
        if DEBUG_COMMAND_STACK:
            print "locking command stack:", self._f_command_stack_is_locked ###
        return

    def _f_unlock_command_stack(self):
        assert self._f_command_stack_is_locked
        self._f_command_stack_is_locked = None
        if DEBUG_COMMAND_STACK:
            print "unlocking command stack"
        return

    def _f_assert_command_stack_unlocked(self):
        assert not self._f_command_stack_is_locked, \
               "bug: command stack is locked: %r" % \
               self._f_command_stack_is_locked
        return
    
    # ==
    
    def userEnterCommand(self, commandName, always_update = False, **options):
        # TODO: needs revision or replacement for USE_COMMAND_STACK
        # todo: remove always_update from callers if ok.
        """
        Public method, called from the UI when the user asks to enter
        a specific command (named by commandName), e.g. using a toolbutton
        or menu item. It can also be called inside commands which want to
        change to another command.

        The commandName argument can be a commandName string, e.g. 'DEPOSIT',
        or a symbolic name like '$DEFAULT_MODE', or [### VERIFY THIS]
        a command instance object. (Details of commandName, and all options,
        are documented in Command._f_userEnterCommand.)

        If commandName is a command name string and we are already in that
        command, then do nothing unless always_update is true [new feature,
        080730; prior code did nothing except self._cseq_update_after_new_mode(),
        equivalent to passing always_update = True to new code].
        Note: all calls which pass always_update as of 080730 do so only
        to preserve old code behavior; passing it is probably not needed
        for most of them. [###REVIEW those calls]

        The current command has to exit (or be suspended) before the new one
        can be entered, but it's allowed to refuse to exit, and if it does
        exit it needs a chance to clean up first. So we let the current
        command implement this method and decide whether to honor the user's
        request. (If it doesn't, it should emit a message explaining why not.
        If it does, it should call the appropriate lower-level command-switching
        method [### TODO: doc what those are or where to find out].

        (If that raises an exception, we assume the current command has a bug
        and fall back to default behavior here.)

        TODO: The tool icons ought to visually indicate the current command,
        but for now this is done by ad-hoc code inside individual commands
        rather than in any uniform way. One defect of that scheme is that
        the code for each command has to know what UI buttons might invoke it;
        another is that it leads to that code assuming that a UI exists,
        complicating future scripting support. When this is improved, the
        updating of toolbutton status might be done by
        self._cseq_update_after_new_mode().
        [Note, that's now in GLPane but should probably move into this class.]
        
        @see: userEnterTemporaryCommand (which is the only caller that passes
              us any options (aside from always_update), as of before 080730)

        @see: MWsemantics.ensureInCommand
        """
        if USE_COMMAND_STACK:
            options = {}
            options['always_update'] = always_update
                # review: most options might not be needed anymore
            self.userEnterCommand_for_USE_COMMAND_STACK( commandName, **options)
            return
        
        # Note: _f_userEnterCommand has a special case for already being in
        # the same-named command, provided that is a basicCommand subclass
        # (i.e. not nullCommand). A lot of callers have a test for this
        # before the call, but they don't need it, except that it
        # avoids the call herein of self._cseq_update_after_new_mode().
        # CHANGING THIS NOW: avoid that update here too, and simplify the callers.
        # [bruce 080730]
        try:
            already_in_command = (self.currentCommand.commandName == commandName)
            
            if not already_in_command:
                self.currentCommand._f_userEnterCommand(commandName, **options)

            if always_update or not already_in_command:
                # REVIEW: the following _cseq_update_after_new_mode looks redundant with
                # the one at the end of start_using_mode, if that one has always
                # run at this point (which I think, but didn't prove).
                # [bruce 070813 comment]
                
                # TODO, maybe: let current command decide whether/how to do
                # this update:
                self._cseq_update_after_new_mode()
            pass
        except:
            # This should never happen unless there's a bug in some command --
            # so don't bother trying to get into the user's requested
            # command, just get into a safe state.
            print_compact_traceback("_f_userEnterCommand: ")
            print "bug: _f_userEnterCommand(%r) had bug when in mode %r; " \
                  "changing back to default mode" % \
                  (commandName, self.currentCommand,)
            # For some bugs, the old mode will have left its toolbar
            # up; we should probably try to call its restore_gui
            # method directly... ok, I added this, though it's
            # untested! ###k It looks safe, and only runs if there's a
            # definite bug anyway. [bruce 040924]
            try:
                self.win.setFocus() #bruce 041010 bugfix (needed in two places)
                    # (I think that was needed to prevent key events from being
                    #  sent to no-longer-shown mode dashboards. [bruce 041220])
                    # a test with USE_COMMAND_STACK (which doesn't call this line)
                    # seems to indicate that this is no longer needed [bruce 080909 comment]
                self.currentCommand.restore_gui()
                    ###REVIEW: restore_gui is probably wrong when options caused
                    # us merely to suspend, not exit, the old mode.
                    # [bruce 070814 comment]
            except:
                print "(...even the old mode's restore_gui method, " \
                      "run by itself, had a bug...)"
            self.start_using_mode( '$DEFAULT_MODE' ) # at end of userEnterCommand, in case of bug
        return

    def userEnterTemporaryCommand(self, commandName, always_update = False):
        #bruce 071011;  # needs revision or replacement for USE_COMMAND_STACK
        """
        Temporarily enter the command with the given commandName
        [TODO: or the given command object?],
        suspending the prior command for resumption after the new one exits,
        unless the prior command.command_can_be_suspended is false
        (usually the case if it too is a temporary command),
        in which case, the command that will be resumed then is the
        same one it was before entering the new command.
        (This means a series of temporary commands can be run,
        after which the prior non-temporary one will be resumed.)

        @note: semantics/API is likely to be revised; see code comments.

        @see: userEnterCommand
        """
        if USE_COMMAND_STACK:
            ### REVIEW: is this always correct?
            self.userEnterCommand(commandName,
                                  always_update = always_update )
            return

        # REVIEW: do we need to generalize command.command_can_be_suspended
        # to a relation between two commands
        # that says whether one can be suspended by another,
        # or whether one can suspend another,
        # based on which commands they are?
         
        # REVIEW: should this method be an option on userEnterCommand or
        # _f_userEnterCommand rather than a separate method? Will those need
        # to call this if the command they are asked to enter is marked as
        # being a temporary one?]

        # TODO: Whatever the answers, ultimately the command sequencer needs
        # to be responsible for deciding how to enter and exit each command,
        # rather than relying on the commands themselves to do this.
        # In particular, no command should override Done to know about
        # prevMode -- instead, the sequencer should record how the command
        # was entered and whether it suspended prevMode then. The command
        # can just declare its type and options in ways which influence
        # the sequencer re this.
        
        #bruce 071011 split this out of Zoom/Pan/Rotate support in ops_view.py;
        # also using it for Paste/Partlib commands in MWsemantics.py (not sure
        # it's identical to what they did, but if not it might be safer)

        # Implementation:
        #
        # If the current command is suspendable,
        # save it in self.prevMode (TODO: make that private)
        # and suspend it while entering the new one.
        # (For now we never have more than one suspended command
        #  at a time.)
        #
        # Otherwise, effectively, immediately exit the current command
        # (which is non-suspendable, probably temporary)
        # and don't change prevMode (so that the suspended
        # command to be resumed later is not changed),
        # and enter the new command in the normal way (###k??).
        #
        # But this is most easily done in a different way with the
        # same effect: exit the current command first (resuming prevMode)
        # and then immediately enter the new one (saving the same value
        # of prevMode again), entering it in the same way as otherwise.
        # [Implem revised by bruce 070814; comment updated by bruce 071011.]
        
        prior_command = self._raw_currentCommand # might be changed below
   
        assert not prior_command.is_null
            # neither case below looks correct for nullmode

        if not prior_command.command_can_be_suspended:
            # (This usually means we're already in a temporary command)
            # Since we can't suspend the prior command, just exit it.
            # (If this toggles off its button and runs this method recursively,
            #  that will cause bugs. TODO -- detect that, fix it if it happens.)
            prior_command.Done(exit_using_done_or_cancel_button = False)
                # presumably this reenters the prior suspended command, prevMode
                # (since there probably was one if prior_command was temporary),
                # but if so, we'll immediately resuspend it below.
            prior_command = self._raw_currentCommand # (an even more prior cmd)
            assert prior_command.command_can_be_suspended # also implies it's not null
        
        # Set self.prevMode (our depth-1 suspended command stack)
        self.prevMode = prior_command
            # bruce 070813 save command object, not commandName
        self.userEnterCommand(commandName,
                              suspend_old_mode = True,
                              always_update = always_update)
                # todo: remove always_update from callers if ok.
            # TODO: if this can become the only use of suspend_old_mode,
            # make it a private option _suspend_old_mode.
            # Indeed, it's now the only use except for internal and
            # commented out ones... [071011 eve]
        return

    # ==

    def find_innermost_command_named(self, commandName, starting_from = None):
        """
        @return: the innermost command with the given commandName attribute,
                 or None if no such command is found.
        @rtype: an active command object, or None

        @param commandName: name of command we're searching for (e.g. 'BUILD_PROTEIN')
        @type: string

        @param starting_from: if provided, start the search at this command
        @type: an active command object (*not* a command name), or None.
        """
        for command in self.all_active_commands(starting_from = starting_from):
            if command.commandName == commandName:
                return command
        return None

    def all_active_commands(self, starting_from = None):
        """
        @return: all active commands, innermost (current) first
        @rtype: list of one or more active command objects

        @param starting_from: if provided, must be an active command,
                              and the return value only includes it and
                              its parent commands (recursively).
                              Note that passing the current command is
                              equivalent to not providing this argument.
        """
        # note: could be written as a generator, but there's no need
        # (the command stack is never very deep).
        if not USE_COMMAND_STACK:
            # current code (maybe untested)
            commands = [self.currentCommand]
            if self.prevMode is not None:
                commands.append(self.prevMode)
            if starting_from is not None:
                if starting_from in commands:
                    where = commands.index(starting_from)
                    commands = commands[where:]
                        # include starting_from, but not what's before it
                else:
                    # this can happen during command transitions
                    # when current command is nullMode; for now, ignore this
                    # error if nullmode is in the list -- hopefully it'll
                    # go away after USE_COMMAND_STACK. [bruce 080801]
                    if not commands[0].is_null:
                        print "error: %r is not in %r" % (starting_from, commands)
        else:
            # new code (untested)
            if starting_from is None:
                starting_from = self.currentCommand
            # maybe: assert starting_from is an active command
            commands = [starting_from]
            command = starting_from.parentCommand # might be None
            while command is not None:
                commands.append(command)
                command = command.parentCommand
            pass
        return commands
        
    # ==
    
    # delegation to parentCommands

    def parentCommand_Draw(self, calling_command):
        """
        Draw whatever the parent command (relative to calling_command,
         a Command object) would draw in its own Draw method,
        if it was the currentCommand.
        (Exception: the parent command is allowed to find out it's
         not current and to modify its display style in response to that.)
         
        @return: True if you find a parent command and call its Draw method,
                 False otherwise.
        """
        # Note: if we wanted, the method name 'Draw' could be an argument
        # so we could delegate anything at all to the parentCommand in this way.
        # We'd need a flag or variant method to say whether to call it in
        # the Command or GraphicsMode part. (Or pass a lambda?? Seems like in
        # that case we should just let caller find the parentCommand instead...)
        if not USE_COMMAND_STACK:
            # old code (soon to be removed):
            # We define "parentCommand" relative to calling_command... but so far we only
            # know how to do that for the current command.
            # WARNING/TODO:
            # this implem assumes there is at most one saved command
            # which should be drawn. If this changes, we'll need to replace
            # self.prevMode with a deeper command stack in the Command Sequencer
            # which provides a way to draw whatever each suspended command
            # thinks it needs to; or we'll need to arrange for prevMode
            # to *be* that stack, delegating Draw to each stack element in turn.
            # [bruce 071011]
            assert self._raw_currentCommand is calling_command, \
                   "parentCommand_Draw doesn't yet work except from " \
                   "currentCommand %r (was called from %r)" % \
                   ( self._raw_currentCommand, calling_command)
                # (Maybe we'll need to generalize that to knowing how to do it
                # for calling_command == prevMode too, which is presumably just
                # to return False, given the depth-1 command stack we have at
                # present.)
            parentCommand = self.prevMode
                # really a Command object of some kind -- TODO, rename to
                # _savedCommand or so
        else:
            # new code (untested and not fully implemented; 080730)
            parentCommand = calling_command.parentCommand
            # can be None, if calling_command is default command,
            # though this is unexpected and probably a bug:
            if parentCommand is None:
                print "unexpected: %r.parentCommand is None" % calling_command
            pass
        
        if parentCommand is not None:
            assert not parentCommand.is_null
            parentCommand.graphicsMode.Draw()
            return True
        return False

    # ==

    _entering_request_command = False
    _request_arguments = None
    _accept_request_results = None
    _fyi_request_data_was_accessed = False

    def callRequestCommand(self,
                           commandName,
                           arguments = None,
                           accept_results = None
                          ): #bruce 080801
        """
        "Call" the specified request command (asynchronously -- push it on the
        command stack and return immediately).

        As it's entered (during this method call), it will record the given
        arguments (a tuple, default ()) for use by the request command.

        When it eventually exits (never during this method call, and almost
        always in a separate user event handler from this method call),
        it will call accept_results with the request results
        (or with None if it was cancelled and has no results ### DECIDE whether it
        might instead just not bother to call it if canceled -- for now,
        this depends on the caller, but current callers require that this
        callback be called no matter how the request command exits).

        The request command should exit itself by calling one of its methods
        command_Done or command_Cancel (if USE_COMMAND_STACK is true),
        or by calling self.Done(exit_using_done_or_cancel_button = False)
        (for self being the request command) (if USE_COMMAND_STACK is False).
        The latter call works in both cases, during the initial implementation
        of USE_COMMAND_STACK.

        The format and nature of its arguments and results depend on
        the particular request command, but by convention (possibly
        enforced) they are always tuples.

        The accept_results callback is usually a bound method in the command
        which is calling this method.
        
        @param commandName: commandName of request command to call
        @type commandName: string

        @param arguments: tuple of request arguments (None is interpreted as ())
        @type arguments: tuple, or None

        @param accept_results: callback for returning request results
        @type accept_results: callable (required argument, can't be None) ###DOC args it takes
        """
        if arguments is None:
            arguments = ()
        assert type(arguments) == type(())

        assert accept_results is not None
        
        if USE_COMMAND_STACK:
            self._f_assert_command_stack_unlocked()
            
        assert self._entering_request_command == False
        assert self._request_arguments is None
        assert self._accept_request_results is None

        self._entering_request_command = True
        self._request_arguments = arguments
        self._accept_request_results = accept_results
        self._fyi_request_data_was_accessed = False
        
        try:
            if not USE_COMMAND_STACK:
                self.userEnterTemporaryCommand(commandName)
            else:
                self._enterRequestCommand(commandName)
                    
            if not self._fyi_request_data_was_accessed:
                print "bug: request command forgot to call _args_and_callback_for_request_command:", commandName
        finally:
            self._entering_request_command = False
            self._request_arguments = None
            self._accept_request_results = None
            self._fyi_request_data_was_accessed = False            
        
        return # from callRequestCommand

    def _f_get_data_while_entering_request_command(self): #bruce 080801
        if self._entering_request_command:
            assert self._request_arguments is not None
            assert self._accept_request_results is not None
            res = ( self._request_arguments, self._accept_request_results )
            self._fyi_request_data_was_accessed = True
        else:
            res = (None, None)
            msg = "likely bug: entering a possible request command which was not called as such using callRequestCommand"
            print_compact_stack( msg + ": ")
        return res

    # ==

    # update methods (tentative, UNTESTED) [bruce 080812]

    def _f_update_current_command(self): #bruce 080812
        """
        [private; called from baseCommand.command_post_event_ui_updater]
        
        Update the command stack, command state (for all active commands),
        and current command UI.
        """

        if self._f_command_stack_is_locked:
            # This can happen, even after I fixed the lack of gl_update
            # when ZoomToAreaMode exits (bug was unrelated to this method).
            #
            # When it happens, it's unsafe to do any updates
            # (especially those which alter the command stack).
            # todo: If this is common, then only print it when
            # DEBUG_COMMAND_SEQUENCER.
            #
            # REVIEW: do we also need something like the old
            # "stop_sending_us_events" system,
            # to protect from all kinds of events? [bruce 080829]
            if DEBUG_COMMAND_SEQUENCER_VERBOSE:
                print "DEBUG_COMMAND_SEQUENCER_VERBOSE: _f_update_current_command does nothing since command stack is locked (%s)" % \
                      self._f_command_stack_is_locked
            return
        else:
            # this is very common
            if DEBUG_COMMAND_SEQUENCER_VERBOSE:
                print "DEBUG_COMMAND_SEQUENCER_VERBOSE: _f_update_current_command called, stack not locked"
        
        self._f_assert_command_stack_unlocked()
        
        ### TODO: decide whether a command-stack update is required.
        #### what if different active cmds disagree? what if request cmd messes up the one showing the PM? ####
        
        
        # update the command stack itself, and any current command state
        # which can affect that
        
        already_called = []
        good = False # might be reset below
        while self.currentCommand not in already_called:
            command = self.currentCommand
            already_called.append( command)
            command.command_update_state() # might alter command stack
            if self.currentCommand is not command:
                # command_update_state altered command stack
                continue
            else:
                # command stack reached a fixed point without error
                good = True
                break
            pass
        if not good:
            print "likely bug: command_update_state changed current command " \
                  "away from, then back to, %r" % self.currentCommand
        # command stack should not be changed after this point
        command = self.currentCommand

        # update internal state of all active commands
        
        command.command_update_internal_state()
        assert command is self.currentCommand, \
               "%r.command_update_internal_state() should not have changed " \
               "current command (to %r)" % (command, self.currentCommand)
        # maybe: warn if default command's command_update_internal_state
        # was not called, by comparing a counter before/after

        # update current command UI
        
        command.command_update_UI()
        assert command is self.currentCommand, \
               "%r.command_update_UI() should not have changed " \
               "current command (to %r)" % (command, self.currentCommand)

        # make sure the correct Property Manager is shown.
        # (ideally this would be done by an update method in an object
        #  whose job is to control the PM slot. TODO: refactor it that way.)

        # note: we can't assume anything has kept track of which PM is shown,
        # until all code to show or hide/close it is revised.
        # So for now, just show it if the one in the UI seems to have changed.
        old_PM = self.currentCommand._KLUGE_current_PM(get_old_PM = True)
        desired_PM = self.currentCommand.propMgr
        if desired_PM is not old_PM:
            if old_PM:
                try:
                    old_PM.close() # might not be needed, if desired_PM is not None; ### REVIEW
                except:
                    # might happen for same reason as an existing common exception related to this...
                    print "fyi: discarded exception in closing %r" % old_PM
                    pass
            if desired_PM:
                desired_PM.show()
            pass

        return
        
    # ==

    if not USE_COMMAND_STACK:
        
        # new code, mostly for the transition to a real command sequencer
        # and a separate currentCommand and graphicsMode
        # [bruce 071010]

        # Note (from point of view of class GLPane, into which we are mixed):
        # external code expects self.currentCommand to always be a
        # working Command object, which has certain callable methods,
        # and expects self.graphicsMode to be a working GraphicsMode object.
        # We'll make this true as soon as possible, and
        # make sure it remains true after that -- even during
        # __init__ and during transitions between commands, when
        # no events should come unless there are reentrance
        # bugs in event processing. [bruce 040922, revised 071011]

        # We store the actual currentCommand object on self.__raw_currentCommand
        # (starts with two underscores); to set that directly (only within this
        # class's internal code), use the property for self._raw_currentCommand
        # (starts with one underscore).

        __raw_currentCommand = None

        def _get_raw_currentCommand(self):
            return self.__raw_currentCommand
        
        def _set_raw_currentCommand(self, command):
            assert isinstance(command, anyCommand)
            self.__raw_currentCommand = command
            return

        _raw_currentCommand = property( _get_raw_currentCommand, _set_raw_currentCommand)

        # Old and new code can access this in various ways;
        # these are illegal to set in new code, but setting them
        # might be allowed (with a complaint) in old code;
        # for each attribute we make a property with both set and get methods
        # (so direct sets never happen without intervention)

        # currentCommand

        def _get_currentCommand(self):
            # TODO: wrap with an API enforcement proxy for Command.
            # WARNING: if we do that, the 'is' test in isCurrentCommand
            # will need revision!
            # (Searching for ".currentCommand is" will find that test.)
            return self._raw_currentCommand

        def _set_currentCommand(self, command):
            assert 0, "illegal to set %r.currentCommand directly" % self

        currentCommand = property( _get_currentCommand, _set_currentCommand)

        pass

    else:
        # USE_COMMAND_STACK case [bruce 080814] (very similar but not the same) ### TODO: review uses of _raw_currentCommand re this ###

        # provide:
        # - a private attr we store it on directly, and modify by direct assignment;
        #   (named the same as before, __raw_currentCommand)
        #   (might be None, briefly during init or while it's being modified)
        # - get and set methods which implement _f_currentCommand, for internal & external (friend-only) use, get and set allowed
        #   - but _f_set_currentCommand can also be called directly
        #   - value can be None, otherwise might as well just use .currentCommand
        #   - if we ever wrap with proxies, this holds the not-wrapped version
        # - for back-compat (for now), make _raw_currentCommand identical to _f_currentCommand,
        #   for get and set, many internal and one external use
        # - currentCommand itself has only a get method, asserts it's not None and correct class

        __raw_currentCommand = None

        def _get_raw_currentCommand(self):
            return self.__raw_currentCommand
        
        def _set_raw_currentCommand(self, command):
            assert command is None or isinstance(command, baseCommand)
                # is it true of nullmode???#### FIX ####
            self._command_stack_change_counter += 1 #bruce 080903 new feature
            self.__raw_currentCommand = command
            return

        _raw_currentCommand = property( _get_raw_currentCommand, _set_raw_currentCommand)
        _f_currentCommand = _raw_currentCommand
        _f_set_currentCommand = _set_raw_currentCommand

        def _get_currentCommand(self):
            assert self._raw_currentCommand is not None
            return self._raw_currentCommand

        def _set_currentCommand(self, command):
            assert 0, "illegal to set %r.currentCommand directly" % self

        currentCommand = property( _get_currentCommand, _set_currentCommand)

        def command_stack_change_indicator(self):
            """
            Return the current value of a "change indicator"
            for the command stack as a whole. Any change to the command stack
            causes this to change, provided it's viewed during one of the
            command_update* methods in the Command API (see baseCommand
            for their default defs and docstrings).

            @see: same-named method in class Assembly.
            """
            return self._command_stack_change_counter
        pass
    
    # graphicsMode

    def _get_graphicsMode(self):
        # TODO: wrap with an API enforcement proxy for GraphicsMode.
        # WARNING: if we do that, any 'is' test on .graphicsMode
        # will need revision.
        # (Searching for ".graphicsMode is" will find at least one such test.)
        res = self._raw_currentCommand.graphicsMode
            # may or may not be same as self._raw_currentCommand (due to an unsplit mode)
            ### FIX in nullMode #}
        assert isinstance(res, GraphicsMode_API)
        if not GLPANE_IS_COMMAND_SEQUENCER:
            print_compact_stack( "deprecated: direct ref of cseq.graphicsMode: ") #bruce 080813
        return res

    def _set_graphicsMode(self, command):
        assert 0, "illegal to set %r.graphicsMode directly" % self

    graphicsMode = property( _get_graphicsMode, _set_graphicsMode)

    # ==

    # custom command methods [bruce 080209 moved these here from GLPane]
    ## TODO: review/rewrite for USE_COMMAND_STACK
    
    def custom_modes_menuspec(self): 
        """
        Return a menu_spec list for entering the available custom modes.
        """
        #bruce 080209 split this out of GLPane.debug_menu_items
        #e should add special text to the item for current mode (if any)
        # saying we'll reload it
        modemenu = []
        for commandName, modefile in self._custom_mode_names_files():
            modemenu.append(( commandName,
                              lambda arg1 = None, arg2 = None,
                                     commandName = commandName,
                                     modefile = modefile :
                              self._enter_custom_mode(commandName, modefile)
                                  # not sure how many args are passed
                          ))
        return modemenu
    
    def _custom_mode_names_files(self):
        #bruce 061207 & 070427 & 080306 revised this
        res = []
        try:
            # special case for cad/src/exprs/testmode.py (or .pyc)
            from utilities.constants import CAD_SRC_PATH
            ## CAD_SRC_PATH = os.path.dirname(__file__)
            for filename in ('testmode.py', 'testmode.pyc'):
                testmodefile = os.path.join( CAD_SRC_PATH, "exprs", filename)
                if os.path.isfile(testmodefile):
                    # note: this fails inside site-packages.zip (in Mac release);
                    # a workaround is below
                    res.append(( 'testmode', testmodefile ))
                    break
            if not res and CAD_SRC_PATH.endswith('site-packages.zip'):
                res.append(( 'testmode', testmodefile ))
                    # special case for Mac release (untested in built release?
                    # not sure) (do other platforms need this?)
            assert res
        except:
            if debug_flags.atom_debug:
                print "fyi: error adding testmode.py from cad/src/exprs " \
                      "to custom modes menu (ignored)"
            pass
        try:
            import platform_dependent.gpl_only as gpl_only
        except ImportError:
            pass
        else:
            modes_dir = os.path.join( self.win.tmpFilePath, "Modes")
            if os.path.isdir( modes_dir):
                for file in os.listdir( modes_dir):
                    if file.endswith('.py') and '-' not in file:
                        commandName, ext = os.path.splitext(file)
                        modefile = os.path.join( modes_dir, file)
                        res.append(( commandName, modefile ))
            pass
        res.sort()
        return res

    def _enter_custom_mode( self, commandName, modefile): #bruce 050515
        fn = modefile
        if not os.path.exists(fn) and commandName != 'testmode':
            msg = "should never happen: file does not exist: [%s]" % fn
            env.history.message( msg)
            return
        if commandName == 'testmode':
            #bruce 070429 explicit import probably needed for sake of py2app
            # (so an explicit --include is not needed for it)
            # (but this is apparently still failing to let the testmode
            # item work in a built release -- I don't know why ###FIX)
            print "_enter_custom_mode specialcase for testmode"
                #e remove this print, when it works in a built release
            import exprs.testmode as testmode
            ## reload(testmode) # This reload is part of what prevented
            # this case from working in A9 [bruce 070611]
            from exprs.testmode import testmode as _modeclass
            print "_enter_custom_mode specialcase -- import succeeded"
        else:
            dir, file = os.path.split(fn)
            base, ext = os.path.splitext(file)
            ## commandName = base
            ###e need better way to import from this specific file!
            # (Like using an appropriate function in the import-related
            #  Python library module.)
            # This kluge is not protected against weird chars in base.
            oldpath = list(sys.path)
            if dir not in sys.path:
                sys.path.append(dir)
                    # Note: this doesn't guarantee we load file from that dir --
                    # if it's present in another one on path (e.g. cad/src),
                    # we'll load it from there instead. That's basically a bug,
                    # but prepending dir onto path would risk much worse bugs
                    # if dir masked any standard modules which got loaded now.
            import platform_dependent.gpl_only as gpl_only
                # make sure exec is ok in this version
                # (caller should have done this already)
            _module = _modeclass = None
                # fool pylint into realizing this is not undefined 2 lines below
            exec("import %s as _module" % (base,))
            reload(_module)
            exec("from %s import %s as _modeclass" % (base,base))
            sys.path = oldpath
        modeobj = _modeclass(self)
            # this should put it into self._commandTable under the name
            # defined in the mode module
            # note: this self is probably supposed to be the command sequencer
        self._commandTable[commandName] = modeobj
            # also put it in under this name, if different
            ### [will this cause bugs?]
        self.userEnterCommand(commandName, always_update = True)
            # note: self is acting as the command sequencer here
        return

    pass # end of class CommandSequencer

# end
