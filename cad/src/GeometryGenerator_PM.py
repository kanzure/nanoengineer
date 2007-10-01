# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

This is a superclass for the property managers of various objects that use 
GeometryGenerator for generating the object. e.g. PlanePropertyManager inherits 
from this class to use common methods such as ok_btn_cliked. 

"""

import env

from PM.PM_Dialog import PM_Dialog

from GeneratorBaseClass import AbstractMethod

class GeometryGenerator_PM(PM_Dialog):
    """
    
    This is a superclass for the property managers of various objects that use 
    GeometryGenerator for generating the object. e.g. PlanePropertyManager 
    inherits from this class to use common methods 
    """
    # The title that appears in the Property Manager header.
    title = "Geometry"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = ""
    
    def __init__(self, win, generator):
        """
        Constructor for the GeometryGenerator_PM
        """
        # pw = part window. 
        # Its subclasses will create their partwindow objects 
        # (and destroy them after Done) -- @@ not be a good idea if we have
        # multiple partwindow support? (i.e. when win object is replaced(?) by 
        # partwindow object for each partwindow).  But this works fine.
        # ..same guess -- because opening multiple windows is not supported
        # When we begin supporting that, lots of things will change and this 
        # might be one of them .--- ninad 20070613
        
        self.generator = generator
        self.geometry = self.generator.geometry
        self.win      =  win
        self.pw       =  None     
        self.modePropertyManager = None
        
        PM_Dialog.__init__(self, 
                           self.pmName, 
                           self.iconPath, 
                           self.title
                           )
        self._addGroupBoxes()
        self._addWhatsThisText()
    
    def _addGroupBoxes(self):
        """
        Add various group boxes to this PM. 
        Abstract method. 
        """
        raise AbstractMethod()
    
    def _addWhatsThisText(self):
        """
        Add what's this text. 
        Abstract method.
        """
        raise AbstractMethod()
    
    
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """       
        self.generator.preview_or_finalize_structure(previewing = False)
        self.accept() 
        
        env.history.message(self.generator.logMessage)
        self.struct = None
        
        self.close() # Close the property manager.
        
        # The following reopens the property manager of the mode after 
        # when the PM of the reference geometry is closed. -- Ninad 20070603 
        # Note: the value of self.modePropertyManager can be None
        # @see: anyMode.propMgr
        self.modePropertyManager = self.win.assy.o.mode.propMgr
                
        if self.modePropertyManager:
            #@self.openPropertyManager(self.modePropertyManager)
            # (re)open the PM of the current command (i.e. "Build > Atoms").
            self.open(self.modePropertyManager)
        return 
    
    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
        self.generator.cancelStructure()
        self.reject() 
        self.close() 
        
        # The following reopens the property manager of the command after
        # the PM of the reference geometry generator (i.e. Plane) is closed.
        # Note: the value of self.modePropertyManager can be None.
        # See anyMode.propMgr
        self.modePropertyManager = self.win.assy.o.mode.propMgr
            
        if self.modePropertyManager:
            #@self.openPropertyManager(self.modePropertyManager)
            # (re)open the PM of the current command (i.e. "Build > Atoms").
            self.open(self.modePropertyManager)
        return
    
    def preview_btn_clicked(self):
        """
        Slot for the Preview button.
        """
        self.generator.preview_or_finalize_structure(previewing = True)
        env.history.message(self.generator.logMessage)
            
    def abort_btn_clicked(self):
        """
        Slot for Abort button
        """
        self.cancel_btn_clicked()
        
    def restore_defaults_btn_clicked(self):
        """
        Slot for Restore defaults button
        """
        pass
    
    def enter_WhatsThisMode(self):
        """
        Show what's this text
        """
        pass  
    
    
    