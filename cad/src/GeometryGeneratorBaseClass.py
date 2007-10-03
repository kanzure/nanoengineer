# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
$Id$

#####=============TEMPORARY GeometryGeneratorBaseClass=========###

#@TODO: This is a temporary class for Alpha9.x, Alpha10 It should be modified
#or deleted during post A9 development (when we revise GeneratorBaseClass)
#This is very much like GeneratorBaseClass but has a few modifications
#for use in PlaneGenerator.  At present, only PlaneGenerator inherits this
#class. -- Ninad 2007-06-06

History:
ninad 20070606: Originally Created this as a temporary work for Alpha9,
                In Alpha9 this class is inherited by PlaneGenerator class. 
                It is still being used because of some missing functionality 
                in GeneratorBaseClass. 
ninad 2007-09-11: Created this file. (split this class out of 
                 ReferenceGeometry.py
ninad 2007-09-17: Code cleanup to split ui part out of this class. 

"""

import platform
import Utility
from utilities.Log import greenmsg
from state_utils   import same_vals

from GeneratorBaseClass import AbstractMethod


class GeometryGeneratorBaseClass:
    """
    Geometry Generator base class . This is a temporary class for Alpha9. 
    It should be modified   or deleted during post A9 development 
    (when we revise GeneratorBaseClass)  This is very much like 
    GeneratorBaseClass but has a few modifications
    for use in PlaneGenerator.  At present, PlaneGenerator inherits this.
    """
    # see definition details in GeneratorBaseClass
    cmd      =  "" 
    cmdname  =  "" 

    ##======common methods for Property Managers=====###
    #@NOTE: This copies some methods from GeneratorBaseClass
    #first I intended to inherit ReferenceGeometry from that class but 
    #had weired problems in importing it. Something to do with 
    #QPaindevice/ QApplication /QPixmap. NE1 didn't start de to that error
    #Therefore, implemented and modified the following methods. OK for Alpha9 
    #and maybe later -- Ninad 20070603
    
     # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        """
        Constructor for the class GeometryGeneratorBaseClass.        
        """
        self.win = win
        self.previousParams       =  None
        self.old_props            =  None
        self.logMessage           = ''
        
        self.struct               =  None
        self.existingStructForEditing  =  False
    
        #bruce 060616 added the following kluge to make sure both cmdname 
        #and cmd are set properly.
        if not self.cmdname and not self.cmd:
            self.cmdname = "Generate something"
        if self.cmd and not self.cmdname:
            # deprecated but common, as of 060616
            self.cmdname = self.cmd # fallback
            try:
                cmdname = self.cmd.split('>')[1]
                cmdname = cmdname.split('<')[0]
                cmdname = cmdname.split(':')[0]
                self.cmdname = cmdname
            except:
                if platform.atom_debug:
                    print "fyi: %r guessed wrong \
                    about format of self.cmd == %r" % (self, self.cmd,)
                
        elif self.cmdname and not self.cmd:
            # this is intended to be the usual situation, but isn't yet, 
            #as of 060616
            self.cmd = greenmsg(self.cmdname + ": ")
        return
    
    def createObject(self):
        """
        Abstract Method (overridden in subclasses). Creates an instance (object)
        of the structure this generator wants to generate. This implements a 
        topLevel command that the client can execute to create an object it wants.
        
        Example: If its a plane generator, this method will create an object of 
                class Plane. 
        
        This method also creates a propMgr objects if it doesn't
        exist , shows the property manager and sets the model (the plane) 
        in preview state.
        
        @see: L{self.editObject} (another top level command that facilitates 
              editing an existing object (existing structure). 
        @see: L{part.createPlaneGenerator} for an example use.
        """
        raise AbstractMethod()
    
    def editObject(self):
        """
        Abstract Method (overridden in subclasses). Facilitates editing an 
        existing object (existing structure). This implements a topLevel command
        that the client can execute to edit an existing object
        (i.e. self.struct) that it wants.
        
        Example: If its a plane generator, this method will be used to edit an 
        object of class Plane. 
        
        This method also creates a propMgr objects if it doesn't
        exist and shows this property manager 
        
        @see: L{self.createObject} (another top level command that facilitates 
              creation of a model object created by this generator 
              (editController)
        @see: L{Plane.edit} and L{PlaneGenerator.editObject} for example use.
        """
        raise AbstractMethod()
        
    
    def _buildStructure(self, params):
        """
        Build a struct using the parameters in the Property Manager.
        Abstract method. 
        
        """
        raise AbstractMethod()

    def _gatherParameters(self):
        """
        Return all the parameters from the Plane Property Manager.
        Abstract method. 
        """
        raise AbstractMethod()
    
    def preview_or_finalize_structure(self, previewing = False):
        """
        Preview or finalize the structure based on the the previeing flag
        @param previewing: If true, the structure will use different cosmetic 
                           properties. 
        @type  previewing: boolean
        """
        
        assert self.struct
    
        self.win.assy.current_command_info(cmdname = self.cmdname) 
        
        params = self._gatherParameters()        

        if not same_vals( params, self.previousParams):
            self.struct = self._buildStructure(params)

        name = self.struct.name
        if not self.existingStructForEditing:
            self.win.assy.place_new_geometry(self.struct)
            self.existingStructForEditing = True            
    
        if previewing:
            self.logMessage = str(self.cmd + "Previewing " + name)
        else:
            self.struct.updateCosmeticProps()
            self.logMessage = str(self.cmd + "Created " + name)
        
        self.previousParams = params      
        self.win.assy.changed()
        self.win.win_update()
                                
    def cancelStructure(self):
        """
        Delete the old structure generated during preview if user modifies 
        some parameters or hits cancel
        """
        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
        
        if self.existingStructForEditing: 
            if self.old_props:
                self.struct.setProps(self.old_props)
                self.struct.updateCosmeticProps()
                self.struct.glpane.gl_update()                 
        else:
            self._removeStructure()
            
    def _removeStructure(self):
        """
        Remove this structure. 
        @see: L{self.cancelStructure}
        """
        if self.struct != None:            
            self.struct.kill()
            self.struct = None       
            self._revert_number()
            self.win.win_update() 
    
    def _revert_number(self):
        """
        need documentation 
        """
        if hasattr(self, '_ViewNum'):
            Utility.ViewNum = self._ViewNum 