# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_chunks.py - enforce rules on chunks containing changed PAM atoms

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from foundation.state_utils import transclose

from dna.updater.dna_updater_globals import ignore_new_changes

from utilities import debug_flags

from dna.updater.dna_updater_debug import assert_unique_chain_baseatoms
from dna.updater.dna_updater_debug import assert_unique_ladder_baseatoms
from dna.updater.dna_updater_debug import assert_unique_wholechain_baseatoms

from dna.model.WholeChain import Axis_WholeChain, Strand_WholeChain

from dna.updater.dna_updater_find_chains import find_axis_and_strand_chains_or_rings

from dna.updater.dna_updater_ladders import dissolve_or_fragment_invalid_ladders
from dna.updater.dna_updater_ladders import make_new_ladders, merge_and_split_ladders

from dna.updater.dna_updater_prefs import pref_dna_updater_convert_to_PAM3plus5

from utilities.constants import MODEL_PAM3, MODEL_PAM5

# ==

def update_PAM_chunks( changed_atoms, homeless_markers):
    """
    Update chunks containing changed PAM atoms, ensuring that
    PAM atoms remain divided into AxisChunks and StrandChunks
    in the right way. Also update DnaMarkers as needed.

    @param changed_atoms: an atom.key -> atom dict of all changed atoms
                          that this update function needs to consider,
                          which includes no killed atoms. WE ASSUME
                          OWNERSHIP OF THIS DICT and modify it in
                          arbitrary ways.
                          Note: in present calling code [071127]
                          this dict might include atoms from closed files.

    @param homeless_markers: ###doc, ###rename
    
    @return: the 2-tuple (all_new_chunks, new_wholechains),
             containing a list of all newly made DnaLadderRailChunks
             (or modified ones, if that's ever possible),
             and a list of all newly made WholeChains
             (each of which covers either all new small chains,
              or some new and some old small chains, with each small chain
              also called one "DnaLadder rail" and having its own
              DnaLadderRailChunk).
    """

    # see scratch file for comments to revise and bring back here...

    ignore_new_changes("as update_PAM_chunks starts", changes_ok = False )

    # Move each DnaMarker in which either atom got killed or changed in
    # structure (e.g. rebonded) onto atoms on the same old wholechain
    # (if it has one) which remain alive. We don't yet know if they'll
    # be in the same new wholechain and adjacent in it -- that will be
    # checked when new wholechains are made, and we retain the moved
    # markers so we can assert that they all get covered that way
    # (which they ought to -- todo, doc why).
    #
    # Note that we might find markers which are not on old wholechains
    # (e.g. after mmp read), and we might even find markers like that
    # on killed atoms (e.g. after mmp insert, which kills clipboard).
    # Those markers can't be moved, but if valid without being moved,
    # can be found and used by a new wholechain. [revised 080311]
    #
    # The old wholechain objects still
    # exist within the markers, and can be used to scan their atoms even though
    # some are dead or their bonding has changed. The markers use them to help
    # decide where and how to move. Warning: this will only be true during the early
    # parts of the da updater run, since the wholechains rely on rail.neighbor_baseatoms
    # to know how their rails are linked, and that will be rewritten later around
    # when new wholechains are made. TODO: assert that we don't rely on that after
    # it's invalid.
    #
    # [code and comment rewritten 080311]

    ## homeless_markers = _f_get_homeless_dna_markers() #e rename # now an arg, 080317
        # this includes markers whose atoms got killed (which calls marker.remove_atom)
        # or got changed in structure (which calls marker.changed_structure)
        # so it should not be necessary to also add to this all markers noticed
        # on changed_atoms, even though that might include more markers than
        # we have so far (especially after we add atoms from invalid ladders below).
    
    live_markers = []
    for marker in homeless_markers:
        still_alive = marker._f_move_to_live_atompair_step1() #e @@@@ rename (no step1) (also fix @@@)
            # note: we don't yet know if they'll still be alive
            # when this updater run is done.
        if still_alive:
            live_markers.append(marker) # only used for asserts
        if (not not still_alive) != (not marker.killed()):
            print "\n***BUG: still_alive is %r but %r.killed() is %r" % \
                  (still_alive, marker, marker.killed())
        if debug_flags.DEBUG_DNA_UPDATER: # SOON: _VERBOSE
            if still_alive:
                print "dna updater: moved marker %r, still alive after step1" % (marker,)
            else:
                print "dna updater: killed marker %r (couldn't move it)" % (marker,)
    del homeless_markers

    ignore_new_changes("from moving DnaMarkers")
        # ignore changes caused by adding/removing marker jigs
        # to their atoms, when the jigs die/move/areborn
    
    # make sure invalid DnaLadders are recognized as such in the next step,
    # and dissolved [possible optim: also recorded for later destroy??].
    # also (#e future optim) break long ones at damage points so the undamaged
    # parts needn't be rescanned in the next step.
    #
    # Also make sure that atoms that are no longer in valid ladders
    # (due to dissolved or fragmented ladders) are scanned below,
    # or that the chains they are in are covered. This is necessary so that
    # the found chains below cover all atoms in every "base pair" (Ss-Ax-Ss)
    # they cover any atom in. Presently this is done by 
    # adding some or all of their atoms into changed_atoms
    # in the following method.
    
    dissolve_or_fragment_invalid_ladders( changed_atoms)
        # note: this adds atoms (live atoms only) to changed_atoms;
        # see its comments and above comment for details.
    
    # Find the current axis and strand chains (perceived from current bonding)
    # on which any changed atoms reside, but only scanning along atoms
    # not still part of valid DnaLadders. (I.e. leave existing undamaged
    # DnaLadders alone.) (The found chains or rings will be used below to
    # make new DnaChain and DnaLadder objects, and (perhaps combined with
    # preexisting untouched chains ###CHECK) to make new WholeChains and tell the
    # small chains about them.)

    ignore_new_changes("from dissolve_or_fragment_invalid_ladders", changes_ok = False)
    
    axis_chains, strand_chains = find_axis_and_strand_chains_or_rings( changed_atoms)

    ignore_new_changes("from find_axis_and_strand_chains_or_rings", changes_ok = False )

    if debug_flags.DNA_UPDATER_SLOW_ASSERTS:
        assert_unique_chain_baseatoms(axis_chains + strand_chains)
    
    # make ladders
    
    # Now use the above-computed info to make new DnaLadders out of the chains
    # we just made (which contain all PAM atoms no longer in valid old ladders),
    # and to merge end-to-end-connected ladders (new/new or new/old) into larger
    # ones, when that doesn't make them too long. We'll reverse chains
    # as needed to make the ones in one ladder correspond in direction, and to
    # standardize their strand bond directions. (There is no longer any need to
    # keep track of index_direction -- it might be useful for new/new ladder
    # merging, but that probably doesn't help us since we also need to handle
    # new/old merging. For now, the lower-level code maintains it for individual
    # chains, and when fragmenting chains above, but discards it for merged
    # chains.)

    # Note: we don't need to rotate smallchains that are rings, to align them
    # properly in ladders, since make_new_ladders will break them up as
    # needed into smaller pieces which are aligned.

    new_axis_ladders, new_singlestrand_ladders = make_new_ladders( axis_chains, strand_chains)

    ignore_new_changes("from make_new_ladders", changes_ok = False)

    if debug_flags.DNA_UPDATER_SLOW_ASSERTS:
        assert_unique_ladder_baseatoms( new_axis_ladders + new_singlestrand_ladders)

    # convert pam model of ladders that want to be converted
    # (assume all old ladders that want this were invalidated
    #  and therefore got remade above; do this before merging
    #  in case conversion errors are confined to smaller ladders
    #  that way, maybe for other reasons) [bruce 080401 new feature]

    default_pam = pref_dna_updater_convert_to_PAM3plus5() and MODEL_PAM3 or None
        # None means "whatever you already are", i.e. do no conversion.
        # There is not yet a way to say "display everything in PAM5".
        # We will probably need either that, or "convert selection to PAM5",
        # or both. As of 080401 we only have "convert one ladder to PAM5" (unfinished).
    
    number_converted = 0
    number_failed = 0
    for ladder in new_axis_ladders + new_singlestrand_ladders:
        wanted, succeeded = ladder._f_convert_pam_if_desired(default_pam)
        didit = wanted and succeeded 
        failed = wanted and not succeeded
        number_converted += not not didit
        number_failed += not not failed
        continue

    # Note: if ladders were converted, their chains are still ok,
    # since those only store baseatoms (for strand and axis),
    # and those transmuted and moved but didn't change identity.
    # So the ladders also don't change identity, and remain valid
    # unless they had conversion errors. If not valid, they are ok
    # in those lists since this was already possible in other ways
    # (I think). (All this needs test and review.)
    #
    # But lots of atoms got changed in lots of ways (transmute, move,
    # rebond, create Pl, kill Pl). Ignore all that.
    # (review: any changes to ignore if conversion wanted and failed?)

    msg = "from converting %d ladders" % number_converted
    if number_failed:
        msg += " (%d desired conversions failed)" % number_failed
        # msg is just for debug, nevermind calling fix_plurals
    
    if number_converted:
        ignore_new_changes(msg, changes_ok = True)
    else:
        ignore_new_changes(msg, changes_ok = False)

    # merge axis ladders (ladders with an axis, and 1 or 2 strands)
    
    merged_axis_ladders = merge_and_split_ladders( new_axis_ladders,
                                                   debug_msg = "axis" )
        # note: each returned ladder is either entirely new (perhaps merged),
        # or the result of merging new and old ladders.

    ignore_new_changes("from merging/splitting axis ladders", changes_ok = False)

    del new_axis_ladders

    # merge singlestrand ladders (with no axis)
    # (note: not possible for an axis and singlestrand ladder to merge)
    
    merged_singlestrand_ladders = merge_and_split_ladders( new_singlestrand_ladders,
                                                           debug_msg = "single strand" )
        # not sure if singlestrand merge is needed; split is useful though

    ignore_new_changes("from merging/splitting singlestrand ladders", changes_ok = False)

    del new_singlestrand_ladders

    merged_ladders = merged_axis_ladders + merged_singlestrand_ladders
    
    if debug_flags.DNA_UPDATER_SLOW_ASSERTS:
        assert_unique_ladder_baseatoms( merged_ladders)

    # Now make or remake chunks as needed, so that each ladder-rail is a chunk.
    # This must be done to all newly made or merged ladders (even if parts are old).

    all_new_chunks = []
    
    for ladder in merged_ladders:
        new_chunks = ladder.remake_chunks()
        all_new_chunks.extend( new_chunks)

    ignore_new_changes("from remake_chunks", changes_ok = True)
        # (changes are from parent chunk of atoms changing)

    # Now make new wholechains on all merged_ladders,
    # let them own their atoms and markers (validating any markers found,
    # moved or not, since they may no longer be on adjacent atoms on same wholechain),
    # and choose their controlling markers.
    # These may have existing DnaSegmentOrStrand objects,
    # or need new ones (made later), and in a later step (not in this function)
    # those objects take over their chunks.
    
    # Note that due to the prior step, any atom in a ladder (new or old)
    # can find its smallchain via its chunk.

    # We'll do axis chains first, in case we want them finalized
    # in figuring out anything about strand markers (not the case for now).
    # For any length-1 axis chains, we'll pick a direction arbitrarily (?),
    # so we can store, for all chains, a pointer to the ladder-index of the
    # chain it connects to (if any).

    # For each kind of chain, the algorithm is handled by this function:
    def algorithm( ladders, ladder_to_rails_function ):
        """
        [local helper function]
        Given a list of ladders (DnaLadders and/or DnaSingleStrandDomains),
        and ladder_to_rails_function to return a list of certain rails
        of interest to the caller from each ladder, partition the resulting
        rails into connected sets (represented as dicts from id(rail) to rail)
        and return a list of these sets.

        "Connected" means the rails are bonded end-to-end so that they belong
        in the same WholeChain. To find some rail's connected rails, we just use
        atom.molecule.ladder and then look for atom in the rail ends of the same
        type of rail (i.e. the ones found by ladder_to_rails_function).
        """
        # note: this is the 3rd or 4th "partitioner" I've written recently;
        # could there be a helper function for partitioning, like there is
        # for transitive closure (transclose)? [bruce 080119]
        toscan_all = {} # maps id(rail) -> rail, for initial set of rails to scan
        for ladder in ladders:
            for rail in ladder_to_rails_function(ladder):
                toscan_all[id(rail)] = rail
        def collector(rail, dict1):
            """
            function for transclose on a single initial rail:
            remove each rail seen from toscan_all if present;
            store neighbor atom pointers in rail,
            and store neighbor rails themselves into dict1
            """
            toscan_all.pop(id(rail), None)
                # note: forgetting id() made this buggy in a hard-to-notice way;
                # it worked without error, but returned each set multiple times.
            rail._f_update_neighbor_baseatoms() # called exactly once per rail,
                # per dna updater run which encounters it (whether as a new
                # or preexisting rail); implem differs for axis or strand atoms
            for neighbor_baseatom in rail.neighbor_baseatoms:
                if neighbor_baseatom is not None:
                    rail1 = _find_rail_of_atom( neighbor_baseatom, ladder_to_rails_function )
                    dict1[id(rail1)] = rail1
            return # from collector
        res = [] # elements are data args for WholeChain constructors (or helpers)
        for rail in toscan_all.values(): # not itervalues (modified during loop)
            if id(rail) in toscan_all: # if still there (hasn't been popped)
                toscan = {id(rail) : rail}
                rails_for_wholechain = transclose(toscan, collector)
                res.append(rails_for_wholechain)
        return res

    # make new wholechains. This also calls marker methods on all markers they find
    # which can kill some of the markers.
    
    new_wholechains = (
        map( Axis_WholeChain, 
             algorithm( merged_axis_ladders,
                        lambda ladder: ladder.axis_rails() ) ) +
        map( Strand_WholeChain,
             algorithm( merged_ladders, # must do both kinds at once!
                        lambda ladder: ladder.strand_rails ) )
     )
    if debug_flags.DEBUG_DNA_UPDATER:
        print "dna updater: made %d new or changed wholechains..." % len(new_wholechains)

    if debug_flags.DNA_UPDATER_SLOW_ASSERTS:
        assert_unique_wholechain_baseatoms(new_wholechains)

    # The new WholeChains should have found and fully updated (or killed)
    # all markers we had to worry about. Assert this -- but only with a
    # debug print, since I might be wrong (e.g. for markers on oldchains
    # of length 1, now on longer ones??) and it ought to be harmless to
    # ignore any markers we missed so far.
    for marker in live_markers:
        marker._f_should_be_done_with_move()
    del live_markers
    
    # note: those Whatever_WholeChain constructors above also have side effects:
    # - own their atoms and chunks (chunk.set_wholechain)
    # - kill markers no longer on adjacent atoms on same wholechain
    #
    # (REVIEW: maybe use helper funcs so constructors are free of side effects?)
    #
    # but for more side effects we run another loop:
    for wholechain in new_wholechains:
        wholechain.own_markers()
        # - own markers
        # - and (in own_markers)
        #   - choose or make controlling marker,
        #   - and tell markers whether they're controlling (might kill some of them)
    if debug_flags.DEBUG_DNA_UPDATER:
        print "dna updater: owned markers of those %d new or changed wholechains" % len(new_wholechains)

    ignore_new_changes("from making wholechains and owning/validating/choosing/making markers",
                       changes_ok = True)
        # ignore changes caused by adding/removing marker jigs
        # to their atoms, when the jigs die/move/areborn
        # (in this case, they don't move, but they can die or be born)

    # TODO: use wholechains and markers to revise base indices if needed
    # (if this info is cached outside of wholechains)

    return all_new_chunks, new_wholechains # from update_PAM_chunks

# ==

def _find_rail_of_atom( atom, ladder_to_rails_function):
    """
    [private helper]
    (can assume atom is an end_baseatom of its rail)
    """
    try:
        rails = ladder_to_rails_function( atom.molecule.ladder)
        for rail in rails:
            for end_atom in rail.end_baseatoms():
                if end_atom is atom:
                    return rail
        assert 0, "can't find any rail in ladder %r (rails %r) which has %r as an end_atom" % \
               ( atom.molecule.ladder, rails, atom )
    except:
        print "\n*** BUG: following exception is about _find_rail_of_atom( %r, .mol = %r, ._dna_updater__error = %r, %r): " % \
              (atom, atom.molecule, atom._dna_updater__error, ladder_to_rails_function )
        raise
    pass

# end

