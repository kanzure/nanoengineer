# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
baseCommand.py - base class for command objects on a command sequencer stack

NOTE: under development, not yet used as of 080730.

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""


from utilities.debug import print_compact_traceback
_pct = print_compact_traceback # local abbreviation for readability

from utilities.constants import CL_ABSTRACT 

# ==

class baseCommand(object):
    """
    Abstract base class for command objects compatible with Command Sequencer.
    """
    # default values of command subclass constants

    command_level = CL_ABSTRACT
        #doc
    
    command_parent = None # TODO: rename this to command_parent_commandName or command_parent_name or ... ###
        # Subclasses should set this to the commandName of the parent command
        # they require, if any (and if that is not the default command).
        # (Whether they require a parent command at all is determined by
        #  their command_level attribute.)
        #
        # For example, BreakStrands_Command requires parent command "Build Dna",
        # so it sets this to 'BUILD_DNA' == BuildDna_EditCommand.commandName.

    # default values of instance variables
    
    _parentCommand = None # parent command object, when self is on command stack
    
    def _get_parentCommand( self):
        return self._parentCommand

    parentCommand = property( _get_parentCommand )

    
    # == exit-related methods
    
    def _command_do_exit_if_ok(self, args = None):
        # todo: args: anything needed to decide if ok or when asking user
        """
        Exit this command (only), if possible, and return True.
        If not possible for some reason, emit messages as needed, and return False.

        @return: whether exit succeeded.
        @rtype: boolean
        
        @note: caller must only call this if this command *should* exit if possible.
               Deciding whether exit is needed, based on a desired next command,
               is up to the caller.

        @note: possible future change to return value: if we ask user about
               exiting, the answer might affect how or how much to exit, needed
               by caller for later stages of exiting multiple commands. In that
               case we'd need to return info about that, whenever exit succeeds.
        """
        try:
            ok = self._command_ok_to_exit(args) # must explain to user if not
        except:
            _pct()
            ok = True
        
        if not ok:
            self._command_log("not exiting")
            return False

        try:
            self.command_will_exit() # args?
        except:
            _pct()

        self._command_do_exit()

        return True

    def _command_ok_to_exit(self, args):
        ask = self.command_exit_should_ask_user(args)
        if ask:
            print "asking is nim" # put up dialog with 3 choices (or more?)
                # call method on self to put it up? or determine choices anyway? (yes)
                # also, if ok to exit but only after some side effects, do those side effects.
        return True

    def command_exit_should_ask_user(self, args):
        """
        [subclasses should extend this as needed]
        """
        return False
    
    def command_will_exit(self):
        """
        [subclasses should extend this as needed]
        """
        self.command_exit_flyout()
        return

    def command_exit_flyout(self):
        """
        Undo whatever was done (to the parent command's flyout toolbar)
        by self.command_enter_flyout() when this command was entered.

        [subclasses should override this as needed]
        """
        return
    
    def _command_do_exit(self):
        """
        [private]
        pop self from the top of the command stack
        """
        assert self is self.commandSequencer._f_currentCommand ###k
        self.commandSequencer._f_set_currentCommand( self._parentCommand )
        return

    # == enter-related methods 
    
    def _command_do_enter_if_ok(self, args = None):
        """
        #doc

        @return: whether enter succeeded.
        @rtype: boolean
        
        @note: caller must only call this if this command *should* enter if possible.

        @note: always called on an instance, even if a command class alone
               could decide to refuse entry.
        """
        try:
            ok = self.command_ok_to_enter(args) # must explain to user if not
        except:
            _pct()
            ok = True
        
        if not ok:
            self._command_log("not entering")
            return False

        try:
            self.command_prepare_to_enter() # get ready to receive events (usually a noop) # args?
        except:
            _pct()
            self._command_log("not entering due to exception")
            return False

        self._command_do_enter() # push self on command stack

        try:
            self.command_entered() # update ui as needed # args?
        except:
            _pct()
            # but since we already entered it by then,
            # return True anyway
            # REVIEW: should caller continue entering subcommands
            # if it planned to? (for now, let it try)

        return True

    def command_ok_to_enter(self, args):
        """
        #doc
        
        [some subclasses should override or extend, most don't need to]
        
        @note: must explain to user if not
        """
        return True

    def command_prepare_to_enter(self):
        """
        #doc
        
        [some subclasses should extend, most don't need to]
        """
        return

    def _command_do_enter(self):
        """
        [private]
        push self on command stack
        """
        ### guess
        self._parentCommand = self.commandSequencer._f_currentCommand ###k
        self.commandSequencer._f_set_currentCommand( self)
        return

    def command_entered(self, args):
        """
        update self's command state and ui as needed, when self has just been
        pushed onto command stack.

        @note: self may or may not still be the current command by the time
               the current user event is fully handled. It might be immediately
               "suspended upon entry" by a subcommand being pushed on top of it.

        @note: similar to old methods Enter and in some cases init_gui.

        [subclasses should extend as needed]
        """
        self.command_enter_flyout()
        return

    def command_enter_flyout(self):
        """
        incrementally modify flyout toolbar of parent command
        (available as self.XXX); self has already been pushed onto command stack
        and is presently on top of it, but other commands might be pushed
        on top of self by the time the current user event is fully processed.
        """
        return

    # == other methods

    def _command_log(self, msg):
        print msg
    
    pass

# end
