# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
WholeChain.py - 

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""


class WholeChain(object):
    """
    A WholeChain knows a sequence of 1 or more smaller chains
    (of DNA PAM atoms) which are linked into a single longer chain or ring
    (or which were so linked when it was constructed).
    (If it's not a ring, then it must be a maximal chain,
    i.e. not able to be extended with more atoms at the ends,
    at the time it's constructed.)

    It is immutable once constructed, as are its smaller chains.
    Modifications to the underlying chaining from which it and its
    smaller chains are derived result in its becoming invalid
    (in variuos ways needed by different users of it)
    and (for some of those users) replaced by one or more new ones.

    Its jobs and role in the DNA Data Model include:

    - At any given time, just after any dna updater run, the valid WholeChains
    are in 1-1 correspondence with the set of DnaSegment and DnaStrand objects.

    - It contains no state for undo/copy/save; that's in the associated
    DnaSegment and DnaStrand objects and their DnaMarkers (which are the same
    as all the valid markers along the wholechain's atoms).
    
    - User operations can make wholechains invalid, and the updater will restore the
    correspondence of each DnaSegment and DnaStrand object to one valid wholechain,
    using the now-invalid wholechains to help it figure out when and how
    to modify existing such objects, and/or delete them or make new ones.
    (It does this mainly by moving DnaMarkers along their old wholechains,
    and having new wholechains decide which markers should determine
    strand or segment identity.)
    
    - Understand base indexing for any whole segment or strand.

    - Be able to find (and/or keep track of) all the DnaMarkers
    along its atoms.

    - Help a DnaMarker scan its atoms to decide where to move to,
    and help it actually move.

    - Decide which marker should determine strand or segment identity for the
    atoms in this wholechain (if it's valid).
    """

    def all_markers(self):
        return self._all_markers ### GUESS and NIM

    def find_controlling_marker(self):
        return self._controlling_marker # GUESS and STUB - recompute it if not valid

    # todo: methods related to base indexing

    # todo: methods to help move markers
    
    pass # end of class WholeChain
