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

TODO: unify similar code in three places: here, ChunkDrawer, ExtraDisplist. ####
"""

from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList # not yet used?

# ==

class TransformedDisplayListsDrawer(object): # refile when done and name is stable
    """
    Superclass for drawing classes which make use of one or more display lists
    (actually CSDLs) to be drawn relative to a transform known to the specific
    subclass, and to be invalidated at appropriate times (with help from the
    subclass).
    
    (The specific subclass knows where to get the transform,
     and when to invalidate the display lists beyond when usage tracking
     does so.)
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

        
####### WARNING: DUPLICATED CODE: following is grabbed from ChunkDrawer.draw,
# then generalized; chunk comments left in so it's easy to see what was grabbed.
# When this class is ready, Chunk itself should be modified to use it.
        
        
# [dup code removed for now]


###### DUPLICATED CODE ends here [090211 comment, code was copied earlier]

                        ####### more, at various indent levels?
                        ####### todo: if this survives, split interior into separate methods to clarify.

##                        pass
##                    pass
##                pass
##            except:
##                xxx
##            pass
        return # from draw
    pass # end of class

# end
