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

def rmtreeSafe(dir):
    # platform-independent 'rm -rf'
    try: shutil.rmtree(dir)
    except OSError, e: pass

class BaseTest:
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

        if not TIME_ONLY:
            t, total = Tests.RANKED_BY_SPEED[methodname]
            if total > TIME_LIMIT:
                global testsSkipped
                testsSkipped += 1
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
            self.startTime = time.time()
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
        if TIME_ONLY:
            global testTimes
            startTime, finishTime = self.startTime, time.time()
            testTimes[self.methodname] = finishTime - startTime
        elif MD5_CHECKS:
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

class NullTest(BaseTest):
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
    # Re-generate this with "python tests.py time_only"
    RANKED_BY_SPEED = {
        'test_amino_acids_ala_l_aminoacid': (8.4515881538391113, 292.8698992729187),
        'test_amino_acids_arg_l_aminoacid': (16.897550821304321, 454.8538236618042),
        'test_amino_acids_asn_l_aminoacid': (10.056391954421997, 331.14827513694763),
        'test_amino_acids_asp_l_aminoacid': (12.478914976119995, 422.92954587936401),
        'test_amino_acids_cys_l_aminoacid': (10.552248001098633, 341.70052313804626),
        'test_amino_acids_gln_l_aminoacid': (7.2884318828582764, 253.37105631828308),
        'test_amino_acids_glu_l_aminoacid': (18.545698881149292, 490.9207603931427),
        'test_amino_acids_gly_l_aminoacid': (6.2237210273742676, 192.34123921394348),
        'test_amino_acids_his_l_aminoacid': (5.7051258087158203, 168.16432523727417),
        'test_amino_acids_ile_l_aminoacid': (7.1139130592346191, 246.0826244354248),
        'test_amino_acids_leu_l_aminoacid': (9.8509140014648438, 311.21676707267761),
        'test_amino_acids_lys_l_aminoacid': (4.6640949249267578, 140.85138630867004),
        'test_amino_acids_met_l_aminoacid': (7.4319419860839844, 268.12668037414551),
        'test_amino_acids_phe_l_aminoacid': (0.054956912994384766,
                                             0.30835819244384766),
        'test_amino_acids_pro_l_aminoacid': (4.5057921409606934, 122.52460861206055),
        'test_amino_acids_ser_l_aminoacid': (10.827859878540039, 352.5283830165863),
        'test_amino_acids_thr_l_aminoacid': (4.0716040134429932, 118.01881647109985),
        'test_amino_acids_tyr_l_aminoacid': (17.521237850189209, 472.37506151199341),
        'test_amino_acids_val_l_aminoacid': (7.100614070892334, 238.96871137619019),
        'test_dynamics_0001': (0.0, 0.0),
        'test_dynamics_0002': (0.28501796722412109, 1.8783180713653564),
        'test_floppy_organics_C2H6': (0.99122405052185059, 16.262491703033447),
        'test_floppy_organics_C3H8': (3.969290018081665, 105.89462566375732),
        'test_floppy_organics_C4H10a': (1.0303390026092529, 18.287234783172607),
        'test_floppy_organics_C4H10b': (6.1513998508453369, 186.11751818656921),
        'test_floppy_organics_C4H10c': (3.4591710567474365, 98.314822673797607),
        'test_floppy_organics_C4H8': (0.48324894905090332, 4.4755322933197021),
        'test_floppy_organics_C5H10': (11.981503963470459, 410.45063090324402),
        'test_floppy_organics_C5H12a': (1.4010508060455322, 34.388141870498657),
        'test_floppy_organics_C5H12b': (4.5366709232330322, 127.06127953529358),
        'test_floppy_organics_C5H12c': (5.5371201038360596, 162.45919942855835),
        'test_floppy_organics_C5H12d': (2.0090811252593994, 53.655117273330688),
        'test_floppy_organics_C5H12e': (9.8751161098480225, 321.09188318252563),
        'test_floppy_organics_C6H12a': (1.3278310298919678, 30.313368082046509),
        'test_floppy_organics_C6H12b': (0.88967704772949219, 12.365112543106079),
        'test_floppy_organics_C6H14a': (2.2347090244293213, 62.0400550365448),
        'test_floppy_organics_C6H14b': (1.7417080402374268, 44.11979603767395),
        'test_floppy_organics_C6H14c': (1.1762402057647705, 25.200761079788208),
        'test_floppy_organics_C6H14d': (11.932842969894409, 386.49255299568176),
        'test_floppy_organics_C6H14e': (2.2804429531097412, 64.320497989654541),
        'test_floppy_organics_C6H14f': (8.2306308746337891, 284.41831111907959),
        'test_floppy_organics_C7H14a': (2.7018167972564697, 82.040554761886597),
        'test_floppy_organics_C7H14b': (6.0212090015411377, 179.96611833572388),
        'test_floppy_organics_C7H14c': (10.990864038467407, 363.51924705505371),
        'test_floppy_organics_CH4': (0.054437160491943359, 0.25340127944946289),
        'test_heteroatom_organics_ADAM_AlH2_Cs': (1.2039239406585693,
                                                  26.404685020446777),
        'test_heteroatom_organics_ADAM_BH2': (3.3327479362487793, 91.417218685150146),
        'test_heteroatom_organics_ADAM_Cl_c3v': (0.97649097442626953,
                                                 15.271267652511597),
        'test_heteroatom_organics_ADAM_F_c3v': (0.81246709823608398,
                                                9.7333366870880127),
        'test_heteroatom_organics_ADAM_NH2_Cs': (6.7423648834228516,
                                                 224.78610825538635),
        'test_heteroatom_organics_ADAM_OH_Cs': (1.7084159851074219,
                                                42.378087997436523),
        'test_heteroatom_organics_ADAM_PH2_Cs': (6.3031060695648193,
                                                 204.93387937545776),
        'test_heteroatom_organics_ADAM_SH_Cs': (0.99440407752990723,
                                                17.256895780563354),
        'test_heteroatom_organics_ADAM_SiH3_C3v': (44.870447874069214,
                                                   535.79120826721191),
        'test_heteroatom_organics_ADAMframe_AlH_Cs': (2.0612678527832031,
                                                      59.805346012115479),
        'test_heteroatom_organics_ADAMframe_BH_Cs': (2.5925590991973877,
                                                     74.017199039459229),
        'test_heteroatom_organics_ADAMframe_NH_Cs': (0.60892510414123535,
                                                     6.6141974925994873),
        'test_heteroatom_organics_ADAMframe_O_Cs': (1.3116340637207031,
                                                    28.985537052154541),
        'test_heteroatom_organics_ADAMframe_PH_Cs': (1.3447470664978027,
                                                     32.987091064453125),
        'test_heteroatom_organics_ADAMframe_S_Cs': (0.74076104164123535,
                                                    7.3549585342407227),
        'test_heteroatom_organics_ADAMframe_SiH2_c2v': (1.9843220710754395,
                                                        51.646036148071289),
        'test_heteroatom_organics_Al_ADAM_C3v': (3.0713629722595215,
                                                 88.084470748901367),
        'test_heteroatom_organics_B_ADAM_C3v': (1.3289759159088135,
                                                31.642343997955322),
        'test_heteroatom_organics_C3H6AlH': (0.79894709587097168, 8.9208695888519287),
        'test_heteroatom_organics_C3H6BH': (0.39984798431396484, 2.6626601219177246),
        'test_heteroatom_organics_C3H6NH': (0.2454218864440918, 1.3251669406890869),
        'test_heteroatom_organics_C3H6O': (0.23571491241455078, 1.0797450542449951),
        'test_heteroatom_organics_C3H6PH': (0.48624897003173828, 5.4468502998352051),
        'test_heteroatom_organics_C3H6S': (0.23258590698242188, 0.84403014183044434),
        'test_heteroatom_organics_C3H6SiH2': (0.76696395874023438, 8.121922492980957),
        'test_heteroatom_organics_C4H8AlH': (1.2692179679870605, 27.673902988433838),
        'test_heteroatom_organics_C4H8BH': (4.5707628726959229, 136.18729138374329),
        'test_heteroatom_organics_C4H8NH': (11.040462970733643, 374.55971002578735),
        'test_heteroatom_organics_C4H8O': (8.4959537982940674, 301.36585307121277),
        'test_heteroatom_organics_C4H8PH': (2.499208927154541, 71.424639940261841),
        'test_heteroatom_organics_C4H8S': (2.291511058807373, 66.612009048461914),
        'test_heteroatom_organics_C4H8SiH2': (0.87538981437683105,
                                              11.475435495376587),
        'test_heteroatom_organics_C5H10AlH': (2.0489368438720703, 57.744078159332275),
        'test_heteroatom_organics_C5H10BH': (1.6558411121368408, 40.669672012329102),
        'test_heteroatom_organics_C5H10NH': (0.9700310230255127, 14.294776678085327),
        'test_heteroatom_organics_C5H10O': (1.5707600116729736, 37.374046802520752),
        'test_heteroatom_organics_C5H10PH': (0.38449406623840332, 2.2628121376037598),
        'test_heteroatom_organics_C5H10S': (0.47199916839599609, 3.9922833442687988),
        'test_heteroatom_organics_C5H10SiH2': (1.1684699058532715,
                                               24.024520874023438),
        'test_heteroatom_organics_CH3AlH2': (2.972553014755249, 85.013107776641846),
        'test_heteroatom_organics_CH3AlHCH3': (1.9149010181427002, 49.66171407699585),
        'test_heteroatom_organics_CH3BH2': (3.6105129718780518, 101.92533564567566),
        'test_heteroatom_organics_CH3BHCH3': (5.7805840969085693, 173.94490933418274),
        'test_heteroatom_organics_CH3NH2': (0.95963311195373535, 13.324745655059814),
        'test_heteroatom_organics_CH3NHCH3': (3.4384329319000244, 94.855651617050171),
        'test_heteroatom_organics_CH3OCH3': (5.0952639579772949, 145.94665026664734),
        'test_heteroatom_organics_CH3OH': (0.26813316345214844, 1.5933001041412354),
        'test_heteroatom_organics_CH3PH2': (2.6964559555053711, 79.338737964630127),
        'test_heteroatom_organics_CH3PHCH3': (0.43955302238464355,
                                              3.5202841758728027),
        'test_heteroatom_organics_CH3SCH3': (0.55842208862304688, 6.005272388458252),
        'test_heteroatom_organics_CH3SH': (0.86670899391174316, 10.600045680999756),
        'test_heteroatom_organics_CH3SiH2CH3': (1.1079399585723877,
                                                19.395174741744995),
        'test_heteroatom_organics_CH3SiH3': (4.0488529205322266, 113.94721245765686),
        'test_heteroatom_organics_C_CH3_3_AlH2': (11.976573944091797,
                                                  398.46912693977356),
        'test_heteroatom_organics_C_CH3_3_BH2': (2.3134219646453857,
                                                 68.9254310131073),
        'test_heteroatom_organics_C_CH3_3_NH2': (6.5994019508361816,
                                                 218.0437433719635),
        'test_heteroatom_organics_C_CH3_3_OH': (4.0037338733673096,
                                                109.89835953712463),
        'test_heteroatom_organics_C_CH3_3_PH2': (7.3236820697784424,
                                                 260.69473838806152),
        'test_heteroatom_organics_C_CH3_3_SH': (2.0400240421295166,
                                                55.695141315460205),
        'test_heteroatom_organics_C_CH3_3_SiH3': (4.5552489757537842,
                                                  131.61652851104736),
        'test_heteroatom_organics_N_ADAM_C3v': (1.1632251739501953,
                                                21.692574977874756),
        'test_heteroatom_organics_P_ADAM_C3v': (1.7552249431610107,
                                                45.875020980834961),
        'test_heteroatom_organics_SiH_ADAM_C3v': (1.8717920780181885,
                                                  47.746813058853149),
        'test_minimize_0001': (7.081989049911499, 231.86809730529785),
        'test_minimize_0002': (0.0, 0.0),
        'test_minimize_0003': (0.0, 0.0),
        'test_minimize_0004': (0.0, 0.0),
        'test_minimize_0005': (6.5104620456695557, 211.44434142112732),
        'test_minimize_0006': (0.0, 0.0),
        'test_minimize_0007': (0.0, 0.0),
        'test_minimize_0008': (5.4587171077728271, 151.40536737442017),
        'test_minimize_0009': (0.48506903648376465, 4.9606013298034668),
        'test_minimize_0010': (0.068049192428588867, 0.43266439437866211),
        'test_minimize_0011': (6.2895340919494629, 198.63077330589294),
        'test_minimize_0012': (5.516711950302124, 156.92207932472229),
        'test_minimize_0013': (0.05047297477722168, 0.19896411895751953),
        'test_minimize_h2': (0.049383163452148438, 0.098462104797363281),
        'test_rigid_organics_C10H12': (0.41807103157043457, 3.0807311534881592),
        'test_rigid_organics_C10H14': (1.4151449203491211, 35.803286790847778),
        'test_rigid_organics_C14H20': (1.6397840976715088, 39.013830900192261),
        'test_rigid_organics_C14H24': (15.026726961135864, 437.95627284049988),
        'test_rigid_organics_C2H6': (1.1634759902954102, 22.856050968170166),
        'test_rigid_organics_C3H6': (0.049078941345214844, 0.049078941345214844),
        'test_rigid_organics_C3H8': (2.6250829696655273, 76.642282009124756),
        'test_rigid_organics_C4H8': (0.05002903938293457, 0.14849114418029785),
        'test_rigid_organics_C6H10': (1.1341750621795654, 20.529349803924561),
        'test_rigid_organics_C8H14': (8.060999870300293, 276.1876802444458),
        'test_rigid_organics_C8H8': (0.17877984046936035, 0.61144423484802246),
        'test_rigid_organics_CH4': (0.056257009506225586, 0.36461520195007324)}

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


######################

class PyrexTests(unittest.TestCase):
    def test_minH2(self):
        import sim
        BASE = "tests/minimize/test_h2"
        lac = LengthAngleComparison(BASE + ".mmp")
        s = sim.Minimize(BASE + ".mmp")
        s.Temperature = 300
        s.go()
        lac.compare(BASE + ".xyz", BASE + ".xyzcmp",
                    LENGTH_TOLERANCE, ANGLE_TOLERANCE)
    def test_other(self):
        import sim
        BASE = "tests/minimize/test_0001"
        lac = LengthAngleComparison(BASE + ".mmp")
        s = sim.Minimize(BASE + ".mmp")
        s.Temperature = 300
        z = s.go()
        lac.compare(BASE + ".xyz", BASE + ".xyzcmp",
                    LENGTH_TOLERANCE, ANGLE_TOLERANCE)

class SlowPyrexTests(PyrexTests):
    def test_dynamics(self):
        import sim
        s = sim.Dynamics("tests/dynamics/test_0002.mmp")
        s.NumFrames = 10000
        s.PrintFrameNums = 0
        s.ItersPerFrame = 100
        s.Temperature = 300
        s.go()
        # creates file: tests/dynamics/test_0002.dpb
        # wouldn't it be nice to verify something? but what?
PyrexTests.slowVersion = SlowPyrexTests

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
            lst.append((t, name))
        lst.sort()
        total = 0.0
        for t, name in lst:
            total = total + t
            dct[name] = (t, total)
        import pprint
        pprint.pprint(dct)
    else:
        print testsSkipped, "tests skipped"
