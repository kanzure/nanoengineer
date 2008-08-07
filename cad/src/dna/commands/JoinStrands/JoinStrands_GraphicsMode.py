# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
"""
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode

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

from PyQt4.Qt import QFont, QString
from utilities.constants import green

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
        
        
    def Draw(self):
        _superclass_for_GM.Draw(self)
        self._draw_dnaBaseNumberLabels()
        
    def _draw_dnaBaseNumberLabels(self):
        """
        Draw the DNA basee number labels.
        
        
        baseNumLabelChoice:(obtained from command class)
        0 =  None
        1 = Strands and Segments
        2 =  Strands Only
        3 =  Segments Only
        
        @see: self._correct_baseatom_order_for_dnaStrand()
        """
        baseNumLabelChoice = self.command.getBaseNumberLabelChoice()
        
        if self.glpane.scale > 65.0:
            fontSize = 9
        else:
            fontSize = 12
        
        if baseNumLabelChoice == 0:
            return 
        
           
        segments = self.win.assy.part.get_topmost_subnodes_of_class(self.win.assy.DnaSegment)
        strands = self.win.assy.part.get_topmost_subnodes_of_class(self.win.assy.DnaStrand)
        
        font = QFont( QString("Helvetica"), fontSize)
        textColor = self.command.getColor_baseNumberLabel()
        # WARNING: Anything smaller than 9 pt on Mac OS X results in 
        # un-rendered text.
        out = self.glpane.out * 3 # bug: 5 is too large                
        
        def func(strandOrSegmentList):        
            for strandOrSegment in strandOrSegmentList:
                whole_chain = strandOrSegment.get_wholechain()
                if whole_chain is None:
                    continue
                baseatoms = whole_chain.get_all_baseatoms_in_order()
                
                if isinstance(strandOrSegment, self.win.assy.DnaStrand):
                    baseatoms = self._correct_baseatom_order_for_dnaStrand(
                        strandOrSegment,
                        baseatoms)
                    
                i = 1
                for atm in baseatoms:
                    text = "%d" %(i)
                    pos = atm.posn() + out ##+ (self.glpane.right + self.glpane.up)
                    
                    self.glpane.renderTextAtPosition(pos, 
                                                     text, 
                                                     textColor = textColor, 
                                                     textFont = font)
                   
                    i += 1
                    
        if baseNumLabelChoice in (1, 2):
            func(strands)
        if baseNumLabelChoice in (1, 3):
            func(segments)
            
    def _correct_baseatom_order_for_dnaStrand(self, strand, baseatoms):
        """
        See a TODO comment in this method body.
        @see: self._draw_dnaBaseNumberLabels()
        
        """
        #@TODO: REVISE this. Its only called from self._draw_dnaBaseNumberLabels()
        #See if this method should be a moved to DnaStrand class and 
        #some portion of the self._draw_dnaBaseNumberLabels() that returns 
        #baseatoms to class DnaStrandOrSegment. Issue with this refactoring: 
        #there is a method in DnaStrand class that returns baseatoms in bond
        #direction. May be it needs to be revised/ replaced with 
        #wholechain.get_all_base_atoms_in_order()
        #-- Ninad 2008-08-06
        numberingOrder = self.command.getBaseNumberingOrder()
        five_prime_end = strand.get_five_prime_end_base_atom()
        if five_prime_end: 
            if numberingOrder == 0:
                if not five_prime_end is baseatoms[0]:
                    baseatoms.reverse()
            elif numberingOrder == 1:
                if five_prime_end is baseatoms[0]:
                    baseatoms.reverse()
        return baseatoms
                
    
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
    