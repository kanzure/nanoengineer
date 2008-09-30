# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-08-04 Created to aid command stack refactoring. 


TODO: 2008-08-04
- cleanup after command toolbar refactoring. 
- more documentation,
- have more flyouts use this new superclass

@see: Ui_PartLibraryFlyout (a subclass)

REVIEW: should this be moved into the widgets package? [bruce 080827 question]
-- This doesn't 'create a widget' so it shouldn't. But the current pkg location
for all UI_*Flyout modules  needs to be reconsidered [Ninad 2008-09-10]
"""

from utilities.exception_classes import AbstractMethod
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction
from PyQt4.Qt import SIGNAL
from utilities.icon_utilities import geticon

from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED
from utilities.debug import print_compact_stack

class Ui_AbstractFlyout(object):
    
    def __init__(self, command):
        """
        Create necessary flyout action list and update the flyout toolbar in
        the command toolbar with the actions provided by the object of this
        class.                             
        """
        self.command = command
        self.command_for_exit_action = self.command #bruce 080827 guess
        self.parentWidget = self.command.propMgr            
        self.win =self.command.win                       
        self._isActive = False
        self._createActions(self.parentWidget)
        self._addWhatsThisText()
        self._addToolTipText()
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
        
    def _action_in_controlArea_to_show_this_flyout(self):
        """
        To be cleaned up. The current implementation of command toolbar code 
        needs an action in the 'Control Area' of the command toolbar 
        to be provided as an argument in order to update the Flyout toolbar
        Example: If its BuildAtoms FlyoutToolbar, in order to display it, 
        the updateCommandToolbar method needs the 'depositAtomsAction' 
        i.e. the action corresponding to BuildAtoms command to be send 
        as an argument (so that it knows to check the Control Area' button 
        under which this action is defined as a subitem.  this is confusing
        and will be cleaned up. Also it is buggy in case of , for example,
        Paste mode whose action is not present as a submenu in any of the 
        Conteol Area buttons. 
        """
        raise AbstractMethod()   
    
    def _getExitActionText(self):
        """
        Raises AbstractMethod. Subclasses must override this method.
        @see: self._createActions()
        @see: attribute, self.command_for_exit_action
        """
        raise AbstractMethod()
        
    def _createActions(self, parentWidget):
        """
        Define flyout toolbar actions for this mode.
        @see: self._getExitActionText() which defines text for exit action.

        @note: subclasses typically extend this method to define more actions.
        """
        #@NOTE: In Build mode, some of the actions defined in this method are also 
        #used in Build Atoms PM. (e.g. bond actions) So probably better to rename 
        #it as _init_modeActions. Not doing that change in mmkit code cleanup 
        #commit(other modes still implement a method by same name)-ninad20070717
                
        self.exitModeAction = NE1_QWidgetAction(parentWidget, win = self.win)
        exitActionText = self._getExitActionText()
        self.exitModeAction.setText(exitActionText)
        self.exitModeAction.setIcon(geticon('ui/actions/Toolbars/Smart/Exit.png'))
        self.exitModeAction.setCheckable(True)
        self.exitModeAction.setChecked(True)   
            
                
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be extended in subclasses. By default it handles only
        self.exitModeAction.
        
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        
        @see: self.activateFlyoutToolbar, self.deActivateFlyoutToolbar
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect
        
        change_connect(self.exitModeAction, SIGNAL("triggered()"),
                       self._exitModeActionSlot)
        return

    def _exitModeActionSlot(self): #bruce 080827 split this out, 
        """
        Do what's appropriate when self.exitModeAction is triggered. 
        """        
        self.command_for_exit_action.command_Done()
        
    def activateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides. 
        @see: baseCommand.command_update_flyout()
        @see: CommandToolbar.updateCommandToolbar()
        @see: self.deActivateFlyoutToolbar()
        @see: Commandtoolbar._f_current_flyoutToolbar
        """      
        #CommandToolbar._f_current_flyoutToolbar is the current flyout toolbar 
        #that is displayed in the 'flyout area' of the command toolbar. 
        #Example, when Build > Dna command is entered, it sets this attr on the 
        #commandToolbar class to the 'BuildDnaFlyout' object. 
        #When that command is exited, BuildDnaFlyout is first 'deactivated' and 
        #the _f_current_flyoutToolbar is assigned a new value (The flyout 
        #object of the next command entered. This can even be 'None' if the 
        #next command doesn't have a flyoutToolbar)
        current_flyoutToolbar = self.win.commandToolbar._f_current_flyoutToolbar 
        
        if self is current_flyoutToolbar:
            return
        
        #We want to assign  the _f_current_flyoutToolbar as 'self'. Before doing
        #that, the 'current' flyout stored in 
        #CommandToolbar._f_current_flyoutToolbar should be deactivated.         
        if current_flyoutToolbar:
            current_flyoutToolbar.deActivateFlyoutToolbar()
        
        self.win.commandToolbar._f_current_flyoutToolbar = self                    
        
        #Always reset the state of action within the flyout to their default 
        #state while 'activating' any flyout toolbar.         
        #Note: This state may be changed further.       
        #See baseCommand.command_update_flyout() where this method is called 
        #first and then, for example, if it is a subcommand, that sub-command
        #may check the action in the flyout toolbar that invoked it. 
        
        #Example: Enter Build Atoms command, then enter Bonds Tool, and select
        #a bond tool from flyout. Now exit BuildAtoms command and reenter it
        #Upon reentry, it should show the default Atoms Tool in the flyout. 
        #This is acheived by calling the following method. Note that it is 
        #not called in deActivateFlyoutToolbar because there could be some 
        #bugs in how frequently that method is called. So always safe to do it 
        #here.
        
        self.resetStateOfActions()
        
        #May be check self.exitModeAction in the default implementation of 
        #self.resetStateOfActions() and then extend that method in subclasses? 
        #Okay to do it here.
        self.exitModeAction.setChecked(True)
        
                
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
            
        self.updateCommandToolbar()
                    
    
    def deActivateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides.
        @see: self.activateFlyoutToolbar()
        @see: CommandToolbar.resetToDefaultState()
        @see: baseCommand.command_update_flyout()
        """
                    
        current_flyout = self.win.commandToolbar._f_current_flyoutToolbar
        previous_flyout = self.win.commandToolbar._f_previous_flyoutToolbar
        
        if self not in (current_flyout, previous_flyout):
            return
        
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)   
            
        self.updateCommandToolbar(bool_entering = False)
            
    def updateCommandToolbar(self, bool_entering = True):
        """
        Update the command toolbar.
        """        
        obj = self
        self.win.commandToolbar.updateCommandToolbar(
            self._action_in_controlArea_to_show_this_flyout(),
            obj, 
            entering = bool_entering)
        
        return    
    
    def resetStateOfActions(self):
        """
        Default implementation does nothing. Resets the state of actions in the 
        flyout toolbar. Generally, it unchecks all the actions except the 
        'ExitModeAction' (but subclasses can implement it differently) 
        
        This is overridden in subclasses to ensure that the default state of the
        flyout is restored. 
        
        Who overrides this? --
        This is overridden in flyout classes of commands that have potential 
        subcommands which care about flyout and may do changes to it. 
        See BuildDnaFlyout, BuildAtomsFlyout for example.  
        
        In general, it will be called for any command that defines its own 
        FlyoutToolbar_class. In such cases, it is called whenever command is 
        entered or resumed.
        
        Example: When its the default DNA command, this method resets all the 
        actions in the flyout toolbar except the 'ExitModeAction'. When
        it is the 'Build Atoms' command, the default state of the toolbar
        is such that the 'Atoms tool' button in the subcontrol area is checked
        along with the 'Exit' button. 
                           
        Example: If Insert > Dna command is exited and the Build > Dna command
        is resumed. When this happens, program needs to make sure that the 
        Insert > DNA button in the flyout is unchecked. It is done by using this
        method. 
        
        @see: self.deActivateFlyoutToolbar()
        @see: self.activateBreakStrands_Command()         
        @see: baseCommand.command_update_flyout() which calls this method.         
        """
        pass
    
                
    
    def _addWhatsThisText(self):
        """
        Add 'What's This' help text for all actions on toolbar. 
        Default implementation does nothing. Should be overridden in subclasses
        """
        pass
    
    def _addToolTipText(self):
        """
        Add 'Tool tip' help text for all actions on toolbar. 
        Default implementation does nothing. Should be overridden in subclasses
        """
        pass
