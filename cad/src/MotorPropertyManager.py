# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
MotorPropertyManager.py

@author: Ninad
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
      
"""
from PyQt4.Qt import QColorDialog

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_ListWidget    import PM_ListWidget
from PM.PM_Constants     import pmRestoreDefaultsButton
from widgets             import QColor_to_RGBf

from GeneratorBaseClass  import AbstractMethod
from EditController_PM   import EditController_PM

from debug               import print_compact_traceback

class MotorPropertyManager(EditController_PM):
    """
    The MotorProperty manager class provides UI and propMgr object for the
    MotorEditController.
    """
    # The title that appears in the Property Manager header.
    title = "Motor"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    #This should be overridden in subclasses
    iconPath = "ui/actions/Simulation/Motor_JUNK.png"
    
    def __init__(self, win, motorEditController):
        """
        Construct the  Motor Property Manager.    
        """
                
        EditController_PM.__init__( self, 
                                    win,
                                    motorEditController) 
                
        
        msg = "Attach a " + self.title + " to the selected atoms"
        
        # This causes the "Message" box to be displayed as well.
        self.updateMessage(msg)
        
        self.glpane = self.win.glpane
               
        # Hide Restore defaults button for Alpha9.
        self.hideTopRowButtons(pmRestoreDefaultsButton)
    
    def show(self):
        """
        Show the  motor Property Manager.
        """
        ##self.update_spinboxes() 
        EditController_PM.show(self)
        #It turns out that if updateCosmeticProps is called before 
        #EditController_PM.show, the 'preview' properties are not updated 
        #when you are editing an existing R.Motor. Don't know the cause at this
        #time, issue is trivial. So calling it in the end -- Ninad 2007-10-03
        self.struct.updateCosmeticProps(previewing = True)
    
    def enable_or_disable_gui_actions(self, bool_enable = False):
        """
        Enable or disable some gui actions when this property manager is 
        opened or closed, depending on the bool_enable. 
        Subclasses can override this method. 
        """
        #It is important to not allow attaching jigs while still editing a
        #motor. See bug 2560 for details. 
        for action in self.win.simulationMenu.actions():
            try:
                action.setEnabled(bool_enable)
            except Exception:
                print_compact_traceback("Ignored exception while disabling "\
                                        " an action.")
        
    def change_jig_color(self):
        """
        Slot method to change the jig's color.
        """
        color = QColorDialog.getColor(self.jig_QColor, self)

        if color.isValid():
            self.jig_QColor = color
            
            ## I intend to implement this once PropMgrColorChooser is complete. 
            #- Mark 2007-05-28
            #self.jig_color_pixmap = \
                #get_widget_with_color_palette(self.jig_color_pixmap, 
                                              #self.jig_QColor)  
            self.struct.color = self.struct.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()
    
    def change_motor_size(self, gl_update = True):
        """
        Slot method to change the jig's size and/or spoke radius.
        Abstract method
        """
        raise AbstractMethod()
            
    def reverse_direction(self):
        """
        Slot for reverse direction button.
        Reverses the direction of the motor.
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
    
    
    
    #Define the UI for the property manager=====================

    def _addGroupBoxes(self):
        """Add the 3 groupboxes for the  Motor Property Manager.
        """
        self.pmGroupBox1 = PM_GroupBox(self, title = "Motor Parameters")
        self._loadGroupBox1(self.pmGroupBox1)
        
        self.pmGroupBox2 = PM_GroupBox(self, title = "Motor Size and Color")
        self._loadGroupBox2(self.pmGroupBox2)
        
        self.pmGroupBox3 = PM_GroupBox(self, title = "Motor Atoms")
        self._loadGroupBox3(self.pmGroupBox3)
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in groupbox 1. 
        Abstract method (overriden in subclasses)
        """     
        raise AbstractMethod()
    
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in groupbox 2. 
        Abstract method (overriden in subclasses)
        """     
        raise AbstractMethod()
    
    def _loadGroupBox3(self, pmGroupBox):
        """
        Load widgets in groupbox 3. 
        This is the default implementation. Can be overridden in subclasses. 
        """     
        
        ##selectedAtomNames = []
        
        ### Create a list of the selected atoms (descriptions).
        ##from bond_constants import describe_atom_and_atomtype
        ##for a in self.struct.atoms:
            ##san = describe_atom_and_atomtype(a)
            ##selectedAtomNames.append(san)
            
        ##self.selectedAtomsListWidget = \
            ##PM_ListWidget(pmGroupBox, 
                                ##label="Atoms :", 
                                ##items=selectedAtomNames,
                                ##row=0, 
                                ##setAsDefault=True,
                                ##numRows=6,
                                ##spanWidth=False)
            
            
        self.selectedAtomsListWidget = \
            PM_ListWidget(pmGroupBox, 
                          label = "Atoms :",
                          heightByRows = 6
                        )
        #old comment --
        # Keep to discuss with Bruce. Mark 2007-06-04
        #self.selectedAtomsListWidget.atoms = self.struct.atoms[:] 
        