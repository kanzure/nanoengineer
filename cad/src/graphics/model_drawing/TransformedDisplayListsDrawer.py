# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
TransformedDisplayListsDrawer.py - abstract class for something that draws
using display lists which it caches under a local coordinate system.

Note: as of 090203 this is mostly a scratch file. #####

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

"""

from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList # not yet used?

# ==

class TransformedDisplayListsDrawer(object): # refile when done and name is stable
    """
    Superclass for drawing classes which make use of one or more display lists
    (actually CSDLs) to be drawn relative to a transform known to the drawing class.
    
    (The specific subclass knows where to get the transform,
     and when to invalidate the display lists.)
    """
    if 0: # just to not execute this until it's ready
        # we'll need these attrs, or revised code:
        assy # for drawLevel
        glname # if there is a "whole-chunk" one for all our primitives
        track_use # method from superclass
        get_dispdef # method in subclass -- not in the API?? maybe it is if it's "get cache key and style args" ####
        1 or is_chunk_visible # ???
        applyMatrix
        # not get_display_mode_handler, delegate_*, hd, chunk_only --
        # that is handled outside by choosing the right rule (this class)
    
    def draw(self, glpane, dispdef):

        
        assert 0 #### note: never yet called as of before 090211 (not even when debug_prefs are set)

        
####### WARNING: DUPLICATED CODE: following is grabbed from Chunk_drawing_methods.draw,
# then generalized; chunk comments left in so it's easy to see what was grabbed.
# When this class is ready, Chunk itself should be modified to use it.
        
        
        #bruce 050804:
        # tell whatever is now drawing our display list
        # (presumably our arg, glpane, but we don't assume this right here)
        # how to find out when our display list next becomes invalid,
        # so it can know it needs to redraw us.
        # (This is probably not actually needed at the moment, 
        # due to a special system used by self.changeapp() in place of
        # self.track_change(), but it should be harmless.)

        ### TODO: make this specific to each display list, if we cache several,
        # in case their invalidation requirements differ.
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

        if 1 or is_chunk_visible: #####
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


###### DUPLICATED CODE ends here [090211 comment, code was copied earlier]

                        ####### more, at various indent levels?
                        ####### todo: if this survives, split interior into separate methods to clarify.

                        pass
                    pass
                pass
            except:
                xxx
            pass
        return # from draw
    pass # end of class

# end
