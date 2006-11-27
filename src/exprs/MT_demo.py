"""
$Id$
"""

#e stub, nim

# biggest nim issues [marked with ####]:
# - where to put a caching map from kidnode, args to MT(kidnode, args)
# - arg semantics for Node
# - or for time-varying node.kids (can be ignored for now)
# complicated details:
# - usage/mod tracking of node.open, node.kids
#   [maybe best to redo node, or use a proxy... in future all model objs need this natively]
# #e more??

from basic import *
from basic import _self

from ToggleShow import * # e.g. If, various other imports we should do explicitly #e

If = If_kluge ####e until it works, then remove and retest

Node = Stub


class MT(InstanceMacro):
    # compare to ToggleShow - lots of copied code

    # args
    node = Arg(Node) #### type?

    # state refs
    open ####
    
    # other formulae
    open_icon   = Overlay(Rect(0.4), TextRect('+',1,1))
    closed_icon = Overlay(Rect(0.4), TextRect('-',1,1))
    openclose_spacer = Spacer(0.4)
        #e or Invisible(open_icon); otoh that's no simpler, since open_icon & closed_icon have to be same size anyway
    
    openclose_visible = Highlightable( If( open, open_icon, closed_icon ), on_press = _self.toggle_open )
    
    def toggle_open(self):
        pass####
    
    openclose_slot = If( node.openable, openclose_visible, openclose_spacer )

    icon = Rect(0.4, 0.4, green)##stub; btw, would be easy to make color show hiddenness or type, bfr real icons work
        ###k is this a shared instance (multiply drawn)?? any issue re highlighting? need to "instantiate again"?
            ##e Better, this ref should not instantiate, only eval, once we comprehensively fix instantiation semantics.
            # wait, why did I think "multiply drawn"? it's not. nevermind.
        ##e selection behavior too
    label = TextRect( node.name ) ###e will need revision to Node or proxy for it, so node.name is usage/mod-tracked
        ##e selection behavior too --
        #e probably not in these items but in the surrounding Row (incl invis bg? maybe not, in case model appears behind it!)
        ##e italic for disabled nodes
        ##e support cmenu
    
    _value = SimpleRow(
        openclose_slot,
        SimpleColumn(
            SimpleRow(icon, label),
            If( open,
                      MT_kids(node.kids), ###e implem or find kids... needs usage/mod tracking
                      Spacer(0) ###BUG that None doesn't work here: see comment in ToggleShow.py
                      )
        )
    )
    pass

class MT_kids(InstanceMacro):
    # args
    kids = Arg(list_Expr)####k more like List or list or Anything...
        ##### note: the kid-list itself is time-varying (not just its members); need to think thru instantiation behavior;
        # what we want in the end is to cache (somewhere, not sure if in _self)
        # the mapping from the kid instance (after If eval - that eval to fixed type thing like in Column, still nim)
        # to the MT instance made from that kid. We would cache these with keys being all the args... like for texture_holder.
        # so that's coarser grained caching than if we did it in _self, but finer than if we ignored poss of varying other args
        # (btw do i mean args, or arg-formulae??).

        # note that the caching gets done in here as we scan the kids... *this* instance is fixed for a given node.kids passed to it.
        # BTW maybe our arg should just be the node, probably that's simpler & better,
        # otoh i ought to at least know how it'd work with arg being node.kids which timevaries.

    _value = Column( map_Expr( MT, kids )) ###e change to caching map??
        #e needs Column which takes a time-varying list arg
        #e change to ScrollableColumn someday (also resizable, scrolling kicks in when too tall; how do we pick threshhold? fixed at 10?)
    
