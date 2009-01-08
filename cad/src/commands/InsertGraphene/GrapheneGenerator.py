# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GrapheneGenerator.py

@author: Will
@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2007-05-17: Implemented PropMgrBaseClass.
Mark 2007-07-24: Now uses new PM module.
Mark 2007-08-06: Renamed GrapheneGeneratorDialog to GrapheneGeneratorPropertyManager.

Ninad 2008-07-23: Cleanup to port Graphene generator to the EditCommand API. 
Now this class simply acts as a generator object called from the editcommand 
while creating the structure.
"""

from math import atan2, pi

from model.chem import Atom

from model.bonds import bond_atoms
import model.bond_constants as bond_constants

from model.chunk import Chunk
import foundation.env as env
from utilities.debug import Stopwatch
from model.elements import PeriodicTable
from utilities.Log import greenmsg


from geometry.VQT import V
sqrt3 = 3 ** 0.5
quartet = ((0, sqrt3 / 2), (0.5, 0), (1.5, 0), (2, sqrt3 / 2))

TOROIDAL = False #debug flag , don't commit it with True!


class GrapheneGenerator:
    """
    The Graphene Sheet Generator class for the "Build Graphene (Sheet)" command.
    """
    def make(self, 
             assy, 
             name, 
             params,              
             position = V(0, 0, 0),
             editCommand = None):
        
        height, width, bond_length, endings = params
        PROFILE = False
        if PROFILE:
            sw = Stopwatch()
            sw.start()
        mol = Chunk(assy, name)
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
                bond_atoms(lst[0], lst[1], bond_constants.V_GRAPHITE)
                bond_atoms(lst[1], lst[2], bond_constants.V_GRAPHITE)
                bond_atoms(lst[2], lst[3], bond_constants.V_GRAPHITE)
                i += 1
                x += 3 * bond_length
            j += 1
            y += sqrt3 * bond_length
        imax, jmax = i, j

        for i in range(imax):
            for j in range(jmax - 1):
                lst1 = bond_dict[(i, j)]
                lst2 = bond_dict[(i, j+1)]
                bond_atoms(lst1[0], lst2[1], bond_constants.V_GRAPHITE)
                bond_atoms(lst1[3], lst2[2], bond_constants.V_GRAPHITE)
                
        for i in range(imax - 1):
            for j in range(jmax):
                lst1 = bond_dict[(i, j)]
                lst2 = bond_dict[(i+1, j)]
                bond_atoms(lst1[3], lst2[0], bond_constants.V_GRAPHITE)

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
