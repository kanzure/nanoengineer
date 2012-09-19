# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
StatePlace.py - help InstanceOrExpr or its subclasses define and store state, in layers [#redoc that]

$Id$


note: this used to be part of staterefs.py; split it out on 061203
"""

from exprs.__Symbols__ import _self
from exprs.Exprs import call_Expr
from exprs.py_utils import attrholder

from exprs.lvals import LvalDict2, LvalForState, LvalError_ValueIsUnset

from utilities import debug_flags

# ==

def StatePlace(kind, ipath_expr = _self.ipath, tracked = True): # revised 061117
    # experimental, but used and working in Highlightable [that use moved to InstanceOrExpr 061126]; related to Arg/Option/Instance
    """In a class definition for an InstanceOrExpr subclass, use the assignment

        <kind>_state = StatePlace(<kind>, <ipath_expr>)

    (for a short string <kind>, usually one of a small set of conventional kinds of storage)
    to cause self.<kind>_state in each Instance to refer to external state specific to
    <ipath_expr> as evaluated in that Instance (by default, _self.ipath, meaning specific
    to that Instance, though usually more persistent than it, perhaps depending on <kind>).

    By default, that state is fully usage-tracked and change-tracked; it should only be
    changed when processing a mouse click or keystroke or similar user action, and changing it
    will invalidate any model variables or drawing side effects that used the prior value of
    the same state. (Changing it *during* model computations or drawing code can cause undetected
    errors and/or detected bad bugs.)

    If tracked = False, then that state is not usage-tracked or change-tracked at all. This is
    appropriate for certain "kinds" of state, e.g. temporary per-frame variables used for drawing code.
    (Some such state could probably just be stored in each Instance, but this is not yet clear. #k)

    It's usually necessary to initialize the contents of the declared stateplaces
    using set_default_attrs in _init_instance, or the like. (Note that the stateplace is often
    found rather than created, and the same sometimes goes for individual attrs within it.
    Both this StatePlace  declaration and set_default_attrs take this into account by only initializing
    what's not already there.)

    See also the [nim] State declaration for use with individual attrs.
    """
    # Implem notes:
    #
    # StatePlace() works by turning into a formula which will eval to a permanent reference
    # to a (found or created) attrholder for storing state of the given kind, at the given ipath
    # (value of ipath_expr), relative to the env of the Instance this is used in (i.e. to _self.env).
    # [revision 061117: the persistent state itself needs usage and change tracking. The attrholder
    # could be permanent and own that state (and do that tracking), or be a transient accessor to it [did it that way].]
    #
    # WARNING/BTW: when I reload, the data should be persistent, but the subscriptions to it probably shouldn't be.
    # But that's really up to each subs -- clearing all of them would be wrong. So ignore it for now.
    # (It means old objects will get invalidated, but that loses them their subs, and nothing recomputes their attrs
    # and resubs them, so it actually doesn't end up causing a lasting performance problem, I think. Review sometime. #k)

    assert isinstance(tracked, bool) or tracked in (0,1)
    assert isinstance(kind, str)
    res_expr = call_Expr( _StatePlace_helper, _self, kind, ipath_expr, tracked )
    return res_expr # from StatePlace


def _StatePlace_helper( self, kind, ipath, tracked): # could become a method in InstanceOrExpr, if we revise StatePlace macro accordingly
    """Create or find, and return, a permanent attrholder for access to all attrs with the given ipath,
    which are usage-and-change-tracked iff tracked is true.
    """
    # [revision 061117: the persistent state itself needs usage and change tracking. The attrholder
    # can be permanent and own that state (and do that tracking), or be a transient accessor to it [done here].
    # [061121 added back the tracked=False possibility.]
    #
    # implem scratch 061117:
    # what needs permanence is the lvals themselves. They will someday be in arrays (one attr, many objects),
    # but the attrholders are one object, many attrs, so let's keep the lvals outside the attrholders,
    # so they are not holders but just accessors. Let's simplify for now, by not keeping persistent attrholders at all,
    # making them nothing but access-translators (knowing kind & ipath to combine with each attr)
    # into one big persistent LvalDict. Or maybe one per kind, if we feel like it, and to get practice
    # with letting the LvalDict to use vary. Hmm, might as well make it one per kind/attr pair, then --
    # but that means all the work is in the attraccessors (since we don't even know the key to identify
    # the LvalDict until we know the attr) -- ok.

    if not tracked:
        # [devel note: this is just the old code for _StatePlace_helper from before it supported "tracked".]
        state = self.env.staterefs
        key = (kind,0,ipath) #e someday, kind should change which state subobj we access, not just be in the key
            # Note: this needs to be not interfere with _attr_accessor, whose key is (kind,attr) -- thus the extra 0
        res = state.setdefault(key, None)
            # I wanted to use {} as default and wrap it with attr interface before returning, e.g. return AttrDict(res),
            # but I can't find code for AttrDict right now, and I worry its __setattr__ is inefficient, so this is easier:
        if res is None:
            res = attrholder()
            state[key] = res
        return res

    res = _attr_accessor( self.env.staterefs, kind, ipath, debug_name = debug_flags.atom_debug and ("%r|%s" % (self,kind)))
        # we leave ipath out of the debug_name, since the accessor's LvalDict2 will add it in in the form of its key
    return res # from _StatePlace_helper


class _attr_accessor:
    """[private helper for _StatePlace_helper]"""
    ##e optim: someday we should rewrite in C both this class,
    # and its storage & usage-tracking classes (LvalDict2, Lval, etc),
    # for speed & RAM usage]
    ##e NIM: doesn't yet let something sign up to recompute one attr's values; only lets them be individually set.
    # This might be a problem. BTW to do that well it might need to also be told a model-class-name;
    # we can probably let that be part of "kind" (or a new sibling to it) when the time comes to put it in.
    def __init__( self, staterefs, kind, ipath, debug_name = None):
        self.__dict__['__staterefs'] = staterefs
        self.__dict__['__kind'] = kind
        self.__dict__['__ipath'] = ipath
        self.__dict__['__debug_name'] = debug_name
        ## self.__dict__['__tables'] = {}
    def __get_table(self, attr):
        kind = self.__dict__['__kind']
        whichtable = (kind,attr) # WARNING: this key is assumed in _StatePlace_helper, since it needs to not interfere with it
        ## tables = self.__dict__['__tables'] # WRONG, store them in staterefs
        staterefs = self.__dict__['__staterefs']
        tables = staterefs
        try:
            res = tables[whichtable]
        except KeyError:
            # (valfunc computes values from keys; it's used to make the lval formulas; but they have to be resettable)
            valfunc = self.valfunc ###e should use an initval_expr to make this
            debug_name = self.__dict__['__debug_name']
            if debug_name:
                debug_name = "%s.%s" % (debug_name, attr)
            tables[whichtable] = res = LvalDict2(valfunc, LvalForState, debug_name = debug_name)
                # note: we pass our own lvalclass, which permits set_constant_value
        return res
    def valfunc(self, key):
        # note: as of 061215 this is never overridden, so the usage-tracking LvalDict2's lvals do for it never tracks usage,
        # but we still need to use Lvals there so we can reset their value. In theory we could use a special kind
        # which didn't have recomputation-usage-tracking code at all. [i guess, as of 061215]
        raise LvalError_ValueIsUnset, "access to key %r in some lvaldict in %r, before that value was set" % (key,self)
            #k [061117 late] use this exception in hopes that it makes hasattr just say an attr is not yet there
            ##e needs more info, so probably make a lambda above to use as valfunc
            # [Update 070109: a certain order of file mods (triggering reload_once, each followed by remaking main instance)
            # can cause a bug of unknown cause which leads to this error. I found it only once, but repeatably,
            # using the demo_drag example and doing this order of touches: test.py lvals.py demo_drag.py test.py.
            # The messages mentioned Highlightable#0 -- not sure if that was an inner or outer expr.
            # Since it only happens in certain reloads, it may not be a "real bug".]
        pass
    def __repr__(self):#070109
        return "<%s(%s,%s) at %#x>" % (self.__class__.__name__, self.__dict__['__kind'], self.__dict__['__debug_name'] or '', id(self))
    def __get_lval(self, attr):
        # WARNING: in spite of the very private name, this is accessed externally due to a kluge. [070815]
        table = self.__get_table(attr) # an LvalDict2 object
        ipath = self.__dict__['__ipath']
        dictkey = ipath
        lval = table[dictkey] # lval might be created at this time (only in one of our two calls)
            ##k let's hope this doesn't internally ask for its value -- error if it does
        return lval
    def __getattr__(self, attr): # in class _attr_accessor
        return self.__get_lval(attr).get_value()
            # error if the value was not yet set; maybe we need an initval_expr like the State macro is about to be given ###e
    def __setattr__(self, attr, val):
        "WARNING: this runs on ALL attribute sets -- do real ones using self.__dict__"
        self.__get_lval(attr).set_constant_value(val)
            ###e probably set_constant_value should be renamed set_value, to fit with StateRefInterface [070312]
            # note: this optims by noticing if the value differs from last time; that ought to be a per-attr decl #e
        return
    def __setattr_default__(self, attr, default): # note: this method name is not special to Python
        """If attr is not set, set it to default, without doing any usage or change tracking.
        [Note: This method name and its meaning is a custom extension to Python's general attribute interface
         consisting of the  __getattr__/__setattr__ (and maybe __delattr__?) special methods.
         This method name is not special to Python itself.]
        """
        self.__get_lval(attr)._set_defaultValue( default)
    pass # end of class _attr_accessor

# ==

def set_default_attrs(obj, **kws): #e if this was general, we could refile into py_utils, but it turns out it's not general enough
    """For each attr=val pair in **kws, if attr is not set in obj, set it, without doing usage or change tracking.
    If obj supports __setattr_default__ (not a special name to Python itself), use that, otherwise use hasattr and setattr
    (with a temporary dynamic suppression of usage or change tracking, if possible -- nim for now except as an assertion).
       Note: this is not very efficient (or self-contained) for general use, for which pure hasattr/setattr would be sufficient.
    """
    # Note about why we disable tracking: hasattr itself does legitimately track use of the attr,
    # since testing thereness does use its "value" in a general sense (as if value was _UNSET_ when not there).
    # But, in this specific code, we don't want client (caller) to see us using attr,
    # since from client POV, all we're doing is changing _UNSET_ to v, which are equivalent values
    # (as client is declaring by calling us).
    # So we need to discard tracked usage of attr here.
    # We also need to discard any change from the set to default value,
    # except that we can probably ignore that issue for now (due to an accident of how current code uses this),
    # since if the attr is unset, it was never yet used, so invalidating it should have no effect.
    if 1:
        from exprs.Exprs import is_pure_expr
        if is_pure_expr(obj):
            assert 0, "set_default_attrs called on pure_expr %r is almost surely a bug; normally do it in _init_instance" % (obj,)
    import foundation.changes as changes
    try:
        method = obj.__setattr_default__
    except AttributeError:
        ## print "fyi: set_default_attrs using general case for",obj,kws.keys() # this happens for all non-tracked StatePlaces
        # general case - let's hope the object doesn't have tracked attrs; the temporary assertion here might not catch this
        ###e instead, we should actively suppress usage/change tracking, so we can permit it in obj
        # (tho careless uses of that would lead to bugs)
        mc = changes.begin_disallowing_usage_tracking('set_default_attrs (hasattr/setattr) for %r' % obj)
            # note: the argument is just an explanation for use in error messages ##e OPTIM: don't precompute that arg
        try:
            for k, v in kws.iteritems():
                if not hasattr(obj, k):
                    setattr(obj, k, v)
        finally:
            changes.end_disallowing_usage_tracking(mc)
    else:
        # use the special method
        mc = changes.begin_disallowing_usage_tracking('set_default_attrs (__setattr_default__) for %r' % obj)
            #e optim: remove this check; it only catches usage tracking, not change tracking (ie inval of something by this), anyway
        try:
            for k, v in kws.iteritems():
                method(k, v) # does its own usage/change-tracking suppression (we assume); this is partially checked (for now)
        finally:
            changes.end_disallowing_usage_tracking(mc)
    return # from set_default_attrs

    #e useful improvements to set_default_attrs (as used in InstanceOrExpr class defs) might be: [061116]
    # - shorter name
    # - able to create new objs of a desired type
    #   (perhaps by using a kw prefix: _type_attr = type, or _init_attr = (type, dfltval aka initarg))
    # - or to check the type if the obj is found (same args and call, but ask the type if it agrees that obj is one of its type)
    # - if obj is wrong type, we might even coerce it, eg add glue code to improve the api, make it relative to our own coords, etc,
    #   if we can do this in our local proxy for the state rather than in the external state. BUT, if we're creating the object too,
    #   we'd better make it clear what type to create it as externally (for others to also see)
    #   vs what type to coerce/glue that too locally (for private use). So we really have to say both the external & local types,
    #   or the external type & local mapping from that, or something like that.
    #   In fact -- maybe even give the two versions different names; which probably implies,
    #   set up a dependency between different external data.
    # - be able to initialize subattrs, like self.state.x.y -- do by creating x of desired type, then doing x.y inside x --
    #   but Q, do you do this if x.y is not there in x, but x is already there, or only if even x is not already there?
    #   usually the first, meaning, use two separate calls of this, but can one notation do it all? (and do we need that?)
    # - we might want a toplevel (expr syntax) version of all this, for use in pure-expr-notation programs; related to LocalState
    #   (see notesfile), esp if that really sets up a local *ref* to perhaps-external state.
    # In the future, it might work differently -- maybe we won't want attrs with default values to use up space,
    # when possible (not possible for the ones stored in allocated slots in arrays), so this will be replaced with
    # some sort of per-class per-kind attr decl, which includes the type & default value. (For that, see the [nim] State decl.)

# end
