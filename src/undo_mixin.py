# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
undo_mixin.py

Provide a mixin class, and related tools, to help state-storing objects work with an UndoArchive
(so that some changes to their state can be undone/redone), specifically by recording their
changes in it and providing methods to apply diffs it has recorded.

$Id$
'''
__author__ = 'bruce'


import state_utils

class StateMixin:
    """Mixin for classes with standard state-related attribute declarations.
    Provides helper methods which make use of those decls.
       Naming conventions:
    State-related decls and methods can start with _s_ and be named like s_whatever_<attrname>
    (for <attrname> not allowed to start with '_')
    unless they're so basic they needn't start with anything special, like _type_<attrname>.
       Standard attributes:
    _type_<attrname> = <typecode> # default is "guess from runtime value"
    _mutable_<attrname> = <bool> # whether we should ever worry that values of this attr might need copying since they're mutable
        # default for this comes from type declaration; conservative default is True ###@@@ do that for undoable attrs
    """
    def _s_init(self):
        #e might be called more than once, unless we switch to new-style classes (inherit from object) and use super syntax
        #e (and if we do, maybe this should be renamed __init__)
        # find all _s_ and _type_ attrs and compile useful info about them
        self._s_equalfunc_dict = {} #k not yet used
        if not self.__class__.__dict__.has_key('_s_mutable_attrs'):
            self.__class__._s_mutable_attrs = tuple( filter( self._s_attr_decl_is_mutable, dir(self.__class__)) )
    def _s_attr_decl_is_mutable(self, attr):
        if attr.startswith('_'):
            return False
        ## return True ###stub, but should be ok since it's conservative -- but it's not since we applied it to dir(class)!
        return False ###stub, WRONG #####@@@@@
    def _s_equalfunc(self, attr):
        "return a func which takes two values for attr and returns true iff they're equivalent state"
        ### should look at type decl of attr
        return lambda x,y: x == y
            # this is wrong for some kinds of class-object-valued attrs, which need 'is';
            # but it might be right for enough to get by for now
    def _s_copyfunc(self, attr):
        """return a func which takes a value for attr and returns a copy of it
        which shares no mutable components with original;
        ##e depending on attr's decl, specific kinds of python objects in copy might be
        copied, refs to orig, wrapped, etc... #doc
        """
        return state_utils.copy_val # conservative; but doesn't yet work if val contains python objects like Atom, Bond, Node, Part
        ## return lambda val: val ### stub!!! WRONG
    pass

_ILLEGAL_UM_KEY = "_ILLEGAL_UM_KEY" # must not be a legitimate value of _um_key; type doesn't matter provided it's ok as a dict key

class GenericDiffTracker_API_Mixin(StateMixin): ### docstring needs revision, names need cleanup - details in docstring #####@@@@@
    """Mixin to help classes handle their undoable state using the Undo Protocol.
    We handle the undo-prep protocol for the attrs stored in self._um_undoable_attrs; [###@@@ actually nothing uses that value yet!]
    value unsharing code for attrs in XXX or with decl
    _um_xxx means GenericDiffTracker_API_Mixin-specific method or attr;
    _undo_xxx means part of the Undo protocol (which this mixin helps you meet, but it's not the only way).

    ###doc needs revision, names need cleanup; the idea is that for one object with several kinds of attrs handled differently,
    it sort of pretends to be more objs, each using own difftracker api, but this mixin is for the generic attrs
    that can be handled by GenericDiffTracker's API... not sure if this mixin has anything to do with any other protocol
    like an "Undo Protocol". not sure of its fate when asked to apply diffs, if same obj has other difftypes too...
    I suppose we need another level which takes a diff dict mapping difftype names to difftype-specific diffs
    and to pass out the parts (in the right order) to difftype-specific mixins....
    #####@@@@@
    """
    _um_key = _ILLEGAL_UM_KEY # default key for possible use before _um_init gets called
    _um_flagdict = _um_preinit_flagdict = {} # a shared "garbage dict" for catching changes tracked before _um_init gets called
    _um_oldval_cache = _um_preinit_oldval_cache = {} # ditto
    _um_exists = False
    _um_deinited = False
    # methods to be overridden in subclasses
    def _um_undoable_attrs(self):
        """Return a sequence of attribute names in self whose changes should be undone by GenericDiffTracker_API_Mixin
        (not including names used internally by the mixin class, such as _um_exists).
        The returned value should not change over the lifetime of this object, but it can depend on args passed to __init__
        provided those args are fully processed before __init__ calls _um_init (since _um_init calls this method).
        The treatment of specific attrs can be modified by per-attr declarations (see the mixin class for details).
        """
        return ()
    def _um_existence_permitted(self):
        """[subclasses should override this as needed]
        Return True iff it looks like we should be considered to exist in self._um_archive's model of undoable state.
        Returning False does not imply anything's wrong, or that we should be or should have been killed/destroyed/deleted/etc --
        just that changes in us should be invisible to Undo.
        """
        return True
    def _um_changed(self):
        """[subclasses should override this as needed]
        Do whatever updates are needed after some or all our (self's) undoable state was changed
        by direct calls to setattr (done immediately before calling this method).
        You may assume that self was not created or deleted in the diff that was just applied,
        i.e. that self._um_exists was True and remains True.
        """
        # noop method in case class doesn't need this
        pass
    def _um_cons_args_kws_defaults(self): # only _um_fixed_cons_args_kws_defaults should call this directly 
        """#doc - explain this better, put it in context:
        [Most subclasses must override this method.]
        Return a tuple of:
        constructor function (which must be a class in some module, which inherits this mixin -- usually self.__class__),
        initargs and kws for constructor (optionally tuned to current attrvals) (needn't be copied, caller does that),
        and the "default" attrvals (for undoable attrs) that will result from using that constructor on those initargs.
        The initargs should do enough that ordinary attrval-diffs from defaults to current attrvals will be sufficient
        to finish reconstructing an object like self in its current state, but neither initargs nor defaults are allowed
        to contain refs to other objects (so any current attrvals which do, will end up being set separately, as changes).
        """
        #####@@@@@ related Q: init allocs wrong key, how do we fix that when reconstructing? with an initarg _um_key?
        consfunc = self.__class__
        initargs = []
        initkws = {} # these don't include _um_key; by the time this gets recreated, it might be different (tho prob not for now)
        defaults = self._um_default_values_dict
        return consfunc, initargs, initkws, defaults
    def _um_fixed_cons_args_kws_defaults(self):
        "properly encoded/copied/verified version of _um_cons_args_kws_defaults [not usually overridden]"
        # we copy initargs, initkws, defaults, to unshare and ensure no objs
        consfunc, args, kws, dflts = self._um_cons_args_kws_defaults() # typically overridden by client code
        archive = self._um_archive
        copy = archive.copy_val
        return archive.consname(consfunc), copy(args), copy(kws), copy(dflts)
    # init and deinit methods
    def _um_init(self, archive, key): # this implies we know archive when we create object. is that reasonable? yes, it seems to be.
        "This should be called sometime during the caller's __init__ method. [#doc when, if it matters]"
        assert not self._um_deinited, "reinit of deinited undoable object is not allowed: %r" % self
        self._um_archive = archive
        self._um_key = archive.allocate_key(self, key)
            # allocate a unique key from the undo-archive we'll be using to store old state and diffs;
            # and (since we pass self) store in the archive a weak ref to self from that key;
            # or if provided key is not None, use that (after asserting it's not already in use).
        self._s_init() #e should use super syntax if we decide this can inherit from object
        self._um_flagdict = archive.difftrackers['generic'].flagdict
        self._um_preinit_flagdict.clear() # discard anything tracked before _um_init was called
        self._um_oldval_cache = {} # hold old vals of attrs that get replaced;
            # attrs with mutable vals have to be handled separately -- copied right from the start into here, unshared copy
        self._um_preinit_oldval_cache.clear()
        # compile some helper lists based on attr decls, of attrs to handle specially
        self._um_mutable_attrs = self._s_mutable_attrs ### stub, should reduce this to only include the ones meant for undo...
        self._um_init_default_values_dict()
        self._um_oldval_cache.update(self._um_default_values_dict) # at next checkpoint, always compare all attrs to defaults
            ###k that might still be good to prevent redundant change-flagging, but values might not matter since stored again later,
            # perhaps differently if they can be coded as init_args
##        self._um_prepare_for_changes()
##            # This is only correct if we're called early enough in __init__
##            # that the current values of *all* attributes (those we store in oldval cache, or others)
##            # are equal to constant class-specific default values (as opposed to something that varies per-instance) --
##            # presumably those would be either class attributes, or constants always set in __init__ before this call --
##            # *and* if those constant values can be reconstructed by creating a new "empty" object (meant for applying diffs to).
##            # That way, any difference in those attr values from those predictable constants will be tracked in the usual way,
##            # even if it occurs from a set or other change later in __init__ (after we return).
##            # [#k This scheme needs to be reviewed once the set of participating attrs is known.]
##            ######@@@@@
##            # ... need to revise this anyway, since we need access to the default values when we're destroyed,
##            # so we might as well access them now and not make so many assumptions about the situation when _um_init is called.
        self._um_set_exists(True) # record our creation as a change [kluge??]
        # note: we don't call _um_check_existence until the next checkpoint, since it might return False before __init__ is done.
        return
    def _um_init_default_values_dict(self):
        ###obs comments:
        ### we need a class-specific (*not* allowed to vary on self) dict of all default values of undoable attrs
        ### actually it can vary depending on initargs, under some conditions (doc'd eleswhere)
        ### but it would be more efficient to prohibit that, so not every instance had to recompute this!
        self._um_default_values_dict = {}
        for attr in self._um_undoable_attrs():
            try:
                dflt = getattr(self.__class__, attr)
            except AttributeError:
                #e print warning, but only once per class?
                try:
                    dflt = getattr(self, attr) ### WRONG, but we need to figure out what to do then - decl, always define on class, ...
                except:
                    print "bug, fatal: exception (traceback follows) looking for default value for attr %r of class %r" % \
                          (attr, self.__class__.__name__)
                    raise
            self._um_default_values_dict[attr] = dflt
        self._um_default_values_dict['_um_exists'] = False        
    def _um_deinit(self):
        """call this when self is deleted wrt the undoable-state model;
        not calling it might cause errors;
        calling it more than once is ok (in same or different checkpoint cycles).
        """
        if not self._um_deinited:
            self._um_set_exists(False) # record our deletion as a change
            # can't mess with _um_key or flagdict(??), since they might be needed during the next checkpoint call
            self._um_deinited = True # prevents reinit
        return
    def _um_check_existence(self):
        "if we should not still exist (for purposes of visibility to undo), but do, correct this situation."
        if not self._um_deinited:
            assert self._um_exists, "bug: _um_check_existence must have been called too early" # can't happen, AFAIK
            if not self._um_existence_permitted():
                self._um_deinit()
        if self._um_deinited: # (note: this might have just now become true during then-clause of above if-statement)
            assert not self._um_exists
            if self._um_existence_permitted():
                print "warning: we don't exist, but could. hmm. possible bug. or maybe not.", self # remove when works #####@@@@@
        return
    def _um_set_exists(self, exists):
        # kluge for dealing with created and destroyed objects ####@@@@ incomplete
        self._um_will_change_attr('_um_exists') 
        self._um_exists = exists # when false, pretend all attrs have or had their default value, for purpose of diffing them ###doit
    def _um_will_change_attr(self, attr): ####@@@@ call this for more attrs!
        "example code - typical clients inline this, maybe so do our own methods"
        #k should we slow down by checking self._um_exists? (might be incorrect when that attr is set!) #k or self._um_deinited?
        self._um_oldval_cache.setdefault(attr, getattr(self,attr))
            ### can this happen during init, when old attr not present?
            ### require attr always present, using class default or __getattr__??
        self._um_flag_me_as_changing()
        #e might optimize by having a per-attr flag for whether it changed yet
    def _um_flag_me_as_changing(self):
        "example code, typically inlined"
        self._um_flagdict[ self._um_key] = self # some objs might store a proxy or helper-obj in here...
        return
    def _undo_checkpoint(self, diffargs): ##, snap = None
        """[undo protocol:] ###doc...
        we reached a checkpoint and you (self) flagged yourself as maybe having changed;
        please return XXX or store in the args YYY...
"we see you flagged yourself as having changed one or more times recently...
ok, there's a checkpoint now (whose name you need not know), and we're asking you to tell us:
- your diffs since then, forwards (for change-record)
- your backwards diffs from now back to then (for undo) [the only one we *have* to ask, btw]
- (and we might sometimes ask for a full current copy of your state, in public format)
and then to flush your internal diff-cache until we ask again."
        store this stuff into the args using your key. (if it's null, store nothing.) (for args not supplied, store nothing.)
        """
        # don't do self._um_check_existence() -- caller has just done that
        oldval_cache = self._um_oldval_cache
        exists = self._um_exists
        existed = oldval_cache.get('_um_exists', exists) # (but leave it in oldval_cache if it changed)
        if not (existed or exists):
            # This happens if we got created and deleted in one cycle, or got change-tracked while not officially existing.
            # Either way, no diffs need to be recorded for us or our attrs.
            # Returning this early is just an optimization, but it might simplify the remaining code.
            return
        oldver, create_f, change_f, change_b, delete_b, newver = diffargs # oldver, newver might not be used for now -- not sure###@@@
        forwards = change_f # synonyms deemed more readable
        backwards = change_b
        key = self._um_key # index of whatever we store into the diff dicts
        assert key != _ILLEGAL_UM_KEY #k not sure if this is guaranteed! if not, then just silently return if it fails.
        defaults_for_create = self._um_default_values_dict #e in principle, this might differ for create and destroy, and for each use
        # deletion diffs, including deletion-kluge for change diffs
        if existed and not exists:
            # We got deleted! For forward diffs, it's enough to store that fact,
            # but backwards diffs need to know how to recreate us (in case this delete is undone).
            #  We split that re-creation into constructor and args, plus additional changes if necessary.
            # Whether to store each current attrval in constructor args or as a "pre-delete change of this attr to its default value"
            # is somewhat arbitrary, but in case attrvals point to objects which would be recreated in parallel,
            # we can't assume those attrvals can be set during the creation stage, only (via a mapping) during the change stage.
            # On the other hand, some objects might have properties unsettable after init;
            # this is up to the constructor-and-args chooser for the client class.
            cons, args, kws, defaults_for_delete = self._um_fixed_cons_args_kws_defaults()
                # get constructor and args for approximating current state, which set attrs to defaults_for_delete,
                # which we'll correct using further changes.
            delete_b[key] = (cons, args, kws) ####@@@@ format?
            # we'll pretend in our diffs that all our attrs changed to those default values, before the delete.
            # But we don't dare to really change them, and the ones that didn't really change weren't change-tracked,
            # so we have to fake that here.
            for attr in defaults_for_delete.keys():
                # if attr didn't change yet, set oldval to true current value
                # (to be compared later to default val == pretend current val)
                if not oldval_cache.has_key(attr):
                    oldval_cache[attr] = getattr(self,attr)
                # (don't do oldval_cache.setdefault(attr, getattr(self,attr)), 
                #  so as to avoid getattr at this late stage unless its really needed;
                #  reason is that dying objects might do unwanted recomputes by getattr;
                #  reason it might help is that some attrs are declared to always be in oldval_cache.)
        # creation diffs
        if exists and not existed:
            # This is similar to the deletion case...
            ###@@@ change to code: _um_init need only flag us... or did it need to set oldvals? maybe to prevent recording only...
            cons, args, kws, defaults_for_create = self._um_fixed_cons_args_kws_defaults()
            create_f[key] = (cons, args, kws)
            oldval_cache.clear()
            oldval_cache.update( defaults_for_create) ###@@@
        # change-diffs (for whichever attrs are recorded in oldval_cache, and actually changed)
        items = oldval_cache.items()
        oldval_cache.clear()
        for attr, oldval in items: # note: this includes attrs we want to diff every time, since their oldval was stored.
            # If an attr and its oldval is stored here, that means one of several things:
            # - self got created since last checkpoint; oldval is default value for attr.
            # - this attr isn't being changedtracked, so we always have to diff it. if it's mutable, oldval is a copy sharing no state.
            # - this attr actually changed (one or more times), or at least some code thinks it might have changed.
            #   (that might mean it got reassigned, or if it's mutable, it might just mean it got modified.)
            # Not all mutable attrs need to be stored here, if client is sure it'll warn us (via _um_will_change_attr)
            # before the attr value is either modified or reassigned. (If it only warns us afterwards, that's pretty useless --
            # they'd need to be pre-stored here even if they're not mutable. So we have no provisions for beig warned afterwards.)
            #
            # See if value is now different (whether that is due to it being modified or reassigned or both; we can't tell).
            equals = self._s_equalfunc(attr) # from StateMixin
            if not exists:
                newval = defaults_for_delete[attr] # on deletion, pretend attr gets reset to default (as explained above)
            else:
                newval = getattr(self, attr)
            if not equals(oldval, newval):
                assert not (not existed and not exists) # no diffs are possible here for objects created and destroyed in one cycle
                # Record this diff (perhaps in both directions).
                # For objects just created, no need to record backwards diffs (except for attr _um_exists itself).
                # For objects just destroyed, no need to record forwards diffs (except for _um_exists).
                # For objects created and destroyed in the same cycle, this implies no diffs will be recorded (see assert below).
                if backwards is not None: # caller wants backwards diffs (always true for now)
                    if existed or attr == '_um_exists':
                        diffs = backwards.setdefault(key, {})
                        diffs[attr] = oldval
                if forwards is not None: # caller wants forwards diffs (warning: value might be {}, so don't use a boolean test!)
                    if exists or attr == '_um_exists':
                        diffs = forwards.setdefault(key, {})
                        diffs[attr] = newval
            continue
        if not existed and not exists:
            # This happens for objects that got changed even though they officially don't exist,
            # or for objects that got created and destroyed within the same inter-checkpoint cycle.
            # The code above should never record diffs for them -- not even for the attr _um_exists,
            # since it didn't change overall -- it was False at start and end of the cycle.
            assert not backwards or not backwards.has_key(key)
            assert not forwards or not forwards.has_key(key)
##        if snap is not None: # or could require use of a sep func for this...
##            assert 0, "snap nim"
        # now clear our state and prepare to capture future changes 
        assert not oldval_cache, "bug: summarizing diffs caused new oldvals to be tracked in %r: %r" % (self, oldval_cache)
        if exists:
            self._um_prepare_for_changes()
        # deletion diffs -- know how to recreate self (with default attrvals) if deletion is undone
        
            
        nim ####@@@@
        return # from _undo_checkpoint
    def _um_prepare_for_changes(self): #######@@@@@@@ set up for attrs which won't be change-tracked, mutable or not
        """Prepare to capture more changes, when self is first created[WRONG###] or just after it's checkpointed.
           This requires storing current values (in oldval_cache) of attributes that won't be change-tracked,
        or whose values are themselves mutable (for speed, this is guessed by declarations rather than tested).
           If any attrs won't be change-tracked (which might or might not include mutable-valued attrs, since in principle
        they can be reliably tracked even though they might change without being assigned to), we also ensure our
        checkpoint method gets called at the next checkpoint, so we can check all such attrs for diffs.
           Otherwise, our checkpoint method only gets called if we tracked a change in some attr.
        ###doc the needs for init, or to 
        """
        #####@@@@@ flag self if any attrs might not be tracked. assume this for mutable ones (or, all?) unless declared otherwise.
        oldval_cache = self._um_oldval_cache
        assert oldval_cache == {}
        ###e deal with mutable-val attrs... to be safe, should we test this at runtime? not sure....
        ###e we'd need copier routine for each one or each type....
        for attr in self._um_mutable_attrs:
            ###e also include the ones we prefer to diff every time, rather than tracking them for changes?
            # problem: including them is not enough unless we also put ourselves into the flagdict every time! (so do that here)
            curval = getattr(self, attr)
            try:
                curval = self._s_copyfunc(attr)(curval)
            except:
                print "error for attr = %r" % (attr,)
                raise
            oldval_cache[attr] = curval
        return
    def _undo_apply_backward_diff(self, diff):
        """diff is what we stored at key in a backwards-diff dict. apply it to our current state,
        assuming without checking that it was a backwards diff from that very state (or at least that this is sure to be legal).
        PRESENT IMPLEM ASSUMES _um_exists is True and remains True! (Ie it doesn't handle object creation/deletion)
        """
        assert self._um_exists
        for attr, val in diff:
            setattr(self, attr, val)
            # note that this setattr might well trigger properties that set undo-flags due to this change!
            #e we might optim (in some client classes) by using self.__dict__.update(diff) and other code to record changes....
        assert self._um_exists
        self._um_changed()
    _undo_apply_forward_diff = _undo_apply_backward_diff ## dangerous if subclass intends to override _undo_apply_backward_diff alone!
    _undo_apply_diff = _undo_apply_backward_diff #k maybe it doesn't need the direction, or prefers to get it inside an arg...
    pass

# end
