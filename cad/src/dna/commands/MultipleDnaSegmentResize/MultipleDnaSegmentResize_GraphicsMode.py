# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
MultipleDnaSegmentResize_GraphicsMode.py 

Graphics mode for resizing multiple dna segments at once

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
see MultipleDnaSegmentResize_EditCommand
"""
from dna.commands.DnaSegment.DnaSegment_GraphicsMode import DnaSegment_GraphicsMode
from PyQt4.Qt import Qt
from graphics.drawing.drawDnaRibbons import drawDnaRibbons
import foundation.env as env
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import DarkBackgroundContrastColor_prefs_key
from utilities.constants import black, banana, silver, lighterblue, darkred
from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.CS_draw_primitives import drawsphere

SPHERE_RADIUS = 6.0
SPHERE_DRAWLEVEL = 2
SPHERE_OPACITY = 0.5 
CYL_RADIUS = 13.0
CYL_OPACITY = 0.4
SPHERE_RADIUS_2 =  3.0

_superclass = DnaSegment_GraphicsMode
class MultipleDnaSegmentResize_GraphicsMode(DnaSegment_GraphicsMode):
    """
    Graphics mode for resizing multiple dna segments at once
    """

    def Enter_GraphicsMode(self):        
        _superclass.Enter_GraphicsMode(self)
        #@TODO: Deselect everything. Is it Ok to do??
        self.win.assy.unpickall_in_GLPane()

    
    def update_cursor_for_no_MB(self):
        """
        Update the cursor for no mouse button pressed
        """       

        if self.command:
            if self.command.isAddSegmentsToolActive():
                self.o.setCursor(self.win.addSegmentToResizeSegmentListCursor)
                return
            if self.command.isRemoveSegmentsToolActive():
                self.o.setCursor(self.win.removeSegmentFromResizeSegmentListCursor)
                return

        _superclass.update_cursor_for_no_MB(self)
        
    def chunkLeftUp(self, a_chunk, event):
        """
        Overrides superclass method. If add or remove segmets tool is active, 
        upon leftUp , when this method gets called, it modifies the list 
        of segments being resized by self.command.
        @see: self.update_cursor_for_no_MB()
        @see: self.end_selection_from_GLPane()
        """
        if self.command.isAddSegmentsToolActive() or \
           self.command.isRemoveSegmentsToolActive():            
            if a_chunk.isAxisChunk():   
                segmentGroup = a_chunk.parent_node_of_class(
                    self.win.assy.DnaSegment)
                if segmentGroup is not None:
                    if self.command.isAddSegmentsToolActive():
                        self.command.addSegmentToResizeSegmentList(segmentGroup)
                    if self.command.isRemoveSegmentsToolActive():
                        self.command.removeSegmentFromResizeSegmentList(segmentGroup)

            self.end_selection_from_GLPane()
            return

        _superclass.chunkLeftUp(self, a_chunk, event)


    def end_selection_from_GLPane(self):
        """
        Overrides superclass method.  In addition to selecting  or deselecting 
        the chunk, if  a tool that adds Dna segments to the segment list in 
        the property manager is active, this method also adds 
        the selected dna segments to that list. Example, if user selects 
        'Add Dna segments' tool and does a lasso selection , then this also
        method adds the selected segments to the list. Opposite behavior if 
        the 'remove segments from segment list too, is active)
        """
        _superclass.end_selection_from_GLPane(self)
        selectedSegments = self.win.assy.getSelectedDnaSegments()
        for segment in selectedSegments:
            if self.command.isAddSegmentsToolActive():
                self.command.addSegmentToResizeSegmentList(segment)
            if self.command.isRemoveSegmentsToolActive():
                self.command.removeSegmentFromResizeSegmentList(segment)


    def keyPressEvent(self, event):
        """
        Handles keyPressEvent. Overrides superclass method. If delete key 
        is pressed while the focus is inside the PM list widget, it deletes
        that list widget item.
        @see: MultipleDnaSegmentResize_PropertyManager.listWidgetHasFocus()
        @TODO: alls self.command.propMgr object which is better to avoid...
        """
        if event.key() == Qt.Key_Delete:
            if self.command.propMgr and self.command.propMgr.listWidgetHasFocus():
                self.command.propMgr.removeListWidgetItems()
                return            

        _superclass.keyPressEvent(self, event)
        
    
    def _drawSpecialIndicators(self):
        """
        Overrides superclass method. 
        
        This draws a transparent cylinder around the segments being resized, to 
        easily distinguish them from other model. 
        
        @see: basicGraphicsmode._drawSpecialIndicators()

        """
        if self.command:
            segmentList = self.command.getResizeSegmentList()
            for segment in segmentList:
                end1, end2 =  segment.getAxisEndPoints()
                if end1 is not None and end2 is not None:
                    drawcylinder(banana, 
                                 end1,
                                 end2,
                                 CYL_RADIUS, 
                                 capped = True,
                                 opacity = CYL_OPACITY )

    def _drawTags(self):
        """
        Overrides _superClass._drawTags()
        for self._tagPositions.
        @see: self.drawTag()
        @see: GraphicsMode._drawTags()
        @see: class PM_SelectionWidget
        """ 
        if 0:
            #see method for details. Used for debugging only
            self._DEBUG_Flag_EndPoint1_ofDnaSegments()

        if self._tagPositions:
            for point in self._tagPositions:          
                drawsphere(silver, 
                           point, 
                           SPHERE_RADIUS,
                           SPHERE_DRAWLEVEL,
                           opacity = SPHERE_OPACITY)

    def _DEBUG_Flag_EndPoint1_ofDnaSegments(self):
        """
        Temporary method that draws a sphere to indicate the endPoint1 
        of each segment being resized. Used for debugging a bug in 
        computing average end points for the resize handles.
        """
        if not self.command:
            return 

        endPoints_1 = []
         
        for segment in self.command.getResizeSegmentList():
            e1, e2 = segment.getAxisEndPoints()
            if e1 is not None:
                endPoints_1.append(e1)
        for end1 in endPoints_1:
            drawsphere(lighterblue, 
                       end1, 
                       SPHERE_RADIUS,
                       SPHERE_DRAWLEVEL,
                       opacity = 1.0)

    def _drawDnaRubberbandLine(self):
        """
        Overrides superclass method. It loops through the segments being resized
        and draws the rubberband lines for all. NOT this could be SLOW
        @see: MultipleDnaSegmentResize_EditCommand.getDnaRibbonParams() for 
              comments.
        @TODO: needs more cleanup
        """

        handleType = ''
        if self.command.grabbedHandle is not None:
            if self.command.grabbedHandle in [self.command.rotationHandle1, 
                                              self.command.rotationHandle2]:
                handleType = 'ROTATION_HANDLE'
            else:
                handleType = 'RESIZE_HANDLE'

        if handleType and handleType == 'RESIZE_HANDLE': 
            #Use the text color that better contrasts with the background color. 
            #mitigates bug 2927
            textColor = self.glpane.get_background_contrast_color()
            for segment in self.command.getResizeSegmentList():  
                self.command.currentStruct = segment
                params_when_adding_bases, params_when_removing_bases = \
                                        self.command.getDnaRibbonParams() 

                
                if params_when_adding_bases:
                    end1, \
                        end2, \
                        basesPerTurn,\
                        duplexRise, \
                        ribbon1_start_point, \
                        ribbon2_start_point, \
                        ribbon1_direction, \
                        ribbon2_direction, \
                        ribbon1Color, \
                        ribbon2Color = params_when_adding_bases 


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
                                   ) 
                    
                    #Draw a sphere that indicates the current position of 
                    #the resize end of each segment . 
                    drawsphere(env.prefs[selectionColor_prefs_key], 
                               end2, 
                               SPHERE_RADIUS_2,
                               SPHERE_DRAWLEVEL,
                               opacity = SPHERE_OPACITY) 
                    
                    
                    #Draw the text next to the cursor that gives info about 
                    #number of base pairs etc            
                    self._drawCursorText(position = end2)

                
                elif params_when_removing_bases:
                    end2 = params_when_removing_bases
                    #Draw a sphere that indicates the current position of 
                    #the resize end of each segment.
                    drawsphere(darkred, 
                               end2, 
                               SPHERE_RADIUS_2,
                               SPHERE_DRAWLEVEL,
                               opacity = SPHERE_OPACITY)   
                    
                    
                    #Draw the text next to the cursor that gives info about 
                    #number of base pairs etc            
                    self._drawCursorText(position = end2)
                
                #Reset the command.currentStruct to None. (it is set to 'segment' 
                #at the beginning of the for loop.
                self.command.currentStruct = None
                                
