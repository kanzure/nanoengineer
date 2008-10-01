# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Bruce
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode
from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_Command
from commands.TestGraphics.TestGraphics_PropertyManager import TestGraphics_PropertyManager

from utilities.debug import register_debug_menu_command

# module imports, for global flag set/get access
import graphics.widgets.GLPane_rendering_methods as GLPane_rendering_methods
import prototype.test_drawing as test_drawing

from prototype.test_drawing import AVAILABLE_TEST_CASES_ITEMS

# == GraphicsMode part

class TestGraphics_GraphicsMode(SelectAtoms_GraphicsMode ):
    """
    Graphics mode for TestGraphics command. 
    """
    pass

# == Command part

class TestGraphics_Command(SelectAtoms_Command): 
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

    FlyoutToolbar_class = None
        # minor bug, when superclass is Build Atoms: the atoms button in the
        # default flyout remains checked when we enter this command,
        # probably due to command_enter_misc_actions() not being overridden in
        # this command.


    # state methods (which mostly don't use self)

    def _get_bypass_paintgl(self):
        print "bypass_paintgl starts out as %r" % (GLPane_rendering_methods.TEST_DRAWING,) #
        return GLPane_rendering_methods.TEST_DRAWING

    def _set_bypass_paintgl(self, enabled):
        print "bypass_paintgl = %r" % (enabled,) #
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
        
    def _get_print_fps(self):
        return test_drawing.printFrames

    def _set_print_fps(self, enabled):
        test_drawing.printFrames = enabled

    print_fps = property( _get_print_fps,
                           _set_print_fps,
                           doc = "print frames-per-second to console every second"
                         )
        
    def _get_testCaseIndex(self):
        for testCase, desc in AVAILABLE_TEST_CASES_ITEMS:
            if test_drawing.testCase == testCase:
                return AVAILABLE_TEST_CASES_ITEMS.index((testCase, desc))
        print "bug in _get_testCaseIndex"
        return 0 # fallback to first choice

    def _set_testCaseIndex(self, index): # doesn't yet work well
        testCase, desc_unused = AVAILABLE_TEST_CASES_ITEMS[index]
        test_drawing.testCase = testCase
        test_drawing.delete_caches()
        self.glpane.gl_update()

    testCaseIndex = property( _get_testCaseIndex,
                             _set_testCaseIndex,
                             doc = "which testCase to run"
                            )

    testCaseChoicesText = []
    for testCase, desc in AVAILABLE_TEST_CASES_ITEMS:
        testCaseChoicesText.append( "%s: %s" % (testCase, desc) ) # fix format

    def _get_nSpheres(self):
        return test_drawing.nSpheres

    def _set_nSpheres(self, value):
        test_drawing.nSpheres = value
        test_drawing.delete_caches()
        self.glpane.gl_update()

    nSpheres = property( _get_nSpheres,
                           _set_nSpheres,
                           doc = "number on a side of a square of spheres"
                         )
        
    pass
    
# == UI for entering this command

def _enter_test_graphics_command(glpane):
    glpane.assy.w.enterOrExitTemporaryCommand('TEST_GRAPHICS')

register_debug_menu_command( "Test Graphics Performance ...", _enter_test_graphics_command )

# end
