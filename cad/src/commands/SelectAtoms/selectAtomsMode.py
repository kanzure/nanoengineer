# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
selectAtomsMode.py 

$Id$


History:

Some things that need cleanup in this code [bruce 060721 comment]: ####@@@@
- redundant use of glRenderMode (see comment where that is used)

- drag algorithms for various object types and modifier keys are split over
lots of methods with lots of common but not identical code. For example, a
set of atoms and jigs can be dragged in the same way, by two different
pieces of code depending on whether an atom or jig in the set was clicked
on. If this was cleaned up, so that objects clicked on would answer
questions about how to drag them, and if a drag_handler object was created
to handle the drag (or the object itself can act as one, if only it is
dragged and if it knows how), the code would be clearer, some bugs would be
easier to fix, and some NFRs easier to implement. [bruce 060728 -- I'm
adding drag_handlers for use by new kinds of draggable or buttonlike things
(only in selectAtoms mode and subclasses), but not changing how old dragging
code works.]

Ninad 2007-02-16: Split selectAtomsMode class out of selectMode.py 
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from 
                          the old class selectAtomsMode moving them into
                          their own module [ See SelectAtoms_command.py and 
                          SelectAtoms_GraphicsMode.py]

"""

from utilities.debug import print_compact_traceback
from utilities.constants import GLPANE_IS_COMMAND_SEQUENCER

from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_basicCommand
from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_basicGraphicsMode

class selectAtomsMode(SelectAtoms_basicCommand, 
                      SelectAtoms_basicGraphicsMode):
    """
    Select Atoms Mode
    """   
    def __init__(self, glpane):
        assert GLPANE_IS_COMMAND_SEQUENCER
        
        commandSequencer = glpane
        
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

