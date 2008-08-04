# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$
History:
Ninad 2008-08-04: Created during the  command stack refactoring project

TODO: 2008-08-04
- See the superclass
"""

from ne1_ui.toolbars.Ui_AbstractFlyout import Ui_AbstractFlyout

class PartLibraryFlyout(Ui_AbstractFlyout):    
    """
    Define Flyout toolbar for the Part library command (Insert > Part Library)
    """
    def _action_in_controlArea_to_show_this_flyout(self):
        """
        Required action in the 'Control Area' as a reference for this 
        flyout toolbar. See superclass method for documentation and todo note.
        """
        #Partlibrary is available as a sub item of the Insert menu in the 
        #control area
        return self.win.partLibAction
    
    def _getExitActionText(self):
        """
        Overrides superclass method. 
        @see: self._createActions()
        """
        return "Exit Partlib"
        
    def getFlyoutActionList(self):
        """ 
        Returns a tuple that contains mode spcific actionlists in the 
        added in the flyout toolbar of the mode. 

        @return: A tuple that contains 3 lists: subControlAreaActionList, 
               commandActionLists and allActionsList
        @rtype: tuple
        @see: L{CommandToolbar._createFlyoutToolBar} which calls this. 
        """

        subControlAreaActionList = []
        commandActionLists   = []
        allActionsList  = []

        subControlAreaActionList.append(self.exitModeAction)   

        lst = []
        commandActionLists.append(lst)      
        allActionsList.append(self.exitModeAction)

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params