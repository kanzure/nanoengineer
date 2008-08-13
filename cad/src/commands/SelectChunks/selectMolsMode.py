# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
selectMolsMode.py

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Ninad 2007-02-16:   Split class selectMolsMode out of selectMode.py
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from
                          the old class selectMolsMode moving them into
                          their own module [ See SelectChunks_Command.py and
                          SelectChunks_GraphicsMode.py]
"""

from commands.SelectChunks.SelectChunks_Command import SelectChunks_basicCommand
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_basicGraphicsMode


class selectMolsMode(SelectChunks_basicCommand,
                     SelectChunks_basicGraphicsMode):
    """
    Select Chunks Mode (compatibility version for unsplit modes; deprecated)
    """
    def __init__(self, commandSequencer):
        glpane = commandSequencer.assy.glpane

        SelectChunks_basicCommand.__init__(self, commandSequencer)
            # was just basicCommand in original

        SelectChunks_basicGraphicsMode.__init__(self, glpane)
            # was just basicGraphicsMode in original
        return

    # (the rest would come from basicMode if post-inheriting it worked,
    #  or we could split it out of basicMode as a post-mixin to use there and
    #  here)

    def __get_command(self):
        return self

    command = property(__get_command)

    def __get_graphicsMode(self):
        return self

    graphicsMode = property(__get_graphicsMode)


    pass # end of class

# end
