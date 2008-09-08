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
from PM.PM_Constants     import PM_RESTORE_DEFAULTS_BUTTON
from PM.PM_FileChooser   import PM_FileChooser
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_ColorComboBox import PM_ColorComboBox
from command_support.EditCommand_PM import EditCommand_PM
import foundation.env as env
from utilities.constants import yellow, orange, red, magenta
from utilities.constants import cyan, blue, white, black, gray
from utilities.constants import  PLANE_ORIGIN_LOWER_LEFT
from utilities.constants import  PLANE_ORIGIN_LOWER_RIGHT
from utilities.constants import  PLANE_ORIGIN_UPPER_LEFT
from utilities.constants import  PLANE_ORIGIN_UPPER_RIGHT
from utilities.constants import LABELS_ALONG_ORIGIN, LABELS_ALONG_PLANE_EDGES
from utilities.prefs_constants import PlanePM_showGridLabels_prefs_key, PlanePM_showGrid_prefs_key

from utilities import debug_flags
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

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

    def __init__(self, command):
        """
        Construct the Plane Property Manager.

        @param plane: The plane.
        @type  plane: L{Plane}
        """

        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False


        EditCommand_PM.__init__( self, command) 



        msg = "Insert a Plane parallel to the screen. Note: This feature is "\
            "experimental for Alpha9 and has known bugs."

        # This causes the "Message" box to be displayed as well.
        self.updateMessage(msg)

        # self.resized_from_glpane flag makes sure that the 
        #spinbox.valueChanged()
        # signal is not emitted after calling spinbox.setValue.
        self.resized_from_glpane = False

        # Hide Preview and Restore defaults button for Alpha9.
        self.hideTopRowButtons(PM_RESTORE_DEFAULTS_BUTTON)
        # needed to figure out if the model has changed or not
        self.previousPMParams = None
        self.gridColor = black
        self.gridXSpacing = 4.0
        self.gridYSpacing = 4.0
        self.gridLineType = 3
        self.displayLabels = False
        self.originLocation = PLANE_ORIGIN_LOWER_LEFT
        self.displayLabelStyle = LABELS_ALONG_ORIGIN

    def _addGroupBoxes(self):
        """
        Add the 1st group box to the Property Manager.
        """
        # Placement Options radio button list to create radio button list.
        # Format: buttonId, buttonText, tooltip
        PLACEMENT_OPTIONS_BUTTON_LIST = [ \
            ( 0, "Parallel to screen",     "Parallel to screen"     ),
            ( 1, "Through selected atoms", "Through selected atoms" ),
            ( 2, "Offset to a plane",      "Offset to a plane"      ),
            ( 3, "Custom",                 "Custom"                 )
        ]

        self.pmPlacementOptions = \
            PM_RadioButtonList( self,
                                title      = "Placement Options", 
                                buttonList = PLACEMENT_OPTIONS_BUTTON_LIST,
                                checkedId  = 3 )

        self.pmGroupBox1 = PM_GroupBox(self, title = "Parameters")
        self._loadGroupBox1(self.pmGroupBox1)

        #image groupbox
        self.pmGroupBox2 = PM_GroupBox(self, title = "Image")
        self._loadGroupBox2(self.pmGroupBox2)

        #grid plane groupbox
        self.pmGroupBox3 = PM_GroupBox(self, title = "Grid")
        self._loadGroupBox3(self.pmGroupBox3)

    def _loadGroupBox3(self, pmGroupBox):
        """
        Load widgets in the grid plane group box.

        @param pmGroupBox: The grid  group box in the PM.
        @type  pmGroupBox: L{PM_GroupBox}
        """
        self.gridPlaneCheckBox = \
            PM_CheckBox( pmGroupBox,
                         text         = "Show grid",
                         widgetColumn  = 0,
                         setAsDefault = True,
                         spanWidth = True
                         )

        connect_checkbox_with_boolean_pref(
            self.gridPlaneCheckBox ,
            PlanePM_showGrid_prefs_key)


        self.gpXSpacingDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "X Spacing:",
                              value         =  4.000,
                              setAsDefault  =  True,
                              minimum       =  1.00,
                              maximum       =  200.0,
                              decimals      =  3,
                              singleStep    =  1.0, 
                              spanWidth = False)

        self.gpYSpacingDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Y Spacing:",
                              value         =  4.000,
                              setAsDefault  =  True,
                              minimum       =  1.00,
                              maximum       =  200.0,
                              decimals      =  3,
                              singleStep    =  1.0, 
                              spanWidth = False)

        lineTypeChoices = [ 'Dotted (default)',
                            'Dashed',
                            'Solid' ]

        self.gpLineTypeComboBox = \
            PM_ComboBox( pmGroupBox ,     
                         label         =  "Line type:", 
                         choices       =  lineTypeChoices,
                         setAsDefault  =  True)

        hhColorList = [ black, orange, red, magenta, 
                        cyan, blue, white, yellow, gray ]
        hhColorNames = [ "Black (default)", "Orange", "Red", "Magenta", 
                         "Cyan", "Blue", "White", "Yellow", "Other color..." ]

        self.gpColorTypeComboBox = \
            PM_ColorComboBox( pmGroupBox,
                              colorList = hhColorList,
                              colorNames = hhColorNames,
                              color = black )

        self.pmGroupBox5 = PM_GroupBox( pmGroupBox )

        self.gpDisplayLabels =\
            PM_CheckBox( self.pmGroupBox5,
                         text         = "Display labels",
                         widgetColumn  = 0,
                         state        = Qt.Unchecked,
                         setAsDefault = True,
                         spanWidth = True )

        originChoices = [ 'Lower left (default)',
                          'Upper left',
                          'Lower right',
                          'Upper right' ]

        self.gpOriginComboBox = \
            PM_ComboBox( self.pmGroupBox5 ,     
                         label         =  "Origin:", 
                         choices       =  originChoices,
                         setAsDefault  =  True )

        positionChoices = [ 'Origin axes (default)',
                            'Plane perimeter' ]

        self.gpPositionComboBox = \
            PM_ComboBox( self.pmGroupBox5 ,     
                         label         =  "Position:", 
                         choices       =  positionChoices,
                         setAsDefault  =  True)

        self._showHideGPWidgets()

        if env.prefs[PlanePM_showGridLabels_prefs_key]:
            self.displayLabels = True
            self.gpOriginComboBox.setEnabled( True )
            self.gpPositionComboBox.setEnabled( True )
        else:
            self.displayLabels = False
            self.gpOriginComboBox.setEnabled( False )
            self.gpPositionComboBox.setEnabled( False )

        return

    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        #TODO: Fix for bug: When you invoke a temporary mode 
        # entering such a temporary mode keeps the signals of 
        #PM from the previous mode connected (
        #but while exiting that temporary mode and reentering the 
        #previous mode, it actually reconnects the signal! This gives rise to 
        #lots  of bugs. This needs more general fix in Temporary mode API. 
        # -- Ninad 2008-01-09 (similar comment exists in MovePropertyManager.py

        #UPDATE: (comment copied and modifief from BuildNanotube_PropertyManager. 
        #The general problem still remains -- Ninad 2008-06-25

        if isConnect and self.isAlreadyConnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to connect widgets"\
                                    "in this PM that are already connected." )
            return 

        if not isConnect and self.isAlreadyDisconnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to disconnect widgets"\
                                    "in this PM that are already disconnected.")
            return

        self.isAlreadyConnected = isConnect
        self.isAlreadyDisconnected = not isConnect

        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 

        change_connect(self.pmPlacementOptions.buttonGroup,
                       SIGNAL("buttonClicked(int)"),
                       self.changePlanePlacement)

        change_connect(self.widthDblSpinBox, 
                       SIGNAL("valueChanged(double)"), 
                       self.change_plane_width)

        change_connect(self.heightDblSpinBox, 
                       SIGNAL("valueChanged(double)"), 
                       self.change_plane_height)

        change_connect(self.aspectRatioCheckBox,
                       SIGNAL("stateChanged(int)"),
                       self._enableAspectRatioSpinBox)


        #signal slot connection for imageDisplayCheckBox
        change_connect(self.imageDisplayCheckBox, 
                       SIGNAL("stateChanged(int)"), 
                       self.toggleFileChooserBehavior)

        #signal slot connection for imageDisplayFileChooser
        change_connect(self.imageDisplayFileChooser.lineEdit, 
                       SIGNAL("editingFinished()"),
                       self.update_imageFile)

        #signal slot connection for heightfieldDisplayCheckBox
        change_connect(self.heightfieldDisplayCheckBox, 
                       SIGNAL("stateChanged(int)"), 
                       self.toggleHeightfield)

        #signal slot connection for heightfieldHQDisplayCheckBox
        change_connect(self.heightfieldHQDisplayCheckBox, 
                       SIGNAL("stateChanged(int)"), 
                       self.toggleHeightfieldHQ)        

        #signal slot connection for heightfieldTextureCheckBox
        change_connect(self.heightfieldTextureCheckBox, 
                       SIGNAL("stateChanged(int)"), 
                       self.toggleTexture)

        #signal slot connection for vScaleSpinBox
        change_connect(self.vScaleSpinBox, 
                       SIGNAL("valueChanged(double)"), 
                       self.change_vertical_scale)

        change_connect(self.plusNinetyButton,
                       SIGNAL("clicked()"),
                       self.rotate_90)

        change_connect(self.minusNinetyButton,
                       SIGNAL("clicked()"),
                       self.rotate_neg_90)

        change_connect(self.flipButton,
                       SIGNAL("clicked()"),
                       self.flip_image)

        change_connect(self.mirrorButton,
                       SIGNAL("clicked()"),
                       self.mirror_image)

        change_connect(self.gridPlaneCheckBox, 
                       SIGNAL("stateChanged(int)"), 
                       self.displayGridPlane)

        change_connect(self.gpXSpacingDoubleSpinBox,
                       SIGNAL("valueChanged(double)"),
                       self.changeXSpacingInGP)

        change_connect(self.gpYSpacingDoubleSpinBox,
                       SIGNAL("valueChanged(double)"),
                       self.changeYSpacingInGP)

        change_connect( self.gpLineTypeComboBox,
                        SIGNAL("currentIndexChanged(int)"),
                        self.changeLineTypeInGP )

        change_connect( self.gpColorTypeComboBox,
                        SIGNAL("editingFinished()"),
                        self.changeColorTypeInGP )

        change_connect( self.gpDisplayLabels,
                        SIGNAL("stateChanged(int)"),
                        self.displayLabelsInGP )

        change_connect( self.gpOriginComboBox,
                        SIGNAL("currentIndexChanged(int)"),
                        self.changeOriginInGP )

        change_connect( self.gpPositionComboBox,
                        SIGNAL("currentIndexChanged(int)"),
                        self.changePositionInGP )

        self._connect_checkboxes_to_global_prefs_keys()

        return

    def _connect_checkboxes_to_global_prefs_keys(self):
        """
        """
        connect_checkbox_with_boolean_pref(
            self.gridPlaneCheckBox ,
            PlanePM_showGrid_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.gpDisplayLabels, 
            PlanePM_showGridLabels_prefs_key)


    def changePositionInGP(self, idx):
        """
        Change Display of origin Labels (choices are along origin edges or along
        the plane perimeter.
        @param idx: Current index of the change grid label position combo box
        @type idx: int
        """
        if idx == 0:
            self.displayLabelStyle = LABELS_ALONG_ORIGIN
        elif idx == 1:
            self.displayLabelStyle = LABELS_ALONG_PLANE_EDGES
        else:
            print "Invalid index", idx
        return

    def changeOriginInGP(self, idx):
        """
        Change Display of origin Labels based on the location of the origin
        @param idx: Current index of the change origin position combo box
        @type idx: int
        """
        if idx == 0:
            self.originLocation = PLANE_ORIGIN_LOWER_LEFT
        elif idx ==1:
            self.originLocation = PLANE_ORIGIN_UPPER_LEFT
        elif idx == 2:
            self.originLocation = PLANE_ORIGIN_LOWER_RIGHT
        elif idx == 3:
            self.originLocation = PLANE_ORIGIN_UPPER_RIGHT
        else:
            print "Invalid index", idx
        return

    def displayLabelsInGP(self, state):
        """
        Choose to show or hide grid labels
        @param state: State of the Display Label Checkbox 
        @type state: boolean
        """
        if env.prefs[PlanePM_showGridLabels_prefs_key]:
            self.gpOriginComboBox.setEnabled(True)
            self.gpPositionComboBox.setEnabled(True)
            self.displayLabels = True
            self.originLocation = PLANE_ORIGIN_LOWER_LEFT
            self.displayLabelStyle = LABELS_ALONG_ORIGIN
        else:
            self.gpOriginComboBox.setEnabled(False)
            self.gpPositionComboBox.setEnabled(False)
            self.displayLabels = False
        return

    def changeColorTypeInGP(self):
        """
        Change Color of grid
        """
        self.gridColor = self.gpColorTypeComboBox.getColor()
        return

    def changeLineTypeInGP(self, idx):
        """
        Change line type in grid
        @param idx: Current index of the Line type combo box
        @type idx: int
        """
        #line_type for actually drawing the grid is: 0=None, 1=Solid, 2=Dashed" or 3=Dotted
        if idx == 0:
            self.gridLineType = 3
        if idx == 1:
            self.gridLineType = 2
        if idx == 2:
            self.gridLineType = 1   
        return

    def changeYSpacingInGP(self, val):
        """
        Change Y spacing on the grid
        @param val:value of Y spacing
        @type val: double
        """
        self.gridYSpacing = float(val)
        return

    def changeXSpacingInGP(self, val):
        """
        Change X spacing on the grid
        @param val:value of X spacing
        @type val: double
        """
        self.gridXSpacing = float(val)
        return

    def displayGridPlane(self, state):
        """
        Display or hide grid based on the state of the checkbox
        @param state: State of the Display Label Checkbox 
        @type state: boolean
        """
        self._showHideGPWidgets()
        if self.gridPlaneCheckBox.isChecked():
            env.prefs[PlanePM_showGrid_prefs_key] = True
            self._makeGridPlane()
        else:
            env.prefs[PlanePM_showGrid_prefs_key] = False

        return 

    def _makeGridPlane(self):
        """
        Show grid on the plane
        """
        #get all the grid related values in here
        self.gridXSpacing = float(self.gpXSpacingDoubleSpinBox.value())
        self.gridYSpacing = float(self.gpYSpacingDoubleSpinBox.value())

        #line_type for actually drawing the grid is: 0=None, 1=Solid, 2=Dashed" or 3=Dotted
        idx = self.gpLineTypeComboBox.currentIndex()
        self.changeLineTypeInGP(idx)
        self.gridColor = self.gpColorTypeComboBox.getColor()

        return


    def _showHideGPWidgets(self):
        """
        Enable Disable grid related widgets based on the state of the show grid 
        checkbox.
        """
        if self.gridPlaneCheckBox.isChecked():
            self.gpXSpacingDoubleSpinBox.setEnabled(True)
            self.gpYSpacingDoubleSpinBox.setEnabled(True)
            self.gpLineTypeComboBox.setEnabled(True)
            self.gpColorTypeComboBox.setEnabled(True)
            self.gpDisplayLabels.setEnabled(True)        
        else:
            self.gpXSpacingDoubleSpinBox.setEnabled(False)
            self.gpXSpacingDoubleSpinBox.setEnabled(False)
            self.gpYSpacingDoubleSpinBox.setEnabled(False)
            self.gpLineTypeComboBox.setEnabled(False)
            self.gpColorTypeComboBox.setEnabled(False)
            self.gpDisplayLabels.setEnabled(False)
        return

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

        self.heightfieldDisplayCheckBox = \
            PM_CheckBox( pmGroupBox,
                         text         = "Create 3D relief",
                         widgetColumn  = 0,
                         state        = Qt.Unchecked,
                         setAsDefault = True,
                         spanWidth = True
                         )

        self.heightfieldHQDisplayCheckBox = \
            PM_CheckBox( pmGroupBox,
                         text         = "High quality",
                         widgetColumn  = 0,
                         state        = Qt.Unchecked,
                         setAsDefault = True,
                         spanWidth = True
                         )        

        self.heightfieldTextureCheckBox = \
            PM_CheckBox( pmGroupBox,
                         text         = "Use texture",
                         widgetColumn  = 0,
                         state        = Qt.Checked,
                         setAsDefault = True,
                         spanWidth = True
                         )

        self.vScaleSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                             label        = " Vertical scale:",
                             value        = 1.0, 
                             setAsDefault = True,
                             minimum      = -1000.0, # -1000 A
                             maximum      =  1000.0, # 1000 A
                             singleStep   = 0.1, 
                             decimals     = 1, 
                             suffix       = ' Angstroms')

        self.heightfieldDisplayCheckBox.setEnabled(False)
        self.heightfieldHQDisplayCheckBox.setEnabled(False)
        self.heightfieldTextureCheckBox.setEnabled(False)
        self.vScaleSpinBox.setEnabled(False)




    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in 1st group box.

        @param pmGroupBox: The 1st group box in the PM.
        @type  pmGroupBox: L{PM_GroupBox}
        """

        self.widthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             label        = "Width:",
                             value        = 16.0, 
                             setAsDefault = True,
                             minimum      = 1.0, 
                             maximum      = 10000.0, # 1000 nm
                             singleStep   = 1.0, 
                             decimals     = 1, 
                             suffix       = ' Angstroms')



        self.heightDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                             label        =" Height:",
                             value        = 16.0, 
                             setAsDefault = True,
                             minimum      = 1.0, 
                             maximum      = 10000.0, # 1000 nm
                             singleStep   = 1.0, 
                             decimals     = 1, 
                             suffix       = ' Angstroms')



        self.aspectRatioCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text         = 'Maintain Aspect Ratio of:' ,
                        widgetColumn = 1,
                        state        = Qt.Unchecked
                        )


        self.aspectRatioSpinBox = \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "",
                              value         =  1.0,
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


    def toggleFileChooserBehavior(self, checked):
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

        self.command.struct.glpane.gl_update()


    def toggleHeightfield(self, checked):
        """
        Enables 3D relief drawing mode.
        """
        if self.command and self.command.struct:
            plane = self.command.struct
            plane.display_heightfield = checked
            if checked:
                self.heightfieldHQDisplayCheckBox.setEnabled(True)
                self.heightfieldTextureCheckBox.setEnabled(True)
                self.vScaleSpinBox.setEnabled(True)                
                plane.computeHeightfield()
            else:
                self.heightfieldHQDisplayCheckBox.setEnabled(False)
                self.heightfieldTextureCheckBox.setEnabled(False)
                self.vScaleSpinBox.setEnabled(False)
                plane.heightfield = None
            plane.glpane.gl_update()

    def toggleHeightfieldHQ(self, checked):
        """
        Enables high quality rendering in 3D relief mode.
        """
        if self.command and self.command.struct:
            plane = self.command.struct
            plane.heightfield_hq = checked
            plane.computeHeightfield()
            plane.glpane.gl_update()

    def toggleTexture(self, checked):
        """
        Enables texturing in 3D relief mode.
        """
        if self.command and self.command.struct:
            plane = self.command.struct
            plane.heightfield_use_texture = checked
            #if plane.display_heightfield and plane.image:
            #    plane.computeHeightfield()
            plane.glpane.gl_update()

    def update_spinboxes(self): 	 
        """ 	 
	Update the width and height spinboxes. 	 
        @see: Plane.resizeGeometry()
	""" 	 
        # self.resized_from_glpane flag makes sure that the 	 
        # spinbox.valueChanged() 	 
        # signal is not emitted after calling spinbox.setValue(). 	 
        # This flag is used in change_plane_size method.-- Ninad 20070601 	 
        if self.command and self.command.hasValidStructure(): 	 
            self.resized_from_glpane = True 	 
            self.heightDblSpinBox.setValue(self.command.struct.height) 	 
            self.widthDblSpinBox.setValue(self.command.struct.width) 	 
            self.win.glpane.gl_update() 	 
            self.resized_from_glpane = False

    def update_imageFile(self):
        """
        Loads image file if path is valid
        """
        
        # Update buttons and checkboxes.
        self.mirrorButton.setEnabled(False)
        self.plusNinetyButton.setEnabled(False)
        self.minusNinetyButton.setEnabled(False)
        self.flipButton.setEnabled(False)
        self.heightfieldDisplayCheckBox.setEnabled(False)
        self.heightfieldHQDisplayCheckBox.setEnabled(False)
        self.heightfieldTextureCheckBox.setEnabled(False)
        self.vScaleSpinBox.setEnabled(False)

        
        plane = self.command.struct

        # Delete current image and heightfield
        plane.deleteImage()
        plane.heightfield = None
        plane.display_image = self.imageDisplayCheckBox.isChecked()

        if plane.display_image: 
            imageFile = str(self.imageDisplayFileChooser.lineEdit.text())

            from model.Plane import checkIfValidImagePath
            validPath = checkIfValidImagePath(imageFile)

            if validPath:
                from PIL import Image

                # Load image from file
                plane.image = Image.open(imageFile)
                plane.loadImage(imageFile)

                # Compute the relief image
                plane.computeHeightfield()

                if plane.image:
                    self.mirrorButton.setEnabled(True)
                    self.plusNinetyButton.setEnabled(True)
                    self.minusNinetyButton.setEnabled(True)
                    self.flipButton.setEnabled(True)
                    self.heightfieldDisplayCheckBox.setEnabled(True)
                    if plane.display_heightfield:
                        self.heightfieldHQDisplayCheckBox.setEnabled(True)
                        self.heightfieldTextureCheckBox.setEnabled(True)
                        self.vScaleSpinBox.setEnabled(True)  


    def show(self):
        """
        Show the Plane Property Manager.
        """
        EditCommand_PM.show(self)
        #It turns out that if updateCosmeticProps is called before 
        #EditCommand_PM.show, the 'preview' properties are not updated 
        #when you are editing an existing plane. Don't know the cause at this
        #time, issue is trivial. So calling it in the end -- Ninad 2007-10-03

        if self.command.struct:

            plane = self.command.struct 
            plane.updateCosmeticProps(previewing = True)
            if plane.imagePath:
                self.imageDisplayFileChooser.setText(plane.imagePath)
            self.imageDisplayCheckBox.setChecked(plane.display_image) 

    def setParameters(self, params):
        """
        """
        width, height, gridColor, gridLineType, \
             gridXSpacing, gridYSpacing, originLocation, \
             displayLabelStyle = params

        # self.resized_from_glpane flag makes sure that the 
        # spinbox.valueChanged()
        # signal is not emitted after calling spinbox.setValue(). 
        # This flag is used in change_plane_size method.-- Ninad 20070601
        self.resized_from_glpane = True
        self.widthDblSpinBox.setValue(width)
        self.heightDblSpinBox.setValue(height)  
        self.win.glpane.gl_update()
        self.resized_from_glpane = False                

        self.gpColorTypeComboBox.setColor(gridColor)
        self.gridLineType = gridLineType

        self.gpXSpacingDoubleSpinBox.setValue(gridXSpacing)
        self.gpYSpacingDoubleSpinBox.setValue(gridYSpacing)

        self.gpOriginComboBox.setCurrentIndex(originLocation)
        self.gpPositionComboBox.setCurrentIndex(displayLabelStyle)

    def getParameters(self):
        """
        """
        width = self.widthDblSpinBox.value()
        height = self.heightDblSpinBox.value()
        gridColor = self.gpColorTypeComboBox.getColor()

        params = (width, height, gridColor, self.gridLineType,
                  self.gridXSpacing, self.gridYSpacing, self.originLocation,  
                  self.displayLabelStyle)

        return params


    def change_plane_width(self, newWidth):
        """
        Slot for width spinbox in the Property Manager.

        @param newWidth: width in Angstroms.
        @type  newWidth: float
        """        
        if self.aspectRatioCheckBox.isChecked():
            self.command.struct.width   =  newWidth
            self.command.struct.height  =  self.command.struct.width / \
                self.aspectRatioSpinBox.value() 
            self.update_spinboxes()
        else:
            self.change_plane_size()
        self._updateAspectRatio()

    def change_plane_height(self, newHeight):
        """
        Slot for height spinbox in the Property Manager.

        @param newHeight: height in Angstroms.
        @type  newHeight: float
        """        
        if self.aspectRatioCheckBox.isChecked():
            self.command.struct.height  =  newHeight 
            self.command.struct.width   =  self.command.struct.height * \
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
            self.command.struct.width   =  self.widthDblSpinBox.value()
            self.command.struct.height  =  self.heightDblSpinBox.value() 
        if gl_update:
            self.command.struct.glpane.gl_update()

    def change_vertical_scale(self, scale):
        """
        Changes vertical scaling of the heightfield.
        """
        if self.command and self.command.struct:
            plane = self.command.struct
            plane.heightfield_scale = scale
            plane.computeHeightfield()
            plane.glpane.gl_update()

    def changePlanePlacement(self, buttonId):
        """
        Slot to change the placement of the plane depending upon the 
        option checked in the "Placement Options" group box of the PM.

        @param buttonId: The button id of the selected radio button (option).
        @type  buttonId: int
        """       

        if buttonId == 0:
            msg = "Create a Plane parallel to the screen. "\
                "With <b>Parallel to Screen</b> plane placement option, the "\
                "center of the plane is always (0,0,0)" 
            self.updateMessage(msg)
            self.command.placePlaneParallelToScreen()            
        elif buttonId == 1:
            msg = "Create a Plane with center coinciding with the common center "\
                "of <b> 3 or more selected atoms </b>. If exactly 3 atoms are "\
                "selected, the Plane will pass through those atoms."        
            self.updateMessage(msg)            
            self.command.placePlaneThroughAtoms()
            if self.command.logMessage:
                env.history.message(self.command.logMessage)
        elif buttonId == 2:
            msg = "Create a Plane at an <b>offset</b> to the selected plane "\
                "indicated by the direction arrow. "\
                "you can click on the direction arrow to reverse its direction."
            self.updateMessage(msg)            
            self.command.placePlaneOffsetToAnother()
            if self.command.logMessage:
                env.history.message(self.command.logMessage)
        elif buttonId == 3:
            #'Custom' plane placement. Do nothing (only update message box)
            # Fixes bug 2439
            msg = "Create a plane with a <b>Custom</b> plane placement. "\
                "The plane is placed parallel to the screen, with "\
                "center at (0, 0, 0). User can then modify the plane placement."
            self.updateMessage(msg)


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
        aspectRatio = self.command.struct.width / self.command.struct.height
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
        if self.command.struct and \
           self.command.struct.offsetParentGeometry:

            dirArrow = self.command.struct.offsetParentGeometry.directionArrow 
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
        if self.command.hasValidStructure():
            self.command.struct.rotateImage(0)
        return

    def rotate_neg_90(self):
        """
        Rotate the image counterclockwise.
        """
        if self.command.hasValidStructure():
            self.command.struct.rotateImage(1)
        return

    def flip_image(self):
        """ 
        Flip the image horizontally.
        """
        if self.command.hasValidStructure():
            self.command.struct.mirrorImage(1)
        return

    def mirror_image(self):
        """
        Flip the image vertically.
        """
        if self.command.hasValidStructure():
            self.command.struct.mirrorImage(0)
        return
