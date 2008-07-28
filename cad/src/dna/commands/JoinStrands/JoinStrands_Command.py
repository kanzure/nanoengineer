# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: 
Many changes planned in JoinStrands_GraphicsMode . 
"""
import foundation.changes as changes

from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from dna.commands.JoinStrands.JoinStrands_PropertyManager import JoinStrands_PropertyManager

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


# == GraphicsMode part

_superclass_for_GM = BuildAtoms_GraphicsMode

class JoinStrands_GraphicsMode( BuildAtoms_GraphicsMode ):
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
            self.command.Done()
 
            
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

    
# == Command part

class JoinStrands_Command(BuildAtoms_Command): 
    """
    Command part for joining two strands. 
    
    """
    # class constants
    
    commandName = 'JOIN_STRANDS'
    featurename = "Join Strands"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_DNA'

    hover_highlighting_enabled = True
    GraphicsMode_class = JoinStrands_GraphicsMode
   
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_gui = True
    
    flyoutToolbar = None

    
    def init_gui(self):
        """
        Initialize GUI for this mode 
        """
        self._init_gui_flyout_action( 'joinStrandsAction' ) 
        
        if self.propMgr is None:
            self.propMgr = JoinStrands_PropertyManager(self)
            #@bug BUG: following is a workaround for bug 2494.
            #This bug is mitigated as propMgr object no longer gets recreated
            #for modes -- niand 2007-08-29
            changes.keep_forever(self.propMgr)  
            
        self.propMgr.show()    
       
        
    def restore_gui(self):
        """
        Restore the GUI 
        """
                    
        if self.propMgr is not None:
            self.propMgr.close()
    
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that dna_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """
        
        bool_keep = BuildAtoms_Command.keep_empty_group(self, group)
        
        if not bool_keep:
            #Lets just not delete *ANY* DnaGroup while in JoinStrands_Command
            #Reason same as the one explained in 
            #.. BreakStrands_Command.keep_empty_group()
                       
            if isinstance(group, self.assy.DnaGroup):
                bool_keep = True                                
        
        return bool_keep
