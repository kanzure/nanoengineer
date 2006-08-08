import os, sys

sys.path.append('/usr/local/lib')
sys.path.append('/usr/local/libexec')

import pynamot

seq = 10 * 'gattaca'
n = len(seq)
strands = 2
# NAMOT seems broken for one strand? Am I using it wrong?

# Base parameters
bu = 0.0   # twists the bases perpendicular to helical axis
op = 180.0
pt = 0.0    # makes the inner part of each base dip by that angle

# Unit parameters
# These are applied to the bases and sugars, but NOT to the phosphates??
dx = 0.0
dy = 5.0
dz = 0.0
twist = 0.0
tilt = 0.0    # does some kind of A-DNA-like twist that I don't get
roll = 0.0

pynamot.Cmd('generate %s d b %s' % (" sd"[strands], seq))

if True:
    pynamot.Cmd('modify unit dx g 1:1 1:%d %f' % (n, dx))
    pynamot.Cmd('modify unit dy g 1:1 1:%d %f' % (n, dy))
    pynamot.Cmd('modify unit dz g 1:1 1:%d %f' % (n, dz))
    pynamot.Cmd('modify unit twist g 1:1 1:%d %f' % (n, twist))
    pynamot.Cmd('modify unit tilt g 1:1 1:%d %f' % (n, tilt))
    pynamot.Cmd('modify unit roll g 1:1 1:%d %f' % (n, roll))

pynamot.Cmd('write pdb foo.pdb')
sys.exit(0)

##################################################################

namot = os.popen('./namot -nogui', 'w')
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

namot.write('write pdb /home/wware/foo.pdb\n')
namot.write('quit\n')
namot.close()
os.system('babel /home/wware/foo.pdb /home/wware/foo.mmp')
