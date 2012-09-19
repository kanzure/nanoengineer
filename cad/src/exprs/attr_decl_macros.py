# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
attr_decl_macros.py -- Instance, Arg, Option, ArgOrOption, State

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

[was in Exprs.py when developed, before State;
 split into this file 061203 to ease recursive import issues with State]
"""

# Symbols for private or semi-private use
# (note, other modules that need these also import them directly from __Symbols__)
from exprs.__Symbols__ import _E_ATTR, _E_REQUIRED_ARG_, _E_DFLT_FROM_TYPE_, _self

from exprs.py_utils import printnim
from exprs.Exprs import internal_Expr, OpExpr
from exprs.Exprs import call_Expr
from exprs.Exprs import eval_to_lval_Expr
from exprs.Exprs import getattr_Expr
from exprs.Exprs import hold_Expr
from exprs.Exprs import tuple_Expr
from exprs.Exprs import is_pure_expr
from exprs.Exprs import constant_Expr
from exprs.Exprs import eval_Expr
from exprs.Exprs import canon_expr
from exprs.Exprs import EVAL_REFORM

from exprs.ExprsMeta import data_descriptor_Expr_descriptor
from exprs.StatePlace import set_default_attrs
from exprs.__Symbols__ import Anything

# ==

# stubs for StateArg etc are defined lower down

# ==

def Instance(expr, _index_expr = _E_ATTR, _lvalue_flag = False, _noinstance = False, doc = None):
    """
    This macro is assigned to a class attr to declare that its value should be a lazily-instantiated Instance of expr (by default).
    Assuming the arg is an expr (not yet checked?), turn into the expr _self._i_instance(hold_Expr(expr), _E_ATTR),
    which is free in the symbols _self and _E_ATTR. [#e _E_ATTR might be changed to _E_INDEX, or otherwise revised.]

    This function is also used internally to help implement the Arg and Option macros;
    for their use only, it has a private _index_expr option, giving an index expr other than _E_ATTR for the new Instance
    (which is used to suggest an ipath for the new instance, relative to that of self).

    Similarly, it helps implement ArgExpr etc, for whose sake it has a private option _noinstance.

    Devel scratch comment:
    Note that the Arg and Option macros may have handy, not expr itself, but a "grabarg" expr which needs to be evaluated
    (with _self bound) to produce the expr to be instantiated. What should they pass?? eval_Expr of the expr they have.
    [#doc - reword this]

    Other private options: _lvalue_flag, _noinstance (_noinstance is only supported when EVAL_REFORM is true)
    """
    if doc:
        printnim("Instance doc is not saved anywhere; should turn into a note to formulascanner to save it as metainfo, maybe")#e
    printnim("review: same index is used for a public Option and a private Instance on an attr; maybe ok if no overlap possible???")##e
    global _self # not needed, just fyi
    if EVAL_REFORM:
        if _lvalue_flag:
            assert not _noinstance # since it makes no sense to ask for this then, AFAIK (if ok for one, ok for all -- see below)
            #070119 bugfix to make Set(var,val) work again (eg when clicking a checkbox_pref)
            # rather than evalling var to its current value. This means _lvalue_flag never gets passed to _i_instance.
            res = call_Expr( getattr_Expr(_self, '_i_instance'), eval_to_lval_Expr(expr), _index_expr )
                ####e if this works, then try simplifying it to remove the _i_instance call! (assuming the lval is never needing make)
                # (or given this macro's name, maybe it makes more sense for LvalueArg to manage to not call it...)
        elif _noinstance:#070122
            # we ignore _index_expr, but callers can't help but pass one, so don't complain when they do
            return expr # i.e. Instance(expr) == expr -- not useful directly, but useful as a passthru option from Arg etc.
        else:
            res = call_Expr( getattr_Expr(_self, '_i_instance'),                   expr,  _index_expr )
    else:
            assert not _noinstance, "bug: _noinstance is only supported when EVAL_REFORM is true"
            res = call_Expr( getattr_Expr(_self, '_i_instance'),         hold_Expr(expr), _index_expr, _lvalue_flag = _lvalue_flag )
    return res

_arg_order_counter = 0 #k might not really be needed?

##e problems w/ Arg etc as implem - they need an expr, which can be simplified as soon as an instance is known,
# but we don't really have smth like that, unless we make a new Instance class to support it.
# they need it to calc the index to use, esp for ArgOrOption if it depends on how the arg was supplied
# (unless we implem that using an If or using default expr saying "look in the option" -- consider those!)

def Arg( type_expr, dflt_expr = _E_REQUIRED_ARG_, _attr_expr = None, _arglist = False, **moreopts):
    ### [update 061204: i think this cmt is obs, not sure:] IMPLEM _E_REQUIRED_ARG_ - do we tell _i_instance somehow?
    ###e see new notes at end of file about how to reform Arg into a more coherent object, useful in wider contexts... [070321]
    """
    To declare an Instance-argument in an expr class,
    use an assignment like this, directly in the class namespace:

      attr = Arg( type, optional default value expr )

    Order matters (specifically, execution order of the Arg macros, or maybe only
    of the exprs containing them, while Python is executing a given class definition,
    before the metaclass's __new__ runs); those attrs which are not already defined
    as args in superclasses [nim] are appended to the inherited arglist, whose positions
    are counted from 0.

    (Handling anything about args in superclasses is NIM. ##e)

    The index of the instance made from this optional argument
    will be its position in the arglist (whether or not the arg was supplied
    or the default value expr was used).

    If the default value expr is not supplied, there is no default value (i.e. the arg is required).
    If it is supplied, it is processed through canon_expr (as if Arg was an Expr constructor),
    unless it's one of the special case symbols (meant only for private use by this family of macros)
    _E_REQUIRED_ARG_ or the other _E_ one.##doc

    [_attr_expr is a private option for use by ArgOrOption. So is _lvalue_flag and ###NIM _noinstance (in moreopts).]
    [_arglist is a private option for use by ArgList.]
    """
    global _arg_order_counter
    _arg_order_counter += 1
    required = (dflt_expr is _E_REQUIRED_ARG_)
    argpos_expr = _this_gets_replaced_with_argpos_for_current_attr( _arg_order_counter, required, _arglist )
        # Implem note:
        # _this_gets_replaced_with_argpos_for_current_attr(...) makes a special thing to be noticed by the FormulaScanner
        # and replaced with the actual arg order within the class (but the same within any single attr).
        # ExprsMeta can do that by scanning values in order of Expr construction.
        # But it has to worry about two vals the same, since then two attrs have equal claim...
        # it does that by asserting that a given _arg_order_counter corresponds to only one attr. ########@@@@@@@nim
        # FYI, the other possible use for _arg_order_counter would be to assert that it only increases,
        # but this is not obviously true (or useful) in undoc but presently supported cases like
        #    attr = If(cond, Arg(type1), Arg(type2))
        # (which the present code treats as alternative type decls for the same arg position).
    ##printnim("asserting that a given _arg_order_counter corresponds to only one attr -- in a better way than ive_seen kluge below")####@@@@@
    attr_expr = _attr_expr # what about current attr to use in index for arg instance and/or
        # in finding the arg expr in an instance (the replacement instance for _self) --
        # this is None by default, since _E_ATTR (the attr we're on) shouldn't affect the index,
        # in this Arg macro. When we're used by other macros they can pass something else for that.
    return _ArgOption_helper( attr_expr, argpos_expr, type_expr, dflt_expr, _arglist = _arglist, **moreopts)

def LvalueArg(type_expr, dflt_expr = _E_REQUIRED_ARG_): #061204, experimental syntax, likely to be revised; #e might need Option variant too
    """
    Declare an Arg which will be evaluated not as usual,
    but to an lvalue object, so its value can be set using .set_to, etc.
    """
    return Arg(type_expr, dflt_expr, _lvalue_flag = True)

def _ArgOption_helper( attr_expr, argpos_expr, type_expr, dflt_expr, _lvalue_flag = False, _arglist = False, **moreopts ):
    """
    [private helper for Arg, Option, and maybe ArgOrOption]

    attr_expr should be None, or some sort of expr (in practice always _E_ATTR so far)
      that will get replaced by a constant_Expr for the current attr (in ExprsMeta's FormulaScanner),
      according to whether the current attr should be part of the index and a public option-name for supplying the arg
      (we make sure those conditions are the same). [#e Note that if someday we wanted to include f(attr) in the index,
      but still use attr alone as an option name, we'd have to modify this to permit both f(attr) (or f) and attr to be passed.]

    argpos_expr should similarly be None, or some sort of expr (in practice a private subclass of internal_Expr)
      that will get replaced by a constant_Expr for the argument position (an int) that should be allocated to the current attr's arg
      (determined in ExprsMeta's FormulaScanner by allocating posns 0,1,2,etc to newly seen arg-attrs, whether or not the attr itself
      is public for that arg).

    type_expr ###doc, passed herein to canon_type

    dflt_expr ###doc, can also be _E_DFLT_FROM_TYPE_ or [handled in caller i think, but survives here unmatteringly] _E_REQUIRED_ARG_;
        will be passed through canon_expr

    _lvalue_flag is a private option used by LvalueArg.

    _arglist is a private option used by ArgList.
    """
    if _lvalue_flag:
        printnim("_lvalue_flag's proper interaction with dflt_expr is nim") # in all cases below
            ### guess: we want it to be an expr for a default stateref
    global _self # fyi
    type_expr = canon_type( type_expr)
    printnim("can type_expr legally be self-dependent and/or time-dependent? ###k I guess that's nim in current code!")#070115 comment
    if _arglist:
        # new feature 070321. The type is applied to each element, but the default value is for the entire list --
        # OTOH, when would it ever be used, since even if no args are supplied, the list can be formed??
        # Probably it would only be used when the list was 0 length, and could meaningfully be [], (), or another list-like thing...
        # this is all a guess and I probably won't even review this code for this issue now, unless it fails when tried. ####k
        type_expr = tuple_Expr(type_expr) # type-coerce the value to a list of the given type [070321 guess] ###e or list_Expr???
    if dflt_expr is _E_DFLT_FROM_TYPE_:
        dflt_expr = default_expr_from_type_expr( type_expr)
            ## note [070115], this would be impossible for time-dependent types! and for self-dep ones, possible but harder than current code.
        assert is_pure_expr(dflt_expr) #k guess 061105
    else:
        dflt_expr = canon_expr(dflt_expr) # hopefully this finally will fix dflt 10 bug, 061105 guesshope ###k [works for None, 061114]
        assert is_pure_expr(dflt_expr) # not sure this is redundant, since not sure if canon_expr checks for Instance ###k
        printnim("not sure if canon_expr checks for Instance")
    # Note on why we use explicit call_Expr & getattr_Expr below,
    # rather than () and . notation like you can use in user-level formulae (which python turns into __call__ and getattr),
    # to construct Exprs like _self._i_grabarg( attr_expr, ...):
    # it's only to work around safety features which normally detect that kind of Expr-formation (getattr on _i_* or _e_*,
    # or getattr then call) as a likely error. These safety features are very important, catching errors that would often lead
    # to hard-to-diagnose bugs (when our code has an Expr but thinks it has an Instance), so it's worth the trouble.
    held_dflt_expr = hold_Expr(dflt_expr)
        # Note, this gets evalled back into dflt_expr (treated as inert, may or may not be an expr depending on what it is right here)
        # by the time _i_grabarg sees it (the eval is done when the call_Expr evals its args before doing the call).
        # So if we wanted _i_grabarg to want None rather than _E_REQUIRED_ARG_ as a special case, we could change to that (there & here).
    grabopts = {}
    if _arglist:
        grabopts.update(dict(_arglist = constant_Expr(_arglist)))
    grabarg_expr = call_Expr( getattr_Expr(_self, '_i_grabarg'), attr_expr, argpos_expr, held_dflt_expr, **grabopts )
        # comments 070115:
        # - This will eval to an expr which depends on self but not on time. We could optim by wrapping it
        # (or declaring it final) in a way which effectively replaced it with its value-expr when first used.
        # (But it's not obvious where to store the result of that, since the exprs being returned now are assigned to classes
        #  and will never be specific to single selfs. Do we need an expr to use here, which can cache its own info in self??
        #  Note: AFAIK, self will be the same as what _self gets replaced with when this is used. (We ought to assert that.) ###e)
        # - Further, grabarg_expr is probably supposed to be wrapped *directly* by eval_Expr, not with type_expr inside. I think I'll
        # make that change right now and test it with EVAL_REFORM still False, since I think it's always been required, as said
        # in other comments here. DOING THIS NOW.
    if attr_expr is not None and argpos_expr is not None:
        # for ArgOrOption, use a tuple of a string and int (attr and argpos) as the index
        index_expr = tuple_Expr( attr_expr, argpos_expr )
    elif attr_expr is None and argpos_expr is None:
        assert 0, "attr_expr is None and argpos_expr is None ..."
    elif attr_expr is not None:
        # for Option, use a plain attr string as the index
        index_expr = attr_expr
    else:
        assert argpos_expr is not None
        # for Arg, use a plain int as the index
        # (note: ExprsMeta replaces argpos_expr with that int wrapped in constant_Expr, but later eval pulls out the raw int)
        index_expr = argpos_expr
# see if this is fixed now, not that it means much since we were using a stub... but who knows, maybe the stub was buggy
# and we compensated for that and this could if so cause a bug:
##    printnim("I suspect type_expr (stub now) is included wrongly re eval_Expr in _ArgOption_helper, in hindsight 061117")
##        ### I suspect the above, because grabarg expr needs to be evalled to get the expr whose type coercion we want to instantiate
    res = Instance( _type_coercion_expr( type_expr, eval_Expr(grabarg_expr) ),
                     _index_expr = index_expr, _lvalue_flag = _lvalue_flag, **moreopts )
        # note: moreopts might contain _noinstance = True, and if so, Instance normally returns its first arg unchanged
        # (depending on other options).
        # 070115 replaced eval_Expr( type_expr( grabarg_expr)) with _type_coercion_expr( type_expr, eval_Expr(grabarg_expr) )
    return res # from _ArgOption_helper

def _type_coercion_expr( type_expr, thing_expr):
    ###e should we make this a full IorE (except when type_expr is Anything?) in order to let it memoize/track its argvals?
    # (can import at runtime if nec.)
    """
    [private helper for Arg, etc] [#e stub]

    Given an expr for a type and an expr [to be evalled to get an expr?? NO, caller use eval_Expr for that] for a thing,
    return an expr for a type-coerced version of the thing.
    """
    if type_expr is None or type_expr is Anything:
        return thing_expr
    # ArgList causes us to get here as well:
    # print "ignoring this type_expr for now: %r" % (type_expr,) # <tuple_Expr#1833: (S.Anything,)>
    return thing_expr

    assert 0, "this will never run" # until we fix canon_type to not always return Anything!!
    print "TypeCoerce is nim, ignoring",type_expr #####070115   ###IMPLEM TypeCoerce
    from xxx import TypeCoerce # note, if xxx == IorE's file, runtime import is required, else recursive import error; use new file??
    return TypeCoerce( type_expr, thing_expr)
        # a new expr, for a helper IorE -- this is an easy way to do some memoization optims (almost as good as optim for finalization),
        # and permit either expr to be time-dependent (not to mention self-dependent) [070115]

class _this_gets_replaced_with_argpos_for_current_attr(internal_Expr):#e rename? mention FormulaScanner or ExprsMeta; shorten
    def _internal_Expr_init(self):
        (self._e__arg_order_counter, self._e_is_required, self._e_is_arglist) = self.args # _e_is_arglist added 070321
            # first arg not presently used, might be obs here and even in caller ##k
        self.attrs_ive_seen = {}
    def _e_override_replace(self, scanner):
        """
        This gets called by a formula scanner when it hits this object in an expr...
        it knows lots of private stuff about FormulaScanner.
        """
        attr = scanner.replacements[_E_ATTR] # a constant_Expr, or an indication of error if this happens (maybe missing then?)
        attr = attr._e_constant_value
        if 1:
            # quick & dirty check for two attrs claiming one arg... come to think of it, is this wrong re inclusion?
            # no, as long as overall replace (of this) happens before this gets called, it'll be ok.
            # but, a better check & better errmsg can be done in scanner if we pass our own args to it.
            # WAIT, i bet this won't actually catch the error, since the replace would actually occur... have to do it in the scanner.
            printnim("improve quick & dirty check for two attrs claiming one arg (it may not even work)")###e
            self.attrs_ive_seen[attr] = 1
            assert len(self.attrs_ive_seen) <= 1, "these attrs claim the same arg: %r" % self.attrs_ive_seen.keys()
            # WARNING: if this works, it will break the use of Arg in future things like lambda_expr or _e_extend
            # where the same Arg() object might get passed to multiple class/attr contexts in runtime-generated exprs with Arg decls.
            # If/when that happens, this object needs to be made immutable, which can be done by removing this code (inside 'if 1'),
            # since it's probably either not working or redundant, according to the comments above and my best guess now. [070321 comment]
        required = self._e_is_required
        arglist = self._e_is_arglist
        pos = scanner.argpos(attr, required, arglist = arglist)
        res = constant_Expr(pos) # this gets included in the scanner's processed expr
        return res
    def _e_eval(self, *args):
        assert 0, "this %r should never get evalled unless you forgot to enable formula scanning (I think)" % self ##k
    pass

def Option( type_expr, dflt_expr = _E_DFLT_FROM_TYPE_, **moreopts):
    """
    To declare a named optional argument in an expr class,
    use an assignment like this, directly in the class namespace,
    and (by convention only?) after all the Arg macros:

      attr = Option( type, optional default value)

    Order probably doesn't matter.

    The index of the instance made from this optional argument
    will be attr (the attribute name).

    If the default value is needed and not supplied, it comes from the type.
    """
    global _E_ATTR # fyi
    argpos_expr = None
    attr_expr = _E_ATTR
    return _ArgOption_helper( attr_expr, argpos_expr, type_expr, dflt_expr, **moreopts)

def ArgOrOption(type_expr, dflt_expr = _E_DFLT_FROM_TYPE_, **moreopts):
    """
    means it can be given positionally or using its attrname [#doc better]
    index contains both attr and argpos; error to use plain Arg after this in same class (maybe not detected)
    """
    global _E_ATTR # fyi
    attr_expr = _E_ATTR
    return Arg( type_expr, dflt_expr, _attr_expr = attr_expr, **moreopts)

def ArgExpr(*args, **moreopts):
    ## return Arg(*args, _noinstance = True) -- syntax error, i don't know why
    moreopts['_noinstance'] = True #k let's hope we always own this dict
    return Arg(*args, **moreopts)

def OptionExpr(*args, **moreopts):
    moreopts['_noinstance'] = True
    return Option(*args, **moreopts)

def ArgOrOptionExpr(*args, **moreopts):
    moreopts['_noinstance'] = True
    return ArgOrOption(*args, **moreopts)

def ArgList(*args, **moreopts): #070321 [tentatively replaces the scratch file ArgList.py]
    # status, 070321 9:30pm: works, except for bad de-optim mentioned below,
    # and unexplained 'expr or lvalflag for instance changed' in _30i. ###BUGS (not showstoppers)
    moreopts['_arglist'] = True
        ###WARNING: there is a bad de-optim due to this, explained in tuple_Expr._e_make_in -- no per-arglist-elt instance caching.
        # WARNING: the implementing code for this uses tuple_Expr, not list_Expr.
        # But args which take explicit lists typically declare their types as list_Expr,
        # and formulae to construct them typically use list_Expr.
        # Since all these are intended to be immutable lists
        # (though perhaps time-dependent ones, with lengths changing even by insertion
        #  due to time-dependent formulae constructing them),
        # my guess is that eventually we'll just make list_Expr a synonym for tuple_Expr.
        # But for now, they are distinct Exprs which eval to python lists/tuples respectively
        # (when they contain nothing that needs instantiation).
    return Arg(*args, **moreopts)

#e ArgListOrOption? it would let you pass a list inline as args, *or* (not and) as a list_Expr- or list- valued named option,
#  or (ignoring the difference I think) a tuple_Expr- or tuple- valued one.
#e ArgExprList? it would let you pass a list of expr formulae inline, turning them into a tuple_Expr, instantiable to a list and/or
#   usable as a list of exprs (e.g. they might get individually wrapped before being instantiated, or get filtered or chosen from, etc)
# But, we *won't* define the names: ArgListExpr (I think)... don't know about any mix of ArgListOrOption and Expr.
# Don't know yet about any mixes of State and Expr, or State and Formula, either. [070321]

# ==

# stubs:

def ArgStub(*args): return Arg(Anything)
## ArgList = ArgStub #e see also ArgList.py
InstanceList = InstanceDict = ArgStub

StateArg = Arg ###STUB - state which can be initially set by an arg...
    # there may be some confusion about whether we set it to an arg formula & later replace with a set formula,
    # or set it to a snapshot in both cases. Review all uses -- maybe split into two variants. [070131]
    #e if it's snapshot version (as I usually thought),
    # StateArg etc can perhaps be implemented as State with a special dflt expr which is Arg (if scanner sees that deep);
    # index ought to be correct!
StateOption = Option ###STUB
StateArgOrOption = ArgOrOption ###STUB
# StateInstance = Instance? Probably not... see class State (not always an Instance).


#e ProducerOf? ExprFor?

#e related macros:
# - Instance(expr, optional index) # default index is attr we assign it to, you can replace or extend that (only replace is implem)
# - InstanceDict(value-expr, optional key-set or key-sequence, optional key-to-index-func) # these exprs can be in _i/_key by default
# - InstanceList(value-expr, number-of-elts, optional key-to-index-func)
## digr: a reason i try to say "range" for "domain" is the use of Python range to create the list of domain indices!
# - Arg variants of those - replace expr with type, inferring expr as type(arg[i]) for i inferred as for Instance,
#   but also come in an order that matters; so:
# - Arg(type, optional default-value expr)
# - ArgList(type-expr) # applies to the remaining args; index should be (attr, posn in this list), I think
# - ArgDict would apply to the remaining kwargs... not sure we'll ever want this

# ==

def canon_type(type_expr):###stub [note: this is not canon_expr!]
    """
    Return a symbolic expr representing a type for coercion
    """

    return Anything # for now! when we implement TypeCoerce, revise this

    printnim("canon_type is a stub; got %r" % type_expr) ## so far: Widget2D, int
    return lambda x:x #stub
##    # special cases [nim]
##    for k,v in {int:Int, float:Float, str:String}.iteritems():
##        if type_expr is k:
##            type_expr = v
##            break
##    ### not sure if for Widget2D or Color or Width we return that, or TypeCoerce(that), or something else
##    assert is_pure_expr(type_expr)
##    return type_expr #stub; needs to work for builtin types like int,
##        # and for InstanceOrExpr subclasses that are types (like Widget -- or maybe even Rect??)
##    # note that the retval will get called to build an expr, thus needs to be in SymbolicExpr -- will that be true of eg CLE?
##    # if not, then some InstanceOrExpr objs need __call__ too, or constructor needs to return a SymbolicExpr, or so.

def default_expr_from_type_expr(type_expr): #061115
    ## note [070115], this would be impossible for time-dependent types! and for self-dep ones, possible but harder than current code.
    """
    #doc
    """
##    assert type_expr is Stub # only permitted for these ones; not even correct for all of them, but surely not for others like int
# Stub is not defined here, never mind
    return canon_expr(None) # stub; only right for Action, wrong for int, str, etc ###e might need revision for ArgList?

# ==

class data_descriptor_Expr(OpExpr):
    def _e_init(self):
        assert 0, "subclass of data_descriptor_Expr must implement _e_init"
    def __repr__(self): # class data_descriptor_Expr
        # same as in OpExpr, for now
        ###e if we end up knowing our descriptor or its attr, print that too
        return "<%s#%d%s: %r>"% (self.__class__.__name__, self._e_serno, self._e_repr_info(), self._e_args,)
    pass

class State(data_descriptor_Expr):
    """
    """
    # note: often referred to as "State macro", even though we don't presently say "def State"
    # (except right here as search engine bait)

    # TODO: big optim: make a variant which just stores the LvalForState object directly in instance.__dict__[attr].
    # That requires replacing not only self._e_attrholder but its API -- now it returns something whose .attr
    # should be accessed; instead the callers need rewriting to just find the LvalForState object and use it.
    # We can then use that variant exclusively unless we want to support old-style reloading in pure exprs tests,
    # and reloading is disabled anyway, so the old style would probably never be returned to. And then we might not
    # need ipath -- not sure (not sure if that's the only use, and we'd still need indexes in single exprs I think).
    # BTW we'd still want State to be turned into a descriptor rather than actually being one,
    # since (I think) we still need ExprsMeta to do substitutions in the exprs it contains
    # (for type (someday) and default value).
    # [bruce 070831 comment]

    # experimental, 061201-04; works (testexpr_16);
##    # supercedes the prior State macro in Exprs.py [already removed since obs and unfinished, 061203]
##    # see also C_rule_for_lval_formula, now obs, meant to be used by that old design for the State macro,
##    # but that design doesn't anticipate having an "lval formula",
##    # but just has an implicit self-relative object and explicit attrname to refer to.

    # Note: the default value expr is evaluated only just when it's first needed.
    # Exception to that: if something like ObjAttr_StateRef asks for our lval using
    # self._e_StateRef__your_attr_in_obj_ref, we evaluate it then,
    # even though it won't strictly be needed until something asks that stateref for our value
    # (if it ever does). I don't know if this can cause problems of too-early eval of that default value. ###REVIEW
    # [bruce 070816 comment]

    _e_wants_this_descriptor_wrapper = data_descriptor_Expr_descriptor
    _e_descriptor = None

    def _e_init(self):
        def myargs(type, dflt = None): # note: these args (not kws) are exprs, and already went through canon_expr
            dflt = dflt ##e stub; see existing stateref code for likely better version to use here
            ##e do we need to de-expr these args?? (especially type)
            ##e dflt is reasonable to be an expr so we'll eval it each time,
            # but do we need code similar to what's in _i_grabarg to do that properly? guess: yes.
            self._e_state_type = type # not _e_type, that has a more general use as of 070215
            self._e_default_val = dflt
            # note: this does not process _e_kws. self._e_debug was set in OpExpr.__init__.
        myargs(*self._e_args)
        # 070831 exploring new State keyword args, for metainfo like minimum
        for kw in self._e_kws.keys():
            if kw != 'doc':
                print "\n*** unrecognized State keyword arg: %s" % kw
            continue
        return
    def _e_set_descriptor(self, descriptor):
        """
        In general (ie part of API of this method, called by data_descriptor_Expr_descriptor):
        storing the descriptor is optional, since it's also passed into the get and set calls.
        In this subclass, we have to store it, since _e_eval can be called without otherwise knowing descriptor.attr.
        """
        if self._e_descriptor is not None:
            assert self._e_descriptor is descriptor, \
                   "bug: %r is not None or %r in %r" % \
                   ( self._e_descriptor, descriptor, self)
                # bug: this failed for Ninad in class MultipleDnaSegmentResize_EditCommand(DnaSegment_EditCommand)
                # (not yet committed, won't be in that form); see email he sent me today [bruce 080514]
        else:
            self._e_descriptor = descriptor
        return
    def _e_get_for_our_cls(self, descriptor, instance):
        if self._e_debug:
            print "_e_get_for_our_cls",(self, descriptor, instance, )
        if self._e_descriptor is not None:
            assert self._e_descriptor is descriptor, \
                   "different descriptors in get: %r stored, %r stored next" % (self._e_descriptor, descriptor)
            ####@@@@ I predict that will happen due to descriptor copying. (Unless we always access this through py code.)
            # (no, that was a bug effect -- i mean, as soon as we use subclasses inheriting a State decl.)
            # I think that copying is not needed in this case. So we probably need to disable it in our class of descriptor. #e [061204]
        attr = descriptor.attr
        holder = self._e_attrholder(instance, init_attr = attr) # might need attr for initialization using self._e_default_val
        return getattr(holder, attr)
    def _e_set_for_our_cls(self, descriptor, instance, val):
        if self._e_debug:
            print "_e_set_for_our_cls",(self, descriptor.attr, instance, val)
        if self._e_descriptor is not None:
            assert self._e_descriptor is descriptor, \
                   "different descriptors in set: %r stored, %r stored next" % (self._e_descriptor, descriptor) # see comment above
        attr = descriptor.attr
        holder = self._e_attrholder(instance) # doesn't need to do any initialization
        return setattr(holder, attr, val)
    def _e_attrholder(self, instance, init_attr = None):
        res = instance.transient_state #e or other kind of stateplace
        # init the default val if needed.
        if init_attr:
            attr = init_attr
            # we need to init the default value for attr, if it's not already defined.
            ####e OPTIM: this hasattr might be slow (or even buggy, tho i think it'll work
            # by raising an exception that's a subclass of AttributeError; the slow part is computing args for that every time)
            if not hasattr(res, attr):
                val = self._e_eval_defaultValue(attr, instance)
                #k should I just do setattr(res, attr, val), or is there something special and better about this:
                ## set_default_attrs(res, {attr : val}) ##k arg syntax
                set_default_attrs(res, **{attr : val})
                # print_compact_stack( "\ndid set_default_attrs of %r, %r, %r: " % (res,attr,val))
                val0 = getattr(res, attr)
                ## assert val is val0,
                if not (val is val0):
                    print "bug: set_default_attrs should have stored %r at %r in %r, but it has %r" % (val, attr, res, val0)
            pass
        return res
    def _e_eval_defaultValue(self, attr, instance): #070904 split this out
        # Note [added 070904]: the default value should not depend on the
        # current values of other State slots (though it can be an expr,
        # and it's fine if it depends on customized instance parameters).
        # In current code, I suspect there can be errors (nondeterminisism)
        # if it does (not sure). This is especially true after today's kluge
        # (a new call of this helper method), which can evaluate this twice.
        # See KLUGE 070904 for cleanup suggestions.
        # Q: Would it be better to change this requirement, to make it say
        # "it's ok if it tries to depend on the values of other State,
        # but we eval it with all State slots at their default values
        # to make sure it's deterministic as used"?

        # eval the dflt expr here, much like _i_instance does it:
        val_expr = self._e_default_val
        index = attr
        val = instance._i_eval_dfltval_expr(val_expr, index)
        return val

    ## AttributeError: no attr '_e_eval_function' in <class 'exprs.attr_decl_macros.State'>   -- why does someone want to call this??
    # where i am 061203 1023p stopping for night -- wondering that. in testexpr_16.
    #
    ##exception in <Lval at 0xff2db70>._compute_method NO LONGER ignored:
    ##    exceptions.AssertionError: recursion in self.delegate computation in <Highlightable#8076(i)>
    ##  [lvals.py:209] [Exprs.py:208] [Exprs.py:400] [instance_helpers.py:677]
    def _e_eval(self, env, ipath):
        # 070112 comment: the print below has been there a long time and I don't recall ever seeing it,
        # so the comment below it guessing it may no longer happen is probably right,
        # meaning that this method probably never gets called anymore.
        #
        # 061204 comments:
        #e - compare to property_Expr
        # - it may indicate a bug that we get here at all -- i thought we'd go through our descriptor instead. maybe only thru py code?
        # - the descriptor knows attr, we don't -- is that ok? no -- it won't let us initialize attr or even find it!
        #   SO WE HAVE TO GET DESCRIPTOR TO SET ITSELF (or at least attr) INSIDE US, exclusively. Doing this now. #######@@@@@@@
        ##e - we may also want a variant of this which "evals us as an lvalue, for use as arg1 of Set()" []
        assert env #061110
        instance = env._self # AttributeError if it doesn't have this [###k uses kluge in widget_env]
        assert self._e_descriptor is not None
        descriptor = self._e_descriptor
        res = self._e_get_for_our_cls(descriptor, instance)
        print "fyi: _e_eval (not thru __get__, i think) of self = %r in instance = %r gets res = %r" % (self, instance, res)
            ### I SUSPECT this never happens now that formula-scanner is properly called on us, but I'm not sure, so find out.
            ### ALSO we'll now see the predicted above bug from copying the descriptor, when we use subclasses inheriting a State decl.
        return res
    def _e_StateRef__your_attr_in_obj_ref( self, descriptor, instance):
        if self._e_debug:
            print "_e_StateRef__your_attr_in_obj_ref",(self, descriptor, instance)
            ### TODO (if needed for future debugging):
            # - also print_compact_stack;
            # - also set lval._changes__debug_print on this lval.
        if self._e_descriptor is not None:
            assert self._e_descriptor is descriptor, \
                   "different descriptors in _e_StateRef__your_attr_in_obj_ref: %r stored, %r stored next" % \
                       (self._e_descriptor, descriptor) # see comment above
        attr = descriptor.attr
        holder = self._e_attrholder(instance, init_attr = attr) # might need attr for initialization using self._e_default_val
            # Note: passing init_attr is necessary to prevent a bug, if this is the first access to this lval
            # before either self._e_get_for_our_cls or self._e_set_for_our_cls.
            # The symptom of the bug was a mysterious error message,
            # ... LvalError_ValueIsUnset: access to key '653872' in some lvaldict in
            #     <_attr_accessor(transient,) at 0x29742eb8>, before that value was set ...
            # which resulted from set_default_attrs never having been run in self._e_attrholder.
            # [bruce 070816 note and bugfix]
        ## print "got this holder, now what?", holder
        ## return setattr(holder, attr, val)
        lval = holder._attr_accessor__get_lval(attr) # should work for now..... ##KLUGE to assume what class & use private method
        # print "got lval: %r\n" % (lval,)
        # lval._changes__debug_print = True # cause various code that touches this lval to print what it does
        if not hasattr(lval, 'defaultValue'):
            # KLUGE 070904; needs cleanup and optim (can eval dflt val expr twice);
            # could be cleaned up easily if it turns out set_default_attrs
            # always calls _set_defaultValue in the lval, since we could make
            # that method set this attr, and make the call of it depend on it
            # not being set. Alternatively we could set a function for computing
            # default val if needed, on the lval itself. ###REVIEW
            lval.defaultValue = self._e_eval_defaultValue(attr, instance)
        return lval

    pass # end of class State

# note: an old def of State, never working, from 061117, was removed 061203 from cvs rev 1.88 of Exprs.py

# ==

# note: for StateArray or StateArrayRefs see statearray.py

# ==

# some advice about reforming Arg in the future, and about implementing ArgList better then, but tolerably now
# (which I'm in the middle of as of 070321 4pm): [edited 070323]
"""
##e some future forms we might want:

expr._e_customize( existing_option_or_arg = value_or_formula )

expr._e_extend( new_option = Option(type, dflt, doc = ""))
expr._e_extend( new_arg = Arg(type, dflt, doc = ""))

so Option and Arg turn into parameter-declaring exprs

which are special because inside a class def, they are not treated as formula for value,
but as formula for type or descriptor, used with other data to get value, as well as set method...
so they are not exprs in the same way as other things are -- we might not want to say they are at all.
Lets say they turn into parameter descriptors.
(I'm guessing they'll be true Python descriptors. I haven't verified that's possible. ###k)

expr._e_extend( new_var = State(type, dflt, doc = "")) # and options to control state-sharing, too


expr._e_customize( _e_type = "..." ) ???

expr._e_customize( _e_type_for_<interface> = ... ) ???

expr._e_customize( _e_meets_<interface> = <boolean> ) ???

==

Arg advice: ###e point to this in ExprsMeta.py and def ArgList too

Here is some new advice about how to reform Arg(), make ArgList(), etc --
btw I then made ArgList today (or started it), but that doesn't supercede this:

- it should become a kind of expr (also Option, etc; note that State already is an expr)

- which is not mutable -- when it learns argpos or attr, it gets replaced with a related expr
  - which might be toplevel-expressed as the same thing with new options which reveal those params,
    i.e. Arg(type_expr, dflt_expr, doc = doc_expr,
             argpos = argpos_expr, attr = attr_expr, required = boolean)

- which has special behavior when used as toplevel class assignment value
(turning into a special kind of descriptor, perhaps one that wraps the decl)
(but review the need for ExprsMeta then modifying the descriptor as it gets inherited into subclasses --
I can no longer remember a justification, since each use passes it the class, I think
 [#k verify that! there was some use that failed to pass something! just the attr?!?],
but I can remember trying to remember a justification and failing...)

- but which in future will also have similar special behavior when used in a lambda_expr [nim],
  or in the _e_extend forms shown above [in '070227 coding log', dated 070321], or the like

- for direct assignment of the Arg expr itself to a class attr, wrap it in hold_Expr, I think
  (but since that permits replacements in general, does it turn them off in this case???
   If not, we might need a special form of hold; or to make those special replacements
   only work at toplevel, i.e. if it's the whole rhs but not a subexpr of it.)
  (maybe they are not even "replacements" but something else -- interactions of the scanner
   with the top things, to decide how to treat them, which can do whatever they like,
   e.g. allow the scanner to add them to an arg-decl-list, known to the class,
   so it can finally detect extra or missing args, implem ArgList, etc.)

- maybe the special behavior which assigns the argpos should be lazy...
that is, replace Arg with something belonging to this instance of it
but not yet knowing the exact argpos. Also put it in a list known to the class.
Then the class (or customized expr) can scan that and assign numbers,
and create code for processing real arglists and knowing what's extra, etc.
Then ArgList is a simple variant of that processing code.

==

update 070323:

let's think about how, in practice, we extract the arg decls from an expr (whether made by ExprsMeta, or also by _e_extend).
... Don't we want the expr to just know them? ExprsMeta should make them in an explicit way, and _e_extend should add to that
(and know which ones are in the class and which ones only in customization formulae). There is, I guess, a decls object
(or list, if that's enough) which has them all. It's trivial to add to them... a first step is reforming what these things
like Arg() actually are. (See above on that.)

There might be an easier short term kluge, too...

- try1 idea [superseded below]: add stuff to those macros (def Arg, etc) which the formula scanner sees
and adds to the decl list, even though it's not the same thing that makes it work.

- better version of that: ##### DO THIS SOON
make the new objects (class Arg, etc),
let the scanner add them to the decl list, but to make them work, let it ask them to expand into the old macros for now.
Just rename def Arg to def Arg_expansion, make a new class Arg, tell it about Arg_expansion, or something like that.
For the simpler ones like ArgExpr and ArgList, let them have expansion methods instead.
For how class Arg controls what ExprsMeta & its scanner does, see class State. Make sure class State fits into the scheme, too!

==

... I decided to implem ArgList now [070321], so I'm doing it, in a few files, see _arglist...
plan is to test it in SimpleColumn...
I'll have to worry about def Apply in controls.py which overrides it -- my guess is,
I should rewrite it more fully than just for that issue... ###
[note that it works but is too inefficient, so using it in SimpleColumn is disabled until that can be worked out -- 070323]

### list_Expr or tuple_Expr? the latter -- see comment near def ArgList

### we might need some type related code to handle tuple_Expr(Anything) or so...

### we'll need new code for _e_make_in on tuple_Expr.

### tuple_Expr should eval to a tuple when it contains pure data,
but not when it contains exprs that need instantiation!!!
But right now we don't know how to tell the difference!
Hmm, I guess we do -- does the value belong to IorE or have _e_make_in? A kluge but should work.

"""

# end
