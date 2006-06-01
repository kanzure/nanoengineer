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
from DnaGeneratorDialog import dna_dialog
from chem import Atom, gensym
from Utility import Group
from HistoryWidget import redmsg, orangemsg, greenmsg
from VQT import A, V, dot, vlen
from bonds import inferBonds, bond_atoms
from files_mmp import _readmmp
from GeneratorBaseClass import GeneratorBaseClass
from fusechunksMode import fusechunksBase

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
        baseList = [ ]
        def insertmmp(filename, tfm):
            grouplist  = _readmmp(assy, filename, isInsert=True)
            if not grouplist:
                raise Exception("Trouble with DNA base: " + filename)
            viewdata, mainpart, shelf = grouplist
            for member in mainpart.members:
                for atm in member.atoms.values():
                    atm._posn = tfm(atm._posn)
            del viewdata
            for member in mainpart.members:
                grp.addchild(member)
                baseList.append(member)
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

        # fuse the bases together into continuous strands
        fcb = fusechunksBase()
        for i in range(len(baseList) - 1):
            fcb.find_bondable_pairs([baseList[i]], [baseList[i+1]])
            fcb.make_bonds(assy)

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

###############################################################################

# GeneratorBaseClass must come BEFORE the dialog in the list of parents
class DnaGenerator(GeneratorBaseClass, dna_dialog):

    cmd = greenmsg("Insert Dna: ")
    sponsor_keyword = 'DNA'

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        dna_dialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        GeneratorBaseClass.__init__(self, win)

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        seq = self.get_sequence()
        dnatype = str(self.dna_type_combox.currentText())
        double = str(self.endings_combox.currentText())
        return (seq, dnatype, double)

    def build_struct(self, params):
        seq, dnatype, double = params
        assert len(seq) > 0, 'Please enter a valid sequence'
        if dnatype == 'A-DNA':
            dna = A_Dna()
        elif dnatype == 'B-DNA':
            dna = B_Dna()
        elif dnatype == 'Z-DNA':
            dna = Z_Dna()
        self.dna = dna  # needed for done msg
        doubleStrand = (double == 'Double')
        if len(seq) > 30:
            env.history.message(self.cmd + "Creating DNA. This may take a moment...")
        else:
            env.history.message(self.cmd + "Creating DNA.")
        grp = Group(gensym("DNA-"), self.win.assy,
                    self.win.assy.part.topnode)
        dna.make(self.win.assy, grp, seq, doubleStrand)
        return grp

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

    def done_msg(self):
        return "Done creating a strand of %s." % self.dna.geometry

    ###################################################
    # Any special controls for this kind of structure

    def complement_btn_clicked(self):
        seq = self.get_sequence(complement=True)
        self.base_textedit.setText(seq)

    def reverse_btn_clicked(self):
        seq = self.get_sequence(reverse=True)
        self.base_textedit.setText(seq)
