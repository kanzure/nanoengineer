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
- Implement full support for DNA "Favorites".
- Add warning (in messagebox) if no DNA has its display style set to 
DNA Cylinder *and* the global display style is not DNA Cylinder.
- Remove DNA Cylinder display style options from Preferences dialog.
- Add "Display Base Orientation Indicators" groupbox.
- Add "DNA Display Style Strand Label Custom Color" pref key/value.
- Add "Base Colors" pref keys/values.
"""
import os, time
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
from PM.PM_ToolButtonRow import PM_ToolButtonRow

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton

from utilities.prefs_constants import dnaStyleAxisShape_prefs_key
from utilities.prefs_constants import dnaStyleAxisColor_prefs_key
from utilities.prefs_constants import dnaStyleAxisScale_prefs_key
from utilities.prefs_constants import dnaStyleAxisEndingStyle_prefs_key

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

from utilities.prefs_constants import dnaStrandLabelsEnabled_prefs_key
from utilities.prefs_constants import dnaStrandLabelsColorMode_prefs_key

dnaDisplayStylePrefsList = \
                         [dnaStyleAxisShape_prefs_key, 
                          dnaStyleAxisScale_prefs_key,
                          dnaStyleAxisColor_prefs_key,
                          dnaStyleAxisEndingStyle_prefs_key,
                          
                          dnaStyleStrandsShape_prefs_key,
                          dnaStyleStrandsScale_prefs_key,
                          dnaStyleStrandsColor_prefs_key,
                          dnaStyleStrandsArrows_prefs_key,
                          
                          dnaStyleStrutsShape_prefs_key,
                          dnaStyleStrutsScale_prefs_key,
                          dnaStyleStrutsColor_prefs_key,
                          
                          dnaStyleBasesShape_prefs_key,
                          dnaStyleBasesScale_prefs_key,
                          dnaStyleBasesColor_prefs_key,
                          dnaStyleBasesDisplayLetters_prefs_key,
                          
                          dnaStrandLabelsEnabled_prefs_key,
                          dnaStrandLabelsColorMode_prefs_key]

# =
# DNA Display Style Favorite File I/O functions. Talk to Bruce about splitting
# these into a separate file and putting them elsewhere. Mark 2008-05-15.

def writeDnaDisplayStyleSettingsToFavoritesFile( basename ):
    """
    Writes a "favorite file" (with a .fav extension) to store all the 
    DNA display style settings (pref keys and their current values).
    
    @param basename: The filename (without the .fav extension) to write.
    @type  basename: string
    
    @note: The favorite file is written to the directory
           $HOME/Nanorex/DnaDisplayStyleFavorites.
    """
    
    if not basename:
        return 0, "No name given."
    
    # Get filename and write the favorite file.
    favfilepath = getFavoritePathFromBasename(basename)
    writeDnaFavoriteFile(favfilepath)
    
    # msg = "Problem writing file [%s]" % favfilepath
    
    return 1, basename

def getFavoritePathFromBasename( basename ):
    """
    Returns the full path to the favorite file given a basename.
    
    @param basename: The favorite filename (without the .fav extension).
    @type  basename: string
    
    @note: The (default) directory for all favorite files is
           $HOME/Nanorex/DnaDisplayStyleFavorites.
    """
    _ext = "fav"
    
    # Make favorite filename (i.e. ~/Nanorex/DnaFavorites/basename.fav)
    from platform.PlatformDependent import find_or_make_Nanorex_subdir
    _dir = find_or_make_Nanorex_subdir('DnaDisplayStyleFavorites')
    return os.path.join(_dir, "%s.%s" % (basename, _ext))

def writeDnaFavoriteFile( filename ):
    """
    Writes a favorite file to I{filename}.
    """
    
    f = open(filename, 'w')
        
    # Write header
    f.write ('!\n! DNA display style favorite file')
    f.write ('\n!Created by NanoEngineer-1 on ')
    timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    f.write(timestr)
    
    for pref_key in dnaDisplayStylePrefsList:
        val = env.prefs[pref_key]
        if isinstance(val, int):
            f.write("%s = %d\n" % (pref_key, val))
        elif isinstance(val, float):
            f.write("%s = %-6.2f\n" % (pref_key, val))
        elif isinstance(val, bool):
            f.write("%s = %d\n" % (pref_key, val))
        else:
            print "Not sure what pref_key '%s' is." % pref_key
        
    f.close()

# =

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
        
        # Favorite buttons signal-slot connections.
        change_connect( self.applyFavoriteButton,
                        SIGNAL("clicked()"), 
                       self.applyFavorite)
        
        change_connect( self.addFavoriteButton,
                        SIGNAL("clicked()"), 
                       self.addFavorite)
        
        change_connect( self.deleteFavoriteButton,
                        SIGNAL("clicked()"), 
                       self.deleteFavorite)
        
        change_connect( self.saveFavoriteButton,
                        SIGNAL("clicked()"), 
                       self.saveFavorite)
        
        change_connect( self.loadFavoriteButton,
                        SIGNAL("clicked()"), 
                       self.loadFavorite)
        
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
                      self.win.userPrefs.change_dnaStyleAxisEndingStyle )
        
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
        
        # Dna Strand labels
        
        change_connect( self.standLabelColorComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.change_dnaStrandLabelsDisplay )
        
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
        self._pmGroupBox1 = PM_GroupBox( self, 
                                         title = "Favorites")
        self._loadGroupBox1( self._pmGroupBox1 )
        
        self._pmGroupBox2 = PM_GroupBox( self, 
                                         title = "Current display settings")
        self._loadGroupBox2( self._pmGroupBox2 )
        
        
        #@ self._pmGroupBox1.hide()
        
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        favoriteChoices = ['Factory default settings']

        self.favoritesComboBox  = \
            PM_ComboBox( pmGroupBox,
                         choices       =  favoriteChoices,
                         spanWidth  =  True)
        
        # PM_ToolButtonRow ===============
        
        # Button list to create a toolbutton row.
        # Format: 
        # - QToolButton, buttonId, buttonText, 
        # - iconPath,
        # - tooltip, shortcut, column
        
        BUTTON_LIST = [ 
            ( "QToolButton", 1,  "APPLY_FAVORITE", 
              "dna/commands/DnaDisplayStyle/ui/icons/ApplyFavorite.png",
              "Apply Favorite", "", 0),
            ( "QToolButton", 2,  "ADD_FAVORITE", 
              "dna/commands/DnaDisplayStyle/ui/icons/AddFavorite.png",
              "Add Favorite", "", 1),
            ( "QToolButton", 3,  "DELETE_FAVORITE",  
              "dna/commands/DnaDisplayStyle/ui/icons/DeleteFavorite.png",
              "Delete Favorite", "", 2),
            ( "QToolButton", 4,  "SAVE_FAVORITE",  
              "dna/commands/DnaDisplayStyle/ui/icons/SaveFavorite.png",
              "Save Favorite", "", 3),
            ( "QToolButton", 5,  "LOAD_FAVORITE",  
              "dna/commands/DnaDisplayStyle/ui/icons/LoadFavorite.png",
              "Load Favorite", \
              "", 4)  
            ]
            
        self.favsButtonGroup = \
            PM_ToolButtonRow( pmGroupBox, 
                              title        = "",
                              buttonList   = BUTTON_LIST,
                              spanWidth    = True,
                              isAutoRaise  = False,
                              isCheckable  = False,
                              setAsDefault = True,
                              )
        
        self.favsButtonGroup.buttonGroup.setExclusive(False)
        
        self.applyFavoriteButton  = self.favsButtonGroup.getButtonById(1)
        self.addFavoriteButton    = self.favsButtonGroup.getButtonById(2)
        self.deleteFavoriteButton = self.favsButtonGroup.getButtonById(3)
        self.saveFavoriteButton   = self.favsButtonGroup.getButtonById(4)
        self.loadFavoriteButton   = self.favsButtonGroup.getButtonById(5)
        
    def _loadGroupBox2(self, pmGroupBox):
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
        
        standLabelColorChoices = ['Hide',
                                  'Show (in strand color)', 
                                  'Black',
                                  'White',
                                  'Custom color...']

        self.standLabelColorComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Strand labels:", 
                         choices       =  standLabelColorChoices,
                         setAsDefault  =  True)
    
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
                         label         =  "Ending style:", 
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
        self.axisEndingStyleComboBox.setCurrentIndex(env.prefs[dnaStyleAxisEndingStyle_prefs_key])
        
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
        
        # DNA Strand label combobox.
        if env.prefs[dnaStrandLabelsEnabled_prefs_key]:
            _dnaStrandColorItem = env.prefs[dnaStrandLabelsColorMode_prefs_key] + 1
        else:
            _dnaStrandColorItem = 0
        self.standLabelColorComboBox.setCurrentIndex(_dnaStrandColorItem)
        
    def change_dnaStrandLabelsDisplay(self, mode):
        """
        Changes DNA Strand labels display (and color) mode.

        @param mode: The display mode:
                    - 0 = hide all labels
                    - 1 = show (same color as chunk)
                    - 2 = show (black)
                    - 3 = show (white)
		    - 4 = show (custom color...)

        @type mode: int
        """
        if mode == 4:
            self.win.userPrefs.change_dnaStrandLabelsColor()
            
        if mode == 0:
            #@ Fix this at the same time I (we) remove the DNA display style
            #  prefs options from the Preferences dialog. --Mark 2008-05-13
            self.win.userPrefs.toggle_dnaDisplayStrandLabelsGroupBox(False)
        else:
            self.win.userPrefs.toggle_dnaDisplayStrandLabelsGroupBox(True)
            self.win.userPrefs.change_dnaStrandLabelsColorMode(mode - 1)
    
    def applyFavorite(self):
        """
        Apply the DNA display style settings stored in the current favorite 
        (selected in the combobox) to the current DNA display style settings.
        """
        current_favorite = self.favoritesComboBox.currentText()
        if current_favorite == 'Factory default settings':
            env.prefs.restore_defaults(dnaDisplayStylePrefsList)
        else:
            msg = "Cannot apply favorite named [%s]. "\
                "This feature is not implemented yet." % current_favorite
            print msg
        self.updateDnaDisplayStyleWidgets()
        return
    
    def addFavorite(self):
        """
        Adds a new favorite to the user's list of favorites.
        """
        # Rules and other info:
        # - The new favorite is defined by the current DNA display style 
        #    settings.
        # - If there is already a favorite with the current DNA display style 
        #    settings, the user is notified by a message box and is given the 
        #    name of the favorite.
        # - The user is prompted to type in a (unique) name for the new 
        #    favorite.
        # - The DNA display style settings are written to a file in a special 
        #    directory on the disk (i.e. $HOME/Nanorex/DNA/Favorites/$FAV_NAME.fav).
        # - The name of the new favorite is added to the list of favorites in
        #    the combobox, which becomes the current option. 
        
        # First, check if there is already a favorite with the current settings.
        # ok = self.checkForDuplicateFavorite()
        # if not ok:
        #     return
        
        # Prompt user for a unique favorite name to add. 
        from widgets.simple_dialogs import grab_text_line_using_dialog
        
        ok, name = \
          grab_text_line_using_dialog(
              title = "Add new favorite",
              label = "favorite name:",
              iconPath = "dna/commands/DnaDisplayStyle/ui/icons/AddFavorite.png",
              default = "" )
        if ok:
            ok, text = writeDnaDisplayStyleSettingsToFavoritesFile(name)
        if ok:
            self.favoritesComboBox.addItem(name)
            _lastItem = self.favoritesComboBox.count()
            self.favoritesComboBox.setCurrentIndex(_lastItem - 1)
            msg = "New favorite [%s] added." % (text)
        else:
            msg = "Can't add favorite [%s]: %s" % (name, text) # text is reason why not
        
        print msg #@ Turn into a history msg.
        
        return
        
    def deleteFavorite(self):
        """
        Deletes the current favorite from the user's personal list of favorites
        (and from disk).
        
        @note: Cannot delete "Factory default settings".
        """
        currentIndex = self.favoritesComboBox.currentIndex()
        currentText = self.favoritesComboBox.currentText()
        if currentIndex == 0:
            msg = "Cannot delete '%s'." % currentText
        else:
            self.favoritesComboBox.removeItem(currentIndex)
            msg = "Deleted favorite named [%s].\n" \
                "Don't forget to delete the favorite file [%s.fav]." \
                % (currentText, currentText)
        print msg
        return
        
    def saveFavorite(self):
        """
        Writes the current favorite (selected in the combobox) to a file that 
        can be given to another NE1 user (i.e. as an email attachment).
        """
        print "saveFavorite(): Not implemented yet."
        return
        
    def loadFavorite(self):
        """
        Prompts the user to choose a "favorite file" (i.e. *.fav) from disk to
        be added to the personal favorites list.
        """
        print "loadFavorite(): Not implemented yet."
        return
        
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
    
    