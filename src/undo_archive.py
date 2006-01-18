# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
undo_archive.py

Collect and organize a set of checkpoints of model state and diffs between them,
providing undo/redo ops which apply those diffs to the model state.

$Id$

not tested:
- not well tested; some NFRs below will make testing easier, so do them first

current bugs:
- logic bug: checkpoint, mods, undo to checkpoint - does it go to *that* cp or the prior one? Now the prior one,
  not what i expect... but if we make cps more often this might not be an issue.

before we implement auto-checkpointing, we must:
- pref to enable it, off by default (maybe a persistent debug_pref)
- replace the /tmp/fff kluge, either with pure use of RAM or a safe temporary file

missing features:
- autocheckpoint is nim; for testing could do it on just a few commands, at start of cmd, and supply metainfo too; see begin_op?
- menu items too hard to reach:
  - need to put them into intended positions in main menu, enable/disable actions, revise their text
    (might as well also revise tooltip to include more info, like metainfo)
  - print history message when we do those things
- no metainfo in diffs, like history serno or time or type of diff or cmd that made it

performance:
- too slow
- too much memory usage (no limit on stack length)

missing state:
- doesn't preserve choice of current part
- doesn't save selection state, per-mode state, maybe other kinds of state (prefs, current movie and its data)
- not sure about viewpoint state, might be sort of ok (untested)

possible bugs:
- undo to very start might not work (empty mmp file) (or might work by now)
- if we undo before first save, it might mess with filename (not sure)
- if we undo, proceed differently, and undo, it might have two potential redos (and asfail), or if not, something else
  is different than I expect, like how it handles last_cp or ver for that when it goes back to one;
  this is hard to test until auto-cp is there, since i keep forgetting to make them
- not sure if redo is restoring viewpoint properly

file ops interaction:
  - no interaction with file save (not sure if it needs one)
  - doesn't properly update assy._modified
  - file open/close interaction not reviewed

advanced:
- out of order redo/undo, and its UI
- prefs to save state on disk, save beyond session

'''
__author__ = 'bruce'

#bruce 060117 newer simpler code, far less modular, and currently a prototype stub kluge...
# will be sped up and cleaned up, and hopefully will be generalized along lines of older code (which is not all in cvs now)

from files_mmp import writemmp_mapping, reset_grouplist, _readmmp_state

import time
import platform
from debug import print_compact_traceback
import env #k not yet needed
from Utility import Group 

debug_undo2 = platform.atom_debug # this is probably ok to commit for now, but won't work for enabling the feature for testing

def mmp_state_from_assy(assy, initial = False): #bruce 060117 prototype-kluge
    """return a data-like python object encoding all the undoable state in assy
    (or in nE-1 while it's using assy)
    (it might contain refs to permanent objects like elements or atomtypes, and/or contain Numeric arrays)
    [modified from files_mmp.writemmpfile_assy]
    """
##    if not initial: # this flag is a kluge; should detect the situation inside assy itself, and this should be a method in assy
##        # otherwise it might be too early to do these (not carefully reviewed)
##        assy.o.saveLastView()
##        assy.update_parts() ### better if we could assume this is done already; also worry about all other updates, like bonds

    if initial:
        # assy lacks enough attrs for write mmp to work, eg .o, .temperature
        return ('mmp_state', "# stub for new assy -- too early") # kluge, stub, won't work for undo back to the start

    # this kluge is not multi-platform-safe, but will not run unless someone uses debug menu item to make undo checkpoint:
    fp = open("/tmp/fff", "w")########@@@@@@@@ KLUGE, fix; or at least make it use a filename in a new per-pid subdir in ~/Nanorex

    mapping = writemmp_mapping(assy) ###e should pass options
    mapping.set_fp(fp)

    try:
        mapping.write_header()
        assy.construct_viewdata().writemmp(mapping)
        assy.tree.writemmp(mapping)
        
        mapping.write("end1\n")
        mapping.past_sim_part_of_file = True

        addshelf = True
        if addshelf:
            assy.shelf.writemmp(mapping)
        
        mapping.write("end molecular machine part " + assy.name + "\n")
    except:
        mapping.close(error = True)
        raise
    else:
        mapping.close()

    fp = open("/tmp/fff", "r")
    data = fp.read()
    fp.close()

    mmpstate = ('mmp_state', data)
    
    return mmpstate #e soon will modify to not use disk, and return a different kind of py object

def _undo_readmmp_kluge(assy, mmpstate): # modified from _readmmp
    "[arg type matches whatever mmp_state_from_assy returns]"
##    if debug_undo2:
##        print (mmpstate)
    junk, data = mmpstate
    del mmpstate
    assert junk == 'mmp_state'
    # data is a string of mmp file bytes, or maybe a list of lines
    isInsert = True # prevents unwanted side effects on assy
    state = _readmmp_state( assy, isInsert)
    lines = data.split('\n')
    for card in lines:
        try:
            errmsg = state.readmmp_line( card) # None or an error message
        except:
            # note: the following two error messages are similar but not identical
            errmsg = "bug while reading this mmp line: %s" % (card,) #e include line number; note, two lines might be identical
            print_compact_traceback("bug while reading this mmp line:\n  %s\n" % (card,) )
        #e assert errmsg is None or a string
        if errmsg:
            ###e general history msg for stopping early on error
            ###e special return value then??
            break
    grouplist = state.extract_toplevel_items() # for a normal mmp file this has 3 Groups, whose roles are viewdata, tree, shelf

    # following could be simplified, but don't bother, entire scheme will be replaced instead
    
    viewdata = Group("Fake View Data", assy, None) # name is never used or stored
    shelf = Group("Clipboard", assy, None) # name might not matter since caller resets it
    
    for g in grouplist:
        if not g.is_group(): # might happen for files that ought to be 'one_part', too, I think, if clipboard item was not grouped
            state.guess_sim_input('missing_group_or_chunk') # normally same warning already went out for the missing chunk 
            tree = Group("tree", assy, None, grouplist)
            grouplist = [ viewdata, tree, shelf ]
            break
    if len(grouplist) == 0:
##        state.format_error("nothing in file")
##        return None
        # this means it represented an empty assy (at least in our initial kluge implem of 060117)
        tree = Group("tree", assy, None, []) #k guess; caller will turn it into PartGroup I think, but is name "tree" ok?? ###@@@
        grouplist = [ viewdata, tree, shelf ]        
    elif len(grouplist) == 1:
        state.guess_sim_input('one_part')
            # note: 'one_part' gives same warning as 'missing_group_or_chunk' as of 050406
        tree = Group("tree", assy, None, grouplist) #bruce 050406 removed [0] to fix bug in last night's new code
        grouplist = [ viewdata, tree, shelf ]
    elif len(grouplist) == 2:
        state.guess_sim_input('no_shelf')
        grouplist.append( shelf)
    elif len(grouplist) > 3:
        state.format_error("more than 3 toplevel groups -- treating them all as in the main part")
            #bruce 050405 change; old code discarded all the data
        tree = Group("tree", assy, None, grouplist)
        grouplist = [ viewdata, tree, shelf ]
    else:
        pass # nothing was wrong!
    assert len(grouplist) == 3
        
    state.destroy() # not before now, since it keeps track of which warnings we already emitted

    return grouplist # from _readmmp

# assy methods, here so reload works

def assy_become_state(self, state): #bruce 060117 kluge for non-modular undo; should be redesigned to be more sensible
    "replace our state with some new state (in an undo-private format) saved earlier by an undo checkpoint"
    # the actual format is a complete kluge, depends on readmpp code, should be changed, esp for atom posns

    
    # == now compare to files_mmp.readmmp
    ## grouplist = _readmmp(assy, filename)
    from undo_archive import _undo_readmmp_kluge
    try:
        grouplist = _undo_readmmp_kluge(self, state) # should have no effect on self (assy), though we have to pass it
##        if debug_undo2:
##            print "grouplist", grouplist
    except:
        print_compact_traceback("exception in _undo_readmmp_kluge")
        raise # caller would otherwise think we worked
        ## grouplist = None
    else:
        self.clear() # clear only if read works, to avoid huge tracebacks
        reset_grouplist(self, grouplist)
        self.changed() #k needed? #e not always correct! (if we undo or redo to where we saved the file)
        assert self.part # update_parts was done already
        self.o.set_part( self.part) # try to prevent exception in GLPane.py:1637
        self.w.mt.resetAssy_and_clear()  # ditto, mt line 108
        self.w.win_update() # precaution
    return

def assy_clear(self): #bruce 060117 draft
    "become empty of undoable state (as if just initialized)"
    self.tree.destroy() # not sure if these work very well yet; maybe tolerable until we modularize our state-holding objects
    self.shelf.destroy()
    self.root = None # memory leak?
    self.tree = self.shelf = None
    self._last_current_selgroup = None # guess, to avoid traceback
    #e viewdata?
    #e selection?
    #e parts?
    #e glpane state?
    #e effect on MT?
    #e selatom?
    #e mode?
    #e current_movie?
    #e filename?
    #e modified?
    self.changed()
    return

# ==

# we'll still try to fit into the varid/vers scheme for multiple out of order undo/redo,
# since we think this is highly desirable for A7 at least for per-part Undo.
# but varids are only needed for highlevel things with separate ops offered.
# so a diff is just a varid-ver list and a separate operation...
# which can ref shared checkpoints if useful. it can ref both cps and do the diff lazily if you want.
# it's an object, which can reveal these things...
# it has facets... all the same needs come up again...
# maybe it's easier to let the facets be flyweight and ref shared larger pieces and just remake themselves?

class Checkpoint:
    def __init__(self, ver = None, state = None, assy_debug_name = None):
        self.varid = 'varid_stub_' + (assy_debug_name or "") #e will come from assy itself
        if ver is None:
            ver = 'ver-' + `time.time()` #####@@@@@ wrong! unique int!
        self.ver = ver
        self.state = state # permit storing this later (public attribute for set) (also public for get, see SimpleDiff.apply_to)
        if debug_undo2:
            print self
        return
    def __repr__(self):
        return "<Checkpoint varid=%r, ver=%r, state id is %#x>" % (self.varid, self.ver, id(self.state))
    def varid_ver(self):
        """Assuming there is one varid for entire checkpoint, return its varid_ver pair.
        Hopefully this API and implem will need revision for A7 since assumption will no longer be true.
        """
        return self.varid, self.ver
    pass

class SimpleDiff:
    "diff defined as going from checkpoint 0 to checkpoint 1 (in that order, when applied)"
    default_opts = dict(op_name = "")
    def __init__(self, cp0, cp1, direction = 1, **options):
        "direction is a sign, 1 means forwards in time (redo diff), -1 means backwards (undo diff); options include opname"
        self.cps = cp0, cp1
        self.direction = direction
        self.options = options
        self.opts = dict(self.default_opts)
        self.opts.update(options) # use these for actual values to use (could be done lazily)
    def reverse_order(self):
        return self.__class__(self.cps[1], self.cps[0], - self.direction, **self.options)
    def menu_desc(self):
        main = {1: "Redo", -1: "Undo"}[self.direction]
        op_name = self.opts['op_name']
        if op_name:
            main = "%s %s" % (main, op_name)
        return main
    def varid_vers(self):
        "list of varid_ver pairs for indexing"
        return [self.cps[0].varid_ver()]
    def last_cp(self):
        "...Hopefully this API and implem will need revision for A7 ..."
        return self.cps[1]
    def apply_to(self, assy):
        "apply this diff-operation to the given model objects"
        assy.become_state(self.cps[1].state) ###IMPLEM become_state, or maybe even have this make a new assy?? try not to...
    pass

def make_checkpoint(assy, initial = False):
    data = mmp_state_from_assy(assy, initial = initial)
    return Checkpoint(None, data, assy_debug_name = assy._debug_name)
        # makes up ver -- iedally we'd do that here, make cp without data, let difftracking add to it...

class AssyUndoArchive: # modified from UndoArchive_older and AssyUndoArchive_older
    def __init__(self, assy):
        self.assy = assy
        self.subs = []
        self.stored_ops = {} # see older class's docstring for this ###doc; look up state varvers to get ops
        self.last_cp = self.initial_cp = make_checkpoint(self.assy, initial = True) # initial checkpoint
            #e note, self.last_cp will be augmented by a desc of varid_vers pairs about cur state; 
            # but for out of order redo, we get to old varid_vers pairs but new cp's; maybe there's a map from one to the other...
            ###k was this part of UndoManager in old code scheme? i think it was grabbed out of actual model objects in UndoManager.
    def subscribe_to_checkpoints(self, func):
        "Do func after every change to the set of undo ops or their validity (ie after a checkpoint or after doing an op)"
        #e not yet needed: feature to let this be removed, or do so when func returns true or raises an exception
        self.subs.append(func)
    def checkpoint(self):
        cp = make_checkpoint(self.assy)
        #e could compare this and last cp for being identical (here, or as we make the diff in next subr)
        redo_diff = SimpleDiff(self.last_cp, cp) #e will be done incrementally by tracking in A7-i-hope version
        undo_diff = redo_diff.reverse_order()
        self.store_op(redo_diff)
        self.store_op(undo_diff)
        self.last_cp = cp
        self.notify_observers()
    def notify_observers(self):
        for func in self.subs:
            try:
                func()
            except:
                print_compact_traceback()
            pass
        return
    def do_op(self, op):
        "do one of the diff-ops we're storing (apply it to state, correct stored varid_ver pairs)"
        op.apply_to(self.assy)
            # note: actually affects more than just assy, perhaps (ie glpane view state...)
            #e when diffs are tracked, worry about this one being tracked
            #e should track how this affects varid_vers pairs
        self.last_cp = op.last_cp()
        self.notify_observers() #k not sure whether this will be too soon or redundant... ###@@@
    def find_undoredos(self):
        #e also pass state_version? for now rely on self.last_cp or some new state-pointer...
        "Return a list of undo and/or redo operations that apply to the current state."
        state_version = dict([self.last_cp.varid_ver()]) ###@@@ extend to more pairs
        # that's a dict from varid to ver for current state; this code would like items list but future code will want the dict #e
        res = []
        for var, ver in state_version.items():
            lis = self.stored_ops.get( (var, ver), [] )
            if not lis and debug_undo2 and (self.last_cp is not self.initial_cp):
                print "why no stored ops for this? (claims to not be initial cp)",var, ver # had to get here somehow...
            res.extend( lis )
        # this includes anything that *might* apply... filter it... not needed for now with only one varid in the system. ###@@@
        return res
    def store_op(self, op):
        for varver in op.varid_vers():
            ops = self.stored_ops.setdefault(varver, [])
            ops.append(op)
        return
    pass


# end
