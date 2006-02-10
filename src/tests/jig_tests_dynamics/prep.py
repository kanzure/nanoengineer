#!/usr/bin/python

import os, shutil, string

def readlines(filename):
    return map(lambda x: x.rstrip(),
               open(filename).readlines())

files = readlines("mmpfiles")

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

for f in files:
    f1 = string.replace(f, "(", "\(")
    f1 = string.replace(f1, ")", "\)")
    srcfile = "/tmp/foo.mmp"
    xyzfile = f1[:-4] + ".xyz"
    tracefile = f1[:-4] + ".trace"
    simplifiedMMP(f, srcfile)
    cmd = "../../simulator -i100 -f1 -x -o%s -q%s %s" % (xyzfile, tracefile, srcfile)
    assert os.system(cmd) == 0
