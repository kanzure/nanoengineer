#!/usr/bin/python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
import sys, os
WHERE = '/home/wware/tmp/mpeg'

JUST_CHECK_FOR_INPUTS = False
REALLY = False

def do(cmd):
    print cmd
    if REALLY: os.system(cmd)


for i in range(1, 9):
    outdir = os.path.join(WHERE, "seq%d" % i)
    do("rm -rf " + outdir)
    do("mkdir " + outdir)

# For the moment, don't worry yet about the nsecs/rots stuff,
# that can be added later.

def testExists(f):
    inf = open(f)   # raises an IOError if it doesn't exist
    #r = inf.read()
    #assert len(r) > 10000
    inf.close()

def average(outdir, srcdir, step, avg, seconds, startSrc=0, startResult=0):
    outdir = os.path.join(WHERE, outdir)
    for i in range(seconds * 30 + 1):
        result = os.path.join(outdir, "frame.%06d.png" % (i + startResult))
        if avg == 1:
            if JUST_CHECK_FOR_INPUTS:
                testExists(os.path.join(WHERE, srcdir,
                                        "wwrot.%06d.png" % (step * i + startSrc)))
            else:
                do("cp " + os.path.join(WHERE, srcdir,
                                        "wwrot.%06d.png" % (step * i + startSrc)) +
                   " " + result)
        else:
            sources = [ ]
            for j in range(avg):
                idx = step * i + j + startSrc
                sources.append(os.path.join(WHERE, srcdir,
                                            "wwrot.%06d.png" % idx))
            if JUST_CHECK_FOR_INPUTS:
                for f in sources:
                    testExists(f)
            else:
                do("convert -average " + " ".join(sources) + " " + result)

def crossFade(outdir, srcdir1, srcdir2, step, avg):
    average(outdir, srcdir1, step, avg, 5)
    # kill the last frame produced from that sequence
    do("rm -f " + os.path.join(WHERE, outdir, "frame.000150.png"))
    print "Doing the crossfade"
    for index in range(15):
        outputFrame = index + 150
        result = os.path.join(WHERE, outdir, "frame.%06d.png" % outputFrame)
        inputFrameStart = outputFrame * step
        if avg == 1:
            if JUST_CHECK_FOR_INPUTS:
                testExists(os.path.join(WHERE, srcdir1,
                                        "wwrot.%06d.png" % inputFrameStart))
                testExists(os.path.join(WHERE, srcdir2,
                                        "wwrot.%06d.png" % inputFrameStart))
            else:
                # Every cross-fade is a half-second, or 15 frames, so average N frames from srcdir1
                # with (15-N) frames from srcdir2
                cmd = "convert -average"
                inframe1 = os.path.join(WHERE, srcdir1,
                                        "wwrot.%06d.png" % inputFrameStart)
                inframe2 = os.path.join(WHERE, srcdir2,
                                        "wwrot.%06d.png" % inputFrameStart)
        else:
            sources1 = [ ]
            for j in range(avg):
                idx = inputFrameStart + j
                sources1.append(os.path.join(WHERE, srcdir1,
                                             "wwrot.%06d.png" % idx))
            sources2 = [ ]
            for j in range(avg):
                idx = inputFrameStart + j
                sources2.append(os.path.join(WHERE, srcdir2,
                                             "wwrot.%06d.png" % idx))
            if JUST_CHECK_FOR_INPUTS:
                for f in sources1 + sources2:
                    testExists(f)
            else:
                do("convert -average " + " ".join(sources1) + " /tmp/blurred1.png")
                do("convert -average " + " ".join(sources2) + " /tmp/blurred2.png")
                inframe1 = "/tmp/blurred1.png"
                inframe2 = "/tmp/blurred2.png"
        if not JUST_CHECK_FOR_INPUTS:
            sources = ((15 - index) * [inframe1,]) + (index * [inframe2,])
            do("convert -average " + " ".join(sources) + " " + result)

    # after cross fade, start at frame 5.5*30 = 165
    average(outdir, srcdir2, step, avg, 5, 165 * step, 165)
    pass

###################################################
# (1) Titles 1 & 2: Medium speed, CPK, 18 seconds
average("seq1", "fast_cpk_png", 4, 4, 18)

# (2) Cross fade: 5 secs medium CPK, half-second fade, 5 secs medium B+S
crossFade("seq2", "fast_cpk_png", "fastpng", 4, 4)

# (3) Title 3: 18 seconds fast B+S (8 secs with title, 10 secs without)
average("seq3", "fastpng", 1, 1, 18)

# (4) Title 4: 18 seconds medium B+S (8 secs with title, 10 secs without)
average("seq4", "fastpng", 4, 4, 18)

# (5) Title 5: 18 seconds fast B+S (8 secs with title, 10 secs without)
average("seq5", "slowpng", 10, 10, 18)

# (6) Titles 6 - 8: 25 seconds, fast jumpy B+S
average("seq6", "slowpng", 10, 1, 25)

# (7) Cross fade: 5 secs slow jumpy B+S, half-second fade, 5 secs slow jumpy CPK
crossFade("seq2", "slowpng", "slow_cpk_png", 10, 1)

# (8) Titles 9 & 10: 27 secs slow CPK (not jumpy)
average("seq8", "slow_cpk_png", 10, 10, 27)
