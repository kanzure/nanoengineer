'''
Boxed.py -- example of high-level layout expr

$Id$
'''

from basic import *
from basic import _self

import Rect
reload_once(Rect)
from Rect import RectFrame

import Overlay
reload_once(Overlay)
from Overlay import Overlay

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
