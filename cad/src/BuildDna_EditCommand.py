# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildDna_EditCommand.py

@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2008-01-11: Created


TODO: as of 2008-01-11
- Needs more documentation and the file is subjected to heavy revision. 
This is an initial implementation of default Dna edit mode.
- Methods such as callback_addSegments might be renamed.
BUGS:
- Has bugs such as -- Flyout toolbar doesn't get updated when you return to 
  BuildDna_EditCommand from a a temporary command. 
- Just entering and leaving BuilddDna_EditCommand creates an empty DnaGroup
"""


from EditCommand import EditCommand
from dna_model.DnaGroup import DnaGroup
from utilities.Log  import greenmsg
from GeneratorBaseClass import PluginBug, UserError

from constants import gensym
from Ui_DnaFlyout import DnaFlyout

from SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from BuildDna_PropertyManager import BuildDna_PropertyManager


class BuildDna_EditCommand(EditCommand):
    """
    BuildDna_EditCommand provides a convenient way to edit or create
    a DnaGroup object     
    """
    cmd              =  greenmsg("Build DNA: ")
    sponsor_keyword  =  'DNA'
    prefix           =  'Dna '   # used for gensym
    cmdname          = "Build Dna"
    commandName       = 'BUILD_DNA'
    featurename       = 'Build Dna '
    
    GraphicsMode_class = SelectChunks_GraphicsMode
    
    command_should_resume_prevMode = False
    command_has_its_own_gui = True
    command_can_be_suspended = True
    
    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 
   

    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for BuildDna_EditCommand
        """
        EditCommand.__init__(self, commandSequencer)
        self.struct = struct
    
    
    def init_gui(self):
        """
        Do changes to the GUI while entering this command. This includes opening 
        the property manager, updating the command toolbar , connecting widget 
        slots (if any) etc. Note: The slot connection in property manager and 
        command toolbar is handled in those classes. 
        
        Called once each time the command is entered; should be called only 
        by code in modes.py
        
        @see: L{self.restore_gui}
        """
        EditCommand.init_gui(self)        
    
        if self.flyoutToolbar is None:
            self.flyoutToolbar = DnaFlyout(self.win, self.propMgr)
        
        self.flyoutToolbar.activateFlyoutToolbar()
    
    def resume_gui(self):
        """
        Called when this command, that was suspended earlier, is being resumed. 
        The temporary command (which was entered by suspending this command)
        might have made some changes to the model which need to be reflected 
        while resuming command. 
        
        Example: A user enters BreakStrands_Command by suspending 
        BuildDna_EditCommand, then breaks a few strands, thereby creating new 
        strand chunks. Now when the user returns to the BuildDna_EditCommand, 
        the command's property manager needs to update the list of strands 
        because of the changes done while in BreakStrands_Command.  
        @see: Command.resume_gui
        @see: Command._enterMode where this method is called.
        """
        #NOTE: Doing command toolbar updates in this method doesn't alwayswork.
        #consider this situation : You are in a) BuildDna_EditCommand, then you 
        #b) enter DnaDuplex_EditCommand(i.e. Dna line) and from this temporary 
        #command, you directly c) enter BreakStrands_Command 
        #-- During b to c, 1) it first exits (b) , 2) resumes (a) 
        #and then 3)enters (c)
        #This method is called during operation #2 and any changes to flyout 
        #toolbar are reset during #3  --- Ninad 2008-01-14
        if self.propMgr:
            self.propMgr.updateListWidgets()
        

    def restore_gui(self):
        """
        Do changes to the GUI while exiting this command. This includes closing 
        this mode's property manager, updating the command toolbar ,
        Note: The slot connection/disconnection in property manager and 
        command toolbar is handled in those classes.
        @see: L{self.init_gui}
        """
        EditCommand.restore_gui(self)
        if self.flyoutToolbar:
            self.flyoutToolbar.deActivateFlyoutToolbar()
              
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
    
    def runCommand(self):
        """
        Overrides EditCommand.runCommand
        """
        self.struct = None     
        self.propMgr.updateListWidgets()

    def create_and_or_show_PM_if_wanted(self, showPropMgr = True):
        """
        Create the property manager object if one doesn't already exist 
        and then show the propMgr if wanted by the user. 
        @param showPropMgr: If True, show the property manager 
        @type showPropMgr: boolean
        """
        EditCommand.create_and_or_show_PM_if_wanted(
            self,
            showPropMgr = showPropMgr)
        
        self.propMgr.updateMessage("Use appropriate command in the command "\
                                   "toolbar to create or modify a DNA Object"\
                                   "<br>"                                   
                                   )
        
    def createStructure(self, showPropMgr = True):
        """
        Overrides superclass method. It doesn't do anything for this type
        of editcommand
        """

        self.preview_or_finalize_structure(previewing = True)
            

    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr        
        propMgr = self.win.createBuildDnaPropMgr_if_needed(self)
        return propMgr


    def _createStructure(self):
        """
        creates and returns the structure (in this case a L{Group} object that 
        contains the DNA strand and axis chunks. 
        @return : group containing that contains the DNA strand and axis chunks.
        @rtype: L{Group}  
        @note: This needs to return a DNA object once that model is implemented        
        """
       
        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name
        
               
        # Create the model tree group node. 
        # Make sure that the 'topnode'  of this part is a Group (under which the
        # DNa group will be placed), if the topnode is not a group, make it a
        # a 'Group' (applicable to Clipboard parts).See part.py
        # --Part.ensure_toplevel_group method. This is an important line
        # and it fixes bug 2585
        self.win.assy.part.ensure_toplevel_group()
       
        dnaGroup = DnaGroup(self.name, 
                         self.win.assy,
                         self.win.assy.part.topnode,
                         editCommand = self)
        try:
            
            self.win.assy.place_new_geometry(dnaGroup)
            
            return dnaGroup

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            dnaGroup.kill()
            raise PluginBug("Internal error while trying to create DNA duplex.")


    def _gatherParameters(self):
        """
        Return the parameters needed to build this structure

        @return: A list of all DnaSegments present withing the self.struct 
                 (which is a dna group) or None if self.structure doesn't exist
        @rtype:  tuple
        """       
        
        #Passing the segmentList as a parameter is not implemented
        ##if self.struct:
            ##segmentList = []
            ##for segment in self.struct.members:
                ##if isinstance(segment, DnaSegment):
                    ##segmentList.append(segment)
            
            ##if segmentList:
                ##return (segmentList)
                    
        return None               


    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        """    
        assert self.struct
        # parameters have changed, update existing structure
        self._revertNumber()

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name
            
        #@NOTE: Unlike editcommands such as Plane_EditCommand, this 
        #editCommand actually removes the structure and creates a new one 
        #when its modified. We don't yet know if the DNA object model 
        # will solve this problem. (i.e. reusing the object and just modifying
        #its attributes.  Till that time, we'll continue to use 
        #what the old GeneratorBaseClass use to do ..i.e. remove the item and 
        # create a new one  -- Ninad 2007-10-24
        self._removeStructure()

        self.previousParams = params        
  
        self.struct = self._createStructure()            
        return 
    
            
    def provideParamsForTemporaryMode(self, temporaryModeName):
        """
        NOTE: This needs to be a general API method. There are situations when 
	user enters a temporary mode , does something there and returns back to
	the previous mode he was in. He also needs to send some data from 
	previous mode to the temporary mode .	 
	@see: B{DnaLineMode}
	@see: self.acceptParamsFromTemporaryMode 
        """
        params = None
        if temporaryModeName == 'DNA_DUPLEX':
            params = (self.callback_addSegments)
        
        return params    
    
    def callback_addSegments(self, segmentList):
        """
        Call back method supplied to the temporary command DnaDuplex_EditCommand. 
        The DnaDuplex_EditCommand gives it a list of segments created 
        while that command was active.
        To be revised and renamed. 
        
        @see: DnaDuplex_EditCommand.restore_gui
        """      
        if self.struct is None:
            self.struct = self._createStructure()  
              
        assert self.struct is not None   
        for segment in segmentList:
            self.struct.addSegment(segment)
        ##self.win.assy.place_new_geometry(dnaGroup)
        self.propMgr.updateListWidgets()
        
        self.previousParams = self._gatherParameters() 
        
        self.win.win_update()


