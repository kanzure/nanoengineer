# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from icon_utilities import geticon

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
        subControlAreaActionList.append(self.exitDna)
        separator = QtGui.QAction(self.parentWindow)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 
        subControlAreaActionList.append(self.dnaDuplexGenerator)
        subControlAreaActionList.append(self.dnaOrigamiGenerator)

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
        self.exitDna = QtGui.QWidgetAction(parentWindow)
        self.exitDna.setText("Exit DNA")
        self.exitDna.setIcon(geticon("ui/actions/Toolbars/Smart/Exit"))

        self.dnaDuplexGenerator = QtGui.QWidgetAction(parentWindow)
        self.dnaDuplexGenerator.setText("DNA")
        self.dnaDuplexGenerator.setIcon(geticon("ui/actions/Tools/Build Structures/DNA"))

        self.dnaOrigamiGenerator = QtGui.QWidgetAction(parentWindow)
        self.dnaOrigamiGenerator.setText("Origami")
        self.dnaOrigamiGenerator.setIcon(geticon("ui/actions/Tools/Build Structures/DNA_Origami"))

        parentWindow.connect(self.exitDna, SIGNAL("triggered()"),
                             self.activateExitDna)
        parentWindow.connect(self.dnaDuplexGenerator, SIGNAL("triggered()"),
                             self.activateDnaDuplexGenerator)
        parentWindow.connect(self.dnaOrigamiGenerator, SIGNAL("triggered()"),
                             self.activateDnaOrigamiGenerator)

    def activateExitDna(self):
        self.parentWindow.commandManager.updateCommandManager(
            self.parentWindow.buildDnaAction, _theDnaFlyout, entering=False)
        
    def activateDnaDuplexGenerator(self):
        self.parentWindow.insertDna()

    def activateDnaOrigamiGenerator(self):
        pass

