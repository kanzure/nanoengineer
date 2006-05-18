# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
DnaGenerator.py

$Id$

http://en.wikipedia.org/wiki/DNA
http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif
"""

__author__ = "Will"

from DnaGeneratorDialog import DnaGeneratorDialog
from math import atan2, sin, cos, pi
import assembly, chem, bonds, Utility
from chem import molecule, Atom
import env
from HistoryWidget import redmsg, greenmsg
from qt import Qt, QApplication, QCursor, QDialog, QDoubleValidator, QValidator
from VQT import A, dot, vlen
from bonds import inferBonds


def rotateTranslate(v, theta, z):
    c, s = cos(theta), sin(theta)
    x = c * v[0] + s * v[1]
    y = -s * v[0] + c * v[1]
    return A((x, y, v[2] + z))

def addAtoms(mol, atoms, transforms=[ ]):
    lst = [ ]
    for elem, pos in atoms:
        for T in transforms:
            pos = T(pos)
        lst.append(Atom(elem, pos, mol))
    return lst

class Dna:
    """This base class may want to provide some provision for the
    fact that we have a two-base periodicity in Z DNA. Or should that
    all be handled there?
    """
    def make(self, mol, sequence, spineA, basesA, spineB, basesB):
        sequence = str(sequence).upper()
        # check to make sure all the bases are valid
        for ch in sequence:
            assert ch in 'CGAT'
        theta = 0.0
        z = -0.5 * self.BASE_SPACING * len(sequence)

        for i in range(len(sequence)):
            def dnaPiece(mol, atoms, theta, z):
                addAtoms(mol, atoms,
                         [ lambda v: rotateTranslate(v, theta, z) ])
            if spineA:
                dnaPiece(mol, self.spine(i), theta, z)
            if basesA:
                ch = sequence[i]
                if ch == 'C':
                    base = self.cytosine(i)
                elif ch == 'G':
                    base = self.guanine(i)
                elif ch == 'A':
                    base = self.adenine(i)
                elif ch == 'T':
                    base = self.thymine(i)
                dnaPiece(mol, base, theta, z)

            # The 3'-to-5' direction is reversed for strand B.
            def dnaPiece(mol, atoms, theta, z, off=self.STRAND_B_ANGLE):
                thetaAverage = 0.
                if len(atoms) > 0:
                    for a in atoms:
                        thetaAverage += atan2(a[1][1], a[1][0])
                    thetaAverage /= len(atoms)
                def flip_3_5(v):
                    x, y = v[0], v[1]
                    r = (x**2 + y**2) ** .5
                    theta = atan2(y, x)
                    # flip theta
                    theta = 2 * thetaAverage - theta
                    x, y = r * cos(theta), r * sin(theta)
                    # flip z
                    return A((x, y, -v[2]))
                addAtoms(mol, atoms, [
                    flip_3_5,
                    lambda v: rotateTranslate(v, theta + off, z)
                    ])
            if spineB:
                dnaPiece(mol, self.spine(i), theta, z)
            if basesB:
                ch = sequence[len(sequence) - 1 - i]
                if ch == 'C':
                    base = self.guanine(i)
                elif ch == 'G':
                    base = self.cytosine(i)
                elif ch == 'A':
                    base = self.thymine(i)
                elif ch == 'T':
                    base = self.adenine(i)
                dnaPiece(mol, base, theta, z)

            theta += self.TWIST_PER_BASE
            z += self.BASE_SPACING


# There are three kinds of DNA helix geometries, A, B, and Z. I got my hands
# on a Z file first, so that's what I'm going with.

class Unimplemented(Dna):
    def make(self, mol, sequence, spineA, basesA, spineB, basesB):
        raise Exception("This flavor of DNA is not yet implemented");

class A_Dna(Unimplemented):
    pass

class B_Dna(Unimplemented):
    pass


class Z_Dna(Dna):

    # Z-DNA has a periodicity of two bases. The odd-numbered basis
    # have one orientation, the even-numbered bases have another.

    TWIST_PER_BASE = pi / 6     # in radians
    BASE_SPACING = 3.419        # in angstroms
    STRAND_B_ANGLE = pi   # in radians - what's the real value????????

    def guanine(self, i):
        if (i & 1) == 1:
            return [
                ('H', A((2.36815, 4.15432, -0.593812))),
                ('C', A((2.3462, 3.08156, -0.404812))),
                ('X', A((0.623164, 2.65709, -0.341812))),
                ('N', A((1.3056, 2.39943, -0.292813))),
                ('N', A((3.42781, 2.31186, -0.259812))),
                ('C', A((2.95308, 1.08161, -0.0798125))),
                ('O', A((4.86438, -0.402678, -0.0648125))),
                ('C', A((1.5568, 1.09511, -0.0638125))),
                ('C', A((3.64512, -0.180686, -0.0058125))),
                ('N', A((0.740102, 0.0305682, 0.0991875))),
                ('N', A((2.79502, -1.2282, 0.151188))),
                ('H', A((3.18495, -2.14649, 0.217188))),
                ('C', A((1.38805, -1.09358, 0.227188))),
                ('N', A((0.709407, -2.27189, 0.422188))),
                ('H', A((-0.319974, -2.27228, 0.468188))),
                ('H', A((1.22966, -3.15474, 0.522188))),
                ]
        else:
            return [
                ('X', A((7.27816, 1.42653, -0.20375))),
                ('N', A((7.00803, 0.749392, -0.15275))),
                ('C', A((7.75835, -0.366205, -0.10175))),
                ('H', A((8.84738, -0.356071, -0.08875))),
                ('N', A((7.04431, -1.46907, -0.07175))),
                ('N', A((4.58836, 1.10329, -0.07175))),
                ('C', A((5.67748, 0.33913, -0.06275))),
                ('H', A((2.33379, 2.07418, -0.05075))),
                ('C', A((3.45399, 0.403295, 0.01825))),
                ('N', A((2.33653, 1.04672, 0.01825))),
                ('C', A((5.74532, -1.01897, 0.02825))),
                ('H', A((1.44658, 0.53328, 0.08625))),
                ('N', A((3.40448, -0.949823, 0.11825))),
                ('C', A((4.53719, -1.75386, 0.12825))),
                ('H', A((2.50933, -1.38969, 0.18825))),
                ('O', A((4.40774, -3.00041, 0.21825))),
                ]

    def adenine(self, i):
        if (i & 1) == 1:
            return [
                ('H', A((3.26716, 3.51455, -0.4996))),
                ('C', A((3.00341, 2.47547, -0.3106))),
                ('X', A((1.22903, 2.45115, -0.2486))),
                ('N', A((1.83563, 2.04601, -0.1986))),
                ('N', A((3.88321, 1.48136, -0.1656))),
                ('H', A((5.54399, -0.899402, -0.0926))),
                ('C', A((3.14289, 0.390127, 0.0144))),
                ('N', A((4.72424, -1.51088, 0.0264))),
                ('C', A((1.78574, 0.718651, 0.0304))),
                ('C', A((3.53192, -0.995858, 0.0884))),
                ('H', A((4.84907, -2.5308, 0.0964))),
                ('N', A((0.749696, -0.133913, 0.1934))),
                ('N', A((2.4672, -1.8243, 0.2454))),
                ('C', A((1.12699, -1.37536, 0.3214))),
                ('H', A((0.358217, -2.11871, 0.4994))),
                ]
        else:
            return [
                ('X', A((7.00976, 2.40349, -0.223133))),
                ('N', A((6.8358, 1.69512, -0.171133))),
                ('C', A((7.73327, 0.69537, -0.121133))),
                ('H', A((8.81036, 0.855919, -0.107133))),
                ('N', A((7.17897, -0.496442, -0.0911333))),
                ('N', A((4.39011, 1.70973, -0.0911333))),
                ('C', A((5.57484, 1.10481, -0.0811333))),
                ('H', A((2.36039, 1.26932, -0.00813333))),
                ('C', A((3.36405, 0.859793, -0.00113333))),
                ('C', A((5.83045, -0.231667, 0.00886667))),
                ('N', A((3.50282, -0.487446, 0.0988667))),
                ('C', A((4.73539, -1.1266, 0.108867))),
                ('N', A((4.78224, -2.42222, 0.201867))),
                ('H', A((5.69113, -2.90589, 0.209867))),
                ('H', A((3.90913, -2.96578, 0.266867))),
                ]

    def cytosine(self, i):
        if (i & 1) == 1:
            return [
                ('H', A((-3.61585, 3.22005, -0.412846))),
                ('H', A((-2.18885, 5.17738, -0.251846))),
                ('C', A((-2.54864, 3.09508, -0.230846))),
                ('X', A((-2.44809, 1.23023, -0.150846))),
                ('C', A((-1.77571, 4.17525, -0.140846))),
                ('N', A((-2.03857, 1.83344, -0.100846))),
                ('N', A((0.13322, 2.71992, 0.0391538))),
                ('C', A((-0.370539, 3.96655, 0.109154))),
                ('C', A((-0.674962, 1.63326, 0.139154))),
                ('N', A((0.455195, 5.01207, 0.219154))),
                ('H', A((1.47347, 4.86321, 0.246154))),
                ('O', A((-0.210573, 0.504413, 0.259154))),
                ('H', A((0.0720632, 5.96691, 0.276154))),
                ]
        else:
            return [
                ('X', A((6.94728, 2.54227, -0.150231))),
                ('N', A((6.78703, 1.83159, -0.0992308))),
                ('H', A((8.8419, 1.21753, -0.0852308))),
                ('C', A((7.8088, 0.874227, -0.0562308))),
                ('C', A((5.48011, 1.33251, -0.0172308))),
                ('C', A((7.57639, -0.442184, 0.0187692))),
                ('N', A((5.20198, 0.0121067, 0.0257692))),
                ('O', A((4.57819, 2.20013, 0.0277692))),
                ('C', A((6.21644, -0.865972, 0.0367692))),
                ('H', A((8.39435, -1.15964, 0.0637692))),
                ('N', A((5.92108, -2.16032, 0.0697692))),
                ('H', A((4.93667, -2.46373, 0.0827692))),
                ('H', A((6.67652, -2.86078, 0.0827692))),
                ]

    def thymine(self, i):
        if (i & 1) == 1:
            return [
                ('H', A((6.29496, 0.809827, -0.998867))),
                ('H', A((6.40842, -0.890711, -0.429867))),
                ('H', A((4.34223, 2.13089, -0.300867))),
                ('C', A((6.03433, 0.114881, -0.186867))),
                ('C', A((3.82887, 1.18857, -0.118867))),
                ('X', A((2.06117, 1.7911, -0.0378667))),
                ('C', A((4.54263, 0.0684204, -0.0288667))),
                ('N', A((2.46802, 1.18609, 0.0111333))),
                ('H', A((1.99494, -2.02479, 0.0231333))),
                ('N', A((2.48013, -1.15963, 0.151133))),
                ('C', A((3.8247, -1.1574, 0.221133))),
                ('C', A((1.7735, -0.004355, 0.251133))),
                ('O', A((4.42821, -2.21222, 0.321133))),
                ('O', A((0.552902, -0.0140027, 0.371133))),
                ('H', A((6.49188, 0.459056, 0.752133))),
                ]
        else:
            return [
                ('H', A((9.50481, -1.22601, -0.622267))),
                ('H', A((8.34882, -2.54067, -0.222267))),
                ('X', A((6.98882, 2.43061, -0.162267))),
                ('N', A((6.81797, 1.72188, -0.111267))),
                ('H', A((8.86387, 1.07693, -0.0972667))),
                ('C', A((7.82617, 0.749271, -0.0682667))),
                ('C', A((5.50428, 1.24205, -0.0292667))),
                ('C', A((7.5742, -0.563048, 0.00673333))),
                ('N', A((5.20649, -0.0744374, 0.0137333))),
                ('O', A((4.6158, 2.12264, 0.0157333))),
                ('C', A((6.2079, -0.966611, 0.0247333))),
                ('H', A((4.2541, -0.378932, 0.0367333))),
                ('O', A((5.91919, -2.15194, 0.0547333))),
                ('C', A((8.70976, -1.54311, 0.0677333))),
                ('H', A((9.10677, -1.58056, 1.09273))),
                ]

    def spine(self, i):
        if (i & 1) == 1:
            return [
                ('H', A((6.70073, -1.29877, -3.34071))),
                ('H', A((8.40993, -0.819175, -3.06771))),
                ('C', A((7.43502, -0.978617, -2.58671))),
                ('X', A((7.31755, 0.893101, -2.15871))),
                ('H', A((5.87989, 0.370838, -1.95571))),
                ('C', A((6.97224, 0.266942, -1.87671))),
                ('H', A((8.44861, -2.62733, -1.59471))),
                ('C', A((7.54404, -2.0225, -1.43671))),
                ('X', A((6.93535, -2.49509, -1.38171))),
                ('C', A((7.41659, 0.103284, -0.386714))),
                ('H', A((8.35365, 0.658526, -0.231714))),
                ('O', A((7.65125, -1.29345, -0.196714))),
                ('H', A((6.07295, 1.62621, 0.328286))),
                ('C', A((6.39758, 0.614469, 0.613286))),
                ('H', A((5.52644, -0.0578401, 0.632286))),
                ('O', A((7.00658, 0.649832, 1.90229))),
                ('O', A((5.9367, 2.60606, 2.96229))),
                ('O', A((4.76934, 0.413364, 3.01229))),
                ('P', A((6.16271, 1.18579, 3.15229))),
                ('X', A((4.67622, -0.235523, 3.21929))),
                ('O', A((6.79221, 0.688987, 4.39229))),
                ]
        else:
            return [
                ('H', A((5.35481, 1.28344, -1.98948))),
                ('H', A((6.75384, -0.754915, -1.75448))),
                ('O', A((4.14479, -0.399751, -1.67048))),
                ('H', A((2.25262, 0.491903, -1.50448))),
                ('C', A((5.13189, 0.550131, -1.20048))),
                ('C', A((2.91526, -0.198025, -0.960476))),
                ('X', A((2.57837, -0.892397, -0.907476))),
                ('C', A((6.41025, -0.198221, -0.870476))),
                ('H', A((7.18863, 0.514016, -0.560476))),
                ('X', A((4.23581, 1.98112, -0.232476))),
                ('C', A((4.47833, 1.28842, -0.00047619))),
                ('O', A((6.13611, -1.10076, 0.189524))),
                ('C', A((3.30434, 0.428989, 0.409524))),
                ('H', A((2.48542, 1.03415, 0.825524))),
                ('H', A((5.19045, 1.39671, 0.830524))),
                ('O', A((8.54033, -0.950882, 0.899524))),
                ('H', A((3.59924, -0.340284, 1.13852))),
                ('P', A((7.18725, -1.30104, 1.37952))),
                ('O', A((7.19779, -2.88942, 1.57852))),
                ('X', A((6.63476, -3.19442, 1.83152))),
                ('O', A((6.6487, -0.671855, 2.56852))),
                ]

#################################

cmd = greenmsg("Insert Dna: ")

class DnaGenerator(DnaGeneratorDialog):

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        DnaGeneratorDialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        self.win = win
        
        # Default DNA parameters
        self.spineAchkbox.setChecked(True)
        self.basesAchkbox.setChecked(True)
        self.spineBchkbox.setChecked(True)
        self.basesBchkbox.setChecked(True)
        self.seq_linedit.setText('GATTACA')

    def accept(self):
        'Slot for the OK button'

        env.history.message(cmd + "Creating DNA. This may take a moment...")
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        try:
            self.buildChunk()
            env.history.message(cmd + "Done.")
        except Exception, e:
            env.history.message(cmd + redmsg(e.args[0]))
            
        QApplication.restoreOverrideCursor() # Restore the cursor
        QDialog.accept(self)

    def reject(self):
        env.history.message(cmd + "DNA not created, there was a problem.")

    def buildChunk(self):
        mol = molecule(self.win.assy, chem.gensym("DNA-"))
        # dna = A_Dna()
        # dna = B_Dna()
        dna = Z_Dna()
        dna.make(mol, self.seq_linedit.text(),
                 self.spineAchkbox.isChecked(), self.basesAchkbox.isChecked(),
                 self.spineBchkbox.isChecked(), self.basesBchkbox.isChecked())
        inferBonds(mol)

        part = self.win.assy.part
        part.ensure_toplevel_group()
        part.topnode.addchild(mol)
        self.win.mt.mt_update()
