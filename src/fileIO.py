# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from Numeric import *
from VQT import *
from string import *
import re
from chem import *
from gadgets import *
from Utility import *



# read a Protein DataBank-format file into a single molecule
def readpdb(assy,filename):
    l=open(filename,"r").readlines()
    assy.filename=filename
    alist=[]
    ndix={}
    mol=molecule(assy, filename)
    for card in l:
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
    assy.addmol(mol)

# Write a single molecule into a Protein DataBank-format file 
def writepdb(assy, filename):
    f = open(filename, "w")
    # Atom object is the key, the atomIndex is the value  
    atomsTable = {}
    # Each element is a list of atoms connected with the 1rst atom
    connectList = []

    atomIndex = 1

    for mol in assy.selmols:
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


# read a Molecular Machine Part-format file into maybe multiple molecules
def readmmp(assy,filnam):
    l=open(filnam,"r").readlines()
    assy.filename=filnam
    mol = None
    ndix={}
    molDic = {}
    groupDic = {}
    assy.alist = []
   
    for card in l:
        key=card[:4]
        if key=="part":
            if mol: assy.addmol(mol)
            try: m=re.search("\((.+)\)", card[8:])
            except NameError: 
                       print "File reading: Molecule name error."
                       return
                       
            mol=molecule(assy,  m.group(1))
            molDic[m.group(1)] = mol
            assy.orderedItemsList += [mol]
            
            try: mol.setDisplay(dispNames.index(card[5:8]))
            except ValueError: mol.setDisplay(diDEFAULT)

            atomDisplay = None

        elif key == "atom":
            m=re.match("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)"
                       ,card)
            n=int(m.group(1))
            sym=PeriodicTable[int(m.group(2))].symbol
            xyz=A(map(float, [m.group(3),m.group(4),m.group(5)]))/1000.0
            a = atom(sym, xyz, mol)
            
            if  atomDisplay:
                    a.display = atomDisplay
                    
            assy.alist += [a]
            ndix[n]=a
            prevatom=a
            prevcard = card
            
        elif key == "bond":
            list=map(int, re.findall("\d+",card[5:]))
            try:
                for a in map((lambda n: ndix[n]), list):
                    mol.bond(prevatom, a)
            except KeyError:
                print "error in MMP file: atom ", prevcard
                print card
                
        elif key[:3] == "end":
            if mol: assy.addmol(mol)
            
        elif card[:5] == "rmoto":
            if mol:
                assy.addmol(mol)
                mol = None
            m=re.match("rmotor (-?\d+\.\d+), (-?\d+\.\d+), \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)", card)
            torq=float(m.group(1))
            sped=float(m.group(2))
            cxyz=A(map(float, [m.group(3),m.group(4),m.group(5)]))/1000.0
            axyz=A(map(float, [m.group(6),m.group(7),m.group(8)]))/1000.0
            prevmotor=motor(assy)
            prevmotor.setcenter(torq, sped, cxyz, axyz)
            
        elif key == "shaf":
            list = map(int, re.findall("\d+",card[6:]))
            list = map((lambda n: ndix[n]), list)
            prevmotor.setShaft(list)

        elif card[:5] == "lmoto":  # Linear Motor
            if mol:
                assy.addmol(mol)
                mol = None
            m = re.match("lmotor (-?\d+\.\d+), (-?\d+\.\d+), \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)", card)
            stiffness = float(m.group(1))
            force = float(m.group(2))
            cxyz = A(map(float, [m.group(3), m.group(4), m.group(5)]))/1000.0  
            axyz = A(map(float, [m.group(6), m.group(7), m.group(8)]))/1000.0
            prevmotor = LinearMotor(assy)
            prevmotor.setCenter(force, stiffness, cxyz, axyz)

        elif card[:6] == "ground":
            if mol:
                assy.addmol(mol)
                mol = None
            list = map(int, re.findall("\d+",card[7:]))
            list = map((lambda n: ndix[n]), list)
            ground(assy, list)
         
        elif key=="csys": # Coordinate System
            m=re.match("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)",card)
            name=m.group(1)
            wxyz = A(map(float, [m.group(2), m.group(3), m.group(4), m.group(5)]))
            zoom=float(m.group(6))
            assy.csys = Csys(name, zoom, wxyz)
            
        elif key=="datu": # Datum Plane
            m=re.match("datum \((.+)\) (.+) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)",card)
            name=m.group(1)
            type=m.group(2)
            vec1 = A(map(float, [m.group(3), m.group(4), m.group(5)]))
            vec2 = A(map(float, [m.group(6), m.group(7), m.group(8)]))
            vec3 = A(map(float, [m.group(9), m.group(10), m.group(11)]))
            vec4 = A(map(float, [m.group(12), m.group(13), m.group(14)]))
            #Datum(name,type,vec1,vec2,vec3,vec4)        
            
        elif card[:5] == "group": # Group of Molecules and/or Groups 
            #list = map(str, re.split("\)\s\(", card[6:]))
            list = card[6:].split(") (")
            m = list[len(list)-1][:-3]  #Remove ')\n'
            list[len(list)-1] = m
            name = list[0][1:]         # Remove '('
            
            members = []
            for mem in list[1:]:
                 rlt = re.match("<(.+)>", mem)
                 if rlt:
                         members += [groupDic[rlt.group(1)]]
                 else:
                         members += [molDic[mem]]
          
            memLength = len(members)
            totLength = len(assy.orderedItemsList)
            del assy.orderedItemsList[totLength-memLength:]
            newGroup = Group(name, members)
            assy.orderedItemsList += [newGroup]  
              
            groupDic[name] = newGroup
            
        elif key=="waal": # van der Waals Interactions
            list = map(int, re.findall("\d+", card[6:]))
            list = map((lambda n: ndix[n]), list)
            assy.waals = Waals(list)
            
        elif key=="kelv":  # Temperature in Kelvin
            m = re.match("kelvin (\d+)",card)
            n = int(m.group(1))
            assy.temperature = n  
            
        elif key=="show": #Display Representation Record
            m = re.match("show (.+)", card)
            smode=m.group(1)
         
            for count in range(len(dispNames)):
                if smode == dispNames[count]:
                    atomDisplay = count
                    break
            

def writeMolecule(mol, atnum, alist, atnums, f):
        carrydisp = dispNames[mol.display]
        f.write("part " + carrydisp + " (" + mol.name + ")\n")
        
        for a in mol.atoms.itervalues():
            alist += [a]
            atnums[a.key] = atnum
            disp = dispNames[a.display]
            if disp != carrydisp:
                f.write("show " + disp + "\n")
                carrydisp = disp
            xyz=a.posn()*1000
            n=(atnum, a.element.eltnum,
               int(xyz[0]), int(xyz[1]), int(xyz[2]))
            f.write("atom %d (%d) (%d, %d, %d)\n" % n)
            atnum += 1
            bl=[]
            for b in a.bonds:
                oa = b.other(a)
                if oa.key in atnums: bl += [atnums[oa.key]]
            if len(bl) > 0:
                f.write("bond1 " + " ".join(map(str,bl)) + "\n")
                
        for g in mol.gadgets:
            f.write(g.__repr__(atnums) + "\n")


def writeGroup(group, atnum, alist, atnums, f):
        for m in group.members:
                if isinstance(m, molecule):
                        writeMolecule(m, atnum, alist, atnums, f)
                else:
                        writeGroup(m, atnum, alist, atnums, f)
        f.write(group.__str__() + "\n")
                        
        

# write all molecules, motors, grounds into an MMP file
def writemmp(assy, filename):
    f = open(filename,"w")
    atnums = {}
    atnum = 1
    assy.alist = []
    
    assy.w.modelTreeView.saveModelTree()
    
    for mem in  assy.orderedItemsList:
        if isinstance(mem, molecule):
                writeMolecule(mem, atnum, assy.alist, atnums, f)
        elif isinstance(mem, Group):
                writeGroup(mem, atnum, assy.alist, atnums, f)

    f.write(assy.csys.__str__() + "\n")
    
    f.write("kelvin " + str(assy.temperature) + "\n")
    
    if assy.waals:
        f.write(assy.waals.__str__(atnums) + "\n")

                     
    f.write("end molecular machine part " + assy.name + "\n")
    f.close()