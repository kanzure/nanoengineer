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

# 3-letter to 1-letter amino acid name conversion
# The three-letter names are used to distinguish "protein" from "non-protein"
# residues in PDB reading code.
AA_3_TO_1 = {
    'ALA':'A', # 20 standard amino acids
    'VAL':'V', 
    'PHE':'F', 
    'PRO':'P', 
    'MET':'M',
    'ILE':'I', 
    'LEU':'L', 
    'ASP':'D', 
    'GLU':'E', 
    'LYS':'K',
    'ARG':'R', 
    'SER':'S', 
    'THR':'T', 
    'TYR':'Y', 
    'HIS':'H',
    'CYS':'C', 
    'ASN':'N', 
    'GLN':'Q', 
    'TRP':'W', 
    'GLY':'G',
    '2AS':'D', # Non-standard codes encountered in the PDB.
    '3AH':'H', # Usually, these codes correspond to modified residues 
    '5HP':'E', # and are only used by the Protein class to convert between 
    'ACL':'R', # three- and single- letter representations. 
    'AIB':'A',
    'ALM':'A', 
    'ALO':'T', 
    'ALY':'K', 
    'ARM':'R', 
    'ASA':'D',
    'ASB':'D', 
    'ASK':'D', 
    'ASL':'D', 
    'ASQ':'D', 
    'AYA':'A',
    'BCS':'C', 
    'BHD':'D', 
    'BMT':'T', 
    'BNN':'A', 
    'BUC':'C',
    'BUG':'L', 
    'C5C':'C', 
    'C6C':'C', 
    'CCS':'C', 
    'CEA':'C',
    'CHG':'A', 
    'CLE':'L', 
    'CME':'C', 
    'CSD':'A', 
    'CSO':'C',
    'CSP':'C', 
    'CSS':'C', 
    'CSW':'C', 
    'CXM':'M', 
    'CY1':'C',
    'CY3':'C', 
    'CYG':'C', 
    'CYM':'C', 
    'CYQ':'C', 
    'DAH':'F',
    'DAL':'A', 
    'DAR':'R', 
    'DAS':'D', 
    'DCY':'C', 
    'DGL':'E',
    'DGN':'Q', 
    'DHA':'A', 
    'DHI':'H', 
    'DIL':'I', 
    'DIV':'V',
    'DLE':'L', 
    'DLY':'K', 
    'DNP':'A', 
    'DPN':'F', 
    'DPR':'P',
    'DSN':'S', 
    'DSP':'D', 
    'DTH':'T', 
    'DTR':'W', 
    'DTY':'Y',
    'DVA':'V', 
    'EFC':'C', 
    'FLA':'A', 
    'FME':'M', 
    'GGL':'E',
    'GLZ':'G', 
    'GMA':'E', 
    'GSC':'G', 
    'HAC':'A', 
    'HAR':'R',
    'HIC':'H', 
    'HIP':'H', 
    'HMR':'R', 
    'HPQ':'F', 
    'HTR':'W',
    'HYP':'P', 
    'IIL':'I', 
    'IYR':'Y', 
    'KCX':'K', 
    'LLP':'K',
    'LLY':'K', 
    'LTR':'W', 
    'LYM':'K', 
    'LYZ':'K', 
    'MAA':'A',
    'MEN':'N', 
    'MHS':'H', 
    'MIS':'S', 
    'MLE':'L', 
    'MPQ':'G',
    'MSA':'G', 
    'MSE':'M', 
    'MVA':'V', 
    'NEM':'H', 
    'NEP':'H',
    'NLE':'L', 
    'NLN':'L', 
    'NLP':'L', 
    'NMC':'G', 
    'OAS':'S',
    'OCS':'C', 
    'OMT':'M', 
    'PAQ':'Y', 
    'PCA':'E', 
    'PEC':'C',
    'PHI':'F', 
    'PHL':'F', 
    'PR3':'C', 
    'PRR':'A', 
    'PTR':'Y',
    'SAC':'S', 
    'SAR':'G', 
    'SCH':'C', 
    'SCS':'C', 
    'SCY':'C',
    'SEL':'S', 
    'SEP':'S', 
    'SET':'S', 
    'SHC':'C', 
    'SHR':'K',
    'SOC':'C', 
    'STY':'Y', 
    'SVA':'S', 
    'TIH':'A', 
    'TPL':'W',
    'TPO':'T', 
    'TPQ':'A', 
    'TRG':'K', 
    'TRO':'W', 
    'TYB':'Y',
    'TYQ':'Y', 
    'TYS':'Y', 
    'TYY':'Y', 
    'AGM':'R', 
    'GL3':'G',
    'SMC':'C', 
    'ASX':'B', 
    'CGU':'E', 
    'CSX':'C', 
    'GLX':'Z',
    'UNK':'X' }

# 3- TO 1-letter conversion for PDB nucleotide names
NUC_3_TO_1 = {
    ' DG':'G',
    ' DA':'A',
    ' DC':'C',
    ' DT':'T',
    ' DU':'U',
    ' DI':'I',
    '  G':'G',
    '  A':'A',
    '  T':'T',
    '  U':'U',
    '  C':'C',
    '  I':'I' }
    
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

# PDB atom name sets for chiral angles for amino acid side chains
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

# Sets of atoms excluded from chi-angle rotations.
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

# Utility methods used by PDB reading code.

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

# Renamed this to "Residue" (which is a proper spelling, compared to "Residue",
# as Eric D has pointed out in his email).

# piotr 082008: This class should be re-factored and moved to its own file.

class Residue:
    """
    This class implements a Residue object. The residue is an object
    describing an individual amino acid of a protein chain.
    """
    
    def __init__(self, id, name):
        """
        @param id: PDB residue number.
        @type id: integer
        
        @param name: PDB name (amino acid name in three-letter code.
        @type name: string (3 characters)
        """
        # list of residue atoms in the same order as they occur in PDB file
        self.atom_list = []
        
        # dictionary for atom_name -> atom mapping
        self.atoms = {} 
        
        ##self.id = id

        # amino acid secondary structure        
        self.secondary_structure = SS_COIL

        # True if the residue is expanded. The feature is used by "Edit
        # Rotamers" command for efficient rotamer manipulation in reduced
        # protein display style.
        self.expanded = False
        
        # Rotamer color, used by "Edit Rotamers" command.
        self.color = None
        
        # These Rosetta-related attributes should be probably moved from this
        # class to some Rosetta-related structure. For now, the Residue
        # and Protein classes
        
        # Rosetta name of mutation range. 
        self.mutation_range = "NATAA"
        
        # Rosetta mutation descriptor. If set, it is usually a string of
        # 20 characters, corresponding to amino acid allowed at a given position.
        # Note: the descriptor is actuallt used by Rosetta only if mutation
        # range is set to "PIKAA". Otherwise, it is used only for informational
        # purposes. 
        self.mutation_descriptor = ""
        
        # True if this residue will be using backrub mode.
        self.backrub = False

    def get_atom_name(self, atom):
        """
        For a given PDB atom name, return a corresponding atom.
        """
        if atom.pdb_info.has_key('atom_name'):
            return atom.pdb_info['atom_name']
        else:
            return None
        
    def add_atom(self, atom, pdbname):
        """ 
        Add a new atom to the atom dictionary. 
        """
        self.atoms[pdbname] = atom
        self.atom_list.append(atom)

    def get_first_atom(self):
        """
        Return first atom of the residue, or None.
        """
        if len(self.atom_list):
            return self.atom_list[0]
        else:
            return None
        
    def get_atom_list(self):
        """
        Return a list of atoms for the residue.
        """
        return self.atom_list
    
    def get_side_chain_atom_list(self):
        """
        Return a list of side chain atoms for the residue. Assumes standard
        PDB atom names.
        """
        return [atom for atom in self.atom_list \
                if self.get_atom_name() not in ['C', 'N', 'O', 'H', 'HA']]

    def get_three_letter_code(self):
        """
        Return a three-letter amino acid code (the residue name).
        """
        atom = self.get_first_atom()
        if atom:
            if atom.pdb_info.has_key('residue_name'):
                return atom.pdb_info['residue_name'][:3]
        return None

    def get_name(self):
        """
        Just another version of get_three_letter_code.
        """
        return self.get_three_letter_code()
        
    def get_one_letter_code(self):
        """
        Return a one-letter amino acid code, or "X" if the residue code
        is not recognized.
        """
        if AA_3_TO_1.has_key(self.get_name()):
            return AA_3_TO_1[self.get_name()]
        
        return "X"
    
    def get_id(self):
        """
        Return a residue ID.
        
        The residue ID is a string representing the residue serial number 
        (integer value up to 9999) and concatenated residue insertion code 
        (single letter character). It is represented by a five character string.
        """
        atom = self.get_first_atom()
        if atom:
            if atom.pdb_info.has_key('residue_id'):
                return atom.pdb_info['residue_id']

        return None
    
    def get_index(self):
        """
        Return a residue index.
        """
        atom = self.get_first_atom()
        if atom:
            if atom.pdb_info.has_key('residue_id'):
                return int(atom.pdb_info['residue_id'][:3])

        return None
    
    def get_atom(self, pdbname):
        """
        Return an atom by PDB name.
        
        @param pdbname: a PDB name of an atom.
        @type: string
        """
        if self.atoms.has_key(pdbname):
            return self.atoms[pdbname]
        else:
            return None
    
    def has_atom(self, atom):
        """
        Check if the atom belongs to self. 
        
        @param atom: atom to be checked
        @type atom: Atom        
        """
        if atom in self.atoms.values():
            return True
        else:
            return False
        
    def set_secondary_structure(self, sec):
        """
        Set a secondary structure type for this residue.
        
        @param sec: secondary structure type to be assigned
        @type sec: int
        
        """
        self.secondary_structure = sec
        
    def get_secondary_structure(self):
        """
        Retrieve a secondary structure type.

        @return: secondary structure of this residue. 
        """
        return self.secondary_structure
        
    def get_atom_by_name(self, name):
        """
        Returns a residue atom for a given name, or None if not found.
        
        @param name: name of the atom
        @type name: string
        
        @return: atom
        """
        if self.atoms.has_key(name):
            return self.atoms[name]
        
        return None
    
    def get_c_alpha_atom(self):
        """
        Return an alpha-carbon atom atom (or None).
        
        @return: alpha carbon atom
        """
        return self.get_atom_by_name("CA")
    
    def get_c_beta_atom(self):
        """
        Return a beta carbon atom (or None).
        
        @return: beta carbon atom
        """
        return self.get_atom_by_name("CA")
    
    def get_n_atom(self):
        """
        Return a backbone nitrogen atom.
        
        @return: backbone nitrogen atom
        """
        return self.get_atom_by_name("N")
        
    def get_c_atom(self):
        """
        Return a backbone carbon atom.
        
        @return: backbone carbonyl group carbon atom
        """
        return self.get_atom_by_name("C")
        
    def get_o_atom(self):
        """
        Return a backbone oxygen atom.
        
        @return: backbone carbonyly group oxygen atom
        """
        return self.get_atom_by_name("O")
        
    def set_mutation_range(self, range):
        """
        Sets a mutation range according to Rosetta definition.
        
        @param range: mutation range
        @type range: string
        """
        self.mutation_range = range
        
    def get_mutation_range(self):
        """
        Gets a mutaion range according to Rosetta definition.
        nie,.
        @return: range
        """
        return self.mutation_range
    
    def set_mutation_descriptor(self, descriptor):
        """
        Sets a mutation descriptor according to Rosetta definition.
        
        @param descriptor: Rosetta mutation descriptor 
        @type descriptor: string (20-characters long)
        """
        self.mutation_descriptor = descriptor
        
    def get_mutation_descriptor(self):
        """
        Returns a mutation descriptor according to Rosetta definition.
        
        @return descriptor: string (20-characters long)
        """
        return self.mutation_descriptor
    
    def calc_torsion_angle(self, atom_list):
        """
        Calculates torsional angle defined by four atoms, A1-A2-A3-A4,
        Return torsional angle value between atoms A2 and A3.
        
        @param atom_list: list of four atoms describing the torsion bond
        @type atom_list: list
        
        @return: value of the torsional angle (float)
        """
   
        from Numeric import dot
        from math import atan2, pi, sqrt
        from geometry.VQT import cross
        
        if len(atom_list) != 4:
            # The list has to have four members.
            return 0.0
        
        # Calculate pairwise distances
        v12 = atom_list[0].posn() - atom_list[1].posn()
        v43 = atom_list[3].posn() - atom_list[2].posn()
        v23 = atom_list[1].posn() - atom_list[2].posn()

        # p is a vector perpendicular to the plane defined by atoms 1,2,3
        # p is perpendicular to v23_v12 plane
        p = cross(v23, v12)
        
        # x is a vector perpendicular to the plane defined by atoms 2,3,4.
        # x is perpendicular to v23_v43 plane
        x = cross(v23, v43)
        
        # y is perpendicular to v23_x plane
        y = cross(v23, x)
        
        # Calculate lengths of the x, y vectors.
        u1 = dot(x, x)
        v1 = dot(y, y)
        
        if u1 < 0.0 or \
           v1 < 0.0:
            return 360.0
        
        u2 = dot(p, x) / sqrt(u1)
        v2 = dot(p, y) / sqrt(v1)
        
        if u2 != 0.0 and \
           v2 != 0.0:
            # calculate the angle
            return atan2(v2, u2) * (180.0 / pi)
        else:
            return 360.0
         
    def get_chi_atom_list(self, which):
        """
        Create a list of four atoms for computing a given chi angle.
        Return None if no such angle exists for this amino acid.
        
        @param which: chi angle (0=chi1, 1=chi2, and so on)
        @type which: int
        
        @return: list of four atoms
        """
        if which in range(4):
            residue_name = self.get_name()
            if chi_angles.has_key(residue_name):
                chi_list = chi_angles[residue_name]
                if chi_list[which]:
                    chi_atom_names = chi_list[which]
                    chi_atoms = []
                    for name in chi_atom_names:
                        atom = self.get_atom_by_name(name)
                        if atom:
                            chi_atoms.append(atom)
                    return chi_atoms
        return None
     
    def get_chi_atom_exclusion_list(self, which):
        """
        Create a list of atoms excluded from rotation for a current amino acid.
        Return None if wrong chi angle is requested.
        
        @param which: chi angle (0=chi1, 1=chi2, and so on)
        @type which: int
        
        @return: list of atoms to be excluded from rotation
        """
        if which in range(4):
            residue_name = self.get_name()
            if chi_exclusions.has_key(residue_name):
                chi_ex_list = chi_exclusions[residue_name]
                ex_atoms = [self.get_atom_by_name("OXT")]
                for w in range(0, which + 1):
                    if chi_ex_list[w]:
                        ex_atom_names = chi_ex_list[w]
                        for name in ex_atom_names:
                            atom = self.get_atom_by_name(name)
                            if atom:
                                ex_atoms.append(atom)
                return ex_atoms
        return None
     
    def get_chi_angle(self, which):
        """
        Computes the side-chain Chi angle. Returns None if the angle
        doesn't exist.
        
        @param which: chi angle (0=chi1, 1=chi2, and so on)
        @type which: int
        
        @return: value of the specified chi angle
        """
        chi_atom_list = self.get_chi_atom_list(which)
        if chi_atom_list:
            return self.calc_torsion_angle(chi_atom_list)                  
        else:
            return None

    
    def get_atom_list_to_rotate(self, which):
        """
        Create a list of atoms to be rotated around a specified chi angle.
        Returns an empty list if wrong chi angle is requested.
        
        piotr 082008: This method should be rewritten in a way so it 
        traverses a molecular graph rather than uses a predefined 
        lists of atoms "excluded" and "included" from rotations.
        Current implementation only works for "proper" amino acids
        that have all atoms named properly and don't include any 
        non-standard atoms.
        
        @param which: chi angle (0=chi1, 1=chi2, and so on)
        @type which: int
        
        @return: list of atoms to be rotated for a specified chi angle
        """
        atom_list = []
        
        chi_atom_exclusion_list = self.get_chi_atom_exclusion_list(which)
        
        if chi_atom_exclusion_list:
            all_atom_list = self.get_atom_list()
            for atom in all_atom_list:
                if atom not in chi_atom_exclusion_list:
                    atom_list.append(atom)
                  
        return atom_list
    
    def lock(self):
        """
        Locks this residue (sets Rosetta mutation range to "native rotamer").      
        """
        self.set_mutation_range("NATRO")
        
    def set_chi_angle(self, which, angle):
        """
        Sets a specified chi angle of this amino acid. 
        
        @param which: chi angle (0=chi1, 1=chi2, and so on)
        @type which: int
        
        @param angle: value of the chi angle to be set
        @type angle:float
        
        @return: angle value if sucessfully completed, None if not
        """
        
        from geometry.VQT import norm, Q, V
        from math import pi, cos, sin
        
        chi_atom_list = self.get_chi_atom_list(which)
        if chi_atom_list:
            angle0 = self.calc_torsion_angle(chi_atom_list)
            dangle = angle - angle0
            if abs(dangle) > 0.0:
                vec = norm(chi_atom_list[2].posn() - chi_atom_list[1].posn())
                atom_list = self.get_atom_list_to_rotate(which)
                first_atom_posn = chi_atom_list[1].posn()
                for atom in atom_list:
                    pos = atom.posn() - first_atom_posn
                    
                    cos_a = cos(pi * (dangle / 180.0))
                    sin_a = sin(pi * (dangle / 180.0))
                    
                    q = V(0, 0, 0)
                    
                    # rotate the point around a vector
                    
                    q[0] += (cos_a + (1.0 - cos_a) * vec[0] * vec[0]) * pos[0];
                    q[0] += ((1.0 - cos_a) * vec[0] * vec[1] - vec[2] * sin_a) * pos[1];
                    q[0] += ((1.0 - cos_a) * 
                             vec[0] * vec[2] + vec[1] * sin_a) * pos[2];
                 
                    q[1] += ((1.0 - cos_a) * 
                             vec[0] * vec[1] + vec[2] * sin_a) * pos[0];
                    q[1] += (cos_a + (1.0 - cos_a) * vec[1] * vec[1]) * pos[1];
                    q[1] += ((1.0 - cos_a) * vec[1] * vec[2] - vec[0] * sin_a) * pos[2];
                 
                    q[2] += ((1.0 - cos_a) * vec[0] * vec[2] - vec[1] * sin_a) * pos[0];
                    q[2] += ((1.0 - cos_a) * vec[1] * vec[2] + vec[0] * sin_a) * pos[1];
                    q[2] += (cos_a + (1.0 - cos_a) * vec[2] * vec[2]) * pos[2];
    
                    q += first_atom_posn
                    
                    atom.setposn(q)
                    return angle
                
        return None
        
    def expand(self):
        """
        Expands a residue side chain.
        """
        
        self.expanded = True
        
    def collapse(self):
        """
        Collapse a residue side chain.
        """
        self.expanded = False
        
    def is_expanded(self):
        """
        Return True if side chain of this amino acid is expanded.
        """
        return self.expanded
    
    def set_color(self, color):
        """
        Sets a rotamer color for current amino acid.
        """
        self.color = color
        
    def set_backrub_mode(self, enable_backrub):
        """
        Sets Rosetta backrub mode (True or False).
        
        @param enable_backrub: should backrub mode be enabled for this residue
        @type enable_backrub: boolean
        """
        self.backrub = enable_backrub
        
    def get_backrub_mode(self):
        """ 
        Gets Rosetta backrub mode (True or False).
        
        @return: is backrub enabled for this residue (boolean)
        """
        return self.backrub
    
# End of Residue class.

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

