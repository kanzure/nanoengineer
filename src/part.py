# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

"""
part.py

Provides class Part, for all chunks and jigs in a single physical space,
together with their selection state and grouping structure (shown in the model tree).

TEMPORARILY OWNED BY BRUCE 050202 for the Part/assembly split ####@@@@

$Id$

see assembly.py docstring, some of which is really about this module. ###@@@ revise

==

This module also contains a lot of code for specific operations on sets of molecules,
which are all in the current part. Some of this code might ideally be moved to some
other file.

==

History: split out of assembly.py (the file, and more importantly the class)
by bruce 050222. The Part/assembly distinction was introduced by bruce 050222
(though some of its functionality was anticipated by the "current selection group"
introduced earlier, just before Alpha-1). [I also rewrote this entire docstring then.]

The Part/assembly distinction is unfinished, particularly in how it relates to some modes and to movie files.

Prior history of assembly.py (and thus of much code in this file) unclear;
assembly.py was almost certainly originated by Josh.

"""

###e imports -- many of these are probably not needed
from Numeric import *
from VQT import *
from string import *
import re
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from struct import unpack

##bruce 050222 thinks the following are not needed here anymore:
##from drawer import drawsphere, drawcylinder, drawline, drawaxes
##from drawer import segstart, drawsegment, segend, drawwirecube
##from shape import *

from chem import *
from movie import *
from gadgets import *
from Utility import *
from HistoryWidget import greenmsg, redmsg
from platform import fix_plurals
from inval import InvalMixin
from changes import begin_event_handler, end_event_handler

# number of atoms for detail level 0
HUGE_MODEL = 20000
# number of atoms for detail level 1
LARGE_MODEL = 5000

class Part(InvalMixin):
    """
    One Part object is created to hold any set of chunks and jigs whose
    coordinates are intended to lie in the same physical space.
    When new clipboard items come into being, new Parts are created as needed
    to hold them; and they should be destroyed when those clipboard items
    no longer exist as such (even if the chunks inside them still exist in
    some other Part).
       Note that parts are not Nodes (or at least, they are not part of the same node-tree
    as the chunks/jigs they contain); each Part has a toplevel node self.tree,
    and a reference to the shared (per-assy) clipboard to use, self.shelf [###k].
    """
    def __init__(self, assy, topnode):
        self.init_InvalMixin()
        self.assy = assy
        self.topnode = topnode
        self.nodecount = 0 # doesn't yet include topnode
        self.add(topnode)
        # for now:
        from assembly import assembly # the class
        assert isinstance(assy, assembly)
        assert isinstance(topnode, Node)
        
        # _modified?? not yet needed for individual parts, but will be later.
        
        # coord sys stuff? data? lastCsys homeCsys xy yz zx ###@@@ review which ivars needed; do we want unique names?? no.
        # the coordinate system (Actually default view) ####@@@@ does this belong to each Part?? guess: yes
        self.homeCsys = Csys(self.assy, "HomeView", 10.0, V(0,0,0), 1.0, 0.0, 1.0, 0.0, 0.0)
        self.lastCsys = Csys(self.assy, "LastView", 10.0, V(0,0,0), 1.0, 0.0, 1.0, 0.0, 0.0) 
        self.xy = Datum(self.assy, "XY", "plane", V(0,0,0), V(0,0,1))
        self.yz = Datum(self.assy, "YZ", "plane", V(0,0,0), V(1,0,0))
        self.zx = Datum(self.assy, "ZX", "plane", V(0,0,0), V(0,1,0))
        grpl1=[self.homeCsys, self.lastCsys, self.xy, self.yz, self.zx]
        self.data=Group("Data", self.assy, None, grpl1)
        self.data.open=False

        # name? no, at least not yet, until there's a Part Tree Widget.
        
        # filename? might need one for helping store associated files... could share assy.filename for now.

        # some attrs are recomputed as needed (see below for their _recompute_ or _get_ methods):
        # e.g. molecules, bbox, center, drawLevel

        # not here: alist, selatoms, selmols - they're all done by a _recompute_xxx
        
        ## moved from assy init, not yet edited for here; some of these will be inval/update vars ###@@@
##        # list of chem.molecule's
##        self.molecules=[]
        # list of the atoms, only valid just after read or write
        #####@@@@@ wrong, just for testing: let alist be seen in assy:
        ## self.alist = [] #None
        
##        # to be shrunk, see addmol
##        self.bbox = BBox()
##        self.center = V(0,0,0)

##        # dictionary of selected atoms (indexed by atom.key)
##        self.selatoms={}
##        # list of selected molecules
##        self.selmols=[]
##        # level of detail to draw
##        self.drawLevel = 2
        
        # the Movie object. ###@@@ might need revision for use in clipboard item parts... esp when it uses filename...
        ###@@@ doesn't work yet, one reason being the menu items in movieMode.py... for now this is in assy:
        ## self.m=Movie(self)
        # movie ID, for future use.
        self.movieID=0
        # ppa = previous picked atoms. ###@@@ not sure per-part; should reset when change mode or part
        self.ppa2 = self.ppa3 = None
        
        ### Some information needed for the simulation or coming from mmp file
        self.temperature = 300
        self.waals = None

        return # from Part.__init__

    # == membership maintenance

    # Note about selection of nodes moving between parts:
    # when nodes are removed or added to parts, we ensure they (or their atoms) are not picked,
    # so that we needn't worry about updating selatoms, selmols, or current selection group;
    # this also seems best in terms of the UI. But note that it's not enough, if .part revision
    # follows tree revision, since picked nodes control selection group using tree structure alone.

    def add(self, node):
        if node.part == self:
            # this is normal, e.g. in ensure_one_part, so don't complain
##            if platform.atom_debug:
##                print "atom_debug: warning: node added to its own part (noop):", node, self
            return
        if node.part:
            if platform.atom_debug: #e this will be common, remove it as soon as you see it (unless i do the remove explicitly)
                print "atom_debug: fyi: node added to new part so removed from old part first:", node, self, node.part
            node.part.remove(node)
        assert node.part == None
        assert not node.picked # since remove did it, or it was not in a part and could not have been picked (I think!)
        #e assert a mol's atoms not picked too (too slow to do it routinely; bugs in this are likely to be noticed)
        node.part = self
        self.nodecount += 1
        if isinstance(node, molecule): #####@@@@@ #e better if we let the node add itself to our stats and lists, i think...
            ## not needed: self.invalidate_attrs(['molecules','selmols','selatoms'])
            self.invalidate_attrs(['molecules']) #e or we could append it... but I doubt that's worthwhile ###@@@
            self.adjust_natoms( len(node.atoms)) ####@@@@ might be useless if this depends on .molecules
            #####@@@@@ also adjust or invalidate bbox, center
        # note that node is not added to any comprehensive list of nodes, in fact, we don't have one.
        # presumably this function is only called when node was just, or is about to be,
        # added to a nodetree in a place which puts it into this part's tree.
        return
    
    def remove(self, node):
        """Remove node (a member of this part) from this part's lists and stats;
        reset node.part; DON'T look for interspace bonds yet (since this node
        and some of its neighbors might be moving to the same new part).
        Node (and its atoms, if it's a chunk) will be unpicked before the removal.
        """
        assert node.part == self
        node.unpick() # this maintains selmols if necessary
        if isinstance(node, molecule):
            # need to unpick the atoms? [would be better to let the node itself have a method for this]
            # (#####@@@@@ fix atom.unpick to not remake selatoms if missing, or to let this part maintain it)
            if (not self.__dict__.has_key('selatoms')) or self.selatoms:
                for atm in node.atoms.itervalues():
                    atm.unpick() #e optimize this by inlining and keeping selatoms test outside of loop
            self.invalidate_attrs(['molecules'])
            self.adjust_natoms(- len(node.atoms)) ####@@@@ might be useless if this depends on .molecules
            #####@@@@@ also adjust or invalidate bbox, center
            ## second try at the above:
##            self.invalidate_attrs(['molecules','selmols','selatoms'])
            ## first try at the above:
##            try:
##                if node.picked and self.__dict__.has_key('selmols'): # not if attr is invalid (common?? ###k)
##                    self.selmols.remove(node)
##                    self.changed_attr('selmols')
##            except ValueError:
##                if platform.atom_debug:
##                    print "part's mol was picked but not in selmols"
##            try:
##                if self.__dict__.has_key('molecules'): # not if attr is invalid (common?? ###k)
##                    self.molecules.remove(node)
##            except ValueError:
##                if platform.atom_debug:
##                    print "part's mol was picked but not in molecules"
        self.nodecount -= 1
        node.part = None
        if self.topnode == node:
            self.topnode = None #k can this happen when any nodes are left??? if so, is it bad?
            if platform.atom_debug:
                print "atom_debug: fyi: topnode leaves part, %d nodes remain" % self.nodecount 
        if self.nodecount <= 0:
            assert self.nodecount == 0
            assert not self.topnode
            self.destroy()
        return

    def destroy(self):
        "forget everything, let all storage be reclaimed" # implem is a guess
        ## self.invalidate_all_attrs() # not needed
        for attr in self.__dict__.keys():
            delattr(self,attr) # is this safe, in arb order??
        return

    # incremental update methods
    
    def selmols_append(self, mol):
        if self.__dict__.has_key('selmols'):
            assert mol not in self.selmols
            self.selmols.append(mol)
        return

    def selmols_remove(self, mol):
        if self.__dict__.has_key('selmols'):
            ## might not always be true in current code, though it should be:
            ## assert mol in self.selmols
            try:
                self.selmols.remove(mol)
            except ValueError: # not in the list
                if platform.atom_debug:
                    print_compact_traceback("selmols_remove finds mol not in selmols (might not be a bug): ")
        return

    def adjust_natoms(self, delta):
        "adjust the number of atoms, if known. Useful since drawLevel depends on this and is often recomputed."
        if self.__dict__.has_key('natoms'):
            self.natoms += delta
        return
    
    # == compatibility methods
    
    def _get_tree(self): #####@@@@@ find and fix all sets of .tree or .root or .data or .shelf
        return self.topnode

    def _get_root(self): #k needed?
        return self.topnode
    
    # == properties that might be overridden by subclasses
    
    def immortal(self):
        """Should this Part be undeletable from the UI (by cut or delete operations)?
        When true, delete will delete its members (leaving it empty but with its topnode (aka tree) still present),
        and cut will cut its members and move them into a copy of its topnode, which is left still present and empty.
        [can be overridden in subclasses]
        """
        return False # simplest value used as default

    # == attributes which should be delegated to self.assy
    
    # attrnames to delegate to self.assy (ideally for writing as well as reading, until all using-code is upgraded)
    assy_attrs = ['w','o','mt','selwhat']
        # 050308: selwhat will be an official assy attribute;
        # some external code assigns to assy.selwhat directly,
        # and for now can keep doing that. Within the Part, perhaps we should
        # use a set_selwhat method if we need one, but for now we just assign
        # directly to self.assy.selwhat.
    assy_attrs_temporary = ['changed'] # tolerable, but might be better to track per-part changes, esp. re movies #####@@@@@
    assy_attrs_review = ['shelf']
        #e in future, we'll split out our own methods for some of these, incl .changed
        #e and for others we'll edit our own methods' code to not call them on self but on self.assy (incl selwhat).
    assy_attrs_all = assy_attrs + assy_attrs_temporary + assy_attrs_review
    
    def __getattr__(self, attr):
        "[overrides InvalMixin.__getattr__]"
        if attr.startswith('_'): # common case, be fast (even though it's done redundantly by InvalMixin.__getattr__)
            raise AttributeError, attr
        if attr in self.assy_attrs_all:
            # delegate to self.assy
            return getattr(self.assy, attr) ###@@@ detect error of infrecur, since assy getattr delegates to here??
        return InvalMixin.__getattr__(self, attr) # uses _get_xxx and _recompute_xxx methods

    # == attributes which should be invalidated and recomputed as needed (both inval and recompute methods follow)

    #bruce 050202 for Alpha: help fix things up after a DND move in/out of assy.tree. ###@@@ revise docstring for self being a Part
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
        self.invalidate_attr('molecules') # note: this also invals bbox, center, drawLevel

    _inputs_for_molecules = [] # only invalidated directly, by update_mols #####@@@@@ need to do it in any other places too?
    def _recompute_molecules(self):
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
            # warning: not in the same order as they are in the tree!
            # even if it was, it might elsewhere be incrementally updated.
        return
    
    ###### what called this? it had a diff name...
    def update_content_summaries(): #bruce 050228 split this from other methods #####@@@@@ wrong, change each method to inval, use _get
        "[private method] recompute bbox and drawLevel attributes"
        assert 0 # not needed i hope
        self.setDrawLevel()
        self.computeBoundingBox()
        return

    _inputs_for_natoms = ['molecules']
    def _recompute_natoms(self):
        #e we might not bother to inval this for indiv atom changes in mols -- not sure yet
        #e should we do it incrly? should we do it on every node, and do other stats too?
        num = 0
        for mol in self.molecules:
            num += len(mol.atoms)
        return num

    _inputs_for_drawLevel = ['natoms']
    def _recompute_drawLevel(self):
        "This is used to control the detail level of sphere subdivision when drawing atoms."
        num = self.natoms
        self.drawLevel = 2
        if num > LARGE_MODEL: self.drawLevel = 1
        if num > HUGE_MODEL: self.drawLevel = 0
    
    def computeBoundingBox(self):
        """Compute the bounding box for this Part. This should be
        called whenever the geometry model has been changed, like new
        parts added, parts/atoms deleted, parts moved/rotated(not view
        move/rotation), etc."""
        self.invalidate_attrs('bbox','center')
        self.bbox, self.center
        return

    _inputs_for_bbox = ['molecules'] # in principle, this should also be invalidated directly by a lot more than does it now
    def _recompute_bbox(self):
        self.bbox = BBox()
        for mol in self.molecules:
              self.bbox.merge(mol.bbox)
        self.center = self.bbox.center()
    
    _inputs_for_center = ['molecules']
    _recompute_center = _recompute_bbox

    _inputs_for_alist = [] # only invalidated directly. Not sure if we'll inval this whenever we should, or before uses. #####@@@@@
    def _recompute_alist(self):
        """Return a list of all atoms in this Part, in the same order in which they
        were read from, or would be written to, an mmp file --
        namely, tree order for chunks, atom.key order within chunks.
        """
        #bruce 050228 changed chunk.writemmp to make this possible,
        # by writing atoms in order of atom.key,
        # which is also the order they're created in when read from an mmp file.
        # Note that just after reading an mmp file, all atoms in alist are ordered by .key,
        # but this is no longer true in general after chunks are reordered, separated, merged,
        # or atoms are created or destroyed. What does remain true is that newly written mmp files
        # would have atoms (and the assy.alist computed by the old mmp-writing code)
        # in the same order as this function computes.
        #   (#e Warning: if we revise mmp file format, this might no longer be correct.
        # For example, if we wanted movies to remain valid when chunks were reordered in the MT
        # and even when atoms were divided into chunks differently,
        # we could store an array of atoms followed by chunking and grouping info, instead of
        # using tree order at all to determine the atom order in the file. Or, we could change
        # the movie file format to not depend so strongly on atom order.)
        self.alist = 333 # not a valid Python sequence
        alist = []
        def func_alist(nn):
            "run this exactly once on all molecules (or other nodes) in this part, in tree order"
            if isinstance(nn, molecule):
                alist.extend(nn.atoms_in_mmp_file_order())
            return # from func_alist only
        self.tree.apply2all( func_alist)
        self.alist = alist
        return

    _inputs_for_selmols = [] # only inval directly, since often stays the same when molecules changes, and might be incrly updated
    def _recompute_selmols(self):
        #e not worth optimizing for selwhat... but assert it was consistent, below.
        self.selmols = 333 # not a valid Python sequence
        res = []
        def func_selmols(nn):
            "run this exactly once on all molecules (or other nodes) in this part (in any order)"
            if isinstance(nn, molecule) and nn.picked:
                res.append(nn)
            return # from func_selmols only
        self.tree.apply2all( func_selmols)
        self.selmols = res
        if self.selmols:
            if self.selwhat != SELWHAT_CHUNKS:
                msg = "bug: part has selmols but selwhat != SELWHAT_CHUNKS"
                if platform.atom_debug:
                    print_compact_stack(msg)
                else:
                    print msg
        return

    _inputs_for_selatoms = [] # only inval directly (same reasons as selmols; this one is *usually* updated incrementally, for speed)
    def _recompute_selatoms(self):
        if self.selwhat != SELWHAT_ATOMS:
            # optimize, by trusting selwhat to be correct.
            # This is slightly dangerous until changes to assy's current selgroup/part
            # also fix up selatoms, and perhaps even verify no atoms selected in new part.
            # But it's likely that there are no such bugs, so we can try it this way for now.
            # BTW, someday we might permit selecting atoms and chunks at same time,
            # and this will need revision -- perhaps we'll have a selection-enabled boolean
            # for each type of selectable thing; perhaps we'll keep selatoms at {} when they're
            # known to be unselectable.
            # [bruce 050308]
            return {} # caller (InvalMixin.__getattr__) will store this into self.selatoms
        self.selatoms = 333 # not a valid dictlike thing
        res = {}
        def func_selatoms(nn):
            "run this exactly once on all molecules (or other nodes) in this part (in any order)"
            if isinstance(nn, molecule):
                for atm in nn.atoms.itervalues():
                    if atm.picked:
                        res[atm.key] = atm
            return # from func_selatoms only
        self.tree.apply2all( func_selatoms)
        self.selatoms = res
        return
        
    # ==
    
    def addmol(self, mol): #bruce 050228 revised this for Part (was on assy) and for inval/update of part-summary attrs.
        """(Public method:)
        Add a chunk to this Part (usually the "current Part").
        Invalidate part attributes which summarize part content (e.g. bbox, drawLevel).
##        Merge bboxes and update our drawlevel
##        (though there is no guarantee that mol's bbox and/or number of atoms
##        won't change again during the same user-event that's running now;
##        some code might add mol when it has no atoms, then add atoms to it).
        """
        self.changed() #bruce 041118
##        self.bbox.merge(mol.bbox) # [see also computeBoundingBox -- bruce 050202 comment]
##        self.center = self.bbox.center()
##        self.molecules += [mol]
        self.ensure_toplevel_group() # need if, e.g., we use Build mode to add to a clipboard item
        self.tree.addmember(mol)
            #bruce 050202 comment: if you don't want this location for the added mol,
            # just call mol.moveto when you're done, like fileIO does.   
        self.invalidate_attrs(['natoms','molecules']) #####@@@@@ does this inval bbox and center too??

    def ensure_toplevel_group(self):
        "make sure this Part's toplevel node is a Group, by Grouping it if not."
        assert self.tree
        if not self.tree.is_group():
            self.tree = Group("Group", self.assy, None, [self.tree])
            self.assy.fix_parts()
        return
    
    # ==
    
    def draw(self, win): ###@@@ win arg, unused, should be renamed or removed
        self.tree.draw(self.o, self.o.display)
    
    # == movie support code
    
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
            #bruce 050210 fixing "movie reset" bug reported by Josh for Alpha-2
            assert m.basepos is m.curpos
            m.basepos = m.curpos = m.atpos = + m._savedbasepos
            m.changed_attr('atpos', skip = ('basepos',) )

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
           
        if len(newPositions) != len(self.alist): #bruce 050225 added some parameters to this error message
            print "moveAtoms: The number of atoms from XYZ file (%d) is not matching with that of the current model (%d)" % \
                  (len(newPositions), len(self.alist))
            return
        for a, newPos in zip(self.alist, newPositions):
                a.setposn(A(newPos))
        self.o.gl_update()                

    #####@@@@@ as of 050225 1109pm we get (end of minimize):
    # The number of atoms from XYZ file (18) is not matching with that of the current model (0)
    # guess: the file writer puts the alist into the assy not here into the part. (and writes from the assy too, regardless of cur part)

    #####@@@@@ end "newly pulled in 050225"

    # functions from the "Select" menu
    # [these are called to change the set of selected things in this part,
    #  when it's the current part; these are event handlers which should
    #  do necessary updates at the end, e.g. win_update, and should print
    #  history messages, etc]

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        [bruce 050201 observes that this docstring is wrong.]
        """ ###@@@
        if self.selwhat == SELWHAT_CHUNKS:
            for m in self.molecules:
                m.pick()
        else:
            assert self.selwhat == SELWHAT_ATOMS
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
        if self.selwhat == SELWHAT_CHUNKS:
            newpicked = filter( lambda m: not m.picked, self.molecules )
            self.unpickparts()
            for m in newpicked:
                m.pick()
        else:
            assert self.selwhat == SELWHAT_ATOMS
            for m in self.molecules:
                for a in m.atoms.itervalues():
                    if a.picked: a.unpick()
                    else: a.pick()
        self.w.win_update()

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """ ###@@@ should make sure we don't traverse interspace bonds, until all bugs creating them are fixed
        if not self.selatoms:
            self.w.history.message(redmsg("Select Connected: No atom(s) selected."))
            return
        
        alreadySelected = len(self.selatoms.values())
        self.marksingle()
        self.w.history.message(greenmsg("Select Connected:"))
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d connected atom(s) selected." % totalSelected)
        
        if totalSelected > alreadySelected:
            ## Otherwise, that just means no new atoms selected, so no update necessary    
            #self.w.win_update()
            self.o.gl_update()
        
    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """ ###@@@ same comment about interspace bonds as in selectConnected
        if not self.selatoms:
            self.w.history.message(redmsg("Select Doubly: No atom(s) selected."))
            return
            
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.w.history.message(greenmsg("Select Doubly:"))
        
        self.w.history.message("Working.  Please wait...")
        alreadySelected = len(self.selatoms.values())
        self.markdouble()
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d doubly connected atom(s) selected." % totalSelected)
        
        QApplication.restoreOverrideCursor() # Restore the cursor
        
        if totalSelected > alreadySelected:
            ## otherwise, means nothing new selected. Am I right? ---Huaicai, not analyze the markdouble() algorithm yet 
            #self.w.win_update()
            self.o.gl_update()

    ###@@@ what calls these? they do win_update but they don't change which select mode is in use.
    
    def selectAtoms(self):
        self.unpickparts()
        self.assy.selwhat = SELWHAT_ATOMS
        self.w.win_update()
            
    def selectParts(self):
        self.pickParts()
        self.w.win_update()

    def pickParts(self):
        self.assy.selwhat = SELWHAT_CHUNKS
        lis = self.selatoms.values()
        self.unpickatoms()
        for atm in lis:
            atm.molecule.pick()

    # == selection functions using a mouse position
    ###@@@ move to glpane??
    
    # (Not toplevel event handlers ###k some aren't anyway)

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
            if self.selwhat == SELWHAT_CHUNKS:
                if not self.selmols:
                    self.selmols = []
                    # bruce 041214 added that, since pickpart used to do it and
                    # calls of that now come here; in theory it's never needed.
                atm.molecule.pick()
                self.w.history.message(atm.molecule.getinfo())
            else:
                assert self.selwhat == SELWHAT_ATOMS
                atm.pick()
                self.w.history.message(atm.getinfo())
        return
    
    def onlypick_at_event(self, event): #renamed from onlypick; modified
        """Unselect everything in the glpane; then select whatever visible atom
        or chunk (depending on self.selwhat) is under the mouse at event.
        If no atom or chunk is under the mouse, nothing in glpane is selected.
        """
        if self.selwhat == SELWHAT_CHUNKS:
            self.unpickparts() # (fyi, this unpicks in clipboard as well)
        else:
            assert self.selwhat == SELWHAT_ATOMS
            self.unpickatoms()
        self.pick_at_event(event)
    
    def unpick_at_event(self, event): #renamed from unpick; modified
        """Make whatever visible atom or chunk (depending on self.selwhat)
        is under the mouse at event get un-selected,
        but don't change whatever else is selected.
        """
        atm = self.findAtomUnderMouse(event)
        if atm:
            if self.selwhat == SELWHAT_CHUNKS:
                atm.molecule.unpick()
            else:
                assert self.selwhat == SELWHAT_ATOMS
                atm.unpick()
        return

    # == internal selection-related routines
    
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
        if self.assy.selwhat != SELWHAT_CHUNKS:
            self.unpickatoms()
            self.assy.selwhat = SELWHAT_CHUNKS
        return
    
    # deselect any selected molecules or groups
    def unpickparts(self):
        self.tree.unpick()
        # before assy/part split, this was root, i.e. assy.tree and assy.shelf

    # for debugging
    def prin(self):
        for a in self.selatoms.itervalues():
            a.prin()
            
    #bruce 050131/050201 for Alpha (really for bug 278 and maybe related ones):
    # sanitize_for_clipboard, for cut and copy and other things that add clipboard items
    # ####@@@@ need to use in sethotspot too??

    #####@@@@@ fate of sanitize_for_clipboard, for assy/part split: [see notes]
    
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
        if 0 and platform.atom_debug: #bruce 050215 this is indeed None for mols copied by mol.copy
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
                print "btw self is",self
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

    # == #####@@@@@ cut/copy/paste/kill will all be revised to handle bonds better (copy or break them as appropriate)
    # incl jig-atom connections too
    
    # bruce 050131/050201 revised these Cut and Copy methods to fix some Alpha bugs;
    # they need further review after Alpha, and probably could use some merging. ###@@@
    # See also assy.kill (Delete operation).
    
    def cut(self):
        eh = begin_event_handler("Cut") # bruce ca. 050307; stub for future undo work; experimental
        try:
            self.w.history.message(greenmsg("Cut:"))
            if self.selatoms:
                #bruce 050201-bug370 (2nd commit here, similar issue to bug 370):
                # changed condition to not use selwhat, since jigs can be selected even in Select Atoms mode
                self.w.history.message(redmsg("Cutting selected atoms is not yet supported.")) #bruce 050201
                ## return #bruce 050201-bug370: don't return yet, in case some jigs were selected too.
                # note: we will check selatoms again, below, to know whether we emitted this message
            new = Group(gensym("Copy"), self.assy, None)
                # bruce 050201 comment: this group is usually, but not always, used only for its members list
            if self.immortal() and self.tree.picked:
                ###@@@ design note: this is an issue for the partgroup but not for clips... what's the story?
                ### Answer: some parts can be deleted by being entirely cut (top node too) or killed, others can't.
                ### This is not a properly of the node, so much as of the Part, I think.... not clear since 1-1 corr.
                ### but i'll go with that guess. immortal parts are the ones that can't be killed in the UI.
                
                #bruce 050201 to fix catchall bug 360's "Additional Comments From ninad@nanorex.com  2005-02-02 00:36":
                # don't let assy.tree itself be cut; if that's requested, just cut all its members instead.
                # (No such restriction will be required for assy.copy, even when it copies entire groups.)
                self.tree.unpick_top()
                ## self.w.history.message(redmsg("Can't cut the entire Part -- cutting its members instead.")) #bruce 050201
                ###@@@ following should use description_for_history, but so far there's only one such Part so it doesn't matter yet
                self.w.history.message("Can't cut the entire Part; copying its toplevel Group, cutting its members.") #bruce 050201
                # new code to handle this case [bruce 050201]
                self.tree.apply2picked(lambda(x): x.moveto(new))
                use = new
                use.name = self.tree.name # not copying any other properties of the Group (if it has any)
                new = Group(gensym("Copy"), self.assy, None)
                new.addmember(use)
            else:
                self.tree.apply2picked(lambda(x): x.moveto(new))
                # bruce 050131 inference from recalled bug report:
                # this must fail in some way that addmember handles, or tolerate jigs/groups but shouldn't;
                # one difference is that for chunks it would leave them in assy.molecules whereas copy would not;
                # guess: that last effect (and the .pick we used to do) might be the most likely cause of some bugs --
                # like bug 278! Because findpick (etc) uses assy.molecules. So I fixed this with sanitize_for_clipboard, below.

            # Now we know what nodes to cut (i.e. move to the clipboard) -- the members of new.
            # And they are no longer in their original location,
            # but neither they nor the group "new" is in its final location.
            # (But they still belong to their original Part, until this is changed later.)
            
            #e much of the following might someday be done automatically by end_event_handler and by methods in a Cut command object
            
            if new.members:
                # move them to the clipboard (individually for now, though this
                # is wrong if they are bonded; also, this should be made common code
                # with DND move to clipboard, though that's more complex since
                # it might move nodes inside an existing item. [bruce 050307 comment])
                self.changed() # bruce 050201 doing this earlier; 050223 made it conditional on new.members
                nshelf_before = len(self.shelf.members) #bruce 050201
                for ob in new.members[:]:
                    # [bruce 050302 copying that members list, to fix bug 360 item 8, like I fixed
                    #  bug 360 item 5 in "copy" 2 weeks ago. It's silly that I didn't look for the same
                    #  bug in this method too, when I fixed it in copy.]
                    # bruce 050131 try fixing bug 278 in a limited, conservative way
                    # (which won't help the underlying problem in other cases like drag & drop, sorry),
                    # based on the theory that chunks remaining in assy.molecules is the problem:
                    ## self.sanitize_for_clipboard(ob) ## zapped 050307 since obs
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
        finally:
            end_event_handler(eh) # this should fix Part membership of moved nodes, break inter-Part bonds #####@@@@@ doit
            # ... but it doesn't, so instead, do this: ######@@@@@@ and review this situation and clean it up:
            self.assy.update_parts()
            #####@@@@@ still need to break inter-part bonds...
            self.w.win_update() ###stub of how this relates to ending the handler
        return

    # copy any selected parts (molecules) [making a new clipboard item... #doc #k]
    #  Revised by Mark to fix bug 213; Mark's code added by bruce 041129.
    #  Bruce's comments (based on reading the code, not all verified by test): [###obs comments]
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
        new = Group(gensym("Copy"), self.assy, None)
            # bruce 050201 comment: this group is always (so far) used only for its members list
        # x is each node in the tree that is picked. [bruce 050201 comment: it's ok if self.tree is picked.]
        # [bruce 050131 comments (not changing it in spite of bugs):
        #  the x's might be chunks, jigs, groups... but maybe not all are supported for copy.
        #  In fact, Group.copy returns 0 and Jig.copy returns None, and addmember tolerates that
        #  and does nothing!!
        #  About chunk.copy: it sets numol.assy but doesn't add it to assy,
        #  and it sets numol.dad but doesn't add it to dad's members -- so we do that immediately
        #  in addmember. So we end up with a members list of copied chunks from assy.tree.]
        self.tree.apply2picked(lambda(x): new.addmember(x.copy(None))) #bruce 050215 changed mol.copy arg from new to None

        # unlike for cut, no self.changed() should be needed
        
        if new.members:
            nshelf_before = len(self.shelf.members) #bruce 050201
            for ob in new.members[:]:
                # [bruce 050215 copying that members list, to fix bug 360 comment #6 (item 5),
                # which I introduced in Alpha-2 by making addmember remove ob from its prior home,
                # thus modifying new.members during this loop]
                self.sanitize_for_clipboard(ob) # not needed on 050131 but might be needed soon, and harmless
                self.shelf.addmember(ob) # add new member(s) to the clipboard
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
        self.assy.update_parts() # stub, 050308; overkill! should just apply to the new shelf items. ######@@@@@@ 
        self.w.win_update()
        return

    def break_interpart_bonds(self): ######@@@@@@ refile, review, implem, implem for jigs
        """Break all bonds between nodes in this part and nodes in other parts;
        jig-atom connections count as bonds [but might not be handled correctly as of 050308].
        #e In future we might optimize this and only do it for specific node-trees.
        """
        self.topnode.apply2all( lambda node: node.break_interpart_bonds() ) ######@@@@@@ IMPLEM
        return
    
    def paste(self, node):
        pass # to be implemented

    def kill(self):
        "delete everything selected in this Part [except the top node, if we're an immortal Part]"
        #bruce 050201 for Alpha: revised this to fix bug 370
        ## "delete whatever is selected from this assembly " #e use this in the assy version of this method, if we need one
        self.w.history.message(greenmsg("Delete:"))
        ###@@@ #e this also needs a results-message, below.
        if self.selatoms:
            self.changed()
            for a in self.selatoms.values():
                a.kill()
            self.selatoms = {} # should be redundant
        
        ## bruce 050201 removed the condition "self.selwhat == 2 or self.selmols"
        # (previously used to decide whether to kill all picked nodes in self.tree)
        # since selected jigs no longer force selwhat to be 2.
        # (Maybe they never did, but my guess is they did; anyway I think they shouldn't.)
        # self.changed() is not needed since removing Group members should do it (I think),
        # and would be wrong here if nothing was selected.
        if self.immortal():
            self.tree.unpick_top() #bruce 050201: prevent deletion of entire part (no msg needed)
        self.tree.apply2picked(lambda o: o.kill())
## no longer needed after assy/Part split:
##        # Also kill anything picked in the clipboard
##        # [revised by bruce 050131 for Alpha, see cvs rev 1.117 for historical comments]
##        self.shelf.apply2picked(lambda o: o.kill()) # kill by Mark(?), 11/04
        self.invalidate_attr('natoms') #####@@@@@ actually this is needed in the atom and molecule kill methods, and add/remove methods
        return

    # ==

    ###@@@ move/rot should be extended to apply to jigs too (and fit into some naming convention)
    
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

    # == these are event handlers which do their own full UI updates at the end
    
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

    #bond atoms (cheap hack) #e is still used? should it be more accessible?
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
    #bruce 050223 revised in minor ways; didn't test since it's not user-accessible now.
    # BTW we could add this for all bonds between selected atoms,
    # per recent Delete Bonds discussion.
    def Unbond(self):
        if not self.selatoms: return
        aa=self.selatoms.values()
        if len(aa)==2:
            self.changed()
            #bruce 041028 bugfix: add [:] to copy following lists,
            # since bust will modify them during the iteration
            for b1 in aa[0].bonds[:]:
                for b2 in aa[1].bonds[:]:
                    if b1 == b2:
                        b1.bust()
                        break #bruce 050223 precaution
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

    #weld selected molecules together  ###@@@ no update -- does caller do it?? [bruce 050223]
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

    #####@@@@@ movie funcs not yet reviewed much for assy/part split
        
    # makes a simulation movie
    def makeSimMovie(self):
        self.simcntl = runSim(self.assy) # Open SimSetup dialog
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

    # == jig makers
    
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
            del(m) #bruce comment 050223: this statement has no effect.
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
            del(m) #bruce comment 050223: this statement has no effect.
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()

    def makeground(self):
        """Grounds (anchors) all the selected atoms so that 
        they will not move during a simulation run.
        There is a limit of 30 atoms per Ground.  Any more will choke the file parser
        in the simulator. To work around this, just make more Grounds.
        """
        # [bruce 050210 modified docstring]
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
        m.atoms[0].molecule.dad.addmember(m) #bruce 050210 replaced obs .mol attr
        self.unpickatoms()
        
    def makethermo(self):
        """Attaches a thermometer to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m=Thermo(self, self.selatoms.values())
        m.atoms[0].molecule.dad.addmember(m) #bruce 050210 replaced obs .mol attr
        self.unpickatoms()

    # == helpers for SelectConnected and SelectDoubly
    
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

    # == more operations on selection, full event handlers with history and update
    
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
                self.addmol(numol) ###e move it to just after the one it was made from? or, end of same group??
                numolist+=[numol]
                if new_old_callback:
                    new_old_callback(numol, mol) # new feature 040929
        msg = fix_plurals("Separate created %d new chunk(s)" % len(numolist))
        self.w.history.message(msg)
        self.w.win_update() #e do this in callers instead?

    def copySelatomFrags(self):
        #bruce 041116, combining modifySeparate and mol.copy; intended for extrude, not yet used but should be
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
        if self.selwhat == SELWHAT_CHUNKS:
            for m in self.selmols:
                m.Passivate(True) # arg True makes it work on all atoms in m
        else:
            assert self.selwhat == SELWHAT_ATOMS
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

    # write moviefile #####@@@@@ not yet reviewed for assy/part split
    def writemovie(self, mflag = 0):
        from fileIO import writemovie
        return writemovie(self.assy, mflag) #####@@@@@  self ->self.assy -- guess

    # read xyz file. #####@@@@@ not yet reviewed for assy/part split
    def readxyz(self):
        from fileIO import readxyz
        return readxyz(self.assy) #####@@@@@  self ->self.assy -- guess
                    
    # end of class Part

# subclasses of Part

class MainPart(Part):
    def immortal(self): return True
    pass

class ClipboardItemPart(Part):
    pass

# ==

def process_changed_dads_fix_parts():
    """Grab (and reset) the global set of nodes with possibly-changed dads,
    and use this info (and our memory from prior times we ran??)
    to fix Parts of all affected nodes.
    If this should someday coexist with other things to do with the
    same set of nodes with changed dads (at the same time, since it's reset),
    then how these interact is unclear; probably we'll be put into an order
    or nesting with those, become methods of an object, and not do our own grab/reset.
    """
    # [Try to be correct even if there are multiple assys and nodes can move between them!
    #  I don't know if we'll achieve this, and it's not urgent.]
    nodes = changed.dads.grab_and_reset_changed_objects()
    ##e future: also know their old dads, so we can see if the dads really changed. Not very important, not done yet.
    # A node with a new dad might have a new Part, and any of its children might have one.
    # By the time we run, they all already have their new dad, so we can figure out what Part they and kids should have.
    # So one easy scheme is just to invalidate the Part for all nodes that might have it wrong. #####@@@@@ not sure...
    # And then, when done, recompute them all? We do want to *actually finish* moving nodes from their old to new Parts,
    # and when that's done, checking them all for external bonds that have become interspace bonds and need to be broken
    # or (maybe) need to induce new Parts to merge.
    for node in topmost_nodes(nodes):
        # this includes nodes that got moved, but perhaps also some "deleted"
        # nodes no longer in the tree at all. This might be a good place to destroy
        # the latter kind! But to avoid bugs, it's safer to do that later (or never).
        # But we detect them right away, to avoid bugs in other methods like find_selection_group.
        if not node.has_home():
            # actually we need to remove them from their Parts, at least, right away.
            clean_deleted_node( node)
                #e (this would be bad if we wanted to keep it around for undo-related purposes)
            continue
        sg = node.find_selection_group()
        ###e next steps: ######@@@@@@ this is where i am, 050303 10:09pm
        # figure out part, make it if nec, see fix_parts (merge that in here somehow, just sort of inline it, about here or so)
        # scan tree headed at node, set part (apply2all), and whenever it changed, record node in another list or dict
        # (no node will be recorded twice since these trees are disjoint and since sg is deterministic for them, assert node!=clipboard)
        # now all part settings are right, membership props (selmols etc) can be fixed when we change part value;
        # so all that's left is handling extern bonds that are now interspace bonds, i think.
        pass#####@@@@@

def clean_deleted_node(node):
    "apply this to all deleted nodes found; it's recursive, no need to use apply2all"
    try:
        #e probably they should already be killed, let's check this if we can
        if node.assy and platform.atom_debug:
            print "fyi, possible bug: clean_deleted_node hits one with an assy (thus not yet killed)", node
        node.kill() # kills members first; removes it from its part; supposedly ok to kill any node twice
    except:
        print_compact_traceback("bug, trying to ignore it: exception in clean_deleted_node: ")
    return

    ## not needed:
##def destroy_nodes_own_part(node):
##    "if node is the top node of its Part, remove that Part from node and its tree, and destroy that Part" ###k?? for who?
##    if node.part and node.part.topnode == node:
##        ...

# ==

# this might be obs before it's ever used; or maybe we'll still want it, not sure yet. [050303 comment]

from Utility import MovingNodes

class MovingBondedNodes(MovingNodes):
    """Guiding & History Object for moving a set of "bonded nodes", perhaps between parts.
    """ #e does this also assume we have the selection rules of "within one part"? Does that even matter to this class?
    # it matters to the callers, esp in whether they are in assy or part objects.
    def begin(self, nodes):
        ###e extend the nodes to include their desirable baggage (jigs, groups),
        # at least in cases of inter-part moves or spatial moves (different issues? maybe not)
        super.begin(self, nodes)
        self.externs = [] #e extern bonds from that set of nodes as a whole --
            # not needed yet unless we want to show it or use it for baggage
    def end(self):
        super.end(self) # now or later?
        #e maintain node -> part mapping; figure out which nodes moved between parts; maintain parts' nodelists etc;
        #e break interspace bonds - for each extern bond (from the moved set), check it? can we assume they end up in same part???
        # no, in general we can't, so instead, just look at all externs from each node in a new part, to see which ones to break.
        # BTW, also record these breakages in this history-object,
        # since it caused them and explained them and they'll become part of its single undo-group.
    pass

# end
