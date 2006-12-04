"""
attr_decl_macros.py -- Instance, Arg, Option, ArgOrOption, State

$Id$

[was in Exprs.py when developed, before State;
 split into this file 061203 to ease recursive import issues with State]
"""

from basic import * # recursive import
from basic import _self

# Symbols for private or semi-private use
# (note, other modules that need these also import them directly from __Symbols__)
from __Symbols__ import _E_ATTR, _E_REQUIRED_ARG_, _E_DFLT_FROM_TYPE_

# ==

def Instance(expr, _index_expr = _E_ATTR):
    """This macro is assigned to a class attr to declare that its value should be a lazily-instantiated Instance of expr. 
    Assuming the arg is an expr (not yet checked?), turn into the expr _self._i_instance(hold_Expr(expr), _E_ATTR),
    which is free in the symbols _self and _E_ATTR. [#e _E_ATTR might be changed to _E_INDEX, or otherwise revised.]
       This function is also used internally to help implement the Arg and Option macros;
    for their use only, it has a private _index_expr option, giving an index expr other than _E_ATTR for the new Instance.
    Note that they may have handy, not expr itself, but a "grabarg" expr which needs to be evaluated (with _self bound)
    to produce that expr. What should they pass?? eval_Expr of the expr they have. [#doc - reword this]
    """
    printnim("review: same index is used for a public Option and a private Instance on an attr; maybe ok if no overlap possible???")##e
    global _self # not needed, just fyi
    ##printnim("why is the expr in the _i_instance call not held??? ##k -- it's %r" % (expr,) )#####@@@@@ see what exprs get printed
        #guess: it should be, but we didn't notice since canon_expr fixes it. question: is it ever a replace-me-in-scan thing??
    return call_Expr( getattr_Expr(_self, '_i_instance'), hold_Expr(expr), _index_expr) 

_arg_order_counter = 0 #k might not really be needed?

##e problems w/ Arg etc as implem - they need an expr, which can be simplified as soon as an instance is known,
# but we don't really have smth like that, unless we make a new Instance class to support it.
# they need it to calc the index to use, esp for ArgOrOption if it depends on how the arg was supplied
# (unless we implem that using an If or using default expr saying "look in the option" -- consider those!)

def Arg( type_expr, dflt_expr = _E_REQUIRED_ARG_, _attr_expr = None): ###IMPLEM _E_REQUIRED_ARG_ - do we tell _i_instance somehow?
    """To declare an Instance-argument in an expr class,
    use an assignment like this, directly in the class namespace:
          attr = Arg( type, optional default value expr )
       Order matters (specifically, execution order of the Arg macros, or maybe only
    of the exprs containing them, while Python is executing a given class definition,
    before the metaclass's __new__ runs); those attrs which are not already defined
    as args in superclasses are appended to the inherited arglist, whose positions
    are counted from 0.
       (Handling anything about args in superclasses is NIM. ##e)
       The index of the instance made from this optional argument
    will be its position in the arglist (whether or not the arg was supplied
    or the default value expr was used).
       If the default value expr is not supplied, there is no default value (i.e. the arg is required).
    If it is supplied, it is processed through canon_expr (as if Arg was an Expr constructor),
    unless it's one of the special case symbols (meant only for private use by this family of macros)
    _E_REQUIRED_ARG_ or the other _E_ one.##doc
       [_attr_expr is a private option for use by ArgOrOption.]
    """
    global _arg_order_counter
    _arg_order_counter += 1
    required = (dflt_expr is _E_REQUIRED_ARG_)
    argpos_expr = _this_gets_replaced_with_argpos_for_current_attr( _arg_order_counter, required )
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
    return _ArgOption_helper( attr_expr, argpos_expr, type_expr, dflt_expr)

def _ArgOption_helper( attr_expr, argpos_expr, type_expr, dflt_expr ):
    """[private helper for Arg, Option, and maybe ArgOrOption]
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
    """
    global _self # fyi
    type_expr = canon_type( type_expr)
    if dflt_expr is _E_DFLT_FROM_TYPE_:
        dflt_expr = default_expr_from_type_expr( type_expr)
        assert is_pure_expr(dflt_expr) #k guess 061105
    else:
        dflt_expr = canon_expr(dflt_expr) # hopefully this finally will fix dflt 10 bug, 061105 guesshope ###k [works for None, 061114]
        assert is_pure_expr(dflt_expr) # not sure this is redundant, since not sure if canon_expr checks for Instance ###k
        printnim("not sure if canon_expr checks for Instance")
    # Note: we have to use explicit call_Expr & getattr_Expr below, to construct Exprs like _self._i_grabarg( attr_expr, ...),
    # only to work around safety features which normally detect that kind of Expr-formation (getattr on _i_* or _e_*,
    # or getattr then call) as a likely error. These safety features are very important, catching errors that would often lead
    # to hard-to-diagnose bugs (when our code has an Expr but thinks it has an Instance), so it's worth the trouble.
    held_dflt_expr = hold_Expr(dflt_expr) 
        # Note, this gets evalled back into dflt_expr (treated as inert, may or may not be an expr depending on what it is right here)
        # by the time _i_grabarg sees it (the eval is done when the call_Expr evals its args before doing the call).
        # So if we wanted _i_grabarg to want None rather than _E_REQUIRED_ARG_ as a special case, we could change to that (there & here).
    grabarg_expr = call_Expr( getattr_Expr(_self, '_i_grabarg'), attr_expr, argpos_expr, held_dflt_expr )
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
    printnim("I suspect type_expr (stub now) is included wrongly re eval_Expr in _ArgOption_helper, in hindsight 061117")
        ### I suspect the above, because grabarg expr needs to be evalled to get the expr whose type coercion we want to instantiate
    return Instance( eval_Expr( type_expr( grabarg_expr)), _index_expr = index_expr )

class _this_gets_replaced_with_argpos_for_current_attr(internal_Expr):#e rename? mention FormulaScanner or ExprsMeta; shorten
    def _internal_Expr_init(self):
        (self._e__arg_order_counter, self._e_is_required,) = self.args
            # first arg not presently used, might be obs here and even in caller ##k
        self.attrs_ive_seen = {}
    def _e_override_replace(self, scanner):
        """This gets called by a formula scanner when it hits this object in an expr...
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
        required = self._e_is_required
        pos = scanner.argpos(attr, required)
        res = constant_Expr(pos) # this gets included in the scanner's processed expr
        return res
    def _e_eval(self, *args):
        assert 0, "this %r should never get evalled unless you forgot to enable formula scanning (I think)" % self ##k
    pass

def Option( type_expr, dflt_expr = _E_DFLT_FROM_TYPE_):
    """To declare a named optional argument in an expr class,
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
    return _ArgOption_helper( attr_expr, argpos_expr, type_expr, dflt_expr)    

def ArgOrOption(type_expr, dflt_expr = _E_DFLT_FROM_TYPE_):
    """means it can be given positionally or using its attrname [#doc better]
    index contains both attr and argpos; error to use plain Arg after this in same class (maybe not detected)
    """
    global _E_ATTR # fyi
    attr_expr = _E_ATTR
    return Arg( type_expr, dflt_expr, _attr_expr = attr_expr)

# ==

# stubs:
Anything = "anything-stub"
def ArgStub(*args): return Arg(Anything)
ArgList = ArgStub
InstanceList = InstanceDict = ArgStub

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
    "Return a symbolic expr representing a type for coercion"
    printnim("canon_type is a stub; got %r" % type_expr) ## so far: Widget2D, int
    return lambda x:x #stub
##    # special cases [nim]
##    for k,v in {int:Int, float:Float, str:String}.iteritems():
##        if type_expr is k:
##            type_expr = v
##            break
##    ### not sure if for Widget2D or Color or Width we return that, or TypeCoercer(that), or something else
##    assert is_pure_expr(type_expr)
##    return type_expr #stub; needs to work for builtin types like int,
##        # and for InstanceOrExpr subclasses that are types (like Widget -- or maybe even Rect??)
##    # note that the retval will get called to build an expr, thus needs to be in SymbolicExpr -- will that be true of eg CLE?
##    # if not, then some InstanceOrExpr objs need __call__ too, or constructor needs to return a SymbolicExpr, or so.

def default_expr_from_type_expr(type_expr): #061115
    "#doc"
##    assert type_expr is Stub # only permitted for these ones; not even correct for all of them, but surely not for others like int
# Stub is not defined here, never mind
    return canon_expr(None) # stub; only right for Action, wrong for int, str, etc

# ==

class data_descriptor_Expr(OpExpr):
    def _e_init(self):
        assert 0, "subclass of data_descriptor_Expr must implement _e_init"
    def __repr__(self): # class data_descriptor_Expr
        # same as in OpExpr, for now
        ###e if we end up knowing our descriptor or its attr, print that too
        return "<%s#%d%s: %r>"% (self.__class__.__name__, self._e_serno, self._e_repr_info(), self._e_args,)
    pass

class State(data_descriptor_Expr): # note: often referred to as "State macro" even though we don't presently say "def State"
    # experimental, 061201/061203; untested;
    # if it works would supercede what's in staterefs.py or whatever (actually Exprs.py for State macro)
    # see also C_rule_for_lval_formula, meant to be used by that old design for the State macro,
    # but this design doesn't anticipate having an "lval formula",
    # but just has an implicit self-relative object and explicit attrname to refer to.
    
    _e_wants_this_descriptor_wrapper = data_descriptor_Expr_descriptor # defined in ExprsMeta, imported from basic
    
    def _e_init(self):
        def myargs(type, dflt = None): # note: these args are exprs, and already went through canon_expr
            dflt = dflt ##e stub; see existing stateref code for likely better version to use here
            ##e do we need to de-expr these args?? (especially type)
            ##e dflt is reasonable to be an expr so we'll eval it each time,
            # but do we need code similar to what's in _i_grabarg to do that properly? guess: yes.
            self._e_type = type
            self._e_default_val = dflt
        myargs(*self._e_args)
        return
    def _e_get_for_our_cls(self, descriptor, instance):
        print "_e_get_for_our_cls",(self, descriptor, instance, )###
        attr = descriptor.attr
        holder = self._e_attrholder(instance, init_attr = attr) # might need attr for initialization using self._e_default_val
        return getattr(holder, attr)
    def _e_set_for_our_cls(self, descriptor, instance, val):
        print "_e_set_for_our_cls",(self, descriptor.attr, instance, val)###
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
                # eval the dflt expr here, mcuh like _i_instance does it:
                val_expr = self._e_default_val
                index = attr
                val = instance._i_eval_dfltval_expr(val_expr, index)
                #k should I just do setattr(res, attr, val), or is there something special and better about this:
                set_default_attrs(res, {attr : val}) ##k arg syntax
                val0 = getattr(res, attr)
                ## assert val is val0,
                if not (val is val0):
                    print "bug: set_default_attrs should have stored %r at %r in %r, but it has %r" % (val, attr, res, val0)
            pass
        return res
    pass # end of class State

# note: an old def of State, never working, from 061117, was removed 061203 from cvs rev 1.88 of Exprs.py

# end
