# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
$Id$

History:
ninad 20070606: Originally Created this as a temporary work for Alpha9,
                In Alpha9 this class is inherited by PlaneGenerator class. 
                It is still being used because of some missing functionality 
                in GeneratorBaseClass. 
ninad 2007-09-11: Created this file. (split this class out of 
                 ReferenceGeometry.py
ninad 2007-09-17: Code cleanup to split ui part out of this class. 

ninad 2007-10-05: Major changes. Refactored GeometryGeneratorBaseClass 
                  and surrounding code. Also renamed GeometryGeneratorBaseClass 
                  to EditController, similar changes in surrounding code
"""

import platform
from utilities.Log        import greenmsg
from utilities.Comparison import same_vals

from constants            import permit_gensym_to_reuse_name
from GeneratorBaseClass   import AbstractMethod



class EditController:
    """
    Geometry Generator base class . This is a temporary class for Alpha9. 
    It should be modified   or deleted during post A9 development 
    (when we revise GeneratorBaseClass)  This is very much like 
    GeneratorBaseClass but has a few modifications
    for use in PlaneEditController.  
    At present, PlaneEditController inherits this.
    """
    # see definition details in GeneratorBaseClass
    cmd      =  "" 
    cmdname  =  "" 
    _gensym_data_for_reusing_name = None

    def __init__(self, win):
        """
        Constructor for the class EditController.        
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
    
    def createStructure(self):
        """
        Default implementation of createStructure method. 
        Might be overridden in  subclasses. Creates an instance (object)
        of the structure this editController wants to generate. This implements
        a topLevel command that the client can execute to create an object it 
        wants.
        
        Example: If its a plane editController, this method will create an 
                object of class Plane. 
        
        This method also creates a propMgr objects if it doesn't
        exist , shows the property manager and sets the model (the plane) 
        in preview state.
        
        @see: L{self.editStructure} (another top level command that facilitates
              editing an existing object (existing structure). 
        @see: L{part.createPlaneEditController} for an example use.
        """
        
        assert not self.struct
        
        self.struct = self._createStructure()
        
        if not self.propMgr:
            self.propMgr = self._createPropMgrObject()
            
        self.propMgr.show()
  
        if self.struct:
            self.preview_or_finalize_structure(previewing = True)        
            self.win.assy.place_new_geometry(self.struct)
        
    def editStructure(self):
        """
        Default implementation of editStructure method. Might be overridden in 
        subclasses. It facilitates editing an existing object 
        (existing structure). This implements a topLevel command that the client
        can execute to edit an existing object(i.e. self.struct) that it wants.
        
        Example: If its a plane edit controller, this method will be used to 
                edit an object of class Plane. 
        
        This method also creates a propMgr objects if it doesn't exist and 
        shows this property manager 
        
        @see: L{self.createStructure} (another top level command that 
              facilitates creation of a model object created by this 
              editController
        @see: L{Plane.edit} and L{PlaneEditController._createPropMgrObject} 
        """
        
        assert self.struct
    
        if not self.propMgr:
            self.propMgr = self._createPropMgrObject()
            
        self.existingStructForEditing = True
        self.old_props = self.struct.getProps()
        self.propMgr.show() 
            
    def _createStructure(self, params):
        """
        Create the model object which this edit controller  creates) 
        Abstract method.         
        @see: L{PlaneEditController._createStructure}
        """
        raise AbstractMethod()
    
    def _createPropMgrObject(self):
        """
        Abstract method (overridden in subclasses). Creates a property manager 
        object (that defines UI things) for this editController. 
        """
        raise AbstractMethod()
    
    def _modifyStructure(self, params):
        """
        Abstract method that modifies the structure (i.e. the object created 
        by this editController) using the parameters provided.
        @param params: The parameters used as an input to modify the structure
                       (object created using this editcontroller) 
        @type  params: tuple
        @see: L{PlaneEditController._modifyStructure}
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
        
        ################################
        ##For certain edit controllers, it is possible that self.struct is 
        ##not created. If so simply return (don't use assert self.struct)
        #This is a commented out stub code for the edit controllers 
        #such as DNAEditController which take input from the user before 
        #creating the struct. TO BE REVISED -- Ninad20071009
        #if 0:
            #if not self.struct:
                #self.struct = self._createStructure()   
                #if not self.struct:
                    #return
        ###############################
            
        self.win.assy.current_command_info(cmdname = self.cmdname) 
        
        params = self._gatherParameters()        

        if not same_vals( params, self.previousParams):
            self._modifyStructure(params)
            
        name = self.struct.name         
    
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
                self.win.glpane.gl_update()               
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
            self._revertNumber()
            self.win.win_update() 
    
    def _revertNumber(self):
        """
        Private method. Called internally when we discard the current structure
        and want to permit a number which was appended to its name to be reused.

        WARNING: the current implementation only works for classes which set
        self.create_name_from_prefix
        to cause our default _build_struct to set the private attr we use
        here, self._gensym_data_for_reusing_name, or which set it themselves
        in the same way (when they call gensym).
        
        This method is copied over from GeneratorBaseClass._revert_number
        """
        if self._gensym_data_for_reusing_name:
            prefix, name = self._gensym_data_for_reusing_name
                # this came from our own call of gensym, or from a caller's if
                # it decides to set that attr itself when it calls gensym
                # itself.
            permit_gensym_to_reuse_name(prefix, name)
        self._gensym_data_for_reusing_name = None
        return
