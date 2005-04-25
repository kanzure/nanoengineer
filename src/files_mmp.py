# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
files_mmp.py -- reading and writing MMP files

$Id$

History: bruce 050414 pulled this out of fileIO.py rev. 1.97
(of which it was the major part),
since I am splitting that into separate modules for each file format.

Perhaps it should be further split into a reading and writing module,
since it's still large, and the code for those is not very related.

Note that a lot of mmp writing code remains in other files,
mainly (but not only) for the classes molecule, atom, and Jig.
(So it's hard to argue that it should not be split in order to
keep the reading and writing code for one format together --
since it's mostly not together now.)

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
when the info record was added, for info chunk hotspot.
(The optional part needs incrementing whenever more kinds of info records
are interpretable, at least once per "release".)

'050130 required; 050421 optional' -- bruce, adding new info records,
namely "info leaf hidden" and "info opengroup open";
and adding "per-part views" in the initial data group,
whose names are HomeView%d and LastView%d. All these changes are
backward-compatible -- old code will ignore the new records.

'050130 required; 050422 optional' -- bruce, adding forward_ref,
info leaf forwarded, and info leaf disabled.

===

General notes about when to change the mmp format version:
see a separate file, fileIO-doc.txt.

[That file has not been renamed, even though this one is no longer fileIO.py.]

[bruce 050227 moved those notes out of this docstring and into that
new file, which is initially in the same directory as this file.]

"""

MMP_FORMAT_VERSION_TO_WRITE = '050130 required; 050422 optional'
    #bruce modified this to indicate required & ideal reader versions... see general notes above.

from Numeric import *
from VQT import *
from string import * # this might no longer be needed [bruce 050414 comment]
import re
from chem import * # needed for atom, bond_atoms, maybe not anything else [bruce 050414 guess]
from jigs import *
from Utility import *
from povheader import povheader, povpoint # this might no longer be needed [bruce 050414 comment]
from mdldata import * # this might no longer be needed [bruce 050414 comment]
from HistoryWidget import redmsg
from elements import PeriodicTable

# == patterns for reading mmp files

#bruce 050414 comment: these pat constants are not presently used in any other files.

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

# == reading mmp files

class _readmmp_state:
    """Hold the state needed by _readmmp between lines;
    and provide some methods to help with reading the lines.
    [See also the classes mmp_interp (another read-helper)
     and writemmp_mapping.]
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
        self.markers = {} #bruce 050422 for forward_ref records
        return

    def destroy(self):
        self.assy = self.history = self.mol = self.ndix = self.groupstack = self.markers = None

    def extract_toplevel_items(self):
        """for use only when done: extract the list of toplevel items
        (removing them from our artificial Group if any);
        but don't verify they are Groups or alter them, that's up to the caller.
        """
        for marker in self.markers.values():
            marker.kill() #bruce 050422; semi-guess
        self.markers = None
        if len(self.groupstack) > 1:
            self.warning("mmp file had %d unclosed groups" % (len(self.groupstack) - 1))
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
        new_opengroup = Group(name, self.assy, old_opengroup)
            # this includes addchild of new group to old_opengroup (so don't call self.addmember)
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
        #bruce 050418 revising this to not have side effects on assy.
        # Instead, caller can do that by scanning the group these are read into.
        # This means we can now ignore the isInsert flag and always return
        # these records. Finally, I'll return them all, not just the ones with
        # special names we recognize (the prior code only called self.addmember
        # if the csys name was HomeView or LastView); caller can detect those
        # special names when it needs to.
        ## if not self.isInsert: #Skip this record if inserting
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
            csys = Csys(self.assy, name, scale, pov, zoomFactor, wxyz)
            self.addmember( csys) # regardless of name; no side effects on assy (yet) for any name,
                # though later code will recognize the names HomeView and LastView and treat them specially
                # (050421 extension: also some related names, for Part views)
        else:
            m = old_csyspat.match(card)
            if m:
                name = m.group(1)
                wxyz = A(map(float, [m.group(2), m.group(3),
                         m.group(4), m.group(5)]))
                scale = float(m.group(6))
                homeCsys = Csys(self.assy, "OldVersion", scale, V(0,0,0), 1.0, wxyz)
                    #bruce 050417 comment
                    # (about Huaicai's preexisting code, some of which I moved into this file 050418):
                    # this name "OldVersion" is detected in fix_assy_and_glpane_views_after_readmmp
                    # (called from MWsemantics.fileOpen, one of our callers)
                    # and changed to "HomeView", also triggering other side effects on glpane at that time.
                lastCsys = Csys(self.assy, "LastView", scale, V(0,0,0), 1.0, A([0.0, 1.0, 0.0, 0.0]))
                self.addmember(homeCsys)
                self.addmember(lastCsys)
            else:
                print "bad format in csys record, ignored:", csys #bruce 050418
        return

# bruce 050417: removing class Datum (and ignoring its mmp record "datum"),
# since it has no useful effect (and not writing it will not even be
# noticed by old code reading our mmp files). But the code should be kept around,
# since we might reuse some of it when we someday have real "datum planes".
# More info about this can be found in other comments/emails.
##    def _read_datum(self, card): # datum -- Datum object
##        if not self.isInsert: #Skip this record if inserting
##            m = re.match(datumpat,card)
##            if not m:
##                self.warning("mmp syntax error; ignoring line: %r" % card)
##                return
##            name = m.group(1)
##            type = m.group(5)
##            col = tuple(map(int, [m.group(2), m.group(3), m.group(4)]))
##            vec1 = A(map(float, [m.group(6), m.group(7), m.group(8)]))
##            vec2 = A(map(float, [m.group(9), m.group(10), m.group(11)]))
##            vec3 = A(map(float, [m.group(12), m.group(13), m.group(14)]))
##            new = Datum(self.assy,name,type,vec1,vec2,vec3)
##            self.addmember(new)
##            new.rgb = col

    def _read_datum(self, card): # datum -- Datum object -- old version deprecated by bruce 050417
        pass # don't warn about an unrecognized mmp record, even when atom_debug

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
        currents = dict(
            chunk = self.mol,
            opengroup = self.groupstack[-1], #bruce 050421
            leaf = ([None] + self.groupstack[-1].members)[-1] #bruce 050421
        )
        interp = mmp_interp(self.ndix, self.markers) #e could optim by using the same object each time [like 'self']
        readmmp_info(card, currents, interp) # has side effect on object referred to by card
        return

    def _read_forward_ref(self, card):
        "forward_ref (%s) ..."
        # add a marker which can be used later to insert the target node in the right place,
        # and also remember the marker here in the mapping (so we can offer that service) ###doc better ###@@@ def & call service
        lp_id_rp = card.split()[1]
        assert lp_id_rp[0] + lp_id_rp[-1] == "()"
        ref_id = lp_id_rp[1:-1]
        marker = MarkerNode(self.assy, ref_id) # note: we remove this if not used, so its node type might not matter much.
        self.addmember(marker)
        self.markers[ref_id] = marker

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
                # (#e To narrow down the cmd that wrote it, we'd need more info than type or
                #  even file comment, from old files -- sorry; maybe we should add an mmp record for
                #  the command that made the file! Will it be bad that file contents are nondet (eg for md5)?
                #  Probably not, since they were until recently anyway, due to dict item arb order.)
                msg = "mmp file probably written by Minimize or Simulate -- " \
                      "lacks original file's chunk/group structure and display modes; " \
                      "unreadable by pre-Alpha5 versions unless resaved." #e revise version name
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

# helper for forward_ref

class MarkerNode(Node):
    def __init__(self, assy, ref_id):
        name = ref_id
        Node.__init__(self, assy, name) # will passing no assy be legal? I doubt it... so don't bother trying.
        return
    pass

# helpers for _read_info method:

class mmp_interp: #bruce 050217; revised docstrings 050422
    """helps translate object refs in mmp file to their objects, while reading the file
    [compare to class writemmp_mapping, which helps turn objs to their refs while writing the file]
    [but also compare to class _readmmp_state... maybe this should be the same object as that. ###k]
    """
    def __init__(self, ndix, markers):
        self.ndix = ndix # maps atom numbers to atoms (??)
        self.markers = markers
    def atom(self, atnum):
        """map atnum string to atom, while reading mmp file
        (raises KeyError if that atom-number isn't recognized,
         which is an mmp file format error)
        """
        return self.ndix[int(atnum)]
    def move_forwarded_node( self, node, val):
        "find marker based on val, put node after it, and then del the marker"
        try:
            marker = self.markers.pop(val) # val is a string; should be ok since we also read it as string from forward_ref record
        except KeyError:
            assert 0, "mmp format error: no forward_ref was written for this forwarded node" ###@@@ improve errmsg
        marker.addsibling(node)
        marker.kill()
    pass

def readmmp_info( card, currents, interp ): #bruce 050217; revised 050421
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
    type = what[0] # as of 050421 this can be 'chunk' or 'opengroup' or 'leaf' ###k
    name = what[1:] # list of words (typically contains exactly one word, an attribute-name)
    thing = currents.get(type)
    if thing: # can be false if type not recognized, or if current one was None
        # record info about the current thing of type <type>
        try:
            meth = getattr(thing, "readmmp_info_%s_setitem" % type) # should be safe regardless of the value of 'type'
        except AttributeError:
            if platform.atom_debug:
                print "atom_debug: fyi: object %r doesn't accept \"info %s\" keys (like %r); ignoring it (not an error)" \
                      % (thing, type, name)
        else:
            try:
                meth( name, val, interp )
            except:
                print_compact_traceback("internal error in %r interpreting %r, ignored: " % (thing,card) )
    elif platform.atom_debug:
        print "atom_debug: fyi: no object found for \"info %s\"; ignoring info record (not an error)" % (type,)
    return

# ==

def _readmmp(assy, filename, isInsert = False): #bruce 050405 revised code & docstring
    """Read an mmp file, print errors and warnings to assy.history,
    modify assy in various ways (a bad design, see comment in insertmmp)
    (but don't actually add file contents to assy -- let caller do that if and where it prefers),
    and return either None (after an error for which caller should store no file contents at all)
    or a list of 3 Groups, which caller should treat as having roles "viewdata", "tree", "shelf",
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
    grouplist = state.extract_toplevel_items() # for a normal mmp file this has 3 Groups, whose roles are viewdata, tree, shelf

    #bruce 050418: if my fixes today for HomeView & LastView work, then following comment is obs: ###@@@
    # Note about homeView and lastView [bruce 050407]... not yet ready to commit.
    # See bruce's fileIO-data-fixer.py file (at home) [renamed data as viewdata 050418] for not-yet-right comment and code.
    # Meanwhile, if we're reading a sim-input file or other erroneous file which
    # uses the following fake 'viewdata' group, its views will be unsavable
    # even if you resave it and reload it and resave it, etc,
    # unless we fix this elsewhere, maybe in reset_grouplist below. ###@@@
    
    # now fix up sim input files and other nonstandardly-structured files;
    # use these extra groups if necessary, else discard them:
    viewdata = Group("Fake View Data", assy, None) # name is never used or stored
    shelf = Group("Clipboard", assy, None) # name might not matter since caller resets it
    
    for g in grouplist:
        if not g.is_group(): # might happen for files that ought to be 'one_part', too, I think, if clipboard item was not grouped
            state.guess_sim_input('missing_group_or_chunk') # normally same warning already went out for the missing chunk 
            tree = Group("tree", assy, None, grouplist)
            grouplist = [ viewdata, tree, shelf ]
            break
    if len(grouplist) == 0:
        state.format_error("nothing in file")
        return None
    elif len(grouplist) == 1:
        state.guess_sim_input('one_part')
            # note: 'one_part' gives same warning as 'missing_group_or_chunk' as of 050406
        tree = Group("tree", assy, None, grouplist) #bruce 050406 removed [0] to fix bug in last night's new code
        grouplist = [ viewdata, tree, shelf ]
    elif len(grouplist) == 2:
        state.guess_sim_input('no_shelf')
        grouplist.append( shelf)
    elif len(grouplist) > 3:
        state.format_error("more than 3 toplevel groups -- treating them all as in the main part")
            #bruce 050405 change; old code discarded all the data
        tree = Group("tree", assy, None, grouplist)
        grouplist = [ viewdata, tree, shelf ]
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
    Stick a new just-read grouplist into assy, within readmmp.
       If grouplist is None, indicating file had bad format,
    do some but not all of the usual side effects.
    [appropriateness of behavior for grouplist == None is unreviewed]
       Otherwise grouplist must be a list of exactly 3 Groups
    (though this is not fully checked here),
    which we treat as viewdata, tree, shelf.
       Changed viewdata behavior 050418:
    We used to assume (if necessary) that viewdata contains Csys records
    which, when parsed during _readmmp, had side effects of storing themselves in assy
    (which was a bad design).
    Now we scan it and perform those side effects ourselves.
    """
    #bruce 050418: revising this for assy/part split
    from Utility import kluge_patch_assy_toplevel_groups
    if grouplist == None:
        # do most of what old code did (most of which probably shouldn't be done,
        # but this needs more careful review (especially in case old code has
        # already messed things up by clearing assy), and merging with callers,
        # which don't even check for any kind of error return from readmmp),
        # except (as of 050418) don't do any side effects from viewdata.
        # Note: this is intentionally duplicated with code from the other case,
        # since the plan is to clean up each case independently.
        assy.shelf.name = "Clipboard"
        assy.shelf.open = False
        assy.root = Group("ROOT", assy, None, [assy.tree, assy.shelf])
        kluge_patch_assy_toplevel_groups(assy)
        assy.update_parts()
        return
    viewdata, tree, shelf = grouplist
        # don't yet store these in any Part, since those will all be replaced
        # with new ones by update_parts, below!
    assy.tree = tree
    assy.shelf = shelf
        # below, we'll scan viewdata for Csys records to store into mainpart
    assy.shelf.name = "Clipboard"
    if not assy.shelf.open_specified_by_mmp_file: #bruce 050421 added condition
        assy.shelf.open = False
    assy.root = Group("ROOT", assy, None, [assy.tree, assy.shelf])
    kluge_patch_assy_toplevel_groups(assy)
    assy.update_parts() #bruce 050309 for assy/part split
    # Now the parts exist, so it's safe to store the viewdata into the mainpart;
    # this imitates what the pre-050418 code did when the csys records were parsed;
    # note that not all mmp files have anything at all in viewdata
    # (e.g. some sim-input files don't).
    mainpart = assy.tree.part
    for m in viewdata.members:
        if isinstance(m, Csys):
            if m.name == "HomeView" or m.name == "OldVersion":
                    # "OldVersion" will be changed to "HomeView" later... see comment elsewhere
                mainpart.homeCsys = m
            elif m.name == "LastView":
                mainpart.lastCsys = m
            elif m.name.startswith("HomeView"):
                maybe_set_partview(assy, m, "HomeView", 'homeCsys')
            elif m.name.startswith("LastView"):
                maybe_set_partview(assy, m, "LastView", 'lastCsys')
    return

def maybe_set_partview( assy, csys, nameprefix, csysattr): #bruce 050421
    partnodes = assy.shelf.members
    for i in range(len(partnodes)): #e inefficient if there are a huge number of shelf items...
        if csys.name == nameprefix + "%d" % (i+1):
            part = partnodes[i].part
            setattr(part, csysattr, csys)
            break
    return

def insertmmp(assy, filename): #bruce 050405 revised to fix one or more assembly/part bugs, I hope
    """Read an mmp file and insert its main part into the existing model."""
    grouplist  = _readmmp(assy, filename, isInsert = True)
        # isInsert = True prevents most side effects on assy;
        # a better design would be to let the caller do them (or not)
    if grouplist:
        viewdata, mainpart, shelf = grouplist
        del viewdata
        ## not yet (see below): del shelf
        assy.part.ensure_toplevel_group()
        assy.part.topnode.addchild( mainpart )
        #bruce 050425 to fix bug 563:
        # Inserted mainpart might contain jigs whose atoms were in clipboard of inserted file.
        #   Internally, right now, those atoms exist, in legitimate chunks in assy
        # (with a chain of dads going up to 'shelf' (the localvar above), which has no dad),
        # and have not been killed. Bug 563 concerns these jigs being inserted with no provision
        # for their noninserted atoms. It's not obvious what's best to do in this case, but a safe
        # simple solution seems to be to pretend to insert and then delete the shelf we just read,
        # thus officially killing those atoms, and removing them from those jigs, with whatever
        # effects that might have (e.g. removing those jigs if all their atoms go away).
        #   (When we add history messages for jigs which die from losing all atoms,
        # those should probably differ in this case and in the usual case,
        # but those are NIM for now.)
        #   I presume it's ok to kill these atoms without first inserting them into any Part...
        # at least, it seems unlikely to mess up any specific Part, since they're not now in one.
        #e in future -- set up special history-message behavior for jigs killed by this:
        shelf.kill()
        #e in future -- end of that special history-message behavior
    return

def fix_assy_and_glpane_views_after_readmmp( assy, glpane):
    "#doc; does gl_update but callers should not rely on that"
    #bruce 050418 moved this code (written by Huaicai) out of MWsemantics.fileOpen
    # (my guess is it should mostly be done by readmmp itself);
    # here is Huaicai's comment about it:
    # Huaicai 12/14/04, set the initial orientation to the file's home view orientation 
    # when open a file; set the home view scale = current fit-in-view scale
    #bruce 050418 change this for assembly/part split (per-part Csys attributes)
    mainpart = assy.tree.part
    assert assy.part == mainpart # necessary for glpane view funcs to refer to it (or was at one time)
    if mainpart.homeCsys.name == "OldVersion": ## old version of mmp file
        mainpart.homeCsys.name = "HomeView"
        glpane.set_part(mainpart) # also sets view, but maybe not fully correctly in this case ###k
        glpane.quat = Q( mainpart.homeCsys.quat) # might be redundant with above
        glpane.setViewFitToWindow()
    else:    
        glpane.set_part(mainpart)
        ## done by that: glpane._setInitialViewFromPart( mainpart)
    return

# == writing mmp files

def workaround_for_bug_296(assy, onepart = None):
##    print "not doing workaround_for_bug_296!"
    return #####@@@@@ 050422
##    """If needed, move jigs in assy.tree and each assy.shelf member to later positions
##    (and emit appropriate messages about this),
##    since current mmp file format requires jigs to come after
##    all chunks whose atoms they connect to.
##    If onepart is provided, then do this only for the node (if any)
##    whose part is onepart.
##    """
##    # bruce 050111 temp fix for bug 296 (maybe enough for Alpha)
##    # bruce 050202 adds:
##    # I developed an extension to this fix for jigs in clipboard items,
##    # but decided not to commit it for Alpha. It's in a diff -c, mailed to cad
##    # for inclusion as a bug296 comment, for testing and use after Alpha.
##    # It might as well be put in as soon as anyone has time, after Alpha goes out.
##    # bruce 050325: I finally put that in, and then further modified this code,
##    # e.g. adding onepart option.
##    def errfunc(msg):
##        "local function for error message output"
##        assy.w.history.message( redmsg( msg))
##    try:
##        from node_indices import move_jigs_if_needed
##        count = 0
##        if onepart == assy.tree.part or not onepart:
##            count = move_jigs_if_needed(assy.tree, errfunc) # (this does the work)
##        shelf_extra = ""
##        try:
##            #bruce 050202 extension to fix it in shelf too [not committed until 050325]
##            count2 = 0
##            for m in assy.shelf.members:
##                count1 = 0
##                if onepart == m.part or not onepart:
##                    count1 = move_jigs_if_needed(m, errfunc)
##                count += count1 # important to count these now in case of exception in next loop iteration
##                count2 += count1
##            if count2:
##                shelf_extra = "of which %d were in clipboard, " % count2
##        except:
##            print_compact_traceback("bug in workaround_for_bug_296 for some shelf item: ")
##            shelf_extra = ""
##        if count:
##            from platform import fix_plurals
##            movedwhat = fix_plurals( "%d jig(s)" % count)
##            warning = "Warning: moved %s within model tree, %s" \
##              "to work around limitation in Alpha mmp file format" % (movedwhat, shelf_extra)
##            assy.w.history.message( redmsg( warning))
##    except:
##        print_compact_traceback("bug in bug-296 bugfix in files_mmp.writemmpfile_assy or _part: ")
##    return

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
        self.options = options # as of 050422, one of them is 'leave_out_sim_disabled_nodes'
        self.sim = options.get('sim', False) # simpler file just for the simulator?
        self.min = options.get('min', False) # even more simple, just for minimize?
        if self.min:
            self.sim = True
        self.forwarded_nodes_after_opengroup = {}
        self.forwarded_nodes_after_child = {}
        pass
    def set_fp(self, fp):
        "set file pointer to write to (don't forget to call write_header after this!)"
        self.fp = fp
    def write(self, lines):
        "write one or more \n-terminates lines (passed as a single string) to our file pointer"
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
            self.fp.write("# mmp file written by Minimize; can't be read before Alpha5\n")
        elif self.sim:
            self.fp.write("# mmp file written by Simulate; can't be read before Alpha5\n")
        
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
    # bruce 050422: support for writing forward-refs to nodes, and later writing the nodes at the right time
    # (to be used for jigs which occur before their atoms in the model tree ordering)
    # 1. methods for when the node first wishes it could be written out
    past_sim_part_of_file = False # set to True by external code (kluge?)
    def not_yet_past_where_sim_stops_reading_the_file(self):
        return not self.past_sim_part_of_file
    def node_ref_id(self, node):
        return id(node)
    def write_forwarded_node_after_nodes( self, node, after_these, force_disabled_for_sim = False ):
        """Due to the mmp file format, node says it must come after the given nodes in the file,
        and optionally also after where the sim stops reading the file.
        Write it out in a nice place in the tree (for sake of old code which doesn't know it should
        be moved back into its original place), as soon in the file as is consistent with these conditions.
        In principle this might be "now", but that's an error -- that is, caller is required
        to only call us if it has to. (We might find a way to relax that condition, but that's harder
        than it sounds.)
        """
        # It seems too hard to put it in as nice a place as the old code did,
        # and be sure it's also a safe place... so let's just put it after the last node in after_these,
        # or in some cases right after where the sim stops reading (but in a legal place re shelf group structure).
        from node_indices import node_position, node_at
        root = self.assy.root # one group containing everything in the entire file
            # this should be ok even if "too high" (as when writing a single part),
            # but probably only due to how we're called ... not sure.
        if force_disabled_for_sim:
            if self.options.get('leave_out_sim_disabled_nodes',False):
                return # best to never write it in this case!
            # assume we're writing the whole assy, so in this case, write it no sooner than just inside the shelf group.
            after_these = list(after_these) + [self.assy.shelf] # for a group, being after it means being after its "begin record"
        afterposns = map( lambda node1: node_position(node1, root), after_these)
        after_this_pos = max(afterposns)
        after_this_node = node_at(root, after_this_pos)
        if after_this_node.is_group():
            assert after_this_node == self.assy.shelf, \
                   "forwarding to after end of a group is not yet properly implemented: %r" % after_this_node
                # (not even if we now skipped to end of that group (by pushing to 'child' not 'opengroup'),
                #  since ends aren't ordered like starts, so max was wrong in that case.)
            self.push_node(node, self.forwarded_nodes_after_opengroup, after_this_node)
        else:
            self.push_node(node, self.forwarded_nodes_after_child, after_this_node)
    def push_node(self, node, dict1, key):
        list1 = dict1.setdefault(key, []) #k syntax #k whether pyobjs ok as keys
        list1.append(node)
    # 2. methods for actually writing it out, when it finally can be
    def pop_forwarded_nodes_after_opengroup(self, og):
        return self.pop_nodes( self.forwarded_nodes_after_opengroup, og)
    def pop_forwarded_nodes_after_child(self, ch):
        return self.pop_nodes( self.forwarded_nodes_after_child, ch)
    def pop_nodes( self, dict1, key):
        list1 = dict1.pop(key, [])
        return list1
    def write_forwarded_node_for_real(self, node):
        self.write_node(node)
        #e also write some forward anchor... not sure if before or after... probably "after child" or "after node" (or leaf if is one)
        assert not node.is_group() # for now; true since we're only used on jigs; desirable since "info leaf" only works in this case
        self.write_info_leaf( 'forwarded', self.node_ref_id(node) )
    def write_info_leaf( self, key, val):
        "write an info leaf record for key and val. WARNING: writes str(val) for any python type of val"
        val = str(val)
        assert '\n' not in val
        self.write( "info leaf %s = %s\n" % (key, val) )
    def write_node(self, node):
        node.writemmp(self)
    pass # end of class writemmp_mapping

# bruce 050322 revised to use mapping; 050325 split, removed assy.alist set
def writemmpfile_assy(assy, filename, addshelf = True): #e should merge with writemmpfile_part
    """Write everything in this assy (chunks, jigs, Groups,
    for both tree and shelf unless addshelf = False)
    into a new MMP file of the given filename.
    Should be called via the assy method writemmpfile.
    Should properly save entire file regardless of current part
    and without changing current part.
    """
    #bruce 050325 renamed this from writemmp
    # to avoid confusion with Node.writemmp.
    # Also, there's now an assy method which calls it
    # and a sister function for Parts which has a Part method.
    
    ##Huaicai 1/27/05, save the last view before mmp file saving
    #bruce 050419 revised to save into glpane's current part
    assy.o.saveLastView()

    assy.update_parts() #bruce 050325 precaution
    
    if addshelf:
        workaround_for_bug_296( assy)
    else:
        workaround_for_bug_296( assy, onepart == assy.tree.part)
    
    fp = open(filename, "w")

    mapping = writemmp_mapping(assy) ###e should pass sim or min options when used that way...
    mapping.set_fp(fp)

    try:
        mapping.write_header()
        assy.construct_viewdata().writemmp(mapping)
        assy.tree.writemmp(mapping)
        
        mapping.write("end1\n")
        mapping.past_sim_part_of_file = True
        
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
    part.assy.o.saveLastView() ###e should change to part.glpane? not sure... [bruce 050419 comment]
        # this updates assy.part csys records, but we don't currently write them out below
    node = part.topnode
    assert part == node.part
    part.assy.update_parts() #bruce 050325 precaution
    if part != node.part and platform.atom_debug:
        print "atom_debug: bug?: part changed during writemmpfile_part, using new one"
    part = node.part
    assy = part.assy
    #e assert node is tree or shelf member? is there a method for that already? is_topnode?
    workaround_for_bug_296( assy, onepart = part)
    fp = open(filename, "w")
    mapping = writemmp_mapping(assy, leave_out_sim_disabled_nodes = True)
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

# end of module files_mmp.py


