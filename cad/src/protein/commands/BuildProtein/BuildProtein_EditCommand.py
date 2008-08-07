# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
BuildProtein_EditCommand.py

@author: Urmi
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""
from command_support.EditCommand import EditCommand
from utilities.Log  import greenmsg
from utilities.constants import gensym
from ne1_ui.toolbars.Ui_ProteinFlyout import ProteinFlyout

class BuildProtein_EditCommand(EditCommand):
    """
    BuildProtein_EditCommand provides a convenient way to edit or create
    a Protein object
    """
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

    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for BuildDna_EditCommand
        """
        EditCommand.__init__(self, commandSequencer)
        self.struct = struct


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
        if self.flyoutToolbar is None:
            self.flyoutToolbar = ProteinFlyout(self.win, self.propMgr)
        self.flyoutToolbar.activateFlyoutToolbar()

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

    def create_and_or_show_PM_if_wanted(self, showPropMgr = True):
        """
        Create the property manager object if one doesn't already exist
        and then show the propMgr if wanted by the user.
        @param showPropMgr: If True, show the property manager
        @type showPropMgr: boolean
        """
        EditCommand.create_and_or_show_PM_if_wanted(
            self,
            showPropMgr = showPropMgr)
        
        self.propMgr.updateMessage("Use appropriate command in the command "\
                                   "toolbar to modify a Protein."\
                                   "<br>"\
                                   "If you change the sequence, make sure to "\
                                   "hit Enter key at the end so that the changes "
                                   "can be saved."
                                   "<br>"
                               )

    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this
        editCommand.
        """
        assert not self.propMgr
        propMgr = self.win.createBuildProteinPropMgr_if_needed(self)
        return propMgr
 
