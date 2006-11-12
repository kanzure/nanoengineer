"""
$Id$

will be renamed or merged

maybe rename to transforms.py, include things like Rotate and Closer

see also Rotated and Closer in testdraw1, for sample opengl code, showing how simple it ought to be
(except that makes no provision for highlighting, which i need to do using move methods or the equiv)
"""

## DelegatingWidget ###IMPLEM, we have only 2D so far, and it doesn't work yet to actually delegate,
# e.g. I don't think using an Overlay inside another one would work right now

_self
Widget
DelegatingMixin
Vec2or3

class Translate(Widget, DelegatingMixin):
    "Translate(thing, vec) translates thing (and its bounding box, 2D or 3D) by vec (2 or 3 components)."
    # 3D aspect is nim
    thing = Arg(Widget)
    delegate = _self.thing
    vec = Arg(Vec2or3)
    # methods needed by all layout primitives: move & draw (see Column)
    def move(self, bla):
        nim # look up the convention for indices... they'll need to match the ones used by thing, I guess None vs 0
    def draw(self):
        self.move(bla)
        self.thing.draw()
        self.move(bla)
    pass

class Center(InstanceMacro):
    "Center(thing) draws as thing, but is centered on the origin"
    # args
    thing = Arg(Widget2D)
    # internal formulas - decide how much to translate thing
    dx = (thing.bright - thing.bleft)/2.0
    dy = (thing.btop - thing.bbottom)/2.0
    # value
    _value = Translate(thing, (dx,dy)) # this translates both thing and its layout box
    pass
