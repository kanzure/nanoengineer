# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2008-01-25: Split the former 'modifyMode ' 
                  into Commmand and GraphicsMode classes
                  and also refactored the GraphicsMode to create indiviudal
                  classes for rotating and translating selected entities.
                  (called RotateChunks_GraphicsMode and
                  TranslateChunks_GraphicsMode)

TODO: [as of 2008-01-25]
The class RotateChunks_GraphicsMode may be renamed to something like
Rotate_GraphicsMode or RotateComponents_GraphicsMode.  The former name
conflicts with the 'RotateMode'.

"""
from utilities import debug_flags
import math
from Numeric import dot, sign
import foundation.env as env
from utilities.Log import redmsg
from utilities.debug import print_compact_stack

from utilities.debug import print_compact_traceback
from geometry.VQT import V, Q, A, vlen, norm
from commands.Move.Move_GraphicsMode import Move_GraphicsMode

_superclass = Move_GraphicsMode

class RotateChunks_GraphicsMode(Move_GraphicsMode):
    """
    Provides Graphics Mode forrotating objects such as chunks.
    """

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for 'Rotate Chunks' Graphics mode
        """
        if self.o.modkeys is None:
            if self.isConstrainedDragAlongAxis:
                self.o.setCursor(self.w.AxisTranslateRotateSelectionCursor)
            else:
                self.o.setCursor(self.w.RotateSelectionCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.RotateSelectionAddCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.RotateSelectionSubtractCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys

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

        _superclass._leftDown_preparation_for_dragging(self, objectUnderMouse, event)
        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        # delta for constrained rotations.
        self.rotDelta = 0

        if self.rotateOption == 'ROTATEDEFAULT':
            self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        else:
            if self.rotateOption == 'ROTATEX':
                ma = V(1,0,0) # X Axis
                self.axis = 'X'
            elif self.rotateOption == 'ROTATEY':
                ma = V(0,1,0) # Y Axis
                self.axis = 'Y'
            elif self.rotateOption == 'ROTATEZ':
                ma = V(0,0,1) # Z Axis
                self.axis = 'Z'
            elif self.rotateOption == 'ROT_TRANS_ALONG_AXIS':
                #The method 'self._leftDown_preparation_for_dragging should
                #never be reached if self.rotateOption is 'ROT_TRANS_ALONG_AXIS'
                #If this code is reached, it indicates a bug. So fail gracefully
                #by calling self.leftADown()
                if debug_flags.atom_debug:
                    print_compact_stack("bug: _leftDown_preparation_for_dragging"\
                                        " called for rotate option"\
                                        "'ROT_TRANS_ALONG_AXIS'")

                self.leftADown(objectUnderMouse, event)
                return

            else:
                print "Move_Command: Error - unknown rotateOption value =", \
                      self.rotateOption
                return

            ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
            # When in the front view, right = 1,0,0 and up = 0,1,0, so ma will
            # be computed as 0,0.This creates a special case problem when the
            # user wants to constrain rotation around the Z axis because Zmat
            # will be zero.  So we have to test for this case (ma = 0,0) and
            # fix ma to -1,0.  This was needed to fix bug 537.  Mark 050420
            if ma[0] == 0.0 and ma[1] == 0.0:
                ma = [-1.0, 0.0]
            self.Zmat = A([ma,[-ma[1],ma[0]]])

        self.leftDownType = 'ROTATE'

        return

    def leftDrag(self, event):
        """
        Rotate the selected object(s):
        - in the plane of the screen following the mouse,
        - or slide and rotate along the an axis

        @param event: The mouse left drag event.
        @type  event: QMouseEvent instance
        """
        _superclass.leftDrag(self, event)

        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            #The _superclass.leftDrag considers this condition.
            #So simply return and don't go further. Fixes bug 2607
            return

        if self.leftDownType in ['ROTATE', 'A_ROTATE']:
            try:
                self.leftDragRotation(event)
                return
            except:
                msg1 = "Controlled rotation not allowed. "
                msg2 = "Key must be pressed before starting the drag"
                env.history.statusbar_msg(msg1 + msg2)
                if debug_flags.atom_debug:
                    msg3 = "Error occured in Move_Command.leftDragRotation."
                    msg4 = "Possibly due to a key press that activated. "
                    msg5 = "Translate groupbox. Aborting drag operation"
                    print_compact_traceback(msg3 + msg4 + msg5)

    def leftDragRotation(self, event):
        """
        Rotate the selected object(s) or slide and rotate along the an axis

        @param event: The mouse left drag event.
        @type  event: QMouseEvent object
        @see : self.leftDrag
        """

        if self.command and self.command.propMgr and \
           hasattr(self.command.propMgr, 'rotateComboBox'):
            if self.command.propMgr.rotateComboBox.currentText() != "Free Drag":
                return

        if self.rotateOption == 'ROTATEDEFAULT':
            self.leftDragFreeRotation(event)
            return

        if self.rotateOption == 'ROT_TRANS_ALONG_AXIS':
            try:
                self.leftADrag(event)
            except:
                print_compact_traceback(" error doing leftADrag")

            return

        #Rotate section
        w=self.o.width+0.0
        h=self.o.height+0.0

        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())

        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w)

        if self.rotateOption == 'ROTATEX':
            ma = V(1,0,0) # X Axis
        elif self.rotateOption == 'ROTATEY':
            ma = V(0,1,0) # Y Axis
        elif self.rotateOption == 'ROTATEZ':
            ma = V(0,0,1) # Z Axis
        else:
            print "rotateChunks_GraphicsMode.leftDrag Error: unknown rotateOption value:",\
                  self.rotateOption
            return

        qrot = Q(ma,-dy) # Quat for rotation delta.
        # Increment rotation delta (and convert to degrees)
        self.rotDelta += qrot.angle *180.0/math.pi * sign(dy)

        if self.command and self.command.propMgr and \
           hasattr(self.command.propMgr, 'updateRotationDeltaLabels'):
            self.command.propMgr.updateRotationDeltaLabels(self.rotateOption,
                                                   self.rotDelta)

        self.win.assy.rotateSpecifiedMovables(qrot,
                                              movables = self._leftDrag_movables)

        # Print status bar msg indicating the current rotation delta.
        if self.o.assy.selmols:
            msg = "%s delta: [0 Angstroms] [%.2f Degrees]" % (self.axis,
                                                              self.rotDelta)
            env.history.statusbar_msg(msg)

        # common finished code
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()

        #End of Rotate Section
        return

    def leftDragFreeRotation(self, event):
        """
        Does an incremental trackball action (free drag rotation)on all selected
        movables.

        @param event: The mouse left drag event.
        @type  event: QMouseEvent instance
        @see : self.leftDragRotation

        """

        selectedMovables = self._leftDrag_movables

        if not selectedMovables:
            # This should never happen (i.e. the method self._leftDragFreeRotation
            # should be called only when movable entities are selected)
            # This is just a safety check.
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return

        #Note: In Alpha 9.1 and before, this operation was done by leftCntlDrag
        #Now, leftCntlDrag is used for 'subtract from selection' which is
        #consistent with the default mode (selectMols mode)- ninad 20070802
        w = self.o.width + 0.0
        h = self.o.height + 0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1],
                                    self.o.quat)

        if self.command and self.command.propMgr and \
           hasattr(self.command.propMgr, 'rotateComboBox'):
            if self.command.propMgr.rotateAsUnitCB.isChecked():
                self.win.assy.rotateSpecifiedMovables(q,
                                              movables = self._leftDrag_movables) # Rotate the selection as a unit.
            else:
                #Following fixes bug 2521
                for item in selectedMovables:
                    try:
                        item.rot(q)
                    except AssertionError:
                        print_compact_traceback("Selected movable doesn't have"\
                                                "rot method?")
            self.o.gl_update()
            return

        #By default always rotate the selection as a unit (this code will
        #never be reached if the command's propMgr has a 'rotateAsaUnit'
        #checkbox )
        self.win.assy.rotateSpecifiedMovables(q,
                                              movables = self._leftDrag_movables)

        self.o.gl_update()

    def leftADown(self, objectUnderMouse, event):
        """
        Set up for sliding and/or rotating the selected chunk(s)
        along/around its own axis when left mouse and key 'A' is pressed.
        Overrides _sperclass.leftADown
        @see: Move_GraphicsMode.leftADown
        """
        _superclass.leftADown(self, objectUnderMouse, event)
        self.leftDownType = 'A_ROTATE'

