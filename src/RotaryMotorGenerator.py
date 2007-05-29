# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
RotaryMotorGenerator.py

$Id$

History:

Mark 2007-05-27: Created.
"""

__author__ = "Mark"

from HistoryWidget import greenmsg

from PyQt4.Qt import QDialog
from RotaryMotorGeneratorDialog import RotaryMotorPropMgr
from GeneratorBaseClass import GeneratorBaseClass

# RotaryMotorPropMgr must come BEFORE GeneratorBaseClass in this list.
class RotaryMotorGenerator(QDialog, RotaryMotorPropMgr, GeneratorBaseClass):
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
        
        self.name = motor.name # Adopt the motor's name as our name.
        
        QDialog.__init__(self, win)
        RotaryMotorPropMgr.__init__(self, motor, glpane)
        GeneratorBaseClass.__init__(self, win)

        # Display Rotary Motor. Mark 2007-05-28.
        self.preview_btn_clicked() # Kludge? Works, except the selected atoms loose selection wireframe(s).

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        """Return all the parameters from the Property Manager.
        """
        #name = self.nameLineEdit.text() # Removed from propmgr. Mark 2007-05-28
        torque = self.torqueDblSpinBox.value()
        initial_speed = self.initialSpeedDblSpinBox.value()
        final_speed = self.finalSpeedDblSpinBox.value()
        dampers_state = self.dampersCheckBox.isChecked()
        enable_minimize_state = self.enableMinimizeCheckBox.isChecked()

        return (torque, initial_speed, final_speed, dampers_state, enable_minimize_state)
    
    def build_struct(self, name, params, position):
        """Build a rotary motor from the parameters in the Property Manager.
        """
        
        #name, torque, initial_speed, final_speed, dampers_state, enable_minimize_state = params
        torque, initial_speed, final_speed, dampers_state, enable_minimize_state = params
        
        self.jig.cancelled = False
        #self.jig.try_rename(name) # Removed from propmgr. Mark 2007-05-28
        self.jig.torque = torque
        self.jig.initial_speed = initial_speed
        self.jig.speed = final_speed
        
        self.change_motor_size(gl_update=False)
        
        self.jig.dampers_enabled = dampers_state
        self.jig.enable_minimize = enable_minimize_state
        
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        
        return self.jig