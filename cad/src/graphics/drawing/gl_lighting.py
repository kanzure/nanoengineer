# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
gl_lighting.py - Lights, materials, and special effects.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

Originated by Josh as drawer.py .

Various developers extended it since then.

Brad G. added ColorSorter features.

At some point Bruce partly cleaned up the use of display lists.

071030 bruce split some functions and globals into draw_grid_lines.py
and removed some obsolete functions.

080210 russ: Split the single display-list into two second-level lists (with and
without color) and a set of per-color sublists so selection and hover-highlight
can over-ride Chunk base colors.  ColorSortedDisplayList is now a class in the
parent's displist attr to keep track of all that stuff.

080311 piotr Added a "drawpolycone_multicolor" function for drawing polycone
tubes with per-vertex colors (necessary for DNA display style)

080313 russ: Added triangle-strip icosa-sphere constructor,"getSphereTriStrips".

080420 piotr Solved highlighting and selection problems for multi-colored
objects (e.g. rainbow colored DNA structures).

080519 russ: pulled the globals into a drawing_globals module and broke
drawer.py into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py CS_ShapeList.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py

080530 russ: Refactored to move the patterned drawing style setup here from
chunk.py, and generalized the prefs decoding to handle selection as well as
hover highlighting.
"""

from OpenGL.GL import GL_AMBIENT
from OpenGL.GL import GL_AMBIENT_AND_DIFFUSE
from OpenGL.GL import glAreTexturesResident
from OpenGL.GL import GL_BACK
from OpenGL.GL import glBegin
from OpenGL.GL import glBindTexture
from OpenGL.GL import glColor4fv
from OpenGL.GL import GL_CONSTANT_ATTENUATION
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import GL_DIFFUSE
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glEnd
from OpenGL.GL import GL_EXTENSIONS
from OpenGL.GL import glFinish
from OpenGL.GL import GL_FOG
from OpenGL.GL import GL_FOG_COLOR
from OpenGL.GL import GL_FOG_END
from OpenGL.GL import GL_FOG_MODE
from OpenGL.GL import GL_FOG_START
from OpenGL.GL import GL_FILL
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_FRONT_AND_BACK
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGetString
from OpenGL.GL import GL_LIGHT0
from OpenGL.GL import GL_LIGHT1
from OpenGL.GL import GL_LIGHT2
from OpenGL.GL import glLightf
from OpenGL.GL import glLightfv
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINE
from OpenGL.GL import glLineWidth
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glMaterialf
from OpenGL.GL import glMaterialfv
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glPolygonMode
from OpenGL.GL import glPolygonOffset
from OpenGL.GL import GL_POLYGON_OFFSET_LINE
from OpenGL.GL import GL_POLYGON_STIPPLE
from OpenGL.GL import glPolygonStipple
from OpenGL.GL import GL_POSITION
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_RENDERER
from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_SHININESS
from OpenGL.GL import GL_SPECULAR
from OpenGL.GL import glTexCoord2f
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import GL_VENDOR
from OpenGL.GL import GL_VERSION
from OpenGL.GL import glVertex2f

from OpenGL.GLU import gluBuild2DMipmaps

from utilities.constants import white
import utilities.debug as debug # for debug.print_compact_traceback

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

import graphics.drawing.drawing_globals as drawing_globals

try:
    from OpenGL.GL import glFog
    from OpenGL.GL import glFogv # piotr 080515
except:
    # The installed version of OpenGL requires argument-typed glFog calls.
    from OpenGL.GL import glFogf as glFog	
    from OpenGL.GL import glFogfv as glFogv

# ==

# Helper functions for use by GL widgets wanting to set up lighting.

#bruce 051212 made these from the code in GLPane which now calls them, so they
#can also be used in ThumbView

# Default lights tuples (format is as used by setup_standard_lights; perhaps
# also assumed by other code).
#grantham 20051121 comment - Light should probably be a class.  Right now,
# changing the behavior of lights requires changing a bunch of
# ambiguous tuples and tuple packing/unpacking.
#bruce 051212 moved this here from GLPane; maybe it belongs in prefs_constants
# instead?
# Note: I'm not sure whether this is the only place where this data is coded.
_default_lights = ((white, 0.1, 0.5, 0.5, -50, 70, 30, True),
                   (white, 0.1, 0.5, 0.5, -20, 20, 20, True),
                   (white, 0.1, 0.1, 0.1, 0, 0, 100, False))
        # for each of 3 lights, this stores ((r,g,b),a,d,s,x,y,z,e)
        # revised format to include s,x,y,z.  Mark 051202.
        # revised format to include c (r,g,b). Mark 051204.
        # Be sure to keep the lightColor prefs keys and _lights colors
        # synchronized.
        # Mark 051204. [a comment from when this was located in GLPane]

def glprefs_data_used_by_setup_standard_lights( glprefs = None): #bruce 051212
    """
    Return a summary of the glprefs data used by setup_standard_lights, for use
    in later deciding whether it needs to be called again due to changes in
    glprefs.
    """
    if glprefs is None:
        glprefs = drawing_globals.glprefs
        pass
    # This must be kept in sync with what's used by setup_standard_lights() .
    return (glprefs.override_light_specular,)

def setup_standard_lights( lights, glprefs = None):
    """
    Set up lighting in the current GL context using the supplied "lights" tuple
    (in the format used by GLPane's prefs) and the optional glprefs object
    (which defaults to drawing_globals.glprefs ).

       Note: the glprefs data used can be summarized by the related function
       glprefs_data_used_by_setup_standard_lights (which see).

       Warning: has side effects on GL_MODELVIEW matrix.

       Note: If GL_NORMALIZE needs to be enabled, callers should do that
       themselves, since this depends on what they will draw and might slow down
       drawing.
    """
    #e not sure whether projection matrix also needs to be reset here
    # [bruce 051212]
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if glprefs is None:
        glprefs = drawing_globals.glprefs
        # note: whatever glprefs data is used below must also be present
        # in the return value of glprefs_data_used_by_setup_standard_lights().
        # [bruce 051212]

    try:
        # new code
        (((r0,g0,b0),a0,d0,s0,x0,y0,z0,e0), \
         ( (r1,g1,b1),a1,d1,s1,x1,y1,z1,e1), \
         ( (r2,g2,b2),a2,d2,s2,x2,y2,z2,e2)) = lights

        # Great place for a print statement for debugging lights.  Keep this.
        # Mark 051204. [revised by bruce 051212]
        #print "-------------------------------------------------------------"
        #print "setup_standard_lights: lights[0]=", lights[0]
        #print "setup_standard_lights: lights[1]=", lights[1]
        #print "setup_standard_lights: lights[2]=", lights[2]

        glLightfv(GL_LIGHT0, GL_POSITION, (x0, y0, z0, 0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (r0*a0, g0*a0, b0*a0, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (r0*d0, g0*d0, b0*d0, 1.0))
        if glprefs.override_light_specular is not None:
            glLightfv(GL_LIGHT0, GL_SPECULAR, glprefs.override_light_specular)
        else:
            # grantham 20051121 - this should be a component on its own
            # not replicating the diffuse color.
            # Added specular (s0) as its own component.  mark 051202.
            glLightfv(GL_LIGHT0, GL_SPECULAR, (r0*s0, g0*s0, b0*s0, 1.0))
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)

        glLightfv(GL_LIGHT1, GL_POSITION, (x1, y1, z1, 0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (r1*a1, g1*a1, b1*a1, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (r1*d1, g1*d1, b1*d1, 1.0))
        if glprefs.override_light_specular is not None:
            glLightfv(GL_LIGHT1, GL_SPECULAR, glprefs.override_light_specular)
        else:
            glLightfv(GL_LIGHT1, GL_SPECULAR, (r1*s1, g1*s1, b1*s1, 1.0))
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)

        glLightfv(GL_LIGHT2, GL_POSITION, (x2, y2, z2, 0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (r2*a2, g2*a2, b2*a2, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (r2*d2, g2*d2, b2*d2, 1.0))
        if glprefs.override_light_specular is not None:
            glLightfv(GL_LIGHT2, GL_SPECULAR, glprefs.override_light_specular)
        else:
            glLightfv(GL_LIGHT2, GL_SPECULAR, (r2*s2, g2*s2, b2*s2, 1.0))
        glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)

        glEnable(GL_LIGHTING)

        if e0:
            glEnable(GL_LIGHT0)
        else:
            glDisable(GL_LIGHT0)

        if e1:
            glEnable(GL_LIGHT1)
        else:
            glDisable(GL_LIGHT1)

        if e2:
            glEnable(GL_LIGHT2)
        else:
            glDisable(GL_LIGHT2)
    except:
        debug.print_compact_traceback(
            "bug (worked around): setup_standard_lights reverting to old code.")
        # old code, used only to set up some sort of workable lighting in case
        # of bugs (this is not necessarily using the same values as
        # _default_lights; doesn't matter since never used unless there are
        # bugs)
        glLightfv(GL_LIGHT0, GL_POSITION, (-50, 70, 30, 0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)

        glLightfv(GL_LIGHT1, GL_POSITION, (-20, 20, 20, 0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.4, 0.4, 0.4, 1.0))
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)

        glLightfv(GL_LIGHT2, GL_POSITION, (0, 0, 100, 0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)

        glEnable(GL_LIGHTING)

        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glDisable(GL_LIGHT2)
    return # from setup_standard_lights

# ==

def setup_fog(fog_start, fog_end, fog_color):

    glFog(GL_FOG_MODE, GL_LINEAR)
    glFog(GL_FOG_START, fog_start)
    glFog(GL_FOG_END, fog_end)
    if len(fog_color) == 3:
        fog_color = (fog_color[0], fog_color[1], fog_color[2], 1.0)
    glFogv(GL_FOG_COLOR, fog_color) # piotr 080515

def enable_fog():
    glEnable(GL_FOG)

def disable_fog():
    glDisable(GL_FOG)

# ==

# grantham 20051121, renamed 20051201; revised by bruce 051126, 051203 (added
# specular_brightness), 051215
def apply_material(color):
    """
    Set OpenGL material parameters based on the given color (length 3 or 4) and
    the material-related prefs values in drawing_globals.glprefs.
    """

    #bruce 051215: make sure color is a tuple, and has length exactly 4, for all
    # uses inside this function, assuming callers pass sequences of length 3 or
    # 4. Needed because glMaterial requires four-component vector and PyOpenGL
    # doesn't check. [If this is useful elsewhere, we can split it into a
    # separate function.]
    color = tuple(color)
    if len(color) == 3:
        color = color + (1.0,) # usual case
    elif len(color) != 4:
        # should never happen; if it does, this assert will always fail
        assert len(color) in [3,4], \
               "color tuples must have length 3 or 4, unlike %r" % (color,)

    glColor4fv(color)          # For drawing lines with lighting disabled.

    if not drawing_globals.glprefs.enable_specular_highlights:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)
        # glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0,0,0,1))
        return

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)

    whiteness = drawing_globals.glprefs.specular_whiteness
    brightness = drawing_globals.glprefs.specular_brightness
    if whiteness == 1.0:
        specular = (1.0, 1.0, 1.0, 1.0) # optimization
    else:
        if whiteness == 0.0:
            specular = color # optimization
        else:
            # assume color[3] (alpha) is not passed or is always 1.0
            c1 = 1.0 - whiteness
            specular = ( c1 * color[0] + whiteness,
                         c1 * color[1] + whiteness,
                         c1 * color[2] + whiteness, 1.0 )
    if brightness != 1.0:
        specular = ( specular[0] * brightness,
                     specular[1] * brightness,
                     specular[2] * brightness, 1.0 )
            #e Could optimize by merging this with above 3 cases (or, of course,
            #  by doing it in C, which we'll do eventually.)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)

    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS,
                drawing_globals.glprefs.specular_shininess)
    return

# ==

#russ 080515: We should find a better place for this!
def get_gl_info_string(glpane): # grantham 20051129
    """
    Return a string containing some useful information about the OpenGL
    implementation.

    Use the GL context from the given QGLWidget glpane (by calling
    glpane.makeCurrent()).
    """

    glpane.makeCurrent() #bruce 070308 added glpane arg and makeCurrent call

    gl_info_string = ''

    gl_info_string += 'GL_VENDOR : "%s"\n' % glGetString(GL_VENDOR)
    gl_info_string += 'GL_VERSION : "%s"\n' % glGetString(GL_VERSION)
    gl_info_string += 'GL_RENDERER : "%s"\n' % glGetString(GL_RENDERER)
    gl_extensions = glGetString(GL_EXTENSIONS)
    gl_extensions = gl_extensions.strip()
    gl_extensions = gl_extensions.replace(" ", "\n* ")
    gl_info_string += 'GL_EXTENSIONS : \n* %s\n' % gl_extensions

    from utilities.debug_prefs import debug_pref, Choice_boolean_False
    if debug_pref("get_gl_info_string call glAreTexturesResident?",
                  Choice_boolean_False):
        # Give a practical indication of how much video memory is available.
        # Should also do this with VBOs.

        # I'm pretty sure this code is right, but PyOpenGL seg faults in
        # glAreTexturesResident, so it's disabled until I can figure that
        # out. [grantham] [bruce 070308 added the debug_pref]

        all_tex_in = True
        tex_bytes = '\0' * (512 * 512 * 4)
        tex_names = []
        tex_count = 0
        tex_names = glGenTextures(1024)
        glEnable(GL_TEXTURE_2D)
        while all_tex_in:
            glBindTexture(GL_TEXTURE_2D, tex_names[tex_count])
            gluBuild2DMipmaps(GL_TEXTURE_2D, 4, 512, 512, GL_RGBA,
                              GL_UNSIGNED_BYTE, tex_bytes)
            tex_count += 1

            glTexCoord2f(0.0, 0.0)
            glBegin(GL_QUADS)
            glVertex2f(0.0, 0.0)
            glVertex2f(1.0, 0.0)
            glVertex2f(1.0, 1.0)
            glVertex2f(0.0, 1.0)
            glEnd()
            glFinish()

            residences = glAreTexturesResident(tex_names[:tex_count])
            all_tex_in = reduce(lambda a,b: a and b, residences)
                # bruce 070308 sees this exception from this line:
                # TypeError: reduce() arg 2 must support iteration

        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(tex_names)

        gl_info_string += "Could create %d 512x512 RGBA resident textures\n" \
                          % tex_count
    return gl_info_string

# ==
# russ 080523: Special effects for highlighting and selection drawing styles.

# 32x32 stipple bitmask patterns, in C arrays.
# To avoid "seams", repeated subpattern sizes must be a power of 2.
# ScreenDoor - 2x2 repeat, 1/4 density (one corner turned on.)
ScreenDoor = numpy.array(16*(4*[0xaa] + 4*[0x00]), dtype = numpy.uint8)
# CrossHatch - 4x4 repeat, 7/16 density (two edges of a square turned on.)
CrossHatch = numpy.array(8*(4*[0xff] + 12*[0x11]), dtype = numpy.uint8)

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
            pattern = ScreenDoor
            pass
        elif (highlight and style == HHS_CROSSHATCH1
              or select and style == SS_CROSSHATCH1):
            pattern = CrossHatch
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
