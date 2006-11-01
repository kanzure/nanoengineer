'''
Boxed.py -- example of high-level layout expr

$Id$
'''

from basic import *

from widget2d import Widget2D #####@@@@@ make reloadable

## Overlay = RectFrame = stub # doesn't work, they get called when we import
Stub = Widget2D
Overlay = RectFrame = Center = Stub###@@@
Color = Stub

from Exprs import Symbol

def Arg(type1 = None, dflt = None):
    return Symbol('_some_Arg')#stub

Option = Arg #stub
#e Instance too, for internal use? Arg & Option instantiate by default (lazily).

# ==

class Boxed(Widget2D):
    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
    Default options are borderthickness = 4, gap = 4, bordercolor = white.
    [#e These can be changed in the env in the usual way. [nim]]
    """
    # args
    thing = Arg(Widget2D)
    # options
    borderthickness = Option(int, 4)
    gap = Option(int, 4)
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

##e see cvs rev 1.7 (or Boxed-outtakes.py, not in cvs), and a notesfile (not in cvs)
# for how-to-devel comments about the above Arg/Option notation (implem, extensions).

# more possibilities:
if 0:
    somth = [ff(i) for i in someattr._range] # workable if symexpr._range returns a list of one specially-typed symbol
    indexedattr = Indexed( lambda i: f(i)) # with more args/options about the range; should be workable; can CL use it for kids??

# end
