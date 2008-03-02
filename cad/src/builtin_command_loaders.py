# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
builtin_command_loaders.py -- loaders for NE1 builtin commands.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Module classification: [bruce 080209]

For now, part of Command Sequencer package, since knows
the list of hardcoded commandnames the Command Sequencer uses
to let other code invoke builtin commands, and knows which
ones should be always loaded and in what order.

Someday, after refactoring, it might belong in ne1_startup.
(Maybe it even belongs there now.)

History:

Bruce 080209 split this out of GLPane.py (where it existed
for purely historical reasons). Semantically it was part
of the Command Sequencer, and it's now split out of there
too.

TODO:

Refactor the code that uses this data (in Command Sequencer)
so its _commandTable is a separate object with which
we register the loading code herein, so it can load
some commands lazily.
"""

from commands.BuildCrystal.cookieMode import cookieMode 
from commands.Extrude.extrudeMode import extrudeMode
from commands.Paste.PasteMode import PasteMode
from commands.PartLibrary.PartLibraryMode import PartLibraryMode
from commands.PlayMovie.movieMode import movieMode
from ZoomToAreaMode  import ZoomToAreaMode
from ZoomInOutMode   import ZoomInOutMode
from PanMode         import PanMode
from RotateMode      import RotateMode
from LineMode        import LineMode
from DnaLineMode     import DnaLineMode
from DnaDuplex_EditCommand import DnaDuplex_EditCommand
from commands.PlaneProperties.Plane_EditCommand import Plane_EditCommand
from commands.RotaryMotorProperties.RotaryMotor_EditCommand import RotaryMotor_EditCommand
from commands.LinearMotorProperties.LinearMotor_EditCommand import LinearMotor_EditCommand
from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_Command
from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command
from BreakStrands_Command     import BreakStrands_Command
from BuildDna_EditCommand    import BuildDna_EditCommand
from DnaSegment_EditCommand  import DnaSegment_EditCommand
from DnaStrand_EditCommand   import DnaStrand_EditCommand
from commands.Move.Move_Command import Move_Command
from commands.Rotate.RotateChunks_Command import RotateChunks_Command
from commands.Translate.TranslateChunks_Command import TranslateChunks_Command
from commands.Fuse.FuseChunks_Command import FuseChunks_Command
from JoinStrands_Command     import JoinStrands_Command
#from SketchMode    import SketchMode #Not implemented yet - 2007-10-25

def preloaded_command_classes():
    """
    Return a list of command classes for the commands which are always loaded
    on startup, and should always be reinitialized (in this order)
    when new command objects are needed.

    @note: currently this includes all loadable builtin commands,
           but soon we will implement a way for some commands to be
           loaded lazily, and remove many commands from this list.
    """
    # classes for builtin commands (or unsplit modes) which were preloaded
    # by toplevel imports above, in order of desired instantiation:
    command_classes = [
        SelectChunks_Command, 
        SelectAtoms_Command,
        BuildAtoms_Command,
        Move_Command,
        cookieMode, 
        extrudeMode, 
        movieMode, 
        ZoomToAreaMode, 
        ZoomInOutMode,
        PanMode, 
        RotateMode, 
        PasteMode, 
        PartLibraryMode, 
        LineMode, 
        DnaLineMode, 
        DnaDuplex_EditCommand,
        Plane_EditCommand,
        LinearMotor_EditCommand,
        RotaryMotor_EditCommand,
        BreakStrands_Command,
        JoinStrands_Command,
        BuildDna_EditCommand,
        DnaSegment_EditCommand, 
        DnaStrand_EditCommand,
        RotateChunks_Command,
        TranslateChunks_Command, 
        FuseChunks_Command,
        ##SketchMode, #Sketchmode not implemented yet
     ]
    # note: we could extract each one's commandName (class constant)
    # if we wanted to return them as commandName, commandClass pairs
    return command_classes

# end

