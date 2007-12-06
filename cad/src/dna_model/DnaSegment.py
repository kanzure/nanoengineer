# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSegment.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from Group import Group

class DnaSegment(Group):
    #e maybe inherit some more special subclass, to make kids not visible in MT;
    # or, DnaStrandOrSegment, since they have lots in common (docstrings are almost identical).
    """
    Model object which represents a Dna Segment inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects:

    - as Group members (not visible in MT, but for convenience of
    reusing preexisting copy/undo/mmp code):

      - one or more DnaAtomMarkers, one of which determines this
        segment's base indexing, and whether/how it survives if its
        chains of PAM atoms are broken or merged with other segments.

      - (maybe) this Segment's DnaAxisChunks.

    - As other attributes:

      - (probably) a chain of DnaAtomChainOrRings
        which are all the PAM atoms in the segment. From these,
        related objects like DnaLadders and connected DnaStrands
        can be found.
    
      - whatever other properties the user needs to assign, which are not
        covered by the member nodes or superclass attributes. However,
        some of these might be stored on the controlling DnaAtomMarker,
        so that if we are merged with another segment, and later separated
        again, it can again control the properties of a segment (as it
        will control its base indexing).
    """
    pass

# end
