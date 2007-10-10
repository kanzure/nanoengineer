# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
modes.py -- provides basicMode, the superclass for old modes
which haven't yet been split into subclasses of Command and GraphicsMode.

$Id$


History:

(For earlier history see modes.py docstring before the split of 071009.)

bruce 050507 moved Hydrogenate and Dehydrogenate into another file

bruce 071009 moved modeMixin into its own file

bruce 071009 split modes.py into Command.py and GraphicsMode.py,
leaving only temporary compatibility mixins in modes.py.

TODO:

Sometime, separate public (API) and private methods within each of
Command.py and GraphicsMode.py (see their module docstrings for details).

Refactor the subclasses of basicMode, then get rid of it.
Same with the other classes in this file.

Notes on how we'll do that:

At some point soon we'll have one currentCommand attr in glpane,
later moved to a separate object, the command sequencer.
And glpane.mode will refer to a derived object
which the current command can return,
perhaps self (for old code) or not (for new code).
(The null object we store in there can then also be a joint or
separate object, independently from everything else. For now
it's still called nullMode (and it's created and stored by modeMixin)
but that will be revised.)

But that doesn't remove the fact that generators (maybe even when based on EditController)
still sort of treat their PM as a guest in some mode and as the "current command".
So "make generators their own command" will be a refactoring we need soon,
perhaps before "split old modes into their Command and GraphicsMode pieces".

But when we "make generators their own command", what GM will they use?
We might have to split one out of the old modes for that purpose
even though it can't yet replace the ones it splits out of.
"""

from constants import GLPANE_IS_COMMAND_SEQUENCER

from Command import anyCommand, nullCommand, basicCommand

from GraphicsMode import anyGraphicsMode, nullGraphicsMode, basicGraphicsMode

# ==

### TODO: fill these in, especially __init__ methods; remove the ones we don't need

class anyMode(anyCommand, anyGraphicsMode):
    # used only in this file (where it provides some default methods and attrs
    # to the classes here, but surely redundantly with their other
    # superclasses, so it's probably not needed),
    # and in old comments in other files.
    pass

class nullMode(nullCommand, nullGraphicsMode, anyMode):
    # used in modeMixin and test_commands
    # see discussion in this module's docstring
    pass

class basicMode(basicCommand, basicGraphicsMode, anyMode):
    """
    Compatibility mixture of Command and GraphicsMode
    for old code which uses one object for both.
    """
    def __init__(self, glpane):
        if GLPANE_IS_COMMAND_SEQUENCER:
            commandSequencer = glpane
        else:
            msg = "don't yet know how to find commandSequencer when not GLPANE_IS_COMMAND_SEQUENCER"
                # btw, glpane.win.commandSequencer doesn't work yet (in the case when they are the same)
            print msg
            assert 0, msg
        
        basicCommand.__init__(self, commandSequencer)
        
        basicGraphicsMode.__init__(self, glpane)
            # no need to pass self as command, due to property below
        
        return
    
    def __get_command(self):
        return self

    command = property(__get_command)

    def __get_graphicsMode(self):
        return self

    graphicsMode = property(__get_graphicsMode)
    
    pass # end of class basicMode

# end
