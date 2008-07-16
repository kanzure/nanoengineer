# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

TODO: (list copied and kept from Ui_DnaFlyout.py --Mark)
- Does the parentWidget for the NanotubeFlyout always needs to be a propertyManager
  The parentWidget is the propertyManager object of the currentCommand on the 
  commandSequencer. What if the currentCommand doesn't have a PM but it wants 
  its own commandToolbar?  Use the mainWindow as its parentWidget? 
- The implementation may change after Command Manager (Command toolbar) code 
  cleanup. The implementation as of 2007-12-20 is an attempt to define 
  flyouttoolbar object in the 'Command.
  
History:
- Mark 2008-03-8: This file created from a copy of Ui_DnaFlyout.py and edited.
"""

import foundation.env as env
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from utilities.icon_utilities import geticon
from utilities.Log import greenmsg
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction

_theNanotubeFlyout = None

#NOTE: global methods setupUi, activateNanotubeFlyout are not called as of 2007-12-19
#Use methods like NanotubeFlyout.activateFlyoutToolbar instead. 
#Command toolbar needs to be integrated with the commandSequencer. 
#See InsertNanotubeLine_EditCommand.init_gui for an example. (still experimental)

def setupUi(mainWindow):
    """
    Construct the QWidgetActions for the Cnt flyout on the 
    Command Manager toolbar.
    """
    global _theNanotubeFlyout

    _theNanotubeFlyout = NanotubeFlyout(mainWindow)
    
# probably needs a retranslateUi to add tooltips too...

def activateNanotubeFlyout(mainWindow):
    mainWindow.commandToolbar.updateCommandToolbar(mainWindow.buildNanotubeAction, 
                                                   _theNanotubeFlyout)

class NanotubeFlyout:    
    def __init__(self, mainWindow, parentWidget):
        """
        Create necessary flyout action list and update the flyout toolbar in
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
        self._addWhatsThisText()
        self._addToolTipText()
    
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
        
        self.subControlActionGroup = QtGui.QActionGroup(self.parentWidget)
        self.subControlActionGroup.setExclusive(False)   
        self.subControlActionGroup.addAction(self.insertNanotubeAction)

        #Action List for  subcontrol Area buttons. 
        subControlAreaActionList = []
        subControlAreaActionList.append(self.exitNanotubeAction)
        separator = QtGui.QAction(self.parentWidget)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 
        subControlAreaActionList.append(self.insertNanotubeAction)        

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
        self.exitNanotubeAction = NE1_QWidgetAction(parentWidget, 
                                                      win = self.win)
        self.exitNanotubeAction.setText("Exit NT")
        self.exitNanotubeAction.setIcon(
            geticon("ui/actions/Toolbars/Smart/Exit.png"))
        self.exitNanotubeAction.setCheckable(True)
        
        self.insertNanotubeAction = NE1_QWidgetAction(parentWidget,
                                                        win = self.win)
        self.insertNanotubeAction.setText("Insert NT")
        self.insertNanotubeAction.setCheckable(True)        
        self.insertNanotubeAction.setIcon(
            geticon("ui/actions/Tools/Build Structures/InsertNanotube.png"))

    def _addWhatsThisText(self):
        """
        Add 'What's This' help text for all actions on toolbar. 
        """
        from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForNanotubeCommandToolbar
        whatsThisTextForNanotubeCommandToolbar(self)
        return
    
    def _addToolTipText(self):
        """
        Add 'Tool tip' help text for all actions on toolbar. 
        """
        from ne1_ui.ToolTipText_for_CommandToolbars import toolTipTextForNanotubeCommandToolbar
        toolTipTextForNanotubeCommandToolbar(self)
        return
    
    def connect_or_disconnect_signals(self, isConnect):
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
            
        change_connect(self.exitNanotubeAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateExitCnt)
        
        change_connect(self.insertNanotubeAction, 
                             SIGNAL("triggered(bool)"),
                             self.activateInsertNanotubeLine_EditCommand)
    
    def activateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides. 
        """    
               
        if self._isActive:
            return
        
        self._isActive = True
        
        #Temporary workaround for bug 2600 
        #until the Command Toolbar code is revised
        #When NanotubeFlyout toolbar is activated, it should switch to (check) the 
        #'Build Button' in the control area. So that the NanotubeFlyout 
        #actions are visible in the flyout area of the command toolbar. 
        #-- Ninad 2008-01-21. 
        self.win.commandToolbar.cmdButtonGroup.button(0).setChecked(True)
        #Now update the command toolbar (flyout area)
        self.win.commandToolbar.updateCommandToolbar(self.win.buildNanotubeAction,
                                                     self)
        #self.win.commandToolbar._setControlButtonMenu_in_flyoutToolbar(
                    #self.cmdButtonGroup.checkedId())
        self.exitNanotubeAction.setChecked(True)
        self.connect_or_disconnect_signals(True)
    
    def deActivateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides.
        """
        if not self._isActive:
            return 
        
        self._isActive = False
        
        self.resetStateOfActions()
            
        self.connect_or_disconnect_signals(False)    
        self.win.commandToolbar.updateCommandToolbar(self.win.buildNanotubeAction,
                                                     self,
                                                     entering = False)
    
    def resetStateOfActions(self):
        """
        Resets the state of actions in the flyout toolbar.
        Uncheck most of the actions. Basically it 
        unchecks all the actions EXCEPT the ExitCntAction
        @see: self.deActivateFlyoutToolbar()
        @see: InsertNanotube_EditCommand.resume_gui()
        """
        
        #Uncheck all the actions in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action.isChecked():
                action.setChecked(False)
        
        
    def activateExitCnt(self, isChecked):
        """
        Slot for B{Exit DNA} action.
        """     
        #@TODO: This needs to be revised. 
        
        if hasattr(self.parentWidget, 'ok_btn_clicked'):
            if not isChecked:
                self.parentWidget.ok_btn_clicked()
        
    def activateInsertNanotubeLine_EditCommand(self, isChecked):
        """
        Slot for (Insert) B{Nanotube} action.
        """
            
        self.win.insertNanotube(isChecked)
        
        #IMPORTANT: 
        #For a QAction, the method 
        #setChecked does NOT emmit the 'triggered' SIGNAL. So 
        #we can call self.capCntAction.setChecked without invoking its 
        #slot method!
        #Otherwise we would have needed to block the signal when action is 
        #emitted ..example we would have called something like :
        #'if self._block_insertNanotubeAction_event: return' at the beginning of
        #this method. Why we didn't use QAction group -- We need these actions
        #to be
        # a) exclusive as well as
        #(b) 'toggle-able' (e.g. if you click on a checked action , it should 
        #uncheck)
        #QActionGroup achieves (a) but can't do (b) 
        
        #Uncheck all the actions except the dna duplex action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.insertNanotubeAction and action.isChecked():
                action.setChecked(False)