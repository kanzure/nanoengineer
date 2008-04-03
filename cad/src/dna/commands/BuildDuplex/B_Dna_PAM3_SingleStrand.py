# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
B_Dna_PAM3_SingleStrand allows resizing a single strand of a DNA. 
See self.modify(). Note that self.make() to create a DnaStrnad from scratch 
is not implemented as of 2008-04-02.

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created on 2008-04-02

TODO as of 2008-04-02
- add more documentation. may undergo major refactoring/renaming changes.
- post FNANO allow resizing of a single strand such that: if axis atoms 
on original dna match with the ones on the newly created single stranded dna,
delete those atoms and fuse the bare strand with existing atoms
- May be revise the dna creation process thoughout. Example, see how to generate
 positions of strand-axis atoms without using the old way of inserting bases from
 mmp and performing transforms on them.
- move this file to dna/model
"""

from dna.commands.BuildDuplex.DnaDuplex import B_Dna_PAM3

from geometry.VQT import Q, norm, vlen, cross
from Numeric import dot


class B_Dna_PAM3_SingleStrand(B_Dna_PAM3):
    """
    B_Dna_PAM3_SingleStrand allows resizing a single strand of a DNA. 
    See self.modify(). Note that self.make() to create a DnaStrnad from scratch 
    is not implemented as of 2008-04-02.
    @see: superclass  B_Dna_PAM3 for more documentation,
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

        original_ladder = self._resizeEndAxisAtom.molecule.ladder
        original_ladder_end = original_ladder.get_ladder_end(self._resizeEndAxisAtom)
    
        rail_for_strandA_of_original_duplex = self._resizeEndStrand1Atom.molecule.get_ladder_rail()      
        
        rail_bond_direction_of_strandA_of_original_duplex = rail_for_strandA_of_original_duplex.bond_direction()

        b = norm(end2 - end1)
        new_ladder =   self.axis_atom_end1.molecule.ladder
        new_ladder_end = new_ladder.get_ladder_end(self.axis_atom_end1)

        chunkListForRotation = new_ladder.all_chunks()

        endBaseAtomList  = new_ladder.get_endBaseAtoms_containing_atom(self.axis_atom_end1)
        
        endStrandbaseAtoms = (endBaseAtomList[0], endBaseAtomList[2])   
        
        self.strandA_atom_end1 = None
        #TODO: REVIEW / REFACTOR THIS and DOC 
        DEBUG_BOND_DIRECTION_ADJUSTMENT = True
        
        if DEBUG_BOND_DIRECTION_ADJUSTMENT:
            for atm in endStrandbaseAtoms:
                if atm is not None:  
                    ##rail = atm.molecule.get_ladder_rail()
                    ##bond_direction = rail.bond_direction()
                    self.strandA_atom_end1 = atm
                    
                    self._set_bond_direction_on_new_strand(atm)
                    ##strand_bond = None
                    ##for bnd in atm.bonds:
                        ##if bnd.is_directional():
                            ##strand_bond = bnd 
                            ##break
                    ##if strand_bond: 
                        ##orig_dnaStrand = self._resizeEndStrand1Atom.molecule.parent_node_of_class(self.assy.DnaStrand)
                        ##new_dnaStrand = atm.molecule.parent_node_of_class(self.assy.DnaStrand)
                        
                        ##five_prime_orig, three_prime_orig = orig_dnaStrand.get_strand_end_base_atoms()
                        ##five_prime_new, three_prime_new = new_dnaStrand.get_strand_end_base_atoms()
                        
                        ##if self._resizeEndStrand1Atom is five_prime_orig:                            
                            ##strand_bond.set_bond_direction_from(atm, 
                                                                ##+1, 
                                                                ##propogate = True)
                        ##elif self._resizeEndStrand1Atom is three_prime_orig:
                            ##strand_bond.set_bond_direction_from(atm, 
                                                                ##- 1, 
                                                                ##propogate = True)

        axis_strand_vector = (self.strandA_atom_end1.posn() - \
                              self.axis_atom_end1.posn())


        vectorAlongLadderStep =  self._resizeEndStrand1Atom.posn() - \
                              self._resizeEndAxisAtom.posn()

        unitVectorAlongLadderStep = norm(vectorAlongLadderStep)

        self.final_pos_strand_end_atom = \
            self.axis_atom_end1.posn() + \
            vlen(axis_strand_vector)*unitVectorAlongLadderStep

        expected_vec = self.final_pos_strand_end_atom - self.axis_atom_end1.posn()
        
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
        @see: self._remove_bases_from_duplex() where this is called. 
        @see: B_Dna_PAM3._strand_neighbors_to_delete() -- overridden here
        
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
        
            
    def _set_bond_direction_on_new_strand(self, strandEndAtom_of_new_strand):
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
            
            orig_dnaStrand = mol.parent_node_of_class(
                self.assy.DnaStrand)
            
            new_dnaStrand = atm.molecule.parent_node_of_class(
                self.assy.DnaStrand)
            
            five_prime_orig, three_prime_orig = \
                           orig_dnaStrand.get_strand_end_base_atoms()
            
            five_prime_new, three_prime_new = \
                          new_dnaStrand.get_strand_end_base_atoms()
            
            if self._resizeEndStrand1Atom is five_prime_orig:     
                #+1 indicates the absolute bond direction i.e. from 5' to 3' end
                strand_bond.set_bond_direction_from(atm, +1, propogate = True)
            elif self._resizeEndStrand1Atom is three_prime_orig:
                strand_bond.set_bond_direction_from(atm, - 1, propogate = True)
            
        
    def _fuse_new_dna_with_original_duplex(self, 
                                           new_endBaseAtomList,
                                           endBaseAtomList):
        """
        Fuse the new dna strand (and axxis) end atom to the original dna 
        
        TODO: 
         - method needs to be renamed The original dna may be a single stranded
        dna or a duplex. Until 2008-04-02 ,it was possible to create or modify
        only a duplex and thats why the name 'duplex'
        -  Refactor further. May be use superclass method with some mods. 
        
        @see: self.modify()
        @see: B_Dna_PAM3._fuse_new_dna_with_original_duplex()
        """        
        #FUSE new dna strand with the original duplex
        chunkList1 = \
                   [ new_endBaseAtomList[0].molecule, 
                     self._resizeEndStrand1Atom.molecule]

        chunkList2 = \
                   [ new_endBaseAtomList[1].molecule,
                      self._resizeEndAxisAtom.molecule]

        ##chunkList3 = \
                   ##[new_endBaseAtomList[2].molecule,
                    ##endBaseAtomList[2].molecule]
        
        #Set the chunk color and chunk display of the new duplex such that
        #it matches with the original duplex chunk color and display
        #Actually, fusing the chunks should have taken care of this, but 
        #for some unknown reasons, its not happening. May be because 
        #chunks are not 'merged'?  ... Setting display and color for new 
        #duplex chunk is explicitely done below. Fixes bug 2711            
        for chunkPair in (chunkList1, chunkList2):##, chunkList3):
            display = chunkPair[1].display
            color   = chunkPair[1].color
            chunkPair[0].setDisplay(display)
            if color:
                chunkPair[0].setcolor(color)
   
        self.fuseBasePairChunks(chunkList1)
        self.fuseBasePairChunks(chunkList2, fuseTolerance = 3.0)
        ##self.fuseBasePairChunks(chunkList3)


