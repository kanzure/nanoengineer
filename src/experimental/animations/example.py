import os, sys, animate, string

for arg in sys.argv[1:]:
    if arg == 'debug':
        animate.DEBUG = True
    elif arg == 'ugly':
        animate.povray_pretty = False
    elif arg.startswith('framelimit='):
        animate.framelimit = string.atoi(arg[11:])

h = 438
w = 584
animate.set_resolution(w, h)
animate.border = (w/10, h/10)

#################################

m = animate.MpegSequence()
m.titleSequence('title1.gif')

# Each frame is 5 femtoseconds, each subframe is 0.5 fs
def textlist(i):
    nsecs = i * 5.0e-6
    return [
        '%.4f nanoseconds' % nsecs,
        '%.3f rotations' % (nsecs / 0.2),
        '%.1f degrees' % (360. * nsecs / 0.2)
        ]
animate.textlist = textlist
m.titleSequence('title2.gif')
m.motionBlurSequence(os.path.join(animate.mpeg_dir, 'fastpov/fast.%06d.pov'),
                     450, 10, 10)


# Each frame is 20 femtoseconds, each subframe is 2 fs
def textlist(i):
    nsecs = i * 20.0e-6
    return [
        '%.3f nanoseconds' % nsecs,
        '%.1f rotations' % (nsecs / 0.2),
        '%.0f degrees' % (360. * nsecs / 0.2)
        ]
animate.textlist = textlist
m.titleSequence('title3.gif')
m.motionBlurSequence(os.path.join(animate.mpeg_dir, 'medpov/med.%06d.pov'),
                     450, 10, 10)


# Each frame is 200 femtoseconds, each subframe is 20 fs
def textlist(i):
    nsecs = i * 200.0e-6
    return [
        '%.2f nanoseconds' % nsecs,
        '%.0f rotations' % (nsecs / 0.2),
        '%.0f degrees' % (360. * nsecs / 0.2)
        ]
animate.textlist = textlist
m.titleSequence('title4.gif')
m.motionBlurSequence(os.path.join(animate.mpeg_dir, 'slowpov/slow.%06d.pov'),
                     450, 10, 10)
m.encode()
