# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-07-24 : Created

TODO:
"""
import foundation.changes as changes
from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from commands.QuteMol.QuteMolPropertyManager import QuteMolPropertyManager

_superclass = SelectChunks_Command
class QuteMol_Command(SelectChunks_Command):

    commandName = 'QUTEMOL'
    default_mode_status_text = ""
    featurename = "QuteMol"
    
    GraphicsMode_class = SelectChunks_GraphicsMode

    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_gui = True

    flyoutToolbar = None

    def init_gui(self):
        """
        Initialize GUI for this mode 
        """
        if self.propMgr is None:
            self.propMgr = QuteMolPropertyManager(self)
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


            