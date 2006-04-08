# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
state_utils.py

General state-related utilities.

$Id$
'''
__author__ = 'bruce'

from state_constants import *
import types
from types import InstanceType # use this form in inner loops
import env
from debug import print_compact_stack
import platform # for atom_debug [bruce 060315]

#060407 zapped all the code that looked at this:
## debug_priorstate_kluge = False # do not commit with true

SAMEVALS_SPEEDUP = False    # Use the C extension

if SAMEVALS_SPEEDUP:
    try:
        # If we're using the samevals extension, we need to tell the
        # extension what a Numeric array looks like, since the symbol
        # PyArray_Type was not available at link time when we built
        # the extension.
        from samevals import setArrayType
        import Numeric
        setArrayType(type(Numeric.array((1,2,3))))
    except ImportError:
        SAMEVALS_SPEEDUP = False

# see debug flags, below

### TODO:
'''
Where is _s_deepcopy (etc) documented? (In code and on wiki?)

That should say:

- When defining _s_deepcopy, consider:

  - is it correct for any copyfunc argument? (esp in its assumption about what that returns, original or copy or transformed copy)
  
  - is its own return value __eq__ to the original? It should be, so you have to define __eq__ AND __ne__ accordingly.
  
  - should you define _s_scan_children to, to scan the same things copied? (Only if they are instance objects, and are "children".
    See S_CHILDREN doc for what that means.)

Did the above for VQT and jigs_planes, still no __eq__ or children for jig_Gamess -- I'll let that be a known bug I fix later,
to test the behavior of my error detect/response code.
Also, when I do fix it (requires analyzing jig_Gamess contents) I might as well turn it into using a mixin
to give it a proper __eq__ based on declaring the state attrs! 
####@@@@

I might as well put state decls into the archived-state objects I'm creating, so they too could be compared by __eq__ and diffed!!!
(Actually, that won't work for diff since it has to descend into their dictionaries in an intelligent way.
 But it might work for __eq__.)

This means my archived-state objects should really be objects, not just tuples or dicts.
Let's change the code that collects one to make this true. Search for... attrdict?

S_CHILDREN: we might need a decl that we have no children (so don't warn me about that), and a reg for external classes of the same.

And certainly we need to go through the existing stateholder classes (e.g. Node) and add their attr/child decls.
Maybe rather than accomodating copyable_attrs, we'll just replace it? Not sure, maybe later (a lot of things use it).

Do any inapprop obs get a key (like data or foreign objs) in current code?? #####@@@@@
'''

##debug_dont_trust_Numeric_copy = False # 060302 -- will this fix last night's singlet-pulling bug? [no, that was weird '==' semantics]
##    # (warning, it's slow!) 
##
##debug_print_every_array_passed_to_Numeric_copy = False # hmm, this might be slow too... to be safe the runtime
##    # use of it should condition it on env.debug(), and to be fast, also on debug_dont_trust_Numeric_copy.

# ==

class _UNSET_class:
    "[private class for _UNSET_, which sometimes represents unset attribute values, and similar things]"
    #e can we add a decl that makes the _s_attr system notice the bug if it ever hits this value in a real attrval? (should we?)
    def __init__(self, name = "_???_"):
        self.name = name
    def __repr__(self):
        return self.name
    pass

try:
    _UNSET_ # ensure only one instance of _UNSET_ itself, even if we reload this module
except:
    _UNSET_ = _UNSET_class("_UNSET_")

try:
    _Bugval
except:
    _Bugval = _UNSET_class("_Bugval")
    
# ==

class _eq_id_mixin_: ##e use more? (GLPane?)
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

def transclose( toscan, collector ):
    """General transitive closure routine using dictionaries for collections in its API,
    where the keys can be whatever you want as long as they are unique (for desired equiv classes of objects)
    and used consistently.
       Details: Toscan should be a dictionary whose values are the starting point for the closure,
    and collector(obj1, dict1) should take one such value obj1 (never passed to it before)
    and for each obj it finds from obj1 (in whatever way it wants -- that defines the relation we're transitively closing),
    store it as a new value in dict1 (with appropriate consistent key).
       We don't modify toscan, and we return a new dictionary (with consistent keys) whose values
    are all the objects we found. Collector will have been called exactly once on each object we return.
    It must not modify toscan (since we use itervalues on it while calling collector),
    at least when it was called on one of the values in toscan.
    """
    # We have three dicts at a time: objects we're finding (not being checked for newness yet),
    # objects we're scanning to look for those, and objects seen (i.e. done with or being scanned).
    # Keys are consistent in all these dicts (and should be as unique as objects need to be distinct),
    # but what they actually are is entirely up to our args (but they must be consistent between the two args as well).
    # [#doc: need to explain that better]
    seen = dict(toscan)
    while toscan:
        found = {}
        len1 = len(toscan)
        for obj in toscan.itervalues():
            collector(obj, found) #e might the collector also want to know the key??
        len2 = len(toscan)
        if len1 != len2:
            # btw, if this happens when toscan is not the one passed in, it's still a bug.
            print "bug: transclose's collector %r modified dict toscan (id %#x, length %d -> %d)" % \
                  (collector, id(toscan), len1, len2)
        # now "subtract seen from found"
        new = {}
        for key, obj in found.iteritems():
            if not seen.has_key(key):
                new[key] = obj
        seen.update(new)
        toscan = new
        continue
    return seen

# ==

# private exceptions for use in private helper functions for certain recursive scanners:
class _IsMutable(Exception): pass
class _NotTheSame(Exception): pass


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

###@@@ not yet clear if these simple ones end up being used...

##class AtomicClassification(Classification):
##    """Atomic (immutable, part-free) types can be scanned and copied trivially....
##    """
####    def scan(self, val, func):
####        "call func on nontrivial parts of val (what this means precisely is not yet defined)"
####        pass
##    def copy(self, val, func):
##        "copy val, using func to copy its parts"
##        return val
##    pass
##
##class ListClassification(Classification):
##    "Classification for Lists (or maybe any similar kind of mutable sequences?)"
####    def scan(self, val, func):
####        "call func on all parts of val"
####        for part in val:
####            func(part)
##    def copy(self, val, func):
##        "copy val, using func for nontrivial parts"
##        return map( func, val) #e optimize by changing API to be same as map, then just using an attrholder, holding map?
##    pass

def copy_list(val):
    return map(copy_val, val)

def scan_list(val, func):
    for elt in val:
        ## func(elt)
        scan_val( elt, func) #bruce 060315 bugfix
    return

def _same_list_helper(v1, v2):
    n = len(v1)
    if n != len(v2):
        raise _NotTheSame
    for i in xrange(n):
        _same_vals_helper(v1[i], v2[i])
    return

##class DictClassification(Classification):
##    def copy(self, val, func):
##        res = {} #e or use same type or class as val? not for now.
##        for key, val1 in val.iteritems():
##            # as an optim, strictly follow a convention that dict keys are immutable so don't need copying
##            res[key] = func(val1)
##        return res
##    pass

def copy_dict(val):
    res = {}
    for key, val1 in val.iteritems():
        res[key] = copy_val(val1)
    return res

def scan_dict(dict1, func):
    len1 = len(dict1) #060405 new code (#####@@@@@ needs to be done in C version too!)
    for elt in dict1.itervalues(): # func must not harm dict1
        ## func(elt)
        scan_val( elt, func) #bruce 060315 bugfix
    len2 = len(dict1)
    if len1 != len2:
        print "bug: scan_dict's func %r modified dict %#x (len %d -> %d) during itervalues" % \
              (func, id(dict1), len1, len2)
    return

def _same_dict_helper(v1, v2):
    if len(v1) != len(v2):
        raise _NotTheSame
    for key, val1 in v1.iteritems():
        if not v2.has_key(key):
            raise _NotTheSame
        _same_vals_helper(val1, v2[key])
    # if we get this far, no need to check for extra keys in v2, since lengths were the same
    return
    
##class TupleClassification(Classification):
##    def copy(self, val, func):
##        """simple version should be best for now
##        """
##        return tuple(map(func, val))
##            # not worth the runtime to save memory by not copying if all parts immutable; save that for the C version.
##    pass

def copy_tuple(val):
    return tuple(map(copy_val, val))

scan_tuple = scan_list

_same_tuple_helper = _same_list_helper

# Tuple of state attr decl values used for attrs which hold "defining state",
# which means state that should (usually) be saved, compared, copied, tracked/changed by Undo, etc.
# Should not include attrs recomputable from these, even if as an optim we sometimes track or save them too (I think).

STATE_ATTR_DECLS = (S_DATA, S_CHILD, S_CHILDREN, S_REF, S_REFS, S_PARENT, S_PARENTS) # but not S_CACHE, S_JUNK(?), S_CHILDREN_NOT_DATA, etc
    #e refile in state_constants.py ? not sure, since it's not needed outside this module

class InstanceClassification(Classification): #k used to be called StateHolderInstanceClassification; not yet sure of scope
    # we might decide to have a helper func classify an instance and return one of several classes, or None-or-so...
    # i mean some more atomic-like classification for classes that deserve one... [060221 late]
    #k not sure if this gains anything from its superclass
    """###doc, implem - hmm, why do we use same obj for outside and inside? because, from outside, you might add to explore-list...
    """
    def __init__(self, class1):
        "Become a Classification for class class1 (applicable to its instances)"
        self.policies = {} # maps attrname to policy for that attr #k format TBD, now a map from attrname to decl val
        self.class1 = class1

        #e now something to take class1 and look up the changedicts and their names -- see changes.register_class_changedict
        #e and let this run when we make InstanceClassification??
        # no, we need to know about new class's chanegdicts before we see any instances!
        # (who does? obj_classifier or undo_archive?)
        
        self.attrcodes_with_no_dflt = []
            # public list of attrcodes with no declared or evident default value (might be turned into a tuple)
            # an attrcode means a pair (attr, acode) where acode's main purpose is to let same-named attrs have different attrdicts
            # [attrcodes were added 060330]
        self.attrcode_dflt_pairs = []
            # public list of attrcode, dflt pairs, for attrs with a default value (has actual value, not a copy);
            # attrcode will be distinct whenever dflt value differs (and maybe more often) [as of 060330]
        self.dict_of_all_state_attrcodes = {}
        self.attrcodes_with_undo_setattr = {} #060404, maps the attrcodes to an arbitrary value (only the keys are currently used)
        self.categories = {} # (public) categories (e.g. 'selection', 'view') for attrs which declare them using _s_categorize_xxx
        self.attrlayers = {} # (public) similar [060404]
        self.attrcode_defaultvals = {} # (public) #doc
            ##@@ use more, also know is_mutable about them, maybe more policy about del on copy
            # as of 060330 this is only used by commented-out code not yet adapted from attr to attrcode.
        self.warn = True # from decls seen so far, do we need to warn about this class (once, when we encounter it)?
        self.debug_all_attrs = False # was env.debug(); can normally be False now that system works
        
        self._find_attr_decls(class1) # fills self.policies and some other instance variables derived from them

        self.attrcodes_with_no_dflt = tuple(self.attrcodes_with_no_dflt) # optimization, I presume; bad if we let new attrs get added later
        self.attrcode_dflt_pairs = tuple(self.attrcode_dflt_pairs)
        
        self.S_CHILDREN_attrs = self.attrs_declared_as(S_CHILD) + \
                                self.attrs_declared_as(S_CHILDREN) + \
                                self.attrs_declared_as(S_CHILDREN_NOT_DATA)  #e sorted somehow? no need yet.
        
        self._objs_are_data = copiers_for_InstanceType_class_names.has_key(class1.__name__) or hasattr(class1, '_s_deepcopy')

        if self.warn and env.debug():
            # note: this should not be env.debug() since anyone adding new classes needs to see it...
            # but during development, with known bugs like this, we should not print stuff so often...
            # so it's env.debug for now, ####@@@@ FIX THAT LATER  [060227]
            print "InstanceClassification for %r sees no mixin or _s_attr decls; please add them or register it (nim)" \
                  % class1.__name__

        if env.debug() and not self.attrcodes_with_no_dflt and self.attrcode_dflt_pairs: #060302; doesn't get printed (good)
            print "InstanceClassification for %r: all attrs have defaults, worry about bug resetting all-default objects"\
                  % class1.__name__
        return

    def __repr__(self):
        return "<%s at %#x for %s>" % (self.__class__.__name__, id(self), self.class1.__name__)
    
    def _find_attr_decls(self, class1):
        "find _s_attr_xxx decls on class1, and process/store them"
        if self.debug_all_attrs:
            print "debug: _find_attr_decls in %s:" % (class1.__name__,)
        hmm = filter(lambda x: x.startswith("_s_"), dir(class1))
        for name in hmm:
            if name.startswith('_s_attr_'):
                attr_its_about = name[len('_s_attr_'):]
                setattr_name = '_undo_setattr_' + attr_its_about
                declval = getattr(class1, name)
                self.policies[attr_its_about] = declval #k for class1, not in general
                if self.debug_all_attrs:
                    print "  %s = %s" % (name, declval)
                self.warn = False # enough to be legitimate state
                #e check if per-instance? if callable? if legal?
                if declval in STATE_ATTR_DECLS:
                    # figure out if this attr has a known default value... in future we'll need decls to guide/override this
                    try:
                        if 'kluge': # see if this fixes some bugs... 060405 1138p
                            # for change-tracked classes, pretend there's no such thing as a default value,
                            # since i suspect some logic bugs in the dual meaning of missing state entries as dflt or dontcare.
                            if class1.__name__ in ('Atom','Bond'):
                                class1.some_attr_im_pretty_sure_it_doesnt_have
                        dflt = getattr(class1, attr_its_about)
                    except AttributeError:
                        # assume no default value unless one is declared (which is nim)
                        acode = 0 ###stub, but will work initially; later will need info about whether class is diffscanned, in layer, etc
                        if class1.__name__ in ('Atom','Bond'): ###@@@ kluge 060404, in two places
                            acode = class1.__name__
                        attrcode = (attr_its_about, acode)
                        self.attrcodes_with_no_dflt.append(attrcode)
                    else:
                        # attr has a default value.
                        # first, make sure it has no _undo_setattr_ method, since our code for those has a bug
                        # in that reset_obj_attrs_to_defaults would need to exclude those attrs, but doesn't...
                        # for more info see the comment near its call. [060404]
                        assert not hasattr(class1, setattr_name), "bug: attr with class default can't have %s too" % setattr_name
                            # this limitation could be removed when we need to, by fixing the code that calls reset_obj_attrs_to_defaults
                        acode = id(dflt) ###stub, but should eliminate issue of attrs with conflicting dflts in different classes
                            # (more principled would be to use the innermost class which changed the _s_decl in a way that matters)
                        if class1.__name__ in ('Atom','Bond'): ###@@@ kluge 060404, in two places
                            acode = class1.__name__ # it matters that this can't equal id(dflt) for this attr in some other class
                        attrcode = (attr_its_about, acode)
                        self.attrcode_dflt_pairs.append( (attrcode, dflt) )
                        self.attrcode_defaultvals[attrcode] = dflt
                        if env.debug() and is_mutable(dflt): #env.debug() (redundant here) is just to make prerelease snapshot safer
                            if env.debug():
                                print "debug warning: dflt val for %r in %r is mutable: %r" % (attr_its_about, class1, dflt)
                            pass # when we see what is warned about, we'll decide what this should do then [060302]
                                # e.g. debug warning: dflt val for 'axis' in <class jigs_motors.LinearMotor at 0x3557d50>
                                #      is mutable: array([ 0.,  0.,  0.])

                        if self.debug_all_attrs:
                            print "                                               dflt val for %r is %r" % (attrcode, dflt,)
                        pass
                    self.dict_of_all_state_attrcodes[ attrcode ] = None
                    if hasattr(class1, setattr_name):
                        self.attrcodes_with_undo_setattr[ attrcode ] = True
                        # only True, not e.g. the unbound method, since classes with this can share attrcodes, so it's just a hint
                pass
            elif name == '_s_deepcopy': # note: exact name, and doesn't end with '_'
                self.warn = False # enough to be legitimate data
            elif name == '_s_scan_children':
                pass ## probably not: self.warn = False
            elif name.startswith('_s_categorize_'):
                #060227; #e should we rename it _s_category_ ?? do we still need it, now that we have _s_attrlayer_ ? (we do use it)
                attr_its_about = name[len('_s_categorize_'):]
                declval = getattr(class1, name)
                assert type(declval) == type('category') # not essential, just to warn of errors in initial planned uses
                self.categories[attr_its_about] = declval
            elif name.startswith('_s_attrlayer_'): #060404
                attr_its_about = name[len('_s_attrlayer_'):]
                declval = getattr(class1, name)
                assert type(declval) == type('attrlayer') # not essential, just to warn of errors in initial planned uses
                self.attrlayers[attr_its_about] = declval
            else:
                print "warning: unrecognized _s_ attribute ignored:", name ##e
        return

    def attrs_declared_as(self, S_something):
        #e if this is commonly called, we'll memoize it in __init__ for each S_something
        res = []
        for attr, decl in self.policies.iteritems():
            if decl == S_something:
                res.append(attr)
        return res

    def obj_is_data(self, obj):
        "Should obj (one of our class's instances) be considered a data object?"
        return self._objs_are_data ## or hasattr(obj, '_s_deepcopy'), if we let individual instances override their classes on this
    
    def copy(self, val, func): # from outside, when in vals, it might as well be atomic! WRONG, it might add self to todo list...
        "Copy val, a (PyObject pointer to an) instance of our class"
        return val
    
    def scan_children( self, obj1, func, deferred_category_collectors = {}, exclude_layers = ()):
        "[for #doc of deferred_category_collectors, see caller docstring]"
        try:
            # (we might as well test this on obj1 itself, since not a lot slower than memoizing the same test on its class)
            method = obj1._s_scan_children # bug: not yet passing deferred_category_collectors ###@@@ [not needed for A7, I think]
        except AttributeError:
            for attr in self.S_CHILDREN_attrs:
                if self.exclude(attr, exclude_layers):
                    continue
                val = getattr(obj1, attr, None)
                cat = self.categories.get(attr) #e need to optimize this (separate lists of attrs with each cat)?
                # cat is usually None; following code works then too;
                #e future optim note: often, cat is 'selection' but val contains no objects (for attr 'picked', val is boolean)
                collector = deferred_category_collectors.get(cat) # either None, or a dict we should modify (perhaps empty now)
                if collector is not None: # can't use boolean test, since if it's {} we want to use it
                    def func2(obj):
                        ## print "collecting %r into %r while scanning %r" % (obj, cat, attr) # works [060227]
                        collector[id(obj)] = obj
                    scan_val(val, func2)
                else:
                    scan_val(val, func) # don't optimize for val is None, since it's probably rare, and this is pretty quick anyway
                #e we might optimize by inlining scan_val, though
        else:
            method(func)
        return

    def exclude(self, attr, exclude_layers):
        "Should you scan attr (of an obj of this clas), given these exclude_layers (perhaps ())?"
        return self.attrlayers.get(attr) in exclude_layers # correct even though .get is often None

    pass # end of class InstanceClassification

# == helper code  [##e all code in this module needs reordering]

known_type_copiers = {} # needs no entry for types whose instances can all be copied as themselves. Also used by is_mutable.

known_type_scanners = {} # only needs entries for types whose instances might contain (or be) InstanceType objects,
    # and which might need to be entered for finding "children" (declared with S_CHILD) -- for now we assume that means
    # there's no need to scan inside bound method objects, though this policy might change.

known_type_same_helpers = {}

# not yet needed, but let the variable exist since there's one use of it I might as well leave active (since rarely run):
copiers_for_InstanceType_class_names = {} # copier functions for InstanceTypes whose classes have certain names
    # (This is mainly for use when we can't add methods to the classes themselves.
    #  The copiers should verify the class is the expected one, and return the original object unchanged if not
    #  (perhaps with a warning), or raise an exception if they "own" the classname.)

# scanners_for_class_names would work the same way, but we don't need it yet.

_debug_deepcopy = False # initial value not used -- set to env.debug() in each run of copy_val [bruce 060311]

def copy_val(val): #bruce 060221 generalized semantics and rewrote for efficiency #bruce 060315 partly optimized env.debug() check
    """Efficiently copy a general Python value (so that mutable components are not shared with the original),
    passing Python instances unchanged, unless they define a _s_deepcopy method,
    and passing unrecognized objects (e.g. QWidgets, bound methods) through unchanged.
       (See a code comment for the reason we can't just use the standard Python copy module for this.)
    """
    global _debug_deepcopy
    _debug_deepcopy = platform.atom_debug # inlined env.debug()
        ##e ideally we'd have a recursive _copy_val_helper that doesn't check this debug flag at all
    try:
        # wware 060308 small performance improvement (use try/except); made safer by bruce, same day
        # known_type_copiers is a fixed public dictionary
        copier = known_type_copiers[type(val)]
    except KeyError:
        # we optimize by not storing any copier for atomic types.
        return val
    else:
        # assume copier is not None, since we know what's stored in known_type_copiers
        return copier(val)
    pass

def is_mutable(val): #060302 [###@@@ use this more]
    """Efficiently scan a potential argument to copy_val to see if it contains any mutable parts (including itself),
    with special cases suitable for use on state-holding attribute values for Undo,
    which might be surprising in other applications (notably, for most InstanceType objects).
       Details:
    Treat list and dict as mutable, tuple (per se) as not (but scan its components) -- all this is correct.
    Treat Numeric.array as mutable, regardless of size or type (dubious for size 0, though type and maybe shape
     could probably be changed, but this doesn't matter for now).
    Treat unknown types with known_type_copiers entries as mutable (wrong in general, ok for now,
     and might cover some of the above cases).
    Treat InstanceType objects as mutable if and only if they define an _s_deepcopy method.
    (The other ones, we're thinking of as immutable references or object pointers,
    and we don't care whether the objects they point to are mutable.)
    """
    try:
        _is_mutable_helper(val)
    except _IsMutable:
        return True
    return False

def _is_mutable_helper(val): #060303
    "[private recursive helper for is_mutable] raise _IsMutable if val (or part of it) is mutable"
    typ = type(val)
    if typ is type(()):
        # tuple is a special case -- later, make provisions for more
        for thing in val:
            _is_mutable_helper(thing)
        return
    elif typ is InstanceType:
        # another special case
        if hasattr(obj, '_s_deepcopy'):
            raise _IsMutable
        return
    else:
        copier = known_type_copiers.get(typ) # this is a fixed public dictionary
        if copier is not None:
            # all copyable types (other than those handled specially above)
            # are always mutable (since the containers themselves are) -- for now.
            # should add a way for more exceptions to register themselves. #e
            raise _IsMutable
        return # atomic or unrecognized types
    pass
    
def scan_val(val, func): 
    """Efficiently scan a general Python value, and call func on all InstanceType objects encountered
    (or in the future, on objects of certain other types, like registered new-style classes or extension classes).
       No need to descend inside any values unless they might contain InstanceType objects. Note that some InstanceType
    objects define the _s_scan_children method, but we *don't* descend into them here using that -- this is only done
    by other code, such as whatever code func might end up delivering such objects to.
       Special case: we never descend into bound method objects either (see comment on known_type_scanners
    for why).
       Return an arbitrary value which caller should not use (always None in the present implem).
    """
    typ = type(val)
    scanner = known_type_scanners.get(typ) # this is a fixed public dictionary
    if scanner is not None:
        scanner(val, func) # we optimize by not storing any scanner for atomic types, or a few others.
    return

_n_sv = _n_svh = 0

def same_vals(v1, v2): #060303
    """Efficiently scan v1 and v2 in parallel to determine whether they're the same, for purposes of undoable state
    or saved state.
       The only reason we really need this (as opposed to just using Python '==' or '!=' and our own __eq__ methods)
    is because Numeric.array.__eq__ is erroneously defined, and if we were using '==' or '!=' on a Python tuple containing 
    a Numeric array, we'd have no way of preventing this issue from making '==' or '!=' come out wrong on the tuple.
    (For details, see bruce email to 'all' of 060302, planned to be copied into code comments and/or the wiki.)
       As long as we have it, we might as well make it a bit more stringent than Python '==' in other ways too,
    like not imitating the behaviors (which are good for '==') of 1.0 == 1, array([1]) == [1], etc. The only reason
    we'll count non-identical objects as equal is that we're not interested in their addresses or in whether someone
    will change one of them and not the other (for whole objects or for their parts).
       ###doc for InstanceType... note that we get what we want by using __eq__ for the most part...
    """
    if 1:
        global _n_sv
        _n_sv += 1
    if v1 is v2:
        # Optimization:
        # this will happen in practice when whole undoable attrvals are immutable
        # (so that we're comparing originals, not different copies),
        # therefore it's probably common enough to optimize for.
        # It's just as well we're not doing it in the recursive helper,
        # since it would probably slow us down when done at every level. [060303 11pm]
        return True 
    try:
        _same_vals_helper(v1, v2)
    except _NotTheSame:
        if env.debug() and not (v1 != v2):
            print "debug warning: same_vals says False but 'not !=' says True, for",v1,v2 ###@@@ remove when pattern seen
        return False
    if env.debug() and (v1 != v2):
        print "debug warning: same_vals says True but '!=' also says True, for",v1,v2 ###@@@ remove when pattern seen
    return True

def _same_vals_helper(v1, v2): #060303
    """[private recursive helper for same_vals] raise _NotTheSame if v1 is not the same as v2
    (i.e. if their type or structure differs, or if any corresponding parts are not the same)
    """
    if 1:
        global _n_svh
        _n_svh += 1
    typ = type(v1)
    if typ is not type(v2):
        raise _NotTheSame
    same_helper = known_type_same_helpers.get(typ) # this is a fixed public dictionary
    if same_helper is not None:
        same_helper(v1, v2) # we optimize by not storing any scanner for atomic types, or a few others.
    # otherwise we assume v1 and v2 are things that can't be or contain a Numeric array, so it's sufficient to use !=.
    # (If not for Numeric arrays of type PyObject, we could safely use != right here on a pair of Numeric arrays --
    #  just not on things that might contain them, in case their type's != method used == on the Numeric arrays,
    #  whose boolean value doesn't correctly say whether they're equal (instead it says whether one or more
    #  corresponding elements are equal). Another difference is that 1 == 1.0, but we'll say those are not the same,
    #  but that aspect of our specification doesn't matter much.)
    if v1 != v2:
        raise _NotTheSame
    return    
    
known_type_copiers[type([])] = copy_list
known_type_copiers[type({})] = copy_dict
known_type_copiers[type(())] = copy_tuple

known_type_scanners[type([])] = scan_list
known_type_scanners[type({})] = scan_dict
known_type_scanners[type(())] = scan_tuple

known_type_same_helpers[type([])] = _same_list_helper
known_type_same_helpers[type({})] = _same_dict_helper
known_type_same_helpers[type(())] = _same_tuple_helper


def copy_InstanceType(obj): #e pass copy_val as an optional arg?
    # note: this shares some code with InstanceClassification  ###@@@DOIT
    # not yet needed, since QColor is not InstanceType (but keep the code here for when it is needed):
    ##copier = copiers_for_InstanceType_class_names.get(obj.__class__.__name__)
    ##    # We do this by name so we don't need to import QColor (for example) unless we encounter one.
    ##    # Similar code might be needed by anything that looks for _s_deepcopy (as a type test or to use it). ###@@@ DOIT, then remove cmt
    ##    #e There's no way around checking this every time, though we might optimize
    ##    # by storing specific classes which copy as selves into some dict;
    ##    # it's not too important since we'll optimize Atom and Bond copying in other ways.
    ##if copier is not None:
    ##    return copier(obj, copy_val) # e.g. for QColor
    try:
        deepcopy_method = obj._s_deepcopy # note: not compatible with copy.deepcopy's __deepcopy__ method
    except AttributeError:
        return obj
    res = deepcopy_method( copy_val)
    if _debug_deepcopy and (obj != res or (not (obj == res))): #bruce 060311 adding _debug_deepcopy as optim (suggested by Will)
        # Bug in deepcopy_method, which will cause false positives in change-detection in Undo (since we'll return res anyway).
        # (It's still better to return res than obj, since returning obj could cause Undo to completely miss changes.)
        #
        # Note: we require obj == res, but not res == obj (e.g. in case a fancy number turns into a plain one).
        # Hopefully the fancy object could define some sort of __req__ method, but we'll try to not force it to for now;
        # this has implications for how our diff-making archiver should test for differences. ###@@@doit

        msg = "bug: obj != res or (not (obj == res)), res is _s_deepcopy of obj; " \
              "obj is %r, res is %r, == is %r, != is %r: " % \
              (obj, res, obj == res, obj != res)

        if not env.debug():
            print msg
        else:
            print_compact_stack( msg + ": ")
            try:
                method = obj._s_printed_diff
                    # experimental (#e rename): list of strings (or so) which explain why __eq_ returns false [060306, for bug 1616]
            except AttributeError:
                pass
            else:
                print "  a reason they are not equal:\n", method(res)
        #e also print history redmsg, once per class per session?
    return res

if SAMEVALS_SPEEDUP:
    # Replace definition above with the extension's version.
    from samevals import copy_val, same_vals, setInstanceCopier, setArrayCopier
    setInstanceCopier(copy_InstanceType)
    setArrayCopier(lambda x: x.copy())

# inlined:
## def is_mutable_InstanceType(obj): 
##     return hasattr(obj, '_s_deepcopy')
  
known_type_copiers[ InstanceType ] = copy_InstanceType

def scan_InstanceType(obj, func):
    func(obj)
    #e future optim: could we change API so that apply could serve in place of scan_InstanceType?
    # Probably not, but nevermind, we'll just do all this in C.
    return None 

known_type_scanners[ InstanceType ] = scan_InstanceType

# Choice 1:
# no need for _same_InstanceType_helper; we set them up so that their __eq__ method is good enough;
# this only works if we assume that any container-like ones (which compare their parts) are ones we wrote,
# so they don't use == on Numeric arrays or != on general values...
# Choice 2:
# on naive objects, we just require id(v1) == id(v2).
### UNDECIDED. For now, doing nothing is equivalent to Choice 1.
# but note that choice 2 is probably safer.
# in fact, if I do that, i'd no longer need _eq_id_mixin just due to StateMixin. (only when __getattr__ and someone calls '==')
# [060303]
# Update 060306: some objects will need _s_same_as(self, other) different from __eq__,
# since __eq__ *might* want to compare some components with != (like int and float) rather than be as strict as same_vals.
# Even __eq__ needs to try to avoid the "Numeric array in list" bug, which in some cases will force it to also call same_vals,
# but when types are known it's plausible that it won't have to, so the distinct methods might be needed.
# When we first need _s_same_as, that will force use of a new _same_InstanceType_helper func.
# Do we need it before then? Not sure. Maybe not; need to define __eq__ better in GAMESS Jig (bug 1616) but _s_same_as
# can probably be the same method. OTOH should we let DataMixin be the thing that makes _s_same_as default to __eq__?? ###
######@@@@@@

# ==

def copy_Numeric_array(obj):
    if obj.typecode() == PyObject:
        if env.debug():
            print "atom_debug: ran copy_Numeric_array, PyObject case" # remove when works once ###@@@
        return array( map( copy_val, obj) )
            ###e this is probably incorrect for multiple dimensions; doesn't matter for now.
            # Note: We can't assume the typecode of the copied array should also be PyObject,
            # since _s_deepcopy methods could return anything, so let it be inferred.
            # In future we might decide to let this typecode be declared somehow...
##    if env.debug():
##        print "atom_debug: ran copy_Numeric_array, non-PyObject case" # remove when works once ... it did
##    if debug_dont_trust_Numeric_copy: # 060302
##        res = array( map( copy_val, list(obj)) )
##        if debug_print_every_array_passed_to_Numeric_copy and env.debug():
##            print "copy_Numeric_array on %#x produced %#x (not using Numeric.copy); input data %s" % (id(obj), id(res), obj) 
##        return res
    return obj.copy() # use Numeric's copy method for Character and number arrays ###@@@ verify ok from doc of this method...

def scan_Numeric_array(obj, func):
    if obj.typecode() == PyObject: # note: this doesn't imply each element is an InstanceType instance, just an arbitrary Python value
        if env.debug():
            print "atom_debug: ran scan_Numeric_array, PyObject case" # remove when works once ###@@@
        ## map( func, obj)
        for elt in obj:
            scan_val(elt, func) #bruce 060315 bugfix
        # is there a more efficient way?
        ###e this is probably correct but far too slow for multiple dimensions; doesn't matter for now.
##    else:
##        if env.debug():
##            print "atom_debug: ran scan_Numeric_array, non-PyObject case" # remove when works once [it did, on test values, 060314]
    return

def _same_Numeric_array_helper(obj1, obj2):
    if obj1.typecode() != obj2.typecode():
        raise _NotTheSame
    if obj1.shape != obj2.shape:
        raise _NotTheSame
    if obj1.typecode() == PyObject:
        if env.debug():
            print "atom_debug: ran _same_Numeric_array_helper, PyObject case" # remove when works once ###@@@
        # assume not multi-dimensional (if we are, this should work [untested] but it will be inefficient)
        for i in xrange(len(obj1)):
            _same_vals_helper(obj1[i], obj2[i]) # two PyObjects (if obj1 is 1-dim) or two lower-dim Numeric arrays
    else:
##        if env.debug():
##            print "atom_debug: ran _same_Numeric_array_helper, non-PyObject case" # remove when works once ###@@@
        if obj1 != obj2:
            # take pointwise !=, then boolean value of that (correct, but is there a more efficient Numeric function?)
            # note: using '==' here (and negating boolean value of result) would NOT be correct
            raise _NotTheSame
    return

try:
    from Numeric import array, PyObject
except:
    if env.debug():
        print "fyi: can't import array, PyObject from Numeric, so not registering its copy & scan functions"
else:
    numeric_array_type = type(array(range(2))) # __name__ is 'array', but Numeric.array itself is a built-in function, not a type
    assert numeric_array_type != InstanceType
    known_type_copiers[ numeric_array_type ] = copy_Numeric_array
    known_type_scanners[ numeric_array_type ] = scan_Numeric_array
    known_type_same_helpers[ numeric_array_type ] = _same_Numeric_array_helper
    _Numeric_array_type = numeric_array_type #bruce 060309 kluge, might be temporary
    del numeric_array_type # but leave array, PyObject as module globals for use by the functions above, for efficiency
    pass

# ==

def copy_QColor(obj):
    from qt import QColor
    assert obj.__class__ is QColor # might fail (in existing calls) if some other class has the same name
    if env.debug():
        print "atom_debug: ran copy_QColor" # remove when works once; will equality work right? ###@@@
    return QColor(obj)

try:
    # this is the simplest way to handle QColor for now; if always importing qt from this module
    # becomes a problem (e.g. if this module should work in environments where qt is not available),
    # make other modules register QColor with us, or make sure it's ok if this import fails
    # (it is in theory).
    from qt import QColor
except:
    if env.debug():
        print "fyi: can't import QColor from qt, so not registering its copy function"
else:
    QColor_type = type(QColor())
        # note: this is the type of a QColor instance, not of the class!
        # type(QColor) is <type 'sip.wrappertype'>, which we'll just treat as a constant,
        # so we don't need to handle it specially.
    assert QColor_type != InstanceType
    ## wrong: copiers_for_InstanceType_class_names['qt.QColor'] = copy_QColor
    known_type_copiers[ QColor_type ] = copy_QColor
    # no scanner for QColor is needed, since it contains no InstanceType objects.
    # no same_helper is needed, since '!=' will work correctly (only possible since it contains no general Python objects).
    del QColor, QColor_type
    pass

# ==

##e Do we need a copier function for a Qt event? Probably not, since they're only safe
# to store after making copies (see comments around QMouseEvent in selectMode.py circa 060220),
# and (by convention) those copies are treated as immutable.

# The reason we can't use the standard Python copy module's deepcopy function:
# it doesn't give us enough control over what it does to instances of unrecognized classes.
# For our own classes, we could do anything, but for other classes, we need them to be copied
# as the identity (i.e. as unaggressively as possible), or perhaps signalled as errors or warnings,
# but copy.deepcopy would copy everything inside them, i.e. copy them as aggressively as possible,
# and there appears to be no way around this.
#
##>>> import copy
##>>> class c:pass
##... 
##>>> c1 = c()
##>>> c2 = c()
##>>> print id(c1), id(c2)  
##270288 269568
##>>> c3 = copy.deepcopy(c1)
##>>> print id(c3)
##269968
#
# And what about the copy_reg module?... it's just a way of extending the Pickle module
# (which we also can't use for this), so it's not relevant.
#
# Notes for the future: we might use copy.deepcopy in some circumstances where we had no fear of
# encountering objects we didn't define;
# or we might write our own C/Pyrex code to imitate copy_val and friends.

# ==

# state_utils-copy_val-outtake.py went here, defined:
# class copy_run, etc
# copy_val

# ==

# state_utils-scanner-outtake.py went here, defined
# class attrlayer_scanner
# class scanner
# ##class Classifier: #partly obs? superseded by known_types?? [guess, 060221]
# ##the_Classifier = Classifier()

# ==

class objkey_allocator:
    """Use one of these to allocate small int keys (guaranteed nonzero) for objects you're willing to keep forever.
    We provide public dict attrs with our tables, and useful methods for whether we saw an object yet, etc.
       Note: a main motivation for having these keys at all is speed and space when using them as dict keys in large dicts,
    compared to python id() values. Other motivations are their uniqueness, and possible use in out-of-session encodings,
    or in other non-live encodings of object references.
    """
    def __init__(self):
        self.obj4key = {}
            # maps key to object. this is intentionally not weak-valued. It's public.
        self._key4obj = {} # maps id(obj) -> key; semiprivate
        self._lastobjkey = 0

    def clear(self):
        self.obj4key.clear()
        self._key4obj.clear()
        #e but don't change self._lastobjkey
        return
    
    def destroy(self):
        self.clear()
        self.obj4key = self._key4obj = self._lastobjkey = 'destroyed'
        return
    
    def allocate_key(self, key = None): # maybe not yet directly called; untested
        "Allocate the requested key (assertfail if it's not available), or a new one we make up, and store None for it."
        if key is not None:
            # this only makes sense if we allocated it before and then abandoned it (leaving a hole), which is NIM anyway,
            # or possibly if we use md5 or sha1 strings or the like for keys (though we'd probably first have to test for prior decl).
            # if that starts happening, remove the assert 0.
            assert 0, "this feature should never be used in current code (though it ought to work if it was used correctly)"
            assert not self.obj4key.has_key(key)
        else:
            # note: this code also occurs directly in key4obj_maybe_new, for speed
            self._lastobjkey += 1
            key = self._lastobjkey
            assert not self.obj4key.has_key(key) # different line number than identical assert above (intended)
        self.obj4key[key] = None # placeholder; nothing is yet stored into self._key4obj, since we don't know obj!
        assert key, "keys are required to be true, whether or not allocated by caller; this one is false: %r" % (key,)
        return key

    def key4obj(self, obj): # maybe not yet directly called; untested; inlined by some code
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
        assert not self.obj4key.has_key(key)
        self.obj4key[key] = obj
        self._key4obj[id(obj)] = key
        return key
    
    pass # end of class objkey_allocator

# ==

class StateSnapshot:
    """A big pile of saved (copies of) attribute values -- for each known attr, a dict from objkey to value.
    The code that stores data into one of these is the collect_state method in some other class.
    The code that applies this data to live current objects is... presently in assy_become_scanned_state
    but maybe should be a method in this class. ####@@@@
       As of 060302 we *might* (#k) require that even default or _UNSET_ attrvalues be stored explicitly, since we suspect
    not doing so can cause bugs, particularly in code to apply a state back into live objects. In future we might
    like to optimize by not storing default values; this is hard to do correctly now since they are not always
    the same for all objects in one attrdict.
    """
    #e later we'll have one for whole state and one for differential state and decide if they're different classes, etc
    def __init__(self, attrcodes = (), debugname = ""):
        self.debugname = debugname
        self.attrdicts = {} # maps attrcodes to their dicts; each dict maps objkeys to values; public attribute for efficiency(??)
        for attrcode in attrcodes:
            self.make_attrdict(attrcode)
        return
    #e methods to apply the data and to help grab the data? see also assy_become_scanned_state, SharedDiffopData (in undo_archive)
    #e future: methods to read and write the data, to diff it, etc, and state-decls to let it be compared...
    #e will __eq__ just be eq on our attrdicts? or should attrdict missing or {} be the same? guess: same.
    def make_attrdict(self, attrcode):
        "Make an attrdict for attrcode. Assume we don't already have one."
        assert self.attrdicts.get(attrcode) is None
        self.attrdicts[attrcode] = {}
    def size(self): ##e should this be a __len__ and/or a __nonzero__ method? ### shares code with DiffObj; use common superclass?
        "return the total number of attribute values we're storing (over all objects and all attrnames)"
        res = 0
        for d in self.attrdicts.itervalues():
            # <rant> Stupid Python didn't complain when I forgot to say .values(),
            # but just told me how many letters were in all the attrnames put together! </rant>
            # (Iteration over a dict being permitted is bad enough (is typing .items() so hard?!?),
            #  but its being over the keys rather than over the values is even worse. IMO.)
            res += len(d)
        return res
    def __repr__(self): #060405 changed this from __str__ to __repr__
        extra = self.debugname and " (%s)" % self.debugname or ""
        return "<%s at %#x%s, %d attrdicts, %d total values>" % \
               (self.__class__.__name__, id(self), extra, len(self.attrdicts), self.size())
##    def print_value_stats(self): # debug function, not yet needed
##        for d in self.attrdicts:
##            # (attrname in more than one class is common, due to inheritance)
##            pass # not yet needed now that I fixed the bug in self.size(), above
    def __eq__(self, other):
        "[this is used by undo_archive to see if the state has really changed]"
        # this implem assumes modtimes/change_counters are not stored in the snapshots (or, not seen by diff_snapshots)!
        return self.__class__ is other.__class__ and not diff_snapshots(self, other)
    def __ne__(self, other):
        return not (self == other)
    def val_diff_func_for(self, attrcode):
        attr, acode = attrcode
        if attr == '_posnxxx': # kluge, should use an _s_decl; remove xxx when this should be tried out ###@@@ [not used for A7]
            return val_diff_func_for__posn # stub for testing
        return None
    def extract_layers(self, layernames): #060404 first implem
        assert layernames == ('atoms',), "layernames can't be %r" % layernames #e generalize, someday
        res = self.__class__()
        for attrcode, attrdict in self.attrdicts.items():
            attr, acode = attrcode
            if acode in ('Atom','Bond'): ###@@@ kluge 060404; assume acode is class name... only true for these two classes!!
                res.attrdicts[attrcode] = self.attrdicts.pop(attrcode)
        return res
    def insert_layers(self, layerstuff): #060404 first implem
        for attrcode in layerstuff.attrdicts.keys():
            assert not self.attrdicts.has_key(attrcode), "attrcode %r overlaps, between %r and %r" % (attrcode, self, layerstuff)
        self.attrdicts.update(layerstuff.attrdicts)
        layerstuff.attrdicts.clear() # optional, maybe not even good...
        return
    pass # end of class StateSnapshot

def val_diff_func_for__posn((p1,p2), whatret): # purely a stub for testing, though it should work
    assert type(p1) is _Numeric_array_type
    assert type(p2) is _Numeric_array_type
    return p2 - p1

def diff_snapshots(snap1, snap2, whatret = 0): #060227 experimental
    "Diff two snapshots. Retval format TBD. Missing attrdicts are like empty ones. obj/attr sorting by varid to be added later."
    keydict = dict(snap1.attrdicts) # shallow copy, used only for its keys (presence of big values shouldn't slow this down)
    keydict.update(snap2.attrdicts)
    attrcodes = keydict.keys()
    del keydict
    attrcodes.sort() # just so we're deterministic
    res = {}
    for attrcode in attrcodes:
        d1 = snap1.attrdicts.get(attrcode, {})
        d2 = snap2.attrdicts.get(attrcode, {})
        # now diff these dicts; set of keys might not be the same
        dflt = _UNSET_
            # This might be correct, assuming each attrdict has been optimized to not store true dflt val for attrdict,
            # or each hasn't been (i.e. same policy for both). Also it's assumed by diff_snapshots_oneway and its caller.
            # Needs review. ##k ###@@@ [060227-28 comment]
    
        # 060309 experimental: support special diff algs for certain attrs,
        # like sets or lists, or a single attrval representing all bonds
        val_diff_func = snap2.val_diff_func_for(attrcode) # might be None; assume snap2 knows as well as snap1 what to do
        assert val_diff_func == snap1.val_diff_func_for(attrcode) # make sure snap1 and snap2 agree (kluge??)
            #e better to use more global knowledge instead? we'll see how it's needed on the diff-applying side...
            # (we ought to clean up the OO structure, when time permits)
        diff = diffdicts(d1, d2, dflt = dflt, whatret = whatret, val_diff_func = val_diff_func)
        if diff:
            res[attrcode] = diff #k ok not to copy its mutable state? I think so...
    return res # just a diff-attrdicts-dict, with no empty dict members (so boolean test works ok) -- not a Snapshot itself.

def diff_snapshots_oneway(snap1, snap2):
    "diff them, but only return what's needed to turn snap1 into snap2, as an object containing attrdicts (all mutable)"
    return DiffObj( diff_snapshots(snap1, snap2, whatret = 2) ) ######@@@@@@ also store val_diff_func per attrcode? [060309 comment]

class DiffObj:
    attrname_valsizes = dict(_posn = 52)
        # maps attrcode (just attrname for now) to our guess about the size
        # of storing one attrval for that attrcode, in this kind of undo-diff;
        # this figure 52 for _posn is purely a guess
        # (the 3 doubles themselves are 24, but they're in a Numeric array
        # and we also need to include the overhead of the entire dict item in our attrdict),
        # and the guesses ought to come from the attr decls anyway, not be
        # hardcoded here (or in future we could measure them in a C-coded copy_val).
    def __init__(self, attrdicts):
        self.attrdicts = attrdicts
    def size(self): ### shares code with StateSnapshot; use common superclass?
        "return the total number of attribute value differences we're storing (over all objects and all attrnames)"
        res = 0
        for d in self.attrdicts.itervalues():
            res += len(d)
        return res
    def RAM_usage_guess(self): #060323
        "return a rough guess of our RAM consumption"
        res = 0
        for attrcode, d in self.attrdicts.iteritems():
            attr, acode = attrcode
            valsize = self.attrname_valsizes.get(attr, 24) # it's a kluge to use attr rather than attrcode here
                # 24 is a guess, and is conservative: 2 pointers in dict item == 8, 2 small pyobjects (8 each??)
            res += len(d) * valsize
        return res
    def __len__(self):
        return self.size()
    def nonempty(self):
        return self.size() > 0
    def __nonzero__(self):
        return self.nonempty()
    pass

def diffdicts(d1, d2, dflt = None, whatret = 0, val_diff_func = None):
    ###e dflt is problematic since we don't know it here and it might vary by obj or class [not anymore, long bfr 060309; ##doc]
    """Given two dicts, return a new one with entries at keys where their values differ (according to same_vals),
    treating missing values as dflt (which is None if not provided, but many callers should pass _UNSET_).
       Values in retval depend on whatret and val_diff_func, as follows:
    If val_diff_func is None, values are pairs (v1, v2) where v1 = d1.get(key, dflt), and same for v2,
    unless we pass whatret == 1 or 2, in which case values are just v1 or just v2 respectively.
    WARNING: v1 and v2 and dflt in these pairs are not copied; retval might share mutable state with d1 and d2 values and dflt arg.
       If val_diff_func is not None, it is called with arg1 == (v1, v2) and arg2 == whatret,
    and what it returns is stored; whatever it returns needs (in the scheme this is intended for)
    to be sufficient to reconstruct v2 from v1 (for whatret == 2),
    or v1 from v2 (for whatret == 1), or both (for whatret == 0), assuming the reconstructor knows which val_diff_func was used. 
    """
    ###E maybe this dflt feature is not needed, if we already didn't store vals equal to dflt? but how to say "unset" in retval?
    # Do we need a new unique object not equal to anything else, just to use for Unset?
    # [later, 060302:] looks like this dflt is per-attrdict and always _UNSET_, but needn't be the same as a per-object one
    # that can safely be per-class. see comments elsewhere dated today.
    res = {}
    for key, v1 in d1.iteritems():
        v2 = d2.get(key, dflt)
##        if 0:
##            if v1 == v2: # optim: == will be faster than != for some of our most common values
##                pass
##            else:
##                res[key] = (v1,v2)
##        elif 0:
##            #####@@@@@ see if *this* fixes my bug... 060302 955a
##            # [it did for whole Numeric arrays, but it won't work for Numeric arrays inside tuples or lists]
##            if v1 != v2:
##                res[key] = (v1,v2)
##        else:
        if not same_vals(v1,v2):
            res[key] = (v1,v2)
    for key, v2 in d2.iteritems():
        #e (optim note: i don't know how to avoid scanning common keys twice, just to find d2-only keys;
        #   maybe copying d1 and updating with d2 and scanning that would be fastest way?
        #   Or I could copy d2 and pop it in the above loop... i'm guessing that'd be slower if this was C, not sure about Python.)
        # if d1 has a value, we handled this key already, and this is usually true, so test that first.
        if not d1.has_key(key):
            v1 = dflt
##            if v1 == v2: # same order and test as above... oops, forgot to include the above's bugfix here, until 060303 11pm!
##                pass
##            else:
##                res[key] = (v1,v2)
            if not same_vals(v1,v2):
                res[key] = (v1,v2)
    if val_diff_func is None:
        if whatret: #e should optimize by using loop variants above, instead ###@@@
            ind = whatret - 1
            for key, pair in res.iteritems():
    ##            res[key] = copy_val(pair[ind]) #KLUGE: copy_val at all (contrary to docstring) -- see if it fixes any bugs [it didn't];
                res[key] = pair[ind] #060303 11pm remove copying, no reason for it
                    # and KLUGE2 - not doing this unless whatret. [060302] results: didn't fix last night's bug.
    else:
        for key, pair in res.items():
            res[key] = val_diff_func( pair, whatret )
                #e We could optim by requiring caller to pass a func that already knows whatret!
                # or letting whatrets 0,1,2 be special cases of val_diff_func (same idea), which takes (v1,v2) to what we want.
                # or just letting whatret be either 0,1,2, or a function.
                #    But these optims are not needed, since the idea is to use this on a small number of attrvals with lots of data in
                # each one (not just on a small number of attr *names*, but a small number of *values*). E.g. one attr for the entire
                # assy which knows all atom positions or bond types in the assy. It's just a way of letting some attrs have their
                # own specialcase diff algs and representations.
                # [later note: as of 060330 this val_diff_func is only supplied by val_diff_func_for, which never supplies one
                #  except for a stub attrname we don't use, and I don't know if we'll use this scheme for A7.]
    return res

# ==

def priorstate_debug(priorstate, what = ""): #e call it, and do the init things
    "call me only to print debug msgs"
    ###@@@ this is to help me zap the "initial_state not being a StatePlace" kluges;
    # i'm not sure where the bad ones are made, so find out by printing the stack when they were made.
    try:
        stack = priorstate._init_stack # compact_stack(), saved by __init__, for StatePlace and StateSnapshot
    except:
        print "bug: this has no _init_stack: %r" % (priorstate,)
    else:
        if not env.seen_before( ("ghjkfdhgjfdk" , stack) ):
            print "one place we can make a %s priorstate like %r is: %s" % (what, priorstate, stack)
    return

def diff_and_copy_state(archive, assy, priorstate): #060228 
    "Return a StatePlace which presently owns the CurrentStateCopy but is willing to give it up when this is next called... #doc"
    # background: we keep a mutable snapshot of the last checkpointed state. right now it's inside priorstate (and defines
    # that immutable-state-object's state), but we're going to grab it out of there and modify it to equal actual current state
    # (as derived from assy using archive), and make a diffobject which records how we had to change it. Then we'll donate it
    # to a new immutable-state-object we make and return (<new>). But we don't want to make priorstate unusable
    # or violate its logical immutability, so we'll tell it to define itself (until further notice) based on <new> and <diffobj>.

    assert isinstance( priorstate, StatePlace) # remove when works, eventually ###@@@
    
    new = StatePlace() # will be given stewardship of our maintained copy of almost-current state, and returned
    # diffobj is not yet needed now, just returned from diff_snapshots_oneway:
    ## diffobj = DiffObj() # will record diff from new back to priorstate (one-way diff is ok, if traversing it also reverses it)
    steal_lastsnap_method = priorstate.steal_lastsnap
    lastsnap = steal_lastsnap_method( ) # and we promise to replace it with (new, diffobj) later, so priorstate is again defined
    assert isinstance(lastsnap, StateSnapshot) # remove when works, eventually ###@@@
    # now we own lastsnap, and we'll modify it to agree with actual current state, and record the changes required to undo this...
    # 060329: this (to end of function) is where we have to do things differently when we only want to scan changed objects.
    # So we do the old full scan for most kinds of things, but not for the 'atoms layer' (atoms, bonds, Chunk.atoms attr).
    import undo_archive #e later, we'll inline this until we reach a function in this file
    cursnap = undo_archive.current_state(archive, assy, use_060213_format = True, exclude_layers = ('atoms',))
    lastsnap_diffscan_layers = lastsnap.extract_layers( ('atoms',) )
    diffobj = diff_snapshots_oneway( cursnap, lastsnap ) # valid for everything except the 'atoms layer'
    ## lastsnap.become_copy_of(cursnap) -- nevermind, just use cursnap
    lastsnap = cursnap
    del cursnap

    modify_and_diff_snap_for_changed_objects( archive, lastsnap_diffscan_layers, ('atoms',), diffobj ) #060404
    
    lastsnap.insert_layers(lastsnap_diffscan_layers)
    new.own_this_lastsnap(lastsnap)
    priorstate.define_by_diff_from_stateplace(diffobj, new)        
    new.really_changed = not not diffobj.nonempty() # remains correct even when new's definitional content changes
    return new

def modify_and_diff_snap_for_changed_objects( archive, lastsnap_diffscan_layers, layers, diffobj ): #060404
    #e rename lastsnap_diffscan_layers
    """[this might become a method of the undo_archive; it will certainly be generalized, as its API suggests]
    - Get sets of changed objects from (our subs to) global changedicts, and clear those.
    - Use those to modify lastsnap_diffscan_layers to cover changes tracked
      in the layers specified (for now only 'atoms' is supported),
    - and record the diffs from that into diffobj.
    """
    assert len(layers) == 1 and layers[0] == 'atoms' # this is all that's supported for now
    # Get the sets of possibly changed objects... for now, this is hardcoded as 2 dicts, for atoms and bonds,
    # keyed by atom.key and id(bond), and with changes to all attrs lumped together (though they're tracked separately);
    # these dicts sometimes also include atoms & bonds belonging to other assys, which we should ignore.
    # [#e Someday we'll need to generalize this --
    #  how will we know which (or how many) dicts to look in, for changed objs/attrs?
    #  don't the attr decls that set up layers also have to tell us that?
    #  and does that get recorded somehow in this lastsnap_diffscan_layers object,
    #  which knows the attrs it contains? yes, that would be good... for some pseudocode
    #  related to this, see commented-out method xxx, just below.]
    chgd_atoms, chgd_bonds = archive.get_and_clear_changed_objs()
    if env.debug():
        print "\nchanged objects: %d atoms, %d bonds" % (len(chgd_atoms), len(chgd_bonds))
    # discard wrong assy atoms... can we tell by having an objkey? ... imitate collect_s_children and (mainly) collect_state
    keyknower = archive.objkey_allocator
    _key4obj = keyknower._key4obj
    changed_live = {} # both atoms & bonds; we'll classify, so more general (for future subclasses); not sure this is worth it
    changed_dead = {} 
    for akey, obj in chgd_atoms.iteritems():
        # akey is atom.key, obj is atom
        key = _key4obj.get(id(obj)) # inlined keyknower.key4obj; key is objkey, not atom.key
        if key is None:
            # discard obj unless it's ours; these submethods are also allowed to say 'no' for dead objs, even if they're one of ours
            if archive.new_Atom_oursQ(obj):
                key = 1 # kluge, only truth value matters; or we could allocate the key and use that, doesn't matter for now
        if key:
            if archive.trackedobj_liveQ(obj):
                changed_live[id(obj)] = obj
            else:
                changed_dead[id(obj)] = obj                
    for idobj, obj in chgd_bonds.iteritems():
        key = _key4obj.get(idobj)
        if key is None:
            if archive.new_Bond_oursQ(obj):
                key = 1
        if key:
            if archive.trackedobj_liveQ(obj):
                changed_live[id(obj)] = obj
            else:
                changed_dead[id(obj)] = obj                
    ## print "changed_live = %s, changed_dead = %s" % (changed_live,changed_dead)
    key4obj = keyknower.key4obj_maybe_new
    diff_attrdicts = diffobj.attrdicts
    for attrcode in archive.obj_classifier.dict_of_all_state_attrcodes.iterkeys():
        if attrcode[1] in ('Atom','Bond'):
            diff_attrdicts.setdefault(attrcode, {}) # this makes some diffs too big, but speeds up our loops ###k is it ok??
            # if this turns out to cause trouble, just remove these dicts at the end if they're still empty
    state_attrdicts = lastsnap_diffscan_layers.attrdicts
    objclsfr = archive.obj_classifier
    ci = objclsfr.classify_instance
    # warning: we now have 3 similar but not identical 'for attrcode' loop bodies,
    # handling live/dflt, live/no-dflt, and dead.
    for idobj, obj in changed_live.iteritems(): # similar to obj_classifier.collect_state
        key = key4obj(obj)
        clas = ci(obj) #e could heavily optimize this if we kept all leaf classes separate; probably should
        for attrcode, dflt in clas.attrcode_dflt_pairs:
            attr, acode_junk = attrcode
            ## state_attrdict = state_attrdicts[attrcode] #k if this fails, just use setdefault with {} [it did; makes sense]
            ## state_attrdict = state_attrdicts.setdefault(attrcode, {})
            state_attrdict = state_attrdicts[attrcode] # this should always work now that _archive_meet_class calls classify_class
                ##e could optim by doing this before loop (or on archive init?), if we know all changetracked classes (Atom & Bond)
            val = getattr(obj, attr, dflt)
            if val is dflt:
                val = _UNSET_ # like collect_state; note, this is *not* equivalent to passing _UNSET_ as 3rd arg to getattr!
            oldval = state_attrdict.get(key, _UNSET_) # see diffdicts and its calls, and apply_and_reverse_diff
                # if we knew they'd be different (or usually different) we'd optim by using .pop here...
                # but since we're lumping together all attrs when collecting changed objs, these vals are usually the same
            if not same_vals(oldval, val):
                # a diff! put a copy of val in state, and oldval (no need to copy) in the diffobj
                if val is _UNSET_: # maybe this is not possible, it'll be dflt instead... i'm not positive dflt can't be _UNSET_, tho...
                    state_attrdict.pop(key, None) # like del, but works even if no item there ###k i think this is correct
                else:
                    state_attrdict[key] = copy_val(val)
                diff_attrdicts[attrcode][key] = oldval
        dflt = None; del dflt
        for attrcode in clas.attrcodes_with_no_dflt:
            attr, acode_junk = attrcode
            state_attrdict = state_attrdicts[attrcode]
            val = getattr(obj, attr, _Bugval)
            oldval = state_attrdict.get(key, _UNSET_) # not sure if _UNSET_ can happen, in this no-dflt case
            if not same_vals(oldval, val):
                state_attrdict[key] = copy_val(val)
                try:
                    diff_attrdict = diff_attrdicts[attrcode]
                except:
                    print "it failed, keys are",diff_attrdicts.keys() ####@@@@ should not happen anymore
                    print " and state ones are",state_attrdicts.keys()
                    ## sys.exit(1)
                    diff_attrdict = diff_attrdicts[attrcode] = {}
                diff_attrdict[key] = oldval #k if this fails, just use setdefault with {} 
        attrcode = None; del attrcode
    for idobj, obj in changed_dead.iteritems():
        #e if we assumed these all have same clas, we could invert loop order and heavily optimize
        key = key4obj(obj)
        clas = ci(obj)
        for attrcode in clas.dict_of_all_state_attrcodes.iterkeys():
            # (this covers the attrcodes in both clas.attrcode_dflt_pairs and clas.attrcodes_with_no_dflt)
            attr, acode_junk = attrcode
            state_attrdict = state_attrdicts[attrcode]
            val = _UNSET_ # convention for dead objects
            oldval = state_attrdict.pop(key, _UNSET_) # use pop because we know val is _UNSET_
            if oldval is not val:
                diff_attrdicts[attrcode][key] = oldval
        attrcode = None; del attrcode
    if 1:
        from undo_archive import _undo_debug_obj, _undo_debug_message
        obj = _undo_debug_obj
        if id(obj) in changed_dead or id(obj) in changed_live:
            # this means obj is not None, so it's ok to take time and print things
            key = _key4obj.get(id(obj))
            if key is not None:
                for attrcode, attrdict in diff_attrdicts.iteritems():
                    if attrdict.has_key(key):
                        _undo_debug_message( "diff for %r.%s gets %r" % (obj, attrcode[0], attrdict[key]) )
                #e also for old and new state, i guess, and needed in apply_and_reverse_diff as well
        pass
    return # from modify_and_diff_snap_for_changed_objects
    
#e for the future, this pseudocode is related to how to generalize the use of chgd_atoms, chgd_bonds seen above.
##def xxx( archive, layers = ('atoms',) ): #bruce 060329; is this really an undo_archive method? 
##    # ok, we've had a dict subscribed for awhile (necessarily), just update it one last time, then we have the candidates, not all valid.
##    # it's sub'd to several things... which somehow reg'd themselves in the 'atoms' layer...
##    for layer in layers: # perhaps the order matters, who knows
##        #e find some sort of object which knows about that layer; do we ask our obj_classifier about this? does it last per-session?
##        # what it knows is the changedict_processors, and a dict we have subscribed to them...
##        # hmm, who owns this dict? the archive? i suppose.
##        layer_obj = archive.layer_obj(layer)##@@ IMPLEM
##        layer_obj.update_your_changedicts()##@@ IMPLEM
##        layer_obj.get_your_dicts() # ....
##    # ...
##    return

# ==

class StatePlace:
    """basically an lval for a StateSnapshot or a (diffobj, StatePlace) pair;
    represents a logically immutable snapshot in a mutable way
    """
    # WARNING: as of 060309 callers have a kluge that will break if anything sets the attr 'attrdicts' in this object. ##@@ fix
    # update 060407: I think this was mostly fixed earlier today, but not entirely -- the only vestige of the problem
    # is some compatibility try/except code, looking for something like data.attrdicts, which should never be needed anymore i think,
    # but it's still there and still means we'd better not have that attr here until it's removed.
    def __init__(self, lastsnap = None):
        self.lastsnap = lastsnap # should be None or a mutable StateSnapshot
        self.diff_and_place = None
        return
    def own_this_lastsnap(self, lastsnap):
        assert self.lastsnap is None
        assert self.diff_and_place is None
        assert lastsnap is not None
        self.lastsnap = lastsnap
        return
    def define_by_diff_from_stateplace(self, diff, place):
        assert self.lastsnap is None
        assert self.diff_and_place is None
        self.diff_and_place = (diff, place)
    def steal_lastsnap(self):
        assert self.lastsnap is not None
        res = self.lastsnap
        self.lastsnap = None
        return res
    #e methods for pulling the snap back to us, too... across the pointer self.diff_and_place, i guess
    def get_snap_back_to_self(self):
        "[recursive (so might not be ok in practice)]"
        # predicted bug if we try this on the initial state, so, need caller to use StatePlace there ####@@@@
        # (this bug never materialized, but I don't know why not!!! [bruce 060309])
        # sanity check re that:
        if 0 and env.debug(): #060309
            print "debug: fyi: calling get_snap_back_to_self", self
                # note: typically called twice per undoable command --
                # is this due to (guess no) begin and end cp, or (guess yes) one recursive call??
        if self.lastsnap is None:
            diff, place = self.diff_and_place
            self.diff_and_place = None
            # now, we need to get snap into place (the recursive part), then steal it, apply & reverse diff, store stuff back
            place.get_snap_back_to_self() # permits steal_lastsnap to work on it
            lastsnap = place.steal_lastsnap()
            apply_and_reverse_diff(diff, lastsnap) # note: modifies diff and lastsnap in place; no need for copy_val
            place.define_by_diff_from_stateplace(diff, self) # place will now be healed as soon as we are
            self.lastsnap = lastsnap # inlined self.own_this_lastsnap(lastsnap)
        return
    #e and for access to it, for storing it back into assy using archive
    def get_attrdicts_for_immediate_use_only(self): # [renamed, 060309]
        "Warning: these are only for immediate use without modification!"
        self.get_snap_back_to_self()
        return self.lastsnap.attrdicts
    def _relative_RAM(self, priorplace): #060323
        """Return a guess about the RAM requirement of retaining the diff data to let this state
        be converted (by Undo) into the state represented by priorplace, also a StatePlace (??).
        Temporary kluge: this must only be called at certain times, soon after self finalized... not sure of details.
        """
        return 18 # stub
    pass # end of class StatePlace

def apply_and_reverse_diff(diff, snap):
    """Given a DiffObj (format TBD) <diff> and a StateSnapshot <snap> (mutable), modify <snap> by applying <diff> to it,
    at the same time recording the values kicked out of <snap> into <diff>, turning it into a reverse diff.
    Return None, to remind caller we modify our argument objects.
    (Note: Calling this again on the reverse diff we returned and on the same now-modified snap should undo its effect entirely.)
    """
    for attrcode, dict1 in diff.attrdicts.items():
        dictsnap = snap.attrdicts.setdefault(attrcode, {})
        if 1:
            # if no special diff restoring func for this attrcode:
            for key, val in dict1.iteritems():
                # iteritems is ok, though we modify dict1, since we don't add or remove items (though we do in dictsnap)
                oldval = dictsnap.get(key, _UNSET_)
                if val is _UNSET_:
                    del dictsnap[key] # always works, or there was no difference in val at this key!
                    # note: if dictsnap becomes empty, nevermind, it's ok to just leave it that way.
                else:
                    dictsnap[key] = val
                dict1[key] = oldval
                    # whether or not oldval is _UNSET_, it indicates a diff, so we have to retain the item
                    # in dict1 or we'd think it was a non-diff at that key!
        else:
            pass # this is WHERE I AM 060309 3:39pm. problem: this produces a val, ready to setattr into an object,
            # but what we need is to be able to do that setattr or actually modify_attr ourselves. hmm.
            # should we store smth that can be used to do it? not so simple i think... or at least less general
            # than it would appear... let's see how this is called. similar issues exist on the scanning side
            # (swept under the rug so far, due to what's still nim).
            #
            #   maybe think from other end -- what _s_attr decls
            # do we want, for being able to set this up the way we'd like?
            # Maybe per-object diff & copy func, for obj owning attrcode's attr, and per-object apply_and_reverse func?
            #  Related (but purely an A8 issue): for binary mmp support, we still need to be able to save the snaps!
            #
            # ... this is called by get_snap_back_to_self, in get_attrdicts_for_immediate_use_only,
            # in assy_become_scanned_state, in assy_become_state (undo_archive func), from assy.become_state,
            # in SimpleDiff.apply_to. In theory, get_snap_back_to_self can pull it over multiple diffs,
            # though in practice, it won't until we merge diffs. So would it work if the snap, for these attrs,
            # was stored in the current state of the objects??
            # ... Hmm, maybe it could work by creating snap-exprs consisting of "cur state plus these diffs"
            # which then get stored by applying the diffs, maybe compressing them together as the expr is built?
            #
    return

# ==

# Terminology/spelling note: in comments, we use "class" for python classes, "clas" for Classification objects.
# In code, we can't use "class" as a variable name (since it's a Python keyword),
# so we might use "clas" (but that's deprecated since we use it for Classification objects too),
# or "class1", or something else.

class obj_classifier: 
    """Classify objects seen, and save the results, and provide basic uses of the results for scanning.
    Probably can't yet handle "new-style" classes. Doesn't handle extension types (presuming they're not InstanceTypes) [not sure].
       Note: the amount of data this stores is proportional to the number of classes and state-holding attribute declarations;
    it doesn't (and shouldn't) store any per-object info. I.e. it soon reaches a small fixed size, regardless of number of objects
    it's used to classify.
    """
    def __init__(self):
        self._clas_for_class = {} # maps Python classes (values of obj.__class__ for obj an InstanceType, for now) to Classifications
        self.dict_of_all_state_attrcodes = {} # maps attrcodes to arbitrary values, for all state-holding attrs ever declared to us
        self.attrcodes_with_undo_setattr = {} # see doc in clas
        return
    
    def classify_instance(self, obj):
        """Obj is known to be of InstanceType. Classify it (memoizing classifications per class when possible).
        It might be a StateHolder, Data object, or neither.
        """
        class1 = obj.__class__
        try:
            # easy & usual case: we recognize that __class__ -- just return the memoized answer.
            # (Only correct if that class doesn't declare to us that we need to redo this per-object, but such a decl is nim.)
            # (This is redundant with the same optimization in classify_class, which needs it for direct calls, but that doesn't matter.)
            # (This is probably fast enough that we don't need to bother storing a map from id(obj) or objkey directly to clas,
            #  which might slow us down anyway by using more memory.)
            # (#e future optim, though: perhaps store clas inside the object, and also objkey, as special attrs)
            return self._clas_for_class[class1]
        except KeyError:
            pass
        return self.classify_class(class1)
        
    def classify_class(self, class1):
        """Find or make (and return) an InstanceClassification for this class;
        if you make it, memoize it and record info about its attr decls.
        """
        try:
            return self._clas_for_class[class1] # redundant when called from classify_instance, but needed for direct calls
        except KeyError:
            pass
        clas = self._clas_for_class[class1] = InstanceClassification(class1)
        self.dict_of_all_state_attrcodes.update( clas.dict_of_all_state_attrcodes )
        self.attrcodes_with_undo_setattr.update( clas.attrcodes_with_undo_setattr )
#bruce 060330 not sure if the following can be fully zapped, though most of it can. Not sure how "cats" are used yet...
# wondering if acode should be classname. ###@@@
# ... ok, most of it can be zapped; here's enough to say what it was about:
##        # Store per-attrdict metainfo, which in principle could vary per-class but should be constant for one attrdict.
#....
##                self.kluge_attr2metainfo[attr] = attr_metainfo
##                self.kluge_attr2metainfo_from_class[attr] = clas # only for debugging
        return clas
    
    def collect_s_children(self, val, deferred_category_collectors = {}, exclude_layers = ()): #060329/060404 added exclude_layers
        """Collect all objects in val, and their s_children, defined as state-holding objects
        found (recursively, on these same objects) in their attributes which were
        declared S_CHILD or S_CHILDREN or S_CHILDREN_NOT_DATA using the state attribute decl system... [#doc that more precisely]
        return them as the values of a dictionary whose keys are their python id()s.
           Note: this scans through "data objects" (defined as those which define an '_s_deepcopy' method)
        only once, but doesn't include them in the return value. This is necessary (I think) because
        copy_val copies such objects. (Whether it's optimal is not yet clear.)
           If deferred_category_collectors is provided, it should be a dict from attr-category names
        (e.g. 'selection', 'view') to usually-empty dicts, into which we'll store id/obj items
        which we reach through categorized attrs whose category names it lists, rather than scanning them
        recursively as usual. (Note that we still scan the attr values, just not the objects found only inside them.)
           If we reach one object along multiple attr-paths with different categories,
        we decide what to do independently each time (thus perhaps recursivly scanning the same object
        we store in a dict in deferred_category_collectors, or storing it in more than one of those dicts).
        Caller should ignore such extra object listings as it sees fit. 
        """ 
        #e optimize for hitting some children lots of times, by first storing on id(obj), only later looking up key (if ever).
        saw = {}
        def func(obj):
            saw[id(obj)] = obj
        scan_val(val, func)
        # now we have some objects to classify and delve into.
        # for each one, we call this (more or less) on val of each child attribute.
        # but we need to do this in waves so we know when we're done. and not do any obj twice.
        # (should we detect cycles of children, which is presumably an error? not trivial to detect, so no for now.)
        # ... this is just transitive closure in two steps, obj to some vals, and those vals scanned (all together).
        # So write the obj to "add more objs to a dict" func. then pass it to a transclose utility, which takes care
        # of knowing which objs are seen for first time.
        data_objs = {}
        # optimized attr accesses: [060315]
        env_debug = env.debug()
        classify_instance = self.classify_instance
        def obj_and_dict(obj1, dict1): #e rename
            """pass me to transclose; I'll store objs into dict1 when I reach them from a child attribute of obj; all objs are
            assumed to be instances of the kind acceptable to classify_instance.
            """
            # note, obj1 might be (what we consider) either a StateHolder or a Data object (or neither).
            # Its clas will know what to do.
            if env_debug:
                #bruce 060314: realized there was a bug in scan_val -- it stops at all elements of lists, tuples, and dicts,
                # rather than recursing as intended and only stopping at InstanceType objects.
                # (copy_val and same_vals (py implems anyway) don't have this bug.)
                # Does this happen in practice in Undo, or do we so far only store child objs 1 level deep in lists or dicts?
                # (Apparently it never happens, since following debug code doesn't print anything.)
                # What would the following code do if it happened?
                # Would it be most efficient/flexible/useful to decide this is a good feature of scan_val,
                # and make this code tolerate it?
                #bruce 060315: decided to fix scan_val.
                ##k Once this is tested, should this check depend on atom_debug?
                # Maybe in classify_instance? (Maybe already there?) ###@@@
                if type(obj1) is not InstanceType: ## in ( types.ListType, types.DictType ):
                    print "debug: bug? scan_children hit obj at %#x of type %r" % (id(obj1), type(obj1)) ####@@@@
            clas = classify_instance(obj1)
            if clas.obj_is_data(obj1):
                data_objs[id(obj1)] = obj1
            def func(obj):
                dict1[id(obj)] = obj
            clas.scan_children( obj1, func,   #k is scan_children correct for obj1 being data?
                                deferred_category_collectors = deferred_category_collectors,
                                exclude_layers = exclude_layers )
        allobjs = transclose( saw, obj_and_dict) #e rename both args
        if 0 and env.debug(): 
            print "atom_debug: collect_s_children had %d roots, from which it reached %d objs, of which %d were data" % \
                  (len(saw), len(allobjs), len(data_objs))
        # allobjs includes both state-holding and data-holding objects. Remove the latter.
        for key in data_objs.iterkeys():
            del allobjs[key]
        return allobjs # from collect_s_children

    def collect_state(self, objdict, keyknower, exclude_layers = ()): #060329/060404 added exclude_layers
        """Given a dict from id(obj) to obj, which is already transclosed to include all objects of interest,
        ensure all these objs have objkeys (allocating them from keyknower (an objkey_allocator instance) as needed),
        and grab the values of all their state-holding attrs,
        and return this in the form of a StateSnapshot object.
        #e In future we'll provide a differential version too.
        """
        key4obj = keyknower.key4obj_maybe_new # or our arg could just be this method
        attrcodes = self.dict_of_all_state_attrcodes.keys()
        if exclude_layers:
            assert exclude_layers == ('atoms',) # the only one we support right here
            attrcodes = filter( lambda (attr, acode): acode not in ('Atom','Bond'), attrcodes )
                # this is required, otherwise insert_layers (into this) will complain about these layers already being there
        snapshot = StateSnapshot(attrcodes)
            # make a place to keep all the values we're about to grab
        attrdicts = snapshot.attrdicts
        len1 = len(objdict)
        for obj in objdict.itervalues():
            key = key4obj(obj)
            clas = self.classify_instance(obj)
            if 'KLUGE': ###@@@ remove when works, at least once this code is debugged; safe for A7
                if exclude_layers:
                    assert exclude_layers == ('atoms',) # the only one we support right here
                    if not ( clas.class1.__name__ not in ('Atom','Bond') ):
                        print "bug: exclude_layers didn't stop us from seeing", obj
            # hmm, use attrs in clas or use __dict__? Either one might be way too big... start with smaller one? nah. guess.
            # also we might as well use getattr and be more flexible (not depending on __dict__ to exist). Ok, use getattr.
            # Do we optim dflt values of attrs? We ought to... even when we're differential, we're not *always* differential.
            ###e need to teach clas to know those, then.
            for attrcode, dflt in clas.attrcode_dflt_pairs: # for attrs holding state (S_DATA, S_CHILD*, S_PARENT*, S_REF*) with dflts
                attr, acode_junk = attrcode
                if clas.exclude(attr, exclude_layers):
                    if env.debug():###@@@ rm when works
                        print "debug: collect_state exclude_layers1 excludes",attr,"of",obj
                    continue
                val = getattr(obj, attr, dflt)
                # note: this dflt can depend on key -- no need for it to be the same within one attrdict,
                # provided we have no objects whose attrs all have default values and all equal them at once [060302]
                if val is not dflt: # it's important in general to use 'is' rather than '==' (I think), e.g. for different copies of {}
                    # We might need to store a copy of val, or we might not if val == dflt and it's not mutable.
                    # There's no efficient perfect test for this, and it's not worth the runtime to even guess it,
                    # since for typical cases where val needn't be stored, val is dflt since instance didn't copy it.
                    # (Not true if Undo stored the val back into the object, but it won't if it doesn't copy it out!)
                    attrdicts[attrcode][key] = copy_val(val)
            for attrcode in clas.attrcodes_with_no_dflt:
                # (This kind of attr might be useful when you want full dicts for turning into Numeric arrays later. Not sure.)
                # Does that mean the attr must always exist on obj? Or that we should "store its nonexistence"?
                # For simplicity, I hope latter case can always be thought of as the attr having a default.
                # I might need a third category of attrs to pull out of __dict__.get so we don't run __getattr__ for them... ##e
                #val = getattr(obj, attr)
                #valcopy = copy_val(val)
                #attrdict = attrdicts[attr]
                #attrdict[key] = valcopy
                attr, acode_junk = attrcode
                if clas.exclude(attr, exclude_layers):
                    if env.debug():###@@@ rm when works
                        print "debug: collect_state exclude_layers2 excludes",attr,"of",obj
                    continue
                attrdicts[attrcode][key] = copy_val(getattr(obj, attr, _Bugval))
                    # We do it all in one statement, for efficiency in case compiler is not smart enough to see that local vars
                    # would not be used again; it might even save time due to lack of bytecodes to update linenumber
                    # to report in exceptions! (Though that will make bugs harder to track down, if exceptions occur.)
                    #
                    #bruce 060311 adding default of Bugval to protect us from bugs (nonexistence of attr) without entirely hiding
                    # them. In theory, if this ever happens in correct code, then this attrval (or whether it's set) shouldn't matter.
                    # I want to use something recognizable, but not _UNSET_ since that would (I think) conflict with its meaning
                    # in diffs (not sure). If it turns out this is not always a bug, I can make this act similarly to _UNSET_
                    # in that, when storing it back, I can unset the attr (this would make Undo least likely to introduce a bug).
                    # I'm not yet doing that, but I added a comment mentioning _Bugval next to the relevant setattr in undo_archive.py.
        len2 = len(objdict)
        if len1 != len2:
            # this should be impossible
            print "bug: collect_state in %r sees objdict (id %#x) modified during itervalues (len %d -> %d)" % \
                  (self, id(objdict), len1, len2)
        if 0 and env.debug():
            print "atom_debug: collect_state got this snapshot:", snapshot
##            if 1: #####@@@@@
##                snapshot.print_value_stats() # NIM
        return snapshot # from collect_state

    def reset_obj_attrs_to_defaults(self, obj):
        """Given an obj we have saved state for, reset each attr we might save
        to its default value (which might be "missing"??), if it has one.
        [#e someday we might also reset S_CACHE attrs, but not for now.]
        """
        from undo_archive import _undo_debug_obj, _undo_debug_message
        clas = self.classify_instance(obj)
        for (attr, acode_junk), dflt in clas.attrcode_dflt_pairs:
            if obj is _undo_debug_obj:
                _undo_debug_message("undo/redo: reset dflt %r.%s = %r" % (obj, attr, dflt))
            setattr(obj, attr, dflt) #e need copy_val? I suspect not, so as of 060311 1030pm PST I'll remove it as an optim.
            # [060302: i think copy_val is not needed given that we only refrain from storing val when it 'is' dflt,
            #  but i think it's ok unless some classes depend on unset attrs being a mutable shared class attr,
            #  which I think is bad enough style that we can safely say we don't support it (though detecting the danger
            #  would be nice someday #e).]
            #e save this for when i have time to analyze whether it's safe:
            ## delattr(obj, attr) # save RAM -- ok (I think) since the only way we get dflts is when this would work... not sure
        # not needed: for attr in clas.attrcodes_with_no_dflt: ...
        return
    
    pass # end of class obj_classifier, if we didn't rename it by now

# ==

class StateMixin( _eq_id_mixin_ ):
    """Convenience mixin for classes that contain state-attribute decls,
    to help them follow the rules for __eq__,
    to avoid debug warnings when they contain no attr decls yet,
    and perhaps to provide convenience methods (none are yet defined).
    """
    # try not having this:
    ## _s_attr__StateMixin__fake = S_IGNORE
        # decl for fake attr __fake (name-mangled to _StateMixin__fake to be private to this mixin class),
        # to avoid warnings about classes with no declared state attrs without requiring them to be registered (which might be nim)
        # (which is ok, since if you added this mixin to them, you must have thought about
        #  whether they needed such decls)
    def _undo_update(self):
        "#doc [see docstring in chunk]"
        return
    pass

class DataMixin:
    """Convenience mixin for classes that act as "data" when present
    in values of declared state-holding attributes. Provides method stubs
    to remind you when you haven't declared a necessary method. (not sure this is good)
    Makes sure state system treats this object as data (and doesn't warn about it).
       Note: it's not obligatory for data-like classes to inherit this, and as of 060302
    I think none of them do (though maybe they should, to serve as examples #e). To find the
    classes that are officially treated as data by Undo and other state_utils features,
    search for _s_deepcopy methods.
    """
    def _s_deepcopy(self, copyfunc): # note: presence of this method makes sure this object is treated as data.
        "#doc [doc available in other implems of this method, and/or its calls; implem must be compatible with __eq__]"
        print "_s_deepcopy needs to be overridden in", self
        print "  (implem must be compatible with __eq__)"
        return self
    def __eq__(self, other):
        print "__eq__ needs to be overridden in", self ### don't put this mixin into Gamess til I test lack of __eq__ there
        print "  (implem must be compatible with _s_deepcopy; don't forget to avoid '==' when comparing Numeric arrays)"
        return self is other
    def __ne__(self, other):
        return not (self == other) # this uses the __eq__ above, or one which the main class defined
    pass

# == test code

def _test():
    print "testing some simple cases of copy_val"
    from Numeric import array
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
