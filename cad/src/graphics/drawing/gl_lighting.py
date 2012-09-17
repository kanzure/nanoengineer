# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
gl_lighting.py - Lights, materials, and special effects (fog).

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Originated by Josh in drawer.py .

Various developers extended it since then.

Brad G. added ColorSorter features and probably apply_material.

080519 russ: pulled the globals into a drawing_globals module and broke
drawer.py into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py c_renderer.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py
"""

from OpenGL.GL import GL_AMBIENT
from OpenGL.GL import GL_AMBIENT_AND_DIFFUSE
from OpenGL.GL import glColor4fv
from OpenGL.GL import GL_CONSTANT_ATTENUATION
from OpenGL.GL import GL_DIFFUSE
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_FOG
from OpenGL.GL import GL_FOG_COLOR
from OpenGL.GL import GL_FOG_END
from OpenGL.GL import GL_FOG_MODE
from OpenGL.GL import GL_FOG_START
from OpenGL.GL import GL_FRONT_AND_BACK
from OpenGL.GL import GL_LIGHT0
from OpenGL.GL import GL_LIGHT1
from OpenGL.GL import GL_LIGHT2
from OpenGL.GL import glLightf
from OpenGL.GL import glLightfv
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glMaterialf
from OpenGL.GL import glMaterialfv
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_POSITION
from OpenGL.GL import GL_SHININESS
from OpenGL.GL import GL_SPECULAR

try:
    from OpenGL.GL import glFog
    from OpenGL.GL import glFogv # piotr 080515
except:
    # The installed version of OpenGL requires argument-typed glFog calls.
    from OpenGL.GL import glFogf as glFog	
    from OpenGL.GL import glFogfv as glFogv
    pass

from utilities.constants import white

from utilities.debug import print_compact_traceback

import graphics.drawing.drawing_globals as drawing_globals # only for glprefs in apply_material

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

def glprefs_data_used_by_setup_standard_lights( glprefs): #bruce 051212
    """
    Return a summary of the glprefs data used by setup_standard_lights
    (when that was passed the same glprefs argument).
    """
    # This must be kept in sync with what's used by setup_standard_lights() .
    return (glprefs.override_light_specular,)

def setup_standard_lights( lights, glprefs):
    """
    Set up lighting in the current GL context using the supplied "lights" tuple
    (in the format used by GLPane's prefs) and the required glprefs object
    (of class GLPrefs).

    @note: the glprefs data used can be summarized by the related function
        glprefs_data_used_by_setup_standard_lights (which see).

    @warning: has side effects on GL_MODELVIEW matrix.

    @note: If GL_NORMALIZE needs to be enabled, callers should do that
        themselves, since this depends on what they will draw and might
        slow down drawing.
    """

    assert glprefs is not None

    # note: whatever glprefs data is used below must also be present
    # in the return value of glprefs_data_used_by_setup_standard_lights().
    # [bruce 051212]

    #e not sure whether projection matrix also needs to be reset here
    # [bruce 051212]
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

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
        print_compact_traceback(
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
# specular_brightness), 051215, 090304 (added optional glprefs arg)

### REVIEW: should apply_material be a method of GLPrefs and perhaps GLPane?
# Or at least, should its glprefs arg be required (removing the last use of
# drawing_globals in this module)? [And in the meantime, moved to that module?]
#
# Probably yes, but making all uses know glprefs requires passing glpane or glprefs
# args or attrs into quite a few functions or methods or instances that don't
# have them yet, including at least CSDL, which ought to have a glprefs or glpane
# attr for use in .draw (as well as a GL resource context attr for other reasons),
# and the bond drawing code. So I don't quite have time to do it now. But it would
# be a good refactoring to do, for itself and to help refactor other things, and
# not too hard to do when someone has time. [bruce 090304 comment]

def apply_material(color, glprefs = None):
    # todo: move into glprefs.py (see comment above for why)
    """
    In the current GL context,
    set material parameters based on the given color (length 3 or 4) and
    the material-related prefs values in glprefs (which defaults to
    drawing_globals.glprefs).
    """
    if glprefs is None:
        glprefs = drawing_globals.glprefs
        pass

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

    if not glprefs.enable_specular_highlights:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)
        # glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0,0,0,1))
        return

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)

    whiteness = glprefs.specular_whiteness
    brightness = glprefs.specular_brightness
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
                glprefs.specular_shininess)
    return

# end
