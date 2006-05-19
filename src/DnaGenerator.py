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
from VQT import V, dot, vlen
from bonds import inferBonds
from files_mmp import insertmmp


def rotateTranslate(v, theta, z):
    c, s = cos(theta), sin(theta)
    x = c * v[0] + s * v[1]
    y = -s * v[0] + c * v[1]
    return V(x, y, v[2] + z)

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
    def make(self, assy, sequence, strandA, strandB):
        sequence = str(sequence).upper()

        theta = 0.0
        z = -0.5 * self.BASE_SPACING * (len(sequence) - 1)
        if strandA:
            for i in range(len(sequence)):
                basename, zInner, zOuter = {
                    #'C': ('cytosine', 2.7, -0.3),
                    #'G': ('guanine',  0.3, 2.4),
                    #'A': ('adenine',  0.9, 0.9),
                    #'T': ('thymine',  2.1, 1.6),
                    'C': ('cytosine', -1.656, -2.275),
                    'G': ('guanine',  -4.024, 0.685),
                    'A': ('adenine',  -3.432, -1.091),
                    'T': ('thymine',  -2.248, -0.499),
                    }[sequence[i]]
                if (i & 1) != 0:
                    suffix = 'outer'
                else:
                    suffix = 'inner'
                basefile = 'experimental/zdna-bases/%s-%s.mmp' % (basename, suffix)
                def tfm(v, theta=theta, z=z):
                    return rotateTranslate(v, theta, z)
                # ignore mol??
                insertmmp(assy, basefile, tfm)
                theta += self.TWIST_PER_BASE
                z += self.BASE_SPACING

        theta = self.STRAND_B_ANGLE
        z = -0.5 * self.BASE_SPACING * (len(sequence) - 1)
        if strandB:
            for i in range(len(sequence)):
            # The 3'-to-5' direction is reversed for strand B.
                basename, zInner, zOuter = {
                    'G': ('cytosine', 2.7, -0.3),
                    'C': ('guanine',  0.3, 2.4),
                    'T': ('adenine',  0.9, 0.9),
                    'A': ('thymine',  2.1, 1.6),
                    }[sequence[i]]
                # outer/inner is flipped from strand A
                if (i & 1) == 0:
                    suffix = 'outer'
                else:
                    suffix = 'inner'
                basefile = 'experimental/zdna-bases/%s-%s.mmp' % (basename, suffix)
                def flip_3_5(v):
                    # flip theta, flip z
                    # theta is atan2(y,x) so flipping y will work
                    # any discrepancy can be folded into STRAND_B_ANGLE
                    return V(v[0], -v[1], -v[2])
                def tfm(v, theta=theta, z=z, flip_3_5=flip_3_5):
                    return rotateTranslate(flip_3_5(v), theta, z)
                insertmmp(assy, basefile, tfm)
                theta += self.TWIST_PER_BASE
                z += self.BASE_SPACING


# There are three kinds of DNA helix geometries, A, B, and Z. I got my hands
# on a Z file first, so that's what I'm going with.

class Unimplemented(Dna):
    def make(self, assy, sequence, strandA, strandB):
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
    STRAND_B_ANGLE = pi   # in radians - what's the real value????????

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
        # dna = A_Dna()
        # dna = B_Dna()
        dna = Z_Dna()
        dna.make(self.win.assy, self.seq_linedit.text(),
                 self.strandAchkbox.isChecked(), self.strandBchkbox.isChecked())
        part = self.win.assy.part
        part.ensure_toplevel_group()
        #part.topnode.addchild(mol)
        self.win.mt.mt_update()
