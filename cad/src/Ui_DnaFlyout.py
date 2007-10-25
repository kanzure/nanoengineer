# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

import env
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from icon_utilities import geticon
from utilities.Log import greenmsg

_theDnaFlyout = None

def setupUi(mainWindow):
    """
    Construct the QWidgetActions for the Dna flyout on the 
    Command Manager toolbar.
    """
    global _theDnaFlyout

    _theDnaFlyout = DnaFlyout(mainWindow)
    
# probably needs a retranslateUi to add tooltips too...

def activateDnaFlyout(mainWindow):
    mainWindow.commandManager.updateCommandManager(mainWindow.buildDnaAction, _theDnaFlyout)

    
class DnaFlyout(object):
    def __init__(self, parentWindow):
        self.parentWindow = parentWindow
        self._createActions(parentWindow)

    def getFlyoutActionList(self):
        """
        Returns a tuple that contains lists of actions used to create
        the flyout toolbar. 
        Called by CommandManager._createFlyoutToolBar().
        @return: params: A tuple that contains 3 lists: 
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
        #'allActionsList' returns all actions in the flyout toolbar 
        #including the subcontrolArea actions. 
        allActionsList = []

        #Action List for  subcontrol Area buttons. 
        subControlAreaActionList = []
        subControlAreaActionList.append(self.exitDnaAction)
        separator = QtGui.QAction(self.parentWindow)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 
        subControlAreaActionList.append(self.dnaDuplexAction)
        subControlAreaActionList.append(self.dnaOrigamiAction)

        allActionsList.extend(subControlAreaActionList)

        commandActionLists = [] 
        #Append empty 'lists' in 'commandActionLists equal to the 
        #number of actions in subControlArea 
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)
                            
        params = (subControlAreaActionList, commandActionLists, allActionsList)
        
        return params

    def _createActions(self, parentWindow):
        self.exitDnaAction = QtGui.QWidgetAction(parentWindow)
        self.exitDnaAction.setText("Exit DNA")
        self.exitDnaAction.setIcon(geticon("ui/actions/Toolbars/Smart/Exit"))
        self.exitDnaAction.setCheckable(True)
        self.exitDnaAction.setChecked(True)

        self.dnaDuplexAction = QtGui.QWidgetAction(parentWindow)
        self.dnaDuplexAction.setText("Duplex")
        self.dnaDuplexAction.setIcon(geticon("ui/actions/Tools/Build Structures/Duplex"))

        self.dnaOrigamiAction = QtGui.QWidgetAction(parentWindow)
        self.dnaOrigamiAction.setText("Origami")
        self.dnaOrigamiAction.setIcon(geticon("ui/actions/Tools/Build Structures/DNA_Origami"))

        parentWindow.connect(self.exitDnaAction, SIGNAL("triggered()"),
                             self.activateExitDna)
        parentWindow.connect(self.dnaDuplexAction, SIGNAL("triggered()"),
                             self.activateDnaDuplexEditController)
        parentWindow.connect(self.dnaOrigamiAction, SIGNAL("triggered()"),
                             self.activateDnaOrigamiEditController)
        
        # Add tooltips
        self.dnaDuplexAction.setToolTip("Duplex")
        self.dnaOrigamiAction.setToolTip("Origami")

    def activateExitDna(self):
        """
        Slot for B{Exit DNA} action.
        """
        self.parentWindow.commandManager.updateCommandManager(
            self.parentWindow.buildDnaAction, _theDnaFlyout, entering=False)
        
    def activateDnaDuplexEditController(self):
        """
        Slot for B{Duplex} action.
        """
        self.parentWindow.insertDna()

    def activateDnaOrigamiEditController(self):
        """
        Slot for B{Origami} action.
        """
        msg1 = greenmsg("DNA Origami: ")
        msg2 = " Not implemented yet"
        final_msg = msg1 + msg2
        env.history.message(final_msg)