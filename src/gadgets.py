# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

"""Classes for motors and jigs
$Id$
"""
from VQT import *
from drawer import drawsphere, drawcylinder, drawline, drawaxes
from drawer import segstart, drawsegment, segend, drawwirecube
from shape import *
from chem import *
import OpenGL.GLUT as glut
from Utility import *
from RotaryMotorProp import *
from LinearMotorProp import *
from GroundProp import *
from StatProp import *
from ThermoProp import *
from HistoryWidget import redmsg

Gno = 0
def gensym(string):
    # warning, there is also a function like this in chem.py
    # but with its own global counter!
    """return string appended with a unique number"""
    global Gno
    Gno += 1
    return string + str(Gno)

def povpoint(p):
    # note z reversal -- povray is left-handed
    return "<" + str(p[0]) + "," + str(p[1]) + "," + str(-p[2]) + ">"


class Jig(Node):
    "abstract superclass for all jigs"
    sym = "Jig"
    # each subclass can define sym as a class constant,
    # to customize the name-making code in __init__
    def __init__(self, assy, atomlist):
        "each subclass needs to call this"
        self.init_icons()
        Node.__init__(self, assy, gensym("%s." % self.sym))
        self.atoms = list(atomlist) # this is always [] for some subclasses
            # but is apparently required to be always nonempty for others
            # bruce 050316: copy it (precaution in case caller modifies it later)
        if atomlist:
            #e should we split this jig if attached to more than one mol??
            # not necessarily, tho the code to update its appearance
            # when one of the atoms move is not yet present. [bruce 041202]
            for a in atomlist:
                a.jigs += [self]
        #e it might make sense to init other attrs here too, like color
        return
        
    #bruce 041202 made the icons class constants, so they will be loaded once
    # per Atom run per subclass, rather than every time we create another jig!
    # But they can't be actually loaded when this module is imported
    # (otherwise we get the error message
    #  "QPaintDevice: Must construct a QApplication before a QPaintDevice"),
    # so we defer the load for each subclass until the first time one of its
    # instances is created. I might move this whole thing into class Node.
    def init_icons(self): #e this might make more sense in Node...
        # see also the same-named, related method in class molecule.
        "each subclass must define mticon = [] as a class constant"
        if self.mticon or not self.icon_names:
            # mticon will be set to a subclass-specific class constant;
            # if we've already loaded the icons (or don't need to for this
            # subclass), return now -- we load them once per subclass.
            return
        # the following runs once per Atom session per Jig subclass.
        for name in self.icon_names: #e could use a key/value dict instead...
            self.mticon.append( imagename_to_pixmap( name))
        return

    def node_icon(self, display_prefs): # bruce 050109 revised this [was seticon]
        "a subclass should override this if it uses mticon[] indices differently"
        return self.mticon[self.hidden]
        
    def setAtoms(self, atomlist):
        if self.atoms:
            print "fyi: bug? setAtoms overwrites existing atoms on %r" % self
            #e remove them? would need to prevent recursive kill.
        self.atoms = list(atomlist) # bruce 050316: copy the list
        for a in atomlist:
            a.jigs += [self]
            
    def copy(self, dad):
        self.assy.w.history.message( redmsg("Jigs cannot yet be copied"))
        return None
        
    # josh 10/26 to fix bug 85
    # bruce 050215 added docstring and added removal of self from atm.jigs
    def rematom(self, atm):
        "remove atom atm from this jig, and remove this jig from atom atm [called from atom.kill]"
        self.atoms.remove(atm)
        #bruce 050215: also remove self from atm's list of jigs
        try:
            atm.jigs.remove(self) # assume no need to notify atm of this
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: ignoring exception in rematom: ")
        # should check and delete the jig if no atoms left
        if not self.atoms:
            self.kill()
        return
    
    def kill(self):
        # bruce 050215 modified this to remove self from our atoms' jiglists, via rematom
        for atm in self.atoms[:]: #bruce 050316: copy the list (presumably a bugfix)
            self.rematom(atm) # the last one removed kills the jig recursively!
        Node.kill(self) # might happen twice, that's ok

    # bruce 050125 centralized pick and unpick (they were identical on all Jig
    # subclasses -- with identical bugs!), added comments; didn't yet fix the bugs.
    #bruce 050131 for Alpha: more changes to it (still needs review after Alpha is out)
    
    def pick(self): 
        """select the Jig"""
        self.assy.w.history.message(self.getinfo()) 
        if not self.picked: #bruce 050131 added this condition (maybe good for history.message too?)
            Node.pick(self) #bruce 050131 for Alpha: using Node.pick
            self.normcolor = self.color # bug if this is done twice in a row! [bruce 050131 maybe fixed now due to the 'if']
            self.color = self.pickcolor
        return

    def unpick(self):
        """unselect the Jig"""
        if self.picked:
            Node.unpick(self) # bruce 050126 -- required now
            self.color = self.normcolor

    def move(self, offset):
        #bruce 050208 made this default method. Is it ever called, in any subclasses??
        pass

    def break_interpart_bonds(self): #bruce 050316 fix the jig analog of bug 371
        "[overrides Node method]"
        #e this should be a "last resort", i.e. it's often better if interpart bonds
        # could split the jig in two, or pull it into a new Part.
        # But that's NIM (as of 050316) so this is needed to prevent some old bugs.
        for atm in self.atoms[:]:
            if self.part != atm.molecule.part:
                self.rematom(atm) # this might kill self, if we remove them all
        return

    def fixes_atom(self, atm): #bruce 050321
        "does this jig hold this atom fixed in space? [should be overridden by subclasses as needed]"
        return False # for most jigs

    def writemmp(self, atnums, alist, f):
        "[overrides Node.writemmp; could be overridden by Jig subclasses, but isn't (as of 050322)]"
         #bruce 050322 made this from old Node.writemmp, but replaced nonstandard use of __repr__
        line = self.mmp_record(atnums) # includes '\n' at end
        if line:
            f.write(line)
        else:
            Node.writemmp(self, atnums, alist, f)

    def mmp_record(self, atnums):
        """[subclasses must override this to return their mmp record,
        which must consist of 1 or more lines each ending in '\n',
        including the last line]
        """
        pass

    def __repr__(self): #bruce 050322 compatibility method, probably not needed, but affects debugging
        return self.mmp_record()

    #e there might be other common methods to pull into here

    pass # end of class Jig


class RotaryMotor(Jig):
    '''A Rotary Motor has an axis, represented as a point and
       a direction vector, a stall torque, a no-load speed, and
       a set of atoms connected to it
       To Be Done -- selecting & manipulation'''
    
    sym = "Rotary Motor"
    mticon = []
    icon_names = ["rmotor.png", "rmotor-hide.png"]

    # create a blank Rotary Motor not connected to anything    
    def __init__(self, assy):
        Jig.__init__(self, assy, [])
        self.torque = 0.0 # in nN * nm
        self.speed = 0.0 # in gHz
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        self.color = self.normcolor = (0.5, 0.5, 0.5) # default color = gray
        self.pickcolor = (1.0, 0.0, 0.0) # red
        self.length = 10.0 # default length of Rotary Motor cylinder
        self.radius = 2.0 # default cylinder radius
        self.sradius = 0.5 #default spoke radius
        # Should self.cancelled be in RotaryMotorProp.setup? - Mark 050109
        self.cancelled = True # We will assume the user will cancel
        self.cntl = RotaryMotorProp(self, assy.o)

    # set the properties for a Rotary Motor read from a (MMP) file
    def setProps(self, name, color, torque, speed, center, axis, length, radius, sradius):
        self.name = name
        self.color = color
        self.torque = torque
        self.speed = speed
        self.center = center
        self.axis = norm(axis)
        self.length = length
        self.radius = radius
        self.sradius = sradius

    # for a motor read from a file, the "shaft" record
    def setShaft(self, shft):
        self.setAtoms(shft) #bruce 041105 code cleanup

    # for a motor created by the UI, center is average point and
    # axis (kludge) is the average of the cross products of
    # vectors from the center to successive points
    # los is line of sight into the screen
    def findCenter(self, shft, los):
        self.setAtoms(shft) #bruce 041105 code cleanup
        # array of absolute atom positions
        # can't use xyz, might be from different molecules
        pos=A(map((lambda a: a.posn()), shft))
        self.center=sum(pos)/len(pos)
        relpos=pos-self.center
        if len(shft) == 1:
            self.axis = norm(los)
        elif len(shft) == 2:
            self.axis = norm(cross(relpos[0],cross(relpos[1],los)))
        else:
            guess = map(cross, relpos[:-1], relpos[1:])
            guess = map(lambda x: sign(dot(los,x))*x, guess)
            self.axis=norm(sum(guess))
        self.edit()

    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()

    def move(self, offset):
        self.center += offset

    def posn(self):
        return self.center

    def axen(self):
        return self.axis
   
    def getinfo(self):
        return "[Object: Rotary Motor] [Name: " + str(self.name) + "] [Torque = " + str(self.torque) + "] [Speed = " +str(self.speed) + "]"
        
    def getstatistics(self, stats):
        stats.nrmotors += 1
               
    # Rotary Motor is drawn as a cylinder along the axis,
    #  with a spoke to each atom
    def draw(self, win, dispdef):
        if self.hidden: return
        bCenter = self.center - (self.length / 2.0) * self.axis
        tCenter = self.center + (self.length / 2.0) * self.axis
        drawcylinder(self.color, bCenter, tCenter, self.radius, 1 )
        ### Draw the rotation sign #####
        drawRotateSign((0,0,0), bCenter, tCenter, self.radius)            
        for a in self.atoms:
            drawcylinder(self.color, self.center, a.posn(), self.sradius)
            
    # Write "rmotor" and "spoke" records to POV-Ray file in the format:
    # rmotor(<cap-point>, <base-point>, cylinder-radius, <r, g, b>)
    # spoke(<cap-point>, <base-point>, scylinder-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        c = self.posn()
        a = self.axen()
        file.write("rmotor(" + povpoint(c+(self.length / 2.0)*a) + "," + povpoint(c-(self.length / 2.0)*a)  + "," + str (self.radius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn()) + "," + str (self.sradius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")

    # Returns the MMP record for the current Rotary Motor as:
    # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)
    def mmp_record(self, ndix = None):
        #bruce 050322 renamed this from __repr__, which was nonstandardly used; see comments in Jig
        cxyz=self.posn() * 1000
        axyz=self.axen() * 1000
        if self.picked: c = self.normcolor
        else: c = self.color
        color=map(int,A(c)*255)
        s="rmotor (%s) (%d, %d, %d) %.2f %.2f (%d, %d, %d) (%d, %d, %d) %.2f %.2f %.2f\n" %\
           (self.name, color[0], color[1], color[2], self.torque, self.speed,
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]),
            self.length, self.radius, self.sradius)
        if ndix:
            nums = map((lambda a: ndix[a.key]), self.atoms)
        else:
            nums = map((lambda a: a.key), self.atoms)
        return s + "shaft " + " ".join(map(str,nums)) + "\n"

    pass # end of class RotaryMotor


class LinearMotor(Jig):
    '''A Linear Motor has an axis, represented as a point and
       a direction vector, a force, a stiffness, and
       a set of atoms connected to it
       To Be Done -- selecting & manipulation'''

    sym = "Linear Motor"
    mticon = []
    icon_names = ["lmotor.png", "lmotor-hide.png"]

    # create a blank Linear Motor not connected to anything
    def __init__(self, assy):
        Jig.__init__(self, assy, [])
        
        self.force = 0.0
        self.stiffness = 0.0
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        self.color = self.normcolor = (0.5, 0.5, 0.5) # default color = gray
        self.pickcolor = (1.0, 0.0, 0.0)
        self.length = 10.0 # default length of Linear Motor box
        self.width = 2.0 # default box width
        self.sradius = 0.5 #default spoke radius
        self.cancelled = True # We will assume the user will cancel
        self.cntl = LinearMotorProp(self, assy.o)

    # set the properties for a Linear Motor read from a (MMP) file
    def setProps(self, name, color, force, stiffness, center, axis, length, width, sradius):
        self.name = name
        self.color = color
        self.force = force
        self.stiffness = stiffness
        self.center = center
        self.axis = norm(axis)
        self.length = length
        self.width = width
        self.sradius = sradius

    # for a linear motor read from a file, the "shaft" record
    def setShaft(self, shaft):
        self.setAtoms(shaft) #bruce 041105 code cleanup
 
    # for a motor created by the UI, center is average point and
    # axis (kludge) is the average of the cross products of
    # vectors from the center to successive points
    # los is line of sight into the screen
    def findCenter(self, shft, los):
        self.setAtoms(shft) #bruce 041105 code cleanup
        # array of absolute atom positions
        # can't use xyz, might be from different molecules
        pos=A(map((lambda a: a.posn()), shft))
        self.center=sum(pos)/len(pos)
        relpos=pos-self.center
        if len(shft) == 1:
            self.axis = norm(los)
        elif len(shft) == 2:
            self.axis = norm(cross(relpos[0],cross(relpos[1],los)))
        else:
            guess = map(cross, relpos[:-1], relpos[1:])
            guess = map(lambda x: sign(dot(los,x))*x, guess)
            self.axis=norm(sum(guess))
        self.edit()

    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()
        
    def move(self, offset):
        self.center += offset

    def posn(self):
        return self.center

    def axen(self):
        return self.axis
   
    def getinfo(self):
        return "[Object: Linear Motor] [Name: " + str(self.name) + \
                    "] [Force = " + str(self.force) + \
                    "] [Stiffness = " +str(self.stiffness) + "]"

    def getstatistics(self, stats):
        stats.nlmotors += 1
   
    # drawn as a gray box along the axis,
    # with a thin cylinder to each atom 
    def draw(self, win, dispdef):
        if self.hidden: return
        drawbrick(self.color, self.center, self.axis, self.length, self.width, self.width)
        drawLinearSign((0,0,0), self.center, self.axis, self.length, self.width, self.width)
        for a in self.atoms:
            drawcylinder(self.color, self.center, a.posn(), self.sradius)

            
    # Write "lmotor" and "spoke" records to POV-Ray file in the format:
    # lmotor(<cap-point>, <base-point>, box-width, <r, g, b>)
    # spoke(<cap-point>, <base-point>, sbox-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        c = self.posn()
        a = self.axen()
        file.write("lmotor(" + povpoint(c+(self.length / 2.0)*a) + "," + 
                    povpoint(c-(self.length / 2.0)*a)  + "," + str (self.width / 2.0) + 
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn())  + "," + str (self.sradius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")

    # Returns the MMP record for the current Linear Motor as:
    # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
    def mmp_record(self, ndix = None):
        cxyz = self.posn() * 1000
        axyz = self.axen() * 1000
        if self.picked: c = self.normcolor
        else: c = self.color
        color=map(int,A(c)*255)
        s = "lmotor (%s) (%d, %d, %d) %.2f %.2f (%d, %d, %d) (%d, %d, %d) %.2f %.2f %.2f\n" %\
           (self.name, color[0], color[1], color[2], self.stiffness, self.force, 
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]),
            self.length, self.width, self.sradius)
        if ndix:
            nums = map((lambda a: ndix[a.key]), self.atoms)
        else:
            nums = map((lambda a: a.key), self.atoms)
        return s + "shaft " + " ".join(map(str, nums)) + "\n"

    pass # end of class LinearMotor


class Ground(Jig):
    '''a Ground just has a list of atoms that are anchored in space'''

    sym = "Ground"
    mticon = []
    icon_names = ["ground.png", "ground-hide.png"]

    # create a blank Ground with the given list of atoms
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list)
        self.color = (0.0, 0.0, 0.0)
        self.normcolor = (0.0, 0.0, 0.0) # set default color of ground to black
        self.pickcolor = (1.0, 0.0, 0.0) # ground is red when picked
        self.cntl = GroundProp(self, assy.o)

    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()

    # it's drawn as a wire cube around each atom (default color = black)
    def draw(self, win, dispdef):
        if self.hidden: return
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "ground" record to POV-Ray file in the format:
    # ground(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            grec = "ground(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(grec)

    def getinfo(self):
        return "[Object: Ground] [Name: " + str(self.name) + "] [Total Grounds: " + str(len(self.atoms)) + "]"

    def getstatistics(self, stats):
        stats.ngrounds += len(self.atoms)
        
    # Returns the MMP record for the current Ground as:
    # ground (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}    
    def mmp_record(self, ndix = None):
        
        if self.picked: c = self.normcolor
        else: c = self.color
        color=map(int,A(c)*255)
        s = "ground (%s) (%d, %d, %d) " %\
           (self.name, color[0], color[1], color[2])
        if ndix:
            nums = map((lambda a: ndix[a.key]), self.atoms)
        else:
            nums = map((lambda a: a.key), self.atoms)

        return s + " ".join(map(str,nums)) + "\n"

    def fixes_atom(self, atm): #bruce 050321
        "does this jig hold this atom fixed in space? [overrides Jig method]"
        return atm in self.atoms
    
    pass # end of class Ground


class Stat(Jig):
    '''A Stat is a Langevin thermostat, which sets a chunk to a specific
    temperature during a simulation. A Stat is defined and drawn on a single
    atom, but its record in an mmp file includes 3 atoms:
    - first_atom: the first atom of the chunk to which it is attached.
    - last_atom: the last atom of the chunk to which it is attached.
    - boxed_atom: the atom in the chunk the user selected. A box is drawn
    around this atom.
       Note that the simulator applies the Stat to all atoms in the entire chunk
    to which it's attached, but in case of merging or joining chunks, the atoms
    in this chunk might be different each time the mmp file is written; even
    the atom order in one chunk might vary, so the first and last atoms can be
    different even when the set of atoms in the chunk has not changed.
    Only the boxed_atom is constant (and only it is saved, as self.atoms[0]).
    '''
    #bruce 050210 for Alpha-2: fix bug in Stat record reported by Josh to ne1-users    
    sym = "Stat"
    mticon = []
    icon_names = ["stat.png", "stat-hide.png"]

    # create a blank Stat with the given list of atoms, set to 300K
    def __init__(self, assy, list):
        # ideally len(list) should be 1, but in case code in fileIO uses more
        # when supporting old Stat records, all I assert here is that it's at
        # least 1, but I only store the first atom [bruce 050210]
        assert len(list) >= 1
        list = list[0:1]
        Jig.__init__(self, assy, list)
        # set default color of new stat to blue
        self.color = self.normcolor = (0.0, 0.0, 1.0) 
        # stat is red when picked
        self.pickcolor = (1.0, 0.0, 0.0) 
        self.temp = 300
        self.cntl = StatProp(self, assy.o)
    
    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()

    # it's drawn as a wire cube around each atom (default color = blue)
    def draw(self, win, dispdef):
        if self.hidden: return
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "stat" record to POV-Ray file in the format:
    # stat(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            srec = "stat(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(srec)

    def getinfo(self):
        return  "[Object: Thermostat] "\
                    "[Name: " + str(self.name) + "] "\
                    "[Temp = " + str(self.temp) + "K]" + "] "\
                    "[Attached to: " + str(self.atoms[0].molecule.name) + "] "

    def getstatistics(self, stats):
        stats.nstats += len(self.atoms)

    # Returns the MMP record for the current Stat as:
    # stat (name) (r, g, b) (temp) first_atom last_atom box_atom
    def mmp_record(self, ndix = None):
        if self.picked: c = self.normcolor
        else: c = self.color
        color=map(int,A(c)*255)
        s = "stat (%s) (%d, %d, %d) (%d) " %\
           (self.name, color[0], color[1], color[2], int(self.temp) )
        if ndix:
            atomkeys = [self.atoms[0].key] + self.atoms[0].molecule.atoms.keys()
                # first key occurs twice, that's ok (but that it's first matters)
            nums = map((lambda ak: ndix[ak]), atomkeys)
            nums = [min(nums), max(nums), nums[0]]
        else:
            nums = map((lambda a: a.key), self.atoms)
        return s + " ".join(map(str,nums)) + "\n"

    pass # end of class Stat


class Thermo(Jig):
    '''A Thermo is a thermometer which measures the temperature of a chunk
    during a simulation. A Thermo is defined and drawn on a single
    atom, but its record in an mmp file includes 3 atoms and applies to all
    atoms in the same chunk; for details see Stat docstring.
    '''
    #bruce 050210 for Alpha-2: fixed same bug as in Stat.
    sym = "Thermo"
    mticon = []
    icon_names = ["thermo.png", "thermo-hide.png"]

    # creates a thermometer for a specific atom. "list" contains only one atom.
    def __init__(self, assy, list):
        # ideally len(list) should be 1, but in case code in fileIO uses more
        # when supporting old Thermo records, all I assert here is that it's at
        # least 1, but I only store the first atom [bruce 050210]
        assert len(list) >= 1
        list = list[0:1]
        Jig.__init__(self, assy, list)
        # set default color of new thermo to dark red
        self.color = self.normcolor = (0.6, 0.0, 0.2) 
        # thermo is red when picked
        self.pickcolor = (1.0, 0.0, 0.0)
        self.cntl = ThermoProp(self, assy.o)
    
    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()

    # it's drawn as a wire cube around each atom (default color = purple)
    def draw(self, win, dispdef):
        if self.hidden: return
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "thermo" record to POV-Ray file in the format:
    # thermo(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            srec = "thermo(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(srec)

    def getinfo(self):
        return  "[Object: Thermometer] "\
                    "[Name: " + str(self.name) + "] "\
                    "[Attached to: " + str(self.atoms[0].molecule.name) + "] "

    def getstatistics(self, stats):
        #bruce 050210 fixed this as requested by Mark
        stats.nthermos += len(self.atoms)

    # Returns the MMP record for the current Thermo as:
    # thermo (name) (r, g, b) first_atom last_atom box_atom
    def mmp_record(self, ndix = None):
        if self.picked: c = self.normcolor
        else: c = self.color
        color=map(int,A(c)*255)
        s = "thermo (%s) (%d, %d, %d) " %\
           (self.name, color[0], color[1], color[2] )
        if ndix:
            atomkeys = [self.atoms[0].key] + self.atoms[0].molecule.atoms.keys()
                # first key occurs twice, that's ok (but that it's first matters)
            nums = map((lambda ak: ndix[ak]), atomkeys)
            nums = [min(nums), max(nums), nums[0]]
        else:
            nums = map((lambda a: a.key), self.atoms)
        return s + " ".join(map(str,nums)) + "\n"

    pass # end of class Thermo

# end
