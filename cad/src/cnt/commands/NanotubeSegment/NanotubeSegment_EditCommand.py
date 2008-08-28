# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
NanotubeSegment_EditCommand provides a way to edit an existing NanotubeSegment. 

@author: Ninad, Mark
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

To edit a segment, first enter BuildNanotube_EditCommand (accessed using Build > Cnt) 
then, select an axis chunk of an existing NanotubeSegment  within the NanotubeGroup you
are editing. When you select the axis chunk, it enters NanotubeSegment_Editcommand
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
    See also: NanotubeSegment_GraphicsMode .. the default graphics mode for this 
    command

History:
Mark 2008-03-10: Created from copy of DnaSegment_EditCommand.py
"""

import foundation.env as env
from command_support.EditCommand       import EditCommand 
from utilities.exception_classes import PluginBug, UserError

from geometry.VQT import V, Veq, vlen
from geometry.VQT import cross, norm

from utilities.constants  import gensym
from utilities.Log        import redmsg
from utilities.Comparison import same_vals

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

from utilities.debug_prefs import debug_pref, Choice_boolean_True
from utilities.constants   import noop
from utilities.Comparison  import same_vals
from utilities.constants   import black
from utilities.debug import print_compact_stack

from graphics.drawables.RotationHandle  import RotationHandle

from cnt.model.NanotubeSegment               import NanotubeSegment

from cnt.commands.NanotubeSegment.NanotubeSegment_ResizeHandle import NanotubeSegment_ResizeHandle
from cnt.commands.NanotubeSegment.NanotubeSegment_GraphicsMode import NanotubeSegment_GraphicsMode

from utilities.prefs_constants import nanotubeSegmentEditCommand_cursorTextCheckBox_length_prefs_key
from utilities.prefs_constants import nanotubeSegmentEditCommand_showCursorTextCheckBox_prefs_key
from utilities.prefs_constants import cursorTextColor_prefs_key

CYLINDER_WIDTH_DEFAULT_VALUE = 0.0
HANDLE_RADIUS_DEFAULT_VALUE = 1.2
ORIGIN = V(0,0,0)

#Flag that appends rotation handles to the self.handles (thus enabling their 
#display and computation while in NanotubeSegment_EditCommand
DEBUG_ROTATION_HANDLES = False

def pref_nt_segment_resize_by_recreating_nanotube():
    res = debug_pref("Nanotube Segment: resize by recreating whole nanotube", 
                     Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True )
    return res

class NanotubeSegment_EditCommand(State_preMixin, EditCommand):
    """
    Command to edit a NanotubeSegment object. 
    To edit a segment, first enter BuildNanotube_EditCommand (accessed using 
    Build > Nanotube) then, select an existing NanotubeSegment within the 
    NanotubeGroup you are editing. When you select the NanotubeSegment, it 
    enters NanotubeSegment_Editcommand and shows the property manager with its
    widgets showing the properties of selected segment.
    """
    cmd              =  'Nanotube Segment'
    prefix           =  'NanotubeSegment' # used for gensym
    cmdname          = "NANOTUBE_SEGMENT"

    commandName      = 'NANOTUBE_SEGMENT'
    featurename      = "Edit Nanotube Segment"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_NANOTUBE'

    command_should_resume_prevMode = True
    command_has_its_own_PM = True
    command_can_be_suspended = False

    create_name_from_prefix  =  True 

    call_makeMenus_for_each_event = True 

    #Graphics Mode 
    GraphicsMode_class = NanotubeSegment_GraphicsMode

    #This is set to BuildDna_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None

    _parentNanotubeGroup = None    

    handlePoint1 = State( Point, ORIGIN)
    handlePoint2 = State( Point, ORIGIN)
    #The minimum 'stopper'length used for resize handles
    #@see: self._update_resizeHandle_stopper_length for details. 
    _resizeHandle_stopper_length = State(Width, -100000)

    rotationHandleBasePoint1 = State( Point, ORIGIN)
    rotationHandleBasePoint2 = State( Point, ORIGIN)

    #See self._update_resizeHandle_radius where this gets changed. 
    #also see NanotubeSegment_ResizeHandle to see how its implemented. 
    handleSphereRadius1 = State(Width, HANDLE_RADIUS_DEFAULT_VALUE)
    handleSphereRadius2 = State(Width, HANDLE_RADIUS_DEFAULT_VALUE)

    cylinderWidth = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE) 
    cylinderWidth2 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE) 


    #@TODO: modify the 'State params for rotation_distance 
    rotation_distance1 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE)
    rotation_distance2 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE)

    leftHandle = Instance(         
        NanotubeSegment_ResizeHandle(    
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth'),
            origin = handlePoint1,
            fixedEndOfStructure = handlePoint2,
            direction = norm_Expr(handlePoint1 - handlePoint2),
            sphereRadius = handleSphereRadius1, 
            range = (_resizeHandle_stopper_length, 10000)                               
        ))

    rightHandle = Instance( 
        NanotubeSegment_ResizeHandle(
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth2'),
            origin = handlePoint2,
            fixedEndOfStructure = handlePoint1,
            direction = norm_Expr(handlePoint2 - handlePoint1),
            sphereRadius = handleSphereRadius2,
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

        #Initialize DEBUG preference
        pref_nt_segment_resize_by_recreating_nanotube()
        return

    def init_gui(self):
        """
        Initialize gui. 
        """

        #Note that NanotubeSegment_EditCommand only act as an edit command for an 
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
        return

    def editStructure(self, struct = None):
        EditCommand.editStructure(self, struct)        
        if self.hasValidStructure():         
            #When the structure (segment) is finalized (after the  modifications)
            #it will be added to the original NanotubeGroup to which it belonged 
            #before we began editing (modifying) it. 
            self._parentNanotubeGroup = self.struct.getNanotubeGroup() 
            #Set the endpoints
            #@ DOES THIS DO ANYTHING? I don't think so. --Mark 2008-04-01
            #@endPoint1, endPoint2 = self.struct.nanotube.getEndPoints()
            #@params_for_propMgr = (endPoint1, endPoint2)

            #TODO 2008-03-25: better to get all parameters from self.struct and
            #set it in propMgr?  This will mostly work except that reverse is 
            #not true. i.e. we can not specify same set of params for 
            #self.struct.setProps ...because endPoint1 and endPoint2 are derived.
            #by the structure when needed. Commenting out following line of code
            self.propMgr.setParameters(self.struct.getProps())

            #Store the previous parameters. Important to set it after you 
            #set nanotube attrs in the propMgr. 
            #self.previousParams is used in self._previewStructure and 
            #self._finalizeStructure to check if self.struct changed.
            self.previousParams = self._gatherParameters()
            self._updateHandleList()
            self.updateHandlePositions()
        return

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
                elif group is self.struct.parent_node_of_class(self.assy.NanotubeGroup):
                    bool_keep = True
            #If this command doesn't have a valid structure, as a fall back, 
            #lets instruct it to keep ALL the NanotubeGroup objects even when empty
            #Reason? ..see explanation in BreakStrands_Command.keep_empty_group
            elif isinstance(group, self.assy.NanotubeGroup):
                bool_keep = True

        return bool_keep

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
        p1, p2 = self.struct.nanotube.getEndPoints()
        return (p1 is not None)

    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return self.win.assy.NanotubeSegment

    def _updateHandleList(self):
        """        
        Updates the list of handles (self.handles) 
        @see: self.editStructure
        @see: NanotubeSegment_GraphicsMode._drawHandles()
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
        return

    def updateHandlePositions(self):
        """
        Update handle positions and also update the resize handle radii and
        their 'stopper' lengths. 
        @see: self._update_resizeHandle_radius()
        @see: self._update_resizeHandle_stopper_length()
        @see: NanotubeSegment_GraphicsMode._drawHandles()
        """
        self.handlePoint1 = None # Needed!
        self.handlePoint2 = None

        #TODO: Call this method less often by implementing model_changed
        #see bug 2729 for a planned optimization
        self.cylinderWidth = CYLINDER_WIDTH_DEFAULT_VALUE
        self.cylinderWidth2 = CYLINDER_WIDTH_DEFAULT_VALUE      

        self._update_resizeHandle_radius()

        handlePoint1, handlePoint2 = self.struct.nanotube.getEndPoints()

        if 0: # Debug prints
            print "updateHandlePositions(): handlePoint1=", handlePoint1
            print "updateHandlePositions(): handlePoint2=", handlePoint2

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
        return

    def _update_resizeHandle_radius(self):
        """
        Finds out the sphere radius to use for the resize handles, based on 
        atom /chunk or glpane display (whichever decides the display of the end 
        atoms. The default value is 1.2.

        @see: self.updateHandlePositions()
        """
        self.handleSphereRadius1 = HANDLE_RADIUS_DEFAULT_VALUE
        self.handleSphereRadius2 = HANDLE_RADIUS_DEFAULT_VALUE
        return

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
        nanotubeRise = self.struct.nanotube.getRise()
        self._resizeHandle_stopper_length = - total_length + nanotubeRise
        return

    def _createPropMgrObject(self):
        """
        Creates a property manager object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = self.win.createNanotubeSegmentPropMgr_if_needed(self)
        return propMgr

    def _gatherParameters(self):
        """
        Return the parameters from the property manager UI.

        @return: The endpoints of the nanotube.
        @rtype:  tuple (endPoint1, endPoint2).
        """     
        return self.propMgr.getParameters()

    def _createStructure(self):
        """
        Creates and returns the structure (in this case a L{NanotubeSegment} 
        object. 
        @return : Nanotube segment that include the nanotube chunk.
        @rtype: L{NanotubeSegment}        
        """
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
        ntSegment = NanotubeSegment(self.name, 
                                    self.win.assy,
                                    self.win.assy.part.topnode,
                                    editCommand = self  )
        try:
            # Make the NanotubeSegment.

            n, m, type, endings, endPoint1, endPoint2 = self._gatherParameters()

            from cnt.model.Nanotube import Nanotube
            self.nanotube = Nanotube()
            nanotube  =  self.nanotube
            nanotube.setChirality(n, m)
            nanotube.setType(type)
            nanotube.setEndings(endings)
            nanotube.setEndPoints(endPoint1, endPoint2)
            position = V(0.0, 0.0, 0.0)
            ntChunk = nanotube.build(self.name, self.win.assy, position)

            nanotube.computeEndPointsFromChunk(ntChunk)

            ntSegment.addchild(ntChunk)

            #set some properties such as nanotubeRise
            #This information will be stored on the NanotubeSegment object so that
            #it can be retrieved while editing this object. 
            #Should these props be assigned to the NanotubeSegment in 
            #Nanotube.build() itself? This needs to be answered while modifying
            #build() method to fit in the dna data model. --Ninad 2008-03-05

            #WARNING 2008-03-05: Since self._modifyStructure calls 
            #self._createStructure() 
            #If in the near future, we actually permit modifying a
            #structure (such as dna) without actually recreating the whole 
            #structure, then the following properties must be set in 
            #self._modifyStructure as well. Needs more thought.
            props =(nanotube.getChirality(),
                    nanotube.getType(),
                    nanotube.getEndings(),
                    nanotube.getEndPoints())

            ntSegment.setProps(props)

            return ntSegment

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            ntSegment.kill()
            raise PluginBug("Internal error while trying to create a NanotubeSegment.")
        return

    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        """    
        if not pref_nt_segment_resize_by_recreating_nanotube():
            self._modifyStructure_NEW_SEGMENT_RESIZE(params)
            return

        assert self.struct
        # parameters have changed, update existing structure
        self._revertNumber()

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

        #@NOTE: Unlike editcommands such as Plane_EditCommand, this 
        #editCommand actually removes the structure and creates a new one 
        #when its modified. -- Ninad 2007-10-24

        self._removeStructure()

        self.previousParams = params

        self.struct = self._createStructure()
        # Now append the new structure in self._segmentList (this list of 
        # segments will be provided to the previous command 
        # (BuildDna_EditCommand)
        # TODO: Should self._createStructure does the job of appending the 
        # structure to the list of segments? This fixes bug 2599 
        # (see also BuildDna_PropertyManager.Ok 

        if self._parentNanotubeGroup is not None:
            #Should this be an assertion? (assert self._parentNanotubeGroup is not 
            #None. For now lets just print a warning if parentNanotubeGroup is None 
            self._parentNanotubeGroup.addSegment(self.struct)
        return  


    def _modifyStructure_NEW_SEGMENT_RESIZE(self, params): #@ NOT FIXED
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.

        @attention: is not implemented.
        """        

        #@TODO: - rename this method from _modifyStructure_NEW_SEGMENT_RESIZE
        #to self._modifyStructure, after more testing
        #This method is used for debug prefence: 
        #'Nanotube Segment: resize without recreating whole duplex'
        #see also self.modifyStructure_NEW_SEGMENT_RESIZE

        assert self.struct      

        from utilities.debug import print_compact_stack
        print_compact_stack("_modifyStructure_NEW_SEGMENT_RESIZE() not fixed!" )
        print "Params =", params

        self.nanotube = params #@

        length_diff =  self._determine_how_to_change_length() #@

        if length_diff == 0:
            print_compact_stack("BUG: length_diff is always ZERO." )
            return
        elif length_diff > 0:
            print "Nanotube longer by ", length_diff, ", angstroms."
        else:
            print "Nanotube shorter by ", length_diff, ", angstroms."

        return

        if numberOfBasePairsToAddOrRemove != 0:   #@@@@ Not reached.

            resizeEnd_final_position = self._get_resizeEnd_final_position(
                ladderEndAxisAtom, 
                abs(numberOfBasePairsToAddOrRemove),
                nanotubeRise )

            self.nanotube.modify(self.struct,
                                 length_diff,
                                 ladderEndAxisAtom.posn(),
                                 resizeEnd_final_position)

        #Find new end points of structure parameters after modification 
        #and set these values in the propMgr. 
        new_end1 , new_end2 = self.struct.nanotube.getEndPoints() #@

        params_to_set_in_propMgr = (new_end1,
                                    new_end2)

        #TODO: Need to set these params in the PM 
        #and then self.previousParams = params_to_set_in_propMgr

        self.previousParams = params
        return  

    def _get_resizeEnd_final_position(self, 
                                      ladderEndAxisAtom, 
                                      numberOfBases, 
                                      nanotubeRise):

        final_position = None   
        if self.grabbedHandle:
            final_position = self.grabbedHandle.currentPosition
        else:
            other_axisEndAtom = self.struct.getOtherAxisEndAtom(ladderEndAxisAtom)
            axis_vector = ladderEndAxisAtom.posn() - other_axisEndAtom.posn()
            segment_length_to_add = 0 #@
            final_position = ladderEndAxisAtom.posn() + norm(axis_vector)*segment_length_to_add

        return final_position

    def getStructureName(self):
        """
        Returns the name string of self.struct if there is a valid structure. 
        Otherwise returns None. This information is used by the name edit field 
        of  this command's PM when we call self.propMgr.show()
        @see: NanotubeSegment_PropertyManager.show()
        @see: self.setStructureName
        """
        if self.hasValidStructure():
            return self.struct.name
        return None

    def setStructureName(self, name):
        """
        Sets the name of self.struct to param <name> (if there is a valid 
        structure. 
        The PM of this command callss this method while closing itself 
        @param name: name of the structure to be set.
        @type name: string
        @see: NanotubeSegment_PropertyManager.close()
        @see: self.getStructureName()

        """
        #@BUG: We call this method in self.propMgr.close(). But propMgr.close() 
                #is called even when the command is 'cancelled'. That means the 
                #structure will get changed even when user hits cancel button or
                #exits the command by clicking on empty space. 
                #This should really be done in self._finalizeStructure but that 
                #method doesn't get called when you click on empty space to exit 
                #the command. See NanotubeSegment_GraphicsMode.leftUp for a detailed 
                #comment. 

        if self.hasValidStructure():
            self.struct.name = name
        return

    def getCursorText(self):
        """
        This is used as a callback method in NanotubeLine mode 
        @see: NanotubeLineMode.setParams, NanotubeLineMode_GM.Draw
        """
        if self.grabbedHandle is None:
            return
        
        text = ''
        textColor = env.prefs[cursorTextColor_prefs_key]
        
        if not env.prefs[nanotubeSegmentEditCommand_showCursorTextCheckBox_prefs_key]:
            return text, textColor

        currentPosition = self.grabbedHandle.currentPosition
        fixedEndOfStructure = self.grabbedHandle.fixedEndOfStructure

        nanotubeLength = vlen( currentPosition - fixedEndOfStructure )

        nanotubeLengthString = self._getCursorText_length(nanotubeLength)
        
        text = nanotubeLengthString
   
        #@TODO: The following updates the PM as the cursor moves. 
        #Need to rename this method so that you that it also does more things 
        #than just to return a textString -- Ninad 2007-12-20
        self.propMgr.ntLengthLineEdit.setText(nanotubeLengthString)

        return text, textColor
    
    def _getCursorText_length(self, nanotubeLength):
        """
        Returns a string that gives the length of the Nanotube for the cursor 
        text
        """
        nanotubeLengthString = ''
        if env.prefs[nanotubeSegmentEditCommand_cursorTextCheckBox_length_prefs_key]:
            lengthUnitString = 'A'
            #change the unit of length to nanometers if the length is > 10A
            #fixes part of bug 2856
            if nanotubeLength > 10.0:
                lengthUnitString = 'nm'
                nanotubeLength = nanotubeLength * 0.1
                
            nanotubeLengthString = "%5.3f%s"%(nanotubeLength, lengthUnitString)
        
        return nanotubeLengthString
    
    def modifyStructure(self):
        """
        Called when a resize handle is dragged to change the length of the 
        segment. (Called upon leftUp) . This method assigns the new parameters 
        for the segment after it is resized and calls 
        preview_or_finalize_structure which does the rest of the job. 
        Note that Client should call this public method and should never call
        the private method self._modifyStructure. self._modifyStructure is 
        called only by self.preview_or_finalize_structure

        @see: B{NanotubeSegment_ResizeHandle.on_release} (the caller)
        @see: B{SelectChunks_GraphicsMode.leftUp} (which calls the 
              the relevent method in DragHandler API. )
        @see: B{exprs.DraggableHandle_AlongLine}, B{exprs.DragBehavior}
        @see: B{self.preview_or_finalize_structure }
        @see: B{self._modifyStructure}        

        As of 2008-02-01 it recreates the structure
        @see: a note in self._createStructure() about use of ntSegment.setProps 
        """

        if not pref_nt_segment_resize_by_recreating_nanotube():
            self.modifyStructure_NEW_SEGMENT_RESIZE()
            return

        if self.grabbedHandle is None:
            return        

        self.propMgr.endPoint1 = self.grabbedHandle.fixedEndOfStructure
        self.propMgr.endPoint2 = self.grabbedHandle.currentPosition
        #@length = vlen(self.propMgr.endPoint1 - self.propMgr.endPoint2 ) #@  

        self.preview_or_finalize_structure(previewing = True)  

        self.updateHandlePositions()
        self.glpane.gl_update()
        return

    def modifyStructure_NEW_SEGMENT_RESIZE(self): #@ NOT FIXED
        """
        Called when a resize handle is dragged to change the length of the 
        segment. (Called upon leftUp) . This method assigns the new parameters 
        for the segment after it is resized and calls 
        preview_or_finalize_structure which does the rest of the job. 
        Note that Client should call this public method and should never call
        the private method self._modifyStructure. self._modifyStructure is 
        called only by self.preview_or_finalize_structure

        @see: B{NanotubeSegment_ResizeHandle.on_release} (the caller)
        @see: B{SelectChunks_GraphicsMode.leftUp} (which calls the 
              the relevent method in DragHandler API. )
        @see: B{exprs.DraggableHandle_AlongLine}, B{exprs.DragBehavior}
        @see: B{self.preview_or_finalize_structure }
        @see: B{self._modifyStructure}        

        As of 2008-02-01 it recreates the structure
        @see: a note in self._createStructure() about use of ntSegment.setProps 
        """
        #TODO: need to cleanup this and may be use use something like
        #self.previousParams = params in the end -- 2008-03-24 (midnight)


        #@TODO: - rename this method from modifyStructure_NEW_SEGMENT_RESIZE
        #to self.modifyStructure, after more testing
        #This method is used for debug prefence: 
        #'Nanotube Segment: resize without recreating whole duplex'
        #see also self._modifyStructure_NEW_SEGMENT_RESIZE

        if self.grabbedHandle is None:
            return   

        self.propMgr.endPoint1 = self.grabbedHandle.fixedEndOfStructure
        self.propMgr.endPoint2 = self.grabbedHandle.currentPosition

        DEBUG_DO_EVERYTHING_INSIDE_MODIFYSTRUCTURE_METHOD = False

        if DEBUG_DO_EVERYTHING_INSIDE_MODIFYSTRUCTURE_METHOD:

            # TO DO: this entire block of code.  --Mark 2008-04-03
            print_compact_stack("modifyStructure_NEW_SEGMENT_RESIZE(): NOT FIXED")

            length = vlen(self.grabbedHandle.fixedEndOfStructure - \
                          self.grabbedHandle.currentPosition )

            endAtom1, endAtom2 = self.struct.getAxisEndAtoms() #@

            for atm in (endAtom1, endAtom2):
                if not same_vals(self.grabbedHandle.fixedEndOfStructure, atm.posn()):
                    ladderEndAxisAtom = atm
                    break

                endPoint1, endPoint2 = self.struct.nanotube.getEndPoints()
                old_dulex_length = vlen(endPoint1 - endPoint2)

                nanotubeRise = self.struct.getProps()      #@ 

                params_to_set_in_propMgr = (
                    self.grabbedHandle.origin,
                    self.grabbedHandle.currentPosition,
                )

                ##self._modifyStructure(params)
                ############################################

                self.nanotube = Nanotube() #@ Creates 5x5 CNT. Miisng PM params.

                length_diff =  self._determine_how_to_change_length()  
                ladderEndAxisAtom = self.get_axisEndAtom_at_resize_end() #@

                #@ Nanotube class needs modify() method.
                self.nanotube.modify(self.struct, 
                                     length_diff,
                                     ladderEndAxisAtom.posn(),
                                     self.grabbedHandle.currentPosition)

        #TODO: Important note: How does NE1 know that structure is modified? 
        #Because number of base pairs parameter in the PropMgr changes as you 
        #drag the handle . This is done in self.getCursorText() ... not the 
        #right place to do it. OR that method needs to be renamed to reflect
        #this as suggested in that method -- Ninad 2008-03-25

        self.preview_or_finalize_structure(previewing = True) 

        ##self.previousParams = params_to_set_in_propMgr

        self.glpane.gl_update()
        return

    def get_axisEndAtom_at_resize_end(self):
        ladderEndAxisAtom = None
        if self.grabbedHandle is not None:
            ladderEndAxisAtom = self.struct.getAxisEndAtomAtPosition(self.grabbedHandle.origin)
        else:
            endAtom1, endAtom2 = self.struct.getAxisEndAtoms()
            ladderEndAxisAtom = endAtom2

        return ladderEndAxisAtom

    def _determine_how_to_change_length(self): #@ NEEDS WORK
        """
        Returns the difference in length between the original nanotube and the
        modified nanotube, where:
           0 = no change in length
         > 0 = lengthen
         < 0 = trim
        """
        nanotubeRise = self.struct.nanotube.getRise()
        endPoint1, endPoint2 = self.struct.nanotube.getEndPoints() #@ 
        original_nanotube_length = vlen(endPoint1 - endPoint2)
        new_nanotube_length      = vlen(endPoint1 - endPoint2) #@
        return new_nanotube_length - original_nanotube_length #@ ALWAYS RETURNS ZERO

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

            nanotubeGroup = self.struct.parent_node_of_class(self.assy.NanotubeGroup)
            if nanotubeGroup is None:
                return
            #following should be self.struct.getNanotubeGroup or self.struct.getNanotubeGroup
            #need to formalize method name and then make change.
            if not nanotubeGroup is highlightedChunk.parent_node_of_class(self.assy.NanotubeGroup):
                item = ("Edit unavailable: Member of a different NanotubeGroup",
                        noop, 'disabled')
                self.Menu_spec.append(item)
                return

        highlightedChunk.make_glpane_context_menu_items(self.Menu_spec,
                                                        command = self)
        return
