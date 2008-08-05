# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
ColorScheme_PropertyManager.py

 The ColorScheme_PropertyManager class provides a Property Manager
 for choosing various colors (example: background)

@author: Urmi
@version: $Id$
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

To do:
- Save/load hh and selection color style settings into/from favorites file.
"""
import os, time, fnmatch, string
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.prefs_constants import workingDirectory_prefs_key
from utilities.Log import greenmsg, redmsg

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui
from PyQt4.Qt import QFileDialog, QString, QMessageBox
from PyQt4.Qt import QColorDialog, QPixmap, QIcon
from PM.PM_Dialog   import PM_Dialog
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_ToolButtonRow import PM_ToolButtonRow
from PM.PM_ColorComboBox import PM_ColorComboBox
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON

from utilities.constants import diDNACYLINDER
from utilities.constants import yellow, orange, red, magenta, cyan, blue
from utilities.constants import white, black, gray, green, darkgreen

from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf

from utilities.icon_utilities import geticon
from utilities.debug import print_compact_traceback

bg_EVENING_SKY = 0
bg_BLUE_SKY = 1
bg_SEAGREEN = 2
bg_BLACK = 3
bg_WHITE = 4
bg_GRAY = 5
bg_CUSTOM = 6

#hover highlighting
# HHS = hover highlighting styles
from utilities.prefs_constants import HHS_INDEXES
from utilities.prefs_constants import HHS_OPTIONS

# SS = selection styles
from utilities.prefs_constants import SS_INDEXES
from utilities.prefs_constants import SS_OPTIONS

from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import backgroundColor_prefs_key
from utilities.prefs_constants import backgroundGradient_prefs_key
from utilities.prefs_constants import fogEnabled_prefs_key

from utilities.constants import black, white, gray

colorSchemePrefsList = \
                     [backgroundGradient_prefs_key,
                      backgroundColor_prefs_key,
                      fogEnabled_prefs_key,
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
    from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
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
        elif isinstance(val, str):
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

            try:
                if backgroundColor_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = tuple(map(float, pref_value[1:-1].split(',')))
                elif backgroundGradient_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = int(pref_value)
                elif fogEnabled_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = bool(int(pref_value))
                elif hoverHighlightingColorStyle_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = str(pref_value)
                elif hoverHighlightingColor_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = tuple(map(float, pref_value[1:-1].split(',')))
                elif selectionColorStyle_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = str(pref_value)
                elif selectionColor_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = tuple(map(float, pref_value[1:-1].split(',')))
                else:
                    print "Not sure what pref_key '%s' is." % pref_keyString
                    continue
            except:
                msg = "\npref_key = '%s'\nvalue = %s" \
                    % (pref_keyString, pref_value)
                print_compact_traceback(msg)

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
        #split keys in colorSchemePrefsList into version number and pref_key

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
        self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]

        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)

        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Edit the color scheme for NE1, including the background color, "\
            "hover highlighting and selection colors, etc."
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

        # background color setting combo box.
        change_connect( self.backgroundColorComboBox,
                      SIGNAL("activated(int)"),
                      self.changeBackgroundColor )

        #hover highlighting style combo box
        change_connect(self.hoverHighlightingStyleComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.changeHoverHighlightingStyle)
        change_connect(self.hoverHighlightingColorComboBox,
                       SIGNAL("editingFinished()"),
                       self.changeHoverHighlightingColor)

        #selection style combo box
        change_connect(self.selectionStyleComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.changeSelectionStyle)
        change_connect(self.selectionColorComboBox,
                       SIGNAL("editingFinished()"),
                       self.changeSelectionColor)

    def changeHoverHighlightingColor(self):
        """
        Slot method for Hover Highlighting color chooser.
        Change the (3D) hover highlighting color.
        """
        color = self.hoverHighlightingColorComboBox.getColor()
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
        color = self.selectionColorComboBox.getColor()
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
        self._updateAllWidgets()
        PM_Dialog.show(self)
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
                                         title = "Background")
        self._loadGroupBox2( self._pmGroupBox2 )

        self._pmGroupBox3 = PM_GroupBox( self,
                                         title = "Highlighting and Selection")
        self._loadGroupBox3( self._pmGroupBox3 )

        self._updateAllWidgets()

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
        from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
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
        self.backgroundColorComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label     =  "Color:",
                         spanWidth = False)

        self._loadBackgroundColorItems()

        self.enableFogCheckBox = \
            PM_CheckBox( pmGroupBox, text = "Enable fog" )

        connect_checkbox_with_boolean_pref( self.enableFogCheckBox, fogEnabled_prefs_key )
        return

    def _loadGroupBox3(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        # hover highlighting style and color
        self.hoverHighlightingStyleComboBox = \
            PM_ComboBox( pmGroupBox,
                         label     =  "Highlighting:",
                         )

        self._loadHoverHighlightingStyleItems()

        hhColorList = [yellow, orange, red, magenta,
                       cyan, blue, white, black, gray]
        hhColorNames = ["Yellow (default)", "Orange", "Red", "Magenta",
                        "Cyan", "Blue", "White", "Black", "Other color..."]

        self.hoverHighlightingColorComboBox = \
            PM_ColorComboBox(pmGroupBox,
                             colorList = hhColorList,
                             colorNames = hhColorNames,
                             color = env.prefs[hoverHighlightingColor_prefs_key]
                             )

        # selection style and color
        self.selectionStyleComboBox = \
            PM_ComboBox( pmGroupBox,
                         label     =  "Selection:",
                         )

        self._loadSelectionStyleItems()

        selColorList = [darkgreen, green, orange, red,
                        magenta, cyan, blue, white, black,
                        gray]
        selColorNames = ["Dark green (default)", "Green", "Orange", "Red",
                         "Magenta", "Cyan", "Blue", "White", "Black",
                         "Other color..."]

        self.selectionColorComboBox = \
            PM_ColorComboBox(pmGroupBox,
                             colorList = selColorList,
                             colorNames = selColorNames,
                             color = env.prefs[selectionColor_prefs_key]
                             )
        return

    def _updateAllWidgets(self):
        """
        Update all the PM widgets. This is typically called after applying
        a favorite.
        """
        self._updateBackgroundColorComboBoxIndex()
        self.updateCustomColorItemIcon(RGBf_to_QColor(env.prefs[backgroundColor_prefs_key]))
        self.hoverHighlightingStyleComboBox.setCurrentIndex(HHS_INDEXES.index(env.prefs[hoverHighlightingColorStyle_prefs_key]))
        self.hoverHighlightingColorComboBox.setColor(env.prefs[hoverHighlightingColor_prefs_key])
        self.selectionStyleComboBox.setCurrentIndex(SS_INDEXES.index(env.prefs[selectionColorStyle_prefs_key]))
        self.selectionColorComboBox.setColor(env.prefs[selectionColor_prefs_key])
        return

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
        backgroundIndexes = [bg_EVENING_SKY, bg_BLUE_SKY, bg_SEAGREEN,
                             bg_BLACK, bg_WHITE, bg_GRAY, bg_CUSTOM]

        backgroundNames   = ["Evening Sky (default)", "Blue Sky", "Sea Green",
                             "Black", "White", "Gray", "Custom..."]

        backgroundIcons   = ["Background_EveningSky", "Background_BlueSky",
                             "Background_SeaGreen",
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

        self._updateBackgroundColorComboBoxIndex() # Not needed, but OK.
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

        if idx == bg_EVENING_SKY:
            self.win.glpane.setBackgroundGradient(idx + 1)
        elif idx == bg_BLUE_SKY:
            self.win.glpane.setBackgroundGradient(idx + 1)
        elif idx == bg_SEAGREEN:
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
            self.updateCustomColorItemIcon(c)
        else:
            # User cancelled. Need to reset combobox to correct index.
            self._updateBackgroundColorComboBoxIndex()
        return

    def updateCustomColorItemIcon(self, qcolor):
        """
        Update the custom color item icon in the background color combobox
        with I{qcolor}.
        """
        pixmap = QPixmap(16, 16)
        pixmap.fill(qcolor)
        self.backgroundColorComboBox.setItemIcon(bg_CUSTOM, QIcon(pixmap))
        return

    def applyFavorite(self):
        """
        Apply the color scheme settings stored in the current favorite
        (selected in the combobox) to the current color scheme settings.
        """
        # Rules and other info:
        # The user has to press the button related to this method when he loads
        # a previously saved favorite file

        current_favorite = self.favoritesComboBox.currentText()
        if current_favorite == 'Factory default settings':
            env.prefs.restore_defaults(colorSchemePrefsList)
            # set it back to blue sky
            self.win.glpane.setBackgroundGradient(1)
        else:
            favfilepath = getFavoritePathFromBasename(current_favorite)
            loadFavoriteFile(favfilepath)
            if env.prefs[backgroundGradient_prefs_key]:
                self.win.glpane.setBackgroundGradient(env.prefs[backgroundGradient_prefs_key])
            else:
                self.win.glpane.setBackgroundColor(env.prefs[backgroundColor_prefs_key])
        #self.hoverHighlightingColorComboBox.setColor(env.prefs[hoverHighlightingColor_prefs_key])
        #self.selectionColorComboBox.setColor(env.prefs[selectionColor_prefs_key])
        self._updateAllWidgets()
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

        #Check to see if favfilepath exists first
        if not os.path.exists(favfilepath):
            msg = "%s does not exist" % favfilepath
            env.history.message(cmd + msg)
            return
        formats = \
                    "Favorite (*.txt);;"\
                    "All Files (*.*)"

        directory = self.currentWorkingDirectory
        saveLocation = directory + "/" + current_favorite + ".txt"

        fn = QFileDialog.getSaveFileName(
            self,
            "Save Favorite As", # caption
            saveLocation, #where to save
            formats, # file format options
            QString("Favorite (*.txt)") # selectedFilter
            )
        if not fn:
            env.history.message(cmd + "Cancelled")

        else:
            #remember this directory

            dir, fil = os.path.split(str(fn))
            self.setCurrentWorkingDirectory(dir)
            saveFavoriteFile(str(fn), favfilepath)
        return

    def setCurrentWorkingDirectory(self, dir = None):
        if os.path.isdir(dir):
            self.currentWorkingDirectory = dir
            self._setWorkingDirectoryInPrefsDB(dir)
        else:
            self.currentWorkingDirectory =  getDefaultWorkingDirectory()

    def _setWorkingDirectoryInPrefsDB(self, workdir = None):
        """
        [private method]
        Set the working directory in the user preferences database.

        @param workdir: The fullpath directory to write to the user pref db.
        If I{workdir} is None (default), there is no change.
        @type  workdir: string
        """
        if not workdir:
            return

        workdir = str(workdir)
        if os.path.isdir(workdir):
            workdir = os.path.normpath(workdir)
            env.prefs[workingDirectory_prefs_key] = workdir # Change pref in prefs db.
        else:
            msg = "[" + workdir + "] is not a directory. Working directory was not changed."
            env.history.message( redmsg(msg))
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

        directory = self.currentWorkingDirectory
        if directory == '':
            directory= getDefaultWorkingDirectory()

        fname = QFileDialog.getOpenFileName(self,
                                         "Choose a file to load",
                                         directory,
                                         formats)

        if not fname:
            env.history.message("User cancelled loading file.")
            return

        else:
            dir, fil = os.path.split(str(fname))
            self.setCurrentWorkingDirectory(dir)
            canLoadFile = loadFavoriteFile(fname)

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


