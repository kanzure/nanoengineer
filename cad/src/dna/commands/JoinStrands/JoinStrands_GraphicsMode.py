# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

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

from dna.command_support.BreakOrJoinStrands_GraphicsMode import BreakOrJoinstrands_GraphicsMode

_superclass_for_GM = BreakOrJoinstrands_GraphicsMode

class JoinStrands_GraphicsMode( BreakOrJoinstrands_GraphicsMode ):
    """
    Graphics mode for Join strands command
    
    """  
    exit_command_on_leftUp = False
        #@TODO: This is a flag that may be set externally by previous commands.
        #Example: In BuildDna_EditCommand (graphicsMode), if you want to join 
        #two strands, upon 'singletLeftDown' of *that command's* graphicsMode,  
        #it enters JoinStrands_Command (i.e. this command and GM), also calling 
        #leftDown method of *this* graphicsmode. Now, when user releases the 
        #left mouse button, it calls leftUp method of this graphics mode, which 
        #in turn exits this command if this flag is set to True
        #(to go back to the previous command user was in) . This is a bit
        #confusing but there is no easy way to implement the functionality 
        #we need in the BuildDna command (ability to Join the strands) . 
        #A lot of code that does bondpoint dragging is available in 
        #BuildAtoms_GraphicsMode, but it isn't in BuildDna_GraphicsMode 
        #(as it is a  SelectChunks_GraphicsMode superclass for lots of reasons)
        #So, for some significant amount of time, we may continue to use 
        #this flag to temporarily enter/exit this command.
        #@see: self.leftUp(), BuildDna_GraphicsMode.singletLeftDown()
        # [-- Ninad 2008-05-02]
        
 
    
    def leftDouble(self, event):
        """
        Overrides BuildAtoms_GraphicsMode.leftDouble. In BuildAtoms mode,
        left double deposits an atom. We don't want that happening here!
        """
        pass
    
    def leftUp(self, event):
        """
        Handles mouse leftUp event.
        @see: BuildDna_GraphicsMode.singletLeftDown()
        """
        _superclass_for_GM.leftUp(self, event)
        
        #See a detailed comment about this class variable after 
        #class definition
        if self.exit_command_on_leftUp:
            self.exit_command_on_leftUp = False
            #Exit this GM's command (i.e. the command 'JoinStrands')
            self.command.command_Done()
 
            
    def deposit_from_MMKit(self, atom_or_pos):
        """
        OVERRIDES superclass method. Returns None as of 2008-05-02
        
        
        Deposit the library part being previewed into the 3D workspace
        Calls L{self.deposit_from_Library_page}

        @param atom_or_pos: If user clicks on a bondpoint in 3D workspace,
                            this is that bondpoint. NE1 will try to bond the 
                            part to this bondpoint, by Part's hotspot(if exists)
                            If user double clicks on empty space, this gives 
                            the coordinates at that point. This data is then 
                            used to deposit the item.
        @type atom_or_pos: Array (vector) of coordinates or L{Atom}

        @return: (deposited_stuff, status_msg_text) Object deposited in the 3 D 
                workspace. (Deposits the selected  part as a 'Group'. The status
                message text tells whether the Part got deposited.
        @rtype: (L{Group} , str)

        """
        #This is a join strands command and we don't want anything to be 
        #deposited from the MMKit. So simply return None. 
        #Fixes bug 2831
        return None

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
        return _superclass_for_GM.get_prefs_value( self, prefs_key)
    