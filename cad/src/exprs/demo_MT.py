# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
demo_MT.py - demo of "model tree in GLPane" (primitive, but works)

@author: bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.


### WARNING: the rest of this docstring has not been reviewed since before MT_try2 was implemented
and MT_try1 was moved into an outtakes file, demo_MT_try1_obs.py. Some of the comments in this file
may belong in that outtakes file rather than here. [070210]


works in testexpr_18

warning: *not* being used in test.py's top_left_corner [as of 070105 anyway], that's something else that looks the same --
but on 070206 it is now being used there...

bugs to fix:
- overlay highlight bug (gray hides plus sign -- for best way to fix, see notesfile 070105)
- updating
- see "nim issues" comment below

nfrs:
- use DisplayListChunk
- see "needed polish" comment below, etc

[renamed from MT_demo.py, 070106]
"""

#todo 070208:
# cleanup:
# - move the new one to top left (try2 on new model) (depends on particular testexpr to find model)
# - move deprecated MT_try1 into an outtakes file to avoid confusion (maybe a loadable one so testexpr_18 & _30h still works)
# - start out being open at the top
# +? turn off debug prints
# - reorder args to _try2 helper classes
# - make helper classes attrs of main MT_try2 (rather than globals)
# demo:
# - cross-highlighting
# polish:
# - alignment bug (openclose vs other parts of row in item)
# - type icons
# - openclose needs a triangle too, so mac ppl can understand it
# someday:
# - implem type coercion and use it to let anything work as a node
#   - move Interface to its own file
#   - make ModelTreeNodeInterface real and use it for that
# - autoupdate for legacy nodes
# - permit_expr_to_vary inval during recompute logic bug: (in instance_helpers, but made use of here)
#   - verify it by test (maybe no bug in MT_try2, so the test is a new class designed to hit the bug)
#   - fix it -- see comments where it's defined


#e stub, but works in test.py:
## # demo_MT
## ###e need better error message when I accidently pass _self rather than _my]
## testexpr_18 = MT_try1( _my.env.glpane.assy.part.topnode ) # works! except for ugliness, slowness, and need for manual update by reloading.


# biggest nim issues [some marked with ####]: [solved just barely enough for testexpr_18]
# - where to put a caching map from kidnode, args to MT(kidnode, args)
#   - note, that's a general issue for any "external data editor"
#     where the node is the external data and MT is our preferred-edit-method
#   - does the scheme used for _texture_holder make sense? ###k
#     - should the usual place for maps like this be explicit MemoDicts located in self.env?? ###k
#       by "like this" I mean, maps from objects to fancier things used to interface to them, potentially shared.
#     - how similar is this to the map by a ColumnList from a kid fixed_type_instance to CLE(that instance)?
#       - guess: it can be identical if we specify what ought to be included in the map-key, i.e. when to share.
#         If that includes "my ipath" or "my serno" (my = the instance), it can act like a local dict (except for weakref issues).
# - where & how to register class MT as the "default ModelTree viewer for Node",
        # [note 070206: that class MT is not MT_try1 -- that's a helper expr for a whole-MT exprhead, which is nim]
#   where 'ModelTree' is basically a general style or place of viewing, and Node is a type of data the user might need to view that way?
#   And in viewing a kid (inside this class), do we go through that central system to create the viewer for it, passing it enough env
#   that it's likely to choose the same MT class to view a kid of a node and that node, but not making this unavoidable? [guess: yes. ##k]
#   Note: if so, this has a lot to say about the viewer-caching question mentioned above.
#   Note: one benefit of that central system is to help with handling other requests for an "obj -> open view of it" map,
#    like for cross-highlighting, or to implem "get me either an existing or new ModelTree viewer for this obj, existing preferred".
#    These need a more explicit ref from any obj to its open viewers than just their presumed observer-dependency provides.
#    Note that the key might be more general for some purposes than others, e.g. I'll take an existing viewer even if it was opened
#    using prefs different than I'd use to make a new one. I'm not sure if any one cache needs more than one key-scheme applicable to
#    one value-slot. Let's try to avoid that for now, except for not excluding it in the general architecture of the APIs.
# - arg semantics for Node
# - or for time-varying node.MT_kids() (can be ignored for now)

# complicated details:
# - usage/mod tracking of node.open, node.MT_kids()
#   [maybe best to redo node, or use a proxy... in future all model objs need this natively]
#   - for an initial demo, do it read-only, i.e. don't bother tracking changes by others to external state

# needed polish:
# - better fonts - from screenshots of NE1 or Safari?
#   - appearing selected
#   - italic, for disabled
# - current-part indicator
# - transparency

# opportunities for new features:
# - cross-highlighting -- mouseover an atom, chunk, jig, or MT chunk or jig, highlights the others too, differently
#   - does require realtime changetracking, *but* could be demoed on entirely new data rather than Node,
#    *or* could justify adding new specialcase tracking code into Node, Atom, Bond.

# small nims:
# - map_Expr
# - mt_instance = MT_try1(obj) # with arg1 being already instantiated, this should make an instance ###IMPLEM that #k first be sure it's right

# #e more??


# ===

### WARNING: the comments above this line have not been reviewed since before MT_try2 was implemented
# and MT_try1 was moved into an outtakes file, demo_MT_try1_obs.py. Some of them
# may belong in that outtakes file rather than here, or maybe be entirely obs even there. [070210] ###


# == imports

from utilities.constants import blue, green, ave_colors, white

from utilities.debug import print_compact_traceback
from utilities.debug import safe_repr

from exprs.Highlightable import Highlightable
from exprs.TextRect import TextRect
from exprs.Column import SimpleRow, SimpleColumn
from exprs.Overlay import Overlay
from exprs.Set import Set
from exprs.Rect import Rect, Spacer
from exprs.images import Image
from exprs.Center import CenterY, Center
from exprs.transforms import Translate
from exprs.projection import DrawInCenter #e but what we need is not those, but DrawInAbsCoords or DrawInThingsCoords
    # or really, just get the place (or places) a thing will draw in, in local coords (see projection.py for more discussion)

from exprs.DisplayListChunk import DisplayListChunk
from exprs.Exprs import call_Expr, list_Expr, getattr_Expr, not_Expr, format_Expr
from exprs.Exprs import is_expr_Instance
from exprs.Exprs import is_Expr
from exprs.If_expr import If
from exprs.widget2d import Stub
from exprs.iterator_exprs import MapListToExpr
from exprs.iterator_exprs import KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr
from exprs.attr_decl_macros import Option, State, Arg
from exprs.instance_helpers import DelegatingInstanceOrExpr, ModelObject, InstanceMacro
from exprs.ExprsConstants import StubType
from exprs.py_utils import identity
from exprs.__Symbols__ import Anything, _self

# ==

##e prototype, experimental definition of an Interface
# (all use of which nim, and it's a stub anyway -- but intended to become real). [070207]

class Interface:
    """
    ###doc
       Note: most InstanceOrExpr interfaces (e.g. ModelTreeNodeInterface) consists of attrs
    (recomputable, tracked), not methods, to make it easier and more concise to give formulae for them when defining
    how some IorE subclass should satisfy the interface. If you want to define them with methods in a particular case,
    use the standard compute method prefix _C_, e.g.

        def _C_mt_kids(self):
            return a sequence of the MT_kids (which the caller promises it will not try to modify).

        or

        mt_kids = formulae for sequence of MT_kids

    This means that to tell if a node follows this interface, until we introduce a new formalism for that [#e as we should],
    or a way to ask whether a given attr is available (perhaps for recomputation) without getting its value [#e as we should],
    you may not be able to avoid getting the current value of at least one attr unique to the interface. ### DESIGN FLAW
    It also means that a text search for all implems of the interface attr should search for _C_attr as well as attr
    (if it's a whole-word search).

    Attr names: the interface attrnames in ModelTreeNodeInterface all start with mt_ as a convention, for several reasons:
    - less chance of interference with attrs in other interfaces supported by the same objects,
      or with attrs already present locally in some class;
    - less chance of accidental reuse in a subclass of a class that inherits the interface;
    - more specific name for text search;
    - to make it more obvious that their defs might be part of a definite interface (and give a hint about finding it).
    """
    pass ###e STUB

Attr = Option ###e STUB -- an attr the interface client can ask for (with its type, default value or formula, docstring)
StateAttr = State ###e STUB -- implies that the interface client can set the attr as well as getting it,
    # and type coercion to the interface might create state as needed to support that (if it's clear how to do that correctly)
Id = StubType

class ModelTreeNodeInterface(Interface):
    """
    Interface for a model tree node (something which can show up in a model tree view).
    Includes default compute method implems for use by type-coercion [which is nim]
    [see also ModelTreeNode_trivial_glue, and the node_xxx helper functions far below, for related code].
       WARNING: this class, itself, is not yet used except as a place to put this docstring.
    But the interface it describes is already in use, as a protocol involving the attrs described here.
    """
    _object = Arg(Anything, doc = "an object we want to coerce into supporting this interface") ###k?? #e does it have to sound so nasty?
    # the recompute attrs in the interface, declared using Attr [nim] so they can include types and docstrings
    mt_node_id =   Attr( Id,        call_Expr( id, _object), doc = "a unique nonrecyclable id for the node that object represents")
        ###BUG: id is wrong -- ipath would be closer (but is not really correct, see comments in def mt_node_id)
    mt_name = StateAttr( str,       "",    doc = "the name of a node in the MT; settable by the MT view (since editable in that UI)")
    mt_kids =      Attr( list_Expr, (),    doc = "the list of visible kids, of all types, in order (client MT view will filter them)")
    mt_openable =  Attr( bool,      False, doc = "whether this node should be shown as openable; if False, mt_kids is not asked for")
                ##e (consider varying mt_openable default if node defines mt_kids, even if the sequence is empty)
    # (##e nothing here yet for type icons)
    pass

# some existing interfaces we might like to clean up and formalize:
# - "selobj interface" (from GLPane to a hover-highlighted object; provided by Highlightable)
# - "DragHandler interface (from selectMode to an object that handles its own mouse clicks/drags; see class DragHandler_API)
#
# some new interfaces we'd like:
# - many of the types used in Arg(type, x) are really interfaces, e.g. ModelObject
#   (which may have variants. eg movable or not, geometric or not, 3d or not -- some of these are like orthogonal interfaces
#    since graphical decorating wrappers (eg Overlay, Column) might provide them too)
# - Draggable (something that provides _cmd_drag_from_to)
# - ModelTreeNodeInterface
# - whatever is needed to be dragged by DraggableObject
# - Drawable (whatever is needed to be drawn -- may have variants, may apply to POV-Ray too)

# ==

# the following ModelTreeNode_trivial_glue example is not yet used, but it points out that default formula for interface attrs
# would often like to refer to the object they're trying to type-coerce (in this case, to use its classname to init new state).

class ModelTreeNode_trivial_glue(DelegatingInstanceOrExpr): #070206, 070207
    # args
    delegate = Arg(ModelObject)
    # default formulae for ModelTreeNodeInterface -- including one which supplies new state
    mt_name = State(str, getattr_Expr(getattr_Expr(delegate, '__class__'), '__name__')) ###k
    #e type - grab it from object, or related to role in parent...
    mt_kids = ()
    mt_openable = False
    ###e something for mt_node_id
    pass

# ==

# define some helper functions which can apply either the new ModelTreeNodeInterface or the legacy Utility.Node interface
# to node, or supply defaults permitting any object to show up in the MT.
#
###BUG: they decide which interface to use for each attr independently, but the correct way is to decide for all attrs at once.
# shouldn't matter for now, though it means defining mt_kids is not enough, you need mt_openable too
# (note that no automatic type coercion is yet implemented, so nothing ever yet uses
#  the default formulae in class ModelTreeNodeInterface).

def node_kids(node): # revised 070207 # REVIEW: rename to something like node_MT_kids? [bruce 080108 comment]
    """
    return the kid list of the node, regardless of which model tree node interface it's trying to use [slight kluge]
    """
    try:
        node.mt_kids # look for (value computed by) ModelTreeNodeInterface method
    except AttributeError:
        pass
    else:
        return node.mt_kids

    try:
        node.MT_kids # look for legacy Node method
    except AttributeError:
            pass
    else:
        return node.MT_kids()

    return () # give up and assume it has no MT_kids

def node_openable(node): # revised 070207
    """
    return the openable property of the node, regardless of which
    model tree node interface it's trying to use [slight kluge]
    """
    try:
        node.mt_openable # look for (value computed by) ModelTreeNodeInterface method
    except AttributeError:
        pass
    else:
        return node.mt_openable

    try:
        node.openable # look for legacy Node method
    except AttributeError:
            pass
    else:
        return node.openable() ###k

    return False # give up and assume it's not openable (as the default formula for mt_openable would have us do)
        ##e (consider varying this if node defines mt_kids or kids, even if they are empty)

def node_name(node): # revised 070207
    """
    return the name property of the node, regardless of which
    model tree node interface it's trying to use [slight kluge]
    """
    try:
        node.mt_name # look for (value computed by) ModelTreeNodeInterface method
    except AttributeError:
        pass
    else:
        return node.mt_name

    try:
        node.name # look for legacy Node variable
    except AttributeError:
            pass
    else:
        return node.name

    try:
        return "%s" % node
    except:
        last_resort = safe_repr(node, maxlen = 20) ### FIX: Undefined variable safe_repr, print_compact_traceback
        print_compact_traceback("node_name fails when trying %%s on node %s: " % last_resort )
        return last_resort
    pass

print_mt_node_id = False # set True for debugging (or remove in a few days [070218])

def mt_node_id(node): # 070207; the name 'node_id' itself conflicts with a function in Utility.py (which we import and use here, btw)
    """
    return the mt_node_id property of the node, regardless of which
    model tree node interface it's trying to use [slight kluge]
    """
    # look for value of ModelTreeNodeInterface attr
    try:
        node.mt_node_id
    except AttributeError:
        pass
    else:
        if print_mt_node_id:
            print "this node %r has mt_node_id %r" % (node,node.mt_node_id)
            # old Q: where do our Rects get it?
            # A: they don't -- the bug fixed by bugfix070218 meant this was never called except for World!!
            # [note: on 070302 the comments about bugfix070218, and the code affected by it, was rewritten and removed
            #  (becoming MapListToExpr).
            #  it might still be in an outtakes file not in cvs on bruce's g5 -- or in cvs rev 1.21 or earlier of this file.]
            # btw, we want it to be for the
            # underlying model object... sort of like how we ask for name or type... [bug noticed 070218 late; see below comment]
        return node.mt_node_id

##    assert not is_expr_Instance(node), "what node is this? %r" % (node,) # most to the point
    if is_expr_Instance(node):
        # All Instances ought to have that, or delegate to something which does -- which ought to be their contained ModelObject.
        ####FIX SOMETIME (implem that properly)
        # Until that's implemented properly (hard now -- see _e_model_type_you_make for the hoops you have to jump thru now),
        # use the ipath (non-ideal, since captures wrappers like Draggable etc, but tolerable,
        # esp since this effectively means use the world-index, which will work ok for now [070218 late])
        return node.ipath ###e should intern it as optim

    assert not is_Expr(node), "pure exprs like %r don't belong as nodes in the model tree" % (node,)

    # look for legacy Node property
    from foundation.Utility import node_id
    res = node_id(node) # not sure what to do if this fails -- let it be an error for now -- consider using id(node) if we need to
    if print_mt_node_id:
        print "legacy node %r has effective mt_node_id %r" % (node,res)
    return res

def mt_node_selected(node): #070216 experiment
    """
    #doc
    """
    # look for value of ModelTreeNodeInterface attr (note: lots of objs don't have this; it's also #WRONG(?), should ask the env)
    try:
        node.selected
    except AttributeError:
        pass
    else:
        return node.selected

    # look for legacy Node property
    try:
        node.picked
    except AttributeError:
        pass
    else:
        return node.picked

    return False

# ===

ModelNode = ModelObject ###stub -- should mean "something that satisfies (aka supports) ModelNodeInterface"

class MT_try2(DelegatingInstanceOrExpr): # works on assy.part.topnode in testexpr_18i, and on World in testexpr_30i
    """
    Model Tree view, using the argument as the top node.
    Has its own openclose state independent of other instances of MT_try2, MT_try1, or the nodes themselves.
    Works on IorE subclasses which support ModelTreeNodeInterface, or on legacy nodes (assy.part.topnode),
    but as of 070208 has no way to be notified of changes to legacy nodes (e.g. openclose state or MT_kids or name).
       Has minor issues listed in "todo" comment [070208] at top of source file.
    [This is the official version of a "model tree view" in the exprs package as of 070208; replaces deprecated MT_try1.]
    """
    arg = Arg(ModelNode, doc = "the toplevel node of this MT view (fixed; no provision yet for a toplevel *list* of nodes #e)")
    #e could let creator supply a nonstandard way to get mt-items (mt node views) for nodes shown in this MT
    def _C__delegate(self):
        # apply our node viewer to our arg
        return self.MT_item_for_object(self.arg, initial_open = True)
            # note: this option to self.MT_item_for_object also works here, if desired: name_suffix = " (MT_try2)"
            ## no longer needed after bugfix070218: name_suffix = " (slow when open!)"
    def MT_item_for_object(self, object, name_suffix = "", initial_open = False):
        "find or make a viewer for object in the form of an MT item for use in self"
        ###e optim: avoid redoing some of the following when we already have a viewer for this object --
        # but to find out if we have one, we probably can't avoid getting far enough in the following to get mt_node_id(object)
        # to use as index (since even id(object) being the same as one we know, does not guarantee mt_node_id(object) is the same --
        # unless we keep a reference to object, which I suppose we could do -- hmm... #k #e),
        # which means coercing object enough into ModelNodeInterface to tell us its mt_node_id.
        # Maybe try to make that fast by making most of it lazily done?
        #
        #e coerce object into supporting ModelNodeInterface
        object = identity(object) ###e STUB: just assume it already does support it
        index = ('MT_item_for_object', mt_node_id(object))
            # note: the constant string in the index is to avoid confusion with Arg & Instance indices;
            # it would be supplied automatically if we made this using InstanceDict [nim] #e
            ###e if nodes could have >1 parent, we'd need to include parent node in index -- only sufficient if some
            # nodes have to be closed under some conds not spelled out here (I think: at most one MT item for a given node
            # is open at a time ###k) -- otherwise the entire root-parents-node path might be needed in the index,
            # at least to permit nonshared openness bit of each separately drawn mt item, which is strongly desired
            # (since we might like them to interact, but not by being shared -- rather, by opening one view of a node closing
            #  its other views)
        expr = _MT_try2_node_helper(object, self, name_suffix = name_suffix, initial_open = initial_open)
            ###BUG: if object differs but its mt_node_id is the same, the Instance expr sameness check might complain!!!
            # Can this happen?? (or does it only happen when self is also not the same, so it's not a problem?) #k
            ##e optim: have variant of Instance in which we pass a constant expr-maker, only used if index is new
            # WARNING: if we do that, it would remove the errorcheck of whether this expr is the same as any prior one at same index
        return self.Instance( expr, index) ###k arg order -- def Instance
    pass # end of class MT_try2

class _MT_try2_kids_helper(DelegatingInstanceOrExpr): # rewrote this 070302 (splitting out older one's alg as MapListToExpr) -- works!
    """
    [private helper expr class for MT_try2]
    One MT item kidlist view -- specific to one instance of _MT_try2_node_helper.
    [#e if we generalize MT_try2 to support a time-varying list of toplevel nodes,
     then we might use one of these at the top, instead of using a single node at the top --
     but more likely a variant of this (at least passing it an option), to turn off
     anything it might display in the left which only makes sense when it's elts are under a common parent node.]
    """
    # args
    kids = Arg( list_Expr, doc = "the sequence of 0 or more kid nodes to show (after filtering, reordering, etc, by _self.mt)")
    mt = Arg( MT_try2,     doc = "the whole MT view (for central storage and prefs)") ###e let this be first arg, like self is for methods??
    parent_item = Arg( mt._MT_try2_node_helper, None, doc = "the parent node item for these kid nodes") #k needed??
    # formulae
    delegate = MapListToExpr( mt.MT_item_for_object,
                              kids,
                              KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleColumn) )
    pass

class _MT_try2_node_helper(DelegatingInstanceOrExpr):
    """
    [private helper expr class for MT_try2]
    One MT item view -- specific to one node, one whole MT, and one (possibly time-varying) position with it.
    """
    # args ####e REORDER THEM
    node = Arg(ModelNode, doc = "any node that needs to be displayed in this MT")
        ###e NOTE: type coercion to this is nim; while that's true, we use helper functions like node_name(node) below;
        # once type coercion is implemented
        # (or simulated by hand by wrapping this arg with a helper expr like ModelTreeNode_trivial_glue),
        #  we could instead use node.mt_name, etc.)
    mt = Arg(MT_try2, doc = "the whole MT view, in which we store MT items for nodes, and keep other central state or prefs if needed")
    name_suffix = Option(str, "")
    initial_open = Option(bool, False, doc = "initial value of boolean state 'open'; only used when this item is first created")
        ##e should ask the node itself for the initial value of open (e.g. so new groups, trying to start open, can do so),
        # and also advise it when we open/close it, in case it wants to make that state persistent in some manner

    # WARNING: compare to MT_try1 -- lots of copied code after this point
    # WARNING: the comments are also copied, and not yet reviewed much for their new context! (so they could be wrong or obs) ###k

    # state refs
    open = State(bool, initial_open)

    # other formulae
    ###e optim: some of these could have shared instances over this class, since they don't depend on _self; should autodetect this
    # Note, + means openable (ie closed), - means closable (ie open) -- this is the Windows convention (I guess; not sure about Linux)
    # and until now I had them reversed. This is defined in two files and in more than one place in one of them. [bruce 070123]
    open_icon   = Overlay(Rect(0.4), TextRect('-',1,1))
    closed_icon = Overlay(Rect(0.4), TextRect('+',1,1))
    openclose_spacer = Spacer(0.4)
        #e or Invisible(open_icon); otoh that's no simpler, since open_icon & closed_icon have to be same size anyway

    # the openclose icon, when open or close is visible (i.e. for openable nodes)
    openclose_visible = Highlightable(
        If( open, open_icon, closed_icon ),
        on_press = Set(open, not_Expr(open)),
        sbar_text = getattr_Expr( _self, '_e_serno') #070301 this permits finding out how often MT gets remade/shared
            # (results as of 070301: remade when main instance is, even if going back to a prior testexpr, out of _19i & _30i)
     )

    openclose_slot = If( call_Expr(node_openable, node), openclose_visible, openclose_spacer )


    if 0:
        # cross-highlighting experiment, 070210, but disabled since approach seems wrong (as explained in comment)
        yellow = DZ = 'need to import these'
        indicator_over_obj_center = Center(Rect(0.4, 0.4, yellow))
        position_over_obj_center = node.center + DZ * 3 ###BUG: DZ does not point towards screen if trackballing was done
            ###STUB:
            # - should be drawn in a fixed close-to-screen plane, or cov plane (if obscuring is not an issue),
            #   - so indicator size is constant in pixels, even in perspective view (I guess),
            #   - also so it's not obscured (especially by node itself) -- or, draw it in a way visible behind obscuring things (might be a better feature)
            # - what we draw here should depend on what node is
            # - we also want to draw a line from type icon to node indicator (requires transforming coords differently)
            # - needs to work if node.center is not defined (use getattr_Expr - but what dflt? or use some Ifs about it)
        pointer_to_obj = DrawInCenter( Translate( indicator_over_obj_center, position_over_obj_center))
            #bug: Translate gets neutralized by DrawInCorner [fixed now]
            ###BUG: fundamentally wrong -- wrong coord system. We wanted DrawInAbsCoords or really DrawInThingsCoords,
            # but this is not well-defined (if thing drawn multiply) or easy (see comments about the idea in projection.py).
    else:
        # What we want instead is to set a variable which affects how the obj is drawn.
        # If this was something all objs compared themselves to, then all objs would track its use (when they compared)
        # and therefore want to redraw when we changed it! Instead we need only the involved objs (old & new value) to redraw,
        # so we need a dict from obj to this flag (drawing prefs set by this MT). Maybe the app would pass this dict to MT_try2
        # as an argument. It would be a dict of individually trackable state elements. (Key could be node_id, I guess.)
        # ### TRY IT SOMETIME -- for now, cross-highlighting experiment is disabled.
        pointer_to_obj = None

    # selection indications can use this
    node_is_selected = call_Expr( mt_node_selected, node)
    kluge_icon_color = If( node_is_selected, blue, green)
    sbar_format_for_name = If( node_is_selected, "%s (selected)", "%s")

    ###STUB for the type_icon ##e the Highlightable would be useful on the label too
    icon = Highlightable(
        Rect(0.4, 0.4, kluge_icon_color), ##stub; btw, would be easy to make color show hiddenness or type, bfr real icons work
        Overlay( Rect(0.4, 0.4, ave_colors(0.1, white, kluge_icon_color)),
                 #070216 mix white into the color like DraggableObject does
                 pointer_to_obj ),
        sbar_text = format_Expr( sbar_format_for_name, call_Expr(node_name, node) )
     )

    ##e selection behavior too

    label = DisplayListChunk(
        # added DisplayListChunk 070213 late -- does it speed it up? not much; big new-item slowness bug remains. retain, since doesn't hurt.
        TextRect( call_Expr(node_name, node) + name_suffix )
     )
        ###e will need revision to Node or proxy for it, so node.name is usage/mod-tracked
        ##e selection behavior too --
        #e probably not in these items but in the surrounding Row (incl invis bg? maybe not, in case model appears behind it!)
        ##e italic for disabled nodes
        ##e support cmenu

    delegate = SimpleRow(
        CenterY(openclose_slot),
        SimpleColumn(
            SimpleRow(CenterY(icon), CenterY(label)),
                #070124 added CenterY, hoping to improve text pixel alignment (after drawfont2 improvements) -- doesn't work
            If( open,
                _MT_try2_kids_helper( call_Expr(node_kids, node) , _self.mt ), # 070218 added _self.mt -- always intended, first used now
                None
                    # Note: this None used to be Spacer(0), due to a bug mentioned in a comment in ToggleShow.py
                    # (but unfortunately not explained there -- it just says "I wanted None here, but it exposes a logic bug,
                    # not trivial to fix, discuss in If or Column" -- my recollected bug-theory is described just below).
                    # On 070302 I confirmed that None seems to work (even in testexpr_18i with a group of 2 chunks, plus two more below).
                    # I don't fully know why it works, since I thought the bug was that SimpleColumn's None specialcase
                    # didn't run, since the element was not None but the If, and then delegating lbox attrs to None didn't work.
                    # (Fixable by using the newer If that evals, but for some reason that's not yet standard, I guess just because
                    # I didn't have time to test it enough or think it through fully re ipath or instance caching or something.)
                    # But as long as it works, use it -- ask Qs later. A recent perhaps-related change: None is allowed in drawkid.
                    # (A memory scrap -- does instantiating None conceivably produce a spacer?? ###k)
             )
         )
     )
    pass # end of class _MT_try2_node_helper

# ==

# note: this predates MT_try2, but it's not moved into demo_MT_try1_obs.py since it might still be used someday. [070210]

Node = Stub # [later note 061215: this is probably the same as Utility.Node;
  # it's NOT the same as that's new subclass, ModelNode in ModelNode.py.]

class test_drag_pixmap(InstanceMacro):
    mt = Arg(Anything) # pass _my.env.glpane.assy.w.mt
    node = Arg(Node) # pass the topnode
    def _C__value(self):
        mt = self.mt # fails, recursion in self.delegate computation -- why? related to parent AttributeError: win? must be.
            ###e NEED BETTER ERROR MESSAGE from exception when computing self.mt by formula from caller.
            # It did have the attrerror, but buried under (and then followed by) too much other stuff (not stopping) to notice.
        node = self.node
        pixmap = mt.get_pixmap_for_dragging_nodes('move', [node]) # (drag_type, nodes); method defined in TreeWidget.py
            #e includes "moving n items", need to make it leave that out if I pass None for drag_type
        print pixmap # <constants.qt.QPixmap object at 0x10fbc2a0>
        #e make Image (texture) from pixmap -- how?
        # - pass the pixmap into ImageUtils somehow (won't be hard, could go in in place of the filename)
        # - worry about how it works in our texture-caching key (won't be hard)
        # - teach ImageUtils how to get a PIL image or equivalent data from it -- requires learning about QPixmap, image formats
        # MAYBE NOT WORTH IT FOR NOW, since I can get the icons anyway, and for text I'd rather have a Qt-independent path anyway,
        # if I can find one -- tho I predict I'll eventually want this one too, so we can make GL text look the same as Qt text.
        # Note: PixelGrabber shows how to go in the reverse direction, from GL to Qt image.
        # Guess: QPixmap or QImage docs will tell me a solution to this. So when I want nice text it might be the quickest way.
        # (Also worth trying PIL's builtin text-image makers, but I'm not sure if we have them in NE1 even tho we have PIL.)
        # The other way is to grab actual screenshots (of whatever) and make my own font-like images. Not ideal, re user-reconfig
        # of font or its size!
        #
        # Here are hints towards using Qt: turn it into QImage, which boasts
        # "The QImage class provides a hardware-independent pixmap representation with direct access to the pixel data."
        # and then extract the data -- not yet known how much of this PyQt can do.
        #
        # - QImage QPixmap::convertToImage () const
        #
        ##uchar * QImage::scanLine ( int i ) const
        ##
        ##Returns a pointer to the pixel data at the scanline with index i. The first
        ##scanline is at index 0.
        ##
        ##The scanline data is aligned on a 32-bit boundary.
        ##
        ##Warning: If you are accessing 32-bpp image data, cast the returned pointer
        ##to QRgb* (QRgb has a 32-bit size) and use it to read/write the pixel value.
        ##You cannot use the uchar* pointer directly, because the pixel format depends
        ##on the byte order on the underlying platform. Hint: use qRed(), qGreen() and
        ##qBlue(), etc. (qcolor.h) to access the pixels.

        image = pixmap.convertToImage()
        print image # <constants.qt.QImage object at 0x10fe1900>

        print "scanlines 0 and 1 are", image.scanLine(0), image.scanLine(1)
            # <sip.voidptr object at 0x5f130> <sip.voidptr object at 0x5f130> -- hmm, same address
        print "image.bits() is",image.bits() # image.bits() is <sip.voidptr object at 0x5f130> -- also same address

        print "\n*** still same address when all collected at once?:" # no. good.
        objs = [image.scanLine(0), image.scanLine(1), image.bits()]
        for obj in objs:
            print obj
        print
        # but what can i do with a <sip.voidptr object>? Can Python buffers help?? Can PIL use it somehow??
        # Or do I have to write a C routine? Or can I pass it directly to OpenGL as texture data, if I get the format right?
        # Hmm, maybe look for Qt/OpenGL example code doing this, even if in C. ##e

        _value = Image( "notfound")
        env = self.env
        ipath = self.ipath
        return _value._e_eval( env, ('v', ipath)) # 'v' is wrong, self.env is guess
            ## AssertionError: recursion in self.delegate computation in <test_drag_pixmap#15786(i)> -- in pixmap set above
    pass

# end

