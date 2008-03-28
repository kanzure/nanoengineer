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

from geometry.VQT import  V
from geometry.VQT import  vlen
from geometry.VQT import  norm

from prototype.test_connectWithState import State_preMixin
from exprs.attr_decl_macros import Instance, State
from exprs.__Symbols__ import _self
from exprs.Exprs import call_Expr
from exprs.Exprs import norm_Expr
from widgets.prefs_widgets import ObjAttr_StateRef
from exprs.ExprsConstants import Width, Point, ORIGIN
from exprs.ExprsConstants import Vector

from model.chunk import Chunk
from model.chem import Atom
from model.bonds import Bond

from dna.commands.DnaStrand.DnaStrand_GraphicsMode import DnaStrand_GraphicsMode
from dna.commands.DnaStrand.DnaStrand_ResizeHandle import DnaStrand_ResizeHandle

from command_support.EditCommand import EditCommand 

from utilities.constants import noop

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
            direction = handleDirection1
        ))

    rightHandle = Instance( 
        DnaStrand_ResizeHandle(
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth2'),
            origin = handlePoint2,
            fixedEndOfStructure = handlePoint1,
            direction = handleDirection2
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
            #What if a flag is set in self.propMgr_updateSequence() when it 
            #updates the seq for the second time and we check that here. 
            #Thats  not good if the method gets called multiple times for some 
            #reason other than the user entered sequence. So not doing here. 
            #Better fix would be to check if sequence gets changed (textChanged)
            #in DnaSequence editor class .... Need to be revised
            self.assignStrandSequence()
            EditCommand._finalizeStructure(self) 
                

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
        
        self.handlePoint1 = None
        self.handlePoint2 = None
        self.handleDirection1 = ORIGIN
        self.handleDirection2 = ORIGIN
        
        strandEndBaseAtom1, strandEndBaseAtom2 = self.struct.get_strand_end_base_atoms()
        
        if strandEndBaseAtom1 is not None:
            axisAtom1 = strandEndBaseAtom1.axis_neighbor()
            if axisAtom1 is not None:
                self.handleDirection1 = self._get_handle_direction(axisAtom1, 
                                                                   strandEndBaseAtom1)
                v1 = strandEndBaseAtom1.posn() - axisAtom1.posn()
                self.handlePoint1 = axisAtom1.posn() + v1/2.0
                
        if strandEndBaseAtom2 is not None:
            axisAtom2 = strandEndBaseAtom2.axis_neighbor()
            if axisAtom2 is not None:
                self.handleDirection2 = self._get_handle_direction(axisAtom2, 
                                                                   strandEndBaseAtom2)
                v2 = strandEndBaseAtom2.posn() - axisAtom2.posn()
                self.handlePoint2 = axisAtom2.posn() + v2/2.0
  
           
        ##if strandEnd1 is not None:
            ##v1 = strandEnd1 - self.axisEnd1
            ##self.handlePoint1 = self.axisEnd1 + norm(v1)*vlen(v1)/2.0
        ##if strandEnd2 is not None:
            ##v2 = strandEnd2 - self.axisEnd2
            ##self.handlePoint2 = self.axisEnd2 + norm(v2)*vlen(v2)/2.0
            
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

