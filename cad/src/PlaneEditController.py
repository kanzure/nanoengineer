# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PlaneEditcontroller.py

@author: Ninad,
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 20070606: Created.
ninad 2007-10-05: Refactored, Also renamed PlaneGenerator to PlaneEditController
                  while refactoring the old GeometryGeneratorBaseClass

"""

from utilities.Log import greenmsg
from EditController import EditController
from PlanePropertyManager import PlanePropertyManager
from Plane import  Plane


class PlaneEditController(EditController):
    """
    The PlaneEditController class  provides an editController Object.
    The editController, depending on what client code needs it to do, may create 
    a new plane or it may be used for an existing plane. 
    """
        
    #@NOTE: self.struct is the Plane object
    
    cmd = greenmsg("Plane: ")
    #
    prefix = '' # Not used by jigs.
    # All jigs like rotary and linear motors already created their
    # name, so do not (re)create it (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix = False 
    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')
    sponsor_keyword = 'Plane'
    #See Command.anyCommand for details about the following flags
    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    
    
    def __init__(self, win, struct = None):
        """
        Constructs an Edit Controller Object. The editController, 
        depending on what client code needs it to do, may create a new plane 
        or it may be used for an existing plane. 
        
        @param win: The NE1 main window.
        @type  win: QMainWindow
        
        @param struct: The model object (in this case plane) that the 
                       PlaneEditController may create and/or edit
                       If struct object is specified, it means this 
                       editController will be used to edit that struct. 
        @type  struct: L{Plane} or None
        
        @see: L{Plane.__init__}
        """     
        EditController.__init__(self, win)
        self.struct = struct      
        
    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editController. 
        """
        assert not self.propMgr
        
        propMgr = PlanePropertyManager(self.win, self)
        
        return propMgr
        
            
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
        height  =  self.propMgr.heightDblSpinBox.value()
        width   =  self.propMgr.widthDblSpinBox.value()
        atmList =  self.win.assy.selatoms_list()
        self.propMgr.changePlanePlacement(
            self.propMgr.pmPlacementOptions.checkedId())
        if self.struct:            
            ctr     =  self.struct.center 
        else:
            ctr = None
        return (width, height, ctr, atmList)
    
    def _createStructure(self):
        """
        Create a Plane object. (The model object which this edit controller 
        creates) 
        """
        assert not self.struct
       
        struct = Plane(self.win, self)
            
        return struct
        
                
    def _modifyStructure(self, params):
        """
        Modifies the structure (Plane) using the provided params.
        @param params: The parameters used as an input to modify the structure
                       (Plane created using this PlaneEditController) 
        @type  params: tuple
        """
        assert self.struct
        assert params 
        assert len(params) == 4             
        
        width, height, center_junk, atmList_junk = params
        self.struct.width   =  width        
        self.struct.height  =  height 
        self.win.win_update() # Update model tree
        self.win.assy.changed()        
        
    ##=====================================##