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

import changes
changes._debug_standard_inval_nottwice_stack = False
changes._debug_standard_inval_twice = False # WARNING: this hides the pseudobug [061207]
changes._debug_standard_inval_twice_stack = False

# == local imports with reload

import basic
basic.reload_once(basic)
del basic

from basic import * # including reload_once, and some stubs
from basic import _self, _this, _my

import Rect
reload_once(Rect)
from Rect import Rect, RectFrame, IsocelesTriangle, Spacer, Sphere

import Column
reload_once(Column)
from Column import Column, SimpleColumn, SimpleRow

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import Boxed
reload_once(Boxed)
from Boxed import Boxed_old, CenterBoxedKluge, CenterBoxedKluge_try1, Boxed

import transforms
reload_once(transforms)
from transforms import Translate, Closer

import Center
reload_once(Center)
from Center import * # e.g. Center, TopRight, CenterRight, Right; not yet complete, mostly working (see specific tests) [061211 112p] 

import TestIterator
reload_once(TestIterator)
from TestIterator import TestIterator

import TextRect
reload_once(TextRect)
from TextRect import TextRect

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable, Button, print_Expr

import ToggleShow
reload_once(ToggleShow)
from ToggleShow import ToggleShow

import images
reload_once(images)
from images import Image, IconImage, PixelGrabber

import controls
reload_once(controls)
from controls import ChoiceButton, ChoiceColumn, checkbox_v3 #e rename

import staterefs
reload_once(staterefs)
from staterefs import PrefsKey_StateRef

import Set
reload_once(Set)
from Set import Set ##e move to basic

import MT_demo #e rename? put in subdir?
reload_once(MT_demo)
from MT_demo import MT, test_drag_pixmap

import demo_drag
reload_once(demo_drag)
from demo_drag import GraphDrawDemo_FixedToolOnArg1, kluge_dragtool_state_checkbox_expr

import projection
reload_once(projection)
from projection import DrawInCorner1, DrawInCorner

# == @@@

import widget_env
reload_once(widget_env)
from widget_env import widget_env

import instance_helpers
reload_once(instance_helpers)
from instance_helpers import DelegatingMixin # needed only in DebugPrintAttrs, which i should refile

from OpenGL.GL import glPopMatrix, glPushMatrix

# == make some "persistent state"

try:
    _state
except:
    _state = {} ###e Note: this is used for env.staterefs as of bfr 061120; see also session_state, not yet used, probably should merge

# == debug code #e refile

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
        for name in attrs:
            print "guy.%s is" % name, getattr(guy,name,"<unassigned>")
##        ##DelegatingInstance_obs.draw(self, *args) # this fails... is it working to del to guy, but that (not being instance) has no .draw??
##        printnim("bug: why doesn't DelegatingInstance_obs delegate to guy?") # since guy does have a draw
##        # let's try it more directly:
        # super draw, I guess:
        return guy.draw(*args) ### [obs cmt?] fails, wrong # args, try w/o self
    pass

#e refile:
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
DebugDraw = DebugPrintAttrs

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

testexpr_9c = SimpleColumn(testexpr_9a, testexpr_9b) # works (only highlighting tested; using 'stubs 061115')

testexpr_9d = testexpr_9b( on_release_in = print_Expr('release in, customized')) # works
    # test customization of option after args supplied

testexpr_9e = testexpr_9b( on_release_in = None) # works
    # test an action of None (should be same as a missing one) (also supplied by customization after args)

testexpr_9cx = SimpleColumn(testexpr_9a, testexpr_9b(projection = True)) ###BUG -- that option breaks the functionality.
    # guess: it might mess up the glselect use of the projection matrix. (since ours maybe ought to be multiplied with it or so)

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
                                          ideal_height = 1647) # try huge texture, non2pow size -- actually works! [bruce's g5]

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

if 0:
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
testexpr_14 = Translate(testexpr_14, V(0,1,0) * 2)
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
testexpr_16c = SimpleColumn( 
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


# == MT_demo

testexpr_18 = MT( _my.env.glpane.assy.part.topnode )
    # works! except for ugliness, slowness, and need for manual update by reloading.
    #e Still need to test: changing the current Part. Should work, tho manual update will make that painful.
    ###e need better error message when I accidently pass _self rather than _my]

testexpr_18a = test_drag_pixmap( _my.env.glpane.assy.w.mt, _my.env.glpane.assy.part.topnode ) # nim, otherwise works -- debug prints


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
        return aligntest(af)
    except:
        return BottomRight(TextRect("didn't work: %r" % afname,1,30))
    pass

testexpr_21d = aligntest(Center)

colwords = ('Left', 'Center', 'Right', '')
rowwords = ('Top', 'Center', 'Bottom', '')
## choiceref_21e = LocalVariable_StateRef(str, "") ###k ok outside anything? it's just an expr, why not? but what's it rel to? var name???
    # answer: each instance has its own state, so it won't work unless shared, e.g. in InstanceMacro or if we specify sharing somehow.
choiceref_21e = PrefsKey_StateRef("A9 devel scratch/testexpr_21e alignfunc", 'Center') # need a non-persistent variant of this... ###e
def mybutton(xword, yword, choiceref):
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
    identity(eval_Expr)( call_Expr( aligntest_by_name, getattr_Expr(choiceref_21e, 'value'))) ,
    TopLeft( Boxed(table_21e))
                        ), (-6,0) )
    # needed bugfix: choiceref_21e.value -> getattr_Expr(choiceref_21e, 'value') -- is there a better way?? ###e
    # ditto for call of aligntest on that -> call_Expr -- and eval_Expr (if it works) which is a ###KLUGE -- need better way for sure.

    # all 15 primitives in the table are defined and working as of 061211 eve

testexpr_21f = Boxed( identity(Center)( Rect(2,3.5,purple))) # test lbox translation by Center -- works
    # (implem of lbox shift is in Translate, so no need to test all alignment prims if this works)

# === set the testexpr to use right now -- note, the testbed might modify this and add exprs of its own   @@@@

enable_testbed = False

testexpr = testexpr_21f ## testexpr_20 ## Rect() # or _19c with the spheres

    ## testexpr_7c nested Boxed
    ## testexpr_9c column of two highlightables
        # testexpr_9cx has a bug, in highlightable with projection = True... the current_glselect cond fix attempt didn't fix it.
        # status 061209 eve: has debug prints, debug ideas are on paper, but for now I'll use a different method (not projection matrix)
        # for doing things like DrawInCorner1. [not using overrider doesn't fix it.]
        #
        # BUG in testexpr_9c (later: and all other highlightables), noticed 061210 morn g4:
        # a rapid motion onto the Highlightable doesn't highlight it, tho it does update sbar text.
        # Only the next motion highlights it. I wonder if it's related to gl_update and usage-tracking sync issues.
        # ... discussion is in BUGS file. Might be fixed now.
    ## testexpr_10c double-nested toggleshow of highlightable rect
    ## testexpr_11r1b image with black padding
    ## testexpr_13z4 red/blue image
    ## testexpr_15d ChoiceColumn
    ## testexpr_16 state test  (testexpr_16c for controlling origin axes)
    ## testexpr_18 model tree demo
    ## testexpr_19b = GraphDrawDemo_FixedToolOnArg1 -- works, but the tool remains IN DEVEL ###
    ## testexpr_20 - four DrawInCorners (works but highlighting is slow)


    # works: _11i, k, l_asfails, m; doesn't work: _11j, _11n  ## stable: testexpr_11k, testexpr_11q11a [g4],
    # testexpr_11ncy2 [stopsign], testexpr_11q5cx2_g5_bigbad [paul notebook, g5, huge non2pow size] testexpr_14 [hide_icons]

    # latest stable tests: _11k, _10c
    # testexpr_5d, and testexpr_6f2, and Boxed tests in _7*, and all of _8*, and testexpr_9c, and _10d I think, and _11d3 etc
    
    # currently under devel [061126]: MT_demo, and need to revamp instantiation, but first make test framework, thus finish PixelGrabber

    # some history:
    # ... after extensive changes for _this [061113 932p], should retest all -- for now did _3x, _5d, _6a thru _6e, and 061114 6g*, 6h*

    #obs cmt: buglike note 061112 829p with _5a: soon after 5 reloads it started drawing each frame twice
    # for no known reason, ie printing "drew %d" twice for each number; the ith time it prints i,i+1. maybe only after mouse
    # once goes over the green rect or the displist text (after each reload)? not sure. [later realized it's just the glselect redraw.]

def testbed(expr):
    "this turns the current testexpr into the actual expr to render"
    ## return Overlay(expr, Closer(Rect(1,1,black), 3.4)) #stub
    ## return Overlay(expr, If(1,DrawInCorner1,Closer)(Highlightable(Rect(1,1,black),Rect(1,1,green),projection=True)))
    ## return Overlay(expr, DrawInCorner(Highlightable(Rect(1,1,black),Rect(1,1,green)) ))
    return Overlay(expr, testexpr_20a)


if not enable_testbed:
    testbed = identity

 #e what next, planned optims, nim tests -- see below

print "using testexpr %r" % testexpr
for name in dir():
    if name.startswith('testexpr') and name != 'testexpr' and eval(name) is testexpr:
        print "(which is probably %s)" % name

# == @@@

#e what next?   [where i am, or should be; updated 061126 late]
# - some boolean controls?
#   eg ChoiceButton in controls.py -- requires StateRef (does a property count as one?), maybe LocalState to use nicely
# - framework to let me start setting up the dna ui?
#   - just do a test framework first (simpler, needed soon); described in PixelGrabber
# - working MT in glpane? yes, MT_demo.py; seems to require revamp of instantiation (separate it from IorE-expr eval)

# == nim tests

# TestIterator (test an iterator - was next up, 061113/14, but got deferred, 061115)
testexpr_7_xxx = TestIterator( testexpr_3 ) # looks right, but it must be faking it (eg sharing an instance?) ###
testexpr_7a_xxx = TestIterator( Boxed(testexpr_6f) )
    ### BUG: shows (by same ipaths) that TestIterator is indeed wrongly sharing an instance
    # [first test that succeeds in showing this rather than crashing is 061115 -- required fixing bugs in Boxed and what it uses]
    # note: each testexpr_6f prints an ipath

# Column, fancy version
testexpr_xxx = Column( Rect(4, 5, white), Rect(1.5, color = blue)) # doesn't work yet (finishing touches in Column, instantiation)

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

def drawtest1_innards(glpane):
    "entry point from ../testdraw.py (called once per mode.Draw call)"
    ## print "got glpane = %r, doing nothing for now" % (glpane,)

    glpane
    staterefs = _state ##e is this really a stateplace? or do we need a few, named by layers for state?
        #e it has: place to store transient state, [nim] ref to model state
    
    inst = find_or_make_main_instance(glpane, staterefs, testexpr, testbed)
        # for testbed changes to have desired effect, we'll need to switch them among __eq__-comparable choices (like exprs)
        # rather than among defs, or editing one def, like we do now... not sure it's easy to make it an expr though;
        # but when it is, change to that to improve this. ##e
    
    from basic import printnim, printfyi

    if 'kluge':
        #### KLUGE: get back to the standard drawing coords
        # (only works since exactly one level of this is pushed since mode.Draw is entered, and we control all that code)
        glPopMatrix()
        glPushMatrix()

    inst.draw()
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
    ###BUG: False seems to not be working for MT_demo, 061205... ah, the intent might have been "printed reloads of testdraw"
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

# ==

def after_drawcompass(glpane, aspect):
    return # "nevermind"

# in after_drawcompass-outtakes.py:
##def make_aux_instance(expr, index): #KLUGE 061208; not memoized, that'll need fixing
##    global _last_main_instance
##    some_env = _last_main_instance.env
##    ipath = (index, ('$$aux', NullIpath))
##    inst = some_env.make(expr, ipath)
##    return inst
##
##def after_drawcompass(glpane, aspect):
##    ...
    
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

# end
