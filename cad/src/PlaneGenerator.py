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

from PlanePropertyManager import PlanePropertyManager
from GeometryGeneratorBaseClass import GeometryGeneratorBaseClass


class PlaneGenerator(PlanePropertyManager, GeometryGeneratorBaseClass):
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
    
    def __init__(self, win, plane):
        """
        Constructs a Property Manager with a default Plane.
        
        @param win: The NE1 main window.
        @type  win: QMainWindow
        
        @param plane: The plane.
        @type  plane: L{Plane}
        """
        self.name = plane.name # Adopt the plane's name as our name.
        self.win  = win

        PlanePropertyManager.__init__(self, plane)
        GeometryGeneratorBaseClass.__init__(self, win)

    ##=========== Structure Generator like interface TO BE REVISED======##
    def gather_parameters(self):
        """
        Return all the parameters from the Plane Property Manager.
        """
        height  =  self.heightDblSpinBox.value()
        width   =  self.widthDblSpinBox.value()
        atmList =  self.win.assy.selatoms_list()
        self.geometry.changePlanePlacement(self.pmPlacementOptions.checkedId())
        ctr     =  self.geometry.center        
        return (width, height, ctr, atmList)
    
    def build_struct(self, name, params):
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
    
    #Following method should become a part of GeometryGeneratorBase Class. 
    #Not making one as GeometryGenerator class may go away and replaced by 
    #another one. 
    #So easier to copy this method after it is done. -- ninad20070608
    def update_props_if_needed_before_closing(self):
        """
        This updates some cosmetic properties of the Plane (e.g. fill color, 
        border color, etc.) before closing the Property Manager.
        """
        
        # Example: The Plane Property Manager is open and the user is 
        # 'previewing' the plane. Now the user clicks on "Build > Atoms" 
        # to invoke the next command (without clicking "Done"). 
        # This calls openPropertyManager() which replaces the current PM 
        # with the Build Atoms PM.  Thus, it creates and inserts the Plane 
        # that was being previewed. Before the plane is permanently inserted
        # into the part, it needs to change some of its cosmetic properties
        # (e.g. fill color, border color, etc.) which distinguishes it as 
        # a new plane in the part. This function changes those properties.
        # ninad 2007-06-13 
        
        #called in updatePropertyManager in MWsemeantics.py --(Partwindow class)
        
        self.geometry.updateCosmeticProps()
        
        #Don't draw the direction arrow when the object is finalized. 
        if self.geometry.offsetParentGeometry:
            dirArrow = self.geometry.offsetParentGeometry.directionArrow 
            dirArrow.setDrawRequested(False)