# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaDuplex.py -- DNA duplex generator helper classes, based on empirical data.

@author: Mark Sims
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2007-10-18:
- Created. Major rewrite of DnaGenHelper.py.
"""

import foundation.env as env
import os
import random

from math    import sin, cos, pi

from debug import print_compact_traceback

from PlatformDependent  import find_plugin_dir
from files.mmp.files_mmp import readmmp
from geometry.VQT import Q, V, angleBetween, cross, vlen
from commands.Fuse.fusechunksMode import fusechunksBase
from utilities.Log      import orangemsg
from command_support.GeneratorBaseClass import PluginBug
from constants          import gensym, darkred, blue, orange, olive
from constants          import diBALL, diTUBES
from prefs_constants import dnaDefaultSegmentColor_prefs_key

from dna.model.Dna_Constants import getDuplexBasesPerTurn

from runSim import adjustSinglet

from model.elements import PeriodicTable
Element_Ae3 = PeriodicTable.getElement('Ae3')

from dna.model.Dna_Constants import basesDict, dnaDict

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

RIGHT_HANDED = -1
LEFT_HANDED  =  1

    
from geometry.VQT import V, Q, norm, cross  
from geometry.VQT import  vlen
from Numeric import dot

class Dna:
    """
    Dna base class. It is inherited by B_Dna and Z_Dna subclasses.
    
    @ivar baseRise: The rise (spacing) between base-pairs along the helical
                    (Z) axis.
    @type baseRise: float
    
    @ivar handedness: Right-handed (B and A forms) or left-handed (Z form).
    @type handedness: int
    
    @ivar model: The model representation, where:
                    - "PAM3" = PAM-5 reduced model.
                    - "PAM5" = PAM-5 reduced model.
                          
    @type model: str
    
    @ivar numberOfBasePairs: The number of base-pairs in the duplex.
    @type numberOfBasePairs: int
    
    @note: Atomistic models are not supported.
    """
        
    def make(self, 
             group, 
             numberOfBasePairs, 
             basesPerTurn, 
             duplexRise,
             endPoint1,
             endPoint2,
             position = V(0, 0, 0)):
        """
        Makes a DNA duplex with the I{numberOfBase} base-pairs. 
        The duplex is oriented with its central axis coincident to the
        line (endPoint1, endPoint1), with its origin at endPoint1.
        
        @param assy: The assembly (part).
        @type  assy: L{assembly}
        
        @param group: The group node object containing the DNA. The caller
                      is responsible for creating an empty group and passing
                      it here. When finished, this group will contain the DNA
                      model.
        @type  group: L{Group}
        
        @param numberOfBasePairs: The number of base-pairs in the duplex.
        @type  numberOfBasePairs: int
        
        @param basesPerTurn: The number of bases per helical turn.
        @type  basesPerTurn: float
        
        @param duplexRise: The rise; the distance between adjacent bases.
        @type  duplexRise: float
        
        @param endPoint1: The origin of the duplex.
        @param endPoint1: L{V}
        
        @param endPoint2: The second point that defines central axis of 
                          the duplex.
        @param endPoint2: L{V}
        
        @param position: The position in 3d model space at which to create
                         the DNA strand. This should always be 0, 0, 0.
        @type position:  position
        """      
        
        self.assy               =  group.assy         
        assy                    =  group.assy
        baseList                =  []
        
        self.setNumberOfBasePairs(numberOfBasePairs)
        self.setBaseRise(duplexRise)
        #See a note in DnaSegment_EditCommand._createStructure(). Should 
        #the parentGroup object <group> be assigned properties such as
        #duplexRise, basesPerTurn in this method itself? to be decided 
        #once dna data model is fully functional (and when this method is 
        #revised) -- Ninad 2008-03-05
        self.setBasesPerTurn(basesPerTurn)
        
        #End axis atom at end1. i.e. the first mouse click point from which 
        #user started drawing the dna duplex (rubberband line). This is initially
        #set to None. When we start creating the duplex and read in the first 
        #mmp file:  MiddleBasePair.mmp, we assign the appropriate atom to this 
        #variable. See self._determine_axis_and_strandA_endAtoms_at_end_1()
        self.axis_atom_end1 = None
        
        #The strand base atom of Strand-A, connected to the self.axis_atom_end1
        #The vector between self.axis_atom_end1 and self.strandA_atom_end1 
        #is used to determine the final orientation of the created duplex. 
        #that aligns this vector such that it is parallel to the screen. 
        #see self._orient_to_position_first_strandA_base_in_axis_plane() for more details.
        self.strandA_atom_end1 = None
        
        
        def insertBaseFromMmp(filename, 
                              subgroup, 
                              tfm, 
                              position = position
                             ):
            """
            Insert the atoms for a nucleic acid base from an MMP file into
            a single chunk.
             - If atomistic, the atoms for each base are in a separate chunk.
             - If PAM5, the pseudo atoms for each base-pair are together in a 
               chunk.
            
            @param filename: The mmp filename containing the base 
                             (or base-pair).
            @type  filename: str
            
            @param subgroup: The part group to add the atoms to.
            @type  subgroup: L{Group}
            
            @param tfm: Transform applied to all new base atoms.
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
                raise PluginBug("No atoms in DNA base? " + filename)
            
            viewdata, mainpart, shelf = grouplist
            
            for member in mainpart.members:
                # 'member' is a chunk containing a full set of 
                # base-pair pseudo atoms.
                                        
                for atm in member.atoms.values():                            
                    atm._posn = tfm(atm._posn) + position
                
                member.name = "BasePairChunk"
                subgroup.addchild(member)
                baseList.append(member)
            
            # Clean up.
            del viewdata                
            shelf.kill()

        def rotateTranslateXYZ(inXYZ, theta, z):
            """
            Returns the new XYZ coordinate rotated by I{theta} and 
            translated by I{z}.
            
            @param inXYZ: The original XYZ coordinate.
            @type  inXYZ: V
            
            @param theta: The base twist angle.
            @type  theta: float
            
            @param z: The base rise.
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
                        
        # Calculate the twist per base in radians.
        twistPerBase = (self.handedness * 2 * pi) / basesPerTurn
        theta = 0.0
        z     = 0.5 * self.getBaseRise() * (self.getNumberOfBasePairs() - 1)
                
        # Create duplex.
        for i in range(self.getNumberOfBasePairs()):
            basefile, zoffset, thetaOffset = \
                self._strandAinfo(i)
            def tfm(v, theta = theta + thetaOffset, z1 = z + zoffset):
                return rotateTranslateXYZ(v, theta, z1)
            
            insertBaseFromMmp(basefile, subgroup, tfm)
            
            if i == 0:
                #The chunk baseList[0] should always contain the information 
                #about the strand end and axis end atoms at end1 we are 
                #interested in. This chunk is obtained by reading in the 
                #first mmp file (at i =0) .
                
                #Note that we could have determined this after the for loop 
                #as well. But now harm in doing it here. This is also safe 
                #from any accidental modifications to the chunk after the for 
                #loop. Note that 'baseList' gets populated in 
                #sub 'def insertBasesFromMMP'.... Related TODO: The method 
                #'def make' itself needs reafcatoring so that all submethods are
                #direct methods of class Dna.
                #@see self._determine_axis_and_strandA_endAtoms_at_end_1() for 
                #more comments
                firstChunkInBaseList = baseList[0]
                self._determine_axis_and_strandA_endAtoms_at_end_1(baseList[0])

            theta -= twistPerBase
            z     -= self.getBaseRise()

        # Fuse the base-pair chunks together into continuous strands.
        fcb = fusechunksBase()
        fcb.tol = 1.5
        for i in range(len(baseList) - 1):
            fcb.find_bondable_pairs([baseList[i]], [baseList[i + 1]])
            fcb.make_bonds(assy)
        
        try:
            self._postProcess(baseList)
        except:
            if env.debug():
                print_compact_traceback( 
                    "debug: exception in %r._postProcess(baseList = %r) \
                    (reraising): " % (self, baseList,))
            raise
        
        # Orient the duplex.
        self._orient(subgroup, endPoint1, endPoint2)
           
        # Regroup subgroup into strand and chunk groups
        self._regroup(subgroup)
        return
    
    def _postProcess(self, baseList):
        return
    
    def _baseFileName(self, basename):
        """
        Returns the full pathname to the mmp file containing the atoms 
        of a nucleic acid base (or base-pair).
        
        Example: If I{basename} is "MidBasePair" and this is a PAM5 model of
        B-DNA, this returns:
         
          - "C:$HOME\cad\plugins\DNA\B-DNA\PAM5-bases\MidBasePair.mmp"
        
        @param basename: The basename of the mmp file without the extention
                         (i.e. "adenine", "MidBasePair", etc.).
        @type  basename: str
        
        @return: The full pathname to the mmp file.
        @rtype:  str
        """
        form    = self.form             # A-DNA, B-DNA or Z-DNA
        model   = self.model + '-bases' # PAM3 or PAM5
        return os.path.join(basepath, form, model, '%s.mmp' % basename)
    
    def _orient(self, dnaGroup, pt1, pt2):
        """
        Orients the DNA duplex I{dnaGroup} based on two points. I{pt1} is
        the first endpoint (origin) of the duplex. The vector I{pt1}, I{pt2}
        defines the direction and central axis of the duplex.
        
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
        scalar = self.getBaseRise() * (self.getNumberOfBasePairs() - 1) * 0.5
        rawOffset = b * scalar
        
        if 0: # Debugging code.
            print "~~~~~~~~~~~~~~"
            print "uVector  a = ", a
            print "uVector  b = ", b
            print "cross(a,b) =", axis
            print "theta      =", theta
            print "baserise   =", self.getBaseRise()
            print "# of bases =", self.getNumberOfBasePairs()
            print "scalar     =", scalar
            print "rawOffset  =", rawOffset 
        
        if theta == 0.0 or theta == 180.0:
            axis = V(0, 1, 0)
            # print "Now cross(a,b) =", axis
            
        rot =  (pi / 180.0) * theta  # Convert to radians
        qrot = Q(axis, rot) # Quat for rotation delta.
        
        # Move and rotate the base chunks into final orientation.
        for m in dnaGroup.members:
            m.move(qrot.rot(m.center) - m.center + rawOffset + pt1)
            m.rot(qrot)
        
        #do further adjustments so that first base of strandA always lies
        #in the screen parallel plane, which is passing through the 
        #axis. 
        self._orient_to_position_first_strandA_base_in_axis_plane(dnaGroup, 
                                                     pt1, 
                                                     pt2)
            
    def _determine_axis_and_strandA_endAtoms_at_end_1(self, chunk):
        """
        Overridden in subclasses. Default implementation does nothing. 
                
        @param chunk: The method itereates over chunk atoms to determine 
                      strand and axis end atoms at end 1. 
        @see: B_DNA_PAM3._determine_axis_and_strandA_endAtoms_at_end_1()
              for documentation and implementation. 
        """
        pass
    
    def _orient_to_position_first_strandA_base_in_axis_plane(self, segment, end1, end2):
        """
        Overridden in subclasses. Default implementation does nothing.
        
        The self._orient method orients the DNA duplex parallel to the screen
        (lengthwise) but it doesn't ensure align the vector
        through the strand end atom on StrandA and the corresponding axis end 
        atom  (at end1) , parallel to the screen. 
        
        This function does that ( it has some rare bugs which trigger where it
        doesn't do its job but overall works okay )
        
        What it does: After self._orient() is done orienting, it finds a Quat 
        that rotates between the 'desired vector' between strand and axis ends at
        end1(aligned to the screen)  and the actual vector based on the current
        positions of these atoms.  Using this quat we rotate all the chunks 
        (as a unit) around a common center. 
        
        @BUG: The last part 'rotating as a unit' uses a readymade method in 
        ops_motion.py -- 'rotateSpecifiedMovables' . This method itself may have
        some bugs because the axis of the dna duplex is slightly offset to the
        original axis. 
        
        @see: self._determine_axis_and_strandA_endAtoms_at_end_1()
        @see: self.make()
        
        @see: B_DNA_PAM3._orient_to_position_first_strandA_base_in_axis_plane
        
        """
        pass
    
    
    def _regroup(self, dnaGroup):
        """
        Regroups I{dnaGroup} into group containing three chunks: I{StrandA},
        I{StrandB} and I{Axis} of the DNA duplex.
        
        @param dnaGroup: The DNA group which contains the base-pair chunks
                         of the duplex.
        @type  dnaGroup: L{Group}
        
        @return: The new DNA group that contains the three chunks
                 I{StrandA}, I{StrandB} and I{Axis}.
        @rtype:  L{Group}
        """
         #Get the lists of atoms (two lists for two strands and one for the axis
         #for creating new chunks 
         
        _strandA_list, _strandB_list, _axis_list = \
                     self._create_atomLists_for_regrouping(dnaGroup)
        
        
                
        # Create strand and axis chunks from atom lists and add 
        # them to the dnaGroup.
        
        # [bruce 080111 add conditions to prevent bugs in PAM5 case
        #  which is not yet supported in the above code. It would be
        #  easy to support it if we added dnaBaseName assignments
        #  into the generator mmp files and generalized the above
        #  symbol names, and added a 2nd pass for Pl atoms.]

        if _strandA_list:
            strandAChunk = \
                     self.assy.makeChunkFromAtomList(
                         _strandA_list,
                         name = gensym("Strand"),
                         group = dnaGroup,
                         color = darkred)
        if _strandB_list:
            strandBChunk = \
                     self.assy.makeChunkFromAtomList(
                         _strandB_list,
                         name = gensym("Strand"),
                         group = dnaGroup,
                         color = blue)
        if _axis_list:
            axisChunk = \
                  self.assy.makeChunkFromAtomList(
                      _axis_list,
                      name = "Axis",
                      group = dnaGroup,
                      color = env.prefs[dnaDefaultSegmentColor_prefs_key])
            


        return

    def getBaseRise( self ):
        """
        Get the base rise (spacing) between base-pairs.
        """
        return float( self.baseRise )
    
    def setBaseRise( self, inBaseRise ):
        """
        Set the base rise (spacing) between base-pairs.
        
        @param inBaseRise: The base rise in Angstroms.
        @type  inBaseRise: float
        """
        self.baseRise  =  inBaseRise
        
    def getNumberOfBasePairs( self ):
        """
        Get the number of base-pairs in this duplex.
        """
        return self.numberOfBasePairs
    
    def setNumberOfBasePairs( self, inNumberOfBasePairs ):
        """
        Set the base rise (spacing) between base-pairs.
        
        @param inNumberOfBasePairs: The number of base-pairs.
        @type  inNumberOfBasePairs: int
        """
        self.numberOfBasePairs  =  inNumberOfBasePairs
        
    def setBasesPerTurn(self, basesPerTurn):
        """
        Sets the number of base pairs per turn
        @param basesPerTurn: Number of bases per turn
        @type  basesPerTurn: int
        """
        self.basesPerTurn = basesPerTurn
    
    def getBasesPerTurn(self):
        """
        returns the number of bases per turn in the duplex
        """
        return self.basesPerTurn
    
    pass

class A_Dna(Dna):
    """
    Provides an atomistic model of the A form of DNA.
    
    The geometry for A-DNA is very twisty and funky. We need to to research 
    the A form since it's not a simple helix (like B) or an alternating helix 
    (like Z).
    
    @attention: This class is not implemented yet.
    """
    form       =  "A-DNA"
    baseRise   =  dnaDict['A-DNA']['DuplexRise']
    handedness =  RIGHT_HANDED

class A_Dna_PAM5(A_Dna):
    """
    Provides a PAM-5 reduced model of the B form of DNA.
    
    @attention: This class is not implemented yet.
    """
    model = "PAM5"
    pass

class A_Dna_PAM3(A_Dna):
    """
    Provides a PAM-5 reduced model of the B form of DNA.
    
    @attention: This class is not implemented yet.
    """
    model = "PAM3"
    pass

class B_Dna(Dna):
    """
    Provides an atomistic model of the B form of DNA.
    """
    form       =  "B-DNA"
    baseRise   =  dnaDict['B-DNA']['DuplexRise']
    handedness =  RIGHT_HANDED
   
    basesPerTurn = getDuplexBasesPerTurn('B-DNA')   
    
    pass

class B_Dna_PAM5(B_Dna):
    """
    Provides a PAM-5 reduced model of the B form of DNA.
    """
    model = "PAM5"
    
    def _isStartPosition(self, index):
        """
        Returns True if I{index} points the first base-pair position (5').
        
        @param index: Base-pair index.
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
        Returns True if I{index} points the last base-pair position (3').
        
        @param index: Base-pair index.
        @type  index: int
        
        @return: True if index is zero.
        @rtype : bool
        """
        if index ==  self.getNumberOfBasePairs() - 1:
            return True
        else:
            return False
    
    def _strandAinfo(self, index):
        """
        Returns parameters needed to add a base, including its complement base,
        to strand A.
        
        @param index: Base-pair index.
        @type  index: int
        """
        zoffset      =  0.0
        thetaOffset  =  0.0
        basename     =  "MiddleBasePair"
        
        if self._isStartPosition(index):
            basename = "StartBasePair"
        
        if self._isEndPosition(index):
            basename = "EndBasePair"
            
        if self.getNumberOfBasePairs() == 1:
            basename = "SingleBasePair"
            
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)
    
    def _postProcess(self, baseList): # bruce 070414
        """
        Set bond direction on the backbone bonds.
        
        @param baseList: List of basepair chunks that make up the duplex.
        @type  baseList: list
        """
        # This implem depends on the specifics of how the end-representations
        # are terminated. If that's changed, it might stop working or it might
        # start giving wrong results. In the current representation, 
        # baseList[0] (a chunk) has two bonds whose directions we must set,
        # which will determine the directions of their strands: 
        #   Ss5 -> Sh5, and Ss5 <- Pe5.
        # Just find those bonds and set the strand directions (until such time
        # as they can be present to start with in the end1 mmp file).
        # (If we were instead passed all the atoms, we could be correct if we 
        # just did this to the first Pe5 and Sh5 we saw, or to both of each if 
        # setting the same direction twice is allowed.)
        atoms = baseList[0].atoms.values()
        Pe_list = filter( lambda atom: atom.element.symbol in ('Pe5'), atoms)
        Sh_list = filter( lambda atom: atom.element.symbol in ('Sh5'), atoms)
        
        if len(Pe_list) == len(Sh_list) == 1:
            for atom in Pe_list:
                assert len(atom.bonds) == 1
                atom.bonds[0].set_bond_direction_from(atom, 1, propogate = True)
            for atom in Sh_list:
                assert len(atom.bonds) == 1
                atom.bonds[0].set_bond_direction_from(atom, -1, propogate = True)
        else:
            #bruce 070604 mitigate bug in above code when number of bases == 1
            # by not raising an exception when it fails.
            msg = "Warning: strand not terminated, bond direction not set \
            (too short)"
            env.history.message( orangemsg( msg))
                
            # Note: It turns out this bug is caused by a bug in the rest of the
            # generator (which I didn't try to diagnose) -- for number of 
            # bases == 1 it doesn't terminate the strands, so the above code
            # can't find the termination atoms (which is how it figures out
            # what to do without depending on intimate knowledge of the base 
            # mmp file contents).

            # print "baseList = %r, its len = %r, atoms in [0] = %r" % \
            #       (baseList, len(baseList), atoms)
            ## baseList = [<molecule 'unknown' (11 atoms) at 0xb3d6f58>],
            ## its len = 1, atoms in [0] = [Ax1, X2, X3, Ss4, Pl5, X6, X7, Ss8, Pl9, X10, X11]
            
            # It would be a mistake to fix this here (by giving it that
            # intimate knowledge) -- instead we need to find and fix the bug 
            # in the rest of generator when number of bases == 1.
        return
    
    def _create_atomLists_for_regrouping(self, dnaGroup):
        """
        Creates and returns the atom lists that will be used to regroup the 
        chunks  within the DnaGroup. 
        
        @param dnaGroup: The DnaGroup whose atoms will be filtered and put into 
                         individual strand A or strandB or axis atom lists.
        @return: Returns a tuple containing three atom lists 
                 -- two atom lists for strand chunks and one for axis chunk. 
        @see: self._regroup()
        """
        _strandA_list  =  []
        _strandB_list  =  []
        _axis_list     =  []
        # Build strand and chunk atom lists.
        for m in dnaGroup.members:
            for atom in m.atoms.values():
                
                if atom.element.symbol in ('Pl5', 'Pe5'):
                    if atom.dnaStrandName == 'Strand1':
                        _strandA_list.append(atom)
                    elif atom.dnaStrandName == 'Strand2':
                        _strandB_list.append(atom)                        
                if atom.element.symbol in ('Ss5', 'Sh5'):
                    if atom.dnaBaseName == 'a':
                        _strandA_list.append(atom)
                        #Now reset the DnaBaseName for the added atom 
                        # to 'unassigned' base i.e. 'X'
                        atom.setDnaBaseName('X')
                    elif atom.dnaBaseName == 'b':
                        _strandB_list.append(atom)
                        #Now reset the DnaBaseName for the added atom 
                        # to 'unassigned' base i.e. 'X'
                        atom.setDnaBaseName('X')
                    else:
                        msg = "Ss3 atom not assigned to strand 'a' or 'b'."
                        raise PluginBug(msg)
                elif atom.element.symbol in ('Ax5', 'Ae5', 'Gv5', 'Gr5'):
                    _axis_list.append(atom)
                    
        return (_strandA_list, _strandB_list, _axis_list)

class B_Dna_PAM3(B_Dna_PAM5):
    """
    Provides a PAM-3 reduced model of the B form of DNA.
    """
    model = "PAM3"
    
    def _strandAinfo(self, index):
        """
        Returns parameters needed to add the next base-pair to the duplex 
        build built.
        
        @param index: Base-pair index.
        @type  index: int
        """
        
        zoffset      =  0.0
        thetaOffset  =  0.0
        basename     =  "MiddleBasePair"
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)
    
    
    
    def _postProcess(self, baseList):
        """
        Final tweaks on the DNA chunk, including:
        
          - Transmute Ax3 atoms on each end into Ae3.
          - Adjust open bond singlets.
        
        @param baseList: List of basepair chunks that make up the duplex.
        @type  baseList: list
        
        @note: baseList must contain at least two base-pair chunks.
        """

        start_basepair_atoms = baseList[0].atoms.values()
        end_basepair_atoms = baseList[-1].atoms.values()
        
        Ax_caps = filter( lambda atom: atom.element.symbol in ('Ax3'), 
                          start_basepair_atoms)
        Ax_caps += filter( lambda atom: atom.element.symbol in ('Ax3'), 
                           end_basepair_atoms)
            
        # Transmute Ax3 caps to Ae3 atoms. 
        # Note: this leaves two "killed singlets" hanging around,  
        #       one from each Ax3 cap.
        for atom in Ax_caps:
            atom.Transmute(Element_Ae3)
        
        # X_List will contain 6 singlets, 2 of which are killed (non-bonded).
        # The other 4 are the 2 pair of strand open bond singlets.
        X_List = filter( lambda atom: atom.element.symbol in ('X'), 
                          start_basepair_atoms)
        X_List += filter( lambda atom: atom.element.symbol in ('X'), 
                           end_basepair_atoms)
                
        # Adjust the 4 open bond singlets.
        for singlet in X_List:
            if singlet.killed():
                # Skip the 2 killed singlets.
                continue
            adjustSinglet(singlet)
        return
    
    def _determine_axis_and_strandA_endAtoms_at_end_1(self, chunk):
        """
        Determine the axis end atom and the strand atom on strand 1 
        connected to it , at end1 . i.e. the first mouse click point from which 
        user started drawing the dna duplex (rubberband line)
        
        These are initially set to None. 
        
        The strand base atom of Strand-A, connected to the self.axis_atom_end1
        The vector between self.axis_atom_end1 and self.strandA_atom_end1 
        is used to determine the final orientation of the created duplex
        done in self._orient_to_position_first_strandA_base_in_axis_plane()
        
        This vector is aligned such that it is parallel to the screen. 
        
        i.e. StrandA end Atom and corresponding axis end atom are coplaner and 
        parallel to the screen.   
        
        @NOTE:The caller should make sure that the appropriate chunk is passed 
              as an argument to this method. This function itself only finds 
              and assigns the axis ('Ax3') and strand ('Ss3' atom and on StrandA)
              atoms it sees first to the  respective attributes. (and which pass
              other necessary tests)        
              
        @see: self.make() where this function is called
        @see: self._orient_to_position_first_strandA_base_in_axis_plane()
        """
        for atm in chunk.atoms.itervalues():
            if self.axis_atom_end1 is None:
                if atm.element.symbol == 'Ax3':
                    self.axis_atom_end1 = atm
            if self.strandA_atom_end1 is None:
                if atm.element.symbol == 'Ss3' and atm.dnaBaseName == 'a':
                    self.strandA_atom_end1 = atm
    
    def _orient_to_position_first_strandA_base_in_axis_plane(self, segment, end1, end2):
        """
        The self._orient method orients the DNA duplex parallel to the screen
        (lengthwise) but it doesn't ensure align the vector
        through the strand end atom on StrandA and the corresponding axis end 
        atom  (at end1) , parallel to the screen. 
        
        This function does that ( it has some rare bugs which trigger where it
        doesn't do its job but overall works okay )
        
        What it does: After self._orient() is done orienting, it finds a Quat 
        that rotates between the 'desired vector' between strand and axis ends at
        end1(aligned to the screen)  and the actual vector based on the current
        positions of these atoms.  Using this quat we rotate all the chunks 
        (as a unit) around a common center.
        
        @BUG: The last part 'rotating as a unit' uses a readymade method in 
        ops_motion.py -- 'rotateSpecifiedMovables' . This method itself may have
        some bugs because the axis of the dna duplex is slightly offset to the
        original axis. 
        
        @see: self._determine_axis_and_strandA_endAtoms_at_end_1()
        @see: self.make()
        """
        
        #the vector between the two end points. these are more likely
        #points clicked by the user while creating dna duplex using endpoints
        #of a line. In genral, end1 and end2 are obtained from self.make()
        b = norm(end2 - end1)        
                
        axis_strand_vector = (self.strandA_atom_end1.posn() - \
                              self.axis_atom_end1.posn())
               
        vectorAlongLadderStep =  cross(-self.assy.o.lineOfSight, b)
        unitVectorAlongLadderStep = norm(vectorAlongLadderStep)
                        
        self.final_pos_strand_end_atom = \
            self.axis_atom_end1.posn() + \
            vlen(axis_strand_vector)*unitVectorAlongLadderStep
        
        expected_vec = self.final_pos_strand_end_atom - self.axis_atom_end1.posn()
        
        q_new = Q(axis_strand_vector, expected_vec)
        
        if dot(axis_strand_vector, self.assy.o.lineOfSight) < 0:            
            q_new2 = Q(b, -q_new.angle)
        else:     
            q_new2 = Q(b, q_new.angle)      
                
        self.assy.rotateSpecifiedMovables(q_new2, segment.members)
        
                
    def _create_atomLists_for_regrouping(self, dnaGroup):
        """
        Creates and returns the atom lists that will be used to regroup the 
        chunks  within the DnaGroup. 
        
        @param dnaGroup: The DnaGroup whose atoms will be filtered and put into 
                         individual strand A or strandB or axis atom lists.
        @return: Returns a tuple containing three atom lists 
                 -- two atom lists for strand chunks and one for axis chunk. 
        @see: self._regroup()
        """
        _strandA_list  =  []
        _strandB_list  =  []
        _axis_list     =  []
        
        # Build strand and chunk atom lists.
        for m in dnaGroup.members:
            for atom in m.atoms.values():
                if atom.element.symbol in ('Ss3'):
                    if atom.dnaBaseName == 'a':
                        _strandA_list.append(atom)
                        #Now reset the DnaBaseName for the added atom 
                        # to 'unassigned' base i.e. 'X'
                        atom.setDnaBaseName('X')
                    elif atom.dnaBaseName == 'b':
                        _strandB_list.append(atom)
                        #Now reset the DnaBaseName for the added atom 
                        # to 'unassigned' base i.e. 'X'
                        atom.setDnaBaseName('X')
                    else:
                        msg = "Ss3 atom not assigned to strand 'a' or 'b'."
                        raise PluginBug(msg)
                elif atom.element.symbol in ('Ax3', 'Ae3'):
                    _axis_list.append(atom)
                    
        return (_strandA_list, _strandB_list, _axis_list)
        
    

class Z_Dna(Dna):
    """
    Provides an atomistic model of the Z form of DNA.
    """
    
    form       =  "Z-DNA"
    baseRise   =  dnaDict['Z-DNA']['DuplexRise']
    handedness =  LEFT_HANDED
    
class Z_Dna_Atomistic(Z_Dna):
    """
    Provides an atomistic model of the Z form of DNA.
    
    @attention: This class will never be implemented.
    """
    model = "PAM5"
    
    def _strandAinfo(self, baseLetter, index):
        """
        Returns parameters needed to add a base to strand A.
        
        @param baseLetter: The base letter.
        @type  baseLetter: str
        
        @param index: Base-pair index.
        @type  index: int
        """
        
        thetaOffset  =  0.0
        basename  =  basesDict[baseLetter]['Name']
        
        if (index & 1) != 0: 
            # Index is odd.
            basename  +=  "-outer"
            zoffset    =  2.045
        else: 
            # Index is even.
            basename  +=  '-inner'
            zoffset    =  0.0
        
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

    def _strandBinfo(self, baseLetter, index):
        """
        Returns parameters needed to add a base to strand B.
        
        @param baseLetter: The base letter.
        @type  baseLetter: str
        
        @param index: Base-pair index.
        @type  index: int
        """
        
        thetaOffset  =  0.5 * pi
        basename     =  basesDict[baseLetter]['Name']
        
        if (index & 1) != 0:
            basename  +=  '-inner'
            zoffset    =  -0.055
        else:
            basename  +=  "-outer"
            zoffset    =  -2.1
        
        basefile     = self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

class Z_Dna_PAM5(Z_Dna):
    """
    Provides a PAM-5 reduced model of the Z form of DNA.
    
    @attention: This class is not implemented yet.
    """
    pass
    
