# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
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

nampat=re.compile("\\(([^)]*)\\)")
csyspat = re.compile("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
datumpat = re.compile("datum \((.+)\) \((\d+), (\d+), (\d+)\) (.*) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)")
keypat=re.compile("\S+")
molpat = re.compile("mol \(.*\) (\S\S\S)")
atom1pat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
atom2pat = re.compile("atom \d+ \(\d+\) \(.*\) (\S\S\S)")

# rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)
rmotpat = re.compile("rmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
lmotpat = re.compile("lmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")

# lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
lmotpat = re.compile("lmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")

# ground (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}
grdpat = re.compile("ground \((.+)\) \((\d+), (\d+), (\d+)\)")

# stat (name) (r, g, b) (temp) atom1 atom2 ... atom25 {up to 25}
statpat = re.compile("stat \((.+)\) \((\d+), (\d+), (\d+)\) \((\d+)\)" )

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
    
def insertmmp(assy, fileName):
    """Reading a mmp file and insert the part into the existing model """    
    groupList  = _readmmp(assy, fileName, isInsert = True)
    
    if len(groupList) != 3: print "wrong number of top-level groups"
    assy.tree.addmember(groupList[1])

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
                
        # Read the MMP record for a Rotary Motor as:
        # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)                           
        elif key == "rmotor":
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
            m=rmotpat.match(card)
            name = m.group(1)
            col=map(lambda (x): int(x)/255.0,
                    [m.group(2),m.group(3),m.group(4)])
            torq=float(m.group(5))
            sped=float(m.group(6))
            cxyz=A(map(float, [m.group(7),m.group(8),m.group(9)]))/1000.0
            axyz=A(map(float, [m.group(10),m.group(11),m.group(12)]))/1000.0
            prevmotor=RotaryMotor(assy)
            prevmotor.setProps(name, col, torq, sped, cxyz, axyz)
            opengroup.addmember(prevmotor)

        elif key == "shaft":
            list = map(int, re.findall("\d+",card[6:]))
            list = map((lambda n: ndix[n]), list)
            prevmotor.setShaft(list)
              
        # Read the MMP record for a Linear Motor as:
        # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
        elif key == "lmotor":
            if mol:
                mol = _addMolecule(mol, assy, opengroup)
            m=lmotpat.match(card)
            name = m.group(1)
            col=map(lambda (x): int(x)/255.0,
                    [m.group(2),m.group(3),m.group(4)])
            force=float(m.group(5))
            stiffness=float(m.group(6))
            cxyz=A(map(float, [m.group(7),m.group(8),m.group(9)]))/1000.0
            axyz=A(map(float, [m.group(10),m.group(11),m.group(12)]))/1000.0
            prevmotor=LinearMotor(assy)
            prevmotor.setProps(name, col, force, stiffness, cxyz, axyz)
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
    # stat (name) (r, g, b) (temp) atom1 atom2 ... atom25 {up to 25}
                
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
            list = map((lambda n: ndix[n]), list)
            
            sr = Stat(assy, list) # create stat and set props
            sr.name=name
            sr.color=col
            sr.temp=temp
            opengroup.addmember(sr)
 
        elif key=="csys": # Coordinate System
            if not isInsert: #Skip this record if inserting
                m=re.match(csyspat,card)
                name=m.group(1)
                wxyz = A(map(float, [m.group(2), m.group(3),
                                 m.group(4), m.group(5)]))
                scale=float(m.group(6))
                assy.csys = Csys(assy, name, scale, wxyz)
                opengroup.addmember(assy.csys)

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
            if not isInsert: #Skip this record if inserting
                m = re.match("kelvin (\d+)",card)
                n = int(m.group(1))
                assy.temperature = n
                
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

    
def insertmmp(assy, fileName):
    """Reading a mmp file and insert the part into the existing model """    
    groupList  = _readmmp(assy, fileName, isInsert = True)
    
    if len(groupList) != 3: print "wrong number of top-level groups"
    assy.tree.addmember(groupList[1])
    
# write all molecules, motors, grounds into an MMP file
def writemmp(assy, filename, addshelf = True):
    f = open(filename,"w")
    atnums = {}
    atnums['NUM'] = 0
    assy.alist = []
    
    f.write("kelvin %d\n" % assy.temperature)
    
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

    cdist = 5.0 # Camera distance
    zfactor = 0.4 # zoom factor
    up = V(0.0, zfactor, 0.0)
    right = V(1.33 * zfactor, 0.0, 0.0)

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
    
    # Camera info
    f.write("\ncamera {\n  location " + povpoint(cdist * assy.o.scale*assy.o.out-assy.o.pov) + "\n  up " + povpoint(up) + "\n  right " + povpoint(right) + "\n  sky " + povpoint(assy.o.up) + "\n  look_at " + povpoint(-assy.o.pov) + "\n}\n\n")
 
    # Write atoms and bonds in the part
    assy.tree.writepov(f, assy.o.display)

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
    # Invisible (not hidden) atoms are drawn
    # This is a bug to be fixed in the future.  Will require work in chunk & chem.writemdl, too.  
    # writepov may have this problem, too.
    # Mark [04-12-05]     
    for mol in assy.molecules: 
        if not mol.hidden or mol.disp != diINVISIBLE: natoms += len(mol.atoms)
    print "fileIO: natoms =", natoms

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