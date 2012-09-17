# Copyright 2009 Nanorex, Inc.  See LICENSE file for details.
"""
DrawingSetCache.py -- cache of DrawingSets with associated drawing intents

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 090313 moved into its own file, from GLPane_drawingset_methods.py,
then factored a lot of access/modification code from its client code
remaining in that file into new methods in this class.

TODO: add usage tracking.
"""

import foundation.env as env

# soon: from foundation.changes import SelfUsageTrackingMixin, SubUsageTrackingMixin

from graphics.drawing.DrawingSet import DrawingSet

# ==

class DrawingSetCache(object,
                      # soon: SelfUsageTrackingMixin, SubUsageTrackingMixin #bruce 090313
                      ): #bruce 090227
    """
    A persistent cache of DrawingSets, one for each "drawing intent"
    specified in the input passed to self.incrementally_set_contents_to().

    (As we're presently used by GLPane_drawingset_methods, that's the
     same set of intents as are passed to glpane.draw_csdl.)

    Some attributes and methods are public.
    """

    # default values of instance variables

    saved_change_indicator = None #bruce 090309
        # public for set and compare (by '==')

    def __init__(self, cachename, temporary):
        self.cachename = cachename # (public, but not used externally [as of 090313])
        self.temporary = temporary # (public, not used *internally* [as of 090313])
        self._dsets = {} # maps drawing intent to DrawingSet;
            # presently private re access/modification,
            # and so are the dsets it contains
        return

    def destroy(self):
        for dset in self._dsets.values():
            dset.destroy()
        self._dsets = {}
        self.saved_change_indicator = None
        return

    def incrementally_set_contents_to(self,
                                      intent_to_csdls,
##                                      dset_change_indicator = None
                                      ):
        """
        Incrementally modify our DrawingSets (creating or destroying
        some of them, modifying others) so that their content matches
        that of the provided dict, intent_to_csdls, which we take ownership
        of and are allowed to arbitrarily modify.

        @param intent_to_csdls: a dict from drawing intents
            (about how a csdl's drawingset should be drawn -- we need to put
             each csdl into a dset which will be drawn in the way it intends)
            to dicts of CSDLs (which maps csdl.csdl_id to csdl).
            We are allowed to arbitrarily modify this dict, so caller
            should not use it after passing it to us.

##        @param dset_change_indicator: if provided (and not false),
##            save this as the value of self.saved_change_indicator.
        """
        #bruce 090313 factored this method out of our client code

##        if dset_change_indicator:
##            self.saved_change_indicator = dset_change_indicator
##            ##### REVIEW: if not, save None?

        dsets = self._dsets
            # review: consider refactoring to turn code around all uses of this
            # into methods in DrawingSetCache

        # 1. handle existing dsets/intents in self
        #    (note: if client uses us non-incrementally, we are initially empty,
        #     so this step efficiently does nothing)
        #
        # - if any prior DrawingSets are completely unused, get rid of them
        #   (note: this defeats future optimizations based on intents which are
        #    "turned on and off", such as per-Part or per-graphicsMode
        #    intents; we'll need to rethink something if we want those here)
        #
        # - for the other prior DrawingSets, figure out csdls to remove and
        #   add; try to optimize for no change; try to do removals first,
        #   to save RAM in case cache updates during add are immediate

        for intent, dset in dsets.items(): # not iteritems!
            if intent not in intent_to_csdls:
                # this intent is not needed at all for this frame
                dset.destroy()
                del dsets[intent]
            else:
                # this intent is used this frame; update dset.CSDLs
                # (using a method which optimizes that into the
                #  minimal number of inlined removes and adds)
                csdls_wanted = intent_to_csdls.pop(intent)
                dset.set_CSDLs( csdls_wanted)
                del csdls_wanted # junk now, since set_CSDLs owns it
            continue

        # 2. handle new intents (if we were initially non-empty, i.e. being used
        #    incrementally) or all intents (when used non-incrementally):
        #    make new DrawingSets for whatever intents remain in intent_to_csdls

        for intent, csdls in intent_to_csdls.items():
            del intent_to_csdls[intent]
                # (this might save temporary ram, depending on python optims)
            dset = DrawingSet(csdls.itervalues())
            dsets[intent] = dset
                # always store them here; remove them later if non-incremental
            del intent, csdls, dset
                # notice bug of reusing these below (it happened, when this was inlined into caller)
            continue
        return

    def draw(self,
             glpane,
             intent_to_options_func,
             debug = False,
             destroy_as_drawn = False
            ):
        """
        Draw all our DrawingSets (in glpane) with appropriate options
        based on their drawing intents, as determined by
        intent_to_options_func.

        @param debug: if true, print debugging info.
        """

        if debug:
            print
            print env.redraw_counter ,
            print "  cache %r%s" % (self.cachename,
                                     self.temporary and " (temporary)" or "") ,
            print "  (for phase %r)" % glpane.drawing_phase
            pass

        for intent, dset in self._dsets.items():
            if debug:
                print "drawing dset, intent %r, %d items" % \
                      (intent, len(dset.CSDLs), )
                pass
            options = intent_to_options_func(intent)
            dset.draw(**options)
            if destroy_as_drawn:
                # don't save them any longer than needed, to save RAM
                # (without this, we'd destroy them all at once near start
                #  of next frame, using code above our call in client,
                #  or later in this frame)
                dset.destroy()
                del self._dsets[intent]
            continue
        return

    pass # end of class DrawingSetCache

# end
