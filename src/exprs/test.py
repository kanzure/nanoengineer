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

from basic import * # including reload_once

import Rect
reload_once(Rect)
from Rect import Rect

import Column
reload_once(Column)
from Column import Column

import Boxed
reload_once(Boxed)
from Boxed import Boxed

import widget_env
reload_once(widget_env)
from widget_env import widget_env

# == stubs

ToggleShow = TestIterator = Column

# == make some "persistent state"

try:
    _state
except:
    _state = {}

# == testexprs

testexpr_1 = Rect(10,16, color = purple) # test basic leaf primitives
print "testexpr_1 is %r" % testexpr_1

testexpr_1b = Boxed(testexpr_1)
print "testexpr_1b is %r" % testexpr_1b

testexpr_2 = Column( testexpr_1, Rect(1.5, color = blue)) # test Column

testexpr_3 = ToggleShow( testexpr_2 ) # test use of Rules, If, toggling...

testexpr_4 = TestIterator( testexpr_3 ) # test an iterator

# == the testexpr to use right now

testexpr = testexpr_1 

# == per-frame drawing code

NullIpath = None ###STUB, refile

def drawtest1_innards(glpane):
    "entry point from ../testdraw.py"
    ## print "got glpane = %r, doing nothing for now" % (glpane,)

    glpane
    staterefs = _state ##e is this really a stateplace? or do we need a few, named by layers for state?
        #e it has: place to store transient state, ref to model state
    some_env = widget_env(glpane, staterefs) #####@@@@@@ IMPLEM more args, etc, and import it

    inst = some_env.make(testexpr, NullIpath) # should memoize this, severe anti-optim not to, but at least it ought to work this way
    inst.draw()
    import env
    print "drew", env.redraw_counter
    return



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
