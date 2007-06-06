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
        
