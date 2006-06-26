# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
GrapheneGenerator.py

$Id$
"""

__author__ = "Will"

from GrapheneGeneratorDialog import graphene_sheet_dialog
from math import atan2, sin, cos, pi
import assembly, chem, bonds, Utility
from chem import molecule, Atom
import env
from HistoryWidget import redmsg, orangemsg, greenmsg
from qt import Qt, QApplication, QCursor, QDialog, QDoubleValidator, QValidator
from VQT import dot
import string
from widgets import double_fixup
from debug import Stopwatch, objectBrowse
from Utility import Group
from GeneratorBaseClass import GeneratorBaseClass
from elements import PeriodicTable

sqrt3 = 3 ** 0.5
quartet = ((0, sqrt3 / 2), (0.5, 0), (1.5, 0), (2, sqrt3 / 2))

TOROIDAL = False   # Just for Will

# GeneratorBaseClass must come BEFORE the dialog in the list of parents
class GrapheneGenerator(GeneratorBaseClass, graphene_sheet_dialog):

    cmd = greenmsg("Insert Graphene: ")
    sponsor_keyword = 'Graphene'
    prefix = 'Graphene-'   # used for gensym

    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        graphene_sheet_dialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        GeneratorBaseClass.__init__(self, win)
        # Validator for the linedit widgets.
        self.validator = QDoubleValidator(self)
        # Range for linedits: 1 to 1000, 2 decimal places
        self.validator.setRange(1.0, 1000.0, 2)
        self.height_linedit.setValidator(self.validator)
        self.width_linedit.setValidator(self.validator)
        self.bond_length_linedit.setValidator(self.validator)
        self.hstr = self.height_linedit.text()
        self.wstr = self.width_linedit.text()
        self.blstr = self.bond_length_linedit.text()

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        # Get length from height_linedit and make sure it is not zero.
        # height_linedit's validator makes sure this has a valid number (float).  
        # The only exception is when there is no text.  Mark 051103.
        if not self.height_linedit.text():
            raise Exception("Please specify a valid length.")
        height = string.atof(str(self.height_linedit.text()))

        if not self.width_linedit.text():
            raise Exception("Please specify a valid width.")
        width = string.atof(str(self.width_linedit.text()))

        if not self.bond_length_linedit.text():
            raise Exception("Please specify a valid bond length.")
        bond_length = str(self.bond_length_linedit.text())
        bond_length = bond_length.split(' ')[0]
        self.bond_length = bond_length = string.atof(bond_length)

        endings = self.endings_combox.currentItem()

        return (height, width, bond_length, endings)

    def build_struct(self, name, params, position):
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

    def length_fixup(self):
        '''Slot for various linedit widgets.
        This gets called each time a user types anything into the widget.
        '''
        hstr = double_fixup(self.validator, self.height_linedit.text(), self.hstr)
        self.height_linedit.setText(hstr)
        wstr = double_fixup(self.validator, self.width_linedit.text(), self.wstr)
        self.width_linedit.setText(wstr)
        blstr = double_fixup(self.validator, self.bond_length_linedit.text(), self.blstr)
        self.bond_length_linedit.setText(blstr)
        self.hstr, self.wstr, self.blstr = hstr, wstr, blstr

    def populate(self, mol, height, width, z, bond_length, endings, position):

        def add(element, x, y, atomtype='sp2'):
            atm = Atom(element, chem.V(x, y, z), mol)
            atm.set_atomtype_but_dont_revise_singlets(atomtype)
            return atm

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
                bonds.bond_atoms(lst[0], lst[1], bonds.V_GRAPHITE)
                bonds.bond_atoms(lst[1], lst[2], bonds.V_GRAPHITE)
                bonds.bond_atoms(lst[2], lst[3], bonds.V_GRAPHITE)
                i += 1
                x += 3 * bond_length
            j += 1
            y += sqrt3 * bond_length
        imax, jmax = i, j

        for i in range(imax):
            for j in range(jmax - 1):
                lst1 = bond_dict[(i, j)]
                lst2 = bond_dict[(i, j+1)]
                bonds.bond_atoms(lst1[0], lst2[1], bonds.V_GRAPHITE)
                bonds.bond_atoms(lst1[3], lst2[2], bonds.V_GRAPHITE)
                
        for i in range(imax - 1):
            for j in range(jmax):
                lst1 = bond_dict[(i, j)]
                lst2 = bond_dict[(i+1, j)]
                bonds.bond_atoms(lst1[3], lst2[0], bonds.V_GRAPHITE)

        # trim to dimensions
        atoms = mol.atoms
        for atm in atoms.values():
            x, y, z = atm.posn()
            xdim, ydim = width + bond_length, height + bond_length
            # xdim, ydim = width + 0.5 * bond_length, height + 0.5 * bond_length
            if (x < -0.5 * xdim or x > 0.5 * xdim or y < -0.5 * ydim or y > 0.5 * ydim):
                atm.kill()

        def trimCarbons():
            # trim all the carbons that only have one carbon neighbor
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
                    atm.setposn(chem.V(x, y, z + zdisp))
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

    ###################################################
    # Special UI things that still must be implemented
    def toggle_graphene_parameters_grpbox(self):
        self.toggle_groupbox(self.graphene_parameters_grpbtn, self.line2,
                             self.height_label, self.height_linedit,
                             self.width_label, self.width_linedit,
                             self.bond_length_label, self.bond_length_linedit,
                             self.endings_label, self.endings_combox)

    def defaults_btn_clicked(self):
        self.languageChange()
