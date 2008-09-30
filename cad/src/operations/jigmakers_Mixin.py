# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
jigmakers_Mixin.py -- provides a mixin class to be inherited by class Part,
for providing operations for making specific kinds of Jigs, and associated
public helper functions.
 
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

071023 bruce split this out of jigs.py, to remove some needless
or misleading import dependencies on jigs.py.
"""

import sys

from PyQt4.Qt import QMessageBox

from utilities.Log import redmsg, greenmsg, orangemsg
import foundation.env as env
from model.jigs import Anchor
from model.jigs import Stat
from model.jigs import Thermo
from model.jigs import AtomSet


class jigmakers_Mixin:
    """
    Provide Jig-making methods to class Part.
    These should be refactored into some common code
    and new methods in the specific Jig subclasses.
    """

    def makeRotaryMotor(self):
        """
        Creates a Rotary Motor edit controller, whhich in turn creates a
        rotory motor connected to the selected atoms.
        """    
        atoms = self.win.assy.selatoms_list()
        #This check fixes bug 2697. Simply don't enter the command (to create 
        #a new motor), if the there aren't enough atoms selected.
        if len(atoms) < 2:
            logMessage = "To create a rotary motor, you must select at least" \
                " two atoms. Rotary motor not created"
            env.history.message(redmsg(logMessage))
            return
        
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('ROTARY_MOTOR')
        assert commandSequencer.currentCommand.commandName == 'ROTARY_MOTOR'
        commandSequencer.currentCommand.runCommand()
      
    def makeLinearMotor(self):
        """
        Creates a Linear Motor edit controller, which in turn creates a
        linear motor connected to the selected atoms.
        """ 
        
        atoms = self.win.assy.selatoms_list()
        
        #This check fixes bug 2697. Simply don't enter the command (to create 
        #a new motor), if the there aren't enough atoms selected.
        
        if len(atoms) < 1:
            logMessage = "To create a linear motor, you must select at least" \
                " one atom. Linear motor not created"
            env.history.message(redmsg(logMessage))
            return
                    
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('LINEAR_MOTOR')
        assert commandSequencer.currentCommand.commandName == 'LINEAR_MOTOR'
        commandSequencer.currentCommand.runCommand()

    def makegamess(self):
        """
        Makes a GAMESS jig from the selected chunks or atoms.
        """
        # [mark 2007-05-07 modified docstring]
        
        if sys.platform == "win32":
            gms_str = "PC GAMESS"
        else:
            gms_str = "GAMESS"
            
        cmd = greenmsg(gms_str + ": ")
        
        atoms = []
        
        # Get a list of atoms from the selected chunks or atoms.
        atoms = self.assy.selected_atoms_list(
            include_atoms_in_selected_chunks = True)
        
        if not atoms:
            msg = "At least one atom must be selected to create a " + \
                  gms_str + " jig."
            env.history.message(cmd + redmsg(msg))
            return
        
        # Make sure that no more than 200 atoms are selected.
        nsa = len(atoms)
        if nsa > 200:
            msg = str(nsa) + " atoms selected.  The limit is 200."
            env.history.message(cmd + redmsg(msg))
            return
        
        # Bug 742.    Mark 050731.
        if nsa > 50:
            ret = QMessageBox.warning( self.assy.w, "Too many atoms?",
                gms_str + " jigs with more than 50 atoms may take an\n"
                "excessively long time to compute (days or weeks).\n"
                "Are you sure you want to continue?",
                "&Continue", "Cancel", "",
                0, 1 )
                
            if ret == 1: # Cancel
                return
                
        from analysis.GAMESS.jig_Gamess import Gamess
        m = Gamess(self.assy, atoms)
        m.edit()
            #bruce 050701 split edit method out of the constructor, so the
            # dialog doesn't show up when the jig is read from an mmp file
        if m.cancelled: # User hit 'Cancel' button in the jig dialog.
            env.history.message(cmd + "Cancelled")
            return
        self.unpickall_in_GLPane()
        self.place_new_jig(m)
        
        env.history.message(cmd + gms_str + " jig created")
        self.assy.w.win_update()
        
    def makeAnchor(self):
        """
        Anchors the selected atoms so that they will not move
        during a minimization or simulation run.
        """        
        cmd = greenmsg("Anchor: ")

        atoms = self.assy.selatoms_list()
        
        if not atoms:
            msg = "You must select at least one atom to create an Anchor."
            env.history.message(cmd + redmsg(msg))
            return
        
        # Print warning if over 200 atoms are selected.
        if atom_limit_exceeded_and_confirmed(self.assy.w,
                                             len(atoms),
                                             limit=200):
            return

        m = Anchor(self.assy, atoms)
        self.unpickall_in_GLPane()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Anchor created")
        self.assy.w.win_update()

    def makestat(self):
        """
        Attaches a Langevin thermostat to the single atom selected.
        """
        cmd = greenmsg("Thermostat: ")

        atoms = self.assy.selatoms_list()
        
        if not atoms:
            msg = "You must select an atom on the chunk you want to " \
                  "associate with a Thermostat."
            env.history.message(cmd + redmsg(msg))
            return
        
        # Make sure only one atom is selected.
        if len(atoms) != 1: 
            msg = "To create a Thermostat, only one atom may be selected."
            env.history.message(cmd + redmsg(msg))
            return
        m = Stat(self.assy, atoms)
        self.unpickall_in_GLPane()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Thermostat created")
        self.assy.w.win_update()
        
    def makethermo(self):
        """
        Attaches a thermometer to the single atom selected.
        """
        cmd = greenmsg("Thermometer: ")

        atoms = self.assy.selatoms_list()
        
        if not atoms:
            msg = "You must select an atom on the chunk you want to " \
                  "associate with a Thermometer."
            env.history.message(cmd + redmsg(msg))
            return
        
        # Make sure only one atom is selected.
        if len(atoms) != 1: 
            msg = "To create a Thermometer, only one atom may be selected."
            env.history.message(cmd + redmsg(msg))
            return
        
        m = Thermo(self.assy, atoms)
        self.unpickall_in_GLPane()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Thermometer created")
        self.assy.w.win_update()
        
        
    def makeGridPlane(self):
        cmd = greenmsg("Grid Plane: ")

        atoms = self.assy.selatoms_list()
        
        if not atoms:
            msg = "You must select 3 or more atoms to create a Grid Plane."
            env.history.message(cmd + redmsg(msg))
            return
        
        # Make sure only one atom is selected.
        if len(atoms) < 3: 
            msg = "To create a Grid Plane, at least 3 atoms must be selected."
            env.history.message(cmd + redmsg(msg))
            return
        
        from model.jigs_planes import GridPlane
        m = GridPlane(self.assy, atoms)
        m.edit()
        if m.cancelled: # User hit 'Cancel' button in the jig dialog.
            env.history.message(cmd + "Cancelled")
            return 
        
        self.unpickall_in_GLPane()
        self.place_new_jig(m)
        
        #After placing the jig, remove the atom list from the jig.
        m.atoms = []
      
        env.history.message(cmd + "Grid Plane created")
        self.assy.w.win_update()
        return
        
    def makeESPImage(self):
        cmd = greenmsg("ESP Image: ")

        atoms = self.assy.selatoms_list()

        if len(atoms) < 3:
            msg = "You must select at least 3 atoms to create an ESP Image."
            env.history.message(cmd + redmsg(msg))
            return
        
        from analysis.ESP.ESPImage import ESPImage
        m = ESPImage(self.assy, atoms)
        m.edit()
        if m.cancelled: # User hit 'Cancel' button in the jig dialog.
            env.history.message(cmd + "Cancelled")
            return 
        
        self.unpickall_in_GLPane()
        self.place_new_jig(m)
        
        # After placing the jig, remove the atom list from the jig.
        m.atoms = []
        
        env.history.message(cmd + "ESP Image created.")
        self.assy.w.win_update()
        return
        
    def makeAtomSet(self):
        cmd = greenmsg("Atom Set: ")

        atoms = self.assy.selatoms_list()

        if not atoms:
            msg = "You must select at least one atom to create an Atom Set."
            env.history.message(cmd + redmsg(msg))
            return
            
        # Print warning if over 200 atoms are selected.
        if atom_limit_exceeded_and_confirmed(self.assy.w,
                                             len(atoms),
                                             limit = 200):
            return
        
        m = AtomSet(self.assy, atoms)
        
        self.place_new_jig(m)
        m.pick() # This is required to display the Atom Set wireframe boxes.
        
        env.history.message(cmd + "Atom Set created.")
        self.assy.w.win_update()
        return

    def makeMeasureDistance(self):
        """
        Creates a Measure Distance jig between two selected atoms.
        """
        
        cmd = greenmsg("Measure Distance Jig: ")

        atoms = self.assy.selatoms_list()

        if len(atoms) != 2:
            msg = "You must select 2 atoms to create a Distance jig."
            env.history.message(cmd + redmsg(msg))
            return
        
        from model.jigs_measurements import MeasureDistance
        d = MeasureDistance(self.assy, atoms)
        self.unpickall_in_GLPane()
        self.place_new_jig(d)
        
        env.history.message(cmd + "Measure Distance jig created")
        self.assy.w.win_update()


    def makeMeasureAngle(self):
        """
        Creates a Measure Angle jig connected to three selected atoms.
        """        
        cmd = greenmsg("Measure Angle Jig: ")

        atoms = self.assy.selatoms_list()

        if len(atoms) != 3:
            msg = "You must select 3 atoms to create an Angle jig."
            env.history.message(cmd + redmsg(msg))
            return
        
        from model.jigs_measurements import MeasureAngle
        d = MeasureAngle(self.assy, atoms)
        self.unpickall_in_GLPane()
        self.place_new_jig(d)
        
        env.history.message(cmd + "Measure Angle jig created")
        self.assy.w.win_update()

    def makeMeasureDihedral(self):
        """
        Creates a Measure Dihedral jig connected to three selected atoms.
        """
        cmd = greenmsg("Measure Dihedral Jig: ")

        atoms = self.assy.selatoms_list()

        if len(atoms) != 4:
            msg = "You must select 4 atoms to create a Dihedral jig."
            env.history.message(cmd + redmsg(msg))
            return
        
        from model.jigs_measurements import MeasureDihedral
        d = MeasureDihedral(self.assy, atoms)
        self.unpickall_in_GLPane()
        self.place_new_jig(d)
        
        env.history.message(cmd + "Measure Dihedral jig created")
        self.assy.w.win_update()
        
    pass # end of class jigmakers_Mixin

# ==

def atom_limit_exceeded_and_confirmed(parent, natoms, limit = 200):
    """
    Displays a warning message if 'natoms' exceeds 'limit'.
    Returns False if the number of atoms does not exceed the limit or if the
    user confirms that the jigs should still be created even though the limit
    was exceeded.
    If parent is 0, the message box becomes an application-global modal dialog
    box. 
    If parent is a widget, the message box becomes modal relative to parent.
    """
    if natoms < limit:
        return False # Atom limit not exceeded.

    wmsg = "Warning: Creating a jig with " + str(natoms) \
        + " atoms may degrade performance.\nDo you still want to add the jig?"
    
    dialog = QMessageBox("Warning", wmsg, 
                    QMessageBox.Warning, 
                    QMessageBox.Yes, 
                    QMessageBox.No, 
                    QMessageBox.NoButton, 
                    parent)

    # We want to add a "Do not show this message again." checkbox to the dialog
    # like this:
    #     checkbox = QCheckBox("Do not show this message again.", dialog)
    # The line of code above works, but places the checkbox in the upperleft
    # corner of the dialog, obscuring important text.  I'll fix this later.
    # Mark 051122.

    ret = dialog.exec_()

    if ret != QMessageBox.Yes:
        return True
    
    # Print warning msg in history widget whenever the user adds new jigs with
    # more than 'limit' atoms.
    wmsg = "Warning: " + str(natoms) + " atoms selected.  A jig with more " \
        "than " + str(limit) + " atoms may degrade performance."
    env.history.message(orangemsg(wmsg))
        
    return False # from atom_limit_exceeded_and_confirmed


# end
