# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
LinearMotorProp.py

$Id$
"""

from PyQt4.Qt import QDialog
from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QColorDialog

from LinearMotorPropDialog import Ui_LinearMotorPropDialog
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf, get_widget_with_color_palette

class LinearMotorProp(QDialog, Ui_LinearMotorPropDialog):
    def __init__(self, motor, glpane):

        QWidget.__init__(self)
        self.setupUi(self)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.change_jig_color)
        self.connect(self.lengthLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.connect(self.widthLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.connect(self.sradiusLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.jig = motor
        self.glpane = glpane
        self.forceLineEdit.setWhatsThis("""<b>Force </b><p>Simulations will begin with the motor's force
        set to this
        value. On each simulation time step, the displacement of the linear motor's atoms are computed using Hooke's
        Law, where:</p>
        <p><b>displacement (x) = - Force(F) / Stiffness(k)</b></p>
        <p>The negative sign indicates that the force
        exerted by the motor (a spring) is in
        direct opposition to the direction of displacement. It is called a
        "restoring force",
        as it tends to restore the system to equilibrium.</p>
        <p>When Stiffness = 0, the restoring force is 0 and the displacement
        will
        continue in one direction.</p>""")
        self.nameLineEdit.setWhatsThis("""<b>Name</b><p>Name of Linear Motor that appears in the Model
        Tree</p>""")
        self.stiffnessLineEdit.setWhatsThis("""<b>Stiffness </b><p>Simulations will begin with the motor's stiffness
        set to this
        value. On each simulation time step, the displacement of the linear motor's atoms are computed using Hooke's
        Law, where:</p>
        <p><b>displacement (x) = - Force(F) / Stiffness(k)</b></p>
        <p>The negative sign indicates that the force
        exerted by the motor (a spring) is in
        direct opposition to the direction of displacement. It is called a
        "restoring force",
        as it tends to restore the system to equilibrium.</p>
        <p>When Stiffness = 0, the restoring force is 0 and the displacement
        will
        continue in one direction.</p>""")
        self.textLabel1_5.setWhatsThis("""<b>Enable in Minimize <i>(experimental)</i></b><p>If checked,
        the force specified above will be applied to the motor's atoms during a structure minimization.  While intended to allow
        simulations to begin with linear motors running at speed, this feature requires more work to be useful.</p>""")
        self.enable_minimize_checkbox.setWhatsThis("""<b>Enable in Minimize <i>(experimental)</i></b><p>If checked,
        the force specified above will be applied to the motor's atoms during a structure minimization.  While intended to allow
        simulations to begin with linear motors running at speed, this feature requires more work to be useful.</p>""")

    def setup(self):

        self.jig_attrs = self.jig.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.

        # Jig color
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap = get_widget_with_color_palette(
            self.jig_color_pixmap, self.jig_QColor)
        self.nameLineEdit.setText(self.jig.name)
        self.stiffnessLineEdit.setText(str(self.jig.stiffness))
        self.forceLineEdit.setText(str(self.jig.force))
        self.lengthLineEdit.setText(str(self.jig.length))
        self.widthLineEdit.setText(str(self.jig.width))
        self.sradiusLineEdit.setText(str(self.jig.sradius)) # spoke radius
        self.enable_minimize_checkbox.setChecked(self.jig.enable_minimize)

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
        '''Slot method to change the jig's length, width and/or spoke radius.'''
        self.jig.length = float(str(self.lengthLineEdit.text())) # motor length
        self.jig.width = float(str(self.widthLineEdit.text())) # motor width
        self.jig.sradius = float(str(self.sradiusLineEdit.text())) # spoke radius
        if gl_update:
            self.glpane.gl_update()

    def accept(self):
        '''Slot for the 'OK' button '''
        self.jig.cancelled = False
        self.jig.try_rename(self.nameLineEdit.text())
        self.jig.force = float(str(self.forceLineEdit.text()))
        self.jig.stiffness = float(str(self.stiffnessLineEdit.text()))

        self.change_motor_size(gl_update=False)

        self.jig.enable_minimize = self.enable_minimize_checkbox.isChecked()

        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        QDialog.accept(self)

    def reject(self):
        '''Slot for the 'Cancel' button '''
        self.jig.attr_update(self.jig_attrs) # Restore attributes of the jig.
        self.glpane.gl_update()
        QDialog.reject(self)
