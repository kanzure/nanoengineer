# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$

unfinished.
"""

from basic import *
from basic import _self

# ==

class ImageChunk(InstanceOrExpr, DelegatingMixin):
    """
    ImageChunk(widget2d) draws widget2d normally, but also captures an image to use
    for faster redrawing. In some cases, it can significantly speed up drawing of certain
    constant pictures or text, at least for now while our text drawing is inefficient
    and we don't yet have the display-list equivalent of ImageChunk.
       WARNING: See the caveats below about significant limitations in when and how
    ImageChunk can be used. See also DisplayListChunk [more widely applicable].
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

    need_redraw = State(bool, True)
        # note: as of 061204, this (for State here and Set below) works in other files
        # but is untested here (since other code here remains nim)

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
                                  post_action = Set(need_redraw, False)), ###k args ###IMPLEM post_action ##e designs ok????
                       filename),
                   Image(...)
                )
    pass # end of class ImageChunk


# end of code

"""
todo:

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
"""

# end
