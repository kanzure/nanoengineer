# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

"""
Residue.py -- Residue class implementation.

Residue class stores information on individual amino acids of a protein
chain. 

@author: Piotr
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

piotr 082708: Re-factored the Residue class out of Protein.py file.

Renamed this class to "Residue" (which is a proper spelling, opposite 
to "Residuum", as Eric D has pointed out in his email).
"""

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
    'GLX':'Z' }

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
# a hydrogen bond pattern present, and are not helices nor strands.
# Currently, the turns are not used for visualization purposes in NE1.

SS_COIL = 0
SS_HELIX = 1
SS_STRAND = 2
SS_TURN = 3


# PDB atom name sets for chiral angles for amino acid side chains

CHI_ANGLES = { "GLY" : [ None, 
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
CHI_EXCLUSIONS = { "PHE" : [ [ "N", "H", "C", "O", "CA", "HA" ],
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

def calc_torsion_angle(atom_list):
    """
    Calculates torsional angle defined by four atoms, A1-A2-A3-A4,
    Return torsional angle value between atoms A2 and A3.
    
    @param atom_list: list of four atoms describing the torsion bond
    @type atom_list: list
    
    @return: value of the torsional angle (float)
    """
    # Note: this appears to be very general and perhaps ought to be moved to a more
    # general place (someday), perhaps VQT.py or nearby. [bruce 080828 comment]
    
    from numpy.oldnumeric import dot
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
     
    
class Residue:
    """
    This class implements a Residue object. The residue is an object
    describing an individual amino acid of a protein chain.
    """
    
    def __init__(self):
        """
        """
        # list of residue atoms in the same order as they occur in PDB file
        self.atom_list = []
        
        # dictionary for atom_name -> atom mapping
        self.atoms = {} 
        
        # amino acid secondary structure        
        self.secondary_structure = SS_COIL

        # True if the residue is expanded. The feature is used by "Edit
        # Rotamers" command for efficient rotamer manipulation in reduced
        # protein display style.
        self.expanded = False
        
        # Rotamer color, used by "Edit Protein" command.
        self.color = None
        
        # These Rosetta-related attributes should be probably moved from this
        # class to some Rosetta-related structure. For now, the Residue
        # and Protein classes include several methods created for Rosetta
        # purposes only.
        
        # Rosetta name of mutation range. 
        self.mutation_range = "NATAA"
        
        # Rosetta mutation descriptor. If set, it is usually a string of
        # 20 characters, corresponding to amino acid allowed at a given position.
        # Note: the descriptor is actually used by Rosetta only if mutation
        # range is set to "PIKAA". Otherwise, it is used only for informational
        # purposes. 
        self.mutation_descriptor = ""
        
        # True if this residue will be using backrub mode.
        self.backrub = False

    def get_atom_name(self, atom):
        """
        For a given PDB atom, return a corresponding atom name.
        """
        if atom.pdb_info and \
           atom.pdb_info.has_key('atom_name'):
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
        Return a first atom of the residue, or None.
        
        @note: this method will cause an exception if the residue is empty
        (has no atoms). This should never happen.
        
        """
        if len(self.atom_list):
            return self.atom_list[0]

        raise Exception("Residue object has no atoms")
        
    def get_atom_list(self):
        """
        Return a list of atoms for the residue.
        """
        return self.atom_list
    
    def get_side_chain_atom_list(self):
        """
        Return a list of side chain atoms for self. Assumes standard
        PDB atom names.
        """
        return [atom for atom in self.atom_list \
                if self.get_atom_name(atom) not in ['C', 'N', 'O', 'H', 'HA']]

    def get_three_letter_code(self):
        """
        Return a three-letter amino acid code (the residue name).
        
        This method returns "   " (a string composed of three spaces) 
        if there is no amino acid code assigned.
        
        @note: this method should probably scan all atoms looking for a 
        PDB residue key, not only the first one. For example, if a new atom
        is added to a residue, the method may not return a valid three-letter 
        code anymore. This could be a desired and expected behavior, but it is 
        not guaranteed in the current implementation. -- piotr 080902
        
        @return: amino acid three-letter name, or "   " if the name is unknown.
        """
        atom = self.get_first_atom()
        if atom and \
           atom.pdb_info:
            if atom.pdb_info.has_key('residue_name'):
                return atom.pdb_info['residue_name'][:3]
        
        return "   "

    def get_one_letter_code(self):
        """
        Return a one-letter amino acid code, or "X" if the residue code
        is not recognized.
        
        @note: see docstring in get_three_letter_code
        
        """
        if AA_3_TO_1.has_key(self.get_three_letter_code()):
            return AA_3_TO_1[self.get_three_letter_code()]
        
        return "X"
    
    def get_id(self):
        """
        Return a residue ID.
        
        The residue ID is a string representing the residue serial number 
        (integer value up to 9999) and concatenated residue insertion code 
        (single letter character). It is represented by a five character string.
        """
        # REVIEW: docstring should clarify whether serial number
        # is padded on left with ' ' or '0' (when less than 1000).
        # [bruce 080904 comment]
        atom = self.get_first_atom()
        
        if atom.pdb_info:
            if atom.pdb_info.has_key('residue_id'):
                return atom.pdb_info['residue_id']

        raise Exception("Residue has no ID")
    
    def get_index(self):
        """
        Return a residue index. The residue index is a numerical equivalent
        of a residue ID (less the insertion code) and is provided for user's
        convenience, i.e. when it is desired for the index to be used 
        independently from the residue insertion code. Also, see docstring
        in get_id.
        """
        # REVIEW: docstring of get_id suggests that residue_id will
        # have 4 chars for serial number and 1 char for insertion code.
        # But this makes use of the first 3 chars only.
        # Needs bugfix or explanation. [bruce 080904 comment]
        
        residue_id = self.get_id()
        
        return int(residue_id[:3])
    
    def has_atom(self, atom):
        """
        Check if the atom belongs to self. 
        
        @param atom: atom to be checked
        @type atom: Atom        
        
        @return: True if the atom belongs to self, False otherwise 
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
        Returns a residue atom for a given PDB atom name, or None if not found.
        The PDB name corresponds to the atom label as defined in PDB file.
        Peptide Builder can create proper atom labels.
        
        This intentionally and without a warning returns None if the atom 
        of a given name is not found. It is caller's responsibility 
        to handle such case properly. --piotr 080902
        
        @param name: name of the atom
        @type name: string
        
        @return: atom or None
        @rtype: Atom
        """
        if self.atoms.has_key(name):
            return self.atoms[name]
        else:
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
        return self.get_atom_by_name("CB")
    
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
        
        @return: backbone carbonyl group oxygen atom
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
        Gets a mutation range according to Rosetta definition.
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
    
    def get_chi_atom_list(self, which):
        """
        Create a list of four atoms for computing a given chi angle.
        Return an empty list if no such angle exists for self, or if
        residue name doesn't match one of the 20 standard amino acid names,
        or if the specified chi angle is out of allowed range (which is 0..3).
        
        @param which: chi angle (0=chi1, 1=chi2, and so on)
        @type which: int
        
        @return: list of four atoms, or empty list
        """
        if which in range(4):
            residue_name = self.get_three_letter_code()
            if CHI_ANGLES.has_key(residue_name):
                chi_list = CHI_ANGLES[residue_name]
                if chi_list[which]:
                    chi_atom_names = chi_list[which]
                    chi_atoms = []
                    for name in chi_atom_names:
                        atom = self.get_atom_by_name(name)
                        if atom:
                            chi_atoms.append(atom)
                    return chi_atoms
        
        return []
     
    def get_chi_atom_exclusion_list(self, which):
        """
        Creates a list of atoms excluded from rotation for a current amino acid.
        Returns an empty list if wrong chi angle is requested.
        
        @param which: chi angle (0=chi1, 1=chi2, and so on)
        @type which: int
        
        @return: list of atoms to be excluded from rotation
        """
        ex_atoms = []
        
        if which in range(4):
            residue_name = self.get_three_letter_code()
            if CHI_EXCLUSIONS.has_key(residue_name):
                chi_ex_list = CHI_EXCLUSIONS[residue_name]
                oxt_atom = self.get_atom_by_name("OXT")
                if oxt_atom:
                    ex_atoms.append(oxt_atom)
                for w in range(0, which + 1):
                    if chi_ex_list[w]:
                        ex_atom_names = chi_ex_list[w]
                        for name in ex_atom_names:
                            atom = self.get_atom_by_name(name)
                            if atom:
                                ex_atoms.append(atom)
        return ex_atoms
     
    def get_chi_angle(self, which):
        """
        Computes the side-chain Chi angle. Returns None if the angle
        doesn't exist.
        
        @note: This method returns None if the chi angle doesn't exist.
        This is intentional and callers should be aware of it.
        
        @param which: chi angle (0=chi1, 1=chi2, and so on)
        @type which: int
        
        @return: value of the specified chi angle, or None
        """
        chi_atom_list = self.get_chi_atom_list(which)
        if chi_atom_list:
            return calc_torsion_angle(chi_atom_list)                  
        else:
            return None

    
    def get_atom_list_to_rotate(self, which):
        """
        Create a list of atoms to be rotated around a specified chi angle.
        Returns an empty list if wrong chi angle is requested, or if all
        atoms are going to be excluded.
        
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
        
        @note: this method intentionally returns None if it is not possible
        to set the specified chi angle
        
        @return: angle value if sucessfully completed, None if not
        """
        # Note: Eric M said he factored some intrinsic coordinate code
        # out of some other file to create a general function for that.
        # Is this also something that could use that function?
        # If so, it's enough for now to comment this saying so
        # rather than to actually refactor it. [bruce 080828 comment]
        #
        # piotr 080902 reply:
        # I think that is different than the internal-to-cartesian 
        # coordinate conversion. Perhaps the code Eric M re-factored from 
        # Peptide Builder could be adapted to be used for torsion angle
        # manipulations, but I think current implementation is more 
        # straightforward. The "rotate point around a vector" routine
        # should be split out, though (and perhaps an equivalent method
        # exists somewhere in the codebase).
        
        from geometry.VQT import norm, Q, V
        from math import pi, cos, sin
        
        # Get a list of atoms to rotate.
        chi_atom_list = self.get_chi_atom_list(which)
        
        if len(chi_atom_list) > 0:
            # Calculate a current chi torsion angle.
            angle0 = calc_torsion_angle(chi_atom_list)
            # Calculate a difference between the current angle and 
            # a requested chi angle.
            dangle = angle - angle0
            if abs(dangle) > 0.0:
                # Vector we are rotating about is the vector connecting 
                # two middle atoms of the chi angle atom list.
                vec = norm(chi_atom_list[2].posn() - chi_atom_list[1].posn())
                # Compute a list of atoms to rotate.
                atom_list = self.get_atom_list_to_rotate(which)
                
                first_atom_posn = chi_atom_list[1].posn()
                
                for atom in atom_list:
                    
                    # Move the origin to the first atom.
                    pos = atom.posn() - first_atom_posn
                    
                    cos_a = cos(pi * (dangle / 180.0))
                    sin_a = sin(pi * (dangle / 180.0))
                    
                    q = V(0, 0, 0)
                    
                    # Rotate the point around a vector
                    
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
    
                    # Move the origin back to the previous position
                    q += first_atom_posn
                    
                    # Set the atom position.
                    atom.setposn(q)
                    
            return angle
                
        return None
        
    def expand(self):
        """
        Expand a residue side chain.
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
        Set a rotamer color for current amino acid.
        """
        self.color = color
        
    def set_backrub_mode(self, enable_backrub):
        """
        Set Rosetta backrub mode (True or False).
        
        @param enable_backrub: should backrub mode be enabled for this residue
        @type enable_backrub: boolean
        """
        self.backrub = enable_backrub
        
    def get_backrub_mode(self):
        """ 
        Get Rosetta backrub mode (True or False).
        
        @return: is backrub enabled for this residue (boolean)
        """
        return self.backrub
    
    pass # end of class Residue

