# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSegment.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.DnaStrandOrSegment import DnaStrandOrSegment

class DnaSegment(DnaStrandOrSegment):
    #e maybe inherit some more special subclass, to make kids not visible in MT;
    # or, DnaStrandOrSegment, since they have lots in common (docstrings 
    # are almost identical).
    """
    Model object which represents a Dna Segment inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects, described in the superclass docstring.

    Among its (self's) Group.members are its DnaAxisChunks and its
    DnaSegmentMarkers, including exactly one controlling marker.
    These occur in undefined order (??). Note that its DnaStrand
    atoms are not inside it; they are easily found from the DnaAxisChunks.
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
