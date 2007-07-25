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

- split some PMs/modes into more than one smaller PM (especially MMKit)

"""

from test_command_PMs import ExampleCommand1_PM, ExampleCommand2_PM, ExampleCommand2E_PM

## from modes import basicMode
from selectAtomsMode import selectAtomsMode

from debug import register_debug_menu_command

from GLPane import GLPane # maybe only needed for an isinstance assertion

class _BUGFIXED_selectAtomsMode(selectAtomsMode):
    def set_selection_filter(self, enabled): ###@@@ IS THIS STILL NEEDED? #k
        # This is needed here for now, since it can't be added directly to selectAtomsMode
        # (where it logically belongs, since it's a selectAtomsMode method that tries to use it),
        # due to problems caused by misguided multiple inheritance in selectAtomsMode.
        # [Adding it here 070704 makes this example command work again, after we broke it knowingly
        #  in the A9.1 release, in order to fix selection filter bugs caused by adding this method
        #  to selectAtomsMode itself. It overrode the same method in a mixin class, that ought to be
        #  used to construct a separate object rather than being a mixin class of a subclass of
        #  selectAtomsMode.]
        pass
    pass
    
class ExampleCommand1(_BUGFIXED_selectAtomsMode):
    """Example command, which uses behavior similar to selectAtomsMode. [Which in future may inherit class Command.]
    """
    modename = 'ExampleCommand1-modename' # internal #e fix init code in basicMode to get it from classname?
    default_mode_status_text = "ExampleCommand1"
    #e define msg_modename, or fix init code in basicMode to get it from default_mode_status_text or classname or...
    # note: that init code won't even run now, since superclas defs it i think -- actually, not sure abt that, probably it doesn't

    def init_gui(self):
        print "init_gui in", self ####

        win = self.win
        self.__PM = pm = ExampleCommand1_PM(win, commandrun = self)
        pm.show()
        selectAtomsMode.init_gui(self) # this fixed the "disconnect without connect" bug
            #k will we need to do this first not last? or not do all of it? seems ok so far.
        return

    def restore_gui(self):
        print "restore_gui in", self ####

        self.__PM.hide() # this works (PM area becomes blank), but doesn't remove the PM tab or change to the MT tab
            ##e should find existing code for doing that and make a common routine in the featureManager to do it (if not one already)
        selectAtomsMode.restore_gui(self) # this apparently worked even when it called init_gui by mistake!!
        return

    # note: ok_btn_clicked, etc, must be defined in our PM class below,
    # not in this class.

    pass # end of class ExampleCommand1

class ExampleCommand2(_BUGFIXED_selectAtomsMode):
    "same but use GBC"

    modename = 'ExampleCommand2-modename'
    default_mode_status_text = "ExampleCommand2"

    def init_gui(self):
        print "init_gui in", self ####

        win = self.win
        self.__PM = pm = ExampleCommand2_PM(win, commandrun = self)
        pm.show()
        selectAtomsMode.init_gui(self)
        return

    def restore_gui(self):
        print "restore_gui in", self ####

        self.__PM.hide()
        selectAtomsMode.restore_gui(self)
        return
    
    pass # end of class ExampleCommand2

# ==

# these imports are not needed in a minimal example like ExampleCommand2
from OpenGL.GL import GL_LEQUAL
from drawer import drawline
from constants import red, green
from VQT import V
##from exprs.basic import PIXELS
##from exprs.images import Image
##from exprs.Overlay import Overlay
from exprs.instance_helpers import get_glpane_InstanceHolder
from exprs.Rect import Rect # needed for Image size option and/or for testing
from exprs.Boxed import Boxed, DraggablyBoxed
from exprs.basic import InstanceMacro, State

from exprs.TextRect import TextRect#k
class TextState(InstanceMacro):#e rename?
    text = State(str, "initial text", doc = "text")#k
    _value = TextRect(text) #k value #e need size?s
    pass

class ExampleCommand2E(ExampleCommand2, object):
    "add things not needed in a minimal example, to try them out (uses same PM as ExampleCommand2)"
    # Note: object superclass is only needed to permit super(ExampleCommand2E, self) to work.
    # object superclass should not come first, or it overrides __new__
    # (maybe could fix using def __init__ -- not tried, since object coming last works ok)

    modename = 'ExampleCommand2E-modename'
    default_mode_status_text = "ExampleCommand2E"
    PM_class = ExampleCommand2E_PM ### NOT YET USED

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
        "do some custom drawing (in the model's abs coordsys) after drawing the model"
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

for classname in ["ExampleCommand1", "ExampleCommand2", "ExampleCommand2E"]:
    cmdname = classname # for now
    register_debug_menu_command( cmdname, (lambda widget, classname = classname: enter_example_command(widget, classname)) )

def register_all_entermode_commands(glpane):
    for name in glpane.modetab.keys():
        def func(glp, name = name):
            glp.mode.Done(new_mode = name)
            print "did Enter %s" % name
            return
        register_debug_menu_command( "Enter %s" % name, func )
    return

if 0:
    import env
    win = env.mainwindow()
    glpane = win.glpane
    register_all_entermode_commands(glpane)
    
# end
