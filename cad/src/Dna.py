# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DNA model classes based on empirical data.

@author: Will Ware
@version:
@copyright: Copyright (c) 2007 Nanorex, Inc.  All rights reserved.

DNA.py

$Id$

History:
Jeff 2007-06-13 (created)
  - Transfered class Dna, A_Dna, A_Dna_PAM5, B_Dna, B_Dna_PAM5, 
    Z_Dna abd Z_Dna_PAM5 from Will Ware's DNAGenerator.py.
  - Added accessor methods getBaseRise/setBaseRise
Mark 2007-08-17:
  - make() creates a duplex structure only (no single strands).
  - Created standard directory structure for DNA MMP files.
  - PAM5 MMP files reworked and simplfied.
  - A single PAM5 base-pair duplex is made correctly.
  - Moved Dna constants to Dna_Constants.py. 
  - Changed default base to "X" (unassigned) from "N" (aNy base).
  - Implemented Standard IUB Codes (see Dna_Constants.py)
"""

# To do:
#
# 1) Atomistic and PAM-5 generated models should have exact orientation
# (i.e. rotational origin).

import env
import os
import re

from math    import atan2, sin, cos, pi
from Numeric import dot

from debug import print_compact_traceback

from platform           import find_plugin_dir
from files_mmp          import _readmmp
from VQT                import V
from chem               import Atom
from bonds              import inferBonds, bond_atoms
from fusechunksMode     import fusechunksBase
from HistoryWidget      import orangemsg
from GeneratorBaseClass import PluginBug
from Utility            import Group

from Dna_Constants import basesDict, dnaDict
from Dna_Constants import PAM5_AtomList # Used only if INSERT_FROM_MMP = False

from chunk         import molecule #@ For insertBaseFromAtomList.

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
numberPattern = re.compile(r"^\s*(\d+)\s*$")

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

RIGHT_HANDED = -1
LEFT_HANDED  =  1

DEBUG = False
DEBUG_SEQUENCE   =  False
INSERT_FROM_MMP  =  True

class Dna:
    """
    Dna base class. It is inherited by B_Dna and Z_Dna subclasses.
    
    @ivar baseRise: The rise (spacing) between base-pairs along the helical
                    (Z) axis.
    @type baseRise: float
    
    @ivar handedness: Right-handed (B and A forms) or left-handed (Z form).
    @type handedness: int
    
    @ivar model: The model representation, where:
                          - "Atomistic" = atomistic model
                          - "PAM5" = PAM-5 reduced model.
    @type model: str
    
    @ivar originalSequence: The original DNA sequence of strand A.
    @type originalSequence: str
    
    @ivar knownSequence: The sequence in which any unrecognized base is converted to 'N'.
    @type knownSequence: str
    """
        
    def make(self, group, inSequence, basesPerTurn, position):
        """
        Makes a PAM5 or atomistic DNA structure.
        
        @param assy: The assembly (part).
        @type  assy: L{assembly}
        
        @param group: The group node object containing the DNA.
        @type  group: L{Group}
        
        @param basesPerTurn: The number of bases per helical turn.
        @type  basesPerTurn: float
        
        @param position: The position in 3d model space at which to
                         create the DNA strand. This is always 0, 0, 0.
        @type position:  position
        """        
        assy                =  group.assy
        originalSequence    =  inSequence       
        self.knownSequence  =  self.removeUnrecognized(originalSequence)
        sequence            =  self.knownSequence
        baseList            =  []
        
        if DEBUG_SEQUENCE:
            print "Making", sequence
        
        def insertBaseFromMmp(filename, subgroup, tfm, position = position):
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
                grouplist = _readmmp(assy, filename, isInsert = True)
            except IOError:
                raise PluginBug("Cannot read file: " + filename)
            if not grouplist:
                raise PluginBug("No atoms in DNA base? " + filename)
            
            viewdata, mainpart, shelf = grouplist
            
            for member in mainpart.members:
                # 'member' is a chunk containing a set of single base atoms
                #  when creating an atomistic model of DNA.
                # 'member' is a chunk containing a set of base-pair 
                #  pseudo-atoms when creating a PAM-5 model of DNA.
                for atm in member.atoms.values():
                    atm._posn = tfm(atm._posn) + position
                    if atm.element.symbol == "Ss":
                        if atm.dnaBaseName == "a":
                            baseLetter = currentBaseLetter
                        else:
                            try:
                                baseLetter = basesDict[currentBaseLetter]['Complement']
                            except:
                                # If complement not found, just assign same letter.
                                baseLetter = currentBaseLetter
                        if DEBUG_SEQUENCE:
                            print "Ss(%r) being set to %r." % (atm.dnaBaseName, baseLetter)
                        atm.setDnaBaseName(baseLetter)
                
                member.name = currentBaseLetter
                subgroup.addchild(member)
                baseList.append(member)
            
            # Clean up.
            del viewdata                
            shelf.kill()
            
        def insertBaseFromAtomList(subgroup, tfm, position = position):
            """
            Inserts a PAM-5 base-pair using a list of PAM-5 atoms.
            
            @attention: This is a test to see if creating long PAM-5 
                        structures is faster this way vs. insertBaseFromMmp().
                        It is not fully working as of 2007-08-18.
            """
            _name = "TESTING"
            
            newChunk  =  molecule( assy, _name )
            
            lastAtom = None
            aList = []
            
            atomList = PAM5_AtomList['midBasePair']
            
            for atom in atomList:
                
                symbol   =  atom[0]
                xyz      =  atom[1]
                a_or_b   =  atom[2]
                newAtom  =  Atom( symbol, xyz, newChunk )
                
                newAtom._posn = tfm(newAtom._posn) + position

                if lastAtom:
                    # Order of atoms in list makes difference!
                    newChunk.bond(newAtom, lastAtom)
                
                if symbol == "Ss":
                    if a_or_b == "a":
                        baseLetter = currentBaseLetter
                    else:
                        try:
                            baseLetter = basesDict[currentBaseLetter]['Complement']
                        except:
                            # If complement not found, just assign same letter.
                            baseLetter = currentBaseLetter
                            
                    newAtom.setDnaBaseName(baseLetter)
                    if DEBUG_SEQUENCE:
                        print "Ss(%r) being set to %r." % (newAtom.dnaBaseName, baseLetter)
                
                lastAtom = newAtom
                
                aList.append(newAtom)
            
            for atom in aList:
                atom.remake_bondpoints()
                
            subgroup.addchild(newChunk)
            baseList.append(newChunk)
            
            return

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

        # Create group for strand A (atomistic mdoel only).
        if (self.model == 'Atomistic'):
            subgroup = Group("Strand A", assy, None)
            group.addchild(subgroup)
        else:
            subgroup = group
        subgroup.open = False
        
        # Calculate the twist per base in radians.
        twistPerBase = (self.handedness * 2 * pi) / basesPerTurn
        theta        = 0.0
        z            = 0.5 * self.baseRise * (len(sequence) - 1)
                
        # Create strand A.
        for i in range(len(sequence)):
            currentBaseLetter = originalSequence[i]
            basefile, zoffset, thetaOffset = \
                self._strandAinfo(currentBaseLetter, i)
            def tfm(v, theta = theta + thetaOffset, z1 = z + zoffset):
                return rotateTranslateXYZ(v, theta, z1)
            if DEBUG: 
                print basefile
            
            if INSERT_FROM_MMP:
                insertBaseFromMmp(basefile, subgroup, tfm)
            else:
                # Warning: Cannot create atomistic DNA structures.
                insertBaseFromAtomList(subgroup, tfm)
            theta -= twistPerBase
            z     -= self.baseRise
        
        # Create strand B (atomistic model only).
        if (self.model == 'Atomistic'):
            subgroup = Group("Strand B", assy, None)
            subgroup.open = False
            group.addchild(subgroup)
            
            theta = 0.0
            z     = 0.5 * self.baseRise * (len(sequence) - 1)
            
            strandB = self.getComplementSequence(sequence)
            for i in range(len(sequence)):
                # The 3'-to-5' direction is reversed for strand B.
                currentBaseLetter = strandB[i]
                basefile, zoffset, thetaOffset = \
                    self._strandBinfo(currentBaseLetter, i)
                def tfm(v, theta = theta + thetaOffset, z1 = z + zoffset):
                    # Flip theta, flip z
                    # Cheesy hack: flip theta by reversing the sign of y,
                    # since theta = atan2(y,x)
                    return rotateTranslateXYZ(V(v[0], -v[1], -v[2]), theta, z1)
                if DEBUG: 
                    print basefile
                insertBaseFromMmp(basefile, subgroup, tfm)
                theta -= twistPerBase
                z     -= self.baseRise

        # Fuse the bases together into continuous strands.
        
        fcb = fusechunksBase()
        fcb.tol = 1.5
        for i in range(len(baseList) - 1):
            fcb.find_bondable_pairs([baseList[i]], [baseList[i + 1]])
            fcb.make_bonds(assy)
        
        try:
            self._postProcess(baseList)
        except:
            if env.debug():
                print_compact_traceback("debug: exception in %r._postProcess(baseList = %r) (reraising): " % (self, baseList,))
            raise
        
        
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
        model   = self.model + '-bases' # Atomistic or PAM5
        return os.path.join(basepath, form, model, '%s.mmp' % basename)

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
        
    def getComplementSequence(self, inSequence):
        """
        Returns the complement DNA sequence.
        
        @param inSequence: The original DNA sequence.
        @type  inSequence: str
        
        @return: The complement DNA sequence.
        @rtype:  str
        """
        assert isinstance(inSequence, str)
        outSequence = ""
        for baseLetter in inSequence:
            if baseLetter not in basesDict.keys():
                baseLetter = "N"
            else:
                baseLetter = basesDict[baseLetter]['Complement']
            outSequence += baseLetter
        return outSequence
        
    def getReverseSequence(self, inSequence):
        """
        Reverses the order of the DNA sequence I{inSequence}.
        
        @param inSequence: The original DNA sequence.
        @type  inSequence: str
        
        @return: The reversed sequence.
        @rtype:  str
        """
        assert isinstance(inSequence, str)
        outSequence = list(inSequence)
        outSequence.reverse()
        outSequence = ''.join(outSequence)
        return outSequence
    
    def removeUnrecognized(self, inSequence, replaceBase = "N"):
        """
        Removes any unrecognized/invalid characters (alphanumeric or
        symbolic) from the DNA sequence.
        """
        assert isinstance(inSequence, str)
        outSequence = ""
        for baseLetter in inSequence:
            if baseLetter not in basesDict.keys():  # 'CGATN'
                baseLetter = replaceBase
            outSequence += baseLetter
        if DEBUG_SEQUENCE:
            print " inSequence:", inSequence
            print "outSequence:", outSequence
        return outSequence
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
    model      =  "Atomistic"
    baseRise   =  dnaDict['A-DNA']['DuplexRise']
    handedness =  RIGHT_HANDED
    
    def _strandAinfo(self, sequence, index):
        """
        Raise exception since A-DNA is not support. 
        """
        raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");
    
    def _strandBinfo(self, sequence, index):
        """
        Raise exception since A-DNA is not support. 
        """
        raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");

class A_Dna_PAM5(A_Dna):
    """
    Provides a PAM-5 reduced model of the B form of DNA.
    
    @attention: This class is not implemented yet.
    """
    pass

class B_Dna(Dna):
    """
    Provides an atomistic model of the B form of DNA.
    """
    form       =  "B-DNA"
    model      =  "Atomistic"
    baseRise   =  dnaDict['B-DNA']['DuplexRise']
    handedness =  RIGHT_HANDED
    
    def _strandAinfo(self, baseLetter, index):
        """
        Returns parameters needed to add a base to strand A.
        
        @param baseLetter: The base letter.
        @type  baseLetter: str
        
        @param index: Index in base sequence. This is unused.
        @type  index: int
        """
        zoffset      =  0.0
        thetaOffset  =  0.0
        basename     =  basesDict[baseLetter]['Name']
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

    def _strandBinfo(self, baseLetter, index):
        """
        Returns parameters needed to add a base to strand B.
        
        @param baseLetter: The base letter.
        @type  baseLetter: str
        
        @param index: Index in base sequence. This is unused.
        @type  index: int
        """
        zoffset      =  0.0
        thetaOffset  =  210 * (pi / 180)
        basename     =  basesDict[baseLetter]['Name']
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

class B_Dna_PAM5(B_Dna):
    """
    Provides a PAM-5 reduced model of the B form of DNA.
    """
    model      =  "PAM5"
    
    def _isStartPosition(self, index):
        """
        Returns True if index points the first base position (5') of 
        self's sequence.
        
        @param index: Index in base sequence.
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
        Returns True if index points the last base position (3') of self's 
        sequence.
        
        @param index: Index in base sequence.
        @type  index: int
        
        @return: True if index is zero.
        @rtype : bool
        """
        if index ==  len(self.knownSequence) - 1:
            return True
        else:
            return False
    
    def _strandAinfo(self, baseLetter, index):
        """
        Returns parameters needed to add a base to strand A.
        
        @param baseLetter: The base letter.
        @type  baseLetter: str
        
        @param index: Index in base sequence.
        @type  index: int
        """
        zoffset      =  0.0
        thetaOffset  =  0.0
        basename     =  "MiddleBasePair"
        
        if self._isStartPosition(index):
            basename = "StartBasePair"
        
        if self._isEndPosition(index):
            basename = "EndBasePair"
            
        if len(self.knownSequence) == 1:
            basename = "SingleBasePair"
            
        
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)
    
    def _postProcess(self, baseList): # bruce 070414
        # Figure out how to set bond direction on the backbone bonds of these strands.
        # This implem depends on the specifics of how the end-representations are terminated.
        # If that's changed, it might stop working or it might start giving wrong results.
        # In the current representation,
        # baseList[0] (a chunk) is called "end1" in MT, and has two bonds whose directions we should set,
        # which will determine the directions of their strands: Ss -> Sh, and Ss <- Pe.
        # Just find those bonds and set the strand directions
        # (until such time as they can be present to start with in the end1 mmp file).
        # (If we were instead passed all the atoms, we could be correct if we just did this
        #  to the first Pe and Sh we saw, or to both of each if setting the same direction twice
        #  is allowed.)
        atoms = baseList[0].atoms.values()
        Pe_list = filter( lambda atom: atom.element.symbol == 'Pe', atoms)
        Sh_list = filter( lambda atom: atom.element.symbol == 'Sh', atoms)
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

            env.history.message( orangemsg( "Warning: strand not terminated, bond direction not set (too short)"))
                
            # Note: It turns out this bug is caused by a bug in the rest of the generator
            # (which I didn't try to diagnose) -- for number of bases == 1 it doesn't terminate the strands,
            # so the above code can't find the termination atoms (which is how it figures out
            # what to do without depending on intimate knowledge of the base mmp file contents).

            # print "baseList = %r, its len = %r, atoms in [0] = %r" % (baseList, len(baseList), atoms)
            ## baseList = [<molecule 'unknown' (11 atoms) at 0xb3d6f58>],
            ## its len = 1, atoms in [0] = [Ax1, X2, X3, Ss4, Pl5, X6, X7, Ss8, Pl9, X10, X11]
            
            # It would be a mistake to fix this here (by giving it that intimate knowledge) --
            # instead we need to find and fix the bug in the rest of generator when number of bases == 1.
        return
    pass

class Z_Dna(Dna):
    """
    Provides an atomistic model of the Z form of DNA.
    """
    
    form       =  "Z-DNA"
    model      =  "Atomistic"
    baseRise   =  dnaDict['Z-DNA']['DuplexRise']
    handedness =  LEFT_HANDED

    def _strandAinfo(self, baseLetter, index):
        """
        Returns parameters needed to add a base to strand A.
        
        @param baseLetter: The base letter.
        @type  baseLetter: str
        
        @param index: Index in base sequence.
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
        
        @param index: Index in base sequence. This is unused.
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
    
