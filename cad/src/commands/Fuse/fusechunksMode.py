# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
fusechunksMode.py - helpers for Fuse Chunks command and related functionality

NOTE: the only class defined herein is fusechunksBase, so this module
should be renamed.

@author: Mark
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.env as env
from geometry.VQT import vlen
from model.bonds import bond_at_singlets
from utilities.Log import orangemsg
from utilities.constants import diINVISIBLE

def fusechunks_lambda_tol_nbonds(tol, nbonds, mbonds, bondable_pairs):
    """
    Returns the bondable pairs tolerance string for the tolerance slider.
    """
    if nbonds < 0:
        nbonds_str = "?"
    else:
        nbonds_str = "%d" % (nbonds,)

    if mbonds < 0:
        mbonds_str = "?"
    elif mbonds == 0:
        mbonds_str = " "
    else:
        mbonds_str = "(%d  non-bondable) " % (mbonds,)

    tol_str = ("%d" % int(tol*100.0))[-3:]
    # fixed-width (3 digits) but using initial spaces
    # (doesn't have all of desired effect, due to non-fixed-width font)

    tol_str = "Tolerence:" + tol_str + "%"

#    return "%s => %s/%s bonds" % (tol_str,nbonds_str,mbonds_str)
#    return "%s => [%s bondable pairs] [%s bonds / %s multibonds] " % (tol_str,bondable_pairs,nbonds_str,mbonds_str)
    return "%s => %s bondable pairs %s" % (tol_str,bondable_pairs,mbonds_str)

def fusechunks_lambda_tol_natoms(tol, natoms):
    """
    Returns the overlapping atoms tolerance string for the tolerance slider.
    """
    if natoms < 0:
        natoms_str = "?"
    else:
        natoms_str = "%d" % (natoms,)

    tol_str = ("      %d" % int(tol*100.0))[-3:]
    # fixed-width (3 digits) but using initial spaces
    # (doesn't have all of desired effect, due to non-fixed-width font)
    tol_str = tol_str + "%"

    return "%s => %s overlapping atoms" % (tol_str, natoms_str)


class fusechunksBase:
    """
    Allows user to move chunks and fuse them to other chunks in the part.

    Two fuse methods are supported:
    1. Make Bonds - bondpoints between chunks will form bonds when they are near each other.
    2. Fuse Atoms - atoms between chunks will be fused when they overlap each other.
    """
    bondable_pairs = [] # List of bondable singlets
    ways_of_bonding = {} # Number of bonds each singlet found
    bondable_pairs_atoms = [] # List of atom pairs that can be bonded
    overlapping_atoms = [] # List of overlapping atoms

    tol = 1.0 # in Angstroms
        # For "Make Bonds", tol is the distance between two bondable singlets
        # For "Fuse Atoms", tol is the distance between two atoms to be considered overlapping

    def find_bondable_pairs(self,
                            chunk_list = None,
                            selmols_list = None,
                            ignore_chunk_picked_state = False
                            ):
        """
        Checks the bondpoints of the selected chunk to see if they are close enough
        to bond with any other bondpoints in a list of chunks.  Hidden chunks are skipped.

        @param ignore_chunk_picked_state: If True, this method treats selected
        or unselected chunks without any difference. i.e. it finds bondable
        pairs even for a chunk that is 'picked'
        """
        self.bondable_pairs = []
        self.ways_of_bonding = {}

        if not chunk_list:
            chunk_list = self.o.assy.molecules
        if not selmols_list:
            selmols_list = self.o.assy.selmols


        for chunk in selmols_list:
            if chunk.hidden or chunk.display == diINVISIBLE:
                # Skip selected chunk if hidden or invisible. Fixes bug 970. mark 060404
                continue

            # Loop through all the mols in the part to search for bondable pairs of singlets.
            # for mol in self.o.assy.molecules:
            for mol in chunk_list:
                if chunk is mol:
                    continue # Skip itself
                if mol.hidden or mol.display == diINVISIBLE:
                    continue # Skip hidden and invisible chunks.
                if mol.picked and not ignore_chunk_picked_state:
                    continue # Skip selected chunks

                # Skip this mol if its bounding box does not overlap the selected chunk's bbox.
                # Remember: chunk = a selected chunk, mol = a non-selected chunk.
                if not chunk.overlapping_chunk(mol, self.tol):
                    continue
                else:
                    # Loop through all the singlets in the selected chunk.
                    for s1 in chunk.singlets:
                        # We can skip mol if the singlet lies outside its bbox.
                        if not mol.overlapping_atom(s1, self.tol):
                            continue
                        # Loop through all the singlets in this chunk.
                        for s2 in mol.singlets:

                            # I substituted the line below in place of mergeable_singlets_Q_and_offset,
                            # which compares the distance between s1 and s2.  If the distance
                            # is <= tol, then we have a bondable pair of singlets.  I know this isn't
                            # a proper use of tol, but it works for now.   Mark 050327
                            if vlen (s1.posn() - s2.posn()) <= self.tol:

                            # ok, ideal, err = mergeable_singlets_Q_and_offset(s1, s2, offset2 = V(0,0,0), self.tol)
                            # if ok:
                            # we can ignore ideal and err, we know s1, s2 can bond at this tol

                                self.bondable_pairs.append( (s1,s2) ) # Add this pair to the list

                                # Now increment ways_of_bonding for each of the two singlets.
                                if s1.key in self.ways_of_bonding:
                                    self.ways_of_bonding[s1.key] += 1
                                else:
                                    self.ways_of_bonding[s1.key] = 1
                                if s2.key in self.ways_of_bonding:
                                    self.ways_of_bonding[s2.key] += 1
                                else:
                                    self.ways_of_bonding[s2.key] = 1

        # Update tolerance label and status bar msgs.
        nbonds = len(self.bondable_pairs)
        mbonds, singlets_not_bonded, singlet_pairs = self.multibonds()
        tol_str = fusechunks_lambda_tol_nbonds(self.tol, nbonds, mbonds, singlet_pairs)
        return tol_str

    def find_bondable_pairs_in_given_atompairs(self, atomPairs):
        """
        This is just a convience method that doesn't need chunk lists as an
        arguments.

        Finds the bondable pairs between the atom pairs provided in the
        atom pair list. The format is [(a1, a2), (a3, a4) ...].
        This method is only used internally (no direct user interation involved)
        It skips the checks such as atom's display while finding the bondable
        pairs..
        As of 2008-04-07 this method is not used.

        """
        self.bondable_pairs = []
        self.ways_of_bonding = {}

        for atm1, atm2 in atomPairs:
            #Skip the pair if its one and the same atom.
            if atm1 is atm2:
                continue
            #Loop through singlets (bondpoints) of atm1 (@see:Atom.singNeighbor)
            for s1 in atm1.singNeighbors():
                #Loop through the 'singlets' i.e. bond point neigbors of atm2
                for s2 in atm2.singNeighbors():
                    if vlen (s1.posn() - s2.posn()) <= self.tol:
                        # Add this pair to the list
                        self.bondable_pairs.append( (s1,s2) )
                        # Now increment ways_of_bonding for each of the two singlets.
                        if s1.key in self.ways_of_bonding:
                            self.ways_of_bonding[s1.key] += 1
                        else:
                            self.ways_of_bonding[s1.key] = 1
                        if s2.key in self.ways_of_bonding:
                            self.ways_of_bonding[s2.key] += 1
                        else:
                            self.ways_of_bonding[s2.key] = 1


    def make_bonds(self, assy = None):
        """
        Make bonds between all bondable pairs of singlets
        """
        self._make_bonds_1(assy)
        self._make_bonds_3()

    def _make_bonds_1(self, assy = None):
        """
        Make bonds -- part 1.
        (Actually make the bonds using bond_at_singlets,
         call assy.changed() if you make any bonds,
         and record some info in several attrs of self.)
        """
        if assy == None:
            assy = self.o.assy
        self.bondable_pairs_atoms = []
        self.merged_chunks = []
        singlet_found_with_multiple_bonds = False # True when there are singlets with multiple bonds.
        self.total_bonds_made = 0 # The total number of bondpoint pairs that formed bonds.
        singlets_not_bonded = 0 # Number of bondpoints not bonded.

#        print self.bondable_pairs

        # This first section of code bonds each bondable pair of singlets.
        for s1, s2 in self.bondable_pairs:
            # Make sure each singlet of the pair has only one way of bonding.
            # If either singlet has more than one ways to bond, we aren't going to bond them.
            if self.ways_of_bonding[s1.key] == 1 and self.ways_of_bonding[s2.key] == 1:
                # Record the real atoms in case I want to undo the bond later (before general Undo exists)
                # Currently, this undo feature is not implemented here. Mark 050325
                a1 = s1.singlet_neighbor()
                a2 = s2.singlet_neighbor()
                self.bondable_pairs_atoms.append( (a1,a2) ) # Add this pair to the list
                bond_at_singlets(s1, s2, move = False) # Bond the singlets.
                assy.changed() # The assy has changed.
            else:
                singlet_found_with_multiple_bonds = True
        self.singlet_found_with_multiple_bonds = singlet_found_with_multiple_bonds

    def _make_bonds_3(self):
        """
        Make bonds -- part 3.
        (Print history warning if self.singlet_found_with_multiple_bonds.)
        """
        if self.singlet_found_with_multiple_bonds:
            mbonds, singlets_not_bonded, bp = self.multibonds()

            self.total_bonds_made = len(self.bondable_pairs_atoms)

            if singlets_not_bonded == 1:
                msg = "%d bondpoint had more than one way to bond. It was not bonded." % (singlets_not_bonded,)
            else:
                msg = "%d bondpoints had more than one way to bond. They were not bonded." % (singlets_not_bonded,)
            env.history.message(orangemsg(msg))

        else:
            # All bondpoints had only one way to bond.
            self.total_bonds_made = len(self.bondable_pairs_atoms)

    def multibonds(self):
        """
        Returns the following information about bondable pairs:
        - the number of multiple bonds
        - number of bondpoints (singlets) with multiple bonds
        - number of bondpoint pairs that will bond
        """
        mbonds = 0 # number of multiple bonds
        mbond_singlets = [] # list of singlets with multiple bonds (these will not bond)
        sbond_singlets = 0 # number of singlets with single bonds (these will bond)

        for s1, s2 in self.bondable_pairs:

            if self.ways_of_bonding[s1.key] == 1 and self.ways_of_bonding[s2.key] == 1:
                sbond_singlets += 1
                continue

            if self.ways_of_bonding[s1.key] > 1:
                if s1 not in mbond_singlets:
                    mbond_singlets.append(s1)
                    mbonds += self.ways_of_bonding[s1.key] - 1 # The first one doesn't count.

            if self.ways_of_bonding[s2.key] > 1:
                if s2 not in mbond_singlets:
                    mbond_singlets.append(s2)
                    mbonds += self.ways_of_bonding[s2.key] - 1 # The first one doesn't count.

        return mbonds, len(mbond_singlets), sbond_singlets

    pass # end of class fusechunksBase

# end
