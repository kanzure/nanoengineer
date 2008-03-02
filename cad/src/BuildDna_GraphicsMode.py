# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
"""

from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from dna_model.DnaSegment import DnaSegment
from dna_model.DnaStrand import DnaStrand

_superclass = SelectChunks_GraphicsMode
class BuildDna_GraphicsMode(SelectChunks_GraphicsMode):
    """
    """    
    
    def chunkLeftUp(self, aChunk, event):
        """
        """
        _superclass.chunkLeftUp(self, aChunk, event)
        
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








