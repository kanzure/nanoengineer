# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
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
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

TODO: this is now short enough that we could merge this module back into
its client code.
"""

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice

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
            TEST_PYREX_OPENGL = debug_pref("GLPane: TEST_PYREX_OPENGL", Choice([0,1,2]))
            # uncomment this line to set it in the old way:
            ## TEST_PYREX_OPENGL = 1
        if TEST_PYREX_OPENGL:
            from graphics.drawing.c_renderer import test_pyrex_opengl
            test_pyrex_opengl(TEST_PYREX_OPENGL)
                #bruce 090303 split this out (untested;
                # it did work long ago when first written, inlined here)
            pass
        else:
            if self.bc_in_use is not None: #bruce 060414
                self.bc_in_use.draw(self.o, 'fake dispdef kluge')
            
            commonGraphicsMode.Draw(self)   
            #self.griddraw()
            if self.selCurve_List:
                self.draw_selection_curve()
            self.o.assy.draw(self.o)
        return

    pass

# end
