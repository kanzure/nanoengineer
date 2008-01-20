# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_debug.py -- debug code for dna_updater

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

def assert_unique_chain_baseatoms(chains, when = ""):
    if when:
        when = " (%s)" % when
    baseatom_info = {} # maps atom.key to chain
    for chain in chains:
        for atom in chain.baseatoms:
            assert atom.key not in baseatom_info, \
                   "baseatom %r in two chains%s: %r and %r" % \
                   (atom, when, baseatom_info[atom.key], chain)
            baseatom_info[atom.key] = chain
    return

def assert_unique_ladder_baseatoms(ladders, when = ""):
    if when:
        when = " (%s)" % when
    baseatom_info = {} # maps atom.key to (ladder, whichrail, rail, pos)
    for ladder in ladders:
        rails = ladder.all_rail_slots_from_top_to_bottom() # list of rail or None
        lastlength = None
        for whichrail in [0,1,2]:
            rail = rails[whichrail]
            if not rail:
                continue
            length = len(rail)
            if lastlength is not None:
                assert lastlength == length, "rail length mismatch in %r" % ladder
            lastlength = length
            baseatoms = rail.baseatoms
            for pos in range(length):
                atom = baseatoms[pos]
                loc_info = (ladder, whichrail, rail, pos)
                assert atom.key not in baseatom_info, \
                   "baseatom %r in two ladders%s; loc info: %r and %r" % \
                   (atom, when, baseatom_info[atom.key], loc_info)
                baseatom_info[atom.key] = loc_info
    return

def assert_unique_wholechain_baseatoms(wholechains, when = ""):
    if when:
        when = " (%s)" % when
    baseatom_info = {} # maps atom.key to (wholechain, chain)
    for wholechain in wholechains:
        for chain in wholechain.chains():
            for atom in chain.baseatoms:
                loc_info = (wholechain, chain)
                assert atom.key not in baseatom_info, \
                       "baseatom %r in two chains%s; loc info: %r and %r" % \
                       (atom, when, baseatom_info[atom.key], loc_info)
                baseatom_info[atom.key] = loc_info
    return

# end
