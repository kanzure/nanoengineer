# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
GrapheneGenerator.py

$Id$
"""

__author__ = "Will"

from GrapheneGeneratorDialog import graphene_sheet_dialog
from math import atan2, sin, cos, pi
import assembly, chem, bonds, Utility
from chem import molecule, Atom, gensym
import env
from HistoryWidget import redmsg, orangemsg, greenmsg
from qt import Qt, QApplication, QCursor, QDialog, QDoubleValidator, QValidator
from VQT import dot
import string
from widgets import double_fixup
from debug import Stopwatch, objectBrowse
from Utility import Group
from GeneratorBaseClass import GeneratorBaseClass

sqrt3 = 3 ** 0.5

class Chirality:

    # Graphene bond length according to Dresselhaus, M. S.,
    # Dresselhaus, G., Eklund, P. C. "Science of Fullerenes and Carbon
    # Graphenes" Academic Press: San Diego, CA, 1995; pp. 760.
    BONDLENGTH = 1.421  # angstroms

    # It's handy to have slightly a bigger version, and its square.
    MAXLEN = 1.2 * BONDLENGTH
    MAXLENSQ = MAXLEN ** 2

    def __init__(self, n, m):
        self.n, self.m = n, m
        x = (n + 0.5 * m) * sqrt3
        y = 1.5 * m
        angle = atan2(y, x)
        twoPiRoverA = (x**2 + y**2) ** .5
        AoverR = (2 * pi) / twoPiRoverA
        self.__cos = cos(angle)
        self.__sin = sin(angle)
        # time to get the constants
        s, t = self.x1y1(0,0)
        u, v = self.x1y1(1./3, 1./3)
        w, x = self.x1y1(0,1)
        F = (t - v)**2
        G = 2 * (1 - cos(AoverR * (s - u)))
        H = (v - x)**2
        J = 2 * (1 - cos(AoverR * (u - w)))
        L = self.BONDLENGTH
        denom = F * J - G * H
        self.R = (L**2 * (F - H) / denom) ** .5
        self.B = (L**2 * (J - G) / denom) ** .5
        self.A = self.R * AoverR

    def x1y1(self, n, m):
        c, s = self.__cos, self.__sin
        x = (n + .5*m) * sqrt3
        y = 1.5 * m
        x1 = x * c + y * s
        y1 = -x * s + y * c
        return (x1, y1)

    def mlimits(self, y3min, y3max, n):
        if y3max < y3min:
            y3min, y3max = y3max, y3min
        B, c, s = self.B, self.__cos, self.__sin
        P = sqrt3 * B * s
        Q = 1.5 * B * (c - s / sqrt3)
        m1, m2 = (y3min + P * n) / Q, (y3max + P * n) / Q
        return int(m1-1.5), int(m2+1.5)

    def xyz(self, n, m):
        x1, y1 = self.x1y1(n, m)
        x2, y2 = self.A * x1, self.B * y1
        R = self.R
        x3 = R * sin(x2/R)
        z3 = R * cos(x2/R)
        return (x3, y2, z3)

    def populate(self, mol, length, bn_members=False):

        def add(element, x, y, z, atomtype='sp2'):
            atm = Atom(element, chem.V(x, y, z), mol)
            atm.set_atomtype_but_dont_revise_singlets(atomtype)
            return atm

        evenAtomDict = { }
        oddAtomDict = { }
        bondDict = { }
        mfirst = [ ]
        mlast = [ ]

        for n in range(self.n):
            mmin, mmax = self.mlimits(-.5 * length, .5 * length, n)
            mfirst.append(mmin)
            mlast.append(mmax)
            for m in range(mmin, mmax+1):
                x, y, z = self.xyz(n, m)
                if bn_members:
                    atm = add("B", x, y, z)
                else:
                    atm = add("C", x, y, z)
                evenAtomDict[(n,m)] = atm
                bondDict[atm] = [(n,m)]
                x, y, z = self.xyz(n+1./3, m+1./3)
                if bn_members:
                    atm = add("N", x, y, z, 'sp3')
                else:
                    atm = add("C", x, y, z)
                oddAtomDict[(n,m)] = atm
                bondDict[atm] = [(n+1, m), (n, m+1)]

        # m goes axially along the graphene, n spirals around the tube
        # like a barber pole, with slope depending on chirality. If we
        # stopped making bonds now, there'd be a spiral strip of
        # missing bonds between the n=self.n-1 row and the n=0 row.
        # So we need to connect those. We don't know how the m values
        # will line up, so the first time, we need to just hunt for the
        # m offset. But then we can apply that constant m offset to the
        # remaining atoms along the strip.
        n = self.n - 1
        mmid = (mfirst[n] + mlast[n]) / 2
        atm = oddAtomDict[(n, mmid)]
        class FoundMOffset(Exception): pass
        try:
            for m2 in range(mfirst[0], mlast[0] + 1):
                atm2 = evenAtomDict[(0, m2)]
                diff = atm.posn() - atm2.posn()
                if dot(diff, diff) < self.MAXLENSQ:
                    moffset = m2 - mmid
                    # Given the offset, zipping up the rows is easy.
                    for m in range(mfirst[n], mlast[n]+1):
                        atm = oddAtomDict[(n, m)]
                        bondDict[atm].append((0, m + moffset))
                    raise FoundMOffset()
            # If we get to this point, we never found m offset.
            # If this ever happens, it indicates a bug.
            raise Exception, "can't find m offset"
        except FoundMOffset:
            pass

        # Use the bond information to bond the atoms
        for (dict1, dict2) in [(evenAtomDict, oddAtomDict),
                               (oddAtomDict, evenAtomDict)]:
            for n, m in dict1.keys():
                atm = dict1[(n, m)]
                for n2, m2 in bondDict[atm]:
                    try:
                        atm2 = dict2[(n2, m2)]
                        if not bonds.bonded(atm, atm2):
                            if bn_members:
                                bonds.bond_atoms(atm, atm2, bonds.V_SINGLE)
                            else:
                                bonds.bond_atoms(atm, atm2, bonds.V_GRAPHITE)
                    except KeyError:
                        pass

# GeneratorBaseClass must come BEFORE the dialog in the list of parents
class GrapheneGenerator(GeneratorBaseClass, graphene_sheet_dialog):

    cmd = greenmsg("Insert Graphene: ")
    sponsor_keyword = 'Graphenes'

    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        graphene_sheet_dialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        GeneratorBaseClass.__init__(self, win)
        # Validator for the length linedit widget.
        self.validator = QDoubleValidator(self)
        # Range of graphene length (0-1000, 2 decimal places)
        self.validator.setRange(0.0, 1000.0, 2)
        self.length_linedit.setValidator(self.validator)
        self.cursor_pos = 0
        self.lenstr = str(self.length_linedit.text())

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        # Get length from length_linedit and make sure it is not zero.
        # length_linedit's validator makes sure this has a valid number (float).  
        # The only exception is when there is no text.  Mark 051103.
        if not self.length_linedit.text():
            raise Exception("Please specify a valid length.")
        self.length = length = string.atof(str(self.length_linedit.text()))

        if not self.width_linedit.text():
            raise Exception("Please specify a valid width.")
        self.width = width = string.atof(str(self.width_linedit.text()))

        if not self.bond_length_linedit.text():
            raise Exception("Please specify a valid bond length.")
        self.bond_length = bond_length = string.atof(str(self.bond_length_linedit.text()))

        endings = self.endings_combox.currentItem()
        if endings == 2:
            raise Exception("Graphene nitrogen ends not implemented yet.")
        return (length, width, bond_length, endings)

    def build_struct(self, params):
        length, width, bond_length, endings = params
        env.history.message(self.cmd + "Creating graphene.")
        self.chirality = Chirality(n, m)
        PROFILE = False
        if PROFILE:
            sw = Stopwatch()
            sw.start()
        xyz = self.chirality.xyz
        mol = molecule(self.win.assy, gensym("Graphene-"))
        atoms = mol.atoms
        mlimits = self.chirality.mlimits
        # populate the tube with some extra carbons on the ends
        # so that we can trim them later
        self.chirality.populate(mol, length + 4 * Chirality.MAXLEN, members != 0)

        # Apply twist and distortions. Bends probably would come
        # after this point because they change the direction for the
        # length. I'm worried about Z distortion because it will work
        # OK for stretching, but with compression it can fail. BTW,
        # "Z distortion" is a misnomer, we're stretching in the Y
        # direction.
        for atm in atoms.values():
            # twist
            x, y, z = atm.posn()
            twistRadians = twist * y
            c, s = cos(twistRadians), sin(twistRadians)
            x, z = x * c + z * s, -x * s + z * c
            atm.setposn(chem.V(x, y, z))
        for atm in atoms.values():
            # z distortion
            x, y, z = atm.posn()
            y *= (zdist + length) / length
            atm.setposn(chem.V(x, y, z))
        length += zdist
        for atm in atoms.values():
            # xy distortion
            x, y, z = atm.posn()
            # radius is approximate
            radius = 0.7844 * n
            x *= (radius + 0.5 * xydist) / radius
            z *= (radius - 0.5 * xydist) / radius
            atm.setposn(chem.V(x, y, z))


        # Judgement call: because we're discarding carbons with funky
        # valences, we will necessarily get slightly more ragged edges
        # on graphenes. This is a parameter we can fiddle with to
        # adjust the length. My thought is that users would prefer a
        # little extra length, because it's fairly easy to trim the
        # ends, but much harder to add new atoms on the end.
        #LENGTH_TWEAK = 0.5 * Chirality.BONDLENGTH
        LENGTH_TWEAK = Chirality.BONDLENGTH

        # trim all the carbons that fall outside our desired length
        # by doing this, we are introducing new singlets
        for atm in atoms.values():
            y = atm.posn()[1]
            if (y > .5 * (length + LENGTH_TWEAK) or
                y < -.5 * (length + LENGTH_TWEAK)):
                atm.kill()

        # trim all the carbons that only have one carbon neighbor
        for atm in atoms.values():
            if not atm.is_singlet() and len(atm.realNeighbors()) == 1:
                atm.kill()

        # if hydrogen endings, hydrogenate
        if endings == 2:
            for atm in atoms.values():
                y = atm.posn()[1]
                if (y > .5 * (length - LENGTH_TWEAK) or
                    y < -.5 * (length - LENGTH_TWEAK)):
                    atm.Hydrogenate()

        if PROFILE:
            t = sw.now()
            env.history.message(greenmsg("%g seconds to build %d atoms" %
                                         (t, len(atoms.values()))))
        return mol

    def length_fixup(self):
        '''Slot for the Length linedit widget.
        This gets called each time a user types anything into the widget.
        '''
        self.lenstr = double_fixup(self.validator, self.length_linedit.text(), self.lenstr)
        self.length_linedit.setText(self.lenstr)

    ###################################################
    # The done message

    def done_msg(self):
        return "Graphene created."

    ###################################################
    # Special UI things that still must be implemented
    def toggle_graphene_distortion_grpbox(self):
        self.toggle_groupbox(self.graphene_distortion_grpbtn, self.line2,
                             self.length_label, self.length_linedit,
                             self.width_label, self.width_linedit,
                             self.bond_length_label, self.bond_length_linedit,
                             self.endings_label, self.endings_linedit)

    def defaults_btn_clicked(self):
        self.languageChange()
##         self.chirality_m_spinbox.setValue(5)
##         self.chirality_n_spinbox.setValue(5)
##         self.twist_spinbox.setValue(0)
##         self.bend_spinbox.setValue(0)
##         self.mwcnt_count_spinbox.setValue(1)

    def enter_WhatsThisMode(self):
        env.history.message(self.cmd + orangemsg("graphene_sheet_dialog.enter_WhatsThisMode(): Not implemented yet"))
