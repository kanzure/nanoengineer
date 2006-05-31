# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
DnaGenerator.py

$Id$

http://en.wikipedia.org/wiki/DNA
http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif
"""

__author__ = "Will"

import sys
import os
import env
import re
from math import atan2, sin, cos, pi
from qt import Qt, QApplication, QCursor, QDialog, QImage, QPixmap
from DnaGeneratorDialog import dna_dialog
from chem import Atom, gensym
from Utility import Group
from HistoryWidget import redmsg, orangemsg, greenmsg
from VQT import A, V, dot, vlen
from bonds import inferBonds, bond_atoms
from files_mmp import _readmmp
from Sponsors import findSponsor

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
basepath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'experimental')

class Dna:

    def make(self, assy, grp, sequence, doubleStrand,
             basenameA={'C': 'cytosine',
                        'G': 'guanine',
                        'A': 'adenine',
                        'T': 'thymine'},
             basenameB={'G': 'cytosine',
                        'C': 'guanine',
                        'T': 'adenine',
                        'A': 'thymine'}):
        def insertmmp(filename, tfm):
            grouplist  = _readmmp(assy, filename, isInsert = True)
            if not grouplist:
                raise Exception("Trouble with DNA base: " + filename)
            viewdata, mainpart, shelf = grouplist
            for member in mainpart.members:
                for atm in member.atoms.values():
                    atm._posn = tfm(atm._posn)
            del viewdata
            for member in mainpart.members:
                grp.addchild(member)
            shelf.kill()

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
            insertmmp(basefile, tfm)
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
                insertmmp(basefile, tfm)
                theta -= self.TWIST_PER_BASE
                z -= self.BASE_SPACING

        # find coincident singlets, remove them, connect their owner atoms
        singlets = { }
        removable = { }
        def dictOnly(n, x):
            import types
            return type(x) == types.DictType
        for m in grp.members:
            for atm in m.atoms.values():
                if atm.is_singlet():
                    singlets[atm.key] = atm
        from bonds import neighborhoodGenerator
        sgn = neighborhoodGenerator(singlets.values(), 2.0)
        for sing1 in singlets.values():
            key1 = sing1.key
            pos1 = sing1.posn()
            for sing2 in sgn(pos1):
                dist = vlen(pos1 - sing2.posn())
                key2 = sing2.key
                if key1 != key2 and dist < 2.0:
                    removable[key1] = sing1
                    removable[key2] = sing2
                    b1, b2 = sing1.bonds[0], sing2.bonds[0]
                    owner1 = b1.other(sing1)
                    owner2 = b2.other(sing2)
                    bond_atoms(owner1, owner2)
        for atm in removable.values():
            atm.kill()

class A_Dna(Dna):
    """The geometry for A-DNA is very twisty and funky. I'd probably need to
    take a few days to research it. It's not a simple helix (like B) or an
    alternating helix (like Z).
    """
    geometry = "A-DNA"
    TWIST_PER_BASE = 0  # WRONG
    BASE_SPACING = 0    # WRONG
    def strandAinfo(self, sequence, i):
        raise Exception("A-DNA is not yet implemented -- please try B- or Z-DNA");
    def strandBinfo(self, sequence, i):
        raise Exception("A-DNA is not yet implemented -- please try B- or Z-DNA");

class B_Dna(Dna):
    geometry = "B-DNA"
    TWIST_PER_BASE = -36 * pi / 180   # radians
    BASE_SPACING = 3.391              # angstroms

    def strandAinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 0.0
        basefile = os.path.join(basepath, 'bdna-bases', '%s.mmp' % basename)
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 210 * (pi / 180)
        basefile = os.path.join(basepath, 'bdna-bases', '%s.mmp' % basename)
        return (basefile, zoffset, thetaOffset)

class Z_Dna(Dna):
    geometry = "Z-DNA"
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
        basefile = os.path.join(basepath, 'zdna-bases', '%s-%s.mmp' % (basename, suffix))
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'inner'
            zoffset = -0.055
        else:
            suffix = 'outer'
            zoffset = -2.1
        thetaOffset = 0.5 * pi
        basefile = os.path.join(basepath, 'zdna-bases', '%s-%s.mmp' % (basename, suffix))
        return (basefile, zoffset, thetaOffset)

##################################

cmd = greenmsg("Insert Dna: ")

# There is some logic associated with Preview/OK/Abort that's complicated enough
# to put it in one place, so that individual generators can focus on what they
# need to do.

class GeneratorBaseClass:

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        self.win = win
        self.group = None
        self.previousParams = None

    def build_struct(self):
        raise Exception("Not implemented in the base class")

    def remove_struct(self):
        if self.group != None:
            part = self.win.assy.part
            part.ensure_toplevel_group()
            part.topnode.delmember(self.group)
            self.win.win_update()
            self.win.mt.mt_update()
            self.group = None

    def preview_btn_clicked(self):
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        try:
            self.build_struct()
        except Exception, e:
            env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_struct()
        QApplication.restoreOverrideCursor() # Restore the cursor
        self.win.win_update()
        self.win.mt.mt_update()

    def done_history_msg(self):
        raise Exception("Not implemented in the base class")

    def ok_btn_clicked(self):
        'Slot for the OK button'
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        try:
            self.build_struct()
            self.done_history_msg()
            self.group = None
        except Exception, e:
            env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_struct()
        QApplication.restoreOverrideCursor() # Restore the cursor
        self.win.win_update()
        self.win.mt.mt_update()
        QDialog.accept(self)

    def done_btn_clicked(self):
        self.ok_btn_clicked()

    def abort_btn_clicked(self):
        self.cancel_btn_clicked()

    def cancel_btn_clicked(self):
        'Slot for the OK button'
        self.remove_struct()
        QDialog.accept(self)

    def close(self, e=None):
        """When the user closes dialog by clicking the 'X' button on
        the dialog title bar, this method is called.
        """
        try:
            self.cancel_btn_clicked()
            return True
        except:
            return False

    def open_sponsor_homepage(self):
        self.sponsor.wikiHelp()

    def enter_WhatsThisMode(self):
        env.history.message(orangemsg('WhatsThis: Not implemented yet'))


# GeneratorBaseClass must come BEFORE the dialog in the list of parents
class DnaGenerator(GeneratorBaseClass, dna_dialog):

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        dna_dialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        GeneratorBaseClass.__init__(self, win)
        self.sponsor = sponsor = findSponsor('DNA')
        sponsor.configureSponsorButton(self.sponsor_btn)

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def build_struct(self):
        seq = self.get_sequence()
        dnatype = str(self.dna_type_combox.currentText())
        double = str(self.endings_combox.currentText())
        params = (seq, dnatype, double)
        if self.previousParams != params:
            self.remove_struct()
            self.previousParams = params
        if self.group == None:
            if len(seq) > 0:
                if dnatype == 'A-DNA':
                    dna = A_Dna()
                elif dnatype == 'B-DNA':
                    dna = B_Dna()
                elif dnatype == 'Z-DNA':
                    dna = Z_Dna()
                self.dna = dna  # needed for done msg
                doubleStrand = (double == 'Double')
                if len(seq) > 30:
                    env.history.message(cmd + "Creating DNA. This may take a moment...")
                else:
                    env.history.message(cmd + "Creating DNA.")
                part = self.win.assy.part
                part.ensure_toplevel_group()
                self.group = grp = Group(gensym("DNA-"), self.win.assy, part.topnode)
                dna.make(self.win.assy, grp, seq, doubleStrand)

    def get_sequence(self, reverse=False, complement=False,
                     cdict={'C':'G', 'G':'C', 'A':'T', 'T':'A'}):
        seq = ''
        for ch in str(self.base_textedit.text()).upper():
            if ch in 'CGAT':
                if complement:
                    ch = cdict[ch]
                seq += ch
            elif ch in '\ \t\r\n':
                pass
            else:
                env.history.message(redmsg('Bogus DNA base: ' + ch +
                                           ' (should be C, G, A, or T)'))
                return ''
        if reverse:
            seq = list(seq)
            seq.reverse()
            seq = ''.join(seq)
        return seq

    ###################################################
    # The done message

    def done_history_msg(self):
        env.history.message(cmd + "Done creating a strand of %s." % self.dna.geometry)

    ###################################################
    # Any special controls for this kind of structure

    def complement_btn_clicked(self):
        seq = self.get_sequence(complement=True)
        self.base_textedit.setText(seq)

    def reverse_btn_clicked(self):
        seq = self.get_sequence(reverse=True)
        self.base_textedit.setText(seq)
