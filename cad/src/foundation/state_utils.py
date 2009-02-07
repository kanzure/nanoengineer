# Copyright 2005-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
state_utils.py - general state-related utilities, and undo-related uses of them.

@author: Bruce
@version: $Id$
@copyright: 2005-2009 Nanorex, Inc.  See LICENSE file for details.

Note: same_vals was moved from here into a new file, utilities/Comparison.py,
to break an import cycle. It is closely related to copy_val which remains here.

TODO:

- Move some of this code into undo_archive, or to methods on one of those,
and/or some code from there to here, so that this module no longer
needs to import undo_archive.
[bruce 071025 suggestion, echoing older comments herein]


DISCUSSION of general data handling functions, their C extensions,
their relation to Undo, and their relation to new-style classes
[bruce 090205/090206]:

There are four general data-handling functions, which might be used on
any data value found in undoable state or model state:

- same_vals

- copy_val

- scan_vals

- is_mutable

These functions need to handle many Python builtin types and extension types,
as well as our own classes, old style or new style. They each use lookup tables
by type, and for class instances (old style or new style), we define special
APIs by which classes can customize their behavior regarding these functions.

There is also type-specific code in Undo other than just calls to those
functions.

We have a C extension module, samevals.pyx / samevalshelp.c, which defines
optimized C versions of same_vals and copy_val.

We have an experimental C extension module which causes classes Atom and Bond
(normally old-style) to be Python extension classes (new-style).

The customization/optimization system for all those functions relies on looking
up an object's type to find hardcoded cases, and in some cases testing it for
equalling InstanceType (for old-style class instances) or for the object
being an instance of InstanceLike (for new-style class instances). (The class
of a new style instance is also its type, but we don't take advantage of that
to optimize by memoizing the classes in the hardcoded-type dicts, since we
presume the isinstance test is fast enough. If we later want to change that,
we can make the C code directly access the same per-type dicts that the Python
code both accesses and maintains.)

This is being revised (supposedly done as of 090206, but not fully tested) so that
new-style classes are also handled if they define appropriate methods and/or
inherit from a new superclass InstanceLike (which StateMixin and DataMixin
now do). The code changes required included replacing or augmenting checks for
InstanceType with checks for InstanceLike, and/or directly checking for
certain methods or attrs without bothering to first check for InstanceLike.
(I tested all 4 combos of (Python vs C same_vals) x (InstanceLike old vs new style),
but only briefly: make atoms, change bond type, make dna, undo all that.)

In general, to make this work properly for any newly defined class (old or new
style), the new class needs to inherit one of the mixin superclasses StateMixin
or DataMixin, and to have correct definitions of __eq__ and __ne__. (One special
case is class Bond, discussed in comments in Comparison.py dated 090205.)


Here is how each Python and C function mentioned above works properly for
new-style classes (assuming the code added 090206 works properly):


- same_vals: this is discussed at length in a comment in Comparison.py dated
090205. Briefly, its special case for InstanceType (to cause
_same_InstanceType_helper to be called) is not useful for any well-coded class
in principle, and is only needed for class Bond (to avoid its kluge in having
a looser version of __eq__ than StateMixin provides), and Bond is an old-style
class (when standard code is being used), so it's fine that we don't extend
that same_vals special case for InstanceType to cover new-style classes.
This is true for both the Python and C versions of same_vals. (And both would
need fixing if we wanted to handle Bond being a new-style class but continue
using its __eq__ kluge. Since Bond is the only class that would need that fix,
we'd want a fix that didn't slow down the general case.)

Re the experimental code which makes Bond a new-style class: the lack
of a same_vals special case would cause __eq__ to be used by same_vals
(for both Python and C versions); this might conceivably cause trouble
in Undo, so it should be fixed. I documented that issue in Bond and made it
print a warning if it's new-style. In fact, now it *is* new-style,
since I'm trying out making all InstanceLike classes new-style.

I'm not bothering to fix this for now (in either Python or C same_vals),
since there's no immediate need to let Bond be a new-style class
(though I've made it one, along with all InstanceLikes, as an experiment),
and the warning should mean we don't forget; we'll see if it causes
any noticable undo bugs. But it ought to be cleaned up before the next release. ### DOIT


- copy_val: this properly handles all old-style and new-style classes.
The details are slightly different for Python and C, and include
detection of InstanceType, isinstance check for InstanceLike,
and looking directly for the _copyOfObject method. The copying is
handled by copy_InstanceType and/or generalCopier (which ought to be merged ###DOIT)
being called to copy instances of these classes.


- scan_vals: this only has a Python version. It properly handles all
old-style and new-style classes similarly to copy_val, calling scan_InstanceType
to handle them (though that's a misleading name when used on new-style classes ### FIX).


- is_mutable: I think this is correct for both old and new style classes,
since in either case it detects an attribute defined only in DataMixin.


- other code, all related to Undo:

  - various checks for InstanceType -- these now also check for InstanceLike,
    or are removed in favor of just checking an arbitrary object for certain
    attrs or methods

  - use of class names via __class__.__name__ -- should work for old- or new-
    style classes, as long as class "basenames" are unique (which is probably not
    verified by this code ### FIX)
    (old-style __name__ has dotted module name, new-style __name__ doesn't)

TODO [as of 090206]:

- I've experimentally made InstanceLike inherit object, forcing all DataMixin/
  StateMixins (incl Atom Bond Node) to be new-style. Test everything to see
  whether this has caused any trouble, and optimize for it by replacing
  __getattr__ methods with properties in certain classes.
  
- cleanups
  - merge copy_InstanceType and generalCopier
  - others listed herein

- renamings
  - variables and functions with InstanceType in their names -- most of these
    now also cover InstanceLikes; the name can just say Instance

"""

from types import InstanceType

from foundation.state_constants import S_DATA
from foundation.state_constants import S_CHILD, S_CHILDREN, S_CHILDREN_NOT_DATA
from foundation.state_constants import S_REF, S_REFS
from foundation.state_constants import S_PARENT, S_PARENTS
from foundation.state_constants import UNDO_SPECIALCASE_ATOM, UNDO_SPECIALCASE_BOND
from foundation.state_constants import ATOM_CHUNK_ATTRIBUTE_NAME
from foundation.state_constants import _UNSET_, _Bugval

import foundation.env as env
from utilities.debug import print_compact_stack
from utilities import debug_flags
from utilities.Comparison import same_vals, SAMEVALS_SPEEDUP
from utilities.constants import remove_prefix

from utilities.GlobalPreferences import debug_pyrex_atoms

DEBUG_PYREX_ATOMS = debug_pyrex_atoms()

### TODO:
"""
Where is _copyOfObject (etc) documented? (In code and on wiki?)

On wiki: 

http://www.nanoengineer-1.net/mediawiki/index.php?title=How_to_add_attributes_to_a_model_object_in_NE1

That documentation should say:

- When defining _copyOfObject, consider:
  
  - is its own return value __eq__ to the original? It should be,
    so you have to define __eq__ AND __ne__ accordingly.
    [later: I think the default def of __ne__ from __eq__ means
     you needn't define your own __ne__.]
  
  - should you define _s_scan_children too, to scan the same things
    that are copied?
    (Only if they are instance objects, and are "children".
     See S_CHILDREN doc for what that means.)
    [later: I think this only matters if they can contain undoable state
     or point to other objects which can.]

I did the above for VQT and jigs_planes, but still no __eq__ or children
for jig_Gamess -- I'll let that be a known bug I fix later,
to test the behavior of my error detect/response code.
[later: I think this ended up getting done.]
Also, when I do fix it (requires analyzing jig_Gamess contents)
I might as well turn it into using a mixin
to give it a proper __eq__ based on declaring the state attrs!

I might as well put state decls into the archived-state objects I'm creating,
so they too could be compared by __eq__ and diffed!!! (Actually, that wouldn't
work for diff since it has to descend into their dictionaries in an intelligent
way. But it might work for __eq__.)

This means my archived-state objects should really be objects, not just
tuples or dicts. Let's change the code that collects one to make this true.
Search for... attrdict?

S_CHILDREN: we might need a decl that we (some class) have no children
(so we don't print a warning about that), and a registration for external classes
of the same thing. [TODO: this needs a better explanation]

And certainly we need to go through the existing stateholder classes (e.g. Node)
and add their attr/child decls. [that has been done]
Maybe rather than accomodating copyable_attrs, we'll just replace it?
Not sure, maybe later (a lot of things use it). [it's still there, 071113]

Do any inappropriate objects get a key (like data or foreign objs)
in current code?? #####@@@@@
"""

##debug_dont_trust_Numeric_copy = False # 060302 -- will this fix last night's
##  singlet-pulling bug? [no, that was weird '==' semantics]
##    # (warning, it's slow!) 
##
##debug_print_every_array_passed_to_Numeric_copy = False # hmm, this might be
##  slow too... to be safe, the runtime use of it should condition it on env.debug(),
##  and to be fast, also on debug_dont_trust_Numeric_copy.

# ==

class _eq_id_mixin_: #bruce 060209 ##e refile? use more? (GLPane?)
    """
    For efficiency, any classes defining __getattr__ which might frequently
    be compared using == or != or coerced to a boolean, should have definitions
    for __eq__ and __ne__ and __nonzero__ (and any others we forgot??),
    even if those are semantically equivalent to Python's behavior when they don't.

    Otherwise Python has to call __getattr__ on each comparison of these objects,
    just to check whether they have one of those special method definitions
    (potentially as a value returned by __getattr__). This makes those simple
    comparisons MUCH SLOWER!
    
    This mixin class is one way of solving that problem by providing definitions
    for those methods.

    It's ok for a subclass to override some of the methods defined here.
    It can override both __eq__ and __ne__, or __eq__ alone (which will cause
    our __ne__ to follow suit, since it calls the instances __eq__), but it
    should not normally override __ne__ alone, since that would probably
    cause __eq__ and __ne__ to be incompatible.

    These definitions are suitable for objects meant as containers for "named"
    mutable state (for which different objects are never equal, even if their
    *current* state is equal, since their future state might not be equal).

    They are not suitable for data-like objects. This is why the class name
    contains '_eq_id_' rather than '_eq_data_'. For datalike objects, there is
    no shortcut to defining each of these methods in a customized way (and that
    should definitely be done, for efficiency, under the same conditions in
    which use of this mixin is recommended). (We might still decide to make
    an _eq_data_mixin_(?) class for them, for some other reason.)
    """
    def __eq__(self, other):
        return self is other
    def __ne__(self, other):
        ## return not (self == other)
        ##     # presumably this uses self.__eq__ -- would direct use be faster?
        return not self.__eq__(other)
    def __nonzero__(self):
        ### warning: I did not verify in Python docs that __nonzero__ is the
        ### correct name for this! [bruce 060209]
        return True
    def __hash__(self):
        #####k guess at name; guess at need for this due to __eq__,
        #####  but it did make our objects ok as dict keys again
        return id(self) #####k guess at legal value
    pass

# ==

def noop(*args, **kws):
    # duplicate code warning: redundant with def noop in constants.py,
    # but i don't want to try importing from there right now [bruce 070412]
    pass

def transclose( toscan, collector, layer_collector = noop, pass_counter = False):
    """
    General transitive closure routine using dictionaries for collections in its API,
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
       If pass_counter = True, then pass collector a third argument, counter,
    which is 1 for values in toscan, 2 for new values found directly connected to those,
    3 for the new values found connected to *those*, etc.
       If layer_collector is provided, then pass it (counter, set of values with that counter)
    each time that becomes known. If it stores counter and collector can see that value,
    it can know the counter value it would be passed (same as the last stored one).
    If it wants to store the set of values, it can know we won't modify it, but it must not
    modify it itself either, until we return. After that, it can own all those sets it got,
    except that the first one might be identical to (i.e. be the same mutable object as) toscan.
    """
    # We have three dicts at a time: objects we're finding (not being checked for newness yet),
    # objects we're scanning to look for those, and objects seen (i.e. done with or being scanned).
    # Keys are consistent in all these dicts (and should be as unique as objects need to be distinct),
    # but what they actually are is entirely up to our args (but they must be consistent between the two args as well).
    # [#doc: need to explain that better]
    seen = dict(toscan)
    counter = 1 # only matters for pass_counter or layer_collector
    while toscan:
        layer_collector(counter, toscan) # new feature [bruce 070412]
        found = {}
        len1 = len(toscan)
        for obj in toscan.itervalues():
            if pass_counter:
                # new feature [bruce 070412] [untested, since layer_collector turned out to be more useful]
                collector(obj, found, counter)
            else:
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
        toscan = new ##e should API permit asking us to store each toscan in an external dict? more useful than passing counter!
        counter += 1
        continue
    return seen

# ==

# private exceptions for use in private helper functions for certain recursive scanners:
class _IsMutable(Exception):
    pass


class Classification: #e want _eq_id_mixin_? probably not, since no getattr.
    """
    Classifications record policies and methods for inspecting/diffing/copying/etc all objects of one kind,
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


# Tuple of state attr decl values used for attrs which hold "defining state",
# which means state that should (usually) be saved, compared, copied, tracked/changed by Undo, etc.
# Should not include attrs recomputable from these, even if as an optim we sometimes track or save them too (I think).

STATE_ATTR_DECLS = (S_DATA, S_CHILD, S_CHILDREN, S_REF, S_REFS, S_PARENT, S_PARENTS) # but not S_CACHE, S_JUNK(?), S_CHILDREN_NOT_DATA, etc
    #e refile in state_constants.py ? not sure, since it's not needed outside this module

class InstanceClassification(Classification): #k used to be called StateHolderInstanceClassification; not yet sure of scope
    # we might decide to have a helper func classify an instance and return one of several classes, or None-or-so...
    # i mean some more atomic-like classification for classes that deserve one... [060221 late]
    #k not sure if this gains anything from its superclass
    """
    ###doc, implem - hmm, why do we use same obj for outside and inside? because, from outside, you might add to explore-list...
    """
    def __init__(self, class1):
        """
        Become a Classification for class class1 (applicable to its instances)
        """
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
        self.attrcode_dflt_pairs = [] # as of 060409 this is not filled with anything, but in future, we'll want it again ##e
            # public list of attrcode, dflt pairs, for attrs with a default value (has actual value, not a copy);
            # attrcode will be distinct whenever dflt value differs (and maybe more often) [as of 060330]
        self.dict_of_all_state_attrcodes = {}
        self.dict_of_all_Atom_chunk_attrcodes = {} #bruce 071104 kluge
        self.attrcodes_with_undo_setattr = {} #060404, maps the attrcodes to an arbitrary value (only the keys are currently used)
        self.categories = {} # (public) categories (e.g. 'selection', 'view') for attrs which declare them using _s_categorize_xxx
        self.attrlayers = {} # (public) similar [060404]
        self.attrcode_defaultvals = {} # (public) #doc
            ##@@ use more, also know is_mutable about them, maybe more policy about del on copy
            # as of 060330 this is only used by commented-out code not yet adapted from attr to attrcode.
        self.warn = True # from decls seen so far, do we need to warn about this class (once, when we encounter it)?
        self.debug_all_attrs = False # was env.debug(); can normally be False now that system works # DEBUG_PYREX_ATOMS?
        
        self._find_attr_decls(class1) # fills self.policies and some other instance variables derived from them

        self.attrcodes_with_no_dflt = tuple(self.attrcodes_with_no_dflt) # optimization, I presume; bad if we let new attrs get added later
        self.attrcode_dflt_pairs = tuple(self.attrcode_dflt_pairs)
        
        self.S_CHILDREN_attrs = self.attrs_declared_as(S_CHILD) + \
                                self.attrs_declared_as(S_CHILDREN) + \
                                self.attrs_declared_as(S_CHILDREN_NOT_DATA)  #e sorted somehow? no need yet.
        
        self._objs_are_data = copiers_for_InstanceType_class_names.has_key(class1.__name__) or \
                              hasattr(class1, '_s_isPureData')
            # WARNING: this code is duplicated/optimized in _same_InstanceType_helper [as of bruce 060419, for A7]

        if self.warn and (env.debug() or DEBUG_PYREX_ATOMS):
            # note: this should not be env.debug() since anyone adding new classes needs to see it...
            # but during development, with known bugs like this, we should not print stuff so often...
            # so it's env.debug for now, ####@@@@ FIX THAT LATER  [060227]
            print "InstanceClassification for %r sees no mixin or _s_attr decls; please add them or register it (nim)" \
                  % class1.__name__

        if (env.debug() or DEBUG_PYREX_ATOMS) and not self.attrcodes_with_no_dflt and self.attrcode_dflt_pairs: #060302; doesn't get printed (good)
            print "InstanceClassification for %r: all attrs have defaults, worry about bug resetting all-default objects"\
                  % class1.__name__
        return

    def __repr__(self):
        return "<%s at %#x for %s>" % (self.__class__.__name__, id(self), self.class1.__name__)

    def _acode_should_be_classname(self, class1): #bruce 071114
        """
        Say whether the acode component of all attrcodes for
        undoable attributes in instances of class1
        should equal the classname of class1,
        rather than having its usual value
        as determined by the caller.
        """
        # VERIFY right thing it should be, right cond; understand why;
        # [prior code was equivalent to class1.__name__ in ('Atom', 'Bond')
        #  and had comment "###@@@ kluge 060404, in two places",
        #  which occurred at both code snippets that are now calls of this.
        #  One of them also says "# it matters that this can't equal id(dflt)
        #  for this attr in some other class" -- I think that was depended on
        #  to let each subclass with same attrname have its own dfltval,
        #  back when dfltvals were supported. But there might be other things
        #  that still happen that assume this, I don't know. [bruce 071114]]
        specialcase_type = getattr( class1, '_s_undo_specialcase', None)
        if specialcase_type in (UNDO_SPECIALCASE_ATOM,
                                UNDO_SPECIALCASE_BOND):
            return True
        return False
        
    def _find_attr_decls(self, class1):
        """
        find _s_attr_xxx decls on class1, and process/store them
        """
        if self.debug_all_attrs:
            print "debug: _find_attr_decls in %s:" % (class1.__name__,)
        all_s_attr_decls = filter(lambda x: x.startswith("_s_"), dir(class1))
        for name in all_s_attr_decls:
            if name.startswith('_s_attr_'):
                ## attr_its_about = name[len('_s_attr_'):]
                attr_its_about = remove_prefix( name, '_s_attr_')
                setattr_name = '_undo_setattr_' + attr_its_about
                declval = getattr(class1, name) # the value assigned to _s_attr_<attr>
                self.policies[attr_its_about] = declval #k for class1, not in general
                if self.debug_all_attrs:
                    print "  %s = %s" % (name, declval)
                self.warn = False # enough to be legitimate state
                #e check if per-instance? if callable? if legal?
                if declval in STATE_ATTR_DECLS:
                    # figure out if this attr has a known default value... in future we'll need decls to guide/override this
                    # (REVIEW: is this really about a declared one, or a class-defined one, if both of those are supported?
                    #  This is academic now, since neither is supported. [bruce 071113 comment])
                    has_dflt, dflt = self.attr_has_default(class1, attr_its_about)
                    assert not has_dflt # see comment in attr_has_default about why current code requires this
                    if not has_dflt:
                        acode = 0 ###stub, but will work initially;
                            # later will need info about whether class is diffscanned, in layer, etc
                        if self._acode_should_be_classname(class1):
                            acode = class1.__name__
                            assert _KLUGE_acode_is_special_for_extract_layers(acode)
                        else:
                            assert not _KLUGE_acode_is_special_for_extract_layers(acode)
                        attrcode = (attr_its_about, acode)
                        self.attrcodes_with_no_dflt.append(attrcode)
                    else:
                        # NOTE: this case never runs as of long before 071114.
                        # attr has a default value.
                        # first, make sure it has no _undo_setattr_ method, since our code for those has a bug
                        # in that reset_obj_attrs_to_defaults would need to exclude those attrs, but doesn't...
                        # for more info see the comment near its call. [060404]
                        assert not hasattr(class1, setattr_name), "bug: attr with class default can't have %s too" % setattr_name
                            # this limitation could be removed when we need to, by fixing the code that calls reset_obj_attrs_to_defaults
                        acode = id(dflt) ###stub, but should eliminate issue of attrs with conflicting dflts in different classes
                            # (more principled would be to use the innermost class which changed the _s_decl in a way that matters)
                        if self._acode_should_be_classname(class1):
                            acode = class1.__name__ # it matters that this can't equal id(dflt) for this attr in some other class
                            assert _KLUGE_acode_is_special_for_extract_layers(acode)
                        else:
                            assert not _KLUGE_acode_is_special_for_extract_layers(acode)
                        attrcode = (attr_its_about, acode)
                        self.attrcode_dflt_pairs.append( (attrcode, dflt) )
                        self.attrcode_defaultvals[attrcode] = dflt
                        if (env.debug() or DEBUG_PYREX_ATOMS) and is_mutable(dflt): #env.debug() (redundant here) is just to make prerelease snapshot safer
                            if (env.debug() or DEBUG_PYREX_ATOMS):
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
                        # only True, not e.g. the unbound method, since classes
                        # with this can share attrcodes, so it's just a hint
                    specialcase_type = getattr( class1, '_s_undo_specialcase', None)
                    if specialcase_type == UNDO_SPECIALCASE_ATOM and \
                       attr_its_about == ATOM_CHUNK_ATTRIBUTE_NAME:
                        self.dict_of_all_Atom_chunk_attrcodes[ attrcode ] = None #071114
                pass
            elif name == '_s_isPureData': # note: exact name (not a prefix), and doesn't end with '_'
                self.warn = False # enough to be legitimate data
            elif name == '_s_scan_children':
                pass ## probably not: self.warn = False
            elif name == '_s_undo_specialcase':
                pass
            elif name == '_s_undo_class_alias':
                pass
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

    def attr_has_default(self, class1, attr):
        """
        Figure out whether attr has a known default value in class1.

        @param class1: a class whose instances might be scanned for diffs by Undo.

        @param attr: an attribute of instances of class1, which contains undoable state.

        @return: (has_dflt, dflt), where has_dflt is a boolean saying
        whether attr has a default value in class1, and (if it does)
        dflt is that value (and is identical to it, not just equal to it,
        if that might matter).
        
        @note: this currently always says "no" by returning (False, None),
        to accomodate limitations in other code. (See code comment for details.)

        @note: in future we'll need decls to guide/override this.
        When we do, the callers may need to distinguish whether there's
        a known default value, vs whether it's stored as a class attribute.
        """
        if 0:
            # This version is disabled because differential mash_attrs requires
            # no dflt vals at all, or it's too complicated.
            #
            # What would be better (and will be needed to support dfltvals
            # for binary mmp save) would be to still store attrs with dflts
            # here, but to change the undo iter loops to iterate over all
            # attrs with or without defaults, unlike now.
            #
            # An earlier kluge [060405 1138p], trying to fix some bugs,
            # was, for change-tracked classes, to pretend there's no such thing
            # as a default value, since I suspected some logic bugs in the dual
            # meaning of missing state entries as dflt or dontcare.
            # That kluge looked at class1.__name__ in ('Atom', 'Bond') to detect
            # change-tracked classes.
            try:
                return True, getattr(class1, attr)
            except AttributeError:
                # assume no default value unless one is declared (which is nim)
                return False, None
            pass
        return False, None
    
    def attrs_declared_as(self, S_something):
        #e if this is commonly called, we'll memoize it in __init__ for each S_something
        res = []
        for attr, decl in self.policies.iteritems():
            if decl == S_something:
                res.append(attr)
        return res

    def obj_is_data(self, obj):
        """
        Should obj (one of our class's instances) be considered a data object?
        """
        return self._objs_are_data
            ## or hasattr(obj, '_s_isPureData'),
            # if we want to let individual instances override this
    
    def copy(self, val, func): # from outside, when in vals, it might as well be atomic! WRONG, it might add self to todo list...
        """
        Copy val, a (PyObject pointer to an) instance of our class
        """
        return val
    
    def scan_children( self, obj1, func, deferred_category_collectors = {}, exclude_layers = ()):
        """
        [for #doc of deferred_category_collectors, see caller docstring]
        """
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
        """
        Should you scan attr (of an obj of this clas), given these exclude_layers (perhaps ())?
        """
        return self.attrlayers.get(attr) in exclude_layers # correct even though .get is often None

    pass # end of class InstanceClassification

# == helper code  [##e all code in this module needs reordering]

_known_type_copiers = {}
    # needs no entry for types whose instances can all be copied as themselves

_known_mutable_types = {} # used by is_mutable

_known_type_scanners = {}
    # only needs entries for types whose instances might contain (or be)
    # InstanceType or InstanceLike objects, and which might need to be entered
    # for finding "children" (declared with S_CHILD) -- for now we assume that
    # means there's no need to scan inside bound method objects, though this
    # policy might change.

# not yet needed, but let the variable exist since there's one use of it I might as well leave active (since rarely run):
copiers_for_InstanceType_class_names = {} # copier functions for InstanceTypes whose classes have certain names
    # (This is mainly for use when we can't add methods to the classes themselves.
    #  The copiers should verify the class is the expected one, and return the original object unchanged if not
    #  (perhaps with a warning), or raise an exception if they "own" the classname.)
    #
    # WARNING: some code is optimized to assume without checking that copiers_for_InstanceType_class_names is empty,
    # so search for all uses of it (in commented out code) if you ever add something to it. [bruce 060419]

# scanners_for_class_names would work the same way, but we don't need it yet.

_DEBUG_COPYOFOBJECT = False # initial value not used -- set to env.debug() in each run of copy_val [bruce 060311]

def copy_val(val):
    """
    Efficiently copy a general Python value (so that mutable components are
    not shared with the original), returning class instances unchanged unless
    they define a _copyOfObject method, and returning unrecognized objects
    (e.g. QWidgets, bound methods) unchanged.

    (See a code comment for the reason we can't just use the standard Python
     copy module for this.)

    @note: this function is replaced by a C implementation when that is
           available. See SAMEVALS_SPEEDUP in the code.
    """
    #bruce 060221 generalized semantics and rewrote for efficiency
    #bruce 060315 partly optimized env.debug() check
    global _DEBUG_COPYOFOBJECT
    _DEBUG_COPYOFOBJECT = debug_flags.atom_debug # inlined env.debug() # DEBUG_PYREX_ATOMS?
        ##e ideally we'd have a recursive _copy_val_helper that doesn't check this debug flag at all
    try:
        # wware 060308 small performance improvement (use try/except);
        # made safer by bruce, same day.
        # [REVIEW: is this in fact faster than using .get?]
        # note: _known_type_copiers is a fixed public dictionary
        copier = _known_type_copiers[type(val)]
    except KeyError:
        # we used to optimize by not storing any copier for atomic types...
        # but now that we call generalCopier [bruce 090206] that is no longer
        # an optimization, but since the C code is
        # used by all end-users and most developers, nevermind for now.
        return generalCopier(val)
    else:
        # assume copier is not None, since we know what's stored in _known_type_copiers
        return copier(val)
    pass

def is_mutable(val): #bruce 060302
    """
    Efficiently scan a potential argument to copy_val to see if it contains
    any mutable parts (including itself), with special cases suitable for use
    on state-holding attribute values for Undo, which might be surprising
    in other applications (notably, for most InstanceType/InstanceLike objects).

    Details:

    Treat list and dict as mutable, tuple (per se) as not (but scan its
     components) -- all this is correct.

    Treat Numeric.array as mutable, regardless of size or type
    (dubious for size 0, though type and maybe shape could probably be changed,
     but this doesn't matter for now).

    Treat unknown types occuring in _known_mutable_types as mutable (ok for now,
     though might need registration scheme in future; might cover some of the
     above cases).

    Treat InstanceLike instances as mutable if and only if they define an
    _s_isPureData attribute. (The other ones, we're thinking of as immutable
    references or object pointers, and we don't care whether the objects they
    point to are mutable.)
    """
    # REVIEW: should this be used more?
    # As of 090206, it only occurs in this file, and its only actual use
    # is for a debug-only warning about mutable default values of undoable
    # attrs (which are allowed and do occur in our code). (Perhaps the
    # original intent was to optimize for non-mutable ones, but this is
    # not presently done.)
    try:
        _is_mutable_helper(val)
    except _IsMutable:
        return True
    return False

def _is_mutable_helper(val, _tupletype = type(())):
    """
    [private recursive helper for is_mutable]

    raise _IsMutable if val (or part of it) is mutable
    """
    #bruce 060303, revised 090206
    typ = type(val)
    if typ is _tupletype:
        # (kluge, 090206: storing _tupletype as an optional arg's default value
        #  is just for faster comparison -- caller should never pass it)
        
        # tuple is a special case, since it has components that might be
        # mutable but is not itself mutable -- someday, make provisions for
        # more special cases like this, which can register themselves
        for thing in val:
            _is_mutable_helper(thing)
        pass
    elif _known_mutable_types.get(typ): # a fixed public dictionary
        raise _IsMutable
    elif hasattr(val, '_s_isPureData'):
        # (note: only possible when isinstance(val, InstanceLike),
        #  but always safe to check, so no need to check for InstanceLike)
        raise _IsMutable
    return # immutable or unrecognized types

def scan_val(val, func): 
    """
    Efficiently scan a general Python value, and call func on all InstanceType
    objects (old-style class instances) and/or InstanceLike objects (instances
    of subclasses of InstanceLike, whether old or new style) encountered.

    No need to descend inside any values unless they might contain class instances.

    Note that some classes define the _s_scan_children method, but we *don't*
    descend into their instances here using that method -- this is only done
    by other code, such as whatever code func might end up delivering such objects to.
    
    Special case: we never descend into bound method objects either.
    
    @return: an arbitrary value which caller should not use (always None in
             the present implem)
    """
    #doc -- the docstring needs to explain why we never descend into bound
    # method objects. It used to say "see comment on _known_type_scanners for
    # why", but I removed that since I can no longer find that comment.
    # [bruce 090206]
    typ = type(val)
    scanner = _known_type_scanners.get(typ) # a fixed public dictionary
    if scanner is not None:
        # we used to optimize by not storing any scanner for atomic types,
        # or a few others; as of 090206 this might be a slowdown ###OPTIM sometime
        scanner(val, func)
    elif isinstance( val, InstanceLike):
        scan_InstanceType(val, func) #bruce 090206, so no need to register these
    return
    
_known_type_copiers[type([])] = copy_list
_known_type_copiers[type({})] = copy_dict
_known_type_copiers[type(())] = copy_tuple

_known_mutable_types[type([])] = True
_known_mutable_types[type({})] = True
# not tuple -- it's hardcoded in the code that uses this

_known_type_scanners[type([])] = scan_list
_known_type_scanners[type({})] = scan_dict
_known_type_scanners[type(())] = scan_tuple


def copy_InstanceType(obj): #e pass copy_val as an optional arg? # rename: _copy_instance ? TODO: merge with generalCopier
    """
    This is called by copy_val to support old-style instances,
    or (for C copy_val only) new-style instances whose classes were
    passed to setInstanceLikeClasses (as of 090206 that is never done).

    (The same thing is done for other new-style InstanceLike classes
     by generalCopier, which will soon be merged with this function.)

    This function's main point is to honor the _copyOfObject method on obj
    (returning whatever it returns), rather than just returning obj
    (as it does anyway if that method is not defined).

    Note that obj._copyOfObject() returns obj for most "model objects"
    (which inherit StateMixin), even though they have other nontrivial
    copy methods. What this copies is a reference to them in the value
    of some attribute on some other object.

    @param obj: the object (class instance) being copied.

    @see: generalCopier
    """
    # note: this shares some code with InstanceClassification  ###@@@DOIT
    
    # the following code for QColor is not yet needed, since QColor instances
    # are not of type InstanceType (but keep the code for when it is needed):
    ##copier = copiers_for_InstanceType_class_names.get(obj.__class__.__name__)
    ##    # We do this by name so we don't need to import QColor (for example)
    ##    # unless we encounter one. Similar code might be needed by anything
    ##    # that looks for _copyOfObject (as a type test or to use it).
    ##    # ###@@@ DOIT, then remove cmt
    ##    #e There's no way around checking this every time, though we might
    ##    # optimize by storing specific classes which copy as selves into some
    ##    # dict; it's not too important since we'll optimize Atom and Bond
    ##    # copying in other ways.
    ##if copier is not None:
    ##    return copier(obj, copy_val) # e.g. for QColor
    
    try:
        # note: not compatible with copy.deepcopy's __deepcopy__ method.
        # see DataMixin and IdentityCopyMixin below.
        copy_method = obj._copyOfObject 
    except AttributeError:
        print "****************** needs _copyOfObject -- inherit DataMixin " \
              "or IdentityCopyMixin or StateMixin: %s" % repr(obj)
        return obj
    res = copy_method() 
        #bruce 081229 no longer pass copy_val (removed never-used copyfunc arg)
    if _DEBUG_COPYOFOBJECT and (obj != res or (not (obj == res))):
        #bruce 060311 adding _DEBUG_COPYOFOBJECT as optim (suggested by Will)
        
        # This has detected a bug in copy_method, which will cause false
        # positives in change-detection in Undo (since we'll return res anyway).
        # (It's still better to return res than obj, since returning obj could
        #  cause Undo to completely miss changes.)
        #
        # Note: we require obj == res, but not res == obj (e.g. in case a fancy
        # number turns into a plain one). Hopefully the fancy object could
        # define some sort of __req__ method, but we'll try to not force it to
        # for now; this has implications for how our diff-making archiver should
        # test for differences. ###@@@doit

        msg = "bug: obj != res or (not (obj == res)), res is _copyOfObject of obj; " \
              "obj is %r, res is %r, == is %r, != is %r: " % \
              (obj, res, obj == res, obj != res)

        if not env.debug():
            print msg
        else:
            print_compact_stack( msg + ": ")
            try:
                method = obj._s_printed_diff
                    # experimental (#e rename):
                    # list of strings (or so) which explain why __eq_ returns
                    # false [060306, for bug 1616]
            except AttributeError:
                pass
            else:
                print "  a reason they are not equal:\n", method(res)
        #e also print history redmsg, once per class per session?
    return res

# ==

_generalCopier_exceptions = {}
    # set of types which generalCopier should not complain about;
    # extended at runtime

if 1:
    # add exceptions for known types we should trivially copy
    # whenever they lack a _copyOfObject method
    class _NEW_STYLE_1(object):
        pass
    class _OLD_STYLE_1:
        pass

    for _x in [1, # int
               None, # NoneType
               True, # bool
               "", # str
               u"", # unicode
               0.1, # float
               # not InstanceType -- warn about missing _copyOfObject method
               ## _OLD_STYLE_1(), # instance == InstanceType
               _OLD_STYLE_1, # classobj
               _NEW_STYLE_1 # type
              ]:
        _generalCopier_exceptions[type(_x)] = type(_x)
    
def generalCopier(obj): #bruce 090206, called from both C and Python copy_val
    """
    @param obj: a new-style class instance, or anything else whose type is not
                known to copy_val
    @type obj: anything
    
    ###doc; related to copy_InstanceType
    """
    try:
        copy_method = obj._copyOfObject
    except AttributeError:
        # This will happen once for anything whose type is not known to copy_val
        # and which doesn't inherit DataMixin or IdentityCopyMixin or StateMixin
        # (or otherwise define _copyOfObject), unless we added it to 
        # _generalCopier_exceptions above.
        if not _generalCopier_exceptions.get(type(obj)):
            print "\n***** adding generalCopier exception for %r " \
                  "(bad if not a built-in type -- classes used in copied model " \
                  "attributes should inherit something like DataMixin or " \
                  "StateMixin)" % type(obj)
            _generalCopier_exceptions[type(obj)] = type(obj)
        return obj
    else:
        return copy_method()
    pass

# ==

if SAMEVALS_SPEEDUP:
    # Replace definition above with the extension's version.
    # (This is done for same_vals in utilities/Comparison.py,
    #  and for copy_val here in state_utils.py.)
    from samevals import copy_val, setInstanceCopier, setGeneralCopier, setArrayCopier
    setInstanceCopier(copy_InstanceType)
        # note: this means copy_InstanceType is applied by the C version
        # of copy_val to instances of InstanceType (or of any class in the
        # list passed to setInstanceLikeClasses, but we no longer do that).
    setGeneralCopier(generalCopier)
        # note: generalCopier is applied to anything that lacks hardcoded copy
        # code which isn't handled by setInstanceCopier, including
        # miscellaneous extension types, and instances of any new-style classes
        # not passed to setInstanceLikeClasses. In current code and in routine
        # usage, it is probably never used, but if we introduce new-style model
        # classes (or use the experimental atombase extension), it will be used
        # to copy their instances. Soon I plan to make some model classes
        # new-style. [new feature, bruce 090206]
    setArrayCopier(lambda x: x.copy())

# inlined:
## def is_mutable_InstanceType(obj): 
##     return hasattr(obj, '_s_isPureData')
  
_known_type_copiers[ InstanceType ] = copy_InstanceType

def scan_InstanceType(obj, func):
    """
    This is called by scan_vals to support old-style instances,
    or new-style instances whose classes inherit InstanceLike
    (or its subclasses such as StateMixin or DataMixin).

    @param obj: the object (class instance) being scanned.

    @param func: ###doc this
    """
    func(obj)
    #e future optim: could we change API so that apply could serve in place
    # of scan_InstanceType? Probably not, but nevermind, we'll just do all
    # this in C at some point.
    return None 

_known_type_scanners[ InstanceType ] = scan_InstanceType
    # (storing this is mainly just an optimization, but not entirely,
    #  if there are any old-style classes that we should scan this way
    #  but which don't inherit InstanceLike; that is probably an error
    #  but not currently detected. [bruce 090206 comment])

# ==

def copy_Numeric_array(obj):
    if obj.typecode() == PyObject:
        if (env.debug() or DEBUG_PYREX_ATOMS):
            print "atom_debug: ran copy_Numeric_array, PyObject case" # remove when works once ###@@@
        return array( map( copy_val, obj) )
            ###e this is probably incorrect for multiple dimensions; doesn't matter for now.
            # Note: We can't assume the typecode of the copied array should also be PyObject,
            # since _copyOfObject methods could return anything, so let it be inferred.
            # In future we might decide to let this typecode be declared somehow...
##    if debug_dont_trust_Numeric_copy: # 060302
##        res = array( map( copy_val, list(obj)) )
##        if debug_print_every_array_passed_to_Numeric_copy and env.debug():
##            print "copy_Numeric_array on %#x produced %#x (not using Numeric.copy); input data %s" % \
##                  (id(obj), id(res), obj) 
##        return res
    return obj.copy() # use Numeric's copy method for Character and number arrays 
        ###@@@ verify ok from doc of this method...

def scan_Numeric_array(obj, func):
    if obj.typecode() == PyObject:
        # note: this doesn't imply each element is an InstanceType instance,
        # just an arbitrary Python value
        if env.debug() or DEBUG_PYREX_ATOMS:
            print "atom_debug: ran scan_Numeric_array, PyObject case" # remove when works once ###@@@
        ## map( func, obj)
        for elt in obj:
            scan_val(elt, func) #bruce 060315 bugfix
        # is there a more efficient way?
        ###e this is probably correct but far too slow for multiple dimensions; doesn't matter for now.
    return

try:
    from Numeric import array, PyObject
except:
    if env.debug() or DEBUG_PYREX_ATOMS:
        print "fyi: can't import array, PyObject from Numeric, so not registering its copy & scan functions"
else:
    # note: related code exists in utilities/Comparison.py.
    numeric_array_type = type(array(range(2)))
        # note: __name__ is 'array', but Numeric.array itself is a
        # built-in function, not a type
    assert numeric_array_type != InstanceType
    _known_type_copiers[ numeric_array_type ] = copy_Numeric_array
    _known_type_scanners[ numeric_array_type ] = scan_Numeric_array
    _known_mutable_types[ numeric_array_type ] = True

    _Numeric_array_type = numeric_array_type #bruce 060309 kluge, might be temporary
    del numeric_array_type
        # but leave array, PyObject as module globals for use by the
        # functions above, for efficiency
    pass

# ==

def copy_QColor(obj):
    from PyQt4.Qt import QColor
    assert obj.__class__ is QColor # might fail (in existing calls) if some other class has the same name
    if (env.debug() or DEBUG_PYREX_ATOMS):
        print "atom_debug: ran copy_QColor" # remove when works once; will equality work right? ###@@@
    return QColor(obj)

try:
    # this is the simplest way to handle QColor for now; if always importing qt from this module
    # becomes a problem (e.g. if this module should work in environments where qt is not available),
    # make other modules register QColor with us, or make sure it's ok if this import fails
    # (it is in theory).
    from PyQt4.Qt import QColor
except:
    if (env.debug() or DEBUG_PYREX_ATOMS):
        print "fyi: can't import QColor from qt, so not registering its copy function"
else:
    QColor_type = type(QColor())
        # note: this is the type of a QColor instance, not of the class!
        # type(QColor) is <type 'sip.wrappertype'>, which we'll just treat as a constant,
        # so we don't need to handle it specially.
    if QColor_type != InstanceType:
        ## wrong: copiers_for_InstanceType_class_names['qt.QColor'] = copy_QColor
        _known_type_copiers[ QColor_type ] = copy_QColor
        _known_mutable_types[ QColor_type ] = True # not sure if needed, but might be, and safe
    else:
        print "Warning: QColor_type is %r, id %#x,\n and InstanceType is %r, id %#x," % \
              ( QColor_type, id(QColor_type), InstanceType, id(InstanceType) )
        print " and they should be != but are not,"
        print " so Undo is not yet able to copy QColors properly; this is not known to cause bugs"
        print " but its full implications are not yet understood. So far this is only known to happen"
        print " in some systems running Mandrake Linux 10.1. [message last updated 060421]"
    # no scanner for QColor is needed, since it contains no InstanceType/InstanceLike
    # objects. no same_helper is needed, since '!=' will work correctly
    # (only possible since it contains no general Python objects).
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
    """
    Use one of these to allocate small int keys (guaranteed nonzero) for objects you're willing to keep forever.
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
        """
        Allocate the requested key (assertfail if it's not available), or a new one we make up, and store None for it.
        """
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
        """
        What's the key for this object, if it has one? Return None if we didn't yet allocate one for it.
        Ok to call on objects for which allocating a key would be illegal (in fact, on any Python values, I think #k).
        """
        return self._key4obj.get(id(obj)) #e future optim: store in the obj, for some objs? not sure it's worth the trouble,
            # except maybe in addition to this, for use in inlined code customized to the classes. here, we don't need to know.
            # Note: We know we're not using a recycled id since we have a ref to obj! (No need to test it -- having it prevents
            # that obj's id from being recycled. If it left and came back, this is not valid, but then neither would the comparison be!)

    def key4obj_maybe_new(self, obj):
        """
        What's the key for this object, which we may not have ever seen before (in which case, make one up)?
        Only legal to call when you know it's ok for this obj to have a key (since this method doesn't check that).
        Optimized for when key already exists.
        """
        try:
            return self._key4obj[id(obj)]
        except KeyError:
            # this is the usual way to assign new keys to newly seen objects (maybe the only way)
            # note: this is an inlined portion of self.allocate_key()
            self._lastobjkey += 1
            key = self._lastobjkey
            assert not self.obj4key.has_key(key)
            self.obj4key[key] = obj
            self._key4obj[id(obj)] = key
            return key
        pass
    
    pass # end of class objkey_allocator

# ==

class StateSnapshot:
    """
    A big pile of saved (copies of) attribute values -- for each known attr, a dict from objkey to value.
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
        """
        Make an attrdict for attrcode. Assume we don't already have one.
        """
        assert self.attrdicts.get(attrcode) is None
        self.attrdicts[attrcode] = {}
    def size(self): ##e should this be a __len__ and/or a __nonzero__ method? ### shares code with DiffObj; use common superclass?
        """
        return the total number of attribute values we're storing (over all objects and all attrnames)
        """
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
        """
        [this is used by undo_archive to see if the state has really changed]
        """
        # this implem assumes modtimes/change_counters are not stored in the snapshots (or, not seen by diff_snapshots)!
        return self.__class__ is other.__class__ and not diff_snapshots(self, other)
    def __ne__(self, other):
        return not (self == other)
    def val_diff_func_for(self, attrcode):
        attr, acode_unused = attrcode
        if attr == '_posnxxx': # kluge, should use an _s_decl; remove xxx when this should be tried out ###@@@ [not used for A7]
            return val_diff_func_for__posn # stub for testing
        return None
    def extract_layers(self, layernames): #060404 first implem
        assert layernames == ('atoms',), "layernames can't be %r" % layernames #e generalize, someday
        res = self.__class__()
        for attrcode, attrdict_unused in self.attrdicts.items():
            attr_unused, acode = attrcode
            if _KLUGE_acode_is_special_for_extract_layers(acode):
                res.attrdicts[attrcode] = self.attrdicts.pop(attrcode)
        return res
    def insert_layers(self, layerstuff): #060404 first implem
        for attrcode in layerstuff.attrdicts.keys():
            assert not self.attrdicts.has_key(attrcode), "attrcode %r overlaps, between %r and %r" % (attrcode, self, layerstuff)
        self.attrdicts.update(layerstuff.attrdicts)
        layerstuff.attrdicts.clear() # optional, maybe not even good...
        return
    pass # end of class StateSnapshot

def _KLUGE_acode_is_special_for_extract_layers(acode): #bruce 071114
    #e rename when we see all the uses...
    # guess: probably just means
    # "acode is for a change-tracked attr, not a full-diff-scanned attr"
    # (together with assuming that for any class, all or none of its attrs are change-tracked),
    # (where by "change-tracked" we mean that changes are reported in registered changedicts --
    #  not directly related to the changed/usage tracked invalidatable lvalues in changes.py)
    # but the code in this file also assumes those objects are all part of
    # the so-called "atoms layer".
    ## was: return acode in ('Atom', 'Bond'): ###@@@ kluge 060404; assume acode is class name... only true for these two classes!!
    return type(acode) == type("")

def val_diff_func_for__posn( (p1, p2), whatret): # purely a stub for testing, though it should work
    assert type(p1) is _Numeric_array_type
    assert type(p2) is _Numeric_array_type
    return p2 - p1

def diff_snapshots(snap1, snap2, whatret = 0): #060227 
    """
    Diff two snapshots. Retval format [needs doc]. Missing attrdicts
    are like empty ones. obj/attr sorting by varid to be added later.
    """
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
    
        # 060309 experimental [not used as of 060409]: support special diff algs for certain attrs,
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
    """
    diff them, but only return what's needed to turn snap1 into snap2,
    as an object containing attrdicts (all mutable)
    """
    return DiffObj( diff_snapshots(snap1, snap2, whatret = 2) )
        ######@@@@@@ also store val_diff_func per attrcode? [060309 comment]

class DiffObj:
    attrname_valsizes = dict(_posn = 52)
        # maps attrcode (just attrname for now) to our guess about the size
        # of storing one attrval for that attrcode, in this kind of undo-diff;
        # this figure 52 for _posn is purely a guess
        # (the 3 doubles themselves are 24, but they're in a Numeric array
        # and we also need to include the overhead of the entire dict item in our attrdict),
        # and the guesses ought to come from the attr decls anyway, not be
        # hardcoded here (or in future we could measure them in a C-coded copy_val).
    def __init__(self, attrdicts = None):
        self.attrdicts = attrdicts or {}
    def size(self): ### shares code with StateSnapshot; use common superclass?
        """
        return the total number of attribute value differences we're
        storing (over all objects and all attrnames)
        """
        res = 0
        for d in self.attrdicts.itervalues():
            res += len(d)
        return res
    def RAM_usage_guess(self): #060323
        """
        return a rough guess of our RAM consumption
        """
        res = 0
        for attrcode, d in self.attrdicts.iteritems():
            attr, acode_unused = attrcode
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
    def accumulate_diffs(self, diffs): #060409
        """
        Modify self to incorporate a copy of the given diffs (which should be another diffobj),
        so that applying the new self is like applying the old self and then applying the given diffs.
        Don't change, or be bothered by future changes to, the given diffs.
        Return None.
        """
        assert isinstance(diffs, DiffObj)
            # What really matters is that its attrdicts use _UNSET_ for missing values,
            # and that each attrdict is independent, unlike for StateSnapshot attrdicts
            # where the meaning of a missing value depends on whether a value is present at that key in any attrdict.
            # Maybe we should handle this instead by renaming 'attrdicts' in one of these objects,
            # or using differently-named get methods for them. #e
        dicts2 = diffs.attrdicts
        dicts1 = self.attrdicts
        for attrcode, d2 in dicts2.iteritems():
            d1 = dicts1.setdefault(attrcode, {})
            d1.update(d2) # even if d1 starts out {}, it's important to copy d2 here, not share it
        return
    pass

def diffdicts(d1, d2, dflt = None, whatret = 0, val_diff_func = None):
    ###e dflt is problematic since we don't know it here and it might vary by obj or class [not anymore, long bfr 060309; ##doc]
    """
    Given two dicts, return a new one with entries at keys where their values differ (according to same_vals),
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
##                res[key] = (v1, v2)
##        elif 0:
##            #####@@@@@ see if *this* fixes my bug... 060302 955a
##            # [it did for whole Numeric arrays, but it won't work for Numeric arrays inside tuples or lists]
##            if v1 != v2:
##                res[key] = (v1, v2)
##        else:
        if not same_vals(v1, v2):
            res[key] = (v1, v2)
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
##                res[key] = (v1, v2)
            if not same_vals(v1, v2):
                res[key] = (v1, v2)
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
                # or letting whatrets 0,1,2 be special cases of val_diff_func (same idea), which takes (v1, v2) to what we want.
                # or just letting whatret be either 0,1,2, or a function.
                #    But these optims are not needed, since the idea is to use this on a small number of attrvals with lots of data in
                # each one (not just on a small number of attr *names*, but a small number of *values*). E.g. one attr for the entire
                # assy which knows all atom positions or bond types in the assy. It's just a way of letting some attrs have their
                # own specialcase diff algs and representations.
                # [later note: as of 060330 this val_diff_func is only supplied by val_diff_func_for, which never supplies one
                #  except for a stub attrname we don't use, and I don't know if we'll use this scheme for A7.]
    return res

# ==

##def priorstate_debug(priorstate, what = ""): #e call it, and do the init things
##    "call me only to print debug msgs"
##    ###@@@ this is to help me zap the "initial_state not being a StatePlace" kluges;
##    # i'm not sure where the bad ones are made, so find out by printing the stack when they were made.
##    try:
##        stack = priorstate._init_stack # compact_stack(), saved by __init__, for StatePlace and StateSnapshot
##    except:
##        print "bug: this has no _init_stack: %r" % (priorstate,)
##    else:
##        if not env.seen_before( ("ghjkfdhgjfdk" , stack) ):
##            print "one place we can make a %s priorstate like %r is: %s" % (what, priorstate, stack)
##    return

def diff_and_copy_state(archive, assy, priorstate): #060228 (#e maybe this is really an archive method? 060408 comment & revised docstring)
    """
    Figure out how the current actual model state (of assy) differs from the last model state we archived (in archive/priorstate).
    Return a new StatePlace (representing a logically immutable snapshot of the current model state)
    which presently owns a complete copy of that state (a mutable StateSnapshot which always tracks our most recent snapshot
    of the actual state), but is willing to give that up (and redefine itself (equivalently) as a diff from a changed version of that)
    when this function is next called.
    """
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
    import foundation.undo_archive as undo_archive #e later, we'll inline this until we reach a function in this file
    cursnap = undo_archive.current_state(archive, assy, use_060213_format = True, exclude_layers = ('atoms',)) # cur state of child objs
    lastsnap_diffscan_layers = lastsnap.extract_layers( ('atoms',) ) # prior state of atoms & bonds, leaving only childobjs in lastsnap
    diffobj = diff_snapshots_oneway( cursnap, lastsnap ) # valid for everything except the 'atoms layer' (atoms & bonds)
    ## lastsnap.become_copy_of(cursnap) -- nevermind, just use cursnap
    lastsnap = cursnap
    del cursnap

    modify_and_diff_snap_for_changed_objects( archive, lastsnap_diffscan_layers, ('atoms',), diffobj, lastsnap._childobj_dict ) #060404
    
    lastsnap.insert_layers(lastsnap_diffscan_layers)
    new.own_this_lastsnap(lastsnap)
    priorstate.define_by_diff_from_stateplace(diffobj, new)        
    new.really_changed = not not diffobj.nonempty() # remains correct even when new's definitional content changes
    return new

def modify_and_diff_snap_for_changed_objects( archive, lastsnap_diffscan_layers, layers, diffobj, childobj_dict ): #060404
    #e rename lastsnap_diffscan_layers
    """
    [this might become a method of the undo_archive; it will certainly be generalized, as its API suggests]
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
    if (env.debug() or DEBUG_PYREX_ATOMS):
        print "\nchanged objects: %d atoms, %d bonds" % (len(chgd_atoms), len(chgd_bonds))
    # discard wrong assy atoms... can we tell by having an objkey? ... imitate collect_s_children and (mainly) collect_state
    keyknower = archive.objkey_allocator
    _key4obj = keyknower._key4obj
    changed_live = {} # both atoms & bonds; we'll classify, so more general (for future subclasses); not sure this is worth it
    changed_dead = {}
    archive._childobj_dict = childobj_dict # temporarily stored, for use by _oursQ and _liveQ methods (several calls deep) [060408]
    for akey_unused, obj in chgd_atoms.iteritems():
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
    archive._childobj_dict = None
    ## print "changed_live = %s, changed_dead = %s" % (changed_live,changed_dead)
    key4obj = keyknower.key4obj_maybe_new
    diff_attrdicts = diffobj.attrdicts
    for attrcode in archive.obj_classifier.dict_of_all_state_attrcodes.iterkeys():
        acode = attrcode[1]
        ## if acode in ('Atom', 'Bond'):
        if _KLUGE_acode_is_special_for_extract_layers(acode):
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
            attr, acode_unused = attrcode
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
        dflt = None
        del dflt
        for attrcode in clas.attrcodes_with_no_dflt:
            attr, acode_unused = attrcode
            state_attrdict = state_attrdicts[attrcode]
            val = getattr(obj, attr, _Bugval)
            oldval = state_attrdict.get(key, _UNSET_) # not sure if _UNSET_ can happen, in this no-dflt case
            if not same_vals(oldval, val):
                state_attrdict[key] = copy_val(val)
                try:
                    diff_attrdict = diff_attrdicts[attrcode]
                except:
                    print "it failed, keys are", diff_attrdicts.keys() ####@@@@ should not happen anymore
                    print " and state ones are", state_attrdicts.keys()
                    ## sys.exit(1)
                    diff_attrdict = diff_attrdicts[attrcode] = {}
                diff_attrdict[key] = oldval #k if this fails, just use setdefault with {} 
        attrcode = None
        del attrcode
    for idobj, obj in changed_dead.iteritems():
        #e if we assumed these all have same clas, we could invert loop order and heavily optimize
        key = key4obj(obj)
        clas = ci(obj)
        for attrcode in clas.dict_of_all_state_attrcodes.iterkeys():
            # (this covers the attrcodes in both clas.attrcode_dflt_pairs and clas.attrcodes_with_no_dflt)
            attr, acode_unused = attrcode
            state_attrdict = state_attrdicts[attrcode]
            val = _UNSET_ # convention for dead objects
            oldval = state_attrdict.pop(key, _UNSET_) # use pop because we know val is _UNSET_
            if oldval is not val:
                diff_attrdicts[attrcode][key] = oldval
        attrcode = None
        del attrcode
    if 1:
        from foundation.undo_archive import _undo_debug_obj, _undo_debug_message
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
    """
    basically an lval for a StateSnapshot or a (diffobj, StatePlace) pair;
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
        res._childobj_dict = None # because caller is about to modify lastsnap, but won't modify this dict to match [060408]
        return res
    #e methods for pulling the snap back to us, too... across the pointer self.diff_and_place, i guess
    def get_snap_back_to_self(self, accum_diffobj = None):
        """
        [recursive (so might not be ok in practice)]
        [if accum_diffobj is passed, accumulate the diffs we traversed into it]
        """
        # predicted bug if we try this on the initial state, so, need caller to use StatePlace there ####@@@@
        # (this bug never materialized, but I don't know why not!!! [bruce 060309])
        # sanity check re that:
        if 0 and env.debug(): #060309 # DEBUG_PYREX_ATOMS?
            print "debug: fyi: calling get_snap_back_to_self", self
                # note: typically called twice per undoable command --
                # is this due to (guess no) begin and end cp, or (guess yes) one recursive call??
        if self.lastsnap is None:
            diff, place = self.diff_and_place
            self.diff_and_place = None
            # now, we need to get snap into place (the recursive part), then steal it, apply & reverse diff, store stuff back
            place.get_snap_back_to_self(accum_diffobj = accum_diffobj) # permits steal_lastsnap to work on it
            lastsnap = place.steal_lastsnap()
            if accum_diffobj is not None: #060407 late, first implem on 060409 but not yet routinely called, for optimizing mash_attrs
                accum_diffobj.accumulate_diffs(diff)
            apply_and_reverse_diff(diff, lastsnap) # note: modifies diff and lastsnap in place; no need for copy_val
            place.define_by_diff_from_stateplace(diff, self) # place will now be healed as soon as we are
            self.lastsnap = lastsnap # inlined self.own_this_lastsnap(lastsnap)
        return
    #e and for access to it, for storing it back into assy using archive
    def get_attrdicts_for_immediate_use_only(self): # [renamed, 060309]
        """
        WARNING: these are only for immediate use without modification!
        They are shared with mutable dicts which we *will* modify the next time some other stateplace
        has this method called on it, if not sooner!
        """
        self.get_snap_back_to_self()
        return self.lastsnap.attrdicts
    
    def get_attrdicts_relative_to_lastsnap(self): #060407 late, done & always used as of 060409
        """
        WARNING: the return value depends on which stateplace last had this method
        (or get_attrdicts_for_immediate_use_only, i.e. any caller of get_snap_back_to_self) run on it!!
        [I think that's all, but whether more needs to be said ought to be analyzed sometime. ##k]
        """
        accum_diffobj = DiffObj()
        self.get_snap_back_to_self(accum_diffobj = accum_diffobj)
        return accum_diffobj.attrdicts #e might be better to get more methods into diffobj and then return diffobj here
    
    def _relative_RAM(self, priorplace): #060323
        """
        Return a guess about the RAM requirement of retaining the diff data to let this state
        be converted (by Undo) into the state represented by priorplace, also a StatePlace (??).
        Temporary kluge: this must only be called at certain times, soon after self finalized... not sure of details.
        """
        return 18 # stub
    pass # end of class StatePlace

def apply_and_reverse_diff(diff, snap):
    """
    Given a DiffObj <diff> and a StateSnapshot <snap> (both mutable), modify <snap> by applying <diff> to it,
    at the same time recording the values kicked out of <snap> into <diff>, thereby turning it into a reverse diff.
    Missing values in <snap> are represented as _UNSET_ in <diff>, in both directions (found or set in <snap>).
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
            pass # use some specialized diff restoring func for this attrcode...
            # this was WHERE I AM 060309 3:39pm.
            # [note, 060407: the feature of attrcodes with specialized diff-finding or restoring functions
            #  might still be useful someday, but turned out to be not needed for A7 and is unfinished
            #  and not actively being developed. There might be partial support for it on the scanning side.]
            # problem: this produces a val, ready to setattr into an object,
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
    """
    Classify objects seen, and save the results, and provide basic uses of the results for scanning.
    Probably can't yet handle "new-style" classes [this is being worked on as of 090206, see InstanceLike in the code].
    Doesn't handle extension types (presuming they're not InstanceTypes) [not sure].
       Note: the amount of data this stores is proportional to the number of classes and state-holding attribute declarations;
    it doesn't (and shouldn't) store any per-object info. I.e. it soon reaches a small fixed size, regardless of number of objects
    it's used to classify.
    """
    def __init__(self):
        self._clas_for_class = {}
            # maps Python classes (values of obj.__class__ for obj an
            #  InstanceType/InstanceLike, for now) to Classifications
        self.dict_of_all_state_attrcodes = {} # maps attrcodes to arbitrary values, for all state-holding attrs ever declared to us
        self.dict_of_all_Atom_chunk_attrcodes = {} # same, only for attrcodes for .molecule attribute of UNDO_SPECIALCASE_ATOM classes
        self.attrcodes_with_undo_setattr = {} # see doc in clas
        return
    
    def classify_instance(self, obj):
        """
        Obj is known to be InstanceType or InstanceLike.
        Classify it (memoizing classifications per class when possible).
        It might be a StateHolder, Data object, or neither.
        """
        if DEBUG_PYREX_ATOMS:
            if not (type(obj) is InstanceType or isinstance(obj, InstanceLike)):
                print "bug: type(%r) is not InstanceType or InstanceLike" % (obj,) ### too verbose if fails!! btw why is it a bug?
                    # and i ought to review all other uses of InstanceType in this file. [bruce 080221 re DEBUG_PYREX_ATOMS]
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
            return self.classify_class(class1)
        pass
        
    def classify_class(self, class1):
        """
        Find or make (and return) an InstanceClassification for this class;
        if you make it, memoize it and record info about its attr decls.
        """
        try:
            return self._clas_for_class[class1] # redundant when called from classify_instance, but needed for direct calls
        except KeyError:
            class_alias = getattr(class1, '_s_undo_class_alias', None)
            if class_alias and class_alias is not class1:
                clas = self._clas_for_class[class1] = self.classify_class(class_alias)
                return clas
            clas = self._clas_for_class[class1] = InstanceClassification(class1)
            self.dict_of_all_state_attrcodes.update( clas.dict_of_all_state_attrcodes )
            self.dict_of_all_Atom_chunk_attrcodes.update( clas.dict_of_all_Atom_chunk_attrcodes )
            self.attrcodes_with_undo_setattr.update( clas.attrcodes_with_undo_setattr )
#bruce 060330 not sure if the following can be fully zapped, though most of it can. Not sure how "cats" are used yet...
# wondering if acode should be classname. ###@@@
# ... ok, most of it can be zapped; here's enough to say what it was about:
##            # Store per-attrdict metainfo, which in principle could vary per-class but should be constant for one attrdict.
##            ....
##            self.kluge_attr2metainfo[attr] = attr_metainfo
##            self.kluge_attr2metainfo_from_class[attr] = clas # only for debugging
            if DEBUG_PYREX_ATOMS:
                if not env.seen_before("DEBUG_PYREX_ATOMS"):
                    from utilities.GlobalPreferences import usePyrexAtomsAndBonds
                    on = usePyrexAtomsAndBonds()
                    print "\nDEBUG_PYREX_ATOMS: Pyrex atoms is", on and "ON" or "OFF"
                    print
                print "DEBUG_PYREX_ATOMS: classify_class made InstanceClassification for %s" % (clas.class1.__name__,)
            return clas
        pass
    
    def collect_s_children(self, val, deferred_category_collectors = {}, exclude_layers = ()): #060329/060404 added exclude_layers
        """
        Collect all objects in val, and their s_children, defined as state-holding objects
        found (recursively, on these same objects) in their attributes which were
        declared S_CHILD or S_CHILDREN or S_CHILDREN_NOT_DATA using the state attribute decl system... [#doc that more precisely]
        return them as the values of a dictionary whose keys are their python id()s.
           Note: this scans through "data objects" (defined as those which define an '_s_isPureData' attribute on their class)
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
            """
            pass me to transclose; I'll store objs into dict1 when I reach them from a child attribute of obj; all objs are
            assumed to be instances of the kind acceptable to classify_instance.
            """
            # note, obj1 might be (what we consider) either a StateHolder or a Data object (or neither).
            # Its clas will know what to do.
            if 1: #bruce 090206 revised ## env_debug or DEBUG_PYREX_ATOMS: 
                #bruce 060314: realized there was a bug in scan_val -- it stops at all elements of lists, tuples, and dicts,
                # rather than recursing as intended and only stopping at InstanceType/InstanceLike objects.
                # (copy_val and same_vals (py implems anyway) don't have this bug.)
                # Does this happen in practice in Undo, or do we so far only store child objs 1 level deep in lists or dicts?
                # (Apparently it never happens, since following debug code doesn't print anything.)
                # What would the following code do if it happened?
                # Would it be most efficient/flexible/useful to decide this is a good feature of scan_val,
                # and make this code tolerate it?
                #bruce 060315: decided to fix scan_val.
                ##k Once this is tested, should this check depend on atom_debug?
                # Maybe in classify_instance? (Maybe already there?) ###@@@
                if not isinstance(obj1, InstanceLike): #bruce 080325, 090206 revised
                    print "debug: bug: scan_children hit obj at %#x of type %r" % (id(obj1), type(obj1))
            clas = classify_instance(obj1)
            if clas.obj_is_data(obj1):
                data_objs[id(obj1)] = obj1
            def func(obj):
                dict1[id(obj)] = obj
            clas.scan_children( obj1, func,   #k is scan_children correct for obj1 being data?
                                deferred_category_collectors = deferred_category_collectors,
                                exclude_layers = exclude_layers )
        allobjs = transclose( saw, obj_and_dict) #e rename both args
        if DEBUG_PYREX_ATOMS: ## 0 and env.debug(): 
            print "atom_debug: collect_s_children had %d roots, from which it reached %d objs, of which %d were data" % \
                  (len(saw), len(allobjs), len(data_objs))
        # allobjs includes both state-holding and data-holding objects. Remove the latter.
        for key in data_objs.iterkeys():
            del allobjs[key]
        return allobjs # from collect_s_children

    def collect_state(self, objdict, keyknower, exclude_layers = ()): #060329/060404 added exclude_layers
        """
        Given a dict from id(obj) to obj, which is already transclosed to include all objects of interest,
        ensure all these objs have objkeys (allocating them from keyknower (an objkey_allocator instance) as needed),
        and grab the values of all their state-holding attrs,
        and return this in the form of a StateSnapshot object.
        #e In future we'll provide a differential version too.
        """
        key4obj = keyknower.key4obj_maybe_new # or our arg could just be this method
        attrcodes = self.dict_of_all_state_attrcodes.keys()
        if exclude_layers:
            assert exclude_layers == ('atoms',) # the only one we support right here
            attrcodes = filter( lambda (attr, acode):
                                ## acode not in ('Atom', 'Bond'),
                                not _KLUGE_acode_is_special_for_extract_layers(acode),
                                attrcodes )
                # this is required, otherwise insert_layers (into this) will complain about these layers already being there
        snapshot = StateSnapshot(attrcodes)
            # make a place to keep all the values we're about to grab
        attrdicts = snapshot.attrdicts
        len1 = len(objdict)
        if DEBUG_PYREX_ATOMS:
            print "\nDEBUG_PYREX_ATOMS: collect_state len(objdict) = %d" % len1
        for obj in objdict.itervalues():
            key = key4obj(obj)
            clas = self.classify_instance(obj)
            if DEBUG_PYREX_ATOMS: ## if 0 and 'ENABLE SLOW TEST CODE': # @@@@@@@ 080221
                if exclude_layers:
                    assert exclude_layers == ('atoms',) # the only one we support right here
                    ## print "remove when works, once this code is debugged -- too slow!" ### bruce 071114
                    ## if not ( clas.class1.__name__ not in ('Atom', 'Bond') ):
                    if getattr(obj, '_s_undo_specialcase', None) in (UNDO_SPECIALCASE_ATOM,
                                                                     UNDO_SPECIALCASE_BOND):
                        print "bug: exclude_layers didn't stop us from seeing", obj
            # hmm, use attrs in clas or use __dict__? Either one might be way too big... start with smaller one? nah. guess.
            # also we might as well use getattr and be more flexible (not depending on __dict__ to exist). Ok, use getattr.
            # Do we optim dflt values of attrs? We ought to... even when we're differential, we're not *always* differential.
            ###e need to teach clas to know those, then.
            for attrcode, dflt in clas.attrcode_dflt_pairs: # for attrs holding state (S_DATA, S_CHILD*, S_PARENT*, S_REF*) with dflts
                attr, acode_unused = attrcode
                if clas.exclude(attr, exclude_layers):
                    if env.debug() or DEBUG_PYREX_ATOMS:###@@@ rm when works
                        print "debug: collect_state exclude_layers1 excludes", attr, "of", obj
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
                attr, acode_unused = attrcode
                if clas.exclude(attr, exclude_layers):
                    if env.debug() or DEBUG_PYREX_ATOMS:###@@@ rm when works
                        print "debug: collect_state exclude_layers2 excludes", attr, "of", obj
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
        """
        Given an obj we have saved state for, reset each attr we might save
        to its default value (which might be "missing"??), if it has one.
        [#e someday we might also reset S_CACHE attrs, but not for now.]
        """
        from foundation.undo_archive import _undo_debug_obj, _undo_debug_message
        clas = self.classify_instance(obj)
        for (attr, acode_unused), dflt in clas.attrcode_dflt_pairs:
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
    
    pass # end of class obj_classifier

# ==

class InstanceLike(object): #bruce 090206; remove 'object' to make it safer (more like old code) ####
    """
    Common superclass for classes whose instances should be considered
    "instancelike" by same_vals, copy_val, scan_vals, is_mutable, and Undo
    (meaning they should participate in various APIs where they can define
    special methods/attrs to get special behavior).
    
    (Where old code checked type(obj) == InstanceType, new code can check
     isinstance(obj, InstanceLike), so it works for new-style classes.)
    """
    pass

class IdentityCopyMixin(InstanceLike): # by EricM
    def _copyOfObject(self):
        """
        Implements the copying of an object for copy_val.  For objects
        which care about their identity (which inherit from
        IdentityCopyMixin), this will return a new reference to the
        same object.  There is no need to override this method.
        Compare this with the behavior of DataMixin._copyOfObject().
        """
        return self

    def _isIdentityCopyMixin(self):
        """
        This method acts as a flag allowing us to tell the difference
        between things which inherit from DataMixin and those which
        inherit from IdentityCopyMixin.  Any given class should only
        inherit from one of those two mixin interfaces (or from StateMixin,
        which inherits from IdentityCopyMixin).  So, both
        _isIdentityCopyMixin and _s_isPureData should not be defined
        on the same object.  This can be used to check coverage of
        types in copy_InstanceType().
        """
        pass
    pass

# Review: The only known classes which need IdentityCopyMixin but not StateMixin
# are Elem, AtomType, and Movie (as of 080321). In the case of Elem and AtomType,
# this is because they are immutable (EricM suggested an Immutable class
# to document that). In the case of Movie, it's not immutable, but it's free of
# any state known to Undo. If more examples of this arise, it will make sense
# to classify them and figure out if they should inherit from any new declarative
# classes. [bruce 080321 comment]

class StateMixin( _eq_id_mixin_, IdentityCopyMixin ):
    """
    Convenience mixin for classes that contain state-attribute (_s_attr)
    declarations, to help them follow the rules for __eq__,
    to avoid debug warnings when they contain no attr decls yet,
    and perhaps to provide convenience methods (none are yet defined).

    Only useful for classes which contain undoable state, as of 071009.
    """
    # try not having this:
    ## _s_attr__StateMixin__fake = S_IGNORE
        # decl for fake attr __fake (name-mangled to _StateMixin__fake
        # to be private to this mixin class),
        # to avoid warnings about classes with no declared state attrs
        # without requiring them to be registered (which might be nim)
        # (which is ok, since if you added this mixin to them, you must
        #  have thought about whether they needed such decls)
    def _undo_update(self):
        """
        #doc [see docstring in chunk]
        """
        return
    pass

class DataMixin(InstanceLike):
    """
    Convenience mixin for classes that act as 'data' when present in
    values of declared state-holding attributes. Provides method stubs
    to remind you when you haven't defined a necessary method. Makes
    sure state system treats this object as data (and doesn't warn
    about it). All such data-like classes which may be handled by
    copy_val must inherit DataMixin.
    """
    _s_isPureData = None # value is arbitrary; only presence of attr matters
        # note: presence of this attribute makes sure this object is treated as data.
        # (this is a kluge, and an isinstance test might make more sense,
        #  but at the moment that might be an import cycle issue.)
        # [by EricM, revised by Bruce 090206]
    def _copyOfObject(self):
        """
        This method must be defined in subclasses to implement
        the copying of an object for copy_val. For data
        objects (which inherit from DataMixin, or define
        _s_isPureData), this should return a newly allocated object
        which will be __eq__ to the original, but which will have a
        different id(). Implementation of this method must be
        compatible with the implementation of __eq__ for this class.

        This method has a name which appears private, solely for performance
        reasons. In particular, InvalMixin.__getattr__() has a fast
        return for attributes which start with an underscore. Many
        objects (like atoms) inherit from InvalMixin, and looking up
        non-existent attributes on them takes significantly longer if
        the attribute name does not start with underscore. In
        general, such objects should inherit from IdentityCopyMixin as
        well, and thus have _copyOfObject defined in order to avoid
        exception processing overhead in copy_InstanceType(), so it
        doesn't really matter. Should something slip through the
        cracks, at least we're only imposing one slowdown on the copy,
        and not two.
        """
        print "_copyOfObject needs to be overridden in", self
        print "  (implem must be compatible with __eq__)"
        return self
    def __eq__(self, other):
        print "__eq__ needs to be overridden in", self
        print "  (implem must be compatible with _copyOfObject; " \
              "don't forget to avoid '==' when comparing Numeric arrays)"
        return self is other
    def __ne__(self, other):
        return not (self == other) 
            # this uses the __eq__ above, or one which the specific class defined
    pass

# ===

# test code

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
