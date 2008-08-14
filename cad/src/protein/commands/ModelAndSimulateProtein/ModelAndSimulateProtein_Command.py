# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
ModelAndSimulate_EditCommand.py

@author: Urmi
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""
from command_support.EditCommand import EditCommand
from utilities.Log  import greenmsg
from utilities.constants import gensym
from ne1_ui.toolbars.Ui_ProteinFlyout_v2 import ProteinFlyout_v2
from protein.commands.ModelAndSimulateProtein.ModelAndSimulateProtein_PropertyManager import ModelAndSimulateProtein_PropertyManager 
from utilities.debug_prefs import debug_pref, Choice_boolean_False

_superclass = EditCommand
class ModelAndSimulateProtein_Command(EditCommand):
    """
    ModelAndSimulateProtein_EditCommand provides a convenient way to edit or create 
    or simulate a Protein object
    """
    cmd              =  greenmsg("Model and simulate protein: ")
    prefix           =  'ProteinGroup'   # used for gensym
    cmdname          = "Model and simulate protein"

    commandName       = 'MODEL_AND_SIMULATE_PROTEIN'
    featurename       = "Model and simulate protein"
    from utilities.constants import CL_ENVIRONMENT_PROVIDING
    command_level = CL_ENVIRONMENT_PROVIDING
    command_should_resume_prevMode = False
    command_has_its_own_PM = True
    command_can_be_suspended = True
    create_name_from_prefix  =  True
    call_makeMenus_for_each_event = True
    
    # methods related to entering this mode         
    dont_update_gui = True
    
    graphicsMode = None
    flyoutToolbar = None
    _currentActiveTool = 'MODEL_PROTEIN'
    
    def __init__(self, commandSequencer, struct = None):
        _superclass.__init__(self, commandSequencer)    
        self.struct = struct
        return
    
    def command_enter_PM(self):
        """
        Overrides superclass method. 
        @see: baseCommand.command_enter_PM()  for documentation
        """
        #important to check for old propMgr object. Reusing propMgr object 
        #significantly improves the performance.
        if not self.propMgr:
            self.propMgr = self._createPropMgrObject()
            #changes.keep_forever(self.propMgr)      
        self.propMgr.show()
        return
    
    def command_exit_PM(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_PM() for documentation
        """
        
        if self.propMgr:
            self.propMgr.close()
        return    
            
    def command_enter_flyout(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_flyout()  for documentation
        """
        if self.flyoutToolbar is None:
            self.flyoutToolbar = self._createFlyoutToolBarObject() 
        self.flyoutToolbar.activateFlyoutToolbar()  
        return
    
    def _createFlyoutToolBarObject(self):
        """
        Create a flyout toolbar to be shown when this command is active. 
        Overridden in subclasses. 
        @see: self.command_enter_flyout()
        """
        flyoutToolbar = ProteinFlyout_v2(self) 
        return flyoutToolbar
    
    def _createPropMgrObject(self):
        propMgr = ModelAndSimulateProtein_PropertyManager(self.w, self)
        return propMgr
        
            
    def command_exit_flyout(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_flyout()  for documentation
        """
        if self.flyoutToolbar:
            self.flyoutToolbar.deActivateFlyoutToolbar()
            
        return
    
    def command_enter_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_misc_actions()  for documentation
        """
        self.w.insertPeptideAction.setChecked(True)
        return
            
    def command_exit_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_misc_actions()  for documentation
        """
        self.w.insertPeptideAction.setChecked(False)  
        return
    
    #END new command API methods ==============================================
    
    
    def init_gui(self):
        """
        Do changes to the GUI while entering this mode. This includes opening 
        the property manager, updating the command toolbar, connecting widget 
        slots etc. 
        
        Called once each time the mode is entered; should be called only by code 
        in modes.py
        
        @see: L{self.restore_gui}
        """
           
        self.dont_update_gui = True # redundant with Enter, 
        self.command_enter_misc_actions()
        self.command_enter_PM() 
        self.command_enter_flyout()
  
        self.dont_update_gui = False
        self.propMgr.updateMessage()
        return
    
    def restore_gui(self):
        """
        Do changes to the GUI while exiting this mode. This includes closing 
        this mode's property manager, updating the command toolbar, 
        disconnecting widget slots etc. 
        @see: L{self.init_gui}
        """
        self.command_exit_misc_actions()
        self.command_exit_flyout()
        self.command_exit_PM()
        return
    
    def setCurrentCommandMode(self, commandName):
        """
        Sets the current active command: modeling or simulation
        """
        self._currentActiveTool = commandName
        return
    
    def enterModelOrSimulateCommand(self, commandName = ''): 
        """
        Enter the given tools subcommand (e.g. Model or Simulate Protein command)
        """
        if not commandName:
            return 
        
        commandSequencer = self.win.commandSequencer
        currentCommand = commandSequencer.currentCommand
        if currentCommand.commandName != commandName:
            # enter command, if not already in it
            commandSequencer.userEnterTemporaryCommand( commandName)
        else:
            # exit command, if already in it
            currentCommand.Done(exit_using_done_or_cancel_button = False)
        
        return
    
    def update_gui(self): 
        """
        can be called many times during the mode;
        should be called only by code in modes.py
        """

        if self.dont_update_gui:   
            return
        
        self.dont_update_gui = True
        try:
            self.update_gui_0()
        except:
            print_compact_traceback("exception from update_gui_0: ")
        self.dont_update_gui = False
        return

    def update_gui_0(self): 
        """
        Overridden in some subclasses. Default implementation does nothing
        @see: B{PasteFromClipboard_Command}
        """        
        pass
    
    def makeMenus(self): #bruce 050705 revised this to support bond menus
        """
        Create context menu for this command. (Build Atoms mode)
        """
        #Urmi 20080806: will implement later, once the basic system is up and
        #working
        return
    
    def StateDone(self):
        """
        @see: Command.StateDone
        """
        
        return None

    def StateCancel(self):
        """
        @see Command.StateCancel
        """
        return None


    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted.
        otherwise returns False. The default implementation always returns
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True.
        @see: Command.keep_empty_group() which is overridden here.
        """

        bool_keep = EditCommand.keep_empty_group(self, group)

        if not bool_keep:
            if group is self.struct:
                bool_keep = True

        return bool_keep

    
