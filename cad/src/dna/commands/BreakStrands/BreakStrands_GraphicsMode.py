# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
BreakStrands_GraphicsMode.py

@author:    Ninad
@version:   $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

History:

2008-07-01:
Split this out of BreakStrands_Command.py into its own module. 
The class was originally created in January 2008

TODO: [ as of 2008-07-01]
- bondLeftup deletes any bonds -- it should only break strands.?
"""

from geometry.VQT import norm

from utilities.constants import red
from utilities.prefs_constants import arrowsOnThreePrimeEnds_prefs_key
from utilities.prefs_constants import arrowsOnFivePrimeEnds_prefs_key
from utilities.prefs_constants import useCustomColorForThreePrimeArrowheads_prefs_key
from utilities.prefs_constants import dnaStrandThreePrimeArrowheadsCustomColor_prefs_key
from utilities.prefs_constants import useCustomColorForFivePrimeArrowheads_prefs_key
from utilities.prefs_constants import dnaStrandFivePrimeArrowheadsCustomColor_prefs_key
from utilities.prefs_constants import breakStrandsCommand_arrowsOnThreePrimeEnds_prefs_key
from utilities.prefs_constants import breakStrandsCommand_arrowsOnFivePrimeEnds_prefs_key
from utilities.prefs_constants import breakStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key
from utilities.prefs_constants import breakStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key
from utilities.prefs_constants import breakStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key
from utilities.prefs_constants import breakStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key

from utilities.constants import banana, darkgreen, red
from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.CS_draw_primitives import drawsphere, draw3DFlag
from dna.commands.BreakStrands.BreakSite_Marker import BreakSite_Marker
from dna.commands.BreakStrands.BreakSite_Marker import DEBUG_DRAW_SPHERES_AROUND_ATOMS_AT_BREAK_SITES
import time
SPHERE_RADIUS = 1.8
SPHERE_DRAWLEVEL = 2
SPHERE_OPACITY = 0.5 
CYL_RADIUS = 2.5
CYL_OPACITY = 0.6
SPHERE_RADIUS_2 =  4.0

from dna.command_support.BreakOrJoinStrands_GraphicsMode import BreakOrJoinstrands_GraphicsMode
from utilities.GlobalPreferences import DEBUG_BREAK_OPTIONS_FEATURE

_superclass = BreakOrJoinstrands_GraphicsMode


class BreakStrands_GraphicsMode(BreakOrJoinstrands_GraphicsMode ):
    """
    Graphics mode for Break Strands command.
    """
    _breakSite_marker = None

    def __init__(self, glpane):
        """
        contructor
        """
        _superclass.__init__(self, glpane)     
        self._create_breakSite_Marker_if_needed()

    def _create_breakSite_Marker_if_needed(self):
        if self._breakSite_marker is None:
            self._breakSite_marker = BreakSite_Marker(self)

    def updateBreakSites(self):
        self._breakSite_marker.update()

    def Enter_GraphicsMode(self):
        _superclass.Enter_GraphicsMode(self)  
        if DEBUG_BREAK_OPTIONS_FEATURE:
            self. _create_breakSite_Marker_if_needed()   
            self._breakSite_marker.full_update()        
        

    def _drawSpecialIndicators(self):
        """
        Overrides superclass method. 

        This draws a transparent cylinder around the segments being resized, to 
        easily distinguish them from other model. 

        @see: basicGraphicsmode._drawSpecialIndicators()

        """
        if self.command:

            if DEBUG_DRAW_SPHERES_AROUND_ATOMS_AT_BREAK_SITES: 
                breakSitesDict = self._breakSite_marker.getBreakSitesDict()

                atmList = breakSitesDict.values()     

                for atm in atmList:                  
                    sphere_radius = max(1.2*atm.drawing_radius(), 
                                        SPHERE_RADIUS)
                    drawsphere(darkgreen, 
                               atm.posn(), 
                               sphere_radius,
                               SPHERE_DRAWLEVEL,
                               opacity = SPHERE_OPACITY) 

            breakSites_atomPairs_dict = self._breakSite_marker.getBreakSites_atomPairsDict()    

            for aDict in breakSites_atomPairs_dict.values(): #DEBUG========
                for atm1, atm2 in aDict.values():
                    #Its okay to do this check for only atm1 (for speed reason) 
                    #lets assume that atm2 drawing radius will be the same (it won't
                    #be the same in very rare cases....)
                    cyl_radius = max(1.3*atm1.drawing_radius(), 
                                     CYL_RADIUS)                

                    drawcylinder(red, 
                                 atm1.posn(),
                                 atm2.posn(),
                                 cyl_radius, 
                                 capped = True,
                                 opacity = CYL_OPACITY )

            startAtomsDict = self._breakSite_marker.getStartAtomsDict()   

            for atm in startAtomsDict.values():
                sphere_radius = max(1.2*atm.drawing_radius(), 
                                    SPHERE_RADIUS_2)
                color = atm.molecule.color
                if color is None:
                    color = banana

                atom_radius = atm.drawing_radius() 
                cyl_radius = 0.5*atom_radius  
                cyl_height = 2.5*atom_radius
                axis_atm = atm.axis_neighbor()
                direction = None
                if axis_atm:
                    #Direction will be opposite of 
                    direction = norm( atm.posn() - axis_atm.posn())

                draw3DFlag(self.glpane, 
                           color, 
                           atm.posn(), 
                           cyl_radius, 
                           cyl_height,
                           direction = direction,
                           opacity = 0.8)
                            ##opacity = CYL_OPACITY)


                ##drawsphere(color, 
                            ##atm.posn(), 
                            ##sphere_radius,
                            ##SPHERE_DRAWLEVEL,
                            ##opacity = SPHERE_OPACITY)



    def _drawSpecialIndicators_ORIG(self):
        """
        Overrides superclass method. 

        This draws a transparent cylinder around the segments being resized, to 
        easily distinguish them from other model. 

        @see: basicGraphicsmode._drawSpecialIndicators()

        """
        if self.command:

            if _DEBUG_DRAW_SPHERES_AROUND_ATOMS_AT_BREAK_SITES: 
                breakSitesDict = self._breakSite_marker.getBreakSitesDict()

                atmList = breakSitesDict.values()     

                for atm in atmList:                  
                    sphere_radius = max(1.2*atm.drawing_radius(), 
                                        SPHERE_RADIUS)
                    drawsphere(darkgreen, 
                               atm.posn(), 
                               sphere_radius,
                               SPHERE_DRAWLEVEL,
                               opacity = SPHERE_OPACITY) 

            breakSites_atomPairs_dict = self._breakSite_marker.getBreakSites_atomPairsDict()    


            for atm1, atm2 in breakSites_atomPairs_dict.values():
                #Its okay to do this check for only atm1 (for speed reason) 
                #lets assume that atm2 drawing radius will be the same (it won't
                #be the same in very rare cases....)
                cyl_radius = max(1.3*atm1.drawing_radius(), 
                                 CYL_RADIUS)                

                drawcylinder(red, 
                             atm1.posn(),
                             atm2.posn(),
                             cyl_radius, 
                             capped = True,
                             opacity = CYL_OPACITY )

            startAtomsDict = self._breakSite_marker.getStartAtomsDict()   

            for atm in startAtomsDict.values():
                sphere_radius = max(1.2*atm.drawing_radius(), 
                                    SPHERE_RADIUS_2)
                color = atm.molecule.color
                if color is None:
                    color = banana

                atom_radius = atm1.drawing_radius() 
                cyl_radius = 0.5*atom_radius  
                cyl_height = 2.5*atom_radius

                draw3DFlag(self.glpane, 
                           color, 
                           atm.posn(), 
                           cyl_radius, 
                           cyl_height,
                           opacity = 0.7)
                            ##opacity = CYL_OPACITY)


                ##drawsphere(color, 
                            ##atm.posn(), 
                            ##sphere_radius,
                            ##SPHERE_DRAWLEVEL,
                            ##opacity = SPHERE_OPACITY)


    def breakStrandBonds_ORIG(self):
        breakSites_atomPairs_dict = self._breakSite_marker.getBreakSites_atomPairsDict()

        lst = list(breakSites_atomPairs_dict.keys())
        for bond in lst:
            bond.bust()

        self._breakSite_marker.update()

    def breakStrandBonds(self):
        breakSites_atomPairs_dict = self._breakSite_marker.getBreakSites_atomPairsDict()

        for aDict in breakSites_atomPairs_dict.values():
            lst = list(aDict.keys())
            for bond in lst:
                bond.bust()

        self._breakSite_marker.full_update()


    def atomLeftUp(self, a, event):
        if self.command.isSpecifyEndAtomsToolActive():           
            self._breakSite_marker.updateEndAtomsDict(a)
            self.glpane.set_selobj(None)
            self.glpane.gl_update()
            ##self.updateBreakSites()
            return 

        if self.command.isSpecifyStartAtomsToolActive():           
            self._breakSite_marker.updateStartAtomsDict(a)
            self.glpane.set_selobj(None)
            self.glpane.gl_update()
            ##self.updateBreakSites()
            return 

        _superclass.atomLeftUp(self, a, event)


    def bondLeftUp(self, b, event):
        """
        Delete the bond upon left up.
        """
        self.bondDelete(event)

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for this mode.
        """
        self.glpane.setCursor(self.win.DeleteCursor)

    def _getBondHighlightColor(self, selobj):
        """
        Return the Bond highlight color . Since its a BreakStrands graphics
        mode, the color is 'red' by default.
        @return: Highlight color of the object (Bond)

        """
        return red


    def leftDouble(self, event):
        """
        Overrides BuildAtoms_GraphicsMode.leftDouble. In BuildAtoms mode,
        left double deposits an atom. We don't want that happening here!
        """
        pass

    _GLOBAL_TO_LOCAL_PREFS_KEYS = {
        arrowsOnThreePrimeEnds_prefs_key:
        breakStrandsCommand_arrowsOnThreePrimeEnds_prefs_key,
        arrowsOnFivePrimeEnds_prefs_key:
        breakStrandsCommand_arrowsOnFivePrimeEnds_prefs_key,
        useCustomColorForThreePrimeArrowheads_prefs_key:
        breakStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key,
        useCustomColorForFivePrimeArrowheads_prefs_key:
        breakStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key,
        dnaStrandThreePrimeArrowheadsCustomColor_prefs_key:
        breakStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key,
        dnaStrandFivePrimeArrowheadsCustomColor_prefs_key:
        breakStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key,
    }

    def get_prefs_value(self, prefs_key): #bruce 080605
        """
        [overrides superclass method for certain prefs_keys]
        """
        # map global keys to local ones, when we have them
        prefs_key = self._GLOBAL_TO_LOCAL_PREFS_KEYS.get( prefs_key, prefs_key)
        return _superclass.get_prefs_value( self, prefs_key)
