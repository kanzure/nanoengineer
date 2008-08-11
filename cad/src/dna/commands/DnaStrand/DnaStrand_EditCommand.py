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
import foundation.env as env
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
from utilities.constants import red, black

from utilities.Comparison import same_vals

from utilities.prefs_constants import dnaStrandEditCommand_cursorTextCheckBox_changedBases_prefs_key
from utilities.prefs_constants import dnaStrandEditCommand_cursorTextCheckBox_numberOfBases_prefs_key
from utilities.prefs_constants import dnaStrandEditCommand_showCursorTextCheckBox_prefs_key

CYLINDER_WIDTH_DEFAULT_VALUE = 0.0
HANDLE_RADIUS_DEFAULT_VALUE = 1.5

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
    prefix           =  'Strand '   # used for gensym
    cmdname          = "DNA_STRAND"
    
    commandName       = 'DNA_STRAND'
    featurename       = "Edit Dna Strand"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_DNA'

    command_should_resume_prevMode = True
    command_has_its_own_PM = True
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

    def command_enter_PM(self):
        """
        See superclass dor documentation.
        """
        #@see DnaSegment_EditCommand.init_gui() for a detailed note. 
        #This command implements similar thing 
        self.create_and_or_show_PM_if_wanted(showPropMgr = False)

    def model_changed(self):
        #This MAY HAVE BUG. WHEN --
        #debug pref 'call model_changed only when needed' is ON
        #See related bug 2729 for details. 

        #The following code that updates te handle positions and the strand 
        #sequence fixes bugs like 2745 and updating the handle positions
        #updating handle positions in model_changed instead of in 
        #self.graphicsMode._draw_handles() is also a minor optimization
        #This can be further optimized by debug pref 
        #'call model_changed only when needed' but its NOT done because of an 
        # issue menitoned in bug 2729   - Ninad 2008-04-07    

        EditCommand.model_changed(self) #This also calls the 
                                        #propMgr.model_changed 

        if self.grabbedHandle is not None:
            return

        #For Rattlesnake, PAM5 segment resizing  is not supported. 
        #@see: self.hasResizableStructure()        
        if self.hasValidStructure():
            isStructResizable, why_not = self.hasResizableStructure()
            if not isStructResizable:
                self.handles = []
                return
            elif len(self.handles) == 0:
                self._updateHandleList()

            self.updateHandlePositions()
            #NOTE: The following also updates self._previousParams
            self._updateStrandSequence_if_needed()


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
        Return the parameters from the property manager UI. Delegates this to
        self.propMgr
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

        #It could happen that the self.struct is killed before this method 
        #is called. For example: Enter Edit Dna strand, select the strand, hit 
        #delete and then hit Done to exit strand edit. Whenever you hit Done, 
        #modify structure gets called (if old params don't match new ones) 
        #so it needs to return safely if the structure was not valid due
        #to some previous operation 
        if not self.hasValidStructure():
            return 
        
        # parameters have changed, update existing structure
        self._revertNumber()


        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix, self.assy) # (in _build_struct)
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
                     color_junk = params
        #see a note about color_junk in DnaSegment_EditCommand._modifyStructure()


        numberOfBasesToAddOrRemove =  self._determine_numberOfBases_to_change()

        if numberOfBasesToAddOrRemove != 0: 
            resizeEndStrandAtom, resizeEndAxisAtom = \
                               self.get_strand_and_axis_endAtoms_at_resize_end()

            if resizeEndAxisAtom:
                dnaSegment = resizeEndAxisAtom.molecule.parent_node_of_class(
                    self.assy.DnaSegment)
                
                if dnaSegment:
                    #A DnaStrand can have multiple DNA Segments with different 
                    #basesPerTurn and duplexRise so make sure that while 
                    #resizing the strand, use the dna segment of the 
                    #resizeEndAxisAtom. Fixes bug 2922 - Ninad 2008-08-04
                    basesPerTurn = dnaSegment.getBasesPerTurn()                
                    duplexRise = dnaSegment.getDuplexRise() 
                                            
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
                                    resizeEndStrandAtom = resizeEndStrandAtom )                        

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

            #@TODO Update self._previousParams again? 
            #This NEEDS TO BE REVISED. BUG MENTIONED BELOW----
            #we already update this in EditCommand class. But, it doesn't work for 
            #the following bug -- 1. create a duplex with 5 basepairs, 2. resize 
            #red strand to 2 bases. 3. Undo 4. Redo 5. Try to resize it again to 
            #2 bases -- it doesn't work because self.previousParams stil stores 
            #bases as 2 and thinks nothing got changed! Can we declare 
            #self._previewStructure as a undiable state? Or better self._previousParams
            #should store self.struct and should check method return value 
            #like self.struct.getNumberOfBases()--Ninad 2008-04-07
            if self.previousParams is not None:
                if new_numberOfBases != self.previousParams[0]:
                    self.propMgr.numberOfBasesSpinBox.setValue(new_numberOfBases)
                    self.previousParams = self._gatherParameters()
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

            final_position = resizeEndAxisAtom.posn() + norm(axis_vector)*segment_length_to_add

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
        if not self.hasValidStructure(): 
            #Fixes bug 2923            
            return
        
        sequenceString = self.propMgr.sequenceEditor.getPlainSequence()
        sequenceString = str(sequenceString)     
        
        #assign strand sequence only if it not the same as the current sequence
        seq = self.struct.getStrandSequence()
        
        if seq != sequenceString:
            self.struct.setStrandSequence(sequenceString) 


    def editStructure(self, struct = None):
        """
        Edit the structure 
        @param struct: structure to be edited (in this case its a strand chunk)
        @type struct: chunk or None (this will change post dna data model)
        """
        EditCommand.editStructure(self, struct)        
        if self.hasValidStructure():
            self._updatePropMgrParams()            

            #TO BE REVISED post dna data model - 2008-02-14
            if isinstance(self.struct.dad , self.assy.DnaSegment):
                self._parentDnaSegment = self.struct.dad   

            #For Rattlesnake, we do not support resizing of PAM5 model. 
            #So don't append the exprs handles to the handle list (and thus 
            #don't draw those handles. See self.model_changed() 
            isStructResizable, why_not = self.hasResizableStructure()
            if not isStructResizable:
                self.handles = []
            else:
                self._updateHandleList()
                self.updateHandlePositions()
                
    def _updatePropMgrParams(self):
        """
        Subclasses may override this method. 
        Update some property manager parameters with the parameters of
        self.struct (which is being edited)
        @see: self.editStructure()
        """

        #Format in which params need to be provided to the Property manager
        
                #numberOfBases, 
                #dnaForm,
                #dnaModel,
                #color

        self._previousNumberOfBases = self.struct.getNumberOfBases()
        numberOfBases = self._previousNumberOfBases        
        color = self.struct.getColor()

        params_for_propMgr = ( numberOfBases,
                               None, 
                               None,                          
                               color )


        #TODO 2008-03-25: better to get all parameters from self.struct and
        #set it in propMgr?  This will mostly work except that reverse is 
        #not true. i.e. we can not specify same set of params for 
        #self.struct.setProps ...because endPoint1 and endPoint2 are derived.
        #by the structure when needed. Commenting out following line of code
        #UPDATE 2008-05-06 Fixes a bug due to which the parameters in propMGr
        #of DnaSegment_EditCommand are not same as the original structure
        #(e.g. bases per turn and duplexrise)
        self.propMgr.setParameters(params_for_propMgr)
        


    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return self.win.assy.DnaStrand
    
    def updateSequence(self):
        """
        Public method provided for convenience. If any callers outside of this 
        command need to update the sequence in the sequence editor, they can simply 
        do currentCommand.updateSequence() rather than 
        currentCommand.propMgr.updateSequence()
        @see: DnaStrand_ProprtyManager.updateSequence() which does the actual 
        job of updating the sequence string in the sequence editor.
        """
        if self.propMgr is not None:
            self.propMgr.updateSequence()


    def hasResizableStructure(self):
        """
        For Rattlesnake release, we dont support strand resizing for PAM5 
        models. If the structure is not resizable, the handles won't be drawn
        @see:self.model_changed()
        @see:DnaStrand_PropertyManager.model_changed()
        @see: self.editStructure()
        @see: DnaSegment.is_PAM3_DnaStrand()
        """
        #Note: This method fixes bugs similar to (and including) bug 2812 but 
        #the changes didn't made it to Rattlesnake rc2 -- Ninad 2008-04-16
        isResizable = True
        why_not = ''

        if not self.hasValidStructure():
            isResizable = False
            why_not     = 'It is invalid.'
            return isResizable, why_not        

        isResizable = self.struct.is_PAM3_DnaStrand()

        if not isResizable:
            why_not = 'It needs to be converted to PAM3 model.'
            return isResizable, why_not

        #The following fixes bug 2812
        strandEndBaseAtom1, strandEndBaseAtom2 = self.struct.get_strand_end_base_atoms()

        if strandEndBaseAtom1 is strandEndBaseAtom2:
            isResizable = False
            why_not = "It is probably a \'closed loop\'."
            return isResizable, why_not


        return True, ''


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
        if len(self.handles) == 0:
            #No handles are appended to self.handles list. 
            #@See self.model_changed() and self._updateHandleList()
            return

        self.cylinderWidth = CYLINDER_WIDTH_DEFAULT_VALUE
        self.cylinderWidth2 = CYLINDER_WIDTH_DEFAULT_VALUE 

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
            axisAtom1 = strandEndBaseAtom1.axis_neighbor()
            if axisAtom1:
                self.handleDirection1 = self._get_handle_direction(axisAtom1, 
                                                                   strandEndBaseAtom1)                
                self.handlePoint1 = axisAtom1.posn()                

        if strandEndBaseAtom2:
            axisAtom2 = strandEndBaseAtom2.axis_neighbor()

            if axisAtom2:
                self.handleDirection2 = self._get_handle_direction(axisAtom2, 
                                                                   strandEndBaseAtom2)
                self.handlePoint2 = axisAtom2.posn()   


        # UPDATE 2008-04-15:
        # Before 2008-04-15 the state attrs for exprs handles were always reset to None
        #at the beginning of the method. But it is calling model_changed signal
        #recursively. (se also bug 2729) So, reset thos state attrs only when 
        #needed  -- Ninad  [ this fix was not in RattleSnake rc1] 

        # Set handlePoints (i.e. their origins) and the handle directions to 
        # None if the atoms used to compute these state attrs are missing. 
        # The GraphicsMode checks if the handles have valid placement 
        # attributes set before drawing it.    

        if strandEndBaseAtom1 is None and strandEndBaseAtom2 is None:
            #probably a ring
            self.handles = []


        if strandEndBaseAtom1 is None or axisAtom1 is None:            
            self.handleDirection1 = None
            self.handlePoint1 = None

        if strandEndBaseAtom2 is None or axisAtom2 is None:            
            self.handleDirection2 = None
            self.handlePoint2 = None

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

        ribbon1_direction = None

        if dnaSegment:     
            basesPerTurn = dnaSegment.getBasesPerTurn()
            duplexRise = dnaSegment.getDuplexRise()        
            ribbon1_start_point = strandEndAtom.posn()

            if strandEndAtom:
                ribbon1_start_point = strandEndAtom.posn()
                for bond_direction, neighbor in strandEndAtom.bond_directions_to_neighbors():
                    if neighbor and neighbor.is_singlet():
                        ribbon1_direction = bond_direction
                        break

            ribbon1Color = strandEndAtom.molecule.color
            if not ribbon1Color:
                ribbon1Color = strandEndAtom.element.color

            return (self.grabbedHandle.origin,
                    self.grabbedHandle.currentPosition,
                    basesPerTurn, 
                    duplexRise, 
                    ribbon1_start_point,
                    ribbon1_direction,
                    ribbon1Color
                )

        return None



    def get_strand_and_axis_endAtoms_at_resize_end(self):
        resizeEndStrandAtom = None        
        resizeEndAxisAtom = None

        strandEndAtom1, strandEndAtom2 = self.struct.get_strand_end_base_atoms()

        if self.grabbedHandle is not None:
            for atm in (strandEndAtom1, strandEndAtom2):
                axisEndAtom = atm.axis_neighbor()
                if axisEndAtom:
                    if same_vals(axisEndAtom.posn(), self.grabbedHandle.origin):
                        resizeEndStrandAtom = atm
                        resizeEndAxisAtom = axisEndAtom


        return (resizeEndStrandAtom, resizeEndAxisAtom)


    def getCursorText(self):
        """
        Used by DnaStrand_GraphicsMode._draw_handles()
        @TODO: It also updates the number of bases
        """
        if self.grabbedHandle is None:
            return

        #@TODO: This updates the PM as the cursor moves. 
        #Need to rename this method so that you that it also does more things 
        #than just to return a textString. Even better if its called in 
        #self.model_changed but at the moment there is a bug thats why we 
        #are doing this update by calling getCursorText in the 
        #GraphicscMode._draw_handles-- Ninad 2008-04-05
        self.update_numberOfBases()
        
        if not env.prefs[dnaStrandEditCommand_showCursorTextCheckBox_prefs_key]:
            return '', black


        #Note: for Rattlesnake rc2, the text color is green when bases are added
        #, red when subtracted black when no change. But this implementation is 
        #changed based on Mark's user experience. The text is now always shown
        #in black color. -- Ninad 2008-04-17
        textColor = black     

        text = ""  
        
        numberOfBases = self.propMgr.numberOfBasesSpinBox.value()
        
        numberOfBasesString = self._getCursorText_numberOfBases(
            numberOfBases)
        
        changedBases = self._getCursorText_changedBases(
            numberOfBases)
        
        text = numberOfBasesString 
        
        if text and changedBases:
            text += " " # Removed comma. Mark 2008-07-03
        
        text += changedBases                   

        return (text , textColor)
    
    def _getCursorText_numberOfBases(self, numberOfBases):
        """
        Return the cursor textstring that gives information about the number 
        of bases if the corresponding prefs_key returns True.
        """
        numberOfBasesString = ''

        if env.prefs[
            dnaStrandEditCommand_cursorTextCheckBox_numberOfBases_prefs_key]:
            numberOfBasesString = "%db"%numberOfBases

        return numberOfBasesString

    def _getCursorText_changedBases(self, numberOfBases):
        """
        @see: self.getCursorText()
        """
        changedBasesString = ''

        if env.prefs[
            dnaStrandEditCommand_cursorTextCheckBox_changedBases_prefs_key]:
            
            original_numberOfBases = self.struct.getNumberOfBases()
            changed_bases = numberOfBases - original_numberOfBases            

            if changed_bases > 0:
                changedBasesString = "(" + "+" + str(changed_bases) + ")"
            else:
                changedBasesString = "(" + str(changed_bases) + ")"

        return changedBasesString


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
        """
        Updates the numberOfBases in the PM while a resize handle is being 
        dragged. 
        @see: self.getCursorText() where it is called. 
        """
        #@Note: originally (before 2008-04-05, it was called in 
        #DnaStrand_ResizeHandle.on_drag() but that 'may' have some bugs 
        #(not verified) also see self.getCursorText() to know why it is
        #called there (basically a workaround for bug 2729
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

