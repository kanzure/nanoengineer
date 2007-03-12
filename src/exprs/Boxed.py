"""
Boxed.py -- example of high-level layout expr

$Id$
"""

from basic import *
from basic import _self

import Rect
reload_once(Rect)
from Rect import RectFrame

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import transforms
reload_once(transforms)
from transforms import Translate

import Center
reload_once(Center)
from Center import Center

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

# ==

class Boxed_old(InstanceMacro): ##e supers of (Widget2D, InstanceMacro) might be best, but I fear it won't work yet,
        # due to lack of proper super() use in those classes
##    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
##    Default options are borderthickness = 4, gap = 4, bordercolor = white.
##    [#e These can be changed in the env in the usual way. [nim]]
##    """
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
    pass # Boxed_old

class Boxed_old_070120(DelegatingInstanceOrExpr):
    "variant of Boxed_old with different delegation code, so I can see if that can fix testexpr_5 re EVAL_REFORM and kluge070119"
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
    delegate = Instance( Overlay( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor),
                      thing,
                      align = Center ) )
        # Note: as of 070121 late, due to changes in IorE, this explicit Instance() should no longer be needed (when EVAL_REFORM or not).
        # But that's only been tested in other classes and when EVAL_REFORM.
        #
        # older debug comments:
        # 070120 the bug in _5x EVAL_REFORM kluge070119 is lexbinding the _self in _self.ww in this expr
        # to Overlay (wrong), not Boxed_old (correct), but [i guess ##k] only when that kluge is turned on.
        # Can I put a debug wrapper on that subexpr, so that when its environment changes, we print the value of _self it sees?? ###e
        # We'd also want to print the stack, so we'd know when it went wrong. Two places to call that code:
        # when forming a new expr (maybe canon_expr could do it if it saw an exprflag requesting it and knew the parent expr's env)
        # or with specific calls to print debug info about certain exprs when some object realizes it's seeing one for the first time
        # (ie at special places in the code, like for each arg expr during _init_instance).
        # Problem: it might not be easy to burrow into exprs to see what env they provide their kids --
        # maybe we don't yet have any inspector-like methods for scanning kid exprs and knowing their envs.
        # But I guess we'd better add some! I think this is the best way to debug this if it doesn't turn out easier
        # (since this way is generally useful). I should make sure I can inspect by interactive cmdline in "debug text edit" window.
        # Basically every expr should give me a dict of subexpr data, key is index, value is an expr with info about env and ipath mods,
        # so I can descend into it by manually typing cmdlines with subexpr indices, or better yet an ipath-fragment.
        # But wait, index is for kid *Instance* not kidmaking *expr* -- hmm. They are not always systematically related.
        # The env and ipath are not even fixed for a given kidmaking expr (tho the lexenv should be, absent bugs).
        # For present purpose I only care about lexenv, and any understandable adhoc index of kidmaking exprs would do.
        # Is env_for_arg useful for this?
        
    pass # Boxed_old_070120
    
class CenterBoxedKluge_try1(Boxed_old): #e 061112/13 just for testing - fails, see comments for explan.
    ww = _self.ww # BUG. This might seem ok, since ww in superclass expanded to _self.ww anyway...
        # but won't it introduce some sort of infinite recursion, since looking up _self.ww will now get *this* rule?
        # Apparently yes:
        ## RuntimeError: maximum recursion depth exceeded
        ##  [lvals.py:160] [Exprs.py:192] [Exprs.py:336] [ExprsMeta.py:250] [ExprsMeta.py:321] [lvals.py:141] [lvals.py:158] [changes.py:318]
        # It would be desirable to fix that, but it's not trivial and not urgent (and not even obviously possible),
        # so I won't worry about it for now.
        # 
        # That means, if you use subclassing to incrementally add formulas, you can't say things like "ww = _self.ww" --
        # you just have to use _self.ww in place of each occurrence of ww, whenever ww comes from a superclass.
        #
        # (Or you could say ww1 = _self.ww, and then use ww1 in place of ww, but that's ugly.)
    hh = _self.hh
    _value = Overlay( Center(RectFrame( ww, hh, thickness = _self.borderthickness, color = _self.bordercolor)),                          
                      Center(_self.thing) )
    pass

class CenterBoxedKluge(InstanceMacro): #e 061112 try 2 -- just for testing (lots of dup code) -- works
        # (so Center works, at least this much -- IIRC it has some nim aspects too)
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
    _value = Instance( Overlay( Center( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor) ),
                      Center( thing ),
                       ))### see if Instance fixes ###EVAL_REFORM bug, 070118 935a --
        ## yes, and doesn't break non-EVAL_REFORM case either, w/ or w/o testbed, in testexpr_5b
    
    pass # CenterBoxedKluge

class Boxed(InstanceMacro):
    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
    Default options are pixelgap = 4 (in pixels), borderwidth = 4 (in pixels), bordercolor = white.
    [#e These can be changed in the env in the usual way. [nim]]
       WARNING: some deprecated but commonly used options are given in model units, not in pixels (probably a design flaw).
    """
    # WARNING: would not work if it inherited from Widget2D,
    # since it would pick up Widget2D default values for lbox attrs like btop. [unconfirmed but likely; 061127 comment]

    # args
    thing = Arg(Widget2D)
    
    # options
    borderwidth = Option(int, 4) # 070305 new feature -- specified in pixels
    borderthickness = Option(Width, borderwidth * PIXELS)
        # old alternative (worse since caller has to multiply by PIXELS); commonly used, but deprecated as of 070305
        # (warning: borderthickness is still used as an internal formula when not supplied)
        # (WARNING: supplying both forms is an error, but is not detected;
        #  this might cause bugs that are hard for the user to figure out
        #  if the different option forms were used in successive customizations of the same expr)
    
    pixelgap = Option(int, 4) # 070305 new feature [#e rename gap? bordergap? (change all gap options to being in pixels?)]
        # (maybe not yet tested with nonzero passed-in values)
    gap = Option(Width, pixelgap * PIXELS)
        # old alternative (worse since caller has to multiply by PIXELS), commonly used, but deprecated as of 070305
        # (see also the comments for borderthickness)
        # (warning: gap is still used as an internal formula when not supplied)
    
    bordercolor = Option(Color, white)
    
    # internal formulae
    extra1 = gap + borderthickness
    ww = thing.width  + 2 * extra1 #k I'm not sure that all Widget2Ds have width -- if not, make it so ##e [061114]
    hh = thing.height + 2 * extra1
    # appearance
    _value = Overlay( Translate( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor),
                                 - V_expr( thing.bleft + extra1, thing.bbottom + extra1) ), #e can't we clarify this somehow?
                      thing)
    def _init_instance(self): # needed solely for sanity check asserts, 061114
        super(Boxed, self)._init_instance()
        if not ( len(self._e_args) == 1):
            print("Boxed requires exactly one arg") #e need a more general mechanism for this; it's inferrable from the Arg decls
        # sanity checks 061114
        assert self.thing._e_is_instance
        ## print "%r._value is %r" % (self, self._value) # computing this now might change behavior, but only if there are bugs, I think
            ## <Boxed#0(i) at 0xe4a6550>._value is <Overlay#2497(i) at 0xe4a6510>
            ## bug: expr for instance changed: self = <Overlay#2497(i) at 0xe4a6510>, index = 0, ...
            ##   [so it *did* change behavior, i.e. by printing that -- presumably due to logic bug in DelegatingWidget2D;
            ##    I saw & understood that same bug in some other test a few days ago. Not clear if it changed behavior in other ways
            ##    in testexpr_7a... I guess it did since I don't see the delegating to non-instance warning anymore.
            ##     I guess I know why -- we stored the new expr but didn't inval the _i_instance_CVdict entry, so it used the old instance
            ##    which it made with a different expr, due to this debug code! Thus I'll disable the code and verify I still have the old bug,
            ##    since I want to try out the other sanity checks I added [061114 953p]. Oops, the code to disable is in Overlay, not (only) here!]
            ### is self._value going to be a pure expr or an instance? which *should* it be?
            # guess: orig intent was expr, but as realized days ago, for consistency it needs to be an instance,
            # and the diff of using the instance macro is in assigning a diff index,
            # and *might be* in holdness of its expr arg, and if so, that might be good or bad, it's not yet understood clearly.
            # but guess is that Instance(Rect()) should work, but if self.xx is a producer, Instance(xx) is unclear to me. [061114]
        return
    pass # Boxed

# ==

# more possibilities:
if 0:
    somth = [ff(i) for i in someattr._range] # workable if symexpr._range returns a list of one specially-typed symbol
    indexedattr = Indexed( lambda i: f(i)) # with more args/options about the range; should be workable; can CL use it for kids??

# end
