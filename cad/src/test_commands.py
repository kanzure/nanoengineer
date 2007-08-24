# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
test_commands.py -- try out using mode classes as command classes for a command stack;
 find out the minimal needs for a command with PM (and improve them);
 prototype a command stack
 
$Id$


How to run these test commands:

- set the debug_pref "test_commands enabled (next session)"

- quit and rerun NE1

- the debug menu's submenu "other" should contain new menu commands
defined in this file, such as ExampleCommand1.


Misc bugs [this list might be out of date]:

- when exiting ExampleCommand2E (using GBC and its own graphics), the graphics remain, because the mode remains.
  A mode calls Done when it leaves but a generator doesn't, so these leave themselves behind as the mode.
  Can they safely call Done?
  And in what method should they do it? A button click, or some exit method inside GBC?

- when exiting EC2E, the PM does disappear, so the conf corner should -- and it does, but not right away,
  so I think we're missing a gl_update. Maybe the existing PM-changing methods need to provide one for the CC
  (gl_update_confcorner or so)?
  
- PM is not removed when entering testmode [probably a special case of the above]

[status: exit code added to EC1 and works; not yet to EC2] ####
  
- [bug noticed 070725]: PM is removed, but its tab remains open, when exiting ExampleCommand1
(true both before and after conversion to use PM_Dialog instead of PropMgrBaseClass)

Cosmetic bugs:

- closing groupboxes makes them flash

- [fixed] tooltip for sponsor button appears everywhere in the PM, even in its bg (annoying) [fixed in PMBC]


TODO:

When cleaning up PropMgrBaseClass etc, note some other things Mark wants to work on soon:

- add message boxes to users of PropertyManagerMixin, in a way easily moved over to PropMgrBaseClass when they use that

- port more modes over to PropMgrBaseClass, e.g. extrudeMode

- split some PMs/modes into more than one smaller PM (especially MMKit). 
  Note: See PM_ElementSelector.py. Mark 2007-08-07.

"""

from test_command_PMs import ExampleCommand1_PM
from test_command_PMs import ExampleCommand2_PM
from test_command_PMs import ExampleCommand2E_PM

from PM.PM_WidgetsDemoPropertyManager import PM_WidgetsDemoPropertyManager

## from modes import basicMode
from selectAtomsMode import selectAtomsMode

from debug import register_debug_menu_command

from GLPane import GLPane # maybe only needed for an isinstance assertion

class ExampleCommand(selectAtomsMode):
    """
    Abstract superclass for the example commands in this file.
    Specific command subclasses need to define the following class constants:
    modename, default_mode_status_text, and PM_class.
    Some of them also need to override mode methods, such as Draw.
    """
    return_to_prior_command = False
    
    def init_gui(self):
        print "init_gui in", self ###
        win = self.win
        self.__PM = pm = self.PM_class(win, commandrun = self)
        pm.show()
        selectAtomsMode.init_gui(self) # this fixed the "disconnect without connect" bug
            #k will we need to do this first not last? or not do all of it? seems ok so far.
        return

    def restore_gui(self):
        print "restore_gui in", self ###
        self.__PM.hide() # this works (PM area becomes blank), but doesn't remove the PM tab or change to the MT tab
            ##e should find existing code for doing that and make a common routine in the featureManager to do it (if not one already)
        selectAtomsMode.restore_gui(self) # this apparently worked even when it called init_gui by mistake!!
        return
    
    pass

class Example_TemporaryCommand_useParentPM(ExampleCommand):
    """
    A kind of example command which suspends the prior command
    and returns to it when done, but only works for commands
    with no PM of their own, which want the parent PM to remain
    visible (and potentially useable) while they run.
       Note that in current code, the parent Confirmation Corner
    remains visible as well. Whether it (and the PM done/cancel
    buttons) work properly during this time is unknown. ###TEST/REVIEW
    """
    # works like panlikeMode I guess -- not yet correct when used together with those!
    # Need to merge this with panlikeMode, use a class constant instead of modename check,
    # know when a toggle button is present, etc. ###TODO
    
    return_to_prior_command = True # class constant ##### bruce 070813; experiment; API will change a lot
        # This needs to affect the way we leave the prior command when entering this one --
        # which means, it needs to affect code that is not inside this command itself.
    prior_command = None # dflt val of ivar
    def set_prior_command(self, command):
        # the ivar we set here has the same purpose as glpane.prevMode in panlikeMode --
        # but storing it in self is far less bug prone, i hope! Do this in panlikeMode too. ###TODO
        self.prior_command = command
        return
    def Done(self, new_mode = None, **new_mode_options):
        ### REVIEW whether it's best to override this vs some other mode api method
        ### also how does it interact with new_mode arg? probably callers of that need to be revised to say what they really mean.

        ###TODO -- revise this per panlikeMode
        if new_mode is None:
            print "leaving subcommand %r normally" % self
            new_mode = self.prior_command
            if new_mode:
                new_mode_options['resuming'] = True # passes resuming = True
                    # note: this is to not call Enter on resumed mode, just init_gui & updaters
                    ###BUG: if this still calls init_gui that might be called twice -- likely bug.
                    # Same issue for extrude. ADD CODE to extrude to detect misuse of connect/discon -- a signal overlap counter!
        else:
            print "leaving subcommand %r abnormally, going to %r" % (self, new_mode)
        ExampleCommand.Done(self, new_mode, **new_mode_options)
        return
    pass
    
class ExampleCommand1(ExampleCommand):
    """
    Example command, which uses behavior similar to selectAtomsMode. 
    [Which in future may inherit class Command.]
    """
    modename = 'ExampleCommand1-modename' # internal #e fix init code in basicMode to get it from classname?
    default_mode_status_text = "ExampleCommand1"
    #e define msg_modename, or fix init code in basicMode to get it from default_mode_status_text or classname or...
    # note: that init code won't even run now, since superclass defs it i think -- actually, not sure abt that, probably it doesn't
    PM_class = ExampleCommand1_PM
    
    # note: ok_btn_clicked, etc, must be defined in our PM class (elsewhere),
    # not in this class.

    pass

class ExampleCommand2( Example_TemporaryCommand_useParentPM): # WRONG: this has own PM, so it'll mess up parent one.
    """
    Like ExampleCommand1, but use GBC (GeneratorBaseClass).
    (This difference shows up only in our PM class.)
    """
    modename = 'ExampleCommand2-modename'
    default_mode_status_text = "ExampleCommand2"
    PM_class = ExampleCommand2_PM
    
    pass

# ==

# these imports are not needed in a minimal example like ExampleCommand2;
# to make that clear, we put them down here instead of at the top of the file
from OpenGL.GL import GL_LEQUAL
from drawer import drawline
from constants import red, green
from VQT import V
##from exprs.basic import PIXELS
##from exprs.images import Image
##from exprs.Overlay import Overlay
from exprs.instance_helpers import get_glpane_InstanceHolder
from exprs.Rect import Rect # needed for Image size option and/or for testing
from exprs.Boxed import Boxed
from exprs.draggable import DraggablyBoxed
from exprs.basic import InstanceMacro, State

from exprs.TextRect import TextRect#k
class TextState(InstanceMacro):#e rename?
    text = State(str, "initial text", doc = "text")#k
    _value = TextRect(text) #k value #e need size?s
    pass

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
        ## expr1 = Rect(4,1,green)
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
        from drawer import drawline
        from constants import red
        from VQT import V
        drawline(red, V(1,0,1), V(1,1,1), width = 2)
        self._expr_instance.draw()
        #print "end ExampleCommand2E Draw"
    
    pass # end of class ExampleCommand2E

# ==

# this should be split into several files; then these imports will be at
# the top of one of the split files

from exprs.ExprsMeta import ExprsMeta
from exprs.StatePlace import StatePlace
from exprs.instance_helpers import IorE_guest_mixin

from test_command_PMs import test_connectWithState_PM
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

def cylinder_height():
    import env
    return env.prefs.get( CYLINDER_HEIGHT_PREFS_KEY, CYLINDER_HEIGHT_DEFAULT_VALUE)

def set_cylinder_height(val):
    import env
    env.prefs[CYLINDER_HEIGHT_PREFS_KEY] = val

from constants import pink
DX = V(1,0,0)
DY = V(0,1,0)
ORIGIN = V(0,0,0) # import these from where?
from drawer import drawcylinder, drawsphere

class test_connectWithState(ExampleCommand, IorE_guest_mixin):
    # the following are needed for now in order to use the State macro,
    # along with the IorE_guest_mixin superclass; this will be cleaned up:
    __metaclass__ = ExprsMeta
    transient_state = StatePlace('transient')
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

# ==

class PM_WidgetDemo(ExampleCommand):
    """
    Used to demo all the PM widgets.
    
    @see: PM_WidgetsDemoPropertyManager in PM_WidgetsDemoPropertyManager.py.
    """
    modename = 'PM_WidgetDemo-modename'
    default_mode_status_text = "PM_Widgets Demo"
    PM_class = PM_WidgetsDemoPropertyManager
    pass

# == generic example or debug/devel code below here

def construct_cmdrun( cmd_class, glpane):
    """Construct and return a new "CommandRun" object, for use in the given glpane.
    Don't Start it -- there is no obligation for the caller to ever start it;
    and if it does, it's allowed to do that after other user events and model changes
    happened in the meantime [REVIEW THAT, it's not good for "potential commands"] --
    but it should not be after this glpane or its underlying model (assembly object)
    get replaced (e.g. by Open File).
    """
    # (we use same interface as <mode>.__init__ for now,
    #  though passing assy might be more logical)
    cmdrun = cmd_class(glpane)
    ###e should also put it somewhere, as needed for a mode ####DOIT
    if 'kluge, might prevent malloc errors after removing pm from ui (guess)':
        import changes
        changes.keep_forever(cmdrun)
    return cmdrun

def start_cmdrun( cmdrun):
    ## ideally:  cmd.Start() #######
    glpane = cmdrun.glpane
    if cmdrun.return_to_prior_command:
        # 070813 new feature, experimental, implem will change; part of Command Sequencer
        ### probably WRONG; need to analyze what happens in Done to decide how much to do here, and how to protect from exceptions
        cmdrun.set_prior_command(glpane.mode) ###IMPLEM
##        glpane.mode.restore_gui() #k guess; should be suspend_gui ####
##        glpane.mode = cmdrun ### more? call some setter? call update_after_new_mode? ###
##        cmdrun.init_gui()
        glpane.mode.Done(new_mode = cmdrun, suspend_old_mode = True)
        ## glpane.gl_update() # REVIEW: not sure if needed; should be removed if redundant (might be excessive someday)
    else:
        glpane.mode.Done(new_mode = cmdrun) # is this what takes the old mode's PM away?
    print "done with start_cmdrun for", cmdrun
        # returns as soon as user is in it, doesn't wait for it to "finish" -- so run is not a good name -- use Enter??
        # problem: Enter is only meant to be called internally by glue code in modeMixin.
        # solution: use a new method, maybe Start. note, it's not guaranteed to change to it immediately! it's like Done (newmode arg).

def enter_example_command(widget, example_command_classname):
    assert isinstance(widget, GLPane)
    glpane = widget
    if 1 and 'reload before use (this module only)': ###during devel only
        if 0 and 'try reloading preqs too': ### can't work easily, glpane stores all the mode classes (not just their names)...
            glpane._reinit_modes() # just to get out of current mode safely
            import modes
            reload(modes)
            import selectMode
            reload(selectMode)
            import selectAtomsMode
            reload(selectAtomsMode)
            glpane.mode = glpane.nullmode = modes.nullMode()
            glpane._reinit_modes() # try to avoid problems with changing to other modes later, caused by those reloads
                # wrong: uses old classes from glpane
        import test_command_PMs
        reload(test_command_PMs)
        import test_commands
        reload(test_commands)
        from test_commands import enter_example_command_doit
    enter_example_command_doit(glpane, example_command_classname)
    return

def enter_example_command_doit(glpane, example_command_classname):
    example_command_class = globals()[example_command_classname]
    example_command_class.modename += 'x'
        # kluge to defeat userSetMode comparison of modename -- not sure if it works; pretty sure it's needed for now
    cmdrun = construct_cmdrun(example_command_class, glpane)
    start_cmdrun(cmdrun)
    return

for classname in ["ExampleCommand1", "ExampleCommand2", "ExampleCommand2E", "PM_WidgetDemo", "test_connectWithState"]:
    cmdname = classname # for now
    register_debug_menu_command( cmdname, (lambda widget, classname = classname: enter_example_command(widget, classname)) )
    
# end
