#!/usr/bin/python

import os
import sys
import string
import shutil
import unittest
import md5
import subprocess

os.system("make simulator")

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
MD5_CHECKS_ONLY = True
GENERATE = False
KEEPRESULTS = False

class BaseTest:
    DEFAULT_INPUTS = ( )  # in addition to xxx.mmp
    DEFAULT_SIMOPTS = ( )
    DEFAULT_OUTPUTS = ( )  # in addition to stdout, stderr

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
        self.basename = os.sep.join([os.getcwd(), "tests",
                                     dirname, testname])

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
            if "xyzcmp" in self.inputs:
                if DEBUG > 0:
                    print ("copy " + self.testname + ".xyz to " +
                           self.basename + ".xyzcmp")
                shutil.copy(self.testname + ".xyz",
                            self.basename + ".xyzcmp")
            return
        if MD5_CHECKS_ONLY:
            inf = open(self.basename + ".md5sums")
            for line in inf.readlines():
                fname, sum = line.split()
                realsum = md5sum(fname)
                if realsum != sum:
                    print "Problem with " + self.basename + " " + fname
                assert realsum == sum
            inf.close()
        else:
            """This will be used for cases where we want to permit
            approximate matches, basically either XYZ positions, or
            sets of bonds and angles, or whole trajectories. We'll
            probably only update this when we get new data from
            Damian, or change approximation methods.
            """
            if "xyzcmp" in self.inputs:
                xyzcmp = open(self.testname + ".xyzcmp")
                xyz = open(self.testname + ".xyz")
                # number of atoms should be the same
                natoms = string.atoi(xyzcmp.readline().strip())
                natoms2 = string.atoi(xyz.readline().strip())
                assert natoms == natoms2
                # ignore RMS for now
                xyzcmp.readline(), xyz.readline()
                for i in range(natoms):
                    elem1, x1, y1, z1 = xyzcmp.readline().split()
                    x1, y1, z1 = map(string.atof, (x1, y1, z1))
                    elem2, x2, y2, z2 = xyz.readline().split()
                    x2, y2, z2 = map(string.atof, (x2, y2, z2))
                    dist = ((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2) ** .5
                    assert dist < 0.5
            # TODO should we check other things in this case?


#########################################

class PassFailTest(BaseTest):
    pass

class MinimizeTest(PassFailTest):
    DEFAULT_SIMOPTS = ("--minimize",
                       "--dump-as-text")
    DEFAULT_OUTPUTS = ("xyz",)

class StructureTest(MinimizeTest):
    DEFAULT_INPUTS = ("xyzcmp",)
    DEFAULT_OUTPUTS = ("trc", "xyz")

class DynamicsTest(StructureTest):
    DEFAULT_INPUTS = ( )
    DEFAULT_SIMOPTS = ("--dump-as-text",)
    DEFAULT_OUTPUTS = ("trc", "xyz")

####################################################
# Everything currently living in a "*.test" file can
# go here, and become more legible.

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
        MD5_CHECKS_ONLY = False
    if "slow" in sys.argv[1:]:
        Tests = SlowTests
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
