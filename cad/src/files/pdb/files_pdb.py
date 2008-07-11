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
import foundation.env as env

from utilities.constants import gensym

from protein.model.Protein import Residuum, Protein

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

    def _finish_molecule():
        """
        Perform some operations after reading entire PDB chain:
          - rebuild (infer) bonds
          - rename molecule to reflect a chain ID
          - delete protein object if this is not a protein
          - append the molecule to the molecule list
        """
        
        if mol.atoms:                
            if numconects == 0:
                msg = orangemsg("PDB file has no bond info; inferring bonds")
                env.history.message(msg)
                # let user see message right away (bond inference can take significant 
                # time) [bruce 060620]
                env.history.h_update() 
                inferBonds(mol)
                
            mol.protein.set_chain_id(chainId)
            
            mol.name = mol.name.replace(".pdb","").lower() + chainId

            ### print "SEQUENCE = ", mol.protein.get_sequence_string()
            
            if mol.protein.count_c_alpha_atoms() == 0:
                # If there is no C-alpha atoms, consider the chunk 
                # not a protein.
                mol.protein = None
                    
            mollist.append(mol)
        else:
            env.history.message( redmsg( "Warning: Pdb file contained no atoms"))
            env.history.h_update() 
            
        
    fi = open(filename,"rU")
    lines = fi.readlines()
    fi.close()
    
    mollist = []

    # Lists of secondary structure tuples (res_id, chain_id) 
    helix = []
    sheet = []
    turn = []
    
    dir, nodename = os.path.split(filename)
    if not isInsert:
        #nodename, extension = os.path.splitext(nodename)
        assy.filename = filename
    
    ndix = {}
    mol = Chunk(assy, nodename)
    
    mol.protein = Protein()
    
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
            chainId = card[21]
            resIdStr = card[22:26].replace(" ", "")
            if resIdStr != "":
                resId = int(resIdStr)
            else:
                resId = 0
            resName = card[17:20]
            sym = card[77:78]
            
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
            
            # First, look at 77-78 field - it should include an element symbol.
            foundit = False
            try:
                PeriodicTable.getElement(sym)
            except:
                pass
            else:
                foundit = True
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
            a = Atom(sym, A(xyz), mol)
            ndix[n] = a
            
            mol.protein.add_pdb_atom(a, name4, resId, resName)
            
            # Assign secondary structure.            
            if (resId, chainId) in helix:
                mol.protein.assign_helix(resId)
            
            if (resId, chainId) in sheet:
                mol.protein.assign_strand(resId)
                
            #if (resId, chainId) in turn:
            #    mol.protein.set_turn(resId)
                
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
            # Finish current molecule.
            _finish_molecule()
            # Create a new molecule 
            mol = Chunk(assy, nodename)
            mol.protein = Protein()
            numconects = 0
            
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
    
    _finish_molecule()
    
    return mollist
    
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
    
    from protein.model.Protein import enableProteins
    
    if enableProteins:
        
        molecules  = _readpdb_new(assy, 
                        filename, 
                        isInsert = False, 
                        showProgressDialog = showProgressDialog,
                        chainId = chainId)
        if molecules:
            from dna.model.DnaGroup import DnaGroup
            from model.assembly import Group
            
            self.win.assy.part.ensure_toplevel_group()

            name = gensym("DnaGroup", assy) 
            
            dnaGroup = Group(name, assy, assy.part.topnode) 
            for mol in molecules:
                if mol is not None:
                    dnaGroup.addchild(mol)

            assy.addnode(dnaGroup)            
    else:
        mol  = _readpdb(assy, 
                        filename, 
                        isInsert = False, 
                        showProgressDialog = showProgressDialog,
                        chainId = chainId)
        
        if mol is not None:
            assy.addmol(mol)
    return
    
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
    

    from protein.model.Protein import enableProteins
    
    if enableProteins: # use new PDB reading code
        
        molecules  = _readpdb_new(assy, 
                        filename, 
                        isInsert = True, 
                        showProgressDialog = True,
                        chainId = chainId)
        if molecules:
            from dna.model.DnaGroup import DnaGroup
            from model.assembly import Group
            
            assy.part.ensure_toplevel_group()

            name = gensym("DnaGroup", assy) 
            
            dnaGroup = DnaGroup(name, assy, assy.part.topnode) 
            for mol in molecules:
                if mol is not None:
                    dnaGroup.addchild(mol)

            assy.addnode(dnaGroup)            
    else:
        mol  = _readpdb(assy, 
                        filename, 
                        isInsert = True, 
                        showProgressDialog = True,
                        chainId = chainId)
        if mol is not None:
            assy.addmol(mol)
    return

# Write a PDB ATOM record record.
# Copied (and modified) from chem.py Atom.writepdb method.
# piotr 080710

def writepdb_atom(atom, file, atomSerialNumber, atomName, chainId, resId, resName):
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
    # Column 1-6: "ATOM  " (str)
    atomRecord = "ATOM  "
    # Column 7-11: Atom serial number (int)
    atomRecord += "%5d" % atomSerialNumber
    # Column 12: Whitespace (str)
    atomRecord += "%1s" % space
    # Column 13-16 Atom name (str)
    # piotr 080710: moved Atom name to column 13
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
    # Column 23-26: Residue sequence number (int) *unused*.
    atomRecord += "%4d" % resId
    # Column 27: Code for insertion of residues (AChar) *unused*
    atomRecord += "%1s" % space
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
    # Column 55-60: Occupancy (float 6.2) *unused*
    atomRecord += "%6s" % space
    # Column 61-66: Temperature factor. (float 6.2) *unused*
    atomRecord += "%6s" % space
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
             excludeFlags = EXCLUDE_BONDPOINTS | EXCLUDE_HIDDEN_ATOMS
             ):
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

    from protein.model.Protein import enableProteins
    
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
        
    for mol in part.molecules:
        if mol.hidden:
            # Atoms and bonds of hidden chunks are never written.
            continue
        for a in mol.atoms.itervalues():
            if exclude(a):
                excluded += 1
                continue
            atomConnectList = []
            
            atomsTable[a.key] = atomSerialNumber
            if enableProteins:
                # piotr 080709 : Use more robust ATOM output code for Proteins.
                resId = 1
                resName = "UNK"
                atomName = a.element.symbol
                if mol.protein:
                    res = mol.protein.get_residuum(a)
                    if res:
                        resId = res.get_id()
                        resName = res.get_three_letter_code()
                        atomName = res.get_atom_name(a)
                writepdb_atom(a, f, atomSerialNumber, atomName, chr(chainIdChar), resId, resName)
            else:
                a.writepdb(f, atomSerialNumber, chr(chainIdChar))
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
            
            atomSerialNumber += 1
            if len(atomConnectList) > 1:
                connectLists.append(atomConnectList)
                # bruce 050318 comment: shouldn't we leave it out if 
                # len(atomConnectList) == 1?
                # I think so, so I'm doing that (unlike the previous code).

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
        f.write("TER   %5d          %1s\n" % (molnum, chr(chainIdChar)))

        molnum += 1
        chainIdChar += 1
        if chainIdChar > 126: # ASCII "~", end of PDB-acceptable chain chars
            chainIdChar = 32 # Rollover to ASCII " "
            
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
