# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
undo_archive.py

Collect and organize a set of checkpoints of model state and diffs between them,
providing undo/redo ops which apply those diffs to the model state.

$Id$
'''
__author__ = 'bruce'

from state_utils import copy_val

class UndoArchive:
    
    copy_val = copy_val
    
    def __init__(self):
        self.stored_ops = {} # from varid,vers to dict of ops which apply on that varid,vers (for details of which ops to store, see code)
        self.lastkey = 0
        ### the network of difftypes, and their diff-summarizing order, is hardcoded for now (there might be 3 to 6 entries here)
        self.difftype_names_in_order = ['generic']
        self.difftrackers = {}
        self.difftrackers['generic'] = GenericDiffTracker()
        #e set up the diff tree itself; do we also store current state or checkpoint name, or not??
        self.weakval_objs = {} ##### SHOULD BE WEAK-VALUED [i think] [when an obj deinits, should we zap its entry in here?? I THINK YES ####@@@@
        pass
    
    def allocate_key(self, obj = None, key = None):
        """Allocate and return a unique key for labelling the state stored by one participating object.
        [Also used (with args None) to allocate keys for other purposes! Not sure if this is a kluge.]
        If obj (presumably that object) is passed, store a weak ref to it from that key,
        accessible via self.obj(key) as long as obj remains alive.
        If key is passed and not None, use that key rather than allocating one (asserting it's not already in use).
        Args are passed positionally.
        """
        if key is None:
            self.lastkey += 1
            key = self.lastkey
            assert not self.weakval_objs.has_key(key), "allocated key %r already in use!" % (key,)
        else:
            assert not self.weakval_objs.has_key(key), "demanded key %r already in use!" % (key,)
        self.weakval_objs[key] = obj # whether or not obj is None!
            # (wisdom of doing this for None is unreviewed. motive: make the above asserts matter then.)
        return key
    
    def obj(self, key):
        "we represent the model, who can return an obj given its key, or make a new one [not in this method??] if it's not alive now... ####???"
        try:
            return self.weakval_objs[key]
        except KeyError:
            # it disappeared! that means it is an empty one... hmm... how do we know its class???
            # it (more generally a constructor for empty state, to which we pass or apply diffs)
            # must be an attr (indexed by key i suppose) of some big container obj...#####@@@@@
            return None #e if this stays like this, rewrite to use .get... but it might not, if we the model know how to find the class...
                # but in general that might depend on info in diffs which was not yet processed, if we just make up this obj as asked for...###
        pass
    
    def consfunc(self, cons):
        "get constructor function from its name (as used internally)"
        modname, cname = cons
        import sys
        module = sys.modules[modname]
        cfunc = getattr(module, cname)
        assert callable(cfunc) # and that it's a class? with right name?
        assert cfunc.__name__ == cname # for now; might not always be true
        return cfunc
    
    def consname(self, cfunc):
        """get constructor name (in private internal format, valid only per-session)
        from constructor func (assuming it's a class, typically defined)
        """
        # the format is a pair, modname, cname
        cname = cfunc.__name__
        modname = cfunc.__module__ ###k probably WRONG (want module name)
        return modname, cname
    
    def recreate_obj_at_key( self, cons, args, kws, key):
        "recreate an object when we're undoing its delete (or redoing its create)"
        consfunc = self.consfunc(cons)
        # assume caller deepcopied args and kws if needed
        kws = dict(kws)
        kws['_um_key'] = key # tell __init__ to pass this key into _um_init
        obj = consfunc(*args, **kws)
        assert obj._um_key == key
        assert obj is self.obj(key)
        return
    
    def delete_obj_at_key(key):
        "delete an object when we're undoing its create (or redoing its delete)"
        obj = self.obj(key)
        assert obj is not None
        assert obj._um_key == key
        self.obj(key)._um_deinit() ####k
        assert obj._um_key == ILLEGAL
        assert self.obj(key) is None ##k not traceback?
        return
    
    def checkpoint(self):
        "... grab diffs from all objects that changed since the last checkpoint ... #doc" # and in the right order re difftype-layer-network...
        
        ### actually we have to do this for each of several flagdicts, one per "type of diff", as registered in a network
        # by the code-layers and class-attrsets. some classes use a different such dict per level of superclass,
        # and the ones that compress diffs into sets (one attr many objs) use their own flagdict,
        # and the ones with special code to worry about types of diffs have their own ordered network... and details are not clear!
        # .. so for now, i'll just hardcode the network rather than set it up by registering.
        # but, i'll try to OO-code it, so the flagdicts are probably in their own objects, which this obj delegates to.
        # and this obj has a dict of those, identified by... what? name of exact class, or some other name chosen by classes?
        # guess: yes.

        # the code layer structure sets up the network, basically by name (uname, in future), with names known to the classes.
        # this network is replicated in every diff-object which gives diffs for a model whose code is organized by those same classes!
        # how does that work... is it set up dynamically each time changes of some kind occur first, when those diffs are current???
        # it might be that the links are not formal, only the difftype names...
        # so we just have a dict from name to difftype-specific-diffobj, which has flagdict, and methods to think about that type of diff.
        # note that its class is the general type of diff, and its instance also knows the specific attr/class names involved.

        #### Should we store those diffobjs in named attrs (following some convention), or in a dict? hmm. guess: a dict. not sure. not at all.
        # pro of attrs: each attr implies special code for the value, and for how they relate, even if this is not yet formalized
        # and if these attrnames are really universal. Note that entire set might itself be in a subobj named by some attr
        # (and implicitly typed by the attrs it contains).

        # Answer to Q above: the network is set up ONCE by the classes, perhaps incrementally as new ones get used,
        # and then it's *also* replicated in each diffobj, but probably only implicitly and in terms of difftype names --
        # the linkages are always the same for all diffobjs and are encoded in this overall object (self) and used each time it runs.
        # Even these diff-collecting objs are PERMANENT, and the using classes can cache their flagdicts in their own init methods.
        
        #e make up a name for this diff? no, caller does that, store some overhead links... might not be needed unless any objs have actual diffs!

        '''
        make up an order to traverse the difftypes as they now stand (if this changed since last time)

        this is a list of names
        for now we can hardcode the list in a nice order
        '''
        alldiffs = {} # or, forward and backward??
        for name in self.difftype_names_in_order:
            tracker = self.difftrackers[name] # a permanent obj for tracking one type of diff our classes know about
            diffs = tracker.checkpoint() # side effect: resets tracker's flagdict for the next cycle of changes
            if diffs: # boolean test for non-empty ok??
                alldiffs[name] = diffs
        if not alldiffs:
            # all diffs are null, no need to do much here (eg no need to name this checkpoint, i think...)
            return
        
        ###e do something with alldiffs ...
        print "got these diffs:", alldiffs
        ops = self.undoredo_from_diffs(alldiffs) # make 1 or more distinct undo/redo ops to store (typically 1 each undo and redo)
            # we handle merging by storing initial ops and then, instead of or when storing new ones, linking them with old ones
            #e but we don't do that yet
        map( self.store_op, ops)
        return

    def store_op(self, op):
        try:
            op.key
        except:
            op.key = self.allocate_key() #e should do in self.op_creator...
        key = op.key
        for varid_ver in op.enough_varid_vers_for_store_indexing():
            dict_of_ops = self.stored_ops.setdefault(varid_ver, {})
            dict_of_ops[ key] = op
        return

    def undoredo_from_diffs(self, alldiffs):
        "make 1 or more distinct undo/redo ops to store (typically 1 each undo and redo) [###e no provision yet for op-merging]"
        # stub version, for only one difftype. ####@@@@
        # for the real multi-difftype version, the hard part is, do we think any atomic ops include more than one difftype? etc
        gendiffs = alldiffs['generic']
        assert len(alldiffs) == 1 # no other kind of diffs is supported here yet
        return gendiffs.make_undoredo_ops() #e if we just looped over difftypes and made sep ops from each, would that be ok? it might be....
    
    #e methods to take a definition of where we are (a set of boundary ops?) and get you some undo or redo candidates...

    def find_undoredos(self, state_version): ### IMPLEM call of this
        """Given state_version, i.e. a dict from obj/attrset-id to valueset-version,
        return a set (list) of all applicable stored undo or redo ops (each labelled as such,
         and containing whatever metainfo will help identify them to the user, as well as diffs)
        which (according to our approximate tests) might possibly validly be applied
        (or partially applied) to state which has that state_version.
        [#e maybe return the ops' names or ids, if we prefer not to hand out promises not to delete them.]
        """
        # terminology: obj/attrset-id == variable
        # implem: each op (which might be compounded from multiple atomic ops, perhaps with its decomposition into them being lazy)
        # is stored on at least one variable/version pair per atomic subop, so that it's only possibly applicable if we find it
        # when scanning all variables in state_version. The way it's stored is as a member of a set at self.stored_ops[varid_ver];
        # that set is the values of a dict so it's fast to remove items from it.
        res = []
        for varid_ver in state_version.iteritems(): # varid_ver is one dict item, i.e. the 2-tuple varid, ver
            ops = self.stored_ops.get(varid_ver, {})
            for op in ops.itervalues():
                if op.applies_to(state_version):
                    res.append(op) #e or op's name or id?
        return res
                
    def destroy(self):
        self.stored_ops = {}
        for dt in self.difftrackers:
            dt.destroy() ###IMPLEM
        self.difftrackers = []
        self.weakval_objs = {}
        #e more?
        return

    pass # end of class UndoArchive

class AssyUndoArchive(UndoArchive): #####@@@@@ rename? use this class; have it define the list of difftrackers, layer actions, etc
    "###doc"
    def __init__(self, *args, **kws):
        UndoArchive.__init__(self, *args, **kws)
        self.__discarded_atoms = {}
        return
    def destroy(self):
        #e safe/good/needed to call discard_unused_atoms???
        self.__discarded_atoms = {}
        UndoArchive.destroy(self)
    def maybe_discard_atom(self, atom):
        "#doc... We don't know yet if some other chunk will want it, so tell model in case no one wants it and it needs deleting."
        self.__discarded_atoms[atom.key] = atom # assume w/o checking that it was not yet in there #k correct?
    def discard_unused_atoms(self):
        #####@@@@@ call this, and make it a non-noop
        "discard any atoms moved out of one chunk and not yet moved into some other one"
        atoms = self.__discarded_atoms
        self.__discarded_atoms = {}
        for atom in atoms.itervalues():
            if atom.molecule is None: #e or _nullMol??
                pass ####e atom.destroy(), zap it from our own dicts, etc; maybe also need to _um_deinit???
        return
    pass # end of class AssyUndoArchive

# ==

class DiffTracker:
    """Abstract class:
    Instances provide a permanent place for one type of before-after diffs to be tracked,
    as objects change in ways that need to contribute to that kind of diffs.
       Each subclass is used for diffs in certain attributes of certain classes,
    and has a specific API for participating objects to report changes,
    and for those objects or their classes to periodically help summarize the accumulated diffs.
       Each subclass provides a checkpoint method, which summarizes accumulated diffs (if any)
    into a separate object ###returned??, and (typically) clears the permanent places herein in which
    objects will continue to report new diffs.
    """
    def __init__(self):
        #e store difftype name? names of prereq difftypes? names of difftype type-conflicts (for noncommutative diffs)???
        pass
    def destroy(self): pass #e override
    pass

class GenericDiffTracker(DiffTracker): # see also GenericDiffTracker_API_Mixin
    """One instance of this class can track all diffs in all generic attrs of all objects
    participating in one UndoArchive, where "generic attrs" are those which need no special
    optimizations for tracking or summarizing their diffs
    (other than whatever common optims this class might someday offer),
    and which have no special worries about kinds of diffs which do or don't commute.
       This object is meant to interact with participating objects via their GenericDiffTracker_API_Mixin superclass,
    which knows this object's private protocol for tracking and summarizing diffs.
    """
    def __init__(self, *args, **kws):
        DiffTracker.__init__(self, *args, **kws)
        self.flagdict = {} # maps keys to objects which changed in the current cycle #doc better
    def checkpoint(self):
        while 1:
            items = self.flagdict.items()
            for key, obj in items:
                # pass 1 -- make sure the ones that should no longer exist know this
                obj._um_check_existence() # this might store them again into flagdict, so don't clear it until we're done
            if len(self.flagdict) > len(items):
                print "possible undo bug: more objs changed due to some realizing they don't exist" #k but it might be ok re this code
                #e should print the new objs too
                continue
            else:
                assert len(self.flagdict) == len(items)
                break # we reached a fixed point in the set of changed objs (should usually or always happen w/o any repeats of loop)
            pass
        if not items:
            return None # optim
        self.flagdict.clear()
            # don't do flagdict = {} -- we want to permit participants to store a direct ref to self.flagdict.
        
        # Make places for objects to store their diff-summaries. In each place, they store them per-object-key
        # (maybe this means per-object or per-varid?)
        # and then (however they wish, but typically) per-attribute.
        #
        # We have one place for each combination of stage (create, change, delete -- or more, if we had more layers)
        # and direction (forwards, backwards), plus places for old and new version-values of varids.
        #
        # We don't formally correlate the things stored in these places (indexed by keys in diff places vs varids in version places),
        # which means that if this isn't an atomic change and we later want to undo/redo part of it but keep track of how
        # that relates to the whole (so we can offer to "redo the rest", etc), which requires varids per atomic change,
        # then at that time, we'll need to re-analyze the changes so we can split this into smaller diff-holder objects
        # which correspond to atomic attr changes with their own varid-version changes. (This might be NIM in initial implem.)
        #
        # [#e Note that in the future, either backwards or forwards diffs, or both, might be optional,
        #  since pure undo could be done with backwards diffs only (generating redo diffs when undo diffs were traversed),
        #  and pure change-archiving could be done with forwards diffs only. So the API we call lets any of these dicts be None.]
        #
        # We make the objects create their own entries (even though they should only do this at their keys)
        # in case some object owns more than one key.
        oldver = {}
        create_f = {} #k assuming we need forwards diffs
        ## create_b = {}
        change_f = {}
        change_b = {}
        ## delete_f = {}
        delete_b = {}
        newver = {}
        diffargs = (oldver, create_f, change_f, change_b, delete_b, newver) # sequence of refs to mutable objects
        for key, obj in items:
            # this obj thinks it might have changed -- ask it to store actual diffs and prep for next checkpoint
            # (it stores them, if any, at its _um_key(??) in the dicts we pass as args)
            #####@@@@@ does it also store the most recent checkpoint before these diffs? if so, it had to ask us when they started...
            # but can this vary per-obj?? i'd guess it can't. hmm. so, it can ignore this, since we ought to know it. ###@@@
            obj._undo_checkpoint( diffargs ) # (this api is specific to this kind of difftracker)
        if self.flagdict:
            from debug import print_compact_stack
            print_compact_stack( "bug? something changed while being asked for its diffs: flagdict = %r: " % (self.flagdict,) )
        if not (create_f or change_f or change_b or delete_b):
            # all diffs are null, no need to do much [if not for an optim, this would also happen if flagdict was empty]
            assert not oldver and not newver ##k ??
            return None # any boolean false value should be ok here, AFAIK
        
        #e refile? or does even generic one do some of this:
        #obs?
        #e compress the diffs, if some of them are about attrs to be stored as arrays... or should objs themselves do that??
        # (objs already did per-obj compression, eg using diffs for attrvals themselves, but probably not inter-obj compression.
        #  alg: visualize as optimizing a bitmap into rects of solid black which cover it. goals: human summary, storage space.
        #  classify objs by set-of-changed-attrs, then for rare such sets, if a superset is more common, upgrade if cheaper
        #  by pretending more attrs changed. otherwise make an array of structs just for those objs with that set of changed attrs,
        #  stored as a struct of arrays, one containing obj-indices. *or* put some attrs into bigger obj-sets....)
        # note: right now they are per-obj and then per-attr. if we compress only when lots, then now, just count objs...
        #e package up the diffs with the before and after checkpoint names, and tell every involved node about this oprun...
        #e also merge them into one undoable-op (several sequential diffs) and/or store flags to permit later merge

        return GenericDiffHolder( diffargs)

    def destroy(self):
        pass # repeated calls ok; no bugs > no mem leaks; can be and should be called from __del__
    pass

class AtomChunkPos_DiffTracker(DiffTracker): ##e needs own mixin? or just hardcode its methods in atom and chunk, using a prefix?
    "Track changes in atom existence and chunk membership, atom position (relative to chunk??), chunk position."
    def __init__(self, *args, **kws):
        DiffTracker.__init__(self, *args, **kws)
        self.flagdict = {} # maps keys to objects which changed in the current cycle #doc better... ###e replace with several dicts
    pass ###e

# ==

class DiffHolder:
    pass

class GenericDiffHolder(DiffHolder):
    def __init__(self, diffargs):
        """diffargs contains:
        ###obs: 6 dicts from obj._um_key to descriptions of forwards/backwards create/change/destroy instructions,
        in the order create_f, create_b, change_f, change_b, delete_f, delete_b.
        Change descriptions are dicts from attrname to attrval, for before and after vals respectively for _b and _f.
        Create_f and delete_b contain object creation instructions (basically classes and initargs?? ###@@@).
        Delete_f and create_b values are just True, to say that the object (of the given key) should be deleted.
        [So they are redundant since the set of keys in the creation info could be used. ###@@@]
        """
        oldver, create_f, change_f, change_b, delete_b, newver = self.diffargs = diffargs
        self.backwards = change_b # synonyms #e clean that up
        self.forwards = change_f
        diffargs_rev = list(diffargs)
        diffargs_rev.reverse()
        self.diffargs_rev = tuple(diffargs_rev) # diffargs as seen from the other direction
        return
    def facet_diffargs(facet):
        if facet == FORWARDS:####implem, rename
            return self.diffargs
        else:
            return self.diffargs_rev
    def __repr__(self):
        return "GenericDiffHolder( backwards = %r, forwards = %r, etc )" % (self.backwards, self.forwards)
    def make_undoredo_ops(self): ####@@@@ revise to use facets;
            #####@@@@@ not sure why this occurs at this level instead of a higher one
            # that covers all layers/difftypes... also, i recall a need for the difftype variation to be in the changes... hmm
            # to resolve that we might need to understand how we do atomposns for chunks, with its own difftypes; also bonds, need atoms.
            # (btw if atomposnslots in chunks are their own type, then do atoms need those like bonds need atoms? or vice versa???)
        "return a sequence of ops (to be offered/stored/merged separately; need not be atomic) made from self"
        #e ignore the issue of whether some of them are co-atomic with ones coming out of other difftypes that co-occurred with this
        return DiffOp( 'Undo', self.backwards, self ), DiffOp( 'Redo', self.forwards, self )
    def _f_apply_diff(self, facet, model): # helper for our ops
        "apply one of our diffs to a model (which can map keys to objects)" ###k i guess it can map keys
        oldver, create_f, change_f, change_b, delete_b, newver = self.facet_diffargs(facet)
        # check oldver
        nim
        # create objects if needed
        for key, (cons, args, kws) in create_f.items():
##            cons = model.cons(cons) ###IMPLEM
            # args should not need mapping, should be pure data;
            # copy them to avoid sharing, which also verifies they're pure data
            args = copy_val(args)
            kws = copy_val(kws)
##            kws['_um_key'] = key # use this key to create the object... what if it's taken? it can't be, they're session-unique.
##                # hmm, maybe that should already be in kws? prob not.
            model.recreate_obj_at_key( cons, args, kws, key ) ###IMPLEM
        # apply changes
        for key, objdiff in change_f.items():
            obj = model.obj(key)
            assert obj is not None
            ####@@@@ can this also destroy obj? 
            assert not objdiff.has_key('_um_exists'), "object create/destroy is nim in apply_diff" #####@@@@@ IMPLEM
            obj._undo_apply_diff(objdiff) #e will it need to know the direction, the related version numbers (maybe in the diff itself), etc?
        #e also does obj want a pass2 to happen later? or do we scan and call their update methods later? ##e
        # delete objects if needed
        for key in delete_b.keys():
            model.delete_obj_at_key( key) ###IMPLEM
        # set newver
        nim
        return # retval useful? like how much we actually did?
        ###e what do we do about the diffs generated by that op, vers to store...
    def _f_all_varid_vers(self, facet, diff):
        """Given one of our diffs, return all the varid_ver pairs it affects,
        including in them the "before" state of vers. ###e fix doc
        """
        oldver, create_f, change_f, change_b, delete_b, newver = self.facet_diffargs(facet)
        return oldver.items()
        ###obs: LOGICBUG: to properly apply a diff you need the after vers, but to decide whether you can apply it you need the before vers,
        # so in storing a diffpair, you ought to store a SQUARE of before forward after backward, ie 4 objects, used in various sqside combos...
        # rather than storing the vers inside the diffs... and maybe the diffs that we pass around need to all ref the entire square
        # (ie us) from different sides? or just get permuted by various ops? how best to package it is unclear. #####@@@@@
    pass

# ==

class DiffOp:
    _all_varid_vers = None
    def __init__(self, kind, diff_to_apply, diffholder):
        self.kind = kind # 'Undo' or 'Redo'
        self.diff_to_apply = diff_to_apply
        self.diffholder = diffholder
        ## done by client code for now: self.key = nim
        return
    def enough_varid_vers_for_store_indexing(self):
        """Return a sequence of varid_ver pairs on which this op should be indexed,
        so that it's found by searching the ones in any state it might apply to.
        (This means we need to include at least one varid_ver pair for each atomic subset
        of the primitive diffs we're made of.)
        [Present implem is not sure about what's atomic so it just returns all the varid_ver pairs.
        THIS MIGHT CAUSE BAD INEFFICIENCY IF SOME OF THOSE PAIRS ARE "POPULAR" since the varids rarely change...
        but how can that be, if they changed in this op? hmm... maybe it's ok... we'll have to see. ###k]
        """
        return self.all_varid_vers()
    def all_varid_vers(self):
        if None is self._all_varid_vers:
            self._all_varid_vers = self._compute_all_varid_vers()
        return self._all_varid_vers
    def _compute_all_varid_vers(self):
        return self.diffholder.all_varid_vers( self.diff_to_apply)
            ####@@@@ all these would be simpler if diff_to_apply was a sideview of diffholder - then we'd only need that view, only 1 init arg
    def applies_to(self, state_version):
        "say whether this op applies to state_version, based only on a match of their ver for each affected varid"
        ## should we let dh do it? like this? return self.diffholder.xxx( self.diff_to_apply)
        # or should we just do it ourselves like this: (yes, for now, until i find a case where dh can and wants to optim it)
        for varid, ver in self.all_varid_vers():
            #e possible optim: know min and max and rare vers that appear in self and in state_version, use to rule out most matches
            if state_version.get(varid) != ver:
                return False # state_version has different ver or no ver.
                    #e some callers might like to find out a varid that didn't match...
                    #e since they could use it to optimize "apply all these diffs in some order that works".
        return True
    def doit(self, model):
        return self.diffholder.apply_diff( self.diff_to_apply, model )
    def what(self):
        "return the text describing the operation we can undo or redo, for a menu item"
        return "to checkpoint" #e stub; will describe from diffs and/or from the user command that caused them, and include history sernos
    def destroy(self):#e call
        #e also remove self from external stores indexed by self.key?? prob not needed -- caller will also clear out those stores,
        # or remove us when it sees we're too old and not recently used.
        # (or let their ref to us be weakvalued? no, then nothing would strongref us!)
        self.diff_to_apply = self.diffholder = None # break cycles
    pass

# end
