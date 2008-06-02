# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

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
from utilities.constants import banana, silver,  darkred, darkgreen, yellow
from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_draw_primitives import drawline

from dna.commands.BuildDna.BuildDna_GraphicsMode import BuildDna_GraphicsMode
from dna.commands.MakeCrossovers.ListWidgetItems_GraphicsMode_Mixin import ListWidgetItems_GraphicsMode_Mixin
from dna.commands.MakeCrossovers.CrossoverSite_Marker import CrossoverSite_Marker

SPHERE_DRAWLEVEL = 2
SPHERE_OPACITY = 0.5 
CYL_RADIUS = 1.0
CYL_OPACITY = 0.4
SPHERE_RADIUS =  2.0





_superclass = BuildDna_GraphicsMode
class MakeCrossovers_Graphicsmode(BuildDna_GraphicsMode,
                                  ListWidgetItems_GraphicsMode_Mixin):
    
    DEBUG_DRAW_PLANE_NORMALS = False
    DEBUG_DRAW_AVERAGE_CENTER_PAIRS_OF_POTENTIAL_CROSSOVERS = False
    DEBUG_DRAW_ALL_POTENTIAL_CROSSOVER_SITES =  True

    _crossoverSite_marker = None
    def __init__(self, glpane):
        _superclass.__init__(self, glpane)
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
        
    def update_after_crossover(self, crossoverPairs):
        self._crossoverSite_marker.update_after_crossover(crossoverPairs)
        
    def update_cursor_for_no_MB(self):
        """
        Update the cursor for no mouse button pressed
        """  
        _superclass.update_cursor_for_no_MB(self)
        ListWidgetItems_GraphicsMode_Mixin.update_cursor_for_no_MB(self)

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


    def Draw(self):
        _superclass.Draw(self)
        self._drawHandles()

    def _drawHandles(self):
        if self._crossoverSite_marker and self._crossoverSite_marker.handleDict:
            for handle in self._crossoverSite_marker.handleDict.values(): 
                if handle is not None: #if handle is None its a bug!
                    handle.draw()

    def _drawSpecialIndicators(self):
        final_crossover_atoms_dict = self._crossoverSite_marker.get_final_crossover_atoms_dict()
        for atm in final_crossover_atoms_dict.values():
            drawsphere(darkgreen, 
                       atm.posn(), 
                       SPHERE_RADIUS,
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
                drawsphere(silver, 
                           point, 
                           SPHERE_RADIUS,
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

    