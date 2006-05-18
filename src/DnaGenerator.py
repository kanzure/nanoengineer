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

# There are three kinds of DNA helix geometries, A, B, and Z. I got my hands
# on a Z file first, so that's what I'm going with.

TWIST_PER_BASE = pi / 6     # in radians
BASE_SPACING = 3.419        # in angstroms
STRAND_B_ANGLE = 0.8 * pi   # in radians

def dnaPiece(mol, atoms, theta, z):
    def rotateTranslate(v, c=cos(theta), s=sin(theta), z=z):
        x = c * v[0] + s * v[1]
        y = -s * v[0] + c * v[1]
        return A((x, y, v[2] + z))
    lst = [ ]
    for elem, pos in atoms:
        lst.append(Atom(elem, rotateTranslate(pos), mol))
    return lst

guanine = [
    #("N", A((-1.417, -5.355, -1.903))),
    ]
adenine = [
    #("N", A((-1.058, -1.845, -0.762))),
    ]
cytosine = [
    #("N", A((-2.058, -1.345, -0.762))),
    ]
thymine = [
    #("N", A((-1.258, -1.645, -0.762))),
    ]

spine = [
    # should we provide hybridizations also?
    ("H", A((-1.417, -5.355, -1.903))),
    ("H", A((-2.61, -4.87, -1.081))),
    ("H", A((-5.063, -4.553, -0.846))),
    ("O", A((-3.058, -2.845, -0.762))),
    ("O", A((-1.099, -6.964, -0.632))),
    ("H", A((-1.133, -2.029, -0.596))),
    ("C", A((-3.008, -4.214, -0.292))),
    ("C", A((-2.088, -2.064, -0.0519997))),
    ("C", A((-4.418, -4.668, 0.0380003))),
    ("H", A((-4.407, -5.723, 0.348))),
    ("O", A((1.061, -6.414, 0.428))),
    ("O", A((-0.772, -4.738, 0.478))),
    ("P", A((-0.37, -6.28, 0.618))),
    ("C", A((-2.023, -4.219, 0.908))),
    ("O", A((-4.908, -3.862, 1.098))),
    ("C", A((-1.88, -2.771, 1.318))),
    ("H", A((-0.884, -2.564, 1.734))),
    ("H", A((-2.416, -4.823, 1.739))),
    ("O", A((-6.399, -5.754, 1.808))),
    ("O", A((-1.007, -6.766, 1.858))),
    ("H", A((-2.65, -2.478, 2.047))),
    ("P", A((-5.758, -4.512, 2.288))),
    ("O", A((-6.887, -3.582, 2.601))),
    ("H", A((-7.241, -3.791, 3.457))),   # hydrogen for end of strand, bondpoint for middl)e
    ("O", A((-4.93, -4.53, 3.478)))
    ]

def makeDna(mol, sequence, spineA, basesA, spineB, basesB):
    sequence = str(sequence).upper()
    # check to make sure all the bases are valid
    for ch in sequence:
        assert ch in 'CGAT'
    theta = 0.0
    z = -0.5 * BASE_SPACING * len(sequence)
    for ch in sequence:
        base = {
            'C': (cytosine, guanine),
            'G': (guanine, cytosine),
            'A': (adenine, thymine),
            'T': (thymine, adenine)
            }[ch]
        if spineA:
            dnaPiece(mol, spine, theta, z)
        if basesA:
            dnaPiece(mol, base[0], theta, z)

        # I am not supremely confident in what follows. The 3'-to-5'
        # direction is reversed for strand B. That probably means that
        # I should be doing a z-flip of the spine, and maybe also the
        # base. Then, to keep handedness consistent, I may need to
        # also x-flip and y-flip things - what a mess, think about it
        # later.

        if spineB:
            dnaPiece(mol, spine, theta + STRAND_B_ANGLE, z)
        if basesB:
            dnaPiece(mol, base[1], theta + STRAND_B_ANGLE, z)
        theta += TWIST_PER_BASE
        z += BASE_SPACING

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
        #try:
        self.buildChunk()
        env.history.message(cmd + "Done.")
        #except:
        #    env.history.message(cmd + "DNA not created, there was a problem.")
            
        QApplication.restoreOverrideCursor() # Restore the cursor
        QDialog.accept(self)

    def reject(self):
        env.history.message(cmd + "DNA not created, there was a problem.")

    def buildChunk(self):
        mol = molecule(self.win.assy, chem.gensym("DNA-"))
        makeDna(mol, self.seq_linedit.text(),
                self.spineAchkbox.isChecked(), self.basesAchkbox.isChecked(),
                self.spineBchkbox.isChecked(), self.basesBchkbox.isChecked())
        inferBonds(mol.atoms.values())

        part = self.win.assy.part
        part.ensure_toplevel_group()
        part.topnode.addchild(mol)
        self.win.mt.mt_update()
