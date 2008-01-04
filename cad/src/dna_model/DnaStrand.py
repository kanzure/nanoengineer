# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaStrand.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.DnaStrandOrSegment import DnaStrandOrSegment

class DnaStrand(DnaStrandOrSegment):
    """
    Model object which represents a Dna Strand inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects, described in the superclass docstring. These include
    its DnaStrandChunks, and its DnaStrandMarkers, exactly one of which is
    its controlling marker.
    """

    pass

# end
