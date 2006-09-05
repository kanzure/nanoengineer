#!/usr/bin/python

import os, sys, threading, time, jobqueue

# Dimensions for recommended povray rendering, gotten from the first line
# of any of the *.pov files.
recommended_width, recommended_height = 751, 459
povray_aspect_ratio = (1. * recommended_width) / recommended_height
assert povray_aspect_ratio > 4.0 / 3.0

def set_resolution(w, h):
    global mpeg_width, mpeg_height, povray_width, povray_height
    # mpeg_height and mpeg_width must both be even to make mpeg2encode
    # happy. The aspect ratio for video should be 4:3.
    def even(x):
        return int(x) & -2
    mpeg_width = even(w)
    mpeg_height = even(h)
    povray_height = mpeg_height
    povray_width = int(povray_aspect_ratio * povray_height)

def set_width(w):
    set_resolution(w, (3.0 / 4.0) * w)
def set_height(h):
    set_resolution((4.0 / 3.0) * h, h)

set_resolution(600, 450)

bitrate = 6.0e6

framelimit = None

povray_pretty = True

# Viewable area is 520x410
border = (40, 20)

class SubframePovrayJob(jobqueue.Job):
    def __init__(self, srcdir, dstdir, ifiles, ofiles,
                 pwidth, pheight, ywidth, yheight):

        jobqueue.Job.__init__(self, srcdir, dstdir,
                              ifiles, ofiles)

        self.pwidth = pwidth
        self.pheight = pheight
        self.ywidth = ywidth
        self.yheight = yheight

    def shellScript(self):

        if povray_pretty:
            povray_options = '+A -V -D +X'
        else:
            povray_options = '-A +Q0 -V -D +X'

        script = ""

        video_aspect_ratio = 4.0 / 3.0
        w2 = int(video_aspect_ratio * self.pheight)
        # Worker machine renders a bunch of pov files to make jpeg files
        for pov, jpeg in map(None, self.inputfiles, self.outputfiles):
            tga = pov[:-4] + '.tga'
            script += ('povray +I%s +O%s +FT %s +W%d +H%d 2>/dev/null\n' %
                       (pov, tga, povray_options, self.pwidth, self.pheight))
            script += ('convert %s -crop %dx%d+%d+0 -geometry %dx%d! %s\n' %
                       (tga, w2, self.pheight, (self.pwidth - w2) / 2,
                        self.ywidth, self.yheight, jpeg))
        return script

    def postJob(self, worker):
        pass

####################
#                  #
#    MPEG STUFF    #
#                  #
####################

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

def textlist(i):
    return [ ]

# Where will I keep all my temporary files? On Mandriva, /tmp is small
# but $HOME/tmp is large.
mpeg_dir = '/home/wware/tmp/mpeg'

def remove_old_yuvs():
    # you don't always want to do this
    jobqueue.do("rm -rf " + mpeg_dir + "/yuvs")
    jobqueue.do("mkdir -p " + mpeg_dir + "/yuvs")

class MpegSequence:

    SECOND = 30    # NTSC frame rate

    def __init__(self):
        self.frame = 0
        self.width = mpeg_width
        self.height = mpeg_height
        self.size = (self.width, self.height)

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

    if True:
        # By default, each title page stays up for fifteen seconds
        def titleSequence(self, titlefile, frames=450):
            assert os.path.exists(titlefile)
            if framelimit is not None: frames = min(frames, framelimit)
            first_yuv = self.yuv_name()
            if border is not None:
                w, h = self.width - 2 * border[0], self.height - 2 * border[1]
                borderoption = ' -bordercolor black -border %dx%d' % border
            else:
                w, h = self.width, self.height
                borderoption = ''
            jobqueue.do('convert %s -geometry %dx%d! %s %s' %
                        (titlefile, w, h, borderoption, first_yuv))
            self.frame += 1
            for i in range(1, frames):
                import shutil
                shutil.copy(first_yuv, self.yuv_name())
                self.frame += 1
    else:
        # By default, each title page stays up for fifteen seconds
        def titleSequence(self, titlefile, frames=450):
            assert os.path.exists(titlefile)
            if framelimit is not None: frames = min(frames, framelimit)
            first_yuv = self.yuv_name()
            jobqueue.do('convert %s -geometry %dx%d %s' %
                        (titlefile, self.width, self.height, first_yuv))
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

    def rawSubframes(self, srcdir, dstdir, povfmt, howmany, povray_res=None):
        if framelimit is not None: howmany = min(howmany, framelimit)
        if povray_res is None:
            povray_res = povray_width, povray_height
        assert povfmt[-4:] == '.pov'
        jpgfmt = povfmt[:-4] + '.jpg'
        q = jobqueue.JobQueue()
        batchsize = 40
        i = 0
        while i < howmany:

            num = min(batchsize, howmany - i)
            assert num > 0
            ifiles = [ ]
            ofiles = [ ]
            for j in range(num):
                ifiles.append(povfmt % (i + j))
                ofiles.append(jpgfmt % (i + j))

            got_them_all = True
            for ofile in ofiles:
                if not os.path.exists(os.path.join(dstdir, ofile)):
                    got_them_all = False
                    break

            if not got_them_all:
                job = SubframePovrayJob(srcdir, dstdir,
                                        ifiles, ofiles,
                                        povray_res[0], povray_res[1],
                                        mpeg_width, mpeg_height)
                q.append(job)
            i += num
        q.start()
        q.wait()


    def translucentTitleSequence(self, titleImage, povfmt, start, incr, frames, avg):
        # avg is how many subframes are averaged to produce each frame
        # ratio is the ratio of subframes to frames
        if framelimit is not None: frames = min(frames, framelimit)
        tmpimage = '/tmp/foo.jpg'
        video_aspect_ratio = 4.0 / 3.0
        w2 = int(video_aspect_ratio * povray_height)
        ywidth, yheight = mpeg_width, mpeg_height
        if border is not None:
            ywidth -= 2 * border[0]
            yheight -= 2 * border[1]
        for i in range(frames):
            if avg > 1:
                avgopt = '-average'
            else:
                avgopt = ''
            inputs = ''
            fnum = start + incr * i
            yuv = (self.yuv_format() % self.frame) + '.yuv'
            for j in range(avg):
                inputs += ' ' + (povfmt % (fnum + j))
            jobqueue.do('convert %s %s -crop %dx%d+%d+0 -geometry %dx%d! %s' %
                        (avgopt, inputs, w2, povray_height, (povray_width - w2) / 2,
                         ywidth, yheight, tmpimage))
            cmd = ('composite %s %s %s' % (titleImage, tmpimage, yuv))
            jobqueue.do(cmd)
            self.frame += 1


    def crossfade(self, povfmt, povfmt2, start, incr, frames, avg, textlist):
        # avg is how many subframes are averaged to produce each frame
        # ratio is the ratio of subframes to frames
        if framelimit is not None: frames = min(frames, framelimit)
        tmpimage = '/tmp/foo.jpg'
        tmpimage2 = '/tmp/foo2.jpg'
        video_aspect_ratio = 4.0 / 3.0
        w2 = int(video_aspect_ratio * povray_height)
        ywidth, yheight = mpeg_width, mpeg_height
        if border is not None:
            ywidth -= 2 * border[0]
            yheight -= 2 * border[1]
        for i in range(frames):
            if avg > 1:
                avgopt = '-average'
            else:
                avgopt = ''
            inputs = ''
            inputs2 = ''
            fnum = start + incr * i
            yuv = (self.yuv_format() % self.frame) + '.yuv'
            for j in range(avg):
                inputs += ' ' + (povfmt % (fnum + j))
                inputs2 += ' ' + (povfmt2 % (fnum + j))
            jobqueue.do('convert %s %s -crop %dx%d+%d+0 -geometry %dx%d! %s' %
                        (avgopt, inputs, w2, povray_height, (povray_width - w2) / 2,
                         ywidth, yheight, tmpimage))
            jobqueue.do('convert %s %s -crop %dx%d+%d+0 -geometry %dx%d! %s' %
                        (avgopt, inputs2, w2, povray_height, (povray_width - w2) / 2,
                         ywidth, yheight, tmpimage2))
            inputs = ''
            for j in range(frames):
                if j < i:
                    inputs += ' ' + tmpimage2
                else:
                    inputs += ' ' + tmpimage
            jobqueue.do('convert -average %s %s' % (inputs, tmpimage))
            if textlist:
                texts = textlist(i)
                cmd = ''
                for j in range(len(texts)):
                    cmd += ' -annotate +10+%d "%s"' % (30 * (j + 1), texts[j])
                if border is not None:
                    cmd += ' -bordercolor black -border %dx%d' % border
                cmd = ('convert %s -font Courier -pointsize 30 %s %s' %
                       (tmpimage, cmd, yuv))
                jobqueue.do(cmd)
            else:
                jobqueue.do('convert %s %s' % (tmpimage, yuv))
            self.frame += 1

    def motionBlur(self, povfmt, start, incr, frames, avg, textlist):
        # avg is how many subframes are averaged to produce each frame
        # ratio is the ratio of subframes to frames
        if framelimit is not None: frames = min(frames, framelimit)
        tmpimage = '/tmp/foo.jpg'
        video_aspect_ratio = 4.0 / 3.0
        w2 = int(video_aspect_ratio * povray_height)
        ywidth, yheight = mpeg_width, mpeg_height
        if border is not None:
            ywidth -= 2 * border[0]
            yheight -= 2 * border[1]
        for i in range(frames):
            if avg > 1:
                avgopt = '-average'
            else:
                avgopt = ''
            inputs = ''
            fnum = start + incr * i
            yuv = (self.yuv_format() % self.frame) + '.yuv'
            for j in range(avg):
                inputs += ' ' + (povfmt % (fnum + j))
            jobqueue.do('convert %s %s -crop %dx%d+%d+0 -geometry %dx%d! %s' %
                        (avgopt, inputs, w2, povray_height, (povray_width - w2) / 2,
                         ywidth, yheight, tmpimage))
            if textlist:
                texts = textlist(i)
                cmd = ''
                for j in range(len(texts)):
                    cmd += ' -annotate +10+%d "%s"' % (30 * (j + 1), texts[j])
                if border is not None:
                    cmd += ' -bordercolor black -border %dx%d' % border
                cmd = ('convert %s -font Courier -pointsize 30 %s %s' %
                       (tmpimage, cmd, yuv))
                jobqueue.do(cmd)
            else:
                jobqueue.do('convert %s %s' % (tmpimage, yuv))
            self.frame += 1

    def simpleSequence(self, drawOne, frames, step=1, repeat_final_frame=1):
        if framelimit is not None: frames = min(frames, framelimit)
        frames = int(frames)
        step = int(step)
        repeat_final_frame = int(repeat_final_frame)
        for i in range(0, frames+1, step):
            yuv = self.yuv_name()
            self.frame += 1
            t = 1.0 * i / frames
            drawOne(t, yuv)
        for i in range(repeat_final_frame - 1):
            import shutil
            shutil.copy(yuv, self.yuv_name())
            self.frame += 1

    def encode(self):
        parfil = mpeg_dir + "/foo.par"
        outf = open(parfil, "w")
        outf.write(params % {'sourcefileformat': self.yuv_format(),
                             'frames': len(self),
                             'height': self.height,
                             'width': self.width,
                             'bitrate': bitrate})
        outf.close()
        # encoding is an inexpensive operation, do it even if not for real
        jobqueue.do('mpeg2encode %s/foo.par %s/foo.mpeg' % (mpeg_dir, mpeg_dir))
        jobqueue.do('rm -f %s/foo.mp4' % mpeg_dir)
        jobqueue.do('ffmpeg -i %s/foo.mpeg -sameq %s/foo.mp4' % (mpeg_dir, mpeg_dir))
