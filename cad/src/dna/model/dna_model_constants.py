# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
dna_model_constants.py -- constants for dna_model internals
(not the same as Dna_Constants.py, which is about DNA itself)

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

# Codes for ladder ends (used privately or passed to other-ladder friend methods)
# or chain ends.
#
# WARNING: they don't correspond in these uses! That is, strand2 of a ladder
# has chain-ends in the order 1,0, but has ladder-ends in the order 0,1.
# So I'll introduce different names for these uses. But there might be
# helper methods which accept either kind -- not sure. For now,
# assume that it's required for the two sets to have identical values.
# [bruce 080116]

LADDER_ENDS = (0, 1)

LADDER_END0 = LADDER_ENDS[0] # "left" for ladder

LADDER_END1 = LADDER_ENDS[1] # "right" for ladder

LADDER_OTHER_END = [1, 0] # 1 - end

LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1 = [-1, 1] # not correct for strand2 of a ladder

LADDER_STRAND1_BOND_DIRECTION = LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1[LADDER_END1]

CHAIN_ENDS = LADDER_ENDS

CHAIN_END0 = CHAIN_ENDS[0] # "5' end" for strand

CHAIN_END1 = CHAIN_ENDS[1] # "3' end" for strand

CHAIN_OTHER_END = [1, 0] # 1 - end

CHAIN_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND = [-1, 1]


MAX_LADDER_LENGTH = 500     # @@@@ TODO: also use this to split long ladders
    # MAX_LADDER_LENGTH limits the length of a DnaLadder that we will create
    # by merging (this is implemented, and ran at 20 for a long time),
    # and (not yet implemented) causes us to split DnaLadders that are longer
    # than this (when encountered by the dna updater).
    #
    # When it's fully implemented, the best value should be determined based
    # on performance (eg of graphics), and might be 20 or lower (splitting
    # would be fairly common for 20).
    #
    # Right now, since it's only partly implemented, and since
    # some display or UI ops may not yet handle split ladders ideally,
    # make it a large enough value that failure to split
    # (resulting in history-dependence of final state) will be rare.
    #
    # [bruce 080314]


# end
