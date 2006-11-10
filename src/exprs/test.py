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

import Boxed
reload_once(Boxed)
from Boxed import Boxed

import widget_env
reload_once(widget_env)
from widget_env import widget_env

import instance_helpers
reload_once(instance_helpers)
from instance_helpers import DelegatingInstance

# == make some "persistent state"

try:
    _state
except:
    _state = {}

# == debug code #e refile

class DelegatingMixin: pass ##stub

class DebugPrintAttrs(Widget, DelegatingMixin):#k guess 061106
    """delegate to our only arg, but whenever we're drawn, before drawing that arg,
    print its attrvalues listed in our other args
    """ #k guess 061106
    #e obscmt: won't work until we make self.args autoinstantiated [obs since now they can be, using Arg or Instance...]
    delegate = Arg(Anything) #k guess 061106 ###IMPLEM Anything
        #k when it said Arg(Widget): is this typedecl safe, re extensions of that type it might have, like Widget2D?
        #k should we leave out the type, thus using whatever the arg expr uses? I think yes, so I changed the type to Anything.
    attrs = ArgList(str)
    def draw(self, *args): #e or do this in some init routine?
        ## guy = self.args[0] ##### will this be an instance?? i doubt it
        guy = self.delegate
        print "guy = %r, guy._e_is_instance = %r" % (guy, guy._e_is_instance)
        ## attrs = self.args[1:]
        attrs = self.attrs
        for name in attrs:
            print "guy.%s is" % name, getattr(guy,name,"<unassigned>")
##        ##DelegatingInstance.draw(self, *args) # this fails... is it working to del to guy, but that (not being instance) has no .draw??
##        printnim("bug: why doesn't DelegatingInstance delegate to guy?") # since guy does have a draw
##        # let's try it more directly:
        # super draw, I guess:
        return guy.draw(*args) ### [obs cmt?] fails, wrong # args, try w/o self
    pass

# == testexprs

# === test basic leaf primitives
testexpr_1 = Rect_old(7,5, color = green) # works as of 061030
testexpr_1x = DebugPrintAttrs(Rect_old(4,7,blue), 'color') # doesn't work yet (instantiation)

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

# === test more complex things

#e testexpr_4 = Overlay( Rect(2), Rect(1, white) )

testexpr_5 = Boxed(testexpr_1) # not tested yet, couldn't work yet (_value, instantiation, Overlay, attrerror: draw)

testexpr_6 = Column( testexpr_1, Rect(1.5, color = blue)) # doesn't work yet (finishing touches in Column, instantiation)

testexpr_7 = ToggleShow( testexpr_2 ) # test use of Rules, If, toggling...

testexpr_8 = TestIterator( testexpr_3 ) # test an iterator

# == set the testexpr to use right now

testexpr = testexpr_3

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
