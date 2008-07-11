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

enableProteins =  debug_pref("Enable Proteins?",
    Choice_boolean_False,
    non_debug = True,
    prefs_key = True)

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
        self.chainId = ''
        self.pdbId = ""
        
    def set_chain_id(self, chainId):
        """
        Sets a single letter chain ID.
        """
        self.chainId = chainId

    def set_pdb_id(self, pdbId):
        """
        Set a four-letter PDB identificator.
        """
        self.pdbId = pdbId
        
    def get_pdb_id(self, pdbId):
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

    def get_amino_acids(self):
        """
        Return a list of residues in current protein object.
        """
        return self.sequence.itervalues()
    
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
            
    def get_residuum(self, atom):
        """
        For a given atom, return a residuum the atom belongs to.
        """
        for aa in self.sequence.itervalues():
            if aa.has_atom(atom):
                return aa
        
        return None
        
# end of Protein class

"""
def getPathLocation():
    #Piotr harcode your dataBasePath and simFilesPath here
    #simplest would be to overwrite the path's file everytime, instead of
    #doing text processing to figure out if the file has changed
    # paths.txt is small enough to do so
    dataBasePath = "/Users/piotr/Programs/RosettaBundle-2.3.0/rosetta_database"
    simFilesPath = "/Users/piotr/Programs/RosettaBundle-2.3.0/tests/"
    pathFile = simFilesPath + "/paths.txt"
    f = open(pathFile, "w+")
    line = "Rosetta Input/Output Paths (order essential)\n"
    f.write(line)
    line = "path is first '/', './',or  '../' to next whitespace, must end with '/'\n"
    f.write(line)
    line = "INPUT PATHS:\n"
    f.write(line)
    word = ["Temp", "Temp"]
          # input files wil always be in this directory
    tempWord = "pdb1"
    word[0] = "%-32s" % tempWord
    simFilesPath = "/Users/piotr/Programs/RosettaBundle-2.3.0/tests/"
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)
    tempWord = "pdb2"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "alternate data files"
    word[0] = "%-32s" % tempWord
    word[1] = dataBasePath + '/\n'
    line = ''.join(word)
    f.write(line)

    tempWord = "fragments"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "structure dssp,ssa (dat,jones)"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "sequence fasta,dat,jones"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "constraints"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "starting structure"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "data files"
    word[0] = "%-32s" % tempWord
    tempWord = dataBasePath + "/\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    line = "OUTPUT PATHS:\n"
    f.write(line)

    tempWord = "movie"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "pdb path"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "score"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "status"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "user"
    word[0] = "%-32s" % tempWord
    tempWord = simFilesPath + "\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    line = "FRAGMENTS: (use '*****' in place of pdb name and chain)\n"
    f.write(line)

    tempWord = "2"
    word[0] = "%-39s" % tempWord
    tempWord = "number of valid fragment files\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "3"
    word[0] = "%-39s" % tempWord
    tempWord = "frag file 1 size\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "aa*****03_05.200_v1_3"
    word[0] = "%-39s" % tempWord
    tempWord = "name\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "9"
    word[0] = "%-39s" % tempWord
    tempWord = "frag file 2 size\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)

    tempWord = "aa*****09_05.200_v1_3"
    word[0] = "%-39s" % tempWord
    tempWord = "name\n"
    word[1] = tempWord
    line = ''.join(word)
    f.write(line)
    f.close()
    return pathFile
"""
