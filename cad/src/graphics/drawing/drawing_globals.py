# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
drawing_globals.py - A module containing global state within the
graphics.drawing suite.

Desireable refactoring: Note that most of this state really belongs
in an object that corresponds to each "GL display list namespace",
i.e. each OpenGL shared resource pool of display lists, textures,
shaders, VBOs, etc. In current code we require all OpenGL drawing
contexts to share that state, so we can get away with keeping it
as globals in a module. Even so, it ought to be refactored, since
this way it makes the code less clear, causes import cycles and
dependencies on import order, confuses pylint, etc.

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

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
"""

# ColorSorter control

#russ 080403: Added drawing variant selection.
use_drawing_variant = use_drawing_variant_default = 1 # DrawArrays from CPU RAM.
use_drawing_variant_prefs_key = "use_drawing_variant"

#russ 080819: Added.
_use_sphere_shaders = use_sphere_shaders_default = True #bruce 090225 revised
use_sphere_shaders_prefs_key = "v1.2/GLPane: use_sphere_shaders"

#russ 090116: Added.
_use_cylinder_shaders = use_cylinder_shaders_default = True #bruce 090303 revised
use_cylinder_shaders_prefs_key = "v1.2/GLPane: use_cylinder_shaders"

#russ 090223: Added.
_use_cone_shaders = use_cone_shaders_default = True #bruce 090225 revised
use_cone_shaders_prefs_key = "v1.2/GLPane: use_cone_shaders"

# Russ 081002: Added.
_use_batched_primitive_shaders = use_batched_primitive_shaders_default = True #bruce 090225 revised
use_batched_primitive_shaders_prefs_key = "v1.2/GLPane: use_batched_primitive_shaders"

#bruce 090303 adding these inits to ease testing for shader presence
# (these variables are set elsewhere, but before this might remain unset when
#  not in use), and an iterator over enabled shaders, and helpers for which
# shaders are desired by prefs.
# This will shortly be moved elsewhere as a refactoring
# (along with the prefs variables related to shaders).

sphereShader = None
cylinderShader = None

def sphereShader_desired(): #bruce 090303
    """
    Based only on preferences, is it desired to use shaders
    for spheres in CSDLs?
    """
    return _use_batched_primitive_shaders and _use_sphere_shaders

def cylinderShader_desired(): #bruce 090303
    """
    Based only on preferences, is it desired to use shaders
    for cylinders in CSDLs?
    """
    return _use_batched_primitive_shaders and _use_cylinder_shaders

def coneShader_desired(): #bruce 090303
    """
    Based only on preferences, is it desired to use shaders
    for cones in CSDLs?
    """
    # this is intentionally not symmetric with cylinderShader_desired(),
    # since we want turning off cylinder shader pref to turn off all uses
    # of the cylinder shader, including cones.
    return _use_batched_primitive_shaders and _use_cylinder_shaders and \
           _use_cone_shaders

def enabled_shaders(): #bruce 090303
    """
    Yield the shaders that are enabled for use during this drawing frame
    (in a deterministic order). The result, if turned into a list,
    is currently [090303] one of the values

    []
    [sphereShader]
    [cylinderShader]
    [sphereShader, cylinderShader]

    where sphereShader and cylinderShader are globals in this module
    whose values are instances of subclasses of GLShaderObject.
    
    For a shader to be "enabled for use" means that it exists, that shader.error
    is not set, and that current prefs say we should use it for its type of
    primitive in any CSDL.

    Note that prefs might request a shader without it being enabled (due to
    error or to its not yet being created), or it might exist and be useable
    without prefs wanting to use it (if they were turned off during the
    session).
    """
    if not _use_batched_primitive_shaders:
        # optimization (kluge)
        return
    for desired, shader in [
        (sphereShader_desired(), sphereShader),
        (cylinderShader_desired(), cylinderShader),
     ]:
        if desired and shader and not shader.error:
            yield shader
        continue
    return

# ==

# Experimental native C renderer (quux module in
# cad/src/experimental/pyrex-opengl)
# [note: as of 090114, this hasn't been maintained for a long time,
#  but it might still mostly work, so we'll keep it around for now
#  as potentially useful example code]
use_c_renderer = use_c_renderer_default = False
#bruce 060323 changed this to disconnect it from old pref setting
use_c_renderer_prefs_key = "use_c_renderer_rev2"

#=

import foundation.env as env #bruce 051126
import utilities.EndUser as EndUser
import sys
import os

from graphics.drawing.glprefs import GLPrefs
import foundation.preferences as preferences # Sets up env.prefs .

# Machinery to load the C renderer.
if EndUser.getAlternateSourcePath() != None:
    sys.path.append(os.path.join( EndUser.getAlternateSourcePath(),
                                  "experimental/pyrex-opengl"))
else:
    sys.path.append("./experimental/pyrex-opengl")

binPath = os.path.normpath(os.path.dirname(os.path.abspath(sys.argv[0]))
                           + '/../bin')
if binPath not in sys.path:
    sys.path.append(binPath)

global quux_module_import_succeeded     # Referenced below in updatePrefsVars().
try:
    import quux
    quux_module_import_succeeded = True
    if "experimental" in os.path.dirname(quux.__file__):
        # Should never happen for end users, but if it does we want to print the
        # warning.
        if env.debug() or not EndUser.enableDeveloperFeatures():
            print "debug: fyi:", \
                  "Using experimental version of C rendering code:", \
                  quux.__file__
except:
    use_c_renderer = False
    quux_module_import_succeeded = False
    if env.debug(): #bruce 060323 added condition
        print "WARNING: unable to import C rendering code (quux module).", \
              "Only Python rendering will be available."
    pass

# ==

    # Russ 080915: Extracted from GLPrefs.update() to break an import cycle.
def updatePrefsVars():
    """
    Helper for GLPrefs.update() .
    """
    global _use_sphere_shaders, _use_cylinder_shaders, _use_cone_shaders
    global _use_batched_primitive_shaders, use_drawing_variant
    global use_c_renderer

    _use_sphere_shaders = env.prefs.get(
        use_sphere_shaders_prefs_key,
        use_sphere_shaders_default)

    _use_cylinder_shaders = env.prefs.get(
        use_cylinder_shaders_prefs_key,
        use_cylinder_shaders_default)

    _use_cone_shaders = env.prefs.get(
        use_cone_shaders_prefs_key,
        use_cone_shaders_default)

    _use_batched_primitive_shaders = env.prefs.get(
        use_batched_primitive_shaders_prefs_key,
        use_batched_primitive_shaders_default)

    use_drawing_variant = env.prefs.get(
        use_drawing_variant_prefs_key,
        use_drawing_variant_default)

    use_c_renderer = (
        quux_module_import_succeeded and
        env.prefs.get(use_c_renderer_prefs_key,
                      use_c_renderer_default))

    if use_c_renderer:
        quux.shapeRendererSetMaterialParameters(self.specular_whiteness,
                                                self.specular_brightness,
                                                self.specular_shininess);
        pass
    return

# A singleton instance of the GLPrefs class.
glprefs = GLPrefs()

# Russ 080915: This would be done by GLPrefs.update() under the GLPrefs
# constructor, except for an awkward inport cycle that otherwise results.
updatePrefsVars()

# ==
# Common code for DrawingSet, TransformControl, et al.

# Russ 080915: Support for lazily updating drawing caches, namely a change
# timestamp.  Rather than recording a time per se, an event counter is used.
NO_EVENT_YET = 0
_event_counter = NO_EVENT_YET
def eventStamp():
    global _event_counter
    _event_counter += 1
    return _event_counter

def eventNow():
    return _event_counter

# end
