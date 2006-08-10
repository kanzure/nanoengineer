#!/usr/bin/python

import sys, string, Image, os

def addtext(infile, outfile, textx, texty, message,
            font = Image.open('font.gif')):
    chars = Image.new('RGB', (12 * len(message), 24), (255, 255, 255))
    for i in range(len(message)):
        x = ord(message[i]) - 32
        if x < 0 or x > 96:
            x = 95
        row, col = x >> 4, x & 15
        fontchar = font.crop((col * 12, row * 24,
                              (col + 1) * 12, (row + 1) * 24))
        chars.paste(fontchar, (i * 12, 0, (i + 1) * 12, 24))
    chars.save('/tmp/fontchars.gif')
    os.system('composite -geometry +%d+%d /tmp/fontchars.gif %s %s'%
              (textx * 12, texty * 24, infile, outfile))

if __name__ == '__main__':
    try:
        infile, outfile, textx, texty, message = sys.argv[1:]
        textx = string.atoi(textx)
        texty = string.atoi(texty)
        addtext(infile, outfile,
                string.atoi(textx), string.atoi(texty),
                message)
    except ValueError:
        print """Usage: %s <infile> <outfile> <x> <y> <message>
        <x> and <y> specify the position of the text
        <message> is the content of the text
        """ % sys.argv[0]

if False:
    # Add clocks to existing animation
    for i in range(600, 1100):
        print i
        fil = 'foo.%06d.yuv'
        tmpfil = 'tmp.gif'
        os.system('convert -size 600x450 %s %s' % (fil, tmpfil))
        psecs = ((i / 15) * 15) * 0.01
        message = '%.2f picoseconds' % psecs
        addtext(tmpfil, fil, 1, 1, message)

    for i in range(1400, 2900):
        print i
        fil = 'foo.%06d.yuv'
        tmpfil = 'tmp.gif'
        os.system('convert -size 600x450 %s %s' % (fil, tmpfil))
        nsecs = ((i / 15) * 15) * (1./3)
        message = '%.2f nanoseconds' % nsecs
        addtext(tmpfil, fil, 1, 1, message)
