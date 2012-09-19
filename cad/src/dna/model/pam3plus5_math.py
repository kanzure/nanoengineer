# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
pam3plus5_math.py -- mathematical helper functions for PAM3+5 <-> PAM5 conversion

@author: Bruce (based on formulas developed by Eric D)
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

Reference and explanation for PAM3+5 conversion formulas:

http://www.nanoengineer-1.net/privatewiki/index.php?title=PAM-3plus5plus_coordinates
"""

from geometry.VQT import Q, V, norm, vlen, cross, X_AXIS, Y_AXIS, Z_AXIS

from utilities.debug import print_compact_traceback

from utilities.constants import MODEL_PAM3, MODEL_PAM5

__USE_OLD_VALUES__ = False

# PAM3+5 conversion constants (in Angstroms)
#
# for explanation, see:
#
# http://www.nanoengineer-1.net/privatewiki/index.php?title=PAM-3plus5plus_coordinates

# ==

######## NOT YET FINAL VALUES ########

# Note: these are approximate numbers (from Eric M, a few days before 080412)
# based on what the current PAM3 and PAM5 generators are producing:
#
# x_a' =  2.695
# x_s' = -0.772
# y_s' = -0.889
# x_g  =  8.657
# y_m  =  6.198

if (__USE_OLD_VALUES__):
    X_APRIME = 2.695 # x_a' (where _ means subscript)

    X_SPRIME = -0.772 # x_s'
    Y_SPRIME = -0.889 # y_s'

    SPRIME_D_SDFRAME = V(X_SPRIME, Y_SPRIME, 0.0)
    # position of PAM3 strand sugar 'd' in baseframe 'd' coordinates
    # (for position of sugar 'u' in 'd' coords, see relpos_in_other_frame)

    DEFAULT_X_G = 8.657 # x_g
    DEFAULT_Y_M = 6.198 # y_m
    # confirmed from my debug print (converting from PAM5 duplex from our
    # current generator, bruce 080412:
    ## ... for data_index 2 stored relpos array([  8.65728085e+00,   6.19902777e+00,  -1.33226763e-15])
    # (and similar numbers)
    # the debug prints that generate those lines look like this in the source code in another file:
    ## print "fyi, on %r for data_index %r stored relpos %r" % (self, direction, relpos) ####

    DEFAULT_GV5_RELPOS = V(DEFAULT_X_G, DEFAULT_Y_M, 0.0)
    # most likely, only x (DEFAULT_X_G) actually matters out of these three coords

    DEFAULT_Ss_plus_to_Pl5_RELPOS = V(-3.459, -0.489, -1.59)
    # derived, bruce 080412, for data_index True stored relpos array([-3.45992359, -0.48928416, -1.59      ])
    # the prior stub value was -0.772, -0.889, -1

    DEFAULT_Ss_minus_to_Pl5_RELPOS = V(1.645 , -2.830,  1.59)
    # derived, bruce 080412, for data_index False stored relpos array([ 1.6456331 , -2.83064599,  1.59      ])
    # the prior stub value was -0.772, -0.889, +1

    # see below for how these are used: default_Pl_relative_position, default_Gv_relative_position

# ==

# Here's another set of numbers from EricD as of 2008/04/13.  "[D]on't
# expect full mutual consistency in the last digit or so."
#
# Ss5-Ss5  1.0749 nm
# Ss5-Gv5  0.9233 nm
# Ax3-Gv5  0.4996 nm
#
# measured off of current PAM3 generator output:
#
# Ss3-Ss3  1.5951 nm (no corresponding value in sim-params.txt)
# Ss3-Ax3  0.8697 nm (0.8700 nm in sim-params.txt)
#
# formulas for computing the below numbers from the above:
#
# y_m = Ss5-Ss5 / 2                                =  0.53745
# x_g = sqrt(Ss5-Gv5^2 - y_m^2)                    =  0.750753213446
# x_a' = x_g - Ax3-Gv5                             =  0.251153213446
# x_s' = x_a' - sqrt(Ss3-Ax3^2 - (Ss3-Ss3 / 2)^2)  = -0.095678283826
# y_s' = y_m - (Ss3-Ss3 / 2)                       = -0.2601
#
# to a more reasonable number of significant figures:
#
# x_a' =  0.2512 nm
# x_s' = -0.0957 nm
# y_s' = -0.2601 nm
# x_g  =  0.7508 nm
# y_m  =  0.5375 nm
#
# (where _ means subscript)
#
# The Pl positioning data comes from the following email from EricD:
#
# Reading data from a slightly imprecise on-screen model,
# the FNANO 08 PAM5 Pl offsets  (in base coordinates and nm)
# are:
#
#   Ss->Pl+   0.2875 -0.4081  0.0882
#   Ss->Pl-  -0.2496 -0.2508 -0.2324
#
# To be redundant, the origin and sign conventions
# in base coordinates are:
#
# (0,0,0) is the location of Ss
# +x is toward the major groove
# +y is toward the opposite Ss
# +z is in the 5'-3'direction

if (not __USE_OLD_VALUES__):
    # (x_a', y_m) is the location of the PAM3 Ax, relative to a PAM5 Ss.
    X_APRIME =  2.512 # x_a'

    X_SPRIME = -0.957 # x_s'
    Y_SPRIME = -2.601 # y_s'

    SPRIME_D_SDFRAME = V(X_SPRIME, Y_SPRIME, 0.0)
    # position of PAM3 strand sugar 'd' in baseframe 'd' coordinates
    # (for position of sugar 'u' in 'd' coords, see relpos_in_other_frame)

    DEFAULT_X_G = 7.508 # x_g
    DEFAULT_Y_M = 5.375 # y_m

    DEFAULT_GV5_RELPOS = V(DEFAULT_X_G, DEFAULT_Y_M, 0.0)
    # most likely, only x (DEFAULT_X_G) actually matters out of these three coords

    # The labels on these are different from the above email, so I've
    # selected them to correspond to the signs in the old data.
    # -EricM
    DEFAULT_Ss_plus_to_Pl5_RELPOS = V(-2.496, -2.508, -2.324)
    DEFAULT_Ss_minus_to_Pl5_RELPOS = V(2.875, -4.081,  0.882)

    # see below for how these are used: default_Pl_relative_position, default_Gv_relative_position

BASEPAIR_HANDLE_DISTANCE_FROM_SS_MIDPOINT = 2.4785
    # used to position Ah5 as a basepair handle.
    # The number comes from Eric D mail of 080515:
    #   The point (0.0, 0.0) in the Standard Reference Frame coordinates
    #   [citation omitted] is on the symmetry axis of the Ss-Gv-Ss triangle,
    #   0.24785 nm above the Ss-Ss base of the triangle.
    #   Eric M's code generates virtual sites from positions specified
    #   in these coordinates.
    #
    # I would have thought this should be the same as X_APRIME =  2.512 (x_a')...
    # maybe that's not true, or maybe one of them is slightly wrong.
    # Anyway, this is close, and it probably doesn't matter if it's exactly
    # right (depending on how basepair handles are implemented in ND-1).
    # [bruce 080516]

# ==

def baseframe_from_pam5_data(ss1, gv, ss2):
    """
    Given the positions of the Ss5-Gv5-Ss5 atoms in a PAM5 basepair,
    return the first Ss5's baseframe (and y_m) as a tuple of
    (origin, rel_to_abs_quat, y_m).

    @note: this is correct even if gv is actually an Ax5 position.
    """
    # y axis is parallel to inter-sugar line

    # base plane orientation comes from the other atom, Gv

    # so get x and z axis around that line

    origin = ss1

    y_vector = ss2 - ss1
    y_length = vlen(y_vector)

    ## y_direction = norm(ss2 - ss1)
    y_direction = y_vector / y_length # optimization

    z_direction = norm(cross(gv - ss1, y_direction))
        # BUG: nothing checks for cross product being too small

    x_direction = norm(cross(y_direction, z_direction))
        # this norm is redundant, but might help with numerical stability

    rel_to_abs_quat = Q(x_direction, y_direction, z_direction)

    y_m = y_length / 2.0

    return ( origin, rel_to_abs_quat, y_m )

def baseframe_from_pam3_data(ss1, ax, ss2):
    """
    Given the positions of the Ss3-Ax3-Ss3 atoms in a PAM3 basepair,
    return the first Ss3's baseframe (and y_m) as a tuple of
    (origin, rel_to_abs_quat, y_m).
    """
    yprime_vector = ss2 - ss1
    yprime_length = vlen(yprime_vector)

    y_direction = yprime_vector / yprime_length # optimization of norm

    z_direction = norm(cross(ax - ss1, y_direction))
        # BUG: nothing checks for cross product being too small

    x_direction = norm(cross(y_direction, z_direction))
        # this norm is redundant, but might help with numerical stability

    rel_to_abs_quat = Q(x_direction, y_direction, z_direction)

    # still need origin, easy since we know SPRIME_D_SDFRAME -- but we do have to rotate that, using the quat

    # rel_to_abs_quat.rot( SPRIME_D_SDFRAME ) # this is Ss5 to Ss3 vector, abs coords

    Ss3_d_abspos = ss1
    Ss5_d_abspos = Ss3_d_abspos - rel_to_abs_quat.rot( SPRIME_D_SDFRAME )

    origin = Ss5_d_abspos

    # y_m = (|S'_u - S'_d| / 2) + y_s'
    y_m = yprime_length / 2.0 + Y_SPRIME

    return ( origin, rel_to_abs_quat, y_m )

# ==

def other_baseframe_data( origin, rel_to_abs_quat, y_m): # bruce 080402
    """
    Given baseframe data for one base in a base pair,
    compute it and return it for the other one.
    """
    # todo: optim: if this shows up in profiles, it can be optimized
    # in various ways, or most simply, we can compute and return both
    # baseframes at once from the baseframe_maker functions above,
    # which already know these direction vectors.
    #
    # note: if this needs debugging, turn most of it into a helper function
    # and assert that doing it twice gets values close to starting values.
    direction_x = rel_to_abs_quat.rot(X_AXIS)
    direction_y = rel_to_abs_quat.rot(Y_AXIS)
    direction_z = rel_to_abs_quat.rot(Z_AXIS)
        # todo: optim: extract these more directly from the quat
    other_origin = origin + 2 * y_m * direction_y #k
    other_quat = Q( direction_x, - direction_y, - direction_z)
    return ( other_origin, other_quat, y_m)

# ==

def baseframe_rel_to_abs(origin, rel_to_abs_quat, relpos):
    """
    Using the baseframe specified by origin and rel_to_abs_quat,
    transform the baseframe-relative position relpos
    to an absolute position.
    """
    # optimization: use 2 args, not a baseframe class with 2 attrs
    return origin + rel_to_abs_quat.rot( relpos )

def baseframe_abs_to_rel(origin, rel_to_abs_quat, abspos):
    """
    Using the baseframe specified by origin and rel_to_abs_quat,
    transform the absolute position abspos
    to a baseframe-relative position.
    """
    # optimization: use 2 args, not a baseframe class with 2 attrs
    return rel_to_abs_quat.unrot( abspos - origin )

def relpos_in_other_frame(relpos, y_m):
    x, y, z = relpos
    return V(x, 2 * y_m - y, - z)

# ==

def default_Pl_relative_position(direction): # revised to principled values (though still not final), bruce 080412 late
    """
    """
    # print "stub for default_Pl_relative_position" ####
    ## return V(X_SPRIME, Y_SPRIME, - direction) # stub

    # use direction to choose one of two different values)
    if direction == 1:
        return DEFAULT_Ss_plus_to_Pl5_RELPOS
    else:
        assert direction == -1
        return DEFAULT_Ss_minus_to_Pl5_RELPOS
    pass

def default_Gv_relative_position():
    # print "stub for default_Gv_relative_position" ####
    return DEFAULT_GV5_RELPOS # assume ok to return same value (mutable Numeric array)

# note this in another file:
##        print "fyi, on %r for data_index %r stored relpos %r" % (self, direction, relpos) ####
##            ##### use these prints to get constants for default_Pl_relative_position (and Gv) @@@@

def correct_Ax3_relative_position(y_m):
    # print "stub for correct_Ax3_relative_position" ####
    return V( X_APRIME, y_m, 0.0)

# note: the analogue for Ss3 position is hardcoded, near the call of
# correct_Ax3_relative_position.

# ==

def compute_duplex_baseframes( pam_model, data ):
    """
    Given a list of three lists of positions (for the 3 rails
    of a duplex DnaLadder, in the order strand1, axis, strand2),
    and one of the baseframe_maker functions baseframe_from_pam3_data
    or baseframe_from_pam5_data, construct and return a list of baseframes
    for the strand sugars in the first rail, strand1.

    @raise: various exceptions are possible if the data is degenerate
            (e.g. if any minor groove angle is 0 or 180 degrees, or if
            any atoms overlap within one basepair, or if these are almost
            the case).

    @warning: no sanity checks are done, beyond whatever is done inside
              baseframe_maker.
    """
    # This could be optimized, either by using Numeric to reproduce
    # the calculations in the baseframe_makers on entire arrays in parallel,
    # or (probably better) by recoding this and everything it calls above
    # into C and/or Pyrex. We'll see if it shows up in a profile.
    if pam_model == MODEL_PAM3:
        baseframe_maker = baseframe_from_pam3_data
    elif pam_model == MODEL_PAM5:
        # assume data comes from Gv5 posns, not Ax5 posns
        baseframe_maker = baseframe_from_pam5_data
    else:
        assert 0, "pam_model == %r is not supported" % pam_model
        # to support mixed, caller would need to identify each rail's model...
    # ideally, if len(data) == 2 and pam_model == MODEL_PAM3, we could append
    # another array of ghost base positions to data, and continue --
    # but this would require knowing axis vector at each base index,
    # but (1) we don't have the atoms in this function, (2) even if our caller
    # passed them, that's hard to do at the axis ends, especially for len == 1,
    # except between dna updater runs or before the dna updater dissolves old
    # ladders -- but this is probably called after that stage during dna updater
    # (not sure ###k).
    # [bruce 080528 comment]
    r1, r2, r3 = data
    try:
        return [baseframe_maker(a1,a2,a3) for (a1,a2,a3) in zip(r1,r2,r3)]
    except:
        print_compact_traceback("exception computing duplex baseframes: ")
        # hmm, we don't know for what ladder here, though caller can say
        return None
    pass


# end
