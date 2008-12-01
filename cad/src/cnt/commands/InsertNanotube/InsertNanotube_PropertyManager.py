# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
InsertNanotube_PropertyManager.py

@author: Mark Sims
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Mark 2008-03-09:
- Created. Copied and edited DnaDuplexPropertyManager.py.
"""

__author__ = "Mark"



from cnt.model.Nanotube import Nanotube

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4.Qt import QAction

from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_ToolButton    import PM_ToolButton
from PM.PM_CoordinateSpinBoxes import PM_CoordinateSpinBoxes
from PM.PM_CheckBox   import PM_CheckBox

from command_support.DnaOrCnt_PropertyManager import DnaOrCnt_PropertyManager
from geometry.VQT import V
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON

from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_InsertNanotube_PropertyManager

from utilities.prefs_constants import insertNanotubeEditCommand_cursorTextCheckBox_angle_prefs_key
from utilities.prefs_constants import insertNanotubeEditCommand_cursorTextCheckBox_length_prefs_key
from utilities.prefs_constants import insertNanotubeEditCommand_showCursorTextCheckBox_prefs_key

from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

_superclass = DnaOrCnt_PropertyManager

class InsertNanotube_PropertyManager( DnaOrCnt_PropertyManager):
    """
    The InsertNanotube_PropertyManager class provides a Property Manager
    for the B{Build > Nanotube > CNT} command.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Insert Nanotube"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/BuildNanotube/InsertNanotube.png"

    def __init__( self, command ):
        """
        Constructor for the Nanotube property manager.
        """
        self.endPoint1 = None
        self.endPoint2 = None

        self.nanotube = Nanotube() # A 5x5 CNT.

        _superclass.__init__( self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

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

        change_connect( self.ntTypeComboBox,
                      SIGNAL("currentIndexChanged(const QString&)"),
                      self._ntTypeComboBoxChanged )

        change_connect(self.chiralityNSpinBox,
                       SIGNAL("valueChanged(int)"),
                       self._chiralityFixup)

        change_connect(self.chiralityMSpinBox,
                       SIGNAL("valueChanged(int)"),
                       self._chiralityFixup)

        change_connect(self.endingsComboBox,
                       SIGNAL("currentIndexChanged(const QString&)"),
                       self._endingsComboBoxChanged )

        # This spin box is currently hidden.
        change_connect(self.bondLengthDoubleSpinBox,
                       SIGNAL("valueChanged(double)"),
                       self._bondLengthChanged)

        change_connect(self.showCursorTextCheckBox,
                       SIGNAL('stateChanged(int)'),
                       self._update_state_of_cursorTextGroupBox)

    
    def show(self):
        _superclass.show(self)
        self.updateMessage("Specify the nanotube parameters below, then click "\
                           "two endpoints in the graphics area to insert a nanotube.")
    
    
    def _update_widgets_in_PM_before_show(self):
        """
        Update various widgets in this Property manager.
        Overrides MotorPropertyManager._update_widgets_in_PM_before_show.
        The various  widgets , (e.g. spinboxes) will get values from the
        structure for which this propMgr is constructed for
        (self.editcCntroller.struct)

        @see: MotorPropertyManager._update_widgets_in_PM_before_show
        @see: self.show where it is called.
        """
        pass

    def _addGroupBoxes( self ):
        """
        Add the Insert Nanotube Property Manager group boxes.
        """

        self._pmGroupBox1 = PM_GroupBox( self, title = "Endpoints" )
        self._loadGroupBox1( self._pmGroupBox1 )
        self._pmGroupBox1.hide()

        self._pmGroupBox2 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox2( self._pmGroupBox2 )

        self._displayOptionsGroupBox = PM_GroupBox( self,
                                                    title = "Display Options" )
        self._loadDisplayOptionsGroupBox( self._displayOptionsGroupBox )

        self._pmGroupBox3 = PM_GroupBox( self, title = "Nanotube Distortion" )
        self._loadGroupBox3( self._pmGroupBox3 )
        self._pmGroupBox3.hide() #@ Temporary.

        self._pmGroupBox4 = PM_GroupBox( self, title = "Multi-Walled CNTs" )
        self._loadGroupBox4( self._pmGroupBox4 )
        self._pmGroupBox4.hide() #@ Temporary.

        self._pmGroupBox5 = PM_GroupBox( self, title = "Advanced Options" )
        self._loadGroupBox5( self._pmGroupBox5 )
        self._pmGroupBox5.hide() #@ Temporary.

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 1.
        """
        #Following toolbutton facilitates entering a temporary NanotubeLineMode
        #to create a CNT using endpoints of the specified line.
        self.specifyCntLineButton = PM_ToolButton(
            pmGroupBox,
            text = "Specify Endpoints",
            iconPath  = "ui/actions/Properties Manager/Pencil.png",
            spanWidth = True
        )
        self.specifyCntLineButton.setCheckable(True)
        self.specifyCntLineButton.setAutoRaise(True)
        self.specifyCntLineButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon)

        #EndPoint1 and endPoint2 coordinates. These widgets are hidden
        # as of 2007- 12 - 05
        self._endPoint1SpinBoxes = PM_CoordinateSpinBoxes(pmGroupBox,
                                                label = "End Point 1")
        self.x1SpinBox = self._endPoint1SpinBoxes.xSpinBox
        self.y1SpinBox = self._endPoint1SpinBoxes.ySpinBox
        self.z1SpinBox = self._endPoint1SpinBoxes.zSpinBox

        self._endPoint2SpinBoxes = PM_CoordinateSpinBoxes(pmGroupBox,
                                                label = "End Point 2")
        self.x2SpinBox = self._endPoint2SpinBoxes.xSpinBox
        self.y2SpinBox = self._endPoint2SpinBoxes.ySpinBox
        self.z2SpinBox = self._endPoint2SpinBoxes.zSpinBox

        self._endPoint1SpinBoxes.hide()
        self._endPoint2SpinBoxes.hide()

    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in group box 2.
        """

        _ntTypeChoices = ['Carbon',
                          'Boron Nitride']
        self.ntTypeComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Type:",
                         choices       =  _ntTypeChoices,
                         setAsDefault  =  True)

        self.ntRiseDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Rise:",
                              value         =  self.nanotube.getRise(),
                              setAsDefault  =  True,
                              minimum       =  2.0,
                              maximum       =  4.0,
                              decimals      =  3,
                              singleStep    =  0.01 )

        self.ntRiseDoubleSpinBox.hide()

        # Nanotube Length
        self.ntLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Nanotube Length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)

        self.ntLengthLineEdit.setDisabled(True)
        self.ntLengthLineEdit.hide()

        # Nanotube diameter
        self.ntDiameterLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Diameter: ",
                         setAsDefault  =  False)

        self.ntDiameterLineEdit.setDisabled(True)
        self.updateNanotubeDiameter()

        self.chiralityNSpinBox = \
            PM_SpinBox( pmGroupBox,
                        label        = "Chirality (n):",
                        value        = self.nanotube.getChiralityN(),
                        minimum      =  2,
                        maximum      =  100,
                        setAsDefault = True )

        self.chiralityMSpinBox = \
            PM_SpinBox( pmGroupBox,
                        label        = "Chirality (m):",
                        value        = self.nanotube.getChiralityM(),
                        minimum      =  0,
                        maximum      =  100,
                        setAsDefault = True )

        # How about having user prefs for CNT and BNNT bond lengths?
        # I'm guessing that if the user wants to set these values, they will
        # do it once and would like those bond length values persist forever.
        # Need to discuss with others to determine if this spinbox comes out.
        # --Mark 2008-03-29
        self.bondLengthDoubleSpinBox = \
            PM_DoubleSpinBox( pmGroupBox,
                              label        = "Bond length:",
                              value        = self.nanotube.getBondLength(),
                              setAsDefault = True,
                              minimum      = 1.0,
                              maximum      = 3.0,
                              singleStep   = 0.1,
                              decimals     = 3,
                              suffix       = " Angstroms" )

        #self.bondLengthDoubleSpinBox.hide()

        endingChoices = ["Hydrogen", "None"] # Removed:, "Nitrogen"]

        self.endingsComboBox= \
            PM_ComboBox( pmGroupBox,
                         label        = "Endings:",
                         choices      = endingChoices,
                         index        = 0,
                         setAsDefault = True,
                         spanWidth    = False )

    def _loadGroupBox3(self, inPmGroupBox):
        """
        Load widgets in group box 3.
        """

        self.zDistortionDoubleSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Z-distortion:",
                              value        = 0.0,
                              setAsDefault = True,
                              minimum      = 0.0,
                              maximum      = 10.0,
                              singleStep   = 0.1,
                              decimals     = 3,
                              suffix       = " Angstroms" )

        self.xyDistortionDoubleSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "XY-distortion:",
                              value        = 0.0,
                              setAsDefault = True,
                              minimum      = 0.0,
                              maximum      = 2.0,
                              singleStep   = 0.1,
                              decimals     = 3,
                              suffix       = " Angstroms" )

        self.twistSpinBox = \
            PM_SpinBox( inPmGroupBox,
                        label        = "Twist:",
                        value        = 0,
                        setAsDefault = True,
                        minimum      = 0,
                        maximum      = 100, # What should maximum be?
                        suffix       = " deg/A" )

        self.bendSpinBox = \
            PM_SpinBox( inPmGroupBox,
                        label        = "Bend:",
                        value        = 0,
                        setAsDefault = True,
                        minimum      = 0,
                        maximum      = 360,
                        suffix       = " deg" )

    def _loadGroupBox4(self, inPmGroupBox):
        """
        Load widgets in group box 4.
        """

        # "Number of Nanotubes" SpinBox
        self.mwntCountSpinBox = \
            PM_SpinBox( inPmGroupBox,
                        label        = "Number:",
                        value        = 1,
                        setAsDefault = True,
                        minimum      = 1,
                        maximum      = 10,
                        suffix       = " nanotubes" )

        self.mwntCountSpinBox.setSpecialValueText("SWNT")

        # "Spacing" lineedit.
        self.mwntSpacingDoubleSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Spacing:",
                              value        = 2.46,
                              setAsDefault = True,
                              minimum      = 1.0,
                              maximum      = 10.0,
                              singleStep   = 0.1,
                              decimals     = 3,
                              suffix       = " Angstroms" )

    def _loadGroupBox5(self, pmGroupBox):
        """
        Load widgets in group box 5.
        """
        self._rubberbandLineGroupBox = PM_GroupBox(
            pmGroupBox,
            title = 'Rubber band Line:')

        ntLineChoices = ['Ladder']
        self.ntRubberBandLineDisplayComboBox = \
            PM_ComboBox( self._rubberbandLineGroupBox ,
                         label         =  " Display as:",
                         choices       =  ntLineChoices,
                         setAsDefault  =  True)

        self.lineSnapCheckBox = \
            PM_CheckBox(self._rubberbandLineGroupBox ,
                        text         = 'Enable line snap' ,
                        widgetColumn = 1,
                        state        = Qt.Checked
                        )


    def _connect_showCursorTextCheckBox(self):
        """
        Connect the show cursor text checkbox with user prefs_key.
        Overrides
        DnaOrCnt_PropertyManager._connect_showCursorTextCheckBox
        """
        connect_checkbox_with_boolean_pref(
            self.showCursorTextCheckBox ,
            insertNanotubeEditCommand_showCursorTextCheckBox_prefs_key )


    def _params_for_creating_cursorTextCheckBoxes(self):
        """
        Returns params needed to create various cursor text checkboxes connected
        to prefs_keys  that allow custom cursor texts.
        @return: A list containing tuples in the following format:
                ('checkBoxTextString' , preference_key). PM_PrefsCheckBoxes
                uses this data to create checkboxes with the the given names and
                connects them to the provided preference keys. (Note that
                PM_PrefsCheckBoxes puts thes within a GroupBox)
        @rtype: list
        @see: PM_PrefsCheckBoxes
        @see: self._loadDisplayOptionsGroupBox where this list is used.
        @see: Superclass method which is overridden here --
        DnaOrCnt_PropertyManager._params_for_creating_cursorTextCheckBoxes()
        """
        params = \
               [  #Format: (" checkbox text", prefs_key)

                   ("Nanotube length",
                    insertNanotubeEditCommand_cursorTextCheckBox_length_prefs_key ),

                    ("Angle",
                     insertNanotubeEditCommand_cursorTextCheckBox_angle_prefs_key )
                 ]

        return params


    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the Insert Nanotube Property Manager.
        """
        pass

    def _setEndPoints(self):
        """
        Set the two endpoints of the nanotube using the values from the
        X, Y, Z coordinate spinboxes in the property manager.

        @note: The group box containing the 2 sets of XYZ spin boxes are
        currently hidden.
        """
        # First endpoint (origin) of nanotube
        x1 = self.x1SpinBox.value()
        y1 = self.y1SpinBox.value()
        z1 = self.z1SpinBox.value()

        # Second endpoint (direction vector/axis) of nanotube.
        x2 = self.x2SpinBox.value()
        y2 = self.y2SpinBox.value()
        z2 = self.z2SpinBox.value()

        if not self.endPoint1:
            self.endPoint1 = V(x1, y1, z1)
        if not self.endPoint2:
            self.endPoint2 = V(x2, y2, z2)

        self.nanotube.setEndPoints(self.endPoint1, self.endPoint2)
            # Need arg "recompute=True", which will recompute the second
            # endpoint (endPoint2) using the nanotube rise.

    def getParameters(self):
        """
        Return the parameters from this property manager to be used to create
        the nanotube.

        @return: A nanotube instance with its attrs set to the current
                 parameters in the property manager.
        @rtype: L{Nanotube}

        @see: L{InsertNanotube_EditCommand._gatherParameters} where this is used
        """
        self._setEndPoints()
        return (self.nanotube)

    def _ntTypeComboBoxChanged( self, type ):
        """
        Slot for the Type combobox. It is called whenever the
        Type choice is changed.

        @param inIndex: The new index.
        @type  inIndex: int
        """
        self.nanotube.setType(str(type))
        self.bondLengthDoubleSpinBox.setValue(self.nanotube.getBondLength())
        #self.bondLengthDoubleSpinBox.setValue(ntBondLengths[inIndex])

    def _bondLengthChanged(self, bondLength):
        """
        Slot for the B{Bond Length} spinbox.
        """
        self.nanotube.setBondLength(bondLength)
        self.updateNanotubeDiameter()
        return

    def _chiralityFixup(self, spinBoxValueJunk = None):
        """
        Slot for several validators for different parameters.
        This gets called whenever the user changes the n, m chirality values.

        @param spinBoxValueJunk: This is the Spinbox value from the valueChanged
                                 signal. It is not used. We just want to know
                                 that the spinbox value has changed.
        @type  spinBoxValueJunk: double or None
        @see: PM_SpinBox.setValue() for a note about blockSignals. 
        """
        _n, _m = self.nanotube.setChirality(self.chiralityNSpinBox.value(),
                                            self.chiralityMSpinBox.value())

        #self.n, self.m = self.nanotube.getChirality()
        
        #QSpinBox.setValue emits valueChanged signal. We don't want that here. 
        #so temporarily blockSignal by passing the blockSignals flag. 
        self.chiralityNSpinBox.setValue(_n, blockSignals = True)
        self.chiralityMSpinBox.setValue(_m, blockSignals = True)
        
        self.updateNanotubeDiameter()

    def updateNanotubeDiameter(self):
        """
        Update the nanotube Diameter lineEdit widget.
        """
        diameterText = "%-7.4f Angstroms" %  (self.nanotube.getDiameter())
        self.ntDiameterLineEdit.setText(diameterText)

        # ntRiseDoubleSpinBox is currently hidden.
        self.ntRiseDoubleSpinBox.setValue(self.nanotube.getRise())

    def _endingsComboBoxChanged(self, endings):
        """
        Slot for the B{Ending} combobox.

        @param endings: The option's text.
        @type  endings: string
        """
        self.nanotube.setEndings(str(endings))
        return

    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.
        """
        whatsThis_InsertNanotube_PropertyManager(self)
        return

