"""
$Id$
"""

# == local imports with reload

import basic
basic.reload_once(basic) # warning: this is only ok (I think) because it's not a recursive import, ie we're not imported by basic
del basic

from basic import *
from basic import _self, _this, _my

import Exprs
reload_once(Exprs)
from Exprs import internal_Expr ###k needed?

class debug_evals_of_Expr(internal_Expr):#061105, not normally used except for debugging # moved here from Exprs.py, 070119
    "wrap a subexpr with me in order to get its evals printed (by print_compact_stack), with (I hope) no other effect"
    def _internal_Expr_init(self):
        ## (self._e_the_expr,) = self.args
        self._e_args = self.args # so replace sees the args
        assert len(self.args) == 1
    def _e_eval(self, env, ipath):
        assert env #061110
        the_expr = self._e_args[0] ## self._e_the_expr
        res = the_expr._e_eval(env, ipath)
        print_compact_stack("debug_evals_of_Expr(%r) evals it to %r at: " % (the_expr, res)) # this works
        return res
    def _e_eval_lval(self, env, ipath):#070119 also print _e_eval_lval calls [maybe untested]
        assert env #061110
        the_expr = self._e_args[0] ## self._e_the_expr
        res = the_expr._e_eval_lval(env, ipath)
        print_compact_stack("debug_evals_of_Expr(%r) eval-lvals it to %r at: " % (the_expr, res)) #k does this ever happen?
        return res
    pass

# == debug code [moved from test.py to here, 070118]

printnim("bug in DebugPrintAttrs, should inherit from IorE not Widget, to not mask what that adds to IorE from DelegatingMixin")###BUG
class DebugPrintAttrs(Widget, DelegatingMixin):#k guess 061106; revised 061109, works now (except for ArgList kluge), ##e refile
    """delegate to our only arg, but whenever we're drawn, before drawing that arg,
    print its attrvalues listed in our other args
    """ #k guess 061106
    #e obscmt: won't work until we make self.args autoinstantiated [obs since now they can be, using Arg or Instance...]
    delegate = Arg(Anything) #k guess 061106
        #k when it said Arg(Widget): is this typedecl safe, re extensions of that type it might have, like Widget2D?
        #k should we leave out the type, thus using whatever the arg expr uses? I think yes, so I changed the type to Anything.
    ## attrs = ArgList(str) # as of 061109 this is a stub equal to Arg(Anything)
    attrs = Arg(Anything, [])
    def draw(self, *args): #e or do this in some init routine?
        ## guy = self.args[0] ##### will this be an instance?? i doubt it
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
##        ##DelegatingInstance_obs.draw(self, *args) # this fails... is it working to del to guy, but that (not being instance) has no .draw??
##        printnim("bug: why doesn't DelegatingInstance_obs delegate to guy?") # since guy does have a draw
##        # let's try it more directly:
        # super draw, I guess:
        return guy.draw(*args) ### [obs cmt?] fails, wrong # args, try w/o self
    pass

# == obs code

class DebugDraw_notsure(InstanceOrExpr,DelegatingMixin):
    """DebugDraw(widget, name) draws like widget, but prints name and other useful info whenever widget gets drawn.
    Specifically, it prints "gotme(name) at (x,y,depth)", with x,y being mouse posn as gluProject returns it.
    (It may print nonsense x,y when we're drawn during glSelect operations.)
    Once per event in which this prints anything, it prints mousepos first.
    If name is 0 or -1 or None, the debug-printing is disabled.
    """
    delegate = Arg(Widget)
    name = Arg(str, '')
    def draw(self):
        # who are we?
        who = who0 = ""
        if len(self._e_args) > 1:
            who0 = delegate
            who = "(%s)" % (who0,)
        if (who0 is not None) and who0 != 0 and who0 != -1:
##            # print "who yes: %r" % (who,), (who is not None), who != 0 , who != -1, 0 != 0
            if env.once_per_event('DebugDraw'):
                try:
                    printmousepos()
                except:
                    print_compact_traceback("ignoring exception in printmousepos(): ")
            # figure out where in the window we'd be drawing right now [this only works if we're not inside a display list]
            x,y,depth = gluProject(0,0,0)
            msg = "gotme%s at %r" % (who, (x,y,depth),)
            ## print_compact_stack(msg + ": ")
            print msg
##        else:
##            print "who no: %r" % (who,)
        self.delegate.draw()
    pass
DebugDraw = DebugPrintAttrs # not used as of long before 070118

# end
