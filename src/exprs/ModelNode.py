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

# See DebugNode (where?) and TestNode when making this.

from Utility import Node

class ModelNode(Node):
    pass

# end except for old code

from Utility import SimpleCopyMixin, Node, imagename_to_pixmap, genViewNum

class TestNode(Node, SimpleCopyMixin): # see TestNode.py... not yet more than a stub... see also DebugNode
    """Abstract class for a kind of Node it's easy to experiment with.
    Just make sure the subclass does the stuff needed by SimpleCopyMixin,
    and that all the attrs can be saved as info records in a simple way by the code herein --
    or maybe we'll save them in a Files Directory shelf instead? Not sure yet.
    """
    def draw(self, glpane, dispdef):
        "Use our subtype to find some rules in a widget expr..."
        # some WE is sitting there in the mode, knowing how to draw things for it...
        # so we ask it...
        # maybe it got passed to this method? ideally as dispdef, but that would break old code...
        # so simplest way is as a dynamic glpane attr, and this is tolerable until we have a chance to clean up all Node draw methods.
        pass
    pass
