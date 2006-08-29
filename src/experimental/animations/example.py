#!/usr/bin/python

import os, sys, animate, string, jobqueue

jobqueue.worker_list = [
    ('localhost', '/tmp/mpeg'),
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
    elif arg == 'rendering':
        rendering = True
    elif arg.startswith('framelimit='):
        animate.framelimit = string.atoi(arg[11:])

h = 438
w = 584
animate.set_resolution(w, h)
animate.border = (35, 18)

#################################

animate.remove_old_yuvs()

m = animate.MpegSequence()

if rendering:
    print 'RENDERING...'
    # First step, generate all the subframes we'll need
    #m.rawSubframes(os.path.join(animate.mpeg_dir, 'fastpov'),
    #               os.path.join(animate.mpeg_dir, 'fastjpeg'),
    #               'wwrot.%06d.pov',
    #               2008)
    m.rawSubframes(os.path.join(animate.mpeg_dir, 'slowpov'),
                   os.path.join(animate.mpeg_dir, 'slowjpeg'),
                   'wwrot.%06d.pov',
                   5020,
                   povray_res=(832, 594))
    raise SystemExit

m.titleSequence('1_Title.gif', 300)
m.titleSequence('2_Intro.gif', 300)

# Each frame is 5 femtoseconds, each subframe is 0.5 fs
def textlist(i):
    nsecs = i * 5.0e-6
    return [
        '%.4f nanoseconds' % nsecs,
        '%.4f rotations' % (nsecs / 0.2)
        ]
animate.textlist = textlist

m.titleSequence('3_0.15ps.gif', 300)
m.blur(os.path.join(animate.mpeg_dir,
                    'fastjpeg/wwrot.%06d.jpg'),
       start=0, incr=1, frames=502, avg=1, textlist=textlist)

# Each frame is 20 femtoseconds, each subframe is 2 fs
def textlist(i):
    nsecs = i * 20.0e-6
    return [
        '%.4f nanoseconds' % nsecs,
        '%.4f rotations' % (nsecs / 0.2)
        ]
animate.textlist = textlist

m.titleSequence('4_0.6ps.gif', 300)
m.blur(os.path.join(animate.mpeg_dir,
                    'fastjpeg/wwrot.%06d.jpg'),
       start=0, incr=4, frames=502, avg=4, textlist=textlist)

# Each frame is 200 femtoseconds, each subframe is 20 fs
def textlist(i):
    nsecs = i * 200.0e-6
    return [
        '%.4f nanoseconds' % nsecs,
        '%.4f rotations' % (nsecs / 0.2)
        ]
animate.textlist = textlist

m.titleSequence('5_6.0ps.gif', 300)
m.blur(os.path.join(animate.mpeg_dir,
                    'slowjpeg/wwrot.%06d.jpg'),
       start=0, incr=10, frames=502, avg=10, textlist=textlist)

# no motion blur, average only one image instead of ten
# same time representation as previously
m.titleSequence('6_OneSample.gif', 300)
m.blur(os.path.join(animate.mpeg_dir,
                    'slowjpeg/wwrot.%06d.jpg'),
       start=0, incr=10, frames=502, avg=1, textlist=textlist)

m.titleSequence('7_FutureFab.gif', 300)
m.titleSequence('8_Credits.gif', 300)

m.encode()
