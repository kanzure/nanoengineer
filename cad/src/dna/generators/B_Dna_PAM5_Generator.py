# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
DnaDuplex.py -- DNA duplex generator helper classes, based on empirical data.

@author: Mark Sims
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2007-10-18:
- Created. Major rewrite of DnaGenHelper.py.
"""

import foundation.env as env
import os

from math    import sin, cos, pi
from utilities.debug import print_compact_traceback, print_compact_stack
from platform_dependent.PlatformDependent import find_plugin_dir
from files.mmp.files_mmp import readmmp
from geometry.VQT import Q, V, angleBetween, cross, vlen
from utilities.Log      import orangemsg
from utilities.exception_classes import PluginBug
from utilities.constants import gensym
from utilities.prefs_constants import dnaDefaultStrand1Color_prefs_key
from utilities.prefs_constants import dnaDefaultStrand2Color_prefs_key
from utilities.prefs_constants import dnaDefaultSegmentColor_prefs_key

from dna.model.Dna_Constants import getDuplexBasesPerTurn

##from dna.updater.dna_updater_prefs import pref_dna_updater_convert_to_PAM3plus5

from simulation.sim_commandruns import adjustSinglet
from model.elements import PeriodicTable
from model.Line import Line

from model.chem import Atom_prekill_prep
Element_Ae3 = PeriodicTable.getElement('Ae3')

from dna.model.Dna_Constants import basesDict, dnaDict
from dna.model.dna_model_constants import LADDER_END0

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

RIGHT_HANDED = -1
LEFT_HANDED  =  1


from geometry.VQT import V, Q, norm, cross
from geometry.VQT import  vlen
from Numeric import dot

from utilities.debug import print_compact_stack
from model.bonds import bond_at_singlets
from dna.generators.B_Dna_Generator import B_Dna_Generator

class B_Dna_PAM5_Generator(B_Dna_Generator):
    """
    Provides a PAM5 reduced model of the B form of DNA.
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
                    if atom.getDnaStrandId_for_generators() == 'Strand1':
                        _strandA_list.append(atom)
                        # Following makes sure that the info record
                        #'dnaStrandId_for_generators' won't be written for
                        #this atom that the dna generator outputs. i.e.
                        #the info record 'dnaStrandId_for_generators' is only
                        #required while generating the dna from scratch
                        #(by reading in the strand base files in 'cad/plugins'
                        #see more comments in Atom.getDnaStrandId_for_generators
                        atom.setDnaStrandId_for_generators('')
                    elif atom.getDnaStrandId_for_generators() == 'Strand2':
                        atom.setDnaStrandId_for_generators('')
                        _strandB_list.append(atom)
                if atom.element.symbol in ('Ss5', 'Sh5'):
                    if atom.getDnaBaseName() == 'a':
                        _strandA_list.append(atom)
                        #Now reset the DnaBaseName for the added atom
                        # to 'unassigned' base i.e. 'X'
                        atom.setDnaBaseName('X')
                    elif atom.getDnaBaseName() == 'b':
                        _strandB_list.append(atom)
                        #Now reset the DnaBaseName for the added atom
                        # to 'unassigned' base i.e. 'X'
                        atom.setDnaBaseName('X')
                    else:
                        msg = "Ss5 or Sh5 atom not assigned to strand 'a' or 'b'."
                        raise PluginBug(msg)
                elif atom.element.symbol in ('Ax5', 'Ae5', 'Gv5', 'Gr5'):
                    _axis_list.append(atom)

        return (_strandA_list, _strandB_list, _axis_list)




