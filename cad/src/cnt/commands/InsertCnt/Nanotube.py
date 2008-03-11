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

from debug import print_compact_traceback

from PlatformDependent  import find_plugin_dir
from files.mmp.files_mmp import readmmp
from geometry.VQT import Q, V, angleBetween, cross, vlen
from commands.Fuse.fusechunksMode import fusechunksBase
from utilities.Log      import orangemsg
from command_support.GeneratorBaseClass import PluginBug
from prefs_constants import dnaDefaultSegmentColor_prefs_key

basepath_ok, basepath = find_plugin_dir("Nanotube")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/Nanotube directory is missing."))

RIGHT_HANDED = -1
LEFT_HANDED  =  1

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
    
    def make(self, 
             group, 
             numberOfCells, 
             cellsPerTurn, 
             cntRise,
             endPoint1,
             endPoint2,
             position = V(0, 0, 0)):
        """
        Makes a nanotube with the I{numberOfCells}. 
        The nanotube is oriented with its central axis coincident to the
        line (endPoint1, endPoint1), with its origin at endPoint1.
        
        @param assy: The assembly (part).
        @type  assy: L{assembly}
        
        @param group: The group node object containing the nanotbue. The caller
                      is responsible for creating an empty group and passing
                      it here. When finished, this group will contain the 
                      nanotube.
        @type  group: L{Group}
        
        @param numberOfCells: The number of repeating cells in the nanotube.
        @type  numberOfCells: int
        
        @param cellsPerTurn: The number of unit cells per helical turn.
        @type  cellsPerTurn: float
        
        @param cntRise: The rise; the distance between adjacent unit cells.
        @type  cntRise: float
        
        @param endPoint1: The origin of the nanotube.
        @param endPoint1: L{V}
        
        @param endPoint2: The second point that defines central axis of 
                          the nanotube.
        @param endPoint2: L{V}
        
        @param position: The position in 3d model space at which to create
                         the nanotube. This should always be 0, 0, 0.
        @type position:  position
        """
        
        self.assy               =  group.assy
        assy                    =  group.assy
        cntCellList                =  []
        
        self.setNumberOfUnitCells(numberOfCells)
        self.setCntRise(cntRise)
        #See a note in CntSegment_EditCommand._createStructure(). Should 
        #the parentGroup object <group> be assigned properties such as
        #cntRise, cellsPerTurn in this method itself? to be decided 
        #once cnt data model is fully functional (and when this method is 
        #revised) -- Ninad 2008-03-05
        self.setCellsPerTurn(cellsPerTurn)
        
        def insertBaseFromMmp(filename, subgroup, tfm, position = position):
            """
            Insert the atoms for a cnt unit cell from an MMP file into
            a single chunk.
             - If atomistic, the atoms for each cell are in a separate chunk.
             - If PAM1, the pseudo atoms for each cell are together in a 
               chunk.
            
            @param filename: The mmp filename containing the nanotube cell 
                             atoms.
            @type  filename: str
            
            @param subgroup: The part group to add the atoms to.
            @type  subgroup: L{Group}
            
            @param tfm: Transform applied to all new cell atoms.
            @type  tfm: V
            
            @param position: The origin in space of the DNA duplex, where the
                             3' end of strand A is 0, 0, 0.
            @type  position: L{V}
            """
            try:
                grouplist = readmmp(assy, filename, isInsert = True)
            except IOError:
                raise PluginBug("Cannot read file: " + filename)
            if not grouplist:
                raise PluginBug("No atoms in CNT? " + filename)
            
            viewdata, mainpart, shelf = grouplist
            
            for member in mainpart.members:
                # 'member' is a chunk containing a full set of 
                # unit cell pseudo atoms (ring).
                for atm in member.atoms.values():
                    atm._posn = tfm(atm._posn) + position
                
                member.name = "CellAxisChunk"
                subgroup.addchild(member)
                cntCellList.append(member)
            
            # Clean up.
            del viewdata                
            shelf.kill()

        def rotateTranslateXYZ(inXYZ, theta, z):
            """
            Returns the new XYZ coordinate rotated by I{theta} and 
            translated by I{z}.
            
            @param inXYZ: The original XYZ coordinate.
            @type  inXYZ: V
            
            @param theta: The unit cell twist angle.
            @type  theta: float
            
            @param z: The unit cell rise.
            @type  z: float
            
            @return: The new XYZ coordinate.
            @rtype:  V
            """
            c, s = cos(theta), sin(theta)
            x = c * inXYZ[0] + s * inXYZ[1]
            y = -s * inXYZ[0] + c * inXYZ[1]
            return V(x, y, inXYZ[2] + z)

        # Make the duplex.
        subgroup = group
        subgroup.open = False
        
        # Calculate the twist per unit cell in radians.
        if cellsPerTurn == 0.0:
            twistPerCell = 0.0
        else:
            twistPerCell = (self.handedness * 2 * pi) / cellsPerTurn
        theta        = 0.0
        z            = 0.5 * self.getCntRise() * (self.getNumberOfCells() - 1)
                
        # Create the nanotube.
        for i in range(self.getNumberOfCells()):
            basefile, zoffset, thetaOffset = \
                self._unitCellInfo(i)
            def tfm(v, theta = theta + thetaOffset, z1 = z + zoffset):
                return rotateTranslateXYZ(v, theta, z1)

            insertBaseFromMmp(basefile, subgroup, tfm)

            theta -= twistPerCell
            z     -= self.getCntRise()

        # Fuse the unit cell chunks together into a segment chunk.
        fcb = fusechunksBase()
        fcb.tol = 1.5
        for i in range(len(cntCellList) - 1):
            fcb.find_bondable_pairs([cntCellList[i]], [cntCellList[i + 1]])
            fcb.make_bonds(assy)
        
        try:
            self._postProcess(cntCellList)
        except:
            if env.debug():
                print_compact_traceback( 
                    "debug: exception in %r._postProcess(cntCellList = %r) \
                    (reraising): " % (self, cntCellList,))
            raise
        
        # Orient the duplex.
        self._orient(subgroup, endPoint1, endPoint2)
        
        # Regroup subgroup into strand and chunk groups
        #@self._regroup(subgroup)
        
        return

    def _postProcess(self, cntCellList):
        return
    
    def _baseFileName(self, basename):
        """
        Returns the full pathname to the mmp file containing the atom
        representing a single cell of a nanotube.
        
        Example: If I{basename} is "MidBasePair" and this is a PAM5 model of
        B-DNA, this returns:
         
          - "C:$HOME\cad\plugins\Nanotube\Carbon\PAM1\cell.mmp"
        """
        type    = self.type  # "Carbon" or "Boron Nitride"
        model   = self.model # "Atomistic" or "PAM1"
        return os.path.join(basepath, type, model, '%s.mmp' % basename)
    
    def _orient(self, cntGroup, pt1, pt2):
        """
        Orients the CNT I{cntGroup} based on two points. I{pt1} is
        the first endpoint (origin) of the nanotube. The vector I{pt1}, I{pt2}
        defines the direction and central axis of the nanotube.
        
        @param pt1: The starting endpoint (origin) of the DNA duplex.
        @type  pt1: L{V}
        
        @param pt2: The second point of a vector defining the direction
                    and central axis of the duplex.
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
        scalar = self.getCntRise() * (self.getNumberOfCells() - 1) * 0.5
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
        
        # Move and rotate the cell chunks into final orientation.
        for m in cntGroup.members:
            m.move(qrot.rot(m.center) - m.center + rawOffset + pt1)
            m.rot(qrot) #@ NEEDED?

    def getCntRise( self ):
        """
        Get the nanotube rise (i.e. spacing) between cells.
        """
        return float( self.cntRise )
    
    def setCntRise( self, inCntRise ):
        """
        Set the base rise (spacing) between base-pairs.
        
        @param inCntRise: The cnt rise in Angstroms.
        @type  inCntRise: float
        """
        self.cntRise  =  inCntRise
        
    def getNumberOfCells( self ):
        """
        Get the number of cells in this nanotube.
        """
        return self.numberOfCells
    
    def setNumberOfUnitCells( self, inNumberOfCells ):
        """
        Set the base rise (spacing) between base-pairs.
        
        @param inNumberOfCells: The number of base-pairs.
        @type  inNumberOfCells: int
        """
        self.numberOfCells  =  inNumberOfCells
        
    def setCellsPerTurn(self, cellsPerTurn):
        """
        Sets the number of cells per turn
        @param cellsPerTurn: Number of bases per turn
        @type  cellsPerTurn: int
        """
        self.cellsPerTurn = cellsPerTurn
    
    def getBasesPerTurn(self):
        """
        returns the number of bases per turn in the duplex
        """
        return self.cellsPerTurn
    
    pass

class Cnt(Nanotube):
    """
    Provides a carbon nanotube.
    """
    type = "Carbon"
    cntRise   =  2.0 # Ranges from ~1.5-4 Angstroms depending on chirality
    cellsPerTurn = 0.0
    handedness = RIGHT_HANDED
    
    def _isStartPosition(self, index):
        """
        Returns True if I{index} points the first position.
        
        @param index: Unit cell index.
        @type  index: int
        
        @return: True if index is zero.
        @rtype : bool
        """
        if index == 0:
            return True
        else:
            return False
        
    def _isEndPosition(self, index):
        """
        Returns True if I{index} points the last position.
        
        @param index: Unit cell index.
        @type  index: int
        
        @return: True if index is zero.
        @rtype : bool
        """
        if index ==  self.getNumberOfCells() - 1:
            return True
        else:
            return False

class Cnt_PAM1(Cnt):
    """
    Provides a PAM-1 reduced model carbon nanotube.
    """
    model = "PAM1"
    
    def _unitCellInfo(self, index):
        """
        Returns parameters needed to add a unit cell p-atom.
        
        @param index: Unit cell index.
        @type  index: int
        """
        zoffset      =  0.0
        thetaOffset  =  0.0
        basename     =  "CntAxisAtoms"
            
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)
    
class Cnt_Atomistic(Cnt):
    """
    Provides an atomistic model of a carbon nanotube.
    
    @note: Only 5x5 CNTs supported.
    """
    model = "Atomistic"
    
    def _unitCellInfo(self, index):
        """
        Returns parameters needed to add a unit cell p-atom.
        
        @param index: Unit cell index.
        @type  index: int
        """
        zoffset      =  0.0
        thetaOffset  =  0.0
        basename     =  "Cnt5x5CellAtoms"
            
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)
    
class BNNT(Cnt):
    """
    Boron Nitride nanotube (BNNT).
    """
    type = "Boron Nitride"
    
 
