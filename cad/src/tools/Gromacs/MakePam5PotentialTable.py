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
RVDW = 10.0 # pm

# table must extend past cutoff to allow smooth transition
CUTOFF_EXTRA = 1.0 # pm

# DELTA_R should be 0.002 for a gromacs compiled to use single
# precision floats, and 0.0005 for doubles.
DELTA_R = 0.002

def f(r):
    if (r < 0.04):
        return 0.0
    return 1.0 / r

def d2_f(r):
    if (r < 0.04):
        return 0.0
    return 2.0 / (r * r * r)

def g(r):
    if (r < 0.04):
        return 0.0
    return -1.0 / (r * r * r * r * r * r)

def d2_g(r):
    if (r < 0.04):
        return 0.0
    return -42.0 / (r * r * r * r * r * r * r * r)

def h(r):
    if (r < 0.04):
        return 0.0
    return 1.0 / (r * r * r * r * r * r * r * r * r * r * r * r)

def d2_h(r):
    if (r < 0.04):
        return 0.0
    return 156.0 / (r * r * r * r * r * r * r * r * r * r * r * r * r * r)

r = 0.0
while (r < RVDW + CUTOFF_EXTRA + (DELTA_R / 2.0)):
    print "%6.3f %13.6e %13.6e %13.6e %13.6e %13.6e %13.6e" % (r, f(r), d2_f(r), g(r), d2_g(r), h(r), d2_h(r))
    r += DELTA_R
