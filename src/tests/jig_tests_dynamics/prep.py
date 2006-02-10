#!/usr/bin/python

import os, shutil, string

def readlines(filename):
    return map(lambda x: x.rstrip(),
               open(filename).readlines())

# These guys have nan's in them
troublesome = [
    "motor_tests/011_rotarymotor-_0_torque_and_0_speed.mmp",
    "motor_tests/016_rotarymotor-negative_torque_and_0_speed.mmp",
    "motor_tests/018_rotarymotor-positive_torque_and_0_speed.mmp",
    "motor_tests/021_rotarymotor-dyno_jig_test_to_same_chunk.mmp"
]

files = readlines("mmpfiles")
files = filter(lambda x: x not in troublesome, files)

def simplifiedMMP(mmp_in, mmp_out):
    # first we translate from a complete MMP file to one the
    # simulator can understand
    groups = [ ]
    lines = readlines(mmp_in)
    outf = open(mmp_out, "w")
    while True:
        L = lines.pop(0)
        if L.startswith("group "):
            lines.insert(0, L)
            break
        outf.write(L + "\n")
    # identify groups and put them into the groups list
    gotFirstGoodGroup = False
    while True:
        nextGroup = [ ]
        # we are either at the start of a group, or something
        # that's not a group
        L = lines.pop(0)
        if L.startswith("end1"):
            # throw this line away, and look for more groups
            L = lines.pop(0)
        if not L.startswith("group ("):
            lines.insert(0, L)
            break
        goodGroup = not (L.startswith("group (View") or
                         L.startswith("group (Clipboard"))
        if goodGroup and not gotFirstGoodGroup:
            while True:
                if L.endswith(" def"):
                    L = L[:-4] + " -"
                outf.write(L + "\n")
                L = lines.pop(0)
                if L.startswith("egroup "):
                    outf.write(L + "\n")
                    break
            gotFirstGoodGroup = True
        else:
            while True:
                L = lines.pop(0)
                if L.startswith("egroup "):
                    break
    # whatever comes after the last group is still in 'lines'
    for L in lines:
        outf.write(L + "\n")
    outf.close()

def setupResults():
    for f in files:
        f1 = string.replace(f, "(", "\(")
        f1 = string.replace(f1, ")", "\)")
        srcfile = "/tmp/foo.mmp"
        xyzfile = f1[:-4] + ".xyz"
        tracefile = f1[:-4] + ".trace"
        simplifiedMMP(f, srcfile)
        cmd = ("../../simulator -i100 -f1 -x -o%s -q%s %s"
               % (xyzfile, tracefile, srcfile))
        assert os.system(cmd) == 0

def compareTraces(goodTrace, iffyTrace):
    def lastLineOfReadings(f):
        lines = readlines(f)
        n = None
        for i in range(len(lines)):
            if lines[i].startswith("# Done:"):
                n = i - 1
                break
        if n == None: return None
        return map(string.atof, lines[n].split())
    good = lastLineOfReadings(goodTrace)
    iffy = lastLineOfReadings(iffyTrace)
    assert len(iffy) == len(good)
    for x, y in map(None, good, iffy):
        if y == 0:
            assert x == 0
        elif y > 0:
            assert 0.99 * y <= x <= 1.01 * y
        else:
            assert 0.99 * y >= x >= 1.01 * y

def testResults():
    # here's where we try to reproduce the results
    for f in files:
        srcfile = "/tmp/foo.mmp"
        questionableXyzfile = "/tmp/foo.xyz"
        questionableTracefile = "/tmp/foo.trace"
        goodXyzfile = f[:-4] + ".xyz"
        goodTracefile = f[:-4] + ".trace"
        simplifiedMMP(f, srcfile)
        cmd = ("../../simulator -i100 -f1 -x -o%s -q%s %s"
               % (questionableXyzfile, questionableTracefile, srcfile))
        assert os.system(cmd) == 0
        compareTraces(goodTracefile, questionableTracefile)

if __name__ == "__main__":
    testResults()
