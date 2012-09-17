# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
import os, sys

seq = 'gattaca'
n = len(seq)
strands = 2
# NAMOT seems broken for one strand? Am I using it wrong?

#########################################################
#
# We will need to ask Paul R to help us understand these distortions.
# I can see what a few of them are doing, but not all.
#
# There is also a probable confusion bug between the "bu" and "pt"
# parameters. See src/input.c lines 1086 and 1102, and notice that
# they appear to be reversed, judging by the names of the fields they
# are changing.
#

# Base parameters
bu = 0.0   # twists the bases perpendicular to helical axis
op = 0.0
pt = 0.0    # makes the inner part of each base dip by that angle

# Unit parameters
# These are applied to the bases and sugars, but NOT to the phosphates??
dx = 0.0
dy = 0.0
dz = 0.0  # additional space between bases, unlike x and y, this is cumulative
twist = 0.0
tilt = 0.0    # does some kind of A-DNA-like twist that I don't get
roll = 10.0

###################################################

def use_pynamot():
    """NAMOT includes a Python interface (pynamot.so, pynamot.dll).
    We can use this (assuming NE-1 is able to find it), but there are
    possible license implications to doing it this way.
    """
    sys.path += ['/usr/local/libexec', '/usr/local/lib']
    import pynamot
    pynamot.Cmd('generate %s d b %s' % (" sd"[strands], seq))
    if True:
        pynamot.Cmd('modify unit dx g 1:1 1:%d %f' % (n, dx))
        pynamot.Cmd('modify unit dy g 1:1 1:%d %f' % (n, dy))
        pynamot.Cmd('modify unit dz g 1:1 1:%d %f' % (n, dz))
        pynamot.Cmd('modify unit twist g 1:1 1:%d %f' % (n, twist))
        pynamot.Cmd('modify unit tilt g 1:1 1:%d %f' % (n, tilt))
        pynamot.Cmd('modify unit roll g 1:1 1:%d %f' % (n, roll))

    pynamot.Cmd('write pdb foo.pdb')


def use_cmd_line():
    # The '-nogui' option comes from our special version of main.c.
    namot = os.popen('namot -nogui', 'w')
    namot.write('generate %s d b %s\n' % (" sd"[strands], seq))

    if False:
        namot.write('modify base bu 1:1:1 1:%d:%d %f\n' % (n, strands, bu))
        namot.write('modify base op 1:1:1 1:%d:%d %f\n' % (n, strands, op))
        namot.write('modify base pt 1:1:1 1:%d:%d %f\n' % (n, strands, pt))

    if True:
        namot.write('modify unit dx l 1:1 1:%d %f\n' % (n, dx))
        namot.write('modify unit dy l 1:1 1:%d %f\n' % (n, dy))
        namot.write('modify unit dz l 1:1 1:%d %f\n' % (n, dz))
        namot.write('modify unit twist l 1:1 1:%d %f\n' % (n, twist))
        namot.write('modify unit tilt l 1:1 1:%d %f\n' % (n, tilt))
        namot.write('modify unit roll l 1:1 1:%d %f\n' % (n, roll))

    namot.write('write pdb foo.pdb\n')
    namot.write('quit\n')
    namot.close()

use_cmd_line()
#use_pynamot()

#os.system('babel foo.pdb foo.mmp')

os.system('rasmol foo.pdb')
