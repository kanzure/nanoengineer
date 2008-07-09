# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
Graphics mode intended to be used while in DnaSegment_EditCommand.
While in this command, user can
(a) Highlight and then left drag the resize handles located at the
    two 'axis endpoints' of thje segment to change its length.
(b) Highlight and then left drag any axis atom (except the two end axis atoms)
    to translate the  whole segment along the axis
(c) Highlight and then left drag any strand atom to rotate the segment around
    its axis.

    Note that implementation b and c may change slightly if we implement special
    handles to do these oprations.

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created 2008-01-25

TODO: as of 2008-02-01:
- This graphics mode uses some duplicated code from Move_GraphicsMode
(for rotating or translating about own axis .. its a small portion and simpler
to understand) and also from DnaLine_GM (mainly the drawing code).
Ideally, it should switch to these graphics modes while remaining in the same
command (using command.switchGraphicsModeTo method) But it poses problems.
Issues related to use of DnaLine_GM are mentioned in DnaSegment_EditCommand.
In future, we may need to incorporate more functionality from these graphics
modes so this should be refactored then.

- Need to review methods in self.leftDrag and self.leftDown ..there might be
 some bugs...not sure.

"""

import foundation.env as env
from dna.commands.BuildDna.BuildDna_GraphicsMode import BuildDna_GraphicsMode
from graphics.drawing.drawDnaRibbons import drawDnaRibbons
from graphics.drawing.CS_draw_primitives import drawcylinder
from utilities.constants import darkred, black, orange
from model.chem import Atom
from utilities.prefs_constants import dnaSegmentResizeHandle_discRadius_prefs_key
from utilities.prefs_constants import dnaSegmentResizeHandle_discThickness_prefs_key

from geometry.VQT import norm

SPHERE_RADIUS = 2.0
SPHERE_DRAWLEVEL = 2

_superclass = BuildDna_GraphicsMode

class DnaSegment_GraphicsMode(BuildDna_GraphicsMode):
    """
    Graphics mode for DnaSegment_EditCommand.
    """
    _sphereColor = darkred
    _sphereOpacity = 0.5

    #The flag that decides whether to draw the handles. This flag is
    #set during left dragging, when no handle is 'grabbed'. This optimizes the
    #drawing code as it skips handle drawing code and also the computation
    #of handle positions each time the mouse moves
    #@see self.leftUp , self.leftDrag, seld.Draw for more details
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

    def bareMotion(self, event):
        """
        @see: self.update_cursor_for_no_MB
        """
        value = _superclass.bareMotion(self, event)

        #When the cursor is over a specifit atom, we need to display
        #a different icon. (e.g. when over a strand atom, it should display
        # rotate cursor)
        self.update_cursor()

        return value # russ 080527

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
                    if self.o.selobj.element.role == 'strand':
                        self.o.setCursor(self.win.rotateAboutCentralAxisCursor)
                    else:
                        self.o.setCursor(self.win.translateAlongCentralAxisCursor)


    def clear_leftA_variables(self):
        self._movablesForLeftDrag = []
        self._commonCenterForRotation = None
        self._axis_for_constrained_motion = None
        _translateAlongAxis = False
        _rotateAboutAxis = False
        _freeDragWholeStructure = False

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

    def Draw(self):
        """
        Draw glpane contents and its contents including handles (if any.) of
        DnaSegment
        @see:self._drawCursorText()
        @see:self._drawHandles()
        """
        _superclass.Draw(self)
        if self._handleDrawingRequested:
            self._drawHandles()


    def _drawHandles(self):
        """
        Draw the handles for the command.struct
        @see: DnaSegment_EditCommand.getDnaRibbonParams()
        @see:self._drawCursorText()
        @see:self.Draw()
        """
        if self.command and self.command.hasValidStructure():
            for handle in self.command.handles:
                if handle.hasValidParamsForDrawing():
                    handle.draw()

            self._drawDnaRubberbandLine()


    def _drawDnaRubberbandLine(self):

        handleType = ''
        if self.command.grabbedHandle is not None:
            if self.command.grabbedHandle in [self.command.rotationHandle1,
                                              self.command.rotationHandle2]:
                handleType = 'ROTATION_HANDLE'
            else:
                handleType = 'RESIZE_HANDLE'

        if handleType and handleType == 'RESIZE_HANDLE':

            params = self.command.getDnaRibbonParams()
            if params:
                end1, end2, basesPerTurn, duplexRise, ribbon1_start_point, \
                    ribbon2_start_point, ribbon1_direction, ribbon2_direction,\
                    ribbon1Color, ribbon2Color = params


                #Note: The displayStyle argument for the rubberband line should
                #really be obtained from self.command.struct. But the struct
                #is a DnaSegment (a Group) and doesn't have attr 'display'
                #Should we then obtain this information from one of its strandChunks?
                #but what if two strand chunks and axis chunk are rendered
                #in different display styles? since situation may vary, lets
                #use self.glpane.displayMode for rubberbandline displayMode
                drawDnaRibbons(self.glpane,
                               end1,
                               end2,
                               basesPerTurn,
                               duplexRise,
                               self.glpane.scale,
                               self.glpane.lineOfSight,
                               self.glpane.displayMode,
                               ribbonThickness = 4.0,
                               ribbon1_start_point = ribbon1_start_point,
                               ribbon2_start_point = ribbon2_start_point,
                               ribbon1_direction = ribbon1_direction,
                               ribbon2_direction = ribbon2_direction,
                               ribbon1Color = ribbon1Color,
                               ribbon2Color = ribbon2Color,
                               stepColor = black )
                        
            #Draw the text next to the cursor that gives info about
            #number of base pairs etc
            self._drawCursorText()