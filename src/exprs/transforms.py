"""
transforms.py - provide Translate [and more later]

$Id$

Translate was developed in Center.py, split out of that 061115

plan: include things like Rotate and Closer

see also Rotated and Closer in testdraw1, for sample opengl code, showing how simple it ought to be
(except that makes no provision for highlighting, which i need to do using move methods or the equiv)
"""

##k [obs cmt? strongly guess yes 061115, but need to test:]
# it doesn't work yet to actually delegate, eg for lbox attrs,
# so I don't think using an Overlay inside another one would work right now

from basic import *
from basic import _self

from OpenGL.GL import glTranslatef ###e later do this thru glpane object

###e [semiobs cmt:]
# these vec routines are not best.. what's best is to turn into (not away from) numeric arrays, for their convenience.
# guess: convention should be to always pass 3dim numeric arrays, and keep 3dim bboxes.
# let 2d routines not use z but still have it, that way same code can do 2d & 3d stuff, no constant checks for len 2 vecs, etc.
# but the above is nim in this code.

def tuple3_from_vec(vec): #stub, but might be enough for awhile
    "turn all kinds of 2D or 3D vecs (tuples or Numeric arrays of ints or floats) into 3-tuples (of ints or floats)"
    try:
        x,y,z = vec
    except:
        x,y = vec
        z = 0
    return x,y,z

def tuple2_from_vec(vec):
    x,y,z = tuple3_from_vec(vec)
    return x,y

def weighted_ave(t, t0, t1): #e refile to py_utils? # not presently used, but useful and tested (was used in debug code)
    """return the weighted average of t0 and t1 using t (i.e. t0 * (1-t) + t1 * t),
    which is t0 for t == 0, and t1 for t == 1. No requirement that 0 <= t <= 1,
    though that's typically true.
    """
    return t0 * (1-t) + t1 * t

class Translate(Widget, DelegatingMixin):
    "Translate(thing, vec) translates thing (and its bounding box, 2D or 3D) by vec (2 or 3 components). [3D aspect is nim]"
    # 3D aspect might be nim
    thing = Arg(Widget)
    delegate = _self.thing
    vec = Arg(Vector)
    # translation of layout box
    # [#e This should be handled differently later, since the current approach requires knowing
    #  all attrs/methods that take or return geometric info in the object's local coords!
    #     A better way might be to have object-local methods to turn number-coords into Points etc, and vice versa,
    #  with Points knowing their coords and their coord-frame identifier. Subtleties include the semantics
    #  of time-variable coord-frames -- it matters which frame a Point is understood to be relative to,
    #  to know whether it moves or not when it doesn't change in value.
    #     If that's too hard to work out, another better way might be to query the object, or our
    #  understanding of its API-type, for type-signatures of methods/attrs needing geometric transformations,
    #  and setting those up here, perhaps in _init_instance (tho this scheme would need optims to move it
    #  at least as far (in being shared between instances) as into _init_expr).
    # ]
    ## for useful debug/example code, _C_debugfactor and call_Expr(_self._C_debugfactor), see rev 1.6:
    ## "_C_debugfactor - temporary eg of debug code, counter-dependent drawing, mixing _C_ and formulae"

    dx = vec[0]
    dy = vec[1]
        #k Interesting Q: would it work here to say dx, dy = vec? I doubt it, since len(vec) (an expr) is not defined.
        # (Besides (an academic point), its length when defined is 3, so we'd need to include dz even if we don't use it.)
    bleft = thing.bleft - dx # might become negative; probably ok, but origin outside lbox will affect Column layout, etc ##e ok?
    bright = thing.bright + dx
    bbottom = thing.bbottom - dy # might become negative; see comment above
    btop = thing.btop + dy
    # methods needed by all layout primitives: move & draw (see Column) & maybe kid (needed for highlighting, maybe not yet called)
    def move(self, i, j): # note: this separate move/draw API is obsolete, but still used, tho only locally (see paper notes circa 091113)
        "move from i to j, where both indices are encoded as None = self and 0 = self.thing"
        #e we might decide to only bother defining the i is None cases, in the API for this, only required for highlighting;
        # OTOH if we use it internally we might need both cases here
        assert self._e_is_instance
        x,y,z = tuple3_from_vec(self.vec)
        if i is None and j == 0:
            glTranslatef(x,y,z) ##e we should inline this method (leaving only this statement) into draw, before thing.draw ...
        elif i == 0 and j is None:
            glTranslatef(-x, -y, -z) ##e ... and leaving only this statement, after thing.draw
        return
    def kid(self, i): # never called, but (for nim hover highlighting) i forget whether it's obs (see paper notes circa 091113)
        assert i == 0
        return self.thing
    ###e note: as said in notesfile, the indices for these drawn kids *could differ* from these arg indices if I wanted...
    # or I could instead define a dict...
    def draw(self):
##        print "start drawing in %r, ipath %r" % (self, self.ipath,)
        assert self._e_is_instance
        self.move(None, 0)
        self.thing.draw()
            # draw kid number 0 -- ##k but how did we at some point tell that kid that it's number 0, so it knows its ipath??
            ##k is it worth adding index or ipath as a draw-arg? (I doubt it, seems inefficient for repeated drawing)
        self.move(0, None)
##        print "done drawing in %r, ipath %r" % (self, self.ipath,)
        return
    pass # end of class Translate

# end
