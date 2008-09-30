# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
TestGraphics_PropertyManager.py

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin

from PyQt4.Qt import SIGNAL
from PM.PM_Dialog   import PM_Dialog
from PM.PM_Slider   import PM_Slider
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_CheckBox import PM_CheckBox

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON

##from utilities.prefs_constants import stereoViewMode_prefs_key
##from utilities.prefs_constants import stereoViewAngle_prefs_key
##from utilities.prefs_constants import stereoViewSeparation_prefs_key

from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED

# ==

class TestGraphics_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The TestGraphics_PropertyManager class provides a Property Manager 
    for the Test Graphics command. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Test Graphics"
    pmName        =  title
    iconPath      =  None ###k "ui/actions/View/Stereo_View.png" ### FIX - use some generic or default icon


    def __init__( self, command ):
        """
        Constructor for the property manager.
        """
        self.command = command

        # review: some of the following are probably not needed:
        self.w = self.command.w
        self.win = self.command.w
        self.pw = self.command.pw        
        self.o = self.win.glpane                 

        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title) # todo: clean up so superclass knows attrnames?

        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Test the performance effect of graphics settings below."

        self.updateMessage(msg)
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
            

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

##        change_connect( self.stereoModeComboBox,
##                        SIGNAL("currentIndexChanged(int)"),
##                        self._stereoModeComboBoxChanged )
##
##        change_connect(self.stereoSeparationSlider,
##                       SIGNAL("valueChanged(int)"),
##                       self._stereoModeSeparationSliderChanged )
##
##        change_connect(self.stereoAngleSlider,
##                       SIGNAL("valueChanged(int)"),
##                       self._stereoModeAngleSliderChanged )

    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show.
        """
        PM_Dialog.show(self)
        # self.updateDnaDisplayStyleWidgets()
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)

    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)
            
        PM_Dialog.close(self)

    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self, 
                                         title = "Settings") ### fix title
        self._loadGroupBox1( self._pmGroupBox1 )

        #@ self._pmGroupBox1.hide()

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        from widgets.prefs_widgets  import ObjAttr_StateRef ### toplevel
        
        self._cb1 = \
            PM_CheckBox(pmGroupBox,
                        text         = 'bypass paintGL',
                        widgetColumn = 1,
                        ## setter = self._set_bypass_paintgl -- TODO - put this in if there's nothing wrong with it as an API
                        )
        self._cb1.connectWithState( ObjAttr_StateRef( self.command, 'bypass_paintgl' ))

        self._cb2 = \
            PM_CheckBox(pmGroupBox,
                        text         = 'redraw continuously',
                        widgetColumn = 1
                        )        
        self._cb2.connectWithState( ObjAttr_StateRef( self.command, 'redraw_continuously' ))

        self._cb3 = \
            PM_CheckBox(pmGroupBox,
                        text         = 'spin model',
                        widgetColumn = 1
                        )        
        self._cb3.connectWithState( ObjAttr_StateRef( self.command, 'spin_model' ))

##        stereoModeChoices = ['Relaxed view', 
##                             'Cross-eyed view',
##                             'Red/blue anaglyphs',
##                             'Red/cyan anaglyphs',
##                             'Red/green anaglyphs']
##
##        self.stereoModeComboBox  = \
##            PM_ComboBox( pmGroupBox,
##                         label         =  "Stereo Mode:", 
##                         choices       =  stereoModeChoices,
##                         setAsDefault  =  True)
##
##        self.stereoModeComboBox.setCurrentIndex(env.prefs[stereoViewMode_prefs_key] - 1)
##            
##        self.stereoSeparationSlider =  \
##            PM_Slider( pmGroupBox,
##                       currentValue = 50,
##                       minimum      = 0,
##                       maximum      = 300,
##                       label        = 'Separation'
##                       )        
##
##        self.stereoSeparationSlider.setValue(env.prefs[stereoViewSeparation_prefs_key])
##
##        self.stereoAngleSlider =  \
##            PM_Slider( pmGroupBox,
##                       currentValue = 50,
##                       minimum      = 0,
##                       maximum      = 100,
##                       label        = 'Angle'
##                       )
##
##        self.stereoAngleSlider.setValue(env.prefs[stereoViewAngle_prefs_key])

##        self._updateWidgets()
                
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

##    def _stereoModeComboBoxChanged(self, mode):
##        """
##        Change stereo mode.
##        
##        @param mode: stereo mode (0=relaxed, 1=cross-eyed, 2=red/blue,
##        3=red/cyan, 4=red/green)
##        @type value: int
##        """
##        env.prefs[stereoViewMode_prefs_key] = mode + 1
##
##        self._updateSeparationSlider()
##        
##    def _stereoModeSeparationSliderChanged(self, value):
##        """
##        Change xxx separation.
##        
##        @param value: separation (0..300)
##        @type value: int
##        """
##        env.prefs[stereoViewSeparation_prefs_key] = value
##
##    def _stereoModeAngleSliderChanged(self, value):
##        """
##        Change xxx angle.
##        
##        @param value: stereo angle (0..100)
##        @type value: int
##        """
##        env.prefs[stereoViewAngle_prefs_key] = value
##
##    def _updateSeparationSlider(self):
##        """ 
##        Update the separation slider widget.
##        """
##        if self.stereoModeComboBox.currentIndex() >= 2: 
##            # for anaglyphs disable the separation slider 
##            self.stereoSeparationSlider.setEnabled(False)
##        else:
##            # otherwise, enable the separation slider
##            self.stereoSeparationSlider.setEnabled(True)
##
##    def _updateWidgets(self):
##        """
##        Update stereo PM widgets.
##        """
##        if self._cb1.isChecked():
##            self.stereoModeComboBox.setEnabled(True)
##            self.stereoSeparationSlider.setEnabled(True)
##            self.stereoAngleSlider.setEnabled(True)
##            self._updateSeparationSlider()
##        else:
##            self.stereoModeComboBox.setEnabled(False)
##            self.stereoSeparationSlider.setEnabled(False)
##            self.stereoAngleSlider.setEnabled(False)
##            
