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
import platform

def do_what_MainWindowUI_should_do(w):
    w.depositAtomDashboard.clear()

    w.depositAtomDashboard.addSeparator()

    w.depositAtomLabel = QLabel(w.depositAtomDashboard,"Build")
    w.depositAtomLabel.setText(" -- Build -- ")
    w.depositAtomDashboard.addSeparator()

    w.pasteComboBox = QComboBox(0,w.depositAtomDashboard,
                                     "pasteComboBox")
    # bruce 041124: that combobox needs to be wider, or to grow to fit items
    # (before this change it had width 100 and minimumWidth 0):
    w.pasteComboBox.setMinimumWidth(160) # barely holds "(clipboard is empty)"

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
    
    def Enter(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        basicMode.Enter(self)
        self.o.assy.unpickatoms()
        self.o.assy.unpickparts()
        self.saveDisp = self.o.display
        self.o.setDisplay(diTUBES)
        self.o.assy.selwhat = 0
        self.new = None # bruce 041124 suspects this is never used
        self.modified = 0 # bruce 040923 new code
        self.pastable = None
        self.o.selatom = None
        self.reset_drag_vars()

    def reset_drag_vars(self):
        #bruce 041124 split this out of Enter; as of 041130,
        # required bits of it are inlined into Down methods as bugfixes
        self.dragatom = None
        self.dragmol = None
        self.pivot = None
        self.pivax = None
        self.baggage = []
        self.line = None
    
    # init_gui does all the GUI display when entering this mode [mark 041004]
    
    # bruce comment 041124 -- init_gui was also being used to update the gui
    # within the mode. That's wrong (especially when it makes someone think
    # that external code should ever call init_gui), so I split out from it an
    # update_gui method, which should be defined here but not called directly
    # except by the internal mode code in modes.py; this file or other files
    # can call mode.UpdateDashboard() when they think that's necessary,
    # which might call mode.update_gui(), or might "invalidate the dashboard"
    # so that mode.update_gui()
    # gets called sometime before the user-event processing is done.
    
    def init_gui(self):
        """called once each time the mode is entered;
        should be called only by code in modes.py
        """
        self.o.setCursor(self.w.DepositAtomCursor)
        # load default cursor for MODIFY mode
        self.w.toolsDepositAtomAction.setOn(1) # turn on the Deposit Atoms icon

        self.pastable = None # by bruce 041124, for safety

        # connect signals (these ought to be disconnected in restore_gui ##e)
        self.w.connect(self.w.pasteComboBox,SIGNAL("activated(int)"),
                       self.setPaste)
        self.w.connect(self.w.elemChangeComboBox,SIGNAL("activated(int)"),
                       self.setAtom)
        self.w.connect(self.w.depositAtomDashboard.pasteRB,
                       SIGNAL("pressed()"), self.setPaste)
        self.w.connect(self.w.depositAtomDashboard.atomRB,
                       SIGNAL("pressed()"), self.setAtom)
        
        self.w.depositAtomDashboard.show() # show the Deposit Atoms dashboard

    dont_update_gui = 0
    
    def update_gui(self):
        """can be called many times during the mode;
        should be called only by code in modes.py
        """

        # avoid unwanted recursion [bruce 041124]
        if self.dont_update_gui:
            return

        # update the contents and current item of self.w.pasteComboBox
        # to match the clipboard
        self.w.pasteComboBox.clear()
        cx = 0
        if self.o.assy.shelf.members: # We have something on the clipboard
            members = list(self.o.assy.shelf.members)
            members.reverse() # bruce 041124 -- model tree seems to have them backwards
            self.pastable = members[0] # (in case none picked)
            for ob,i in zip(members, range(len(members))):
                self.w.pasteComboBox.insertItem(ob.name)
                if ob.picked:
                    cx = i
                    self.pastable = ob # ob is the clipboard object that will be pasted.
        else: # Nothing on the clipboard
            self.pastable = None
            # insert a text label saying it's empty [bruce 041124]
            self.w.pasteComboBox.insertItem("(clipboard is empty)")
            
        # Set pasteComboBox to the picked item (cx)
        # (or to the last picked one, if several are picked)
        self.w.pasteComboBox.setCurrentItem(cx)
            
        # update the radio buttons
        if self.w.pasteP: self.w.depositAtomDashboard.pasteRB.setOn(True)
        else: self.w.depositAtomDashboard.atomRB.setOn(True)
    
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
    	self.o.setDisplay(self.saveDisp) #bruce 041129; see notes for bug 133
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

    def posn_str(self, atm): #bruce 041123
        """return the position of an atom
        as a string for use in our status messages
        (also works if given an atom's position vector itself -- kluge, sorry)
        """
        try:
            x,y,z = atm.posn()
        except AttributeError:
            x,y,z = atm # kluge to accept either arg type
        return "(%.2f, %.2f, %.2f)" % (x,y,z)
    
    def leftDown(self, event):
        """If there's nothing nearby, deposit a new atom.
        If cursor is on a singlet, deposit an atom bonded to it.
        If it is a real atom, drag it around.
        """
        self.pivot = self.pivax = self.dragmol = None #bruce 041130 precautions
        self.bareMotion(event) #bruce 041130 in case no bareMotion happened yet
        a = self.o.selatom
        el =  PeriodicTable[self.w.Element]
        self.modified = 1
        self.o.assy.modified = 1
        if a: # if something was "lit up"
            if a.element == Singlet:
                a0 = a.singlet_neighbor() # do this before a is killed!
                if self.w.pasteP:
                    # user wants to paste something
                    if self.pastable:
                        thing, desc = self.pasteBond(a)
                        if thing:
                            status = "replaced open bond on %r with %s (%s)" % (a0, thing.name, desc)
                        else:
                            status = desc
                            # bruce 041123 added status message, to fix bug 163,
                            # and added the rest of them to describe what we do
                            # (or why we do nothing)
                    else:
                        # do nothing
                        status = "nothing selected to paste" #k correct??
                else:
                    # user wants to create an atom of element el
                    a1, desc = self.attach(el, a)
                    if a1 != None:
                        status = "replaced open bond on %r with new atom %s at %s" % (a0, desc, self.posn_str(a1))
                    else:
                        status = desc
                    del a1, desc
                self.o.selatom = None
                self.dragmol = None
                self.w.msgbarLabel.setText(status)
                self.w.update()
                return # don't move a newly bonded atom
            # else we've grabbed an atom
            elif a.realNeighbors(): # probably part of larger molecule
                self.dragmol = a.molecule
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
                    self.pivax = True #k might have bugs if realNeighbors in other mols??
                    #bruce 041130 tried using this case for 1-atom mol as well,
                    # but it made singlet highlighting wrong (due to pivax??).
                    # (Could that mean there's some sort of basepos-updating bug
                    # in mol.pivot? ###@@@)
                    return
                # more than 2 externs -- fall thru
            elif len(a.molecule.atoms) == 1 + len(a.bonds):
                #bruce 041130 added this case to let plain left drag work to
                # drag a 1-real-atom mol, not only a larger mol as before; the
                # docstring makes me think this was the original intention, and
                # the many "invalid bug reports" whose authors assume this will
                # work imply this feature is desired and intuitively expected.
                self.dragmol = a.molecule
                # fall thru
            else:
                #bruce 041130 added this case too:
                # no real neighbors, but more than just the singlets in the mol
                # (weird but possible)... for now, just do the same, though if
                # there are 1 or 2 externs it might be better to do pivoting. #e
                self.dragmol = a.molecule
                # fall thru
        else:
            # nothing was "lit up" -- we're in empty space;
            # create something and (if an atom) drag it rigidly
            atomPos = self.getCoords(event)
            if self.w.pasteP:
                if self.pastable:
                    thing, desc = self.pasteFree(atomPos)
                    self.dragmol = None
                    status = "pasted %s (%s) at %s" % (thing.name, desc, self.posn_str(atomPos))
                else:
                    # do nothing
                    status = "nothing selected to paste" #k correct??
            else:
                self.o.selatom = oneUnbonded(el, self.o.assy, atomPos)
                self.dragmol = self.o.selatom.molecule
                status = "made new atom %r at %s" % (self.o.selatom, self.posn_str(self.o.selatom) )
            self.w.msgbarLabel.setText(status)
            # fall thru
        # move the molecule rigidly (if self.dragmol and self.o.selatom were set)
        self.pivot = None
        self.pivax = None
        self.w.update()
    
    def dragto(self, point, event, perp = None):
        """Return the point to which we should drag the given point,
        if event is the drag-motion event and we want to drag the point
        parallel to the screen (or perpendicular to the given direction "perp"
        if one is passed in). (Only correct for points, not extended objects,
        unless you use the point which was clicked on (not e.g. the center)
        as the dragged point.)
        """
        #bruce 041123 split this from two methods, and bugfixed to make dragging
        # parallel to screen. (I don't know if there was a bug report for that.)
        # Should be moved into modes.py and used in modifyMode too. ###e
        p1, p2 = self.o.mousepoints(event)
        if perp == None:
            perp = self.o.out
        point2 = planeXline(point, perp, p1, norm(p2-p1)) # args are (ppt, pv, lpt, lv)
        if point2 == None:
            # should never happen, but use old code as a last resort:
            point2 = ptonline(point, p1, norm(p2-p1))
        return point2
        
    def leftDrag(self, event):
        """ drag a new atom or an old atom's molecule
	"""
        #bruce 041130 revised docstring
        if not (self.dragmol and self.o.selatom): return
        m = self.dragmol
        a = self.o.selatom
        px = self.dragto(a.posn(), event)
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
        #e bruce 041130 thinks this should be given a new-coordinates-message,
        # like in leftShiftDrag but starting with the atom-creation message
        # (but the entire mol gets dragged, so the msg should reflect that)
        # ###@@@
        self.o.paintGL()

    def leftUp(self, event):
        self.dragmol = None
        self.o.selatom = None
        #bruce 041130 comment: it forgets selatom, but doesn't repaint,
        # so selatom is still visible; then the next event will probably
        # set it again; all this seems ok for now, so I'll leave it alone.
	
    def leftShiftDown(self, event):
        """If there's nothing nearby, do nothing. If cursor is on a
        singlet, drag it around, rotating the atom it's bonded to if
        possible.  If it is a real atom, drag it around (but not
        the real atoms it's bonded to).
        """
        #bruce 041130 revised docstring
        self.pivot = self.pivax = self.line = None #bruce 041130 precaution
        self.baggage = [] #bruce 041130 precaution
        self.dragatom = None #bruce 041130 fix bug 230 (1 of 2 redundant fixes)
        self.bareMotion(event) #bruce 041130 in case no bareMotion happened yet
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
        return
                        

    def leftShiftDrag(self, event):
        """ drag the atom around
	"""
        if not self.dragatom: return
        a = self.dragatom
        apos0 = a.posn()
        px = self.dragto(a.posn(), event)
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
        self.bareMotion(event, True) # indicate singlets we might bond to
            #bruce 041130 asks: is it correct to do that when a is real?
        if a.element == Singlet:
            self.line = [a.posn(), px]
        #bruce 041130 added status bar message with new coordinates
        apos1 = a.posn()
        if apos1 - apos0:
            ##k does this ever overwrite some other message we want to keep??
            if a.element == Singlet:
                # this message might not be useful enough to be worthwhile...
                msg = "pulling open bond %r to %s" % (a, self.posn_str(a))
            else:
                msg = "dragged atom %r to %s" % (a, self.posn_str(a))
            self.w.msgbarLabel.setText(msg)
        self.o.paintGL()
        return

    def leftShiftUp(self, event):
        if not self.dragatom: return
        self.baggage = []
        self.line = None
        self.bareMotion(event, True)
        if self.dragatom.is_singlet():
            if self.o.selatom and self.o.selatom != self.dragatom:
                dragatom = self.dragatom
                selatom = self.o.selatom
                if selatom.is_singlet(): #bruce 041119, just for safety
                    self.dragged_singlet_over_singlet(dragatom, selatom)
        self.dragatom = None #bruce 041130 fix bug 230 (1 of 2 redundant fixes)
        self.o.paintGL()

    def dragged_singlet_over_singlet(self, dragatom, selatom):
        #bruce 041119 split this out and added checks to fix bugs #203
        # (for bonding atom to itself) and #121 (atoms already bonded).
        # I fixed 121 by doing nothing to already-bonded atoms, but in
        # the future we might want to make a double bond. #e
        if selatom.singlet_neighbor() == dragatom.singlet_neighbor():
            # this is a bug according to the subroutine, but not to us
            print_error_details = 0
        else:
            # for any other error, let subr print a bug report,
            # since we think we caught them all before calling it
            print_error_details = 1
        flag, status = bond_at_singlets(dragatom, selatom, \
                         print_error_details = print_error_details)
        # we ignore flag, which says whether it's ok, warning, or error
        self.w.msgbarLabel.setText("%s: %s" % (self.msg_modename, status))
        return

    ## delete with cntl-left mouse
    def leftCntlDown(self, event):
        self.bareMotion(event) #bruce 041130 in case no bareMotion happened yet
        a = self.o.selatom
        if a:
            # this may change hybridization someday
            if a.element == Singlet: return
            a.kill()
            self.o.selatom = None #bruce 041130 precaution
            self.o.assy.modified = 1
        self.w.update()

    def middleDouble(self, event):
        """ End deposit mode
	"""
	self.Done()

    ###################################################################
    #   Cutting and pasting                                           #
    ###################################################################
    
    def pasteBond(self, sing):
        """If self.pastable has an unambiguous hotspot,
        paste a copy of it onto the given singlet;
        return (the copy, description) or (None, whynot)
        """
        # bruce 041123 added return values (and guessed docstring).
        m = self.pastable
        if len(m.singlets)==0:
            return None, "no open bonds in %r (only pasteable in empty space)" % m.name
        if len(m.singlets)>1 and not m.hotspot:
            return None, "%r has %d open bonds, but none has been set as its hotspot" % (m.name, len(m.singlets))
        numol = self.pastable.copy(None)
        # bruce 041116 added (implicitly, by default) cauterize = 1
        # to mol.copy() above; change this to cauterize = 0 here if unwanted,
        # and for other uses of mol.copy in this file.
        # For this use, there's an issue that new singlets make it harder to
        # find a default hotspot! Hmm... I think copy should set one then.
        # So now it does [041123].
        hs = numol.hotspot or numol.singlets[0]
        bond_at_singlets(hs,sing) # this will move hs.molecule (numol) to match
        self.o.assy.addmol(numol) # do this last, in case it computes bbox
        return numol, "copy of %r" % m.name
        
    # paste the pastable object where the cursor is
    def pasteFree(self, pos):
        numol = self.pastable.copy(None, pos)
        
        self.o.assy.addmol(numol)
        return numol, "copy of %r" % self.pastable.name
        


    ###################################################################
    #  Oh, ye acolytes of klugedom, feast your eyes on the following  #
    ###################################################################

    # singlet is supposedly the lit-up singlet we're pointing to.
    # make a new atom of el.
    # bond the new atom to it, and any other ones around you'd
    # expect it to form bonds with
    # [bruce comment 041115: only bonds to singlets in same molecule; why?
    #  more info 041203:
    #  answer from josh: that's a bug, but we won't fix it for alpha.
    #  bruce thinks it has a recent bug number (eg 220-230) but forgets what it is.
    # ]
    
    # bruce 041123 new features:
    # return the new atom and a description of it, or None and the reason we made nothing.
    def attach(self, el, singlet):
        if not el.numbonds:
            return (None, "%s makes no bonds; can't attach one to an open bond" % el.name)
        spot = self.findSpot(el, singlet)
        pl = []
        rl = [] # real neighbors of singlets in pl [for bug 232 fix]
        mol = singlet.molecule
        cr = el.rcovalent

        for s in mol.nearSinglets(spot, cr*1.5):
            #bruce 041203 quick fix for bug 232:
            # don't include two singlets on the same real atom!
            # (This is not ideal -- we should pick the best one to keep,
            #  not just the first one. How should we decide which is best?? #e)
            real = s.singlet_neighbor()
            if real not in rl:
                pl += [(s, self.findSpot(el, s))]
                rl += [real]
            elif platform.atom_debug:
                print "fyi (ATOM_DEBUG): depositMode.attach refrained from causing bug232 by bonding twice to %r" % real

        n = min(el.numbonds, len(pl))
        if n == 1:
            a = self.bond1(el, singlet, spot)
        elif n == 2:
            a = self.bond2(el,pl)
        elif n == 3:
            a = self.bond3(el,pl)
        elif n == 4:
            a = self.bond4(el,pl)
        else:
            print "too many bonds!", el.numbonds, len(pl)
            a = None
        if a != None:
            desc = "%r (in %r)" % (a, a.molecule.name)
            #e what if caller renames a.molecule??
            if n > 1:
                desc += " (%d bonds made)" % n
        else:
            desc = "bug: too many (%d) bonds to make!" % n
        mol.shakedown()
        self.o.paintGL() ##e probably should be moved to caller
        return a, desc

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
        if len(el.quats): #bruce 041119 revised to support "onebond" elements
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
        return a #bruce 041123
        
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
        return a #bruce 041123

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
        return a #bruce 041123

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
        return a #bruce 041123

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
        "called from radiobutton presses and spinbox changes"
        self.w.pasteP = True
        self.w.depositAtomDashboard.pasteRB.setOn(True)
        cx = self.w.pasteComboBox.currentItem()
        if self.o.assy.shelf.members:
            try:
                self.pastable = self.o.assy.shelf.members[-1-cx]
                # bruce 041124 - changed [cx] to [-1-cx] (should just fix model tree)
                # bruce 041124: the following status bar message (by me)
                # is a good idea, but first we need to figure out how to
                # remove it from the statusbar when it's no longer
                # accurate!
                #
                ## self.w.msgbarLabel.setText("Ready to paste %r" % self.pastable.name)
            except: # IndexError (or its name is messed up)
                # should never happen, but be robust [bruce 041124]
                self.pastable = None
        else:
            self.pastable = None # bruce 041124
        # bruce 041124 adding more -- I think it's needed to fully fix bug 169:
        # update clipboard selection status to match the spinbox,
        # but prevent it from recursing into our spinbox updater
        self.dont_update_gui = 1
        try:
            self.o.assy.shelf.unpick()
            if self.pastable:
                self.pastable.pick()
        finally:
            self.dont_update_gui = 0
            self.o.assy.mt.update() # update model tree
        return
        
    def setAtom(self):
        "called from radiobutton presses and spinbox changes"
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
        # revised 041124 to fix bug 169, by mark and then by bruce
        """if called on a singlet, make that singlet the hotspot for
        the molecule.  (if there's only one, it's automatically the
        hotspot)
        """
        if self.o.selatom and self.o.selatom.element == Singlet:
            self.o.selatom.molecule.hotspot = self.o.selatom
            new = self.o.selatom.molecule.copy(None) # None means no assembly
            new.move(-new.center)
            self.o.assy.shelf.setopen() #bruce 041124 change: open clipboard
            # bruce 041124 change: add new after the other members, not before,
            # so the order will (at least sometimes) match what's in the spinbox.
            # (addmember adds it at the beginning by default, I think, though it
            # appends it to the list, because the list order is reversed from
            # what's displayed in the model tree, evidently. If that's a bug and
            # is fixed, then this code will be wrong and will need revision.)
            if self.o.assy.shelf.members:
                self.o.assy.shelf.members[0].addmember(new)
                # [0] is last item, since members are shown in reverse, evidently
            else:
                self.o.assy.shelf.addmember(new) # old code; adds at beginning
            self.o.assy.shelf.unpick()
            new.pick()
            self.w.pasteP = True
            self.UpdateDashboard() # (probably also called by new.pick())
            self.w.update()
        return

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
            print 'externs', m.externs
            for a in m.atlist:
                print a
                for b in a.bonds:
                    print '   ', b

    pass # end of class depositMode
