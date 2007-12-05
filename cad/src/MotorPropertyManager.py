# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
MotorPropertyManager.py

@author: Ninad
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
      
"""
from PyQt4.Qt import QColorDialog

from PM.PM_GroupBox      import PM_GroupBox

from PM.PM_SelectionListWidget import PM_SelectionListWidget
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
        EditController_PM.show(self)
        #It turns out that if updateCosmeticProps is called before 
        #EditController_PM.show, the 'preview' properties are not updated 
        #when you are editing an existing R.Motor. Don't know the cause at this
        #time, issue is trivial. So calling it in the end -- Ninad 2007-10-03
        self.editController.struct.updateCosmeticProps(previewing = True)
        self.updateAttachedAtomListWidget()

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
        
        
        EditController_PM.connect_or_disconnect_signals(self, isConnect)
        
        self.attachedAtomsListWidget.connect_or_disconnect_signals(isConnect)

    
    def close(self):
        """
        Close this Property manager.
        """
        if self.attachedAtomsListWidget:
            self.attachedAtomsListWidget.clearTags()            
        EditController_PM.close(self)


    def enable_or_disable_gui_actions(self, bool_enable = False):
        """
        Enable or disable some gui actions when this property manager is 
        opened or closed, depending on the bool_enable. 
        This is the default implementation. Subclasses can override this method.
        @param bool_enable: If True, the gui actions or widgets will be enabled
                            otherwise disabled. 
        @type  bool_enable: boolean
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
            self.editController.struct.color = self.editController.struct.normcolor = QColor_to_RGBf(color)
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
        self.editController.struct.reverse_direction()
        self.glpane.gl_update()
    
    def updateAttachedAtomListWidget(self, atomList = None):
        """
        Update the list of attached atoms in the self.selectedAtomsListWidget
        """
              
        if not atomList:
            if self.editController.struct:
                atomList = self.editController.struct.atoms[:]
                         
        self.attachedAtomsListWidget.insertItems(row = 0, 
                                                 items = atomList )
        
            
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
        self.attachedAtomsListWidget = \
            PM_SelectionListWidget(pmGroupBox, 
                                   self.win,
                                   heightByRows = 6  )       