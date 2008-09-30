# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Bruce
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from commands.TestGraphics.TestGraphics_PropertyManager import TestGraphics_PropertyManager

from utilities.debug import register_debug_menu_command

# module imports, for global flag set/get access
import graphics.widgets.GLPane_rendering_methods as GLPane_rendering_methods
import prototype.test_drawing as test_drawing

# == GraphicsMode part

class TestGraphics_GraphicsMode(BuildAtoms_GraphicsMode ):
    """
    Graphics mode for TestGraphics command. 
    """
    pass

# == Command part

class TestGraphics_Command(BuildAtoms_Command): 
    """

    """
       
    # class constants
    GraphicsMode_class = TestGraphics_GraphicsMode
    PM_class = TestGraphics_PropertyManager
    
    commandName = 'TEST_GRAPHICS'
    featurename = "Test Graphics"
    from utilities.constants import CL_GLOBAL_PROPERTIES
    command_level = CL_GLOBAL_PROPERTIES
   

    command_should_resume_prevMode = True 
    command_has_its_own_PM = True

    flyoutToolbar_class = None ###k

    # state methods

    def _get_bypass_paintgl(self):
        print "_get_bypass_paintgl returns %r" % (GLPane_rendering_methods.TEST_DRAWING,)######
        return GLPane_rendering_methods.TEST_DRAWING

    def _set_bypass_paintgl(self, enabled):
        print "_set_bypass_paintgl gets %r" % (enabled,)######
        GLPane_rendering_methods.TEST_DRAWING = enabled
        self.glpane.gl_update()

    bypass_paintgl = property( _get_bypass_paintgl,
                               _set_bypass_paintgl,
                               doc = "bypass paintGL normal code"
                                     "(draw specific test cases instead)"
                             )

    def _get_redraw_continuously(self):
        return test_drawing.ALWAYS_GL_UPDATE

    def _set_redraw_continuously(self, enabled):
        test_drawing.ALWAYS_GL_UPDATE = enabled
        self.glpane.gl_update()

    redraw_continuously = property( _get_redraw_continuously,
                                    _set_redraw_continuously,
                                    doc = "call paintGL continuously"
                                          "(cpu can get hot!)"
                                  )

    def _get_spin_model(self):
        return test_drawing.SPIN

    def _set_spin_model(self, enabled):
        test_drawing.SPIN = enabled

    spin_model = property( _get_spin_model,
                           _set_spin_model,
                           doc = "spin model whenever it's redrawn"
                         )
    
    pass
    
# == UI for entering this command

def _enter_test_graphics_command(glpane):
    glpane.assy.w.enterOrExitTemporaryCommand('TEST_GRAPHICS')

register_debug_menu_command( "Test Graphics Performance ...", _enter_test_graphics_command )

# end
