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
The class was originally in January 2008

TODO: [ as of 2008-07-01]
- bondLeftup deletes any bonds -- it should only break strands.?
"""

from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode

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

from temporary_commands.TemporaryCommand import ESC_to_exit_GraphicsMode_preMixin

_superclass = BuildAtoms_GraphicsMode

class BreakStrands_GraphicsMode( ESC_to_exit_GraphicsMode_preMixin,
                                 BuildAtoms_GraphicsMode ):
    """
    Graphics mode for Break Strands command.
    """

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
