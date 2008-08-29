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

DEBUG_USE_COMMAND_STACK = True

# ==

class baseCommand(object):
    """
    Abstract base class for command objects compatible with Command Sequencer.
    """
    # default values of command subclass constants

    # WARNING: presently some of these are overridden in anyCommand and/or basicCommand;
    # that will be cleaned up after the refactoring is complete. [bruce 080815 comment]

    command_level = CL_ABSTRACT
        #doc
    
    command_parent = None # TODO: rename this to command_parentName or ... ###
        # Subclasses should set this to the commandName of the parent command
        # they require, if any (and if that is not the default command).
        # (Whether they require a parent command at all is determined by
        #  their command_level attribute.)
        #
        # For example, BreakStrands_Command requires parent command "Build Dna",
        # so it sets this to 'BUILD_DNA' == BuildDna_EditCommand.commandName.

    # default values of instance variables; properties; access methods

    # - related to parentCommand
    
    _parentCommand = None # parent command object, when self is on command stack
    
    def _get_parentCommand( self):
        return self._parentCommand

    parentCommand = property( _get_parentCommand ) # a read-only property

    def command_is_active(self):
        """
        @return: whether self is presently on the command stack (whether or not
                 it's on top (aka current)).
        @rtype: boolean
        """
        # note: this is not as robust a definition as might be hoped.
        # iterating over the command stack and comparing the result
        # might catch more bugs.
        return self.parentCommand is not None

    # - related to a command's property manager (PM)
    
    command_has_its_own_PM = True
    
    propMgr = None # will be set to the PM to use with self (whether or not created by self)

    # == access methods

    def is_fixed_parent_command(cls):
        from commandSequencer.command_levels import FIXED_PARENT_LEVELS
        return cls.command_level in FIXED_PARENT_LEVELS
    
    is_fixed_parent_command = classmethod(is_fixed_parent_command)
        # someday: check whether this can be called directly on the class object... probably not.

    def command_that_supplies_PM(self):
        """
        Return the innermost command (of self or its parent/grandparent/etc)
        which supplies the PM when self is current. Note that this command
        will supply a value of None for the PM, if self does.

        Self must be an active command (on the command stack).

        Print a warning if any PM encountered appears to
        have .command set incorrectly.
        """
        # find innermost command whose .propMgr differs from its
        # parent's .propMgr.
        cseq = self.commandSequencer
        commands = cseq.all_active_commands( starting_from = self )
        res = None
        for command in commands:
            if not command.parentCommand or \
               command.parentCommand.propMgr is not command.propMgr:
                res = command
                break
        assert res # since outermost command has no parent
        assert res.propMgr is self.propMgr # sanity check on algorithm
        # check PM's command field
        if res.propMgr:
            ## assert res.propMgr.command is res, \
            if not (res.propMgr.command is res):
                print "\n*** BUG: " \
                   "%r.PM %r has wrong .command %r, found from %r" % \
                   (res, res.propMgr, res.propMgr.command, self)
        return res
            
    # == exit-related methods

    def command_Done(self, implicit = False): # TODO: add these to weird_to_override
        """
        Exit this command, after also exiting any subcommands it may have,
        as if its Done button was pressed.

        @param implicit: this is occurring as a result of the user asking
                         to enter some other command (not nestable under
                         this command), rather than by an explicit exit
                         request.
        @type implicit: boolean
        """
        self.commandSequencer._f_exit_active_command(self, implicit = implicit)
        return
    
    def command_Cancel(self):
        """
        Exit this command, after also exiting any subcommands it may have,
        as if its Cancel button was pressed.
        """
        self.commandSequencer._f_exit_active_command(self, cancel = True)
        return
    
    def command_Abandon(self): ###@@@ CALL ME
        """
        Abandon this command, after also abandoning as any subcommands it may
        have, by exiting it as soon as possible without changing the model
        any more than necessary. The side effects from this can be any
        combination of those from Done or Cancel, depending on the
        specific command. This is only called due to logic bugs in
        the code for opening a new file, which fail to exit all commands
        normally beforehand.
        """
        self.commandSequencer._f_exit_active_command(self, forced = True)
        return
    
    def _f_command_do_exit_if_ok(self):
        # todo: args: anything needed to decide if ok or when asking user
        """
        Exit this command (but not any other commands), when it's the current
        command, if possible or if self.commandSequencer.exit_is_forced is true,
        and return True.
        
        If not possible for some reason, emit messages as needed,
        and return False.

        @return: whether exit succeeded.
        @rtype: boolean
        
        @note: caller must only call this if this command *should* exit if
               possible, and if it's the current command (not merely an active
               command, even if it's the command which is supplying the PM).
               Deciding whether exit is needed, based on a desired next command,
               is up to the caller.

        @note: possible future change to return value: if we ask user about
               exiting, the answer might affect how or how much to exit, needed
               by caller for later stages of exiting multiple commands. In that
               case we'd need to return info about that, whenever exit succeeds.

        @note: certain attrs in self.commandSequencer (e.g. .exit_is_cancel)
               will tell self.command_will_exit which side effects to do.
               For documentation of those attrs, see CommandSequencer methods
              _f_exit_active_command and _exit_currentCommand_with_flags.
        """
        self.commandSequencer._f_lock_command_stack("preparing to exit a command")
        try:
            try:
                ok = self._command_ok_to_exit() # must explain to user if not
            except:
                _pct()
                ok = True
            
            if not ok and not self.commandSequencer.exit_is_forced:
                self._command_log("not exiting")
                return False

            try:
                self.command_will_exit() # args?
            except:
                _pct()
        finally:
            self.commandSequencer._f_unlock_command_stack()

        self._command_do_exit()

        return True

    def _command_ok_to_exit(self): # only in this file so far, 080826
        ask = self.command_exit_should_ask_user()
        if ask:
            print "asking is nim" # put up dialog with 3 choices (or more?)
                # call method on self to put it up? or determine choices anyway? (yes)
                # also, if ok to exit but only after some side effects, do those side effects.
                # (especially likely if self.commandSequencer.exit_is_forced is true; ### TODO: put this in some docstring)
        return True

    def command_exit_should_ask_user(self):# only in this file so far, 080826
        """
        [subclasses should extend this as needed,
         perhaps using self.commandSequencer.exit_is_forced]
        """
        # note: someday this may call a renamed self.haveNontrivialState() method,
        # and if that returns true, check a user pref to decide what to do.
        # Initially it's ok if it always returns False.
        return False
    
    def command_will_exit(self):
        """
        Perform side effects on self and the UI, needed when self
        is about to be exited for any reason.

        @note: when this is called, self is on top of the command stack,
               but it may or may not have been on top when the current user
               event handler started (e.g. some other command may have already
               exited during the same user event).
               
        @note: base class implementation calls self methods
               command_exit_misc_actions and command_exit_flyout.
        
        [subclasses should extend this as needed, typically calling
         superclass implementation at the end]
        """
        # note: we call these in the reverse order of how
        # command_entered calls the corresponding _enter_ methods.
        self.command_exit_misc_actions()
        self.command_exit_flyout()
        self.command_exit_PM()
        return
    
    def command_exit_PM(self):
        """
        Do whatever needs to be done to a command's PM
        when the command is about to exit. (Usually,
        nothing needs to be done.)

        [subclasses should override this as needed]
        """
        return
    
    def command_exit_flyout(self):
        """
        Undo whatever was done (to the parent command's flyout toolbar)
        by self.command_enter_flyout() when this command was entered.

        [subclasses should override this as needed]
        """
        return
    
    def command_exit_misc_actions(self):
        """
        Undo whatever was done
        by self.command_enter_misc_actions() when this command was entered.

        [subclasses should override this as needed]
        """
        return

    def _command_do_exit(self):
        """
        [private]
        pop self from the top of the command stack
        """
        if DEBUG_USE_COMMAND_STACK:
            print "_command_do_exit:", self
        assert self is self.commandSequencer._f_currentCommand, \
               "can't pop %r since it's not currentCommand %r" % \
               (self, self.commandSequencer._f_currentCommand)
        assert self._parentCommand is not None # would fail for default command
        self.commandSequencer._f_set_currentCommand( self._parentCommand )
        self._parentCommand = None
        return

    # == enter-related methods 
    
    def _command_do_enter_if_ok(self, args = None):
        """
        #doc

        @return: whether enter succeeded.
        @rtype: boolean
        
        @note: caller must only call this if this command *should* enter if possible.

        @note: always called on an instance, even if a command class alone
               could (in principle) decide to refuse entry.
        """
        self.commandSequencer._f_lock_command_stack("preparing to enter a command")
        try:
            try:
                ok = self.command_ok_to_enter() # must explain to user if not
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
        finally:
            self.commandSequencer._f_unlock_command_stack()

        self._command_do_enter() # push self on command stack

        self.commandSequencer._f_lock_command_stack("calling command_entered")
        try:
            self.command_entered() # update ui as needed # args?
        except:
            _pct()
            # but since we already entered it by then,
            # return True anyway
            # REVIEW: should caller continue entering subcommands
            # if it planned to? (for now, let it try)
        self.commandSequencer._f_unlock_command_stack()

        return True

    def command_ok_to_enter(self):
        """
        Determine whether it's ok to enter self (assuming the user has
        explicitly asked to enter self), given the current state
        of the model and command stack. If not ok, explain to user
        why not (using redmsg or dialog) and return False.
        If ok, have no visible effect and return True.
        Should never have a side effect on the model.

        @return: True if ok to enter (usual case).
        @rtype: boolean

        @note: overriding this should be rare, and is always a UI design flaw.
               Instead, commands should enter, then help the user make it ok
               to use them (e.g. help them select an appropriate argument).
                
        [a few subclasses should override or extend, most don't need to]
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
        if DEBUG_USE_COMMAND_STACK:
            print "_command_do_enter:", self
        assert self._parentCommand is None
        self._parentCommand = self.commandSequencer._f_currentCommand
        self.commandSequencer._f_set_currentCommand( self)
        return

    def command_entered(self):
        """
        Update self's command state and ui as needed, when self has just been
        pushed onto command stack. (But never modify the command stack.
        If that's necessary, do it in command_update_state.)

        @note: self may or may not still be the current command by the time
               the current user event is fully handled. It might be immediately
               "suspended upon entry" by a subcommand being pushed on top of it.

        @note: base class implementation calls other methods of self,
               command_enter_flyout and command_enter_misc_actions.

        @note: similar to old methods Enter and parts of init_gui.

        [subclasses should extend as needed, typically calling superclass
         implementation at the start]
        """

        self.graphicsMode.Enter_GraphicsMode() ### REVIEW: refactor into a subclass which defines this attr?
            # note: existing implems do some state-resetting (good) and some UI updates (bad),
            # including update_cursor. The latter is being turned off when USE_COMMAND_STACK is true.
        
        if not self.command_has_its_own_PM:
            # note: that flag must be True (so this doesn't run) in the default
            # command, since it has no self.parentCommand
            self.propMgr = self.parentCommand.propMgr
        
        self.command_enter_PM()
        self.command_enter_flyout()
        self.command_enter_misc_actions()
        return

    def command_enter_PM(self):
        """
        Do whatever needs to be done to a command's PM object (self.propMgr)
        when a command has just been entered (but don't show that PM).

        For commands which use their parent command's PM, it has already
        been assigned to self.propMgr, assuming this method is called by
        the base class implementation of command_entered (as usual)
        and that self.command_has_its_own_PM is false.
        
        In that case, this method is allowed to perform side effects on
        that "parent PM" (and this is the best place to do them),
        but this is only safe if the parent command and PM are of the expected
        class and have been coded with this in mind.

        For commands which create their own PM, typically they either do it
        in __init__, or in this method (when their PM doesn't already exist).
        A created PM is conventionally stored in self.propMgr, and publicly
        accessed from there. It will persist there even when self is not on
        the command stack.

        For many commands, nothing needs to be done by this method.

        PM signal/slot connections should typically be created just once
        when the PM is first created.

        @note: base class implementation of command_entered calls this,
               after setting self.propMgr to PM from parent command if
               self.command_has_its_own_PM is false.

        @note: some subclasses also update the PM state in this method
               (e.g EditCommand calls create_and_or_show_PM_if_wanted,
                which is often extended to call self.propMgr.updateMessage),
               but it is better to do that in an appropriate update method,
               such as self.command_update_UI() or self.propMgr.update_UI().

        [subclasses should override as needed]
        """
        return

    def command_enter_flyout(self):
        """
        incrementally modify flyout toolbar of parent command
        (available as self.parentCommand).

        @note: Called by base class implementation of command_entered.

        [subclasses should override as needed]
        """
        return

    def command_enter_misc_actions(self):
        """
        incrementally modify the state of miscellaneous UI actions
        upon entry to this command.

        @note: Called by base class implementation of command_entered.

        [subclasses should override as needed]
        """
        return

    # == update methods

    def command_post_event_ui_updater(self):
        """
        Commands can extend this if they need to optimize by completely ignoring
        some updates under certain conditions.

        Note: this is called from MWsemantics.post_event_ui_updater.

        Note that this prevents *all* active commands, or the command sequencer,
        from doing any updates in response to this method (whose base class implem
        is indirectly the only caller of any command_update_* method),
        so it's safer to optimize one of the command_update_* methods instead.
        """
        self.commandSequencer._f_update_current_command()
        return

    def command_update_state(self): ### tentative; details under discussion
        # note: likely implem of call to this: a new cseq method is called by
        # existing method command_post_event_ui_updater, which loops over the methods
        # described in the docstring
        # note: code now in model_changed and other update methods
        # is divided up into the new update methods listed here.
        """
        At the end of any user event that may have changed system state
        which may need to cause changes to the command stack or to any
        active command's state or UI, the command sequencer will call
        this method on the current command, repeating that until the
        command stack doesn't change (but never calling it twice
        on the same command, during one user event, to prevent infinite
        recursion due to bugs in specific implems of this method).

        This method is responsible for:

        - optimizing for frequent calls (e.g. for every mouse drag event),
          by checking whether anything it cares about has actually changed
          (see below for how it can do this ### change counter; once per event
           means can set self._something_changed for other methods)

        - updating any "state machines" inside this command which can
          cause it to alter the command stack

        - exiting this command and/or entering other commands, if necessary
          due to its own state or system state

        If this method doesn't change the command stack (i.e. if self remains
        the current command), then after it returns, the command sequencer
        will call self.command_update_internal_state(), which should update
        internal state for all commands on the command stack, in bottom to top
        order (see its docstring for details ### superclass calls, base implem).
        
        The command sequencer will then call self.command_update_UI()
        (and, possibly, other update_UI methods on other UI objects ###doc).
        
        @note: For any command that has a "state machine", its logic should be
               implemented within this method.

        [many subclasses must override or extend this method; when extending,
         see the docstring for the specific superclass method being extended
         to decide when to call the superclass method within the new method]
        """
        return

    def command_update_internal_state(self):
        """
        Update the internal state of this command and all parent commands.
        Self is on the command stack, but might not be the current command.

        This must update all state that might be seen by other commands or
        UI elements, even if that state is stored in self.propMgr.
        It should not update UI elements themselves, unless they are used
        to store internal state.

        This must not change the command stack (error if it does).
        Any updates which might require exiting or entering commands
        must be done earlier, in a command_update method.

        @note: the base class implementation delegates to the parent command,
               so a typical subclass implementation of this method need only
               call its superclass method in order to accomplish the "all parent
               commands" part of its responsibility. Typically it should call
               its superclass method before doing its own updates.

        @see: command_update_state, for prior updates that might change the
              command stack; see its docstring for the context of this call
              
        @see: command_update_UI, for subsequent updates of UI elements only
        """
        if self.parentCommand:
            self.parentCommand.command_update_internal_state()
        return

    def command_update_UI(self):
        """
        Update UI elements owned by or displayed by this command
        (e.g. self.propMgr and/or self's flyout toolbar) (preferably by
        calling update_UI methods in those UI elements, rather than by
        hardcoding the update algorithms, since the UI elements themselves
        may be owned by parent commands rather than self).

        Self is always the current command.

        @see: command_update_state, for prior updates that might change the
              command stack; see its docstring for the context of this call

        @see: command_update_internal_state, for prior updates that change
              internal state variables in all active commands (even if those
              are stored in their property manager objects)
        """
        if self.propMgr:
            self.propMgr.update_UI() ### IMPLEM; must work when PM is shown or not shown, and should not show it
                # note: what shows self.propMgr (if it ought to be shown but isn't)
                # is the base implem of our indirect caller,
                # commandSequencer._f_update_current_command,
                # after we return.
        
        ### maybe: also something to update the flyout toolbar, from an attribute?
        
        return
    
    # == other methods

    def _command_log(self, msg):
        print msg
    
    pass

# end
