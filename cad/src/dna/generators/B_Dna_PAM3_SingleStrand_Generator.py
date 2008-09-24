# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
B_Dna_PAM3_Generator_SingleStrand allows resizing a single strand of a DNA.
See self.modify(). Note that self.make() to create a DnaStrnad from scratch
is not implemented as of 2008-04-02.

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created on 2008-04-02

TODO as of 2008-04-07
- add more documentation. may undergo major refactoring/renaming changes.
- post FNANO allow resizing of a single strand such that: if axis atoms
on original dna match with the ones on the newly created single stranded dna,
delete those atoms and fuse the bare strand with existing atoms
- May be revise the dna creation process thoughout. Example, see how to generate
 positions of strand-axis atoms without using the old way of inserting bases from
 mmp and performing transforms on them.
- move this file to dna/model
- Methods such as the following need REVIEW post FNANO08 (not urgent). May be
 revise algorithm for optimization or supporting some features such as
 'extend and bond
 self._fuse_new_dna_with_original_duplex
 self._replace_overlapping_axisAtoms_of_new_dna

"""

from geometry.VQT import Q, norm, vlen, cross
from Numeric import dot
from utilities.debug import print_compact_stack
from model.bonds import bond_at_singlets

from dna.generators.B_Dna_PAM3_Generator import B_Dna_PAM3_Generator

class B_Dna_PAM3_SingleStrand_Generator(B_Dna_PAM3_Generator):
    """
    B_Dna_PAM3_SingleStrand_Generator allows resizing a single strand of a DNA.
    See self.modify(). Note that self.make() to create a DnaStrnad from scratch
    is not implemented as of 2008-04-02.
    @see: superclass  B_Dna_PAM3_Generator for more documentation,
    """
    def _strandAinfo(self, index):
        """
        Returns parameters needed to add the next base of the
        @param index: Base-pair index.
        @type  index: int
        """
        #unused param index. Just inheriting from the superclass..
        del index

        zoffset      =  0.0
        thetaOffset  =  0.0
        basename     =  "PAM3-SingleStrand/MiddleBasePair"
        basefile     =  self._baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

    def _orient_for_modify(self, end1, end2):
        """
        Do the final orientation of the newly generated dna, around its own
        axis so that the axis and strand atoms on this new dna are
        fusable with the resize end on the original dna.
        @param end1: end1 of new dna (segment) generated
        @param end2: end2 of new dna (segment) generated
        """

        b = norm(end2 - end1)
        new_ladder =   self.axis_atom_end1.molecule.ladder

        chunkListForRotation = new_ladder.all_chunks()

        endBaseAtomList  = new_ladder.get_endBaseAtoms_containing_atom(self.axis_atom_end1)

        endStrandbaseAtoms = (endBaseAtomList[0], endBaseAtomList[2])

        self.strandA_atom_end1 = None
        #TODO: REVIEW / REFACTOR THIS and DOC
        for atm in endStrandbaseAtoms:
            if atm is not None:
                self.strandA_atom_end1 = atm
                self._set_bond_direction_on_new_strand(atm)


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
        
        
    def _strand_neighbors_to_delete(self, axisAtom):
        """
        Returns a list of strand neighbors of the given axis atom to delete
        from the original dna being resized (and resizing will result in
        removing bases/ basepairs from the dna). This method determines
        whether both the strand neigbors of this axisAtom need to be deleted
        or is it just a single strand neighbor on a specific Dna Strand Group
        needs to be deleted. The latter is the case while resizing a
        single strand of a Dna. i.e. in this class, it will find a strand neighbor
        to the given axis atom on the strand being resized.
        @see: self._remove_bases_from_dna() where this is called.
        @see: B_Dna_PAM3_Generator._strand_neighbors_to_delete() -- overridden here

        """
        #Note that sicne we are resizing a single strand, the list this
        #method returns will have only one strand atom or will be empty if
        #strand atom on the strand being resized is not found.
        #

        strand_neighbors_to_delete = []

        strand_neighbors  = axisAtom.strand_neighbors()

        if self._resizeEndStrand1Atom:
            mol = self._resizeEndStrand1Atom.molecule
            resize_strand = mol.parent_node_of_class(self.assy.DnaStrand)
            for atm in strand_neighbors:
                strand = atm.molecule.parent_node_of_class(self.assy.DnaStrand)
                if strand is resize_strand:
                    strand_neighbors_to_delete = [atm]
                    break
        return strand_neighbors_to_delete


    def _set_bond_direction_on_new_strand(self,
                                          strandEndAtom_of_new_strand
                                          ):
        """
        Set the bond direction on the new strand. The bond direction will be set
        such that the new strand can be fused with the strand being resized
        Example: if the last strand atom of strand being resized is a 5' end atom,
        this method will make sure that the first strand end atom of the
        new strand we created is a 3' end.
        @param strandEndAtom_of_new_strand: The strand end base atom on the new
               strand. The bond direction will be set from this atom and will
               be propogated further along the strand atom chain this atom
               belongs to (of the new strand)
        @type strandEndAtom_of_new_strand: B{Atom}
        """
        atm = strandEndAtom_of_new_strand

        strand_bond = None
        for bnd in atm.bonds:
            if bnd.is_directional():
                strand_bond = bnd
                break
        if strand_bond:
            mol = self._resizeEndStrand1Atom.molecule

            orig_dnaStrand = mol.parent_node_of_class(self.assy.DnaStrand)

            five_prime_orig, three_prime_orig = \
                           orig_dnaStrand.get_strand_end_base_atoms()

            if self._resizeEndStrand1Atom is five_prime_orig:
                #+1 indicates the absolute bond direction i.e. from 5' to 3' end
                strand_bond.set_bond_direction_from(atm, +1, propogate = True)
            elif self._resizeEndStrand1Atom is three_prime_orig:
                strand_bond.set_bond_direction_from(atm, - 1, propogate = True)

    def _replace_overlapping_axisAtoms_of_new_dna(self, new_endBaseAtomList):
        """
        Checks if the new dna (which is a single strand in this class)
        has any axis atoms that overlap the axis atoms of the original dna.
        If it finds such atoms, the such overlapping atoms of the new dna are
        replaced with that on the original dna. Because of this operation, the
        strand atoms of the new dna are left without axis atoms. So, this method
        then calls appropriate method to create bonds between new strand atoms
        and corresponding axis atoms of the original dna.

        Also, the replacement operation could leave out some neighboring axis
        atoms of the *new dna* without bonds. So those need to be bonded with
        the axis atom of the original dna which replaced their neighbor.
        This is done by calling self._bond_axisNeighbors_with_orig_axisAtoms()

        @see self._fuse_new_dna_with_original_duplex() for  a detail example

        @see: self._bond_bare_strandAtoms_with_orig_axisAtoms()
        @see self._bond_axisNeighbors_with_orig_axisAtoms()

        @BUG: Bug or unsupported feature:
              If the axis atoms of the original dna have a broken bond in
              between, then the wholechain will stop at the broken bond
              and thus, overlapping axis atoms of new dna after that bond
              won't be removed --- in short, the extended strand won't be
              properly fused. We need to come up with well defined rules
              ..example -- when the strand should decide it needs to remove
              overlapping atoms? ...even when it is overlapping with a
              different dna? (not the one we are resizing ) etc.
        """
        #new dna generated by self.modify
        endAxisAtom_new_dna = new_endBaseAtomList[1]
        axis_wholechain_new_dna = endAxisAtom_new_dna.molecule.wholechain
        atomlist_with_overlapping_atoms = axis_wholechain_new_dna.get_all_baseatoms()

        #dna being resized (the original structure which is being resized)
        axis_wholechain_orig_dna = self._resizeEndAxisAtom.molecule.wholechain
        atomlist_to_keep = axis_wholechain_orig_dna.get_all_baseatoms()
        axisEndBaseAtoms_orig_dna = axis_wholechain_orig_dna.end_baseatoms()

        overlapping_atoms = \
                          self._find_overlapping_axisAtomPairs(atomlist_to_keep,
                                                               atomlist_with_overlapping_atoms)


        axis_and_strand_atomPairs_to_bond = []
        axis_and_axis_atomPairs_to_bond = []
        fusableAxisAtomPairsDict = {}

        for atm_to_keep, atm_to_delete in overlapping_atoms:
            #Make sure that atm_to_keep (the axis atom on original dna)
            #has only one strand neighbor, OTHERWISE , if we delete
            #the overlapping axis atoms on the new dna, the bare strand of
            #the new dna can not be bonded with the old dna axis! and we
            #will endup having a bare strand with no axis atom!
            #-Ninad 2008-04-04

            strand_neighbors_of_atm_to_keep = atm_to_keep.strand_neighbors()

            #Before deleting the overlapping axis atom of the new dna,
            #make sure that the corresponding old axis atom has only
            #one strand neighbor. Otherwise, there will be no axis atom
            #available for the bare strand atom that will result because
            #of this delete operation!
            if len(strand_neighbors_of_atm_to_keep) == 1 and atm_to_delete:
                #We know that the new dna is a single strand. So the
                #axis atom will ONLY have a single strand atom atatched.
                #If not, it will be a bug!
                strand_atom_new_dna = atm_to_delete.strand_neighbors()[0]

                #We will fuse this strand atom to the old axis atom
                axis_and_strand_atomPairs_to_bond.append((atm_to_keep,
                                                     strand_atom_new_dna))

                fusableAxisAtomPairsDict[atm_to_keep] = atm_to_delete
                ##fusableAxisAtomPairs.append((atm_to_keep, atm_to_delete))


        for atm_to_keep in axisEndBaseAtoms_orig_dna:
            #This means that we are at the end of the chain of the
            #original dna. There could be some more axis atoms on the
            #new dna that go beyond the original dna axis chain -- [A]
            #Thus, after we replace the overlapping axis atoms of the
            #new dna with the original axis atoms, we should make sure
            #to bond them with the atoms [A] mentioned above
            if fusableAxisAtomPairsDict.has_key(atm_to_keep):
                atm_to_delete = fusableAxisAtomPairsDict[atm_to_keep]
                for neighbor in atm_to_delete.axis_neighbors():
                    if neighbor is not None and \
                       neighbor not in fusableAxisAtomPairsDict.values():
                        axis_and_axis_atomPairs_to_bond.append((atm_to_keep,
                                                           neighbor))

        for atm_to_delete in fusableAxisAtomPairsDict.values():
            try:
                #Now delete the overlapping axis atom on new dna
                atm_to_delete.kill()
            except:
                print_compact_stack("Strand resizing: Error killing axis atom")

        if axis_and_strand_atomPairs_to_bond:
            self._bond_bare_strandAtoms_with_orig_axisAtoms(axis_and_strand_atomPairs_to_bond)

        if axis_and_axis_atomPairs_to_bond:
            self._bond_axisNeighbors_with_orig_axisAtoms(axis_and_axis_atomPairs_to_bond)

    def _bond_bare_strandAtoms_with_orig_axisAtoms(self,
                                                   axis_and_strand_atomPairs_to_bond):
        """
        Create bonds between the bare strand atoms of the new dna with the
        corresponding axis atoms of the original dna. This method should be
        called ONLY from self._replace_overlapping_axisAtoms_of_new_dna() where
        we remove the axis atoms of new dna that overlap the ones in old dna.
        We need to re-bond the bare strand atoms as a result of this replacment,
        with the axis atoms of the old dna.
        @param axis_and_strand_atomPairs_to_bond: A list containing pairs of the
               axis and strand atoms that will be bonded together. It is of the
               format [(atm1, atm2) , ....]
               Where,
               atm1 is always axisAtom of original dna
               atm2 is always bare strandAtom of new dna

        @type  axis_and_strand_atomPairs_to_bond: list
        @see: self._replace_overlapping_axisAtoms_of_new_dna() which calls this.
        """

        #@REVIEW/ TODO: Make sure that we are not bondingan axis atom with a
        #5' or 3' bondpoint of the strand atom.Skip the pair if its one and
        #the same atom (?) This may not be needed because of the other
        #code but is not obvious , so better to make sure in this method
        #-- Ninad 2008-04-11


        for atm1, atm2 in axis_and_strand_atomPairs_to_bond:
            #Skip the pair if its one and the same atom.
            if atm1 is not atm2:
                for s1 in atm1.singNeighbors():
                    if atm2.singNeighbors():
                        s2 = atm2.singNeighbors()[0]
                        bond_at_singlets(s1, s2, move = False)
                        #REVIEW 2008-04-10 if 'break' is needed -
                        break


        #Alternative-- Use find bondable pairs using class fuseChunksBase
        # Fuse the base-pair chunks together into continuous strands.
        #But this DOESN't WORK if bondpoints are disoriented or beyond the
        #tolerance limit. So its always better to bond atoms explicitely as done
        #above
        ##from commands.Fuse.fusechunksMode import fusechunksBase
        ##fcb = fusechunksBase()
        ##fcb.tol = 2.0
        ##fcb.find_bondable_pairs_in_given_atompairs(axis_and_strand_atomPairs_to_bond)
        ##fcb.make_bonds(self.assy)

    def _bond_axisNeighbors_with_orig_axisAtoms(self,
                                                axis_and_axis_atomPairs_to_bond
                                                ):
        """
        The operation that replaces the overlapping axis atoms of the new dnas
        with the corresponding axis atoms of the original dna could leave out
        some neighboring axis atoms of the *new dna* without bonds. So those
        need to be bonded with the axis atom of the original dna which replaced
        their neighbor. This method does that job.
        @param axis_and_axis_atomPairs_to_bond: A list containing pairs of the
               axis atom of original dna and axis atom on the new dna (which was
               a neighbor of the atom deleted in the replacement operation and
               was bonded to it) . Thies eatoms will be bonded with each other.
               It is of the format [(atm1, atm2) , ....]
               Where,
               atm1 is always axisAtom of original dna which replaced the
                     overlapping axis atom of new dna (and thereby broke
                     bond between that atom's axis neighbors )

               atm2 is always axis Atom of new dna , that was a neighbor to
                    an axis atom, say 'A', replaced by original dna axis atom
                    (because 'A' was overlapping) and was previously
                    bonded to 'A'.
        """
        for atm1, atm2 in axis_and_axis_atomPairs_to_bond:
            #Skip the pair if its one and the same atom.
            if atm1 is atm2:
                continue
            #the following check (atm1.singNeighbors()) < 1....)doesn't work in
            #some cases! So explicitly checking the length of the bondpoint
            #neighbors of the atom in the for loop afterwords.
            ##if len(atm1.singNeighbors()) < 1 or len(atm2.singNeighbors()) < 1:
                ##continue

            #Loop through bondpoints of atm1
            for s1 in atm1.singNeighbors():
                #bond point neigbors of atm2
                if atm2.singNeighbors():
                    s2 = atm2.singNeighbors()[0]
                    bond_at_singlets(s1, s2, move = False)
                    break

    def _fuse_new_dna_with_original_duplex(self,
                                           new_endBaseAtomList,
                                           endBaseAtomList):
        """
        First it fuses the end axis and strand atoms of the new dna with the
        corresponding end base atoms of the original dna.

        Then, it checks if the new dna (which is a single strand in this class)
        has any axis atoms that overlap the axis atoms of the original dna.
        If it finds such atoms, the such overlapping atoms of the new dna are
        replaced with that on the original dna. (This is done by calling
        self._replace_overlapping_axisAtoms_of_new_dna())


        EXAMPLE:

        Figure A:
        Figure A shows the original dna -- * denote the axis atoms
        and we will be resizing strand (2)

        (1) 3' <--<--<--<--<--<--<--<--<--<--<--<--< 5'
               |  |  |  |  |  |  |  |  |  |  |  |  |
        (A)    *--*--*--*--*--*--*--*--*--*--*--*--*
               |  |  |  |  |  |  |  |  |  |  |  |  |
        (2) 5' >-->-->-->-->-->3'

        Figure B:
        Lets assume that we extend strand (2) by 4 bases. So,
        the new dna that we will create in self.modify() is indicated by the
        strand (2) with symbols 'X' for strand base atoms and symbol 'o' for
        the axis base atoms. Clearly, the axis atoms 'o' overlap the axis atoms
        of the original dna. So we will remove those. As a result of this
        replacement, strand atoms 'X' will be without any axis atoms , so we
        will bond them with the original axis atoms '*'. The overall result is
        the original duplex's strand 2 gets extended by 4 bases and it still
        remains connected with the corresponding bases in strand (1) (the
        complementary strand )
        (1) 3' <--<--<--<--<--<--<--<--<--<--<--<--< 5'
               |  |  |  |  |  |  |  |  |  |  |  |  |
        (A)    *--*--*--*--*--*--o--o--o--o--*--*--*
               |  |  |  |  |  |  |  |  |  |  |  |  |
        (2) 5' >-->-->-->-->-->==X==X==X==X>

        @see self._replace_overlapping_axisAtoms_of_new_dna() for more details

        TODO:
         - method needs to be renamed The original dna may be a single stranded
        dna or a duplex. Until 2008-04-02 ,it was possible to create or modify
        only a duplex and thats why the name 'duplex'
        -  Refactor further. May be use superclass method with some mods.

        @see: self.modify()
        @see: B_Dna_PAM3_Generator._fuse_new_dna_with_original_duplex()


        """

        #FUSE new dna strand with the original duplex
        chunkList1 = \
                   [ new_endBaseAtomList[0].molecule,
                     self._resizeEndStrand1Atom.molecule]

        chunkList2 = \
                   [ new_endBaseAtomList[1].molecule,
                      self._resizeEndAxisAtom.molecule]


        #Set the chunk color and chunk display of the new duplex such that
        #it matches with the original duplex chunk color and display
        #Actually, fusing the chunks should have taken care of this, but
        #for some unknown reasons, its not happening. May be because
        #chunks are not 'merged'?  ... Setting display and color for new
        #duplex chunk is explicitely done below. Fixes bug 2711
        for chunkPair in (chunkList1, chunkList2):
            display = chunkPair[1].display
            color   = chunkPair[1].color
            chunkPair[0].setDisplayStyle(display)
            if color:
                chunkPair[0].setcolor(color)

            #Original implementation which relied on  on fuse chunks for finding
            #bondable atom pairs within a tolerance limit. This is no longer
            #used and can be removed after more testing of explicit bonding
            #done in self._bond_atoms_in_atomPairs() (called below)
            #-- Ninad 2008-04-11
            ##self.fuseBasePairChunks(chunkPair)

        endAtomPairsToBond = [ (new_endBaseAtomList[0],
                                self._resizeEndStrand1Atom),

                                (new_endBaseAtomList[1],
                                 self._resizeEndAxisAtom)]

        #Create explicit bonds between the end base atoms
        #(like done in self._bond_bare_strandAtoms_with_orig_axisAtoms())
        #instead of relying on fuse chunks (which relies on finding
        #bondable atom pairs within a tolerance limit. This fixes bug 2798
        self._bond_atoms_in_atomPairs(endAtomPairsToBond)
        
        

        #Make sure to call this AFTER the endatoms of new and
        #original DNAs are joined. Otherwise (if you replace the overlapping
        #atoms first), if the endAxisAtom of the new dna is an overlapping
        #atom, it will get deleted and in turn it will invalidate the
        #new_endBaseAtomList! (and thus, even the end strand atom won't
        #be fused with original dna end strand atom)
        self._replace_overlapping_axisAtoms_of_new_dna(new_endBaseAtomList)
        


    def _find_overlapping_axisAtomPairs(self,
                                         atomlist_to_keep,
                                         atomlist_with_overlapping_atoms,
                                         tolerance = 1.1
                                         ):
        """
        @param atomlist_to_keep: Atomlist which will be used as a reference atom
               list. The atoms in this list will be used to find the atoms
               in the *other list* which overlap atom positions in *this list*.
               Thus, the atoms in 'atomlist_to_keep' will be preserved (and thus
               won't be appended to self.overlapping_atoms)
        @type atomlist_to_keep: list
        @param atomlist_with_overlapping_atoms: This list will be checked with
               the first list (atom_list_to_keep) to find overlapping atoms.
               The atoms in this list that overlap with the atoms from the
               original list will be appended to self.overlapping_atoms
               (and will be eventually deleted)

        """

        overlapping_atoms_to_delete = []

        # Remember: chunk = a selected chunk  = atomlist to keep
        # mol = a non-selected -- to find overlapping atoms from


        # Loop through all the atoms in the selected chunk.
        # Use values() if the loop ever modifies chunk or mol--
        for a1 in atomlist_to_keep:
            # Singlets can't be overlapping atoms. SKIP those
            if a1.is_singlet():
                continue

            # Loop through all the atoms in atomlist_with_overlapping_atoms.
            for a2 in atomlist_with_overlapping_atoms:
                # Only atoms of the same type can be overlapping.
                # This also screens singlets, since a1 can't be a
                # singlet.
                if a1.element is not a2.element:
                    continue

                # Compares the distance between a1 and a2.
                # If the distance
                # is <= tol, then we have an overlapping atom.
                # I know this isn't a proper use of tol,
                # but it works for now.   Mark 050901
                if vlen (a1.posn() - a2.posn()) <= tolerance:
                    # Add this pair to the list--
                    overlapping_atoms_to_delete.append( (a1,a2) )
                    # No need to check other atoms in this chunk--
                    break

        return overlapping_atoms_to_delete

