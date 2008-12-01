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

Bruce & Ninad did a big command sequencer refactoring, circa 080812

TODO:

A lot of methods in class Command are private helper methods,
available to subclasses and/or to default implems of public methods,
but are not yet named as private or otherwise distinguished
from API methods. We should turn anyCommand into Command_API,
add all the API methods to it, and rename the other methods
in class Command to look private.
"""

from PyQt4.Qt import QToolButton

from utilities.debug import print_compact_traceback, print_compact_stack

from utilities.debug_prefs import debug_pref, Choice_boolean_False

from utilities import debug_flags
from platform_dependent.PlatformDependent import shift_name
from platform_dependent.PlatformDependent import control_name
from platform_dependent.PlatformDependent import context_menu_prefix

from foundation.FeatureDescriptor import find_or_make_FeatureDescriptor
from foundation.FeatureDescriptor import basicCommand_Descriptor
from foundation.FeatureDescriptor import register_abstract_feature_class

from foundation.state_utils import StateMixin

from utilities.constants import noop

from model.jigs import Jig
    # this is used only for cmenu making
    # TODO: probably it should be factored into a method on the object being tested

from command_support.GraphicsMode_API import GraphicsMode_API

from command_support.baseCommand import baseCommand 

import foundation.changes as changes

# ==

class anyCommand(baseCommand, StateMixin):
    """
    abstract superclass for all Command objects in NE1, including nullCommand.

    @note: command base class methods are divided somewhat arbitrarily between
           baseCommand, anyCommand, and basicCommand. In some cases, methods
           defined in baseCommand are overridden in anyCommand or basicCommand.
           For more info see baseCommand docstring.
    """
    #bruce 071008 added object superclass; 071009 split anyMode -> anyCommand

    # Default values for command-object or command-subclass attributes.
    # External code assumes every command has these attributes, but it should
    # treat them as read-only; command-related code (in this file) can override
    # them in subclasses and/or instances, and modify them directly.

    # note: soon, command_level and command_parent, and some other of the
    # following default values, will be inherited from a new superclass baseCommand.
    __abstract_command_class = True

    featurename = ""
    
    # Command's property manager. Subclasses should initialize the propMgr object 
    # if they need one. [in command_enter_PM (after refactoring) or __init__]
    propMgr = None
    
        

    command_should_resume_prevMode = False
        # Boolean; whether this command, when exiting, should resume the prior command
        # if one is saved as commandSequencer.prevMode
        # (which it is presumed to have suspended when it was entered).
        # TODO: make this also control whether it *does* save prevMode when it's entered;
        # presently that is done by entering it using a special method,
        # commandSequencer.userEnterCommand.
        # [bruce 071011, to be revised (replaces need for customized Done methods)]
        #
        # WARNING: in the new command API as of 2008-09-26, this no longer 
        #controls command nesting as described above, but it has other effects,
        #e.g. on want_confirmation_corner_type.
    
    command_has_its_own_PM = True
        # note: following comment predates the command stack refactoring circa 080806.
        # This flag now means only that the command should create its own PM
        # in self.propMgr rather than letting one from the parent (if any)
        # remain visible.
        #
        # REVIEW: can this be replaced by bool(self.PM_class) once that's
        # fully implemented? [bruce 080905 question]
        #
        #command_has_its_own_PM means, for example, the command has its own PM,
        #and/or the Done/Cancel button corner (confirmation 
        #corner). 
        #For most of the commands, this is True (e.g. BuildAtoms mode , 
        #BuildCrystal Mode, DnaDuplexEdit Controller etc.) 
        # For many temporary commands #such as Zoom/Pan/Rotate/Line_Command 
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
        # This flag also means that if you hit 'Done' or 'Cancel' of the
        # previous mode (while in a temporary mode) , then 'that previous mode'
        # will exit. The related code makes sure to first leave the temporary 
        # mode(s) before leaving the regular mode (the command with 
        # command_has_its_own_PM set to True). See also, flag 
        # 'exit_using_done_cancel' in basicCommand.Done used (= False) for a 
        # typical exit of a temporary mode . See that method for detailed 
        # comment. -- Ninad 2007-11-09
    
    def __repr__(self): #bruce 080829, modified from Utility.py version
        """
        [subclasses can override this, and often do]
        """
        classname = self.__class__.__name__.split('.')[-1]
        return "<%s at %#x>" % (classname, id(self))

    # (default methods that should be noops in both nullCommand and Command
    #  can be put here instead if desired; for docstrings, see basicCommand)
    
    def isCurrentCommand(self): #bruce 071008
        # WARNING: this value of False means the nullCommand should never itself
        # run code which assumes that this returns true when self is current.
        # The reason for this stub value is in case this method is ever called on nullCommand
        # at an early stage of startup, before the usual method would work.
        return False

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

# ==

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

    # (the nullCommand instance is not put into the command sequencer's _commandTable)

    is_null = True
    
    commandName = 'nullCommand'
        # this will be overwritten in the nullCommand instance
        # when the currentCommand is changing [bruce 050106]
        # [not sure if that was about commandName or msg_commandName or both]
    
    # Command-specific null methods
    
    def autodelete_empty_groups(self, topnode):
        return
    
    pass # end of class nullCommand

# ==

class basicCommand(anyCommand):
    """
    Common code between class Command (see its docstring)
    and old-code-compatibility class basicMode.
    Will be merged with class Command (keeping that one's name)
    when basicMode is no longer needed.

    @note: command base class methods are divided somewhat arbitrarily between
           baseCommand, anyCommand, and basicCommand. In some cases, methods
           defined in baseCommand are overridden in anyCommand or basicCommand.
           For more info see baseCommand docstring.
    """
    # TODO: split into minimalCommand, which does as little as possible
    # which meets the Command API and permits switching between commands
    # in conjunction with the Command Sequencer; and basicCommand, which
    # has all the rest (the basic functionality of an NE1 command).
    # (This is not urgent, since all commands should have that basic
    #  functionality. It might make things clearer or ease refactoring
    #  some of minimalCommand into the Command Sequencer.)
    # (later clarification: this comment is not about _minimalCommand in
    #  test_commands.py, though that might hold some lessons for this.)
    # [bruce 071011 comment]
    
    # Subclasses should define the following class constants,
    # and normally need no __init__ method.
    # If they have an __init__ method, it must call Command.__init__
    # and pass the CommandSequencer in which this command can run.
    commandName = "(bug: missing commandName)"
    featurename = "Undocumented Command"
    
    __abstract_command_class = True

    
    PM_class = None
        #Command subclasses can override this class constant with the appropriate
        #Property Manager class, if they have their own Property Manager object.
        #This is used by self._createPropMgrObject(). 
        #See also self.command_enter_PM. 
       
        #NOTE 2008-09-02: The class constant PM_class was introduced today and 
        #will soon be used in all commands. But before that, it will be tested 
        #in a few command classes [ -- Ninad comment]. This comment can be 
        #deleted when all commands that have their own PM start using this.

        # Note: for the new command API as of 2008-09-26, this is always used,
        # since base class command_enter_PM calls _createPropMgrObject.
        # [bruce 080909]       

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
        assert glpane is not commandSequencer
            # this might happen due to bugs in certain callers,
            # since in old code they were the same object
        
        self.pw = None # pw = part window
            # TODO: remove this, or rename it -- most code uses .win for the same thing
                
        # verify self.commandName is set for our subclass
        assert not self.commandName.startswith('('), \
            "bug: commandName class constant missing from subclass %s" % \
            self.__class__.__name__
        
        # check whether subclasses override methods we don't want them to
        # (after this works I might remove it, we'll see)
        # [most methods have been removed after the command api was revised -- bruce 080929]
        weird_to_override = [ 'StartOver'                              
                             #bruce 080806
                            ]
            # not 'modifyTransmute', 'keyPress', they are normal to override;
            # not 'draw_selection_curve', 'Wheel', they are none of my business;
            # not 'makemenu' since no relation to new mode changes per se.
            # [bruce 040924]
    
        weird_to_override += [
                         'command_Done', 'command_Cancel', #bruce 080827
                        ]
        for attr in weird_to_override:
            def same_method(m1, m2):
                # m1/m2.im_class will differ (it's the class of the query,
                # not where func is defined), so only test im_func
                return m1.im_func == m2.im_func
            if not same_method( getattr(self, attr) ,
                                getattr(basicCommand, attr) ):
                print "fyi (for developers): subclass %s overrides basicCommand.%s; " \
                      "this is deprecated after mode changes of 040924." % \
                      (self.__class__.__name__, attr)

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
    
    def command_enter_PM(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_PM()  for documentation
        """
        #important to check for old propMgr object. Reusing propMgr object 
        #significantly improves the performance.
        if not self.propMgr:
            self.propMgr = self._createPropMgrObject()
            #@bug BUG: following is a workaround for bug 2494.
            #This bug is mitigated as propMgr object no longer gets recreated
            #for modes -- ninad 2007-08-29
            if self.propMgr:
                changes.keep_forever(self.propMgr)  
    
    def _createPropMgrObject(self):
        """
        Returns the property manager object for this command.
        @see: self._createFlyoutToolbarObject()
        """
        if self.PM_class is None:
            return None
    
        propMgr = self.PM_class(self)
        return propMgr
    
    def get_featurename(clas): #bruce 071227, revised into classmethod 080722
        """
        Return the "feature name" to be used for the wiki help feature page
        (not including the initial "Feature:" prefix), for this basicCommand
        concrete subclass.

        Usually, this is one or a few space-separated capitalized words.

        [overrides baseCommand method]
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
        during the calls of command_entered ).
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
                    self.Menu_spec.append( None ) 
                        # there's a bug in this separator, for BuildCrystal_Command...
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

    def _KLUGE_visible_PM_buttons(self): #bruce 070627
        """
        private method (but ok for use by self._ccinstance), and a kluge:
        return the Done and Cancel QToolButtons of the current PM,
        if they are visible, or None for each one that is not visible.

        Used both for deciding what CC buttons to show, and for acting on the buttons
        (assuming they are QToolButtons).
        """
        # note: this is now much less of a kluge, but still somewhat klugy
        # (since it makes one UI element depend on another one),
        # so I'm not renaming it. [bruce 080929 comment]
        
        pm = self.propMgr #bruce 080929 revision, used to call _KLUGE_current_PM
            # (but recently, it passed an option that made it equivalent)
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
        
        This makes use of various attrs defined on self, so it should
        be called on whichever command the confirmation corner would
        terminate, which is not necessarily the current command.

        The return value can be one of the strings 'Done+Cancel' or
        'Done' or 'Cancel', or None (for no conf. corner).
        Or it can be one of those values with 'Transient-Done' in place
        of 'Done'.

        (Later we may add other possible values, e.g. 'Exit'.)

        @see: confirmation_corner.py, for related info
        
        [Many subclasses will need to override this; we might also revise
         the default to be computed in a more often correct manner.]
        """
        # What we do:
        # find the current PM, and ask which of these buttons are visible to it:
        #   pm.done_btn.isVisibleTo(pm)
        #   pm.abort_btn.isVisibleTo(pm).
        # We also use them to perform the actions (they are QToolButtons).
        # KLUGE: we do this in other code which finds them again redundantly
        # (calling the same kluge helper function).
        
        done_button_vis, cancel_button_vis = self._KLUGE_visible_PM_buttons()
            # each one is either None, or a QToolButton (a true value),
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
        return res
        
    def should_exit_when_ESC_key_pressed(self): # not overridden, as of 080815
        """
        @return: whether this command should exit when the ESC key is pressed
        @rtype: boolean

        [May be overridden in subclasses.]
        
        Default implementation returns the value of
        self.command_should_resume_prevMode
        (except for the default command, which returns False).
        For now, if you hit Escape key in all such commands,
        the command will exit.
        
        @see: ESC_to_exit_GraphicsMode_preMixin.keyPress()
        """
        return (self.command_should_resume_prevMode and not self.is_default_command())
    
    # methods for leaving this command (from a dashboard tool or an
    # internal request).

    # Notes on state-accumulating modes, e.g. Build Crystal, Extrude,
    # and [we hoped at the time] Build Atoms [bruce 040923]:
    #
    # [WARNING: these comments are MOSTLY OBSOLETE now that
    # USE_COMMAND_STACK is true (new command API, which 
    # is the default API as of 2008-09-26) ]
    #
    # Each command which accumulates state, meant to be put into its
    # model (assembly) in the end, decides how much to put in as it
    # goes -- that part needs to be "undone" (removed from the
    # assembly) to support a Cancel event -- versus how much to retain
    # internally -- that part needs to be "done" (put into in the
    # assembly) upon a Done event.  (BTW, as I write this, I think
    # that only BuildAtoms_Command (so far) puts any state into the assembly
    # before it's Done.)
    #
    # Both kinds of state (stored in the command or in the assembly)
    # should be considered when overriding self.haveNontrivialState()
    # -- it should say whether Done and Cancel should have different
    # ultimate effects. (Note "should" rather than "would" --
    # i.e. even if Cancel does not yet work, like in BuildAtoms_Command,
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
    
    def _warnUserAboutAbandonedChanges(self): #bruce 080908 split this out
        """
        Private helper method for command subclasses overriding command_will_exit
        which (when commandSequencer.exit_is_forced is true) need to warn the user
        about changes being abandoned when closing a model, which were not
        noticed by a file modified check due to logic bugs in how that works
        and how those changes are stored. Most commands don't need to call this;
        only commands that store changes in self rather than in assy might
        need to call it.

        It does nothing if self.commandSequencer.warn_about_abandoned_changes 
        is False.
        @see: ExtrudeMode.command_will_exit() where it is called. 
        """
        
        if not self.commandSequencer.warn_about_abandoned_changes:
            return
        
        msg = "%s with changes is being forced to abandon those changes!\n" \
              "Sorry, no choice for now." % (self.get_featurename(),)
        self._warning_for_abandon( msg, bother_user_with_dialog = 1 )
        return

    def warning(self, *args, **kws):
        # find out whether this ever happens. If not, remove it. [bruce 080912]
        print_compact_stack( "fyi: deprecated method basicCommand.warning(*%r, **%r) was called: " % (args, kws))
        self._warning_for_abandon(*args, **kws)

    def _warning_for_abandon(self, str1, bother_user_with_dialog = 0, ensure_visible = 1):
        """
        Show a warning to the user, without interrupting them
        (i.e. not in a dialog) unless bother_user_with_dialog is
        true, or unless ensure_visible is true and there's no other
        way to be sure they'll see the message.  (If neither of
        these options is true, we might merely print the message to
        stdout.)

        Also always print the warning to the console.

        In the future, this might go into a status bar in the
        window, if we can be sure it will remain visible long
        enough.  For now, that won't work, since some status bar
        messages I emit are vanishing almost instantly, and I can't
        yet predict which ones will do that.  Due to that problem
        and since the stdout/stderr output might be hidden from the
        user, ensure_visible implies bother_user_with_dialog for
        now.  (And when we change that, we have to figure out
        whether all the calls that no longer use dialogs are still
        ok.)

        In the future, all these messages will also probably get
        timestamped and recorded in a log file, in addition to
        whereever they're shown now.

        @see: env.history; other methods named warning.
        """
        # bruce 040922 wrote this (in GLPane, named warning)
        # bruce 080912: this was almost certainly only called by
        # self._warnUserAboutAbandonedChanges.
        # so I moved its body here from class GLPane,
        # and renamed it, and added a deprecated compatibility
        # call from the old method name (warning).

        # TODO: cleanup; merge with other 'def warning' methods and with
        # env.history / statusbar methods.
        # Or, perhaps just inline it into its sole real caller.

        from PyQt4.Qt import QMessageBox
        
        use_status_bar = 0 # always 0, for now
        use_dialog = bother_user_with_dialog

        if ensure_visible:
            prefix = "WARNING"
            use_dialog = 1 ###e for now, and during debugging --
            ### status bar would be ok when we figure out how to
            ### guarantee it lasts
        else:
            prefix = "warning"
        str1 = str1[0].upper() + str1[1:] # capitalize the sentence
        msg = "%s: %s" % (prefix, str1,)
        ###e add a timestamp prefix, at least for the printed one

        # always print it so there's a semi-permanent record they can refer to
        
        print msg 

        if use_status_bar: # do this first
            ## [this would work again as of 050107:] self.win.statusBar().message( msg)
            assert 0 # this never happens for now
        if use_dialog:
            # use this only when it's worth interrupting the user to make
            # sure they noticed the message.. see docstring for details
            ##e also linebreak it if it's very long? i might hope that some
            # arg to the messagebox could do this...
            QMessageBox.warning(self.o, prefix, msg) # args are widget, title, content
        return
        
    def StartOver(self):
        # only callable from UI of Extrude & Build Crystal;
        # needs rename [bruce 080806 comment]
        """
        Support Start Over action for a few commands which implement this

        [subclasses should NOT override this]
        """
        #bruce 080827 guess; UNTESTED ###
        self.command_Cancel()
        self.commandSequencer.userEnterCommand(self.commandName)
           
    # ==

    def find_self_or_parent_command_named(self, commandName): #bruce 080801; maybe untested
        """
        Return the first command of self and its parentCommands (if any)
        which has the given commandName, or None if none does
        (often an error, but no error message is printed).
        """
        # note: this could be rewritten to not use self.commandSequencer
        # at all (a nice cleanup, but not urgent or required).
        cseq = self.commandSequencer
        res = cseq.find_innermost_command_named( commandName,
                                                 starting_from = self )
        return res

    def find_parent_command_named(self, commandName): #bruce 080801
        """
        Return the first of self's parentCommands (if any)
        which has the given commandName, or None if none does
        (often an error, but no error message is printed).

        @note: we expect at most one active command to have a given
               commandName (at a given time), but this may not be checked
               or enforced.
        """
        # review: can this be simplified, now that new command api is always used?
        # e.g. it could probably work without referencing self.commandSequencer.
        cseq = self.commandSequencer
        commands = cseq.all_active_commands( starting_from = self )
        for command in commands[1:]: # only look at our parent commands
            if command.commandName == commandName:
                return command
        return None

    # ==

    def _args_and_callback_for_request_command(self): #bruce 080801, might be revised/renamed
        """
        ###doc
        """
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
