# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
depositMode.py


$Id$

"""
from Numeric import *
from modes import *
from VQT import *
from chem import *
import drawer
from constants import elemKeyTab

def do_what_MainWindowUI_should_do(w):
    w.depositAtomDashboard.clear()

    w.depositAtomDashboard.addSeparator()

    w.depositAtomLabel = QLabel(w.depositAtomDashboard,"Build")
    w.depositAtomLabel.setText(" -- Build -- ")
    w.depositAtomDashboard.addSeparator()

    w.pasteComboBox = QComboBox(0,w.depositAtomDashboard,
                                     "pasteComboBox")

    w.depositAtomDashboard.addSeparator()

    w.elemChangeComboBox = QComboBox(0,w.depositAtomDashboard,
                                     "elemChangeComboBox")

    w.depositAtomDashboard.addSeparator()

    bg = QButtonGroup(w.depositAtomDashboard)
    lay = QHBoxLayout(bg)
    lay.setAutoAdd(True)
    w.depositAtomDashboard.pasteRB = QRadioButton("Paste", bg)
    w.depositAtomDashboard.atomRB = QRadioButton("Atom", bg)
    
    w.depositAtomDashboard.addSeparator()
    w.toolsDoneAction.addTo(w.depositAtomDashboard)
    w.depositAtomDashboard.setLabel("Build")
    w.elemChangeComboBox.clear()
    w.elemChangeComboBox.insertItem("Hydrogen")
    w.elemChangeComboBox.insertItem("Helium")
    w.elemChangeComboBox.insertItem("Boron")
    w.elemChangeComboBox.insertItem("Carbon")
    w.elemChangeComboBox.insertItem("Nitrogen")
    w.elemChangeComboBox.insertItem("Oxygen")
    w.elemChangeComboBox.insertItem("Fluorine")
    w.elemChangeComboBox.insertItem("Neon")
    w.elemChangeComboBox.insertItem("Aluminum")
    w.elemChangeComboBox.insertItem("Silicon")
    w.elemChangeComboBox.insertItem("Phosphorus")
    w.elemChangeComboBox.insertItem("Sulfur")
    w.elemChangeComboBox.insertItem("Chlorine")
    w.elemChangeComboBox.insertItem("Argon")
    w.elemChangeComboBox.insertItem("Germanium")
    w.elemChangeComboBox.insertItem("Astatine")
    w.elemChangeComboBox.insertItem("Selenium")
    w.elemChangeComboBox.insertItem("Bromine")
    w.elemChangeComboBox.insertItem("Krypton")
    w.elemChangeComboBox.insertItem("Antimony")
    w.elemChangeComboBox.insertItem("Tellurium")
    w.elemChangeComboBox.insertItem("Iodine")
    w.elemChangeComboBox.insertItem("Xenon")
    w.connect(w.elemChangeComboBox,SIGNAL("activated(int)"),w.elemChange)

class depositMode(basicMode):
    """ This class is used to manually add atoms to create any structure.
       Users know it as "Build mode".
    """
    
    # class constants
    backgroundColor = 74/256.0, 187/256.0, 227/256.0
    gridColor = 74/256.0, 187/256.0, 227/256.0
    modename = 'DEPOSIT' 
    msg_modename = "Build mode" 
    default_mode_status_text = "Mode: Build"

    def __init__(self, glpane):
        basicMode.__init__(self, glpane)

    # methods related to entering this mode
    
    def Enter(self): # bruce 040922 split setMode into Enter and init_gui (fyi)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        basicMode.Enter(self)
        self.o.assy.unpickatoms()
        self.o.assy.unpickparts()
        self.saveDisp = self.o.display
        self.o.setDisplay(diTUBES)
        self.o.assy.selwhat = 0
        self.new = None
        self.o.selatom = None
        self.dragatom = None
        self.dragmol = None
        self.pivot = None
        self.pivax = None
        self.baggage = []
        self.line = None
        self.modified = 0 # bruce 040923 new code
        self.pastable = None
    
    # init_gui does all the GUI display when entering this mode [mark 041004]
    def init_gui(self):
#        print "depositMode.py: init_gui(): Cursor set to DepositAtomCursor"
        self.o.setCursor(self.w.DepositAtomCursor)
        # load default cursor for MODIFY mode
        self.w.toolsDepositAtomAction.setOn(1) # turn on the Deposit Atoms icon
        
        self.w.pasteComboBox.clear()
        cx = 0
        for ob,i in zip(self.o.assy.shelf.members,
                        range(len(self.o.assy.shelf.members))):
            self.w.pasteComboBox.insertItem(ob.name)
            if ob.picked: cx = i
            self.pastable = ob
        self.w.pasteComboBox.setCurrentItem(cx)
            
        self.w.connect(self.w.pasteComboBox,SIGNAL("activated(int)"),
                       self.setPaste)
        self.w.connect(self.w.elemChangeComboBox,SIGNAL("activated(int)"),
                       self.setAtom)
        
        if self.w.pasteP: self.w.depositAtomDashboard.pasteRB.setOn(True)
        else: self.w.depositAtomDashboard.atomRB.setOn(True)
            
        self.w.connect(self.w.depositAtomDashboard.pasteRB,
                       SIGNAL("pressed()"), self.setPaste)
        self.w.connect(self.w.depositAtomDashboard.atomRB,
                       SIGNAL("pressed()"), self.setAtom)
        
        self.w.depositAtomDashboard.show() # show the Deposit Atoms dashboard

    # methods related to exiting this mode [bruce 040922 made these from
    # old Done method, and added new code; there was no Flush method]

    def haveNontrivialState(self):
        return False
        #return self.modified # bruce 040923 new code

    def StateDone(self):
        return None
    # we never have undone state, but we have to implement this method,
    # since our haveNontrivialState can return True

    def StateCancel(self):
        # to do this correctly, we'd need to remove the atoms we added
        # to the assembly; we don't attempt that yet [bruce 040923,
        # verified with Josh]
        change_desc = "your changes are"
            #e could use the count of changes in self.modified,
            #to say "%d changes are", or "change is"...
        msg = "%s Cancel not implemented -- %s still there.\n\
        You can only leave this mode via Done." % \
              ( self.msg_modename, change_desc )
        self.warning( msg, bother_user_with_dialog = 1)
        return True # refuse the Cancel
    
    # restore_gui handles all the GUI display when leavinging this mode
    # [mark 041004]
    def restore_gui(self):
        self.w.depositAtomDashboard.hide() # Stow away dashboard


    def restore_patches(self):
        self.o.display = self.saveDisp
        self.o.selatom = None

    def clear(self):
        self.new = None

    # event methods
    
    def keyPress(self,key):
        if key == Qt.Key_Control:
            self.o.setCursor(self.w.KillCursor)
        for sym, code, num in elemKeyTab:
            if key == code:
                self.w.setElement(num)
        return

    def keyRelease(self,key):
        basicMode.keyRelease(self, key)
        if key == Qt.Key_Control:
            self.o.setCursor(self.w.DepositAtomCursor)

    def rightCntlDown(self, event):          
            basicMode.rightCntlDown(self, event)
            self.o.setCursor(self.w.DepositAtomCursor)

    def getCoords(self, event):
        """ Retrieve the object coordinates of the point on the screen
	with window coordinates(int x, int y) 
	"""
        x = event.pos().x()
        y = self.o.height - event.pos().y()

        p1 = A(gluUnProject(x, y, 0.0))
        p2 = A(gluUnProject(x, y, 1.0))
        at = self.o.assy.findpick(p1,norm(p2-p1),2.0)
        if at: pnt = at.posn()
        else: pnt = - self.o.pov
        k = (dot(self.o.lineOfSight,  pnt - p1) /
             dot(self.o.lineOfSight, p2 - p1))

        return p1+k*(p2-p1)

    def bareMotion(self, event, singOnly=False):
        doPaint = 0
        if self.o.selatom:
            self.o.selatom.molecule.changeapp()
            self.o.selatom = None
            doPaint = 1
        p1, p2 = self.o.mousepoints(event)
        z = norm(p1-p2)
        x = cross(self.o.up,z)
        y = cross(z,x)
        mat = transpose(V(x,y,z))
        for mol in self.o.assy.molecules:
            if not mol.hidden:
                a = mol.findatoms(p2, mat, TubeRadius, -TubeRadius)
                # can't use findSinglets
                if a and (a.element==Singlet or not singOnly):
                    mol.changeapp()
                    self.o.selatom = a
                    doPaint = 1
                    break
        if doPaint: self.o.paintGL()
	
    def leftDown(self, event):
        """If there's nothing nearby, deposit a new atom.
        If cursor is on a singlet, deposit an atom bonded to it.
        If it is a real atom, drag it around.
        """
        a = self.o.selatom
        el =  PeriodicTable[self.w.Element]
        self.modified = 1
        self.o.assy.modified = 1
        if a: # if something was "lit up"
            if a.element == Singlet:
                if self.w.pasteP and self.pastable: self.pasteBond(a)
                elif not self.w.pasteP: self.attach(el, a)
                self.o.selatom = None
                self.dragmol = None
                self.w.update()
                return # don't move a newly bonded atom
            # else we've grabbed an atom
            elif a.realNeighbors(): # part of larger molecule
                self.dragmol = a.molecule
                a.molecule.fix_externs() #bruce 041029
                e=a.molecule.externs
                if len(e)==1: # pivot around one bond
                    self.pivot = e[0].center
                    self.pivax = None
                    return
                elif len(e)==2: # pivot around 2 bonds
                    self.pivot = e[0].center
                    self.pivax = norm(e[1].center-e[0].center)
                    return
                elif len(e)==0: # drag it around
                    self.pivot = None
                    self.pivax = True
                    return
            # no externs or more than 2 -- fall thru
        else:
            atomPos = self.getCoords(event)
            if self.w.pasteP and self.pastable:
                self.pasteFree(atomPos)
                self.dragmol = None
            elif not self.w.pasteP: 
                self.o.selatom = oneUnbonded(el, self.o.assy, atomPos)
                self.dragmol = self.o.selatom.molecule
        # move the molecule rigidly
        self.pivot = None
        self.pivax = None
        self.w.update()
                        

    def leftDrag(self, event):
        """ drag the new atom around
	"""
        if not (self.dragmol and self.o.selatom): return
        m = self.dragmol
        a = self.o.selatom
        p1, p2 = self.o.mousepoints(event)
        px = ptonline(a.posn(), p1, norm(p2-p1))
        if self.pivot:
            po = a.posn() - self.pivot
            pxv = px - self.pivot
        if self.pivot and self.pivax:
            m.pivot(self.pivot, twistor(self.pivax, po, pxv))
        elif self.pivot:
            q1 = twistor(self.pivot-m.center, po, pxv)
            q2 = Q(q1.rot(po), pxv)
            m.pivot(self.pivot, q1+q2)
        elif self.pivax:
            m.rot(Q(a.posn()-m.center,px-m.center))
            m.move(px-a.posn())
        else:
            m.move(px-a.posn())
        self.o.paintGL()

    def leftUp(self, event):
        self.dragmol = None
        self.o.selatom = None
	
    def leftShiftDown(self, event):
        """If there's nothing nearby, do nothing If cursor is on a
        singlet, drag it around, rotating the atom it's bonded to if
        possible.  If it is a real atom, drag it around.
        """
        a = self.o.selatom
        if not a: return
        # now, if something was "lit up"
        self.modified = 1
        self.o.assy.modified = 1
        if a.element == Singlet:
            pivatom = a.neighbors()[0]
            neigh = pivatom.realNeighbors()
            self.baggage = pivatom.singNeighbors()
            self.baggage.remove(a)
            if neigh:
                if len(neigh)==2:
                    self.pivot = pivatom.posn()
                    self.pivax = norm(neigh[0].posn()-neigh[1].posn())
                    self.baggage = []
                elif len(neigh)>2:
                    self.pivot = None
                    self.pivax = None
                    self.baggage = []
                else: # atom on a single stalk
                    self.pivot = pivatom.posn()
                    self.pivax = norm(self.pivot-neigh[0].posn())
            else: # no real neighbors
                self.pivot = pivatom.posn()
                self.pivax = None
        else: # we've grabbed an atom
            self.pivot = None
            self.pivax = None
            self.baggage = a.singNeighbors()
        self.dragatom = a
        self.w.update()
                        

    def leftShiftDrag(self, event):
        """ drag the new atom around
	"""
        if not self.dragatom: return
        a = self.dragatom
        p1, p2 = self.o.mousepoints(event)
        v2 = norm(p2-p1)
        px = ptonline(a.posn(), p1, v2)
        
        if a.element != Singlet and not self.pivot:
            # no pivot, just dragging it around
            apo = a.posn()
            # find the delta quat for the average real bond and apply
            # it to the singlets
            n = a.realNeighbors()
            old = V(0,0,0)
            new = V(0,0,0)
            for at in n:
                old += at.posn()-apo
                new += at.posn()-px
                at.adjSinglets(a, px)
            delta = px - apo
            if n:
                q=Q(old,new)
                for at in self.baggage:
                    at.setposn(q.rot(at.posn()-apo)+px)
            else: 
                for at in self.baggage:
                    at.setposn(at.posn()+delta)
            # [Josh wrote, about the following "a.setposn(px)":]
            # there's some weirdness I don't understand
            # this doesn't work if done before the loop above
            a.setposn(px)
            # [bruce 041108 writes:]
            # This a.setposn(px) can't be done before the at.adjSinglets(a, px)
            # in the loop before it, or adjSinglets (which compares a.posn() to
            # px) would think atom a was not moving.
        elif self.pivax: # pivoting around an axis
            quat = twistor(self.pivax, a.posn()-self.pivot, px-self.pivot)
            for at in [a]+self.baggage:
                at.setposn(quat.rot(at.posn()-self.pivot) + self.pivot)
        elif self.pivot: # pivoting around a point
            quat = Q(a.posn()-self.pivot, px-self.pivot)
            for at in [a]+self.baggage:
                at.setposn(quat.rot(at.posn()-self.pivot) + self.pivot)
        self.bareMotion(event, True)
        if a.element == Singlet:
            self.line = [a.posn(), px]
        self.o.paintGL()

    def leftShiftUp(self, event):
        if not self.dragatom: return
        self.dragatom.molecule.shakedown()
        self.baggage = []
        self.line = None
        self.bareMotion(event, True)
        if self.dragatom.element == Singlet:
            if self.o.selatom and self.o.selatom != self.dragatom:
                makeBonded(self.dragatom, self.o.selatom)
        self.o.paintGL()
        

    ## delete with cntl-left mouse
    def leftCntlDown(self, event):
        a = self.o.selatom
        if a:
            # this may change hybridization someday
            if a.element == Singlet: return
            m = a.molecule
            a.kill()
            if m.atoms: m.shakedown()
            else: m.kill()
        self.w.update()

    def middleDouble(self, event):
        """ End deposit mode
	"""
	self.Done()

    ###################################################################
    #   Cutting and pasting                                           #
    ###################################################################
        
    # paste the pastable object where the cursor is
    def pasteBond(self, sing):
        m = self.pastable
        if len(m.singlets)==0: return
        if len(m.singlets)>1 and not m.hotspot: return
        numol = self.pastable.copy(None)
        hs = numol.hotspot or numol.singlets[0]
        self.o.assy.addmol(numol)
        makeBonded(hs,sing)
        
        
    # paste the pastable object where the cursor is
    def pasteFree(self, pos):
        numol = self.pastable.copy(None, pos)
        
        self.o.assy.addmol(numol)
        


    ###################################################################
    #  Oh, ye acolytes of klugedom, feast your eyes on the following  #
    ###################################################################

    # singlet is supposedly the lit-up singlet we're pointing to.
    # bond the new atom to it, and any other ones around you'd
    # expect it to form bonds with
    def attach(self, el, singlet):
        if not el.numbonds: return
        spot = self.findSpot(el, singlet)
        pl = []
        mol = singlet.molecule
        cr = el.rcovalent

        for s in mol.nearSinglets(spot, cr*1.5):
            pl += [(s, self.findSpot(el, s))]

        n = min(el.numbonds, len(pl))
        if n == 1:
            self.bond1(el, singlet, spot)
        elif n == 2:
            self.bond2(el,pl)
        elif n == 3:
            self.bond3(el,pl)
        elif n == 4:
            self.bond4(el,pl)
        else:
            print "too many bonds!", el.numbonds, len(pl)
        mol.shakedown()
        self.o.paintGL()

    # given an element and a singlet, find the place an atom of the
    # element would like to be if bonded at the singlet
    def findSpot(self, el, singlet):
        obond = singlet.bonds[0]
        a1 = obond.other(singlet)
        cr = el.rcovalent
        pos = singlet.posn() + cr*norm(singlet.posn()-a1.posn())
        return pos

    def bond1(self, el, singlet, pos):
        obond = singlet.bonds[0]
        a1 = obond.other(singlet)
        mol = a1.molecule
        a = atom(el.symbol, pos, mol)
        obond.rebond(singlet, a)
        if el.base:
            # There is at least one other bond
            # this rotates the atom to match the bond formed above
            r = singlet.posn() - pos
            rq = Q(r,el.base)
            # if the other atom has any other bonds, align 60 deg off them
            if len(a1.bonds)>1:
                # don't pick ourself
                if a==a1.bonds[0].other(a1):
                    a2pos = a1.bonds[1].other(a1).posn()
                else: a2pos = a1.bonds[0].other(a1).posn()
                s1pos = pos+(rq + el.quats[0] - rq).rot(r)
                spin = twistor(r,s1pos-pos, a2pos-a1.posn()) + Q(r, pi/3.0)
            else: spin = Q(1,0,0,0)
            for q in el.quats:
                q = rq + q - rq - spin
                x = atom('X', pos+q.rot(r), mol)
                mol.bond(a,x)
        
    def bond2(self, el, lis):
        s1, p1 = lis[0]
        s2, p2 = lis[1]
        pos = (p1+p2)/2.0
        opos = s2.posn()

        mol = s1.molecule
        a = atom(el.symbol, pos, mol)

        s1.bonds[0].rebond(s1, a)
        s2.bonds[0].rebond(s2, a)

        # this rotates the atom to match the bonds formed above
        r = s1.posn() - pos           
        rq = Q(r,el.base)
        # this moves the second bond to a possible position
        # note that it doesn't matter which bond goes where
        q1 = rq + el.quats[0] -rq
        b2p = q1.rot(r)
        # rotate it into place
        tw = twistor(r, b2p, opos-pos)
        # now for all the rest
        for q in el.quats[1:]:
            q = rq + q - rq + tw
            x = atom('X', pos+q.rot(r), mol)
            mol.bond(a,x)

    def bond3(self, el, lis):
        s1, p1 = lis[0]
        s2, p2 = lis[1]
        s3, p3 = lis[2]
        pos = (p1+p2+p3)/3.0
        opos =  (s1.posn() + s2.posn() + s3.posn())/3.0

        mol = s1.molecule
        a = atom(el.symbol, pos, mol)

        s1.bonds[0].rebond(s1, a)
        s2.bonds[0].rebond(s2, a)
        s3.bonds[0].rebond(s3, a)

        opos = pos + el.rcovalent*norm(pos-opos)
        x = atom('X', opos, mol)
        mol.bond(a,x)

    def bond4(self, el, lis):
        s1, p1 = lis[0]
        s2, p2 = lis[1]
        s3, p3 = lis[2]
        s4, p4 = lis[3]
        pos = (p1+p2+p3+p4)/4.0
        opos =  (s1.posn() + s2.posn() + s3.posn() + s4.posn())/4.0

        mol = s1.molecule
        a = atom(el.symbol, pos, mol)

        s1.bonds[0].rebond(s1, a)
        s2.bonds[0].rebond(s2, a)
        s3.bonds[0].rebond(s3, a)
        s4.bonds[0].rebond(s4, a)

    ####################
    # buttons
    ####################

    # add hydrogen atoms to each dangling bond above the water
    def modifyHydrogenate(self):
        pnt = - self.o.pov
        z = self.o.out
        x = cross(self.o.up,z)
        y = cross(z,x)
        mat = transpose(V(x,y,z))

        for mol in self.o.assy.molecules:
            if not mol.hidden:
                for a in mol.findAllSinglets(pnt, mat, 10000.0, -TubeRadius):
                    a.Hydrogenate()
        self.o.paintGL()


    ## dashboard things
        
    def setPaste(self):
        self.w.pasteP = True
        self.w.depositAtomDashboard.pasteRB.setOn(True)
        print 'pasting',self.w.pasteComboBox.currentItem()
        
    def setAtom(self):
        self.w.pasteP = False
        self.pastable = None
        self.w.depositAtomDashboard.atomRB.setOn(True)

    ####################
    # utility routines
    ####################


    def Draw(self):
        """ Draw a sketch plane to indicate where the new atoms will sit
	by default
	"""
	basicMode.Draw(self)
        if self.line: drawline(white, self.line[0], self.line[1])
        self.o.assy.draw(self.o)
        self.surface()

                           
    def surface(self):
        """The water's surface
	"""
	glDisable(GL_LIGHTING)
	glColor4fv(self.gridColor + (0.6,))
        glEnable(GL_BLEND)
        
	# the grid is in eyespace
	glPushMatrix()
	q = self.o.quat
	glTranslatef(-self.o.pov[0], -self.o.pov[1], -self.o.pov[2])
	glRotatef(- q.angle*180.0/pi, q.x, q.y, q.z)
        x = 1.5*self.o.scale
	glBegin(GL_QUADS)
        glVertex(-x,-x,0)
        glVertex(x,-x,0)
        glVertex(x,x,0)
        glVertex(-x,x,0)
	glEnd()
	glPopMatrix()
        glDisable(GL_BLEND)
	glEnable(GL_LIGHTING)
        return

        
    def makeMenus(self):
        
        self.Menu_spec = [
            ('Set Hotspot', self.setHotSpot),
            ('Select', self.select) ] # bruce 041103 capitalized 'Select'

        self.debug_Menu_spec = [
            ("dump", self.dump)
        ]

        # Ninad asks whether we should add more elements to this [bruce 041103]
        self.Menu_spec_shift = [
            ('Carbon', self.w.setCarbon),
            ('Hydrogen', self.w.setHydrogen),
            ('Oxygen', self.w.setOxygen),
            ('Nitrogen', self.w.setNitrogen) ]

        # Ninad says this is redundant, but I left it in; Josh should decide
        # for this mode [bruce 041103]
        self.Menu_spec_control = [
            ('Passivate', self.o.assy.modifyPassivate),
            ('Hydrogenate', self.o.assy.modifyHydrogenate),
            ('Separate', self.o.assy.modifySeparate) ]
        
    def setHotSpot(self):
        """if called on a singlet, make that singlet the hotspot for
        the molecule.  (if there's only one, it's automatically the
        hotspot)
        """
        if self.o.selatom and self.o.selatom.element == Singlet:
            self.o.selatom.molecule.hotspot = self.o.selatom
            new = self.o.selatom.molecule.copy(None)
            new.move(-new.center)
            self.o.assy.shelf.addmember(new)
            self.o.assy.shelf.unpick()
            new.pick()
            self.w.pasteP = True
            self.w.update()
            self.init_gui()


    def select(self):
        if self.o.selatom:
            self.o.assy.pickParts()
            self.o.assy.unpickparts()
            self.o.selatom.molecule.pick()
            self.w.update()
                                    
    def skip(self):
        pass

    def dump(self):
        if self.o.selatom:
            m = self.o.selatom.molecule
            print "mol", m.name, len(m.atoms), len(m.atlist), len(m.curpos)
            m.fix_externs() #bruce 041029
            print 'externs', m.externs
            for a in m.atlist:
                print a
                for b in a.bonds:
                    print '   ', b

    pass # end of class depositMode
