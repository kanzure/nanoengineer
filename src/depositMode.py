# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
depositMode.py

Currently owned by Josh for extensive additions.

$Id$
"""
from Numeric import *
from modes import *
from VQT import *
from chem import *
import drawer
from constants import elemKeyTab


class depositMode(basicMode):
    """ This class is used to manually add atoms to create any structure.
       Users know it as "sketch mode".
    """
    
    # class constants
    backgroundColor = 74/256.0, 187/256.0, 227/256.0
    gridColor = 74/256.0, 187/256.0, 227/256.0
    modename = 'DEPOSIT' 
    msg_modename = "Deposit mode" 
    default_mode_status_text = "Mode: Deposit"

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
        self.modified = 0 # bruce 040923 new code
    
    # init_gui does all the GUI display when entering this mode [mark 041004]
    def init_gui(self):
        self.o.setCursor(self.w.DepositAtomCursor) 
        self.w.depositAtomDashboard.show()

    # methods related to exiting this mode [bruce 040922 made these from
    # old Done method, and added new code; there was no Flush method]

    def haveNontrivialState(self):
        return self.modified # bruce 040923 new code

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
        self.w.depositAtomDashboard.hide()

    def restore_patches(self):
        self.o.display = self.saveDisp
        self.o.selatom = None

    def clear(self):
        self.new = None

    # event methods
    
    def keyPress(self,key):
        for sym, code, num in elemKeyTab:
            if key == code:
                self.w.setElement(num)
        return

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

    def bareMotion(self, event):
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
            if mol.display != diINVISIBLE:
                a = mol.findatoms(p2, mat, TubeRadius, -TubeRadius)
                if a:
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
        self.o.SaveMouse(event)
        self.picking = True
        p1, p2 = self.o.mousepoints(event)
        self.dragdist = 0.0
        a = self.o.selatom
        el =  PeriodicTable[self.w.Element]
        if a: # if something was "lit up"
            self.modified = 1             
            if a.element == Singlet:
                self.attach(el, self.o.selatom)
            # else we've grabbed an atom
        else:
            atomPos = self.getCoords(event)
            self.selatom = oneUnbonded(el, self.o.assy, atomPos)
        self.w.update()
                        

    def leftDrag(self, event):
        """ 
	"""
       
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)

        self.o.SaveMouse(event)

        self.o.paintGL()

    def leftUp(self, event):
        atomPos = self.getCoords(event)
        p1, p2 = self.o.mousepoints(event)

        self.w.update()

    ## delete with cntl-left mouse
    def leftCntlDown(self, event):
        a = self.o.selatom
        if a:
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
        else: print "too many bonds!"
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
        del mol.atoms[singlet.key]
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
        del mol.atoms[s1.key]
        s2.bonds[0].rebond(s2, a)
        del mol.atoms[s2.key]

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
        del mol.atoms[s1.key]
        s2.bonds[0].rebond(s2, a)
        del mol.atoms[s2.key]
        s3.bonds[0].rebond(s3, a)
        del mol.atoms[s3.key]

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
        del mol.atoms[s1.key]
        s2.bonds[0].rebond(s2, a)
        del mol.atoms[s2.key]
        s3.bonds[0].rebond(s3, a)
        del mol.atoms[s3.key]
        s4.bonds[0].rebond(s4, a)
        del mol.atoms[s3.key]


    def Draw(self):
        """ Draw a sketch plane to indicate where the new atoms will sit
	by default
	"""
	basicMode.Draw(self)
        if self.sellist: self.pickdraw()
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
        
        self.Menu1 = self.makemenu([('dump', self.dump),
                                    None,
                                    ('Move', self.move),
                                    ('Double bond', self.skip),
                                    ('Triple bond', self.skip)
                                    ])
        
        self.Menu2 = self.makemenu([('Carbon', self.w.setCarbon),
                                    ('Hydrogen', self.w.setHydrogen),
                                    ('Oxygen', self.w.setOxygen),
                                    ('Nitrogen', self.w.setNitrogen)
                                    ])
        
        self.Menu3 = self.makemenu([('Passivate', self.o.assy.modifyPassivate),
                                    ('Hydrogenate', self.o.assy.modifyHydrogenate),
                                    ('Separate', self.o.assy.modifySeparate)])

    def move(self):
        self.Done(new_mode = 'MODIFY')
                                    
    def skip(self):
        pass

    def dump(self):
        if self.selatom:
            m = self.selatom.molecule
            print "mol", m.name, len(m.atoms), len(m.atlist), len(m.curpos)
            for a in m.atlist:
                print a
                for b in a.bonds:
                    print b

    pass # end of class depositMode
