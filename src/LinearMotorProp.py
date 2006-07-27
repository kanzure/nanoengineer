# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
LinearMotorProp.py

$Id$
"""

from qt import *
from LinearMotorPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf
import copy

class LinearMotorProp(LinearMotorPropDialog):
    def __init__(self, motor, glpane):

        LinearMotorPropDialog.__init__(self)
        self.jig = motor
        self.glpane = glpane
        QWhatsThis.add(self.forceLineEdit, """<b>Force </b><p>Simulations will begin with the motor's force
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
        QWhatsThis.add(self.nameLineEdit, """<b>Name</b><p>Name of Linear Motor that appears in the Model
        Tree</p>""")
        QWhatsThis.add(self.stiffnessLineEdit, """<b>Stiffness </b><p>Simulations will begin with the motor's stiffness
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
        QWhatsThis.add(self.textLabel1_5, """<b>Enable in Minimize <i>(experimental)</i></b><p>If checked,
        the force specified above will be applied to the motor's atoms during a structure minimization.  While intended to allow
        simulations to begin with linear motors running at speed, this feature requires more work to be useful.</p>""")
        QWhatsThis.add(self.enable_minimize_checkbox, """<b>Enable in Minimize <i>(experimental)</i></b><p>If checked,
        the force specified above will be applied to the motor's atoms during a structure minimization.  While intended to allow
        simulations to begin with linear motors running at speed, this feature requires more work to be useful.</p>""")

    def setup(self):
        
        self.jig_attrs = self.jig.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.
        
        # Jig color
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap.setPaletteBackgroundColor(self.jig_QColor)

        self.nameLineEdit.setText(self.jig.name)
        self.stiffnessLineEdit.setText(str(self.jig.stiffness))
        self.forceLineEdit.setText(str(self.jig.force))
        self.lengthLineEdit.setText(str(self.jig.length))
        self.widthLineEdit.setText(str(self.jig.width))
        self.sradiusLineEdit.setText(str(self.jig.sradius)) # spoke radius
        self.enable_minimize_checkbox.setChecked(self.jig.enable_minimize)

    def change_jig_color(self):
        '''Slot method to change the jig's color.'''
        color = QColorDialog.getColor(self.jig_QColor, self, "ColorDialog")

        if color.isValid():
            self.jig_color_pixmap.setPaletteBackgroundColor(color)
            self.jig_QColor = color
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
