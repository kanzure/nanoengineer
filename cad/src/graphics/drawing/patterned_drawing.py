# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
patterned_drawing.py - special effects for highlighted/selected drawing styles

@author: Russ
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

Russ 080523 wrote this [in chunk.py?]

Russ 080530 refactored to move the patterned drawing style setup here
[in gl_lighting.py?] from chunk.py, and generalized the prefs decoding
to handle selection as well as hover highlighting.

Bruce 090304 moved it into its own file to avoid a likely future import cycle
(when it's supported in shaders), and since it doesn't belong in gl_lighting.py.
"""

from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINE
from OpenGL.GL import glLineWidth
from OpenGL.GL import GL_FILL
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_BACK
from OpenGL.GL import glPolygonMode
from OpenGL.GL import glPolygonOffset
from OpenGL.GL import GL_POLYGON_OFFSET_LINE
from OpenGL.GL import GL_POLYGON_STIPPLE
from OpenGL.GL import glPolygonStipple

import numpy

import foundation.env as env

from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import HHS_SOLID, HHS_SCREENDOOR1
from utilities.prefs_constants import HHS_CROSSHATCH1, HHS_BW_PATTERN
from utilities.prefs_constants import HHS_POLYGON_EDGES, HHS_HALO
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import SS_SOLID, SS_SCREENDOOR1, SS_CROSSHATCH1
from utilities.prefs_constants import SS_BW_PATTERN, SS_POLYGON_EDGES, SS_HALO
from utilities.prefs_constants import haloWidth_prefs_key

# ==

# 32x32 stipple bitmask patterns, in C arrays.
# To avoid "seams", repeated subpattern sizes must be a power of 2.
# _ScreenDoor - 2x2 repeat, 1/4 density (one corner turned on.)
_ScreenDoor = numpy.array(16*(4*[0xaa] + 4*[0x00]), dtype = numpy.uint8)
# _CrossHatch - 4x4 repeat, 7/16 density (two edges of a square turned on.)
_CrossHatch = numpy.array(8*(4*[0xff] + 12*[0x11]), dtype = numpy.uint8)

# ==

def _decodePatternPrefs(highlight = False, select = False):
    """
    Internal common code for startPatternedDrawing and endPatternedDrawing.
    Returns a tuple of prefs data.
    """
    key = (highlight and hoverHighlightingColorStyle_prefs_key
           or select and selectionColorStyle_prefs_key) # False or string.
    style = bool(key) and env.prefs[key] # False or enum string.
    solid = style == False or (highlight and style == HHS_SOLID or
                               select and style == SS_SOLID) # bool.
    pattern = None          # None or a bitarray pointer.
    edges = halos = False   # bool.

    # Nothing to do for solid colors.
    if not solid:
        # Check for stipple-patterned drawing styles.
        if (highlight and style == HHS_SCREENDOOR1
            or select and style == SS_SCREENDOOR1):
            pattern = _ScreenDoor
            pass
        elif (highlight and style == HHS_CROSSHATCH1
              or select and style == SS_CROSSHATCH1):
            pattern = _CrossHatch
            pass
        # Check for polygon-edge drawing styles.
        if pattern is None:
            edges = (highlight and style == HHS_POLYGON_EDGES
                     or select and style == SS_POLYGON_EDGES)
            halos = (highlight and style == HHS_HALO
                     or select and style == SS_HALO)
            pass
        pass

    return (key, style, solid, pattern, edges, halos)

def isPatternedDrawing(highlight = False, select = False):
    """
    Return True if either highlight or select is passed as True, and the
    corresponding preference is set to select a patterned (non-solid) drawing
    style.
    """
    (key, style, solid, pattern, edges, halos) = \
          _decodePatternPrefs(highlight, select)
    return not solid

def startPatternedDrawing(highlight = False, select = False):
    """
    Start drawing with a patterned style, if either highlight or select is
    passed as True, and the corresponding preference is set to select a
    patterned drawing style.

    This is common code for two different prefs keys, each of which has its own
    set of settings constants...

    Return value is True if one of the patterned styles is selected.
    """
    (key, style, solid, pattern, edges, halos) = \
          _decodePatternPrefs(highlight, select)
        
    if solid:
        # Nothing to do here for solid colors.
        return False

    # Set up stipple-patterned drawing styles.
    if pattern is not None:
        glEnable(GL_POLYGON_STIPPLE)
        glPolygonStipple(pattern)
        return True

    # Both polygon edges and halos are drawn in line-mode.
    if edges or halos:
        glPolygonMode(GL_FRONT, GL_LINE)
        glPolygonMode(GL_BACK, GL_LINE)

        if halos:
            # Draw wide, unshaded lines, offset a little bit away from the
            # viewer so that only the silhouette edges are visible.
            glDisable(GL_LIGHTING)
            glLineWidth(env.prefs[haloWidth_prefs_key])
            glEnable(GL_POLYGON_OFFSET_LINE)
            glPolygonOffset(0.0, 5.e4) # Constant offset.
            pass

        pass
    return True

def endPatternedDrawing(highlight = False, select = False):
    """
    End drawing with a patterned style, if either highlight or select is
    passed as True, and the corresponding preference is set to select a
    patterned drawing style.

    This is common code for two different prefs keys, each of which has its own
    set of settings constants...

    Return value is True if one of the patterned styles is selected.
    """
    (key, style, solid, pattern, edges, halos) = \
          _decodePatternPrefs(highlight, select)
        
    if solid:
        # Nothing to do here for solid colors.
        return False

    # End stipple-patterned drawing styles.
    if pattern is not None:
        glDisable(GL_POLYGON_STIPPLE)
        return True

    # End line-mode for polygon-edges or halos styles.
    if edges or halos:
        glPolygonMode(GL_FRONT, GL_FILL)
        glPolygonMode(GL_BACK, GL_FILL)

        if halos:
            # Back to normal lighting and treatment of lines and polygons.
            glEnable(GL_LIGHTING)
            glLineWidth(1.0)
            glDisable(GL_POLYGON_OFFSET_LINE)
            glPolygonOffset(0.0, 0.0)
            pass

        pass
    return True

# end
