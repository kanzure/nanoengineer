from VQT import *
from drawer import drawsphere, drawcylinder, drawline, drawaxes
from drawer import segstart, drawsegment, segend, drawwirecube
from shape import *
from chem import *


def povpoint(p):
    # note z reversal -- povray is left-handed
    return "<" + str(p[0]) + "," + str(p[1]) + "," + str(-p[2]) + ">"


# A motor has an axis of rotation, represented as a point and
# a direction vector, a stall torque, a no-load speed, and
# a set of atoms connected to it
# 2BDone -- selecting & manipulation
class motor:
    # create a blank motor connected to anything
    def __init__(self, assy):
        self.torque=0.0
        self.speed=0.0
        self.center=V(0,0,0)
        self.axis=V(0,0,0)
        self.atoms=[]
        self.picked=0
        self.molecule = None

    # for a motor read from a file, the "motor" record
    def setcenter(self, torq, spd, cntr, xs):
        self.torque=torq
        self.speed=spd
        self.center=cntr
        self.axis=norm(xs)

    # for a motor read from a file, the "shaft" record
    def setshaft(self, shft):
        self.atoms=shft
        # this is a hack, but a motor shouldn't be
        # attached to more than one molecule anyway
        self.molecule = shft[0].molecule
        self.center -= self.molecule.center
        self.molecule.gadgets += [self]

    # for a motor created by the UI, center is average point and
    # axis (kludge) is the average of the cross products of
    # vectors from the center to successive points
    # los is line of sight into the screen
    def findcenter(self, shft, los):
        self.atoms=shft
        # array of absolute atom positions
        # can't use xyz, might be from different molecules
        pos=A(map((lambda a: a.posn()), shft))
        self.center=sum(pos)/len(pos)
        relpos=pos-self.center
        if len(shft) == 1:
            axis = norm(los)
        elif len(shft) == 2:
            axis = norm(cross(relpos[0],cross(relpos[1],los)))
        else:
            guess = map(cross, relpos[:-1], relpos[1:])
            guess = map(lambda x: sign(dot(los,x))*x, guess)
            self.axis=norm(sum(guess))

        self.molecule = shft[0].molecule
        self.center -= self.molecule.center
        self.molecule.gadgets += [self]
        

    def move(self, offset):
        self.center += offset

    def posn(self):
        return self.molecule.quat.rot(self.center) + self.molecule.center

    def axen(self):
        return self.molecule.quat.rot(self.axis)

    # drawn as a gray cylinder along the axis,
    # with a spoke to each atom    
    def draw(self, win, dispdef):
        col=(0.5, 0.5, 0.5)
        drawcylinder(col,self.center+5*self.axis,self.center-5*self.axis,
                     2.0, self.picked, 1)
        for a in self.atoms:
            drawcylinder(col, self.center, a.xyz ,0.5, self.picked)
            
    # write on a povray file
    def povwrite(self, file, dispdef):
        c = self.posn()
        a = self.axen()
        file.write("motor(" + povpoint(c+5*a) +
                    "," + povpoint(c-5*a) + ")\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) +
                       "," + povpoint(a.posn()) + ")\n")

    # the representation is also the mmp-file record
    def __repr__(self, ndix=None):
        cxyz=self.posn() * 1000
        axyz=self.axen() * 1000
        s="motor %.2f, %.2f, (%d, %d, %d) (%d, %d, %d)\n" %\
           (self.torque, self.speed,
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]))
        if ndix:
            nums = map((lambda a: ndix[a.key]), self.atoms)
        else:
            nums = map((lambda a: a.key), self.atoms)
        return s + "shaft " + " ".join(map(str,nums))

# a ground just has a list of atoms
class ground:
    def __init__(self, assy, list):
        self.atoms =list
        # should really split ground if attached to more than one mol
        self.molecule = list[0].molecule
        self.molecule.gadgets += [self]
        

    # it's drawn as a black wire cube around each atom
    def draw(self, win, dispdef):
        col=(0, 0, 0)
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(col, a.xyz, rad)
            
    # write on a povray file
    def povwrite(self, file, dispdef):
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            file.write("ground(" + povpoint(a.posn()) + "," +
                       str(rad) + ")\n")

    def move(self, offset):
        pass
    
    # the representation is also the mmp-file record
    def __repr__(self, ndix=None):
        if ndix:
            nums = map((lambda a: ndix[a.key]), self.atoms)
        else:
            nums = map((lambda a: a.key), self.atoms)
        return "ground " + " ".join(map(str,nums))
