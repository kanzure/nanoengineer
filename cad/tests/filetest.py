# Copyright 2005, 2007 Nanorex, Inc.  See LICENSE file for details.
import unittest
import chem
import assembly
from qt import QApplication, SIGNAL
import Utility
import os

#########################

import undo
undo._use_hcmi_hack = False

#########################

import MWsemantics
import startup_funcs

STILL_NEED_MODULARIZATION = True

if STILL_NEED_MODULARIZATION:
    # file functions don't work right unless I do all this first
    startup_funcs.before_creating_app()
    app = QApplication([ ])
    foo = MWsemantics.MWsemantics()
    startup_funcs.pre_main_show(foo)
    foo.show()
    startup_funcs.post_main_show(foo)

else:
    foo = fileSlotsMixin()  # ? ? ?
    # we still want assembly and group and atom,
    # and we still want to be able to select subgroups
    # but we don't want QApplication and QMainWindow

###################

class FileTest(unittest.TestCase):

    TESTDATA = {
        "filename": "../partlib/gears/LilGears.mmp",
        "numatoms": 170,
        "bondLines": 150,
        "numchunks": 1
        }

    def extraSaveMmpTest(self):
        pass

    def setUp(self):
        #foo.fileNew()
        #foo.fileOpen("../partlib/pumps/Pump.mmp")
        foo.fileOpen(self.TESTDATA["filename"])

    def tearDown(self):
        foo.fileClose()

    def getLines(self, searchterm, fileExt):
        return os.popen("egrep \"" + searchterm + "\" /tmp/foo."
                        + fileExt).readlines()

    def countLines(self, searchterm, fileExt, expected):
        n = len(self.getLines(searchterm, fileExt))
        if n != expected:
            print "EXPECTED", expected, "GOT", n
        assert n == expected

    def testOpenFile(self):
        assy = foo.assy
        assy.checkparts()
        pump = assy.current_selgroup()
        assert pump.__class__ == Utility.PartGroup
        class MyStats: pass
        stats = MyStats()
        assy.tree.init_statistics(stats)
        assy.tree.getstatistics(stats)
        assert stats.natoms == self.TESTDATA["numatoms"]
        assert stats.nchunks == self.TESTDATA["numchunks"]

    def testSavePdbFile(self):
        foo.saveFile("/tmp/foo.pdb")
        self.countLines("ATOM", "pdb", self.TESTDATA["numatoms"])
        # I'd count the CONECT lines too, but for large structures
        # that number varies. I don't know if that's a legitimate
        # failure of the test, or a funny (but legit) behavior of
        # the file format.
        os.system("rm /tmp/foo.pdb")

    def testSaveMmpFile(self):
        foo.saveFile("/tmp/foo.mmp")
        self.countLines("atom", "mmp", self.TESTDATA["numatoms"])
        self.countLines("bond", "mmp", self.TESTDATA["bondLines"])
        self.extraSaveMmpTest()
        os.system("rm /tmp/foo.mmp")

######################

class FileTestBigStructure(FileTest):

    TESTDATA = {
        "filename": "../partlib/pumps/Pump.mmp",
        "numatoms": 6165,
        "bondLines": 4417,
        "numchunks": 2,
        }

    def extraSaveMmpTest(self):
        assert self.getLines("^mol ", "mmp") == [
            "mol (Pump Casing) def\n",
            "mol (Pump Rotor) def\n"
            ]

######################

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileTest, "test"))
    suite.addTest(unittest.makeSuite(FileTestBigStructure, "test"))
    runner.run(suite)
