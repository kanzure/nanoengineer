"""
current bugs [061013]:

- reload_once does it too often -- should be only when i do the reload effect from testmode/testdraw in cad/src
  (ie base it on that counter, not the redraw counter, but be sure that counter incrs before any imports)
- lots of things are nim, including drawtest1_innards

061113:
- auto reload is not working (even after touch *.py) when another file is modified and this one isn't, or so -- not sure when
but I think it used to be working...

$Id$
"""

#e during devel, see drawtest1_innards for main entry point from testdraw.py


# and old todo-list, still perhaps useful:
#
# Would it be useful to try to define several simple things all at once?

# Boxed, Rect, Cube, ToggleShow, Column/Row

# classify them:
# - 2d layout:
#   - Column/Row, Boxed, Checkerboard
# - has kids:
#   - Column
#   - all macros (since _value is a kid, perhaps of null or constant index)
#   - If [and its kids have to be lazy]
#   - Cube, Checkerboard
# - macro:
#   - ToggleShow, Boxed, MT
# - has state:
#   - ToggleShow
# - simple leaf:
#   - Rect
# - complicated options:
#   - Grid
# - complicated visible structure
#   - Cube, Grid, Checkerboard, MT
# - 3d layout
#   - Cube
# - iterator
#   - Cube, Checkerboard (and fancier: Table)

# first: Column, Boxed, Rect, If



# == imports from parent directory

# (none yet)

# == local imports with reload

import basic
basic.reload_once(basic)
del basic

from basic import * # including reload_once, and some stubs
from basic import _self, _this

import Rect
reload_once(Rect)
from Rect import Rect, RectFrame

import Column
reload_once(Column)
from Column import Column

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import Boxed
reload_once(Boxed)
from Boxed import Boxed_old, CenterBoxedKluge, CenterBoxedKluge_try1, Boxed

import Center
reload_once(Center)
from Center import Center, Translate

import TestIterator
reload_once(TestIterator)
from TestIterator import TestIterator

import TextRect
reload_once(TextRect)
from TextRect import TextRect

# == @@@

import widget_env
reload_once(widget_env)
from widget_env import widget_env

import instance_helpers
reload_once(instance_helpers)
from instance_helpers import DelegatingInstance_obs, DelegatingMixin # needed only in DebugPrintAttrs, which i should refile

# == make some "persistent state"

try:
    _state
except:
    _state = {}

# == debug code #e refile

class DebugPrintAttrs(Widget, DelegatingMixin):#k guess 061106; revised 061109, works now (except for ArgList kluge), ##e refile
    """delegate to our only arg, but whenever we're drawn, before drawing that arg,
    print its attrvalues listed in our other args
    """ #k guess 061106
    #e obscmt: won't work until we make self.args autoinstantiated [obs since now they can be, using Arg or Instance...]
    delegate = Arg(Anything) #k guess 061106
        #k when it said Arg(Widget): is this typedecl safe, re extensions of that type it might have, like Widget2D?
        #k should we leave out the type, thus using whatever the arg expr uses? I think yes, so I changed the type to Anything.
    attrs = ArgList(str) # as of 061109 this is a stub equal to Arg(Anything)
    def draw(self, *args): #e or do this in some init routine?
        ## guy = self.args[0] ##### will this be an instance?? i doubt it
        guy = self.delegate
        print "guy = %r, guy._e_is_instance = %r" % (guy, guy._e_is_instance)
        ## attrs = self.args[1:]
        attrs = self.attrs
        if type(attrs) == type("kluge"):
            attrs = [attrs]
            printnim("need to unstub ArgList in DebugPrintAttrs")
        else:
            printfyi("seems like ArgList may have worked in DebugPrintAttrs")
        for name in attrs:
            print "guy.%s is" % name, getattr(guy,name,"<unassigned>")
##        ##DelegatingInstance_obs.draw(self, *args) # this fails... is it working to del to guy, but that (not being instance) has no .draw??
##        printnim("bug: why doesn't DelegatingInstance_obs delegate to guy?") # since guy does have a draw
##        # let's try it more directly:
        # super draw, I guess:
        return guy.draw(*args) ### [obs cmt?] fails, wrong # args, try w/o self
    pass

# == testexprs

# === test basic leaf primitives
## testexpr_1 = Rect_old(7,5, color = green) # works as of 061030
    # [but Rect_old is obs, so I removed it 061113, tho it's probably the only test of _DEFAULT_ and _args, also obs]

testexpr_2 = Rect(8,6, color = purple) # works as of 061106

testexpr_2a = Rect(8,5, color = trans_red) # fails, since appears fully red ###BUG in translucent color support

# test not supplying all the args

testexpr_2b = Rect(4, color = purple) # works [061109]
testexpr_2c = Rect(color = purple) # asfail - guess, not has_args since this is just a customization 061109 ###BUG (make it work?)
testexpr_2d = Rect() # works, except default size is too big, since 10 makes sense for pixels but current units are more like "little"
testexpr_2e = Rect(4, 5, white) # works

# test non-int args
testexpr_2f = Rect(4, 2.6, blue) # works

#e test some error detection (nonunderstood option name, color supplied in two ways -- problem is, detecting those is nim)

#e test some formulas? e.g. a rect whose width depends on redraw_counter??

testexpr_3 = RectFrame(6,4) # works
testexpr_3a = RectFrame(6,4,color=blue) # works
testexpr_3b = RectFrame(6,4,thickness=5*PIXELS) # works
testexpr_3c = RectFrame(6,4,5*PIXELS,red) # works

# test DebugPrintAttrs (and thereby DelegatingMixin)
testexpr_3x = DebugPrintAttrs(Rect(4,7,blue), 'color') # works now! late 061109 (won't yet work with more than one attrname)

# === test more complex things

# Overlay (as of 061110 only implemented with exactly two args)

# these all work as expected, now that I know why Rect(1, white) doesn't work. After the commit I can clean it up. #e
testexpr_4 = Overlay( Rect(2), Rect(1, white) ) # might work since exactly two args; requires ArgList for more ###k test 061110
    # appears to work except that the white rect does not show; that's a bug, but for now, try a less ambiguous test:
testexpr_4a = Overlay( Rect(2,1), Rect(1, 2, white) ) # works; white rect is in front, but that didn't happen in test 4!! ####???
testexpr_4b = Rect(1.5, white) # could this be the problem? white is probably interpreted as a Width! (as 1) why no error?? ###e
printnim("the error of Color as Width in Rect(1.5, white) ought to be detected in draw_utils even before type coercion works")
testexpr_4c = Rect(1.5, color = white) # works
testexpr_4d = Overlay( Rect(2), Rect(1, color = white) ) # works!

# Boxed
testexpr_5 = Boxed_old( Rect(2,3.5,green)) # works as of 061110 late,
    # except for non-centering (and known nims re inclusion in bigger things), I think on 061111

testexpr_5a = Boxed_old( Center( Rect(2,3.5,green))) # sort of works, but alignment is wrong as expected [still as of 061112]
testexpr_5b = CenterBoxedKluge( Rect(2,3.5,yellow)) # works, 061112 827p
testexpr_5c_exits = CenterBoxedKluge_try1( Rect(2,3.5,orange)) # 061113 morn - fails (infrecur in lval -> immediate exit), won't be fixed soon
testexpr_5d = Boxed( Rect(2,3.5,purple)) # 061113 morn - works; this should become the official Boxed, tho its internal code is unclear

# TextRect, and _this
testexpr_6a = TextRect("line 1\nline 2", 2,8) # works
    # note, nlines/ncols seems like the right order, even though height/width goes the other way
testexpr_6b = TextRect("line 3\netc", 2) # works except for wrong default ncols
testexpr_6c = TextRect("line 4\n...") # works except for wrong defaults

testexpr_6d = TextRect("%r" % _self.ipath) # bug: Expr doesn't intercept __mod__(sp?) -- can it?? should it?? not for strings. ######
testexpr_6e = TextRect(format_Expr("%r", _self.ipath),4,60) # incorrect test: _self is not valid unless we're assigned in some pyclass
    # (so what it does is just print the expr's repr text -- we can consider it a test for that behavior)
    # (note: it tells us there's a problem by printing "warning: Symbol('_self') evals to itself")

testexpr_6f = TextRect(format_Expr( "%r", _this(TextRect).ipath ),4,60) # printed ipath is probably right: 'NullIPath' ###k verify
    # obs cmt (correct but old, pre-061114):
    # PRETENDS TO WORK but it must be the wrong thing's ipath,
    # since we didn't yet implem finding the right thing in _this!! [061113 934p]
    # Guess at the cause: I wanted this to be delegated, but that won't work since it's defined in the proxy (the _this object)
    # so __getattr__ will never run, and will never look for the delegate. This problem exists for any attr normally found
    # in an InstanceOrExpr. Solution: make it instantiate/eval to some other class, not cluttered with attrs. [done now, 061114]
    # 
    # update 061114: now it works differently and does find right thing, but the printed ipath looks wrong [WRONG - it's not wrong]
    # Is it ipath of the pure expr (evalled too soon),
    # or is the ipath (of the right instance) wrong? Or are we asking too early, before the right one is set?
    # How can I find out? [061114 152p]
    # A: it wasn't wrong, it was the top expr so of course it was None -- now I redefined it to  'NullIPath'.
    # But a good test is for an expr in which it's not None, so try this, which will also verify ipaths are different:
testexpr_6f2 = Overlay(testexpr_6f, Translate(testexpr_6f, (0,-2))) # works!
    
testexpr_6g = TextRect(format_Expr( "%r", _this(TextRect) ),4,60) # seems to work, 061114
testexpr_6g2 = TextRect(format_Expr( "%r", (_this(TextRect),_this(TextRect)) ),4,60) # should be the same instance - works (best test)

testexpr_6h = TextRect(format_Expr( "%r", _this(TextRect)._e_is_instance ),4,60) # unsupported.
    # prints False; wrong but not a bug -- ._e_* is unsupportable on any symbolic expr.
    # Reason (not confirmed by test, but sound):
    # it never even forms a getattr_Expr, rather it evals to False immediately during expr parsing.
testexpr_6h2 = TextRect(format_Expr( "%r", getattr_Expr(_this(TextRect),'_e_is_instance') ),4,60) # works (prints True)
## testexpr_6i = TextRect(format_Expr( "%r", _this(TextRect).delegate ),4,60) # attrerror, not a bug since TextRects don't have it

testexpr_6j = TextRect(format_Expr( "%r", (_this(TextRect),_this(TextRect).ncols) ),4,60) # works: prints (<textrect...>, 60)

    #e more kinds of useful TextRect msg-formulae we'd like to know how to do: 
    #e how to access id(something), or env.redraw_counter, or in general a lambda of _self

# TestIterator (test an iterator - next up, 061113/14)
testexpr_7 = TestIterator( testexpr_3 ) # looks right, but it must be faking it (eg sharing an instance?) ###
# note: each testexpr_6f prints an ipath
testexpr_7a = TestIterator( Boxed(testexpr_6f) ) # crashes 
testexpr_7b = Boxed(testexpr_6f) # works (and led to an adjustment of PIXELS to 0.035 -- still not precisely right -- not important)
testexpr_7c = Boxed(testexpr_7b) # works as of 061114 noon or so.
testexpr_7d = Boxed(testexpr_7c) # works (3 nested Boxeds).

# Column
testexpr_8 = Column( Rect(4, 5, white), Rect(1.5, color = blue)) # doesn't work yet (finishing touches in Column, instantiation)

# ToggleShow
testexpr_9 = ToggleShow( testexpr_2 ) # test use of Rules, If, toggling...



# === set the testexpr to use right now   @@@

testexpr = testexpr_7d
    # latest stable test: testexpr_5d, and testexpr_6f2
    # currently under devel [061113 937p]: testexpr_6f et al (see BUG comments above);
    # when it works, continue impleming _7
    # ... after extensive changes for _this [061113 932p], should retest all -- for now did _3x, _5d, _6a thru _6e, and 061114 6g*, 6h*


# buglike note 061112 829p with _5a: soon after 5 reloads it started drawing each frame twice
# for no known reason, ie printing "drew %d" twice for each number; the ith time it prints i,i+1. maybe only after mouse
# once goes over the green rect or the displist text (after each reload)? not sure.


print "using testexpr %r" % testexpr
for name in dir():
    if name.startswith('testexpr') and name != 'testexpr' and eval(name) is testexpr:
        print "(which is probably %s)" % name

# == per-frame drawing code

def drawtest1_innards(glpane):
    "entry point from ../testdraw.py"
    ## print "got glpane = %r, doing nothing for now" % (glpane,)

    glpane
    staterefs = _state ##e is this really a stateplace? or do we need a few, named by layers for state?
        #e it has: place to store transient state, ref to model state
    some_env = widget_env(glpane, staterefs) #####@@@@@@ IMPLEM more args, etc, and import it

    inst = some_env.make(testexpr, NullIpath)
    from basic import printnim, printfyi
    printnim("severe anti-optim not to memoize some_env.make result in draw") ###e but at least it ought to work this way
    inst.draw()
    import env
    print "drew", env.redraw_counter
    return


# old comments:

# upon reload, we'll make a new env (someday we'll find it, it only depends on glpane & staterefs),
# make an instance of testexpr in it, set up to draw that instance.

# this is like making a kid, where testexpr is the code for it.

# when we draw, we'll use that instance.

# problem: draw is passed glpane, outer inst doesn't have one... but needs it...
# what's justified here? do we store anything on glpane except during one user-event?
# well, our knowledge of displists is on it... lots of cached objs are on it...

# OTOH, that might mean we should find our own stores on it, with it passed into draw --
# since in theory, we could have instances, drawable on several different renderers, passed in each time,
# some being povray files. these instances would have their own state....

# OTOH we need to find persistent state anyway (not destroyed by reload, that's too often)

# some state is in env.prefs, some in a persistent per-session object, some per-reload or per-glpane...

try:
    session_state
    # assert it's the right type; used for storing per-session transient state which should survive reload
except:
    session_state = {}

per_reload_state = {}

# also per_frame_state, per_drag_state ... maybe state.per_frame.xxx, state.per_drag.xxx...

# end
