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
         EditCommand API. (and related changes)
         
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
    RotaryMotor_EditCommand.
    """
    # The title that appears in the Property Manager header.
    title = "Rotary Motor"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Simulation/Rotary_Motor.png"
    
    def __init__(self, win, motorEditCommand):
        """
        Construct the Rotary Motor Property Manager.    
        """
                
        MotorPropertyManager.__init__( self, 
                                       win,
                                       motorEditCommand) 
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect
                
        MotorPropertyManager.connect_or_disconnect_signals(self, isConnect)
        
        change_connect(self.directionPushButton, 
                     SIGNAL("clicked()"), 
                     self.reverse_direction)
        change_connect(self.motorLengthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        change_connect(self.motorRadiusDblSpinBox, 
                    SIGNAL("valueChanged(double)"), 
                    self.change_motor_size)
        change_connect(self.spokeRadiusDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        change_connect(self.colorPushButton, 
                     SIGNAL("clicked()"), 
                     self.change_jig_color)
    
    def _update_widgets_in_PM_before_show(self):
        """
        Update various widgets  in this Property manager.
        Overrides MotorPropertyManager._update_widgets_in_PM_before_show. 
        The various  widgets , (e.g. spinboxes) will get values from the 
        structure for which this propMgr is constructed for 
        (self.editcCntroller.struct)
        
        @see: MotorPropertyManager._update_widgets_in_PM_before_show
        @see: self.show where it is called. 
        """       
        if self.editController and self.editController.struct:            
            torque = self.editController.struct.torque
            initial_speed = self.editController.struct.initial_speed
            final_speed = self.editController.struct.speed
            dampers_enabled = self.editController.struct.dampers_enabled
            enable_minimize = self.editController.struct.enable_minimize
            
            length = self.editController.struct.length
            radius = self.editController.struct.radius
            spoke_radius = self.editController.struct.sradius
            normcolor = self.editController.struct.normcolor
        else:
            torque = 0.0
            initial_speed = 0.0
            final_speed = 0.0
            dampers_enabled = False
            enable_minimize = False
            
            length = 10.0
            radius = 1.0
            spoke_radius = 0.2
            normcolor = gray
            
        self.torqueDblSpinBox.setValue(torque)
        self.initialSpeedDblSpinBox.setValue(initial_speed)
        self.finalSpeedDblSpinBox.setValue(final_speed)
        self.dampersCheckBox.setChecked(dampers_enabled)
        self.enableMinimizeCheckBox.setChecked(enable_minimize)
        
        self.motorLengthDblSpinBox.setValue(length)
        self.motorRadiusDblSpinBox.setValue(radius)
        self.spokeRadiusDblSpinBox.setValue(spoke_radius)
        self.jig_QColor = RGBf_to_QColor(normcolor)
            
    def change_motor_size(self, gl_update = True):
        """
        Slot method to change the jig's length, radius and/or spoke radius.
        """
        if self.editController and self.editController.struct:
            self.editController.struct.length = \
                self.motorLengthDblSpinBox.value()# motor length
            self.editController.struct.radius = \
                self.motorRadiusDblSpinBox.value() # motor radius
            self.editController.struct.sradius = \
                self.spokeRadiusDblSpinBox.value() # spoke radius
            
            if gl_update:
                self.glpane.gl_update()
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in MotorParamsGroupBox.
        """    
        if self.editController and self.editController.struct:
            torque = self.editController.struct.torque
            initial_speed = self.editController.struct.initial_speed
            final_speed = self.editController.struct.speed
            dampers_enabled = self.editController.struct.dampers_enabled
            enable_minimize = self.editController.struct.enable_minimize
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
        
        
    
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in groubox 2.
        """
        if self.editController and self.editController.struct:
            length = self.editController.struct.length
            radius = self.editController.struct.radius
            spoke_radius = self.editController.struct.sradius
            normcolor = self.editController.struct.normcolor
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
        
        
        # Used as default color by Color Chooser
        self.jig_QColor = RGBf_to_QColor(normcolor) 
        
        self.colorPushButton = \
            PM_PushButton(pmGroupBox,
                          label = "Color :",
                          text = "Choose...")
    
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        from gui.WhatsThisText_for_PropertyManagers import whatsThis_RotaryMotorPropertyManager
        whatsThis_RotaryMotorPropertyManager(self)
    

