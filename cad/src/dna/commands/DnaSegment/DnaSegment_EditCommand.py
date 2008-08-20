# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSegment_EditCommand provides a way to edit an existing DnaSegment. 

To edit a segment, first enter BuildDna_EditCommand (accessed using Build> Dna) 
then, select an axis chunk of an existing DnaSegment  within the DnaGroup you
are editing. When you select the axis chunk, it enters DnaSegment_Editcommand
and shows the property manager with its widgets showing the properties of 
selected segment. 

While in this command, user can 
(a) Highlight and then left drag the resize handles located at the 
    two 'axis endpoints' of thje segment to change its length.  
(b) Highlight and then left drag any axis atom (except the two end axis atoms)
    to translate the  whole segment along the axis
(c) Highlight and then left drag any strand atom to rotate the segment around 
    its axis. 

    Note that implementation b and c may change slightly if we implement special
    handles to do these oprations. 
    See also: DnaSegment_GraphicsMode .. the default graphics mode for this 
    command


@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
Ninad 2008-01-18: Created

TODO:
- Needs cleanup and REFACTORING.


"""

import foundation.env as env
from command_support.EditCommand       import EditCommand 
from utilities.exception_classes import PluginBug, UserError

from geometry.VQT import V, Veq, vlen
from geometry.VQT import cross, norm
from Numeric import dot

from utilities.constants  import gensym
from utilities.Log        import redmsg
from prototype.test_connectWithState import State_preMixin

from exprs.attr_decl_macros import Instance, State
from exprs.__Symbols__      import _self
from exprs.Exprs            import call_Expr
from exprs.Exprs            import norm_Expr
from exprs.ExprsConstants   import Width, Point
from widgets.prefs_widgets  import ObjAttr_StateRef

from model.chunk import Chunk
from model.chem import Atom
from model.bonds import Bond

from utilities.constants   import noop
from utilities.constants    import black, applegreen

from graphics.drawables.RotationHandle  import RotationHandle

from dna.model.DnaSegment           import DnaSegment
from dna.model.Dna_Constants        import getDuplexRise
from dna.model.Dna_Constants        import getNumberOfBasePairsFromDuplexLength
from dna.model.Dna_Constants        import getDuplexLength

from dna.commands.BuildDuplex.DnaDuplex import B_Dna_PAM3
from dna.commands.BuildDuplex.DnaDuplex import B_Dna_PAM5
from dna.commands.DnaSegment.DnaSegment_ResizeHandle import DnaSegment_ResizeHandle
from dna.commands.DnaSegment.DnaSegment_GraphicsMode import DnaSegment_GraphicsMode

from utilities.prefs_constants import dnaSegmentEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key
from utilities.prefs_constants import dnaSegmentEditCommand_cursorTextCheckBox_length_prefs_key
from utilities.prefs_constants import dnaSegmentEditCommand_showCursorTextCheckBox_prefs_key
from utilities.prefs_constants import dnaSegmentEditCommand_cursorTextCheckBox_changedBasePairs_prefs_key
from utilities.prefs_constants import dnaSegmentResizeHandle_discRadius_prefs_key
from utilities.prefs_constants import dnaSegmentResizeHandle_discThickness_prefs_key
from dna.model.Dna_Constants import getDuplexLength

CYLINDER_WIDTH_DEFAULT_VALUE = 0.0
HANDLE_RADIUS_DEFAULT_VALUE = 1.2
ORIGIN = V(0,0,0)

#Flag that appends rotation handles to the self.handles (thus enabling their 
#display and computation while in DnaSegment_EditCommand
DEBUG_ROTATION_HANDLES = False


class DnaSegment_EditCommand(State_preMixin, EditCommand):
    """
    Command to edit a DnaSegment object. 
    To edit a segment, first enter BuildDna_EditCommand (accessed using Build> Dna) 
    then, select an axis chunk of an existing DnaSegment  within the DnaGroup you
    are editing. When you select the axis chunk, it enters DnaSegment_Editcommand
    and shows the property manager with its widgets showing the properties of 
    selected segment.
    """
    cmd              =  'Dna Segment'
    prefix           =  'Segment '   # used for gensym
    cmdname          = "DNA_SEGMENT"
    
    commandName       = 'DNA_SEGMENT'
    featurename       = "Edit Dna Segment"
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
    GraphicsMode_class = DnaSegment_GraphicsMode

    #This is set to BuildDna_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None   

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

    duplexRise =  getDuplexRise('B-DNA')

    leftHandle = Instance(         
        DnaSegment_ResizeHandle(    
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth'),
            origin = handlePoint1,
            fixedEndOfStructure = handlePoint2,
            direction = norm_Expr(handlePoint1 - handlePoint2),
            sphereRadius = handleSphereRadius1, 
            discRadius = env.prefs[dnaSegmentResizeHandle_discRadius_prefs_key],
            discThickness = env.prefs[dnaSegmentResizeHandle_discThickness_prefs_key],
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
            discRadius = env.prefs[dnaSegmentResizeHandle_discRadius_prefs_key],
            discThickness = env.prefs[dnaSegmentResizeHandle_discThickness_prefs_key],
            range = (_resizeHandle_stopper_length, 10000)
        ))

    rotationHandle1 = Instance(         
        RotationHandle(    
            command = _self,
            rotationDistanceRef = call_Expr( ObjAttr_StateRef,
                                             _self, 
                                             'rotation_distance1'),
            center = handlePoint1,
            axis = norm_Expr(handlePoint1 - handlePoint2),
            origin = rotationHandleBasePoint1,
            radiusVector = norm_Expr(rotationHandleBasePoint1 - handlePoint1)

        ))

    rotationHandle2 = Instance(         
        RotationHandle(    
            command = _self,
            rotationDistanceRef = call_Expr( ObjAttr_StateRef,
                                             _self, 
                                             'rotation_distance2'),
            center = handlePoint2,
            axis = norm_Expr(handlePoint2 - handlePoint1),
            origin = rotationHandleBasePoint2,
            radiusVector = norm_Expr(rotationHandleBasePoint2 - handlePoint2)

        ))


    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for DnaDuplex_EditCommand
        """

        glpane = commandSequencer.assy.glpane
        State_preMixin.__init__(self, glpane)        
        EditCommand.__init__(self, commandSequencer)
        self.struct = struct

        #Graphics handles for editing the structure . 
        self.handles = []        
        self.grabbedHandle = None


    def command_enter_PM(self):
        """
        See superclass dor documentation.
        """
        #Note that DnaSegment_EditCommand only act as an edit command for an 
        #existing structure. The call to self.propMgr.show() is done only during
        #the call to self.editStructure ..i .e. only after self.struct is 
        #updated. This is done because of the following reason:
        # - self.init_gui is called immediately after entering the command. 
        # - self.init_gui in turn, initialized propMgr object and may also 
        #  show the property manager. The self.propMgr.show routine calls 
        #  an update widget method just before the show. This update method 
        #  updates the widgets based on the parameters from the existing 
        #  structure of the command (self.editCommand.struct)
        #  Although, it checks whether this structure exists, the editCommand
        #  could still have a self.struct attr from a previous run. (Note that 
        #  EditCommand API was written before the command sequencer API and 
        #  it has some loose ends like this. ) -- Ninad 2008-01-22
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

            self._update_previousParams_in_model_changed()


    def _update_previousParams_in_model_changed(self):
        #The following fixes bug 2802. The bug comment has details of what
        #it does. Copying some portion of it below--            
        #We have fixed similar problem for strand resizing, by updating the
        #self.previousParams attr in model_changed method (and also updating
        #the numberOfBasePairs spinbox in the PM. But here, user can even 
        #change the number of basepairs from the PM. When he does that, 
        #the model_changed is called and it resets the number of basepairs 
        #spinbox value with  the ones currently on the structure! Thereby 
        #making it impossible to upate structure using spinbox.  To fix this
        #we introduce a new parameter in propMgr.getParameters() which 
        #reports the actual number of bases on the structure. 
        #-- Ninad 2008-04-12
        if self.previousParams is not None:
            new_numberOfBasePairs = self.struct.getNumberOfBasePairs()
            if new_numberOfBasePairs != self.previousParams[0]:
                self.propMgr.numberOfBasePairsSpinBox.setValue(new_numberOfBasePairs)
                self.previousParams = self.propMgr.getParameters()



    def editStructure(self, struct = None):
        EditCommand.editStructure(self, struct)        
        if self.hasValidStructure():             
            self._updatePropMgrParams()

            #Store the previous parameters. Important to set it after you 
            #set duplexRise and basesPerTurn attrs in the propMgr. 
            #self.previousParams is used in self._previewStructure and 
            #self._finalizeStructure to check if self.struct changed.
            self.previousParams = self._gatherParameters()

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
        #(i.e. in propMgr.setParameters():
            #numberOfBasePairs,
            #dnaForm, 
            #dnaModel,
            #basesPerTurn,
            #duplexRise, 
            #endPoint1, 
            #endPoint2

        basesPerTurn, duplexRise = self.struct.getProps()
        endPoint1, endPoint2 = self.struct.getAxisEndPoints()
        numberOfBasePairs = self.struct.getNumberOfBasePairs()
        color = self.struct.getColor()

        params_for_propMgr = (
                              numberOfBasePairs,
                              None, 
                              None,
                              basesPerTurn, 
                              duplexRise, 
                              endPoint1, 
                              endPoint2, 
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
        @see: BreakStrands_Command.keep_empty_group
        @see: Group.autodelete_when_empty.. a class constant used by the 
              dna_updater (the dna updater then decides whether to call this 
              method to see which empty groups need to be deleted)
        """

        bool_keep = EditCommand.keep_empty_group(self, group)

        if not bool_keep:     
            if self.hasValidStructure():                
                if group is self.struct:
                    bool_keep = True
                elif group is self.struct.parent_node_of_class(self.assy.DnaGroup):
                    bool_keep = True
            #If this command doesn't have a valid structure, as a fall back, 
            #lets instruct it to keep ALL the DnaGroup objects even when empty
            #Reason? ..see explanation in BreakStrands_Command.keep_empty_group
            elif isinstance(group, self.assy.DnaGroup):
                bool_keep = True

        return bool_keep

    def hasResizableStructure(self):
        """
        For Rattlesnake release, we dont support segment resizing for PAM5 
        models. If the structure is not resizable, the handles won't be drawn
        @see:self.model_changed()
        @see:DnaSegment_PropertyManager.model_changed()
        @see: self.editStructure()
        @see: DnaSegment.is_PAM3_DnaSegment()
        """
        #Note: This method fixes bugs similar to bug 2812 but the changes 
        #didn't made it to Rattlesnake rc2 -- Ninad 2008-04-16
        isResizable = True
        why_not = ''

        if not self.hasValidStructure():
            isResizable = False
            why_not     = 'It is invalid.'
            return isResizable, why_not

        isResizable = self.struct.is_PAM3_DnaSegment()
        if not isResizable:
            why_not = 'It needs to be converted to PAM3 model'
            return isResizable, why_not

        endAtom1, endAtom2 = self.struct.getAxisEndAtoms() 

        if endAtom1 is None or endAtom2 is None:
            isResizable = False
            why_not = "Unable to determine one or both end atoms of the segment"
            return isResizable, why_not

        if endAtom1 is endAtom2:
            isResizable = False
            why_not = "Resizing a segment with single atom is unsupported"
            return isResizable, why_not

        return isResizable, why_not

    def hasValidStructure(self):
        """
        Tells the caller if this edit command has a valid structure. 
        Overrides EditCommand.hasValidStructure()
        """
        #(By Bruce 2008-02-13)

        isValid = EditCommand.hasValidStructure(self)

        if not isValid:
            return isValid

        # would like to check here whether it's empty of axis chunks;
        # instead, this will do for now (probably too slow, though):
        p1, p2 = self.struct.getAxisEndPoints()
        return (p1 is not None)

    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return self.win.assy.DnaSegment

    def _updateHandleList(self):
        """        
        Updates the list of handles (self.handles) 
        @see: self.editStructure
        @see: DnaSegment_GraphicsMode._drawHandles()
        """   
        # note: if handlePoint1 and/or handlePoint2 can change more often than this 
        # runs, we'll need to rerun the two assignments above whenever they 
        # change and before the handle is drawn. An easy way would be to rerun
        # these assignments in the draw method of our GM. [bruce 080128]
        self.handles = [] # guess, but seems like a good idea [bruce 080128]
        self.handles.append(self.leftHandle)
        self.handles.append(self.rightHandle)
        if DEBUG_ROTATION_HANDLES:
            self.handles.append(self.rotationHandle1)
            self.handles.append(self.rotationHandle2)

    def updateHandlePositions(self):
        """
        Update handle positions and also update the resize handle radii and
        their 'stopper' lengths. 
        @see: self._update_resizeHandle_radius()
        @see: self._update_resizeHandle_stopper_length()     
        @see: DnaSegment_GraphicsMode._drawHandles()
        """  

        if len(self.handles) == 0:
            #No handles are appended to self.handles list. 
            #@See self.model_changed() and self._updateHandleList()
            return


        #TODO: Call this method less often by implementing model_changed
        #see bug 2729 for a planned optimization
        self.cylinderWidth = CYLINDER_WIDTH_DEFAULT_VALUE
        self.cylinderWidth2 = CYLINDER_WIDTH_DEFAULT_VALUE      

        self._update_resizeHandle_radius()

        handlePoint1, handlePoint2 = self.struct.getAxisEndPoints()        

        if handlePoint1 is not None and handlePoint2 is not None:
            # (that condition is bugfix for deleted axis segment, bruce 080213)

            self.handlePoint1, self.handlePoint2 = handlePoint1, handlePoint2 

            #Update the 'stopper'  length where the resize handle being dragged 
            #should stop. See self._update_resizeHandle_stopper_length()
            #for more details
            self._update_resizeHandle_stopper_length()            

            if DEBUG_ROTATION_HANDLES:
                self.rotation_distance1 = CYLINDER_WIDTH_DEFAULT_VALUE
                self.rotation_distance2 = CYLINDER_WIDTH_DEFAULT_VALUE
                #Following computes the base points for rotation handles. 
                #to be revised -- Ninad 2008-02-13
                unitVectorAlongAxis = norm(self.handlePoint1 - self.handlePoint2)

                v  = cross(self.glpane.lineOfSight, unitVectorAlongAxis)

                self.rotationHandleBasePoint1 = self.handlePoint1 + norm(v) * 4.0  
                self.rotationHandleBasePoint2 = self.handlePoint2 + norm(v) * 4.0 


    def _update_resizeHandle_radius(self):
        """
        Finds out the sphere radius to use for the resize handles, based on 
        atom /chunk or glpane display (whichever decides the display of the end 
        atoms.  


        @see: self.updateHandlePositions()
        @see: B{Atom.drawing_radius()}
        """
        atm1 , atm2 = self.struct.getAxisEndAtoms()                  
        if atm1 is not None:
            self.handleSphereRadius1 = max(1.25*atm1.drawing_radius(), 
                                           1.25*HANDLE_RADIUS_DEFAULT_VALUE)
        if atm2 is not None: 
            self.handleSphereRadius2 =  max(1.25*atm2.drawing_radius(), 
                                            1.25*HANDLE_RADIUS_DEFAULT_VALUE)

    def _update_resizeHandle_stopper_length(self):
        """
        Update the limiting length at which the resize handle being dragged
        should 'stop'  without proceeding further in the drag direction. 
        The segment resize handle stops when you are dragging it towards the 
        other resizeend and the distance between the two ends reaches two 
        duplexes. 

        The self._resizeHandle_stopper_length computed in this method is 
        used as a lower limit of the 'range' option provided in declaration
        of resize handle objects (see class definition for the details)
        @see: self.updateHandlePositions()
        """

        total_length = vlen(self.handlePoint1 - self.handlePoint2)        
        duplexRise = self.struct.getDuplexRise() 

        #Length of the duplex for 2 base pairs
        two_bases_length = getDuplexLength('B-DNA', 
                                           2, 
                                           duplexRise = duplexRise)

        self._resizeHandle_stopper_length = - total_length + two_bases_length


    def _createPropMgrObject(self):
        """
        Creates a property manager object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = self.win.createDnaSegmentPropMgr_if_needed(self)
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
        Creates and returns the structure (in this case a L{Group} object that 
        contains the DNA strand and axis chunks. 
        @return : group containing that contains the DNA strand and axis chunks.
        @rtype: L{Group}  
        @note: This needs to return a DNA object once that model is implemented        
        """

        params = self._gatherParameters()


        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        number_of_basePairs_from_struct,\
                                       numberOfBases, \
                                       dnaForm, \
                                       dnaModel, \
                                       basesPerTurn, \
                                       duplexRise, \
                                       endPoint1, \
                                       endPoint2, \
                                       color_junk = params
        #Note: color_junk is not used. Ideally it should do struct.setColor(color) 
        #but the color combobox in the PM directly sets the color of the 
        #structure to the specified one when the current index in the combobx 
        #changes

        #If user enters the number of basepairs and hits preview i.e. endPoint1
        #and endPoint2 are not entered by the user and thus have default value 
        #of V(0, 0, 0), then enter the endPoint1 as V(0, 0, 0) and compute
        #endPoint2 using the duplex length. 
        #Do not use '==' equality check on vectors! its a bug. Use same_vals 
        # or Veq instead. 
        if Veq(endPoint1 , endPoint2) and Veq(endPoint1, V(0, 0, 0)):
            endPoint2 = endPoint1 + \
                      self.win.glpane.right*getDuplexLength('B-DNA', 
                                                            numberOfBases)


        if numberOfBases < 1:
            msg = redmsg("Cannot preview/insert a DNA duplex with 0 bases.")
            self.propMgr.updateMessage(msg)
            self.dna = None # Fixes bug 2530. Mark 2007-09-02
            return None

        if dnaForm == 'B-DNA':
            if dnaModel == 'PAM3':
                dna = B_Dna_PAM3()
            elif dnaModel == 'PAM5':
                dna = B_Dna_PAM5()
            else:
                print "bug: unknown dnaModel type: ", dnaModel
        else:
            raise PluginBug("Unsupported DNA Form: " + dnaForm)

        self.dna  =  dna  # needed for done msg

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix, self.win.assy) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name


        # Create the model tree group node. 
        # Make sure that the 'topnode'  of this part is a Group (under which the
        # DNa group will be placed), if the topnode is not a group, make it a
        # a 'Group' (applicable to Clipboard parts).See part.py
        # --Part.ensure_toplevel_group method. This is an important line
        # and it fixes bug 2585
        self.win.assy.part.ensure_toplevel_group()
        dnaSegment = DnaSegment(self.name, 
                                self.win.assy,
                                self.win.assy.part.topnode,
                                editCommand = self  )
        try:
            # Make the DNA duplex. <dnaGroup> will contain three chunks:
            #  - Strand1
            #  - Strand2
            #  - Axis

            dna.make(dnaSegment, 
                     numberOfBases, 
                     basesPerTurn, 
                     duplexRise,
                     endPoint1,
                     endPoint2)

            #set some properties such as duplexRise and number of bases per turn
            #This information will be stored on the DnaSegment object so that
            #it can be retrieved while editing this object. 
            #This works with or without dna_updater. Now the question is 
            #should these props be assigned to the DnaSegment in 
            #dnaDuplex.make() itself ? This needs to be answered while modifying
            #make() method to fit in the dna data model. --Ninad 2008-03-05

            #WARNING 2008-03-05: Since self._modifyStructure calls 
            #self._createStructure() 
            #If in the near future, we actually permit modifying a
            #structure (such as dna) without actually recreating the whole 
            #structre, then the following properties must be set in 
            #self._modifyStructure as well. Needs more thought.
            props = (duplexRise, basesPerTurn)            
            dnaSegment.setProps(props)

            return dnaSegment

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            dnaSegment.kill()
            raise PluginBug("Internal error while trying to create DNA duplex.")


    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        """                
        assert self.struct        

        self.dna = B_Dna_PAM3()

        number_of_basePairs_from_struct,\
                                       numberOfBases, \
                                       dnaForm, \
                                       dnaModel, \
                                       basesPerTurn, \
                                       duplexRise, \
                                       endPoint1, \
                                       endPoint2 , \
                                       color = params

        #Delete unused parameters. 
        del endPoint1
        del endPoint2
        del number_of_basePairs_from_struct



        numberOfBasePairsToAddOrRemove =  self._determine_numberOfBasePairs_to_change()


        ladderEndAxisAtom = self.get_axisEndAtom_at_resize_end()

        if numberOfBasePairsToAddOrRemove != 0:   

            resizeEnd_final_position = self._get_resizeEnd_final_position(
                ladderEndAxisAtom, 
                abs(numberOfBasePairsToAddOrRemove),
                duplexRise )

            self.dna.modify(self.struct, 
                            ladderEndAxisAtom,
                            numberOfBasePairsToAddOrRemove, 
                            basesPerTurn, 
                            duplexRise,
                            ladderEndAxisAtom.posn(),
                            resizeEnd_final_position)

        #Find new end points of structure parameters after modification 
        #and set these values in the propMgr. 
        new_end1 , new_end2 = self.struct.getAxisEndPoints()

        params_to_set_in_propMgr = (numberOfBases, 
                                    dnaForm,
                                    dnaModel,
                                    basesPerTurn, 
                                    duplexRise,
                                    new_end1,
                                    new_end2, 
                                    color)

        #TODO: Need to set these params in the PM 
        #and then self.previousParams = params_to_set_in_propMgr

        self.previousParams = params

        return  

    def _get_resizeEnd_final_position(self, 
                                      ladderEndAxisAtom, 
                                      numberOfBases, 
                                      duplexRise):

        final_position = None   
        if self.grabbedHandle:
            final_position = self.grabbedHandle.currentPosition
        else:
            other_axisEndAtom = self.struct.getOtherAxisEndAtom(ladderEndAxisAtom)
            axis_vector = ladderEndAxisAtom.posn() - other_axisEndAtom.posn()
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
        @see: DnaSegment_PropertyManager.show()
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
        @see: DnaSegment_PropertyManager.close()
        @see: self.getStructureName()

        """
        #@BUG: We call this method in self.propMgr.close(). But propMgr.close() 
                #is called even when the command is 'cancelled'. That means the 
                #structure will get changed even when user hits cancel button or
                #exits the command by clicking on empty space. 
                #This should really be done in self._finalizeStructure but that 
                #method doesn't get called when you click on empty space to exit 
                #the command. See DnaSegment_GraphicsMode.leftUp for a detailed 
                #comment. 

        if self.hasValidStructure():
            self.struct.name = name

    def getCursorText(self):
        """
        This is used as a callback method in DnaLine mode 
        @see: DnaLineMode.setParams, DnaLineMode_GM.Draw
        """
        #@TODO: Refactor this. Similar code exists in 
        #DnaStrand_EditCommand.getCursorText() -- Ninad 2008-04-12
        if self.grabbedHandle is None:
            return        

        currentPosition = self.grabbedHandle.currentPosition
        fixedEndOfStructure = self.grabbedHandle.fixedEndOfStructure

        duplexRise = self.struct.getDuplexRise()

        #############

        raw_numberOfBasePairsToAddOrRemove = self._determine_numberOfBasePairs_to_change()

        #Following fixes bugs like 2904 and 2906
        #Note that we are using numberOfBasePairsToAddOrRemove in self._modifyStructure()
        #if self._determine_numberOfBasePairs_to_change() returns the number of basepairs 
        #to add, it returns 1 more than the actual number of basepairs. Because 
        #while creating the dna, it removes the first base pair of the newly created 
        #dna. So, for cursor text and for PM spinbox, we should make adjustments to the
        #raw_numberOfBasePairsToAddOrRemove so that it reflects the correct value 
        #in the spinbox and in the PM

        if raw_numberOfBasePairsToAddOrRemove > 1:
            numberOfBasePairsToAddOrRemove = raw_numberOfBasePairsToAddOrRemove - 1

        else:
            numberOfBasePairsToAddOrRemove = raw_numberOfBasePairsToAddOrRemove

        current_numberOfBasePairs = self.struct.getNumberOfBasePairs()
      
        numberOfBasePairs = current_numberOfBasePairs + numberOfBasePairsToAddOrRemove
        
        if hasattr(self.propMgr, 'numberOfBasePairsSpinBox'):            
            #@TODO: The following updates the PM as the cursor moves. 
            #Need to rename this method so that you that it also does more things 
            #than just to return a textString -- Ninad 2007-12-20
            self.propMgr.numberOfBasePairsSpinBox.setValue(numberOfBasePairs)

        
        #Use the text color that better contrasts with the background color. 
        #mitigates bug 2927
        textColor = self.glpane.get_background_contrast_color()

        text = "" 

        if not env.prefs[dnaSegmentEditCommand_showCursorTextCheckBox_prefs_key]:
            return '', black
        
                
        #@@TODO: refactor. 
        #this duplex length canculation fixes bug 2906
        duplexLength = getDuplexLength('B-DNA', 
                                   numberOfBasePairs, 
                                   duplexRise = duplexRise)

        #Cursor text strings --
        duplexLengthString = str(round(duplexLength, 3))

        numberOfBasePairsString = self._getCursorText_numberOfBasePairs(
            numberOfBasePairs)


        duplexLengthString  = self._getCursorText_length(duplexLength)

        changedBasePairsString = self._getCursorText_changedBasePairs(
            numberOfBasePairs)

        #Add commas (to be refactored)
        commaString = ", "
        text = numberOfBasePairsString        

        if text and changedBasePairsString:
            text += " "# commaString not needed here. Mark 2008-07-03

        text += changedBasePairsString 
        
        if text and duplexLengthString:
            text += commaString

        text += duplexLengthString
        
        return (text, textColor)

    def _getCursorText_numberOfBasePairs(self, numberOfBasePairs):
        """
        Return the cursor textstring that gives information about the number 
        of basepairs if the corresponding prefs_key returns True.
        """
        numberOfBasePairsString = ''

        if env.prefs[
            dnaSegmentEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key]:
            numberOfBasePairsString = "%db"%numberOfBasePairs

        return numberOfBasePairsString

    def _getCursorText_length(self, duplexLength):
        """
        """
        duplexLengthString = ''
        if env.prefs[dnaSegmentEditCommand_cursorTextCheckBox_length_prefs_key]:
            lengthUnitString = 'A'
            #change the unit of length to nanometers if the length is > 10A
            #fixes part of bug 2856
            if duplexLength > 10.0:
                lengthUnitString = 'nm'
                duplexLength = duplexLength * 0.1
            duplexLengthString = "%5.3f%s"%(duplexLength, lengthUnitString)

        return duplexLengthString


    def _getCursorText_changedBasePairs(self, numberOfBasePairs):
        """
        """
        changedBasePairsString = ''

        if env.prefs[
            dnaSegmentEditCommand_cursorTextCheckBox_changedBasePairs_prefs_key]:            

            original_numberOfBasePairs = self.struct.getNumberOfBasePairs()

            changed_basePairs = numberOfBasePairs - original_numberOfBasePairs

            if changed_basePairs > 0:
                changedBasePairsString = "(" + "+" + str(changed_basePairs) + ")"
            else:
                changedBasePairsString = "(" + str(changed_basePairs) + ")"

        return changedBasePairsString


    def getDnaRibbonParams(self):
        """
        Returns parameters for drawing the dna ribbon. 

        If the dna rubberband line should NOT be drawn (example when you are 
        removing basepairs from the segment 
        So the caller should check if the method return value is not None. 
        @see: DnaSegment_GraphicsMode._draw_handles()
        """

        if self.grabbedHandle is None:
            return None

        if self.grabbedHandle.origin is None:
            return None

        direction_of_drag = norm(self.grabbedHandle.currentPosition - \
                                 self.grabbedHandle.origin)

        #If the segment is being shortened (determined by checking the 
        #direction of drag) , no need to draw the rubberband line. 
        if dot(self.grabbedHandle.direction, direction_of_drag) < 0:
            return None

        basesPerTurn = self.struct.getBasesPerTurn()
        duplexRise = self.struct.getDuplexRise()

        ladderEndAxisAtom = self.get_axisEndAtom_at_resize_end()
        ladder = ladderEndAxisAtom.molecule.ladder                        
        endBaseAtomList  = ladder.get_endBaseAtoms_containing_atom(ladderEndAxisAtom)
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


        return (self.grabbedHandle.origin,
                self.grabbedHandle.currentPosition,
                basesPerTurn,
                duplexRise, 
                ribbon1_start_point,
                ribbon2_start_point,
                ribbon1_direction,
                ribbon2_direction,
                ribbon1Color,
                ribbon2Color )

    def modifyStructure(self):
        """

        Called when a resize handle is dragged to change the length of the 
        segment. (Called upon leftUp) . This method assigns the new parameters 
        for the segment after it is resized and calls 
        preview_or_finalize_structure which does the rest of the job. 
        Note that Client should call this public method and should never call
        the private method self._modifyStructure. self._modifyStructure is 
        called only by self.preview_or_finalize_structure

        @see: B{DnaSegment_ResizeHandle.on_release} (the caller)
        @see: B{SelectChunks_GraphicsMode.leftUp} (which calls the 
              the relevent method in DragHandler API. )
        @see: B{exprs.DraggableHandle_AlongLine}, B{exprs.DragBehavior}
        @see: B{self.preview_or_finalize_structure }
        @see: B{self._modifyStructure}        

        As of 2008-02-01 it recreates the structure
        @see: a note in self._createStructure() about use of dnaSegment.setProps 
        """
        #TODO: need to cleanup this and may be use use something like
        #self.previousParams = params in the end -- 2008-03-24 (midnight)


        if self.grabbedHandle is None:
            return   

        ##self.propMgr.setParameters(params_to_set_in_propMgr)          
        #TODO: Important note: How does NE1 know that structure is modified? 
        #Because number of base pairs parameter in the PropMgr changes as you 
        #drag the handle . This is done in self.getCursorText() ... not the 
        #right place to do it. OR that method needs to be renamed to reflect
        #this as suggested in that method -- Ninad 2008-03-25

        self.preview_or_finalize_structure(previewing = True) 

        ##self.previousParams = params_to_set_in_propMgr

        self.glpane.gl_update()

    def get_axisEndAtom_at_resize_end(self):
        ladderEndAxisAtom = None
        if self.grabbedHandle is not None:
            ladderEndAxisAtom = self.struct.getAxisEndAtomAtPosition(self.grabbedHandle.origin)
        else:
            endAtom1, endAtom2 = self.struct.getAxisEndAtoms()
            ladderEndAxisAtom = endAtom2

        return ladderEndAxisAtom

    def _determine_numberOfBasePairs_to_change(self):
        """
        """

        duplexRise = self.struct.getDuplexRise()
        numberOfBasesToAddOrRemove = 0
        #Following helps fixing bugs like 2904 and 2906 see also self.getCursorText()
        #and TODO items in that method. Also note that the grabbed handle case
        #is similar to the one in MultipleDnaSegmentResize_EditCommand. 
        #needs refactoring and overall cleanup.
        if self.grabbedHandle is not None:
            
            currentPosition = self.grabbedHandle.currentPosition
            fixedEndOfStructure = self.grabbedHandle.fixedEndOfStructure


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
                pass
        else:
            #The Property manager will be showing the current number 
            #of base pairs (w. May be we can use that number directly here? 
            #The following is  safer to do so lets just recompute the 
            #number of base pairs. (if it turns out to be slow, we will consider
            #using the already computed calue from the property manager
            new_numberOfBasePairs = self.propMgr.numberOfBasePairsSpinBox.value()

            endPoint1, endPoint2 = self.struct.getAxisEndPoints()
            if endPoint1 is None or endPoint2 is None:
                return 0

            original_duplex_length = vlen(endPoint1 - endPoint2)

            original_numberOfBasePairs = self.struct.getNumberOfBasePairs()

            numberOfBasesToAddOrRemove = new_numberOfBasePairs - original_numberOfBasePairs 

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

            dnaGroup = self.struct.parent_node_of_class(self.assy.DnaGroup)
            if dnaGroup is None:
                return
            #following should be self.struct.getDnaGroup or self.struct.getDnaGroup
            #need to formalize method name and then make change.
            if not dnaGroup is highlightedChunk.parent_node_of_class(self.assy.DnaGroup):
                item = ("Edit unavailable: Member of a different DnaGroup",
                        noop, 'disabled')
                self.Menu_spec.append(item)
                return

        highlightedChunk.make_glpane_context_menu_items(self.Menu_spec,
                                                        command = self)

