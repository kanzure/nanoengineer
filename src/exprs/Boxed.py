'''
Boxed.py -- example of high-level layout expr

$Id$
'''

from basic import *
from basic import _self

from Rect import RectFrame
from Overlay import Overlay

#e later import Center, when not a stub

# 061110 now that Overlay works with 2 args, what remains for this to work?
# - Overlay with align option
# - Center, to pass to that
# + verify RectFrame args & options used here are correct
# - _value needs to work (this is the only fundamentally new feature)
# - .width and .height need to be defined from layout box on any Widget2D
#   - and their use as named args in Rect needs to not be messed up by that
# What if we make _value work and ignore the rest?
# - Overlay will ignore the align option
# + RectFrame options still matter
# + .width and .height should work if they happen to be used internally in RectFrame
# - then it ought to work, except for looking wrong!
# So, plan: verify those things about RectFrame [done], implement _value ###, and make it work (looking wrong) as a test.
# First, what if I don't make _value work? Then I predict it will fail from lack of a draw method. Try it. Yes, that happens.
#
# Implem notes for _value [061110] [#e refile]:
# - Q: make it have an implicit Instance, I think -- or use a convention of adding one explicitly?
#   A: the convention, so it can work with other formulas too? no, they'd also need instantiation to work... not sure actually.###@@@
#   - BTW that might mean we get in trouble trying to pure-eval (which is what?) an Expr made from InstanceOrExpr, e.g. for a formula
#   to figure an iterator-expr to use in something else! We'll have to try that, and understand the semantics more clearly...
#   could it be that we'll have to explicitly Hold the exprs assigned to class attrs in cases like that?!?
# - where we use that _value is probably in _e_eval in InstanceOrExpr. (I still don't know if that and make_in are exactly the same.)
# - so we could do the instantiation in the place where we use it... then (later) test what happens if it's a number or so. (##e)
#   - (or what if the entire macro with its value is supposed to come up with a pure expr? test that too. ##e)
# So for now, just run the instantiation in the place we use it, in InstanceOrExpr._e_eval.
# But worry about whether InstanceOrExpr._e_make_in sometimes gets called instead by the calling code.
# Maybe better do it in whichever one has precedence when they both exist... that's _e_make_in (used in _CV__i_instance_CVdict).
# _e_eval just calls it, so that way it'll work in both. Ok, do it. ###
# WAIT, is it possible for the _value formula to vary with time, so that we want an outer instance,
# delegating to a variable inner one? (Perhaps memoizing them all sort of like GlueCodeMemoizer would do... perhaps only last one.)
# hmm... #### note that _make_in should pick up the same instance anyway, if it exists, but it looks to me like it might not!!! ###BUG
#
# let's try an explicit experiment, InstanceMacro:

class InstanceMacro(InstanceOrExpr, DelegatingMixin): #e refile if kept
    "#doc -- supports _value"
    #e might not work together with use by the macro of DelegatingMixin in its own way, if that's even possible
    delegate = Instance( _self._value, '!_value') #k guess: this might eval it once too many times... ####k
        #k note: I worried that using '_value' itself, as index, could collide with an index used to eval the expr version of _value,
        # in future examples which do that (though varying expr is not presently supported by Instance, I think -- OTOH
        # there can be two evals inside _i_instance due to eval_Expr, so the problem might arise that way, dep on what it does with
        # indices itself)
    pass

# ==

class Boxed(InstanceMacro): ##e supers of (Widget2D, InstanceMacro) might be best, but I fear it won't work yet,
        # due to lack of proper super() use in those classes
    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
    Default options are borderthickness = 4, gap = 4, bordercolor = white.
    [#e These can be changed in the env in the usual way. [nim]]
    """
    # args
    thing = Arg(Widget2D)
    # options
    borderthickness = Option(Width, 4 * PIXELS)
    gap = Option(Width, 4 * PIXELS)
    bordercolor = Option(Color, white)
    # internal formulas
    extra = 2 * gap + 2 * borderthickness
    ww = thing.width  + extra
    hh = thing.height + extra
    # value
    _value = Overlay( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor),                          
                      thing,
                      align = Center )
    pass

##class CenterBoxedKluge(Boxed): #e 061112 just for testing - fails, weird exceptions re ww and super
##    _value = Overlay( Center(RectFrame( ww, hh, thickness = borderthickness, color = bordercolor)),                          
##                      Center(thing) )
##    pass

class CenterBoxedKluge(InstanceMacro): #e 061112 just for testing -- lots of dup code
    # args
    thing = Arg(Widget2D)
    # options
    borderthickness = Option(Width, 4 * PIXELS)
    gap = Option(Width, 4 * PIXELS)
    bordercolor = Option(Color, white)
    # internal formulas
    extra = 2 * gap + 2 * borderthickness
    ww = thing.width  + extra
    hh = thing.height + extra
    # value
    _value = Overlay( Center( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor) ),                          
                      Center( thing ),
                       )
    pass
   
# ==

# more possibilities:
if 0:
    somth = [ff(i) for i in someattr._range] # workable if symexpr._range returns a list of one specially-typed symbol
    indexedattr = Indexed( lambda i: f(i)) # with more args/options about the range; should be workable; can CL use it for kids??

# end
