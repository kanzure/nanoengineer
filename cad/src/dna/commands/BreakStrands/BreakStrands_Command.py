# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
@author:    Ninad
@version:   $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: [ as of 2008-01-04]
- To be revised heavily . Still a stub, needs documentation.
"""

import foundation.changes as changes

from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from dna.commands.BreakStrands.BreakStrands_PropertyManager import BreakStrands_PropertyManager
from dna.commands.BreakStrands.BreakStrands_GraphicsMode import BreakStrands_GraphicsMode

# == Command part

_superclass = BuildAtoms_Command
class BreakStrands_Command(BuildAtoms_Command):
    """

    """
    # class constants

    commandName = 'BREAK_STRANDS'
    featurename = "Break Strands"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_DNA'

    hover_highlighting_enabled = True
    GraphicsMode_class = BreakStrands_GraphicsMode


    command_can_be_suspended = False
    command_should_resume_prevMode = True
    command_has_its_own_gui = True

    flyoutToolbar = None

    def init_gui(self):
        """
        Initialize GUI for this mode
        """
        self._init_gui_flyout_action( 'breakStrandAction' )
        
        if self.propMgr is None:
            self.propMgr = BreakStrands_PropertyManager(self)
            #@bug BUG: following is a workaround for bug 2494.
            #This bug is mitigated as propMgr object no longer gets recreated
            #for modes -- niand 2007-08-29
            changes.keep_forever(self.propMgr)

        self.propMgr.show()


    def restore_gui(self):
        """
        Restore the GUI
        """

        if self.propMgr is not None:
            self.propMgr.close()


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

        bool_keep = _superclass.keep_empty_group(self, group)

        if not bool_keep:
            #Lets just not delete *ANY* DnaGroup while in BreakStrands_Command
            #Although BreakStrands command can only be accessed through
            #BuildDna_EditCommand, it could happen (due to a bug) that the
            #previous command is not BuildDna_Editcommand. So bool_keep
            #in that case will return False propmting dna updater to even delete
            #the empty DnaGroup (if it becomes empty for some reasons) of the
            #BuildDna command. To avoid this ,this method will instruct
            # to keep all instances of DnaGroup even when they might be empty.
            if isinstance(group, self.assy.DnaGroup):
                bool_keep = True
            #Commented out code that shows what I was planning to implement
            #earlier.
            ##previousCommand = self.commandSequencer.prevMode # keep_empty_group: .struct
            ##if previousCommand.commandName == 'BUILD_DNA':
                ##if group is previousCommand.struct:
                    ##bool_keep = True

        return bool_keep
