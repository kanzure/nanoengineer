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

To do:

- get_id_for_aa(): Add flag options for customizing the description(s) returned for aa_ids.
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
    See module docstring for more info.
    """
    # This class was implemented by Piotr in July 2008. 
    
    def __init__(self):

        # Dictionary that maps residue names to residue objects.
        self.residues = {}
        
        # Ordered list of amino acids.
        self.residues_list = []
        
        # Ordered list of alpha carbon atoms. It should contain at least one atom.
        # This could be probably pre-calculated every time
        # [I can't tell what that last sentence means -- every time that what occurs?
        #  motivation? -- bruce 080828]
        self.ca_atom_list = []
        
        # Single-character chain identifier.
        self.chainId = ''
        
        # PDB identifier of the protein, typically, a four character string
        # in the following format: "1abc"
        self.pdbId = ""
        
        # Index of "current" amino acid (used by Edit Protein command).
        self.current_aa_idx = 0

        # Display list for expanded rotamers, used by ProteinChunk.draw_realtime
        # The purpose of this list is to speed up drawing of "expanded" rotamers,
        # and avoid re-generating protein models in reduced display style 
        # if a modification is made to side chain atoms and not to backbone 
        # atoms (e.g. if a side chain chi angle was edited). 
        # The idea is to allow for simultaneous displaying of atomistic
        # (for expanded rotamers) and reduced (for backbone) representations.
        # This implementation is wrong, as the display list is never properly
        # deleted. This attribute could be moved to Chunk class, or implemented
        # in a different way, so the list is deleted in current OpenGL context.
        # Potentially, current implementation can cause memory leaks by not
        # deleting display lists. 
        self.residues_dl = None
        
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
        Set a four-letter PDB identifier.
        
        @param pdbId: PDB ID of current protein
        @type pdbId: string (four characters)
        """
        self.pdbId = pdbId
        
    def get_pdb_id(self):
        """
        Return a four-letter PDB identifier.
        
        @return: PDB ID of current protein (four-character string)
        """
        return self.pdbId
        
    def add_pdb_atom(self, atom, pdbname, resId, resName, setType = False):
        """
        Adds a new atom to the protein. Returns a residue that the atom
        has been added to. 
        
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
        if self.residues.has_key(resId):
            # Find an existing residue.
            aa = self.residues[resId]
        else:
            # This is a new residue.
            aa = Residue()
            self.residues[resId] = aa
            # Append the residue to amino acid list to have a properly ordered
            # list of amino acids.
            self.residues_list.append(aa)
            
        # Add the atom to the residue.
        aa.add_atom(atom, pdbname)
        
        # If this is an alpha carbon atom, add it to the list of alpha carbons.
        if pdbname == "CA":
            self.ca_atom_list.append(atom)
            
        return aa
        
    def is_c_alpha(self, atom):
        """
        Check if the atom is a C-alpha atom.
        
        @param atom: atom to be tested
        @type atom: Atom
        
        @return: True if atom is an alpha carbon atom, False if it is not
        @rtype: boolean
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
        
        @note: the returned list is mutable and should not be modified
        outside of the Protein class.

        @return: list of alpha carbon atoms
        """
        return self.ca_atom_list
    
    def is_c_beta(atom):
        """
        Check if the atom is a C-beta atom.
        
        @param atom: atom to be tested
        @type atom: Atom
        
        @return: True if atom is a carbon-beta atom, False if it is not.
        @rtype: boolean
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
        of the inProtein.
        
        @param inProtein:input protein chunk
        @type inProtein: L{Chunk}
        """
        #Urmi 20080728: created to set the secondary structure of the rosetta
        #outputted protein
        #
        # piotr 081908: Explanation. Rosetta fixed backbone simulation doesn't 
        # change the backbone atom positions, so it is safe to copy the secondary
        # structure information from the input protein. 
        # piotr 082008: This is no longer true for flexible backbone simulations,
        # i.e. when using the backrub mode. It is not going to cause major problems,
        # as the backbone changes are relatively minor, but in general we need
        # a secondary structure computation algorithm.
                
        aa_list_for_rosetta = self.get_amino_acids()
        i = 0
        for aa in inProtein.protein.get_amino_acids():
            ss = aa.get_secondary_structure()
            aa_list_for_rosetta[i].set_secondary_structure(ss)
            i = i + 1

    def get_secondary_structure_string(self):
        """
        Create and return a protein sequence string. 'H' corresponds
        to helical conformation, 'E' corresponds to extended secondary
        structure, '-' corresponds to coil (other types of secondary structure).
        
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

    # The two methods below (get_id_for_aa and get_amino_acid_id)
    # should probably be renamed, the names are confusing now -- piotr 080902
    
    def get_id_for_aa(self, aa, index):
        """
        Create and return an info text describing a specified residue.
        (See "get_amino_acid_id" method docstring for more information.)

        @param aa: queried amino acid
        @type aa: Residue
        
        @param index: index of the queried amino acid [0, sequence_length-1]
        @type index: int
        
        @return: string describing this residue
        """
        # REVIEW: should this be private? Also, I guessed "@type aa".
        # [bruce 080904 comment]
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
        
    def get_amino_acid_id(self, index):
        """
        Create and return a descriptive text related to a residue of a given
        sequence index. The text is composed of protein name, index, residue name, 
        residue index.

        @note: this method will cause an exception if there is no residue
               of the specified index
        
        @param index: index of a queried amino acid [0, sequence_length-1]
        @type index: int
        
        @return: string describing this residue
        """
        aa_list = self.get_amino_acids()

        if index in range(len(aa_list)):
            aa = aa_list[index]
            aa_id = self.get_id_for_aa(aa, index)
            return aa_id

        raise Exception("Residue index is out of range: %d" % index)
    
    def get_amino_acid_id_list(self):
        """
        Create and return a list of residue descriptions. See get_amino_acid_id
        for details on the description format.
        
        @return: list of residue descriptions for all amino acids
        """
        id_list = []
        index = 0
        
        for aa in self.get_amino_acids():
            aa_id = self.get_id_for_aa(aa, index)
            id_list.append(aa_id)
            index += 1
            
        return id_list
    
    def get_amino_acids(self):
        """
        Return a list of residues in this protein. 
        
        @note: the returned list is mutable and should not be modified
               outside of the Protein class.
        
        @return: list of residues
        """
        return self.residues_list
    
    def count_amino_acids(self):
        """
        Returns the number of amino acids.
        """
        return len(self.residues_list)
    
    def assign_helix(self, resId):
        """
        Assign a helical secondary structure to resId.

        @note: this method will raise an exception if a residue of a 
        specified resId doesn't exist
        
        @param resId: residue ID for secondary structure assignment
        @type resId: int
        """
        if self.residues.has_key(resId):
            aa = self.residues[resId]
            aa.set_secondary_structure(SS_HELIX)
            
        raise Exception("Specified residue doesn't exist")
 
    def assign_strand(self, resId):
        """
        Assign a beta secondary structure to resId.
        
        The proper name of this secondary structure type is 
        "beta strand", but names "beta", "strand", "extended" are used 
        interchangeably (PDB files use "STRAND" name to mark the beta
        conformation fragments).
        
        @note: this method will raise an exception if a residue of a 
        specified resId doesn't exist

        @param resId: residue ID for secondary structure assignment
        @type resId: int
        """
        if self.residues.has_key(resId):
            aa = self.residues[resId]
            aa.set_secondary_structure(SS_STRAND)
            
        raise Exception("Specified residue doesn't exist")
    
    def assign_turn(self, resId):
        """
        Assign a turn secondary structure to resId.
        
        @note: this method will raise an exception if a residue of a 
        specified resId doesn't exist

        @param resId: residue ID for secondary structure assignment
        @type resId: int
        """
        if self.residues.has_key(resId):
            aa = self.residues[resId]
            aa.set_secondary_structure(SS_TURN)
            
        raise Exception("Specified residue doesn't exist")

    def expand_rotamer(self, aa):
        """
        Expand a side chain of a given residue.
        
        @note: aa should belong to the Protein object.
        
        @param aa: amino acid to expand
        @type aa: Residue
        
        @return: True if a given residue belongs to self, or False otherwise.        
        """
        if aa in self.residues_list:
            self.residues_dl = None
            aa.expand()
            return True
        
        return False
    
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
        for aa in self.residues.values():
            aa.collapse()
        
    def expand_all_rotamers(self):
        """
        Expand all side chains.
        """
        self.residues_dl = None
        self.residues_hi_dl = None
        for aa in self.residues.values():
            aa.expand()
        
    def get_residue(self, atom):
        """
        For a given atom, return a residue that the atom belongs to.
        
        @param atom: atom to look for
        @type atom: Atom
        
        @return: residue the atom belongs to, or None if not found
        """
        for aa in self.residues.itervalues():
            if aa.has_atom(atom):
                return aa
        
        return None
        
    def traverse_forward(self):
        """
        Increase an index of the current amino acid. The index is an 
        attribute of self (Protein class).
        
        @return: True if the forward step is possible, otherwise False.
        """
        if self.current_aa_idx < len(self.residues) - 1:
            self.current_aa_idx += 1
            return True
        return False
    
    def traverse_backward(self):
        """
        Decrease an index of the current amino acid. The index is an 
        attribute of self (Protein class).
        
        @return: True if the backward step is possible, otherwise False.
        """
        if self.current_aa_idx > 0:
            self.current_aa_idx -= 1
            return True
        
        return False
    
    # General comment regarding the "current residue" mechanism. The purpose
    # of the "current_aa_idx" attribute is to have a mechanism for selecting
    # and focusing on an individual amino acid. Currently, this mechanism
    # is only used by "Edit Protein" command and probably the "Edit Protein"
    # command should keep track of the current residue. It would be
    # better if this attribute was removed from the Protein class. 
    # -- piotr 080902
    
    def get_current_amino_acid(self):
        """
        Get current amino acid. 
        
        @return: current amino acid (Residue) 
        """
        if self.current_aa_idx in range(len(self.residues_list)):
            return self.residues_list[self.current_aa_idx]
        return None
    
    def get_amino_acid_at_index(self, index):
        """
        Return the amino acid at the given index.
        
        @note: This method returns None if there is no amino acid at the
        specified index. This is intentional - callers should be aware of it.
        
        @param index: index of amino acid requested
        @type index: int

        @return: amino acid (Residue)
        """
        #Urmi 20080728: created to do the two way connection between protein
        #sequence editor and residue combo box
        if index in range(len(self.residues_list)):
            return self.residues_list[index]
        
        return None
    
    def get_current_amino_acid_index(self):
        """
        Get index of current amino acid.
        
        @return: index of current amino acid (integer)
        """
        return self.current_aa_idx
        
    def set_current_amino_acid_index(self, index):
        """
        Set index of current amino acid (if it's in the allowed range).
        
        @param index: index of current amino acid
        @type index: integer
        
        @return: True if the index is allowed, False if it is out of allowed range
        @rtype: boolean
        """
        if index in range(len(self.residues_list)):
            self.current_aa_idx = index
            return True
        else:
            return False
    
    def get_number_of_backrub_aa(self):
        """
        Returns a number of backrub amino acids.
        
        @return: number of amino acids assigned as "backrub" 
        @rtype: integer
        """
        nbr = 0
        for aa in self.get_amino_acids():
            if aa.get_backrub_mode():
                nbr += 1
        
        return nbr
        
    def is_backrub_setup_correctly(self):
        """
        Returns True if the backrub table is properly set up, False otherwise.
        
        @rtype: boolean
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
        
        @note: Probably this method should not reside here, since this file is for
               the actual model. Maybe we'll take care of that when we move to the
               new model
        """ 
        win.commandSequencer.userEnterCommand('EDIT_PROTEIN')
        return
       
    pass # end of class Protein


# Protein helper methods should be located here.
# Mark 2008-12-14
def getAllProteinChunksInPart(assy):
    """
    Returns a list of all the protein chunks in assy.
    
    @return: a list of all the protein chunks in assy.
    @rtype: list of chunks
    """
    proteinChunkList = []
    for mol in assy.molecules:
        if mol.isProteinChunk():
            proteinChunkList.append(mol)
    return proteinChunkList

# piotr 082008: This and possibly several Rosetta-related methods of the Protein 
# class should be re-factored and moved to a separate file in simulations/ROSETTA.
    
def write_rosetta_resfile(filename, chunk):
    """
    Write a Rosetta resfile for a given protein chunk. Return True 
    if successfully written, otherwise return False. Writes backrub
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

