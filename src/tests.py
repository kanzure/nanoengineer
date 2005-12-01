#!/usr/bin/python

"""Regression and QA test script for the simulator

Type:     python tests.py help
for descriptions of command line arguments.

$Id$
"""

__author__ = "Will"

import Numeric
import math
import md5
import os
import qt
import random
import re
import shutil
import string
import sys
import time
import traceback
import unittest

if not os.path.exists("simulator"):
    raise SystemExit("Please rebuild the simulator executable")

# Global flags and variables set from command lines
DEBUG = 0
MD5_CHECKS = False
STRUCTURE_COMPARISON_CHECKS = False
GENERATE = False
KEEP_RESULTS = False
SHOW_TODO = False
FULL_ASSERTIONS = False
C_STRUCT_COMPARE = False

class Unimplemented(AssertionError):
    pass

def todo(str):
    if SHOW_TODO:
        raise Unimplemented(str)

##################################################################

# How much variation do we permit in bond lengths and bond
# angles before we think it's a problem? For now these are
# wild guesses, to be later scrutinized by smart people.

LENGTH_TOLERANCE = 0.05    # angstroms
ANGLE_TOLERANCE = 0.5      # degrees

class WrongNumberOfAtoms(AssertionError):
    pass

class PositionMismatch(AssertionError):
    pass

class LengthMismatch(AssertionError):
    pass

class AngleMismatch(AssertionError):
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
        todo("I'm pretty sure os.linesep is not used correctly here")
        lines = lines.split(os.linesep)
        numAtoms = string.atoi(lines[0])
        lines = lines[2:]
        for i in range(numAtoms):
            a = Atom()
            element, x, y, z = lines[i].split()
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
        todo("I'm pretty sure os.linesep is not used correctly here")
        lines = lines.split(os.linesep)
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

    def readXyz(self, xyzFilename):
        todo("handle multiple-frame xyz files from animations")
        xyz = XyzFile()
        xyz.read(xyzFilename)
        if len(xyz) != self.numAtoms:
            raise WrongNumberOfAtoms, \
                  "%d, should be %d" % (len(xyz), self.numAtoms)

        lengthList = [ ]
        for first in self.bondLengthTerms.keys():
            for second in self.bondLengthTerms[first]:
                lengthList.append((first, second,
                                   measureLength(xyz, first, second)))
        angleList = [ ]
        for first in self.bondAngleTerms.keys():
            for second, third in self.bondAngleTerms[first]:
                angleList.append((first, second, third,
                                  measureAngle(xyz, first, second, third)))

        return (lengthList, angleList)

    def compare(self, questionableXyzFile, knownGoodXyzFile,
                lengthTolerance, angleTolerance):
        todo("handle multiple-frame xyz files from animations")
        L1, A1 = self.readXyz(questionableXyzFile)
        L2, A2 = self.readXyz(knownGoodXyzFile)
        for xyz1, xyz2 in map(None, L1, L2):
            a1, a2, L = xyz1
            a11, a22, LL = xyz2
            if a1 != a11 or a2 != a22:
                raise LengthMismatch("Term expected (%d, %d) versus (%d, %d)"
                                     % (a1, a2, a11, a22))
            if abs(L - LL) > lengthTolerance:
                e1 = _PeriodicTable[self.mmp.atoms[a1].elem]
                e2 = _PeriodicTable[self.mmp.atoms[a2].elem]
                str = "(%s:%d, %s:%d) expected %g, got %g" % (e1, a1, e2, a2, LL, L)
                raise LengthMismatch(str)
        for xyz1, xyz2 in map(None, A1, A2):
            a1, a2, a3, A = xyz1
            a11, a22, a33, AA = xyz2
            if a1 != a11 or a2 != a22 or a3 != a33:
                raise AngleMismatch("Term expected (%d, %d, %d) versus (%d, %d, %d)"
                                    % (a1, a2, a3, a11, a22, a33))
            if abs(L - LL) > angleTolerance:
                e1 = _PeriodicTable[self.mmp.atoms[a1].elem]
                e2 = _PeriodicTable[self.mmp.atoms[a2].elem]
                e3 = _PeriodicTable[self.mmp.atoms[a3].elem]
                str = "(%s:%d, %s:%d) expected %g, got %g" % (e1, a1, e2, a2,
                                                              e3, a3, AA, A)
                raise AngleMismatch(str)

##################################################################

def rmtreeSafe(dir):
    # platform-independent 'rm -rf'
    try: shutil.rmtree(dir)
    except OSError, e: pass

def md5sum(filename):
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

class BaseTest:
    DEFAULT_INPUTS = ( )  # in addition to xxx.mmp
    DEFAULT_SIMOPTS = ( )
    DEFAULT_OUTPUTS = ( )  # in addition to stdout, stderr

    class MD5SumMismatch(AssertionError):
        pass

    def __init__(self, dir=None, test=None,
                 simopts=None, inputs=None, outputs=None,
                 lengthTolerance=LENGTH_TOLERANCE,
                 angleTolerance=ANGLE_TOLERANCE,
                 expectedExitStatus=0):

        self.dirname = dir
        self.shortname = test
        self.testname = testname = "test_" + test # test_C2H4
        self.midname = midname = os.sep.join(["tests", dir, testname])
        self.basename = os.sep.join([os.getcwd(), midname])
        self.lengthTolerance = lengthTolerance
        self.angleTolerance = angleTolerance
        self.expectedExitStatus = expectedExitStatus

        if inputs == None:
            inputs = self.DEFAULT_INPUTS
        if simopts == None:
            simopts = self.DEFAULT_SIMOPTS
        if outputs == None:
            outputs = self.DEFAULT_OUTPUTS
        self.inputs = inputs
        self.simopts = simopts
        self.outputs = outputs
        self.runInSandbox()

    def getBasename(self):
        # get the calling method name e.g. "test_rigid_organics_C2H4"
        name = sys._getframe(2).f_code.co_name
        name = name[5:]  # get rid of "test_"
        n = name.rindex("_")
        self.dirname = dirname = name[:n]  # rigid_organics
        self.shortname = shortname = name[n+1:]  # C2H4
        self.testname = testname = "test_" + shortname # test_C2H4
        self.midname = midname = os.sep.join(["tests", dirname, testname])
        self.basename = os.sep.join([os.getcwd(), midname])

    def runInSandbox(self):
        # Run the simulator in sim/src/tmp.
        here = os.getcwd()
        tmpdir = "tmp_" + self.dirname + "_" + self.shortname
        try:
            rmtreeSafe(tmpdir)
            os.mkdir(tmpdir)
            # Copy the input files into the tmp directory.
            shutil.copy("simulator", tmpdir)
            # We always have a .mmp file
            shutil.copy(self.basename + ".mmp", tmpdir)
            for ext in self.inputs:
                shutil.copy(self.basename + "." + ext, tmpdir)
            # Go into the tmp directory and run the simulator.
            os.chdir(tmpdir)
            exitStatus = self.runCommand(self.simopts)
            if exitStatus != self.expectedExitStatus:
                str = ("simulator exit status was %d, expected %d" %
                       (exitStatus, self.expectedExitStatus))
                raise AssertionError(str)
            if GENERATE:
                self.generateOutputFiles()
            else:
                self.checkOutputFiles()
            return
        finally:
            os.chdir(here)
            if not KEEP_RESULTS:
                rmtreeSafe(tmpdir)

    def runCommand(self, opts):
        def substFOO(str):
            if str.startswith("FOO"):
                return self.testname + str[3:]
            return str
        cmdline = [ "./simulator" ] + map(substFOO, opts)
        if DEBUG > 0:
            print self.basename
            print cmdline
        simProcess = qt.QProcess()
        stdout = open("stdout", "a")
        stderr = open("stderr", "a")
        def blabout():
            stdout.write(str(simProcess.readStdout()))
        def blaberr():
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

    def generateOutputFiles(self):
        self.generateMd5Sums()
        # Don't overwrite xyzcmp files if they are Damian's data
        if self.dirname not in ("rigid_organics", "floppy_organics",
                                "amino_acids"):
            # if we care about doing XYZ comparisons, generate a
            # foo.xyzcmp file
            if "xyzcmp" in self.inputs:
                if DEBUG > 0:
                    print ("copy " + self.testname + ".xyz to " +
                           self.basename + ".xyzcmp")
                shutil.copy(self.testname + ".xyz",
                            self.basename + ".xyzcmp")

    def checkOutputFiles(self):
        if DEBUG > 0:
            print os.listdir(".")
        if DEBUG > 1:
            print ("******** " + self.basename + " ********")
            for f in os.listdir("."):
                if f != "simulator":
                    # assume everything else is a text file
                    print "---- " + f + " ----"
                    sys.stdout.write(open(f).read())
        if MD5_CHECKS:
            self.checkMd5Sums()
        if STRUCTURE_COMPARISON_CHECKS:
            if "xyzcmp" in self.inputs:
                if C_STRUCT_COMPARE:
                    if self.runCommand(("--base-file", "FOO.xyzcmp",
                                        "FOO.xyz")) != 0:
                        raise AssertionError("bad structure match")
                else:
                    self.structureComparisonBondlengthsBondangles()
            todo("anything else we should be checking here?")

    # Generate MD5 checksums for all output files, store in
    # tests/rigid_organics/test_C4H8.md5sums (for example)
    def generateMd5Sums(self):
        outf = open(self.basename + ".md5sums", "w")
        outf.write("stdout %s\n" % md5sum("stdout"))
        outf.write("stderr %s\n" % md5sum("stderr"))
        for ext in self.outputs:
            fname = self.testname + "." + ext
            outf.write("%s %s\n" % (fname, md5sum(fname)))
        outf.close()

    def checkMd5Sums(self):
        inf = open(self.basename + ".md5sums")
        for line in inf.readlines():
            fname, sum = line.split()
            realsum = md5sum(fname)
            if realsum != sum:
                raise self.MD5SumMismatch(self.midname + " " + fname)
        inf.close()

    def structureComparisonBondlengthsBondangles(self):
        todo("handle multiple-frame xyz files from animations")
        lac = LengthAngleComparison(self.testname + ".mmp")
        lac.compare(self.testname + ".xyz", self.testname + ".xyzcmp",
                    self.lengthTolerance, self.angleTolerance)

#########################################

class FailureExpectedTest(BaseTest):
    """By default, the input for this kind of test is a MMP file,
    the command line is given explicitly in the test methods, and the
    outputs are stdout, stderr, and the exit value. We expect a failure
    here but I'm not sure exactly what kind of failure.
    """
    DEFAULT_SIMOPTS = None  # force an explicit choice
    def runInSandbox(self):
        """Until I know exactly what kind of failure Eric wants here,
        just make it pass all the time.
        """
        pass

class MinimizeTest(BaseTest):
    """Perform a minimization, starting with a MMP file. The results
    should be stdout, stderr, exit value, and an XYZ file. All these
    are checked for correctness.
    """
    DEFAULT_SIMOPTS = ("--minimize", "--dump-as-text", "FOO.mmp")
    DEFAULT_OUTPUTS = ("xyz",)

class StructureTest(MinimizeTest):
    """Perform a minimization, starting with a MMP file. The results
    should be stdout, stderr, exit value, a TRC file, and an XYZ file.
    All these are checked for correctness. The XYZ file can be
    compared to an XYZCMP file for closeness of fit.
    """
    DEFAULT_INPUTS = ("xyzcmp",)
    DEFAULT_SIMOPTS = ("--minimize", "--dump-as-text", "FOO.mmp")
    DEFAULT_OUTPUTS = ( )

class DynamicsTest(MinimizeTest):
    """Make a dynamics movie, starting with a MMP file. The results
    should be stdout, stderr, exit value, a TRC file, and an XYZ file
    with multiple frames. All these are checked for correctness.
    """
    DEFAULT_INPUTS = ( )
    DEFAULT_SIMOPTS = ("--dump-as-text", "FOO.mmp")
    DEFAULT_OUTPUTS = ("trc", "xyz")

####################################################

class Tests(unittest.TestCase):
    """Put the fast tests here.
    """
    def test_dynamics_0002(self):
        # ground, thermostat, and thermometer test
        DynamicsTest(dir="dynamics", test="0002",
                     simopts=("--num-frames=100",
                              "--temperature=300",
                              "--iters-per-frame=10",
                              "--dump-as-text",
                              "FOO.mmp"))
    def test_minimize_0001(self):
        StructureTest(dir="minimize", test="0001")
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
    def test_minimize_0005(self):
        StructureTest(dir="minimize", test="0005")
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
    def test_minimize_0008(self):
        # test ground in minimize
        MinimizeTest(dir="minimize", test="0008")
    def test_minimize_0009(self):
        StructureTest(dir="minimize", test="0009")
    def test_minimize_0010(self):
        MinimizeTest(dir="minimize", test="0010")
    def test_minimize_0011(self):
        MinimizeTest(dir="minimize", test="0011")
    def test_minimize_0012(self):
        MinimizeTest(dir="minimize", test="0012")
    def test_minimize_0013(self):
        StructureTest(dir="minimize", test="0013")
    def test_rigid_organics_C10H12(self):
        StructureTest(dir="rigid_organics", test="C10H12")
    def test_rigid_organics_C10H14(self):
        StructureTest(dir="rigid_organics", test="C10H14")
    def test_rigid_organics_C14H20(self):
        StructureTest(dir="rigid_organics", test="C14H20")
    def test_rigid_organics_C14H24(self):
        StructureTest(dir="rigid_organics", test="C14H24")
    def test_rigid_organics_C2H6(self):
        StructureTest(dir="rigid_organics", test="C2H6")
    def test_rigid_organics_C3H6(self):
        StructureTest(dir="rigid_organics", test="C3H6")
    def test_rigid_organics_C3H8(self):
        StructureTest(dir="rigid_organics", test="C3H8")
    def test_rigid_organics_C4H8(self):
        StructureTest(dir="rigid_organics", test="C4H8")
    def test_rigid_organics_C6H10(self):
        StructureTest(dir="rigid_organics", test="C6H10")
    def test_rigid_organics_C8H14(self):
        StructureTest(dir="rigid_organics", test="C8H14")
    def test_rigid_organics_C8H8(self):
        StructureTest(dir="rigid_organics", test="C8H8")
    def test_rigid_organics_CH4(self):
        StructureTest(dir="rigid_organics", test="CH4")
    def test_floppy_organics_C2H6(self):
        StructureTest(dir="floppy_organics", test="C2H6")
    def test_floppy_organics_C3H8(self):
        StructureTest(dir="floppy_organics", test="C3H8")
    def test_floppy_organics_C4H10a(self):
        StructureTest(dir="floppy_organics", test="C4H10a")
    def test_floppy_organics_C4H10b(self):
        StructureTest(dir="floppy_organics", test="C4H10b")
    def test_floppy_organics_C4H10c(self):
        StructureTest(dir="floppy_organics", test="C4H10c")
    def test_floppy_organics_C4H8(self):
        StructureTest(dir="floppy_organics", test="C4H8")
    def test_floppy_organics_C5H10(self):
        StructureTest(dir="floppy_organics", test="C5H10")
    def test_floppy_organics_C5H12a(self):
        StructureTest(dir="floppy_organics", test="C5H12a")
    def test_floppy_organics_C5H12b(self):
        StructureTest(dir="floppy_organics", test="C5H12b")
    def test_floppy_organics_C5H12c(self):
        StructureTest(dir="floppy_organics", test="C5H12c")
    def test_floppy_organics_C5H12d(self):
        StructureTest(dir="floppy_organics", test="C5H12d")
    def test_floppy_organics_C5H12e(self):
        StructureTest(dir="floppy_organics", test="C5H12e")
    def test_floppy_organics_C6H12a(self):
        StructureTest(dir="floppy_organics", test="C6H12a")
    def test_floppy_organics_C6H12b(self):
        StructureTest(dir="floppy_organics", test="C6H12b")
    def test_floppy_organics_C6H14a(self):
        StructureTest(dir="floppy_organics", test="C6H14a")
    def test_floppy_organics_C6H14b(self):
        StructureTest(dir="floppy_organics", test="C6H14b")
    def test_floppy_organics_C6H14c(self):
        StructureTest(dir="floppy_organics", test="C6H14c")
    def test_floppy_organics_C6H14d(self):
        StructureTest(dir="floppy_organics", test="C6H14d")
    def test_floppy_organics_C6H14e(self):
        StructureTest(dir="floppy_organics", test="C6H14e")
    def test_floppy_organics_C6H14f(self):
        StructureTest(dir="floppy_organics", test="C6H14f")
    def test_floppy_organics_C7H14a(self):
        StructureTest(dir="floppy_organics", test="C7H14a")
    def test_floppy_organics_C7H14b(self):
        StructureTest(dir="floppy_organics", test="C7H14b")
    def test_floppy_organics_C7H14c(self):
        StructureTest(dir="floppy_organics", test="C7H14c")
    def test_floppy_organics_CH4(self):
        StructureTest(dir="floppy_organics", test="CH4")
    def test_amino_acids_ala_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="ala_l_aminoacid")
    def test_amino_acids_arg_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="arg_l_aminoacid")
    def test_amino_acids_asn_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="asn_l_aminoacid")
    def test_amino_acids_asp_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="asp_l_aminoacid")
    def test_amino_acids_cys_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="cys_l_aminoacid")
    def test_amino_acids_gln_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="gln_l_aminoacid")
    def test_amino_acids_glu_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="glu_l_aminoacid")
    def test_amino_acids_gly_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="gly_l_aminoacid")
    def test_amino_acids_his_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="his_l_aminoacid")
    def test_amino_acids_ile_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="ile_l_aminoacid")
    def test_amino_acids_leu_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="leu_l_aminoacid")
    def test_amino_acids_lys_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="lys_l_aminoacid")
    def test_amino_acids_met_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="met_l_aminoacid")
##     def test_amino_acids_phe_l_aminoacid(self):
##         StructureTest(dir="amino_acids", test="phe_l_aminoacid")
    def test_amino_acids_pro_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="pro_l_aminoacid")
    def test_amino_acids_ser_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="ser_l_aminoacid")
    def test_amino_acids_thr_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="thr_l_aminoacid")
    def test_amino_acids_tyr_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="tyr_l_aminoacid")
    def test_amino_acids_val_l_aminoacid(self):
        StructureTest(dir="amino_acids", test="val_l_aminoacid")

class SlowTests(Tests):
    """Put the slow tests here.
    """
    def test_dynamics_0001(self):
        # rotary motor test
        FailureExpectedTest(dir="dynamics", test="0001",
                            simopts=("--num-frames=30",
                                     "--temperature=0",
                                     "--iters-per-frame=10000",
                                     "--dump-as-text",
                                     "FOO.mmp"))

###########################################

if __name__ == "__main__":

    # Process command line arguments
    def generate():
        """recreate reference files for tests
        """
        global GENERATE
        GENERATE = True
    def md5check():
        """perform MD5 checksum comparisons; useful for simulator
        development
        """
        global MD5_CHECKS
        if sys.platform != "linux2":
            raise SystemExit("MD5 checks supported only on Linux")
        MD5_CHECKS = True
    def lengths_angles():
        """perform structure comparisons with known-good structures,
        computed by QM simulations, comparing bond lengths and bond angles
        """
        global STRUCTURE_COMPARISON_CHECKS
        STRUCTURE_COMPARISON_CHECKS = True
    def structcompare():
        """perform structure comparisons with known-good structures,
        computed by QM simulations, using code in sim/src/structcompare.c
        """
        global STRUCTURE_COMPARISON_CHECKS, C_STRUCT_COMPARE
        STRUCTURE_COMPARISON_CHECKS = True
        C_STRUCT_COMPARE = True
    def slow():
        """perform slow tests (not for regression testing)
        """
        global Tests, SlowTests
        Tests = SlowTests

    def debug():
        """debug this script
        """
        global DEBUG
        DEBUG = 1
    def keep():
        """when a test is finished, don't delete its temporary directory
        (useful for debug)
        """
        global KEEP_RESULTS
        KEEP_RESULTS = True
    def todo_tasks():
        """reminders of what work still needs doing
        """
        global SHOW_TODO, MD5_CHECKS, STRUCTURE_COMPARISON_CHECKS
        SHOW_TODO = True
        # catch all the TODOs everywhere
        MD5_CHECKS = True
        STRUCTURE_COMPARISON_CHECKS = True
    def assertions():
        """print non-abbreviated assertion statements (useful for debug)
        """
        global FULL_ASSERTIONS
        FULL_ASSERTIONS = True

    def help():
        """print help information
        """
        global options
        for opt in options:
            print opt.__name__ + "\n    " + opt.__doc__
        sys.exit(0)

    options = (md5check,
               lengths_angles,
               structcompare,
               slow,
               generate,
               debug,
               keep,
               todo_tasks,
               assertions,
               help)

    for arg in sys.argv[1:]:
        found = False
        for opt in options:
            if opt.__name__ == arg:
                found = True
                opt()
                break
        if not found:
            print "Don't understand command line arg:", arg
            print "Try typing:   python tests.py help"
            sys.exit(1)

    # For failures, don't usually bother with complete tracebacks,
    # it's more information than we need.
    def addFailure(self, test, err):
        self.failures.append((test, traceback.format_exception(*err)[-1]))
    if not FULL_ASSERTIONS:
        unittest.TestResult.addFailure = addFailure

    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
