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
    The generator, depending on what client code needs it to do, then 
    either creates a new plane or its used for an existing plane, 
    which doesn't have a generator. 
    """
    
    #@ NOTE: Reference Plane defines PlaneGenerator object as 'self.propMgr'. 
    # need to be renamed??
    #@ NOTE: self.geometry is the Plane object (defined in PlanePropertyManager)
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
    geometry = None
    
    def __init__(self, win, geometry = None):
        """
        Constructs a Generator (Edit Controller) Object. The generator, 
        depending on what client code needs it to do, then 
        either creates a new plane or its used for an existing plane, 
        which doesn't have a generator.  
        
        @param win: The NE1 main window.
        @type  win: QMainWindow
        
        @param geometry: The geometry object (in this case plane)
                         If this is specified, it means this generator is 
                         created lazily for a Plane object without a generator.
                         If this is specified, it won't create a new Plane 
                         object. See bug 2554 for details
        @type  geometry: L{Plane} or None
        
        @see: L{Plane.__init__}
        """        
        
                
        GeometryGeneratorBaseClass.__init__(self, win)          
        
        if geometry:
            self.geometry = geometry
        else:
            self.geometry = Plane(win, self)         
        self.propMgr = PlanePropertyManager(win, self)
        self.propMgr.show()
        self.preview_or_finalize_structure(previewing = True)
    
    def placePlaneParallelToScreen(self):
        """
        Orient this plane such that it is placed parallel to the screen
        """
        self.geometry.placePlaneParallelToScreen()
        
        
    def placePlaneThroughAtoms(self):
        """
        Orient this plane such that its center is same as the common center of 
        three or more selected atoms.
        """
        self.geometry.placePlaneThroughAtoms()
        #NOTE: This log message can be used to either display a history message 
        #if using NE1 UI or for consol print when command is executed via 
        #command prompt. Its upto the client to use this message. This, 
        #however needs a global updater that will clear previous log message 
        #from this object, in order to avoid errors. (if in some cases, the 
        #logMessage is not there, client could accidentaly use garbage 
        #logMessage hanging out from some previous execution) 
        #This is subject to revision. May not be needed after once Logging 
        #facility (see Log.py) is fully implemented -- Ninad 20070921
        self.logMessage = self.cmd + self.geometry.logMessage
        
    def placePlaneOffsetToAnother(self):
        """
        Orient the plane such that it is parallel to a selected plane , with an
        offset.
        """
        self.geometry.placePlaneOffsetToAnother()
        self.logMessage = self.cmd + self.geometry.logMessage
    
    def edit(self):
        """
        Edit the Plane properties.
        """
        self.existingStructForEditing = True
        self.old_props = self.geometry.getProps()
        self.propMgr.show()   

    ##=========== Structure Generator like interface TO BE REVISED======##
    def gather_parameters(self):
        """
        Return all the parameters from the Plane Property Manager.
        """
        height  =  self.propMgr.heightDblSpinBox.value()
        width   =  self.propMgr.widthDblSpinBox.value()
        atmList =  self.win.assy.selatoms_list()
        self.propMgr.changePlanePlacement(
            self.propMgr.pmPlacementOptions.checkedId())
        if self.geometry:            
            ctr     =  self.geometry.center 
        else:
            ctr = None
        return (width, height, ctr, atmList)
    
    def buildStructure(self, params = None):
        """
        Build a Plane using the current parameters in the Property Manager.
        
        @param name: The name of the plane.
        @type  name: str
        
        @param params: The plane properties from the PM UI.
        @type  params: tuple
        """
 
        if params:
            width, height, center_junk, atmList_junk = params
            self.geometry.width   =  width        
            self.geometry.height  =  height 

        self.win.win_update() # Update model tree
        self.win.assy.changed()        
        return self.geometry
    ##=====================================##