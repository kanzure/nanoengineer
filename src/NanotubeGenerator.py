# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
NanotubeGenerator.py

$Id$

See http://www.nanoengineer-1.net/mediawiki/index.php?title=Nanotube_generator_dialog
for notes about what's going on here.
"""

__author__ = "Will"

from NanotubeGeneratorDialog import nanotube_dialog
from math import atan2, sin, cos, pi, asin
import assembly, chem, bonds, Utility
from chem import molecule, Atom
import env
from HistoryWidget import redmsg, orangemsg, greenmsg
from qt import Qt, QApplication, QCursor, QDialog, QDoubleValidator, QValidator
from VQT import dot, vlen, cross, norm
import random
import string
from widgets import double_fixup
from debug import Stopwatch, objectBrowse
from Utility import Group
from GeneratorBaseClass import GeneratorBaseClass
from elements import PeriodicTable
from bonds import bonded, bond_atoms, V_GRAPHITE, NeighborhoodGenerator
from bonds_from_atoms import make_bonds
from buckyball import BuckyBall
from OpenGL.quaternion import quaternion
import platform

sqrt3 = 3 ** 0.5

class Chirality:

    def __init__(self, n, m, bond_length=1.40):
        self.bond_length = bond_length
        self.maxlen = maxlen = 1.2 * bond_length
        self.maxlensq = maxlen**2
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
        denom = F * J - G * H
        self.R = (bond_length**2 * (F - H) / denom) ** .5
        self.B = (bond_length**2 * (J - G) / denom) ** .5
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

        # m goes axially along the nanotube, n spirals around the tube
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
                if dot(diff, diff) < self.maxlensq:
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

####################################################################
# Endcaps

from debug import linenum
import Numeric

def add_endcap(mol, length, radius):
    BONDLENGTH = 1.402
    def newtonsMethod(start, errfunc, steps):
        # Works with vectors of any size
        dimensions = Numeric.size(start)
        p = start
        for i in range(steps):
            h = 1.0e-4
            e0 = errfunc(p)
            gradient = p.copy()  # all components will be replaced
            for j in range(dimensions):
                p1 = p.copy()
                p1[j] += h
                gradient[j] = (errfunc(p1) - e0) / h
            if vlen(gradient) < 1.0e-15:
                return p, e0
            p = p - (e0 / vlen(gradient)**2) * gradient
        return p, errfunc(p)
    # The error function relates to the bonds we want to bond to.
    # Start with the +Y end of the tube.
    def is_north(atm):
        return atm.posn()[1] > length / 2 - 3.0
    def is_south(atm):
        return atm.posn()[1] < -length / 2 + 3.0
    regional_singlets = filter(lambda atm: is_north(atm) and atm.is_singlet(),
                               mol.atoms.values())
    desired_bonds = [ ]
    bond_y_top = -1.0e20
    bond_y_bottom = 1.0e20
    for sing in regional_singlets:
        sp = sing.posn()
        op = sing.realNeighbors()[0].posn()
        # extend the bond from the owner until its BONDLENGTH long
        d = sp - op
        sp = op + (BONDLENGTH / vlen(d)) * d
        desired_bonds.append((op, sp))
        bond_y_top = max(sp[1], op[1], bond_y_top)
        bond_y_bottom = min(sp[1], op[1], bond_y_top)
    divider = (bond_y_top + bond_y_bottom) / 2

    # So I want the bonds on the buckyball to approach these as closely as
    # possible. Given that I know the radius of the buckyball, I can put it
    # at the y coordinate I want easily.
    bball = BuckyBall(2)
    br = bball.radius()
    if br < radius:
        ypos = length / 2
    else:
        ypos = length / 2 - (br**2 - radius**2)**.5
    def moveball(theta, phi):
        lst = [ ]
        ct, st = cos(theta), sin(theta)
        cp, sp = cos(phi), sin(phi)
        for vec in bball.carbons():
            x, y, z = vec
            x, y = ct * x + st * y, -st * x + ct * y
            x, z = cp * x + sp * z, -sp * x + cp * z
            y += ypos
            lst.append(chem.V(x, y, z))
        return lst
    def errfunc(anglevec):
        theta, phi = anglevec
        lst = moveball(theta, phi)
        above = [ ]
        below = [ ]
        bonds = [ ]
        for i, j in bball.bondlist():
            ipos, jpos = lst[i], lst[j]
            if ((ipos[1] < divider and jpos[1] > divider) or
                (ipos[1] > divider and jpos[1] < divider)):
                bonds.append((ipos, jpos))
        # now for each of the desired bonds, find the closest-fitting
        # buckyball bond
        totalerr = 0.0
        for a, b in desired_bonds:
            bestfit = 1.0e20
            for c, d in bonds:
                bestfit = min(bestfit,
                              vlen(a - c)**2 + vlen(b - d)**2,
                              vlen(a - d)**2 + vlen(b - c)**2)
            totalerr += bestfit
        return totalerr
    minerror = 1.0e20
    bestvec = None
    for i in range(30):
        theta = pi * (2 * random.random() - 1)
        phi = pi * (2 * random.random() - 1)
        z = Numeric.array([theta, phi])
        z, err = newtonsMethod(z, errfunc, 5)
        if err < minerror:
            minerror = err
            bestvec = z
    theta, phi = bestvec

    # kill the old atoms above the divider
    for atm in mol.atoms.values():
        if atm.posn()[1] >= divider:
            atm.kill()

    atoms = [ ]
    positions = filter(lambda vec: vec[1] > divider,
                       moveball(theta, phi))
    for newpos in positions:
        newguy = Atom('C', newpos, mol)
        atoms.append(newguy)
        newguy.set_atomtype('sp2')

    maxradius = 1.5 * BONDLENGTH

    make_bonds(mol.atoms.values(), V_GRAPHITE)
    for atm in mol.atoms.values():
        for s in atm.singNeighbors():
            s.kill()
        atm.make_enough_singlets()
    env.history.message(orangemsg('Nanotube endcap generation is an inexact science. ' +
                                  'Manual touch-up will be required.'))

#################################################################

# GeneratorBaseClass must come BEFORE the dialog in the list of parents
class NanotubeGenerator(GeneratorBaseClass, nanotube_dialog):

    cmd = greenmsg("Insert Nanotube: ")
    sponsor_keyword = 'Nanotubes'
    prefix = 'Nanotube-'   # used for gensym

    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Nanotubes', 'Carbon')

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        nanotube_dialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        GeneratorBaseClass.__init__(self, win)
        # Validator for the length linedit widget.
        self.validator = QDoubleValidator(self)
        # Range of nanotube length (0-1000, 2 decimal places)
        # also used to validate bond length
        self.validator.setRange(0.0, 1000.0, 2)
        self.length_linedit.setValidator(self.validator)
        self.bond_length_linedit.setValidator(self.validator)
        self.cursor_pos = 0
        self.lenstr = str(self.length_linedit.text())
        self.blstr = str(self.bond_length_linedit.text())
        self.zstr = str(self.z_distortion_linedit.text())
        self.xystr = str(self.xy_distortion_linedit.text())
        self.spstr = str(self.mwcnt_spacing_linedit.text())

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        n = self.chirality_n_spinbox.value()
        m = self.chirality_m_spinbox.value()
        assert n > 0, 'n cannot be zero'
        assert n >= m, 'n cannot be smaller than m'
        # Get length from length_linedit and make sure it is not zero.
        # length_linedit's validator makes sure this has a valid number (float).  
        # The only exception is when there is no text.  Mark 051103.
        def fetch(name, linedit):
            x = str(linedit.text())
            if not x:
                raise Exception("Please specify a valid " + name)
            return string.atof(x.split(' ')[0])

        self.length = length = fetch('length', self.length_linedit)
        self.bond_length = bond_length = fetch('bond length', self.bond_length_linedit)
        self.zdist = zdist = fetch('Z distortion', self.z_distortion_linedit)
        self.xydist = xydist = fetch('XY distortion', self.xy_distortion_linedit)
        self.spacing = spacing = fetch('spacing', self.mwcnt_spacing_linedit)

        twist = pi * self.twist_spinbox.value() / 180.0
        bend = pi * self.bend_spinbox.value() / 180.0
        members = self.members_combox.currentItem()
        endings = self.endings_combox.currentItem()
        if endings == 1 and not platform.atom_debug:
            raise Exception('Nanotube endcaps not implemented yet.')
        numwalls = self.mwcnt_count_spinbox.value()
        return (length, n, m, bond_length, zdist, xydist,
                twist, bend, members, endings, numwalls, spacing)

    def build_struct(self, params, mol=None):
        length, n, m, bond_length, zdist, xydist, \
                twist, bend, members, endings, numwalls, spacing = params
        # This can take a few seconds. Inform the user.
        # 100 is a guess on my part. Mark 051103.
        if length > 100.0:
            env.history.message(self.cmd + "Creating nanotube. This may take a moment...")
        else: # Nanotubes under 100 Angstroms shouldn't take long.
            env.history.message(self.cmd + "Creating nanotube.")
        self.chirality = Chirality(n, m, bond_length)
        PROFILE = False
        if PROFILE:
            sw = Stopwatch()
            sw.start()
        xyz = self.chirality.xyz
        if mol == None:
            mol = molecule(self.win.assy, self.name)
        atoms = mol.atoms
        mlimits = self.chirality.mlimits
        # populate the tube with some extra carbons on the ends
        # so that we can trim them later
        self.chirality.populate(mol, length + 4 * self.chirality.maxlen, members != 0)

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
            radius = self.chirality.R
            x *= (radius + 0.5 * xydist) / radius
            z *= (radius - 0.5 * xydist) / radius
            atm.setposn(chem.V(x, y, z))


        # Judgement call: because we're discarding carbons with funky
        # valences, we will necessarily get slightly more ragged edges
        # on nanotubes. This is a parameter we can fiddle with to
        # adjust the length. My thought is that users would prefer a
        # little extra length, because it's fairly easy to trim the
        # ends, but much harder to add new atoms on the end.
        LENGTH_TWEAK = bond_length

        # trim all the carbons that fall outside our desired length
        # by doing this, we are introducing new singlets
        for atm in atoms.values():
            y = atm.posn()[1]
            if (y > .5 * (length + LENGTH_TWEAK) or
                y < -.5 * (length + LENGTH_TWEAK)):
                atm.kill()

        # Apply bend. Equations are anomalous for zero bend.
        if abs(bend) > pi / 360:
            R = length / bend
            for atm in atoms.values():
                x, y, z = atm.posn()
                theta = y / R
                x, y = R - (R - x) * cos(theta), (R - x) * sin(theta)
                atm.setposn(chem.V(x, y, z))

        def trimCarbons():
            # trim all the carbons that only have one carbon neighbor
            for i in range(2):
                for atm in atoms.values():
                    if not atm.is_singlet() and len(atm.realNeighbors()) == 1:
                        atm.kill()

        trimCarbons()
        # if we're not picky about endings, we don't need to trim carbons
        if endings == 1:
            # buckyball endcaps
            add_endcap(mol, length, self.chirality.R)
        if endings == 2:
            # hydrogen terminations
            for atm in atoms.values():
                atm.Hydrogenate()
        elif endings == 3:
            # nitrogen terminations
            dstElem = PeriodicTable.getElement('N')
            atomtype = dstElem.find_atomtype('sp2')
            for atm in atoms.values():
                if len(atm.realNeighbors()) == 2:
                    atm.Transmute(dstElem, force=True, atomtype=atomtype)

        if PROFILE:
            t = sw.now()
            env.history.message(greenmsg("%g seconds to build %d atoms" %
                                         (t, len(atoms.values()))))

        if numwalls > 1:
            n += int(spacing * 3 + 0.5)  # empirical tinkering
            params = (length, n, m, bond_length, zdist, xydist,
                      twist, bend, members, endings, numwalls-1, spacing)
            self.build_struct(params, mol=mol)

        return mol

    def length_fixup(self):
        '''Slot for the Length linedit widget.
        This gets called each time a user types anything into the widget.
        '''
        self.lenstr = double_fixup(self.validator, self.length_linedit.text(), self.lenstr)
        self.length_linedit.setText(self.lenstr)
        self.blstr = double_fixup(self.validator, self.bond_length_linedit.text(), self.blstr)
        self.bond_length_linedit.setText(self.blstr)
        self.zstr = double_fixup(self.validator, self.z_distortion_linedit.text(), self.zstr)
        self.z_distortion_linedit.setText(self.zstr)
        self.xystr = double_fixup(self.validator, self.xy_distortion_linedit.text(), self.xystr)
        self.xy_distortion_linedit.setText(self.xystr)
        self.spstr = double_fixup(self.validator, self.mwcnt_spacing_linedit.text(), self.spstr)
        self.mwcnt_spacing_linedit.setText(self.spstr)

    ###################################################
    # The done message

    def done_msg(self):
        return "Nanotube created."

    ###################################################
    # Special UI things that still must be implemented
    def toggle_nt_distortion_grpbox(self):
        self.toggle_groupbox(self.nt_distortion_grpbtn, self.line2_2,
                             self.z_distortion_label, self.z_distortion_linedit,
                             self.xy_distortion_label, self.xy_distortion_linedit,
                             self.twist_label, self.twist_spinbox,
                             self.bend_label, self.bend_spinbox)

    def toggle_nt_parameters_grpbox(self):
        self.toggle_groupbox(self.nt_parameters_grpbtn, self.line2,
                             self.chirality_n_label, self.chirality_n_spinbox,
                             self.chirality_m_label, self.chirality_m_spinbox,
                             self.length_label, self.length_linedit,
                             self.members_label, self.members_combox,
                             self.endings_label, self.endings_combox,
                             self.bond_length_label, self.bond_length_linedit)

    def toggle_mwcnt_grpbox(self):
        self.toggle_groupbox(self.mwcnt_grpbtn, self.line2_3,
                             self.mwcnt_spacing_label, self.mwcnt_spacing_linedit,
                             self.mwcnt_count_label, self.mwcnt_count_spinbox)

    def defaults_btn_clicked(self):
        self.languageChange()
        self.chirality_m_spinbox.setValue(5)
        self.chirality_n_spinbox.setValue(5)
        self.twist_spinbox.setValue(0)
        self.bend_spinbox.setValue(0)
        self.mwcnt_count_spinbox.setValue(1)
