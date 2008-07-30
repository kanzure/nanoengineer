# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
test_commands_init.py -- make the commands in test_commands available in the UI.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details. 

How to run these test commands: see test_commands.py docstring.

This is initialized in startup_misc.py as of 071030.
"""

from utilities.debug import register_debug_menu_command

import utilities.EndUser as EndUser, utilities.Initialize as Initialize

# ==

def construct_cmdrun( cmd_class, glpane):
    """
    Construct and return a new "command run" object, for use in the given glpane.
    Don't start it -- there is no obligation for the caller to ever start it;
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
        import foundation.changes as changes
        changes.keep_forever(cmdrun)
    return cmdrun

def start_cmdrun( cmdrun):
    ## ideally:  cmd.Start() #######
    glpane = cmdrun.glpane # TODO: glpane -> commandSequencer
    if cmdrun.test_commands_start_as_temporary_command:
        # bruce 071011
        # note: was written for commands with no PM of their own, but was only tested for a command that has one (and works)...
        # also do we need the Draw delegation to prevMode as in TemporaryCommand_Overdrawing? ### REVIEW
        #
        # update, bruce 080730:
        # TODO: print a warning if cmdrun.command_level is not something
        # we'd consider "nestable", per the likely intent of starting it
        # as a temporary command.
        glpane.userEnterTemporaryCommand( cmdrun, always_update = True)
    else:
        glpane.currentCommand.Done(new_mode = cmdrun) # is this what takes the old mode's PM away?
    print "done with start_cmdrun for", cmdrun
        # returns as soon as user is in it, doesn't wait for it to "finish" -- so run is not a good name -- use Enter??
        # problem: Enter is only meant to be called internally by glue code in modeMixin.
        # solution: use a new method, maybe Start. note, it's not guaranteed to change to it immediately! it's like Done (newmode arg).
    return

def enter_example_command(widget, example_command_classname):
##    assert isinstance(widget, GLPane) # assumed by _reinit_modes; assertion disabled to fix an import cycle
    glpane = widget
    if 0 and EndUser.enableDeveloperFeatures(): ###during devel only; broken due to file splitting
        # reload before use (this module only)
        if 0 and 'try reloading preqs too': ### can't work easily, glpane stores all the mode classes (not just their names)...
            glpane._reinit_modes() # just to get out of current mode safely
            import command_support.modes as modes
            reload(modes)
            ## from selectAtomsMode import selectAtomsMode # commented so it doesn't affect import dependency tools
            _superclass = 'Undefined variable' # FIX
            if _superclass is selectAtomsMode:
                import commands.Select.selectMode as selectMode
                reload(selectMode)
                import commands.SelectAtoms.selectAtomsMode as selectAtomsMode
                reload(selectAtomsMode)
            
            # revised 071010 (glpane == commandSequencer == modeMixin), new code UNTESTED:
            glpane._recreate_nullmode()
            glpane.use_nullmode()

            glpane._reinit_modes() # try to avoid problems with changing to other modes later, caused by those reloads
                # wrong: uses old classes from glpane
        import prototype.test_command_PMs as test_command_PMs
        reload(test_command_PMs)
        Initialize.forgetInitialization(__name__)
        import prototype.test_commands_init as test_commands_init
        reload(test_commands_init)
        test_commands_init.initialize()
            # (note: reload code is untested since the change [bruce 071030]
            #  to call initialize explicitly rather than as import side effect,
            #  done together with splitting this module out of test_commands)
        from prototype.test_commands_init import enter_example_command_doit
    else:
        from prototype.test_commands_init import enter_example_command_doit
        
    enter_example_command_doit(glpane, example_command_classname)
    return

def enter_example_command_doit(glpane, example_command_classname):
    example_command_class = globals()[example_command_classname]
    example_command_class.commandName += 'x'
        # kluge to defeat _f_userEnterCommand (and now userEnterCommand)
        # comparison of commandName -- not sure if it works; pretty sure
        # it's needed for now
        # TODO: replace it with a new option to pass to that method.
    cmdrun = construct_cmdrun(example_command_class, glpane)
    start_cmdrun(cmdrun)
    return

def initialize():
    if (Initialize.startInitialization(__name__)):
        return
    
    # initialization code (note: it's all a kluge, could be cleaned up pretty easily)

    # Note: the global declarations are needed due to the kluge above
    # involving globals()[example_command_classname]
    
    classnames = [ ] # extended below

    global ExampleCommand1
    from prototype.test_commands import ExampleCommand1
    classnames.append("ExampleCommand1")

    global ExampleCommand2
    from prototype.test_commands import ExampleCommand2
    classnames.append("ExampleCommand2")

    global test_connectWithState
    from prototype.test_connectWithState import test_connectWithState
    classnames.append("test_connectWithState")

    global ExampleCommand2E
    from prototype.example_expr_command import ExampleCommand2E
    classnames.append("ExampleCommand2E")

    for classname in classnames:
        cmdname = classname # for now
        register_debug_menu_command( cmdname, (lambda widget, classname = classname: enter_example_command(widget, classname)) )
    
    Initialize.endInitialization(__name__)
    return

# end
