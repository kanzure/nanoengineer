# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad,
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 20070606: Created.

"""
#@@TODO: This class inherits GeometryGeneratorBaseClass
#and not 'GeneratoeBaseClass. 
#GeometryGeneratorBaseClass is a temporary implementation (just for A9) see 
#more notes in ReferenceGeometry.py GeometryGeneratorBaseClass - Ninad 20070606 

from utilities.Log import greenmsg

from GeometryGeneratorBaseClass import GeometryGeneratorBaseClass
from PlanePropertyManager import PlanePropertyManager
from Plane import  Plane


class PlaneGenerator(GeometryGeneratorBaseClass):
    """
    The PlaneGenerator class  Edit Controller) provides a generator Object. 
    The generator, depending on what client code needs it to do, may create a 
    new plane or it may be used for an existing plane. 
    """
    
    #@ NOTE: Reference Plane defines PlaneGenerator object as 'self.propMgr'. 
    # need to be renamed??
    #@ NOTE: self.struct is the Plane object (defined in PlanePropertyManager)
    # comment ninad 20070606
    
    cmd = greenmsg("Plane: ")
    #
    prefix = '' # Not used by jigs.
    # All jigs like rotary and linear motors already created their
    # name, so do not (re)create it (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix = False 
    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')
    sponsor_keyword = 'Plane'
    propMgr = None
    
    def __init__(self, win, struct = None):
        """
        Constructs a Generator (Edit Controller) Object. The generator, 
        depending on what client code needs it to do, may create a new plane 
        or it may be used for an existing plane. 
        
        @param win: The NE1 main window.
        @type  win: QMainWindow
        
        @param struct: The struct object (in this case plane)
                         If struct object is specified, it means 
                         that this generator object will be used for that 
                         struct.
        @type  struct: L{Plane} or None
        
        @see: L{Plane.__init__}
        """     
        GeometryGeneratorBaseClass.__init__(self, win)
        self.struct = struct      
        
    def _createPropMgrObject(self):
        """
        """
        assert not self.propMgr
        
        self.propMgr = PlanePropertyManager(self.win, self)
        
            
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
        Build a Plane using the current parameters in the Property Manager.
        
        @param name: The name of the plane.
        @type  name: str
        
        @param params: The plane properties from the PM UI.
        @type  params: tuple
        """
        
        if not self.struct:
            self.struct = Plane(self.win, self)
            return self.struct
    
    def _modifyStructure(self, params):
        """
        Modifies the structure using the provided params.
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