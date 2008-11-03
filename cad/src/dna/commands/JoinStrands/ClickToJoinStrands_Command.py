# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

History:
2008-10-22: Created to support single click join strand operation 
Example: while in this command, if user clicks anywhere on a strand, its 3'end
is joined to the nearest 5' end on the same dnasegment.

TODOs as of 2008-10-26: 
- Method _bond_two_strandAtoms needs refactoring and to be moved to a dna_helper
package. 
"""
import foundation.env as env
from dna.commands.JoinStrands.JoinStrands_PropertyManager import JoinStrands_PropertyManager
from commands.Select.Select_Command import Select_Command
from dna.commands.JoinStrands.ClickToJoinStrands_GraphicsMode import ClickToJoinStrands_GraphicsMode
import foundation.env as env
from utilities.prefs_constants import joinStrandsCommand_clickToJoinDnaStrands_prefs_key
from utilities.debug import print_compact_stack
from utilities.constants import CL_SUBCOMMAND
from model.bonds import bond_at_singlets
from geometry.NeighborhoodGenerator import NeighborhoodGenerator 
from utilities.prefs_constants import joinStrandsCommand_recursive_clickToJoinDnaStrands_prefs_key
# == Command part

_superclass = Select_Command
class ClickToJoinStrands_Command(Select_Command): 
    """
    Command part for joining two strands. 
    @see: superclass B{BreakOrJoinStrands_Command} 
    """
    # class constants
    
    commandName = 'CLICK_TO_JOIN_STRANDS'
    featurename = "Click To Join Strands"   
    GraphicsMode_class = ClickToJoinStrands_GraphicsMode     
    
    FlyoutToolbar_class = None    
    command_should_resume_prevMode = False
    command_has_its_own_PM = False
                
    #class constants for the NEW COMMAND API -- 2008-07-30
    command_level = CL_SUBCOMMAND
    command_parent = 'JOIN_STRANDS'
    
               
    def command_update_state(self):
        """
        See superclass for documentation. 
        Note that this method is called only when self is the currentcommand on 
        the command stack. 
        @see: BuildAtomsFlyout.resetStateOfActions()
        @see: self.activateAtomsTool()
        """
        _superclass.command_update_state(self)
        
        #Make sure that the command Name is JOIN_STRANDS. (because subclasses 
        #of JoinStrands_Command might be using this method). 
        #As of 2008-10-23, if the checkbox 'Click on strand to join'
        #in the join strands PM is checked, NE1 will enter a command that 
        #implements different mouse behavior in its graphics mode and will stay
        #there. 
        if self.commandName == 'CLICK_TO_JOIN_STRANDS' and \
           not env.prefs[joinStrandsCommand_clickToJoinDnaStrands_prefs_key]:
            
            self.command_Done()
            
    def joinNeighboringStrands(self, strand, endChoice = 'THREE_PRIME_END'):
        """
        Join the 3 or 5' end of the given strand with a 5' or 3' (respt) end of 
        a neighboring strand, on the SAME DnaSegment. 
        
        @param strand: The DnaStrand whose 3' or 5' end will be joined with 
                       the 5' or 3' end base atom (respectively) on a 
                       neighboring strand of the same DnaSegment. 
        @type strand: DnaStrand              
        @see: self._bond_two_strandAtoms()
        @TODO: implement code when endChoice is 'Five prime end'. At the moment,
        it works only for the the 3' end atom of <strand>.
        
        @see: ClickToJoinStrands_GraphicsMode.chunkLeftUp()
        """
        
        if not isinstance(strand, self.assy.DnaStrand):
            print_compact_stack("bug: %s is not a DnaStrand instance"%strand)
            return
        
        if endChoice == 'THREE_PRIME_END':
            current_strand = strand
            
            count = 0
            
            #This implements a NFR by Mark. Recursively join the DnaStrand's
            #3 prime end with the 5' end of a neighboring strand. 
            #This is SLOW for recursively joining strands.
            while(True):
                #If the 'recursivly join DnaStrand option is not checked
                #return immediately after the first interation (which joins
                #the two neighboring strands)
                if count == 1 and \
                   not env.prefs[joinStrandsCommand_recursive_clickToJoinDnaStrands_prefs_key]:
                    return
                                
                endAtom = current_strand.get_three_prime_end_base_atom()
                if endAtom is None:
                    return 
                
                #Now find the nearest five prime end atom on a strand of the 
                #*same* Dna segment. 
                axis_atom = endAtom.axis_neighbor()
                if axis_atom is None:
                    return 
                
                segment = current_strand.get_DnaSegment_with_content_atom(endAtom)
                
                if segment is None:
                    return 
                
                #find all five prime end base atoms contained by this DnaSegment.             
                raw_five_prime_ends = segment.get_all_content_five_prime_ends()
                
                def func(atm):
                    """
                    Returns true if the given atom's strand is not same as 
                    the 'strand' which is 'endAoms' parent DnaStrand 
                    
                    """
                    if atm.getDnaStrand() is current_strand:
                        return False
                    
                    return True
                
                #Following ensures that the three prime end of <strand> won't be 
                #bonded to the five prime end of the same strand. 
                five_prime_ends = filter(lambda atm: func(atm), raw_five_prime_ends)
                           
                #Max radius within which to search for the 'neighborhood' atoms 
                #(five prime ends) 
                maxBondLength = 10.0
                neighborHood = NeighborhoodGenerator(five_prime_ends, maxBondLength)
                
                pos = endAtom.posn()
                region_atoms = neighborHood.region(pos)
                            
                #minor optimization
                if not region_atoms:
                    print_compact_stack("No five prime end atoms found within %f A "\
                                        "radius of the strand's 3 prime end"%(maxBondLength))
                    return
                elif len(region_atoms) == 1:
                    five_prime_end_atom = region_atoms[0]
                else:          
                    lst = []
                    for atm in region_atoms:
                        length = vlen(pos - atm.posn())
                        lst.append((length, atm))
                    lst.sort()
                    
                    #Five prime end atom nearest to the 'endAtom' is the contained
                    #within the first tuple of the sorted list 'tpl'
                    length, five_prime_end_atom = lst[0]
                                         
                self._bond_two_strandAtoms(endAtom, five_prime_end_atom)
                self.assy.update_parts()
                
                current_strand = endAtom.getDnaStrand()
                count += 1
                
        elif endChoice == 'FIVE_PRIME_END':
            #NOT IMPLEMENTED AS OF 2008-10-26
            endAtom = strand.get_five_prime_end_base_atom()
            if endAtom is None:
                return
                
    def _bond_two_strandAtoms(self, atm1, atm2):
        """
        Bonds the given strand atoms (sugar atoms) together. To bond these atoms, 
        it always makes sure that a 3' bondpoint on one atom is bonded to 5'
        bondpoint on the other atom.         

        @param atm1: The first sugar atom of PAM3 (i.e. the strand atom) to be 
                     bonded with atm2. 
        @param atm2: Second sugar atom
        
        @see: self.joinNeighboringStrands() which calls this
        
        TODO 2008-10-26: This method is originally from 
        B_DNA_PAM3_SingleStrand class. It is modified further to account for 
        color change after bonding the two strand atoms. It needs to 
        be refactored and moved to a dna_helper package. [-- Ninad comment]
        """
        #Moved from B_Dna_PAM3_SingleStrand_Generator to here, to fix bugs like 
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
            bond_at_singlets(bondPoint1, bondPoint2, move = False)
        else:
            print_compact_stack("Bug: unable to bond atoms %s and %s: " %
                                (atm1, atm2) )
            
            
        #The following fixes bug 2770
        #Set the color of the whole dna strandGroup to the color of the
        #strand, whose bondpoint, is dropped over to the bondboint of the 
        #other strandchunk (thus joining the two strands together into
        #a single dna strand group) - Ninad 2008-04-09
        color = atm1.molecule.color 
        if color is None:
            color = atm1.element.color
        strandGroup1 = atm1.molecule.parent_node_of_class(self.assy.DnaStrand)
        
        #Temporary fix for bug 2829 that Damian reported. 
        #Bruce is planning to fix the underlying bug in the dna updater 
        #code. Once its fixed, The following block of code under 
        #"if DEBUG_BUG_2829" can be deleted -- Ninad 2008-05-01
        
        DEBUG_BUG_2829 = True
        
        if DEBUG_BUG_2829:            
            strandGroup2 = atm2.molecule.parent_node_of_class(
                self.assy.DnaStrand)                
            if strandGroup2 is not None:
                #set the strand color of strandGroup2 to the one for 
                #strandGroup1. 
                strandGroup2.setStrandColor(color)
                strandChunkList = strandGroup2.getStrandChunks()
                for c in strandChunkList:
                    if hasattr(c, 'invalidate_ladder'):
                        c.invalidate_ladder()
        
    