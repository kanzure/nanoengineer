# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
File IO functions for reading and writing PDB and MMP files

$Id$

===

Notes by bruce 050217 about mmp file format version strings:

Specific mmp format versions used so far:

[developers: maintain this list!]

<no mmpformat record> -- before 050130 (shortly before Alpha-1 released)

  (though the format had several versions before then,
   not all upward-compatible)

'050130' -- the mmpformat record, using this format-version "050130",
were introduced just before Alpha-1 release, at or shortly after
the format was changed so that two (rather than one) Csys records
were stored, one for Home View and one for Last View

'050130 required; 050217 optional' -- introduced by bruce on 050217,
when the info record was added.

===

General notes about when to change the mmp format version:
see a separate file, fileIO-doc.txt.

[bruce 050227 moved those notes out of this docstring and into that
new file, which is initially in the same directory as this file.]

"""

MMP_FORMAT_VERSION_TO_WRITE = '050130 required; 050217 optional'
    #bruce modified this to indicate required & ideal reader versions... see general notes above.

from Numeric import *
from VQT import *
from string import *
import re
from chem import *
from gadgets import *
from Utility import *
from povheader import povheader
from mdldata import *
from HistoryWidget import redmsg # bruce 050107
from elements import PeriodicTable

nampat = re.compile("\\(([^)]*)\\)")
old_csyspat = re.compile("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
new_csyspat = re.compile("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
datumpat = re.compile("datum \((.+)\) \((\d+), (\d+), (\d+)\) (.*) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)")
keypat = re.compile("\S+")
molpat = re.compile("mol \(.*\) (\S\S\S)")
atom1pat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
atom2pat = re.compile("atom \d+ \(\d+\) \(.*\) (\S\S\S)")

# Old Rotary Motor record format: 
# rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)
old_rmotpat = re.compile("rmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")

# New Rotary Motor record format: 
# rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az) length radius spoke_radius
new_rmotpat = re.compile("rmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) (-?\d+\.\d+)")

# Old Linear Motor record format: 
# lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
old_lmotpat = re.compile("lmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")

# New Linear Motor record format: 
# lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az) length width spoke_radius
new_lmotpat = re.compile("lmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) (-?\d+\.\d+)")

# ground (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}
grdpat = re.compile("ground \((.+)\) \((\d+), (\d+), (\d+)\)")

# stat (name) (r, g, b) (temp) first_atom last_atom boxed_atom
statpat = re.compile("stat \((.+)\) \((\d+), (\d+), (\d+)\) \((\d+)\)" )

# thermo (name) (r, g, b) first_atom last_atom boxed_atom
thermopat = re.compile("thermo \((.+)\) \((\d+), (\d+), (\d+)\)" )

def getname(str, default):
    x= nampat.search(str)
    if x: return x.group(1)
    return gensym(default)


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
                    mol.bond(a1, a2)
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
    if mol:
        assy.addmol(mol)
    return
    
# Insert a Protein DataBank-format file into a single molecule
#bruce 050322 revised this for bug 433
def insertpdb(assy,filename):
    """Reads a pdb file and inserts it into the existing model """
    mol  = _readpdb(assy, filename, isInsert = True)
    if mol:
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
        from platform import fix_plurals
        msg = "Warning: excluded %d open bond(s) from saved PDB file; consider Hydrogenating and resaving." % excluded
        msg = fix_plurals(msg)
        assy.w.history.message( redmsg( msg))
    return # from writepdb

def _addMolecule(mol, assy, group):
        """Make sure to call this function before any other record operation
        except for record types: atom, bond, shaft and csys, datum, walls,
        kelvin. This adds the previous molecule to its group.
        """
        group.addchild(mol) # bruce 050322: try just doing this; seems to work;
            # if no bugs are reported, we can probably do this at start of mol record
            # and remove the need for all the existing calls of this routine.
##        assy.addmol(mol)
##            #bruce 050321 suspects addmol is no longer needed
##            # (in fact I'm not even sure _addMolecule itself is still needed --
##            #  it might now be ok to just store the empty mol in the right group
##            #  when it's initially made; figure this out sometime. ###k)
##        mol.moveto(group)
        return None #bruce 050228

def _readmmp(assy, filename, isInsert = False):
    """The routine to actually reading a mmp file and save data
    into data structure"""
    #bruce 041011: added 'U' to file mode, for universal newline support.
    lines = open(filename,"rU").readlines()
    if not isInsert:
        assy.filename = filename
    mol = None # the current molecule being built, if any [bruce comment 050228]
    ndix = {}
##    assy.alist = [] # bruce 050325 removed this
    AddAtoms = True
    #assy.tree = Group("Root", assy, None)
    groupstack = [] #stack to store (group, name) tuples
    grouplist = []     #List of top level groups will be returned by the function
    opengroup = None #The only current group which can accept children
 
    for card in lines:
        key = keypat.match(card)
        if not key: continue
        key = key.group(0)
        
        if key == "group": # Group of Molecules and/or Groups
            ##Huaicai to fix bug 142---12/09/04
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
                    
            name = getname(card, "Grp")
            opengroup = Group(name, assy, opengroup)#assy.tree)
            if not groupstack: grouplist += [opengroup]
            
            #"opengroup" will be always at the top of "groupstack" 
            groupstack = [(opengroup, name)] + groupstack 

        elif key == "egroup": # Group of Molecules and/or Groups
            name = getname(card, "Grp")
            curgrp, curnam = groupstack[0]
            if name != curnam:
                print "mismatched group records:", name, curnam
                break
            if mol:
                mol = _addMolecule(mol, assy, curgrp)
            groupstack = groupstack[1:]
            if groupstack: opengroup, junk = groupstack[0]
            else: opengroup = None

        elif key=="mol":
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
            name = getname(card, "Mole")
            mol=molecule(assy,  name)
            disp = molpat.match(card)
            if disp:
                try: mol.setDisplay(dispNames.index(disp.group(1)))
                except ValueError: pass
            else:
                mol.setDisplay(diDEFAULT)

        elif key == "atom":
            m=atom1pat.match(card)
            if not m:
                print card
                
            n=int(m.group(1))
            sym=PeriodicTable.getElement(int(m.group(2))).symbol
            xyz=A(map(float, [m.group(3),m.group(4),m.group(5)]))/1000.0
            a = atom(sym, xyz, mol)
            disp = atom2pat.match(card)
            if disp:
                try: a.setDisplay(dispNames.index(disp.group(1)))
                except ValueError: pass
                    
##            if AddAtoms: 
##                assy.alist += [a]
            
            ndix[n]=a
            prevatom=a
            prevcard = card
            
        elif key == "bond1":
            list=map(int, re.findall("\d+",card[5:]))
            try:
                for a in map((lambda n: ndix[n]), list):
                    mol.bond(prevatom, a)
            except KeyError:
                print "error in MMP file: atom ", prevcard
                print card
                
        # Read the MMP record for a Rotary Motor as either:
        # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az) length, radius, spoke_radius
        # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)
        elif key == "rmotor":
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
            m = new_rmotpat.match(card) # Try to read card with new format
            if not m: m = old_rmotpat.match(card) # If that didn't work, read card with old format
            ngroups = len(m.groups()) # ngroups = number of fields found (12=old, 15=new)
            name = m.group(1)
            col=map(lambda (x): int(x)/255.0,
                    [m.group(2),m.group(3),m.group(4)])
            torq=float(m.group(5))
            sped=float(m.group(6))
            cxyz=A(map(float, [m.group(7),m.group(8),m.group(9)]))/1000.0
            axyz=A(map(float, [m.group(10),m.group(11),m.group(12)]))/1000.0
            if ngroups == 15: # if we have 15 fields, we have the length, radius and spoke radius.
                length = float(m.group(13))
                radius = float(m.group(14))
                sradius = float(m.group(15))
            else: # if not, set the default values for length, radius and spoke radius.
                length = 10.0
                radius = 2.0
                sradius = 0.5
            prevmotor=RotaryMotor(assy)
            prevmotor.setProps(name, col, torq, sped, cxyz, axyz, length, radius, sradius)
            opengroup.addmember(prevmotor)

        elif key == "shaft":
            list = map(int, re.findall("\d+",card[6:]))
            list = map((lambda n: ndix[n]), list)
            prevmotor.setShaft(list)
              
        # Read the MMP record for a Linear Motor as:
        # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az) length, width, spoke_radius
        # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
        elif key == "lmotor":
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
            m = new_lmotpat.match(card) # Try to read card with new format
            if not m: m = old_lmotpat.match(card) # If that didn't work, read card with old format
            ngroups = len(m.groups()) # ngroups = number of fields found (12=old, 15=new)
            name = m.group(1)
            col=map(lambda (x): int(x)/255.0,
                    [m.group(2),m.group(3),m.group(4)])
            force=float(m.group(5))
            stiffness=float(m.group(6))
            cxyz=A(map(float, [m.group(7),m.group(8),m.group(9)]))/1000.0
            axyz=A(map(float, [m.group(10),m.group(11),m.group(12)]))/1000.0
            if ngroups == 15: # if we have 15 fields, we have the length, width and spoke radius.
                length = float(m.group(13))
                width = float(m.group(14))
                sradius = float(m.group(15))
            else: # if not, set the default values for length, width and spoke radius.
                length = 10.0
                width = 2.0
                sradius = 0.5
            prevmotor=LinearMotor(assy)
            prevmotor.setProps(name, col, force, stiffness, cxyz, axyz, length, width, sradius)
            opengroup.addmember(prevmotor)

    # Read the MMP record for a Ground as:
    # ground (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}
    
        elif key == "ground":
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
            
            m=grdpat.match(card)
            name = m.group(1)
            col=map(lambda (x): int(x)/255.0,
                    [m.group(2),m.group(3),m.group(4)])

            # Read in the list of atoms
            card =card[card.index(")")+1:] # skip past the color field
            list = map(int, re.findall("\d+",card[card.index(")")+1:]))
            list = map((lambda n: ndix[n]), list)
            
            gr = Ground(assy, list) # create ground and set props
            gr.name=name
            gr.color=col
            opengroup.addmember(gr)

    # Read the MMP record for a Thermostat as:
    # stat (name) (r, g, b) (temp) first_atom last_atom box_atom
                
        elif key == "stat":
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
            
            m=statpat.match(card)
            name = m.group(1)
            col=map(lambda (x): int(x)/255.0,
                    [m.group(2),m.group(3),m.group(4)])
            temp=m.group(5)

            # Read in the list of atoms
            card =card[card.index(")")+1:] # skip past the color field
            card =card[card.index(")")+1:] # skip past the temp field
            list = map(int, re.findall("\d+",card[card.index(")")+1:]))
            
            # We want "list" to contain only the 3rd item, so let's remove 
            # first_atom (1st item) and last_atom (2nd item) in list.
            # They will get regenerated in the Thermo constructor.  
            # Mark 050129
            if len(list) > 2: del list[0:2]
            
            # Now remove everything else from the list except for the boxed_atom.
            # This would happen if we loaded an old part with more than 3 atoms listed.
            if len(list) > 1:
                del list[1:]
                msg = "Warning: a thermostat record was found (" + name + ") in the part which contained extra atoms.  They will be ignored."
                assy.w.history.message( redmsg(msg))
                
            list = map((lambda n: ndix[n]), list)

            sr = Stat(assy, list) # create stat and set props
            sr.name=name
            sr.color=col
            sr.temp=temp
            opengroup.addmember(sr)

    # Read the MMP record for a Thermometer as:
    # thermo (name) (r, g, b) first_atom last_atom box_atom
                
        elif key == "thermo":
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
            
            m=thermopat.match(card)
            name = m.group(1)
            col=map(lambda (x): int(x)/255.0,
                    [m.group(2),m.group(3),m.group(4)])

            # Read in the list of atoms
            card =card[card.index(")")+1:] # skip past the color field
            list = map(int, re.findall("\d+",card[card.index(")")+1:]))
            
            # We want "list" to contain only the 3rd item, so let's remove 
            # first_atom (1st item) and last_atom (2nd item) in list.
            # They will get regenerated in the Thermo constructor.  
            # Mark 050129
            if len(list) > 2: del list[0:2]
            
            # Now remove everything else from the list except for the boxed_atom.
            # This would happen if we loaded an old part with more than 3 atoms listed.
            if len(list) > 1:
                del list[1:]
                msg = "Warning: a thermometer record was found in the part which contained extra atoms.  They will be ignored."
                assy.w.history.message( redmsg(msg))
                
            list = map((lambda n: ndix[n]), list)

            sr = Thermo(assy, list) # create stat and set props
            sr.name=name
            sr.color=col
            opengroup.addmember(sr)
             
        elif key=="csys": # Coordinate System
            if not isInsert: #Skip this record if inserting
                ###Huaicai 1/27/05, new file format with home view 
                ### and last view information        
                m = new_csyspat.match(card)
                if m:        
                        name = m.group(1)
                        wxyz = A(map(float, [m.group(2), m.group(3),
                                 m.group(4), m.group(5)]))
                        scale=float(m.group(6))
                        pov = A(map(float, [m.group(7), m.group(8), m.group(9)]))
                        zoomFactor = float(m.group(10))
                        if (name == "HomeView"):
                                assy.homeCsys = Csys(assy, name, scale, pov, zoomFactor, wxyz)
                                opengroup.addmember(assy.homeCsys)
                        elif (name == "LastView"):                         
                                assy.lastCsys = Csys(assy, name, scale, pov, zoomFactor, wxyz)
                                opengroup.addmember(assy.lastCsys)
                else:
                  m = old_csyspat.match(card)
                  if m:
                        name=m.group(1)
                        wxyz = A(map(float, [m.group(2), m.group(3),
                                 m.group(4), m.group(5)]))
                        scale=float(m.group(6))
                        assy.homeCsys = Csys(assy, "OldVersion", scale, V(0,0,0), 1.0, wxyz)
                        opengroup.addmember(assy.homeCsys)
                        assy.lastCsys = Csys(assy, "LastView", scale, V(0,0,0), 1.0, A([0.0, 1.0, 0.0, 0.0]))
                        opengroup.addmember(assy.lastCsys)

        elif key=="datum": # Datum object
            if not isInsert: #Skip this record if inserting
                m=re.match(datumpat,card)
                if not m:
                        print card
                        continue
                name=m.group(1)
                type=m.group(5)
                col = tuple(map(int, [m.group(2), m.group(3), m.group(4)]))
                vec1 = A(map(float, [m.group(6), m.group(7), m.group(8)]))
                vec2 = A(map(float, [m.group(9), m.group(10), m.group(11)]))
                vec3 = A(map(float, [m.group(12), m.group(13), m.group(14)]))
                new = Datum(assy,name,type,vec1,vec2,vec3)
                opengroup.addmember(new)
                new.rgb = col
            
        elif key=="waals": # van der Waals Interactions
            pass # code was wrong -- to be implemented later
            
        elif key=="kelvin":  # Temperature in Kelvin
            if not isInsert: # Skip this record if inserting
                m = re.match("kelvin (\d+)",card)
                n = int(m.group(1))
                assy.temperature = n
                
        elif key=="mmpformat":  # MMP File Format. Mark 050130
            if not isInsert: # Skip this record if inserting
                m = re.match("mmpformat (.*)",card)
                assy.mmpformat=m.group(1)

        ## [bruce 050324 commenting out movieID until it's used; strategy for this will change, anyway.]                
##        elif key=="movie_id": # Movie ID - To be supported for Beta.  Mark 05-01-16
##            if not isInsert: # Skip this record if inserting
##                m = re.match("movie_id (\d+)",card)
##                n = int(m.group(1))
##                assy.movieID = n
                
        elif key=="end1":  # End of main tree
            AddAtoms = False

        elif key == "end":
            # end of file
            pass
        
        elif key == "info":
            #bruce 050217 new mmp record, for optional info about
            # various types of objects which occur earlier in the file
            # (what I mean by "optional" is that it's never an error for the
            #  specified type of thing or type of info to not be recognized,
            #  as can happen when a new file is read by older code)
            
            # find current chunk -- how we do this depends on details of
            # the other mmp-record readers in this big if/elif statement,
            # and is likely to need changing sometime
            chunk = mol
            # make dict of all current items that info record might refer to
            currents = dict(chunk = chunk)
            interp = mmp_interp(ndix) #e could optim by using the same object each time
            readmmp_info(card, currents, interp) # has side effect on object referred to by card
                    
        else:
            # unrecognized mmp record; not an error, since the format
            # is meant to be upward-compatible when new records are added,
            # as long as it's ok for old code to ignore them and not signal an error
            #bruce 050217 new debug feature: warning for unrecognized record
            if platform.atom_debug:
                print "atom_debug: fyi: unrecognized mmp record type ignored (not an error): %r" % key
    
    return grouplist # from _readmmp

class mmp_interp: #bruce 050217
    "helps translate object refs in mmp file to their objects"
    def __init__(self, ndix):
        self.ndix = ndix # maps atom numbers to atoms (??)
    def atom(self, atnum):
        "map atnum string to atom, while reading mmp file"
        return self.ndix[int(atnum)]
    pass

def readmmp_info( card, currents, interp ): #bruce 050217
    """Handle an info record 'card' being read from an mmp file;
    currents should be a dict from thingtypes to the current things of those types,
    for all thingtypes which info records can give info about (so far, just 'chunk');
    interp should be an mmp_interp object #doc.
       The side effect of this function, when given "info <type> <name> = <val>",
    is to tell the current thing of type <type> (that is, the last one read from this file)
    that its optional info <name> has value <val>,
    using a standard info-accepting method on that thing.
    <type> should be a "word";
    <name> should be one or more "words"
    (it's supplied as a python list of strings to the info-accepting method);
    <val> can be (for now) any string with no newlines,
    and no whitespace at the ends; its permissible syntax might be further restricted later.
    """
    #e interface will need expanding when info can be given about non-current things too
    what, val = card.split('=', 1)
    key = "info"
    what = what[len(key):]
    what = what.strip() # e.g. "chunk xxx" for info of type xxx about the current chunk
    val = val.strip()
    what = what.split() # e.g. ["chunk", "xxx"], always 2 or more words
    type = what[0]
    name = what[1:] # list of words (typically contains exactly one word, an attribute-name)
    thing = currents.get(type)
    if thing: # can be false if type not recognized, or if current one was None
        # record info about the current thing of type <type>
        try:
            thing.readmmp_info_setitem( name, val, interp )
        except:
            print_compact_traceback("error reading info record for %s %r, ignored: " % (type, name) )
    elif platform.atom_debug:
        print "atom_debug: fyi: no object found for info record for %s %r; ignoring it (not an error)" % (type, name)
    return

# read a Molecular Machine Part-format file into maybe multiple molecules
def readmmp(assy, filename): #bruce 050302 split out some subroutines for use in other code
    """Reading a mmp file to create a new model """
    grouplist = _readmmp(assy, filename)
    grouplist = fix_grouplist(assy, grouplist)
    reset_grouplist(assy, grouplist)
    return
    
def fix_grouplist(assy, grouplist):
    #bruce 050302; temporary since all this code is badly structured
    """[private]
    common code for readmmp and insertmmp --
    check and canonicalize a grouplist read from an mmp file
    """
    if len(grouplist) == 2:
        #bruce 050217 upward-compatible reader extension (needs no mmpformat-record change):
        # permit missing 3rd group, so we can read mmp files written as input for the simulator
        # (and since there is no good reason not to!)
        grouplist.append( Group("Clipboard", assy, None) )
        assert len(grouplist) == 3
        assy.w.history.message( "(fyi: this mmp file was written as input for the simulator, and contains no clipboard items)" )
        
    if len(grouplist) != 3:
        print "wrong number of top-level groups; treating file as empty"
        #bruce 050217: also emit a user-visible error message
        # (It says the program treats the file as empty;
        #  I think this is accurate [given how this function is called],
        #  but I'm not 100% sure)
        assy.w.history.message( redmsg( "mmp file format error: wrong number of top-level groups; treating file as empty" ))
        #e it would be nice to have an "error return" here...
        return None
    else:
        ## assy.data, assy.tree, assy.shelf = grouplist
        return grouplist
    pass

def reset_grouplist(assy, grouplist):
    #bruce 050302 split this out of readmmp;
    # it should be entirely rewritten and become an assy method
    """[private]
    stick a new grouplist into assy, within readmmp;
    if grouplist is None, indicating file had bad format,
    do some but not all of the usual side effects.
    [appropriateness of behavior for grouplist == None is unreviewed]
    """
    if grouplist:
        assy.data, assy.tree, assy.shelf = grouplist
    #bruce 050302: old code does a lot of the following even if grouplist is None;
    # until I understand all the effects better, I won't change that.
    assy.shelf.name = "Clipboard"
    assy.data.open = assy.shelf.open = False
    assy.root = Group("ROOT", assy, None, [assy.tree, assy.shelf])
    #bruce 050131 for Alpha:
    from Utility import kluge_patch_assy_toplevel_groups
    kluge_patch_assy_toplevel_groups(assy)
    #bruce 050309 for assy/part split
    assy.update_parts()
##    assy.fix_parts() #bruce 050302 for assy/part split
    return

def insertmmp(assy, filename): #bruce 050302 using some subrs split from readmmp
    """Reading a mmp file and insert the part into the existing model """
    #####@@@@@ this implem is wrong -- does it in the main part, regardless of the current part.
    grouplist  = _readmmp(assy, filename, isInsert = True)
    # bruce 050302 permit reading a sim-input mmp file (2 top groups)
    grouplist = fix_grouplist(assy, grouplist)
    if grouplist:
        assy.tree.addmember(grouplist[1])
    return

def workaround_for_bug_296(assy, onepart = None):
    """If needed, move jigs in assy.tree and each assy.shelf member to later positions
    (and emit appropriate messages about this),
    since current mmp file format requires jigs to come after
    all chunks whose atoms they connect to.
    If onepart is provided, then do this only for the node (if any)
    whose part is onepart.
    """
    # bruce 050111 temp fix for bug 296 (maybe enough for Alpha)
    # bruce 050202 adds:
    # I developed an extension to this fix for jigs in clipboard items,
    # but decided not to commit it for Alpha. It's in a diff -c, mailed to cad
    # for inclusion as a bug296 comment, for testing and use after Alpha.
    # It might as well be put in as soon as anyone has time, after Alpha goes out.
    # bruce 050325: I finally put that in, and then further modified this code,
    # e.g. adding onepart option.
    def errfunc(msg):
        "local function for error message output"
        assy.w.history.message( redmsg( msg))
    try:
        from node_indices import move_jigs_if_needed
        count = 0
        if onepart == assy.tree.part or not onepart:
            count = move_jigs_if_needed(assy.tree, errfunc) # (this does the work)
        shelf_extra = ""
        try:
            #bruce 050202 extension to fix it in shelf too [not committed until 050325]
            count2 = 0
            for m in assy.shelf.members:
                count1 = 0
                if onepart == m.part or not onepart:
                    count1 = move_jigs_if_needed(m, errfunc)
                count += count1 # important to count these now in case of exception in next loop iteration
                count2 += count1
            if count2:
                shelf_extra = "of which %d were in clipboard, " % count2
        except:
            print_compact_traceback("bug in workaround_for_bug_296 for some shelf item: ")
            shelf_extra = ""
        if count:
            from platform import fix_plurals
            movedwhat = fix_plurals( "%d jig(s)" % count)
            warning = "Warning: moved %s within model tree, %s" \
              "to work around limitation in Alpha mmp file format" % (movedwhat, shelf_extra)
            assy.w.history.message( redmsg( warning))
    except:
        print_compact_traceback("bug in bug-296 bugfix in fileIO.writemmpfile_assy or _part: ")
    return

class writemmp_mapping: #bruce 050322, to help with minimize selection and other things
    """Provides an object for accumulating data while writing an mmp file.
    Specifically, the object stores options which affect what's written,
    accumulates an encoding of atoms as numbers,
    has helper methods for using that encoding,
    writing some parts of the file;
    in future this will be able to write forward refs for jigs and save
    the unwritten jigs they refer to until they're written at the end.
    """
    fp = None
    def __init__(self, assy, **options):
        "#doc; assy is used for some side effects (hopefully that can be cleaned up)."
        self.assy = assy
        self.atnums = atnums = {}
        atnums['NUM'] = 0 # kluge from old code, kept for now
            #e soon change atnums to store strings, and keep 'NUM' as separate instvar
##        self.alist = [] # might be removed later; used only as an initial compatibility kluge (grabbed by client code)
        self.options = options
        self.sim = options.get('sim', False) # simpler file just for the simulator?
        self.min = options.get('min', False) # even more simple, just for minimize?
        if self.min:
            self.sim = True
        pass
    def set_fp(self, fp):
        "set file pointer to write to (don't forget to call write_header after this!)"
        self.fp = fp
    def write(self, lines):
        "write one or more \n-terminates lines to our file pointer"
        #e future versions might also hash these lines, to help make a movie id
        self.fp.write(lines)
    def close(self, error = False):
        if error:
            try:
                self.write("\n# error writing file\n")
            except:
                print_compact_traceback("exception writing to mmp file, ignored: ")
        self.fp.close()
    def write_header(self):
        assy = self.assy
        # The MMP File Format is initialized here, just before we write the file.
        # Mark 050130
        # [see also the general notes and history of the mmpformat,
        # in a comment or docstring near the top of this file -- bruce 050217]
        assy.mmpformat = MMP_FORMAT_VERSION_TO_WRITE
            #bruce 050322 comment: this side effect is questionable when self.sim or self.min is True
        self.fp.write("mmpformat %s\n" % assy.mmpformat)
        
        if self.min:
            self.fp.write("# mmp file for minimizer, might affect details of format\n")
        elif self.sim:
            self.fp.write("# mmp file for simulator, might affect details of format\n")
        
        if not self.min:
            self.fp.write("kelvin %d\n" % assy.temperature)
        # To be added for Beta.  Mark 05-01-16
        ## f.write("movie_id %d\n" % assy.movieID)
        return
    def encode_next_atom(self, atom):
        """Assign the next sequential number (for use only in this writing of this mmp file)
        to the given atom; return the number AS A STRING and also store it herein for later use.
        Error if this atom was already assigned a number.
        """
        # code moved here from old atom.writemmp in chem.py
        atnums = self.atnums
##        alist = self.alist
        assert atom.key not in atnums # new assertion, bruce 030522
        atnums['NUM'] += 1 # old kluge, to be removed
        num = atnums['NUM']
##        alist.append(atom) #k needed??
        atnums[atom.key] = num
        assert str(num) == self.encode_atom(atom)
        return str(num)
    def encode_atom(self, atom):
        """Return an encoded reference to this atom (a short string, actually
        a printed int as of 050322, guaranteed true i.e. not "")
        for use only in the mmp file contents we're presently creating,
        or None if no encoding has yet been assigned to this atom for this
        file-writing event.
           This has no side effects -- to allocate new encodings, use
        encode_next_atom instead.
           Note: encoding is valid only for one file-writing-event,
        *not* for the same filename if it's written to again later
        (in principle, not even if the file contents are unchanged, though in
        practice, for other reasons, we try to make the encoding deterministic).
        """
        if atom.key in self.atnums:
            return str(self.atnums[atom.key])
        else:
            return None
        pass
    def dispname(self, display):
        "(replaces disp = dispNames[self.display] in older code)"
        if self.sim:
            disp = "-" # assume sim ignores this field
        else:
            disp = dispNames[display]
        return disp
    pass # end of class writemmp_mapping

# bruce 050322 revised to use mapping; 050325 split, removed assy.alist set
def writemmpfile_assy(assy, filename, addshelf = True): #e should merge with writemmpfile_part
    """Write everything in this assy (chunks, jigs, Groups,
    for both tree and shelf unless addshelf = False)
    into a new MMP file of the given filename.
    Should be called via the assy method writemmpfile.
    """
    #bruce 050325 renamed this from writemmp
    # to avoid confusion with Node.writemmp.
    # Also, there's now an assy method which calls it ###@@@doit
    # and a sister function for Parts which has a Part method.

    assy.update_parts() #bruce 050325 precaution
    
    if addshelf:
        workaround_for_bug_296( assy)
    else:
        workaround_for_bug_296( assy, onepart == assy.tree.part)
    
    ##Huaicai 1/27/05, save the last view before mmp 
    ## file saving
    assy.o.saveLastView(assy)
    
    fp = open(filename, "w")

    mapping = writemmp_mapping(assy) ###e should pass sim or min options when used that way...
    ## assy.alist = mapping.alist # (empty list which will grow during writemmp methods)
    ##    # initial compatibility kluge (preserve same bugs as before)
    mapping.set_fp(fp)

    try:
        mapping.write_header()
        assy.data.writemmp(mapping)
        assy.tree.writemmp(mapping)
        
        mapping.write("end1\n")
        
        if addshelf:
            assy.shelf.writemmp(mapping)
        
        mapping.write("end molecular machine part " + assy.name + "\n")
    except:
        mapping.close(error = True)
        raise
    else:
        mapping.close()
    return # from writemmpfile_assy

def writemmpfile_part(part, filename): ##e should merge with writemmpfile_assy
    "write an mmp file for a single Part"
    node = part.topnode
    assert part == node.part
    part.assy.update_parts() #bruce 050325 precaution
    if part != node.part and platform.atom_debug:
        print "atom_debug: bug?: part changed during writemmpfile_part, using new one"
    part = node.part
    assy = part.assy
    #e assert node is tree or shelf member? is there a method for that already? is_topnode?
    workaround_for_bug_296( assy, onepart = part)
    assy.o.saveLastView(assy)
    fp = open(filename, "w")
    mapping = writemmp_mapping(assy)
    mapping.set_fp(fp)
    try:
        mapping.write_header() ###e header should differ in this case
        ##e header or end comment or both should say which Part we wrote
        node.writemmp(mapping)
        mapping.write("end molecular machine part " + assy.name + "\n")
    except:
        mapping.close(error = True)
        raise
    else:
        mapping.close()
    return # from writemmpfile_part

def povpoint(p):
    # note z reversal -- povray is left-handed
    return "<" + str(p[0]) + "," + str(p[1]) + "," + str(-p[2]) + ">"
        
# Create a POV-Ray file
def writepovfile(assy, filename):
    f = open(filename,"w")
    ## bruce 050325 removed this (no effect except on assy.alist which is bad now)
    ## atnums = {}
    ## atnums['NUM'] = 0
    ## assy.alist = [] 

    cdist = 6.0 ###5.0 # Camera distance
    aspect = (assy.o.width + 0.0)/(assy.o.height + 0.0)
    zfactor =  0.4 # zoom factor 
    up = V(0.0, zfactor, 0.0)
    right = V( aspect * zfactor, 0.0, 0.0) ##1.33  
    import math
    angle = 2.0*atan2(aspect, cdist)*180.0/math.pi
    
    f.write("// Recommended window size: width=%d, height=%d \n\n"%(assy.o.width, assy.o.height))

    f.write(povheader)

    # Background color
    f.write("background {\n  color rgb " + povpoint(assy.o.mode.backgroundColor*V(1,1,-1)) + "\n}\n")

    light1 = (assy.o.out + assy.o.left + assy.o.up) * 10.0
    light2 = (assy.o.right + assy.o.up) * 10.0
    light3 = assy.o.right + assy.o.down + assy.o.out/2.0
    
    # Light sources
    f.write("\nlight_source {\n  " + povpoint(light1) + "\n  color Gray10 parallel\n}\n")
    f.write("\nlight_source {\n  " + povpoint(light2) + "\n  color Gray40 parallel\n}\n")
    f.write("\nlight_source {\n  " + povpoint(light3) + "\n  color Gray40 parallel\n}\n")
    
    vdist = cdist
    if aspect < 1.0:
            vdist = cdist / aspect
    eyePos = vdist * assy.o.scale*assy.o.out-assy.o.pov
    # Camera info
    f.write("\ncamera {\n  location " + povpoint(eyePos)  + "\n  up " + povpoint(up) + "\n  right " + povpoint(right) + "\n  sky " + povpoint(assy.o.up) + "\n angle " + str(angle) + "\n  look_at " + povpoint(-assy.o.pov) + "\n}\n\n")
 
    # write a union object, which encloses all following objects, so it's 
    # easier to set a global modifier like "Clipped_by" for all objects
    # Huaicai 1/6/05
    f.write("\nunion {\t\n") ##Head of the union object
 
    # Write atoms and bonds in the part
    assy.tree.writepov(f, assy.o.display)
    
    farPos = -cdist*assy.o.scale*assy.o.out*assy.o.far + eyePos
    nearPos = -cdist*assy.o.scale*assy.o.out*assy.o.near + eyePos
    
    pov_out = (assy.o.out[0], assy.o.out[1], -assy.o.out[2])
    pov_far =  (farPos[0], farPos[1], -farPos[2])
    pov_near =  (nearPos[0], nearPos[1], -nearPos[2])
    pov_in = (-assy.o.out[0], -assy.o.out[1], assy.o.out[2])
    
    ### sets the near and far clipping plane
    f.write("clipped_by { plane { " + povpoint(-assy.o.out) + ", " + str(dot(pov_in, pov_far)) + " }\n")
    f.write("             plane { " + povpoint(assy.o.out) + ", " + str(dot(pov_out, pov_near)) + " } }\n")
    f.write("}\n\n")  

    f.close()
    

# Create an MDL file - by Chris Phoenix and Mark for John Burch [04-12-03]
def writemdlfile(assy, filename):
    alist = [] #bruce 050325 changed assy.alist to localvar alist
    natoms = 0
    # Specular values keyed by atom color 
    # Only Carbon, Hydrogen and Silicon supported here
    specValues = {(117,117,117):((183, 183, 183), 16, 44), \
                       (256,256,256):((183, 183, 183), 15, 44), \
                       (111,93,133):((187,176,200), 16, 44)}

    # Determine the number of visible atoms in the part.
    # Invisible atoms are drawn.  Hidden atoms are not drawn.
    # This is a bug to be fixed in the future.  Will require work in chunk/chem.writemdl, too.  
    # writepov may have this problem, too.
    # Mark [04-12-05]     
    # To test this, we need to get a copy of Animation Master.
    # Mark [05-01-14]
    for mol in assy.molecules: 
        if (not mol.hidden) and (mol.disp != diINVISIBLE): natoms += len(mol.atoms)
#    print "fileIO: natoms =", natoms

    f = open(filename, 'w');
    
    # Write the header
    f.write(mdlheader)
    
    # Write atoms with spline coordinates
    f.write("Splines=%d\n"%(13*natoms))
    assy.tree.writemdl(alist, f, assy.o.display)
    
    # Write the GROUP information
    # Currently, each atom is 
    f.write("[ENDMESH]\n[GROUPS]\n")
    
    atomindex = 0 
    
    for mol in assy.molecules:
        col = mol.color # Color of molecule
        for a in mol.atoms.values():
            
            # Begin GROUP record for this atom.
            f.write("[GROUP]\nName=Atom%d\nCount=80\n"%atomindex)
            
            # Write atom mesh IDs
            for j in range(80):
                f.write("%d\n"%(98-j+atomindex*80))

            # Write Pivot record for this atom.
#            print "a.pos = ", a.posn()
            xyz=a.posn()
            n=(float(xyz[0]), float(xyz[1]), float(xyz[2]))
            f.write("Pivot= %f %f %f\n" % n)
            
            # Add DiffuseColor record for this atom.
            color = col or a.element.color
            rgb=map(int,A(color)*255) # rgb = 3-tuple of int
            color=(int(rgb[0]), int(rgb[1]), int(rgb[2]))
            f.write("DiffuseColor=%d %d %d\n"%color)

            # Added specularity per John Burch's request
            # Specular values keyed by atom color           
            (specColor, specSize, specIntensity) = \
             specValues.get(color, ((183,183,183),16,44))
            f.write("SpecularColor=%d %d %d\n"%specColor)
            f.write("SpecularSize=%d\n"%specSize)
            f.write("SpecularIntensity=%d\n"%specIntensity)
            
            # End the group for this atom.
            f.write("[ENDGROUP]\n")
            
            atomindex += 1
        
    # ENDGROUPS
    f.write("[ENDGROUPS]\n")

    # Write the footer and close
    fpos = f.tell()
    f.write(mdlfooter)
    f.write("FileInfoPos=%d\n"%fpos)
    f.close()
    

def readElementColors(fileName):
    """Read element colors (ele #, r, g, b) from a text file,   each element is on a new line.  A line starts from '#' is a comment line.
    <Parameter> fileName: a string for the input file name
    <Return>:  A list of quardral tuples--(ele #, r, g, b) if succeed, otherwise 'None' 
    """
    try:
        lines = open(fileName, "rU").readlines()         
    except:
        print "Exception occurred to open file: ", fileName
        return None
    
    elemColorTable = []
    for line in lines: 
        if not line.startswith('#'):
            try:
                words = line.split()
                row = map(int, words[:4])
                # Check Element Number validity
                if row[0] >= 0 and row[0] <= 54:
                    # Check RGB index values
                    if row[1] < 0 or row[1] > 255 or row[2] < 0 or row[2] > 255 or row[3] < 0 or row[3] > 255:
                        raise ValueError, "An RGB index value not in a valid range (0-255)."
                    elemColorTable += [row]
                else:
                    raise ValueError, "Element number value not in a valid range."
            except:
               print "Error in element color file %s.  Invalid value in line: %sElement color file not loaded." % (fileName, line)
               return None
    
    return elemColorTable           


def saveElementColors(fileName, elemTable):
    """Write element colors (ele #, r, g, b) into a text file,  each element is on a new line.  A line starts from '#' is a comment line.
    <Parameter> fileName: a string for the input file name
    <Parameter> elemTable: A dictionary object of all elements in our periodical table 
    """
    assert type(fileName) == type(" ")
    
    try:
        f = open(fileName, "w")
    except:
        print "Exception occurred to open file %s to write: " % fileName
        return None
   
    f.write("# nanoENGINEER-1.com Element Color File, Version 050311\n")
    f.write("# File format: ElementNumber r(0-255) g(0-255) b(0-255) \n")
    
    for eleNum, elm in elemTable.items():
        col = elm.color
        r = int(col[0] * 255 + 0.5)
        g = int(col[1] * 255 + 0.5)
        b = int(col[2] * 255 + 0.5)
        f.write(str(eleNum) + "  " + str(r) + "  " + str(g) + "  " + str(b) + "\n")
    
    f.close()
