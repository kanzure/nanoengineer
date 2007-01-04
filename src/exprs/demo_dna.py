"""
demo_dna.py
$Id$
"""


from basic import *
from basic import _self

import Rect
reload_once(Rect)
from Rect import Rect, RectFrame

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import transforms
reload_once(transforms)
from transforms import Translate

import Center
reload_once(Center)
from Center import Center

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable


# let's start with a resizable rectangular raster of dna turns.
# it's really a resizable guide shape on which we can draw regions of dna to fill in,
# and they in turn act as guide shapes for placing actual strands, cyls, etc, or paths or seams.

# but to start with, let's just be able to draw it... and have it draw some little objs on which to click to fill it or make crossovers.

# so something much simpler is a resizable table of little rects.

# it has the rects, and a resize handle.

# do we bother at this stage to split it into its data and its appearance? Not yet, since that's hard....

Grid = Resizer = Stub

class xxx(DelegatingInstanceOrExpr):
    nrows = State(int, 5) # each row is actually two helices
    ncols = State(int, 10)
    delegate = Overlay(
        Grid( Rect(1), nrows, ncols ),
        Resizer() # resizer of what? and, displayed where? aligned with a grid corner? how?
            # is a Box resizer (one per corner) any simpler?
    )
    pass

# ok, I've still never made a resizable box, resizable at each corner.

class newerBoxed(DelegatingInstanceOrExpr):
    # args
    thing = Arg(Widget2D)
    # options
    borderthickness = Option(Width, 4 * PIXELS)
    gap = Option(Width, 4 * PIXELS)
    bordercolor = Option(Color, white)
    # internal formulas
    extra1 = gap + borderthickness
    ww = thing.width  + 2 * extra1 #k I'm not sure that all Widget2Ds have width -- if not, make it so ##e [061114]
    hh = thing.height + 2 * extra1
    # value
    delegate = Overlay( Translate( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor),
                                 - V_expr( thing.bleft + extra1, thing.bbottom + extra1) ), #e can't we clarify this somehow?
                      thing)
    pass

##class ResizableBox(DelegatingWidgetExpr): # compare to Boxed
##    Overlay(RectFrame(),
##            


class resizablyBoxed(DelegatingInstanceOrExpr):
    # args
    thing = Arg(Widget2D) # display thing (arg1) in the box, but don't use it for the size except to initialize it
    # options
    borderthickness = Option(Width, 4 * PIXELS)
    gap = Option(Width, 4 * PIXELS)
    bordercolor = Option(Color, white)
    # state - initialize from formulas based on args and instance sizes, is that ok??
    thing_width = State(float, thing.width) #k I'm not sure that all Widget2Ds have width -- if not, make it so ##e [061114]
    thing_height = State(float, thing.height)
    # internal formulas, revised to use state
    extra1 = gap + borderthickness
    ww = thing_width  + 2 * extra1
    hh = thing_height + 2 * extra1
    # not yet any way to change the state... to test, add on_press which adds 1 to it or so #e
    # value
    delegate = Overlay( Translate( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor),
                                 - V_expr( thing.bleft + extra1, thing.bbottom + extra1) ), #e can't we clarify this somehow?
                        Highlightable(thing, on_press = _self.on_press_thing))
    # actions
    def on_press_thing(self):
        self.thing_width += 1
        self.thing_height += 2
    pass
