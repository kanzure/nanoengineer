# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

'''
chunk.py -- provides class molecule, for a chunk of atoms
which are moved and selected as a unit.

Temporarily owned by bruce 041104 for shakedown inval/update code.

[split out of chem.py by bruce circa 041118]

$Id$
'''
__author__ = "Josh"

from chem import *

from debug import print_compact_stack, print_compact_traceback


# == Molecule (i.e. Chunk)

# (Josh wrote:)
# I use "molecule" and "part" interchangeably throughout the program.
# this is the class intended to represent rigid collections of
# atoms bonded together, but it's quite possible to make a molecule
# object with unbonded atoms, and with bonds to atoms in other
# molecules

# Huaicai: It's completely possible to create a molecule without any atoms,
# so don't assume it always has atoms.   09/30/04
class molecule(Node):
    def __init__(self, assembly, nam=None, dad=None):
        Node.__init__(self, assembly, dad, nam or gensym("Mol"))
        # atoms in a dictionary, indexed by atom.key
        self.atoms = {}
        # motors, grounds
        self.gadgets = []
        # center and bounding box of the molecule
        self.center=V(0,0,0)
        # this overrides global display (GLPane.display)
        # but is overriden by atom value if not default
        self.display = diDEFAULT
        # this set and the molecule in assembly.selmols
        # must remain consistent
        self.picked=0
        # this specifies the molecule's attitude in space
        self.quat = Q(1, 0, 0, 0)
        # this overrides atom colors if set
        self.color = None
        # for caching the display as a GL call list
        self.displist = glGenLists(1)
        self.havelist = 0
        # default place to bond this molecule -- should be a singlet
        self.hotspot = None
        
          
    def bond(self, at1, at2):
        """Cause atom at1 to be bonded to at2
        """
        b=bond(at1,at2)
        #bruce 041029 precautionary change -- I find in debugging that the bond
        # can be already in one but not the other of at1.bonds and at2.bonds,
        # as a result of prior bugs. To avoid worsening those bugs, we should
        # change this... but for now I'll just print a message about it.
        if (b in at1.bonds) != (b in at2.bonds):
            print "fyi: debug: for new bond %r, (b in at1.bonds) != (b in at2.bonds)" % b
        if not b in at2.bonds:
            at1.bonds += [b]
            at2.bonds += [b]
        # may have changed appearance of the molecule
        self.havelist = 0
        ###e bruce 041029: what about havelist of the other molecule??

    def shakedown(self):
        """Find center and bounding box for atoms, and set each one's
        xyz to be relative to the center and find principal axes
        """
        if not self.atoms:
            self.bbox = BBox()
            self.center = V(0,0,0)
            self.quat = Q(1,0,0,0)
            self.axis = V(1,0,0)
            self.basepos = self.curpos = []
            #bruce 041029 take more precautions:
            self.atlist = self.singlets = self.singlpos = self.singlbase = []
            del self.polyhedron, self.eval, self.evec, self.axis
            self.externs = []
            self.havelist = 0
            return
        atpos = []
        atlist = []
        singlets = []
        singlpos = []
        for a,i in zip(self.atoms.values(),range(len(self.atoms))):
            pos = a.posn()
            atpos += [pos]
            atlist += [a]
            a.index = i
            a.xyz = 'no'
            if a.element == Singlet:
                 singlets += [a]
                 singlpos += [pos]
        atpos = A(atpos)
        

        self.bbox = BBox(atpos)
        self.center = add.reduce(atpos)/len(self.atoms)
        self.quat = Q(1,0,0,0)  # since all atoms are in place 

        # make the positions relative to the center
        self.basepos = atpos-self.center
        self.curpos = atpos
        self.atlist = array(atlist, PyObject)
        self.singlets = array(singlets, PyObject)
        if self.singlets:
            self.singlpos = array(singlpos)
            self.singlbase = self.singlpos - self.center

        # find extrema in many directions
        xtab = dot(self.basepos, polyXmat)
        mins = minimum.reduce(xtab) - 1.8
        maxs = maximum.reduce(xtab) + 1.8

        self.polyhedron = makePolyList(cat(maxs,mins))

        # and compute inertia tensor
        tensor = zeros((3,3),Float)
        for p in self.basepos:
            rsq = dot(p, p)
            m= - multiply.outer(p, p)
            m[0,0] += rsq
            m[1,1] += rsq
            m[2,2] += rsq
            tensor += m
        self.eval, self.evec = eigenvectors(tensor)
    
        # Pick a principal axis: if square or circular, the axle;
        # otherwise the long axis (this is a heuristic)
        if len(atpos)<=1:
            self.axis = V(1,0,0)
        elif len(atpos) == 2:
            self.axis = norm(subtract.reduce(atpos))
        else:
            ug = argsort(self.eval)
            if self.eval[ug[0]]/self.eval[ug[1]] >0.95:
                self.axis = self.evec[ug[2]]
            else: self.axis = self.evec[ug[0]]
            
        # bruce 041029 revised following code
        self.externs = INVALID_EXTERNS
        self.fix_externs() # note: includes changeapp()
        return # from molecule.shakedown

    def externs_valid(self): #bruce 041029
        return type(self.externs) == type([])

    def fix_externs(self): #bruce 041029
        "if self.externs is marked as invalid, make it correct (and setup all bonds)"
        if type(self.externs) != type([]):
            assert self.externs == INVALID_EXTERNS
            # following code taken from self.draw(); similar to other methods
            drawn = {}
            self.externs = []
            for atm in self.atoms.itervalues():
                for bon in atm.bonds:
                    if bon.key not in drawn:
                        if bon.other(atm).molecule != self:
                            self.externs += [bon]
                        else:
                            drawn[bon.key] = bon
                        bon.setup()
            # may have changed appearance of the molecule
            self.havelist = 0 # changeapp()
        assert self.externs_valid()
        return # from molecule.fix_externs

    def freeze(self):
        """ set the molecule up for minimization or simulation"""
        self.center = V(0,0,0)
        self.quat = Q(1,0,0,0)  
        self.basepos = self.curpos # reference == same object
        if self.singlets:
            self.singlbase = self.singlpos # ditto

    def unfreeze(self):
        """ to be done at the end of minimization or simulation"""
        self.shakedown()


    def draw(self, o, dispdef):
        """draw all the atoms, using the atom's, molecule's,
        or GLPane's display mode in that order of preference
        Use the hash table drawn to draw each bond only once,
        as each one will be referenced from two atoms
        If the molecule itself is selected, draw its
        bounding box as a wireframe
        o is a GLPane
        """
        if self.hidden: return
        self.glpane = o # needed for the edit method - Mark [2004-10-13]
        
        #Tried to fix some bugs by Huaicai 09/30/04
        if len(self.atoms) == 0:
            return
            # do nothing for a molecule without any atoms

        # put it in its place
        glPushMatrix()

        glTranslatef(self.center[0], self.center[1], self.center[2])
        
        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)

        if self.picked:
            drawlinelist(PickedColor,self.polyhedron)

        if self.display != diDEFAULT: disp = self.display
        else: disp = o.display

        # cache molecule display as GL list
        if self.havelist and self.externs_valid():
            glCallList(self.displist)

        else:
            glNewList(self.displist, GL_COMPILE_AND_EXECUTE)

            # bruce 041028 -- protect against exceptions while making display
            # list, or OpenGL will be left in an unusable state (due to the lack
            # of a matching glEndList) in which any subsequent glNewList is an
            # invalid operation. (Also done in shape.py; not needed in drawer.py.)
            try:
                self.draw_displist(o, disp) # also recomputes self.externs
            except:
                print_compact_traceback("exception in molecule.draw_displist ignored: ")
            glEndList()
            self.havelist = 1 # always set this flag, even if exception happened,
            # so it doesn't keep happening with every redraw of this molecule.
            #e (in future it might be safer to remake the display list to contain
            # only a known-safe thing, like a bbox and an indicator of the bug.)
            
        glPopMatrix()

        for bon in self.externs:
            bon.draw(o, disp, self.color, self.assy.drawLevel)
        return # from molecule.draw()

    def draw_displist(self, glpane, disp): #bruce 041028 split this out of molecule.draw

        drawLevel = self.assy.drawLevel
        drawn = {}
        self.externs = []
        
        for atm in self.atoms.itervalues():
            try:
                # bruce 041014 hack for extrude -- use colorfunc if present
                try:
                    color = self.colorfunc(atm)
                except: # no such attr, or it's None, or it has a bug
                    color = self.color
                # end bruce hack, except for use of color rather than
                # self.color in atm.draw (but not in bon.draw -- good??)
                atm.draw(glpane, disp, color, drawLevel)
                for bon in atm.bonds: # similar to self.fix_externs(), but draws
                    if bon.key not in drawn:
                        if bon.other(atm).molecule != self:
                            self.externs += [bon]
                        else:
                            drawn[bon.key] = bon
                            bon.draw(glpane, disp, self.color, drawLevel)
            except:
                # [bruce 041028 general workaround to make bugs less severe]
                # exception in drawing one atom. Ignore it and try to draw the
                # other atoms. #e In future, draw a bug-symbol in its place.
                print_compact_traceback("exception in drawing one atom or bond ignored: ")
        return # from molecule.draw_displist()

    def writemmp(self, atnums, alist, f):
        disp = dispNames[self.display]
        f.write("mol (" + self.name + ") " + disp + "\n")
        for a in self.atoms.itervalues():
            a.writemmp(atnums, alist, f)

    # write to a povray file:  draw the atoms and bonds inside a molecule
    def povwrite(self, file, disp):
        if self.hidden: return
#    def povwrite(self, file, win):

        if self.display != diDEFAULT: disp = self.display
#        else: disp = win.display
#        disp = self.display
        
        drawn = {}
        for atm in self.atoms.itervalues():
            atm.povwrite(file, disp, self.color)
            for bon in atm.bonds:
                if bon.key not in drawn:
                    drawn[bon.key] = bon
                    bon.povwrite(file, disp, self.color)

    def move(self, offs):
        self.center += offs
        self.curpos = self.center + self.quat.rot(self.basepos)
        if self.singlets:
            self.singlpos = self.center + self.quat.rot(self.singlbase)
        self.fix_externs()
        for bon in self.externs: bon.setup()
        
        #Added by Huaicai 10/27/04
        #Update its bounding box
        self.bbox.data += offs


    def rot(self, q):
        self.quat += q
        self.curpos = self.center + self.quat.rot(self.basepos)
        if self.singlets:
            self.singlpos = self.center + self.quat.rot(self.singlbase)
        self.fix_externs()
        for bon in self.externs: bon.setup()
        
        #Added by Huaicai 10/27/04
        #Update its bounding box
        self.bbox = BBox(self.curpos)
        

    def pivot(self, point, q):
        """pivot the molecule around point by quaternion q
        """
        r = point - self.center
        self.center += r - q.rot(r)
        self.quat += q
        self.curpos = self.center + self.quat.rot(self.basepos)
        if self.singlets:
            self.singlpos = self.center + self.quat.rot(self.singlbase)
        self.fix_externs()
        for bon in self.externs: bon.setup()


    def stretch(self, factor):
        self.basepos *= 1.1
        self.curpos = self.center + self.quat.rot(self.basepos)
        if self.singlets:
            self.singlpos = self.center + self.quat.rot(self.singlbase)
        self.fix_externs()
        for bon in self.externs: bon.setup()
        self.changeapp()


    def getaxis(self):
        return self.quat.rot(self.axis)

    def setcolor(self, color):
        """change the molecule's color
        """
        self.color = color
        self.havelist = 0

    def setDisplay(self, disp):
        self.display = disp
        self.havelist = 0
        
    def changeapp(self):
        """call when you've changed appearance of the molecule
        """ 
        self.havelist = 0

    def seticon(self, treewidget):
        self.icon = treewidget.moleculeIcon
        
    def getinfo(self):
        # Return information about the selected moledule for the msgbar [mark 2004-10-14]
        ele2Num = {}
        
        # Determine the number of element types in this molecule.
        for a in self.atoms.itervalues():
            if not ele2Num.has_key(a.element.symbol): ele2Num[a.element.symbol] = 1 # New element found
            else: ele2Num[a.element.symbol] += 1 # Increment element
            
        # String construction for each element to be displayed.
        natoms = len(self.atoms) # number of atoms in the chunk
        nsinglets = 0
        einfo = ""
     
        for item in ele2Num.iteritems():
            if item[0] == "X":  # It is a Singlet
                nsinglets = int(item[1])
                continue
            else: eleStr = "[" + item[0] + ": " + str(item[1]) + "] "
            einfo += eleStr
            
        if nsinglets: # Add singlet info to end of info string
            eleStr = "[Singlets: " + str(nsinglets) + "]"
            einfo += eleStr
         
        natoms -= nsinglets   # The real number of atoms in this chunk

        minfo =  "Chunk Name: [" + str (self.name) + "]     Total Atoms: " + str(natoms) + " " + einfo
                        
        return minfo

    def pick(self):
        """select the molecule.
        """
        if not self.picked:
            Node.pick(self)
            self.assy.selmols.append(self)
            # may have changed appearance of the molecule
            self.havelist = 0

            # print molecule info on the msgbar. - Mark [2004-10-14]
            self.assy.w.msgbarLabel.setText(self.getinfo())

    def unpick(self):
        """unselect the molecule.
        """
        if self.picked:
            Node.unpick(self)
            if self in self.assy.selmols: self.assy.selmols.remove(self)
            # may have changed appearance of the molecule
            self.havelist = 0
            # self.assy.w.msgbarLabel.setText(" ")

    def kill(self):
        #e bruce 041029 thinks we'll someday want to detect killing a mol or Node twice
        self.fix_externs() # bruce 041029; calls setup on all bonds (ok??)
        # (caller no longer needs to set externs to [] when there are no atoms)
        self.unpick()
        Node.kill(self)
        try:
            self.assy.molecules.remove(self)
            self.assy.modified = 1
        except ValueError:
            print "fyi: mol.kill: mol %r not in self.assy.molecules" % self #bruce 041029
            pass
        for b in self.externs:
            b.bust(self)
        self.externs = [] #bruce 041029 precaution against repeated kills
        
        #10/28/04, delete all atoms, so gadgets attached can be deleted when no atoms
        #  attaching the gadget . Huaicai
        for a in self.atoms.values(): a.kill()

        #bruce 041029 precautions:
        if self.atoms:
            print "fyi: bug (ignored): %r mol.kill retains killed atoms %r" % (self,self.atoms)
        self.atoms = {}
        self.shakedown() # this is fast, now that we have no atoms
        return # from molecule.kill

    # point is some point on the line of sight
    # matrix is a rotation matrix with z along the line of sight,
    # positive z out of the plane
    # return positive points only, sorted by distance
    def findatoms(self, point, matrix, radius, cutoff):
        v = dot(self.curpos-point,matrix)
        r = sqrt(v[:,0]**2 + v[:,1]**2)
        i = argmax(v[:,2] - 100000.0*(r>radius))
        if r[i]>radius: return None
        if v[i,2]<cutoff: return None
        return self.atlist[i]


    # point is some point on the line of sight
    # matrix is a rotation matrix with z along the line of sight,
    # positive z out of the plane
    # return positive points only, sorted by distance
    def findSinglets(self, point, matrix, radius, cutoff):
        if not self.singlets: return None
        v = dot(self.singlpos-point,matrix)
        r = sqrt(v[:,0]**2 + v[:,1]**2)
        i = argmax(v[:,2] - 100000.0*(r>radius))
        if r[i]>radius: return None
        if v[i,2]<cutoff: return None
        return self.singlets[i]

    # Same, but return all that match
    def findAllSinglets(self, point, matrix, radius, cutoff):
        if not self.singlets: return []
        v = dot(self.singlpos-point,matrix)
        r = sqrt(v[:,0]**2 + v[:,1]**2)
        lis = []
        for i in range(len(self.singlets)):
            if r[i]<=radius and v[i,2]>=cutoff: lis += [self.singlets[i]]
        return lis

    # return the singlets in the given sphere
    # sorted by increasing distance from the center
    def nearSinglets(self, point, radius):
        if not self.singlets: return []
        v = self.singlpos-point
        r = sqrt(v[:,0]**2 + v[:,1]**2 + v[:,2]**2)
        p= r<=radius
        i=argsort(compress(p,r))
        return take(compress(p,self.singlets),i)

    def copy(self, dad=None, offset=V(0,0,0)):
        """Copy the molecule to a new molecule.
        offset tells where it will go relative to the original.
        """
        pairlis = []
        ndix = {}
        numol = molecule(self.assy, gensym(self.name))
        for a in self.atoms.itervalues():
            na = a.copy(numol)
            pairlis += [(a, na)]
            ndix[a.key] = na
        for (a, na) in pairlis:
            for b in a.bonds:
                if b.other(a).key in ndix:
                    numol.bond(na,ndix[b.other(a).key])
        try: numol.hotspot = ndix[self.hotspot.key]
        except AttributeError: pass
        numol.curpos = self.curpos+offset
        numol.shakedown()
        numol.setDisplay(self.display)
        numol.dad = dad
        return numol

    def passivate(self, p=False):
        for a in self.atoms.values():
            if p or a.picked: a.passivate()

        self.shakedown()

    def Hydrogenate(self):
        """Add hydrogen to all unfilled bond sites on carbon
        atoms assuming they are in a diamond lattice.
        For hilariously incorrect results, use on graphite.
        This ought to be an atom method.
        """
        # will change appearance of the molecule
        self.havelist = 0
        for a in self.atoms.values():
            a.Hydrogenate()
            
    def Dehydrogenate(self):
        """remove hydrogen atoms from selected molecule.
        Return the number of atoms removed [bruce 041018 new feature].
        [bruce comment 041018: I think caller MUST do a shakedown,
         or kill the molecule if it ends up with no atoms.
         In theory, neighbors of removed H can be in other molecules,
         and those also need shakedown or kill.
         But I think it would be wrong to do any of that here.]
        """
        # will change appearance of the molecule
        self.havelist = 0
        count = 0
        for a in self.atoms.values():
            count += a.Dehydrogenate()
        return count
            
    def edit(self):
        cntl = MoleculeProp(self)    
        cntl.exec_loop()
        self.assy.mt.update()


    def __str__(self):
        return "<Molecule of " + self.name + ">"

    def dump(self):
        print self, len(self.atoms), 'atoms,', len(self.singlets), 'singlets'
        for a in self.atlist:
            print a
            for b in a.bonds:
                print b

    def merge(self, mol):
        """merge the given molecule into this one.
        assume they are in the same assy.
        """
        # bruce 041029 wonders why it matters whether self and mol are in the
        # same assembly... if anyone knows, can you add a comment?
        pairlis = []
        ndix = {}
        for a in mol.atoms.values():
            a.hopmol(self)
        assert not mol.atoms # bruce 041029
        self.shakedown()
        ## mol.externs = [] # bruce 041029 thinks no longer needed; seems ok
        mol.kill()

def oneUnbonded(elem, assy, pos):
    """[bruce comment 040928:] create one unbonded atom, of element elem,
    at position pos, in its own new molecule."""
    mol = molecule(assy, gensym('Chunk.'))
    a = atom(elem.symbol, pos, mol)
    r = elem.rcovalent
    if elem.bonds and elem.bonds[0][2]:
        for dp in elem.bonds[0][2]:
            x = atom('X', pos+r*dp, mol)
            mol.bond(a,x)
    assy.addmol(mol)

    return a

def makeBonded(s1, s2):
    """s1 and s2 are singlets; make a bond between their real atoms in
    their stead. If they are in different molecules, move s1's to
    match the bond. Set its center to the bond point and its axis to
    the line of the bond.
    """
    b1 = s1.bonds[0]
    b2 = s2.bonds[0]
    a1 = b1.other(s1)
    a2 = b2.other(s2)
    m1 = s1.molecule
    m2 = s2.molecule
    if m1 != m2: # move the molecule
        m1.rot(Q(a1.posn()-s1.posn(), s2.posn()-a2.posn()))
        m1.move(s2.posn()-s1.posn())
    s1.kill()
    s2.kill()
    m1.bond(a1,a2)
    m1.shakedown()
    m2.shakedown()

    # caller must take care of redisplay
    
# this code knows where to place missing bonds in carbon
# sure to be used later

        
##         # length of Carbon-Hydrogen bond
##         lCHb = (Carbon.bonds[0][1] + Hydrogen.bonds[0][1]) / 100.0
##         for a in self.atoms.values():
##             if a.element == Carbon:
##                 valence = len(a.bonds)
##                 # lone atom, pick 4 directions arbitrarily
##                 if valence == 0:
##                     b=atom("H", a.xyz+lCHb*norm(V(-1,-1,-1)), self)
##                     c=atom("H", a.xyz+lCHb*norm(V(1,-1,1)), self)
##                     d=atom("H", a.xyz+lCHb*norm(V(1,1,-1)), self)
##                     e=atom("H", a.xyz+lCHb*norm(V(-1,1,1)), self)
##                     self.bond(a,b)
##                     self.bond(a,c)
##                     self.bond(a,d)
##                     self.bond(a,e)

##                 # pick an arbitrary tripod, and rotate it to
##                 # center away from the one bond
##                 elif valence == 1:
##                     bpos = lCHb*norm(V(-1,-1,-1))
##                     cpos = lCHb*norm(V(1,-1,1))
##                     dpos = lCHb*norm(V(1,1,-1))
##                     epos = V(-1,1,1)
##                     q1 = Q(epos, a.bonds[0].other(a).xyz - a.xyz)
##                     b=atom("H", a.xyz+q1.rot(bpos), self)
##                     c=atom("H", a.xyz+q1.rot(cpos), self)
##                     d=atom("H", a.xyz+q1.rot(dpos), self)
##                     self.bond(a,b)
##                     self.bond(a,c)
##                     self.bond(a,d)

##                 # for two bonds, the new ones can be constructed
##                 # as linear combinations of their sum and cross product
##                 elif valence == 2:
##                     b=a.bonds[0].other(a).xyz - a.xyz
##                     c=a.bonds[1].other(a).xyz - a.xyz
##                     v1 = - norm(b+c)
##                     v2 = norm(cross(b,c))
##                     bpos = lCHb*(v1 + sqrt(2)*v2)/sqrt(3)
##                     cpos = lCHb*(v1 - sqrt(2)*v2)/sqrt(3)
##                     b=atom("H", a.xyz+bpos, self)
##                     c=atom("H", a.xyz+cpos, self)
##                     self.bond(a,b)
##                     self.bond(a,c)

##                 # given 3, the last one is opposite their average
##                 elif valence == 3:
##                     b=a.bonds[0].other(a).xyz - a.xyz
##                     c=a.bonds[1].other(a).xyz - a.xyz
##                     d=a.bonds[2].other(a).xyz - a.xyz
##                     v = - norm(b+c+d)
##                     b=atom("H", a.xyz+lCHb*v, self)
##                     self.bond(a,b)
