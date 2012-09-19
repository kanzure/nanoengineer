# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
TransformedDisplayListsDrawer.py - abstract class for something that draws
using display lists which it caches under a local coordinate system.

Note: as of 090213-17 this contains common code which is used, though
the "transformed" aspects are still not implemented or not used,
and there is still a lot of potential common code in the subclasses
(mainly in the draw method) not yet in this superclass since highly
nontrivial to refactor.

@author: Bruce
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

This code relates to:
- frustum culling(?)
- caching of multiple display lists (e.g. one per display style)
- display lists drawn under a transform;
  modifying them as needed if transform changes
  (needed by vertex arrays in CSDLs, not by pure OpenGL display lists)
- usage/change tracking related to display list contents

TODO: unify similar code in three places: here, ChunkDrawer, ExtraChunkDisplayList. ###
"""

from utilities.debug_prefs import debug_pref, Choice_boolean_True

from foundation.changes import SelfUsageTrackingMixin, SubUsageTrackingMixin
    #bruce 050804, so glpanes can know when they need to redraw a chunk's display list,
    # and chunks can know when they need to inval that because something drawn into it
    # would draw differently due to a change in some graphics pref it used

from graphics.drawing.ColorSortedDisplayList import ColorSortedDisplayList # not yet used?

# ==

class TransformedDisplayListsDrawer(object,
                                    SelfUsageTrackingMixin, SubUsageTrackingMixin
                                    ):
    """
    Superclass for drawing classes which make use of one or more display lists
    (actually CSDLs) to be drawn relative to a transform known to the specific
    subclass, and to be invalidated at appropriate times (with help from the
    subclass).

    (The specific subclass knows where to get the transform,
     and when to invalidate the display lists beyond when usage tracking
     does so.)
    """
    # todo (someday): might be partly obs as of 090217;
    # OTOH some of it doesn't apply yet until ExternalBondSetDrawer
    # handles transforms (to optimize drag):
    #
    # to pull in more of the subclass draw methods,
    # we'd need the following attrs, or revised code:
    # - assy # for drawLevel
    # - glname # if there is a "whole-chunk" one for all our primitives
    # - get_dispdef # method in subclass -- not in the API?? maybe it is if
    #   it's "get cache key and style args" ###
    # - is_chunk_visible # ???
    # - applyMatrix
    # but not get_display_mode_handler, delegate_*, hd, chunk_only --
    # that is handled outside by choosing the right rule (this class)

    _havelist_inval_counter = 0 # see also self.havelist

    # there is no class default for displist; see __get_displist.

    glpane = None

    havelist = 0

    def __init__(self):
        # note: self.displist is allocated on demand by __get_displist
        # [bruce 070523]

        self.extra_displists = {} # precaution, probably not needed
            ### REFACTOR: the code to make these is not in this class
            # or even in the subclass ChunkDrawer, but in a cooperating object
            # Chunk_SpecialDrawingHandler -- probably that ought to be calling
            # back to ChunkDrawer to make this, so only this class and its
            # subclasses would know about self.extra_displists, and so
            # this class could have methods to fill it in which its
            # subclass would be overriding. [bruce 090224 comment]

        return

    # ==

    def invalidate_display_lists_for_style(self, style): #bruce 090217
        """
        @see: documentation of same method in class Chunk

        [this is a conservative implementation; many subclasses
         will want to override this as an optimization]
        """
        self.invalidate_display_lists()
        return

    # ======

    #### note: many following methods were moved here from our subclass Chunk
    # by bruce 090213, but their docstrings and comments are mostly not yet
    # updated for that move.

    def invalidate_display_lists(self): #bruce 050804, revised 090212
        """
        [public, though uses outside this class or class Chunk are suspicious
         re modularity, and traditionally have been coded as changeapp calls
         on Chunk instead]

        This is meant to be called when something whose usage we tracked
        (while making our main display list) next changes.
        """
        # note: the old code when this was in class Chunk and used mainly
        # for end_tracking_usage invalidator was:
        ## self.changeapp(0) # that now tells self.glpane to update, if necessary
        # but I think the correct code should have been more like this, all along:
        self.havelist = 0
        self.track_inval()
        #### REVIEW: all comments about track_inval, havelist, changeapp,
        # and whether the old code did indeed do changeapp and thus gl_update_something.

        # note: as of 090216, in our subclass ExternalBondSetDrawer, this is
        # called at least once per external bond (rung bond) when dna is being
        # rigidly dragged. Once TransformNode works well enough, it won't be
        # called at all for rigid drag. (It will still be called often in some
        # other cases, so it ought to be fast.)

        return

    # == Methods relating to our main OpenGL display list (or CSDL),
    #    self.displist [revised, bruce 090212]

    # (Note: most of these methods could be moved to a new superclass
    #  concerned with maintaining self.displist for any sort of object
    #  that needs one (TransformedDisplayListsDrawer?). If that's done, see also
    #  GLPane_mixin_for_DisplayListChunk for useful features of other
    #  kinds to integrate into that code. But note that a typical object
    #  probably needs a dictionary of displists for different uses,
    #  not just a single one -- even this class has some like that,
    #  in self.extra_displists. That might be more useful to generalize.
    #  [bruce 071103/090123/090212 comment])

    # Note: to invalidate the drawing effects of
    # executing self.displist (along with our extra_displists),
    # when our graphical appearance changes,
    # we set self.havelist = 0 and sometimes call track_inval.
    # The external interface to that is invalidate_display_lists.
    #
    # As for the display list name or CSDL itself, it's allocated on demand
    # (during drawing, when the right GL context is sure to be current),
    # and discarded when we're killed, using the self.displist property
    # that follows.

    _displist = None

    def __get_displist(self):
        """
        get method for self.displist property:

        Initialize self._displist if necessary, and return it.

        @note: This must only be called when the correct GL context is current.
               (If several contexts share display lists, it doesn't matter
                which one is current, but one of them must be.)
               There is no known way to check this, but ignoring it will cause
               bugs. The simplest way to be sure of this is to call this method
               only during drawing.
        """
        if not self._displist:
            self._displist = ColorSortedDisplayList(self.getTransformControl())
        return self._displist

    def getTransformControl(self): #bruce 090223
        """
        @return: the transformControl to use for our ColorSortedDisplayLists
                 (perhaps None)

        [subclasses should override as needed]
        """
        return None

    def __set_displist(self):
        """
        set method for self.displist property; should never be called
        """
        assert 0

    def __del_displist(self):
        """
        del method for self.displist property

        @warning: doesn't deallocate OpenGL display lists;
                  caller must do that first if desired
        """
        self._displist = None ### review: pull more of the deallocator into here?

    displist = property(__get_displist, __set_displist, __del_displist)

    def _has_displist(self):
        """
        @return: whether we presently have a valid display list name
                 (or equivalent object), as self.displist.
        @rtype: boolean

        @note: not the same as self.havelist, which contains data related
               to whether self.displist not only exists, but has up to date
               contents.
        """
        return self._displist is not None

    # new feature [bruce 071103]:
    # deallocate display lists of killed chunks.
    # TODO items re this:
    # - doc the fact that self.displist can be different when chunk kill is undone
    # - worry about ways chunks can miss out on this:
    #   - created, then undo that
    #   - no redraw, e.g. for a thumbview in a dialog that gets deleted...
    #     maybe ok if user ever shows it again, but what if they never do?
    # - probably ok, but need to test:
    #   - close file, or open new file
    #   - when changing to a new partlib part, old ones getting deleted
    #   - create chunk, undo, redo, etc or then kill it
    #   - kill chunk, undo, redo, undo, etc or then kill it

    def _immediately_deallocate_displists(self): #bruce 071103
        """
        [private method]

        Deallocate our OpenGL display lists, and make sure they'll be
        reallocated when next needed.

        @warning: This always deallocates and always does so immediately;
        caller must ensure this is desired and safe at this time
        (e.g. that our GL context is current).
        """
        if self._has_displist():
            #russ 080225: Moved deallocation into ColorSortedDisplayList class
            # for ColorSorter.
            self.displist.deallocate_displists()
            for extra_displist in self.extra_displists.values():
                extra_displist.deallocate_displists()
            self.extra_displists = {}
            del self.displist # note: runs __del_displist due to a property
                # this del is necessary, so __get_displist will allocate another
                # display list when next called (e.g. if a killed chunk is revived by Undo)
            self.havelist = 0
            self._havelist_inval_counter += 1 # precaution, need not analyzed

            ## REVIEWED: this self.glpane = None seems suspicious,
            # but removing it could mess up _gl_context_if_any
            # if that needs to return None, but the docstring of that
            # says that our glpane (once it occurs) is permanent,
            # so I think it should be more correct to leave it assigned here
            # than to remove it (e.g. conceivably removing it could prevent
            # deallocation of DLs when that should happen, though since it's
            # happening now, that seems unlikely, but what if this code is
            # extended to deallocate other DLs on self, one at a time).
            # OTTH what if this is needed to remove a reference cycle?
            # but that can't matter for a permanent glpane
            # and can be fixed for any by removing its ref to the model.
            # Conclusion: best not to remove it here, though pre-090212
            # code did remove it. [bruce 090212]
            ## self.glpane = None
        pass

    def _deallocate_displist_later(self): #bruce 071103
        """
        At the next convenient time when our OpenGL context is current,
        if self._ok_to_deallocate_displist(),
        call self._immediately_deallocate_displists().
        """
        self.call_when_glcontext_is_next_current( self._deallocate_displist_if_ok )
        return

    def _deallocate_displist_if_ok(self): #bruce 071103
        if self._ok_to_deallocate_displist():
            self._immediately_deallocate_displists()
        return

    def _ok_to_deallocate_displist(self): #bruce 071103
        """
        Say whether it's ok to deallocate self's OpenGL display list
        right now (assuming our OpenGL context is current).

        [subclasses must override this]
        """
        raise Exception("subclass must implement")

    def _gl_context_if_any(self): #bruce 071103
        """
        If self has yet been drawn into an OpenGL context,
        return a GLPane_minimal object which corresponds to it;
        otherwise return None. (Note that self can be drawn
        into at most one OpenGL context during its lifetime,
        except for contexts which share display list names.)
        """
        # (I'm not sure whether use of self.glpane is a kluge.
        #  I guess it would not be if we formalized what it already means.)
        return self.glpane

    def call_when_glcontext_is_next_current(self, func): #bruce 071103
        """
        """
        glpane = self._gl_context_if_any()
        if glpane:
            glpane.call_when_glcontext_is_next_current(func)
        return

    def deallocate_displist_if_needed(self):
        """
        If we can and need to deallocate our display lists,
        do so when next safe and convenient (if it's still ok then).
        """
        # bruce 090123 split this out
        if self._enable_deallocate_displist():
            need_to_deallocate = self._ok_to_deallocate_displist()
            if need_to_deallocate:
                ## print "undo or redo calling _deallocate_displist_later on %r" % self
                self._deallocate_displist_later()
        return

    def _f_kill_displists(self): #bruce 090123 split this out of Chunk.kill
        """
        Private helper for model kill methods such as Chunk.kill
        """
        if self._enable_deallocate_displist():
            self._deallocate_displist_later() #bruce 071103
        return

    def _enable_deallocate_displist(self):
        res = debug_pref("GLPane: deallocate OpenGL display lists of killed objects?",
                         Choice_boolean_True, # False is only useful for debugging
                         prefs_key = True )
        return res

    def _f_kluge_set_selectedness_for_drawing(self, picked):
        """
        private helper for performing necessary side effects
        (on our behavior when we subsequently draw)
        of Chunk.pick and Chunk.unpick.

        @note: won't be needed once CSDL stops storing picked state;
               also could probably be removed as an external API call
               by calling it with self._chunk.picked at the start of our own
               drawing methods.
        """
        #bruce 090123 split this out of Chunk.pick and Chunk.unpick;
        # REFACTOR: should not be needed once CSDL stops storing picked state

        if self._has_displist(): #bruce 090223 added condition
            self.displist.selectPick(picked)
            # Note: selectPick shouldn't be needed for self.extra_displists,
            # due to how they're drawn.
            ### REVIEW [bruce 090114]: is selectPick still needed for
            # self.displist? If not, is the CSDL picked state still needed
            # for anything? (A goal is to remove it entirely.) For status on
            # this, see my 090114 comments in ColorSorter.py (summary: it is
            # almost but not quite possible to remove it now).
        return

    # =====

    # support for collect_drawing_func [bruce 090312]

    # note: this is only for local drawing (in self's local coords);
    # if we also need absolute model coord drawing
    # we should add another persistent CSDL for that,
    # and another collector (or an option to this one)
    # to add funcs to it.

    _csdl_for_funcs = None # once allocated, never changed and always drawn

    def begin_collecting_drawing_funcs(self):
        if self._csdl_for_funcs:
            self._csdl_for_funcs.clear_drawing_funcs()

    def collect_drawing_func(self, func, *args, **kws):
        if not self._csdl_for_funcs:
            tc = self.getTransformControl()
            csdl = self._csdl_for_funcs = ColorSortedDisplayList( tc)
                # review: I think we needn't explicitly deallocate this csdl
                # since it contains no DLs. Am I right? [bruce 090312 Q]
        else:
            csdl = self._csdl_for_funcs
        if args or kws:
            func = (lambda _args = args, _kws = kws, _func = func:
                           _func(*_args, **_kws) )
        csdl.add_drawing_func( func )
        return

    def end_collecting_drawing_funcs(self, glpane):
        if self._csdl_for_funcs:
            glpane.draw_csdl( self._csdl_for_funcs )
        return

    # =====

    def draw(self, glpane):

        raise Exception("subclass must implement")

        # someday, we'll either have a real draw method here,
        # or at least some significant helper methods for it.

    pass # end of class

# end
