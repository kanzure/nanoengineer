# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
CommandSequencer.py - class for sequencing commands and maintaining command stack.
Each Assembly owns one of these.

@author: Bruce (partly based on older code by Josh)
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 2004 or 2005: written (partly based on older code by Josh),
as class modeMixin in modes.py, mixin class for GLPane

Bruce 071009 split into its own file

Bruce 071030 file (but not class) renamed to CommandSequencer

Bruce 2008 made "not GLPANE_IS_COMMAND_SEQUENCER" work (not yet on by default)

Bruce 2008 (with Ninad working in other files) made USE_COMMAND_STACK work

Bruce 080909 class renamed from modeMixin to CommandSequencer

Bruce 080911 turned off GLPANE_IS_COMMAND_SEQUENCER by default

Bruce 080925 remove support for GLPANE_IS_COMMAND_SEQUENCER

Ninad 2008-09-26: Turned on USE_COMMAND_STACK by default; stripped out old code

[old comment:]
roughly: mode -> command or currentCommand, ...
"""

import os
import sys

from utilities.constants import DEFAULT_COMMAND

from utilities.debug import print_compact_traceback, print_compact_stack

from utilities import debug_flags

import foundation.env as env

from commandSequencer.command_levels import allowed_parent

from command_support.modes import nullMode
from command_support.baseCommand import baseCommand # only for isinstance assertion


_DEBUG_CSEQ_INIT = False # DO NOT COMMIT with True

_SAFE_MODE = DEFAULT_COMMAND

DEBUG_COMMAND_SEQUENCER = False
_DEBUG_F_UPDATE_CURRENT_COMMAND = False
_DEBUG_COMMAND_STACK_LOCKING = False

# ==

# TODO: mode -> command or currentCommand in lots of comments, some method names

class CommandSequencer(object):
    """
    Controller/owner class for command stack and command switching behavior.

    (Each Assembly owns one of these. Before 080911/080925, it was instead
    a mixin of class GLPane.)

    External API for changing command stack (will be revised):
    to enter a given command:
    - userEnterCommand
    to exit a command (and perhaps then enter a specific new one):
    - command.command_Done, others
    other:
    - start_using_initial_mode
    - exit_all_commands

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
    # Note: works directly with some code in class baseCommand and basicCommand
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

    prevMode = property() # hopefully this causes errors on any access of it ### check this

    _command_stack_change_counter = 0
    _flyout_command_change_counter = 0

    _previous_flyout_update_indicators = None

    # these are documented in our class docstring:
    exit_is_cancel = False
    exit_is_forced = False
    warn_about_abandoned_changes = True
    exit_is_implicit = False
    exit_target = None
    enter_target = None

    pass

    def __init__(self, assy): #bruce 080813
        """
        WARNING: This only partly initializes self.
        Subsequent init calls should also be made, namely:
        - _reinit_modes, from glpane.setAssy, from _make_and_init_assy or GLPane.__init__
        - start_using_initial_mode - end of MWsemantics.__init__, or _make_and_init_assy.

        To reuse self "from scratch", perhaps with new command objects (as used to be necessary
        when self was a GLPane mixin which could be reused with a new assy)
        and/or new command classes (e.g. after a developer reloads some of them),
        first call self.exit_all_commands(), then do only the "subsequent init calls"
        mentioned above -- don't call this method again.
        """
        # todo: should try to clean up init code (see docstring)
        # now that USE_COMMAND_STACK is always true.
        if _DEBUG_CSEQ_INIT:
            print "_DEBUG_CSEQ_INIT: __init__"###

        self.assy = assy
        self.win = assy.win
        assert self.assy
        assert self.win

        # make sure certain attributes are present (important once we're a
        # standalone object, since external code expects us to have these
        # even if we don't need them ourselves) (but it's ok if they're still None)
        self.win # probably used only in EditCommand and in some methods in self
        self.assy # used in self and in an unknown amount of external code

        self._registered_command_classes = {} #bruce 080805

        self._recreate_nullmode()
        self._use_nullmode()
        # see docstring for additional inits needed as external calls
        return

    def _recreate_nullmode(self): # only called from this file, as of 080805
        self.nullmode = nullMode()
            # TODO: rename self.nullmode; note that it's semi-public [###REVIEW: what uses it?];
            # it's a safe place to absorb events that come at the wrong time
            # (mainly in case of bugs, but also happens routinely sometimes)
        return

    def _reinit_modes(self): #revised, bruce 050911, 080209
        """
        @see: docstring for __init__
        """
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

        # old docstring:
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
            # review: could this be toplevel now that GLPANE_IS_COMMAND_SEQUENCER
            # is never true? I don't know; I can't recall why this should not be
            # toplevel, though I do recall I had a good reason when I added
            # that comment fairly recently. [bruce 080925 comment]
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
        Exit all currently active commands (even the default command),
        and leave the current command as nullMode.

        During the exiting, make sure self.exit_is_forced is true
        when examined by exit-related methods in command classes.

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
        assert self.currentCommand and self.currentCommand.parentCommand
        # set attrs for telling command_will_exit what side effects to do
        self.exit_is_cancel = cancel
        self.exit_is_forced = forced
        self.warn_about_abandoned_changes = warn_about_abandoned_changes
        self.exit_is_implicit = implicit
        # set attrs to let command_exit methods construct dialog text, etc
        # (when used along with the other attrs)
        self.exit_target = exit_target # a commandName, if we're exiting it as a goal ### FIX to featurename?
        self.enter_target = enter_target # a commandName, if we're entering it as a goal ### FIX to featurename?
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

    def _use_nullmode(self):
        """
        [private]
        self._raw_currentCommand = self.nullmode
        """
        # note: 4 calls, all in this file, as of before 080805; making it private
        #
        # Note: This is only called during
        # exit_all_commands (with current command being default command),
        # and during init or reinit of self (with current command always being
        # nullMode, according to debug prints no longer present).
        #[bruce 080814/080909 comment]
        self._raw_currentCommand = self.nullmode

    def is_this_command_current(self, command):
        """
        Semi-private method for use by Command.isCurrentCommand;
        for doc, see that method.
        """
        # We compare to self._raw_currentCommand in case self.currentCommand
        # has been wrapped by an API-enforcement (or any other) proxy.
        return self._raw_currentCommand is command

# not used as of before 080929, but keep for now:
##    def _update_model_between_commands(self):
##        # review: when USE_COMMAND_STACK, this might be needed (as much as it ever was),
##        # but calling it is NIM. For now, we'll try not calling it and
##        # see if this ever matters. It may be that we even do update_parts
##        # before redraw or undo checkpoint, which makes this even less necessary.
##        # [bruce 080909 comment]
##        #bruce 050317: do update_parts to insulate new mode from prior one's bugs
##        try:
##            self.assy.update_parts()
##            # Note: this is overkill (only known to be needed when leaving
##            # extrude, and really it's a bug that it doesn't do this itself),
##            # and potentially too slow (though I doubt it),
##            # and not a substitute for doing this at the end of operations
##            # that need it (esp. once we have Undo); but doing it here will make
##            # things more robust. Ideally we should "assert_this_was_not_needed".
##        except:
##            print_compact_traceback("bug: update_parts: ")
##        else:
##            if debug_flags.atom_debug:
##                self.assy.checkparts() #bruce 050315 assy/part debug code
##        return

    def start_using_initial_mode(self, mode): #bruce 080812
        """
        [semi-private]
        Initialize self to the given initial mode,
        which must be one of the strings '$STARTUP_MODE' or '$DEFAULT_MODE',
        just after self is created or _reinit_modes is called.

        @see: docstring of __init__.

        @see: exit_all_commands
        """
        # as of 080812, this is called from 3 places:
        # - MWsemantics.__init__
        # - _make_and_init_assy
        # - extrude_reload
        assert mode in ('$STARTUP_MODE', '$DEFAULT_MODE')
        #bruce 080814 guess for USE_COMMAND_STACK case:
        self._raw_currentCommand = None ###??
        command_instance = self._find_command_instance( mode)
            # note: exception if this fails to find command (never returns false)
        entered = command_instance._command_do_enter_if_ok()
        assert entered
        return

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
        # todo: clean up the old term MODE used in the string constants
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
        # (Note: if commandName is a command object, this method just returns that object.
        #  For now, we depend on this in test_commands_init.py. [bruce 080910 comment])
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

    def userEnterCommand(self, want_commandName, always_update = False):
        """
        [main public method for changing command stack
         to get into a specified command]

        Exit and enter commands as needed, so that the current command
        has the given commandName.

        @see: userEnterCommand_OLD_DOCSTRING
        """
        ### TODO: docstring probably could use more info which is now in
        # the docstring of userEnterCommand_OLD_DOCSTRING. But most of that
        # docstring is obsolete, so I'm not just copying it here unedited.
        # [bruce 080929 comment]
        #
        # todo: remove always_update from callers if ok.

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

        if want_commandName != want_command.commandName:
            #bruce 080910
            if want_commandName is want_command:
                # this is routine when we're called from test_commands_init.py
                print "fyi: command object %r passed as want_commandName to userEnterCommand" % want_commandName
                want_commandName = want_command.commandName # make following code work
            else:
                assert 0, "commandName mismatch: userEnterCommand gets want_commandName %r, " \
                          "led to want_command %r whose commandName is %r" % \
                          (want_commandName, want_command, want_command.commandName )
                pass
            pass

        assert type(want_commandName) == type(""), "not a string: %r" % (want_commandName,) #bruce 080910

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

            next_commandName_to_enter = self._next_commandName_to_enter( self.currentCommand, want_command)
                # note: might be want_commandName; never None
            assert old_commandName != next_commandName_to_enter, \
                   "should be different: old_commandName %r, next_commandName_to_enter %r" % \
                   (old_commandName, next_commandName_to_enter)

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
            # Q: when do we call command_post_event_ui_updater, which calls command_update_state,
            #     and some related methods in the current command and/or all active commands?
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

            # review: should we call self._update_model_between_commands() like old code did?
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
        if _DEBUG_COMMAND_STACK_LOCKING:
            print "_DEBUG_COMMAND_STACK_LOCKING: locking command stack:", self._f_command_stack_is_locked ###
        return

    def _f_unlock_command_stack(self):
        assert self._f_command_stack_is_locked
        self._f_command_stack_is_locked = None
        if _DEBUG_COMMAND_STACK_LOCKING:
            print "_DEBUG_COMMAND_STACK_LOCKING: unlocking command stack"
        return

    def _f_assert_command_stack_unlocked(self):
        assert not self._f_command_stack_is_locked, \
               "bug: command stack is locked: %r" % \
               self._f_command_stack_is_locked
        return

    # ==

    def userEnterCommand_OLD_DOCSTRING(self, commandName, always_update = False):
        ### TODO: docstring needs merging into that of userEnterCommand
        """
        Public method, called from the UI when the user asks to enter
        a specific command (named by commandName), e.g. using a toolbutton
        or menu item. It can also be called inside commands which want to
        change to another command.

        The commandName argument can be a commandName string, e.g. 'DEPOSIT',
        or a symbolic name like '$DEFAULT_MODE', or [### VERIFY THIS]
        a command instance object. (Details of commandName, and all options,
        are documented in Command._f_userEnterCommand [### TODO: revise doc,
        since that method no longer exists].)

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

        @see: MWsemantics.ensureInCommand
        """
        assert 0 # this method exists only for its docstring

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
        if starting_from is None:
            starting_from = self.currentCommand
        # maybe: assert starting_from is an active command
        commands = [starting_from]
        command = starting_from.parentCommand # might be None
        while command is not None:
            commands.append(command)
            command = command.parentCommand
        return commands

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
        It should then exit itself by calling one of its methods
        command_Done or command_Cancel.

        The format and nature of the request arguments and results depend on
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

        self._f_assert_command_stack_unlocked()

        assert self._entering_request_command == False
        assert self._request_arguments is None
        assert self._accept_request_results is None

        self._entering_request_command = True
        self._request_arguments = arguments
        self._accept_request_results = accept_results
        self._fyi_request_data_was_accessed = False

        try:
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

    # update methods [bruce 080812]

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
            #
            # REVIEW: do we also need something like the old
            # "stop_sending_us_events" system (which temporarily
            # set current command to nullmode),
            # to protect from all kinds of events? [bruce 080829]
            if _DEBUG_F_UPDATE_CURRENT_COMMAND:
                print "_DEBUG_F_UPDATE_CURRENT_COMMAND: _f_update_current_command does nothing since command stack is locked (%s)" % \
                      self._f_command_stack_is_locked
            return
        else:
            # this is very common
            if _DEBUG_F_UPDATE_CURRENT_COMMAND:
                print "_DEBUG_F_UPDATE_CURRENT_COMMAND: _f_update_current_command called, stack not locked"

        self._f_assert_command_stack_unlocked()

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

        # Note: we can't assume anything has kept track of which PM is shown,
        # until all code to show or hide/close it is revised. (That is,
        # we have to assume some old code exists which shows, hides, or
        # changes the PM without telling us about it.)
        #
        # So for now, we just check whether the PM in the UI is the one we want,
        # and if not, fix that.
        old_PM = self._KLUGE_current_PM()
        desired_PM = self.currentCommand.propMgr
        if desired_PM is not old_PM:
            if old_PM:
                try:
                    old_PM.close() # might not be needed, if desired_PM is not None ### REVIEW
                except:
                    # might happen for same reason as an existing common exception related to this...
                    print "fyi: discarded exception in closing %r" % old_PM
                    pass
            if desired_PM:
                desired_PM.show()
            pass

        # let currentCommand update its flyout toolbar if command stack has
        # changed since any command last did that using this code [bruce 080910]
        flyout_update_indicators = ( self._flyout_command_change_counter, )
        if self._previous_flyout_update_indicators != flyout_update_indicators:
            self._previous_flyout_update_indicators = flyout_update_indicators
            command.command_update_flyout()
            assert command is self.currentCommand, \
                   "%r.command_update_flyout() should not have changed " \
                   "current command (to %r)" % (command, self.currentCommand)
            pass

        return # from _f_update_current_command

    def _KLUGE_current_PM(self):
        """
        private method, and a kluge;
        see KLUGE_current_PropertyManager docstring for more info
        """
        #bruce 070627; new option 080819
        #bruce 080929 moved to this file and revised
        pw = self.win.activePartWindow()
        if not pw:
            # I don't know if pw can be None
            print "fyi: _KLUGE_current_PM sees pw of None" ###
            return None
        try:
            return pw.KLUGE_current_PropertyManager()
        except:
            # I don't know if this can happen
            msg = "ignoring exception in %r.KLUGE_current_PropertyManager()" % (pw,)
            print_compact_traceback(msg + ": ")
            return None
        pass

    # ==

    # USE_COMMAND_STACK case [bruce 080814] ### TODO: review uses of _raw_currentCommand re this ###

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

        self.__raw_currentCommand = command

        self._command_stack_change_counter += 1
        if command and command.command_affects_flyout():
            self._flyout_command_change_counter += 1
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
        return

    pass # end of class CommandSequencer

# end
