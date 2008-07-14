# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

"""
Protein.py -- Protein class implementation.

@author: Piotr
$Id:$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

Piotr 2008-07-09:
- Created a preliminary version of the Protein class.

"""

# 3-letter to 1-letter conversion
AA_3_TO_1 = {
    "ALA" : "A",
    "ARG" : "R",
    "ASN" : "N",
    "ASP" : "D",
    "CYS" : "C",
    "GLN" : "E",
    "GLU" : "Q",
    "GLY" : "G",
    "HIS" : "H",
    "ILE" : "I",
    "LEU" : "L",
    "LYS" : "K",
    "MET" : "M",
    "MSE" : "M",
    "PHE" : "F",
    "PRO" : "P",
    "SER" : "S",
    "THR" : "T",
    "TRP" : "W",
    "TYR" : "Y",
    "UNK" : "X",
    "VAL" : "V" }

# Types of secondary structure as defined in PDB format.
# There are various definitions of secondary structure in use.
# The most common is a three-letter code: helix (H), extended (E),
# coil (C). PDB distingushes a fourth type, turn (T) that corresponds
# to the chain fragments that rapidly change direction, have
# a hydrogen bond patter present, and are not helices nor strands.
# Currently, the turns are not used for visualization purposes in NE1.

SS_COIL = 0
SS_HELIX = 1
SS_STRAND = 2
SS_TURN = 3

from utilities.debug_prefs import debug_pref, Choice_boolean_False

enableProteins =  debug_pref("Enable Proteins? (next session)",
    Choice_boolean_False,
    non_debug = True,
    prefs_key = True)

def is_water(resName, atomName):
    """
    Check if a PDB residue is a water molecule.
    """    
    water_codes = ["H2O", "HHO", "OHH", "HOH", "OH2", "SOL", "WAT", "DOD", 
                   "DOH", "HOD", "D2O", "DDO", "ODD", "OD2", "HO1", "HO2",
                   "HO3", "HO4"]
    
    if atomName == "O" and \
       resName in water_codes:
        return True
    
    return False

class Residuum:
    """
    This class implements a Residuum object.
    """
    
    def __init__(self, id, name):
        """
        id is a PDB residue number.
        name is a PDB name (amino acid name in three-letter code.
        """
        self.atoms = {} # dictionary for name -> atom mapping
        self.names = {} # inverse dictionary for atom -> name mapping
        self.name = name[:3]
        self.id = id
        self.secondary_structure = SS_COIL
        
    def get_atom_name(self, atom):
        """
        For a given PDB atom name, return a corresponding atom.
        """
        if atom in self.names:
            return self.names[atom]
        return None
       
    def add_atom(self, atom, pdbname):
        """ 
        Add a new atom to the atom dictionary. 
        """
        self.atoms[pdbname] = atom
        self.names[atom] = pdbname
        
    def get_atom_list(self):
        """
        Return a list of atoms of residuum object.
        """
        return self.atoms.itervalues()
    
    def get_three_letter_code(self):
        """
        Return a three-letter amino acid code.
        """
        return self.name

    def get_one_letter_code(self):
        """
        Return a one-letter amino acid code, or "X" if the residuum code
        is not recognized.
        """
        if AA_3_TO_1.has_key(self.name):
            return AA_3_TO_1[self.name]
        
        return "X"
    
    def get_id(self):
        """
        Return a residue ID.
        """
        return self.id
    
    def get_atom(self, pdbname):
        """
        Return an atom by PDB name.
        """
        if self.atoms.has_key(pdbname):
            return self.atoms[pdbname]
        return None

    def has_atom(self, atom):
        """
        Check if the atom belongs to self.
        """
        if atom in self.atoms.values():
            return True
        else:
            return False
        
    def set_secondary_structure(self, type):
        """
        Set a secondary structure type for current amino acid.
        """
        self.secondary_structure = type
        
    def get_secondary_structure(self):
        """
        Retrieve a secondary structure type.
        """
        return self.secondary_structure
        
    def get_c_alpha_atom(self):
        """
        Return a CA atom (or None).
        """
        if self.atoms.has_key("CA"):
            return self.atoms["CA"]
        return None
    
    def get_c_beta_atom(self):
        """
        Return a CB atom (or None).
        """
        if self.atoms.has_key("CB"):
            return self.atoms["CB"]
        return None
    
    def get_n_atom(self):
        """
        Return a backbone nitrogen atom.
        """
        if self.atoms.has_key("N"):
            return self.atoms["N"]
        return None
        
    def get_c_atom(self):
        """
        Return a backbone carbon atom.
        """
        if self.atoms.has_key("C"):
            return self.atoms["C"]
        return None
        
    def get_o_atom(self):
        """
        Return a backbone oxygen atom.
        """
        if self.atoms.has_key("O"):
            return self.atoms["O"]
        return None
        
# End of Residuum class.

class Protein:
    """
    This class implements a protein model.
    """
    
    def __init__(self):
        self.ca_atom_list = []
        self.sequence = {}
        self.expanded_rotamers_list = []
        self.chainId = ''
        self.pdbId = ""
        self.current_aa_idx = 0
        
    def set_chain_id(self, chainId):
        """
        Sets a single letter chain ID.
        """
        self.chainId = chainId

    def get_chain_id(self):
        """
        Gets a single letter chain ID.
        """
        return self.chainId

    def set_pdb_id(self, pdbId):
        """
        Set a four-letter PDB identificator.
        """
        self.pdbId = pdbId
        
    def get_pdb_id(self):
        """
        Return a four-letter PDB identificator.
        """
        return self.pdbId
        
    def add_pdb_atom(self, atom, pdbname, resId, resName):
        """
        Adds a new atom to the protein.
        """
        if self.sequence.has_key(resId):
            # Find an existing residuum.
            aa = self.sequence[resId]
        else:
            # This is a new residuum.
            aa = Residuum(resId, resName)
            self.sequence[resId] = aa
           
        aa.add_atom(atom, pdbname)
        
        if pdbname == "CA":
            self.ca_atom_list.append(atom)
        
    def is_c_alpha(self, atom):
        """
        Check if this is a C-alpha atom.
        """
        if atom in self.ca_atom_list:
            return True
        else:
            return False
        
    def count_c_alpha_atoms(self):
        """
        Return a total number of alpha carbon atoms.
        """
        return len(self.ca_atom_list)
    
    def get_c_alpha_atoms(self):
        """
        Return a list of alpha carbon atoms.
        """
        return self.ca_atom_list
    
    def is_c_beta(atom):
        """
        Check if this is a C-beta atom.
        """
        if atom in self.cb_atom_list:
            return True
        else:
            return False
    
    def get_sequence_string(self):
        """
        Create and return a protein sequence string.
        """
        seq = ""
        for aa in self.get_amino_acids():
            seq += aa.get_one_letter_code()
        return seq

    def get_amino_acid_id_list(self):
        """
        Create and return a list of amino acid IDs (protein name, 
        index, residuum name, residuum index).
        """
        id_list = []
        idx = 1
        for aa in self.get_amino_acids():
            aa_id = self.get_pdb_id() + \
                  self.get_chain_id() + \
                  "[" + \
                  repr(idx) + \
                  "] : " + \
                  aa.get_three_letter_code() + \
                  "[" + \
                  repr(int(aa.get_id())) + \
                  "]" 
            id_list.append(aa_id)
            idx += 1
            
        return id_list
    
    def get_amino_acids(self):
        """
        Return a list of residues in current protein object.
        """
        return self.sequence.values()
    
    def assign_helix(self, resId):
        """
        Assign a helical secondary structure to resId.
        """
        if self.sequence.has_key(resId):
            aa = self.sequence[resId]
            aa.set_secondary_structure(SS_HELIX)
            
    def assign_strand(self, resId):
        """
        Assign a beta secondary structure to resId.
        """
        if self.sequence.has_key(resId):
            aa = self.sequence[resId]
            aa.set_secondary_structure(SS_STRAND)
            
    def assign_turn(self, resId):
        """
        Assign a turn secondary structure to resId.
        """
        if self.sequence.has_key(resId):
            aa = self.sequence[resId]
            aa.set_secondary_structure(SS_TURN)
            
    def expand_rotamer(self, aa):
        """
        Expand a rotamer.
        """
        if not aa in self.expanded_rotamers_list:
            self.expanded_rotamers_list.append(aa)
            
    def is_expanded(self, aa):
        """
        Check if a given amino acid's rotamer is expanded.
        """
        if aa in self.expanded_rotamers_list:
            return True
    
        return False
    
    def collapse_all_rotamers(self):
        """
        Collapse all rotamers.
        """
        self.expanded_rotamers_list = []
        
    def get_residuum(self, atom):
        """
        For a given atom, return a residuum the atom belongs to.
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
        """
        if self.current_aa_idx in range(len(self.sequence)):
            return self.sequence.values()[self.current_aa_idx]
        return None
    
    def get_current_amino_acid_index(self):
        """
        """
        return self.current_aa_idx
        
    def set_current_amino_acid_index(self, index):
        """
        """
        self.current_aa_idx = index
        
# end of Protein class

