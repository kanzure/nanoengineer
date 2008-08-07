# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-08-07: Created.

TODO:
"""
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from PyQt4.Qt import QFont, QString

_superclass = BuildAtoms_GraphicsMode
class BreakOrJoinstrands_GraphicsMode(BuildAtoms_GraphicsMode):
    """
    Common superclass for GraphicsMode classes of Break and Join Strands 
    commands. 
    @see: BreakStrand_GraphicsMode()
    @see: JoinStrands_GraphicsMode() 
    """
    def Draw(self):
        _superclass.Draw(self)
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
                    pos = atm.posn() + (0.03+ atm.highlighting_radius())*self.glpane.out ##+ (self.glpane.right + self.glpane.up)
                    
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