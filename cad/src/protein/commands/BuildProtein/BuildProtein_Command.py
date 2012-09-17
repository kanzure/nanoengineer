# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
BuildProtein_Command.py

@author: Urmi
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""
from command_support.EditCommand import EditCommand
from utilities.Log  import greenmsg
from ne1_ui.toolbars.Ui_ProteinFlyout import ProteinFlyout
from protein.commands.BuildProtein.BuildProtein_PropertyManager import BuildProtein_PropertyManager
from protein.commands.BuildProtein.BuildProtein_GraphicsMode    import BuildProtein_GraphicsMode

_superclass = EditCommand
class BuildProtein_Command(EditCommand):
    """
    ModelAndSimulateProtein_EditCommand provides a convenient way to edit or create
    or simulate a Protein object
    """

    # class constants
    GraphicsMode_class = BuildProtein_GraphicsMode

    PM_class = BuildProtein_PropertyManager

    #Flyout Toolbar
    FlyoutToolbar_class = ProteinFlyout

    cmd              =  greenmsg("Build Protein: ")
    prefix           =  'ProteinGroup'   # used for gensym
    cmdname          = "Build Protein"

    commandName       = 'BUILD_PROTEIN'
    featurename       = "Build Protein"
    from utilities.constants import CL_ENVIRONMENT_PROVIDING
    command_level = CL_ENVIRONMENT_PROVIDING
    command_should_resume_prevMode = False
    command_has_its_own_PM = True
    create_name_from_prefix  =  True
    call_makeMenus_for_each_event = True

    flyoutToolbar = None
    _currentActiveTool = 'MODEL_PROTEIN'

    def command_enter_misc_actions(self):
        """
        Overrides superclass method.

        @see: baseCommand.command_enter_misc_actions()  for documentation
        """
        self.w.buildProteinAction.setChecked(True)
        return

    def command_exit_misc_actions(self): #@@@
        """
        Overrides superclass method.

        @see: baseCommand.command_exit_misc_actions()  for documentation
        """
        #self.w.buildProteinAction.setChecked(False)
        return

    def getCurrentActiveTool(self):
        return self._currentActiveTool

    def setCurrentCommandMode(self, commandName):
        """
        Sets the current active command: modeling or simulation
        """
        self._currentActiveTool = commandName
        return

    def enterModelOrSimulateCommand(self, commandName = ''):
        """
        Enter the given tools subcommand (e.g. Model or Simulate Protein command)
        """
        if not commandName:
            return

        commandSequencer = self.win.commandSequencer
        commandSequencer.userEnterCommand( commandName)
        return

    def makeMenus(self):
        """
        Create context menu for this command.
        """
        #Urmi 20080806: will implement later, once the basic system is up and
        #working
        return

    def keep_empty_group(self, group): #@@@
        """
        Returns True if the empty group should not be automatically deleted.
        otherwise returns False. The default implementation always returns
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True.
        @see: Command.keep_empty_group() which is overridden here.
        """

        bool_keep = EditCommand.keep_empty_group(self, group)

        if not bool_keep:
            if group is self.struct:
                bool_keep = True

        return bool_keep


