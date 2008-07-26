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
from utilities.debug import print_compact_traceback, print_compact_stack
from utilities.Log import orangemsg

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
    featurename = "Make Crossovers"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_DNA'

    hover_highlighting_enabled = True
    GraphicsMode_class = MakeCrossovers_Graphicsmode
   
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_gui = True
    
    flyoutToolbar = None
    
                
    def Enter(self):
        ListWidgetItems_Command_Mixin.Enter(self)    
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
            
        #Now set the initial segment list. The segments within this segment list
        #will be searched for the crossovers. 
        selectedSegments = self.win.assy.getSelectedDnaSegments()        
        self.ensureSegmentListItemsWithinLimit(selectedSegments)
                
        self.propMgr.show()    
        
    
                   
        
    def restore_gui(self):
        """
        Restore the GUI 
        """                   
        if self.propMgr is not None:
            self.propMgr.close()
            
            
    def logMessage(self, type = 'DEFAULT'): 
        """
        Updates the PM message groupbox message with the one specified below. 
        """
        msg = ''
        if type == 'ADD_SEGMENTS_ACTIVATED':
            msg = """To add new PAM3 DNA segments to the list, click on the segment's
             axis. Multiple segments can be added at once by doing a 
            rectangular lasso selection in the 3D workspace."""
        elif type == 'REMOVE_SEGMENTS_ACTIVATED':
            msg = """To remove segments from the list, click on the segment's 
            axis. Multiple segments can be removed at once by doing a 
            rectangular lasso selection in the 3D workspace."""
        elif type == 'LEFT_DRAG_STARTED':
            msg = """Transparent green spheres (if present) around the atoms indicate 
            potential crossover sites."""
        elif type == 'LEFT_DRAG_FINISHED':
            msg = self.propMgr.defaultLogMessage
        elif type == 'WARNING_LIMIT_EXCEEDED':
            msg = "Only a maximum of <b> %d </b> DNA segments can be searched for "\
                "crossover sites. Segments not added to the list"%self.itemLimitForSegmentListWidget()
            msg = orangemsg(msg)
        elif type == 'WARNING_PAM5_SEGMENT_FOUND':
            msg = """Warning: One or more of the PAM5 DNA segments have been 
            removed from the segment list.Make Crossovers command is only 
            availble for PAM3 model."""
            msg = orangemsg(msg)
        else:
            msg = self.propMgr.defaultLogMessage
        
        self.propMgr.updateMessage(msg)
            
            
    def itemLimitForSegmentListWidget(self):
        """
        Maximum number of items allowed in the segment list widet.(For 
        performance reasons)
        """
        return MAXIMUM_ALLOWED_DNA_SEGMENTS_FOR_CROSSOVER
    
    
    def ensureSegmentListItemsWithinLimit(self, segments):
        """
        """
        #Following should never happen but added as a safety
        if len(self._structList) > self.itemLimitForSegmentListWidget():
            self.logMessage('WARNING_LIMIT_EXCEEDED')
            return
        
        #Optimization
        if len(self._structList) == 0 and \
           len(segments)<= self.itemLimitForSegmentListWidget():
            self.setSegmentList(segments)
            return
        
        raw_number_of_segments =  len(self._structList) + len(segments)
        if raw_number_of_segments <= self.itemLimitForSegmentListWidget():
            for segment in segments:
                self.addSegmentToSegmentList(segment)
            return
        
        #Check how many of the segments are already in self._structList. 
        #Filter the ones that are *NOT* in self._structList. This filtered 
        #segments are the segments to add to the list
        
        def func(segment):
            if segment not in self._structList:
                return True
            return False
        
        segments_to_add = filter(lambda seg: func(seg), segments)
        
        raw_number_of_segments = len(segments_to_add) + len(self._structList)
        
        if raw_number_of_segments <= self.itemLimitForSegmentListWidget():
            for segment in segments:
                self.addSegmentToSegmentList(segment)
            return
        else:
            self.logMessage('WARNING_LIMIT_EXCEEDED')
            

    def makeAllCrossovers(self):
        """
        Make all possible crossovers
        @see: self.makeCrossover()
        """
        crossoverPairs = self.graphicsMode.get_final_crossover_pairs()
        if crossoverPairs:
            for pairs in crossoverPairs:
                self.makeCrossover(pairs, 
                                   suppress_post_crossover_updates = True)                
                
        self.graphicsMode.clearDictionaries()
        
                    
    def makeCrossover(self, 
                      crossoverPairs, 
                      suppress_post_crossover_updates = False):
        """
        Make the crossover between the atoms of the crossover pairs. 
        @param crossoverPairs: A tuple of 4 atoms between which the crossover
               will be made. Note: As of 2008-06-03, this method assumes the 
               following  form: (atom1, neighbor1, atom2, neighbor2) 
               Where all atoms are PAM3 atoms. pair of atoms atom1 and neighbor1
               are sugar atoms bonded to each other
               (same for pair atom2, neighbor2)
               The bond between these atoms will be broken first and then the 
               atoms are bonded to the opposite atoms. 
               
        @type crossoverPair: tuple
        @param suppress_post_crossover_updates: After making a crossover, this 
        method calls its graphicsMode method to do some more updates (such 
        as updating the atoms dictionaries etc.) But if its a batch process, 
        (e.g. user is calling makeAllCrossovers, this update is not needed 
        after making an individual crossover. The caller then sets this flag to 
        true to tell this method to skip that update.
        @type suppress_post_crossover_updates: boolean
        @seE:self.makeAllCrossovers()
        """
        if len(crossoverPairs) != 4:
            print_compact_stack("Bug in making the crossover.len(crossoverPairs) != 4")
            return

        atm1, neighbor1, atm2, neighbor2 = crossoverPairs
        bond1 = find_bond(atm1, neighbor1)
        if bond1:
            bond1.bust()
        
        bond2 = find_bond(atm2, neighbor2)
        if bond2:
            bond2.bust()
        #Do we need to check if these pairs are valid (i.e.a 5' end atom is 
        #bonded to a 3' end atom.. I think its not needed as its done in 
        #self._bond_two_strandAtoms. 
        self._bond_two_strandAtoms(atm1, neighbor2)
        self._bond_two_strandAtoms(atm2, neighbor1)
        
        if not suppress_post_crossover_updates:
            self.graphicsMode.update_after_crossover_creation(crossoverPairs)
                
    
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
            
        #Copied over from BuildAtoms_GraphicsMode._singletLeftUp_joinStrands()
        #The following fixes bug 2770 
        #Set the color of the whole dna strandGroup to the color of the
        #strand, whose bondpoint, is dropped over to the bondboint of the 
        #other strandchunk (thus joining the two strands together into
        #a single dna strand group) - Ninad 2008-04-09
        color = atm1.molecule.color 
        if color is None:
            color = atm1.element.color
        strandGroup1 = atm1.molecule.parent_node_of_class(self.win.assy.DnaStrand)
                   
        strandGroup2 = atm2.molecule.parent_node_of_class(
            self.win.assy.DnaStrand)                
        if strandGroup2 is not None:
            #set the strand color of strandGroup2 to the one for 
            #strandGroup1. 
            strandGroup2.setStrandColor(color)
            strandChunkList = strandGroup2.getStrandChunks()
            for c in strandChunkList:
                if hasattr(c, 'invalidate_ladder'):
                    c.invalidate_ladder()
        
        #Do the actual bonding        
        if bondPoint1 and bondPoint2:
            try:
                bond_at_singlets(bondPoint1, bondPoint2, move = False)
            except:
                print_compact_traceback("Bug: unable to bond atoms %s and %s"%(atm1, 
                                                                           atm2))
                
            if strandGroup1 is not None:
                strandGroup1.setStrandColor(color) 
                
    def updateCrossoverSites(self):
        """
        Calls the grraphics mode method that does the job of updating 
        all the crossover sites in the 3D workspace. 
        """
        self.graphicsMode.updateCrossoverSites()
           
        
    def updateExprsHandleDict(self): 
        self.graphicsMode.updateExprsHandleDict()
        
    def ensureValidSegmentList(self):
        """
        Ensures that the segments within the segment list being searched for 
        crossover sites have all valid segments (even empty list is considered
        as valid as of 2008-06-04)
        @see: MakeCrossversPropertyManager.model_changed()
        """
        pam5_segment_found = False
        for segment in self._structList:
            if not segment.is_PAM3_DnaSegment():
                pam5_segment_found = True                
                self._structList.remove(segment)
        if pam5_segment_found:
            self.logMessage('WARNING_PAM5_SEGMENT_FOUND')
            
        return pam5_segment_found
 
  
