# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

"""
Protein.py -- Protein class implementation.

The Protein class stores protein-related information and provides several
methods used by Protein display style and Rosetta simulations.

Currently, the protein objects can be created by reading a protein
structure from PDB file or by using Peptide Builder.

@author: Piotr
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

piotr 080707: Created a preliminary version of the Protein class.

piotr 081908: Completed docstrings and documented better the code.

piotr 082008: Better documentation of this file; code re-factoring.
"""

import foundation.env as env

from utilities.debug_prefs import debug_pref, Choice_boolean_False
from utilities.prefs_constants import rosetta_backrub_enabled_prefs_key

from protein.model.Residue import Residue
from protein.model.Residue import SS_HELIX, SS_STRAND, SS_COIL, SS_TURN
from protein.model.Residue import AA_3_TO_1, NUC_3_TO_1

# Utility methods used by PDB reading code, perhaps they should be moved
# to files_pdb.py

def is_water(resName):
    """
    Check if a PDB residue is a water molecule.
    
    @param resName: PDB residue name (3-letter string)
    @type resName: string
    """    
    water_codes = ["H2O", "HHO", "OHH", "HOH", "OH2", "SOL", "WAT", "DOD", 
                   "DOH", "HOD", "D2O", "DDO", "ODD", "OD2", "HO1", "HO2",
                   "HO3", "HO4"]
    
    if resName[:3] in water_codes:
        return True
    
    return False

def is_amino_acid(resName):
    """
    Check if a PDB residue is an amino acid.
    
    @param resName: PDB residue name (3-letter string)
    @type resName: string
    """
    if AA_3_TO_1.has_key(resName[:3]):
        return True
    
    return False
    
def is_nucleotide(resName):
    """
    Check if a PDB residue is a nucleotide.
    
    @param resName: PDB residue name (3-letter string)
    @type resName: string
    """
    if NUC_3_TO_1.has_key(resName[:3]):
        return True
    
    return False

class Protein:
    """
    This class implements a protein model in NanoEngineer-1. 
    This class was implemented by Piotr in July 2008. 
    """
    
    def __init__(self):

        # PDB indentifier of the protein, typically, a four character string
        # of following format: "1abc"
        self.pdbId = ""
        
        # Single-character chain identifier.
        self.chainId = ''
        
        # Dictionary that maps residue names to residue objects. 
        # The name "sequence" is confusing and should be changed 
        # to "residues". piotr 082008        
        self.sequence = {}
        
        # Ordered list of amino acids.
        self.amino_acid_list = []
        
        # Ordered list of alpha carbon atoms. It should contain at least one atom.
        # This could be probably pre-calculated every time
        self.ca_atom_list = []
        
        # Index of "current" amino acid (used by Edit Rotamers command).
        self.current_aa_idx = 0

        # Display list for expanded rotamers, used by ProteinChunk.draw_realtime
        self.residues_dl = None
        
        # List of aromatic atoms, used for bond type assignment in PDB reading
        # code.
        self.aromatic_atoms = []
        
        # List of sp2 atoms bonded with a single bond, used for bond type
        # assignment in PDB reading code. If two atoms are "single bonded"
        # and both are sp2, they should be bonded with a single bond.
        self.single_bonded_atoms = []
        
    def set_chain_id(self, chainId):
        """
        Sets a single letter chain ID.
        
        @param chainId: chain ID of current protein
        @type chainId: character
        """
        self.chainId = chainId

    def get_chain_id(self):
        """
        Gets a single letter chain ID.
        
        @return: chain ID of current protein (character)
        """
        return self.chainId

    def set_pdb_id(self, pdbId):
        """
        Set a four-letter PDB identificator.
        
        @param pdbId: PDB ID of current protein
        @type pdbId: string (four characters)
        """
        self.pdbId = pdbId
        
    def get_pdb_id(self):
        """
        Return a four-letter PDB identificator.
        
        @return: PDB ID of current protein (four-character string)
        """
        return self.pdbId
        
    def add_pdb_atom(self, atom, pdbname, resId, resName, setType=False):
        """
        Adds a new atom to the protein. Returns a residue that the atom
        has been added to. Assigns the atom type.
        
        @param atom: new atom to be added to the protein
        @type atom: Atom
        
        @param pdbname: PDB name (label) of the atom (up to four characters)
        @type pdbname: string
        
        @param resId: PDB residue ID (an integer, usually)
        @type resId: integer
        
        @param resName: PDB residue name
        @type name: string
        
        @param setType: if True, try to determine the atom type based on 
                        PDB residue name and atom name                         
        @type setType: boolean
        
        @return: residue the atom has been added to (Residue) 
        """
        if self.sequence.has_key(resId):
            # Find an existing residue.
            aa = self.sequence[resId]
        else:
            # This is a new residue.
            aa = Residue(resId, resName)
            self.sequence[resId] = aa
            # Append the residue to amino acid list to have a properly ordered
            # list of amino acids.
            self.amino_acid_list.append(aa)
            
        # Add the atom to the residue.
        aa.add_atom(atom, pdbname)
        
        # If this is an alpha carbon atom, add it to the list of alpha carbons.
        if pdbname == "CA":
            self.ca_atom_list.append(atom)
            
        """
        if setType:
            _assigned = False
            # Look for the atom type and set the type
            if PROTEIN_ATOM_TYPES.has_key(resName):
                atom_type_dict = PROTEIN_ATOM_TYPES[resName]
                if atom_type_dict.has_key(pdbname):
                    atom_type = atom_type_dict[pdbname]
                    ### print (resName, pdbname, atom_type)
                    if atom_type == "sp2s":
                        atom.pdb_is_single_bonded = True
                        atom_type = "sp2"
                    if atom_type == "sp2a":
                        atom.pdb_is_aromatic = True
                        atom_type = "sp2"
                    atom.set_atomtype_but_dont_revise_singlets(atom_type) 
                    _assigned = True
            if not _assigned:
                # Look for common atom types (N, C, O)
                atom_type_dict = PROTEIN_ATOM_TYPES["ANY"]
                if atom_type_dict.has_key(pdbname):
                    atom_type = atom_type_dict[pdbname]
                    atom.set_atomtype_but_dont_revise_singlets(atom_type) 
        """
        
        return aa
    
    def is_atom_aromatic(self, atom):
        """
        Test if the atom is aromatic
        """
        if hasattr(atom, 'pdb_is_aromatic'):
            if atom.pdb_is_aromatic:
                return True
        else:
            return False
        
    def is_atom_single_bonded(self, atom):
        """
        Test if the atom is aromatic
        """
        if hasattr(atom, 'pdb_is_single_bonded'):
            if atom.pdb_is_single_bonded:
                return True
        else:
            return False
        
    def is_c_alpha(self, atom):
        """
        Check if the atom is a C-alpha atom.
        
        @param atom: atom to be tested
        @type atom: boolean
        
        @return: True if atom is an alpha carbon atom, False if it is not
        """
        if atom in self.ca_atom_list:
            return True
        else:
            return False
        
    def count_c_alpha_atoms(self):
        """
        Return a total number of alpha carbon atoms in the protein
        (usually equal to the protein sequence length).
        
        @return: number of C-alpha atoms (integer)
        """
        return len(self.ca_atom_list)
    
    def get_c_alpha_atoms(self):
        """
        Return a list of alpha carbon atoms.
        
        @return: list of atoms 
        """
        return self.ca_atom_list
    
    def is_c_beta(atom):
        """
        Check if the atom is a C-beta atom.
        
        @param atom: atom to be tested
        @type atom: boolean
        
        @return: True if atom is a carbon-beta atom, False if it is not.
        """
        if atom in self.cb_atom_list:
            return True
        else:
            return False
    
    def get_sequence_string(self):
        """
        Create and return a protein sequence string.
        
        @return: string corresponding to the protein sequence in 1-letter code
        """
        seq = ""
        for aa in self.get_amino_acids():
            seq += aa.get_one_letter_code()
        return seq
    
    def set_rosetta_protein_secondary_structure(self, inProtein):
        """
        Set the secondary structure of the protein outputted from rosetta to that
        of the inProtein. (created by Urmi)
        
        piotr 081908: Explanation. Rosetta fixed backbone simulation doesn't 
        change the backbone atom positions, so it is safe to copy the secondary
        structure information from the input protein. 
        
        piotr 082008: This is no longer true for flexible backbone simulations,
        i.e. when using the bakcrub mode. It is not going to cause major problems,
        as the backbone changes are relatively minor, but in general we need
        a secondary structure computation algorithm.
        
        @param inProtein:input protein chunk
        @type inProtein: L{Chunk}
        """
        #Urmi 20080728: created to set the secondary structure of the rosetta
        #outputted protein
        aa_list_for_rosetta = self.get_amino_acids()
        i = 0
        for aa in inProtein.protein.get_amino_acids():
            ss = aa.get_secondary_structure()
            aa_list_for_rosetta[i].set_secondary_structure(ss)
            i = i + 1
        return

    def get_secondary_structure_string(self):
        """
        Create and return a protein sequence string. 'H' corresponds
        to helical conformation, 'E' corresponds to extended secondary
        structure, 'C' corresponds to coil (other types of secondary structure).
        
        @return: secondary structure string 
        """
        ss_str = ""
        for aa in self.get_amino_acids():
            ss = aa.get_secondary_structure()
            if ss == SS_HELIX:    
                ss_str += "H"
            elif ss == SS_STRAND:
                ss_str += "E"
            else:
                ss_str += "-"
                
        return ss_str

    def get_amino_acid_id(self, index):
        """
        Create and return a description of this residue (protein name, index, 
        residue name, residue index).
        
        @return: string describing the current residue
        """
        aa_list = self.get_amino_acids()
        if index in range(len(aa_list)):
            aa = aa_list[index]
            aa_id = self.get_pdb_id() + \
                  self.get_chain_id() + \
                  "[" + \
                  repr(index+1) + \
                  "] : " + \
                  aa.get_three_letter_code() + \
                  "[" + \
                  repr(int(aa.get_id())) + \
                  "]" 
            return aa_id
        return None
    
    def get_amino_acid_id_list(self):
        """
        Create and return a list of residue descriptions (protein name, index, 
        residue name, residue index).
        
        @return: list of residue descriptions for all amino acids
        """
        id_list = []
        for idx in range(len(self.get_amino_acids())):
            aa_id = self.get_amino_acid_id(idx)
            id_list.append(aa_id)
            
        return id_list
    
    def get_amino_acids(self):
        """
        Return a list of residues in this protein.
        
        @return: list of residues
        """
        return self.amino_acid_list
    
    def assign_helix(self, resId):
        """
        Assign a helical secondary structure to resId.
        
        @param resId: residue ID for secondary structure assignment
        @type resId: int
        """
        if self.sequence.has_key(resId):
            aa = self.sequence[resId]
            aa.set_secondary_structure(SS_HELIX)
            
    def assign_strand(self, resId):
        """
        Assign a beta secondary structure to resId.
        
        @param resId: residue ID for secondary structure assignment
        @type resId: int
        """
        if self.sequence.has_key(resId):
            aa = self.sequence[resId]
            aa.set_secondary_structure(SS_STRAND)
            
    def assign_turn(self, resId):
        """
        Assign a turn secondary structure to resId.
        
        @param resId: residue ID for secondary structure assignment
        @type resId: int
        """
        if self.sequence.has_key(resId):
            aa = self.sequence[resId]
            aa.set_secondary_structure(SS_TURN)
            
    def expand_rotamer(self, aa):
        """
        Expand a side chain of a given amino acid.
        
        @param aa: amino acid to expand
        @type aa: Residue
        """
        self.residues_dl = None
        aa.expand()

    def is_expanded(self, aa):
        """
        Check if a given amino acid's rotamer is expanded.
        
        @param aa: amino acid to check 
        @type aa: Residue
        
        @return: True if amino acid's side chain is expanded
        """
        return aa.is_expanded()
    
    def collapse_all_rotamers(self):
        """
        Collapse all side chains.
        """
        self.residues_dl = None
        self.residues_hi_dl = None
        for aa in self.sequence.values():
            aa.collapse()
        
    def expand_all_rotamers(self):
        """
        Expand all side chains.
        """
        self.residues_dl = None
        self.residues_hi_dl = None
        for aa in self.sequence.values():
            aa.expand()
        
    def get_residue(self, atom):
        """
        For a given atom, return a residue that the atom belongs to.
        
        @param atom: atom to look for
        @type atom: Atom
        
        @return: residue the atom belongs to, or None if not found
        """
        for aa in self.sequence.itervalues():
            if aa.has_atom(atom):
                return aa
        
        return None
        
    def traverse_forward(self):
        """
        Increase an index of the current amino acid.
        """
        if self.current_aa_idx < len(self.sequence)-1:
            self.current_aa_idx += 1
            return True
        return False
    
    def traverse_backward(self):
        """
        Decrease an index of the current amino acid.
        """
        if self.current_aa_idx > 0:
            self.current_aa_idx -= 1
            return True
        return False
    
    def get_current_amino_acid(self):
        """
        Get current amino acid. 
        
        @return: current amino acid (Residue)
        """
        if self.current_aa_idx in range(len(self.sequence)):
            return self.sequence.values()[self.current_aa_idx]
        return None
    
    def get_amino_acid_at_index(self, index):
        """
        Return the amino acid at the given index
        
        @param index: index of amino acid requested
        @type index: int

        @return: amino acid (Residue)
        """
        #Urmi 20080728: created to do the two way connection between protein
        #sequence editor and residue combo box
        if index in range(len(self.amino_acid_list)):
            return self.amino_acid_list[index]
        return None
    
    def get_current_amino_acid_index(self):
        """
        Get index of current amino acid.
        
        @return: index of current amino acid (integer)
        """
        return self.current_aa_idx
        
    def set_current_amino_acid_index(self, index):
        """
        Set index of current amino acid.
        
        @param index: index of current amino acid
        @type index: integer
        """
        if index in range(len(self.amino_acid_list)):
            self.current_aa_idx = index
            
    def get_number_of_backrub_aa(self):
        """
        Returns a number of backrub amino acids.
        
        @return: number of amino acids assigned as "backrub" (integer)
        """
        nbr = 0
        for aa in self.get_amino_acids():
            if aa.get_backrub_mode():
                nbr += 1
        return nbr
        
    def is_backrub_setup_correctly(self):
        """
        Returns True if the backrub table is properly set up.
        
        @return: boolean
        """
        last_aa = None
        # Check if at least two consecutive amino acids have backrub flag
        # set as True.
        for aa in self.get_amino_acids():
            if last_aa and \
               last_aa.get_backrub_mode() and \
               aa.get_backrub_mode():
                return True
            last_aa = aa            
        return False
        
    def edit(self, win):
        """
        Edit the protein chunk
        
        @note: Probably should not reside here since this file is for the actual 
               model. May be we'll take care of that when we move to the new model
        
        """ 
        from utilities.GlobalPreferences import MODEL_AND_SIMULATE_PROTEINS
        if MODEL_AND_SIMULATE_PROTEINS:
            win.commandSequencer.userEnterCommand('MODEL_AND_SIMULATE_PROTEIN')
        else:    
            win.commandSequencer.userEnterTemporaryCommand('BUILD_PROTEIN')
            assert win.commandSequencer.currentCommand.commandName == 'BUILD_PROTEIN'
            win.commandSequencer.currentCommand.runCommand()
        return
       
# end of Protein class

# piotr 082008: This and possibly several Rosetta-related methods of the Protein 
# class should be re-factored and moved to a separate file.
    
def write_rosetta_resfile(filename, chunk):
    """
    Write a Rosetta resfile for a given protein chunk. Return True 
    if succefully written, otherwise return False. Writes backrub
    information if the backrub mode is enabled in user preferences.
    
    Currently, we only support single-chain Rosetta simulations.
    
    @param chunk: protein chunk to be written
    """
    
    # Make sure this is a valid protein chunk.
    if chunk is None or \
       chunk.protein is None:
        return False

    # Check if the backrub mode is enabled.
    use_backrub = env.prefs[rosetta_backrub_enabled_prefs_key]
    
    # Get a list of amino acids.
    amino_acids = chunk.protein.get_amino_acids()

    # Open the output file.
    f = open(filename, "w")
    
    if not f:
        return False
    
    # Write a standard file header.
    f.write(" This file specifies which residues will be varied\n")
    f.write("                                                  \n")
    f.write(" Column   2:  Chain                               \n")
    f.write(" Column   4-7:  sequential residue number         \n")
    f.write(" Column   9-12:  pdb residue number               \n")
    f.write(" Column  14-18: id  (described below)             \n")
    f.write(" Column  20-40: amino acids to be used            \n")
    f.write("                                                  \n")
    f.write(" NATAA  => use native amino acid                  \n")
    f.write(" ALLAA  => all amino acids                        \n")
    f.write(" NATRO  => native amino acid and rotamer          \n")
    f.write(" PIKAA  => select inividual amino acids           \n")
    f.write(" POLAR  => polar amino acids                      \n")
    f.write(" APOLA  => apolar amino acids                     \n")
    f.write("                                                  \n")
    f.write(" The following demo lines are in the proper format\n")
    f.write("                                                  \n")
    f.write(" A    1    3 NATAA                                \n")
    f.write(" A    2    4 ALLAA                                \n")
    f.write(" A    3    6 NATRO                                \n")
    f.write(" A    4    7 NATAA                                \n")
    f.write(" B    5    1 PIKAA  DFLM                          \n")
    f.write(" B    6    2 PIKAA  HIL                           \n")
    f.write(" B    7    3 POLAR                                \n")
    f.write(" -------------------------------------------------\n")

    # Begin the actual data records.
    f.write(" start\n")

    index = 0
    for aa in amino_acids:
        # For each consecutive amino acid
        index += 1
        mut = aa.get_mutation_range()
        # Write the amino acid and its mutation range name
        out_str = " " + \
                chunk.protein.get_chain_id() + \
                "%5d" % int(index) + \
                "%6s" % aa.get_id() + \
                mut 
        if use_backrub and \
           aa.backrub:
            # Append "B" when in backrub mode. 
            out_str += "B"
        if mut == "PIKAA":
            out_str += "  " + aa.get_mutation_descriptor().replace("_","") + "\n"
        else:
            out_str += "\n"
            
        f.write(out_str)
        
    # Close the output file. 
    f.close()
    
    return True

