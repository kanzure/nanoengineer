# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
drawing_globals.py - A module containing global state within the
graphics.drawing suite.

Variables can be (and are) dynamically added to the module at runtime.

Some of the variables contained here are mode control for the whole drawing
package, including the ColorSorter suite.  Other parts are communication between
the phases of setup and operations, which is only incidentally about OpenGL.

Import it this way to show that it is a module:
  import graphics.drawing.drawing_globals as drawing_globals

Access variables as drawing_globals.varname .

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""

# ColorSorter control
#bruce 060323 changed this to False for A7 release. russ 080314: default on.
allow_color_sorting = allow_color_sorting_default = True
#bruce 060323 changed this to disconnect it from old pref setting
allow_color_sorting_prefs_key = "allow_color_sorting_rev2"
#russ 080225: Added, 080314: default on.
use_color_sorted_dls = use_color_sorted_dls_default = True
use_color_sorted_dls_prefs_key = "use_color_sorted_dls"
#russ 080320: Added.
use_color_sorted_vbos = use_color_sorted_vbos_default = False
use_color_sorted_vbos_prefs_key = "use_color_sorted_vbos"
#russ 080403: Added drawing variant selection.
use_drawing_variant = use_drawing_variant_default = 1 # DrawArrays from CPU RAM.
use_drawing_variant_prefs_key = "use_drawing_variant"
#russ 080819: Added.
use_sphere_shaders = use_sphere_shaders_default = False
use_sphere_shaders_prefs_key = "use_sphere_shaders"

# Experimental native C renderer (quux module in
# cad/src/experimental/pyrex-opengl)
use_c_renderer = use_c_renderer_default = False
#bruce 060323 changed this to disconnect it from old pref setting
use_c_renderer_prefs_key = "use_c_renderer_rev2"

#=

import foundation.env as env #bruce 051126
import utilities.EndUser as EndUser
import sys
import os

if EndUser.getAlternateSourcePath() != None:
    sys.path.append(os.path.join( EndUser.getAlternateSourcePath(),
                                  "experimental/pyrex-opengl"))
else:
    sys.path.append("./experimental/pyrex-opengl")

binPath = os.path.normpath(os.path.dirname(os.path.abspath(sys.argv[0]))
                           + '/../bin')
if binPath not in sys.path:
    sys.path.append(binPath)

global quux_module_import_succeeded
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
