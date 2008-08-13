# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
depositMode.py -- Build Atoms mode.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: As of 2007-01-04
- Items listed in BuildAtoms_GraphicsMode
- Items listed in Select_GraphicsMode.py 

History:
depositMode.py Originally by Josh Hall and then significantly modified by 
several developers. 

In January 2008, the old depositMode class was split into new Command and 
GraphicsMode parts and the these classes were moved into their own module 
[ See BuildAtoms_Command.py and BuildAtoms_GraphicsMode.py]
"""

from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_basicCommand
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_basicGraphicsMode

class depositMode( BuildAtoms_basicCommand,
                   BuildAtoms_basicGraphicsMode):
    # this class (and file) is no longer needed except by testmode [as of before 080812]
    """
    Build Atoms Mode (hybrid object which encompasses both - command and 
    graphicsMode objects as self)
    """   
    def __init__(self, commandSequencer):
        glpane = commandSequencer.assy.glpane
        
        BuildAtoms_basicCommand.__init__(self, commandSequencer)
            # was just basicCommand in original
        
        BuildAtoms_basicGraphicsMode.__init__(self, glpane)
            # was just basicGraphicsMode in original
        return

    # (the rest would come from basicMode if post-inheriting it worked,
    #  or we could split it out of basicMode as a post-mixin to use there 
    #  and here)
    
    def __get_command(self):
        return self

    command = property(__get_command)

    def __get_graphicsMode(self):
        return self

    graphicsMode = property(__get_graphicsMode)
    
