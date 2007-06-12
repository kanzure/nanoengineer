# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
files_pdb.py -- reading and writing PDB files

$Id$

History: this was part of fileIO.py,
until bruce 050414 started splitting that
into separate modules for each file format.

bruce 050901 used env.history in some places.

bruce 070410 added some hacks to read more pdb files successfully --
but they need review by someone who knows whether they're correct or not.
(I'll commit this to both branches, Qt3 & Qt4, since this file is presently
identical in both, so doing that should not cause a problem.)
"""

import os
from chunk import molecule
from chem import atom
from bonds import bond_atoms, inferBonds
from string import capitalize
from elements import PeriodicTable, Singlet
from platform import fix_plurals
from HistoryWidget import redmsg, orangemsg
from VQT import A, vlen
import env

def _readpdb(assy, filename, isInsert = False):
    """Read a Protein DataBank-format file into a single new chunk, which is returned,
    unless there are no atoms in the file, in which case a warning is printed
    and None is returned. (The new chunk (if returned) is in assy, but is not
    yet added into any Group or Part in assy -- caller must do that.)
    Unless isInsert = True, set assy.filename to match the file we read,
    even if we return None.
    """
    fi = open(filename,"rU")
    lines = fi.readlines()
    fi.close()
    
    dir, nodename = os.path.split(filename)
    if not isInsert:
        assy.filename = filename
    ndix = {}
    mol = molecule(assy, nodename)
    numconects = 0

    atomname_exceptions = {
        "HB":"H", #k these are all guesses -- I can't find this documented anywhere [bruce 070410]
        ## "HE":"H", ### REVIEW: I'm not sure about this one -- leaving it out means it's read as Helium,
        # but including it erroneously might prevent reading an actual Helium if that was intended.
        # Guess for now: include it for ATOM but not HETATM. (So it's specialcased below, rather than
        # being included in this table.)
        "HN":"H",
     }

    for card in lines:
        key = card[:6].lower().replace(" ", "")
        if key in ["atom", "hetatm"]:
            ## sym = capitalize(card[12:14].replace(" ", "").replace("_", "")) 
            #bruce 070410 revised this to also discard digits, handle HB, HE, HN (guesses)
            atomname = card[12:14] # column numbers 13-14 in pdb format
                # (though full atom name is 13-16; see http://www.wwpdb.org/documentation/format2.3-0108-us.pdf page 156)
            for bad in "_ 0123456789":
                atomname = atomname.replace(bad, "")
            atomname = atomname_exceptions.get(atomname, atomname)
            if atomname == "HE" and key == "atom":
                atomname = "H" # see comment in atomname_exceptions
            sym = capitalize(atomname) 
            try:
                PeriodicTable.getElement(sym)
            except:
                # note: this typically fails with AssertionError (not e.g. KeyError) [bruce 050322]
                msg = "Warning: Pdb file: unknown element %s in: %s" % (sym,card)
                print msg #bruce 070410 added this print
                env.history.message( redmsg( msg ))

                ##e It would probably be better to create a fake atom, so the CONECT records would still work.
                # Better still might be to create a fake element, so we could write out the pdb file again
                # (albeit missing lots of info). [bruce 070410 comment]
                
                # Note: an advisor tells us:
                #   PDB files sometimes encode atomtypes,
                #   using C_R instead of C, for example, to represent sp2 carbons.
                # That particular case won't trigger this exception, since we only look at 2 characters,
                # i.e. C_ in that case. It would be better to realize this means sp2
                # and set the atomtype here (and perhaps then use it when inferring bonds,
                # which we do later if the file doesn't have any bonds). [bruce 060614/070410 comment]
            else:
                xyz = map(float, [card[30:38],card[38:46],card[46:54]])
                n = int(card[6:11])
                a = atom(sym, A(xyz), mol)
                ndix[n] = a
        elif key == "conect":
            try:
                a1 = ndix[int(card[6:11])]
            except:
                #bruce 050322 added this level of try/except and its message;
                # see code below for at least two kinds of errors this might catch,
                # but we don't try to distinguish these here. BTW this also happens
                # as a consequence of not finding the element symbol, above,
                # since atoms with unknown elements are not created.
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
    #bruce 050322 part of fix for bug 433: don't return an empty chunk
    if not mol.atoms:
        env.history.message( redmsg( "Warning: Pdb file contained no atoms"))
        return None
    if numconects == 0:
        env.history.message(orangemsg("PDB file has no bond info; inferring bonds"))
        env.history.h_update() # let user see message right away (bond inference can take significant time) [bruce 060620]
        inferBonds(mol)
    return mol
    
# read a Protein DataBank-format file into a single molecule
#bruce 050322 revised this for bug 433
def readpdb(assy,filename):
    """Reads a pdb file"""
    mol  = _readpdb(assy, filename, isInsert = False)
    if mol is not None:
        assy.addmol(mol)
    return
    
# Insert a Protein DataBank-format file into a single molecule
#bruce 050322 revised this for bug 433
def insertpdb(assy,filename):
    """Reads a pdb file and inserts it into the existing model """
    mol  = _readpdb(assy, filename, isInsert = True)
    if mol is not None:
        assy.addmol(mol)
    return

# Write all molecules into a Protein DataBank-format file
# [bruce 050318 revised comments, and made it not write singlets or their bonds,
#  and made it not write useless 1-atom CONECT records, and include each bond
#  in just one CONECT record instead of two.]

# PDB exclude flags, used by writepdb() and its callers. 
# Ask Bruce what "constants" file these should be moved to.
# Mark 2007-06-11
writeAllAtoms = 0
excludeSinglets = 1
excludeHiddenAtoms = 2 # excludes both hidden and invisible atoms.
excludePAM5Atoms = 4

def writepdb(part, filename, excludeFlags=excludeSinglets|excludeHiddenAtoms):
    """Write <part> into a new PDB file <filename>.
    
    <part> - the part.
    
    <filename> - the fullpath of the PDB file. 
                 We don't care if it has the .pdb extension or not.
    
    <excludeFlags> used to exclude certain atoms from being written, where:
    
        writeAllAtoms = 0 (even writes hidden and invisble atoms)
        excludeSinglets = 1 (excludes bondpoints)
        excludeHiddenAtoms = 2 (excludes both hidden and invisible atoms)
        excludePAM5Atoms = 4 (excludes PAM-5 pseudo atoms)
    """

    # PDB File Format available at http://www.rcsb.org/pdb/static.do?p=file_formats/pdb/index.html
    
    f = open(filename, "w") # doesn't yet detect errors in opening file [bruce 050927 comment]
    
    # Atom object's key is the key, the atomIndex is the value  
    atomsTable = {}
    # Each element of connectList is a list of atoms to be connected with the
    # 1st atom in the list, i.e. the atoms to write into a CONECT record
    connectList = []

    atomIndex = 1

    def exclude(atm): #bruce 050318
        """Exclude this atom (and bonds to it) from the file under the following conditions:
        - if it is a singlet
        - if it is not visible
        - if it is a member of a hidden chunk (molecule)
        """
        # Added not visible and hidden member of chunk. This effectively deletes these atoms, which might be considered a bug.
        # Suggested solutions:
        # - if the current file is a PDB and has hidden atoms/chunks, warn user before quitting NE1 (suggest saving as MMP).
        # - do not support native PDB. Open PDBs as MMPs; only allow export of PDB.
        # Fixes bug 2329. Mark 070423
        
        if excludeFlags & excludeSinglets:
            if atm.element == Singlet: 
                return True # Exclude
        if excludeFlags & excludeHiddenAtoms:
            if not atm.visible() or atm.molecule.hidden:
                return True # Exclude
        if excludeFlags & excludePAM5Atoms:
            # PAM5 atoms begin at 200.
            if atm.element.eltnum >= 200:
                return True # Exclude
        return False # Don't exclude.

    excluded = 0
    molnum=1
    chainId = chr(96+molnum)
    space = " "
    
    for mol in part.molecules:
        molstr = "MOL" + str(molnum) + "\n"
        f.write(str(molstr))
        for a in mol.atoms.itervalues():
            if exclude(a):
                excluded += 1
                continue
            aList = []
            f.write("ATOM  ")
            f.write("%5d" % atomIndex)
            f.write("%3s" % a.element.symbol)
            pos = a.posn()
            fpos = (float(pos[0]), float(pos[1]), float(pos[2])) 
            f.write("%7s" % space)
            f.write("%1s" % chainId.upper()) # Chain identifier - single letter in column 22. 
                # This has been tested with 35 chunks and still works in QuteMol. Mark 070430.
            f.write("%8s" % space)
            f.write("%8.3f%8.3f%8.3f" % fpos)

            atomsTable[a.key] = atomIndex
            aList.append(a)
            for b in a.bonds:
                a2 = b.other(a)
                if a2.key in atomsTable:
                    assert not exclude(a2) # see comment below
                    aList.append(a2)
                #bruce 050318 comment: the old code wrote every bond twice
                # (once from each end). I doubt we want that, so now I only
                # write them from the 2nd-seen end. (This also serves to
                # not write bonds to excluded atoms, without needing to check
                # that directly. The assert verifies this claim.)

            atomIndex += 1
            if len(aList) > 1:
                connectList.append(aList)
                #bruce 050318 comment: shouldn't we leave it out if len(aList) == 1?
                # I think so, so I'm doing that (unlike the previous code).

            f.write("\n")
            
        for aList in connectList:
            f.write("CONECT")
            for a in aList:
                index = atomsTable[a.key]
                f.write("%5d" % index)
            f.write("\n")
            
        connectList = []
        molnum+=1
        chainId = chr(96+molnum)

        f.write("END\n")
    
    f.close()
    
    if excluded:
        msg = "Warning: excluded %d open bond(s) from saved PDB file; consider Hydrogenating and resaving." % excluded
        msg = fix_plurals(msg)
        env.history.message( orangemsg( msg))
    return # from writepdb

# end

