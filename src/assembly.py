# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

"""
assembly.py -- provides class assembly, a set of molecules
(plus selection state) to be shown in one glpane.

$Id$
"""
from Numeric import *
from VQT import *
from string import *
import re
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from struct import unpack

from drawer import drawsphere, drawcylinder, drawline, drawaxes
from drawer import segstart, drawsegment, segend, drawwirecube
from shape import *
from chem import *
from movie import *
from gadgets import *
from Utility import *

# number of atoms for detail level 0
HUGE_MODEL = 20000
# number of atoms for detail level 1
LARGE_MODEL = 5000

def hashAtomPos(pos):
        return int(dot(V(1000000, 1000,1),floor(pos*1.2)))

# the class for groups of parts (molecules)
# currently only one level, but should be recursive
class assembly:
    def __init__(self, win, nm = None):
        # ignore changes to this assembly during __init__;
        # this will be set back to 0 at the end of __init__:
        self._modified = 1 
        
        # nothing is done with this now, but should have a
        # control for browsing/managing the list
        global assyList
        assyList += [self]
        # the MWsemantics displaying this assembly. 
        self.w = win
        # self.mt = win.modelTreeView
        # self.o = win.glpane
        #  ... done in MWsemantics to avoid a circularity
        
        # the name if any
        self.name = nm or gensym("Assembly")
        # all the Nodes in the assembly registered here
        self.dict = {}
        
        # the coordinate system (Actually default view)
        self.csys = Csys(self, "CSys", 10.0, 0.0, 1.0, 0.0, 0.0)
        self.xy = Datum(self, "XY", "plane", V(0,0,0), V(0,0,1))
        self.yz = Datum(self, "YZ", "plane", V(0,0,0), V(1,0,0))
        self.zx = Datum(self, "ZX", "plane", V(0,0,0), V(0,1,0))
        grpl1=[self.csys, self.xy, self.yz, self.zx]
        self.data=Group("Data", self, None, grpl1)
        self.data.open=False

        self.shelf = Group("Clipboard", self, None, [])
        self.shelf.open = False

        # the model tree for this assembly
        self.tree = Group(self.name, self, None)
        self.root = Group("ROOT", self, None, [self.tree, self.shelf])
        # list of chem.molecule's
        self.molecules=[]
        # list of the atoms, only valid just after read or write
        self.alist = [] #None
        # filename if this was read from a file
        self.filename = ""
        # to be shrunk, see addmol
        self.bbox = BBox()
        self.center=V(0,0,0)
        # dictionary of selected atoms (indexed by atom.key)
        self.selatoms={}
        # list of selected molecules
        self.selmols=[]
        # what to select: 0=atoms, 2 = molecules
        self.selwhat = 2
        # level of detail to draw
        self.drawLevel = 2
        # currently unimplemented
        self.selmotors=[]
        self.undolist=[]
        # 1 if there is a structural difference between assy and file
        self._modified = 0 # note: this was set to 1 at start of __init__
        # the Movie object.
        self.m=Movie(self)
        
        ### Some information needed for the simulation or coming from mmp file
        self.temperature = 300
        self.waals = None

        return # from assembly.__init__

    def has_changed(self): # bruce 050107
        """Report whether this assembly (or something it contains)
        has been changed since it was last saved or loaded from a file.
        See self.changed() docstring and comments for more info.
        Don't use or set self._modified directly!
           #e We might also make this method query the current mode
        to see if it has changes which ought to be put into this assembly
        before it's saved.
        """
        return self._modified
    
    def changed(self): # bruce 050107
        """Record the fact that this assembly (or something it contains)
        has been changed, in the sense that saving it into a file would
        produce meaningfully different file contents than if that had been
        done before the change.
           Note that some state changes (such as selecting chunks or atoms)
        affect some observers (like the glpane or model tree), but not what
        would be saved into a file; such changes should *not* cause calls to
        this method (though in the future there might be other methods for
        them to call, e.g. perhaps self.changed_selection() #e).
           [Note: as of 050107, it's unlikely that this is called everywhere
        it needs to be. It's called in exactly the same places where the
        prior code set self.modified = 1. In the future, this will be called
        from lower-level methods than it is now, making complete coverage
        easier. #e]
        """
        # bruce 050107 added this method; as of now, all method names (in all
        # classes) of the form 'changed' or 'changed_xxx' (for any xxx) are
        # hereby reserved for this purpose! [For beta, I plan to put in a
        # uniform system for efficiently recording and propogating change-
        # notices of that kind, as part of implementing Undo (among other uses).]
        if not self._modified:
            self._modified = 1
            # Feel free to add more side effects here, inside this 'if'
            # statement, even if they are slow! They will only run the first
            # time you modify this assembly, since its _modified flag was most
            # recently reset [i.e. since it was saved].
            # [For Beta, they might run more often (once per undoable user-
            #  event), so we'll review them for speed at that time. For now,
            #  only saving this assembly to file (or loading or clearing it)
            #  is permitted to reset this flag to 0.]
            
            # The part changed.  The movie, if it exists, is not longer valid.
            # Not true.  If the user has changed a display mode on a check or atom
            # this gets called.
            if self.m.isOpen: 
                print "assembly.changed(): closeing moviefile =",self.m.filename
                self.m.fileobj.close()
                self.m.isOpen = False
            self.m.IsValid = False # Need to ask Bruce how to do this properly.
            
            self.w.history.message("(fyi: part now has unsaved changes)") #e revise terminology?
            pass
        # If you think you need to add a side-effect *here* (which runs every
        # time this method is called, not just the first time after each save),
        # that would probably be too slow -- we'll need to figure out a different
        # way to get the same effect (like recording a "modtime" or "event counter").
        return

    def reset_changed(self): # bruce 050107
        """[private method] #doc this... see self.changed() docstring.
        """
        self._modified = 0
    
    def selectingWhat(self):
        """return 'Atoms' or 'Molecules' to indicate what is currently
        being selected [by bruce 040927; might change]
        """
        # bruce 040927: this seems to be wrong sometimes,
        # e.g. when no atoms or molecules exist in the assembly... not sure.
        return {0: "Atoms", 2: "Molecules"}[self.selwhat]

    def checkpicked(self, always_print = 0):
        """check whether every atom and molecule has its .picked attribute
        set correctly. Fix errors, too. [bruce 040929]
        """
        if always_print: print "fyi: checkpicked()..."
        self.checkpicked_atoms(always_print = 0)
        self.checkpicked_mols(always_print = 0)
        # maybe do in order depending on selwhat, right one first?? probably doesn't matter.
        #e we ought to call this really often and see when it prints something,
        # so we know what causes the selection bugs i keep hitting.
        # for now see menu1 in select mode (if i committed my debug hacks in there)
        
    def checkpicked_mols(self, always_print = 1):
        "checkpicked, just for molecules [bruce 040929]"
        if always_print: print "fyi: checkpicked_mols()..."
        for mol in self.molecules:
            wantpicked = (mol in self.selmols)
            if mol.picked != wantpicked:
                print "mol %r.picked was %r, should be %r (fixing)" % (mol, mol.picked, wantpicked)
                mol.picked = wantpicked
        return

    def checkpicked_atoms(self, always_print = 1):
        "checkpicked, just for atoms [bruce 040929]"
        if always_print: print "fyi: checkpicked_atoms()..."
        lastmol = None
        for mol in self.molecules:
            for atom in mol.atoms.values(): ##k
                wantpicked = (atom.key in self.selatoms) ##k
                if atom.picked != wantpicked:
                    if mol != lastmol:
                        lastmol = mol
                        print "in mol %r:" % mol
                    print "atom %r.picked was %r, should be %r (fixing)" % (atom, atom.picked, wantpicked)
                    atom.picked = wantpicked
        return
    
    # convert absolute atom positions to relative, find
    # bounding boxes, do some housekeeping

    def addmol(self,mol):
        """(Public method:)
        Add a chunk to this assembly.
        Merge bboxes and update our drawlevel
        (though there is no guarantee that mol's bbox and/or number of atoms
        won't change again during the same user-event that's running now;
        some code might add mol when it has no atoms, then add atoms to it).
        """
        self.changed() #bruce 041118
        self.bbox.merge(mol.bbox)
        self.center = self.bbox.center()
        self.molecules += [mol]
        self.tree.addmember(mol)
   
        self.setDrawLevel()
        
    ## Calculate the number of atoms in an assembly, which is used to
    ## control the detail level of sphere subdivision
    def setDrawLevel(self):

        num = 0
        for mol in self.molecules:
	    num += len(mol.atoms)
        self.drawLevel = 2
        if num > LARGE_MODEL: self.drawLevel = 1
        if num > HUGE_MODEL: self.drawLevel = 0


    # to draw, just draw everything inside
    def draw(self, win):
        self.tree.draw(self.o, self.o.display)
    
    # make a new molecule using a cookie-cut shape
    def molmake(self,shap):
        self.changed() # The file and the part are now out of sync.
        mol = molecule(self, gensym("Cookie."))
        ndx={}
        hashAtomPos 
        bbhi, bblo = shap.bbox.data
        # Widen the grid enough to get bonds that cross the box
        griderator = genDiam(bblo-1.6, bbhi+1.6)
        pp=griderator.next()
        while (pp):
            pp0 = pp1 = None
            if shap.isin(pp[0]):
                pp0h = hashAtomPos(pp[0])
                if pp0h not in ndx:
                    pp0 = atom("C", pp[0], mol)
                    ndx[pp0h] = pp0
                else: pp0 = ndx[pp0h]
            if shap.isin(pp[1]):
                pp1h = hashAtomPos(pp[1])
                if pp1h not in ndx:
                    pp1 = atom("C", pp[1], mol)
                    ndx[pp1h] = pp1
                else: pp1 = ndx[pp1h]
            if pp0 and pp1: mol.bond(pp0, pp1)
            elif pp0:
                x = atom("X", (pp[0] + pp[1]) / 2.0, mol)
                mol.bond(pp0, x)
            elif pp1:
                x = atom("X", (pp[0] + pp[1]) / 2.0, mol)
                mol.bond(pp1, x)
            pp=griderator.next()

        #Added by huaicai to fixed some bugs for the 0 atoms molecule 09/30/04
        if len(mol.atoms) > 0:  
            self.addmol(mol)
            self.unpickatoms()
            self.unpickparts()
            self.selwhat = 2
            mol.pick()
            self.mt.mt_update()

    def savebasepos(self):
        """Copy current atom positions into an array.
        """
        # save a copy of each chunk's basepos array 
        # (in the chunk itself, why not -- it's the most convenient place)
        for m in self.molecules:
            m._savedbasepos = + m.basepos
            
#        if not self.alist: return
#        for a in self.alist:
#            self.copybasepos = + a.molecule.basepos
            
    def restorebasepos(self):
        """Restore atom positions copied earlier by savebasepos().
        """
        # restore that later (without erasing it, so no need to save it 
        # again right now)
        # (only valid when every molecule is "frozen", i.e. basepos and 
        # curpos are same object):
        for m in self.molecules:
            m.basepos = m.curpos = + m._savedbasepos
        
#        if not self.alist: return
#        for a in self.alist:
#            a.molecule.basepos[a.index] = self.copybasepos[a.index]
        
        for b in self.blist.itervalues():
            b.setup_invalidate()
            
        for m in self.molecules:
            m.changeapp(0)

    def deletebasepos(self):
        """Erase the savedbasepos array.  It takes a lot of room.
        """
        for m in self.molecules:
            del m._savedbasepos
            
    # set up to run a movie or minimization
    def movsetup(self):
        for m in self.molecules:
            m.freeze()
        self.blist = {}
        for a in self.alist:
            for b in a.bonds:
                self.blist[b.key]=b
        pass

    # move the atoms one frame as for movie or minimization
    # .dpb file is in units of 16 pm
    # units here are angstroms
    def movatoms(self, file, addpos = True):
        if not self.alist: return
        ###e bruce 041104 thinks this should first check whether the
        # molecules involved have been updated in an incompatible way
        # (which might change the indices of atoms); otherwise crashes
        # might occur. It might be even worse if a shakedown would run
        # during this replaying! (This is just a guess; I haven't tested
        # it or fully analyzed all related code, or checked whether
        # those dangerous mods are somehow blocked during the replay.)
        for a in self.alist:
            # (assuming mol still frozen, this will change both basepos and
            #  curpos since they are the same object; it won't update or
            #  invalidate other attrs of the mol, however -- ok?? [bruce 041104])
            if addpos: a.molecule.basepos[a.index] += A(unpack('bbb',file.read(3)))*0.01
            else: a.molecule.basepos[a.index] -= A(unpack('bbb',file.read(3)))*0.01
            
            # Debugging code - Mark 050107
#            pt =str(A(a.molecule.basepos[a.index]))
#            msg = "atompos: " + str(a.index) + "," + pt
#            self.w.history.message(msg)
#            print "assembly.movatoms:",msg
            
        for b in self.blist.itervalues():
            b.setup_invalidate()
            
        for m in self.molecules:
            m.changeapp(0)

    # regularize the atoms' new positions after the motion
    def movend(self):
        # terrible hack for singlets in simulator, which treats them as H
        for a in self.alist:
            if a.element==Singlet: a.snuggle()
        for m in self.molecules:
            m.unfreeze()
        self.o.paintGL()


    #########################

            # user interface

    #########################

    # functions from the "Select" menu

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        if self.selwhat:
            for m in self.molecules:
                m.pick()
        else:
            for m in self.molecules:
                for a in m.atoms.itervalues():
                    a.pick()
        self.w.win_update()


    def selectNone(self):
        self.unpickatoms()
        self.unpickparts()
        self.w.win_update()


    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)
        """
        # revised by bruce 041217 after discussion with Josh;
        # previous version inverted selatoms only in chunks with
        # some selected atoms.
        if self.selwhat:
            newpicked = filter( lambda m: not m.picked, self.molecules )
            self.unpickparts()
            for m in newpicked:
                m.pick()
        else:
            for m in self.molecules:
                for a in m.atoms.itervalues():
                    if a.picked: a.unpick()
                    else: a.pick()
        self.w.win_update()

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """
        self.marksingle()
        self.w.win_update()

    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        self.markdouble()
        self.w.win_update()

    def selectAtoms(self):
        self.unpickparts()
        self.selwhat = 0
        self.w.win_update()
            
    def selectParts(self):
        self.pickParts()
        self.w.win_update()

    def pickParts(self):
        self.selwhat = 2
        lis = self.selatoms.values()
        self.unpickatoms()
        if lis:
            for a in lis:
                a.molecule.pick()


    # dumb hack: find which atom the cursor is pointing at by
    # checking every atom...
    # [bruce 041214 comment: findpick is now mostly replaced by findAtomUnderMouse;
    #  its only remaining call is in depositMode.getcoords, which uses a constant
    #  radius other than the atoms' radii, and doesn't use iPic or iInv,
    #  but that too might be replaced in the near future, once bug 269 response
    #  is fully decided upon.
    #  Meanwhile, I'll make this one only notice visible atoms, and clean it up.
    #  BTW it's now the only caller of atom.checkpick().]
    
    def findpick(self, p1, v1, r=None):
        distance = 1000000
        atom = None
        for mol in self.molecules:
            if mol.hidden: continue
            disp = mol.get_dispdef()
            for a in mol.atoms.itervalues():
                if not a.visible(disp): continue
                dist = a.checkpick(p1, v1, disp, r, None)
                if dist:
                    if dist < distance:
                        distance = dist
                        atom = a
        return atom

    # bruce 041214, for fixing bug 235 and some unreported ones:
    def findAtomUnderMouse(self, event, water_cutoff = False, singlet_ok = False):
        """Return the atom (if any) whose front surface should be visible at the
        position of the given mouse event, or None if no atom is drawn there.
        This takes into account all known effects that affect drawing, except
        bonds and other non-atom things, which are treated as invisible.
        (Someday we'll fix this by switching to OpenGL-based hit-detection. #e)
           Note: if several atoms are drawn there, the correct one to return is
        the one that obscures the others at that exact point, which is not always
        the one whose center is closest to the screen!
           When water_cutoff is true, also return None if the atom you would
        otherwise return (more precisely, if the place its surface is touched by
        the mouse) is under the "water surface".
           Normally never return a singlet (though it does prevent returning
        whatever is behind it). Optional arg singlet_ok permits returning one.
        """
        p1, p2 = self.o.mousepoints(event, 0.0)
        z = norm(p1-p2)
        x = cross(self.o.up,z)
        y = cross(z,x)
        matrix = transpose(V(x,y,z))
        point = p2
        cutoffs = dot( A([p1,p2]) - point, matrix)[:,2]
        near_cutoff = cutoffs[0]
        if water_cutoff:
            far_cutoff = cutoffs[1]
            # note: this can be 0.0, which is false, so an expression like
            # (water_cutoff and cutoffs[1] or None) doesn't work!
        else:
            far_cutoff = None
        z_atom_pairs = []
        for mol in self.molecules:
            if mol.hidden: continue
            pairs = mol.findAtomUnderMouse(point, matrix, \
                far_cutoff = far_cutoff, near_cutoff = near_cutoff )
            z_atom_pairs.extend( pairs)
        if not z_atom_pairs:
            return None
        z_atom_pairs.sort() # smallest z == farthest first; we want nearest
        res = z_atom_pairs[-1][1] # nearest hit atom
        if res.element == Singlet and not singlet_ok:
            return None
        return res

    #bruce 041214 renamed and rewrote the following pick_event methods, as part of
    # fixing bug 235 (and perhaps some unreported bugs).
    # I renamed them to distinguish them from the many other "pick" (etc) methods
    # for Node subclasses, with common semantics different than these have.
    # I removed some no-longer-used related methods.
    
    def pick_at_event(self, event): #renamed from pick; modified
        """Make whatever visible atom or chunk (depending on self.selwhat)
        is under the mouse at event get selected,
        in addition to whatever already was selected.
        You are not allowed to select a singlet.
        Print a message about what you just selected (if it was an atom).
        """
        # [bruce 041227 moved the getinfo status messages here, from the atom
        # and molecule pick methods, since doing them there was too verbose
        # when many items were selected at the same time. Original message
        # code was by [mark 2004-10-14].]
        atm = self.findAtomUnderMouse(event)
        if atm:
            if self.selwhat:
                if not self.selmols:
                    self.selmols = []
                    # bruce 041214 added that, since pickpart used to do it and
                    # calls of that now come here; in theory it's never needed.
                atm.molecule.pick()
                self.w.history.message(atm.molecule.getinfo())
            else:
                atm.pick()
                self.w.history.message(atm.getinfo())
        return
    
    def onlypick_at_event(self, event): #renamed from onlypick; modified
        """Unselect everything in the glpane; then select whatever visible atom
        or chunk (depending on self.selwhat) is under the mouse at event.
        If no atom or chunk is under the mouse, nothing in glpane is selected.
        """
        if self.selwhat:
            self.unpickparts()
        else:
            self.unpickatoms()
        self.pick_at_event(event)
    
    def unpick_at_event(self, event): #renamed from unpick; modified
        """Make whatever visible atom or chunk (depending on self.selwhat)
        is under the mouse at event get un-selected,
        but don't change whatever else is selected.
        """
        atm = self.findAtomUnderMouse(event)
        if atm:
            if self.selwhat:
                atm.molecule.unpick()
            else:
                atm.unpick()
        return
                
    # deselect any selected atoms
    def unpickatoms(self):
        if self.selatoms:
            for a in self.selatoms.itervalues():
                # this inlines and optims atom.unpick
                a.picked = 0
                a.molecule.changeapp(1)
            self.selatoms = {}

    # deselect any selected molecules
    def unpickparts(self):
        self.root.unpick()
        self.data.unpick()
        # bruce 041214 comment:
        # note that selected items in the clipboard remain selected (I think)

    # for debugging
    def prin(self):
        for a in self.selatoms.itervalues():
            a.prin()

    def cut(self):
        if self.selwhat==0: return
        new = Group(gensym("Copy"),self,None)
        self.tree.apply2picked(lambda(x): x.moveto(new))
        
        if new.members:
            for ob in (new.members):
                self.shelf.addmember(ob) # add new member(s) to the clipboard
                # if the new member is a molecule, move the center a little.
                if isinstance(ob, molecule): ob.move(-ob.center)
            ob.pick()

        self.changed()
        self.w.win_update()


    # copy any selected parts (molecules)
    #  Revised by Mark to fix bug 213; Mark's code added by bruce 041129.
    #  Bruce's comments (based on reading the code, not all verified by test):
    #    0. If groups are not allowed in the clipboard (bug 213 doesn't say,
    #  but why else would it have been a bug to have added a group there?),
    #  then this is only a partial fix, since if a group is one of the
    #  selected items, apply2picked will run its lambda on it directly.
    #    1. The group 'new' is now seemingly used only to hold
    #  a list; it's never made a real group (I think). So I wonder if this
    #  is now deviating from Josh's intention, since he presumably had some
    #  reason to make a group (rather than just a list).
    #    2. Is it intentional to select only the last item added to the
    #  clipboard? (This will be the topmost selected item, since (at least
    #  for now) the group members are in bottom-to-top order.)
    def copy(self):
        if self.selwhat==0: return
        new = Group(gensym("Copy"),self,None)
        # x is each item in the tree that is picked.
        self.tree.apply2picked(lambda(x): new.addmember(x.copy(new)))
        
        if new.members:
            for ob in (new.members):
                self.shelf.addmember(ob) # add new member(s) to the clipboard
                # if the new member is a molecule, move the center a little.
                if isinstance(ob, molecule): ob.move(-ob.center)
            ob.pick()

        self.w.win_update()

    def paste(self, node):
        pass # to be implemented

    # move any selected parts in space ("move" is an offset vector)
    def movesel(self, move):
        for mol in self.selmols:
            self.changed()
            mol.move(move)
 
 
    # rotate any selected parts in space ("rot" is a quaternion)
    def rotsel(self, rot):
        for mol in self.selmols:
            self.changed()
            mol.rot(rot)
             

    def kill(self): # bruce 041118 simplified this after shakedown changes
        "delete whatever is selected from this assembly"
        if self.selatoms:
            self.changed()
            for a in self.selatoms.values():
                a.kill()
            self.selatoms = {} # should be redundant
        if self.selwhat == 2 or self.selmols:
            self.tree.apply2picked(lambda o: o.kill())

        # Kill anything picked in the clipboard
        
        # [bruce 041129 thinks this was added by Mark (and is needed).
        #  But I think it can be unintended and go unseen if user selected
        #  using glpane, so maybe it should depend on focus and/or on whether
        #  clipboard is open. So for now I think I'll add a check for clipboard
        #  being open, which is a kluge but at least ensures the kill is seen.
        #  A better fix might be for clipboard to have its own focus, distinct
        #  from the main tree/glpane, but that has to wait for the future.
        #  Digression: won't picking atoms unpick anything in the clipboard,
        #  and is this intended (in case it messes up pasting)?]
        
        if self.shelf.open: # condition by bruce 041129
            # [bruce 041220: should we also require event not from glpane,
            #  and nothing selected in glpane?? so nothing but click in mtree
            #  would work... issue is related to click in mtree not unseling in
            #  clipboard, but we need that too, since its sel defines pastable.
            #  This whole thing needs to be rethought even before Alpha... ###@@@]
            self.shelf.apply2picked(lambda o: o.kill()) # kill by Mark(?), 11/04
            
        self.setDrawLevel()


##    # actually remove a given molecule from the list [no longer used]
##    def killmol(self, mol):
##        mol.kill()
##        self.setDrawLevel()


    def Hide(self):
        "Hide all selected chunks"
        if self.selwhat == 2:
            self.tree.apply2picked(lambda x: x.hide())
            self.w.win_update()

    def Unhide(self):
        "Unhide all selected chunks"
        if self.selwhat == 2:
            self.tree.apply2picked(lambda x: x.unhide())
            self.w.win_update()

    #bond atoms (cheap hack)
    def Bond(self):
        if not self.selatoms: return
        aa=self.selatoms.values()
        if len(aa)==2:
            self.changed()
            aa[0].molecule.bond(aa[0], aa[1])
            #bruce 041028 bugfix: bring following lines inside the 'if'
            aa[0].molecule.changeapp(0)
            aa[1].molecule.changeapp(0)
            self.o.paintGL()

    #unbond atoms (cheap hack)
    def Unbond(self):
        if not self.selatoms: return
        self.changed()
        aa=self.selatoms.values()
        if len(aa)==2:
            #bruce 041028 bugfix: add [:] to copy following lists,
            # since bust will modify them during the iteration
            for b1 in aa[0].bonds[:]:
                for b2 in aa[1].bonds[:]:
                    if b1 == b2: b1.bust()
        self.o.paintGL()

    #stretch a molecule
    def Stretch(self):
        self.changed()
        if not self.selmols: return
        for m in self.selmols:
            m.stretch(1.1)
        self.o.paintGL()

    #weld selected molecules together
    def weld(self):
        if len(self.selmols) < 2: return
        mol = self.selmols[0]
        for m in self.selmols[1:]:
            mol.merge(m)


    def align(self):
        if len(self.selmols) < 2: return
        ax = V(0,0,0)
        for m in self.selmols:
            ax += m.getaxis()
        ax = norm(ax)
        for m in self.selmols:
            m.rot(Q(m.getaxis(),ax))
        self.o.paintGL()
                  

    #############

    def __str__(self):
        return "<Assembly of " + self.filename + ">"

    def computeBoundingBox(self):
        """Compute the bounding box for the assembly. This should be
        called whenever the geomety model has been changed, like new
        parts added, parts/atoms deleted, parts moved/rotated(not view
        move/rotation), etc."""
        
        self.bbox = BBox()
        for mol in self.molecules:
              self.bbox.merge(mol.bbox)
        self.center = self.bbox.center()
        
    # makes a simulation movie
    def makeSimMovie(self):
        self.simcntl = runSim(self) # Open SimSetup dialog
        if self.m.cancelled: return -1 # user hit Cancel button in SimSetup Dialog.
        r = self.writemovie()
        # Movie created.  Initialize.
        if not r: 
            self.m.IsValid = True # Movie is valid.
            self.m.currentFrame = 0
        return r

    # makes a minimize movie
    def makeMinMovie(self):
        r = self.writemovie(1)
        # Minimization worked.  Start the movie.
        if not r: 
            self.w.history.message("Minimizing...")
            self.m.currentFrame = 0
            self.m._setup()
            self.m._play()
            self.m._close()

        return
        
    # makes a motor connected to the selected atoms
    # note I don't check for a limit of 25 atoms, but any more
    # will choke the file parser in the simulator
    def makeRotaryMotor(self, sightline):
        if not self.selatoms: return
        m=RotaryMotor(self)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Rotary Motory Dialog.
            del(m)
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()
      
    # makes a Linear Motor connected to the selected atoms
    # note I don't check for a limit of 25 atoms, but any more
    # will choke the file parser in the simulator
    def makeLinearMotor(self, sightline):
        if not self.selatoms: return
        m = LinearMotor(self)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Linear Motory Dialog.
            del(m)
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()

    # makes all the selected atoms grounded
    # same note as above
    def makeground(self):
        if not self.selatoms: return
        m=Ground(self, self.selatoms.values())
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()
        
    # sets the temp of all the selected atoms
    # same note as above
    def makestat(self):
        if not self.selatoms: return
        m=Stat(self, self.selatoms.values())
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()

    # select all atoms connected by a sequence of bonds to
    # an already selected one
    def marksingle(self):
        for a in self.selatoms.values():
            self.conncomp(a, 1)

    # connected components. DFS is elegant!
    # This is called with go=1 from eached already picked atom
    # its only problem is relatively limited stack in Python
    def conncomp(self, atom, go=0):
        if go or not atom.picked:
            atom.pick()
            for a in atom.neighbors(): self.conncomp(a)

    # select all atoms connected by two disjoint sequences of bonds to
    # an already selected one. This picks stiff components but doesn't
    # cross single-bond or single-atom bearings or hinges
    # does select e.g. hydrogens connected to the component and nothing else
    def markdouble(self):
        self.father= {}
        self.stack = []
        self.out = []
        self.dfi={}
        self.p={}
        self.i=0
        for a in self.selatoms.values():
            if a not in self.dfi:
                self.father[a]=None
                self.blocks(a)
        for (a1,a2) in self.out[-1]:
            a1.pick()
            a2.pick()
        for mol in self.molecules:
            for a in mol.atoms.values():
                if len(a.bonds) == 1 and a.neighbors()[0].picked:
                    a.pick()

    # compared to that, the doubly-connected components algo is hairy.
    # cf Gibbons: Algorithmic Graph Theory, Cambridge 1985
    def blocks(self, atom):
        self.dfi[atom]=self.i
        self.p[atom] = self.i
        self.i += 1
        for a2 in atom.neighbors():
            if atom.key < a2.key: pair = (atom, a2)
            else: pair = (a2, atom)
            if not pair in self.stack: self.stack += [pair]
            if a2 in self.dfi:
                if a2 != self.father[atom]:
                    self.p[atom] = min(self.p[atom], self.dfi[a2])
            else:
                self.father[a2] = atom
                self.blocks(a2)
                if self.p[a2] >= self.dfi[atom]:
                    pop = self.stack.index(pair)
                    self.out += [self.stack[pop:]]
                    self.stack = self.stack[:pop]
                self.p[atom] = min(self.p[atom], self.p[a2])

    # separate selected atoms into a new molecule
    # (one new mol for each existing one containing any selected atoms)
    # do not break bonds
    def modifySeparate(self, new_old_callback = None):
        """For each molecule (named N) containing any selected atoms,
           move the selected atoms out of N (but without breaking any bonds)
           into a new molecule which we name N-frag.
           If N is now empty, remove it.
           If new_old_callback is provided, then each time we create a new
           (and nonempty) fragment N-frag, call new_old_callback with the
           2 args N-frag and N (that is, with the new and old molecules).
           Warning: we pass the old mol N to that callback,
           even if it has no atoms and we deleted it from this assembly.
        """
        # bruce 040929 wrote or revised docstring, added new_old_callback feature
        # for use from Extrude.
        # Note that this is called both from a tool button and for internal uses.
        # bruce 041222 removed side effect on selection mode, after discussion
        # with Mark and Josh. Also added some status messages.
        # Questions: is it good to refrain from merging all moved atoms into one
        # new mol? If not, then if N becomes empty, should we rename N-frag to N?
        
        if not self.selatoms: # optimization, and different status msg
            msg = "Separate: no atoms selected"
            self.w.history.message(msg)
            return
        numolist=[]
        for mol in self.molecules[:]: # new mols are added during the loop!
            numol = molecule(self, gensym(mol.name + "-frag"))
            for a in mol.atoms.values():
                if a.picked:
                    # leave the moved atoms picked, so still visible
                    a.hopmol(numol)
            if numol.atoms:
                self.addmol(numol)
                numolist+=[numol]
                if new_old_callback:
                    new_old_callback(numol, mol) # new feature 040929
        from platform import fix_plurals
        msg = fix_plurals("Separate created %d new chunk(s)" % len(numolist))
        self.w.history.message(msg)
        self.w.win_update() #e do this in callers instead?

    def copySelatomFrags(self):
        #bruce 041116, combining modifySeparate and mol.copy; for extrude
        """
           For each molecule (named N) containing any selected atoms,
           copy the selected atoms of N to make a new molecule named N-frag
           (which is not added to the assembly, self). The old mol N is unchanged.
           The copy is done as if by molecule.copy (with cauterize = 1),
           except that all bonds between selected atoms are copied, even if not in same mol.
           Return a list of pairs of new and old molecules [(N1-frag,N1),...].
           (#e Should we optionally return a list of pairs of new and old atoms, too?
           And one of new bonds or singlets and old external atoms, or the equiv?)
        """
        oldmols = {}
        for a in self.selatoms.values():
            m = a.molecule
            oldmols[id(m)] = m ###k could we use key of just m, instead??
        newmols = {}
        for old in oldmols.values():
            numol = molecule(self, gensym(mol.name + "-frag"))
            newmols[id(old)] = numol # same keys as in oldmols
        nuats = {}
        for a in self.selatoms.values():
            old = a.molecule
            numol = newmols[id(old)]
            a.info = id(a) # lets copied atoms correspond (useful??)
            nuat = a.copy() # uses new copy method as of bruce 041116
            numol.addatom(nuat)
            nuats[id(a)] = nuat
        extern_atoms_bonds = []
        for a in self.selatoms.values():
            assert a.picked
            for b in a.bonds:
                a2 = b.other(a)
                if a2.picked:
                    # copy the bond (even if it's a mol-mol bond), but only once per bond
                    if id(a) < id(a2):
                        bond_atoms(nuats[id(a)], nuats[id(a2)])
                else:
                    # make a singlet instead of this bond (when we're done)
                    extern_atoms_bonds.append( (a,b) ) # ok if several times for one 'a'
                    #e in future, might keep more info
        for a,b in extern_atoms_bonds:
            # compare to code in Bond.unbond(): ###e make common code
            nuat = nuats[id(a)]
            x = atom('X', + b.ubp(a), nuat.molecule)
            bond_atoms(nuat, x)
        res = []
        for old in oldmols.values():
            new = newmols[id(old)]
            res.append( (new,old) )
        return res
        

    # change surface atom types to eliminate dangling bonds
    # a kludgey hack
    # bruce 041215 added some comments.
    def modifyPassivate(self):
        if self.selwhat == 2:
            for m in self.selmols:
                m.Passivate(True) # arg True makes it work on all atoms in m
        else:
            for m in self.molecules:
                m.Passivate() # lack of arg makes it work on only selected atoms
                # (maybe it could just iterate over selatoms... #e)
                
        self.changed() # could be much smarter
        self.o.paintGL()

    # add hydrogen atoms to each dangling bond
    def modifyHydrogenate(self):
        self.o.mode.modifyHydrogenate()
        
    # remove hydrogen atoms from every selected atom/molecule
    def modifyDehydrogenate(self):
        self.o.mode.modifyDehydrogenate()

    # write moviefile
    def writemovie(self, mflag = 0):
        from fileIO import writemovie
        return writemovie(self, mflag)
            
    # end of class assembly