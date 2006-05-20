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
from VQT import A, V, dot, vlen
from bonds import inferBonds
from files_mmp import insertmmp
import re

def rotateTranslate(v, theta, z):
    c, s = cos(theta), sin(theta)
    x = c * v[0] + s * v[1]
    y = -s * v[0] + c * v[1]
    return V(x, y, v[2] + z)

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")

class Dna:
    """This base class may want to provide some provision for the
    fact that we have a two-base periodicity in Z DNA. Or should that
    all be handled there?
    """
    def insertmmp(self, mol, basefile, tfm):
        lst = [ ]
        for line in open(basefile).readlines():
            m = atompat.match(line)
            if m:
                elem = {
                    0: 'X',
                    1: 'H',
                    6: 'C',
                    7: 'N',
                    8: 'O',
                    15: 'P',
                    }[int(m.group(2))]
                xyz = A(map(float, [m.group(3),m.group(4),m.group(5)]))/1000.0
                lst.append(Atom(elem, tfm(xyz), mol))
        return lst

    def make(self, mol, sequence, strandA, strandB):
        sequence = str(sequence).upper()

        if strandA:
            theta = 0.0
            z = 0.5 * self.BASE_SPACING * (len(sequence) - 1)
            for i in range(len(sequence)):
                basename = {
                    'C': 'cytosine',
                    'G': 'guanine',
                    'A': 'adenine',
                    'T': 'thymine',
                    }[sequence[i]]
                if (i & 1) != 0:
                    suffix = 'outer'
                    zoffset = 2.045
                else:
                    suffix = 'inner'
                    zoffset = 0.0
                basefile = 'experimental/zdna-bases/%s-%s.mmp' % (basename, suffix)
                def tfm(v, theta=theta, z1=z+zoffset):
                    return rotateTranslate(v, theta, z1)
                self.insertmmp(mol, basefile, tfm)
                theta -= self.TWIST_PER_BASE
                z -= self.BASE_SPACING

        if strandB:
            theta = self.STRAND_B_ANGLE + (pi / 6) * (len(sequence) - 1)
            z = -2.1 - 0.5 * self.BASE_SPACING * (len(sequence) - 1)
            for i in range(len(sequence)):
                # The 3'-to-5' direction is reversed for strand B.
                j = len(sequence) - 1 - i
                basename = {
                    'G': 'cytosine',
                    'C': 'guanine',
                    'T': 'adenine',
                    'A': 'thymine',
                    }[sequence[j]]
                if (j & 1) != 0:
                    suffix = 'inner'
                    zoffset = 2.045
                    thetaCenter = 0.0
                else:
                    suffix = 'outer'
                    zoffset = 0.0
                    thetaCenter = 0.0
                basefile = 'experimental/zdna-bases/%s-%s.mmp' % (basename, suffix)
                def flip_3_5(v, thetaCenter=thetaCenter):
                    # flip theta, flip z
                    x, y, z = tuple(v)
                    r, theta = (x**2 + y**2) ** 0.5, atan2(y, x)
                    theta = 2 * thetaCenter - theta
                    x, y = r * cos(theta), r * sin(theta)
                    return V(x, y, -z)
                def tfm(v, theta=theta, z1=z+zoffset, flip_3_5=flip_3_5):
                    return rotateTranslate(flip_3_5(v), theta, z1)
                self.insertmmp(mol, basefile, tfm)
                theta += self.TWIST_PER_BASE
                z += self.BASE_SPACING


# There are three kinds of DNA helix geometries, A, B, and Z. I got my hands
# on a Z file first, so that's what I'm going with.

class Unimplemented(Dna):
    def make(self, mol, sequence, strandA, strandB):
        raise Exception("This flavor of DNA is not yet implemented");

class A_Dna(Unimplemented):
    pass

class B_Dna(Unimplemented):
    pass


class Z_Dna(Dna):

    # Z-DNA has a periodicity of two bases. The odd-numbered basis
    # have one orientation, the even-numbered bases have another.

    TWIST_PER_BASE = pi / 6     # in radians
    BASE_SPACING = 3.715        # in angstroms
    # This value for the strand B angle really surprises me. I don't understand it.
    STRAND_B_ANGLE = 0.5 * pi

    # Take care of the directory name, and the alternation of inner and
    # outer bases, which won't occur in A and B DNA.

#################################

cmd = greenmsg("Insert Dna: ")

class DnaGenerator(DnaGeneratorDialog):

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        DnaGeneratorDialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        self.win = win
        
        # Default DNA parameters
        self.strandAchkbox.setChecked(True)
        self.strandBchkbox.setChecked(True)
        self.seq_linedit.setText('GATTACA')

    def accept(self):
        'Slot for the OK button'

        env.history.message(cmd + "Creating DNA. This may take a moment...")
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        if False:
            try:
                self.buildChunk()
                env.history.message(cmd + "Done.")
            except Exception, e:
                env.history.message(cmd + redmsg(str(e.args[0])))
        else:
            self.buildChunk()
            env.history.message(cmd + "Done.")
            
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
                 self.strandAchkbox.isChecked(), self.strandBchkbox.isChecked())
        inferBonds(mol)
        part = self.win.assy.part
        part.ensure_toplevel_group()
        part.topnode.addchild(mol)
        self.win.mt.mt_update()
