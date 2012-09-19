# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
DnaDuplex.py -- DNA duplex generator helper classes, based on empirical data.

@author: Mark Sims
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2007-10-18:
- Created. Major rewrite of DnaGenHelper.py.
"""

import foundation.env as env
from utilities.debug import print_compact_stack
from platform_dependent.PlatformDependent import find_plugin_dir
from geometry.VQT import Q, cross, vlen
from utilities.Log      import orangemsg
from utilities.exception_classes import PluginBug
from simulation.sim_commandruns import adjustSinglet
from model.elements import PeriodicTable

Element_Ae3 = PeriodicTable.getElement('Ae3')
basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

RIGHT_HANDED = -1
LEFT_HANDED  =  1

from geometry.VQT import norm
from Numeric import dot
from dna.generators.B_Dna_Generator import B_Dna_Generator

class B_Dna_PAM3_Generator(B_Dna_Generator):
    """
    Provides a PAM3 reduced model of the B form of DNA.
    """
    model = "PAM3"

    strandA_atom_end1 = None

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

        if len(baseList) < 1:
            print_compact_stack("bug? (ignoring) DnaDuplex._postProcess called but "\
                                "baseList is empty. Maybe dna_updater was "\
                                "run?: ")
            return

        start_basepair_atoms = baseList[0].atoms.values()
        end_basepair_atoms = baseList[-1].atoms.values()

        Ax_caps = filter( lambda atom: atom.element.symbol in ('Ax3'),
                          start_basepair_atoms)
        Ax_caps += filter( lambda atom: atom.element.symbol in ('Ax3'),
                           end_basepair_atoms)

        # Transmute Ax3 caps to Ae3 atoms.
        # Note: this leaves two "killed singlets" hanging around,
        #       one from each Ax3 cap.
        #
        # REVIEW: is it safe to simply not do this when dna_updater_is_enabled()?
        # [bruce 080320 question]
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
                if atm.element.symbol == 'Ss3' and atm.getDnaBaseName() == 'a':
                    self.strandA_atom_end1 = atm

    def _orient_for_modify(self, end1, end2):
        """
        Orient the new dna to match up appropriately with the original dna
        (being modified/resized)
        """

        b = norm(end2 - end1)
        new_ladder =   self.axis_atom_end1.molecule.ladder
        new_ladder_end = new_ladder.get_ladder_end(self.axis_atom_end1)

        chunkListForRotation = new_ladder.all_chunks()

        #This method fixes bug 2889. See that method for more comments.
        self._redetermine_resizeEndStrand1Atom_and_strandA_atom_end1()

        axis_strand_vector = (self.strandA_atom_end1.posn() - \
                              self.axis_atom_end1.posn())


        vectorAlongLadderStep =  self._resizeEndStrand1Atom.posn() - \
                              self._resizeEndAxisAtom.posn()

        unitVectorAlongLadderStep = norm(vectorAlongLadderStep)

        self.final_pos_strand_end_atom = \
            self.axis_atom_end1.posn() + \
            vlen(axis_strand_vector)*unitVectorAlongLadderStep


        q_new = Q(axis_strand_vector, vectorAlongLadderStep)

        if dot(axis_strand_vector, cross(vectorAlongLadderStep, b)) < 0:
            q_new2 = Q(b, -q_new.angle)
        else:
            q_new2 = Q(b, q_new.angle)


        self.assy.rotateSpecifiedMovables(q_new2, chunkListForRotation, end1)


    def _redetermine_resizeEndStrand1Atom_and_strandA_atom_end1(self):
        """
        @ATTENTION: The strandA endatom at end1 is modified in this method.
        It is originally computed in self._determine_axis_and_strandA_endAtoms()

        The recomputation is done to fix bug 2889 (for v1.1.0).
        See B_Dna_PAM3_Generator.orient_for_modify() for details.
        This NEEDS CLEANUP
        @see: self._create_raw_duplex()
        @see: self.orient_for_modify()
        """
        #Method created just before codefreeze for v1.1.0 to fix newly discovered
        #bug 2889 -- Ninad 2008-06-02
        #Perhaps computing this strand atom  always be done at a later
        #stage (like done in here). But not sure if this will cause any bugs.
        #So not changing the original implementation .


        new_ladder =   self.axis_atom_end1.molecule.ladder
        endBaseAtomList  = new_ladder.get_endBaseAtoms_containing_atom(self.axis_atom_end1)

        endStrandbaseAtoms = (endBaseAtomList[0], endBaseAtomList[2])

        self.strandA_atom_end1 = None

        #Check if the resizeEndStrandAtom is a 5' or a 3' end.
        #If it is a 5' or 3' end, then chose the strand end atom of the
        #new duplex such that it is the opposite of it (i.e. if resizeEndStrandAtom
        #is a 5' end, the strand end atom on new duplex should be chosen such that
        #its a 3' end. Using these references, we will orient the new duplex
        #to match up correctly with the resizeEnd strand atom (and later
        #the old and new dnas will be bonded at these ends)

        #However, if the chosen resizeEndStrandAtom of original duplex
        #doesn't have a 5' or 3' end, then we will choose the second
        #resizeEndStrandEndAtom on the original duplex and do the same
        #computations
        resizeEndStrandAtom_isFivePrimeEndAtom = False
        resizeEndStrandAtom_isThreePrimeEndAtom = False
        if self._resizeEndStrand1Atom.isFivePrimeEndAtom():
            resizeEndStrandAtom_isFivePrimeEndAtom = True
        elif self._resizeEndStrand1Atom.isThreePrimeEndAtom():
            resizeEndStrandAtom_isThreePrimeEndAtom = True

        if not (resizeEndStrandAtom_isFivePrimeEndAtom or \
                resizeEndStrandAtom_isThreePrimeEndAtom):
            if self._resizeEndStrand2Atom:
                if self._resizeEndStrand2Atom.isFivePrimeEndAtom():
                    resizeEndStrandAtom_isFivePrimeEndAtom = True
                elif self._resizeEndStrand2Atom.isThreePrimeEndAtom():
                    resizeEndStrandAtom_isThreePrimeEndAtom = True

                if (resizeEndStrandAtom_isFivePrimeEndAtom or \
                    resizeEndStrandAtom_isThreePrimeEndAtom):
                    #Swap resizeEndStrand1Atom and resizeEndStrand2Atom
                    atm1, atm2 = self._resizeEndStrand1Atom, self._resizeEndStrand2Atom
                    self._resizeEndStrand1Atom, self._resizeEndStrand2Atom = atm2, atm1


        for atm in endStrandbaseAtoms:
            if atm is not None:
                if atm.isThreePrimeEndAtom() and \
                   resizeEndStrandAtom_isFivePrimeEndAtom:
                    self.strandA_atom_end1 = atm
                    break
                elif atm.isFivePrimeEndAtom() and \
                     resizeEndStrandAtom_isThreePrimeEndAtom:
                    self.strandA_atom_end1 = atm
                    break

        if self.strandA_atom_end1 is None:
            #As a fallback, set this atom to any atom in endStrandbaseAtoms
            #but, this may cause a bug in which bond directions are not
            #properly set.
            for atm in endStrandbaseAtoms:
                if atm is not None:
                    self.strandA_atom_end1 = atm




    def _orient_to_position_first_strandA_base_in_axis_plane(self, baseList, end1, end2):
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


        self.assy.rotateSpecifiedMovables(q_new2, baseList, end1)

    def _strand_neighbors_to_delete(self, axisAtom):
        """
        Returns a list of strand neighbors of the given axis atom to delete
        from the original dna being resized (and resizing will result in
        removing bases/ basepairs from the dna). This method determines
        whether both the strand neigbors of this axisAtom need to be deleted
        or is it just a single strand neighbor on a specific Dna ladder
        needs to be deleted. The latter is the case while resizing a
        single strand of a Dna.
        @see: self._remove_bases_from_dna() where this is called.
        @see: Dna._strand_neighbors_to_delete() -- overridden here
        @see: B_Dna_PAM3_Generator_SingleStrand._strand_neighbors_to_delete() which
              overrides this method
        """
        strand_neighbors_to_delete = axisAtom.strand_neighbors()
        return strand_neighbors_to_delete


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
                        msg = "Ss3 atom not assigned to strand 'a' or 'b'."
                        raise PluginBug(msg)
                elif atom.element.symbol in ('Ax3', 'Ae3'):
                    _axis_list.append(atom)

        return (_strandA_list, _strandB_list, _axis_list)