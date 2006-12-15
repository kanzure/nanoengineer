"""
$Id$
"""

#e stub, but works in test.py:
## # MT_demo
## ###e need better error message when I accidently pass _self rather than _my]
## testexpr_18 = MT( _my.env.glpane.assy.part.topnode ) # works! except for ugliness, slowness, and need for manual update by reloading.


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
# - mt_instance = MT(obj) # with arg1 being already instantiated, this should make an instance ###IMPLEM that #k first be sure it's right

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

# == stubs

If = If_kluge ####e until it works, then remove and retest

Node = Stub # [later note 061215: this is probably the same as Utility.Node; it's NOT the same as that's new subclass, ModelNode.]

# == trivial prototype of central cache of MT-viewers for objects

def _make_new_MT_viewer_for_object(key):
    obj, essential_data, reload_counter = key
    print "viewing node %r, reload_counter = %r" % (obj, reload_counter) ###
    # obj is a Node or equivalent
    mt_instance = MT(obj) # but will this work, with arg1 being already instantiated -- will it make an instance? not yet! ###IMPLEM that
    return mt_instance

_MT_viewer_for_object = MemoDict(_make_new_MT_viewer_for_object)
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

def node_kids(node):
    return node.kids(_DISPLAY_PREFS)

_DISPLAY_PREFS = dict(open = True) # private to def node_kids


##class Column(InstanceMacro): #kluge just for MT_kids
##    eltlist = Arg(list_Expr)
##    _value = SimpleColumn( *eltlist) ### this is wrong, but it seemed to cause an infinite loop -- did it? ###k
        ##    exceptions.KeyboardInterrupt: 
        ##  [debug.py:1320] [debug.py:1305] [test.py:120] [MT_demo.py:100] [MT_demo.py:102] (this line)
        ##  [Exprs.py:271] return getitem_Expr(self, index)  [Exprs.py:360] [Exprs.py:880]
        # guess: *expr is an infloop, since it tries to turn it into a sequence, forming expr[0], expr[1], etc, forever.
        # the Exprs lines above are probably compatible with that.
        # Can this bug be detected? Is there an __xxx__ which gets called first, to grab the whole sequence,
        # which I can make fail with an error? I can find out: *debug_expr where that expr prints all getattr failures. Later.
    
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

    ## _value = Column( map_Expr( MT_viewer_for_object, kids )) ###e change to caching map?? no, MT_viewer_for_object does the caching.
        #e needs Column which takes a time-varying list arg
        #e change to ScrollableColumn someday
        # (also resizable, scrolling kicks in when too tall; how do we pick threshhold? fixed at 10?)

    def _C__value(self): # we need this since we don't yet have a way of including " * map(func,expr)" in a toplevel expr.
        kids = self.kids
        assert type(kids) == type([])
        elts = map(MT_viewer_for_object, kids)
        res = SimpleColumn(*elts) # [note: ok even when not elts, as of bugfix 061205 in SimpleColumn]
        ## return res # bug: AssertionError: compute method asked for on non-Instance <SimpleColumn#10982(a)>
        # I guess that means we have to instantiate it here to get the delegate. kluge this for now:
        return res._e_eval(self.env, ('v',self.ipath)) # 'v' is wrong, self.env is guess
    pass

##_ColumnKluge = Column # don't let our kluge mess up someone who unwisely imports * from here
##del Column


class MT(InstanceMacro):
    # compare to ToggleShow - lots of copied code

    # args
    node = Arg(Node) #### type? the actual arg will be a node instance...

    # state refs
    open = State(bool, False)
    
    # other formulae
    open_icon   = Overlay(Rect(0.4), TextRect('+',1,1))
    closed_icon = Overlay(Rect(0.4), TextRect('-',1,1))
    openclose_spacer = Spacer(0.4)
        #e or Invisible(open_icon); otoh that's no simpler, since open_icon & closed_icon have to be same size anyway

    # the openclose icon, when open or close is visible (i.e. for openable nodes)
    openclose_visible = Highlightable(
        If( open, open_icon, closed_icon ),
        on_press = Set(open, not_Expr(open)) )
    
    openclose_slot = If( call_Expr(node.openable), openclose_visible, openclose_spacer )

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
                      MT_kids( call_Expr(node_kids, node) ), ###e implem or find kids... needs usage/mod tracking
                      Spacer(0) ###BUG that None doesn't work here: see comment in ToggleShow.py
                      )
        )
    )
    pass # end of class MT

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

