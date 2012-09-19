# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
TestIterator.py

@author: bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

"""

# not reviewed recently, was part of NewInval
# as of 061106 the setup looks obs, but it might as well be revived and tested before Column is worked on much
# revived 061113, see below

from exprs.Overlay import Overlay

from exprs.transforms import Translate

from exprs.Column import SimpleColumn
##from exprs.Column import SimpleRow

from geometry.VQT import V

from exprs.Exprs import V_expr
from exprs.widget2d import Widget2D, Stub, Widget
from exprs.instance_helpers import InstanceMacro
from exprs.attr_decl_macros import Arg, ArgExpr, Instance
from exprs.ExprsConstants import PIXELS

# just a guess for this symbol...
## from OpenGL.GL import glTranslatefv # I think this used to work but doesn't now, so instead:
from OpenGL.GL import glTranslatef
def glTranslatefv(vec):
    x, y, z = vec
    glTranslatef(x, y, z)
    return

# == obs:

HelperClass = Widget2D
class TestIterator_old_nevertried(HelperClass):
    """
    simple iterator which makes two instances of the same WE arg
    """
    def _make(self, place):
        arg = self._e_args[0] # 061106 args -> _e_args (guess)
        self._define_kid(1, arg) # lexenvfunc can be default (identity), I think
        self._define_kid(2, arg)
        #####@@@@@ what about drawing coords? and layout? layout can be stubbed, but coords should differ.
        # do our kid instances even need to know about their coords? I doubt it.
        return
    def _move(self, kid1, kid2):
        "move between coords for kid1 (an index) and coords for kid2; either can be None to indicate self" ### guess, not yet called
        # algorithm: pretend we're Column, but in some trivial form.
        if kid1 is None: kid1 = 1
        if kid2 is None: kid2 = 1
        assert kid1 in (1,2) and kid2 in (1,2)
        glTranslatefv(V((kid2 - kid1) * 2.0, 0, 0))
        return
    def draw(self):
        self._move(None, 1)
        self._draw_kid(1)
        self._move(1, 2)
        self._draw_kid(2)
        self._move(2, None) #k needed?
        return
    def _draw_kid(self, index):
        # might be in HelperClass
        self.drawkid( self._kids[index] ) ## self._kids[index].draw() # this might lazily create the kid, as self._kid_lvals[index].value or so
        return
    pass

# ==

# [was once] real, but needs:
# - Maker or so
# - review Instance
# - imports
# - not sure if w1.width is always defined

Maker = Stub # won't work, since Arg instantiates (unless several bugs conspire to make it work wrongly, eg with 1 shared instance)

class TestIterator_alsoobsnow_nevertried(InstanceMacro):
    """
    simple iterator which makes two instances of the same arg
    """
    #e for debug, we should make args to pass to this which show their ipaths as text!
    thing = Arg(Maker(Widget)) # Maker? ExprFor? ProducerOf? Producer? Expr?
    w1 = Instance(thing)
        #k is number of evals correct in principle? internal uses of Instance assumed the expr was literal, were they wrong?
        # analyzing the code: this calls _i_inst with (an arg that evaluated to) getattr_Expr(_self, 'thing'),
        # and to instantiate that, it evals it, returning (I think) whatever self.thing is, which should be an instance of the arg.
        # This may make no sense but it's predicted that self.w1 and self.w2 should be instances, and the same one, of the arg.
        # that's wrong [thing's formula instantiates once too much, Instance(thing) once too little since I meant, I guess, I(*thing)]
        # , but it's not what I seem to be seeing, which is w1.width below running on either a non-instance
        # or something with a non-instance inside it. The non-instance is Translate, w1 should be a Boxed, so maybe that's consistent
        # if there's an error in Boxed. So I'm adding sanity checks to zome of: Boxed, Overlay, InstanceMacro, Translate. ###DOIT
##    print "w1 before ExprsMeta = %r" % (w1,) ###
    w2 = Instance(thing)
    # kluge since we don't have Row yet:
    _value = Overlay( w1, Translate(w2, V_expr(w1.width + 4 * PIXELS, 0,0)))
    pass

##print "w1 after ExprsMeta = %r" % (TestIterator.__dict__['w1'],) ###

# ==

class TestIterator(InstanceMacro):
    """
    simple iterator which makes two distinct instances of the same arg
    """
    #e for debug, we should make args to pass to this which show their ipaths as text!
    thing = ArgExpr(Widget)
    w1 = Instance(thing)
    w2 = Instance(thing) # two distinct instances
    _value = SimpleColumn( w1, w2)
    pass

class TestIterator_wrong_to_compare(InstanceMacro):
    """
    variant of that which shows one Instance twice
    """
    thing = Arg(Widget) # the only difference
    w1 = Instance(thing) # these Instances will be idempotent
    w2 = Instance(thing)
    _value = SimpleColumn( w1, w2) # show one instance twice
    pass

# ==

#k not reviewed:
if 0:
    Rect = black = If = red = ToggleShow = 'needs import'
    _enclosing_If = 'needs implem' # see comment below

    goal1 = TestIterator(Rect(1,1,black))

    goal2 = TestIterator(If(_enclosing_If.index[0] == 1, Rect(1,1,black), Rect(1,1,red))) #####@@@@@ _enclosing_If IMPLEM, part of lexenv

    goal3 = TestIterator(ToggleShow(Rect(1,1,red))) # with a def for ToggleShow



# - iterator
#   - Cube, Checkerboard (and fancier: Table)
# see also, in its context elsewhere, a common use for iterators "for the edges in some kind of 3d network or polyhedron..."
