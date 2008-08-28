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
# a hydrogen bond pattern present, and are not helices nor strands.
# Currently, the turns are not used for visualization purposes in NE1.

SS_COIL = 0
SS_HELIX = 1
SS_STRAND = 2
SS_TURN = 3


# PDB atom name sets for chiral angles for amino acid side chains

# REVIEW: if this is a constant, its name should be CHI_ANGLES

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
        # REVIEW: id is the name of a Python builtin, so it should not be
        # used for local variables. Doing so will work, but will cause bugs
        # if someone doesn't notice it when adding new code such as
        # print "%#x" % id(something).
        # [bruce 080828 comment]
        
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
        # REVIEW: that comment appears truncated.
        
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

    def get_atom_name(self, atom): # REVIEW: docstring has input & output backwards.
        """
        For a given PDB atom name, return a corresponding atom.
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
                if self.get_atom_name(atom) not in ['C', 'N', 'O', 'H', 'HA']]

    def get_three_letter_code(self):
        """
        Return a three-letter amino acid code (the residue name).
        """
        atom = self.get_first_atom()
        if atom and \
           atom.pdb_info:
            if atom.pdb_info.has_key('residue_name'):
                return atom.pdb_info['residue_name'][:3]
        return None

    def get_name(self):
        """
        Just another version of get_three_letter_code.
        """
        # REVIEW: if it's good to have both versions,
        # it is probably because they have different descriptions or "contracts"
        # even though they have the same implementation.
        # If so, this docstring should describe what this method is for,
        # and add a @note that it behaves identically to get_three_letter_code
        # if that is interesting to callers. (The method name could also usefully
        # be more specific.)
        # If not, it's probably best to pick one method name and only use that one.
        # [bruce 080828 comment]
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
        if atom and \
           atom.pdb_info:
            if atom.pdb_info.has_key('residue_id'):
                return atom.pdb_info['residue_id']

        return None
    
    def get_index(self):
        """
        Return a residue index.
        """
        # REVIEW: either the docstring or a comment should explain
        # why this has almost (but not quite) the same implementation
        # as get_id. (Otherwise, a reviewer can wonder whether that's
        # intentional.)
        # Also the docstring should say a bit more about what this is for.
        # [bruce 080828 comment]
        atom = self.get_first_atom()
        if atom and \
           atom.pdb_info:
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
        # REVIEW: docstring should be more specific about what kind of name this is about.
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
        # REVIEW: docstring or comment should explain why this is
        # implemented identically to get_c_alpha_atom.
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
        # REVIEW: is carbonyly a typo?
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
        # REVIEW: this doesn't use self; it should probably be a function, not a method.
        # Also, it appears to be very general and ought to be moved to a more
        # general place (someday), perhaps VQT.py or nearby. [bruce 080828 comment]
        
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
        # REVIEW: the docstring claims this returns a list of four atoms,
        # but in fact the code appears to be able to return a shorter list.
        # Should the code check for that, and return None instead?
        # If not, explain why not in a comment.
        # Also, the "@return" part doesn't document the None return value,
        # and the general description seems to give a smaller set of
        # conditions for returning None than the code apperas to have.
        # [bruce 080828 comment]
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
                    # REVIEW: can this ever be [None]? If so, is that ok?
                    # If so, docstring should say so.
                    # Also, some of the same comments as for get_chi_atom_list
                    # apply here. [bruce 080828 comment]
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
        # REVIEW: Eric M said he factored some intrinsic coordinate code
        # out of some other file to create a general function for that.
        # Is this also something that could use that function?
        # If so, it's enough for now to comment this saying so
        # rather than to actually refactor it. [bruce 080828 comment]
        
        from geometry.VQT import norm, Q, V
        from math import pi, cos, sin
        
        # Get a list of atoms to rotate.
        chi_atom_list = self.get_chi_atom_list(which)
        if chi_atom_list:
            # Calculate a current chi torsion angle.
            angle0 = self.calc_torsion_angle(chi_atom_list)
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
    
    pass # end of class Residue

