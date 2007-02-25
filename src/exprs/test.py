"""
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

import changes
changes._debug_standard_inval_nottwice_stack = False
changes._debug_standard_inval_twice = False # WARNING: this hides the pseudobug [061207]
changes._debug_standard_inval_twice_stack = False

# == local imports with reload

import basic
basic.reload_once(basic)
del basic

from basic import * # including reload_once, and some stubs
from basic import _self, _this, _my, _app

import Rect
reload_once(Rect)
from Rect import Rect, RectFrame, IsocelesTriangle, Spacer, Sphere

import Column
reload_once(Column)
from Column import SimpleColumn, SimpleRow # no longer includes still-nim Column itself [070129]

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import Boxed
reload_once(Boxed)
from Boxed import Boxed_old, Boxed_old_070120, CenterBoxedKluge, CenterBoxedKluge_try1, Boxed

import transforms
reload_once(transforms)
from transforms import Translate, Closer

import Center
reload_once(Center)
from Center import * # e.g. Center, TopRight, CenterRight, Right; not yet complete, mostly working (see specific tests) [061211 112p] 

import TestIterator
reload_once(TestIterator)
from TestIterator import TestIterator, TestIterator_wrong_to_compare

import TextRect
reload_once(TextRect)
from TextRect import TextRect

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable, Button, print_Expr, _setup_UNKNOWN_SELOBJ

import ToggleShow
reload_once(ToggleShow)
from ToggleShow import ToggleShow

import images
reload_once(images)
from images import Image, IconImage, PixelGrabber

import controls
reload_once(controls)
from controls import ChoiceButton, ChoiceColumn, ChoiceRow, checkbox_v3, checkbox_pref, ActionButton, PrintAction
    #e rename some of these?

import staterefs
reload_once(staterefs)
from staterefs import PrefsKey_StateRef

import Set
reload_once(Set)
from Set import Set ##e move to basic

import demo_MT
reload_once(demo_MT)
from demo_MT import test_drag_pixmap, MT_try2

# MT_try1 was moved to this outtakes file 070210; it's still importable from there and works in testexpr_18
# (verified in test.py cvs rev 1.224), but since it's obs, we'll no longer import it (thus breaking all tests
# using MT_try1 unless you reenable this import).
if 0:
    import demo_MT_try1_obs
    reload_once(demo_MT_try1_obs)
    from demo_MT_try1_obs import MT_try1
else:
  MT_try1 = Stub

import demo_drag
reload_once(demo_drag)
from demo_drag import GraphDrawDemo_FixedToolOnArg1, kluge_dragtool_state_checkbox_expr, demo_drag_toolcorner_expr_maker

import projection
reload_once(projection)
from projection import DrawInCorner1, DrawInCorner

import ModelNode # as of 061215 450p this import fails (no consistent MRO) but causes no other problems
    # (it did on try1 but that was after lots of file edits in a running session, and didn't repeat in a new session)
reload_once(ModelNode)
from ModelNode import Sphere_ExampleModelNode ###stub or wrong, not yet used [061215]

import DisplistChunk # works 070103, with important caveats re Highlightable (see module docstring)
reload_once(DisplistChunk)
from DisplistChunk import DisplistChunk

##import demo_polygon # stub 070103
    # commented out 070117 since it's a scratch file with syntax errors
    # [and it was renamed 070125 from demo_dna.py]
##reload_once(demo_polygon)
##from demo_polygon import newerBoxed, resizablyBoxed

import lvals
reload_once(lvals)
from lvals import Lval_which_recomputes_every_time ##e and more? refile in basic??

import widget_env
reload_once(widget_env)
from widget_env import widget_env

import debug_exprs
reload_once(debug_exprs)
from debug_exprs import DebugPrintAttrs

import dna_ribbon_view
reload_once(dna_ribbon_view)
from dna_ribbon_view import DNA_Cylinder, dna_ribbon_view_toolcorner_expr_maker, World_dna_holder

import draggable
reload_once(draggable)
from draggable import DraggableObject

# ==

from OpenGL.GL import glPopMatrix, glPushMatrix # needed in drawtest1_innards

# == make some "persistent state"

try:
    _state
except:
    _state = {} ###e Note: this is used for env.staterefs as of bfr 061120; see also session_state, not yet used, probably should merge

# == testexprs

# === test basic leaf primitives
## testexpr_1 = Rect_old(7,5, color = green) # works 061030; removed 061113 since obs (tho only test of obs _DEFAULT_ and _args)

testexpr_2 = Rect(8,6, color = purple) # works as of 061106

testexpr_2a = Rect(8,5, color = trans_red) # fails, since appears fully red ###BUG in translucent color support

# test not supplying all the args

testexpr_2b = Rect(4, color = purple) # works [061109]
testexpr_2c = Rect(color = purple) # works; had warning from no explicit args until 070121 (still warns minimally for now)
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

def FilledSquare(fillcolor, bordercolor, size = 0.5, thickness_ratio = 0.05): # 061115 direct copy from cad/src/testdraw.py
    return Overlay( Rect(size, size, fillcolor),
                    RectFrame(size, size, size * thickness_ratio, bordercolor)
    )

testexpr_3y = FilledSquare(purple, blue) # works, except top border quantized to 0 pixels thick, others to 1 (not surprising)

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
    # failed in EVAL_REFORM but that got fixed 070117 1012p, see comments below

testexpr_5x = Boxed_old_070120( Rect(2,3.5,pink)) # 070120 variant of testexpr_5 -- to try in EVAL_REFORM kluge070119 -- ###

testexpr_5a = Boxed_old( Center( Rect(2,3.5,green))) # sort of works, but alignment is wrong as expected [still as of 061112]
testexpr_5b = CenterBoxedKluge( Rect(2,3.5,yellow)) # works, 061112 827p
testexpr_5c_exits = CenterBoxedKluge_try1( Rect(2,3.5,orange)) # 061113 morn - fails (infrecur in lval -> immediate exit), won't be fixed soon
testexpr_5d = Boxed( Rect(2,3.5,purple)) # 061113 morn - works; this should become the official Boxed, tho its internal code is unclear

# TextRect, and _this
testexpr_6a = TextRect("line 1\nline 2", 2,8) # works
    # note, nlines/ncols seems like the right order, even though height/width goes the other way
testexpr_6b = TextRect("line 3\netc", 2) # works except for wrong default ncols
testexpr_6c = TextRect("line 4\n...") # works except for wrong defaults -- now nlines default is fixed, 061116

testexpr_6d = TextRect("%r" % _self.ipath) # bug: Expr doesn't intercept __mod__(sp?) -- can it?? should it?? not for strings. ######
testexpr_6e = TextRect(format_Expr("%r", _self.ipath),4,60) # incorrect test: _self is not valid unless we're assigned in some pyclass
    # (so what it does is just print the expr's repr text -- we can consider it a test for that behavior)
    # (note: it tells us there's a problem by printing "warning: Symbol('_self') evals to itself")
    # Update 070118: in EVAL_REFORM, this has an exception, AttributeError: 'lexenv_Expr' object has no attribute 'ipath',
    # about the bare symbol _self wrapped with a lexenv_Expr. I think that's ok, since it's an error in the first place.
    # Maybe the error behavior could be improved, but we can ignore that for now.

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

# Boxed   (_7 and _7a were TestIterator, now deferred)
testexpr_7b = Boxed(testexpr_6f) # works (and led to an adjustment of PIXELS to 0.035 -- still not precisely right -- not important)
testexpr_7c = Boxed(testexpr_7b) # works as of 061114 noon or so. (2 nested Boxeds)
testexpr_7d = Boxed(testexpr_7c) # works (3 nested Boxeds)

# SimpleColumn & SimpleRow [tho out of testexpr_7*, TestIterator doesn't work yet, only nested Boxed does]
testexpr_8 = SimpleColumn( testexpr_7c, testexpr_7b ) # works (gap is ok after Translate lbox fixed)
testexpr_8a = SimpleColumn( testexpr_7c, testexpr_7c, pixelgap = 0 ) # works (gap is ok after Translate lbox fixed)
testexpr_8b = SimpleColumn( Rect(1,1,blue), Rect(1,1,red), pixelgap = 1 ) # works (with pixelgap 2,1,0,-1)
testexpr_8c = SimpleColumn( Rect(1,1,blue), None, Rect(1,1,orange), pixelgap = 1 ) # None-removal works, gap is not fooled

testexpr_8d = SimpleRow( Rect(1,1,blue), None, Rect(1,1,orange), pixelgap = 1 ) # works
testexpr_8e = SimpleRow( Rect(1,1,blue), Rect(2,2,orange), pixelgap = 1 ) # works
testexpr_8f = SimpleRow(SimpleColumn(testexpr_8e, testexpr_8e, Rect(1,1,green)),Rect(1,1,gray)) # works

# [don't forget that we skipped TestIterator above -- I think I can safely leave iterators unsolved, and fancy Column unfinished,
#  while I work on state, highlighting, etc, as needed for ToggleShow and MT-in-GLPane [061115]]
# [warning: some commits today in various files probably say 061114 but mean 061115]

# Highlightable, primitive version [some egs are copied from cad/src/testdraw.py, BUT NOT YET ALL THE PRIMS THEY REQUIRE ##e]

testexpr_9a = Highlightable(
                    Rect(2, 3, pink),
                    # this form of highlight (same shape and depth) works from either front or back view
                    Rect(2, 3, orange), # comment this out to have no highlight color, but still sbar_text
                    # example of complex highlighting:
                    #   Row(Rect(1,3,blue),Rect(1,3,green)),
                    # example of bigger highlighting (could be used to define a nearby mouseover-tooltip as well):
                    #   Row(Rect(1,3,blue),Rect(2,3,green)),
                    sbar_text = "big pink rect"
                )
                # works for highlighting, incl sbar text, 061116;
                # works for click and release in or out too, after fixing of '_self dflt_expr bug', 061116.

if 'stubs 061115':
    Translucent = identity

testexpr_9b = Button(
                    ## Invisible(Rect(1.5, 1, blue)), # works
                    Translucent(Rect(1.5, 1, blue)), # has bug in Translucent
                    ## IsocelesTriangle(1.6, 1.1, orange),
                        # oops, I thought there was an expanding-highlight-bug-due-to-depthshift-and-perspective,
                        # but it was only caused by this saying 1.6, 1.1 rather than 1.5, 1!
                    Rect(1.5, 1, orange),
                      ## Overlay( Rect(1.5, 1, lightgreen) and None, (IsocelesTriangle(1.6, 1.1, orange))),
                        ###@@@ where do I say this? sbar_text = "button, unpressed"
                        ##e maybe I include it with the rect itself? (as an extra drawn thing, as if drawn in a global place?)
                    IsocelesTriangle(1.5, 1, green),
                    IsocelesTriangle(1.5, 1, yellow),#e lightgreen better than yellow, once debugging sees the difference
                        ###@@@ sbar_text = "button, pressed", 
                    # actions (other ones we don't have include baremotion_in, baremotion_out (rare I hope) and drag)
                    on_press = print_Expr('pressed'),
                    on_release_in = print_Expr('release in'), # had a bug (did release_out instead), fixed by 'KLUGE 061116'
                    on_release_out = print_Expr('release out')
                )   # using 'stubs 061115':
                    # - highlighting works
                    # - button aspect (on_* actions) was not yet tested on first commit; now it is,
                    #   and each action does something, but on_release_in acted like on_release_out,
                    #   but I fixed that bug.
                    ###e should replace colors by text, like enter/leave/pressed_in/pressed_out or so
                # update 070118, with no testbed and EVAL_REFORM turned off: still works, but prints
                # debug_pref: preDraw_glselect_dict failure ... whenever mouse goes off or on while it's pressed.
                # That's probably not a bug, but it might be worth understanding re other bugs in highlighting system.
                # Guess: the selobj is out of date but still used in some way.
                # update 070212: still works after unstubbing IsocelesTriangle (before now it was equal to Rect).

testexpr_9c = SimpleColumn(testexpr_9a, testexpr_9b) # works (only highlighting tested; using 'stubs 061115')

testexpr_9d = testexpr_9b( on_release_in = print_Expr('release in, customized')) # works
    # test customization of option after args supplied

testexpr_9e = testexpr_9b( on_release_in = None) # works
    # test an action of None (should be same as a missing one) (also supplied by customization after args)

testexpr_9cx = SimpleColumn(testexpr_9a, testexpr_9b(projection = True)) # works 070118?? before that -- ###BUG -- that option breaks the functionality.
    # guess: it might mess up the glselect use of the projection matrix. (since ours maybe ought to be multiplied with it or so)
    #
    # ... update 070118: if I understand this correctly, it's working now (EVAL_REFORM off or on both work, with no testbed).
    # I don't know why/how/ifreally it got fixed, but maybe it did, since I did a few things to highlighting code since that time,
    # including not using that z-offset kluge in the depth test, changing to GL_LEQUAL (with different Overlay order), maybe more.
    # OTOH I didn't review this code now -- maybe all that happened is I disabled that projection option somehow. Who knows. #k
    # BTW it has lots of debug prints like <Highlightable#146280(i)> (projection=True) not saving due to current_glselect.
    # I don't know if it always did.


testexpr_9f = Highlightable( Rect(color = If_expr(_this(Highlightable).env.glpane.in_drag, blue, lightblue))) # fails, silly reason
    ## AssertionError: this expr needs its arguments supplied: <Rect#0(i w/o a)>
    # I turned that into a warning, but it fails later (ends up trying to draw_filled_rect with color = If_expr(...)),
    # perhaps because destructive_supply_args never ran -- just a speculation, but I can't see anything else that could differ.
    # Hmm, maybe the bug will occur even if I supply the args?!? Try that now:
testexpr_9fx1 = Rect(color = If_expr(_my.env.glpane.in_drag, blue, lightblue)) # still fails (expected)
    # _my is ok since everyone's glpane is the same!
    # This has the same ###BUG!!! Hmm, why doesn't that expr get evalled? Oh, duh, I forgot to supply the args. Ok, this is the control experiment.
testexpr_9fx2 = Rect(color = If_expr(_my.env.glpane.in_drag, blue, lightblue))() # still fails
    # This has the same bug, and does have args and no longer complains it doesn't! So some code to eval If_expr or _my is missing.
testexpr_9fx3 = Rect(1, 1, If_expr(_my.env.glpane.in_drag, blue, lightblue)) # try it with args supplied at same time, and color not an option -- still fails;
    # after I overrode _e_eval in If_expr it sort of works but gets stuck at true state, but maybe in_drag itself gets stuck (in rubberband selrect)??
    # hard to say; double-click makes it 0, using atoms makes it 1 again...
    # note that I was wrong that glpane.in_drag would be ok for this application instead of something about _this(Highlightable) --
    # it's true about *any* drag, not only about a drag of that object -- not what I intended. Even so it ought to work.
    # It might be failing due to lack of inval when in_drag changes, of course. Try adding another draggable somewhere?
    # No, dragging around on a TextRect causes lots of redraws, but no reprints of "<If_expr#19096(a)> gets cond 1"! Why?
    # Because something contains its value and didn't usage-track anything which we're invalidating here! AHA. ######BUG
    # That can be fixed by referring to trackable state, provided it's not _i_instance_dict or whatever which fails to track this eval anyway. Try it.
testexpr_9fx4 = Highlightable( Rect(1, 1, If_expr(_this(Highlightable).transient_state.in_drag, blue, lightblue))) # works, if I
    # remember to click rather than just to mouseover -- the code says in_drag, not in_bareMotion!
        ##e should make an abbrev for that attr as HL.in_drag -- maybe use State macro for it? read only is ok, maybe good.
        ##e should add an accessible attr for detecting whether we're over it [aka in_bareMotion -- not a serious name-suggestion].
        # What to call it?
    # Q, 070118: Does that mean all the comments in _9f thru _9f3 are mistaken, as if mouseover == drag???
    # Or did I click in those tests?
    # 070122 update: I don't know if it means that, but recently they failed in EVAL_REFORM but this is probably expected.
    # This one, testexpr_9fx4, had a bug in ER, apparently due to no local ipath mod, fixed some days ago by adding one. So it works now.
    
testexpr_9fx5 = Highlightable( Rect(color = If_expr(_this(Highlightable).transient_state.in_drag, blue, lightblue))) # works with warning
    # so it turns out the If_expr was a total red herring -- once fixed, the no-args form now warns us, but works anyway.
testexpr_9fx6 = Highlightable( Rect(color = If_expr(_this(Highlightable).transient_state.in_drag, purple, lightblue))() ) # works

                               
# ToggleShow
testexpr_10a = ToggleShow( Rect(2,3,lightgreen) ) # test use of Rules, If, toggling... works
testexpr_10b = ToggleShow( Highlightable(Rect(2,3,green)) ) # use Highlightable on rect - avoid redraw per mousemotion on it - works
testexpr_10c = ToggleShow(ToggleShow( Highlightable(Rect(2,3,green)) )) # works
testexpr_10d = ToggleShow(ToggleShow( Rect(2,3,yellow) )) # works
    # [all still work [on g4] after StatePlace move, 061126 late; _10c also tested on g5, works]
    # [also ok on g4: all of _11 & _12 which I retried]

# Image

from testdraw import courierfile
blueflake = "blueflake.jpg"

testexpr_11a = Image(courierfile) # works
testexpr_11a1 = Image("courier-128.png") # works (note: same image)
testexpr_11a2 = Image(blueflake) # works [and no longer messes up text as a side effect, now that drawfont2 binds its own texture]
    # WARNING: might only work due to tex size accident -- need to try other sizes
testexpr_11b = SimpleRow( Image(blueflake), Image(courierfile) ) # works (same caveat about tex size accidents applies, re lbox dims)
testexpr_11c = SimpleColumn( Image(courierfile), Image(blueflake), pixelgap=1 ) # works
testexpr_11d = SimpleRow(
    SimpleColumn( Image(courierfile), Image(blueflake), pixelgap=1 ),
    SimpleColumn( Image(blueflake), Image(courierfile), pixelgap=1 ), pixelgap=1
    ) # works
testexpr_11d2 = SimpleColumn(
    SimpleColumn( Image(courierfile), Image(blueflake), pixelgap=1 ),
    SimpleColumn( Image(blueflake), Image(courierfile), pixelgap=1 ),
    ) # works
testexpr_11d3 = SimpleColumn(
    SimpleRow( Image(courierfile), Image(blueflake), pixelgap=1 ),
    SimpleRow( Image(blueflake), Image(courierfile), pixelgap=1 ),
    ) # works; but suffers continuous redraw as mouse moves over image
        # (as expected; presumably happens for the others too, and for all other tests, not just images; seen also for Rect)
        ##e we need a general fix for that -- should all these leafnodes allocate a glname if nothing in their surroundings did??
testexpr_11d4 = SimpleRow(
    SimpleRow( Image(courierfile), Image(blueflake), pixelgap=1 ),
    SimpleRow( Image(blueflake), Image(courierfile), pixelgap=1 ),
    ) # works
testexpr_11e = ToggleShow( testexpr_11a2) # works; continuous redraw as mouse moves over image (as expected)
testexpr_11f = ToggleShow( Highlightable( testexpr_11a)) # works; no continuous redraw (as expected)

testexpr_11g = Image(blueflake, nreps = 2) # works; this series is best viewed at zoom of 3 or so [061126]
testexpr_11h = Image(blueflake, clamp = True, nreps = 3, use_mipmaps = True) # works (clamping means only one corner has the image)
testexpr_11i = testexpr_11h(pixmap = True) # works (reduced fuzziness) [note: this customizes an option after args supplied]
    # note: there is probably a bug in what Image texture options do to subsequent drawfont2 calls. [as of 061126 noon; not confirmed]
    # note: defaults are clamp = False, use_mipmaps = True, decal = True, pixmap = False;
    #   the options not tried above, or tried only with their defaults, are not yet tested -- namely,
    #   untested settings include use_mipmaps = False, decal = False [nim].
testexpr_11j = testexpr_11h(use_mipmaps = False) # DOESN'T WORK -- no visible difference from _11i. #####BUG ???

testexpr_11k = testexpr_11h(tex_origin = (-1,-1)) # works; latest stable test in _11 (the rest fail, or are bruce-g4-specific, or ugly)

# try other sizes of image files

## testexpr_11l_asfails = testexpr_11k(courierfile) # can I re-supply args? I doubt it. indeed, this asfails as expected.
    # note, it asfails when parsed (pyevalled), so I have to comment out the test -- that behavior should perhaps be changed.
    
imagetest = Image(tex_origin = (-1,-1), clamp = True, nreps = 3, use_mipmaps = True) # customize options

testexpr_11m = imagetest(courierfile) # works
    # [but weirdly, on bruce's g5 061128 212p as first test, clamped part is blue! ###BUG??
    #  screenshot on g5 is in /Nanorex/bug notes/clamped is blue.jpg
    #  It turns out it is a different color depending on what's been displayed before!
    #  If i have some atoms, at least with testexpr_11pcy2, and highlight them etc, it affects this color.
    #  Must be something in the texture or its border looking at current color,
    #  or some GL state that affects drawing that border region. But it affects color all around the triangle icon in the file,
    #  not just around the square pasted area, so it must have something to do with the alpha value, or some sort of background.]

testexpr_11n = imagetest("stopsign.png") # fails; guess, our code doesn't support enough in-file image formats; ###BUG
    # exception is SystemError: unknown raw mode, [images.py:73] [testdraw.py:663] [ImageUtils.py:69] [Image.py:439] [Image.py:323]
    ##e need to improve gracefulness of response to this error
    # PIL reports: (22, 22), 'RGBA'
testexpr_11nc = imagetest("stopsign.png", convert = True) # [061128, does convert = True help? partly...]
    # this lets us read it and display it, but we get "IOError: cannot write mode RGBX as PNG"
    # when we try to write it out to update it.
    # (But why does it try to write it into a PNG file, not some other format of its choice? ###k Specify or hardcode an update format?)
    # What's better is to just use RGBA in the texture, if we can... I need to look at the texture making code re this. ###e
testexpr_11ncx2 = imagetest("stopsign.png", convert = True, _tmpmode = 'TIFF') # works, see 11pc-variant comments for details
testexpr_11ncy2 = imagetest("stopsign.png", convert = 'RGBA', _tmpmode = 'TIFF') # ditto

testexpr_11o = imagetest("RotateCursor.bmp") # fails, unknown raw mode ###BUG
    # PIL reports: (32, 32), '1'
    # "1-bit bilevel, stored with the leftmost pixel in the most significant bit. 0 means black, 1 means white."
testexpr_11oc = imagetest("RotateCursor.bmp", convert = True) # works but with exception, like _11nc
testexpr_11ocx = imagetest("RotateCursor.bmp", convert = True, _tmpmode = 'JPEG') # see if this fixes exception -- well, not quite:
    ## debug warning: oldmode != newmode ('RGBX' != 'CMYK') in
    ## <nEImageOps at 0xf029d28 for '/Nanorex/Working/cad/images/RotateCursor.bmp'>.update
    ##fyi: following exception relates to <JpegImagePlugin.JpegImageFile instance at 0xf029cb0> with mode 'CMYK'
    ##exception in <Lval at 0xf037e18>._compute_method NO LONGER ignored: exceptions.SystemError: unknown raw mode
testexpr_11ocx2 = imagetest("RotateCursor.bmp", convert = True, _tmpmode = 'TIFF') # works!
testexpr_11ocy = imagetest("RotateCursor.bmp", convert = 'RGBA') # IOError: cannot write mode RGBA as BMP
testexpr_11ocy2 = imagetest("RotateCursor.bmp", convert = 'RGBA', _tmpmode = 'TIFF') # works, looks same as ocx2

testexpr_11p = imagetest("win_collapse_icon.png") # fails, unknown raw mode ###BUG
    # PIL reports: (16, 8), 'RGBA'
testexpr_11pc = imagetest("win_collapse_icon.png", convert = True) # works but with exception, like _11nc
testexpr_11pcx = imagetest("win_collapse_icon.png", convert = True, _tmpmode = 'JPEG') # see if this fixes exception -- no, like ocx
testexpr_11pcx2 = imagetest("win_collapse_icon.png", convert = True, _tmpmode = 'TIFF') # works, looks better than some others
testexpr_11pcy = imagetest("win_collapse_icon.png", convert = 'RGBA') # partly works, no exception, but alpha not yet "active" --
    # it's probably not processed properly by neImageOps paste (see comments there), and also not drawn properly.
testexpr_11pcy2 = imagetest("win_collapse_icon.png", convert = 'RGBA', _tmpmode = 'TIFF') # works, looks worse than pcx2, improper alpha

    ###e conclusion: we need to improve image loading / texture making code, so icon/cursor images can work [cmt says how - im.convert]
    # note: mac shell command 'file' reveals image file format details, e.g.
    ## % file stopsign.png
    ## stopsign.png: PNG image data, 22 x 22, 8-bit/color RGBA, non-interlaced
    # however, on some images it's clearly incorrect (at least on bruce's g4):
    ## /Nanorex/bug notes/1059 files/IMG_1615.JPG: JPEG image data, EXIF standard 0.73, 10752 x 2048
        # obviously too large; PIL says (1704, 2272), 'RGB' when ne1 reads it
    ## blueflake.jpg:     JPEG image data, JFIF standard 1.01, aspect ratio, 1 x 1 # actually (268, 282), 'RGB' [acc'd to PIL]
    ## courier-128.png:   PNG image data, 128 x 128, 8-bit/color RGB, non-interlaced # actually (128, 128), 'RGB'
    ## redblue-34x66.jpg: JPEG image data, JFIF standard 1.01, resolution (DPCM), 0 x 0 # actually (34, 66), 'RGB'

    # more conclusions, 061128: Image defaults should be convert = True, _tmpmode = 'TIFF' for now, until Alpha handled properly.
    # eventually the options should depend on the image type so as not to waste texture ram when used for cursors.
    #e still need to test more images below with those options. plus the ones that work without them.
    #e should retest _tmpmode = JPEG since I altered code for that.



# try some images only available on bruce's g4

testexpr_11q1 = imagetest("/Nanorex/bug notes/1059 files/IMG_1615.JPG") # works
testexpr_11q1b = Image("/Nanorex/bug notes/1059 files/IMG_1615.JPG", ideal_width = 1704, ideal_height = 2272) # works [070223]
testexpr_11q2 = imagetest("/Nanorex/bug notes/bounding poly bug.jpg") # works
testexpr_11q3 = imagetest("/Nanorex/bug notes/1059 files/peter-easter-512.png") # works
testexpr_11q4 = imagetest("/Nanorex/bug notes/1059 files/IMG_1631.JPG alias") # (mac alias) fails
    ## IOError: cannot identify image file [images.py:56] [testdraw.py:658] [ImageUtils.py:28] [Image.py:1571]
testexpr_11q5 = imagetest("/Nanorex/DNA/paul notebook pages/stages1-4.jpg") # fails, unknown raw mode, ###BUG [try converting it. ###e]
    # fyi, PIL reports size & mode as (1275, 1647), 'L'
    # which means "8-bit greyscale. 0 means black, 255 means white."
    # accd to http://www.pythonware.com/library/pil/handbook/decoder.htm
    # so converting it is likely to work, but generalizing the retval of getTextureData would be more efficient,
    # but it's too large anyway so we need to support getting subrect textures from it. #e

imagetest_x2 = imagetest(convert = True, _tmpmode = 'TIFF')
imagetest_y2 = imagetest(convert = 'RGBA', _tmpmode = 'TIFF')

testexpr_11q5cx2_g4 = imagetest_x2("/Nanorex/DNA/paul notebook pages/stages1-4.jpg") # shows the "last resort" file.
##    ## for the record, at first I didn't guess why it showed courier font file, so I thought the following:
##        ##print "testexpr_11q5cx2 _e_args are",testexpr_11q5cx2._e_args # args correct...
##        ## guess: too big to resize or load or paste(?), error not reported,
##        ## but new texture did not get bound properly.
##        ## could confirm theory by putting it in a column, predict we'd show prior one in its place. ##e
##        ## WAIT, WRONG, it's just the lastresort file, since this one is only found under that name on g4!!!
    # That lastresort file needs to look different and/or print error message when found! Ok, now it prints error msg at least.
    
testexpr_11q5cx2_g5 = imagetest_x2("/Nanorex/DNA/pwkr-user-story/notebook page images/stages1-4.jpg") # works, but poor resolution
testexpr_11q5cx2_g5_bigbad = imagetest_x2("/Nanorex/DNA/pwkr-user-story/notebook page images/stages1-4.jpg",
                                          ideal_width = 1275,
                                          ideal_height = 1647) # try huge texture, non2pow size -- actually works! [bruce's g5] [g4 too]

    #e also try bigger ideal sizes for that one, or try loading a subregion of the image.
    # but for now, if we need it, just grab smaller images out of it using an external program.
    
    
testexpr_11q6 = imagetest("/Users/bruce/untitled.jpg") # glpane screenshot saved by NE1, jpg # works (note clamping artifact -- it's ok)
testexpr_11q7 = imagetest("/Users/bruce/untitled.png") # glpane screenshot saved by NE1, png # works
    # note: those are saved by a specific filetype option in "File -> Save As..."
testexpr_11q8 = imagetest("/Users/bruce/PythonModules/data/idlewin.tiff") # try tiff -- works
testexpr_11q9 = imagetest("/Users/bruce/PythonModules/data/glass.bmp") # bmp from NeHe tutorials -- works
testexpr_11q10 = imagetest("/Users/bruce/PythonModules/data/kp3.png") # png from KidPix [also on g5] -- fails, unknown raw mode ###BUG
    # fyi, PIL reports (512, 512), 'RGBA'; converting it is likely to work; generalizing to use 'A' in texture would be better. #e

testexpr_11q10x2 = imagetest_x2("/Users/bruce/PythonModules/data/kp3.png") # works

testexpr_11q11 = imagetest("/Users/bruce/PythonModules/data/textil03.jpg") # a tiling texture from the web -- works
testexpr_11q11a = imagetest("/Users/bruce/PythonModules/data/textil03.jpg", clamp=False) # try that with tiling effect -- works!
testexpr_11q12 = imagetest("/Users/bruce/PythonModules/data/dock+term-text.png") # a screenshot containing dock icons -- works

# try differently-resized images [using new features 061127, Image options rescale = False, ideal_width = 128, ideal_height = 128]
###e rename ideal_width -> tex_width?? not sure. decide later. poss name conflict.
# [note, the texture size used in the above tests used to depend on a debug pref, default 256 but 512 on g4;
#  it is now 256 by default but can be passed as option to Image; RETEST (for that and for revised implem)]

testexpr_11r1 = Image(blueflake, rescale = False) # works; I can't really tell whether I can detect smaller texture size (256 not 512)
testexpr_11r1b = Image(blueflake, rescale = False, ideal_width = 512, ideal_height = 512) # works, but note unexpected black border on left
testexpr_11r1c = SimpleRow(testexpr_11r1, testexpr_11r1b) # works (but not aligned or even at same scale -- hard to compare)

testexpr_11r2 = Image("redblue-34x66.jpg", rescale = False) # works, except the desired image is in upper left corner of black padding,
    # not lower left as expected, and maybe some filtering happened when it pasted,
    # and the black padding itself is destined to be undrawn
    ###BUG that some of that is nim ##e
testexpr_11r2b = Image("redblue-34x66.jpg") # works (rescaled to wider aspect ratio, like before)

testexpr_11s = Translate(Image("blueflake.jpg",size=Rect(7,0.4)),(1,0)) # try the new size option [061130] -- works [broken] [works again]
testexpr_11s1 = Highlightable(Image("blueflake.jpg",size=Rect(7,0.4))) # make sure this fixes mouseover stickiness and sbar text -- works [broken] [works again]
testexpr_11s2 = Boxed(Image("blueflake.jpg",size=Rect(7,0.4))) # test its lbox -- won't work? coded a fix, but that broke the use of size entirely!! [fixed, works]

testexpr_11t = imagetest("storyV3-p31.tiff") # 070222; local to bruce G5 (not in cvs); -- fails, IOError: cannot identify image file
testexpr_11tx = imagetest("storyV3-p31x.tiff") # different error -- that means _11t finds the file and can't load it -- why?

#e see also testexpr_13z2 etc

    ##e want to try: gif; pdf; afm image, paul notebook page (converted);
    # something with transparency (full in some pixels, or partial)
    #
    ####e We could also try different code to read the ones that fail, namely, QImage or QPixmap rather than PIL. ## try it

# test Spacer [circa 061126]
testexpr_12 = SimpleRow( Rect(4, 2.6, blue), Spacer(4, 2.6, blue), Rect(4, 2.6, blue)) # works
testexpr_12a = SimpleColumn( testexpr_12, Spacer(4, 2.6, blue), Rect(4, 2.6, blue)) # works
testexpr_12b = SimpleColumn( testexpr_12, Spacer(0), Rect(4, 2.6, green), pixelgap = 0) # works

# test PixelGrabber -- not fully implemented yet (inefficient, saves on every draw), and requires nonrotated view, all on screen, etc
testexpr_13 = PixelGrabber(testexpr_12b, "/tmp/pgtest_13.jpg") # lbox bug... [fixed now]
    # worked, when it was a partial implem that saved entire glpane [061126 830p]
testexpr_13x1 = Boxed(testexpr_12b) # ... but this works, as if lbox is correct! hmm...
testexpr_13x2 = PixelGrabber(testexpr_13x1, "/tmp/pgtest_13x2.jpg") # works the same (except for hitting left margin of glpane) [fixed now]
testexpr_13x3 = Boxed(Translate(testexpr_12b, (1,1))) # works
testexpr_13x4 = Boxed(Translate(Translate(testexpr_12b, (1,1)), (1,1))) # works
testexpr_13x5 = Boxed(Boxed(Translate(Translate(testexpr_12b, (1,1)), (1,1)))) # works -- not sure how! [because Boxed is not Widget2D]
testexpr_13x6 = Boxed(PixelGrabber(testexpr_12b)) # predict PixelGrabber lbox will be wrong, w/ shrunken Boxed -- it is... fixed now.
testexpr_13x7 = Boxed(PixelGrabber(Rect(1,1,red))) # simpler test -- works, saves correct image! no bbottom bug here...
testexpr_13x8 = Boxed(PixelGrabber(SimpleColumn(Rect(1,1,red),Rect(1,1,blue)))) # this also had lbox bug, now i fixed it, now works.
    # It was a simple lbox misunderstanding in PixelGrabber code. [###e maybe it means lbox attr signs are wrongly designed?]

savedimage = "redblue-34x66.jpg"
    ## was "/tmp/PixelGrabber-test.jpg" - use that too but not as a "test" since it's not deterministic;
    ## it'd actually be a "command to see the last PixelGrabber test which saved into the default file"
testexpr_13z = Boxed(bordercolor=purple)(Image(savedimage)) # works, but aspect ratio wrong -- that's a feature for now...
testexpr_13z2 = Boxed(color=purple)(Image(savedimage, rescale = False)) # works (with padding etc for now) ####e make this the default?
testexpr_13z3 = Boxed(color=purple)(Image(savedimage, rescale = False, ideal_width = 128, ideal_height = 128)) # works
testexpr_13z4 = Boxed(color=purple)(Image(savedimage, rescale = False, ideal_width = 64, ideal_height = 64)) # will rescale... yes.
    # note that it prints a debug warning that it can't do as asked

# try non-power-of-2 texture sizes (not confirmed that's what's actually being given to us; should get ImageUtils to tell us ####e)
testexpr_13z5 = Boxed(color=purple)(Image(savedimage, rescale = False, ideal_width = 36, ideal_height = 68))
    # works on g4: non-2pow sizes -- but aspect ratio is wrong ###BUG??
testexpr_13z6 = Boxed(color=purple)(Image(savedimage, rescale = False, ideal_width = 34, ideal_height = 66)) # ditto -- ###BUG??

    ###BUG - in some above, purple is showing as white. ah, option name is wrong. revise it in Boxed?? probably, or add warning. ##e


# try out a table of icons (notation is not very nice though...)
# [note: this code to setup testexpr_14 all runs even if we don't display that test,
#  but the images won't load [that's verified] so it shouldn't be too slow]
hide_icons = """
anchor-hide.png                 gamess-hide.png                 measuredihedral-hide.png        moltubes-hide.png
atomset-hide.png                gridplane-hide.png              measuredistance-hide.png        molvdw-hide.png
displayCylinder-hide.png        ground-hide.png                 molcpk-hide.png                 rmotor-hide.png
displaySurface-hide.png         linearmotor-hide.png            moldefault-hide.png             stat-hide.png
espimage-hide.png               lmotor-hide.png                 molinvisible-hide.png           thermo-hide.png
espwindow-hide.png              measureangle-hide.png           mollines-hide.png
""".split() # 23 icons

if 1:
    # test the corresponding non-hidden icons instead -- works
    hide_icons = map(lambda name: name.replace("-hide",""), hide_icons)
    for another in "clipboard-empty.png clipboard-full.png clipboard-gray.png".split():
        hide_icons.append(another)
    pass

# how do you take 4 groups of 6 of those? we need a utility function, or use Numeric reshape, but for now do this:
res = []
## moved into images.py:
## IconImage = Image(ideal_width = 22, ideal_height = 22, convert = True, _tmpmode = 'TIFF') # size 22 MIGHT FAIL on some OpenGL drivers
nevermind = lambda func: identity
for i in range(5): # 4 is enough unless you set 'if 1' above
    res.append([])
    for j in range(6):
        res[i].append(None) # otherwise, IndexError: list assignment index out of range
        try:
            res[i][j] = hide_icons[i * 6 + j]
            res[i][j] = IconImage(res[i][j])
            if not ((i + j ) % 3): # with 3 -> 2 they line up vertically, but that's only a coincidence -- this is not a real Table. 
                pass ## res[i][j] = Boxed(res[i][j])
        except IndexError:
            res[i][j] = nevermind(Boxed)(Spacer(1 * PIXELS)) ## None   ###e Spacer should not need any args to be size 0
        continue
    continue
testexpr_14 = SimpleColumn( * map(lambda row: nevermind(Boxed)(SimpleRow(*row)), res) ) # works!
testexpr_14 = Translate(testexpr_14, V(-1,1,0) * 2)
testexpr_14x = SimpleColumn(*[Rect(2 * i * PIXELS, 10 * PIXELS) for i in range(13)])
    # works (so to speak) -- 11th elt is TextRect("too many columns")
    ####e i need that general warning when there are too many args!!
testexpr_14x2 = SimpleRow(*[Rect(2 * i * PIXELS, 10 * PIXELS) for i in range(13)]) # works -- TextRect("too many rows")


# ChoiceButton (via ChoiceColumn, a convenience function to call it, which ought to be redesigned and made an official expr too #e)
#   summary, 061130 1015p: mostly works, except for bugs which are not its fault, namely TextRect hit test,
#   speed/sync of selobj update (guess at cause of sometimes picking wrong one after fast motion),
#   selobj-changeover effects (guess at cause of sbar_text not working after a click and no motion off the object)
testexpr_15 = ChoiceColumn(6,2) # doesn't work - click on choice only works if it's the one that's already set (also color is wrong)
    ## ( nchoices, dflt = 0, **kws), kws can be content, background, background_off ## make_testexpr_for_ChoiceButton()
testexpr_15a = ChoiceColumn(6,2, background = Rect(3,1,green), background_off = Rect(2,1,gray))
    # almost works -- you can click on any choice, but only for click over area of gray rect,
    # including the part behind the text, but not for click over other part of text
    # (and maybe this is the text click bug i recalled before, didn't resee in toggleshow, but there the text is over the grayrect??)
    # possible clue: for mouseover sbar msg, there is hysteresis, you see it in text not over rect iff you were seeing it before
    # (from being over rect), not if you come directly from blank area. #k is same true of whether click works? yes!
    # another clue: if you move mouse too fast from blank to rect to text not over rect, you don't get sbar msg.
    # you have to hover over the good place and wait for redraw and see it, only then move out over the "suspended" part
    # (text not over rect, hanging instead over infinite depth empty space).

    # see also bug comments in controls.py.
    
testexpr_15b = ChoiceColumn(6,2, background = Rect(3,1,green), background_off = IconImage("espwindow-hide.png"))

##e ChoiceColumn should be an InstanceMacro, not a def! doesn't work to be customized this way.
## testexpr_15cx = testexpr_15b(background = Rect(3,1,red)) -- ###BUG? missing errmsg? somehow it silently doesn't work.
##niceargs = ChoiceColumn(background = Rect(3,1,green), background_off = IconImage("espwindow-hide.png")) # error, not enough args
##testexpr_15cy = niceargs(6,2)

niceargs = dict(background = Rect(3,1,green), background_off = IconImage("espwindow-hide.png"))
testexpr_15c = ChoiceColumn(6,2, content = TextRect("zz",1,30), **niceargs) # bug more likely at far right end of text, but not consistent
testexpr_15d = ChoiceColumn(6,2, content = Rect(7,0.3,white), **niceargs) # compare Rect here -- works, reliable except right after click [which is a ###BUG]
testexpr_15e = ChoiceColumn(6,2, content = Translate(Image("blueflake.jpg",size=Rect(7,0.4)),(1,0)), **niceargs) # compare Image -- works
    # see also _22

# State [061203]
class toggler(InstanceMacro):
    var = State(int, 0)
    _value = Highlightable(
        list_Expr( # if you use [] directly, you get TypeError: list indices must be integers (of course)
            Rect(1,1,red),
            Rect(1,1,green),
            Rect(1,1,blue),
        )[ mod_Expr(var,3) ],
            #e do we want a nicer syntax for this, as simple as If which you can only use when 3 is 2? Case or Switch?
        on_press = Set(var, var+1)
    )
    pass
testexpr_16 = SimpleRow(toggler(), toggler()) # works
    # as of 061204 this works, even tho State & Set are not completely implemented (and I predict bugs in some uses)

checkbox_image = IconImage(ideal_width = 25, ideal_height = 21, size = Rect(25 * PIXELS, 21 * PIXELS))
    # note, IconImage ought to use orig size in pixels but uses 22x22,
    # and ought to display with orig size but doesn't -- all those image options need reform, as its comments already know ###e

class checkbox_v1(InstanceMacro):
    var = State(int, 0) #e bool, False?
    _value = Highlightable(
        list_Expr( 
            checkbox_image('mac_checkbox_off.jpg'),
            checkbox_image('mac_checkbox_on.jpg'),
        )[ mod_Expr(var,2) ],
            #e or use If
        on_press = Set(var, mod_Expr(var+1,2) ) #e or use not_Expr
    )
    pass
testexpr_16a = SimpleColumn( 
    SimpleRow(checkbox_v1(), TextRect("option 1",1,10)), 
    SimpleRow(checkbox_v1(), TextRect("option 2",1,10)),
  ) # works

class checkbox_v2(InstanceMacro):
    # this is now copied into controls.py, but it's probably to be renamed and revised there, so leave this test here
    default_value = Option(bool, False)
    var = State(bool, default_value)
        #e need to be able to specify what external state to use, eg a prefs variable
        # (but i don't know if the arg or option decl can be part of the same decl, unless it's renamed, e.g. StateArg)
    _value = Highlightable(
        If( var,
            checkbox_image('mac_checkbox_on.jpg'),
            checkbox_image('mac_checkbox_off.jpg'),
        ),
        on_press = Set(var, not_Expr(var) )
    )
    pass
testexpr_16b = SimpleColumn( 
    SimpleRow(checkbox_v2(), TextRect("option 1a",1,10)), #e need to be able to specify specific external state, eg a prefs variable
    SimpleRow(checkbox_v2(default_value = True)(), TextRect("option 2a",1,10)), # that 2nd () is to tell it "yes, we supplied args"
  ) # works

from prefs_constants import displayOriginAxis_prefs_key
testexpr_16c = SimpleColumn( # [later: see also kluge_dragtool_state_checkbox_expr, similar to this with different prefs_key]
    SimpleRow(checkbox_v3(PrefsKey_StateRef(displayOriginAxis_prefs_key)), # test: specify external state, eg a prefs variable
              ###e would this look better? checkbox_v3(prefs_key = displayOriginAxis_prefs_key)
              TextRect("display origin axis",1,20)),
  ) # works! (changes the axis display)
    # an older implem doesn't work yet, see comments in controls.py
    # note: if prior verson of _16c diff implem of _v3) failed first in same session, then in this good test or a prior good test
    # being retried, we'd see a double-inval warning for glpane (something called standard_inval twice). But if no error in same session
    # then I never saw this.


# == dragging (e.g. on_drag)
testexpr_17 = Highlightable(Rect(), on_drag = print_Expr("on_drag happened")) # works, but trivial (only prints)

# testexpr_17a was moved below and renamed to testexpr_19


# == demo_MT

testexpr_18 = MT_try1( _my.env.glpane.assy.part.topnode )
    # works! except for ugliness, slowness, and need for manual update by reloading.
    #e Still need to test: changing the current Part. Should work, tho manual update will make that painful.
    ###e need better error message when I accidently pass _self rather than _my]

testexpr_18a = test_drag_pixmap( _my.env.glpane.assy.w.mt, _my.env.glpane.assy.part.topnode ) # nim, otherwise works -- debug prints

testexpr_18i = MT_try2( _my.env.glpane.assy.part.topnode ) #070207


# == more dragging

testexpr_19 = GraphDrawDemo_FixedToolOnArg1(Rect(10)) # works
## testexpr_17a = testexpr_19 # alias, remove soon
    # [for current status see comments just before GraphDrawDemo_FixedToolOnArg1]
testexpr_19a = GraphDrawDemo_FixedToolOnArg1(Overlay(Rect(10),Sphere(1.5))) # works
testexpr_19b = GraphDrawDemo_FixedToolOnArg1(Overlay(Rect(10),SimpleRow(Sphere(1.5),Sphere(2)))) # works
    # note that you can interchange the guide shapes at runtime, and retain the drawing which was done with their aid.
    # (just by editing this file's choice of testexpr, and clicking to reload it)

testexpr_19c = Overlay( testexpr_19b, # edit this one by hand if you want
                        Translate( kluge_dragtool_state_checkbox_expr, (6,-4) ) ###e need to wrap this with "draw at the edge, untrackballed"
                    )
# later 061213:
testexpr_19d = Overlay( testexpr_19b,
                        DrawInCorner(Boxed(kluge_dragtool_state_checkbox_expr))
                    ) # (works but highlight-sync bug is annoying) -- after some changes inside 061214, still works

testexpr_19e = Overlay( GraphDrawDemo_FixedToolOnArg1( Rect(9), highlight_color = green),
                            # this is the new (and only current) test of background.copy(color=green) experiment [061214]
                        DrawInCorner(Boxed(kluge_dragtool_state_checkbox_expr)) ) # ugly color, but works

# later 070106: (syntax is a kluge; see also testexpr_26)
testexpr_19f = eval_Expr( call_Expr( lambda thing:
                                     Overlay( thing,
                                              DrawInCorner( Boxed(
                                                  eval_Expr( call_Expr( demo_drag_toolcorner_expr_maker, thing.world )) )) ),
                                     testexpr_19b ))
    # This is not a valid example for EVAL_REFORM (and indeed it fails then):
    # testexpr_19b is not instantiated (when we eval the call_Expr and ask for thing.world) but needs to be.
    # Since this whole syntax was a kluge, I should not worry much about making it or something similar still work,
    # but should instead make a better toplevel syntax for the desired effect, and make *that* work... for that, see lambda_Expr.py. ###e
    # So for the time being I won't try to fix this for EVAL_REFORM.
    # (At one time it didn't work without EVAL_REFORM unless testbed was enabled. I'm guessing that was an old bug (predating EVAL_REFORM)
    # and I fixed it -- for details see cvs revs prior to 1.202 (Qt3 branch).)
    
# hmm, what would happen if we just tried to tell it to instantiate, in the simplest way we might think of?
# It may not work but it just might -- at least it'll be interesting to know why it fails... [070122 945a]
# fails because Instance wants to make one using _self._i_instance, but _self has no binding here, evals to itself.
testexpr_19g_try1_fails = eval_Expr( call_Expr( lambda thing:
                                     Overlay( thing,
                                              DrawInCorner( Boxed(
                                                  eval_Expr( call_Expr( demo_drag_toolcorner_expr_maker, thing.world )) )) ),
                                     Instance(testexpr_19b) ))
# Is there a sensible default binding for _self? In this lexical place it might be "the _app, found dynamically"...
# but to be less klugy we want to make Instance work differently here... or use a different thing to make one...
# or make Instance an expr. Or at least give it a helper func to have a backup for _self._i_instance failing or _self having no value.
# But as a test I can just manually insert whatever would work for that... hmm, how about this: [later: see also testexpr_30g]
testexpr_19g = eval_Expr( call_Expr( lambda thing:
                                     Overlay( thing,
                                              DrawInCorner( Boxed(
                                                  eval_Expr( call_Expr( demo_drag_toolcorner_expr_maker, thing.world )) )) ),
                                     ## _app._i_instance(testexpr_19b)
                                         # safety rule: automatic formation of getattr_Expr not allowed for attrs starting _i_
                                     call_Expr( _app.Instance, testexpr_19b, "#19b")
                                     )) # works now, after some bugfixes [070122]

testexpr_19haux = GraphDrawDemo_FixedToolOnArg1(Overlay(testexpr_11q1b(size = Rect(10)),SimpleRow(Sphere(2),Sphere(1),Sphere(0.5),Sphere(0.25))))
testexpr_19h = eval_Expr( call_Expr( lambda thing:
                                     Overlay( thing,
                                              DrawInCorner( Boxed(
                                                  eval_Expr( call_Expr( demo_drag_toolcorner_expr_maker, thing.world )) )) ),
                                     call_Expr( _app.Instance, testexpr_19haux, "#19h")
                                     )) # 070223 --

# == DrawInCorner

def func(text, color, corner):
    color1 = ave_colors(0.6,white,color)
    color2 = ave_colors(0.1,white,color)
    return DrawInCorner( Boxed( SimpleColumn(
                                       TextRect(text,1,11),
                                       Highlightable(Rect(1,1,color1),Rect(1,1,color2)))) , corner)

testexpr_20 = Overlay(
    Rect(1,1,purple),
    func('lower left', red, (-1,-1)),
    func('upper left', green, (-1,1)),
    func('lower right', black, (1,-1)),
    func('upper right', blue, (1,1)))
    # works -- except for textrect size when I rotate the trackball, and it's intolerably slow to highlight.
    # (why slow? chopping out TextRect speeds it somewhat, but it's still slow. ###e SHOULD COMPARE to same stuff drawn in center.)
testexpr_20a = Overlay(
    ##Rect(1,1,purple),
    func('lower left', red, (-1,-1)),
    func('upper left', green, (-1,1)),
    func('lower right', black, (1,-1)),
    func('upper right', blue, (1,1)))

# == alignment exprs [061211]

def wrap1(alignfunc):
    return Boxed(alignfunc(Rect()))

testexpr_21 = Boxed(SimpleColumn(wrap1(Left), wrap1(Center), wrap1(Right))) # works
testexpr_21a = Boxed(SimpleRow(wrap1(Left), wrap1(Center), wrap1(Right))) # works
testexpr_21b = Boxed(SimpleColumn(wrap1(TopRight), wrap1(CenterRight), wrap1(BottomRight))) # might work but hard to interpret
testexpr_21c = Boxed(SimpleRow(wrap1(TopRight), wrap1(CenterRight), wrap1(BottomRight))) # ditto

# the following testexpr_21d & _especially _21e are examples of toplevel code we need to figure out how to simplify. ####

def aligntest(af):
    "[af should be an alignment func (class) like Center]"
    try:
        def doit(n):
            return af(Translate(Rect(n),(-n/3.0,-n/3.0)))
        return Overlay(BottomRight(TextRect(af.__name__)),
                       BottomLeft(Boxed(SimpleRow(doit(0.4),
                                                  doit(0.6),
                                                  doit(0.9) ))),
                       TopRight(Boxed(SimpleColumn(doit(0.45),
                                                   doit(0.65),
                                                   doit(0.95) ))) )
    except:
        print sys.exc_info() ##k
        return BottomRight(TextRect('exception discarded') )#e find a way to include the text?

def aligntest_by_name(afname):
    try:
        import Center
        af = getattr(Center, afname)
        res = aligntest(af)
        worked = True #e or a version counter?? to be correct, i think it needs one [070122]
    except:
        res = BottomRight(TextRect("didn't work: %r" % afname,1,30))
        worked = False
    ## return res
    return local_ipath_Expr( (worked,afname), res)
        # try local_ipath_Expr as a bugfix for _21e/_21g in EVAL_REFORM, 070122 -- partly works (fully after we have Expr.__eq__);
        # for details see long comment in _21g.

testexpr_21d = aligntest(Center)

colwords = ('Left', 'Center', 'Right', '')
rowwords = ('Top', 'Center', 'Bottom', '')
## choiceref_21e = LocalVariable_StateRef(str, "") ###k ok outside anything? it's just an expr, why not? but what's it rel to? var name???
    # answer: each instance has its own state, so it won't work unless shared, e.g. in InstanceMacro or if we specify sharing somehow.
choiceref_21e = PrefsKey_StateRef("A9 devel scratch/testexpr_21e alignfunc5", 'Center') # need a non-persistent variant of this... ###e
    # later note: choiceref_21e (constructed by PrefsKey_StateRef) is an expr, not yet an instance.
def mybutton(xword, yword, choiceref): # later note: choiceref is really choiceref_expr,  not yet an instance.
    word = yword + xword
    if word == 'CenterCenter':
        word = 'Center'
    elif word == 'Center':
        ## word = (xword or 'Y') + (yword or 'X') -- oops, wrong order (YCenter)
        if not xword:
            word = yword + 'Y' # i.e. CenterY
        elif not yword:
            word = xword + 'X' # CenterX
    if not word:
        return Spacer()
    return ChoiceButton(word, choiceref, content = TextRect( format_Expr("%s", _this(ChoiceButton).choiceval), 1,12 ) )

table_21e = SimpleColumn(* [SimpleRow(* [mybutton(colword, rowword, choiceref_21e) for colword in colwords]) for rowword in rowwords])
testexpr_21e = Translate( Overlay(
    eval_Expr( call_Expr( aligntest_by_name, getattr_Expr(
        ## choiceref_21e, ###BUG in EVAL_REFORM noticed 070122 -- see below for fix-attempt
        call_Expr( _app.Instance, choiceref_21e, 'testexpr_21e.choiceref_21e'),
            # try this 070122 -- fixes it except for "bug: expr or lvalflag for instance changed", same as same change
            # does for testexpr_21g, so for now I'm only doing further work in testexpr_21g. [fully fixed there & here, eventually]
        'value'))) ,
    TopLeft( Boxed(table_21e))
                        ), (-6,0) )
    # non-EVAL_REFORM: works, IIRC.
    # EVAL_REFORM [070122]: mostly works after bugfixes, same as _21g (which see).
    # Later, works fully now, due to new Expr.__eq__, same as _21g. At all bugfix-stages (3 fixes I think) these egs behaved the same,
    # tho in some cases they needed different variants of the same bugfix-change. [070122 late]

    # all 15 primitives in the table are defined and working as of 061211 eve

testexpr_21f = Boxed( identity(Center)( Rect(2,3.5,purple))) # test lbox translation by Center -- works
    # (implem of lbox shift is in Translate, so no need to test all alignment prims if this works)

class class_21g(DelegatingInstanceOrExpr): # see how far I can simplify testexpr_21e using an expr class [061212]
    choiceref_21g = Instance( PrefsKey_StateRef("A9 devel scratch/testexpr_21g alignfunc", 'Center') ) #070122 bugfix for EVAL_REFORM
        # note: this is an expr. In current code [061212]: it's implicitly instantiated, i think.
        # In planned newer code [i think]: you'd have to explicitly instantiate it if it mattered,
        # but it doesn't matter in this case, since this expr has no instance-specific data or state.
        # update 070122 -- indeed, it fails in EVAL_REFORM. Partly fixed by Instance above (the "it doesn't matter" above is nim ###e).
        # For more of the fix see comments of this date below. [fully fixed now]
    colwords = ('Left', 'Center', 'Right', '')
    rowwords = ('Top', 'Center', 'Bottom', '')
    ## xxx = TextRect( format_Expr("%s", _this(ChoiceButton).choiceval), 1,12 ) #k is _this ok, tho it requires piecing together to work?
        # no, see comment "IT WILL FAIL" -- and indeed it does:
        ## AssertionError: _this failed to find referent for '_this_ChoiceButton' (at runtime)
    def mybutton_CANTWORK(self, xword, yword):
        # an ordinary method -- return an expr when asked for one - but does require self to run, THOUGH IT OUGHT NOT TO
        #k (should we make it into a classmethod or staticmethod? yes, see below)
        word = yword + xword
        if word == 'CenterCenter':
            word = 'Center'
        elif word == 'Center':
            if not xword:
                word = yword + 'Y' # i.e. CenterY
            elif not yword:
                word = xword + 'X' # CenterX
        if not word:
            return Spacer()
        ###k is it ok that this returns something that was constructed around self.choiceref_21g,
        # a saved choiceref instance, the same instance each time this runs (for different args)?
        # reiterating the above comment about the choiceref_21g attr def:
        # current code: yes, sharing that instance is ok
        # planned new code: it will be including an expr anyway, tho hopefully one with the optim-power
        # to cache instantiated versions on self if it so desires... this might mean self.choiceref_21g
        # is a "sharable partly-instantiated-as-appropriate-for-self thing", able to be anything in
        # between instance and expr. (But what if it was a number vs a number-producer?? #k)
        ###k what about for self.xxx?
        # In planned new code, it's just an expr, so we're fine (given that we're returning "just an expr").
        # In current code, it will eval to an instance...
        # _this might fail now, fail later (my guess), or work later.
        # But the instance is the same for each button, which is definitely wrong. SO IT WILL FAIL.###BUG
        return ChoiceButton(word, self.choiceref_21g, content = self.xxx )
    # this next is supposed to be an expr dependent only on this class... but it can't be if mybutton gets choiceref_21g via self.
    # so fix that:
    def mybutton(xword, yword, choiceref): ## , xxx): # staticmethod, but only after direct use as function
        word = yword + xword
        if word == 'CenterCenter':
            word = 'Center'
        elif word == 'Center':
            if not xword:
                word = yword + 'Y' # i.e. CenterY
            elif not yword:
                word = xword + 'X' # CenterX
        if not word:
            return Spacer() 
        ## return ChoiceButton(word, choiceref, content = xxx )
        return ChoiceButton(word, choiceref, content = TextRect( format_Expr("%s", _this(ChoiceButton).choiceval), 1,12 ) )
    # now pass what we need to mybutton, direct from the class namespace -- will this work now, or do we need to do it before the staticmethod call??
    # yes, we got TypeError: 'staticmethod' object is not callable until we did that
    table_21g = SimpleColumn(* [SimpleRow(* [mybutton(colword, rowword, choiceref_21g) for colword in colwords]) for rowword in rowwords])
    mybutton = staticmethod(mybutton) # this statement could just as well be 'del mybutton', i think
    del mybutton #k ok?
    # the following required compromises with current code:
    # getattr_Expr, eval_Expr, no xxx in mybutton call above (due to _this vs autoinstantiation).
    delegate = Overlay(
        eval_Expr( call_Expr( aligntest_by_name, getattr_Expr(choiceref_21g, 'value') )) ,
        ###BUG in EVAL_REFORM noticed 070122: theory: this expr gets recomputed when the getattr_Expr's someobj.value is changed (correct),
        # but the index assigned to it does not change (even though it includes components from the changed expr, which would change
        # if it was due to an If that the expr changed). Symptom: "bug: expr or lvalflag for instance changed", and no update of the
        # alignment demo display (both behaviors same as for _21e -- after both of them got a new manual Instance to fix a worse bug).
        # This bug was predicted by a comment in class eval_Expr regarding changes in its argval (in this case, an expr constructed
        # and returned by our ad-hoc external function, aligntest_by_name).
        #
        # Maybe refile these comments into class eval_Expr: ##e
        # 
        # The best fix would probably be to invalidate the instance at that fixed index, letting the index stay fixed, saying it's ok
        # for the expr there to change. This requires inval access to the LvalDict2 used by _CV__i_instance_CVdict.
        # It's best because it'll take care of all cases of "bug: expr or lvalflag for instance changed",
        # albeit sometimes inefficiently. The details of how to best do this inval (by usage/change tracking of the expr)
        # are not trivial... not yet worked out. ###e
        #
        # Another fix might be to wrap a varying part of this expr with some fixed Instance which absorbs the change.
        # (That wrapper might need the previous fix internally, but it might be more efficient if the varying part
        #  was smaller than it is now.) Not worked out. ###e
        #
        # Another fix might be to add something unique to the local ipath mods from this retval. I'm not sure this can work,
        # since the innermost differing retval is not a pure expr -- unless I add it in an ad-hoc way to something outside that --
        # which is a useful thing to be able to do, even if not the best general fix for this example. It could be done by a
        # toplevel use of something like lexenv_ipath_Expr (perhaps inside aligntest func itself), or by an option to eval_Expr.
        #   Note that if the goal is indeed to memoize any variants of this varying expr, but to be conservative about how much
        # gets memoized, then this is the only principled fix. So on those grounds I'll try it by using the new local_ipath_Expr
        # in aligntest_by_name.
        #   This fix works fine in both _21e and this _21g, except that "bug: expr or lvalflag for instance changed"
        # is still printed when equal but not identical exprs are seen at the same index (i.e. whenever we try any choice for the 2nd
        # time (since remaking the main instance). In this case it doesn't indicate a real bug -- except that pure-expr equality should
        # be based on formal structure, not pyobj identity. Now that's fixed by a new Expr.__eq__ (except for loose ends documented
        # in a comment there), and testexpr_21g seems to work fully now.

            # [older comments, not reviewed on 070122:]
                # predict failure here in .value, until I re-add getattr_Expr [and then? works]
                # yes, it failed, but I didn't predict the exact manner: AssertionError: compute method asked for on non-Instance <PrefsKey_StateRef#105377(a)>
                # and i'm unsure if it's equiv to what i predicted... ##k
            # I think ExprsMeta scanner makes choiceref_21g symbolic -- but, too late to help? YES, ###BUG, unless we wrap the def above with something
            # to make it symbolic, even if we needn't wrap it with something to instantiate it.
            # And I think the eval_Expr requirement isn't affected by being in a class. And I think the next line TopLeft( Boxed(table_21g)) will still work,
            # UNLESS replacement of table_21g with _self.table_21g causes trouble (not sure). #k likely BUG -- but seems to work ok for some reason... aha,
            # it's because _self.table_21g evals to what's already an instance, since all exprs as class attrs become instances as self attrs in current code.
            # In planned new code it will also work, with table_21g staying an expr until used (or explicitly type-coerced or instantiated).
        TopLeft( Boxed(table_21g))
     )
    pass

testexpr_21g = Translate( class_21g(), (-6,0) ) # works [061212 154p]; works in EVAL_REFORM [after 3 bugfixes, 070122]

# ==

##niceargs = dict(background = Rect(3,1,green), background_off = IconImage("espwindow-hide.png"))
##testexpr_15c = ChoiceColumn(6,2, content = TextRect("zz",1,30), **niceargs) # bug more likely at far right end of text, but not consistent
##testexpr_15d = ChoiceColumn(6,2, content = Rect(7,0.3,white), **niceargs) # compare Rect here -- works, reliable except right after click [which is a ###BUG]
##testexpr_15e = ChoiceColumn(6,2, content = Translate(Image("blueflake.jpg",size=Rect(7,0.4)),(1,0)), **niceargs) # compare Image -- works

testexpr_22 = DrawInCorner(ChoiceRow(6,2), (1,-1)) # works! (though default options are far from perfect)
    # see also kluge_dragtool_state_prefs_default and _19*

# == test DisplistChunk

  ##BUG in general when not wrapped directly around translated Highlightable, or when an HL is trackballed.
  # Most of these are not marked as indiv ##BUGs.

testexpr_23 = DisplistChunk(Rect(1,green)) # might work
testexpr_23x = DisplistChunk(Rect(1,green), debug_prints = "dlc1") # might work

# try to detect the speedup of trackball or animated rotation. some of these may fail immediately due to highlighting issue.
# (remember to turn off testbed for speed tests.)
testexpr_23a1 = TextRect("hjfdfhjksdhfkjafhjksdhfkafdftftytudyufdyufua\n" * 26, max_lines = 100, max_cols = 100) # works
testexpr_23a2 = DisplistChunk(testexpr_23a1) # works -- *much* faster (as eyeballed using rotate view 90)
    # WHY does this not fail due to highlighting issue? Maybe TextRect is not natively highlightable. Ah, that must be it.
testexpr_23a1h = Highlightable(testexpr_23a1) # works
testexpr_23a2h = DisplistChunk(testexpr_23a1h) # doesn't crash, and even its highlighting sbar msg works! WHY??? ####
    # At least it does have a bug -- the highlight is drawn in the home position of the main thing, ignoring trackball rot/shift.
    # Guess: loading the matrix doesn't fail while compiling a displist, it just loads the wrong matrix.
    # If so (and if indep of opengl driver), I can leave this unfixed until I need highlighting behavior inside one of these.
    # (It also suggests a kluge fix: load the matrix for real, by disabling displist, once each time the local coords change!
    #  Some experiments suggest this might work. Hmm. ##### THINK WHETHER THIS COULD WORK -- no, inefficient, needed for all objs.
    #  Or is it only needed for "candidates found by glselect"?? Hmm.... #####)
    # This may also mean it can work fine for exprs that are shown in fixed places, like widgets in our testbed.

# I suspect it may have another highlighting bug besides coords, namely, in use of a different appearance for highlighting.
# But it turns out it doesn't. Later: I guess that's because in DisplistChunk(Highlightable(...)), the draw_in_abs_coords
# is called directly on the inner Highlightable, so the displist is only used when running the usual draw on the whole thing.
testexpr_23b = testexpr_9c(fakeoption=0) # customize it just to make it nonequal - works
testexpr_23bh = DisplistChunk(testexpr_9c) # sort of works - top rect works except for coords, bottom rect doesn't work at all,
    # maybe [wrong] since not moused until after trackball, or trackball too far for it??
    # or [right i think] since not drawn at origin?
    # if the latter, it probably breaks the hopes of making this work trivially for testbed widgets.
# ... maybe it would turn out differently if the DisplistChunk was embedded deeper inside them:
testexpr_23bh2 = SimpleColumn( DisplistChunk(testexpr_9a), DisplistChunk(testexpr_9b)) # works.

# so I put it in checkbox_pref, and this sped up the testbed expr with 5 of them, so I adopted it in there as standard.
# I also retested demo_drag (_19d) re that; it works.

testexpr_23ch = Highlightable(testexpr_10c) # works, but prints debug fyi: len(names) == 2 (names = (429L, 439L)) due to glname nesting
testexpr_23cd = DisplistChunk(testexpr_10c) # has expected coord ##BUG -- outermost toggle works, inner one as if not highlightable
    # probably a bit faster (smoother rot90) than bare testexpr_10c, tho hard to be sure.
    ###e sometime try improving demo_MT to use DisplistChunk inside -- should not be hard -- but not right now.

    # but I did improve demo_drag inside... testexpr_19d still works, and seems to be faster (hard to be sure)

# == demo_polygon.py (stub)

# commented out 070117, see comment after "import demo_polygon"
##testexpr_24 = newerBoxed(Boxed(Rect(1))) # works
##testexpr_24a = newerBoxed(Boxed(Highlightable(Rect(1)))) # works
##testexpr_24b = resizablyBoxed(Boxed(Rect(1))) # works with action being incrs of state

  # now modifying _19d to let me drag existing nodes... sort of working, see comments there...
  # will use this in _24b or so to let me define corner resizers -- as long as their local coords are right, they
  # are just like any other draggable things in local coords. that is where i am 070103 447p (one of two places with that comment)

# == ActionButton

testexpr_25 = ActionButton( PrintAction("pressed me"), "test button")

# == demo of shared instance, drawn in two places (syntax is a kluge, and perhaps won't even keep working after eval/instantiate fix )

testexpr_26 = eval_Expr( call_Expr( lambda shared: SimpleRow(shared, shared) , testexpr_10c )) # no longer a correct test [070122]
    # pre-EVAL_REFORM status: works, except for highlighting bug --
    # when you draw one instance twice, Highlightables only work within the last-drawn copy. See BUGS file for cause and fix.
    # EVAL_REFORM status 070122: this no longer makes a shared instance -- it shows different instances of the same expr.
    # So use _26g instead.

# try the same fix for EVAL_REFORM as we're trying in _19g [070122 1017a]:
testexpr_26g = eval_Expr( call_Expr( lambda shared: SimpleRow(shared, shared) ,
                                     call_Expr( _app.Instance, testexpr_10c, "_26g")
                                     )) # works, after some bugfixes (but highlight only works on right, as explained above)

# == TestIterator [070122]

testexpr_27preq = SimpleColumn(testexpr_6f, testexpr_6f) # works (two different ipaths)
testexpr_27 = TestIterator(testexpr_6f) # works [shows that ipaths differ]
testexpr_27w = TestIterator_wrong_to_compare(testexpr_6f) # works -- ipaths are the same, since it makes one instance, draws it twice

# ==

# this demos a bug, not yet diagnosed:
testexpr_28 = eval_Expr( call_Expr( lambda shared: SimpleRow(shared, shared) ,
                                     call_Expr( _app.Instance_misspelled, testexpr_10c, "_28")
                                     )) # this has "infrecur in delegate" bug, don't know cause yet ###BUG

# ==

# test customization outside of If_expr -- unanticipated, probably won't work, but how exactly will it fail? [070125 Q]
# (the desire came up in Ribbon2_try1 in new file dna_ribbon_view.py, but devel comments might as well be in If_expr.py)

testexpr_29 = If( mod_Expr( _app.redraw_counter, 2), Rect(1, 1.5), Rect(1.5, 1) ) (color = red) # partly works --
    # it just ignores the customization. (How, exactly??? see below for theory #k)
    # it doesn't fail to build the expr, or to run it -- it just ignores the customization opts.
    # I think If is actually an IorE macro which takes opts, fails to complain about not recognizing them,
    # and has no way to make them available to what's inside it. ###WAIT, does If_expr have a bug that makes it instantiate its args??
    # test this now:

# does If_expr have a bug that makes it instantiate its args??
# if yes bug, these ipaths might be same -- not sure -- so I won't know for sure it's ok even if they differ.
# if no bug, they'll definitely differ.
testexpr_29ax = TestIterator(If_expr(False, testexpr_6f)) ###BUG: note that I failed to pass an arg for the else clause... still a bug:
    ## IndexError: tuple index out of range
    ## [lvals.py:210] [Exprs.py:254] [Exprs.py:1043] [Exprs.py:1023] [Exprs.py:952] [Exprs.py:918] [If_expr.py:71] [If_expr.py:81]

testexpr_29a = TestIterator(If_expr(True, testexpr_6f)) # ipaths differ -- this test works, but I'm not sure if this means If_expr is ok
    # (i.e. doesn't have the bug mentioned). But I guess it does... since I can't think of a more definitive test...
    # wait, maybe it's *not a bug* for If_expr to instantiate its args when it itself is *instantiated* -- tho it would be
    # if it did that when it was *evalled*. But right now it's not an OpExpr anyway, so it doesn't even *simplify* when evalled!
    # Which is a lack of optim, but not a bug. I suppose it means it never returns a local-ipath-mod... if it did I'd have seen
    # _then and _else in ipaths (before interning them).

# See if If_OpExpr works at all, and if so, works in that example. First see what it does when given too few args.
testexpr_29aox = TestIterator(If_OpExpr(True, testexpr_6f)) # TypeError: <lambda>() takes exactly 3 arguments (2 given) -- tolerable for now
testexpr_29ao  = TestIterator(If_OpExpr(True, testexpr_6f, TextRect("bug_else"))) # works, different ipaths
testexpr_29aox2  = TestIterator(If_OpExpr(False, testexpr_6f, TextRect("bug_else"))) # works, shows "bug_else" twice
testexpr_29aox3  = If_OpExpr(False, TextRect("True"), TextRect("False")) # -- works, shows "False"
    # note, we predict the old If used local ipath strings _then and _else, and the new one uses argnumbers supplied by OpExpr method.
    # This could be seen in the tests if we'd turn off ipath interning -- I ought to add an option for that, general
    # or for use when making kids of a specific instance (which would work now, since lexenv_ipath_Expr or whatever doesn't
    # intern it until it combines it with another ipath -- and could work later if it took an arg then for whether to intern it).
    # (this would take 5-10 minutes, so do it if I suspect any bugs in this ####e)
    # Q: should I switch over from If_expr to If_OpExpr (in implems, the name would be If_expr)?? #####e DECIDE -- note it's not done
    # in terms of a real implem, re default else clause, or refraining from even evalling (not just from instantiating) unused clauses

# == test dna_ribbon_view.py
testexpr_30 =  DNA_Cylinder() # works 070131 (has no DisplistChunk inside it)
testexpr_30a =  DisplistChunk(DNA_Cylinder()) # works 070131
    # (but it'd be more sensible to include DisplistChunk inside it instead, so it can have one per display style pref setting)

# try modifying testexpr_19g to put in some controls
testexpr_30b = World_dna_holder()
testexpr_30g = eval_Expr( call_Expr( lambda world_ui:
                                     Overlay( world_ui,
                                              DrawInCorner( Boxed(
                                                  eval_Expr( call_Expr( dna_ribbon_view_toolcorner_expr_maker, world_ui )) )) ),
                                     ## _app._i_instance(testexpr_30b)
                                     call_Expr( _app.Instance, testexpr_30b, "#30b")
                                     ))
testexpr_30h = eval_Expr( call_Expr( lambda world_ui: #070206
                                     Overlay( world_ui,
                                              DrawInCorner( Boxed(
                                                  eval_Expr( call_Expr( dna_ribbon_view_toolcorner_expr_maker, world_ui )) )),
                                              ## DrawInCorner( testexpr_18, (1,1) ), # works
                                              ## DrawInCorner( MT_try1(world_ui.world), (1,1) ), # semi-works -- autoupdate fails,
                                                  # and it prints "bug: expr or lvalflag for instance changed",
                                                  # and I know why -- see ###BUG comments 070206 in demo_MT.py.
                                                  # How to fix it is also described in there, but not yet attempted.
                                              DrawInCorner( MT_try1(getattr_Expr(world_ui, 'world')), (1,1) ), # predict same bug - yes.
                                             ),
                                     ## _app._i_instance(testexpr_30b)
                                     call_Expr( _app.Instance, testexpr_30b, "#30bh")
                                     ))

WORLD_MT_CORNER = (-1,1) # top right corner [changed from top left, 070210]

testexpr_30i = eval_Expr( call_Expr( lambda world_ui: #070207 -- just like 30h except MT_try1 -> MT_try2 
                                     Overlay( world_ui,
                                              DrawInCorner( Boxed(
                                                  eval_Expr( call_Expr( dna_ribbon_view_toolcorner_expr_maker, world_ui )) )),
                                              DrawInCorner( MT_try2(getattr_Expr(world_ui, 'world')), WORLD_MT_CORNER ),
                                             ),
                                     call_Expr( _app.Instance, testexpr_30b, "#30bi")
                                     ))

#070208 -- _30ix is like _30i except includes vv.reload_counter in world_ui make-index.
# No effect except when instance remade after modifying test.py (thus reloading it).
# Then, it remakes the world_ui (desired effect) but also the world itself (undesired effect, makes it lose its objects).
# Could be fixed by making the world separately; ultimately we want buttons for remaking various obj layers (incl model and ui);
# for now just live with it, meaning this _30ix is only useful rarely, for debugging.
from testdraw import vv
testexpr_30ix = eval_Expr( call_Expr( lambda world_ui: 
                                     Overlay( world_ui,
                                              DrawInCorner( Boxed(
                                                  eval_Expr( call_Expr( dna_ribbon_view_toolcorner_expr_maker, world_ui )) )),
                                              DrawInCorner( MT_try2(getattr_Expr(world_ui, 'world')), WORLD_MT_CORNER ),
                                             ),
                                     call_Expr( _app.Instance, testexpr_30b, "#30bi(%d)" % vv.reload_counter)
                                     ))

# == DraggableObject

testexpr_31 = DraggableObject(Rect(1,0.5,yellow)) # works [but see caveats in draggable.py]
    # [note: this can work even though Rect() has no .move (and no state of its own, so far), since we never try to flush motion;
    #  eventually what's needed is for Rect(), when coerced to ModelObject, to acquire enough position state to be moved ###e]

# == misc

testexpr_32 = IsocelesTriangle(1.5, 1, green) # works [after unstubbing of IsocelesTriangle from being equal to Rect, 070212]
    # fyi: so does _9b, which contains IsocelesTriangle

# === set the testexpr to use right now -- note, the testbed might modify this and add exprs of its own   @@@@

enable_testbed = True

testexpr = testexpr_30i # testexpr_19h # testexpr_18i ## testexpr_29aox3 ## testexpr_18 ## testexpr_9fx4 ##  _26g _28

    # as of 070121 at least these work ok in EVAL_REFORM with now-semipermanent kluge070119:
    # _2, _3a, _4a, _5, _5a, _10a, _10c, _9c, _9d, _9cx,
    # and finally _19d (bugfixed for non-ER case re ipath[0], and for ER case re delegate autoInstance).
    # The delegate autoInstance takes care of the last known bug in ER (IIRC, which is far from certain),
    # but a lot of tests have never been done in it.
    # Later: also _21g, _14, others.
    
    ## testexpr_24b
    ## testexpr_10c ## testexpr_9c
    ## testexpr_19d
    ## testexpr_9f ## testexpr_21g ## testexpr_20 ## Rect() # or _19c with the spheres

    ## testexpr_2 - a simple Rect
    ## testexpr_7c nested Boxed
    ## testexpr_9c column of two highlightables
        # testexpr_9cx has a bug, in highlightable with projection = True... the current_glselect cond fix attempt didn't fix it.
        # status 061209 eve: has debug prints, debug ideas are on paper, but for now I'll use a different method (not projection matrix)
        # for doing things like DrawInCorner1. [not using overrider doesn't fix it.]
        # status 070122: seemed to work recently in ER, don't know why, details commented next to the test.
        #
        # BUG in testexpr_9c (later: and all other highlightables), noticed 061210 morn g4:
        # a rapid motion onto the Highlightable doesn't highlight it, tho it does update sbar text.
        # Only the next motion highlights it. I wonder if it's related to gl_update and usage-tracking sync issues.
        # ... discussion is in BUGS file. Might be fixed now.
    ## testexpr_9fx4 - use of _this(Highlightable).attr to determine Rect color; _9fx6 with missing args (warning but works)
    ## testexpr_10c double-nested toggleshow of highlightable rect
    ## testexpr_11r1b image with black padding; _11s1 highlightable stretched image
    ## testexpr_13z4 red/blue image
    ## testexpr_14 array of hidden-state icons for MT (from cad/images) (change if 0 to if 1 to see non-hidden icons) [retested 070122]
    ## testexpr_15d ChoiceColumn [briefly retested 070122]
    ## testexpr_16 state test  (testexpr_16c for controlling origin axes)
    ## testexpr_18 model tree demo using MT_try1
    ## testexpr_19g GraphDrawDemo_FixedToolOnArg1 -- works [070122]; for non-ER the last tested was _19f; older _19d lacks clear button
    ## testexpr_20 four DrawInCorners (works but highlighting is slow)
    ## testexpr_21e table of alignment testers; _21g same in class form -- update 070122: works in EVAL_REFORM too --
        # after I fixed 3 bugs, including adding a mostly-complete pure-expr __eq__ (which has loose ends in Expr.__eq__ comments,
        # which don't affect testexpr_21g/_21e).
    ## testexpr_22 ChoiceRow (in corner)
    ## testexpr_23bh2 DisplistChunk

    # works: _11i, k, l_asfails, m; doesn't work: _11j, _11n  ## stable: testexpr_11k, testexpr_11q11a [g4],
    # testexpr_11ncy2 [stopsign], testexpr_11q5cx2_g5_bigbad [paul notebook, g5, huge non2pow size] testexpr_14 [hide_icons]

    # latest stable tests: _11k, _10c
    # testexpr_5d, and testexpr_6f2, and Boxed tests in _7*, and all of _8*, and testexpr_9c, and _10d I think, and _11d3 etc
    
    # currently under devel [061126]: demo_MT, and need to revamp instantiation, but first make test framework, thus finish PixelGrabber

    # some history:
    # ... after extensive changes for _this [061113 932p], should retest all -- for now did _3x, _5d, _6a thru _6e, and 061114 6g*, 6h*

# ==

def get_redraw_counter(): #070108
    "#doc [WARNING: this is not a usage/change-tracked attribute!]"
    import env
    return env.redraw_counter

_lval_for_redraw_counter = Lval_which_recomputes_every_time( get_redraw_counter) #070108

def get_redraw_counter_ALWAYSCHANGES(): #070108 experiment -- useless, since it correctly causes an unwanted gl_update after every redraw!
    "like get_redraw_counter() but act as if we use something which changes every time (usage/change tracked the max legal amount)"
    return _lval_for_redraw_counter.get_value()

from preferences import _NOT_PASSED ###k

def get_pref(key, dflt = _NOT_PASSED): #e see also... some stateref-maker I forget
    """Return a prefs value. Fully usage-tracked.
    [Kluge until we have better direct access from an expr to env.prefs. Suggest: use in call_Expr.]
    """
    import env
    return env.prefs.get(key, dflt)

debug_prints_prefs_key = "A9 devel/debug prints for my bug?" # also defined in GLPane.py

bottom_left_corner = Boxed(SimpleColumn(
##    checkbox_pref("A9 devel/testdraw/use old vv.displist?", "use old vv.displist?"), # see USE_DISPLAY_LIST_OPTIM
##    checkbox_pref("A9 devel/testdraw/drawtest in old way?", "drawtest in old way?", dflt = False),
##    checkbox_pref("A9 devel/testdraw/use GLPane_Overrider?", "use GLPane_Overrider? (after reload)", dflt = True), # works (moves compass)
    checkbox_pref("A9 devel/testdraw/super.Draw?", "draw model & region-sel rect?", dflt = True), # works
    checkbox_pref("A9 devel/testdraw/show old timing data?", "show old timing data?", dflt = False), # works (side effect on text in next one)
    checkbox_pref("A9 devel/testdraw/show old use displist?", "show old use displist?", dflt = False), # works
    checkbox_pref("A9 devel/testdraw/draw test graphics?", "draw old test graphics?", dflt = False), # works, but turns off above two too (ignore)
    checkbox_pref(debug_prints_prefs_key, "debug prints for redraw?", dflt = False), # note prefs_key text != checkbox label text
    checkbox_pref("A9 devel/show redraw_counter?", "show redraw_counter?", dflt = False), # works, but has continuous redraw bug
    Highlightable(DisplistChunk(
        CenterY(TextRect( format_Expr("instance remade at redraw %r", call_Expr(get_redraw_counter)))) )),
            # NOTE: not usage/change tracked, thus not updated every redraw, which we depend on here
    ## CenterY(TextRect( format_Expr("current redraw %r [BUG: CAUSES CONTINUOUS REDRAWS]", call_Expr(get_redraw_counter_ALWAYSCHANGES)))),
    If( call_Expr(get_pref, "A9 devel/show redraw_counter?", False),
        # 070124 disabled both orders of Highlightable(DisplistChunk(, since fuzzy during highlighting after my testdraw.py fixes
        ##Highlightable(DisplistChunk( CenterY(TextRect( format_Expr("current redraw %r", _app.redraw_counter))) )), 
        ## DisplistChunk (Highlightable( CenterY(TextRect( format_Expr("current redraw %r", _app.redraw_counter))) )),
        # 070124 just don't use a displist, since it'd be remade on every draw anyway (except for glselect and main in same-counted one)
        Highlightable( CenterY(TextRect( format_Expr("current redraw %r", _app.redraw_counter))) ),
            # should be properly usage/change tracked; has continuous redraw bug, not yet understood.
            # note: after checking the checkbox above, the bug shows up only after the selobj changes away from that checkbox.
            # update 070110 1040p: the bug is fixed in GLPane.py/changes.py; still not fully understood; more info to follow. ###e
        Highlightable(DisplistChunk(TextRect("current redraw: use checkbox (bug is fixed)"))) ####
    ),
    Highlightable(DisplistChunk( CenterY(TextRect( format_Expr("testname: %r", _app.testname))) )),
 ))
    # cosmetic bugs in this: mouse stickiness on text label (worse on g4?) [fixed], and label not active for click [fixed],
    # but now that those are fixed, highlighting of text changes pixel alignment with screen,
    # and Boxed not resizable, and labels wouldn't grow if it was (and they're not long enough, tho that'd be ok if they'd grow),
    # and reload is pretty slow since we're not caching all this testbed stuff (at least I guess that's why)

top_left_corner = None # testexpr_18i
    # testexpr_10c # nested ToggleShow. -- works, usual 
    # testexpr_18 # (MT_try1) also works, and has indep node.open state, i think (limited autoupdate makes it hard to be sure).
    # update 070206: testexpr_18 mostly works, but has a funny alignment issue. ###BUG (but can ignore for now)

class AppOuterLayer(DelegatingInstanceOrExpr): #e refile when works [070108 experiment]
    "helper class for use in testbed, to provide glue code between testexpr and the rest of NE1"
    redraw_counter = State(int)
    testname = State(str)#070122
    delegate = Arg(Anything) # might need to delegate lbox attrs (or might not, not sure, but no harm in doing it)
    def draw(self):
        import env
##        print "changes._print_all_subs = True"
##        changes._print_all_subs = True ####
        self.redraw_counter = env.redraw_counter # assume this set is subject to LvalForState's same_vals->noinval optimization #k verify
##        changes._print_all_subs = False
##        print "changes._print_all_subs = False"
        ## (note: that set caused no warning, even when done twice. Why not, since it's during recomputation that used it?? #k)
        # THEORY OF CONTIN REDRAW BUG WHEN THIS IS USED IN DRAWING:
        # the use last time means the set above does gl_update during this repaint. ... but the details of how & why are elusive...
        # (Would a separate lval for each draw fix it? would some kind of clear or ignore of invals at the right time fix it?
        #  the right time for the inval from this set right now is *now* in terms of changing what the redraw will do,
        #  but *never* in terms of causing the gl_update from our caller's use of this here. Not sure how to fix that. ####k 070109)
        self.testname = ', '.join(testnames)
        if get_pref(debug_prints_prefs_key):
            print "AppOuterLayer: before delegate draw", env.redraw_counter###
        self.drawkid( self.delegate) ## self.delegate.draw()
        if get_pref(debug_prints_prefs_key):
            print "AppOuterLayer: after delegate draw", env.redraw_counter###
    ###e need an env for args which binds some varname to self (dynamically), so the args have some way to access our state
    def env_for_arg(self, index):
        env = self.env_for_args #e or could use super of this method [better #e]
        if index == 0: #KLUGE that we know index for that arg (delegate, arg1)
            env = env.with_lexmods(dict(_app = self)) # something to provide access to self under the name _app (for now)
                # NOTE: this is meant to be a dynamic binding.
                # It might work anyway, given how it's used (inside & outside this expr) -- not sure. ##k
                # See comments in widget_env.py about needed lexical/dynamic cleanup.
        return env
    pass
        
def testbed(expr):
    "this turns the current testexpr into the actual expr to render"
    ## return Overlay(expr, Closer(Rect(1,1,black), 3.4)) #stub
    ## return Overlay(expr, If(1,DrawInCorner1,Closer)(Highlightable(Rect(1,1,black),Rect(1,1,green),projection=True)))
    ## return Overlay(expr, DrawInCorner(Highlightable(Rect(1,1,black),Rect(1,1,green)) ))
    return AppOuterLayer( # [note: defines _app in dynenv]
        Overlay( expr,
                 
##                 ## or maybe: WithEnv(expr, _env = access to app state, env module, etc ...) or, intercept .draw and run special code...
##                 ## _WrapDrawMethod(expr, ...)... with code to copy app state into instance State -- of what instance? smth in env...
                 DrawInCorner( top_left_corner, (-1,1)), # some sort of MT on top left
                 ## testexpr_20a,
                 DrawInCorner( bottom_left_corner, (-1,-1)), # checkboxes on bot left [note: contains _app as ref to dynenv]
                 ####BUG: the _app ref in this works now, except it triggers continuous redraw, not sure why.
                 # the bug when it didn't work was not lex/dyn confusion, it was just that the _app use was not in the scope of its
                 # definition.
                )
     )

if not enable_testbed:
    testbed = identity

 #e what next, planned optims, nim tests -- see below

testnames = [] # note: we show this in the testbed via _app, like we show current redraw [070122]

print "using testexpr %r" % testexpr
for name in dir():
    if name.startswith('testexpr') and name != 'testexpr' and eval(name) is testexpr:
        print "(which is probably %s)" % name
        testnames.append(name)


# == @@@

#e what next?   [where i am, or should be; updated 061126 late]
# - some boolean controls?
#   eg ChoiceButton in controls.py -- requires StateRef (does a property count as one?), maybe LocalState to use nicely
# - framework to let me start setting up the dna ui?
#   - just do a test framework first (simpler, needed soon); described in PixelGrabber
# - working MT in glpane? yes, demo_MT.py; seems to require revamp of instantiation (separate it from IorE-expr eval)

# == nim tests

# Column, fancy version
## testexpr_xxx = Column( Rect(4, 5, white), Rect(1.5, color = blue)) # doesn't work yet (finishing touches in Column, instantiation)

# @@@

# BTW, all this highlighting response (e.g. testexpr_9c) is incredibly slow.
# Maybe it's even slower the first time I mouseover the 2nd one, suggesting that instantiation time is slow,
# but this doesn't make sense since I reinstantiate everything on each draw in the current code. hmm.

# PLANNED OPTIMS (after each, i need to redo lots of tests):
# - don't always gl_update when highlighting -- requires some code review (or experiment, make it turnable off/on)
# - retain the widget_env and the made testexpr between drawings, if no inputs changed (but not between reloads)
# - display lists (I don't yet know which of the above two will matter more)
# - simplify exprs, like the grabarg one
#   - related (maybe needed as part of that): know which attrvals are "final", and which methods are deterministic (by attrname).
# - some optims mentioned in StatePlace - faster & denser storage, and kinds of state with no usage/mod tracking.
# - in Lval: self.track_use() # (defined in SelfUsageTrackingMixin) ###e note: this will need optimization
# but first, make a state-editing example using Button.

# "intentional deferred loose ends"
# - iterators, and separation of expreval/instantiation (same thing? not sure)
# - geom data types (eg Point) with relative coords; good system for transforms in things like Translate
# - highlighting that works in displists
# - povray


# == per-frame drawing code

_kluge_current_testexpr_instance = None
    # new feature 070106 for use by other modules such as demo_drag, but it's deprecated at birth and may never be used.
    # WARNING: if enable_testbed is set, this is actually an instance of testbed(testexpr), not of testexpr alone,
    # and there's no simple way to find the instance of testexpr inside it (even assuming there's exactly one instance,
    # which is only a convention).

def drawtest1_innards(glpane):
    "entry point from ../testdraw.py (called once per mode.Draw call)"

    mode = glpane.mode # assume this is always testmode
    _setup_UNKNOWN_SELOBJ(mode) #061218 kluge (multiple places, some in cad/src);
        # fixes "highlight sync bug" in which click on checkbox, then rapid motion away from it,
        # then click again, could falsely click the same checkbox twice.
    
    glpane
    staterefs = _state ##e is this really a stateplace? or do we need a few, named by layers for state?
        #e it has: place to store transient state, [nim] ref to model state
    
    inst = find_or_make_main_instance(glpane, staterefs, testexpr, testbed)
        # for testbed changes to have desired effect, we'll need to switch them among __eq__-comparable choices (like exprs)
        # rather than among defs, or editing one def, like we do now... not sure it's easy to make it an expr though;
        # but when it is, change to that to improve this. ##e

    global _kluge_current_testexpr_instance
    _kluge_current_testexpr_instance = inst
    
    from basic import printnim, printfyi

    if 'kluge':
        #### KLUGE: get back to the standard drawing coords
        # (only works since exactly one level of this is pushed since mode.Draw is entered, and we control all that code)
        glPopMatrix()
        glPushMatrix()

    inst.draw() # can't use self.drawkid -- we're not an IorE instance (just a function)
    if not glpane.is_animating: # cond added 061121, but will probably need mod so we print the first & last ones or so... #e
        if not glpane.in_drag: # subcond added 061208; should be easily controllable;
                # might be problematic if *all* drag-caused redraws are not printed, but I'm guessing the last one will be [##k].
                # it turns out, it is in some cases and not others.
                # if this is a problem, or if in_drag redraws matter, also consider printing ".", for them. In fact, try this now.
            import env
            ##print "drew", env.redraw_counter   ##e or print_compact_stack
            sys.stdout.write(";")
            sys.stdout.flush()
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
        # Note: this shows it often draws one frame twice, not at the same moment, presumably due to GLPane highlighting alg's
        # glselect redraw. That is, it draws a frame, then on mouseover of something, draws it glselect, then immediately
        # draws the *next* frame which differs in having one object highlighted. (Whereas on mouse-leave of that something,
        # it only redraws once, presumably since it sees the infinite depth behind the mousepos, so it doesn't need the glselect draw.)
        #    That behavior (drawing a new frame with a highlighted object) sounds wrong to me, since I thought it
        # would manage in that case to only draw the highlighted object (and to do it in the same paintGL call as the glselect),
        # but it's been awhile since I analyzed that code. Or maybe it has a bug that makes it do an extra gl_update, or maybe our
        # own code does one for some reason, or maybe it's code I added to selectMode for drag_handler support that does it.
        # (That last seems likely, since that code has a comment saying it's conservative and might often be doing an extra one;
        #  it also lets the drag_handler turn that off, which might be an easy optim to try sometime. ####)
        # When the time comes (eg to optim it), just use print_compact_stack here. [061116 comment]
        printnim("see code for how to optim by replacing two redraws with one, when mouse goes over an object") # see comment above
    return

# ==  what to draw in the corner @@@@ ###NIM for now

## corner_expr = Rect(3,2,red)
corner_expr = testexpr_16c # works to show it, but it doesn't work as a control since it doesn't get highlighted!!! ###LOGIC BUG

# ==

MEMOIZE_MAIN_INSTANCE = True      # whether to memoize it across redraws, without reloads

MEMOIZE_ACROSS_RELOADS = False    # whether to memoize it across reloads
    ###BUG: False seems to not be working for demo_MT, 061205... ah, the intent might have been "printed reloads of testdraw"
    # but the code looks for reloads of this module test.py! Which often correspond but not always!
    # Solution: include testdraw.vv.reload_counter in the data, when this is false.


try:
    _last_main_instance_data
except:
    # WARNING: duplicated code, a few lines away
    _last_main_instance_data = (None, None, None, None, None)
    _last_main_instance = None
else:
    # reloading
    if not MEMOIZE_ACROSS_RELOADS:
        # WARNING: duplicated code, a few lines away
        _last_main_instance_data = (None, None, None, None, None)
        _last_main_instance = None
    pass

def find_or_make_main_instance(glpane, staterefs, testexpr, testbed): #061120; got testbed 061208
    if not MEMOIZE_MAIN_INSTANCE:
        return make_main_instance(glpane, staterefs, testexpr, testbed)
    global _last_main_instance_data, _last_main_instance
    from testdraw import vv
    new_data = (glpane, staterefs, testexpr, testbed, MEMOIZE_ACROSS_RELOADS or vv.reload_counter ) # revised as bugfix, 061205
        # note: comparison data doesn't include funcs & classes changed by reload & used to make old inst,
        # including widget_env, Lval classes, etc, so when memoizing, reload won't serve to try new code from those defs
    if new_data != _last_main_instance_data:
        old = _last_main_instance_data
        _last_main_instance_data = new_data
        res = _last_main_instance = make_main_instance(glpane, staterefs, testexpr, testbed)
        print "\n**** MADE NEW MAIN INSTANCE %s ****\n" % time.asctime(), res, \
              "(glpane %s, staterefs %s, testexpr %s, testbed %s, reloads %s)" % _cmpmsgs(old, new_data)
    else:
        res = _last_main_instance
        ## print "reusing main instance", res
    return res

def _cmpmsgs(d1, d2):
    """return e.g. ("same", "DIFFERENT", "same") to show how d1 and d2 compare using == at corresponding elts"""
    assert len(d1) == len(d2)
    res = [_cmpmsg(d1[i], d2[i]) for i in range(len(d1))]
    return tuple(res) # tuple is required for this to work properly with print formatting

def _cmpmsg(e1,e2):
    return (e1 == e2) and "same" or "DIFFERENT"

def make_main_instance(glpane, staterefs, testexpr, testbed):
    some_env = widget_env(glpane, staterefs)
    inst = some_env.make(testbed(testexpr), NullIpath)
    return inst

class _find_or_make: #061217 from find_or_make_main_instance etc #e refile ### NOT YET USED
    """Helper class for caching made things when the input data hasn't changed.
    (Note that it is up to you to not accidentally discard and remake instances of this class itself, e.g. upon module reload.
     Or maybe we'll let you do it, and have this class store its data elsewhere... that might be more convenient,
     especially during development of this class.)
    If you want a "remake button" for such a thing, let the button increment a counter which is part of the input data.
    If you want an "always remake" button, let it control whether an always-changing counter gets included in the data or not.
    If the data is positional, then include a constant in place of anything you sometimes leave out.
    """
    def __init__(self, printname = None): #e makefunc? cacheplace?
        self.old_data = None
        self.printname = printname
    def find_or_make(self, *data_args, **data_kws):
        if 0: ## not MEMOIZE_MAIN_INSTANCE:
            return self.make(*data_args, **data_kws) #e store in self.res?
        for i in range(len(data_args)):
            data_kws[i] = data_args[i] ###k only safe if passing a dict via ** always copies it!
        new_data = data_kws #k ok since dict.__eq__ does what i want
        if not same_vals( new_data, self.old_data): # use same_vals to avoid the bug in != for "Numeric array in tuple"
            # remake, but first explain why
            old_data = self.old_data
            self.old_data = new_data
            if self.printname:
                print "remaking %r, because",
                if old_data is None:
                    print "not made before"
                else:
                    # make sure keys are the same
                    k1 = old_data.keys()
                    k2 = new_data.keys()
                    k1.sort()
                    k2.sort()
                    if k1 != k2:
                        print "data keys changed (bug?)"
                    else:
                        for k in k1:
                            if not same_vals(old_data[k], new_data[k]):
                                print "%s DIFFERENT" % k,
                            else:
                                print "%s same" % k,
                        print
                    pass
                pass
            res = self.res = self.make(*data_args, **data_kws)
##            print "\n**** MADE NEW MAIN INSTANCE %s ****\n" % time.asctime(), res, \
##                  "(glpane %s, staterefs %s, testexpr %s, testbed %s, reloads %s)" % _cmpmsgs(old, new_data)
        else:
            res = self.res
            ## print "reusing %s" % self.printname, res
        return res
    def make(self):
        assert 0, "subclass should implement" ### or use a self.func
    pass
    
# ==

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
    session_state = {}    ### NOT YET USED as of 061120

per_reload_state = {}     ### NOT YET USED as of 061120

# also per_frame_state, per_drag_state ... maybe state.per_frame.xxx, state.per_drag.xxx...

# ==

# one-time tests: to do them, change if 0 to if 1:

if 0:
    class something(InstanceOrExpr):#070123
        attr1 = Arg(int)
        attr2 = attr1 # do we get a warning? yes (but it's not understandable -- that could be fixed).
        ## formula <...> already in replacements -- error?? its rhs is <..._self.attr1...>; new rhs would be for attr 'attr2'
        pass    
if 0:
    # above warning mentions in order attr1, attr2. does that depend on this order here? let's find out in this next test:
    class something(InstanceOrExpr):
        attr2 = Arg(int)
        attr1 = attr2 # in what order does the warning mention these attrs? same order as before: attr1 then attr2.
if 0:
    # what if I ask Arg() to record locals().keys() when it runs? Won't help, even if it works -- when it runs, *neither*
    # of these attrs will be defined in locals. Even so, does it work at all?? Yes.
    class something(InstanceOrExpr):
        print locals().keys() # ['__module__']
        attr2 = 0
        print locals().keys() # ['__module__', 'attr2']
        attr1 = 0
        print locals().keys() # ['__module__', 'attr2', 'attr1']
        pass
# end
