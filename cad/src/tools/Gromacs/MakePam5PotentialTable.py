#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""

Create an .xvg file suitable for passing as the argument to -table for
mdrun.  The table consists of 7 columns:

r f f'' g g'' h h''

In other words, three functions evaluated at evenly spaced r values,
and their second derivatives.  For the standard Coulomb and
Lennard-Jones potentials, the functions are:

f(r) = 1/r

g(r) = -1/r^6

h(r) = 1/r^12

This table is read by the GROMACS mdrun process when user specified
potential functions are used.  We use this for the non-bonded
interactions between PAM5 model DNA helices.

"""

# RVDW must match the VanDerWaalsCutoffRadius value passed to ND1.
RVDW = 3.0 # pm

# table must extend past cutoff to allow smooth transition
CUTOFF_EXTRA = 1.0 # pm

# DELTA_R should be 0.002 for a gromacs compiled to use single
# precision floats, and 0.0005 for doubles.
DELTA_R = 0.002

import math

def r_1(r):
    if (r < 0.04):
        return 0.0
    return 1.0 / r

def d2_r_1(r):
    if (r < 0.04):
        return 0.0
    return 2.0 / (r * r * r)

def r_6(r):
    if (r < 0.04):
        return 0.0
    return -1.0 / (r * r * r * r * r * r)

def d2_r_6(r):
    if (r < 0.04):
        return 0.0
    return -42.0 / (r * r * r * r * r * r * r * r)

def r_12(r):
    if (r < 0.04):
        return 0.0
    return 1.0 / (r * r * r * r * r * r * r * r * r * r * r * r)

def d2_r_12(r):
    if (r < 0.04):
        return 0.0
    return 156.0 / (r * r * r * r * r * r * r * r * r * r * r * r * r * r)

# For Z(I) = 2 (Mg2+) and rho(i) = 0.02 M,
#
# LambdaD = 1.180059331
# LB = 0.714319428
# J = 1.305703721
# sigma = 0.4 (still)
# Zp = -1 (still)
#
# Yukawa = (0.522281489 / r ) * exp [-(r - 0.4) / 1.180059331 ]

YA = 0.522281489
YB = 0.4
YC = 1.180059331

def yukawa(r):
    if (r < 0.04):
        return yukawa(0.04) + 0.04 - r ;
    return (YA / r) * math.exp(-(r - YB) / YC)

def d_yukawa(r):
    if (r < 0.04):
        return 0.0
    return YA * math.exp(-(r - YB) / YC) * (-1.0/(r * r) - 1.0/(YC * r))

def d2_yukawa(r):
    if (r < 0.04):
        return 0.0
    return YA * math.exp(-(r - YB) / YC) * (2.0/(YC * r * r) + 1.0/(YC * YC * r) + 2.0/(r * r * r))


# Switching function to smoothly reduce a function to zero.
# Transition begins when r == start, below which the value is 1.  The
# value smoothly changes to 0 by the time r == end, after which it
# remains 0.
#
# Potential functions are multiplied by the switching function S:
#
#          (r/start - 1)^4
# S = (1 - ----------------- ) ^4
#          (end/start - 1)^4
#
# in the range start < r < end.

SWITCH_START = 2.0
SWITCH_END = 3.0

SWITCH_LEN = SWITCH_END - SWITCH_START
SWITCH_LEN_4 = SWITCH_LEN * SWITCH_LEN * SWITCH_LEN * SWITCH_LEN

SWITCH_D_1 = ((SWITCH_END / SWITCH_START) - 1)
SWITCH_D_2 = -16.0 / (SWITCH_D_1 * SWITCH_D_1 * SWITCH_D_1 * SWITCH_D_1 * SWITCH_START)
SWITCH_D2_1 = (SWITCH_END / SWITCH_START) - 1
SWITCH_D2_1_4 = SWITCH_D2_1 * SWITCH_D2_1 * SWITCH_D2_1 * SWITCH_D2_1
SWITCH_D2_1_8 = SWITCH_D2_1_4 * SWITCH_D2_1_4
SWITCH_D2_1_8_START_2 = SWITCH_D2_1_8 * SWITCH_START * SWITCH_START

def switch(r):
    if (r <= SWITCH_START):
        return 1.0
    if (r >= SWITCH_END):
        return 0.0

    rDiff = r - SWITCH_START
    S1 = ((rDiff * rDiff * rDiff * rDiff) / SWITCH_LEN_4) - 1
    return S1 * S1 * S1 * S1

def d_switch(r):
    if (r <= SWITCH_START):
        return 0.0
    if (r >= SWITCH_END):
        return 0.0

    t1 = r - SWITCH_START
    t1_4 = t1 * t1 * t1 * t1
    t2 = 1 - t1_4 / SWITCH_LEN_4
    t3 = (r / SWITCH_START) - 1
    t4 = t2 * t2 * t2 * t3 * t3 * t3
    return SWITCH_D_2 * t4

def d2_switch(r):
    if (r <= SWITCH_START):
        return 0.0
    if (r >= SWITCH_END):
        return 0.0

    t1 = r - SWITCH_START
    t1_4 = t1 * t1 * t1 * t1
    t2 = t1_4 / SWITCH_LEN_4

    t3 = (r / SWITCH_START) - 1
    t3_2 = t3 * t3
    t3_4 = t3_2 * t3_2

    return (48 * (-(1 - t2) * SWITCH_D2_1_4 + 4 * t3_4) * (t2 - 1) * (t2 - 1) * t3_2) / SWITCH_D2_1_8_START_2

def switch_yukawa(r):
    return switch(r) * yukawa(r)

def d2_switch_yukawa(r):
    return d2_switch(r) * yukawa(r) + 2.0 * d_switch(r) * d_yukawa(r) + switch(r) * d2_yukawa(r)

r = 0.0
while (r < RVDW + CUTOFF_EXTRA + (DELTA_R / 2.0)):
    print "%6.3f %13.6e %13.6e %13.6e %13.6e %13.6e %13.6e" % (r,
                                                               r_1(r), d2_r_1(r),
                                                               switch_yukawa(r), d2_switch_yukawa(r),
                                                               0, 0)
    r += DELTA_R
