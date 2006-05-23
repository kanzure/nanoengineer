# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
DnaGenerator.py

$Id$

http://en.wikipedia.org/wiki/DNA
http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif
"""

__author__ = "Will"

from DnaGeneratorDialog import dna_dialog
from math import atan2, sin, cos, pi
from chem import molecule, Atom, gensym
import env
import os
from HistoryWidget import redmsg, orangemsg, greenmsg
from qt import Qt, QApplication, QCursor, QDialog
from VQT import A, V, dot, vlen
from bonds import inferBonds
import re

DEBUG = True

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")

class Dna:

    baseCache = { }

    def insertmmp(self, mol, basefile, tfm):
        if self.baseCache.has_key(basefile):
            base = self.baseCache[basefile]
        else:
            base = [ ]
            if not os.path.exists(basefile):
                raise Exception("can't find file: " + basefile)
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
                    base.append((elem, xyz))
            self.baseCache[basefile] = base
        lst = [ ]
        for elem, xyz in base:
            lst.append(Atom(elem, tfm(xyz), mol))
        return lst

    def make(self, mol, sequence, doubleStrand,
             basenameA={'C': 'cytosine',
                        'G': 'guanine',
                        'A': 'adenine',
                        'T': 'thymine'},
             basenameB={'G': 'cytosine',
                        'C': 'guanine',
                        'T': 'adenine',
                        'A': 'thymine'}):
        for ch in sequence:
            if ch not in 'GACT':
                raise Exception('Unknown DNA base (not G, A, C, or T): ' + ch)

        def rotateTranslate(v, theta, z):
            c, s = cos(theta), sin(theta)
            x = c * v[0] + s * v[1]
            y = -s * v[0] + c * v[1]
            return V(x, y, v[2] + z)

        theta = 0.0
        z = 0.5 * self.BASE_SPACING * (len(sequence) - 1)
        for i in range(len(sequence)):
            basefile, zoffset, thetaOffset = \
                      self.strandAinfo(basenameA[sequence[i]], i)
            def tfm(v, theta=theta+thetaOffset, z1=z+zoffset):
                return rotateTranslate(v, theta, z1)
            self.insertmmp(mol, basefile, tfm)
            theta -= self.TWIST_PER_BASE
            z -= self.BASE_SPACING

        if doubleStrand:
            theta = 0.0
            z = 0.5 * self.BASE_SPACING * (len(sequence) - 1)
            for i in range(len(sequence)):
                # The 3'-to-5' direction is reversed for strand B.
                basefile, zoffset, thetaOffset = \
                          self.strandBinfo(basenameB[sequence[i]], i)
                def tfm(v, theta=theta+thetaOffset, z1=z+zoffset):
                    # Flip theta, flip z
                    # Cheesy hack: flip theta by reversing the sign of y,
                    # since theta = atan2(y,x)
                    return rotateTranslate(V(v[0], -v[1], -v[2]), theta, z1)
                self.insertmmp(mol, basefile, tfm)
                theta -= self.TWIST_PER_BASE
                z -= self.BASE_SPACING


expdir = os.path.join(os.curdir, 'experimental')

class A_Dna(Dna):
    """The geometry for A-DNA is very twisty and funky. I'd probably need to
    take a few days to research it. It's not a simple helix (like B) or an
    alternating helix (like Z).
    """
    TWIST_PER_BASE = 0  # WRONG
    BASE_SPACING = 0    # WRONG
    def strandAinfo(self, sequence, i):
        raise Exception("A-DNA is not yet implemented -- please try B- or Z-DNA");
    def strandBinfo(self, sequence, i):
        raise Exception("A-DNA is not yet implemented -- please try B- or Z-DNA");

class B_Dna(Dna):
    TWIST_PER_BASE = -36 * pi / 180   # radians
    BASE_SPACING = 3.391              # angstroms

    def strandAinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 0.0
        basefile = os.path.join(expdir, 'bdna-bases', '%s.mmp' % basename)
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 210 * (pi / 180)
        basefile = os.path.join(expdir, 'bdna-bases', '%s.mmp' % basename)
        return (basefile, zoffset, thetaOffset)

class Z_Dna(Dna):
    TWIST_PER_BASE = pi / 6     # in radians
    BASE_SPACING = 3.715        # in angstroms

    def strandAinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'outer'
            zoffset = 2.045
        else:
            suffix = 'inner'
            zoffset = 0.0
        thetaOffset = 0.0
        basefile = os.path.join(expdir, 'zdna-bases', '%s-%s.mmp' % (basename, suffix))
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'inner'
            zoffset = -0.055
        else:
            suffix = 'outer'
            zoffset = -2.1
        thetaOffset = 0.5 * pi
        basefile = os.path.join(expdir, 'zdna-bases', '%s-%s.mmp' % (basename, suffix))
        return (basefile, zoffset, thetaOffset)


#################################

cmd = greenmsg("Insert Dna: ")

class DnaGenerator(dna_dialog):

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        dna_dialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        self.win = win
        self.mol = None
        self.previousParams = None

    def build_dna(self):
        'Slot for the OK button'
        seq = str(self.base_textedit.text()).upper()
        dnatype = str(self.dna_type_combox.currentText())
        double = str(self.endings_combox.currentText())
        params = (seq, dnatype, double)
        if self.previousParams != params:
            self.remove_dna()
            self.previousParams = params
        if self.mol == None:
            if len(seq) > 0:
                if dnatype == 'A-DNA':
                    dna = A_Dna()
                elif dnatype == 'B-DNA':
                    dna = B_Dna()
                elif dnatype == 'Z-DNA':
                    dna = Z_Dna()
                doubleStrand = (double == 'Double')
                env.history.message(cmd + "Creating DNA. This may take a moment...")
                QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
                try:
                    self.mol = mol = molecule(self.win.assy, gensym("DNA-"))
                    dna.make(mol, seq, doubleStrand)
                    inferBonds(mol)
                    part = self.win.assy.part
                    part.ensure_toplevel_group()
                    part.topnode.addchild(mol)
                    self.win.win_update()
                    self.win.mt.mt_update()
                    env.history.message(cmd + "Done.")
                except Exception, e:
                    env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
                QApplication.restoreOverrideCursor() # Restore the cursor

    def remove_dna(self):
        if self.mol != None:
            part = self.win.assy.part
            part.ensure_toplevel_group()
            part.topnode.delmember(self.mol)
            self.win.win_update()
            self.win.mt.mt_update()
            self.mol = None

    def preview_btn_clicked(self):
        self.build_dna()

    def ok_btn_clicked(self):
        'Slot for the OK button'
        self.build_dna()
        self.mol = None
        QDialog.accept(self)

    def abort_btn_clicked(self):
        self.cancel_btn_clicked()

    def cancel_btn_clicked(self):
        'Slot for the OK button'
        self.remove_dna()
        QDialog.accept(self)

    def complement_btn_clicked(self):
        seq = ''
        for ch in str(self.base_textedit.text()).upper():
            if ch == 'G': seq += 'C'
            elif ch == 'C': seq += 'G'
            elif ch == 'A': seq += 'T'
            elif ch == 'T': seq += 'A'
            else:
                env.history.message(redmsg('Bogus DNA sequence: ' + ch))
                return
        self.base_textedit.setText(seq)

    def reverse_btn_clicked(self):
        seq = ''
        for ch in str(self.base_textedit.text()).upper():
            if ch not in 'CGAT':
                env.history.message(redmsg('Bogus DNA sequence: ' + ch))
                return
            else:
                seq = ch + seq
        self.base_textedit.setText(seq)

    def close(self, e=None):
        """When the user closes dialog by clicking the 'X' button on
        the dialog title bar, this method is called.
        """
        try:
            QDialog.accept(self)
            return True
        except:
            return False

    def open_sponsor_homepage(self):
        env.history.message(orangemsg('Sponsor homepage: Not implemented yet'))

    def enter_WhatsThisMode(self):
        env.history.message(orangemsg('WhatsThis: Not implemented yet'))
