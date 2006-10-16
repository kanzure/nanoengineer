'''
Exprs.py

$Id$
'''

class Expr: # subclasses: SymbolicExpr (OpExpr or Symbol), Drawable###obs
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
    def __init__(self, *args, **kws):
        assert 0, "subclass %r of Expr must implement __init__" % self.__class__.__name__
    def __call__(self, *args, **kws):
        assert 0, "subclass %r of Expr must implement __call__" % self.__class__.__name__

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
        args = self._e_args
        modargs = tuple(map(reps, args)) ##k reps is callable??
        if args == modargs:
            ##k requires fast == on Expr, which unlike other ops is not meant as a formula
            # (could it be a formula, but with a boolean value too, stored independently???)
            return self
        return self.__class__(*modargs)
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
        self._e_args = args
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
    pass
