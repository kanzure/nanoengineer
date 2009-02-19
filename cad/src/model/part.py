# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
part.py -- class Part, for all chunks and jigs in a single physical space,
together with their selection state and grouping structure (shown in the
model tree).

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

see assembly.py docstring, some of which is really about this module. ###@@@ revise

==

This module also contains a lot of code for specific operations on sets of molecules,
which are all in the current part. Some of this code might ideally be moved to some
other file. [As of 050507, much of that has now been moved.]

==

History:

Split out of assembly.py (the file, and more importantly the class)
by bruce 050222. The Part/assembly distinction was introduced by bruce 050222
(though some of its functionality was anticipated by the "current selection group"
introduced earlier, just before Alpha-1). [I also rewrote this entire docstring then.]

The Part/assembly distinction is unfinished, particularly in how it
relates to some modes and to movie files.

Prior history of assembly.py (and thus of much code in this file) unclear;
assembly.py was almost certainly originated by Josh.

bruce 050507 moved various methods out of this file, into more appropriate
smaller files, some existing (jigs.py) and some new (ops_*.py).

bruce 050513 replaced some == with 'is' and != with 'is not',
to avoid __getattr__ on __xxx__ attrs in python objects.
"""

from utilities import debug_flags

from utilities.debug import print_compact_traceback, print_compact_stack
from utilities.Log import redmsg

from utilities.constants import diINVISIBLE
from utilities.constants import diDEFAULT
from utilities.constants import SELWHAT_CHUNKS, SELWHAT_ATOMS

from utilities.prefs_constants import levelOfDetail_prefs_key
from utilities.prefs_constants import startup_GLPane_scale_prefs_key
from utilities.prefs_constants import indicateOverlappingAtoms_prefs_key


from geometry.VQT import V, Q
from geometry.BoundingBox import BBox
from geometry.NeighborhoodGenerator import NeighborhoodGenerator


from foundation.Utility import Node
from foundation.Group import Group
from foundation.Assembly_API import Assembly_API
from foundation.node_indices import fix_one_or_complain
from foundation.inval import InvalMixin
from foundation.state_utils import StateMixin
from foundation.state_constants import S_REF, S_DATA, S_PARENT, S_CHILD

import foundation.env as env


from graphics.model_drawing.PartDrawer import PartDrawer


from model.NamedView import NamedView
from model.chunk import Chunk
from model.jigs import Jig


from operations.jigmakers_Mixin import jigmakers_Mixin
from operations.ops_atoms import ops_atoms_Mixin
from operations.ops_connected import ops_connected_Mixin
from operations.ops_copy import ops_copy_Mixin
from operations.ops_motion import ops_motion_Mixin
from operations.ops_rechunk import ops_rechunk_Mixin
from operations.ops_select import ops_select_Mixin


from dna.operations.ops_pam import ops_pam_Mixin

# ==

# number of atoms for detail level 0
HUGE_MODEL = 40000
# number of atoms for detail level 1
LARGE_MODEL = 5000

debug_parts = False # set this to True in a debugger, to enable some print statements, etc

debug_1855 = False # DO NOT COMMIT WITH TRUE [bruce 060415]

# ==

# Part_drawing_frame, for use in Part._drawing_frame [bruce 090218]

# (todo: better name? put in its own file?)

# WARNING: The present scheme for Part._drawing_frame would not work
# if multiple threads could draw one Part, or if complex objects in
# a part (e.g. chunks) might be drawn twice in one frame. See comments
# near its use in Chunk.draw for ways we might need to generalize it.
# [bruce 070928/090218]

class Part_drawing_frame_superclass:
    """
    """
    # repeated_bonds_dict lets bonds (or ExternalBondSets) avoid being
    # drawn twice. It maps id(bond) to bond (for any Bond or ExternalBondSet)
    # for all bonds that might otherwise be drawn twice. It is public
    # for use and modification by anything that draws bonds, but only
    # during a single draw call (or a single draw of a subset of the model).
    #
    # Note that OpenGL drawing (draw methods) uses it only for external
    # bonds, but POV-Ray drawing (writepov methods) uses it for all
    # bonds; this is ok even if some writepov methods someday call some
    # draw methods.
    repeated_bonds_dict = None

    # These are for implementing optional indicators about overlapping atoms.
    _f_state_for_indicate_overlapping_atoms = None
    indicate_overlapping_atoms = False

    pass

class Part_drawing_frame(Part_drawing_frame_superclass):
    """
    One of these is created whenever drawing all or part of a Part,
    once per "drawing frame" (e.g. call of Part.draw()).

    It holds attributes needed during a single draw call
    (or, a draw of a portion of the model).

    See superclass code comments for documentation of attributes.

    For more info, see docstring of Part.before_drawing_model.
    """
    def __init__(self):
        
        self.repeated_bonds_dict = {}

        # Note: this env reference may cause undesirable usage tracking,
        # depending on when it occurs. This should cause no harm --
        # only a needless display list remake when the pref is changed.
        self.indicate_overlapping_atoms = \
            env.prefs[indicateOverlappingAtoms_prefs_key]

        if self.indicate_overlapping_atoms:
            TOO_CLOSE = 0.3 # stub, guess; needs to not be true even for
                # bonded atoms, or atoms and their bondpoints,
                # but big enough to catch "visually hard to separate" atoms.
                # (1.0 is far too large; 0.1 is ok but too small to be best.)
                # It would be much better to let this depend on the elements
                # and whether they're bonded, and not hard to implement
                # (each atom could be asked whether it's too close to each
                #  other one, and take all this into account). If we do that,
                # this value should be the largest tolerance for any pair
                # of atoms, and the code that uses this NeighborhoodGenerator
                # should do more filtering on the results. [bruce 080411]
            self._f_state_for_indicate_overlapping_atoms = \
                NeighborhoodGenerator( [], TOO_CLOSE, include_singlets = True )
        return
    
    pass

class fake_Part_drawing_frame(Part_drawing_frame_superclass):
    """
    Use one of these "in between draw calls" to avoid or mitigate bugs.
    """
    # todo: print a warning whenever our methods/attrs are used,
    # or create self on demand and print a warning then.
    def __init__(self):
        print_compact_stack(
            "warning: fake_Part_drawing_frame is being instantiated: " )
        # done in superclass: self.repeated_bonds_dict = None
            # This is necessary to remove any chance of self surviving
            # for more than one draw of one object (since using an actual
            # dict then would make bonds sometimes fail to be drawn).
            # Client code must tolerate this value.
    pass
        
# == 

class Part( jigmakers_Mixin, InvalMixin, StateMixin,
            ops_atoms_Mixin, ops_pam_Mixin, ops_connected_Mixin, ops_copy_Mixin,
            ops_motion_Mixin, ops_rechunk_Mixin, ops_select_Mixin,
            object # fyi; redundant with InstanceLike inherited via StateMixin
            ):
    """
    One Part object is created to hold any set of chunks and jigs whose
    coordinates are intended to lie in the same physical space.
    When new clipboard items come into being, new Parts are created as needed
    to hold them; and they should be destroyed when those clipboard items
    no longer exist as such (even if the chunks inside them still exist in
    some other Part).
       Note that parts are not Nodes (or at least, they are not part of the same node-tree
    as the chunks/jigs they contain); each Part has a toplevel node self.topnode,
    and a reference to its assy, used for (e.g.) finding a reference to the shared
    (per-assy) clipboard to use, self.shelf.
    """

    # default values for some instance variables
    name = "" #bruce 060227 moved this into class and made it "" rather than None, for simplicity of _s_attr defaultval code
        # this is [someday? now?] set to any name autogenerated for our topnode,
        # so it can be reused if necessary (if our topnode changes a couple times in a row)
        # rather than autogenerating another name.
        # It would also be useful if there was a Part Tree Widget...
    alive = False # set to True at end of __init__, and again to False if we're destroyed(??#k)
    _drawer = None

    # state decls (for attrs set in __init__) [bruce 060224]
    _s_attr_name = S_DATA
    _s_attr_topnode = S_PARENT
    _s_attr_nodecount = S_DATA
    _s_attr_homeView = S_CHILD
    _s_attr_lastView = S_CHILD
    ## not true, i think: _s_categorize_homeView = 'view' # [bruce 060227]
    _s_categorize_lastView = 'view' # [bruce 060227]
    _s_attr_ppa2 = S_REF
    _s_attr_ppa3 = S_REF
    _s_attr_ppm = S_REF
    _s_attr_alive = S_DATA # needed since the part can be destroyed, which sets alive to False

    def _undo_update_always(self): #bruce 060224
        """
        This is run on every Part still around after an Undo or Redo op, whether or not it was modified by that op.
        """
        # (though to be honest, that's due to a kluge, as of 060224 -- it won't yet run this on any other class!)
        attrs = self.invalidatable_attrs()
        if debug_1855:
            print "debug_1855: part %r _undo_update_always will inval %r" % (self, attrs,)
            # this looks ok
        self.invalidate_attrs( attrs) # especially selmols, selatoms, and molecules, but i guess all of them matter
            ###e should InvalMixin *always* do this? (unless overridden somehow?) guess: not quite.
        # don't call this, it can't be allowed to exist (I think):
        ## StateMixin._undo_update_always(self)
        return

    def __init__(self, assy, topnode):
        self.init_InvalMixin()
        self.assy = assy
        self.topnode = topnode
            # some old code refers to topnode as tree or root, but that's deprecated
            # since it doesn't work for setting the value (it causes bugs we won't detect)
            # so change all uses of that... maybe I have by now? ###k
        self.nodecount = 0 # doesn't yet include topnode until we self.add it, below
        prior_part = topnode.part
        if prior_part is None:
            prior_part = topnode.prior_part #bruce 050527 new feature; also might be None
        if prior_part is not None:
            # topnode.part might be destroyed when we add topnode to ourselves,
            # so we'd better first salvage from it whatever might be useful
            # (copying its view attributes fixes bug 556 [bruce 050420])
            # [now we can also get these from topnode.prior_part if necessary;
            #  it is like .part but doesn't modify part's nodecount or stats;
            #  this is added to nodes made by copying other nodes, or Groups containing those,
            #  so that view info can generally be preserved for copies -- bruce 050527]
            self.homeView = prior_part.homeView.copy()
            self.lastView = prior_part.lastView.copy()
            # (copying its name, if we were the first ones to get to it and if it doesn't
            #  any longer need its name (since it has no topnode), might be enough
            #  to make ungroup/regroup of a clipboard item preserve an autogenerated name;
            #  I'm not 100% sure it's always a good idea, but it's worth a try, I guess;
            #  if it's bad it'll be because the part still wanted its name for some reason. [bruce 050420])
            if prior_part.name and prior_part.topnode is None:
                # steal its name
                self.name = prior_part.name
                prior_part.name = None
                del prior_part.name # save RAM (in undo archives, until undo does this itself) (not important, mainly a test, 060227)
        else:
            # HomeView and LastView -- these are per-part, are switched into
            # GLPane when its current part changes (i.e. very soon after our
            # assy's current part changes), and are written into mmp file for
            # main part, and in future for all parts.
            ###e bruce 050527 comment: would it ever be better to set these to
            # fit the content? If so, we'd have to just inval them here, since
            # most of the content is probably in nodes other than topnode,
            # which are not yet added (and we don't want to assume topnode's
            # kids will all be added, though for now this might be true --
            # not sure).

            #Default scale is usually = 10.0-- obtained from the preference
            #value for startup_GLPane_scale_prefs_key
            #@see: GLPane.__init__,
            #@see:GLPane._adjust_GLPane_scale_if_needed()
            default_scale = float(env.prefs[startup_GLPane_scale_prefs_key])
            self.homeView = NamedView(self.assy,
                                      "HomeView",
                                      default_scale,
                                      V(0,0,0),
                                      1.0,
                                      Q(1.0, 0.0, 0.0, 0.0))

            self.lastView = NamedView(self.assy,
                                      "LastView",
                                      default_scale,
                                      V(0,0,0),
                                      1.0,
                                      Q(1.0, 0.0, 0.0, 0.0))

        self.add(topnode)
        # for now:
        assert isinstance(assy, Assembly_API)
        assert isinstance(topnode, Node)

        # self._modified?? not yet needed for individual parts, but will be later.


        ##bruce 050417 zapping all Datum objects, since this will have no important effect,
        ## even when old code reads our mmp files.
        ## More info about this can be found in other comments/emails.
##        self.xy = Datum(self.assy, "XY", "plane", V(0,0,0), V(0,0,1))
##        self.yz = Datum(self.assy, "YZ", "plane", V(0,0,0), V(1,0,0))
##        self.zx = Datum(self.assy, "ZX", "plane", V(0,0,0), V(0,1,0))

        ##bruce 050418 replacing this with viewdata_members method and its caller in assy:
##        grpl1 = [self.homeView, self.lastView] ## , self.xy, self.yz, self.zx] # [note: only use of .xy, .yz, .zx as of 050417]
##        self.viewdata = Group("View Data", self.assy, None, grpl1) #bruce 050418 renamed this; not a user-visible change
##        self.viewdata.open = False


        # some attrs are recomputed as needed (see below for their _recompute_ or _get_ methods):
        # e.g. molecules, bbox, center, drawLevel, alist, selatoms, selmols

        # movie ID, for future use. [bruce 050324 commenting out movieID until it's used; strategy for this will change, anyway.]
        ## self.movieID = 0

        # ppa = previous picked atoms. ###@@@ not sure these are per-part; should reset when change mode or part
        self.ppa2 = self.ppa3 = self.ppm = None

        self.alive = True # we're not yet destroyed

        self._drawer = PartDrawer(self) #bruce 090218 refactoring

        if debug_parts:
            print "debug_parts: fyi: created Part:", self

        return # from Part.__init__

    def viewdata_members(self, i): #bruce 050418: this helps replace old assy.data for writing mmp files
        #bruce 050421: patch names for sake of saving per-Part views;
        # should be ok since names not otherwise used (I hope);
        # if not (someday), we can make copies and patch their names
        suffix = i and str(i) or ""
        self.homeView.name = "HomeView" + suffix
        self.lastView.name = "LastView" + suffix
        return [self.homeView, self.lastView]

    def __repr__(self):
        classname = self.__class__.__name__
        try:
            topnodename = "%r" % self.topnode.name
        except:
            topnodename = "<topnode??>"
        try:
            return "<%s %#x %s (%d nodes)>" % (classname, id(self), topnodename, self.nodecount)
        except:
            return "<some part, exception in its __repr__>" #bruce 050425

    # == updaters (###e refile??)

    def gl_update(self):
        """
        update whatever glpane is showing this part (more than one, if necessary)
        """
        self.assy.o.gl_update()

    # == membership maintenance

    # Note about selection of nodes moving between parts:
    # when nodes are removed from or added to parts, we ensure they (or their atoms) are not picked,
    # so that we needn't worry about updating selatoms, selmols, or current selection group;
    # this also seems best in terms of the UI. But note that it's not enough, if .part revision
    # follows tree revision, since picked nodes control selection group using tree structure alone.

    def add(self, node):
        if node.part is self:
            # this is normal, e.g. in ensure_one_part, so don't complain
            return
        if node.part is not None:
            if debug_parts:
                # this will be common
                print "debug_parts: fyi: node added to new part so removed from old part first:", node, self, node.part
            node.part.remove(node)
        assert node.part is None
        # this is a desired assertion, but make it a debug print
        # so as not to cause worse bugs: [bruce 080314]
        ## assert not node.picked # since remove did it, or it was not in a part and could not have been picked (I think!)
        if node.picked:
            msg = "\n***BUG: node.picked in %r.add(%r); clearing it to avoid more bugs" % \
                  (self, node)
            print_compact_stack( msg + ": ")
            node.picked = False # too dangerous to use node.unpick() here
            # Review: could we just make this legal, by doing
            # self.selmols_append(node) if node is a chunk?
            # (For now, instead, just have new nodes call .inherit_part
            #  before .pick. This fixed a bug in DnaLadderRailChunk.)
            # [bruce 080314 comment]
            pass
        #e should assert a mol's atoms not picked too (too slow to do it routinely; bugs in this are likely to be noticed)
        node.part = node.prior_part = self
            #bruce 050527 comment: I hope and guess this is the only place node.part is set to anything except None; need to check ###k
        self.nodecount += 1
        if isinstance(node, Chunk): ###@@@ #e better if we let the node add itself to our stats and lists, i think...
            self.invalidate_attrs(['molecules'], skip = ['natoms']) # this also invals bbox, center
                #e or we could append node to self.molecules... but I doubt that's worthwhile ###@@@
            self.adjust_natoms( len(node.atoms))
        # note that node is not added to any comprehensive list of nodes; in fact, we don't have one.
        # presumably this function is only called when node was just, or is about to be,
        # added to a nodetree in a place which puts it into this part's tree.
        # Therefore, in the absence of bugs and at the start of any user event handler,
        # self.topnode should serve as a comprehensive tree of this part's nodes.
        return

    def remove(self, node):
        """
        Remove node (a member of this part) from this part's lists and stats;
        reset node.part; DON'T look for interspace bonds yet (since this node
        and some of its neighbors might be moving to the same new part).
        Node (and its atoms, if it's a chunk) will be unpicked before the removal.
        """
        assert node.part is self
        node.unpick() # this maintains selmols if necessary
        if isinstance(node, Chunk):
            # need to unpick the atoms? [would be better to let the node itself have a method for this]
            ###@@@ (fix atom.unpick to not remake selatoms if missing, or to let this part maintain it)
            if (not self.__dict__.has_key('selatoms')) or self.selatoms:
                for atm in node.atoms.itervalues():
                    atm.unpick(filtered = False)
                        #bruce 060331 precaution: added filtered = False, to fix potential serious bugs (unconfirmed)
                        #e should optimize this by inlining and keeping selatoms test outside of loop
            self.invalidate_attrs(['molecules'], skip = ['natoms']) # this also invals bbox, center
            self.adjust_natoms(- len(node.atoms))
        self.nodecount -= 1
        node.part = None
        if self.topnode is node:
            self.topnode = None #k can this happen when any nodes are left??? if so, is it bad?
            if debug_parts:
                print "debug_parts: fyi: topnode leaves part, %d nodes remain" % self.nodecount
            # it can happen when I drag a Group out of clipboard: "debug_parts: fyi: topnode leaves part, 2 nodes remain"
            # and it doesn't seem to be bad (the other 2 nodes were pulled out soon).
        if self.nodecount <= 0:
            assert self.nodecount == 0
            assert not self.topnode
            self.destroy()
            # NOTE: since Node.part is undoable, a destroyed Part can come back
            # to life after Undo. I don't know if this is related to a newly found bug:
            # make duplex with dna updater on, undo to before that, redo, nodecount is wrong.
            # For more info see today's comment in assembly.py.
            # [bruce 080325]
        return

    def destroy_with_topnode(self): #bruce 050927; consider renaming this to destroy, and destroy to something else
        """
        destroy self.topnode and then self; assertionerror if self still has nodes after topnode is destroyed
        WARNING [060322]: This probably doesn't follow the semantics of other destroy methods (the issue is unreviewed). ###@@@
        """
        if self.topnode is not None:
            self.topnode.kill() # use kill, since Node.destroy is NIM [#e this should be fixed, might cause memory leaks]
        self.destroy()
        return

    def destroy(self): #bruce 050428 making this much more conservative for Alpha5 release and to fix bug 573
        """
        forget enough to prevent memory leaks; only valid if we have no nodes left; MUST NOT forget views!
        WARNING [060322]: This doesn't follow the semantics of other destroy methods; in particular, destroyed Parts might be revived
        later by Undo. This should be fixed by renaming this method (perhaps to kill), so we can add a real destroy method. ###@@@
        """
        #bruce 050527 added requirement (already true in current implem) that this not forget views,
        # so node.prior_part needn't prevent destroy, but can be used to retrieve default initial views for node.
        if debug_parts:
            print "debug_parts: fyi: destroying part", self
        assert self.nodecount == 0, "can't destroy a Part which still has nodes" # esp. since it doesn't have a list of them!
            # actually it could scan self.assy.root to find them... but for now, we'll enforce this anyway.
        if self.assy and self.assy.o: #e someday change this to self.glpane??
            self.assy.o.forget_part(self) # just in case we're its current part
        ## self.invalidate_all_attrs() # not needed
        self.alive = False # do this one first ###@@@ see if this can help a Movie who knows us see if we're safe... [050420]
        if self._drawer:
            self._drawer.destroy()
            del self._drawer
        if "be conservative for now, though memory leaks might result": #bruce 050428
            return
        # bruce 050428 removed the rest for now. In fact, even what we had was probably not enough to
        # prevent memory leaks, since we've never paid attention to that, so the Nodes might have them
        # (in the topnode tree, deleted earlier, or the View nodes we still have, which might get into
        #  temporary Groups in writemmp_file code and not get properly removed from those groups).
        ## BTW, bug 573 came from self.assy = None followed by __getattr__ wanting attrs from self.assy
        ## such as 'w' or 'current_selgroup_iff_valid'.
##        # set all attrs to None, including self.alive (which is otherwise True to indicate we're not yet destroyed)
##        for attr in self.__dict__.keys():
##            if not attr.startswith('_'):
##                #bruce 050420 see if this 'if' prevents Python interpreter hang
##                # when this object is later passed as argument to other code
##                # in bug 519 (though it probably won't fix the bug);
##                # before this we were perhaps deleting Python-internal attrs too,
##                # such as __dict__ and __class__!
##                if 0 and debug_flags.atom_debug:
##                    print "atom_debug: destroying part - deleting i mean resetting attr:",attr
##                ## still causes hang in movie mode:
##                ## delattr(self,attr) # is this safe, in arb order of attrs??
##                setattr(self, attr, None)
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
                if debug_flags.atom_debug:
                    print_compact_traceback("selmols_remove finds mol not in selmols (might not be a bug): ")
        return

    def adjust_natoms(self, delta):
        """
        adjust the number of atoms, if known. Useful since drawLevel depends on this and is often recomputed.
        """
        if self.__dict__.has_key('natoms'):
            self.natoms += delta
        return

    # == compatibility methods

    ###@@@ find and fix all sets of .tree or .root or .data (old name, should all be renamed now) or .viewdata (new name) or .shelf

    def _get_tree(self): #k this would run for part.tree; does that ever happen?
        print_compact_stack("_get_tree is deprecated: ")
        return self.topnode

    def _get_root(self): #k needed?
        print_compact_stack("_get_root is deprecated: ")
        return self.topnode

    # == properties that might be overridden by subclasses

    def immortal(self):
        """
        Should this Part be undeletable from the UI (by cut or delete operations)?
        When true, delete will delete its members (leaving it empty but with its topnode still present),
        and cut will cut its members and move them into a copy of its topnode, which is left still present and empty.
        [can be overridden in subclasses]
        """
        return False # simplest value used as default

    # == attributes which should be delegated to self.assy

    # attrnames to delegate to self.assy (ideally for writing as well as reading, until all using-code is upgraded)
    assy_attrs = ['w','o','mt','selwhat','win'] #bruce 071008 added 'win'
        ### TODO: add glpane, once we have it in assy and verify not already used here [bruce 071008 comment]
        # 050308: selwhat will be an official assy attribute;
        # some external code assigns to assy.selwhat directly,
        # and for now can keep doing that. Within the Part, perhaps we should
        # use a set_selwhat method if we need one, but for now we just assign
        # directly to self.assy.selwhat.
    assy_attrs_temporary = ['changed'] # tolerable, but might be better to track per-part changes, esp. re movies ###@@@
    assy_attrs_review = ['shelf', 'current_movie']
        #e in future, we'll split out our own methods for some of these, incl .changed
        #e and for others we'll edit our own methods' code to not call them on self but on self.assy (incl selwhat).
    assy_attrs_all = assy_attrs + assy_attrs_temporary + assy_attrs_review

    def __getattr__(self, attr): # in class Part
        """
        [overrides InvalMixin.__getattr__]
        """
        if attr.startswith('_'): # common case, be fast (even though it's done redundantly by InvalMixin.__getattr__)
            raise AttributeError, attr
        if attr in self.assy_attrs_all:
            # delegate to self.assy
            return getattr(self.assy, attr) ###@@@ detect error of infrecur, since assy getattr delegates to here??
        return InvalMixin.__getattr__(self, attr) # uses _get_xxx and _recompute_xxx methods

    # == attributes which should be invalidated and recomputed as needed (both inval and recompute methods follow)

    _inputs_for_molecules = [] # only invalidated directly ###@@@ need to do it in any other places too?
    def _recompute_molecules(self):
        """
        recompute self.molecules as a list of this part's chunks, IN ARBITRARY AND NONDETERMINISTIC ORDER.
        """
        self.molecules = 333 # not a sequence - detect bug of touching or using this during this method
        seen = {} # values will be new list of mols
        def func(n):
            "run this exactly once on all molecules that properly belong in this assy"
            if isinstance(n, Chunk):
                # check for duplicates (mol at two places in tree) using a dict, whose values accumulate our mols list
                if seen.get(id(n)):
                    print "bug: some chunk occurs twice in this part's topnode tree; semi-tolerated but not fixed"
                    msg = " that chunk is %r, and this part is %r, in assy %r, with topnode %r" % \
                          (n, self, self.assy, self.topnode) #bruce 080403, since this happened to tom
                    print_compact_stack(msg + ": ")
                    return # from func only
                seen[id(n)] = n
            return # from func only
        self.topnode.apply2all( func)
        self.molecules = seen.values()
            # warning: not in the same order as they are in the tree!
            # even if it was, it might elsewhere be incrementally updated.
        return

    def nodes_in_mmpfile_order(self, nodeclass = None):
        """
        Return a list of leaf nodes in this part (only of the given class, if provided)
        in the same order as they appear in its nodetree (depth first),
        which should be the same order they'd be written into an mmp file,
        unless something reorders them first (as happens for certain jigs
        in workaround_for_bug_296, as of 050325,
        but maybe not as of 051115 since workaround_for_bug_296 was removed some time ago).
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
        """
        Recompute and set the value of self.drawLevel,
        which controls the detail level of spheres used to draw atoms.
        """
        num = self.natoms # note: self.natoms must be accessed whether or not
            # its value is needed, due to limitations in InvalMixin.
            # Review: it might be good to optimize by not using InvalMixin
            # so we don't need to recompute self.natoms when it's not needed.
        lod = env.prefs[ levelOfDetail_prefs_key ] # added by mark, revised by bruce, 060215
        lod = int(lod)
        if lod > 2:
            # presume we're running old code (e.g. A7)
            # using a prefs db written by newer code (e.g. A8)
            lod = 2 # max LOD current code can handle
                # (see _NUM_SPHERE_SIZES, len(drawing_globals.sphereList))
        # now set self.drawLevel from lod
        if lod < 0:
            # -1 means "Variable based on the number of atoms in the part."
            # [bruce 060215 changed that from 3, so we can expand number of
            #  LOD levels in the future.]
            self.drawLevel = 2
            if num > LARGE_MODEL:
                self.drawLevel = 1
            if num > HUGE_MODEL:
                self.drawLevel = 0
        else:
            # High (2), medium (1) or low (0)
            self.drawLevel = lod
        return

    # == scanners (maybe not all of them?)

    def enforce_permitted_members_in_groups(self, **opts): #bruce 080319
        """
        Intended to be called after self has just been read, either
        before or after update_parts and/or the dna updater has first run
        (with appropriate options passed to distinguish those cases).

        Make sure all our groups that only permit some kinds of members
        (e.g. DnaStrandOrSegment groups)
        only have that kind of members, by ejecting non-permitted members
        to higher groups, making a new toplevel group if necessary.

        FYI: As of 080319 this just means we make sure the only members
        of a DnaStrand or DnaSegment (i.e. a DnaStrandOrSegment)
        are chunks (any subclass) and DnaMarker jigs. The dna updater,
        run later, will make sure there is a 1-1 correspondence between
        controlling markers and DnaStrandOrSegments, and (nim?) that only
        DnaLadderRailChunks are left inside DnaStrandOrSegments.
        (It may have a bug in which a DnaStrandOrSegment containing only
        an ordinary chunk with non-PAM atoms would be left in that state.)

        @param opts: options to pass to group API methods permit_as_member
                     and _f_wants_to_be_killed. As of 080319, only
                     pre_updaters is recognized, default True,
                     saying whether we're running before updaters
                     (especially the dna updater) have first been run.

        @warning: implementation is mostly in friend methods in class Node
                  and/or Group, and is intended to be simple and safe, *not* fast.
                  Therefore this is not suitable to run within the dna updater,
                  only after mmp read.

        @warning: this does not check self.topnode._f_wants_to_be_killed
                  since that is nontrivial to do safely and is probably not
                  needed at present.

        @note: this method's only purpose (and that of the friend methods
               it calls) is to clean up incorrect mmp files whose UI ops
               were not properly enforcing these rules.
        """
        assert self.topnode
        orig_topnode = self.topnode
        ejected_anything = self.topnode.is_group() and \
            self.topnode._f_move_nonpermitted_members(**opts)
        # if it ejected anything, then as a special case for being at the top,
        # ensure_toplevel_group created a group to wrap the old topnode,
        # which is what contains the ejected nodes.
        # Verify this, and if it happened, repeat once, and then
        # ungroup if it has one or no members.
        if ejected_anything != (orig_topnode is not self.topnode):
            if ejected_anything:
                print "\n***BUG: sanitize_dnagroups ejected from topnode %r " \
                      "but didn't replace it" % orig_topnode
            else:
                print "\n***BUG: sanitize_dnagroups replaced topnode %r " \
                      "with %r but didn't eject anything" % \
                      (orig_topnode, self.topnode)
            pass
        else:
            # no bug, safe to proceed
            if orig_topnode is not self.topnode:
                # repeat, but only once (all new activity should be confined
                #  within the new topnode, presumably an ordinary Group
                #  made by ensure_toplevel_part)
                ejected_anything = self.topnode.is_group() and \
                    self.topnode._f_move_nonpermitted_members(**opts)
                if ejected_anything:
                    print "\n***BUG: sanitize_dnagroups ejected from new topnode in %r" % self
                    # don't print new topnode, we don't know whether or not it changed --
                    # if this ever happens, revise to print more info
                elif not self.topnode.is_group():
                    print "\n***BUG: sanitize_dnagroups replaced topnode with a non-Group in %r" % self
                else:
                    # still no bug, safe to proceed
                    if len(self.topnode) <= 1:
                        self.topnode.ungroup() #k
                    pass
                pass
            pass
        return

    # == Bounding box methods

    ### BUG: these only consider chunks (self.molecules) --
    # they would miss other model objects such as Jigs. [bruce 070919 comment]
    #
    # REVIEW: is self.bbox (which these recompute) still used for anything?
    # Could it have been superceded by the one recalculated in glpane.setViewFitToWindow?
    # (Note, it's used in glpane.setViewRecenter, but only after an explicit recomputation
    #  done by self.computeBoundingBox(), so its "auto-maintained" aspect is not being used
    #  by that.)
    # [bruce 070919 question]

    def computeBoundingBox(self):
        """
        Compute the bounding box for this Part. This should be
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

    # more bounding box methods [split out of GLPane methods by bruce 070919]

    def bbox_for_viewing_model(self): #bruce 070919 split this out of a GLPane method
        """
        Return a BBox object suitable for choosing a view which shows the entire model
        (visible objects only).
        BUGS:
        - considers only chunks.
        - rectilinear bbox, not screen-aligned, is a poor approximation to the
          model volume for choosing the view. (Fixing this would require
          some changes in the caller as well.)
        """
        bbox = BBox()

        for mol in self.molecules:
            if mol.hidden or mol.display == diINVISIBLE:
                continue
            bbox.merge(mol.bbox)
        return bbox

    def bbox_for_viewing_selection(self): #bruce 070919 split this out of a GLPane method
        """
        Return a BBox object suitable for choosing a view which shows all
        currently selected objects in the model.
        BUGS:
        - considers only visible objects, even though some invisible objects,
        when selected, are indirectly visible (and all ought to be).
        (If this is fixed, comments and message strings in the caller will
         need revision.)
        - rectilinear bbox, not screen-aligned, is a poor approximation to the
          model volume for choosing the view. (Fixing this would also require
          some changes in the caller.)
        """
        movables = self.getSelectedMovables()

        #We will compute a Bbox with a point list.
        #Approach to fix bug 2250. ninad060905
        pointList = []

        selatoms_list = self.selatoms_list()
        if selatoms_list:
            for atm in selatoms_list:
                if atm.display == diINVISIBLE: #ninad 060903  may not be necessary.
                #@@@ Could be buggy because user is probably seeing the selection wireframe around invisible atom
                #and you are now allowing zoom to selection. Same is true for invisible chunks.
                    continue
                pointList.append(atm.posn())

        if movables:
            for obj in movables:
                if obj.hidden:
                    continue
                if not isinstance(obj, Jig):
                    if obj.display == diINVISIBLE:
                        continue
                if isinstance(obj, Chunk):
                    for a in obj.atoms.itervalues():
                        pointList.append(a.posn())
                elif isinstance(obj, Jig):
                    pointList.append(obj.center)
        else:
            if not selatoms_list:
                return None

        bbox = BBox(pointList)

        return bbox

    # ==

    _inputs_for_alist = [] # only invalidated directly. Not sure if we'll inval this whenever we should, or before uses. ###@@@
    def _recompute_alist(self):
        """
        Recompute self.alist, a list of all atoms in this Part, in the same order in which they
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
            """
            run this exactly once on all molecules (or other nodes) in this part, in tree order
            """
            if isinstance(nn, Chunk):
                alist.extend(nn.atoms_in_mmp_file_order())
                    ### REVIEW for PAM3+5: do we need to pass a mapping to
                    # atoms_in_mmp_file_order so it will include conversion atoms?
                    # If so, does caller need to pass it in, to determine conversion options?
                    # If so, do we replace the pseudo-invalidation of this list with
                    # a get method for it, or with passing the option to the mapping
                    # to tell it to collect the atoms actually written? (guess: the latter)
                    # [bruce 080321/080327 questions]
            return # from func_alist only
        self.topnode.apply2all( func_alist)
        self.alist = alist
        return

    # == do the selmols and selatoms recomputers belong in ops_select??

    _inputs_for_selmols = [] # only inval directly, since often stays the same when molecules changes, and might be incrly updated
    def _recompute_selmols(self):
        #e not worth optimizing for selwhat... but assert it was consistent, below.
        self.selmols = 333 # not a valid Python sequence
        res = []
        def func_selmols(nn):
            """
            run this exactly once on all molecules (or other nodes) in this part (in any order)
            """
            if isinstance(nn, Chunk) and nn.picked:
                res.append(nn)
            return # from func_selmols only
        self.topnode.apply2all( func_selmols)
        self.selmols = res
        if self.selmols:
            if self.selwhat != SELWHAT_CHUNKS:
                msg = "bug: part has selmols but selwhat != SELWHAT_CHUNKS"
                if debug_flags.atom_debug:
                    print_compact_stack(msg)
                else:
                    print msg
        return

    _inputs_for_selatoms = [] # only inval directly (same reasons as selmols; this one is *usually* updated incrementally, for speed)
    def _recompute_selatoms(self):
        if debug_1855:
            print "debug_1855: part %r _recompute_selatoms, self.selwhat is %r, so we %s assume result is {} without checking" % \
                  ( self, self.selwhat, {False:"WON'T",True:"WILL (not anymore)"}[self.selwhat != SELWHAT_ATOMS] )
            # Note: this optim (below, now removed) was wrong after undo in that bug...
            # I don't trust it to be always right even aside from Undo, so I'll remove it for A7.
            # For A8 maybe we should replace it with an optim based on an accurate per-part count of picked atoms?
            # Killed nodes might fail to get uncounted, but that would be ok. ##e
#bruce 060415 zapping this to fix bug 1855...
# but if we find selatoms and this would have said not to, should we fix selwhat??
# For now we just complain (debug only) but don't fix it. ###@@@
##        if self.selwhat != SELWHAT_ATOMS:
##            # optimize, by trusting selwhat to be correct.
##            # This is slightly dangerous until changes to assy's current selgroup/part
##            # also fix up selatoms, and perhaps even verify no atoms selected in new part.
##            # But it's likely that there are no such bugs, so we can try it this way for now.
##            # BTW, someday we might permit selecting atoms and chunks at same time,
##            # and this will need revision -- perhaps we'll have a selection-enabled boolean
##            # for each type of selectable thing; perhaps we'll keep selatoms at {} when they're
##            # known to be unselectable.
##            # [bruce 050308]
##            return {} # caller (InvalMixin.__getattr__) will store this into self.selatoms
        self.selatoms = 333 # not a valid dictlike thing
        res = {}
        def func_selatoms(nn):
            "run this exactly once on all molecules (or other nodes) in this part (in any order)"
            if isinstance(nn, Chunk):
                for atm in nn.atoms.itervalues():
                    if atm.picked:
                        res[atm.key] = atm
            return # from func_selatoms only
        self.topnode.apply2all( func_selatoms)
        self.selatoms = res
        if debug_1855:
            print "debug_1855: part %r _recompute_selatoms did so, stores %r" % (self, res,)
            # guess: maybe this runs too early, before enough is updated, due to smth asking for it, maybe for incr update purposes
        if res and self.selwhat != SELWHAT_ATOMS and debug_flags.atom_debug:
            #bruce 060415; this prints, even after fix (or mitigation to nothing but debug prints) of bug 1855,
            # and I don't yet see an easy way to avoid that, so making it debug-only for A7.
            print "debug: bug: part %r found %d selatoms, even though self.selwhat != SELWHAT_ATOMS (not fixed)" % (self,len(res))
        return

    def selatoms_list(self): #bruce 051031
        """
        Return the current list of selected atoms, in order of selection (whenever that makes sense), earliest first.
        This list is recomputed whenever requested, since order can change even when set of selected atoms
        doesn't change; therefore its API looks like a method rather than like an attribute.
           Intended usage: use .selatoms_list() instead of .selatoms.values() for anything which might care about atom order.
        """
        items = [(atm.pick_order(), atm) for atm in self.selatoms.itervalues()]
        items.sort()
        return [pair[1] for pair in items]

    def selected_atoms_list(self, include_atoms_in_selected_chunks = False): #bruce 070508
        """
        Return a list of all selected atoms. If the option says to, also include
        real (i.e. selectable, ignoring selection filter) atoms in selected chunks.
        Atoms are in arbitrary order, except that if only atoms were selected (not chunks),
        then they're in order of selection.
        """
        res = self.selatoms_list() # use some private knowledge: we now own this mutable list.
        if include_atoms_in_selected_chunks:
            #e [someday it might be that chunks too will have a pick_order;
            #   then we could sort them with the atoms before expanding them into atoms,
            #   and change our spec to return all atoms in order of selection
            #   (using arb or mmp file order within picked chunks)]
            for chunk in self.selmols:
                for atom in chunk.atoms.itervalues():
                    if not atom.is_singlet():
                        res.append(atom)
        return res

    # ==

    def addmol(self, mol): # searching for "def addnode" should also find this
        """
        [Public method; the name addmol is DEPRECATED, use addnode instead:]

        Add any kind of Node to this Part (usually the "current Part"),
        at the end of the top level of its node tree
        (so it will be visible as the last node in this Part's
         section of the Model Tree, when this Part is visible).

        Invalidate part attributes which summarize part content (e.g. bbox, drawLevel).

        @param mol: the Node to add to self
        @type mol: Node

        @note: The method name addmol is deprecated. New code should use its alias, addnode.
        """
        #bruce 050228 revised this for Part (was on assy) and for inval/update of part-summary attrs.
        ## not needed since done in changed_members:
        ## self.changed() #bruce 041118
        self.ensure_toplevel_group() # needed if, e.g., we use Build mode to add to a clipboard item
        self.topnode.addchild(mol)
            #bruce 050202 comment: if you don't want this location for the added mol,
            # just call mol.moveto when you're done, like [some other code] does.
        ## done in addchild->changed_dad->inherit_part->Part.add:
        ## self.invalidate_attrs(['natoms','molecules']) # this also invals bbox and center, via molecules

        #bruce 050321 disabling the following debug code, since not yet ok for all uses of _readmmp;
        # btw does readmmp even need to call addmol anymore??
        #bruce 050322 now readmmp doesn't call addmol so I'll try reenabling this debug code:
        if debug_flags.atom_debug:
            self.assy.checkparts()

    addnode = addmol #bruce 060604/080318; should make addnode the fundamental one, and clean up above comments

    def ensure_toplevel_group(self): #bruce 080318 revised so unopenables like DnaStrand don't count
        """
        Make sure this Part's toplevel node is a Group (of a kind which
         does not mind having arbitrary new members added to it),
        by Grouping it if not.

        @note: most operations which create new nodes and want to add them
               needn't call this directly, since they can call self.addnode or
               assy.addnode instead.
        """
        topnode = self.topnode
        assert topnode is not None
        if not topnode.is_group() or not topnode.MT_DND_can_drop_inside():
            # REVIEW: is that the best condition? Do we need an argument
            # to help us know what kinds of groups are acceptable here?
            # And if the current one is not, what kind to create?
            # [bruce 080318 comment, and revised condition]
            self.create_new_toplevel_group()
        return

    def create_new_toplevel_group(self):
        """
        #doc; return newly made toplevel group
        """
        ###e should assert we're a clipboard item part
        # to do this correctly, I think we have to know that we're a "clipboard item part";
        # this implem might work even if we permit Groups of clipboard items someday
        old_top = self.topnode
        #bruce 050420 keep autogen names in self as well as in topnode
        name = self.name or self.assy.name_autogrouped_nodes_for_clipboard( [old_top])
        self.name = name
        # beginning of section during which assy's Part structure is invalid
        self.topnode = Group(name, self.assy, None)
        self.add(self.topnode)
        # now put the new Group into the node tree in place of old_top
        old_top.addsibling(self.topnode)
        self.topnode.addchild(old_top) # do this last, since it makes old_top forget its old location
        # now fix our assy's current selection group if it used to be old_top,
        # but without any of the usual effects from "selgroup changed"
        # (since in a sense it didn't -- at least the selgroup's part didn't change).
        self.assy.fyi_part_topnode_changed(old_top, self.topnode)
        # end of section during which assy's Part structure is invalid
        if debug_flags.atom_debug:
            self.assy.checkparts()
        return self.topnode
    
    def get_topmost_subnodes_of_class(self, clas): #Ninad 2008-08-06, revised by bruce 080807
        """
        Return a list of the topmost (direct or indirect)
        children of self.topnode (Nodes or Groups), or
        self.topnode itself, which are instances of the
        given class (or of a subclass).
        
        That is, scanning depth-first into self's tree of nodes,
        for each node we include in our return value, we won't
        include any of its children.

        @param clas: a class.

        @note: to avoid import cycles, it's often desirable to
               specify the class as an attribute of a convenient
               Assembly object (e.g. xxx.assy.DnaSegment)
               rather than as a global value that needs to be imported
               (e.g. DnaSegment, after "from xxx import DnaSegment").

        @see: same-named method on class Group.
        """
        node = self.topnode # not necessarily a Group
        if isinstance( node, clas):
            return node
        elif node.is_group():
            return node.get_topmost_subnodes_of_class( clas)
        else:
            return []

    # ==

    # note: self._drawer and self.drawing_frame
    # are mostly-orthogonal refactorings, both by bruce 090218
    
    _drawing_frame = None # allocated on demand

    _drawing_frame_class = fake_Part_drawing_frame
        # Note: this attribute is modified dynamically.
        # This default value is appropriate for drawing which does not
        # occur between matched calls of before/after_drawing_model, since
        # drawing then is deprecated but needs to work,
        # so this class will work, but warn when created.
        # Its "normal" value is used between matched calls
        # of before/after_drawing_model.
    
    def __get_drawing_frame(self):
        """
        get method for self.drawing_frame property:
        
        Initialize self._drawing_frame if necessary, and return it.
        """
        if not self._drawing_frame:
            self._drawing_frame = self._drawing_frame_class()
            # note: self._drawing_frame_class changes dynamically
        return self._drawing_frame
    
    def __set_drawing_frame(self):
        """
        set method for self.drawing_frame property; should never be called
        """
        assert 0
    
    def __del_drawing_frame(self):
        """
        del method for self.drawing_frame property
        """
        self._drawing_frame = None

    drawing_frame = property(__get_drawing_frame, __set_drawing_frame, __del_drawing_frame)

    def _has_drawing_frame(self):
        """
        @return: whether we presently have an allocated drawing frame
                 (which would be returned by self.drawing_frame).
        @rtype: boolean
        """
        return self._drawing_frame is not None

    def draw(self, glpane):
        """
        Draw all of self's visible model objects
        using the given GLPane,
        whose OpenGL context must already be current.
        """
        self.invalidate_attr('natoms') #bruce 060215, so that natoms and drawLevel are recomputed every time
            # (needed to fix bugs caused by lack of inval of natoms when atoms die or are born;
            #  also means no need for prefs change to inval drawLevel, provided it gl_updates)
            # (could optim by only invalling drawLevel itself if the prefs value is not 'variable', I think,
            #  but recomputing natoms should be fast compared to drawing, anyway)
        self.before_drawing_model()
        error = True
        try:
            # draw all visible model objects in self
            self.topnode.draw(glpane, glpane.displayMode)
            error = False
        finally:
            self.after_drawing_model(error)
        return

    def before_drawing_model(self): #bruce 070928
        """
        Whenever self's model, or part of it, is drawn,
        that should be bracketed by calls of self.before_drawing_model()
        and self.after_drawing_model() (using try/finally to guarantee
        the latter call). This is already done by self.draw,
        but must be done explicitly if something draws a portion of
        self's model in some other way.

        Specifically, the caller must do (in this order):
        * call self.before_drawing_model()
        
        * call node.draw() (with proper arguments, and exception protection)
          on some subset of the nodes of self (not drawing any node twice);
          during these calls, reference can be made to attributes of
          self.drawing_frame (which is allocated on demand if/when first used
          after this method is called)
        
        * call self.after_drawing_model() (with proper arguments)

        Nesting of these pairs of before_drawing_model/after_drawing_model calls
        is not permitted and will cause bugs.
        
        This API will need revision when the model can contain repeated parts,
        since each repetition will need to be bracketed by matched calls
        of before_drawing_model and after_drawing_model, but they will need
        to behave differently to permit nesting (e.g. have a stack of prior
        values of the variables they reset).
        """
        del self.drawing_frame
        self._drawing_frame_class = Part_drawing_frame
            # instantiated the first time self.drawing_frame is accessed
        return

    def after_drawing_model(self, error = False): #bruce 070928
        """
        @see: before_drawing_model

        @param error: if the caller knows, it can pass an error flag
                      to indicate whether drawing succeeded or failed.
                      If it's known to have failed, we might not do some
                      things we normally do. Default value is False
                      since most calls don't pass anything. (#REVIEW: good?)
        """
        del error # not yet used (error param added by bruce 080411)
        del self.drawing_frame
        del self._drawing_frame_class # expose class default value
        return

    def draw_text_label(self, glpane):
        """
        #doc; called from GLPane.paintGL just after it calls mode.Draw()
        """
        # caller catches exceptions, so we don't have to bother
        text = self.glpane_text()
        if text:
            #bruce 090218 refactored this
            self._drawer.draw_text_label(glpane, text)
        return

    def glpane_text(self):
        return "" # default implem, subclasses might override this

    def writepov(self, f, dispdef): # revised, bruce 090218
        """
        Draw self's visible model objects into an open povray file
        (which already has whatever headers & macros it needs),
        using the given display mode by default.
        """
        self.before_drawing_model()
            # This is needed at least for its setting up of
            # self.drawing_frame.repeated_bonds_dict, and using its
            # "full version" will help permit future draw methods that
            # work for either OpenGL or POV-Ray.
        error = True
        try:
            self.topnode.writepov(f, dispdef)
            error = False
        finally:
            self.after_drawing_model(error)
        return

    # ==

    def break_interpart_bonds(self): ###@@@ move elsewhere in method order? review, implem for jigs
        """
        Break all bonds between nodes in this part and nodes in other parts;
        jig-atom connections count as bonds [but might not be handled correctly as of 050308].
        #e In future we might optimize this and only do it for specific node-trees.
        """
        # Note: this implem assumes that the nodes in self are exactly the node-tree under self.topnode.
        # As of 050309 this is always true (after update_parts runs), but might not be required except here.
        self.topnode.apply2all( lambda node: node.break_interpart_bonds() )
        return

    # == these are event handlers which do their own full UI updates at the end

    # bruce 050201 for Alpha:
    #    Like I did to fix bug 370 for Delete (and cut and copy),
    # make Hide and Unhide work on jigs even when in selatoms mode.

    def Hide(self):
        """
        Hide all selected chunks and jigs
        """
        self.topnode.apply2picked(lambda x: x.hide())
        self.w.win_update()

    def Unhide(self):
        """
        Unhide all selected chunks and jigs
        """
        self.topnode.apply2picked(lambda x: x.unhide())
        self.w.win_update()

    # ==

    def place_new_geometry(self, plane):
        self.ensure_toplevel_group()
        self.addnode(plane)
        # note: fix_one_or_complain will do nothing
        # (and return 0) as long as plane has no atoms,
        # which I think is true for all ref. geometry, for now anyway
        # [bruce 071214 comment]
        def errfunc(msg):
            "local function for error message output"
            # I think this will never happen [bruce 071214]
            env.history.message( redmsg( "Internal error making new geometry: " + msg))
        fix_one_or_complain( plane, self.topnode, errfunc)
        self.assy.changed()
        self.w.win_update()
        return

    def place_new_jig(self, jig): #bruce 050415, split from all jig makers, extended, bugfixed
        """
        Place a new jig
        (created by user, from atoms which must all be in this Part)
        into a good place in this Part's model tree.
        """
        atoms = jig.atoms # public attribute of the jig
        assert atoms, "bug: new jig has no atoms: %r" % jig
        for atm in atoms:
            assert atm.molecule.part is self, \
                   "bug: new jig %r's atoms are not all in the current Part %r (e.g. %r is in %r)" % \
                   ( jig, self, atm, atm.molecule.part )
        # First just put it after any atom's chunk (as old code did); then fix that place below.
        self.ensure_toplevel_group() #bruce 050415 fix bug 452 item 17
        mol = atoms[0].molecule # arbitrary chunk involved with this jig
        mol.dad.addchild(jig)
        assert jig.part is self, "bug in place_new_jig's way of setting correct .part for jig %r" % jig
        # Now put it in the right place in the tree, if it didn't happen to end up there in addchild.
        # BTW, this is probably still good to do, even though it's no longer necessary to do
        # whenever we save the file (by workaround_for_bug_296, now removed),
        # i.e. even though the mmp format now permits forward refs to jigs. [bruce 051115 revised comment]
        def errfunc(msg):
            "local function for error message output"
            # I think this should never happen [bruce ca. 050415]
            env.history.message( redmsg( "Internal error making new jig: " + msg))
        fix_one_or_complain( jig, self.topnode, errfunc)
        # now it's after all the atoms in it, but we also need to move it
        # outside of any group it doesn't belong in (and after that group
        # so that it remains after all its atoms). [bruce 080515 bugfix]
        move_after_this_group = None
        for group in jig.containing_groups():
            if not 1: ## group.allow_this_node_inside(jig): # IMPLEM, to the extent we need it aside from permit_as_member
                move_after_this_group = group
            else:
                location = move_after_this_group or jig
                if group is location.dad and not group.permit_as_member( jig, pre_updaters = False ):
                    ###doc: explain why this option pre_updaters = False makes sense
                    # review: use the other code that calls permit_as_member instead of
                    # calling it directly?
                    move_after_this_group = group
                pass
            continue
        if move_after_this_group is not None:
            move_after_this_group.addsibling(jig)
        return

    # ==

    def resetAtomsDisplay(self):
        """
        Resets the display mode for each atom in the selected chunks
        to default display mode.
        Returns the total number of atoms that had their display setting reset.
        """
        n = 0
        for chunk in self.selmols:
            n += chunk.set_atoms_display(diDEFAULT)
        if n:
            self.changed()
        return n

    def showInvisibleAtoms(self):
        """
        Resets the display mode for each invisible (diINVISIBLE) atom in the
        selected chunks to default display mode.
        Returns the total number of invisible atoms that had their display setting reset.
        """
        n = 0
        for chunk in self.selmols:
            n += chunk.show_invisible_atoms()
        if n:
            self.changed()
        return n

    ###e refile these new methods:

    def writemmpfile(self, filename, **mapping_options): #bruce 051209 added **mapping_options
        # as of 050412 this didn't yet turn singlets into H;
        # but as of long before 051115 it does (for all calls -- so it would not be good to use for Save Selection!)
        #bruce 051209  -- now it only does that if **mapping_options ask it to.
        from files.mmp.files_mmp_writing import writemmpfile_part
        writemmpfile_part( self, filename, **mapping_options)

    pass # end of class Part

# == subclasses of Part

class MainPart(Part):
    def immortal(self):
        return True
    def location_name(self):
        return "main part"
    def movie_suffix(self):
        """
        what suffix should we use in movie filenames? None means don't permit making them.
        """
        return ""
    pass

class ClipboardItemPart(Part):
    def glpane_text(self):
        #e abbreviate long names...
        return "%s (%s)" % (self.topnode.name, self.location_name())
    def location_name(self):
        """
        [used in history messages and on glpane]
        """
        # bruce 050418 change:
        ## return "clipboard item %d" % ( self.clipboard_item_number(), )
        return "on Clipboard" #e might be better to rename that to Shelf, so only the current
            # pastable (someday also in OS clipboard) can be said to be "on the Clipboard"!
    def clipboard_item_number(self):
        """
        this can be different every time...
        """
        return self.assy.shelf.members.index(self.topnode) + 1
    def movie_suffix(self):
        """
        what suffix should we use in movie filenames? None means don't permit making them.
        """
        ###e stub -- not a good choice, since it changes and thus is reused...
        # it might be better to assign serial numbers to each newly made Part that needs one for this purpose...
        # actually I should store part numbers in the file, and assign new ones as 1 + max of existing ones in shelf.
        # then use them in dflt topnode name and in glpane text (unless redundant) and in this movie suffix.
        # but this stub will work for now. Would it be better to just return ""? Not sure. Probably not.
        return "-%d" % ( self.clipboard_item_number(), )
    pass

# end
