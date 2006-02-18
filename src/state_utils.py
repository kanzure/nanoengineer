# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
state_utils.py

General state-related utilities.

$Id$
'''
__all__ = ['copy_val'] # __all__ must be the first symbol defined in the module.

    #e was the old name (copy_obj) better than copy_val??

__author__ = 'bruce'

# ==

class _eq_id_mixin_: ##e use more (GLPane?); renamed from _getattr_efficient_eq_id_mixin_
    """For efficiency, any objects defining __getattr__ which might frequently be compared
    with == or != or coerced to a boolean, should have definitions for __eq__ and __ne__ and __nonzero__
    (and any others we forgot??), even if those are semantically equivalent to Python's behavior when they don't.
    Otherwise Python has to call __getattr__ on each comparison of these objects, just to check whether
    they have one of those special method definitions (potentially as a value returned by __getattr__).
       This mixin class provides definitions for those methods. It's ok for a class to override some of these.
    It can override both __eq__ and __ne__, or __eq__ alone, but should not normally override __ne__ alone,
    since our definition of __ne__ is defined as inverse of object's __eq__.
       These definitions are suitable for objects meant as containers for "named" mutable state
    (for which different objects are never equal, even if their *current* state is equal, since their future
    state might not be). They are not suitable for data-like objects. This is why the name contains _eq_id_
    rather than _eq_data_. For datalike objects, there is no shortcut to defining each of these methods in
    a customized way (and that should definitely be done, for efficiency, under same conditions in which use
    of this mixin is recommended). We might still decide to make an _eq_data_mixin_(?) class for them, for some other reason.
    """
    #bruce 060209
    def __eq__(self, other):
        return self is other
    def __ne__(self, other):
        ## return not (self == other) # presumably this uses self.__eq__ -- would direct use be faster?
        return not self.__eq__(other)
    def __nonzero__(self): ###k I did not verify in Python docs that __nonzero__ is the correct name for this! [bruce 060209]
        ## return self is not None # of course it isn't!
        return True
    def __hash__(self): #####k guess at name; guess at need for this due to __eq__, but it did make our objects ok as dict keys again
        return id(self) #####k guess at legal value
    pass

# ==

class objkey_allocator:
    """Use one of these to allocate small int keys for objects you're willing to keep forever.
    We provide public dict attrs with our tables, and useful methods for whether we saw an object yet, etc.
    """
    def __init__(self):
        self.obj4key = {}
            # maps key to object. this is intentionally not weak-valued. It's public.
        self._key4obj = {} # maps id(obj) -> key; semiprivate
        self._lastobjkey = 0

    def allocate_key(self, key = None): # not yet directly called; untested
        "Allocate the requested key (assertfail if it's not available), or a new one we make up, and store None for it."
        if key is not None:
            # this only makes sense if we allocated it before and then abandoned it (leaving a hole), which is NIM anyway,
            # or possibly if we use md5 or sha1 strings or the like for keys (though we'd probably first have to test for prior decl).
            # if that starts happening, remove the assert 0.
            assert 0, "this feature should never be used in current code (though it ought to work if it was used correctly)"
            assert not self.obj4key.haskey(key)
        else:
            # note: this code also occurs directly in key4obj_maybe_new, for speed
            self._lastobjkey += 1
            key = self._lastobjkey
            assert not self.obj4key.haskey(key) # different line number than identical assert above (intended)
        self.obj4key[key] = None # placeholder; nothing is yet stored into self._key4obj, since we don't know obj!
        return key

    def key4obj(self, obj): # maybe not yet directly called; untested
        """What's the key for this object, if it has one? Return None if we didn't yet allocate one for it.
        Ok to call on objects for which allocating a key would be illegal (in fact, on any Python values, I think #k).
        """
        return self._key4obj.get(id(obj)) #e future optim: store in the obj, for some objs? not sure it's worth the trouble,
            # except maybe in addition to this, for use in inlined code customized to the classes. here, we don't need to know.
            # Note: We know we're not using a recycled id since we have a ref to obj! (No need to test it -- having it prevents
            # that obj's id from being recycled. If it left and came back, this is not valid, but then neither would the comparison be!)

    def key4obj_maybe_new(self, obj):
        """What's the key for this object, which we may not have ever seen before (in which case, make one up)?
        Only legal to call when you know it's ok for this obj to have a key (since this method doesn't check that).
        Optimized for when key already exists.
        """
        try:
            return self._key4obj[id(obj)]
        except KeyError:
            pass
        # this is the usual way to assign new keys to newly seen objects (maybe the only way)
        # note: this is an inlined portion of self.allocate_key()
        self._lastobjkey += 1
        key = self._lastobjkey
        assert not self.obj4key.haskey(key)
        self.obj4key[key] = obj
        self._key4obj[id(obj)] = key
        return key
    
    pass # end of class objkey_allocator

# ==

class Classification: #e want _eq_id_mixin_? probably not, since no getattr.
    """Classifications record policies and methods for inspecting/diffing/copying/etc all objects of one kind,
    or can be used as dict keys for storing those policies externally.
    (By "one kind of object", we often mean the instances of one Python class, but not always.)
    """
    pass

# possible future optim: some of these could be just attrholders, not instances, so their methods wouldn't require 'self'...
# OTOH some of them do make use of self, and, we might put generic methods on the superclass.
# ... ok, leave it like this for now, and plan to turn it into C code someday; or, use class methods.
# (or just use these subclasses but define funcs outside and store them as attrs on the sole instances)

class AtomicClassification(Classification):
    """Atomic (immutable, part-free) types can be scanned and copied trivially....
    """
##    def scan(self, val, func):
##        "call func on nontrivial parts of val (what this means precisely is not yet defined)"
##        pass
    def copy(self, val, func):
        "copy val, using func to copy its parts"
        return val
    pass

class ListClassification(Classification):
    "Classification for Lists (or maybe any similar kind of mutable sequences?)"
##    def scan(self, val, func):
##        "call func on all parts of val"
##        for part in val:
##            func(part)
    def copy(self, val, func):
        "copy val, using func for nontrivial parts"
        return map( func, val) #e optimize by changing API to be same as map, then just using an attrholder, holding map?
    pass

class DictClassification(Classification):
    def copy(self, val, func):
        res = {} #e or use same type or class as val? not for now.
        for key, val1 in val.iteritems():
            # as an optim, strictly follow a convention that dict keys are immutable so don't need copying
            res[key] = func(val1)
        return res
    pass

class TupleClassification(Classification):
    def copy(self, val, func):
        """simple version should be best for now
        """
        return tuple(map(func, val))
##    def copy(self, val, func):
##        """optimize by not copying unless you have to; use 'is' on copied parts to decide
##        (assume func is identity whenever it can be)"
##        """
##        copies = map(func, val)
##        for i in xrange(len(val)):
##            if copies[i] is not val[i]: # hmm, is this too slow for that optim to be worthwhile? it does save memory...
##                return tuple(copies)
##        return val
    pass

class StateHolderInstanceClassification(Classification):
    """###doc, implem - hmm, why do we use same obj for outside and inside? because, from outside, you might add to explore-list...
    """
    def __init__(self, clas, lis):
        "Become a Classification for class clas, whose declared state-holding attrs are the attrnames in sequence lis."
        self.attrs = dict([(attr, attr) for attr in lis]) #e might replace vals with their policies, now or later
        self.attrlist = tuple(lis)
    def copy(self, val, func): # from outside, when in vals, it might as well be atomic! WRONG, it might add self to todo list...
        return val
    pass

# == helper code  [##e all code in this module needs reordering]

from Numeric import array, PyObject

numeric_array_type = type(array(range(2))) # __name__ is 'array', but Numeric.array itself is a built-in function, not a type


# atomic_types = common types whose objects have no parts -- no need to scan, not mutable, no custom defs
atomic_types = tuple( map(type, (1, 1L, 1.0, "x", u"x", None, True)) ) #e also complex (a python builtin type)? functions, etc?

container_types = tuple( map(type, ( [], (), {} ))) # scan parts (and sometimes copy them) with specialized non-customizable code

# For speed in initial classification of Python values (most of whose types are in atomic_types),
# we keep the most basic info in a global dict (from type to a code), and let various functions access it inline.
# The values are:
# missing, for types we never saw before (eg extension types, internal types). Warn, then treat as opaque.
# 0 if no special handling is required (atomic or opaque, use ==).
# 1 if some callers will want to use inline special code (container_types).
# 2 for anything else -- call classify(val) to look up (or create and memoize) Classification which tells you how to handle it.
# For uniformity, you can call that on anything, even if known_types[type(val)] is 0 or 1. (NIM?)

# or should we store the Classification itself, not 2? (tho often it's a func of __class__ -- so store a code to say use __class__?)

known_types = {}
known_classes = {}

for typ in atomic_types:
    known_types[typ] = 0

for typ in container_types:
    known_types[typ] = 1 # hmm, why not use different code for each?

# typical code:
#   code = known_types.get(type(val));
#   if code == 0 or 1, fast inlined special case;
#   else call classify(val) & use result in a general way.

###e need to declare InstanceType! Should we have a Classifier for handling it (which says, look at __class__)?

# should known_types store a classifier object?

def classify(val):
    "#doc"
    typ = type(val)
    code = known_types.get(typ)
    if code is None:
        print "fyi: classify sees type %r for first time; it ought to be declared; treating it as atomic" % typ
        known_types[typ] = 0 # treat as atomic, to avoid bugs from delving into it
        return AtomicClassification ### IMPLEM
    else:
        assert code == 2 # since using this on vals you don't have to use it on is NIM
    

# ==

class copy_run: # might have called it Copier, but that conflicts with the ops_copy.py class; rename it again if it becomes public
    "one instance exists to handle one copy-operation of some python value, of the kind we use in copyable attributes"
    #e the reason it's an object is so it can store options given to the function copy_val, when we define those.
    #e such options would affect what this does for python objects it doesn't always copy.
    unknowns_pass_through = False
    def __init__(self):
        ##e might need args for how to map pyobjs, or use subclass for that...
        #e ideal might be a func to copy them, which takes our own copy_val method...
        pass ## not needed: self.memo = {} # maps id(obj) to obj for objs that might contain self-refs
    def copy_val(self, obj):
        t = type(obj)
        if t in atomic_types:
            return obj
        #e memo check? not yet needed. if it is, see copy module (python library) source code for some subtleties.
        copy = self.copy_val
        if t is type([]):
            return map( copy, obj )
        if t is type(()):
            #e note: we don't yet bother to optimize by avoiding the copy when the components are immutable,
            # like copy.deepcopy does.
            return tuple( map( copy, obj ) )
        if t is type({}):
            res = {}
            for key0, val in obj.iteritems():
                key = copy(key0) # might not be needed or even desirable; ok for now
                if key0 is not key:
                    if platform.atom_debug:#######@@@@@@@@
                        print "warning: copy_val copied this dict key:",key # will happen for tuples... should look, then remove
                val = copy(val)
                res[key] = val #e want to detect overlaps as errors? to be efficient, could just compare lengths.
            assert len(res) == len(obj) # for now
            return res
        #e Numeric array
        if t is numeric_array_type:
            if obj.typecode() == PyObject:
                return array( map( copy, obj) )
                # we don't know whether the copy typecode should be PyObject (eg if they get encoded),
                # so let it be inferred for now... fix this when we see how this needs to be used,
                # by requiring it to be declared, since it relates to the mapping of objects...
                # or by some other means.
            return obj.copy() # use Numeric's copy method for Character and number arrays ###@@@ verify ok from doc of this method...
        # Handle data-like objects which declare themselves as such.
        # Note: we have to use our own method name and API, since its API can't be made compatible
        # with the __deepcopy__ method used by the copy module (since that doesn't call back to our own
        # supplied copy function for copying parts, only to copy.deepcopy).
        #e We might need to revise the method name, if we split the issues of how vs whether to deepcopy an object.
        try:
            method = obj._s_deepcopy
            # This should be defined in any object which should *always* be treated as fully copied data.
            # Presently this includes VQT.Q (quats), and maybe class gamessParms.
        except AttributeError:
            pass
        else:
            return method( self.copy_val) # (passing copy_val wouldn't be needed if we knew obj only contained primitive types)
        # Special case for QColor; if this set gets extended we can use some sort of table and registration mechanism.
        # We do it by name so this code doesn't need to import QColor.
        if obj.__class__.__name__ == 'qt.QColor':
            return _copy_QColor(obj) # extra arg for copyfunc is not needed
        return copy_unknown_type(self, obj)
    def copy_unknown_type(self, obj):
        if self.unknowns_pass_through:
            return obj
        #e future: if we let clients customize handling of classes like Atom, Bond, Node,
        # they might want to encode them, wrap them, copy them, or leave them as unchanged refs.
        #
        # Unknown or unexpected pyobjs will always be errors
        # (whether or not they define copy methods of some other kind),
        # though we might decide to make them print a warning rather than assertfailing,
        # once this system has been working for long enough to catch the main bugs.
        assert 0, "uncopyable by copy_val: %r" % (obj,)
    pass

class copy_run_unknowns_pass_through(copy_run):
    unknowns_pass_through = True
    pass

def _copy_QColor(obj):
    from qt import QColor
    assert obj.__class__ is QColor
    return QColor(obj)

# ==

# right now, copy_run only uses self to know which class it is, of the following. in future it might know more... not sure

copy_val = copy_run().copy_val

copy_val_again = copy_run_unknowns_pass_through().copy_val # temporary name

def copy_val_OBS_FOR_DOCSTRING(obj):
    """Copy obj, leaving no shared mutable components between copy and original,
    assuming (and verifying) that obj is a type we consider (in nE-1) to be a
    "standard data-like type", and using our standard copy semantics for such types.
    (These standards are not presently documented except in the code of this module.)
       #e In the future, additional args will define our actions on non-data-like Python objects
    (e.g. Atom, Bond, Node), for example by providing an encoding filter for use on them which might
    raise an exception if they were illegal to pass, and we might even merge the behaviors of this function
    and the ops_copy.Copier class; for now, all unrecognized types or classes are errors
    if encountered in our recursive scan of obj (at any depth).
       We don't handle or check for self-reference in obj -- that would always be an error;
    it would always cause infinite recursion in the present implem of this function.
       We don't optimize for shared subobjects within obj. Each reference to one of those
    is copied separately, whether it's mutable or immutable. This could be easily fixed if desired.
    """
##    return copy_run().copy_val(obj) # let's hope the helper gets deleted automatically if it saves any state (it doesn't now)
    assert 0, "never called"
    pass



# ==

class attrlayer_scanner:
    def __init__(self):
        pass
    def scan(self, scanner):
        self.scanner = scanner
        self.archive = scanner.archive
        self.start()
        self.doit()
        self.end()
        del self.scanner
        del self.archive
        return
    def start(self):
        self.vals_grabbed = {} # maps key to a grabbed val (not yet scanned, copied, diffed) -- motivation: ordering all scanning by attr
        self.vals_scanned = {} # maps key to a fully scanned val for this attr (diffed if we're ever going to)
        self.copy_val = copy_run_gather_unknowns(func = self.scanner.see_and_return_obj).copy_val ######@@@@@@ IMPLEM
        return
    def doit(self):
        "scan all vals"
        vg = self.vals_grabbed
        copy_val = self.copy_val
        while vg:
            key, val = vg.popitem()
            valcopy = copy_val(val) # this puts new objs into scanner... is that what we want? maybe here first? ###
            ### we want new objs to have attrs in old and this layer pushed into our own vg dict, or scanned immediately
            # by finished layers... #####@@@@@ IMPLEM
        assert 0, "done, now what?"#####@@@@@ IMPLEM
    def end(self):
        pass # not sure if caller is really done with our values... maybe there's more to our lifecycle
    def scan_leftover(self, key, obj, attr, val):
        "after we're done, some later layer finds obj (with key) with an attr in this layer, with val."
        ###e use same copy_val, or a new one for use in this stage?
        # ignore attr, obj for now
        ###e when diffing, we'd first compare val here, unless we have to explore it... which i guess we do... subclasses re that?
        valcopy = self.copy_val(val) ####@@@@ review where this puts found objs
        # store key and valcopy
        assert not self.vals_scanned.haskey(key) ###@@@ remove when works
        self.vals_scanned[key] = valcopy
    pass

## for explore layer, do we use a subclass?? well, does it have its own code? yes, for what to do on unrec objs...
# but that could just be a lambda we pass in, which is to be preferred when just as simple.

# note - we don't have attrs until we see objs... which means, the order of attrs is not known at first...
# so how do we insert new attrs? does this chg order of old ones? or should classes be predeclared so this gets sorted out?

class scanner: #bruce 060209, a work in progress (not yet called or correct)
    #e Ultimately, this might become methods of archive... not sure whether it's useful aside from undo... maybe it is (copy, mmpwrite)
    def __init__(self, archive):
        "depends on archive for certain methods for registering objects, etc..."
        self.archive = archive
    def start(self, start_val):
        "prepare to scan, maybe do so; start_val can be anything (obj, list of objs, val, list of vals)" #k klugy protocode
        self.seen_objs = {} # maps id(obj) to obj, for objs seen before in a single complete scan.
            # for speed on repeatedly seeing them we use id(obj), and we have to keep a reference to avoid its recycling
            # unless as future optim we can depend on archive keeping one (as we could if we always grabbed key).
            # Not sure if we need obj and/or key otherwise.
        self.objs_to_explore = {} # maps key to obj for objs we want to explore (delve inside) later in this scan
            ###e we may have to split this by attr layer based on attr and stage in which we found them... don't know yet
        ## self.copy_val = self.archive.copy_val_for_scan ######@@@@@@ implem - hmm, it explores...
        ##e could optim the following by making some attrs preaccessed, i bet
##        self.copy_val = copy_run_gather_unknowns(func = self.see_and_return_obj).copy_val ######@@@@@@ IMPLEM
            #e actually, do this per-attr ###@@@
##        #obs??
##        self.todo = start_objs #e put in list, so ok if contains dups?
##
##        ### don't we need to store them more permanently? ####@@@@ key not id
##        ## or do we reuse this scanner object multiple times? and, seen before is one thing, seen in this scan is another...
##        self.encoded_objs = {} # maps id(obj) to encoded_obj, only for objs that should be encoded when present in value-diffs
        self.vals_todo = [start_val] ###k??
        # let's say that for any class to be explored inside, you have to predeclare it when you load it.
        # that lets us process its attr decls now (if not earlier). in fact, archive can do that and store that...
        # so ask it when we need to know order. And we do! We want order of all layers
        # and ability to later sort class/attr pair into layers. ok to lump several attrs into one layer, i think,
        # and for that set to not be known and not be done in order. attr only matters re copy policy.
        # maybe best to put objs, not attrvals, on the todo list? the objs hold the attrs... then have a todo list per layer.
        # only badness is no ability to just scan the obj's dict. (or a need to scan it *and* later use getattr.)
        # otoh, maybe just declare that any attr with custom scanner/copyer needs its own layer. (most use generic scanner,
        # many are in generic layer.)
        self.attrlayers_todo = [x() for x in self.archive.attrlayer_constructors()] ###k guess [#e later: optim by reusing these?]
        return
    def doit(self): # explore_all
        layers = self.attrlayers_todo
        self.attrlayers_todo = 222
        for layer in layers:
            layer.scan(self)
        
##        while self.vals_todo:
##            # process every element, then replace it with a new list...
##            # hmm, this doesn't make sense, since process means copy, and we don't know where to save the copy.
##            # so we need to process it as found, or, have more in our todo list, like attr key val (organized as per-attr lists).
##            ######@@@@@ this is where i am 1130am 060216
##            todo = self.vals_todo
##            self.vals_todo = 333
##            self.objs_to_explore = {}
    def end(self):
        del self.seen_objs
        del self.objs_to_explore
        pass
    def see_and_return_obj(self, obj):
        ## new, key = self.archive.objkey_newQ(obj) # see it, get or make key, say whether it's newly seen by archive... wait, not the point
        try:
            return self.seen_objs[id(obj)] # note, we're just assuming this returns obj! (for speed)
        except KeyError:
            pass
        # first time we're seeing obj in this scan
        self.seen_objs[id(obj)] = obj
        key = self.archive.key4obj_maybe_new(obj) # do we want to know if archive never saw it before, too?
            # who analyzes policy for it, archive or us? probably archive, so it can memoize policy per obj. ####@@@@
        self.objs_to_explore[key] = obj ###e only do this if type is ok? or, check that later?
        return obj
##    def copyval_and_explore(self, val):
##        assert 0
    def explore_all(self, starting_todo):
        # objs in self.todo are the ones we still need to scan - each is being seen for the first time (already checked if seen before)
        ##e we'll have several levels of todo ((structure, selection, view) x (provisional)), scan them in order...
        todo = list(starting_todo)
        ###e maybe scan it as vals instead? or as one val... but no diffs?? hmm? what do ppl want as roots - most flex is vals.
        while self.todo:
            self.newtodo = [] # used in explore
            todo = self.todo
            self.todo = 333
            for obj in todo:
                self.explore(obj) # explore obj for more objs, store diffs/vals found in obj somewhere, append unseen objs to newtodo
                encoded = self.new_encoding(obj) ###e WRONG, no, don't redo if seen in prior scan (I think)
                if encoded is not obj:
                    self.encoded_objs[id(obj)] = encoded
                # self.seen_objs[id(obj)] = obj # just this scan... actually didn't this happen earlier when we first encountered obj? YES
                continue #??
            self.todo = self.newtodo
        return
    def explore(self, obj):
        ###e seen it ever? seen it this scan? needs encoding? (figure that out first, in case it refs itself in some attr)
        # if it's new: store that stuff, then:
        # figure out its type, and thus its attr-policy-map (or ask it)
        objid # for this, take time to find a nice key (small int); might just have a map from id(obj) to that
        for attr, val in obj.__dict__.iteritems():
            # figure policy of this attr, and dict to store valdiffs in if we're doing that, also whether it's structure or sel etc
            this_attrs_diffs # a dict in which to store diffs for this attr
            # and of course whether to proceed
            oldval = this_attrs_last_seen_state[objid] ##e encoded??? (always copied) # we have this for *every* attrval... so store it below!
            #e if we don't have an oldval...
            if val != oldval:
                # val differs, needs two things:
                # - exploring for new objs
                # - storing as a diff
                ##### what about scanning objs that are not found as diffs, but might have diffs inside them?
                # do we depend on change tracking to report them to us? or, rescan some or all attrs every time? ###e
                encoded = self.explore_copy_encode_val(val) # stores new stuff on newtodo, i guess... hmm, same method should also copy/encode val
                ###e check again for != in case encoding made it equal??? (rethink when we need some encoding someday? we don't yet)
                this_attrs_diffs[objid] = oldval
                this_attrs_last_seen_state[objid] = encoded # not val? also val? hmm... consider need seply for copy, encode, in val ####e
            continue
        return
    def gather(self, obj, classification ):
        #060215 - assume gathering is a separate phase, which does no diffing, and is not incremental except for optimized classes.
        # might as well pretend to be efficient, so note that we already classified the object when we found it! not yet.
        # Does obj have any attrs for us to explore? if so, it is an instance object, or decls them... or is in our table of exceptions
        # fast way: look at its __class__
        assert 0
    def classify(self, obj):
        #e should this be on archive, so it can keep keys? it can call up to arch as needed, and self has arch during loops needing it
        return the_Classifier.classify(obj)
    pass

    
class Classifier:
    """Maintain an ability to classify arbitrary python values. Permit policies to be declared for classes
    by special attribute names, or by explicit calls to our decl methods (passing the class or its name).
    For classes declared by name, or defined in toplevel code (??), warn when first seeing new classes with same name.
    """
    def __init__(self):
        self.classifications = {}
    def classify(self, val):
        """Classify arbitrary python values (but when they are instance objects, let them override that classification);
        return classification;
        warn once per new class for new classes with the same name as old ones.
        """
        # use __class__ or type() to determine preliminary classification
        try:
            clas = val.__class__ # this exists even for ints, etc!
        except AttributeError:
            # commonest cases of this: extension objects, classes (not sure about functions, bound methods)
            clas = type(val) # see if mutable -- not needed here... see if atomic -- needed so we can scan its parts
            #e record the fact there was no __class__??
        res = self.classifications.get(clas)
        if res is None:
            res = self.new_class(clas) # handle newly seen classes or types
        ##e figure out if answer needs to be per-instance (nim, not yet needed)
        return res
##    def objkey(self, obj):
##        """Return object key (for state-containing objects, assigned here if necessary) or None (for other objects);
##        """
##        pass
    def new_class(self, clas):
        """create, store and return classification for newly seen classes or types
        (not worrying about per-instance classification even if they request that)
        """
        res = Classification()
        self.classifications[clas] = res
        if self.debug:
            print "new class or type:", clas, res
        return res
    pass

the_Classifier = Classifier() # if we reload this module, start over (#e ideally we'd default to info declared in the older one)

# i fear it's too slow.
# - keep a global dict of types - most objs in it and are atomic and get skipped by all algs; inline the access.
# unknown types are rare.. for them call a func.


# == test code

def _test():
    print "testing some simple cases of copy_val"
    map( _test1, [2,
                  3,
                  "string",
                  [4,5],
                  (6.0,),
                  {7:8,9:10},
                  array([2,3]),
                  None] )
    print "done"

def _test1(obj): #e perhaps only works for non-pyobj types for now
    if obj != copy_val(obj):
        print "failed for %r" % (obj,)

if __name__ == '__main__':
    _test()

# end
