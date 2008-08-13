# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
selectMode.py -- Select Chunks and Select Atoms modes,
also used as superclasses for some other modes

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

- Ninad 070216 moved selectAtomsMode and selectMolsMode out of selectMode.py
"""

from commands.Select.Select_Command import Select_basicCommand
from commands.Select.Select_GraphicsMode import Select_basicGraphicsMode

from command_support.modes import anyMode

class selectMode(Select_basicCommand, 
                 Select_basicGraphicsMode,
                 anyMode):                            
    """
    """
    # NOTE: Inheriting from superclass anymode is harmless. It is done as 
    # Not sure whether it's needed. It is put in case there is an isinstance 
    # assert in other code
    # Ignore it for now, because it will go away when everything is split and
    # we simplify these split modes to have only the main two classes.
    
    def __init__(self, commandSequencer):
        glpane = commandSequencer.assy.glpane
        
        Select_basicCommand.__init__(self, commandSequencer)
            # was just basicCommand in original
        
        Select_basicGraphicsMode.__init__(self, glpane)
            # was just basicGraphicsMode in original
        return

    # (the rest would come from basicMode if post-inheriting it worked,
    #  or we could split it out of basicMode as a post-mixin to use there and here)
    
    def __get_command(self):
        return self

    command = property(__get_command)

    def __get_graphicsMode(self):
        return self

    graphicsMode = property(__get_graphicsMode)
    
