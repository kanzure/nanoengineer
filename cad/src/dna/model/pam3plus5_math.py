# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
pam3plus5_math.py -- mathematical helper functions for PAM3+5 <-> PAM5 conversion

@author: Bruce (based on formulas developed by Eric D)
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

Reference and explanation for PAM3+5 conversion formulas:

http://www.nanoengineer-1.net/privatewiki/index.php?title=PAM-3plus5plus_coordinates
"""

from geometry.VQT import Q, V, norm, vlen, cross


# PAM3+5 conversion constants
# explanation: http://www.nanoengineer-1.net/privatewiki/index.php?title=PAM-3plus5plus_coordinates

# STUBS FOR ACTUAL VALUES

X_APRIME = 1.0 # x_a' (where _ means subscript)

X_SPRIME = 1.0 
Y_SPRIME = 1.0

SPRIME_D_SDFRAME = V(X_SPRIME, Y_SPRIME, 0)


# goals:
# - enumerate the numerical parameters i need - see above
# - make sure i know the formulas for the conversion - prototyping them below

# then:
# - ask for the params
# - implement DnaLadder methods/attrs to help with conversion
# - add ladder cmenu op to do an in-place conversion (modifying the model); use this for testing, and it's useful

# ==

def baseframe_from_pam5_data(ss1, gv, ss2):
    """
    Given the positions of the Ss5-Gv5-Ss5 atoms in a PAM5 basepair,
    return the first Ss5's baseframe as a tuple of
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
    return the first Ss3's baseframe as a tuple of
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

    # y_m ??

    return ( origin, rel_to_abs_quat, y_m )

# ==

def baseframe_rel_to_abs(origin, rel_to_abs_quat, relpos):
    # optimization: use 2 args, not a baseframe class with 2 attrs
    return origin + rel_to_abs_quat.rot( relpos )

def baseframe_abs_to_rel(origin, rel_to_abs_quat, abspos):
    # optimization: use 2 args, not a baseframe class with 2 attrs
    return rel_to_abs_quat.unrot( abspos - origin )

# end
