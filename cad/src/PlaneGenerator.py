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


class PlaneGenerator(GeometryGeneratorBaseClass):
    """
    The PlaneGenerator class provides a Property Manager and a structure 
    generator/editor for creating and/or editing a reference Plane.
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
    
    def __init__(self, win, geometry):
        """
        Constructs a Property Manager with a default Plane.
        
        @param win: The NE1 main window.
        @type  win: QMainWindow
        
        @param plane: The plane.
        @type  plane: L{Plane}
        """        
        
        self.geometry = geometry
        self.propMgr = geometry.propMgr
        
        self.name = self.geometry.name # Adopt the plane's name as our name.
        GeometryGeneratorBaseClass.__init__(self, win, struct = self.geometry)

    ##=========== Structure Generator like interface TO BE REVISED======##
    def gather_parameters(self):
        """
        Return all the parameters from the Plane Property Manager.
        """
        height  =  self.propMgr.heightDblSpinBox.value()
        width   =  self.propMgr.widthDblSpinBox.value()
        atmList =  self.win.assy.selatoms_list()
        self.geometry.changePlanePlacement(
            self.propMgr.pmPlacementOptions.checkedId())
        ctr     =  self.geometry.center        
        return (width, height, ctr, atmList)
    
    def buildStructure(self, name, params):
        """
        Build a Plane using the current parameters in the Property Manager.
        
        @param name: The name of the plane.
        @type  name: str
        
        @param params: The plane properties from the PM UI.
        @type  params: tuple
        """
        width, height, center_junk, atmList_junk = params
        self.geometry.width   =  width        
        self.geometry.height  =  height   
        self.geometry.win.win_update() # Update model tree
        self.geometry.win.assy.changed()        
        return self.geometry
    ##=====================================##
    
    