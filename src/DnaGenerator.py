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
from qt import Qt, QApplication, QCursor, QDialog, QImage, QPixmap
from VQT import A, V, dot, vlen
from bonds import inferBonds
import re
import base64
from wiki_help import WikiHelpBrowser
from xml.dom.minidom import parseString  # or parse, for file
from platform import find_or_make_Nanorex_subdir

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


expdir = os.path.join(os.getcwd(), 'experimental')

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

# This is a file that the program would periodically download from our server.
# It would be cached for when the user is working offline. If I were feeling
# fancy, I would post this file on my own webserver

sponsorInfo = '''<?xml version="1.0" encoding="utf-8"?>
<sponsor>
    <!-- Base64 encoded PNG file -->
    <logo>iVBORw0KGgoAAAANSUhEUgAAAFAAAAAeCAMAAACMnWmDAAAAwFBMVEXgGCD3xcfjMR72zhTrcxrv
    horsbnP1tbf//8zkOT///9PztBbxlJb63t/oWBzujRj56BL////kNDvufYLoUljhHibzpqj51dbm
    TBztgBn32xPxpxb87ebugoblPx3vi4/hJB/wmhfpXGL//+Tsc3f0wRXwj5P0rK785t7pZRv1t7rx
    mp3mQ0r+9fLtdHjiJi774uP4ycrmSiH98PDzqKv//+D1sLP75OXqYGX2u73ten4AAAAAAAAAAAAA
    AAAAAAA5wl0TAAAACXRSTlP//////////wBTT3gSAAAAAWJLR0Q/PmMwdQAAAAlwSFlzAAAASAAA
    AEgARslrPgAAAfFJREFUSMel1g1vmzAQBuBzoKwNWzgTNrBpAllLMjAbTNCt3f//YTPfZtFaTE9K
    YkfiyWsfRoHbq9p+O+//X4dpeL7fXl8N1189CBgqNtlGmZgwr/ppGXgYicQw+LGfHLlhJPEMvHnQ
    BG07jg1jwJP29R7QRLneFLuFMgxkSjTfAcb81Hx0EWPehjvxeD3IsN0+B3fQBGXNZDeLqAfGvNu9
    HTZBw06H/ss1oIlOByPv39o1t3lXgUbThWGQot1NxoE2eEQcbh65faduCwE2iJt1oDNGYXLEx5Vy
    pS1aYDJkkpuJMtdwYEIMR3CvAcY4ZgoQnXH9Mi8fwYMGuJv2StoGjmduN4XVAh0lCMoaeyubZa4B
    E+X2MCTIFD5cAcYqYc9APmXXAANlYZAyxo7qbAXIEIOcPAsBrldYhGTFxSd3uetC7gHxipyKH5Gn
    AYaylxbNKHUrEUUR+PW9yH5RUkGURcSrhO/VZK8Byj6AqCkpH0mRN+AHWhCfAs39WoIUKs8VpQYo
    2wDk2d9nFimtqPSzO/qpOkjQLV8kKH6+eJaol4MBqg+VQDYFPv/52j8eGEu1m5LOQIbTyQP1x5aD
    7HXQ0AZPynHol6yCCNZjpAXa6tH4p1ow+k3yxeDTR1hYX5b9FdlWl+iNOt80dfl+ffHtX3qHXE7Q
    ENyTAAAAAElFTkSuQmCC</logo>
    <text>[http://www.mcdonalds.com Purveyors] of fine dining experiences
    throughout the world</text>
</sponsor>
'''

sponsorInfo = ""

##################################

cmd = greenmsg("Insert Dna: ")

class DnaGenerator(dna_dialog):

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        dna_dialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        self.win = win
        self.mol = None
        self.previousParams = None

        # Sponsor stuff
        # (1) download the sponsor information
        # (2) store the text and the logo in files somewhere in ~/Nanorex
        # (3) use the logo to replace the existing logo
        # (4) be ready, when the user clicks the sponsor button, to pop up the text
        magicUrl = 'http://willware.net/sponsorfoo.xml'
        import urllib
        try:
            f = urllib.urlopen(magicUrl)
            r = f.read()
            info = parseString(r)
        except:
            info = sponsorInfo

        tmpdir = find_or_make_Nanorex_subdir('Sponsors')
        self.sponsorLogo = sponsorLogo = os.path.join(tmpdir, 'logo.png')
        self.sponsorText = sponsorText = os.path.join(tmpdir, 'sponsor.txt')
        open(sponsorLogo, 'w').write(base64.decodestring(self.getXmlText(info, 'logo')))
        open(sponsorText, 'w').write(self.getXmlText(info, 'text'))

        qimg = QImage(sponsorLogo)
        qpxmp = QPixmap(qimg)
        self.sponsor_btn.setPixmap(qpxmp)

    def build_dna(self):
        'Slot for the OK button'
        seq = self.get_sequence()
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

    def complement_btn_clicked(self):
        seq = self.get_sequence(complement=True)
        self.base_textedit.setText(seq)

    def reverse_btn_clicked(self):
        seq = self.get_sequence(reverse=True)
        self.base_textedit.setText(seq)

    def close(self, e=None):
        """When the user closes dialog by clicking the 'X' button on
        the dialog title bar, this method is called.
        """
        try:
            self.cancel_btn_clicked()
            return True
        except:
            return False

    def getXmlText(self, doc, tag):
        parent = doc.getElementsByTagName(tag)[0]
        start, middle, finish = re.compile('\['), re.compile(' '), re.compile('\]')
        rc = ""
        for node in parent.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        while True:
            m = start.search(rc)
            if m == None:
                break
            s, e = m.start(), m.end()
            m = middle.search(rc[e:])
            s2, e2 = m.start() + e, m.end() + e
            m = finish.search(rc[e2:])
            s3, e3 = m.start() + e2, m.end() + e2
            mid = "<a href=\"%s\">%s</a>" % (rc[e:s2], rc[e2:s3])
            rc = rc[:s] + mid + rc[e3:]
        return rc

    def open_sponsor_homepage(self):
        w = WikiHelpBrowser(open(self.sponsorText).read())
        w.show()

    def enter_WhatsThisMode(self):
        env.history.message(orangemsg('WhatsThis: Not implemented yet'))
