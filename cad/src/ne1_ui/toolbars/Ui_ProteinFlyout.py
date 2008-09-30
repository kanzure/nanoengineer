# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Urmi
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version $Id$

piotr 080713: Added editRotamers action.

"""

import foundation.env as env
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from utilities.icon_utilities import geticon
from utilities.Log import greenmsg
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction

_theProteinFlyout = None

def setupUi(mainWindow):
    """
    Construct the QWidgetActions for the Dna flyout on the 
    Command Manager toolbar.
    """
    global _theDnaFlyout

    _theProteinFlyout = ProteinFlyout(mainWindow)

# probably needs a retranslateUi to add tooltips too...

def activateProteinFlyout(mainWindow):
    mainWindow.commandToolbar.updateCommandToolbar(mainWindow.insertPeptideAction, 
                                                   _theProteinFlyout)

class ProteinFlyout:    
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


        #Action List for  subcontrol Area buttons. 
        subControlAreaActionList = []
        subControlAreaActionList.append(self.exitProteinAction)
        separator = QtGui.QAction(self.parentWidget)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 
        subControlAreaActionList.append(self.buildPeptideAction)        
        subControlAreaActionList.append(self.editRotamersAction)        
        subControlAreaActionList.append(self.editResiduesAction)        
        subControlAreaActionList.append(self.compareProteinsAction)        
        subControlAreaActionList.append(self.displayProteinStyleAction)
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
        self.exitProteinAction = NE1_QWidgetAction(parentWidget,
                                                     win = self.win)
        self.exitProteinAction.setText("Exit Protein")
        self.exitProteinAction.setIcon(
            geticon("ui/actions/Toolbars/Smart/Exit.png"))
        self.exitProteinAction.setCheckable(True)

        self.buildPeptideAction = NE1_QWidgetAction(parentWidget,
                                                      win = self.win)
        self.buildPeptideAction.setText("Peptide")
        self.buildPeptideAction.setCheckable(True)  
        self.buildPeptideAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/Peptide.png"))

        self.editRotamersAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.editRotamersAction.setText("Rotamers")
        self.editRotamersAction.setCheckable(True)  
        self.editRotamersAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/Rotamers.png"))
        
        self.editResiduesAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.editResiduesAction.setText("Residues")
        self.editResiduesAction.setCheckable(True)  
        self.editResiduesAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/Residues.png"))
        
        self.compareProteinsAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.compareProteinsAction.setText("Compare")
        self.compareProteinsAction.setCheckable(True)  
        self.compareProteinsAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/Compare.png"))
        
        self.displayProteinStyleAction = NE1_QWidgetAction(parentWidget, 
                                                           win = self.win)

        self.displayProteinStyleAction.setText("Edit Style")
        self.displayProteinStyleAction.setCheckable(True)        
        self.displayProteinStyleAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/EditProteinDisplayStyle.png"))
        
        self.subControlActionGroup = QtGui.QActionGroup(self.parentWidget)
        self.subControlActionGroup.setExclusive(False)   
        self.subControlActionGroup.addAction(self.buildPeptideAction)
        self.subControlActionGroup.addAction(self.displayProteinStyleAction)
        

    def _addWhatsThisText(self):
        """
        Add 'What's This' help text for all actions on toolbar. 
        """
        #change this later
        from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForProteinCommandToolbar
        whatsThisTextForProteinCommandToolbar(self)
        return

    def _addToolTipText(self):
        """
        Add 'Tool tip' help text for all actions on toolbar. 
        """
        #add something here later
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

        change_connect(self.exitProteinAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateExitProtein)

        change_connect(self.buildPeptideAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateBuildPeptide_EditCommand)

        change_connect(self.editRotamersAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateEditRotamers_EditCommand)

        change_connect(self.editResiduesAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateEditResidues_EditCommand)

        change_connect(self.compareProteinsAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateCompareProteins_EditCommand)

        change_connect(self.displayProteinStyleAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateProteinDisplayStyle_Command)

    def activateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides. 
        """                   
        if self._isActive:
            return
        
        self._isActive = True

        self.win.commandToolbar.cmdButtonGroup.button(0).setChecked(True)
        #Now update the command toolbar (flyout area)
        self.win.commandToolbar.updateCommandToolbar(self.win.insertPeptideAction,
                                                     self)
        #self.win.commandToolbar._setControlButtonMenu_in_flyoutToolbar(
                    #self.cmdButtonGroup.checkedId())
        self.exitProteinAction.setChecked(True)
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
        self.win.commandToolbar.updateCommandToolbar(self.win.insertPeptideAction,
                                                     self,
                                                     entering = False)

    def resetStateOfActions(self):
        """
        Resets the state of actions in the flyout toolbar.
        Uncheck most of the actions. Basically it 
        unchecks all the actions EXCEPT the ExitDnaAction
        @see: self.deActivateFlyoutToolbar()
        @see: self.activateBreakStrands_Command() 
        @see: baseCommand.command_update_flyout()
        """

        #Uncheck all the actions in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action.isChecked():
                action.setChecked(False)

    def activateExitProtein(self, isChecked):
        """
        Slot for B{Exit DNA} action.
        """     
        #@TODO: This needs to be revised. 

        if hasattr(self.parentWidget, 'ok_btn_clicked'):
            if not isChecked:
                self.parentWidget.ok_btn_clicked()

    def activateBuildPeptide_EditCommand(self, isChecked):
        """
        Slot for B{Duplex} action.
        """

        self.win.insertPeptide(isChecked)

        #Uncheck all the actions except the dna duplex action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.buildPeptideAction and action.isChecked():
                action.setChecked(False)

    def activateEditRotamers_EditCommand(self, isChecked):
        """
        Slot for B{EditRotamers} action.
        """

        self.win.enterEditRotamersCommand(isChecked)

        for action in self.subControlActionGroup.actions():
            if action is not self.editRotamersAction and action.isChecked():
                action.setChecked(False)

    def activateEditResidues_EditCommand(self, isChecked):
        """
        Slot for B{EditResidues} action.
        """

        self.win.enterEditResiduesCommand(isChecked)

        for action in self.subControlActionGroup.actions():
            if action is not self.editResiduesAction and action.isChecked():
                action.setChecked(False)

    def activateCompareProteins_EditCommand(self, isChecked):
        """
        Slot for B{CompareProteins} action.
        """

        self.win.enterCompareProteinsCommand(isChecked)

        for action in self.subControlActionGroup.actions():
            if action is not self.compareProteinsAction and action.isChecked():
                action.setChecked(False)

    def activateProteinDisplayStyle_Command(self, isChecked):
        """
        Call the method that enters DisplayStyle_Command. 
        (After entering the command) Also make sure that 
        all the other actions on the DnaFlyout toolbar are unchecked AND 
        the DisplayStyle Action is checked. 
        """

        self.win.enterProteinDisplayStyleCommand(isChecked)

        #Uncheck all the actions except the (DNA) display style action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.displayProteinStyleAction and action.isChecked():
                action.setChecked(False)
