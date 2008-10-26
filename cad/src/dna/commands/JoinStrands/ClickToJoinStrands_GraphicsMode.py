# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-10-21 : Created

TODO:
"""

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
    
    
