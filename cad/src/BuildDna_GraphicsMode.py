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
                if isinstance(aChunk.dad, DnaSegment):
                    segment = aChunk.dad
                    segment.edit()
            elif aChunk.isStrandChunk():
                aChunk.edit()








