# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
MultipleDnaSegmentResize_EditCommand provides a way to edit (resize) one or more 
DnaSegments. To resize segments, select the segments you want to resize, 
highlight the axis of any one (in the default command), right click  and select 
'Resize DnaSegments' from the context menu to enter this command. Then you can 
interactively modify the segment list using the Property Manager
and use the resize handles to resize all segments at once. 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-05-09 - 2008-05-14 Created / modified.

"""
from Numeric import dot
from geometry.VQT import V, norm, vlen
from utilities.constants import applegreen

from dna.commands.DnaSegment.DnaSegment_EditCommand import DnaSegment_EditCommand
from dna.commands.MultipleDnaSegmentResize.MultipleDnaSegmentResize_GraphicsMode import MultipleDnaSegmentResize_GraphicsMode

from dna.model.Dna_Constants    import getDuplexLength 
from dna.model.Dna_Constants    import getNumberOfBasePairsFromDuplexLength

from dna.generators.B_Dna_PAM3_Generator import B_Dna_PAM3_Generator

from exprs.attr_decl_macros import Instance, State
from exprs.__Symbols__      import _self
from exprs.Exprs            import call_Expr
from exprs.Exprs            import norm_Expr
from exprs.ExprsConstants   import Width, Point
from widgets.prefs_widgets  import ObjAttr_StateRef

from dna.commands.DnaSegment.DnaSegment_ResizeHandle import DnaSegment_ResizeHandle
from utilities.debug import print_compact_stack
from dna.command_support.DnaSegmentList import DnaSegmentList
from dna.commands.MultipleDnaSegmentResize.MultipleDnaSegmentResize_PropertyManager import MultipleDnaSegmentResize_PropertyManager

CYLINDER_WIDTH_DEFAULT_VALUE = 0.0
HANDLE_RADIUS_DEFAULT_VALUE = 4.0
ORIGIN = V(0, 0, 0)


_superclass = DnaSegment_EditCommand
class MultipleDnaSegmentResize_EditCommand(DnaSegment_EditCommand):
    
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = "PARTIAL: 2008-09-05: may be some update code needs to be in methods like command_update_internal_state"
    
    #Graphics Mode 
    GraphicsMode_class = MultipleDnaSegmentResize_GraphicsMode
    
    #Property Manager
    PM_class = MultipleDnaSegmentResize_PropertyManager

    cmdname = 'MULTIPLE_DNA_SEGMENT_RESIZE' # REVIEW: needed? correct?

    commandName = 'MULTIPLE_DNA_SEGMENT_RESIZE'
    featurename = "Edit Multiple Dna Segments"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_DNA'

    #This command operates on (resizes) multiple DnaSegments at once. 
    #It does that by  looping through the DnaSegments and resizing them 
    #individually. self.currentStruct is set to the 'current' DnaSegment 
    #in that loop and then it is used in the resizing code. 
    #@see: DnaSegmentList class
    #@see: self.modifyStructure()
    currentStruct = None

    


    handlePoint1 = State( Point, ORIGIN)
    handlePoint2 = State( Point, ORIGIN)
    #The minimum 'stopper'length used for resize handles
    #@see: self._update_resizeHandle_stopper_length for details. 
    _resizeHandle_stopper_length = State(Width, -100000)

    rotationHandleBasePoint1 = State( Point, ORIGIN)
    rotationHandleBasePoint2 = State( Point, ORIGIN)

    #See self._update_resizeHandle_radius where this gets changed. 
    #also see DnaSegment_ResizeHandle to see how its implemented. 
    handleSphereRadius1 = State(Width, HANDLE_RADIUS_DEFAULT_VALUE)
    handleSphereRadius2 = State(Width, HANDLE_RADIUS_DEFAULT_VALUE)

    cylinderWidth = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE) 
    cylinderWidth2 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE) 


    #@TODO: modify the 'State params for rotation_distance 
    rotation_distance1 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE)
    rotation_distance2 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE)

    leftHandle = Instance(         
        DnaSegment_ResizeHandle(    
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth'),
            origin = handlePoint1,
            fixedEndOfStructure = handlePoint2,
            direction = norm_Expr(handlePoint1 - handlePoint2),
            sphereRadius = handleSphereRadius1, 
            range = (_resizeHandle_stopper_length, 10000)   
        ))

    rightHandle = Instance( 
        DnaSegment_ResizeHandle(
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth2'),
            origin = handlePoint2,
            fixedEndOfStructure = handlePoint1,
            direction = norm_Expr(handlePoint2 - handlePoint1),
            sphereRadius = handleSphereRadius2,
            range = (_resizeHandle_stopper_length, 10000)
        ))


    def _update_previousParams_in_model_changed(self):
        """
        Overrides superclass method. Does nothing in this class.
        @see: self.model_changed() which calls this method. 
        """
        pass

    def isAddSegmentsToolActive(self):
        """
        Returns True if the Add segments tool in the PM, that allows adding 
        dna segments from the resize segment list,  is active. 
        @see: MultipleDnaSegmentResize_GraphicsMode.chunkLeftUp()
        @see: MultipleDnaSegmentResize_GraphicsMode.end_selection_from_GLPane()
        @see: self.isRemoveSegmentsToolActive()
        @see: self.addSegmentToResizeSegmentList()
        """
        if self.propMgr is None:
            return False

        return self.propMgr.isAddSegmentsToolActive()

    def isRemoveSegmentsToolActive(self):
        """
        Returns True if the Remove Segments tool in the PM, that allows removing 
        dna segments from the resize segment list, is active. 
        @see: MultipleDnaSegmentResize_GraphicsMode.chunkLeftUp()
        @see: MultipleDnaSegmentResize_GraphicsMode.end_selection_from_GLPane()
        @see: self.isAddSegmentsToolActive()
        @see: self.removeSegmentFromResizeSegmentList()
        """
        if self.propMgr is None:
            return False

        return self.propMgr.isRemoveSegmentsToolActive()

    def addSegmentToResizeSegmentList(self, segment):
        """
        Adds the given segment to the resize segment list
        @param segment: The DnaSegment to be added to the resize segment list.
        Also does other things such as updating resize handles etc.
        @type sement: B{DnaSegment}
        @see: self.isAddSegmentsToolActive()
        """
        assert isinstance(segment, self.win.assy.DnaSegment)
        self.struct.addToStructList(segment)        


    def removeSegmentFromResizeSegmentList(self, segment):
        """
        Removes the given segment from the resize segment list
        @param segment: The DnaSegment to be removed from the resize segment 
        list. Also does other things such as updating resize handles etc.
        @type sement: B{DnaSegment}
        @see: self.isRemoveSegmentsToolActive()
        """
        assert isinstance(segment, self.win.assy.DnaSegment)
        self.struct.removeFromStructList(segment)   


    def setResizeStructList(self, structList):
        """
        Replaces the list of segments to be resized with the 
        given segmentList. Calls the related method of self.struct. 
        @param structList: New list of segments to be resized. 
        @type  structList: list
        @see: DnaSegmentList.setResizeStructList()
        """
        if self.hasValidStructure():
            self.struct.setStructList(structList)
            self.updateHandlePositions()

    def getResizeSegmentList(self):
        """
        Returns a list of segments to be resized at once. 
        @see: DnaSegmentList.getStructList()
        """
        if self.hasValidStructure():
            return self.struct.getStructList()
        return ()

    def updateResizeSegmentList(self):
        """
        Update the list of resize segments (maintained by self.struct)
        """
        if self.hasValidStructure():
            self.struct.updateStructList()


    def editStructure(self, struct = None):
        """
        Overrides superclass method. It first creates a B{DnaSegmentList} object
        using the provided list (struct argument) The DnaSegmentList object
        acts as self.struct. 
        @param struct: The caller of this method should provide a list of 
               containing all the structurs that need to be edited (resized) at 
               once. Caller also needs to make sure that this list contains 
               objects of class DnaSegment. 
        @type  struct: list
        @see: B{DnaSegmentList}
        """
        if isinstance(struct, list):
            dnaSegmentListObject = DnaSegmentList(self, 
                                                  structList = struct)  

        _superclass.editStructure(self, struct = dnaSegmentListObject)    

    def _updatePropMgrParams(self):
        """
        Subclasses may override this method. 
        Update some property manager parameters with the parameters of
        self.struct (which is being edited)
        @see: self.editStructure()
        @TODO: For multiple Dna segment resizing, this method does nothing as
           of 2008-05-14. Need to be revised.
        """

        #Commented out code as of 2008-05-14 ===========

        #endPoint1, endPoint2 = self.struct.getAxisEndPoints()
        #params_for_propMgr = (None,
                                #endPoint1, 
                                #endPoint2)

        ##TODO 2008-03-25: better to get all parameters from self.struct and
        ##set it in propMgr?  This will mostly work except that reverse is 
        ##not true. i.e. we can not specify same set of params for 
        ##self.struct.setProps ...because endPoint1 and endPoint2 are derived.
        ##by the structure when needed. Commenting out following line of code
        ##UPDATE 2008-05-06 Fixes a bug due to which the parameters in propMGr
        ##of DnaSegment_EditCommand are not same as the original structure
        ##(e.g. bases per turn and duplexrise)
        ###self.propMgr.setParameters(params_for_propMgr)

        pass

    def _update_resizeHandle_radius(self):
        """
        Finds out the sphere radius to use for the resize handles, based on 
        atom /chunk or glpane display (whichever decides the display of the end 
        atoms.  The default  value is 1.2.


        @see: self.updateHandlePositions()
        @see: B{Atom.drawing_radius()}
        @TODO: Refactor this. It does essentially same thing as the 
        superclass method. The problem is due to the use of the global constant
        HANDLE_RADIUS_DEFAULT_VALUE which needs to be different (bigger) in this
        class. So better to make it a class constant (need similar changes 
        in several commands. To be done in a refactoring project. 
        """
        atm1 , atm2 = self.struct.getAxisEndAtoms()                  
        if atm1 is not None:
            self.handleSphereRadius1 = max(1.005*atm1.drawing_radius(), 
                                           1.005*HANDLE_RADIUS_DEFAULT_VALUE)
        if atm2 is not None: 
            self.handleSphereRadius2 =  max(1.005*atm2.drawing_radius(), 
                                            1.005*HANDLE_RADIUS_DEFAULT_VALUE)


    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        """        

        if self.currentStruct is None:
            print_compact_stack("bug: self.currentStruct doesn't exist"\
                                "exiting self._modifyStructure")
            return

        assert isinstance(self.currentStruct , self.win.assy.DnaSegment)

        self.dna = B_Dna_PAM3_Generator()      

        duplexRise = self.currentStruct.getDuplexRise()

        basesPerTurn = self.currentStruct.getBasesPerTurn()

        numberOfBasePairsToAddOrRemove =  self._determine_numberOfBasePairs_to_change()

        ladderEndAxisAtom = self.get_axisEndAtom_at_resize_end()

        if ladderEndAxisAtom is None:
            print_compact_stack("bug: unable to resize the DnaSegment"\
                                "%r, end axis ato not found"%self.currentStruct)
            return


        if numberOfBasePairsToAddOrRemove != 0:  

            resizeEnd_final_position = self._get_resizeEnd_final_position(
                ladderEndAxisAtom, 
                abs(numberOfBasePairsToAddOrRemove),
                duplexRise )

            self.dna.modify(self.currentStruct, 
                            ladderEndAxisAtom,
                            numberOfBasePairsToAddOrRemove, 
                            basesPerTurn, 
                            duplexRise,
                            ladderEndAxisAtom.posn(),
                            resizeEnd_final_position)

        self.previousParams = params

        return 

    def modifyStructure(self):
        """

        Called when a resize handle is dragged to change the length of one 
        or more DnaSegments (to be resized together)  Called upon leftUp . 

        To acheive this resizing, it loops through the DnaSegments to be resized
        and calls self._modifyStructure() for individual DnaSegments. 

        Note that Client should call this public method and should never call
        the private method self._modifyStructure. 

        @see: B{DnaSegment_ResizeHandle.on_release} (the caller)
        @see: B{SelectChunks_GraphicsMode.leftUp} (which calls the 
              the relevent method in DragHandler API. )
        @see: B{exprs.DraggableHandle_AlongLine}, B{exprs.DragBehavior}

        @see: B{self._modifyStructure}   
        @see: B{DnaSegmentList.updateAverageEndPoints()}

        """

        if self.grabbedHandle is None:
            return   

        for segment in self.getResizeSegmentList():
            #TODO 2008-05-14: DnaSegmentList class relies on self.currentStruct.
            #See if there is a better way. Ok for now 
            self.currentStruct = segment
            #self._modifyStructure needs 'param' argument. As of 2008-05-14
            #it is not supported/needed for multiple dna segment resizing. 
            #So just pass an empty tuple. 
            params = ()
            self._modifyStructure(params)
            #Reset the self.currentStruct after use
            self.currentStruct = None

        #Update the average end points of the self.struct so that resize handles
        #are placed at proper positions. 
        self.struct.updateAverageEndPoints()

        self.win.assy.changed()
        self.win.win_update()


    def _get_resizeEnd_final_position(self, 
                                      ladderEndAxisAtom, 
                                      numberOfBases, 
                                      duplexRise):
        """
        Returns the final position of the resize end. 
        Note that we can not use the grabbedHandle's currentPosition as the 
        final position because resize handle is placed at an 'average' position.
        So we must compute the correct vector using the 'self.currentStruct'
        """

        final_position = None  

        other_axisEndAtom = self.struct.getOtherAxisEndAtom(ladderEndAxisAtom)

        if other_axisEndAtom is None:
            return None

        axis_vector = ladderEndAxisAtom.posn() - other_axisEndAtom.posn()
        segment_length_to_add = getDuplexLength('B-DNA', 
                                                numberOfBases, 
                                                duplexRise = duplexRise)

        signFactor = + 1

        ##if self.grabbedHandle is not None:
            ##vec = self.grabbedHandle.currentPosition - \
            ##       self.grabbedHandle.fixedEndOfStructure

            ##if dot(vec, axis_vector) < 0:
                ##signFactor = -1
            ##else:
                ##signFactor = +1


        axis_vector = axis_vector * signFactor


        final_position = ladderEndAxisAtom.posn() + \
                       norm(axis_vector)*segment_length_to_add

        return final_position


    def hasResizableStructure(self):   
        """
        """
        if len(self.struct.getStructList()) == 0:
            why_not = 'Segment list is empty'
            isResizable = False 
            return isResizable, why_not          

        return  _superclass.hasResizableStructure(self)

    def _getStructureType(self):
        """
        Returns the type of the structure this command supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() 
        """
        return DnaSegmentList


    def getDnaRibbonParams(self):
        """
        Overrides superclass method. 
        @TODO:[2008-05-14]  This could SLOW things up! Its called multiple times 
        from the graphics mode (for all the DnaSegments to be resized at once).
        There is no apparent solution to this, but we could try optimizing the 
        following code. Also needs some refactoring. 
        @see: MultipleDnaSegmentResize_GraphicsMode._drawHandles()
        @see: self._determine_numberOfBasePairs_to_change()
        """

        #Optimization: First test a few basic things to see if the dna ribbon 
        #should be drawn, before doing more computations -- Ninad 2008-05-14

        params_when_adding_bases = None
        params_when_removing_bases = None        

        if self.grabbedHandle is None:
            return None, None

        if self.grabbedHandle.origin is None:
            return None, None

        ladderEndAxisAtom = self.get_axisEndAtom_at_resize_end()

        if ladderEndAxisAtom is None:
            return None, None

        numberOfBasePairsToAddOrRemove = self._determine_numberOfBasePairs_to_change()

        if numberOfBasePairsToAddOrRemove == 0:
            return None, None


        direction_of_drag = norm(self.grabbedHandle.currentPosition - \
                                 self.grabbedHandle.origin)


        #@TODO: BUG: DO NOT use self._get_resizeEnd_final_position to compute 
        #the resizeEnd_final_position. It computes the segment length to add
        #using the number of base pairs to add ... and it uses 
        #getDuplexLength method which in turn rounds off the length as an integer
        #multiple of duplexRise. Although this is what we want in self._modify()
        #the drawDnaRibbon draws the base pair only if step size is > 3.18! 
        #so no basepair is drawn at exact val of 3.18. This is BUG, harder to 
        #fix. for drawing dna ribbon, lets justcompute the resize end final 
        #position using the following code. -- Ninad 2008-05-14
        other_axisEndAtom = self.struct.getOtherAxisEndAtom(ladderEndAxisAtom)

        if other_axisEndAtom is None:
            return None, None

        axis_vector = ladderEndAxisAtom.posn() - other_axisEndAtom.posn()
        currentPosition = self.grabbedHandle.currentPosition
        changedLength = vlen(currentPosition - self.grabbedHandle.origin)
        
        #NOTE: (TODO) we call self._determine_numberOfBasePairs_to_change() at the 
        #beginning of this method which checks various things such as 
        #total distance moved by the handle etc to determine whether to draw 
        #the ribbon. So those checks are not done here. If that call is removed
        #then we need to do those checks.

        if dot(self.grabbedHandle.direction, direction_of_drag) < 0:
            signFactor = -1.0
        else:
            signFactor = 1.0

        resizeEnd_final_position = ladderEndAxisAtom.posn() + \
                                 norm(axis_vector)*changedLength*signFactor        



        #If the segment is being shortened (determined by checking the 
        #direction of drag) , no need to draw the rubberband line. 
        if dot(self.grabbedHandle.direction, direction_of_drag) < 0:
            params_when_adding_bases = None
            params_when_removing_bases = (resizeEnd_final_position)

            return params_when_adding_bases, \
                   params_when_removing_bases

        basesPerTurn = self.struct.getBasesPerTurn()
        duplexRise = self.struct.getDuplexRise()

        ladder = ladderEndAxisAtom.molecule.ladder                        
        endBaseAtomList  = ladder.get_endBaseAtoms_containing_atom(
            ladderEndAxisAtom)

        ribbon1_start_point = None
        ribbon2_start_point = None  
        ribbon1_direction = None
        ribbon2_direction = None

        ribbon1Color = applegreen
        ribbon2Color = applegreen

        if endBaseAtomList and len(endBaseAtomList) > 2: 
            strand_atom1 = endBaseAtomList[0]
            strand_atom2 = endBaseAtomList[2]

            if strand_atom1:
                ribbon1_start_point = strand_atom1.posn()
                for bond_direction, neighbor in strand_atom1.bond_directions_to_neighbors():
                    if neighbor and neighbor.is_singlet():
                        ribbon1_direction = bond_direction
                        break

                ribbon1Color = strand_atom1.molecule.color
                if not ribbon1Color:
                    ribbon1Color = strand_atom1.element.color

            if strand_atom2:
                ribbon2_start_point = strand_atom2.posn()
                for bond_direction, neighbor in strand_atom2.bond_directions_to_neighbors():
                    if neighbor and neighbor.is_singlet():
                        ribbon2_direction = bond_direction
                        break
                ribbon2Color = strand_atom2.molecule.color
                if not ribbon2Color:
                    ribbon2Color = strand_atom2.element.color
                    
        
        params_when_adding_bases = ( ladderEndAxisAtom.posn(),
                                     resizeEnd_final_position,                                     
                                     basesPerTurn,
                                     duplexRise, 
                                     ribbon1_start_point,
                                     ribbon2_start_point,
                                     ribbon1_direction,
                                     ribbon2_direction,
                                     ribbon1Color,
                                     ribbon2Color )

        params_when_removing_bases = None        

        return params_when_adding_bases, params_when_removing_bases


    def _determine_numberOfBasePairs_to_change(self):
        """
        Overrides superclass method
        @TODO: This is significantly different (and perhaps better)
               than the superclass method. See how to incorporate changes in 
               this method in superclass.

        @see: self.getDnaRibbonParams()
        """

        currentPosition = self.grabbedHandle.currentPosition
        fixedEndOfStructure = self.grabbedHandle.fixedEndOfStructure
        duplexRise = self.struct.getDuplexRise()

        changedLength = vlen(currentPosition - self.grabbedHandle.origin)

        direction_of_drag = norm(self.grabbedHandle.currentPosition - \
                                 self.grabbedHandle.origin)


        #Even when the direction of drag is negative (i.e. the basepairs being 
        #removed), make sure not to remove base pairs for very small movement
        #of the grabbed handle 
        if changedLength < 0.2*duplexRise:
            return 0

        #This check quickly determines if the grabbed handle moved by a distance
        #more than the duplexRise and avoids further computations
        #This condition is applicable only when the direction of drag is 
        #positive..i.e. bases bing added to the segment. 
        if changedLength < duplexRise and \
           dot(self.grabbedHandle.direction, direction_of_drag) > 0:
            return 0


        #If the segment is being shortened (determined by checking the 
        #direction of drag)  

        numberOfBasesToAddOrRemove =  \
                                   getNumberOfBasePairsFromDuplexLength(
                                       'B-DNA', 
                                       changedLength,
                                       duplexRise = duplexRise)

        if dot(self.grabbedHandle.direction, direction_of_drag) < 0:            
            numberOfBasesToAddOrRemove = - numberOfBasesToAddOrRemove


        if numberOfBasesToAddOrRemove > 0:
            #dna.modify will remove the first base pair it creates 
            #(that basepair will only be used for proper alignment of the 
            #duplex with the existing structure) So we need to compensate for
            #this basepair by adding 1 to the new number of base pairs. 

            #UPDATE 2008-05-14: The following commented out code 
            #i.e. "##numberOfBasesToAddOrRemove += 1" is not required in this 
            #class , because the way we compute the number of base pairs to 
            #be added is different than than how its done at the moment in the
            #superclass. In this method, we compute bases to be added from 
            #the resize end and that computation INCLUDES the resize end. 
            #so the number that it returns is already one more than the actual
            #bases to be added. so commenting out the following line
            # -- Ninad 2008-05-14
            ##numberOfBasesToAddOrRemove += 1
            ##print "*** numberOfBasesToAddOrRemove = ", numberOfBasesToAddOrRemove
            ##print "**** changedLength =", changedLength
            pass
            ###UPDATE 2008-06-26: for some reason, when the number of base pairs
            ###to be added (i.e. value of numberOfBasesToAddOrRemove) is  1 more 
            ###than the actual number of base pairs to be added. So subtract 1 
            ###from this number. Cause not debugged. -- Ninad
            ##if numberOfBasesToAddOrRemove > 1:
                ##numberOfBasesToAddOrRemove -= 1
            #UPDATE 2008-08-20: Note that DnaSegment_EditCommand.getCursorText()
            #does the job of removing the extra basepair from numberOfBasesToAddOrRemove
            #It(subtracting 1 basePair) is not done here as 
            #self._modifyStructure() needs it without the subtraction. This is
            #prone to bugs and need to be cleaned up. -- Ninad
            

        return numberOfBasesToAddOrRemove

    