#!/usr/bin/python

import os, sys, shutil, string, types, Numeric

DEBUG = False

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


class ImageBuffer:
    """
    This fast ImageBuffer can perform the image averaging that Bruce
    and Eric D talked about. It can also help put font characters on
    an image.
    """
    def __init__(self, fil=None, size=None):
        if size is None:
            lines = os.popen('convert -verbose %s /dev/null' % fil).readlines()
            if len(lines) < 1 or len(lines[0].split()) < 3:
                print 'confusion', repr(lines)
                raise Exception
            size = lines[0].split()[2]
        self.typ = Numeric.UInt32
        self.w, self.h = w, h = map(string.atoi, size.split('x'))
        planesize = w * h
        if fil is not None:
            # array module has fast file I/O, Numeric might not
            import array
            do('convert -size %s -interlace plane %s /tmp/foo.rgb' % (size, fil))
            a = array.array('B')  # unsigned bytes
            a.fromstring(open('/tmp/foo.rgb').read())
            self.red = Numeric.array(a[:planesize], self.typ)
            self.green = Numeric.array(a[planesize:2*planesize], self.typ)
            self.blue = Numeric.array(a[2*planesize:], self.typ)

    def __add__(self, other):
        assert self.w == other.w
        assert self.h == other.h
        dst = ImageBuffer(size=('%dx%d' % (self.w, self.h)))
        dst.red = self.red + other.red
        dst.green = self.green + other.green
        dst.blue = self.blue + other.blue
        return dst

    def __rmul__(self, other):
        assert type(other) in (types.IntType, types.FloatType)
        dst = ImageBuffer(size=('%dx%d' % (self.w, self.h)))
        dst.red = (other * self.red).astype(self.typ)
        dst.green = (other * self.green).astype(self.typ)
        dst.blue = (other * self.blue).astype(self.typ)
        return dst

    def copy(self, other):
        assert self.w == other.w
        assert self.h == other.h
        dst = ImageBuffer(size=('%dx%d' % (self.w, self.h)))
        dst.red = self.red + other.red
        dst.green = self.green + other.green
        dst.blue = self.blue + other.blue

    def copy(self, typ='B'):
        size = '%dx%d' % (self.w, self.h)
        dst = ImageBuffer(size=size)
        dst.red = self.red.copy()
        dst.green = self.green.copy()
        dst.blue = self.blue.copy()
        return dst

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

    def saveAs(self, fil):
        outf = open('/tmp/foo.rgb', 'w')
        outf.write(self.red.astype(Numeric.UInt8).tostring())
        outf.write(self.green.astype(Numeric.UInt8).tostring())
        outf.write(self.blue.astype(Numeric.UInt8).tostring())
        outf.close()
        do('convert -depth 8 -size %dx%d -interlace plane /tmp/foo.rgb %s' %
           (self.w, self.h, fil))

# Figure out how to make this less dependent on my directory structure.
font = ImageBuffer('/home/wware/polosims/cad/src/experimental/animations/font.gif')

# I did the animation at the fast rate (10 fsec per step) for 500
# frames, and put those in fastpov/fast.xxxxxx.pov. I did the
# animation at the slow rate (333.3 fsec per step for 1500 frames
# (which took three hours) and those are in slowpov/slow.xxxxxx.pov. I
# made the titles by grabbing screenshots of text from OpenOffice and
# cropping it to roughly a 4:3 aspect ratio.

QUICK_CHECK = False


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

# Are we ready to discard any existing animation frames?
OVERWRITE_FRAMES = False

if OVERWRITE_FRAMES:
    do("rm -rf " + mpeg_dir)
    do("mkdir -p " + mpeg_dir)

def convert_and_crop(infile, w1, h1, outfile, w2, h2):
    scale = max(1.0 * w2 / w1, 1.0 * h2 / h1)
    w3, h3 = int(scale * w1), int(scale * h1)
    w3, h3 = max(w3, w2), max(h3, h2)
    # First we scale the image up to w3 x h3, preserving the old aspect ratio.
    # Then we crop it down to w2 x h2 to get the desired size.
    do('convert %s -geometry %dx%d -crop %dx%d+%d+%d %s' %
       (infile, w3, h3, w2, h2, (w3 - w2) / 2, (h3 - h2) / 2, outfile))

def getGifSize(gifFile):
    lines = os.popen('convert -verbose %s /dev/null' % gifFile).readlines()
    dimensions = lines[0].split()[2]
    return map(string.atoi, dimensions.split('x'))  # width, height

def povraySequence(filename_format, begin, frames):
    if QUICK_CHECK: frames = min(frames, 10)
    for i in range(frames):
        pov = (filename_format + '.pov') % i
        tga = '%s/foo.%06d.tga' % (mpeg_dir, i + begin)
        yuv = '%s/foo.%06d.yuv' % (mpeg_dir, i + begin)
        do('povray +I%s +O%s +FT +A +W%d +H%d +V -D +X' %
           (pov, tga, povray_width, povray_height))
        convert_and_crop(tga, povray_width, povray_height,
                         yuv, mpeg_width, mpeg_height)
        os.remove(tga)
    return begin + frames

# By default, each title page stays up for 300 frames, or ten seconds
def titleSequence(gifFile, begin, frames=300):
    if QUICK_CHECK: frames = min(frames, 10)
    h, w = getGifSize(gifFile)
    first_yuv = '%s/foo.%06d.yuv' % (mpeg_dir, begin)
    convert_and_crop(gifFile, h, w, first_yuv, mpeg_width, mpeg_height)
    for i in range(1, frames):
        yuv = '%s/foo.%06d.yuv' % (mpeg_diri + begin)
        shutil.copy(first_yuv, yuv)
    return begin + frames

###################################################

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



#################################################################

def addtext(infile, outfile, textx, texty, message, size=None):
    ib = ImageBuffer(infile, size=size)
    for i in range(len(message)):
        # ascii codes from 32 to 126
        x = ord(message[i]) - 32
        if x < 0 or x > 94:
            x = 0
        if False:
            ib.paste(font,
                     (textx + i) * 12, texty * 24,
                     (x & 0xf) * 12, (x >> 4) * 24,
                     12, 24)
        else:
            ib.merge(font,
                     (textx + i) * 12, texty * 24,
                     (x & 0xf) * 12, (x >> 4) * 24,
                     12, 24)
    ib.saveAs(outfile)

def add_clocks_to_existing_animation():
    def psecs(lo, hi, psecs_per_frame):
        if DEBUG:
            hi = min(hi, lo + 5)
        for i in range(lo, hi):
            psecs = (((i - lo) / 30) * 30) * psecs_per_frame
            message = '%.2f picoseconds' % psecs
            print i, ':', message
            fil = 'foo.%06d.yuv' % i
            addtext(fil, fil, 1, 1, message, '600x450')
    psecs(600, 1100, 0.01)
    psecs(1400, 2900, 1.0 / 3.0)

def averageManyFrames(fmt, lo, hi, size=None):
    fmt += '.yuv'
    ib = ImageBuffer(fmt % lo, size=size)
    for i in range(lo + 1, hi):
        ib2 = ImageBuffer(fmt % i, size=size)
        ib += ib2
    return (1.0 / (hi - lo)) * ib

def hack_motion_blur():
    # N = 4500
    blurring = 20
    N = 20
    povraySequence('/home/wware/tmp/mpeg/subframes/subframes.%06d', 0, N + blurring)
    fmt = '/home/wware/tmp/mpeg/foo.%06d'
    for i in range(N / 10):
        ib = averageManyFrames(fmt, 10 * i, 10 * i + blurring,
                               size='600x450')
        ib.saveAs('cruft.%04d.jpg' % i)

####################################################


if __name__ == '__main__':

    frames = 0
    if OVERWRITE_FRAMES:
        frames = titleSequence('title1.gif', frames)
        frames = titleSequence('title2.gif', frames)
        frames = povraySequence('fastpov/fast.%06d.pov', frames, 500)  # 16.67 seconds
        frames = titleSequence('title3.gif', frames)
        frames = povraySequence('slowpov/slow.%06d.pov', frames, 1500)  # 50 seconds

    sourcefileformat = mpeg_dir + "/foo.%06d"
    outf = open("ne1.par", "w")
    outf.write(params % {'sourcefileformat': sourcefileformat,
                         'frames': frames,
                         'height': mpeg_height,
                         'width': mpeg_width,
                         'bitrate': bitrate})
    outf.close()

    do('mpeg2encode ne1.par foo.mpeg')


if False and __name__ == '__main__':
    try:
        infile, outfile, textx, texty, message = sys.argv[1:]
        textx = string.atoi(textx)
        texty = string.atoi(texty)
        addtext(infile, outfile, textx, texty, message)
    except ValueError:
        print """Usage: %s <infile> <outfile> <x> <y> <message>
        <x> and <y> specify the position of the text
        <message> is the content of the text
        """ % sys.argv[0]
