# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-07-30: Created to refactor Build Chunks command (currently called
BuildAtoms_Command).  

TODO:

- Classes created to refactor BuildAtoms_Command (rather 'BuildChunks' command)
to be revised further. 
- document
- REVIEW: _reusePropMgr_of_parentCommand -- this is an experimental method 
that will fit in the NEW command API (2008-07-30) . to be revised/ renamed. 
e.g. command_reuse_PM etc.
"""

from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from model.bond_constants import V_SINGLE, V_DOUBLE, V_TRIPLE, V_AROMATIC, V_CARBOMERIC, V_GRAPHITE
from utilities.constants import CL_SUBCOMMAND

_superclass = BuildAtoms_Command
class AtomsTool_Command(BuildAtoms_Command):
    
    featurename = 'Build Atoms Mode/AtomsTool'
    commandName = 'ATOMS_TOOL'
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    command_has_its_own_gui = False
    
    currentActiveTool = 'ATOMS_TOOL'
    
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    command_level = CL_SUBCOMMAND
    command_parent = 'DEPOSIT'
    
    def Enter(self):
        _superclass.Enter(self)
        #NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        self.command_enter_PM()
        
        self.command_enter_flyout()
        
        
    def command_enter_flyout(self):
        """
        REUSE the flyout toolbar from the parent_command (BuildAtoms_command 
        in this case)
        @TODO: 
        - may need cleanup in command stack refactoring. But the method name is 
        such that it fits the new method names in command API.         
        """
        self._reuse_attr_of_parentCommand('flyoutToolbar')
        
    def command_enter_PM(self):
        """
        #NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        @see: self._reuse_attr_of_parentCommand()
        """
        self._reuse_attr_of_parentCommand('propMgr')
   
    def _reuse_attr_of_parentCommand(self, attr_name = ''): 
        """
        Reuse the given attr of the parent command. 
        Example: reuse 'flyoutToolbar' or 'propMgr' attrs in self. 
        @see: self.command_enter_flyout()
        """
        # WARNING: this code is duplicated in other places.
        
        #@TODO: this could be a new command API method. That gets automatically
        #called based on some CL_* flags that decides whether to use certain 
        #attrs such as flyouttoolbar or PM of the parent command
        #-- Ninad 2008-08-01

        # It's not good to add this to Command API, for several reasons,
        # one of which is that it's probably not the best way to do what
        # it's doing. Also, it's only correct for commands which define
        # self.command_parent.
        #
        # For now, to avoid duplicated code, it could be moved to
        # BuildAtoms_Command (but remain private).
        # [bruce 080801 comments]
        
        if not attr_name:
            print_compact_stack("bug: trying to set an attr with no name "
                                "in this command: ")
            return
        
        previousCommand = self.find_parent_command_named( self.command_parent)
        
        if previousCommand:
            try:
                parent_attr = getattr(previousCommand, attr_name)
            except:
                msg = "bug: parent command %s doesn't have an " \
                      "attr named %r" % (previousCommand, attr_name)
                print_compact_traceback( msg + ": " )
                return                
                
            setattr(self, attr_name, parent_attr)

        else:
            msg = "bug: parent command %s not found" % self.command_parent
            print_compact_stack( msg + ": " )
        return
    
    def init_gui(self):
        pass
    
    def restore_gui(self):
        pass
    
    #TEMPORARILY override the is*ToolActive methods in BuildAtoms_Command. 
    #These methods will go away when BuildAtoms command starts treating 
    #each tool as a subcommand. 
    
    def isAtomsToolActive(self):
        """
        Tells whether the Atoms Tool is active (boolean)          
        """        
        return True
    
    def isBondsToolActive(self):
        """
        Tells whether the Bonds Tool is active (boolean)          
        """        
        return False
    
    def isDeletBondsToolActive(self):
        """
        Tells whether the Delete Bonds Tool is active (boolean)          
        """        
        return False
    
    
