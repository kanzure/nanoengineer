#!/usr/bin/python

import os, sys, string, types, Numeric

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

def do(cmd):
    if DEBUG:
        try:
            raise Exception
        except:
            tb = sys.exc_info()[2]
            f = tb.tb_frame.f_back
            print f.f_code.co_filename, f.f_code.co_name, f.f_lineno
        print cmd
    if os.system(cmd) != 0:
        raise Exception(cmd)

####################
#                  #
#   IMAGE BUFFER   #
#                  #
####################

def _image_size(img):
    lines = os.popen('convert -verbose %s /dev/null' % img).readlines()
    if len(lines) < 1 or len(lines[0].split()) < 3:
        print 'confusion', repr(lines)
        raise Exception
    size = lines[0].split()[2]
    w, h = map(string.atoi, size.split('x'))
    return w, h

class ImageBuffer:
    """
    This fast ImageBuffer can perform the image averaging that Bruce
    and Eric D talked about. It can also help put font characters on
    an image.
    """
    def __init__(self, fil=None, size=None):
        if size is None:
            assert fil is not None
            size = _image_size(fil)
        elif type(size) is types.StringType:
            size = map(string.atoi, size.split('x'))
        self.fil = fil
        self.size = size = tuple(size)
        self.w, self.h = w, h = size
        if fil is not None:
            # array module has fast file I/O, Numeric might not
            import array
            do('convert -size %s -interlace plane %s /tmp/foo.rgb' %
               ('%dx%d' % size, fil))
            a = array.array('B')  # unsigned bytes
            a.fromstring(open('/tmp/foo.rgb').read())
            self.red = Numeric.array(a[:w*h], Numeric.UInt32)
            self.green = Numeric.array(a[w*h:2*w*h], Numeric.UInt32)
            self.blue = Numeric.array(a[2*w*h:], Numeric.UInt32)

    def _subcopy(self):
        dst = ImageBuffer(size=(self.w, self.h))
        dst.fil = self.fil
        dst.size = self.size
        dst.w = self.w
        dst.h = self.h
        return dst

    def copy(self):
        dst = self._subcopy()
        dst.red = self.red.copy()
        dst.green = self.green.copy()
        dst.blue = self.blue.copy()
        return dst

    def __add__(self, other):
        assert self.w == other.w
        assert self.h == other.h
        dst = self._subcopy()
        dst.red = self.red + other.red
        dst.green = self.green + other.green
        dst.blue = self.blue + other.blue
        return dst

    def __mul__(self, other):
        assert type(other) in (types.IntType, types.FloatType)
        dst = self._subcopy()
        dst.red = (other * self.red).astype(Numeric.UInt32)
        dst.green = (other * self.green).astype(Numeric.UInt32)
        dst.blue = (other * self.blue).astype(Numeric.UInt32)
        return dst

    def __rmul__(self, other):
        return other.__mul__(self)

    def paste(self, smaller, x1, y1, x2, y2, w2, h2):
        r1, g1, b1 = self.red, self.green, self.blue
        r2, g2, b2 = smaller.red, smaller.green, smaller.blue
        w1, h1, sw = self.w, self.h, smaller.w
        assert x1 + w2 < w1
        assert y1 + h2 < h1
        A = x1 + y1 * w1
        B = x2 + y2 * sw
        for row in range(h2):
            for dst, src in ((r1, r2), (g1, g2), (b1, b2)):
                dst[A:A+w2] = src[B:B+w2]
            A += w1
            B += sw

    def merge(self, smaller, x1, y1, x2, y2, w2, h2):
        r1, g1, b1 = self.red, self.green, self.blue
        r2, g2, b2 = smaller.red, smaller.green, smaller.blue
        w1, h1, sw = self.w, self.h, smaller.w
        assert x1 + w2 < w1
        assert y1 + h2 < h1
        A = x1 + y1 * w1
        B = x2 + y2 * sw
        for row in range(h2):
            for dst, src in ((r1, r2), (g1, g2), (b1, b2)):
                dst[A:A+w2] = (0.5 * (src[B:B+w2] + dst[A:A+w2])).astype(Numeric.UInt32)
            A += w1
            B += sw

    def addtext(self, textx, texty, message):
        for i in range(len(message)):
            # ascii codes from 32 to 126
            x = ord(message[i]) - 32
            if x < 0 or x > 94:
                x = 0
            #func = self.paste  # opaque text
            func = self.merge  # translucent text
            func(font,
                 (textx + i) * 12, texty * 24,
                 (x & 0xf) * 12, (x >> 4) * 24,
                 12, 24)

    def save(self, fil=None):
        if fil is None:
            fil = self.fil
        assert fil is not None
        outf = open('/tmp/foo.rgb', 'w')
        outf.write(self.red.astype(Numeric.UInt8).tostring())
        outf.write(self.green.astype(Numeric.UInt8).tostring())
        outf.write(self.blue.astype(Numeric.UInt8).tostring())
        outf.close()
        do('convert -depth 8 -size %dx%d -interlace plane /tmp/foo.rgb %s' %
           (self.w, self.h, fil))

# Figure out how to make this less dependent on my directory structure.
font = ImageBuffer('/home/wware/polosims/cad/src/experimental/animations/font.gif')

####################
#                  #
#    MPEG STUFF    #
#                  #
####################

# Dimensions for recommended povray rendering, gotten from the first line
# of any of the *.pov files.
recommended_width, recommended_height = 751, 459
aspect_ratio = (1. * recommended_width) / recommended_height

povray_height = 450
povray_width = int(aspect_ratio * povray_height)

# Google Video uses a 4:3 aspect ratio because that's what is specified
# below in the MPEG parameter file.
aspect_ratio = 4.0 / 3.0
# mpeg_height and mpeg_width must both be even to make mpeg2encode
# happy. NTSC is 4:3 with resolution 704x480, with non-square pixels.
# I don't know if ImageMagick handles non-square pixels.
def even(x): return int(x) & -2
mpeg_height = povray_height
mpeg_width = even(aspect_ratio * mpeg_height)

# Bit rate of the MPEG stream in bits per second. For 30 FPS video at
# 600x450, 2 mbits/sec looks good and gives a file size of about 250
# Kbytes per second of video. At 1.5 mbits/sec you start to see some
# MPEG artifacts, with file size of 190 Kbytes per second of video.
bitrate = 2.0e6

# Where will I keep all my temporary files? On Mandriva, /tmp is small
# but $HOME/tmp is large.
mpeg_dir = '/home/wware/tmp/mpeg'


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


class MpegSequence:

    def __init__(self, bitrate, forReal=False):
        self.bitrate = bitrate
        self.frame = 0
        self.width = mpeg_width
        self.height = mpeg_height
        self.size = (self.width, self.height)
        # We might not want to overwrite all our YUV files
        self.forReal = forReal
        if forReal:
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

    # By default, each title page stays up for 300 frames, or ten seconds
    def titleSequence(self, titlefile, frames=300):
        assert os.path.exists(titlefile)
        if not self.forReal:
            self.frame += frames
            return
        if DEBUG: frames = min(frames, 10)
        first_yuv = self.yuv_name()
        self.convert_and_crop(titlefile, first_yuv)
        self.frame += 1
        for i in range(1, frames):
            import shutil
            shutil.copy(first_yuv, self.yuv_name())
            self.frame += 1

    def previouslyComputed(self, fmt, frames, begin=0):
        assert os.path.exists(titlefile)
        if not self.forReal:
            self.frame += frames
            return
        if DEBUG: frames = min(frames, 10)
        for i in range(frames):
            import shutil
            src = fmt % (i + begin)
            shutil.copy(src, self.yuv_name())
            self.frame += 1

    # This could probably be done a lot more efficiently as a method
    # in ImageBuffer, as long as we don't need to re-sample pixels.
    def convert_and_crop(self, infile, outfile):
        w1, h1 = _image_size(infile)
        w2, h2 = self.size
        scale = max(1.0 * w2 / w1, 1.0 * h2 / h1)
        w3, h3 = int(scale * w1), int(scale * h1)
        w3, h3 = max(w3, w2), max(h3, h2)
        # First we scale the image up to w3 x h3, preserving the old aspect ratio.
        # Then we (shrink if needed and) crop it to the desired size.
        do('convert %s -geometry %dx%d -crop %dx%d+%d+%d %s' %
           (infile, w3, h3, w2, h2, (w3 - w2) / 2, (h3 - h2) / 2, outfile))

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

    def povraySequence(self, povfmt, frames, psecs_per_frame=None,
                       begin=0):
        assert povfmt[-4:] == '.pov'
        if DEBUG: frames = min(frames, 10)
        for i in range(frames):
            if DEBUG: linenum('i', i)
            pov = povfmt % (i + begin)
            assert os.path.exists(pov), 'cannot find file: ' + pov
            tga = '%s/foo.%06d.tga' % (mpeg_dir, self.frame)
            yuv = self.yuv_name()
            nfmt = self.nanosecond_format(psecs_per_frame)
            if self.forReal:
                do('povray +I%s +O%s +FT +A +W%d +H%d +V -D +X 2>/dev/null' %
                   (pov, tga, povray_width, povray_height))
                # think about immediately converting the TGA to an ImageBuffer
                self.convert_and_crop(tga, yuv)
                os.remove(tga)
                if psecs_per_frame is not None:
                    ib = ImageBuffer(yuv, size=self.size)
                    nsecs = 0.001 * i * psecs_per_frame
                    ib.addtext(1, 1, nfmt % nsecs)
                    # Rotation of small bearing at 5 GHz
                    ib.addtext(1, 2, '%.3f rotations' % (nsecs / 0.2))
                    ib.save()
            self.frame += 1

    # This could be combined with povraySequence, which is a special case
    # where avg and ratio are both 1.
    def motionBlurSequence(self, povfmt, frames, psecs_per_subframe,
                           ratio, avg, begin=0):
        # avg is how many subframes are averaged to produce each frame
        # ratio is the ratio of subframes to frames
        if not self.forReal:
            self.frame += frames
            return
        if DEBUG:
            frames = min(frames, 3)
            avg = min(avg, 5)
            print 'MOTION BLUR SEQUENCE'
            print 'povfmt', povfmt
            print 'frames', frames
            print 'psecs_per_subframe', psecs_per_subframe
            print 'ratio', ratio
            print 'avg', avg
            print 'begin', begin
        N = frames * ratio
        nfmt = self.nanosecond_format(ratio * psecs_per_subframe)
        for i in range(frames):
            if DEBUG: linenum('i', i)
            previous = self.frame
            if DEBUG: linenum('starting POV files at', begin + i * ratio)
            self.povraySequence(povfmt, avg, begin=begin+i*ratio)
            self.frame = previous
            ib = ImageBuffer(self.yuv_name(self.frame), size=self.size)
            for j in range(1, avg):
                ib += ImageBuffer(self.yuv_name(self.frame + j),
                                  size=self.size)
            ib *= 1.0 / avg
            if DEBUG: update_psecs = 1
            else: update_psecs = 30
            nsecs = 0.001 * i * ratio * psecs_per_subframe
            ib.addtext(1, 1, nfmt % nsecs)
            # Rotation of small bearing at 5 GHz
            ib.addtext(1, 2, '%.3f rotations' % (nsecs / 0.2))
            ib.save()
            self.frame += 1

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
        do('mpeg2encode foo.par foo.mpeg')


###################################################


def example_usage():
    m = MpegSequence(2e6, True)
    #m.titleSequence('title1.gif')
    #m.titleSequence('title2.gif')
    #m.povraySequence('fastpov/fast.%06d.pov', 450, psecs_per_frame=0.01)
    #m.titleSequence('title3.gif')

    # 10 psecs per animation second -> 1/3 psecs per frame
    # 1/30 psecs per subframe
    if True:
        m.motionBlurSequence('slowpov/slow.%06d.pov', 450, 1. / 30,
                             10, 10)
    else:
        m.motionBlurSequence('slowpov/slow.%06d.pov', 3, 1. / 30,
                             1000, 5)

    m.encode()

# python -c "import animate; animate.example_usage()"

# python -c "import animate; animate.DEBUG=True; animate.example_usage()"
