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

    [Note: we might decide to put the DnaStrandChunks inside the
     DnaSegment whose axis they attach to (as is done in DnaDuplex_EditCommand
     as of 080111), instead. This is purely an implementation issue but
     has implications for selection and copying code. bruce comment 080111]
    """

    pass

# end
