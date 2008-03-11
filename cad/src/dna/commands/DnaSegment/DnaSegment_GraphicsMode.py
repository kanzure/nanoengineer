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
from Numeric import dot
from PyQt4.Qt import QMouseEvent
from dna.commands.BuildDna.BuildDna_GraphicsMode import BuildDna_GraphicsMode
from dna.model.DnaSegment import DnaSegment

from dna.temporary_commands.DnaLineMode import DnaLine_GM
from TemporaryCommand import ESC_to_exit_GraphicsMode_preMixin

from graphics.drawing.drawDnaRibbons import drawDnaRibbons

import foundation.env as env
from prefs_constants import bdnaBasesPerTurn_prefs_key

import math
from geometry.VQT import V, norm, A, Q, vlen
from constants import darkred, blue, black
from debug import print_compact_traceback

from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT

from model.chem import Atom
from model.bonds import Bond

SPHERE_RADIUS = 2.0
SPHERE_DRAWLEVEL = 2


from dna.commands.BuildDna.BuildDna_GraphicsMode import DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND

_superclass = BuildDna_GraphicsMode

class DnaSegment_GraphicsMode(ESC_to_exit_GraphicsMode_preMixin,
                              BuildDna_GraphicsMode):
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

    cursor_over_when_LMB_pressed = ''        

    def bareMotion(self, event):
        """
        @see: self.update_cursor_for_no_MB
	"""
        _superclass.bareMotion(self, event)
        
        #When the cursor is over a specifit atom, we need to display 
        #a different icon. (e.g. when over a strand atom, it should display 
        # rotate cursor)    
        self.update_cursor()            
    

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
                        
    #===========================================================================
    #START-- UNUSED METHODS DUE TO CHANGE IN IMPLEMENTATION 
    #The following methods are not used as of 2008-03-04 due to a change in
    #implementation" Earlier, if you click on a strand or segment (while 
    #in BuildDna_EditCommand or its subcommands) it used to enter the edit mode 
    #of the object being editable. I am planning to make it a user preference
    #-- Ninad 2008-03-04
    def chunkLeftDown(self, aChunk, event):
        if 0:
            if self.command and self.command.hasValidStructure():
                dnaGroup = aChunk.getDnaGroup()
                
                if dnaGroup is not None:
                    if dnaGroup is self.command.struct.getDnaGroup():
                        if aChunk.isStrandChunk():
                            aChunk.pick()
                            pass
    #END -- UNUSED METHODS DUE TO CHANGE IN IMPLEMENTATION 
    #===========================================================================
                        
    def chunkLeftUp(self, aChunk, event):
        """
        """
        _superclass.chunkLeftUp(self, aChunk, event)
        
        if not self.current_obj_clicked:
            return
        
        if DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND:        
            if aChunk.picked:
                if aChunk.isAxisChunk():   
                    segmentGroup = aChunk.parent_node_of_class(self.o.assy.DnaSegment)
                    if segmentGroup is not None:                    
                        segmentGroup.edit()
                elif aChunk.isStrandChunk() and aChunk is not self.command.struct:
                    strandGroup = aChunk.parent_node_of_class(self.o.assy.DnaStrand)
                    if strandGroup is not None:
                        strandGroup.edit()
                    else:
                        aChunk.edit()

    def leftDown(self, event):
        """
        """
        self.reset_drag_vars()
                       
        obj = self.get_obj_under_cursor(event)

        if obj is None:
            self.cursor_over_when_LMB_pressed = 'Empty Space'
            
        
            
        #@see dn_model.DnaSegment.isAncestorOf. 
        #It checks whether the object under the 
        #cursor (which is glpane.selobj) is contained within the DnaSegment
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
        self._leftDown_preparation_for_dragging(event)


    def _leftDown_preparation_for_dragging(self, event):
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
        self.leftADown(event)
        

    def leftADown(self, event):
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


        ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
        self.Zmat = A([ma,[-ma[1],ma[0]]])

        obj = self.get_obj_under_cursor(event)

        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            #Left A drag is not possible unless the cursor is over a 
            #selected object. So make sure to let self.leftAError method sets
            #proper flag so that left-A drag won't be done in this case.
            return

        ##self.doObjectSpecificLeftDown(obj, event)
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
        if self.command and self.command.handles:
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
                       
        #If the cursor was not over something that belownged to structure 
        #being edited (example - atom or bond of a DnaSegment) don't 
        #do left drag.(left drag will work only for the DnaSegment being edited)
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
        
        #First, don't draw handles (set the flag here so that self.Draw knows 
        #not to draw handles) This skips unnecessary computation of new handle
        #position during left dragging. The flag is reset to True in leftUp
        if self.command and self.command.handles:
            if self.command.grabbedHandle is None:
                self._handleDrawingRequested = False
        
        #Copies AND modifies some code from move_GraphicsMode for doing 
        #leftDrag translation or rotation. 
               
        w = self.o.width + 0.0
        h = self.o.height + 0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())

        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w)       

        movables = []
        rotateAboutAxis = False
        translateAlongAxis = False
        freeDragWholeStructure = False # If true, the whole segment will be 
                                       #free dragged
        
        #Refactoring / optimization TODO: May be we should set these flags in 
        #leftDown (rather in self._leftDown_preparation_for_dragging)
        #by defining a method such as self._setLeftDragsFlags and retieve 
        #those in leftDrag (rather than computing them here everytime. 
        #Same goes for movable list. -- Ninad 2008-02-12
        if self.command and self.command.struct:
            #Resultant axis is the axis of the segment itself. 
            resAxis = self.command.struct.getAxisVector()
            #May be we should use is_movable test below? But we know its a dna
            #segment and all its members are chunks only. Also note that 
            #movables are NOT the 'selected' objects here. 
            
            #@see: DnaSegment.get_all_content_chunks() for details about 
            #what it returns. See also DnaSegment.isAncestorOf() which 
            #is called in self.leftDown to determine whether the DnaSegment 
            #user is editing is an ancestor of the selobj. (it also considers
            #'logical contents' while determining whether it is an ancestor.
            #-- Ninad 2008-03-11
            movables = self.command.struct.get_all_content_chunks()
            
            if isinstance(self.o.selobj, Atom) and \
               self.o.selobj.element.role == 'axis':                
                translateAlongAxis = True
                rotateAboutAxis = False
                freeDragWholeStructure = False
            elif isinstance(self.o.selobj, Atom) and \
                 self.o.selobj.element.role == 'strand':
                translateAlongAxis = False
                rotateAboutAxis = True
                freeDragWholeStructure = False
            elif isinstance(self.o.selobj, Bond):
                translateAlongAxis = False
                rotateAboutAxis = False
                freeDragWholeStructure = True
        

        if translateAlongAxis:
            for mol in movables:
                mol.move(dx*resAxis)

        if rotateAboutAxis:
            #Don't include the axis chunk in the list of movables. 
            #Fixes (or works around) a bug due to which the axis chunk 
            #displaces from its original position while rotating about that axis.
            #The bug might be in the computation of common center in 
            #ops_motion.rotateSpecifiedMovables or it could be some weired effect
            # in chunk center computation ..because of which the common center
            #of chunks is slightly off the axis. Considering only strand chunks 
            # (and not axisChunk) is a workaround for this bug. Actual bug 
            #might be harder to fix not sure. -- Ninad 2008-02-12
            
            #UPDATE 2008-02-13
            #Disabled temporarily to see if this fixes a recently introduced 
            #bug :strands don't rotate about segment's axis:
            ##new_movables = list(movables)
            ##for chunk in new_movables:
                ##if chunk.isAxisChunk():
                    ##new_movables.remove(chunk)
            self.o.assy.rotateSpecifiedMovables(Q(resAxis,-dy), 
                                                movables = movables) 
        
        if freeDragWholeStructure:
            try:
                point = self.dragto( self.movingPoint, event) 
                offset = point - self.movingPoint
                self.o.assy.translateSpecifiedMovables(offset, movables = movables)
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
    
  
    def drawHighlightedChunk(self, glpane, selobj, hicolor, hicolor2):
        """
        [overrides SelectChunks_basicGraphicsMode method]
        """
        # bruce 071008 (intending to be equivalent to prior code)
        return False    

    def Draw(self):
        """
        """
        if self._handleDrawingRequested:
            self._drawHandles()     
        _superclass.Draw(self)
              
    def _drawHandles(self):
        """
        Draw the handles for the command.struct 
        """    
        if self.command and self.command.hasValidStructure():            
            for handle in self.command.handles:
                handle.draw()
        
        handleType = ''
        if self.command.grabbedHandle is not None:
            if self.command.grabbedHandle in [self.command.rotationHandle1, 
                                              self.command.rotationHandle2]:
                handleType = 'ROTATION_HANDLE'
            else:
                handleType = 'RESIZE_HANDLE'
        
        
        if handleType and handleType == 'RESIZE_HANDLE':            
            # We have no easy way to get the original "bases per turn" value
            # that was used to create this segment, so we will use
            # the current "bases per turn" user pref value. This is really 
            # useful (and a kludge) workaround for doing origami design work
            # since we (Tom and I) often need to resize DNA origami segments.
            # I spoke with Bruce about this and we agree that this will be 
            # much easier to fix once the DNA updater/data model is 
            # implemented (soon), so let's wait until then. Mark 2008-02-10.
            basesPerTurn = env.prefs[bdnaBasesPerTurn_prefs_key]
            
            #Note: The displayStyle argument for the rubberband line should 
            #really be obtained from self.command.struct. But the struct 
            #is a DnaSegment (a Group) and doesn't have attr 'display'
            #Should we then obtain this information from one of its strandChunks?
            #but what if two strand chunks and axis chunk are rendered 
            #in different display styles? since situation may vary, lets 
            #use self.glpane.displayMode for rubberbandline displayMode
            drawDnaRibbons(self.command.grabbedHandle.fixedEndOfStructure,
                           self.command.grabbedHandle.currentPosition,
                           basesPerTurn,
                           self.command.duplexRise,
                           self.glpane.scale,
                           self.glpane.lineOfSight,
                           self.glpane.displayMode,
                           ribbonThickness = 4.0,
                           ribbon1Color = darkred,
                           ribbon2Color = blue,
                           stepColor = black )
            #Draw the text next to the cursor that gives info about 
            #number of base pairs etc
            if self.command:
                text = self.command.getCursorText()
                self.glpane.renderTextNearCursor(text, offset = 30)
        else:
            #No handle is grabbed. But may be the structure changed 
            #(e.g. while dragging it ) and as a result, the endPoint positions 
            #are modified. So we must update the handle positions because 
            #during left drag (when handle is not dragged) we skip the 
            #handle drawing code and computation to update the handle positions
            self.command.updateHandlePositions()
            

class DnaSegment_DragHandles_GraphicsMode(DnaLine_GM):
    """
    EXPERIMENTAL class to use DnaLine_GM functionality while dragging a handle
    See a comment in class DnaSegment_EditCommand, just above the method
    'EXPERIMENTALswitchGraphicsModeTo'
    """

    cursor_over_when_LMB_pressed = ''
    
    def Enter_GraphicsMode(self):
        self.endPoint1 = self.command.aHandle.origin
        DnaLine_GM.Enter_GraphicsMode(self)
   
    def Draw(self):
        """
        Draw
        """        
        DnaLine_GM.Draw(self)
        self._drawHandles()


    def _drawHandles(self):
        """
        draw handles
        """    
        if self.command and self.command.struct:
            if isinstance(self.command.struct, DnaSegment):
                for handle in self.command.handles:
                    handle.draw()
    
    def leftUp(self, event):
        """
        Method to be called during leftUp mouse event
        """
        self.command.preview_or_finalize_structure(previewing = True)
