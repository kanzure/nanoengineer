# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
RotaryMotorGenerator.py

$Id$

History:

Mark 2007-05-27: Created.
"""

__author__ = "Mark"

from utilities.Log import greenmsg

from PyQt4.Qt import QDialog
from RotaryMotorGeneratorDialog import RotaryMotorPropMgr
from command_support.GeneratorBaseClass import GeneratorBaseClass

# RotaryMotorPropMgr must come BEFORE GeneratorBaseClass in this list.
class RotaryMotorGenerator(RotaryMotorPropMgr, GeneratorBaseClass):
    """The Rotary Motor Generator class.
    """

    cmd = greenmsg("Insert Rotary Motor: ")
    #
    prefix = '' # Not used by jigs.
    # All jigs like rotary and linear motors already created their
    # name, so do not (re)create it (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix = False
    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')
    sponsor_keyword = 'RotaryMotor'

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win, motor, glpane):

        self.jig = motor
        self.name = motor.name # Adopt the motor's name as our name.

        RotaryMotorPropMgr.__init__(self, motor, glpane)
        GeneratorBaseClass.__init__(self, win)

        # Display Rotary Motor. Mark 2007-05-28.
        self.preview_btn_clicked() # Kludge? Works though.

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        """Return all the parameters from the Property Manager.
        """

        torque = self.torqueDblSpinBox.value()
        initial_speed = self.initialSpeedDblSpinBox.value()
        final_speed = self.finalSpeedDblSpinBox.value()
        dampers_state = self.dampersCheckBox.isChecked()
        enable_minimize_state = self.enableMinimizeCheckBox.isChecked()
        color = self.jig.color
        atoms = self.jig.atoms[:]
        #atoms = self.selectedAtomsListWidget.atoms

        if 1:
            print "\n---------------------------------------------------" \
                  "\ngather_parameters(): "\
                  "\ntorque = ", torque, \
                  "\ninitial_speed = ", initial_speed, \
                  "\nfinal_speed = ", final_speed, \
                  "\ndampers_state = ", dampers_state, \
                  "\nenable_minimize_state = ", enable_minimize_state, \
                  "\ncolor = ", color, \
                  "\natoms = ", atoms

        return (torque, initial_speed, final_speed,
                dampers_state, enable_minimize_state,
                color, atoms)

    def build_struct(self, name, params, position):
        """Build and return a new rotary motor from the parameters in the Property Manager.
        """

        torque, initial_speed, final_speed, \
        dampers_state, enable_minimize_state, \
        color, atoms = params

        self.jig.cancelled = False
        self.jig.torque = torque
        self.jig.initial_speed = initial_speed
        self.jig.speed = final_speed
        self.jig.dampers_enabled = dampers_state
        self.jig.enable_minimize = enable_minimize_state
        self.jig.color = color
        self.jig.atoms = atoms

        if 1:
            print "\n---------------------------------------------------" \
                  "\nbuild_struct(): "\
                  "\ntorque = ", self.jig.torque, \
                  "\ninitial_speed = ", self.jig.initial_speed, \
                  "\nfinal_speed = ", self.jig.speed, \
                  "\ndampers_state = ", self.jig.dampers_enabled, \
                  "\nenable_minimize_state =", self.jig.enable_minimize, \
                  "\ncolor = ", self.jig.color, \
                  "\natoms = ", self.jig.atoms

        return self.jig

