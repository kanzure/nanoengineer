# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
File IO functions for reading and writing PDB and MMP files

$Id$
"""
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

nampat=re.compile("\\(([^)]*)\\)")
old_csyspat = re.compile("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
new_csyspat = re.compile("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
datumpat = re.compile("datum \((.+)\) \((\d+), (\d+), (\d+)\) (.*) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)")
keypat=re.compile("\S+")
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


# read a Protein DataBank-format file into a single molecule
def _readpdb(assy, filename, isInsert = False):

    f=open(filename,"rU").readlines()
    
    dir, nodename = os.path.split (filename)
    if not isInsert: assy.filename=filename
    ndix={}
    mol=molecule(assy, nodename)
        
    for card in f:
        key=card[:6].lower().replace(" ", "")
        if key in ["atom", "hetatm"]:
            sym = capitalize(card[12:14].replace(" ", "").replace("_", ""))
            try: PeriodicTable[EltSym2Num[sym]]
            except KeyError: print 'unknown element "',sym,'" in: ',card
            else:
                xyz = map(float, [card[30:38],card[38:46],card[46:54]])
                n=int(card[6:11])
                a=atom(sym, A(xyz), mol)
                ndix[n]=a
        elif key == "conect":
            a1=ndix[int(card[6:11])]
            for i in range(11, 70, 5):
                try: a2=ndix[int(card[i:i+5])]
                except ValueError: break
                mol.bond(a1, a2)
#    f.close()
    return mol
    
# read a Protein DataBank-format file into a single molecule
def readpdb(assy,filename):
    """Reads a pdb file"""
    mol  = _readpdb(assy, filename, isInsert = False)
    assy.addmol(mol)
    
# Insert a Protein DataBank-format file into a single molecule
def insertpdb(assy,filename):
    """Reads a pdb file and inserts it into the existing model """
    mol  = _readpdb(assy, filename, isInsert = True)
    assy.addmol(mol)

# Write a single molecule into a Protein DataBank-format file 
def writepdb(assy, filename):
    f = open(filename, "w")
    # Atom object is the key, the atomIndex is the value  
    atomsTable = {}
    # Each element is a list of atoms connected with the 1rst atom
    connectList = []

    atomIndex = 1

    for mol in assy.molecules:
        for a in mol.atoms.itervalues():
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
                aList.append(b.other(a))

            atomIndex += 1
            connectList.append(aList)

            f.write("\n")

    for aList in connectList:
        f.write("CONECT")
        for a in aList:
            index = atomsTable[a.key]
            f.write("%5d" % index)
        f.write("\n")

    f.write("END")
    f.close()   

# Huaicai to implement readxyz - Mark 050120
def readxyz(assy):
        """Read a single-frame XYZ file created by the simulator, typically  for minimizing a part. Check file format, return a list of atom new positions in the same order as assy.alist
        """
        xyzFile = assy.m.filename
        lines = open(xyzFile, "rU").readlines()
        
        if len(lines) < 3: ##Invalid file format
             print "%s: File format error." % xyzFile
             return
        
        atomList = assy.alist
        ## stores the new position for each atom in atomList
        newAtomsPos = [] 
        
        try:     
                numAtoms = int(lines[0])
                rms = float(lines[1][4:])
        except ValueError:
                print "%s: File format error in Line 1 and/or Line 2" % xyzFile
                return
        
        atomIndex = 0
        for line in lines[2:]:
                words = line.split()
                if len(words) != 4:
                      print "%s: Line %d format error." % (lines.index(line), xyzFile)
                      return
                try:        
                    if words[0] != atomList[atomIndex].element.symbol:
                        print "%s: atom %d is not matching." % (xyzFile, atomIndex)
                        return
                    
                    newAtomsPos += [map(float, words[1:])]
                except ValueError:
                        print "%s: atom %d position number format error." % (xyzFile, atomIndex)
                        return
                         
                atomIndex += 1
        
        if (len(newAtomsPos) != len(atomList)):
                print "The number of atoms from %s is not matching with the current model." % xyzFile
                
        return newAtomsPos        
        
        
def _addMolecule(mol, assy, group):
        """Make sure to call this function before any other record operation except for record types: atom, bond, shaft and csys, dataum, walls, kelvin. This adds the previous molecule to its group """
        
        assy.addmol(mol)
        mol.moveto(group)
        mol = None
        
        return mol        


def _readmmp(assy, filnam, isInsert = False):
    """The routine to actually reading a mmp file and save data
    into data structure"""
    #bruce 041011: added 'U' to file mode, for universal newline support.
    l=open(filnam,"rU").readlines() 
    if not isInsert: assy.filename=filnam
    mol = None
    ndix={}
    assy.alist = []
    AddAtoms = True
    #assy.tree = Group("Root", assy, None)
    groupstack = [] #stack to store (group, name) tuples
    grouplist = []     #List of top level groups will be returned by the function
    opengroup = None #The only current group which can accept children
 
    for card in l:
        key=keypat.match(card)
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

        if key == "egroup": # Group of Molecules and/or Groups
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
            sym=PeriodicTable[int(m.group(2))].symbol
            xyz=A(map(float, [m.group(3),m.group(4),m.group(5)]))/1000.0
            a = atom(sym, xyz, mol)
            disp = atom2pat.match(card)
            if disp:
                try: a.setDisplay(dispNames.index(disp.group(1)))
                except ValueError: pass
                    
            if AddAtoms: 
                assy.alist += [a]
            
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
                
        elif key=="movie_id": # Movie ID - To be supported for Beta.  Mark 05-01-16
            if not isInsert: # Skip this record if inserting
                m = re.match("movie_id (\d+)",card)
                n = int(m.group(1))
                assy.movieID = n
                
        elif key=="end1":  # End of main tree
            AddAtoms = False
    
    return grouplist        
            

# read a Molecular Machine Part-format file into maybe multiple molecules
def readmmp(assy, filnam):
    """Reading a mmp file to create a new model """
    grouplist = _readmmp(assy, filnam)
    if len(grouplist) != 3: print "wrong number of top-level groups"
    else: assy.data, assy.tree, assy.shelf = grouplist
    assy.shelf.name = "Clipboard"
    assy.data.open = assy.shelf.open = False
    assy.root = Group("ROOT", assy, None, [assy.tree, assy.shelf])
    #bruce 050131 for Alpha:
    from Utility import kluge_patch_assy_toplevel_groups
    kluge_patch_assy_toplevel_groups(assy)
    return
    
def insertmmp(assy, fileName):
    """Reading a mmp file and insert the part into the existing model """    
    groupList  = _readmmp(assy, fileName, isInsert = True)
    
    if len(groupList) != 3: print "wrong number of top-level groups"
    assy.tree.addmember(groupList[1])

def workaround_for_bug_296(assy):
    """If needed, move jigs in assy.tree to later positions
    (and emit appropriate messages about this),
    since current mmp file format requires jigs to come after
    all chunks whose atoms they connect to.
    """
    # bruce 050111 temp fix for bug 296 (maybe enough for Alpha)
    # bruce 050202 adds:
    # I developed an extension to this fix for jigs in clipboard items,
    # but decided not to commit it for Alpha. It's in a diff -c, mailed to cad
    # for inclusion as a bug296 comment, for testing and use after Alpha.
    # It might as well be put in as soon as anyone has time, after Alpha goes out.
    def errfunc(msg):
        "local function for error message output"
        assy.w.history.message( redmsg( msg))
    try:
        from node_indices import move_jigs_if_needed
        count = move_jigs_if_needed(assy.tree, errfunc) # (this does the work)
        if count:
            from platform import fix_plurals
            movedwhat = fix_plurals( "%d jig(s)" % count)
            warning = "Warning: moved %s within model tree, " \
              "to work around limitation in Alpha mmp file format" % movedwhat
            assy.w.history.message( redmsg( warning))
    except:
        print_compact_traceback("bug in bug-296 bugfix in fileIO.writemmp: ")
    return

# write all molecules, motors, grounds into an MMP file
def writemmp(assy, filename, addshelf = True):
    
    workaround_for_bug_296( assy)
    
    ##Huaicai 1/27/05, save the last view before mmp 
    ## file saving
    assy.o.saveLastView(assy)  
    
    f = open(filename,"w")
    atnums = {}
    atnums['NUM'] = 0
    assy.alist = []
    
    # The MMP File Format is initialized here, just before we write the file.
    # Mark 050130
    assy.mmpformat = '050130'
    f.write("mmpformat %s\n" % assy.mmpformat)
    
    f.write("kelvin %d\n" % assy.temperature)
    
    # To be added for Beta.  Mark 05-01-16
#    f.write("movie_id %d\n" % assy.movieID)
    
    assy.data.writemmp(atnums, assy.alist, f)
    assy.tree.writemmp(atnums, assy.alist, f)

    f.write("end1\n")
    
    if addshelf: assy.shelf.writemmp(atnums, assy.alist, f)
                     
    f.write("end molecular machine part " + assy.name + "\n")
    f.close()

def povpoint(p):
    # note z reversal -- povray is left-handed
    return "<" + str(p[0]) + "," + str(p[1]) + "," + str(-p[2]) + ">"
        
# Create a POV-Ray file
def writepov(assy, filename):
    f = open(filename,"w")
    atnums = {}
    atnums['NUM'] = 0
    assy.alist = []

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
def writemdl(assy, filename):
    assy.alist = []
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
    assy.tree.writemdl(assy.alist, f, assy.o.display)
    
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
    

# Write a dpb or xyz trajectory file.
def writemovie(assy, mflag = False):
    """Creates a moviefile.  The name of the moviefile it creates is found in
    assy.m.filename.  The moviefile is either a DPB file or an XYZ trajectory file.
    DPB = Differential Position Bytes (binary file)
    XYZ = XYZ trajectory file (text file)
    mflag:
        0 = default, runs a full simulation using parameters stored in the movie object.
        1 = run the simulator with -m and -x flags, creating a single-frame XYZ file.
        2 = run the simulator with -m flags, creating a multi-frame DPB moviefile.
    """
    # Make sure some chunks are in the part.
    if not assy.molecules: # Nothing in the part to minimize.
        msg = redmsg("Can't create movie.  No chunks in part.")
        assy.w.history.message(msg)
        return -1
    
    # "pid" = process id.  
    # We use the PID to create unique filenames for this instance of the program,
    # so that if we run more than one program at the same time, we don't use
    # the same temporary file names.
    pid = os.getpid()
    
    if mflag == 1: # single-frame XYZ file
        assy.m.filename = os.path.join(assy.w.tmpFilePath, "sim-%d.xyz" % pid)
        
    if mflag == 2: #multi-frame DPB file
        assy.m.filename = os.path.join(assy.w.tmpFilePath, "sim-%d.dpb" % pid)
    
    if assy.m.filename: 
        moviefile = assy.m.filename
    else:
        msg = redmsg("Can't create movie.  Empty filename.")
        assy.w.history.message(msg)
        return -1
        
    # Check that the moviefile has a valid extension.
    ext = moviefile[-4:]
    if ext not in ['.dpb', '.xyz']:
        # Don't recognize the moviefile extension.
        msg = redmsg("Movie [" + moviefile + "] has unsupported extension.")
        assy.w.history.message(msg)
        print "writeMovie: " + msg
        return -1

    # We always save the current part to an MMP file.  In the future, we may want to check
    # if assy.filename is an MMP file and use it if not assy.has_changed().
    mmpfile = os.path.join(assy.w.tmpFilePath, "sim-%d.mmp" % pid)
    traceFile = "-q"+ os.path.join(assy.w.tmpFilePath, "sim-%d-trace.txt" % pid)    

    # filePath = the current directory NE-1 is running from.
    filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        
    # "program" is the full path to the simulator executable. 
    if sys.platform == 'win32': 
        program = os.path.normpath(filePath + '/../bin/simulator.exe')
    else:
        program = os.path.normpath(filePath + '/../bin/simulator')
    
    # Make sure the simulator exists
    if not os.path.exists(program):
        msg = redmsg("Simulator [" + program + "] does not exit.  Simluation aborted.")
        assy.w.history.message(msg)
        return -1

    # Change cursor to Wait (hourglass) cursor
    ##Huaicai 1/10/05, it's more appropriate to change the cursor
    ## for the main window, not for the progressbar window
    QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
    #oldCursor = QCursor(assy.w.cursor())
    #assy.w.setCursor(QCursor(Qt.WaitCursor) )

    outfile = "-o"+moviefile
    infile = mmpfile

    # "formarg" = File format argument
    if ext == ".dpb": formarg = ''
    else: formarg = "-x"
    
    # "args" = arguments for the simulator.
    if mflag: 
        args = [program, '-m', str(formarg), traceFile, outfile, infile]
    else: 
        # THE TIMESTEP ARGUMENT IS MISSING ON PURPOSE.
        # The timestep argument "-s + (assy.timestep)" is not supported for Alpha.
        args = [program, 
                    '-f' + str(assy.m.totalFrames),
                    '-t' + str(assy.m.temp), 
                    '-i' + str(assy.m.stepsper), 
                    str(formarg),
		    traceFile, 
                    outfile, 
                    infile]

    # Tell user we're creating the movie file...
#    msg = "Creating movie file [" + moviefile + "]"
#    assy.w.history.message(msg)

    # READ THIS IF YOU PLAN TO CHANGE ANY CODE FOR writemovie()!
    # writemmp must come before computing "natoms".  This ensures that writemovie
    # will work when creating a movie for a file without an assy.alist.  Examples of this
    # situation include:
    # 1)  The part is a PDB file.
    # 2) We have chunks, but no assy.alist.  This happens when the user opens a 
    #      new part, creates something and simulates before saving as an MMP file.
    # 
    # I do not know if it was intentional, but assy.alist is not created until an mmp file 
    # is created.  We are simply taking advantage of this "feature" here.
    # - Mark 050106
    
    writemmp(assy, mmpfile, False)
    assy.m.natoms = natoms = len(assy.alist)
#    print "writeMovie: natoms = ",natoms, "assy.filename =",assy.filename
            
    # We cannot to determine the exact final size of an XYZ trajectory file.
    # This formula is an estimate.  "filesize" must never be larger than the
    # actual final size of the XYZ file, or the progress bar will never hit 100%,
    # even though the simulator finished writing the file.
    # - Mark 050105 
    if formarg == "-x":
        # Single shot minimize.
        if mflag: # Assuming mflag = 2. If mflag = 1, filesize could be wrong.  Shouldn't happen, tho.
            filesize = natoms * 16 # single-frame xyz filesize (estimate)
            pbarCaption = "Minimize"
            pbarMsg = "Minimizing..."
        # Write XYZ trajectory file.
        else:
            filesize = assy.m.totalFrames * ((natoms * 28) + 25) # multi-frame xyz filesize (estimate)
            pbarCaption = "Save File"
            pbarMsg = "Saving XYZ trajectory file " + os.path.basename(moviefile) + "..."
    else: 
        # Multiframe minimize
        if mflag:
            filesize = (max(100, int(sqrt(natoms))) * natoms * 3) + 4
            pbarCaption = "Minimize"
        # Simulate
        else:
            filesize = (assy.m.totalFrames * natoms * 3) + 4
            pbarCaption = "Simulator"
            pbarMsg = "Creating movie file " + os.path.basename(moviefile) + "..."
            msg = "Simulation started: Total Frames: " + str(assy.m.totalFrames)\
                    + ", Steps per Frame: " + str(assy.m.stepsper)\
                    + ", Temperature: " + str(assy.m.temp)
            assy.w.history.message(msg)

    # We can't overwrite an existing moviefile, so delete it if it exists.
    if os.path.exists(moviefile):
        print "assy.m.isOpen =",assy.m.isOpen
        if assy.m.isOpen: 
            print "closing moviefile"
            assy.m.fileobj.close()
            assy.m.isOpen = False
            print "fileIO.writemovie(). assy.m.isOpen =", assy.m.isOpen
        
        print "deleting moviefile: [",moviefile,"]"
        os.remove (assy.m.filename) # Delete before spawning simulator.

    # These are useful when debugging the simulator.     
    print  "program = ",program
    print  "Spawnv args are %r" % (args,) # this %r remains (see above)
    
    arguments = QStringList()
    for arg in args:
        arguments.append(arg)
    
    simProcess = None    
    try:
        ## Start the simulator in a different process 
        simProcess = QProcess()
        simProcess.setArguments(arguments)
        simProcess.start()
        
        # Launch the progress bar. Wait until simulator is finished
        r = assy.w.progressbar.launch( filesize,
                        moviefile, 
                        pbarCaption, 
                        pbarMsg, 
                        1)
       
        
    except: # We had an exception.
        print_compact_traceback("exception in simulation; continuing: ")
        if simProcess:
            #simProcess.tryTerminate()
	    simProcess.kill()
            simProcess = None
        r = -1 # simulator failure
        
    QApplication.restoreOverrideCursor() # Restore the cursor
    #assy.w.setCursor(oldCursor)
        
    if not r: return r # Main return
        
    if r == 1: # User pressed Abort button in progress dialog.
        msg = redmsg("Simulator: Aborted.")
        assy.w.history.message(msg)         
        
        ##Tries to terminate the process the nice way first, so the process
        ## can do whatever clean up it requires. If the process
        ## is still running after 2 seconds (a kludge). it terminates the 
        ## process the hard way.
        #simProcess.tryTerminate()
        #QTimer.singleShot( 2000, simProcess, SLOT('kill()') )
        simProcess.kill()
        
    else: # Something failed...
        msg = redmsg("Simulation failed: exit code %r " % r)
        assy.w.history.message(msg)

    return r