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
from HistoryWidget import greenmsg, redmsg
from platform import fix_plurals


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
        self.homeCsys = Csys(self, "HomeView", 10.0, V(0,0,0), 1.0, 0.0, 1.0, 0.0, 0.0)
        self.lastCsys = Csys(self, "LastView", 10.0, V(0,0,0), 1.0, 0.0, 1.0, 0.0, 0.0) 
        self.xy = Datum(self, "XY", "plane", V(0,0,0), V(0,0,1))
        self.yz = Datum(self, "YZ", "plane", V(0,0,0), V(1,0,0))
        self.zx = Datum(self, "ZX", "plane", V(0,0,0), V(0,1,0))
        grpl1=[self.homeCsys, self.lastCsys, self.xy, self.yz, self.zx]
        self.data=Group("Data", self, None, grpl1)
        self.data.open=False

        self.shelf = Group("Clipboard", self, None, [])
        self.shelf.open = False

        # the model tree for this assembly
        self.tree = Group(self.name, self, None)
        self.root = Group("ROOT", self, None, [self.tree, self.shelf])

        # bruce 050131 for Alpha:
        # For each assembly, maintain one Node or Group which is the
        # "current selection group" (the PartGroup or one of the
        # clipboard items), in which all selection is required to reside.
        #    It might sometimes be an out-of-date node, either a
        # former shelf item or a node from a previously loaded file --
        # not sure if these can happen, but "user beware".
        #    Sometime after Alpha, we'll show this group in the glpane
        # and let operations (which now look at self.tree or self.molecules)
        # affect it instead of affecting the main model
        # (or having bugs whenever clipboard items are selected, as they
        # often do now).
        self.current_selection_group = None

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

        #bruce 050131 for Alpha:
        from Utility import kluge_patch_assy_toplevel_groups
        kluge_patch_assy_toplevel_groups( self)

        # level of detail to draw
        self.drawLevel = 2
        # currently unimplemented
        self.selmotors=[]
        self.undolist=[]
        # 1 if there is a structural difference between assy and file
        self._modified = 0 # note: this was set to 1 at start of __init__
        # the Movie object.
        self.m=Movie(self)
        # movie ID, for future use.
        self.movieID=0
        # ppa = previous picked atoms.
        self.ppa2 = self.ppa3 = None
        
        # the current version of the MMP file format
        # this is set in fileIO.writemmp. Mark 050130
        self.mmpformat = ''
        
        ### Some information needed for the simulation or coming from mmp file
        self.temperature = 300
        self.waals = None

        return # from assembly.__init__
    
    def set_current_selection_group(self, node): #bruce 050131 for Alpha
        prior = self.current_selection_group
        self.current_selection_group = node
##        if platform.atom_debug:
##            print "atom_debug: set_current_selection_group(): from %r to %r" % (node_name(prior),node_name(node))
        if self.is_nonstd_selection_group(node) and not self.is_nonstd_selection_group(prior):
            try:
                msgfunc = self.w.history.message
                # decided to be conservative for now, even though this might be pretty common
                # and I'm tempted to use transient_msg so as to not mess up the history
                ## msgfunc = self.w.history.transient_msg
            except:
                pass # too early?
            else:
                msg = "Warning (alpha): some operations don't work or have bugs for selected clipboard items"
                msgfunc(redmsg(msg)) # don't use redmsg if we change to transient_msg above
        if prior != node:
            self.current_selection_group_changed( prior)
        return

    def current_selection_group_changed(self, prior = 0): #bruce 050131 for Alpha
        "#doc; prior == 0 means unknown -- caller might pass None"
        #e in future (post-Alpha) this might revise self.molecules, what to show in glpane, etc
        # for now, make sure nothing outside it is picked!
        didany = self.root.unpick_all_except( self.current_selection_group )
        if didany:
            try: # precaution against new bugs in this alpha-bug-mitigation code
                # what did we deselect?
                if prior and not isinstance(prior, Group):
                    what = node_name(prior)
                elif prior:
                    what = "some items in " + node_name(prior)
                else:
                    what = "some items"
                ## why = "since selection should not involve more than one clipboard item or part at a time" #e wording??
                why = "to limit selection to one clipboard item or the part" #e wording??
                    #e could make this more specific depending on which selection groups were involved
                msg = "Warning: deselected %s, %s" % (what, why)
            except:
                if platform.atom_debug:
                    raise 
                msg = "Warning: deselected some previously selected items"
            try:
                self.w.history.message( redmsg( msg))
            except:
                pass # too early? (can this happen?)
        pass

    def is_nonstd_selection_group(self, node):
        return node and node != self.tree

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
            
            self.w.history.message("(fyi: part now has unsaved changes)") #e revise terminology?
            
            # Regenerate the movie ID.
            # This will probably not make Alpha.  It is intended to be used in the future
            # as a way to validate movie files.  assy.movieID is handed off to the simulator
            # as an argument (-b) where it writes the number in the movie (.dpb) file header.
            # (see writemovie() in fileIO.py.)
            # The number is then compared to assy.movieID when the movie file is opened
            # at a later time. This check will be done in movie._checkMovieFile().
            # Mark - 050116
            import random
            self.movieID = random.randint(0,4000000000) # 4B is good enough
            
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

# bruce 050201: this is not currently used. If confirmed, zap it in a few days.
##    def selectingWhat(self):
##        """return 'Atoms' or 'Molecules' to indicate what is currently
##        being selected [by bruce 040927; might change]
##        """
##        # bruce 040927: this seems to be wrong sometimes,
##        # e.g. when no atoms or molecules exist in the assembly... not sure.
##        return {0: "Atoms", 2: "Molecules"}[self.selwhat]

    def checkpicked(self, always_print = 0):
        """check whether every atom and molecule has its .picked attribute
        set correctly. Fix errors, too. [bruce 040929]
        Note that this only checks molecules in assy.tree, not assy.shelf,
        since self.molecules only includes those. [bruce 050201 comment]
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
        self.bbox.merge(mol.bbox) # [see also computeBoundingBox -- bruce 050202 comment]
        self.center = self.bbox.center()
        self.molecules += [mol]
        self.tree.addmember(mol)
            #bruce 050202 comment: if you don't want this location for the added mol,
            # just call mol.moveto when you're done, like fileIO does.
            # (Not suitable for mols *already in a group* being added to tree as a whole... ####e) #####@@@@@
   
        self.setDrawLevel()

    #bruce 050202 for Alpha: help fix things up after a DND move in/out of assy.tree.
    def update_mols(self):
        """[Semi-private method]
        Caller is telling us that it might have moved molecules
        into or out of assy.tree (assy == self)
        without properly updating assy.molecules list (which causes lots of bugs if not fixed),
        or (less important but still matters) our bbox, center, or drawLevel.
           Rather than not tolerating such callers (for Alpha),
        just thank them for the info and take the time now to fix things up
        by rescanning assy.tree and remaking assy.molecules (etc) from scratch.
           See also sanitize_for_clipboard, related but sort of an inverse,
        perhaps not needed as much if this is called enough.
           Note: neither this method nor sanitize_for_clipboard (which do need to be merged,
        see also changed_dad which needs to help them know how much needs doing and/or help do it)
        yet does enough. E.g. see bug 371 about bonds between main model and clipboard items.
        """
        self.molecules = 333 # not a sequence - detect bug of touching or using this during this method
        seen = {} # values will be new list of mols
        def func(n):
            "run this exactly once on all molecules that properly belong in this assy"
            if isinstance(n, molecule):
                # check for duplicates (mol at two places in tree) using a dict, whose values accumulate our mols list
                if seen.get(id(n)):
                    print "bug: some chunk occurs twice in assy.tree; semi-tolerated but not fixed"
                    return # from local func only, not from update_mols!
                seen[id(n)] = n
            return # from func only
        self.tree.apply2all( func)
        self.molecules = seen.values()
        self.setDrawLevel()
        self.computeBoundingBox()
        return
        
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
            
    def restorebasepos(self):
        """Restore atom positions copied earlier by savebasepos().
        """
        # restore that later (without erasing it, so no need to save it 
        # again right now)
        # (only valid when every molecule is "frozen", i.e. basepos and 
        # curpos are same object):
        for m in self.molecules:
            m.basepos = m.curpos = + m._savedbasepos

        for b in self.blist.itervalues():
            b.setup_invalidate()
            
        for m in self.molecules:
            m.changeapp(0)

    def deletebasepos(self):
        """Erase the savedbasepos array.  It takes a lot of room.
        """
#        if not self.molecules._savedbasepos:
#            print "assembly.deletebasepos(): NO _SAVEBASEPOS TO DELETE."
#            return
            
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
        self.o.gl_update()


    def moveAtoms(self, newPositions):
        """Huaicai 1/20/05: Move a list of atoms to newPosition. After 
            all atoms moving, bond updated, update display once.
           <parameter>newPosition is a list of atom absolute position, the list order is the same as self.alist """
           
        if len(newPositions) != len(self.alist):
                print "The number of atoms from XYZ file is not matching with that of the current model"
                return
        for a, newPos in zip(self.alist, newPositions):
                a.setposn(A(newPos))
        self.o.gl_update()                


    #########################

            # user interface

    #########################

    # functions from the "Select" menu

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        [bruce 050201 observes that this docstring is wrong.]
        """ ###@@@
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
        if not self.selatoms:
            self.w.history.message(redmsg("Select Connected: No atom(s) selected."))
            return
        
        alreadySelected = len(self.selatoms.values())
        self.marksingle()
        self.w.history.message(greenmsg("Select Connected:"))
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d connected atom(s) selected." % totalSelected)
        
        if totalSelected > alreadySelected: ## Otherwise, that just means no new atoms selected, so no update necessary    
                #self.w.win_update()
                self.o.gl_update()
                

    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        if not self.selatoms:
            self.w.history.message(redmsg("Select Doubly: No atom(s) selected."))
            return
        self.w.history.message(greenmsg("Select Doubly:"))
        
        alreadySelected = len(self.selatoms.values())
        self.markdouble()
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d doubly connected atom(s) selected." % totalSelected)
        
        if totalSelected > alreadySelected: ## otherwise, means nothing new selected. Am I right? ---Huaicai, not analyze the markdouble() algorithm yet 
                #self.w.win_update()
                self.o.gl_update()
        

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
            self.unpickparts() # (fyi, this unpicks in clipboard as well)
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

    def permit_pick_parts(self): #bruce 050125
        "ensure it's legal to pick chunks"
        if not self.selwhat:
            self.unpickatoms()
            self.selwhat = 2
        return
    
    # deselect any selected molecules or groups
    def unpickparts(self):
        self.root.unpick() # root contains self.tree and self.shelf
        self.data.unpick()

    # for debugging
    def prin(self):
        for a in self.selatoms.itervalues():
            a.prin()

    #bruce 050131/050201 for Alpha (really for bug 278 and maybe related ones):
    # sanitize_for_clipboard, for cut and copy and other things that add clipboard items
    # #####@@@@@ need to use in sethotspot too??
    
    def sanitize_for_clipboard(self, ob): 
        """Prepare ob for addition to the clipboard as a new toplevel item;
        should be called just before adding ob to shelf, OR for entire toplevel items already in shelf
        (or both; should be ok, though slower, to call more than once per item).
        NOT SURE IF OK to call when ob still has a dad in its old location.
        (Nor if it ever is thus called, tho i doubt it.)
        """
        self.sanitize_for_clipboard_0( ob) # recursive version handles per-chunk, per-group issues
        #e now do things for the shelf-item as a whole, if any, e.g. fix bug 371 about interspace bonds
        #e 050202: someday, should we do a version of the jig-moving workaround_for_bug_296?
        # that function itself is not reviewed for safety when called from here,
        # but it might be ok, tho better to consolidate its messages into one
        # (as in the "extension of that fix to the clipboard" it now comments about).
        if platform.atom_debug:
            print "atom_debug: fyi: sanitize_for_clipboard sees selgroup of ob is %r" % ob.find_selection_group()
            ###e if this is None, then I'll have an easy way to break bonds from this item to stuff in the main model (bug 371)
            #e i.e. break_wormholes() or break_interspace_bonds()
        return
    
    def sanitize_for_clipboard_0(self, ob): #bruce 050131 for Alpha (really for bug 278 and maybe related ones)
        """[private method:]
        The recursive part of sanitize_for_clipboard:
        keep clipboard items (or chunks inside them) out of assy.molecules,
        so they can't be selected from glpane
        """
        #e should we do ob.unpick_top() as well?
        if ob.assy != self: #bruce 050202, and replaced ob.assy.molecules with self.molecules
            ob.assy = self # for now! in beta this might be its selgroup.
            if platform.atom_debug:
                print "sanitize_for_clipboard_0: node had wrong assy! fixed it:", ob
        if isinstance(ob, molecule):
            if self.selatoms:
                # bruce 050201 for Alpha: worry about selected atoms in chunks in clipboard
                # [no bugs yet reported on this, but maybe it could happen #k]
                #e someday ought to print atom_debug warning if this matters, to find out...
                try:
                    for atm in ob.atoms.values():
                        atm.unpick()
                except:
                    print_compact_traceback("sanitize_for_clipboard_0 ignoring error unpicking atoms: ")
                    pass
            try:
                self.molecules.remove(ob)
                # note: don't center the molecule here -- that's only appropriate
                # for each toplevel cut object as a whole!
            except:
                pass
        elif isinstance(ob, Group): # or any subclass! e.g. the Clipboard itself (deprecated to call this on that tho).
            for m in ob.members:
                self.sanitize_for_clipboard_0(m)
        return

    # bruce 050131/050201 revised these Cut and Copy methods to fix some Alpha bugs;
    # they need further review after Alpha, and probably could use some merging. ###@@@
    # See also assy.kill (Delete operation).
    
    def cut(self):
        self.w.history.message(greenmsg("Cut:"))
        if self.selatoms:
            #bruce 050201-bug370 (2nd commit here, similar issue to bug 370):
            # changed condition to not use selwhat, since jigs can be selected even in Select Atoms mode
            self.w.history.message(redmsg("Cutting selected atoms is not yet supported.")) #bruce 050201
            ## return #bruce 050201-bug370: don't return yet, in case some jigs were selected too.
            # note: we will check selatoms again, below, to know whether we emitted this message
        new = Group(gensym("Copy"),self,None)
            # bruce 050201 comment: this group is usually, but not always, used only for its members list
        if self.tree.picked:
            #bruce 050201 to fix catchall bug 360's "Additional Comments From ninad@nanorex.com  2005-02-02 00:36":
            # don't let assy.tree itself be cut; if that's requested, just cut all its members instead.
            # (No such restriction will be required for assy.copy, even when it copies entire groups.)
            self.tree.unpick_top()
            ## self.w.history.message(redmsg("Can't cut the entire Part -- cutting its members instead.")) #bruce 050201
            self.w.history.message("Can't cut the entire Part; copying its toplevel Group, cutting its members.") #bruce 050201
            # new code to handle this case [bruce 050201]
            self.tree.apply2picked(lambda(x): x.moveto(new))
            use = new
            use.name = self.tree.name # not copying any other properties of the Group (if it has any)
            new = Group(gensym("Copy"),self,None)
            new.addmember(use)
        else:
            self.tree.apply2picked(lambda(x): x.moveto(new))
            # bruce 050131 inference from recalled bug report:
            # this must fail in some way that addmember handles, or tolerate jigs/groups but shouldn't;
            # one difference is that for chunks it would leave them in assy.molecules whereas copy would not;
            # guess: that last effect (and the .pick we used to do) might be the most likely cause of some bugs --
            # like bug 278! Because findpick (etc) uses assy.molecules. So I fixed this with sanitize_for_clipboard, below.
        
        self.changed() # bruce 050131 resisted temptation to make this conditional on new.members; 050201 moved it earlier
        
        if new.members:
            nshelf_before = len(self.shelf.members) #bruce 050201
            for ob in new.members:
                # bruce 050131 try fixing bug 278 in a limited, conservative way
                # (which won't help the underlying problem in other cases like drag & drop, sorry),
                # based on the theory that chunks remaining in assy.molecules is the problem:
                self.sanitize_for_clipboard(ob)
                self.shelf.addmember(ob) # add new member(s) to the clipboard [incl. Groups, jigs -- won't be pastable]
                # if the new member is a molecule, move it to the center of its space
                if isinstance(ob, molecule): ob.move(-ob.center)
            ## ob.pick() # bruce 050131 removed this
            nshelf_after = len(self.shelf.members) #bruce 050201
            self.w.history.message( fix_plurals("Cut %d item(s)" % (nshelf_after - nshelf_before)) + "." ) #bruce 050201
                ###e fix_plurals can't yet handle "(s)." directly. It needs improvement after Alpha.
        else:
            if not self.selatoms:
                #bruce 050201-bug370: we don't need this if the message for selatoms already went out
                self.w.history.message(redmsg("Nothing to cut.")) #bruce 050201
        
        self.w.win_update()

    # copy any selected parts (molecules) [making a new clipboard item... #doc #k]
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
        self.w.history.message(greenmsg("Copy:"))
        if self.selatoms:
            #bruce 050201-bug370: revised this in same way as for assy.cut (above)
            self.w.history.message(redmsg("Copying selected atoms is not yet supported.")) #bruce 050131
            ## return
        new = Group(gensym("Copy"),self,None)
            # bruce 050201 comment: this group is always (so far) used only for its members list
        # x is each node in the tree that is picked. [bruce 050201 comment: it's ok if self.tree is picked.]
        # [bruce 050131 comments (not changing it in spite of bugs):
        #  the x's might be chunks, jigs, groups... but maybe not all are supported for copy.
        #  In fact, Group.copy returns 0 and Jig.copy returns None, and addmember tolerates that
        #  and does nothing!!
        #  About chunk.copy: it sets numol.assy but doesn't add it to assy,
        #  and it sets numol.dad but doesn't add it to dad's members -- so we do that immediately
        #  in addmember. So we end up with a members list of copied chunks from assy.tree.]
        self.tree.apply2picked(lambda(x): new.addmember(x.copy(new)))

        # unlike for cut, no self.changed() should be needed
        
        if new.members:
            nshelf_before = len(self.shelf.members) #bruce 050201
            for ob in new.members:
                self.sanitize_for_clipboard(ob) # not needed on 050131 but might be needed soon, and harmless
                self.shelf.addmember(ob) # add new member(s) to the clipboard
                #bruce comment 050131: this ignores prior membership in new; tolerable in this case
                # if the new member is a molecule, move it to the center of its space
                if isinstance(ob, molecule): ob.move(-ob.center)
            ## ob.pick() # bruce 050131 removed this
            nshelf_after = len(self.shelf.members) #bruce 050201
            self.w.history.message( fix_plurals("Copied %d item(s)" % (nshelf_after - nshelf_before)) + "." ) #bruce 050201
                ###e fix_plurals can't yet handle "(s)." directly. It needs improvement after Alpha.
        else:
            if not self.selatoms:
                #bruce 050201-bug370: we don't need this if the message for selatoms already went out
                self.w.history.message(redmsg("Nothing to Copy.")) #bruce 050201

        self.w.win_update()

    def paste(self, node):
        pass # to be implemented

    def unselect_clipboard_items(self): #bruce 050131 for Alpha
        "to be called before operations which are likely to fail when any clipboard items are selected"
        self.set_current_selection_group( self.tree)

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
        #bruce 050201 for Alpha: revised this to fix bug 370
        "delete whatever is selected from this assembly [except the PartGroup node itself]"
        self.w.history.message(greenmsg("Delete:"))
        ###@@@ #e this also needs a results-message, below.
        if self.selatoms:
            self.changed()
            for a in self.selatoms.values():
                a.kill()
            self.selatoms = {} # should be redundant
        if 1:
            ## bruce 050201 removed the condition "self.selwhat == 2 or self.selmols"
            # since selected jigs no longer force selwhat to be 2.
            # (Maybe they never did, but my guess is they did; anyway I think they shouldn't.)
            # self.changed() is not needed since removing Group members should do it (I think),
            # and would be wrong here if nothing was selected.
            self.tree.unpick_top() #bruce 050201: prevent deletion of entire part (no msg needed)
            self.tree.apply2picked(lambda o: o.kill())
            # Also kill anything picked in the clipboard
            # [revised by bruce 050131 for Alpha, see cvs rev 1.117 for historical comments]
            self.shelf.apply2picked(lambda o: o.kill()) # kill by Mark(?), 11/04
        self.setDrawLevel()
        return


##    # actually remove a given molecule from the list [no longer used]
##    def killmol(self, mol):
##        mol.kill()
##        self.setDrawLevel()


    # bruce 050201 for Alpha:
    #    Like I did to fix bug 370 for Delete (and cut and copy),
    # make Hide and Unhide work on jigs even when in selatoms mode.
    #    Also make them work in clipboard (by changing
    # self.tree to self.root below) -- no reason
    # not to, and it's confusing when cmenu offers these choices but they do nothing.
    # It's ok for them to operate on entire Part since they only affect leaf nodes.
    
    def Hide(self):
        "Hide all selected chunks and jigs"
        self.root.apply2picked(lambda x: x.hide())
        self.w.win_update()

    def Unhide(self):
        "Unhide all selected chunks and jigs"
        self.root.apply2picked(lambda x: x.unhide())
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
            self.o.gl_update()

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
        self.o.gl_update()

    #stretch a molecule
    def Stretch(self):
        if not self.selmols:
            self.w.history.message(redmsg("no selected chunks to stretch")) #bruce 050131
            return
        self.changed()
        for m in self.selmols:
            m.stretch(1.1)
        self.o.gl_update()

    #weld selected molecules together
    def weld(self):
        #bruce 050131 comment: might now be safe for clipboard items
        # since all selection is now forced to be in the same one;
        # this is mostly academic since there's no pleasing way to use it on them,
        # though it's theoretically possible (since Groups can be cut and maybe copied).
        if len(self.selmols) < 2:
            self.w.history.message(redmsg("need two or more selected chunks to weld")) #bruce 050131
            return
        self.changed() #bruce 050131 bugfix or precaution
        mol = self.selmols[0]
        for m in self.selmols[1:]:
            mol.merge(m)


    def align(self):
        if len(self.selmols) < 2:
            self.w.history.message(redmsg("need two or more selected chunks to align")) #bruce 050131
            return
        self.changed() #bruce 050131 bugfix or precaution
        ax = V(0,0,0)
        for m in self.selmols:
            ax += m.getaxis()
        ax = norm(ax)
        for m in self.selmols:
            m.rot(Q(m.getaxis(),ax))
        self.o.gl_update()
                  

    #############

    def __str__(self):
        return "<Assembly of " + self.filename + ">"

    def computeBoundingBox(self):
        """Compute the bounding box for the assembly. This should be
        called whenever the geometry model has been changed, like new
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
    def makeMinMovie(self,mtype = 2):
        """Minimize the part and display the results.
        mtype:
            1 = tell writemovie() to create a single-frame XYZ file.
            2 = tell writemovie() to create a multi-frame DPB moviefile.
        """
        r = self.writemovie(mtype) # Writemovie informs user if there was a problem.
        if r: return # We had a problem writing the minimize file.  Simply return.
        
        if mtype == 1:  # Load single-frame XYZ file.
            newPositions = self.readxyz()
            if newPositions:
                self.moveAtoms(newPositions)
            
        else: # Play multi-frame DPB movie file.
            self.m.currentFrame = 0
            # If _setup() returns a non-zero value, something went wrong loading the movie.
            if self.m._setup(): return
            self.m._play()
            self.m._close()
        
    def makeRotaryMotor(self, sightline):
        """Creates a Rotary Motor connected to the selected atoms.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m=RotaryMotor(self)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Rotary Motory Dialog.
            del(m)
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()
      
    def makeLinearMotor(self, sightline):
        """Creates a Linear Motor connected to the selected atoms.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m = LinearMotor(self)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Linear Motory Dialog.
            del(m)
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()

    def makeground(self):
        """Grounds (anchors) all the selected atoms so that 
        they will not move during a simulation run.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m=Ground(self, self.selatoms.values())
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()

    def makestat(self):
        """Attaches a Langevin thermostat to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m=Stat(self, self.selatoms.values())
        m.mol.dad.addmember(m)
        self.unpickatoms()
        
    def makethermo(self):
        """Attaches a thermometer to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m=Thermo(self, self.selatoms.values())
        m.mol.dad.addmember(m)
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
            for a in atom.neighbors():
                 self.conncomp(a)

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

    def modifyDeleteBonds(self):
        """Delete all bonds between selected and unselected atoms or chunks
        """
        
        if not self.selatoms and not self.selmols: # optimization, and different status msg
            msg = redmsg("Delete Bonds: Nothing selected")
            self.w.history.message(msg)
            return
        
        self.w.history.message(greenmsg("Delete Bonds:"))
        
        cutbonds = 0
        
        # Delete bonds between selected atoms and their neighboring atoms that are not selected.
        for a in self.selatoms.values():
            for b in a.bonds[:]:
                neighbor = b.other(a)
                if neighbor.element != Singlet:
                    if not neighbor.picked:
                        b.bust()
                        a.pick() # Probably not needed, but just in case...
                        cutbonds += 1

        # Delete bonds between selected chunks and chunks that are not selected.
        for mol in self.selmols[:]:
            # "externs" contains a list of bonds between this chunk and a different chunk
            for b in mol.externs[:]:
                # atom1 and atom2 are the connect atoms in the bond
                if int(b.atom1.molecule.picked) + int(b.atom2.molecule.picked) == 1: 
                    b.bust()
                    cutbonds += 1
                    
        msg = fix_plurals("%d bond(s) deleted" % cutbonds)
        self.w.history.message(msg)
        
        if self.selatoms and cutbonds:
            self.modifySeparate() # Separate the selected atoms into a new chunk
        else:
            self.w.win_update() #e do this in callers instead?
        
    #m modifySeparate needs to be changed to modifySplit.  Need to coordinate
    # this with Bruce since this is called directly from some mode modules.
    # Mark 050209
    #
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
        self.o.gl_update()

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

    # read xyz file.
    def readxyz(self):
        from fileIO import readxyz
        return readxyz(self)
                    
    # end of class assembly