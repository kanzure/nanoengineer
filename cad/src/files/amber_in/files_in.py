# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

"""
files_in.py -- reading AMBER .in file fragments

@author: EricM
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""


# Various standard residues appear in AMBER data files with .in
# extensions.  These describe the residue with internal coordinates,
# each atom placed with respect to other previously placed atoms.

# Actual .in files in the AMBER source tree contain multiple residues,
# each of which has data specified beyond just the z-matrix of
# internal coordinates.  This routine is designed to read a single
# fragment from one of those files, where the fragment consists of
# just the lines defining the z-matrix for a single residue.

# Here is a sample of such a fragment, Glycene:

#   i igraph isymbl itree na nb  nc     r      theta      phi      chrg
#
#    1  DUMM  DU    M    0  -1  -2     0.000     0.000     0.000   0.00000
#    2  DUMM  DU    M    1   0  -1     1.449     0.000     0.000   0.00000
#    3  DUMM  DU    M    2   1   0     1.522   111.100     0.000   0.00000
#    4  N     N     M    3   2   1     1.335   116.600   180.000  -0.374282
#    5  H     H     E    4   3   2     1.010   119.800     0.000   0.253981
#    6  CA    CT    M    4   3   2     1.449   121.900   180.000  -0.128844
#    7  HA2   H0    E    6   4   3     1.090   109.500   300.000   0.088859
#    8  HA3   H0    E    6   4   3     1.090   109.500    60.000   0.088859
#    9  C     C     M    6   4   3     1.522   110.400   180.000   0.580584
#   10  O     O     E    9   6   4     1.229   120.500     0.000  -0.509157

# The format is columns of data separated by whitespace.  Different
# AMBER .in files use different widths for the various columns.  The
# first column is the atom index number (i).  The first three atoms
# are dummy atoms, used to establish the coordinate system.

# The second column is a unique atom name for each of the non-dummy
# atoms (igraph).

# The third column is the AMBER atom type (isymbl).

# Column 4 is the topology for the atom (itree).  It determines the
# number of non-loop bonds.  We're going to ignore this, and just
# create a bond for each radius specification.

# Columns 5, 6, and 7 are indices for three previous atoms (na, nb,
# nc)

# Columns 8, 9, and 10 are the radius (r), angle (theta), and torsion
# angle (phi) parameters.

# The last column is the fractional charge on the atom (chrg).  We are
# ignoring the charge here.

# The radius parameter is in Angstroms, the angle and torsion
# parameters are in degrees.

# Taking line ten an an example, the Oxygen atom it represents is
# 1.229 Angstroms away from Carbon atom number 9.  The O-C-C angle
# between atoms 10, 9, and 6 is 120.5 degrees.  The O-C-C-N torsion
# angle between atoms 10, 9, 6, and 4 is 0 degrees, indicating that
# the O and N are on the same side of the C-C bond.

# See: http://amber.scripps.edu/doc/prep.html

import os

from geometry.InternalCoordinatesToCartesian import InternalCoordinatesToCartesian
from geometry.VQT import A

from model.chunk import Chunk
from model.chem import Atom
from model.bonds import bond_atoms
from model.elements import PeriodicTable

AMBER_AtomTypes = {}

_is_initialized = False

def _init():
    global _is_initialized
    if (_is_initialized):
        return

    AMBER_AtomTypes["C"]  = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CA"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CB"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CC"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CD"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CK"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CM"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CN"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CQ"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CR"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CT"] = PeriodicTable.getElement("C").find_atomtype("sp3")
    AMBER_AtomTypes["CV"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CW"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["C*"] = PeriodicTable.getElement("C").find_atomtype("sp2")
    AMBER_AtomTypes["CY"] = PeriodicTable.getElement("C").find_atomtype("sp")
    AMBER_AtomTypes["CZ"] = PeriodicTable.getElement("C").find_atomtype("sp")

    AMBER_AtomTypes["C0"] = PeriodicTable.getElement("Ca").find_atomtype("?")

    AMBER_AtomTypes["H"]  = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["H0"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["HC"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["H1"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["H2"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["H3"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["HA"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["H4"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["H5"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["HO"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["HS"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["HW"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["HP"] = PeriodicTable.getElement("H").find_atomtype("?")
    AMBER_AtomTypes["HZ"] = PeriodicTable.getElement("H").find_atomtype("?")

    AMBER_AtomTypes["F"]  = PeriodicTable.getElement("F").find_atomtype("?")
    AMBER_AtomTypes["Cl"] = PeriodicTable.getElement("Cl").find_atomtype("?")
    AMBER_AtomTypes["Br"] = PeriodicTable.getElement("Br").find_atomtype("?")
    AMBER_AtomTypes["I"]  = PeriodicTable.getElement("I").find_atomtype("?")
    AMBER_AtomTypes["IM"] = PeriodicTable.getElement("Cl").find_atomtype("?")
    AMBER_AtomTypes["IB"] = PeriodicTable.getElement("Na").find_atomtype("?")
    AMBER_AtomTypes["MG"] = PeriodicTable.getElement("Mg").find_atomtype("?")

    AMBER_AtomTypes["N"]  = PeriodicTable.getElement("N").find_atomtype("sp2")
    AMBER_AtomTypes["NA"] = PeriodicTable.getElement("N").find_atomtype("sp2")
    AMBER_AtomTypes["NB"] = PeriodicTable.getElement("N").find_atomtype("sp2")
    AMBER_AtomTypes["NC"] = PeriodicTable.getElement("N").find_atomtype("sp2")
    AMBER_AtomTypes["N2"] = PeriodicTable.getElement("N").find_atomtype("sp2")
    AMBER_AtomTypes["N3"] = PeriodicTable.getElement("N").find_atomtype("sp3")
    AMBER_AtomTypes["NT"] = PeriodicTable.getElement("N").find_atomtype("sp3")
    AMBER_AtomTypes["N*"] = PeriodicTable.getElement("N").find_atomtype("sp2")
    AMBER_AtomTypes["NY"] = PeriodicTable.getElement("N").find_atomtype("sp")

    AMBER_AtomTypes["O"]  = PeriodicTable.getElement("O").find_atomtype("sp2")
    AMBER_AtomTypes["O2"] = PeriodicTable.getElement("O").find_atomtype("sp2")
    AMBER_AtomTypes["OW"] = PeriodicTable.getElement("O").find_atomtype("sp3")
    AMBER_AtomTypes["OH"] = PeriodicTable.getElement("O").find_atomtype("sp3")
    AMBER_AtomTypes["OS"] = PeriodicTable.getElement("O").find_atomtype("sp3")

    AMBER_AtomTypes["P"]  = PeriodicTable.getElement("P").find_atomtype("sp3(p)") #sp3(p) is 'sp3(phosphate)

    AMBER_AtomTypes["S"]  = PeriodicTable.getElement("S").find_atomtype("sp3") # ?
    AMBER_AtomTypes["SH"] = PeriodicTable.getElement("S").find_atomtype("sp3") # ?

    AMBER_AtomTypes["CU"] = PeriodicTable.getElement("Cu").find_atomtype("?")
    AMBER_AtomTypes["FE"] = PeriodicTable.getElement("Fe").find_atomtype("?")
    AMBER_AtomTypes["Li"] = PeriodicTable.getElement("Li").find_atomtype("?")
    AMBER_AtomTypes["IP"] = PeriodicTable.getElement("Na").find_atomtype("?")
    AMBER_AtomTypes["Na"] = PeriodicTable.getElement("Na").find_atomtype("?")
    AMBER_AtomTypes["K"]  = PeriodicTable.getElement("K").find_atomtype("?")
    #AMBER_AtomTypes["Rb"] = PeriodicTable.getElement("Rb").find_atomtype("?")
    #AMBER_AtomTypes["Cs"] = PeriodicTable.getElement("Cs").find_atomtype("?")
    AMBER_AtomTypes["Zn"] = PeriodicTable.getElement("Zn").find_atomtype("?")

    _is_initialized = True


def insertin(assy, filename):
    _init()

    dir, nodename = os.path.split(filename)

    mol = Chunk(assy, nodename)
    mol.showOverlayText = True

    file = open(filename)
    lines = file.readlines()
    atoms = {}
    transform = InternalCoordinatesToCartesian(len(lines), None)
    for line in lines:
        columns = line.strip().split()
        index = int(columns[0])
        name = columns[1]
        type = columns[2]
        na = int(columns[4])
        nb = int(columns[5])
        nc = int(columns[6])
        r = float(columns[7])
        theta = float(columns[8])
        phi = float(columns[9])

        transform.addInternal(index, na, nb, nc, r, theta, phi)
        xyz = transform.getCartesian(index)

        if (index > 3):
            if (AMBER_AtomTypes.has_key(type)):
                sym = AMBER_AtomTypes[type]
            else:
                print "unknown AMBER atom type, substituting Carbon: %s" % type
                sym = "C"

            a = Atom(sym, A(xyz), mol)
            atoms[index] = a
            a.setOverlayText(type)
            if (na > 3):
                a2 = atoms[na]
                bond_atoms(a, a2)

    assy.addmol(mol)
