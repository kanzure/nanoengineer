#!/usr/bin/python

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

import Numeric
import math
import md5
import os
import random
import re
import shutil
import string
import sys
import time
import traceback
import types
import unittest

if __name__ == "__main__":
    if not os.path.exists("simulator"):
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
TEST_DIR = None
LIST_EVERYTHING = False

class Unimplemented(AssertionError):
    pass

def todo(str):
    if SHOW_TODO:
        raise Unimplemented(str)

testTimes = { }
testsSkipped = 0

##################################################################

# How much variation do we permit in bond lengths and bond
# angles before we think it's a problem? For now these are
# wild guesses, to be later scrutinized by smart people.

LENGTH_TOLERANCE = 0.05    # angstroms
ANGLE_TOLERANCE = 5        # degrees

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

        def closeEnough(self, other, tolerance):
            if self.__class__ != other.__class__:
                return False
            if self.atoms != other.atoms:
                return False
            return abs(self.measure - other.measure) < tolerance

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
        for len1, len2 in map(None, L1, L2):
            if LIST_EVERYTHING:
                print len1
            elif not len1.closeEnough(len2, lengthTolerance):
                raise LengthMismatch(repr(len1) + " expected " + repr(len2))
        for ang1, ang2 in map(None, A1, A2):
            if LIST_EVERYTHING:
                print ang1
            elif not ang1.closeEnough(ang2, angleTolerance):
                raise AngleMismatch(repr(ang1) + " expected " + repr(ang2))

##################################################################

class EarlyTermination(Exception):
    pass

def rmtreeSafe(dir):
    # platform-independent 'rm -rf'
    try: shutil.rmtree(dir)
    except OSError, e: pass

class TimedTest:

    def __init__(self):
        if not TIME_ONLY:
            t, total = Tests.RANKED_BY_SPEED[self.methodname]
            if total > TIME_LIMIT:
                global testsSkipped
                testsSkipped += 1
                raise EarlyTermination
        self.startTime = time.time()

    def finish(self):
        if TIME_ONLY:
            global testTimes
            startTime, finishTime = self.startTime, time.time()
            testTimes[self.methodname] = finishTime - startTime
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
        self.midname = midname = os.sep.join(["tests", dir, testname])
        # methodname = test_rigid_organics_C2H4
        self.methodname = methodname = "_".join(["test", dir, test])
        # basename = .../sim/src/tests/rigid_organics/test_C2H4
        self.basename = os.sep.join([os.getcwd(), midname])
        self.expectedExitStatus = expectedExitStatus

        try:
            TimedTest.__init__(self)
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
            shutil.copy("simulator", tmpdir)
            # We always have a .mmp file
            shutil.copy(self.basename + ".mmp", tmpdir)
            for ext in self.inputs:
                shutil.copy(self.basename + "." + ext, tmpdir)
            # Go into the tmp directory and run the simulator.
            os.chdir(tmpdir)
            #self.startTime = time.time()
            exitStatus = self.runCommand(self.simopts)
            if exitStatus != self.expectedExitStatus:
                str = ("simulator exit status was %d, expected %d" %
                       (exitStatus, self.expectedExitStatus))
                raise AssertionError(str)
            if GENERATE:
                self.generateMd5Sums()
            else:
                self.checkOutputFiles()
            return
        finally:
            os.chdir(here)
            if not KEEP_RESULTS:
                rmtreeSafe(tmpdir)

    def runCommand(self, opts):
        import qt
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
        try:
            self.finish()
        except EarlyTermination:
            return
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
    def generateMd5Sums(self):
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

    def structureComparisonBondlengthsBondangles(self):
        todo("handle multiple-frame xyz files from animations")
        lac = LengthAngleComparison(self.testname + ".mmp")
        lac.compare(self.testname + ".xyz", self.testname + ".xyzcmp",
                    LENGTH_TOLERANCE, ANGLE_TOLERANCE)

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

class PyrexTest(TimedTest):

    def __init__(self, methodname, base=None):
        self.methodname = methodname
        self.base = base
        try:
            TimedTest.__init__(self)
        except EarlyTermination:
            return
        self.run()
        try:
            self.finish()
        except EarlyTermination:
            pass

    def run(self):
        import sim
        lac = LengthAngleComparison(self.base + ".mmp")
        s = sim.Minimize(self.base + ".mmp")
        s.Temperature = 300
        s.go()
        lac.compare(self.base + ".xyz", self.base + ".xyzcmp",
                    LENGTH_TOLERANCE, ANGLE_TOLERANCE)

####################################################

class Tests(unittest.TestCase):
    # Re-generate this with "python tests.py time_only"
    RANKED_BY_SPEED = {
        'test_amino_acids_ala_l_aminoacid': (1.9574508666992188, 65.829175472259521),
        'test_amino_acids_arg_l_aminoacid': (2.845736026763916, 84.467382431030273),
        'test_amino_acids_asn_l_aminoacid': (3.9342498779296875, 98.459981203079224),
        'test_amino_acids_asp_l_aminoacid': (4.5649271011352539, 111.43301033973694),
        'test_amino_acids_cys_l_aminoacid': (2.6238188743591309, 70.673336505889893),
        'test_amino_acids_gln_l_aminoacid': (6.6940081119537354, 128.93099141120911),
        'test_amino_acids_glu_l_aminoacid': (9.4835491180419922, 154.51688146591187),
        'test_amino_acids_gly_l_aminoacid': (1.0299968719482422, 48.772754430770874),
        'test_amino_acids_his_l_aminoacid': (5.2524340152740479, 116.68544435501099),
        'test_amino_acids_ile_l_aminoacid': (2.6943509578704834, 76.034211397171021),
        'test_amino_acids_leu_l_aminoacid': (8.3265669345855713, 145.03333234786987),
        'test_amino_acids_lys_l_aminoacid': (7.7757740020751953, 136.7067654132843),
        'test_amino_acids_met_l_aminoacid': (5.5515389442443848, 122.23698329925537),
        'test_amino_acids_phe_l_aminoacid': (0.055304050445556641,
                                             3.0889453887939453),
        'test_amino_acids_pro_l_aminoacid': (3.6579089164733887, 94.525731325149536),
        'test_amino_acids_ser_l_aminoacid': (4.3427910804748535, 106.86808323860168),
        'test_amino_acids_thr_l_aminoacid': (3.3646390438079834, 90.867822408676147),
        'test_amino_acids_tyr_l_aminoacid': (23.940731048583984, 178.45761251449585),
        'test_amino_acids_val_l_aminoacid': (4.0653109550476074, 102.52529215812683),
        'test_dynamics_0001': (0.0, 2.8426270484924316),
        'test_dynamics_0002': (0.27630090713500977, 13.105825185775757),
        'test_floppy_organics_C2H6': (0.12293386459350586, 7.9696669578552246),
        'test_floppy_organics_C3H8': (0.43416190147399902, 22.770768642425537),
        'test_floppy_organics_C4H10a': (0.39482307434082031, 19.865383625030518),
        'test_floppy_organics_C4H10b': (2.2203421592712402, 68.049517631530762),
        'test_floppy_organics_C4H10c': (0.34117007255554199, 18.01392126083374),
        'test_floppy_organics_C4H8': (0.13282299041748047, 8.1024899482727051),
        'test_floppy_organics_C5H10': (0.9909508228302002, 45.731656551361084),
        'test_floppy_organics_C5H12a': (1.491508960723877, 60.223838567733765),
        'test_floppy_organics_C5H12b': (0.58927702903747559, 30.990051507949829),
        'test_floppy_organics_C5H12c': (1.417910099029541, 57.259235620498657),
        'test_floppy_organics_C5H12d': (0.88733601570129395, 41.024554491043091),
        'test_floppy_organics_C5H12e': (0.94618821144104004, 44.740705728530884),
        'test_floppy_organics_C6H12a': (0.27666187286376953, 13.382487058639526),
        'test_floppy_organics_C6H12b': (0.28373289108276367, 13.947802782058716),
        'test_floppy_organics_C6H14a': (1.0165359973907471, 47.742757558822632),
        'test_floppy_organics_C6H14b': (0.73052382469177246, 37.734435558319092),
        'test_floppy_organics_C6H14c': (1.0690550804138184, 49.841809511184692),
        'test_floppy_organics_C6H14d': (1.31803297996521, 55.841325521469116),
        'test_floppy_organics_C6H14e': (1.8434181213378906, 63.871724605560303),
        'test_floppy_organics_C6H14f': (2.6665239334106445, 73.339860439300537),
        'test_floppy_organics_C7H14a': (0.71399593353271484, 37.003911733627319),
        'test_floppy_organics_C7H14b': (1.1561110019683838, 52.094208478927612),
        'test_floppy_organics_C7H14c': (3.0358009338378906, 87.503183364868164),
        'test_floppy_organics_CH4': (0.050858020782470703, 3.0336413383483887),
        'test_heteroatom_organics_ADAM_AlH2_Cs': (1.8044679164886475,
                                                  62.028306484222412),
        'test_heteroatom_organics_ADAM_BH2': (0.63968896865844727, 32.85053539276123),
        'test_heteroatom_organics_ADAM_Cl_c3v': (0.39522695541381836,
                                                 20.260610580444336),
        'test_heteroatom_organics_ADAM_F_c3v': (0.27051901817321777,
                                                12.829524278640747),
        'test_heteroatom_organics_ADAM_NH2_Cs': (0.93056797981262207,
                                                 42.850147485733032),
        'test_heteroatom_organics_ADAM_OH_Cs': (0.88188600540161133,
                                                40.137218475341797),
        'test_heteroatom_organics_ADAM_PH2_Cs': (1.4730939865112305,
                                                 58.732329607009888),
        'test_heteroatom_organics_ADAM_SH_Cs': (0.43400216102600098,
                                                22.336606740951538),
        'test_heteroatom_organics_ADAM_SiH3_C3v': (2.8224000930786133,
                                                   81.621646404266357),
        'test_heteroatom_organics_ADAMframe_AlH_Cs': (0.49486494064331055,
                                                      26.526994705200195),
        'test_heteroatom_organics_ADAMframe_BH_Cs': (0.69986796379089355,
                                                     35.580101728439331),
        'test_heteroatom_organics_ADAMframe_NH_Cs': (0.28516888618469238,
                                                     14.517940521240234),
        'test_heteroatom_organics_ADAMframe_O_Cs': (0.2931821346282959,
                                                    15.103321552276611),
        'test_heteroatom_organics_ADAMframe_PH_Cs': (0.31265497207641602,
                                                     16.342389345169067),
        'test_heteroatom_organics_ADAMframe_S_Cs': (0.23904585838317871,
                                                    11.518996238708496),
        'test_heteroatom_organics_ADAMframe_SiH2_c2v': (0.39939999580383301,
                                                        20.660010576248169),
        'test_heteroatom_organics_Al_ADAM_C3v': (0.5531761646270752,
                                                 28.693865776062012),
        'test_heteroatom_organics_B_ADAM_C3v': (0.34799599647521973,
                                                18.36191725730896),
        'test_heteroatom_organics_C3H6AlH': (0.1853950023651123, 9.3459186553955078),
        'test_heteroatom_organics_C3H6BH': (0.14544486999511719, 8.3908967971801758),
        'test_heteroatom_organics_C3H6NH': (0.11328792572021484, 7.4958279132843018),
        'test_heteroatom_organics_C3H6O': (0.088491916656494141, 6.8671247959136963),
        'test_heteroatom_organics_C3H6PH': (0.16201400756835938, 9.1605236530303955),
        'test_heteroatom_organics_C3H6S': (0.08668208122253418, 6.6909139156341553),
        'test_heteroatom_organics_C3H6SiH2': (0.21787381172180176, 10.38456130027771),
        'test_heteroatom_organics_C4H8AlH': (0.41529703140258789, 21.483160495758057),
        'test_heteroatom_organics_C4H8BH': (0.54457187652587891, 28.140689611434937),
        'test_heteroatom_organics_C4H8NH': (1.2428290843963623, 54.523292541503906),
        'test_heteroatom_organics_C4H8O': (0.99456501007080078, 46.726221561431885),
        'test_heteroatom_organics_C4H8PH': (0.3402099609375, 17.332291126251221),
        'test_heteroatom_organics_C4H8S': (0.30320405960083008, 15.406525611877441),
        'test_heteroatom_organics_C4H8SiH2': (0.45977091789245605,
                                              24.139268398284912),
        'test_heteroatom_organics_C5H10AlH': (0.61157083511352539,
                                              32.210846424102783),
        'test_heteroatom_organics_C5H10BH': (0.60922408103942871, 31.599275588989258),
        'test_heteroatom_organics_C5H10NH': (0.34046006202697754, 17.672751188278198),
        'test_heteroatom_organics_C5H10O': (0.2671349048614502, 12.559005260467529),
        'test_heteroatom_organics_C5H10PH': (0.29219889640808105, 14.810139417648315),
        'test_heteroatom_organics_C5H10S': (0.21963405609130859, 10.82377028465271),
        'test_heteroatom_organics_C5H10SiH2': (0.48593807220458984,
                                               26.032129764556885),
        'test_heteroatom_organics_CH3AlH2': (0.063932895660400391,
                                             5.3263344764709473),
        'test_heteroatom_organics_CH3AlHCH3': (0.94437003135681152,
                                               43.794517517089844),
        'test_heteroatom_organics_CH3BH2': (0.093707084655761719, 6.960831880569458),
        'test_heteroatom_organics_CH3BHCH3': (1.1862549781799316, 53.280463457107544),
        'test_heteroatom_organics_CH3NH2': (0.16070890426635742, 8.9985096454620361),
        'test_heteroatom_organics_CH3NHCH3': (0.37237715721130371,
                                              19.095346450805664),
        'test_heteroatom_organics_CH3OCH3': (0.10467100143432617, 7.166569709777832),
        'test_heteroatom_organics_CH3OH': (0.076311826705932617, 6.3633959293365479),
        'test_heteroatom_organics_CH3PH2': (0.31078290939331055, 15.717308521270752),
        'test_heteroatom_organics_CH3PHCH3': (0.25824618339538574,
                                              12.029121398925781),
        'test_heteroatom_organics_CH3SCH3': (0.58856391906738281, 30.400774478912354),
        'test_heteroatom_organics_CH3SH': (0.19000887870788574, 9.5359275341033936),
        'test_heteroatom_organics_CH3SiH2CH3': (0.46847820281982422,
                                                24.607746601104736),
        'test_heteroatom_organics_CH3SiH3': (0.44934988021850586, 23.220118522644043),
        'test_heteroatom_organics_C_CH3_3_AlH2': (0.73638701438903809,
                                                  38.47082257270813),
        'test_heteroatom_organics_C_CH3_3_BH2': (0.67547917366027832,
                                                 34.183696746826172),
        'test_heteroatom_organics_C_CH3_3_NH2': (0.70981407165527344,
                                                 36.289915800094604),
        'test_heteroatom_organics_C_CH3_3_OH': (0.46898913383483887,
                                                25.076735734939575),
        'test_heteroatom_organics_C_CH3_3_PH2': (0.78450989723205566,
                                                 39.255332469940186),
        'test_heteroatom_organics_C_CH3_3_SH': (0.55492591857910156,
                                                29.248791694641113),
        'test_heteroatom_organics_C_CH3_3_SiH3': (0.4078528881072998,
                                                  21.067863464355469),
        'test_heteroatom_organics_N_ADAM_C3v': (0.28158283233642578,
                                                13.664069890975952),
        'test_heteroatom_organics_P_ADAM_C3v': (0.3752140998840332,
                                                19.470560550689697),
        'test_heteroatom_organics_SiH_ADAM_C3v': (0.45937895774841309,
                                                  23.679497480392456),
        'test_minimize_0001': (0.65768218040466309, 33.508217573165894),
        'test_minimize_0002': (0.0, 2.8426270484924316),
        'test_minimize_0003': (0.0, 2.8426270484924316),
        'test_minimize_0004': (0.0, 2.8426270484924316),
        'test_minimize_0005': (0.52554893493652344, 27.052543640136719),
        'test_minimize_0006': (0.0, 2.8426270484924316),
        'test_minimize_0007': (0.0, 2.8426270484924316),
        'test_minimize_0008': (0.89502501487731934, 41.91957950592041),
        'test_minimize_0009': (0.2143549919128418, 9.9494695663452148),
        'test_minimize_0010': (0.055970907211303711, 3.144916296005249),
        'test_minimize_0011': (0.54357409477233887, 27.596117734909058),
        'test_minimize_0012': (0.33484196662902832, 16.992081165313721),
        'test_minimize_0013': (0.050697088241577148, 2.982783317565918),
        'test_minimize_h2': (0.049787998199462891, 2.9320862293243408),
        'test_pyrex_dynamics': (0.21957492828369141, 10.604136228561401),
        'test_pyrex_minH2': (0.039671182632446289, 2.8822982311248779),
        'test_pyrex_minimize0001': (0.46945595741271973, 25.546191692352295),
        'test_pyrex_unittests': (2.8426270484924316, 2.8426270484924316),
        'test_rigid_organics_C10H12': (0.21721792221069336, 10.166687488555908),
        'test_rigid_organics_C10H14': (0.36105203628540039, 18.72296929359436),
        'test_rigid_organics_C14H20': (0.56341886520385742, 29.812210559844971),
        'test_rigid_organics_C14H24': (2.7650349140167236, 78.799246311187744),
        'test_rigid_organics_C2H6': (0.19918704032897949, 9.735114574432373),
        'test_rigid_organics_C3H6': (0.078390836715698242, 6.4417867660522461),
        'test_rigid_organics_C3H8': (0.23208117485046387, 11.279950380325317),
        'test_rigid_organics_C4H8': (0.14832496643066406, 8.6855347156524658),
        'test_rigid_organics_C6H10': (0.26274895668029785, 12.291870355606079),
        'test_rigid_organics_C8H14': (1.0962879657745361, 50.938097476959229),
        'test_rigid_organics_C8H8': (0.11592411994934082, 7.7258720397949219),
        'test_rigid_organics_CH4': (0.060283184051513672, 4.2758197784423828),
        'test_singlebond_stretch_Cl_AlH2': (0.061307907104492188, 4.8833048343658447),
        'test_singlebond_stretch_Cl_BH2': (0.063423871994018555, 5.135122537612915),
        'test_singlebond_stretch_Cl_CH3': (0.059573173522949219, 3.7362344264984131),
        'test_singlebond_stretch_Cl_Cl': (0.059303045272827148, 3.5576772689819336),
        'test_singlebond_stretch_Cl_F': (0.058634042739868164, 3.2620124816894531),
        'test_singlebond_stretch_Cl_NH2': (0.060225009918212891, 4.2155365943908691),
        'test_singlebond_stretch_Cl_OH': (0.059254884719848633, 3.4391021728515625),
        'test_singlebond_stretch_Cl_PH2': (0.060878992080688477, 4.6998758316040039),
        'test_singlebond_stretch_Cl_SH': (0.059272050857543945, 3.4983742237091064),
        'test_singlebond_stretch_Cl_SiH3': (0.059774160385131836, 3.9154026508331299),
        'test_singlebond_stretch_F_AlH2': (0.064551115036010742, 5.455256462097168),
        'test_singlebond_stretch_F_BH2': (0.062253952026367188, 4.9455587863922119),
        'test_singlebond_stretch_F_CH3': (0.05990910530090332, 4.0352096557617188),
        'test_singlebond_stretch_F_F': (0.059068918228149414, 3.3798472881317139),
        'test_singlebond_stretch_F_NH2': (0.060482025146484375, 4.3967528343200684),
        'test_singlebond_stretch_F_OH': (0.059668064117431641, 3.7959024906158447),
        'test_singlebond_stretch_F_PH2': (0.06052398681640625, 4.5177936553955078),
        'test_singlebond_stretch_F_SH': (0.059530019760131836, 3.6766612529754639),
        'test_singlebond_stretch_F_SiH3': (0.060665130615234375, 4.6389968395233154),
        'test_singlebond_stretch_H2Al_AlH2': (0.074005126953125, 6.2124252319335938),
        'test_singlebond_stretch_H2Al_CH3': (0.071208953857421875,
                                             6.0660891532897949),
        'test_singlebond_stretch_H2Al_SiH3': (0.072330951690673828,
                                              6.1384201049804688),
        'test_singlebond_stretch_H2B_AlH2': (0.070688009262084961, 5.994880199432373),
        'test_singlebond_stretch_H2B_BH2': (0.080048084259033203, 6.5218348503112793),
        'test_singlebond_stretch_H2B_CH3': (0.1141200065612793, 7.6099479198455811),
        'test_singlebond_stretch_H2B_NH2': (0.69653701782226562, 34.880233764648438),
        'test_singlebond_stretch_H2B_PH2': (0.065023899078369141, 5.5849902629852295),
        'test_singlebond_stretch_H2B_SiH3': (0.087718963623046875,
                                             6.7786328792572021),
        'test_singlebond_stretch_H2N_AlH2': (0.12086105346679688, 7.8467330932617188),
        'test_singlebond_stretch_H2N_CH3': (0.22409892082214355, 11.047869205474854),
        'test_singlebond_stretch_H2N_NH2': (0.14631295204162598, 8.5372097492218018),
        'test_singlebond_stretch_H2N_PH2': (0.15226602554321289, 8.8378007411956787),
        'test_singlebond_stretch_H2N_SiH3': (0.069988012313842773,
                                             5.9241921901702881),
        'test_singlebond_stretch_H2P_AlH2': (0.066989898681640625,
                                             5.7189431190490723),
        'test_singlebond_stretch_H2P_CH3': (0.11021709442138672, 7.3825399875640869),
        'test_singlebond_stretch_H2P_PH2': (0.064709901809692383, 5.5199663639068604),
        'test_singlebond_stretch_H2P_SiH3': (0.064370870590209961,
                                             5.3907053470611572),
        'test_singlebond_stretch_H3C_CH3': (0.074658870697021484, 6.2870841026306152),
        'test_singlebond_stretch_H3C_SiH3': (0.082396984100341797,
                                             6.6042318344116211),
        'test_singlebond_stretch_H3Si_SiH3': (0.066962957382202148,
                                              5.6519532203674316),
        'test_singlebond_stretch_HO_AlH2': (0.063498973846435547, 5.1986215114593506),
        'test_singlebond_stretch_HO_BH2': (0.314849853515625, 16.657239198684692),
        'test_singlebond_stretch_HO_CH3': (0.10575318336486816, 7.2723228931427002),
        'test_singlebond_stretch_HO_NH2': (0.10106682777404785, 7.0618987083435059),
        'test_singlebond_stretch_HO_OH': (0.14296197891235352, 8.2454519271850586),
        'test_singlebond_stretch_HO_PH2': (0.062848806381225586, 5.0084075927734375),
        'test_singlebond_stretch_HO_SiH3': (0.068184137344360352, 5.8542041778564453),
        'test_singlebond_stretch_HS_AlH2': (0.41944408416748047, 21.902604579925537),
        'test_singlebond_stretch_HS_BH2': (0.31242585182189941, 16.029734373092651),
        'test_singlebond_stretch_HS_CH3': (0.067076921463012695, 5.786020040512085),
        'test_singlebond_stretch_HS_NH2': (0.28496885299682617, 14.232771635055542),
        'test_singlebond_stretch_HS_OH': (0.06089019775390625, 4.7607660293579102),
        'test_singlebond_stretch_HS_PH2': (0.061230897903442383, 4.8219969272613525),
        'test_singlebond_stretch_HS_SH': (0.060516834259033203, 4.4572696685791016),
        'test_singlebond_stretch_HS_SiH3': (0.25187897682189941, 11.770875215530396),
        'test_singlebond_stretch_H_AlH2': (0.059977054595947266, 4.095186710357666),
        'test_singlebond_stretch_H_BH2': (0.060451030731201172, 4.336270809173584),
        'test_singlebond_stretch_H_CH3': (0.060538053512573242, 4.5783317089080811),
        'test_singlebond_stretch_H_Cl': (0.058765888214111328, 3.3207783699035645),
        'test_singlebond_stretch_H_F': (0.058462142944335938, 3.203378438949585),
        'test_singlebond_stretch_H_H': (0.059453964233398438, 3.617131233215332),
        'test_singlebond_stretch_H_NH2': (0.05972599983215332, 3.855628490447998),
        'test_singlebond_stretch_H_OH': (0.059897899627685547, 3.9753005504608154),
        'test_singlebond_stretch_H_PH2': (0.063291072845458984, 5.0716986656188965),
        'test_singlebond_stretch_H_SH': (0.063780069351196289, 5.2624015808105469),
        'test_singlebond_stretch_H_SiH3': (0.060124874114990234, 4.1553115844726562)
        }
    
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
    def test_dynamics_0002(self):
        # ground, thermostat, and thermometer test
        DynamicsTest(dir="dynamics", test="0002",
                     simopts=("--num-frames=100",
                              "--temperature=300",
                              "--iters-per-frame=10",
                              "--dump-as-text",
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
                s = sim.Dynamics("tests/dynamics/test_0002.mmp")
                s.NumFrames = 100
                s.PrintFrameNums = 0
                s.IterPerFrame = 10
                s.Temperature = 300
                s.go()
                assert not sim.isFileAscii("tests/dynamics/test_0002.dpb")
        Foo("test_pyrex_dynamics")

    def test_pyrex_unittests(self):
        class Foo(PyrexTest):
            def run(self):
                import sim
                sim.test()
        Foo("test_pyrex_unittests")

###########################################

if __name__ == "__main__":

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
        global Tests, PyrexTests
        Tests = PyrexTests
    def loose(x):
        """Loosen tolerances on length and angle comparisons.
        """
        global LOOSE_TOLERANCES
        LOOSE_TOLERANCES = True
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

    def help(x):
        """print help information
        """
        print __doc__
        global options
        for opt in options:
            print opt.__name__ + "\n        " + opt.__doc__
        sys.exit(0)

    options = (md5check,
               lengths_angles,
               structcompare,
               time_limit,
               pyrex,
               loose,
               test_dir,
               list_everything,
               generate,
               debug,
               time_only,
               keep,
               todo_tasks,
               verbose_failures,
               help)

    # Default behavior is to do all the tests, including the slow ones,
    # with loose tolerances, so things pass
    defaultArgs = ("lengths_angles", "loose")

    args = sys.argv[1:]
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
    if LOOSE_TOLERANCES:
        LENGTH_TOLERANCE = 0.15    # angstroms
        ANGLE_TOLERANCE = 15       # degrees
    if TEST_DIR != None:
        attrs = dir(Tests)
        for attr in attrs:
            if attr.startswith("test_") and \
               not attr.startswith("test_" + TEST_DIR):
                def passAutomatically(self):
                    pass
                setattr(Tests, attr, passAutomatically)

    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

    if TIME_ONLY:
        lst = [ ]
        dct = { }
        for name in testTimes.keys():
            t = testTimes[name]
            lst.append([t, name])
        def sortfunc(x, y):
            if x[1] == "test_pyrex_unittests":
                return -1
            elif y[1] == "test_pyrex_unittests":
                return 1
            else: return cmp(x[0], y[0])
        lst.sort(sortfunc)
        total = 0.0
        for t, name in lst:
            total = total + t
            dct[name] = (t, total)
        import pprint
        pprint.pprint(dct)
    else:
        print len(Tests.RANKED_BY_SPEED) - testsSkipped, "tests really done,",
        print testsSkipped, "tests skipped"
