# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
undo_archive.py

Collect and organize a set of checkpoints of model state and diffs between them,
providing undo/redo ops which apply those diffs to the model state.

$Id$

[060223: out of date status info from this docstring was mostly moved to undo_archive-doc.text,
 not in cvs; can clean up and commit later #e]

'''
__author__ = 'bruce'

import time, os
import platform
from debug import print_compact_traceback, print_compact_stack
from debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True
import env
import state_utils
from state_utils import objkey_allocator, obj_classifier, diff_and_copy_state, transclose
from prefs_constants import historyMsgSerialNumber_prefs_key, undoRestoreView_prefs_key

destroy_bypassed_redos = True # whether to destroy the Redo stack to save RAM
    # [not implemented yet -- flag has no effect, but shows where to do it -- 060301]
    # aka destroy alternate futures, destroy inaccessible redos...

debug_undo2 = False
    ## = platform.atom_debug # this is probably ok to commit for now, but won't work for enabling the feature for testing

def mmp_state_from_assy(archive, assy, initial = False, use_060213_format = False): #bruce 060117 prototype-kluge
    """return a data-like python object encoding all the undoable state in assy
    (or in nE-1 while it's using assy)
    (it might contain refs to permanent objects like elements or atomtypes, and/or contain Numeric arrays)
    """
    if use_060213_format:
        return ('scan_whole', mmp_state_by_scan(archive, assy) ) # not yet differential, just a different state-scanner, more general

    assert 0 # 060301, zapped even the commented-out alternative, 060314

def mmp_state_by_scan(archive, assy): #e misnamed, since other things refer to this as the non-mmp option
    """[#doc better:]
    Return a big object listing all the undoable data reachable from assy,
    in some data-like form (but including live objrefs), mostly equivalent to a list of objkey/attr/value triples,
    suitable for mashing it back into assy, and whatever undoable objs it contains, at a later time.
    """
    scanner = archive.obj_classifier
    start_objs = [assy] #k need any others?
    viewdict = {}
    # kluge: defer collection of view-related objects and discard them, but don't bother deferring selection-related objects,
    # since for now there aren't any (and looking for them would slow us down until atoms are processed separately in a faster way).
    state_holding_objs_dict = scanner.collect_s_children( start_objs, deferred_category_collectors = {'view':viewdict} )
    
    ## print "didn't bother scanning %d view-related objects:" % len(viewdict), viewdict.values() # works [060227]
    
    #e figure out which ones are new or gone? not needed until we're differential, unless this is a good place
    # to be sure the gone ones are properly killed (and don't use up much RAM). if that change anything
    # we might have to redo the scan until nothing is killed, since subobjects might die due to this.

##    print "mmp_state_by_scan",assy
    state = scanner.collect_state( state_holding_objs_dict, archive.objkey_allocator )
    return state

# ==

# assy methods, here so reload works

def assy_become_state(self, state, archive): #bruce 060117 kluge for non-modular undo; should be redesigned to be more sensible
    """[self is an assy] replace our state with some new state (in an undo-private format) saved earlier by an undo checkpoint,
    using archive to interpret it if necessary
    """
    if type(state) == type(()):
        format, data = state
        # state can be None if exception (bug) was caught while checkpoint was made,
        # but it's not yet worth protecting from that here [bruce 060208]
    else:
        format, data = 'scan_whole', state # kluge 060301
    del state
    if format == 'mmp_state':
        assert 0 #060301 [removed commented-out support code, 060314]
    elif format == 'scan_whole':
        assy_become_scanned_state(self, data, archive) # that either does self.update_parts() or doesn't need it done (or both)
        # fall thru
    else:
        assert 0, "unknown format %r" % (format,)
    self.changed() #k needed? #e not always correct! (if we undo or redo to where we saved the file)
        #####@@@@@ review after scan_whole 060213
    assert self.part # update_parts was done already
    self.o.set_part( self.part) # try to prevent exception in GLPane.py:1637
    self.w.mt.resetAssy_and_clear()  # ditto, mt line 108
    self.w.win_update() # precaution
    return

def assy_clear(self): #bruce 060117 draft
    # [note: might be called as assy.clear() or self.clear() in this file.]
    "[self is an assy] become empty of undoable state (as if just initialized)"
    self.tree.destroy() # not sure if these work very well yet; maybe tolerable until we modularize our state-holding objects
        #bruce 060322 comments [MOSTLY WRONG but useful anyway, as explained in next lines]:
        # - as I wrote the following, I was thinking that this was an old method of assy, so they might be partly misguided.
        #   I'm not even sure it's ever called, and if it is, it might not be tantamount to assy.destroy as I think I was assuming.
        # - it's unclear whether general semantics of .destroy would condone this destroying their children (as it now does);
        #   guess: desirable to destroy solely-owned children or (more generally) children all of whose parents are destroyed,
        #   but not others (e.g. not Node.part unless all its Nodes are -- note, btw, Part.destroy is not a true destroy method in
        #   semantics).
        # - current implem is not enough (re refs from undo archive). Furthermore, letting the archive handle it might be best,
        #   but OTOH we don't want to depend on their being one, so some more general conventions for destroy (of objs with children)
        #   might actually be best.
        # - ###@@@ why doesn't this destroy self.um if it exists??? guess: oversight; might not matter a lot
        #   since i think the next one destroys it (need to verify). [MISGUIDED, see above]
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

# doesn't work: from asyncore import safe_repr

def safe_repr(obj, maxlen = 1000):
    try:
        rr = "%r" % (obj,)
    except:
        rr = "<repr failed for id(obj) = %#x, improve safe_repr to print its class at least>" % id(obj)
    if len(rr) > maxlen:
        return rr[(maxlen - 4):] + "...>" # this should also be in a try/except, even len should be
    else:
        return rr
    pass

def assy_become_scanned_state(self, data, archive):
    "[self is an assy; data is returned by mmp_state_by_scan, and is therefore presumably a StateSnapshot or StatePlace object]"
    ####@@@@ this should really be a method of AssyUndoArchive (not just assy itself) [bruce 060313 realization]
    assy = self
    assert assy is archive.assy
##    print "assy_become_scanned_state", data
    modified = {} # key->obj for objects we modified
    # use undotted localvars, for faster access in inner loop:
    modified_get = modified.get
    obj4key = archive.obj4key
    reset_obj_attrs_to_defaults = archive.obj_classifier.reset_obj_attrs_to_defaults
    from state_utils import copy_val as copy
        # ideally, copy_val might depend on attr (and for some attrs is not needed at all),
        # i.e. we should grab one just for each attr farther inside this loop, and have a loop variant without it
        # (and with the various kinds of setattr/inval replacements too --
        #  maybe even let each attr have its own loop if it wants, with atoms & bonds an extreme case)
    try:
        attrdicts = data.attrdicts # works for a StateSnapshot ####@@@@ this is dangerous, what if someone adds that attr to StatePlace?
    except:
        attrdicts = data.get_attrdicts_for_immediate_use_only() # works for a StatePlace
    for attr, dict1 in attrdicts.items(): ##e might need to be in a specific order
        ## might_have_undo_setattr = (attr == 'molecule')
        # _undo_setattr_molecule turned out not to be useful so far [060314], so for speed,
        # limit this testing kluge (which will never find an actual _undo_setattr_xxx)
        # to a rarer attribute, but one that does exist sometimes:
        might_have_undo_setattr = (attr == 'temperature') ###@@@ KLUGE for testing, and good enough for initial use
            # (so might be released in A7, due to time pressures, embarrassingly enough) [bruce 060313]
        for key, val in dict1.iteritems(): # maps objkey to attrval
            obj = modified_get(key)
            if obj is None:
                # first time we're touching this object
                obj = obj4key[key]
                modified[key] = obj
                ## reset_obj_attrs_to_defaults(obj) -- no, be a bit more subtle:
                # If any attr of this obj might_have_undo_setattr, we want it to see the old value,
                # so we don't want to reset *that* attr to its default value.
                # One way: exception for just those attrs.
                # Another way: exception for all attrs we plan to set specifically (only needed when "those attrs" are among them).
                # For initial use of might_have_undo_setattr, I can be simple, then figure out the proper way later.
                ## if attrdicts['molecule'].has_key(key):
                ##     # i.e. if we plan to set this obj's .molecule
                ##     ....
                # I can be even simpler, since it happens that .molecule has no default value in Atom
                # so reset_obj_attrs_to_defaults won't touch it! This is a ####@@@@ KLUGE which needs to be thought through
                # and fixed later, especially since I might decide to add a class default molecule = None at any time.
                # (Probably I should assert that doesn't happen. Ok, I'll do it in state_utils.)
                reset_obj_attrs_to_defaults(obj)
                #######e set all attrs in obj (which we store, or are cached) to their default values (might mean delattr?)
                # w/o this we have bugs...
                pass
            val = copy(val) #e possible future optim: let some attrs declare that this copy is not needed
            if might_have_undo_setattr: # optim: this flag depends on attr name
                setattr_name = '_undo_setattr_' + attr # only support attr-specific setattrs for now, for speed and subclass simplicity
                try:
                    method = getattr(obj, setattr_name) #e possible future optim: store unbound method for this class and attr
                except AttributeError:
                    pass # fall thru, use normal setattr
                else:
                    method(val, archive) # note: val might be _Bugval
                    #e someday, catch exceptions, emit redmsg but continue with restoring other state, or at least other attrs
                    continue
            # else, or if we fell through:
            setattr(obj, attr, val) ##k might need revision in case:
                # dflt val should be converted to missing val, either as optim or as requirement for some attrs (atomtype?) #####@@@@@
                # dflt vals were not stored, to save space, so missing keys should be detected and something done about them ...
                # this is done for objects we modify, but what about reachable objs with all default values?
                # either look for those on every value we copy and store, or make sure every obj has one attr with no default value
                # or whose actual value is never its default value. This seems true of all our current objs, so I'll ignore this issue for now!
                # ###k (also this remains unreviewed for issues of which objs "exist" and which don't... maybe it only matters as space optim...)
            ##e someday: check if val is _Bugval, maybe print error message or delete it or both
            # (can share code with deleting it if it's attr-specific dflt, once we clean up decls so different dflts mean different attrdicts)
            # [bruce 060311 comment]
            continue
        continue
#bruce 060314 this turned out not to be useful; leave it as an example
# until analoguous stuff gets created (since the principle of organization
# is correct, except for being nonmodular)
##    if 1:
##        ####@@@@ KLUGE: somehow we happen to know that we need to process mols_with_invalid_atomsets here,
##        # before running any obj._undo_update functions (at least for certain classes).
##        # We can know this since we're really (supposed to be) a method on AssyUndoArchive (so we know all about
##        # the kinds of data in assys). [bruce 060313]
##        for chunk in archive.mols_with_invalid_atomsets.values():
##            # chunk had one or more atoms leave it or join it, during the setattrs above
##            # (actually, during some _undo_setattr_molecule on those atoms; they kept its .atoms up to date,
##            #  but saved invals for here, for efficiency)
##            chunk.invalidate_atom_lists()
##                # this effectively inlines that part of chunk.addatom and delatom not done by atom._undo_setattr_molecule
##                # (we could just add chunk into modified (localvar), but this is more efficient (maybe))
    # that has replaced .molecule for lots of atoms; need to fix the .atoms dicts of those mols [060314]
    if 1: # simple way to start with ####@@@@ should split into separate func for profiling (need funcs for above and below things too)
        mols = {}
        moldict = attrdicts.get('molecule',{}) # {} can happen, when no Chunks were in the state!
        for atom_objkey, mol in moldict.iteritems():
            mols[id(mol)] = mol
        from chunk import _nullMol
        for badmol in (None, _nullMol):
            if mols.has_key(id(badmol)):
                # should only happen if undoable state contains killed or still-being-born atoms; I don't know if it can
                # (as of 060317 tentative fix to bug 1633 comment #1, it can -- _hotspot is S_CHILD but can be killed)
                if env.debug() and badmol is None:
                    print "debug: why does some atom in undoable state have .molecule = %r?" % (badmol,)
                del mols[id(badmol)]
                # but we also worry below about the atoms that had it (might not be needed for _nullMol; very needed for None)
        for mol in mols.itervalues():
            mol.atoms = {}
        for atom_objkey, mol in moldict.iteritems():
            if mol not in (None, _nullMol):
                atom = modified_get(atom_objkey)
                mol.atoms[ atom.key ] = atom # inlines some of Chunk.addatom; note: atom.key != atom_objkey
        for mol in mols.itervalues():
            mol.invalidate_atom_lists() # inlines some more of Chunk.addatom
        pass
    for key, obj in modified.iteritems():
        ###e zap S_CACHE attrs? or depend on update funcs to zap/inval/update them? for now, the latter. Review this later. ###@@@
        try:
            method = obj._undo_update
            ##e btw, for chunk, it'll be efficient to know which attrs need which updating... which means, track attrs used, now!
            ##e in fact, it means, do attrs in layers and do the updates of objs for each layer. if inval-style, that's fine.
            # objs can also reg themselves to be updated again in later layers. [need to let them do that]
            # not yet sure how to declare attrlayers... maybe test-driven devel will show me a simple way.
        except AttributeError:
            pass
        else:
            try:
                method()
            except:
                print_compact_traceback( "exception in _undo_update for %s; skipping it: " % safe_repr(obj))
            pass
        continue
    # now do the registered undo updaters
    if 1:
        # for now, kluge it because we know there's exactly this one:
        from chem import _undo_update_Atom_jigs
        updaters_in_order = [_undo_update_Atom_jigs]
    for func in updaters_in_order:
        try:
            func(archive, assy)
        except:
            print_compact_traceback( "exception in some registered updater %s; skipping it: " % safe_repr(func))
        continue
    #e also do some sort of general update of assy itself? or just let those be registered? for now, do this one:
    # now i think this might not be safe, and also should not be needed:
    ## assy.update_parts()
    # but I'll do it at the very end (below) just to be safe in a different way.
    #e now inval things in every Part, especially selatoms, selmols, molecules, maybe everything it recomputes
    for node in assy.topnodes_with_own_parts():
        node.part._undo_update_always() # kluge, since we're supposed to call this on every object that defines it
    assy.update_parts()
    if 1: #060302 4:45pm fix some unreported bugs about undo when hover highlighting is active -> inappropriate highlighting
        win = env.mainwindow()
        glpane = win.glpane
        glpane.selatom = glpane.selobj = None # this works; but is there a better way (like some method in GLPane)?
            # if there is, not sure it's fully safe!
            #e Also, ideally glpane should do this itself in _undo_update_always, which we should call.
    return # from assy_become_scanned_state

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
    """Represents a slot to be filled (usually long after object is first created)
    with a snapshot of the model's undoable state. API permits snapshot data (self.state) to be
    filled in later, or (if implem supports) defined by a diff from the state of another checkpoint.
       Some things done in the calling code (esp. fill_checkpoint) will probably be moved into methods of this class eventually.
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
        self.varid = make_assy_varid(assy_debug_name)
        global _cp_counter
        _cp_counter += 1
        self.cp_counter = _cp_counter ###k not yet used; might help sort Redos, but more likely we'll use some metainfo
        ## self.ver = 'ver-' + `_cp_counter` # this also helps sort Redos
        self.ver = None # not yet known (??)
        self.complete = False # public for get and set
        if debug_undo2:
            print "debug_undo2: made cp:", self
        return
    def store_complete_state(self, state):
        self.state = state # public for get and set and hasattr; won't exist at first
        self.complete = True
        return
    def __repr__(self):
        self.update_ver_kluge()
        if self.complete:
            return "<Checkpoint %r varid=%r, ver=%r, state id is %#x>" % (self.cp_counter, self.varid, self.ver, id(self.state))
        else:
            #e no point yet in hasattr(self, 'state') distinction, since always false as of 060118
            assert not hasattr(self, 'state')
            return "<Checkpoint %r varid=%r, ver=%r, incomplete state>" % (self.cp_counter, self.varid, self.ver)
        pass
    def varid_ver(self): ###@@@ this and the attrs it returns will be WRONG when there's >1 varid_ver pair
        """Assuming there is one varid for entire checkpoint, return its varid_ver pair.
        Hopefully this API and implem will need revision for A7 since assumption will no longer be true.
        """
        self.update_ver_kluge()
        if self.ver is None:
            if platform.atom_debug:
                print "atom_debug: warning, bug?? self.ver is None in varid_ver() for",self ###@@@
        return self.varid, self.ver
    def update_ver_kluge(self):
        try:
            mi = self.metainfo # stored by outside code (destined to become a method) when we're finalized
        except:
            pass
        else:
            self.ver = mi.assy_change_counters
        return
    def next_history_serno(self):#060301
        try:
            mi = self.metainfo # stored by outside code (destined to become a method) when we're finalized
        except:
            return -1
        else:
            return mi.next_history_serno
        pass
        
    pass # end of class Checkpoint

class SimpleDiff:
    """Represent a diff defined as going from checkpoint 0 to checkpoint 1
    (in that order, when applied);
    also considered to be an operation for applying that diff in that direction.
    Also knows whether that direction corresponds to Undo or Redo,
    and might know some command_info about the command that adds changes to this diff
    (we assume only one command does that, i.e. this is a low-level unmerged diff and commands are fully tracked/checkpointed),
    and (maybe, in future) times diff was created and last applied, and more.
       Neither checkpoint needs to have its state filled in yet, except for our apply_to method.
    Depending on how and when this is used they might also need their varid_ver pairs for indexing.
    [Note: error of using cp.state too early, for some checkpoint cp, are detected by that attr not existing yet.]
    """
    default_opts = dict()
    default_command_info = dict(cmdname = "operation", n_merged_changes = 0)
        # client code will directly access/modify self.command_info['n_merged_changes'] [060312], maybe other items
    suppress_storing_undo_redo_ops = False
    assert_no_changes = False
    destroyed = False
    def __init__(self, cp0, cp1, direction = 1, **options):
        """direction +1 means forwards in time (apply diff for redo), -1 means backwards (apply diff for undo),
        though either way we have to keep enough info for both redo and undo;
        as of 060126 there are no public options, but one private one for use by self.reverse_order().
        """
        self.cps = cp0, cp1
        self.direction = direction
        self.options = options # self.options is for use when making variants of self, like reverse_order
        self.opts = dict(self.default_opts)
        self.opts.update(options) # self.opts is for extracting actual option values to use (could be done lazily) [not yet used]
        self.key = id(self) #e might be better to not be recycled, but this should be ok for now
        # self.command_info: make (or privately be passed) a public mutable dict of command metainfo,
        # with keys such as cmd_name (#e and history sernos? no, those should be in checkpoint metainfo),
        # shared between self and self.reverse_order() [060126]
        self.command_info = self.options.get('_command_info_dict', dict(self.default_command_info) )
        self.options['_command_info_dict'] = self.command_info # be sure to pass the same shared dict to self.reverse_order()
        return
    def finalize(self, assy):
        ####@@@@ 060123 notyetcalled; soon, *this* is what should call fill_checkpoint on self.cps[1]!
        # let's finish this, 060210, so it can be tested, then done differently in BetterDiff
        """Caller, which has been letting model changes occur which are meant to be recorded in this diff,
        has decided it's time to finalize this diff by associating current model state with self.cps[1]
        and recording further changes in a new diff, which we(?) will create and return (or maybe caller will do that
        after we're done, not sure; hopefully caller will, and it'll also cause changetracking to go there --
        or maybe it needs to have already done that??).
           But first we'll store whatever we need to about the current model state, in self and/or self.cps.
        So, analyze the low-level change records to make compact diffs or checkpoint saved state,
        and record whatever else needs to be recorded... also make up new vers for whatever varids we think changed
        (the choice of coarseness of which is a UI issue) and record those in this diff and also in whatever model-related place
        records the "current varid_vers" for purposes of making undo/redo available ops for menus.
        """
        assert self.direction == 1
        #e figure out what changed in model, using scan of it, tracking data already in us, etc
        #####@@@@@ call fill_checkpoint
        #e make up vers for varids changed
        # *this* is what should call fill_checkpoint on self.cps[1]!
    def RAM_guess_when_finalized(self): #060323
        """Return a rough guess about the RAM usage to be attributed to keeping this Undoable op on the Undo stack.
        This must be called only when this diff has been finalized and is still undoable.
        Furthermore, as a temporarily kluge, it might be necessary to call it only once and/or in the proper Undo stack order.
        """
        # Current implem is basically one big kluge, starting with non-modularity of finding the DiffObj to ask.
        # When the Undo stack becomes a graph (or maybe even per-Part stacks), we'll have to replace this completely.
        assert self.direction == -1 # we should be an Undo diff
        s1 = self.cps[1].state
        s0 = self.cps[0].state
        return s0._relative_RAM(s1)
    def reverse_order(self):#####@@@@@ what if merged??
        return self.__class__(self.cps[1], self.cps[0], - self.direction, **self.options)
    def menu_desc(self):#####@@@@@ need to merge self with more diffs, to do this?? -- yes, redo it inside the MergingDiff ##e
        main = self.optype() # "Undo" or "Redo"
        include_history_sernos = not not env.prefs[historyMsgSerialNumber_prefs_key] #060309; is this being checked at the right time??
        if include_history_sernos:
            hist = self.history_serno_desc()
        else:
            hist = ""
        if self.command_info['n_merged_changes']:
            # in this case, put "changes" before hist instead of cmdname after it
            # (maybe later it'll be e.g. "selection changes")
            ##e should we also always put hist in parens?...
            # now, hist also sees this flag and has special form BUT ONLY WHILE BEING COLLECTED... well, it could use parens always...
            ##e in case of only one cmd so far, should we not do this different thing at all?
            # (not sure, it might help you realize autocp is disabled)
            changes_desc = self.changes_desc()
            if changes_desc:
                main += " %s" % (changes_desc,)
        if hist:
            # this assumes op_name is present; if not, might be better to remove '.' and maybe use parens around numbers...
            # but i think it's always present (not sure) [060301]
            main += " %s" % (hist,)
        if not self.command_info['n_merged_changes']:
            op_name = self.cmdname()
            if op_name:
                main += " %s" % (op_name,)
        return main
    def history_serno_desc(self): #060301; split out 060312
        "describe history serno range, if we have one; always return a string, maybe null string; needs to work when last serno unknown"
        if self.direction == 1:
            start_cp, end_cp = self.cps
        else:
            end_cp, start_cp = self.cps
        s1 = start_cp.next_history_serno()
        s2 = end_cp.next_history_serno()
        if s2 == -1: #060312 guess for use when current_diff.command_info['n_merged_changes'], and for direction == -1
            if not self.command_info['n_merged_changes'] and env.debug():
                print "debug: that's weird, command_info['n_merged_changes'] ought to be set in this case"
            return "(%d.-now)" % (s1,)
        
        n = s2 - s1
        if n < 0:
            print "bug in history serno order",s1,s2,self.direction,self
            # this 's1,s2 = s2,s1', the only time it happened, just made it more confusing to track down the bug, so zap it [060312]
            pass
##            n = -n
##            s1,s2 = s2,s1
        range0 = s1
        range1 = s2 - 1
        if n == 0:
            ## hist = ""
            #060304 we need to know which history messages it came *between*. Not sure what syntax should be...
            # maybe 18 1/2 for some single char that looks like 1/2?
            ## hist = "%d+" % range1 # Undo 18+ bla... dubious... didn't look understandable.
            hist = "(after %d.)" % range1 # Undo (after 18.) bla
            if debug_pref("test unicode one-half in Undo menutext", Choice_boolean_False): #060312
                hist = u"%d\xbd" % range1 # use unicode "1/2" character instead ( without u"", \xbd error, \x00bd wrong )
        elif n == 1:
            assert range0 == range1
            hist = "%d." % range1
        else:
            hist = "%d-%d." % (range0, range1)
        if self.command_info['n_merged_changes'] and hist and hist[0] != '(' and hist[-1] != ')':
            return "(%s)" % (hist,)
        return hist
    def cmdname(self):
        return self.command_info['cmdname']
    def changes_desc(self):#060312  
        return "changes" #e (maybe later it'll be e.g. "selection changes")
    def varid_vers(self):#####@@@@@ need to merge self with more diffs, to do this??
        "list of varid_ver pairs for indexing"
        return [self.cps[0].varid_ver()] 
    def apply_to(self, archive):###@@@ do we need to merge self with more diffs, too? [see class MergingDiff]
        "apply this diff-operation to the given model objects"
        cp = self.cps[1]
        assert cp.complete
        assy = archive.assy
        assy.become_state(cp.state, archive) # note: in present implem this might effectively redundantly do some of restore_view() [060123]
        cp.metainfo.restore_view(assy)
            # note: this means Undo restores view from beginning of undone command,
            # and Redo restores view from end of redone command.
            #e (Also worry about this when undoing or redoing a chain of commands.)
            # POSSIBLE KLUGE: with current implem, applying a chain of several diffs can be done by applying the last one.
            # The current code might perhaps do this when the skipped diffs are empty or have been merged -- don't know.
            # This will need fixing once we're merging any nonempty diffs. ####@@@@ [060123]
        cp.metainfo.restore_assy_change_counters(assy) # change current-state varid_vers records
        archive.set_last_cp_after_undo(cp) #060301
        return
    def optype(self):
        return {1: "Redo", -1: "Undo"}[self.direction]
    def __repr__(self):
        if self.destroyed:
            return "<destroyed SimpleDiff at %#x>" % id(self) #untested [060301]
        return "<%s key %r type %r from %r to %r>" % (self.__class__.__name__, self.key, self.optype(), self.cps[0], self.cps[1])
    def destroy(self):
        self.destroyed = True
        self.command_info = self.opts = self.options = self.cps = None
        # no cycles, i think, but do the above just in case
        ###e now, don't we need to remove ourself from archive.stored_ops?? ###@@@
    pass # end of class SimpleDiff

# ==

# commenting out SharedDiffopData and BetterDiff 060301 1210pm
# since it looks likely SimpleDiff will use differentially-defined states without even knowing it,
# just by having states in the checkpoints which know it themselves.

##class SharedDiffopData: ####@@@@ stub, apparently, as of 060216;
##    ###see also the become_state functions, which have similar code to apply_to;
##    ##060222 new code in state_utils superceding some of this...
##    """Hold replacement values for various attrs of various objects (objects are known to us only by their keys),
##    and be able to swap them with the attrvals in the objects, in alternate "directions"
##    """
##    def __init__(self):
##        assert 0 # not used as of before 060227, but slated to be used soon
##        self.attrdiffs = {} # maps attrnames to dicts from objkey to replacement-val, for use in self.direction
##        self.rev_attrdiffs = {} # ditto, for use in opposite direction, if we have them; typically built up while attrdiffs is applied
##        self.direction = -1 # the direction we can next be applied in (or 0 if we can be applied in either direction??)
##    def _swap(self):
##        assert self.direction # otherwise we'd literally swap them
##        self.attrdiffs = self.rev_attrdiffs # assume this is done after these were built up (should this attr be missing otherwise?)
##        self.rev_attrdiffs = {}
##        self.direction = - self.direction
##    def store(self, objkey, attr, val):
##        "this is mainly just example code, in reality we'd do some of this outside a loop, inline the rest"
##        key2val = self.attrdiffs.get(attr, {})
##        key2val[objkey] = val
##    def apply_to(self, archive, direction):####@@@@ stub, apparently, as of 060216; see also the become_state functions, which have similar code
##        """Change the archive model objects by storing into them the attrvals we have recorded for them
##        (for a subset of obj,attr pairs), and pulling out the values we're overwriting
##        so we'll have enough info to undo this change later..
##        """
##        if self.direction:
##            assert self.direction == direction #k does this belong in caller? is it redundant with varid_vers?
##        obj4key = archive.obj4key # for efficiency, let this be a public dict in archive
##        objs_touched = {} # by any attrs... for merging diffs, it might be better for caller to pass this and do the update,
##         #e  but then if our attrs come in layers, caller has to scan the diffs to merge one layer at a time, maybe... not sure;
##         # maybe it only has to do that for update, ie track objs touched in each layer.
##        #e we're not bothering to distinguish which attrs were touched, for now; later we might divide attrs into layers,
##        # do layers in order, update after each layer, just objs touched in that layer.
##        # Or, we might tell certain objs which attrs were touched (ie let them handle the touching, not setattr).
##        for attr, key2val in self.attrdiffs.items():
##            dflt = None # might be specific to attr; might be gotten out of obj.__class__??
##            key2old = {} # replaces key2val
##            for key, val in key2val.iteritems():
##                obj = obj4key[key]
##                # put val in obj at attr, but record the old val first, also update obj later
##                #e in future we might ask obj if it wants us to do this in a special way
##                oldval = getattr(obj, attr, dflt)
##                setattr(obj, attr, val)
##                objs_touched[key] = obj
##                # we don't need to copy val, since we're not keeping it (we already owned it, now obj does),
##                # or oldval, since obj no longer has it!
##                ##e assume we don't need to encode/decode them either
##                key2old[key] = oldval
##            # store key2old, zap key2val
##            self.rev_attrdiffs[attr] = key2old
##            del self.attrdiffs[attr]
##        assert not self.attrdiffs
##        for obj in objs_touched.values():
##            archive.update_touched_obj(obj) #e need to use a special order?? #e "touched" is putting it mildly
##        #e were varid-vers part of the ordinary attrs that got modified just now??
##        self._swap()
##        return
##    pass
##
##class BetterDiff(SimpleDiff): #060210 # someday SimpleDiff will probably go away ####@@@@ use this
##    """A more efficient diff, which only records differences between its checkpoints,
##    and also implements its own finalize method
##    """
##    def __init__(self, cp0, cp1 = None, direction = 1, **options):
##        assert 0 # not used as of before 060227, but slated to be used soon
##        if cp1 is None:
##            pass ####@@@@ cp1 is new checkpoint
##        SimpleDiff.__init__(self, cp0, cp1, direction, **options) ###e need to be passed cp1?? yes, privately...
##        # similarly to self.command_info, we need a private shared place to store the diff data for one or the other direction,
##        # and to know which direction it's in
##        self.shared_diffop_data = self.options.get('_shared_diffop_data', None)
##        if self.shared_diffop_data is None:
##            self.shared_diffop_data = SharedDiffopData()
##        self.options['_shared_diffop_data'] = self.shared_diffop_data
##    def apply_to(self, archive):
##        "apply this diff-operation to the model objects owned by archive"
##        cp = self.cps[1]
##        assert cp.complete
##        #e assert cps[0] is where we start?
##        self.shared_diffop_data.apply_to( archive, self.direction)
##        assy = archive.assy
##        ## assy.become_state(cp.state, archive) # note: in present implem this might effectively redundantly do some of restore_view() [060123]
##        cp.metainfo.restore_view(assy)
##            # note: this means Undo restores view from beginning of undone command,
##            # and Redo restores view from end of redone command.
##            #e (Also worry about this when undoing or redoing a chain of commands.)
##        cp.metainfo.restore_assy_change_counters(assy) # change current-state varid_vers records
##        archive.set_last_cp_after_undo(cp) #060301
##        return
##    pass

# ==

_last_real_class_for_name = {}

def undo_classname_for_decls(class1):
    """Return Undo's concept of a class's name for use in declarations,
    given either the class or the name string. For dotted classnames (of builtin objects)
    this does not include the '.' even if class1.__name__ does (otherwise the notation
    "classname.attrname" would be ambiguous). Note that in its internal object analysis tables,
    classnames *do* include the '.' if they have one (if we have any tables of names,
    as opposed to tables of classes).
    """
    try:
        res = class1.__name__ # assume this means it's a class
    except AttributeError:
        res = class1 # assume this means it's a string
    else:
        res = res.split('.')[-1] # turn qt.xxx into xxx
        assert not '.' in res # should be impossible here
        #e should assert it's really a class -- need to distinguish new-style classes here??
        _last_real_class_for_name[res] = class1 ##k not sure if this is enough to keep that up to date
    assert type(res) == type("name")
    assert not '.' in res, 'dotted classnames like %r are not allowed, since then "classname.attrname" would be ambiguous' % (res,)
    return res

class _testclass: pass

assert undo_classname_for_decls(_testclass) == "_testclass"
assert undo_classname_for_decls("_testclass") == "_testclass"


_classname_for_nickname = {}

def register_class_nickname(name, class1):
    """Permit <name>, in addition to class1.__name__ (or class1 itself if it's a string),
    to be used in declarations involving class1 to the Undo system.
       This should be used only (or mainly) when the actual class name is deprecated and the class is slated
    to be renamed to <name> in the future, to permit declarations to use the preferred name in advance.
    Internally (for purposes of state decls), the Undo system will still identify all classes by their value of __name__
    (or its last component [I think], if __name__ contains a '.' like for some built-in or extension classes).
    """
    assert not '.' in name
    realname = undo_classname_for_decls(class1)
    _classname_for_nickname[name] = realname
    return

#e refile, in this file or another? not sure.

def register_undo_updater( func, updates = (), after_update_of = () ):
    ####@@@@ THIS IS NIM, its effect is kluged elsewhere [still true 060314]
    """Register <func> to be called on 2 args (archive, assy) every time some AssyUndoArchive mashes some
    saved state into the live objects of the current state (using setattr) and needs to fix things that might
    have been messed up by that or might no longer be consistent.
       The optional arguments <updates> and <after_update_of> affect the order in which the registered funcs
    are run, as described below. If not given for some func, its order relative to the others is arbitrary
    (and there is no way for the others to ask to come before or after it, even if they use those args).
       The ordering works as follows: to "fully update an attr" means that Undo has done everything it might
    need to do to make the values (and presence or absense) of that attr correct, in all current objects of
    that attr's class (including objects Undo needs to create as part of an Undo or Redo operation).
       The things it might need to do are, in order: its own setattrs (or delattrs?? ###k) on that attr;
    that class's _undo_update function; and any <funcs> registered with this function (register_undo_updater)
    which list that attr or its class(??) in their optional <updates> argument (whose syntax is described below).
       That defines the work Undo needs to do, and some of the ordering requirements on that work. The only other
    requirement is that each registered <func> which listed some attrs or classes in its optional
    <after_update_of> argument can't be run until those attrs or classes have been fully updated.
    (To "fully update a class", listed in <after_update_of>, means to update every attr in it which has been
    declared to Undo, except any attrs listed individually in the <updates> argument. [###k not sure this is right or practical])
       (If these requirements introduce a circularity, that's a fatal error we'll detect at runtime.)
       The syntax of <updates> and <after_update_of> is a sequence of classes, classnames, or "classname.attrname"
    strings. (Attrname strings can't be given without classnames, even if only one class has a declared attribute
    of that name.)
       Classnames don't include module names (except for builtin objects whose __class__._name__ includes them).
    All classes of the same name are considered equivalent. (As of 060223 the system isn't designed
    to support multiple classes of the same name, but it won't do anything to stop you from trying. In the future
    we might add explicit support for runtime reloading of classes and upgrading of their instances to the new versions
    of the same classes.)
       Certain classes have nicknames (like 'Chunk' for class molecule) which can be used here because they've been
    specifically registered as permitted, using register_class_nickname.
       [This docstring was written before the code was, and when only one <func> was being registered so far,
    so it's subject to revision from encountering reality (or to being out of date if that revision hasn't
    happened yet). ###k]
    """
    ## print "register_undo_updater ought to register %r but it's nim, or maybe only use of the registration is nim" % func
    # pseudocode
    if "pseudocode":
        from constants import noop
        somethingYouHaveToDo = progress_marker = canon = this_bfr_that = noop
    task = somethingYouHaveToDo(func)
    for name in updates:
        name = progress_marker(canon(name), 'target')
        this_bfr_that(task, name)
    for name in after_update_of:
        name = progress_marker(canon(name), 'requirement')
        # elsewhere we'll set up "attr (as target) comes before class comes before attr (as requirement)" and maybe
        # use different sets of attrs on each side (S_CACHE or not)
        this_bfr_that(name, task)
    return

''' example:
register_undo_updater( _undo_update_Atom_jigs, 
                       updates = ('Atom.jigs', 'Bond.pi_bond_obj'),
                       after_update_of = (Assembly, Node, 'Atom.bonds') # Node also covers its subclasses Chunk and Jig.
                           # We don't care if Atom is updated except for .bonds, nor whether Bond is updated at all,
                           # which is good because *we* are presumably a required part of updating both of those classes!
                    )
'''

# ==

# These three functions go together as one layer of the API for using checkpoints.
# They might be redundant with what's below or above them (most likely above, i.e.
# they probably ought to be archive methods),
# but for now it's clearest to think about them in this separate layer.

def make_empty_checkpoint(assy, cptype = None):
    """Make a new Checkpoint object, with no state.
    Sometime you might want to call fill_checkpoint on it,
    though in the future there will be more incremental options.
    """
    cp = Checkpoint(assy_debug_name = assy._debug_name)
        # makes up cp.ver -- would we ideally do that here, or not?
    cp.cptype = cptype #e put this inside constructor? (i think it's always None or 'initial', here)
    cp.assy_change_counters = None # None means they're not yet known
    return cp

def current_state(archive, assy, **options):
    """Return a data-like representation of complete current state of the given assy;
    initial flag means it might be too early (in assy.__init__) to measure this
    so just return an "empty state".
       On exception while attempting to represent current state, print debug error message
    and return None (which is never used as return value on success).
    """
    try:
        #060208 added try/except and this debug_pref
        pkey = "simulate one undo checkpoint bug"
        if debug_pref("simulate bug in next undo checkpoint", Choice_boolean_False, prefs_key = pkey):
            env.prefs[pkey] = False
            assert 0, "this simulates a bug in this undo checkpoint"
        data = mmp_state_from_assy(archive, assy, **options)
    except:
        print_compact_traceback("bug while determining state for undo checkpoint %r; subsequent undos might crash: " % options )
            ###@@@ need to improve situation in callers so crash warning is not needed (mark checkpoint as not undoable-to)
            # in the meantime, it might not be safe to print a history msg now (or it might - not sure); I think i'll try:
        from HistoryWidget import redmsg # not sure this is ok to do when this module is imported, tho probably it is
        env.history.message(redmsg("Bug: Internal error while storing Undo checkpoint; it might not be safe to Undo to this point."))
        data = None
    return data

def fill_checkpoint(cp, state, assy): #e later replace calls to this with cp method calls
    env.change_counter_checkpoint() ###k here?? store it??
    assert cp is not None
    assert not cp.complete
    cp.store_complete_state(state)
    # Note: we store assy.all_change_counters() in two places, cp and cp.metainfo, both of which are still used as of 060227.
    # Each of them is used in more than one place in this file, I think (i.e. 4 uses in all, 2 for each).
    # This ought to be fixed but I'm not sure how is best, so leaving both places active for now. [bruce 060227]
    cp.assy_change_counters = assy.all_change_counters() #060121, revised to use all_ 060227
    cp.metainfo = checkpoint_metainfo(assy) # also stores redundant assy.all_change_counters() [see comment above]
        # this is only the right time for this info if the checkpoint is filled at the right time.
        # We'll assume we fill one for begin and end of every command and every entry/exit into recursive event processing
        # and that ought to be enough. Then if several diffs get merged, we have lots of cp's to combine this info from...
        # do we also need to save metainfo at specific diff-times *between* checkpoints? Not sure yet -- assume no for now;
        # if we need this someday, consider "internal checkpoints" instead, since we might need to split the diffsequence too.
    return

# ==

class checkpoint_metainfo:
    """Hold the metainfo applicable at some moment in the undoable state...
    undecided whether one checkpoint and/or diff might have more than one of these.
    E.g. for a diff we might have this at start of first command in it, at first and last diff in it, and at end of command;
    for checkpoint we might have it for when we finalize it.
       Don't hold any ref to assy or glpane itself!
    """
    def __init__(self, assy):
        self.set_from(assy) #e might not always happen at init??
    def set_from(self, assy):
        try:
            glpane = assy.o # can fail even at end of assy.__init__, but when it does, assy.w.glpane does too
        except:
            self.view = "initial view not yet set - stub, will fail if you undo to this point" ######@@@@@@
            if env.debug():#060301 - does this ever happen (i doubt it)
                print "debug:",self.view
        else:
            self.view = current_view_for_Undo(glpane, assy) # Csys object (for now), with an attribute pointing out the current Part
            ###e should this also save the current mode, considered as part of the view??? [060301]
        self.time = time.time()
        #e cpu time?
        #e glpane.redraw_counter? (sp?)
        self.assy_change_counters = assy.all_change_counters()
        # history serno that will be used next 
        self.next_history_serno = env.last_history_serno + 1 # [060301]
            ###e (also worry about transient_msgs queued up, re this)
        #e current cmd on whatever stack of those we have? re recursive events if this matters? are ongoing tasks relevant??
        #e current part or selgroup or its index [#k i think this is set in current_view_for_Undo]
        return
    def restore_view(self, assy):
        "restore the view & current part from self (called at end of an Undo or Redo command)"
            # also selection? _modified? window_caption (using some new method on assy that knows it needs to do that)?
        glpane = assy.o
        set_view_for_Undo(glpane, assy, self.view)
            # doesn't animate, for now -- if it does, do we show structure change before, during, or after?
            #e sets current selgroup; doesn't do update_parts; does it (or caller) need to?? ####@@@@
        #e caller should do whatever updates are needed due to this (e.g. gl_update)
    def restore_assy_change_counters(self, assy):
        #e ... and not say it doesn't if the only change is from a kind that is not normally saved.
        assy.reset_changed_for_undo( self.assy_change_counters) # never does env.change_counter_checkpoint() or the other one
    pass

def current_view_for_Undo(glpane, assy): #e shares code with saveNamedView
    """Return the current view in this glpane which is showing this assy,
    with additional attributes saved along with the view by Undo (i.e. the index of the current selection group).
    (The assy arg is used for multiple purposes specific to Undo.)
    WARNING: present implem of saving current Part (using its index in MT) is not suitable for out-of-order Redo.
    """
    from Utility import Csys
    oldc = assy.all_change_counters()
    
    csys = Csys(assy, "name", glpane.scale, glpane.pov, glpane.zoomFactor, glpane.quat)
    
    newc = assy.all_change_counters()
    assert oldc == newc
    
    csys.current_selgroup_index = assy.current_selgroup_index() # storing this on the csys is a kluge, but should be safe
    
    return csys # ideally would not return a Node but just a "view object" with the same 4 elements in it as passed to Csys

def set_view_for_Undo(glpane, assy, csys): # shares code with Csys.set_view; might be very similar to some GLPane method, too
    """Restore the view (and the current Part) to what was saved by current_view_for_Undo.
    WARNING: present implem of saving current Part (using its index in MT) is not suitable for out-of-order Redo.
    WARNING: might not gl_update, assume caller does so [#k obs warning?]
    """
    ## compare to Csys.set_view (which passes animate = True) -- not sure if we want to animate in this case [we do, for A8],
    # but if we do, we might have to do that at a higher level in the call chain
    self = glpane # dubious correctness re new prefs usage [060314]
    restore_view = env.prefs[undoRestoreView_prefs_key] #060314
    restore_current_part = True # always do this no matter what
    ## restore_mode?? nah (not for A7 anyway; unclear what's best in long run)
    if restore_view:
        if type(csys) == type(""):
            from VQT import V,Q
            #####@@@@@ code copied from GLPane.__init__, should be shared somehow, or at least comment GLPane and warn it's copied
            #e also might not be the correct view, it's just the hardcoded default view... but i guess it's correct.
            # rotation
            self.quat = Q(1, 0, 0, 0)
            # point of view (i.e. negative of center of view)
            self.pov = V(0.0, 0.0, 0.0)
            # half-height of window in Angstroms (gets reset by certain view-changing operations [bruce 050615 comment])
            self.scale = 10.0
            # zoom factor
            self.zoomFactor = 1.0
        else:
            self.animateToView(csys.quat, csys.scale, csys.pov, csys.zoomFactor, animate = False)
                # if we want this to animate, we probably have to move that higher in the call chain and do it after everything else
    if restore_current_part:
        if type(csys) == type(""):
            if env.debug():
                print "debug: fyi: cys == '' still happens" # does it? ###@@@ 060314 remove if seen, or if not seen
            current_selgroup_index = 0
        else:
            current_selgroup_index = csys.current_selgroup_index
        sg = assy.selgroup_at_index(current_selgroup_index)
        assy.set_current_selgroup(sg)
            #e how might that interact with setting the selection? Hopefully, not much, since selection (if any) should be inside sg.
    #e should we update_parts?
    return

# ==

from idlelib.Delegator import Delegator
# print "Delegator",Delegator,type(Delegator),`Delegator`

class MergingDiff(Delegator):
    "A higher-level diff, consisting of a diff with some merging options which cause more diffs to be applied with it"
    def __init__(self, diff, flags = None, archive = None):
        Delegator.__init__(self, diff) # diff is now self.delegate; all its attrs should be constant since they get set on self too
        self.flags = flags
        self.archive = archive # this ref is non-cyclic, since this kind of diff doesn't get stored anywhere for a long time
    def apply_to(self, archive):
        res = self.delegate.apply_to(archive)
        # print "now we should apply the diffs we would merge with",self #####@@@@@
        return res
    # def __del__(self):
    #     print "bye!" # this proves it's readily being deleted...
    pass

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
    format_options = dict(use_060213_format = True)
        # Note: this is never changed and use_060213_format = False is not supported, but preserve this until we have another format option
        # that varies, in case we need one for diffing some attrs in special ways. Note: use_060213_format appears in state_utils.py too.
        # [bruce 060314]

    copy_val = state_utils.copy_val #060216, might turn out to be a temporary kluge ###@@@

    inited = False
    
    def __init__(self, assy):
        self.assy = assy # represents all undoable state we cover (this will need review once we support multiple open files)

        self.obj_classifier = obj_classifier()
        
        self.objkey_allocator = oka = objkey_allocator()
        self.obj4key = oka.obj4key # public attr, maps keys -> objects
            ####@@@@ does this need to be the same as atom keys? not for now, but maybe yes someday... [060216]
        
        self.stored_ops = {} # map from (varid, ver) pairs to lists of diff-ops that implement undo or redo from them;
            # when we support out of order undo in future, this will list each diff in multiple places
            # so all applicable diffs will be found when you look for varid_ver pairs representing current state.
            # (Not sure if that system will be good enough for permitting enough out-of-order list-modification ops.)

        # == above is general; below is specific to the kind of data we find in an assembly (Atoms, Bonds, Chunks...)
        
        # change tracking dicts for Atoms and Bonds (not sure we want them here, as opposed to inside current_diff...) [bruce 060315]
        self._changed_parent_Atoms = {} # atom.key -> atom (not objkey!) for atoms w/ changed assy or molecule or liveness/killedness
            # (an atom's assy is atom.molecule.assy; no need to track changes here to the mol's .part or .dad)
        self._changed_structure_Atoms = {} ###e format TBD, but tracks changes to element, atomtype, bond set (###k bond order?)
        self._changed_posn_Atoms = {} # tracks changes to atom._posn (not clear what it'll do when we can treat baseposn as defining state)
        self._changed_picked_Atoms = {} # tracks changes to atom.picked (not to _pick_time etc, we don't cover that in Undo)

        self._changed_otherwise_Atoms = {} # tracks all other model changes to Atoms (display mode; not sure if any more ###k)

        self._changed_Bonds = {} # tracks all changes to Bonds: existence, which atoms, bond order. [bond.key or id(bond) is TBD ###k]

        # rest of init is done later, by self.initial_checkpoint, when caller is more ready [060223]
        ###e not sure were really inited enough to return... we'll see
        return

    def _clear(self):
        """[private helper method for self.clear_undo_stack()]
        Clear our main data stores, which are set up in __init__, and everything referring to undoable objects or objkeys.
        (But don't clear our obj_classifier.)
        """
        self.current_diff.destroy()
        self.current_diff = None
        self.next_cp = None
        self.stored_ops = {}
        self.objkey_allocator.clear() # after this, all existing keys (in diffs or checkpoints) are nonsense...
        # ... so we'd better get rid of them (above and here):
        self.inited = False
        self.initial_checkpoint() # should we clean up the code by making this the only way to call initial_checkpoint?
        return

    def initial_checkpoint(self): # called by clear_undo_stack in two ways??? one by undo_manager? ###doc situation [060304]
        assert not self.inited
        assy = self.assy
        cp = make_empty_checkpoint(assy, 'initial') # initial checkpoint
        #e the next three lines are similar to some in self.checkpoint --
        # should we make self.set_last_cp() to do part of them? compare to do_op's effect on that, when we code that. [060118] [060301 see also set_last_cp_after_undo]
        fill_checkpoint(cp, current_state(self, assy, initial = True, **self.format_options), assy) ### it's a kluge to pass initial; revise to detect this in assy itself
        if self.pref_report_checkpoints():
            self.debug_histmessage("(initial checkpoint: %r)" % cp)
        self.last_cp = self.initial_cp = cp
##        self.last_cp_arrival_reason = 'initial' # why we got to the situation of model state agreeing with this, when last we did
            #e note, self.last_cp will be augmented by a desc of varid_vers pairs about cur state; 
            # but for out of order redo, we get to old varid_vers pairs but new cp's; maybe there's a map from one to the other...
            ###k was this part of UndoManager in old code scheme? i think it was grabbed out of actual model objects in UndoManager.
        self.inited = True # should come before _setup_next_cp
        self._setup_next_cp() # don't know cptype yet (I hope it's 'begin_cmd'; should we say that to the call? #k)
        ## self.notify_observers() # current API doesn't permit this to do anything during __init__, since subs is untouched then
        return
    
    def destroy(self): #060126 precaution
        "free storage, make doing of our ops illegal (noop with bug warning; or maybe just exception)"
        if self.pref_report_checkpoints():
            self.debug_histmessage("(destroying: %r)" % self)
        self.next_cp = self.last_cp = self.initial_cp = None
        self.assy = None
        self.stored_ops = {} #e more, if it can contain any cycles -- design was that it wouldn't, but true situation not reviewed lately [060301]
        self.current_diff = None #e destroy it first?
        self.objkey_allocator.destroy()
        self.objkey_allocator = None
        return
    
    def __repr__(self):
        return "<AssyUndoArchive at %#x for %r>" % (id(self), self.assy) # if destroyed, assy will be None

    # ==

    def _setup_next_cp(self):
        """[private method, mainly for begin_cmd_checkpoint:]
        self.last_cp is set; make (incomplete) self.next_cp, and self.current_diff to go between them.
        Index it... actually we probably can't fully index it yet if that depends on its state-subset vers.... #####@@@@@
        """
        assert self.inited
        assert self.next_cp is None
        self.next_cp = make_empty_checkpoint(self.assy) # note: we never know cptype yet, tho we might know what we hope it is...
        self.current_diff = SimpleDiff(self.last_cp, self.next_cp) # this is a slot for the actual diff, whose content is not yet known
            # this attr is where change-trackers would find it to tell it what changed (once we have any)
            # assume it's too early for indexing this, or needing to -- that's done when it's finalized
        return

    def set_last_cp_after_undo(self, cp): # 060301
        """We're doing an Undo or Redo command which has just caused actual current state (and its change_counters) to equal cp.state.
        Therefore, self.last_cp is no longer relevant, and that attr should be set to cp so further changes are measured relative to that
        (and self.current_diff and next_cp should be freshly made, forking off from it -- or maybe existing self.next_cp can be recycled for this;
        also we might need some of the flags in self.current_diff... but not the changes, I think, which either don't exist yet or are
        caused by tracking changes applied by the Undo op itself).
           (Further modelstate changes by this same Undo/Redo command are not expected and might cause bugs -- if they result in a diff,
        it would be a separate undoable diff and would prevent Redo from being available. So we might want to assert that doesn't happen,
        but if such changes *do* happen it's the logically correct consequence, so we don't want to try to alter that consequence.)
        """
        assert self.inited
        assert self.last_cp is not None
        assert self.next_cp is not None
        assert self.current_diff is not None
        assert cp is not None
        assert self.last_cp is not cp # since it makes no sense if it is, though it ought to work within this routine
        # not sure this is right, but it's simplest that could work, plus some attempts to clean up unused objects:
        self.current_diff.destroy() # just to save memory; might not be needed (probably refdecr would take care of it) since no ops stored from it yet
        self.last_cp.end_of_undo_chain_for_awhile = True # not used by anything, but might help with debugging someday; "for awhile" because we might Redo to it
        self.last_cp = cp
            ###@@@ we might need to mark cp for later freeing of its old Redo stack if we depart from it other than by another immediate Undo or Redo...
            # tho since we might depart from somewhere else on that stack, never mind, we should instead
            # just notice the departure and find the stuff to free at that time.
        # next_cp can be recycled since it's presently empty, I think, or if not, it might know something useful ####@@@@ REVIEW
        self.current_diff = SimpleDiff(self.last_cp, self.next_cp)
        self.current_diff.assert_no_changes = True # fyi: used where we check assy_change_counters
        return
        
    def clear_undo_stack(self): #bruce 060126 to help fix bug 1398 (open file left something on Undo stack) [060304 removed *args, **kws]
        assert self.inited # note: the same-named method in undo_manager instead calls initial_checkpoint the first time
        if self.current_diff: #k probably always true; definitely required for it to be safe to do what follows.
            self.current_diff.suppress_storing_undo_redo_ops = True # note: this is useless if the current diff turns out to be empty.

            if 1: #060304 try to actually free storage; I think this will work even with differential checkpoints...
                self._clear()

##                #obs comments? [as of 060304]
##                #e It might be nice to also free storage for all prior checkpoints and diffs
##                # (by erasing them from stored_ops and from any other refs to them),
##                # but I'm worried about messing up too many things
##                # (since this runs from inside some command whose diff-recording is ongoing).
##                # If we decide to do that, do it after the other stuff here, to all cp's/diffs before last_cp. #e
##                # This shouldn't make much difference in practice
##                # (for existing calls of this routine, from file open & file close), so don't bother for now.
##                #
##                # In order to only suppress changes before this method is called, rather than subsequent ones too,
##                # we also do a special kind of checkpoint here.
##                self.checkpoint( cptype = "clear")
##                #
##                self.initial_cp = self.last_cp # (as of 060126 this only affects debug_undo2 prints)
            pass
        return
    
    def pref_report_checkpoints(self): #bruce 060127 revised meaning and menutext, same prefs key
        "whether to report all checkpoints which see any changes from the prior one"
        res = debug_pref("undo/report changed checkpoints", Choice_boolean_False,
                         prefs_key = "_debug_pref_key:" + "undo/report all checkpoints")
        return res

    def debug_histmessage(self, msg):
        env.history.message(msg, quote_html = True, color = 'gray')

    def update_before_checkpoint(self): # see if this shows up in any profiles [split this out 060309]
        "#doc"
        ##e these need splitting out (and made registerable) as "pre-checkpoint updaters"... note, they can change things,
        # ie update change_counters, but that ought to be ok, as long as they can't ask for a recursive checkpoint,
        # which they won't since only UI event processors ever ask for those. [060301]
        
        self.assy.update_parts() # make sure assy has already processed changes (and assy.changed has been called if it will be)
            #bruce 060127, to fix bug 1406 [definitely needed for 'end...' cptype; not sure about begin, clear]
            # note: this has been revised from initial fix committed for bug 1406, which was in assembly.py and
            # was only for begin and end cp's (but was active even if undo autocp pref was off).

        #bruce 060313: we no longer need to update mol.atpos for every chunk. See comments in chunk.py docstring about atom.index.
        # [removed commented-out code for it, 060314]
        return
    
    def checkpoint(self, cptype = None, cmdname_for_debug = "", merge_with_future = False ): # called from undo_manager
        """When this is called, self.last_cp should be complete, and self.next_cp should be incomplete,
        with its state defined as equalling the current state, i.e. as a diff (which is collecting current changes) from last_cp,
        with that diff being stored in self.current_diff.
        And this diff might or might not be presently empty. (#doc distinction between changes we record but don't count as nonempty,
        like current view, vs those we undo but would not save in a file (selection), vs others.)
           We should finalize self.next_cp with the current state, perhaps optimizing this if its defining diff is empty,
        and then shift next_cp into last_cp and a newly created checkpoint into next_cp, recreating a situation like the initial one.
           In other words, make sure the current model state gets stored as a possible point to undo or redo to.
           Note [060301]: similar but different cp-shifting might occur when an Undo or Redo command is actually done.
        Thus, if this is the end-checkpoint after an Undo command, it might find last_cp being the cp "undone to" by that command
        (guess as of 060301 1159am, nim #k ###@@@).
        """
        if not self.inited:
            if env.debug():
                print_compact_stack("debug note: undo_archive not yet inited (maybe not an error)")
            return

##        if 0: # bug 1440 debug code 060320, and 1747 060323
##            print_compact_stack("undo cp, merge=%r: " % merge_with_future)
        
        if not merge_with_future:
            #060312 added 'not merge_with_future' cond as an optim; seems ok even if this would set change_counters,
            # since if it needs to run, we presume the user ops will run it on their own soon enough and do another
            # checkpoint.
            self.update_before_checkpoint()

        assert cptype
        assert self.last_cp is not None
        assert self.next_cp is not None
        assert self.current_diff is not None
        
        # Finalize self.next_cp -- details of this code probably belong at a lower level related to fill_checkpoint #e
        ###e specifically, this needs moving into the new method (to be called from here)
        ## self.current_diff.finalize(...)

        # as of sometime before 060309, use_diff is only still an option for debugging/testing purposes:
        use_diff = debug_pref("use differential undo?", Choice_boolean_True, prefs_key = 'A7-devel/differential undo')
                ## , non_debug = True) #bruce 060302 removed non_debug
            # it works, 122p 060301, so making it default True and non_debug.
            # (It was supposed to traceback when undoing to initial_state, but it didn't,
            #  so I'm "not looking that gift horse in the mouth" right now. ###@@@)
            #k see also comments mentioning 'differential'
            
        # maybe i should clean up the following code sometime...
        debug3 = 0 and env.debug() # for now [060301] if 0 060302; this is here (not at top of file) so runtime env.debug() affects it
        if debug3:
            print "\ncp", self.assy.all_change_counters(), env.last_history_serno + 1
        if merge_with_future:
            #060309, partly nim; 060312 late night, might be done!
            if 0 and env.debug():
                print "debug: skipping undo checkpoint"
            ### Here's the plan [060309 855pm]:
            # in this case, used when auto-checkpointing is disabled, it's almost like not doing a checkpoint,
            # except for a few things:
            # + we update_parts (etc) (done above) to make sure change counters are accurate
            #   (#e optim: let caller flag say if that's needed)
            # - we make sure that change counter info (or whatever else is needed)
            #   will be available to caller's remake_UI_menuitems method
            #   - that might include what to say in Undo, like "undo to what history serno for checkpoint or disabling", or in Redo
            #   - #e someday the undo text might include info on types of changes, based on which change counters got changed
            #   - ideally we do that by making current_diff know about it... not sure if it gets stored but still remains current...
            #     if so, and if it keeps getting updated in terms of end change counters, do we keep removing it and restoring it???
            #     or can we store it on a "symbolic index" meaning "current counters, whatever they may be"??? ###
            #   - but i think a simpler way is just to decide here what those menu items should be, and store it specially, for undo,
            #     and just trash redo stack on real change but let the ui use the stored_ops in usual way otherwise, for Redo.
            #     Note that Redo UI won't be updated properly until we implement trashing the redo stack, in that case!
            # - we trash the redo stack based on what changed, same as usual (nim, this case and other case, as of 060309 852p).
            if self.last_cp.assy_change_counters == self.assy.all_change_counters():
                pass # nothing new; Undo being enabled can be as normal, based on last_cp #####@@@@@
            else:
                # a change -- Undo should from now on always be enabled, and should say "to last manual cp" or
                # "to when we disabled autocp" 
                ####k Note: we need to only pay attention to changes that should be undoable, not e.g. view changes,
                # in the counters used above for these tests! Otherwise we'd enable Undo action
                # and destroy redo stack when we shouldn't. I think we're ok on this for now, but only because
                # calls to the view change counter are nim. ####@@@@ [060312 comment]
                if destroy_bypassed_redos:
                    self.clear_redo_stack( from_cp = self.last_cp, except_diff = self.current_diff ) # it's partly nim as of 060309
                        # this is needed both to save RAM and (only in this merge_with_future case) to disable the Redo menu item
                # set some flags about that, incl text based on what kind of thing has changed
                self.current_diff.command_info['n_merged_changes'] += 1 # this affects find_undoredos [060312 10:16pm]
                    # starts out at 0 for all diffs; never set unless diff w/ changes sticks around for more
                    ####@@@@ this number will be too big until we store those different change_counters and compare to *them* instead;
                    # just store them right now, and comparison above knows to look for them since n_merged_changes > 0;
                    # but there's no hurry since the menu text is fine as it is w/o saying how many cmds ran ###e
                ##e this would be a good time to stash the old cmdname in the current_diff.command_info(sp?)
                # and keep the list of all of them which contributed to the changes,
                # for possible use in coming up with menu_desc for merged changes
                # (though change_counters might be just as good or better)
            pass
        else:
            if 0 and env.debug():
                print "debug: NOT skipping undo checkpoint" # can help debug autocp/manualcp issues [060312]
            # entire rest of method
            if self.last_cp.assy_change_counters == self.assy.all_change_counters():
                # no change in state; we still keep next_cp (in case ctype or other metainfo different) but reuse state...
                # in future we'll still need to save current view or selection in case that changed and mmpstate didn't ####@@@@
                if debug_undo2 or debug3:
                    print "checkpoint type %r with no change in state" % cptype, self.assy.all_change_counters(), env.last_history_serno + 1
                    if env.last_history_serno + 1 != self.last_cp.next_history_serno():
                        print "suspicious: env.last_history_serno + 1 (%d) != self.last_cp.next_history_serno() (%d)" % \
                              ( env.last_history_serno + 1 , self.last_cp.next_history_serno() )
                really_changed = False
                state = self.last_cp.state
                #060301 808p part of bugfix for "bug 3" [remove this cmt in a few days];
                # necessary when use_diff, no effect when not
            else:
                # possible change in state;
                # false positives are not common enough to optimize for, but common enough to try to avoid/workaround bugs in

                ## assert not self.current_diff.assert_no_changes...
                # note, its failure might no longer indicate a bug if we have scripting and a script can say,
                # inside one undoable operation, "undo to point P, then do op X".
                if self.current_diff.assert_no_changes: #060301
                    msg = "apparent bug in Undo: self.current_diff.assert_no_changes is true, but change_counters were changed"
                    # we don't yet know if there's a real diff, so if this happens, we might move it later down, inside 'if really_changed'.
                    print msg
                    from HistoryWidget import redmsg # not sure this is ok to do when this module is imported, tho probably it is
                    env.history.message(redmsg(msg))
                
                if debug_undo2:
                    print "checkpoint %r at change %r, last cp was at %r" % (cptype, \
                                    self.assy.all_change_counters(), self.last_cp.assy_change_counters)
                if not use_diff:
                    state = current_state(self, self.assy, **self.format_options) ######@@@@@@ need to optim when only some change_counters changed!
                    really_changed = (state != self.last_cp.state) # this calls StateSnapshot.__ne__ (which calls __eq__) [060227]
                    if not really_changed and env.debug():
                        print "debug: note: detected lack of really_changed using (state != self.last_cp.state)"
                            ###@@@ remove when works and no bugs then
                else:
                    #060228
                    assert self.format_options == dict(use_060213_format = True), "nim for mmp kluge code" #e in fact, remove that code when new bugs gone
                    state = diff_and_copy_state(self, self.assy, self.last_cp.state)
#obs, it's fixed now [060301]
##                        # note: last_cp.state is no longer current after an Undo!
##                        # so this has a problem when we're doing the end-cmd checkpoint after an Undo command.
##                        # goal: diffs no longer form a simple chain... rather, it forks.
##                        # hmm. we diff against the cp containing the current state! (right?) ### [060301]
                    really_changed = state.really_changed
                    if not really_changed and debug3: # see if this is printed for bug 3, 060301 8pm [it is]
                        print "debug: note: detected lack of really_changed in diff_and_copy_state"
                        ###@@@ remove when works and no bugs then
                        # ok, let's get drastic (make debug pref if i keep it for long):
                        ## state.print_everything() IMPLEM  ####@@@@
                        print "state.lastsnap.attrdicts:", state.lastsnap.attrdicts # might be huge; doesn't contain ids of mutables
                    elif debug3: # condition on rarer flag soon,
                        # or have better debug pref for undo stats summary per chgcounter'd cp ###e doit
                        print "debug: note: real change found by diff_and_copy_state"
                if not really_changed:
                    # Have to reset changed_counters, or undo stack becomes disconnected, since it uses them as varid_vers.
                    # Not needed in other case above since they were already equal.
                    # Side benefit: will fix file-modified indicator too (though in some cases its transient excursion to "modified" during
                    #  a drag, and back to "unmodified" at the end, might be disturbing). Bug: won't yet fix that if sel changed, model didn't.
                    #####e for that, need to reset each one separately based on what kind of thing changed. ####@@@@ doit!
                    self.assy.reset_changed_for_undo( self.last_cp.assy_change_counters)
            if really_changed:
                self.current_diff.empty = False # used in constructing undo menu items ####@@@@ DOIT!
                if destroy_bypassed_redos:
                    #####@@@@@ this might be a good place to destroy the Redo stack to save RAM, since we just realized we had a "newdo";
                    # but it might be complicated, e.g. if the new change was on one of those sub-stacks in front of the main one,
                    # or in one Part when those have separate stacks, etc...
                    # the stuff to destroy (naively) is everything linked to from self.last_cp except self.current_diff / self.next_cp, *i think*.
                    # What would be easy would be a debug-print saying whether it looks like there's anything to destroy,
                    # so we could tell if its guesses seem accurate. [060301]
                    self.clear_redo_stack( from_cp = self.last_cp, except_diff = self.current_diff ) # it's partly nim as of 060309
            else:
                # not really_changed
                # guess: following line causes bug 3 when use_diff is true
                if not use_diff:
                    state = self.last_cp.state
                        # note: depending on how this is reached, it sets state for first time or replaces it with an equal value
                        # (which is good for saving space -- otherwise we'd retain two equal but different huge state objects)
                else:
                    pass # in this case there's no motivation, and (guess) it causes "bug 3", so don't do it,
                        # but do set state when assy_change_counters says no change [done] 060301 8pm
                self.current_diff.empty = True
                self.current_diff.suppress_storing_undo_redo_ops = True # (this is not the only way this flag can be set)
                    # I'm not sure this is right, but as long as varid_vers are the same, or states equal, it seems to make sense... #####@@@@@
            fill_checkpoint(self.next_cp, state, self.assy) # stores self.assy.all_change_counters() onto it -- do that here, for clarity?
                #e This will be revised once we incrementally track some changes - it won't redundantly grab unchanged state,
                # though it's likely to finalize and compress changes in some manner, or grab changed parts of the state.
                # It will also be revised if we compute diffs to save space, even for changes not tracked incrementally.
                #e also store other metainfo, like time of completion, cmdname of caller, history serno, etc (here or in fill_checkpoint)

            if not self.current_diff.empty and self.pref_report_checkpoints():
                if cptype == 'end_cmd':
                    cmdname = self.current_diff.cmdname()
                else:
                    cmdname = cmdname_for_debug # a guess, used only for debug messages -- true cmdname is not yet known, in general
                if cmdname:
                    desc = "(%s/%s)" % (cptype, cmdname)
                else:
                    desc = "(%s)" % cptype
                self.debug_histmessage( "(undo checkpoint %s: %r)" % (desc, self.next_cp) )
                del cmdname, desc
            
            if not self.current_diff.suppress_storing_undo_redo_ops:
                redo_diff = self.current_diff
                undo_diff = redo_diff.reverse_order()
                self.store_op(redo_diff)
                self.store_op(undo_diff)
                # note, we stored those whether or not this was a begin or end checkpoint;
                # figuring out which ones to offer, merging them, etc, might take care of that, or we might change this policy
                # and only store them in certain cases, probably if this diff is begin-to-end or the like;
                # and any empty diff always gets merged with followon ones, or not offered if there are none. ######@@@@@@
            
            # Shift checkpoint variables        
            self.last_cp = self.next_cp
            self.next_cp = None # in case of exceptions in rest of this method
            self.last_cp.cptype = cptype #k is this the only place that knows cptype, except for 'initial'?
    ##        self.last_cp_arrival_reason = cptype # affects semantics of Undo/Redo user-level ops
    ##            # (this is not redundant, since it might differ if we later revisit same cp as self.last_cp)
            self._setup_next_cp() # sets self.next_cp and self.current_diff
        return

    def clear_redo_stack( self, from_cp = None, except_diff = None ): #060309 (untested)
        "#doc"
        #e scan diff+1s from from_cp except except_diff, thinking of diffs as edges, cp's or their indices as nodes.
        # can we do it by using find_undoredos with an arg for the varid_vers to use instead of current ones?

        # use that transclose utility... on the nodes, i guess, but collect the edges as i go
        # (nodes are state_versions, edges are diffs)
        # (transclose needs dict keys for these nodes... the nodes are data-like so they'll be their own keys)
        
        assert from_cp is not None # and is a checkpoint?
        # but it's ok if except_diff is None
        state_version_start = self.state_version_of_cp(from_cp)
        # toscan = { state_version_start: state_version_start } # TypeError: dict objects are unhashable
        def dictkey(somedict):
            "you know what I meant! assume it was an immutable dict!"
            items = somedict.items()
            items.sort() # a bit silly since in present use there is always just one item, but this won't run super often, i hope
                # (for that matter, in present use that item's key is always the same...)
            # return items # TypeError: list objects are unhashable
            return tuple(items)
        toscan = { dictkey(state_version_start): state_version_start }
        diffs_to_destroy = {}
        def collector(state_version, dict1):
            ops = self._raw_find_undoredos( state_version)
            for op in ops:
                if op.direction == 1 and op is not except_diff: # redo, not undo
                    # found an edge to destroy, and its endpoint node to further explore
                    diffs_to_destroy[op.key] = op
                    state_version_endpoint = self.state_version_of_cp( op.cps[1])
                    dict1[ dictkey(state_version_endpoint)] = state_version_endpoint
            return # from collector
        transclose( toscan, collector) # retval is not interesting to us; what matters is side effect on diffs_to_destroy
        if diffs_to_destroy:
            ndiffs = len(diffs_to_destroy)
            len1 = len(self.stored_ops)
            if env.debug():
                print "debug: clear_redo_stack found %d diffs to destroy" % ndiffs
            for diff in diffs_to_destroy.values():
                diff.destroy() #k did I implem this fully?? I hope so, since clear_undo_stack probably uses it too...
                # the thing to check is whether they remove themselves from stored_ops....
            diffs_to_destroy = None # refdecr them too, before saying we're done (since the timing of that is why we say it)
            toscan = state_version_start = from_cp = None
            len2 = len(self.stored_ops)
            savings = len1 - len2 # always 0 for now, since we don't yet remove them, so don't print non-debug msg when 0 (for now)
            if ndiffs and (savings < 0 or env.debug()):
                print "  debug: clear_redo_stack finished; removed %d entries from self.stored_ops" % (savings,) ###k bug if 0 (always is)
        else:
            if 0 and env.debug():
                print "debug: clear_redo_stack found nothing to destroy"
        return
    
    def current_command_info(self, *args, **kws): ##e should rename add_... to make clear it's not finding and returning it
        assert not args
        if not self.inited:
            if env.debug():
                print_compact_stack("debug note: undo_archive not yet inited (maybe not an error)")
            return
        self.current_diff.command_info.update(kws) # recognized keys include cmd_name
            ######@@@@@@ somewhere in... what? a checkpoint? a diff? something larger? (yes, it owns diffs, in 1 or more segments)
            # it has 1 or more segs, each with a chain of alternating cps and diffs.
            # someday even a graph if different layers have different internal cps. maybe just bag of diffs
            # and overall effect on varidvers, per segment. and yes it's more general than just for undo; eg affects history.
        return
    
    def do_op(self, op): ###@@@ 345pm some day bfr 060123 - figure out what this does if op.prior is not current, etc;
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
        assert self.inited
        # self.current_diff is accumulating changes that occur now,
        # including the ones we're about to do by applying self to assy.
        # Make sure it is not itself later stored (redundantly) as a diff that can be undone or redone.
        # (If it was stored, then whenever we undid a change, we'd have two copies of the same change stored as potential Undos.)
        
        self.current_diff.suppress_storing_undo_redo_ops = True  # [should this also discard self.last_cp as irrelevant??? then apply_to can set it? 060301 Q ###@@@]

        # Some code (find_undoredos) might depend on self.assy.all_change_counters() being a valid
        # representative of self.assy's state version;
        # during op.apply_to( archive) that becomes false (as changes occur in archive.assy), but apply_to corrects this at the end
        # by restoring self.assy.all_change_counters() to the correct old value from the end of the diff.

        # The remaining comments might be current, but they need clarification. [060126 comment]
        
        # in present implem [060118], we assume without checking that this op is not being applied out-of-order,
        # and therefore that it always changes the model state between the same checkpoints that the diff was made between
        # (or that it can ignore and/or discard any way in which the current state disagrees with the diff's start-checkpoint-state).

#bruce 060314 not useful now, but leave the code as example (see longer comment elsewhere):
##        self.mols_with_invalid_atomsets = {} ##@@ KLUGE to put this here -- belongs in become_state or so, but that's
##            # not yet a method of self! BTW, this might be wrong once we merge -- need to review it then. [bruce 060313]
        
        op.apply_to( self) # also restores view to what it was when that change was made [as of 060123]
            # note: actually affects more than just assy, perhaps (ie glpane view state...)
            #e when diffs are tracked, worry about this one being tracked
            #e apply_to itself should also track how this affects varid_vers pairs #####@@@@@

#ditto:
##        del self.mols_with_invalid_atomsets # this will have been used by updaters sometime inside op.apply_to
        
        #060123 202p following [later removed] is wrong since this very command (eg inside some menu item)
        # is going to do its own end-checkpoint.
        # the diffs done by the above apply_to are going to end up in the current diff...
        # what we need to do here is quite unrelated to self.last_cp -- know the varid_vers pairs, used in making undo/redo menuitems.
        # (and i bet last_cp_arrival_reason is similarly wrongheaded
        # and applies instead to (if anything) the "current state" of varid_vers pairs)
        # ... but how do we track the current state's varid_ver pairs? in our own checkpoint filler?
        # at two times:
        # - when random code makes random changes it probably needs to track them... this can be done when those chgs are
        #   packed into a diff, since we're saying "make sure it looks like we just applied this diff as if by redoing this op"
        #   (including having same effect on varid_vers as that would have)
        # - when it makes those while applying a diff, then at least the direct ones inside the diff can have them set to old vals
        #   (tho if updates to restore consistency also run, not sure they fit in -- but in single-varid system that's moot)
        return
    
    def state_version(self):
        ## assy_varid = make_assy_varid(self.assy._debug_name)
        # kluge: optim of above:
        assy_varid = ASSY_VARID_STUB
        assy_ver = self.assy.all_change_counters() # note: this is about totally current state, not any diff or checkpoint;
            # it will be wrong while we're applying an old diff and didn't yet update assy.all_change_counters() at the end
        return {assy_varid: assy_ver} # only one varid for now (one global undo stack) [i guess this is still true with 3 change counters... 060227]

    def state_version_of_cp(self, cp): #060309 ###k maybe this should be (or is already) a cp method...
        return {ASSY_VARID_STUB: cp.assy_change_counters}
        
    def find_undoredos(self):
        "Return a list of undo and/or redo operations that apply to the current state; return merged ops if necessary."
        #e also pass state_version? for now rely on self.last_cp or some new state-pointer...
        if not self.inited:
            return []

        if 1:
            # the following if-condition is a kluge (wrong in principle but probably safe, not entirely sure it's correct) [060309]:
            import undo_manager
            do_warning = undo_manager._AutoCheckpointing_enabled
        else:
            do_warning = True # gives false warnings when not _AutoCheckpointing_enabled
        if do_warning:
            # try to track down some of the bugs... if this is run when untracked changes occurred (and no checkpoint),
            # it would miss everything. If this sometimes happens routinely when undo stack *should* be empty but isn't,
            # it could explain dificulty in reproducing some bugs. [060216]
            if self.last_cp.assy_change_counters != self.assy.all_change_counters():
                print "WARNING: find_undoredos sees self.last_cp.assy_change_counters != self.assy.all_change_counters()", \
                      self.last_cp.assy_change_counters, self.assy.all_change_counters()
            pass

        if self.current_diff.command_info['n_merged_changes']:
            # if the current_diff has any changes at all (let alone merged ones, or more precisely, those intending
            # to merge with yet-unhappened ones, because autocheckpointing is disabled), it's the only applicable one,
            # in the current [060312] single-undo-stack, no-inserted-view-ops scheme. The reason we check specifically
            # for merged changes (not any old changes) is that there's no record of any other kind of changes in current_diff,
            # and when other kinds get noticed in there they immediately cause it to be replaced by a new (empty) current_diff.
            # So there's no way and no point, and the reason there's no need is that non-current diffs get indexed
            # so they can be found in stored_ops by _raw_find_undoredos.
            return [self.current_diff.reverse_order()] ####k ####@@@@ ??? [added this 060312; something like it seems right]
        
        state_version = self.state_version()
        ## state_version = dict([self.last_cp.varid_ver()]) ###@@@ extend to more pairs
        # that's a dict from varid to ver for current state;
        # this code would be happy with the items list but future code will want the dict #e

        res = self._raw_find_undoredos( state_version) #060309 split that out, moved its debug code back here & revised it

        if not res and debug_undo2 and (self.last_cp is not self.initial_cp):
            print "why no stored ops for this? (claims to not be initial cp)", state_version # had to get here somehow...

        if debug_undo2:
            print "\nfind_undoredos dump of found ops, before merging:"
            for op in res:
                print op
            print "end of oplist\n"
        # Need to filter out obsolete redos (not sure about undos, but I guess not) ... actually some UIs might want to offer them,
        # so i'd rather let caller do that (plus it has the separated undo/redo lists).
        # But then to save time, let caller discard what it filters out, and let it do the merging only on what's left --
        # i.e. change docstring and API so caller merges, not this routine (not sure of this yet) #####@@@@@.
        ######@@@@@@ need to merge
        ##k need to store_op at end-checkpoint! right now we store at all cps... will that be ok? probably good...
        ## (or begin, if end missed -- do that by auto-end? what about recursion?
        #   let recursion also end, then begin anew... maybe merge... see more extensive comments mentioning word "cyberspace",
        #   maybe in a notesfile or in code)
        return res

    def _raw_find_undoredos(self, state_version):
        "#doc"
        res = {}
        for var, ver in state_version.items():
            lis = self.stored_ops.get( (var, ver), () )
            for op in lis: #e optim by storing a dict so we can use update here? doesn't matter for now
                if not op.destroyed:
                    ####e cond only needed because destroy doesn't yet unstore them;
                    # but don't bother unstoring them here, it would miss some
                    res[op.key] = op
        # this includes anything that *might* apply... filter it... not needed for now with only one varid in the system. ###@@@
        return res.values()
    
    def store_op(self, op):
        assert self.inited
        for varver in op.varid_vers():
            ops = self.stored_ops.setdefault(varver, [])
            ops.append(op)
        return

    def _n_stored_vals(self): #060309, unfinished, CALL IT as primitive ram estimate #e add args for variants of what it measures ####@@@@
        res = 0
        for oplist in stored_ops.itervalues():
            for op in oplist:
                res += op._n_stored_vals() ###IMPLEM
        return res
    
    def wrap_op_with_merging_flags(self, op, flags = None):
        "[see docstring in undo_manager]"
        return MergingDiff(op, flags = flags, archive = self) # stub
    
    pass # end of class AssyUndoArchive

ASSY_VARID_STUB = 'assy' # kluge [060309]: permit optims from this being constant, as long as this doesn't depend on assy, etc;
    # all uses of this except in make_assy_varid() are wrong in principle, so fix them when that kluge becomes invalid.

def make_assy_varid(assy_debug_name):
    "make the varid for changes to the entire assy, for use when we want a single undo stack for all its Parts"
    ## return 'varid_stub_' + (assy_debug_name or "") #e will come from assy itself
    return ASSY_VARID_STUB # stub, but should work

# end
