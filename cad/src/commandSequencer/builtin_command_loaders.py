# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
builtin_command_loaders.py -- loaders for NE1 builtin commands, used in order.

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

from commands.BuildCrystal.BuildCrystal_Command import BuildCrystal_Command 
from commands.Extrude.extrudeMode import extrudeMode
from commands.Paste.PasteFromClipboard_Command import PasteFromClipboard_Command
from commands.PartLibrary.PartLibrary_Command import PartLibrary_Command
from commands.PlayMovie.movieMode import movieMode
from commands.PlaneProperties.Plane_EditCommand import Plane_EditCommand
from commands.RotaryMotorProperties.RotaryMotor_EditCommand import RotaryMotor_EditCommand
from commands.LinearMotorProperties.LinearMotor_EditCommand import LinearMotor_EditCommand
from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_Command
from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command
from commands.Move.Move_Command import Move_Command
from commands.Rotate.RotateChunks_Command import RotateChunks_Command
from commands.Translate.TranslateChunks_Command import TranslateChunks_Command
from commands.Fuse.FuseChunks_Command import FuseChunks_Command
from commands.StereoProperties.StereoProperties_Command import StereoProperties_Command
# Urmi background color chooser PM 080523
from commands.ColorScheme.ColorScheme_Command import ColorScheme_Command
from commands.LightingScheme.LightingScheme_Command import LightingScheme_Command
from commands.StereoProperties.StereoProperties_Command import StereoProperties_Command
from commands.QuteMol.QuteMol_Command import QuteMol_Command

from temporary_commands.ZoomToAreaMode import ZoomToAreaMode
from temporary_commands.ZoomInOutMode import ZoomInOutMode
from temporary_commands.PanMode import PanMode
from temporary_commands.RotateMode import RotateMode
from temporary_commands.Line.LineMode import LineMode
from temporary_commands.RotateAboutPoint_Command import RotateAboutPoint_Command

#Carbon nanotube command imports 
from cnt.commands.BuildNanotube.BuildNanotube_EditCommand import BuildNanotube_EditCommand
from cnt.commands.InsertNanotube.InsertNanotube_EditCommand import InsertNanotube_EditCommand
from cnt.commands.NanotubeSegment.NanotubeSegment_EditCommand import NanotubeSegment_EditCommand

#DNA command imports =======

from dna.commands.BuildDna.BuildDna_EditCommand     import BuildDna_EditCommand
from dna.commands.BuildDuplex.DnaDuplex_EditCommand import DnaDuplex_EditCommand
from dna.commands.DnaSegment.DnaSegment_EditCommand import DnaSegment_EditCommand
from dna.commands.DnaStrand.DnaStrand_EditCommand   import DnaStrand_EditCommand
from dna.commands.MakeCrossovers.MakeCrossovers_Command import MakeCrossovers_Command
from dna.commands.BreakStrands.BreakStrands_Command import BreakStrands_Command
from dna.commands.JoinStrands.JoinStrands_Command import JoinStrands_Command
from dna.commands.OrderDna.OrderDna_Command       import OrderDna_Command
from dna.commands.DnaDisplayStyle.DnaDisplayStyle_Command import DnaDisplayStyle_Command
from dna.commands.MultipleDnaSegmentResize.MultipleDnaSegmentResize_EditCommand import MultipleDnaSegmentResize_EditCommand
from dna.temporary_commands.DnaLineMode             import DnaLineMode

# Protein command imports
from protein.commands.BuildPeptide.Peptide_EditCommand import Peptide_EditCommand
from protein.commands.BuildProtein.BuildProtein_EditCommand import BuildProtein_EditCommand
from protein.commands.ProteinDisplayStyle.ProteinDisplayStyle_Command import ProteinDisplayStyle_Command
from protein.commands.EditRotamers.EditRotamers_Command import EditRotamers_Command
from protein.commands.EditResidues.EditResidues_Command import EditResidues_Command
from protein.commands.CompareProteins.CompareProteins_Command import CompareProteins_Command

from protein.commands.ModelAndSimulateProtein.ModelAndSimulateProtein_Command import ModelAndSimulateProtein_Command
from protein.commands.ModelAndSimulateProtein.ModelProtein_Command import ModelProtein_Command
from protein.commands.ModelAndSimulateProtein.SimulateProtein_Command import SimulateProtein_Command
from protein.commands.FixedBBProteinSim.FixedBBProteinSim_Command import FixedBBProteinSim_Command
from protein.commands.BackrubProteinSim.BackrubProteinSim_Command import BackrubProteinSim_Command
#Graphene commands 
from commands.InsertGraphene.Graphene_EditCommand import Graphene_EditCommand

from commands.BuildAtoms.BondTool_Command import SingleBondTool
from commands.BuildAtoms.BondTool_Command import DoubleBondTool
from commands.BuildAtoms.BondTool_Command import TripleBondTool
from commands.BuildAtoms.BondTool_Command import AromaticBondTool
from commands.BuildAtoms.BondTool_Command import GraphiticBondTool
from commands.BuildAtoms.BondTool_Command import DeleteBondTool
from commands.BuildAtoms.BondTool_Command import BondTool_Command
from commands.BuildAtoms.AtomsTool_Command import AtomsTool_Command

def preloaded_command_classes():
    """
    Return a list of command classes for the commands which are always loaded
    on startup, and should always be reinitialized (in this order)
    when new command objects are needed.

    @note: currently this includes all loadable builtin commands,
           but soon we will implement a way for some commands to be
           loaded lazily, and remove many commands from this list.

    @note: commands should be initialized in this order, in case this makes
           some bugs deterministic. In theory, any order should work (and it's
           a bug if it doesn't), but in practice, we have found that some
           mysterious Qt bugs (C crashes) depend on which command classes are
           instantiated at startup, so it seems safest to keep all this
           deterministic, even at the cost of failing to detect our own
           order-dependency bugs if any creep in.
    """
    # classes for builtin commands (or unsplit modes) which were preloaded
    # by toplevel imports above, in order of desired instantiation:
    command_classes = [
        SelectChunks_Command, 
        SelectAtoms_Command,
        BuildAtoms_Command,
        Move_Command,
        BuildCrystal_Command, 
        extrudeMode, 
        movieMode, 
        ZoomToAreaMode, 
        ZoomInOutMode,
        PanMode, 
        RotateMode, 
        PasteFromClipboard_Command, 
        PartLibrary_Command, 
        LineMode, 
        DnaLineMode, 
        DnaDuplex_EditCommand,
        Plane_EditCommand,
        LinearMotor_EditCommand,
        RotaryMotor_EditCommand,
        BreakStrands_Command,
        JoinStrands_Command,
        MakeCrossovers_Command,
        BuildDna_EditCommand,
        DnaSegment_EditCommand, 
        DnaStrand_EditCommand,
        MultipleDnaSegmentResize_EditCommand,
        OrderDna_Command,
        DnaDisplayStyle_Command,
        BuildNanotube_EditCommand,
        InsertNanotube_EditCommand,
        NanotubeSegment_EditCommand, 
        Graphene_EditCommand,
        RotateChunks_Command,
        TranslateChunks_Command, 
        FuseChunks_Command,
        RotateAboutPoint_Command,        
        StereoProperties_Command,
        QuteMol_Command,
        ColorScheme_Command,
        Peptide_EditCommand,
        BuildProtein_EditCommand,
        ProteinDisplayStyle_Command,
        LightingScheme_Command,
        EditRotamers_Command,
        EditResidues_Command,
        CompareProteins_Command,
        ModelProtein_Command,
        SimulateProtein_Command,
        ModelAndSimulateProtein_Command,
        FixedBBProteinSim_Command,
        BackrubProteinSim_Command,
        #Tools in Build Atoms command --
        SingleBondTool,
        DoubleBondTool,
        TripleBondTool,
        AromaticBondTool,
        GraphiticBondTool,
        DeleteBondTool, 
        AtomsTool_Command, 
        BondTool_Command
    ]
    
    # note: we could extract each one's commandName (class constant)
    # if we wanted to return them as commandName, commandClass pairs
    return command_classes

# end

