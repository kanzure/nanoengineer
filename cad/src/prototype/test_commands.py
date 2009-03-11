# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
test_commands.py -- try out using mode classes as command classes for a command stack;
 find out the minimal needs for a command with PM (and improve them);
 prototype a command stack

@author: Bruce
@version: $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.


How to run these test commands:

- set the debug_pref "test_commands enabled (next session)"

- quit and rerun NE1

- the debug menu's submenu "other" should contain new menu commands
defined in this file, such as ExampleCommand1. (Note: not all of them
are contiguous in that submenu, since the entire submenu is sorted
alphabetically.)


Cosmetic bugs:

- closing groupboxes makes them flash


TODO:

Split into several files in a subdirectory.

When cleaning up PropMgrBaseClass etc, note some other things Mark wants to work on soon:

- add message boxes to users of PropertyManagerMixin, in a way easily moved over to PropMgrBaseClass when they use that

- port more modes over to PropMgrBaseClass, e.g. extrudeMode

- split some PMs/modes into more than one smaller PM (especially MMKit). 
  Note: See PM_ElementSelector.py. Mark 2007-08-07.

Fix problems with _Example_TemporaryCommand_useParentPM (commented where it's used)
"""

from prototype.test_command_PMs import ExampleCommand1_PM
##from prototype.test_command_PMs import ExampleCommand2_PM

from PM.PM_WidgetsDemoPropertyManager import PM_WidgetsDemoPropertyManager

from command_support.GraphicsMode import GraphicsMode
from command_support.Command import Command


# ==

class _minimalGraphicsMode(GraphicsMode):
    # [not sure whether this comment is obs, as of 080910:]
    # this is enough to draw the axes, compass, etc, and the model, but not with highlighting (model or expr):
    # What we need is some of what's in SelectAtoms_Command and maybe some of what's in testmode.
    # It's more efficient to refactor those to get a new generally useful GraphicsMode,
    # than to build them up separately here. HOWEVER, for the purpose of testing Command/GraphicsMode split,
    # this one might be enough, if we split it. So do that below.
    def Draw_model(self):
        super(_minimalGraphicsMode, self).Draw_model()
        self.glpane.part.draw(self.glpane) # draw the current Part
    pass

class _minimalCommand(Command):
    GraphicsMode_class = _minimalGraphicsMode
    pass

## this worked a long time -- _superclass = _minimalCommand
# but time to try SelectAtoms again now that it's split [bruce 080123]
from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_Command
_superclass = SelectAtoms_Command

# ==

class ExampleCommand(_superclass):
    """
    Abstract superclass for the example commands in this file.
    Specific command subclasses need to define the following class constants:
    commandName, and PM_class.
    Some of them also need to override mode methods, such as Draw_model and/or Draw_other.
    """
    test_commands_start_as_temporary_command = False
    PM_class = None # if not overridden, means we need no PM (BUG: we'll still get a PM tab)
    featurename = "Prototype: Undocumented Example Command"
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC
    __abstract_command_class = True

# ==

##class _Example_TemporaryCommand_useParentPM(ExampleCommand):
##    # BUGS:
##    # - doesn't call parentGraphicsMode.Draw; maybe should use something like
##    #   Overdrawing_GraphicsMode_preMixin from TemporaryCommand.py ####
##    #   [see also Delegating_GraphicsMode]
##    #
##    # Note: this works if you have your own PM; perhaps untested when you don't.
##    # Warning: currently only one level of temporary commands is permitted;
##    # if you enter one of these commands and then enter another TemporaryCommand (e.g. Zoom Tool)
##    # it exits the first temporary commmand you were in.
##    command_should_resume_prevMode = True #bruce 071011, to be revised (replaces need for customized Done method)
##    test_commands_start_as_temporary_command = True # enter in different way
##        ### maybe todo: set up a similar thing in Command API?
##        # it would replace all calls of userEnterCommand.
##        # [later, 080730: that idea might be obsolete or invalid in its details.
##        #  revisit after ongoing command stack refactoring.]
##    pass

_Example_TemporaryCommand_useParentPM = ExampleCommand

# ==

class ExampleCommand1(ExampleCommand):
    """
    Example command, which uses behavior similar to SelectAtoms_Command
    [but, _superclass is now revised...]. 
    [Which inherits class Command.]
    """
    commandName = 'ExampleCommand1-commandName' # internal #e fix init code in basicMode to get it from classname?
    featurename = "Prototype: Example Command 1"
    # note: init code in basicMode won't even run now, since superclass defs it i think --
    # actually, not sure abt that, probably it doesn't
    PM_class = ExampleCommand1_PM
    
    # note: ok_btn_clicked, etc, must be defined in our PM class (elsewhere),
    # not in this class.

    pass

##class ExampleCommand2( _Example_TemporaryCommand_useParentPM): # WRONG: this has own PM, so it'll mess up parent one.
##    """
##    Like ExampleCommand1, but use GBC (GeneratorBaseClass).
##    (This difference shows up only in our PM class.)
##    """
##    commandName = 'ExampleCommand2-commandName'
##    featurename = "Prototype: Example Command 2"
##    PM_class = ExampleCommand2_PM
##    pass

# ==

class PM_WidgetDemo(ExampleCommand):
    """
    Used to demo all the PM widgets.
    
    @see: PM_WidgetsDemoPropertyManager in PM_WidgetsDemoPropertyManager.py.
    """
    # Note: this is no longer added to the UI. I don't know why it was removed.
    # I know that for awhile it was broken due to a bug. [bruce 071030 comment]
    commandName = 'PM_WidgetDemo-commandName'
    featurename = "Test Command: PM_Widgets Demo"
    PM_class = PM_WidgetsDemoPropertyManager
    pass

# ==

# for init code which makes these available from the UI, see test_commands_init.py

# end
