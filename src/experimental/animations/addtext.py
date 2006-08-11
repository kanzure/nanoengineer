#!/usr/bin/python

import array, sys, string, os, cPickle

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

"""
I have two uses for an ImageBuffer. One is to perform the image
averaging that Bruce and Eric D talked about. The other is to put font
characters on an image.
"""
class ImageBuffer:
    def __init__(self, fil, size=None):
        if size is None:
            lines = os.popen('convert -verbose %s /dev/null' % fil).readlines()
            size = lines[0].split()[2]
        self.w, self.h = w, h = map(string.atoi, size.split('x'))
        planesize = w * h
        do('convert -size %s -interlace plane %s /tmp/foo.rgb' % (size, fil))
        r = open('/tmp/foo.rgb').read()
        self.red = red = array.array('B')
        red.fromstring(r[:planesize])
        self.green = green = array.array('B')
        green.fromstring(r[planesize:2*planesize])
        self.blue = blue = array.array('B')
        blue.fromstring(r[2*planesize:])
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
    def saveAs(self, fil):
        outf = open('/tmp/foo.rgb', 'w')
        self.red.tofile(outf)
        self.green.tofile(outf)
        self.blue.tofile(outf)
        outf.close()
        do('convert -depth 8 -size %dx%d -interlace plane /tmp/foo.rgb %s' %
           (self.w, self.h, fil))

font = ImageBuffer('font.gif')

def addtext(infile, outfile, textx, texty, message, size=None):
    ib = ImageBuffer(infile, size=size)
    for i in range(len(message)):
        # ascii codes from 32 to 126
        x = ord(message[i]) - 32
        if x < 0 or x > 94:
            x = 0
        ib.paste(font,
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


if __name__ == '__main__':
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
