# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
@author:    Ninad
@version:   $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: [ as of 2008-01-04]
- To be revised heavily . Still a stub, needs documentation.
"""

from dna.command_support.BreakOrJoinStrands_Command import BreakOrJoinStrands_Command
from dna.commands.BreakStrands.BreakStrands_PropertyManager import BreakStrands_PropertyManager
from dna.commands.BreakStrands.BreakStrands_GraphicsMode import BreakStrands_GraphicsMode

#debug flag for experimental code Ninad is
#working on (various break strands options)
from utilities.GlobalPreferences import DEBUG_BREAK_OPTIONS_FEATURE

_superclass = BreakOrJoinStrands_Command
class BreakStrands_Command(BreakOrJoinStrands_Command):
    """

    """
    # class constants
    commandName = 'BREAK_STRANDS'
    featurename = "Break Strands"    
    GraphicsMode_class = BreakStrands_GraphicsMode

    def _createPropMgrObject(self):
        propMgr = BreakStrands_PropertyManager(self)
        return propMgr    
    
    def _get_init_gui_flyout_action_string(self):
        return 'breakStrandAction'
    
    #===========================================================================
    #Methods used in experimental feature that provide various break options
    #these are not called but thhe methods do have a safety check to 
    #see id DEBUG_BREAK_OPTIONS_FEATURE is set to True. -- ninad 2008-08-06
            
    
    def getStrandList(self):     
        part = self.win.assy.part
        return part.get_topmost_subnodes_of_class(self.win.assy.DnaStrand)
    
    def isSpecifyEndAtomsToolActive(self):
        return False
    
    def isSpecifyStartAtomsToolActive(self):
        if not DEBUG_BREAK_OPTIONS_FEATURE:
            return False        
        return True
    
    def getNumberOfBasesBeforeNextBreak(self):
        if not DEBUG_BREAK_OPTIONS_FEATURE:
            return 2
        
        if self.propMgr:
            return self.propMgr.getNumberOfBasesBeforeNextBreak()
        
        return 2
    
    def breakStrandBonds(self):        
        if not DEBUG_BREAK_OPTIONS_FEATURE:
            return
        
        self.graphicsMode.breakStrandBonds()
        
    def updateBreakSites(self):
        if not DEBUG_BREAK_OPTIONS_FEATURE:
            return
        self.graphicsMode.updateBreakSites()
        
    #===========================================================================
