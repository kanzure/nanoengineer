# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
RotaryMotor_EditCommand.py

@author: Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
ninad 2007-10-09: Created. This deprecates 'RotoryMotorGenerator'
"""

import foundation.env as env
from utilities.Log   import redmsg, greenmsg, orangemsg
from model.jigs_motors import RotaryMotor
from operations.jigmakers_Mixin import atom_limit_exceeded_and_confirmed
from command_support.Motor_EditCommand import Motor_EditCommand

from commands.RotaryMotorProperties.RotaryMotorPropertyManager import RotaryMotorPropertyManager

class RotaryMotor_EditCommand(Motor_EditCommand):
    """
    The RotaryMotor_EditCommand class  provides an editCommand Object.
    The editCommand, depending on what client code needs it to do, may create
    a new rotary motor or it may be used for an existing rotary motor.
    """
    #Property Manager
    PM_class = RotaryMotorPropertyManager
    cmd = greenmsg("Rotary Motor: ")
    commandName = 'ROTARY_MOTOR'
    featurename = "Rotary Motor"

    def _gatherParameters(self):
        """
        Return all the parameters from the Rotary Motor Property Manager.
        """
        torque = self.propMgr.torqueDblSpinBox.value()
        initial_speed = self.propMgr.initialSpeedDblSpinBox.value()
        final_speed = self.propMgr.finalSpeedDblSpinBox.value()
        dampers_state = self.propMgr.dampersCheckBox.isChecked()
        enable_minimize_state = self.propMgr.enableMinimizeCheckBox.isChecked()
        color = self.struct.color
        atoms = self.win.assy.selatoms_list()


        return (torque,
                initial_speed,
                final_speed,
                dampers_state,
                enable_minimize_state,
                color,
                atoms)

    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type.
        Returns the type of the structure this editCommand supports.
        This is used in isinstance test.
        @see: EditCommand._getStructureType() (overridden here)
        """
        return RotaryMotor


    def _createStructure(self):
        """
        Create a Rotary Motor object. (The model object which this edit
        controller creates)
        """
        assert not self.struct

        atoms = self.win.assy.selatoms_list()

        atomNumberRequirementMet, logMessage = \
                                self._checkMotorAtomLimits(len(atoms))

        if atomNumberRequirementMet:
            self.win.assy.part.ensure_toplevel_group()
            motor = RotaryMotor(self.win.assy)
            motor.findCenterAndAxis(atoms, self.win.glpane)
            self.win.assy.place_new_jig(motor)
        else:
            motor = None
            env.history.message(redmsg(logMessage))

        return motor

    def _modifyStructure(self, params):
        """
        Modifies the structure (Rotary Motor) using the provided params.
        @param params: The parameters used as an input to modify the structure
                       (Rotary Motor created using this
                       RotaryMotor_EditCommand)
        @type  params: tuple
        """
        assert self.struct
        assert params
        assert len(params) == 7

        torque, initial_speed, final_speed, \
              dampers_state, enable_minimize_state, \
              color, atoms  = params

        numberOfAtoms = len(atoms)

        atomNumberRequirementMet, logMessage = \
                                self._checkMotorAtomLimits(numberOfAtoms)

        if not atomNumberRequirementMet:
            atoms = self.struct.atoms[:]
            logMessage = logMessage + " Motor will remain attached to the"\
                       " atoms listed in the 'Motor Atoms' list in this" \
                       " property manager"
            logMessage = orangemsg(logMessage)
            self.propMgr.updateMessage(logMessage)
            assert len(atoms) > 0

        self.struct.cancelled = False
        self.struct.torque = torque
        self.struct.initial_speed = initial_speed
        self.struct.speed = final_speed
        self.struct.dampers_enabled = dampers_state
        self.struct.enable_minimize = enable_minimize_state
        self.struct.color = color
        #Not sure if it is safe to do self.struct.atoms = atoms
        #Instead using 'setShaft method -- ninad 2007-10-09
        self.struct.setShaft(atoms)


        self.struct.findCenterAndAxis(atoms, self.win.glpane)

        self.propMgr.updateAttachedAtomListWidget(atomList = atoms)

        self.win.win_update() # Update model tree
        self.win.assy.changed()

    ##=====================================##

    def _checkMotorAtomLimits(self, numberOfAtoms):
        """
        Check if the number of atoms selected by the user, to which the motor
        is to be attached, is within acceptable limits.
        @param numberOfAtoms: Number of atoms selected by the user, to which the
                              motor needs to be attached.
        @type numberOfAtoms: int
        """
        logMessage = ""
        isAtomRequirementMet = False

        if numberOfAtoms == 0:
            logMessage = "No Atoms selected to create a Rotary Motor."
            isAtomRequirementMet = False
            return (isAtomRequirementMet, logMessage)

        # wware 051216, bug 1114, need >= 2 atoms for rotary motor
        if numberOfAtoms < 2:
            msg = redmsg("You must select at least two atoms to create"\
                         " a Rotary Motor.")
            logMessage = msg
            isAtomRequirementMet = False
            return (isAtomRequirementMet, logMessage)

        if numberOfAtoms >= 2 and numberOfAtoms < 200:
            isAtomRequirementMet = True
            logMessage = ""
            return (isAtomRequirementMet, logMessage)

        # Print warning if over 200 atoms are selected.
        # The warning should be displayed in a MessageGroupBox. Mark 2007-05-28
        if numberOfAtoms > 200:
            if not atom_limit_exceeded_and_confirmed(self.win,
                                                     numberOfAtoms,
                                                     limit = 200):
                logMessage = "Warning: Motor is attached to more than 200 "\
                           "atoms. This may result in a performance degradation"
                isAtomRequirementMet = True
            else:
                logMessage = "%s creation cancelled" % (self.cmdname)
                isAtomRequirementMet = False

            return (isAtomRequirementMet, logMessage)




