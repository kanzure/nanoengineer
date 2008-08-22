# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
"""

from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from model.chem import Atom
from model.bonds import Bond
from Numeric import dot
from PyQt4.Qt import QMouseEvent
from geometry.VQT import V, Q, A, norm, vlen
from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT
from utilities.debug import print_compact_traceback
import math

from graphics.drawing.drawDnaLabels import draw_dnaBaseNumberLabels

DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND = True

_superclass = SelectChunks_GraphicsMode
class BuildDna_GraphicsMode(
                            SelectChunks_GraphicsMode):
    """
    """

    #The flag that decides whether to draw the handles. This flag is
    #set during left dragging, when no handle is 'grabbed'. This optimizes the
    #drawing code as it skips handle drawing code and also the computation
    #of handle positions each time the mouse moves
    #@see self.leftUp , self.leftDrag, seld.Draw for more details
    _handleDrawingRequested = True

    #Some left drag variables used to drag the whole segment along axis or
    #rotate the segment around its own axis of for free drag translation
    _movablesForLeftDrag = []

    #Subclasses such as MakeCrossovers_GraphicsMode need this attr.
    #needs refactoring. See self.leftADown()
    _movable_dnaSegment_for_leftDrag = None

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

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for Select mode (Default implementation).
        """
        _superclass.update_cursor_for_no_MB(self)

        #minor optimization -- don't go further into the method if
        #nothing is highlighted i.e. self.o.selobj is None.
        if self.o.selobj is None:
            return

        if self.o.modkeys is None:
            if isinstance(self.o.selobj, Atom):
                if self.o.selobj.element.role == 'strand':
                    self.o.setCursor(self.win.rotateAboutCentralAxisCursor)
                elif self.o.selobj.element.role == 'axis':
                    self.o.setCursor(self.win.translateAlongCentralAxisCursor)
                    
                    
    
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

    def leftDown(self, event):
        """
        """
        self.reset_drag_vars()

        self.clear_leftA_variables()

        _superclass.leftDown(self, event)

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
        ##self._leftDown_preparation_for_dragging(event)

    def clear_leftA_variables(self):
        self._movablesForLeftDrag = []
        #Subclasses such as MakeCrossovers_GraphicsMode need this attr.
        #(self._movable_dnaSegment_for_leftDrag) needs refactoring.
        self._movable_dnaSegment_for_leftDrag = None
        self._commonCenterForRotation = None
        self._axis_for_constrained_motion = None
        self._translateAlongAxis = False
        self._rotateAboutAxis = False
        self._freeDragWholeStructure = False

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

    def singletLeftDown(self, s, event):
        """
        Handles SingletLeftDown (left down on a bond point) event.
        @see: JoinStrands_GraphicsMode.leftUp()
        """

        #@see: class JoinStrands_GraphicsMode for a detailed explanation.
        #copying some portion in that comment below --
        #Example: In this BuildDna_EditCommand (graphicsMode), if you want to
        #join  two strands, upon 'singletLeftDown'  it enters
        #JoinStrands_Command , also calling leftDown method of its graphicsmode.
        #Now, when user releases theLMB, it calls
        #JoinStrands_GraphicsMode.leftUp()  which in turn exits that command
        #if the flag 'exit_command_on_leftUp' is set to True(to go back to the
        #previous command user was in) .
        #A lot of code that does bondpoint dragging is available in
        #BuildAtoms_GraphicsMode, but it isn't in BuildDna_GraphicsMode
        #(as it is a  SelectChunks_GraphicsMode superclass for lots of reasons)
        #So, for some significant amount of time, we may continue to use
        #this flag to temporarily enter/exit this command.
        #@see: self.leftUp(), BuildDna_GraphicsMode.singletLeftDown()

        #Note: Going back and forth between joinstrands command has a bug
        #due to commandstack depth. It won't go back to DnaStrand and Segment
        #edit commands (if the previous command was one of those) instead it
        #will always return to BuildDna_EditCommand.

        commandSequencer = self.win.commandSequencer

        commandSequencer.userEnterTemporaryCommand('JOIN_STRANDS')

        assert commandSequencer.currentCommand.commandName == 'JOIN_STRANDS'

        #Make sure that the glpane selobj is set to 's' (this bondpoint)
        #when we enter a different command, all that information is probably
        #lost , so its important to set it explicitly here.
        self.glpane.set_selobj(s)

        #'gm' is the graphics mode of JoinStrands_Command
        gm = commandSequencer.currentCommand.graphicsMode
        #Set the graphics mode flag so that it knows to return to
        #BuildDna_EditCommand upon leftUp()
        gm.exit_command_on_leftUp = True
        gm.leftDown(event)
        return


    def chunkLeftDown(self, a_chunk, event):
        """
        Depending on the modifier key(s) pressed, it does various operations on
        chunk..typically pick or unpick the chunk(s) or do nothing.

        If an object left down happens, the left down method of that object
        calls this method (chunkLeftDown) as it is the 'SelectChunks_GraphicsMode' which
        is supposed to select Chunk of the object clicked
        @param a_chunk: The chunk of the object clicked (example, if the  object
                      is an atom, then it is atom.molecule
        @type a_chunk: B{Chunk}
        @param event: MouseLeftDown event
        @see: self.atomLeftDown
        @see: self.chunkLeftDown
        @see:self.objectSetUp()
        """

        strandOrSegment = a_chunk.parent_node_of_class(
            self.win.assy.DnaStrandOrSegment)

        if strandOrSegment is not None:
            #Make sure to call chunkSetUp if you are not calling the
            #chunkLeftDown method of superclass. This in turn,
            #calls self.objectSetUp(). Fixes a problem in selecting a
            #DnaClynder chunk (selobj = Chunk)
            self.chunkSetUp(a_chunk, event)
            return

        _superclass.chunkLeftDown(self, a_chunk, event)


    def chunkLeftUp(self, aChunk, event):
        """
        Upon chunkLeftUp, it enters the strand or segment edit command
        This is an alternative implementation. As of 2008-03-03,
        we have decided to change this implementation. Keeping the
        related methods alive if, in future, we want to switch to this
        implementation and/or add a user preference to do this.
        """

        _superclass.chunkLeftUp(self, aChunk, event)

        if self.glpane.modkeys is not None:
            #Don't go further if some modkey is pressed. We will call the
            #edit method of the Dna components only if no modifier key is
            #pressed

            return

        if not self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            return

        #@TODO: If the object under mouse was double clicked, don't enter the
        #edit mode, instead do appropriate operation such as expand selection or
        #contract selection (done in superclass)
        #Note: when the object is just single clicked, it becomes editable).

        if self.editObjectOnSingleClick():
            if aChunk.picked:
                if aChunk.isAxisChunk() or aChunk.isStrandChunk():
                    strandOrSegmentGroup = aChunk.parent_node_of_class(
                        self.win.assy.DnaStrandOrSegment)
                    if strandOrSegmentGroup is not None:
                        strandOrSegmentGroup.edit()
                        strandOrSegmentGroup.pick()

    def _do_leftShiftCntlUp_delete_operations(self,
                                              event,
                                              objUnderMouse,
                                              parentNodesOfObjUnderMouse = ()):
        """
        Overrides superclass method

        @param parentNodesOfObjUnderMouse: Tuple containing the
                parent chunk(s), of which, the object
                under mouse  is a part of,  or, some other node such as a
                DnaStrand Or DnaSegment etc which the user probably wants to
                operate on.
        @type: Tuple

        @see: self.chunkLeftUp()
        @see: self.leftShiftCntlUp() which calls this method.
        @see: SelectChunks_GraphicsMode._do_leftShiftCntlUp_delete_operations()
        """
        obj = objUnderMouse
        if obj is self.o.selobj:
            if isinstance(obj, Bond):
                self.bondDelete(event)
                return


        _superclass._do_leftShiftCntlUp_delete_operations(
            self,
            event,
            objUnderMouse,
            parentNodesOfObjUnderMouse = parentNodesOfObjUnderMouse)


    def leftADown(self, objectUnderMouse, event):
        """
        Method called during mouse left down . It sets some parameters
        necessary for rotating the structure around its own axis (during
        a left drag to follow) In graphics modes such as
        RotateChunks_GraphicsMode, rotating entities around their own axis is
        acheived by holding down 'A' key and then left dragging , thats why the
        method is named as 'leftADrag'  (A= Axis)
        """
        obj = objectUnderMouse

        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            #Left A drag is not possible unless the cursor is over a
            #selected object. So make sure to let self.leftAError method sets
            #proper flag so that left-A drag won't be done in this case.
            return

        ma = V(0, 0, 0)
        chunk = None

        if isinstance(obj, Atom):
            chunk = obj.molecule
        elif isinstance(obj, self.win.assy.Chunk):
            chunk = obj
        elif isinstance(obj, Bond):
            chunk1 = obj.atom1.molecule
            chunk2 = obj.atom2.molecule
            #@@ what should we do if its a interchunk bond?? lets just select
            #one chunk
            chunk = chunk1

        if chunk is None:
            return

        ma, segment = chunk.getAxis_of_self_or_eligible_parent_node()

        self._axis_for_constrained_motion = ma

        #@see: DnaSegment.get_all_content_chunks() for details about
        #what it returns. See also DnaSegment.isAncestorOf() which
        #is called in self.leftDown to determine whether the DnaSegment
        #user is editing is an ancestor of the selobj. (it also considers
        #'logical contents' while determining whether it is an ancestor.
        #-- Ninad 2008-03-11

        if isinstance(segment, self.win.assy.DnaSegment):
            self._movablesForLeftDrag = segment.get_all_content_chunks()
            self._movable_dnaSegment_for_leftDrag = segment
        else:
            self._movablesForLeftDrag = self.win.assy.getSelectedMovables()

        ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))

        self.Zmat = A([ma,[-ma[1],ma[0]]])


        if isinstance(obj, Atom) and \
           obj.element.role == 'axis':
            self._translateAlongAxis = True
            self._rotateAboutAxis = False
            self._freeDragWholeStructure = False
        elif isinstance(obj, Atom) and \
             obj.element.role == 'strand':
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
            axis_neighbor = obj.axis_neighbor()
            if axis_neighbor is not None:
                self._commonCenterForRotation = axis_neighbor.posn()
        else:
            self._translateAlongAxis = False
            self._rotateAboutAxis = False
            self._freeDragWholeStructure = True


        self.o.SaveMouse(event)
        self.dragdist = 0.0


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
        if hasattr(self.command, 'handles') and self.command.handles:
            self.command.updateHandlePositions()
            if not self._handleDrawingRequested:
                self._handleDrawingRequested = True

        #IMPLEMENTATION CHANGE 2008-03-05.
        #Due to an implementation change, user is not allowed to
        #exit this command by simply clicking onto empty space. So following
        #is commented out. (Keeping it for now just in case we change our mind
        #soon. If you see this code being commented out even after 1 or 2 months
        #from the original comment date, please just delete it.
        #--Ninad 2008-03-05
        ##if self.cursor_over_when_LMB_pressed == 'Empty Space':
            ###Exit this command by directly calling command.Done.
            ###This skips call of command.preview_or_finalize_structure
            ###Not calling 'preview_or_finialize_structure before calling
            ###command.Done(), has an advantage. As of 2008-02-20, we
            ###remove the structure (segment) and recreate it upon done.
            ###This also removes, for instance, any cross overs you created
            ###earlier. although same thing happens when you hit 'Done button',
            ###it is likely to happen by accident while you are in segment edit
            ###mode and just click on empty space, Therefore, we simply call
            ###Command.Done(). See a related bug mentioned in
            ###DnaSegment_EditCommand.setStructureName
            ##self.command.Done()


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
        #which checkes if self.drag_handler is in assy.getSelecteedMovables
        #I don't know why it does that... I think it always assums that the
        #drag handler is officially a node in the MT? In our case,
        #the drag handler is a 'Highlightable' object (actually
        #an instance of 'DnaSegment_ResizeHandle' (has superclass from
        #exprs module ..which implements API for a highlightable object
        #So it doesn't get registered in the selectMovables list. Thats why
        #we are not calling _superclass.leftDrag. The above mentioned
        #method in the superclass needs to be revised -- Ninad 2008-02-01

        if self.drag_handler is not None:
            self.dragHandlerDrag(self.drag_handler, event)
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

        #First, don't draw handles (set the flag here so that self.Draw knows
        #not to draw handles) This skips unnecessary computation of new handle
        #position during left dragging. The flag is reset to True in leftUp

        if hasattr(self.command, 'handles') and self.command.handles:
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

        if self._translateAlongAxis:
            for mol in self._movablesForLeftDrag:
                mol.move(dx*self._axis_for_constrained_motion)

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


        self.dragdist += vlen(deltaMouse) #k needed?? [bruce 070605 comment]

        self.o.SaveMouse(event)
        self.o.assy.changed() #ninad060924 fixed bug 2278
        self.o.gl_update()
        return

    def _is_dnaGroup_highlighting_enabled(self):
        """
        Overrides SelectChunks_GraphicsMode._is_dnaGroup_highlighting_enabled()

        Returns a boolean that decides whether to highlight the whole
        DnaGroup or just the chunk of the glpane.selobj.
        Example: In default mode (SelectChunks_graphicsMode) if the cursor is
        over an atom or a bond which belongs to a DnaGroup, the whole
        DnaGroup is highlighted. But if you are in buildDna mode, the
        individual strand and axis chunks will be highlighted in this case.
        Therefore, subclasses of SelectChunks_graphicsMode should override this
        method to enable or disable the DnaGroup highlighting. (the Default
        implementation returns True)
        @see: self._get_objects_to_highlight()
        @see: self.drawHighlightedChunk()
        @see : self.drawHighlightedObjectUnderMouse()
        """
        return False

    def editObjectOnSingleClick(self):
        """
        Subclasses can override this method. If this method returns True,
        when you left click on a DnaSegment or a DnaStrand, it becomes editable
        (i.e. program enters the edit command of that particular object if
        that object is editable)
        @see: MakeCrossover_GraphicsMode.editObjectOnSingleClick()
        """
        if DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND:
            return True
        

    def drawHighlightedChunk(self, glpane, selobj, hicolor, hicolor2):
        """
        Overrides SelectChunks_basicGraphicsMode method.
        """
        chunk = None

        if isinstance(selobj, self.win.assy.Chunk):
            chunk = selobj
        elif isinstance(selobj, Atom):## and not selobj.is_singlet():
            chunk = selobj.molecule
        elif isinstance(selobj, Bond):
            #@@@ what if its a interchunk bond -- case not supported as of
            #2008-04-30
            chunk = selobj.atom1.molecule


        if chunk is not None:
            dnaStrandOrSegment = chunk.parent_node_of_class(
                self.win.assy.DnaStrandOrSegment)
            if dnaStrandOrSegment is not None:
                if self.glpane.modkeys == 'Shift+Control':
                    #Don't highlight the whole chunk if object under cursor
                    #is a bond and user has pressed the Shift+Control key
                    #It means we will allow breaking of that bond upon leftClick
                    if isinstance(selobj, Bond):
                        return False
                else:
                    #If the object under cursor is not a bond,
                    #AND the modifier key is not "Shift+Control', only highlight
                    #that object (which will most likely be the Atom or a
                    #singlet. This special highlighting will be used to do
                    #various stuff like rotating the Dna duplex around its axis
                    #etc.
                    if isinstance(selobj, Atom):
                        return False

        #For all other cases , do what superclass does for highlighting
        # a chunk
        return _superclass.drawHighlightedChunk(self,
                                                glpane,
                                                selobj,
                                                hicolor,
                                                hicolor2)


    def _drawCursorText(self, position = None):
        """
        Draw the text near the cursor. It gives information about number of
        basepairs/bases being added or removed, length of the segment (if self.struct
        is a strand etc.
        @param position: Optional argument. If position (a vector) is specified, 
                         instead of drawing the text at the cursor position, 
                         it is drawn at the specified position. 
        @type position: B{V} or None
               
        @see: DnaSegment_GraphicsMode,  DnaStrand_GraphicsMode  (subclasses of
        this class where this is being used.
        """
        if hasattr(self.command, 'grabbedHandle') and hasattr(self.command,
                                                              'getCursorText'):
            if self.command.grabbedHandle is not None:
                #Draw the text next to the cursor that gives info about
                #number of base pairs etc

                text , textColor = self.command.getCursorText()
                                
                if position is None:
                    self.glpane.renderTextNearCursor(text,
                                                     offset = 30,
                                                     color = textColor)
                else:
                    self.glpane.renderTextAtPosition( position,
                                                      text, 
                                                      textColor = textColor)
    
    
    def _drawLabels(self):
        """
        Overrides superclass method
        @see: self.Draw()
        @see: drawDnaLabels.py
        """
        _superclass._drawLabels(self)
        #Draw the Dna base number labels. 
        draw_dnaBaseNumberLabels(self.glpane)
        
    