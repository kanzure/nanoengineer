'''
Boxed.py -- example of high-level layout expr

$Id$
'''

from basic import *
from basic import _self

from widget2d import Widget2D #####@@@@@ make reloadable

## Overlay = RectFrame = stub # doesn't work, they get called when we import
Stub = Widget2D
Overlay = RectFrame = Center = Stub###@@@

# ==

class Boxed(Widget2D):
    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
    Default options are borderthickness = 4, gap = 4, bordercolor = white.
    [#e These can be changed in the env in the usual way. [nim]]
    """
    # arguments
    _args = ('thing')
    _TYPE_thing = Widget2D # automatically instantiated, since we don't say otherwise [#e but how would we say otherwise?]
    # options (name, maybe default, maybe type)
    _options = dict(borderthickness = 4, gap = 4, bordercolor = white) # values could be formulas using _self; computed vals are public(?)
        # [later note: this is basically a constant FormulaSet described by a dict.]
    # internal formulas (computed vals are not public, at least not by default, though for now this is probably not enforced)
    _ = _self #e can this be done globally, or will it mess up certain IDE debuggers? Guess: it won't, since they'll do it only in __main__. ##k
    #k do i like this _.xxx syntax? Not much...
    extra = 2 * _.gap + 2 * _.borderthickness
    ww = _.thing.width  + _.extra
    hh = _.thing.height + _.extra
    # equivalent value for all uses (like a macro expansion for Boxed(widget, opts))
    _value = Overlay( RectFrame( _.ww, _.hh, thickness = _.borderthickness, color = _.bordercolor),
                      _.thing, ##e is it ok that the alignment of thing will be lost, re the outside? it's not ideal. how to fix??
                      align = Center )
    pass # end of class Boxed

# end
