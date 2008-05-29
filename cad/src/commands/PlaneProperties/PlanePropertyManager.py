# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 20070602: Created.

"""
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_RadioButtonList import PM_RadioButtonList
from PM.PM_ToolButtonRow import PM_ToolButtonRow
from PM.PM_Constants     import pmRestoreDefaultsButton
from PM.PM_FileChooser   import PM_FileChooser
from command_support.EditCommand_PM import EditCommand_PM
import foundation.env as env


# Placement Options radio button list to create radio button list.
# Format: buttonId, buttonText, tooltip
PLACEMENT_OPTIONS_BUTTON_LIST = [ \
    ( 0, "Parallel to screen",     "Parallel to screen"     ),
    ( 1, "Through selected atoms", "Through selected atoms" ),
    ( 2, "Offset to a plane",      "Offset to a plane"      ),
    ( 3, "Custom",                 "Custom"                 )
]

class PlanePropertyManager(EditCommand_PM):
    """
    The PlanePropertyManager class provides a Property Manager for a 
    (reference) Plane.
    """

    # The title that appears in the Property Manager header.
    title = "Plane"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Insert/Reference Geometry/Plane.png"

    def __init__(self, win, planeEditCommand):
        """
        Construct the Plane Property Manager.

        @param plane: The plane.
        @type  plane: L{Plane}
        """

        EditCommand_PM.__init__( self, 
                                 win,
                                 planeEditCommand) 



        msg = "Insert a Plane parallel to the screen. Note: This feature is \
            experimental for Alpha9 and has known bugs."

        # This causes the "Message" box to be displayed as well.
        self.updateMessage(msg)

        # self.resized_from_glpane flag makes sure that the 
        #spinbox.valueChanged()
        # signal is not emitted after calling spinbox.setValue.
        self.resized_from_glpane = False

        # Hide Preview and Restore defaults button for Alpha9.
        self.hideTopRowButtons(pmRestoreDefaultsButton)
        # needed to figure out if the model has changed or not
        self.previousPMParams = None
        self.imageFile = ""

    def _addGroupBoxes(self):
        """
        Add the 1st group box to the Property Manager.
        """
        self.pmPlacementOptions = \
            PM_RadioButtonList( self,
                                title      = "Placement Options", 
                                buttonList = PLACEMENT_OPTIONS_BUTTON_LIST,
                                checkedId  = 3 )

        self.connect(self.pmPlacementOptions.buttonGroup,
                     SIGNAL("buttonClicked(int)"),
                     self.changePlanePlacement)

        self.pmGroupBox1 = PM_GroupBox(self, title = "Parameters")
        self._loadGroupBox1(self.pmGroupBox1)

        #image groupbox
        self.pmGroupBox2 = PM_GroupBox(self, title = "Image")
        self._loadGroupBox2(self.pmGroupBox2)


    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in the image group box.

        @param pmGroupBox: The image group box in the PM.
        @type  pmGroupBox: L{PM_GroupBox}
        """
        self.imageDisplayCheckBox = \
            PM_CheckBox( pmGroupBox,
                         text         = "Display image",
                         widgetColumn  = 0,
                         state        = Qt.Unchecked,
                         setAsDefault = True,
                         spanWidth = True
                         )

        self.imageDisplayFileChooser = \
            PM_FileChooser(pmGroupBox,
                           label     = 'Image file:',
                           text      = '' ,
                           spanWidth = True,
                           filter    = "PNG (*.png);;"\
                           "All Files (*.*)"
                           )
        self.imageDisplayFileChooser.setEnabled(False)
        # add change image properties button

        BUTTON_LIST = [ 
            ( "QToolButton", 1,  "+90", 
              "ui/actions/Properties Manager/RotateImage+90.png",
              "+90", "", 0),
            ( "QToolButton", 2,  "-90", 
              "ui/actions/Properties Manager/RotateImage-90.png",
              "-90", "", 1),
            ( "QToolButton", 3,  "FLIP",  
              "ui/actions/Properties Manager/FlipImageVertical.png",
              "Flip", "", 2),
            ( "QToolButton", 4,  "MIRROR",  
              "ui/actions/Properties Manager/FlipImageHorizontal.png",
              "Mirror", "", 3) 
        ]

        #image change button groupbox
        self.pmGroupBox2 = PM_GroupBox(pmGroupBox, title = "Modify Image")

        self.imageChangeButtonGroup = \
            PM_ToolButtonRow( self.pmGroupBox2, 
                              title        = "",
                              buttonList   = BUTTON_LIST,
                              spanWidth    = True,
                              isAutoRaise  = False,
                              isCheckable  = False,
                              setAsDefault = True,
                              )

        self.imageChangeButtonGroup.buttonGroup.setExclusive(False)

        self.plusNinetyButton  = self.imageChangeButtonGroup.getButtonById(1)
        self.minusNinetyButton    = self.imageChangeButtonGroup.getButtonById(2)
        self.flipButton = self.imageChangeButtonGroup.getButtonById(3)
        self.mirrorButton   = self.imageChangeButtonGroup.getButtonById(4)

        # buttons enabled when a valid image is loaded
        self.mirrorButton.setEnabled(False)
        self.plusNinetyButton.setEnabled(False)
        self.minusNinetyButton.setEnabled(False)
        self.flipButton.setEnabled(False)

        self.connect(self.plusNinetyButton,SIGNAL("clicked()"),self.rotate_90)
        self.connect(self.minusNinetyButton,SIGNAL("clicked()"),self.rotate_neg_90)
        self.connect(self.flipButton,SIGNAL("clicked()"),self.flip_image)
        self.connect(self.mirrorButton,SIGNAL("clicked()"),self.mirror_image)

        #signal slot connection for imageDisplayCheckBox
        self.connect(self.imageDisplayCheckBox, 
                     SIGNAL("stateChanged(int)"), 
                     self.toggleFileChooserBehavior)

        #signal slot connection for imageDisplayFileChooser
        self.connect(self.imageDisplayFileChooser.lineEdit, 
                     SIGNAL("editingFinished()"),
                     self.update_imageFile)


    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in 1st group box.

        @param pmGroupBox: The 1st group box in the PM.
        @type  pmGroupBox: L{PM_GroupBox}
        """

        self.widthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             label        = "Width:",
                             value        = 10.0, 
                             setAsDefault = True,
                             minimum      = 1.0, 
                             maximum      = 200.0,
                             singleStep   = 1.0, 
                             decimals     = 3, 
                             suffix       = ' Angstroms')

        self.connect(self.widthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_plane_width)

        self.heightDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                             label        =" Height:",
                             value        = 10.0, 
                             setAsDefault = True,
                             minimum      = 1.0, 
                             maximum      = 200.0,
                             singleStep   = 1.0, 
                             decimals     = 3, 
                             suffix       = ' Angstroms')

        self.connect(self.heightDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_plane_height)

        self.aspectRatioCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text         = 'Maintain Aspect Ratio of:' ,
                        widgetColumn = 1,
                        state        = Qt.Unchecked
                        )

        self.connect(self.aspectRatioCheckBox,
                     SIGNAL("stateChanged(int)"),
                     self._enableAspectRatioSpinBox)

        self.aspectRatioSpinBox = \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "",
                              value         =  2.0,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  10.0,
                              singleStep    =  0.1,
                              decimals      =  2,
                              suffix        =  " to 1.00")   

        if self.aspectRatioCheckBox.isChecked():
            self.aspectRatioSpinBox.setEnabled(True)
        else:
            self.aspectRatioSpinBox.setEnabled(False)

    def _addWhatsThisText(self):
        """
        What's This text for some of the widgets in this Property Manager.  

        @note: Many PM widgets are still missing their "What's This" text.
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_PlanePropertyManager
        whatsThis_PlanePropertyManager(self)


    def  toggleFileChooserBehavior(self, checked):
        """
        Enables FileChooser and displays image when checkbox is checked otherwise 
        not
        """
        self.imageDisplayFileChooser.lineEdit.emit(SIGNAL("editingFinished()"))
        if checked == Qt.Checked:
            self.imageDisplayFileChooser.setEnabled(True)   
        elif checked == Qt.Unchecked:
            self.imageDisplayFileChooser.setEnabled(False)
            # if an image is already displayed, that's need to be hidden as well
        else:
            pass


    def update_imageFile(self):
        if self.imageDisplayCheckBox.isChecked(): 
            self.imageFile = str(self.imageDisplayFileChooser.lineEdit.text())

            from model.Plane import checkIfValidImagePath
            validPath = checkIfValidImagePath(self.imageFile)

            if validPath:
                self.mirrorButton.setEnabled(True)
                self.plusNinetyButton.setEnabled(True)
                self.minusNinetyButton.setEnabled(True)
                self.flipButton.setEnabled(True)
            else:
                self.mirrorButton.setEnabled(False)
                self.plusNinetyButton.setEnabled(False)
                self.minusNinetyButton.setEnabled(False)
                self.flipButton.setEnabled(False)
        else:
            self.imageFile =""
            self.mirrorButton.setEnabled(False)
            self.plusNinetyButton.setEnabled(False)
            self.minusNinetyButton.setEnabled(False)
            self.flipButton.setEnabled(False)


    def show(self):
        """
        Show the Plane Property Manager.
        """
        self.update_spinboxes() 
        EditCommand_PM.show(self)
        #It turns out that if updateCosmeticProps is called before 
        #EditCommand_PM.show, the 'preview' properties are not updated 
        #when you are editing an existing plane. Don't know the cause at this
        #time, issue is trivial. So calling it in the end -- Ninad 2007-10-03

        if self.editCommand.struct:
            self.editCommand.struct.updateCosmeticProps(previewing = True)


    def change_plane_width(self, newWidth):
        """
        Slot for width spinbox in the Property Manager.
        """
        if self.aspectRatioCheckBox.isChecked():
            self.editCommand.struct.width   =  newWidth
            self.editCommand.struct.height  =  self.editCommand.struct.width / \
                self.aspectRatioSpinBox.value() 
            self.update_spinboxes()
        else:
            self.change_plane_size()
        self._updateAspectRatio()

    def change_plane_height(self, newHeight):
        """
        Slot for height spinbox in the Property Manager.
        """
        if self.aspectRatioCheckBox.isChecked():
            self.editCommand.struct.height  =  newHeight 
            self.editCommand.struct.width   =  self.editCommand.struct.height * \
                self.aspectRatioSpinBox.value()
            self.update_spinboxes()
        else:
            self.change_plane_size()
        self._updateAspectRatio()

    def change_plane_size(self, gl_update = True):
        """
        Slot to change the Plane's width and height.

        @param gl_update: Forces an update of the glpane.
        @type  gl_update: bool
        """
        if not self.resized_from_glpane:
            self.editCommand.struct.width   =  self.widthDblSpinBox.value()
            self.editCommand.struct.height  =  self.heightDblSpinBox.value() 
        if gl_update:
            self.editCommand.struct.glpane.gl_update()

    def changePlanePlacement(self, buttonId):
        """
        Slot to change the placement of the plane depending upon the 
        option checked in the "Placement Options" group box of the PM.

        @param buttonId: The button id of the selected radio button (option).
        @type  buttonId: int
        """       

        if buttonId == 0:
            msg = "Create a Plane parallel to the screen. \
                With <b>Parallel to Screen</b> plane placement option, the \
                center of the plane is always (0,0,0)" 
            self.updateMessage(msg)
            self.editCommand.placePlaneParallelToScreen()            
        elif buttonId == 1:
            msg = "Create a Plane with center coinciding with the common center\
                of <b> 3 or more selected atoms </b>. If exactly 3 atoms are \
                selected, the Plane will pass through those atoms."        
            self.updateMessage(msg)            
            self.editCommand.placePlaneThroughAtoms()
            if self.editCommand.logMessage:
                env.history.message(self.editCommand.logMessage)
        elif buttonId == 2:
            msg = "Create a Plane at an <b>offset</b> to the selected plane\
                indicated by the direction arrow. \
                you can click on the direction arrow to reverse its direction."
            self.updateMessage(msg)            
            self.editCommand.placePlaneOffsetToAnother()
            if self.editCommand.logMessage:
                env.history.message(self.editCommand.logMessage)
        elif buttonId == 3:
            #'Custom' plane placement. Do nothing (only update message box)
            # Fixes bug 2439
            msg = "Create a plane with a <b>Custom</b> plane placement. \
                The plane is placed parallel to the screen, with \
                center at (0, 0, 0). User can then modify the plane placement."
            self.updateMessage(msg)

    def update_spinboxes(self):
        """
        Update the width and height spinboxes.
        """
        # self.resized_from_glpane flag makes sure that the 
        # spinbox.valueChanged()
        # signal is not emitted after calling spinbox.setValue(). 
        # This flag is used in change_plane_size method.-- Ninad 20070601
        if self.editCommand and self.editCommand.struct:
            self.resized_from_glpane = True
            self.heightDblSpinBox.setValue(self.editCommand.struct.height)
            self.widthDblSpinBox.setValue(self.editCommand.struct.width)
            self.editCommand.struct.glpane.gl_update()
            self.resized_from_glpane = False

    def _enableAspectRatioSpinBox(self, enable):
        """
        Slot for "Maintain Aspect Ratio" checkbox which enables or disables
        the Aspect Ratio spin box.

        @param enable: True = enable, False = disable.
        @type  enable: bool
        """

        self.aspectRatioSpinBox.setEnabled(enable)

    def _updateAspectRatio(self):
        """
        Updates the Aspect Ratio spin box based on the current width and height.
        """
        aspectRatio = self.editCommand.struct.width / self.editCommand.struct.height
        self.aspectRatioSpinBox.setValue(aspectRatio)


    def update_props_if_needed_before_closing(self):
        """
        This updates some cosmetic properties of the Plane (e.g. fill color, 
        border color, etc.) before closing the Property Manager.
        """

        # Example: The Plane Property Manager is open and the user is 
        # 'previewing' the plane. Now the user clicks on "Build > Atoms" 
        # to invoke the next command (without clicking "Done"). 
        # This calls openPropertyManager() which replaces the current PM 
        # with the Build Atoms PM.  Thus, it creates and inserts the Plane 
        # that was being previewed. Before the plane is permanently inserted
        # into the part, it needs to change some of its cosmetic properties
        # (e.g. fill color, border color, etc.) which distinguishes it as 
        # a new plane in the part. This function changes those properties.
        # ninad 2007-06-13 

        #called in updatePropertyManager in MWsemeantics.py --(Partwindow class)

        EditCommand_PM.update_props_if_needed_before_closing(self)

        #Don't draw the direction arrow when the object is finalized. 
        if self.editCommand.struct and \
           self.editCommand.struct.offsetParentGeometry:

            dirArrow = self.editCommand.struct.offsetParentGeometry.directionArrow 
            dirArrow.setDrawRequested(False)

    def updateMessage(self, msg = ''):
        """
        Updates the message box with an informative message
        @param message: Message to be displayed in the Message groupbox of 
                        the property manager
        @type  message: string
        """
        self.MessageGroupBox.insertHtmlMessage(msg, 
                                               setAsDefault = False,
                                               minLines     = 5)

    def rotate_90(self):
        """
        Rotate the image clockwise.
        """
        if self.editCommand.struct is not None:
            self.editCommand.struct.rotateImage(0)
        return

    def rotate_neg_90(self):
        """
        Rotate the image counterclockwise.
        """
        if self.editCommand.struct is not None:
            self.editCommand.struct.rotateImage(1)
        return

    def flip_image(self):
        """ 
        Flip the image horizontally.
        """
        if self.editCommand.struct is not None:
            self.editCommand.struct.mirrorImage(1)
        return

    def mirror_image(self):
        """
        Flip the image vertically.
        """
        if self.editCommand.struct is not None:
            self.editCommand.struct.mirrorImage(0)
        return
