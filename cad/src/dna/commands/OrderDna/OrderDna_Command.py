# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Mark
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.changes as changes
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from command_support.EditCommand import EditCommand
from utilities.constants import red
from dna.commands.OrderDna.OrderDna_PropertyManager import OrderDna_PropertyManager

from graphics.drawing.drawDnaLabels import draw_dnaBaseNumberLabels

from utilities.GlobalPreferences import USE_COMMAND_STACK

# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class OrderDna_GraphicsMode( SelectChunks_GraphicsMode ):
    """
    Graphics mode for "Order DNA" command. 
    """
    def _drawLabels(self):
        """
        Overrides suoerclass method.
        @see: GraphicsMode._drawLabels()
        """
        _superclass_for_GM._drawLabels(self)
        draw_dnaBaseNumberLabels(self.glpane)
    
# == Command part

class OrderDna_Command(EditCommand): 
    """
    
    """
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = "PARTIAL: 2008-09-05: needs PM_class refactoring"
    
    # class constants
    
    commandName = 'ORDER_DNA'
    featurename = "Order DNA"
    from utilities.constants import CL_EXTERNAL_ACTION
    command_level = CL_EXTERNAL_ACTION
         
    GraphicsMode_class = OrderDna_GraphicsMode
   
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    flyoutToolbar = None

    def init_gui(self):
        """
        Initialize GUI for this mode 
        """
        self._init_gui_flyout_action( 'orderDnaAction' , 'BUILD_DNA') 
        
                
        if self.propMgr is None:
            self.propMgr = OrderDna_PropertyManager(self)
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
            
        
    #START new command API methods =============================================
        
    def command_enter_PM(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_PM()  for documentation
        """
        #important to check for old propMgr object. Reusing propMgr object 
        #significantly improves the performance.
        if not self.propMgr:
            self.propMgr = self._createPropMgrObject()
            #@bug BUG: following is a workaround for bug 2494.
            #This bug is mitigated as propMgr object no longer gets recreated
            #for modes -- ninad 2007-08-29
            changes.keep_forever(self.propMgr)  
            
        
        if not USE_COMMAND_STACK:
            self.propMgr.show()    
            
            
    def command_enter_flyout(self):
        """
        Overrides superclass method. 
        @see: EditCommand.command_enter_flyout()
        """
        self._init_gui_flyout_action( 'orderDnaAction' , 'BUILD_DNA') 
        
                
    def command_exit_flyout(self):
        """
        Overrides superclass method. 
        @see: EditCommand.command_exit_flyout()
        """
        if self.flyoutToolbar:
            self.flyoutToolbar.orderDnaAction.setChecked(False)
            
            
    def _createPropMgrObject(self):
        propMgr = OrderDna_PropertyManager(self)
        return propMgr
  
    
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that dna_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """
        
        bool_keep = EditCommand.keep_empty_group(self, group)
        
        if not bool_keep:
            #Lets just not delete *ANY* DnaGroup while in OrderDna_Command
            #Although OrderDna command can only be accessed through
            #BuildDna_EditCommand, it could happen (due to a bug) that the 
            #previous command is not BuildDna_Editcommand. So bool_keep 
            #in that case will return False propmting dna updater to even delete
            #the empty DnaGroup (if it becomes empty for some reasons) of the 
            #BuildDna command. To avoid this ,this method will instruct 
            # to keep all instances of DnaGroup even when they might be empty.            
            if isinstance(group, self.assy.DnaGroup):
                bool_keep = True
            #Commented out code that shows what I was planning to implement 
            #earlier. 
            ##previousCommand = self.commandSequencer.prevMode # keep_empty_group: .struct
            ##if previousCommand.commandName == 'BUILD_DNA':
                ##if group is previousCommand.struct:
                    ##bool_keep = True                                
        
        return bool_keep
