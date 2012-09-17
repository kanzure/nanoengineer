# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
dna_updater_follow_strand.py - helper function for dna_updater_ladders.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.constants import noop

_FAKE_AXIS_FOR_BARE_STRANDS = [1]
    # arbitrary non-false object comparable using 'is'
    # (it might be enough for it to be not None, even if false)
    # (the code could be simplified to let it just be None,
    #  but it's not worth the trouble right now)
    # [bruce 080117]

def dna_updater_follow_strand(phase, strand, strand_axis_info, break_axis, break_strand, axis_break_between_Q = None):
    """
    If phase is 1:

    Loop over strand's base atoms, watching the strand join and leave
    axis chains and move along them; break both axis and strand
    whenever it joins, leaves, or moves discontinuously
    along axis (treating lack of Ax as moving continuously on an
    imaginary Ax chain different from all real ones)
    (for details, see the code comments).

    The breaks must be done only virtually, by calling the provided
    functions with the 3 args (chain, index, whichside) -- the API
    for those functions should be the same as for the method break_chain_later
    of the helper class chains_to_break in the calling code.

    If phase is 2:

    Same, but the only breaks we make are strand_breaks at the same
    places at which axis_break_between_Q says the axis has a break
    (for its API doc see chains_to_break.break_between_Q in caller).

    @return: None
    """
    # For phase 1:
    #
    # Loop over strand's base atoms, watching the strand join and leave
    # axis chains and move along them. If it jumps (moves more than one base)
    # or stays on the same atom (implying that it switched ladder sides --
    #  not physically realistic, but we can't depend on it never happening),
    # pretend that it left the axis and rejoined it. Leaving the axis
    # (pretend or really) breaks the strand there (in terms of which ladder
    # rail it will end up in) and breaks the axis after the leaving point
    # (or on both sides of that axis atom, if we didn't yet know the
    #  direction of travel of the strand along the axis, since we just
    #  entered the axis). Joining an axis breaks that axis before that
    #  point, relative to the direction we'll travel in, so record this
    #  and break the axis as we start to travel.
    #
    # The only other case is if we just change directions, i.e. we hit axis
    # atoms A, B, A. (This is not physically realistic, if only due to the
    #  implied base stacking, but we can't depend on it not happening.)
    # This implies we changed sides of the axis (from one ladder rail to
    # the other), but we don't know if that was before or after B, so we
    # pretend we left and rejoined both before and after B. (In fact,
    # since either leaving or joining requires a break, maybe both these
    # breaks are always required. If not, extra breaks at this stage are ok,
    # since they'll be fixed later when we merge ladders.)
    #
    # In more detail: in case we switched after B in that A B A sequence,
    # do whatever a jump after B would do (no special case required).
    # In case we switched sides before B, we wish we'd done a jump at the
    # prior step, but we know enough now (in the step when we detect this)
    # to do all the same things that would do, so do them now.
    #
    # About rings -- we could be aware of ring index circular order,
    # but we want rings in ladders to be "aligned" in terms of indexes
    # in those ladders (one index for all 3 atoms on one ladder rung),
    # so the easiest way to ensure that is just to pretend rings are
    # chains at this stage (for both strand and axis rings), and break
    # strands whereever they go around the ring (jumping from end to
    # start). This means we should just ignore ring index circularity.
    #
    # (We may or may not patch this later by noticing which ladders are
    # whole rings... since moebius rings are possible, or partial rings
    # (axis rail is ring, strand rail is not), it's probably best to
    # ignore this on ladders and just follow the individual chains as
    # needed.)

    # To get started, we're in the state of having left some axis
    # (all done with it) and about to enter a new one. The loop body
    # can't know that, so record an impossible value of which axis
    # we're in. In general, the loop variables need to know which
    # axis we were in, where we were, and which way we were going
    # or that we just entered it, with a special case for having
    # been in no axis or having been all done with the prior axis.

    # (For phase 2, just modify this slightly.)

    if strand.baselength() == 0:
        # This was not supposed to be possible, but it can happen in the MMKit
        # for the "bare Pl atom". Maybe the strand should refuse to be made then,
        # but this special case seems to fix the assertion error we otherwise
        # got below, from "assert prior_axis is not None # since at least one s_atom",
        # so for now, permit it (with debug print) and see if it causes any other trouble.
        print "fyi: dna_updater_follow_strand bailing on 0-length strand %r" % (strand,)
        return

    assert phase in (1,2)
    if phase == 2:
        break_strand_phase2 = break_strand
        break_strand = noop # optimization
        break_axis = noop # optimization
        assert callable( axis_break_between_Q)
        assert callable( break_strand_phase2)
    else:
        assert axis_break_between_Q is None
        break_strand_phase2 = None # not used, but mollify pylint

    assert callable(break_axis)
    assert callable(break_strand)

    prior_axis = None
    prior_index = None
    prior_direction = None # normally, -1 or 1, or 0 for "just entered"

    for s_atom, s_index in list(strand.baseatom_index_pairs()) + [(None, None)]:
        if s_atom is None:
            # last iteration, just to make strand seem to jump off prior_axis
            # at the end
            assert prior_axis is not None # since at least one s_atom
            (axis, index) = None, None
        else:
            try:
                (axis, index) = strand_axis_info[s_atom.key]
                # Note: this fails for a bare strand atom (permittable
                # by debug_prefs), e.g. in the mmkit -- and more
                # importantly is now permitted "officially" for
                # representing single strands,
                # at least until we implement some 'unpaired-base' atoms.
                # So, pretend all bare strand atoms live on a special
                # fake axis and move along it continuously.
            except KeyError:
                axis = _FAKE_AXIS_FOR_BARE_STRANDS
                index = s_index # always acts like continuous motion
            pass

        # set the variables jumped, new_direction, changed_direction;
        # these are their values unless changed explicitly just below:
        jumped = False
        new_direction = 0 # unknown
        changed_direction = False
        if axis is prior_axis: # 'is' is ok since these are objects, both current, so disjoint in atoms
            delta = index - prior_index
                # ok to ignore ring index circularity (see above for why)
            if delta not in (-1,1):
                # see long comment above for why even 0 means we jumped
                jumped = True
            else:
                new_direction = delta # only used if we don't jump
                if phase == 2:
                    if (axis is not _FAKE_AXIS_FOR_BARE_STRANDS) and \
                       axis_break_between_Q(axis, index, prior_index):
                        # break the strand to match the axis break we just passed over
                        break_strand_phase2(strand, s_index, -1)
                if prior_direction and new_direction != prior_direction:
                    jumped = True
                    new_direction = 0 # required when we pretend to jump
                    changed_direction = True
            del delta
        else:
            jumped = True
        # (after this, jumped, new_direction, changed_direction are final)

        # We need helper routines to do a jump, since there are two
        # different jumps we might do. We need them in pieces since
        # we can't always call them all at once for one jump.
        # (This would be true even if we recorded all jumps and
        #  did them all later, since we don't find out what to record
        #  except in these pieces, during different steps.)
        def do_jump_from_axis(from_axis, from_index, from_direction):
            # break from_axis after the leaving point,
            # or on both sides of that if we had just entered it
            # (in which case "after" is an undefined direction).
            if from_direction == 1:
                break_axis( from_axis, from_index, 1)
            elif from_direction == -1:
                break_axis( from_axis, from_index, -1)
            else:
                break_axis( from_axis, from_index, 1)
                break_axis( from_axis, from_index, -1)
            return
        def do_jump_of_strand( strand, new_s_index):
            # break strand at the jump
            break_strand( strand, new_s_index, -1)
            return
        def do_jump_to_axis_once_new_direction_known( to_axis, entry_index, new_direction):
            # break backwards, before entry point
            break_axis( to_axis, entry_index, - new_direction)
            return

        if jumped:
            assert new_direction == 0
            if prior_axis is not None and prior_axis is not _FAKE_AXIS_FOR_BARE_STRANDS:
                do_jump_from_axis( prior_axis, prior_index, prior_direction)
            if s_index is not None:
                do_jump_of_strand( strand, s_index)
            # set up to break new axis before the entry point --
            # this is done by recording the state as described above,
            # so the next loop iteration will do it (by calling
            #  do_jump_to_axis_once_new_direction_known), once it knows
            # the direction of travel. (If we leave immediately and
            # never know the direction, do_jump_from_axis breaks
            # the axis in both directions and takes care of it.)

            if changed_direction:
                # (rare, not physically realistic; see long comment above)
                # The after-jump is taken care of, but we have to do the
                # before-jump too (see long comment above for details).
                # We know the axis atom path was A B A (with B being prior
                # and A being current), so we know all necessary indices,
                # since we can compute arbitrarily old strand indices.
                # The jump to do right here is A1 -> B A2 where A2 is
                # current step (and steps A1 and A2 had same axis atom)...
                # uh oh, we don't know what the prior direction was at
                # that time -- just use the worst case of 0, which breaks
                # axis on both sides of A.
                A1_axis = axis
                A1_index = index
                X_to_A1_direction = 0 # worst-case guess
                do_jump_from_axis( A1_axis, A1_index, X_to_A1_direction )

                B_strand = strand
                B_s_index = s_index - 1
                do_jump_of_strand( B_strand, B_s_index)

                B_axis = axis
                B_index = prior_index
                A1_to_B_direction = prior_direction
                B_to_A2_direction = - A1_to_B_direction # (same axis)
                    # note: not new_direction, since we zeroed that artificially!
                assert B_to_A2_direction in (-1, 1)
                do_jump_to_axis_once_new_direction_known( B_axis, B_index, B_to_A2_direction )
            pass
        else:
            # we didn't jump
            assert new_direction in (-1,1)
            assert not changed_direction
            assert prior_axis is axis
            if not prior_direction:
                # we just entered this axis in the prior step -
                # break it before entry point
                if axis is not _FAKE_AXIS_FOR_BARE_STRANDS:
                    do_jump_to_axis_once_new_direction_known( axis, prior_index, new_direction )
            pass
        # record state for the next iteration:
        prior_axis = axis
        prior_index = index
        prior_direction = new_direction
        continue # for s_atom, s_index in strand.baseatom_index_pairs()
    return # from dna_updater_follow_strand

# end

