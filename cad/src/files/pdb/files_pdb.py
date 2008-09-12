# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
files_pdb.py -- reading and writing PDB files

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

This was part of fileIO.py,
until bruce 050414 started splitting that
into separate modules for each file format.

bruce 070410 added some hacks to read more pdb files successfully --
but they need review by someone who knows whether they're correct or not.
(I'll commit this to both branches, Qt3 & Qt4, since this file is presently
identical in both, so doing that should not cause a problem.)
"""

import os, time
from model.chunk import Chunk
from model.chem import Atom
from model.bonds import bond_atoms
from operations.bonds_from_atoms import inferBonds
from string import capitalize
from model.elements import PeriodicTable, Singlet
from platform_dependent.PlatformDependent import fix_plurals
from utilities.Log import redmsg, orangemsg
from geometry.VQT import A
from utilities.version import Version
from utilities.debug_prefs import debug_pref, Choice_boolean_False
from datetime import datetime
from model.Comment import Comment
from foundation.Group import Group

import foundation.env as env

from utilities.constants import gensym

from protein.model.Protein import Protein
from protein.model.Residue import Residue

def _readpdb(assy, 
             filename, 
             isInsert = False, 
             showProgressDialog = False, 
             chainId = None):
    """
    Read a Protein DataBank-format file into a single new chunk, which is 
    returned unless there are no atoms in the file, in which case a warning
    is printed and None is returned. (The new chunk (if returned) is in assy,
    but is not yet added into any Group or Part in assy -- caller must do that.)
    Unless isInsert = True, set assy.filename to match the file we read,
    even if we return None.
    
    @param assy: The assembly.
    @type  assy: L{assembly}
    
    @param filename: The PDB filename to read.
    @type  filename: string
    
    @param isInsert: If True, the PDB file will be inserted into the current
                     assembly. If False (default), the PDB is opened as the 
                     assembly.
    @param isInsert: boolean
    
    @param showProgressDialog: if True, display a progress dialog while reading
                               a file.
    @type  showProgressDialog: boolean
    
    @return: A chunk containing the contents of the PDB file.
    @rtype:  L{Chunk}
    
    @see: U{B{PDB File Format}<http://www.wwpdb.org/documentation/format23/v2.3.html>}
    """
        
    fi = open(filename,"rU")
    lines = fi.readlines()
    fi.close()
    
    dir, nodename = os.path.split(filename)
    if not isInsert:
        assy.filename = filename
    ndix = {}
    mol = Chunk(assy, nodename)
    numconects = 0

    atomname_exceptions = {
        "HB":"H", #k these are all guesses -- I can't find this documented 
                  # anywhere [bruce 070410]
        ## "HE":"H", ### REVIEW: I'm not sure about this one -- 
                    ###          leaving it out means it's read as Helium,
        # but including it erroneously might prevent reading an actual Helium 
        # if that was intended.
        # Guess for now: include it for ATOM but not HETATM. (So it's 
        # specialcased below, rather than being included in this table.)
        # (Later: can't we use the case of the 'E' to distinguish it from He?)
        "HN":"H",
     }
    
    # Create and display a Progress dialog while reading the MMP file. 
    # One issue with this implem is that QProgressDialog always displays 
    # a "Cancel" button, which is not hooked up. I think this is OK for now,
    # but later we should either hook it up or create our own progress
    # dialog that doesn't include a "Cancel" button. --mark 2007-12-06
    if showProgressDialog:
        _progressValue = 0
        _progressFinishValue = len(lines)
        win = env.mainwindow()
        win.progressDialog.setLabelText("Reading file...")
        win.progressDialog.setRange(0, _progressFinishValue)
        _progressDialogDisplayed = False
        _timerStart = time.time()
    for card in lines:
        key = card[:6].lower().replace(" ", "")
        if key in ["atom", "hetatm"]:
            ## sym = capitalize(card[12:14].replace(" ", "").replace("_", "")) 
            # bruce 080508 revision (guess at a bugfix for reading NE1-saved
            # pdb files):
            # get a list of atomnames to try; use the first one we recognize.
            # Note that full atom name is in columns 13-16 i.e. card[12:16];
            # see http://www.wwpdb.org/documentation/format2.3-0108-us.pdf,
            # page 156. The old code only looked at two characters,
            # card[12:14] == columns 13-14, and discarded ' ' and '_',
            # and capitalized (the first character only). The code as I revised
            # it on 070410 also discarded digits, and handled HB, HE, HN
            # (guesses) using the atomname_exceptions dict.
            name4 = card[12:16].replace(" ", "").replace("_", "")
            name3 = card[12:15].replace(" ", "").replace("_", "")
            name2 = card[12:14].replace(" ", "").replace("_", "")
            def nodigits(name):
                for bad in "0123456789":
                    name = name.replace(bad, "")
                return name
            atomnames_to_try = [
                name4, # as seems best according to documentation
                name3,
                name2, # like old code
                nodigits(name4),
                nodigits(name3),
                nodigits(name2) # like code as revised on 070410
            ]
            foundit = False
            for atomname in atomnames_to_try:
                atomname = atomname_exceptions.get(atomname, atomname)
                if atomname == "HE" and key == "atom":
                    atomname = "H" # see comment in atomname_exceptions
                sym = capitalize(atomname) # turns either 'he' or 'HE' into 'He'
                try:
                    PeriodicTable.getElement(sym)
                except:
                    # note: this typically fails with AssertionError 
                    # (not e.g. KeyError) [bruce 050322]
                    continue
                else:
                    foundit = True
                    break
                pass
            if not foundit:
                msg = "Warning: Pdb file: will use Carbon in place of unknown element %s in: %s" \
                    % (name4, card)
                print msg #bruce 070410 added this print
                env.history.message( redmsg( msg ))

                ##e It would probably be better to create a fake atom, so the 
                # CONECT records would still work.
                #bruce 080508 let's do that:
                sym = "C"
                
                # Better still might be to create a fake element, 
                # so we could write out the pdb file again
                # (albeit missing lots of info). [bruce 070410 comment]
                
                # Note: an advisor tells us:
                #   PDB files sometimes encode atomtypes,
                #   using C_R instead of C, for example, to represent sp2 
                #   carbons.
                # That particular case won't trigger this exception, since we
                # only look at 2 characters [eventually, after trying more, as of 080508],
                # i.e. C_ in that case. It would be better to realize this means
                # sp2 and set the atomtype here (and perhaps then use it when
                # inferring bonds,  which we do later if the file doesn't have 
                # any bonds). [bruce 060614/070410 comment]

            # Now the element name is in sym.
            xyz = map(float, [card[30:38], card[38:46], card[46:54]] )
            n = int(card[6:11])
            a = Atom(sym, A(xyz), mol)
            ndix[n] = a            
        elif key == "conect":
            try:
                a1 = ndix[int(card[6:11])]
            except:
                #bruce 050322 added this level of try/except and its message;
                # see code below for at least two kinds of errors this might
                # catch, but we don't try to distinguish these here. BTW this 
                # also happens as a consequence of not finding the element 
                # symbol, above,  since atoms with unknown elements are not 
                # created.
                env.history.message( redmsg( "Warning: Pdb file: can't find first atom in CONECT record: %s" % (card,) ))
            else:
                for i in range(11, 70, 5):
                    try:
                        a2 = ndix[int(card[i:i+5])]
                    except ValueError:
                        # bruce 050323 comment:
                        # we assume this is from int('') or int(' ') etc;
                        # this is the usual way of ending this loop.
                        break
                    except KeyError:
                        #bruce 050322-23 added history warning for this,
                        # assuming it comes from ndix[] lookup.
                        env.history.message( redmsg( "Warning: Pdb file: can't find atom %s in: %s" % (card[i:i+5], card) ))
                        continue
                    bond_atoms(a1, a2)
                    numconects += 1
            
        if showProgressDialog: # Update the progress dialog.
            _progressValue += 1
            if _progressValue >= _progressFinishValue:
                win.progressDialog.setLabelText("Building model...")
            elif _progressDialogDisplayed:
                win.progressDialog.setValue(_progressValue)
            else:
                _timerDuration = time.time() - _timerStart
                if _timerDuration > 0.25: 
                    # Display progress dialog after 0.25 seconds
                    win.progressDialog.setValue(_progressValue)
                    _progressDialogDisplayed = True
    
    if showProgressDialog: # Make the progress dialog go away.
        win.progressDialog.setValue(_progressFinishValue) 
    
    #bruce 050322 part of fix for bug 433: don't return an empty chunk
    if not mol.atoms:
        env.history.message( redmsg( "Warning: Pdb file contained no atoms"))
        return None
    if numconects == 0:
        msg = orangemsg("PDB file has no bond info; inferring bonds")
        env.history.message(msg)
        # let user see message right away (bond inference can take significant 
        # time) [bruce 060620]
        env.history.h_update() 
        inferBonds(mol)
    return mol
    

# PDB atom types for proteins. Assumes that the remaining atom types
# have default hybridizations. 

PROTEIN_ATOM_TYPES = { 
    "ANY" : {
        "N"   : "sp2(graphitic)", # these atom types are common for all amino
        "C"   : "sp2",            # acids
        "O"   : "sp2" },
    "PHE" : {
        "CG"  : "sp2aro", # "sp2a" is an sp2 atom connected to another sp2a atom
        "CD1" : "sp2aro", # with an aromatic bond
        "CE1" : "sp2aro",
        "CZ"  : "sp2aro",
        "CE2" : "sp2aro",
        "CD2" : "sp2aro" },
    "GLU" : {
        "CD"  : "sp2",
        "OE1" : "sp2" },
    "GLN" : {
        "CD"  : "sp2",
        "OE1" : "sp2" },
    "ASP" : {
        "CG"  : "sp2",
        "OD1" : "sp2" },
    "ASN" : {
        "CG"  : "sp2",
        "OD1" : "sp2" },
    "TRP" : {
        "CG"  : "sp2",
        "CD1" : "sp2",
        "CE2" : "sp2aro",
        "CZ2" : "sp2aro",
        "CH2" : "sp2aro",
        "CZ3" : "sp2aro",
        "CE3" : "sp2aro",
        "CD2" : "sp2aro" },
    "TYR" : {
        "CG"  : "sp2aro",
        "CD1" : "sp2aro",
        "CE1" : "sp2aro",
        "CZ"  : "sp2aro",
        "CE2" : "sp2aro",
        "CD2" : "sp2aro" },
    "ARG" : {
        "CZ"  : "sp2",
        "NH2" : "sp2" },
    "HIS" : {
        "CG"  : "sp2",
        "CE1" : "sp2a", 
        "NE2" : "sp2a",      # Two "sp2s" atoms are connected with a bond 
        "CD2" : "sp2" } }    # of order 1. I introduced this temporary marker
                             # to describe conjugated double bond systems.
                             # If the one of the "a", "b", or "c" markers
                             # is specified, only the atoms sharing the
                             # same marker will be double-bonded.

# " DG", "DC", "DT", and " DA" names correspond to deoxynucleotides
# as defined in PDB format >= 3.0 
# Older versions didn't distinguish between RNA and DNA base names
# so both compounds used "  G", "  C", "  A", "  T" (and "  U" in case of
# RNA)
                             
NUCLEIC_ATOM_TYPES = {
    " DC" : {
        "P"   : "sp3(p)", # phosphate phosphorus
        "OP1" : "sp2(-.5)",  # and two negatively charged oxygens 
        "OP2" : "sp2(-.5)",
        "C2"  : "sp2a",
        "O2"  : "sp2a", 
        "C4"  : "sp2b",
        "N3"  : "sp2b",
        "C5"  : "sp2a",
        "C6"  : "sp2a" },
    " DG" : {
        "P"   : "sp3(p)",
        "OP1" : "sp2(-.5)",
        "OP2" : "sp2(-.5)",
        "C4"  : "sp2b",
        "C5"  : "sp2b", 
        "C8"  : "sp2a",
        "N7"  : "sp2a", 
        "C2"  : "sp2a",
        "N3"  : "sp2a", 
        "C6"  : "sp2c",
        "O6"  : "sp2c" },
    " DA" : {
        "P"   : "sp3(p)",
        "OP1" : "sp2(-.5)",
        "OP2" : "sp2(-.5)",
        "C2"  : "sp2a",
        "N3"  : "sp2a",
        "C6"  : "sp2b",
        "N1"  : "sp2b",
        "N4"  : "sp2b",
        "C4"  : "sp2c",
        "C5"  : "sp2c",
        "N7"  : "sp2a",
        "C8"  : "sp2a" },
    " DT" : {
        "P"   : "sp3(p)",
        "OP1" : "sp2(-.5)",
        "OP2" : "sp2(-.5)",
        "C5"  : "sp2a",
        "C6"  : "sp2a",
        "C4"  : "sp2b",
        "O4"  : "sp2b",
        "C2"  : "sp2a",
        "O2"  : "sp2a" },
    "  C" : {
        "P"   : "sp3(p)", 
        "O1P" : "sp2(-.5)",        
        "O2P" : "sp2(-.5)",
        "C2"  : "sp2a",
        "O2"  : "sp2a", 
        "C4"  : "sp2b",
        "N3"  : "sp2b",
        "C5"  : "sp2a",
        "C6"  : "sp2a" },
    "  G" : {
        "P"   : "sp3(p)",
        "O1P" : "sp2(-.5)",
        "O2P" : "sp2(-.5)",
        "C4"  : "sp2b",
        "C5"  : "sp2b", 
        "C8"  : "sp2a",
        "N7"  : "sp2a", 
        "C2"  : "sp2a",
        "N3"  : "sp2a", 
        "C6"  : "sp2c",
        "O6"  : "sp2c" },
    "  A" : {
        "P"   : "sp3(p)",
        "O1P" : "sp2(-.5)",
        "O2P" : "sp2(-.5)",
        "C2"  : "sp2a",
        "N3"  : "sp2a",
        "C6"  : "sp2b",
        "N1"  : "sp2b",
        "N4"  : "sp2b",
        "C4"  : "sp2c",
        "C5"  : "sp2c",
        "N7"  : "sp2a",
        "C8"  : "sp2a" },
    "  T" : {
        "P"   : "sp3(p)",
        "O1P" : "sp2(-.5)",
        "O2P" : "sp2(-.5)",
        "C5"  : "sp2a",
        "C6"  : "sp2a",
        "C4"  : "sp2b",
        "O4"  : "sp2b",
        "C2"  : "sp2a",
        "O2"  : "sp2a" },
    }


# Important notes: (piotr 080909)
#
# - the PDB reading code can read standard Protein Data Bank files and preserve
# ATOM and HETATM record information, so the molecules can be exported as PDB
# and recognized by other programs
#
# - not all information contained in PDB files is preserved, only per-atom fields  
#
# - only first model is read from multi-model files,
# 
# - "Heteroatoms" group is created in Model Tree even if there are no heteroatoms
#
# - inferBonds method is used to rebuild bonds for proteins and DNA. This should
# be replaced by bond assignment using pattern matching. Currently, only 
# proper bond orders are assigned for standard residues, but connectivity
# is computed using the inferBonds method.
# 
# - PAM3 and PAM5 models can be written and read using the new code,
# although - as it was before - the internal DNA representation is not preserved
# 
# - the old PDB I/O code still remains there, and will be used if ENABLE_PROTEINS
# debug pref is set to False (perhaps this behavior should be controlled by
# another debug pref)

def _readpdb_new(assy, 
             filename, 
             isInsert = False, 
             showProgressDialog = False, 
             chainId = None):
    """
    Read a Protein DataBank-format file into a single new chunk, which is 
    returned unless there are no atoms in the file, in which case a warning
    is printed and None is returned. (The new chunk (if returned) is in assy,
    but is not yet added into any Group or Part in assy -- caller must do that.)
    Unless isInsert = True, set assy.filename to match the file we read,
    even if we return None.
    
    @param assy: The assembly.
    @type  assy: L{assembly}
    
    @param filename: The PDB filename to read.
    @type  filename: string
    
    @param isInsert: If True, the PDB file will be inserted into the current
                     assembly. If False (default), the PDB is opened as the 
                     assembly.
    @param isInsert: boolean
    
    @param showProgressDialog: if True, display a progress dialog while reading
                               a file.
    @type  showProgressDialog: boolean
    
    @return: A chunk containing the contents of the PDB file.
    @rtype:  L{Chunk}
    
    @see: U{B{PDB File Format}<http://www.wwpdb.org/documentation/format23/v2.3.html>}
    """

    # These methods should be probably moved to this file.
    from protein.model.Protein import is_water, is_amino_acid, is_nucleotide
    
    def _add_bondpoints(mol):
        """
        Adds missing bondpoints to a molecule.
        
        @param mol: molecule
        @type mol: Chunk
        """
        atlist = [atom for (key, atom) in mol.atoms.items()]
        for atom in atlist:
            atom.make_enough_bondpoints()

    def _set_atom_type(atom, atom_name, res_name):
        """
        Assigns an atom type based on atom name and residue name by
        simple name pattern matching.
        
        @param atom_name: PDB name of the atom
        @type atom_name: string
        
        @param res_name: PDB residue name
        @type res_name: string
        """
        atom.setOverlayText(atom_name)
        _assigned = False
        ### print (res_name, atom_name)
        # Look for the atom type and set the type
        if PROTEIN_ATOM_TYPES.has_key(res_name):
            # Found a protein residue.
            atom_type_dict = PROTEIN_ATOM_TYPES[res_name]
            if atom_type_dict.has_key(atom_name):
                # Found the atom.
                atom_type = atom_type_dict[atom_name]
                if atom_type == "sp2a":
                    sp2a_atoms.append(atom)
                    atom_type = "sp2"
                if atom_type == "sp2c":
                    sp2c_atoms.append(atom)
                    atom_type = "sp2"
                if atom_type == "sp2b":
                    sp2b_atoms.append(atom)
                    atom_type = "sp2"
                if atom_type == "sp2aro":
                    aromatic_atoms.append(atom)
                    atom_type = "sp2"
                atom.set_atomtype_but_dont_revise_singlets(atom_type) 
                _assigned = True
        elif NUCLEIC_ATOM_TYPES.has_key(res_name):
            # Found a nucleic acid residue
            atom_type_dict = NUCLEIC_ATOM_TYPES[res_name]
            if atom_type_dict.has_key(atom_name):
                # Found the atom.
                atom_type = atom_type_dict[atom_name]
                if atom_type == "sp2a":
                    sp2a_atoms.append(atom)
                    atom_type = "sp2"
                if atom_type == "sp2b":
                    sp2b_atoms.append(atom)
                    atom_type = "sp2"
                if atom_type == "sp2c":
                    sp2c_atoms.append(atom)
                    atom_type = "sp2"
                atom.set_atomtype_but_dont_revise_singlets(atom_type) 
                _assigned = True            
        if not _assigned:
            # Look for common atom types (N, C, O)
            atom_type_dict = PROTEIN_ATOM_TYPES["ANY"]
            # For remaining residues, look at one of the standard atom types 
            if atom_type_dict.has_key(atom_name):
                atom_type = atom_type_dict[atom_name]
                atom.set_atomtype_but_dont_revise_singlets(atom_type) 
        
    def _finalize_molecule():
        """
        Performs some operations after reading the entire PDB chain:

        - rebuild (infer) bonds for protein and DNA chains
        - assigns proper bond orders for standard residues
        - renames molecule to reflect a chain ID
        - deletes the "protein" attribute if it is not a protein
        - appends the molecule to the molecule list
        """
        
        if mol == water:
            # Skip water, to be added to the mollist explicitly at the end.
            return
        
        if mol.atoms:  
            # Create a molecule name by concatenating PDB ID and chain ID
            mol.name = pdbid.lower() + chainId

            if mol.protein.count_c_alpha_atoms() == 0 and \
               not dont_split:
               # If there are C-alpha atoms and dont_split flag is not set, 
               # consider the chunk non-protein. 
                
                # Create a heteromolecule name
                mol.name = resName + '[' + resId.replace(' ','') + ']'
                
                hetgroup.addchild(mol)
            else:
                # For protein - infer the bonds anyway. This should be replaced
                # by a proper atom / bond type assignment, for example using 
                # the templates present in the Peptide Generator. piotr 081908
                inferBonds(mol)
                    
                aromatic_atom_list = []
                single_bonded_atom_list = []
                
                # This is a protein.
                # Assign proper atom types according to protein templates.
                # amino_acid_list = mol.protein.get_amino_acids() 
                #for aa in amino_acid_list:
                    
                # aromatic, single_bonded = set_protein_atom_type(atom, 
                                                                
                # Assign bond orders. piotr 081908
                from model.bond_constants import V_DOUBLE, V_AROMATIC, V_GRAPHITE

                # Inferring bond types
                for atom in mol.atoms.itervalues():
                    if atom.bonds:
                        for bond in atom.bonds:
                            atom1_type = bond.atom1.getAtomTypeName()
                            atom2_type = bond.atom2.getAtomTypeName()
                            if (atom1_type == "sp2" and 
                                atom2_type == "sp2"):
                                if (bond.atom1 in aromatic_atoms and 
                                    bond.atom2 in aromatic_atoms):
                                    bond.set_v6(V_AROMATIC)
                                elif ((bond.atom1 in sp2a_atoms and 
                                       bond.atom2 in sp2a_atoms) or 
                                      (bond.atom1 in sp2b_atoms and 
                                       bond.atom2 in sp2b_atoms) or 
                                      (bond.atom1 in sp2c_atoms and 
                                       bond.atom2 in sp2c_atoms) or 
                                      (bond.atom1 not in sp2a_atoms and
                                       bond.atom1 not in sp2b_atoms and
                                       bond.atom1 not in sp2c_atoms and
                                       bond.atom1 not in aromatic_atoms)):  
                                    bond.set_v6(V_DOUBLE)
                            # for phosphate P - charged oxygen bond: assign V_GRAPHITE
                            if ((atom1_type == "sp3(p)" and
                                 atom2_type == "sp2(-.5)") or 
                               ((atom2_type == "sp3(p)" and
                                 atom1_type == "sp2(-.5)"))):
                                bond.set_v6(V_GRAPHITE)
                                
                if mol.protein.count_c_alpha_atoms() == 0:
                    # It is not a protein molecule: remove the protein information.
                    mol.protein = None
                else:
                    # Set the PDB information (chain ID and PDB code)
                    mol.protein.set_chain_id(chainId)
                    mol.protein.set_pdb_id(pdbid)
                
                # Add the molecule to mollist
                    mollist.append(mol)                
                    
                # Create bondpoints for easy hydrogenation
                _add_bondpoints(mol)                    
        else:
            env.history.message( redmsg( "Warning: PDB residue contained no atoms"))
            env.history.h_update() 
            pass
        
        pass # _finalize_molecule
    
    # Read the file contents.
    fi = open(filename,"rU")
    lines = fi.readlines()
    fi.close()

    assy.part.ensure_toplevel_group()

    aromatic_atoms = []
    sp2a_atoms = []
    sp2b_atoms = []
    sp2c_atoms = []

    # List of molecules read from PDB file.
    mollist = []

    # Lists of secondary structure tuples (res_id, chain_id) 
    helix = []
    sheet = []
    turn = []
    
    dir, nodename = os.path.split(filename)
    if not isInsert:
        assy.filename = filename
    
    # dictionary for HETATM connectivity reconstruction
    ndix = {}

    lastResId = None
    
    # Create a molecule chunk
    mol = Chunk(assy, nodename)
    mol.protein = Protein()
    dont_split = False

    hetgroup = Group("Heteroatoms", assy, assy.part.topnode) 

    # Create a chunk to store water molecules.
    water = Chunk(assy, nodename)
            
    numconects = 0
    
    comment_text = ""
    _read_rosetta_info = False
    comment_title = "PDB Header"
    
    # Create a temporary PDB ID - it should be later extracted from the
    # file header.
    pdbid = nodename.replace(".pdb","").lower()
    
    atomname_exceptions = {
        "HB":"H", #k these are all guesses -- I can't find this documented 
                  # anywhere [bruce 070410]
        "CA":"C",  
        "NE":"N",  
        "HG":"H",  
        ## "HE":"H", ### REVIEW: I'm not sure about this one -- 
                    ###          leaving it out means it's read as Helium,
        # but including it erroneously might prevent reading an actual Helium 
        # if that was intended.
        # Guess for now: include it for ATOM but not HETATM. (So it's 
        # specialcased below, rather than being included in this table.)
        # (Later: can't we use the case of the 'E' to distinguish it from He?)
        "HN":"H",
     }
    
    # Create and display a Progress dialog while reading the MMP file. 
    # One issue with this implem is that QProgressDialog always displays 
    # a "Cancel" button, which is not hooked up. I think this is OK for now,
    # but later we should either hook it up or create our own progress
    # dialog that doesn't include a "Cancel" button. --mark 2007-12-06
    if showProgressDialog:
        _progressValue = 0
        _progressFinishValue = len(lines)
        win = env.mainwindow()
        win.progressDialog.setLabelText("Reading file...")
        win.progressDialog.setRange(0, _progressFinishValue)
        _progressDialogDisplayed = False
        _timerStart = time.time()

    for card in lines:
        key = card[:6].lower().replace(" ", "")
        if key in ["atom", "hetatm"]:
            
            # Set _is_hetero flag for HETATM
            if key == "atom":
                _is_hetero = False
            else:
                _is_hetero = True
                
            ## sym = capitalize(card[12:14].replace(" ", "").replace("_", "")) 
            # bruce 080508 revision (guess at a bugfix for reading NE1-saved
            # pdb files):
            # get a list of atomnames to try; use the first one we recognize.
            # Note that full atom name is in columns 13-16 i.e. card[12:16];
            # see http://www.wwpdb.org/documentation/format2.3-0108-us.pdf,
            # page 156. The old code only looked at two characters,
            # card[12:14] == columns 13-14, and discarded ' ' and '_',
            # and capitalized (the first character only). The code as I revised
            # it on 070410 also discarded digits, and handled HB, HE, HN
            # (guesses) using the atomname_exceptions dict.
            name4 = card[12:16].replace(" ", "").replace("_", "")
            name3 = card[12:15].replace(" ", "").replace("_", "")
            name2 = card[12:14].replace(" ", "").replace("_", "")
            chainId = card[21]

            resId = card[22:26].replace(" ", "") + card[27]

            if lastResId == None:
                lastResId = resId
                
            resName = card[17:20]
            
            _is_water = is_water(resName)
            _is_amino_acid = is_amino_acid(resName)
            _is_nucleotide = is_nucleotide(resName)
            
            sym = card[77:79] # Element symbol

            alt = card[16] # Alternate location indicator
            
            if alt != ' ' and \
               alt != 'A':
                # Skip non-standard alternate location
                # This is not very safe test, it should preserve
                # the remaining atoms. piotr 080715 
                continue
            
###ATOM    131  CB  ARG A  18     104.359  32.924  58.573  1.00 36.93           C  

            def nodigits(name):
                for bad in "0123456789":
                    name = name.replace(bad, "")
                return name
            atomnames_to_try = [
                name4, # as seems best according to documentation
                name3,
                name2, # like old code
                nodigits(name4),
                nodigits(name3),
                nodigits(name2) # like code as revised on 070410
            ]
            
            # piotr 080819: first look at the 77-78 field - it should include 
            # the element symbol.
            foundit = False
            try:
                PeriodicTable.getElement(sym)
            except:
                pass
            else:
                foundit = True
            # if not found, look at possible atom names 
            if not foundit:
                for atomname in atomnames_to_try:
                    atomname = atomname_exceptions.get(atomname, atomname)
                    if atomname[0] == 'H' and key == "atom":
                        atomname = "H" # see comment in atomname_exceptions
                    
                    sym = capitalize(atomname) # turns either 'he' or 'HE' into 'He'
                    
                    try:
                        PeriodicTable.getElement(sym)
                    except:
                        # note: this typically fails with AssertionError 
                        # (not e.g. KeyError) [bruce 050322]
                        continue
                    else:
                        foundit = True
                        break
                    pass
            if not foundit:
                msg = "Warning: Pdb file: will use Carbon in place of unknown element %s in: %s" \
                    % (name4, card)
                print msg #bruce 070410 added this print
                env.history.message( redmsg( msg ))

                ##e It would probably be better to create a fake atom, so the 
                # CONECT records would still work.
                #bruce 080508 let's do that:
                sym = "C"
                
                # Better still might be to create a fake element, 
                # so we could write out the pdb file again
                # (albeit missing lots of info). [bruce 070410 comment]
                
                # Note: an advisor tells us:
                #   PDB files sometimes encode atomtypes,
                #   using C_R instead of C, for example, to represent sp2 
                #   carbons.
                # That particular case won't trigger this exception, since we
                # only look at 2 characters [eventually, after trying more, as of 080508],
                # i.e. C_ in that case. It would be better to realize this means
                # sp2 and set the atomtype here (and perhaps then use it when
                # inferring bonds,  which we do later if the file doesn't have 
                # any bonds). [bruce 060614/070410 comment]

            # Now the element name is in sym.
            xyz = map(float, [card[30:38], card[38:46], card[46:54]] )
            n = int(card[6:11])

            if resId != lastResId and \
               not _is_amino_acid and \
               not _is_nucleotide and \
               not _is_water:
                # Finalize current molecule.
                _finalize_molecule()
                
                # Discard the original molecule and create a new one. 
                mol = Chunk(assy, nodename)
                mol.protein = Protein()
                dont_split = False
            
            if _is_water:
                # If this is a water molecule, add the atom to the Water chunk
                a = Atom(sym, A(xyz), water)
            else:
                # Otherwise, add it to the current molecule.
                a = Atom(sym, A(xyz), mol)

            # Store PDB information in the Atom object pdb_info dict.
            if not a.pdb_info:
                # Create the pdb_info dictionary if it doesn't exist.
                a.pdb_info = {}
                
            # Store PDB atom properties in the pdb_info dict
            a.pdb_info['atom_name'] = name4
            a.pdb_info['residue_id'] = resId
            a.pdb_info['residue_name'] = resName
            a.pdb_info['chain_id'] = chainId
            
            if not _is_hetero:
                # The 'standard_atom' key represents a bool value set to
                # true if this atom is "standard PDB atom", e.g. it was
                # read from ATOM record.
                a.pdb_info['standard_atom'] = True
            
            # Normally, the connectivity information is only available 
            # for HETATM records. But other programs can write CONECT info 
            # for ATOM records, as well.             
            ndix[n] = a
            
            if _is_amino_acid or \
               _is_nucleotide:
                # Don't split proteins or nucleotides into individual 
                # residues. What about carbohydrates? piotr 081908
                dont_split = True
                
            if not _is_water:
                # Adds the atom to the "protein" chunk.
                mol.protein.add_pdb_atom(a, 
                                         name4, 
                                         resId, 
                                         resName,
                                         setType=True)
                
            if _is_amino_acid or \
               _is_nucleotide:
                # Recognize atom type by pattern matching of the atom name.
                # Do this only for proteins and nucleic acids.
                _set_atom_type(a, name4, resName)
                
            # Assign one of three types of secondary structure.            
            if (resId, chainId) in helix:
                # helix
                mol.protein.assign_helix(resId)
            
            if (resId, chainId) in sheet:
                # extended
                mol.protein.assign_strand(resId)
                
            if (resId, chainId) in turn:
                # turn 
                mol.protein.assign_turn(resId)
            
            # Remember the most recent resId
            lastResId = resId
            
        elif key == "conect":
            try:
                a1 = ndix[int(card[6:11])]
            except:
                #bruce 050322 added this level of try/except and its message;
                # see code below for at least two kinds of errors this might
                # catch, but we don't try to distinguish these here. BTW this 
                # also happens as a consequence of not finding the element 
                # symbol, above,  since atoms with unknown elements are not 
                # created.
                env.history.message( redmsg( "Warning: Pdb file: can't find first atom in CONECT record: %s" % (card,) ))
            else:
                for i in range(11, 70, 5):
                    try:
                        a2 = ndix[int(card[i:i+5])]
                    except ValueError:
                        # bruce 050323 comment:
                        # we assume this is from int('') or int(' ') etc;
                        # this is the usual way of ending this loop.
                        break
                    except KeyError:
                        #bruce 050322-23 added history warning for this,
                        # assuming it comes from ndix[] lookup.
                        env.history.message( redmsg( "Warning: Pdb file: can't find atom %s in: %s" % (card[i:i+5], card) ))
                        continue
                    bond_atoms(a1, a2)
                    numconects += 1
        
        elif key == "ter":
            # Finalize current molecule.
            _finalize_molecule()
            
            # Discard the original molecule and create a new one. 
            mol = Chunk(assy, nodename)
            mol.protein = Protein()
            dont_split = False
            ### numconects = 0
                        
        # HEADER, COMPND and REMARK fields are added to the comment text
        elif key == "header":
            # Extract PDB ID from the header string.
            pdbid = card[62:66].lower()
            comment_text += card
        
        elif key == "compnd":
            comment_text += card
        
        elif key == "remark":
            comment_text += card
            
        elif key == "model":
            # Check out the MODEL record, ignore everything other than MODEL 1.
            # This behavior should be optional and set via User Preference.
            # piotr 080714
            model_id = int(card[6:20])
            if model_id > 1:
                env.history.message( redmsg( "Warning: multi-model file; skipping remaining models."))
                env.history.h_update() 
                # Skip remaining part of the file.
                break
            
        elif key in ["helix", "sheet", "turn"]:
            # Read secondary structure information.
            if key == "helix":
                begin = int(card[22:25])
                end = int(card[34:37])
                chainId = card[19]
                for s in range(begin, end+1):
                    helix.append((s, chainId))            
            elif key == "sheet":
                begin = int(card[23:26])
                end = int(card[34:37])
                chainId = card[21]
                for s in range(begin, end+1):
                    sheet.append((s, chainId))            
            elif key == "turn":
                begin = int(card[23:26])
                end = int(card[34:37])
                chainId = card[19]
                for s in range(begin, end+1):
                    turn.append((s, chainId))            
        else:
            # Rosetta-written PDB files include scoring information.
            if card[7:15] == "ntrials:":
                _read_rosetta_info = True
                comment_text += "Rosetta Scoring Analysis\n"
            if card[9:15] == "score:":
                score = float(card[16:])
                comment_title = "Rosetta Score: %g" % score
            if _read_rosetta_info:
                comment_text += card
                
        if showProgressDialog: # Update the progress dialog.
            _progressValue += 1
            if _progressValue >= _progressFinishValue:
                win.progressDialog.setLabelText("Building model...")
            elif _progressDialogDisplayed:
                win.progressDialog.setValue(_progressValue)
            else:
                _timerDuration = time.time() - _timerStart
                if _timerDuration > 0.25: 
                    # Display progress dialog after 0.25 seconds
                    win.progressDialog.setValue(_progressValue)
                    _progressDialogDisplayed = True
    
    if showProgressDialog: # Make the progress dialog go away.
        win.progressDialog.setValue(_progressFinishValue) 
    
    _finalize_molecule()
    
    mollist.append(hetgroup)
        
    if water.atoms:
        # Rebuild bonds in case there are hydrogens present.
        inferBonds(water)
        # Add bondpoints.
        _add_bondpoints(water)
        
        # Check if there are any water molecules
        water.name = "Solvent"
        # The water should be hidden by default.
        water.hide()
        mollist.append(water)
        
    return (mollist, comment_text, comment_title)
    

# read oa Protein DataBank-format file or insert it into a single Chunk
# piotr 080715 refactored "read" and "insert" code so they both call
# this method instead having a redundant code (the only difference is
# "isInsert" parameter.
#bruce 050322 revised this for bug 433
def read_or_insert_pdb(assy, 
            filename, 
            showProgressDialog = False,
            chainId = None,
            isInsert = False):
    """
    Reads (loads) a PDB file, or inserts it into an existing chunk.
    
    @param assy: The assembly.
    @type  assy: L{assembly}
    
    @param filename: The PDB filename to read.
    @type  filename: string
    
    @param showProgressDialog: if True, display a progress dialog while reading
                               a file. Default is False.
    @type  showProgressDialog: boolean
    """
    
    from utilities.GlobalPreferences import ENABLE_PROTEINS
    
    if ENABLE_PROTEINS:
        molecules, comment_text, comment_title  = _readpdb_new(assy, 
                        filename, 
                        isInsert = isInsert, 
                        showProgressDialog = showProgressDialog,
                        chainId = chainId)
        if molecules:
            assy.part.ensure_toplevel_group()

            dir, name = os.path.split(filename)
            
            #name = gensym(nodename, assy) 
            
            group = Group(name, assy, assy.part.topnode) 
            for mol in molecules:
                if mol is not None:
                    group.addchild(mol)

            comment = Comment(assy, comment_title, comment_text)

            group.addchild(comment)
            
            assy.addnode(group)
            
    else:
        mol  = _readpdb(assy, 
                        filename, 
                        isInsert = isInsert, 
                        showProgressDialog = showProgressDialog,
                        chainId = chainId)
        
        if mol is not None:
            assy.addmol(mol)
    return
    

# read a Protein DataBank-format file into a single Chunk
#bruce 050322 revised this for bug 433
def readpdb(assy, 
            filename, 
            showProgressDialog = False,
            chainId = None):
    """
    Reads (loads) a PDB file.
    
    @param assy: The assembly.
    @type  assy: L{assembly}
    
    @param filename: The PDB filename to read.
    @type  filename: string
    
    @param showProgressDialog: if True, display a progress dialog while reading
                               a file. Default is False.
    @type  showProgressDialog: boolean
    """
    
    read_or_insert_pdb(assy, 
                       filename, 
                       showProgressDialog = showProgressDialog,
                       chainId = chainId,
                       isInsert = False)

    
# Insert a Protein DataBank-format file into a single Chunk
#bruce 050322 revised this for bug 433
def insertpdb(assy, 
              filename,
              chainId = None):
    """
    Reads a pdb file and inserts it into the existing model.
    
    @param assy: The assembly.
    @type  assy: L{assembly}
    
    @param filename: The PDB filename to read.
    @type  filename: string
    """
    
    read_or_insert_pdb(assy, 
                       filename, 
                       showProgressDialog = True,
                       chainId = chainId,
                       isInsert = True)


# Write a PDB ATOM record record.
# Copied and modified version of chem.py Atom.writepdb method.
# Should be moved back to Atom class as soon as we decided that the
# new implementation is satisfactory.
# piotr 080710

def writepdb_atom(atom, file, atomSerialNumber, atomName, chainId, resId, \
                  resName, hetatm, occup, temp):
    """
    Write a PDB ATOM record for the atom into I{file}.
    
    @param atom: The atom.
    @type  atom: Atom
    
    @param file: The PDB file to write the ATOM record to.
    @type  file: file
    
    @param atomSerialNumber: A unique number for this atom.
    @type  atomSerialNumber: int
    
    @param chainId: The chain id. It is a single character. See the PDB
                    documentation for the ATOM record more information.
    @type  chainId: str
    
    @note: If you edit the ATOM record, be sure to to test QuteMolX.
                
    @see: U{B{ATOM Record Format}<http://www.wwpdb.org/documentation/format23/sect9.html#ATOM>}
    """
    space = " "
    # Begin ATOM record ----------------------------------
    # Column 1-6: "ATOM  " (str) or "HETATM" depending on a type of atom
    if hetatm:
        atomRecord = "HETATM"
    else:
        atomRecord = "ATOM  "
    # Column 7-11: Atom serial number (int)
    atomRecord += "%5d" % atomSerialNumber
    # Column 12: Whitespace (str)
    atomRecord += "%1s" % space
    # Column 13-16 Atom name (str)
    # piotr 080710: moved Atom name to column 13
    if len(atomName) == 4:
        atomRecord += "%-4s" % atomName[:4]
    else:
        atomRecord += " %-3s" % atomName[:3]        
    # Column 17: Alternate location indicator (str) *unused*
    atomRecord += "%1s" % space
    # Column 18-20: Residue name - unused (str)
    atomRecord += "%3s" % resName
    # Column 21: Whitespace (str)
    atomRecord += "%1s" % space
    # Column 22: Chain identifier - single letter (str) 
    # This has been tested with 35 chunks and still works in QuteMolX.
    atomRecord += "%1s" % chainId.upper()
    # Column 23-27: Residue sequence number (int) + Code for insertion of residues (AChar) 
    atomRecord += "%5s" % resId
    # Column 28-30: Whitespace (str)
    atomRecord += "%3s" % space
    # Get atom XYZ coordinate
    _xyz = atom.posn()
    # Column 31-38: X coord in Angstroms (float 8.3)
    atomRecord += "%8.3f" % float(_xyz[0])
    # Column 39-46: Y coord in Angstroms (float 8.3)
    atomRecord += "%8.3f" % float(_xyz[1])
    # Column 47-54: Z coord in Angstroms (float 8.3)
    atomRecord += "%8.3f" % float(_xyz[2])
    # Column 55-60: Occupancy (float 6.2) - should be "1.0"
    atomRecord += "%6.2f" % occup
    # Column 61-66: Temperature factor. (float 6.2) *unused*
    atomRecord += "%6.2f" % temp
    # Column 67-76: Whitespace (str)
    atomRecord += "%10s" % space
    # Column 77-78: Element symbol, right-justified (str)
    atomRecord += "%2s" % atom.element.symbol[:2]
    # Column 79-80: Charge on the atom (str) *unused*
    atomRecord += "%2s\n" % space
    # End ATOM record ----------------------------------
    
    file.write(atomRecord)

    return


# Write all Chunks into a Protein DataBank-format file
# [bruce 050318 revised comments, and made it not write singlets or their bonds,
#  and made it not write useless 1-atom CONECT records, and include each bond
#  in just one CONECT record instead of two.]

# PDB exclude flags, used by writepdb() and its callers. 
# Ask Bruce what "constants" file these should be moved to (if any).
# Mark 2007-06-11
WRITE_ALL_ATOMS = 0
EXCLUDE_BONDPOINTS = 1
EXCLUDE_HIDDEN_ATOMS = 2 # excludes both hidden and invisible atoms.
EXCLUDE_DNA_ATOMS = 4
EXCLUDE_DNA_AXIS_ATOMS = 8
EXCLUDE_DNA_AXIS_BONDS = 16

def writepdb(part, 
             filename, 
             mode = 'w', 
             excludeFlags = EXCLUDE_BONDPOINTS | EXCLUDE_HIDDEN_ATOMS,
             singleChunk = None):
    """
    Write a PDB file of the I{part}.
    
    @param part: The part.
    @type  part: assembly
    
    @param filename: The fullpath of the PDB file to write. 
                     We don't care if it has the .pdb extension or not.
    @type  filename: string
                 
    @param mode: 'w' for writing (the default)
                 'a' for appending
    @type  mode: string
    
    @param excludeFlags: used to exclude certain atoms from being written, 
        where:
        WRITE_ALL_ATOMS = 0 (even writes hidden and invisble atoms)
        EXCLUDE_BONDPOINTS = 1 (excludes bondpoints)
        EXCLUDE_HIDDEN_ATOMS = 2 (excludes invisible atoms)
        EXCLUDE_DNA_ATOMS = 4 (excludes PAM3 and PAM5 pseudo atoms)
        EXCLUDE_DNA_AXIS_ATOMS = 8 (excludes PAM3 axis atoms)
        EXCLUDE_DNA_AXIS_BONDS = 16 (supresses PAM3 axis bonds)
    @type  excludeFlags: integer
    
    @note: Atoms and bonds of hidden chunks are never written.
    
    @see: U{B{PDB File Format}<http://www.wwpdb.org/documentation/format23/v2.3.html>}
    """

    if mode != 'a': # Precaution. Mark 2007-06-25
        mode = 'w'
    
    f = open(filename, mode) 
    # doesn't yet detect errors in opening file [bruce 050927 comment]
    
    # Atom object's key is the key, the atomSerialNumber is the value  
    atomsTable = {}
    # Each element of connectLists is a list of atoms to be connected with the
    # 1st atom in the list, i.e. the atoms to write into a CONECT record
    connectLists = []
    
    atomSerialNumber = 1

    from utilities.GlobalPreferences import ENABLE_PROTEINS
    
    def exclude(atm): #bruce 050318
        """
        Exclude this atom (and bonds to it) from the file under the following
        conditions (as selected by excludeFlags):
            - if it is a singlet
            - if it is not visible
            - if it is a member of a hidden chunk
            - some dna-related conditions (see code for details)
        """
        # Added not visible and hidden member of chunk. This effectively deletes
        # these atoms, which might be considered a bug.
        # Suggested solutions:
        # - if the current file is a PDB and has hidden atoms/chunks, warn user
        #   before quitting NE1 (suggest saving as MMP).
        # - do not support native PDB. Open PDBs as MMPs; only allow export of
        #   PDB.
        # Fixes bug 2329. Mark 070423
        
        if excludeFlags & EXCLUDE_BONDPOINTS:
            if atm.element == Singlet: 
                return True # Exclude
        if excludeFlags & EXCLUDE_HIDDEN_ATOMS:
            if not atm.visible():
                return True # Exclude
        if excludeFlags & EXCLUDE_DNA_AXIS_ATOMS:
##            if atm.element.symbol in ('Ax3', 'Ae3'):
            #bruce 080320 bugfix: revise to cover new elements and PAM5.
            if atm.element.role == 'axis':
                return True # Exclude
        if excludeFlags & EXCLUDE_DNA_ATOMS:
            # PAM5 atoms begin at 200.
            #
            # REVIEW: better to check atom.element.pam?
            # What about "carbon nanotube pseudoatoms"?
            # [bruce 080320 question]
            if atm.element.eltnum >= 200:
                return True # Exclude
        # Always exclude singlets connected to DNA p-atoms.
        if atm.element == Singlet: 
            for a in atm.neighbors():
                if a.element.eltnum >= 200:
                    # REVIEW: see above comment about atom.element.pam vs >= 200
                    return True
        return False # Don't exclude.

    excluded = 0
    molnum   = 1
    chainIdChar  = 65 # ASCII "A"
    
    if mode == 'w':
        writePDB_Header(f)
        
    # get a list of chunks in model tree order
    mollist = part.nodes_in_mmpfile_order(nodeclass = Chunk)
    
    for mol in mollist:
        if singleChunk:
            mol = singleChunk
        if mol.hidden:
            # Atoms and bonds of hidden chunks are never written.
            continue

        # write atoms in proper order 
        ordered_atoms = mol.atoms_in_mmp_file_order()
        
        for a in ordered_atoms:
            if exclude(a):
                excluded += 1
                continue
            atomConnectList = []
            atomsTable[a.key] = atomSerialNumber
            hetatm = True
            if ENABLE_PROTEINS:
                # piotr 080709 : Use more robust ATOM output code for Proteins.
                resId = "   1 "                        
                resName = "   "
                atomName = a.element.symbol
                hetatm = True
                occup = 1.0
                temp = 0.0
                
                if a.pdb_info:
                    if a.pdb_info.has_key('residue_id'):
                        resId = a.pdb_info['residue_id']
                    if a.pdb_info.has_key('residue_name'):
                        resName = a.pdb_info['residue_name']
                    if a.pdb_info.has_key('atom_name'):
                        atomName = a.pdb_info['atom_name']
                    if a.pdb_info.has_key('standard_atom'):
                        hetatm = False
                    if a.pdb_info.has_key('chain_id'):
                        chainIdChar = ord(a.pdb_info['chain_id'][0])
                    if a.pdb_info.has_key('occupancy'):
                        occup = a.pdb_info['occupancy']
                    if a.pdb_info.has_key('temperature_factor'):
                        temp = a.pdb_info['temperature_factor']    
                    
                writepdb_atom(a, 
                              f, 
                              atomSerialNumber, 
                              atomName, 
                              chr(chainIdChar), 
                              resId, 
                              resName,
                              hetatm,
                              occup,
                              temp)
            else:
                a.writepdb(f, atomSerialNumber, chr(chainIdChar))
                
            if hetatm:
                atomConnectList.append(a)
        
                for b in a.bonds:
                    a2 = b.other(a)
                    # The following removes bonds b/w PAM3 axis atoms.
                    if excludeFlags & EXCLUDE_DNA_AXIS_BONDS:
                        ##                    if a.element.symbol in ('Ax3', 'Ae3'):
                        ##                        if a2.element.symbol in ('Ax3', 'Ae3'):
                        ##                            continue
                        #bruce 080320 bugfix: revise to cover new elements and PAM5.
                        if a.element.role == 'axis' and a2.element.role == 'axis':
                                continue
                            
                    if a2.key in atomsTable:
                        assert not exclude(a2) # see comment below
                        atomConnectList.append(a2)
                    #bruce 050318 comment: the old code wrote every bond twice
                    # (once from each end). I doubt we want that, so now I only
                    # write them from the 2nd-seen end. (This also serves to
                    # not write bonds to excluded atoms, without needing to check
                    # that directly. The assert verifies this claim.)
                
                if len(atomConnectList) > 1:
                    connectLists.append(atomConnectList)
                    # bruce 050318 comment: shouldn't we leave it out if 
                    # len(atomConnectList) == 1?
                    # I think so, so I'm doing that (unlike the previous code).
    
            atomSerialNumber += 1
        
        # Write the chain TER-minator record
        #
        # COLUMNS     DATA TYPE         FIELD           DEFINITION
        # ------------------------------------------------------
        #  1 - 6      Record name       "TER     "
        #  7 - 11     Integer           serial          Serial number.
        # 18 - 20     Residue name      resName         Residue name.
        # 22          Character         chainID         Chain identifier.
        # 23 - 26     Integer           resSeq          Residue sequence number.
        # 27          AChar             iCode           Insertion code.
        
        # piotr 080908 note: This is not exactly correct, the TER record 
        # shouldn't be saved between consecutive non-standard residues 
        # (HETATM records), e.g. water molecules shouldn't be separated
        # by TER records.
        f.write("TER   %5d          %1s\n" % (molnum, chr(chainIdChar)))

        molnum += 1
        chainIdChar += 1
        if chainIdChar > 126: # ASCII "~", end of PDB-acceptable chain chars
            chainIdChar = 32 # Rollover to ASCII " "
        
        if singleChunk:
            break
        
    for atomConnectList in connectLists:
        # Begin CONECT record ----------------------------------
        f.write("CONECT")
        for a in atomConnectList:
            index = atomsTable[a.key]
            f.write("%5d" % index)
        f.write("\n")
        # End CONECT record ----------------------------------
        connectLists = []
            
    f.write("END\n")
    
    f.close()
    
    if excluded:
        msg  = "Warning: excluded %d open bond(s) from saved PDB file; " \
             % excluded
        msg += "consider Hydrogenating and resaving." 
        msg  = fix_plurals(msg)
        env.history.message( orangemsg(msg))
    return # from writepdb


def writePDB_Header(fileHandle):
    """
    Writes an informative REMARK 5 header at the top of the PDB file with the
    given fileHandle.
    
    @param fileHandle: The file to write into.
    @type  fileHandle: file
    """
    version = Version()
    fileHandle.write("REMARK   5\n")
    fileHandle.write("REMARK   5 Created %s"
        % (datetime.utcnow().strftime("%Y/%m/%d %I:%M:%S %p UTC\n")))
    fileHandle.write("REMARK   5 with NanoEngineer-1 version %s nanoengineer-1.com\n"
        % repr(version))
    fileHandle.write("REMARK   5")
    fileHandle.write("""
REMARK   6
REMARK   6 This file generally complies with the PDB format version 2.3
REMARK   6 Notes:
REMARK   6
REMARK   6 - Sets of atoms are treated as PDB chains terminated with TER
REMARK   6   records. Since the number of atom sets can exceed the 95 possible
REMARK   6   unique chains expressed in ATOM records by single non-control ASCII
REMARK   6   characters, TER record serial numbers will be used to uniquely
REMARK   6   identify atom sets/chains. Chain identifiers in ATOM records will
REMARK   6   "roll-over" after every 95 chains.
REMARK   6\n""")
