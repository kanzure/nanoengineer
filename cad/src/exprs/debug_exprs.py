# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

# == local imports with reload

from utilities.debug import safe_repr
from utilities.debug import print_compact_stack

from exprs.Exprs import internal_Expr ###k probably not needed (imported by basic) but needs test

from exprs.py_utils import printnim
from exprs.py_utils import printfyi
from exprs.instance_helpers import DelegatingMixin
from exprs.attr_decl_macros import Arg
from exprs.widget2d import Widget
from exprs.__Symbols__ import Anything

# ==

def getattr_debugprint(obj, attr): #070211; tested, though not usually in use
    """a version of getattr which does better debug printing on exceptions
    (use it as a drop-in replacement for 2-arg getattr to help with debugging)
    """
    try:
        return getattr(obj, attr)
    except AttributeError:
        print "getattr_debugprint: %s has no %r (reraising)" % (safe_repr(obj), attr)
        raise
    pass

class debug_evals_of_Expr(internal_Expr):#061105, not normally used except for debugging
    "wrap a subexpr with me in order to get its evals printed (by print_compact_stack), with (I hope) no other effect"
    def _internal_Expr_init(self):
        self._e_args = self.args # so replace sees the args
        assert len(self.args) == 1
    def _e_eval(self, env, ipath):
        assert env
        the_expr = self._e_args[0]
        res = the_expr._e_eval(env, ipath)
        print_compact_stack("debug_evals_of_Expr(%r) evals it to %r at: " % (the_expr, res)) # this works
        return res
    def _e_eval_lval(self, env, ipath):#070119 also print _e_eval_lval calls [maybe untested]
        assert env
        the_expr = self._e_args[0]
        res = the_expr._e_eval_lval(env, ipath)
        print_compact_stack("debug_evals_of_Expr(%r) eval-lvals it to %r at: " % (the_expr, res)) #k does this ever happen?
        return res
    pass

printnim("bug in DebugPrintAttrs, should inherit from IorE not Widget, to not mask what that adds to IorE from DelegatingMixin")###BUG
class DebugPrintAttrs(Widget, DelegatingMixin): # guess 061106; revised 061109, works now (except for ArgList kluge)
    """delegate to our arg, but print specified attrvalues before each draw call
    """
    #e might be useful to also print things like x,y,depth hitpoint window coords & 3d coords (see obs code DebugDraw, removed after cvs rev 1.3)
    delegate = Arg(Anything)
    ## attrs = ArgList(str) # as of 061109 this is a stub equal to Arg(Anything)
    attrs = Arg(Anything, [])
    def draw(self):
        guy = self.delegate
        print "guy = %r" % (guy, )
        ## attrs = self.args[1:]
        attrs = self.attrs
        if type(attrs) == type("kluge"):
            attrs = [attrs]
            printnim("need to unstub ArgList in DebugPrintAttrs")
        else:
            printfyi("seems like ArgList may have worked in DebugPrintAttrs")
        if 'ipath' not in attrs:
            attrs.append('ipath')#070118; not sure it's good
        for name in attrs:
            print "guy.%s is" % name, getattr(guy,name,"<unassigned>")
        return self.drawkid( guy) ## return guy.draw()
    pass

# end
