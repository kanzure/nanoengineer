# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
File IO functions for reading and writing PDB and MMP files

$Id$

###e this file should be split into several separate modules. [bruce 050405]

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
from chem import * # should get chunk.bond_atoms
from gadgets import *
from Utility import *
from povheader import povheader
from mdldata import *
from HistoryWidget import redmsg # bruce 050107
from elements import PeriodicTable

# == patterns for reading mmp files

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

# == pdb files (reading and writing)

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

# == reading mmp files

class _readmmp_state:
    """Hold the state needed by _readmmp between lines;
    and provide some methods to help with reading the lines.
    """
    #bruce 050405 made this class from most of _readmmp to help generalize it
    # (e.g. for reading sim input files for minimize selection)
    def __init__(self, assy, isInsert):
        self.assy = assy
        self.history = assy.w.history
        self.isInsert = isInsert
        #bruce 050405 made the following from old _readmmp localvars, and revised their comments
        self.mol = None # the current molecule being built, if any [bruce comment 050228]
        self.ndix = {}
        topgroup = Group("__opengroup__", assy, None)
            #bruce 050405 topgroup holds toplevel groups (or other items) as members; replaces old code's grouplist
        self.groupstack = [topgroup]
            #bruce 050405 revised this -- no longer stores names separately, and current group is now at end
            # stack (top at end) to store all unclosed groups
            # (the only group which can accept children, as we read the file, is always self.groupstack[-1];
            #  in the old code this was called opengroup [bruce 050405])
        self.sim_input_badnesses_so_far = {} # helps warn about sim-input files
        return

    def destroy(self):
        self.assy = self.history = self.mol = self.ndix = self.groupstack = None

    def extract_toplevel_items(self):
        """for use only when done: extract the list of toplevel items
        (removing them from our artificial Group if any);
        but don't verify they are Groups or alter them, that's up to the caller.
        """
        if len(self.groupstack) > 1:
            self.warning("mmp file had %d unclosed groups" % len(self.groupstack) - 1)
        topgroup = self.groupstack[0]
        self.groupstack = "error if you keep reading after this"
        res = topgroup.members[:]
        for m in res:
            topgroup.delmember(m)
        return res

    def warning(self, msg):
        self.history.message( redmsg( "Warning: " + msg))

    def format_error(self, msg): ###e use more?
        self.history.message( redmsg( "Warning: mmp format error: " + msg)) ###e and say what we'll do? review calls; syntax error
    
    def readmmp_line(self, card):
        "returns None, or error msg(#k), or raises exception on bugs or maybe some syntax errors"
        key_m = keypat.match(card)
        if not key_m:
            # ignore blank lines (does this also ignore some erroneous lines??) #k
            return
        key = key_m.group(0)
        # key should now be the mmp record type, e.g. "group" or "mol"
        try:
            linemethod = getattr(self, "_read_" + key) # e.g. _read_group, _read_mol, ...
        except AttributeError:
            # unrecognized mmp record; not an error, since the format
            # is meant to be upward-compatible when new records are added,
            # as long as it's ok for old code to ignore them and not signal an error.
            errmsg = None
            #bruce 050217 new debug feature: warning for unrecognized record
            #e (maybe only do this the first time we see it?)
            if platform.atom_debug:
                print "atom_debug: fyi: unrecognized mmp record type ignored (not an error): %r" % key
        except:
            # bug, or syntax error (e.g. from non-identifier chars in key? not sure if that triggers this)
            errmsg = "syntax error or bug" ###e improve message
        else:
            # if linemethod itself has an exception, best to let the caller handle it
            # (only it knows whether the line passed to us was made up or really in the file)
            return linemethod(card)
                # note: no need to pass 'self', since this is a bound method
        return errmsg
    
    def _read_group(self, card): # group: begins a Group (of chunks, jigs, and/or Groups)
        #bruce 050405 revised this; it can be further simplified
        name = getname(card, "Grp")
        assert name != None #bruce 050405 hope/guess
        old_opengroup = self.groupstack[-1]
        new_opengroup = Group(name, self.assy, old_opengroup) # this includes addchild of new group to old_opengroup
        self.groupstack.append(new_opengroup)

    def _read_egroup(self, card): # egroup: close the current group record
        #bruce 050405 revised this; it can be further simplified
        name = getname(card, "Grp")
        assert name != None #bruce 050405 hope/guess
        if len(self.groupstack) == 1:
            return "egroup %r when no groups remain unclosed" % (name,)
        curgroup = self.groupstack.pop()
        curname = curgroup.name
        if name != curname:
            # note, unlike old code we've already popped a group; shouldn't matter [bruce 050405]
            return "mismatched group records: egroup %r tried to match group %r" % (name, curname) #bruce 050405 revised this msg
        return None # success
    
    def _read_mol(self, card): # mol: start a molecule
        name = getname(card, "Mole")
        mol = molecule(self.assy,  name)
        self.mol = mol # so its atoms, etc, can find it (might not be needed if they'd search for it) [bruce 050405 comment]
            # now that I removed _addMolecule, this is less often reset to None,
            # so we'd detect more errors if they did search for it [bruce 050405]
        disp = molpat.match(card)
        if disp:
            try: mol.setDisplay(dispNames.index(disp.group(1)))
            except ValueError: pass
        #bruce 050405: removing the following, since disp is already that,
        # and its other side effects are not needed unless disp changes.
##            else:
##                mol.setDisplay(diDEFAULT)
        self.addmember(mol) #bruce 050405; removes need for _addMolecule

    def _read_atom(self, card):
        m = atom1pat.match(card)
        if not m:
            print card
        n = int(m.group(1))
        sym = PeriodicTable.getElement(int(m.group(2))).symbol
        xyz = A(map(float, [m.group(3),m.group(4),m.group(5)]))/1000.0
        if not self.mol:
            #bruce 050405 new feature for reading new bare sim-input mmp files
            self.guess_sim_input('missing_group_or_chunk')
            self.mol = molecule(self.assy,  "sim chunk")
            self.addmember(self.mol)
        a = atom(sym, xyz, self.mol)
        disp = atom2pat.match(card)
        if disp:
            try: a.setDisplay(dispNames.index(disp.group(1)))
            except ValueError: pass
        self.ndix[n] = a
        self.prevatom = a
        self.prevcard = card
        
    def _read_bond1(self, card):
        list = map(int, re.findall("\d+",card[5:]))
        try:
            for a in map((lambda n: self.ndix[n]), list):
                bond_atoms( self.prevatom, a)
        except KeyError:
            print "error in MMP file: atom ", self.prevcard
            print card
            
    # Read the MMP record for a Rotary Motor as either:
    # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az) length, radius, spoke_radius
    # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)
    def _read_rmotor(self, card):
        m = new_rmotpat.match(card) # Try to read card with new format
        if not m: m = old_rmotpat.match(card) # If that didn't work, read card with old format
        ngroups = len(m.groups()) # ngroups = number of fields found (12=old, 15=new)
        name = m.group(1)
        col = map(lambda (x): int(x)/255.0,
                [m.group(2),m.group(3),m.group(4)])
        torq = float(m.group(5))
        sped = float(m.group(6))
        cxyz = A(map(float, [m.group(7),m.group(8),m.group(9)]))/1000.0
        axyz = A(map(float, [m.group(10),m.group(11),m.group(12)]))/1000.0
        if ngroups == 15: # if we have 15 fields, we have the length, radius and spoke radius.
            length = float(m.group(13))
            radius = float(m.group(14))
            sradius = float(m.group(15))
        else: # if not, set the default values for length, radius and spoke radius.
            length = 10.0
            radius = 2.0
            sradius = 0.5
        motor = RotaryMotor(self.assy)
        motor.setProps(name, col, torq, sped, cxyz, axyz, length, radius, sradius)
        self.addmotor(motor)

    def addmotor(self, motor): #bruce 050405 split this out
        self.addmember(motor)
        self.prevmotor = motor # might not be needed if we just looked for it when we need it [bruce 050405 comment]

    def _read_shaft(self, card):
        list = map(int, re.findall("\d+",card[6:]))
        list = map((lambda n: self.ndix[n]), list)
        self.prevmotor.setShaft(list)
          
    # Read the MMP record for a Linear Motor as:
    # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az) length, width, spoke_radius
    # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
    def _read_lmotor(self, card):
        m = new_lmotpat.match(card) # Try to read card with new format
        if not m: m = old_lmotpat.match(card) # If that didn't work, read card with old format
        ngroups = len(m.groups()) # ngroups = number of fields found (12=old, 15=new)
        name = m.group(1)
        col = map(lambda (x): int(x)/255.0,
                [m.group(2),m.group(3),m.group(4)])
        force = float(m.group(5))
        stiffness = float(m.group(6))
        cxyz = A(map(float, [m.group(7),m.group(8),m.group(9)]))/1000.0
        axyz = A(map(float, [m.group(10),m.group(11),m.group(12)]))/1000.0
        if ngroups == 15: # if we have 15 fields, we have the length, width and spoke radius.
            length = float(m.group(13))
            width = float(m.group(14))
            sradius = float(m.group(15))
        else: # if not, set the default values for length, width and spoke radius.
            length = 10.0
            width = 2.0
            sradius = 0.5
        motor = LinearMotor(self.assy)
        motor.setProps(name, col, force, stiffness, cxyz, axyz, length, width, sradius)
        self.addmotor(motor)

    # Read the MMP record for a Ground as:
    # ground (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}

    def _read_ground(self, card):
        m = grdpat.match(card)
        name = m.group(1)
        col = map(lambda (x): int(x)/255.0,
                [m.group(2),m.group(3),m.group(4)])

        # Read in the list of atoms
        card = card[card.index(")")+1:] # skip past the color field
        list = map(int, re.findall("\d+",card[card.index(")")+1:]))
        list = map((lambda n: self.ndix[n]), list)
        
        gr = Ground(self.assy, list) # create ground and set props
        gr.name = name
        gr.color = col
        self.addmember(gr)

    # Read the MMP record for a Thermostat as:
    # stat (name) (r, g, b) (temp) first_atom last_atom box_atom
            
    def _read_stat(self, card):
        m = statpat.match(card)
        name = m.group(1)
        col = map(lambda (x): int(x)/255.0,
                [m.group(2),m.group(3),m.group(4)])
        temp = m.group(5)

        # Read in the list of atoms
        card = card[card.index(")")+1:] # skip past the color field
        card = card[card.index(")")+1:] # skip past the temp field
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
            msg = "a thermostat record was found (" + name + ") in the part which contained extra atoms.  They will be ignored."
            self.warning(msg)
            
        list = map((lambda n: self.ndix[n]), list)

        sr = Stat(self.assy, list) # create stat and set props
        sr.name = name
        sr.color = col
        sr.temp = temp
        self.addmember(sr)

    # Read the MMP record for a Thermometer as:
    # thermo (name) (r, g, b) first_atom last_atom box_atom
            
    def _read_thermo(self, card):
        m = thermopat.match(card)
        name = m.group(1)
        col = map(lambda (x): int(x)/255.0,
                [m.group(2),m.group(3),m.group(4)])

        # Read in the list of atoms
        card = card[card.index(")")+1:] # skip past the color field
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
            msg = "a thermometer record was found in the part which contained extra atoms.  They will be ignored."
            self.warning(msg)
            
        list = map((lambda n: self.ndix[n]), list)

        sr = Thermo(self.assy, list) # create stat and set props
        sr.name = name
        sr.color = col
        self.addmember(sr)
         
    def _read_csys(self, card): # csys -- Coordinate System
        if not self.isInsert: #Skip this record if inserting
            ###Huaicai 1/27/05, new file format with home view 
            ### and last view information        
            m = new_csyspat.match(card)
            if m:        
                    name = m.group(1)
                    wxyz = A(map(float, [m.group(2), m.group(3),
                             m.group(4), m.group(5)]))
                    scale = float(m.group(6))
                    pov = A(map(float, [m.group(7), m.group(8), m.group(9)]))
                    zoomFactor = float(m.group(10))
                    if (name == "HomeView"):
                            self.assy.homeCsys = Csys(self.assy, name, scale, pov, zoomFactor, wxyz)
                            self.addmember(self.assy.homeCsys)
                    elif (name == "LastView"):                         
                            self.assy.lastCsys = Csys(self.assy, name, scale, pov, zoomFactor, wxyz)
                            self.addmember(self.assy.lastCsys)
            else:
              m = old_csyspat.match(card)
              if m:
                    name = m.group(1)
                    wxyz = A(map(float, [m.group(2), m.group(3),
                             m.group(4), m.group(5)]))
                    scale = float(m.group(6))
                    self.assy.homeCsys = Csys(self.assy, "OldVersion", scale, V(0,0,0), 1.0, wxyz)
                    self.addmember(self.assy.homeCsys)
                    self.assy.lastCsys = Csys(self.assy, "LastView", scale, V(0,0,0), 1.0, A([0.0, 1.0, 0.0, 0.0]))
                    self.addmember(self.assy.lastCsys)

    def _read_datum(self, card): # datum -- Datum object
        if not self.isInsert: #Skip this record if inserting
            m = re.match(datumpat,card)
            if not m:
                self.warning("mmp syntax error; ignoring line: %r" % card)
                return
            name = m.group(1)
            type = m.group(5)
            col = tuple(map(int, [m.group(2), m.group(3), m.group(4)]))
            vec1 = A(map(float, [m.group(6), m.group(7), m.group(8)]))
            vec2 = A(map(float, [m.group(9), m.group(10), m.group(11)]))
            vec3 = A(map(float, [m.group(12), m.group(13), m.group(14)]))
            new = Datum(self.assy,name,type,vec1,vec2,vec3)
            self.addmember(new)
            new.rgb = col

    def addmember(self, thing): #bruce 050405 split this out
        self.groupstack[-1].addchild(thing)
        
    def _read_waals(self, card): # waals -- van der Waals Interactions
        pass # code was wrong -- to be implemented later
        
    def _read_kelvin(self, card): # kelvin -- Temperature in Kelvin (simulation parameter)
        if not self.isInsert: # Skip this record if inserting
            m = re.match("kelvin (\d+)",card)
            n = int(m.group(1))
            self.assy.temperature = n
            
    def _read_mmpformat(self, card): # mmpformat -- MMP File Format. Mark 050130
        if not self.isInsert: # Skip this record if inserting
            m = re.match("mmpformat (.*)",card)
            self.assy.mmpformat = m.group(1)

    ## [bruce 050324 commenting out movieID until it's used; strategy for this will change, anyway.]                
##        def _read_movie_id(self, card): # movie_id -- Movie ID - To be supported for Beta.  Mark 05-01-16
##            if not self.isInsert: # Skip this record if inserting
##                m = re.match("movie_id (\d+)",card)
##                n = int(m.group(1))
##                self.assy.movieID = n
            
    def _read_end1(self, card): # end1 -- End of main tree
        pass

    def _read_end(self, card): # end -- end of file
        pass
    
    def _read_info(self, card):
        #bruce 050217 new mmp record, for optional info about
        # various types of objects which occur earlier in the file
        # (what I mean by "optional" is that it's never an error for the
        #  specified type of thing or type of info to not be recognized,
        #  as can happen when a new file is read by older code)
        
        # Find current chunk -- how we do this depends on details of
        # the other mmp-record readers in this big if/elif statement,
        # and is likely to need changing sometime. It's self.mol.
        # Now make dict of all current items that info record might refer to.
        currents = dict(chunk = self.mol)
        interp = mmp_interp(self.ndix) #e could optim by using the same object each time
        readmmp_info(card, currents, interp) # has side effect on object referred to by card
        return

    def guess_sim_input(self, type): #bruce 050405
        """Caller finds (and will correct) weird structure which makes us guess
        this is a sim input file of the specified type;
        warn user if you have not already given the same warning
        (normally only one such warning should appear, so warn about that as well).
        """
        # once we see how this is used, we'll revise it to be more like a "state machine"
        # knowing the expected behavior for the various types of files.
        bad_to_worse = ['no_shelf','one_part','missing_group_or_chunk'] # order is not yet used
        badness = bad_to_worse.index(type)
        if badness not in self.sim_input_badnesses_so_far:
            self.sim_input_badnesses_so_far[badness] = type
            if type == 'missing_group_or_chunk' or type == 'one_part':
                # (this message is a guess, since erroneous files could give rise to this too)
                msg = "this mmp file was probably written as simulator input; " \
                      "it's missing some structure and won't be readable by versions before Alpha5." #e revise version name
            elif type == 'no_shelf':
                # (this might not happen at all for files written by Alpha5 and beyond)
                # comment from old code's fix_grouplist:
                #bruce 050217 upward-compatible reader extension (needs no mmpformat-record change):
                # permit missing 3rd group, so we can read mmp files written as input for the simulator
                # (and since there is no good reason not to!)
                msg = "this mmp file was written as input for the simulator, and contains no clipboard items" #e add required version
            else:
                msg = "bug in guess_sim_input: missing message for %r" % type
            self.warning( msg)
            # normally only one of these warnings will occur, so we also ought to warn if that is not what happens...
            if len(self.sim_input_badnesses_so_far) > 1:
                self.format_error("the prior warnings should not appear together for the same file")
        return
    
    pass # end of class _readmmp_state

# helpers for _read_info method:

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

# ==

def _readmmp(assy, filename, isInsert = False): #bruce 050405 revised code & docstring
    """Read an mmp file, print errors and warnings to assy.history,
    modify assy in various ways (a bad design, see comment in insertmmp)
    (but don't actually add file contents to assy -- let caller do that if and where it prefers),
    and return either None (after an error for which caller should store no file contents at all)
    or a list of 3 Groups, which caller should treat as having roles "data", "tree", "shelf",
    regardless of how many toplevel items were in the file, or of whether they were groups.
    (We handle normal mmp files with exactly those 3 groups, old sim-input files with only
    the first two, and newer sim-input files for Parts (one group) or for minimize selection
    (maybe no groups at all). And most other weird kinds of mmp files someone might create.)
    """
    state = _readmmp_state( assy, isInsert)
    lines = open(filename,"rU").readlines()
        # 'U' in filemode is for universal newline support
    if not isInsert:
        assy.filename = filename ###e would it be better to do this at the end, and not at all if we fail?
    for card in lines:
        try:
            errmsg = state.readmmp_line( card) # None or an error message
        except:
            # note: the following two error messages are similar but not identical
            errmsg = "bug while reading this mmp line: %s" % (card,) #e include line number; note, two lines might be identical
            print_compact_traceback("bug while reading this mmp line:\n  %s\n" % (card,) )
        #e assert errmsg is None or a string
        if errmsg:
            ###e general history msg for stopping early on error
            ###e special return value then??
            break
    grouplist = state.extract_toplevel_items() # for a normal mmp file this has 3 Groups, whose roles are data, tree, shelf

    # now fix up sim input files and other nonstandardly-structured files;
    # use these extra groups if necessary, else discard them:
    data = Group("data", assy, None)
    shelf = Group("Clipboard", assy, None) # name might not matter
    
    for g in grouplist:
        if not g.is_group(): # might happen for files that ought to be 'one_part', too, I think, if clipboard item was not grouped
            state.guess_sim_input('missing_group_or_chunk') # normally same warning already went out for the missing chunk 
            tree = Group("tree", assy, None, grouplist)
            grouplist = [ data, tree, shelf ]
            break
    if len(grouplist) == 0:
        state.format_error("nothing in file")
        return None
    elif len(grouplist) == 1:
        state.guess_sim_input('one_part')
            # note: 'one_part' gives same warning as 'missing_group_or_chunk' as of 050406
        tree = Group("tree", assy, None, grouplist) #bruce 050406 removed [0] to fix bug in last night's new code
        grouplist = [ data, tree, shelf ]
    elif len(grouplist) == 2:
        state.guess_sim_input('no_shelf')
        grouplist.append( shelf)
    elif len(grouplist) > 3:
        state.format_error("more than 3 toplevel groups -- treating them all as in the main part")
            #bruce 050405 change; old code discarded all the data
        tree = Group("tree", assy, None, grouplist)
        grouplist = [ data, tree, shelf ]
    else:
        pass # nothing was wrong!
    assert len(grouplist) == 3
        
    state.destroy() # not before now, since it keeps track of which warnings we already emitted 
    return grouplist # from _readmmp

# read a Molecular Machine Part-format file into maybe multiple molecules
def readmmp(assy, filename): #bruce 050302 split out some subroutines for use in other code
    """Read an mmp file to create a new model (including a new Clipboard)."""
    grouplist = _readmmp(assy, filename)
    reset_grouplist(assy, grouplist) # handles grouplist == None (though not very well)
    return
    
def reset_grouplist(assy, grouplist):
    #bruce 050302 split this out of readmmp;
    # it should be entirely rewritten and become an assy method
    """[private]
    stick a new grouplist into assy, within readmmp;
    if grouplist is None, indicating file had bad format,
    do some but not all of the usual side effects.
    Otherwise grouplist must be a list of exactly 3 Groups (not checked),
    which we treat as data, tree, shelf.
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

def insertmmp(assy, filename): #bruce 050405 revised to fix one or more assembly/part bugs, I hope
    """Read an mmp file and insert its main part into the existing model."""
    grouplist  = _readmmp(assy, filename, isInsert = True)
        # isInsert = True prevents most side effects on assy;
        # a better design would be to let the caller do them (or not)
    if grouplist:
        data, mainpart, shelf = grouplist
        del data, shelf
        assy.part.ensure_toplevel_group()
        assy.part.topnode.addchild( mainpart )
    return

# == writing mmp files

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
                self.write("\n# error while writing file; stopping here, might be incomplete\n")
                #e maybe should include an optional error message from the caller
                #e maybe should write something formal and/or incorrect so file can't be read w/o noticing this error
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
        assert atom.key not in atnums # new assertion, bruce 030522
        atnums['NUM'] += 1 # old kluge, to be removed
        num = atnums['NUM']
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
    # Also, there's now an assy method which calls it
    # and a sister function for Parts which has a Part method.

    assy.update_parts() #bruce 050325 precaution
    
    if addshelf:
        workaround_for_bug_296( assy)
    else:
        workaround_for_bug_296( assy, onepart == assy.tree.part)
    
    ##Huaicai 1/27/05, save the last view before mmp file saving
    assy.o.saveLastView(assy)
    
    fp = open(filename, "w")

    mapping = writemmp_mapping(assy) ###e should pass sim or min options when used that way...
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

# ==

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
    
# ==

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
    
# ==

###e these should be moved into some other file [bruce 050405 comment]

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

# end

