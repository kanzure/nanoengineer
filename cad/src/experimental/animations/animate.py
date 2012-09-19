#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
import os, sys, threading, time, types, jobqueue

bitrate = 6.0e6

framelimit = None

povray_pretty = True

class Dimensions:
    def __init__(self, w, h):
        def even(x):
            return int(x) & -2
        self.width = even(w)
        self.height = even(h)
    def __add__(self, other):
        return Dimensions(self.width + other.width,
                          self.height + other.height)
    def __sub__(self, other):
        return Dimensions(self.width - other.width,
                          self.height - other.height)
    def __rmul__(self, other):
        numtypes = (types.IntType, types.FloatType)
        if type(other) in numtypes:
            return Dimensions(other * self.width,
                              other * self.height)
        elif type(other) is types.TupleType and \
             len(other) is 2 and \
             type(other[0]) in numtypes and \
             type(other[1]) in numtypes:
            return Dimensions(other[0] * self.width,
                              other[1] * self.height)
        else:
            raise TypeError(other)
    def povray(self):
        return ' +W%d +H%d ' % (self.width, self.height)
    def geometry(self):
        return ' -geometry %dx%d ' % (self.width, self.height)
    def exactGeometry(self):
        return ' -geometry %dx%d! ' % (self.width, self.height)
    def resizeFrom(self, wider):
        ar = self.aspectRatio()
        if wider.aspectRatio() > ar:
            # original format is wider, so crop horizontally
            w2 = int(ar * wider.height)
            return (' -crop %dx%d+%d+0 -geometry %dx%d! ' %
                            (w2, wider.height, (wider.width - w2) / 2,
                             self.width, self.height))
        else:
            # original format is taller, so crop vertically
            h2 = int(wider.width / ar)
            return (' -crop %dx%d+0+%d -geometry %dx%d! ' %
                            (wider.width, h2, (wider.height - h2) / 2,
                             self.width, self.height))
    def border(self):
        return ' -bordercolor black -border %dx%d ' % (self.width, self.height)
    def __repr__(self):
        return "<Dimensions %d %d>" % (self.width, self.height)
    def aspectRatio(self):
        return 1.0 * self.width / self.height
    def even(self):
        return (self.width & -2, self.height & -2)

def setScale(scale):
    global povray, video, border, clipped
    # Dimensions for recommended povray rendering, gotten from the first line
    # of any of the *.pov files.
    povray = scale * Dimensions(751, 459)

    video = scale * Dimensions(600, 450)
    # When outside of frame is 600x450, viewable area is 520x410
    border = (0.0666, 0.0444) * video
    clipped = video - 2 * border

setScale(1.0)

class SubframePovrayJob(jobqueue.Job):

    def shellScript(self):

        if povray_pretty:
            povray_options = '+A -V -D +X'
        else:
            povray_options = '-A +Q0 -V -D +X'

        script = ""

        # Worker machine renders a bunch of pov files to make jpeg files
        for pov, jpeg in map(None, self.inputfiles, self.outputfiles):
            tga = pov[:-4] + '.tga'
            script += ('povray +I%s +O%s +FT %s %s 2>/dev/null\n' %
                       (pov, tga, povray_options, povray.povray()))
            script += ('convert %s %s %s\n' %
                       (tga, clipped.resizeFrom(povray), jpeg))
        return script

class MotionBlurJob(jobqueue.Job):

    def shellScript(self):
        num_inputs = len(self.inputfiles)
        num_outputs = len(self.outputfiles)
        script = ""
        i = 0
        for outfile in self.outputfiles:
            script += 'convert -average'
            for j in range(num_inputs / num_outputs):
                script += ' ' + self.inputfiles[i]
                i += 1
            script += ' ' + outfile + '\n'
        return script


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
        #self.width = mpeg_width
        #self.height = mpeg_height
        #self.size = (self.width, self.height)

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

    def titleSequence(self, titlefile, frames=450):
        assert os.path.exists(titlefile)
        if framelimit is not None: frames = min(frames, framelimit)
        first_yuv = self.yuv_name()
        jobqueue.do('convert %s %s %s %s' %
                    (titlefile, border.border(), video.exactGeometry(), first_yuv))
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
                job = SubframePovrayJob(srcdir, dstdir, ifiles, ofiles)
                q.append(job)
            i += num
        q.start()
        q.wait()


    def textBottom(self, jpgfmt, start, incr, frames, avg, divider, rgb, titleImage):
        """You've got some text near the bottom of the screen and you
        want to set a dividing height, and take the lower portion of
        the screen, where the text is, and fade it toward light blue
        so you have good contrast for the text. Above the division you
        have normal chrominance for the sequence.
        """
        # avg is how many subframes are averaged to produce each frame
        # ratio is the ratio of subframes to frames
        if framelimit is not None: frames = min(frames, framelimit)
        tmpimage = '/tmp/foo.jpg'
        tmpimage2 = '/tmp/foo2.jpg'
        averages = [ ]
        averages2 = [ ]
        # Stick the averages in a bunch of GIF files
        assert jpgfmt[-4:] == '.jpg'
        srcdir, fil = os.path.split(jpgfmt)
        jpgfmt = fil
        dstdir = srcdir
        avgfmt = jpgfmt[:-4] + '.gif'
        if avg > 1:
            # parallelize the averaging because it's the slowest operation
            # each job will be five frames
            q = jobqueue.JobQueue()
            i = 0
            while i < frames:
                frames_this_job = min(5, frames - i)
                ifiles = [ ]
                ofiles = [ ]
                for j in range(frames_this_job):
                    P = start + (i + j) * incr
                    for k in range(avg):
                        ifiles.append(jpgfmt % (P + k))
                    ofile = avgfmt % P
                    averages.append(ofile)
                    ofiles.append(ofile)
                job = MotionBlurJob(srcdir, dstdir, ifiles, ofiles)
                q.append(job)
                i += frames_this_job
            q.start()
            q.wait()
        else:
            averages = map(lambda i: jpgfmt % (start + i * incr),
                           range(frames))
        for i in range(frames):
            fnum = start + incr * i
            yuv = (self.yuv_format() % self.frame) + '.yuv'
            jobqueue.do('convert %s %s %s' %
                        (os.path.join(dstdir, averages[i]),
                         clipped.exactGeometry(), tmpimage))
            # tmpimage is now in clipped dimensions
            if titleImage is not None:
                w, h = clipped.width, clipped.height
                jobqueue.do(('mogrify -region +0+%d -fill \"rgb(%d,%d,%d)\" -colorize 75 %s') %
                            (divider, rgb[0], rgb[1], rgb[2], tmpimage))
                jobqueue.do('composite %s %s %s %s' % (titleImage,
                                                       clipped.exactGeometry(),
                                                       tmpimage, tmpimage))
            jobqueue.do('convert %s %s %s %s' % (tmpimage, border.border(),
                                                 video.exactGeometry(), yuv))
            self.frame += 1
        return start + incr * frames

    def motionBlur(self, jpgfmt, start, incr, frames, avg,
                   textlist=None, fadeTo=None, titleImage=None):
        # avg is how many subframes are averaged to produce each frame
        # ratio is the ratio of subframes to frames
        if framelimit is not None: frames = min(frames, framelimit)
        tmpimage = '/tmp/foo.jpg'
        tmpimage2 = '/tmp/foo2.jpg'
        averages = [ ]
        averages2 = [ ]
        # Stick the averages in a bunch of GIF files
        assert jpgfmt[-4:] == '.jpg'
        srcdir, fil = os.path.split(jpgfmt)
        jpgfmt = fil
        dstdir = srcdir
        avgfmt = jpgfmt[:-4] + '.gif'
        if fadeTo is not None:
            assert fadeTo[-4:] == '.jpg'
            fadesrcdir, fadeTo = os.path.split(fadeTo)
            avgfadefmt = fadeTo[:-4] + '.gif'
            fadedstdir = fadesrcdir
        if avg > 1:
            # parallelize the averaging because it's the slowest operation
            # each job will be five frames
            q = jobqueue.JobQueue()
            i = 0
            while i < frames:
                frames_this_job = min(5, frames - i)
                ifiles = [ ]
                ofiles = [ ]
                for j in range(frames_this_job):
                    P = start + (i + j) * incr
                    for k in range(avg):
                        ifiles.append(jpgfmt % (P + k))
                    ofile = avgfmt % P
                    averages.append(ofile)
                    ofiles.append(ofile)
                job = MotionBlurJob(srcdir, dstdir, ifiles, ofiles)
                q.append(job)
                i += frames_this_job
            if fadeTo is not None:
                i = 0
                while i < frames:
                    frames_this_job = min(5, frames - i)
                    ifiles = [ ]
                    ofiles = [ ]
                    for j in range(frames_this_job):
                        P = start + (i + j) * incr
                        for k in range(avg):
                            ifiles.append(fadeTo % (P + k))
                        ofile = avgfadefmt % P
                        averages2.append(ofile)
                        ofiles.append(ofile)
                    job = MotionBlurJob(fadesrcdir, fadedstdir, ifiles, ofiles)
                    q.append(job)
                    i += frames_this_job
            q.start()
            q.wait()
        else:
            averages = map(lambda i: jpgfmt % (start + i * incr),
                           range(frames))
            if fadeTo is not None:
                averages2 = map(lambda i: fadeTo % (start + i * incr),
                                range(frames))

        for i in range(frames):
            fnum = start + incr * i
            yuv = (self.yuv_format() % self.frame) + '.yuv'
            jobqueue.do('convert %s %s %s' %
                        (os.path.join(dstdir, averages[i]),
                         clipped.exactGeometry(), tmpimage))
            # tmpimage is now in clipped dimensions
            if fadeTo is not None:
                jobqueue.do('convert %s %s %s' %
                            (os.path.join(fadedstdir, averages2[i]),
                             clipped.exactGeometry(), tmpimage2))
                # perform a cross-fade
                inputs = ''
                for j in range(frames):
                    if j < i:
                        inputs += ' ' + tmpimage2
                    else:
                        inputs += ' ' + tmpimage
                jobqueue.do('convert -average %s %s' % (inputs, tmpimage))
            if titleImage is not None:
                jobqueue.do('convert %s -average lightblue.jpg lightblue.jpg lightblue.jpg %s %s' %
                            (clipped.exactGeometry(), tmpimage, tmpimage))
                jobqueue.do('composite %s %s %s %s' % (titleImage,
                                                       clipped.exactGeometry(),
                                                       tmpimage, tmpimage))
            elif textlist is not None:
                texts = textlist(i)
                cmd = 'convert ' + tmpimage + ' -font Courier-Bold -pointsize 30 '
                for j in range(len(texts)):
                    cmd += ' -annotate +10+%d "%s"' % (30 * (j + 1), texts[j])
                cmd += ' ' + tmpimage
                jobqueue.do(cmd)
            jobqueue.do('convert %s %s %s %s' % (tmpimage, border.border(),
                                                 video.exactGeometry(), yuv))
            self.frame += 1
        return start + incr * frames

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
                             'height': video.height,
                             'width': video.width,
                             'bitrate': bitrate})
        outf.close()
        # encoding is an inexpensive operation, do it even if not for real
        jobqueue.do('mpeg2encode %s/foo.par %s/foo.mpeg' % (mpeg_dir, mpeg_dir))
        jobqueue.do('rm -f %s/foo.mp4' % mpeg_dir)
        jobqueue.do('ffmpeg -i %s/foo.mpeg -sameq %s/foo.mp4' % (mpeg_dir, mpeg_dir))
