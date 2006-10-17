#!/usr/bin/python

import os, sys, animate, string, jobqueue

jobqueue.worker_list = [
    # ('localhost', '/tmp/mpeg'),
    ('server', '/tmp/mpeg'),
    ('laptop', '/tmp/mpeg'),
    ('mac', '/Users/wware/tmp')
    ]

rendering = False

for arg in sys.argv[1:]:
    if arg.startswith('debug='):
        jobqueue.DEBUG = string.atoi(arg[6:])
    elif arg == 'ugly':
        animate.povray_pretty = False
        animate.setScale(0.25)
    elif arg == 'clean':
        dirs = ('slowjpeg', 'slow_cpk_jpeg', 'fastjpeg')
        for d in dirs:
            jobqueue.do('rm -rf ' + os.path.join(animate.mpeg_dir, d))
            jobqueue.do('mkdir -p ' + os.path.join(animate.mpeg_dir, d))
    elif arg == 'rendering':
        rendering = True
    elif arg.startswith('framelimit='):
        animate.framelimit = string.atoi(arg[11:])

#################################

struct_name = 'wwrot'
# struct_name = 'simp'

animate.remove_old_yuvs()

m = animate.MpegSequence()

if rendering:
    print 'RENDERING...'
    # First step, generate all the subframes we'll need
    m.rawSubframes(os.path.join(animate.mpeg_dir, 'fastpov'),
                   os.path.join(animate.mpeg_dir, 'fastjpeg'),
                   struct_name + '.%06d.pov',
                   2160+1)

    n = 8120
    m.rawSubframes(os.path.join(animate.mpeg_dir, 'slowpov'),
                   os.path.join(animate.mpeg_dir, 'slowjpeg'),
                   struct_name + '.%06d.pov',
                   n+1,
                   povray_res=(832, 594))
    m.rawSubframes(os.path.join(animate.mpeg_dir, 'slow_cpk_pov'),
                   os.path.join(animate.mpeg_dir, 'slow_cpk_jpeg'),
                   struct_name + '.%06d.pov',
                   n+1,
                   povray_res=(832, 594))
    raise SystemExit

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
    jobqueue.do(cmd)
    # Fonts are in /usr/lib/openoffice/share/psprint/fontmetric/
    preamble = "Presented by"
    cmd = ('convert -fill white -font Helvetica-Bold -pointsize 48 -draw' +
           ' "text %d,%d \'%s\'" /tmp/foo.jpg %s' %
           (preamble_xpos, preamble_ypos, preamble, filename))
    jobqueue.do(cmd)

# Start with the Nanorex logo sequence
m.simpleSequence(drawOneFrame, 0.5*m.SECOND, step=1, repeat_final_frame=1.5*m.SECOND)

####################################################################

"""
Motion blur works by averaging some number of subframes to get each
frame. Frames are presented at 30 frames per real second, the NTSC
standard for video."fs" is femtoseconds.

Segments at 6 ps per second: frame is 200 fs, subframe is 20 fs,
average 10 at a time.

Segments at 0.6 ps per second: frame is 20 fs, subframe is 5 fs,
average 4 at a time.

Segments at 0.15 ps per second: frame is 5 fs, averaging 1, subframe
also 5 fs.

I'll need 162 picoseconds of slow simulation using 20 fs subframes, or
8100 subframes.

I'll need 10.8 picoseconds of fast simulation using 5 fs subframes, or
2160 subframes.
"""

def textlist_6ps(framenumber):
    # 200 fs is 200.0e-6 nanoseconds
    nsecs = framenumber * 200.0e-6
    return [
        '%.4f nanoseconds' % nsecs,
        '%.4f rotations' % (nsecs / 0.2)
        ]

def textlist_0_6ps(framenumber):
    nsecs = framenumber * 20.0e-6
    return [
        '%.4f nanoseconds' % nsecs,
        '%.4f rotations' % (nsecs / 0.2)
        ]

def textlist_0_15ps(framenumber):
    nsecs = framenumber * 5.0e-6
    return [
        '%.4f nanoseconds' % nsecs,
        '%.4f rotations' % (nsecs / 0.2)
        ]

SLOW_CPK = os.path.join(animate.mpeg_dir, 'slow_cpk_jpeg/' + struct_name + '.%06d.jpg')
SLOW_TUBES = os.path.join(animate.mpeg_dir, 'slowjpeg/' + struct_name + '.%06d.jpg')
FAST_TUBES = os.path.join(animate.mpeg_dir, 'fastjpeg/' + struct_name + '.%06d.jpg')

def slow_cpk_with_title(titleImage, real_seconds, start=0, avg=10):
    # Background animation with title, 6 ps/s blurred CPK
    # Use "avg=1" to make it jumpy
    return m.motionBlur(SLOW_CPK,
                        start=start, incr=10, frames=real_seconds*m.SECOND, avg=avg,
                        titleImage=titleImage)

def slow_cpk(real_seconds, start=0):
    # Background animation with title, 6 ps/s blurred CPK
    # Use "avg=1" to make it jumpy
    return m.motionBlur(SLOW_CPK,
                        start=start, incr=10, frames=real_seconds*m.SECOND, avg=avg,
                        textlist=textlist_6ps)

def slow_tubes_with_title(titleImage, real_seconds, start=0, avg=10):
    # Background animation with title, 6 ps/s blurred, tubes
    # Use "avg=1" to make it jumpy
    return m.motionBlur(SLOW_TUBES,
                        start=start, incr=10, frames=real_seconds*m.SECOND, avg=avg,
                        titleImage=titleImage)

def slow_tubes(real_seconds, start=0, avg=10):
    # Background animation with title, 6 ps/s blurred, tubes
    # Use "avg=1" to make it jumpy
    return m.motionBlur(SLOW_TUBES,
                        start=start, incr=10, frames=real_seconds*m.SECOND, avg=avg,
                        textlist=textlist_6ps)

def medium_tubes_with_title(titleImage, real_seconds, start=0):
    # Background animation with title, 0.6 ps/s blurred, tubes
    return m.motionBlur(FAST_TUBES,
                        start=start, incr=4, frames=real_seconds*m.SECOND, avg=4,
                        titleImage=titleImage)

def medium_tubes(real_seconds, start=0):
    # Background animation with title, 0.6 ps/s blurred, tubes
    return m.motionBlur(FAST_TUBES,
                        start=start, incr=4, frames=real_seconds*m.SECOND, avg=4,
                        textlist=textlist_0_6ps)

def fast_tubes_with_title(titleImage, real_seconds, start=0):
    # Background animation with title, 0.15 ps/s blurred, tubes
    return m.motionBlur(FAST_TUBES,
                        start=start, incr=1, frames=real_seconds*m.SECOND, avg=1,
                        titleImage=titleImage)

def fast_tubes(real_seconds, start=0):
    # Background animation with title, 0.15 ps/s blurred, tubes
    return m.motionBlur(FAST_TUBES,
                        start=start, incr=1, frames=real_seconds*m.SECOND, avg=1,
                        textlist=textlist_0_15ps)

def cross_fade(real_seconds, from_filespec, to_filespec, start=0, avg=10):
    # We only do cross-fades at 6 ps/sec
    return m.motionBlur(from_filespec,
                        start=start, incr=10, frames=real_seconds*m.SECOND,
                        avg=avg, textlist=textlist_6ps,
                        fadeTo=to_filespec)

####################################################################
# Slow simulation: 23 real seconds, 6900 subframes, 138 psecs

z = slow_cpk_with_title('Titles_22_Sep_2006/1SmallBearingPage-17.gif', 8, start=0)
z = slow_cpk_with_title('Titles_22_Sep_2006/2SmallBearingPage-17.gif', 15, start=z)

####################################################################
# Slow animation: 10.5 real seconds, 3150 subframes, 63 psecs

z = slow_cpk(5, start=0)
z = cross_fade(0.5, SLOW_CPK, SLOW_TUBES, start=z)
z = slow_tubes(5, start=z)

####################################################################
# Fast simulation: 18 seconds, 540 subframes, 2.7 psecs

z = fast_tubes_with_title('Titles_22_Sep_2006/3SmallBearingPage-17.gif', 8, start=0)
z = fast_tubes(10, start=z)

####################################################################
# Fast simulation: 18 real seconds, 2160 subframes, 10.8 psecs

z = medium_tubes_with_title('Titles_22_Sep_2006/4SmallBearingPage-17.gif', 8, start=0)
z = medium_tubes(10, start=z)

####################################################################
# Slow simulation: 18 real seconds, 5400 subframes, 108 psecs

z = slow_tubes_with_title('Titles_22_Sep_2006/5SmallBearingPage-17.gif', 8, start=0)
z = slow_tubes(10, start=z)

####################################################################
# Slow animation: 25 real seconds, 7500 subframes, 150 psecs
# Jumpy with explanation of jumpiness

z = slow_tubes_with_title('Titles_22_Sep_2006/6SmallBearingPage-17.gif', 15, start=0, avg=1)
z = slow_tubes_with_title('Titles_22_Sep_2006/7SmallBearingPage-17.gif', 5, start=z, avg=1)
z = slow_tubes_with_title('Titles_22_Sep_2006/8SmallBearingPage-17.gif', 5, start=z, avg=1)

####################################################################
# Slow simulation: 10.5 real seconds, 3150 subframes, 63 psecs
# Jumpy

z = slow_tubes(5, start=0, avg=1)
z = cross_fade(0.5, SLOW_TUBES, SLOW_CPK, start=z, avg=1)
z = slow_cpk(5, start=z, avg=1)

####################################################################
# Slow simulation: 27 real seconds, 8100 subframes, 162 psecs

z = slow_cpk_with_title('Titles_22_Sep_2006/9SmallBearingPage-17.gif', 12, start=0)
z = slow_cpk_with_title('Titles_22_Sep_2006/10SmallBearingPage-17.gif', 15, start=z)

m.encode()
