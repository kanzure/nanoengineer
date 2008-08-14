# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:

ninad 2007-02-07: Created to implement new UI for Move and Rotate chunks mode.
ninad 2007-08-20: Code cleanup to use new PM module classes. 

"""


from commands.Move.Ui_MovePropertyManager import Ui_MovePropertyManager
from PyQt4.Qt import Qt, SIGNAL

#debug flag to keep signals always connected
from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED


class MovePropertyManager(Ui_MovePropertyManager):
    """
    The MovePropertyManager class provides a Property Manager 
    for the "Move > Translate / Rotate Components  commands. It also 
    serves as a superclass for FusePropertyManager
    """

    def __init__(self, command):
        Ui_MovePropertyManager.__init__(self, command) 
        
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected =  False
                
        self.lastCheckedRotateButton = None 
        self.lastCheckedTranslateButton = None                     
        self.updateMessage()
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect the slots in Move Property Manager. 
        @see: modifyMode.connect_or_disconnect_signals.
        """
        if isConnect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect

        #TODO: This is a temporary fix for a bug. When you invoke a temporary mode 
        #such as LineMode or PanMode, entering such a temporary mode keeps the 
        #PM from the previous mode open (and theus keeps all its signals 
        #connected)  but while exiting that temporary mode and reentering the 
        #previous mode, it atucally reconnects the signal! This gives rise to 
        #lots  of bugs. This needs more general fix in Temporary mode API. 
        # -- Ninad 2007-10-29

        if isConnect and self.isAlreadyConnected:
            return
        

        self.isAlreadyConnected = isConnect

        change_connect(self.translateGroupBox.titleButton,
                       SIGNAL("clicked()"),
                       self.activate_translateGroupBox_using_groupButton) 

        change_connect(self.rotateGroupBox.titleButton,
                       SIGNAL("clicked()"),
                       self.activate_rotateGroupBox_using_groupButton)

        change_connect(self.translateComboBox, 
                       SIGNAL("currentIndexChanged(int)"), 
                       self.updateTranslateGroupBoxes)

        change_connect(self.rotateComboBox, 
                       SIGNAL("currentIndexChanged(int)"), 
                       self.updateRotateGroupBoxes)

        change_connect( self.freeDragTranslateButtonGroup.buttonGroup, 
                        SIGNAL("buttonClicked(QAbstractButton *)"), 
                        self.changeMoveOption )

        change_connect( self.freeDragRotateButtonGroup.buttonGroup, 
                        SIGNAL("buttonClicked(QAbstractButton *)"), 
                        self.changeRotateOption )

        change_connect(self.transDeltaPlusButton, 
                       SIGNAL("clicked()"), 
                       self.command.transDeltaPlus)

        change_connect(self.transDeltaMinusButton, 
                       SIGNAL("clicked()"), 
                       self.command.transDeltaMinus)

        change_connect(self.moveAbsoluteButton, 
                       SIGNAL("clicked()"), 
                       self.command.moveAbsolute)

        change_connect(self.rotateThetaPlusButton, 
                       SIGNAL("clicked()"), 
                       self.command.rotateThetaPlus)

        change_connect(self.rotateThetaMinusButton, 
                       SIGNAL("clicked()"), 
                       self.command.rotateThetaMinus)

        change_connect(self.moveFromToButton, 
                       SIGNAL("toggled(bool)"), 
                       self.command.moveFromToTemporaryMode)
        
        change_connect(self.rotateAboutPointButton, 
                       SIGNAL("toggled(bool)"), 
                       self.command.rotateAboutPointTemporaryCommand)
        
        

    def ok_btn_clicked(self):
        """
        Calls MainWindow.toolsDone to exit the current mode. 
        @attention: this method needs to be renamed. (this should be done in 
        PM_Dialog)
        """
        self.w.toolsDone()

    def activate_translateGroupBox_using_groupButton(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the button that was checked when this groupbox  was active
        last time. (if applicable). This method is called only when move 
        groupbox button is clicked. See also activate_translateGroupBox 
        method.
        """
        
        self.toggle_translateGroupBox()

        if not self.w.toolsMoveMoleculeAction.isChecked():
            
            self.w.toolsMoveMoleculeAction.setChecked(True)
            self.command.switchGraphicsModeTo(newGraphicsMode = 'TRANSLATE_CHUNKS')

            # Update the title and icon.
            self.setHeaderIcon(self.translateIconPath)
            self.setHeaderTitle(self.translateTitle)

            self.deactivate_rotateGroupBox()          

            buttonToCheck = self.getTranslateButtonToCheck()

            if buttonToCheck:
                buttonToCheck.setChecked(True) 
            else:
                transButtonGroup = self.freeDragTranslateButtonGroup
                buttonToCheck = transButtonGroup.getButtonByText('MOVEDEFAULT')
                buttonToCheck.setChecked(True)

            self.changeMoveOption(buttonToCheck)
            
            self.command.graphicsMode.update_cursor()
            self.updateMessage()
            

    def activate_rotateGroupBox_using_groupButton(self):
        """
        Show contents of this groupbox, deactivae the other groupbox. 
        Also check the button that was checked when this groupbox  was active 
        last time. (if applicable). This method is called only when rotate 
        groupbox button is clicked. See also activate_rotateGroupBox method. 
        """
        
        self.toggle_rotateGroupBox()

        if not self.w.rotateComponentsAction.isChecked():            
            self.w.rotateComponentsAction.setChecked(True)   
            self.command.switchGraphicsModeTo(newGraphicsMode = 'ROTATE_CHUNKS')
            
            # Update the title and icon.
            self.setHeaderIcon(self.rotateIconPath)
            self.setHeaderTitle(self.rotateTitle)

            self.deactivate_translateGroupBox()

            #Following implements NFR bug 2485.
            #Earlier, it used to remember the last checked button 
            #so this wasn't necessary       
            buttonToCheck = self.getRotateButtonToCheck()

            if buttonToCheck:           
                buttonToCheck.setChecked(True) 
            else:
                rotButtonGroup = self.freeDragRotateButtonGroup
                buttonToCheck = rotButtonGroup.getButtonByText('ROTATEDEFAULT')
                buttonToCheck.setChecked(True)

            self.changeRotateOption(buttonToCheck)
            
            self.command.graphicsMode.update_cursor()
            self.updateMessage()
           
    def activate_translateGroupBox(self):
        """
        Show contents of this groupbox, deactivae the other groupbox. 
        Also check the button that was checked when this groupbox  was active 
        last time. (if applicable) This button is called when 
        toolsMoveMoleculeAction is checked from the toolbar or command toolbar. 
        see also: activate_translateGroupBox_using_groupButton
        """

        
        self.command.switchGraphicsModeTo(newGraphicsMode = 'TRANSLATE_CHUNKS')

        #Update the icon and the title
        self.setHeaderIcon(self.translateIconPath)
        self.setHeaderTitle(self.translateTitle)

        self.toggle_translateGroupBox()

        self.deactivate_rotateGroupBox()    

        #Following implements NFR bug 2485.
        #Earlier, it used to remember the last checked button 
        #so this wasn't necessary
        buttonToCheck = self.getTranslateButtonToCheck()


        if buttonToCheck:
            buttonToCheck.setChecked(True) 
        else:
            transButtonGroup = self.freeDragTranslateButtonGroup
            buttonToCheck = transButtonGroup.getButtonByText('MOVEDEFAULT')
            buttonToCheck.setChecked(True)

        self.changeMoveOption(buttonToCheck)
        
        self.command.graphicsMode.update_cursor()
        self.updateMessage()
       
    def activate_rotateGroupBox(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the button that was checked when this groupbox  was active 
        last time. (if applicable). This button is called when 
        rotateComponentsAction is checked from the toolbar or command toolbar. 
        @see: L{self.activate_rotateGroupBox_using_groupButton}
        """
        
        
        self.command.switchGraphicsModeTo(newGraphicsMode = 'ROTATE_CHUNKS')
                
        #Update the icon and the title. 
        self.setHeaderIcon(self.rotateIconPath)
        self.setHeaderTitle(self.rotateTitle)

        self.toggle_rotateGroupBox()

        self.deactivate_translateGroupBox()           

        buttonToCheck = self.getRotateButtonToCheck() 

        if buttonToCheck:
            buttonToCheck.setChecked(True) 
        else:
            rotButtonGroup = self.freeDragRotateButtonGroup
            buttonToCheck = rotButtonGroup.getButtonByText('ROTATEDEFAULT')
            buttonToCheck.setChecked(True)

        self.changeRotateOption(buttonToCheck)
        
        self.command.graphicsMode.update_cursor()
        self.updateMessage()
        
      
    def deactivate_rotateGroupBox(self):
        """ Hide the items in the groupbox, Also 
        store the current checked button which will be checked again 
        when user activates this groupbox again. After storing 
        the checked button, uncheck it (so that other active groupbox 
        button can operate easily). """

        self.rotateGroupBox.collapse()

        #Store the last checked button of the groupbox you are about to close
        #(in this case Rotate Groupbox is the groupbox that will be deactivated 
        #and Move groupbox will be activated (opened) ) 
        lastCheckedRotateButton = self.freeDragRotateButtonGroup.checkedButton()
        self.setLastCheckedRotateButton(lastCheckedRotateButton)     

        #Disconnect checked button in Rotate Components groupbox
        #bruce 070613 added condition
        if self.freeDragRotateButtonGroup.checkedButton(): 
            self.freeDragRotateButtonGroup.checkedButton().setChecked(False)

    def deactivate_translateGroupBox(self):
        """ Hide the items in the groupbox, Also 
        store the current checked button which will be checked again 
        when user activates this groupbox again. After storing 
        the checked button, uncheck it (so that other active groupbox 
        button can operate easily). """

        self.translateGroupBox.collapse() 

        #Store the last checked button of the groupbox you are about to close
        #(in this case Move Groupbox is the groupbox that will be deactivated 
        # and 'Rotate groupbox will be activated (opened) ) 
        buttonGroup = self.freeDragTranslateButtonGroup
        lastCheckedTranslateButton = buttonGroup.checkedButton()        
        self.setLastCheckedMoveButton(lastCheckedTranslateButton)        

        #Disconnect checked button in Move groupbox
        if self.freeDragTranslateButtonGroup.checkedButton():
            self.freeDragTranslateButtonGroup.checkedButton().setChecked(False) 


    def toggle_translateGroupBox(self):

        """ 
        Toggles the item display in the parent groupbox of the button and 
        hides the other groupbox also disconnecting the actions in the other 
        groupbox
        Example: If user clicks on Move groupbox button, it will toggle the 
        display of the groupbox, connect its actions and Hide the other groupbox 
        i.e. Rotate Compomnents groupbox and also disconnect actions inside it.
        """

        self.translateGroupBox.toggleExpandCollapse()


    def toggle_rotateGroupBox(self):
        """ 
        Toggles the item display in the parent groupbox of the button and 
        hides the other groupbox also disconnecting the actions in the other 
        groupbox.
        Example: If user clicks on Move groupbox button, it will toggle the 
        display of the groupbox, connect its actions and Hide the other groupbox 
        i.e. Rotate Compomnents groupbox and also  disconnect actions inside it
       """

        self.rotateGroupBox.toggleExpandCollapse()


    def setLastCheckedRotateButton(self, lastCheckedButton):
        """" 
        Sets the  'last checked button value' Program remembers the last checked 
        button in a groupbox (either Translate or rotate (components)) . 
        When that groupbox is displayed, it checkes this last button again 
        (see get method)
        """
        self.lastCheckedRotateButton = lastCheckedButton

    def setLastCheckedMoveButton(self, lastCheckedButton):
        """" Sets the  'last checked button value' Program remembers the last 
        checked button in a groupbox (either Translate components or rotate 
        components) . When that groupbox is displayed, it checkes this last 
        button again (see get method)
        """
        self.lastCheckedTranslateButton = lastCheckedButton

    def getLastCheckedRotateButton(self):
        """returns the last checked button in a groupbox."""
        if self.lastCheckedRotateButton:
            return self.lastCheckedRotateButton
        else:
            return None

    def getLastCheckedMoveButton(self):
        """returns the last checked button in a groupbox."""
        if self.lastCheckedTranslateButton:
            return self.lastCheckedTranslateButton
        else:
            return None

    def getRotateButtonToCheck(self):
        """
        Decide which rotate group box button to check 
        based on the last button that was checked in *translate* 
        groupbox
        @return <buttonToCheck>:rotate button to be checked when rotate groupbox 
        is active (and when free drag rotate is chosen from the combo box)"""
        lastMoveButton =  self.getLastCheckedMoveButton()

        rotateButtonToCheck = None

        if lastMoveButton in \
           self.freeDragTranslateButtonGroup.buttonGroup.buttons():
            transButtonGroup = self.freeDragTranslateButtonGroup.buttonGroup
            buttonId = transButtonGroup.id(lastMoveButton)

            rotButtonGroup = self.freeDragRotateButtonGroup
            rotateButtonToCheck = rotButtonGroup.getButtonById(buttonId)


        return rotateButtonToCheck

    def getTranslateButtonToCheck(self):
        """ Decide which translate group box button to check 
        based on the last button that was checked in *rotate* groupbox.

        @return <buttonToCheck>:translate button to be checked when translate 
        grpbx is active (and when free drag translate is chosen from the combo 
        box)"""

        lastRotateButton =  self.getLastCheckedRotateButton()
        translateButtonToCheck = None

        if lastRotateButton in \
           self.freeDragRotateButtonGroup.buttonGroup.buttons():
            rotButtonGroup = self.freeDragRotateButtonGroup.buttonGroup
            buttonId = rotButtonGroup.id(lastRotateButton)

            transButtonGroup = self.freeDragTranslateButtonGroup
            translateButtonToCheck = transButtonGroup.getButtonById(buttonId)


        return translateButtonToCheck

    def updateRotationDeltaLabels(self, rotateOption, rotDelta):
        """ 
        Updates the Rotation Delta labels in the Rotate combobox  while rotating
        the selection around an axis
        """

        if rotateOption == 'ROTATEX':
            listx = [self.rotateXLabelRow]            
            listyz = [self.rotateYLabelRow, self.rotateZLabelRow]           
            for lbl in listx:
                lbl.setBold(isBold = True)
                lbl.show()
            txt = str(round(rotDelta, 2))
            self.deltaThetaX_lbl.setText(txt)
            for lbl in listyz:
                lbl.setBold(isBold = False)
                lbl.show()
        elif rotateOption == 'ROTATEY':
            listy = [self.rotateYLabelRow]
            listxz = [self.rotateXLabelRow, self.rotateZLabelRow]
            for lbl in listy :
                lbl.setBold(True)     
                lbl.show()
            txt = str(round(rotDelta, 2))
            self.deltaThetaY_lbl.setText(txt)
            for lbl in listxz:
                lbl.setBold(False)
                lbl.show()
        elif rotateOption == 'ROTATEZ':
            listz = [self.rotateZLabelRow]
            listxy =  [ self.rotateXLabelRow, self.rotateYLabelRow]
            for lbl in listz:
                lbl.setBold(True)
                lbl.show()
            txt = str(round(rotDelta, 2))
            self.deltaThetaZ_lbl.setText(txt)
            for lbl in listxy:
                lbl.setBold(False)   
                lbl.show()
        else:
            print "MovePropertyManager.updateRotationDeltaLabels:\
                  Error - unknown rotateOption value :", self.rotateOption

    def toggleRotationDeltaLabels(self, show = False):
        """ 
        Hide all the rotation delta labels when  
        rotateFreeDragAction is checked 
        """

        lst = [self.rotateXLabelRow, self.rotateYLabelRow, self.rotateZLabelRow]

        if not show:            
            for lbl in lst:
                lbl.hide()    
        else:
            for lbl in lst:
                lbl.show()

    def changeMoveOption(self, button):
        """
        Change the translate option. 

        @param button: QToolButton that decides the type of translate operation 
                       to be set.
        @type  button: QToolButton 
                       U{B{QToolButton}
                       <http://doc.trolltech.com/4.2/qtoolbutton.html>}

        """

        buttonText = str(button.text())

        assert buttonText in ['TRANSX', 'TRANSY', 'TRANSZ', 
                              'ROT_TRANS_ALONG_AXIS', 'MOVEDEFAULT' ]
        
        self.command.graphicsMode.moveOption = buttonText
        
        #commandSequencer = self.win.commandSequencer  
        
        #if commandSequencer.currentCommand.commandName == 'TRANSLATE_CHUNKS':
            #commandSequencer.currentCommand.graphicsMode.moveOption = buttonText

        ##self.command.moveOption = buttonText


    def changeRotateOption(self, button):
        """
        Change the rotate option. 

        @param button: QToolButton that decides the type of rotate operation 
                       to be set.
        @type  button: QToolButton 
                       U{B{QToolButton}
                       <http://doc.trolltech.com/4.2/qtoolbutton.html>}
        """  

        buttonText = str(button.text())

        assert buttonText in ['ROTATEX', 'ROTATEY', 'ROTATEZ', 
                              'ROT_TRANS_ALONG_AXIS', 'ROTATEDEFAULT' ]


        if buttonText in ['ROTATEDEFAULT', 'ROT_TRANS_ALONG_AXIS']:
            self.toggleRotationDeltaLabels(show = False)
        else:
            self.toggleRotationDeltaLabels(show = True)
        
        self.command.graphicsMode.rotateOption = buttonText
        #commandSequencer = self.win.commandSequencer
        #if commandSequencer.currentCommand.commandName == 'ROTATE_CHUNKS':
            #commandSequencer.currentCommand.graphicsMode.rotateOption = buttonText

        ##self.command.rotateOption = buttonText


    def set_move_xyz(self, x, y, z):
        """
        Set values of X, Y and Z coordinates in the Move Property Manager.
        @param x: X coordinate of the common center of the selected objects
        @param y: Y coordinate of the common center of the selected objects
        @param z: Z coordinate of the common center of the selected objects
        """
        self.moveXSpinBox.setValue(x)
        self.moveYSpinBox.setValue(y)
        self.moveZSpinBox.setValue(z)

    def get_move_xyz(self):
        """
        Returns the xyz coordinate in the Move Property Manager. 
        @return: the coordinate
        @rtype: tuple (x, y, z)
        """

        x = self.moveXSpinBox.value()
        y = self.moveYSpinBox.value()
        z = self.moveZSpinBox.value()

        return (x, y, z)   

    def set_move_delta_xyz(self, delX, delY, delZ):
        """
        Sets the values for 'move by distance delta' spinboxes 
        These are the values by which the selection will be translated 
        along the specified axes.
        @param delX: Delta X value 
        @param delY: Delta Y value
        @param delZ: Delta Z value

        """
        self.moveDeltaXSpinBox.setValue(delX)
        self.moveDeltaYSpinBox.setValue(delY)
        self.moveDeltaZSpinBox.setValue(delZ)

    def get_move_delta_xyz(self, Plus = True):
        """
        Returns the values for 'move by distance delta' spinboxes 
        @param Plus : Boolean that decides the sign of the return values. 
        (True returns positive values)
        @return : A tuple containing delta X, delta Y and delta Z values
        """

        delX = self.moveDeltaXSpinBox.value()
        delY = self.moveDeltaYSpinBox.value()
        delZ = self.moveDeltaZSpinBox.value()

        if Plus: 
            return (delX, delY, delZ) # Plus
        else: 
            return (-delX, -delY, -delZ) # Minus
        
    def show(self):
        Ui_MovePropertyManager.show(self)
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)

    def close(self):
        """
        Closes this Property Manager.
        @see:  L{PM_GroupBox.close()}  (overrides this method) 
        @Note: Before calling close method of its superclass, it collapses the 
        translate and rotate groupboxes. This is necessary as it calls the 
        activate groupbox method which also toggles the current state of the 
        current groupbox. Earlier, explicitely collapsing groupboxes while 
        closing the PM was not needed as a new PM object was created each time
        you enter move mode. (and L{Ui_MovePropertyManager} used to call 
        collapse method of these groupboxes to acheive the desired effect. 

        """

        self.translateGroupBox.collapse()
        self.rotateGroupBox.collapse()
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)
            
        Ui_MovePropertyManager.close(self)

    def updateMessage(self, msg = ''): # Mark 2007-06-23
        """
        Updates the message box with an informative message.
        """
        graphicsModeName = ''
        #Question: should we define a new attr in Graphicsmode classes 
        #suchs as graphicsModeName ? (or a method that returns the GM name 
        # and which falls backs to graphicsMode.__class__.__name__ if name  is 
        # not defined ? -- Ninad 2008-01-25
        if hasattr(self.command, 'graphicsMode'):
            graphicsModeName = self.command.graphicsMode.__class__.__name__

        if msg:
            self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )
            return

        from operations.ops_select import objectSelected
        if objectSelected(self.o.assy):
            msg = ""
        else:
            msg = "Click on an object to select it."
        
        if graphicsModeName:

            if graphicsModeName == 'TranslateChunks_GraphicsMode':
                currentIndex = self.translateComboBox.currentIndex()
                if  currentIndex == 0:
                    msg += "To <b>translate</b> the selection, <b>highlight</b> "\
                        "any of the selected items and <b>drag</b> while holding " \
                        "down the left mouse button. Translate options are "\
                        "available below."
                elif currentIndex == 1:
                    msg += "<b>Translate</b> the selection by specified offset, "\
                        "using the <b>'+Delta'</b> and <b> '-Delta'</b> "\
                        "buttons."
                elif currentIndex == 2:
                    msg += "Use <b>Move Selection</b> button to translate the "\
                        "selection to the specified absolute XYZ coordinate."
                    
            else:
                currentIndex = self.rotateComboBox.currentIndex()
                if  currentIndex == 0:
                    msg += "To <b>rotate</b> the selection, <b>highlight</b> "\
                        "any of the selected items and <b>drag</b> while holding " \
                        "down the left mouse button. Rotate options are "\
                        "available below."
                elif currentIndex == 1:
                    msg += "<b> Rotate </b> the selection by the specified "\
                        "angle, around the specified axis, using the "\
                        " <b>'+Theta'</b> and <b> '-Theta'</b> buttons."

        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )