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
from PM.PM_ColorComboBox import PM_ColorComboBox

from command_support.MotorPropertyManager import MotorPropertyManager

from utilities.constants import gray

class LinearMotorPropertyManager(MotorPropertyManager):
    """
    The LinearMotorProperty manager class provides UI and propMgr object for the
    LinearMotor_EditCommand.
    """
    # The title that appears in the Property Manager header.
    title = "Linear Motor"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Simulation/LinearMotor.png"

    
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
        change_connect(self.motorWidthDblSpinBox,
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
            force = self.command.struct.force
            stiffness = self.command.struct.stiffness
            enable_minimize = self.command.struct.enable_minimize

            length = self.command.struct.length
            width = self.command.struct.width
            spoke_radius = self.command.struct.sradius
            normcolor = self.command.struct.normcolor
        else:
            force = 0.0
            stiffness = 0.0
            enable_minimize = False

            length = 10
            width = 1
            spoke_radius = 0.2
            normcolor = gray

        self.forceDblSpinBox.setValue(force)
        self.stiffnessDblSpinBox.setValue(stiffness)
        self.enableMinimizeCheckBox.setChecked(enable_minimize)

        self.motorLengthDblSpinBox.setValue(length)
        self.motorWidthDblSpinBox.setValue(width)
        self.spokeRadiusDblSpinBox.setValue(spoke_radius)
        return
    
    def change_motor_size(self, gl_update=True):
        """
        Slot method to change the jig's length, width and/or spoke radius.
        """
        self.command.struct.length = self.motorLengthDblSpinBox.value()
        self.command.struct.width =  self.motorWidthDblSpinBox.value()
        # spoke radius --
        self.command.struct.sradius = self.spokeRadiusDblSpinBox.value()
        if gl_update:
            self.glpane.gl_update()
        return

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in MotorParamsGroupBox.
        """
        if self.command and self.command.struct:
            force = self.command.struct.force
            stiffness = self.command.struct.stiffness
            enable_minimize = self.command.struct.enable_minimize
        else:
            force = 0.0
            stiffness = 0.0
            enable_minimize = False

        self.forceDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             label = "Force:",
                             value = force,
                             setAsDefault = True,
                             minimum    = 0.0,
                             maximum    = 5000.0,
                             singleStep = 1.0,
                             decimals   = 1,
                             suffix     =' pN')
        self.stiffnessDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             label = "Stiffness:",
                             value = stiffness,
                             setAsDefault = True,
                             minimum    = 0.0,
                             maximum    = 1000.0,
                             singleStep = 1.0,
                             decimals   = 1,
                             suffix     =' N/m')

        self.enableMinimizeCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text ="Enable in minimize",
                        widgetColumn = 1
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
            width = self.command.struct.width
            spoke_radius = self.command.struct.sradius
            normcolor = self.command.struct.normcolor
        else:
            length = 10
            width = 1
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


        self.motorWidthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                                label="Motor width :",
                                value = width,
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
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_LinearMotorPropertyManager
        whatsThis_LinearMotorPropertyManager(self)
        return
    
    def _addToolTipText(self):
        """
        What's Tool Tip text for widgets in this Property Manager.
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_LinearMotorPropertyManager
        ToolTip_LinearMotorPropertyManager(self)
        return
