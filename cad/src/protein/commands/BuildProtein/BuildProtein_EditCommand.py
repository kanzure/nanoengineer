# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
BuildProtein_EditCommand.py

@author: Urmi
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""
from command_support.EditCommand import EditCommand
from utilities.Log  import greenmsg
from ne1_ui.toolbars.Ui_ProteinFlyout import ProteinFlyout

from protein.commands.BuildProtein.BuildProtein_PropertyManager import BuildProtein_PropertyManager
from utilities.GlobalPreferences import USE_COMMAND_STACK

_superclass = EditCommand
class BuildProtein_EditCommand(EditCommand):
    """
    BuildProtein_EditCommand provides a convenient way to edit or create
    a Protein object
    """
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = None #fully ported
    
    #Property Manager
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
    command_can_be_suspended = True
    create_name_from_prefix  =  True
    call_makeMenus_for_each_event = True
        
    
    if not USE_COMMAND_STACK:    
        def init_gui(self):
            """
            Do changes to the GUI while entering this command. This includes opening
            the property manager, updating the command toolbar , connecting widget
            slots (if any) etc. Note: The slot connection in property manager and
            command toolbar is handled in those classes.
    
            Called once each time the command is entered; should be called only
            by code in modes.py
    
            @see: L{self.restore_gui}
            """
            EditCommand.init_gui(self)
            self.command_enter_flyout()
            
        def resume_gui(self):
            """
            Called when this command, that was suspended earlier, is being resumed.
            The temporary command (which was entered by suspending this command)
            might have made some changes to the model which need to be reflected
            while resuming command.
    
            Example: A user enters BreakStrands_Command by suspending
            BuildDna_EditCommand, then breaks a few strands, thereby creating new
            strand chunks. Now when the user returns to the BuildDna_EditCommand,
            the command's property manager needs to update the list of strands
            because of the changes done while in BreakStrands_Command.
            @see: Command.resume_gui
            @see: Command._enterMode where this method is called.
            """
            
            if self.flyoutToolbar:
                self.flyoutToolbar.resetStateOfActions()
    
    
        def restore_gui(self):
            """
            Do changes to the GUI while exiting this command. This includes closing
            this mode's property manager, updating the command toolbar ,
            Note: The slot connection/disconnection in property manager and
            command toolbar is handled in those classes.
            @see: L{self.init_gui}
            """
            EditCommand.restore_gui(self)
            
            if self.flyoutToolbar:
                self.flyoutToolbar.deActivateFlyoutToolbar()
                
        def command_enter_flyout(self):
            if self.flyoutToolbar is None:
                self.flyoutToolbar = self._createFlyoutToolBarObject()
            self.flyoutToolbar.activateFlyoutToolbar()
    
        def _createFlyoutToolBarObject(self):
            """
            Create a flyout toolbar to be shown when this command is active. 
            Overridden in subclasses. 
            @see: PasteFromClipboard_Command._createFlyouttoolBar()
            @see: self.command_enter_flyout()
            """
            #from ne1_ui.toolbars.Ui_ProteinFlyout_v2 import ProteinFlyout_v2
            flyoutToolbar = ProteinFlyout(self.win, self.propMgr) 
            return flyoutToolbar

    def runCommand(self):
        """
        Overrides EditCommand.runCommand
        """
        self.struct = None
        self.existingStructForEditing = False
        

    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted.
        otherwise returns False. The default implementation always returns
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True.
        (and as of 2008-03-06, it is proposed that dna_updater calls this method
        when needed.
        @see: Command.keep_empty_group() which is overridden here.
        """

        bool_keep = EditCommand.keep_empty_group(self, group)

        if not bool_keep:
            if group is self.struct:
                bool_keep = True

        return bool_keep