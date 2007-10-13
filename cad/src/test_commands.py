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
defined in this file, such as ExampleCommand1. (Note: not all of them
are contiguous in that submenu, since the entire submenu is sorted
alphabetically.)


Cosmetic bugs:

- closing groupboxes makes them flash


TODO:

Split into several files in a subdirectory.

When cleaning up PropMgrBaseClass etc, note some other things Mark wants to work on soon:

- add message boxes to users of PropertyManagerMixin, in a way easily moved over to PropMgrBaseClass when they use that

- port more modes over to PropMgrBaseClass, e.g. extrudeMode

- split some PMs/modes into more than one smaller PM (especially MMKit). 
  Note: See PM_ElementSelector.py. Mark 2007-08-07.

Fix problems with Example_TemporaryCommand_useParentPM (commented where it's used)

"""

from test_command_PMs import ExampleCommand1_PM
from test_command_PMs import ExampleCommand2_PM

from PM.PM_WidgetsDemoPropertyManager import PM_WidgetsDemoPropertyManager

## from modes import basicMode
from selectAtomsMode import selectAtomsMode

from debug import register_debug_menu_command

from GLPane import GLPane # maybe only needed for an isinstance assertion

# ==

class ExampleCommand(selectAtomsMode):
    """
    Abstract superclass for the example commands in this file.
    Specific command subclasses need to define the following class constants:
    modename, default_mode_status_text, and PM_class.
    Some of them also need to override mode methods, such as Draw.
    """
    test_commands_start_as_temporary_command = False
    PM_class = None # if not overridden, means we need no PM (BUG: we'll still get a PM tab)
    
    def init_gui(self):
        print "init_gui in", self ###
        win = self.win
        # note: propMgr is initialized to None in our superclass anyMode
        if self.PM_class:
            self.propMgr = self.PM_class(win, commandrun = self)
        selectAtomsMode.init_gui(self) # this fixed the "disconnect without connect" bug
            #k will we need to do this first not last? or not do all of it? seems ok so far.
        if self.propMgr:
            self.propMgr.show()
        return

    def restore_gui(self):
        print "restore_gui in", self ###
        if self.propMgr:
            self.propMgr.close() # removes PM tab -- better than the prior .hide() call [bruce 070829]
        selectAtomsMode.restore_gui(self) # this apparently worked even when it called init_gui by mistake!!
        return
    
    pass

# ==

class Example_TemporaryCommand_useParentPM(ExampleCommand): # note: this works if you have your own PM; perhaps untested when you don't
    command_can_be_suspended = False #bruce 071011
    command_should_resume_prevMode = True #bruce 071011, to be revised (replaces need for customized Done method)
    test_commands_start_as_temporary_command = True # enter in different way
        ### TODO: set up a similar thing in Command API? it would replace all calls of userEnterTemporaryCommand
    pass

# ==

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

### TODO: split this part (here to end) into a separate file

import EndUser, Initialize

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
    if not hasattr(cmdrun, 'glpane'):
        print "bug: no glpane in cmdrun %r: did it forget to call ExampleCommand.__init__?" % (cmdrun,)
    ###e should also put it somewhere, as needed for a mode ####DOIT
    if 'kluge, might prevent malloc errors after removing pm from ui (guess)':
        import changes
        changes.keep_forever(cmdrun)
    return cmdrun

def start_cmdrun( cmdrun):
    ## ideally:  cmd.Start() #######
    glpane = cmdrun.glpane # TODO: glpane -> commandSequencer
    if cmdrun.test_commands_start_as_temporary_command:
        # bruce 071011
        # note: was written for commands with no PM of their own, but was only tested for a command that has one (and works)...
        # also do we need the Draw delegation to prevMode as in TemporaryCommand_Overdrawing? ### REVIEW
        glpane.userEnterTemporaryCommand( cmdrun)
    else:
        glpane.currentCommand.Done(new_mode = cmdrun) # is this what takes the old mode's PM away?
    print "done with start_cmdrun for", cmdrun
        # returns as soon as user is in it, doesn't wait for it to "finish" -- so run is not a good name -- use Enter??
        # problem: Enter is only meant to be called internally by glue code in modeMixin.
        # solution: use a new method, maybe Start. note, it's not guaranteed to change to it immediately! it's like Done (newmode arg).
    return

def enter_example_command(widget, example_command_classname):
    assert isinstance(widget, GLPane)
    glpane = widget
    if 0 and EndUser.enableDeveloperFeatures(): ###during devel only; broken due to file splitting
        # reload before use (this module only)
        if 0 and 'try reloading preqs too': ### can't work easily, glpane stores all the mode classes (not just their names)...
            glpane._reinit_modes() # just to get out of current mode safely
            import modes
            reload(modes)
            import selectMode
            reload(selectMode)
            import selectAtomsMode
            reload(selectAtomsMode)
            
            ## glpane.mode = glpane.nullmode = modes.nullMode()
            # revised 071010 (glpane == commandSequencer == modeMixin), new code UNTESTED:
            glpane._recreate_nullmode()
            glpane.use_nullmode()

            glpane._reinit_modes() # try to avoid problems with changing to other modes later, caused by those reloads
                # wrong: uses old classes from glpane
        import test_command_PMs
        reload(test_command_PMs)
        Initialize.forgetInitialization(__name__)
        import test_commands
        reload(test_commands)
        from test_commands import enter_example_command_doit
    else:
        from test_commands import enter_example_command_doit
        
    enter_example_command_doit(glpane, example_command_classname)
    return

def enter_example_command_doit(glpane, example_command_classname):
    example_command_class = globals()[example_command_classname]
    example_command_class.modename += 'x'
        # kluge to defeat _f_userEnterCommand comparison of modename -- not sure if it works; pretty sure it's needed for now
        # TODO: replace it with a new option to pass to that method
    cmdrun = construct_cmdrun(example_command_class, glpane)
    start_cmdrun(cmdrun)
    return

def initialize():
    if (Initialize.startInitialization(__name__)):
        return
    
    # initialization code (note: it's all a kluge, could be cleaned up pretty easily)
    classnames = ["ExampleCommand1", "ExampleCommand2", "ExampleCommand2E"] # extended below

    global test_connectWithState
        # this is needed due to globals()[example_command_classname] above (kluge)
    from test_connectWithState import test_connectWithState
        ### once we split this file, we can avoid import loop & still import this at top,
        # and same for the other imports here
    classnames.append("test_connectWithState")

    global ExampleCommand2E
    from example_expr_command import ExampleCommand2E
    classnames.append("ExampleCommand2E")

    global test_polyline_drag
    from test_polyline_drag import test_polyline_drag # ditto
    classnames.append("test_polyline_drag")

    for classname in classnames:
        cmdname = classname # for now
        register_debug_menu_command( cmdname, (lambda widget, classname = classname: enter_example_command(widget, classname)) )
    
    Initialize.endInitialization(__name__)
    return

initialize() ### TODO: call this from another file, and after the reload of this module above

# end
