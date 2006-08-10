#!/usr/bin/python

import os, sys, shutil, string


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
# happy. NTSC is 4:3 with resolution 704x480, so those are non-square
# pixels. Luckily I don't need to figure that out very soon.
def even(x): return int(x) & -2
mpeg_height = povray_height
mpeg_width = even(aspect_ratio * mpeg_height)

# megabits per second of MPEG stream, 3e6 minimum for good quality NTSC
# probably a lower rate is tolerable for Google video display, but you
# want the downloaded video to look better
bitrate = 3e6

os.system("rm -rf /tmp/mpeg")
os.system("mkdir /tmp/mpeg")

def convert_and_crop(infile, w1, h1, outfile, w2, h2):
    scale = max(1.0 * w2 / w1, 1.0 * h2 / h1)
    w3, h3 = int(scale * w1), int(scale * h1)
    w3, h3 = max(w3, w2), max(h3, h2)
    # First we scale the image up to w3 x h3, preserving the old aspect ratio.
    # Then we crop it down to w2 x h2 to get the desired size.
    os.system('convert %s -geometry %dx%d -crop %dx%d+%d+%d %s' %
              (infile, w3, h3, w2, h2, (w3 - w2) / 2, (h3 - h2) / 2, outfile))

def getGifSize(gifFile):
    lines = os.popen('convert -verbose %s /dev/null' % gifFile).readlines()
    dimensions = lines[0].split()[2]
    return map(string.atoi, dimensions.split('x'))  # width, height

def povraySequence(filename_format, begin, frames):
    if QUICK_CHECK: frames = min(frames, 10)
    for i in range(frames):
        pov = filename_format % i
        tga = '/tmp/mpeg/foo.%06d.tga' % (i + begin)
        yuv = '/tmp/mpeg/foo.%06d.yuv' % (i + begin)
        cmd = ('povray +I%s +O%s +FT +A +W%d +H%d +V -D +X' %
               (pov, tga, povray_width, povray_height))
        os.system(cmd)
        convert_and_crop(tga, povray_width, povray_height,
                         yuv, mpeg_width, mpeg_height)
        os.remove(tga)
    return begin + frames

# By default, each title page stays up for 300 frames, or ten seconds
def titleSequence(gifFile, begin, frames=300):
    if QUICK_CHECK: frames = min(frames, 10)
    h, w = getGifSize(gifFile)
    first_yuv = '/tmp/mpeg/foo.%06d.yuv' % begin
    convert_and_crop(gifFile, h, w, first_yuv, mpeg_width, mpeg_height)
    for i in range(1, frames):
        yuv = '/tmp/mpeg/foo.%06d.yuv' % (i + begin)
        shutil.copy(first_yuv, yuv)
    return begin + frames

###################################################

frames = 0
frames = titleSequence('title1.gif', frames)
frames = titleSequence('title2.gif', frames)
frames = povraySequence('fastpov/fast.%06d.pov', frames, 500)  # 16.67 seconds
frames = titleSequence('title3.gif', frames)
frames = povraySequence('slowpov/slow.%06d.pov', frames, 1500)  # 50 seconds

###################################################

sourcefileformat = "/tmp/mpeg/foo.%06d"

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

outf = open("ne1.par", "w")
outf.write(params % {'sourcefileformat': sourcefileformat,
                     'frames': frames,
                     'height': mpeg_height,
                     'width': mpeg_width,
                     'bitrate': bitrate})
outf.close()

os.system('mpeg2encode ne1.par foo.mpeg')
