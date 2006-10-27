'''
Exprs.py

$Id$
'''    

try:
    _reload_ok
except:
    _reload_ok = False # can be redefined at runtime from a debugger, but reload will probably lead to bugs.
    # this will prevent reload_once from actually reloading it ###IMPLEM
else:
    assert _reload_ok, "Exprs module is not allowed to be reloaded, since we test for isinstance(val, Expr) while other modules get imported!"
    
# kluge to avoid recursive import problem (done in modules which are imported by basic -- is this one?? maybe import basic ok??):
def printnim(*args):
    import basic
    basic.printnim(*args)
    return

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
    _e_has_args = False # subclass __init__ or other methods must set this True when it's correct... ###nim, not sure well-defined
        # (though it might be definable as whether any __init__ or __call__ had nonempty args or empty kws)
        # (but bare symbols don't need args so they would have this True as well)
        # see also InstanceOrExpr .has_args -- if this survives, that should be renamed so it's the same thing
        # (the original use for this, val_is_special, doesn't need it -- the check for _self is enough) [061027]
    def __init__(self, *args, **kws):
        assert 0, "subclass %r of Expr must implement __init__" % self.__class__.__name__
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
        print "__get__ is nim in the Expr", self, ", which is assigned to some attr in", obj ####@@@@ NIM; see above for how [061023 or 24]
        print "this formula needed wrapping by ExprsMeta to become a compute rule..." ####@@@@
        return
    def _e_compute_method(self, instance):
        "Return a compute method version of this formula, which will use instance as the value of _self."
        #####@@@@@ WRONG API in a few ways: name, scope of behavior, need for env in _e_eval, lack of replacement due to env w/in self.
        return lambda self = self: self._e_eval( _self = instance) #e assert no args received by this lambda?
        # TypeError: _e_eval() got an unexpected keyword argument '_self'
        ####@@@@ 061026 have to decide: are OpExprs mixed with ordinary exprs? even instances? do they need env, or just _self?
        # what about ipath? if embedded instances, does that force whole thing to be instantiated? (or no need?)
        # wait, embedded instances cuold not even be produced w/o whole ting instantiating... so i mean,
        # embedded things that *need to* instantiate. I guess we need to mark exprs re that...
        # (this might prevent need for ipath here, if pure opexprs can't need that path)
        # if so, who scans the expr to see if it's pure (no need for ipath or full env)? does expr track this as we build it?
    def __repr__(self):
        ## return str(self) #k can this cause infrecur?? yes, at least for testexpr_1 (a Rect) on 061016
        return "<%s at %#x: str = %r>" % (self.__class__.__name__, id(self), self.__str__())
    def __str__(self):
        return "??"
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
        printnim("_e_replace is nim for option vals")###@@@
        args = self._e_args
        modargs = tuple(map(reps, args)) ##k reps is callable??
        if args == modargs:
            ##k requires fast == on Expr, which unlike other ops is not meant as a formula
            # (could it be a formula, but with a boolean value too, stored independently???)
            return self
        return self.__class__(*modargs)
    def _e_free_in(self, sym): #e name is confusing, sounds like "free of" which is the opposite -- rename to "contains_free"??
        """Return True if self contains sym (Symbol or its name) as a free variable, in some arg or option value.
        [some subclasses override this]
        """
        try:
            _e_args = self._e_args
            #k not sure this is defined in all exprs! indeed, not in a Widget2D python instance... ####@@@@
        except AttributeError:
            ## warning: following is slow, even when it doesn't print -- needs optim ####@@@@
            from basic import printonce
            printonce("debug note: _e_free_in False since no _e_args in %r" % self) # print once per self
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
        return call_Expr(self, args, kws)
    def __getattr__(self, attr):###
        if attr.startswith('__') or attr.startswith('_e_'):
            raise AttributeError, attr 
        return getattr_Expr(self, attr)
    pass

class OpExpr(SymbolicExpr):
    "Any expression formed by an operation (treated symbolically) between exprs, or exprs and constants"
    def __init__(self, *args):
        self._e_args = map(canon_expr, args)
        self._e_init()
    def _e_init(self):
        assert 0, "subclass of OpExpr must implement this"
    pass

class call_Expr(OpExpr): # note: superclass is OpExpr, not SymbolicExpr, even though it can be produced by SymbolicExpr.__call__
    def _e_init(self):
        assert len(self._e_args) == 3
        self._e_callee, self._e_call_args, self._e_call_kws = self._e_args
        #e might be useful to record line number, at least for some heads like NamedLambda; see Symbol compact_stack call for how
    def __str__(self):
        if self._e_call_kws:
            return "%s(*%r, **%r)" % self._e_args #e need parens?
        elif self._e_call_args:
            return "%s%r" % (self._e_callee, self._e_call_args)
        else:
            return "%s%r" % (self._e_callee, self._e_call_args) # works the same i hope
    def _e_eval(self, env):
        print "how do we eval a call? as a call, or by looking up a rule?"###e
    pass

class getattr_Expr(OpExpr):
    def __call__(self, *args, **kws):
        print '__call__ of %r with:' % self,args,kws###@@@
        assert 0, "getattr exprs are not callable [ok??]"
    def _e_init(self):
        assert len(self._e_args) == 2 #e kind of useless and slow #e should also check types?
    def __str__(self):
        return str(self._e_args[0]) + '.' + self._e_args[1] #e need parens?
    def _e_eval(self, env):
        return getattr(env._e_eval_expr(self._e_args[0]), env._e_eval_expr(self._e_args[1])) ###k correct, or do usage tracking? probably correct, obj does tracking...
    pass

class mul_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s * %s" % self._e_args #e need parens?
    def _e_eval(self, env):
        return env._e_eval_expr(self._e_args[0]) * env._e_eval_expr(self._e_args[1])
    pass

class div_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s / %s" % self._e_args #e need parens?
    pass

class add_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s + %s" % self._e_args #e need parens?
    def _e_eval(self, env):
        return env._e_eval_expr(self._e_args[0]) + env._e_eval_expr(self._e_args[1])
    # maybe, 061016: ####@@@@ [current issues: args to _make_in, for normals & Ops; symbol lookup; when shared exprs ref same instance]
    def _C_value(self):
        return self.kids[0].value + self.kids[1].value
    def _make_in(self, place, ipath): #### WRONG (see below), really more like _init_instance, called by common _destructive_make_in
        ###WRONG args (maybe -- place -> env??), and defined in wrong class (common to all OpExprs or exprs with fixed kids arrays),
        ###and attrs used here (kids, args, maybe even is_instance) might need _e_ (??),
        ### and maybe OpExprs never need ipath or place, just env
        ###    (for symbol lookup when they include symbols? or did replacement already happen to make self understood??)
        ### and WORST OF ALL, it's actually a destructive make -- maybe it's _init_instance, called by common _destructive_make_in .
        assert not self.is_instance ###@@@ need to be in InstanceOrExpr superclass for this
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
    pass

class neg_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 1
    def __str__(self):
        return "- %s" % self._e_args #e need parens?
    pass

class If_expr(OpExpr): # so we can use If in formulas
    pass
# see also class If_ in testdraw.py
## def If(): pass

class ConstantExpr(Expr): ###k super is not quite right -- we want some things in it, like isinstance Expr, but not the __add__ defs
    def __init__(self, val):
        self._e_constant_value = val ####USE ME, by defining _e_eval?
        self._e_args = () # allows super _e_free_in to be correct
    pass

def canon_expr(subexpr):###CALL ME; a comment in Column.py says that env.understand_expr should call this...
    "Make subexpr an Expr, if it's not"
    if isinstance(subexpr, Expr):
        return subexpr
    elif isinstance(subexpr, type([])):
        return ListExpr(*subexpr) ###IMPLEM; btw is this always correct? or only in certain contexts??
            # could be always ok if ListExpr is smart enough to revert back to a list sometimes.
        #e analogous things for tuple and/or dict? not sure. or for other classes which mark themselves somehow??
    else:
        # assert it's not various common errors, like expr classes or not-properly-reloaded exprs
        assert not hasattr(subexpr, '_e_compute_method'), "subexpr seems bad: %r" % (subexpr,) ###e better choice of method to look for?
        #e more checks?
        # assume it's a python constant
        #e later add checks for its type, sort of like we'd use in same_vals or so... in fact, how about this?
        from state_utils import same_vals
        assert same_vals(subexpr, subexpr)
        return ConstantExpr(subexpr)
    pass

# ==

class Symbol(SymbolicExpr):
    "A kind of Expr that is just a symbol with a given name. Often used via the __Symbols__ module."
    def __init__(self, name = None):
        if name is None:
            name = "?%s" % compact_stack(skip_innermost_n = 3).split()[-1] # kluge - show line where it's defined
        self._e_name = name
        return
    def __str__(self):
        return self._e_name
    def __repr__(self):
        ## return 'Symbol(%r)' % self._e_name
        return 'S.%s' % self._e_name
    def _e_eval(self, env):
        print "how do we eval a symbol? some sort of env lookup ..."
        ## -- in the object (env i guess) or lexenv(?? or is that replacement??) which is which?
        # maybe: replacement is for making things to instantiate (uses widget expr lexenv), eval is for using them (uses env & state)
        # env (drawing_env) will let us grab attrs/opts in object, or things from dynenv as passed to any lexcontaining expr, i think...
        return env._e_eval_symbol(self) # note: cares mainly or only about self._e_name
    def _e_free_in(self, sym):
        """General case: Return True if Expr self contains sym (Symbol or its name) as a free variable, in some arg or option value.
        For this class Symbol, that means: Return True if sym is self or self's name.
        [overrides super version]
        """
        return (sym is self) or (sym == self._e_name)
    pass
