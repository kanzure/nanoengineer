# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
RotaryMotorProp.py

$Id$
"""

from PyQt4.Qt import QDialog
from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QColorDialog

from RotaryMotorPropDialog import Ui_RotaryMotorPropDialog
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf, get_widget_with_color_palette

class RotaryMotorProp(QDialog, Ui_RotaryMotorPropDialog):
    def __init__(self, motor, glpane):

        QWidget.__init__(self)
        self.setupUi(self)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.change_jig_color)
        self.connect(self.lengthLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.connect(self.radiusLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.connect(self.sradiusLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.jig = motor
        self.glpane = glpane
        self.nameLineEdit.setWhatsThis("""<b>Name</b><p>Name of Rotary Motor that appears in the Model
        Tree</p>""")
        self.torqueLineEdit.setWhatsThis("""<b>Torque </b><p>Simulations will begin with the motor's torque
        set to this value.</p>""")
        self.speedLineEdit.setWhatsThis("""<b>Final Speed</b><p>The final velocity of the motor's flywheel
        during simulations.</p>""")
        self.initialSpeedLineEdit.setWhatsThis("""<b>Initial Speed</b><p>Simulations will begin with the motor's
        flywheel rotating at this velocity.</p>""")
        self.dampers_textlabel.setWhatsThis("""<b>Dampers</b><p>If checked, the dampers are enabled for this
        motor during a simulation. See the Rotary Motor web page on the NanoEngineer-1 Wiki for more information.</p>""")
        self.textLabel1_5.setWhatsThis("""<b>Enable in Minimize <i>(experimental)</i></b><p>If checked,
        the torque specified above will be applied to the motor atoms during a structure minimization.  While intended to allow simulations
        to begin with rotary motors running at speed, this feature requires more work to be useful.</p>""")
        self.dampers_checkbox.setWhatsThis("""<b>Dampers</b><p>If checked, the dampers are enabled for this
        motor during a simulation. See the Rotary Motor web page on the NanoEngineer-1 Wiki for more information.</p>""")
        self.enable_minimize_checkbox.setWhatsThis("""<b>Enable in Minimize <i>(experimental)</i></b><p>If checked,
        the torque specified above will be applied to the motor atoms during a structure minimization.  While intended to allow simulations
        to begin with rotary motors running at speed, this feature requires more work to be useful.</p>""")

    def setup(self):

        self.jig_attrs = self.jig.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.

        # Jig color
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap = get_widget_with_color_palette(
            self.jig_color_pixmap, self.jig_QColor)

        self.nameLineEdit.setText(self.jig.name)
        self.torqueLineEdit.setText(str(self.jig.torque))
        self.initialSpeedLineEdit.setText(str(self.jig.initial_speed))
        self.speedLineEdit.setText(str(self.jig.speed))
        self.lengthLineEdit.setText(str(self.jig.length))
        self.radiusLineEdit.setText(str(self.jig.radius))
        self.sradiusLineEdit.setText(str(self.jig.sradius)) # spoke radius
        self.enable_minimize_checkbox.setChecked(self.jig.enable_minimize)
        self.dampers_checkbox.setChecked(self.jig.dampers_enabled) # mark & bruce 060421


    def change_jig_color(self):
        '''Slot method to change the jig's color.'''
        color = QColorDialog.getColor(self.jig_QColor, self)

        if color.isValid():
            self.jig_QColor = color
            self.jig_color_pixmap = get_widget_with_color_palette(
            self.jig_color_pixmap, self.jig_QColor)
            self.jig.color = self.jig.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()

    def change_motor_size(self, gl_update=True):
        '''Slot method to change the jig's length, radius and/or spoke radius.'''
        self.jig.length = float(str(self.lengthLineEdit.text())) # motor length
        self.jig.radius = float(str(self.radiusLineEdit.text())) # motor radius
        self.jig.sradius = float(str(self.sradiusLineEdit.text())) # spoke radius
        if gl_update:
            self.glpane.gl_update()

    def accept(self):
        '''Slot for the 'OK' button '''
        self.jig.cancelled = False
        self.jig.try_rename(self.nameLineEdit.text())
        self.jig.torque = float(str(self.torqueLineEdit.text()))
        self.jig.initial_speed = float(str(self.initialSpeedLineEdit.text()))
        self.jig.speed = float(str(self.speedLineEdit.text()))

        self.change_motor_size(gl_update=False)

        self.jig.enable_minimize = self.enable_minimize_checkbox.isChecked()
        self.jig.dampers_enabled = self.dampers_checkbox.isChecked() # bruce 060421

        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        QDialog.accept(self)

    def reject(self):
        '''Slot for the 'Cancel' button '''
        self.jig.attr_update(self.jig_attrs) # Restore attributes of the jig.
        self.glpane.gl_update()
        QDialog.reject(self)
