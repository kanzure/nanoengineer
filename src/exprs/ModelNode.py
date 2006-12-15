"""
ModelNode.py

$Id$

Introduction / history / implem plans:

ModelNode is an abstract subclass of Node
for model objects which want to be stored in assy.tree
so as to let a lot of existing NE1 interfaces reach them there:

MT display:
  MT-cmenu
  maybe Edit Properties
  DND
  selection via MT, with its Group/Part-related selection semantics
  copy/cut/delete via MT
3d drawing subject to:
  current Part
  Show/Hide
Undo
mmp file save/load

Maybe also 3D selection and move? We only "get these for free" if we make it
a subclass of Chunk or Atom or Bond or (most likely -- fewest assumptions) Jig,
but that might not be worth the trouble, compared to just modifying the
necessary code in the existing modes, especially selectMode.


ModelNode will have specific subclasses for specific model objects.

It might have a Node and Group variant, if I have any trouble with isinstance(x,Group)
or varying of node.openable. But I hope I won't need that. Maybe any such trouble is easily fixable.

I decided I needn't bother with a separate Node proxy object, since there is not much overlap
with required method names. The draw method is not even needed on my model objects -- they can
in general get looked up to find a viewer for them. So the superclass has Node-compatible draw
which calls exprs draw on the drawable form that gets looked up as their viewer. (For convenience,
esp to start with, they could have their own default_draw method to be used if that lookup fails.)

The MT, when redrawing, should usage-track and subscribe mt_update as the invalidator.

Undo will need decls...

Copy -- can SimpleCopyMixin work? It needs an exception to usage-tracking (basically to discard it)
since it is defined to take a snapshot.

...
"""

from basic import *
from basic import _self, _my, _this

from Utility import SimpleCopyMixin, Node, imagename_to_pixmap, genViewNum
from state_utils import copy_val, S_DATA #k copy_val in basic? where is S_DATA really?

from Rect import Sphere #reload

class ModelNode(Node, SimpleCopyMixin, InstanceOrExpr):
    __metaclass__ = ExprsMeta
    ###IMPLEM - rewrite the rest of this class
    def __init__(self, stuff, name = None):
        assy = env.mainwindow().assy #k wrongheaded??
        Node.__init__(self, assy, name)
        self.stuff = stuff # exprs for what to draw (list of objects)
    _s_attr_stuff = S_DATA
    def draw(self, glpane, dispdef):
        if self.picked: # only draw when picked! (good?)
            draw_stuff(self.stuff, glpane)
    def writemmp(self, mapping):
        """Write this Node to an mmp file, as controlled by mapping,
        which should be an instance of files_mmp.writemmp_mapping.
        """
        line = "# nim: mmp record for %r" % self.__class__.__name__
        mapping.write(line + '\n')
        # no warning; this happens all the time as we make undo checkpoints
        return
    def __CM_upgrade_my_code(self): # experiment
        "replace self with an updated version using the latest code, for self *and* self's data!"
        name = self.__class__.__name__
        print "name is",name # "DebugNode"
        print self.__class__.__module__ 
        #e rest is nim; like copy_val but treats instances differently, maps them through an upgrader
    pass

class Sphere_ExampleModelNode(ModelNode):
    "A sphere."
    pos = StateArg(Position, ORIGIN)
        #e or can all arg/option formulas be treated as state, if we want them to be? (no, decl needed)
        #e or can/should the decl "this is changeable, ie state" as a flag option to the Arg macro?
        #e can it be set to a new *formula*, not just a new constant value? (for constraint purposes)
        #e - if so, does this require a decl to say it's possible, or is it always possible? (note: it affects mmp writing and copy)
    
    if 0:
        # StateArg might be equivalent to this (except for the name to use in the Arg if it matters, e.g. for StateOption):
        _orig_pos = Arg(Position, ORIGIN) #e can we pass an index to override '_orig_pos' if it matters?
        pos = State(Position, _orig_pos) # see similar code in drag_demo (in class Vertex I think)
        
    radius = StateArg(Width, 1)
    color = StateArgOrOption(Color, gray)
    def draw_unpicked(self):
        ###KLUGE: this is copied from Sphere.draw in Rect.py.
        ##e Instead, we should define and cache a real Sphere using self-formulas, and draw that,
        # and delegate to it for lbox as well.
        from drawer import drawsphere # drawsphere(color, pos, radius, detailLevel)
        drawsphere(self.fix_color(self.color), self.center, self.radius, self.detailLevel) # some of this won't work ######IMPLEM
    # so is using Sphere hard?
    _value = Sphere(pos, radius, color) # and something to delegate to it... but only for drawing??
    pass

# end

