# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
An example of a structure generator's user interface
meant to be a template for developers.

The AtomGeneratorDialog class is an example of how PropMgrBaseClass
is used to build a structure generator's user interface (dialog) in
NanoEngineer-1.  The key points of interest are the methods: __init__,
addGroupBoxes and add_whats_this_text.  They all **must always** be
overridden when a new structure generator dialog class is defined.

The class variables <title> and <iconPath> should be changed to fit the
new structure generator's role.

The class static variables (prefixed with _s) and their accessor
methods (Get.../Set...) are purely for the sake of example and may
be omitted from any new implementation.

@author: Jeff Birac
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
  Jeff 2007-05-29: Based on Mark Sims' GrapheneGeneratorDialog.py, v1.17

            Convention of variables' names:

                   variable's role     prefix      examples
                  -----------------   --------    ----------
                - incoming parameter    in...      inData
                                                   inObjectPointer

                - outgoing parameter               outBufferPointer
                  or function return    out...     outCalculation

                - I/O parameter         io...      ioDataBuffer

                - static variable       s...       sDefaultValue

                - local variable        the...     theUserName
                                                   theTempValue

                - class member          m...       mObjectName
                  (aka attribute or                mPosition
                  instance variable)               mColor

  Mark 2007-07-24: Uses new PM module.

"""

from utilities.icon_utilities import geticon, getpixmap

from PyQt4.Qt import Qt, SIGNAL

from PM.PM_Dialog          import PM_Dialog
from PM.PM_GroupBox        import PM_GroupBox
from PM.PM_DoubleSpinBox   import PM_DoubleSpinBox
from PM.PM_ComboBox        import PM_ComboBox
from PM.PM_SpinBox         import PM_SpinBox
from PM.PM_TextEdit        import PM_TextEdit
from PM.PM_PushButton      import PM_PushButton
from PM.PM_LineEdit        import PM_LineEdit
from PM.PM_CheckBox        import PM_CheckBox
from PM.PM_RadioButton     import PM_RadioButton

from PM.PM_ElementChooser     import PM_ElementChooser

from mock import Mock

class AtomGeneratorPropertyManager(PM_Dialog):
    """ Implements user interface to specify properties of an atom """

    __metaclass__ = Mock()

    # The title that appears in the property manager header.
    title = "Insert Atom"
    # The name of this property manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to PNG file that appears in the header.
    iconPath = "ui/actions/Command Toolbar/BuildAtoms/InsertAtom.png"

    # Jeff 20070530:
    # Private static variables (prefixed with '_s') are used to assure consistency
    # between related widgets and simplify code revision.
    # Example: The unit for coordinates is specified by _sCoordinateUnit.  All
    # widgets related to coordinates should refer to _sCoordinateUnit rather than
    # hardcoding the unit for each coordinate widget.  The advantage comes when
    # a later revision uses different units (or chosen possibly via a user
    # preference), the value of only _sCoordinateUnit (not blocks of code)
    # needs to be changed.  All related widgets follow the new choice for units.

    _sMinCoordinateValue   = -30.0
    _sMaxCoordinateValue   =  30.0
    _sStepCoordinateValue  =  0.1
    _sCoordinateDecimals   =  3
    _sCoordinateUnit       =  'Angstrom'
    _sCoordinateUnits      =  _sCoordinateUnit + 's'

    def __init__(self):
        """
        Construct the Atom Property Manager.
        """
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        self.addGroupBoxes()
        self.add_whats_this_text()

        msg = "Edit the Atom parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert the atom \
        into the model."

        # This causes the "Message" box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault = False )

    def getCartesianCoordinates(self):
        """
        Gets the cartesian coordinates for the position of the atom
        specified in the coordinate spin boxes of the Atom Generator
        property manager.
        """
        return ( self.xCoordinateField.value,
                 self.yCoordinateField.value,
                 self.zCoordinateField.value )

    def getMinCoordinateValue(self):
        """
        Get the minimum value allowed in the coordinate spin boxes
        of the Atom Generator property manager.
        """
        return self.sel_sMinCoordinateValue

    def getMaxCoordinateValue(self):
        """
        Get the maximum value allowed in the coordinate
        spin boxes of the Atom Generator property manager.
        """
        return self._sMaxCoordinateValue

    def getStepCoordinateValue(self):
        """
        Get the value by which a coordinate increases/decreases
        when the user clicks an arrow of a coordinate spin box
        in the Atom Generator property manager.
        """
        return self._sStepCoordinateValue

    def getCoordinateDecimals(self):
        """
        Get the number of decimal places given for a value in a
        coordinate spin box in the Atom Generator property manager.
        """
        return self._sStepCoordinateValue

    def getCoordinateUnit(self):
        """
        Get the unit (of measure) for the coordinates of the
        generated atom's position.
        """
        return self._sCoordinateUnit

    def setCartesianCoordinates( self, inX, inY, inZ ):
        """
        Set the cartesian coordinates for the position of the atom
        specified in the coordinate spin boxes of the Atom Generator
        property manager.
        """
        # We may want to restrict
        self.xCoordinateField.value  =  inX
        self.yCoordinateField.value  =  inY
        self.zCoordinateField.value  =  inZ

    def setMinCoordinateValue( self, inMin ):
        """
        Set the minimum value allowed in the coordinate spin boxes
        of the Atom Generator property manager.
        """
        self._sMinCoordinateValue  =  inMin

    def setMaxCoordinateValue( self, inMax ):
        """
        Set the maximum value allowed in the coordinate
        spin boxes of the Atom Generator property manager.
        """
        self._sMaxCoordinateValue  =  inMax

    def setStepCoordinateValue( self, inStep ):
        """
        Set the value by which a coordinate increases/decreases
        when the user clicks an arrow of a coordinate spin box
        in the Atom Generator property manager.
        """
        self._sStepCoordinateValue  =  inStep

    def setCoordinateDecimals( self, inDecimals ):
        """
        Set the number of decimal places given for a value in a
        coordinate spin box in the Atom Generator property manager.
        """
        self._sStepCoordinateValue  =  inDecimals

    def setCoordinateUnit( self, inUnit ):
        """
        Set the unit(s) (of measure) for the coordinates of the
        generated atom's position.
        """
        self._sCoordinateUnit   =  inUnit
        self._sCoordinateUnits  =  inUnit + 's'

    def addGroupBoxes(self):
        """
        Add the 1 groupbox for the Atom Property Manager.
        """

        self.pmGroupBox1 = \
            PM_GroupBox( self,
                         title =  "Atom Position" )

        self.loadGroupBox1(self.pmGroupBox1)

        self.pmElementChooser =  PM_ElementChooser(self)

        AddTestGroupBoxes = True # For testing. Mark 2007-05-24

        if not AddTestGroupBoxes: # Add test widgets to their own groupbox.
            return


        """
        self.testGroupBox1 = \
            PM_GroupBox( self,
                         title = "Test Widgets1" )

        self.loadTestWidgets1(self.testGroupBox1)

        self.pmLineEditGroupBox = \
            PM_GroupBox( self,
                         title = "PM_LineEdit Widgets" )

        self.loadLineEditGroupBox(self.pmLineEditGroupBox)
        """

        """
        self.radioButtonGroupBox = \
            PM_GroupBox( self,
                         title =  "PM_RadioButtons" )

        self.loadRadioButtonGroupBox(self.radioButtonGroupBox)


        self.pmToolButtonGroupBox = \
            PM_GroupBox( self,
                         title = "MMKit Widget" )

        self.loadToolButtonGroupBox(self.pmToolButtonGroupBox)
        """

    def loadGroupBox1(self, inPmGroupBox):
        """
        Load widgets into groupbox 1.
        """

        # User input to specify x-coordinate
        # of the generated atom's position.
        self.xCoordinateField  =  \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  self._sMinCoordinateValue,
                              maximum       =  self._sMaxCoordinateValue,
                              singleStep    =  self._sStepCoordinateValue,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )

        # User input to specify y-coordinate
        # of the generated atom's position.
        self.yCoordinateField  =  \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  self._sMinCoordinateValue,
                              maximum       =  self._sMaxCoordinateValue,
                              singleStep    =  self._sStepCoordinateValue,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )

        # User input to specify z-coordinate
        # of the generated atom's position.
        self.zCoordinateField = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  self._sMinCoordinateValue,
                              maximum       =  self._sMaxCoordinateValue,
                              singleStep    =  self._sStepCoordinateValue,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )


    def add_whats_this_text(self):
        """
        What's This... text for some of the widgets in the
        Atom Property Manager.
        :Jeff 2007-05-30:
        """

        self.xCoordinateField.setWhatsThis("<b>x</b><p>: The x-coordinate (up "\
                                           "to </p>" \
                                           + str( self._sMaxCoordinateValue ) \
                                           + self._sCoordinateUnits \
                                           + ") of the Atom in " \
                                           + self._sCoordinateUnits + '.')

        self.yCoordinateField.setWhatsThis("<b>y</b><p>: The y-coordinate (up" \
                                           "to </p>"\
                                           + str( self._sMaxCoordinateValue ) \
                                           + self._sCoordinateUnits \
                                           + ") of the Atom in " \
                                           + self._sCoordinateUnits + '.')

        self.zCoordinateField.setWhatsThis("<b>z</b><p>: The z-coordinate (up" \
                                           "to </p>" \
                                           + str( self._sMaxCoordinateValue )
                                           + self._sCoordinateUnits \
                                           + ") of the Atom in "
                                           + self._sCoordinateUnits + '.')




    def loadTestWidgets1(self, inPmGroupBox):
        """
        Adds widgets to <inPmGroupBox>.
        Used for testing purposes. Mark 2007-05-24
        """

        # I intend to create a special PropMgr to display all widget types
        # for testing purposes. For now, I just add them to the end of the
        # Graphene Sheet property manager. Mark 2007-05-22

        self.spinBox = \
            PM_SpinBox( inPmGroupBox,
                        label        = "Spinbox:",
                        value        = 5,
                        setAsDefault = True,
                        minimum      = 2,
                        maximum      = 10,
                        suffix       = ' things',
                        spanWidth    = True )

        self.doubleSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox,
                              #label="Spanning DoubleSpinBox :",
                              label        = "", # No label
                              value        = 5.0,
                              setAsDefault = True,
                              minimum      = 1.0,
                              maximum      = 10.0,
                              singleStep   = 1.0,
                              decimals     = 1,
                              suffix       = ' Suffix',
                              spanWidth    = True )

        # Add a prefix example.
        self.doubleSpinBox.setPrefix("Prefix ")

        choices = [ "First", "Second", "Third (Default)", "Forth" ]

        self.comboBox1= \
            PM_ComboBox( inPmGroupBox,
                         label        = 'Choices: ',
                         choices      = choices,
                         index        = 2,
                         setAsDefault = True,
                         spanWidth    = False )

        self.comboBox2= \
            PM_ComboBox( inPmGroupBox,
                         label        = ' :Choices',
                         labelColumn  = 1,
                         choices      = choices,
                         index        = 2,
                         setAsDefault = True,
                         spanWidth    = False )

        self.comboBox3= \
            PM_ComboBox( inPmGroupBox,
                         label        = ' Choices (SpanWidth = True):',
                         labelColumn  = 1,
                         choices      = choices,
                         index        = 2,
                         setAsDefault = True,
                         spanWidth    = True )

        self.textEdit = \
            PM_TextEdit( inPmGroupBox,
                         label     = "TextEdit:",
                         spanWidth = False )


        self.spanTextEdit = \
            PM_TextEdit( inPmGroupBox,
                         label     = "",
                         spanWidth = True )


        self.groupBox = \
            PM_GroupBox( inPmGroupBox,
                         title          = "Group Box Title" )

        self.comboBox2= \
            PM_ComboBox( self.groupBox,
                         label        = "Choices:",
                         choices      = choices,
                         index        = 2,
                         setAsDefault = True,
                         spanWidth    = False )

        self.groupBox2 = \
            PM_GroupBox( inPmGroupBox,
                         title          = "Group Box Title" )

        self.comboBox3= \
            PM_ComboBox( self.groupBox2,
                         label        = "Choices:",
                         choices      = choices,
                         index        = 2,
                         setAsDefault = True,
                         spanWidth    = True )

        self.pushButton1 = \
            PM_PushButton( inPmGroupBox,
                           label = "",
                           text  = "PushButton1" )

        self.pushButton2 = \
            PM_PushButton( inPmGroupBox,
                           label     = "",
                           text      = "PushButton2",
                           spanWidth = True )

    def loadLineEditGroupBox(self, inPmGroupBox):
        """
        Load PM_LineEdit test widgets in group box.
        """

        self.lineEdit1 = \
            PM_LineEdit( inPmGroupBox,
                         label        = "Name:",
                         text         = "RotaryMotor-1",
                         setAsDefault = True,
                         spanWidth    = False)

        self.lineEdit2 = \
            PM_LineEdit( inPmGroupBox,
                         label        = ":Name",
                         labelColumn  = 1,
                         text         = "RotaryMotor-1",
                         setAsDefault = True,
                         spanWidth    = False)

        self.lineEdit3 = \
            PM_LineEdit( inPmGroupBox,
                         label        = "LineEdit (spanWidth = True):",
                         text         = "RotaryMotor-1",
                         setAsDefault = False,
                         spanWidth    = True)

    def loadCheckBoxGroupBox(self, inPmGroupBox):
        """
        Load PM_CheckBox test widgets in group box.
        """
        self.checkBoxGroupBox = \
            PM_GroupBox( inPmGroupBox,
                         title          = "<b> PM_CheckBox examples</b>" )

        self.checkBox1 = \
            PM_CheckBox( self.checkBoxGroupBox,
                         text         = "Widget on left:",
                         widgetColumn = 1,
                         state        = Qt.Checked,
                         setAsDefault = True,
                        )

        self.checkBox2 = \
            PM_CheckBox( self.checkBoxGroupBox,
                         text         = "Widget on right",
                         widgetColumn  = 1,
                         state        = Qt.Checked,
                         setAsDefault = True,
                         )


    def loadRadioButtonGroupBox(self, inPmGroupBox):
        """
        Test for PM_RadioButtonGroupBox.
        """
        #from PyQt4.Qt import QButtonGroup
        #self.radioButtonGroup = QButtonGroup()
        #self.radioButtonGroup.setExclusive(True)

        self.radioButton1 = \
            PM_RadioButton( inPmGroupBox,
                            label     = "Display PM_CheckBox group box",
                            spanWidth =  False)

        self.radioButton2 = \
            PM_RadioButton( inPmGroupBox,
                            label     = "Display PM_ComboBox group box",
                            spanWidth =  False)

        self.radioButton3 = \
            PM_RadioButton( inPmGroupBox,
                            label     = "Display PM_DoubleSpinBox group box",
                            spanWidth =  False)

        self.radioButton4 = \
            PM_RadioButton( inPmGroupBox,
                            label     = "Display PM_PushButton group box",
                            spanWidth =  False)
