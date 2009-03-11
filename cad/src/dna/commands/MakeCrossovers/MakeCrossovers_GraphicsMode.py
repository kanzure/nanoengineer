# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

History:
2008-05-21 - 2008-06-01 Created and further refactored and modified
@See: ListWidgetItems_Command_Mixin, 
      ListWidgetItems_GraphicsMode_Mixin
      ListWidgetItems_PM_Mixin,
      CrossoverSite_Marker,
      MakeCrossovers_Command

TODO  2008-06-01 :
See class CrossoverSite_Marker for details
"""

import foundation.env as env

from PyQt4.Qt import Qt
from utilities.constants import banana, silver,  darkred, darkgreen, yellow
from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_draw_primitives import drawline

from dna.commands.BuildDna.BuildDna_GraphicsMode import BuildDna_GraphicsMode
from dna.commands.MakeCrossovers.ListWidgetItems_GraphicsMode_Mixin import ListWidgetItems_GraphicsMode_Mixin
from dna.commands.MakeCrossovers.CrossoverSite_Marker import CrossoverSite_Marker
from utilities.prefs_constants import makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key


SPHERE_DRAWLEVEL = 2
SPHERE_OPACITY = 0.5 
CYL_RADIUS = 1.0
CYL_OPACITY = 0.4
SPHERE_RADIUS =  2.0
SPHERE_RADIUS_FOR_TAGS =  4.0


_superclass = BuildDna_GraphicsMode

class MakeCrossovers_Graphicsmode(BuildDna_GraphicsMode,
                                  ListWidgetItems_GraphicsMode_Mixin):
    
    DEBUG_DRAW_PLANE_NORMALS = False
    DEBUG_DRAW_AVERAGE_CENTER_PAIRS_OF_POTENTIAL_CROSSOVERS = False
    DEBUG_DRAW_ALL_POTENTIAL_CROSSOVER_SITES =  False
    
    _crossoverSite_marker = None
    
    _handleDrawingRequested = True
    
    #@see: self.leftADown where this flag is set.
    # It is then used in self.leftADrag.
    _should_update_crossoverSites_during_leftDrag = False
    
    #Used to log a message in the command.propMgr.See self.leftDrag, self.leftUp
    #This flag ensures that its done only once during left drag. Needs cleanup.
    #this attr was introduced just before v1.1.0 release--Ninad 2008-06-03
    _leftDrag_logMessage_emitted = False
    
    def __init__(self, glpane):
        _superclass.__init__(self, glpane)
        self._handleDrawingRequested = True
        self._createCrossoverSite_Marker_if_needed()
    
    def _createCrossoverSite_Marker_if_needed(self):
        if self._crossoverSite_marker is None:
            self._crossoverSite_marker = CrossoverSite_Marker(self)
            
    def Enter_GraphicsMode(self):
        _superclass.Enter_GraphicsMode(self)  
        self._createCrossoverSite_Marker_if_needed()
        self._crossoverSite_marker.update()
        
    def clearDictionaries(self):
        self._crossoverSite_marker.clearDictionaries()
    
    def get_final_crossover_pairs(self):
        return self._crossoverSite_marker.get_final_crossover_pairs()
               
    def updateExprsHandleDict(self):
        self._crossoverSite_marker.updateExprsHandleDict()  
        
    def update_after_crossover_creation(self, crossoverPairs):
        self._crossoverSite_marker.update_after_crossover_creation(crossoverPairs)
        
    def updateCrossoverSites(self):
        """
        Delegates  the responsibility of updating all crossover sites in the 3D
        wokspace to the self._crossoverSite_marker.
        """
        self._crossoverSite_marker.update()
        
    def update_cursor_for_no_MB(self):
        """
        Update the cursor for no mouse button pressed
        """  
        _superclass.update_cursor_for_no_MB(self)
        ListWidgetItems_GraphicsMode_Mixin.update_cursor_for_no_MB(self)
        
    def keyPressEvent(self, event):
        """
        Handles keyPressEvent. Overrides superclass method. If delete key 
        is pressed while the focus is inside the PM list widget, it deletes
        that list widget item.
        @see: ListWidgetItems_PM_Mixing.listWidgetHasFocus()
        @TODO: Calls self.command.propMgr object which is better to avoid...
        """
        if event.key() == Qt.Key_Delete:
            if self.command.propMgr and self.command.propMgr.listWidgetHasFocus():
                self.command.propMgr.removeListWidgetItems()
                return            

        _superclass.keyPressEvent(self, event)
        
    def leftADown(self, objectUnderMouse, event):
        """
        Overrides superclass method. This method also sets flag used in 
        self.leftDrag that decide whether to compute the crossover sites 
        during the left drag.Example: If user is dragging a dnaSegment that is 
        is not included in the crossover site search, it skips the computation 
        during the left drag. Thus providing a minor optimization. 
        """
        _superclass.leftADown(self, objectUnderMouse, event)        
        
        if not env.prefs[makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key]:
            self._should_update_crossoverSites_during_leftDrag = True             
        elif self._movable_dnaSegment_for_leftDrag and \
           self._movable_dnaSegment_for_leftDrag in self.command.getSegmentList():
            self._should_update_crossoverSites_during_leftDrag = True
        else:
            self._should_update_crossoverSites_during_leftDrag = False

    def chunkLeftUp(self, a_chunk, event):
        """
        Overrides superclass method. If add or remove segmets tool is active, 
        upon leftUp , when this method gets called, it modifies the list 
        of segments being resized by self.command.
        @see: self.update_cursor_for_no_MB()
        @see: self.end_selection_from_GLPane()
        """
        ListWidgetItems_GraphicsMode_Mixin.chunkLeftUp(self, a_chunk, event)
        _superclass.chunkLeftUp(self, a_chunk, event)
        
        
    def leftUp(self, event):
        _superclass.leftUp(self, event) 
        self._crossoverSite_marker.updateHandles()       
        if self._leftDrag_logMessage_emitted:
            self.command.logMessage('LEFT_DRAG_FINISED')
        if not self._handleDrawingRequested:
            self._handleDrawingRequested = True   
            
        self._leftDrag_logMessage_emitted = False
            
    def editObjectOnSingleClick(self):
        """
        Overrides superclass method. If this method returns True, 
        when you left click on a DnaSegment or a DnaStrand, it becomes editable
        (i.e. program enters the edit command of that particular object if
        that object is editable). If this returns False, program simply stays in
        the current command. 
        @see: BuildDna_GraphicsMode.editObjectOnSingleClick()
        """
        return False
        
            
    def leftDrag(self, event):
        """
        Overrides superclass method. Also updates the potential crossover sites.
        """
        _superclass.leftDrag(self, event)
        self._handleDrawingRequested = False   
        if self._should_update_crossoverSites_during_leftDrag:
            self._crossoverSite_marker.partialUpdate()
            if not self._leftDrag_logMessage_emitted:
                self._leftDrag_logMessage_emitted = True
                self.command.logMessage('LEFT_DRAG_STARTED')

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

        ListWidgetItems_GraphicsMode_Mixin.end_selection_from_GLPane(self)


    def Draw_other(self):
        _superclass.Draw_other(self)
        if self._handleDrawingRequested:
            self._drawHandles()

    def _drawHandles(self):
        if self._crossoverSite_marker and self._crossoverSite_marker.handleDict:
            for handle in self._crossoverSite_marker.handleDict.values(): 
                if handle is not None: #if handle is None its a bug!
                    handle.draw()                    
    

    def _drawSpecialIndicators(self):
        final_crossover_atoms_dict = self._crossoverSite_marker.get_final_crossover_atoms_dict()
        for atm in final_crossover_atoms_dict.values():
            sphere_radius = max(1.20*atm.drawing_radius(), 
                                SPHERE_RADIUS)
            drawsphere(darkgreen, 
                       atm.posn(), 
                       sphere_radius,
                       SPHERE_DRAWLEVEL,
                       opacity = SPHERE_OPACITY) 

        if self.DEBUG_DRAW_ALL_POTENTIAL_CROSSOVER_SITES:
            atom_dict = self._crossoverSite_marker.get_base_orientation_indicator_dict()
            for atm in atom_dict.values():
                drawsphere(darkred, 
                           atm.posn(), 
                           1.5,
                           SPHERE_DRAWLEVEL,
                           opacity = SPHERE_OPACITY) 

        if self.DEBUG_DRAW_PLANE_NORMALS:    
            self._DEBUG_drawPlaneNormals()

        if self.DEBUG_DRAW_AVERAGE_CENTER_PAIRS_OF_POTENTIAL_CROSSOVERS:
            self._DEBUG_draw_avg_centerpairs_of_potential_crossovers()


    def _drawTags(self):
        """
        Overrides _superClass._drawTags()
        for self._tagPositions.
        @see: self.drawTag()
        @see: GraphicsMode._drawTags()
        @see: class PM_SelectionWidget
        """ 
       
        if self._tagPositions:
            for point in self._tagPositions:          
                drawsphere(banana, 
                           point, 
                           SPHERE_RADIUS_FOR_TAGS ,
                           SPHERE_DRAWLEVEL,
                           opacity = SPHERE_OPACITY)

    
    def _DEBUG_drawPlaneNormals(self):
        ends = self._crossoverSite_marker.get_plane_normals_ends_for_drawing()
        for end1, end2 in ends:
            drawcylinder(banana, 
                         end1,
                         end2,
                         CYL_RADIUS, 
                         capped = True,
                         opacity = CYL_OPACITY )

    def _DEBUG_draw_avg_centerpairs_of_potential_crossovers(self):
        pairs = self._crossoverSite_marker.get_avg_center_pairs_of_potential_crossovers
        for pair in pairs:
            drawline(yellow, pair[0], pair[1], width = 2)

    
