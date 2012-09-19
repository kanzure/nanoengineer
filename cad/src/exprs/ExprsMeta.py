# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
ExprsMeta.py -- one metaclass, to take care of whatever is best handled using a metaclass,
and intended to be used for all or most classes in this module.

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

===

####### need to insert improved text for the following, drafted 061025 in notesfile: ######@@@@@@

here it is, not quite done, but i might still edit it in the text file, and/or wikify it

==

Python provides several ways for class attributes to determine how instance attributes are computed.
To summarize: the class attributes can be constants, functions, or other descriptors,
with corresponding instance attribute accesses resulting in constants, bound methods, or fairly arbitrary behavior.

We want to add a few specific ways of our own:

- class attributes which are formulas in _self,
  for which instance.attr should be a read-only per-instance memoized invalidatable/recomputable value
  computed by the formula

- class attributes which are like a "descriptor expression", but with the "descriptor" knowing the class and attr
it was assigned to (which ordinary ones don't know):

  - for example, resulting in instance.attr acting like a dict of individually invalidatable/recomputable values,
  defined by a method or formula on the key, extensible as new keys are used,
  with the permitted keys either unlimited, fitting some type or pattern, or listed explicitly by a
  once-computable method or formula

  [###e (details unclear -- does this mean all exprs include details of what gets memoized, at what level inside??)]

- specially-named methods, assigned to _prefix_attr rather than directly to attr, which nonetheless control what
instance.attr does (similarly to one of the ways mentioned above), with subclasses able to override superclasses
about attr even if they define its behavior by assigning to different class attributes (one to attr itself,
one to _prefix1_attr, one to _prefix2_attr). (This way is most convenient when you want to express the behavior using
Python code rather than as formulas.)

We find a metaclass to be the simplest way of achieving certain key aspects of those desires:

- Descriptor exprs might be shared among attrs or between classes -- they don't know their cls/attr location,
and it's not even unique (meaning they'd be wrong to cache cls/attr info inside themselves, even if they knew it).

A metaclass can wrap descriptors (or the like) with this location info, with the resulting wrapped exprs
being unique (so they can be allowed to cache data which depends on this location info). Effectively, it can
wrap things that follow our own descriptor protocol to produce things that follow Python's.

- Overriding of attr assignments doesn't normally affect related attrs; if some class defines contradicting
values for attr and _prefix1_attr and _prefix2_attr, all meant to control instance.attr in different ways,
the defn to follow should be the one defined in the innermost class, but you can't easily tell which one that is.
(If Python copies superclass dicts into subclass dicts, maybe you can't tell at all, absent metaclasses, except by
something as klugy as comparing line numbers found inside function code objects and their classes.)

  - We could solve this just by recording the class and attr of each def, as we'll do to solve the prior problem...
  ### could we really use that info to solve this? should we?

  - But what we actually do is have the metaclass create something directly on the attr,
  which says how it's supposed to be
  defined in that class (and is a descriptor which causes that to actually happen in the right way).

  This scheme has the advantage of dispensing with any need for __getattr__ (I think).

  (Note, it could also do it by creating a special prefix attr saying
   which other prefix attr controls the def. Should it?? ####)

The actual creation of the class/attr-specific descriptor for runtime use is best done lazily,
on first use of that attr in an instance. This lets it more safely import code, more easily
access inherited class attrs, etc... and lets most of the system be more similar to non-metaclass-based code.

The metaclass just records enough info, and makes it active in the right places, to allow this to happen properly.


======= old text, not sure it's all obs/redundant now:

Reasons we needed a metaclass, and some implementation subtleties:

- If there are ways of defining how self.attr behaves using different class attributes (e.g. attr or _C_attr or _CV_attr),
overriding by subclasses would not normally work as intended if subclasses tried to override different attrs
than the ones providing the superclass behavior. (E.g., defining _C_attr in a subclass would not override a formula or constant
assigned directly to attr in a superclass.)

ExprsMeta solves this problem by detecting each class's contributions to the intended definition of attr (for any attr)
from any class attributes related to attr (e.g. attr or _xxx_attr), and encoding these as descriptors on attr itself.

(Those descriptors might later replace themselves when first used in a given class, but only with descriptors on the same attr.)

- Some objects assigned to attr in a class don't have enough info to act well as descriptors, and/or might be shared
inappropriately on multiple attrs in the same or different classes. (Formulas on _self, assigned to attr, can have both problems.)

ExprsMeta replaces such objects with unshared, wrapped versions which know the attr they're assigned to.

Note that it only does this in the class in which they are syntactically defined -- they might be used from either that class
or a subclass of it, and if they replace themselves again when used, they should worry about that. Python probably copies refs
to them into each class's __dict__, but these copies are all shared. This means they should not modify themselves in ways which
depend on which subclass they're used from.

For example, if a descriptor assigned by ExprsMeta makes use of other attributes besides its main definining attribute,
those other attributes might be overridden independently of the main one, which means their values need to be looked for
independently in each class the descriptor is used in. This means two things:

1. The descriptor needs to cache its knowledge about how to work in a specific class, in that class, not in itself
(not even if it's already attached to that class, since it might be attached to both a class and its subclass).
It should do this by creating a new descriptor (containing that class-specific knowledge) and assigning it only into one class.

2. In case I'm wrong about Python copying superclass __dict__ refs into subclass __dicts__, or in case this behavior changes,
or in case Python does this copying lazily rather than at class-definition time, each class-specific descriptor should verify
it's used from the correct class each time. If it wants to work correctly when that fails (rather than just assertfailing),
it should act just like a non-class-specific descriptor and create a new class-specific copy assigned to the subclass it's used from.

Note that the simplest scheme combines points 1 and 2 by making each of these descriptors the same -- it caches info for being used
from the class it's initially assigned to, but always checks this and creates a subclass-specific descriptor (and delegates that
use to it) if used from a subclass. All we lose by fully merging those points is the check on my beliefs about Python.
Hopefully a simple flag can handle that by asserting (warning when false) that the copying into a subclass happens at most once.


What ExprsMeta handles specifically:

- formulas on _self assigned directly to attr (in a class)

- _C_attr methods (or formulas??), making use of optional _TYPE_attr or _DEFAULT_attr declarations (#k can those decls be formulas??)

- _CV_attr methods (or formulas??), making use of optional _CK_attr methods (or formulas??), and/or other sorts of decls as above

- _options (abbrev for multiple _DEFAULT_), but not _args

"""

# == imports

# from python library

from idlelib.Delegator import Delegator

# from modules in cad/src

from utilities.constants import remove_prefix
##from env import seen_before
from utilities.debug import print_compact_traceback, print_compact_stack

# from this exprs package in cad/src

from exprs.py_utils import printnim, printfyi

from exprs.lvals import Lval, LvalDict2, call_but_discard_tracked_usage

from exprs.Exprs import is_Expr
from exprs.Exprs import is_pure_expr
from exprs.Exprs import canon_expr
from exprs.Exprs import is_Expr_pyinstance
from exprs.Exprs import getattr_Expr
from exprs.Exprs import constant_Expr
from exprs.Exprs import expr_serno
from exprs.Exprs import expr_is_Instance
from exprs.Exprs import is_Expr_pyclass
from exprs.__Symbols__ import _E_ATTR, _self

# ==

# added 061201: as of 061204 not sure if still needed (guess: no), tho still active
FAKE_ATTR = "<FAKE_ATTR>" # not a possible attr name, but a string in case used in __repr__
FAKE_CLSNAME = "<FAKE_CLSNAME>"

class ClassAttrSpecific_NonDataDescriptor(object):
    """
    Abstract class for descriptors which cache class- and attr- specific info
    (according to the scheme described in the ExprsMeta module's docstring).

    Actually, there's a pair of abstract classes, one each for Data and NonData descriptors.

    To make our implem of self.copy_for_subclass() correct in our subclasses (so they needn't
    override it), we encourage them to not redefine __init__, but to rely on our implem of __init__
    which stores all its arguments in fixed attrs of self, namely clsname, attr, args, and kws,
    and then calls self._init1(). [self.cls itself is not yet known, but must be set before first use,
    by calling _ExprsMeta__set_cls.]

    TODO: rename _init1 to something more specific.
    """
    __copycount = 0
    cls = None
    clsname = attr = '<unset>' # probably never seen
    def __init__(self, clsname, attr, *args, **kws):
        # to simplify
        #e perhaps this got called from a subclass init method, which stored some additional info of its own,
        # but most subclasses can just let us store args/kws and use that, and not need to override copy_for_subclass. [#k]
        self.clsname = clsname #######@@@@@@ fix for this in CV_rule too
        ## self.cls = cls # assume this is the class we'll be assigned into (though we might be used from it or any subclass)
        self.attr = attr # assume this is the attr of that class we'll be assigned into
        self.args = args
        self.kws = kws
            ###e Q: If self (in subclass methods) needs to compute things which copy_for_subclass should copy
            # into a copy of self made for a subclass of self.cls, rather than recomputing on its own,
            # should they be stored by self into self.kws,
            # then detected in copy.kws by copy._init1?
            # (Or, kept in copy.kws, and used directly from there by copy's other methods)??
            # Example: our formula-handling subclass might need to modify its arg val from the one it gets passed.
            # (Or it might turn out that's done before calling it, so this issue might not come up for that example.)
        self._init1()
        #e super init?
    def __repr__(self): #061205 moved this here from a subclass, and removed the worse ones in other subclasses
        return "<%s at %#x for %r in %r>" % (self.__class__.__name__, id(self), self.attr, self.clsname)
    def _init1(self):
        """
        #doc
        [subclasses can override this]
        """
        pass
    def _ExprsMeta__set_cls(self, cls):
        """
        [private method for ExprsMeta to call when it knows the defining class]
        """
        self.cls = cls
        if self.clsname == FAKE_CLSNAME:
            self.clsname = cls.__name__
        else:
            assert self.clsname == cls.__name__ #k
        #e should we store only the class id and name, to avoid ref cycles? Not very important since classes are not freed too often.
        return
    def _ExprsMeta__set_attr(self, attr): # see class State_helper discussion for motivation
        """
        [private method for ExprsMeta to call when it knows the defining attr]
        """
        # 061201, not always called(?) or needed, experimental
        print "called _ExprsMeta__set_attr",self,attr
            ####k does it ever happen? if not, it's probably obs; even if so, might be unneeded [cmt 061204]
            # update: this probably never happens, since until 071107, it referenced
            # an undefined symbol FAKE_ATTRNAME (probably a typo)
        if self.attr == FAKE_ATTR:
            self.attr = attr
        else:
            assert self.attr == attr, "%r already has an attr, but another one %r is trying to be set in it" % (self, attr)
        return
    def check(self, cls2):
        ###e remove all calls of this when it works (need to optim)
        cls = self.cls
        assert cls is not None, "self.cls None in check, self.clsname = %r, self.attr = %r" % \
               (self.clsname, self.attr)
               # need to call _ExprsMeta__set_cls before now
        assert self.clsname == cls.__name__, "self.clsname %r != cls.__name__ %r for self %r, cls %r" % \
               (self.clsname, cls.__name__, self, cls)
            # make sure no one changed this since we last checked
        attr = self.attr
        assert cls.__dict__[attr] is self
        if cls2 is not None: #k can that ever fail??
            assert issubclass(cls2, cls), "cls2 should be subclass of cls (or same class): %r subclass of %r" % (cls2, cls)
        return
    def __get__(self, obj, cls):
        """
        [subclasses should NOT override this -- override get_for_our_cls instead]
        """
        # WARNING: similar code to __set__ in a subclass
        self.check(cls) #e remove when works (need to optim)
        if obj is None:
            ## print_compact_stack("fyi, __get__ direct from class of attr %r in obj %r: " % (self.attr, self))
                # Note: for what this is about, see long comment near printnim in FormulaScanner far below. [061101]
                #
                # Update: disabled print, since this now happens routinely in ObjAttr_StateRef
                # for getting a data_descriptor_Expr_descriptor [bruce 070815]
                #
                # Note: this print was also causing tracebacks in pychecker (see EricM email to cad list),
                # so it's lucky that we no longer need it. But it was legitimate, so that was a pychecker bug
                # which might bite us in the future. [bruce 070817]
            return self
        assert cls is not None, "I don't know if this ever happens, or what it means if it does, or how to handle it" #k in py docs
            #e remove when works (need to optim)
        if cls is not self.cls:
            copy = self.copy_for_subclass(cls) # e.g. from 'InstanceOrExpr' to 'Rect'
            attr = self.attr
            ## cls.__dict__[attr] = copy # oops, this doesn't work: TypeError: object does not support item assignment
            # turns out it's a dictproxy object (created on the fly, like unbound methods are), as (I guess) is any new style
            # class's __dict__. Guess: this is so you can't violate a descriptor's ability to control what set/del does.
            # You can still modify the actual class dict using setattr -- if the descriptor permits.
            # So, what to do? Can I get my descriptor to permit this? Depends which kind it is! *This* class can't handle it
            # (no __set__ method), but which one do I actually use? (And for that matter, would they both even work re my
            # assumptions about access order when I wrote them? #####k)
            # Hmm -- CV_rule uses a nondata desc (no __set__, problem), but C_rule uses a data desc. Why is that?
            # C_rule comment says it has to be a data descriptor. CV_rule likes to be overridden by an instance it makes,
            # so likes to be non-data (though it does have code to not require this). Conclusion: simplest fix is to
            # use only the subclass that has __set__, and make that __set__ sometimes work, and change the above code to use it.
            # I will try this for now [061103 830p], then look for a better fix someday, e.g. not needing this copy at all
            # (I forget why I needed it). ... wait, the suggestion fails -- it would get into __set__, but then what could that do
            # to actually change the class dict? It could store something in the instance but not in the class!!
            # Does that mean it's reversed -- without __set__ I'm ok since I can use setattr? If so, I can fix this by
            # changing C_rule to not store into same attr in instance.__dict__ so it can use a non-data descriptor.
            # But WAIT AGAIN, the descriptor will gate access to the instance, not necessarily to the class -- we'll have to try it.
            setattr( cls, attr, copy) # this might fail in the DataDescriptor subclass used in C_rule, but I don't know. ###k
            if 0:
                print "setattr( cls, attr, copy) worked for supporting %r from %r for attr %r in %r" % \
                      (cls , self.cls, attr, self) ####@@@@ self is relevant so we see which kind of descriptor it worked for
            # btw it also might "succeed but not have the desired effect". What's the predicted bug if it silently has no effect? ##k
            return copy.__get__(obj, cls)
        return self.get_for_our_cls(obj)
    # we have no __set__ or __delete__ methods, since we need to be a non-data descriptor.
    def get_for_our_cls(self, obj):
        """
        [Subclass should implement]
        do the __get__ for our class (initializing our class-specific info if necessary)
        """
        return None
    def copy_for_subclass(self, cls):
        if 0:
            printfyi("copy_for_subclass from %r to %r" % (self.cls.__name__, cls.__name__))###@@@
        copy = self.__class__(cls.__name__, self.attr, *self.args, **self.kws)
        copy._ExprsMeta__set_cls(cls)
        copy.__copycount = self.__copycount + 1 #k needed anymore??
##        if copy.__copycount > 1:
##            if not seen_before("ClassAttrSpecific_{Non,}DataDescriptor copied again"):
##                print "once-per-session developer warning: this copy got copied again:", \
##                      self, "for class %s" % self.cls.__name__, "copied as", copy, "for class %s" % cls.__name__
                # Note: this may be normal for Rect -> Spacer, and it's probably not an error at all.
                # If this keeps seeming true, remove the message.
                # (For that matter, I could probably remove the copying behavior entirely. ##k) [061205 comment]
                # Update 070323: it's happened for more cases of inheritance chains, all legit, e.g.
                # for '_delegate' in 'DraggablyBoxed' and for 'per_frame_state' in '_cmd_DrawOnSurface_BG',
                # and AFAIK it's ok when this happens, so I'm removing the warning.
        return copy
    pass # end of class ClassAttrSpecific_NonDataDescriptor

class ClassAttrSpecific_DataDescriptor(ClassAttrSpecific_NonDataDescriptor):
    """
    Like our superclass, but has __set__ and __delete__ methods so as to be a data descriptor.
    (Defining either method would be enough to make Python treat us as a data descriptor,
     but we'd rather complain equally about either one running, so we define both.)

    Our implems of __set__ and __delete__ just assert 0; subclasses can override them
    (with other errors or to make them work), but don't need to.

    WARNING: if subclasses did intend to override them, most likely they'd need overhead code
    like our superclass has in __get__, so in practice such overriding is not yet supported --
    to support it, we'd want to add that sort of code to this class (perhaps sharing common code
    with our superclass's __get__).

    [FYI about when to use a data or non-data descriptor:
     - If a Python descriptor (of any kind, not just the kind created by one of these classes)
     wants to store info of its own in instance.__dict__[attr], it has to be a data descriptor,
     since otherwise that info would be retrieved directly by getattr, rather than going through the descriptor.
     (It might need to intercept that (for example) either to alter the data, or record the fact of its retrieval.)
     - If it doesn't want to store anything there, then it can be either data or non-data. (Of course it has to be "data"
     if it wants to support setattr or delattr.)
     - If it wants to store something there and does want getattr to retrieve it directly (as an optim),
     then it ought to be a non-data descriptor, asusming it doesn't need to support set or del.
    ]
    """
    def __set__(self, obj, val):
        """
        [subclasses should NOT override this -- override set_for_our_cls instead]
        """
        # WARNING: similar code to __get__ in our superclass
        if obj is None:
            print_compact_stack("fyi, __set__ direct from class of attr %r in obj %r: " % (self.attr, self)) ####@@@@ ever happens?
                # what this is about -- see long comment near printnim in FormulaScanner far below [061101]
            return
        cls = obj.__class__ #### TOTAL GUESS, but otherwise I have to panic since cls is not passed in [061117]
        self.check(cls) #e remove when works (need to optim)
##        assert cls is not None, "I don't know if this ever happens, or what it means if it does, or how to handle it" #k in py docs
##            #e remove when works (need to optim)
        if cls is not self.cls:
            copy = self.copy_for_subclass(cls) # e.g. from 'InstanceOrExpr' to 'Rect'
            attr = self.attr
            setattr( cls, attr, copy) # this might fail in the DataDescriptor subclass used in C_rule, but I don't know. ###k
            if 1:
                print "setattr( cls, attr, copy) worked for supporting __set__ %r from %r for attr %r in %r" % \
                      (cls , self.cls, attr, self) ####@@@@ self is relevant so we see which kind of descriptor it worked for
            # btw it also might "succeed but not have the desired effect". What's the predicted bug if it silently has no effect? ##k
            return copy.__set__(obj, val)
        return self.set_for_our_cls(obj, val)
    def set_for_our_cls(self, obj, val):
        """
        [Subclass should implement -- do the __set__ for our class
         (initializing our class-specific info if necessary)]
        """
        assert 0, "subclass %r of %r should implement set_for_our_cls" % (self.__class__, self)
    def __delete__(self, *args): # note: descriptor protocol wants __delete__, not __del__!
        print "note: ClassAttrSpecific_DataDescriptor.__delete__ is about to assert 0"
        assert 0, "__delete__ is not yet supported in this abstract class"
    pass # end of class ClassAttrSpecific_DataDescriptor

# ==

class C_rule(ClassAttrSpecific_DataDescriptor):
    """
    One of these should be stored on attr by ExprsMeta when it finds a _C_attr compute method,
    formula (if supported #k), or constant,
    or when it finds a formula directly on attr.
    """
    # implem note: this class has to be a data descriptor, because it wants to store info of its own in instance.__dict__[attr],
    # without that info being retrieved as the value of instance.attr. If it would be less lazy (and probably less efficient too)
    # and store that info somewhere else, it wouldn't matter whether it was a data or non-data descriptor.
    def get_for_our_cls(self, instance):
        # make sure cls-specific info is present -- we might have some, in the form of _TYPE_ decls around compute rule?? not sure. ##e
        # (none for now)

        # now find instance-specific info --
        # namely an Lval object for instance.attr, which we store in instance.__dict__[attr]
        # (though in theory, we could store it anywhere, as long as we'd find a
        #  different one for each instance, and delete it when instance got deleted)
        attr = self.attr
        try:
            lval = instance.__dict__[attr]
        except KeyError:
            # (this happens once per attr per instance)
            # Make a compute method for instance.attr, letting instance have first dibs (in case it's customized this attr),
            # otherwise using self's default method.
            # NOTE: this would not work for constant formulas like _DEFAULT_color = gray, except for the call of canon_expr (to be added)
            # on all _DEFAULT_attr values -- otherwise instance.attr would just grab gray, never going through this code which
            # looks for an override. In this way alone, _DEFAULT_attr is more powerful than an ordinary (private) attr.
            # Beware -- this may seem to mask the bug in which private attrs can also be overridden by customizing option values.
            # (As of 061101 that bug is fixed, except it was never tested for either before or after the fix.)
            compute_method = self.compute_method_from_customized_instance(instance)
##            if compute_method:
##                printnim("custom override should only work for _DEFAULT_! not private attr formulas")#but we don't know prefix here
##                #k when we do know prefix here, should we decide _DEFAULT_ is special here, or pass to above method to ask instance??
            if not compute_method:
                compute_method = self.make_compute_method_for_instance(instance)
            # make a new Lval object from the compute_method
            lval = instance.__dict__[attr] = Lval(compute_method)
        return lval.get_value() # this does usage tracking, validation-checking, recompute if needed
            # Notes:
            # [from when this code was in class _C_rule used by InvalidatableAttrsMixin in lvals.py; probably still applicable now]
            # - There's a reference cycle between compute_method and instance, which is a memory leak.
            # This could be fixed by using a special Lval (stored in self, not instance, but with data stored in instance)
            # which we'd pass instance to on each use. (Or maybe a good solution is a C-coded metaclass, for making instance?)
            # - The __set__ in our superclass detects the error of the compute method setting the attr itself. Good enough for now.
            # Someday, if we use a special Lval object that is passed self and enough into to notice that itself,
            # then we could permit compute objects to do that, if desired. But the motivation to permit that is low.
            # - There is no provision for direct access to the Lval object (e.g. to directly call its .set_formula method).
            # We could add one if needed, but I don't know the best way. Maybe find this property (self) and use a get_lval method,
            # which is passed the instance? Or, setattr(instance, '_lval_' + attr, lval).
    def compute_method_from_customized_instance(self, instance):
        """
        See if we permit instance to customize self.attr's formula, and if instance has done so;
        if so, return a compute method from that; else return None.
        """
        permit_override = self.kws.get('permit_override', False) #e do in __init__ with pop, so we can check for unknown options?
        if not permit_override:
            return None
        try:
            instance.custom_compute_method # defined e.g. by InstanceOrExpr
        except AttributeError:
            return None
        printfyi("DEPRECATED: compute_method_from_customized_instance (since _DEFAULT_ is); attr %r" % (self.attr,)) ##k 061103
        return instance.custom_compute_method(self.attr) # a method or None
    def make_compute_method_for_instance(self, instance):
        """
        #doc;
        doesn't consider per-instance customized compute methods.
        """
        assert 0, "subclass should implement this"
    pass # end of class C_rule

class C_rule_for_method(C_rule):
    def _init1(self):
        ## () = self.args is a syntax error!
        assert len(self.args) == 0
        #e could/should we assert no unknown kws??
    def make_compute_method_for_instance(self, instance):
        return getattr(instance, '_C_' + self.attr) # kluge, slightly, but it's the simplest and most efficient way
        ###e maybe a better way is to grab the function from cls.__dict__ and call its __get__?
    pass

class C_rule_for_formula(C_rule):
    def _init1(self):
        (self.formula,) = self.args
        #e could/should we assert no unknown kws??
    def make_compute_method_for_instance(self, instance):
        return self.formula._e_compute_method(instance, '$' + self.attr) # index arg is a guess, 061110
    pass

def choose_C_rule_for_val(clsname, attr, val, **kws):
    """
    return a new object made from the correct class out of
    C_rule_for_method or C_rule_for_formula or a val-specified wrapper,
    depending on val
    """
    if is_pure_expr(val):
        # assume val is a formula on _self
        # first scan it for subformulas that need replacement, and return replaced version, also recording info in scanner
        scanner = kws.pop('formula_scanner', None)
        if scanner:
##            val0 = val # debug msg only
            val = scanner.scan(val, attr) #e more args?
##            if val0 is not val:
##                print "scanner replaces %r by %r" % (val0, val)
##            else:
##                print "scanner leaves unchanged %r" % (val0,)
        wrapper = getattr(val, '_e_wants_this_descriptor_wrapper', None) # new feature 061203; 061204 moved after scanner as bugfix
        if wrapper:
            assert issubclass(wrapper, ClassAttrSpecific_NonDataDescriptor)
            return wrapper(clsname, attr, val, **kws)
        flag = getattr(val, '_e_is_lval_formula', False)
        assert not flag # 061203
        if flag: # new feature 061117, for State macro and the like [note 061203: that State macro is obs, new one doesn't use this]
            # it's a formula for an lval, rather than for a val!
            print "should not happen yet: val = %r, flag = %r" % (val,flag) # an expr or so??
            return C_rule_for_lval_formula(clsname, attr, val, **kws)
        return C_rule_for_formula(clsname, attr, val, **kws)
    elif is_Expr(val):
        print("Instance case needs review in choose_C_rule_for_val")
            # does this ever happen? in theory, it can... (depending on needs_wrap_by_ExprsMeta)
        return val ###k not sure caller can take this
    #e support constant val?? not for now.
    else:
        return C_rule_for_method(clsname, attr, **kws)
        ###KLUGE (should change): they get val as a bound method directly from cls, knowing it came from _C_attr
    pass

class C_rule_for_lval_formula(ClassAttrSpecific_DataDescriptor): #061117 - review all comments before done! ###OBS as of 061203
    """
    #doc;
    used for obs-061117 version of State macro,
    not sure it'll ever be used as of newer 061203 version of it,
    maybe for its #e-refexpr
    """
    ###nim: type-formula
    def _init1(self):
        (self.lval_formula,) = self.args
        assert 0, "no one should be calling this yet...." #####@@@@@@
    def make_lval_for_instance(self, instance):
        """
        return an lval (found or made by our formula) for this instance
        """
        print "make_lval_for_instance",(self, instance)#####@@@@@
        #e not sure what to do if this formula turns out to be time-dependent... what should be invalidated if it does?? ####
        # for now, just be safe and discard tracked usage, tho it might be better to replace the lval with a new one if it invals.#e
        index = '$' + self.attr # guess, 061117
        lval = eval_and_discard_tracked_usage( self.lval_formula, instance, index)
        return lval
    def get_for_our_cls(self, instance):
        print "get_for_our_cls",(self, self.attr, instance, )#####@@@@@
        attr = self.attr
        try:
            lval = instance.__dict__[attr]
        except KeyError:
            # (this happens at most once per attr per instance, iff the attr is gotten-from before it's ever been set, in this instance)
            lval = instance.__dict__[attr] = self.make_lval_for_instance(instance)
        if not lval.can_get_value(): ###e should optim by doing this only on exception from get_value
            # note: this has to be checked whether we found or made the lval
            # preventable by prior set (in this instance or a prior one), or by lval having an initval_compute_method
            raise AttributeError, "attr %r hasn't been set yet in class %r" % (attr, self.cls)
                ####k or LvalError_ValueIsUnset??? I think not... when less tired, explain why. [061117 late]
        # old code, whose index might be needed in state_Expr ##k:
##            index = '$$' + self.attr # guess, 061117
##            initval = eval_and_discard_tracked_usage(initval_expr, instance, index)
##                # note: we need to discard tracked usage from initval_computer
##                # (which is not an error -- initval_expr is allowed to be time-dependent,
##                #   but we don't want to recompute anything when it changes)
##                # note: this is not evaluated until the moment it's needed; that's important, since
##                # (1) it's legal for this to be an error to eval at times before when we need it;
##                # (2) its value might change before we need it, and it's defined to give us the value at the time of first need.
##            lval.set_constant_value(initval) # needed so .get_value() will work; .get_value() is still needed for its usage-tracking
        return lval.get_value() # this does usage tracking, validation-checking, recompute if needed
    def set_for_our_cls(self, instance, val):
        print "set_for_our_cls",(self, self.attr, instance, val)#####@@@@@
        attr = self.attr
        try:
            lval = instance.__dict__[attr]
        except KeyError:
            # (this happens at most once per attr per instance, iff the attr is set before it's ever been gotten-from, in this instance)
            lval = instance.__dict__[attr] = self.make_lval_for_instance(instance)
        # note: that lval's initval_expr is never evaluated, if it's not needed since we set it before getting from it;
        # (that's not just an optim -- it's legal for initval_expr to be an error to eval in cases where we won't eval it)
        # (note that just because set-before-get happened in this instance doesn't mean it happened overall --
        #  otoh we might discard older unused initval exprs
        #  [those points are related, but i am a bit too tired to explain (or see exactly) how])
        lval.set_constant_value(val)
            ###e probably set_constant_value should be renamed set_value, to fit with StateRefInterface [070312]
        return
##    def __repr__(self):
##        return "<%s at %#x for %r>" % (self.__class__.__name__, id(self), self.attr)#061117 changed self.lval_formula -> self.attr
    pass # end of class C_rule_for_lval_formula
    #
    # historical note [061117 841p]: see cvs rev 1.42 for a version of this class
    # which misguidely handled initval_expr itself, and a comment explaining why that was wrong.

def eval_and_discard_tracked_usage(formula, instance, index): #061117 #e refile into Exprs? #e see also other calls of call_but_discard_tracked_usage
    """
    Evaluate a formula (for an instance, at an index) which is allowed to be time-dependent,
    but for which we don't want to recompute anything when its value changes.

    This works by discarding tracked usage from the eval.

    Usage advice: If ordinary eval is called instead of this (for formulas whose value changes
    can occur but should not trigger recomputes of whatever our caller is computing),
    changes to this formula's value would incorrectly invalidate whatever our caller happens to be recomputing,
    which might be a bug, or more likely would just be a big performance hit
    (causing needless recomputes of arbitrarily lots of stuff).
    """
    #e could be more efficient, but doesn't matter too much -- so far only used when initializing Instance objects
    computer = formula._e_compute_method(instance, index)
    return call_but_discard_tracked_usage( computer)

class data_descriptor_Expr_descriptor(ClassAttrSpecific_DataDescriptor):
    """
    #doc
    @note: used only in class State(data_descriptor_Expr)
    """
    def _init1(self):
        (self.expr,) = self.args
        self.expr._e_set_descriptor(self) # whether it stores anything is up to the specific subclass
    def get_for_our_cls(self, instance):
        # print "get_for_our_cls",(self, self.attr, instance, )
        assert self.attr != FAKE_ATTR
        return self.expr._e_get_for_our_cls(self, instance) #e or pass self.attr rather than self?
    def set_for_our_cls(self, instance, val):
        # print "set_for_our_cls",(self, self.attr, instance, val)
        assert self.attr != FAKE_ATTR
        return self.expr._e_set_for_our_cls(self, instance, val) #e or pass self.attr rather than self?
##    def __repr__(self):
##        return "<%s at %#x for %r>" % (self.__class__.__name__, id(self), self.attr)
    def _StateRef__your_attr_in_obj_ref( self, instance): #bruce 070815
        return self.expr._e_StateRef__your_attr_in_obj_ref( self, instance)
    pass # end of class data_descriptor_Expr_descriptor

# ==

class CV_rule(ClassAttrSpecific_NonDataDescriptor):
    """
    One of these should be stored by ExprsMeta when it finds a _CV_attr compute method,
    formula (if supported #k), or constant (if supported #k).
    """
    prefixV = '_CV_'
    prefixK = '_CK_'
    def get_for_our_cls(self, instance):
        attr = self.attr
        # Make sure cls-specific info is present -- we might have some, in the form of _TYPE_ decls around compute rule?? not sure. ##e
        # In principle, we certainly have some in the form of the optional _CK_ compute method...
        # but our current code finds it easier to make this instance-specific and just grab a bound method for each instance.
        if 0:
            # if it's ever class-specific we might do something like this:
            try:
                compute_methodK = self.compute_methodK
            except AttributeError:
                compute_methodK = getattr(self.cls, self.prefixK + attr, None)
                #e process it if it's a formula or constant sequence
                self.compute_methodK = compute_methodK

        # Now find instance-specific info --
        # which is a RecomputableDict object for our attr in instance, and our bound V and K methods.
        # (Formulas or constants for them are not yet supported. ###e nim)
        try:
            rdobj = instance.__dict__[attr]
            print "warning: rdobj was not found directly, but it should have been, since this is a non-data descriptor", self #e more?
        except KeyError:
            # make a new object from the compute_methods (happens once per attr per instance)
            rdobj = instance.__dict__[attr] = self.make_rdobj_for_instance(instance)
        return rdobj # this object is exactly what instance.attr retrieves (directly, from now on, or warning above gets printed)

    def make_rdobj_for_instance(self, instance):
        #e refile into a subclass?? (so some other subclass can use formulas)
        #e actually, splitting rhs types into subclasses would not work,
        # since main subclass can change whether it assigns formula or function to _CV_attr!!!
        # ditto for C_rule -- say so there... wait, i might be wrong for C_rule and for _CV_ here,
        # since self is remade for each one, but not for _CK_ (since indeply overridden) if that
        # needn't match _CV_ in type. hmm. #####@@@@@
        attr = self.attr
        compute_methodV = getattr(instance, self.prefixV + attr) # should always work
##        compute_methodV = bound_compute_method_to_callable( compute_methodV,
##                                                              formula_symbols = (_self, _i), ###IMPLEM _i
##                                                              constants = True )
##            # also permit formulas in _self and _i, or constants (either will be converted to a callable)
        assert callable(compute_methodV)
        compute_methodK = getattr(instance, self.prefixK + attr, None)
            # optional method or [nim] formula or constant, or None (None can mean missing, since legal constant values are sequences)
        if compute_methodK is not None:
##            compute_methodK = bound_compute_method_to_callable( compute_methodK,
##                                                                formula_symbols = (_self,),
##                                                                constants = True )
            assert callable(compute_methodK)
        obj = RecomputableDict(compute_methodV, compute_methodK)
        return obj
    # Note: we have no __set__ method, so in theory (since Python will recognize us as a non-data descriptor),
    # once we've stored obj in instance.__dict__ above, it will be gotten directly
    # without going through __get__. We print a warning above if that fails.

    # Note: similar comments about memory leaks apply, as for C_rule.

    pass # end of class CV_rule

class CV_rule_for_val(CV_rule):pass ####k guess off top of head, much later than the code was written [061103]

def choose_CV_rule_for_val(clsname, attr, val):
    """
    return an appropriate CV_rule object, depending on val
    """
    if is_formula(val):
        assert 0, "formulas on _CV_attr are not yet supported"
        # when they are, we'll need _self and _i both passed to _e_compute_method
    else:
        # constants are not supported either, for now
        # so val is a python compute method (as a function)
        ###KLUGE: CV_rule gets val as a bound method, like C_rule does
        return CV_rule_for_val(clsname, attr)
    pass

# ==

# prefix_X_ routines process attr0, val on clsname, where attr was prefix _X_ plus attr0, and return val0
# where val0 can be directly assigned to attr0 in cls (not yet known); nothing else from defining cls should be assigned to it.

def prefix_C_(clsname, attr0, val, **kws): ###k **kws is suspicious but needed at the moment - kluge?? [061101]
    val0 = choose_C_rule_for_val(clsname, attr0, val, **kws)
    return val0

def prefix_CV_(clsname, attr0, val, **kws):
    val0 = choose_CV_rule_for_val(clsname, attr0, val) ###k even worse, needed in call but not ok here -- worse kluge?? [061101]
    return val0

def prefix_nothing(clsname, attr0, val, **kws):
    # assume we're only called for a formula -- but [as of 061117] it might be a formula for an lval, rather than for a val!
    ## assert is_formula(val)
    permit_override = kws.get('permit_override', False) # it's a kluge to know about this here
    if not permit_override and not needs_wrap_by_ExprsMeta(val):
        ## print "why is this val not special? (in clsname %r, attr0 %r) val = %r" % (clsname, attr0, val)
        printnim("not needs_wrap_by_ExprsMeta(val)")
        #kluge 061030: i changed this to a warning, then to printnim since common, due to its effect on ConstantExpr(10),
        # tho the proper fix is different -- entirely change how _DEFAULT_ works. (see notesfile).
        # But on 061101 we fixed _DEFAULT_ differently so this is still an issue -- it's legit to turn formulas
        # on _DEFAULT_attr into e.g. ConstantExpr(10) which doesn't contain _self.
        # Guess: in that case it implicitly DOES contain it! kluge for now: ignore test when permitting override. ###@@@
    val0 = choose_C_rule_for_val(clsname, attr0, val, **kws)
    return val0

def prefix_DEFAULT_(clsname, attr0, val, **kws):
    """
    #doc
    WARNING: caller has to also know something about _DEFAULT_, since it declares attr0 as an option
    """
    printfyi("_DEFAULT_ is deprecated and may soon be unsupported") #070121
    if 'kluge061103':
        assert val is canon_expr(val)
    else:
        val = canon_expr(val) # needed even for constant val, so instance rules will detect overrides in those instances
            ##e could optim somehow, for instances of exprs that didn't do an override for attr0
    assert is_formula(val) # make sure old code would now always do the following, as we do for now:
    ## did this 061101 -- printnim("here is one place we could put in code to disallow override except for _DEFAULT_")
    ## return prefix_nothing(clsname, attr0, val, permit_override = True, **kws) ###k GUESS this is bad syntax
    kws['permit_override'] = True
    return prefix_nothing(clsname, attr0, val, **kws)

# old code before 061029 837p:
##    if not hasattr(val, '_e_compute_method'): ###e improve condition
##        # if val is not a formula or any sort of expr, it can just be a constant. e.g. _DEFAULT_color = gray
##        # what if it's a method?? that issue is ignored for now. (bug symptom: bound method might show up as the value. not sure.)
##        # what if it's a "constant classname" for an expr? that's also ignored. that won't be in this condition...
##        # (the bug symptom for that would be a complaint that it's not special (since it doesn't have _self).)
##        # Q: if it's a formula or expr, not free in _self, should we just let that expr itself be the value??
##        # This might make sense... it ought to mean, the value doesn't depend on self (unless it's a bound method, also ok maybe).
##        #####@@@@@
##        return val
##    return prefix_nothing(clsname, attr0, val)

prefix_map = {'':prefix_nothing,
              '_C_':prefix_C_,
              '_DEFAULT_': prefix_DEFAULT_,
              '_CV_':prefix_CV_,
              }
    #e this could be more modular, less full of duplicated prefix constants and glue code

def attr_prefix(attr): # needn't be fast
    for prefix in prefix_map: #.keys()
        if prefix and attr.startswith(prefix):
            return prefix
    return ''

def needs_wrap_by_ExprsMeta(val, msg_info = ''): # renamed from val_is_special, and revised, 061203
    """
    #doc
    val needs_wrap_by_ExprsMeta if it's an Expr pyinstance (for now)
    [no longer has to contain _self as a free variable]
    """
    if not is_Expr_pyinstance(val):
        return False
##    if not val._e_free_in('_self'):###WRONG I think, re State... changed now
##        if msg_info:
##            msg_info = " (%r)" % (msg_info,)
##        print "weird val%s: an Expr that is not free in _self" % msg_info, val
##        return True ## was False until 061203 1009p
        # and what it printed for was:
        ##weird val (('open_icon', 'ToggleShow')): an Expr that is not free in _self <Overlay#3945(a)>
        ##weird val (('closed_icon', 'ToggleShow')): an Expr that is not free in _self <Overlay#3952(a)>
        ##weird val (('openclose', 'ToggleShow')): an Expr that is not free in _self <Highlightable#3959(a)>
        ##
        ##weird val (('var', 'toggler')): an Expr that is not free in _self <State#6617: (<constant_Expr#6615: <type 'int'>>, <constant_Expr#6616: 0>)>
        ##weird val (('_value', 'toggler')): an Expr that is not free in _self <Highlightable#6647(a)>
    if val._e_is_instance: #061203
        print "POSSIBLE BUG: val._e_is_instance true, for val being wrapped as Expr by ExprsMeta: %r" % (val,)#k ever happens??
    return True
##    return is_Expr_pyinstance(val) and val._e_free_in('_self')
        # 061201 Q: are there any implicit ways of containing _self? A: not presently. But note that in sequential class assignments
        # like x = Arg(), y = x + 1, y contains _self since Arg() does. We depend on that in the current code.
        # THIS WILL BE AN ISSUE FOR THINGS LIKE PROPERTY EXPRS, and I wonder if it even has caused some bugs I've seen and
        # wondered about? I vaguely recall one of those "should have been processed by ExprsMeta" prints which I didn't understand. ###k
        # The actual text is "this formula needed wrapping by ExprsMeta to become a compute rule" btw.
        #
        ## outtake: and val.has_args [now would be val._e_has_args]
        ## outtake: hasattr(val, '_e_compute_method') # this was also true for classes
    ##e 061101: we'll probably call val to ask it in a fancier way... not sure... Instance/Arg/Option might not need this
    # if they *turn into* a _self expr! See other comments with this date [i hope they have it anyway]


is_formula = is_Expr #####e review these -- a lot of them need more cases anyway

def is_attr_equals_self_attr_assignment(attr, val, classname = "?"): #070324 split out this predicate
    """
    is the assignment attr = val of the exact form attr = _self.attr
    (for the same attr, ie recursive)?
    """
    if isinstance(val, getattr_Expr) \
       and val._e_args[0] is _self \
       and isinstance( val._e_args[1], constant_Expr) \
       and val._e_args[1]._e_constant_value == attr:
        assert len(val._e_args) == 2, \
               "in class %s: dflt arg is not allowed in attr = getattr_Expr(_self, attr, dflt) (attr = %r)" % (classname, attr)
        return True
    return False

# ==

class ExprsMeta(type):
    # follows 'MyMeta' metaclass example from http://starship.python.net/crew/mwh/hacks/oop-after-python22-1.txt
    def __new__(cls, name, bases, ns):
        # Notes:
        # - this code runs once per class, so it needn't be fast.
        # - cls is NOT the class object being defined -- that doesn't exist yet, since it's our job to create it and return it!
        #   (It's the class ExprsMeta.)
        # - But we know which class is being defined, since we have its name in the argument <name>.
        data_for_attr = {}
        processed_vals = []
        orig_ns_keys = ns.keys() # only used in exception text, for debugging
        # handle _options [deprecated since 061101] by turning it into equivalent _DEFAULT_ decls
        _options = ns.pop('_options', None)
        if _options is not None:
            print "_options (defined in class %s) is deprecated, since a later formula rhs won't see attr in namespace" % name
            assert type(_options) is type({})
            for optname, optval in _options.items():
                # _DEFAULT_optname = optval
                attr = '_DEFAULT_' + optname
                assert not ns.has_key(attr), \
                       "error: can't define %r both as %r and inside _options in the same class %r (since ExprsMeta is its metaclass); ns contained %r" % \
                       ( optname, attr, name, orig_ns_keys )
                ns[attr] = optval
                # no need to check for ns[optname] here -- this will be caught below -- but the error message will be misleading
                # since it will pretend you defined it using _DEFAULT_; so we'll catch that case here, at least
                # (though this doesn't catch a conflict with some other way of defining optname; that'll still have misleading error
                #  msg below).
                assert not ns.has_key(optname), \
                       "error: can't define %r directly and inside _options in the same class %r (since ExprsMeta is its metaclass); ns contained %r" % \
                       ( optname, name, orig_ns_keys )
                del attr
                continue
            del optname, optval
        del _options

        # Remove "attr = _self.attr" entirely, before any other ns processing. [070324]
        # (This has to be done here, to permit _C_attr to coexist with that form.)
        # (I ran into this for a0 and _C_a0 in SimpleColumn, 070321, and in one or two other places since then.)
        for attr, val in ns.items():
            prefix = attr_prefix(attr)
            if not prefix:
                if is_attr_equals_self_attr_assignment(attr, val):
                    del ns[attr]
            continue

        # look for special vals, or vals assigned to special prefixes, in the new class object's original namespace
        # (since we will modify these in the namespace we'll actually use to create it)
        for attr, val in ns.iteritems():

            # [070210 removed "draw decorators" (autowrap of draw function by _e_decorate_draw),
            #  introduced 070104 but still nim, since it seems simpler and good enough
            #  just to filter all kid-draw-calls thru a new method IorE.drawkid(kid).
            #  (last here in cvs rev 1.66)]

            # The desired transform is something like
            # If attr has a special prefix, or val has a special value, run attr-prefix-specific code
            # for defining what value to actually store on attr-without-its-prefix. Error if we are told
            # to store more than one value on attr.

            #obs?:
            # which might create new items in this namespace (either replacing ns[attr],
            # or adding or wrapping ns[f(attr)] for f(attr) being attr without its prefix).
            # (If more than one object here wants to control the same descriptor,
            #  complain for now; later we might run them in a deterministic order somehow.)

            prefix = attr_prefix(attr)
            if prefix:
                attr0 = remove_prefix(attr, prefix)
                if ns.has_key(attr0):
                    # assert not is_attr_equals_self_attr_assignment(attr0, ns[attr0]) # since already removed earlier # remove when works
                    assert 0, \
                       "error: can't define both %r and %r in the same class %r (since ExprsMeta is its metaclass); ns contained %r" % \
                       ( attr0, attr, name, orig_ns_keys )
                    #e change that to a less harmless warning?
                    # note: it's not redundant with the similar assert below, except when *both* prefix and needs_wrap_by_ExprsMeta(val).
                    # note: ns contains just the symbols defined in class's scope in the source code, plus __doc__ and __module__.
            else:
                attr0 = attr
            if hasattr(val, '_ExprsMeta__set_attr'): # note 061203: maybe not needed after all, tho not harmful, might help catch errors
                ### PROBLEM: true for symbolic expr val.
                # POSSIBLE SOLUTION: exclude _[A-Z] attrnames, not _[a-z]. (Hmm: _S_ATTR_??)
                # DONE INSTEAD [061203]: exclude any attr which might be name-mangled (starts _ but not __, contains __).
                #k also check val is a pyinstance, not pyclass? no need for now.
                # 061201
                #e should we do this after prefix processing, instead? doesn't matter for now, not mixed with prefixes or needs_wrap_by_ExprsMeta.
                ##k but make sure these vals work with formula scanning for _self.attr replacement! #####IMPLEM
                val._ExprsMeta__set_attr(attr) #e could set clsname too, or pass it to this same method, if needed
            if prefix or needs_wrap_by_ExprsMeta(val, msg_info = (attr, name)):
                ok = True
                if not prefix and attr.startswith('_'):
                    # note: this scheme doesn't yet handle special vals on "helper prefixes" such as the following:
                    for helper_prefix in ('_CK_', '_TYPE_'):
                        ## assert not attr.startswith(helper_prefix), "special val not yet supported for %r: %r" % (attr, val)
                        if attr.startswith(helper_prefix):
                            print "WARNING: special val not yet supported for %r: %r" % (attr, val)
                                # this one we need to support:
                                #   _DEFAULT_height = _self.width [now it's in prefix_map]
                                # this one is a bug in my condition for detecting a formula:
                                #   _TYPE_thing = <class 'exprs.widget2d.Widget2D'>
                            ok = False
                            break
                        continue
##                if prefix == '_DEFAULT_':
##                    printnim("_DEFAULT_ needs to be handled differently before it will let named options override it")###@@@
##                    # _DEFAULT_ needs to declare attr0 as an option, ie let it be overridden by named options
##                    ### how we'll do this: leave it sitting there in the namespace, DON'T COPY IT TO ATTR (that's WRONG),
##                    # instead make the DEFAULT thing a rule of its own, but also do the decl
##                    # and also set up a rule on attr which grabs it from options and DEFAULT in the proper way.
                if ok:
                    lis = data_for_attr.setdefault(attr0, [])
                    lis.append((prefix, val))
                pass
            continue
        del attr, val
        # extract from each lis its sole (prefix, val), element (could be removed if we cleaned up code to not need lis at all),
        # and prepare those for sorting by expr_serno(val)
        # [needed so we process val1 before val2 if val1 is included in val2 -- assumed by FormulaScanner]
        newitems = []
        for attr0, lis in data_for_attr.iteritems():
            assert len(lis) == 1, "error: can't define %r and %r in the same class %r (when ExprsMeta is its metaclass); ns contained %r" % \
                       ( lis[0][0] + attr0,
                         lis[1][0] + attr0,
                         name, orig_ns_keys )
                #e change that to a less harmful warning?
            prefix, val = lis[0]
            if 'kluge061103':
                # we have to make sure canon_expr happens before sorting, not in the processor after the sort,
                # or the sort is in the wrong order:
                if prefix == '_DEFAULT_':
                    printnim("should de-kluge061103: val = canon_expr(val) for _DEFAULT_ before sorting")
                    val = canon_expr(val)
            newitems.append( (expr_serno(val), prefix, attr0, val) )
            del prefix, val, attr0, lis
        del data_for_attr
        # sort vals by their expr_serno [motivation [IIRC, 061201 ##k]: if expr1 contains expr2, make sure expr1 comes first]
        # (I don't think we have to give properties (like State_helper) a serno -- canon_expr will make an expr wrapper which gets one.
        #  What we might need to do is make them act symbolic re getattr... before they get processed at all.
        #  Hmm, how does that work for whatever Arg turns into?? 061201 Q
        #  A: it turns into an expr; then that gets turned into a descriptor by our prefix-map,
        #  but as an expr, it's easily extendible into other exprs, including by getattr, when used during the class def.
        #  Can a descriptor work like that? ONLY IF IT STARTS ALL ITS OWN ATTRNAMES BY _e_ or so!!!! Hmm, do I want that?
        #  It would end up simplifying things... maybe it would already be an expr with no wrapping, unlike a plain property....
        #  OTOH besides the work, it makes these objects bugprone to handle, since they don't complain about missing attrs.
        #  So what about the old way -- let them be exprs when created, maybe even symbolic ones (perhaps unlike Arg/Option),
        #  but not descriptors yet, and turn them into descriptors in this scanner.
        #  But maybe in a simpler way than we do now? Or maybe have a kind of expr that is easy to make into a descriptor --
        #  maybe it's enough to set a flag in it to tell it "don't be symbolic anymore". Is doing that dynamically ok,
        #  which means, once the class it's in is defined, are you done with that way of using it? Guess: yes. If so,
        #  this would increase safety. But it still means writing the descriptor-content-methods with all-_e_ attrs,
        #  even if the descriptors themselves are separate objects. Or just using current system, with DescriptorForState, like C_rule.
        ####)
        newitems.sort()
        ## print "newitems for class %s:" % name, newitems # this can print a lot, since single Expr vals can have long reprs
##        if 'debugging' 'kluge061103':
##            print "newitems for class %s:" % name
##            for junk, prefix, attr0, val in newitems:
##                print prefix, attr0, expr_serno(val), val.__class__
        # process the vals assigned to certain attrs, and assign them to the correct attrs even if they were prefixed
        scanner = FormulaScanner( debug_name = name) #070321 added debug_name
            # this processes formulas by fixing them up where their source refers directly to an attr
            # defined by another (earlier) formula in the same class, or (#nim, maybe) in a superclass (by supername.attr).
            # It replaces a direct ref to attr (which it sees as a ref to its assigned formula value, in unprocessed form,
            # since python eval turns it into that before we see it) with the formula _self.attr (which can also be used directly).
            # Maybe it will replace supername.attr as described in a comment inside FormulaScanner. #e
        for junk, prefix, attr0, val in newitems:
            del junk
            # prefix might be anything in prefix_map (including ''), and should control how val gets processed for assignment to attr0.
            processor = prefix_map[prefix]
            val0 = processor(name, attr0, val, formula_scanner = scanner)
                # note, this creates a C_rule (or the like) for each formula
            ns[attr0] = val0
            # new feature 070316: if this assignment looks exactly like attr = _self.attr (before processor runs),
            # then don't store it in ns. This permits "inheritance of formulae from superclass"
            # but with the use of attr (not _self.attr) in subsequent formulae. Seems to work (testexpr_36).
            # update 070321: see another comment of this date, about a conflict we should make legal between this and def _C_attr.
            # update 070324: this needs to be done earlier, and now it is. Just assert that worked. ##e refile these comments?
            # assert not is_attr_equals_self_attr_assignment(attr0, val) # remove when works
                # old code said, when that assert cond failed:
                ## assert val0 == val # should be ok, but there is not yet an __eq__ method on OpExpr!!!
                ## print "skipping ns[attr0] = val for attr0 = %r, val = %r" % (attr0, val) # works
                ## del ns[attr0]
            processed_vals.append(val0) # (for use with __set_cls below)
            del prefix, attr0, val
        del newitems
        # create the new class object
        res = super(ExprsMeta, cls).__new__(cls, name, bases, ns)
        assert res.__name__ == name #k
        # tell the processed vals what class object they're in
        for thing in processed_vals:
            try:
                if hasattr(thing, '_ExprsMeta__set_cls'):
                    # (note: that's a tolerable test, since name is owned by this class, but not sure if this scheme is best --
                    #  could we test for it at the time of processing, and only append to processed_vals then??
                    #  OTOH, what better way to indicate the desire for this info at this time, than to have this method? #k)
                    thing._ExprsMeta__set_cls(res)
                        # style point: __set_cls is name-mangled manually, since the method defs are all outside this class
            except:
                print "data for following exception: res,thing =",res,thing
                    # fixed by testing for __set_cls presence:
                    ## res,thing = <class 'exprs.Rect.Rect'> (0.5, 0.5, 0.5)
                    ## AttributeError: 'tuple' object has no attribute 'set_cls' [when it had a different name, non-private]
                raise
        return res # from __new__ in ExprsMeta
    pass # end of class ExprsMeta

class FormulaScanner: #061101  ##e should it also add the attr to the arglist of Arg and Option if it finds them? [061101]
    def __init__(self, debug_name = ""):
        self.debug_name = debug_name
        self.replacements = {}
        self.seen_order = -1 # this class knows about retvals of expr_serno (possible ones, possible non-unique ones)
        self.linecounter = 0 # this must be unique for each separate formula we scan, and be defined while we scan it
        self.argposns = {} # attr -> arg position ##e fix for superclass args
        self.next_argpos = 0 # next arg position to allocate ##e fix for superclass args
        self.saw_arglist = False # whether an ArgList was declared (if so, it used up all remaining arg positions) [070321 new feature]
        self.saw_non_required_arg = False # whether an Arg decl for a non-required Arg was seen [070321 new feature]
            # WARNING: saw_arglist and saw_non_required_arg are used only for error messages, and thus are affected by kluges
            # which reset them to False after one error message is emitted, to prevent them from issuing redundant ones.
            # Therefore they are NOT permanent records of those errors. If that is needed, replace the kluges with two different
            # attrs for each, one for whether the condition was seen and one for whether it led to an error message being printed.
    def __repr__(self): #070321
        debug_name = self.debug_name
        return "<%s at %#x%s>" % (self.__class__.__name__, id(self), debug_name and (" (%s)" % debug_name) or "")
    def scan(self, formula, attr):
        """
        Scan the given formula (which might be or contain a C_rule object from a superclass) .... #doc
        Return a modified copy in which replacements were done, .... #doc
        """
        self.linecounter += 1
        printnim("several serious issues remain about C_rules from superclasses in ExprsMeta; see code comment") ####@@@@
            # namely: if a C_rule (the value of a superclass attrname) is seen in place of a formula in ExprsMeta:
            # - will it notice it as needs_wrap_by_ExprsMeta?
            # - will it do the right thing when using it (same as it does when making one for a subclass)?
            # - does C_rule need OpExpr methods for letting source code say e.g. thing.width on it?
            # - if so, does it need renaming of its own methods and attrs (especially args/kws) to start with _e_?
            # Idea to help with these: like a function making an unbound method, C_rule can modify its retval when
            # accessed from its class, not only when accessed from its instance. Can it actually return a "formula in _self"
            # for accessing its attr? This would do our replacement for us in the present context, but I'm not sure its good
            # if some *other* code accesses an attr in the class. OTOH, I can't think of any other code needing to do that,
            # unless it thinks it'll get an unbound method that way -- but for instance var attrs, it won't think that --
            # if anything it'll think it should get a "default value". (Or perhaps it might want the formula passed into the C_rule.)
            # Note, the C_rule remains available in the class's __dict__ if needed.
            #   Related Qs: what if a class formula accidentally passes a superclass attrname directly to a Python function?
            # If it does this for one in the same class, it passes the formula or expr assigned to that one in the source code,
            # before processing by FormulaScanner. This will generally fail... and needn't be specifically supported, I think.
            #   A test shows that I was wrong: you can't access superclass namespace directly, in the first place!
            # You have to say superclassname.attr (like for using unbound methods in Python, even as rhs of an assignment
            # directly in subclass, not in a def in there, I now realize). If someone said this in our system, they would NOT
            # want _self.attr, if they had redefined (or were going to redefine) attr! They'd want either the formula assigned
            # to attr in the superclass, or something like _self._superclassname__attr with that formula assigned forever to that attr
            # (in the superclass). BTW, they'd probably want the processed formula, that is, if the formula they got had source
            # saying "attr2" (which had evalled to some unprocessed formula assigned to attr2) they'd want that to become _self.attr2.
            # Does access from a class happen when a subclass internally caches things? Does subclass __dict__ have everything?
            # Should find out... for now, just print_compact_stack whenever access from class happens, in a def __get__ far above.
            #    Guess: best soln is for class access to return either _self.attr or (much better, semantically) the processed formula;
            # I think that solves all issues listed above, except that it would be supoptimal (maybe very) if the same super formula
            # was used multiple times (since no sharing of cached recompute results). If that matters, return _self._class__attr
            # and plop that formula on _class__attr in that class. BUT I haven't designed how Arg or Option work
            # or thought this through at all re them; maybe this scanner handles them too... s##e
            # [061101]
        #e if not a formula or C_rule, asfail or do nothing
        error_if_Arg_or_Option = False
        if 1:
            new_order = expr_serno(formula)
            assert new_order >= self.seen_order, 'you have to sort vals before calling me, but I got order %r, then %r in %r' % \
                   (self.seen_order, new_order, formula) #### this is failing, so print the exprs it gets:
##            print "fyi here is a formula for worrying about that sort order bug: %r" % formula
##                # the bug is that we sort it as 10, but see it here as constant_Expr(10) -- but who does that?
##                # Turns out it was done in prefix_DEFAULT_, so in 'kluge061103' we predo that before sorting.
            if new_order == self.seen_order > 0:
                error_if_Arg_or_Option = True #doc ###IMPLEM its effect; is it really just an error about _E_ATTR?? not sure.
            self.seen_order = new_order
            pass
        self.replacements[_E_ATTR] = constant_Expr(attr) # this allows formulas created by Option to find out the attr they're on
        printnim("we need some scheme to detect two attrs with the same val, if that val contains an Arg or Option subexpr")
            # once vals are sorted, these are easy to see (they're successive)... we exploit that above, to set error_if_Arg_or_Option
        if error_if_Arg_or_Option:
            del self.replacements[_E_ATTR] ###KLUGE -- at least this ought to cause an error, eventually & hard to understand
                # but under the right conditions... #e instead we need to put in a "replacement it's an error to use".
                ###WRONG since Arg doesn't put in the symbol _E_ATTR, I think... what's ambiguous for it is, ref same arg, or another Arg?
                ##e to fix, use a scheme we need anyway -- a thing in the expr which runs code when we scan it, to get its replace-val.
                # (Can that be an effect of doing constant-folding if replace-vals are constants, incl funcs being called on args??)
            printnim("should test that above kluge (del at _E_ATTR) detects thing = thing2 = Option(...) even if not Arg()")##e

            # current status by test 061103 8pm - for bright = width, and bheight = top, that warning gets printed,
            # but nothing else seems to detect the error (if it is an error, I forget, but I think it is). #####@@@@@

        res = self.replacement_subexpr(formula)
        # register formula to be replaced if found later in the same class definition [#e only if it's the right type??]
        if formula in self.replacements:
            print "warning: formula %r already in replacements -- error?? its rhs is %r; new rhs would be for attr %r" % \
                  (formula, self.replacements[formula], attr)
            # maybe not error (tho if smth uses it after this, that might deserve a warning) --
            # in any case, don't replace it with a new replacement
        else:
            self.replacements[formula] = getattr(_self, attr) # this creates a getattr_Expr [#e clearer to just use that directly?]
                # don't do this before calling self.replacement_subexpr above, or it'll find this replacement immediately!
        return res
    def replacement_subexpr(self, subexpr): ###e arg to preclude replacing entire thing, to help detect a1=a2=Arg() error
        """
        Map a subexpr found in a formula (perhaps a C_rule from a superclass, if that can happen and is supported)
        into its replacement, which is usually the same subexpr.
        """
        assert not isinstance(subexpr, ClassAttrSpecific_NonDataDescriptor), "formula containing super C_rule is nim" #e more info
        if subexpr in self.replacements: # looked up by id(), I hope ###k
            res = self.replacements[subexpr]
##            print "replacing %r by %r" % (subexpr,res)
            return res
        elif hasattr(subexpr, '_e_override_replace') and is_Expr_pyinstance(subexpr):
            # It wants to do it itself, perhaps using private knowledge about the methods & internal attrs in this scanner.
            # (This is used by special subexprs which call self.argpos in order to allocate argument positions.)
            return subexpr._e_override_replace( self )
        ###e can we find an Instance here?? assume no, for now.
        assert not expr_is_Instance(subexpr)
        printnim("I bet InstanceOrExpr is going to need arb getattr when Expr, and _e_ before all methodnames.... see code cmt")
            #### PROBLEM re that printnim:
            # attr1 = Rect(...); attr2 = attr1.width -- this does a getattr that will fail in current code --
            # or might return something like a bound method (or C_rule or whatever it returns).
            # [###e C_rule better detect this error, when _e_is_instance false in it -- i bet it does...
            #  yes, it does it inside _e_compute_method.]
            # BUT it might be illegal anyway, if we needed to say instead attr1 = Instance(Rect(...)) for that to work,
            # with Instance (or Arg or Option) effectively returning something like a Symbol
            # (representing a _self-specific instance, like _self does) -- in fact [061101],
            # Instance(expr) might immediately return something like
            # _self._i_instance( expr, relindex-incl-attr-and-formula-subexpr-index )
            # or maybe that relindex can itself just be a symbol, so it can be put in easily and replaced later in a simple way.

        # otherwise assume it's a formula
        ###e special case for a formula headed by Arg or Option etc? just ask the expr if it wants to know attr,
        # ie if it's a macro which wants that, and if so, copy it with a new keyword or so, before replacing it as below.
        printnim("need special replacement for Arg etc which needs to know attr and formula-subexpr-index?")
        # do replacements in the parts
        if is_Expr_pyclass(subexpr):
            # it's a python class -- has no replaceable parts
            return subexpr
        return subexpr._e_replace_using_subexpr_filter( self.replacement_subexpr ) ###IMPLEM in Expr #k does API survive lexscoping??
    def argpos(self, attr, required, arglist = False):
        """
        An Arg or ArgOrOption macro has just been seen for attr, in the source line identified by self.linecounter.
        (It is a required arg iff required is true. It is an ArgList iff arglist is true [new feature 070321].)
        (In the future, if a superclass defines args, this might be one of those or a new one.)
        What argument position (numbered 0, 1, 2, etc) does this arg correspond to? Return the answer, and record it.

        NIM: ASSUME NO ARGUMENTS COME FROM THE SUPERCLASSES. To fix that, we'll need to find out what they were,
        then see if these are in that list (if so return old number), or not (and start new numbers after end of that list).
        Behavior when superclass has optional args and this class then defines required ones is not decided (might be an error).

        NIM: any decl to override this, like _args.
        """
        try:
            res = self.argposns[attr]
            ## print "fyi: scanner argpos returned an already-known pos %d for %r; other data:" % (res, attr), self, self.argposns
            # Note: this shows that finding the attr already recorded here is very common -- I guess since the thing that
            # gets replaced with the argpos occurs twice in every expanded Arg macro, or in lots of them anyway.
            # (It might also happen in a more unavoidable way, if we implemented inheritance of argpos from superclass someday,
            #  tho the need for the recent kluge to permit attr = _self.attr (elsewhere in this file) suggests that might
            #  not be possible after all -- allocated argpos could be inherited, but probably not the initial defns desired
            #  in the class namespace, unless we added some sort of kluge to bring them in, which seems like a bad idea.) [070321]
            return res
        except KeyError:
            # new argument -- allocate an arglist position for it
            if self.saw_arglist:
                print "error (ignoring it): another arg is declared after an arglist was seen",\
                      self,attr,required,arglist,self.argposns ###e improve message
                self.saw_arglist = False # kluge: don't keep complaining about this for more args after the same ArgList
            if arglist:
                self.saw_arglist = True
                    ##e also record this for this arg?
                    # no need for now, but in future, recording all arg/opt decls in one list (of all kinds)
                    # for processing once by the class (or customized expr) will permit better error checking of passed args/opts.
                    # [070321 comment]
            pos = self.next_argpos
            self.next_argpos += 1
            self.argposns[attr] = pos
            ###e also record whether it's required, and assert that once they stop being required, new ones are also not required
            if self.saw_non_required_arg and required:
                print "warning: required arg decl for %r comes after non-required arg decl -- it won't do what you want" % attr, self ###e improve msg
                self.saw_non_required_arg = False # kluge: don't keep complaining about this for the same non-required arg
            if not required:
                self.saw_non_required_arg = True
            # (do we also need to record their names? well, we're doing that. Do we need to record whether their names are public? #e)
            return pos
    pass # end of class FormulaScanner

# ==

# helpers for CV_rule
# (generally useful, but placed here since this module is very fundamental so should be mostly self-contained;
#  we might relax this later #e, but files helping implement this need to say so, like lvals.py does,
#  since most files in this module assume they can depend on this one.)

class ConstantComputeMethodMixin:
    # use this when defining things used inside ExprsMeta [is this necessary?? maybe it's lazy enough to not need it? I doubt it. #k]
    # only ok when they don't need any recomputes after the first compute.
    # (maybe just use python properties instead? #e)
    def __getattr__(self, attr): # in class ConstantComputeMethodMixin
        # return quickly for attrs that can't have compute rules
        if attr.startswith('__') or attr.startswith('_C'):
            raise AttributeError, attr # must be fast for __repr__, __eq__, __add__, etc
        try:
            cmethod = getattr(self, '_C_' + attr)
        except AttributeError:
            raise AttributeError, attr
        try:
            val = cmethod()
        except:
            print_compact_traceback("bla: ") ###e
            val = None
        setattr(self, attr, val)
        return val
    pass

class DictFromKeysAndFunction(ConstantComputeMethodMixin):
    """
    Act like a read-only dict with a fixed set of keys (computed from a supplied function when first needed;
    if that func is not supplied, all keys are permitted and iteration over this dict is not supported),
    and with all values computed by another supplied function (not necessarily constant, thus not cached).
    """
    def __init__(self, compute_value_at_key, compute_key_sequence = None, validate_keys = False):
        self.compute_value_at_key = compute_value_at_key
        self.compute_key_sequence = compute_key_sequence # warning: might be None
        self.validate_keys = validate_keys
    def _C_key_sequence(self):
        # called at most once, when self.key_sequence is first accessed
        assert self.compute_key_sequence, "iteration not supported in %r, since compute_key_sequence was not supplied" % self
        return self.compute_key_sequence()
    def _C_key_set(self):
        return dict([(key,key) for key in self.key_sequence])
    def __getitem__(self, key):
        if self.validate_keys: #e [if this is usually False, it'd be possible to optim by skipping this check somehow]
            if not key in self.key_set:
                raise KeyError, key
        return self.compute_value_at_key(key) # not cached in self
    # dict methods, only supported when compute_key_sequence was supplied
    def keys(self):
        """
        @note: unlike for an ordinary dict, this is ordered, if compute_key_sequence retval is ordered
        """
        return self.key_sequence
    iterkeys = keys
    def values(self):
        """
        @note: unlike for an ordinary dict, this is ordered, if compute_key_sequence retval is ordered
        """
        compval = self.compute_value_at_key
        return map( compval, self.key_sequence )
    itervalues = values
    def items(self):
        """
        @note: unlike for an ordinary dict, this is ordered, if compute_key_sequence retval is ordered
        """
        compval = self.compute_value_at_key
        return [(key, compval(key)) for key in self.key_sequence]
    iteritems = items
    pass # end of class DictFromKeysAndFunction

class RecomputableDict(Delegator):
    """
    Act like a read-only dict with variable (invalidatable/recomputable) values,
    and a fixed key sequence used only to support iteration
    (with iteration not supported if the key sequence compute function is not supplied).

    If validate_keys is True, every __getitem__ verifies the supplied key is in the specified key sequence.

    #e Someday, self.lvaldict might be a public attr -- not sure if this is needed;
    main use is "iterate over values defined so far".

    [This class is used by ExprsMeta to help implement _CV_ dict-item compute methods.]
    """
    def __init__(self, compute_methodV, compute_methodK = None, validate_keys = False):
        self.lvaldict = LvalDict2(compute_methodV)
        Delegator.__init__( self,
                            DictFromKeysAndFunction(
                                self.compute_value_at_key,
                                compute_methodK,
                                validate_keys = validate_keys ) )
        return
    def compute_value_at_key(self, key): #e should rename to be private?
        return self.lvaldict[key].get_value()
    def inval_at_key(self, key):#070207
        """
        [public method, on a dictlike object whose other client code might treat it much like an ordinary dict]

        Invalidate our lval at the given key. This has two effects:
        - force it to be recomputed when next asked for;
        - propogate this inval to anything which tracked a use of the value.
        Note that __delitem__, if we implemented it, would only do the first of these effects.
        That would probably be a bug, so for now, we're not implementing it (exception if you try to del an item).
        """
        self.lvaldict[key].inval()
    pass

###e tests needed:
# - make sure customization of attr formulas doesn't work unless they were defined using _DEFAULT_

# end
