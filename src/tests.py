#!/usr/bin/python

import os
import sys
import shutil
import unittest
from subprocess import Popen

os.system("make simulator")

FAIL_UNIMPLEMENTED_TESTS = False
DEBUG = False
SLOW_TESTS = False

class FailTest:

    def __init__(self, basename, simopts,
                 inputs=("mmp",), outputs=()):
        self.basename = basename
        self.inputs = inputs
        self.outputs = outputs  # not using this yet
        self.runInSandbox(simopts)
        assert self.exitvalue == 0

    def runInSandbox(self, opts):
        # Run the simulator in sim/src/tmp.
        tmpdir = "tmp"
        try:
            shutil.rmtree(tmpdir)
        except OSError, e:
            assert e.args[0] == 2
        os.mkdir(tmpdir)
        # Copy the input files into the tmp directory.
        shutil.copy("simulator", tmpdir)
        for ext in self.inputs:
            shutil.copy(self.basename + "." + ext, tmpdir)
        # Go into the tmp directory and run the simulator.
        here = os.getcwd()
        os.chdir(tmpdir)
        cmdline = ("./simulator",) + opts
        stdout = open("stdout", "w")
        stderr = open("stderr", "w")
        if DEBUG: print cmdline
        p = Popen(cmdline, stdout=stdout, stderr=stderr)
        self.exitvalue = p.wait()
        stdout.close()
        stderr.close()
        self.stdout = open("stdout").read()
        self.stderr = open("stderr").read()
        if DEBUG:
            print ("******** " + self.basename + " ******** " +
                   repr(self.exitvalue) + " ********")
            for f in os.listdir("."):
                if f != "simulator":
                    print "---- " + f + " ----"
                    sys.stdout.write(open(f).read())
        os.chdir(here)
        shutil.rmtree(tmpdir)

class MinimizeTest(FailTest):

    def __init__(self, basename, simopts=None,
                 inputs=("mmp",), outputs=("trc", "xyz")):
        if simopts == None:
            testname = basename.split(os.sep)[-1]
            simopts = ("--minimize",
                       "--dump-as-text",
                       testname + ".mmp")
        self.basename = basename
        self.inputs = inputs
        self.outputs = outputs  # not using this yet
        self.runInSandbox(simopts)
        assert self.exitvalue == 0
        if SLOW_TESTS:
            if FAIL_UNIMPLEMENTED_TESTS:
                assert "slow MinimizeTest unimplemented" == None
        else:
            # check MD5 checksums only
            if FAIL_UNIMPLEMENTED_TESTS:
                assert "fast MinimizeTest unimplemented" == None

class StructureTest(FailTest):

    def __init__(self, basename, simopts=None,
                 inputs=("mmp",), outputs=("trc", "xyz")):
        if simopts == None:
            testname = basename.split(os.sep)[-1]
            simopts = ("--minimize",
                       "--dump-as-text",
                       testname + ".mmp")
        self.basename = basename
        self.inputs = inputs
        self.outputs = outputs  # not using this yet
        self.runInSandbox(simopts)
        assert self.exitvalue == 0
        if SLOW_TESTS:
            if FAIL_UNIMPLEMENTED_TESTS:
                assert "slow StructureTest unimplemented" == None
        else:
            # check MD5 checksums only
            if FAIL_UNIMPLEMENTED_TESTS:
                assert "fast StructureTest unimplemented" == None

class DynamicsTest(FailTest):

    def __init__(self, basename, simopts=None,
                 inputs=("mmp", "xyz"), outputs=("trc", "xyz")):
        if simopts == None:
            testname = basename.split(os.sep)[-1]
            simopts = ("--dump-as-text",
                       testname + ".mmp")
        self.basename = basename
        self.inputs = inputs
        self.outputs = outputs  # not using this yet
        self.runInSandbox(simopts)
        assert self.exitvalue == 0
        if SLOW_TESTS:
            if FAIL_UNIMPLEMENTED_TESTS:
                assert "slow DynamicsTest unimplemented" == None
        else:
            # check MD5 checksums only
            if FAIL_UNIMPLEMENTED_TESTS:
                assert "fast DynamicsTest unimplemented" == None


    def dynamicsTest(self, simopts, inputs=("mmp", "xyz"), outputs=()):
        self.runInSandbox(simopts, inputs=inputs, outputs=outputs)
        self.assertEqual(self.exitvalue, 0)
        if SLOW_TESTS:
            if FAIL_UNIMPLEMENTED_TESTS:
                self.fail("slow dynamicsTest unimplemented")
        else:
            # check MD5 checksums only
            if FAIL_UNIMPLEMENTED_TESTS:
                self.fail("fast dynamicsTest unimplemented")

####################################################
# Everything currently living in a "*.test" file can
# go here, and become more legible.

class Tests(unittest.TestCase):
    """Put the fast tests here.
    """
    def test_minimize_0001(self):
        StructureTest("tests/minimize/test_0001")
    def test_minimize_0002(self):
        FailTest("tests/minimize/test_0002",
                 ("--num-frames=500",
                  "--minimize",
                  "--dump-as-text",
                  "test_0002.mmp"))
    def test_minimize_0003(self):
        FailTest("tests/minimize/test_0003",
                 ("--num-frames=300",
                  "--minimize",
                  "--dump-intermediate-text",
                  "--dump-as-text",
                  "test_0003.mmp"))
    def test_minimize_0004(self):
        FailTest("tests/minimize/test_0004",
                 ("--num-frames=600",
                  "--minimize",
                  "--dump-as-text",
                  "test_0004.mmp"))
    def test_minimize_0005(self):
        StructureTest("tests/minimize/test_0005")
    def test_minimize_0006(self):
        FailTest("tests/minimize/test_0006",
                 ("--num-frames=300",
                  "--minimize",
                  "--dump-intermediate-text",
                  "--dump-as-text",
                  "test_0006.mmp"))
    def test_minimize_0007(self):
        FailTest("tests/minimize/test_0007",
                 ("--num-frames=300",
                  "--minimize",
                  "--dump-intermediate-text",
                  "--dump-as-text",
                  "test_0007.mmp"))
    def test_minimize_0008(self):
        # test ground in minimize
        MinimizeTest("tests/minimize/test_0008")
    def test_minimize_0009(self):
        StructureTest("tests/minimize/test_0009")
    def test_minimize_0010(self):
        MinimizeTest("tests/minimize/test_0010")
    def test_minimize_0011(self):
        MinimizeTest("tests/minimize/test_0011")
    def test_minimize_0012(self):
        MinimizeTest("tests/minimize/test_0012")
    def test_minimize_0013(self):
        StructureTest("tests/minimize/test_0013")
    def test_rigid_organics_C10H12(self):
        StructureTest("tests/rigid_organics/test_C10H12")
    def test_rigid_organics_C10H14(self):
        StructureTest("tests/rigid_organics/test_C10H14")
    def test_rigid_organics_C14H20(self):
        StructureTest("tests/rigid_organics/test_C14H20")
    def test_rigid_organics_C14H24(self):
        StructureTest("tests/rigid_organics/test_C14H24")
    def test_rigid_organics_C2H6(self):
        StructureTest("tests/rigid_organics/test_C2H6")
    def test_rigid_organics_C3H6(self):
        StructureTest("tests/rigid_organics/test_C3H6")
    def test_rigid_organics_C3H8(self):
        StructureTest("tests/rigid_organics/test_C3H8")
    def test_rigid_organics_C4H8(self):
        StructureTest("tests/rigid_organics/test_C4H8")
    def test_rigid_organics_C6H10(self):
        StructureTest("tests/rigid_organics/test_C6H10")
    def test_rigid_organics_C8H14(self):
        StructureTest("tests/rigid_organics/test_C8H14")
    def test_rigid_organics_C8H8(self):
        StructureTest("tests/rigid_organics/test_C8H8")
    def test_rigid_organics_CH4(self):
        StructureTest("tests/rigid_organics/test_CH4")
    def test_dynamics_0001(self):
        # rotary motor test
        FailTest("tests/dynamics/test_0001",
                 ("--num-frames=30",
                  "--temperature=0",
                  "--iters-per-frame=10000",
                  "--dump-as-text",
                  "test_0001.xyz"),
                 inputs=("mmp", "xyz"))
    def test_dynamics_0002(self):
        # ground, thermostat, and thermometer test
        DynamicsTest("tests/dynamics/test_0002",
                     ("--num-frames=100",
                      "--temperature=300",
                      "--iters-per-frame=10",
                      "--dump-as-text",
                      "test_0002.xyz"))

###########################################

if __name__ == "__main__":
    if "debug" in sys.argv[1:]:
        DEBUG = True
    if "unimp" in sys.argv[1:]:
        FAIL_UNIMPLEMENTED_TESTS = True
    if "slow" in sys.argv[1:]:
        SLOW_TESTS = True
    #if SLOW_TESTS:
    #    Tests = SlowTests
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
