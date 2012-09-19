# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
drawing_globals.py - A module containing global state within the
graphics.drawing suite (which is, in principle, mostly specific to
one "GL resource context" (display list namespace, etc)). For historical
reasons, a lot of its state is assigned from outside, and some of it
is not in principle specific to a resource context but is either a
constant or ought to be part of an argument passed to drawing routines.

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

WARNINGS:

Variables can be (and are) dynamically added to this module at runtime.
Note: Setting globals here should not be (but, unfortunately, is presently)
done as a side effect of loading other modules. It makes the imports of those
modules falsely appear unnecessary, since nothing defined in them is used.
It also confuses tools which import the module in which the assignment is
used, but not the one which makes the assignment.

Some of the variables contained here are mode control for the whole drawing
package, including the ColorSorter suite.  Other parts are communication between
the phases of setup and operations, which is only incidentally about OpenGL.
Other things are just geometric constants useful for setting up display lists,
e.g. a list of vertices of a diamond grid.

Usage:

Import it this way to show that it is a module:

  import graphics.drawing.drawing_globals as drawing_globals

Access variables as drawing_globals.varname .

TODO:

Desireable refactoring: Note that most of this state really belongs
in an object that corresponds to each "GL display list namespace"
aka "GL resource context",
i.e. each OpenGL shared resource pool of display lists, textures,
shaders, VBOs, etc.

In current code, we require all OpenGL drawing
contexts to share that state, so we can get away with keeping it
as globals in a module. Even so, this ought to be refactored, since
this way it makes the code less clear, causes import cycles and
dependencies on import order, confuses pylint, etc.

(Bruce 090303 is doing related cleanup by introducing ShaderGlobals
and moving shader prefs into GLPrefs, but the fundamental change
is still needed.)
"""

from graphics.drawing.glprefs import GLPrefs

# more imports are kept below, since they will be refactored into a separate module

# ==

# A singleton instance of the GLPrefs class.
# This is used in only these ways:
# - by old code (perhaps all being refactored away circa 090304)
# - to initialize glpane.glprefs when there is no other source.
# It must be initialized during import of this module,
# or some code would risk importing a value for it from before
# it was initialized.
# If this causes an import cycle, it can be moved to another module,
# since it's not otherwise used in this module.

# [review: rename it to avoid confusion, once all old uses are removed?]

glprefs = GLPrefs()

# =====

# these are assigned by external code (incomplete list;
# defined here to partly mollify pylint; not yet classified
# into how to distribute them after refactoring; to find lots more,
# use pylint on various modules in graphics/drawing)

drawing_phase = None

# =====

# Everything below here should be something that belongs in an object
# that corresponds to a "GL resource context"' someday we will refactor
# this module into such an object (owned by each glpane) and other things.
# For example, fixed-use OpenGL display lists (like sphereList) belong here.
# (Presently many such things are stored here by external code, like setup_draw.
#  That should be changed too.)
# [bruce 090304]

from graphics.drawing.ShaderGlobals import SphereShaderGlobals
from graphics.drawing.ShaderGlobals import CylinderShaderGlobals

sphereShaderGlobals = SphereShaderGlobals()
cylinderShaderGlobals = CylinderShaderGlobals()

# for use by test_drawing.py only, shares no state with other globals
test_sphereShader = None

# ==

def setup_desired_shaders(glprefs): #bruce 090303
    """
    Setup shaders within our state, according to shader-use desires of glprefs.

    @note: does not check glpane.permit_shaders.
    """
    if glprefs.sphereShader_desired():
        sphereShaderGlobals.setup_if_needed_and_not_failed()

    if glprefs.cylinderShader_desired():
        cylinderShaderGlobals.setup_if_needed_and_not_failed()

    return

def sphereShader_available(): #bruce 090306
    return sphereShaderGlobals.shader_available()

def cylinderShader_available():
    return cylinderShaderGlobals.shader_available()

coneShader_available = cylinderShader_available

# ==

def enabled_shaders(glpane): #bruce 090303
    """
    Return a list of the shaders that are enabled for use during this
    drawing frame (in a deterministic order), in this glpane.

    "enabled" means three things are true:
    * desired for its types of primitives in CSDLs (re glpane.glprefs),
    * available for use (re shader setup errors; see shader_available),
    * permitted for use (glpane.permit_shaders).

    @note: the result is currently [090303] one of the values

    []
    [sphereShader]
    [cylinderShader]
    [sphereShader, cylinderShader]

    where sphereShader and cylinderShader are instances of subclasses
    of GLShaderObject which are enabled for current use in the
    GL resource context represented by this (singleton) module.

    Note that prefs might request a shader without it being enabled (due to
    error or to its not yet being created), or it might exist and be useable
    without prefs wanting to use it (if they were turned off during the
    session).
    """
    glprefs = glpane.glprefs
    res = []
    if glpane.permit_shaders and glprefs._use_batched_primitive_shaders:
        # note: testing _use_batched_primitive_shaders is just
        # an optimization (and a kluge) (so nevermind that it's private)
        for desired, shaderGlobals in [
            (glprefs.sphereShader_desired(), sphereShaderGlobals),
            (glprefs.cylinderShader_desired(), cylinderShaderGlobals),
         ]:
            if desired and shaderGlobals.shader_available():
                res += [ shaderGlobals.shader ]
            continue
    return res

# end
