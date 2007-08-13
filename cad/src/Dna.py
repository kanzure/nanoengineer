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
from VQT                import A, V, vlen
from chem               import Atom
from bonds              import inferBonds, bond_atoms
from fusechunksMode     import fusechunksBase
from HistoryWidget      import orangemsg
from GeneratorBaseClass import PluginBug
from Utility            import Group

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
numberPattern = re.compile(r"^\s*(\d+)\s*$")

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

END1 = '[' # these must be single characters, not used for base letters. 
END2 = ']'

DEBUG = False
DEBUG_SEQUENCE  =  False

RIGHT_HANDED = -1
LEFT_HANDED  =  1

class Dna:
    """
    Dna base class. It is inherited by B_Dna and Z_Dna subclasses.
    
    @ivar baseRise: The rise (spacing) between base-pairs along the helical
                    (Z) axis.
    @type baseRise: float
    
    @ivar handedness: Right-handed (B and A forms) or left-handed (Z form).
    @type handedness: int
    
    @ivar doubleStrand: Double (True) or single (False).
    @type doubleStrand: bool
    
    @ivar representation: The model representation, where:
                          - "Atom" = atomistic model
                          - "PAM5" = PAM-5 reduced model.
    @type representation: str
    
    @ivar sequence: The sequence of strand A.
    @type sequence: str
    
    @ivar sequenceA: The sequence of strand A.
    @type sequenceA: str
    
    @ivar sequenceB: The sequence of strand B.
    @type sequenceB: str
    """
    basesDict  =  { 'A':{'Name':'Adenine',   'Complement':'T'},
                    'C':{'Name':'Cytosine',  'Complement':'G'},
                    'G':{'Name':'Guanine',   'Complement':'C'},
                    'T':{'Name':'Thymine',   'Complement':'A'},
                    'N':{'Name':'aNy base',  'Complement':'N'} }
    
    baseRise       = 0.0
    handedness     = None
    doubleStrand   = True
    representation = ""
    sequence       = ""
    sequenceA      = sequence

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

    def make(self,
             assy,
             grp,
             basesPerTurn,
             position,
             basenameA = { 'C': 'cytosine',
                           'G': 'guanine',
                           'A': 'adenine',
                           'T': 'thymine',
                           'N': 'unknown',
                          END1: 'end1',
                          END2: 'end2'},
             basenameB = { 'G': 'cytosine',
                           'C': 'guanine',
                           'T': 'adenine',
                           'A': 'thymine',
                           'N': 'unknown',
                          END1: 'end1',
                          END2: 'end2'}
             ):
        """
        Make a strand of DNA.
        
        @param assy: The assembly (part).
        @type  assy: L{assembly}
        
        @param grp: The group node to contain the DNA.
        @type  grp: L{Group}
        
        @param basesPerTurn: The number of bases per helical turn.
        @type  basesPerTurn: float
        
        @param position: The position in 3d model space at which to
                         create the DNA strand. This is always 0, 0, 0.
        @type position:  position
        
        @param basenameA: A dictionary of legal (supported) bases in strand A.
        @type  basenameA: dict
        
        @param basenameB: A dictionary of legal (supported) bases in strand B.
                          Strand B is always complementary to strand A.
        @type  basenameB: dict
        """
        
        sequence = self.sequence
        baseList = []
        
        if DEBUG_SEQUENCE:
            print "Making", sequence
            
        def insertmmp(filename, subgroup, tfm, position = position):
            """
            Read the mmp file containing the atoms for a nucleic acid base.
            
            @param filename: The mmp filename.
            @type  filename: str
            
            @param subgroup:
            @type  subgroup: L{Group}
            
            @param tfm: Transformation matrix applied to all new base atoms.
            @type  tfm: V
            
            @param position:
            @type  position:
            """
            try:
                grouplist = _readmmp(assy, filename, isInsert = True)
            except IOError:
                raise PluginBug("Cannot read file: " + filename)
            if not grouplist:
                raise PluginBug("No atoms in DNA base? " + filename)
            viewdata, mainpart, shelf = grouplist
            for member in mainpart.members:
                for atm in member.atoms.values():
                    atm._posn = tfm(atm._posn) + position
            del viewdata
                   
            for member in mainpart.members:
                subgroup.addchild(member)
                baseList.append(member)
                
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

        # Calculate the twist per base in radians.
        twistPerBase = (self.handedness * 2 * pi) / basesPerTurn
        
        if self.doubleStrand:
            subgroup = Group("strand 1", grp.assy, None)
            grp.addchild(subgroup)
        else:
            subgroup = grp
        subgroup.open = False

        if (sequence.isdigit()):
            baseCount = int(sequence)
            sequence = baseCount * "N"
            
        sequence = self._addEndCaps(sequence)
        theta = 0.0
        z = 0.5 * self.baseRise * (len(sequence) - 1)
        
        # Create strand A.
        for i in range(len(sequence)):
            basefile, zoffset, thetaOffset = \
                self._strandAinfo(basenameA[sequence[i]], i)
            def tfm(v, theta = theta + thetaOffset, z1 = z + zoffset):
                return rotateTranslateXYZ(v, theta, z1)
            if DEBUG: 
                print basefile
            insertmmp(basefile, subgroup, tfm)
            theta -= twistPerBase
            z     -= self.baseRise
        
        # Create strand B.
        if self.doubleStrand:
            subgroup = Group("strand 2", grp.assy, None)
            subgroup.open = False
            grp.addchild(subgroup)
            
            theta = 0.0
            z     = 0.5 * self.baseRise * (len(sequence) - 1)
            
            for i in range(len(sequence)):
                # The 3'-to-5' direction is reversed for strand B.
                basefile, zoffset, thetaOffset = \
                    self._strandBinfo(basenameB[sequence[i]], i)
                def tfm(v, theta = theta + thetaOffset, z1 = z + zoffset):
                    # Flip theta, flip z
                    # Cheesy hack: flip theta by reversing the sign of y,
                    # since theta = atan2(y,x)
                    return rotateTranslateXYZ(V(v[0], -v[1], -v[2]), theta, z1)
                if DEBUG: print basefile
                insertmmp(basefile, subgroup, tfm)
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

    def _addEndCaps(self, sequence):
        return sequence

    def _postProcess(self, baseList):
        return
    pass

class A_Dna(Dna):
    """
    Provides an atomistic model of the A form of DNA.
    
    The geometry for A-DNA is very twisty and funky. We need to to research 
    the A form since it's not a simple helix (like B) or an alternating helix 
    (like Z).
    
    @attention: This class is not implemented yet.
    """
    geometry   = "A-DNA"
    baseRise   = 3.391 # WRONG
    handedness = RIGHT_HANDED
    
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
    
    geometry   = "B-DNA"
    baseRise   = 3.391        # Angstroms
    handedness = RIGHT_HANDED

    def _baseFileName(self, basename):
        """
        Returns the full pathname to the mmp file containing the atoms 
        of a nucleic acid base (B form).
        
        @param basename: The basename of the mmp file (i.e. "adenine", 
                         "cytosine", "guanine", "thymine" or "unknown").
        @type  basename: str
        
        @return: The full pathname to the mmp file.
        @rtype:  str
        """
        return os.path.join(basepath, 
                            'bdna-bases', '%s.mmp' % basename)

    def _strandAinfo(self, basename, index):
        """
        Returns parameters needed to add a base to strand A.
        
        @param basename: The basename of the mmp file (i.e. "adenine", 
                         "cytosine", "guanine", "thymine" or "unknown").
        @type  basename: str
        
        @param index: Index in base sequence. This is unused.
        @type  index: int
        """
        zoffset = 0.0
        thetaOffset = 0.0
        basefile = self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

    def _strandBinfo(self, basename, index):
        """
        Returns parameters needed to add a base to strand B.
        
        @param basename: The basename of the mmp file (i.e. "adenine", 
                         "cytosine", "guanine", "thymine" or "unknown").
        @type  basename: str
        
        @param index: Index in base sequence. This is unused.
        @type  index: int
        """
        zoffset = 0.0
        thetaOffset = 210 * (pi / 180)
        basefile = self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

class B_Dna_PAM5(B_Dna):
    """
    Provides a PAM-5 reduced model of the B form of DNA.
    """
    
    baseRise   = 3.18         # Angstroms
    handedness = RIGHT_HANDED
    
    def _baseFileName(self, basename):
        """
        Returns the full pathname to the mmp file containing the PAM-5 
        pseudo-atoms of a nucleic acid base.
        
        @param basename: The basename of the mmp file (i.e. "adenine", 
                         "cytosine", "guanine", "thymine" or "unknown").
        @type  basename: str
        
        @return: The full pathname to the mmp file.
        @rtype:  str
        """
        return os.path.join(basepath, 
                            'bdna-pseudo-bases', '%s.mmp' % basename)
    
    def _addEndCaps(self, sequence):
        """
        Add end cap characters to I{sequence}.
        
        @param sequence: The DNA sequence of strand A.
        @type  sequence: str
        """
        if (len(sequence) > 1):
            return END1 + sequence[1:-1] + END2 
            #bruce 070518 replaced end-codes 'Y' and 'Z' with END1 and END2
        return sequence
    
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
    
    geometry   = "Z-DNA"
    baseRise   = 3.715        # Angstroms
    handedness = LEFT_HANDED

    def _baseFileName(self, basename, suffix):
        """
        Returns the full pathname to the mmp file containing the atoms 
        of a nucleic acid base (Z form).
        
        @param basename: The basename of the mmp file (i.e. "adenine", 
                         "cytosine", "guanine", "thymine" or "unknown").
        @type  basename: str
        
        @param suffix: Determines whether the "inner" or "outer" version of the
                       base is used.
        @type  suffix: str
        
        @return: The full pathname to the mmp file.
        @rtype:  str
        """
        return os.path.join(basepath, 
                            'zdna-bases', '%s-%s.mmp' % (basename, suffix))

    def _strandAinfo(self, basename, index):
        """
        Returns parameters needed to add a base to strand A.
        
        @param basename: The basename of the mmp file (i.e. "adenine", 
                         "cytosine", "guanine", "thymine" or "unknown").
        @type  basename: str
        
        @param index: Index in base sequence.
        @type  index: int
        """
        if (index & 1) != 0:
            suffix = 'outer'
            zoffset = 2.045
        else:
            suffix = 'inner'
            zoffset = 0.0
        thetaOffset = 0.0
        basefile = self._baseFileName(basename, suffix)
        return (basefile, zoffset, thetaOffset)

    def _strandBinfo(self, basename, index):
        """
        Returns parameters needed to add a base to strand B.
        
        @param basename: The basename of the mmp file (i.e. "adenine", 
                         "cytosine", "guanine", "thymine" or "unknown").
        @type  basename: str
        
        @param index: Index in base sequence. This is unused.
        @type  index: int
        """
        if (index & 1) != 0:
            suffix = 'inner'
            zoffset = -0.055
        else:
            suffix = 'outer'
            zoffset = -2.1
        thetaOffset = 0.5 * pi
        basefile = self._baseFileName(basename, suffix)
        return (basefile, zoffset, thetaOffset)

class Z_Dna_PAM5(Z_Dna):
    """
    Provides a PAM-5 reduced model of the Z form of DNA.
    
    @attention: This class is not implemented yet.
    """
    pass
    
