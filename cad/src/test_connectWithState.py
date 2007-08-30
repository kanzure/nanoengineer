# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
test_connectWithState.py -- test the connectWithState features,
and scratch code for their improvement.
 
$Id$

History:

070830 bruce split this out of test_commands.py and test_command_PMs.py
"""

# == PM class

from test_command_PMs import test_connectWithState_PM #### TODO: pull in here

from test_command_PMs import CYLINDER_VERTICAL_DEFAULT_VALUE, CYLINDER_WIDTH_DEFAULT_VALUE
    ### REVISE: the default value should come from the stateref, when using the State macro,
    # so it can be defined only in this file and not needed via globals by the PM

# REVISE: for prefs state, what is defined in what file?
# can we make the PM code not even know whether specific state is defined in prefs or in the mode or in a node?
# (i don't yet know how, esp for state in a node where the choice of nodes depends on other state,
#  but it's a good goal -- do we need to get the stateref itself from the command in a standard way? ### REVIEW)

# RELATED ISSUE: are staterefs useful when we don't have a UI to connect widgets to them? guess: yes.

# RELATED: can there be an object with modifiable attrs which refers to prefs values?
# If there was, the attr names would come from where? (the table in preferences.py i guess)
# Or, always define them in your own objs as needed using a State-like macro??

from test_command_PMs import CYLINDER_HEIGHT_PREFS_KEY, CYLINDER_HEIGHT_DEFAULT_VALUE
from test_command_PMs import cylinder_round_caps
    ### better to define here... ### REVISE

# == command class

from test_commands import ExampleCommand

from VQT import V

from constants import pink
# TODO: import the following from somewhere
DX = V(1,0,0)
DY = V(0,1,0)
ORIGIN = V(0,0,0)
from drawer import drawcylinder, drawsphere

from exprs.ExprsMeta import ExprsMeta
from exprs.StatePlace import StatePlace
from exprs.instance_helpers import IorE_guest_mixin
from exprs.attr_decl_macros import State

from OpenGL.GL import GL_LEQUAL

def cylinder_height():
    import env
    return env.prefs.get( CYLINDER_HEIGHT_PREFS_KEY, CYLINDER_HEIGHT_DEFAULT_VALUE)

def set_cylinder_height(val):
    import env
    env.prefs[CYLINDER_HEIGHT_PREFS_KEY] = val

class test_connectWithState(ExampleCommand, IorE_guest_mixin):
    # the following are needed for now in order to use the State macro,
    # along with the IorE_guest_mixin superclass; this will be cleaned up:
    __metaclass__ = ExprsMeta
    transient_state = StatePlace('transient') ###k needed?
    _e_is_instance = True

    # class constants needed by mode API for example commands
    modename = 'test_connectWithState-modename'
    default_mode_status_text = "test_connectWithState"
    PM_class = test_connectWithState_PM

    # this might be needed if we draw any exprs:
    standard_glDepthFunc = GL_LEQUAL

    # tracked state -- this initializes specially defined instance variables
    # which will track all their uses and changes so that connectWithState
    # works for them:
    cylinderVertical = State(bool, False)
    cylinderWidth = State(float, 2.0)
    cylinderColor = State('color-stub', pink) # type should be Color (nim), but type is not yet used
    
        # note: you can add _e_debug = True to one or more of these State definitions
        # to see debug prints about some accesses to this state.
    
    # initial values of instance variables
    propMgr = None

    def __init__(self, glpane):
        super(test_connectWithState, self).__init__(glpane)
            # that only calls some mode's init method,
            # so (for now) call this separately:
        IorE_guest_mixin.__init__(self, glpane)
        return

    def Draw(self):
        color = self.cylinderColor
        length = cylinder_height()
        if self.cylinderVertical:
            direction = DY
        else:
            direction = DX
        end1 = ORIGIN - direction * length/2.0
        end2 = ORIGIN + direction * length/2.0
        radius = self.cylinderWidth / 2.0
        capped = True
        drawcylinder(color, end1, end2, radius, capped)

        if cylinder_round_caps():
            detailLevel = 2
            drawsphere( color, end1, radius, detailLevel)
            drawsphere( color, end2, radius, detailLevel)
        
        return

    def cmd_Bigger(self):
        self.cylinderWidth += 0.5
        set_cylinder_height( cylinder_height() + 0.5)
        # TODO: enforce maxima
        return

    def cmd_Smaller(self):
        self.cylinderWidth -= 0.5
        set_cylinder_height( cylinder_height() - 0.5)
        # enforce minima (###BUG: not the same ones as declared in the PM)
        ### REVISE: min & max should be declared in State macro and (optionally) enforced by it
        if self.cylinderWidth < 0.1:
            self.cylinderWidth = 0.1
        if cylinder_height() < 0.1:
            set_cylinder_height(0.1)
        return
    
    pass

# end
