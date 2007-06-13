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


from HistoryWidget import greenmsg

from PyQt4.Qt import QDialog
from PlanePropertyManager import PlanePropMgr
from ReferenceGeometry import GeometryGeneratorBaseClass

from debug import print_compact_traceback

class PlaneGenerator(QDialog, PlanePropMgr, GeometryGeneratorBaseClass):
    ''' PlaneGenerator creates the PropertyManager object for Reference Plane.'''
    
    #@NOTE: Reference Plane defines  PlaneGenerator object as 'self.propMgr'. 
    #need to be renamed??
    #@NOTE: self.geometry : is the Plane object (defined in PlanePropMgr)
    #comment ninad 20070606
    
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
        
        self.name = plane.name # Adopt the plane's name as our name.
        self.w = self.win = win
        
        QDialog.__init__(self, win)
        PlanePropMgr.__init__(self, plane)
        GeometryGeneratorBaseClass.__init__(self, win)
        


    ##=========== Structure Generator like interface TO BE REVISED======##
    def gather_parameters(self):
        """Return all the parameters from the Property Manager.
        """
        height = self.heightDblSpinBox.value()
        width = self.widthDblSpinBox.value()
        atmList = self.win.assy.selatoms_list()
        self.geometry.changePlanePlacement(self.planePlacement_btngrp.checkedId())
        ctr = self.geometry.center        
        return (width, height, ctr, atmList)
    
    def build_struct(self, name, params):
        """Build a Plane from the parameters in the Property Manager.
        """
        width, height, center_junk, atmList_junk = params
        self.geometry.width = width        
        self.geometry.height = height   
        self.geometry.win.win_update() # Update model tree
        self.geometry.win.assy.changed()        
        return self.geometry
    ##=====================================##
    
    #Following method should become a part of GeometryGeneratorBase Class. 
    #Not making one as GeometryGenerator class may go away and replaced by another one. 
    #So easier to copy this method after it is done. -- ninad20070608
    def update_props_if_needed_before_closing(self):
        '''This updates some cosmetic properties of the Plane (geometry object)
        before closing the Property Manager. (exiting 'Preview' )'''
        
        ##Example: Plane Property manager is open and user is 'previewing' the 
        ##plane. Now user clicks on the Build Atoms  button to enter that mode. 
        ##This calls the openPropertyManager method which replaces the current 
        ##PM with the Build Atoms PM.  Thus,it permanently adds the Plane that was
        ##being previewed (good or bad -- implementation decision ..OK for now), 
        ##When the plane is 'finalized' it needs to change some of its 
        ##cosmetic properties such as fill color, border color etc so that the 
        ##user will notice that its not being 'previewed' . This function
        ##changes those properties. -- ninad 20070613 
        
        #called in updatePropertyManager in MWsemeantics.py -- (Partwindow class)
        
        self.geometry.updateCosmeticProps()
        
        #Don't draw the direction arrow when the object is finalized. 
        if self.geometry.offsetParentGeometry:
            self.geometry.offsetParentGeometry.directionArrow.setDrawRequested(False)
        
    