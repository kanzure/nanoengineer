# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

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


class Jig(Node): #bruce 041105 encapsulate common code so I can extend it
    "abstract superclass for all jigs"
    # each subclass needs to define sym as a class constant
    def __init__(self, assy, atomlist):
        "each subclass needs to call this"
        Node.__init__(self, assy, None, gensym("%s." % self.sym))
        ## self.picked = 0 # redundant with Node.__init__
        self.atoms = atomlist # this is always [] for some subclasses
            # but is apparently required to be always nonempty for others
        if atomlist:
            #e should really split this jig if attached to more than one mol
            ## self.molecule = atomlist[0].molecule
            ## self.molecule.gadgets += [self]
              # note: mol.gadgets is never used, as of sometime before 041105,
              # probably as of josh's fix to bug 85 on 041026 [bruce 041105]
            for a in atomlist:
                # bruce 041105: I don't think multiple mols causes bugs anymore:
                ## if a.molecule is not self.molecule:
                ##    print "fyi: bug? %r has atoms from different chunks" % self
                a.jigs += [self]
        else:
            pass ## self.molecule = None
        #e it might make sense to init other attrs here too, like color
        return
    def setAtoms(self, atomlist):
        # the subclass code I made this from did nothing to set
        # self.molecule or its .gadgets member; presumably neither
        # is needed (at least for the calling subclasses) [bruce 041105]
        ## assert not self.atoms # otherwise we'd have to delete them properly
        if self.atoms:
            print "fyi: bug? setAtoms overwrites existing atoms on %r" % self
        self.atoms = atomlist
        for a in atomlist:
            a.jigs += [self]
    # josh 10/26 to fix bug 85
    def rematom(self, a):
        self.atoms.remove(a)
        # should check and delete the jig if no atoms left
        if not self.atoms:
            self.kill()
    def kill(self):
        #e don't we need to remove self from self.molecule.gadgets?? [guess: no]
        # and also remove self from all our atoms' a.jigs? [guess: yes]
        # [bruce question 041105; looks like a bug but i will ask josh]
        Node.kill(self)
    #e there might be other common methods to pull into here
    pass # class Jig


class RotaryMotor(Jig):
    '''A Rotary Motor has an axis, represented as a point and
       a direction vector, a stall torque, a no-load speed, and
       a set of atoms connected to it
       To Be Done -- selecting & manipulation'''
    
    sym = "Rotary Motor"
    
# create a blank Rotary Motor not connected to anything    
    def __init__(self, assy):
##        Node.__init__(self, assy, None, gensym("Rotary Motor."))
        Jig.__init__(self, assy, [])
        self.torque = 0.0
        self.speed = 0.0
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
##        self.atoms = []
##        self.molecule = None
        self.color = self.normcolor = (0.5, 0.5, 0.5) # default color = gray
        self.pickcolor = (1.0, 0.0, 0.0)
        self.length = 10.0 # default length of Rotary Motor cylinder
        self.radius = 2.0 # default cylinder radius
        self.sradius = 0.5 #default spoke radius
        
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.rmotorIcon = QPixmap(filePath + "/../images/rmotor.png")
        
        self.cntl = RotaryMotorProp(self, assy.o)

    # set the properties for a Rotary Motor read from a (MMP) file
    def setProps(self, name, color, torque, speed, center, axis):
        self.name = name
        self.color = color
        self.torque = torque
        self.speed = speed
        self.center = center
        self.axis = norm(axis)

    # for a motor read from a file, the "shaft" record
    def setShaft(self, shft):
        self.setAtoms(shft) #bruce 041105 code cleanup
##        self.atoms = shft
##        # josh 10/26 to fix bug 85
##        for a in shft: a.jigs += [self]

    # for a motor created by the UI, center is average point and
    # axis (kludge) is the average of the cross products of
    # vectors from the center to successive points
    # los is line of sight into the screen
    def findCenter(self, shft, los):
        self.setAtoms(shft) #bruce 041105 code cleanup
##        self.atoms=shft
##        # josh 10/26 to fix bug 85
##        for a in shft: a.jigs += [self]
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
   
    def seticon(self):
        self.icon = self.rmotorIcon

    def getinfo(self):
        return "[Object: Rotary Motor] [Name: " + str(self.name) + "] [Torque = " + str(self.torque) + "] [Speed = " +str(self.speed) + "]"

    def pick(self):
        """select the rotary motor
        """
        self.picked = True
        self.assy.w.msgbarLabel.setText(self.getinfo())
        self.normcolor = self.color
        self.color = self.pickcolor

    def unpick(self):
        """unselect the rotary motor
        """
        if self.picked:
            self.picked = False
            self.assy.w.msgbarLabel.setText(" ")
            self.color = self.normcolor
               
    # Rotary Motor is drawn as a cylinder along the axis,
    #  with a spoke to each atom
    def draw(self, win, dispdef):
        if self.hidden: return
        drawcylinder(self.color,
                    self.center + (self.length / 2.0) * self.axis,
                    self.center - (self.length / 2.0) * self.axis,
                    self.radius, 1)
        for a in self.atoms:
            drawcylinder(self.color, self.center, a.posn(), self.sradius)
            
    # Write "rmotor" and "spoke" records to POV-Ray file in the format:
    # rmotor(<cap-point>, <base-point>, cylinder-radius, <r, g, b>)
    # spoke(<cap-point>, <base-point>, scylinder-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        c = self.posn()
        a = self.axen()
        print "gadgets.py: writepov(): writing rotar motor record"
        file.write("rmotor(" + povpoint(c+(self.length / 2.0)*a) + "," + povpoint(c-(self.length / 2.0)*a)  + "," + str (self.radius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn()) + "," + str (self.sradius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")

    # Returns the MMP record for the current Rotary Motor as:
    # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)
    def __repr__(self, ndix=None):
        cxyz=self.posn() * 1000
        axyz=self.axen() * 1000
        if self.picked: c = self.normcolor
        else: c = self.color
        color=map(int,A(c)*255)
        s="rmotor (%s) (%d, %d, %d) %.2f %.2f (%d, %d, %d) (%d, %d, %d)\n" %\
           (self.name, color[0], color[1], color[2], self.torque, self.speed,
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]))
        if ndix:
            nums = map((lambda a: ndix[a.key]), self.atoms)
        else:
            nums = map((lambda a: a.key), self.atoms)
        return s + "shaft " + " ".join(map(str,nums)) + "\n"


class LinearMotor(Jig):
    '''A Linear Motor has an axis, represented as a point and
       a direction vector, a force, a stiffness, and
       a set of atoms connected to it
       To Be Done -- selecting & manipulation'''

    sym = "Linear Motor"

# create a blank Linear Motor not connected to anything
    def __init__(self, assy):
##        Node.__init__(self, assy, None, gensym("Linear Motor."))
        Jig.__init__(self, assy, [])
        
        self.force = 0.0
        self.stiffness = 0.0
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
##        self.atoms = []
##        self.picked = 0
##        self.molecule = None
        self.color = self.normcolor = (0.5, 0.5, 0.5) # default color = gray
        self.pickcolor = (1.0, 0.0, 0.0)
        self.length = 10.0 # default length of Linear Motor box
        self.width = 2.0 # default box width
        self.sradius = 0.5 #default spoke radius
        self.cntl = LinearMotorProp(self, assy.o)
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.lmotorIcon = QPixmap(filePath + "/../images/lmotor.png")

    # set the properties for a Linear Motor read from a (MMP) file
    def setProps(self, name, color, force, stiffness, center, axis):
        self.name = name
        self.color = color
        self.force = force
        self.stiffness = stiffness
        self.center = center
        self.axis = norm(axis)

    # for a linear motor read from a file, the "shaft" record
    def setShaft(self, shaft):
        self.setAtoms(shaft) #bruce 041105 code cleanup
##        self.atoms = shaft
##        for a in shaft: a.jigs += [self]
 
    # for a motor created by the UI, center is average point and
    # axis (kludge) is the average of the cross products of
    # vectors from the center to successive points
    # los is line of sight into the screen
    def findCenter(self, shft, los):
        self.setAtoms(shft) #bruce 041105 code cleanup
##        self.atoms=shft
##        for a in shft: a.jigs += [self]
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
   
    def seticon(self):
        self.icon = self.lmotorIcon
        
    def getinfo(self):
        return "[Object: Linear Motor] [Name: " + str(self.name) + \
                    "] [Force = " + str(self.force) + \
                    "] [Stiffness = " +str(self.stiffness) + "]"
   
    def pick(self):
        """select the linear motor
        """
        self.picked = True
        self.assy.w.msgbarLabel.setText(self.getinfo())
        self.normcolor = self.color
        self.color = self.pickcolor

    def unpick(self):
        """unselect the rotary motor
        """
        if self.picked:
            self.picked = False
            self.assy.w.msgbarLabel.setText(" ")
            self.color = self.normcolor
                    
    # drawn as a gray box along the axis,
    # with a thin cylinder to each atom 
    def draw(self, win, dispdef):
        if self.hidden: return
        drawbrick(self.color, self.center, self.axis, self.length, self.width, self.width)
        for a in self.atoms:
            drawcylinder(self.color, self.center, a.posn(), self.sradius)

#    def draw(self, win, dispdef):
#        glPushMatrix()
#        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color)
#        glTranslatef(self.center[0], self.center[1], self.center[2])
#        glRotate(-acos(self.axis[2])*180.0/pi, self.axis[1], -self.axis[0], 0.0)
#        glScale(2.0, 2.0, 10.0) # width1, width2, length of lmotor box
#        glScale(self.width / 2.0, self.width / 2.0, self.length) # width1, width2, length of lmotor box
#        glut.glutSolidCube(1.0)
#        glPopMatrix()
            
    # Write "lmotor" and "spoke" records to POV-Ray file in the format:
    # lmotor(<cap-point>, <base-point>, box-width, <r, g, b>)
    # spoke(<cap-point>, <base-point>, sbox-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        c = self.posn()
        a = self.axen()
        print "gadgets.py: writepov(): writing lmotor record"
        file.write("lmotor(" + povpoint(c+(self.length / 2.0)*a) + "," + 
                    povpoint(c-(self.length / 2.0)*a)  + "," + str (self.width / 2.0) + 
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn())  + "," + str (self.sradius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")

    # Returns the MMP record for the current Linear Motor as:
    # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
    def __repr__(self, ndix = None):
        cxyz = self.posn() * 1000
        axyz = self.axen() * 1000
        if self.picked: c = self.normcolor
        else: c = self.color
        color=map(int,A(c)*255)
        s = "lmotor (%s) (%d, %d, %d) %.2f %.2f (%d, %d, %d) (%d, %d, %d)\n" %\
           (self.name, color[0], color[1], color[2], self.stiffness, self.force, 
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]))
        if ndix:
            nums = map((lambda a: ndix[a.key]), self.atoms)
        else:
            nums = map((lambda a: a.key), self.atoms)
        return s + "shaft " + " ".join(map(str, nums)) + "\n"

# a Ground is just has a list of atoms anchored in space
class Ground(Jig):
    '''a Ground just has a list of atoms that are anchored in space'''

    sym = "Ground"

# create a blank Ground with the given list of atoms
    def __init__(self, assy, list):
##        Node.__init__(self, assy, None, gensym("Ground."))
##        self.atoms =list
##        # should really split ground if attached to more than one mol
##        self.molecule = list[0].molecule
##        self.molecule.gadgets += [self]
##        self.picked = 0
        Jig.__init__(self, assy, list)
        self.color = (0.0, 0.0, 0.0)
        self.normcolor = (0.0, 0.0, 0.0) # set default color of ground to black
        self.pickcolor = (1.0, 0.0, 0.0) # ground is red when picked
        self.cntl = GroundProp(self, assy.o)
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.groundIcon = QPixmap(filePath + "/../images/ground.png")
        
##        for a in list: a.jigs += [self]

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

    def move(self, offset):
        pass

    def seticon(self):
        self.icon = self.groundIcon
        
    def getinfo(self):
        return "[Object: Ground] [Name: " + str(self.name) + "] [Total Grounds: " + str(len(self.atoms)) + "]"

    def pick(self):
        """select the ground
        """
        self.picked = True
        self.assy.w.msgbarLabel.setText(self.getinfo())
        self.normcolor = self.color
        self.color = self.pickcolor
        
    def unpick(self):
        """unselect the ground
        """
        if self.picked:
            self.picked = False
            self.assy.w.msgbarLabel.setText(" ")
            self.color = self.normcolor
                                   
    # Returns the MMP record for the current Ground as:
    # ground (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}    
    def __repr__(self, ndix=None):
        
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
        
class Stat(Jig):
    '''a Stat just has a list of atoms that are set to a specific temperature'''
    
    sym = "Stat"
    
# create a blank Stat with the given list of atoms, set to 300K
    def __init__(self, assy, list):
##        Node.__init__(self, assy, None, gensym("Stat."))
##        self.atoms =list
##        # should really split stat if attached to more than one mol
##        self.molecule = list[0].molecule
##        self.molecule.gadgets += [self]
##        self.picked = 0
        Jig.__init__(self, assy, list)
        self.color = self.normcolor = (0.0, 0.0, 1.0) # set default color of new stat to blue
        self.pickcolor = (1.0, 0.0, 0.0) # stat is red when picked
        self.temp = 300
        
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.statIcon = QPixmap(filePath + "/../images/stat.png")
        
        self.cntl = StatProp(self, assy.o)
        
##        for a in list: a.jigs += [self]   
    
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

    def move(self, offset):
        pass

    def seticon(self):
        self.icon = self.statIcon

    def getinfo(self):
        return "[Object: Thermostat] [Name: " + str(self.name) + "] [Temp = " + str(self.temp) + "K]" + "] [Total Stats: " + str(len(self.atoms)) + "]"
        
    def pick(self):
        """select the thermostat
        """
        self.picked = True
        self.assy.w.msgbarLabel.setText(self.getinfo())
        self.normcolor = self.color
        self.color = self.pickcolor
        
    def unpick(self):
        """unselect the thermostat
        """
        if self.picked:
            self.picked = False
            self.assy.w.msgbarLabel.setText(" ")
            self.color = self.normcolor
               
    # Returns the MMP record for the current Stat as:
    # stat (name) (r, g, b) (temp) atom1 atom2 ... atom25 {up to 25}
    def __repr__(self, ndix=None):
        if self.picked: c = self.normcolor
        else: c = self.color
        color=map(int,A(c)*255)
        s = "stat (%s) (%d, %d, %d) (%d) " %\
           (self.name, color[0], color[1], color[2], int(self.temp))
        if ndix:
            nums = map((lambda a: ndix[a.key]), self.atoms)
        else:
            nums = map((lambda a: a.key), self.atoms)
        return s + " ".join(map(str,nums)) + "\n"
