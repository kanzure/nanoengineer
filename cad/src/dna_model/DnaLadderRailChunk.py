# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaLadderRailChunk.py - 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from chunk import Chunk

class DnaLadderRailChunk(Chunk):
    ladder = None # will be a DnaLadder in finished instances
    ###e todo: undo, copy for that attr
    
    def invalidate_ladder(self): #bruce 071203
        """
        [overrides Chunk method]
        """
        self.ladder.invalidate()
        return
    
    ###e todo: at least self-inval on structure changes... like new atoms...

    def in_a_valid_ladder(self): #bruce 071203
        """
        Is this chunk a rail of a valid DnaLadder?
        [overrides Chunk method]
        """
        return self.ladder.valid
    

    #e draw method?
    pass

#e subclasses, Axis & Strand - prob sep files

# end
