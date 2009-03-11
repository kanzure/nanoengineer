# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2008-01-25: Split modifyMode into Command and GraphicsMode classes
                  and also refactored the GraphicsMode to create individual
                  classes for rotating and translating selected entities
                  (called RotateChunks_GraphicsMode and
                  TranslateChunks_GraphicsMode)
"""

import math
from Numeric import dot

from PyQt4.Qt import QMouseEvent
from PyQt4.Qt import Qt
import foundation.env as env
from geometry.VQT import V, Q, A, vlen, norm
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from utilities.constants import SUBTRACT_FROM_SELECTION
from utilities.constants import ADD_TO_SELECTION
from utilities.constants import START_NEW_SELECTION
from utilities.constants import DELETE_SELECTION

_superclass = SelectChunks_GraphicsMode

#Contains common code of both Rotate and Translate GraphicsModes.

class Move_GraphicsMode(SelectChunks_GraphicsMode):
    """
    """
    # class constants
    gridColor = 52/255.0, 128/255.0, 26/255.0


    # class variables
    moveOption = 'MOVEDEFAULT'
    rotateOption = 'ROTATEDEFAULT'
    axis = 'X'
    RotationOnly = False
    TranslationOnly = False
    isConstrainedDragAlongAxis = False

    #The following variable stores a string. It is used in leftDrag related
    #methods to handle cases where the user may do a keypress *while* left
    #dragging, which would change the move type. This variable is assigned a
    #string value.See self.leftDownForTranslatation for an example.
    leftDownType = None

    def Enter_GraphicsMode(self):
        """
        Things needed while entering the GraphicsMode (e.g. updating cursor,
        setting some attributes etc).
        This method is called in self.command.command_entered()
        @see: B{GraphicsMode.Enter_GraphicsMode}
        """
        _superclass.Enter_GraphicsMode(self)

        #Initialize the flag for Constrained translation and rotation
        #along the axis of the chunk to False. This flag is set
        #to True whenever keyboard key 'A' is pressed
        #while in Translate/Rotate mode. See methods keyPress, keyRelease,
        #leftDown, Drag and leftADown, Drag for details.
        self.isConstrainedDragAlongAxis = False

        self.dragdist = 0.0
        self.clear_leftA_variables() #bruce 070605 precaution
        self.o.assy.selectChunksWithSelAtoms()

    def keyPress(self,key):
        _superclass.keyPress(self, key)
        # For these key presses, we toggle the Action item, which will send
        # an event to changeMoveMode, where the business is done.
        # Mark 050410

        # If Key 'A' is pressed, set the flag for Constrained translation and
        #rotation along the axis of the chunk; otherwise reset that flag
        # [REVIEW: is that resetting good, for any key at all??
        #If so, document why. bruce comment 071012]
        if key == Qt.Key_A:
            self.isConstrainedDragAlongAxis = True
        else:
            self.isConstrainedDragAlongAxis = False

        self.update_cursor()

    def keyRelease(self,key):
        _superclass.keyRelease(self, key)

        if key in [Qt.Key_X, Qt.Key_Y, Qt.Key_Z, Qt.Key_A]:
            self.movingPoint = None # Fixes bugs 583 and 674 along with change
            ##in leftDrag().  Mark 050623
        elif key == Qt.Key_R:
            self.RotationOnly = False # Unconstrain translation.
        elif key == Qt.Key_T:
            self.TranslationOnly = False # Unconstrain rotation.

        #Set the flag for Constrained translation and rotation
        #along the axis of the chunk to False
        self.isConstrainedDragAlongAxis = False
        self.update_cursor()

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for 'Move Chunks' mode.
        Overridden in subclasses.
        @see: RotateChunks_GraphicsMode.update_cursor_for_no_MB
        @see: TranslateChunks_GraphicsMode.update_cursor_for_no_MB
        """
        _superclass.update_cursor_for_no_MB(self)

    def leftDown(self, event):
        """
        Handle left down event. Preparation for dragging and/or selection
        @param event: The mouse left down event.
        @type  event: QMouseEvent instance
        @see: self._leftDown_preparation_for_dragging
        """
        #The following variable stores a string. It is used in leftDrag related
        #methods to handle cases where the user may do a keypress *while* left
        #dragging, which would change the move type. This variable is assigned a
        #string value.See self.leftDownForTranslatation for an example.
        self.leftDownType = None

        self.clear_leftA_variables() #bruce 070605 added this
                                     #(guess at what's needed)
        env.history.statusbar_msg("")

        self.reset_drag_vars()


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

        # If keyboard key 'A' is pressed OR if the corresponding toolbutton
        # in the propMgr is pressed,  set it up for constrained translation
        # and rotation along the axis and return.

        # @TODO: Should reuse the flag self.isConstrainedDragAlongAxis instead
        # of checking move/ rotate options independently. Better to associate
        # key 'A' with the appropriate option in the PM. Also, the
        # propMgr sets the moveOption flags of the graphics mode. PropMgr should
        # be prevented from using graphicsmode object for clarity. This is
        # one of the code cleanup and refactoring projects related to this command
        # (this is one of the things that hasn't completely cleanued up
        # during refactoring and major cleanup of the old modifyMode class code.
        # --Ninad 2008-04-09

        # Permit movable object picking upon left down.
        obj = self.get_obj_under_cursor(event)

        if self.isConstrainedDragAlongAxis or \
           self.moveOption == 'ROT_TRANS_ALONG_AXIS' or \
           self.rotateOption == 'ROT_TRANS_ALONG_AXIS':
            self.leftADown(obj, event)
            return


        # If highlighting is turned on, get_obj_under_cursor() returns atoms,
        # singlets, bonds, jigs,
        # or anything that can be highlighted and end up in glpane.selobj.
        # [bruce revised this comment, 060725]If highlighting is turned off,
        # get_obj_under_cursor() returns atoms and singlets (not bonds or jigs).
        # [not sure if that's still true -- probably not. bruce 060725 addendum]
        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            return

        self.doObjectSpecificLeftDown(obj, event)

        #Subclasses should override one of the following method if they need
        #to do additional things to prepare for dragging.
        self._leftDown_preparation_for_dragging(obj, event)

        self.w.win_update()
        return

    def _leftDown_preparation_for_dragging(self,  objectUnderMouse, event):
        """
        Subclasses should override this (AND ALSO CALLING THIS method in
        the overridden method)
        if they need additional things to be
        done in self.leftDown, to prepare for left dragging the selection.
        @see: TranslateChunks_GraphicsMode._leftDown_preparation_for_dragging
        @see: RotateChunks_GraphicsMode._leftDown_preparation_for_dragging
        """
        self._leftDrag_movables = self.getMovablesForLeftDragging()


    def leftDrag(self, event):
        """
        Drag the selected object(s):
        - in the plane of the screen following the mouse,
        - or slide and rotate along the an axis

        Overridden in subclasses

        @param event: The mouse left drag event.
        @type  event: QMouseEvent instance
        @see: TranslateChunks.leftDrag
        @see: RotateChunks.leftDrag
        """
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            ##self.continue_selection_curve(event)
            self.emptySpaceLeftDrag(event)
            return

        if self.o.modkeys is not None:
            #@see: comment related to this condition in _superclass.leftDrag
            self.emptySpaceLeftDown(self.LMB_press_event)
            return

        if not self.picking:
            return

        if not self._leftDrag_movables:
            return

        if self.isConstrainedDragAlongAxis:
            try:
                self.leftADrag(event)
                return
            except:
                # this might be obsolete, since leftADrag now tries to handle
                #this (untested) [bruce 070605 comment]
                print "Key A pressed after Left Down. controlled "\
                      "translation will not be performed"

        # end of leftDrag

    def leftUp(self, event):
        """
        Overrides leftdrag method of _superclass
        """
        if self.cursor_over_when_LMB_pressed == 'Empty Space': #@@ needed?
            self.emptySpaceLeftUp(event)
        elif self.dragdist < 2:
            _superclass.leftUp(self,event)

    def EndPick(self, event, selSense):
        """
        Pick if click
        """
        #Don't select anything if the selection is locked.
        #see self.selection_locked() for more comments.
        if self.selection_locked():
            return

        if not self.picking:
            return

        self.picking = False

        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(),
                       0.0)
        self.dragdist += vlen(deltaMouse)

        if self.dragdist < 7:
            # didn't move much, call it a click
            has_jig_selected = False
            if self.o.jigSelectionEnabled and self.jigGLSelect(event, selSense):
                has_jig_selected = True
            if not has_jig_selected:
                # Note: this code is similar to def end_selection_curve
                # in Select_GraphicsMode.py. See comment there
                # about why it handles jigs separately and
                # how to clean that up (which mentions findAtomUnderMouse
                # and jigGLSelect). [bruce 080917 comment]
                if selSense == SUBTRACT_FROM_SELECTION:
                    self.o.assy.unpick_at_event(event)
                if selSense == ADD_TO_SELECTION:
                    self.o.assy.pick_at_event(event)
                if selSense == START_NEW_SELECTION:
                    self.o.assy.onlypick_at_event(event)
                if selSense == DELETE_SELECTION:
                    self.o.assy.delete_at_event(event)

            #Call graphics mode API method
            self.end_selection_from_GLPane()
            self.w.win_update()

    def clear_leftA_variables(self): # bruce 070605
        #k should it clear sbar too?
        # Clear variables that only leftADown can set. This needs to be done
        #for every mousedown and mouseup ###DOIT.
        # (more precisely for any call of Down that if A is then pressed might
        #start calling leftADrag ####)
        # Then, if they're not properly set during leftADrag, it will show a
        #statusbar error and do nothing.
        # This should fix bugs caused by 'A' keypress during drag or 'A'
        #keypress not noticed by NE1 (in wrong widget or app).
        # [bruce 070605 bugfix; also added all these variables]
        self._leftADown = False # whether we're doing a leftA-style drag at all
        self._leftADown_rotateAsUnit = None
        self._leftADown_movables = None # list of movables for leftADrag
            # WARNING: some code (rotsel calls) assumes this is also the movable
            #selected objects
        self._leftADown_indiv_axes = None
        self._leftADown_averaged_axis = None
        self._leftADown_error = False # whether an error should cause subsequent
        #leftADrags to be noops
        self._leftADown_dragcounter = 0
        self._leftADown_total_dx_dy = V(0.0, 0.0)
        return

    def leftAError(self, msg):
        env.history.statusbar_msg( msg) #bruce 070605
        self._leftADown_error = True # prevent more from happening in leftADrag
        return

    def leftADown(self, objectUnderMouse, event):
        """
        Set up for sliding and/or rotating the selected chunk(s)
        along/around its own axis when left mouse and key 'A' is pressed.
        Overriden in subclasses
        @see: TranslateChunks_GraphicsMode.leftADown
        @seE: RotateChunks_GraphicsMode.leftADown
        """

        self._leftADown = True

        if self.command and \
           self.command.propMgr and \
           hasattr(self.command.propMgr, 'rotateAsUnitCB'):
            self._leftADown_rotateAsUnit = self.command.propMgr.rotateAsUnitCB.isChecked()
        else:
            self._leftADown_rotateAsUnit = True


        obj = objectUnderMouse

        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            #Left A drag is not possible unless the cursor is over a
            #selected object. So make sure to let self.leftAError method sets
            #proper flag so that left-A drag won't be done in this case.
            self.leftAError("")
            return

        self.doObjectSpecificLeftDown(obj, event)

        movables = self.getMovablesForLeftDragging()
        self._leftADown_movables = movables

        if not movables:
            self.leftAError("(nothing movable is selected)")
            return

        self.o.SaveMouse(event)

        #bruce 070605 questions (about code that was here before I did
        #anything to it today):
        # - how are self.Zmat, self.picking, self.dragdist used during leftADrag?
        # - Why is the axis recomputed in each leftADrag? I think that's a bug,
        #for "rotate as a unit", since it varies!
        #   And it's slow, either way, since it should not vary (once bugs are
        #fixed) but .getaxis will always have to recompute it.
        #   So I'll change this to compute the axes or axis only once, here in
        #leftADown, and use it in each leftADrag.
        # - Why is the "averaged axis" computed here at all, when not "rotate
        #as a unit"?

        ma = V(0,0,0) # accumulate "average axis" (only works well if all axes
        #similar in direction, except perhaps for sign)
        self._leftADown_indiv_axes = [] #bruce 070605 optim
        for mol in movables:
            axis = mol.getaxis()
            if dot(ma, axis) < 0.0: #bruce 070605 bugfix, in case axis happens
                #to point the opposite way as ma
                axis = - axis
            self._leftADown_indiv_axes.append(axis) # not sure it's best to put
            #sign-corrected axes here, but I'm guessing it is
            ma += axis

        self._leftADown_averaged_axis = norm(ma) #bruce 070605 optim/bugfix


        if vlen(self._leftADown_averaged_axis) < 0.5: # ma was too small
            # The pathological case of zero ma is probably possible,
            #but should be rare;
            # consequences not reviewed; so statusbar message and refusal
            #seems safest:
            self.leftAError("(axes can't be averaged, doing nothing)")
            return

        ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
        self.Zmat = A([ma,[-ma[1],ma[0]]])
        self.picking = True
        self.dragdist = 0.0

        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
        # Following is in leftDrag() to compute move offset during drag op.
        self.startpt = self.movingPoint

        self._leftADown_total_dx_dy = V(0.0, 0.0)

        if 0: # looks ok; axis for 3-strand n=10 DNA is reasonably close to
            #axis of Axis strand [bruce 070605]
            print "\nleftADown gets",self._leftADown_averaged_axis
            print self._leftADown_indiv_axes
            print movables
            print self.Zmat


        return # from leftADown

    def leftADrag(self, event):
        """
        Move selected chunk(s) along its axis (mouse goes up or down)
        and rotate around its axis (left-right) while left dragging
        the selection with keyboard key 'A' pressed
        """

        ##See comments of leftDrag()--Huaicai 3/23/05
        if not self.picking:
            return

        if self._leftADown_error:
            return

        if not self._leftADown:
            self.leftAError("(doing nothing -- 'A' pressed after drag already started)")
            return

        movables = self._leftADown_movables
        assert movables # otherwise error flag was set during leftADown [bruce 070605]

        self._leftADown_dragcounter += 1
        counter = self._leftADown_dragcounter # mainly useful for debugging

        w = self.o.width + 0.0
        h = self.o.height + 0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())

        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w)

        self._leftADown_total_dx_dy += V(dx,dy)
        tot_dx, tot_dy = self._leftADown_total_dx_dy

        env.history.statusbar_msg("this 'A'-drag: translation: %f; rotation: %f" % (tot_dx, tot_dy))
            #bruce 070605; format might need cleanup

        if not self._leftADown_rotateAsUnit:
            # move/rotate individually ###UNTESTED since rewrite [bruce 070605]
            for mol, ma in zip(movables, self._leftADown_indiv_axes):
                mol.move(dx*ma)
                mol.rot(Q(ma,-dy))
        else:
            # move/rotate selection as a unit

            #find out resultant axis, translate and rotate the specified
            #movables along this axis -- ninad 20070605
            # (modified/optimized by bruce 070605)
            resAxis = self._leftADown_averaged_axis
            for mol in movables:
                mol.move(dx*resAxis)
            self.win.assy.rotateSpecifiedMovables( Q(resAxis,-dy),
                                                   movables = movables)
            # this assumes movables are exactly the selected movable objects
            # (as they are)
            # [could this be slow, or could something in here have a memory
            # leak?? (maybe redrawing selected chunks?)
            #  interaction is way too slow, and uneven, and I hear swapping
            # in the bg.  Aha, I bet it's all those Undo checkpoints, which we
            #should not be collecting during drags at all!!
            #  --bruce 070605 Q]
            #Implementation change note: the movables are computed only in
            #self.leftADown or self._leftDown_preparation_for_dragging()
            #the movables needen't necessarily be the selected objects
            #see self.getMovablesForLeftDragging() for details.
            #--Ninad 2008-04-08

        self.dragdist += vlen(deltaMouse) #k needed?? [bruce 070605 comment]
        self.o.SaveMouse(event)
        self.o.assy.changed() #ninad060924 fixed bug 2278
        self.o.gl_update()
        return

    def leftShiftUp(self, event):
        """
        Handle Left mouse up event when shift key is pressed.
        """
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftUp(event)
            return
        if self.o.modkeys == 'Shift+Control':
            self.end_selection_curve(event)
            return
        self.EndPick(event, ADD_TO_SELECTION)

    def leftDouble(self, event):
        """
        Do nothing upon double click , while in move mode
        (pre Alpha9 - experimental)
        """
        return

