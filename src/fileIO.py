# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
# 10/4 currently being owned by Josh
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

nampat=re.compile("\\(([^)]*)\\)")
csyspat = re.compile("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
datumpat = re.compile("datum \((.+)\) \((\d+), (\d+), (\d+)\) (.*) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)")
keypat=re.compile("\S+")
molpat = re.compile("mol \(.*\) (\S\S\S)")
atom1pat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
atom2pat = re.compile("atom \d+ \(\d+\) \(.*\) (\S\S\S)")
rmotpat = re.compile("rmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")


def getname(str, default):
    x= nampat.search(str)
    if x: return x.group(1)
    return gensym(default)


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
    assy.alist = []
    assy.tree = Group("Root", assy, None)
    groupstack = []
    grouplist = []
    opengroup = None
 
    for card in l:
        key=keypat.match(card)
        if not key: continue
        key = key.group(0)

        if key == "group": # Group of Molecules and/or Groups
            name = getname(card, "Grp")
            opengroup = Group(name, assy, assy.tree)
            if not groupstack: grouplist += [opengroup]
            groupstack = [(opengroup, name)] + groupstack

        if key == "egroup": # Group of Molecules and/or Groups
            name = getname(card, "Grp")
            curgrp, curnam = groupstack[0]
            if name != curnam:
                print "mismatched group records:", name, curnam
                break
            if mol:
                assy.addmol(mol)
                mol.moveto(curgrp)
                mol = None
            groupstack = groupstack[1:]
            if groupstack: opengroup, junk = groupstack[0]
            else: opengroup = None

        elif key=="mol":
            if mol:
                assy.addmol(mol)
                mol.moveto(opengroup)
                mol = None
            name = getname(card, "Mole")
            mol=molecule(assy,  name)
            disp = molpat.match(card)
            mol.setDisplay(diDEFAULT)
            if disp:
                try: mol.setDisplay(dispNames.index(disp.group(1)))
                except ValueError: pass

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
                           
        elif key == "rmotor":
            if mol:
                assy.addmol(mol)
                mol.moveto(opengroup)
                mol = None
            m=rmotpat.match(card)
            name = m.group(1)
            col=map(lambda (x): int(x)/255.0,
                    [m.group(2),m.group(3),m.group(4)])
            torq=float(m.group(5))
            sped=float(m.group(6))
            cxyz=A(map(float, [m.group(7),m.group(8),m.group(9)]))/1000.0
            axyz=A(map(float, [m.group(10),m.group(11),m.group(12)]))/1000.0
            prevmotor=motor(assy)
            prevmotor.setcenter(torq, sped, cxyz, axyz)
            prevmotor.col=col
            opengroup.addmember(prevmotor)         
            
        elif key == "shaft":
            list = map(int, re.findall("\d+",card[6:]))
            list = map((lambda n: ndix[n]), list)
            prevmotor.setShaft(list)

        elif key == "lmotor":  # Linear Motor
            if mol:
                assy.addmol(mol)
                mol.moveto(opengroup)
                mol = None
            m = re.match("lmotor (-?\d+\.\d+), (-?\d+\.\d+), \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)", card)
            stiffness = float(m.group(1))
            force = float(m.group(2))
            cxyz = A(map(float, [m.group(3), m.group(4), m.group(5)]))/1000.0  
            axyz = A(map(float, [m.group(6), m.group(7), m.group(8)]))/1000.0
            prevmotor = LinearMotor(assy)
            prevmotor.setCenter(force, stiffness, cxyz, axyz)
            opengroup.addmember(prevmotor)         

        elif key == "ground":
            if mol:
                assy.addmol(mol)
                mol.moveto(opengroup)
                mol = None
            name = getname(card, "Gnd")
            # fix for color
            card =card[card.index(")")+1:]
            list = map(int, re.findall("\d+",card[card.index(")")+1:]))
            list = map((lambda n: ndix[n]), list)
            gr = ground(assy, list)
            gr.name=name
            opengroup.addmember(gr)
         
        elif key=="csys": # Coordinate System
            m=re.match(csyspat,card)
            name=m.group(1)
            wxyz = A(map(float, [m.group(2), m.group(3),
                                 m.group(4), m.group(5)]))
            scale=float(m.group(6))
            assy.csys = Csys(assy, name, scale, wxyz)
            opengroup.addmember(assy.csys)

        elif key=="datum": # Datum object
            if mol:
                assy.addmol(mol)
                mol.moveto(opengroup)
                mol = None
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
            m = re.match("kelvin (\d+)",card)
            n = int(m.group(1))
            assy.temperature = n  

    if len(grouplist) != 3: print "wrong number of top-level groups"
    else: assy.data, assy.tree, assy.shelf = grouplist
    assy.data.open = assy.shelf.open = False
    assy.root = Group("ROOT", assy, None, [assy.tree, assy.shelf])
            
# write all molecules, motors, grounds into an MMP file
def writemmp(assy, filename):
    f = open(filename,"w")
    atnums = {}
    atnums['NUM'] = 0
    assy.alist = []
    
    f.write("kelvin %d\n" % assy.temperature)
    
    assy.data.writemmp(atnums, assy.alist, f)
    assy.tree.writemmp(atnums, assy.alist, f)

    f.write("end1\n")
    
    assy.shelf.writemmp(atnums, assy.alist, f)
    
                     
    f.write("end molecular machine part " + assy.name + "\n")
    f.close()
