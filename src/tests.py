#!/usr/bin/python

import os
import sys
import shutil
import unittest
from subprocess import Popen

os.system("make simulator")

FAIL_UNIMPLEMENTED_TESTS = False

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.simulator = os.sep.join([os.getcwd(), "simulator"])
    def basename(self):
        # get the calling method name e.g. "test_rigid_organics_C2H4"
        name = sys._getframe(2).f_code.co_name
        name = name[5:]  # get rid of "test_"
        n = name.rindex("_")
        dirname = name[:n]
        testname = "test_" + name[n+1:]
        return os.sep.join([os.getcwd(), "tests",
                            dirname, testname])
    def runInSandbox(self, cmdline):
        # This will not run in /tmp/... under Linux. Instead it
        # will create a tmp subdirectory in sim/src.
        self.tmpdir = tmpdir = "tmp"
        try:
            shutil.rmtree(tmpdir)
        except OSError, e:
            assert e.args[0] == 2
        os.mkdir(tmpdir)
        here = os.getcwd()
        os.chdir(tmpdir)
        # run program, get exitvalue, stdout, stderr
        # os.tmpfile() might be useful here
        stdout = open("stdout", "w")
        stderr = open("stderr", "w")
        if " " in cmdline:
            cmdline = cmdline.split()
        exitvalue = Popen(cmdline, stdout=stdout, stderr=stderr).wait()
        self.exitvalue = exitvalue
        self.stdout = open("stdout").read()
        self.stderr = open("stderr").read()
        os.chdir(here)
    def tearDown(self):
        if hasattr(self, "tmpdir"):
            try:
                shutil.rmtree(self.tmpdir)
            except OSError, e:
                assert e.args[0] == 2
    def failTest(self, simopts):
        mmpfile = self.basename() + ".mmp"
        #print mmpfile
        self.runInSandbox(self.simulator + " " +
                          simopts + " " + mmpfile)
        self.assertEqual(self.exitvalue, 0)
    def structureTest(self):
        mmpfile = self.basename() + ".mmp"
        print mmpfile
        if FAIL_UNIMPLEMENTED_TESTS:
            self.fail("structureTest unimplemented")
    def minimizeTest(self):
        mmpfile = self.basename() + ".mmp"
        # check the .trc and .xyz files
        if FAIL_UNIMPLEMENTED_TESTS:
            self.fail("minimizeTest unimplemented")
    def dynamicsTest(self):
        mmpfile = self.basename() + ".mmp"
        self.runInSandbox(self.simulator + " --num-frames=100" +
                          "--temperature=300 --iters-per-frame=10 " +
                          "--dump-as-text " + mmpfile)
        if FAIL_UNIMPLEMENTED_TESTS:
            self.fail("minimizeTest unimplemented")

####################################################
# Everything currently living in a "*.test" file can
# go here, and become more legible.

class FastTests(BaseTest):
    def test_pwd(self):
        self.runInSandbox("pwd")
        self.assertEquals(self.stdout, "/home/wware/polosims/sim/src/tmp\n")
        self.assertEquals(self.stderr, "")
        self.assertEquals(self.exitvalue, 0)
    def test_minimize_0001(self):
        self.structureTest()
    def test_minimize_0002(self):
        self.failTest("-f500 -m -x")
    def test_minimize_0002(self):
        self.failTest("-f500 -m -x test_0002.mmp")
    def test_minimize_0003(self):
        self.failTest("-f300 -m -X -x test_0003.mmp")
    def test_minimize_0004(self):
        self.failTest("-f600 -m -x test_0004.mmp")
    def test_minimize_0005(self):
        self.structureTest()
    def test_minimize_0006(self):
        self.failTest("-f300 -m -X -x test_0006.mmp")
    def test_minimize_0007(self):
        self.failTest("-f300 -m -X -x test_0007.mmp")
    def test_minimize_0008(self):
        # test ground in minimize
        self.minimizeTest()
    def test_minimize_0009(self):
        self.structureTest()
    def test_minimize_0010(self):
        self.minimizeTest()
    def test_minimize_0011(self):
        self.minimizeTest()
    def test_minimize_0012(self):
        self.minimizeTest()
    def test_minimize_0013(self):
        self.structureTest()
    def test_rigid_organics_C10H12(self):
        self.structureTest()
    def test_rigid_organics_C10H14(self):
        self.structureTest()
    def test_rigid_organics_C14H20(self):
        self.structureTest()
    def test_rigid_organics_C14H24(self):
        self.structureTest()
    def test_rigid_organics_C2H6(self):
        self.structureTest()
    def test_rigid_organics_C3H6(self):
        self.structureTest()
    def test_rigid_organics_C3H8(self):
        self.structureTest()
    def test_rigid_organics_C4H8(self):
        self.structureTest()
    def test_rigid_organics_C6H10(self):
        self.structureTest()
    def test_rigid_organics_C8H14(self):
        self.structureTest()
    def test_rigid_organics_C8H8(self):
        self.structureTest()
    def test_rigid_organics_CH4(self):
        self.structureTest()

class SlowTests(FastTests):
    def test_dynamics_0001(self):
        # rotary motor test
        self.failTest("--num-frames=30" +
                      "--temperature=0 --iters-per-frame=10000 " +
                      "--dump-as-text")
    def test_dynamics_0002(self):
        # ground, thermostat, and thermometer test
        self.dynamicsTest()
	#PROGRAM simulator -f100 -t300 -i10 -x test_0002.mmp

###########################################

def runTests(slow=False):
    if slow: tests = SlowTests
    else: tests = FastTests
    suite = unittest.makeSuite(tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    if "unimp" in sys.argv[1:]:
        FAIL_UNIMPLEMENTED_TESTS = True
    runTests(slow=('slow' in sys.argv[1:]))
