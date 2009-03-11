# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details.
"""
EditNanotube_GraphicsMode.py

Graphics mode for EditNanotube_EditCommand.

While in this command, user can
(a) Highlight and then left drag the resize handles located at the
    two 'endpoints' of the nanotube to change its length.
(b) Highlight and then left drag any nanotube atom to translate the nanotube
    segment along the axis

@author: Ninad, Mark
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created 2008-03-10 from copy of DnaSegment_GraphicsMode.py
Recreated 2008-04-02 from copy of DnaSegment_GraphicsMode.py
"""
from Numeric import dot
from PyQt4.Qt import QMouseEvent

from cnt.commands.BuildNanotube.BuildNanotube_GraphicsMode import BuildNanotube_GraphicsMode
from cnt.model.NanotubeSegment import NanotubeSegment


from graphics.drawing.drawNanotubeLadder import drawNanotubeLadder

import foundation.env as env

import math
from geometry.VQT import V, norm, A, Q, vlen
from utilities.constants import gray, black, darkred
from utilities.debug import print_compact_traceback

from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT

from model.chem import Atom
from model.bonds import Bond

SPHERE_RADIUS = 2.0
SPHERE_DRAWLEVEL = 2

from cnt.commands.BuildNanotube.BuildNanotube_GraphicsMode import DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND

_superclass = BuildNanotube_GraphicsMode

class EditNanotube_GraphicsMode(BuildNanotube_GraphicsMode):
    """
    Graphics mode for EditNanotube_EditCommand.
    """
    _sphereColor = darkred
    _sphereOpacity = 0.5

    #The flag that decides whether to draw the handles. This flag is
    #set during left dragging, when no handle is 'grabbed'. This optimizes the
    #drawing code as it skips handle drawing code and also the computation
    #of handle positions each time the mouse moves
    #@see self.leftUp , self.leftDrag, self.Draw_other for more details
    _handleDrawingRequested = True

    #Some left drag variables used to drag the whole segment along axis or
    #rotate the segment around its own axis of for free drag translation
    _movablesForLeftDrag = []

    #The common center is the center about which the list of movables (the segment
    #contents are rotated.
    #@see: self.leftADown where this is set.
    #@see: self.leftDrag where it is used.
    _commonCenterForRotation = None
    _axis_for_constrained_motion = None

    #Flags that decide the type of left drag.
    #@see: self.leftADown where it is set and self.leftDrag where these are used
    _translateAlongAxis = False
    _rotateAboutAxis = False
    _freeDragWholeStructure = False

    cursor_over_when_LMB_pressed = ''

    def Enter_GraphicsMode(self):
        _superclass.Enter_GraphicsMode(self)
        #Precaution
        self.clear_leftA_variables()
        return

    def bareMotion(self, event):
        """
        @see: self.update_cursor_for_no_MB
        """
        value = _superclass.bareMotion(self, event)

        #When the cursor is over a specific atom, we need to display
        #a different icon. (e.g. when over a strand atom, it should display
        # rotate cursor)
        self.update_cursor()

        return value

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for Select mode (Default implementation).
        """
        _superclass.update_cursor_for_no_MB(self)

        #minor optimization -- don't go further into the method if
        #nothing is highlighted i.e. self.o.selobj is None.
        if self.o.selobj is None:
            return

        if self.command and hasattr(self.command.struct, 'isAncestorOf'):
            if not self.command.struct.isAncestorOf(self.o.selobj):
                return

            if self.o.modkeys is None:
                if isinstance(self.o.selobj, Atom):
                    self.o.setCursor(self.win.translateAlongCentralAxisCursor)
                elif isinstance(self.o.selobj, Bond):
                    self.o.setCursor(self.win.TranslateSelectionCursor)
        return

    def leftDown(self, event):
        """
        """
        self.reset_drag_vars()

        self.clear_leftA_variables()

        obj = self.get_obj_under_cursor(event)

        if obj is None:
            self.cursor_over_when_LMB_pressed = 'Empty Space'

        #@see dn_model.NanotubeSegment.isAncestorOf.
        #It checks whether the object under the
        #cursor (which is glpane.selobj) is contained within the NanotubeSegment
        #currently being edited
        #Example: If the object is an Atom, it checks whether the
        #atoms is a part of the dna segment. *being edited*
        #(i.e. self.comman.struct). If its not (e.g. its an atom of another
        #dna segment, then the this method returns . (leftDrag on structures
        #NOT being edited won't do anything-- a desirable effect)
        if self.command and hasattr(self.command.struct, 'isAncestorOf'):
            if not self.command.struct.isAncestorOf(obj):
                _superclass.leftDown(self, event)
                return
            else:
                #Optimization: This value will be used in self.leftDrag.
                # Instead of checking everytime whether the
                #self.command.struct contains the highlighted objetc
                #(glpane.selobj)
                _superclass.leftDown(self, event)
                self.cursor_over_when_LMB_pressed = 'Structure Being Edited'

        self.LMB_press_event = QMouseEvent(event) # Make a copy of this event
        #and save it.
        # We will need it later if we change our mind and start selecting a 2D
        # region in leftDrag().Copying the event in this way is necessary
        #because Qt will overwrite  <event> later (in
        # leftDrag) if we simply set self.LMB_press_event = event.  mark 060220

        self.LMB_press_pt_xy = (event.pos().x(), event.pos().y())
        # <LMB_press_pt_xy> is the position of the mouse in window coordinates
        #when the LMB was pressed.
        #Used in mouse_within_stickiness_limit (called by leftDrag() and other
        #methods).
        # We don't bother to vertically flip y using self.height
        #(as mousepoints does),
        # since this is only used for drag distance within single drags.
        #Subclasses should override one of the following method if they need
        #to do additional things to prepare for dragging.
        self._leftDown_preparation_for_dragging(obj, event)
        return

    def clear_leftA_variables(self):
        self._movablesForLeftDrag = []
        self._commonCenterForRotation = None
        self._axis_for_constrained_motion = None
        _translateAlongAxis = False
        _rotateAboutAxis = False
        _freeDragWholeStructure = False
        return

    def _leftDown_preparation_for_dragging(self, objectUnderMouse, event):
        """
        Handle left down event. Preparation for rotation and/or selection
        This method is called inside of self.leftDown.
        @param event: The mouse left down event.
        @type  event: QMouseEvent instance
        @see: self.leftDown
        @see: self.leftDragRotation
        Overrides _superclass._leftDown_preparation_for_dragging
        """
        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
        self.leftADown(objectUnderMouse, event)
        return
    
    def leftADown(self, objectUnderMouse, event):
        """
        Method called during mouse left down . It sets some parameters
        necessary for rotating the structure around its own axis (during
        a left drag to follow) In graphics modes such as
        RotateChunks_GraphicsMode, rotating entities around their own axis is
        acheived by holding down 'A' key and then left dragging , thats why the
        method is named as 'leftADrag'  (A= Axis)
        """
        ma = V(0, 0, 0)

        if self.command and self.command.struct:
            ma = self.command.struct.getAxisVector()

        self._axis_for_constrained_motion = self.command.struct.getAxisVector()

        #@see: NanotubeSegment.get_all_content_chunks() for details about
        #what it returns. See also NanotubeSegment.isAncestorOf() which
        #is called in self.leftDown to determine whether the NanotubeSegment
        #user is editing is an ancestor of the selobj. (it also considers
        #'logical contents' while determining whether it is an ancestor.
        #-- Ninad 2008-03-11
        self._movablesForLeftDrag = self.command.struct.get_all_content_chunks()

        ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))

        self.Zmat = A([ma,[-ma[1],ma[0]]])

        obj = objectUnderMouse

        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            #Left A drag is not possible unless the cursor is over a
            #selected object. So make sure to let self.leftAError method sets
            #proper flag so that left-A drag won't be done in this case.
            return

        if isinstance(obj, Atom):
            self._translateAlongAxis = True
            self._rotateAboutAxis = False
            self._freeDragWholeStructure = False
        elif 0: #@@@ isinstance(obj, Atom): # Rotate about axis not supported.
            self._translateAlongAxis = False
            self._rotateAboutAxis = True
            self._freeDragWholeStructure = False
            #The self._commonCenterForrotation is a point on segment axis
            #about which the whole segment will be rotated. Specifying this
            #as a common center  for rotation fixes bug 2578. We determine this
            #by selecting the center of the axis atom that is connected
            #(bonded) to the strand atom being left dragged. Using this as a
            #common center instead of the avaraging the center of the segment
            #axis atoms has an advantage. We compute the rotation offset 'dy'
            #with reference to the strand atom being dragged, so it seems more
            #appropriate to use the nearest axis center for segment rotation
            #about axis. But what happens if the axis is not straigt but is
            #curved? Should we select the averaged center of all axis atoms?
            #..that may not be right. Or should we take _average center_ of
            #a the following axis atoms --strand atoms axis_neighbors and
            #axis atom centers directly connected to this axis atom.
            #  -- Ninad 2008-03-25
            self._commonCenterForRotation = obj.axis_neighbor().posn()
        elif isinstance(obj, Bond):
            self._translateAlongAxis = False
            self._rotateAboutAxis = False
            self._freeDragWholeStructure = True

        self.o.SaveMouse(event)
        self.dragdist = 0.0
        return

    def leftUp(self, event):
        """
        Method called during Left up event.
        """
        _superclass.leftUp(self, event)
        self.update_selobj(event)
        self.update_cursor()
        self.o.gl_update()

        #Reset the flag that decides whether to draw the handles. This flag is
        #set during left dragging, when no handle is 'grabbed'. See the
        #class definition for more details about this flag.
        if self.command and self.command.handles:
            if not self._handleDrawingRequested:
                self._handleDrawingRequested = True
                pass
            pass
        return
    
    def leftDrag(self, event):
        """
        Method called during Left drag event.
        """
        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            # [let this happen even for drag_handlers -- bruce 060728]
            return

        self.current_obj_clicked = False

        #If there is a drag handler (e.g. a segment resize handle is being
        #dragged, call its drag method and don't proceed further.

        #NOTE:
        #In SelectChunks_GraphicsMode.leftDrag, there is a condition statement
        #which checks if self.drag_handler is in assy.getSelecteedMovables
        #I don't know why it does that... I think it always assums that the
        #drag handler is officially a node in the MT? In our case,
        #the drag handler is a 'Highlightable' object (actually
        #an instance of 'EditNanotube_ResizeHandle' (has superclass from
        #exprs module ..which implements API for a highlightable object
        #So it doesn't get registered in the selectMovables list. Thats why
        #we are not calling _superclass.leftDrag. The above mentioned
        #method in the superclass needs to be revised -- Ninad 2008-02-01

        if self.drag_handler is not None:
            self.dragHandlerDrag(self.drag_handler, event)
            return

        #If the cursor was not over something that belonged to structure
        #being edited (example - atom or bond of a differnt NanotubeSegment)
        #don't do left drag.(left drag will work only for the NanotubeSegment
        #eing edited)
        if self.cursor_over_when_LMB_pressed != 'Structure Being Edited':
            return

        #Duplicates some code from SelectChunks_GraphicsMode.leftDrag
        #see a to do comment below in this method
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftDrag(event)
            return

        if self.o.modkeys is not None:
            # If a drag event has happened after the cursor was over an atom
            # and a modkey is pressed, do a 2D region selection as if the
            # atom were absent.
            self.emptySpaceLeftDown(self.LMB_press_event)
            #bruce 060721 question: why don't we also do emptySpaceLeftDrag
            # at this point?
            return

        #TODO: This duplicates some code from SelectChunks_GraphicsMode.leftDrag

        #Following code will never be called if a handle is grabbed.
        #Thus, it instructs what to do for other cases (when user is not moving
        #the draggable handles)

        #First, don't draw handles (set the flag here so that self.Draw_other knows
        #not to draw handles) This skips unnecessary computation of new handle
        #position during left dragging. The flag is reset to True in leftUp
        if self.command and self.command.handles:
            if self.command.grabbedHandle is None:
                self._handleDrawingRequested = False

        #Copies AND modifies some code from Move_GraphicsMode for doing
        #leftDrag translation or rotation.

        w = self.o.width + 0.0
        h = self.o.height + 0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())

        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w)

        offset = None

        if self._translateAlongAxis:
            offset = dx * self._axis_for_constrained_motion
            for mol in self._movablesForLeftDrag:
                mol.move(offset)

        if self._rotateAboutAxis:
            rotation_quat = Q(self._axis_for_constrained_motion, -dy)
            self.o.assy.rotateSpecifiedMovables(
                rotation_quat,
                movables = self._movablesForLeftDrag,
                commonCenter = self._commonCenterForRotation )

        if self._freeDragWholeStructure:
            try:
                point = self.dragto( self.movingPoint, event)
                offset = point - self.movingPoint
                self.o.assy.translateSpecifiedMovables(offset,
                                                       movables = self._movablesForLeftDrag)
                self.movingPoint = point
            except:
                #may be self.movingPoint is not defined in leftDown?
                #(e.g. _superclass.leftDown doesn't get called or as a bug? )
                print_compact_traceback("bug:unable to free drag the whole segment")

        if offset: # Update the nanotube endpoints.
            endPt1, endPt2 = self.command.struct.nanotube.getEndPoints()
            endPt1 += offset
            endPt2 += offset
            self.command.struct.nanotube.setEndPoints(endPt1, endPt2)

        self.dragdist += vlen(deltaMouse) #k needed?? [bruce 070605 comment]

        self.o.SaveMouse(event)
        self.o.assy.changed() #ninad060924 fixed bug 2278
        self.o.gl_update()
        return

    def drawHighlightedChunk(self, glpane, selobj, hicolor, hicolor2):
        """
        [overrides SelectChunks_basicGraphicsMode method]
        """
        # bruce 071008 (intending to be equivalent to prior code)
        return False

    def Draw_other(self):
        """
        """
        _superclass.Draw_other(self)
        if self._handleDrawingRequested:
            self._drawHandles()
        return

    def _drawHandles(self):
        """
        Draw the handles for the command.struct
        """
        if 0: #self.command and self.command.hasValidStructure():
            for handle in self.command.handles:
                handle.draw()

        if self.command and self.command.hasValidStructure():
            for handle in self.command.handles:
                if handle.hasValidParamsForDrawing():
                    handle.draw()

        handleType = ''
        if self.command.grabbedHandle is not None:
            if self.command.grabbedHandle in [self.command.rotationHandle1,
                                              self.command.rotationHandle2]:
                handleType = 'ROTATION_HANDLE'
            else:
                handleType = 'RESIZE_HANDLE'

        # self.command.struct is (temporarily?) None after a nanotube segment
        # has been resized. This causes a trackback. This seems to fix it.
        # --Mark 2008-04-01
        if not self.command.struct:
            return

        if handleType and handleType == 'RESIZE_HANDLE':

            #use self.glpane.displayMode for rubberbandline displayMode
            drawNanotubeLadder(self.command.grabbedHandle.fixedEndOfStructure,
                          self.command.grabbedHandle.currentPosition,
                          self.command.struct.nanotube.getRise(),
                          self.glpane.scale,
                          self.glpane.lineOfSight,
                          ladderWidth = self.command.struct.nanotube.getDiameter(),
                          beamThickness = 4.0,
                          beam1Color = gray,
                          beam2Color = gray,
                          )

            self._drawCursorText()
        else:
            #No handle is grabbed. But may be the structure changed
            #(e.g. while dragging it ) and as a result, the endPoint positions
            #are modified. So we must update the handle positions because
            #during left drag (when handle is not dragged) we skip the
            #handle drawing code and computation to update the handle positions
            #TODO: see bug 2729 for planned optimization
            self.command.updateHandlePositions()
        return
    pass
