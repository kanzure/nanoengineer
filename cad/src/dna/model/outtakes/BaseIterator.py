# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
BaseIterator.py - stub, not yet used -- probably superseded by
class PositionInWholeChain in WholeChain.py, being written now.

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

Plan:
- write this code as proto of marker move code, also can be used by user ops between updater runs
 (bfr they change stuff or after they change and run updater -- uses old info in between (that might be useful??)):
  - find ladder and index for an atom, via .molecule -- atom method
  - scan on these indices using rail.neighbor_baseatoms -- atom or ladder method? ladder is best i think.
    ### update: from one ladder to next, need to use wholechain, can't trust atom.molecule... can use ladders inside rails if useful
    but it might be more useful to use rails directly. ###decide
  maybe global helpers are good, or even a flyweight for doing the scan (can have attrs like ringQ, base index, etc).
  hmm, that flyweight base scanner could be used in dna sequence code (edit, write to file, etc),
  for this, for marker move... seems like a good idea.
  methods:
  - make one from atom, or ladder/whichrail/whichbase
  - scan it both dirs
  - get things from it (as attrs or get methods)
  - ask it things like whether there's a nick or crossover? scan to next nick or crossover? etc

See also:
* obsolete scratch file outtakes/BasePair.py (might have some methodname ideas)

"""

class BaseIterator(object):
    def __init__(self, ladder, whichrail, whichbase):
        """
        @param ladder: the DnaLadder our current base atom is on
        @type ladder: DnaLadder

        @param whichrail: which rail in the ladder (as a "rail index"(#doc)) our current base atom is on
        @type whichrail: ### (depends on strand or axis; or might cause us to choose proper subclass)

        @param whichbase: index of our current base atom within the rail
        """
        # init args are saved as public read-only attrs
        self.ladder = ladder
        self.whichrail = whichrail
        self.whichbase = whichbase
        self.check_init_args() # in debug, we also call this other times when we change these
        self._update_after_changing_init_args()
    def check_init_args(self):
        pass # nim @@@
    def _update_after_changing_init_args():
        """
        our methods must call this after any change to the public init arg attrs

        @see: check_init_args
        """
        self._rail = self.ladder.get_rail_by_index(self.whichrail) # IMPLEM get_rail_by_index (and #doc the rail index convention)
        assert self._rail
        ## assert isinstance(self._rail, self._rail_class) # IMPLEM self._rail_class (strandQ affects it)
        pass # nim @@@
    def move_to_next_base(self, delta = 1): # rename to move?

        assert 0 ### LOGIC BUG [noticed much later, 080307]:
                # our index direction of motion can differ on each rail.
                # this code treats it as always 1.
                # This code probably superseded by class PositionInWholeChain
                # in WholeChain.py being written now.

        self.whichbase += delta
            # do we need all, some, or none of self._update_after_changing_init_args()
            # if we only change whichbase? guess for now: none, except the following loop conds.
        error = False
        while not error and self.whichbase >= len(self._rail.baseatoms):
            error = self._move_to_next_rail() # also decrs self.whichbase
            assert self.whichbase >= 0
                # other loop won't be needed
        while not error and self.whichbase < 0:
            error = self._move_to_prior_rail()
            assert self.whichbase < len(self._rail.baseatoms)
                # other loop won't be needed
        # note: submethods should have reported the error (maybe saved in self.error??) @@@
        # note: submethods should have done needed updates @@@
        # Q: if we move off the end of a chain, do we remember whichbase so we can move back??
        # Q: is it not an error to move off the end, if we plan to call methods to make more DNA "up to here"??
        #    maybe add an optional arg to permit that, otherwise error...
        return
    def _move_to_prior_rail(self):
        ###
    def _move_to_next_rail(self):
        """
        Assume... ###
        # also decrs self.whichbase
        # should report an error and return True then (maybe saved in self.error)
        # do needed updates
        """
        next_atom = self._rail.neighbor_baseatoms[LADDER_END1] # might be an atom, None, or -1
        assert next_atom != -1 # if this fails, prior dna updater run didn't do enough of its job
        # todo: handle exceptions in the following
##        next_chunk = next_atom.molecule ### BUG: invalid during updater, chunks get broken. ##### BIG LOGIC BUG, uhoh @@@@@@
##            # can we use rail_end_atom_to_ladder? i guess so, it got set by last updater run... ladder is still valid... ###DOIT
##        assert next_chunk
##        next_ladder = next_chunk.ladder
##        next_ladder = rail_end_atom_to_ladder(next_atom) # IMPORT - nevermind, see below
##        assert next_ladder #k redundant?
        # now scan through whichrail and whichend until we find next_atom... what about len==1 case??
        # ah, in that case use new rail's neighbor_baseatoms to find our own... or can we use wholechain for all this? ###DECIDE
        # YES, that is what the wholechain is for. ###DOIT
        # we might even use its index cache to skip many rails at once, if we ever need to optim large delta (unlikely).


        # WRONG:
        next_rail = None # will be set if we find it
        for candidate in next_ladder.all_rails():
            if candidate.baseatoms[0].molecule is next_chunk: ### BUG: invalid during updater, chunks get broken.





        self._update_after_changing_init_args()
    pass


class StrandBaseIterator(BaseIterator):
    strandQ = True
    ## _rail_class =
    pass

class AxisBaseIterator(BaseIterator):
    strandQ = False
    ## _rail_class =
    pass

# end
