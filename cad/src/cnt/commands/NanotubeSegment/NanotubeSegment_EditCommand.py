# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
NanotubeSegment_EditCommand.py

@author: Ninad, Mark
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

While in this command, user can 
(a) Highlight and then left drag the resize handles located at the 
    two 'endpoints' of the nanotube to change its length.  
(b) Highlight and then left drag any nanotube atom to translate the 
    nanotube along its axis.

History:
Mark 2008-03-10: Created from copy of DnaSegment_EditCommand.py
"""

import foundation.env as env
from command_support.EditCommand       import EditCommand 
from utilities.exception_classes import PluginBug, UserError
from geometry.VQT import V, vlen
from geometry.VQT import cross, norm
from utilities.constants  import gensym
from exprs.State_preMixin import State_preMixin
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

from utilities.debug import print_compact_stack

from graphics.drawables.RotationHandle  import RotationHandle

from cnt.model.NanotubeSegment               import NanotubeSegment

from cnt.commands.NanotubeSegment.NanotubeSegment_ResizeHandle import NanotubeSegment_ResizeHandle
from cnt.commands.NanotubeSegment.NanotubeSegment_GraphicsMode import NanotubeSegment_GraphicsMode

from utilities.prefs_constants import nanotubeSegmentEditCommand_cursorTextCheckBox_length_prefs_key
from utilities.prefs_constants import nanotubeSegmentEditCommand_showCursorTextCheckBox_prefs_key
from utilities.prefs_constants import cursorTextColor_prefs_key

from cnt.commands.NanotubeSegment.NanotubeSegment_PropertyManager import NanotubeSegment_PropertyManager

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
    Command to edit a NanotubeSegment (nanotube).
    """
    # class constants
    GraphicsMode_class = NanotubeSegment_GraphicsMode
    PM_class = NanotubeSegment_PropertyManager
    
    commandName      = 'NANOTUBE_SEGMENT'
    featurename      = "Edit Nanotube Segment"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_NANOTUBE'
    
    command_should_resume_prevMode = True
    command_has_its_own_PM = True
    
    flyoutToolbar = None

    call_makeMenus_for_each_event = True 

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

    def __init__(self, commandSequencer):
        """
        Constructor for InsertDna_EditCommand
        """
        glpane = commandSequencer.assy.glpane
        State_preMixin.__init__(self, glpane)        
        EditCommand.__init__(self, commandSequencer)
        
        #Graphics handles for editing the structure . 
        self.handles = []        
        self.grabbedHandle = None

        #Initialize DEBUG preference
        pref_nt_segment_resize_by_recreating_nanotube()
        return
    
    def editStructure(self, struct = None):
        EditCommand.editStructure(self, struct)        
        if self.hasValidStructure():

            #TODO 2008-03-25: better to get all parameters from self.struct and
            #set it in propMgr?  This will mostly work except that reverse is 
            #not true. i.e. we can not specify same set of params for 
            #self.struct.setProps ...because endPoint1 and endPoint2 are derived.
            #by the structure when needed.
            self.propMgr.setParameters(self.struct.getProps())

            #Store the previous parameters. Important to set it after you 
            #set nanotube attrs in the propMgr. 
            #self.previousParams is used in self._previewStructure and 
            #self._finalizeStructure to check if self.struct changed.
            self.previousParams = self._gatherParameters()
            self._updateHandleList()
            self.updateHandlePositions()
        return

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
        structure and creates a new one using self._createStructure.
        """    
        if not pref_nt_segment_resize_by_recreating_nanotube():
            self._modifyStructure_NEW_SEGMENT_RESIZE(params)
            return

        assert self.struct
        self.name = self.struct.name # Preserve name before removing struct.
        self._removeStructure()
        self.previousParams = params
        self.struct = self._createStructure()
        return  

    def _modifyStructure_NEW_SEGMENT_RESIZE(self, params): #@ NOT FIXED
        """
        This resizes without recreating whole nanotube 
        Overrides EditCommand._modifystructure.
        @attention: is not implemented.
        """        

        #@TODO: - rename this method from _modifyStructure_NEW_SEGMENT_RESIZE
        #to self._modifyStructure, after more testing
        #This method is used for debug prefence: 
        #'Nanotube Segment: resize without recreating whole nanotube'
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
        of this command's PM when we call self.propMgr.show()
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

        highlightedChunk.make_glpane_context_menu_items(self.Menu_spec,
                                                        command = self)
        return
