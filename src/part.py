# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

"""
part.py

Provides class Part, for all chunks and jigs in a single physical space,
together with their selection state and grouping structure (shown in the model tree).

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
from assembly import SELWHAT_CHUNKS, SELWHAT_ATOMS # can't yet import class assembly -- recursive import problem; do it at runtime


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
    as the chunks/jigs they contain); each Part has a toplevel node self.topnode,
    and a reference to the shared (per-assy) clipboard to use, self.shelf [###k].
    """
    def __init__(self, assy, topnode):
        self.init_InvalMixin()
        self.assy = assy
        self.topnode = topnode
            # some old code refers to topnode as tree or root, but that's deprecated
            # since it doesn't work for setting the value (it causes bugs we won't detect)
            ######@@@@@@ so change all uses of that...
        self.nodecount = 0 # doesn't yet include topnode
        self.add(topnode)
        # for now:
        from assembly import assembly
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
                
        # movie ID, for future use. [bruce 050324 commenting out movieID until it's used; strategy for this will change, anyway.]
        ## self.movieID=0
        # ppa = previous picked atoms. ###@@@ not sure per-part; should reset when change mode or part
        self.ppa2 = self.ppa3 = None
        
        ### Some information needed for the simulation or coming from mmp file
        ## self.temperature = 300 # for now this is an attr of assy
        ## self.waals = None ## bruce 050325 removed since nowhere used

        if platform.atom_debug:
            print "atom_debug: fyi: created Part:", self

        return # from Part.__init__

    def __repr__(self):
        classname = self.__class__.__name__
        try:
            topnodename = "%r" % self.topnode.name
        except:
            topnodename = "<topnode??>"
        return "<%s %#x %s (%d nodes)>" % (classname, id(self), topnodename, self.nodecount)

    # == updaters (###e refile??)

    def gl_update(self):
        "update whatever glpane is showing this part (more than one, if necessary)"
        self.assy.o.gl_update()
    
    # == membership maintenance

    # Note about selection of nodes moving between parts:
    # when nodes are removed or added to parts, we ensure they (or their atoms) are not picked,
    # so that we needn't worry about updating selatoms, selmols, or current selection group;
    # this also seems best in terms of the UI. But note that it's not enough, if .part revision
    # follows tree revision, since picked nodes control selection group using tree structure alone.

    def add(self, node):
        if node.part == self:
            # this is normal, e.g. in ensure_one_part, so don't complain
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
            self.invalidate_attrs(['molecules'], skip = ['natoms']) # this also invals bbox, center
                #e or we could append node to self.molecules... but I doubt that's worthwhile ###@@@
            self.adjust_natoms( len(node.atoms)) 
        # note that node is not added to any comprehensive list of nodes; in fact, we don't have one.
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
            self.invalidate_attrs(['molecules'], skip = ['natoms']) # this also invals bbox, center
            self.adjust_natoms(- len(node.atoms))
        self.nodecount -= 1
        node.part = None
        if self.topnode == node:
            self.topnode = None #k can this happen when any nodes are left??? if so, is it bad?
            if platform.atom_debug:
                print "atom_debug: fyi: topnode leaves part, %d nodes remain" % self.nodecount
            # it can happen when I drag a Group out of clipboard: "atom_debug: fyi: topnode leaves part, 2 nodes remain"
            # and it doesn't seem to be bad (the other 2 nodes were pulled out soon).
        if self.nodecount <= 0:
            assert self.nodecount == 0
            assert not self.topnode
            self.destroy()
        return

    def destroy(self):
        "forget everything, let all storage be reclaimed; only valid if we have no nodes left" # implem is a guess
        if platform.atom_debug:
            print "atom_debug: fyi: destroying part", self
        assert self.nodecount == 0, "can't destroy a Part which still has nodes" # esp. since it doesn't have a list of them!
            # actually it could scan self.assy.root to find them... but for now, we'll enforce this anyway.
        ## self.invalidate_all_attrs() # not needed
        for attr in self.__dict__.keys():
            delattr(self,attr) # is this safe, in arb order of attrs??
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
        print_compact_stack("_get_tree is deprecated: ")
        return self.topnode

    def _get_root(self): #k needed?
        print_compact_stack("_get_root is deprecated: ")
        return self.topnode
    
    # == properties that might be overridden by subclasses
    
    def immortal(self):
        """Should this Part be undeletable from the UI (by cut or delete operations)?
        When true, delete will delete its members (leaving it empty but with its topnode still present),
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
    assy_attrs_review = ['shelf', 'current_movie']
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

    _inputs_for_molecules = [] # only invalidated directly #####@@@@@ need to do it in any other places too?
    def _recompute_molecules(self):
        "recompute self.molecules as a list of this part's chunks, IN ARBITRARY AND NONDETERMINISTIC ORDER."
        self.molecules = 333 # not a sequence - detect bug of touching or using this during this method
        seen = {} # values will be new list of mols
        def func(n):
            "run this exactly once on all molecules that properly belong in this assy"
            if isinstance(n, molecule):
                # check for duplicates (mol at two places in tree) using a dict, whose values accumulate our mols list
                if seen.get(id(n)):
                    print "bug: some chunk occurs twice in assy.tree; semi-tolerated but not fixed"
                    return # from func only
                seen[id(n)] = n
            return # from func only
        self.topnode.apply2all( func)
        self.molecules = seen.values()
            # warning: not in the same order as they are in the tree!
            # even if it was, it might elsewhere be incrementally updated.
        return

    def nodes_in_mmpfile_order(self, nodeclass = None): #bruce 050325 to help with movie writing; might not be needed
        """Return a list of leaf nodes in this part (only of the given class, if provided)
        in the same order as they appear in its nodetree (depth first),
        which should be the same order they'd be written into an mmp file,
        unless something reorders them first (as happens for certain jigs
        in workaround_for_bug_296, as of 050325).
        See also _recompute_alist.
        """
        res = []
        def func(n):
            if not nodeclass or isinstance(n, nodeclass):
                res.append(n)
            return # from func only
        self.topnode.apply2all( func)
        return res

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
        self.invalidate_attrs(['bbox','center'])
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
        """Recompute self.alist, a list of all atoms in this Part, in the same order in which they
        were read from, or would be written to, an mmp file --
        namely, tree order for chunks, atom.key order within chunks.
        See also nodes_in_mmpfile_order.
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
        self.topnode.apply2all( func_alist)
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
        self.topnode.apply2all( func_selmols)
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
        self.topnode.apply2all( func_selatoms)
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
        ## not needed since done in changed_members:
        ## self.changed() #bruce 041118
##        self.bbox.merge(mol.bbox) # [see also computeBoundingBox -- bruce 050202 comment]
##        self.center = self.bbox.center()
##        self.molecules += [mol]
        self.ensure_toplevel_group() # need if, e.g., we use Build mode to add to a clipboard item
        self.topnode.addchild(mol)
            #bruce 050202 comment: if you don't want this location for the added mol,
            # just call mol.moveto when you're done, like fileIO does.   
        ## done in addchild->changed_dad->inherit_part->Part.add:
        ## self.invalidate_attrs(['natoms','molecules']) # this also invals bbox and center, via molecules
        
        #bruce 050321 disabling the following debug code, since not yet ok for all uses of _readmmp;
        # btw does readmmp even need to call addmol anymore??
        #bruce 050322 now readmmp doesn't call addmol so I'll try reenabling this:
        if 1 and platform.atom_debug:
            self.assy.checkparts()

    def ensure_toplevel_group(self): #bruce 050228, 050309
        "make sure this Part's toplevel node is a Group, by Grouping it if not."
        assert self.topnode
        if not self.topnode.is_group():
            # to do this correctly, I think we have to know that we're a "clipboard item";
            # this implem might work even if we permit Groups of clipboard items someday
            old_top = self.topnode
            name = self.assy.name_autogrouped_nodes_for_clipboard( [old_top])
            # beginning of section during which assy's Part structure is invalid
            self.topnode = Group(name, self.assy, None)
            self.add(self.topnode)
            # now put the new Group into the node tree in place of old_top
            old_top.addsibling(self.topnode)
            self.topnode.addchild(old_top) # do this last, since it makes old_top forget its old location
            # now fix our assy's current selection group if it used to be old_top,
            # but without any of the usual effects from "selgroup changed"
            # (since in a sense it didn't).
            self.assy.fyi_part_topnode_changed(old_top, self.topnode)
            # end of section during which assy's Part structure is invalid
            if platform.atom_debug:
                self.assy.checkparts()
        return
    
    # ==
    
    def draw(self, win): ###@@@ win arg, unused, should be renamed or removed
        self.topnode.draw(self.o, self.o.display)

    def draw_text_label(self, glpane):
        "#doc; called from GLPane.paintGL just after it calls mode.Draw()"
        # caller catches exceptions, so we don't have to bother
        text = self.glpane_text()
        if text:
            # code from GLPane.drawarrow
            glDisable(GL_LIGHTING)
            glDisable(GL_DEPTH_TEST)
            glPushMatrix()
            font = QFont(QString("Helvetica"), 24, QFont.Bold)
            glpane.qglColor(Qt.red) # this needs to be impossible to miss -- not nice-looking!
                #e tho it might be better to pick one of several bright colors
                # by hashing the partname, so as to change the color when the part changes.
            # this version of renderText uses window coords (0,0 at upper left)
            # rather than model coords (but I'm not sure what point on the string-image
            # we're setting the location of here -- guessing it's bottom-left corner):
            glpane.renderText(25,40, QString(text), font)
            glPopMatrix()
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            return

    def glpane_text(self):
        return "" # default implem, subclasses might override this
        
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
        self.topnode.unpick()
        # before assy/part split, this was root, i.e. assy.tree and assy.shelf

    # for debugging
    def prin(self):
        for a in self.selatoms.itervalues():
            a.prin()
    
    # == #####@@@@@ cut/copy/paste/kill will all be revised to handle bonds better (copy or break them as appropriate)
    # incl jig-atom connections too
    
    # bruce 050131/050201 revised these Cut and Copy methods to fix some Alpha bugs;
    # they need further review after Alpha, and probably could use some merging. ###@@@
    # See also assy.kill (Delete operation).
    
    def cut(self):
        eh = begin_event_handler("Cut") # bruce ca. 050307; stub for future undo work; experimental
        center_these = []
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
            if self.immortal() and self.topnode.picked:
                ###@@@ design note: this is an issue for the partgroup but not for clips... what's the story?
                ### Answer: some parts can be deleted by being entirely cut (top node too) or killed, others can't.
                ### This is not a properly of the node, so much as of the Part, I think.... not clear since 1-1 corr.
                ### but i'll go with that guess. immortal parts are the ones that can't be killed in the UI.
                
                #bruce 050201 to fix catchall bug 360's "Additional Comments From ninad@nanorex.com  2005-02-02 00:36":
                # don't let assy.tree itself be cut; if that's requested, just cut all its members instead.
                # (No such restriction will be required for assy.copy, even when it copies entire groups.)
                self.topnode.unpick_top()
                ## self.w.history.message(redmsg("Can't cut the entire Part -- cutting its members instead.")) #bruce 050201
                ###@@@ following should use description_for_history, but so far there's only one such Part so it doesn't matter yet
                self.w.history.message("Can't cut the entire Part; copying its toplevel Group, cutting its members.") #bruce 050201
                # new code to handle this case [bruce 050201]
                self.topnode.apply2picked(lambda(x): x.moveto(new))
                use = new
                use.name = self.topnode.name # not copying any other properties of the Group (if it has any)
                new = Group(gensym("Copy"), self.assy, None)
                new.addchild(use)
            else:
                self.topnode.apply2picked(lambda(x): x.moveto(new))
                # bruce 050131 inference from recalled bug report:
                # this must fail in some way that addchild handles, or tolerate jigs/groups but shouldn't;
                # one difference is that for chunks it would leave them in assy.molecules whereas copy would not;
                # guess: that last effect (and the .pick we used to do) might be the most likely cause of some bugs --
                # like bug 278! Because findpick (etc) uses assy.molecules. So I fixed this with sanitize_for_clipboard, below.
                # [later, 050307: replaced that with update_parts.]

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
                    self.shelf.addchild(ob) # add new member(s) to the clipboard [incl. Groups, jigs -- won't be pastable]
                    # If the new member is a molecule, move it to the center of its space --
                    # but not yet, since it messes up break_interpart_bonds which we'll do later!
                    # This caused bug 452 item 18.
                    # Doing the centering later is a temporary fix, should not be necessary,
                    # since the better fix is for breaking a bond to not care if its endpoint coords make sense.
                    # (That is, to reposition the singlets from scratch, not based on the existing bond.)
                    # [bruce 050321]
                    if isinstance(ob, molecule):
                        center_these.append(ob) ## was: ob.move(-ob.center)
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
            for ob in center_these: #bruce 050321
                if ob.is_top_of_selection_group(): # should be always True, but check to be safe
                    ob.move(-ob.center)
                elif platform.atom_debug:
                    print "atom_debug: bug? mol we should center no longer is_top_of_selection_group", ob
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
        # x is each node in the tree that is picked. [bruce 050201 comment: it's ok if self.topnode is picked.]
        # [bruce 050131 comments (not changing it in spite of bugs):
        #  the x's might be chunks, jigs, groups... but maybe not all are supported for copy.
        #  In fact, Group.copy returns 0 and Jig.copy returns None, and addchild tolerates that
        #  and does nothing!!
        #  About chunk.copy: it sets numol.assy but doesn't add it to assy,
        #  and it sets numol.dad but doesn't add it to dad's members -- so we do that immediately
        #  in addchild. So we end up with a members list of copied chunks from assy.tree.]
        self.topnode.apply2picked(lambda(x): new.addchild(x.copy(None))) #bruce 050215 changed mol.copy arg from new to None

        # unlike for cut, no self.changed() should be needed
        
        if new.members:
            nshelf_before = len(self.shelf.members) #bruce 050201
            for ob in new.members[:]:
                # [bruce 050215 copying that members list, to fix bug 360 comment #6 (item 5),
                # which I introduced in Alpha-2 by making addchild remove ob from its prior home,
                # thus modifying new.members during this loop]
                ## no longer needed, 050309:
                ## self.sanitize_for_clipboard(ob) # not needed on 050131 but might be needed soon, and harmless
                self.shelf.addchild(ob) # add new member(s) to the clipboard
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
        self.assy.update_parts() # stub, 050308; overkill! should just apply to the new shelf items. ####@@@@ 
        self.w.win_update()
        return

    def break_interpart_bonds(self): ###@@@ move elsewhere in method order? review, implem for jigs
        """Break all bonds between nodes in this part and nodes in other parts;
        jig-atom connections count as bonds [but might not be handled correctly as of 050308].
        #e In future we might optimize this and only do it for specific node-trees.
        """
        # Note: this implem assumes that the nodes in self are exactly the node-tree under self.topnode.
        # As of 050309 this is always true (after update_parts runs), but might not be required except here.
        self.topnode.apply2all( lambda node: node.break_interpart_bonds() )
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
        # (previously used to decide whether to kill all picked nodes in self.topnode)
        # since selected jigs no longer force selwhat to be 2.
        # (Maybe they never did, but my guess is they did; anyway I think they shouldn't.)
        # self.changed() is not needed since removing Group members should do it (I think),
        # and would be wrong here if nothing was selected.
        if self.immortal():
            self.topnode.unpick_top() #bruce 050201: prevent deletion of entire part (no msg needed)
        self.topnode.apply2picked(lambda o: o.kill())
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
    
    def Hide(self):
        "Hide all selected chunks and jigs"
        self.topnode.apply2picked(lambda x: x.hide())
        self.w.win_update()

    def Unhide(self):
        "Unhide all selected chunks and jigs"
        self.topnode.apply2picked(lambda x: x.unhide())
        self.w.win_update()

    ##bruce 050317 removing Bond and Unbond since no longer user accessible
    ## and probably unsafe anyway (no valence maintenance) and obsolete.
    ## They used to be menu commands. (BTW Bond is now also the name of a class.)
    ## But the code can stay to remind us we'll need something like Unbond
    ## for any set of selected atoms, sometime.
##    #bond atoms (cheap hack) #e is still used? should it be more accessible?
##    def Bond(self):
##        if not self.selatoms: return
##        aa=self.selatoms.values()
##        if len(aa)==2:
##            self.changed()
##            aa[0].molecule.bond(aa[0], aa[1])
##            #bruce 041028 bugfix: bring following lines inside the 'if'
##            aa[0].molecule.changeapp(0)
##            aa[1].molecule.changeapp(0)
##            self.o.gl_update()
##
##    #unbond atoms (cheap hack)
##    #bruce 050223 revised in minor ways; didn't test since it's not user-accessible now.
##    # BTW we could add this for all bonds between selected atoms,
##    # per recent Delete Bonds discussion.
##    def Unbond(self):
##        if not self.selatoms: return
##        aa=self.selatoms.values()
##        if len(aa)==2:
##            self.changed()
##            #bruce 041028 bugfix: add [:] to copy following lists,
##            # since bust will modify them during the iteration
##            for b1 in aa[0].bonds[:]:
##                for b2 in aa[1].bonds[:]:
##                    if b1 == b2:
##                        b1.bust()
##                        break #bruce 050223 precaution
##            self.o.gl_update()

    #stretch a molecule
    def Stretch(self):
        if not self.selmols:
            self.w.history.message(redmsg("no selected chunks to stretch")) #bruce 050131
            return
        self.changed()
        for m in self.selmols:
            m.stretch(1.1)
        self.o.gl_update()
        
        # Added history message.  Mark 050413.
        from platform import fix_plurals
        info = fix_plurals( "stretched %d chunk(s)" % len(self.selmols))
        self.w.history.message( info)

    #invert a chunk
    def Invert(self):
        '''Invert the atoms of the selected chunk(s)'''
        if not self.selmols:
            self.w.history.message(redmsg("no selected chunks to invert"))
            return
        self.changed()
        for m in self.selmols:
            m.stretch(-1.0)
        self.o.gl_update()
        
        from platform import fix_plurals
        info = fix_plurals( "inverted %d chunk(s)" % len(self.selmols))
        self.w.history.message( info)
        
    #merge selected molecules together  ###@@@ no update -- does caller do it?? [bruce 050223]
    def merge(self):
        #mark 050411 changed name from weld to merge (Bug 515)
        #bruce 050131 comment: might now be safe for clipboard items
        # since all selection is now forced to be in the same one;
        # this is mostly academic since there's no pleasing way to use it on them,
        # though it's theoretically possible (since Groups can be cut and maybe copied).
        if len(self.selmols) < 2:
            self.w.history.message(redmsg("Need two or more selected chunks to merge")) #bruce 050131
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

    # == jig makers
    
    def makeRotaryMotor(self, sightline):
        """Creates a Rotary Motor connected to the selected atoms.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m = RotaryMotor(self.assy)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Rotary Motory Dialog.
            del(m) #bruce comment 050223: this statement has no effect.
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addchild(m)
        self.unpickatoms()
      
    def makeLinearMotor(self, sightline):
        """Creates a Linear Motor connected to the selected atoms.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m = LinearMotor(self.assy)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Linear Motory Dialog.
            del(m) #bruce comment 050223: this statement has no effect.
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addchild(m)
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
        m = Ground(self.assy, self.selatoms.values())
        mol = self.selatoms.values()[0].molecule
        mol.dad.addchild(m)
        self.unpickatoms()

    def makestat(self):
        """Attaches a Langevin thermostat to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m = Stat(self.assy, self.selatoms.values())
        m.atoms[0].molecule.dad.addchild(m) #bruce 050210 replaced obs .mol attr
        self.unpickatoms()
        
    def makethermo(self):
        """Attaches a thermometer to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m = Thermo(self.assy, self.selatoms.values())
        m.atoms[0].molecule.dad.addchild(m) #bruce 050210 replaced obs .mol attr
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
            numol = molecule(self.assy, gensym(mol.name + "-frag"))
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
            numol = molecule(self.assy, gensym(mol.name + "-frag"))
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

    def resetAtomsDisplay(self):
        """Resets the display mode for each atom in the selected chunks 
        to default display mode.
        Returns the total number of atoms that had their display setting reset.
        """
        n = 0
        for chunk in self.selmols:
            n += chunk.set_atoms_display(diDEFAULT)
        if n: self.changed()
        return n

    def showInvisibleAtoms(self):
        """Resets the display mode for each invisible (diINVISIBLE) atom in the 
        selected chunks to default display mode.
        Returns the total number of invisible atoms that had their display setting reset.
        """
        n = 0
        for chunk in self.selmols:
            n += chunk.show_invisible_atoms()
        if n: self.changed()
        return n

    ###e refile these new methods:

    def writemmpfile(self, filename):
        from fileIO import writemmpfile_part
        writemmpfile_part( self, filename)

    def selection(self): #bruce 050404 experimental feature for initial use in Minimize Selection
        "return an object which represents the contents of the current selection, independently of part attrs... how long valid??"
        # the idea is that this is a snapshot of selection even if it changes
        # but it's not clear how valid it is after the part contents itself starts changing...
        # so don't worry about this yet, consider it part of the experiment...
        return Selection( self, self.selatoms, self.selmols )
        
    # end of class Part

# subclasses of Part

class MainPart(Part):
    def immortal(self): return True
    def location_name(self):
        return "main part"
    def movie_suffix(self):
        "what suffix should we use in movie filenames? None means don't permit making them."
        return ""
    pass

class ClipboardItemPart(Part):
    def glpane_text(self):
        #e abbreviate long names...
        return "%s (%s)" % (self.topnode.name, self.location_name())
    def location_name(self):
        return "clipboard item %d" % ( self.clipboard_item_number(), )
    def clipboard_item_number(self):
        "this can be different every time..."
        return self.assy.shelf.members.index(self.topnode) + 1
    def movie_suffix(self):
        "what suffix should we use in movie filenames? None means don't permit making them."
        ###e stub -- not a good choice, since it changes and thus is reused...
        # it might be better to assign serial numbers to each newly made Part that needs one for this purpose...
        # actually I should store part numbers in the file, and assign new ones as 1 + max of existing ones in shelf.
        # then use them in dflt topnode name and in glpane text (unless redundant) and in this movie suffix.
        # but this stub will work for now. Would it be better to just return ""? Not sure. Probably not.
        return "-%d" % ( self.clipboard_item_number(), )
    pass

# other

class Selection: #bruce 050404 experimental feature for initial use in Minimize Selection
    def __init__(self, part, selatoms, selmols): #e revise init args
        self.part = part
        self.topnode = part.topnode # might change...
        self.selatoms = dict(selatoms) # copy the dict
        self.selmols = list(selmols) # copy the list
        assert not (self.selatoms and self.selmols) #e could this change? try not to depend on it
        #e jigs?
        return
    def nonempty(self): #e make this the object's boolean value too?
        # assume that each selmol has some real atoms, not just singlets! Should always be true.
        return self.selatoms or self.selmols
    def atomslist(self):
        "return a list of all selected real atoms, whether selected as atoms or in selected chunks; no singlets or jigs"
        #e memoize this!
        if self.selmols:
            res = dict(self.selatoms) # dict from atom keys to atoms
            for mol in self.selmols:
                # we'll add real atoms and singlets, then remove singlets
                # (probably faster than only adding real atoms, since .update is one bytecode
                #  and (for large mols) most atoms are not singlets)
                res.update(mol.atoms)
                for s in mol.singlets:
                    del res[s.key]
        else:
            res = self.selatoms
        items = res.items()
        items.sort() # sort by atom key; might not be needed
        return [atom for key, atom in items]
    pass # end of class Selection

# ==

##def process_changed_dads_fix_parts():
##    """Grab (and reset) the global set of nodes with possibly-changed dads,
##    and use this info (and our memory from prior times we ran??)
##    to fix Parts of all affected nodes.
##    If this should someday coexist with other things to do with the
##    same set of nodes with changed dads (at the same time, since it's reset),
##    then how these interact is unclear; probably we'll be put into an order
##    or nesting with those, become methods of an object, and not do our own grab/reset.
##    """
##    # [Try to be correct even if there are multiple assys and nodes can move between them!
##    #  I don't know if we'll achieve this, and it's not urgent.]
##    nodes = changed.dads.grab_and_reset_changed_objects()
##    ##e future: also know their old dads, so we can see if the dads really changed. Not very important, not done yet.
##    # A node with a new dad might have a new Part, and any of its children might have one.
##    # By the time we run, they all already have their new dad, so we can figure out what Part they and kids should have.
##    # So one easy scheme is just to invalidate the Part for all nodes that might have it wrong. #####@@@@@ not sure...
##    # And then, when done, recompute them all? We do want to *actually finish* moving nodes from their old to new Parts,
##    # and when that's done, checking them all for external bonds that have become interspace bonds and need to be broken
##    # or (maybe) need to induce new Parts to merge.
##    for node in topmost_nodes(nodes):
##        # this includes nodes that got moved, but perhaps also some "deleted"
##        # nodes no longer in the tree at all. This might be a good place to destroy
##        # the latter kind! But to avoid bugs, it's safer to do that later (or never).
##        # But we detect them right away, to avoid bugs in other methods like find_selection_group.
##        if not node.has_home():
##            # actually we need to remove them from their Parts, at least, right away.
##            clean_deleted_node( node)
##                #e (this would be bad if we wanted to keep it around for undo-related purposes)
##            continue
##        sg = node.find_selection_group()
##        ###e next steps: ######@@@@@@ this is where i am, 050303 10:09pm
##        # figure out part, make it if nec, see fix_parts (merge that in here somehow, just sort of inline it, about here or so)
##        # scan tree headed at node, set part (apply2all), and whenever it changed, record node in another list or dict
##        # (no node will be recorded twice since these trees are disjoint and since sg is deterministic for them, assert node!=clipboard)
##        # now all part settings are right, membership props (selmols etc) can be fixed when we change part value;
##        # so all that's left is handling extern bonds that are now interspace bonds, i think.
##        pass#####@@@@@
##
##def clean_deleted_node(node):
##    "apply this to all deleted nodes found; it's recursive, no need to use apply2all"
##    try:
##        #e probably they should already be killed, let's check this if we can
##        if node.assy and platform.atom_debug:
##            print "fyi, possible bug: clean_deleted_node hits one with an assy (thus not yet killed)", node
##        node.kill() # kills members first; removes it from its part; supposedly ok to kill any node twice
##    except:
##        print_compact_traceback("bug, trying to ignore it: exception in clean_deleted_node: ")
##    return
##
##    ## not needed:
####def destroy_nodes_own_part(node):
####    "if node is the top node of its Part, remove that Part from node and its tree, and destroy that Part" ###k?? for who?
####    if node.part and node.part.topnode == node:
####        ...
##
### ==
##
### this might be obs before it's ever used; or maybe we'll still want it, not sure yet. [050303 comment]
##
##from Utility import MovingNodes
##
##class MovingBondedNodes(MovingNodes):
##    """Guiding & History Object for moving a set of "bonded nodes", perhaps between parts.
##    """ #e does this also assume we have the selection rules of "within one part"? Does that even matter to this class?
##    # it matters to the callers, esp in whether they are in assy or part objects.
##    def begin(self, nodes):
##        ###e extend the nodes to include their desirable baggage (jigs, groups),
##        # at least in cases of inter-part moves or spatial moves (different issues? maybe not)
##        super.begin(self, nodes)
##        self.externs = [] #e extern bonds from that set of nodes as a whole --
##            # not needed yet unless we want to show it or use it for baggage
##    def end(self):
##        super.end(self) # now or later?
##        #e maintain node -> part mapping; figure out which nodes moved between parts; maintain parts' nodelists etc;
##        #e break interspace bonds - for each extern bond (from the moved set), check it? can we assume they end up in same part???
##        # no, in general we can't, so instead, just look at all externs from each node in a new part, to see which ones to break.
##        # BTW, also record these breakages in this history-object,
##        # since it caused them and explained them and they'll become part of its single undo-group.
##    pass
##
### end