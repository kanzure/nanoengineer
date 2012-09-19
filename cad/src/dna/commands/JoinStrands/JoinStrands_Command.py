# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs:
Many changes planned in JoinStrands_GraphicsMode .
"""

from dna.commands.JoinStrands.JoinStrands_PropertyManager import JoinStrands_PropertyManager
from dna.command_support.BreakOrJoinStrands_Command import BreakOrJoinStrands_Command
from dna.commands.JoinStrands.JoinStrands_GraphicsMode import JoinStrands_GraphicsMode
import foundation.env as env
from utilities.prefs_constants import joinStrandsCommand_clickToJoinDnaStrands_prefs_key


# == Command part

_superclass = BreakOrJoinStrands_Command
class JoinStrands_Command(BreakOrJoinStrands_Command):
    """
    Command part for joining two strands.
    @see: superclass B{BreakOrJoinStrands_Command}
    """
    # class constants

    commandName = 'JOIN_STRANDS'
    featurename = "Join Strands"

    GraphicsMode_class = JoinStrands_GraphicsMode
    PM_class = JoinStrands_PropertyManager

    def _get_init_gui_flyout_action_string(self):
        return 'joinStrandsAction'

    def command_update_state(self):
        """
        See superclass for documentation.
        Note that this method is called only when self is the currentcommand on
        the command stack.
        @see: BuildAtomsFlyout.resetStateOfActions()
        @see: self.activateAtomsTool()
        """
        _superclass.command_update_state(self)

        #Make sure that the command Name is JOIN_STRANDS. (because subclasses
        #of JoinStrands_Command might be using this method).
        #As of 2008-10-23, if the checkbox 'Click on strand to join'
        #in the join strands PM is checked, NE1 will enter a command that
        #implements different mouse behavior in its graphics mode and will stay
        #there.
        if self.commandName == 'JOIN_STRANDS' and \
           env.prefs[joinStrandsCommand_clickToJoinDnaStrands_prefs_key] \
           and not self.graphicsMode.exit_command_on_leftUp:

            self.commandSequencer.userEnterCommand('CLICK_TO_JOIN_STRANDS')


