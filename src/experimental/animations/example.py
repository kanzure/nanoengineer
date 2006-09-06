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

# struct_name = 'wwrot'
struct_name = 'simp'

animate.remove_old_yuvs()

m = animate.MpegSequence()

if rendering:
    print 'RENDERING...'
    # First step, generate all the subframes we'll need
    m.rawSubframes(os.path.join(animate.mpeg_dir, 'fastpov'),
                   os.path.join(animate.mpeg_dir, 'fastjpeg'),
                   struct_name + '.%06d.pov',
                   2160+1)

##     n = 10*30*10
    n = 1500
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

"""
Segments that are done at 6 ps per second will have frames that are 200 femtoseconds,
and when averaging ten frames, the subframes will be 20 femtoseconds.

For the title stuff, I need 22 seconds at 6 ps per second.

Segments at 0.6 ps per second: frame is 20 fs, subframe is 5 fs, average 4 at a time.

Segments at 0.15 ps per second: frame is 5 fs, averaging 1, no subframe.



"""

if False:
    # this is just for testing
    m.titleSequence('Titles_31_Aug_2006/Dummy20%Bearing.gif', 300)
else:
    # m.simpleSequence(drawOneFrame, 0.5*m.SECOND, step=1, repeat_final_frame=1.5*m.SECOND)

    # Animated background, 6 ps/s blurred CPK, 8 seconds
    z = m.motionBlur(os.path.join(animate.mpeg_dir,
                                  'slow_cpk_jpeg/' + struct_name + '.%06d.jpg'),
                     start=0, incr=10, frames=8*m.SECOND, avg=10,
                     titleImage='Titles_31_Aug_2006/1_Title.gif')

    # Continued animated background, 6 ps/s blurred CPK, 15 seconds
    m.motionBlur(os.path.join(animate.mpeg_dir,
                              'slow_cpk_jpeg/' + struct_name + '.%06d.jpg'),
                 start=z,
                 incr=10, frames=15*m.SECOND, avg=10,
                 titleImage='Titles_31_Aug_2006/2_InitialText.gif')

    ####################################################################
    # then
    # Regular animation, 6 ps/s CPK, blurred, 5 seconds
    # 1/2 second cross-fade
    # Regular animation, 6 ps/s tubes, blurred, 5 seconds

    def textlist(i):
        nsecs = i * 200.0e-6
        return [
            '%.4f nanoseconds' % nsecs,
            '%.4f rotations' % (nsecs / 0.2)
            ]
    z = m.motionBlur(os.path.join(animate.mpeg_dir,
                                  'slow_cpk_jpeg/' + struct_name + '.%06d.jpg'),
                     start=0, incr=10, frames=5*m.SECOND, avg=10, textlist=textlist)
    z = m.motionBlur(os.path.join(animate.mpeg_dir,
                                  'slow_cpk_jpeg/' + struct_name + '.%06d.jpg'),
                     start=z, incr=10, frames=0.5*m.SECOND, avg=10, textlist=textlist,
                     fadeTo=os.path.join(animate.mpeg_dir,
                                         'slowjpeg/' + struct_name + '.%06d.jpg'))
    m.motionBlur(os.path.join(animate.mpeg_dir,
                              'slowjpeg/' + struct_name + '.%06d.jpg'),
                 start=z, incr=10, frames=5*m.SECOND, avg=10, textlist=textlist)

##     ####################################################################
##     # Each frame is 5 femtoseconds, each subframe is 0.5 fs
##     def textlist(i):
##         nsecs = i * 5.0e-6
##         return [
##             '%.4f nanoseconds' % nsecs,
##             '%.4f rotations' % (nsecs / 0.2)
##             ]
##     animate.textlist = textlist

##     # Animated background, 0.15 ps/s tubes, 8 seconds
##     m.titleSequence('Titles_31_Aug_2006/3_0.15ps.gif', 300)
##     m.motionBlur(os.path.join(animate.mpeg_dir,
##                               'fastjpeg/' + struct_name + '.%06d.jpg'),
##                  start=0, incr=1, frames=m.SECOND, avg=1, textlist=textlist)
##     # then
##     # Regular animation, 0.15 ps/s tubes, 10 seconds

##     ####################################################################
##     # Each frame is 20 femtoseconds, each subframe is 2 fs
##     def textlist(i):
##         nsecs = i * 20.0e-6
##         return [
##             '%.4f nanoseconds' % nsecs,
##             '%.4f rotations' % (nsecs / 0.2)
##             ]
##     animate.textlist = textlist

##     # Animated background, 0.6 ps/s tubes blurred, 8 seconds
##     z = m.motionBlur(os.path.join(animate.mpeg_dir,
##                                   'fastjpeg/' + struct_name + '.%06d.jpg'),
##                      start=0, incr=4, frames=8*m.SECOND, avg=4,
##                      titleImage='Titles_31_Aug_2006/4_0.6ps.gif')
##     # then
##     # Regular animation, 0.6 ps/s tubes blurred, 10 seconds
##     m.motionBlur(os.path.join(animate.mpeg_dir,
##                               'fastjpeg/' + struct_name + '.%06d.jpg'),
##                  start=z, incr=4, frames=10*m.SECOND, avg=4, textlist=textlist)

##     ####################################################################
##     # Each frame is 200 femtoseconds, each subframe is 20 fs
##     def textlist(i):
##         nsecs = i * 200.0e-6
##         return [
##             '%.4f nanoseconds' % nsecs,
##             '%.4f rotations' % (nsecs / 0.2)
##             ]
##     animate.textlist = textlist

##     # Animated background, 6.0 ps/s tubes blurred, 8 seconds
##     z = m.motionBlur(os.path.join(animate.mpeg_dir,
##                                   'slowjpeg/' + struct_name + '.%06d.jpg'),
##                      start=0, incr=10, frames=8*m.SECOND, avg=10,
##                      titleImage='Titles_31_Aug_2006/5_6.0ps.gif')
##     # then
##     # Regular animation, 6.0 ps/s tubes blurred, 10 seconds
##     m.motionBlur(os.path.join(animate.mpeg_dir,
##                               'fastjpeg/' + struct_name + '.%06d.jpg'),
##                  start=z, incr=10, frames=10*m.SECOND, avg=10, textlist=textlist)

##     ####################################################################
##     # Animated background, 6.0 ps/s tubes jumpy, 10 seconds
##     z = m.motionBlur(os.path.join(animate.mpeg_dir,
##                                   'slowjpeg/' + struct_name + '.%06d.jpg'),
##                      start=0, incr=10, frames=502, avg=1,
##                      titleImage='Titles_31_Aug_2006/6_6.0ps_Jumpy.gif')

##     ####################################################################
##     # then
##     # Regular animation, 6.0 ps/s tubes jumpy, 4 seconds
##     # 1/2 second cross-fade to CPK view
##     # Regular animation, 6.0 ps/s CPK jumpy, 5 seconds
##     z = m.motionBlur(os.path.join(animate.mpeg_dir,
##                                   'slowjpeg/' + struct_name + '.%06d.jpg'),
##                      start=z, incr=10, frames=5*m.SECOND, avg=10, textlist=textlist)
##     z = m.motionBlur(os.path.join(animate.mpeg_dir,
##                                   'slowjpeg/' + struct_name + '.%06d.jpg'),
##                      start=z, incr=10, frames=0.5*m.SECOND, avg=10, textlist=textlist,
##                      fadeTo=os.path.join(animate.mpeg_dir,
##                                          'slow_cpk_jpeg/' + struct_name + '.%06d.jpg'))
##     m.motionBlur(os.path.join(animate.mpeg_dir,
##                               'slow_cpk_jpeg/' + struct_name + '.%06d.jpg'),
##                  start=z, incr=10, frames=5*m.SECOND, avg=10, textlist=textlist)

##     ####################################################################
##     # Animated background, 6 ps/s blurred CPK, 12 seconds
##     m.titleSequence('Titles_31_Aug_2006/7_FinalText.gif', 300)
##     # Continue animated background, 6 ps/s blurred CPK, 15 seconds
##     m.titleSequence('Titles_31_Aug_2006/8_Credits.gif', 300)

m.encode()
