"""
$Id$
"""

from modes import basicMode
from selectAtomsMode import selectAtomsMode

from PropMgrBaseClass import PropMgrBaseClass

from debug import register_debug_menu_command

from GLPane import GLPane # maybe for an isinstance assertion only


class ExampleCommand1(selectAtomsMode):
    """Example command, which uses behavior similar to selectAtomsMode. [Which in future may inherit class Command.]
    """
    modename = 'ExampleCommand1-modename' # internal #e fix init code in basicMode to get it from classname?
    default_mode_status_text = "ExampleCommand1"
    #e define msg_modename, or fix init code in basicMode to get it from default_mode_status_text or classname or...
    # note: that init code won't even run now, since superclas defs it i think -- actually, not sure abt that, probably it doesn;t
    pass

class ExampleCommand1_PM(PropMgrBaseClass):
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
    return cmdrun

def start_cmdrun( cmdrun):
    ## ideally:  cmd.Start() #######
    glpane = cmdrun.glpane
    glpane.mode.Done(new_mode = cmdrun) # is this what takes the old mode's PM away?
    print "done with start_cmdrun for", cmdrun
        # returns as soon as user is in it, doesn't wait for it to "finish" -- so run is not a good name -- use Enter??
        # problem: Enter is only meant to be called internally by glue code in modeMixin.
        # solution: use a new method, maybe Start. note, it's not guaranteed to change to it immediately! it's like Done (newmode arg).

def enter_ExampleCommand1(widget):
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
        import test_commands
        reload(test_commands)
        from test_commands import enter_ExampleCommand1_doit
    enter_ExampleCommand1_doit(glpane)
    return

def enter_ExampleCommand1_doit(glpane):
    cmdrun = construct_cmdrun(ExampleCommand1, glpane)
    start_cmdrun(cmdrun)
    return

register_debug_menu_command( "ExampleCommand1", enter_ExampleCommand1 )

def register_all_entermode_commands(glpane):
    for name in glpane.modetab.keys():
        def func(glp, name = name):
            glp.mode.Done(new_mode = name)
            print "did Enter %s" % name
            return
        register_debug_menu_command( "Enter %s" % name, func )
    return

if 1:
    import env
    win = env.mainwindow()
    glpane = win.glpane
    register_all_entermode_commands(glpane)
    
# end
