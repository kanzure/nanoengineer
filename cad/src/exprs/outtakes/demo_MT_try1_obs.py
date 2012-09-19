# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$

WARNING: perhaps never tested since removed from demo_MT.py on 070210 --
essentially just an outtakes file, saved in case comments are still relevant;
mayb still be imported from test.py
"""

# == imports

from basic import *
from basic import _self

from ToggleShow import * # e.g. If, various other imports we should do explicitly #e  ### FIX THIS, do them explicitly

from Set import Set ##e move to basic

from Rect import Rect, Spacer

from images import IconImage, Image #e and more

from Center import CenterY


from demo_MT import node_kids, node_openable, mt_node_id, node_name

# == stubs

If = If_kluge ####e until it works, then remove and retest

Node = Stub # [later note 061215: this is probably the same as Utility.Node; it's NOT the same as that's new subclass, ModelNode.]


# == trivial prototype of central cache of MT-viewers for objects

# WARNING [added 061215]: this assumes _make_new_MT_viewer_for_object uses no usage-tracked values and thus never needs recomputing.
# That's probably true since the reload counter is in the key. If that becomes false, we'll probably need to replace MemoDict
# with a variant based on LvalDict2.

def _make_new_MT_viewer_for_object(key):
    obj, essential_data, reload_counter = key
    print "viewing node %r, reload_counter = %r" % (obj, reload_counter) # leave this in, since it's only used by deprecated MT_try1
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
    from exprs.reload import exprs_globals # untested since vv was renamed and moved
    reload_counter = exprs_globals.reload_counter # ditto
        # this is so we clear this cache on reload (even if this module is not reloaded)
        # which partly makes up for not live-updating the displayed MT
    key = (obj, essential_data, reload_counter)
    return _MT_viewer_for_object[ key ] # assume essential_data is already hashable (eg not dict but sorted items of one)


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


class MT_try1(InstanceMacro): # deprecated MT_try1 as of 070208, since MT_try2 works better
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
                #070124 added CenterY, hoping to improve text pixel alignment (after drawfont2 improvements) -- doesn't work
            If( open,
                      MT_kids_try1( call_Expr(node_kids, node) ), ###e implem or find kids... needs usage/mod tracking
                      Spacer(0) ###BUG that None doesn't work here: see comment in ToggleShow.py
                      )
        )
    )
    pass # end of class MT_try1

# end
