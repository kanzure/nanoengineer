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
- ultimately we'll need checkpointing at begin and end of every command and every period of recursive event processing,
  and a way to discard diffs with nothing in them (and merge their checkpoints) (so undo/redo won't be a noop).
  We could approximate that if we had a good-enough "anything changed flag" or counter (updated by all kinds of changes),
  but we can do it just as well in a diff-tracking system so we might as well wait for that to exist... unless we don't have that
  for a long period.
  In the short run we can't afford so many checkpoints (since they're slow), so we'll have them only at begin_cmd points,
  and make the "next begin_cmd" even though it's not filled in yet. make_checkpoint or its calling code will handle this.

before we implement auto-checkpointing, we must:
+ pref to enable it, off by default (maybe a persistent debug_pref) [done, but not persistent for now]
+ replace the /tmp/fff kluge, either with pure use of RAM [later] or a safe temporary file [did that for now]

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

import time, os
import platform
from debug import print_compact_traceback
import env #k not yet needed
from Utility import Group 

debug_undo2 = platform.atom_debug # this is probably ok to commit for now, but won't work for enabling the feature for testing

# Since it's easiest, we store all or part of a checkpoint in a real mmp file on disk;
# this might be useful for debugging so we'll keep it around during development,
# though in the released code, most of the info will be represented in binary and most or all of it will be kept only in RAM.

# Note: as of 060117, it won't make this subdir or file for anyone who doesn't make an undo checkpoint,
# either manually or via a debug_pref for autocheckpointing,
# since our "initial checkpoint" for every assy is made without using a file.

def compute_checkpoint_kluge_filename():
    from platform import find_or_make_Nanorex_subdir
    subdir = find_or_make_Nanorex_subdir('UndoKlugeCheckpoints')
    return os.path.join( subdir, "checkpoint-%d.mmp" % os.getpid())

compute_checkpoint_kluge_filename = None

def checkpoint_kluge_filename():
    global _checkpoint_kluge_filename
    if not _checkpoint_kluge_filename:
        _checkpoint_kluge_filename = compute_checkpoint_kluge_filename()
    return _checkpoint_kluge_filename


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

    # the following code is not reached (as of 060117)
    # unless the user explicitly asks for an undo checkpoint
    # (via menu command or preference setting).
    
    fp = open( checkpoint_kluge_filename(), "w")

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

    fp = open( checkpoint_kluge_filename(), "r")
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

_cp_counter = 0

class Checkpoint:
    """Represents a slot to be filled (when created or later, perhaps gradually, perhaps virtually)
    with a snapshot of the model's undoable state. API permits snapshot data (self.state) to be specified when created,
    or filled in later, or (if implem supports) defined by a diff from the state of another checkpoint.
       Self.state will not exist until the state-data is fully defined (unless a future revision supports its being
    some sort of lazily-valued expr which indicates a lazily filled diff and a prior checkpoint).
       Self.complete is a boolean which is True once the snapshot contents are fully defined. As of 060118 this is
    the same as hasattr(self, 'state'), but if self.state can be lazy then it might exist with self.complete still being false.
       The main varid_ver might exist right away, but the ones that depend on the difference with prior state won't exist
    until the set of differences is known.
       Note: it is good to avoid letting a checkpoint contain a reference to its assy or archive or actual model objects,
    since those would often be cyclic refs or refs to garbage, and prevent Python from freeing things when it should.
    """
    def __init__(self, assy_debug_name = None):
        # in the future there might be a larger set of varid_ver pairs based on the data changes, but for now there's
        # one main one used for the entire undoable state, with .ver also usable for ordering checkpoints; this will be retained;
        # cp.varid will be the same for any two checkpoints that need to be compared (AFAIK).
        self.varid = 'varid_stub_' + (assy_debug_name or "") #e will come from assy itself
        global _cp_counter
        _cp_counter += 1
        self.ver = 'ver-' + `_cp_counter` # this also helps sort Redos
        self.complete = False # public for get and set
        if debug_undo2:
            print "debug_undo2: made cp:", self
        return
    def store_complete_state(self, state):
        self.state = state # public for get and set and hasattr; won't exist at first
        self.complete = True
        return
    def __repr__(self):
        if self.complete:
            return "<Checkpoint varid=%r, ver=%r, state id is %#x>" % (self.varid, self.ver, id(self.state))
        else:
            #e no point yet in hasattr(self, 'state') distinction, since always false as of 060118
            assert not hasattr(self, 'state')
            return "<Checkpoint varid=%r, ver=%r, incomplete state>" % (self.varid, self.ver)
        pass
    def varid_ver(self):
        """Assuming there is one varid for entire checkpoint, return its varid_ver pair.
        Hopefully this API and implem will need revision for A7 since assumption will no longer be true.
        """
        return self.varid, self.ver
    pass

class SimpleDiff:
    """Represent a diff defined as going from checkpoint 0 to checkpoint 1
    (in that order, when applied);
    also considered to be an operation for applying that diff in that direction.
    Also knows whether that direction corresponds to Undo or Redo,
    and knows some metainfo such as op_name (of cmd that created it; not yet properly set ###e),
    and (in future) times diff was created and last applied, and more.
       Neither checkpoint needs to have its state filled in yet, except for our apply_to method.
    Depending on how and when this is used they might also need their varid_ver pairs for indexing.
    [Note: error of using cp.state too early, for some checkpoint cp, are detected by that attr not existing yet.]
    """
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
        main = self.optype() # "Undo" or "Redo"
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
        cp = self.cps[1]
        assert cp.complete
        assy.become_state(cp.state)
    def optype(self):
        return {1: "Redo", -1: "Undo"}[self.direction]
    pass

# ==

# These three functions go together as one layer of the API for using checkpoints.
# They might be redundant with what's below or above them (most likely above, i.e.
# they probably ought to be archive methods),
# but for now it's clearest to think about them in this separate layer.

def make_checkpoint(assy, cptype = None):
    """Make a new Checkpoint object, with no state.
    Sometime you might want to call fill_checkpoint on it,
    though in the future there will be more incremental options.
    """
    cp = Checkpoint(assy_debug_name = assy._debug_name)
        # makes up cp.ver -- would we ideally do that here, or not?
    cp.cptype = cptype #e put this inside constructor? (i think it's always None or 'initial', here)
    return cp

def current_state(assy, initial = False):
    """Return a data-like representation of complete current state of the given assy;
    initial flag means it might be too early (in assy.__init__) to measure this
    so just return an "empty state".
    """
    data = mmp_state_from_assy(assy, initial = initial)
    return data

def fill_checkpoint(cp, state): #e later replace calls to this with cp method calls
    assert cp is not None
    assert not cp.complete
    cp.store_complete_state(state)
    return

# ==

class AssyUndoArchive: # modified from UndoArchive_older and AssyUndoArchive_older # TODO: maybe assy.changed will tell us...
    """#docstring is in older code... maintains a series (or graph) of checkpoints and diffs connecting them....
     At most times, we have one complete ('filled') checkpoint, and a subsequent incomplete one (subject to being modified
    by whatever changes other code might next make to the model objects).
     Even right after an undo or redo, we'll have a checkpoint
    that we just forced the model to agree with, and another one to hold whatever changes the user might make next
    (if they do anything other than another immediate undo or redo). (Hopefully we'll know whether that other one has
    actually changed or not, but in initial version of this code we might have to guess; maybe assy.changed will tell us.)
     If user does an undo, and then wants to change the view before deciding whether to redo, we'd better not make that
    destroy their ability to redo! So until we support out-of-order undo/redo and a separate undo stack for view changes
    (as it should appear in the UI for this), we won't let view changes count as a "new do" which would eliminate the redo stack.
    """
    next_cp = None
    current_diff = None
    def __init__(self, assy):
        self.assy = assy # represents all undoable state we cover (this will need review once we support multiple open files)
        self.subs = [] # list of functions to run after we might have changed the set of immediately applicable undo/redo ops
        self.stored_ops = {} # map from (varid, ver) pairs to lists of diff-ops that implement undo or redo from them;
            # when we support out of order undo in future, this will list each diff in multiple places
            # so all applicable diffs will be found when you look for varid_ver pairs representing current state.
            # (Not sure if that system will be good enough for permitting enough out-of-order list-modification ops.)
        cp = make_checkpoint(self.assy, 'initial') # initial checkpoint
        #e the next three lines are similar to some in self.checkpoint --
        # should we make self.set_last_cp() to do part of them? compare to do_op's effect on that, when we code that. [060118]
        fill_checkpoint(cp, current_state(assy, initial = True)) ### it's a kluge to pass initial; revise to detect this in assy itself
        self.last_cp = self.initial_cp = cp
        self.last_cp_arrival_reason = 'initial' # why we got to the situation of model state agreeing with this, when last we did
            #e note, self.last_cp will be augmented by a desc of varid_vers pairs about cur state; 
            # but for out of order redo, we get to old varid_vers pairs but new cp's; maybe there's a map from one to the other...
            ###k was this part of UndoManager in old code scheme? i think it was grabbed out of actual model objects in UndoManager.
        self._setup_next_cp() # don't know cptype yet (I hope it's 'begin_cmd'; should we say that to the call? #k)
        ## self.notify_observers() # current API doesn't permit this to do anything during __init__, since subs is untouched then
        return
    def _setup_next_cp(self):
        """[private method, mainly for begin_cmd_checkpoint:]
        self.last_cp is set; make (incomplete) self.next_cp, and self.current_diff to go between them.
        Index it... actually we probably can't fully index it yet if that depends on its state-subset vers.... #####@@@@@
        """
        assert self.next_cp is None
        self.next_cp = make_checkpoint(self.assy) # note: we never know cptype yet, tho we might know what we hope it is...
        redo_diff = SimpleDiff(self.last_cp, self.next_cp) # this is a slot for the actual diff, whose content is not yet known
        # assume it's too early for indexing this, or needing to -- let that be done by some sort of end_cmd #######@@@@@@@
##        undo_diff = redo_diff.reverse_order()
##        self.store_op(redo_diff)
##        self.store_op(undo_diff)
        self.current_diff = redo_diff # this attr is where change-trackers would find it to tell it what changed (once we have any)
        ## self.notify_observers() - done by caller if desired (since different callers might do it differently, later, not at all)
        return
    def _setup_Null_next_cp(self):
        assert self.next_cp is None
        self.next_cp = None
        self.current_diff = None
        return
    def changed(self): #######@@@@@@@ call from begin_cmd_checkpoint? no, from the next cmd's if a change happened!
        """[semi-private -- call this if you know some change happened but self.next_cp might not be set yet;
        ensures that is set and self.current_diff are set]
        """
        if self.next_cp is None:
            self._setup_next_cp()
        assert self.next_cp is not None
        assert self.current_diff is not None # IT MIGHT BE BETTER to let this always exist, and be evidently empty or not,
            # so trackers needn't check whether it exists.
            # for now [060118 452p] we'll assume that if begin_cmd happens, then it will in fact change something,
            # so the next Undo should always go back to the point of that begin_cmd (so it knows what diff or cp to put in menu item).
            # A bg problem or danger with current willynilly cp-mods is that menu item diffops might not get updated
            # when the current or next cp does... need to think about that.
            # WHERE I AM 060118 456pm -- working out all this kind of stuff; in middle of 3-4 revisions to it.
            # In danger of forgetting somethig...
            # including, need to make *only the simplest test* work, ad commit, so cadders can start to try it out and
            # prioritize complaints about how it handles view changes (incl what view to use to show an undo), current part changes, etc.
        return
    def subscribe_to_checkpoints(self, func):
        "Do func after every change to the set of undo ops or their validity (ie after a checkpoint or after doing an undo/redo op)"
        #e not yet needed: feature to let this be removed, or do so when func returns true or raises an exception
        self.subs.append(func)
    def checkpoint(self, cptype = None ):#####@@@@@ revise calls [this is where i am 060118 343pm]
        """Cause self.next_cp to become complete, i.e. to have fully defined state, equal to current model state;
        and prepare for a subsequent checkpoint call. In other words, make sure the current model state gets stored in here
        and could later be Undone to or Redone to.
        """
        assert cptype
        self.last_cp = self.next_cp
        self.next_cp = None # in case of exceptions in rest of this method
        cp = self.last_cp
        cp.cptype = cptype #k is this the only place that knows cptype, except for 'initial'?
        self.last_cp_arrival_reason = cptype # affects semantics of Undo/Redo user-level ops
            # (this is not redundant, since it might differ if we later revisit same cp as self.last_cp)
        #e store other metainfo, like time of completion, cmdname of caller, history serno, etc (here or in fill_checkpoint)
        fill_checkpoint(cp, current_state(self.assy))
            #e This will be revised once we incrementally track some changes - it won't redundantly grab unchanged state,
            # though it's likely to finalize and compress changes in some manner, or grab changed parts of the state.
            # It will also be revised if we compute diffs to save space, even for changes not tracked incrementally.
            #e ... could compare this and last cp for being identical
        self._setup_next_cp()
        self.notify_observers() # note: current API doesn't permit this to do anything during __init__, since subs is untouched then
        return
    def notify_observers(self):
        for func in self.subs:
            try:
                func()
            except:
                print_compact_traceback()
            pass
        return
    def do_op(self, op): ###@@@ where i am 345pm - figure out what this does if op.prior is not current, etc;
                # how it relates to whether assy changed since last_cp set; etc.
        """assuming caller has decided it's safe, good, etc, in the case of out-of-order undo,
        Do one of the diff-ops we're storing
        (ie apply it to model to change its state in same direction as in this diff),
        and record this as a change to current varid_ver pairs
        (not yet sure if those are stored here or in model or both, or of details for overall vs state-subset varids).
           If this is exactly what moves model state between preexisting checkpoints (i.e. not out-of-order),
        change overall varid_ver (i.e. our analog of an "undo stack pointer") to reflect that;
        otherwise [nim as of 060118] make a new checkpoint, ver, and diff to stand for the new state, though some state-subset
        varid_vers (from inside the diff) will usually be reused. (Always, in all cases I know how to code yet; maybe not for list ops.)        
        """
        # in present implem [060118], we assume without checking that this op is not being applied out-of-order,
        # and therefore that it always changes the model state between the same checkpoints that the diff was made between
        # (or that it can ignore and/or discard any way in which the current state disagrees with the diff's start-checkpoint-state).
        op.apply_to(self.assy)
            # note: actually affects more than just assy, perhaps (ie glpane view state...)
            #e when diffs are tracked, worry about this one being tracked
            #e should track how this affects varid_vers pairs
        self.last_cp = op.last_cp()
        self.last_cp_arrival_reason = op.optype()
        self._setup_Null_next_cp()
            # let it be set up for real if/when a change actually happens (gets tracked, nim),
            # or is planned to immediately happen (begin_cmd), or is recognized as having happened (nim).
        ## self._setup_next_cp()
        self.notify_observers() #k not sure whether this will be too soon or redundant... ###@@@
        return
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
