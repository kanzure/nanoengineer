# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2008-01-25: Split modifyMode into Commmand and GraphicsMode classes
                  and also refactored the GraphicsMode to create indiviudal
                  classes rotating and tranlating selected entities.
                  (called RotateChunks_GraphicsMode and
                   TranslateChunks_GraphicsMode)

TODO: [as of 2008-01-25]
The class TranslateChunks_GraphicsMode may be renamed to
Translate_GraphicsMode or TranslateComponents_GraphicsMode.
"""
from utilities import debug_flags
import math
from numpy import dot
import foundation.env as env
from utilities.debug import print_compact_traceback
from geometry.VQT import V, A, vlen, norm
from commands.Move.Move_GraphicsMode import Move_GraphicsMode

_superclass = Move_GraphicsMode

class TranslateChunks_GraphicsMode(Move_GraphicsMode):
    """
    Provides Graphics Mode for translating objects such as chunks.
    """
    # class variables
    moveOption = 'MOVEDEFAULT'

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for 'Rotate Chunks' Graphics Mode
        """
        if self.o.modkeys is None:
            if self.isConstrainedDragAlongAxis:
                self.o.setCursor(self.w.AxisTranslateRotateSelectionCursor)
            else:
                self.o.setCursor(self.w.TranslateSelectionCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.TranslateSelectionAddCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.TranslateSelectionSubtractCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys

        return

    def _leftDown_preparation_for_dragging(self, objectUnderMouse, event):
        """
        Handle left down event. Preparation for translation and/or selection
        This method is called inside of self.leftDown.
        @param event: The mouse left down event.
        @type  event: QMouseEvent instance
        @see: self.leftDown
        @see: self.leftDragTranslation
        Overrides _superclass._leftDown_preparation_for_dragging
        """
        _superclass._leftDown_preparation_for_dragging(self, objectUnderMouse, event)

        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        self.transDelta = 0 # X, Y or Z deltas for translate.
        self.moveOffset = [0.0, 0.0, 0.0] # X, Y and Z offset for move.

        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
        # Following is in leftDrag() to compute move offset during drag op.
        self.startpt = self.movingPoint

        # Translate section

        if self.moveOption != 'MOVEDEFAULT':
            if self.moveOption == 'TRANSX':
                ma = V(1,0,0) # X Axis
                self.axis = 'X'
            elif self.moveOption == 'TRANSY':
                ma = V(0,1,0) # Y Axis
                self.axis = 'Y'
            elif self.moveOption == 'TRANSZ':
                ma = V(0,0,1) # Z Axis
                self.axis = 'Z'
            elif self.moveOption == 'ROT_TRANS_ALONG_AXIS':
                #The method 'self._leftDown_preparation_for_dragging should
                #never be reached if self.moveOption is 'ROT_TRANS_ALONG_AXIS'
                #If this code is reached, it indicates a bug. So fail gracefully
                #by calling self.leftADown()
                if debug_flags.atom_debug:
                    print_compact_stack("bug: _leftDown_preparation_for_dragging"\
                                        " called for translate option"\
                                        "'ROT_TRANS_ALONG_AXIS'")
                self.leftADown(objectUnderMouse, event)
                return
            else:
                print "TranslateChunks_GraphicsMode Error - "\
                      "unknown moveOption value =", self.moveOption

            ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
            # When in the front view, right = 1,0,0 and up = 0,1,0, so ma will
            #be computed as 0,0.
            # This creates a special case problem when the user wants to
            #constrain rotation around
            # the Z axis because Zmat will be zero.  So we have to test for
            #this case (ma = 0,0) and
            # fix ma to -1,0.  This was needed to fix bug 537.  Mark 050420
            if ma[0] == 0.0 and ma[1] == 0.0: ma = [-1.0, 0.0]
            self.Zmat = A([ma,[-ma[1],ma[0]]])

            # end of Translate section

        self.leftDownType = 'TRANSLATE'

        return

    def leftDrag(self, event):
        """
        Translate the selected object(s):
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

        if self.leftDownType in ['TRANSLATE', 'A_TRANSLATE']:
            try:
                self.leftDragTranslation(event)
                return
            except:
                msg1 = "Controlled translation not allowed. "
                msg2 = "Key must be pressed before starting the drag"
                env.history.statusbar_msg(msg1 + msg2)
                if debug_flags.atom_debug:
                    msg3 = "Error occured in "\
                         "TranslateChunks_GraphicsMode.leftDragTranslation."
                    msg4 = "Possibly due to a key press that activated. "
                    msg5 = "Rotate groupbox. Aborting drag operation"
                    print_compact_traceback(msg3 + msg4 + msg5)

    def leftADown(self, objectUnderMouse, event):
        """
        """
        _superclass.leftADown(self, objectUnderMouse, event)
        self.leftDownType = 'A_TRANSLATE'

    def leftDragTranslation(self, event):
        """
        Translate the selected object(s):
        - in the plane of the screen following the mouse,
        - or slide and rotate along the an axis

        @param event: The mouse left drag event.
        @see: self.leftDrag()
        @see: self._leftDragFreeTranslation()
        @see: self._leftDragConstrainedTranslation()
        """
        #TODO: Further cleanup of this method and also for
        # _superclass.leftDragTranslation. Need to move some common code
        #in this method to self.leftDrag. Lower priority -- ninad 20070727

        if self.command and self.command.propMgr and \
           hasattr(self.command.propMgr, "translateComboBox"):
            if self.command.propMgr.translateComboBox.currentText() != "Free Drag":
                return

        # Fixes bugs 583 and 674 along with change in keyRelease.  Mark 050623
        # Fix per Bruce's email.  Mark 050704
        if self.movingPoint is None:
            self.leftDown(event)

        if self.moveOption == 'ROT_TRANS_ALONG_AXIS':
            try:
                self.leftADrag(event)
            except:
                print_compact_traceback(" error doing leftADrag")
            return
        # Move section
        if self.moveOption == 'MOVEDEFAULT':
            self._leftDragFreeTranslation(event)
            return
            # end of Move section

        self._leftDragConstrainedTranslation(event)
        return

    def _leftDragConstrainedTranslation(self, event):
        """
        Constrained translation during the left drag.
        @see: self.leftDragTranslation()
        @see: self._leftDragFreeTranslation()
        """
        # Constrained translation
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w)
        if self.moveOption == 'TRANSX':
            ma = V(1,0,0) # X Axis
        elif self.moveOption == 'TRANSY':
            ma = V(0,1,0) # Y Axis
        elif self.moveOption == 'TRANSZ':
            ma = V(0,0,1) # Z Axis
        else:
            print "_leftDragConstrainedTranslation Error: unknown moveOption value:", \
                  self.moveOption
            return

        self.transDelta += dx # Increment translation delta
        self.win.assy.translateSpecifiedMovables(dx*ma,
                                                 movables = self._leftDrag_movables)

        # Print status bar msg indicating the current translation delta
        if self.o.assy.selmols:
            msg = "%s delta: [%.2f Angstroms] [0 Degrees]" % (self.axis,
                                                              self.transDelta)
            env.history.statusbar_msg(msg)

        # common finished code
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()

        return


