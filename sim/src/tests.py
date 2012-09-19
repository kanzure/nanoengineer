#!/usr/bin/python
# Copyright 2005-2006 Nanorex, Inc.  See LICENSE file for details.

"""Regression and QA test script for the simulator

$Id$

Test cases will generally arrive as MMP files with QM-minimized atom
positions (or for QM dynamics simulations, sequences of atom
positions). These should be translated into *.xyzcmp files, which are
the references that the minimizer should be trying to approach.

The positions from the QM data can be perturbed to provide starting
points for minimization tests. For instance, from the QM-minimized
file tests/rigid_organics/C3H6.mmp provided by Damian, we generate
test_C3H6.xyzcmp as described above, then generate test_C3H6.mmp by
perturbing those positions. Then we use test_C3H6.xyzcmp and
test_C3H6.mmp for testing.
"""

__author__ = "Will"

try:
    import Numeric
except ImportError:
    import numpy as Numeric
import math
import md5
import os
import os.path
import random
import re
import shutil
import string
import sys
import time
import traceback
import types
import unittest

if sys.platform == "win32":
    simulatorCmd = "simulator.exe"
else:
    simulatorCmd = "simulator"

if __name__ == "__main__":
    if not os.path.exists(simulatorCmd):
        print "simulator needs rebuilding"
    if not os.path.exists("sim.so"):
        print "sim.so needs rebuilding"

# Global flags and variables set from command lines
DEBUG = 0
MD5_CHECKS = False
TIME_ONLY = False
TIME_LIMIT = 1.e9
LENGTH_ANGLE_TEST, STRUCTCOMPARE_C_TEST = range(2)
STRUCTURE_COMPARISON_TYPE = LENGTH_ANGLE_TEST
GENERATE = False
KEEP_RESULTS = False
SHOW_TODO = False
VERBOSE_FAILURES = False
LOOSE_TOLERANCES = False
MEDIUM_TOLERANCES = False
TIGHT_TOLERANCES = False
TEST_DIR = None
LIST_EVERYTHING = False

class Unimplemented(AssertionError):
    pass

def todo(str):
    if SHOW_TODO:
        raise Unimplemented(str)

def readlines(filename):
    return map(lambda x: x.rstrip(),
               open(filename).readlines())

testTimes = { }
testsSkipped = 0

##################################################################

# How much variation do we permit in bond lengths and bond
# angles before we think it's a problem? For now these are
# wild guesses, to be later scrutinized by smart people.

# default values, overridden by loose, medium, and tight options
LENGTH_TOLERANCE = 0.139   # angstroms
ANGLE_TOLERANCE = 14.1     # degrees
#LENGTH_TOLERANCE = 0.05    # angstroms
#ANGLE_TOLERANCE = 5        # degrees

class WrongNumberOfAtoms(AssertionError):
    pass

class PositionMismatch(AssertionError):
    pass

class LengthAngleMismatch(AssertionError):
    pass

def V(*v):
    return Numeric.array(v, Numeric.Float)

def vlen(v1):
    return math.sqrt(Numeric.dot(v1, v1))

def angleBetween(vec1, vec2):
    TEENY = 1.0e-10
    lensq1 = Numeric.dot(vec1, vec1)
    if lensq1 < TEENY:
        return 0.0
    lensq2 = Numeric.dot(vec2, vec2)
    if lensq2 < TEENY:
        return 0.0
    dprod = Numeric.dot(vec1 / lensq1**.5, vec2 / lensq2**.5)
    if dprod >= 1.0:
        return 0.0
    if dprod <= -1.0:
        return 180.0
    return (180/math.pi) * math.acos(dprod)

def measureLength(xyz, first, second):
    """Returns the angle between two atoms (nuclei)"""
    p0 = apply(V, xyz[first])
    p1 = apply(V, xyz[second])
    return vlen(p0 - p1)

def measureAngle(xyz, first, second, third):
    """Returns the angle between two atoms (nuclei)"""
    p0 = apply(V, xyz[first])
    p1 = apply(V, xyz[second])
    p2 = apply(V, xyz[third])
    v01, v21 = p0 - p1, p2 - p1
    return angleBetween(v01, v21)

_PeriodicTable = [
    "X",  # our singlet has element number zero
    "H",                                                "He",
    "Li", "Be",             "B",  "C",  "N", "O", "F",  "Ne",
    "Na", "Mg",             "Al", "Si", "P", "S", "Cl", "Ar",
    "K",  "Ca" #Sc,Ti,V,Cr,Mn,Fe....
    ]

_MmpAtomPattern = re.compile("^atom (\d+) \((\d+)\) " +
                             "\((\-?\d+), (\-?\d+), (\-?\d+)\)")

class Atom:
    def __init__(self):
        self.elem = 0
        self.x = self.y = self.z = 0.0
        self.bonds = [ ]
    def clone(self):
        "permit deep cloning of structure files"
        a = Atom()
        for key in self.__dict__.keys():
            setattr(a, key, getattr(self, key))
        return a
    def __repr__(self):
        element = _PeriodicTable[self.elem]
        return "%s %f %f %f" % (element, self.x, self.y, self.z)

class XyzFile:
    """Python class to contain information from an XYZ file"""
    def __init__(self):
        self.atoms = [ ]
    def clone(self):
        other = XyzFile()
        other.atoms = [ ]
        for a in self.atoms:
            other.atoms.append(a.clone())
        return other
    def getAtom(self, i):
        return self.atoms[i]
    def __getitem__(self, i):
        a = self.atoms[i]
        return (a.x, a.y, a.z)
    def __setitem__(self, i, xyz):
        a = self.atoms[i]
        a.x, a.y, a.z = xyz
    def __len__(self):
        return len(self.atoms)
    def read(self, filename):
        inf = open(filename)
        self.readstring(inf.read())
        inf.close()
    def readstring(self, lines):
        lines = lines.split("\n")
        numAtoms = string.atoi(lines[0].strip())
        lines = lines[2:]
        for i in range(numAtoms):
            a = Atom()
            element, x, y, z = lines[i].split()
            a.elem = _PeriodicTable.index(element)
            a.x, a.y, a.z = map(string.atof, (x, y, z))
            self.atoms.append(a)
    def readFromList(self, lst):
        assert type(lst) == types.ListType
        for atminfo in lst:
            a = Atom()
            element, x, y, z = atminfo
            a.elem = _PeriodicTable.index(element)
            a.x, a.y, a.z = map(string.atof, (x, y, z))
            self.atoms.append(a)
    def write(self, title, outf=None):
        if outf == None:
            outf = sys.stdout
        outf.write("%d\n%s\n" % (len(self.atoms), title))
        for atm in self.atoms:
            element = _PeriodicTable[self.elem]
            outf.write("%s %f %f %f\n" %
                       (element, self.x, self.y, self.z))

class MmpFile:
    """This is meant to be a Python class representing a MMP file. It
    is not intended to represent ALL the information in a MMP file,
    although it might do that in some distant-future version."""
    class _AtomHolder:
        """Atom holders are indices into the MmpFile.atoms list,
        and that's done so that MmpFiles are easier to clone.
        """
        def __init__(self, owner, match, rest):
            a = Atom()
            groups = match.groups()
            a.elem = elem = string.atoi(groups[1])
            str = "atom %s" % groups[0]
            str += " (%s)" % groups[1]
            str += " (%d, %d, %d)"
            str += rest
            a._mmpstr = str
            a.x = 0.001 * string.atoi(groups[2])
            a.y = 0.001 * string.atoi(groups[3])
            a.z = 0.001 * string.atoi(groups[4])
            self._owner = owner
            self._index = len(owner.atoms)
            owner.atoms.append(a)
        def mmpBonds(self, line):
            if hasattr(self, "_str") or not line.startswith("bond"):
                return False
            a = self._owner.atoms[self._index]
            for b in line.split()[1:]:
                a.bonds.append(string.atoi(b))
            return True
        def __str__(self):
            if hasattr(self, "_str"): return self._str
            a = self._owner.atoms[self._index]
            return a._mmpstr % (int(a.x * 1000),
                                int(a.y * 1000),
                                int(a.z * 1000))
    def __init__(self):
        self.atoms = [ ]
        self.lines = [ ]
    def clone(self):
        other = MmpFile()
        other.lines = self.lines[:]
        other.atoms = [ ]
        for a in self.atoms:
            other.atoms.append(a.clone())
        return other
    def getAtom(self, i):
        return self.atoms[i]
    def __getitem__(self, i):
        a = self.atoms[i]
        return (a.x, a.y, a.z)
    def __setitem__(self, i, xyz):
        a = self.atoms[i]
        a.x, a.y, a.z = xyz
    def __len__(self):
        return len(self.atoms)
    def read(self, filename):
        inf = open(filename)
        self.readstring(inf.read())
        inf.close()
    def readstring(self, lines):
        lines = lines.split("\n")
        i, n = 0, len(lines)
        while i < n:
            line = lines[i]
            m = _MmpAtomPattern.match(line)
            if m == None:
                self.lines.append(line)
            else:
                rest = line[m.span()[1]:]  # anything after position
                atm = MmpFile._AtomHolder(self, m, rest)
                self.lines.append(atm)
                line = lines[i+1]
                if line.startswith("info atom"):
                    self.lines.append(line)
                    i += 1
                elif atm.mmpBonds(line):
                    self.lines.append(line)
                    i += 1
            i += 1
    def write(self, outf=None):
        if outf == None:
            outf = sys.stdout
        for ln in self.lines:
            outf.write(str(ln) + "\n")
    def convertToXyz(self):
        import XyzFile
        xyz = XyzFile.XyzFile()
        for a in self.atoms:
            xyz.atoms.append(a)
        return xyz
    def perturb(self):
        """WARNING: Using this method will put some atoms in the
        dangerous high-Morse-potential region.
        """
        A = 0.5   # some small number of angstroms
        A = A / (3 ** .5)   # amount in one dimension
        for i in range(len(self)):
            x, y, z = self[i]
            x += random.normalvariate(0.0, A)
            y += random.normalvariate(0.0, A)
            z += random.normalvariate(0.0, A)
            self[i] = (x, y, z)

def simplifiedMMP(mmp_in, mmp_out):
    # translate from a complete MMP file to one the simulator can
    # understand
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
        # we are either at the start of a group, or something that's
        # not a group
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

class LengthAngleComparison:
    def __init__(self, mmpFilename):
        self.bondLengthTerms = bondLengthTerms = { }
        self.bondAngleTerms = bondAngleTerms = { }

        def addBondLength(atm1, atm2):
            if atm1 == atm2:
                raise AssertionError("bond from atom to itself?")
            if atm2 < atm1:
                atm1, atm2 = atm2, atm1
            if bondLengthTerms.has_key(atm1):
                if atm2 not in bondLengthTerms[atm1]:
                    bondLengthTerms[atm1].append(atm2)
            else:
                bondLengthTerms[atm1] = [ atm2 ]

        def getBonds(atm1):
            lst = [ ]
            if bondLengthTerms.has_key(atm1):
                for x in bondLengthTerms[atm1]:
                    lst.append(x)
            for key in bondLengthTerms.keys():
                if atm1 in bondLengthTerms[key]:
                    if key not in lst:
                        lst.append(key)
            lst.sort()
            return lst

        def addBondAngle(atm1, atm2, atm3):
            if atm1 == atm3:
                return
            if atm3 < atm1:
                atm1, atm3 = atm3, atm1
            value = (atm2, atm3)
            if bondAngleTerms.has_key(atm1):
                if value not in bondAngleTerms[atm1]:
                    bondAngleTerms[atm1].append(value)
            else:
                bondAngleTerms[atm1] = [ value ]

        self.mmp = mmp = MmpFile()
        mmp.read(mmpFilename)

        # store all the bonds in bondLengthTerms
        for i in range(len(mmp)):
            a = mmp.atoms[i]
            for b in a.bonds:
                addBondLength(i, b - 1)

        # generate angles from chains of two bonds
        for first in range(len(mmp)):
            for second in getBonds(first):
                for third in getBonds(second):
                    addBondAngle(first, second, third)

        self.numAtoms = len(mmp)

    class LengthMeasurement:
        def __init__(self, first, second, mmp, xyz):
            self.measure = length = measureLength(xyz, first, second)
            self.atoms = (first, second)
            # In MMP and PDB files, we count from 1, where Python list
            # elements start indexing at zero.
            e1 = _PeriodicTable[mmp.atoms[first].elem]
            e2 = _PeriodicTable[mmp.atoms[second].elem]
            self.reprstr = ("<Length %s%d %s%d %g>"
                            % (e1, first + 1, e2, second + 1, length))

        def __repr__(self):
            return self.reprstr

        def closeEnough(self, other):
            if self.__class__ != other.__class__:
                return 1e20
            if self.atoms != other.atoms:
                return 1e20
            return abs(self.measure - other.measure)

    class AngleMeasurement(LengthMeasurement):
        def __init__(self, first, second, third, mmp, xyz):
            self.measure = angle = measureAngle(xyz, first, second, third)
            self.atoms = (first, second, third)
            # In MMP and PDB files, we count from 1, where Python list
            # elements start indexing at zero.
            e1 = _PeriodicTable[mmp.atoms[first].elem]
            e2 = _PeriodicTable[mmp.atoms[second].elem]
            e3 = _PeriodicTable[mmp.atoms[third].elem]
            self.reprstr = ("<Angle %s%d %s%d %s%d %g>"
                            % (e1, first + 1, e2, second + 1,
                               e3, third + 1, angle))

    def getLAfromXYZ(self, xyz):
        if len(xyz) != self.numAtoms:
            raise WrongNumberOfAtoms, \
                  "%d, expected %d" % (len(xyz), self.numAtoms)

        lengthList = [ ]
        for first in self.bondLengthTerms.keys():
            for second in self.bondLengthTerms[first]:
                lengthList.append(self.LengthMeasurement(first, second,
                                                         self.mmp, xyz))
        angleList = [ ]
        for first in self.bondAngleTerms.keys():
            for second, third in self.bondAngleTerms[first]:
                angleList.append(self.AngleMeasurement(first, second, third,
                                                       self.mmp, xyz))

        return (lengthList, angleList)

    def compare(self, questionableXyz, knownGoodXyzFile,
                lengthTolerance, angleTolerance):
        todo("handle multiple-frame xyz files from animations")
        xyz = XyzFile()
        if type(questionableXyz) == types.StringType:
            xyz.read(questionableXyz)
        elif type(questionableXyz) == types.ListType:
            xyz.readFromList(questionableXyz)
        else:
            raise Exception, type(questionableXyz)
        L1, A1 = self.getLAfromXYZ(xyz)
        xyz = XyzFile()
        xyz.read(knownGoodXyzFile)
        L2, A2 = self.getLAfromXYZ(xyz)
        mismatches=""
        maxangle=0
        maxlen=0
        for len1, len2 in map(None, L1, L2):
            diff = len1.closeEnough(len2)
            if diff > lengthTolerance:
                mismatches += "got      %s\nexpected %s diff %f\n" %(repr(len1), repr(len2), diff)
                if diff > maxlen:
                    maxlen = diff
        for ang1, ang2 in map(None, A1, A2):
            diff = ang1.closeEnough(ang2)
            if diff > angleTolerance:
                mismatches += "got      %s\nexpected %s diff %f\n" %(repr(ang1), repr(ang2), diff)
                if diff > maxangle:
                    maxangle = diff

        if mismatches:
            if maxlen > 0:
                mismatches += "max length difference: %f > %f\n" %(maxlen, lengthTolerance)
            if maxangle > 0:
                mismatches += "max angle  difference: %f > %f\n" %(maxangle, angleTolerance)
            raise LengthAngleMismatch("\n" + mismatches)

##################################################################

class EarlyTermination(Exception):
    pass

def rmtreeSafe(dir):
    # platform-independent 'rm -rf'
    try: shutil.rmtree(dir)
    except OSError, e: pass

lastRecordedTime = testStartTime = time.time()

class TimedTest:

    def start(self):
        global testsSkipped
        if (not TIME_ONLY and not GENERATE and
            time.time() > testStartTime + TIME_LIMIT):
            testsSkipped += 1
            raise EarlyTermination

    def finish(self):
        if TIME_ONLY:
            global testTimes, lastRecordedTime
            previous = lastRecordedTime
            lastRecordedTime = t = time.time()
            testTimes[self.methodname] = t - previous
            raise EarlyTermination

class SandboxTest(TimedTest):
    DEFAULT_INPUTS = ( )  # in addition to xxx.mmp
    DEFAULT_SIMOPTS = ( )
    DEFAULT_OUTPUTS = ( )  # in addition to stdout, stderr

    def md5sum(self, filename):
        hash = md5.new()
        inf = open(filename)
        for line in open(filename).readlines():
            try:
                line.index("Date and Time")
                pass
            except ValueError:
                hash.update(line)
        inf.close()
        def hex2(ch):
            return "%02X" % ord(ch)
        return "".join(map(hex2, hash.digest()))

    class MD5SumMismatch(AssertionError):
        pass

    def __init__(self, dir=None, test=None,
                 simopts=None, inputs=None, outputs=None,
                 expectedExitStatus=0):

        global Tests

        self.dirname = dir  # rigid_organics
        self.shortname = test  # C2H4
        self.testname = testname = "test_" + test # test_C2H4
        # midname = tests/rigid_organics/test_C2H4
        self.midname = midname = os.path.join("tests", dir, testname)
        # methodname = test_rigid_organics_C2H4
        self.methodname = methodname = "_".join(["test", dir, test])
        # basename = .../sim/src/tests/rigid_organics/test_C2H4
        self.basename = os.path.join(os.getcwd(), midname)
        self.expectedExitStatus = expectedExitStatus

        try:
            TimedTest.start(self)
        except EarlyTermination:
            return

        if inputs == None:
            inputs = self.DEFAULT_INPUTS
        if simopts == None:
            simopts = self.DEFAULT_SIMOPTS
        if outputs == None:
            outputs = self.DEFAULT_OUTPUTS
        self.inputs = inputs
        self.simopts = simopts
        self.outputs = outputs
        if LIST_EVERYTHING:
            print
            print dir, testname
        self.runInSandbox()

    def runInSandbox(self):
        # Run the simulator in sim/src/tmp.
        here = os.getcwd()
        tmpdir = "tmp_" + self.dirname + "_" + self.shortname
        try:
            rmtreeSafe(tmpdir)
            os.mkdir(tmpdir)
            # Copy the input files into the tmp directory.
            shutil.copy(simulatorCmd, tmpdir)
            # We always have a .mmp file
            shutil.copy(self.basename + ".mmp", tmpdir)
            if not GENERATE:
                for ext in self.inputs:
                    shutil.copy(self.basename + "." + ext, tmpdir)
            # Go into the tmp directory and run the simulator.
            os.chdir(tmpdir)
            exitStatus = self.runCommand(self.simopts)
            if self.expectedExitStatus != None:
                if exitStatus != self.expectedExitStatus:
                    inf = open("stderr")
                    sys.stderr.write(inf.read())
                    inf.close()
                    str = ("simulator exit status was %d, expected %d" %
                           (exitStatus, self.expectedExitStatus))
                    raise AssertionError(str)
            if GENERATE:
                self.generateOutputFiles()
            else:
                if DEBUG > 0:
                    print os.listdir(".")
                if DEBUG > 2:
                    print ("******** " + self.basename + " ********")
                    for f in os.listdir("."):
                        if f != simulatorCmd:
                            # assume everything else is a text file
                            print "---- " + f + " ----"
                            sys.stdout.write(open(f).read())
                try:
                    self.finish()
                except EarlyTermination:
                    return
                self.checkOutputFiles()
            return
        finally:
            os.chdir(here)
            if not KEEP_RESULTS:
                rmtreeSafe(tmpdir)

    def runCommandQt(self, opts):
        import qt
        def substFOO(str):
            if str.startswith("FOO"):
                return self.testname + str[3:]
            return str
        cmdline = [ "./" + simulatorCmd ] + map(substFOO, opts)
        if DEBUG > 0:
            print self.basename
            print cmdline
        simProcess = qt.QProcess()
        stdout = open("stdout", "a")
        stderr = open("stderr", "a")
        def blabout():
            r = str(simProcess.readStdout())
            if DEBUG > 1:
                print "STDOUT", r
            stdout.write(str(simProcess.readStdout()))
        def blaberr():
            r = str(simProcess.readStderr())
            if DEBUG > 1:
                print "STDERR", r
            stderr.write(str(simProcess.readStderr()))
        qt.QObject.connect(simProcess, qt.SIGNAL("readyReadStdout()"), blabout)
        qt.QObject.connect(simProcess, qt.SIGNAL("readyReadStderr()"), blaberr)
        args = qt.QStringList()
        for arg in cmdline:
            args.append(arg)
        simProcess.setArguments(args)
        simProcess.start()
        while simProcess.isRunning():
            time.sleep(0.1)
        stdout.close()
        stderr.close()
        return simProcess.exitStatus()

    def runCommandSubprocess(self, opts):
        import subprocess
        def substFOO(str):
            if str.startswith("FOO"):
                return self.testname + str[3:]
            return str
        cmdline = [ "./" + simulatorCmd ] + map(substFOO, opts)
        stdout = open("stdout", "w")
        stderr = open("stderr", "w")
        p = subprocess.Popen(cmdline)
        r = p.wait()
        stdout.close()
        stderr.close()
        return r

    def runCommand(self, opts):
        usingQt = True
        try:
            import qt
        except ImportError:
            usingQt = False
        if usingQt:
            return self.runCommandQt(opts)
        else:
            return self.runCommandSubprocess(opts)

    def checkOutputFiles(self):
        if MD5_CHECKS:
            self.checkMd5Sums()
        else:
            if "xyzcmp" in self.inputs:
                if STRUCTURE_COMPARISON_TYPE == STRUCTCOMPARE_C_TEST:
                    if self.runCommand(("--base-file", "FOO.xyzcmp",
                                        "FOO.xyz")) != 0:
                        raise AssertionError("bad structure match")
                else:
                    self.structureComparisonBondlengthsBondangles()
            todo("anything else we should be checking here?")

    # Generate MD5 checksums for all output files, store in
    # tests/rigid_organics/test_C4H8.md5sums (for example)
    def generateOutputFiles(self):
        outf = open(self.basename + ".md5sums", "w")
        outf.write("stdout %s\n" % self.md5sum("stdout"))
        outf.write("stderr %s\n" % self.md5sum("stderr"))
        for ext in self.outputs:
            fname = self.testname + "." + ext
            outf.write("%s %s\n" % (fname, self.md5sum(fname)))
        outf.close()

    def checkMd5Sums(self):
        inf = open(self.basename + ".md5sums")
        for line in inf.readlines():
            fname, sum = line.split()
            realsum = self.md5sum(fname)
            if realsum != sum:
                raise self.MD5SumMismatch(self.midname + " " + fname)
        inf.close()

    def structureComparisonBondlengthsBondangles(self, lengthtol=None, angletol=None):
        if lengthtol == None: lengthtol = LENGTH_TOLERANCE
        if angletol == None: angletol = ANGLE_TOLERANCE
        todo("handle multiple-frame xyz files from animations")
        lac = LengthAngleComparison(self.testname + ".mmp")
        lac.compare(self.testname + ".xyz", self.testname + ".xyzcmp",
                    lengthtol, angletol)

#########################################

class TraceFile:
    def __init__(self, filename):
        f = open(filename)
        lines = [ ]
        for L in f.readlines():
            lines.append(L.rstrip())
        f.close()
        description = ""
        Ncolumns = re.compile('^(\d+) columns')
        i = 0
        self.columnNames = [ ]
        while True:
            if lines[i][:1] != '#':
                break
            line = lines[i][2:]
            description += line + '\n'
            if   line.startswith('uname -a: '):
                self.platform = line[10:]
            elif line.startswith('CFLAGS: '):
                self.cflags = line[8:]
            elif line.startswith('LDFLAGS: '):
                self.ldflags = line[9:]
            elif line.startswith('Command Line: '):
                self.commandLine = line[14:]
            elif line.startswith('Date and Time: '):
                self.dateAndTime = line[15:]
            elif line.startswith('Input File: '):
                self.inputFile = line[12:]
            elif line.startswith('Output File: '):
                self.outputFile = line[13:]
            elif line.startswith('Trace File: '):
                self.traceFile = line[12:]
            elif line.startswith('Number of Frames: '):
                self.numFrames = string.atoi(line[18:])
            elif line.startswith('Steps per Frame: '):
                self.stepsPerFrame = string.atoi(line[17:])
            elif line.startswith('Temperature: '):
                self.temperature = string.atof(line[13:])
            elif line.startswith('Number of Atoms: '):
                self.numAtoms = string.atoi(line[17:])
            else:
                m = Ncolumns.search(line)
                if m != None:
                    N = string.atoi(m.group(1))
                    for j in range(N):
                        self.columnNames.append(lines[i][2:])
                        i += 1
                    while i < len(lines) and lines[i][:1] == '#':
                        i += 1
                    break
            i += 1
        self.data = data = [ ]
        while i < len(lines) and lines[i][:1] != '#':
            data.append(map(string.atof,
                            lines[i].split()))
            i += 1

    def fuzzyMatch(self, other):
        def substr(haystack, needle):
            try: haystack.index(needle)
            except ValueError: return False
            return True
        assert self.columnNames == other.columnNames, "different column names"
        assert len(self.data) == len(other.data), "wrong number of data lines"
        tests = [ ]
        for name in self.columnNames:
            # here we can customize tests by the types of jigs
            if name.startswith('Thermo'):
                # ignore thermometers, they are way too noisy
                def alwaysPass(x, y):
                    assert x == x, "not-a-number values in reference results"
                    assert y == y, "not-a-number values in test results"
                tests.append(alwaysPass)
            elif name.startswith('Rotary Motor') and substr(name, "speed"):
                # rotary motor speeds seem to get a lot of variation
                def checkSpeed(x, y, name=name):
                    assert x == x, "not-a-number values in reference results"
                    assert y == y, "not-a-number values in test results"
                    xdif = abs(x - y)
                    assert xdif < 10.0 or (xdif / abs(x)) < 0.2, \
                           ("%s: expected %g, got %g" % (name, x, y))
                tests.append(checkSpeed)
            elif name.startswith('Angle'):
                # angles seem to get a lot of variation
                def checkAngle(x, y, name=name):
                    assert x == x, "not-a-number values in reference results"
                    assert y == y, "not-a-number values in test results"
                    xdif = abs(x - y)
                    assert xdif < 10.0 or (xdif / abs(x)) < 0.2, \
                           ("%s: expected %g, got %g" % (name, x, y))
                tests.append(checkAngle)
            elif name.startswith('Dihedral'):
                # dihedral angles vary a lot, and they flip sign if they
                # pass through 180 or -180
                def checkDihedral(x, y, name=name):
                    assert x == x, "not-a-number values in reference results"
                    assert y == y, "not-a-number values in test results"
                    # handle sign flips when angles jump -180 <-> +180
                    xdif = min(abs(x - y),
                               min(abs(x + 360 - y), abs(x - y - 360)))
                    assert xdif < 50.0 or (xdif / abs(x)) < 0.4, \
                           ("%s: expected %g, got %g" % (name, x, y))
                tests.append(checkDihedral)
            else:
                def check(x, y, name=name):
                    assert x == x, "not-a-number values in reference results"
                    assert y == y, "not-a-number values in test results"
                    xdif = abs(x - y)
                    assert xdif < 1.0 or (xdif / abs(x)) < 0.1, \
                           ("%s: expected %g, got %g" % (name, x, y))
                tests.append(check)
        n = len(self.columnNames)
        for d1, d2 in map(None, self.data, other.data):
            for i in range(n):
                tests[i](d1[i], d2[i])

#########################################

class NullTest(SandboxTest):
    def runInSandbox(self):
        global testTimes
        testTimes[self.methodname] = 0.0

class FailureExpectedTest(NullTest):
    """By default, the input for this kind of test is a MMP file,
    the command line is given explicitly in the test methods, and the
    outputs are stdout, stderr, and the exit value. We expect a failure
    here but I'm not sure exactly what kind of failure.

    Until I know exactly what kind of failure Eric wants here,
    just make it pass all the time.
    """
    DEFAULT_SIMOPTS = None  # force an explicit choice

class MinimizeTest(SandboxTest):
    """Perform a minimization, starting with a MMP file. The results
    should be stdout, stderr, exit value, and an XYZ file. All these
    are checked for correctness.
    """
    DEFAULT_SIMOPTS = ("--minimize", "--dump-as-text", "--trace-file", "FOO.trc", "FOO.mmp")
    DEFAULT_OUTPUTS = ("xyz",)

class StructureTest(MinimizeTest):
    """Perform a minimization, starting with a MMP file. The results
    should be stdout, stderr, exit value, a TRC file, and an XYZ file.
    All these are checked for correctness. The XYZ file can be
    compared to an XYZCMP file for closeness of fit.
    """
    DEFAULT_INPUTS = ("xyzcmp",)
    DEFAULT_SIMOPTS = ("--minimize", "--dump-as-text", "--trace-file", "FOO.trc", "FOO.mmp")
    DEFAULT_OUTPUTS = ( )

class DynamicsTest(MinimizeTest):
    """Make a dynamics movie, starting with a MMP file. The results
    should be stdout, stderr, exit value, a TRC file, and an XYZ file
    with multiple frames. All these are checked for correctness.
    """
    DEFAULT_INPUTS = ( )
    DEFAULT_SIMOPTS = ("--dump-as-text", "--trace-file", "FOO.trc", "FOO.mmp")
    DEFAULT_OUTPUTS = ("trc", "xyz")

class PyrexTest(TimedTest):

    def __init__(self, methodname, base=None):
        self.methodname = methodname
        self.base = base
        try:
            self.start()
        except EarlyTermination:
            return
        self.run()
        try:
            self.finish()
        except EarlyTermination:
            pass

    def run(self):
        lac = LengthAngleComparison(self.base + ".mmp")
        import sim
        s = sim.theSimulator()
        s.reinitGlobals()
        inputfile = self.base + ".mmp"
        outputfile = self.base + ".xyz"
        s.InputFileName = inputfile
        s.OutputFileName = outputfile
        s.ToMinimize = 1
        s.DumpAsText = 1
        s.OutputFormat = 0
        s.Temperature = 300
        s.go(frame_callback=None, trace_callback=None)
        lac.compare(self.base + ".xyz", self.base + ".xyzcmp",
                    LENGTH_TOLERANCE, ANGLE_TOLERANCE)


class JigTest(SandboxTest):

    DEFAULT_INPUTS = ("trc", "xyzcmp")
    DEFAULT_SIMOPTS = ("-i100", "-f1", "--dump-as-text", "--trace-file", "FOO.trc", "FOO.mmp")
    DEFAULT_OUTPUTS = ("trc", "xyz")

    def generateOutputFiles(self):
        shutil.copy(self.testname + ".trc", self.basename + ".trc")
        shutil.copy(self.testname + ".xyz", self.basename + ".xyzcmp")

    def runInSandbox(self):
        if GENERATE:
            # If the simplified MMP doesn't already exist, generate it now
            mmpfile = self.midname + ".mmp"
            if not os.path.exists(mmpfile):
                mmp_orig = os.path.join("tests", self.dirname, self.shortname + ".mmp")
                simplifiedMMP(mmp_orig, mmpfile)
        SandboxTest.runInSandbox(self)

    def checkOutputFiles(self):
        # Given a trace file with several frames, and columns for various
        # jigs, make sure the jigs all have roughly the same numbers as they
        # had during a known-good run.
        def lastLineOfReadings(f):
            lines = readlines(f)
            n = None
            for i in range(len(lines)):
                if lines[i].startswith("# Done:"):
                    n = i - 1
                    break
            if n == None: return None
            return map(string.atof, lines[n].split())
        # add the following line to regenerate trace files when they fail to match?
        # shutil.copy(self.testname + ".trc", self.basename + ".trcnew")
        goodT = TraceFile(self.basename + ".trc")
        iffyT = TraceFile(self.testname + ".trc")
        goodT.fuzzyMatch(iffyT)
        # loosen up angles a little extra
        self.structureComparisonBondlengthsBondangles(LENGTH_TOLERANCE,
                                                      1.5 * ANGLE_TOLERANCE)

####################################################

# Re-generate this with "python tests.py time_only"
RANKED_BY_RUNTIME = [
    'test_dynamics_0001',
    'test_minimize_0002',
    'test_minimize_0003',
    'test_minimize_0004',
    'test_minimize_0006',
    'test_minimize_0007',
    'test_badCallback3',
    'test_framecallback',
    'test_badCallback1',
    'test_pyrex_minH2',
    'test_badCallback2',
    'test_minimize_h2',
    'test_temperature_tests_003_thermostat_test_3',
    'test_singlebond_stretch_H_SH',
    'test_singlebond_stretch_F_NH2',
    'test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_7',
    'test_singlebond_stretch_H_H',
    'test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_6',
    'test_rigid_organics_CH4',
    'test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_1',
    'test_singlebond_stretch_Cl_F',
    'test_reordering_jigs_or_chunks_03_thermo_anchor_reordering',
    'test_enabled_disabled_jigs_003_one_thermometer_enabled_other_disabled',
    'test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_8',
    'test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_5',
    'test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_2',
    'test_singlebond_stretch_H_Cl',
    'test_temperature_tests_003_thermostat_test_5',
    'test_singlebond_stretch_Cl_OH',
    'test_singlebond_stretch_H_NH2',
    'test_singlebond_stretch_F_SH',
    'test_singlebond_stretch_F_PH2',
    'test_minimize_0013',
    'test_singlebond_stretch_H_PH2',
    'test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_1',
    'test_motors_009_linearmotor_Methane_Molecule',
    'test_singlebond_stretch_Cl_CH3',
    'test_singlebond_stretch_HS_OH',
    'test_enabled_disabled_jigs_001_disabled_anchors',
    'test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_3',
    'test_temperature_tests_003_thermostat_test_4',
    'test_singlebond_stretch_Cl_PH2',
    'test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_2',
    'test_temperature_tests_003_thermostat_test_2',
    'test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_4',
    'test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_5',
    'test_singlebond_stretch_Cl_NH2',
    'test_singlebond_stretch_H_CH3',
    'test_singlebond_stretch_F_SiH3',
    'test_singlebond_stretch_Cl_AlH2',
    'test_enabled_disabled_jigs_004_one_thermostat_enabled_other_disabled',
    'test_singlebond_stretch_Cl_SH',
    'test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_4',
    'test_temperature_tests_003_thermostat_test_1',
    'test_singlebond_stretch_H_SiH3',
    'test_singlebond_stretch_HS_NH2',
    'test_singlebond_stretch_H_F',
    'test_singlebond_stretch_HS_SH',
    'test_singlebond_stretch_H_OH',
    'test_floppy_organics_CH4',
    'test_singlebond_stretch_F_CH3',
    'test_singlebond_stretch_F_OH',
    'test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_3',
    'test_singlebond_stretch_F_AlH2',
    'test_singlebond_stretch_Cl_Cl',
    'test_singlebond_stretch_HO_AlH2',
    'test_singlebond_stretch_F_F',
    'test_singlebond_stretch_Cl_SiH3',
    'test_singlebond_stretch_H2N_PH2',
    'test_singlebond_stretch_H3C_CH3',
    'test_temperature_tests_003_thermostat_test',
    'test_singlebond_stretch_HS_PH2',
    'test_singlebond_stretch_H2P_CH3',
    'test_singlebond_stretch_H2P_PH2',
    'test_singlebond_stretch_H2P_AlH2',
    'test_temperature_tests_002_two_methanes_10A_apart_vdw_6',
    'test_singlebond_stretch_H2Al_SiH3',
    'test_singlebond_stretch_HS_AlH2',
    'test_singlebond_stretch_HS_CH3',
    'test_singlebond_stretch_F_BH2',
    'test_singlebond_stretch_HO_PH2',
    'test_singlebond_stretch_H3C_SiH3',
    'test_singlebond_stretch_H_BH2',
    'test_singlebond_stretch_H2P_SiH3',
    'test_singlebond_stretch_H3Si_SiH3',
    'test_singlebond_stretch_H_AlH2',
    'test_singlebond_stretch_HO_SiH3',
    'test_singlebond_stretch_Cl_BH2',
    'test_singlebond_stretch_H2N_AlH2',
    'test_motors_014_rotarymotor_negative_torque_and_negative_speed',
    'test_motors_013_rotarymotor_0_torque_and_positive_speed',
    'test_singlebond_stretch_H2Al_AlH2',
    'test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_5',
    'test_enabled_disabled_jigs_002_one_anchor_enabled_other_disabled',
    'test_motors_018_rotarymotor_positive_torque_and_0_speed',
    'test_singlebond_stretch_H2B_BH2',
    'test_enabled_disabled_jigs_005_disabled_measure_distance_jig',
    'test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_4',
    'test_enabled_disabled_jigs_007_one_linearmotor_enabled_and_other_disabled',
    'test_motors_025_two_linearmotors_applying_equal_forces_normal_to_each_other',
    'test_motors_028_bug1306_test2',
    'test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_2',
    'test_heteroatom_organics_C3H6O',
    'test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_6',
    'test_motors_019_rotarymotor_medium_torque_and_speed',
    'test_motors_011_rotarymotor_0_torque_and_0_speed',
    'test_temperature_tests_001_two_methanes_9A_apart_vdw_5',
    'test_motors_015_rotarymotor_negative_torque_and_positive_speed',
    'test_enabled_disabled_jigs_006_one_rotarymotor_enabled_and_other_disabled',
    'test_motors_012_rotarymotor_0_torque_and_negative_speed',
    'test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_1',
    'test_motors_and_anchors_005_rotorymotor_against_anchor_3',
    'test_singlebond_stretch_H2N_SiH3',
    'test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_7',
    'test_singlebond_stretch_H2B_SiH3',
    'test_heteroatom_organics_C3H6NH',
    'test_singlebond_stretch_H2B_CH3',
    'test_singlebond_stretch_HO_CH3',
    'test_motors_020_rotarymotor_high_torque_and_speed',
    'test_motors_016_rotarymotor_negative_torque_and_0_speed',
    'test_singlebond_stretch_H2B_AlH2',
    'test_motors_017_rotarymotor_positive_torque_and_negative_speed',
    'test_rigid_organics_C3H6',
    'test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_8',
    'test_minimize_0010',
    'test_heteroatom_organics_CH3OH',
    'test_heteroatom_organics_C3H6S',
    'test_motors_026_two_linearmotors_applying_equal_and_opposite_forces',
    'test_floppy_organics_C2H6',
    'test_singlebond_stretch_H2Al_CH3',
    'test_heteroatom_organics_C3H6BH',
    'test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_4',
    'test_heteroatom_organics_C3H6PH',
    'test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_7',
    'test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_8',
    'test_heteroatom_organics_CH3AlH2',
    'test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_4',
    'test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_3',
    'test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_2',
    'test_motors_030_rotarymotor_and_linear_motor_attached_to_same_atoms',
    'test_floppy_organics_C4H8',
    'test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_6',
    'test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_1',
    'test_singlebond_stretch_HO_NH2',
    'test_heteroatom_organics_CH3BH2',
    'test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_6',
    'test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_2',
    'test_motors_003_linearmotor_0_force_and_positive_stiffness',
    'test_rigid_organics_C8H8',
    'test_motors_004_linearmotor_negative_force_and_negative_stiffness',
    'test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_3',
    'test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_8',
    'test_motors_006_linearmotor_negative_force_and_0_stiffness',
    'test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_1',
    'test_singlebond_stretch_H2B_PH2',
    'test_motors_007_linearmotor_positive_force_and_0_stiffness',
    'test_frameAndTraceCallback',
    'test_minimize_0009',
    'test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_3',
    'test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_7',
    'test_motors_001_linearmotor_0_force_and_0_stiffness',
    'test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_5',
    'test_heteroatom_organics_C3H6SiH2',
    'test_heteroatom_organics_CH3OCH3',
    'test_motors_021_rotarymotor_dyno_jig_test_to_same_chunk',
    'test_rigid_organics_C4H8',
    'test_singlebond_stretch_HO_OH',
    'test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_5',
    'test_motors_023_rotarymotor_two_planet_gears',
    'test_motors_002_linearmotor_0_force_and_negative_stiffness',
    'test_motors_and_anchors_003_rotorymotor_against_anchor_1',
    'test_floppy_organics_C6H12b',
    'test_jigs_to_several_atoms_003_linearmotor_to_50_atoms',
    'test_heteroatom_organics_ADAMframe_O_Cs',
    'test_amino_acids_tyr_l_aminoacid',
    'test_heteroatom_organics_ADAMframe_S_Cs',
    'test_heteroatom_organics_ADAMframe_PH_Cs',
    'test_heteroatom_organics_ADAM_Cl_c3v',
    'test_rigid_organics_C10H12',
    'test_motors_and_anchors_004_rotorymotor_against_anchor_2',
    'test_floppy_organics_C4H10c',
    'test_rigid_organics_C10H14',
    'test_heteroatom_organics_C5H10PH',
    'test_heteroatom_organics_CH3SH',
    'test_motors_024_linearmotor_two_dodecahedranes',
    'test_heteroatom_organics_CH3AlHCH3',
    'test_heteroatom_organics_B_ADAM_C3v',
    'test_heteroatom_organics_C5H10O',
    'test_motors_and_anchors_002_linearmotor_pulling_against_anchor_2',
    'test_heteroatom_organics_ADAMframe_SiH2_c2v',
    'test_motors_027_two_rotarymotors_applying_equal_and_opposite_torque',
    'test_heteroatom_organics_CH3NH2',
    'test_heteroatom_organics_C5H10S',
    'test_motors_and_anchors_001_linearmotor_pulling_against_anchor_1',
    'test_floppy_organics_C6H12a',
    'test_rigid_organics_C2H6',
    'test_heteroatom_organics_ADAMframe_BH_Cs',
    'test_heteroatom_organics_SiH_ADAM_C3v',
    'test_rigid_organics_C3H8',
    'test_heteroatom_organics_ADAM_SH_Cs',
    'test_dpbFileShouldBeBinary',
    'test_pyrex_dynamics',
    'test_heteroatom_organics_ADAMframe_NH_Cs',
    'test_motors_008_linearmotor_positive_force_and_positive_stiffness',
    'test_traceCallbackWithMotor',
    'test_heteroatom_organics_ADAM_F_c3v',
    'test_heteroatom_organics_C4H8S',
    'test_singlebond_stretch_H2N_NH2',
    'test_heteroatom_organics_CH3PHCH3',
    'test_heteroatom_organics_P_ADAM_C3v',
    'test_singlebond_stretch_HO_BH2',
    'test_heteroatom_organics_C4H8AlH',
    'test_heteroatom_organics_C5H10NH',
    'test_jigs_to_several_atoms_006_anchors_to_100_atoms',
    'test_motors_005_linearmotor_negative_force_and_positive_stiffness',
    'test_heteroatom_organics_Al_ADAM_C3v',
    'test_heteroatom_organics_ADAMframe_AlH_Cs',
    'test_minimize_0012',
    'test_jigs_to_several_atoms_004_linearmotor_to_100_atoms',
    'test_jigs_to_several_atoms_005_anchors_to_50_atoms',
    'test_floppy_organics_C7H14c',
    'test_singlebond_stretch_H2N_CH3',
    'test_jigs_to_several_atoms_001_rotarymotor_to_50_atoms',
    'test_heteroatom_organics_C_CH3_3_SiH3',
    'test_heteroatom_organics_C3H6AlH',
    'test_motors_010_linearmotor_box_of_helium',
    'test_heteroatom_organics_CH3PH2',
    'test_pyrex_minimize0001',
    'test_heteroatom_organics_N_ADAM_C3v',
    'test_motors_029_bug_1331',
    'test_rigid_organics_C14H20',
    'test_floppy_organics_C4H10a',
    'test_heteroatom_organics_C4H8NH',
    'test_floppy_organics_C3H8',
    'test_heteroatom_organics_C4H8BH',
    'test_rigid_organics_C6H10',
    'test_minimize_0011',
    'test_minimize_0005',
    'test_singlebond_stretch_HS_SiH3',
    'test_heteroatom_organics_CH3SiH2CH3',
    'test_floppy_organics_C5H12b',
    'test_heteroatom_organics_C_CH3_3_SH',
    'test_heteroatom_organics_C_CH3_3_OH',
    'test_minimize_0001',
    'test_heteroatom_organics_C5H10SiH2',
    'test_heteroatom_organics_C4H8SiH2',
    'test_singlebond_stretch_HS_BH2',
    'test_heteroatom_organics_ADAM_BH2',
    'test_heteroatom_organics_C5H10AlH',
    'test_heteroatom_organics_C_CH3_3_BH2',
    'test_heteroatom_organics_CH3SiH3',
    'test_heteroatom_organics_CH3NHCH3',
    'test_heteroatom_organics_ADAM_OH_Cs',
    'test_heteroatom_organics_C_CH3_3_NH2',
    'test_heteroatom_organics_C4H8PH',
    'test_floppy_organics_C7H14a',
    'test_rigid_organics_C8H14',
    'test_floppy_organics_C5H12d',
    'test_heteroatom_organics_C_CH3_3_PH2',
    'test_heteroatom_organics_ADAM_AlH2_Cs',
    'test_jigs_to_several_atoms_007_rotarymotor_and_anchors_to_100_atoms',
    'test_jigs_to_several_atoms_002_rotarymotor_to_100_atoms',
    'test_heteroatom_organics_ADAM_PH2_Cs',
    'test_heteroatom_organics_ADAM_NH2_Cs',
    'test_heteroatom_organics_CH3SCH3',
    'test_floppy_organics_C5H10',
    'test_floppy_organics_C5H12e',
    'test_singlebond_stretch_H2B_NH2',
    'test_heteroatom_organics_C4H8O',
    'test_motors_022_rotary_motor_small_bearing_test',
    'test_amino_acids_ala_l_aminoacid',
    'test_heteroatom_organics_C5H10BH',
    'test_floppy_organics_C6H14a',
    'test_floppy_organics_C6H14c',
    'test_minimize_0008',
    'test_heteroatom_organics_CH3BHCH3',
    'test_floppy_organics_C7H14b',
    'test_amino_acids_asp_l_aminoacid',
    'test_floppy_organics_C6H14b',
    'test_floppy_organics_C5H12c',
    'test_floppy_organics_C5H12a',
    'test_floppy_organics_C6H14d',
    'test_floppy_organics_C6H14e',
    'test_floppy_organics_C4H10b',
    'test_heteroatom_organics_C_CH3_3_AlH2',
    'test_rigid_organics_C14H24',
    'test_amino_acids_ser_l_aminoacid',
    'test_amino_acids_pro_l_aminoacid',
    'test_heteroatom_organics_ADAM_SiH3_C3v',
    'test_amino_acids_ile_l_aminoacid',
    'test_amino_acids_cys_l_aminoacid',
    'test_floppy_organics_C6H14f',
    'test_amino_acids_thr_l_aminoacid',
    'test_amino_acids_glu_l_aminoacid',
    'test_amino_acids_val_l_aminoacid',
    'test_amino_acids_asn_l_aminoacid',
    'test_amino_acids_gly_l_aminoacid',
    'test_amino_acids_his_l_aminoacid',
    'test_amino_acids_met_l_aminoacid',
    'test_amino_acids_arg_l_aminoacid',
    'test_dynamics_small_bearing_01',
    'test_amino_acids_gln_l_aminoacid',
    'test_amino_acids_lys_l_aminoacid',
    'test_amino_acids_leu_l_aminoacid',
    'test_amino_acids_phe_l_aminoacid'
    ]

try:
    import sim
    class PyrexUnitTests(sim.Tests, TimedTest):

        def test_framecallback(self):
            self.methodname = "test_framecallback"
            try: TimedTest.start(self)
            except EarlyTermination: return
            try:
                sim.Tests.test_framecallback(self)
            finally:
                try: TimedTest.finish(self)
                except EarlyTermination: pass
        def test_frameAndTraceCallback(self):
            self.methodname = "test_frameAndTraceCallback"
            try: TimedTest.start(self)
            except EarlyTermination: return
            try:
                sim.Tests.test_frameAndTraceCallback(self)
            finally:
                try: TimedTest.finish(self)
                except EarlyTermination: pass
        def test_traceCallbackWithMotor(self):
            self.methodname = "test_traceCallbackWithMotor"
            try: TimedTest.start(self)
            except EarlyTermination: return
            try:
                sim.Tests.test_traceCallbackWithMotor(self)
            finally:
                try: TimedTest.finish(self)
                except EarlyTermination: pass
        def test_dpbFileShouldBeBinary(self):
            self.methodname = "test_dpbFileShouldBeBinary"
            try: TimedTest.start(self)
            except EarlyTermination: return
            try:
                sim.Tests.test_dpbFileShouldBeBinary(self)
            finally:
                try: TimedTest.finish(self)
                except EarlyTermination: pass
        def test_badCallback1(self):
            self.methodname = "test_badCallback1"
            try: TimedTest.start(self)
            except EarlyTermination: return
            try:
                sim.Tests.test_badCallback1(self)
            finally:
                try: TimedTest.finish(self)
                except EarlyTermination: pass
        def test_badCallback2(self):
            self.methodname = "test_badCallback2"
            try: TimedTest.start(self)
            except EarlyTermination: return
            try:
                sim.Tests.test_badCallback2(self)
            finally:
                try: TimedTest.finish(self)
                except EarlyTermination: pass
        def test_badCallback3(self):
            self.methodname = "test_badCallback3"
            try: TimedTest.start(self)
            except EarlyTermination: return
            try:
                sim.Tests.test_badCallback3(self)
            finally:
                try: TimedTest.finish(self)
                except EarlyTermination: pass

    baseClass = PyrexUnitTests
except ImportError:
    baseClass = unittest.TestCase


class Tests(baseClass):

    def test_minimize_h2(self):
        StructureTest(dir="minimize", test="h2")

    def test_dynamics_0001(self):
        # rotary motor test
        FailureExpectedTest(dir="dynamics", test="0001",
                            simopts=("--num-frames=30",
                                     "--temperature=0",
                                     "--iters-per-frame=10000",
                                     "--dump-as-text",
                                     "FOO.mmp"))
    #def test_dynamics_0002(self):
    #    # ground, thermostat, and thermometer test
    #    DynamicsTest(dir="dynamics", test="0002",
    #                 simopts=("--num-frames=100",
    #                          "--temperature=300",
    #                          "--iters-per-frame=10",
    #                          "--dump-as-text",
    #                          "FOO.mmp"))

    def test_dynamics_small_bearing_01(self):
        # rotary motor test
        DynamicsTest(dir="dynamics", test="small_bearing_01",
                     simopts=("--num-frames=100",
                              "--temperature=300",
                              "--iters-per-frame=10",
                              "--dump-as-text",
                              "--trace-file", "FOO.trc",
                              "FOO.mmp"))

    def test_minimize_0002(self):
        FailureExpectedTest(dir="minimize", test="0002",
                            simopts=("--num-frames=500",
                                     "--minimize",
                                     "--dump-as-text",
                                     "FOO.mmp"))
    def test_minimize_0003(self):
        FailureExpectedTest(dir="minimize", test="0003",
                            simopts=("--num-frames=300",
                                     "--minimize",
                                     "--dump-intermediate-text",
                                     "--dump-as-text",
                                     "FOO.mmp"))
    def test_minimize_0004(self):
        FailureExpectedTest(dir="minimize", test="0004",
                            simopts=("--num-frames=600",
                                     "--minimize",
                                     "--dump-as-text",
                                     "FOO.mmp"))
    def test_minimize_0006(self):
        FailureExpectedTest(dir="minimize", test="0006",
                            simopts=("--num-frames=300",
                                     "--minimize",
                                     "--dump-intermediate-text",
                                     "--dump-as-text",
                                     "FOO.mmp"))
    def test_minimize_0007(self):
        FailureExpectedTest(dir="minimize", test="0007",
                            simopts=("--num-frames=300",
                                     "--minimize",
                                     "--dump-intermediate-text",
                                     "--dump-as-text",
                                     "FOO.mmp"))

    # In Emacs, do "sort-lines" to keep things organized
    def test_amino_acids_ala_l_aminoacid(self): StructureTest(dir="amino_acids", test="ala_l_aminoacid")
    def test_amino_acids_arg_l_aminoacid(self): StructureTest(dir="amino_acids", test="arg_l_aminoacid")
    def test_amino_acids_asn_l_aminoacid(self): StructureTest(dir="amino_acids", test="asn_l_aminoacid")
    def test_amino_acids_asp_l_aminoacid(self): StructureTest(dir="amino_acids", test="asp_l_aminoacid")
    def test_amino_acids_cys_l_aminoacid(self): StructureTest(dir="amino_acids", test="cys_l_aminoacid")
    def test_amino_acids_gln_l_aminoacid(self): StructureTest(dir="amino_acids", test="gln_l_aminoacid")
    def test_amino_acids_glu_l_aminoacid(self): StructureTest(dir="amino_acids", test="glu_l_aminoacid")
    def test_amino_acids_gly_l_aminoacid(self): StructureTest(dir="amino_acids", test="gly_l_aminoacid")
    def test_amino_acids_his_l_aminoacid(self): StructureTest(dir="amino_acids", test="his_l_aminoacid")
    def test_amino_acids_ile_l_aminoacid(self): StructureTest(dir="amino_acids", test="ile_l_aminoacid")
    def test_amino_acids_leu_l_aminoacid(self): StructureTest(dir="amino_acids", test="leu_l_aminoacid")
    def test_amino_acids_lys_l_aminoacid(self): StructureTest(dir="amino_acids", test="lys_l_aminoacid")
    def test_amino_acids_met_l_aminoacid(self): StructureTest(dir="amino_acids", test="met_l_aminoacid")
    def test_amino_acids_phe_l_aminoacid(self): StructureTest(dir="amino_acids", test="phe_l_aminoacid")
    def test_amino_acids_pro_l_aminoacid(self): StructureTest(dir="amino_acids", test="pro_l_aminoacid")
    def test_amino_acids_ser_l_aminoacid(self): StructureTest(dir="amino_acids", test="ser_l_aminoacid")
    def test_amino_acids_thr_l_aminoacid(self): StructureTest(dir="amino_acids", test="thr_l_aminoacid")
    def test_amino_acids_tyr_l_aminoacid(self): StructureTest(dir="amino_acids", test="tyr_l_aminoacid")
    def test_amino_acids_val_l_aminoacid(self): StructureTest(dir="amino_acids", test="val_l_aminoacid")
    def test_floppy_organics_C2H6(self): StructureTest(dir="floppy_organics", test="C2H6")
    def test_floppy_organics_C3H8(self): StructureTest(dir="floppy_organics", test="C3H8")
    def test_floppy_organics_C4H10a(self): StructureTest(dir="floppy_organics", test="C4H10a")
    def test_floppy_organics_C4H10b(self): StructureTest(dir="floppy_organics", test="C4H10b")
    def test_floppy_organics_C4H10c(self): StructureTest(dir="floppy_organics", test="C4H10c")
    def test_floppy_organics_C4H8(self): StructureTest(dir="floppy_organics", test="C4H8")
    def test_floppy_organics_C5H10(self): StructureTest(dir="floppy_organics", test="C5H10")
    def test_floppy_organics_C5H12a(self): StructureTest(dir="floppy_organics", test="C5H12a")
    def test_floppy_organics_C5H12b(self): StructureTest(dir="floppy_organics", test="C5H12b")
    def test_floppy_organics_C5H12c(self): StructureTest(dir="floppy_organics", test="C5H12c")
    def test_floppy_organics_C5H12d(self): StructureTest(dir="floppy_organics", test="C5H12d")
    def test_floppy_organics_C5H12e(self): StructureTest(dir="floppy_organics", test="C5H12e")
    def test_floppy_organics_C6H12a(self): StructureTest(dir="floppy_organics", test="C6H12a")
    def test_floppy_organics_C6H12b(self): StructureTest(dir="floppy_organics", test="C6H12b")
    def test_floppy_organics_C6H14a(self): StructureTest(dir="floppy_organics", test="C6H14a")
    def test_floppy_organics_C6H14b(self): StructureTest(dir="floppy_organics", test="C6H14b")
    def test_floppy_organics_C6H14c(self): StructureTest(dir="floppy_organics", test="C6H14c")
    def test_floppy_organics_C6H14d(self): StructureTest(dir="floppy_organics", test="C6H14d")
    def test_floppy_organics_C6H14e(self): StructureTest(dir="floppy_organics", test="C6H14e")
    def test_floppy_organics_C6H14f(self): StructureTest(dir="floppy_organics", test="C6H14f")
    def test_floppy_organics_C7H14a(self): StructureTest(dir="floppy_organics", test="C7H14a")
    def test_floppy_organics_C7H14b(self): StructureTest(dir="floppy_organics", test="C7H14b")
    def test_floppy_organics_C7H14c(self): StructureTest(dir="floppy_organics", test="C7H14c")
    def test_floppy_organics_CH4(self): StructureTest(dir="floppy_organics", test="CH4")
    def test_heteroatom_organics_ADAM_AlH2_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAM_AlH2_Cs")
    def test_heteroatom_organics_ADAM_BH2(self): StructureTest(dir="heteroatom_organics", test="ADAM_BH2")
    def test_heteroatom_organics_ADAM_Cl_c3v(self): StructureTest(dir="heteroatom_organics", test="ADAM_Cl_c3v")
    def test_heteroatom_organics_ADAM_F_c3v(self): StructureTest(dir="heteroatom_organics", test="ADAM_F_c3v")
    def test_heteroatom_organics_ADAM_NH2_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAM_NH2_Cs")
    def test_heteroatom_organics_ADAM_OH_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAM_OH_Cs")
    def test_heteroatom_organics_ADAM_PH2_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAM_PH2_Cs")
    def test_heteroatom_organics_ADAM_SH_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAM_SH_Cs")
    def test_heteroatom_organics_ADAM_SiH3_C3v(self): StructureTest(dir="heteroatom_organics", test="ADAM_SiH3_C3v")
    def test_heteroatom_organics_ADAMframe_AlH_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAMframe_AlH_Cs")
    def test_heteroatom_organics_ADAMframe_BH_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAMframe_BH_Cs")
    def test_heteroatom_organics_ADAMframe_NH_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAMframe_NH_Cs")
    def test_heteroatom_organics_ADAMframe_O_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAMframe_O_Cs")
    def test_heteroatom_organics_ADAMframe_PH_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAMframe_PH_Cs")
    def test_heteroatom_organics_ADAMframe_S_Cs(self): StructureTest(dir="heteroatom_organics", test="ADAMframe_S_Cs")
    def test_heteroatom_organics_ADAMframe_SiH2_c2v(self): StructureTest(dir="heteroatom_organics", test="ADAMframe_SiH2_c2v")
    def test_heteroatom_organics_Al_ADAM_C3v(self): StructureTest(dir="heteroatom_organics", test="Al_ADAM_C3v")
    def test_heteroatom_organics_B_ADAM_C3v(self): StructureTest(dir="heteroatom_organics", test="B_ADAM_C3v")
    def test_heteroatom_organics_C3H6AlH(self): StructureTest(dir="heteroatom_organics", test="C3H6AlH")
    def test_heteroatom_organics_C3H6BH(self): StructureTest(dir="heteroatom_organics", test="C3H6BH")
    def test_heteroatom_organics_C3H6NH(self): StructureTest(dir="heteroatom_organics", test="C3H6NH")
    def test_heteroatom_organics_C3H6O(self): StructureTest(dir="heteroatom_organics", test="C3H6O")
    def test_heteroatom_organics_C3H6PH(self): StructureTest(dir="heteroatom_organics", test="C3H6PH")
    def test_heteroatom_organics_C3H6S(self): StructureTest(dir="heteroatom_organics", test="C3H6S")
    def test_heteroatom_organics_C3H6SiH2(self): StructureTest(dir="heteroatom_organics", test="C3H6SiH2")
    def test_heteroatom_organics_C4H8AlH(self): StructureTest(dir="heteroatom_organics", test="C4H8AlH")
    def test_heteroatom_organics_C4H8BH(self): StructureTest(dir="heteroatom_organics", test="C4H8BH")
    def test_heteroatom_organics_C4H8NH(self): StructureTest(dir="heteroatom_organics", test="C4H8NH")
    def test_heteroatom_organics_C4H8O(self): StructureTest(dir="heteroatom_organics", test="C4H8O")
    def test_heteroatom_organics_C4H8PH(self): StructureTest(dir="heteroatom_organics", test="C4H8PH")
    def test_heteroatom_organics_C4H8S(self): StructureTest(dir="heteroatom_organics", test="C4H8S")
    def test_heteroatom_organics_C4H8SiH2(self): StructureTest(dir="heteroatom_organics", test="C4H8SiH2")
    def test_heteroatom_organics_C5H10AlH(self): StructureTest(dir="heteroatom_organics", test="C5H10AlH")
    def test_heteroatom_organics_C5H10BH(self): StructureTest(dir="heteroatom_organics", test="C5H10BH")
    def test_heteroatom_organics_C5H10NH(self): StructureTest(dir="heteroatom_organics", test="C5H10NH")
    def test_heteroatom_organics_C5H10O(self): StructureTest(dir="heteroatom_organics", test="C5H10O")
    def test_heteroatom_organics_C5H10PH(self): StructureTest(dir="heteroatom_organics", test="C5H10PH")
    def test_heteroatom_organics_C5H10S(self): StructureTest(dir="heteroatom_organics", test="C5H10S")
    def test_heteroatom_organics_C5H10SiH2(self): StructureTest(dir="heteroatom_organics", test="C5H10SiH2")
    def test_heteroatom_organics_CH3AlH2(self): StructureTest(dir="heteroatom_organics", test="CH3AlH2")
    def test_heteroatom_organics_CH3AlHCH3(self): StructureTest(dir="heteroatom_organics", test="CH3AlHCH3")
    def test_heteroatom_organics_CH3BH2(self): StructureTest(dir="heteroatom_organics", test="CH3BH2")
    def test_heteroatom_organics_CH3BHCH3(self): StructureTest(dir="heteroatom_organics", test="CH3BHCH3")
    def test_heteroatom_organics_CH3NH2(self): StructureTest(dir="heteroatom_organics", test="CH3NH2")
    def test_heteroatom_organics_CH3NHCH3(self): StructureTest(dir="heteroatom_organics", test="CH3NHCH3")
    def test_heteroatom_organics_CH3OCH3(self): StructureTest(dir="heteroatom_organics", test="CH3OCH3")
    def test_heteroatom_organics_CH3OH(self): StructureTest(dir="heteroatom_organics", test="CH3OH")
    def test_heteroatom_organics_CH3PH2(self): StructureTest(dir="heteroatom_organics", test="CH3PH2")
    def test_heteroatom_organics_CH3PHCH3(self): StructureTest(dir="heteroatom_organics", test="CH3PHCH3")
    def test_heteroatom_organics_CH3SCH3(self): StructureTest(dir="heteroatom_organics", test="CH3SCH3")
    def test_heteroatom_organics_CH3SH(self): StructureTest(dir="heteroatom_organics", test="CH3SH")
    def test_heteroatom_organics_CH3SiH2CH3(self): StructureTest(dir="heteroatom_organics", test="CH3SiH2CH3")
    def test_heteroatom_organics_CH3SiH3(self): StructureTest(dir="heteroatom_organics", test="CH3SiH3")
    def test_heteroatom_organics_C_CH3_3_AlH2(self): StructureTest(dir="heteroatom_organics", test="C_CH3_3_AlH2")
    def test_heteroatom_organics_C_CH3_3_BH2(self): StructureTest(dir="heteroatom_organics", test="C_CH3_3_BH2")
    def test_heteroatom_organics_C_CH3_3_NH2(self): StructureTest(dir="heteroatom_organics", test="C_CH3_3_NH2")
    def test_heteroatom_organics_C_CH3_3_OH(self): StructureTest(dir="heteroatom_organics", test="C_CH3_3_OH")
    def test_heteroatom_organics_C_CH3_3_PH2(self): StructureTest(dir="heteroatom_organics", test="C_CH3_3_PH2")
    def test_heteroatom_organics_C_CH3_3_SH(self): StructureTest(dir="heteroatom_organics", test="C_CH3_3_SH")
    def test_heteroatom_organics_C_CH3_3_SiH3(self): StructureTest(dir="heteroatom_organics", test="C_CH3_3_SiH3")
    def test_heteroatom_organics_N_ADAM_C3v(self): StructureTest(dir="heteroatom_organics", test="N_ADAM_C3v")
    def test_heteroatom_organics_P_ADAM_C3v(self): StructureTest(dir="heteroatom_organics", test="P_ADAM_C3v")
    def test_heteroatom_organics_SiH_ADAM_C3v(self): StructureTest(dir="heteroatom_organics", test="SiH_ADAM_C3v")
    def test_minimize_0001(self): StructureTest(dir="minimize", test="0001")
    def test_minimize_0005(self): StructureTest(dir="minimize", test="0005")
    def test_minimize_0008(self): MinimizeTest(dir="minimize", test="0008")
    def test_minimize_0009(self): StructureTest(dir="minimize", test="0009")
    def test_minimize_0010(self): MinimizeTest(dir="minimize", test="0010")
    def test_minimize_0011(self): MinimizeTest(dir="minimize", test="0011")
    def test_minimize_0012(self): MinimizeTest(dir="minimize", test="0012")
    def test_minimize_0013(self): StructureTest(dir="minimize", test="0013")
    def test_rigid_organics_C10H12(self): StructureTest(dir="rigid_organics", test="C10H12")
    def test_rigid_organics_C10H14(self): StructureTest(dir="rigid_organics", test="C10H14")
    def test_rigid_organics_C14H20(self): StructureTest(dir="rigid_organics", test="C14H20")
    def test_rigid_organics_C14H24(self): StructureTest(dir="rigid_organics", test="C14H24")
    def test_rigid_organics_C2H6(self): StructureTest(dir="rigid_organics", test="C2H6")
    def test_rigid_organics_C3H6(self): StructureTest(dir="rigid_organics", test="C3H6")
    def test_rigid_organics_C3H8(self): StructureTest(dir="rigid_organics", test="C3H8")
    def test_rigid_organics_C4H8(self): StructureTest(dir="rigid_organics", test="C4H8")
    def test_rigid_organics_C6H10(self): StructureTest(dir="rigid_organics", test="C6H10")
    def test_rigid_organics_C8H14(self): StructureTest(dir="rigid_organics", test="C8H14")
    def test_rigid_organics_C8H8(self): StructureTest(dir="rigid_organics", test="C8H8")
    def test_rigid_organics_CH4(self): StructureTest(dir="rigid_organics", test="CH4")
    def test_singlebond_stretch_Cl_AlH2(self): StructureTest(dir="singlebond_stretch", test="Cl_AlH2")
    def test_singlebond_stretch_Cl_BH2(self): StructureTest(dir="singlebond_stretch", test="Cl_BH2")
    def test_singlebond_stretch_Cl_CH3(self): StructureTest(dir="singlebond_stretch", test="Cl_CH3")
    def test_singlebond_stretch_Cl_Cl(self): StructureTest(dir="singlebond_stretch", test="Cl_Cl")
    def test_singlebond_stretch_Cl_F(self): StructureTest(dir="singlebond_stretch", test="Cl_F")
    def test_singlebond_stretch_Cl_NH2(self): StructureTest(dir="singlebond_stretch", test="Cl_NH2")
    def test_singlebond_stretch_Cl_OH(self): StructureTest(dir="singlebond_stretch", test="Cl_OH")
    def test_singlebond_stretch_Cl_PH2(self): StructureTest(dir="singlebond_stretch", test="Cl_PH2")
    def test_singlebond_stretch_Cl_SH(self): StructureTest(dir="singlebond_stretch", test="Cl_SH")
    def test_singlebond_stretch_Cl_SiH3(self): StructureTest(dir="singlebond_stretch", test="Cl_SiH3")
    def test_singlebond_stretch_F_AlH2(self): StructureTest(dir="singlebond_stretch", test="F_AlH2")
    def test_singlebond_stretch_F_BH2(self): StructureTest(dir="singlebond_stretch", test="F_BH2")
    def test_singlebond_stretch_F_CH3(self): StructureTest(dir="singlebond_stretch", test="F_CH3")
    def test_singlebond_stretch_F_F(self): StructureTest(dir="singlebond_stretch", test="F_F")
    def test_singlebond_stretch_F_NH2(self): StructureTest(dir="singlebond_stretch", test="F_NH2")
    def test_singlebond_stretch_F_OH(self): StructureTest(dir="singlebond_stretch", test="F_OH")
    def test_singlebond_stretch_F_PH2(self): StructureTest(dir="singlebond_stretch", test="F_PH2")
    def test_singlebond_stretch_F_SH(self): StructureTest(dir="singlebond_stretch", test="F_SH")
    def test_singlebond_stretch_F_SiH3(self): StructureTest(dir="singlebond_stretch", test="F_SiH3")
    def test_singlebond_stretch_H2Al_AlH2(self): StructureTest(dir="singlebond_stretch", test="H2Al_AlH2")
    def test_singlebond_stretch_H2Al_CH3(self): StructureTest(dir="singlebond_stretch", test="H2Al_CH3")
    def test_singlebond_stretch_H2Al_SiH3(self): StructureTest(dir="singlebond_stretch", test="H2Al_SiH3")
    def test_singlebond_stretch_H2B_AlH2(self): StructureTest(dir="singlebond_stretch", test="H2B_AlH2")
    def test_singlebond_stretch_H2B_BH2(self): StructureTest(dir="singlebond_stretch", test="H2B_BH2")
    def test_singlebond_stretch_H2B_CH3(self): StructureTest(dir="singlebond_stretch", test="H2B_CH3")
    def test_singlebond_stretch_H2B_NH2(self): StructureTest(dir="singlebond_stretch", test="H2B_NH2")
    def test_singlebond_stretch_H2B_PH2(self): StructureTest(dir="singlebond_stretch", test="H2B_PH2")
    def test_singlebond_stretch_H2B_SiH3(self): StructureTest(dir="singlebond_stretch", test="H2B_SiH3")
    def test_singlebond_stretch_H2N_AlH2(self): StructureTest(dir="singlebond_stretch", test="H2N_AlH2")
    def test_singlebond_stretch_H2N_CH3(self): StructureTest(dir="singlebond_stretch", test="H2N_CH3")
    def test_singlebond_stretch_H2N_NH2(self): StructureTest(dir="singlebond_stretch", test="H2N_NH2")
    def test_singlebond_stretch_H2N_PH2(self): StructureTest(dir="singlebond_stretch", test="H2N_PH2")
    def test_singlebond_stretch_H2N_SiH3(self): StructureTest(dir="singlebond_stretch", test="H2N_SiH3")
    def test_singlebond_stretch_H2P_AlH2(self): StructureTest(dir="singlebond_stretch", test="H2P_AlH2")
    def test_singlebond_stretch_H2P_CH3(self): StructureTest(dir="singlebond_stretch", test="H2P_CH3")
    def test_singlebond_stretch_H2P_PH2(self): StructureTest(dir="singlebond_stretch", test="H2P_PH2")
    def test_singlebond_stretch_H2P_SiH3(self): StructureTest(dir="singlebond_stretch", test="H2P_SiH3")
    def test_singlebond_stretch_H3C_CH3(self): StructureTest(dir="singlebond_stretch", test="H3C_CH3")
    def test_singlebond_stretch_H3C_SiH3(self): StructureTest(dir="singlebond_stretch", test="H3C_SiH3")
    def test_singlebond_stretch_H3Si_SiH3(self): StructureTest(dir="singlebond_stretch", test="H3Si_SiH3")
    def test_singlebond_stretch_H_AlH2(self): StructureTest(dir="singlebond_stretch", test="H_AlH2")
    def test_singlebond_stretch_H_BH2(self): StructureTest(dir="singlebond_stretch", test="H_BH2")
    def test_singlebond_stretch_H_CH3(self): StructureTest(dir="singlebond_stretch", test="H_CH3")
    def test_singlebond_stretch_H_Cl(self): StructureTest(dir="singlebond_stretch", test="H_Cl")
    def test_singlebond_stretch_H_F(self): StructureTest(dir="singlebond_stretch", test="H_F")
    def test_singlebond_stretch_H_H(self): StructureTest(dir="singlebond_stretch", test="H_H")
    def test_singlebond_stretch_H_NH2(self): StructureTest(dir="singlebond_stretch", test="H_NH2")
    def test_singlebond_stretch_HO_AlH2(self): StructureTest(dir="singlebond_stretch", test="HO_AlH2")
    def test_singlebond_stretch_HO_BH2(self): StructureTest(dir="singlebond_stretch", test="HO_BH2")
    def test_singlebond_stretch_HO_CH3(self): StructureTest(dir="singlebond_stretch", test="HO_CH3")
    def test_singlebond_stretch_H_OH(self): StructureTest(dir="singlebond_stretch", test="H_OH")
    def test_singlebond_stretch_HO_NH2(self): StructureTest(dir="singlebond_stretch", test="HO_NH2")
    def test_singlebond_stretch_HO_OH(self): StructureTest(dir="singlebond_stretch", test="HO_OH")
    def test_singlebond_stretch_HO_PH2(self): StructureTest(dir="singlebond_stretch", test="HO_PH2")
    def test_singlebond_stretch_HO_SiH3(self): StructureTest(dir="singlebond_stretch", test="HO_SiH3")
    def test_singlebond_stretch_H_PH2(self): StructureTest(dir="singlebond_stretch", test="H_PH2")
    def test_singlebond_stretch_HS_AlH2(self): StructureTest(dir="singlebond_stretch", test="HS_AlH2")
    def test_singlebond_stretch_HS_BH2(self): StructureTest(dir="singlebond_stretch", test="HS_BH2")
    def test_singlebond_stretch_HS_CH3(self): StructureTest(dir="singlebond_stretch", test="HS_CH3")
    def test_singlebond_stretch_H_SH(self): StructureTest(dir="singlebond_stretch", test="H_SH")
    def test_singlebond_stretch_H_SiH3(self): StructureTest(dir="singlebond_stretch", test="H_SiH3")
    def test_singlebond_stretch_HS_NH2(self): StructureTest(dir="singlebond_stretch", test="HS_NH2")
    def test_singlebond_stretch_HS_OH(self): StructureTest(dir="singlebond_stretch", test="HS_OH")
    def test_singlebond_stretch_HS_PH2(self): StructureTest(dir="singlebond_stretch", test="HS_PH2")
    def test_singlebond_stretch_HS_SH(self): StructureTest(dir="singlebond_stretch", test="HS_SH")
    def test_singlebond_stretch_HS_SiH3(self): StructureTest(dir="singlebond_stretch", test="HS_SiH3")
    def test_singlebond_stretch_test_Cl_AlH2(self): StructureTest(dir="singlebond_stretch", test="Cl_AlH2")
    def test_singlebond_stretch_test_Cl_BH2(self): StructureTest(dir="singlebond_stretch", test="Cl_BH2")
    def test_singlebond_stretch_test_Cl_CH3(self): StructureTest(dir="singlebond_stretch", test="Cl_CH3")
    def test_singlebond_stretch_test_Cl_Cl(self): StructureTest(dir="singlebond_stretch", test="Cl_Cl")
    def test_singlebond_stretch_test_Cl_F(self): StructureTest(dir="singlebond_stretch", test="Cl_F")
    def test_singlebond_stretch_test_Cl_NH2(self): StructureTest(dir="singlebond_stretch", test="Cl_NH2")
    def test_singlebond_stretch_test_Cl_OH(self): StructureTest(dir="singlebond_stretch", test="Cl_OH")
    def test_singlebond_stretch_test_Cl_PH2(self): StructureTest(dir="singlebond_stretch", test="Cl_PH2")
    def test_singlebond_stretch_test_Cl_SH(self): StructureTest(dir="singlebond_stretch", test="Cl_SH")
    def test_singlebond_stretch_test_Cl_SiH3(self): StructureTest(dir="singlebond_stretch", test="Cl_SiH3")
    def test_singlebond_stretch_test_F_AlH2(self): StructureTest(dir="singlebond_stretch", test="F_AlH2")
    def test_singlebond_stretch_test_F_BH2(self): StructureTest(dir="singlebond_stretch", test="F_BH2")
    def test_singlebond_stretch_test_F_CH3(self): StructureTest(dir="singlebond_stretch", test="F_CH3")
    def test_singlebond_stretch_test_F_F(self): StructureTest(dir="singlebond_stretch", test="F_F")
    def test_singlebond_stretch_test_F_NH2(self): StructureTest(dir="singlebond_stretch", test="F_NH2")
    def test_singlebond_stretch_test_F_OH(self): StructureTest(dir="singlebond_stretch", test="F_OH")
    def test_singlebond_stretch_test_F_PH2(self): StructureTest(dir="singlebond_stretch", test="F_PH2")
    def test_singlebond_stretch_test_F_SH(self): StructureTest(dir="singlebond_stretch", test="F_SH")
    def test_singlebond_stretch_test_F_SiH3(self): StructureTest(dir="singlebond_stretch", test="F_SiH3")
    def test_singlebond_stretch_test_H2Al_AlH2(self): StructureTest(dir="singlebond_stretch", test="H2Al_AlH2")
    def test_singlebond_stretch_test_H2Al_CH3(self): StructureTest(dir="singlebond_stretch", test="H2Al_CH3")
    def test_singlebond_stretch_test_H2Al_SiH3(self): StructureTest(dir="singlebond_stretch", test="H2Al_SiH3")
    def test_singlebond_stretch_test_H2B_AlH2(self): StructureTest(dir="singlebond_stretch", test="H2B_AlH2")
    def test_singlebond_stretch_test_H2B_BH2(self): StructureTest(dir="singlebond_stretch", test="H2B_BH2")
    def test_singlebond_stretch_test_H2B_CH3(self): StructureTest(dir="singlebond_stretch", test="H2B_CH3")
    def test_singlebond_stretch_test_H2B_NH2(self): StructureTest(dir="singlebond_stretch", test="H2B_NH2")
    def test_singlebond_stretch_test_H2B_PH2(self): StructureTest(dir="singlebond_stretch", test="H2B_PH2")
    def test_singlebond_stretch_test_H2B_SiH3(self): StructureTest(dir="singlebond_stretch", test="H2B_SiH3")
    def test_singlebond_stretch_test_H2N_AlH2(self): StructureTest(dir="singlebond_stretch", test="H2N_AlH2")
    def test_singlebond_stretch_test_H2N_CH3(self): StructureTest(dir="singlebond_stretch", test="H2N_CH3")
    def test_singlebond_stretch_test_H2N_NH2(self): StructureTest(dir="singlebond_stretch", test="H2N_NH2")
    def test_singlebond_stretch_test_H2N_PH2(self): StructureTest(dir="singlebond_stretch", test="H2N_PH2")
    def test_singlebond_stretch_test_H2N_SiH3(self): StructureTest(dir="singlebond_stretch", test="H2N_SiH3")
    def test_singlebond_stretch_test_H2P_AlH2(self): StructureTest(dir="singlebond_stretch", test="H2P_AlH2")
    def test_singlebond_stretch_test_H2P_CH3(self): StructureTest(dir="singlebond_stretch", test="H2P_CH3")
    def test_singlebond_stretch_test_H2P_PH2(self): StructureTest(dir="singlebond_stretch", test="H2P_PH2")
    def test_singlebond_stretch_test_H2P_SiH3(self): StructureTest(dir="singlebond_stretch", test="H2P_SiH3")
    def test_singlebond_stretch_test_H3C_CH3(self): StructureTest(dir="singlebond_stretch", test="H3C_CH3")
    def test_singlebond_stretch_test_H3C_SiH3(self): StructureTest(dir="singlebond_stretch", test="H3C_SiH3")
    def test_singlebond_stretch_test_H3Si_SiH3(self): StructureTest(dir="singlebond_stretch", test="H3Si_SiH3")
    def test_singlebond_stretch_test_H_AlH2(self): StructureTest(dir="singlebond_stretch", test="H_AlH2")
    def test_singlebond_stretch_test_H_BH2(self): StructureTest(dir="singlebond_stretch", test="H_BH2")
    def test_singlebond_stretch_test_H_CH3(self): StructureTest(dir="singlebond_stretch", test="H_CH3")
    def test_singlebond_stretch_test_H_Cl(self): StructureTest(dir="singlebond_stretch", test="H_Cl")
    def test_singlebond_stretch_test_H_F(self): StructureTest(dir="singlebond_stretch", test="H_F")
    def test_singlebond_stretch_test_H_H(self): StructureTest(dir="singlebond_stretch", test="H_H")
    def test_singlebond_stretch_test_H_NH2(self): StructureTest(dir="singlebond_stretch", test="H_NH2")
    def test_singlebond_stretch_test_HO_AlH2(self): StructureTest(dir="singlebond_stretch", test="HO_AlH2")
    def test_singlebond_stretch_test_HO_BH2(self): StructureTest(dir="singlebond_stretch", test="HO_BH2")
    def test_singlebond_stretch_test_HO_CH3(self): StructureTest(dir="singlebond_stretch", test="HO_CH3")
    def test_singlebond_stretch_test_H_OH(self): StructureTest(dir="singlebond_stretch", test="H_OH")
    def test_singlebond_stretch_test_HO_NH2(self): StructureTest(dir="singlebond_stretch", test="HO_NH2")
    def test_singlebond_stretch_test_HO_OH(self): StructureTest(dir="singlebond_stretch", test="HO_OH")
    def test_singlebond_stretch_test_HO_PH2(self): StructureTest(dir="singlebond_stretch", test="HO_PH2")
    def test_singlebond_stretch_test_HO_SiH3(self): StructureTest(dir="singlebond_stretch", test="HO_SiH3")
    def test_singlebond_stretch_test_H_PH2(self): StructureTest(dir="singlebond_stretch", test="H_PH2")
    def test_singlebond_stretch_test_HS_AlH2(self): StructureTest(dir="singlebond_stretch", test="HS_AlH2")
    def test_singlebond_stretch_test_HS_BH2(self): StructureTest(dir="singlebond_stretch", test="HS_BH2")
    def test_singlebond_stretch_test_HS_CH3(self): StructureTest(dir="singlebond_stretch", test="HS_CH3")
    def test_singlebond_stretch_test_H_SH(self): StructureTest(dir="singlebond_stretch", test="H_SH")
    def test_singlebond_stretch_test_H_SiH3(self): StructureTest(dir="singlebond_stretch", test="H_SiH3")
    def test_singlebond_stretch_test_HS_NH2(self): StructureTest(dir="singlebond_stretch", test="HS_NH2")
    def test_singlebond_stretch_test_HS_OH(self): StructureTest(dir="singlebond_stretch", test="HS_OH")
    def test_singlebond_stretch_test_HS_PH2(self): StructureTest(dir="singlebond_stretch", test="HS_PH2")
    def test_singlebond_stretch_test_HS_SH(self): StructureTest(dir="singlebond_stretch", test="HS_SH")
    def test_singlebond_stretch_test_HS_SiH3(self): StructureTest(dir="singlebond_stretch", test="HS_SiH3")

    ### Pyrex tests

    def test_pyrex_minH2(self): PyrexTest("test_pyrex_minH2", "tests/minimize/test_h2")
    def test_pyrex_minimize0001(self): PyrexTest("test_pyrex_minimize0001", "tests/minimize/test_0001")

    def test_pyrex_dynamics(self):
        class Foo(PyrexTest):
            def run(self):
                import sim
                s = sim.theSimulator()

                s.reinitGlobals()
                s.InputFileName = "tests/dynamics/test_0002.mmp"
                s.OutputFileName = "tests/dynamics/test_0002.dpb"
                s.ToMinimize = 0
                s.DumpAsText = 0
                s.OutputFormat = 1
                s.NumFrames = 100
                s.PrintFrameNums = 0
                s.IterPerFrame = 10
                s.Temperature = 300
                s.go()
                assert not sim.isFileAscii("tests/dynamics/test_0002.dpb")
        Foo("test_pyrex_dynamics")

    # Jig tests
    def test_enabled_disabled_jigs_001_disabled_anchors(self):
        JigTest(dir="enabled_disabled_jigs", test="001_disabled_anchors")
    def test_enabled_disabled_jigs_002_one_anchor_enabled_other_disabled(self):
        JigTest(dir="enabled_disabled_jigs", test="002_one_anchor_enabled_other_disabled")
    def test_enabled_disabled_jigs_003_one_thermometer_enabled_other_disabled(self):
        JigTest(dir="enabled_disabled_jigs", test="003_one_thermometer_enabled_other_disabled")
    def test_enabled_disabled_jigs_004_one_thermostat_enabled_other_disabled(self):
        JigTest(dir="enabled_disabled_jigs", test="004_one_thermostat_enabled_other_disabled")
    def test_enabled_disabled_jigs_005_disabled_measure_distance_jig(self):
        JigTest(dir="enabled_disabled_jigs", test="005_disabled_measure_distance_jig")
    def test_enabled_disabled_jigs_006_one_rotarymotor_enabled_and_other_disabled(self):
        JigTest(dir="enabled_disabled_jigs", test="006_one_rotarymotor_enabled_and_other_disabled")
    def test_enabled_disabled_jigs_007_one_linearmotor_enabled_and_other_disabled(self):
        JigTest(dir="enabled_disabled_jigs", test="007_one_linearmotor_enabled_and_other_disabled")
    def test_jigs_to_several_atoms_001_rotarymotor_to_50_atoms(self):
        JigTest(dir="jigs_to_several_atoms", test="001_rotarymotor_to_50_atoms")
    def test_jigs_to_several_atoms_002_rotarymotor_to_100_atoms(self):
        JigTest(dir="jigs_to_several_atoms", test="002_rotarymotor_to_100_atoms")
    def test_jigs_to_several_atoms_003_linearmotor_to_50_atoms(self):
        JigTest(dir="jigs_to_several_atoms", test="003_linearmotor_to_50_atoms")
    def test_jigs_to_several_atoms_004_linearmotor_to_100_atoms(self):
        JigTest(dir="jigs_to_several_atoms", test="004_linearmotor_to_100_atoms")
    def test_jigs_to_several_atoms_005_anchors_to_50_atoms(self):
        JigTest(dir="jigs_to_several_atoms", test="005_anchors_to_50_atoms")
    def test_jigs_to_several_atoms_006_anchors_to_100_atoms(self):
        JigTest(dir="jigs_to_several_atoms", test="006_anchors_to_100_atoms")
    def test_jigs_to_several_atoms_007_rotarymotor_and_anchors_to_100_atoms(self):
        JigTest(dir="jigs_to_several_atoms", test="007_rotarymotor_and_anchors_to_100_atoms")
    def test_motors_001_linearmotor_0_force_and_0_stiffness(self):
        JigTest(dir="motors", test="001_linearmotor_0_force_and_0_stiffness")
    def test_motors_002_linearmotor_0_force_and_negative_stiffness(self):
        JigTest(dir="motors", test="002_linearmotor_0_force_and_negative_stiffness")
    def test_motors_003_linearmotor_0_force_and_positive_stiffness(self):
        JigTest(dir="motors", test="003_linearmotor_0_force_and_positive_stiffness")
    def test_motors_004_linearmotor_negative_force_and_negative_stiffness(self):
        JigTest(dir="motors", test="004_linearmotor_negative_force_and_negative_stiffness")
    def test_motors_005_linearmotor_negative_force_and_positive_stiffness(self):
        JigTest(dir="motors", test="005_linearmotor_negative_force_and_positive_stiffness")
    def test_motors_006_linearmotor_negative_force_and_0_stiffness(self):
        JigTest(dir="motors", test="006_linearmotor_negative_force_and_0_stiffness")
    def test_motors_007_linearmotor_positive_force_and_0_stiffness(self):
        JigTest(dir="motors", test="007_linearmotor_positive_force_and_0_stiffness")
    def test_motors_008_linearmotor_positive_force_and_positive_stiffness(self):
        JigTest(dir="motors", test="008_linearmotor_positive_force_and_positive_stiffness")
    def test_motors_009_linearmotor_Methane_Molecule(self):
        JigTest(dir="motors", test="009_linearmotor_Methane_Molecule")
    def test_motors_010_linearmotor_box_of_helium(self):
        JigTest(dir="motors", test="010_linearmotor_box_of_helium")
    def test_motors_011_rotarymotor_0_torque_and_0_speed(self):
        JigTest(dir="motors", test="011_rotarymotor_0_torque_and_0_speed")
    def test_motors_012_rotarymotor_0_torque_and_negative_speed(self):
        JigTest(dir="motors", test="012_rotarymotor_0_torque_and_negative_speed")
    def test_motors_013_rotarymotor_0_torque_and_positive_speed(self):
        JigTest(dir="motors", test="013_rotarymotor_0_torque_and_positive_speed")
    def test_motors_014_rotarymotor_negative_torque_and_negative_speed(self):
        JigTest(dir="motors", test="014_rotarymotor_negative_torque_and_negative_speed")
    def test_motors_015_rotarymotor_negative_torque_and_positive_speed(self):
        JigTest(dir="motors", test="015_rotarymotor_negative_torque_and_positive_speed")
    def test_motors_016_rotarymotor_negative_torque_and_0_speed(self):
        JigTest(dir="motors", test="016_rotarymotor_negative_torque_and_0_speed")
    def test_motors_017_rotarymotor_positive_torque_and_negative_speed(self):
        JigTest(dir="motors", test="017_rotarymotor_positive_torque_and_negative_speed")
    def test_motors_018_rotarymotor_positive_torque_and_0_speed(self):
        JigTest(dir="motors", test="018_rotarymotor_positive_torque_and_0_speed")
    def test_motors_019_rotarymotor_medium_torque_and_speed(self):
        JigTest(dir="motors", test="019_rotarymotor_medium_torque_and_speed")
    def test_motors_020_rotarymotor_high_torque_and_speed(self):
        JigTest(dir="motors", test="020_rotarymotor_high_torque_and_speed")
    def test_motors_021_rotarymotor_dyno_jig_test_to_same_chunk(self):
        JigTest(dir="motors", test="021_rotarymotor_dyno_jig_test_to_same_chunk")
    def test_motors_022_rotary_motor_small_bearing_test(self):
        JigTest(dir="motors", test="022_rotary_motor_small_bearing_test")
    def test_motors_023_rotarymotor_two_planet_gears(self):
        JigTest(dir="motors", test="023_rotarymotor_two_planet_gears")
    def test_motors_024_linearmotor_two_dodecahedranes(self):
        JigTest(dir="motors", test="024_linearmotor_two_dodecahedranes")
    def test_motors_025_two_linearmotors_applying_equal_forces_normal_to_each_other(self):
        JigTest(dir="motors", test="025_two_linearmotors_applying_equal_forces_normal_to_each_other")
    def test_motors_026_two_linearmotors_applying_equal_and_opposite_forces(self):
        JigTest(dir="motors", test="026_two_linearmotors_applying_equal_and_opposite_forces")
    def test_motors_027_two_rotarymotors_applying_equal_and_opposite_torque(self):
        JigTest(dir="motors", test="027_two_rotarymotors_applying_equal_and_opposite_torque")
    def test_motors_028_bug1306_test2(self):
        JigTest(dir="motors", test="028_bug1306_test2")
    def test_motors_029_bug_1331(self):
        JigTest(dir="motors", test="029_bug_1331")
    def test_motors_030_rotarymotor_and_linear_motor_attached_to_same_atoms(self):
        JigTest(dir="motors", test="030_rotarymotor_and_linear_motor_attached_to_same_atoms")
    def test_motors_and_anchors_001_linearmotor_pulling_against_anchor_1(self):
        JigTest(dir="motors_and_anchors", test="001_linearmotor_pulling_against_anchor_1")
    def test_motors_and_anchors_002_linearmotor_pulling_against_anchor_2(self):
        JigTest(dir="motors_and_anchors", test="002_linearmotor_pulling_against_anchor_2")
    def test_motors_and_anchors_003_rotorymotor_against_anchor_1(self):
        JigTest(dir="motors_and_anchors", test="003_rotorymotor_against_anchor_1")
    def test_motors_and_anchors_004_rotorymotor_against_anchor_2(self):
        JigTest(dir="motors_and_anchors", test="004_rotorymotor_against_anchor_2")
    def test_motors_and_anchors_005_rotorymotor_against_anchor_3(self):
        JigTest(dir="motors_and_anchors", test="005_rotorymotor_against_anchor_3")
    def test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_1(self):
        JigTest(dir="reordering_jigs_or_chunks", test="01_thermo_anchor_reordering_1")
    def test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_2(self):
        JigTest(dir="reordering_jigs_or_chunks", test="01_thermo_anchor_reordering_2")
    def test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_3(self):
        JigTest(dir="reordering_jigs_or_chunks", test="01_thermo_anchor_reordering_3")
    def test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_4(self):
        JigTest(dir="reordering_jigs_or_chunks", test="01_thermo_anchor_reordering_4")
    def test_reordering_jigs_or_chunks_01_thermo_anchor_reordering_5(self):
        JigTest(dir="reordering_jigs_or_chunks", test="01_thermo_anchor_reordering_5")
    def test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_1(self):
        JigTest(dir="reordering_jigs_or_chunks", test="02_thermo_anchor_stat_reordering_1")
    def test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_2(self):
        JigTest(dir="reordering_jigs_or_chunks", test="02_thermo_anchor_stat_reordering_2")
    def test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_3(self):
        JigTest(dir="reordering_jigs_or_chunks", test="02_thermo_anchor_stat_reordering_3")
    def test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_4(self):
        JigTest(dir="reordering_jigs_or_chunks", test="02_thermo_anchor_stat_reordering_4")
    def test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_5(self):
        JigTest(dir="reordering_jigs_or_chunks", test="02_thermo_anchor_stat_reordering_5")
    def test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_6(self):
        JigTest(dir="reordering_jigs_or_chunks", test="02_thermo_anchor_stat_reordering_6")
    def test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_7(self):
        JigTest(dir="reordering_jigs_or_chunks", test="02_thermo_anchor_stat_reordering_7")
    def test_reordering_jigs_or_chunks_02_thermo_anchor_stat_reordering_8(self):
        JigTest(dir="reordering_jigs_or_chunks", test="02_thermo_anchor_stat_reordering_8")
    def test_reordering_jigs_or_chunks_03_thermo_anchor_reordering(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_anchor_reordering")
    def test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_1(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_rmotor_anchor_stat_reordering_1")
    def test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_2(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_rmotor_anchor_stat_reordering_2")
    def test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_3(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_rmotor_anchor_stat_reordering_3")
    def test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_4(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_rmotor_anchor_stat_reordering_4")
    def test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_5(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_rmotor_anchor_stat_reordering_5")
    def test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_6(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_rmotor_anchor_stat_reordering_6")
    def test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_7(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_rmotor_anchor_stat_reordering_7")
    def test_reordering_jigs_or_chunks_03_thermo_rmotor_anchor_stat_reordering_8(self):
        JigTest(dir="reordering_jigs_or_chunks", test="03_thermo_rmotor_anchor_stat_reordering_8")
    def test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_1(self):
        JigTest(dir="reordering_jigs_or_chunks", test="04_thermo_lmotor_anchor_stat_reordering_1")
    def test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_2(self):
        JigTest(dir="reordering_jigs_or_chunks", test="04_thermo_lmotor_anchor_stat_reordering_2")
    def test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_3(self):
        JigTest(dir="reordering_jigs_or_chunks", test="04_thermo_lmotor_anchor_stat_reordering_3")
    def test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_4(self):
        JigTest(dir="reordering_jigs_or_chunks", test="04_thermo_lmotor_anchor_stat_reordering_4")
    def test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_5(self):
        JigTest(dir="reordering_jigs_or_chunks", test="04_thermo_lmotor_anchor_stat_reordering_5")
    def test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_6(self):
        JigTest(dir="reordering_jigs_or_chunks", test="04_thermo_lmotor_anchor_stat_reordering_6")
    def test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_7(self):
        JigTest(dir="reordering_jigs_or_chunks", test="04_thermo_lmotor_anchor_stat_reordering_7")
    def test_reordering_jigs_or_chunks_04_thermo_lmotor_anchor_stat_reordering_8(self):
        JigTest(dir="reordering_jigs_or_chunks", test="04_thermo_lmotor_anchor_stat_reordering_8")
    def test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_1(self):
        JigTest(dir="reordering_jigs_or_chunks", test="05_thermo_lmotor_anchor_measurement_jigs_reordering_1")
    def test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_2(self):
        JigTest(dir="reordering_jigs_or_chunks", test="05_thermo_lmotor_anchor_measurement_jigs_reordering_2")
    def test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_3(self):
        JigTest(dir="reordering_jigs_or_chunks", test="05_thermo_lmotor_anchor_measurement_jigs_reordering_3")
    def test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_4(self):
        JigTest(dir="reordering_jigs_or_chunks", test="05_thermo_lmotor_anchor_measurement_jigs_reordering_4")
    def test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_5(self):
        JigTest(dir="reordering_jigs_or_chunks", test="05_thermo_lmotor_anchor_measurement_jigs_reordering_5")
    def test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_6(self):
        JigTest(dir="reordering_jigs_or_chunks", test="05_thermo_lmotor_anchor_measurement_jigs_reordering_6")
    def test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_7(self):
        JigTest(dir="reordering_jigs_or_chunks", test="05_thermo_lmotor_anchor_measurement_jigs_reordering_7")
    def test_reordering_jigs_or_chunks_05_thermo_lmotor_anchor_measurement_jigs_reordering_8(self):
        JigTest(dir="reordering_jigs_or_chunks", test="05_thermo_lmotor_anchor_measurement_jigs_reordering_8")
    def test_temperature_tests_001_two_methanes_9A_apart_vdw_5(self):
        JigTest(dir="temperature_tests", test="001_two_methanes_9A_apart_vdw_5")
    def test_temperature_tests_002_two_methanes_10A_apart_vdw_6(self):
        JigTest(dir="temperature_tests", test="002_two_methanes_10A_apart_vdw_6")
    def test_temperature_tests_003_thermostat_test_1(self):
        JigTest(dir="temperature_tests", test="003_thermostat_test_1")
    def test_temperature_tests_003_thermostat_test_2(self):
        JigTest(dir="temperature_tests", test="003_thermostat_test_2")
    def test_temperature_tests_003_thermostat_test_3(self):
        JigTest(dir="temperature_tests", test="003_thermostat_test_3")
    def test_temperature_tests_003_thermostat_test_4(self):
        JigTest(dir="temperature_tests", test="003_thermostat_test_4")
    def test_temperature_tests_003_thermostat_test_5(self):
        JigTest(dir="temperature_tests", test="003_thermostat_test_5")
    def test_temperature_tests_003_thermostat_test(self):
        JigTest(dir="temperature_tests", test="003_thermostat_test")

class TwoStreamTextTestResult(unittest._TextTestResult):

    def __init__(self, progressStream, resultStream, descriptions, verbosity):
        unittest._TextTestResult.__init__(self, unittest._WritelnDecorator(progressStream), descriptions, verbosity)
        self.resultStream = unittest._WritelnDecorator(resultStream)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.resultStream.writeln(self.separator1)
            self.resultStream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            self.resultStream.writeln(self.separator2)
            self.resultStream.writeln("%s" % err)


class Main(unittest.TextTestRunner):
    def main(self, args):
        options = None
        # Process command line arguments
        def generate(x):
            """update md5sums files according to current simulator
            behavior
            """
            global GENERATE
            GENERATE = True
        def md5check(x):
            """perform MD5 checksum comparisons; useful for simulator
            development
            """
            global MD5_CHECKS
            if sys.platform != "linux2":
                raise SystemExit("MD5 checks supported only on Linux")
            MD5_CHECKS = True
        def lengths_angles(x):
            """perform structure comparisons with known-good structures
            computed by QM minimizations, comparing bond lengths and bond
            angles
            """
            global STRUCTURE_COMPARISON_TYPE
            STRUCTURE_COMPARISON_TYPE = LENGTH_ANGLE_TEST
        def structcompare(x):
            """perform structure comparisons with known-good structures
            computed by QM minimizations, using code in structcompare.c
            """
            global STRUCTURE_COMPARISON_TYPE
            STRUCTURE_COMPARISON_TYPE = STRUCTCOMPARE_C_TEST
        def time_limit(x):
            """do as many tests as possible in this many seconds
            """
            assert x[:1] == "="
            global TIME_LIMIT
            TIME_LIMIT = string.atof(x[1:])
        def pyrex(x):
            """Perform the Pyrex tests
            """
            for nm in dir(Tests):
                if nm.startswith("test_") and not nm.startswith("test_pyrex"):
                    try: delattr(Tests, nm)
                    except AttributeError: pass
        def loose(x):
            """Loose tolerances on length and angle comparisons.
            """
            global LOOSE_TOLERANCES
            LOOSE_TOLERANCES = True
        def medium(x):
            """Moderate tolerances on length and angle comparisons.
            """
            global MEDIUM_TOLERANCES
            MEDIUM_TOLERANCES = True
        def tight(x):
            """Tight tolerances on length and angle comparisons.
            """
            global TIGHT_TOLERANCES
            TIGHT_TOLERANCES = True
        def test_dir(x):
            """which directory should we test
            """
            assert x[:1] == "="
            x = x[1:]
            assert x in ("minimize", "dynamics", "rigid_organics",
                         "amino_acids", "floppy_organics",
                         "heteroatom_organics")
            global TEST_DIR
            TEST_DIR = x
        def list_everything(x):
            """Instead of just showing the first failure for each test
            case, show every non-compliant energy term
            """
            global LIST_EVERYTHING
            LIST_EVERYTHING = True

        def debug(x):
            """debug this script
            """
            global DEBUG
            if x[:1] == "=":
                DEBUG = string.atoi(x[1:])
            else:
                DEBUG = 1
        def time_only(x):
            """measure the time each test takes, ignore any results
            """
            global TIME_ONLY, Tests
            TIME_ONLY = True
        def keep(x):
            """when a test is finished, don't delete its temporary
            directory (useful for debug)
            """
            global KEEP_RESULTS
            KEEP_RESULTS = True
        def todo_tasks(x):
            """reminders of what work still needs doing
            """
            global SHOW_TODO, MD5_CHECKS
            SHOW_TODO = True
            # catch all the TODOs everywhere
            MD5_CHECKS = True
        def verbose_failures(x):
            """print non-abbreviated assertion statements (useful for
            debug)
            """
            global VERBOSE_FAILURES
            VERBOSE_FAILURES = True
        def verbose_progress(x):
            """print verbose test names as progress indicator instead of dots.
            """
            self.verbosity = 2

        def help(x):
            """print help information
            """
            print __doc__
            for opt in options:
                print opt.__name__ + "\n            " + opt.__doc__
            sys.exit(0)

        options = (md5check,
                   lengths_angles,
                   structcompare,
                   time_limit,
                   pyrex,
                   loose,
                   medium,
                   tight,
                   test_dir,
                   list_everything,
                   generate,
                   debug,
                   time_only,
                   keep,
                   todo_tasks,
                   verbose_failures,
                   verbose_progress,
                   help)

        # Default behavior is to do all the tests, including the slow ones,
        # with loose tolerances, so things pass
        defaultArgs = ()

        if len(args) < 1:
            args = defaultArgs

        for arg in args:
            found = False
            for opt in options:
                nm = opt.__name__
                if arg.startswith(nm):
                    found = True
                    arg = arg[len(nm):]
                    opt(arg)
                    break
            if not found:
                print "Don't understand command line arg:", arg
                print "Try typing:   python tests.py help"
                sys.exit(1)

        # For failures, don't usually bother with complete tracebacks,
        # it's more information than we need.
        def addFailure(self, test, err):
            self.failures.append((test, traceback.format_exception(*err)[-1]))
        if not VERBOSE_FAILURES:
            unittest.TestResult.addFailure = addFailure
        global LENGTH_TOLERANCE, ANGLE_TOLERANCE
        if TIGHT_TOLERANCES:
            LENGTH_TOLERANCE = 0.03    # angstroms
            ANGLE_TOLERANCE = 3        # degrees
        if MEDIUM_TOLERANCES:
            LENGTH_TOLERANCE = 0.11    # angstroms
            ANGLE_TOLERANCE = 12       # degrees
        if LOOSE_TOLERANCES:
            LENGTH_TOLERANCE = 0.138   # angstroms
            ANGLE_TOLERANCE = 14.1     # degrees

        casenames = self.getCasenames()
        self.run(unittest.TestSuite(map(Tests, casenames)))

        if TIME_ONLY:
            lst = [ ]
            for name in testTimes.keys():
                t = testTimes[name]
                lst.append([t, name])
            lst.sort()
            import pprint
            pprint.pprint(map(lambda x: x[1], lst))
        else:
            print len(casenames) - testsSkipped, "tests really done,",
            print testsSkipped, "tests skipped"

    def getCasenames(self):
        # Start with tests that appear both as entries in RANKED_BY_RUNTIME
        # and _also_ as test cases in Tests.
        casenames = filter(lambda x: hasattr(Tests, x), RANKED_BY_RUNTIME)

        if TIME_ONLY or GENERATE:
            # Add any test cases in Tests that did not appear in RANKED_BY_RUNTIME.
            for attr in dir(Tests):
                if attr.startswith("test_") and attr not in casenames:
                    casenames.append(attr)
        elif TEST_DIR != None:
            # filter the results to only what we want
            def filt(name):
                return name.startswith("test_" + TEST_DIR)
            casenames = filter(filt, casenames)

        return casenames

    def _getCasenames(self):
        return [
            'test_dynamics_small_bearing_01',
            ]

    # send progress indicators to stderr (usually a terminal)
    def _makeResult(self):
        return TwoStreamTextTestResult(sys.stderr, sys.stdout, self.descriptions, self.verbosity)

    # send test results to stdout (can be easily redirected)
    def __init__(self, stream=sys.stdout, descriptions=1, verbosity=1):
        self.stream = unittest._WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity

"""
If you want some special selection of cases, you can do it like this:

import sys
import tests

class Main(tests.Main):
    def getCasenames(self):
        return [
            'test_motors_011_rotarymotor_0_torque_and_0_speed',
            'test_motors_016_rotarymotor_negative_torque_and_0_speed',
            'test_motors_018_rotarymotor_positive_torque_and_0_speed',
            'test_motors_021_rotarymotor_dyno_jig_test_to_same_chunk',
            ]

Main().main(sys.argv[1:])
"""

###########################################


if __name__ == "__main__":
    Main().main(sys.argv[1:])
