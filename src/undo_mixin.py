# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
undo_mixin.py

Provide a mixin class, and related tools, to help state-storing objects work with an UndoArchive
(so that some changes to their state can be undone/redone), specifically by recording their
changes in it and providing methods to apply diffs it has recorded.

$Id$
'''
__author__ = 'bruce'


import state_utils

class StateMixin: ####@@@@ might be obs and/or WRONG [051013]
    # note: see also _s_deepcopy, defined on some data-like classes, which this is *not* [bruce 060209 comment]
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

# Note: as of 060208 UndoStateMixin is (and has for a long time) been mixed into
# the classes Atom, Bond, Node, Part, and assembly.
# Those classes, plus VQT, modes, and maybe movie, and some classes used in movie and mode attrvals,
# will be the ones scanned for undoable state. Any of those defining __getattr__, or having attrs that
# should not be scanned normally, will need some sort of mixin or other customization for Undo.
# We'll define those mixins here. Right now there's only one, but that's likely to change.

# There is a def __eq__ and def __ne__ in Bond, ####k ok with this, delete it
# and def __getattr__ in these eq_id classes: GLPane ###k, ThumbView, and some of the classes with UndoStateMixin,
# [and some class in py files named] modelTree (?), modes(?), movie(?)
# and these _eq_data_ classes: VQT, Selection (is this really datalike? probably yes ##e).
# I also had to check anything with InvalMixin (Atom, molecule, Part) -- all covered above.

# classes whose mixin/attr policy is not yet clear:   ###@@@ THIS IS WHERE I AM 060209 514p
# VQT, GLPane, ThumbView, anyMode, assembly, part,
# movie, its subobjects like atomlist or whatever and moviefile
# Selection
# (would be nice to "debugwarn but handle" these, when python objects, by using __dict__) 



# what do classes mix in, to tell us how to treat them if we encounter them in an undo checkpoint scan?
# - if they are containers of state, name is id, then one mixin, StateContainerMixin (more or less like the StateMixin prototype, above)
# - if they are like data, defining __eq__, then StateDataMixin (maybe)
# - if they are proxy for container of state, StateProxyMixin (maybe) (no examples yet, but there might be when UI is customizable)s

# For efficiency, any objects with __getattr__ and residing in undoable-state attribute values
# should inherit _getattr_efficient_eq_mixin_ , including those mixing in this class, and more.

class UndoStateMixin( StateMixin, state_utils._eq_id_mixin_ ):
    # like StateContainerMixin (renaming of StateMixin???) but specifically for Undo
    #bruce 060209 renamed this UndoStateMixin from GenericDiffTracker_API_Mixin (but new name is tentative)
    ### docstring needs revision, names need cleanup - details in docstring #####@@@@@
    """[obsolete docstring]
    Mixin to help classes handle their undoable state using the Undo Protocol.
    We handle the undo-prep protocol for the attrs stored in self._um_undoable_attrs; [###@@@ actually nothing uses that value yet!]
    value unsharing code for attrs in XXX or with decl
    _um_xxx means UndoStateMixin-specific method or attr;
    _undo_xxx means part of the Undo protocol (which this mixin helps you meet, but it's not the only way).

    ###doc needs revision, names need cleanup; the idea is that for one object with several kinds of attrs handled differently,
    it sort of pretends to be more objs, each using own difftracker api, but this mixin is for the generic attrs
    that can be handled by GenericDiffTracker's API... not sure if this mixin has anything to do with any other protocol
    like an "Undo Protocol". not sure of its fate when asked to apply diffs, if same obj has other difftypes too...
    I suppose we need another level which takes a diff dict mapping difftype names to difftype-specific diffs
    and to pass out the parts (in the right order) to difftype-specific mixins....
    #####@@@@@
    """
    
    # OLD STUFF after this point -- mostly obs at the moment, but some or most of it might be revived
    # for change-tracking [bruce 060209 comment]  
    _um_key = _ILLEGAL_UM_KEY # default key for possible use before _um_init gets called ###@@@ no, _um_set_key ??
    _um_flagdict = _um_preinit_flagdict = {} # a shared "garbage dict" for catching changes tracked before our first checkpoint (#k??)
## was: before _um_init gets called
    _um_oldval_cache = _um_preinit_oldval_cache = {} # ditto
    ###@@@ WRONG:
    _um_exists = False
    _um_deinited = False
    # config constants to be overridden in subclasses
    _um_changetracked_attrs = () #####@@@@@ use _um_changetracked_attrs
        # for these attrs, client object promises to track changes by hand, so copying/diffing values is not always needed
    # methods to be overridden in subclasses
    def _um_undoable_attrs(self):
        ####@@@@@ 060209: must decide whether the default is () or __dict__.keys(), or if this only feeds in to answer;
        # note that subclasses like to say "return superclass.attr_for_use_by_this + (more,guys,)", so it's nice if default FOR ATTR is ()...
        # the other day i was thinking it's more like we'd want to take them out of dict keys, than add them in..
        # can we start with a list, take out any that have dfltval on class but are nt in list,then add in any in dict?
        # thatis, figure you're listing "the ones to include of the ones defined on class", not "of the ones in init"... dangerous
        # since otherwise it doesn't matter if you move a dflt assignment from class to init.
        # ... maybe we declare the ins and the outs both, and others use per-class dflt policy,
        # which might be "treat as in (or out), but debug-warn". *OR*, a special name meaning "this is default policy" could be put in
        # one or the other list, or not. e.g. '$other' ?
        # ... do we want each of several mixin classes to inherit from this and contribute their own lists of in and out attrs for scanning?
        # if so, they need to use __um_xxx methods/attrs to do that... which is possible... case in point: GLPane and modeMixin.
        # For now, if that's the only case, save the general facility for later. ####@@@@
        #  Problem: this API is inefficient since it's per object (and in theory per-checkpoint). Hmm. Flag to tell system it's per-object,
        # otherwise it trusts 1st value to work for everyone in one class??
        """Return a sequence of attribute names in self whose changes should be undone by UndoStateMixin
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
    def _s_describe(self, mapping): ##e refile? rename?
        #e also it needs to take optional oldval_cache arg
        ###@@@ clarify: I think this is called by the undo mixin, rather than being "directly" part of an undo protocol for newly seen objs
        """Describe self's current state, as initargs and other diffs (whose format might be attr-specific),
        well enough to permit later recreation of an equivalent object (in the same session).
           Use mapping to make return value "pure data" (i.e. not referring to objects which might
        need to be different in a re-created copy). (Note: the API requires us, not the caller, to use mapping,
        in case it has to be used differently for different parts of our returned state.)
        [default implementation of a method needed by the "state API" [#doc - the official term for that might be different]]
        """
        clas = self.__class__ # constructor #####@@@@@ use mapping.consname?
        args, kws = self._um_initargs() # constructor args [many classes override _um_initargs rather than this method]
        desc = [ ('constructor', clas, args, kws) ]
        copy = mapping.copy # this translates all objects to suitable refs to them, and/or complaints about them if not legal [###k]
        desc = copy(desc)#k
        for attr in self._um_undoable_attrs():
            val = getattr(self, attr)
            #e future optim: we might diff val with whatever we know the initargs alone would produce;
            # for now, using some redundant vals here is simpler & more robust & always ok
            val = copy(val)
            desc.append( ('setattr', attr, val) )
                # Note: when this "setattr expr" is applied (to self or to its replacement),
                # self's class can override how that works, for all attrs or specific attrs;
                # they don't have to use setattr directly, though that's the default implementation.
                # Typically, they'd add change-warning calls before it and inval calls afterwards.
        return desc
    def _um_initargs(self):
        """[this docstring might be partly #obs, not reviewed since moved from class Node]
           Return args and kws needed by __init__, as a pair (args, kws) where args is a sequence and kws is a dict,
        in case self is deleted and might need to be recreated by Undo, or in case self's creation is undone but might need redoing.
        This does not return enough info to recreate self (for example, the attrs named in copyable_attrs);
        see the calling code for more info.
           No mapping is passed, since we don't have to translate or copy the returned args (caller does that if needed).
        [###obs: This method's existence and API is Node-specific rather than part of the general state- or undo- APIs,
         though its purpose is to let Node satisfy those APIs by implementing this method's caller.]
        [Node subclasses with different __init__ args must override this method.]
        [Note: this method's API is not compatible with, nor even very analogous to,
         the Pickle/cPickle API method of a similar name. The differences include:
         not all pickleable attrs are undoable; this method rarely returns all the
         undoable state, since not all of that can generally be passed to __init__.]
        """
        assert 0, "_um_initargs needs to be overridden in %r" % self
        ## this might be enough for some classes, esp. if they were written with that goal:
        ## return (), {}
    def _um_changed(self):
        """[subclasses should override this as needed]
        Do whatever updates are needed after some or all our (self's) undoable state was changed
        by direct calls to setattr (done immediately before calling this method).
        You may assume that self was not created or deleted in the diff that was just applied,
        i.e. that self._um_exists was True and remains True.
        """
        # noop method in case class doesn't need this
        pass
##    def _um_cons_args_kws_defaults(self): # only _um_fixed_cons_args_kws_defaults should call this directly 
##        """#doc - explain this better, put it in context:
##        [Most subclasses must override this method.]
##        Return a tuple of:
##        constructor function (which must be a class in some module, which inherits this mixin -- usually self.__class__),
##        initargs and kws for constructor (optionally tuned to current attrvals) (needn't be copied, caller does that),
##        and the "default" attrvals (for undoable attrs) that will result from using that constructor on those initargs.
##        The initargs should do enough that ordinary attrval-diffs from defaults to current attrvals will be sufficient
##        to finish reconstructing an object like self in its current state, but neither initargs nor defaults are allowed
##        to contain refs to other objects (so any current attrvals which do, will end up being set separately, as changes).
##        """
##        #####@@@@@ related Q: init allocs wrong key, how do we fix that when reconstructing? with an initarg _um_key?
##        consfunc = self.__class__
##        initargs = []
##        initkws = {} # these don't include _um_key; by the time this gets recreated, it might be different (tho prob not for now)
#### defaults = self._um_default_values_dict
##        return consfunc, initargs, initkws ## , defaults
##    def _um_fixed_cons_args_kws_defaults(self):#####@@@@@ WRONG to want dflts at all here,or in the one it calls
##        "properly encoded/copied/verified version of _um_cons_args_kws_defaults [not usually overridden]"
##        # we copy initargs, initkws, defaults, to unshare and ensure no objs
##        consfunc, args, kws = self._um_cons_args_kws_defaults() # typically overridden by client code
#### , dflts
##        archive = self._um_archive
##        copy = archive.copy_val
##        return archive.consname(consfunc), copy(args), copy(kws) ## , copy(dflts)
    # init and deinit methods
    #####@@@@@ ALL WRONG
    def _um_init(self, archive, key): # this implies we know archive when we create object. is that reasonable? yes, it seems to be.
        "This should be called sometime during the caller's __init__ method. [#doc when, if it matters]"
        assert not self._um_deinited, "reinit of deinited undoable object is not allowed: %r" % self
        self._um_archive = archive
        self._um_key = archive.allocate_key(self, key) ###@@@ WARNING: on 060216 I rewrote that method anew, ignoring whatever old one this was meant to call (if it even ever existed)
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
##        self._um_init_default_values_dict()
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
##    def _um_init_default_values_dict(self):
##        ###obs comments:
##        ### we need a class-specific (*not* allowed to vary on self) dict of all default values of undoable attrs
##        ### actually it can vary depending on initargs, under some conditions (doc'd eleswhere)
##        ### but it would be more efficient to prohibit that, so not every instance had to recompute this!
##        self._um_default_values_dict = {}
##        for attr in self._um_undoable_attrs():
##            try:
##                dflt = getattr(self.__class__, attr)
##            except AttributeError:
##                #e print warning, but only once per class?
##                dflt = None ### WRONG, but should be safe for commit [to fix breakage of morning of 051012]
####                try:
####                    dflt = getattr(self, attr) ### WRONG, but we need to figure out what to do then - decl, always define on class, ...
####                except:
####                    print "bug, fatal: exception (traceback follows) looking for default value for attr %r of class %r" % \
####                          (attr, self.__class__.__name__)
####                    raise
##            ### zap this too, for commit, 051012
####            self._um_default_values_dict[attr] = dflt
##        self._um_default_values_dict['_um_exists'] = False        
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
        # 051017: I think not.
        # note: if obj is not tracking changes (before being "registered and checkpointed" or after dying), _um_oldval_cache is a junk dict. ####k
        oldval_cache = self._um_oldval_cache
        if not oldval_cache.has_key(attr):
          if 1: # temporary #####@@@@@
            val = getattr(self, attr) #####@@@@@ LOGIC BUG: attr might be a "virtual attr"; getattr won't work! should we make it work?
            ## val = copy_val(val)
            ## nim
            ######@@@@@@ COPY VAL in case it's mutable and gets modified, or contains objrefs, unless a decl prevents this as an optim!
                # note: copy speed is not very important, since this happens at most once per attr per checkpoint.
            oldval_cache[attr] = val
            ###k can this happen during init, when old attr not present? (if so, we'll find out, by seeing an AttributeError above.)
            ###e require attr always present, using class default or __getattr__??
            # Recording this object as changing is only needed if oldval was not already there,
            # since we require that if any oldval is stored (which is only useful if it might change w/o pre-warning),
            # the obj will always be scanned for diffs in that attr. ###k
            self._um_flag_me_as_changing()
        return
    def _um_flag_me_as_changing(self): ###@@@ this might need to be attr-specific... probably in flagdict itself, nothing else.
        #e might be a precomputed lambda? NO! needn't be fast, shouldn't be space-consuming on numerous tiny objects.
        "example code, typically inlined"#obs docstring, prob wrong
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
        want_diffs = True # changed to False before used, in some cases
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
##        defaults_for_create = self._um_default_values_dict #e in principle, this might differ for create and destroy, and for each use
        # deletion diffs, including deletion-kluge for change diffs
        if existed and not exists:
            # We got deleted! For forward diffs, it's enough to store that fact,
            # but backwards diffs need to know how to recreate us (in case this delete is undone).
            #  We split that re-creation into constructor and args, plus additional changes if necessary.
            # Whether to store each current attrval in constructor args or as a "pre-delete change of this attr
            # to an arbitrary (unknown) different value" (just a kluge so the backwards diff of that change tells us the attrval)
            # is somewhat arbitrary, but in case attrvals point to objects which would be recreated in parallel,
            # we can't assume those attrvals can be set during the creation stage, only (via a mapping) during the change stage.
            # On the other hand, some objects might have properties unsettable after init;
            # this is up to the constructor-and-args chooser for the client class.
            mapping = self._um_archive
            desc = self._s_describe(mapping, oldval_cache)
            nim # that arg and its use ###@@@
                # This uses oldval_cache attr values (whenever they exist) rather than the ones in self,
                # not only for correctness but to avoid getattr at this late stage unless its really needed
                # (in case dying objects might do unwanted recomputes in getattr; this should avoid some bugs
                #  systematically rather than intermittently since some attrs are declared to always be in oldval_cache).
                # Also, we could do this more easily by just changing self values back to the ones in oldval_cache,
                # but that too is avoided since it might not always be safe.

            # now store desc instead of any diffs...
            want_diffs = False
            nim ####@@@@ honor want_diffs
            delete_b[key] = desc ####@@@@ format? any need to split it into layers? to apply it, that's needed, due to order issues!
            nim ## revise using code for this format
            
            
        # creation diffs
        if exists and not existed:
            # This is similar to the deletion case, but simpler since we can always use current attrvals.
            mapping = self._um_archive
            desc = self._s_describe(mapping)
            want_diffs = False
            create_f[key] = desc ###k don't take time to validate mapping was done or redo it [or should we? maybe in debug mode...]
                # , but check that (using copy where all mapped objs in input are an error) if this diff is actually used...

            neededQ ###@@@ IS THIS NEEDED:
            neededQ # change to code: _um_init need only flag us... or did it need to set oldvals? maybe to prevent recording only...
            neededQ # oldval_cache.clear()

        ###@@@ where i am - here

            
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

# == changetracker strategies -- different ways of knowing when to report diffs, and what old and new values to compare

# Each undoable class (including superclasses) declares which one of these changetracker classes to use for each undoable attr;
# there's one changetracker object (of one of these classes) per undoable attribute definition.
# (Objects whose undo decls vary per-object act as if they were singleton classes wrt this system,
#  rather than sharing these per-class. More precisely, they specify some object to hold this info,
#  perhaps self or self.__class__ or something in between.)

class undoable_attr_tracker:
    def __init__(self):
        pass
##    def obj_getattr(self, key):
##        "get our attr from the obj with the given key"
##        #e could probably optimize, by effectively compiling this method body in __init__
##        obj = self.model.obj(key)
##        return getattr(obj, self.attr)
    pass

class objset_tracker:
    """Track a set of objects of one class, whose state-diffs should be tracked and archived together... #doc
    """
    # add, remove methods...
    def checkpoint(self):
        # for each undoable attr that class declared, track it in the appropriate way; some of those attrs share flagdicts...
        pass
    pass
        
class full_diff_every_checkpoint(undoable_attr_tracker): # could use pre_change_track's scanner since it always has copy of all oldvals
    """Don't bother tracking changes as they happen; just always have a copy of the old value, and diff the values each time.
    One of these objects handles one attr, but the set of objects to scan can be shared among several of these objects... ###k how?
    """
    def __init__(self):
        pass
    def checkpoint(self):
        pass
    pass

class pre_change_track(undoable_attr_tracker):
    "object has to tell us before changing the attribute, so we can copy the oldval at that time"
    def __init__(self):
        self.oldvals ###@@@ set by self.prep_to_track_until_checkpoint
        self.model
        self.attr
        #super init
        pass
    def will_change(self, key, obj): #e faster to not pass obj?
        """obj (with key) is warning us that obj.attr might change soon;
        it might warn repeatedly (though it doesn't have to except once per checkpoint),
        so be fast except for the first time before each checkpoint.
        """
        # only do anything if oldval not stored already
        oldvals = self.oldvals
        if not oldvals.has_key(key):
            val = getattr(obj, self.attr) #e could optimize; could let caller also copy_val...
            val = self.model.copy(val) # note, this might register and/or translate any objects it finds in val
            oldvals[key] = val # (stored value also tells us to scan obj at next checkpoint) #e could also store obj
    def checkpoint(self):
        # any object which might have changed in this attr has its oldval stored here.
        # [i suspect some code can be shared -- the diff is the same, it's just how to find the objs that differs - vals or flags.]
        model = self.model
        copy = model.copy #e might depend on self
        attr = self.attr
        #e optim: also store copy, obj methods, and attr (no xxx.yyy in loop body)
        for key, oldval in self.oldvals.items(): ###k swap out oldvals already if it might grow during loop
            obj = model.obj(key)
            newval = getattr(obj, attr)
            newval = copy(newval) # this could find and register new objects; should they be recursively scanned?? ###k
                ### that suggests we need a 2-pass checkpoint! but i'm not sure we really do...
                # (otoh it might be worse (oresmic) if describing of their attrs has to happen in layers... don't know if it does;
                #  it's effectively a copy/translate of all the new objs found; issue is can ref be made nonrecursively; guess yes,
                #  just requires assigning a key; but worry about refs from initargs... worst case: have lists of things to scan
                #  incl attrs and new objs, iterate scanning some lists and building up others until all are empty.)
                # pass 1: scan vals and find new objs (in any layer) (and scan them too while describing their state, etc)
                # pass 2: actually generate diffs (in layered order)
            diff = self.diff(oldval, newval) # is this bidirectional?? is it multipart, to be added somewhere, with nonempty reported?
                # is it primitive or a val-diff? is format attr-dependent?
            nim # store diff
        # now prep for next
        return
    pass

class post_change_track(undoable_attr_tracker):
    """object has to tell us before or after changing the attribute (anytime before next checkpoint is ok);
    we always have our own copy of the state
    """
    def __init__(self):
        pass
    def checkpoint(self):
        # difference from others: we have a separate oldval dict (full) and flagdict (partial).
        for key, obj in self.flagdict.items():
            # obj needs diff in this attr... use same code as above (share the code)
            pass
        pass
    pass

# end
