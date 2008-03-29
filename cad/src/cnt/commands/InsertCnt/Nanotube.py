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

from math    import sin, cos, pi

from utilities.debug import print_compact_traceback

from platform.PlatformDependent import find_plugin_dir
from files.mmp.files_mmp import readmmp
from geometry.VQT import Q, V, angleBetween, cross, vlen
from commands.Fuse.fusechunksMode import fusechunksBase
from utilities.Log      import orangemsg
from command_support.GeneratorBaseClass import PluginBug
from utilities.prefs_constants import dnaDefaultSegmentColor_prefs_key
from cnt.commands.InsertCnt.Chirality import Chirality
from model.chunk import Chunk
from model.elements import PeriodicTable

basepath_ok, basepath = find_plugin_dir("Nanotube")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/Nanotube directory is missing."))

class Nanotube:
    """
    Nanotube base class. It is inherited by C_Nanotube and BN_Nanotube 
    subclasses.
    
    @ivar cntRise: The rise (spacing) between unit cells along the central
                    (Z) axis.
    @type cntRise: float
    
    @ivar type: The type of nanotube; one of:
                    - "Carbon Nanotube" 
                    - "Boron-Nitride Nanotube"
    @type type: str
    
    @ivar model: The model representation, where:
                    - "PAM1" = PAM-1 reduced model.
    @type model: str
    
    @ivar numberOfCells: The number of cells in the nanotube.
    @type numberOfCells: int
    """
    
    def build(self, name, assy, params, position, 
              mol = None, 
              createPrinted = False):
        """
        Build a nanotube from the parameters in the Property Manger dialog.
        """
        
        ntChirality, ntType, n, m, bond_length, endings, \
               zdist, xydist, twist, bend, \
               numwalls, spacing, \
               endPoint1, endPoint2 = params
        
        cntAxis = endPoint2 - endPoint1
        length = vlen(cntAxis)
                
        # This can take a few seconds. Inform the user.
        # 100 is a guess on my part. Mark 051103.
        if not createPrinted:
            # If it's a multi-wall tube, only print the "Creating" message once.
            if length > 100.0:
                env.history.message("This may take a moment...")
        self.chirality = Chirality(n, m, 
                                   type = ntType, 
                                   bond_length = bond_length)
        PROFILE = False
        if PROFILE:
            sw = Stopwatch()
            sw.start()
        xyz = self.chirality.xyz
        if mol == None:
            mol = Chunk(assy, name)
        atoms = mol.atoms
        mlimits = self.chirality.mlimits
        # populate the tube with some extra carbons on the ends
        # so that we can trim them later
        self.chirality.populate(mol, length + 4 * self.chirality.maxlen, ntType)

        # Apply twist and distortions. Bends probably would come
        # after this point because they change the direction for the
        # length. I'm worried about Z distortion because it will work
        # OK for stretching, but with compression it can fail. BTW,
        # "Z distortion" is a misnomer, we're stretching in the Y
        # direction.
        for atm in atoms.values():
            # twist
            x, y, z = atm.posn()
            twistRadians = twist * z
            c, s = cos(twistRadians), sin(twistRadians)
            x, y = x * c + y * s, -x * s + y * c
            atm.setposn(V(x, y, z))
        for atm in atoms.values():
            # z distortion
            x, y, z = atm.posn()
            z *= (zdist + length) / length
            atm.setposn(V(x, y, z))
        length += zdist
        for atm in atoms.values():
            # xy distortion
            x, y, z = atm.posn()
            radius = self.chirality.R
            x *= (radius + 0.5 * xydist) / radius
            y *= (radius - 0.5 * xydist) / radius
            atm.setposn(V(x, y, z))

        # Judgement call: because we're discarding carbons with funky
        # valences, we will necessarily get slightly more ragged edges
        # on nanotubes. This is a parameter we can fiddle with to
        # adjust the length. My thought is that users would prefer a
        # little extra length, because it's fairly easy to trim the
        # ends, but much harder to add new atoms on the end.
        LENGTH_TWEAK = bond_length

        # trim all the carbons that fall outside our desired length
        # by doing this, we are introducing new singlets
        for atm in atoms.values():
            x, y, z = atm.posn()
            if (z > .5 * (length + LENGTH_TWEAK) or
                z < -.5 * (length + LENGTH_TWEAK)):
                atm.kill()

        # Apply bend. Equations are anomalous for zero bend.
        if abs(bend) > pi / 360:
            R = length / bend
            for atm in atoms.values():
                x, y, z = atm.posn()
                theta = z / R
                x, z = R - (R - x) * cos(theta), (R - x) * sin(theta)
                atm.setposn(V(x, y, z))

        def trimCarbons():
            # trim all the carbons that only have one carbon neighbor
            for i in range(2):
                for atm in atoms.values():
                    if not atm.is_singlet() and len(atm.realNeighbors()) == 1:
                        atm.kill()

        trimCarbons()
        # if we're not picky about endings, we don't need to trim carbons
        if endings == "Capped":
            # buckyball endcaps
            addEndcap(mol, length, self.chirality.R)
        if endings == "Hydrogen":
            # hydrogen terminations
            for atm in atoms.values():
                atm.Hydrogenate()
        elif endings == "Nitrogen":
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

        if numwalls > 1:
            n += int(spacing * 3 + 0.5)  # empirical tinkering            
            params = (ntType, n, m, bond_length, endings, \
                      zdist, xydist, twist, bend, \
                      numwalls - 1, spacing, \
                      endPoint1, endPoint2)
            
            self.build(name, assy, params, position, mol = mol, createPrinted = True)
            
        # Orient the nanotube.
        if numwalls == 1: 
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

class Cnt(Nanotube):
    """
    Provides a carbon nanotube.
    """
    type = "Carbon"
    
class Bnnt(Nanotube):
    """
    Boron Nitride nanotube (BNNT).
    """
    type = "Boron Nitride"
    
 
