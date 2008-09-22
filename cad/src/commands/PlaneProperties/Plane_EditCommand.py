# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Plane_EditCommand.py

@author: Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
ninad 20070606: Created.
ninad 2007-10-05: Refactored, Also renamed PlaneGenerator to Plane_EditCommand
                  while refactoring the old GeometryGeneratorBaseClass
ninad 2007-12-26: Changes to make Plane_EditCommand a command on command stack

Summer 2008: Urmi and Piotr added code to support image display and grid display
             within Plane objects.

@TODO 2008-04-15:
Note that Plane_EditCommand was originally implemented before the command 
sequencer was operational. This class and its Property Manager has some methods 
that need cleanup to matchup with the command/commandsequencer API. 
e.g. in its PM, the method update_props_if_needed_before_closing need to be 
revised because there is any easy way now, to know which command is currently 
active.Also a general clanup is due -- Ninad

TODO 2008-09-09
Refactor update ui related code. e.g. see self.command_will_exit() -- 
self.struct.updatecosmeticProps() should go inside a command_update method. 
[-- Ninad]

"""

from utilities.Log import greenmsg
from command_support.EditCommand import EditCommand
from commands.PlaneProperties.PlanePropertyManager import PlanePropertyManager
from model.Plane import Plane
from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode
from utilities.Comparison import same_vals
from utilities.GlobalPreferences import USE_COMMAND_STACK

_superclass = EditCommand
class Plane_EditCommand(EditCommand):
    """
    The Plane_EditCommand class  provides an editCommand Object.
    The editCommand, depending on what client code needs it to do, may create 
    a new plane or it may be used for an existing plane. 
    """
    
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = None #fully ported

    #@NOTE: self.struct is the Plane object
    
    PM_class = PlanePropertyManager
    
    GraphicsMode_class = SelectAtoms_GraphicsMode

    cmd = greenmsg("Plane: ")
    #
    prefix = '' # Not used by jigs.
    # All jigs like rotary and linear motors already created their
    # name, so do not (re)create it (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix = False 
    #See Command.anyCommand for details about the following flags

    #command_can_be_suspended = False mitigates bug similar to bug 2699
    #(atleast it removes the property manager) . Actual fix will be cleanup of 
    #command/command sequencer and inscreasing the command stack depth
    #-- Ninad 2008-04-15
    command_can_be_suspended = False 
    command_should_resume_prevMode = True
    command_has_its_own_PM = True
        # When <command_should_resume_prevMode> and <command_has_its_own_PM>
        # are both set to True (like here), want_confirmation_corner_type()
        # will determine that the confirmation corner should include the
        # Transient-Done image, which is sometimes OK and sometimes not OK.
        # This is what bug 2701 is about (assigned to me). I will talk to Ninad
        # and Bruce about fixing this (after Rattlesnake). 
        # --Mark 2008-03-24

    commandName = 'REFERENCE_PLANE'
    featurename = "Reference Plane"
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC
    
    #see self.command_update_internal_state() 
    _previous_display_params = None

    def command_entered(self):
        """
        """
        #See EditCommand.Enter for a detailed comment on why self.struct is 
        #set to None while entering this command.
        self.struct = None
        _superclass.command_entered(self)
    
    def command_will_exit(self):
        #Following call doesn't update the struct with steps similar to 
        #ones in bug 2699. Instead calling struct.updateCosmeticProps directly
        #Note 2008-09-09: this code was copied from the former self.restore_gui. 
        #This needs to do inside an update method. 
        if self.hasValidStructure():            
            self.struct.updateCosmeticProps() 
            
        _superclass.command_will_exit(self)
        
          
    if not USE_COMMAND_STACK:        

        def Enter(self):
            """
            Enter this command. 
            @see: _superclass.Enter
            """
            #See _superclass.Enter for a detailed comment on why self.struct is 
            #set to None while entering this command.
            if self.struct:
                self.struct = None
    
            _superclass.Enter(self)
    
        def restore_gui(self):
            """
            @see: _superclass.restore_gui
            """
            _superclass.restore_gui(self)
            #Following call doesn't update the struct with steps similar to 
            #ones in bug 2699. Instead calling struct.updateCosmeticProps directly
            ##self.propMgr.update_props_if_needed_before_closing()
            if self.hasValidStructure():
                self.struct.updateCosmeticProps() 


    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this command supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return Plane

    
    def placePlaneParallelToScreen(self):
        """
        Orient this plane such that it is placed parallel to the screen
        """
        self.struct.placePlaneParallelToScreen()


    def placePlaneThroughAtoms(self):
        """
        Orient this plane such that its center is same as the common center of 
        three or more selected atoms.
        """
        self.struct.placePlaneThroughAtoms()
        #NOTE: This log message can be used to either display a history message 
        #if using NE1 UI or for consol print when command is executed via 
        #command prompt. Its upto the client to use this message. This, 
        #however needs a global updater that will clear previous log message 
        #from this object, in order to avoid errors. (if in some cases, the 
        #logMessage is not there, client could accidentaly use garbage 
        #logMessage hanging out from some previous execution) 
        #This is subject to revision. May not be needed after once Logging 
        #facility (see Log.py) is fully implemented -- Ninad 20070921
        self.logMessage = self.cmd + self.struct.logMessage

    def placePlaneOffsetToAnother(self):
        """
        Orient the plane such that it is parallel to a selected plane , with an
        offset.
        """
        self.struct.placePlaneOffsetToAnother()
        self.logMessage = self.cmd + self.struct.logMessage


    ##=========== Structure Generator like interface ======##
    
    def _gatherParameters(self):
        """
        Return all the parameters from the Plane Property Manager.
        """
        width, height, gridColor, gridLineType, gridXSpacing, gridYSpacing, \
             originLocation,  displayLabelStyle = self.propMgr.getParameters()
    
        atmList =  self.win.assy.selatoms_list()
        self.propMgr.changePlanePlacement(
            self.propMgr.pmPlacementOptions.checkedId())        
        
        if self.struct:            
            ctr     =  self.struct.center 
            imagePath = self.struct.imagePath    
        else:
            ctr = None
            imagePath = ''
   
        
        return (width, height, ctr, atmList, imagePath, 
                gridColor, gridLineType, gridXSpacing, 
                gridYSpacing, originLocation, displayLabelStyle)
        
    def _createStructure(self):
        """
        Create a Plane object. (The model object which this edit controller 
        creates) 
        """
        assert not self.struct
               
        self.win.assy.part.ensure_toplevel_group()        
        struct = Plane(self.win, self)
        self.win.assy.place_new_geometry(struct)

        return struct


    def _modifyStructure(self, params):
        """
        Modifies the structure (Plane) using the provided params.
        @param params: The parameters used as an input to modify the structure
                       (Plane created using this Plane_EditCommand) 
        @type  params: tuple
        """
        assert self.struct
        assert params 
        assert len(params) == 11           
        width, height, center_junk, atmList_junk, imagePath, \
             gridColor, gridLineType, gridXSpacing, \
             gridYSpacing,  originLocation, displayLabelStyle = params
      
        self.struct.width   =  width        
        self.struct.height  =  height 
        self.struct.imagePath = imagePath
        self.struct.gridColor = gridColor
        self.struct.gridLineType = gridLineType
        self.struct.gridXSpacing = gridXSpacing
        self.struct.gridYSpacing = gridYSpacing        
        self.struct.originLocation = originLocation
        self.struct.displayLabelStyle = displayLabelStyle
                
        self.win.win_update() # Update model tree
        self.win.assy.changed()        

    ##=====================================##
    
    def command_update_internal_state(self):
        """
        Extends the superclass method.
        This method should replace model_changed() eventually. This method 
        calss self.model_changed at the moment.  
        @see:baseCommand.command_update_internal_state() for documentation
        
        @see: PlanePropertyManager._update_UI_do_updates()
        @see: PlanePropertyManager.update_spinboxes()
        @see: Plane.resizeGeometry()        
        """   
        self.model_changed()
    
        
    def model_changed(self):
        
        #check first if the plane object exists first
        if not self.hasValidStructure():
            return       
        
        #NOTE: The following ensures that the image path and other display 
        #prams are properly updated in the plane. Perhaps its better done using 
        #env.prefs? Revising this code to fix bugs in resizing because
        #of the self._modifyStructure call. See also original code in 
        #Revision 12982  -- Ninad 2008-09-19
                
        currentDisplayParams = self.propMgr.getCurrrentDisplayParams()
                
        if same_vals(currentDisplayParams, self._previous_display_params):
            return
        
        self._previous_display_params = currentDisplayParams
        
        params = self._gatherParameters()
        self._modifyStructure(params)
        
    def runCommand(self):
        """
        Overrides superclass method. 
        Run this edit command. This method is called when user invokes 
        Insert > Plane command (to create a new plane object) . In addition 
        to creating the Plane object and Property manager, this also updates
        the property manager values with the ones for the new Plane object. 
        
        @see: MWSemantics.createPlane() which calls this while inserting a 
        new Plane
        @see: self.editStructure()
        @see: PlanePropertyManager.setParameters()
        @see: self._updatePropMgrParams()
        @TODO: The code that updates the PropMgr params etc needs to be in the 
        EditCommand API method/
        
        """
        _superclass.runCommand(self)
        if self.hasValidStructure():             
            self._updatePropMgrParams()

            #Store the previous parameters. Important to set it after you 
            #set attrs in the propMgr. 
            #self.previousParams is used in self._previewStructure and 
            #self._finalizeStructure to check if self.struct changed.
            self.previousParams = self._gatherParameters()
        
    def editStructure(self, struct = None):
        """
        """
        _superclass.editStructure(self, struct)        
        if self.hasValidStructure():             
            self._updatePropMgrParams()

            #Store the previous parameters. Important to set it after you 
            #set attrs in the propMgr. 
            #self.previousParams is used in self._previewStructure and 
            #self._finalizeStructure to check if self.struct changed.
            self.previousParams = self._gatherParameters()
            
            
    def _updatePropMgrParams(self):
        """
        Subclasses may override this method. 
        Update some property manager parameters with the parameters of
        self.struct (which is being edited)
        @see: self.editStructure()
        """             
        
        params_for_propMgr = (self.struct.width, 
                              self.struct.height, 
                              self.struct.gridColor, 
                              self.struct.gridLineType, 
                              self.struct.gridXSpacing,
                              self.struct.gridYSpacing,
                              self.struct.originLocation,
                              self.struct.displayLabelStyle
                              )
        
        
        #TODO 2008-03-25: better to get all parameters from self.struct and
        #set it in propMgr?  This will mostly work but some params used in 
        #PM are not required by structy and vice versa. (e.g. struct.name)
      
        self.propMgr.setParameters(params_for_propMgr)
    
