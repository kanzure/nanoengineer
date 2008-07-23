# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

"""
Protein.py -- Protein class implementation.

@author: Piotr
@version: $Id$
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

chi_angles = { "GLY" : [ None, 
                         None, 
                         None, 
                         None ],
               "ALA" : [ None,
                         None, 
                         None,
                         None ],
               "SER" : [ [ "N"  , "CA" , "CB" , "OG"  ],
                         None,
                         None,
                         None ],
               "GLU" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         [ "CA" , "CB" , "CG" , "CD"  ],
                         [ "CB" , "CG" , "CD" , "OE1" ],
                         None ],
               "GLN" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         [ "CA" , "CB" , "CG" , "CD"  ],
                         [ "CB" , "CG" , "CD" , "OE1" ],
                         None ],
               "ASP" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         [ "CA" , "CB" , "CG" , "OD1" ],
                         None,
                         None ],
               "ASN" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         [ "CA" , "CB" , "CG" , "OD1" ],
                         None,
                         None ],
               "CYS" : [ [ "N"  , "CA" , "CB" , "SG"  ],
                         None,
                         None,
                         None ],
               "MET" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         [ "CA" , "CB" , "CG" , "SD" ],
                         None,
                         None ],
               "THR" : [ [ "N"  , "CA" , "CB" , "CG2" ],
                         None,
                         None,
                         None ],
               "LEU" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         [ "CA" , "CB" , "CG" , "CD1" ],
                         None,
                         None ],
               "ILE" : [ [ "N"  , "CA" , "CB" , "CG1" ],
                         [ "CA" , "CB" , "CG1", "CD1" ],
                         None,
                         None ],
               "VAL" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         None,
                         None,
                         None ],
               "TRP" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         None,
                         None,
                         None ],
               "TYR" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         None,
                         None,
                         None ],
               "LYS" : [ [ "N"  , "CA" , "CB" , "OG"  ],
                         None,
                         None,
                         None ],
               "ARG" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         None,
                         None,
                         None ],
               "HIS" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         None,
                         None,
                         None ],
               "PHE" : [ [ "N"  , "CA" , "CB" , "CG"  ],
                         [ "CA" , "CB" , "CG" , "CD1" ],
                         None,
                         None ] }

chi_exclusions = { "PHE" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3" ],
                             None,
                             None ],
                   "THR" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             None, 
                             None,
                             None ],
                   "GLU" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3" ], 
                             [ "CG", "HG2", "HG3" ],
                             None ],
                   "GLN" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3" ], 
                             [ "CG", "HG2", "HG3" ],
                             None ],
                   "ASP" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3" ], 
                             None,
                             None ],
                   "ASN" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3" ], 
                             None,
                             None ],
                   "CYS" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             None, 
                             None,
                             None ],
                   "MET" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3" ], 
                             None,
                             None ],
                   "ARG" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             None, 
                             None,
                             None ],
                   "LYS" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             None, 
                             None,
                             None ],
                   "HIS" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             None, 
                             None,
                             None ],
                   "LEU" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3" ], 
                             None,
                             None ],
                   "ILE" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3" ], 
                             None,
                             None ],
                   "SER" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             None, 
                             None,
                             None ],
                   "TYR" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             [ "CB", "HB2", "HB3"],
                             None,
                             None ],
                   "TRP" : [ [ "N", "H", "C", "O", "CA", "HA" ],
                             None, 
                             None,
                             None ] }

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
        self.atom_list = []
        self.name = name[:3]
        self.id = id
        self.secondary_structure = SS_COIL
        self.mutation_range = "NATAA"
        self.mutation_descriptor = ""
        self.expanded = False
        self.color = None
        
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
        self.atom_list.append(atom)
        
    def get_atom_list(self):
        """
        Return a list of atoms of residuum object.
        """
        return self.atom_list
    
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
        
    def get_atom_by_name(self, name):
        if self.atoms.has_key(name):
            return self.atoms[name]
        return None
    
    def get_c_alpha_atom(self):
        """
        Return a CA atom (or None).
        """
        return self.get_atom_by_name("CA")
    
    def get_c_beta_atom(self):
        """
        Return a CB atom (or None).
        """
        return self.get_atom_by_name("CA")
    
    def get_n_atom(self):
        """
        Return a backbone nitrogen atom.
        """
        return self.get_atom_by_name("N")
        
    def get_c_atom(self):
        """
        Return a backbone carbon atom.
        """
        return self.get_atom_by_name("C")
        
    def get_o_atom(self):
        """
        Return a backbone oxygen atom.
        """
        return self.get_atom_by_name("O")
        
    def set_mutation_range(self, range):
        """
        """
        self.mutation_range = range
        
    def get_mutation_range(self):
        """
        """
        return self.mutation_range
    
    def set_mutation_descriptor(self, descriptor):
        """
        """
        self.mutation_descriptor = descriptor
        
    def get_mutation_descriptor(self):
        return self.mutation_descriptor
    
    def calc_torsion_angle(self, atom_list):
        """
        Calculates a torsion angle between four atoms.
        """
   
        from Numeric import dot
        from math import atan2, pi, sqrt
        from geometry.VQT import cross
        
        if len(atom_list) != 4:
            return 0.0
        
        v12 = atom_list[0].posn() - atom_list[1].posn()
        v43 = atom_list[3].posn() - atom_list[2].posn()
        v23 = atom_list[1].posn() - atom_list[2].posn()
        
        p = cross(v23, v12)
        x = cross(v23, v43)
        y = cross(v23, x)
        
        u1 = dot(x, x)
        v1 = dot(y, y)
        
        if u1 < 0.0 or \
           v1 < 0.0:
            return 360.0
        
        u2 = dot(p, x) / sqrt(u1)
        v2 = dot(p, y) / sqrt(v1)
        
        if u2 != 0.0 and \
           v2 != 0.0:
            return atan2(v2, u2) * (180.0 / pi)
        else:
            return 360.0
         
    def get_chi_atom_list(self, which):
        """
        """
        if which in range(4):
            if chi_angles.has_key(self.name):
                chi_list = chi_angles[self.name]
                #print "CHI LIST = ", chi_list
                if chi_list[which]:
                    chi_atom_names = chi_list[which]
                    chi_atoms = []
                    for name in chi_atom_names:
                        atom = self.get_atom_by_name(name)
                        #print "CHI ATOM = ", (name, atom)
                        if atom:
                            chi_atoms.append(atom)
                    return chi_atoms
        return None
     
    def get_chi_atom_exclusion_list(self, which):
        """
        """
        if which in range(4):
            if chi_exclusions.has_key(self.name):
                chi_ex_list = chi_exclusions[self.name]
                #print "CHI LIST = ", chi_list
                ex_atoms = [self.get_atom_by_name("OXT")]
                for w in range(0, which + 1):
                    if chi_ex_list[w]:
                        ex_atom_names = chi_ex_list[w]
                        for name in ex_atom_names:
                            atom = self.get_atom_by_name(name)
                            #print "CHI ATOM = ", (name, atom)
                            if atom:
                                ex_atoms.append(atom)
                return ex_atoms
        return None
     
    def get_chi_angle(self, which):
        """
        Computes the side-chain Chi angle. Returns None if the angle
        doesn't exist.
        """
        chi_atom_list = self.get_chi_atom_list(which)
        if chi_atom_list:
            return self.calc_torsion_angle(chi_atom_list)                    
        return None

    
    def get_atom_list_to_rotate(self, which):
        """
        """
        atom_list = []
        
        chi_atom_exclusion_list = self.get_chi_atom_exclusion_list(which)
        
        if chi_atom_exclusion_list:
            all_atom_list = self.get_atom_list()
            for atom in all_atom_list:
                if atom not in chi_atom_exclusion_list:
                    atom_list.append(atom)
                  
        return atom_list

    def set_chi_angle(self, which, angle, lock=False):
        """
        """
        from geometry.VQT import norm, Q, V
        from math import pi, cos, sin
        
        chi_atom_list = self.get_chi_atom_list(which)
        if chi_atom_list:
            angle0 = self.calc_torsion_angle(chi_atom_list)
            dangle = angle - angle0
            if abs(dangle) > 0.0:
                if lock:
                    # Lock the edited amino acid.
                    self.set_mutation_range("NATRO")
                vec = norm(chi_atom_list[2].posn() - chi_atom_list[1].posn())
                atom_list = self.get_atom_list_to_rotate(which)
                first_atom_posn = chi_atom_list[1].posn()
                for atom in atom_list:
                    pos = atom.posn() - first_atom_posn
                    
                    cos_a = cos(pi * (dangle / 180.0))
                    sin_a = sin(pi * (dangle / 180.0))
                    
                    q = V(0, 0, 0)
                    
                    q[0] += (cos_a + (1.0 - cos_a) * vec[0] * vec[0]) * pos[0];
                    q[0] += ((1.0 - cos_a) * vec[0] * vec[1] - vec[2] * sin_a) * pos[1];
                    q[0] += ((1.0 - cos_a) * vec[0] * vec[2] + vec[1] * sin_a) * pos[2];
                 
                    q[1] += ((1.0 - cos_a) * vec[0] * vec[1] + vec[2] * sin_a) * pos[0];
                    q[1] += (cos_a + (1.0 - cos_a) * vec[1] * vec[1]) * pos[1];
                    q[1] += ((1.0 - cos_a) * vec[1] * vec[2] - vec[0] * sin_a) * pos[2];
                 
                    q[2] += ((1.0 - cos_a) * vec[0] * vec[2] - vec[1] * sin_a) * pos[0];
                    q[2] += ((1.0 - cos_a) * vec[1] * vec[2] + vec[0] * sin_a) * pos[1];
                    q[2] += (cos_a + (1.0 - cos_a) * vec[2] * vec[2]) * pos[2];
    
                    q += first_atom_posn
                    
                    atom.setposn(q)
                
        return None
        
    def expand(self):
        self.expanded = True
        
    def collapse(self):
        self.expanded = False
        
    def is_expanded(self):
        return self.expanded
    
    def set_color(self, color):
        self.color = color
        
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
        self.current_aa_idx = 0
        self.mutation_range_list = []
        self.residues_dl = None
        self.residues_hi_dl = None
        
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
    
    def set_rosetta_protein_secondary_structure(self, inProtein):
        
        aa_list_for_rosetta = self.get_amino_acids()
        i = 0
        for aa in inProtein.protein.get_amino_acids():
            ss = aa.get_secondary_structure()
            aa_list_for_rosetta[i].set_secondary_structure(ss)
            i = i + 1
        return

    def get_secondary_structure_string(self):
        """
        Create and return a protein sequence string.
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
        Create and return an amino acid ID (protein name, 
        index, residuum name, residuum index).
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
        Create and return a list of amino acid IDs (protein name, 
        index, residuum name, residuum index).
        """
        id_list = []
        for idx in range(len(self.get_amino_acids())):
            aa_id = self.get_amino_acid_id(idx)
            id_list.append(aa_id)
            
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
        self.residues_dl = None
        aa.expand()
        
    def is_expanded(self, aa):
        """
        Check if a given amino acid's rotamer is expanded.
        """
        return aa.is_expanded()
    
    def collapse_all_rotamers(self):
        """
        Collapse all rotamers.
        """
        self.residues_dl = None
        self.residues_hi_dl = None
        for aa in self.sequence.values():
            aa.collapse()
        
    def expand_all_rotamers(self):
        """
        Expand all rotamers.
        """
        self.residues_dl = None
        self.residues_hi_dl = None
        for aa in self.sequence.values():
            aa.expand()
        
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
        if index in range(len(self.sequence)):
            self.current_aa_idx = index
       
# end of Protein class

def write_rosetta_resfile(filename, chunk):
    """
    Write a Rosetta resfile for a given protein chunk. Return True 
    if succefully written, otherwise return False.
    """
    
    # Make sure this is a valid protein chunk.
    if chunk is None or \
       chunk.protein is None:
        return False

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
        index += 1
        mut = aa.get_mutation_range()
        out_str = " " + \
                chunk.protein.get_chain_id() + \
                "%5d" % int(index) + \
                "%5d " % int(aa.get_id()) + \
                mut 
        if mut == "PIKAA":
            out_str += "  " + aa.get_mutation_descriptor().replace("_","") + "\n"
        else:
            out_str += "\n"
            
        f.write(out_str)
        
    # Close the output file. 
    f.close()
    
    return True

