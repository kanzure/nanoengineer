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
- Transfered class Dna, A_Dna, A_Dna_BasePseudoAtoms, B_Dna, B_Dna_BasePseudoAtoms, 
Z_Dna abd Z_Dna_BasePseudoAtoms from Will Ware's DNAGenerator.py.
- Added accessor methods getBaseSpacing/setBaseSpacing

"""


from math           import atan2, sin, cos, pi
from platform       import find_plugin_dir
from files_mmp      import _readmmp
from VQT            import A, V, dot, vlen
from chem           import Atom
from bonds          import inferBonds, bond_atoms
from fusechunksMode import fusechunksBase
from HistoryWidget  import orangemsg

import sys, os, env, re, random

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
numberPattern = re.compile(r"^\s*(\d+)\s*$")

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

END1 = '[' # these must be single characters, not used for base letters. 
END2 = ']'

DEBUG = False
DEBUG_SEQUENCE  =  False

class Dna:

    def getBaseSpacing( self ):
        return float( self.BASE_SPACING )
    
    def setBaseSpacing( self, inBaseSpacing ):
        self.BASE_SPACING  =  inBaseSpacing

    def make(self, assy, grp, sequence, doubleStrand, basesPerTurn, position,
             basenameA={'C': 'cytosine',
                        'G': 'guanine',
                        'A': 'adenine',
                        'T': 'thymine',
                        'N': 'unknown',
                        END1: 'end1',
                        END2: 'end2'},
             basenameB={'G': 'cytosine',
                        'C': 'guanine',
                        'T': 'adenine',
                        'A': 'thymine',
                        'N': 'unknown',
                        END1: 'end1',
                        END2: 'end2'}):
        baseList = [ ]
        if DEBUG_SEQUENCE:
            print "making", sequence
        def insertmmp(filename, subgroup, tfm, position=position):
            try:
                grouplist  = _readmmp(assy, filename, isInsert=True)
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

        def rotateTranslate(v, theta, z):
            c, s = cos(theta), sin(theta)
            x = c * v[0] + s * v[1]
            y = -s * v[0] + c * v[1]
            return V(x, y, v[2] + z)

        # Calculate the twist per base in radians
        twistPerBase = (self.handedness * 2 * pi) / basesPerTurn
        
        if doubleStrand:
            subgroup = Group("strand 1", grp.assy, None)
            grp.addchild(subgroup)
        else:
            subgroup = grp
        subgroup.open = False

        if (sequence.isdigit()):
            baseCount = int(sequence)
            sequence = baseCount * "N"
        sequence = self.addEndCaps(sequence)
        theta = 0.0
        z = 0.5 * self.BASE_SPACING * (len(sequence) - 1)
        for i in range(len(sequence)):
            basefile, zoffset, thetaOffset = \
                      self.strandAinfo(basenameA[sequence[i]], i)
            def tfm(v, theta=theta+thetaOffset, z1=z+zoffset):
                return rotateTranslate(v, theta, z1)
            if DEBUG: print basefile
            insertmmp(basefile, subgroup, tfm)
            theta -= twistPerBase
            z -= self.BASE_SPACING
        
        if doubleStrand:
            subgroup = Group("strand 2", grp.assy, None)
            subgroup.open = False
            grp.addchild(subgroup)
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
                if DEBUG: print basefile
                insertmmp(basefile, subgroup, tfm)
                theta -= twistPerBase
                z -= self.BASE_SPACING

        # fuse the bases together into continuous strands
        fcb = fusechunksBase()
        fcb.tol = 1.5
        for i in range(len(baseList) - 1):
            fcb.find_bondable_pairs([baseList[i]], [baseList[i+1]])
            fcb.make_bonds(assy)
        
        from debug import print_compact_traceback
        try:
            self.postprocess(baseList)
        except:
            if env.debug():
                print_compact_traceback("debug: exception in %r.postprocess(baseList = %r) (reraising): " % (self, baseList,))
            raise
        return

    def addEndCaps(self, sequence):
        return sequence

    def postprocess(self, baseList):
        return
    pass

class A_Dna(Dna):
    """The geometry for A-DNA is very twisty and funky. I'd probably need to
    take a few days to research it. It's not a simple helix (like B) or an
    alternating helix (like Z).
    """
    geometry = "A-DNA"
    BASE_SPACING = 0    # WRONG
    handedness = -1     # right-handed
    
    def strandAinfo(self, sequence, i):
        raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");
    def strandBinfo(self, sequence, i):
        raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");

class A_Dna_BasePseudoAtoms(A_Dna):
    pass

class B_Dna(Dna):
    geometry = "B-DNA"
    BASE_SPACING = 3.391    # angstroms
    handedness = -1         # right-handed

    def baseFileName(self, basename):
        return os.path.join(basepath, 'bdna-bases', '%s.mmp' % basename)

    def strandAinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 0.0
        basefile = self.baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 210 * (pi / 180)
        basefile = self.baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

class B_Dna_BasePseudoAtoms(B_Dna):
    BASE_SPACING = 3.18 # angstroms
    handedness = -1     # right-handed
    
    def baseFileName(self, basename):
        return os.path.join(basepath, 'bdna-pseudo-bases', '%s.mmp' % basename)
    def addEndCaps(self, sequence):
        if (len(sequence) > 1):
            return END1 + sequence[1:-1] + END2 #bruce 070518 replaced end-codes 'Y' and 'Z' with END1 and END2
        return sequence
    def postprocess(self, baseList): # bruce 070414
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
    geometry = "Z-DNA"
    BASE_SPACING = 3.715    # in angstroms
    handedness = 1          # left-handed

    def baseFileName(self, basename, suffix):
        return os.path.join(basepath, 'zdna-bases', '%s-%s.mmp' % (basename, suffix))

    def strandAinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'outer'
            zoffset = 2.045
        else:
            suffix = 'inner'
            zoffset = 0.0
        thetaOffset = 0.0
        basefile = self.baseFileName(basename, suffix)
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'inner'
            zoffset = -0.055
        else:
            suffix = 'outer'
            zoffset = -2.1
        thetaOffset = 0.5 * pi
        basefile = self.baseFileName(basename, suffix)
        return (basefile, zoffset, thetaOffset)

class Z_Dna_BasePseudoAtoms(Z_Dna):
    def baseFileName(self, basename, suffix):
        return os.path.join(basepath, 'zdna-pseudo-bases', '%s-%s.mmp' % (basename, suffix))
