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
from utilities.debug import print_compact_stack
from utilities.constants import gensym
from utilities.constants import purple
from utilities.Comparison import same_vals

from geometry.VQT import  V
from geometry.VQT import  vlen
from geometry.VQT import  norm
from Numeric import dot

from prototype.test_connectWithState import State_preMixin
from exprs.attr_decl_macros import Instance, State
from exprs.__Symbols__ import _self
from exprs.Exprs import call_Expr
from exprs.Exprs import norm_Expr
from widgets.prefs_widgets import ObjAttr_StateRef
from exprs.ExprsConstants import Width, Point, ORIGIN, Color
from exprs.ExprsConstants import Vector

from model.chunk import Chunk
from model.chem import Atom
from model.bonds import Bond

from dna.commands.DnaStrand.DnaStrand_GraphicsMode import DnaStrand_GraphicsMode
from dna.commands.DnaStrand.DnaStrand_ResizeHandle import DnaStrand_ResizeHandle
from dna.model.Dna_Constants import getNumberOfBasePairsFromDuplexLength
from dna.model.Dna_Constants import getDuplexLength
from dna.commands.BuildDuplex.B_Dna_PAM3_SingleStrand import B_Dna_PAM3_SingleStrand

from command_support.EditCommand import EditCommand 

from utilities.constants import noop
from utilities.Comparison import same_vals



CYLINDER_WIDTH_DEFAULT_VALUE = 0.0
HANDLE_RADIUS_DEFAULT_VALUE = 1.3

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

    call_makeMenus_for_each_event = True 

    #Graphics Mode 
    GraphicsMode_class = DnaStrand_GraphicsMode

    #@see: self.updateHandlePositions for details on how these variables are 
    #used in computation. 
    #@see: DnaStrand_ResizeHandle and handle declaration in this class 
    #definition
    handlePoint1 = State( Point, ORIGIN)
    handlePoint2 = State( Point, ORIGIN)    
    
    handleDirection1 = State(Vector, ORIGIN)
    handleDirection2 = State(Vector, ORIGIN)
    
    #See self._update_resizeHandle_radius where this gets changed. 
    #also see DnaSegment_ResizeHandle to see how its implemented. 
    handleSphereRadius1 = State(Width, HANDLE_RADIUS_DEFAULT_VALUE)
    handleSphereRadius2 = State(Width, HANDLE_RADIUS_DEFAULT_VALUE)
    
    #handleColors 
    handleColor1 = State(Color, purple)
    handleColor2 = State(Color, purple)
    
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
            direction = handleDirection1,
            sphereRadius = handleSphereRadius1,
            handleColor = handleColor1
        ))
    
    
    rightHandle = Instance( 
        DnaStrand_ResizeHandle(
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth2'),
            origin = handlePoint2,
            fixedEndOfStructure = handlePoint1,
            direction = handleDirection2,
            sphereRadius = handleSphereRadius2,
            handleColor = handleColor2
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
                
        #This is used for comarison purpose in model_changed method to decide
        #whether to update the sequence. 
        self._previousNumberOfBases = None

    def init_gui(self):
        """
        Initialize gui. 
        """
        #@see DnaSegment_EditCommand.init_gui() for a detailed note. 
        #This command implements similar thing 
        self.create_and_or_show_PM_if_wanted(showPropMgr = False)
        
    def NOT_IMPELMENTED_model_changed(self):
        if self.hasValidStructure():
            new_numberOfBases = self.struct.getNumberOfBases()
            if not same_vals(new_numberOfBases, self._previousNumberOfBases):
                print "***new_numberOfBases = %d, self._previousNumberOfBases = %d"%(new_numberOfBases,
                                                                                     self._previousNumberOfBases)
                self.propMgr.updateSequence()
                self._previousNumberOfBases = new_numberOfBases
        
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that dna_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """
        
        bool_keep = EditCommand.keep_empty_group(self, group)
        
        if not bool_keep:     
            if self.hasValidStructure():                
                if group is self.struct:
                    bool_keep = True
                elif group is self.struct.parent_node_of_class(self.assy.DnaGroup):
                    bool_keep = True
        
        return bool_keep

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
        return self.propMgr.getParameters()

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
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        """        
        
        
        assert self.struct
        # parameters have changed, update existing structure
        self._revertNumber()


        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name

        self.dna = B_Dna_PAM3_SingleStrand()
            
        numberOfBases, \
                    dnaForm, \
                    dnaModel, \
                    basesPerTurn, \
                    duplexRise = params
        
        
        numberOfBasesToAddOrRemove =  self._determine_numberOfBases_to_change()
     
        if numberOfBasesToAddOrRemove != 0: 
            resizeEndStrandAtom, resizeEndAxisAtom = \
                           self.get_strand_and_axis_endAtoms_at_resize_end()
        
            if resizeEndAxisAtom:
                dnaSegment = resizeEndAxisAtom.molecule.parent_node_of_class(
                    self.assy.DnaSegment)
            
                resizeEnd_final_position = self._get_resizeEnd_final_position(
                    resizeEndAxisAtom, 
                    abs(numberOfBasesToAddOrRemove),
                    duplexRise )
                  
                self.dna.modify(dnaSegment, 
                                resizeEndAxisAtom,
                                numberOfBasesToAddOrRemove, 
                                basesPerTurn, 
                                duplexRise,
                                resizeEndAxisAtom.posn(),
                                resizeEnd_final_position,
                                resizeEndStrandAtom = resizeEndStrandAtom
                            )
                
        
        self.previousParams = params
                
        
        return  
    
    def _finalizeStructure(self):
        """
        Overrides EditCommand._finalizeStructure. 
        @see: EditCommand.preview_or_finalize_structure
        """     
        if self.struct is not None:
            #@TODO 2008-03-19:Should we always do this even when strand sequence
            #is not changed?? Should it waste time in comparing the current 
            #sequence with a previous one? Assigning sequence while leaving the 
            #command will be slow for large files.Need to be optimized if 
            #problematic.
            #What if a flag is set in self.propMgr.updateSequence() when it 
            #updates the seq for the second time and we check that here. 
            #Thats  not good if the method gets called multiple times for some 
            #reason other than the user entered sequence. So not doing here. 
            #Better fix would be to check if sequence gets changed (textChanged)
            #in DnaSequence editor class .... Need to be revised
            EditCommand._finalizeStructure(self) 
            self._updateStrandSequence_if_needed()
            self.assignStrandSequence()
            
    def _previewStructure(self):        
        EditCommand._previewStructure(self)
        self.updateHandlePositions()
        self._updateStrandSequence_if_needed()
  
    def _updateStrandSequence_if_needed(self):
        if self.hasValidStructure():
            new_numberOfBases = self.struct.getNumberOfBases()
            if not same_vals(new_numberOfBases, self._previousNumberOfBases):
                self.propMgr.updateSequence()
                self._previousNumberOfBases = new_numberOfBases    
    
    def _get_resizeEnd_final_position(self, 
                                      resizeEndAxisAtom, 
                                      numberOfBases, 
                                      duplexRise):
        
        final_position = None   
        if self.grabbedHandle:
            final_position = self.grabbedHandle.currentPosition
        else:
            dnaSegment = resizeEndAxisAtom.molecule.parent_node_of_class(self.assy.DnaSegment)
            other_axisEndAtom = dnaSegment.getOtherAxisEndAtom(resizeEndAxisAtom)
            axis_vector = resizeEndAxisAtom.posn() - other_axisEndAtom.posn()
            segment_length_to_add = getDuplexLength('B-DNA', 
                                                    numberOfBases, 
                                                    duplexRise = duplexRise)
            
            final_position = ladderEndAxisAtom.posn() + norm(axis_vector)*segment_length_to_add
            
        return final_position
                

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
            
    def assignStrandSequence(self):
        """
        Assigns the sequence typed in the sequence editor text field to 
        the selected strand chunk. The method it invokes also assigns 
        a complimentary sequence to the mate strand.
        @see: Chunk.setStrandSequence
        """
        sequenceString = self.propMgr.sequenceEditor.getPlainSequence()
        sequenceString = str(sequenceString)       
        self.struct.setStrandSequence(sequenceString) 
        

    def editStructure(self, struct = None):
        """
        Edit the structure 
        @param struct: structure to be edited (in this case its a strand chunk)
        @type struct: chunk or None (this will change post dna data model)
        """
        EditCommand.editStructure(self, struct)        
        if self.hasValidStructure():
            self._previousNumberOfBases = self.struct.getNumberOfBases()
            self.propMgr.numberOfBasesSpinBox.setValue(self._previousNumberOfBases)
            
            #TO BE REVISED post dna data model - 2008-02-14
            if isinstance(self.struct.dad , self.assy.DnaSegment):
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

        if isinstance(self.struct, self.assy.DnaStrand):
            return True
        elif isinstance(self.struct, Chunk) and self.struct.isStrandChunk(): 
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
        
        # Set handlePoints (i.e. their origins) and the handle directions to 
        # None. The GraphicsMode checks if the handles ahve valid placement 
        # attributes set before drawing it.
        # For example, if the one of the strand end atoms is NOT at a 
        # 'DnaSegment end' , then the handlePoint of the handle at that end will
        # remain 'None' as a result.
        self.handlePoint1 = None
        self.handlePoint2 = None        
        self.handleDirection1 = None
        self.handleDirection2 = None
        
        axisAtom1 = None
        axisAtom2 = None
        strandEndBaseAtom1 = None
        strandEndBaseAtom2 = None  
        
        #It could happen (baecause of bugs) that standEndBaseAtom1 and 
        #strandEndBaseAtom2 are one and the same! i.e strand end atom is 
        #not bonded. If this happens, we should throw a traceback bug 
        #exit gracefully. The possible cause of this bug may be ---
        #(just an example): For some reason, the modify code is unable to 
        #determine the correct bond direction of the resized structure
        #and therefore, while fusing the original strand with the new one created
        #by DnaDuplex.modify, it is unable to find bondable pairs! 
        # [- Ninad 2008-03-31]
        strandEndBaseAtom1, strandEndBaseAtom2 = self.struct.get_strand_end_base_atoms()
        if strandEndBaseAtom1 is strandEndBaseAtom2:
            print_compact_stack("bug in updating handle positions, some resized DnaStrand " \
                                "has only one atom")
            return
        
        if strandEndBaseAtom1:
            axisAtom1 = self.struct.get_DnaSegment_axisEndAtom_connected_to(strandEndBaseAtom1)
            if axisAtom1:
                self.handleDirection1 = self._get_handle_direction(axisAtom1, 
                                                                   strandEndBaseAtom1)
                
                self.handlePoint1 = axisAtom1.posn()
                #Alternate implementation --
                #Position the handle midway between the axis and strand atoms
                if 0:
                    v1 = strandEndBaseAtom1.posn() - axisAtom1.posn()
                    self.handlePoint1 = axisAtom1.posn() + v1/2.0
                
        if strandEndBaseAtom2:
            axisAtom2 = self.struct.get_DnaSegment_axisEndAtom_connected_to(
                strandEndBaseAtom2)
            
            if axisAtom2:
                self.handleDirection2 = self._get_handle_direction(axisAtom2, 
                                                                   strandEndBaseAtom2)
                self.handlePoint2 = axisAtom2.posn()
                #Alternate implementation --
                #Position the handle midway between the axis and strand atoms
                if 0:
                    v2 = strandEndBaseAtom2.posn() - axisAtom2.posn()
                    self.handlePoint2 = axisAtom2.posn() + v2/2.0
        
        
        #update the radius of resize handle 
        self._update_resizeHandle_radius(axisAtom1, axisAtom2)
        
        #update the display color of the handles
        self._update_resizeHandle_color(strandEndBaseAtom1, strandEndBaseAtom2)
        
    def _update_resizeHandle_radius(self, axisAtom1, axisAtom2):
        """
        Finds out the sphere radius to use for the resize handles, based on 
        atom /chunk or glpane display (whichever decides the display of the end 
        atoms.  The default  value is 1.2.


        @see: self.updateHandlePositions()
        @see: B{Atom.drawing_radius()}
        """               
                          
        if axisAtom1 is not None:
            self.handleSphereRadius1 = max(1.005*axisAtom1.drawing_radius(), 
                                           1.005*HANDLE_RADIUS_DEFAULT_VALUE)
        if axisAtom2 is not None: 
            self.handleSphereRadius2 =  max(1.005*axisAtom2.drawing_radius(), 
                                           1.005*HANDLE_RADIUS_DEFAULT_VALUE) 
            
    def _update_resizeHandle_color(self, 
                                   strandEndBaseAtom1, 
                                   strandEndBaseAtom2):
        """
        Update the color of resize handles using the current color 
        of the *chunk* of the corresponding strand end atoms. 
        @Note: If no specific color is set to the chunk, it uses 'purple' as
        the default color (and doesn't use the atom.element.color) . This 
        can be changed if needed.
        """
        if strandEndBaseAtom1 is not None:
            color = strandEndBaseAtom1.molecule.color 
            if color: 
                self.handleColor1 = color
                                
        if strandEndBaseAtom2 is not None:
            color = strandEndBaseAtom2.molecule.color 
            if color: 
                self.handleColor2 = color
           
    def _get_handle_direction(self, axisAtom, strandAtom):
        """
        Get the handle direction.
        """
        
        handle_direction = None
                        
        strand_rail = strandAtom.molecule.get_ladder_rail() 
        
        for bond_direction in (1, -1):
            next_strand_atom = strandAtom.strand_next_baseatom(bond_direction)
            if next_strand_atom:
                break
        
        if next_strand_atom:
            next_axis_atom = next_strand_atom.axis_neighbor()
            if next_axis_atom:
                handle_direction = norm(axisAtom.posn() - next_axis_atom.posn())
                
        return handle_direction
    
    def getDnaRibbonParams(self):
        """
        Returns parameters for drawing the dna ribbon. 
        
        If the dna rubberband line should NOT be drawn (example when you are 
        removing bases from the strand or  if its unable to get dnaSegment) , 
        it retuns None. So the caller should check if the method return value
        is not None. 
        @see: DnaStrand_GraphicsMode._draw_handles()
        """
        
        if self.grabbedHandle is None:
            return None
        
        if self.grabbedHandle.origin is None:
            return None
        
        direction_of_drag = norm(self.grabbedHandle.currentPosition - \
                                 self.grabbedHandle.origin)
        
        #If the strand bases are being removed (determined by checking the 
        #direction of drag) , no need to draw the rubberband line. 
        if dot(self.grabbedHandle.direction, direction_of_drag) < 0:
            return None
        
        strandEndAtom, axisEndAtom = self.get_strand_and_axis_endAtoms_at_resize_end()
        
        #DnaStrand.get_DnaSegment_with_content_atom saely handles the case where
        #strandEndAtom is None. 
        dnaSegment = self.struct.get_DnaSegment_with_content_atom(strandEndAtom)
        
        if dnaSegment:     
            basesPerTurn = dnaSegment.getBasesPerTurn()
            duplexRise = dnaSegment.getDuplexRise()        
            ribbon1_start_point = strandEndAtom.posn()
            
            ribbon1Color = strandEndAtom.molecule.color
            if not ribbon1Color:
                ribbon1Color = strandEndAtom.element.color
        
            return (self.grabbedHandle.origin,
                    self.grabbedHandle.currentPosition,
                    basesPerTurn, 
                    duplexRise, 
                    ribbon1_start_point,
                    ribbon1Color
                )
        
        return None
             
    
    
    def get_strand_and_axis_endAtoms_at_resize_end(self):
        resizeEndStrandAtom = None        
        resizeEndAxisAtom = None
        
        strandEndAtom1, strandEndAtom2 = self.struct.get_strand_end_base_atoms()
        
        if self.grabbedHandle is not None:
            for atm in (strandEndAtom1, strandEndAtom2):
                axisEndAtom = self.struct.get_DnaSegment_axisEndAtom_connected_to(atm)
                if axisEndAtom:
                    if same_vals(axisEndAtom.posn(), self.grabbedHandle.origin):
                        resizeEndStrandAtom = atm
                        resizeEndAxisAtom = axisEndAtom
                        
        
        return (resizeEndStrandAtom, resizeEndAxisAtom)
    
     

    def modifyStructure(self):
        """
        
        Called when a resize handle is dragged to change the length of the 
        segment. (Called upon leftUp) . This method assigns the new parameters 
        for the segment after it is resized and calls 
        preview_or_finalize_structure which does the rest of the job. 
        Note that Client should call this public method and should never call
        the private method self._modifyStructure. self._modifyStructure is 
        called only by self.preview_or_finalize_structure

        @see: B{DnaStrand_ResizeHandle.on_release} (the caller)
        @see: B{SelectChunks_GraphicsMode.leftUp} (which calls the 
              the relevent method in DragHandler API. )
        @see: B{exprs.DraggableHandle_AlongLine}, B{exprs.DragBehavior}
        @see: B{self.preview_or_finalize_structure }
        @see: B{self._modifyStructure}         
        """
        #TODO: need to cleanup this and may be use use something like
        #self.previousParams = params in the end -- 2008-03-24 (midnight)
           
        
        if self.grabbedHandle is None:
            return   
        
        #TODO: Important note: How does NE1 know that structure is modified? 
        #Because number of base pairs parameter in the PropMgr changes as you 
        #drag the handle . This is done in self.getCursorText() ... not the 
        #right place to do it. OR that method needs to be renamed to reflect
        #this as suggested in that method -- Ninad 2008-03-25        
        self.preview_or_finalize_structure(previewing = True) 
        
        self.glpane.gl_update()
    
    def update_numberOfBases(self):
        if self.grabbedHandle is None:
            return
                
        currentPosition = self.grabbedHandle.currentPosition
        resize_end = self.grabbedHandle.origin
        
        new_duplexLength = vlen( currentPosition - resize_end )
                        
        numberOfBasePairs_to_change = getNumberOfBasePairsFromDuplexLength('B-DNA', 
                                                              new_duplexLength)
        
        original_numberOfBases = self.struct.getNumberOfBases()
        #If the dot product of handle direction and the direction in which it 
        #is dragged is negative, this means we need to subtract bases
        direction_of_drag = norm(currentPosition - resize_end)
        if dot(self.grabbedHandle.direction, direction_of_drag ) < 0:
            total_number_of_bases = original_numberOfBases - numberOfBasePairs_to_change
            self.propMgr.numberOfBasesSpinBox.setValue(total_number_of_bases)
        else:
            total_number_of_bases = original_numberOfBases + numberOfBasePairs_to_change
            self.propMgr.numberOfBasesSpinBox.setValue(total_number_of_bases - 1)
                    
        
    def _determine_numberOfBases_to_change(self):
        """
        """       
        #The Property manager will be showing the current number 
        #of base pairs (w. May be we can use that number directly here? 
        #The following is  safer to do so lets just recompute the 
        #number of base pairs. (if it turns out to be slow, we will consider
        #using the already computed calue from the property manager
        
        original_numberOfBases = self.struct.getNumberOfBases()
       
        numberOfBasesToAddOrRemove = self.propMgr.numberOfBasesSpinBox.value()\
                                   - original_numberOfBases 
        
        if numberOfBasesToAddOrRemove > 0:
            #dna.modify will remove the first base pair it creates 
            #(that basepair will only be used for proper alignment of the 
            #duplex with the existing structure) So we need to compensate for
            #this basepair by adding 1 to the new number of base pairs. 
            numberOfBasesToAddOrRemove += 1

                               
        return numberOfBasesToAddOrRemove
    

    def makeMenus(self): 
        """
        Create context menu for this command. (Build Dna mode)
        """
        if not hasattr(self, 'graphicsMode'):
            return

        selobj = self.glpane.selobj

        if selobj is None:
            return

        self.Menu_spec = []

        highlightedChunk = None
        if isinstance(selobj, Chunk):
            highlightedChunk = selobj
        if isinstance(selobj, Atom):
            highlightedChunk = selobj.molecule
        elif isinstance(selobj, Bond):
            chunk1 = selobj.atom1.molecule
            chunk2 = selobj.atom2.molecule
            if chunk1 is chunk2 and chunk1 is not None:
                highlightedChunk = chunk1

        if highlightedChunk is None:
            return

        if self.hasValidStructure():
            if (self.struct is highlightedChunk) or \
               (self.struct is highlightedChunk.parent_node_of_class(
                   self.assy.DnaStrand)):
                item = (("Currently editing %r"%self.struct.name), 
                        noop, 'disabled')
                self.Menu_spec.append(item)
                return	 
            #following should be self.struct.getDnaGroup or self.struct.getDnaGroup
            #need to formalize method name and then make change.
            dnaGroup = self.struct.parent_node_of_class(self.assy.DnaGroup)
            if dnaGroup is None:
                return            
            if not dnaGroup is highlightedChunk.parent_node_of_class(self.assy.DnaGroup):                
                item = ("Edit unavailable: Member of a different DnaGroup",
                        noop, 'disabled')
                self.Menu_spec.append(item)
                return

        highlightedChunk.make_glpane_context_menu_items(self.Menu_spec,
                                                 command = self)

