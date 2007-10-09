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
from PyQt4.Qt import QColorDialog
from PyQt4.Qt import SIGNAL

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_PushButton    import PM_PushButton
from PM.PM_ListWidget    import PM_ListWidget
from PM.PM_Constants     import pmRestoreDefaultsButton

from widgets import RGBf_to_QColor, QColor_to_RGBf
from widgets import get_widget_with_color_palette

from utilities.Comparison import same_vals

from EditController_PM import EditController_PM


class RotaryMotorPropertyManager(EditController_PM):
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
                
        EditController_PM.__init__( self, 
                                    win,
                                    motorEditController) 
                
        
        msg = "Insert a Rotary motor."
        
        # This causes the "Message" box to be displayed as well.
        self.updateMessage(msg)
        
        self.glpane = self.win.glpane
               
        # Hide Restore defaults button for Alpha9.
        self.hideTopRowButtons(pmRestoreDefaultsButton)
    
    def show(self):
        """
        Show the Rotary motor Property Manager.
        """
        ##self.update_spinboxes() 
        EditController_PM.show(self)
        #It turns out that if updateCosmeticProps is called before 
        #EditController_PM.show, the 'preview' properties are not updated 
        #when you are editing an existing R.Motor. Don't know the cause at this
        #time, issue is trivial. So calling it in the end -- Ninad 2007-10-03
        self.struct.updateCosmeticProps(previewing = True)
        

    def _addGroupBoxes(self):
        """Add the 3 groupboxes for the Rotary Motor Property Manager.
        """
        self.pmGroupBox1 = PM_GroupBox(self, title = "Rotary Motor Parameters")
        self._loadGroupBox1(self.pmGroupBox1)
        
        self.pmGroupBox2 = PM_GroupBox(self, title = "Motor Size and Color")
        self._loadGroupBox2(self.pmGroupBox2)
        
        self.pmGroupBox3 = PM_GroupBox(self, title = "Motor Atoms")
        self._loadGroupBox3(self.pmGroupBox3)
              
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in MotorParamsGroupBox.
        """                
        self.torqueDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Torque :", 
                                value = self.struct.torque, 
                                setAsDefault = True,
                                minimum    = 0.0, 
                                maximum    = 1000.0, 
                                singleStep = 1.0, 
                                decimals   = 1, 
                                suffix     =' nN-nm')
        
        self.initialSpeedDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                                label = "Initial Speed :", 
                                value = self.struct.initial_speed, 
                                setAsDefault = True,
                                minimum    = 0.0, 
                                maximum    = 100.0, 
                                singleStep = 1.0, 
                                decimals   = 1, 
                                suffix     =' GHz')
        
        self.finalSpeedDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                                label="Final Speed :", 
                                value = self.struct.speed, 
                                setAsDefault=True,
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
                              
        
        self.dampersCheckBox.setChecked(self.struct.dampers_enabled)
        
        self.enableMinimizeCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text ="Enable in Minimize",
                        widgetColumn = 0
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
        """Load widgets in groubox 2.
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
        
        self.motorRadiusDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label="Motor Radius :", 
                                value = self.struct.radius, 
                                setAsDefault = True,
                                minimum = 0.1, 
                                maximum = 50.0, 
                                singleStep=0.1, 
                                decimals=1, 
                                suffix=' Angstroms')
        
        self.connect(self.motorRadiusDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        
        self.spokeRadiusDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label="Spoke Radius :", 
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
                              label="Color :",
                              text="Choose...")
        
        self.connect(self.colorPushButton, 
                     SIGNAL("clicked()"), 
                     self.change_jig_color)
        
    def _loadGroupBox3(self, pmGroupBox):
        """Load widgets in groubox 3.
        """
        
        '''
        selectedAtomNames = []
        
        # Create a list of the selected atoms (descriptions).
        from bond_constants import describe_atom_and_atomtype
        for a in self.struct.atoms:
            san = describe_atom_and_atomtype(a)
            selectedAtomNames.append(san)
            
        self.selectedAtomsListWidget = \
            PM_ListWidget(pmGroupBox, 
                                label="Atoms :", 
                                items=selectedAtomNames,
                                row=0, 
                                setAsDefault=True,
                                numRows=6,
                                spanWidth=False)
            '''
            
        self.selectedAtomsListWidget = \
            PM_ListWidget(pmGroupBox, 
                          label="Atoms :",
                          heightByRows = 6
                        )
        #old comment --
        # Keep to discuss with Bruce. Mark 2007-06-04
        #self.selectedAtomsListWidget.atoms = self.struct.atoms[:]    
    
        
    def _addWhatsThisText(self):
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
            # I intend to implement this once PropMgrColorChooser is complete. 
            - Mark 2007-05-28
            self.jig_color_pixmap = \
                get_widget_with_color_palette(self.jig_color_pixmap, 
                                              self.jig_QColor)  """ 
            self.struct.color = self.struct.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()
            
    def change_motor_size(self, gl_update=True):
        """
        Slot method to change the jig's length, radius and/or spoke radius.
        """
        self.struct.length = self.motorLengthDblSpinBox.value()# motor length
        self.struct.radius = self.motorRadiusDblSpinBox.value() # motor radius
        self.struct.sradius = self.spokeRadiusDblSpinBox.value() # spoke radius
        if gl_update:
            self.glpane.gl_update()
            
    def reverse_direction(self):
        """Slot for reverse direction button.
        Reverse the direction fo the motor.
        """
        self.struct.reverse_direction()
        self.glpane.gl_update()
    
    def update_props_if_needed_before_closing(self):
        """
        This updates some cosmetic properties of the Rotary motor (e.g. opacity)
        before closing the Property Manager.
        """
        #API method. See Plane.update_props_if_needed_before_closing for another
        #example.        
        # Example: The Rotary Motor Property Manager is open and the user is 
        # 'previewing' the motor. Now the user clicks on "Build > Atoms" 
        # to invoke the next command (without clicking "Done"). 
        # This calls self.open() which replaces the current PM 
        # with the Build Atoms PM.  Thus, it creates and inserts the motor 
        # that was being previewed. Before the motor is permanently inserted
        # into the part, it needs to change some of its cosmetic properties
        # (e.g. opacity) which distinguishes it as 
        # a previewed motor in the part. This function changes those properties.
        # [ninad 2007-10-09 comment]    
        
        #called from updatePropertyManager in Ui_PartWindow.py (Partwindowclass)

        self.struct.updateCosmeticProps()
    
    def updateMessage(self, message = ''):
        """
        Updates the message box with an informative message
        @param message: Message to be displayed in the Message groupbox of 
                        the property manager
        @type  message: string
        """
        msg = message
        self.MessageGroupBox.insertHtmlMessage(msg, 
                                               setAsDefault = False,
                                               minLines     = 5)