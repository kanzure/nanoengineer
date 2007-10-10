# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

This is a superclass for the property managers of various objects that use 
EditController for generating the object. e.g. PlanePropertyManager inherits 
from this class to use common methods such as ok_btn_cliked. 

"""

import env

from PM.PM_Dialog import PM_Dialog

from GeneratorBaseClass import AbstractMethod

class EditController_PM(PM_Dialog):
    """
    
    This is a superclass for the property managers of various objects that use 
    EditController for generating the object. e.g. PlanePropertyManager 
    inherits from this class to use common methods 
    """
    # The title that appears in the Property Manager header.
    title = "Geometry"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = ""
    
    def __init__(self, win, editController):
        """
        Constructor for the EditController_PM
        """
        # pw = part window. 
        # Its subclasses will create their partwindow objects 
        # (and destroy them after Done) -- @@ not be a good idea if we have
        # multiple partwindow support? (i.e. when win object is replaced(?) by 
        # partwindow object for each partwindow).  But this works fine.
        # ..same guess -- because opening multiple windows is not supported
        # When we begin supporting that, lots of things will change and this 
        # might be one of them .--- ninad 20070613
        
        self.editController = editController
        self.struct = self.editController.struct
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
    
    def show(self):
        """
        """
        PM_Dialog.show(self)
        self.enable_or_disable_gui_actions(bool_enable = False)
    
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
        self.editController.preview_or_finalize_structure(previewing = False)
        self.accept() 
        
        env.history.message(self.editController.logMessage)
        
        self.close() # Close the property manager.
        
        self.enable_or_disable_gui_actions(bool_enable = True)
        
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
        self.editController.cancelStructure()
        self.reject() 
        self.close() 
        
        self.enable_or_disable_gui_actions(bool_enable = True)
        # The following reopens the property manager of the command after
        # the PM of the reference geometry editController (i.e. Plane) is closed.
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
        self.editController.preview_or_finalize_structure(previewing = True)
        env.history.message(self.editController.logMessage)
            
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
    
    def enable_or_disable_gui_actions(self, bool_enable = False):
        """
        Enable or disable some gui actions when this property manager is 
        opened or closed, depending on the bool_enable. 
        Subclasses can override this method. 
        
        """
        pass
    
        
    
    
    