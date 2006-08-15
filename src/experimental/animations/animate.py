#!/usr/bin/python

import os, sys, string, types, Numeric, threading, time

# Dimensions for recommended povray rendering, gotten from the first line
# of any of the *.pov files.
recommended_width, recommended_height = 751, 459
povray_aspect_ratio = (1. * recommended_width) / recommended_height

# Bit rate of the MPEG stream in bits per second. For 30 FPS video at
# 600x450, 2 mbits/sec looks good and gives a file size of about 250
# Kbytes per second of video. At 1.5 mbits/sec you start to see some
# MPEG artifacts, with file size of 190 Kbytes per second of video.
bitrate = 3.0e6

# Google Video uses a 4:3 aspect ratio because that's what is specified
# below in the MPEG parameter file.
video_aspect_ratio = 4.0 / 3.0

framelimit = None

####################
#                  #
#   DEBUG STUFF    #
#                  #
####################

DEBUG = False

def linenum(*args):
    try:
        raise Exception
    except:
        tb = sys.exc_info()[2]
        f = tb.tb_frame.f_back
        print f.f_code.co_filename, f.f_code.co_name, f.f_lineno,
    if len(args) > 0:
        print ' --> ',
        for x in args:
            print x,
    print

def do(cmd, howfarback=0):
    if DEBUG:
        try:
            raise Exception
        except:
            tb = sys.exc_info()[2]
            f = tb.tb_frame.f_back
            for i in range(howfarback):
                f = f.f_back
            print f.f_code.co_filename, f.f_code.co_name, f.f_lineno
        print cmd
    if os.system(cmd) != 0:
        raise Exception(cmd)

############################
#                          #
#    DISTRIBUTED POVRAY    #
#                          #
############################

worker_list = [
    ('localhost', '/tmp'),
    ('server', '/tmp'),
    ('laptop', '/tmp'),
    ('mac', '/Users/wware/tmp')
    ]

_which_povray_job = 0

class PovrayJob:
    def __init__(self, srcdir, dstdir, povfmt, povmin, povmax_plus_one, yuv,
                 pwidth, pheight, ywidth, yheight, textlist):

        assert povfmt[-4:] == '.pov'
        assert yuv[-4:] == '.yuv'
        self.srcdir = srcdir
        self.dstdir = dstdir
        self.povfmt = povfmt
        self.povmin = povmin
        self.povmax_plus_one = povmax_plus_one
        self.yuv = yuv
        self.pwidth = pwidth
        self.pheight = pheight
        self.ywidth = ywidth
        self.yheight = yheight
        self.textlist = textlist

        self.srcdir = srcdir
        self.dstdir = dstdir

    def go(self, machine, workdir):

        global _which_povray_job
        self.scriptname = 'povray_job_%08d.sh' % _which_povray_job
        _which_povray_job += 1

        shellscript = open(self.scriptname, 'w')
        shellscript.write('cd %s\n' % workdir)
        tgalist = [ ]
        erasable = [ ]
        for i in range(self.povmin, self.povmax_plus_one):
            pov = os.path.join(workdir, self.povfmt % i)
            tga = pov[:-4] + '.tga'
            shellscript.write('povray +I%s +O%s +FT +A +W%d +H%d +V -D +X 2>/dev/null\n' %
                              (pov, tga, self.pwidth, self.pheight))
            tgalist.append(tga)
            erasable.append(pov)
            erasable.append(tga)
        w2 = int(video_aspect_ratio * self.pheight)

        cmd = ('convert -average %s -crop %dx%d+%d+0 -geometry %dx%d!' %
               (' '.join(tgalist), w2, self.pheight, (self.pwidth - w2) / 2,
                self.ywidth, self.yheight))
        shellscript.write(cmd + ' ' + os.path.join(workdir, self.yuv) + '\n')

        # clean up the pov and tga files
        shellscript.write('rm -f ' + (' '.join(erasable)) + '\n')
        shellscript.close()
        os.system('chmod 755 ' + self.scriptname)

        local = machine in ('localhost', '127.0.0.1')

        if local:
            # do stuff on this machine
            def copy_out(src, dst):
                do('cp ' + src + ' ' + dst, howfarback=1)
            copy_in = copy_out
            def run(cmd):
                do(cmd, howfarback=1)
        else:
            # do stuff on a remote machine
            def copy_out(src, dst):
                do('scp ' + src + ' ' + machine + ':' + dst, howfarback=1)
            def copy_in(src, dst):
                do('scp ' + machine + ':' + src + ' ' + dst, howfarback=1)
            def run(cmd):
                do('ssh ' + machine + ' ' + cmd, howfarback=1)

        '''
        It would be smart to tar-gzip the pov files for shipping to
        the host, like this:
        
        (cd srcdir; tar cf - foo.pov bar.pov baz.pov) | gzip | \
                     ssh machine "(cd workdir; gunzip | tar xf -)"

        Likewise, the yuv file can be gzipped for the return voyage.

        ssh machine "(cd workdir; tar cf - foo.yuv | gzip)" | \
                     gunzip | (cd dstdir; tar xf -)
        '''

        # scp shell script and pov files to worker
        copy_out(self.scriptname,
                 os.path.join(workdir, self.scriptname))
        run('chmod +x ' + os.path.join(workdir, self.scriptname))
        do('rm -f ' + self.scriptname)
        for i in range(self.povmin, self.povmax_plus_one):
            copy_out(os.path.join(self.srcdir, self.povfmt % i),
                     os.path.join(workdir, self.povfmt % i))

        # run the shell script on the worker
        run(os.path.join(workdir, self.scriptname))

        # scp yuv file back from worker
        copy_in(os.path.join(workdir, self.yuv),
                os.path.join(self.dstdir, self.yuv))

        if self.textlist:
            cmd = ('convert -size %dx%d %s -font times-roman -pointsize 30' %
                   (self.ywidth, self.yheight, os.path.join(self.dstdir, self.yuv)))
            for i in range(len(self.textlist)):
                cmd += ' -annotate +10+%d "%s"' % (30 * (i + 1), self.textlist[i])
            cmd += ' /tmp/annotated.%s' % self.yuv
            do(cmd)
            do('mv %s %s' %
               ('/tmp/annotated.%s' % self.yuv,
                os.path.join(self.dstdir, self.yuv)))

        # clean up the worker machine
        run('rm -f %s %s' %
            (os.path.join(workdir, self.scriptname),
             os.path.join(workdir, self.yuv)))

all_workers_stop = False

class Worker(threading.Thread):

    def __init__(self, jobqueue, machine, workdir):
        threading.Thread.__init__(self)
        self.machine = machine
        self.jobqueue = jobqueue
        self.workdir = workdir
        self.busy = True

    def run(self):
        global all_workers_stop
        while not all_workers_stop:
            job = None
            self.jobqueue.lock()
            job = self.jobqueue.get()
            self.jobqueue.unlock()
            if job is None:
                self.busy = False
                return
            try:
                job.go(self.machine, self.workdir)
            except:
                all_workers_stop = True
                raise

class PovrayJobQueue:

    def __init__(self):
        self.worker_pool = [ ]
        self.jobqueue = [ ]
        self._lock = threading.Lock()
        for machine, workdir in worker_list:
            self.worker_pool.append(Worker(self, machine, workdir))

    def lock(self):
        self._lock.acquire()
    def unlock(self):
        self._lock.release()
    def append(self, job):
        self.lock()
        self.jobqueue.append(job)
        self.unlock()
    def get(self):
        q = self.jobqueue
        if len(q) == 0:
            return None
        return q.pop(0)

    def start(self):
        for worker in self.worker_pool:
            worker.start()
    def wait(self):
        busy_workers = 1
        while busy_workers > 0:
            time.sleep(0.5)
            busy_workers = 0
            for worker in self.worker_pool:
                if worker.busy:
                    busy_workers += 1
            if all_workers_stop:
                raise Exception

####################
#                  #
#    MPEG STUFF    #
#                  #
####################

# mpeg_height and mpeg_width must both be even to make mpeg2encode
# happy. NTSC is 4:3 with resolution 704x480, with non-square pixels.
# I don't know if ImageMagick handles non-square pixels.
def even(x): return int(x) & -2
if False:
    povray_height = recommended_height
    povray_width = int(povray_aspect_ratio * povray_height)
    mpeg_height = povray_height
    mpeg_width = even(video_aspect_ratio * mpeg_height)
else:
    povray_height = 480
    povray_width = int(povray_aspect_ratio * povray_height)
    mpeg_width = 704
    mpeg_height = 480

params = """MPEG-2 Test Sequence, 30 frames/sec
%(sourcefileformat)s    /* name of source files */
-         /* name of reconstructed images ("-": don't store) */
-         /* name of intra quant matrix file     ("-": default matrix) */ 
-         /* name of non intra quant matrix file ("-": default matrix) */
stat.out  /* name of statistics file ("-": stdout ) */
1         /* input picture file format: 0=*.Y,*.U,*.V, 1=*.yuv, 2=*.ppm */ 
%(frames)d       /* number of frames */
0         /* number of first frame */
00:00:00:00 /* timecode of first frame */
15        /* N (# of frames in GOP) */
3         /* M (I/P frame distance) */
0         /* ISO/IEC 11172-2 stream */
0         /* 0:frame pictures, 1:field pictures */
%(width)d       /* horizontal_size */
%(height)d       /* vertical_size */
2         /* aspect_ratio_information 1=square pel, 2=4:3, 3=16:9, 4=2.11:1 */
5         /* frame_rate_code 1=23.976, 2=24, 3=25, 4=29.97, 5=30 frames/sec. */
%(bitrate)f  /* bit_rate (bits/s) */
112       /* vbv_buffer_size (in multiples of 16 kbit) */
0         /* low_delay  */
0         /* constrained_parameters_flag */
4         /* Profile ID: Simple = 5, Main = 4, SNR = 3, Spatial = 2, High = 1 */
8         /* Level ID:   Low = 10, Main = 8, High 1440 = 6, High = 4          */
0         /* progressive_sequence */
1         /* chroma_format: 1=4:2:0, 2=4:2:2, 3=4:4:4 */
2         /* video_format: 0=comp., 1=PAL, 2=NTSC, 3=SECAM, 4=MAC, 5=unspec. */
5         /* color_primaries */
5         /* transfer_characteristics */
4         /* matrix_coefficients */
%(width)d       /* display_horizontal_size */
%(height)d       /* display_vertical_size */
0         /* intra_dc_precision (0: 8 bit, 1: 9 bit, 2: 10 bit, 3: 11 bit */
1         /* top_field_first */
0 0 0     /* frame_pred_frame_dct (I P B) */
0 0 0     /* concealment_motion_vectors (I P B) */
1 1 1     /* q_scale_type  (I P B) */
1 0 0     /* intra_vlc_format (I P B)*/
0 0 0     /* alternate_scan (I P B) */
0         /* repeat_first_field */
0         /* progressive_frame */
0         /* P distance between complete intra slice refresh */
0         /* rate control: r (reaction parameter) */
0         /* rate control: avg_act (initial average activity) */
0         /* rate control: Xi (initial I frame global complexity measure) */
0         /* rate control: Xp (initial P frame global complexity measure) */
0         /* rate control: Xb (initial B frame global complexity measure) */
0         /* rate control: d0i (initial I frame virtual buffer fullness) */
0         /* rate control: d0p (initial P frame virtual buffer fullness) */
0         /* rate control: d0b (initial B frame virtual buffer fullness) */
2 2 11 11 /* P:  forw_hor_f_code forw_vert_f_code search_width/height */
1 1 3  3  /* B1: forw_hor_f_code forw_vert_f_code search_width/height */
1 1 7  7  /* B1: back_hor_f_code back_vert_f_code search_width/height */
1 1 7  7  /* B2: forw_hor_f_code forw_vert_f_code search_width/height */
1 1 3  3  /* B2: back_hor_f_code back_vert_f_code search_width/height */
"""


# Where will I keep all my temporary files? On Mandriva, /tmp is small
# but $HOME/tmp is large.
mpeg_dir = '/home/wware/tmp/mpeg'

class MpegSequence:

    def __init__(self, bitrate):
        self.bitrate = bitrate
        self.frame = 0
        self.width = mpeg_width
        self.height = mpeg_height
        self.size = (self.width, self.height)
        do("rm -rf " + mpeg_dir + "/yuvs")
        do("mkdir -p " + mpeg_dir + "/yuvs")

    def __len__(self):
        return self.frame

    def yuv_format(self):
        # Leave off the ".yuv" so we can use it for the
        # mpeg2encode parameter file.
        return mpeg_dir + '/yuvs/foo.%06d'

    def yuv_name(self, i=None):
        if i is None:
            i = self.frame
        return (self.yuv_format() % i) + '.yuv'

    # By default, each title page stays up for five seconds
    def titleSequence(self, titlefile, frames=150):
        assert os.path.exists(titlefile)
        if framelimit is not None: frames = min(frames, framelimit)
        first_yuv = self.yuv_name()
        do('convert -geometry %dx%d! %s %s' %
           (self.width, self.height, titlefile, first_yuv))
        self.frame += 1
        for i in range(1, frames):
            import shutil
            shutil.copy(first_yuv, self.yuv_name())
            self.frame += 1

    def previouslyComputed(self, fmt, frames, begin=0):
        assert os.path.exists(titlefile)
        if framelimit is not None: frames = min(frames, framelimit)
        for i in range(frames):
            import shutil
            src = fmt % (i + begin)
            shutil.copy(src, self.yuv_name())
            self.frame += 1

    def nanosecond_format(self, psecs_per_frame):
        if psecs_per_frame >= 10.0:
            return '%.0f nanoseconds'
        elif psecs_per_frame >= 1.0:
            return '%.1f nanoseconds'
        elif psecs_per_frame >= 0.1:
            return '%.2f nanoseconds'
        elif psecs_per_frame >= 0.01:
            return '%.3f nanoseconds'
        else:
            return '%.4f nanoseconds'

    # This could be combined with povraySequence, which is a special case
    # where avg and ratio are both 1.
    def motionBlurSequence(self, povfmt, frames, psecs_per_subframe,
                           ratio, avg, begin=0):
        # avg is how many subframes are averaged to produce each frame
        # ratio is the ratio of subframes to frames
        if framelimit is not None: frames = min(frames, framelimit)
        if DEBUG:
            print 'MOTION BLUR SEQUENCE'
            print 'povfmt', povfmt
            print 'frames', frames
            print 'psecs_per_subframe', psecs_per_subframe
            print 'ratio', ratio
            print 'avg', avg
            print 'begin', begin
        pq = PovrayJobQueue()
        nfmt = self.nanosecond_format(ratio * psecs_per_subframe)
        yuvs = [ ]
        srcdir, povfmt = os.path.split(povfmt)

        for i in range(frames):
            yuv = self.yuv_name()
            yuvs.append(yuv)
            dstdir, yuv = os.path.split(yuv)
            nsecs = 0.001 * i * ratio * psecs_per_subframe
            textlist = [
                nfmt % nsecs,
                # Rotation of small bearing at 5 GHz
                '%.3f rotations' % (nsecs / 0.2),
                '%.1f degrees' % (360. * nsecs / 0.2)
                ]
            job = PovrayJob(srcdir, dstdir, povfmt,
                            begin + i * ratio,
                            begin + i * ratio + avg,
                            yuv,
                            povray_width, povray_height,
                            mpeg_width, mpeg_height, textlist)
            pq.append(job)
            self.frame += 1
        pq.start()
        pq.wait()

    def encode(self):
        parfil = mpeg_dir + "/foo.par"
        outf = open(parfil, "w")
        outf.write(params % {'sourcefileformat': self.yuv_format(),
                             'frames': len(self),
                             'height': self.height,
                             'width': self.width,
                             'bitrate': self.bitrate})
        outf.close()
        # encoding is an inexpensive operation, do it even if not for real
        do('mpeg2encode %s/foo.par %s/foo.mpeg' % (mpeg_dir, mpeg_dir))


###################################################


def example_usage():
    m = MpegSequence(bitrate)
    m.titleSequence('title1.gif')
    m.titleSequence('title2.gif')
    m.motionBlurSequence(os.path.join(mpeg_dir, 'fastpov/fast.%06d.pov'),
                         450, 0.0005, 10, 10)
    m.titleSequence('title3.gif')
    m.motionBlurSequence(os.path.join(mpeg_dir, 'medpov/med.%06d.pov'),
                         450, 0.002, 10, 10)
    m.titleSequence('title4.gif')
    m.motionBlurSequence(os.path.join(mpeg_dir, 'slowpov/slow.%06d.pov'),
                         450, 0.02, 10, 10)
    m.encode()

'''
Example usages:

python -c "import animate; animate.example_usage()"
python -c "import animate; animate.framelimit=4; animate.example_usage()"
python -c "import animate; animate.DEBUG=True; animate.example_usage()"

or you could write a script that imports and uses this stuff.
'''
