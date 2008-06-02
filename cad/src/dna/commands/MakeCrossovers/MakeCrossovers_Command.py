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
      CrossoverSite_Marker
      MakeCrossovers_GraphicsMode
      

TODO  2008-06-01 :
See class CrossoverSite_Marker for details
"""
import time
import foundation.changes as changes
from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command
from dna.commands.MakeCrossovers.MakeCrossovers_GraphicsMode import MakeCrossovers_Graphicsmode
from dna.commands.MakeCrossovers.MakeCrossovers_PropertyManager import MakeCrossovers_PropertyManager
from model.bond_constants import find_bond
from model.bonds import bond_at_singlets
from utilities.debug import print_compact_traceback

from dna.commands.MakeCrossovers.ListWidgetItems_Command_Mixin import ListWidgetItems_Command_Mixin

MAXIMUM_ALLOWED_DNA_SEGMENTS_FOR_CROSSOVER = 8

_superclass = SelectChunks_Command
class MakeCrossovers_Command(SelectChunks_Command, 
                             ListWidgetItems_Command_Mixin
                             ):
    """
    
    """
    # class constants
    
    commandName = 'MAKE_CROSSOVERS'
    default_mode_status_text = ""
    featurename = 'MAKE_CROSSOVERS'
         
    hover_highlighting_enabled = True
    GraphicsMode_class = MakeCrossovers_Graphicsmode
   
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_gui = True
    
    flyoutToolbar = None
    
                
    def Enter(self):      
        
        
        ListWidgetItems_Command_Mixin.Enter(self)  
        
        #Now set the initial segment list. The segments within this segment list
        #will be searched for the crossovers. 
        selectedSegments = self.win.assy.getSelectedDnaSegments()
        if len(selectedSegments) < MAXIMUM_ALLOWED_DNA_SEGMENTS_FOR_CROSSOVER:
            self.setSegmentList(selectedSegments)
            
        _superclass.Enter(self)     


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
                self.flyoutToolbar.makeCrossoversAction.setChecked(True)
            except AttributeError:
                self.flyoutToolbar = None
        
        if self.propMgr is None:
            self.propMgr = MakeCrossovers_PropertyManager(self)
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
            

    def makeAllCrossovers(self):
        crossoverPairs = self.graphicsMode.get_final_crossover_pairs()
        if crossoverPairs:
            for pairs in crossoverPairs:
                self.makeCrossover(pairs)                
                
        self.graphicsMode.clearDictionaries()
        
                    
    def makeCrossover(self, crossoverPairs):
        atm1, neighbor1, atm2, neighbor2 = crossoverPairs
        bond1 = find_bond(atm1, neighbor1)
        if bond1:
            bond1.bust()
        
        bond2 = find_bond(atm2, neighbor2)
        if bond2:
            bond2.bust()
        
        self._bond_two_strandAtoms(atm1, neighbor2)
        self._bond_two_strandAtoms(atm2, neighbor1)
        
        self.graphicsMode.update_after_crossover(crossoverPairs)
                
    
    def _bond_two_strandAtoms(self, atm1, atm2):
        """
        Bonds the given strand atoms (sugar atoms) together. To bond these atoms, 
        it always makes sure that a 3' bondpoint on one atom is bonded to 5'
        bondpoint on the other atom. 
                
        @param atm1: The first sugar atom of PAM3 (i.e. the strand atom) to be 
                     bonded with atm2. 
        @param atm2: Second sugar atom
        @Note: This method is copied from DnaDuplex.py
        
        """
        #Moved from B_Dna_PAM3_SingleStrand to here, to fix bugs like 
        #2711 in segment resizing-- Ninad 2008-04-14
        assert atm1.element.role == 'strand' and atm2.element.role == 'strand'
        #Initialize all possible bond points to None
                
        five_prime_bondPoint_atm1  = None
        three_prime_bondPoint_atm1 = None
        five_prime_bondPoint_atm2  = None
        three_prime_bondPoint_atm2 = None
        #Initialize the final bondPoints we will use to create bonds
        bondPoint1 = None
        bondPoint2 = None
        
        #Find 5' and 3' bondpoints of atm1 (BTW, as of 2008-04-11, atm1 is 
        #the new dna strandend atom See self._fuse_new_dna_with_original_duplex
        #But it doesn't matter here. 
        for s1 in atm1.singNeighbors():
            bnd = s1.bonds[0]            
            if bnd.isFivePrimeOpenBond():
                five_prime_bondPoint_atm1 = s1                
            if bnd.isThreePrimeOpenBond():
                three_prime_bondPoint_atm1 = s1
                
        #Find 5' and 3' bondpoints of atm2
        for s2 in atm2.singNeighbors():
            bnd = s2.bonds[0]
            if bnd.isFivePrimeOpenBond():
                five_prime_bondPoint_atm2 = s2
            if bnd.isThreePrimeOpenBond():
                three_prime_bondPoint_atm2 = s2
        #Determine bondpoint1 and bondPoint2 (the ones we will bond). See method
        #docstring for details.
        if five_prime_bondPoint_atm1 and three_prime_bondPoint_atm2:
            bondPoint1 = five_prime_bondPoint_atm1
            bondPoint2 = three_prime_bondPoint_atm2
        #Following will overwrite bondpoint1 and bondPoint2, if the condition is
        #True. Doesn't matter. See method docstring to know why.
        if three_prime_bondPoint_atm1 and five_prime_bondPoint_atm2:
            bondPoint1 = three_prime_bondPoint_atm1
            bondPoint2 = five_prime_bondPoint_atm2
            
        #Do the actual bonding        
        if bondPoint1 and bondPoint2:
            try:
                bond_at_singlets(bondPoint1, bondPoint2, move = False)
            except:
                print_compact_traceback("Bug: unable to bond atoms %s and %s"%(atm1, 
                                                                           atm2))
    def updateExprsHandleDict(self): 
        self.graphicsMode.updateExprsHandleDict()
 
  