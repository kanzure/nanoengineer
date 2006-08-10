#!/usr/bin/python

import sys, string, Image, os

try:
    infile, outfile, textx, texty, message = sys.argv[1:]
    textx = string.atoi(textx)
    texty = string.atoi(texty)
except ValueError:
    print """Usage: %s <infile> <outfile> <x> <y> <message>
    <x> and <y> specify the position of the text
    <message> is the content of the text
    """ % sys.argv[0]

font = Image.open('font.gif')

chars = Image.new('RGB', (12 * len(message), 24), (255, 255, 255))
for i in range(len(message)):
    x = ord(message[i]) - 48
    if x < 0 or x > 78:
        x = 79
    row, col = x >> 4, x & 15
    fontchar = font.crop((col * 12, row * 24, (col + 1) * 12, (row + 1) * 24))
    chars.paste(fontchar, (i * 12, 0, (i + 1) * 12, 24))
chars.save('/tmp/fontchars.gif')

os.system('composite -geometry +%d+%d /tmp/fontchars.gif %s %s'%
          (textx * 12, texty * 24, infile, outfile))
