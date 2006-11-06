'''
Exprs.py -- class Expr, and related subclasses and utilities, other than those involving Instances

$Id$
'''    

# note: this module should not import ExprsMeta, though its InstanceOrExpr subclass needs to (in another module).
# instead, it is probably fully imported by ExprsMeta, and certainly by basic.

#e want __all__? would contain most of it.

# as of 061102 this module is probably reloadable:
##try:
##    _reload_ok
##except:
##    _reload_ok = False # can be redefined at runtime from a debugger, but reload will probably lead to bugs.
##    # this will prevent reload_once from actually reloading it
##else:
##    ###@@@ #k maybe no longer needed soon? [061102]
##    assert _reload_ok, "Exprs module is not allowed to be reloaded, since we test for isinstance(val, Expr) while other modules get imported!"

from basic import printnim, printfyi, stub # this may be a recursive import (with most things in basic not yet defined)
from debug import print_compact_stack

# == utilities #e refile

def map_dictvals(func, dict1):
    """This does to a dict's values what map does to lists --
    i.e. it makes a new dict whose values v are replaced by func(v).
    [If you wish func also depended on k, see map_dictitems.]
    """
    return dict([(k,func(v)) for k,v in dict1.iteritems()])

def map_dictitems(func, dict1):
    """This does to a dict's items what map does to lists --
    i.e. it makes a new dict whose items are f(item) from the old dict's items.
    Func should take 1 argument, a pair (k,v), and return a new pair (k2, v2).
    Often k2 is k, but this is not required.
    If the new items have overlapping keys, the result is... I don't know what. #k
    """
    return dict(map(func, dict1.iteritems()))

# == serial numbers (along with code in Expr.__init__)

_next_e_serno = 1 # incremented after being used in each new Expr instance (whether or not _e_is_instance is true for it)
    ###e should we make it allocated in Expr subclasses too, by ExprsMeta, and unique in them?

def expr_serno(expr):
    """Return the unique serial number of any Expr (except that Expr python subclasses all return 0).
    Non-Exprs all return -1.
    """
    try:
        return expr._e_serno # what if expr is a class? is this 0 for all of those?? yes for now. ###k
    except:
        assert not is_Expr(expr)
        # for now, this happens a lot, since ExprsMeta calls us on non-expr vals such as compute method functions,
        # and even sometimes on ordinary Python constants.
##        printnim("Maybe this never happens -- non-Expr in expr_serno: %r" % (expr,)) ####@@@@ it does...
##            # e.g. for <function _C_delegate at 0xf3f55f0>, or func _C__dict_of_lvals, and maybe a tuple??
##        #e assert(0)??
        return -1
    pass

# == predicates

def is_Expr(expr):
    "is expr an Expr -- meaning, a subclass or instance of class Expr? (Can be true even if it's also considered an Instance.)"
    return hasattr(expr, '_e_serno')

def is_pure_expr(expr):
    "is expr an Expr (py class or py instance), but not an Instance?" 
    return is_Expr(expr) and not expr_is_Instance(expr)

def expr_is_Instance(expr):
    "is an Expr an Instance?"
    res = expr._e_is_instance
    assert res is False or res is True
    return res

def is_Expr_pyinstance(expr):
    """Is expr an Expr python instance (not an Expr subclass)?
    (This is necessary to be sure you can safely call Expr methods on it.) 
    [Use this instead of isinstance(Expr) in case Expr module was reloaded.]
    """
    return is_Expr(expr) and is_Expr(expr.__class__)

# ==

class Expr(object): # subclasses: SymbolicExpr (OpExpr or Symbol), Drawable###obs  ####@@@@ MERGE with InstanceOrExpr, or super it
    """abstract class for symbolic expressions that python parser can build for us,
    from Symbols and operations including x.a and x(a);
    also used as superclass for WidgetExpr helper classes,
    though those don't yet usually require the operation-building facility,
    and I'm not positive that kluge can last forever.
       All Exprs have in common an ability to:
    - replace lexical variables in themselves with other exprs,
    in some cases retaining their link to the more general unreplaced form (so some memo data can be shared through it),
    tracking usage of lexical replacements so a caller can know whether or not the result is specific to a replacement
    or can be shared among all replaced versions of an unreplaced form;
    ###@@@ details?
    - be customized by being "called" on new arg/option lists; ###@@@
    - and (after enough replacement to be fully defined, and after being "placed" in a specific mutable environment)
    to evaluate themselves as formulas, in the current state of their environment,
    tracking usage of env attrs so an external system can know when the return value becomes invalid;
    - 
    """
    _e_args = () # this is a tuple of the expr's args (processed by canon_expr), whenever those args are always all exprs.
    _e_kws = {} # this is a dict of the expr's kw args (processed by canon_expr), whenever all kwargs are exprs.
        # note: all Expr subclasses should store either all or none of their necessary data for copy in _e_args and _e_kws,
        # or they should override methods including copy(?) and replace(?) which make that assumption. ##k [061103]
    _e_is_instance = False # override in certain subclasses or instances ###IMPLEM
    _e_serno = 0 ###k guess; since Expr subclasses count as exprs, they all have a serno of 0 (I hope this is ok)
    _e_has_args = False # subclass __init__ or other methods must set this True when it's correct... ###nim, not sure well-defined
        # (though it might be definable as whether any __init__ or __call__ had nonempty args or empty kws)
        # (but bare symbols don't need args so they should have this True as well, similar for OpExpr -- all NIM)
        # see also InstanceOrExpr .has_args -- if this survives, that should be renamed so it's the same thing [done now, 061102]
        # (the original use for this, val_is_special, doesn't need it -- the check for _self is enough) [061027]
    def __init__(self, *args, **kws):
        assert 0, "subclass %r of Expr must implement __init__" % self.__class__.__name__
    def _init_e_serno_(self):
        """[private -- all subclasses must call this; the error of not doing so is not directly detected --
         but if they call canon_expr on their args, they should call this AFTER that, so self._e_serno
         will be higher than that of self's args! This may not be required for ExprsMeta sorting to work,
         but we want it to be true anyway, and I'm not 100% sure it's not required. (Tentative proof that it's not required:
         if you ignore serno of whatever canon_expr makes, prob only constant_Expr, then whole serno > part serno anyway.)]
        Assign a unique serial number, in order of construction of any Expr.
        FYI: This is used to sort exprs in ExprsMeta, and it's essential that the order
        matches that of the Expr constructors in the source code of the classes created by ExprsMeta
        (for reasons explained therein, near its expr_serno calls).
        """
        #e Probably this should be called by __init__ and our subclasses should call that,
        # but the above assert is useful in some form.
        # Note that this needn't be called by __call__ in InstanceOrExpr,
        # but only because that ends up calling __init__ on the new expr anyway.
        global _next_e_serno
        self._e_serno = _next_e_serno
        _next_e_serno += 1
        if 'debug' and self._e_serno == 149: #k hope not too early for %r to work
            print_compact_stack("just made expr 149, %r, at: " % self)
        return
    def __call__(self, *args, **kws):
        assert 0, "subclass %r of Expr must implement __call__" % self.__class__.__name__

    def __get__(self, obj, cls):
        """The presence of this method makes every Expr a Python descriptor. This is so an expr which is a formula in _self
        can be assigned to cls._C_attr for some attr (assuming cls inherits from InvalidatableAttrsMixin),
        and will be used as a "compute method" to evaluate obj.attr. The default implementation creates some sort of Lval object
        with its own inval flag and subscriptions, but sharing the _self-formula, which recomputes by evaluating the formula
        with _self representing obj.
        """
        ''' more on the implem:
        It stores this Lval object in obj.__dict__[attr], finding attr by scanning cls.__dict__
        the first time. (If it finds itself at more than one attr, this needs to work! Is that possible? Yes -- replace each
        ref to the formula by a copy which knows attr... but maybe that has to be done when class is created?
        Easiest way is first-use-of-class-detection in the default implem. (Metaclass is harder, for a mixin being who needs it.)
         Ah, easier way: just store descriptors on the real attrs that know what to do... as we're in the middle of doing
        in the code that runs when we didn't, namely _C_rule or _CV_rule. ###)
        '''
        if obj is None:
            return self
        #e following error message text needs clarification -- when it comes out of the blue it's hard to understand
        print "__get__ is nim in the Expr", self, ", which is assigned to some attr in", obj ####@@@@ NIM; see above for how [061023 or 24]
        print "this formula needed wrapping by ExprsMeta to become a compute rule..." ####@@@@
        return
    def _e_compute_method(self, instance):
        "Return a compute method version of this formula, which will use instance as the value of _self."
        #####@@@@@ WRONG API in a few ways: name, scope of behavior, need for env in _e_eval, lack of replacement due to env w/in self.
        ##return lambda self = self: self._e_eval( _self = instance) #e assert no args received by this lambda?
        # TypeError: _e_eval() got an unexpected keyword argument '_self'
        ####@@@@ 061026 have to decide: are OpExprs mixed with ordinary exprs? even instances? do they need env, or just _self?
        # what about ipath? if embedded instances, does that force whole thing to be instantiated? (or no need?)
        # wait, embedded instances cuold not even be produced w/o whole ting instantiating... so i mean,
        # embedded things that *need to* instantiate. I guess we need to mark exprs re that...
        # (this might prevent need for ipath here, if pure opexprs can't need that path)
        # if so, who scans the expr to see if it's pure (no need for ipath or full env)? does expr track this as we build it?

        # try 2 061027 late:
        assert instance._e_is_instance, "compute method asked for on non-Instance %r" % (instance,) # happens if a kid is non-instantiated(?)
        env0 = instance.env # fyi: AttributeError for a pure expr (ie a non-instance)
        env = env0.with_literal_lexmods(_self = instance)
        ipath0 = instance.ipath ####k not yet defined i bet... funny, it didn't seem to crash from this -- did i really test it??
        index = 'stub' ###should be the attr of self we're coming from, i think!
        printnim("_e_compute_method needs to be passed an index")
        ipath = (index, ipath0)
        return lambda self=self, env=env, ipath=ipath: self._e_eval( env, ipath ) #e assert no args received by this lambda?
    def __repr__(self): # class Expr
        "[often overridden by subclasses; __str__ can depend on __repr__ but not vice versa(?) (as python itself does by default(??))]"
        ## return str(self) #k can this cause infrecur?? yes, at least for testexpr_1 (a Rect) on 061016
        ## return "<%s at %#x: str = %r>" % (self.__class__.__name__, id(self), self.__str__())
        return "<%s#%d at %#x>" % (self.__class__.__name__, self._e_serno, id(self))
##    def __str__(self):
##        return "??"
    # ==
    def __rmul__( self, lhs ):
        """operator b * a"""
        return mul_Expr(lhs, self)
    def __mul__( self, rhs ):
        """operator a * b"""
        return mul_Expr(self, rhs)
    def __rdiv__( self, lhs ):
        """operator b / a"""
        return div_Expr(lhs, self)
    def __div__( self, rhs ):
        """operator a / b"""
        return div_Expr(self, rhs)
    def __radd__( self, lhs ):
        """operator b + a"""
        return add_Expr(lhs, self)
    def __add__( self, rhs ):
        """operator a + b"""
        return add_Expr(self, rhs)
    def __rsub__( self, lhs ):
        """operator b - a"""
        return sub_Expr(lhs, self)
    def __sub__( self, rhs ):
        """operator a - b"""
        return sub_Expr(self, rhs)
    def __neg__( self):
        """operator -a"""
        return neg_Expr(self)
    # == not sure where these end up
    def __float__( self):
        """operator float(a)"""
        print "kluge: float(expr) -> 17.0"####@@@@ need float_Expr
        return 17.0
    def _e_replace(self, reps):
        "perform replacements (reps) in self, and return the result [same as self if possible?] [some subclasses override this]"
        # for most kinds of exprs, just replace in the args, and in the option values [####@@@@ NIM].
        assert 0, "###@@@ is _e_replace ever called? it might be obs"# [061103 comment]
        printnim("_e_replace is nim for option vals")
        args = self._e_args
        modargs = tuple(map(reps, args)) ##k reps is callable??
        if args == modargs:
            ##k requires fast == on Expr, which unlike other ops is not meant as a formula
            # (could it be a formula, but with a boolean value too, stored independently???)
            return self
        return self.__class__(*modargs)
    def _e_replace_using_subexpr_filter(self, func): #e rename, since more like map than filter; subexpr_mapper??
        if not isinstance(self, (OpExpr, constant_Expr)):#k syntax
            printfyi("_e_replace_using_subexpr_filter called on class %s" % self.__class__.__name__)
                 ####k ever on an InstanceOrExpr?? might be wrong then, just as _e_eval should not go inside -- not sure!
                 # more likely, it needs to go in but in a lexcontext-modified way! [061105 guess] ###@@@
        args = self._e_args
        kws = self._e_kws
        if not args and not kws: ###k this will break until all exprs define these... put dflt defs in Expr??
            return self # optim
        modargs = tuple(map(func, args))
        modkws = map_dictvals(func, kws)
        if modargs == args and modkws == kws:
            return self # helps prevent memory leaks (by avoiding needless reconstruction of equal exprs); might help serno too??
        printnim("replace would be wrong for an expr with subexprs but also other data -- do we have any such? ##k")##k
        return self.__class__(*modargs, **modkws)
    def _e_free_in(self, sym): #e name is confusing, sounds like "free of" which is the opposite -- rename to "contains_free"??
        """Return True if self contains sym (Symbol or its name) as a free variable, in some arg or option value.
        [some subclasses override this]
        """
        try:
            _e_args = self._e_args
            #k not sure this is defined in all exprs! indeed, not in a Widget2D python instance... ####@@@@
        except AttributeError:
            #####@@@@ warning: following is slow, even when it doesn't print -- NEEDS OPTIM ####@@@@
            from basic import printonce
            printonce("debug note: _e_free_in is False since no _e_args attr in %r" % self) # print once per self
            return False ###k guess -- correct? #####@@@@@
        for arg in _e_args: 
            if arg._e_free_in(sym):
                return True
        printnim("_e_free_in is nim for option vals")###@@@
        return False
    pass

class SymbolicExpr(Expr): # Symbol or OpExpr
    def __call__(self, *args, **kws):
        # print '__call__ of %r with:' % self,args,kws###@@@
        return call_Expr(self, *args, **kws)
    def __getattr__(self, attr):
        if attr.startswith('__'):
            # be very fast at not finding special python attrs like __repr__
            raise AttributeError, attr
        if attr.startswith('_e_') or attr.startswith('_i_'):
            # We won't pretend to find Expr methods/attrs starting _e_ (also used in Instances),
            # or Instance ones starting _i_ -- but do reveal which class we didn't find them in.
            raise AttributeError, "no attr %r in %r" % (attr, self.__class__) #e safe_repr for class
        if 1 and attr.startswith('_i_'): ###e slow, remove when devel is done
            printnim("slow, remove when devel is done: _i_ noninstance check")
            assert self._e_is_instance #k not positive this is ok, we'll see [061105]
        return getattr_Expr(self, attr)
    pass

class OpExpr(SymbolicExpr):
    "Any expression formed by an operation (treated symbolically) between exprs, or exprs and constants"
    def __init__(self, *args):
        self._e_args = tuple(map(canon_expr, args)) # tuple is required, so _e_args works directly for a format string of same length
        self._init_e_serno_() # call this AFTER canon_expr (for sake of _e_serno order)
        self._e_init()
    def _e_init(self):
        assert 0, "subclass of OpExpr must implement this"
    def __repr__(self): # class OpExpr
        return "<%s#%d: %r>"% (self.__class__.__name__, self._e_serno, self._e_args,)
    def _e_argval(self, i, env,ipath):
        """Under the same assumptions as _e_eval (see its docstring),
        compute and return the current value of an implicit kid-instance made from self._e_args[i], at relative index i,
        doing usage-tracking into caller (i.e. doing no memoization or caching of our own).
        """
         ##e consider swapping argorder to 0,ipath,env or (0,ipath),env
        return self._e_args[i]._e_eval(env, (i,ipath))
    def _e_kwval(self, k, env,ipath):
        "Like _e_argval, but return the current value of our implicit-kid-instance of self._e_kws[k], rel index k."
        return self._e_kws[k]._e_eval(env, (k,ipath))
    def _e_eval(self, env,ipath):
        """Considering ourself implicitly instantiated by the replacements (especially _self_) in env,
        or more precisely, instantiated as a formula residing in env's _self, after replacement by env's other replacements,
        with that implicit instance using the index-path given as ipath
        (and perhaps finding explicit sub-instances using that ipath, if we ever need those),
        compute and return our current value,
        doing usage-tracking into caller (i.e. doing no memoization or caching of our own).
           Note that an expr's current value might be any Python object;
        if it happens to be an Instance or Expr or special symbol,
        we should not notice that or do any special cases based on that
        (otherwise we'll cause bugs for uses of _e_eval on internal formulas like the ones made by the Arg macro).
           Most subclasses can use this implem, by defining an _e_eval_function which is applied to their arg values.
        If they have other data, or even kws, and/or if they don't want to always evaluate all args (like If or an InstanceOrExpr),
        they should redefine this method. [We're not presently in InstanceOrExpr at all, but that might change,
        though this implem won't work there since those want to never eval their args now. 061105]
        """
        assert not self._e_kws #e remove when done with devel -- just checks that certain subclasses overrode us -- or, generalize this
        debug = False
        if debug:
            print "eval %r" % self
        res = apply(self._e_eval_function, [self._e_argval(i,env,ipath) for i in range(len(self._e_args))])
        if debug:
            print "res = %r" % (res,) # could be anything
        return res
    pass # end of class OpExpr

class call_Expr(OpExpr): # note: superclass is OpExpr, not SymbolicExpr, even though it can be produced by SymbolicExpr.__call__
    def __init__(self, callee, *callargs, **kws):
        # need to extend OpExpr.__init__ so we can have kws, and canon them
        self._e_kws = map_dictvals(canon_expr, kws) ###e optim: precede by "kws and"
        OpExpr.__init__(self, callee, *callargs) # call this AFTER you call canon_expr above (for sake of _e_serno order)
    def _e_init(self):
        ## obs: assert len(self._e_args) == 3
        ## obs: self._e_callee, self._e_call_args, self._e_call_kws = self._e_args
        self._e_callee = self._e_args[0]
        self._e_call_args = self._e_args[1:]
        self._e_call_kws = self._e_kws #e could use cleanup below to not need this alias
        #e might be useful to record line number, at least for some heads like NamedLambda; see Symbol compact_stack call for how
    def __str__(self):
        if self._e_call_kws:
            return "%s(*%r, **%r)" % (self._e_callee, self._e_call_args, self._e_call_kws) #e need parens?
        elif self._e_call_args:
            return "%s%r" % (self._e_callee, self._e_call_args)
        else:
            return "%s%r" % (self._e_callee, self._e_call_args) # works the same i hope
    def _e_eval(self, env, ipath):
        """[the only reason the super method is not good enough is that we have _e_kws too, I think;
            maybe also the distinction of that to self._e_call_kws, but I doubt that distinction is needed -- 061105]
        """
        # 061102: we do this (_e_eval in general)
        # by imagining we've done the replacements in env (e.g. for _self) to get an instance of the expr,
        # and then using ordinary eval rules on that, which include forwarding to _value for some Instances,
        # but typically result is an Instance or a python data object.
        # So, just eval it as a call, I think.
        argvals = [self._e_argval(i,env,ipath) for i in range(len(self._e_args))] # includes value of callee as argvals[0]
        # the following assumes _e_call_kws is a subset of (or the same as) _e_kws (with its items using the same keys).
        kwvals = map_dictitems( lambda (k,v): (k,self._e_kwval(k,env,ipath)), self._e_call_kws )
        printnim('###e optim: precede by "self._e_call_kws and"') # in 2 places
        return argvals[0] ( *argvals[1:], **kwvals )
    pass

class getattr_Expr(OpExpr):
    def __call__(self, *args, **kws):
        print '__call__ of %r with:' % self,args,kws###@@@
        assert 0, "getattr exprs are not callable [ok??]"
    def _e_init(self):
        assert len(self._e_args) == 2 #e kind of useless and slow #e should also check types?
        attr = self._e_args[1]
        assert attr #e and assert that it's a python identifier string? Note, it's actually a constant_Expr containing a string!
            # And in theory it's allowed to be some other expr which evals to a string,
            # though I don't know if we ever call it that way
            # (and we might want to represent or print it more compactly when we don't).
    def __str__(self):
         return "%s.%s" % self._e_args #e need parens? need quoting of 2nd arg? Need to not say '.' if 2nd arg not a py-ident string?
    _e_eval_function = getattr
    pass

class mul_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s * %s" % self._e_args #e need parens?
    _e_eval_function = lambda x,y:x*y # does this have a builtin name? see operators module ###k
    pass

class div_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s / %s" % self._e_args #e need parens?
    _e_eval_function = lambda x,y:x/y 
    pass

class add_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s + %s" % self._e_args #e need parens?
    _e_eval_function = lambda x,y:x+y 
##    # maybe, 061016: ####@@@@ [current issues: args to _e_make_in, for normals & Ops; symbol lookup; when shared exprs ref same instance]
##    def _C_value(self):
##        return self.kids[0].value + self.kids[1].value
    def _make_in_WRONG(self, place, ipath): #### WRONG (see below), really more like _init_instance, called by common _destructive_make_in
        ###WRONG args (maybe -- place -> env??), and defined in wrong class (common to all OpExprs or exprs with fixed kids arrays),
        ###and attrs used here (kids, args, maybe even _e_is_instance) might need _e_ (??),
        ### and maybe OpExprs never need ipath or place, just env
        ###    (for symbol lookup when they include symbols? or did replacement already happen to make self understood??)
        ### and WORST OF ALL, it's actually a destructive make -- maybe it's _init_instance, called by common _destructive_make_in .
        assert not self._e_is_instance ###@@@ need to be in InstanceOrExpr superclass for this [obs cmt??061102]
        # following says place._make_in but probably means env.make! [061020 guess]
        ##self.kids = map(place._make_in, self.args.items()) # hmm, items have index->expr already -- but this leaves out ipath
        args = self._e_args
        self.kids = [place._make_in(args[i], [i, ipath]) for i in range(len(args))]
            # note (proposed): [i, ipath] is an inlined sub_index(i,ipath); [] leaves room for intern = append
    pass

class sub_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s - %s" % self._e_args #e need parens?
    _e_eval_function = lambda x,y:x-y 
    pass

class neg_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 1
    def __str__(self):
        return "- %s" % self._e_args #e need parens?
    _e_eval_function = lambda x:-x 
    pass

class list_Expr(OpExpr): #k not well reviewed, re how it should be used, esp. in 0-arg case
    #aka ListExpr, but we want it not uppercase by convention for most OpExprs
    def _e_init(self):
        pass
    def __str__(self):
        return "%s" % (list(self._e_args),) #e need parens?
    _e_eval_function = lambda *args:list(args) #k syntax?
    pass

class tuple_Expr(OpExpr): #k not well reviewed, re how it should be used, esp. in 0-arg case
    def _e_init(self):
        pass
    def __str__(self):
        return "%s" % (tuple(self._e_args),) #e need parens?
    _e_eval_function = lambda *args:tuple(args) #k syntax? ###e optim: args are probably already a tuple
    pass

class If_expr(OpExpr): # so we can use If in formulas
    pass
# see also class If_ in testdraw.py
## def If(): pass

class internal_Expr(Expr):
    "Abstract class for various kinds of low-level exprs for internal use that have no visible subexprs."
    def __init__(self, *args, **kws):
        """store args & kws but don't canon_expr them -- assume they are not necessarily exprs
        (and even if they are, that they should be treated inertly)
        """
        self.args = args # not sure if the non-_e_ name is ok... if not, try _e_data_args or so? ###k
        self.kws = kws
        self._internal_Expr_init() # subclasses should override this method to do their init
        self._init_e_serno_()
        return
    def _internal_Expr_init(self):
        assert 0, "subclass must implem"
    pass
    
class constant_Expr(internal_Expr):
    ###k super may not be quite right -- we want some things in it, like isinstance Expr, but not the __add__ defs [not sure, actually]
    def _internal_Expr_init(self):
        (self._e_constant_value,) = self.args
    def __repr__(self): # class constant_Expr
        return "<%s#%d: %r>"% (self.__class__.__name__, self._e_serno, self._e_constant_value,)
    def __str__(self):
        return "%r" % (self._e_constant_value,) #e need parens?
            #k 061105 changed %s to %r w/o reviewing calls (guess: only affects debugging)
    def _e_eval(self, env, ipath):
        if '061103 kluge2':
            maybe = env.lexval_of_symbol(_self) #e suppress the print from this
            instantiating = (maybe is not _self)
            assert instantiating, "no _self rep in _e_eval of %r" % self # turns out _e_eval always has to implicitly instantiate [061105]
        if instantiating:
            res = self._e_constant_value
        else:
            assert 0
            ## this can be what _e_simplify does, when we have that (for constant-folding an related optims)
            res = self
        if 0 and self._e_constant_value == 10: # if 0 since that 'dflt 10' bug is finally fixed, 061105
            # keep this for now, since i still don't know where 10 came from -- maybe someone called eval that shouldn't have? [061105]
            print_compact_stack("is this eval of %r to %r (instantiating = %r) justified? : " % (self, res, instantiating) )
                ####@@@@ 061103 9pm i suspect it wasn't when we still went to 10 even though not instantiating,
                # at least when used to grab an expr by _i_grabarg to pass to _i_instance. [where i am]
                # I think it's the confusing two-kinds-of-eval -- if this was "eval an instance of this at this _self" it would be ok.
                # So the above kluge might fix this, and if it does we'll have to support make_in here I guess.
                # but that might be an issue... where do we put what we make? well, nowhere, we just return it as 10. ###e
                # PROBLEM: everytime i hit this it's from Rect line 66 with instantiating = True... so I don't yet see
                # how the existing code is calling it this way -- why is grabarg using a compute method at all?
                # Is it somehow happening right inside the CV thing? I guess so... why?!?
        return res
    def _e_make_in(self, env, ipath): ###e equiv to _e_eval? see comment in _CV__i_instance_CVdict [061105]
        "Instantiate self in env, at the given index-path."
        #e also a method of InstanceOrExpr, guess we'll add to OpExpr and maybe more, not yet in Expr tho, not sure needed in all exprs
        return self._e_constant_value # thought to be completely correct, 061105
    pass

class debug_evals_of_Expr(internal_Expr):#061105, not normally used except for debugging
    "wrap a subexpr with me in order to get its evals printed (by print_compact_stack), with (I hope) no other effect"
    def _internal_Expr_init(self):
        ## (self._e_the_expr,) = self.args
        self._e_args = self.args # so replace sees the args
        assert len(self.args) == 1
    def _e_eval(self, env, ipath):
        the_expr = self._e_args[0] ## self._e_the_expr
        res = the_expr._e_eval(env, ipath)
        print_compact_stack("debug_evals_of_Expr(%r) evals it to %r at: " % (the_expr, res)) #k does this ever happen?
        return res
    pass
    
def canon_expr(subexpr):###CALL ME FROM MORE PLACES -- a comment in Column.py says that env.understand_expr should call this...
    "Make subexpr an Expr, if it's not already. (In future, we might also intern it.)"
    if is_Expr(subexpr):
        return subexpr # true for Instances too -- ok??
##    ## elif issubclass(subexpr, Expr): # TypeError: issubclass() arg 1 must be a class
##    elif isinstance(subexpr, type) and issubclass(subexpr, Expr):
##        return subexpr # for _TYPE_xxx = Widget2D, etc -- is it ever not ok? ####k
    elif isinstance(subexpr, type([])):
        return list_Expr(*subexpr) ###k is this always correct? or only in certain contexts??
            # could be always ok if list_Expr is smart enough to revert back to a list sometimes.
        #e analogous things for tuple and/or dict? not sure. or for other classes which mark themselves somehow??
    else:
        #e assert it's not various common errors, like expr classes or not-properly-reloaded exprs
        #e more checks?
        # assume it's a python constant
        #e later add checks for its type, sort of like we'd use in same_vals or so... in fact, how about this?
        from state_utils import same_vals
        assert same_vals(subexpr, subexpr)
        return constant_Expr(subexpr)
    pass

# ==

class Symbol(SymbolicExpr):
    "A kind of Expr that is just a symbol with a given name. Often used via the __Symbols__ module."
    def __init__(self, name = None):
        self._init_e_serno_()
        if name is None:
            name = "?%s" % compact_stack(skip_innermost_n = 3).split()[-1] # kluge - show line where it's defined
        self._e_name = name
        return
    def __str__(self):
        return self._e_name
    def __repr__(self):
        ## return 'Symbol(%r)' % self._e_name
        ##e should only use following form when name looks like a Python identifier!
        return 'S.%s' % self._e_name
    def __eq__(self, other): #k probably not needed, since symbols are interned as they're made
        return self.__class__ is other.__class__ and self._e_name == other._e_name
    def __ne__(self, other):
        return not (self == other)
    def _e_eval(self, env, ipath):
        """As with super _e_eval, our job is:
        Imagine that env's replacements should be done in self,
        and that the resulting modified self should be instantiated within the object which is env's replacement for _self.
        Then evaluate the result at the current time.
           For self a symbol other than _self, that just means, do the replacement, worrying about symbols inside that value
        (in terms of repeated replacement if any), then evaluate the result. I am not sure what context the replacements are in,
        whether this can ever be used to create an expr result, whether _self is a special case, etc, so for now,
        print warnings (or maybe asfail) if any of those cases arise.
           For self the symbol _self, this happens all the time with env's value for _self being an instance,
        and what we want to return is that very instance. This may mean that technically env's value should be a constant expr
        which we should eval here, *or* that we should have a special case for _self here, *or* that we should never be
        recursively evaluating replacements here. For now, I'll handle this by not recursively evaluating,
        warning if _self doesn't get an Instance, and warning if self is not _self. [061105]
        """
        #pre-061105 comments, probably obs & wrong:
        ## print "how do we eval a symbol? some sort of env lookup ..."
        #[later 061027: if lookup gets instance, do we need ipath? does instance have it already? (not same one, for sure -- this is
        # like replacement). If lookup gets expr, do we instantiate it here? For now, just make _self work -- pretend expr was already
        # instantiated and in the place of _self it had an instance. So, when we hit an instance with _e_eval, what happens?
        # If we believe that getattr_Expr, it returns a value which is "self" which is exactly the same instance --
        # i.e. Thing instance evals to itself. This is not like OpExpr instance which evals to a value. I suppose If also evals
        # to not itself.... this is related to what CLE wanted to do, which is eval something to a "fixed instance" -- let's review
        # the API it proposed to use for calling that utility.... that's in GlueCodeMemoizer, it does instance.eval() but I knew it
        # might be misnamed, but I did think no point in passing it args (instance already knows them). I know some instances define
        # _value (like Boxed), maybe .eval() would go into it... probably it would. BTW, What if ._value is an expr (not Instance)?
        # What if we call it _e_value and it's defined on some expr?? ####@@@@
        # Summary guess: look up sym, then eval result with same args. If instance, they have a method which looks for _value,
        # defaults to self. This method might be _e_eval itself... or have some other name.]
        #older comments:
        ## -- in the object (env i guess) or lexenv(?? or is that replacement??) which is which?
        # maybe: replacement is for making things to instantiate (uses widget expr lexenv), eval is for using them (uses env & state)
        # env (drawing_env) will let us grab attrs/opts in object, or things from dynenv as passed to any lexcontaining expr, i think...
        val = env.lexval_of_symbol(self) # note: cares mainly or only about self._e_name; renamed _e_eval_symbol -> lexval_of_symbol
            # but I'm not sure it's really more lexenv than dynenv, at least as seen w/in env... [061028] ####@@@@
        # val is an intermediate value, needs further eval [this old comment might be wrong; see docstring -- 061105]
        if self == val:
            if self is not val:
                print "warning: %r and %r are two different Symbols with same name, thus equal" % (self,val)
            print "warning: Symbol(%r) evals to itself" % self._e_name
            return self
        if self._e_name != '_self':
            print "warning: _e_eval of a symbol other than _self is not well-reviewed or yet well-understood"
                # e.g. what should be in env? what if it's an expr with free vars incl _self -- are they in proper context?
                # see docstring for more info [061105]
        ## pre-061105 code did: return val._e_eval(env, ipath)
        # and that might be needed for other syms -- not sure yet [061105]
        return val
    def _e_free_in(self, sym):
        """General case: Return True if Expr self contains sym (Symbol or its name) as a free variable, in some arg or option value.
        For this class Symbol, that means: Return True if sym is self or self's name.
        [overrides super version]
        """
        return (sym is self) or (sym == self._e_name)
    pass

# ==

##_self = Symbol('_self') # is it ok if this is done more than once, or does only the __Symbols__ module cache them??
##
### does this work? at least no exception from it -- good, but why not? ###k
##_self.attr1.attr2
##
####_self2 = Symbol('_self')
####assert _self2 is _self # i bet this will fail; if so, just import __Symbols__ right here [but make it work someday ##e]
##
##del _self

# Symbols for public & private use
from __Symbols__ import _self
from __Symbols__ import _E_ATTR, _E_REQUIRED_ARG_, _E_DFLT_FROM_TYPE_
    # this imports this Exprs module recursively, but requires nothing below this point in this module, so it should be ok

# some essential macros: Instance, Arg, Option, ArgOrOption

def Instance(expr, _index_expr = _E_ATTR):
    """Assuming the arg is an expr (not yet checked?), turn into the expr _self._i_instance(expr, _E_ATTR),
    which is free in the symbols _self and _E_ATTR. [#e _E_ATTR might be changed to _E_INDEX, or otherwise revised.]
    """
    printnim("review: same index is used for a public Option and a private Instance on an attr; maybe ok if no overlap possible???")##e
    global _self # not needed, just fyi
    return call_Expr( getattr_Expr(_self, '_i_instance'), expr, _index_expr)

_arg_order_counter = 0

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
    dflt_expr ###doc, can also be _E_DFLT_FROM_TYPE_ or _E_REQUIRED_ARG_;
        will be asserted not None (kluge, since canon_expr could accept None), then passed through canon_expr
    """
    global _self # fyi
    type_expr = canon_type( type_expr)
    if dflt_expr is _E_DFLT_FROM_TYPE_:
        dflt_expr = default_expr_from_type_expr( type_expr)
        assert is_pure_expr(dflt_expr) #k guess 061105
    else:
        assert dflt_expr is not None # see docstring
        dflt_expr = canon_expr(dflt_expr) # hopefully this finally will fix dflt 10 bug, 061105 guesshope ###k
        assert is_pure_expr(dflt_expr) # not sure this is redundant, since not sure if canon_expr checks for Instance ###k
        printnim("not sure if canon_expr checks for Instance")
    # Note: we have to use explicit call_Expr & getattr_Expr below, to construct Exprs like _self._i_grabarg( attr_expr, ...),
    # only to work around safety features which normally detect that kind of Expr-formation (getattr on _i_* or _e_*,
    # or getattr then call) as a likely error. These safety features are very important, catching errors that would often lead
    # to hard-to-diagnose bugs (when our code has an Expr but thinks it has an Instance), so it's worth the trouble.
    held_dflt_expr = constant_Expr(dflt_expr) # 061105 bugfix (not merely an optim as some recent comments seemed to think)
        # Note, this gets evalled back into dflt_expr (treated as inert, may or may not be an expr depending on what it is right here)
        # by the time _i_grabarg sees it (the eval is done when the call_Expr evals its args before doing the call).
        # So if we wanted _i_grabarg to want None rather than _E_REQUIRED_ARG_ as a special case, we could change to that (there & here).
    if 0 and "debug that 'dflt 10' bug":
        ## print("using debug_evals_of_Expr on held_dflt_expr %r, will it work?" % held_dflt_expr)#####@@@@@
        held_dflt_expr = debug_evals_of_Expr(held_dflt_expr)
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
    #### obs: index_expr   = call_Expr( getattr_Expr(_self, '_i_grabarg_index'), attr_expr, argpos_expr )
    return Instance( type_expr( grabarg_expr), _index_expr = index_expr )

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
        return constant_Expr(pos) # this gets included in the scanner's processed expr
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
    "#doc; index contains both attr and argpos; error to use plain Arg after this in same class (maybe not detected)"
    global _E_ATTR # fyi
    attr_expr = _E_ATTR
    return Arg( type_expr, dflt_expr, _attr_expr = attr_expr)

def canon_type(type_expr):###stub
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
##    return type_expr #stub; needs to work for builtin types like int, or helper classes that are types like Widget (or Rect??)
##    # note that the retval will get called to build an expr, thus needs to be in SymbolicExpr -- will that be true of eg CLE?
##    # if not, then some InstanceOrExpr objs need __call__ too, or constructor needs to return a SymbolicExpr, or so.

default_expr_from_type_expr = stub ###IMPLEM

# end

