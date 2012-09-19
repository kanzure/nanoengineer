# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Exprs.py -- class Expr, and related subclasses and utilities, other than those involving Instances

@author: Bruce
@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  See LICENSE file for details.

TODO:

this file is getting kind of long - maybe split it in some sensible way?
"""

# note: this module should not import ExprsMeta, though its InstanceOrExpr subclass needs to (in another module).
# instead, it is probably fully imported by ExprsMeta.

from utilities.debug import compact_stack
from utilities.debug import print_compact_stack
from utilities.debug import safe_repr

##from debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True, Choice

from utilities.Comparison import same_vals

from exprs.py_utils import printnim, printfyi, printonce
from exprs.intern_ipath import intern_ipath

from foundation.state_constants import _UNSET_

# ==

EVAL_REFORM = True
    # False supposedly acts like old code, True like new code which has by now become standard;
    # this affects all class defs, so to be safe, print a warning if the value is not true.
    # [bruce 070115 & 071102]

if not EVAL_REFORM:
    print "EVAL_REFORM is %r" % EVAL_REFORM

# == utilities #e refile

def map_dictvals(func, dict1):
    """
    This does to a dict's values what map does to lists --
    i.e. it makes a new dict whose values v are replaced by func(v).
    [If you wish func also depended on k, see map_dictitems.]
    """
    return dict([(k,func(v)) for k,v in dict1.iteritems()])

def map_dictitems(func, dict1):
    """
    This does to a dict's items what map does to lists --
    i.e. it makes a new dict whose items are f(item) from the old dict's items.
    Func should take 1 argument, a pair (k,v), and return a new pair (k2, v2).
    Often k2 is k, but this is not required.
    If the new items have overlapping keys, the result is... I don't know what. #k
    """
    return dict(map(func, dict1.iteritems()))

# == serial numbers (along with code in Expr.__init__)

_next_e_serno = 1 # incremented after being used in each new Expr instance (whether or not _e_is_instance is true for it)
    ###e should we make it allocated in Expr subclasses too, by ExprsMeta, and unique in them?

_debug_e_serno = -1 ## normally -1 # set to the serno of an expr you want to watch #k untested since revised

def expr_serno(expr):
    """
    Return the unique serial number of any Expr (except that Expr python subclasses all return 0).
    Non-Exprs all return -1.
    """
    try:
        return expr._e_serno # what if expr is a class? is this 0 for all of those?? yes for now. ###k
    except:
        # for now, this case happens a lot, since ExprsMeta calls us on non-expr vals such as compute method functions,
        # and even sometimes on ordinary Python constants.
        assert not is_Expr(expr)
        return -1
    pass

# == predicates

def is_Expr(expr):
    """
    is expr an Expr -- meaning, a subclass or instance of class Expr? 
    (Can be true even if it's also considered an Instance.)
    """
    return hasattr(expr, '_e_serno')

def is_expr_Instance(expr): ##e or just is_Instance?? or is_Expr_Instance?
    """
    #doc
    """
    return is_Expr(expr) and expr_is_Instance(expr)

def is_expr_Instance_or_None(expr): #070326, common enough to have its own predicate
    return expr is None or is_expr_Instance(expr)

def is_pure_expr(expr): ##e why not is_pure_Expr? is lowercase expr a generic term of some sort? [070207 terminology Q]
    """
    is expr an Expr (py class or py instance), but not an Instance?
    """
    return is_Expr(expr) and not expr_is_Instance(expr)

def expr_is_Instance(expr):
    """
    is an Expr an Instance?
    """
    res = expr._e_is_instance
    assert res is False or res is True ###e hmm, might fail for classes, need to fix
    return res

def is_Expr_pyinstance(expr): ##e make sure we check this before calling _e_eval / _e_compute_method / _e_make_in on an expr
    """
    Is expr an Expr, and also a python instance (not an Expr subclass)?
    (This is necessary to be sure you can safely call Expr methods on it.) 
    (Note: If so, it might or might not be an Instance.)
    [Use this instead of isinstance(Expr) in case Expr module was reloaded.]
    """
    return is_Expr(expr) and is_Expr(expr.__class__)

def is_Expr_pyclass(expr):
    """
    Is expr an Expr and a python class (i.e. is it a subclass of Expr)?
    [This is easier to use than issubclass, since that has an exception on non-classes.]
    """
    return is_Expr(expr) and not is_Expr(expr.__class__)

def is_constant_expr(expr): # written for use in def If, not reviewed for more general use
    """
    #doc;
    WARNING: not reviewed for use after some code gets reloaded during debugging
    [but, it seems like it should be ok, since constant_Expr is defined in this module, and this module is not auto-reloaded.]
    """
    assert is_pure_expr(expr)
    return isinstance(expr, constant_Expr) ###k probably too limited; #e might need to delve in looking for sources of non-constancy;
        #e might prefer to return the simpified const value, or a non-constant indicator (eg an equiv constant_Expr or None)

def expr_constant_value(expr): # written for use in def If, not reviewed for more general use
    """
    #doc;
    WARNING: not fully reviewed for use after some code gets reloaded during debugging [see is_constant_expr doc for details].
    """
    if is_constant_expr(expr):
        return True, expr._e_constant_value #k will be wrong once is_constant_expr is improved -- a single func will need to do both things
    else:
        return False, "arb value"
    pass

def is_constant_for_instantiation(expr): #070131, moved here 070321 from instance_helpers.py
    """
    Is expr (which might be an arbitrary python object) a constant for instantiation?
    (If true, it's also a constant for eval, but not necessarily vice versa.)
    """
    #e refile? should be compatible with _e_make_in methods in kinds of exprs it's true for
    # anything except a pure expr is a constant, and so is an Expr subclass
    if not (is_pure_expr(expr) and is_Expr_pyinstance(expr)):
        return True
    # cover a constant Symbol too, e.g. Automatic
    #e (merge _e_sym_constant with _e_instance? see comment in Symbol._e_make_in for discussion)
    if getattr(expr, '_e_sym_constant', False):
        return True
    return False

# ==

class Expr(object): # notable subclasses: SymbolicExpr (OpExpr or Symbol), InstanceOrExpr
    """
    abstract class for symbolic expressions that python parser can build for us,
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
    ##e for debug it would be useful to record line/file of expr construction, and then for any instance or expr
    # printed in an error msg or traceback, print the chain of these (as it gets customized, gets args, gets instantiated) --
    # sort of like a stacktrace of where it was made. Not hard (see compact_stack for how). Enable using global flag. [070131]

    # default/initial values of instance variables
    _e_is_symbolic = False #061113
    _e_args = () # this is a tuple of the expr's args (processed by canon_expr), whenever those args are always all exprs.
    _e_kws = {} # this is a dict of the expr's kw args (processed by canon_expr), whenever all kwargs are exprs.
        # note: all expr subclasses which use this should reassign to it, so this shared version remains empty.
        # note: all Expr subclasses should store either all or none of their necessary data for copy in _e_args and _e_kws,
        # or they should override methods including copy(?) and replace(?) which make that assumption. ##k [061103]
    _e_is_instance = False # override in certain subclasses or instances ###IMPLEM
    _e_serno = 0 ###k guess; since Expr subclasses count as exprs, they all have a serno of 0 (I hope this is ok)
    _e_has_args = False # subclass __init__ or other methods must set this True when it's correct... ###nim, not sure well-defined
        # (though it might be definable as whether any __init__ or __call__ had nonempty args or empty kws)
        # (but bare symbols don't need args so they should have this True as well, similar for OpExpr -- all NIM)
        # see also InstanceOrExpr .has_args -- if this survives, that should be renamed so it's the same thing [done now, 061102]
        # (the original use for this, needs_wrap_by_ExprsMeta, doesn't need it -- the check for _self is enough) [061027]
    def __init__(self, *args, **kws):
        assert 0, "subclass %r of Expr must implement __init__" % self.__class__.__name__
    def __eq__(self, other):#070122
        """
        Default implem for many but not all subclasses of Expr.
        Note: we don't require _e_sernos to be equal!
        """
        # this and/or its overridings assume: same_vals works on Exprs [not tested or reviewed ###DOIT],
        # and widget_env is also given a correct __eq__ [###NIM, means lexenv_Exprs will rarely compare equal when they should].
        if self is other:
            return True
        if (not hasattr(other, '__class__')):
            return False # without this test, epydoc fails with: AttributeError: class SyntaxError has no attribute '__class__'
        if self.__class__.__name__ != other.__class__.__name__:
            return False #e this might change someday when comparing proxies -- see comment below
        if self.__class__ is not other.__class__:
            print "warning: exprs passed to __eq__, sernos %r and %r, have different classes with same name %s -- reload issue?" % \
                  (self._e_serno, other._e_serno, self.__class__.__name__)
            return False # this is safest (e.g. it lets us assume other is an Expr in the remaining code)
        if self._e_is_instance or other._e_is_instance: # this is not safe to ask unless we know other is an Expr
            return False # Instances are only equal if identical, for now (and an Instance can't equal a non-Instance);
                #e later two Instances might be equal if they know they're proxies for the same something else (not sure)
        # now we're comparing two pure exprs of the same class
        #e optim: if both are interned, return False; otherwise intern them and recompare
        # In case of Numeric array args, should we only use __ne__, use same_vals, or trust what we compare here to come out of
        # canon_expr? I think I'll trust canon_expr but use != anyway (redundant), but in constant_Expr use same_vals.
        if self._e_has_args != other._e_has_args:
            return False
        if self._e_args != other._e_args:
            return False
        if self._e_kws != other._e_kws:
            return False
        return True
    def __ne__(self, other):
        return not self.__eq__(other)
    def _e_init_e_serno(self): # renamed from _init_e_serno_, 061205
        """
        [private -- all subclasses must call this; the error of not doing so is not directly detected --
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
        if self._e_serno == _debug_e_serno: #k hope not too early for %r to work
            print_compact_stack("just made expr %d, %r, at: " % (_debug_e_serno, self))
        return
    def _e_dir_added(self): # 061205
        """
        For a symbolic expr only, return the names in dir(self) which were stored by external assignments.
        """
        assert self._e_is_symbolic
        assert not self._e_is_instance #k probably implied by _e_is_symbolic
        return filter( lambda name: not (name.startswith('_e_') or name.startswith('__')) , dir(self) )
    def __call__(self, *args, **kws):
        assert 0, "subclass %r of Expr must implement __call__" % self.__class__.__name__
    # note: for __getattr__, see also the subclasses; for __getitem__ see below

    def __get__(self, obj, cls):
        """
        The presence of this method makes every Expr a Python descriptor. This is so an expr which is a formula in _self
        can be assigned to cls._C_attr for some attr (assuming cls inherits from InvalidatableAttrsMixin),
        and will be used as a "compute method" to evaluate obj.attr. The default implementation creates some sort of Lval object
        with its own inval flag and subscriptions, but sharing the _self-formula, which recomputes by evaluating the formula
        with _self representing obj.
        """
        # more on the implem:
        # It stores this Lval object in obj.__dict__[attr], finding attr by scanning cls.__dict__
        # the first time. (If it finds itself at more than one attr, this needs to work! Is that possible? Yes -- replace each
        # ref to the formula by a copy which knows attr... but maybe that has to be done when class is created?
        # Easiest way is first-use-of-class-detection in the default implem. (Metaclass is harder, for a mixin being who needs it.)
        #  Ah, easier way: just store descriptors on the real attrs that know what to do... as we're in the middle of doing
        # in the code that runs when we didn't, namely _C_rule or _CV_rule. ###)
        if obj is None:
            return self
        #e following error message text needs clarification -- when it comes out of the blue it's hard to understand
        print "__get__ is nim in the Expr", self, ", which is assigned to some attr in", obj ####@@@@ NIM; see above for how [061023 or 24]
        print "this formula needed wrapping by ExprsMeta to become a compute rule...:", self ####@@@@
        return
    def _e_compute_method(self, instance, index, _lvalue_flag = False):
        """
        Return a compute method version of this formula, which will use instance as the value of _self,
        at the given index relative to instance. [index is a required arg as of 070120.]
        
        Example index [#k guess 061110]: the attrname where self was found in instance (as an attrvalue),
        or if self was found inside some attrval (but not equal to the whole),
        a tuple containing the attrname and something encoding where self occurred in the attrval.
        Update 070120: that "found inside some attrval" part is now handled by lexenv_ipath_Expr,
        and index can be modified as suggested by kluge070119 (experimental, not yet debugged).
        """
        #####@@@@@ WRONG API in a few ways: name, scope of behavior, need for env in _e_eval, lack of replacement due to env w/in self.
        ##return lambda self = self: self._e_eval( _self = instance) #e assert no args received by this lambda?
        # TypeError: _e_eval() got an unexpected keyword argument '_self'
        ####@@@@ 061026 have to decide: are OpExprs mixed with ordinary exprs? even instances? do they need env, or just _self?
        # what about ipath? if embedded instances, does that force whole thing to be instantiated? (or no need?)
        # wait, embedded instances could not even be produced w/o whole thing instantiating... so i mean,
        # embedded things that *need to* instantiate. I guess we need to mark exprs re that...
        # (this might prevent need for ipath here, if pure opexprs can't need that path)
        # if so, who scans the expr to see if it's pure (no need for ipath or full env)? does expr track this as we build it?

        # try 2 061027 late: revised 070117
        assert instance._e_is_instance, "compute method for %r asked for on non-Instance %r (index %r, lvalflag %r)" % \
               (self, instance, index, _lvalue_flag) # happens if a kid is non-instantiated(?) # revised 070117

        env, ipath = instance._i_env_ipath_for_formula_at_index( index) # split out of here into IorE, 070117
            # does _self = instance binding [tho that might change -- 070120]

        if not _lvalue_flag:
            # usual case
            return lambda self=self, env=env, ipath=ipath: self._e_eval( env, ipath ) #e assert no args received by this lambda?
        else:
            # lvalue case, added 061204, experimental -- unclear if returned object is ever non-flyweight or has anything but .set_to
            # [note, this presumably never happens when EVAL_REFORM, at least as of late 070119]
            return lambda self=self, env=env, ipath=ipath: self._e_eval_lval( env, ipath )
        pass
    def __repr__(self): # class Expr
        """
        [often overridden by subclasses; 
         __str__ can depend on __repr__ but not vice versa(?) 
         (as python itself does by default(??))]
        """
        ## return str(self) #k can this cause infrecur?? yes, at least for testexpr_1 (a Rect_old) on 061016
        ## return "<%s at %#x: str = %r>" % (self.__class__.__name__, id(self), self.__str__())
        return "<%s#%d%s>" % (self.__class__.__name__, self._e_serno, self._e_repr_info())
    def _e_repr_info(self):#061114
        """
        [private helper for __repr__]
        """
        if self._e_has_args:
            if self._e_is_instance:
                return '(i)'
            else:
                return '(a)'
        else:
            if self._e_is_instance:
                return '(i w/o a)' # an error, i think, at least for now
            else:
                return ''
        pass
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
    def __pos__( self):
        """operator +a"""
        return pos_Expr(self)

    #e __mod__? (only ok if not used for print formatting -- otherwise we'd break debug prints like "%r" % expr)
    #e __len__? (might be ok, except lack of it catches bugs every so often, so I guess it's not a good idea)
    #e various type coercers...
    # but some special methodnames are impossible to support safely, like __str__, __eq__, etc...
    #e unless we have a special expr wrapper to give it the power to support all those too, but only if used right away. [061113]

    def __getitem__( self, index): #k not reviewed for slices, unlikely they'll work fully
        """ operator a[b] """
        #e will Instances extend this to return their kids??
        return getitem_Expr(self, index)
    
    # == not sure where these end up
    def __float__( self):
        """ operator float(a) """
        print_compact_stack( "kluge: float(expr) -> 17.0: " )####@@@@ need float_Expr
        return 17.0
    def _e_replace_using_subexpr_filter(self, func): #e rename, since more like map than filter; subexpr_mapper??
# zapped 061114 since common and so far always ok:
##        if not isinstance(self, (OpExpr, constant_Expr)):#k syntax
##            printfyi("_e_replace_using_subexpr_filter called on pyinstance of class %s" % self.__class__.__name__)
##                 ####k ever on an InstanceOrExpr?? might be wrong then, just as _e_eval should not go inside -- not sure!
##                 # more likely, it needs to go in but in a lexcontext-modified way! [061105 guess] ###@@@
        args = self._e_args
        kws = self._e_kws
        if not args and not kws:
            return self # optim
        modargs = tuple(map(func, args))
        modkws = map_dictvals(func, kws)
        if modargs == args and modkws == kws:
            # Note: requires fast == on Expr -- currently we let Python use 'is' by default. [#k in py doc, verify that's what happens]
            # Note: '==' (unlike other ops) is not meant as a formula.
            # (Could it be a formula, but with a boolean value too, stored independently??)
            #
            # Note: this is not affected by the Numeric Python design flaw (i.e. bug) about what '==' means,
            # since any Numeric arrays in args or kws have been wrapped by constant_Expr.
            # [070321, educated guess, not absolutely verified ####k]
            return self # helps prevent memory leaks (by avoiding needless reconstruction of equal exprs); might help serno too??
        printnim("replace would be wrong for an expr with subexprs but also other data -- do we have any such? ##k")##k
            #k (wouldn't it also be wrong for expr w/ other data, even if no args/kws??)
        return self.__class__(*modargs, **modkws)
    def _e_free_in(self, sym): #e name is confusing, sounds like "free of" which is the opposite -- rename to "contains_free"??
        """
        Return True if self contains sym (Symbol or its name) as a free variable, in some arg or option value.
        [some subclasses override this]
        """
        try:
            _e_args = self._e_args
            #k not sure this is defined in all exprs! indeed, not in a Widget2D python instance... ####@@@@
        except AttributeError:
            #####@@@@ warning: following is slow, even when it doesn't print -- NEEDS OPTIM ####@@@@
            printonce("debug note: _e_free_in is False since no _e_args attr in %r" % self) # print once per self
            return False ###k guess -- correct? #####@@@@@
        for arg in _e_args: 
            if arg._e_free_in(sym):
                return True
        printnim("_e_free_in is nim for option vals")###@@@ btw 061114 do we still use _e_free_in at all? see if this gets printed.
        return False
    def _e_eval_to_expr(self, env, ipath, expr):#070117, revised 070118 to save ipath
        """
        #doc
        """
        assert EVAL_REFORM # otherwise exprs don't eval to self except some Symbols, and I guess those don't call this tho i forget...#k
        return lexenv_ipath_Expr(env, ipath, expr) # the full ipath might not be needed but might be ok... ###k
    # note: _e_eval is nim in this class -- it must be implemented in subclasses that need it.
    # If you want to add a default errmsg def here, first review whether its presence would affect the expr-building code!
    # [070117 comment]
    def _e_burrow_for_find_or_make(self, env, ipath): #070119 #e might rename find_or_make to instantiate or so
        """
        General case: Return (subexpr, new_env, new_ipath), where subexpr is the outermost subexpr of self
        which has no outermost local ipath or env mods, and those mods are stripped from self to get subexpr,
        and added to env, ipath to make new_env, new_ipath. Instantiating (self, env, ipath) and
        (subexpr, new_env, new_ipath) should get the same result semantically, and the implem enforces this
        by canonicalizing (self, env, ipath) using this method before instantiation. [###NIM]
           Trivial version for most expr classes: just return (self, env, ipath) unchanged.
        Overrides are only needed (so far, AFAIK) by lexenv_Expr and lexenv_ipath_Expr.
        [When IorE subclasses implement instance-sharing a la textureholders or (desired) CLE or other glue code
         (eg type coercion) objects, they too are likely to need a nontrivial implem of this, which filters the ipath
         down to the part that uniquely identifies the shared object. ##e]
        (Expr classes that can't be the result of evaluation (e.g. constant_Expr, If_expr, probably eval_Expr)
        don't need to override this, since exprs should be evalled before being instantiated. ###k)
        """
        # Is the docstring right about this not being needed in If_expr? eval_Expr? constant_Expr?? other internal exprs? ###k
        return (self, env, ipath)
    pass # end of class Expr

def safer_attrpath(obj, *attrs): #e refile, doc, rename
    for attr in attrs:
        try:
            obj = getattr(obj, attr)
        except AttributeError:
            return "<no %r in some %s>" % (attr, obj.__class__.__name__)
        continue
    return obj

class SymbolicExpr(Expr): # Symbol or OpExpr
    _e_is_symbolic = True #061113
    _e_sym_constant = False #070131, can be overridden in subclasses or instances; see class Symbol for doc
    def __call__(self, *args, **kws):
        assert not self._e_is_instance # (should never happen I think)
        return call_Expr(self, *args, **kws)
    def __getattr__(self, attr): # in class SymbolicExpr
        if attr.startswith('__'):
            # be very fast at not finding special python attrs like __repr__
            raise AttributeError, attr
        # the code after this happens when constructing exprs, not when using them,
        # so a bit of slowness should be ok.
        assert not self._e_is_instance # (should never happen I think; if it can be legal, change to raise attrerror)
        if self._e_sym_constant:
            # [this special case might be evidence that _e_sym_constant should imply something like _e_is_instance --
            #  both of them mean "eval to self", "instantiate to self". Maybe they should even be merged...
            #  idea not reviewed. Should check whether other special cases for _e_is_instance apply to _e_sym_constant. ###e 070131]
            raise AttributeError, "no attr %r in %s" % (attr, safe_repr(self))
        if attr.startswith('_i_'):
            assert self._e_is_instance, \
                   "safety rule: automatic formation of getattr_Expr not allowed for attrs starting _i_, as in %r.%s" % \
                   (self, attr)
                #k not positive this is ok, we'll see [061105]
                # 070122 this failed with _app._i_instance(testexpr_19b) (and I added text to the assertion),
                # but that just means _app needs a public instancemaker rather than just that internal one -- now it has .Instance
            # note: self._e_is_instance is defined in all pyinstance exprs, not only InstanceOrExpr.
            assert 0 # not reached
        if attr.startswith('_e_') or (attr.startswith('_') and '__' in attr): # _i_ is handled separately above
            # We won't pretend to find Expr methods/attrs starting _e_ (also used in Instances),
            # or Instance ones starting _i_ -- but do reveal which class or object we didn't find them in.
            ##e ideally we'd reveal something longer than class and shorter than object...
            # 061203: also exclude _attr__xxx since it might be name-mangled. Needed to exclude _ExprsMeta__set_attr.
            # [Not confident this exclusion is always good -- maybe what we really need is a variant of hasattr
            # which turns off or detects and ignores the effect of this __getattr__. ###k]
            raise AttributeError, "no attr %r in %s" % (attr, safe_repr(self))
        return getattr_Expr(self, attr)
    pass

class OpExpr(SymbolicExpr):
    """
    Any expression formed by an operation (treated symbolically) between exprs, or exprs and constants
    """
    _e_debug = False #e move to a superclass? [bruce 070816 new feature]
    def __init__(self, *args, **kws): # arglist would just be "self, *args, doc = None" except that it's invalid syntax
        self._e_args = tuple(map(canon_expr, args)) # tuple is required, so _e_args works directly for a format string of same length
        self._e_init_e_serno() # call this AFTER canon_expr (for sake of _e_serno order)
        doc = kws.pop('doc', None)
        self.__doc__ = doc #070207 added this keyword arg -- supplied (to a StateAttr stub) but not yet used;
            # not sure it belongs in this class rather than the subclass that needed it (State) ##k
        # don't do this: junk = kws.pop('_KLUGE_fakeoption', None)
        debug = kws.pop('_e_debug', False)
        if debug:
            # activate some debug prints for self (only used by some subclasses)
            self._e_debug = True
        assert not kws, "unexpected keyword args for %s: %r" % (self.__class__.__name__, kws.keys())
        self._e_init()
        return
    def _e_init(self):
        assert 0, "subclass of OpExpr must implement _e_init"
    def __repr__(self): # class OpExpr
        return "<%s#%d%s: %r>"% (self.__class__.__name__, self._e_serno, self._e_repr_info(), self._e_args,)
    def _e_argval(self, i, env,ipath): # see also a copy of this in IfExpr
        """
        Under the same assumptions as _e_eval (see its docstring),
        compute and return the current value of an implicit kid-instance made from self._e_args[i], at relative index i,
        doing usage-tracking into caller (i.e. doing no memoization or caching of our own).
        """
        def __debug_frame_repr__(locals):
            """return a string for inclusion in some calls of print_compact_stack"""
            # note: this will always run before res is available
            return "_e_argval(i = %r, ipath = %r), self = %r" % (i,ipath,self)
         ##e consider swapping argorder to 0,ipath,env or (0,ipath),env
        arg = self._e_args[i]
        try:
            res = arg._e_eval(env, (i,ipath))
        except:
            print "following exception concerns arg._e_eval(...) where arg = %r" % (arg,) #070228 (guess: arg is class World itself)
            raise
        return res
    def _e_kwval(self, k, env,ipath):
        """
        Like _e_argval, but return the current value of our implicit-kid-instance of self._e_kws[k], rel index k.
        """
        return self._e_kws[k]._e_eval(env, (k,ipath))
    def _e_eval(self, env, ipath):
        """
        Considering ourself implicitly instantiated by the replacements (especially _self_) in env,
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
        assert env #061110
        assert not self._e_kws #e remove when done with devel -- just checks that certain subclasses overrode us -- or, generalize this
        func = self._e_eval_function
            # Note: these functions would turn into bound methods here,
            # if we didn't wrap them with staticmethod when assigning them.
            # Not doing that caused the "tuple_Expr bug" (see cvs for details).
            # Another solution would have been to grab the funcs only out of
            # the class's __dict__. Using staticmethod seems clearer.
        res = apply(func, [self._e_argval(i,env,ipath) for i in range(len(self._e_args))])
        return res
    def _e_eval_lval(self, env,ipath):
        """
        #doc
        """
        assert env #061110
        assert not self._e_kws #e remove when done with devel -- just checks that certain subclasses overrode us -- or, generalize this
        func = self._e_eval_lval_function
        res = apply(func, [self._e_argval(i,env,ipath) for i in range(len(self._e_args))])
        return res
    pass # end of class OpExpr

class call_Expr(OpExpr): # note: superclass is OpExpr, not SymbolicExpr, even though it can be produced by SymbolicExpr.__call__
    ###BUG: __repr__ doesn't print self._e_kws [noticed 070119]
    def __init__(self, callee, *callargs, **kws):
        # we extend OpExpr.__init__ so we can have kws, and canon them
        self._e_kws = map_dictvals(canon_expr, kws) ###e optim: precede by "kws and"
        OpExpr.__init__(self, callee, *callargs) # call this AFTER you call canon_expr above (for sake of _e_serno order)
    def _e_init(self):
        # Store some args under more convenient names.
        # Note: this does NOT hide them from (nondestructive) _e_replace* methods,
        # since those find the original args, modify them, and construct a new expr from them.
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
        """
        [the only reason the super method is not good enough is that we have _e_kws too, I think;
         maybe also the distinction of that to self._e_call_kws, but I doubt that distinction is needed -- 061105]
        """
        assert env #061110
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

class LvalueFromObjAndAttr(object): #061204 for _e_eval_lval and LvalueArg, likely to be revised #e refile?
    #e later note 070316: we use this in toplevel expr macros to turn obj.attr into a stateref,
    # since getattr_Expr can't do that (it only makes a syntactic lval).
    # Should we rename this to e.g. getattr_StateRef, and put it into basic? (It's already in basic, since Exprs.* is.)
    # Maybe, but ONLY IF WE MAKE IT AN EXPR -- as it is, you have to use call_Expr with it.
    ##e make a variant for getitem_Expr? 
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr
    def set_to(self, val):
        ###e probably we should rename set_to -> set_value, and define get_value and value -- see StateRefInterface [070312]
        try:
            setattr( self.obj, self.attr, val)
        except:
            print "following exception in setattr( self.obj, self.attr, val) concerns self = %r" % (self,)
            raise
        pass
    # 070312 conform to StateRefInterface
    set_value = set_to
    def get_value(self):
        return getattr(self.obj, self.attr)
    value = property( get_value, set_value)
    def __repr__(self):
        return "<%s at %#x for %r.%r>" % (self.__class__.__name__, id(self), self.obj, self.attr)
    #e some sort of .get function, .value attr (can be set or get), subscribe func, etc
    pass

class getattr_Expr(OpExpr):
    def __call__(self, *args, **kws):
        msg = "error: getattr exprs are not callable: " \
              "explicit call_Expr needed, instead of direct call " \
              "of %r with:" % self, args, kws #bruce 080528 revised msg
        print msg
        assert 0, msg
    def _e_init(self):
        assert len(self._e_args) in (2,3) #e kind of useless and slow #e should also check types? #070203 permit 3-arg form
        attr = self._e_args[1]
        assert attr #e and assert that it's a python identifier string? Note, it's actually a constant_Expr containing a string!
            # And in theory it's allowed to be some other expr which evals to a string,
            # though I don't know if we ever call it that way
            # (and we might want to represent or print it more compactly when we don't).
    def __str__(self):
        if len(self._e_args) == 2:
            return "%s.%s" % self._e_args #e need parens? need quoting of 2nd arg? Need to not say '.' if 2nd arg not a py-ident string?
        else:
            return "getattr_Expr(%s, %s, %s)" % self._e_args
    _e_eval_function = getattr # this doesn't need staticmethod, maybe since <built-in function getattr> has different type than lambda
    ## _e_eval_lval_setto_function = setattr
    _e_eval_lval_function = staticmethod(LvalueFromObjAndAttr) #061204 #k not sure if staticmethod is required; at least it works ###UNREVIEWED for 3 args
    pass

class getitem_Expr(OpExpr): #061110
    def _e_init(self):
        assert len(self._e_args) == 2 #e kind of useless and slow??
        # note, _e_args[1] is often constant_Expr(<an int as list-index> or <an attrname as dict key>), but could be anything
    def __str__(self):
        return "%s[%s]" % self._e_args #e need parens?
    _e_eval_function = staticmethod( lambda x,y:x[y] )
    #e _e_eval_lval_function too, variant of LvalueFromObjAndAttr?
    pass

class mul_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s * %s" % self._e_args #e need parens?
    _e_eval_function = staticmethod( lambda x,y:x*y ) # does this have a builtin name? see operators module ###k
    pass

class div_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s / %s" % self._e_args #e need parens?
    _e_eval_function = staticmethod( lambda x,y:x/y )
    pass

class add_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s + %s" % self._e_args #e need parens?
    _e_eval_function = staticmethod( lambda x,y:x+y )
    ##e refile this note (proposed): [i, ipath] is an inlined sub_index(i,ipath); [] leaves room for intern = append
    pass

class sub_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s - %s" % self._e_args #e need parens?
    _e_eval_function = staticmethod( lambda x,y:x-y )
    pass

class neg_Expr(OpExpr):
    def _e_init(self):
        assert len(self._e_args) == 1
    def __str__(self):
        return "- %s" % self._e_args #e need parens?
    _e_eval_function = staticmethod( lambda x:-x )
    pass

class pos_Expr(OpExpr):#061211
    def _e_init(self):
        assert len(self._e_args) == 1
    def __str__(self):
        return "+ %s" % self._e_args #e need parens?
    _e_eval_function = staticmethod( lambda x:+x )
    pass

class list_Expr(OpExpr): #k not well reviewed, re how it should be used, esp. in 0-arg case
    #aka ListExpr, but we want it not uppercase by convention for most OpExprs
    def _e_init(self):
        pass
    def __str__(self):
        return "%s" % (list(self._e_args),) #e need parens?
    _e_eval_function = staticmethod( lambda *args:list(args) )
        ####e consider making this a tuple_Expr synonym -- see ArgList comments [070321]
    pass

def printfunc(*args, **kws): #e refile, maybe rename dprint; compare to same-named *cannib*.py func
    prefix = kws.pop('prefix', '')
    assert not kws
    print "printfunc %s: %r" % (prefix, args)
    return args[0]

class tuple_Expr(OpExpr): #k not well reviewed, re how it should be used, esp. in 0-arg case
    def _e_init(self):
        pass
    def __str__(self):
        return "%s" % (tuple(self._e_args),) #e need parens?
    def _e_eval_function(self, *argvals):
        # only become a tuple if we contain nothing to instantiate -- otherwise a tuple_Expr -- needed for ArgList [070321]
        for val in argvals:
            if is_pure_expr(val): #k not sure this condition is exactly right
                if self._e_args == argvals:
                    return self # optimization
                return tuple_Expr(*argvals)
            continue
        return argvals # a tuple, not a tuple_Expr
    def _e_make_in(self, env, ipath): # 070321 needed for ArgList
        # we don't need to eval each arg expr, since we ourselves were just evalled (and are the result of that)
        # so all our args are evalled. But, not all evalled things have _e_make_in! Also, they went through canon_expr after eval.
        # Either we need to check both for constant_Expr (or anything else canon_expr can make ###k), and check
        # is_constant_for_instantiation like _i_instance does, or we need to actually call _i_instance,
        # depending, I think, on how much we want to cache these instances. For now I'll do what's easiest
        # (is_constant_for_instantiation, no caching) and review it later. WARNING: things like SimpleColumn
        # which declared each arg separately used to be able to cache them individually -- so THIS IS ######WRONG.
        # It'll work, I think, but be a slowdown.
        mades = [self._e_make_argval(argval, env, i, ipath) for (i,argval) in zip(range(len(self._e_args)), self._e_args)]
        return tuple(mades)
    def _e_make_argval(self, argval, env, i, ipath):
        """
        [private helper]
        """
        if is_constant_for_instantiation(argval):
            # print "fyi: tuple_Expr is_constant_for_instantiation true for %r" % (argval,)
            # this happens when an Instance is passed as an ArgList element, e.g. <PM_from_groups#40798(i)> in a SimpleColumn;
            # it's legit, so remove the print. [070322]
            return argval
        constflag, constval = expr_constant_value(argval)
        if constflag:
            # argval is a constant_Expr -- this happens here (but not in _i_instance) due to canon_expr.
            # btw, don't put _e_make_in on constant_Expr, i think - might hide bugs. (A correct def of it is there but cmted out.)
            return constval
        return argval._e_make_in(env, (i, ipath)) ###WRONG as explained in comment above.
    pass

# same as in basic.py:
from numpy.oldnumeric import dot
from geometry.VQT import V, norm, vlen

class V_expr(OpExpr):
    """
    Make an expr for a Numeric array of floats. Called like VQT.py's V macro.
    """
    # Note: the name contains 'expr', not 'Expr', since it's more public than the
    # typical class named op_Expr (official reason) and since it looks better in
    # contrast with V (real reason). Note that the real reason, but not the official one,
    # explains why we later used 'E' in format_Expr.]
    def _e_init(self):
        pass
    def __str__(self):
        return "V_expr%s" % (tuple(self._e_args),) #e need parens?
    _e_eval_function = staticmethod( lambda *args: V(*args) ) #e could inline as optim
    pass

# ==

# these function -> OpExpr macros are quick hacks, fine except for their printform and maybe their efficiency.

##e maybe rewrite them like this: norm_Expr = func_Expr(norm)

def norm_Expr(*args):
    return call_Expr( norm, *args)

def vlen_Expr(*args):
    return call_Expr( vlen, *args)

def dot_Expr(*args):
    return call_Expr( dot, *args)

def max_Expr(*args):
    return call_Expr( max, *args)

def min_Expr(*args):
    return call_Expr( min, *args)

def int_Expr(*args):
    return call_Expr( int, *args)

def not_Expr(arg): # maybe this is an operator so we can just make an OpExpr in usual way??
    ###e try it - try using not instead, in the call of this, to see if __not__ is the right name
    return call_Expr(lambda val: not val, arg)

def eq_Expr(arg1, arg2):
    return call_Expr(lambda a1,a2: a1 == a2, arg1, arg2)

def ne_Expr(arg1, arg2):
    return call_Expr(lambda a1,a2: a1 != a2, arg1, arg2)

def mod_Expr(arg1, arg2):
    return call_Expr( _eval_mod_Expr, arg1, arg2)

def _eval_mod_Expr(a1, a2):#070121
    """
    private helper
    """
    assert not (type(a1) == type('')), \
           "mod_Expr arg1 %r is a string, would do string formatting instead of mod by %r" % (a1, a2)
    return a1 % a2

# ==

class and_Expr(OpExpr): #061128
    """
    Evaluate only enough args (out of 2 or more) 
    to return the last one if they're all true, 
    otherwise the first false one.
    """
    def _e_init(self):
        assert len(self._e_args) >= 2
        assert not self._e_kws #k needed?
    def __str__(self):
        return "and_Expr%r" % self._e_args
    def _e_eval(self, env, ipath):
        assert env
        for i in range(len(self._e_args)):
            res = self._e_argval(i,env,ipath)
            if not res:
                return res # the first false res
            continue
        return res # the last res, if they're all true
    # note: operator.__and__ requires exactly two args, and couldn't help anyway since we don't always want to eval arg2
    pass

class or_Expr(OpExpr): #061128 untested
    """
    Evaluate only enough args (out of 2 or more) 
    to return the last one if they're all false, 
    otherwise the first true one.
    """
    def _e_init(self):
        assert len(self._e_args) >= 2
        assert not self._e_kws #k needed?
    def __str__(self):
        return "or_Expr%r" % self._e_args
    def _e_eval(self, env, ipath):
        assert env
        for i in range(len(self._e_args)):
            res = self._e_argval(i,env,ipath)
            if res:
                return res # the first true res
            continue
        return res # the last res, if they're all false
    pass

# note: see also If_expr.py

# ==

def assert_0_func(msg): #e refile #e rename
    """
    Raise an AssertionError with msg, but be a function, so we're usable in lambdas.
    Typical usage: cond and result or assert_0_func("error-description" % args).
    """
    assert 0, msg

class format_Expr(OpExpr): #061113, seems to work
    #k (tho no test yet proved it defers eval til when it needs to -- hmm, same for *all* OpExprs, until we implem statemods?
    #   no -- once something can access redraw_counter, that should provide a good enough test, for any OpExpr we make depend on that.)
    """
    Make an expr for producing the results of <format_string> % <*args>.
    (See also mod_Expr [nim ##e], for exprs based on numeric uses of the % operator. Maybe they can be expressed using % directly?)
    Note, unlike __mod__ (sp??), this is varargs, not two args.
    It would be nice to be able to say the latter directly,
    but it's hard to do without dangerously interfering with debug prints of exprs in the code
    (though it might be possible someday -- see code comments for details).
       We might rename this to sprintf or format (not printf, since that implies a side effect on stdout).
    """
    def _e_init(self):
        assert len(self._e_args) >= 2 #e later, change to >=1, since just 1 arg is legal -- I guess.
            # For now, >= 2 is usefully stricter for debugging.
            # In fact, maybe we'll keep it -- it catches use of '%' rather than ',', like in format_Expr("/tmp/%s.jpg" % testname)
        #e could assert arg0 is a string, but (1) not required until runtime, (2) hard to say anyway.
        pass
    def __str__(self):
        return "format_Expr%s" % (tuple(self._e_args),) #e need parens?
    _e_eval_function = staticmethod( lambda arg1, *args:
                                     ((type(arg1) is str) and (arg1 % args))
                                     or assert_0_func("format_Expr got non-string format %r" % arg1)
                                ) #e accept unicode arg1 too; python2.2 has an official way to express that (using the name string??)
    pass # format_Expr
    
# ==

class internal_Expr(Expr):
    """
    Abstract class for various kinds of low-level exprs 
    for internal use that have no visible subexprs.
    """
    def __init__(self, *args, **kws):
        """
        store args & kws but don't canon_expr them -- assume they are not necessarily exprs
        (and even if they are, that they should be treated inertly)
        """
        self.args = args # not sure if the non-_e_ name is ok... if not, try _e_data_args or so? ###k
        self.kws = kws
        self._internal_Expr_init() # subclasses should override this method to do their init
        self._e_init_e_serno()
        return
    def _internal_Expr_init(self):
        assert 0, "subclass must implem"
    def __eq__(self, other):
        """
        [overrides Expr version; WARNING: must be overridden by any internal_Expr subclasses that use self.kws]
        """
        if not Expr.__eq__(self, other):
            return False
        a1 = self.args
        a2 = other.args # must be tuples
        if a1 and a2:
            if not same_vals(a1,a2):
                ####k assume same_vals works properly for Exprs [perhaps never verified -- might give false negatives];
                # we need to use it instead of just == or != due to Numeric arrays in lists or tuples
                return False
        else:
            if a1 != a2: # 'or' might be faster, and is correct, but that's less clear, so nevermind -- someday this will be in C anyway
                return False
        # the following is not yet needed by any internal_Expr subclasses so far -- so leave it out for now, but keep the code
        ##k1 = self.kws
        ##k2 = other.kws
        ##if k1 and k2:
        ##    if not same_vals(k1,k2):
        ##        return False
        ##else:
        ##    if k1 != k2:
        ##        return False
        return True
    pass
    
class constant_Expr(internal_Expr):
    #### NOT YET REVIEWED FOR EVAL_REFORM 070117 [should it ever wrap the result using _e_eval_to_expr -- maybe in a variant class?] 
    ###k super may not be quite right -- we want some things in it, like isinstance Expr, but not the __add__ defs [not sure, actually]
    def _internal_Expr_init(self):
        (self._e_constant_value,) = self.args
    def __repr__(self): # class constant_Expr
        return "<%s#%d%s: %r>"% (self.__class__.__name__, self._e_serno, self._e_repr_info(), self._e_constant_value,)
    def __str__(self):
        return "%r" % (self._e_constant_value,) #e need parens?
            #k 061105 changed %s to %r w/o reviewing calls (guess: only affects debugging)
    def _e_eval(self, env, ipath):
        assert env #061110
        ## env._self # AttributeError if it doesn't have this [###k uses kluge in widget_env]
        # that failed (with the misleading AttrError from None due to Delegator),
        # but it's legit to fail now, since the constant can easily be in a lexenv with no binding for _self.
        return self._e_constant_value
##    def _e_make_in(self, env, ipath): ###e equiv to _e_eval? see comment in _CV__i_instance_CVdict [061105]
##        "Instantiate self in env, at the given index-path."
##        #e also a method of InstanceOrExpr, tho not yet of any common superclass --
##        # I guess we'll add to OpExpr and maybe more -- maybe Expr, but not sure needed in all exprs
##        return self._e_constant_value # thought to be completely correct, 061105 [and still, 061110, but zapping since redundant]
    pass

class hold_Expr(constant_Expr):
    #e might be renamed to something like no_eval, or we might even revise call_Expr to not always eval its args... not sure
    """
    Like constant_Expr, but (1) value has to be an expr, (2) replacements occur in value.
    Used internally to prevent eval of args to call_Expr.
    """
    def _e_replace_using_subexpr_filter(self, func): #e rename, since more like map than filter; subexpr_mapper??
        arg = self._e_constant_value #e another implem, maybe cleaner: store this data in _e_args; possible problems not reviewed
        modarg = func(arg)
        if modarg == arg:
            return self
        return self.__class__(modarg)
    pass

class eval_to_lval_Expr(internal_Expr):#070119, needed only when EVAL_REFORM
    """
    wrap a subexpr with me in order to cause _e_eval of me to only call _e_eval_lval on the subexpr
    """
    def _internal_Expr_init(self):
        ## (self._e_the_expr,) = self.args
        self._e_args = self.args # so replace sees the args
        assert len(self.args) == 1
    def _e_eval(self, env, ipath):
        assert env #061110
        the_expr = self._e_args[0] ## self._e_the_expr
        res = the_expr._e_eval_lval(env, ipath)
        ##e needs better __repr__ for its prints of self to be useful
        # print "fyi (routine): %r l-evals it to %r" % (self, res) # remove when works
        return res
    def _e_eval_lval(self, env, ipath):
        print "fyi or bug? %r didn't expect to have its _e_eval_lval called; just passing it through" % (self,)
            ## if that happens much and is not an error, remove the print once i understand why -- probably harmless
        return self._e_eval(env, ipath)
    pass

class property_Expr(internal_Expr): ##k guess, 061119, for attr 'open' in ToggleShow.py;
    # maybe just a kluge, since mixing properties with exprs is probably a temp workaround, tho in theory it might make sense...
    # if it can be rationalized then it's good to leave it in, maybe even encourage it. See also class State.
    """
    #doc; 
    canon_expr will turn a python property into this 
    (or maybe any misc data descriptor??)
    """
    def _internal_Expr_init(self):
        (self._e_property,) = self.args
    def __repr__(self):
        return "<%s#%d%s: %r>"% (self.__class__.__name__, self._e_serno, self._e_repr_info(), self._e_property,)
    def _e_eval(self, env, ipath):
        assert env #061110
        instance = env._self # AttributeError if it doesn't have this [###k uses kluge in widget_env]
            # if this ever fails, see comments about this construction in constant_Expr and lexenv_Expr -- it might be ok. [070118]
        prop = self._e_property
        clas = instance.__class__ ### MIGHT BE WRONG, not sure, might not matter unless someone overrides the prop attr, not sure...
        res = prop.__get__(instance, clas) #k is this right? we want to call it like the class would to any descriptor. seems to work.
        ## print "%r evals in %r to %r" % (self, instance, res)
        return res
    pass

class lexenv_Expr(internal_Expr): ##k guess, 061110 late
    """
    lexenv_Expr(env, expr) evals expr inside env, regardless of the passed env, but without altering the passed ipath.
    THIS BEHAVIOR IS INCORRECT AND WILL BE CHANGED SOON [070109 comment].
    It is opaque to replacement -- even by ExprsMeta, so it should never appear inside a class-attr value [##e should enforce that].
       WARNING [070106]: lexenv_Expr will have a major bug once we implement anything that can override dynamic env vars,
    since it should, but doesn't, inherit dynamic vars from the passed env rather than from its own env argument --
    only lexical vars should be overridden by the argument env. For more info see the discussion in widget_env.py docstring.
    To fix this bug, we need to know how to combine the lexical vars from the argument env with the dynamic ones from the passed env. ###
    """
    def _internal_Expr_init(self):
        (self._e_env0, self._e_expr0) = self.args
    def __repr__(self):
        return "<%s#%d%s: %r, %r>" % (self.__class__.__name__, self._e_serno, self._e_repr_info(),
                                      self._e_env0, self._e_expr0,)
    def _e_call_with_modified_env(self, env, ipath, whatever = 'bug'): # revised 070119
        """
        [private helper method] 
        Call self._e_expr0.<whatever> with lexenv self._e_env0 and [nim] dynenv taken from the given env
        """
        # about the lval code: #061204 semi-guess; works for now. _e_eval and _e_eval_lval methods merged on 070109.
        # Generalized to whatever arg for _e_make_in and revised accordingly (for sake of EVAL_REFORM), 070117.
        #e (should the val/lval distinction be an arg in the _e_eval API?
        #   maybe only for some classes, ie variant methods for fixed arg, another for genl arg??)
        expr, env, ipath = self._e_burrow_for_find_or_make( env, ipath) ###k more efficient than, and equiv to, _1step
        submethod = getattr(expr, whatever)
        res = submethod(env, ipath)
            #e if exception, print a msg that includes whatever?
        return res
    def _e_burrow_for_find_or_make(self, env, ipath): #070119
        """
        ###redoc, since redundant with Expr implem docstring:
        Return (expr, env, ipath) in an inner form, where expr has no outermost local ipath or env.
        [overrides trivial Expr version]
           Details: General case (Expr): Return (self, env, ipath) if self can be directly instantiated in env at ipath
        (i.e. if self will find or make itself at exactly that env and ipath, since self has no outermost local mods to them),
        or an equivalent-for-instantiation (subexpr, locally_modified_env, locally_modified_ipath) if not,
        where subexpr meets the condition described above, and is formed by stripping off outer env-mods and ipath-mods from self
        and adding them onto the passed env and ipath.
           This method implements that general case for lexenv_Expr and lexenv_ipath_Expr.
        """
        new_expr, new_env, new_ipath = self._e_burrow_for_find_or_make_1step( env, ipath)
        return new_expr._e_burrow_for_find_or_make( new_env, new_ipath)
    def _e_burrow_for_find_or_make_1step(self, env, ipath):
        """
        [private helper method for _e_burrow_for_find_or_make]
        """
        new_expr = self._e_expr0
        lexenv = self._e_env0
        # now we want to combine the dynamic part of env with the lexical part of lexenv, to make a modified newenv.
        new_env = env.dynenv_with_lexenv(lexenv) # env supplies the dynenv part of new_env, lexenv the lexenv part.
            # WARNING: this is initially a stub which returns lexenv, equiv to the old code here.
            # PROBLEM: new_env is perhaps often recreated with an equal but not identical value from the same inputs,
            #  but it's not memoized or change-tracked. It can't easily be changed-tracked ... maybe ipath finding handles this... ###k]
            #e Note: This might be renamed; might be turned into a helper function rather than a method
            ###e Q: does this ever need to modify ipath, eg move some of it into or out of dynenv?
            # I don't know; ipath can be thought of as part of the dynenv, so it's proper that it's passed on, anyway. [070118 comment]
        new_ipath = self._e_locally_modify_ipath(ipath) # differs for lexenv_Expr and lexenv_ipath_Expr
        return (new_expr, new_env, new_ipath)
    def _e_locally_modify_ipath(self, ipath):
        return ipath # differs for lexenv_Expr and lexenv_ipath_Expr
    # note: the following methods are similar in two classes
    def _e_eval(self, env, ipath):
        return self._e_call_with_modified_env(env, ipath, whatever = '_e_eval')
    def _e_eval_lval(self, env, ipath):
        return self._e_call_with_modified_env(env, ipath, whatever = '_e_eval_lval')
    def _e_make_in(self, env, ipath):
        assert EVAL_REFORM # since it only happens then
        return self._e_call_with_modified_env(env, ipath, whatever = '_e_make_in')
    pass # end of class lexenv_Expr

class lexenv_ipath_Expr(lexenv_Expr): #070118
    """
    #doc
    """
    #k Q: will this need to be Symbolic, so getattr_Expr can be formed from it?
    # A: I think not, since expr.attr should become a getattr_Expr only if expr "stands for an Instance",
    # like a Symbol or Arg() or Instance() does... this needs to be better understood, formalized, documented
    # (for example, those macros turn into some sort of OpExpr, not something which says specifically "I stand for an Instance").
    # This came up since some code had an expr of this class (lexenv_ipath_Expr) which it thought was an Instance,
    # and took bleft from it, getting an AttributeError -- but if this class formed getattr_Exprs there would have been
    # no exception at all. [070212]
    def _internal_Expr_init(self):
        (self._e_env0, self._e_local_ipath, self._e_expr0) = self.args
    def __repr__(self):
        return "<%s#%d%s: %r, %r, %r>" % (self.__class__.__name__, self._e_serno, self._e_repr_info(),
                                      self._e_env0, self._e_local_ipath, self._e_expr0,)
    def _e_locally_modify_ipath(self, ipath): # WARNING: dup code for this in local_ipath_Expr and here
        localstuff = self._e_local_ipath # for now, just include it all [might work; might be too inefficient]
        if 1:
            # they are getting too long for debug prints already! [070121 morn]
            intern_ipath( ipath) # no need to use the result of this interning; not using it will make debug prints more understandable
            localstuff2 = intern_ipath( localstuff) ###e optim: do this in init? is that equivalent?? I think so... ######e
            # print "interned %r to %r" % (localstuff, localstuff2) # works
            localstuff = localstuff2
        return (localstuff, ipath)
    pass # lexenv_ipath_Expr

class local_ipath_Expr(lexenv_Expr): #070122 experimental
    """
    experimental -- just add some local ipath components to the ipath -- no change in env
    """
    #e probably, these 3 classes should be reorg'd into abstract/mixin1/mixin2/3reals,
    # so the shared code for doing more stuff (to env or to ipath) comes from mixins
    def _internal_Expr_init(self):
        (self._e_local_ipath, self._e_expr0) = self.args
    def __repr__(self):
        return "<%s#%d%s: %r, %r>" % (self.__class__.__name__, self._e_serno, self._e_repr_info(),
                                      self._e_local_ipath, self._e_expr0,)
    def _e_burrow_for_find_or_make_1step(self, env, ipath):
        """
        [overrides lexenv_Expr implem]
        [private helper method for _e_burrow_for_find_or_make]
        """
        new_expr = self._e_expr0        
        new_env = env # differs from superclass
        new_ipath = self._e_locally_modify_ipath(ipath)
        return (new_expr, new_env, new_ipath)
    def _e_locally_modify_ipath(self, ipath):
        # WARNING: dup code from lexenv_ipath_Expr (differs from superclass)
        localstuff = self._e_local_ipath 
        if 1:
            intern_ipath( ipath)
            localstuff2 = intern_ipath( localstuff)
            localstuff = localstuff2
        return (localstuff, ipath)
    pass # local_ipath_Expr

class eval_Expr(OpExpr):
    """
    An "eval operator", more or less. For internal use only [if not, indices need to be generalized].
    Used when you need to put an expr0 inside some other expr1 where it will be evalled later,
    but you have, instead of expr0, expr00 which will eval to expr0. In such cases, you can put eval_Expr(expr00)
    in the place where you were supposed to put expr0, and when the time comes to eval that, expr00 will be evalled twice,
    in the same env and with appropriately differing indices.
    """
    def _e_init(self):
        pass
    def _e_call_on_argval(self, env, ipath, whatever = 'bug'):
        "[private helper method]"
        # same initial comment as in lexenv_Expr applies here [as of 070117]
        assert env #061110
        (arg,) = self._e_args
        ## argval = arg._e_eval(env, 'unused-index') # I think this index can never be used; if it can be, pass ('eval_Expr',ipath)
        index = 'eval_Expr(%s)' % whatever
        argval = arg._e_eval(env, (index, ipath)) #070109 this index can in fact be used, it turns out.
            # note: it's correct that we call arg._e_eval regardless of whatever being '_e_eval' or something else.
        try:
            submethod = getattr(argval, whatever)
            res = submethod(env, ipath)
                ###BUG (likely): if argval varies, maybe this ipath should vary with it -- but I'm not sure in what way.
                # We probably have to depend on argval to have different internal ipaths when it comes from different sources --
                # but presently that's nim (nothing yet wraps exprs with local-ipath-modifiers, tho e.g. If probably should),
                # so this might lead to incorrectly overlapping ipaths. It's not at all clear how to fix this in general,
                # and most likely, most uses of eval_Expr are kluges which are wrong in some way anyway, which this issue is
                # hinting at, since it seems fundamentally unfixable in general. [070109 comment]
                # update 070118: the plan is that argval will soon have a local-ipath-modifier as its outer layer,
                # which adds something to the ipath we pass to the submethod above, thus presumably solving the problem
                # (though until we intern exprs/ipaths and/or memoize the ipath->storage association, it might make things slower).
                # update 070122: but it doesn't yet solve it for testexpr_21e or _21g, in which an ad-hoc function returns an expr
                # based on a passed argument (according to a guess at the bug cause). See discussion near testexpr_21g.
        except:
            print "following exception concerns argval.%s(...) where argval is %r and came from evalling %r" % \
                  (whatever, argval, arg) #061118, revised 070109 & 070117
            raise
        ## print "eval_Expr eval%s goes from %r to %r to %r" % (_e_eval_lval and "_lval" or "", arg, argval, res) #untested since lval
        return res
    # note: the following methods are similar in two classes
    def _e_eval(self, env, ipath):
        return self._e_call_on_argval(env, ipath, whatever = '_e_eval')
    def _e_eval_lval(self, env, ipath):
        return self._e_call_on_argval(env, ipath, whatever = '_e_eval_lval')
    def _e_make_in(self, env, ipath):
        assert EVAL_REFORM # since it only happens then
        return self._e_call_on_argval(env, ipath, whatever = '_e_make_in')
    pass # end of class eval_Expr

##from VQT import V ###e replace with a type constant -- probably there's one already in state_utils
##V_expr = tuple_Expr ### kluge; even once this is defined, in formulas you may have to use V_expr instead of V,
    # unless we redefine V to not try to use float() on exprs inside it -- right now it's def V(*v): return array(v, Float)
    # (note: that Float is from numpy.oldnumeric and equals 'd')
    ##e (maybe we could make a new V def try to use old def, make __float__ asfail so that would fail, then use V_expr if any expr arg)

def canon_expr(subexpr):###CALL ME FROM MORE PLACES -- a comment in Column.py says that env.understand_expr should call this...
    """
    Make subexpr an Expr, if it's not already.
       Simple Python data (e.g. ints, floats, or None, and perhaps most Python class instances)
    will be wrapped with constant_Expr.
       Python lists or tuples (or dicts?##e) can contain exprs, and will become their own kind of exprs,
    or (as a future optim #e) will also be wrapped with constant_Expr if they don't contain exprs.
       (In future, we might also intern the resulting expr or the input expr. #e)
    """
    if is_Expr(subexpr): # whether pure expr or Instance
        # bruce 070914 removing the following, since I'm not using it
        # and it's causing some (runtime) import loops (Exprs <-> instance_helpers):
##        if is_Expr_pyclass(subexpr):
##            if debug_pref("wrap expr subclasses in constant_Expr?", Choice_boolean_False, prefs_key = True):
##                # new feature 070228; not sure if it ever came up before; if it did, this change might cause trouble;
##                # therefore print something whenever it's used, for now. In fact, it is likely to be misguided so I'll make it a debug_pref.
##                print "canon_expr treating this expr class as a constant: %r" % (subexpr,) ##e print_compact_stack?
##                assert same_vals(subexpr, subexpr)
##                return constant_Expr(subexpr)
##            elif debug_pref("pseudo-customize IorE subclasses?", Choice_boolean_False, prefs_key = True):
##                # turn it into an equivalent safer expr -- but only if it's in IorE
##                from exprs.instance_helpers import InstanceOrExpr #k safe??
##                if issubclass(subexpr, InstanceOrExpr):
##                    res = subexpr( _KLUGE_fakeoption = None )
##                    print "canon_expr turning expr class %r into %s" % (subexpr,res) #### remove when thought to be safe? printfyi?
##                    return res
##                else:
##                    print "canon_expr not changing expr class %r" % (subexpr,) ####
        if subexpr._e_serno == _debug_e_serno:
            print_compact_stack( "_debug_e_serno %d seen as arg %r to canon_expr, at: " % (_debug_e_serno, subexpr))
        return subexpr
            # true for Instances too -- ok?? [070122: see cmt in IorE._e_eval when EVAL_REFORM, which accomodates this]
##    ## elif issubclass(subexpr, Expr): # TypeError: issubclass() arg 1 must be a class
##    elif isinstance(subexpr, type) and issubclass(subexpr, Expr):
##        return subexpr # for _TYPE_xxx = Widget2D, etc -- is it ever not ok? ####k
    elif isinstance(subexpr, type([])):
        return list_Expr(*subexpr) ###k is this always correct? or only in certain contexts??
            # could be always ok if list_Expr is smart enough to revert back to a list sometimes.
        #e analogous things for tuple and/or dict? not sure. or for other classes which mark themselves somehow??
    elif isinstance(subexpr, type(())):
        return tuple_Expr(*subexpr) ###e should optim when it's entirely constant, like (2,3)
            # [needed for (dx,dy) in Translate(thing, (dx,dy)), 061111]
##    elif isinstance(subexpr, type(V(1,1.0))): ###e
##        # try to handle things like V(dx,dy) too... turns out this is not yet supportable, probably never.
##        # so this is more harmful than good -- a real V() is a constant, since it can't contain exprs anyway --
##        # if we redefine V to not require floats, we might as well go all the way to V_expr inside it.
##        printnim("kluge: turning V(expr...) into a tuple_Expr for now!") #####@@@@@
##        return tuple_Expr(*subexpr) #e replace with NumericArray_expr or V_expr or so
    elif isinstance(subexpr, property):
        res = property_Expr(subexpr)
        ## print "canon_expr wrapping property %r into %r" % (subexpr, res)
        return res
    else:
        #e assert it's not various common errors, like expr classes or not-properly-reloaded exprs
        #e more checks?
        # assume it's a python constant
        #e later add checks for its type, sort of like we'd use in same_vals or so... in fact, how about this?
        assert same_vals(subexpr, subexpr)
        ###e at first i thought: we should delve into it and assert you don't find Exprs... but delve in what way, exactly?
        # if you have a way, you understand the type, and then just handle it instead of checking for the unmet need to handle it.
        # we could let data objects tell us their subobjs like they do for Undo (I forget the details, some way of scanning kids)
        return constant_Expr(subexpr)
    pass

# ==

class Symbol(SymbolicExpr):
    """
    A kind of Expr that is just a symbol with a given name.
    Often used via the __Symbols__ module.
    """
    # Default values of instance variables.
    # These are normally set (optionally) after __init__, by the code that creates the symbols,
    # and never changed after that.
    _e_sym_constant = False # caller can set this to True if it's normal for this symbol to eval to itself (not deserving of warning)
    _e_eval_forward_to = _UNSET_ # caller can set this to something if it wants this symbol to evaluate to the same thing as that does.
    def __init__(self, name = None, doc = None):
        self._e_init_e_serno()
        if name is None:
            name = "?%s" % compact_stack(skip_innermost_n = 2).split()[-1] # kluge - show line where it's defined
        self._e_name = name
        self.__doc__ = doc # default is None, for a Symbol with no individual docstring.
            # (self.__doc__ can optionally be set by caller after we return)
        return
    def __str__(self):
        return self._e_name
    def __repr__(self):
        ## return 'Symbol(%r)' % self._e_name
        ##e should only use following form when name looks like a Python identifier!
        return 'S.%s' % self._e_name
    def __eq__(self, other): #k probably not needed, since symbols are interned as they're made
        return self.__class__ is getattr(other, '__class__', None) and self._e_name == other._e_name
            #070304 bugfix: survive not hasattr(other, '__class__') [maybe not tested since i'm not sure if this is ever used]
    def __ne__(self, other):
        return not (self == other)
    def _e_eval(self, env, ipath):
        """
        As with super _e_eval, our job is:
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
        # env ("drawing env") will let us grab attrs/opts in object, or things from dynenv as passed to any lexcontaining expr, i think...
        if self._e_eval_forward_to is not _UNSET_:
            printfyi("forwarding %r to value of %r" % (self, self._e_eval_forward_to))###
            return env._e_eval( self._e_eval_forward_to, ipath) #070131; note this forwarding is not overridable by env (experimental)
        val = env.lexval_of_symbol(self) # note: cares mainly or only about self._e_name; renamed _e_eval_symbol -> lexval_of_symbol
            # but I'm not sure it's really more lexenv than dynenv, at least as seen w/in env... [061028] ####@@@@
        # val is an intermediate value, needs further eval [this old comment might be wrong; see docstring -- 061105]
        if self == val:
            # return self (perhaps wrapped), after perhaps printing a warning
            if self is not val:
                print "warning: %r and %r are two different Symbols with same name, thus equal" % (self, val)
            if EVAL_REFORM:#070117
                if not self._e_sym_constant: #070131 added this cond (and attr)
                    print "warning: Symbol(%r) evals to itself [perhaps wrapped by _e_eval_to_expr]" % self._e_name
                return self._e_eval_to_expr(env, ipath, self)
            else:
                if not self._e_sym_constant: #070131 added this cond (and attr)
                    print "warning: Symbol(%r) evals to itself" % self._e_name
                return self
        # reached only when self != val
        assert self != val # remove when works
        if self._e_name not in ('_self', '_my', '_app'): #k Q: does this also happen for a thisname, _this_<classname> ?
            print "warning: _e_eval of a symbol other than _self or _my is not well-reviewed or yet well-understood:", self._e_name
                # e.g. what should be in env? what if it's an expr with free vars incl _self -- are they in proper context?
                # see docstring for more info [061105]
        ## pre-061105 code did: return val._e_eval(env, ipath)
        # and that might be needed for other syms -- not sure yet [061105]
        return val
    def _e_make_in(self, env, ipath):#070131
        assert self._e_sym_constant, "only constant Symbols can be instantiated, not %r" % self
        # and (at least for now) they instantiate to themselves, like other constants do
        return self
    def _e_free_in(self, sym): ###k might be obs [070131 comment]
        """
        General case: Return True if Expr self contains sym (Symbol or its name) as a free variable, in some arg or option value.
        For this class Symbol, that means: Return True if sym is self or self's name.
        [overrides super version]
        """
        return (sym is self) or (sym == self._e_name)
    pass # end of class Symbol

# note about Instance, Arg, Option, ArgOrOption, State -- they are now in another file to ease import-recursion issues.

# end

