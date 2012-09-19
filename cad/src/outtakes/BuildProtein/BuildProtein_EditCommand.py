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

_superclass = EditCommand
class BuildProtein_EditCommand(EditCommand):
    """
    BuildProtein_EditCommand provides a convenient way to edit or create
    a Protein object
    """

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
    create_name_from_prefix  =  True
    call_makeMenus_for_each_event = True

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