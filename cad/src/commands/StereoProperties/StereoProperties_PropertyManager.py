# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
StereoProperties_PropertyManager.py

 The StereoProperties_PropertyManager class provides a Property Manager 
 for the Stereo View command.

@author: Piotr
@version: 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""
import os, time
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui
from PM.PM_Dialog   import PM_Dialog
from PM.PM_Slider   import PM_Slider
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_StackedWidget import PM_StackedWidget
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ToolButtonRow import PM_ToolButtonRow

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton

from utilities.prefs_constants import stereoViewMode_prefs_key
from utilities.prefs_constants import stereoViewAngle_prefs_key
from utilities.prefs_constants import stereoViewSeparation_prefs_key

###from commands.StereoProperties.StereoProperties_Command import stereoEnabled

# =

class StereoProperties_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The StereoProperties_PropertyManager class provides a Property Manager 
    for the Stereo View command. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Stereo View"
    pmName        =  title
    iconPath      =  "ui/actions/View/Stereo_View.png"


    def __init__( self, parentCommand ):
        """
        Constructor for the property manager.
        """

        self.parentMode = parentCommand
        self.w = self.parentMode.w
        self.win = self.parentMode.w
        self.pw = self.parentMode.pw        
        self.o = self.win.glpane                 

        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)

        DebugMenuMixin._init1( self )

        self.showTopRowButtons( pmDoneButton | \
                                pmWhatsThisButton)

        msg = "Modify the Stereo View settings below."

        self.updateMessage(msg)

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

        change_connect(self.stereoEnabledCheckBox, 
                       SIGNAL("toggled(bool)"), 
                       self._enableStereo ) 

        change_connect( self.stereoModeComboBox,
                        SIGNAL("currentIndexChanged(int)"),
                        self._stereoModeComboBoxChanged )

        change_connect(self.stereoSeparationSlider,
                       SIGNAL("valueChanged(int)"),
                       self._stereoModeSeparationSliderChanged )

        change_connect(self.stereoAngleSlider,
                       SIGNAL("valueChanged(int)"),
                       self._stereoModeAngleSliderChanged )

    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """      
        self.win.toolsDone()

    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """  
        #TODO: Cancel button needs to be removed. See comment at the top
        self.win.toolsDone()

    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show.
        """
        PM_Dialog.show(self)
        # self.updateDnaDisplayStyleWidgets()
        self.connect_or_disconnect_signals(isConnect = True)

    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        self.connect_or_disconnect_signals(False)
        PM_Dialog.close(self)

    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self, 
                                         title = "Settings")
        self._loadGroupBox1( self._pmGroupBox1 )

        #@ self._pmGroupBox1.hide()

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """

        #stereoSettingsGroupBox = PM_GroupBox( None )

        self.stereoEnabledCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text         = 'Enable Stereo View',
                        widgetColumn = 1
                        )        

        stereoModeChoices = ['Relaxed view', 
                             'Cross-eyed view',
                             'Red/blue anaglyphs']

        self.stereoModeComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Stereo Mode:", 
                         choices       =  stereoModeChoices,
                         setAsDefault  =  True)

        self.stereoModeComboBox.setCurrentIndex(env.prefs[stereoViewMode_prefs_key]-1)

        self.stereoSeparationSlider =  \
            PM_Slider( pmGroupBox,
                       currentValue = 50,
                       minimum      = 0,
                       maximum      = 300,
                       label        = 'Separation'
                       )        

        self.stereoSeparationSlider.setValue(env.prefs[stereoViewSeparation_prefs_key])

        self.stereoAngleSlider =  \
            PM_Slider( pmGroupBox,
                       currentValue = 50,
                       minimum      = 0,
                       maximum      = 100,
                       label        = 'Angle'
                       )        

        self.stereoAngleSlider.setValue(env.prefs[stereoViewAngle_prefs_key])

    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the Stereo Property Manager.  
        """
        pass

    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the Stereo Property Manager.  
        """
        pass

    def _enableStereo(self, enabled):
        """
        Enable stereo view.
        """        
        if self.o:
            self.o.stereo_enabled = enabled
            self.o.gl_update()

    def _stereoModeComboBoxChanged(self, mode):
        """
        Change stereo mode.
        """

        env.prefs[stereoViewMode_prefs_key] = mode + 1

        # print "stereo mode = ", env.prefs[stereoViewMode_prefs_key]

        if self.o:
            self.o.gl_update()        

    def _stereoModeSeparationSliderChanged(self, value):
        """
        Change stereo view separation.
        """

        env.prefs[stereoViewSeparation_prefs_key] = value
        if self.o:
            self.o.gl_update()        

    def _stereoModeAngleSliderChanged(self, value):
        """
        Change stereo view angle.
        """

        env.prefs[stereoViewAngle_prefs_key] = value
        if self.o:
            self.o.gl_update()        

