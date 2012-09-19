# Copyright 2005, 2007 Nanorex, Inc.  See LICENSE file for details.
import unittest
import chem
import assembly
import Utility
import debug
from elements import PeriodicTable

Hydrogen = PeriodicTable.getElement(1)
Carbon = PeriodicTable.getElement(6)
Nitrogen = PeriodicTable.getElement(7)
Oxygen = PeriodicTable.getElement(8)
Singlet = PeriodicTable.getElement(0)

##########################
# Avoid this:
#    QPaintDevice: Must construct a QApplication before a QPaintDevice

class DummyPixmap:
    def __init__(self, iconpath):
        pass

Utility.QPixmap = DummyPixmap

#########################

# enforce API protection
debug.privateMethod = debug._privateMethod

# We could do this in $HOME/.atom-debug-rc and avoid the need for
# the boolean altogether.

#########################

if False:
    # Make sure the tests are really working
    # Passivate no longer transmutes atoms
    # so testPassivate should break
    def passivate(self):
        pass
    chem.Atom.Passivate = passivate

#########################

def countElements(mol, d):
    """In a molecule, verify the numbers of atoms with given element names.
    """
    for name in d.keys():
        expectedCount = d[name]
        count = 0
        for a in mol.atlist:
            if a.element.name == name:
                count += 1
        assert count == expectedCount

class ChemTest(unittest.TestCase):
    """Various tests of chemistry bookkeeping
    """

    def setUp(self):
        self.assy = assy = assembly.assembly(None)
        self.mol = mol = chem.molecule(assy)
        self.a = a = chem.Atom("C", chem.V(0.0, 0.0, 0.0), mol)
        self.a.set_atomtype("sp3", True)

    def testInitialCounts(self):
        countElements(self.mol,
                      {"Carbon": 1,
                       "Hydrogen": 0,
                       "Singlet": 4})

    def testPassivate(self):
        self.a.Passivate()
        assert self.a.element.name == "Neon"

    def testHydrogenate(self):
        self.mol.Hydrogenate()
        countElements(self.mol,
                      {"Carbon": 1,
                       "Hydrogen": 4,
                       "Singlet": 0})

    def testDehydrogenate(self):
        self.testHydrogenate()
        self.mol.Dehydrogenate()
        self.testInitialCounts()

if __name__ == "__main__":
    suite = unittest.makeSuite(ChemTest, "test")
    runner = unittest.TextTestRunner()
    runner.run(suite)
