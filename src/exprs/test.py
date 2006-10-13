'''
current bugs [061013]:

- reload_once does it too often -- should be only when i do the reload effect from testmode/testdraw in cad/src
  (ie base it on that counter, not the redraw counter, but be sure that counter incrs before any imports)
- lots of things are nim

$Id$
'''


# == imports from parent directory

from debug import reload_once_per_event

# == local imports with reload

import basic
reload_once_per_event(basic, always_print = True, never_again = False) # similar code is in basic.py
    # we do this before all other imports, so they don't have to -- because we're an overall entry point!
from basic import * # including reload_once

import Rect
reload_once(Rect)
from Rect import Rect

import Column
reload_once(Column)
from Column import Column

# == stubs

ToggleShow = TestIterator = Column

# == testexprs

from draw_utils import black, blue

print 'Rect is', Rect
testexpr_1 = Rect(1, color = black) # test basic leaf primitives

testexpr_2 = Column( testexpr_1, Rect(1.5, color = blue)) # test Column

testexpr_3 = ToggleShow( testexpr_2 ) # test use of Rules, If, toggling...

testexpr_4 = TestIterator( testexpr_3 ) # test an iterator

# == the testexpr to use right now

testexpr = testexpr_1 

# == per-frame drawing code

def drawtest1_innards(glpane):
    "entry point from ../testdraw.py"
    print "got 5 glpane = %r" % (glpane,)
    return

if 0:####@@@@
    glpane
    some_env = drawing_env(glpane) #####@@@@@@ IMPLEM some args

    inst = some_env.make(testexpr) #e pass in glpane, place to store transient state, ref to model state
    inst.draw()

class drawing_env: ###e cannibalize this; only used just above
    def __init__(self, glpane):
        #e needs what args? glpane; place to store stuff (assy or part, and transient state); initial state defaults or decls...
        pass
    def make(self, expr, tstateplace):
        #e look for rules
        #e Q: is this memoized? does it allocate anything like a state index, or was that already done by customizing this env?
        print "making",expr#####@@@@@
        return expr.make_in(self, tstateplace) #####@@@@@@ IMPLEM, see class xxx below
    def _e_eval_expr(self, expr):
        ###e look for _e_eval method; test for simple py type
        assert 0, "nim"####@@@@
    def _e_eval_symbol(self, expr):
        assert 0, "nim"####@@@@
    pass


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

