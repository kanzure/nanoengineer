#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
from animate import *
from jobqueue import *

preamble = "Presented by"

def drawOneFrame(t, filename):
    def move(t, start, finish):
        return start + t * (finish - start)
    # t varies from 0.0 to 1.0 over the course of the sequence
    preamble_xpos = 80
    preamble_ypos = move(t, -90, 180)
    nanorex_xpos = 50
    nanorex_ypos = move(t, 460, 140)
    cmd = (('composite -geometry +%d+%d ' % (nanorex_xpos, nanorex_ypos)) +
           'Nanorex_logos/nanorex_logo_text_outline_medium.png black.jpg /tmp/foo.jpg')
    do(cmd)
    # Fonts are in /usr/lib/openoffice/share/psprint/fontmetric/
    cmd = ('convert -fill white -font Helvetica-Bold -pointsize 48 -draw' +
           ' "text %d,%d \'%s\'" /tmp/foo.jpg %s' %
           (preamble_xpos, preamble_ypos, preamble, filename))
    do(cmd)

m = MpegSequence()
m.simpleSequence(drawOneFrame, 0.5*m.SECOND, step=1, repeat_final_frame=1.5*m.SECOND)
m.encode()
