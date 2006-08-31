#!/usr/bin/python

import animate, jobqueue
from math import *

preamble = "Presented by"

def drawOneFrame(t, filename):
    # t varies from 0.0 to 1.0 over the course of the sequence
    A = -4
    m = (exp(A * t) - exp(A * 0.75)) / (1.0 - exp(A * 0.75))
    m = max(m, 0.0)
    preamble_xpos = 80
    preamble_ypos = 180 - 200.0 * m * cos(30 * t)
    nanorex_xpos = 50
    nanorex_ypos = 140
    cmd = (('composite -dissolve %d -geometry +%d+%d ' % (100 * t, nanorex_xpos, nanorex_ypos)) +
           'Nanorex_logos/nanorex_logo_text_outline_medium.png blank.jpg /tmp/foo.jpg')
    jobqueue.do(cmd)
    cmd = 'convert -fill white'
    cmd += (' -font times-roman -pointsize 48 -draw' +
            ' "text %d,%d \'%s\'"' % (preamble_xpos, preamble_ypos, preamble))
    cmd += ' /tmp/foo.jpg ' + filename
    jobqueue.do(cmd)

m = animate.MpegSequence()
m.simpleSequence(2 * m.SECOND, drawOneFrame, step=1, repeat_final_frame=m.SECOND)
m.encode()
