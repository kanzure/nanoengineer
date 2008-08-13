# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
selectAtomsMode.py 

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Ninad 2007-02-16: Split selectAtomsMode class out of selectMode.py 
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from 
                          the old class selectAtomsMode moving them into
                          their own module [ See SelectAtoms_command.py and 
                          SelectAtoms_GraphicsMode.py]
"""

from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_basicCommand
from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_basicGraphicsMode

class selectAtomsMode(SelectAtoms_basicCommand, 
                      SelectAtoms_basicGraphicsMode):
    """
    Select Atoms Mode
    """   
    def __init__(self, commandSequencer):
        glpane = commandSequencer.assy.glpane
        
        SelectAtoms_basicCommand.__init__(self, commandSequencer)
            # was just basicCommand in original
        
        SelectAtoms_basicGraphicsMode.__init__(self, glpane)
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

