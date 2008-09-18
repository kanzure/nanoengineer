# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
assembly.py -- provides class Assembly, for everything stored in one mmp file,
including one main part and zero or more clipboard items; see also part.py.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

==

About the Assembly and Part classes, and their relationship:

[###@@@ warning, 050309: docstring not reviewed recently]

Each Assembly has a set of Parts, of which one is always "current"; the current part
is what is displayed in the glpane and operated on by most operations,
and (for now, as of 050222) the assy attributes selmols, selatoms, and molecules
always refer to the same-named attrs of the current Part. (In fact, many other
assy methods and attrs are either delegated to the current Part or have directly
become Part methods or been split into assy and Part methods.)

All selected objects (even atoms) must be in the current part;
the current part is changed by using the model tree to select something
in some other part. The main model is one part, and each clipboard item is another part.
It is not yet possible to form Groups of separate parts in the Clipboard,
but this might be added somehow in the future. For now, any Group in the clipboard
is necessarily a single Part (or inside one); each toplevel member of the clipboard
is exactly one separate Part.

Once several known bugs (like 371) are fixed, then bonds between parts will not be allowed
(since they would be bonds between atoms or jigs in different physical spaces),
and bonds that become "interspace bonds" (due to move or copy operations)
will be automatically broken, or will cause things to be placed into the same space
in order not to break them.

Note that all info in the assy relates either to its named file or to something
about the current command (in the general sense of that term, not just the current assy.o.currentCommand object);
but the assy's info relating to its named file is not all stored directly in that file --
some of it is stored in other files (such as movie files), and in the future, some of it
might be stored in files referred to from some object within one of its Parts.

==

Both Part and Assembly might well be renamed. We don't yet know the best terms
with which to refer to these concepts, or even the exact ideal boundary between them in the code.

==

History:

The Part/Assembly distinction was introduced by bruce 050222
(though some of its functionality was anticipated by the "current selection group"
introduced earlier, just before Alpha-1). [I also rewrote this entire docstring then.]

The Part/Assembly distinction is unfinished, particularly in how it relates to some modes and to movie files.

Prior history unclear; almost certainly originated by Josh.

Bruce 050513-16 replaced some == with 'is' and != with 'is not', to avoid __getattr__
on __xxx__ attrs in python objects.

Bruce 080403 renamed class assembly -> class Assembly.
"""

###@@@ Note: lots of old code below has been commented out for the initial
# assy/part commit, to help clarify what changed in viewcvs,
# but will be removed shortly thereafter.
# Also, several functions will be moved between files after that first commit
# but have been kept in the same place before then for the benefit of viewcvs diff.

import os
import time

import utilities.Initialize as Initialize

from foundation.Utility import node_name
from foundation.Group import Group
from operations.pastables import is_pastable

from utilities.debug import print_compact_traceback
from utilities.prefs_constants import workingDirectory_prefs_key

from utilities.Log import orangemsg ##, greenmsg, redmsg
from utilities import debug_flags
from platform_dependent.PlatformDependent import find_or_make_any_directory
import foundation.env as env
from foundation.state_utils import StateMixin
from utilities.debug import print_compact_stack
import foundation.undo_archive as undo_archive

from utilities.GlobalPreferences import GLPANE_IS_COMMAND_SEQUENCER

from utilities.constants import gensym, SELWHAT_CHUNKS, SELWHAT_ATOMS
from foundation.state_constants import S_CHILD, S_DATA, S_REF

from model.part import Part as Part_class # use a name we can search for [bruce 071029]
    ### TODO: rename the class Part itself somehow; both Part and part are too generic

from model.part import MainPart
from model.part import ClipboardItemPart

from utilities.icon_utilities import imagename_to_pixmap
from commands.PartProperties.PartProp import PartProp
from PyQt4 import QtGui

from foundation.Assembly_API import Assembly_API
from model.prefsTree import MainPrefsGroupPart
import foundation.undo_manager as undo_manager
from files.mmp.files_mmp_writing import writemmpfile_assy

# ==

debug_assy_changes = 0 #bruce 050429

if 1: #bruce 060124 debug code; safe but dispensable
    debug_assy_changes = debug_assy_changes or undo_archive.debug_undo2

_global_assy_number = 0 # count Assembly objects [bruce 050429]

_assy_owning_win = None #bruce 060122; assumes there's only one main window; probably needs cleanup

# ==

class Assembly( StateMixin, Assembly_API):
    """
    (This is the closest thing we have to an object
    representing the contents of an open mmp file,
    but it also has associated state like selection
    and undo_archive, controllers like undo_manager,
    and lots of miscellaneous methods for manipulating
    that data.)
    """
    # The following class constant attrs can be used in isinstance tests
    # (e.g. isinstance( node, assy.DnaGroup)) and also as arguments
    # to Node.parent_node_of_class. Using them can avoid import cycles
    # (compared to other code importing these classes directly)
    # 
    # Note that these imports must not be moved to toplevel,
    # and are not redundant with toplevel imports of the same symbols,
    # if they exist. [bruce 080310]
    from foundation.Group import Group
    from model.chunk      import Chunk
    from model.chem       import Atom
    from model.jigs       import Jig
    from model.Plane      import Plane
    
    from dna.model.Block  import Block
    from dna.model.DnaGroup   import DnaGroup
    from dna.model.DnaSegment import DnaSegment
    from dna.model.DnaStrand  import DnaStrand
    from dna.model.DnaMarker  import DnaMarker
    from dna.model.DnaLadderRailChunk import DnaLadderRailChunk
    from dna.model.DnaLadderRailChunk import DnaStrandChunk
    from dna.model.DnaStrandOrSegment import DnaStrandOrSegment
    
    from cnt.model.NanotubeGroup   import NanotubeGroup # --mark 2008-03-09
    from cnt.model.NanotubeSegment import NanotubeSegment # --mark 2008-03-09
    
    #bruce 060224 adding alternate name Assembly for this (below), which should become the preferred name
    #bruce 071026 inheriting Assembly_API so isinstance tests need only import that file
    #bruce 071026 added docstring

    # change counters (actually more like modtimes than counters, since changes occurring between checkpoints
    # might count as only one change -- see code for details):

    # model changes (all changes that affect mmp file and should mark it in UI as needing to be saved)
    # (includes all structural changes and many display changes)
    # (note that a few changes are saved but don't mark it as needing save, like "last view" (always equals current view))
    
    _model_change_indicator = 0 #bruce 060121-23; sometimes altered by self.changed() (even if self._modified already set)
        #bruce 060227 renamed this from _change_indicator to
        # _model_change_indicator, but don't plan to rename self.changed().
        #
        # maybe: add a separate change counter for drag changes vs other kinds
        # of changes (less frequent), to help optimize some PM updates;
        # not necessary unless we notice drag being too slow due to PM updates
        # (or diffs which prevent them but take time), which this would fix
        # [bruce 080808 comment]

    _selection_change_indicator = 0
    
    _view_change_indicator = 0 # also includes changing current part, glpane display mode
        # [mostly nim as of 060228, 080805]

    def all_change_indicators(self): #bruce 060227; 071116 & 080805, revised docstring  ### TODO: fix docstring after tests
        """
        Return a tuple of all our change indicators which relate to undoable
        state, suitable for later passing to self.reset_changed_for_undo().

        (Presently, this means all of our change indicators except the
        one returned by command_stack_change_indicator.) 

        The order is guaranteed to be:

        (model_change_indicator, selection_change_indicator, view_change_indicator)

        and if we add new elements, we guarantee we'll add them at the end
        (so indices of old elements won't change).

        @note: view_change_indicator is mostly NIM (as of 080805)

        @note: these are not really "counters" -- they might increase by more
               than 1 for one change, or only once for several changes,
               or decrease after Undo. All the numbers mean is that, if they
               don't differ, no change occurred in the corresponding state.
               They might be renamed to "change indicators" to reflect this.

        @note: model_change_indicator only changes when assy.changed() is called,
               and at most once per potential undoable operation. For example,
               during a drag, some model component's position changes many times,
               but model_change_indicator only changes once during that time,
               when the user operation that does the drag happens to call
               assy.changed() for the first time during that undoable operation.

        @note: I don't know whether model_change_indicator works properly when
               automatic Undo checkpointing is turned off -- needs review.
               (The issue is whether it changes at most once during any one
               *potential* or *actual* undoable operation.) This relates to
               whether env.change_counter_checkpoint() is called when Undo
               checkpointing is turned off. I am planning to try a fix to this
               today [080805], and also to the "changing only once during drag"
               issue noted above, by adding a call to that function sometime
               during every user event -- probably after all ui updaters are called.

        @see: self.command_stack_change_indicator (not included in our return value)
        """
        return self._model_change_indicator, self._selection_change_indicator, self._view_change_indicator

    def model_change_indicator(self): #bruce 080731
        """
        @see: all_change_indicators
        """
        # todo: ensure it's up to date
        return self._model_change_indicator

    def selection_change_indicator(self): #bruce 080731
        """
        @see: all_change_indicators
        """
        # todo: ensure it's up to date
        return self._selection_change_indicator

    def view_change_indicator(self): #bruce 080731
        """
        NOT YET IMPLEMENTED
        
        @see: all_change_indicators
        """
        # todo: ensure it's up to date
        assert 0, "don't use this yet, the counter attr is mostly NIM" #bruce 080805
        return self._view_change_indicator
    
    def command_stack_change_indicator(self): #bruce 080903
        """
        @see: same-named method in class CommandSequencer.

        @note: this is intentionally not included in the value of
               self.all_change_indicators().
        """
        return self.commandSequencer.command_stack_change_indicator()
    
    # state declarations:
    # (the change counters above should not have ordinary state decls -- for now, they should have none)
    
    _s_attr_tree = S_CHILD #bruce 060223
    _s_attr_shelf = S_CHILD
    #e then more, including current_movie, temperature, etc (whatever else goes in mmp file is probably all that's needed);
    # not sure if .part is from here or glpane or neither; not sure about selection (maybe .picked is enough, then rederive?);
    # view comes from glpane and it should be its own root object, i think; mode is also in glpane ###@@@

    #bruce 060227 more decls (some guesses):
    # not root (since i think tree & shelf are never replaced), filename
    _s_attr_temperature = S_DATA
    _s_attr_current_movie = S_CHILD
    _s_attr__last_current_selgroup = S_REF # this should fix bug 1578 [bruce 060227 guess]
    # don't need .part, it's derived by __getattr__ from selgroup
    ### might need _modified? probably not, do separately

    _s_attr_selwhat = S_DATA #bruce 060302 fix bug 1607
    _s_attr__last_set_selwhat = S_DATA # avoids debug warning when undo changes self.selwhat without this decl
    
    # initial values of some instance variables
    undo_manager = None #bruce 060127

    assy_valid = False # whether it's ok for updaters to run right now [###misnamed] [bruce 080117]

    assy_closed = False # whether this assy has been closed by calling self.close_assy [bruce 080314]
        # todo: use this more.
    
    permanently_disable_updaters = False # whether the running of updaters on objects
        # in this assy has been permanently disabled. Note that once this is set
        # to True, it might cause errors to ever reset it to False.
        # Currently it is only set when closing this assy, but we could also
        # set it on assys in which we want to disable ever running updaters
        # (e.g. the assys used in MMKit) if desired.
        # Not yet implemented in all updaters. Implemented in dna updater.
        # [bruce 080314]
    
    def __init__(self,
                 win,
                 name = None,
                 own_window_UI = False,
                 run_updaters = False,
                 commandSequencerClass = None
                 ):
        """
        @type win: MWsemantics or None
        """
        self.own_window_UI = own_window_UI

        if not run_updaters: #bruce 080403
            self.permanently_disable_updaters = True
        
        # ignore changes to this Assembly during __init__, and after it,
        # until the client code first calls our reset_changed method.
        # [bruce 050429 revised that behavior and this comment, re bug 413]
        self._modified = 1 
        
        # the MWsemantics displaying this Assembly (or None, when called from ThumbView)
        self.w = win # deprecated but widely used [bruce 071008]
        self.win = win #bruce 071008
        # both of the following are done later in MWsemantics
        # to avoid a circularity, via self.set_glpane and
        # self.set_modelTree:
        #   self.mt = win.modelTreeView [or win.mt, probably the same thing, not 100% clear -- bruce 070503 comment]
        #   self.o = win.glpane
        
        # the name if any
        self.name = str(name or gensym("Assembly"))
            # note: we intentionally don't pass an assy argument to gensym.
            # [bruce 080407 comment]

        #bruce 050429
        global _global_assy_number
        _global_assy_number += 1
        self._debug_name = self.name + "-%d" % _global_assy_number
        self._assy_number = _global_assy_number # use in __repr__, bruce 080219

        want_undo_manager = False
        if own_window_UI:
            #bruce 060127 added own_window_UI flag to help fix bug 1403
            # (this is false when called from ThumbView to make its "dummy Assembly" (which passes self.w of None),
            # or from MMKit for Library assy (which passes self.w of main window, same as main assy).
            # Another way would be to test (self.w.assy is self), but w.assy could not yet be set up at this time,
            # so any fix like that is more unclear than just having our __init__-caller pass us this flag.
            assert self.w
            global _assy_owning_win
            if 1: #bruce 070517 fix a change that looks wrong -- make this always happen, like it used to
##                from constants import MULTIPANE_GUI
##                if not MULTIPANE_GUI:
##                # wware 20061115 - we need to permit assys to coexist
                if _assy_owning_win is not None:
                    _assy_owning_win.deinit()
                    # make sure assys don't fight over control of main menus, etc [bruce 060122]
            _assy_owning_win = self

            want_undo_manager = True #bruce 060223: don't actually make one until init of all state attrs is complete
        
        # the Clipboard... this is replaced by another one later (of a different class),
        # once or twice each time a file is opened. ####@@@@ should clean up
        self.shelf = Group("Clipboard", self, None, [])
        self.shelf.open = False

        # the model tree for this Assembly
        self.tree = Group(self.name, self, None)

        # a node containing both tree and shelf (also replaced when a file is opened)
        ####@@@@ is this still needed, after assy/part split? not sure why it would be. ###k
        self.root = Group("ROOT", self, None, [self.tree, self.shelf])

        # bruce 050131 for Alpha:
        # For each Assembly, maintain one Node or Group which is the
        # "current selection group" (the PartGroup or one of the
        # clipboard items), in which all selection is required to reside.
        #    It might sometimes be an out-of-date node, either a
        # former shelf item or a node from a previously loaded file --
        # not sure if these can happen, but "user beware".
        #    [As of 030510, we store it privately and check it in all uses.]
        #    Sometime after Alpha, we'll show this group in the glpane
        # and let operations (which now look at self.tree or self.molecules)
        # affect it instead of affecting the main model
        # (or having bugs whenever clipboard items are selected, as they
        # often do now).
        # bruce 050228 update: this is still used after assy/part split,
        # but some of the above comment has been done differently,
        # and this needs to be kept in sync with self.part. #doc sometime.
        self.init_current_selgroup() # must be re-called when self.tree is replaced

        # filename if this entire Assembly (all parts) was read from a file
        self.filename = ""
        # what to select: 0=atoms, 2 = molecules
        # [bruce 050308 change: new code should use SELWHAT_ATOMS and SELWHAT_CHUNKS
        #  instead of hardcoded constants, and never do boolean tests of selwhat]
        #bruce 050517: as of now, self.selwhat should only be set (other than by this init)
        # via self.set_selwhat(). [BTW, when we make a new assy and init this, are we sure it
        # always corresponds to the mode? Probably it does now only since we change to that mode
        # when opening files. #k]
        self.selwhat = SELWHAT_CHUNKS # initial value for new assy
        self._last_set_selwhat = self.selwhat
        
        #bruce 050131 for Alpha:
        self.kluge_patch_toplevel_groups( )
        self.update_parts( do_post_event_updates = False)
            #bruce 050309 for assy/part split

        #bruce 050429 as part of fixing bug 413, no longer resetting self._modified here --
        # client code should call reset_changed instead, when appropriate.
        
        # the current version of the MMP file format
        # this is set in files_mmp_writing.writemmpfile_assy. Mark 050130
        # [bruce 050325 comments: it's not clear to me what this means
        #  (eg if you read an old file does this indicate that old file's format?)
        #  or why it needs to be set here at all.]
        self.mmpformat = ''

        self.temperature = 300 # bruce 050325 have to put this back here for now

        # bruce 050325 revising Movie code for assy/part split and other reasons.
        # Now it works like this: there can be several active Movie objects,
        # but if one is playing or is the one to be played by default (e.g. the last one made),
        # then it's stored here in assy.current_movie; otherwise that's None. However, unlike before,
        # each movie object knows the alist which is correct for it (or, thinks it knows,
        #  since with old .dpb format it could easily be wrong unless we made it in this session),
        # and in principle old movies can be replayed (but only in the same session)
        # as long as their alist atoms still exist,
        # even if they've been reordered or new ones made, etc
        # (though we might enforce their being all in one Part, and later, add more conditions).
        # For movies made in prior sessions (actually it's worse -- made from prior opened files),
        # we still depend on our guess that the atom order is the same as in the current Part
        # when the moviefile is loaded, checked only by number of atoms. When we have new .dpb format
        # we can improve that.
        self.current_movie = None
            # before 050325 this was called self.m and was always the same Movie object (per assy)

        if debug_assy_changes:
            print "debug_assy_changes: creating", self
        
        # make sure these exist [bruce 050418]:
        assert self.tree
        assert self.tree.part
        assert self.tree.part.homeView
        assert self.tree.part.lastView

        if want_undo_manager:
            #bruce 060223: we no longer do this until we're fully inited, since when undoing to initial checkpoint
            # and doing some new op from there, the new op needs to see a fully initialized assy.
            #obs older comment (can be mostly removed soon):
            #bruce 051005: create object for tracking changes in our model, before creating any
            # model objects (ie nodes for tree and shelf). Since this is not initially used except
            # to record changes as these objects are created, the fact that self is still incomplete 
            # (e.g. lacks important attributes like tree and root and part) should not matter. [#k I hope]
            menus = (win.editMenu,) # list of menus containing editUndo/editRedo actions (for aboutToShow signal) [060122]
            self.undo_manager = undo_manager.AssyUndoManager(self, menus) # be sure to call init1() on this within self.__init__!
                # fyi: this [no longer, 060223] sets self._u_archive for use by our model objects when they report changes
                # (but its name and value are private to AssyUndoManager's API for our model objects,
                #  which is why we don't set it here)
            self.undo_manager.init1() #k still exists and needed, but does it still need to be separate from __init__? [060223]
            # Note: self.undo_manager won't start recording checkpoints until someone calls self.clear_undo_stack() at least once,
            # which can't be done until some more initialization is done by our callers,
            # in ways which currently differ for the first Assembly created, and later ones.
            # This is not even done by the end of MWsemantics.__init__, as of now.
            # For details, search out the highest-level calls to clear_undo_stack. [bruce 060223]
            # [update, 080229: be sure to call it before adding much data to the model, though,
            # since it scans all current data twice the first time it's called, only once thereafter.
            # See its docstring for details.]
            pass

        # could remove these when they work, but no need:
        # test node_depth method: [bruce 080116]
        assert self.root.node_depth() == 0
        assert self.tree.node_depth() == 1
        assert self.shelf.node_depth() == 1

        self._init_glselect_name_dict()

        if GLPANE_IS_COMMAND_SEQUENCER:
            assert not commandSequencerClass
        else:
            assert bool(commandSequencerClass) == bool(own_window_UI)
                # since own_window_UI determines whether external code
                # expects us to have self.commandSequencer accessible
            if commandSequencerClass: #bruce 080813
                # make and own a command sequencer of the given class
                
                # Note: importing the usual class directly causes import cycle
                # problems, for legitimate or at least hard-to-avoid reasons --
                # it knows a lot of command classes, and some of them know how
                # to construct Assemblies (albeit ones that don't need command
                #  sequencers, as it happens for now, but that might not be
                #  fundamental). So we make the caller tell us, to avoid that,
                # and since it makes perfect sense.
                
                # Review: is class Assembly not the ideal object to own a
                # command sequencer?? Other candidates: partwindow; or a
                # specialized subclass of Assembly.
                # The same question might apply to our undo manager.
                # Related Q: is finding commandSequencer via assy legitimate?
                # [bruce 080813 questions]

                self.commandSequencer = commandSequencerClass(self) #bruce 080813

        self.assy_valid = True
                        
        return # from Assembly.__init__

    # ==
    
    def set_glpane(self, glpane): #bruce 080216
        self.o = glpane # historical name for our glpane, widely used
        self.glpane = glpane # clearer name, added 080216
        if GLPANE_IS_COMMAND_SEQUENCER:
            #bruce 080813 permit new code running under old flag value
            # to reference assy.commandSequencer
            if self.own_window_UI:
                self.commandSequencer = glpane
        return

    def set_modelTree(self, modelTree): #bruce 080216
        self.mt = modelTree
        return
    
    def __repr__(self):
        #bruce 080117
        # report _assy_number & main-ness, bruce 080219
        # main-ness code revised (bugfix during __init__), bruce 080516
        global _global_assy_number
        extra = "(bug in repr if seen)"
        try:
            win = env.mainwindow()
        except:
            extra = "(exception in env.mainwindow())"
        else:
            if win is None:
                extra = "(no mainwindow)"
            else:
                try:
                    assy = win.assy
                except AttributeError:
                    extra = "(mainwindow has no .assy)"
                else:
                    if self is assy:
                        extra = "(main)"
                    else:
                        extra = "(not main)"
                    pass
                pass
            pass
        # now extra describes the "main assy status"
        res = "<%s #%d/%d %s %r at %#x>" % \
              (self.__class__.__name__.split('.')[-1],
               self._assy_number,
               _global_assy_number, # this lets you tell if it's the most
                   # recent one -- but beware of confusion from partlib assys;
                   # so also report whether it's currently the main one:
               extra,
               self.name,
               id(self))
        return res
    
    def deinit(self): # bruce 060122
        """
        make sure assys don't fight over control of main menus, etc
        """
        # as of 080314, this is only called by:
        # - MWsemantics.cleanUpBeforeExiting
        # - __init__ of the next mainwindow assy, if this is one (I think).

        if not self.assy_closed:
            print "\nbug: deinit with no close_assy of %r" % self
            self.close_assy()
            pass
        
        ###e should this be extended into a full destroy method, and renamed? guess: yes. [bruce 060126]
        if self.undo_manager:
            self.undo_manager.deinit()
            #e more? forget self.w?? maybe someday, in case someone uses it now who should be using env.mainwindow()
        return

    def close_assy(self): #bruce 080314
        """
        self is no longer being actively used, and never will be again.
        (I.e. it's being discarded.)
        
        Record this state in self, and do (or permit later code to do,
        by recording it) various optimizations and safety changes for
        closed assys.

        @note: doesn't yet do most of what it ought to do (e.g. destroy atoms).
        """
        self.assy_closed = True
        self.permanently_disable_updaters = True
        return
    
    # ==

    _glselect_name_dict = None # in case of access before init
    
    def _init_glselect_name_dict(self): #bruce 080220
        if 0:
            # use this code as soon as:
            # - all users of env.py *glselect_name funcs/attrs
            #   are replaced with calls of our replacement methods below.
            # - moving a Node to a new assy, if it can happen, reallocates its glname
            #   or can store the same one in the new assy.
            #   (or decide that makes no sense and retain this shared dict?)
            # - destroyed bonds (etc) can figure out how to call dealloc_my_glselect_name
            # [bruce 080220/080917]
            from graphics.drawing.glselect_name_dict import glselect_name_dict
            self._glselect_name_dict = glselect_name_dict()
            # todo: clear this when we are destroyed, and make sure accesses to it
            # either never happen or don't mind not finding an object for a name.
        else:
            # use the global one in env.py, until we are able to use the above code
            # and can remove the one in env.py and its access functions/attrs.
            self._glselect_name_dict = env._shared_glselect_name_dict
        return

    def alloc_my_glselect_name(self, obj): #bruce 080220
        """
        Allocate a GL_SELECT name for obj to pass to glPushName
        during its OpenGL drawing, and record obj as its owner
        for purposes of hit-testing by our GLPane.
        
        @see: glselect_name_dict.alloc_my_glselect_name for details.
        @see: our method dealloc_my_glselect_name
        """
        return self._glselect_name_dict.alloc_my_glselect_name(obj)
    
    def dealloc_my_glselect_name(self, obj, name): #bruce 080220
        """
        Deallocate the GL_SELECT name which was allocated for obj
        using self.alloc_my_glselect_name.
        
        @see: glselect_name_dict.dealloc_my_glselect_name for details.
        """
        return self._glselect_name_dict.dealloc_my_glselect_name(obj, name)

    def object_for_glselect_name(self, name): #bruce 080220
        """
        Look up the owning object for a GL_SELECT name
        which was allocated for obj using self.alloc_my_glselect_name.

        @return: the object we find, or None if none is found.

        @note: old code used env.obj_with_glselect_name.get for this;
               a cleanup which replaces that with access to this method
               was partly done as of 080220, and is perhaps being completed
               on 080917. (Note the spelling differences:
               obj vs object and with vs for.)
        """
        # (I don't know if the following test for self._glselect_name_dict
        #  already existing is needed. Maybe only after we're destroyed (nim)?)
        return self._glselect_name_dict and \
               self._glselect_name_dict.object_for_glselect_name(name)

    # ==

    def kluge_patch_toplevel_groups(self, assert_this_was_not_needed = False): #bruce 050109
        #bruce 071026 moved this here from helper function kluge_patch_assy_toplevel_groups in Utility.py
        """
        [friend function; not clearly documented]
        This kluge is needed until we do the same thing in
        whatever makes the toplevel groups in an Assembly (eg files_mmp).
        Call it as often as you want (at least once before updating model tree
        if self might be newly loaded); it only changes things when it needs to
        (once for each newly loaded file or inited assy, basically);
        in theory it makes assy (self) "look right in the model tree"
        without changing what will be saved in an mmp file,
        or indeed what will be seen by any other old code looking at
        the 3 attrs of self which this function replaces (shelf, tree, root).
        Note: if any of them is None, or not an instance object, we'll get an exception here.
        """
        #bruce 050131 for Alpha:
        # this is now also called in Assembly.__init__ and in readmmp,
        # not only from the mtree.
        
        ## oldmod = assy_begin_suspend_noticing_changes(self)
        oldmod = self.begin_suspend_noticing_changes()
        # does doing it this soon help? don't know why, was doing before root mod...
        # now i am wondering if i was wrong and bug of wrongly reported assy mod
        # got fixed even by just doing this down below, just before remaking root.
        # anyway that bug *is* fixed now, so ok for now, worry about it later. ###@@@
        fixroot = 0
        try:
            if self.shelf.__class__ is Group:
                self.shelf = self.shelf.kluge_change_class( ClipboardShelfGroup)
                fixroot = 1
            if self.tree.__class__ is Group:
                self.tree = self.tree.kluge_change_class( PartGroup)
                ##bruce 050302 removing use of 'viewdata' here,
                # since its elements are no longer shown in the modelTree,
                # and I might as well not figure them out re assy/part split until we want
                # them back and know how we want them to behave regarding parts.
    ##            lis = list(self.viewdata.members)
    ##            # are these in the correct order (CSys XY YZ ZX)? I think so. [bruce 050110]
    ##            self.tree.kluge_set_initial_nonmember_kids( lis )
                fixroot = 1
            if self.root.__class__ is Group or fixroot:
                fixroot = 1 # needed for the "assert_this_was_not_needed" check
                #e make new Root Group in there too -- and btw, use it in model tree widgets for the entire tree...
                # would it work better to use kluge_change_class for this?
                # academic Q, since it would not be correct, members are not revised ones we made above.
                self.root = RootGroup("ROOT", self, None, [self.tree, self.shelf]) #k ok to not del them from the old root??
                ###@@@ BUG (suspected caused here): fyi: too early for this status msg: (fyi: part now has unsaved changes)
                # is it fixed now by the begin/end funcs? at leastI don't recall seeing it recently [bruce 050131]
                ## removed this, 050310: self.current_selection_group = self.tree #bruce 050131 for Alpha
                self.root.unpick() #bruce 050131 for Alpha, not yet 100% sure it's safe or good, but probably it prevents bugs
                ## revised this, 050310:
                ## self.current_selection_group = self.tree # do it both before and after unpick (though in theory either alone is ok)
                ## self.current_selgroup_changed()
                ## self.set_current_selgroup( self.tree) -- no, checks are not needed and history message is bad
                self.init_current_selgroup() #050315
        finally:
            ## assy_end_suspend_noticing_changes(self,oldmod)
            self.end_suspend_noticing_changes(oldmod)
            if fixroot and assert_this_was_not_needed: #050315
                if debug_flags.atom_debug:
                    print_compact_stack("atom_debug: fyi: kluge_patch_toplevel_groups sees fixroot and assert_this_was_not_needed: ")
        return

    # ==

    #bruce 051031: keep counter of selection commands in assy (the model object), not Part,
    # to avoid any chance of confusion when atoms (which will record this as their selection time)
    # move between Parts (though in theory, they should be deselected then, so this might not matter).
    _select_cmd_counter = 0
    def begin_select_cmd(self):
        # Warning: same named method exists in Assembly, GLPane, and ops_select, with different implems.
        # The best place to save this state is not clear, but probably it's a place that won't explicitly exist
        # until we restructure the code, since it's part of the "current selection" state, which in principle
        # should be maintained as its own object, either per-window or per-widget or per-model.
        # [bruce 051031]
        self._select_cmd_counter += 1
        return
    
    def set_selwhat(self, selwhat): #bruce 050517
        ## print_compact_stack( "set_selwhat to %r: " % (selwhat,))
        assert selwhat in (SELWHAT_ATOMS, SELWHAT_CHUNKS)
        if not self._last_set_selwhat == self.selwhat: # compare last officially set one to last actual one
            if debug_flags.atom_debug: # condition is because BuildCrystal_Command will do this, for now
                print_compact_stack( "atom_debug: bug: this failed to call set_selwhat, but set it directly, to %r:\n " \
                                     % (self.selwhat,) )
        self.selwhat = selwhat
        self._last_set_selwhat = self.selwhat
        return

    def construct_viewdata(self): #bruce 050418; this replaces old assy.data attribute for writing mmp files
        #bruce 050421: extend this for saving per-part views (bug 555)
        grpl1 = self.tree.part.viewdata_members(0)
        # Now grab these from the other parts too,
        # but store them in some other way which won't mess up old code which reads the file we'll write these into
        # (namely, as some new mmp record type which the old code would ignore)...
        # or just as a Csys with a name the old code will not store!
        # (This name comes from the argument we pass in.)
        partnodes = self.shelf.members # would not be correct to use self.topnodes_with_own_parts() here
        grpl1 = list(grpl1) # precaution, not needed for current implem as of 050421
        for i,node in zip(range(len(partnodes)),partnodes):
            ll = node.part.viewdata_members(i+1)
            grpl1.extend(ll)
        #bruce 050429 part of fix for bug 413: insulate self from misguided self.changed()
        # done when this Group is made.
        oldmod = self.begin_suspend_noticing_changes()
        res = Group("View Data", self, None, grpl1)
        self.end_suspend_noticing_changes(oldmod)
        return res

    def init_current_selgroup(self):
        self._last_current_selgroup = self.tree
        return

    next_clipboard_item_number = 1 # initial value of instance variable
    def name_autogrouped_nodes_for_clipboard(self, nodes, howmade = ""):
        """
        Make up a default initial name for an automatically made Group
        whose purpose is to keep some nodes in one clipboard item.
           The nodes in question might be passed, but this is optional
        (but you have to pass None or [] if you don't want to pass them),
        and they might not yet be in the clipboard, might not be the complete set,
        and should not be disturbed by this method in any way.
           A word or phrase describing how the nodes needing this group were made
        can also optionally be passed.
           Someday we might use these args (or anything else, e.g. self.filename)
        to help make up the name.
        """
        # original version: return "<Clipboard item>"
        # bruce 050418: to improve this and avoid the unfixed bug of '<' in names
        # (which mess up history widget's html),
        # I'll use "Clipboard item <n>" where n grows forever, per-file,
        # except that rather than storing it, I'll just look at the nodes now in the file,
        # and remember the highest one used while the file was loaded in the session.
        # (So saving and reloading the file will start over based on the numbers used in the file,
        #  which is basically good.)
        #e (Should I use a modtime instead (easier to implement, perhaps more useful)? No;
        #   instead, someday make that info available for *all* nodes in a 2nd MT column.)
        prefix = "Clipboard item" # permit space, or not, between this and a number, to recognize a number
        for node in self.shelf.members:
            name = node.name
            number = None
            if name.startswith(prefix):
                rest = name[len(prefix):].strip()
                if rest and rest.isdigit():
                    try:
                        number = int(rest)
                    except:
                        # can this happen (someday) for weird unicode digits permitted by isdigit? who knows...
                        print "ignoring clipboard item name containing weird digits: %r" % (name,)
                        number = None
            if number is not None and self.next_clipboard_item_number <= number:
                # don't use any number <= one already in use
                self.next_clipboard_item_number = number + 1
        res = "%s %d" % (prefix, self.next_clipboard_item_number)
        self.next_clipboard_item_number += 1 # also don't reuse this number in this session
        return res
    
    # == Parts

    prefs_node = None #bruce 050602; default value of instance variable; experimental
    
    def topnode_partmaker_pairs(self): #bruce 050602
        """
        Return a list of (node, partclass) pairs,
        for each node (in the tree of our nodes we'd display in a model tree)
        which should be at the top of its own Part of the specified Part subclass.
           The partclass might actually be any Part constructor with similar API
        to a Part subclass, though as of 050602 it's always a Part subclass.
           Return value is a mutable list owned by the caller (nothing will modify it
        unless caller does (more precisely, except via caller's reference to it)).
           Implem note: we don't ask the nodes themselves for the partclass,
        since it might depend on their position in the MT rather than on the nodetype.
        """
        res = [(self.tree, MainPart)]
        for node in self.shelf.members:
            res.append(( node, ClipboardItemPart ))
        if self.prefs_node is not None:
            res.append(( self.prefs_node, MainPrefsGroupPart ))
        return res

    def topnodes_with_own_parts(self): #bruce 050602; should match topnode_partmaker_pairs
        res = [self.tree] + self.shelf.members
        if self.prefs_node is not None:
            res.append( self.prefs_node)
        return res

    def all_parts(self): #bruce 080319
        """
        Return all Parts in assy. Assume without checking
        that update_parts (or the part of it that fixes .part structure)
        has been run since the last time assy's node tree structure changed.
        """
        return [topnode.part for topnode in self.topnodes_with_own_parts()]
    
    def update_parts(self,
                     do_post_event_updates = True,
                     do_special_updates_after_readmmp = False ):
        """
        For every node in this assy, make sure it's in the correct Part,
        creating new parts as necessary (of the correct classes).
        
        Also break any inter-part bonds, and set the current selgroup
        (fixing it if necessary).

        Also call env.do_post_event_updates(), unless the option
        do_post_event_updates is false.

        Also do special updates meant to be done just after models
        are read by readmmp (or after part of them are inserted by insertmmp),
        if the option do_special_updates_after_readmmp is True.
        Some of these might happen before any updaters run in this call
        (and might be desirable to do before they *ever* run
         to make it safe and/or effective to run the updaters),
        so be sure to pass this on the first update_parts call
        (which happens when updaters are enabled by kluge_main_assy.assy_valid)
        after readmmp or insertmmp modifies assy.

        [See also the checkparts method.]        
        """
        #bruce 080319 added option do_special_updates_after_readmmp
        #
        #bruce 071119 revised docstring, added do_post_event_updates option
        # (which was effectively always True before).
        #
        #bruce 060127: as of now, I'll be calling update_parts
        # before every undo checkpoint (begin and end both), so that all resulting changes
        # (and the effect of calling assy.changed, now often done by do_post_event_updates as of yesterday)
        # get into the same undo diff.) [similar comment is in do_post_event_updates]
        #
        ###@@@ revise the following comment, it's just notes during development:
        # this is a simple brute-force scan, which might be good enough, and if so might be the simplest method that could work.
        # so if it works and seems ok to use whenever nodes change parts, then take care of entirely new nodes somehow (mol init),
        # and then just call this whenever needed... and it should be ok to add nodes to parts in addmember, when they're new
        # (and when dad has a part); and to do this to kids when groups with no parts are added to nodes with parts.
        # So only for a node-move must we worry and do it later... or so it seems, 050308 806pm.

        #bruce 050602 revised the following:
        for (node, part_constructor) in self.topnode_partmaker_pairs():
            self.ensure_one_part( node, part_constructor)
        
        # now all nodes have correct parts, so it's safe to break inter-part bonds.
        # in the future we're likely to do this separately for efficiency (only on nodes that might need it).
        partnodes = self.topnodes_with_own_parts() # do this again in case the nodes changed (though I doubt that can happen)
        for node in partnodes:
            # do this for all parts, even though the experimental prefsnode doesn't need it (as such)
            # (as a kluge, it might use it for smth else; if so, could #e rename the method and then say this is no longer a kluge)
            node.part.break_interpart_bonds()
            # note: this is not needed when shelf has no members, unless there are bugs its assertions catch.
            # but rather than not do it then, I'll just make it fast, since it should be able to be fast
            # (except for needing to recompute externs, but probably something else would need to do that anyway).
            # [bruce 050513] [####@@@@ review this decision later]
        
        # now make sure current_selgroup() runs without errors, and also make sure
        # its side effects (from fixing an out of date selgroup, notifying observers
        # of any changes (e.g. glpane)) happen now rather than later.
        sg = self.current_selgroup()
        # and make sure selgroup_part finds a part from it, too
        assert self.selgroup_part(sg)
        
        if do_special_updates_after_readmmp:
            # do the "pre-updaters" updates of this kind.
            # initial kluge: don't use registration, or pass new args to
            # env.do_post_event_updates, just hardcode the before and after
            # updaters. This also makes it easier to run only on the correct assy
            # (self).
            from dna.updater.fix_after_readmmp import fix_after_readmmp_before_updaters
            fix_after_readmmp_before_updaters(self)
        
        if do_post_event_updates:
            # 050519 new feature: since bonds might have been broken above
            # (by break_interpart_bonds), do this too:
            ## self.update_bonds() #e overkill -- might need to be optimized
            env.do_post_event_updates() #bruce 050627 this replaces update_bonds
        
        if do_special_updates_after_readmmp:
            # Do the "post-updaters" updates of this kind.
            # For now, there is only one (hardcoded), for the dna updater.
            # And [bruce 080319 bugfix] it's only safe if the last potential run
            # of the dna updater (in env.do_post_event_updates, above)
            # actually happened, and succeeded.
            from dna.updater.fix_after_readmmp import fix_after_readmmp_after_updaters            
            import model.global_model_changedicts as global_model_changedicts
            from model.global_model_changedicts import LAST_RUN_SUCCEEDED
            if global_model_changedicts.status_of_last_dna_updater_run == LAST_RUN_SUCCEEDED:
                fix_after_readmmp_after_updaters(self)
            else:
                print "fyi: skipped fix_after_readmmp_after_updaters since status_of_last_dna_updater_run = %r, needs to be %r" % \
                      ( global_model_changedicts.status_of_last_dna_updater_run, LAST_RUN_SUCCEEDED )
            pass

        try:
            self.fix_nodes_that_occur_twice() #bruce 080516
        except:
            msg = "\n*** BUG: exception in %r.fix_nodes_that_occur_twice(); " \
                  "will try to continue" % self
            print_compact_traceback(msg + ": ")
            msg2 = "Bug: exception in fix_nodes_that_occur_twice; " \
                   "see console prints. Will try to continue."
            env.history.redmsg( msg2 )
            pass
        
        return # from update_parts

    def ensure_one_part(self, node, part_constructor): #bruce 050420 revised this to help with bug 556; revised again 050527
        """
        Ensure node is the top node of its own Part, and all its kids are in that Part,
        either by verifying this situation, or creating a new Part just for node and its kids.
        Specifically:
           If node's part is None or not owned by node (ie node is not its own part's topnode),
        give node its own new Part using the given constructor (permitting the new part to copy some
        info from node's old part, like view attrs, if it wants to).
        (Class is not used if node already owns its Part.)
           If node's kids (recursively) are not in node's (old or new) part, add them.
        [But don't try to break inter-Part bonds, since when this is run,
         some nodes might still be in the wrong Part, e.g. when several nodes
         will be moved from one part to another.]
           We have no way to be sure node's old part doesn't have other nodes besides
        our node's recursive kids; caller can assure this by covering all nodes with some call
        of this method.
        """
        #bruce 050420: don't remove node from its old wrong part. Old code [revised 050516] was:
##        if node.part and node is not node.part.topnode: #revised 050513
##            # this happens, e.g., when moving a Group to the clipboard, and it becomes a new clipboard item
##            node.part.remove(node) # node's kids will be removed below
##            assert node.part is None
##        if node.part is None:
        if node.part is None or node.part.topnode is not node: # if node has no part or does not own its part (as its topnode)
            part1 = part_constructor(self, node) # make a new part with node on top -- uses node's old part (if any) for initial view
            assert node.part is part1 # since making the new part should have added node to it, and set node.part to it
            assert node is node.part.topnode
        # now make sure all node's kids (recursively) are in node.part
        addmethod = node.part.add
        node.apply2all( addmethod ) # noop for nodes already in part;
            # also auto-removes nodes from their old part, if any;
            # also destroys emptied parts.
        return

    def fix_nodes_that_occur_twice(self): # bruce 080516
        """
        Detect, report, and fix nodes that occur more than once
        as group members under self.root.
        """
        # WARNING: the code here that runs when this kind of error is detected
        # is untested (as of the initial commit on 080516). That's ok, since
        # the call is exception-protected, and that protection has been tested.
        #
        # Motivation: there have been bugs that prevented saving an mmp file
        # that could have been caused by some chunks occurring more than once
        # in the internal model tree. (One such bug turned out to have another
        # cause, and it's unconfirmed that any bug has this cause, but it's
        # possible in principle, or could happen for some new bug.)
        # 
        # This kind of bug is bad enough to always check for (since the check
        # can be fast), and if found, to always report and fix. The initial check
        # shouldn't be too slow, since we've already scanned every atom (in the
        # caller update_parts) and this only needs to scan all nodes. If it finds
        # a problem, it scans again, doing more work to know how to report and fix
        # the problem.
        nodes_seen = {} # id(node) -> node, for all nodes in assy.tree
        nodes_seen_twice = {} # same, but only for nodes seen more than once
        def func(node):
            if node is None:
                # should never happen, but if it does, don't be confused
                # (todo: actually check for isinstance Node)
                print "bug: found None in place of a node, inside", self
                return # filter this later (bug: won't always happen)
            if nodes_seen.has_key(id(node)):
                # error; save info to help fix it later
                nodes_seen_twice[id(node)] = node
            nodes_seen[id(node)] = node
            return
        self.root.apply2all(func)
        if nodes_seen_twice:
            # bug. report and try to fix.
            print "\n*** Bug found by %r.fix_nodes_that_occur_twice()" % self
            msg2 = "Bug: some node occurs twice in the model; " \
                   "see console prints for details. Will try to continue."
            env.history.redmsg(msg2)
            # error details will now just be printed as we discover them
            print "for %d nodes:" % len(nodes_seen_twice), nodes
            # To fix, first decide which parent is legitimate for each duplicate
            # node (which is node.dad if that parent node was seen),
            # then filter all members lists to only include one occurrence
            # of each node and only inside its legitimate parent.
            # But if existing parent is not legit, change node.dad to
            # first legal one.
            parents_seen = {}
            for m in nodes_seen_twice.itervalues():
                parents_seen[id(m)] = [] # even if not found again below
            def func2(node):
                if node.is_group():
                    for m in node.members:
                        if nodes_seen_twice.has_key(id(m)):
                            parents_seen[id(m)].append( node)
                                # might list one parent twice, but only consecutively
                return
            self.root.apply2all(func2)
            # parents_seen now knows all the groups whose members lists need
            # filtering (as entries in one of its parent-list values)
            # (but we may not bother using it for that optim),
            # and helps us figure out which parent of each node is legit.
            current_parent_slot = [None] # kluge
            nodes_returned_true = {}
            def fixer(node):
                """
                Fix node to have correct parent, and return True if it should
                remain in the place where we just saw it.
                (Can be passed to filter() over a group's members list.)
                """
                if node is None:
                    return False # todo: actually check for isinstance Node
                if not nodes_seen_twice.has_key(id(node)):
                    return True
                if nodes_returned_true.has_key(id(node)):
                    # don't think about it again, once we said where it goes,
                    # and make sure it's not allowed anywhere else
                    # (in same parent or another one)
                    return False
                if nodes_seen.has_key(id(node.dad)): # correct even if dad is None
                    legit_parent = node.dad
                else:
                    candidates = parents_seen[id(node)]
                    if not candidates:
                        # should never happen or we would not have seen this node
                        print "should never happen: no parent for", node
                        return False
                    oldp = node.dad # for debug print
                    legit_parent = node.dad = candidates[0]
                    node.changed_dad() ####k safe now?
                    print "changed parent of node %r from %r to %r" % (node, oldp, node.dad)
                    if not nodes_seen.has_key(id(node.dad)):
                        print "should never happen: node.dad still not in nodes_seen for", node
                        # assuming that doesn't happen, node.dad is only fixed once per node
                    pass
                # now see if legit_parent is the current one
                if legit_parent is current_parent_slot[0]:
                    nodes_returned_true[id(node)] = node
                    return True
                return False
            def func3(node):
                if node.is_group():
                    # filter its members through fixer
                    current_parent_slot[0] = node
                    oldmembers = node.members
                    newmembers = filter( fixer, oldmembers)
                    if len(newmembers) < len(oldmembers):
                        print "removing %d members from %r, " \
                              "changing them from %r to %r" % \
                              ( len(oldmembers) - len(newmembers),
                                node, oldmembers, newmembers )
                        node.members = newmembers
                        node.changed_members() ###k safe now?
                        pass
                    pass
                return
            self.root.apply2all( func3)
            print
            pass # end of case for errors detected and fixed
        return # from fix_nodes_that_occur_twice
                
    # == Part-related debugging functions

    def checkparts(self, when = ""):
        """
        make sure each selgroup has its own Part, and all is correct about them
        """
        # presumably this is only called when debug_flags.atom_debug,
        # but that's up to the caller, and as of 080314 there are many calls,
        # including at least one which calls it even when not atom_debug.
        for node in self.topnodes_with_own_parts():
            try:
                assert node.is_top_of_selection_group() ##e rename node.is_selection_group()??
                assert node.part.topnode is node # this also verifies each node has a different part, which is not None
                kids = []
                node.apply2all( kids.append ) # includes node itself
                for kid in kids:
                    #bruce 060412 added output string to this assert
                    assert kid.part is node.part, "%r.part == %r, %r.part is %r, should be same" % (kid, kid.part, node, node.part)
                ## assert node.part.nodecount == len(kids), ...
                if not (node.part.nodecount == len(kids)):
                    # Note: this now fails if you make duplex under dna updater,
                    # undo to before that, then redo. And nodecount is only used
                    # to destroy Parts, which is dubious since Undo can revive
                    # them, and is probably harmless to skip since only non-assert
                    # side effect is assy.forget_part, but assy probably checks current
                    # part before returning it (#k verify).
                    # So, change it into a minor debug print for now, but,
                    # leave it enough on to be told by other developers about the causes.
                    # There is still a bug this may signify, since duplex/undo/redo
                    # fails to recreate the duplex!
                    # [bruce 080325]
                    if not env.seen_before("nodecount bug for Part %#x" % (id(node.part),)):
                        msg = "\nbug for %r: node.part.nodecount %d != len(kids) %d" % \
                              (node.part, node.part.nodecount, len(kids))
                        print msg
            except:
                #bruce 080325 revised message, removed re-raise at end;
                #bruce 080410 revising again -- this seems to happen when pasting CX4 with hotspot
                # into free space in its own clipboard item, so reducing the print messiness
                # until we can debug this
                if debug_flags.atom_debug:
                    msg = "\n***BUG?: ignoring exception in checkparts(%s) of %r about node %r" % \
                          (when and `when` or "", self, node)
                    print_compact_traceback(msg + ": ")
                else:
                    print "exception in checkparts about node %r ignored, set debug_flags to see" % \
                          (node,)
                # this would be useful, but doesn't seem to work right in this context:
                ## if not when:
                ##     print_compact_stack(" ... which was called from here: ") #bruce 080314
                pass
            continue
        return

    # ==

    def draw(self, glpane): #bruce 050617 renamed win arg to glpane, and made submethod use it for the first time
        if debug_flags.atom_debug and self.own_window_UI:
            #bruce 060224 added condition, so we don't keep reporting this old bug in MMKit Library ThumbView:
            # AssertionError: node.part.nodecount 3 != len(kids) 1
            # ...
            # self <assembly.Assembly instance at 0xd1d62b0>,
            # glpane <ThumbView.MMKitView object at 0xcc38f00>: [main.py:186] [ThumbView.py:193] [ThumbView.py:594] [assembly.py:513]
            try:
                self.checkparts()
            except: #bruce 051227 catch exception in order to act more like non-atom_debug version
                print_compact_traceback("atom_debug: exception in checkparts; drawing anyway though this might not work: ")
                print_compact_stack("atom_debug: more info about that exception: self %r, glpane %r: " % (self, glpane))
        if self.part is not None: #k not None condition needed??
            self.part.draw(glpane)
        return
    
    # == current selection group (see it and/or change it)

    def current_selgroup_iff_valid(self):
        """
        If the current selection group, as stored (with no fixing!),
        is valid in all ways we can think of checking
        (except any ways related to Parts, which are not examined here),
        return it, otherwise return None (not an error).
        Never has side effects.
        """
        sg = self._last_current_selgroup
        if not self.valid_selgroup( sg):
            return None
        return sg

    def valid_selgroup(self, sg):
        """
        If the GIVEN (not current) selection group (with no fixing!)
        is valid in all ways we can think of checking
        (except ways related to its .part, which is not examined -- see selgroup_part for that)
        as a candidate for being or becoming our current selection group,
        then return True, otherwise False (not an error).
        Never has side effects.
        """
        if sg is None: return False
        if sg.assy is not self: return False
        if not sg.is_top_of_selection_group():
            return False
        if not (self.root.is_ascendant(sg) or self.prefs_node is sg): #bruce 050602 kluge: added prefs_node
            return False # can this ever happen??
        # I think we won't check the Part, even though it could, in theory,
        # be present but wrong (in the sense that sg.part.topnode is not sg),
        # since that way, this method can be independent of Parts,
        # and since is_top_of_selection_group should have been enough
        # for what this method is used for. Logically, we use this to see
        # the selgroup structure, but consider it lower-level than where we
        # know that each selgroup wants its own Part (and maintain that).
        return True

    def current_selgroup(self):
        """
        If the current selection group is valid as stored, return it.
        If not, try to fix it, choosing a new one which includes the stored one if possible
        (this situation might be normal after a DND move of a whole clipboard item
         into the inside of some other Part),
        or the main part (self.tree) if not (this might happen if some code deletes nodes
        without changing the selection group).
           Like current_selgroup_iff_valid(), ignore its Part; see selgroup_part for that.
        Also, new Parts are never made (or old Parts revised) in this method.
           If the current selgroup is changed, the new one is both returned and stored.
        """
        sg = self.current_selgroup_iff_valid()
        if sg is not None:
            return sg
        # now we're a bit redundant with that method (this seems necessary);
        # also, at this point we're almost certain to debug print and/or
        # to change self._last_current_selgroup (via self.set_current_selgroup ###k).
        sg = self._last_current_selgroup
        # since that guy was invalid, we'll definitely forget about it now
        # except for its use below as 'sg' (in this run of this method).
        self._last_current_selgroup = None # hopefully to be revised below
        if sg is not None and sg.assy is self and self.root.is_ascendant(sg):
            assert not sg.is_top_of_selection_group() # the only remaining way it could have been wrong
            # this is the one case where we use the invalid _last_current_selgroup in deciding on the new one.
            newsg = sg.find_selection_group() # might be None
            if newsg is None:
                newsg = self.tree
        else:
            newsg = self.tree
        # now newsg is the one we'll *try* to change to and return, if *it* is valid.
        # (if it is not None but not valid, that's probably a bug, and we won't change to it;
        #  ideally we'd change to self.tree then, but since it's probably a bug we won't bother.)
        if newsg is None:
            #k probably can't happen unless self.tree is None, which I hope never happens here
            if debug_flags.atom_debug:
                print_compact_stack("atom_debug: cur selgroup None, no tree(?), should never happen: ")
            # we already stored None, and it's not good to call current_selgroup_changed now (I think) ##k
            return None
        # Note: set_current_selgroup looks at prior self._last_current_selgroup,
        # so the fact that we set that to None (above) is important.
        # Also, what if newsg is sg (should never happen here)?
        # Then it won't be valid (else we'd have returned at top of this method)
        # and we'll see debug prints in set_current_selgroup.
        self.set_current_selgroup( newsg) # this stores it and notifies observers if any (eg updates glpane)
        return self._last_current_selgroup # (this will be same as newsg, or debug prints already occurred)

    def selgroup_part(self, sg):
        """
        Given a valid selgroup sg (or None), check that it's its .part's topnode,
        and if so return its .part, and if not return None after emitting debug prints
        (which always indicates a bug, I'm 90% sure as I write it -- except maybe during init ###k #doc).
        """
        try:
            assert sg is not None
            assert sg.part is not None, "sg %r .part should not be None" % (sg,) #bruce 060412
            assert sg.part.topnode is not None, "part %r topnode is None, should be %r" % (sg.part, sg) #bruce 060412
            assert sg.part.topnode is sg, "part %r topnode is %r should be %r" % (sg.part, sg.part.topnode, sg)
        except:
            print_compact_traceback("bug: in assy %r, selgroup.part problem: " % self ) # printing assy in case it's not the main one
            print_compact_stack(" location of selgroup.part problem: ")
            return None
        return sg.part

    # ==
    
    def current_selgroup_index(self): #bruce 060125 so Undo can store "current part" w/o doing update_parts [guess; wisdom unreviewed]
        """
        Return the index of the current selgroup, where 0 means self.tree and 1, 2, etc refer to
        the clipboard items in their current positional order. [Note that this won't be useful for out-of-order redo.]
        """
        sg = self.current_selgroup()
        if sg is self.tree:
            return 0
        try:
            return self.shelf.members.index(sg) + 1
        except:
            print_compact_traceback("bug in current_selgroup_index, returning 0: ")
            return 0
        pass

    def selgroup_at_index(self, i): #bruce 060125 for Undo
        """
        Return the selection group at index i (0 means self.tree),
        suitable for passing to set_current_selgroup.
        """
        if i == 0:
            return self.tree
        try:
            return self.shelf.members[i-1]
        except:
            print_compact_traceback("bug in selgroup_at_index(%d), returning self.tree: " % (i,) )
            return self.tree
        pass
    
    # == changing the current selection group

    ##e move this lower down?
    def fyi_part_topnode_changed(self, old_top, new_top):
        """
        [private method for a single caller in Part]
        Some Part tells us that its topnode changed from old_top to new_top.
        If our current selgroup happened to be old_top, make it now be new_top,
        but don't emit a history message about this change.
        [#e: not sure if we should do any unpicking or updating, in general;
         current caller doesn't need or want any.]
        """
        if self._last_current_selgroup is old_top:
            self._last_current_selgroup = new_top
            # no need (in fact, it would be bad) to call current_selgroup_changed, AFAIK
            # (does this suggest that "current part" concept ought to be more
            #  primitive than "current selgroup" concept??)
        # now the Part situation should be ok, no need for assy.update_parts
        return

    def set_current_part(self, part):
        self.set_current_selgroup( part.topnode)
    
    def set_current_selgroup(self, node): #bruce 050131 for Alpha; heavily revised 050315; might need options wrt history msg, etc
        """
        Set our current selection group to node, which should be a valid one.
        [public method; no retval]
        """
        assert node
        prior = self.current_selgroup_iff_valid() # don't call current_selgroup itself here --
            # it might try to "fix an out of date current selgroup"
            # and end up unpicking the node being passed to us.
        if node is prior:
            return # might be redundant with some callers, that's ok [#e simplify them?]
        if prior is None and self._last_current_selgroup:
            prior = 0 # tell submethod that we don't know the true prior one
        if not self.valid_selgroup(node):
            # probably a bug in the caller. Complain, and don't change current selgroup.
            if debug_flags.atom_debug:
                print_compact_stack("atom_debug: bug: invalid selgroup %r not being used" % (node,))
            #e if this never happens, change it to raise an exception (ie just be an assert) ###@@@
            return
        #####@@@@@ now inline the rest
        # ok to set it and report that it changed.
        self._last_current_selgroup = node
        self.current_selgroup_changed(prior = prior) # as of 050315 this is the only call of that method
        return
    
    def current_selgroup_changed(self, prior = 0): #bruce 050131 for Alpha
        """
        #doc; caller has already stored new valid one; prior == 0 means unknown -- caller might pass None
        """
        #e in future (post-Alpha) this might revise self.molecules, what to show in glpane, etc
        # for now, make sure nothing outside it is picked!
        # This is the only place where that unpicking from changing selgroup is implemented. ###@@@ verify that claim

        sg = self._last_current_selgroup

        # unpick everything in a different selgroup (but save the message about this for last)
        didany = self.root.unpick_all_except( sg )

        # notify observers of changes to our current selgroup (after the side effect of the unpick!)
        self.o.set_part( self.part)
        ## done by that: self.o.gl_update()
        
        # print a history message about a new current Part, if possible #####@@@@@ not when initing to self.tree!
        try:
            # during init, perhaps lots of things could go wrong with this, so catch them all
            msg = "showing %r (%s)" % (sg.part.topnode.name, sg.part.location_name())
                # AttributeError: 'NoneType' object has no attribute 'topnode' ######@@@@@@
            ## this was too frequent to leave them all in, when clicking around the clipboard:
            ## env.history.message( greenmsg( msg)) ###e need option for this?
            env.history.message( msg, transient_id = "current_selgroup_changed")
        except:
            if debug_flags.atom_debug:
                print_compact_traceback("atom_debug: bug?? or just init?: can't print changed-part msg: ")
            pass

        # emit a message about what we unpicked, if anything
        if didany:
            try: # precaution against new bugs in this alpha-bug-mitigation code
                # what did we deselect?
                # [note, prior might be None or 0, so boolean test is needed [bruce guess/comment 050516]]
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
                if debug_flags.atom_debug:
                    raise 
                msg = "Warning: deselected some previously selected items"
            try:
                env.history.message( orangemsg( msg))
            except:
                pass # too early? (can this happen?)

        return # from current_selgroup_changed

    # == general attribute code
    def initialize():
        if (Initialize.startInitialization(__name__)):
            return
        # attrnames to delegate to the current part
        # (ideally for writing as well as reading, until all using-code is upgraded) ###@@@ use __setattr__ ?? etc??
        Assembly.part_attrs = ['molecules','selmols','selatoms','homeView','lastView']
            ##part_methods = ['selectAll','selectNone','selectInvert']###etc... the callable attrs of part class??
        Assembly.part_methods = filter( lambda attr:
                                        not attr.startswith('_')
                                        and callable(getattr(Part_class,attr)), # note: this tries to get self.part before it's ready...
                                        dir(Part_class) ) #approximation!
        #####@@@@@ for both of the following:
        Assembly.part_attrs_temporary = ['bbox','center','drawLevel'] # temp because caller should say assy.part or be inside self.part
        Assembly.part_attrs_review = ['ppa2','ppa3','ppm']
        ###@@@ bruce 050325 removed 'alist', now all legit uses of that are directly on Part or Movie
        ### similarly removed 'temperature' (now on assy like it was),'waals' (never used)
        #e in future, we'll split out our own methods for some of these, incl .changed
        #e and for others we'll edit our own methods' code to not call them on self but on self.assy (incl selwhat)
        Assembly.part_attrs_all = Assembly.part_attrs + Assembly.part_attrs_temporary + Assembly.part_attrs_review

        Initialize.endInitialization(__name__)

    # can we use the decorator @staticmethod instead?
    initialize = staticmethod(initialize)
    
    def __getattr__(self, attr): # in class Assembly
        if attr.startswith('_'): # common case, be fast
            raise AttributeError, attr
        elif attr == 'part':
            sg = self.current_selgroup() # this fixes it if possible; should always be a node but maybe with no Part during init
            ## return self.parts[node_id(sg)]           
#bruce 050528 removing this since it prevents clipboard from opening in MT once it's closed, when displaying a clipboard item!
##            if 1:
##                # open all containing nodes below assy.root (i.e. the clipboard, if we're a clipboard item)
##                containing_node = sg.dad
##                while containing_node is not None and containing_node is not self.root:
##                    containing_node.open = True
##                    containing_node = containing_node.dad
            part = self.selgroup_part(sg)
            if part is None:
##                #e [this IS REDUNDANT with debug prints inside selgroup_part]
##                # no point in trying to fix it -- if that was possible, current_selgroup() did it.
##                # if it has no bugs, the only problem it couldn't fix would be assy.tree.part being None.
##                # (which might happen during init, and trying to make a part for it might infrecur or otherwise be bad.)
##                # so if following debug print gets printed, we might extend it to check whether that "good excuse" is the case.
##                if 1:
##                    print_compact_stack("atom_debug: fyi: assy %r getattr .part finds selgroup problem: " % self )
                return None
            return part
        elif attr in self.part_attrs_all:
            # delegate to self.part
            try:
                part = self.part
            except:
                print "fyi: following exception getting self.part happened just before we looked for its attr %r" % (attr,)
                raise
            try:
                return getattr(part, attr) ###@@@ detect error of infrecur, since part getattr delegates to here??
            except:
                print "fyi: following exception in assy.part.attr was for attr = %r" % (attr,)
                raise
        elif attr in self.part_methods:
            # attr is a method-name for a method we should delegate to our current part.
            # it's not enough to return the current self.part's bound method...
            # we need to create and return a fake bound method of our own
            # which, when called in the future, will delegate to our .part *at that time* --
            # in case it is not called immediately, but stored away (e.g. as a menu item's callable)
            # and used later when our current part might have changed.
            def deleg(*args,**kws):
                meth = getattr(self.part, attr)
                return meth(*args,**kws)
            return deleg
        raise AttributeError, attr

    # == tracking undoable changes that aren't saved

    def changed_selection(self): #bruce 060129; this will need revision if we make it part-specific
        # see also same-named Node method
        if self._suspend_noticing_changes:
            return
        self._selection_change_indicator = env.change_counter_for_changed_objects()
        return

    def changed_view(self): #bruce 060129 ###@@@ not yet called enough
        if self._suspend_noticing_changes:
            return
        self._view_change_indicator = env.change_counter_for_changed_objects()
        return
    
    # == change-tracking [needs to be extended to be per-part or per-node, and for Undo]
    
    def has_changed(self):
        """
        Report whether this Assembly (or something it contains)
        has been changed since it was last saved or loaded from a file.
        See self.changed() docstring and comments for more info.
        Don't use or set self._modified directly!
           #e We might also make this method query the current mode
        to see if it has changes which ought to be put into this Assembly
        before it's saved.
        """
        return self._modified
    
    def changed(self): # by analogy with other methods this would be called changed_model(), but we won't rename it [060227]
        """
        Record the fact that this Assembly (or something it contains)
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
           See also: changed_selection, changed_view.
        """
        # bruce 050107 added this method; as of now, all method names (in all
        # classes) of the form 'changed' or 'changed_xxx' (for any xxx) are
        # hereby reserved for this purpose! [For beta, I plan to put in a
        # uniform system for efficiently recording and propogating change-
        # notices of that kind, as part of implementing Undo (among other uses).]

        if self._suspend_noticing_changes:
            return #bruce 060121 -- this changes effective implem of begin/end_suspend_noticing_changes; should be ok
        
        newc = env.change_counter_for_changed_objects() #bruce 060123
        
        if debug_assy_changes:
            oldc = self._model_change_indicator
            print
            self.modflag_asserts()
            if oldc == newc:
                print "debug_assy_changes: self._model_change_indicator remains", oldc
            else:
                print_compact_stack("debug_assy_changes: self._model_change_indicator %d -> %d: " % (oldc, newc) )
            pass
        
        self._model_change_indicator = newc
            ###e should optimize by feeding new value from changed children (mainly Nodes) only when needed
            ##e will also change this in some other routine which is run for changes that are undoable but won't set _modified flag

        if not self._modified:
            self._modified = 1
            # Feel free to add more side effects here, inside this 'if'
            # statement, even if they are slow! They will only run the first
            # time you modify this Assembly since it was last saved, opened, or closed
            # (i.e. since the last call of reset_changed).

            # A long time ago, this is where we'd emit a history message about unsaved changes.
            # Now we denote a file change by adding an asterisk (or whatever the user prefers)
            # to the end of the filename in the window caption.
            self.w.update_mainwindow_caption_properly() #e should this depend on self.own_window_UI? [bruce 060127 question] ####@@@@
            if debug_assy_changes:
                print time.asctime(), self, self.name
                print_compact_stack("atom_debug: part now has unsaved changes")
            pass
        
        # If you think you need to add a side-effect *here* (which runs every
        # time this method is called, not just the first time after each save),
        # that would probably be too slow -- we'll need to figure out a different
        # way to get the same effect (like recording a "modtime" or "event counter").
        
        self.modflag_asserts() #e should speed-optimize this eventually
        
        return # from Assembly.changed()

    def modflag_asserts(self): #bruce 060123; revised 060125
        """
        check invariants related to self._modified
        """
        if 1: ###@@@ maybe should be: if debug_flags.atom_debug:
            hopetrue = ( (not self._modified) == (self._model_change_indicator == self._change_indicator_when_reset_changed) )
            if not hopetrue:
                print_compact_stack(
                    "bug? (%r.modflag_asserts() failed; %r %r %r): " % \
                      (self, self._modified, self._model_change_indicator, self._change_indicator_when_reset_changed)
                )
        return

    # Methods to toggle change-noticing during specific sections of code.
    # (These depend on assy._modified working as it did on 050109 - 050429;
    #  they'll need review when we add per-Part _modified flag, Undo, etc.)
    # [written by bruce 050110 as helper functions in Utility.py;
    #  renamed and moved here by bruce 050429, re bug 413]

    _suspend_noticing_changes = False
        #bruce 060121 for Undo; depends on proper matching and lack of nesting of following methods,
        # which looks true at the moment; see also use of this in self.changed(), which changes
        # effective implem of following methods.
    
    def begin_suspend_noticing_changes(self): #bruce 060121 revised implem, see comment above and in self.changed()
        """
        See docstring of end_suspend_noticing_changes.
        """
        assert not self._suspend_noticing_changes
        self._suspend_noticing_changes = True # this prevents self.changed() from doing much
        oldmod = self._modified
        self._modified = 1 # probably no longer needed as of 060121
        return oldmod # this must be passed to the 'end' function
        # also, if this is True, caller can safely not worry about
        # calling "end" of this, i suppose; best not to depend on that

    def end_suspend_noticing_changes(self, oldmod):
        """
        Call this sometime after every call of begin_suspend_noticing_changes.
        These begin/end pairs can be nested, but see the caveat below about the oldmod argument in that case.
           The argument should be the begin method's return value, unless you know you want the new situation
        to look "not modified", in which case the argument should be False.
        Note that even calls of self.reset_changed() (between the begin and end methods)
        are not noticed, so if one occurred and should have been noticed,
        this can only be fixed by passing False to this method.
           Caveat: with nested begin/end pairs, if an inner end's oldmod was False
        (instead of the "correct" value returned by its matching begin method),
        then changes after that inner end method *will* (incorrectly) be noticed.
        This is a bug in the present implementation which needs to be worked around.
        It might be inherent in the present API, I don't know; the present API has no
        protection for mismatch-bugs and needs revision anyway.
           It's probably safe even if the Assembly object these methods are being called on
        is not the same for the begin and end methods!
        """
        # docstring by bruce 050429 ; might be wrong due to changes of 060121
        assert self._suspend_noticing_changes
        self._suspend_noticing_changes = False
        self._modified = oldmod
        return

    _change_indicator_when_reset_changed = -1 #bruce 060123 for Undo; as of 060125 it should no longer matter whether the value is even
    
    def reset_changed(self): # bruce 050107
        """
        [private method] #doc this... see self.changed() docstring...
        """
        #bruce 060123 assuming all calls are like File->Save call...
        # actual calls are from MWsem.__init__, File->Open,
        # File->Save (actually saved_main_file; does its own update_mainwindow_caption), File->Close
        if self._suspend_noticing_changes:
            print "warning, possible bug: self._suspend_noticing_changes is True during reset_changed" #bruce guess 060121
        if debug_assy_changes:
            print_compact_stack( "debug_assy_changes: %r: reset_changed: " % self )
        self._modified = 0
        #e should this call self.w.update_mainwindow_caption(changed = False),
        # or fulfill a subs to do that?? [bruce question 060123]

        self._change_indicator_when_reset_changed = self._model_change_indicator #bruce 060125 (eve) revised this; related to bugs 1387, 1388??
            ## = env.change_counter_checkpoint() #bruce 060123 for Undo
            ##k not sure it's right to call change_counter_checkpoint and not subsequently call change_counter_for_changed_objects,
            # but i bet it's ok... more problematic is calling change_counter_checkpoint at all! #######@@@@@@@
            # the issue is, this is not actually a change to our data, so why are we changing self._model_change_indicator??
            # OTOH, if just before saving we always changed our data just for fun, the effect would be the same, right?
            # Well, not sure -- what about when we Undo before... if we use this as a vers, maybe no diffs will link at it...
            # but why would they not? this is not running inside undo, but from an op that does changes like anything else does
            # (namely file save) (open or close is yet another issue since assy is replaced during the cmd ###@@@).
            # so i'm guessing it's ok. let's leave it in and find out. hmm, it might make it *look* like file->save did a change
            # and should be undoable -- but undoing it will have no effect. Really in order to make sure we know that diff
            # is empty, it would be better not to do this, or somehow to know there was no real change.
            # plan: zap the final '= env...' and revise modflag_asserts accordingly. worry about real changes for sure
            # changing counter even if they wouldn't... call checkpoint here even if not using value?!?!?!? #####@@@@@ 060124 230pm
        #bruce 060201 update for bug 1425: if you call self.changed() right after this, you'll asfail unless we
        # call env.change_counter_checkpoint() now (discarding result is ok), for a good reason -- once we "used up"
        # the current value of _model_change_indicator in _change_indicator_when_reset_changed, we better use a different value
        # for the next real change (so it looks like a change)! This would be needed (to make sure checkpoints notice the change)
        # even if the asserts were not being done. So the following now seems correct and required:
        env.change_counter_checkpoint() #bruce 060201 fix bug 1425
        return

    def reset_changed_for_undo(self, change_counters ): #bruce 060123 guess; needs cleanup
        """
        External code (doing an Undo or Redo) has made our state like it was when self.all_change_indicators() was as given.
        Set all self._xxx_change_indicator attrs to match that tuple,
        and update self._modified to match (using self._change_indicator_when_reset_changed without changing it).
           Note that modified flag is false if no model changes happened, even if selection or structural changes happened.
        Thus if we redo or undo past sel or view changes alone, modified flag won't change.
        """
        # in other words, treat self.all_change_indicators() as a varid_vers for our current state... ###@@@
        model_cc, sel_cc, view_cc = change_counters # order must match self.all_change_indicators() retval
        modflag = (self._change_indicator_when_reset_changed != model_cc)
        if debug_assy_changes:
            print_compact_stack( "debug_assy_changes for %r: reset_changed_for_undo(%r), modflag %r: " % \
                                 (self, change_counters, modflag) )
        self._modified = modflag
        self._model_change_indicator = model_cc
        self._selection_change_indicator = sel_cc
        self._view_change_indicator = view_cc
        self.modflag_asserts()
        #####@@@@@ need any other side effects of assy.changed()??
        if self.w:
            self.w.update_mainwindow_caption_properly()
        return
    
    # ==
    
    ## bruce 050308 disabling checkpicked for assy/part split; they should be per-part
    ## and they fix errors in the wrong direction (.picked is more fundamental)
    def checkpicked(self, always_print = 0):
        if always_print:
            print "fyi: checkpicked() is disabled until assy/part split is completed"
        return

    # ==

    def apply2movies(self, func): #bruce 050428
        """
        apply func to all possibly-ever-playable Movie objects we know about.
        (Not to mere sim-param-holders for minimize, etc.)
        """
        if self.current_movie:
            # for now, this is the only one! (even if it's a "mere param-holder".)
            # at some point there'll also be movie nodes in the MT...
            ##e when there can be more than one, perhaps catch exceptions here and/or "or" the retvals together...
            func( self.current_movie)
        return
    
    # ==

    def __str__(self):
        if debug_flags.atom_debug:
            return "<Assembly of file %r" % self.filename + " (id = %r, _debug_name = %r)>" % (id(self), self._debug_name) #bruce 050429
        return "<Assembly of " + self.filename + ">"

    def writemmpfile(self, filename, **options): #bruce 080326 revised
        _options = dict(addshelf = True)
        _options.update(options)
        writemmpfile_assy( self, filename, **_options)
        
    def get_cwd(self):
        """
        Returns the current working directory for assy.
        """
        if self.filename: 
            cwd, file = os.path.split(self.filename)
        else: 
            cwd = env.prefs[workingDirectory_prefs_key]
        return cwd

    # ==

#bruce 060407 zapped this, and the code can be removed soon
##    def become_state(self, state, archive): #bruce 060117 kluge [will it still be needed?]
##        from undo_archive import assy_become_state
##        return assy_become_state(self, state, archive) # this subroutine will probably become a method of class Assembly

    def clear(self): #bruce 060117 kluge [will it still be needed?]
        return undo_archive.assy_clear(self) # this subroutine will probably become a method of class Assembly

    def editUndo(self):
        if self.undo_manager:
            self.undo_manager.editUndo()

    def editRedo(self):
        if self.undo_manager:
            self.undo_manager.editRedo()

    def undo_checkpoint_before_command(self, *args, **kws):
        ## moved into undo_manager: self.update_parts() #bruce 060127, precaution related to fixing bug 1406
        if self.undo_manager:
            return self.undo_manager.undo_checkpoint_before_command(*args, **kws)

    def undo_checkpoint_after_command(self, *args, **kws):
        ## moved into undo_manager: self.update_parts() #bruce 060127, to fix bug 1406
##            #e [or should undo_manager use a callback, to do it even from
##            #   initial and clear checkpoints, and recursive-event ones??]
        if self.undo_manager:
            return self.undo_manager.undo_checkpoint_after_command(*args, **kws)

    def current_command_info(self, *args, **kws):
        #e (will this always go into undo system, or go into some more general current command object in env, instead?)
        if self.undo_manager:
            return self.undo_manager.current_command_info(*args, **kws)

    def clear_undo_stack(self, *args, **kws):
        if self.undo_manager:
            return self.undo_manager.clear_undo_stack(*args, **kws)

    def allNodes(self, class1 = None): #bruce 060224; use more widely?
        """
        Return a new list (owned by caller) of all Nodes in self.tree or self.shelf (including Groups ###untested).
        If class1 is passed, limit them to the instances of that class.
        WARNING: self.shelf might be in the list, if it includes Groups. If this is bad we might revise the API to exclude it.
        """
        res = []
        def func(node):
            if not class1 or isinstance(node, class1):
                res.append(node)
        self.tree.apply2all(func)
        self.shelf.apply2all(func)
        return res
    
    def get_part_files_directory(self): # Mark 060703.
        """
        Returns the Part Files directory for this Assembly, even if it doesn't exist.
        """
        # Maybe find_or_make_part_files_directory() should call this to centralize name creation. Mark 060703.
        if self.filename:
            path_wo_ext, ext = os.path.splitext(self.filename)
            return 0, os.path.abspath(os.path.normpath(path_wo_ext + " Files"))
        else:
            return 1, "I cannot do this until this part is saved."
        
    def find_or_make_part_files_directory(self, make=True):
        """
        Return the Part Files directory for this Assembly. Make it if it doesn't already exist.
        If <make> is False, return the Part Files directory if it already exists. If it doesn't exist, return None.
        
        Specifically, return:
            - on success, return (0, part files directory), 
              or if <make> is False and the Part Files directory does not exist, return (0, None).
            - on error, return (1, errormsg).
        
        About the "Part Files" directory:
        
        The Part Files directory exists next to the current MMP file and has the same name as
        the MMP file (without the .mmp extension) but with the ' Files' suffix. For example, 
        the MMP file "DNA Shape.mmp" will have "DNA Shape Files" as its Part Files directory.
        
        The Part Files directory contains all the associated subdirectories and files for this MMP part,
        such as POV-Ray Scene files (*.pov), movie files (*.dpb), GAMESS files (*.gms), etc.
        
        The Part Files directory currently supports:
            - POV-Ray Scene files (*.pov). 
        
        To be implemented: 
            - Movie files (*.dpb)
            - GAMESS files (*.gms)
            - ESP Image files (*.png)
            - Image files (*.png, *.bmp, etc)
        """
        if self.filename:
            # The current file has been saved, so it is OK to make the Part Files directory.
            path_wo_ext, ext = os.path.splitext(self.filename)
            return find_or_make_any_directory(path_wo_ext + " Files", make = make)
        else:
            if make:
                # Cannot make the Part Files directory until the current file is saved. Return error.
                return 1, "I cannot do this until this part is saved."
            else:
                # The current file has not been saved, but since <make> = False, no error.
                return 0, None
        
    def find_or_make_pov_files_directory(self, make=True):
        """
        Return the POV-Ray Scene Files directory for this Assembly. 
        The POV-Ray Scene Files directory is a subdirectory under the current MMP file's Part Files directory
        and contains all the associated POV-Ray files for this Assembly.
        For any error, return (1, errortext); on success return (0, full_path_of_pov_files_dir).
        In other words, return (errorcode, path_or_errortext).
        """
        errorcode, dir_or_errortext = self.find_or_make_part_files_directory(make = make)
        if errorcode:
            return errorcode, dir_or_errortext
        
        povfiles_dir  = os.path.join(dir_or_errortext, "POV-Ray Scene Files")
        return find_or_make_any_directory(povfiles_dir, make = make)
    
    pass # end of class Assembly

## Assembly = assembly #bruce 060224 thinks this should become the preferred name for the class (and the only one, when practical)

# ==

# specialized kinds of Groups: [bruce 050108/050109]
# [moved from Utility.py since now only used here;
#  TODO: these Group subclasses could all be renamed as private.
#  bruce 071026]

class PartGroup(Group):
    """
    A specialized Group for holding the entire "main model" of an Assembly,
    with provisions for including the "assy.viewdata" elements as initial MT_kids, but not in self.members
    (which is a kluge, and hopefully can be removed reasonably soon, though perhaps not for Alpha).
    """
    def __init__(self, name, assy, dad, members = (), editCommand = None): #bruce 080306
        self._initialkids = [] #bruce 050302, bugfixed 080306 (was a mutable class variable! tho not used as such in its old code)
        Group.__init__(self, name, assy, dad, members = members, editCommand = editCommand)
        return
    # These revised definitions are the non-kluge reason we need this subclass: ###@@@ also some for menus...
    def is_top_of_selection_group(self):
        return True #bruce 050131 for Alpha
    def rename_enabled(self):
        return False
    def drag_move_ok(self):
        return False
    # ... but drag_copy is permitted! (someday, when copying groups is permitted)
    # drop methods should be the same as for any Group
    def permits_ungrouping(self):
        return False
    def _class_for_copies(self, mapping):
        #bruce 080314, preserving original behavior
        del mapping
        return Group
    def node_icon(self, display_prefs):
        # same whether closed or open
        return imagename_to_pixmap("modeltree/part.png")
##    # And this temporary kluge makes it possible to use this subclass where it's
##    # needed, without modifying assembly.py or files_mmp.py:
##    def kluge_set_initial_nonmember_kids(self, lis): #bruce 050302 comment: no longer used, for now
##        """
##        [This kluge lets the csys and datum plane model tree items
##        show up in the PartGroup, without their nodes being in its members list,
##        since other code wants their nodes to remain in assy.viewdata, but they can
##        only have one .dad at a time. Use of it means you can't assume node.dad
##        corresponds to model tree item parent!]
##        """
##        lis = filter( lambda node: node.show_in_model_tree(), lis)
##            # bruce 050127; for now this is the only place that honors node.show_in_model_tree()!
##        self._initialkids = list(lis)
    def MT_kids(self, display_prefs = {}): #bruce 080108 revised semantics
        """
        overrides Group.MT_kids
        """
##        if not self.openable() or not display_prefs.get('open', False):
##            return []
        # (I think this is never called when not self.open and self.openable(),
        #  so don't bother optimizing that case. [bruce 080306])
        regularkids = Group.MT_kids(self, display_prefs)
        if 1 and self.open:
            #bruce 080306 test code, should clean up
            from utilities.debug_prefs import debug_pref, Choice_boolean_False
            want_fake_kid = debug_pref("Model Tree: show fake initial kid?", Choice_boolean_False)
            have_fake_kid = not not self._initialkids
            if have_fake_kid and not want_fake_kid:
                self._initialkids = []
            elif want_fake_kid and not have_fake_kid:
                dad = None # works...
                # Note, if you select it you can get messages like:
                #   atom_debug: bug(?): change_current_selgroup_to_include_self on node with no selgroup; ignored
                # and that clicking elsewhere on MT doesn't deselect it.
                #
                # Note: if dad is self, making the Group apparently adds it
                # to our members list! This seems to be why it was appearing
                # twice, one in the fake top position and once at the
                # bottom (the same node, sharing selection/renaming state).
                _fake_kid = Group("fake initial kid", self.assy, dad)
                self._initialkids = [_fake_kid]
            pass
        return list(self._initialkids) + list(regularkids)
    def edit(self):
        cntl = PartProp(self.assy)
            #bruce comment 050420: PartProp is passed assy and gets its stats from assy.tree.
            # This needs revision if it should someday be available for Parts on the clipboard.
        cntl.exec_()
        self.assy.mt.mt_update()
    def description_for_history(self):
        """
        [overridden from Group method]
        """
        return "Part Name: [" + self.name +"]"
    pass

class ClipboardShelfGroup(Group):
    """
    A specialized Group for holding the Clipboard (aka Shelf).
    """
    def postcopy_in_mapping(self, mapping): #bruce 050524
        assert 0, "ClipboardShelfGroup.postcopy_in_mapping should never be called!"
    def pick(self): #bruce 050131 for Alpha
        msg = "Clipboard can't be selected or dragged. (Individual clipboard items can be.)"
        env.history.statusbar_msg( msg)
    def is_selection_group_container(self):
        return True #bruce 050131 for Alpha
    def rename_enabled(self):
        return False
    def drag_move_ok(self):
        return False
    def drag_copy_ok(self):
        return False
    def drop_on_should_autogroup(self, drag_type, nodes): #bruce 071025
        """
        [overrides Node method]
        """
        # note: drop on clipboard makes a new clipboard item.
        return len(nodes) > 1
    def permits_ungrouping(self):
        return False
    ##bruce 050316: does always being openable work around the bugs in which this node is not open when it should be?
    ###e btw we need to make sure it becomes open whenever it contains the current part. ####@@@@
##    def openable(self): # overrides Node.openable()
##        "whether tree widgets should permit the user to open/close their view of this node"
##        non_empty = (len(self.members) > 0)
##        return non_empty
    def _class_for_copies(self, mapping):
        #bruce 080314, preserving original behavior; probably not needed
        del mapping
        print "why is %r being copied?" % self
            # since I think this should never be called
        return Group
    def node_icon(self, display_prefs):
        del display_prefs # unlike most Groups, we don't even care about 'open'
        non_empty = (len(self.members) > 0)
        if non_empty:
            kluge_pixmap = imagename_to_pixmap("modeltree/clipboard-full.png")
            res = imagename_to_pixmap("modeltree/clipboard-full.png")
        else:
            kluge_pixmap = imagename_to_pixmap("modeltree/clipboard-gray.png")
            res = imagename_to_pixmap("modeltree/clipboard-empty.png")
        # kluge: guess: makes paste tool look enabled or disabled
        ###@@@ clean this up somehow?? believe it or not, it might actually be ok...
        self.assy.w.editPasteAction.setIcon(QtGui.QIcon(kluge_pixmap))
        return res
    def edit(self):
        return "The Clipboard does not yet provide a property-editing dialog."
    def edit_props_enabled(self):
        return False
    def description_for_history(self):
        """
        [overridden from Group method]
        """
        return "Clipboard"    
    def getPastables(self):
        """
        """
        pastables = []
        pastables = filter(is_pastable, self.members)
        return pastables
    pass

class RootGroup(Group):
    """
    A specialized Group for holding the entire model tree's toplevel nodes,
    which (by coincidence? probably more like a historical non-coincidence)
    imitates the assy.root member of the pre-050109 code. [This will be revised... ###@@@]
    [btw i don't know for sure that this is needed at all...]
    ###obs doc, but reuse some of it:
    This is what the pre-050108 code made or imitated in modelTree as a Group called ROOT. ###k i think
    This will be revised soon, because
    (1) the Assembly itself might as well be this Node,
    (2)  the toplevel members of an Assembly will differ from what they are now.
    """
    def postcopy_in_mapping(self, mapping): #bruce 050524
        assert 0, "RootGroup.postcopy_in_mapping should never be called!"
    def pick(self): #bruce 050131 for Alpha
        self.redmsg( "Internal error: tried to select assy.root (ignored)" )
    #e does this need to differ from a Group? maybe in some dnd/rename attrs...
    # or maybe not, since only its MT_kids are shown (not itself) ###@@@
    # (we do use the fact that it differs in class from a Group
    #  as a signal that we might need to replace it... not sure if this is needed)
    pass

# end
