# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
example_expr_command.py -- example of how to use an interactive graphics
expr in a command (unfinished, so partly scratch code); command and PM
are each variants of ExampleCommand2's command and PM classes
 
$Id$

History:

070830 bruce split this out of test_commands.py and test_command_PMs.py,
in which it was called ExampleCommand2E
"""

# == PM class

from test_command_PMs import ExampleCommand2_PM

class ExampleCommand2E_PM( ExampleCommand2_PM ):
    """Property Manager for Example Command 2E"""
    title = "Example Command 2E"
    pass

# == command class

# these imports are not needed in a minimal example like ExampleCommand2:

from OpenGL.GL import GL_LEQUAL
from drawer import drawline
from constants import red, green
from VQT import V
from exprs.instance_helpers import get_glpane_InstanceHolder
from exprs.Boxed import Boxed
from exprs.draggable import DraggablyBoxed

from exprs.instance_helpers import InstanceMacro
from exprs.attr_decl_macros import State
from exprs.TextRect import TextRect

class TextState(InstanceMacro): # rename?
    text = State(str, "initial text", doc = "text")
    _value = TextRect(text) # need size?
    pass

from test_commands import ExampleCommand2

class ExampleCommand2E(ExampleCommand2, object):
    """
    Add things not needed in a minimal example, to try them out.
    (Uses a PM which is the same as ExampleCommand2 except for title.)
    """
    # Note: object superclass is only needed to permit super(ExampleCommand2E, self) to work.
    # object superclass should not come first, or it overrides __new__
    # (maybe could fix using def __init__ -- not tried, since object coming last works ok)

    modename = 'ExampleCommand2E-modename'
    default_mode_status_text = "ExampleCommand2E"
    PM_class = ExampleCommand2E_PM

    standard_glDepthFunc = GL_LEQUAL # overrides default value of GL_LESS from GLPane
        # note: this is to prevent this warning:
        ## fyi (printonce): Overlay in reverse order (need to override standard_glDepthFunc in your new mode??)
        # but we should probably make it the default for all modes soon.

    def __init__(self, glpane):
        "create an expr instance, to draw in addition to the model"
        super(ExampleCommand2E, self).__init__(glpane)
        expr1 = TextState()
        expr2 = DraggablyBoxed(expr1, resizable = True)
            ###BUG: resizing is projecting mouseray in the wrong way, when plane is tilted!
            # I vaguely recall that the Boxed resizable option was only coded for use in 2D widgets,
            # whereas some other constrained drag code is correct for 3D but not yet directly usable in Boxed.
            # So this is just an example interactive expr, not the best way to do resizing in 3D. (Though it could be fixed.)

        # note: this code is similar to expr_instance_for_imagename in confirmation_corner.py
        ih = get_glpane_InstanceHolder(glpane)
        expr = expr2
        index = (id(self),) # WARNING: needs to be unique, we're sharing this InstanceHolder with everything else in NE1
        self._expr_instance = ih.Instance( expr, index, skip_expr_compare = True)

        return
        
    def Draw(self):
        """
        Do some custom drawing (in the model's abs coordsys) after drawing the model.
        """
        #print "start ExampleCommand2E Draw"
        glpane = self.o
        super(ExampleCommand2E, self).Draw()
        drawline(red, V(1,0,1), V(1,1,1), width = 2)
        self._expr_instance.draw()
        #print "end ExampleCommand2E Draw"
    
    pass # end of class ExampleCommand2E

# end
