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
from PM.PM_ColorComboBox import PM_ColorComboBox

from utilities.constants import gray

from command_support.MotorPropertyManager import MotorPropertyManager


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
    iconPath = "ui/actions/Simulation/RotaryMotor.png"
    
       
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
        change_connect(self.motorColorComboBox, 
                SIGNAL("editingFinished()"), 
                self.change_jig_color) 
        return
    
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
        if self.command and self.command.struct:            
            torque = self.command.struct.torque
            initial_speed = self.command.struct.initial_speed
            final_speed = self.command.struct.speed
            dampers_enabled = self.command.struct.dampers_enabled
            enable_minimize = self.command.struct.enable_minimize
            
            length = self.command.struct.length
            radius = self.command.struct.radius
            spoke_radius = self.command.struct.sradius
            normcolor = self.command.struct.normcolor
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
        return
    
    def change_motor_size(self, gl_update = True):
        """
        Slot method to change the jig's length, radius and/or spoke radius.
        """
        if self.command and self.command.struct:
            self.command.struct.length = \
                self.motorLengthDblSpinBox.value()# motor length
            self.command.struct.radius = \
                self.motorRadiusDblSpinBox.value() # motor radius
            self.command.struct.sradius = \
                self.spokeRadiusDblSpinBox.value() # spoke radius
            
            if gl_update:
                self.glpane.gl_update()
        return
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in MotorParamsGroupBox.
        """    
        if self.command and self.command.struct:
            torque = self.command.struct.torque
            initial_speed = self.command.struct.initial_speed
            final_speed = self.command.struct.speed
            dampers_enabled = self.command.struct.dampers_enabled
            enable_minimize = self.command.struct.enable_minimize
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
                                label = "Initial speed :", 
                                value = initial_speed, 
                                setAsDefault = True,
                                minimum    = 0.0, 
                                maximum    = 100.0, 
                                singleStep = 1.0, 
                                decimals   = 1, 
                                suffix     = ' GHz')
        
        self.finalSpeedDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                                label = "Final speed :", 
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
                        text = "Enable in minimize",
                        widgetColumn = 0
                        )
        self.enableMinimizeCheckBox.setChecked(enable_minimize)
        
        self.directionPushButton = \
            PM_PushButton(pmGroupBox,
                          label = "Direction :",
                          text = "Reverse",
                          spanWidth = False)
        return
    
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in groubox 2.
        """
        if self.command and self.command.struct:
            length = self.command.struct.length
            radius = self.command.struct.radius
            spoke_radius = self.command.struct.sradius
            normcolor = self.command.struct.normcolor
        else:
            length = 10
            radius = 1
            spoke_radius = 0.2
            normcolor = gray

        self.motorLengthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Motor length :", 
                                value = length, 
                                setAsDefault = True,
                                minimum = 0.5, 
                                maximum = 500.0, 
                                singleStep = 0.5, 
                                decimals = 1, 
                                suffix = ' Angstroms')

        self.motorRadiusDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label="Motor radius :", 
                                value = radius, 
                                setAsDefault = True,
                                minimum = 0.1, 
                                maximum = 50.0, 
                                singleStep = 0.1, 
                                decimals = 1, 
                                suffix = ' Angstroms')

        self.spokeRadiusDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Spoke radius :", 
                                value = spoke_radius, 
                                setAsDefault = True,
                                minimum = 0.1, 
                                maximum = 50.0, 
                                singleStep = 0.1, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        self.motorColorComboBox = \
            PM_ColorComboBox(pmGroupBox,
                             color = normcolor)
        return
    
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_RotaryMotorPropertyManager
        whatsThis_RotaryMotorPropertyManager(self)
        return
        
    def _addToolTipText(self):
        """
        What's Tool Tip text for widgets in this Property Manager.  
        """       
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_RotaryMotorPropertyManager
        ToolTip_RotaryMotorPropertyManager(self)
        return


