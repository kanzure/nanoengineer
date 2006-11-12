'''
current bugs [061013]:

- reload_once does it too often -- should be only when i do the reload effect from testmode/testdraw in cad/src
  (ie base it on that counter, not the redraw counter, but be sure that counter incrs before any imports)
- lots of things are nim, including drawtest1_innards

$Id$
'''

#e during devel, see drawtest1_innards for main entry point from testdraw.py

# == imports from parent directory

# (none yet)

# == local imports with reload

import basic
basic.reload_once(basic)
del basic

from basic import * # including reload_once, and some stubs

import Rect
reload_once(Rect)
from Rect import Rect_old, Rect, RectFrame

import Column
reload_once(Column)
from Column import Column

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import Boxed
reload_once(Boxed)
from Boxed import Boxed

import widget_env
reload_once(widget_env)
from widget_env import widget_env

import instance_helpers
reload_once(instance_helpers)
from instance_helpers import DelegatingInstance_obs, DelegatingMixin

# == make some "persistent state"

try:
    _state
except:
    _state = {}

# == debug code #e refile

class DebugPrintAttrs(Widget, DelegatingMixin):#k guess 061106; revised 061109, works now (except for ArgList kluge)
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
testexpr_1 = Rect_old(7,5, color = green) # works as of 061030

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

testexpr_5 = Boxed( Rect(2,3.5,green)) # doesn't work yet (gets attrerror: draw, as predicted until _value works)

testexpr_6 = Column( testexpr_1, Rect(1.5, color = blue)) # doesn't work yet (finishing touches in Column, instantiation)

testexpr_7 = ToggleShow( testexpr_2 ) # test use of Rules, If, toggling...

testexpr_8 = TestIterator( testexpr_3 ) # test an iterator

# == set the testexpr to use right now

testexpr = testexpr_5 # usually testexpr_5

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
