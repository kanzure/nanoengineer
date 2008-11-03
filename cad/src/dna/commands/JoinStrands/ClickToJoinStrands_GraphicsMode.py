# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-10-21 : Created

TODO:
"""

from utilities.prefs_constants import arrowsOnThreePrimeEnds_prefs_key
from utilities.prefs_constants import arrowsOnFivePrimeEnds_prefs_key 
from utilities.prefs_constants import useCustomColorForThreePrimeArrowheads_prefs_key 
from utilities.prefs_constants import dnaStrandThreePrimeArrowheadsCustomColor_prefs_key 
from utilities.prefs_constants import useCustomColorForFivePrimeArrowheads_prefs_key 
from utilities.prefs_constants import dnaStrandFivePrimeArrowheadsCustomColor_prefs_key 

from utilities.prefs_constants import joinStrandsCommand_arrowsOnThreePrimeEnds_prefs_key
from utilities.prefs_constants import joinStrandsCommand_arrowsOnFivePrimeEnds_prefs_key 
from utilities.prefs_constants import joinStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key 
from utilities.prefs_constants import joinStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key 
from utilities.prefs_constants import joinStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key 
from utilities.prefs_constants import joinStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key 


from dna.commands.BuildDna.BuildDna_GraphicsMode import BuildDna_GraphicsMode

_superclass = BuildDna_GraphicsMode
class ClickToJoinStrands_GraphicsMode(BuildDna_GraphicsMode):
    
    def update_cursor_for_no_MB(self):
        """
        Update the cursor for no mouse button pressed
        """            
        _superclass.update_cursor_for_no_MB(self)
        
        if self.command and self.o.selobj is None:
            self.o.setCursor(self.win.clickToJoinStrandsCursor)
                    
    
    def editObjectOnSingleClick(self):
        """
        Subclasses can override this method. If this method returns True,
        when you left click on a DnaSegment or a DnaStrand, it becomes editable
        (i.e. program enters the edit command of that particular object if
        that object is editable)
        @see: MakeCrossover_GraphicsMode.editObjectOnSingleClick()
        """
        return False
    
    def chunkLeftUp(self, aChunk, event):
        """
        Upon chunkLeftUp, join the 3' end of a strand with a five prime end of 
        a neighboring strand. 
        @see: ClickToJoinStrands_Command.joinNeighboringStrands() which 
        is called here. 
        """

        _superclass.chunkLeftUp(self, aChunk, event)
        
        
        strand = aChunk.getDnaStrand()        
        self.command.joinNeighboringStrands(strand)
    
    
    _GLOBAL_TO_LOCAL_PREFS_KEYS = {
        arrowsOnThreePrimeEnds_prefs_key:
            joinStrandsCommand_arrowsOnThreePrimeEnds_prefs_key,
        arrowsOnFivePrimeEnds_prefs_key:
            joinStrandsCommand_arrowsOnFivePrimeEnds_prefs_key,
        useCustomColorForThreePrimeArrowheads_prefs_key:
            joinStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key,
        useCustomColorForFivePrimeArrowheads_prefs_key:
            joinStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key,
        dnaStrandThreePrimeArrowheadsCustomColor_prefs_key:
            joinStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key,
        dnaStrandFivePrimeArrowheadsCustomColor_prefs_key:
            joinStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key,
     }
        
    def get_prefs_value(self, prefs_key): #bruce 080605
        """
        [overrides superclass method for certain prefs_keys]
        """
        # map global keys to local ones, when we have them
        prefs_key = self._GLOBAL_TO_LOCAL_PREFS_KEYS.get( prefs_key, prefs_key)
        return _superclass.get_prefs_value( self, prefs_key)