# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ColorScheme_PropertyManager.py

 The ColorScheme_PropertyManager class provides a Property Manager 
 for choosing various colors (example: background)

@author: Urmi
@version: $Id: ColorScheme_PropertyManager.py 12867 2008-05-20 20:29:44Z urmim $
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.


"""
import os, time, fnmatch, string
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.Log import greenmsg

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui
from PyQt4.Qt import QFileDialog, QString, QMessageBox
from PM.PM_Dialog   import PM_Dialog
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_StackedWidget import PM_StackedWidget
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ToolButtonRow import PM_ToolButtonRow
from PM.PM_ColorChooser import PM_ColorChooser
from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton

from utilities.constants import diDNACYLINDER


from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf
from PyQt4.Qt import QColorDialog
from utilities.icon_utilities import geticon
from utilities.debug import print_compact_traceback


bg_BLUE_SKY = 0
bg_EVENING_SKY = 1
bg_BLACK = 2
bg_WHITE = 3
bg_GRAY = 4
bg_CUSTOM = 5

#hover highlighting 
# HHS = hover highlighting styles
HHS_SOLID = 0
HHS_SCREENDOOR1 = 1
HHS_CROSSHATCH1 = 2
HHS_BW_PATTERN = 3
HHS_POLYGON_EDGES = 4
HHS_HALO = 5
HHS_DISABLED = 6

HHS_INDEXES = [HHS_SOLID, HHS_SCREENDOOR1, HHS_CROSSHATCH1, HHS_BW_PATTERN,
              HHS_POLYGON_EDGES, HHS_HALO, HHS_DISABLED]

HHS_OPTIONS = ["Highlight in solid color",
               "Highlight in screendoor pattern",
               "Highlight in crosshatch pattern",
               "Highlight with black-and-white pattern",
               "Highlight in colored polygon edges",
               "Highlight in colored halo",
               "Disable hover highlighting"]

# SS = selection styles

SS_SOLID = 0
SS_SCREENDOOR1 = 1
SS_CROSSHATCH1 = 2
SS_BW_PATTERN = 3
SS_POLYGON_EDGES = 4
SS_HALO = 5

SS_INDEXES = [SS_SOLID, SS_SCREENDOOR1, SS_CROSSHATCH1, 
              SS_BW_PATTERN, SS_POLYGON_EDGES, SS_HALO]

SS_OPTIONS = ["Solid color",
              "Screendoor pattern",
              "Crosshatch pattern",
              "Black-and-white pattern",
              "Colored polygon edges",
              "Colored halo"]


from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import backgroundColor_prefs_key
from utilities.prefs_constants import backgroundGradient_prefs_key
from utilities.constants import black, white, gray
colorSchemePrefsList = \
                     [backgroundGradient_prefs_key,
                      backgroundColor_prefs_key,
                      hoverHighlightingColorStyle_prefs_key,
                      hoverHighlightingColor_prefs_key,
                      selectionColorStyle_prefs_key,
                      selectionColor_prefs_key
                      ]

# =
# Color Scheme Favorite File I/O functions. 

def writeColorSchemeToFavoritesFile( basename ):
    """
    Writes a "favorite file" (with a .txt extension) to store all the 
    color scheme settings (pref keys and their current values).
            
    @param basename: The filename (without the .txt extension) to write.
    @type  basename: string
            
    @note: The favorite file is written to the directory
            $HOME/Nanorex/Favorites/ColorScheme.
    """
            
    if not basename:
        return 0, "No name given."
            
    # Get filename and write the favorite file.
    favfilepath = getFavoritePathFromBasename(basename)
    writeColorSchemeFavoriteFile(favfilepath)            
            
    # msg = "Problem writing file [%s]" % favfilepath

    return 1, basename


def getFavoritePathFromBasename( basename ):
    """
    Returns the full path to the favorite file given a basename.
    
    @param basename: The favorite filename (without the .txt extension).
    @type  basename: string
    
    @note: The (default) directory for all favorite files is
           $HOME/Nanorex/Favorites/ColorScheme.
    """
    _ext = "txt"
    
    # Make favorite filename (i.e. ~/Nanorex/Favorites/ColorScheme/basename.txt)
    from platform.PlatformDependent import find_or_make_Nanorex_subdir
    _dir = find_or_make_Nanorex_subdir('Favorites/ColorScheme')
    return os.path.join(_dir, "%s.%s" % (basename, _ext))

def writeColorSchemeFavoriteFile( filename ):
    """
    Writes a favorite file to I{filename}.
    """
    
    f = open(filename, 'w')
        
    # Write header
    f.write ('!\n! Color Scheme favorite file')
    f.write ('\n!Created by NanoEngineer-1 on ')
    timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    f.write(timestr)
    
    #write preference list in file without the NE version 
    for pref_key in colorSchemePrefsList:
        val = env.prefs[pref_key]
        
        pref_keyArray = pref_key.split("/")
        pref_key = pref_keyArray[1]
        
        if isinstance(val, int):
            f.write("%s = %d\n" % (pref_key, val))
        
        #tuples written as string for now
        elif isinstance(val, tuple):
            f.write("%s = %s\n" % (pref_key, val))
        elif isinstance(val, bool):
            f.write("%s = %d\n" % (pref_key, val))
        else:
            print "Not sure what pref_key '%s' is." % pref_key
        
    f.close()

    
def loadFavoriteFile( filename ):
    """
    Loads a favorite file from anywhere in the disk.
    
    @param filename: The full path for the favorite file.
    @type  filename: string
    
    """
    
    if os.path.exists(filename):
        favoriteFile = open(filename, 'r')
    else:
        env.history.message("Favorite file to be loaded does not exist.")
        return 0
     
    # do syntax checking on the file to figure out whether this is a valid
    # favorite file
    
    
    line = favoriteFile.readline()
    line = favoriteFile.readline()
    
    if line != "! Color Scheme favorite file\n":
        env.history.message(" Not a proper favorite file")
        favoriteFile.close()
        return 0
    
    while 1:
        line = favoriteFile.readline()
        
        # marks the end of file
        if line == "":
            break
        
        
        # process each line to obtain pref_keys and their corresponding values
        if line[0] != '!':
        
            keyValuePair = line.split('=')
            pref_keyString = keyValuePair[0].strip()
            pref_value=keyValuePair[1].strip()
        
            # check if pref_value is an integer or tuple (for colors)
        
            try: 
                int(pref_value)
                pref_valueToStore = int(pref_value)
                
            except ValueError:
                pref_valueToStore = tuple(map(float, pref_value[1:-1].split(',')))
                
            # match pref_keyString with its corresponding variable name in the 
            # preference key list
        
            pref_key = findPrefKey( pref_keyString )
        
            #add preference key and its corresponding value to the dictionary
        
            if pref_key:
                env.prefs[pref_key] = pref_valueToStore
             
     
               
    favoriteFile.close()
    
    #check if a copy of this file exists in the favorites directory. If not make
    # a copy of it in there
    
    
    favName = os.path.basename(str(filename))
    name = favName[0:len(favName)-4]
    favfilepath = getFavoritePathFromBasename(name)
    
    if not os.path.exists(favfilepath):
        saveFavoriteFile(favfilepath, filename)
    
    return 1
      
    
def findPrefKey( pref_keyString ):
    """
    Matches prefence key in the colorSchemePrefsList with pref_keyString
    from the favorte file that we intend to load. 

    
    @param pref_keyString: preference from the favorite file to be loaded.
    @type  pref_keyString: string
    
    @note: very inefficient since worst case time taken is proportional to the 
    size of the list. If original preference strings are in a dictionary, access
    can be done in constant time
    
    """
    
    for keys in colorSchemePrefsList:
        #split keys in dnaDisplayStylePrefList into version number and pref_key
        
        pref_array= keys.split("/")
        if pref_array[1] == pref_keyString:
            return keys
        
    return None
    
def saveFavoriteFile( savePath, fromPath ):
    
    """
    Save favorite file to anywhere in the disk

    
    @param savePath: full path for the location where the favorite file is to be saved.
    @type  savePath: string
    
    @param savePath: ~/Nanorex/Favorites/ColorScheme/$FAV_NAME.txt
    @type  fromPath: string
    
    """
    if savePath:
        saveFile = open(savePath, 'w')
    if fromPath:
        fromFile = open(fromPath, 'r')
        
    lines=fromFile.readlines()   
    saveFile.writelines(lines)
        
    saveFile.close()
    fromFile.close()
    
    return    

# =

class ColorScheme_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The ColorScheme_PropertyManager class provides a Property Manager 
    for choosing background and other colors for the Choose Color toolbar command
    as well as the View/Color Scheme command

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Color Scheme"
    pmName        =  title
    iconPath      =  "ui/actions/View/ColorScheme.png"
    
    
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
        
        msg = "Edit the color scheme for NE1, including the background color, "\
            "hover highlighting and selection colors, etc."
        self.updateMessage(msg)
        
        self._setupPM_Color()
    
    def _setupPM_Color(self):
        """
        Setup the "Color" PM
	"""
        self._loadBackgroundColorItems()
        self._loadHoverHighlightingStyleItems()
        self.hoverHighlightingStyleComboBox.setCurrentIndex(env.prefs[hoverHighlightingColorStyle_prefs_key])
        self.hoverHighlightingColorChooser.setColor(env.prefs[hoverHighlightingColor_prefs_key])
        self._loadSelectionStyleItems()
        self.selectionStyleComboBox.setCurrentIndex(env.prefs[selectionColorStyle_prefs_key])
        
        # will be uncommented after Russ finish setting this pref key: Urmi 20080530
        #self.selectionColorChooser.setColor(env.prefs[selectionColorStyle_prefs_key])
        
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
        
        # background color setting combo box.
        change_connect( self.backgroundColorComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.changeBackgroundColor )
        
        #hover highlighting style combo box
        change_connect(self.hoverHighlightingStyleComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.changeHoverHighlightingStyle)
        change_connect(self.hoverHighlightingColorChooser, 
                       SIGNAL("editingFinished()"),
                       self.changeHoverHighlightingColor)
    
        #selection style combo box
        change_connect(self.selectionStyleComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.changeSelectionStyle)
        change_connect(self.selectionColorChooser, 
                       SIGNAL("editingFinished()"),
                       self.changeSelectionColor)  
        
    def changeHoverHighlightingColor(self):
        """
        Slot method for Hover Highlighting color chooser.
        Change the (3D) hover highlighting color.
        """
        color = self.hoverHighlightingColorChooser.getColor()
        env.prefs[hoverHighlightingColor_prefs_key] = color
        return
        
    def changeHoverHighlightingStyle(self, idx):
        
        """
        Slot method for Hover Highlighting combobox.
        Change the (3D) hover highlighting style.
        """
        env.prefs[hoverHighlightingColorStyle_prefs_key] = HHS_INDEXES[idx]
        
    def changeSelectionStyle(self, idx):
        
        """
        Slot method for Selection color style combobox.
        Change the (3D) Selection color style.
        """
        env.prefs[selectionColorStyle_prefs_key] = SS_INDEXES[idx]
        
    def changeSelectionColor(self):
        """
        Slot method for Selection color chooser.
        Change the (3D) Selection color.
        """
        color = self.selectionColorChooser.getColor()
        env.prefs[selectionColor_prefs_key] = color
        return    
        
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
        
        if env.prefs[backgroundGradient_prefs_key]:
                    self.win.glpane.setBackgroundGradient(env.prefs[backgroundGradient_prefs_key])
        else:
            self.win.glpane.setBackgroundColor(env.prefs[backgroundColor_prefs_key])
        self.win.glpane.gl_update() 
        
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
                                         title = "Color settings")
        self._loadGroupBox2( self._pmGroupBox2 )
        
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        # Other info
        # Not only loads the factory default settings but also all the favorite
        # files stored in the ~/Nanorex/Favorites/DnaDisplayStyle directory
        
        favoriteChoices = ['Factory default settings']

        #look for all the favorite files in the favorite folder and add them to 
        # the list
        from platform.PlatformDependent import find_or_make_Nanorex_subdir
        _dir = find_or_make_Nanorex_subdir('Favorites/ColorScheme')
        
        
        for file in os.listdir(_dir):
            fullname = os.path.join( _dir, file)
            if os.path.isfile(fullname):
                if fnmatch.fnmatch( file, "*.txt"):
                    
                    # leave the extension out
                    favoriteChoices.append(file[0:len(file)-4])
        
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
              "ui/actions/Properties Manager/ApplyColorSchemeFavorite.png",
              "Apply Favorite", "", 0),
            ( "QToolButton", 2,  "ADD_FAVORITE", 
              "ui/actions/Properties Manager/AddFavorite.png",
              "Add Favorite", "", 1),
            ( "QToolButton", 3,  "DELETE_FAVORITE",  
              "ui/actions/Properties Manager/DeleteFavorite.png",
              "Delete Favorite", "", 2),
            ( "QToolButton", 4,  "SAVE_FAVORITE",  
              "ui/actions/Properties Manager/SaveFavorite.png",
              "Save Favorite", "", 3),
            ( "QToolButton", 5,  "LOAD_FAVORITE",  
              "ui/actions/Properties Manager/LoadFavorite.png",
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
        #background color combo box
        self.pmGroupBox1 = PM_GroupBox(pmGroupBox, title = "Background:")
        self.backgroundColorComboBox  = \
            PM_ComboBox( self.pmGroupBox1,
                         label     =  "",
                         spanWidth = True)
        
        #hover highlighting group box
        
        self.pmGroupBox2 = PM_GroupBox(pmGroupBox, title = "Hover highlighting:")
        self.hoverHighlightingStyleComboBox = \
            PM_ComboBox( self.pmGroupBox2,
                         label     =  "Style:",
                         )
        
        self.hoverHighlightingColorChooser = \
            PM_ColorChooser(self.pmGroupBox2,
                            label = "Color"
                            )
        
        #selection style and color group box
        
        self.pmGroupBox3 = PM_GroupBox(pmGroupBox, title = "Selection:")
        self.selectionStyleComboBox = \
            PM_ComboBox( self.pmGroupBox3,
                         label     =  "Style:",
                         )
        
        self.selectionColorChooser = \
            PM_ColorChooser(self.pmGroupBox3,
                            label = "Color"
                            )
    
        
    def _loadSelectionStyleItems(self):
        """
	Load the selection color style combobox with items.
	"""        
        for selectionStyle in SS_OPTIONS:
            self.selectionStyleComboBox.addItem(selectionStyle)
        return
    
    def _loadHoverHighlightingStyleItems(self):
        """
	Load the hover highlighting style combobox with items.
	"""
        for hoverHighlightingStyle in HHS_OPTIONS:
            self.hoverHighlightingStyleComboBox.addItem(hoverHighlightingStyle)
        return
        
    def _loadBackgroundColorItems(self):
        """
	Load the background color combobox with all the color options and sets 
        the current background color
	"""
        backgroundIndexes = [bg_BLUE_SKY, bg_EVENING_SKY, 
                             bg_BLACK, bg_WHITE, bg_GRAY, bg_CUSTOM]
        
        backgroundNames   = ["Blue Sky (default)", "Evening Sky",
                             "Black", "White", "Gray", "Custom..."]
        
        backgroundIcons   = ["Background_BlueSky", "Background_EveningSky", 
                             "Background_Black",   "Background_White", 
                             "Background_Gray",    "Background_Custom"]
        
        backgroundIconsDict = dict(zip(backgroundNames, backgroundIcons))
        backgroundNamesDict = dict(zip(backgroundIndexes, backgroundNames))
        
        for backgroundName in backgroundNames:
            
            basename = backgroundIconsDict[backgroundName] + ".png"
            iconPath = os.path.join("ui/dialogs/Preferences/", 
                                    basename)
            self.backgroundColorComboBox.addItem(geticon(iconPath), 
                                                 backgroundName)
        
        self._updateBackgroundColorComboBoxIndex()
        return    
        
    def _updateBackgroundColorComboBoxIndex(self):
        """
        Set current index in the background color combobox.
	"""
        if self.win.glpane.backgroundGradient:
            self.backgroundColorComboBox.setCurrentIndex(self.win.glpane.backgroundGradient - 1)
        else:
            if (env.prefs[ backgroundColor_prefs_key ] == black):
                self.backgroundColorComboBox.setCurrentIndex(bg_BLACK)
            elif (env.prefs[ backgroundColor_prefs_key ] == white):
                self.backgroundColorComboBox.setCurrentIndex(bg_WHITE)  
            elif (env.prefs[ backgroundColor_prefs_key ] == gray):
                self.backgroundColorComboBox.setCurrentIndex(bg_GRAY)
            else:
                self.backgroundColorComboBox.setCurrentIndex(bg_CUSTOM) 
        return
    
    def changeBackgroundColor(self, idx):
        """
	Slot method for the background color combobox.
	"""
        #print "changeBackgroundColor(): Slot method called. Idx =", idx

        if idx == bg_BLUE_SKY:  
            self.win.glpane.setBackgroundGradient(idx + 1)
        elif idx == bg_EVENING_SKY:
            self.win.glpane.setBackgroundGradient(idx + 1)
        elif idx == bg_BLACK:
            self.win.glpane.setBackgroundColor(black)
        elif idx == bg_WHITE:
            self.win.glpane.setBackgroundColor(white)
        elif idx == bg_GRAY:
            self.win.glpane.setBackgroundColor(gray)
        elif idx == bg_CUSTOM: 
            #change background color to Custom Color
            self.chooseCustomBackgroundColor()
        else:
            msg = "Unknown color idx=", idx
            print_compact_traceback(msg)
            
        
        self.win.glpane.gl_update() # Needed!
        return
    
    def chooseCustomBackgroundColor(self):
        """
        Choose a custom background color.
        """
        c = QColorDialog.getColor(RGBf_to_QColor(self.win.glpane.getBackgroundColor()), self)
        if c.isValid():
            self.win.glpane.setBackgroundColor(QColor_to_RGBf(c))
        else:
            self._updateBackgroundColorComboBoxIndex()

    def applyFavorite(self):
        """
        Apply the color scheme settings stored in the current favorite 
        (selected in the combobox) to the current DNA display style settings.
        """
        # Rules and other info:
        # The user has to press the button related to this method when he loads
        # a previously saved favorite file
        
        current_favorite = self.favoritesComboBox.currentText()
        if current_favorite == 'Factory default settings':
            env.prefs.restore_defaults(colorSchemePrefsList)
            # set it back to blue sky
            self.win.glpane.setBackgroundGradient(1)
            self.win.glpane.gl_update()
        else:
            favfilepath = getFavoritePathFromBasename(current_favorite)
            loadFavoriteFile(favfilepath)
            if env.prefs[backgroundGradient_prefs_key]:
                self.win.glpane.setBackgroundGradient(env.prefs[backgroundGradient_prefs_key])
            else:
                self.win.glpane.setBackgroundColor(env.prefs[backgroundColor_prefs_key])
            self.win.glpane.gl_update()
        return
    
    def addFavorite(self):
        """
        Adds a new favorite to the user's list of favorites.
        """
        # Rules and other info:
        # - The new favorite is defined by the current color scheme
        #    settings.
    
        # - The user is prompted to type in a name for the new 
        #    favorite.
        # - The color scheme settings are written to a file in a special 
        #    directory on the disk 
        # (i.e. $HOME/Nanorex/Favorites/ColorScheme/$FAV_NAME.txt).
        # - The name of the new favorite is added to the list of favorites in
        #    the combobox, which becomes the current option. 
        
        # Existence of a favorite with the same name is checked in the above 
        # mentioned location and if a duplicate exists, then the user can either
        # overwrite and provide a new name.
        
        
        
        # Prompt user for a favorite name to add. 
        from widgets.simple_dialogs import grab_text_line_using_dialog
        
        ok1, name = \
          grab_text_line_using_dialog(
              title = "Add new favorite",
              label = "favorite name:",
              iconPath = "ui/actions/Properties Manager/AddFavorite.png",
              default = "" )
        if ok1:
            # check for duplicate files in the 
            # $HOME/Nanorex/Favorites/ColorScheme/ directory
            
            fname = getFavoritePathFromBasename( name )
            if os.path.exists(fname):
                
                #favorite file already exists!
                
                _ext= ".txt"
                ret = QMessageBox.warning( self, "Warning!",
                "The favorite file \"" + name + _ext + "\"already exists.\n"
                "Do you want to overwrite the existing file?",
                "&Overwrite", "&Cancel", "",
                0,    # Enter == button 0
                1)   # Escape == button 1  
                
                if ret == 0:
                    #overwrite favorite file
                    ok2, text = writeColorSchemeToFavoritesFile(name)
                    indexOfDuplicateItem = self.favoritesComboBox.findText(name)
                    self.favoritesComboBox.removeItem(indexOfDuplicateItem)
                    print "Add Favorite: removed duplicate favorite item."
                else:
                    env.history.message("Add Favorite: cancelled overwriting favorite item.")              
                    return 
                
            else:
                ok2, text = writeColorSchemeToFavoritesFile(name)
        else:
            # User cancelled.
            return
        if ok2:
            
            self.favoritesComboBox.addItem(name)
            _lastItem = self.favoritesComboBox.count()
            self.favoritesComboBox.setCurrentIndex(_lastItem - 1)
            msg = "New favorite [%s] added." % (text)
        else:
            msg = "Can't add favorite [%s]: %s" % (name, text) # text is reason why not
        
        env.history.message(msg) 
        
        return
        
    def deleteFavorite(self):
        """
        Deletes the current favorite from the user's personal list of favorites
        (and from disk, only in the favorites folder though).
        
        @note: Cannot delete "Factory default settings".
        """
        currentIndex = self.favoritesComboBox.currentIndex()
        currentText = self.favoritesComboBox.currentText()
        if currentIndex == 0:
            msg = "Cannot delete '%s'." % currentText
        else:
            self.favoritesComboBox.removeItem(currentIndex)
            
            
            # delete file from the disk
            
            deleteFile= getFavoritePathFromBasename( currentText )
            os.remove(deleteFile)
            
            msg = "Deleted favorite named [%s].\n" \
                "and the favorite file [%s.txt]." \
                % (currentText, currentText)
            
        env.history.message(msg) 
        return
        
    def saveFavorite(self):
        """
        Writes the current favorite (selected in the combobox) to a file, any 
        where in the disk that 
        can be given to another NE1 user (i.e. as an email attachment).
        """
        
        cmd = greenmsg("Save Favorite File: ")
        env.history.message(greenmsg("Save Favorite File:"))
        current_favorite = self.favoritesComboBox.currentText()
        favfilepath = getFavoritePathFromBasename(current_favorite)
        
        formats = \
                    "Favorite (*.txt);;"\
                    "All Files (*.*)"
         
        
        fn = QFileDialog.getSaveFileName(
            self, 
            "Save Favorite As", # caption
            favfilepath, #where to save
            formats, # file format options
            QString("Favorite (*.txt)") # selectedFilter
            )
        if not fn:
            env.history.message(cmd + "Cancelled")
        
        else:
            saveFavoriteFile(str(fn), favfilepath)
        return
        
    def loadFavorite(self):
        """
        Prompts the user to choose a "favorite file" (i.e. *.txt) from disk to
        be added to the personal favorites list.
        """
        # If the file already exists in the favorites folder then the user is 
        # given the option of overwriting it or renaming it
        
        env.history.message(greenmsg("Load Favorite File:"))
        formats = \
                    "Favorite (*.txt);;"\
                    "All Files (*.*)"
         
        directory= getDefaultWorkingDirectory()
        
        fname = QFileDialog.getOpenFileName(self,
                                         "Choose a file to load",
                                         directory,
                                         formats)
                    
        if not fname:
            env.history.message("User cancelled loading file.")
            return

        else:
            canLoadFile=loadFavoriteFile(fname)
            
            if canLoadFile == 1:
                
            
                #get just the name of the file for loading into the combobox
            
                favName = os.path.basename(str(fname))
                name = favName[0:len(favName)-4]
                indexOfDuplicateItem = self.favoritesComboBox.findText(name)
            
                #duplicate exists in combobox 
            
                if indexOfDuplicateItem != -1:
                    ret = QMessageBox.warning( self, "Warning!",
                                               "The favorite file \"" + name + 
                                               "\"already exists.\n"
                                               "Do you want to overwrite the existing file?",
                                               "&Overwrite", "&Rename", "&Cancel",
                                               0,    # Enter == button 0
                                               1   # button 1
                                               )  
                
                    if ret == 0:
                        self.favoritesComboBox.removeItem(indexOfDuplicateItem)
                        self.favoritesComboBox.addItem(name)
                        _lastItem = self.favoritesComboBox.count()
                        self.favoritesComboBox.setCurrentIndex(_lastItem - 1)
                        ok2, text = writeColorSchemeToFavoritesFile(name)
                        msg = "Overwrote favorite [%s]." % (text)
                        env.history.message(msg) 
         
                    elif ret == 1:
                        # add new item to favorites folder as well as combobox
                        self.addFavorite()
                        
                    else:
                        #reset the display setting values to factory default
                    
                        factoryIndex = self.favoritesComboBox.findText(
                                             'Factory default settings')
                        self.favoritesComboBox.setCurrentIndex(factoryIndex)
                        env.prefs.restore_defaults(colorSchemePrefsList)
                        
                        # set it back to blue sky
                        self.win.glpane.setBackgroundGradient(1)
                        self.win.glpane.gl_update() 
                        env.history.message("Cancelled overwriting favorite file.")              
                        return 
                else:
                    self.favoritesComboBox.addItem(name)
                    _lastItem = self.favoritesComboBox.count()
                    self.favoritesComboBox.setCurrentIndex(_lastItem - 1)
                    msg = "Loaded favorite [%s]." % (name)
                    env.history.message(msg) 
         
                if env.prefs[backgroundGradient_prefs_key]:
                    self.win.glpane.setBackgroundGradient(env.prefs[backgroundGradient_prefs_key])
                else:
                    self.win.glpane.setBackgroundColor(env.prefs[backgroundColor_prefs_key])
                self.win.glpane.gl_update() 
            
            
        return
    
    
    
    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the Color Scheme Property Manager.  
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import WhatsThis_ColorScheme_PropertyManager
        WhatsThis_ColorScheme_PropertyManager(self)
                
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the Color Scheme Property Manager.  
        """
        #modify this for color schemes
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_ColorScheme_PropertyManager 
        ToolTip_ColorScheme_PropertyManager(self)
    
    