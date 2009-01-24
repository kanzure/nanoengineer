# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Chunk_drawing_methods.py -- Chunk mixin for methods related to drawing 
(using OpenGL or compatible primitives -- someday this may cover POV-Ray
as well, but it doesn't as of early 2009)

@author: Josh, Bruce, others
@version; $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Written over several years as part of chunk.py.

Bruce 090123 split these methods out of class Chunk in chunk.py.
(For prior svn history, see chunk.py. I decided against using
svn copy, even though this code has lots of history in there,
since it's shortly going to get refactored much more within
this file, and things will be clearer if this split starts
a clear separation of old and new in the history,
especially since 3/4 of the old chunk.py is not this code.)

TODO: refactor this in two ways:

 * make this code into a separate drawing-controller object 
   which cooperates with class Chunk
   (but more than one instance per Chunk might be possible, 
    if it's drawn in more than one glpane or more than one way; 
    re this, review the self.glpane attr)

 * split it into sub/superclasses for Chunk and the superclasses
   to be split out of Chunk (e.g. AtomCloud, PointCloud, TransformNode
   (all names tentative); this involves picking apart def draw in
   particular, since the display list and transform code is general
   but there is speciic code for atoms & bonds as well; some of this
   will ultimately turn into GraphicsRules (name also tentative)

"""

import math # only used for pi, everything else is from Numeric [as of before 071113]

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPopName
from OpenGL.GL import glPushName


from utilities.constants import diBALL
from utilities.constants import diDNACYLINDER
from utilities.constants import diLINES
from utilities.constants import diTUBES
from utilities.constants import diTrueCPK
from utilities.constants import MAX_ATOM_SPHERE_RADIUS 
from utilities.constants import BBOX_MIN_RADIUS
##from utilities.constants import PickedColor

from utilities.debug import print_compact_traceback

from utilities.debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False

from utilities.GlobalPreferences import use_frustum_culling

from utilities.Log import graymsg

from utilities.prefs_constants import bondpointHotspotColor_prefs_key
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key


import foundation.env as env


from graphics.display_styles.displaymodes import get_display_mode_handler

from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList

##from drawer import drawlinelist

import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.gl_lighting import apply_material

from graphics.drawing.special_drawing import SPECIAL_DRAWING_STRAND_END
from graphics.drawing.special_drawing import SpecialDrawing_ExtraChunkDisplayList
from graphics.drawing.special_drawing import Chunk_SpecialDrawingHandler

from model.elements import PeriodicTable

# ==

_DRAW_BONDS = True # Debug/test switch. Similar constant in CS_workers.py.

# ==

class Chunk_drawing_methods:
    """
    Mixin (meant only for use by class Chunk) with all
    drawing-related methods for class Chunk which use
    OpenGL drawing (or the same drawing primitives)
    or which directly handle its OpenGL display lists.
    """
    
    # Note: there are a few significant points of interaction between other
    # Chunk methods/attrs and the ones in this mixin, which all have to be
    # refactored if we turn this into a cooperating class, especially if there
    # can be more than one instance of this class per Chunk (even though we
    # presume they all refer back to the chunk for its collor and display
    # style settings).
    
    # One of them is self.havelist, used extensively here and set to 0
    # in many places in chunk.py (both legitimate). (And also haveradii,
    # if it's different for different displayed views of one chunk,
    # which seems likely; if we move it, we might move sel_radii etc and
    # findAtomUnderMouse too -- or maybe they belong in yet another
    # cooperating class??)

    # Also, findAtomUnderMouse is either specific to a glpane or needs one
    # (and a viewing ray, etc) passed in, though it's not a display/drawing
    # method but a picking/selection method.
    
    # One might be _havelist_inval_counter, set in one place on a chunk by
    # external code.
    
    # One is the methods inval_display_list and changeapp. See one of them for
    # a more detailed comment about how to refactor them.

    # One might be the Chunk superclasses SelfUsageTrackingMixin,
    # SubUsageTrackingMixin, and the calls of their methods (which may occur
    # mostly or entirely in this file -- not reviewed).
    
    # Other users/setters of self.glpane include: this drawing code,
    # some external code, and the changeapp method in chunk.py.
    
    # The attribute self.memo_dict may belong in this class. It's used
    # by whole-Chunk display styles (displaymodes.py) -- we'll have to see
    # whether those run on a single displayed-Chunk object out of several
    # associated with one Chunk, and review the issue at that time.
    
    # The attribute glname is non-obvious, since it's possible that a chunk
    # has the same one even if displayed in more than one place -- or not,
    # if we want to use that to distinguish which copy is being hit.
    # Review this again when more refactoring is done.

        
    _havelist_inval_counter = 0 # see also self.havelist in chunk.py
    
    # there is no class default for displist; see _get_displist.
    
    def _init_Chunk_drawing_methods(self):
        """
        """
        # note: self.displist is allocated on demand by _get_displist 
        # [bruce 070523]

        self.extra_displists = {} # precaution, probably not needed
        
        return
    
    # == Methods relating to our OpenGL display list, self.displist.
    #
    # (Note: most of these methods could be moved with few changes to a new
    # mixin class [or cooperating class] concerned with maintaining
    # self.displist for any sort of object that needs one. If that's done, see
    # also GLPane_mixin_for_DisplayListChunk for useful features of other
    # kinds to integrate into that code. [bruce 071103/090123 comment])

    # Note about InvalMixin (Chunk superclass which handles invalidation
    # between attributes and calls _get_ and _recompute_ methods) relation to
    # display list:
    #
    # * display list contents (i.e. about invalidating the drawing effects of
    # executing it, when our graphical appearance changes): It's not sensible
    # to integrate the drawing effect of the display list contents into this
    # recompute system, since we normally execute it in OpenGL as a side
    # effect of recomputing it. To invalidate its contents, we just do this
    # directly as a special case, self.havelist = 0, in the low-level
    # modifiers that need to. The external interface to that is changeapp.
    #
    # * display list name allocated from OpenGL (value of self.displist); 
    # see _get_displist.
    
    def _get_displist(self):
        """
        initialize and return self.displist
        [must only be called when an appropriate GL context is current]
        """
        #bruce 070523 change: do this on demand, not in __init__, to see if it
        #fixes bug 2402 in which this displist can be 0 on Linux (when
        #entering Extrude).
        
        # Theory: you should allocate it only when you know you're in a good
        # GL context and are ready to draw, which is most safely done when you
        # are first drawing, so allocating it on demand is the easiest way to
        # do that. Theory about bug 2042: maybe some Qt drawing was changing
        # the GL context in an unpredictable way; we were not even making
        # glpane (or a thumbview) current before allocating this, until now.
        
        # Note: we use _get_displist rather than _recompute_displist so we
        # don't need to teach full_inval_and_update to ignore 'displist' as a
        # special case. WARNING: for this method it's appropriate to set
        # self.displist as well as returning it, but for most uses of _get_xxx
        # methods, setting it would be wrong.
        self.displist = ColorSortedDisplayList()
        return self.displist

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

    def _deallocate_displist(self): #bruce 071103
        """
        [private method; must only be called when our displist's GL context is current]
        Deallocate our OpenGL display list, and record that we did so.
        """
        if self.__dict__.has_key('displist'):
            # Note: we can't use hasattr for that test, since it would
            # allocate self.displist (by calling _get_displist) if we
            # don't have one yet.
            #russ 080225: Moved deallocation into ColorSortedDisplayList class
            # for ColorSorter.
            self.displist.deallocate_displists()
            for extra_displist in self.extra_displists.values():
                extra_displist.deallocate_displists()
            self.extra_displists = {}
            self.displist = None
            del self.displist
                # this del is necessary, so _get_displist will be called if another
                # display list is needed (e.g. if a killed chunk is revived by Undo)
            self.havelist = 0
            self.glpane = None
        pass

    def deallocate_displist_later(self): #bruce 071103
        """
        At the next convenient time when our OpenGL context is current,
        if self.ok_to_deallocate_displist(),
        call self._deallocate_displist().
        """
        self.call_when_glcontext_is_next_current( self._deallocate_displist_if_ok )
        return

    def _deallocate_displist_if_ok(self): #bruce 071103
        if self.ok_to_deallocate_displist():
            self._deallocate_displist()
        return

    def ok_to_deallocate_displist(self): #bruce 071103
        """
        Say whether it's ok to deallocate self's OpenGL display list
        right now (assuming our OpenGL context is current).
        """
        return len(self.atoms) == 0
            # self.killed() might also be correct,
            # but would be redundant with this anyway

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
        return self.__dict__.get('glpane', None)

    def call_when_glcontext_is_next_current(self, func): #bruce 071103
        """
        """
        glpane = self._gl_context_if_any()
        if glpane:
            glpane.call_when_glcontext_is_next_current(func)
        return

    def _deallocate_displist_if_needed(self):
        """
        """
        # bruce 090123 split this out of 
        # Chunk._f_invalidate_atom_lists_and_maybe_deallocate_displist
        if self._enable_deallocate_displist():
            need_to_deallocate = self.ok_to_deallocate_displist()
            if need_to_deallocate:
                ## print "undo or redo calling deallocate_displist_later on %r" % self
                self.deallocate_displist_later()
        return
        
    def _kill_displists(self): #bruce 090123 split this out of Chunk.kill
        """
        Private helper for Chunk.kill.
        """
        # todo: when this code is changed from mixin to cooperating object,
        # somehow this needs to happen to all such objects attached to one chunk
        # when that chunk is killed. [bruce 090123 comment]
        if self._enable_deallocate_displist():
            self.deallocate_displist_later() #bruce 071103
        return

    def _enable_deallocate_displist(self):
        res = debug_pref("GLPane: deallocate OpenGL display lists of killed chunks?",
                         Choice_boolean_True, # False is only useful for debugging
                         prefs_key = True )
        return res

    def _selectedness_drawing_effects(self, picked):
        """
        private helper for drawing effects of Chunk.pick and Chunk.unpick
        """
        #bruce 090123 split this out of Chunk.pick and Chunk.unpick;
        # REFACTOR: should not be needed once CSDL stops storing picked state.

        #russ 080303: Back again to display lists, this time color-sorted.
        self.displist.selectPick(picked)
            # Note: selectPick shouldn't be needed for self.extra_displists,
            # due to how they're drawn.
            ### REVIEW [bruce 090114]: is selectPick still needed for
            # self.displist? If not, is the CSDL picked state still needed
            # for anything? (A goal is to remove it entirely.) For status on
            # this, see my 090114 comments in ColorSorter.py (summary: it is
            # almost but not quite possible to remove it now).
        return

    # == drawing methods applicable to any TransformNode
    
    def pushMatrix(self):
        """
        Do glPushMatrix(), 
        then transform from (presumed) world coordinates
        to self's private coordinates.
        @see: self.applyMatrix()
        @see: self.popMatrix()
        """
        glPushMatrix()
        self.applyMatrix()
        return

    def applyMatrix(self):
        """
        Without doing glPushMatrix(), 
        transform from (presumed) world coordinates 
        to self's private coordinates.
        @see: self.pushMatrix()
        """
        # Russ 080922: If there is a transform in our main CSDL, use it instead.
        ### REVIEW [bruce 090113]: that is probably not correct in general.
        tc = self.displist.transformControl
        if tc is not None:
            tc.applyTransform()
        else:
            origin = self.basecenter
            glTranslatef(origin[0], origin[1], origin[2])
            q = self.quat
            glRotatef(q.angle*180.0/math.pi, q.x, q.y, q.z)
            pass
        return

    def popMatrix(self): #bruce 050609
        """
        Undo the effect of self.pushMatrix().
        """
        glPopMatrix()

    # == drawing methods which are mostly specific to Chunk, though they have
    # == plenty of more general aspects which ought to be factored out
    
    def draw(self, glpane, dispdef):
        """
        Draw all the atoms, using the atom's, self's,
        or GLPane's display mode in that order of preference.
        (Note that our dispdef argument is not used at all.)
        Draw each bond only once, even though internal bonds
        will be referenced from two atoms in this Chunk.
        (External bonds are drawn once by each Chunk they connect.)
        If the Chunk itself is selected, draw its bounding box as a
        wireframe; selected atoms are drawn specially by atom.draw.
        """

        # piotr 080331 moved this assignment before visibility 
        # and frustum culling tests 
        self.glpane = glpane # needed for the edit method - Mark [2004-10-13]
            # (and now also needed by BorrowerChunk during draw_dispdef's call
            #  of _dispfunc [bruce 060411])
            #
            ##e bruce 041109: couldn't we figure out self.glpane on the fly from self.dad?
            # (in getattr or in a special method)
            #bruce 050804: self.glpane is now also used in self.changeapp(),
            # since it's faster than self.track_change (whose features are overkill for this),
            # though the fact that only one glpane can be recorded in self
            # is a limitation we'll need to remove at some point.

        if not self.atoms:
            # do nothing for a Chunk without any atoms
            # [to fix bugs -- Huaicai 09/30/04]
            # (moved before frustum test, bruce 080411)
            return

        # Indicate overlapping atoms, if that pref is enabled.
        # We do this outside of the display list so we can still use that
        # for most of the drawing (for speed). We do it even for atoms
        # in hidden chunks, even in display modes that don't draw atoms,
        # etc. (But not for frustum culled atoms, since the indicators
        # would also be off-screen.) [bruce 080411 new feature]

        indicate_overlapping_atoms = self.part and self.part.indicate_overlapping_atoms
            # note: using self.part for this is a slight kluge;
            # see the comments where this variable is defined in class Part.

        if self.hidden and not indicate_overlapping_atoms:
            # (usually do this now, to avoid overhead of frustum test;
            #  if indicate_overlapping_atoms is true, we'll test self.hidden
            #  again below, to make sure we still skip other drawing)
            return

        # Frustum culling test # piotr 080331
        # piotr 080401: Do not return yet, because external bonds 
        # may be still drawn.
        # piotr 080402: Added a correction for the true maximum
        # DNA CPK atom radius.
        # Maximum VdW atom radius in PAM3/5 = 5.0 * 1.25 + 0.2 = 6.2
        # = MAX_ATOM_SPHERE_RADIUS
        # The default radius used by BBox is equal to sqrt(3*(1.8)^2) =
        # = 3.11 A, so the difference = approx. 3.1 A = BBOX_MIN_RADIUS
        # The '0.5' is another 'fuzzy' safety margin, added here just 
        # to be sure that all objects are within the sphere.
        # piotr 080403: moved the correction here from GLPane.py
        is_chunk_visible = glpane.is_sphere_visible(self.bbox.center(), 
                                                    self.bbox.scale() + 
                                                     (MAX_ATOM_SPHERE_RADIUS - BBOX_MIN_RADIUS)
                                                     + 0.5 )

        if indicate_overlapping_atoms and is_chunk_visible:
            self.draw_overlap_indicators_if_needed()

        if self.hidden:
            # catch the case where indicate_overlapping_atoms skipped this test earlier
            return

        self.basepos
        # make sure basepos is up-to-date, so basecenter is not changed
        # during the redraw. #e Ideally we'd have a way to detect or
        # prevent further changes to it during redraw, but this is not
        # needed for now since they should not be possible, and should
        # cause visible bugs if they happen. At least let's verify
        # the mol coord system has not changed by the time we're done:
        should_not_change = ( + self.basecenter, + self.quat )

        #bruce 050804:
        # tell whatever is now drawing our display list
        # (presumably our arg, glpane, but we don't assume this right here)
        # how to find out when our display list next becomes invalid,
        # so it can know it needs to redraw us.
        # (This is probably not actually needed at the moment, 
        # due to a special system used by self.changeapp() in place of
        # self.track_change(), but it should be harmless.)
        self.track_use()

        drawLevel = self.assy.drawLevel # this might recompute it
            # (if that happens and grabs the pref value, I think this won't
            #  subscribe our display list to it, since we're outside the
            #  begin/end for that, and that's good, since we include this in
            #  havelist instead, which avoids some unneeded redrawing, e.g. if
            #  pref changed and changed back while displaying a different Part.
            #  [bruce 060215])
            # update, bruce 080930: that point is probably moot, since
            #  drawLevel is part of havelist.

        disp = self.get_dispdef(glpane) 
            # piotr 080401: Moved it here, because disp is required by 
            # _draw_external_bonds.

        if is_chunk_visible:
            # piotr 080401: If the chunk is culled, skip drawing, but still draw 
            # external bonds (unless a separate debug pref is set.) 
            # The frustum culling test is now performed individually for every
            # external bond. 

            #This is needed for chunk highlighting
            ### REVIEW: this is our first use of "nested glnames". The hover
            # highlighting code in GLPane was written with the assumption
            # that we never use them, and the effects of using them on it
            # have not been reviewed. Conceivably it might slow it down
            # (by making some of its optims work less well, e.g. due to
            # overlapping highlight regions between self and its draw-children
            # with their own glnames (atoms and bonds), or cause bugs, though
            # I think both of those are unlikely, so this review is not urgent.
            # [bruce 080411 comment]
            glPushName(self.glname)

            # put it in its place
            glPushMatrix()

            try: #bruce 041119: do our glPopMatrix no matter what
                self.applyMatrix() # Russ 080922: This used to be inlined here.

                # Moved to above - piotr 080401
                # But what if there is an exception in self.get_dispdef ?
                # disp = self.get_dispdef(glpane)

    ##            delegate_selection_wireframe = False
                delegate_draw_atoms = False
                delegate_draw_chunk = False
                hd = None
                if 1:
                    #bruce 060608 look for a display mode handler for this chunk
                    # (whether it's a whole-chunk mode, or one we'll pass to the
                    #  atoms as we draw them (nim)).
                    hd = get_display_mode_handler(disp)
                    # see if it's a chunk-only handler. If so, we don't draw
                    # atoms or chunk selection wireframe ourselves -- instead,
                    # we delegate those tasks to it
                    if hd:
                        chunk_only = hd.chunk_only
    ##                    delegate_selection_wireframe = chunk_only
                        delegate_draw_atoms = chunk_only
                        delegate_draw_chunk = chunk_only
                            #e maybe later, we'll let hd tell us each of these,
                            # based on the chunk state.
                    pass

                #bruce 060608 moved drawing of selection wireframe from here to
                # after the new increment of _havelist_inval_counter
                # (and split it into a new submethod), even though it's done
                # outside of the display list. This was necessary for
                # _f_drawchunk_selection_frame's use of memoized data to work.            
                ## self._draw_selection_frame(glpane, delegate_selection_wireframe, hd)

                # cache chunk display (other than selection wireframe or hover
                # highlighting) as OpenGL display list

                # [bruce 050415 changed value of self.havelist when it's not 0,
                #  from 1 to (disp,),
                #  to fix bug 452 item 15 (no havelist inval for non-current
                #  parts when global default display mode is changed); this
                #  will incidentally optimize some related behaviors by avoiding
                #  some needless havelist invals, now that we've also removed
                #  the now-unneeded changeapp of all chunks upon global dispdef
                #  change (in GLPane.setGlobalDisplayStyle).]
                # [bruce 050419 also including something for element radius and
                #  color prefs, to fix bugs in updating display when those
                #  change (eg bug 452 items 12-A, 12-B).]

                eltprefs = PeriodicTable.color_change_counter, PeriodicTable.rvdw_change_counter
                matprefs = drawing_globals.glprefs.materialprefs_summary() #bruce 051126
                #bruce 060215 adding drawLevel to havelist
                if self.havelist == (disp, eltprefs, matprefs, drawLevel): 
                    # (note: value must agree with set of havelist, below)
                    # self.displist is still valid -- use it.
                    # Russ 081128: Switch from draw_dl() [now removed] to draw() with selection arg.
                    self.displist.draw(selected = self.picked)
                    for extra_displist in self.extra_displists.itervalues():
                        # [bruce 080604 new feature]
                        # note: similar code in else clause, differs re wantlist
                        extra_displist.draw_but_first_recompile_if_needed(glpane, selected = self.picked)
                        # todo: pass wantlist? yes in theory, but not urgent.
                        continue
                    pass
                else:
                    # our main display list (and all extra lists) needs to be remade
                    if 1:
                        #bruce 060608: record info to help per-chunk display modes
                        # figure out whether they need to invalidate their memo data.
                        if not self.havelist:
                            # Only count when it was set to 0 externally, not
                            # just when it doesn't match and we reset it
                            # below. (Note: current code will also increment
                            # this every frame, when wantlist is false. I'm
                            # not sure what to do about that. Could we set it
                            # here to False rather than 0, so we can tell??
                            # ##e)
                            self._havelist_inval_counter += 1
                        ##e in future we might also record eltprefs, matprefs,
                        ##drawLevel (since they're stored in .havelist)
                    self.havelist = 0 #bruce 051209: this is now needed
                    try:
                        wantlist = not env.mainwindow().movie_is_playing #bruce 051209
                            # warning: use of env.mainwindow is a KLUGE
                    except:
                        print_compact_traceback("exception (a bug) ignored: ")
                        wantlist = True
                    self.extra_displists = {} # we'll make new ones as needed
                    if wantlist:
                        ##print "Regenerating display list for %s" % self.name
                        match_checking_code = self.begin_tracking_usage()
                        #russ 080225: Moved glNewList into ColorSorter.start for displist re-org.
                        #russ 080225: displist side effect allocates a ColorSortedDisplayList.
                        #russ 080305: Chunk may already be selected, tell the CSDL.
                        ColorSorter.start(self.displist, self.picked)

                    # bruce 041028 -- protect against exceptions while making display
                    # list, or OpenGL will be left in an unusable state (due to the lack
                    # of a matching glEndList) in which any subsequent glNewList is an
                    # invalid operation. (Also done in shape.py; not needed in drawer.py.)
                    try:
                        self._draw_for_main_display_list(
                            glpane, disp,
                            (hd, delegate_draw_atoms, delegate_draw_chunk),
                            wantlist)
                    except:
                        print_compact_traceback("exception in Chunk._draw_for_main_display_list ignored: ")

                    if wantlist:
                        ColorSorter.finish()
                        #russ 080225: Moved glEndList into ColorSorter.finish for displist re-org.

                        self.end_tracking_usage( match_checking_code, self.inval_display_list )
                        # This is the only place where havelist is set to anything true;
                        # the value it's set to must match the value it's compared with, above.
                        # [bruce 050415 revised what it's set to/compared with; details above]
                        self.havelist = (disp, eltprefs, matprefs, drawLevel)
                        assert self.havelist, (
                            "bug: havelist must be set to a true value here, not %r"
                            % (self.havelist,))
                        # always set the self.havelist flag, even if exception happened,
                        # so it doesn't keep happening with every redraw of this Chunk.
                        #e (in future it might be safer to remake the display list to contain
                        # only a known-safe thing, like a bbox and an indicator of the bug.)

                    # draw the extra_displists (only needed if wantlist? not sure, so do always;
                    #  guess: there will be none of them unless wantlist is set, so it doesn't matter)
                    for extra_displist in self.extra_displists.itervalues():
                        extra_displist.draw_but_first_recompile_if_needed(glpane,
                                                                          selected = self.picked,
                                                                          wantlist = wantlist)
                        
                    pass # end of the case where "main display list (and extra lists) needs to be remade"

                # REVIEW: is it ok that self.glname is exposed for the following
                # renderOverlayText drawing? Guess: yes, even though it means mouseover
                # of the text will cause a redraw, and access to chunk context menu.
                # If it turns out that that redraw also visually highlights the chunk,
                # we might reconsider, but even that might be ok.
                # [bruce 081211 comments]
                if (self.chunkHasOverlayText and self.showOverlayText):
                    self.renderOverlayText(glpane)
                
                #@@ninad 070219 disabling the following--
                ## self._draw_selection_frame(glpane, delegate_selection_wireframe, hd)

                # piotr 080320
                if hd:
                    hd._f_drawchunk_realtime(glpane, self)

                if self.hotspot is not None: 
                    # note: accessing self.hotspot can have side effects in getattr
                    self.overdraw_hotspot(glpane, disp) 
                        # note: this only does anything for pastables
                        # (toplevel clipboard items) as of 050316

                # russ 080409 Array to string formatting is slow, avoid it
                # when not needed.  Use !=, not ==, to compare Numeric arrays.
                # (!= returns V(0,0,0), a False boolean value, when equal.)
                if (should_not_change[0] != self.basecenter or
                    should_not_change[1] != self.quat):
                    assert `should_not_change` == `( + self.basecenter, + self.quat )`, \
                           "%r != %r, what's up?" % (should_not_change,
                                                     ( + self.basecenter, + self.quat))

                pass # end of drawing within self's local coordinate frame

            except:
                print_compact_traceback("exception in Chunk.draw, continuing: ")

            glPopMatrix()

            glPopName() # pops self.glname

            pass # end of 'if is_chunk_visible:'

        self._draw_outside_local_coords(glpane, disp, drawLevel, is_chunk_visible)

        return # from Chunk.draw()

    def renderOverlayText(self, glpane): # by EricM
        gotone = False
        for atom in self.atoms.itervalues():
            text = atom.overlayText
            if (text):
                gotone = True
                pos = atom.baseposn()
                radius = atom.drawing_radius() * 1.01
                pos = pos + glpane.out * radius
                glpane.renderTextAtPosition(pos, text)
        if (not gotone):
            self.chunkHasOverlayText = False

    def _draw_outside_local_coords(self, glpane, disp, drawLevel, is_chunk_visible):
        #bruce 080520 split this out
        """
        Do the part of self.draw that goes outside self's
        local coordinate system and outside its display list.

        [Subclasses can extend this if needed.]
        """
        draw_external_bonds = True # piotr 080401
            # Added for the additional test - the external bonds could be still
            # visible even if the chunk is culled.

        # For extra performance, the user may skip drawing external bonds
        # entirely if the frustum culling is enabled. This may have some side
        # effects: problems in highlighting external bonds or missing 
        # external bonds if both chunks are culled. piotr 080402
        if debug_pref("GLPane: skip all external bonds for culled chunks",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True): 
            # the debug pref has to be checked first
            if not is_chunk_visible: # the chunk is culled piotr 080401
                # so don't draw external bonds at all
                draw_external_bonds = False

        # draw external bonds.

        # Could we skip this if display mode "disp" never draws bonds?
        # No -- individual atoms might override that display mode.
        # Someday we might decide to record whether that's true when
        # recomputing externs, and to invalidate it as needed -- since it's
        # rare for atoms to override display modes. Or we might even keep a
        # list of all our atoms which override our display mode. ###e
        # [bruce 050513 comment]
        if draw_external_bonds and self.externs:
            self._draw_external_bonds(glpane, disp, drawLevel, is_chunk_visible)

        return # from Chunk._draw_outside_local_coords()

    def _draw_external_bonds(self, glpane, disp, drawLevel, is_chunk_visible = True):
        """
        Draw self's external bonds (if debug_prefs and frustum culling permit).
        """
        if not _DRAW_BONDS:
            return
        #bruce 080215 split this out, added one debug_pref
        
        # decide whether to draw any external bonds at all
        # (possible optim: decide once per redraw, cache in glpane)
        
        # piotr 080320: if this debug_pref is set, the external bonds 
        # are hidden whenever the mouse is dragged. This speeds up interactive 
        # manipulation of DNA segments by a factor of 3-4x in tubes
        # or ball-and-sticks display styles.
        # This extends the previous condition to suppress the external
        # bonds during animation.
        suppress_external_bonds = (
           (getattr(glpane, 'in_drag', False) # glpane.in_drag undefined in ThumbView
            and
            debug_pref("GLPane: suppress external bonds when dragging?",
                           Choice_boolean_False,
                           non_debug = True,
                           prefs_key = True
                           ))
           or 
           (self.assy.o.is_animating # review: test in self.assy.o or glpane?
            and
            debug_pref("GLPane: suppress external bonds when animating?",
                           Choice_boolean_False,
                           non_debug = True,
                           prefs_key = True
                           ))
         )
        
        if suppress_external_bonds:
            return
        
        # external bonds will be drawn (though some might be culled).
        # make sure the info needed to draw them is up to date.
        
        self._update_bonded_chunks()
        
        bondcolor = self.drawing_color()
        selColor = env.prefs[selectionColor_prefs_key]
        
        # decide whether external bonds should be frustum-culled.
        frustum_culling_for_external_bonds = \
            not is_chunk_visible and use_frustum_culling()
            # piotr 080401: Added the 'is_chunk_visible' parameter default to True
            # to indicate if the chunk is culled or not. Assume that if the chunk
            # is not culled, we have to draw the external bonds anyway. 
            # Otherwise, there is a significant performance hit for frustum
            # testing the visible bonds. 

        # find or set up repeated_bonds_dict
        
        # Note: to prevent objects (either external bonds themselves,
        # or ExternalBondSet objects) from being drawn twice,
        # [new feature, bruce 070928 bugfix and optimization]
        # we use a dict recreated each time their part gets drawn,
        # in case of multiple views of the same part in one glpane;
        # ideally the draw methods would be passed a "model-draw-frame"
        # instance (associated with the part) to make this clearer.
        # If we can ever draw one chunk more than once when drawing one part,
        # we'll need to modify this scheme, e.g. by optionally passing
        # that kind of object -- in general, a "drawing environment"
        # which might differ on each draw call of the same object.)
        model_draw_frame = self.part # kluge, explained above
            # note: that's the same as each bond's part.
        repeated_bonds_dict = model_draw_frame and model_draw_frame.repeated_bonds_dict
        del model_draw_frame
        if repeated_bonds_dict is None:
            # (Note: we can't just test "not repeated_bonds_dict",
            #  in case it's {}.)
            # This can happen when chunks are drawn in other ways than
            # via Part.draw (e.g. as Extrude mode repeat units),
            # or [as revised 080314] due to bugs in which self.part is None;
            # we need a better fix for this, but for now,
            # just don't use the dict. As a kluge to avoid messing up
            # the loop below, just use a junk dict instead.
            # [bruce 070928 fix new bug 2548]
            # (This kluge means that external bonds drawn by e.g. Extrude
            # will still be subject to the bug of being drawn twice.
            # The better fix is for Extrude to set up part.repeated_bonds_dict
            # when it draws its extra objects. We need a bug report for that.)
            repeated_bonds_dict = {} # KLUGE

        if debug_pref("GLPane: use ExternalBondSets for drawing?", #bruce 080707
                      Choice_boolean_False,
                          # won't be default True until it's not slower, & tested
                      non_debug = True,
                      prefs_key = True ):
            objects_to_draw = self._bonded_chunks.itervalues()
            use_outer_colorsorter = False
        else:
            objects_to_draw = self.externs
            use_outer_colorsorter = True
        
        # actually draw them

        if use_outer_colorsorter:
            ColorSorter.start(None)
                # [why is this needed? bruce 080707 question]
        
        for bond in objects_to_draw:
            # note: bond might be a Bond, or an ExternalBondSet
            if id(bond) not in repeated_bonds_dict:
                # BUG: disp and bondcolor depend on self, so the bond appearance
                # may depend on which chunk draws it first (i.e. on their Model
                # Tree order). How to fix this is the subject of a current design
                # discussion. [bruce 070928 comment]
                repeated_bonds_dict[id(bond)] = bond
                if frustum_culling_for_external_bonds:
                    # bond frustum culling test piotr 080401
                    ### REVIEW: efficient under all settings of debug_prefs??
                    # [bruce 080702 question]
                    c1, c2, radius = bond.bounding_lozenge()
                    if not glpane.is_lozenge_visible(c1, c2, radius):
                        continue # skip the bond drawing if culled
                if bond.should_draw_as_picked():
                    color = selColor #bruce 080430 cosmetic improvement
                else:
                    color = bondcolor
                bond.draw(glpane, disp, color, drawLevel)
            continue
        
        if use_outer_colorsorter:
            ColorSorter.finish()
        
        return # from _draw_external_bonds

##    def _draw_selection_frame(self, glpane, delegate_selection_wireframe, hd):
##        "[private submethod of self.draw]"
##        if self.picked:
##            if not delegate_selection_wireframe:
##                try:
##                    drawlinelist(PickedColor, self.polyhedron or [])
##                except:
##                    # bruce 041119 debug code;
##                    # also "or []" failsafe (above)
##                    # in case recompute exception makes it None
##                    print_compact_traceback("exception in drawlinelist: ")
##                    print "(self.polyhedron is %r)" % self.polyhedron
##            else:
##                hd._f_drawchunk_selection_frame(glpane, self, PickedColor, highlighted = False)
##            pass
##        return

    def draw_overlap_indicators_if_needed(self): #bruce 080411, renamed 090108
        """
        If self overlaps any atoms (in self's chunk or in other chunks)
        already scanned (by calling this method on them) during this drawing 
        frame (paintGL call),
        draw overlap indicators around self and/or those atoms as needed,
        so that each atom needing an overlap indicator gets one drawn at
        least once, assuming this method is called on all atoms drawn
        during this drawing frame.
        """
        model_draw_frame = self.part # kluge, explained elsewhere in this file
        if not model_draw_frame:
            return
        neighborhoodGenerator = model_draw_frame._f_state_for_indicate_overlapping_atoms
        for atom in self.atoms.itervalues():
            pos = atom.posn()
            prior_atoms_too_close = neighborhoodGenerator.region(pos)
            if prior_atoms_too_close:
                # This atom overlaps the prior atoms.
                # Draw an indicator around it,
                # and around the prior ones if they don't have one yet.
                # (That can be true even if there is more than one of them,
                #  if the prior ones were not too close to each other,
                #  so for now, just draw it on the prior ones too, even
                #  though this means drawing it twice for each atom.)
                #
                # Pass an arg which indicates the atoms for which one or more
                # was too close. See draw_overlap_indicator docstring for more
                # about how that can be used, given our semi-symmetrical calls.
                for prior_atom in prior_atoms_too_close:
                    prior_atom.draw_overlap_indicator((atom,))
                atom.draw_overlap_indicator(prior_atoms_too_close)
            neighborhoodGenerator.add(atom)
            continue
        return

    def _draw_for_main_display_list(self, glpane, disp0, hd_info, wantlist):
        """
        [private submethod of self.draw]

        Draw the contents of our main display list, which the caller
        has already opened for compile and execute (or the equivalent,
        if it's a ColorSortedDisplayList object) if wantlist is true,
        or doesn't want to open otherwise (so we do immediate mode
        drawing then).

        Also (if self attrs permit and wantlist argument is true)
        capture functions for deferred drawing into new instances
        of appropriate subclasses of ExtraChunkDisplayList added to
        self.extra_displists, so that some aspects of our atoms and bonds
        can be drawn from separate display lists, to avoid remaking our
        main one whenever those need to change.
        """
        if wantlist and \
            hasattr(glpane, 'graphicsMode') and \
            debug_pref("use special_drawing_handlers?",
                                   Choice_boolean_True, #bruce 080606 enable by default for v1.1
                                   non_debug = True,    # (but leave it visible in case of bugs)
                                   prefs_key = True):
            # set up the right kind of special_drawing_handler for self;
            # this will be passed to the draw calls of our atoms and bonds
            # [new feature, bruce 080605]
            #
            # bugfix [bruce 080606 required for v1.1, for dna in partlib view]:
            # hasattr test, since ThumbView has no graphicsMode.
            # (It ought to, but that's a refactoring too big for this release,
            #  and giving it a fake one just good enough for this purpose doesn't
            #  seem safe enough.)
            special_drawing_classes = { # todo: move into a class constant
                SPECIAL_DRAWING_STRAND_END: SpecialDrawing_ExtraChunkDisplayList,
             }
            self.special_drawing_handler = \
                    Chunk_SpecialDrawingHandler( self, special_drawing_classes )
        else:
            self.special_drawing_handler = None
        del wantlist

        #bruce 050513 optimizing this somewhat; 060608 revising it
        if debug_pref("GLPane: report remaking of chunk display lists?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True ): #bruce 080214
            print "debug fyi: remaking display lists for chunk %r" % self
            summary_format = graymsg( "debug fyi: remade display lists for [N] chunk(s)" )
            env.history.deferred_summary_message(summary_format)

        hd, delegate_draw_atoms, delegate_draw_chunk = hd_info

        # draw something for the chunk as a whole
        if delegate_draw_chunk:
            hd._f_drawchunk(self.glpane, self)
        else:
            self._standard_draw_chunk(glpane, disp0)

        # draw the individual atoms and internal bonds (if desired)
        if delegate_draw_atoms:
            pass # nothing for this is implemented, or yet needed [as of bruce 060608]
        else:
            self._standard_draw_atoms(glpane, disp0)
        return

    def highlight_color_for_modkeys(self, modkeys):
        """
        This is used to return a highlight color for the chunk highlighting. 
        See a comment in this method below
        """
        #NOTE: before 2008-03-13, the chunk highlighting was achieved by using
        #the atoms and bonds within the chunk. The Atom and Bond classes have
        #their own glselect name, so the code was able to recognize them as
        #highlightable objects and then depending upon the graphics mode the
        #user was in, it used to highlight the whole chunk by accessing the
        #chunk using, for instance, atom.molecule. although this is still
        #implemented, for certain display styles such as DnaCylinderChunks,
        #the atoms and bonds are never drawn. So there is no way to access the
        #chunk! To fix this, we need to make chunk a highlightable object.
        #This is done by making sure that the chunk gets a glselect name
        #(glname) and by defining this API method - Ninad 2008-03-13

        return env.prefs[hoverHighlightingColor_prefs_key]

    def draw_highlighted(self, glpane, color):
        """
        Draws this chunk as highlighted with the specified color. 
        
        In future, 'draw_in_abs_coords' defined on some node classes
        could be merged into this method (for highlighting various objects).

        @param glpane: the GLPane
        @param color: highlight color
        
        @see: dna_model.DnaGroup.draw_highlighted
        @see: SelectChunks_GraphicsMode.drawHighlightedChunk()
        @see: SelectChunks_GraphicsMode._get_objects_to_highlight()
        """
        #This was originally a sub-method in 
        #SelectChunks_GraphicsMode.drawHighlightedChunks. Moved here 
        #(Chunk.draw_highlighted) on 2008-02-26

        # Early frustum clipping test. piotr 080331
        # Could it cause any trouble by not drawing the external bonds?
        # REVIEW [bruce 090114]: is there any good reason to use this test
        # for highlighted-object drawing (i.e. cases when some chunks out
        # of whatever gets highlighted are not at all visible)?
        if not glpane.is_sphere_visible(self.bbox.center(), self.bbox.scale()):
            return

        # Russ 081212: Switch from glCallList to CSDL.draw for shader prims.
        if self.__dict__.has_key('displist'):
            # (note: attr is missing if displist was not yet allocated)
            apply_material(color) ### REVIEW: still needed?
            self.pushMatrix()
            for csdl in ([self.displist] +
                         [ed.csdl for ed in self.extra_displists.values()]):
                csdl.draw(highlighted = True, highlight_color = color)
            self.popMatrix()
            pass

        # piotr 080521: Get display mode for drawing external bonds and/or
        # the "realtime" objects.
        disp = self.get_dispdef(glpane)

        #russ 080302: Draw external bonds.
        if self.externs:
            # From Chunk.draw():
            drawLevel = self.assy.drawLevel
            # From Chunk._draw_external_bonds:
            # todo [bruce 090114 comment]: optimize this to not draw them twice
            # (as was done in older code). (Note that there will soon be
            # objects containing display lists for them, and our job will
            # be to not draw *those objects* twice, in any one frame.)
            ColorSorter.start(None)
            for bond in self.externs:
                bond.draw(glpane, disp, color, drawLevel)
                continue
            ColorSorter.finish()
            pass
        pass

        # piotr 080521
        # Highlight "realtime" objects (e.g. 2D DNA cylinder style).
        hd = get_display_mode_handler(disp)
        if hd:
            hd._f_drawchunk_realtime(glpane, self, highlighted = True)
            pass
        
        return

    def _standard_draw_chunk(self, glpane, disp0, highlighted = False):
        """
        [private submethod of self.draw]
        
        Draw the standard representation of this chunk as a whole
        (except for chunk selection wireframe),
        as if self's display mode was disp0 (not a whole-chunk display mode).
        
        This is run inside our local coordinate system and display-list-making.
        
        It is not run if chunk drawing is delegated to a whole-chunk display mode.

        @note: as of 080605 or before, this is always a noop, but is kept around
               since it might be used someday (see code comments)
        """
        # note: we're keeping this for future expansion even though it's
        # always a noop at the moment (even in subclasses). 
        # It's not used for whole-chunk display styles, but it might be used
        # someday, e.g. to let chunks show their axes, name, bbox, etc,
        # or possibly to help implement a low-level-of-detail form.
        # [bruce 090113 comment]
        del glpane, disp0, highlighted
        return

    def drawing_color(self): #bruce 080210 split this out, used in Atom.drawing_color
        """
        Return the color tuple to use for drawing self, or None if
        per-atom colors should be used.
        """
        color = self.color # None or a color
        color = self.modify_color_for_error(color)
            # (no change in color if no error)
        return color

    def modify_color_for_error(self, color):
        """
        [overridden in some subclasses]
        """
        return color

    def _standard_draw_atoms(self, glpane, disp0): 
        """
        [private submethod of self.draw:]
        
        Draw all our atoms and all their internal bonds, in the standard way,
        *including* atom selection wireframes, as if self's display mode was disp0;
        this occurs inside our local coordinate system and display-list-making;
        it doesn't occur if atom drawing is delegated to our display mode.
        """
        #bruce 060608 split this out of _draw_for_main_display_list
        drawLevel = self.assy.drawLevel
        drawn = {}
        ## self.externs = [] # bruce 050513 removing this
        # bruce 041014 hack for extrude -- use _colorfunc if present
        # [part 1; optimized 050513]
        _colorfunc = self._colorfunc # might be None 
            # [as of 050524 we supply a default so it's always there]
        _dispfunc = self._dispfunc 
            #bruce 060411 hack for BorrowerChunk, might be more generally useful someday

        atomcolor = self.drawing_color() # None or a color
            # bruce 080210 bugfix (predicted) [part 1 of 2]:
            # use this even when _colorfunc is being used
            # (so chunk colors work in Extrude; IIRC there was a bug report on that)
            # [UNTESTED whether that bug exists and whether this fixes it]

        bondcolor = atomcolor # never changed below

        for atom in self.atoms.itervalues(): 
            #bruce 050513 using itervalues here (probably safe, speed is needed)
            try:
                color = atomcolor # might be modified before use
                disp = disp0 # might be modified before use
                # bruce 041014 hack for extrude -- use _colorfunc if present 
                # [part 2; optimized 050513]
                if _colorfunc is not None:
                    try:
                        color = _colorfunc(atom) # None or a color
                    except:
                        print_compact_traceback("bug in _colorfunc for %r and %r: " % (self, atom)) 
                        _colorfunc = None # report the error only once per displist-redraw
                        color = None
                    else:
                        if color is None:
                            color = atomcolor
                                # bruce 080210 bugfix (predicted) [part 2 of 2]
                        #bruce 060411 hack for BorrowerChunk; done here and
                        # in this way in order to not make ordinary drawing
                        # inefficient, and to avoid duplicating this entire method:
                        if _dispfunc is not None:
                            try:
                                disp = _dispfunc(atom)
                            except:
                                print_compact_traceback("bug in _dispfunc for %r and %r: " % (self, atom))
                                _dispfunc = None # report the error only once per displist-redraw
                                disp = disp0 # probably not needed
                                pass
                            pass
                        pass
                    pass
                # otherwise color and disp remain unchanged

                # end bruce hack 041014, except for use of color rather than
                # self.color in atom.draw (but not in bond.draw -- good??)

                atomdisp = atom.draw(
                    glpane, disp, color, drawLevel,
                    special_drawing_handler = self.special_drawing_handler
                 )

                #bruce 050513 optim: if self and atom display modes don't need to draw bonds,
                # we can skip drawing bonds here without checking whether their other atoms
                # have their own display modes and want to draw them,
                # since we'll notice that when we get to those other atoms
                # (whether in self or some other chunk).
                # (We could ask atom.draw to return a flag saying whether to draw its bonds here.)
                #    To make this safe, we'd need to not recompute externs here,
                # but that should be ok since they're computed separately anyway now.
                # So I'm removing that now, and doing this optim.
                ###e (I might need to specialcase it for singlets so their 
                # bond-valence number is still drawn...) [bruce 050513]
                #bruce 080212: this optim got a lot less effective since a few CPK bonds
                # are now also drawn (though most are not).

                if atomdisp in (diBALL, diLINES, diTUBES, diTrueCPK, diDNACYLINDER):
                    # todo: move this tuple into bonds module or Bond class
                    for bond in atom.bonds:
                        if id(bond) not in drawn:
                            ## if bond.other(atom).molecule != self: could be faster [bruce 050513]:
                            if bond.atom1.molecule is not self or bond.atom2.molecule is not self:
                                pass ## self.externs.append(bond) # bruce 050513 removing this
                            else:
                                # internal bond, not yet drawn
                                drawn[id(bond)] = bond
                                bond.draw(glpane, disp, bondcolor, drawLevel,
                                          special_drawing_handler = self.special_drawing_handler
                                          )  
            except:
                # [bruce 041028 general workaround to make bugs less severe]
                # exception in drawing one atom. Ignore it and try to draw the
                # other atoms. #e In future, draw a bug-symbol in its place.
                print_compact_traceback("exception in drawing one atom or bond ignored: ")
                try:
                    print "current atom was:", atom
                except:
                    print "current atom was... exception when printing it, discarded"
                try:
                    atom_source = atom._f_source # optional atom-specific debug info
                except AttributeError:
                    pass
                else:
                    print "Source of current atom:", atom_source
        return # from _standard_draw_atoms (submethod of _draw_for_main_display_list)

    def overdraw_hotspot(self, glpane, disp): #bruce 050131
        """
        If this chunk is a (toplevel) clipboard item with a hotspot
        (i.e. if pasting it onto a bond will work and use its hotspot),
        display its hotspot in a special form.
        As with selatom, we do this outside of the display list.        
        """
        if self._should_draw_hotspot(glpane):
            hs = self.hotspot
            try:
                color = env.prefs[bondpointHotspotColor_prefs_key] #bruce 050808

                level = self.assy.drawLevel #e or always use best level??
                ## code copied from selatom.draw_as_selatom(glpane, disp, color, level)
                pos1 = hs.baseposn()
                drawrad1 = hs.highlighting_radius(disp)
                ## drawsphere(color, pos1, drawrad1, level) # always draw, regardless of disp
                hs.draw_atom_sphere(color, pos1, drawrad1, level, None, abs_coords = False)
                    #bruce 070409 bugfix (draw_atom_sphere); important if it's really a cone
            except:
                msg = "debug: ignoring exception in overdraw_hotspot %r, %r" % \
                      (self, hs)
                print_compact_traceback(msg + ": ")
                pass
            pass
        return

    def _should_draw_hotspot(self, glpane): #bruce 080723 split this out, cleaned it up
        """
        Determine whether self has a valid hotspot and wants to draw it specially.
        """
        # bruce 050416 warning: the conditions here need to match those in depositMode's
        # methods for mentioning hotspot in statusbar, and for deciding whether a clipboard
        # item is pastable. All this duplicated hardcoded conditioning is bad; needs cleanup. #e
        
        # We need these checks because some code removes singlets from a chunk (by move or kill)
        # without checking whether they are that chunk's hotspot.

        # review/cleanup: some of these checks might be redundant with checks
        # in the get method run by accessing self.hotspot.
            
        hs = self.hotspot ### todo: move lower, after initial tests

        wanted = (self in self.assy.shelf.members) or glpane.always_draw_hotspot
            #bruce 060627 added always_draw_hotspot re bug 2028
        if not wanted:
            return False

        if hs is None:
            return False
        if not hs.is_singlet():
            return False
        if not hs.key in self.atoms:
            return False
        return True

    pass # end of class Chunk_drawing_methods

# end
