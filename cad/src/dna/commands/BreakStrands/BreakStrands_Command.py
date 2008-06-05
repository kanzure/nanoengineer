# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: [ as of 2008-01-04]
- To be revised heavily . Still a stub, needs documentation.
- bondLeftup deletes any bonds -- it should only break strands. 
- Move BreakStrands_GraphicsMode into its own module when need arises. 
"""

import foundation.changes as changes
import foundation.env as env
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from utilities.constants import red
from dna.commands.BreakStrands.BreakStrands_PropertyManager import BreakStrands_PropertyManager

from utilities.prefs_constants import breakStrandsCommand_arrowsOnThreePrimeEnds_prefs_key
from utilities.prefs_constants import breakStrandsCommand_arrowsOnFivePrimeEnds_prefs_key 
from utilities.prefs_constants import breakStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key 
from utilities.prefs_constants import breakStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key 
from utilities.prefs_constants import breakStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key 
from utilities.prefs_constants import breakStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key 


from temporary_commands.TemporaryCommand import ESC_to_exit_GraphicsMode_preMixin
# == GraphicsMode part

_superclass_for_GM = BuildAtoms_GraphicsMode

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
    
    def pref_arrowsOnThreePrimeEnds(self):
        """
        Return the appropriate value of the preference for whether to
        draw arrows on 3' strand ends of PAM DNA.
        [overrides superclass method, using different prefs_key]
        """
        return env.prefs[breakStrandsCommand_arrowsOnThreePrimeEnds_prefs_key]

    def pref_arrowsOnFivePrimeEnds(self):
        """
        Return the appropriate value of the preference for whether to
        draw arrows on 5' strand ends of PAM DNA.

        [overrides superclass method, using different prefs_key]
        """
        return env.prefs[breakStrandsCommand_arrowsOnFivePrimeEnds_prefs_key]

    def pref_useCustomColorForThreePrimeArrowheads(self):
        """
        Return the appropriate value of the preference for whether to use a
        custom color for 3' arrowheads (if they are drawn)
        or for 3' strand end atoms (if arrowheads are not drawn).

        [overrides superclass method, using different prefs_key]
        """
        return env.prefs[breakStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key]

    def pref_useCustomColorForFivePrimeArrowheads(self):
        """
        Return the appropriate value of the preference for whether to use a
        custom color for 5' arrowheads (if they are drawn)
        or for 5' strand end atoms (if arrowheads are not drawn).
        [overrides superclass method, using different prefs_key]
        """
        return env.prefs[breakStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key]

    def pref_dnaStrandThreePrimeArrowheadsCustomColor(self):
        """
        Return the appropriate value of the preference for what custom color
        to use when drawing 3' arrowheads (if they are drawn)
        or 3' strand end atoms (if arrowheads are not drawn).
        [overrides superclass method, using different prefs_key]

        """
        return env.prefs[breakStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key]

    def pref_dnaStrandFivePrimeArrowheadsCustomColor(self):
        """
        Return the appropriate value of the preference for what custom color
        to use when drawing 5' arrowheads (if they are drawn)
        or 5' strand end atoms (if arrowheads are not drawn).
        [overrides superclass method, using different prefs_key]
        """
        return env.prefs[breakStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key]
        
    
  
# == Command part


class BreakStrands_Command(BuildAtoms_Command): 
    """
    
    """
    # class constants
    
    commandName = 'BREAK_STRANDS'
    default_mode_status_text = ""
    featurename = "Break Strands"
         
    hover_highlighting_enabled = True
    GraphicsMode_class = BreakStrands_GraphicsMode
   
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_gui = True
    
    flyoutToolbar = None

    def init_gui(self):
        """
        Initialize GUI for this mode 
        """
        previousCommand = self.commandSequencer.prevMode 
        if previousCommand.commandName == 'BUILD_DNA':
            try:
                self.flyoutToolbar = previousCommand.flyoutToolbar
                #Need a better way to deal with changing state of the 
                #corresponding action in the flyout toolbar. To be revised 
                #during command toolbar cleanup 
                self.flyoutToolbar.breakStrandAction.setChecked(True)
            except AttributeError:
                self.flyoutToolbar = None
        
        if self.propMgr is None:
            self.propMgr = BreakStrands_PropertyManager(self)
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
            #Lets just not delete *ANY* DnaGroup while in BreakStrands_Command
            #Although BreakStrands command can only be accessed through
            #BuildDna_EditCommand, it could happen (due to a bug) that the 
            #previous command is not BuildDna_Editcommand. So bool_keep 
            #in that case will return False propmting dna updater to even delete
            #the empty DnaGroup (if it becomes empty for some reasons) of the 
            #BuildDna command. To avoid this ,this method will instruct 
            # to keep all instances of DnaGroup even when they might be empty.            
            if isinstance(group, self.assy.DnaGroup):
                bool_keep = True
            #Commented out code that shows what I was planning to implement 
            #earlier. 
            ##previousCommand = self.commandSequencer.prevMode 
            ##if previousCommand.commandName == 'BUILD_DNA':
                ##if group is previousCommand.struct:
                    ##bool_keep = True                                
        
        return bool_keep