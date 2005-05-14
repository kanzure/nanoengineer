# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
files_pdb.py -- reading and writing PDB files

$Id$

History: this was part of fileIO.py,
until bruce 050414 started splitting that
into separate modules for each file format.
"""

import os
from chunk import molecule
from chem import atom, bond_atoms
from string import capitalize
from elements import PeriodicTable, Singlet
from platform import fix_plurals
from HistoryWidget import redmsg
from VQT import A

def _readpdb(assy, filename, isInsert = False): #bruce 050322 revised method & docstring in several ways
    """Read a Protein DataBank-format file into a single new chunk, which is returned,
    unless there are no atoms in the file, in which case a warning is printed
    and None is returned. (The new chunk (if returned) is in assy, but is not
    yet added into any Group or Part in assy -- caller must do that.)
    Unless isInsert = True, set assy.filename to match the file we read,
    even if we return None.
    """
    fi = open(filename,"rU")
    lines = fi.readlines()
    fi.close() #bruce 050322 added fi.close
    
    dir, nodename = os.path.split(filename)
    if not isInsert:
        assy.filename = filename
    ndix = {}
    mol = molecule(assy, nodename)
        
    for card in lines:
        key = card[:6].lower().replace(" ", "")
        if key in ["atom", "hetatm"]:
            sym = capitalize(card[12:14].replace(" ", "").replace("_", ""))
            try:
                PeriodicTable.getElement(sym)
            except:
                #bruce 050322 replaced print with history warning,
                # and generalized exception from KeyError
                # (since a test reveals AssertionError is what happens)
                assy.w.history.message( redmsg( "Warning: Pdb file: unknown element %s in: %s" % (sym,card) ))
                ## print 'unknown element "',sym,'" in: ',card
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
                assy.w.history.message( redmsg( "Warning: Pdb file: can't find first atom in CONECT record: %s" % (card,) ))
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
                        assy.w.history.message( redmsg( "Warning: Pdb file: can't find atom %s in: %s" % (card[i:i+5], card) ))
                        continue
                    bond_atoms(a1, a2)
    #bruce 050322 part of fix for bug 433: don't return an empty chunk
    if not mol.atoms:
        assy.w.history.message( redmsg( "Warning: Pdb file contained no atoms"))
        return None
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
def writepdb(assy, filename):
    f = open(filename, "w")
    # Atom object's key is the key, the atomIndex is the value  
    atomsTable = {}
    # Each element of connectList is a list of atoms to be connected with the
    # 1st atom in the list, i.e. the atoms to write into a CONECT record
    connectList = []

    atomIndex = 1

    def exclude(atm): #bruce 050318
        "should we exclude this atom (and bonds to it) from the file?"
        return atm.element == Singlet

    excluded = 0
    for mol in assy.molecules:
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
            space = " "
            f.write("%16s" % space)
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

    f.write("END\n") #bruce 050318 added newline
    f.close()
    if excluded:
        msg = "Warning: excluded %d open bond(s) from saved PDB file; consider Hydrogenating and resaving." % excluded
        msg = fix_plurals(msg)
        assy.w.history.message( redmsg( msg))
    return # from writepdb

# end

