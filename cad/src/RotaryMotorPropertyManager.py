# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
RotaryMotorPropertyManager.py

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

History:

Mark 2007-05-28: Created as RotaryMotorGeneratorDialog.py
Ninad 2007-10-09: 
       - Deprecated RotaryMotorGeneratorDialog class
       - Created RotaryMotorPropertyManager class to match the 
         EditController API. (and related changes)
         
"""

from PyQt4.Qt import SIGNAL

from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_PushButton    import PM_PushButton

from widgets import RGBf_to_QColor
from constants import gray

from MotorPropertyManager import MotorPropertyManager


class RotaryMotorPropertyManager(MotorPropertyManager):
    """
    The RotaryMotorProperty manager class provides UI and propMgr object for the
    RotaryMotorEditController.
    """
    # The title that appears in the Property Manager header.
    title = "Rotary Motor"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Simulation/Rotary_Motor.png"
    
    def __init__(self, win, motorEditController):
        """
        Construct the Rotary Motor Property Manager.    
        """
                
        MotorPropertyManager.__init__( self, 
                                       win,
                                       motorEditController) 
                           

    def change_motor_size(self, gl_update = True):
        """
        Slot method to change the jig's length, radius and/or spoke radius.
        """
        self.struct.length = self.motorLengthDblSpinBox.value()# motor length
        self.struct.radius = self.motorRadiusDblSpinBox.value() # motor radius
        self.struct.sradius = self.spokeRadiusDblSpinBox.value() # spoke radius
        if gl_update:
            self.glpane.gl_update()
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in MotorParamsGroupBox.
        """      
        if self.struct:
            torque = self.struct.torque
            initial_speed = self.struct.initial_speed
            final_speed = self.struct.speed
            dampers_enabled = self.struct.dampers_enabled
            enable_minimize = self.struct.enable_minimize
        else:
            torque = 0.0
            initial_speed = 0.0
            final_speed = 0.0
            dampers_enabled = False
            enable_minimize = False
        
        self.torqueDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Torque :", 
                                value = torque, 
                                setAsDefault = True,
                                minimum    = 0.0, 
                                maximum    = 1000.0, 
                                singleStep = 1.0, 
                                decimals   = 1, 
                                suffix     =' nN-nm')
        
        self.initialSpeedDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                                label = "Initial Speed :", 
                                value = initial_speed, 
                                setAsDefault = True,
                                minimum    = 0.0, 
                                maximum    = 100.0, 
                                singleStep = 1.0, 
                                decimals   = 1, 
                                suffix     = ' GHz')
        
        self.finalSpeedDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                                label = "Final Speed :", 
                                value = final_speed, 
                                setAsDefault = True,
                                minimum  = 0.0, 
                                maximum  = 100.0, 
                                singleStep = 1.0, 
                                decimals = 1, 
                                suffix = ' GHz')
        
        self.dampersCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text = "Dampers",
                        widgetColumn = 0
                        )
                              
        
        self.dampersCheckBox.setChecked(dampers_enabled)
        
        self.enableMinimizeCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text = "Enable in Minimize",
                        widgetColumn = 0
                        )
        self.enableMinimizeCheckBox.setChecked(enable_minimize)
        
        self.directionPushButton = \
            PM_PushButton(pmGroupBox,
                          label = "Direction :",
                          text = "Reverse",
                          spanWidth = False)
        
        self.connect(self.directionPushButton, 
                     SIGNAL("clicked()"), 
                     self.reverse_direction)
    
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in groubox 2.
        """
        if self.struct:
            length = self.struct.length
            radius = self.struct.radius
            spoke_radius = self.struct.sradius
            normcolor = self.struct.normcolor
        else:
            length = 10
            radius = 1
            spoke_radius = 0.2
            normcolor = gray
            
        
        self.motorLengthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Motor Length :", 
                                value = length, 
                                setAsDefault = True,
                                minimum = 0.5, 
                                maximum = 500.0, 
                                singleStep = 0.5, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        self.connect(self.motorLengthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        
        self.motorRadiusDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label="Motor Radius :", 
                                value = radius, 
                                setAsDefault = True,
                                minimum = 0.1, 
                                maximum = 50.0, 
                                singleStep = 0.1, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        self.connect(self.motorRadiusDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        
        self.spokeRadiusDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Spoke Radius :", 
                                value = spoke_radius, 
                                setAsDefault = True,
                                minimum = 0.1, 
                                maximum = 50.0, 
                                singleStep = 0.1, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        self.connect(self.spokeRadiusDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        # Used as default color by Color Chooser
        self.jig_QColor = RGBf_to_QColor(normcolor) 
        
        self.colorPushButton = \
            PM_PushButton(pmGroupBox,
                          label = "Color :",
                          text = "Choose...")
        
        self.connect(self.colorPushButton, 
                     SIGNAL("clicked()"), 
                     self.change_jig_color)
        

    def _addWhatsThisText(self):
        """
        What's This text for some of the widgets in the Property Manager.
        """
        
        # Removed name field from property manager. Mark 2007-05-28
        #self.nameLineEdit.setWhatsThis("""<b>Name</b><p>Name of Rotary Motor 
        #that appears in the Model Tree</p>""")
        
        self.torqueDblSpinBox.setWhatsThis("""<b>Torque </b><p>Simulations 
        will begin with the motor's torque set to this value.</p>""")
        
        self.initialSpeedDblSpinBox.setWhatsThis("""<b>Initial Speed</b> 
        <p>Simulations will begin with the motor's flywheel rotating at 
        this velocity.</p>""")
        
        self.finalSpeedDblSpinBox.setWhatsThis("""<b>Final Speed</b><p>The final
        velocity of the motor's flywheel during simulations.</p>""")
        
        self.dampersCheckBox.setWhatsThis("""<b>Dampers</b><p>If checked, 
        the dampers are enabled for this motor during a simulation. 
        See the Rotary Motor web page on the NanoEngineer-1 Wiki for 
        more information.</p>""")
        
        self.enableMinimizeCheckBox.setWhatsThis("""<b>Enable in Minimize 
        <i>(experimental)</i></b>
        <p>If checked, the torque specified above will be applied to the 
        motor atoms during a structure minimization.  While intended to 
        allow simulations to begin with rotary motors running at speed, 
        this feature requires more work to be useful.</p>""")

