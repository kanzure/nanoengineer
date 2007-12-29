# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGroup.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.Block import Block

# Following import is disabled. See addSegment method for reason.
## from dna_model.DnaSegment import DnaSegment

class DnaGroup(Block):
    """
    Model object which packages together some Dna Segments, Dna Strands,
    and other objects needed to represent all their PAM atoms and markers.

    The contents are not directly visible to the user in the model tree,
    except for Blocks (fyi, this behavior comes from our Block superclass,
    which is a kind of Group).
    
    But internally, most of the contents are Nodes which can be stored
    in mmp files, copied, and undo-scanned in the usual ways.

    Specific kinds of Group member contents include:
    - DnaStrands (optionally inside Blocks)
    - DnaSegments (ditto)
    - Blocks (a kind of Group)
    - DnaAtomMarkers (a kind of Jig, probably always inside an owning
      DnaStrand or DnaSegment)
    - specialized chunks for holding PAM atoms:
      - DnaAxisChunk (undecided whether these will live inside DnaSegments
        they belong to, but probably they will)
      - DnaStrandChunk (undecided whether these will live inside their
        DnaStrands, but probably they will)

    As other attributes:
    - whatever other properties the user needs to assign, which are not
      covered by the member nodes or superclass attributes.
    """
    # example method:
    def get_segments(self):
        """
        Return a list of all our DnaSegment objects.
        """
        return self.get_subnodes_of_class("DnaSegment") # IMPLEM get_subnodes_of_class
    

    def addSegment(self, segment):
        """
        Adds a new segment object for this dnaGroup.
        
        @param segment: The DnaSegment to be added to this DnaGroup object
        @type: B{DnaSegment}  
        """
        # importing DnaSegment created an import cycle which throws error. 
        # So the isinstance check is is disabled for now.
        ## assert isinstance(segment, DnaSegment)
        
        self.addchild(segment)

# end
