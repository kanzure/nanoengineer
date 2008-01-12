# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSegment.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.DnaStrandOrSegment import DnaStrandOrSegment

class DnaSegment(DnaStrandOrSegment):
    """
    Model object which represents a Dna Segment inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects, described in the superclass docstring.

    Among its (self's) Group.members are its DnaAxisChunks and its
    DnaSegmentMarkers, including exactly one controlling marker.
    These occur in undefined order (??). Note that its DnaStrand
    atoms are not inside it; they are easily found from the DnaAxisChunks.

    [Note: we might decide to put the DnaStrandChunks inside the
     DnaSegment whose axis they attach to, instead; for more info,
     see docstring of class DnaStrand. bruce comment 080111]

    Note that this object will never show up directly in the Model Tree
    once the DNA Data Model is fully implemented, since it will always
    occur inside a DnaGroup (and since it's not a Block).
    """
    
    #Following methods are NOT IMPLEMENTED YET =================================
    
    def getAxisEndPoints(self):
        """
        Derives and returns the two axis end points based on the atom positions
        of the segment. 
        
        @return: a list containing the two endPoints of the Axis.
        @rtype: list 
        """
        #method NIY
        assert 0
        

# end
