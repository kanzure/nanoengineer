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
from MWsemantics import windowList  # Rearchitecture: fix this mess
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

    class ConstError(TypeError): pass
    def __setattr__(self,name,value):
        # Don't touch my precious constants
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't reassign " + name
        self.__dict__[name] = value

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

    def populate(self, mol, length, posns):
        def add(element, x, y, z, mol=mol):
            atm = Atom(element, chem.V(x, y, z), mol)
            atm.set_atomtype("sp2")
            posns.append((x, y, z))
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

    def __init__(self):
        NanotubeGeneratorDialog.__init__(self)
        self.win = win = windowList[0]  # Rearchitecture: fix this mess
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
        length = self.length
        maxLen = 1.2 * Chirality.BONDLENGTH
        maxLenSq = maxLen ** 2
        positions = [ ]
        # populate the tube with some extra carbons on the ends
        # so that we can trim them later
        self.chirality.populate(self.mol, length + 3 * maxLen, positions)

        # kill all the singlets
        for a in self.mol.atoms.keys():
            if self.mol.atoms[a].is_singlet():
                self.mol.atoms[a].kill()

        # make a list of positions close enough to be bonded
        bondList = [ ]
        N = len(positions)
        atoms = self.mol.atoms
        akeys = atoms.keys()
        for i in range(N):
            x1, y1, z1 = positions[i]
            for j in range(i+1, N):
                x2, y2, z2 = positions[j]
                # try to keep this test as quick as possible by
                # disqualifying candidates as early as possible
                dx2 = (x1 - x2) ** 2
                if dx2 < maxLenSq:
                    dy2 = (y1 - y2) ** 2
                    if dy2 < maxLenSq:
                        dz2 = (z1 - z2) ** 2
                        if dz2 < maxLenSq:
                            if (dx2 + dy2 + dz2) < maxLenSq:
                                a = atoms[akeys[i]]
                                b = atoms[akeys[j]]
                                bonds.bond_atoms(a, b, bonds.V_GRAPHITE)

        # trim all the carbons that fall outside our desired length
        for a in self.mol.atoms.keys():
            y = self.mol.atoms[a].posn()[1]
            if y > .5 * length or y < -.5 * length:
                self.mol.atoms[a].kill()
        part = self.win.assy.part
        part.ensure_toplevel_group()
        part.topnode.addchild(self.mol)
        self.win.mt.mt_update()


"""
Damian's notes on cleaning up passivation:

Where there's one C, make it C-H, which will make its carbon atom
type (for now) aromatic. The rules for aromaticity (Huckel's 4n+2,
that is) break down in large pi-systems, so we don't need to worry
about counting rings to make the pi-electrons work out right.

Where there are two carbons (where you've got -O-O- now), make each
of those C-H, which will also make their atom types aromatic (those
same C-C units are the dimers the DC10c tip is designed to build
with).  There'll be no complaints from the nanotube community who,
like I said, don't typically think about any other atom types but C
and H (and H only when necessary).

-----------------------------
Bruce's notes:

All the C atoms should be sp2, I think, whether or not connected to H.

You also have to independently set the bond types of the bonds.
You can use set_v6 and the named constants like V_GRAPHITIC.
Or there's a method whose name I forget which would take the string
"graphitic" as an arg. BTW the constants might be called "graphite"
rather than "graphitic". Maybe we should rename them.

Most bonds in the nanotube should be set to "graphitic".

For the bonds at the ends, it's up to you whether/how to make them
1, 2, or g to fix valence errors.

There is no guarantee this is possible -- if you terminate with H,
it won't always be possible. The best compromise is bond type 1
for C-H, g for C-C, and ignore the valence errors.

But for using the nanotube for further construction it's more useful
to terminate with open bonds (element X or 0) than with H.
Then the bond types can all be g -- no valence errors.
(And all C atoms should be sp2.)

Maybe a checkbox for this is called for.
"""