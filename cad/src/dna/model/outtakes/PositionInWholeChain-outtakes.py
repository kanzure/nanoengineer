from numpy import sign

class PositionInWholeChain(object):
    """
    """
    def __init__(self, wholechain, rail, index, direction):
        self.wholechain = wholechain
        self.rail = rail
        self.index = index # base index in current rail
        self.direction = direction # in current rail only
            # note: our direction in each rail can differ.
        self.off_end = False # might not be true, but if so we'll find out
        # review: should we now move_by 0 to normalize index if out of range?
        return
    
    def move_by(self, relindex):
        # don't i recall code similar to this somewhere? yes, BaseIterator.py - stub, not yet used
        self.index += self.direction * relindex
        self.off_end = False # be optimistic, we might be back on if we were off
        assert 0 # LOGIC BUG: if rail dirs alternate as we move, then the following conds alternate too --
                # we're not always in the same loop below!! (better find out if i need to write it this way
                # or only as the scanner which yields the atoms -- might be easier that way) ### DECIDE
        while self.index < 0 and not self.off_end:
            self._move_to_prior_rail(sign(relindex))
        while self.index >= len(self.rail) and not self.off_end:
            self._move_to_next_rail(sign(relindex))
        return

    def _move_to_prior_rail(self, motion_direction):
        assert self.index < 0 and not self.off_end
        self._move_to_neighbor_rail(END0, motion_direction)# IMPORT, which variant of END0? 

    def _move_to_next_rail(self, motion_direction):
        assert self.index >= len(self.rail) and not self.off_end
        self._move_to_neighbor_rail(END1, motion_direction)
        
    def _move_to_neighbor_rail(self, end, motion_direction):
        neighbor_rail, index, direction = self.find_neighbor_rail(end) # IMPLEM
        # index is on end we get onto first, direction is pointing into that rail,
        # but does this correspond to our dir of motion or its inverse? depends on sign of relindex that got us here!
        if not neighbor_rail:
            self.off_end = True # self.index is negative but remains valid for self.rail
            return
        self.rail = neighbor_rail # now set index, direction to match
        
    def yield_atom_posns(self, counter = 0, countby = 1, pos = None):
        # maybe 1: might be a method on WholeChain which is passed rail, index, direction, then dispense with this object,
        # OR, maybe 2: might yield a stream of objects of this type, instead
        grab the vars
        if pos is None: # if pos passed, self is useless -- so use WholeChain method which is always passed pos; in here, no pos arg
            pos = self.pos
        
        while 1: # or, while not hitting end condition, like hitting start posn again
            if direction > 0:
                while index < len(rail):
                    yield rail, index, direction # and counter?
                    index += 1
                now jump into next rail, no data needed except jump off END1 of this rail
            else:
                while index >= 0:
                    yield rail, index, direction # and counter?
                    index -= 1
                now jump off END0 of this rail, and continue




this might be correct:

class PositionInWholeChain(object):
    """
    """
    def __init__(self, wholechain, rail, index, direction):
        self.wholechain = wholechain
        self.rail = rail
        self.index = index # base index in current rail
        self.direction = direction # in current rail only
            # note: our direction in each rail can differ.
        
        self.pos = (rail, index, direction) ##k or use property for one or the other?
        return
        
    def yield_rail_index_direction_counter(self, **options):
        return self.wholechain.yield_rail_index_direction_counter( self.pos, **options )
    
    def _that_method_in_WholeChain(self, pos, counter = 0, countby = 1):
        """
        @note: the first position we yield is always pos, with the initial value of counter.
        """
        rail, index, direction = pos
        # assert one of our rails, valid index in it
        assert direction in (-1, 1)
        while 1:
            # yield, move, adjust, check, continue
            yield rail, index, direction, counter
            # move
            counter += countby
            index += direction
            # adjust
            def jump_off(end):
                neighbor_atom = rail.neighbor_baseatoms[end]
                # neighbor_atom might be None, atom, or -1 if not yet set
                assert neighbor_atom != -1
                if neighbor_atom is None:
                    rail = None # outer code will return due to this
                    index, direction = None, None # illegal values (to detect bugs in outer code)
                else:
                    rail, index, direction = self._find_end_atom_chain_and_index(neighbor_atom)
                    assert rail
                return rail, index, direction
            if index < 0:
                # jump off END0 of this rail
                rail, index, direction = jump_off(LADDER_END0)
            elif index >= len(rail):
                # jump off END1 of this rail
                rail, index, direction = jump_off(LADDER_END1)
            else:
                pass
            # check
            if not rail:
                return
            assert 0 <= index < len(rail)
            assert direction in (-1, 1)
            } # TODO: or if reached starting pos or passed ending pos, return
            continue
        assert 0 # not reached
        pass
