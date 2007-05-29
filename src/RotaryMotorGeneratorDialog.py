# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""

$Id$

History:

Mark 2007-05-28: Implemented Rotary Motor using new PropMgrBaseClass.
  
"""
        
__author__ = "Mark"

# To do list:
# - Sort out <name> b/w jigs.py, this file and GeneratorBaseClass.py.
# - Prompt user to select atoms via Property Manager messagebox.
# - Update "Selected Atoms" groupbox as atoms are selected/unselected.
# - When implemented, add new PropMgrColorChooser.

import sys
from PyQt4.Qt import *
from Utility import geticon, getpixmap
from PropMgrBaseClass import *
from PropMgr_Constants import *
from widgets import RGBf_to_QColor, QColor_to_RGBf, get_widget_with_color_palette
from bonds import CC_GRAPHITIC_BONDLENGTH

class RotaryMotorPropMgr(object, PropMgrBaseClass):
    """RotaryMotorPropMgr class.
    """
    
    # <title> - the title that appears in the property manager header.
    title = "Rotary Motor"
    # <propmgr_name> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    propmgr_name = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Simulation/Rotary_Motor.png"
    
    def __init__(self, motor, glpane):
        """Construct the Rotary Motor Property Manager.
        """
        self.jig = motor
        self.glpane = glpane
        
        PropMgrBaseClass.__init__(self, self.propmgr_name)
        self.setPropMgrIcon(self.iconPath)
        self.setPropMgrTitle(self.title)
        self.addGroupBoxes()
        self.addBottomSpacer() 
        self.add_whats_this_text()
        
        #msg = "Edit the Rotary Motor parameters and click <b>Done</b> \
        #    to save."
        
        # This causes the "Message" box to be displayed as well.
        #self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
        
        # Hide preview button.
        self.hideTopRowButtons(pmHidePreviewButton)  
    
    def addGroupBoxes(self):
        """Add the 3 groupboxes for the Rotary Motor Property Manager.
        """
        self.addGroupBoxSpacer()
        self.pmGroupBox1 = PropMgrGroupBox(self, 
                                           title="Rotary Motor Parameters",
                                           titleButton=True)
        self.loadGroupBox1(self.pmGroupBox1)
        
        self.addGroupBoxSpacer()
        self.pmGroupBox2 = PropMgrGroupBox(self, 
                                           title="Motor Size and Color",
                                           titleButton=True)
        self.loadGroupBox2(self.pmGroupBox2)
        
        self.addGroupBoxSpacer()
        self.pmGroupBox3 = PropMgrGroupBox(self, 
                                           title="Selected Atoms",
                                           titleButton=True)
        self.loadGroupBox3(self.pmGroupBox3)
              
    def loadGroupBox1(self, pmGroupBox):
        """Load widgets in groubox 1.
        """
        
        """
        # Leave out of the propmgr. Mark 2007-05-28
        self.nameLineEdit = \
            PropMgrLineEdit(pmGroupBox, 
                            label="Name :",
                            text=self.jig.name,
                            setAsDefault=True,
                            spanWidth=False)"""
        
        self.torqueDblSpinBox = \
            PropMgrDoubleSpinBox(pmGroupBox, 
                                label="Torque :", 
                                val=self.jig.torque, 
                                setAsDefault=True,
                                min=0.0, max=1000.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' nN-nm')
        
        self.initialSpeedDblSpinBox = \
            PropMgrDoubleSpinBox(pmGroupBox,
                                label="Initial Speed :", 
                                val=self.jig.initial_speed, 
                                setAsDefault=True,
                                min=0.0, max=100.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' GHz')
        
        self.finalSpeedDblSpinBox = \
            PropMgrDoubleSpinBox(pmGroupBox,
                                label="Final Speed :", 
                                val=self.jig.speed, 
                                setAsDefault=True,
                                min=0.0, max=100.0, 
                                singleStep=1.0, decimals=1, 
                                suffix=' GHz')
        
        self.dampersCheckBox = \
            PropMgrCheckBox(pmGroupBox,
                              label="Dampers :",
                              isChecked=self.jig.dampers_enabled,
                              setAsDefault=True,
                              spanWidth=False)
        
        self.enableMinimizeCheckBox = \
            PropMgrCheckBox(pmGroupBox,
                              label="Enable in Minimize :",
                              isChecked=self.jig.enable_minimize,
                              setAsDefault=True,
                              spanWidth=False)
        
        self.directionPushButton = \
            PropMgrPushButton(pmGroupBox,
                              label="Direction :",
                              text="Reverse")
        
        self.connect(self.directionPushButton, 
                     SIGNAL("clicked()"), 
                     self.reverse_direction)
    
    def loadGroupBox2(self, pmGroupBox):
        """Load widgets in groubox 2.
        """
        
        self.motorLengthDblSpinBox = \
            PropMgrDoubleSpinBox(pmGroupBox, 
                                label="Motor Length :", 
                                val=self.jig.length, 
                                setAsDefault=True,
                                min=0.5, max=500.0, 
                                singleStep=0.5, decimals=1, 
                                suffix=' Angstroms')
        
        self.connect(self.motorLengthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        
        self.motorRadiusDblSpinBox = \
            PropMgrDoubleSpinBox(pmGroupBox, 
                                label="Motor Radius :", 
                                val=self.jig.radius, 
                                setAsDefault=True,
                                min=0.1, max=50.0, 
                                singleStep=0.1, decimals=1, 
                                suffix=' Angstroms')
        
        self.connect(self.motorRadiusDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        
        self.spokeRadiusDblSpinBox = \
            PropMgrDoubleSpinBox(pmGroupBox, 
                                label="Spoke Radius :", 
                                val=self.jig.sradius, 
                                setAsDefault=True,
                                min=0.1, max=50.0, 
                                singleStep=0.1, decimals=1, 
                                suffix=' Angstroms')
        
        self.connect(self.spokeRadiusDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        
        self.colorPushButton = \
            PropMgrPushButton(pmGroupBox,
                              label="Color :",
                              text="Choose...")
        
        self.connect(self.colorPushButton, 
                     SIGNAL("clicked()"), 
                     self.change_jig_color)
        
    def loadGroupBox3(self, pmGroupBox):
        """Load widgets in groubox 3.
        """
        from bond_constants import describe_atom_and_atomtype
        
        selectedAtoms = [] 
        
        # Create a list of the selected atoms (descriptions).
        for a in self.jig.atoms:
            sa = describe_atom_and_atomtype(a)
            selectedAtoms.append(sa)
            
        self.selectedAtomsListWidget = \
            PropMgrListWidget(pmGroupBox, 
                                label="Atoms :", 
                                choices=selectedAtoms,
                                row=0, 
                                setAsDefault=False,
                                numRows=4,
                                spanWidth=False)
        
    def add_whats_this_text(self):
        """What's This text for some of the widgets in the Property Manager.
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
        
        return
    
    def change_jig_color(self):
        """Slot method to change the jig's color.
        """
        color = QColorDialog.getColor(self.jig_QColor, self)

        if color.isValid():
            self.jig_QColor = color
            """
            # I intend to implement this once PropMgrColorChooser is complete. Mark 2007-05-28
            self.jig_color_pixmap = \
                get_widget_with_color_palette(self.jig_color_pixmap, 
                                              self.jig_QColor)  """ 
            self.jig.color = self.jig.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()
            
    def change_motor_size(self, gl_update=True):
        '''Slot method to change the jig's length, radius and/or spoke radius.'''
        self.jig.length = self.motorLengthDblSpinBox.value()# motor length
        self.jig.radius = self.motorRadiusDblSpinBox.value() # motor radius
        self.jig.sradius = self.spokeRadiusDblSpinBox.value() # spoke radius
        if gl_update:
            self.glpane.gl_update()
            
    def reverse_direction(self):
        """Slot for reverse direction button.
        Reverse the direction fo the motor.
        """
        self.jig.reverse_direction()
        self.glpane.gl_update()