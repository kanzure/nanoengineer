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

class ExampleCommand(selectAtomsMode):
    """
    Abstract superclass for the example commands in this file.
    Specific command subclasses need to define the following class constants:
    modename, default_mode_status_text, and PM_class.
    Some of them also need to override mode methods, such as Draw.
    """
    return_to_prior_command = False
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
    # works like ArrangementMode I guess -- not yet correct when used together with those!
    # Need to merge this with ArrangementMode, use a class constant instead of modename check,
    # know when a toggle button is present, etc. ###TODO
    
    return_to_prior_command = True # class constant ##### bruce 070813; experiment; API will change a lot
        # This needs to affect the way we leave the prior command when entering this one --
        # which means, it needs to affect code that is not inside this command itself.
    prior_command = None # dflt val of ivar
    def set_prior_command(self, command):
        # the ivar we set here has the same purpose as glpane.prevMode in ArrangementMode --
        # but storing it in self is far less bug prone, i hope! Do this in ArrangementMode too. ###TODO
        self.prior_command = command
        return
    def Done(self, new_mode = None, **new_mode_options):
        ### REVIEW whether it's best to override this vs some other mode api method
        ### also how does it interact with new_mode arg? probably callers of that need to be revised to say what they really mean.

        ###TODO -- revise this per ArrangementMode
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
            glpane.mode = glpane.nullmode = modes.nullMode()
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
        # kluge to defeat userSetMode comparison of modename -- not sure if it works; pretty sure it's needed for now
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
