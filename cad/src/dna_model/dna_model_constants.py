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

LADDER_OTHER_END = [1,0] # 1 - end

LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1 = [-1, 1] # not correct for strand2 of a ladder


CHAIN_ENDS = LADDER_ENDS

CHAIN_END0 = CHAIN_ENDS[0] # "5' end" for strand

CHAIN_END1 = CHAIN_ENDS[1] # "3' end" for strand

CHAIN_OTHER_END = [1,0] # 1 - end

CHAIN_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND = [-1, 1]


# end
