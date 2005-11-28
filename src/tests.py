#!/usr/bin/python

"""Regression and QA test script for the simulator

Usage: tests.py [options]

Available options are:
    generate -- recreate reference files for tests
    keep -- when a test is finished, don't delete its temporary
            directory (useful for debug)
    thorough -- perform more in-depth tests beyond simply comparing
                MD5 checksums of output files
    slow -- perform slow tests (not for regression testing)
    debug -- debug this script

In day-to-day regression testing, the likely set of options will
be none at all, so that you get the fast tests and only do MD5
checksum comparisons. In infrequent QA testing, the likely set of
options will be "slow thorough". When we get new files from Damian
we'll use "generate". When this script needs updating or maintenance
the "debug" and "keep" options will be useful.

Currently all our test cases are very small molecules, so using
"thorough" doesn't make much difference, so I recommend that as a
regression test until our test cases grow so large or numerous that
it's preferable to 

$Id$
"""

__author__ = "Will"

import Numeric
import math
import md5
import os
import random
import re
import shutil
import string
import subprocess
import sys
import unittest

os.system("make simulator")

##################################################################

# How much variation do we permit in bond lengths and bond
# angles before we think it's a problem? For now these are
# wild guesses, to be later scrutinized by smart people.

POSITION_TOLERANCE = 0.5   # angstroms
LENGTH_TOLERANCE = 0.2     # angstroms
ANGLE_TOLERANCE = 10       # degrees

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
                if atm.mmpBonds(line):
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
            assert atm1 != atm2
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

        mmp = MmpFile()
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
        # TODO: handle multiple-frame xyz files from animations
        xyz = XyzFile()
        xyz.read(xyzFilename)
        if len(xyz) != self.numAtoms:
            raise WrongNumberOfAtoms, xyzFilename + \
                  " -> %d should be %d" % (len(xyz), self.numAtoms)

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

    def compare(self, xyzFilename1, xyzFilename2):
        # TODO: handle multiple-frame xyz files from animations
        L1, A1 = self.readXyz(xyzFilename1)
        L2, A2 = self.readXyz(xyzFilename2)
        for xyz1, xyz2 in map(None, L1, L2):
            a1, a2, L = xyz1
            a11, a22, LL = xyz2
            if a1 != a11 or a2 != a22:
                raise LengthMismatch("Term (%d, %d) versus (%d, %d)"
                                     % (a11, a22, a1, a2))
            if abs(L - LL) > LENGTH_TOLERANCE:
                raise LengthMismatch("(%d, %d) -> %f versus %f"
                                     % (a1, a2, LL, L))
        for xyz1, xyz2 in map(None, A1, A2):
            a1, a2, a3, A = xyz1
            a11, a22, a33, AA = xyz2
            if a1 != a11 or a2 != a22 or a3 != a33:
                raise AngleMismatch("Term (%d, %d, %d) versus (%d, %d, %d)"
                                    % (a11, a22, a33, a1, a2, a3))
            if abs(L - LL) > ANGLE_TOLERANCE:
                raise AngleMismatch("(%d, %d, %d) -> %f versus %f"
                                    % (a1, a2, a3, AA, A))

##################################################################

class Unimplemented(AssertionError):
    pass

def rmtreeSafe(dir):
    # platform-independent 'rm -rf'
    try: shutil.rmtree(dir)
    except OSError, e: assert e.args[0] == 2

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

DEBUG = 0
TESTS_BEYOND_MD5_CHECKS = False
GENERATE = False
KEEPRESULTS = False

class BaseTest:
    DEFAULT_INPUTS = ( )  # in addition to xxx.mmp
    DEFAULT_SIMOPTS = ( )
    DEFAULT_OUTPUTS = ( )  # in addition to stdout, stderr

    class MD5SumMismatch(AssertionError):
        pass

    def __init__(self, simopts=None, inputs=None, outputs=None):
        self.getBasename()
        if inputs == None:
            inputs = self.DEFAULT_INPUTS
        if simopts == None:
            simopts = self.DEFAULT_SIMOPTS
        if outputs == None:
            outputs = self.DEFAULT_OUTPUTS
        self.inputs = inputs
        self.outputs = outputs  # not using this yet
        self.runInSandbox(simopts)
        assert self.exitvalue == 0

    def getBasename(self):
        # get the calling method name e.g. "test_rigid_organics_C2H4"
        name = sys._getframe(2).f_code.co_name
        name = name[5:]  # get rid of "test_"
        n = name.rindex("_")
        self.dirname = dirname = name[:n]  # rigid_organicw
        self.shortname = shortname = name[n+1:]  # C2H4
        self.testname = testname = "test_" + shortname # test_C2H4
        self.midname = midname = os.sep.join(["tests", dirname, testname])
        self.basename = os.sep.join([os.getcwd(), midname])

    def runInSandbox(self, opts):
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
            cmdline = (("./simulator",) + opts +
                       (self.testname + ".mmp",))
            stdout = open("stdout", "w")
            stderr = open("stderr", "w")
            if DEBUG > 0:
                print self.basename
                print cmdline
            p = subprocess.Popen(cmdline,
                                 stdout=stdout, stderr=stderr)
            self.exitvalue = p.wait()
            stdout.close()
            stderr.close()
            self.checkOutputFiles()
            return
        finally:
            os.chdir(here)
            if not KEEPRESULTS: rmtreeSafe(tmpdir)

    def checkOutputFiles(self):
        if DEBUG > 0:
            print os.listdir(".")
        if DEBUG > 1:
            print ("******** " + self.basename + " ******** " +
                   repr(self.exitvalue) + " ********")
            for f in os.listdir("."):
                if f != "simulator":
                    # assume everything else is a text file
                    print "---- " + f + " ----"
                    sys.stdout.write(open(f).read())
        if GENERATE:
            # generate MD5 checksums for all output files, store in
            # .../sim/src/tests/rigid_organics/test_C4H8.md5sums
            outf = open(self.basename + ".md5sums", "w")
            stdout = md5sum("stdout")
            stderr = md5sum("stderr")
            outf.write("stdout %s\n" % md5sum("stdout"))
            outf.write("stderr %s\n" % md5sum("stderr"))
            for ext in self.outputs:
                fname = self.testname + "." + ext
                outf.write("%s %s\n" % (fname, md5sum(fname)))
            outf.close()
            # if we care about doing XYZ comparisons, generate a
            # foo.xyzcmp file
            if "xyzcmp" in self.inputs:
                if DEBUG > 0:
                    print ("copy " + self.testname + ".xyz to " +
                           self.basename + ".xyzcmp")
                shutil.copy(self.testname + ".xyz",
                            self.basename + ".xyzcmp")
            return
        # If we're not generating new output files (which we won't
        # do very often), we must be verifying a test case.
        #
        # Verify md5 checksums for output files
        inf = open(self.basename + ".md5sums")
        for line in inf.readlines():
            fname, sum = line.split()
            realsum = md5sum(fname)
            if realsum != sum:
                raise self.MD5SumMismatch(self.midname + " " + fname)
        inf.close()
        if TESTS_BEYOND_MD5_CHECKS:
            if "xyzcmp" in self.inputs:
                #self.structureComparisonAbsolute()
                self.structureComparisonBondlengthsBondangles()
            # TODO should we check other things in this case?

    def structureComparisonAbsolute(self):
        xyzcmpname = self.testname + ".xyzcmp"
        xyzname = self.testname + ".xyz"
        xyzcmp = open(xyzcmpname)
        xyz = open(xyzname)
        # number of atoms should be the same
        natoms = string.atoi(xyzcmp.readline().strip())
        natoms2 = string.atoi(xyz.readline().strip())
        if natoms != natoms2:
            raise WrongNumberOfAtoms, xyzname + \
                  " -> %d should be %d" % (natoms2, natoms)
        assert natoms == natoms2
        # ignore RMS for now
        xyzcmp.readline(), xyz.readline()
        for i in range(natoms):
            elem1, x1, y1, z1 = xyzcmp.readline().split()
            x1, y1, z1 = map(string.atof, (x1, y1, z1))
            elem2, x2, y2, z2 = xyz.readline().split()
            x2, y2, z2 = map(string.atof, (x2, y2, z2))
            dist = ((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2) ** .5
            if dist > POSITION_TOLERANCE:
                raise PositionMismatch, self.midname

    def structureComparisonBondlengthsBondangles(self):
        # TODO: handle multiple-frame xyz files from animations
        lac = LengthAngleComparison(self.testname + ".mmp")
        lac.compare(self.testname + ".xyz", self.testname + ".xyzcmp")

#########################################

class PassFailTest(BaseTest):
    """By default, the input for this kind of test are is a MMP file,
    the command line is given explicitly in the test methods, and the
    outputs are stdout, stderr, and the exit value. After the command
    line is run, the MD5 checksums for stdout and stderr are compared
    to earlier runs, and the exit value should be zero.
    """
    pass

class MinimizeTest(PassFailTest):
    """Perform a minimization, starting with a MMP file. The results
    should be stdout, stderr, exit value, and an XYZ file. All these
    are checked for correctness.
    """
    DEFAULT_SIMOPTS = ("--minimize",
                       "--dump-as-text")
    DEFAULT_OUTPUTS = ("xyz",)

class StructureTest(MinimizeTest):
    """Perform a minimization, starting with a MMP file. The results
    should be stdout, stderr, exit value, a TRC file, and an XYZ file.
    All these are checked for correctness. The XYZ file can be
    compared to an XYZCMP file for closeness of fit.
    """
    DEFAULT_INPUTS = ("xyzcmp",)
    DEFAULT_OUTPUTS = ("trc", "xyz")

class DynamicsTest(StructureTest):
    """Make a dynamics movie, starting with a MMP file. The results
    should be stdout, stderr, exit value, a TRC file, and an XYZ file
    with multiple frames. All these are checked for correctness.
    """
    DEFAULT_INPUTS = ( )
    DEFAULT_SIMOPTS = ("--dump-as-text",)
    DEFAULT_OUTPUTS = ("trc", "xyz")

####################################################

class Tests(unittest.TestCase):
    """Put the fast tests here.
    """
    def test_minimize_0001(self):
        StructureTest()
    def test_minimize_0002(self):
        PassFailTest(("--num-frames=500",
                      "--minimize",
                      "--dump-as-text"))
    def test_minimize_0003(self):
        PassFailTest(("--num-frames=300",
                      "--minimize",
                      "--dump-intermediate-text",
                      "--dump-as-text"))
    def test_minimize_0004(self):
        PassFailTest(("--num-frames=600",
                      "--minimize",
                      "--dump-as-text"))
    def test_minimize_0005(self):
        StructureTest()
    def test_minimize_0006(self):
        PassFailTest(("--num-frames=300",
                      "--minimize",
                      "--dump-intermediate-text",
                      "--dump-as-text"))
    def test_minimize_0007(self):
        PassFailTest(("--num-frames=300",
                      "--minimize",
                      "--dump-intermediate-text",
                      "--dump-as-text"))
    def test_minimize_0008(self):
        # test ground in minimize
        MinimizeTest()
    def test_minimize_0009(self):
        StructureTest()
    def test_minimize_0010(self):
        MinimizeTest()
    def test_minimize_0011(self):
        MinimizeTest()
    def test_minimize_0012(self):
        MinimizeTest()
    def test_minimize_0013(self):
        StructureTest()
    def test_rigid_organics_C10H12(self):
        StructureTest()
    def test_rigid_organics_C10H14(self):
        StructureTest()
    def test_rigid_organics_C14H20(self):
        StructureTest()
    def test_rigid_organics_C14H24(self):
        StructureTest()
    def test_rigid_organics_C2H6(self):
        StructureTest()
    def test_rigid_organics_C3H6(self):
        StructureTest()
    def test_rigid_organics_C3H8(self):
        StructureTest()
    def test_rigid_organics_C4H8(self):
        StructureTest()
    def test_rigid_organics_C6H10(self):
        StructureTest()
    def test_rigid_organics_C8H14(self):
        StructureTest()
    def test_rigid_organics_C8H8(self):
        StructureTest()
    def test_rigid_organics_CH4(self):
        StructureTest()
    def test_dynamics_0002(self):
        # ground, thermostat, and thermometer test
        DynamicsTest(("--num-frames=100",
                      "--temperature=300",
                      "--iters-per-frame=10",
                      "--dump-as-text"))

class SlowTests(Tests):
    """Put the slow tests here.
    """
    def test_dynamics_0001(self):
        # rotary motor test
        PassFailTest(("--num-frames=30",
                      "--temperature=0",
                      "--iters-per-frame=10000",
                      "--dump-as-text"))

###########################################

if __name__ == "__main__":
    if "generate" in sys.argv[1:]:
        GENERATE = True
    if "debug" in sys.argv[1:]:
        DEBUG = 1
    if "keep" in sys.argv[1:]:
        KEEPRESULTS = True
    if "thorough" in sys.argv[1:]:
        TESTS_BEYOND_MD5_CHECKS = True
    if "slow" in sys.argv[1:]:
        Tests = SlowTests
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
