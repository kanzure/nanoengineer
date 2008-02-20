# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

Histort
Created on 2008-02-14

TODO: as of 2008-02-14
- Post dna data model implementation:    
  - We need to make sure that the strand doesn't form a ring  ( in other words
    no handles when strand is a ring). The current code ignores that. 
  - implement/ revise methods such as self.modifyStructure(), 
    self._gather_parameters() etc. 
  - self.updateHandlePositions() may need revision if the current supporting 
    methods in class dna_model.DnaSegment change. 

"""
from debug import print_compact_stack

from geometry.VQT import  V
from geometry.VQT import  vlen
from geometry.VQT import  norm

from test_connectWithState import State_preMixin
from exprs.attr_decl_macros import Instance, State
from exprs.__Symbols__ import _self
from exprs.Exprs import call_Expr
from exprs.Exprs import norm_Expr
from prefs_widgets import ObjAttr_StateRef
from exprs.ExprsConstants import Width, Point

from chunk import Chunk

from DnaStrand_GraphicsMode import DnaStrand_GraphicsMode
from DnaStrand_ResizeHandle import DnaStrand_ResizeHandle

from EditCommand import EditCommand 

from dna_model.DnaSegment import DnaSegment

CYLINDER_WIDTH_DEFAULT_VALUE = 0.0

ORIGIN = V(0,0,0)

class DnaStrand_EditCommand(State_preMixin, EditCommand):
    """
    Command to edit a DnaStrand (chunk object as of 2008-02-14)
    
    To edit a Strand, first enter BuildDna_EditCommand (accessed using 
    Build> Dna) then, select a strand chunk of an existing DnaSegment within the 
    DnaGroup you are editing. When you select the strand chunk, it enters 
    DnaStrand_Editcommand, shows its property manager and also shows the 
    resize handles if any.
    """
    cmd              =  'Dna Strand'
    sponsor_keyword  =  'DNA'
    prefix           =  'Strand '   # used for gensym
    cmdname          = "DNA_STRAND"
    commandName       = 'DNA_STRAND'
    featurename       = 'Edit_Dna_Strand'


    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    command_can_be_suspended = False

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 

    #Graphics Mode 
    GraphicsMode_class = DnaStrand_GraphicsMode

    #@see: self.updateHandlePositions for details on how these variables are 
    #used in computation. 
    #@see: DnaStrand_ResizeHandle and handle declaration in this class 
    #definition
    handlePoint1 = State( Point, ORIGIN)
    handlePoint2 = State( Point, ORIGIN)    
    axisEnd1 = State( Point, ORIGIN)
    axisEnd2 = State( Point, ORIGIN)
    #TODO: 'cylinderWidth attr used for resize handles -- needs to be renamed 
    #along with 'height_ref attr in exprs.DraggableHandle_AlongLine
    cylinderWidth = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE) 
    cylinderWidth2 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE) 
        
    #Resize Handles for Strand. See self.updateHandlePositions()
    leftHandle = Instance(         
        DnaStrand_ResizeHandle( 
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth'),
            origin = handlePoint1,
            fixedEndOfStructure = handlePoint2,
            direction = norm_Expr(axisEnd1 - axisEnd2)
            ))

    rightHandle = Instance( 
        DnaStrand_ResizeHandle(
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth2'),
            origin = handlePoint2,
            fixedEndOfStructure = handlePoint1,
            direction = norm_Expr(axisEnd2 - axisEnd1)
        ))
    

    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for DnaDuplex_EditCommand
        """
        
        glpane = commandSequencer
        State_preMixin.__init__(self, glpane)        
        EditCommand.__init__(self, commandSequencer)
        self.struct = struct
        
        #DnaSegment object to which this strand belongs 
        self._parentDnaSegment = None
        
        #It uses BuildDna_EditCommand.flyoutToolbar ( in other words, that 
        #toolbar is still accessible and not changes while in this command)
        flyoutToolbar = None

        #Graphics handles for editing the structure . 
        self.handles = []        
        self.grabbedHandle = None

    def init_gui(self):
        """
        Initialize gui. 
        """
        #@see DnaSegment_EditCommand.init_gui() for a detailed note. 
        #This command implements similar thing 
        self.create_and_or_show_PM_if_wanted(showPropMgr = False)
        
    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = self.win.createDnaStrandPropMgr_if_needed(self)
        return propMgr

    def _gatherParameters(self):
        """
        Return the parameters from the property manager UI.

        @return: All the parameters (get those from the property manager):
                 - numberOfBases
                 - dnaForm
                 - basesPerTurn
                 - endPoint1
                 - endPoint2
        @rtype:  tuple
        """     
        return None
    
    def _createStructure(self):
        """
        Creates and returns the structure -- TO BE IMPLEMENTED ONCE 
        DNA_MODEL IS READY FOR USE.
        @return : DnaStrand.
        @rtype: L{Group}  
        @note: This needs to return a DNA object once that model is implemented        
        """
        pass
    
    def _modifyStructure(self, params):
        """
        TO BE IMPLEMENTED ONCE 
        DNA_MODEL IS READY FOR USE.
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        """    
        pass
    
    def getStructureName(self):
        """
        Returns the name string of self.struct if there is a valid structure. 
        Otherwise returns None. This information is used by the name edit field 
        of  this command's PM when we call self.propMgr.show()
        @see: DnaStrand_PropertyManager.show()        
        @see: self.setStructureName
        """
        if self.hasValidStructure():
            return self.struct.name
        else:
            return None
        
    def setStructureName(self, name):
        """
        Sets the name of self.struct to param <name> (if there is a valid 
        structure. 
        The PM of this command callss this method while closing itself 
        @param name: name of the structure to be set.
        @type name: string
        @see: DnaStrand_PropertyManager.close()
        @see: self.getStructureName()
        @see: DnaSegment_GraphicsMode.leftUp , 
              DnaSegment_editCommand.setStructureName for comments about some 
              issues.         
        """
               
        if self.hasValidStructure():
            self.struct.name = name
    
    def editStructure(self, struct = None):
        """
        Edit the structure 
        @param struct: structure to be edited (in this case its a strand chunk)
        @type struct: chunk or None (this will change post dna data model)
        """
        EditCommand.editStructure(self, struct)        
        if self.struct:
            #TO BE REVISED post dna data model - 2008-02-14
            if isinstance(self.struct.dad , DnaSegment):
                self._parentDnaSegment = self.struct.dad   
                
            self._updateHandleList()
            self.updateHandlePositions()
    
    def hasValidStructure(self):
        """
        Tells the caller if this edit command has a valid structure. 
        Overrides EditCommand.hasValidStructure()
        """
        
        if self.struct is None:
            return False
                
        if self.struct.killed(): # (bruce080213: can this happen?)
            return False
        
        if isinstance(self.struct, Chunk) and self.struct.isStrandChunk(): 
            return True
        
        return False

    def _updateHandleList(self):
        """        
        Updates the list of handles (self.handles) 
        @see: self.editStructure
        @see: DnaSegment_GraphicsMode._drawHandles()
        """        
        # note: if handlePoint1 and/or handlePoint2 can change more often than 
        # this runs, we'll need to rerun the two assignments above whenever they
        # change and before the handle is drawn. An easy way would be to rerun
        # these assignments in the draw method of our GM. [bruce 080128]
        self.handles = [] # guess, but seems like a good idea [bruce 080128]
        self.handles.append(self.leftHandle)
        self.handles.append(self.rightHandle)
    
    def updateHandlePositions(self):
        """
        Update handle positions
        """
        self.cylinderWidth = CYLINDER_WIDTH_DEFAULT_VALUE
        self.cylinderWidth2 = CYLINDER_WIDTH_DEFAULT_VALUE    
               
        if self.struct is not None and \
           self.struct.dad is self._parentDnaSegment:
                       
            #axis end atom positions
            axisEnd1, axisEnd2 = \
                self._parentDnaSegment.getAxisEndPoints()

            if axisEnd1 is not None and axisEnd2 is not None:
                # note: this condition was an attempt to fix traceback
                # when dna udpater is on. It didn't fix it, and is not necessary
                # for the real fix to work (default values of ORIGIN in the
                # State declarations). But it seems like a good idea anyway
                # so I will leave it in place. [bruce 080216]

                self.axisEnd1, self.axisEnd2 = axisEnd1, axisEnd2
                
                #List of *positions* of strand atoms connected to the axis end atoms.
                strandEndPoints = self._parentDnaSegment.getStrandEndPointsFor(self.struct)
                
                if len(strandEndPoints) != 2:
                    print_compact_stack("BUG in drawing handles: dna segment "\
                                        "probably doesn't have exactly two end"\
                                        " axis atoms: "
                                        )
                    return
                
                #Now comput the handle base positions. for Strand resize handles, 
                #the base position will lie midway between the axis end atom 
                #and corresponding strand end atom of the strand. 
                strandEnd1 = strandEndPoints[0]
                strandEnd2 = strandEndPoints[1]
                if strandEnd1 is not None:
                    v1 = strandEnd1 - self.axisEnd1
                    self.handlePoint1 = self.axisEnd1 + norm(v1)*vlen(v1)/2.0
                if strandEnd2 is not None:
                    v2 = strandEnd2 - self.axisEnd2
                    self.handlePoint2 = self.axisEnd2 + norm(v2)*vlen(v2)/2.0

    
    def modifyStructure(self):
        """
        TO BE MODIFIED POST DNA DATA MODEL IMPLEMENTATION.       
        
        @see: @see: B{DnaStrand_ResizeHandle.on_release} (the caller)
        @see: B{DnaSegment_EditCommand.modifystructure()} for comments
        @see: B{SelectChunks_GraphicsMode.leftUp} (which calls the 
              the relevent method in DragHandler API. )
        @see: B{exprs.DraggableHandle_AlongLine}, B{exprs.DragBehavior}
        @see: B{self.preview_or_finalize_structure }
        @see: B{self._modifyStructure}        
    
        """
        pass
        
