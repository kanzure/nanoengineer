# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Select_GraphicsMode_DrawMethod_preMixin.py 

Mixin class for the Select_basicGraphicsMode. The only purpose of creating this 
mixin class was for easy understanding of the code in Select_basicGraphicsMode
As the name suggest, this mixin class overrides only the Draw Method of the 
'basicGraphicsMode' . This is a 'preMixin' class, meaning, it needs to be 
inherited by the subclass 'Select_basicGraphicsMode' _before_ it inherits the 
'basicGraphicsMode'

To be used as a Mixin class only for Select_basicGraphicsMode. 

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

"""

import sys
import os
import foundation.env as env
import Numeric
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslate

from utilities.Log import redmsg

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice
from utilities.debug import print_compact_stack

from command_support.GraphicsMode import commonGraphicsMode

class Select_GraphicsMode_DrawMethod_preMixin(commonGraphicsMode):
    """
    Mixin class for the Select_basicGraphicsMode. The only purpose of creating this 
    mixin class was for easy understanding of the code in Select_basicGraphicsMode
    As the name suggest, this mixin class overrides only the Draw Method of the 
    'basicGraphicsMode' . This is a 'preMixin' class, meaning, it needs to be 
    inherited by the subclass 'Select_basicGraphicsMode' _before_ it inherits the 
    'basicGraphicsMode'.
    @see: B{Select_basicGraphicsMode}
    """
    # ==

    def Draw(self):
        if 1:
            # TODO: move this test code into a specific test mode just for it,
            # so it doesn't clutter up or slow down this general-use mode.
            #
            # wware 060124  Embed Pyrex/OpenGL unit tests into the cad code
            # grantham 060207:
            # Set to 1 to see a small array of eight spheres.
            # Set to 2 to see the Large-Bearing model, but this is most effective if
            #  the Large-Bearing has already been loaded normally into rotate mode
            #bruce 060209 set this from a debug_pref menu item, not a hardcoded flag
            TEST_PYREX_OPENGL = debug_pref("TEST_PYREX_OPENGL", Choice([0,1,2]))
            # uncomment this line to set it in the old way:
            ## TEST_PYREX_OPENGL = 1
        if TEST_PYREX_OPENGL:
            try:
                print_compact_stack("selectMode Draw: " )###
                ### BUG: if import quux fails, we get into some sort of infinite
                ###   loop of Draw calls. [bruce 070917 comment]

                #self.w.win_update()
                ## sys.path.append("./experimental/pyrex-opengl") # no longer 
                ##needed here -- always done in drawer.py
                binPath = os.path.normpath(os.path.dirname(
                    os.path.abspath(sys.argv[0])) + '/../bin')
                if binPath not in sys.path:
                    sys.path.append(binPath)
                import quux
                if "experimental" in os.path.dirname(quux.__file__):
                    print "WARNING: Using experimental version of quux module"
                # quux.test()
                quux.shapeRendererInit()
                quux.shapeRendererSetUseDynamicLOD(0)
                quux.shapeRendererStartDrawing()
                if TEST_PYREX_OPENGL == 1:
                    center = Numeric.array((Numeric.array((0, 0, 0), 'f'),
                                            Numeric.array((0, 0, 1), 'f'),
                                            Numeric.array((0, 1, 0), 'f'),
                                            Numeric.array((0, 1, 1), 'f'),
                                            Numeric.array((1, 0, 0), 'f'),
                                            Numeric.array((1, 0, 1), 'f'),
                                            Numeric.array((1, 1, 0), 'f'),
                                            Numeric.array((1, 1, 1), 'f')), 'f')
                    radius = Numeric.array((0.2, 0.4, 0.6, 0.8,
                                            1.2, 1.4, 1.6, 1.8), 'f')
                    color = Numeric.array((Numeric.array((0, 0, 0, 0.5), 'f'),
                                           Numeric.array((0, 0, 1, 0.5), 'f'),
                                           Numeric.array((0, 1, 0, 0.5), 'f'),
                                           Numeric.array((0, 1, 1, 0.5), 'f'),
                                           Numeric.array((1, 0, 0, 0.5), 'f'),
                                           Numeric.array((1, 0, 1, 0.5), 'f'),
                                           Numeric.array((1, 1, 0, 0.5), 'f'),
                                           Numeric.array((1, 1, 1, 0.5), 'f')), 'f')
                    result = quux.shapeRendererDrawSpheres(8, center, radius, color)
                elif TEST_PYREX_OPENGL == 2:
                    # grantham - I'm pretty sure the actual compilation, init,
                    # etc happens once
                    from bearing_data import sphereCenters, sphereRadii
                    from bearing_data import sphereColors, cylinderPos1
                    from bearing_data import cylinderPos2, cylinderRadii
                    from bearing_data import cylinderCapped, cylinderColors
                    glPushMatrix()
                    glTranslate(-0.001500, -0.000501, 151.873627)
                    result = quux.shapeRendererDrawSpheres(1848, 
                                                           sphereCenters, 
                                                           sphereRadii, 
                                                           sphereColors)
                    result = quux.shapeRendererDrawCylinders(5290, 
                                                             cylinderPos1,
                                                             cylinderPos2, 
                                                             cylinderRadii, 
                                                             cylinderCapped, 
                                                             cylinderColors)
                    glPopMatrix()
                quux.shapeRendererFinishDrawing()

            except ImportError:
                env.history.message(redmsg(
                    "Can't import Pyrex OpenGL or maybe bearing_data.py, rebuild it"))
        else:
            if self.bc_in_use is not None: #bruce 060414
                self.bc_in_use.draw(self.o, 'fake dispdef kluge')
            
            commonGraphicsMode.Draw(self)   
            #self.griddraw()
            if self.selCurve_List: self.draw_selection_curve()
            self.o.assy.draw(self.o)
