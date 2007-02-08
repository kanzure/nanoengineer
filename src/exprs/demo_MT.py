"""
demo_MT.py

$Id$

works in testexpr_18

warning: *not* being used in test.py's top_left_corner [as of 070105 anyway], that's something else that looks the same --
but on 070206 it is now being used there...

bugs to fix:
- overlay highlight bug (gray hides plus sign -- for best way to fix, see notesfile 070105)
- updating
- see "nim issues" comment below

nfrs:
- use DisplistChunk
- see "needed polish" comment below, etc

[renamed from MT_demo.py, 070106]
"""

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
# - or for time-varying node.kids (can be ignored for now)

# complicated details:
# - usage/mod tracking of node.open, node.kids
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


# == imports

from basic import *
from basic import _self

from ToggleShow import * # e.g. If, various other imports we should do explicitly #e

import Set
reload_once(Set)
from Set import Set ##e move to basic

import Rect
reload_once(Rect)
from Rect import Rect, Spacer

import images
reload_once(images)
from images import IconImage, Image #e and more

import Center
reload_once(Center)
from Center import CenterY

# == stubs

If = If_kluge ####e until it works, then remove and retest

Node = Stub # [later note 061215: this is probably the same as Utility.Node; it's NOT the same as that's new subclass, ModelNode.]

# == trivial prototype of central cache of MT-viewers for objects

# WARNING [added 061215]: this assumes _make_new_MT_viewer_for_object uses no usage-tracked values and thus never needs recomputing.
# That's probably true since the reload counter is in the key. If that becomes false, we'll probably need to replace MemoDict
# with a variant based on LvalDict2.

def _make_new_MT_viewer_for_object(key):
    obj, essential_data, reload_counter = key
    print "viewing node %r, reload_counter = %r" % (obj, reload_counter) ###
    # obj is a Node or equivalent
    mt_instance = MT_try1(obj) # but will this work, with arg1 being already instantiated -- will it make an instance? not yet! ###IMPLEM that
    ###BUG (presumed, 070206, old): this is actually an expr, not an instance.
    # The correct fix is to instantiate it now -- *not* automatically when MT_try1(obj) is formed, as a comment above says should be done --
    # and to index it by both the "whole MT" we're populating (perhaps a "self" this function should be a method in),
    # and the "node_id" of obj (something unique, and never recycled, unlike id(obj)).
    # This may require passing that "whole MT" in dynenv part of Instance.env with Instance part of essential data,
    # or revising how we call this so it can just get "whole MT" as one of the args.
    # The code that needs revising is mainly MT_kids_try1 -- see more comments therein.
    return mt_instance 

_MT_viewer_for_object = MemoDict( _make_new_MT_viewer_for_object)
    # args are (object, essential-data) where data diffs should prevent sharing of an existing viewer
    # (this scheme means we'd find an existing but not now drawn viewer... but we only have one place to draw one at a time,
    #  so that won't come up as a problem for now.)
    # (this is reminiscent of the Qt3MT node -> TreeItem map...
    #  will it have similar problems? I doubt it, except a memory leak at first, solvable someday by a weak-key node,
    #  and a two-level dict, key1 = weak node, key2 = essentialdata.)

def MT_viewer_for_object(obj, essential_data = None):
    from testdraw import vv
    reload_counter = vv.reload_counter # this is so we clear this cache on reload (even if this module is not reloaded)
        # which partly makes up for not live-updating the displayed MT
    key = (obj, essential_data, reload_counter)
    return _MT_viewer_for_object[ key ] # assume essential_data is already hashable (eg not dict but sorted items of one)


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
            return a sequence of the kids (which the caller promises it will not try to modify).
            
        or
        
        mt_kids = formulae for sequence of kids
        
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
    """Interface for a model tree node (something which can show up in a model tree view).
    Includes default compute method implems for use by type-coercion [which is nim]
    [see also ModelTreeNode_trivial_glue, and the node_xxx helper functions far below, for related code].
       WARNING: this class, itself, is not yet used except as a place to put this docstring.
    But the interface it describes is already in use, as a protocol involving the attrs described here.
    """
    _object = Arg(Anything, doc = "an object we want to coerce into supporting this interface") ###k?? #e does it have to sound so nasty?
    # the recompute attrs in the interface, declared using Attr [nim] so they can include types and docstrings
    mt_node_id =   Attr( Id,        call_Expr( id, _object), doc = "a unique nonrecyclable id for the node that object represents")
    mt_name = StateAttr( str,       "",    doc = "the name of a node in the MT; settable by the MT view (since editable in that UI)")
    mt_kids =      Attr( list_Expr, (),    doc = "the list of kids, of all types, in order (client MT view will filter them)")
    mt_openable =  Attr( bool,      False, doc = "whether this node should be shown as openable; if False, mt_kids is not asked for")
                ##e (consider varying mt_openable default if node defines mt_kids, even if the sequence is empty)
    # (##e nothing here yet for type icons)
    pass

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

_DISPLAY_PREFS = dict(open = True) # private to def node_kids

def node_kids(node): # revised 070207
    "return the kid list of the node, regardless of which model tree node interface it's trying to use [slight kluge]"
    try:
        node.mt_kids # look for (value computed by) ModelTreeNodeInterface method
    except AttributeError:
        pass
    else:
        return node.mt_kids

    try:
        node.kids # look for legacy Node method
    except AttributeError:
            pass
    else:
        return node.kids(_DISPLAY_PREFS)

    return () # give up and assume it has no kids

def node_openable(node): # revised 070207
    "return the openable property of the node, regardless of which model tree node interface it's trying to use [slight kluge]"
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
    "return the name property of the node, regardless of which model tree node interface it's trying to use [slight kluge]"
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
        last_resort = safe_repr(node, maxlen = 20)
        print_compact_traceback("node_name fails when trying %%s on node %s: " % last_resort )
        return last_resort
    pass

def mt_node_id(node): # 070207; the name 'node_id' itself conflicts with a function in Utility.py (which we import and use here, btw)
    "return the mt_node_id property of the node, regardless of which model tree node interface it's trying to use [slight kluge]"
    # look for value of ModelTreeNodeInterface attr
    try:
        node.mt_node_id
    except AttributeError:
        pass
    else:
        return node.mt_node_id

    assert not is_expr_Instance(node) # most to the point
    assert not is_Expr(node) # stronger, and also should be true
    
     # look for legacy Node property
    from Utility import node_id
    res = node_id(node) # not sure what to do if this fails -- let it be an error for now -- consider using id(node) if we need to
    return res


##class Column(InstanceMacro): #kluge just for MT_kids_try1
##    eltlist = Arg(list_Expr)
##    _value = SimpleColumn( *eltlist) ### this is wrong, but it seemed to cause an infinite loop -- did it? ###k
        ##    exceptions.KeyboardInterrupt: 
        ##  [debug.py:1320] [debug.py:1305] [test.py:120] [demo_MT.py:100] [demo_MT.py:102] (this line)
        ##  [Exprs.py:271] return getitem_Expr(self, index)  [Exprs.py:360] [Exprs.py:880]
        # guess: *expr is an infloop, since it tries to turn it into a sequence, forming expr[0], expr[1], etc, forever.
        # the Exprs lines above are probably compatible with that.
        # Can this bug be detected? Is there an __xxx__ which gets called first, to grab the whole sequence,
        # which I can make fail with an error? I can find out: *debug_expr where that expr prints all getattr failures. Later.
    
class MT_kids_try1(InstanceMacro):
    # args
    kids = Arg(list_Expr)####k more like List or list or Anything...
        ##### note: the kid-list itself is time-varying (not just its members); need to think thru instantiation behavior;
        # what we want in the end is to cache (somewhere, not sure if in _self)
        # the mapping from the kid instance (after If eval - that eval to fixed type thing like in Column, still nim)
        # to the MT_try1 instance made from that kid. We would cache these with keys being all the args... like for texture_holder.
        # so that's coarser grained caching than if we did it in _self, but finer than if we ignored poss of varying other args
        # (btw do i mean args, or arg-formulae??).

        # note that the caching gets done in here as we scan the kids... *this* instance is fixed for a given node.kids passed to it.
        # BTW maybe our arg should just be the node, probably that's simpler & better,
        # otoh i ought to at least know how it'd work with arg being node.kids which timevaries.

    ## _value = Column( map_Expr( MT_viewer_for_object, kids )) ###e change to caching map?? no, MT_viewer_for_object does the caching.
        #e needs Column which takes a time-varying list arg
        #e change to ScrollableColumn someday
        # (also resizable, scrolling kicks in when too tall; how do we pick threshhold? fixed at 10?)

    def _C__value(self): # we need this since we don't yet have a way of including " * map(func,expr)" in a toplevel expr.
        kids = self.kids
        assert type(kids) == type([])
        elts = map(MT_viewer_for_object, kids) ###BUG (presumed, 070206): elts is a list of exprs; intention was a list of instances.
            # The effect is that, if this is recomputed (which does not happen in testexpr_18, but does in testexpr_30h, 070206 10pm),
            # it evals to itself and returns a different expr to be instantiated (by code in InstanceMacro) using the same index,
            # which prints
            ## bug: expr or lvalflag for instance changed: self = <MT_kids_try1#64648(i)>, index = (-1021, '!_value'),
            ## new data = (<SimpleColumn#65275(a)>, False), old data = (<SimpleColumn#64653(a)>, False)
            # and (evidently, from the failure of the visible MT to update) fails to make a new instance from the new expr.
            # The fix is discussed in comments in MT_viewer_for_object but requires a rewrite of MT_try1 and MT_kids_try1 classes. ####TRYIT
        res = SimpleColumn(*elts) # [note: ok even when not elts, as of bugfix 061205 in SimpleColumn]
        ## return res # bug: AssertionError: compute method asked for on non-Instance <SimpleColumn#10982(a)>
        # I guess that means we have to instantiate it here to get the delegate. kluge this for now:
        return res._e_eval(self.env, ('v',self.ipath)) # 'v' is wrong, self.env is guess
    pass

##_ColumnKluge = Column # don't let our kluge mess up someone who unwisely imports * from here
##del Column


class MT_try1(InstanceMacro):
    # WARNING: compare to ToggleShow - lots of copied code -- also compare to the later _try2 version, which copies from this

    # args
    node = Arg(Node) #### type? the actual arg will be a node instance...

    # state refs
    open = State(bool, False)
    
    # other formulae
    # Note, + means openable (ie closed), - means closable (ie open) -- this is the Windows convention (I guess; not sure about Linux)
    # and until now I had them reversed. This is defined in two files and in more than one place in one of them. [bruce 070123]
    open_icon   = Overlay(Rect(0.4), TextRect('-',1,1))
    closed_icon = Overlay(Rect(0.4), TextRect('+',1,1))
    openclose_spacer = Spacer(0.4)
        #e or Invisible(open_icon); otoh that's no simpler, since open_icon & closed_icon have to be same size anyway

    # the openclose icon, when open or close is visible (i.e. for openable nodes)
    openclose_visible = Highlightable(
        If( open, open_icon, closed_icon ),
        on_press = Set(open, not_Expr(open)) )
    
    openclose_slot = If( call_Expr(node_openable, node), openclose_visible, openclose_spacer )

    icon = Rect(0.4, 0.4, green)##stub; btw, would be easy to make color show hiddenness or type, bfr real icons work
        ###k is this a shared instance (multiply drawn)?? any issue re highlighting? need to "instantiate again"?
            ##e Better, this ref should not instantiate, only eval, once we comprehensively fix instantiation semantics.
            # wait, why did I think "multiply drawn"? it's not. nevermind.
        ##e selection behavior too
    label = TextRect( call_Expr(node_name, node) ) ###e will need revision to Node or proxy for it, so node.name is usage/mod-tracked
        ##e selection behavior too --
        #e probably not in these items but in the surrounding Row (incl invis bg? maybe not, in case model appears behind it!)
        ##e italic for disabled nodes
        ##e support cmenu
    
    _value = SimpleRow(
        openclose_slot,
        SimpleColumn(
            SimpleRow(CenterY(icon), CenterY(label)),
                #070124 added CenterY, hoping to improve text pixel alignment (after drawfont2 improvements in testdraw) -- doesn't work
            If( open,
                      MT_kids_try1( call_Expr(node_kids, node) ), ###e implem or find kids... needs usage/mod tracking
                      Spacer(0) ###BUG that None doesn't work here: see comment in ToggleShow.py
                      )
        )
    )
    pass # end of class MT_try1

# ===

ModelNode = ModelObject ###stub -- should mean "something that satisfies (aka supports) ModelNodeInterface"

class MT_try2(DelegatingInstanceOrExpr): # works on assy.topnode (~~) in testexpr_18i; ###UNTESTED on World in testexpr_30i
    """
    """
    arg = Arg(ModelNode, doc = "the toplevel node of this MT view (fixed; no provision yet for a toplevel *list* of nodes #e)")
    #e could let creator supply a nonstandard way to get mt-items (mt node views) for nodes shown in this MT
    def _C__delegate(self):
        # apply our node viewer to our arg
        return self.MT_item_for_object(self.arg, name_suffix = " (MT_try2)" )
    def MT_item_for_object(self, object, name_suffix = ""):
        "find or make a viewer for object in the form of an MT item for this MT"
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
        expr = _MT_try2_node_helper(object, self, name_suffix = name_suffix)
            ###BUG: if object differs but its mt_node_id is the same, the Instance expr sameness check might complain!!!
            # Can this happen?? (or does it only happen when self is also not the same, so it's not a problem?) #k
            ##e optim: have variant of Instance in which we pass a constant expr-maker, only used if index is new
            # WARNING: if we do that, it would remove the errorcheck of whether this expr is the same as any prior one at same index
        return self.Instance( expr, index) ###k arg order -- def Instance
    pass # end of class MT_try2

# don't use this, most likely: [070207]
##from __Symbols__ import _FORWARD_REF_ ###e refile; ###IMPLEM its special behavior (if it still seems ok & good); #e rename
##    ###e and permit an exception to bug: __call__ of <getattr_Expr#24476: ... when using it
##    ### make them attrs of the mt -- but would call_Expr(globals) work to find them?
## # so you can say in expr E, _FORWARD_REF_.F to refer to expr F lower down in the module


class _MT_try2_kids_helper(DelegatingInstanceOrExpr):
    """[private helper expr class for MT_try2]
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
        ###KLUGE: with bare _MT_try2_node_helper we have a forward ref which doesn't work.
        # Best soln seems to be to let the main MT_try2 have these exprheads in it -- good in other ways too.
        # But I didn't bother to implem that yet, since by reordering the classes, only this forward ref is left,
        # and it won't matter until type coercion by Arg is implemented... or will it? actually it will. No, it won't
        # this will become a getattr_Expr and never get evalled I think. If it does, I'll fix it, or stubbify it in MT_try2. ####k

    # WARNING: compare to MT_kids_try1 -- lots of copied code after this point -- well, not really, it needs rewrite... ###e
    # WARNING: the comments are also copied, and not yet reviewed much for their new context! (so they could be wrong or obs) ###k

    # In current implem of SimpleColumn, we have to produce a column expr with a different arglist, listing the kids themselves
    # (rather than some expr that evals to a list of them). We'd better say that if the expr changes at that index, it's ok.
    # (Or use fresh index each time? No, inefficient & unnatural.)
    # I don't have control of the 'delegate' attr's instantiation code, so I'll use _delegate.
    def _C__delegate(self):
        print "recomputing %r._delegate" % self # make sure this doesn't happen more often than the kidset changes -- not sure it'll work #####
        index = '_C__delegate'
        # compute the SimpleColumn expr we need (see comment above for why we need a mew one each time)
        kids = self.kids # usage tracked (that's important)
        assert not kids or type(list(kids)) == type([])
        for kid in kids:
            # might be a legacy node or a new node (instance)
            assert not is_Expr(kid) or is_expr_Instance(kid)
        elts = map( _MT_try2_node_helper, kids)
        for elt in elts:
            # should be an expr (not instance) of _MT_try2_node_helper ##e remove when works, might not always be valid in future
            assert is_pure_expr(elt)
        expr = SimpleColumn(*elts) # [note: ok even when elts is empty, as of bugfix 061205 in SimpleColumn]
        if 1:
            # do we need to eval expr first? in theory i forget, but in practice this one evals to itself so it doesn't matter. ###k
            ##e do we need to discard usage tracking during the following??
            res = self.Instance( expr, index, permit_expr_to_vary = True) ###IMPLEM permit_expr_to_vary
        return res
    pass # end of class _MT_try2_kids_helper


class _MT_try2_node_helper(DelegatingInstanceOrExpr):
    """[private helper expr class for MT_try2]
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
    
    # WARNING: compare to MT_try1 -- lots of copied code after this point
    # WARNING: the comments are also copied, and not yet reviewed much for their new context! (so they could be wrong or obs) ###k
    
    # state refs
    open = State(bool, False)
    
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
        on_press = Set(open, not_Expr(open)) )
    
    openclose_slot = If( call_Expr(node_openable, node), openclose_visible, openclose_spacer )

    ###STUB for the type_icon:
    icon = Rect(0.4, 0.4, green)##stub; btw, would be easy to make color show hiddenness or type, bfr real icons work
        ###k is this a shared instance (multiply drawn)?? any issue re highlighting? need to "instantiate again"?
            ##e Better, this ref should not instantiate, only eval, once we comprehensively fix instantiation semantics.
            # wait, why did I think "multiply drawn"? it's not. nevermind.
        ##e selection behavior too
    label = TextRect( call_Expr(node_name, node) + name_suffix ) ###e will need revision to Node or proxy for it, so node.name is usage/mod-tracked
        ##e selection behavior too --
        #e probably not in these items but in the surrounding Row (incl invis bg? maybe not, in case model appears behind it!)
        ##e italic for disabled nodes
        ##e support cmenu
    
    delegate = SimpleRow(
        openclose_slot,
        SimpleColumn(
            SimpleRow(CenterY(icon), CenterY(label)),
                #070124 added CenterY, hoping to improve text pixel alignment (after drawfont2 improvements in testdraw) -- doesn't work
            If( open,
                      _MT_try2_kids_helper( call_Expr(node_kids, node) ),
                      Spacer(0) ###BUG that None doesn't work here: see comment in ToggleShow.py
                      )
        )
    )
    pass

# ==

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

