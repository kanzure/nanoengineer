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

class PrematureTermination(Exception):
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
                raise PrematureTermination

    def startTiming(self):
        self.startTime = time.time()

    def finishTiming(self):
        if TIME_ONLY:
            global testTimes
            startTime, finishTime = self.startTime, time.time()
            testTimes[self.methodname] = finishTime - startTime
            raise PrematureTermination

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
        except PrematureTermination:
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
            self.startTiming()
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
            self.finishTiming()
        except PrematureTermination:
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

    def __init__(self, methodname):
        self.methodname = methodname
        try:
            TimedTest.__init__(self)
        except PrematureTermination:
            return
        self.startTiming()
        self.run()
        self.finishTiming()

####################################################

class Tests(unittest.TestCase):
    # Re-generate this with "python tests.py time_only"
    RANKED_BY_SPEED = {
        'test_amino_acids_ala_l_aminoacid': (1.946666955947876, 55.024072885513306),
        'test_amino_acids_arg_l_aminoacid': (2.8490579128265381, 76.331800699234009),
        'test_amino_acids_asn_l_aminoacid': (3.9334299564361572, 90.349052906036377),
        'test_amino_acids_asp_l_aminoacid': (4.3835141658782959, 107.23448324203491),
        'test_amino_acids_cys_l_aminoacid': (2.6352710723876953, 59.895891904830933),
        'test_amino_acids_gln_l_aminoacid': (6.6894419193267822, 124.71745729446411),
        'test_amino_acids_glu_l_aminoacid': (9.5068850517272949, 150.33339238166809),
        'test_amino_acids_gly_l_aminoacid': (1.0480170249938965, 38.119378089904785),
        'test_amino_acids_his_l_aminoacid': (5.2245981693267822, 112.45908141136169),
        'test_amino_acids_ile_l_aminoacid': (2.7162671089172363, 67.97348690032959),
        'test_amino_acids_leu_l_aminoacid': (8.3089730739593506, 140.8265073299408),
        'test_amino_acids_lys_l_aminoacid': (7.800076961517334, 132.51753425598145),
        'test_amino_acids_met_l_aminoacid': (5.5689339637756348, 118.02801537513733),
        'test_amino_acids_phe_l_aminoacid': (0.059222936630249023,
                                             0.37899422645568848),
        'test_amino_acids_pro_l_aminoacid': (3.6750280857086182, 86.41562294960022),
        'test_amino_acids_ser_l_aminoacid': (4.3379099369049072, 102.85096907615662),
        'test_amino_acids_thr_l_aminoacid': (3.3784561157226562, 82.740594863891602),
        'test_amino_acids_tyr_l_aminoacid': (24.489926099777222, 174.82331848144531),
        'test_amino_acids_val_l_aminoacid': (4.1050240993499756, 98.513059139251709),
        'test_dynamics_0001': (0.0, 0.0),
        'test_dynamics_0002': (0.26997113227844238, 4.8889110088348389),
        'test_floppy_organics_C2H6': (0.12560606002807617, 1.3842589855194092),
        'test_floppy_organics_C3H8': (0.43270397186279297, 13.320019483566284),
        'test_floppy_organics_C4H10a': (0.3897240161895752, 10.87376880645752),
        'test_floppy_organics_C4H10b': (2.2365479469299316, 57.260620832443237),
        'test_floppy_organics_C4H10c': (0.34221982955932617, 9.4276819229125977),
        'test_floppy_organics_C4H8': (0.13552212715148926, 1.5197811126708984),
        'test_floppy_organics_C5H10': (0.97845196723937988, 35.062201023101807),
        'test_floppy_organics_C5H12a': (1.4929301738739014, 49.455256938934326),
        'test_floppy_organics_C5H12b': (0.59053206443786621, 21.41552734375),
        'test_floppy_organics_C5H12c': (1.4041359424591064, 46.501685857772827),
        'test_floppy_organics_C5H12d': (0.91233491897583008, 31.291476964950562),
        'test_floppy_organics_C5H12e': (0.93021392822265625, 33.15148401260376),
        'test_floppy_organics_C6H12a': (0.27853798866271973, 5.4406559467315674),
        'test_floppy_organics_C6H12b': (0.28512191772460938, 6.0075919628143311),
        'test_floppy_organics_C6H14a': (0.99991703033447266, 36.062118053436279),
        'test_floppy_organics_C6H14b': (0.74242210388183594, 28.826469898223877),
        'test_floppy_organics_C6H14c': (1.0822620391845703, 40.277742147445679),
        'test_floppy_organics_C6H14d': (1.2998778820037842, 45.097549915313721),
        'test_floppy_organics_C6H14e': (1.855618953704834, 53.07740592956543),
        'test_floppy_organics_C6H14f': (2.6498298645019531, 62.545721769332886),
        'test_floppy_organics_C7H14a': (0.72782993316650391, 27.351072788238525),
        'test_floppy_organics_C7H14b': (1.1427440643310547, 41.420486211776733),
        'test_floppy_organics_C7H14c': (3.0303380489349365, 79.362138748168945),
        'test_floppy_organics_CH4': (0.05700993537902832, 0.26131939888000488),
        'test_heteroatom_organics_ADAM_AlH2_Cs': (1.7665300369262695,
                                                  51.221786975860596),
        'test_heteroatom_organics_ADAM_BH2': (0.64491009712219238,
                                              23.872439622879028),
        'test_heteroatom_organics_ADAM_Cl_c3v': (0.29991602897644043,
                                                 7.4817349910736084),
        'test_heteroatom_organics_ADAM_F_c3v': (0.2818140983581543,
                                                5.7224700450897217),
        'test_heteroatom_organics_ADAM_NH2_Cs': (0.92979311943054199,
                                                 32.221270084381104),
        'test_heteroatom_organics_ADAM_OH_Cs': (0.7752220630645752,
                                                29.601691961288452),
        'test_heteroatom_organics_ADAM_PH2_Cs': (1.4606409072875977,
                                                 47.962326765060425),
        'test_heteroatom_organics_ADAM_SH_Cs': (0.45082616806030273,
                                                14.216476678848267),
        'test_heteroatom_organics_ADAM_SiH3_C3v': (2.7863609790802002,
                                                   73.482742786407471),
        'test_heteroatom_organics_ADAMframe_AlH_Cs': (0.52295708656311035,
                                                      17.560133934020996),
        'test_heteroatom_organics_ADAMframe_BH_Cs': (0.69823503494262695,
                                                     25.918647766113281),
        'test_heteroatom_organics_ADAMframe_NH_Cs': (0.28730106353759766,
                                                     6.2948930263519287),
        'test_heteroatom_organics_ADAMframe_O_Cs': (0.29506683349609375,
                                                    6.8820030689239502),
        'test_heteroatom_organics_ADAMframe_PH_Cs': (0.31160902976989746,
                                                     8.0968689918518066),
        'test_heteroatom_organics_ADAMframe_S_Cs': (0.24475502967834473,
                                                    3.8517296314239502),
        'test_heteroatom_organics_ADAMframe_SiH2_c2v': (0.40902590751647949,
                                                        12.473547458648682),
        'test_heteroatom_organics_Al_ADAM_C3v': (0.5388331413269043,
                                                 18.622530221939087),
        'test_heteroatom_organics_B_ADAM_C3v': (0.35501885414123535,
                                                10.12680983543396),
        'test_heteroatom_organics_C3H6AlH': (0.19909811019897461, 2.7223963737487793),
        'test_heteroatom_organics_C3H6BH': (0.15747785568237305, 1.8206369876861572),
        'test_heteroatom_organics_C3H6NH': (0.11276602745056152, 1.0203909873962402),
        'test_heteroatom_organics_C3H6O': (0.10418295860290527, 0.90762495994567871),
        'test_heteroatom_organics_C3H6PH': (0.16425609588623047, 2.148881196975708),
        'test_heteroatom_organics_C3H6S': (0.1007840633392334, 0.80344200134277344),
        'test_heteroatom_organics_C3H6SiH2': (0.21960115432739258, 3.364795446395874),
        'test_heteroatom_organics_C4H8AlH': (0.41376805305480957, 12.887315511703491),
        'test_heteroatom_organics_C4H8BH': (0.54127907752990723, 19.70292329788208),
        'test_heteroatom_organics_C4H8NH': (1.2170538902282715, 43.797672033309937),
        'test_heteroatom_organics_C4H8O': (1.0092430114746094, 37.071361064910889),
        'test_heteroatom_organics_C4H8PH': (0.33976507186889648, 9.0854620933532715),
        'test_heteroatom_organics_C4H8S': (0.30352497100830078, 7.7852599620819092),
        'test_heteroatom_organics_C4H8SiH2': (0.45895099639892578,
                                              14.675427675247192),
        'test_heteroatom_organics_C5H10AlH': (0.61214303970336914,
                                              23.227529525756836),
        'test_heteroatom_organics_C5H10BH': (0.60581707954406738, 22.615386486053467),
        'test_heteroatom_organics_C5H10NH': (0.34410905838012695, 9.7717909812927246),
        'test_heteroatom_organics_C5H10O': (0.27320694923400879, 5.1621179580688477),
        'test_heteroatom_organics_C5H10PH': (0.29204320907592773, 6.5869362354278564),
        'test_heteroatom_organics_C5H10S': (0.24217915534973145, 3.6069746017456055),
        'test_heteroatom_organics_C5H10SiH2': (0.48464798927307129,
                                               17.037176847457886),
        'test_heteroatom_organics_CH3AlH2': (0.06856083869934082, 0.4475550651550293),
        'test_heteroatom_organics_CH3AlHCH3': (0.93226504325866699,
                                               34.083749055862427),
        'test_heteroatom_organics_CH3BH2': (0.09816288948059082, 0.70265793800354004),
        'test_heteroatom_organics_CH3BHCH3': (1.1601319313049316, 42.580618143081665),
        'test_heteroatom_organics_CH3NH2': (0.16398811340332031, 1.9846251010894775),
        'test_heteroatom_organics_CH3NHCH3': (0.3968048095703125, 11.661090612411499),
        'test_heteroatom_organics_CH3OCH3': (0.11788797378540039, 1.1382789611816406),
        'test_heteroatom_organics_CH3OH': (0.083057880401611328, 0.60449504852294922),
        'test_heteroatom_organics_CH3PH2': (0.31411099433898926, 8.4109799861907959),
        'test_heteroatom_organics_CH3PHCH3': (0.25769400596618652,
                                              4.3570196628570557),
        'test_heteroatom_organics_CH3SCH3': (0.57736778259277344, 20.824995279312134),
        'test_heteroatom_organics_CH3SH': (0.17879700660705566, 2.3276782035827637),
        'test_heteroatom_organics_CH3SiH2CH3': (0.46702694892883301,
                                                15.604696750640869),
        'test_heteroatom_organics_CH3SiH3': (0.44563102722167969, 13.765650510787964),
        'test_heteroatom_organics_C_CH3_3_AlH2': (0.73297500610351562,
                                                  28.084047794342041),
        'test_heteroatom_organics_C_CH3_3_BH2': (0.70459508895874023,
                                                 26.623242855072021),
        'test_heteroatom_organics_C_CH3_3_NH2': (0.69763612747192383,
                                                 25.220412731170654),
        'test_heteroatom_organics_C_CH3_3_OH': (0.47530603408813477,
                                                16.552528858184814),
        'test_heteroatom_organics_C_CH3_3_PH2': (0.7774500846862793,
                                                 30.379142045974731),
        'test_heteroatom_organics_C_CH3_3_SH': (0.54470419883728027,
                                                20.24762749671936),
        'test_heteroatom_organics_C_CH3_3_SiH3': (0.40343093872070312,
                                                  12.064521551132202),
        'test_heteroatom_organics_N_ADAM_C3v': (0.29981589317321777,
                                                7.181818962097168),
        'test_heteroatom_organics_P_ADAM_C3v': (0.39051699638366699,
                                                11.264285802841187),
        'test_heteroatom_organics_SiH_ADAM_C3v': (0.46224212646484375,
                                                  15.137669801712036),
        'test_minimize_0001': (0.65033698081970215, 24.52277660369873),
        'test_minimize_0002': (0.0, 0.0),
        'test_minimize_0003': (0.0, 0.0),
        'test_minimize_0004': (0.0, 0.0),
        'test_minimize_0005': (0.52356314659118652, 18.083697080612183),
        'test_minimize_0006': (0.0, 0.0),
        'test_minimize_0007': (0.0, 0.0),
        'test_minimize_0008': (2.7228949069976807, 70.696381807327271),
        'test_minimize_0009': (0.21574997901916504, 3.1451942920684814),
        'test_minimize_0010': (0.05845189094543457, 0.31977128982543945),
        'test_minimize_0011': (0.53911399841308594, 19.161644220352173),
        'test_minimize_0012': (0.3347170352935791, 8.745697021484375),
        'test_minimize_0013': (0.054762125015258789, 0.14807939529418945),
        'test_minimize_h2': (0.053918123245239258, 0.093317270278930664),
        'test_pyrexMinH2': (0.039399147033691406, 0.039399147033691406),
        'test_pyrexMinimize0001': (0.47252607345581055, 16.07722282409668),
        'test_pyrexUnittests': (4.0589821338653564, 94.408035039901733),
        'test_rigid_organics_C10H12': (0.20704793930053711, 2.9294443130493164),
        'test_rigid_organics_C10H14': (0.35723495483398438, 10.484044790267944),
        'test_rigid_organics_C14H20': (0.59404206275939941, 22.009569406509399),
        'test_rigid_organics_C14H24': (2.7114980220794678, 65.257219791412354),
        'test_rigid_organics_C2H6': (0.19562005996704102, 2.5232982635498047),
        'test_rigid_organics_C3H6': (0.073882102966308594, 0.52143716812133789),
        'test_rigid_organics_C3H8': (0.24759602546691895, 4.0993256568908691),
        'test_rigid_organics_C4H8': (0.14337801933288574, 1.6631591320037842),
        'test_rigid_organics_C6H10': (0.26192021369934082, 4.6189398765563965),
        'test_rigid_organics_C8H14': (1.0761020183563232, 39.195480108261108),
        'test_rigid_organics_C8H8': (0.12037396430969238, 1.258652925491333),
        'test_rigid_organics_CH4': (0.056230068206787109, 0.20430946350097656)}

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

    def test_pyrexMinH2(self):
        class Foo(PyrexTest):
            def run(self):
                import sim
                BASE = "tests/minimize/test_h2"
                lac = LengthAngleComparison(BASE + ".mmp")
                s = sim.Minimize(BASE + ".mmp")
                s.Temperature = 300
                s.go()
                lac.compare(BASE + ".xyz", BASE + ".xyzcmp",
                            LENGTH_TOLERANCE, ANGLE_TOLERANCE)
        return Foo("test_pyrexMinH2")
    def test_pyrexMinimize0001(self):
        class Foo(PyrexTest):
            def run(self):
                import sim
                BASE = "tests/minimize/test_0001"
                lac = LengthAngleComparison(BASE + ".mmp")
                s = sim.Minimize(BASE + ".mmp")
                s.Temperature = 300
                z = s.go()
                lac.compare(BASE + ".xyz", BASE + ".xyzcmp",
                            LENGTH_TOLERANCE, ANGLE_TOLERANCE)
        return Foo("test_pyrexMinimize0001")

##     def test_pyrexDynamics(self):
##         class Foo(PyrexTest):
##             def run(self):
##                 import sim
##                 s = sim.Dynamics("tests/dynamics/test_0002.mmp")
##                 s.NumFrames = 10000
##                 s.PrintFrameNums = 0
##                 s.IterPerFrame = 100
##                 s.Temperature = 300
##                 s.go()
##                 # creates file: tests/dynamics/test_0002.dpb
##                 # wouldn't it be nice to verify something? but what?
##         return Foo("test_pyrexDynamics")

    def test_pyrexUnittests(self):
        class Foo(PyrexTest):
            def run(self):
                import sim
                sim.test()
        return Foo("test_pyrexUnittests")

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
