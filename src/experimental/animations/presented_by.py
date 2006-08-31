#!/usr/bin/python

import animate, jobqueue

preamble = "Presented by"

def drawOneFrame(t, filename):
    # t varies from 0.0 to 1.0 over the course of the sequence
    preamble_xpos = 80
    preamble_ypos = 180 * t
    finalx = 50
    nanorex_xpos = 600 - (600 - finalx) * t
    nanorex_ypos = 140
    cmd = (('composite -geometry +%d+%d ' % (nanorex_xpos, nanorex_ypos)) +
           'Nanorex_logos/nanorex_logo_text_outline_medium.png blank.jpg /tmp/foo.jpg')
    jobqueue.do(cmd)
    cmd = 'convert -fill white'
    cmd += (' -font times-roman -pointsize 48 -draw' +
            ' "text %d,%d \'%s\'"' % (preamble_xpos, preamble_ypos, preamble))
    cmd += ' /tmp/foo.jpg ' + filename
    jobqueue.do(cmd)

m = animate.MpegSequence()
m.simpleSequence(5 * m.SECOND, drawOneFrame, step=1, repeat_final_frame=m.SECOND)
m.encode()
