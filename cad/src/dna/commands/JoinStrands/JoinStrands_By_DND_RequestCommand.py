# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
JoinStrands_By_DND_RequestCommand

This is a request command called whenever a user wants to join two strands by
drag and drop. (DND = Drag and Drop). During singletLeftDown of the current
graphicsMode, it calls this request command and then during left up, this
request command is exited. 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created to fix this bug reported by Mark:
1. Insert DNA.
2. Nick one of the strands using "Break Strands"
3. Heal nick using "Join Strands" (using drag-and-drop). This causes
the premature exit from "Join Strands".


TODO:
"""

from utilities.constants import CL_REQUEST
from dna.commands.JoinStrands.JoinStrands_GraphicsMode import JoinStrands_GraphicsMode
from dna.commands.JoinStrands.JoinStrands_Command import JoinStrands_Command

class JoinStrands_By_DND_RequestCommand(JoinStrands_Command):
    """
   
    Example: In this BuildDna_EditCommand (graphicsMode), if you want to
    join  two strands, upon 'singletLeftDown'  it enters
    JoinStrands_Command , also calling leftDown method of its graphicsmode.
    Now, when user releases theLMB, it calls
    JoinStrands_GraphicsMode.leftUp()  which in turn exits that command
    if the flag 'exit_command_on_leftUp' is set to True(to go back to the
    previous command user was in) .
    A lot of code that does bondpoint dragging is available in
    BuildAtoms_GraphicsMode, but it isn't in BuildDna_GraphicsMode
    (as it is a  SelectChunks_GraphicsMode superclass for lots of reasons)
    So, for some significant amount of time, we may continue to use
    this flag to temporarily enter/exit this command.
    @see: BuildDna_GraphicsMode.singletLeftDown()
    @see: ClickToJoinStrands_GraphicsMode.
    """
    
    command_level = CL_REQUEST
    commandName = 'JoinStrands_By_DND'
    featureName = 'JoinStrands_By_DND'
    GraphicsMode_class = JoinStrands_GraphicsMode
    
    
    command_should_resume_prevMode = True 
    command_has_its_own_PM = False
    
    
    pass
