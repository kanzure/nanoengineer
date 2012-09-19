# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
ModelNode.py

@author: bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

Note: as of sometime before 070129 this is an unfinished stub,
and it's not clear whether it will be used.

==

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

much later: see also non-cvs notes (files & paper) of 070105
"""
import time

from foundation.Utility import Node
from foundation.state_constants import S_DATA

from exprs.Rect import Sphere

from exprs.lvals import RecomputingMemoDict ##, call_but_discard_tracked_usage, LvalError_ValueIsUnset

import foundation.env as env

from utilities.constants import gray

from exprs.instance_helpers import InstanceOrExpr
from exprs.attr_decl_macros import StateArg, StateArgOrOption, Arg
from exprs.ExprsConstants import Position, ORIGIN, Width, Color

# ===

# WRONG

##class ModelNode(Node, SimpleCopyMixin, InstanceOrExpr):
##    __metaclass__ = ExprsMeta
    ##  reload failed (not supported in this version?); continuing: exceptions.TypeError: Cannot create a consistent method resolution
    ##  order (MRO) for bases Node, SimpleCopyMixin, InstanceOrExpr
    ##    [debug.py:1320] [debug.py:1305] [test.py:137] [ModelNode.py:69] [ExprsMeta.py:900]
    ##
    ##  ### why can't it?
    ##
    ##  ### that might be yet another reason not to make ModelObjects and their Nodes the same object

class ModelNode(InstanceOrExpr): #e rename since not a Node anymore (unless I actually like this name; doubtful; try ModelObject)
    ###IMPLEM - rewrite the rest of this class, it's obsolete
    def __init__(self, stuff, name = None):
        assy = env.mainwindow().assy #k wrongheaded??
        Node.__init__(self, assy, name)###WRONG now that Node is no longer a superclass
        self.stuff = stuff # exprs for what to draw (list of objects)
    _s_attr_stuff = S_DATA
    def draw(self, glpane, dispdef):
        if self.picked: # only draw when picked! (good?)
            draw_stuff(self.stuff, glpane) ### FIX: Undefined variable 'draw_stuff'
    def writemmp(self, mapping):
        """
        Write this Node to an mmp file, as controlled by mapping,
        which should be an instance of writemmp_mapping.
        """
        line = "# nim: mmp record for %r" % self.__class__.__name__
        mapping.write(line + '\n')
        # no warning; this happens all the time as we make undo checkpoints
        return
    def __CM_upgrade_my_code(self): # experiment
        """
        replace self with an updated version using the latest code, for self *and* self's data!
        """
        name = self.__class__.__name__
        print "name is",name # "DebugNode"
        print self.__class__.__module__
        #e rest is nim; like copy_val but treats instances differently, maps them through an upgrader

    # new code:
    def draw(self, glpane, dispdef): # follows Node.draw API
        #e should create appropriate drawable for the given glpane and dispdef;
        # even if we kluge them as fixed, we need to instantiate our "appearance-expr" (which might default to self? no, draw method is an issue)
        # btw isn't there a parent env and ipath we need to inherit, to draw properly?
        # from this draw-interface, the best ipath might be id(self) or so -- or self.ipath if it has one. or parent-node index-path??
        # not really, given moving of nodes.
        # maybe a per-node serno is best. _e_serno could work unless it changes too often. And it does. hmm.
        # Maybe this has to be specified by whoever makes *us*! that means, self.ipath is best.
        kid = self.find_or_make_kid('_value', glpane) ###IMPLEM find_or_make_kid -- think through the issues
        self.drawkid( kid) ## kid.draw()
    pass

class Sphere_ExampleModelNode(ModelNode):
    """
    A sphere.
    """
    pos = StateArg(Position, ORIGIN) ###IMPLEM StateArg , StateArgOrOption
        #e or can all arg/option formulas be treated as state, if we want them to be? (no, decl needed)
        #e or can/should the decl "this is changeable, ie state" as a flag option to the Arg macro?
        #e can it be set to a new *formula*, not just a new constant value? (for constraint purposes)
        #e - if so, does this require a decl to say it's possible, or is it always possible? (note: it affects mmp writing and copy)

    if 0:
        # StateArg might be equivalent to this (except for the name to use in the Arg if it matters, e.g. for StateOption):
        _orig_pos = Arg(Position, ORIGIN) #e can we pass an index to override '_orig_pos' if it matters?
        pos = State(Position, _orig_pos) # see similar code in demo_drag (in class Vertex I think)

    radius = StateArg(Width, 1)
    color = StateArgOrOption(Color, gray)
##    def draw_unpicked(self):
##        ###KLUGE: this is copied from Sphere.draw in Rect.py.
##        ##e Instead, we should define and cache a real Sphere using self-formulas, and draw that,
##        # and delegate to it for lbox as well.
##        from drawer import drawsphere # drawsphere(color, pos, radius, detailLevel)
##        drawsphere(self.fix_color(self.color), self.center, self.radius, self.detailLevel) # some of this won't work ######IMPLEM
    # so is using Sphere hard? maybe not:
    _value = Sphere(pos, radius, color) # and something to delegate to it... but only for drawing and lbox, delegation by ModelNode??
        # wait, why would we delegate lbox? if we're a Node does that mean we have a position? if lbox is used, does that mean we're
        # drawn by a graphic parent, not as the appearance of some node? For now, assume we won't delegate lbox. OTOH can some
        # graphic thing use a model object as shorthand for "whatever that looks like in the present env"? Without wrapping it??
        # If so, that might lead to our desire to delegate lbox, and everything else in some to-be-formalized "3dgraphics API".
    #e but how would we make that depend on the current display mode? just look at self.env? Or is that part of the model?
        # what about instances of drawables -- they depend on env, maybe they are not fixed for a given model object like we are!!!
        # should we grab env out of glpane when Node.draw is called?

        ###LOGIC PROBLEM 1: Group.draw assumes there's 1-1 correspondence between subnodes in MT and subnodes drawn.
        # POSSIBLE EASY FIX: override Group.draw for our own kind of Grouplike objects. At least, it can modify drawing env,
        # even if it also usually calls the subnode draw methods. BTW we could pass env to draw as a new optional arg.

        ###LOGIC PROBLEM 2: we'd really rather make a parallel drawable (perhaps a tree) and draw that, not call draw on subnodes
        # directly. POSSIBLE EASY FIX: just do it -- don't call draw on subnodes directly, assume they're kids of main drawable.
        # Then Node.draw only gets called at the top of "our kind of Group". That can even work for subnodes not of our type,
        # if we turn them into drawables of a simple kind, by wrapping them with "draw old-style Node using old API".

        ### PROBLEM 3: what if we are drawn multiply in one screen, how does it work?
        # SOLUTION: the Node.draw is not our normal draw api -- that's "find view of this model object and draw it"
        # (specific to env, ipath, other things). The Node.draw is mainly used when legacy modes (not testmode) draw the object.
        # Those can only draw it in one place so it doesn't matter. (Hmm, what if we define a Grouplike node which draws whatever's
        # under it in more than one place? It'd have to work by altering global coords before calling Node.draw. It could pass
        # optional env and ipath args, or whatever, to permit smart nodes to create Instances of their appearance...
        # think this through. ###e)    (It's almost like we just want to add new dynamic args to Node.draw and start using that...
        # in order to coexist in mixed ways with old-style Nodes. They should be dynamic so they pass through old-style Nodes
        # unchanged and are still seen by their new-style Node children. But does this work when there's >1 glpane?
        # BTW, what about drawing with Atoms or Bonds (old drawables, but not Nodes)??
        # I'm not even sure their .draw API is the same. It might be, or could be made to be.)

        ### WORSE PROBLEM 4: what if >1 MT, with different MT-views of one model object? Letting model obj be its own MTNode
        # is a scheme only one of the MTs can use, or that requires the MT-views to be identical (even for value of node.open).
        # If we had multiple MTs we'd want each to have its own set of Nodes made to view our model objects.
        # That would be a fundamentally better scheme anyway. So we'll want it for our own newer MTs (like the ones in the GLPane).
        # So will we want it from the start?
        # Or let it coexist with "model obj can give you a node for another MT, and at same time, be one for "the MT""?

        # ... I guess it now seems like making a separate Node proxy is best, and only using it for this old-MT interface
        # but noting the multiple purposes of that (all the ones listed in the module docstring, unless testmode is running
        # and not using the old rendering code on the assy). For awhile, even in testmode, save file will still use assy.tree, etc.
        # So we'll keep needing to interface with these old APIs through the "old MT view". But we'll like having new views too,
        # incl new-MT (in glpane or not) and new-graphics view (various dispmodes).

        # SO FIRST FIGURE OUT THE GENERAL WAY TO GET VIEW OBJECTS FROM MODEL OBJECTS. Some sort of caching recomputing dict?
        # preferably with adaptive keys, that automatically generalize when subkeys are not used in main expr or subexprs...
        # but for now, ok to ignore that optim (esp if we redecide the key for each subexpr, and some *know* they don't use
        # some parts of the most general key). Compare to what's in demo_MT, texture_holder, CL.
        #
        # ... re all that, see RecomputingMemoDict (written just now, not yet used). ###e
        # The idea is to use it to map objects into images (views) of themselves (with keys containing objs and other data),
        # where instances are images of exprs, view objs are instances of model objs
        # (whether the view objs are Nodes (old MT) or MTViews (new one) or _3DViews(?)), glue code wrapped things of those things.
        # But in some cases we'd like the dict val to permanent -- in that case, use MemoDict and a wayfunc that recomputes internally
        # and delegates to what it recomputes (or forwards to it if it becomes final, as an optim). This might be true for glue code,
        # not sure about viewers. We might like to say which style we prefer in each case (as if part of the key).
        #
        # Note: current direct uses of MemoDict are texture holders and MTView; of LvalDict2 are subinstances -- and any others?
        # StatePlaces -- but they don't make use of the recomputing ability.
    pass

class OldNodeDrawer(InstanceOrExpr):
    node = Arg(Node)
    def draw(self):
        glpane = self.env.glpane
        dispdef = None ###STUB
        node.draw(glpane, dispdef) #####PROBLEM: attrs of old nodes or their subnodes are not usage/change-tracked.
        return
    pass

def testfunc(key):
    return "%s, %s" % (key, time.asctime()) # note: uses no usage-tracked values!!!

rcmd = RecomputingMemoDict(testfunc)

def dictmap(dict1, list1): ##e does this have another name in py_utils, or is there a dict->func converter there??
    #e return tuple??
    return [dict1[key] for key in list1]

if 0:
    print "rcmd maps 1 to %r, 2 to %r, 1 to %r" % tuple(dictmap(rcmd, [1,2,1])) #e change time to counter so you can tell it didn't recompute

# end

