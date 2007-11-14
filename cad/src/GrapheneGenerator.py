# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GrapheneGenerator.py

@author: Will
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2007-05-17: Implemented PropMgrBaseClass.
Mark 2007-07-24: Now uses new PM module.
Mark 2007-08-06: Renamed GrapheneGeneratorDialog to GrapheneGeneratorPropertyManager.
"""

from math import atan2, pi

from VQT import V
from chem import Atom

import bonds # for bond_atoms
import bond_constants

from chunk import molecule
import env
from debug import Stopwatch
from elements import PeriodicTable
from utilities.Log import greenmsg

from GrapheneGeneratorPropertyManager import GrapheneGeneratorPropertyManager
from GeneratorBaseClass import GeneratorBaseClass

sqrt3 = 3 ** 0.5
quartet = ((0, sqrt3 / 2), (0.5, 0), (1.5, 0), (2, sqrt3 / 2))

TOROIDAL = False   # Just for Will

class GrapheneGenerator( GrapheneGeneratorPropertyManager, GeneratorBaseClass):
    """
    The Graphene Sheet Generator class for the "Build Graphene (Sheet)" command.
    """

    cmd = greenmsg("Build Graphene: ")
    prefix = 'Graphene-'   # used for gensym
    # Generators for DNA, nanotubes and graphene have their MT name generated 
    # (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix = True 
    # We now support multiple keywords 
    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')
    sponsor_keyword = 'Graphene'

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        GrapheneGeneratorPropertyManager.__init__(self)
        GeneratorBaseClass.__init__(self, win)

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        """Return all the parameters from the Property Manager.
        """
        height = self.heightField.value()
        width = self.widthField.value()
        self.bond_length = bond_length = self.bondLengthField.value()
        endings = self.endingsComboBox.currentIndex()

        return (height, width, bond_length, endings)

    def build_struct(self, name, params, position):
        """Build a graphene sheet from the parameters in the Property Manager.
        """
        height, width, bond_length, endings = params
        PROFILE = False
        if PROFILE:
            sw = Stopwatch()
            sw.start()
        mol = molecule(self.win.assy, self.name)
        atoms = mol.atoms
        z = 0.0
        self.populate(mol, height, width, z, bond_length, endings, position)

        if PROFILE:
            t = sw.now()
            env.history.message(greenmsg("%g seconds to build %d atoms" %
                                         (t, len(atoms.values()))))
        return mol

    def populate(self, mol, height, width, z, bond_length, endings, position):
        """
        Create a graphene sheet chunk.
        """

        def add(element, x, y, atomtype='sp2'):
            atm = Atom(element, V(x, y, z), mol)
            atm.set_atomtype_but_dont_revise_singlets(atomtype)
            return atm

        num_atoms = len(mol.atoms)
        bond_dict = { }
        i = j = 0
        y = -0.5 * height - 2 * bond_length
        while y < 0.5 * height + 2 * bond_length:
            i = 0
            x = -0.5 * width - 2 * bond_length
            while x < 0.5 * width + 2 * bond_length:
                lst = [ ]
                for x1, y1 in quartet:
                    atm = add("C", x + x1 * bond_length, y + y1 * bond_length)
                    lst.append(atm)
                bond_dict[(i, j)] = lst
                bonds.bond_atoms(lst[0], lst[1], bond_constants.V_GRAPHITE)
                bonds.bond_atoms(lst[1], lst[2], bond_constants.V_GRAPHITE)
                bonds.bond_atoms(lst[2], lst[3], bond_constants.V_GRAPHITE)
                i += 1
                x += 3 * bond_length
            j += 1
            y += sqrt3 * bond_length
        imax, jmax = i, j

        for i in range(imax):
            for j in range(jmax - 1):
                lst1 = bond_dict[(i, j)]
                lst2 = bond_dict[(i, j+1)]
                bonds.bond_atoms(lst1[0], lst2[1], bond_constants.V_GRAPHITE)
                bonds.bond_atoms(lst1[3], lst2[2], bond_constants.V_GRAPHITE)
                
        for i in range(imax - 1):
            for j in range(jmax):
                lst1 = bond_dict[(i, j)]
                lst2 = bond_dict[(i+1, j)]
                bonds.bond_atoms(lst1[3], lst2[0], bond_constants.V_GRAPHITE)

        # trim to dimensions
        atoms = mol.atoms
        for atm in atoms.values():
            x, y, z = atm.posn()
            xdim, ydim = width + bond_length, height + bond_length
            # xdim, ydim = width + 0.5 * bond_length, height + 0.5 * bond_length
            if (x < -0.5 * xdim or x > 0.5 * xdim or y < -0.5 * ydim or y > 0.5 * ydim):
                atm.kill()

        def trimCarbons():
            """Trim all the carbons that only have one carbon neighbor.
            """
            for i in range(2):
                for atm in atoms.values():
                    if not atm.is_singlet() and len(atm.realNeighbors()) == 1:
                        atm.kill()

        if TOROIDAL:
            # This is for making electrical inductors. What would be
            # really good here would be to break the bonds that are
            # stretched by this and put back the bondpoints.
            angstromsPerTurn = 6.0
            for atm in atoms.values():
                x, y, z = atm.posn()
                r = (x**2 + y**2) ** .5
                if 0.25 * width <= r <= 0.5 * width:
                    angle = atan2(y, x)
                    zdisp = (angstromsPerTurn * angle) / (2 * pi)
                    atm.setposn(V(x, y, z + zdisp))
                else:
                    atm.kill()

        if endings == 1:
            # hydrogen terminations
            trimCarbons()
            for atm in atoms.values():
                atm.Hydrogenate()
        elif endings == 2:
            # nitrogen terminations
            trimCarbons()
            dstElem = PeriodicTable.getElement('N')
            atomtype = dstElem.find_atomtype('sp2')
            for atm in atoms.values():
                if len(atm.realNeighbors()) == 2:
                    atm.Transmute(dstElem, force=True, atomtype=atomtype)

        for atm in atoms.values():
            atm.setposn(atm.posn() + position)

        if num_atoms == len(mol.atoms):
            raise Exception("Graphene sheet too small - no atoms added")
