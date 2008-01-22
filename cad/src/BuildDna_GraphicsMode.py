# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
"""

from SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from dna_model.DnaSegment import DnaSegment

class BuildDna_GraphicsMode(SelectChunks_GraphicsMode):
    """
    """    
    
    def chunkLeftUp(self, aChunk, event):
        """
        """
        SelectChunks_GraphicsMode.chunkLeftUp(self, aChunk, event)
        
        if aChunk.picked and aChunk.isAxisChunk():   
            if isinstance(aChunk.dad, DnaSegment):
                segment = aChunk.dad
                segment.edit()
        
    pass







