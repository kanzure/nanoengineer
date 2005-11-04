# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
NanotubeGenerator.py

$Id$

See http://www.nanoengineer-1.net/mediawiki/index.php?title=Nanotube_generator_dialog
for notes about what's going on here.
"""

__author__ = "Will"

from NanotubeGeneratorDialog import NanotubeGeneratorDialog
from math import atan2, sin, cos, pi
import assembly, chem, bonds, Utility
from chem import molecule, Atom
import env
from HistoryWidget import redmsg, greenmsg
from qt import Qt, QApplication, QCursor, QDialog, QDoubleValidator, QValidator

sqrt3 = 3 ** 0.5

class Chirality:

    # Nanotube bond length according to Dresselhaus, M. S.,
    # Dresselhaus, G., Eklund, P. C. "Science of Fullerenes and Carbon
    # Nanotubes" Academic Press: San Diego, CA, 1995; pp. 760.
    BONDLENGTH = 1.421  # angstroms

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

    def populate(self, mol, length):
        def add(element, x, y, z, mol=mol):
            atm = Atom(element, chem.V(x, y, z), mol)
            atm.set_atomtype("sp2")
        for n in range(self.n):
            mmin, mmax = self.mlimits(-.5 * length, .5 * length, n)
            for m in range(mmin-1, mmax+1):
                x, y, z = self.xyz(n, m)
                if -.5 * length <= y <= .5 * length:
                    add("C", x, y, z)
                x, y, z = self.xyz(n+1./3, m+1./3)
                if -.5 * length <= y <= .5 * length:
                    add("C", x, y, z)

cmd = greenmsg("Insert Nanotube: ")

class NanotubeGenerator(NanotubeGeneratorDialog):

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        NanotubeGeneratorDialog.__init__(self)
        self.win = win
        self.mol = molecule(win.assy, chem.gensym("Nanotube."))
        
        # Validator for the length linedit widget.
        self.validator = QDoubleValidator(self)
        self.validator.setRange(0.0, 1000.0, 2) # Range of nanotube length (0-100, 2 decimal places)
        self.length_linedit.setValidator(self.validator)
        self.cursor_pos = 0
        
        # Default nanotube parameters.
        self.n = 5
        self.m = 5
        self.length = 5.0 # Angstoms
        self.lenstr = '%1.2f' % self.length # Also used for validation
        
        self.setup()

    # These four methods are needed to implement the GUI semantics.
    
    def setup(self):
        self.n_spinbox.setValue(self.n)
        self.m_spinbox.setValue(self.m)
        self.length_linedit.setText(self.lenstr)

    def accept(self):
        'Slot for the OK button'
        
        # Get length from length_linedit and make sure it is not zero.
        # length_linedit's validator makes sure this has a valid number (float).  
        # The only exception is when there is no text.  Mark 051103.
        import string
        if self.length_linedit.text():
            self.length = string.atof(str(self.length_linedit.text()))
        else:
            self.length = 0.0
            env.history.message(cmd + redmsg("Please specify length."))
            return
        
        # This can take a few seconds.  Inform the user.  100 is a guess on my part.  Mark 051103.
        if self.length > 100.0:
            env.history.message(cmd + "Creating nanotube. This may take a moment...")
            QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
            self.generateTube()
            env.history.message(cmd + "Done.")
            QApplication.restoreOverrideCursor() # Restore the cursor
            QDialog.accept(self)
        
        else: # Shouldn't take long.
            QDialog.accept(self)
            env.history.message(cmd + "Nanotube created.")
            self.generateTube()

    def generateTube(self):
        try:
            self.n
            self.m
            self.length
        except AttributeError:
            env.history.message(cmd + redmsg("Please specify chirality (n, m) and length."))
            return
        self.chirality = Chirality(self.n, self.m)
        self.buildChunk()

    def setN(self, n):
        'Slot for chiral (N) spinbox'
        self.n = n

    def setM(self, m):
        'Slot for chiral (M) spinbox'
        self.m = m

    def length_fixup(self):
        '''Slot for the Length linedit widget.
        This gets called each time a user types anything into the widget.
        '''
        from widgets import double_fixup
        self.lenstr = double_fixup(self.validator, self.length_linedit.text(), self.lenstr)
        self.length_linedit.setText(self.lenstr)

    def buildChunk(self):
        from Numeric import dot
        length = self.length
        xyz = self.chirality.xyz
        atoms = self.mol.atoms
        mlimits = self.chirality.mlimits
        maxLen = 1.2 * Chirality.BONDLENGTH
        maxLenSq = maxLen ** 2
        # populate the tube with some extra carbons on the ends
        # so that we can trim them later
        self.chirality.populate(self.mol, length + 4 * maxLen)

        # kill all the singlets
        for atm in atoms.values():
            if atm.is_singlet():
                atm.kill()

        # faster bond-finding algorithm, wware 051104
        # A 100-angstrom-long (60,7) nanotube is currently taking 18
        # seconds from when I hit "Ok" to when it appears on the screen.
        # It has 6052 atoms.
        # A 300-A-long (80,0) nanotube takes 1 minute, 8 seconds, and
        # has 22560 atoms, so this is a linear-time algorithm, taking
        # about 3 milliseconds per atom.

        # By partitioning the atoms into 3D voxels, we can search just
        # the atoms in the 3x3x3 nearest voxels to find out who bonds
        # to an atom. First, sort the atoms into voxels.
        voxels = { }
        for atm in atoms.values():
            x, y, z = map(float, atm.posn())
            idx = (int(x / maxLen),
                   int(y / maxLen),
                   int(z / maxLen))
            try: voxels[idx].append(atm)
            except KeyError: voxels[idx] = [ atm ]

        # Do the bonding
        for atm in atoms.values():
            x, y, z = map(float, atm.posn())
            # get the voxel index
            x1 = int(x / maxLen)
            y1 = int(y / maxLen)
            z1 = int(z / maxLen)
            # get a bounding box around the atom, use it to create
            # a screening function for our short list of neighbors
            xmin, xmax = x - maxLen, x + maxLen
            ymin, ymax = y - maxLen, y + maxLen
            zmin, zmax = z - maxLen, z + maxLen
            def closeEnough(atm2):
                if atm2 == atm or bonds.bonded(atm, atm2): return False
                x, y, z = map(float, atm2.posn())
                if x < xmin or x > xmax: return False
                if y < ymin or y > ymax: return False
                if z < zmin or z > zmax: return False
                diff = atm.posn() - atm2.posn()
                return dot(diff, diff) < maxLenSq

            # Compile the short list of neighbors
            lst = [ ]
            for x2 in range(x1-1, x1+2):
                for y2 in range(y1-1, y1+2):
                    for z2 in range(z1-1, z1+2):
                        idx = (x2, y2, z2)
                        try: lst += voxels[idx]
                        except KeyError: pass

            # Step through the short list and bond as needed
            for atm2 in filter(closeEnough, lst):
                bonds.bond_atoms(atm, atm2, bonds.V_GRAPHITE)

        # trim all the carbons that fall outside our desired length
        # by doing this, we are introducing new singlets
        for atm in atoms.values():
            y = atm.posn()[1]
            if y > .5 * (length + maxLen) or y < -.5 * (length + maxLen):
                atm.kill()

        # trim all the carbons that only have one carbon neighbor
        for atm in atoms.values():
            if not atm.is_singlet() and len(atm.realNeighbors()) == 1:
                atm.kill()

        part = self.win.assy.part
        part.ensure_toplevel_group()
        part.topnode.addchild(self.mol)
        self.win.mt.mt_update()
