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

import foundation.env as env
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from utilities.icon_utilities import geticon
from utilities.Log import greenmsg
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction
from ne1_ui.toolbars.Ui_AbstractFlyout import Ui_AbstractFlyout

_superclass = Ui_AbstractFlyout
class DnaFlyout(Ui_AbstractFlyout):  
    
    def _action_in_controlArea_to_show_this_flyout(self):
        """
        Required action in the 'Control Area' as a reference for this 
        flyout toolbar. See superclass method for documentation and todo note.
        """
        return self.win.buildDnaAction
    
    def _getExitActionText(self):
        """
        Overrides superclass method. 
        @see: self._createActions()
        """
        return "Exit DNA"
    
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
        subControlAreaActionList.append(self.exitModeAction)
        separator = QtGui.QAction(self.parentWidget)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 
        subControlAreaActionList.append(self.dnaDuplexAction)        
        subControlAreaActionList.append(self.breakStrandAction)
        subControlAreaActionList.append(self.joinStrandsAction)
        subControlAreaActionList.append(self.makeCrossoversAction)
        subControlAreaActionList.append(self.convertDnaAction)
        subControlAreaActionList.append(self.orderDnaAction)
        subControlAreaActionList.append(self.editDnaDisplayStyleAction)

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
        """
        Overrides superclass method
        """
        
        _superclass._createActions(self, parentWidget)
        
        self.dnaDuplexAction = NE1_QWidgetAction(parentWidget,
                                                 win = self.win)
        self.dnaDuplexAction.setText("Insert DNA")
        self.dnaDuplexAction.setCheckable(True)        
        self.dnaDuplexAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildDna/InsertDna.png"))
        
        self.breakStrandAction = NE1_QWidgetAction(parentWidget,
                                                   win = self.win)
        self.breakStrandAction.setText("Break Strand")
        self.breakStrandAction.setCheckable(True)        
        self.breakStrandAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildDna/BreakStrand.png"))
        
        self.joinStrandsAction = NE1_QWidgetAction(parentWidget,
                                                   win = self.win)
        self.joinStrandsAction.setText("Join Strands")
        self.joinStrandsAction.setCheckable(True)        
        self.joinStrandsAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildDna/JoinStrands.png"))
        
        self.makeCrossoversAction = NE1_QWidgetAction(parentWidget,
                                                      win = self.win)
        self.makeCrossoversAction.setText("Crossovers")
        self.makeCrossoversAction.setCheckable(True)        
        self.makeCrossoversAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildDna/MakeCrossovers.png"))

        self.dnaOrigamiAction = NE1_QWidgetAction(parentWidget,
                                                  win = self.win)
        self.dnaOrigamiAction.setText("Origami")
        self.dnaOrigamiAction.setIcon(
            geticon("ui/actions/Tools/Build Structures/DNA_Origami.png"))
        
        self.convertDnaAction = NE1_QWidgetAction(parentWidget,
                                                      win = self.win)
        self.convertDnaAction.setText("Convert")
        self.convertDnaAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildDna/ConvertDna.png"))
        
        self.orderDnaAction = NE1_QWidgetAction(parentWidget,
                                                win = self.win)
        self.orderDnaAction.setText("Order DNA")
        self.orderDnaAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildDna/OrderDna.png"))
        
        self.editDnaDisplayStyleAction = NE1_QWidgetAction(parentWidget,
                                                           win = self.win)
        self.editDnaDisplayStyleAction.setText("Edit Style")
        self.editDnaDisplayStyleAction.setCheckable(True)        
        self.editDnaDisplayStyleAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildDna/EditDnaDisplayStyle.png"))
        
        self.subControlActionGroup = QtGui.QActionGroup(self.parentWidget)
        self.subControlActionGroup.setExclusive(False)   
        self.subControlActionGroup.addAction(self.dnaDuplexAction)
        self.subControlActionGroup.addAction(self.breakStrandAction) 
        self.subControlActionGroup.addAction(self.joinStrandsAction)
        self.subControlActionGroup.addAction(self.makeCrossoversAction)
        self.subControlActionGroup.addAction(self.editDnaDisplayStyleAction)
        
    def _addWhatsThisText(self):
        """
        Add 'What's This' help text for all actions on toolbar. 
        """
        from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForDnaCommandToolbar
        whatsThisTextForDnaCommandToolbar(self)
        return
    
    def _addToolTipText(self):
        """
        Add 'Tool tip' help text for all actions on toolbar. 
        """
        from ne1_ui.ToolTipText_for_CommandToolbars import toolTipTextForDnaCommandToolbar
        toolTipTextForDnaCommandToolbar(self)
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
            
        _superclass.connect_or_disconnect_signals(self, 
                                                  isConnect)
        
        change_connect(self.dnaDuplexAction, 
                             SIGNAL("triggered(bool)"),
                             self.activateDnaDuplex_EditCommand)
        
        change_connect(self.breakStrandAction, 
                             SIGNAL("triggered(bool)"),
                             self.activateBreakStrands_Command)
        
        change_connect(self.joinStrandsAction,
                             SIGNAL("triggered(bool)"),
                             self.activateJoinStrands_Command)
        
        change_connect(self.makeCrossoversAction,
                             SIGNAL("triggered(bool)"),
                             self.activateMakeCrossovers_Command)
        
        change_connect(self.dnaOrigamiAction, 
                             SIGNAL("triggered()"),
                             self.activateDnaOrigamiEditCommand)
        
        change_connect(self.convertDnaAction, 
                             SIGNAL("triggered()"),
                             self.convertDnaCommand)
        
        
        
        if 1: # the new way, with the "DNA Order" PM.
            change_connect(self.orderDnaAction, 
                                 SIGNAL("triggered(bool)"),
                                 self.activateOrderDna_Command)
        else: # the old way (without the PM)
            change_connect(self.orderDnaAction, 
                                 SIGNAL("triggered()"),
                                 self.orderDnaCommand)
        
        change_connect(self.editDnaDisplayStyleAction, 
                             SIGNAL("triggered(bool)"),
                             self.activateDisplayStyle_Command)
    
    def ORIGINAL_activateFlyoutToolbar(self): #Unused as of 2008-08-13 (and onwards)
        #This method can be removed in the near future. Testing has not discovered
        #any new bugs after Ui_DnaFlyout was inherited from Ui_AbstractFlyout. 
        """
        Updates the flyout toolbar with the actions this class provides. 
        """                   
        if self._isActive:
            return
        
        self._isActive = True
        
        #Temporary workaround for bug 2600 .
        #until the Command Toolbar code is revised
        #When DnaFlyout toolbar is activated, it should switch to (check) the 
        #'Build Button' in the control area. So that the DnaFlyout 
        #actions are visible in the flyout area of the command toolbar. 
        #-- Ninad 2008-01-21. 
        #UPDATE 2008-04-12: There is a better fix available (see bug 2801)
        #That fix is likely to unnecessiate the following -- but not tested 
        #well. After more testing, the following line of code can be removed
        #@see: CommandToolbar.check_controlAreaButton_containing_action -- Ninad
        
        self.win.commandToolbar.cmdButtonGroup.button(0).setChecked(True)
        #Now update the command toolbar (flyout area)
        self.win.commandToolbar.updateCommandToolbar(self.win.buildDnaAction,
                                                     self)
        #self.win.commandToolbar._setControlButtonMenu_in_flyoutToolbar(
                    #self.cmdButtonGroup.checkedId())
        self.exitDnaAction.setChecked(True)
        
       
        self.connect_or_disconnect_signals(True)
    
                
            
    def activateDnaDuplex_EditCommand(self, isChecked):
        """
        Slot for B{Duplex} action.
        """
            
        self.win.insertDna(isChecked)
        
        #IMPORTANT: 
        #For a QAction, the method 
        #setChecked does NOT emmit the 'triggered' SIGNAL. So 
        #we can call self.breakStrandAction.setChecked without invoking its 
        #slot method!
        #Otherwise we would have needed to block the signal when action is 
        #emitted ..example we would have called something like :
        #'if self._block_dnaDuplexAction_event: return' at the beginning of this
        #method. Why we didn't use QAction group -- We need these actions to be
        # a) exclusive as well as
        #(b) 'toggle-able' (e.g. if you click on a checked action , it should 
        #uncheck)
        #QActionGroup achieves (a) but can't do (b) 
        
        #Uncheck all the actions except the dna duplex action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.dnaDuplexAction and action.isChecked():
                action.setChecked(False)
            
    def activateBreakStrands_Command(self, isChecked):
        """
        Call the method that enters BreakStrands_Command. 
        (After entering the command) Also make sure that 
        all the other actions on the DnaFlyout toolbar are unchecked AND 
        the BreakStrands Action is checked. 
        """
        
        self.win.enterBreakStrandCommand(isChecked)
        
        #Uncheck all the actions except the break strands action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.breakStrandAction and action.isChecked():
                action.setChecked(False)
            
    def activateJoinStrands_Command(self, isChecked):
        """
        Call the method that enters JoinStrands_Command. (After entering the 
        command) Also make sure that all the other actions on the DnaFlyout 
        toolbar are unchecked AND the JoinStrands Action is checked. 
        """
        self.win.enterJoinStrandsCommand(isChecked)
        
        #Uncheck all the actions except the join strands action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.joinStrandsAction and action.isChecked():
                action.setChecked(False)
            elif action is self.joinStrandsAction and not action.isChecked():
                pass
                #action.setChecked(True)
                
    def activateMakeCrossovers_Command(self, isChecked):
        """
        Call the method that enters JoinStrands_Command. (After entering the 
        command) Also make sure that all the other actions on the DnaFlyout 
        toolbar are unchecked AND the JoinStrands Action is checked. 
        """
        self.win.enterMakeCrossoversCommand(isChecked)
        
        #Uncheck all the actions except the join strands action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.makeCrossoversAction and action.isChecked():
                action.setChecked(False)
            elif action is self.makeCrossoversAction and not action.isChecked():
                pass
                #action.setChecked(True)
        
    def activateDnaOrigamiEditCommand(self):
        """
        Slot for B{Origami} action.
        """
        msg1 = greenmsg("DNA Origami: ")
        msg2 = "Not implemented yet."
        final_msg = msg1 + msg2
        env.history.message(final_msg)
        
    
    def convertDnaCommand(self):
        """
        Slot for B{Convert DNA} action.
        """
        cs = self.win.commandSequencer
        cs.userEnterCommand('CONVERT_DNA')
        return
    
    def orderDnaCommand(self):
        """
        Slot for B{Order DNA} action.
        @see: MWSemantics.orderDna
        """
        self.win.orderDna()
        return
    
    def activateOrderDna_Command(self, isChecked):
        """
        Call the method that enters OrderDna_Command. 
        (After entering the command) Also make sure that 
        all the other actions on the DnaFlyout toolbar are unchecked AND 
        the DisplayStyle Action is checked. 
        """
        
        self.win.enterOrderDnaCommand(isChecked)
        
        #Uncheck all the actions except the Order DNA action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.editDnaDisplayStyleAction and action.isChecked():
                action.setChecked(False)
                
    def activateDisplayStyle_Command(self, isChecked):
        """
        Call the method that enters DisplayStyle_Command. 
        (After entering the command) Also make sure that 
        all the other actions on the DnaFlyout toolbar are unchecked AND 
        the DisplayStyle Action is checked. 
        """
        
        self.win.enterDnaDisplayStyleCommand(isChecked)
        
        #Uncheck all the actions except the (DNA) display style action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.editDnaDisplayStyleAction and action.isChecked():
                action.setChecked(False)
                
                
    def resetStateOfActions(self):
        """
        See superclass for more documentation. 
        
        Resets the state of actions in the flyout toolbar.
        It unchecks all the actions EXCEPT the ExitModeAction. This is called 
        while resuming a command. 
        
        This is called while resuming a command.         
        
        Example: If Insert > Dna command is exited and the Build > Dna command
        is resumed. When this happens, program needs to make sure that the 
        Insert > DNA button in the flyout is unchecked. It is done by using this
        method. 
        
        
        @see: self.deActivateFlyoutToolbar()
        @see: self.activateBreakStrands_Command() 
        @see: AbstractFlyout.resetStateOfActions()
        @see: baseCommand.command_update_flyout() which calls this method. 
        """
        #Uncheck all the actions in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action.isChecked():
                action.setChecked(False)
