#!/usr/bin/python

from animate import *
from jobqueue import *

preamble = "Presented by"

def drawOneFrame(t, filename):
    # t varies from 0.0 to 1.0 over the course of the sequence
    preamble_xpos = 80
    preamble_ypos = 270 * t - 90
    nanorex_xpos = 50
    nanorex_ypos = 140
    cmd = (('composite -dissolve %d -geometry +%d+%d ' % (100 * t, nanorex_xpos, nanorex_ypos)) +
           'Nanorex_logos/nanorex_logo_text_outline_medium.png blank.jpg /tmp/foo.jpg')
    do(cmd)
    # Fonts are in /usr/lib/openoffice/share/psprint/fontmetric/
    cmd = ('convert -fill \#f53b19 -font Helvetica-Bold -pointsize 48 -draw' +
           ' "text %d,%d \'%s\'" /tmp/foo.jpg %s' %
           (preamble_xpos, preamble_ypos, preamble, filename))
    do(cmd)

m = MpegSequence()
m.simpleSequence(m.SECOND / 2, drawOneFrame, step=1, repeat_final_frame=m.SECOND)
m.encode()
