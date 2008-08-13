# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Command.py -- provides class basicCommand, superclass for commands
[see also baseCommand.py, once ongoing refactoring is completed]

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

bruce 071009 split modes.py into Command.py and GraphicsMode.py,
leaving only temporary compatibility mixins in modes.py.
For prior history see modes.py docstring before the split.

TODO:

A lot of methods in class Command are private helper methods,
available to subclasses and/or to default implems of public methods,
but are not yet named as private or otherwise distinguished
from API methods. We should turn anyCommand into Command_API,
add all the API methods to it, and rename the other methods
in class Command to look private.

Methods such as basicCommand.Done, basicCommand._enterMode, 
basicCommand._exitMode and CommandSequencer.start_using_mode need cleanup
(needs to be done together).

This is happening as part of a big command sequencer refactoring
by Bruce & Ninad, circa 080812 (ongoing).
"""

from PyQt4.Qt import QToolButton

from utilities.debug import print_compact_traceback, print_compact_stack

from utilities.debug_prefs import debug_pref, Choice_boolean_False ##, Choice_boolean_True

from utilities import debug_flags
from platform_dependent.PlatformDependent import shift_name
from platform_dependent.PlatformDependent import control_name
from platform_dependent.PlatformDependent import context_menu_prefix

from foundation.FeatureDescriptor import find_or_make_FeatureDescriptor
from foundation.FeatureDescriptor import basicCommand_Descriptor
from foundation.FeatureDescriptor import register_abstract_feature_class

from foundation.state_utils import StateMixin

from utilities.constants import noop

from utilities.GlobalPreferences import USE_COMMAND_STACK

from model.jigs import Jig
    # this is used only for cmenu making
    # TODO: probably it should be factored into a method on the object being tested

from command_support.GraphicsMode_API import GraphicsMode_API

from command_support.baseCommand import baseCommand # warning: modified below, if not USE_COMMAND_STACK

# ==

class anyCommand(object, StateMixin):
    """
    abstract superclass for all Command objects, including nullCommand
    """
    #bruce 071008 added object superclass; 071009 split anyMode -> anyCommand

    # Default values for command-object or command-subclass attributes.
    # External code assumes every command has these attributes, but it should
    # treat them as read-only; command-related code (in this file) can override
    # them in subclasses and/or instances, and modify them directly.

    # note: soon, command_level and command_parent will be inherited from
    # a new superclass baseCommand.

    from utilities.constants import CL_ABSTRACT
    command_level = CL_ABSTRACT
        # command_level is not yet documented, part of command stack refactoring
    
    command_parent = None
        # Subclasses should set this to the commandName of the parent command
        # they require, if any (and if that is not the default command).
        # (Whether they require a parent command at all is determined by
        #  their command_level attribute.)
        #
        # For example, BreakStrands_Command requires parent command "Build Dna",
        # so it sets this to 'BUILD_DNA' == BuildDna_EditCommand.commandName.
        # This attr is used in a revised command stack scheme as of 2008-07-28
        # (still being developed).
    
    is_null = False # overridden only in nullCommand
    
    # internal name of command, e.g. 'DEPOSIT',
    # only seen by users in "debug" error messages;
    # might be used to create some prefs_keys and/or in some prefs values
    # [but I don't know if any such uses remain -- bruce 080727 comment]
    commandName = "(bug: missing commandName 1)" 

    featurename = ""
    
    # Command's property manager. Subclasses should initialize the propMgr object 
    # if they need one. [in command_enter_PM (after refactoring) or __init__]
    propMgr = None

    
    # note: the following 2 command_ attributes may be ignored or revised
    # after the current command stack refactoring is complete [070830]:
    
    command_can_be_suspended = False
        # Boolean; whether this command can be suspended while temporary commands run,
        # to be resumed when they finish. Should be True for most real commands
        # (so is True in basicCommand) but is often False for other temporary commands.
        # [bruce 071011]

    command_should_resume_prevMode = False
        # Boolean; whether this command, when exiting, should resume the prior command
        # if one is saved as commandSequencer.prevMode
        # (which it is presumed to have suspended when it was entered).
        # TODO: make this also control whether it *does* save prevMode when it's entered;
        # presently that is done by entering it using a special method,
        # commandSequencer.userEnterTemporaryCommand.
        # [bruce 071011, to be revised (replaces need for customized Done methods)]
    
    command_has_its_own_PM = True
        # note: following comment predates the command stack refactoring circa 080806.
        # This flag now means only that the command should create its own PM
        # in self.propMgr rather than letting one from the parent (if any)
        # remain visible.
        #
        #command_has_its_own_PM means, for example, the command has its own PM,
        #and flyout toolbar and/or the Done/Cancel button corner (confirmation 
        #corner). 
        #For most of the commands, this is True (e.g. BuildAtoms mode , 
        #BuildCrystal Mode, DnaDuplexEdit Controller etc.) 
        # For many temporary commands #such as Zoom/Pan/Rotate/LineMode 
        # it is False. That means when the temporary command is active, 
        # it is only doing some thing in the glpane and giving the user an 
        # impression as if he is still in the previous command he was 
        # working on. A good example is PanMode. If user is in Build Atoms mode
        # and needs to Pan the view, he can simply activate the PanTool(PanMode)
        # The PanMode, being the temporary mode, has not gui of its own. All it 
        # needs to do is to Pan the view. Thus it continues to use the PM and 
        # flyout toolbar from Build Atoms mode, giving the user an impression
        # that he is still operating on the old mode.         
        # This flag is also used in fixing bugs like 2566. 
        # When user exits these temporary modes(i.e. 'tempoary commands') ,
        # with this flag set to 'False', it skips the init_gui method etc. 
        # of the previous mode, while resuming 'that' (previouse) mode. 
        # This flag also means that if you hit 'Done' or 'Cancel' of the
        # previous mode (while in a temporary mode) , then 'that previous mode'
        # will exit. The related code makes sure to first leave the temporary 
        # mode(s) before leaving the regular mode (the command with 
        # command_has_its_own_PM set to True). See also, flag 
        # 'exit_using_done_cancel' in basicCommand.Done used (= False) for a 
        # typical exit of a temporary mode . See that method for detailed 
        # comment. -- Ninad 2007-11-09
    
    
    # (default methods that should be noops in both nullCommand and Command
    #  can be put here instead if desired; for docstrings, see basicCommand)
    
    def model_changed(self): #bruce 070925; TODO [bruce 080804]: revise/rename (in Commands and their PMs)
        return
    
    def command_post_event_ui_updater(self): #bruce 070925; bruce 080812 renamed this, from state_may_have_changed
        """
        This is called after every user event (###verify).
        Overridden only in basicCommand as of 080731 (###describe).
        """
        # note: called by MWsemantics.post_event_ui_updater [080731 comment]
        return

    def isCurrentCommand(self): #bruce 071008
        # WARNING: this value of False means the nullCommand should never itself
        # run code which assumes that this returns true when self is current.
        # The reason for this stub value is in case this method is ever called on nullCommand
        # at an early stage of startup, before the usual method would work.
        return False

    def get_featurename(self):
        return "null command" # should never be seen [revised, bruce 080727]

    def keep_empty_group(self, group): #bruce 080305
        """
        When self is the current command, and an empty group with
        group.autodelete_when_empty set to true is noticed by
        self.autodelete_empty_groups(), should that group be kept
        (not killed) by that method? (Otherwise it will be killed,
        at least by the default implementation of that method.)

        @note: subclasses should override this to return True
               for certain kinds of empty groups which they want
               to preserve while they are the current command
               (and which would otherwise be deleted due to having
               group.autodelete_when_empty set).
        """
        return False

    def autodelete_empty_groups(self, topnode):
        """
        Kill all empty groups under topnode
        (which may or may not be a group)
        for which group.autodelete_when_empty is true
        and group.temporarily_prevent_autodelete_when_empty is false
        and self.keep_empty_group(group) returns False.

        But set group.temporarily_prevent_autodelete_when_empty
        on all empty groups under topnode for which
        group.autodelete_when_empty is true
        and self.keep_empty_group(group) returns True.
        
        Do this bottom-up, so killing inner empty groups
        (if it makes their containing groups empty)
        subjects their containing groups to this test.

        @note: called by master_model_updater, after the dna updater.

        @note: overridden in nullCommand to do nothing. Not normally
               overridden otherwise, but can be, provided the
               flag group.temporarily_prevent_autodelete_when_empty
               is both honored and set in the same way (otherwise,
               Undo bugs like bug 2705 will result).
        """
        #bruce 080305; revised 080326 as part of fixing bug 2705
        # (to set and honor temporarily_prevent_autodelete_when_empty)
        if not topnode.is_group():
            return
        for member in topnode.members[:]:
            self.autodelete_empty_groups(member)
        if (not topnode.members and
            topnode.autodelete_when_empty and
            not topnode.temporarily_prevent_autodelete_when_empty
           ):
            if not self.keep_empty_group(topnode):
                topnode.kill()
            else:
                topnode.temporarily_prevent_autodelete_when_empty = True
                # Note: not doing this would cause bug 2705 or similar
                # if undo got back to this state during a command
                # whose keep_empty_group no longer returned True
                # for topnode, since then, topnode would get deleted,
                # and subsequent redos would be modifying incorrect state,
                # e.g. adding children to topnode and assuming it remains alive.
            pass
        return
    
    def isHighlightingEnabled(self):
        """
        Should be overridden in subclasses. Default implementation returns True
        @see: BuildAtoms_Command.isHighlightingEnabled()
        """
        return True
    
    def isWaterSurfaceEnabled(self):
        """
        Should be overridden in subclasses. Default implementation returns True
        The graphicsMode of current command calls this method to enable/disable
        water surface and for deciding whther to highlight object under cursor. 
        @see: BuildAtoms_Command.isWaterSurfaceEnabled()
        @see: BuildAtoms_GraphicsMode. 
        """
        return False
    
    pass # end of class anyCommand


class nullCommand(anyCommand):
    """
    do-nothing command (for internal use only) to avoid crashes
    in case of certain bugs during transition between commands
    """

    # needs no __init__ method; constructor takes no arguments
    
    # WARNING: the next two methods are similar in all "null objects", of which
    # we have nullCommand and nullGraphicsMode so far. They ought to be moved
    # into a common nullObjectMixin for all kinds of "null objects". [bruce 071009]
    
    def noop_method(self, *args, **kws):
        if debug_flags.atom_debug:
            print "fyi: atom_debug: nullCommand noop method called -- " \
                  "probably ok; ignored"
        return None #e print a warning?
    def __getattr__(self, attr): # in class nullCommand
        # note: this is not inherited by other Command classes,
        # since we are not their superclass
        if not attr.startswith('_'):
            if debug_flags.atom_debug:
                print "fyi: atom_debug: nullCommand.__getattr__(%r) -- " \
                      "probably ok; returned noop method" % attr
            return self.noop_method
        else:
            raise AttributeError, attr #e args?

    # Command-specific attribute null values

    # TODO: revise the 'mode' term in the following attribute names

    # (the nullCommand instance is not put into the command sequencer's _commandTable)

    is_null = True
    
    commandName = 'nullCommand'
        # this will be overwritten in the nullCommand instance
        # when the currentCommand is changing [bruce 050106]
        # [not sure if that was about commandName or msg_commandName or both]
    
    # Command-specific null methods
    
    def Done(self, *args, **kws):
        #bruce 060316 added this to remove frequent harmless debug print
        pass

    def autodelete_empty_groups(self, topnode):
        return
    
    pass # end of class nullCommand

# ==

if not USE_COMMAND_STACK:
    class baseCommand(object):
        pass

class basicCommand(baseCommand, anyCommand):
    """
    Common code between class Command (see its docstring)
    and old-code-compatibility class basicMode.
    Will be merged with class Command (keeping that one's name)
    when basicMode is no longer needed.
    """
    # TODO: split into minimalCommand, which does as little as possible
    # which meets the Command API and permits switching between commands
    # in conjunction with the Command Sequencer (e.g. it implements
    # Done, _f_userEnterCommand, init_gui, etc etc); and basicCommand, which
    # has all the rest (the basic functionality of an NE1 command).
    # (This is not urgent, since all commands should have that basic
    #  functionality. It might make things clearer or ease refactoring
    #  some of minimalCommand into the Command Sequencer.)
    # [bruce 071011 comment]
    
    # Subclasses should define the following class constants,
    # and normally need no __init__ method.
    # If they have an __init__ method, it must call Command.__init__
    # and pass the CommandSequencer in which this command can run.
    commandName = "(bug: missing commandName)"
    featurename = "Undocumented Command"
    from utilities.constants import CL_ABSTRACT
    command_level = CL_ABSTRACT

    command_can_be_suspended = True # good default value for most commands [bruce 071011]

    def __init__(self, commandSequencer):
        """
        This is called once on each newly constructed Command.
        Some kinds of Commands are constructed again each time they are
        invoked; others have a single instance which is reused for
        multiple invocations, but never across open files -- at least
        in the old mode code before 071009 -- not sure, after that).
        In the old code, it's called once per new assembly, since the
        commands store the assembly internally, and that happens once or
        twice when we open a new file, or once when we use file->close.

        This method sets up that command to be available (but not yet active)
        in that commandSequencer's _commandTable (mapping commandName to command object
        for reusable command objects -- for now that means all of them, by default --
        TODO, revise this somehow, maybe control it by a per-Command class constant).

        REVIEW: are there ever more args, or if the UI wants this to immediately
        do something, does it call some other method immediately? Guess: the latter.
        """
        glpane = commandSequencer.assy.glpane
        assert glpane
        assert glpane is commandSequencer ### TEMPORARY, only true when GLPANE_IS_COMMAND_SEQUENCER
        
        self.pw = None # pw = part window
            # TODO: remove this, or rename it -- most code uses .win for the same thing
                
        # verify self.commandName is set for our subclass
        assert not self.commandName.startswith('('), \
            "bug: commandName class constant missing from subclass %s" % \
            self.__class__.__name__
        
        # check whether subclasses override methods we don't want them to
        # (after this works I might remove it, we'll see)
        ### bruce 050130 removing 'Done' temporarily; see PanMode.Done for why.
        # later note: as of 070521, we always get warned "subclass movieMode
        # overrides basicMode._exitMode". I am not sure whether this override is
        # legitimate, so I'm not removing the warning for now. [bruce 070521]
        weird_to_override = ['Cancel', 'StartOver',
                             '_f_userEnterCommand', '_exitMode', 'Abandon', '_cleanup',
                             'clear', #bruce 080806
                            ]
            # not 'modifyTransmute', 'keyPress', they are normal to override;
            # not 'draw_selection_curve', 'Wheel', they are none of my business;
            # not 'makemenu' since no relation to new mode changes per se.
            # [bruce 040924]
        if USE_COMMAND_STACK and 0: # only enable this once we'll never go back...
            # also complain about commands not fully ported to the new API
            for methodname, howtofix in (
##                ('refuseEnter', ""), # only used in extrudeMode -- removed, 080806
                ('Enter', ""),
                ('init_gui', ""),
                ('resume_gui', ""),
                ('update_gui', ""),
                ('UpdateDashboard', ""),
                ('Done', ""),
                ('StateDone', ""),
                ('StateCancel', ""),
                ('restore_gui', ""),
            ):
                weird_to_override += [methodname]
                # todo: print howtofix when needed
                continue
            pass
        for attr in weird_to_override:
            def same_method(m1, m2):
                # m1/m2.im_class will differ (it's the class of the query,
                # not where func is defined), so only test im_func
                return m1.im_func == m2.im_func
            if not same_method( getattr(self, attr) ,
                                getattr(basicCommand, attr) ):
                print "fyi (for developers): subclass %s overrides basicCommand.%s; " \
                      "this is deprecated after mode changes of 040924." % \
                      (self.__class__.__name__, attr) # todo: print howtofix as well

        # other inits
        self.glpane = glpane # REVIEW: needed?
        self.win = glpane.win
        
        ## self.commandSequencer = self.win.commandSequencer #bruce 070108
        # that doesn't work, since when self is first created during GLPane creation,
        # self.win doesn't yet have this attribute:
        # (btw the exception from this is not very understandable.)
        # So instead, we define a property that does this alias, below.
        
        # Note: the attributes self.o and self.w are deprecated, but often used.
        # New code should use some other attribute, such as self.glpane or
        # self.commandSequencer or self.win, as appropriate. [bruce 070613, 071008]
        self.o = self.glpane # REVIEW: needed? (deprecated)
        self.w = self.win # (deprecated)
        
        # store ourselves in our command sequencer's _commandTable
        # [revised to call a commandSequencer method, bruce 080209]
        ###REVIEW whether this is used for anything except changing to
        # new command by name [bruce 070613 comment]
        commandSequencer.store_commandObject(self.commandName, self)
            # note: this can overwrite a prior instance of the same command,
            # e.g. when setAssy is called.

        # exercise self.get_featurename(), just for its debug prints
        self.get_featurename()
            
        return # from basicCommand.__init__

    # ==

    # remove these once we always inherit from baseCommand,
    # from which they're copied; see it for their docstrings: ###
    if not USE_COMMAND_STACK:
        def command_ok_to_enter(self):
            return True
    
    # ==
    
    def get_featurename(clas): #bruce 071227, revised into classmethod 080722
        """
        Return the "feature name" to be used for the wiki help feature page
        (not including the initial "Feature:" prefix), for this basicCommand
        concrete subclass.

        Usually, this is one or a few space-separated capitalized words.
        """
        # (someday: add debug command to list all known featurenames,
        #  by object type -- optionally as wiki help links, for testing;
        #  later: see "export command table", which does part of this)

        my_command_descriptor = find_or_make_FeatureDescriptor( clas)
            # note: this knows how to look up clas.featurename;
            # and that it might need to use basicCommand_Descriptor,
            # because that's been registered for use with all
            # subclasses of basicCommand (below).

        assert my_command_descriptor, "probably an abstract class: %r" % (clas,)

        return my_command_descriptor.featurename

    get_featurename = classmethod( get_featurename)
    
    # ==
    
    def _get_commandSequencer(self):
        return self.win.commandSequencer #bruce 070108
    
    commandSequencer = property(_get_commandSequencer)
    
    def _get_assy(self): #bruce 071116
        return self.commandSequencer.assy
    
    assy = property(_get_assy) #bruce 071116

    # ==
    
    def isCurrentCommand(self): #bruce 071008, for Command API
        """
        Return a boolean to indicate whether self is the currently active command.
        (Compares instance identity, not just class name or command name.)

        This can be used in "slot methods" that receive Qt signals from a PM
        to reject signals that are meant for a newer command object of the same class,
        in case the old command didn't disconnect those signals from its own methods
        (as it ideally should do).
        
        Warning: this is False even if self is temporarily suspended by e.g. Pan Tool,
        which has no PM of its own (so self's UI remains fully displayed); this
        needs to be considered when this method is used to determine whether UI
        actions should have an effect.

        Warning: this is False while a command is still being entered (i.e.
        during the calls of Enter and init_gui, and the first call of update_gui).
        But it's not a good idea to rely on that behavior -- if you do, you should
        redefine this function to guarantee it, and add suitable comments near the
        places which *could* in principle be modified to set .currentCommand to the
        command object being entered, earlier than they do now.
        """
        return self.commandSequencer.is_this_command_current(self)

    def set_cmdname(self, name):
        """
        Helper method for setting the cmdname to be used by Undo/Redo.
        Called by undoable user operations which run within the context
        of this Command.
        """
        self.win.assy.current_command_info(cmdname = name)

    ### TODO: move this up, and rename to indicate it's about the graphics area's
    # empty space context menus
    
    call_makeMenus_for_each_event = False
        # default value of class attribute; subclasses can override

    def setup_graphics_menu_specs(self): # review: rename/revise for new command api? not urgent. [080806]
        ### TODO: make this more easily customized, esp the web help part;
        ### TODO if possible: fix the API (also of makeMenus) to not depend
        # on setting attrs as side effect
        """
        Call self.makeMenus(), then postprocess the menu_spec attrs
        it sets on self, namely some or all of
        
        Menu_spec,
        Menu_spec_shift,
        Menu_spec_control,
        debug_Menu_spec,
        
        and make sure the first three of those are set on self
        in their final (modified) forms, ready for the caller
        to (presumably) turn into actual menus.
        
        (TODO: optim: if we know we're being called again for each event,
         optim by producing only whichever menu_specs are needed. This is
         not always just one, since we sometimes copy one into a submenu
         of another.)
        """
        # Note: this was split between Command.setup_graphics_menu_specs and
        # GraphicsMode._setup_menus, bruce 071009

        # lists of attributes of self we examine and perhaps remake:
        mod_attrs = ['Menu_spec_shift', 'Menu_spec_control']
        all_attrs = ['Menu_spec'] + mod_attrs + ['debug_Menu_spec']

        # delete any Menu_spec attrs previously set on self
        # (needed when self.call_makeMenus_for_each_event is true)
        for attr in all_attrs:
            if hasattr(self, attr):
                del self.__dict__[attr]
        
        #bruce 050416: give it a default menu; for modes we have now,
        # this won't ever be seen unless there are bugs
        #bruce 060407 update: improve the text, re bug 1739 comment #3,
        # since it's now visible for zoom/pan/rotate tools
        self.Menu_spec = [("%s" % self.get_featurename(), noop, 'disabled')]
        self.makeMenus()
            # bruce 040923 moved this here, from the subclasses;
            # for most modes, it replaces self.Menu_spec
        # bruce 041103 changed details of what self.makeMenus() should do
        
        # self.makeMenus should have set self.Menu_spec, and maybe some sister attrs
        assert hasattr(self, 'Menu_spec'), "%r.makeMenus() failed to set up" \
               " self.Menu_spec (to be a menu spec list)" % self # should never happen after 050416
        orig_Menu_spec = list(self.Menu_spec)
            # save a copy for comparisons, before we modify it
        # define the ones not defined by self.makeMenus;
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
        if debug_flags.atom_debug and self.debug_Menu_spec:
            # put the debug items into the main menu
            self.Menu_spec.extend( [None] + self.debug_Menu_spec )
            # note: [bruce 050914, re bug 971; edited 071009, 'mode' -> 'command']
            # for commands that don't remake their menus on each use,
            # the user who turns on ATOM-DEBUG won't see the menu items
            # defined by debug_Menu_spec until they remake all command objects
            # (lazily?) by opening a new file. This might change if we remake
            # command objects more often (like whenever the command is entered),
            # but the best fix would be to remake all menus on each use.
            # But this requires review of the menu-spec making code for
            # each command (for correctness when run often), so for now,
            # it has to be enabled per-command by setting
            # command.call_makeMenus_for_each_event for that command.
            # It's worth doing this in the commands that define
            # command.debug_Menu_spec.]
        
        # new feature, bruce 041103:
        # add submenus to Menu_spec for each modifier-key menu which is
        # nonempty and different than Menu_spec
        # (was prototyped in extrudeMode.py, bruce 041010]
        doit = []
        for attr, modkeyname in [
                ('Menu_spec_shift', shift_name()),
                ('Menu_spec_control', control_name()) ]:
            submenu_spec = getattr(self, attr)
            if orig_Menu_spec != submenu_spec and submenu_spec:
                doit.append( (modkeyname, submenu_spec) )
        if doit:
            self.Menu_spec.append(None)
            for modkeyname, submenu_spec in doit:
                itemtext = '%s-%s Menu' % (context_menu_prefix(), modkeyname)
                self.Menu_spec.append( (itemtext, submenu_spec) )
            # note: use PlatformDependent functions so names work on Mac or non-Mac,
            # e.g. "Control-Shift Menu" vs. "Right-Shift Menu",
            # or   "Control-Command Menu" vs. "Right-Control Menu".
            # [bruce 041014]
        if isinstance( self.o.selobj, Jig): # NFR 1740. mark 060322
            # TODO: find out whether this works at all (I would be surprised if it does,
            #  since I'd think that we'd never call this if selobj is not None);
            # if it does, put it on the Jig's cmenu maker, not here, if possible;
            # if it doesn't, also put it there if NFR 1740 remains undone and desired.
            # [bruce comment 071009]
            ##print "fyi: basicCommand.setup_graphics_menu_specs sees isinstance(selobj, Jig)"
            ##    # see if this can ever happen
            ##    # yes, this happened when I grabbed an RMotor's GLPane cmenu. [bruce 071025]
            from foundation.wiki_help import wiki_help_menuspec_for_object
            ms = wiki_help_menuspec_for_object( self.o.selobj )
            if ms:
                self.Menu_spec.append( None )
                self.Menu_spec.extend( ms )
        else:
            featurename = self.get_featurename()
            if featurename:
                from foundation.wiki_help import wiki_help_menuspec_for_featurename
                ms = wiki_help_menuspec_for_featurename( featurename )
                if ms:
                    self.Menu_spec.append( None ) # there's a bug in this separator, for cookiemode...
                        # [did I fix that? I vaguely recall fixing a separator
                        #  logic bug in the menu_spec processor... bruce 071009]
                    # might this look better before the above submenus, with no separator?
                    ## self.Menu_spec.append( ("web help: " + self.get_featurename(),
                    ##                         self.menucmd_open_wiki_help_page ) )
                    self.Menu_spec.extend( ms )
        return # from setup_graphics_menu_specs

    def makeMenus(self): # review: rename/revise for new command api? not urgent. [080806]
        ### TODO: rename to indicate it's about the graphics area's empty space context menus;
        # move above setup_graphics_menu_specs
        """
        [Subclasses can override this to assign menu_spec lists (describing
        the context menus they want to have) to self.Menu_specs (and related attributes).
        [### TODO: doc the related attributes, or point to an example that shows them all.]
        Depending on a class constant call_makeMenus_for_each_event (default False),
        this will be called once during init (default behavior) or on every mousedown
        that needs to put up a context menu (useful for "dynamic context menus").]
        """
        pass ###e move the default menu_spec to here in case subclasses want to use it?

    # ==

    # confirmation corner methods [bruce 070405-070409, 070627]

    # Note [obs?]: if we extend the conf. corner to "generators" in the short term,
    # before the "command sequencer" is implemented, some of the following methods
    # may be revised to delegate to the "current generator" or its PM.
    # If so, when doing this, note that many modes currently act as their own PM widget.

    def _KLUGE_current_PM(self): #bruce 070627
        """
        private method, and a kluge;
        see KLUGE_current_PropertyManager docstring for more info
        """
        if USE_COMMAND_STACK:
            return self.propMgr
        pw = self.w.activePartWindow()
        if not pw:
            # I don't know if pw can be None
            print "fyi: _KLUGE_current_PM sees pw of None" ###
            return None
        try:
            res = pw.KLUGE_current_PropertyManager()
            if res is not self.propMgr:
                # I think this should now be rare, now that Ninad removed
                # all official "guest PM" commands; let's find out...
                # unfortunately it's common, apparently due to a logic bug
                # in terms of when we access this vs. when various things are
                # updated, since the PMs don't match the command objects in the
                # debug prints (see below, when entering or exiting Break Strands) --
                # or maybe it's a side effect of an exception in entering it, in
                # current code? Try again when that bug is fixed... #### trying this now, 080812
                #
                ## debug note: _KLUGE_current_PM returns
                ## <dna.commands.BreakStrands.BreakStrands_PropertyManager.BreakStrands_PropertyManager
                ## object at 0xb333858>, but <commands.SelectChunks.SelectChunks_Command.SelectChunks_Command
                ## object at 0x9f66870>.propMgr is None
                #
                # [bruce 080806]
                ## pass
                print "debug note: _KLUGE_current_PM returns %r, but %r.propMgr is %r" % \
                      (res, self, self.propMgr) ### if happens, fix; if not, clean up all calls
##                assert 0, "failure in _KLUGE_current_PM, see console prints"
##                    #bruce 080812 (temporary) -- make this un-missable by
##                    # developers, for next few days -- also added 'raise' below
            return res
        except:
##            raise #bruce 080812 (temporary) -- goes with above assert 0
            # I don't know if this can happen
            msg = "ignoring exception in %r.KLUGE_current_PropertyManager()" % (pw,)
            print_compact_traceback(msg + ": ")
            return None
        pass

    def _KLUGE_visible_PM_buttons(self): #bruce 070627
        """
        private method (but ok for use by self._ccinstance), and a kluge:
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

    def want_confirmation_corner_type(self): # review: rename for new Command API? not urgent. [080806]
        """
        Subclasses should return the type of confirmation corner they
        currently want, typically computed from their current state.

        The return value can be one of the strings 'Done+Cancel' or
        'Done' or 'Cancel', or None (for no conf. corner).
        Later we may add another possible value, 'Exit'.
        [See confirmation_corner.py for related info.]
        
        [Many subclasses will need to override this; we might also revise
         the default to be computed in a more often correct manner.]
        """
        # What we do:
        # find the current PM (self or an active generator, at the moment --
        # very klugy), and ask which of these buttons are visible to it
        # (rather than using self.haveNontrivialState()):
        #   pm.done_btn.isVisibleTo(pm)
        #   pm.abort_btn.isVisibleTo(pm).
        # We also use them to perform the actions (they are QToolButtons).
        # KLUGE: we do this in other code which finds them again redundantly
        # (calling the same kluge helper function).
        if debug_pref("Conf corner test: use haveNontrivialState",
                      Choice_boolean_False,
                      prefs_key = True ):
            # old code, works, but not correct for default command or when
            # generators active.
            # REVIEW: after command stack refactoring circa 080730,
            # will this be correct?
            if self.haveNontrivialState():
                return 'Done+Cancel'
            else:
                # when would we just return 'Cancel'? only for a generator?
                return 'Done' # in future this will sometimes or always be 'Exit'
        else:
            done_button_vis, cancel_button_vis = self._KLUGE_visible_PM_buttons()
                # each one is either None, or a QToolButton (a true value)
                # currently displayed on the current PM

            res = []
            if done_button_vis:
                #For temporary commands with their own gui (the commands that
                #are expected to return to the previous command when done), 
                #use the 'Transient-Done' confirmation corner images. 
                if self.command_has_its_own_PM and \
                   self.command_should_resume_prevMode:
                    res.append('Transient-Done')
                else:
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
    
    # ==

    def warning(self, *args, **kws): # review: rename/revise for new Command API? Not urgent. [080806]
        self.o.warning(*args, **kws)

    # == methods related to entering this command
    
    def _enterMode(self, resuming = False, has_its_own_gui = True): #### obsolete after USE_COMMAND_STACK;
        # called only by self.commandSequencer.start_using_mode
        #bruce 070813 added resuming option
        """
        Friend method for command sequencer -- immediately
        enter this command, i.e. prepare it for use, not worrying at
        all about any prior current command.  Return something false
        (e.g. None) normally, or something true if you want to
        refuse entry to the new command (see comments in the call to
        this for why you might want to do that).  Note that the
        calling command sequencer has not yet set its self.currentCommand to point to us
        when it calls this method, and it will never do so unless
        we return something false (as we usually do).  Should not
        be overridden by subclasses.

        @param resuming: whether we're resuming this command (after a completed
                         subcommand); otherwise we're entering it as if anew.
                         This is for use by Subcommands resuming their parent
                         commands.
        @type resuming: bool
        @param has_its_own_gui:  This flag determines whether the current mode
                                 uses its own gui (such as PM, flyout
                                 toolbar). The flag was introduced to 
                                 fix bugs like 2566. Note that this flag is 
                                 about the  mode the user has *just exited*
                                 and not the 'new_mode' that he is has just 
                                 entered. See class anyCommand.has_its_own_gui 
                                 for a detailed comment.
                                 
        @type has_its_own_gui: boolean
        """
        assert not USE_COMMAND_STACK # obsolete otherwise [080806]
        if not resuming:
##            refused = self.refuseEnter(warn = 1)
            refused = not self.command_ok_to_enter()
            if not refused:
                # do command-specific entry initialization;
                # this method is still allowed to refuse, as well
                refused = self.Enter() 
                if refused:
                    print "fyi: late refusal by %r, better if it had been " \
                          "in command_ok_to_enter" % self # (but sometimes it might be necessary)
        else:
            refused = False
        if not refused:
            if resuming and (not has_its_own_gui):
                self.resume_gui()
                pass # Do nothing if the command doesn't have its own gui and is 
                     # going to resume the previous mode uses previous Mode Gui. 
                     # This fixes bug 2566 which used to reconnect signals in the 
                     # PM of the previous mode upon re-entering it. 
            else:
                self.init_gui()
                    ###FIX: perhaps use resume_gui instead, if resuming -- or pass that option.
                self.resume_gui()
                self.update_gui() # see also UpdateDashboard
                self.update_mode_status_text()
        # caller (our command sequencer) will set its self.currentCommand to point to us,
        # but only if we return false
        return refused

##    def refuseEnter(self, warn):
##        """
##        Subclasses should override this: examine the current
##        selection state of your command's model, and anything else you care
##        about, and decide whether you would refuse to become the
##        new current command, if asked to. If you would refuse, and if
##        warn = true, then emit an error message explaining this.
##        In any case, return whether you refuse entry (i.e. true if
##        you do, false if you don't).         
##        """
##        return 0
    
    def Enter(self):
        """
        Subclasses should override this: first call superclass.Enter(self)
        for your superclass (update 071010: for old code that might be
        basicMode, for new code it might be Command).
        
        Then set whatever internal state you need to upon being entered,
        modify settings in your command or its model or glpane (self.o) if necessary,
        and return None.
        
        If something goes wrong, so that you don't accept being the
        new current command, emit an error message explaining why
        (perhaps in a dialog or status bar), and return True -- but
        it's better if you can figure this out earlier, in
        command_ok_to_enter().        
        """
        self.UpdateDashboard() # hide Done button for Default command. Mark 050922.
        
        # TODOs:
        # - We are likely to create a Enter_Command method instead of just
        #   the 'Enter' method
        # - An example of the worry in current scheme -- what if that 
        #   update_cursor call in basicGraphicsMode.Enter_GraphicsMode tries to 
        #   use some Command attrs to decide on the cursor which are only 
        #   initialized in the subclass command.Enter? 
        # - Maybe we should call Enter_GraphicsMode in or after method 
        #   CommandSequencer.start_using_mode? Not sure if that method actually 
        #   uses some things from graphicsMode.Enter. 
        # - [bruce writes]: If calls to methods such as update_cursor (done in 
        #   Enter_GraphicsMode part) need some command attrs to be set, then,
        #   maybe in the Enter_Command scheme, the default Enter would do 
        #   3 things: Enter_Command, Enter_GM, and whatever update calls are
        #   then needed, like update_cursor . Or whoever calls Enter could do it.
        # - NOTE, the split Enter method (Enter_GraphicsMode and proposed 
        #   Enter_Command method) scheme doesn't consider the effect 
        #   on the non-split modes such as modifyMode. But some basic tests 
        #   indicate that this may not be an issue. (looks safe)
        # [Ninad 2007-12-28 comment]
                
        self.graphicsMode.Enter_GraphicsMode()
        
        return None
    
    def should_exit_when_ESC_key_pressed(self):
        """
        Returns whether the command should exit when the ESC key is pressed.
        May be overridden in subclasses. 
        
        Default implementation does the following: 
        If its going to resume the previous command
        (which can be verified using attr command_should_resume_prevMode). For 
        now, if you hit Escape key in all such commands, the command will 
        exit. 
        @see: class ESC_to_exit_GraphicsMode_preMixin.keyPress().
        """
        return (self.command_should_resume_prevMode and not self.is_default_command())

    def init_gui(self):
        """
        Subclasses should define this to set up UI stuff like dashboards,
        cursors, toggle icons, etc.

        It should be called only once each time the command is entered.
        Therefore, it should not be called by other code (for that,
        see UpdateDashboard()), nor defined by commands to do things that
        need redoing many times while the command remains active (for that, see
        update_gui()).
        """
        pass

    def _init_gui_flyout_action( self, action_attr, parentCommandName = None ):
        """
        [helper method for command entry]
        
        If our direct parent command has the expected commandName,
        copy self.flyoutToolbar from it and call setChecked on the specified
        action in it (if it has that action) (setting self.flyoutToolbar = None
        if any of this fails by raising AttributeError, with no error message)
        and return the parent command. Otherwise return None.

        @param action_attr: attribute name of this command's action in
                            this or parent command's flyout toolbar.
                            Example: 'breakStrandAction'
        @type: string

        @param parentCommandName: commandName of expected parent command;
                                  if not provided or None, we use
                                  self.command_parent for this.
                                  Example: 'BUILD_DNA'
        @type: string

        @return: parent command, if it has expected commandName, otherwise None.
        @rtype: Command or None
        
        [helper method for use in init_gui implementations;
         might need refactoring]
        """
        #bruce 080726 split this out of init_gui methods (by Ninad)
        # of several Commands.
        if parentCommandName is None:
            parentCommandName = self.command_parent
            assert self.command_parent, \
                   "_init_gui_flyout_action in %r requires " \
                   "self.command_parent assignment" % self
        if not USE_COMMAND_STACK:
            parentCommand = self.commandSequencer.prevMode # _init_gui_flyout_action: flyoutToolbar
        else:
            #bruce 080804
            parentCommand = self.parentCommand
            assert parentCommand # should be already set by now (during command_entered)
        if parentCommand.commandName == parentCommandName:
            try:
                self.flyoutToolbar = parentCommand.flyoutToolbar
                #Need a better way to deal with changing state of the 
                #corresponding action in the flyout toolbar. To be revised 
                #during command toolbar cleanup
                action = getattr(self.flyoutToolbar, action_attr)
                action.setChecked(True)
            except AttributeError:
                # REVIEW: this could have several causes; would any of them
                # be bugs and deserve an error message? [bruce 080726 questions]
                self.flyoutToolbar = None
            return parentCommand
        else:
            if USE_COMMAND_STACK:
                print "fyi: _init_gui_flyout_action in %r found wrong kind " \
                      "of parent command" % self # not sure if this ever happens; might be a bug if so
            return None
        pass
    
    def resume_gui(self): # TODO [bruce 080804]: replace, or revise docstring; called in _enterMode; used in 3 commands [080806]
        """
        Called when this command, that was suspended earlier, is being resumed. 
        The temporary command (which was entered by suspending this command)
        might have made some changes to the model which need to be reflected 
        somehow in this resuming command. Default implementation does nothing.
        
        Example: A user enters BreakStrands_Command by suspending 
        BuildDna_EditCommand, then breaks a few strands, thereby creating new 
        strand chunks. Now when the user returns to the BuildDna_EditCommand, 
        the command's property manager needs to update the list of strands 
        because of the changes done while in BreakStrands_Command. 
        @see: BuildDna_EditCommand.resume_gui. 
        @see: self._enterMode
        """
        pass
    
    def update_gui(self): # TODO [bruce 080806]: replace the 2 defs with general update method defs; called in _enterMode and UpdateDashboard
        """
        Subclasses should define this to update their dashboard to reflect state
        that might have changed in the rest of the program, e.g. selection state
        in the model tree. Not intended to be called directly by external code;
        for that, see UpdateDashboard().
        """
        assert not USE_COMMAND_STACK # obsolete in that case
        return

    def UpdateDashboard(self): # TODO [bruce 080806]: replace defs with general update method; called by 2 commands, and basicCommand.Enter.
        """
        Public method, meant to be called only on the current command object:

        Make sure this command's UI is updated before the processing of
        the current user event is finished, by calling its update_gui method
        (and perhaps doing a few other things).

        External code that might change things which some commands
        need to reflect in their UI should call this one or more times
        after any such changes, before the end of the same user event.

        Multiple calls per event are ok (but in the initial implem might
        be slow). Subclasses should not override this; for that, see update_gui().

        @note: this method is misnamed, since commands now have PMs rather
        than dashboards, but it applies to any sort of UI except the GLPane.

        @note: overriding update_gui is now deprecated -- new Commands
        should define model_changed (to be renamed) instead -- but until we revise
        depositMode and its subclasses to define one or more of those instead
        of update_gui (which is a good cleanup to do when we have time),
        we can't remove updateDashboard or existing calls to it.
        [bruce 071221, revised 080804]
        """
        # @attention: Need to ask Bruce whether this method can be removed since
        # there are no longer any dashboards. [--mark]
        #
        # Reply:
        # I looked into this, and it can't yet be removed -- depositMode
        # and some of its subclasses are relying on it (it calls update_gui,
        # and they rely on that to set up and maintain a list of
        # pastable objects, and perhaps for other reasons).
        #
        # See also my additions to the docstring.
        #
        # However, it's possible that this method's effect on
        # self.w.toolsDoneAction could be removed; I don't know.
        # If that makes a visible difference that we rely on
        # (in any commands, not just depositMode), then it can't
        # be removed (until we reimplement that effect in some
        # other way), but I have not tried to find out whether it does.
        #
        # [bruce 071221]
        
        # For now, this method just updates the dashboard immediately.
        # This might be too slow if it's called many times per event, so someday
        # we might split this into separate invalidation and update code;
        # this will then be the invalidation routine, in spite of the name.
        # We *don't* also call update_mode_status_text -- that's separate.
        
        # This shows the Done button on the dashboard unless the current
        # command is the Default command. Resolves bug #958 and #959.
        # [Mark 050922]
        if self.is_default_command(): #bruce 060403, 080709 revised this
            self.w.toolsDoneAction.setVisible(0)
        else:
            self.w.toolsDoneAction.setVisible(1)

        # call update_gui if legal
        if self.isCurrentCommand(): #bruce 050122 added this condition
            self.update_gui()
        
        return

    def is_default_command(self): #bruce 080709 refactoring
        return self.commandName == self.commandSequencer.default_commandName()
    
    def update_mode_status_text(self):
        # REVIEW: still needed after command stack refactoring? noop now.
        # [bruce 080717 comment]
        """
        new method, bruce 040927; here is my guess at its doc
        [maybe already obs?]:

        Update the command-status widget to show
        the currently correct command-status text for this command.
        Subclasses should not override this; its main purpose is to
        know how to do this in the environment of any command.  This
        is called by the standard command-entering code when it's sure
        we're entering a new command, and whenever it suspects the
        correct status text might have changed (e.g. after certain
        user events #nim).  It can also be called by modes
        themselves when they think the correct text might have
        changed. To actually *specify* that text, they should do
        whatever they need to do (which might differ for each command)
        to change the value which would be returned by their
        command-specific method get_mode_status_text()
        [which no longer exists as of 080717 since all calls were removed].
        """
        self.w.update_mode_status( mode_obj = self)
            # note: mode_obj = self is needed in case
            # glpane.currentCommand == nullMode at the moment.

    if not USE_COMMAND_STACK:
        def command_post_event_ui_updater(self): #bruce 080804 revision
            """
            #doc

            FYI: This is called by env.do_post_event_updates() by a registered
            "post_event_ui_updater" set up by MWsemantics. [still true 080804]
            """
            self.model_changed() # TODO: revise or rename this
            return

    def model_changed(self): #bruce 070925 added this to Command API.
        # bruce 080804 revised docstring
        # TODO [bruce 080804]: replace, or rename.
        """
        Subclasses should extend this (or make sure their self.propMgr defines
        it) to check whether any program state has changed that should be
        reflected in their UI, and if so, update their UI accordingly.

        Program state checked by any implem of this method should NOT be
        updated by this method. (At least, not normally, and doing so might
        cause bugs of a variety of kinds unless carefully analyzed --
        for example, bugs in the division of changes into undoable commands,
        or in the consistency of state which requires update calls after
        it's changed (due to relative ordering of calls of this, updaters,
        drawing, and other user events).)
        
        Program state checked by an implem of this method might include:
        - model state (see Assembly.model_change_counter)
        - selection state (see Assembly.selection_change_counter)
        - view state (see Assembly.view_change_counter)
          - should include Ortho/Perspective, but I guess it doesn't ###FIX
          - includes view center, direction, scale(?)
        - hover-highlighted object (glpane.selobj)

        This method will be called at most approximately once per user mouse or key
        event. The calling code should try to only call it when needed,
        but needn't guarantee this, so implementations should try to be fast
        when the call was not needed, e.g. by checking applicable change
        counters, or diffing old and new state.

        See also update_gui; this method is typically implemented
        more efficiently and called much more widely, and should eventually
        replace update_gui.
        """
        if self.propMgr:
            if hasattr( self.propMgr, 'model_changed'):
                self.propMgr.model_changed()
        return
    
    # methods for changing to some other command
    
    def _f_userEnterCommand(self, commandName, **options): # renamed from userSetMode [bruce 071011]
        """
        [friend method, to be called only by self.commandSequencer]
        
        User has asked to change to the command with the given commandName;
        we might or might not permit this, depending on our own state.
        If we permit it, do it (after appropriate cleanup, depending on
        options, which can include suspend_old_mode); if not, show an
        appropriate error message. Exception: if we're already in the
        requested command, do nothing.

        Special case: commandName can be an actual command instance object,
        not a command name. In that case we switch to it (if we permit
        ourselves switching to anything like it) even if it has the same
        commandname as self.
        """
        if self.commandName == commandName:
            # note that this implies commandName is a string, not a command instance
            if self.isCurrentCommand():
                # changing from the active command to itself -- do nothing
                # (special case, not equivalent to behavior without it)
                return
            else:
                # I don't think this can happen, but if it does,
                # it's either a bug or we're some fake command like nullMode. #k
                print "fyi (for developers): self.commandName == commandName %r " \
                      "but not self.isCurrentCommand() (probably ok)" % commandName
                # but fall through to change commands in the normal way
        # bruce 041007 removing code for warning about changes and requiring
        # explicit Done or Cancel if self.haveNontrivialState()
        self.Done( commandName, **options)
        return

    # methods for leaving this command (from a dashboard tool or an
    # internal request).

    # Notes on state-accumulating modes, e.g. cookie, extrude,
    # deposit [bruce 040923]:
    #
    # Each command which accumulates state, meant to be put into its
    # model (assembly) in the end, decides how much to put in as it
    # goes -- that part needs to be "undone" (removed from the
    # assembly) to support a Cancel event -- versus how much to retain
    # internally -- that part needs to be "done" (put into in the
    # assembly) upon a Done event.  (BTW, as I write this, I think
    # that only depositMode (so far) puts any state into the assembly
    # before it's Done.)
    #
    # Both kinds of state (stored in the command or in the assembly)
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
    # already put into the assembly by this command's operation (but only
    # since the last time it was entered). Either of those can also
    # emit an error message and return True to refuse to do the
    # requested operation of Done or Cancel (they normally return
    # None).  If they return True, we assume they made no changes to
    # the stored state, in the command or in the assembly (but we have no
    # way of enforcing that; bugs are likely if they get this wrong).
    #
    # I believe that exactly one of StateDone and StateCancel will be
    # called, for any way of leaving a command, except for Abandon, if
    # self.haveNontrivialState() returns true; if it returns false,
    # neither of them will be called.
    #
    # -- bruce 040923

    def Done(self, 
             new_mode = None, 
             suspend_old_mode = False,
             exit_using_done_or_cancel_button = True,
             **new_mode_options):
        """
        Called by the slot method for the Done tool in the dashboard;
        also called internally (in _f_userEnterCommand and elsewhere)
        if user asks to start a new command (new_mode) and the current
        command has decided to permit that in spite of the lack of an
        explicit Done.

        Revision of API for subclasses [bruce 040922]: Done should not be
        overridden in subclasses; instead they should override
        haveNontrivialState and/or StateDone and/or StateCancel as
        appropriate.
        
        @param exit_using_done_or_cancel_button: 
                       This flag is usually true. Only temporary modes such as 
                       Zoom/Pan/rotate , which don't have their own gui, set it 
                       to False for a regular temporary mode exit (such as 
                       pressing the 'Escape key'. Example: If user is in Build
                       Atoms mode , then invokes Pan tool, and hits 'Escape' key
                       the program, based on this flag decides whether to exit 
                       the 'Pan mode' or 'also exit build Atoms mode' .  In this 
                       case, (Escape key exit) the flag is set to False by the 
                       caller, so program knows that user actually didn't press
                       'done' or Cancel button from the Build Atoms PM. 
                       (and thus exit_using_done_or_cancel_button was 'False')
        @type exit_using_done_or_cancel_button: boolean                       
        """
        # TODO: most or all of the following should be done by the CommandSequencer
        # rather than by self. Same goes for several of the methods this calls.
        # [bruce 071011 comment]
        
        #TODO: About the  parameter exit_using_done_or_cancel_button: 
        # This is a bit complicated but is needed in the present implementation
        # and can be cleaned up while doing a general cleanup of the Done and 
        # other methods -- 2007-11-08
        
        resuming = False
        if self.command_should_resume_prevMode:
            # (Historical note: this imitates the overrides of Done formerly done
            #  in specific TemporaryCommands.)
            # TODO: review whether to do this somewhere else, so it also covers Cancel;
            # and/or refactor it further so the Command Sequencer fully handles it
            # (as said just above). # [bruce 071011 change and comment]
            ##assert not suspend_old_mode
            ##    # bruce 071011 added this; old code just pretended it was false
            
            if new_mode is None:
                try:
                    new_mode = self.commandSequencer.prevMode 
                    if new_mode and not self.command_has_its_own_PM:
                        if exit_using_done_or_cancel_button:                           
                            # This fixes bugs like 2566, 2565 
                            # @bug: But it doesn't fix the
                            # following bug: As of 2007-11-09, the 
                            # commandSequencer does 
                            # not consider various editController as commands. 
                            # Because of this, there is a bug in this 
                            # conditional. The bug and related NFR is documented
                            # in bug 2583 
                            if new_mode.command_has_its_own_PM:
                                #Example: command has a PM which in turn has a 
                                #done/cancel button or a formal way to exit a 
                                #regular mode. 
                                new_mode.Done()
                            else:
                                #new Command is a temporary mode with no special
                                #ui to exit it.
                                new_mode.Done(exit_using_done_or_cancel_button = False)
                            resuming = False
                            new_mode = None
                        else:                            
                            resuming = True
                except:
                    print_compact_traceback("bug, ignoring: ") #bruce 071011 added this
            else:
                #TEMPORARY FIX FOR BUG 2593, 2800 NEEDS CLEANUP
                # This code is not copied in Cancel 
                # method as it seems unncessary to do so (as of 2007-12-21) 
                #(This part of the code is reached only when user explicitely 
                #invokes a new command and before entering that command, we
                #execute 'autoDone' on the current command
                #If the current command is a temporary command, it is necessary
                #to properly exit the previous command from which it was invoked. 
                #before entering the 'new_mode' (not 'None' in this elase 
                #statement) The new_mode  is supplied to the this method as a 
                #parameter, This fixes bugs like 2593, 2800.  
                previous_command = self.commandSequencer.prevMode
                if previous_command is not new_mode:
                    self._exit_previous_command(exit_using_done_or_cancel_button)
            if resuming:
                new_mode_options['resuming'] = True
                new_mode_options['has_its_own_gui'] = self.command_has_its_own_PM
            else:
                assert new_mode_options.get('resuming', False) == False
                    # bruce 071011 added this; old code just pretended it was false
        if not suspend_old_mode:
            if self.haveNontrivialState():
                # use this (tho it should be just an optim), to make sure
                # it's not giving false negatives
                refused = self.StateDone()
                if refused:
                    # subclass says not to honor the Done request
                    # (and it already emitted an appropriate message)
                    return
        new_mode_options['suspend_old_mode'] = suspend_old_mode
        
        self._exitMode( new_mode, **new_mode_options)
        if resuming:
            assert new_mode is self.commandSequencer.prevMode
            # presumably we are now back in new_mode == prevMode (having resumed it);
            # if not, print a debug warning (probably redundant with some existing error message);
            # if so, remove it from the "command stack" by setting prevMode to None.
            if new_mode is self.commandSequencer._raw_currentCommand:
                # note: this private access is a sign we belong inside CommandSequencer
                self.commandSequencer.prevMode = None
                    #bruce 071011 added this behavior; in theory it might fix bugs;
                    # if not then I think it has no effect
            else:
                print "warning: failed to enter", new_mode # remove if fully redundant
        return
    
    def _exit_previous_command(self, exit_using_done_or_cancel_button): # has exactly one call, in Done, as of 080804
        """
        NEEDS CLEANUP. Called in self.Done, when a new command to enter 
        is specified. Example: when a temporary command is not going to resume
        a previous command but rather enter a new command invoked by the user, 
        this function first exits any pending previous mode commands. 
        @see: comment in self.Done. 
        """
        assert not USE_COMMAND_STACK # this method will be replaced when USE_COMMAND_STACK is true
        previous_command = self.commandSequencer.prevMode
        #Fixed bug 2800. The original if conditional was as follows --
        #if previous_command and not self.command_has_its_own_PM
        #But it could happen that the current command is a temporary command 
        #that usually resumes the previous mode and it still has its own gui.
        #(e.g. Join Strand command). So 'if not self.command_has_its_own_PM
        #is incorrect. -- Ninad 2008-04-12. See also bug 2583
        
        if previous_command:           
            if exit_using_done_or_cancel_button:
                if previous_command.command_has_its_own_PM:
                    previous_command.Done()
                else:
                    #new Command is a temporary mode with no special
                    #ui to exit it.
                    previous_command.Done(
                        exit_using_done_or_cancel_button = False)
        return
        
    def StateDone(self):
        """
        Mode objects (e.g. cookieMode) which might have accumulated
        state which is not yet put into their model (assembly)
        should override this StateDone method to put that
        state into the model, and return None.  If, however, for
        some reason they want to refuse to let the user's Done
        event be honored, they should instead (not changing the
        model) emit an error message and return True.
        """
        assert 0, "bug: command subclass %r needs custom StateDone method, " \
                  "since its haveNontrivialState() apparently returned True" % \
               self.__class__.__name__
    
    def Cancel(self, 
               new_mode = None, 
               exit_using_done_or_cancel_button = True,
               **new_mode_options):
        """
        Cancel tool in dashboard; might also be called internally
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
                # subclass says not to honor the Cancel request
                # (and it already emitted an appropriate message)
                return      
        
        #TODO: Following code is mostly duplicated from self.Done. Need to 
        #refactor these methods to use common code
        resuming = False
        if self.command_should_resume_prevMode:
            if new_mode is None:
                try:
                    new_mode = self.commandSequencer.prevMode
                    if new_mode and not self.command_has_its_own_PM:
                        if exit_using_done_or_cancel_button:
                            # This fixes bugs like 2566, 2565 
                            # @bug: But it doesn't fix the
                            # following bug: As of 2007-11-09, the 
                            # commandSequencer does 
                            # not consider various editController as commands. 
                            # Because of this, there is a bug in this 
                            # conditional. The bug and related NFR is documented
                            # in bug 2583    
                            if new_mode.command_has_its_own_PM:
                                new_mode.Cancel()
                            else:
                                new_mode.Cancel(exit_using_don_or_cancel = False)
                                
                            resuming = False
                            new_mode = None
                        else:                            
                            resuming = True
                except:
                    print_compact_traceback("bug, ignoring: ")
            else:
                #TEMPORARY FIX FOR BUG 2593 NEEDS CLEANUP 
                #(just like in self.Done)
                # This code is not copied in Cancel 
                # method as it seems unncessary to do so (as of 2007-12-21) 
                #(This part of the code is reached only when user explicitely 
                #invokes a new command and before entering that command, we
                #execute 'autoDone' on the current command
                #If the current command is a temporary command, it is necessary
                #to properly exit the previous command from which it was invoked. 
                #before entering the 'new_mode' (not 'None' in this elase 
                #statement) The new_mode  is supplied to the this method as a 
                #parameter, This fixes bugs like 2593.  
                previous_command = self.commandSequencer.prevMode
                if previous_command is not new_mode: 
                    if previous_command and not self.command_has_its_own_PM:            
                        if exit_using_done_or_cancel_button:
                            if previous_command.command_has_its_own_PM:
                                previous_command.Cancel()
                            else:
                                #new Command is a temporary mode with no special
                                #ui to exit it.
                                previous_command.Cancel(
                                    exit_using_done_or_cancel_button = False)                                        
            if resuming:
                new_mode_options['resuming'] = True
                new_mode_options['has_its_own_gui'] = self.command_has_its_own_PM
            else:
                assert new_mode_options.get('resuming', False) == False
                    # bruce 071011 added this; old code just pretended it was false
        
        
        self._exitMode( new_mode, **new_mode_options)

    def StateCancel(self):
        """
        Mode objects (e.g. depositMode) which might have
        accumulated state directly into their model (assembly)
        should override this StateCancel method to undo
        those changes in the model, and return None.

        Alternatively, if they are unable to remove that state from
        the model (e.g. if that code is not yet implemented, or too
        hard to implement correctly), they should warn the user,
        and then either leave all state unchanged (in command object
        and model) and return True (to refuse to honor the user's
        Cancel request), or go ahead and leave the unwanted state
        in the model, and return None (which honors the Cancel but
        leaves the user with unwanted new state in the model).
        Perhaps, when they warn the user, they would ask which of
        those two things to do.
        """
        return None # this is correct for all existing modes except depositMode
                    # -- bruce 040923
        ## assert 0, "bug: command subclass %r needs custom StateCancel method, " \
        ##           "since its haveNontrivialState() apparently returned True" % \
        ##       self.__class__.__name__

    def haveNontrivialState(self):
        """
        Subclasses which accumulate state (either in the command
        object or in their model (assembly), or both) should
        override this appropriately (see long comment above for
        details). False positive is annoying, but permitted (its
        only harm is forcing the user to explicitly Cancel or Done
        when switching directly into some other command); but false
        negative would be a bug, and would cause lost state after
        Done or (for some modes) incorrectly
        uncancelled/un-warned-about state after Cancel.
        """
        return False
    
    def _exitMode(self, new_mode = None, suspend_old_mode = False, **new_mode_options): # called from Done & Cancel
        """
        Internal method -- immediately leave this command, discarding
        any internal state it might have without checking whether
        that's ok (if that check might be needed, we assume it
        already happened). Ask our command sequencer to change to new_mode
        (which might be a commandName or a command object or None), if provided
        (and if that command accepts being the new currentCommand), otherwise to
        its default command.

        [Unlikely to be overridden by subclasses.]
        """
        if not suspend_old_mode:
            self._cleanup()
        if new_mode is None:
            new_mode = '$DEFAULT_MODE'
        self.commandSequencer.start_using_mode(new_mode, **new_mode_options) # in _exitMode
            ## REVIEW: is suspend_old_mode needed in start_using_mode?
            # Tentative conclusion: its only effects would be:
            # - help us verify expected relations between flags in new mode class
            #   and suspend_old_mode (differs for temporary commands vs others)
            # - how to fall back
            #   if using the new command fails -- it would make us fall back to
            #   old command rather than to default command.
            # Ideally we'd use a
            # continuation-like style, wrapping new_mode with a fallback
            # command, and pass that as new_mode. So it's not worth fixing this
            # for now -- save it for when we have a real command-sequencer.
            # [bruce 070814 comment]
        return

    def Abandon(self):
        """
        This is only used when we are forced to Cancel, whether or not this
        is ok (with the user) to do now -- someday it should never be called.
        Basically, every call of this is by definition a bug -- but
        one that can't be fixed in the command-related code alone.
        [But it would be easy to fix in the file-opening code, once we
        agree on how.]
        """
        if self.haveNontrivialState():
            msg = "%s with changes is being forced to abandon those changes!\n" \
                  "Sorry, no choice for now." % (self.get_featurename(),)
            self.o.warning( msg, bother_user_with_dialog = 1 )
        # don't do self._exitMode(), since it sets a new current command and
        #ultimately asks command sequencer to update for that... which is
        #premature now.  #e should we extend _exitMode to accept
        #commandNames of 'nullMode', and not update? also 'default'?
        #probably not...
        self._cleanup()

    def _cleanup(self): # called only from _exitMode & Abandon, in this file; only caller of stop_sending_us_events [080805]
        """
        [guess at doc, 080806:]
        Do some things needed by all ways of exiting a command.

        [private; should not be overridden]
        """
        # (the following are probably only called together, but it's
        # good to split up their effects as documented in case we
        # someday call them separately, and also just for code
        # clarity. -- bruce 040923)
        
        if not USE_COMMAND_STACK: #bruce 080805 guess ### REVIEW
            self.commandSequencer.stop_sending_us_events( self)
                # stop receiving events from our command sequencer or glpane
                # (i.e. change current command to nullMode)
            self.restore_gui()
        self.w.setFocus() #bruce 041010 bugfix (needed in two places)
            # (I think that was needed to prevent key events from being sent to
            #  no-longer-shown command dashboards. [bruce 041220])
##        self.restore_patches()

        #### TODO: either rename the following for new command API,
        # or copy their code into new command API methods and abandon them.
        # Guess: just do them from per-subclass overrides of command_will_exit.
        # [bruce 080806 comment]
        
        self.graphicsMode.restore_patches_by_GraphicsMode() # move earlier?
        self.restore_patches_by_Command()
        self.clear_command_state() # clear our internal state, if any
        
        return # from _cleanup
        
    def restore_gui(self):
        """
        subclasses use this to restore UI stuff like dashboards, cursors,
        toggle icons, etc.
        """
        pass

    def restore_patches_by_Command(self):
        """
        subclasses should restore anything they temporarily modified in
        their environment (such as temporary objects stored in major objects
        like win or glpane or assy, or settings changes in them)

        @see: GraphicsMode.restore_patches_by_GraphicsMode
        """
        pass
    
    def clear(self): #bruce 080806 deprecated this (old name of clear_command_state) ### rename in subs, in calls
        print_compact_stack("%r is calling clear, should use new name clear_command_state: " % self)
        self.clear_command_state()
        return
    
    def clear_command_state(self):
        #bruce 080806 renamed clear -> clear_command_state;
        # semantics are tentative (call during enter too, like in Extrude? fold into command_will_exit?);
        # will be renamed again (to start with 'command_') if it remains in new Command API
        """
        subclasses with internal state should reset it to null values
        (somewhat redundant with Enter; best to clear things now)
        """
        return
        
    # [bruce comment 040923; trimmed, 080806]
    #
    # The preceding and following methods, StartOver Cancel
    # Done, handle the common tools on the dashboards.
    #
    # Each dashboard uses instances of the same tools, for a uniform
    # look and action; the tool itself does not know which command it
    # belongs to -- its action just calls glpane.currentCommand.method for the
    # current glpane (ie command sequencer) and for one of the specified methods (or ...,
    # the old name of Cancel, until we fix MWSemantics).
    #
    # Of these methods, Done and Cancel should never be customized
    # directly -- rather, subclasses for specific modes should
    # override some of the methods they call, as described in this
    # file's header comment.
    #
    # StartOver should also never be customized, since the generic
    # method here should always work.

    # other dashboard tools
    
    def StartOver(self):
        # may work (not tested recently); only callable from UI of extrude & cookie;
        # needs rename ### [bruce 080806 comment]
        #### works, but has wrong error message when nim in sketch command -- fix later [older comment]
        """
        Support Start Over action for a few commands which implement this

        [subclasses should NOT override this]
        """
        self.Cancel(new_mode = self.commandName)

    # ==

    def find_self_or_parent_command_named(self, commandName): #bruce 080801; maybe untested
        """
        Return the first command of self and its parentCommands (if any)
        which has the given commandName, or None if none does
        (often an error, but no error message is printed).
        """
        # note: this implem ought to work both before and after the
        # command stack refactoring related to USE_COMMAND_STACK;
        # after it, it could be rewritten to not use self.commandSequencer
        # at all (a nice cleanup, but not urgent or required).
        cseq = self.commandSequencer
        res = cseq.find_innermost_command_named( commandName,
                                                 starting_from = self )
        return res

    def find_parent_command_named(self, commandName): #bruce 080801; maybe untested
        """
        Return the first of self's parentCommands (if any)
        which has the given commandName, or None if none does
        (often an error, but no error message is printed).

        @note: we expect at most one active command to have a given
               commandName (at a given time), but this may not be checked
               or enforced.
        """
        # note: this implem ought to work both before and after the
        # command stack refactoring related to USE_COMMAND_STACK;
        # after it, it should be reviewed for possible simplification.
        cseq = self.commandSequencer
        commands = cseq.all_active_commands( starting_from = self )
        for command in commands[1:]: # only look at our parent commands
            if command.commandName == commandName:
                return command
        return None

    def find_parentCommand(self): #bruce 080813; won't be needed once .parentCommand always works
        cseq = self.commandSequencer
        commands = cseq.all_active_commands( starting_from = self )
        commands = commands[1:] # only look at our parent commands
        if not commands:
            res = None
        else:
            res = commands[0]
        if self.command_parent:
            assert res is self.find_parent_command_named( self.command_parent) # not sure this is always required...
        if USE_COMMAND_STACK:
            assert res is self.parentCommand
            # maybe: if not, add a property to make this always true... then use it
            # to replace all calls of _reuse_attr_of_parentCommand with direct assignments.
        return res

    def _reuse_attr_of_parentCommand(self, attr_name = ''): # by Ninad; moved here by bruce 080813; might be revised
        """
        [helper method for use in subclasses; not part of Command API]
        
        Reuse the given attr of the parent command in self,
        by assigning self.attr = self.parentCommand.attr
        (in the correct way based on how parentCommand should be found).
        
        Example: reuse 'flyoutToolbar' or 'propMgr' attrs in self. 
        @see: AtomsTool_Command.command_enter_flyout() for an example.
        """        
        #@TODO: this could be a new command API method. That gets automatically
        #called based on some CL_* flags that decides whether to use certain 
        #attrs such as flyouttoolbar or PM of the parent command
        #-- Ninad 2008-08-01

        # It's not good to add this to Command API, for several reasons,
        # one of which is that it's probably not the best way to do what
        # it's doing. Also, it's only correct for commands which define
        # self.command_parent [that has been fixed as of 080813].
        #
        # For now, to avoid duplicated code, I'll add it here anyway,
        # since I want to use it in more commands.
        #
        # Ultimately, all uses of this should be replaced with direct
        # assignments of the appropriate attrs.
        # [bruce 080801/080813 comments]
        
        if not attr_name:
            print_compact_stack("bug: trying to set an attr with no name "
                                "in this command: ")
            return
        
##        parentCommand = self.find_parent_command_named( self.command_parent) ### BUG: won't work for nestable commands.
        parentCommand = self.find_parentCommand()
            #bruce 080813 generalization -- should be same when command_parent is defined,
            # but also work for nestables like Zoom
        
        if parentCommand:
            try:
                parent_attr = getattr(parentCommand, attr_name)
            except:
                msg = "bug: parent command %s doesn't have an " \
                      "attr named %r" % (parentCommand, attr_name)
                print_compact_traceback( msg + ": " )
                return                
                
            setattr(self, attr_name, parent_attr)

        else:
            msg = "bug: parent command %s not found" % self.command_parent # might be None -- todo: improve msg in that case
            print_compact_stack( msg + ": " )
        return

    # ==

    def _args_and_callback_for_request_command(self): #bruce 080801, might be revised/renamed
        """
        ###doc
        """
        assert not USE_COMMAND_STACK # nim otherwise
        cseq = self.commandSequencer
        return cseq._f_get_data_while_entering_request_command()
    
    pass # end of class basicCommand

register_abstract_feature_class( basicCommand, basicCommand_Descriptor )

# ==

class Command(basicCommand):
    """
    Subclass this class to create a new Command, or more often,
    a new general type of Command. This class contains code which
    most Command classes need. [See basicCommand docstring about
    how and when that class will be merged with this class.]

    A Command is a temporary mode of interaction
    for the entire UI which the user enters in order to accomplish
    a specific operation or kind of interaction. Some Commands exit
    very soon and on their own, but most can endure indefinitely
    until the user activates a Done or Cancel action to exit them.

    An instance of a Command subclass corresponds to a single run
    of a command, which may or may not have actually become active
    and/or still be active. Mode-like commands may repeatedly become
    active due to separate user actions, whereas operation-like commands
    are more likely to be active just once (with new instances of the
    same class being created when the user again asks for the same
    operation to occur).
    """
    # default values of class constants (often overridden by subclasses)
    
    GraphicsMode_class = None        
        # Each Command subclass must override this class constant with the
        # most abstract GraphicsMode subclass which they are able to work with.
        # In concrete Command subclasses, it must be a subclass of
        # GraphicsMode_API, whose constructor takes a single argument,
        # which will be the command instance.
        #
        # Command subclasses which inherit (say) SomeCommand can also define
        # a corresponding GraphicsMode subclass (and assign it to this class attribute)
        # using SomeCommand.GraphicsMode_class as its superclass.
        #
        # (This works when the set of methods can be known at import time.
        #  The init args, kws, and side effects needn't be known then,
        #  since the Command methods which supply them can be overridden.)
        #
        # The main issue in this scheme is the import dependence between
        # any Command subclass and the GraphicsMode methods used to
        # implement it, though logically, it'd be better if it was only
        # dependent then on the API of those GraphicsMode methods,
        # and not on their implem until it had to be instantiated.
        # Eventually, to librarify this code, we'll need to solve that problem.

    def __init__(self, commandSequencer):
        basicCommand.__init__(self, commandSequencer)
        # also create and save our GraphicsMode,
        # so command sequencer can find it inside us for use by the glpane
        # (and how does it know when we change it or we get changed,
        #  which means its GM changed?)
        self._create_GraphicsMode()
        return
    
    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
            # maybe: let caller pass something to replace this?
        assert issubclass(GM_class, GraphicsMode_API)

        args = [self] # the command is the only ordinary init argument
        kws = {} # TODO: let subclasses add kws to this
        # NOT TODO [see end of comment for why not]:
        # permit the following to sometimes share a single GM instance
        # between multiple commands (might or might not be important)
        # (possible importance: if something expensive like expr instances
        #  are cached in the GM instance itself; for now they're cached in
        #  the GLPane based on the Command or GM name, so this doesn't matter)
        # Big difficulty with that: how can graphicsMode.command point back to self?
        # We'd have to reset it with every delegation, or pass it as an argument
        # into every method (or attr get) -- definitely worse than the benefit,
        # so NEVERMIND. Instead, just share anything expensive that a GM sets up.
        
        self.graphicsMode = GM_class(*args, **kws)
        pass

    pass

commonCommand = basicCommand
    # use this for mixin classes that need to work in both basicCommand and Command

# end
