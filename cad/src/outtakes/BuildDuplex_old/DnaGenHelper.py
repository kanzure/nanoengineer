# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
DnaGenHelper.py -- DNA generator helper classes, based on empirical data.

WARNING: this file has been mostly superseded by DnaDuplex.py.
It is used only in DnaGenerator.py, also superseded.

@author: Will Ware
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

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

Mark 2007-10-18:
- Did a major rewrite of this module, superseding it --
  DnaDuplex.py.

Bruce 2008-1-1:
- renamed this from Dna.py to DnaGenHelper.py so it's
  not in a way of a proposed "dna" package.
"""

# To do:
#
# 1) Atomistic and PAM5 generated models should have exact orientation
# (i.e. rotational origin).

import foundation.env as env
import os
import re

from math    import sin, cos, pi

from utilities.debug import print_compact_traceback

from platform_dependent.PlatformDependent import find_plugin_dir
from files.mmp.files_mmp import readmmp
from geometry.VQT import V
from commands.Fuse.fusechunksMode import fusechunksBase
from utilities.Log import orangemsg
from utilities.exception_classes import PluginBug

from dna.model.Dna_Constants import basesDict, dnaDict

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
numberPattern = re.compile(r"^\s*(\d+)\s*$")

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

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

    @ivar model: The model representation, where:
                          - "Atomistic" = atomistic model
                          - "PAM5" = PAM5 reduced model.
    @type model: str

    @ivar sequence: The sequence (of strand A of the duplex).
    @type sequence: str
    """

    def make(self, group, inSequence, basesPerTurn, position = V(0, 0, 0)):
        """
        Makes a DNA duplex with the sequence I{inSequence}.
        The duplex is oriented with its central axis coincident
        to the Z axis.

        @param assy: The assembly (part).
        @type  assy: L{assembly}

        @param group: The group node object containing the DNA. The caller
                      is responsible for creating an empty group and passing
                      it here. When finished, this group will contain the DNA
                      model.
        @type  group: L{Group}

        @param basesPerTurn: The number of bases per helical turn.
        @type  basesPerTurn: float

        @param position: The position in 3d model space at which to create
                         the DNA strand. This should always be 0, 0, 0.
        @type position:  position
        """

        self.sequence  =  inSequence
        assy           =  group.assy
        baseList       =  []

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
                ok, grouplist = readmmp(assy, filename, isInsert = True)
            except IOError:
                raise PluginBug("Cannot read file: " + filename)
            if not grouplist:
                raise PluginBug("No atoms in DNA base? " + filename)

            viewdata, mainpart, shelf = grouplist

            for member in mainpart.members:
                # 'member' is a chunk containing a set of base-pair atoms.
                for atm in member.atoms.values():
                    atm._posn = tfm(atm._posn) + position
                    if atm.element.symbol in ('Se3', 'Ss3', 'Ss5'):
                        if atm.getDnaBaseName() == "a":
                            baseLetter = currentBaseLetter
                        else:
                            try:
                                baseLetter = \
                                    basesDict[currentBaseLetter]['Complement']
                            except:
                                # If complement not found, just assign same
                                # letter.
                                baseLetter = currentBaseLetter
                        if 0:
                            print "Ss(%r) being set to %r." \
                                  % (atm.getDnaBaseName(), baseLetter)
                        atm.setDnaBaseName(baseLetter)

                member.name = currentBaseLetter
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

        # Begin making DNA.
        subgroup = group
        subgroup.open = False

        # Calculate the twist per base in radians.
        twistPerBase = (self.handedness * 2 * pi) / basesPerTurn
        theta        = 0.0
        z            = 0.5 * self.baseRise * (len(self.sequence) - 1)

        # Create PAM5 or PAM3 duplex.
        for i in range(len(self.sequence)):
            currentBaseLetter = self.sequence[i]
            basefile, zoffset, thetaOffset = \
                self._strandAinfo(currentBaseLetter, i)
            def tfm(v, theta = theta + thetaOffset, z1 = z + zoffset):
                return rotateTranslateXYZ(v, theta, z1)

            insertBaseFromMmp(basefile, subgroup, tfm)

            theta -= twistPerBase
            z     -= self.baseRise

        # Fuse the base chunks together into continuous strands.
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

    def _strandAinfo(self, baseLetter, index):
        """
        Raise exception since A-DNA is not support.
        """
        raise PluginBug("A-DNA is not yet implemented.")

    def _strandBinfo(self, sequence, index):
        """
        Raise exception since A-DNA is not support.
        """
        raise PluginBug("A-DNA is not yet implemented.")
    pass

class A_Dna_Atomistic(A_Dna):
    """
    Provides an atomistic model of the A form of DNA.

    @attention: This class is not implemented yet.
    """
    pass

class A_Dna_PAM5(A_Dna):
    """
    Provides a PAM5 reduced model of the B form of DNA.

    @attention: This class is not implemented yet.
    """
    pass

class B_Dna(Dna):
    """
    Provides an atomistic model of the B form of DNA.
    """
    form       =  "B-DNA"
    baseRise   =  dnaDict['B-DNA']['DuplexRise']
    handedness =  RIGHT_HANDED
    pass

class B_Dna_Atomistic(B_Dna):
    """
    Provides an atomistic model of the B form of DNA.
    """
    model      =  "Atomistic"

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

    pass

class B_Dna_PAM5(B_Dna):
    """
    Provides a PAM5 reduced model of the B form of DNA.
    """
    model      =  "PAM5"

    def _isStartPosition(self, index):
        """
        Returns True if I{index} points the first base position (5') of
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
        Returns True if I{index} points the last base position (3') of self's
        sequence.

        @param index: Index in base sequence.
        @type  index: int

        @return: True if index is zero.
        @rtype : bool
        """
        if index ==  len(self.sequence) - 1:
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

        if len(self.sequence) == 1:
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
    pass

class B_Dna_PAM3(B_Dna_PAM5):
    """
    Provides a PAM3 reduced model of the B form of DNA.
    """
    model      =  "PAM3"

    def _postProcess(self, baseList): # bruce 070414
        """
        Set bond direction on the backbone bonds.

        @param baseList: List of basepair chunks that make up the duplex.
        @type  baseList: list

        @note: baseList must contain at least two base-pair chunks.
        """
        # This implem depends on the specifics of how the end-representations
        # are terminated. If that's changed, it might stop working or it might
        # start giving wrong results. In the current representation,
        # baseList[0] (a chunk) is the starting end of the duplex. It has two
        # bonds whose directions we should set, which will determine the
        # directions of their strands: Se3 -> Ss3, and Sh3 <- Ss3.
        # Just find those bonds and set the strand directions.

        assert len(baseList) >= 2
        basepair1_atoms = baseList[0].atoms.values() # StartBasePair.MMP
        basepair2_atoms = baseList[1].atoms.values() # MiddleBasePair or EndBasePair.MMP
        Se3_list = filter( lambda atom: atom.element.symbol in ('Se3'), basepair1_atoms)
        Sh3_list = filter( lambda atom: atom.element.symbol in ('Sh3'), basepair1_atoms)
        # To set the direction of the Se3 -> Ss3 bond, we need the Ss3 atom
        # from the second base-pair (i.e. baseList[1]) that is connected to
        # the Se3 atom in the first base-pair.
        # Ss3_list will have only one Ss3 atom if the duplex is only two
        # base-pairs long. Otherwise, Ss3_list will have two Ss3 atoms.
        Ss3_list = filter( lambda atom: atom.element.symbol in ('Ss3'), basepair2_atoms)
        if len(Se3_list) == len(Sh3_list) == 1:
            for atom in Se3_list:
                assert len(atom.bonds) == 2
                # This is fragile since it is dependent on the bond order in the
                # PAM3 StartBasePair.MMP file. If the order gets changed in that
                # file, this will fail.
                # A more robust approach would be to check for the Se3 -> Ss3
                # bond, which is the one we want here. Mark 2007-09-27.
                #atom.bonds[1].set_bond_direction_from(atom, 1, propogate = True)
                # This implements the more robust stategy mentioned
                # above. I'd like Bruce to review it and confirm it is good.
                # Mark 2007-09-27.
                #atom.bonds[1].set_bond_direction_from(Ss3_list[0], -1, propogate = True)
                try: # Try the first Ss3 atom in Ss3_list.
                    atom.bonds[1].set_bond_direction_from(Ss3_list[0], -1, propogate = True)
                except: # That wasn't it, so it must be the second Ss3 atom.
                    atom.bonds[1].set_bond_direction_from(Ss3_list[1], -1, propogate = True)
            for atom in Sh3_list:
                assert len(atom.bonds) == 1
                atom.bonds[0].set_bond_direction_from(atom, -1, propogate = True)
        else:
            #bruce 070604 mitigate bug in above code when number of bases == 1
            # by not raising an exception when it fails.
            msg = "Warning: strand not terminated, bond direction not set \
            (too short)"
            env.history.message( orangemsg( msg))
        return

class Z_Dna(Dna):
    """
    Provides an atomistic model of the Z form of DNA.
    """

    form       =  "Z-DNA"
    baseRise   =  dnaDict['Z-DNA']['DuplexRise']
    handedness =  LEFT_HANDED

class Z_Dna_PAM5(Z_Dna):
    """
    Provides an atomistic model of the Z form of DNA.

    @attention: This class is not implemented yet.
    """
    model      =  "Atomistic"

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
    Provides a PAM5 reduced model of the Z form of DNA.

    @attention: This class is not implemented yet.
    """
    pass

