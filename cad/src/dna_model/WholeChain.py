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
    (in various ways needed by different users of it)
    and (for some of those users) replaced by one or more newly
    constructed wholechains.

    Its jobs and role in the DNA Data Model include:

    - Understand base indexing for any whole segment or strand.

    - Be able to find (and/or keep track of) all the DnaMarkers
    along its atoms.

    - Help a DnaMarker scan its atoms to decide where to move to,
    and help it actually move.

    - Decide which marker should determine strand or segment identity
    and base indexing scheme for the atoms in this wholechain
    (if it's valid). Markers might contain user-settable attributes
    (or inherit those from their owning strand or segment) to know
    how to do this, e.g. a higher or lower priority in controlling
    base indexing, policies for which direction to move in and how
    to adjust base index when moving, how to move when new bases
    are inserted (detectable if these go between the two marker
    atoms), etc. [### todo: say some of that on DnaMarker docstring]

    Specialized kinds of markers might serve as, for example,
    startpoints or endpoints of sequence constraints, or good places
    for a base index discontinuity in a ring (if the index origin
    should not be used).

    Invariants, and how it maintains them:

    - At any given time, just after any dna updater run, the valid WholeChains
    are in 1-1 correspondence with the set of DnaSegment and DnaStrand objects,
    via their controlling markers.

    - Just after any dna updater run, each WholeChain knows about the DnaMarkers
    on its atoms, of which there are one or more, with exactly one being a 
    "controlling marker", which determines the identity of the
    DnaSegment and DnaStrand object which own the wholechain's atoms,
    and determines the base indexing scheme they use (origin and direction).
    
    - When things change (i.e. when user operations make wholechains invalid),
    and the dna updater runs again (always before the next undo checkpoint
    takes its snapshot of the model state), the dna updater
    (and methods in the markers and chains) decide how to maintain this
    association (wholechain -> controlling marker -> owning strand or segment)
    based on how the controlling marker moves and whether it stays / stops being
    / becomes controlling. (The wholechain chooses
    or makes a new controlling marker as needed for this.)

    - To do this, the wholechain uses the now-invalid wholechains to help it
    figure out when and how to modify existing DnaSegment or DnaStrand objects,
    and/or delete them or make new ones. (It does this mainly by moving
    DnaMarkers whose atoms got deleted to new locations (of non-deleted atoms)
    along their old wholechains, and then having new wholechains decide which
    markers should determine their strand's or segment's identity, by being
    the wholechain's one "controlling marker".)

    State:
    
    - A WholeChain contains no state for undo/copy/save; that's in the associated
    DnaSegment and DnaStrand objects and their DnaMarkers. (The set of DnaMarkers
    belonging to a DnaSegment and DnaStrand object is the same as the set of
    all the valid markers along its wholechain's atoms.)
    """

    def __init__(self, args): # who calls this? maybe we make this for each new smallchain?
        self.xxx = args
        bla
        pass
    
    def all_markers(self):
        return self._all_markers ### GUESS and NIM

    def find_controlling_marker(self):
        return self._controlling_marker # GUESS and STUB - recompute it if not valid

    def _choose_controlling_marker(self):
        """
        [private]
        Look for existing markers on our atoms.
        Choose one of them to be our controlling marker.

        If one or more are already controlling, it will be one of them. [### REVIEW -- not sure this point is right]
        If more than one are, we have rules to let them compete.
        If none is, ditto.

        Return the marker we choose, but don't tell any markers they are or are not controlling now
        (up to caller to do this if desired).
        ### REVIEW: if no marker, return None or make one?
        """
        all_markers = self.all_markers() #k updated when?? @@@
        candidates = [marker
                      for marker in self.all_markers()
                      if marker.wants_to_be_controlling()]
        list_of_preferred_markers_this_time = [] ### stub - in real life let external code add markers to this list, pop them all here
        items = []
        for marker in candidates:
            order_info = (marker in list_of_preferred_markers_this_time, # note: False < True
                          marker.control_priority,
                          marker.get_oldness(), # assume oldness is unique -- inverse of something allocated by a counter
                          )
            items.append( (order_info, marker) )
        items.sort()
        if items:
            return items[-1][1]
        return None ###k

    
    # todo: methods related to base indexing

    # todo: methods to help move markers, derived from or related to
    # _f_move_to_live_atom_step1 and _step2 in dna_updater_chunks.py
    
    pass # end of class WholeChain
