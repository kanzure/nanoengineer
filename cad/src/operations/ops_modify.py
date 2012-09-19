# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
ops_modify.py provides modifySlotsMixin for MWsemantics,
with modify slot methods and related helper methods.

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Note: many ops_*.py files provide mixin classes for Part,
not for MWsemantics like this one.

History:

mark 2008-02-02 split this out of MWsemantics.py.
"""

from utilities import debug_flags
from utilities.debug import reload_once_per_event

class modifySlotsMixin:
    """
    Mixin class to provide modify-related methods for class MWsemantics.
    Has slot methods and their helper methods.
    """

    def modifyAdjustSel(self):
        """
        Adjust the current selection.
        """
        if debug_flags.atom_debug:
            print "debug: reloading sim_commandruns on each use, for development"
            import simulation.sim_commandruns as sim_commandruns
            reload_once_per_event(sim_commandruns)
        from simulation.sim_commandruns import Minimize_CommandRun
        cmdrun = Minimize_CommandRun( self, 'Sel', type = 'Adjust')
        cmdrun.run()
        return

    def modifyAdjustAll(self):
        """
        Adjust all atoms.
        """
        if debug_flags.atom_debug:
            print "debug: reloading sim_commandruns on each use, for development"
            import simulation.sim_commandruns as sim_commandruns
            reload_once_per_event(sim_commandruns)
        from simulation.sim_commandruns import Minimize_CommandRun
        cmdrun = Minimize_CommandRun( self, 'All', type = 'Adjust')
        cmdrun.run()
        return

    def modifyCheckAtomTypes(self):
        """
        Check Atom Types for all atoms.
        """
        from simulation.sim_commandruns import CheckAtomTypes_CommandRun
        cmdrun = CheckAtomTypes_CommandRun(self)
        cmdrun.run()
        return

    def modifyHydrogenate(self):
        """
        Add hydrogen atoms to each singlet in the selection.
        """
        self.assy.modifyHydrogenate()

    # remove hydrogen atoms from selected atoms/molecules
    def modifyDehydrogenate(self):
        """
        Remove all hydrogen atoms from the selection.
        """
        self.assy.modifyDehydrogenate()

    def modifyPassivate(self):
        """
        Passivate the selection by changing surface atoms to eliminate singlets.
        """
        self.assy.modifyPassivate()

    def modifyDeleteBonds(self):
        """
        Delete all bonds between selected and unselected atoms or chunks.
        """
        self.assy.modifyDeleteBonds()

    def modifyStretch(self):
        """
        Stretch/expand the selected chunk(s).
        """
        self.assy.Stretch()

    def modifySeparate(self):
        """
        Form a new chunk from the selected atoms.
        """
        self.assy.modifySeparate()

    def modifyMerge(self):
        """
        Create a single chunk from two of more selected chunks.
        """
        self.assy.merge()
        self.win_update()

    def makeChunkFromAtom(self):
        """
        Create a new chunk from the selected atoms.
        """
        self.assy.makeChunkFromSelectedAtoms()
        self.win_update()

    def modifyInvert(self):
        """
        Invert the atoms of the selected chunk(s).
        """
        self.assy.Invert()

    def modifyMirror(self):
        """
        Mirrors the selected chunks through a Plane (or Grid Plane).
        """
        self.assy.Mirror()

    def modifyAlignCommonAxis(self):
        """
        Align selected chunks to the computed axis of the first chunk.
        """
        self.assy.align()
        self.win_update()

    def modifyCenterCommonAxis(self):
        """
        Same as "Align to Common Axis", except that it moves all the selected
        chunks to the center of the first selected chunk after
        aligning/rotating the other chunks.
        """

        # This is still not fully implemented as intended.  Instead of moving all the selected
        # chunks to the center of the first selected chunk, I want to have them moved to the closest
        # (perpendicular) point of the first chunk's axis.  I've studied and understand the math involved;
        # I just need to implement the code.  I plan to ask Bruce for help since the two of us will get it
        # done much more quickly together than me doing it alone.
        # Mark 050829.

        self.assy.alignmove()
        self.win_update()
