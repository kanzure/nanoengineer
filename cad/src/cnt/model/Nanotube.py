# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Nanotube.py -- Nanotube generator helper classes, based on empirical data.

@author: Mark Sims
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2008-03-09:
- Created.
"""

import foundation.env as env
import os

from math import sin, cos, pi
from math import atan2, asin
from Numeric import dot

from model.chem import Atom
from model.bonds import bond_atoms
from model.bond_constants import V_GRAPHITE, V_SINGLE
from model.bond_constants import atoms_are_bonded

from utilities.Log import orangemsg, greenmsg
from utilities.debug import Stopwatch
from utilities.debug import print_compact_traceback

from platform.PlatformDependent import find_plugin_dir
from files.mmp.files_mmp import readmmp
from geometry.VQT import Q, V, angleBetween, cross, vlen
from commands.Fuse.fusechunksMode import fusechunksBase
from command_support.GeneratorBaseClass import PluginBug
from utilities.prefs_constants import dnaDefaultSegmentColor_prefs_key
from model.chunk import Chunk
from model.elements import PeriodicTable

from model.bonds import CC_GRAPHITIC_BONDLENGTH, BN_GRAPHITIC_BONDLENGTH

ntTypes = ["Carbon", "Boron Nitride"]
ntEndings = ["None", "Hydrogen", "Nitrogen"] # "Capped" NIY.
ntBondLengths = [CC_GRAPHITIC_BONDLENGTH, BN_GRAPHITIC_BONDLENGTH]
sqrt3 = 3 ** 0.5

basepath_ok, basepath = find_plugin_dir("Nanotube")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/Nanotube directory is missing."))

class Nanotube:
    """
    Nanotube base class.
    """
    endPoint1 = None
    endPoint2 = None
    endings = "None" # "None", "Hydrogen" or "Nitrogen". "Capped" NIY.
    zdist  = 0.0 # Angstroms
    xydist = 0.0 # Angstroms
    twist  = 0   # Degrees/Angstrom
    bend   = 0   # Degrees
    numwalls = 1 # Single
    spacing  = 2.46 # Spacing b/w MWNT in Angstroms 
    
    def __init__(self, n = 5, m = 5, type = "Carbon", bond_length = None):
        """
        Constructor. Creates an instance of Nanotube, which contains the
        parameters and helper methods for a nanotube.
        """
        self.n = n
        self.m = m
        assert type in ntTypes
        self.type = type
        if bond_length:
            self.bond_length = bond_length
        else:
            self.bond_length = ntBondLengths[ntTypes.index(type)]
        self.update()
        
    def update(self, n = None, m = None, type = None, bond_length = None):
        """
        Updates all the chirality attrs based on new n, m, type and/or
        bond_length values.
        """
        if n:
            self.n = n
        else:
            n = self.n
        if m:
            self.m = m
        else:
            m = self.m
            
        if type:
            assert type in ntTypes
            self.type = type
        else:
            type = self.type
        
        if bond_length:
            self.bond_length = bond_length
        else:
            bond_length = self.bond_length
            
        self.setRise() #@ Not correctly implemented yet. See comments in method.
        
        self.maxlen = maxlen = 1.2 * bond_length
        self.maxlensq = maxlen**2
        
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
        denom = F * J - G * H
        self.R = (bond_length**2 * (F - H) / denom) ** .5
        self.B = (bond_length**2 * (J - G) / denom) ** .5
        self.A = self.R * AoverR
        
        if 0:
            print "--------------"
            print "angle =", angle
            print "A =", self.A
            print "B =", self.B
            print "R =", self.R

    def x1y1(self, n, m):
        c, s = self.__cos, self.__sin
        x = (n + .5*m) * sqrt3
        y = 1.5 * m
        x1 = x * c + y * s
        y1 = -x * s + y * c
        return (x1, y1)

    def mlimits(self, z3min, z3max, n):
        if z3max < z3min:
            z3min, z3max = z3max, z3min
        B, c, s = self.B, self.__cos, self.__sin
        P = sqrt3 * B * s
        Q = 1.5 * B * (c - s / sqrt3)
        m1, m2 = (z3min + P * n) / Q, (z3max + P * n) / Q
        return int(m1-1.5), int(m2+1.5)

    def xyz(self, n, m):
        x1, y1 = self.x1y1(n, m)
        x2, y2 = self.A * x1, self.B * y1
        R = self.R
        x3 = R * sin(x2/R)
        y3 = R * cos(x2/R)
        z3 = y2
        return (x3, y3, z3)
    
    def setChirality(self, n, m):
        """
        Set the n,m chiral integers of self.
        
        Two restrictions are maintained:
        - n >= 2
        - 0 <= m <= n
        
        @param n: chiral integer I{n}
        @type  n: int
        
        @param m: chiral integer I{m}
        @type  m: int
        """        
        if n < 2:
            n = 2
        if m != self.m:
            # m changed. If m became larger than n, make n bigger.
            if m > n:
                n = m
        elif n != self.n:
            # n changed. If n became smaller than m, make m smaller.
            if m > n:
                m = n
        self.n = n
        self.m = m
        return
    
    def getChirality(self):
        """
        Returns the n,m chirality of self.
        
        @return: n, m
        @rtype:  int, int
        """
        return (self.n, self.m)
    
    def getType(self):
        """
        Return the type of nanotube.
        
        @return: the type of nanotube.
        @rtype:  string
        """
        return self.type
    
    def getRadius(self):
        """
        Returns the radius of the nanotube.
        
        @return: The radius in Angstroms.
        @rtype: float
        """
        return self.R
    
    def getDiameter(self):
        """
        Returns the diameter of the nanotube.
        
        @return: The diameter in Angstroms.
        @rtype: float
        """
        return self.R * 2.0
    
    def setBondLength(self, bond_length):
        """
        Sets the I{bond length} between two neighboring atoms in self.
        
        @param bond_length: The bond length in Angstroms.
        @type  bond_length: float
        """
        self.bond_length
        self.update(bond_length = bond_length)
        return 
    
    def getBondLength(self):
        """
        Returns the bond length between atoms in the nanotube.
        
        @return: The bond length in Angstroms.
        @rtype: float
        """
        return self.bond_length
    
    def setEndings(self, endings):
        """
        Sets the type of I{endings} of the nanotube self.
        
        @param endings: Either "None", "Hydrogen", or "Nitrogen".
        @type  endings: string
        
        @note: "Capped" endings are not implemented yet.
        """
        assert endings in ntEndings
        self.endings = endings
        
    def getEndings(self):
        """
        Returns the type of I{endings} of the nanotube self.
        
        @return: Either "None", "Hydrogen", or "Nitrogen".
        @rtype : string
        
        @note: "Capped" endings are not implemented yet.
        """
        return self.endings
    
    def setEndPoints(self, endPt1, endPt2):
        self.endPoint1 = endPt1
        self.endPoint2 = endPt2
        
    def getEndPoints(self):
        return (self.endPoint1, self.endPoint2)
    
    def setRise(self): #@ See Python get/set attr builtin methods.
        """
        Sets the rise. This needs to be called anytime a parameter of self
        changes.
        """
        # Need formula to compute rise.
        # I'm sure this is doable, but I need to research it further to learn
        # how to compute rise from these params. --Mark 2008-03-12
        self.rise = 2.5 # default
        if self.m == 0:
            self.rise = 2.146
        if self.m == 5:
            self.rise = 2.457
            
    def getRise(self):
        """
        Returns the nanotube U{rise}.

        @return: The rise in Angstroms.
        @rtype: float
        """
        return self.rise
    
    def getLength(self, numberOfCells):
        """
        Returns the nanotube length (in Angstroms) given the number of cells.
        
        @param numberOfCells: The number of cells in the nanotube.
        @type  numberOfCells: int
        
        @return: The length of the nanotube in Angstroms.
        @rtype: float
        """
        assert numberOfCells >= 0
        return self.rise * (numberOfCells - 1)

    def populate(self, mol, length):
        """
        Populates a chunk (mol) with the atoms.
        """

        def add(element, x, y, z, atomtype='sp2'):
            atm = Atom(element, V(x, y, z), mol)
            atm.set_atomtype_but_dont_revise_singlets(atomtype)
            return atm

        evenAtomDict = { }
        oddAtomDict = { }
        bondDict = { }
        mfirst = [ ]
        mlast = [ ]

        for n in range(self.n):
            mmin, mmax = self.mlimits(-.5 * length, .5 * length, n)
            mfirst.append(mmin)
            mlast.append(mmax)
            for m in range(mmin, mmax+1):
                x, y, z = self.xyz(n, m)
                if self.type == "Carbon":
                    atm = add("C", x, y, z) # CNT
                else:
                    atm = add("B", x, y, z) # BNNT
                evenAtomDict[(n,m)] = atm
                bondDict[atm] = [(n,m)]
                x, y, z = self.xyz(n + 1.0 / 3, m + 1.0 / 3 )
                if self.type == "Carbon":
                    atm = add("C", x, y, z) # CNT
                else:
                    atm = add("N", x, y, z, 'sp3') # BNNT
                oddAtomDict[(n,m)] = atm
                bondDict[atm] = [(n + 1, m), (n, m + 1)]

        # m goes axially along the nanotube, n spirals around the tube
        # like a barber pole, with slope depending on chirality. If we
        # stopped making bonds now, there'd be a spiral strip of
        # missing bonds between the n=self.n-1 row and the n=0 row.
        # So we need to connect those. We don't know how the m values
        # will line up, so the first time, we need to just hunt for the
        # m offset. But then we can apply that constant m offset to the
        # remaining atoms along the strip.
        n = self.n - 1
        mmid = (mfirst[n] + mlast[n]) / 2
        atm = oddAtomDict[(n, mmid)]
        class FoundMOffset(Exception): pass
        try:
            for m2 in range(mfirst[0], mlast[0] + 1):
                atm2 = evenAtomDict[(0, m2)]
                diff = atm.posn() - atm2.posn()
                if dot(diff, diff) < self.maxlensq:
                    moffset = m2 - mmid
                    # Given the offset, zipping up the rows is easy.
                    for m in range(mfirst[n], mlast[n]+1):
                        atm = oddAtomDict[(n, m)]
                        bondDict[atm].append((0, m + moffset))
                    raise FoundMOffset()
            # If we get to this point, we never found m offset.
            # If this ever happens, it indicates a bug.
            raise Exception, "can't find m offset"
        except FoundMOffset:
            pass

        # Use the bond information to bond the atoms
        for (dict1, dict2) in [(evenAtomDict, oddAtomDict),
                               (oddAtomDict, evenAtomDict)]:
            for n, m in dict1.keys():
                atm = dict1[(n, m)]
                for n2, m2 in bondDict[atm]:
                    try:
                        atm2 = dict2[(n2, m2)]
                        if not atoms_are_bonded(atm, atm2):
                            if self.type == "Carbon":
                                bond_atoms(atm, atm2, V_GRAPHITE) # CNT
                            else:
                                bond_atoms(atm, atm2, V_SINGLE) # BNNT
                    except KeyError:
                        pass
                    
    def build(self, name, assy, position, mol = None, createPrinted = False):
        """
        Build a nanotube from the parameters in the Property Manger dialog.
        """
        endPoint1, endPoint2 = self.getEndPoints()
        cntAxis = endPoint2 - endPoint1
        length = vlen(cntAxis)
                
        # This can take a few seconds. Inform the user.
        # 100 is a guess. --Mark 051103.
        if not createPrinted:
            # If it's a multi-wall tube, only print the "Creating" message once.
            if length > 100.0:
                env.history.message("This may take a moment...")
        PROFILE = False
        if PROFILE:
            sw = Stopwatch()
            sw.start()
        xyz = self.xyz
        if mol == None:
            mol = Chunk(assy, name)
        atoms = mol.atoms
        mlimits = self.mlimits
        # populate the tube with some extra carbons on the ends
        # so that we can trim them later
        self.populate(mol, length + 4 * self.maxlen)

        # Apply twist and distortions. Bends probably would come
        # after this point because they change the direction for the
        # length. I'm worried about Z distortion because it will work
        # OK for stretching, but with compression it can fail. BTW,
        # "Z distortion" is a misnomer, we're stretching in the Y
        # direction.
        for atm in atoms.values():
            # twist
            x, y, z = atm.posn()
            twistRadians = self.twist * z
            c, s = cos(twistRadians), sin(twistRadians)
            x, y = x * c + y * s, -x * s + y * c
            atm.setposn(V(x, y, z))
        for atm in atoms.values():
            # z distortion
            x, y, z = atm.posn()
            z *= (self.zdist + length) / length
            atm.setposn(V(x, y, z))
        length += self.zdist
        for atm in atoms.values():
            # xy distortion
            x, y, z = atm.posn()
            radius = self.getRadius()
            x *= (radius + 0.5 * self.xydist) / radius
            y *= (radius - 0.5 * self.xydist) / radius
            atm.setposn(V(x, y, z))

        # Judgement call: because we're discarding carbons with funky
        # valences, we will necessarily get slightly more ragged edges
        # on nanotubes. This is a parameter we can fiddle with to
        # adjust the length. My thought is that users would prefer a
        # little extra length, because it's fairly easy to trim the
        # ends, but much harder to add new atoms on the end.
        LENGTH_TWEAK = self.getBondLength()

        # trim all the carbons that fall outside our desired length
        # by doing this, we are introducing new singlets
        for atm in atoms.values():
            x, y, z = atm.posn()
            if (z > .5 * (length + LENGTH_TWEAK) or
                z < -.5 * (length + LENGTH_TWEAK)):
                atm.kill()

        # Apply bend. Equations are anomalous for zero bend.
        if abs(self.bend) > pi / 360:
            R = length / self.bend
            for atm in atoms.values():
                x, y, z = atm.posn()
                theta = z / R
                x, z = R - (R - x) * cos(theta), (R - x) * sin(theta)
                atm.setposn(V(x, y, z))

        def trimCarbons():
            """
            Trim all the carbons that only have one carbon neighbor.
            """
            for i in range(2):
                for atm in atoms.values():
                    if not atm.is_singlet() and len(atm.realNeighbors()) == 1:
                        atm.kill()

        trimCarbons()
        
        # If we're not picky about endings, we don't need to trim carbons
        if self.endings == "Capped":
            # buckyball endcaps
            addEndcap(mol, length, self.getRadius())
        if self.endings == "Hydrogen":
            # hydrogen terminations
            for atm in atoms.values():
                atm.Hydrogenate()
        elif self.endings == "Nitrogen":
            # nitrogen terminations
            dstElem = PeriodicTable.getElement('N')
            atomtype = dstElem.find_atomtype('sp2')
            for atm in atoms.values():
                if len(atm.realNeighbors()) == 2:
                    atm.Transmute(dstElem, force=True, atomtype=atomtype)

        # Translate structure to desired position
        for atm in atoms.values():
            v = atm.posn()
            atm.setposn(v + position)

        if PROFILE:
            t = sw.now()
            env.history.message(greenmsg("%g seconds to build %d atoms" %
                                         (t, len(atoms.values()))))

        if self.numwalls > 1:
            n += int(self.spacing * 3 + 0.5)  # empirical tinkering                        
            self.build(name, assy, 
                       endPoint1, endPoint2, 
                       position, 
                       mol = mol, createPrinted = True)
            
        # Orient the nanotube.
        if self.numwalls == 1: 
            # This condition ensures that MWCTs get oriented only once.
            self._orient(mol, endPoint1, endPoint2)

        return mol
    pass # End build()

    def _postProcess(self, cntCellList):
        pass
    
    def _orient(self, cntChunk, pt1, pt2):
        """
        Orients the CNT I{cntChunk} based on two points. I{pt1} is
        the first endpoint (origin) of the nanotube. The vector I{pt1}, I{pt2}
        defines the direction and central axis of the nanotube.
        
        @param pt1: The starting endpoint (origin) of the nanotube.
        @type  pt1: L{V}
        
        @param pt2: The second point of a vector defining the direction
                    and central axis of the nanotube.
        @type  pt2: L{V}
        """
        
        a = V(0.0, 0.0, -1.0)
        # <a> is the unit vector pointing down the center axis of the default
        # DNA structure which is aligned along the Z axis.
        bLine = pt2 - pt1
        bLength = vlen(bLine)
        b = bLine/bLength
        # <b> is the unit vector parallel to the line (i.e. pt1, pt2).
        axis = cross(a, b)
        # <axis> is the axis of rotation.
        theta = angleBetween(a, b)
        # <theta> is the angle (in degress) to rotate about <axis>.
        scalar = bLength * 0.5
        rawOffset = b * scalar
        
        if 0: # Debugging code.
            print ""
            print "uVector  a = ", a
            print "uVector  b = ", b
            print "cross(a,b) =", axis
            print "theta      =", theta
            print "cntRise   =", self.getCntRise()
            print "# of cells =", self.getNumberOfCells()
            print "scalar     =", scalar
            print "rawOffset  =", rawOffset
        
        if theta == 0.0 or theta == 180.0:
            axis = V(0, 1, 0)
            # print "Now cross(a,b) =", axis
            
        rot =  (pi / 180.0) * theta  # Convert to radians
        qrot = Q(axis, rot) # Quat for rotation delta.
        
        # Move and rotate the nanotube into final orientation.
        cntChunk.move(qrot.rot(cntChunk.center) - cntChunk.center + rawOffset + pt1)
        cntChunk.rot(qrot) #@ NEEDED?
    
    pass
    
 
