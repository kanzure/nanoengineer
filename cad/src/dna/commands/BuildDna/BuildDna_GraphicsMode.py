# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
"""

from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from dna.model.DnaSegment import DnaSegment
from dna.model.DnaStrand import DnaStrand

DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND = False

_superclass = SelectChunks_GraphicsMode
class BuildDna_GraphicsMode(SelectChunks_GraphicsMode):
    """
    """    
    
    def chunkLeftUp(self, aChunk, event):
        """
        Upon chunkLeftUp, it enters the strand or segment edit command
        This is an alternative implementation. As of 2008-03-03, 
        we have decided to change this implementation. Keeping the 
        related methods alive if, in future, we want to switch to this 
        implementation and/or add a user preference to do this. 
        """
        _superclass.chunkLeftUp(self, aChunk, event)
        
        if DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND:
            if aChunk.picked:
                if aChunk.isAxisChunk():   
                    segmentGroup = aChunk.parent_node_of_class(DnaSegment)
                    if segmentGroup is not None:                    
                        segmentGroup.edit()
                elif aChunk.isStrandChunk():
                    strandGroup = aChunk.parent_node_of_class(DnaStrand)
                    if strandGroup is not None:
                        strandGroup.edit()
                    else:
                        aChunk.edit()
                
    def _is_dnaGroup_highlighting_enabled(self):
        """
        Overrides SelectChunks_GraphicsMode._is_dnaGroup_highlighting_enabled()
        
        Returns a boolean that decides whether to highlight the whole 
        DnaGroup or just the chunk of the glpane.selobj. 
        Example: In default mode (SelectChunks_graphicsMode) if the cursor is
        over an atom or a bond which belongs to a DnaGroup, the whole 
        DnaGroup is highlighted. But if you are in buildDna mode, the 
        individual strand and axis chunks will be highlighted in this case. 
        Therefore, subclasses of SelectChunks_graphicsMode should override this
        method to enable or disable the DnaGroup highlighting. (the Default 
        implementation returns True)
        @see: self._get_objects_to_highlight()
        @see: self.drawHighlightedChunk()
        @see : self.drawHighlightedObjectUnderMouse()
	"""
        return False








