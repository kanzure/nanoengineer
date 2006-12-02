"""
$Id$
"""

from basic import *
from basic import _self


from ExprsMeta import ClassAttrSpecific_DataDescriptor, FAKE_ATTR, FAKE_CLSNAME

class State_helper(ClassAttrSpecific_DataDescriptor):
    # experimental, 061201; if it works would supercede what's in staterefs.py or whatever (actually Exprs.py for State macro)
    # see also C_rule_for_lval_formula, meant to be used by that old design for the State macro,
    # but this design doesn't anticipate having an "lval formula",
    # but just has an implicit self-relative object and explicit attrname to refer to.
    def _init1(self):
        (self.type, self.default_val) = self.args # maybe also the kind of state
    def get_for_our_cls(self, instance):
        print "get_for_our_cls",(self, self.attr, instance, )#####@@@@@
        holder = self.attrholder(instance)
        return getattr(holder, self.attr)
    def attrholder(self, instance):
        res = instance.transient_state #e or other kind of stateplace
        # check attr (needed only for debugging)
        attr = self.attr
        assert attr != FAKE_ATTR
        # init the default val if needed
        set_default_attrs(res, {attr : self.default_val}) ##k arg syntax
            # It's not easy to optimize that for not calling it every time,
            # since whether it's needed is per-instance (not per-self) and per-attr.
            # So set_default_attrs may already be doing that check about as efficiently as we could,
            # except for our computing arg2 to pass it, which could be optimized away by our
            # first calling a query routine to see if the default has been set yet.
            # (But translating all this into C is probably a better use of time.)
            # (I guess the other easy optim would be to inline this for "set" and not call set_default_attrs then. #e)
        return res
    def set_for_our_cls(self, instance, val):
        print "set_for_our_cls",(self, self.attr, instance, val)#####@@@@@
        holder = self.attrholder(instance)
        return setattr(holder, self.attr, val)
    def __repr__(self):
        return "<%s at %#x for %s>" % (self.__class__.__name__, id(self), self.attr)
    pass # end of class State_helper

def State(type, dflt = None):
    dflt = dflt ##e stub; see existing stateref code for likely better version to use here
    return State_helper(FAKE_CLSNAME, FAKE_ATTR, (type, dflt), {})
        ##e or we could have a mixin that replaced __init__ with one which produced these args from (type, dflt)... not important
        

# one question about how the above can be enough -- does it count as something the formula scanner
# can detect and replace with _self.attr? and how does its self.attr get set, anyway? The other scheme
# set that by making this be an expr with an arg expr _E_ATTR which the scanner would replace,
# and made the result be an expr so the scanner would know to replace it in other exprs with _self.attr.
#
# I think I should generalize what ExprsMeta will do so the attr can be fed in more simply.
#
# Note that any ClassAttrSpecific_DataDescriptor should be constructed like itsclass(clsname, attr, *args, **kws)
# where in this case args are extra stuff like type, dflt. Could the attr be set later like the cls is, tho that's nim for now?
# The initial set can't know the attr -- current code never sets one of these directly, but doesn't even make it until the time
# of the scan -- partly so one shared expr assigned to two attrs could be copied and given a separate attr for each one.
# But we can rule that out for objects we construct just for their assignment; they could have a fake attr and clsname until scanned...
# and we know the scanning will happen soon... and the error of a class assignment "attr1 = attr2" is detectable w/o difficulty.
# (So a simpler scheme looks possible, and it even in hindsight looks better for exprs... unless the thing they need which we don't
#  is changing to a new kind of object, so maybe they might as well get the attr then after all. But this seemed to make their
#  error detection of "attr1 = attr2" a bit more difficult!)



class ImageChunk(InstanceOrExpr, DelegatingMixin):
    """ImageChunk(widget2d) draws widget2d normally, but also captures an image to use 
    for faster redrawing. In some cases, it can significantly speed up drawing of certain
    constant pictures or text, at least for now while our text drawing is inefficient 
    and we don't yet have the display-list equivalent of ImageChunk.
       WARNING: See the caveats below about significant limitations in when and how 
    ImageChunk can be used. See also DisplayListChunk [nim, more widely applicable].
       The default options redraw the image normally at least once per session,
    and never store it on disk (except perhaps in temporary files due to implementation kluges).
    They draw it normally again (and cache a new image) whenever some variable used to draw it
    changes. 
       Options are provided to change the set of variables whose changes invalidate
    the cached image, to record a history of changed images for debugging and testing
    purposes, to keep a saved image on disk for rapid startup, to require developer
    confirmation of changes to that image, and to bring up debugging panes for control
    of these options and browsing of past image versions.
       Caveats: ImageChunk works by grabbing pixels from the color buffer immediately after
    drawing widget2d. This can only work properly if widget2d is drawn in an unrotated orientation,
    and always at the same size in pixels on the screen, but ImageChunk doesn't enforce or check
    this. Therefore it's only suitable for use in 2d screen-aligned widget layouts.
       It can also be confused by obscuring objects drawn into the same pixels in the color or depth
    buffers, if they are drawn first (which is not in general easy to control), so it's only safe
    to use when no such obscuring objects will be drawn, or when they're guaranteed to be drawn
    later than the ImageChunk.
       Likely bug: it doesn't yet do anything to make the lbox aligned at precise pixel boundaries.
    """
    # implem: delegate lbox to arg1, but override draw.
    widget2d = Arg(Widget2D)
    filename = Arg(str) ###e make temp filename default, using python library calls ##e make sure those are easy to use from exprs

    #e state: need_redraw, usage tracking (via an lval, standing for the result of drawing?)
    ###e (we need a standard helper for that)
    # (maybe an object which can supply the wrapping method we need below)
    
    need_redraw = State(bool, True) ###IMPLEM State -- can it just make me a property compatible with the handmade ones? how attrname?
        # attrname issue is why it needs to make something processed by ExprsMeta. Can it just return one directly? I think so.

    def usagetrack_draw(self, draw_method, *args, **kws): ##e this needs to be a method inside some sort of lval object, not of self
        #e begin tracking
        res = draw_method(*args, **kws)
        #e end tracking
        return res

    # this is the delegate for drawing -- we'll delegate the lbox attrs separately, i think -- or cache them too (usage-tracked)??####e
    
    delegate = If( need_redraw,
                   ##e we want this subinstance's draw call to be wrapped in our own code
                   # which does usage tracking around it
                   # and sets need_redraw, False after it. Can we do that, supplying the wrapping method?
                   PixelGrabber(
                       WrapMethod(widget2d, 'draw', _self.usagetrack_draw, ##k is that _self. needed?
                                  post_action = Set(need_redraw, False)), ###k args ###IMPLEM ##e designs ok????
                       filename),
                   Image(...)
                )
    pass # end of class ImageChunk


# end of code

''' #e:
default options: in-ram image, no files, thus not 

but assume the same instance can be multiply drawn
(why not? if anything needs to save one or more locations for redraw, 
 it's an outer thing like a Highlighting)

(exception would be if appearence depended on 

options to:

[note, a lot of these would be useful inval-control or inval-debug options in general]

not do it on every inval
 but only when user confirms
 but only when session starts

do it even when not needed
  if user asks
  if given other formula invals
  on session start, reporting changes
  
save it in a file, or not

use that file in new sessions, or not

intercept a special modkey or debug command on the widget
to put up a prefs/inspector pane for that widget
'''

# end
