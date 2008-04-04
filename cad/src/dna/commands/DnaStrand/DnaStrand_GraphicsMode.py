# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Graphics mode intended to be used while in DnaStrand_EditCommand. 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created 2008-02-14

"""
from dna.commands.BuildDna.BuildDna_GraphicsMode import BuildDna_GraphicsMode
from temporary_commands.TemporaryCommand import ESC_to_exit_GraphicsMode_preMixin
from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT
from graphics.drawing.drawDnaRibbons import drawDnaSingleRibbon
from utilities.constants import darkred, blue, black, red, darkgreen


_superclass = BuildDna_GraphicsMode

class DnaStrand_GraphicsMode(ESC_to_exit_GraphicsMode_preMixin,
                             BuildDna_GraphicsMode):
    
    _handleDrawingRequested = True
    cursor_over_when_LMB_pressed = ''
    
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
                       
        #If the cursor was not over something that belonged to structure 
        #being edited (example - atom or bond of a DnaSegment) don't 
        #do left drag.(left drag will work only for the DnaStrand being edited)
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
            self.command.updateHandlePositions()
            if not self._handleDrawingRequested:
                self._handleDrawingRequested = True
        
        #@see: comment in DnaSegment_GraphicsMode.leftUp on why the following 
        #doesn't call command.preview_finialize_structure before calling 
        #command.Done()
        #IMPLEMENTATION CHANGE 2008-03-05. 
        #Due to an implementation change, user is not allowed to 
        #exit this command by simply clicking onto empty space. So following 
        #is commented out. (Keeping it for now just in case we change our mind
        #soon. If you see this code being commented out even after 1 or 2 months
        #from the original comment date, please just delete it. 
        #--Ninad 2008-03-05
        ##if self.cursor_over_when_LMB_pressed == 'Empty Space':
            ##self.command.Done()
    
    def Draw(self):
        """
        Draw this DnaStrand object and its contents including handles (if any.)
        """
        if self._handleDrawingRequested:
            self._drawHandles()     
        _superclass.Draw(self)
        
    def _drawHandles(self):
        """
        Draw the handles for the command.struct 
        @see: DnaStrand_ResizeHandle.hasValidParamsForDrawing ()
        """    
        if self.command and self.command.hasValidStructure():            
            for handle in self.command.handles:
                #Check if handle's center (origin) and direction are 
                #defined. (ONLY checks if those are not None)
                if handle.hasValidParamsForDrawing():
                    handle.draw()
                
        if self.command.grabbedHandle is not None:
            params = self.command.getDnaRibbonParams()
            if params:
                end1, end2, basesPerTurn, duplexRise, \
                    ribbon1_start_point, ribbon1Color = params
                drawDnaSingleRibbon(end1,
                               end2,
                               basesPerTurn,
                               duplexRise,
                               self.glpane.scale,
                               self.glpane.lineOfSight,
                               self.glpane.displayMode,
                               ribbon1_start_point = ribbon1_start_point,
                               ribbonThickness = 4.0,
                               ribbon1Color = ribbon1Color,
                               stepColor = black )
            #Draw the text next to the cursor that gives info about 
            #number of base pairs etc
            if self.command:
                text , textColor = self.command.getCursorText()
                self.glpane.renderTextNearCursor(text, 
                                                 offset = 30,
                                                 color = textColor
                                             )
        