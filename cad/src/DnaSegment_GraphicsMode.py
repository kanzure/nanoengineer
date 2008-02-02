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
 
- When you left drag a strand atom to rotate it around its own axis, 
 the axis vector changes. May be there is a bug in 
 ops_select.rotateSpecifiedMovables? Need to check. 

"""
from Numeric import dot
from PyQt4.Qt import QMouseEvent
from BuildDna_GraphicsMode import BuildDna_GraphicsMode
from dna_model.DnaSegment import DnaSegment

from DnaLineMode import DnaLine_GM

from drawer import drawRibbons

import math
from VQT import V, norm, A, Q, vlen
from constants import darkred, blue, black

from chem import Atom

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

        # print "selectMolsMode.update_cursor_for_no_MB(): button=",\
        #  self.o.button,"modkeys=",self.o.modkeys

        _superclass.update_cursor_for_no_MB(self)

        if self.o.modkeys is None:
            if isinstance(self.o.selobj, Atom):
                if self.o.selobj.element.role == 'strand':
                    self.o.setCursor(self.win.rotateAboutCentralAxisCursor)
                else:
                    self.o.setCursor(self.win.translateAlongCentralAxisCursor)


    def leftDown(self, event):
        """
        """
        obj = self.get_obj_under_cursor(event)

        if obj is None:
            self.cursor_over_when_LMB_pressed = 'Empty Space'


        if not isinstance(self.o.selobj, Atom):
            _superclass.leftDown(self, event)
            return
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

        self.reset_drag_vars()

        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0	

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
            
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.command.Done()


    def leftDrag(self, event):
        """
        Method called during Left drag event. 
        """
        #Duplicates some code from SelectChunks_GraphicsMode.leftDrag
        #see a to do comment below in this method
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':             
            if self.drag_handler is not None:
                self.dragHandlerDrag(self.drag_handler, event)
                    # does updates if needed
            else:
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
        #but doesn't call that method. This is because in 
        #SelectChunks_GraphicsMode.leftDrag, there is a condition statement 
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
        
        if self.command and self.command.struct:
            #Resultant axis is the axis of the segment itself. 
            resAxis = self.command.struct.getAxisVector()
            #May be we should use is_movable test below? But we know its a dna
            #segment and all its members are chunks only. Also note that 
            #movables are NOT the 'selected' objects here. 
            movables = self.command.struct.members
            if isinstance(self.o.selobj, Atom) and \
               self.o.selobj.element.role == 'axis':                
                translateAlongAxis = True
                rotateAboutAxis = False
            elif isinstance(self.o.selobj, Atom) and \
                 self.o.selobj.element.role == 'strand':
                translateAlongAxis = False
                rotateAboutAxis = True

        if translateAlongAxis:
            for mol in movables:
                mol.move(dx*resAxis)

        if rotateAboutAxis:
            self.o.assy.rotateSpecifiedMovables(Q(resAxis,-dy), 
                                                movables = movables) 
        
        self.dragdist += vlen(deltaMouse) #k needed?? [bruce 070605 comment]
        self.o.SaveMouse(event)
        self.o.assy.changed() #ninad060924 fixed bug 2278
        self.o.gl_update()
        return


    def drawHighlightedChunk(self, glpane, selobj, hicolor):
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
        if self.command and self.command.struct:
            if isinstance(self.command.struct, DnaSegment):
                for handle in self.command.handles:
                    handle.draw()
                    
        if self.command.grabbedHandle is not None:
            drawRibbons(self.command.grabbedHandle.fixedEndOfStructure,
                        self.command.grabbedHandle.currentPosition,
                           self.command.duplexRise,
                           self.glpane.scale,
                           self.glpane.lineOfSight,
                           ribbonThickness = 4.0,
                           ribbon1Color = darkred,
                           ribbon2Color = blue,
                           stepColor = black    
                        )   
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
        Method to be called duringleftUp mouse event
        """
        self.command.preview_or_finalize_structure(previewing = True)
            
        

