# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

TODO: 
- Does the parentWidget for the DnaFlyout always needs to be a propertyManager
  The parentWidget is the propertyManager object of the currentCommand on the 
  commandSequencer. What if the currentCommand doesn't have a PM but it wants 
  its own commandToolbar?  Use the mainWindow as its parentWidget? 
- The implementation may change after Command Manager (Command toolbar) code 
  cleanup. The implementation as of 2007-12-20 is an attempt to define 
  flyouttoolbar object in the 'Command.
"""

import env
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from icon_utilities import geticon
from utilities.Log import greenmsg

_theDnaFlyout = None

#NOTE: global methods setupUi, activateDnaFlyout are not called as of 2007-12-19
#Use methods like DnaFlyout.activateFlyoutToolbar instead. 
#Command toolbar needs to be integrated with the commandSequencer. 
#See DnaDuplexEditController.init_gui for an example. (still experimental)


def setupUi(mainWindow):
    """
    Construct the QWidgetActions for the Dna flyout on the 
    Command Manager toolbar.
    """
    global _theDnaFlyout

    _theDnaFlyout = DnaFlyout(mainWindow)
    
# probably needs a retranslateUi to add tooltips too...

def activateDnaFlyout(mainWindow):
    mainWindow.commandToolbar.updateCommandToolbar(mainWindow.buildDnaAction, 
                                                   _theDnaFlyout)

    
class DnaFlyout:    
    def __init__(self, mainWindow, parentWidget):
        """
        Create necessary flyoot action list and update the flyout toolbar in
        the command toolbar with the actions provided by the object of this
        class.
        
        @param mainWindow: The mainWindow object
        @type  mainWindow: B{MWsemantics} 
        
        @param parentWidget: The parentWidget to which actions defined by this 
                             object belong to. This needs to be revised.
                             
        """
        
        self.parentWidget = parentWidget
        self.win = mainWindow
        self._isActive = False
        self._createActions(self.parentWidget)

    def getFlyoutActionList(self):
        """
        Returns a tuple that contains lists of actions used to create
        the flyout toolbar. 
        Called by CommandToolbar._createFlyoutToolBar().
        @return: params: A tuple that contains 3 lists: 
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
        #'allActionsList' returns all actions in the flyout toolbar 
        #including the subcontrolArea actions. 
        allActionsList = []

        #Action List for  subcontrol Area buttons. 
        subControlAreaActionList = []
        subControlAreaActionList.append(self.exitDnaAction)
        separator = QtGui.QAction(self.parentWidget)
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

    def _createActions(self, parentWidget):
        self.exitDnaAction = QtGui.QWidgetAction(parentWidget)
        self.exitDnaAction.setText("Exit DNA")
        self.exitDnaAction.setIcon(geticon("ui/actions/Toolbars/Smart/Exit"))
        self.exitDnaAction.setCheckable(True)
        
        self.dnaDuplexAction = QtGui.QWidgetAction(parentWidget)
        self.dnaDuplexAction.setText("Duplex")
        self.dnaDuplexAction.setCheckable(True)        
        self.dnaDuplexAction.setIcon(geticon("ui/actions/Tools/Build Structures/Duplex"))

        self.dnaOrigamiAction = QtGui.QWidgetAction(parentWidget)
        self.dnaOrigamiAction.setText("Origami")
        self.dnaOrigamiAction.setIcon(geticon("ui/actions/Tools/Build Structures/DNA_Origami"))

        # Add tooltips
        self.dnaDuplexAction.setToolTip("Duplex")
        self.dnaOrigamiAction.setToolTip("Origami")
    
    def connect_or_disconnet_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        
        @see: self.activateFlyoutToolbar, self.deActivateFlyoutToolbar
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
            
        change_connect(self.exitDnaAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateExitDna)
        
        change_connect(self.dnaDuplexAction, 
                             SIGNAL("triggered(bool)"),
                             self.activateDnaDuplexEditController)
        
        change_connect(self.dnaOrigamiAction, 
                             SIGNAL("triggered()"),
                             self.activateDnaOrigamiEditController)
    
    
    def activateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides. 
        """    
        if self._isActive:
            return
        
        self._isActive = True
        self.win.commandToolbar.updateCommandToolbar(self.win.buildDnaAction,
                                                     self)
        self.exitDnaAction.setChecked(True)
        self.connect_or_disconnet_signals(True)
    
    def deActivateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides.
        """
        if not self._isActive:
            return 
        
        self._isActive = False
        
        if self.dnaDuplexAction.isChecked():
            self.dnaDuplexAction.setChecked(False)
            
        self.connect_or_disconnet_signals(False)    
        self.win.commandToolbar.updateCommandToolbar(self.win.buildDnaAction,
                                                     self,
                                                     entering = False)

    def activateExitDna(self, isChecked):
        """
        Slot for B{Exit DNA} action.
        """     
        #@TODO: This needs to be revised. 
        
        if hasattr(self.parentWidget, 'ok_btn_clicked'):
            if not isChecked:
                self.parentWidget.ok_btn_clicked()
        
    def activateDnaDuplexEditController(self, isChecked):
        """
        Slot for B{Duplex} action.
        """
        self.win.insertDna(isChecked)

    def activateDnaOrigamiEditController(self):
        """
        Slot for B{Origami} action.
        """
        msg1 = greenmsg("DNA Origami: ")
        msg2 = " Not implemented yet"
        final_msg = msg1 + msg2
        env.history.message(final_msg)        