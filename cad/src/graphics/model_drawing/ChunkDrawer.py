# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
ChunkDrawer.py -- class ChunkDrawer, for drawing a chunk
(using OpenGL or compatible primitives -- someday this may cover POV-Ray
as well, but it doesn't as of early 2009)

@author: Josh, Bruce, others
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.


History:

Written over several years as part of chunk.py.

bruce 090123 split these methods out of class Chunk in chunk.py.
(For prior svn history, see chunk.py. I decided against using
svn copy, even though this code has lots of history in there,
since it's shortly going to get refactored much more within
this file, and things will be clearer if this split starts
a clear separation of old and new in the history,
especially since 3/4 of the old chunk.py is not this code.)

bruce 090211 added markers where code was recently duplicated between self.draw
and TransformedDisplayListsDrawer.draw (not yet used). This should be refactored
soon into a common superclass, but first we need to

bruce 090212 change mixin class into cooperating object ChunkDrawer

bruce 090213 rename and move this module into graphics.model_drawing.ChunkDrawer


TODO: refactor:

 * someday, use GraphicsRules, and make more than one instance per Chunk
   possible (supporting more than one view of a chunk, mixed display styles,
   and/or multiple cached display styles)

 * soon [old description:]
   split it into sub/superclasses for Chunk and the superclasses
   to be split out of Chunk (e.g. AtomCloud, PointCloud, TransformNode
   (all names tentative); this involves picking apart def draw in
   particular, since the display list and transform code is general,
   but there is specific code for atoms & bonds as well; some of this
   will ultimately turn into GraphicsRules (name also tentative)

   [newer description:] split out a superclass TransformedDisplayListsDrawer

"""

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName


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
from utilities.prefs_constants import selectionColor_prefs_key


import foundation.env as env


from graphics.display_styles.displaymodes import get_display_mode_handler

from graphics.drawing.ColorSorter import ColorSorter

##from drawer import drawlinelist

import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.gl_lighting import apply_material

from graphics.model_drawing.special_drawing import SPECIAL_DRAWING_STRAND_END
from graphics.model_drawing.special_drawing import SpecialDrawing_ExtraChunkDisplayList
from graphics.model_drawing.special_drawing import Chunk_SpecialDrawingHandler

from graphics.model_drawing.TransformedDisplayListsDrawer import TransformedDisplayListsDrawer

from model.elements import PeriodicTable

# ==

_DRAW_EXTERNAL_BONDS = True # Debug/test switch.
    # note: there is a similar constant _DRAW_BONDS in CS_workers.py.

# ==

class ChunkDrawer(TransformedDisplayListsDrawer):
    """
    Drawing class (meant only for use by class Chunk)
    """
    #bruce 090211 renamed from Chunk_drawing_methods, revised from mixin
    # into cooperating class. The older mixin class in this file contained all
    # drawing-related methods for class Chunk which use
    # OpenGL drawing (or the same drawing primitives)
    # or which directly handle its OpenGL display lists.
    
    # Note: there are a few significant points of interaction between methods
    # and attrs in Chunk and ChunkDrawer. These can be found via their
    # interobject references: self._drawer in Chunk points to this object,
    # and self._chunk in this class points to its Chunk. That might be revised
    # if there can be more than one instance of this class per Chunk (though we
    # presume they all refer back to the chunk for its color and display
    # style settings). 

    # Some of the methods/attrs that might want further refactoring include:
    
    
    # - haveradii, if it should be different for different displayed views
    # of one chunk, which seems likely; if we move it, we might move sel_radii
    # etc and findAtomUnderMouse too -- or maybe they belong in yet another
    # cooperating class??

    # - findAtomUnderMouse is either specific to a glpane or needs one
    # (and a viewing ray, etc) passed in, though it's not a display/drawing
    # method but a picking/selection method.
    
    # - _havelist_inval_counter in this class, and Chunk _memo_dict, are only
    # used together (by whole-Chunk display styles (displaymodes.py), via new
    # methods in class Chunk). Further refactoring is desirable.
    
    # - self.glname is non-obvious, since it's possible that a chunk
    # has the same one even if displayed in more than one place -- or not,
    # if we want to use that to distinguish which copy is being hit.
    # Review this again when more refactoring is done. For now, it's in Chunk.
    
    def __init__(self, chunk):
        """
        """
        TransformedDisplayListsDrawer.__init__(self)
        self._chunk = chunk
        return

    # == unsorted methods

    def invalidate_display_lists_for_style(self, style): #bruce 090211
        """
        @see: documentation of same method in class Chunk

        [overrides superclass method]
        """
        #### TODO: revise this when chunks can cache display lists even for
        # non-current display styles, to revise any cached style-including
        # display lists, whether or not that's the current style.
        if not self.glpane or \
           self._chunk.get_dispdef(self.glpane) == style:
            self.invalidate_display_lists()
        return

        #### REVIEW: all comments about track_inval, havelist, changeapp,
        # and whether the old code did indeed do changeapp and thus gl_update_something.

    def _ok_to_deallocate_displist(self): #bruce 071103
        """
        Say whether it's ok to deallocate self's OpenGL display list
        right now (assuming our OpenGL context is current).

        [overrides TransformedDisplayListsDrawer method]
        """
        return len(self._chunk.atoms) == 0
            # self.killed() might also be correct,
            # but would be redundant with this anyway
    
    # == drawing methods which are mostly specific to Chunk, though they have
    # == plenty of more general aspects which ought to be factored out

    def is_visible(self, glpane):
        """
        Is self visible in the given glpane?

        Use a fast test; false positives are ok.
        """
        # by piotr 080331; bruce 090212 split into separate method
        # piotr 080402: Added a correction for the true maximum
        # DNA CPK atom radius.
        # Maximum VdW atom radius in PAM3/5 = 5.0 * 1.25 + 0.2 = 6.2
        # = MAX_ATOM_SPHERE_RADIUS
        # The default radius used by BBox is equal to sqrt(3*(1.8)^2) =
        # = 3.11 A, so the difference = approx. 3.1 A = BBOX_MIN_RADIUS
        # The '0.5' is another 'fuzzy' safety margin, added here just 
        # to be sure that all objects are within the sphere.
        # piotr 080403: moved the correction here from GLPane.py
        bbox = self._chunk.bbox
        center = bbox.center()
        radius = bbox.scale() + (MAX_ATOM_SPHERE_RADIUS - BBOX_MIN_RADIUS) + 0.5
        return glpane.is_sphere_visible( center, radius )

    def draw_csdl(self, csdl, selected = False): #bruce 090218 ##### CALL IN MORE PLACES, this class and EBset
        drawing_frame = self.get_drawing_frame()
        if drawing_frame and drawing_frame.use_drawingsets:
            intent = bool(selected) #### for now ##### PROBABLY WRONG RE TRANSFORM in current calling code
            drawing_frame.draw_csdl_in_drawingset(csdl, intent)
        else:
            csdl.draw(selected = selected)
        return
    
    def draw(self, glpane):
        """
        Draw self (including its external bonds, perhaps optimizing
        to avoid drawing them twice) in the appropriate display style,
        based on the style assigned to self's individual atoms
        (if there is one), or to self, or to glpane.

        This draws everything associated with self or its atoms or bonds,
        including atom-selection indicators, atom overlap indicators,
        error indicators, self's appearance as selected or not,
        bond letters, base letters, etc. Most but not all of what we draw
        is included in one or more display lists, which are updated as needed
        before drawing them.

        The output of this method consists of side effects, namely OpenGL calls
        (which are not in general suitable for inclusion in a display list being
        compiled by the caller).
        
        The correct GL context must be current whenever this method is called.
        """
        #bruce 090212 revised docstring
        
        # review:
        # - is glpane argument used, aside from setting self.glpane? [yes.]
        # - is self.glpane used in this method (after we set it initially)?
        #   [yes, at least in a submethod.]
        # - (regarding self.glpane uses after this method returns, see below.)
        # - is any other way of finding the glpane used?
        # someday, clean up everything related to the glpane arg and self.glpane
        # (or effectively supersede them by using GraphicsRules).
        
        self.glpane = glpane # needed, see below 
            ### review (not urgent): during this method, or after it returns,
            # is self.glpane needed here or in self._chunk or both? [bruce 090212]
            #
            # known reasons self.glpane might be needed in one or the other class:
            # - for the edit method - Mark [2004-10-13]
            # - in BorrowerChunk._dispfunc, called by draw_dispdef [bruce 060411]
            # - in invalidate_display_lists_for_style [bruce 090212]
            # - by self.call_when_glcontext_is_next_current via self._gl_context_if_any
            # - for delegate_draw_chunk, see code below
            # - in Chunk.changeapp [removed as of bruce 090212]
            #   note: the old comment about that use said:
                #bruce 050804: self.glpane is now also used in self.changeapp(),
                # since it's faster than self.track_inval (whose features are overkill for this),
                # though the fact that only one glpane can be recorded in self
                # is a limitation we'll need to remove at some point.
            # but now I'm revising that (in self.invalidate_display_lists) to use
            # track_inval, not direct gl_update (or related method), since
            # that's theoretically better. (So it's no longer a use of
            # self.glpane.) If it's too slow (which I doubt), we'll notice it
            # in a profile and optimize it.
        
        if not self._chunk.atoms:
            return

        # Indicate overlapping atoms, if that pref is enabled.
        # We do this outside of the display list so we can still use that
        # for most of the drawing (for speed). We do it even for atoms
        # in hidden chunks, even in display modes that don't draw atoms,
        # etc. (But not for frustum culled atoms, since the indicators
        # would also be off-screen.) [bruce 080411 new feature]

        drawing_frame = self.get_drawing_frame()
        
        indicate_overlapping_atoms = drawing_frame and \
                                     drawing_frame.indicate_overlapping_atoms
            # note: using self._chunk.part for this is a slight kluge;
            # see the comments where this variable is defined in class Part.

        if self._chunk.hidden and not indicate_overlapping_atoms:
            # (usually do this now, to avoid overhead of frustum test;
            #  if indicate_overlapping_atoms is true, we'll test
            #  self._chunk.hidden again below, to make sure we still
            #  skip other drawing)
            return

        # Frustum culling test [piotr 080331]
        # Don't return yet on failure, because external bonds 
        # may be still drawn [piotr 080401]
        is_chunk_visible = self.is_visible(glpane)
        
        if indicate_overlapping_atoms and is_chunk_visible:
            self.draw_overlap_indicators_if_needed()

        if self._chunk.hidden:
            # catch the case where indicate_overlapping_atoms skipped this test earlier
            return

        self._chunk.basepos # note: has side effects in __getattr__
            # make sure basepos is up-to-date, so basecenter is not changed
            # during the redraw. #e Ideally we'd have a way to detect or
            # prevent further changes to it during redraw, but this is not
            # needed for now since they should not be possible, and should
            # cause visible bugs if they happen. At least let's verify the
            # self._chunk coord system has not changed by the time we're done:
        should_not_change = ( + self._chunk.basecenter, + self._chunk.quat )

        ### WARNING: DUPLICATED CODE: much of the remaining code in this method
        # is very similar to ExternalBondSetDrawer.draw. Ideally the common
        # parts would be moved into our common superclass,
        # TransformedDisplayListsDrawer. [bruce 090211/090217 comment]

        #bruce 050804 (probably not needed at that time due to glpane code
        #  in changeapp) / 090212 (probably needed now):
        # call track_use to tell whatever is now drawing us
        # (presumably our arg, glpane, but we don't assume this right here)
        # how to find out when any of our display list contents next become
        # invalid, so it can know it needs to redraw us. [note: I didn't check
        # whether extra_displist invalidity is handled by this same code (guess:
        # no), or in some independent way using gl_update.]
        self.track_use()

        drawLevel = self._chunk.assy.drawLevel # this might recompute it
            # (if that happens and grabs the pref value, I think this won't
            #  subscribe our display list to it, since we're outside the
            #  begin/end for that, and that's good, since we include this in
            #  havelist instead, which avoids some unneeded redrawing, e.g. if
            #  pref changed and changed back while displaying a different Part.
            #  [bruce 060215])

        disp = self._chunk.get_dispdef(glpane)

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
            glPushName(self._chunk.glname)

            # put it in its place
            glPushMatrix()

            try: # do our glPopMatrix no matter what
                self._chunk.applyMatrix()
                
                ##delegate_selection_wireframe = False
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
                        ##delegate_selection_wireframe = chunk_only
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
                havelist_data = (disp, eltprefs, matprefs, drawLevel)
                    # note: havelist_data must be boolean true
                    #bruce 060215 adding drawLevel to havelist
                
                if self.havelist == havelist_data: 
                    # self.displist is still valid -- use it.
                    # Russ 081128: Switch from draw_dl() [now removed] to draw() with selection arg.
                    self.draw_csdl(self.displist, selected = self._chunk.picked)
                    for extra_displist in self.extra_displists.itervalues():
                        # [bruce 080604 new feature]
                        # note: similar code in else clause, differs re wantlist
                        extra_displist.draw_but_first_recompile_if_needed(
                            glpane,
                            selected = self._chunk.picked
                         )
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
                            #### REVIEW: is this a speedup (as intended) or a slowdown?
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
                        ColorSorter.start(self.displist, self._chunk.picked)

                    # bruce 041028 -- protect against exceptions while making display
                    # list, or OpenGL will be left in an unusable state (due to the lack
                    # of a matching glEndList) in which any subsequent glNewList is an
                    # invalid operation.
                    try:
                        self._draw_for_main_display_list(
                            glpane, disp,
                            (hd, delegate_draw_atoms, delegate_draw_chunk),
                            wantlist)
                    except:
                        msg = "exception in Chunk._draw_for_main_display_list ignored"
                        print_compact_traceback(msg + ": ")

                    if wantlist:
                        ColorSorter.finish(draw_now = True) ##### BUG: should draw separately, using self.draw_csdl. #####

                        self.end_tracking_usage( match_checking_code, self.invalidate_display_lists )
                        self.havelist = havelist_data
                        
                        # always set the self.havelist flag, even if exception happened,
                        # so it doesn't keep happening with every redraw of this Chunk.
                        #e (in future it might be safer to remake the display list to contain
                        # only a known-safe thing, like a bbox and an indicator of the bug.)

                    # draw the extra_displists (only needed if wantlist? not sure, so do always;
                    #  guess: there will be none of them unless wantlist is set, so it doesn't matter)
                    for extra_displist in self.extra_displists.itervalues():
                        extra_displist.draw_but_first_recompile_if_needed(
                            glpane,
                            selected = self._chunk.picked,
                            wantlist = wantlist
                         )
                        
                    pass # end of the case where "main display list (and extra lists) needs to be remade"

                # REVIEW: is it ok that self._chunk.glname is exposed for the following
                # _renderOverlayText drawing? Guess: yes, even though it means mouseover
                # of the text will cause a redraw, and access to chunk context menu.
                # If it turns out that that redraw also visually highlights the chunk,
                # we might reconsider, but even that might be ok.
                # [bruce 081211 comments]
                if ( self._chunk.chunkHasOverlayText and
                     self._chunk.showOverlayText ):
                    self._renderOverlayText(glpane)
                
                #@@ninad 070219 disabling the following--
                ## self._draw_selection_frame(glpane, delegate_selection_wireframe, hd)

                # piotr 080320
                if hd:
                    hd._f_drawchunk_realtime(glpane, self._chunk)

                if self._chunk.hotspot is not None: 
                    # note: accessing self._chunk.hotspot can have side effects in getattr
                    self.overdraw_hotspot(glpane, disp) 
                        # note: this only does anything for pastables
                        # (toplevel clipboard items) as of 050316

                # russ 080409 Array to string formatting is slow, avoid it
                # when not needed.  Use !=, not ==, to compare Numeric arrays.
                # (!= returns V(0,0,0), a False boolean value, when equal.)
                if (should_not_change[0] != self._chunk.basecenter or
                    should_not_change[1] != self._chunk.quat):
                    assert `should_not_change` == `( + self._chunk.basecenter, + self._chunk.quat )`, \
                           "%r != %r, what's up?" % (should_not_change,
                                                     ( + self._chunk.basecenter, + self._chunk.quat))

                pass # end of drawing within self's local coordinate frame

            except:
                print_compact_traceback("exception in Chunk.draw, continuing: ")

            glPopMatrix()

            glPopName() # pops self._chunk.glname

            pass # end of 'if is_chunk_visible:'

        self._draw_outside_local_coords(glpane, disp, drawLevel, is_chunk_visible)

        return # from Chunk.draw()

    def _renderOverlayText(self, glpane): # by EricM
        gotone = False
        for atom in self._chunk.atoms.itervalues():
            text = atom.overlayText
            if (text):
                gotone = True
                pos = atom.baseposn()
                radius = atom.drawing_radius() * 1.01
                pos = pos + glpane.out * radius
                glpane.renderTextAtPosition(pos, text)
        if (not gotone):
            self._chunk.chunkHasOverlayText = False

    def _draw_outside_local_coords(self, glpane, disp, drawLevel, is_chunk_visible):
        """
        Do the part of self.draw that goes outside self's
        local coordinate system and outside its display lists.

        [Subclasses can extend this if needed]
        """
        #bruce 080520 split this out; extended in class VirtualSiteChunkDrawer
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
        if draw_external_bonds and self._chunk.externs:
            self._draw_external_bonds(glpane, disp, drawLevel, is_chunk_visible)

        return # from Chunk._draw_outside_local_coords()

    def _draw_external_bonds(self, glpane, disp, drawLevel, is_chunk_visible = True):
        """
        Draw self's external bonds (if debug_prefs and frustum culling permit).

        @note: handles both cases of debug_pref for whether to use
               ExternalBondSets for drawing them.
        """
        if not _DRAW_EXTERNAL_BONDS:
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
           (self._chunk.assy.o.is_animating
                # review: test in self._chunk.assy.o or glpane?
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
        
        self._chunk._update_bonded_chunks()
        
        bondcolor = self._chunk.drawing_color()
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
        
        # update, bruce 090218: revised drawing_frame code below;
        # this fixes some but not all of the future problems mentioned above.

        drawing_frame = self.get_drawing_frame() # might be None, in theory
        
        repeated_bonds_dict = drawing_frame and drawing_frame.repeated_bonds_dict
            # might be None, if we're not being drawn between a pair
            # of calls to part.before/after_drawing_model
            # (which is deprecated but might still occur),
            # or if our chunk has no Part (a bug).
        
        if repeated_bonds_dict is None:
            # (Note: we can't just test "not repeated_bonds_dict",
            #  in case it's {}.)
            # This can happen when chunks are drawn in other ways than
            # via Part.draw (e.g. as Extrude repeat units?),
            # or [as revised 080314] due to bugs in which self._chunk.part
            # is None; we need a better fix for this, but for now,
            # just don't use the dict. As a kluge to avoid messing up
            # the loop below, just use a junk dict instead.
            # [bruce 070928 fix new bug 2548]
            repeated_bonds_dict = {} # kluge

        if debug_pref("GLPane: use ExternalBondSets for drawing?", #bruce 080707
                      Choice_boolean_True,
                          # changed to default True, bruce 090217,
                          # though not yet fully tested
                      non_debug = True,
                      prefs_key = "v1.2/use ExternalBondSets for drawing?" ):
            objects_to_draw = self._chunk._bonded_chunks.itervalues()
            use_outer_colorsorter = False
        else:
            objects_to_draw = self._chunk.externs
            use_outer_colorsorter = True
        
        # actually draw them

        if use_outer_colorsorter:
            # note: not used with ExternalBondSets
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
            ColorSorter.finish(draw_now = True)
        
        return # from _draw_external_bonds

##    def _draw_selection_frame(self, glpane, delegate_selection_wireframe, hd):
##        "[private submethod of self.draw]"
##        chunk = self._chunk
##        if chunk.picked:
##            if not delegate_selection_wireframe:
##                try:
##                    drawlinelist(PickedColor, chunk.polyhedron or [])
##                except:
##                    # bruce 041119 debug code;
##                    # also "or []" failsafe (above)
##                    # in case recompute exception makes it None
##                    print_compact_traceback("exception in drawlinelist: ")
##                    print "(chunk.polyhedron is %r)" % chunk.polyhedron
##            else:
##                hd._f_drawchunk_selection_frame(glpane, chunk, PickedColor, highlighted = False)
##            pass
##        return

    def get_drawing_frame(self): #bruce 090218
        """
        Return the current drawing_frame if we have one, or None.

        @see: class Part_drawing_frame
        """
        # note: accessing part.drawing_frame allocates it on demand
        # if it wasn't already allocated during that call of Part.draw.
        return self._chunk.part and self._chunk.part.drawing_frame
    
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
        model_draw_frame = self.get_drawing_frame()
        if not model_draw_frame:
            return
        neighborhoodGenerator = model_draw_frame._f_state_for_indicate_overlapping_atoms
        if not neighborhoodGenerator:
            # precaution after refactoring, probably can't happen [bruce 090218]
            return
        for atom in self._chunk.atoms.itervalues():
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

            ### REVIEW: can/should we optim this by doing it during __init__?
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
            hd._f_drawchunk(self.glpane, self._chunk)
        else:
            self._standard_draw_chunk(glpane, disp0)

        # draw the individual atoms and internal bonds (if desired)
        if delegate_draw_atoms:
            pass # nothing for this is implemented, or yet needed [as of bruce 060608]
        else:
            self._standard_draw_atoms(glpane, disp0)
        return

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
        if not self.is_visible(glpane): #bruce 090212 revised slightly
            return

        # Russ 081212: Switch from glCallList to CSDL.draw for shader prims.
        ##### TODO: use self.draw_csdl.
        if self._has_displist():
            apply_material(color) ### REVIEW: still needed?
            self._chunk.pushMatrix()
            for csdl in ([self.displist] +
                         [ed.csdl for ed in self.extra_displists.values()]):
                csdl.draw(highlighted = True, highlight_color = color)
            self._chunk.popMatrix()
            pass

        # piotr 080521: Get display mode for drawing external bonds and/or
        # the "realtime" objects.
        disp = self._chunk.get_dispdef(glpane)

        #russ 080302: Draw external bonds.
        ##### TODO: use ExternalBondSets.
        if self._chunk.externs:
            # From Chunk.draw():
            drawLevel = self._chunk.assy.drawLevel
            # From Chunk._draw_external_bonds:
            # todo [bruce 090114 comment]: optimize this to not draw them twice
            # (as was done in older code). (Note that there will soon be
            # objects containing display lists for them, and our job will
            # be to not draw *those objects* twice, in any one frame.)
            ColorSorter.start(None)
            for bond in self._chunk.externs:
                bond.draw(glpane, disp, color, drawLevel)
                continue
            ColorSorter.finish(draw_now = True)
            pass
        pass

        # piotr 080521
        # Highlight "realtime" objects (e.g. 2D DNA cylinder style).
        hd = get_display_mode_handler(disp)
        if hd:
            hd._f_drawchunk_realtime(glpane, self._chunk, highlighted = True)
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

    def _standard_draw_atoms(self, glpane, disp0): 
        """
        [private submethod of self.draw:]
        
        Draw all our atoms and all their internal bonds, in the standard way,
        *including* atom selection wireframes, as if self's display mode was disp0;
        this occurs inside our local coordinate system and display-list-making;
        it doesn't occur if atom drawing is delegated to our display mode.
        """
        #bruce 060608 split this out of _draw_for_main_display_list
        drawLevel = self._chunk.assy.drawLevel
        drawn = {}
        # bruce 041014 hack for extrude -- use _colorfunc if present
        # [part 1; optimized 050513]
        _colorfunc = self._chunk._colorfunc # might be None 
            # [as of 050524 we supply a default so it's always there]
        _dispfunc = self._chunk._dispfunc
            #bruce 060411 hack for BorrowerChunk, might be more generally useful someday

        atomcolor = self._chunk.drawing_color() # None or a color
            # bruce 080210 bugfix (predicted) [part 1 of 2]:
            # use this even when _colorfunc is being used
            # (so chunk colors work in Extrude; IIRC there was a bug report on that)
            # [UNTESTED whether that bug exists and whether this fixes it]

        bondcolor = atomcolor # never changed below

        for atom in self._chunk.atoms.itervalues(): 
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
                # self.color in Atom.draw (but not in Bond.draw -- good??)

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
                            if bond.atom1.molecule is not self._chunk or \
                               bond.atom2.molecule is not self._chunk:
                                # external bond (todo: could simplify the test)
                                pass
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
        #### REVIEW: ok if this remains outside any CSDL?
        """
        If self._chunk is a (toplevel) clipboard item with a hotspot
        (i.e. if pasting it onto a bondpoint will work and use its hotspot),
        draw its hotspot in a special manner.

        @note: As with selatom, we do this outside of the display list.        
        """
        if self._should_draw_hotspot(glpane):
            hs = self._chunk.hotspot
            try:
                color = env.prefs[bondpointHotspotColor_prefs_key] #bruce 050808

                level = self._chunk.assy.drawLevel #e or always use best level??
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
        Determine whether self has a valid hotspot and
        wants to draw it specially.
        """
        # bruce 050416 warning: the conditions here need to match those in depositMode's
        # methods for mentioning hotspot in statusbar, and for deciding whether a clipboard
        # item is pastable. All this duplicated hardcoded conditioning is bad; needs cleanup. #e
        
        # We need these checks because some code removes singlets from a chunk (by move or kill)
        # without checking whether they are that chunk's hotspot.

        # review/cleanup: some of these checks might be redundant with checks
        # in the get method run by accessing self._chunk.hotspot.
            
        hs = self._chunk.hotspot ### todo: move lower, after initial tests

        wanted = (self in self._chunk.assy.shelf.members) or glpane.always_draw_hotspot
            #bruce 060627 added always_draw_hotspot re bug 2028
        if not wanted:
            return False

        if hs is None:
            return False
        if not hs.is_singlet():
            return False
        if not hs.key in self._chunk.atoms:
            return False
        return True

    pass # end of class ChunkDrawer

# end
