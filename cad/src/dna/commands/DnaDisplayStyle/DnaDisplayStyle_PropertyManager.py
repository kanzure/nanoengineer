# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaDisplayStyle_PropertyManager.py

 The DnaDisplayStyle_PropertyManager class provides a Property Manager 
 for the B{Display Style} command on the flyout toolbar in the 
 Build > Dna mode. 

@author: Mark
@version: $Id$
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

To do:
- Add warning (in messagebox) if no DNA has its display style set to 
DNA Cylinder *and* the global display style is not DNA Cylinder.
- Add "Restore factory defaults" button to the bottom of each page.
- Add "Favorites" groupbox.
- Remove DNA Cylinder display style options from Preferences dialog.
- Add "Display Strand Labels" groupbox.
- Add "Display Base Orientation Indicators" groupbox.
"""
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui
from PM.PM_Dialog   import PM_Dialog
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_StackedWidget import PM_StackedWidget
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton

from utilities.prefs_constants import dnaStyleAxisShape_prefs_key
from utilities.prefs_constants import dnaStyleAxisColor_prefs_key
from utilities.prefs_constants import dnaStyleAxisScale_prefs_key
from utilities.prefs_constants import dnaStyleAxisTaper_prefs_key

from utilities.prefs_constants import dnaStyleStrandsShape_prefs_key
from utilities.prefs_constants import dnaStyleStrandsColor_prefs_key
from utilities.prefs_constants import dnaStyleStrandsScale_prefs_key
from utilities.prefs_constants import dnaStyleStrandsArrows_prefs_key

from utilities.prefs_constants import dnaStyleStrutsShape_prefs_key
from utilities.prefs_constants import dnaStyleStrutsColor_prefs_key
from utilities.prefs_constants import dnaStyleStrutsScale_prefs_key

from utilities.prefs_constants import dnaStyleBasesShape_prefs_key
from utilities.prefs_constants import dnaStyleBasesColor_prefs_key
from utilities.prefs_constants import dnaStyleBasesScale_prefs_key
from utilities.prefs_constants import dnaStyleBasesDisplayLetters_prefs_key

class DnaDisplayStyle_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The DnaDisplayStyle_PropertyManager class provides a Property Manager 
    for the B{Display Style} command on the flyout toolbar in the 
    Build > Dna mode. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "DNA Display Style"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/Dna_Display_Style.png"
    
    
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
        
        msg = "Modify the DNA display settings below."
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
        
        # Axis groupbox.
        change_connect( self.axisShapeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleAxisShape )
        
        change_connect( self.axisScaleDoubleSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.win.userPrefs.change_dnaStyleAxisScale )
        
        change_connect( self.axisColorComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleAxisColor )
        
        change_connect( self.axisEndingStyleComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleAxisTaper )
        
        # Strands groupbox.
        change_connect( self.strandsShapeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleStrandsShape )
        
        change_connect( self.strandsScaleDoubleSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.win.userPrefs.change_dnaStyleStrandsScale )
        
        change_connect( self.strandsColorComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleStrandsColor )
        
        change_connect( self.strandsArrowsComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleStrandsArrows )
        
        # Structs groupbox.
        change_connect( self.strutsShapeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleStrutsShape )
        
        change_connect( self.strutsScaleDoubleSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.win.userPrefs.change_dnaStyleStrutsScale )
        
        change_connect( self.strutsColorComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleStrutsColor )
        
        # Nucleotides groupbox.
        change_connect( self.nucleotidesShapeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleBasesShape )
        
        change_connect( self.nucleotidesScaleDoubleSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.win.userPrefs.change_dnaStyleBasesScale )
        
        change_connect( self.nucleotidesColorComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.win.userPrefs.change_dnaStyleBasesColor )
        
        connect_checkbox_with_boolean_pref(
            self.dnaStyleBasesDisplayLettersCheckBox,
            dnaStyleBasesDisplayLetters_prefs_key)
        
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
        self.updateDnaDisplayStyleWidgets()
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
        self._pmGroupBox1 = PM_GroupBox( self, title = "Display Options" )
        self._loadGroupBox1( self._pmGroupBox1 )
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        dnaComponentChoices = ['Axis', 
                                'Strands',
                                'Struts',
                                'Nucleotides']

        self.dnaComponentComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Component:", 
                         choices       =  dnaComponentChoices,
                         setAsDefault  =  True)
        
        self._loadAxisGroupBox()
        self._loadStrandsGroupBox()
        self._loadStrutsGroupBox()
        self._loadNucleotidesGroupBox()
        
        widgetList = [self.axisGroupBox, 
                      self.strandsGroupBox,
                      self.strutsGroupBox,
                      self.nucleotidesGroupBox]
        
        self.dnaComponentStackedWidget = \
            PM_StackedWidget( pmGroupBox,
                              self.dnaComponentComboBox,
                              widgetList )
    
    def _loadAxisGroupBox(self):
        """
        Load the Axis group box.
        """
        
        axisGroupBox = PM_GroupBox( None )
        self.axisGroupBox = axisGroupBox
        
        axisShapeChoices = ['None', 'Wide tube', 'Narrow tube']
        
        self.axisShapeComboBox = \
            PM_ComboBox( axisGroupBox ,     
                         label         =  "Shape:", 
                         choices       =  axisShapeChoices,
                         setAsDefault  =  True)
        
        self.axisScaleDoubleSpinBox  =  \
            PM_DoubleSpinBox( axisGroupBox,
                              label         =  "Scale:",
                              value         =  1.00,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  2.0,
                              decimals      =  2,
                              singleStep    =  0.1 )
        
        axisColorChoices = ['Same as chunk', 
                            'Base order', 
                            'Base order (discrete)',
                            'Base type',
                            'Strand order']
        
        self.axisColorComboBox = \
            PM_ComboBox( axisGroupBox ,     
                         label         =  "Color:", 
                         choices       =  axisColorChoices,
                         setAsDefault  =  True)
        
        endingTypeChoices = ['Flat', 
                             'Taper start', 
                             'Taper end',
                             'Taper both',
                             'Spherical']
        
        self.axisEndingStyleComboBox = \
            PM_ComboBox( axisGroupBox ,     
                         label         =  "Ending Style:", 
                         choices       =  endingTypeChoices,
                         setAsDefault  =  True)
        
    def _loadStrandsGroupBox(self):
        """
        Load the Strands group box.
        """
        
        strandsGroupBox = PM_GroupBox( None )
        self.strandsGroupBox = strandsGroupBox
        
        strandsShapeChoices = ['None', 'Cylinders', 'Tube']
        
        self.strandsShapeComboBox = \
            PM_ComboBox( strandsGroupBox ,     
                         label         =  "Shape:", 
                         choices       =  strandsShapeChoices,
                         setAsDefault  =  True)
        
        self.strandsScaleDoubleSpinBox  =  \
            PM_DoubleSpinBox( strandsGroupBox,
                              label         =  "Scale:",
                              value         =  1.00,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  5.0,
                              decimals      =  2,
                              singleStep    =  0.1 )
        
        strandsColorChoices = ['Same as chunk', 
                               'Base order', 
                               'Strand order']
        
        self.strandsColorComboBox = \
            PM_ComboBox( strandsGroupBox ,     
                         label         =  "Color:", 
                         choices       =  strandsColorChoices,
                         setAsDefault  =  True)
        
        strandsArrowsChoices = ['None', 
                                '5\'', 
                                '3\'', 
                                '5\' and 3\'']
        
        self.strandsArrowsComboBox = \
            PM_ComboBox( strandsGroupBox ,     
                         label         =  "Arrows:", 
                         choices       =  strandsArrowsChoices,
                         setAsDefault  =  True)
    
    def _loadStrutsGroupBox(self):
        """
        Load the Struts group box.
        """
        
        strutsGroupBox = PM_GroupBox( None )
        self.strutsGroupBox = strutsGroupBox
        
        strutsShapeChoices = ['None', 
                              'Base-axis-base cylinders', 
                              'Straight cylinders']
        
        self.strutsShapeComboBox = \
            PM_ComboBox( strutsGroupBox ,     
                         label         =  "Shape:", 
                         choices       =  strutsShapeChoices,
                         setAsDefault  =  True)
        
        self.strutsScaleDoubleSpinBox  =  \
            PM_DoubleSpinBox( strutsGroupBox,
                              label         =  "Scale:",
                              value         =  1.00,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  3.0,
                              decimals      =  2,
                              singleStep    =  0.1 )
        
        strutsColorChoices = ['Same as strand', 
                              'Base order', 
                              'Strand order',
                              'Base type']
        
        self.strutsColorComboBox = \
            PM_ComboBox( strutsGroupBox ,     
                         label         =  "Color:", 
                         choices       =  strutsColorChoices,
                         setAsDefault  =  True)
        
    def _loadNucleotidesGroupBox(self):
        """
        Load the Nucleotides group box.
        """
        nucleotidesGroupBox = PM_GroupBox( None )
        self.nucleotidesGroupBox = nucleotidesGroupBox
        
        nucleotidesShapeChoices = ['None', 
                                   'Sugar spheres', 
                                   'Base cartoons']
        
        self.nucleotidesShapeComboBox = \
            PM_ComboBox( nucleotidesGroupBox ,     
                         label         =  "Shape:", 
                         choices       =  nucleotidesShapeChoices,
                         setAsDefault  =  True)
        
        self.nucleotidesScaleDoubleSpinBox  =  \
            PM_DoubleSpinBox( nucleotidesGroupBox,
                              label         =  "Scale:",
                              value         =  1.00,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  3.0,
                              decimals      =  2,
                              singleStep    =  0.1 )
        
        nucleotidesColorChoices = ['Same as strand', 
                                   'Base order', 
                                   'Strand order',
                                   'Base type']
        
        self.nucleotidesColorComboBox = \
            PM_ComboBox( nucleotidesGroupBox ,     
                         label         =  "Color:", 
                         choices       =  nucleotidesColorChoices,
                         setAsDefault  =  True)
        
        self.dnaStyleBasesDisplayLettersCheckBox = \
            PM_CheckBox(nucleotidesGroupBox ,
                        text         = 'Display base letters',
                        widgetColumn = 1
                        )
    
    def updateDnaDisplayStyleWidgets( self ):
        """
        Updates all the DNA Display style widgets based on the current pref keys
        values.
        
        @note: This should be called each time the PM is displayed (see show()).
        """
        self.axisShapeComboBox.setCurrentIndex(env.prefs[dnaStyleAxisShape_prefs_key])
        self.axisScaleDoubleSpinBox.setValue(env.prefs[dnaStyleAxisScale_prefs_key])
        self.axisColorComboBox.setCurrentIndex(env.prefs[dnaStyleAxisColor_prefs_key])
        self.axisEndingStyleComboBox.setCurrentIndex(env.prefs[dnaStyleAxisTaper_prefs_key])
        
        self.strandsShapeComboBox.setCurrentIndex(env.prefs[dnaStyleStrandsShape_prefs_key])
        self.strandsScaleDoubleSpinBox.setValue(env.prefs[dnaStyleStrandsScale_prefs_key])
        self.strandsColorComboBox.setCurrentIndex(env.prefs[dnaStyleStrandsColor_prefs_key])
        self.strandsArrowsComboBox.setCurrentIndex(env.prefs[dnaStyleStrandsArrows_prefs_key])
        
        self.strutsShapeComboBox.setCurrentIndex(env.prefs[dnaStyleStrutsShape_prefs_key])
        self.strutsScaleDoubleSpinBox.setValue(env.prefs[dnaStyleStrutsScale_prefs_key])
        self.strutsColorComboBox.setCurrentIndex(env.prefs[dnaStyleStrutsColor_prefs_key])
        
        self.nucleotidesShapeComboBox.setCurrentIndex(env.prefs[dnaStyleBasesShape_prefs_key])
        self.nucleotidesScaleDoubleSpinBox.setValue(env.prefs[dnaStyleBasesScale_prefs_key])
        self.nucleotidesColorComboBox.setCurrentIndex(env.prefs[dnaStyleBasesColor_prefs_key])
        
    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the DNA Property Manager.  
        """
        pass
                
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the DNA Property Manager.  
        """
        pass
    
    