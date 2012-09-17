#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
import os

# Make up a DVD that tests the borders on a television, to find out
# how big the borders need to be. Start with a black field and a white
# horizontal rectangle, and a text display of the number of border
# pixels as the white rectangle grows horizontally. Then do a vertical
# rectangle. The whole thing should be a ten-second animation maybe.

# Start with black.jpg, a 600x450 black image.

# The outcome of this test, with my television and my DVD player, is
# that a 600x450 graphic should have a border that shrinks it to
# 520x420 in order to keep things visible.

def do(cmd):
    print cmd
    if os.system(cmd) != 0:
        raise Exception

def fillHorizontal(border, filename):
    left = border / 2
    right = 600 - left
    cmd = 'convert'
    cmd += ' -fill white'
    cmd += ' -draw "rectangle %d,250 %d,350"' % (left, right)
    cmd += (' -font courier -pointsize 24 -draw' +
            ' "text 200, 110 \'Border test\'"')
    cmd += (' -font courier -pointsize 24 -draw' +
            ' "text 200, 150 \'%d/600 pixels\'"'
            % (right - left))
    cmd += ' black.jpg ' + filename
    do(cmd)

def fillVertical(border, filename):
    top = border / 2
    bottom = 450 - top
    cmd = 'convert'
    cmd += ' -fill white'
    cmd += ' -draw "rectangle 350,%d 450,%d"' % (top, bottom)
    cmd += (' -font courier -pointsize 24 -draw' +
            ' "rotate 90 text 130, -200 \'%d/450 pixels\'"'
            % (bottom - top))
    cmd += ' black.jpg ' + filename
    do(cmd)

yuv_num = 0

def oneSecond(func, param, yuvname):
    global yuv_num
    func(param, yuvname)
    for j in range(1, 30):
        do('cp %s %s' % (yuvname, 'foo.%06d.yuv' % yuv_num))
        yuv_num += 1

for i in range(0, 100, 10):
    yuvname = 'foo.%06d.yuv' % yuv_num
    yuv_num += 1
    oneSecond(fillHorizontal, i, yuvname)

for i in range(0, 100, 10):
    yuvname = 'foo.%06d.yuv' % yuv_num
    yuv_num += 1
    oneSecond(fillVertical, i, yuvname)

do('mpeg2encode foo.par foo.mpeg')
do('rm -f foo.00*.yuv')
do('ffmpeg -i foo.mpeg -sameq foo.mp4')
