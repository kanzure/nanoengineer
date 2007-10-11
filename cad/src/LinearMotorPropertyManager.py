# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
LinearMotorPropertyManager.py

@author: Ninad
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

History:
ninad 2007-10-11: Created, deprecating the LinearMototorPropDialog.py
"""

from PyQt4.Qt import SIGNAL

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_PushButton    import PM_PushButton

from widgets import RGBf_to_QColor

from MotorPropertyManager import MotorPropertyManager


class LinearMotorPropertyManager(MotorPropertyManager):
    """
    The LinearMotorProperty manager class provides UI and propMgr object for the
    LinearMotorEditController.
    """
    # The title that appears in the Property Manager header.
    title = "Linear Motor"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Simulation/Linear_Motor.png"
    
    def __init__(self, win, motorEditController):
        """
        Construct the Linear Motor Property Manager.    
        """
                
        MotorPropertyManager.__init__( self, 
                                       win,
                                       motorEditController) 
    
    def change_motor_size(self, gl_update=True):
        """
        Slot method to change the jig's length, width and/or spoke radius.
        """
        self.struct.length = float(str(self.lengthLineEdit.text())) 
        self.struct.width = float(str(self.widthLineEdit.text())) 
        # spoke radius --
        self.struct.sradius = float(str(self.sradiusLineEdit.text())) 
        if gl_update:
            self.glpane.gl_update()
            
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in MotorParamsGroupBox.
        """                
        self.forceDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                             label = "Force:", 
                             value = self.struct.force, 
                             setAsDefault = True,
                             minimum    = 0.0, 
                             maximum    = 5000.0, 
                             singleStep = 1.0, 
                             decimals   = 1, 
                             suffix     =' pN')
        self.stiffnessDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                             label = "Stiffness:", 
                             value = self.struct.stiffness, 
                             setAsDefault = True,
                             minimum    = 0.0, 
                             maximum    = 1000.0, 
                             singleStep = 1.0, 
                             decimals   = 1, 
                             suffix     =' N/m')
                       
        self.enableMinimizeCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text ="Enable in Minimize",
                        widgetColumn = 1
                        )
        self.enableMinimizeCheckBox.setChecked(self.struct.enable_minimize)
        
        self.directionPushButton = \
            PM_PushButton(pmGroupBox,
                          label="Direction :",
                          text="Reverse",
                          spanWidth = False)
        
        self.connect(self.directionPushButton, 
                     SIGNAL("clicked()"), 
                     self.reverse_direction)
    
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in groubox 2.
        """
        
        self.motorLengthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Motor Length :", 
                                value = self.struct.length, 
                                setAsDefault = True,
                                minimum = 0.5, 
                                maximum = 500.0, 
                                singleStep = 0.5, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        self.connect(self.motorLengthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        
        self.motorWidthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label="Motor Width :", 
                                value = self.struct.width, 
                                setAsDefault = True,
                                minimum = 0.1, 
                                maximum = 50.0, 
                                singleStep = 0.1, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        self.connect(self.motorWidthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        
        self.spokeRadiusDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Spoke Radius :", 
                                value = self.struct.sradius, 
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
        self.jig_QColor = RGBf_to_QColor(self.struct.normcolor) 
        
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
        #self.nameLineEdit.setWhatsThis("""<b>Name</b><p>Name of Linear Motor 
        #that appears in the Model Tree</p>""")
        
        self.forceDblSpinBox.setWhatsThis("""<b>Force </b><p>Simulations 
        will begin with the motor's force set to this value.</p>""")
        
        self.enableMinimizeCheckBox.setWhatsThis("""<b>Enable in Minimize 
        <i>(WARNING: THIS IS EXPERIMENTAL FEATURE)</i></b>
        <p>If checked, the torque specified above will be applied to the 
        motor atoms during a structure minimization.  While intended to 
        allow simulations to begin with Linear motors running at speed, 
        this feature requires more work to be useful.</p>""")
