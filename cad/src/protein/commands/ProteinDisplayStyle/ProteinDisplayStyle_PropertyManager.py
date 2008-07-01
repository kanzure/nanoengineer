# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
ProteinDisplayStyle_PropertyManager.py

The ProteinDisplayStyle_PropertyManager class provides a Property Manager 
for the B{Display Style} command on the flyout toolbar in the 
Build > Protein mode. 

@author: Urmi
@version: $Id: 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""
import os, time, fnmatch, string
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.prefs_constants import workingDirectory_prefs_key

from utilities.Log import greenmsg
from utilities.constants import yellow, orange, red, magenta 
from utilities.constants import cyan, blue, white, black, gray

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui

from PyQt4.Qt import QFileDialog, QString, QMessageBox, QSlider
from PM.PM_Dialog   import PM_Dialog
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_StackedWidget import PM_StackedWidget
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ToolButtonRow import PM_ToolButtonRow
from PM.PM_Slider import PM_Slider
from PM.PM_Constants import PM_DONE_BUTTON
from PM.PM_Constants import PM_WHATS_THIS_BUTTON
from PM.PM_ColorComboBox import PM_ColorComboBox


# UM 20080623: the constants below need to be removed
from utilities.constants import diDNACYLINDER

from utilities.prefs_constants import proteinStyle_prefs_key
from utilities.prefs_constants import proteinStyleSmooth_prefs_key
from utilities.prefs_constants import proteinStyleQuality_prefs_key
from utilities.prefs_constants import proteinStyleScaling_prefs_key
from utilities.prefs_constants import proteinStyleScaleFactor_prefs_key
from utilities.prefs_constants import proteinStyleColors_prefs_key
from utilities.prefs_constants import proteinStyleAuxColors_prefs_key
from utilities.prefs_constants import proteinStyleCustomColor_prefs_key 
from utilities.prefs_constants import proteinStyleAuxCustomColor_prefs_key 
from utilities.prefs_constants import proteinStyleColorsDiscrete_prefs_key 
from utilities.prefs_constants import proteinStyleHelixColor_prefs_key 
from utilities.prefs_constants import proteinStyleStrandColor_prefs_key
from utilities.prefs_constants import proteinStyleCoilColor_prefs_key

proteinDisplayStylePrefsList = \
                         [proteinStyle_prefs_key,
                          proteinStyleSmooth_prefs_key,
                          proteinStyleQuality_prefs_key, 
                          proteinStyleScaling_prefs_key, 
                          proteinStyleScaleFactor_prefs_key, 
                          proteinStyleColors_prefs_key, 
                          proteinStyleAuxColors_prefs_key, 
                          proteinStyleCustomColor_prefs_key, 
                          proteinStyleAuxCustomColor_prefs_key, 
                          proteinStyleColorsDiscrete_prefs_key, 
                          proteinStyleHelixColor_prefs_key, 
                          proteinStyleStrandColor_prefs_key, 
                          proteinStyleCoilColor_prefs_key ]

# Protein Display Style Favorite File I/O functions. 

def writeProteinDisplayStyleSettingsToFavoritesFile( basename ):
    
    """
    Writes a "favorite file" (with a .txt extension) to store all the
    Protein display style settings (pref keys and their current values).

    @param basename: The filename (without the .fav extension) to write.
    @type  basename: string

    @note: The favorite file is written to the directory
            $HOME/Nanorex/Favorites/ProteinDisplayStyle.
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

    @param basename: The favorite filename (without the .txt extension).
    @type  basename: string

    @note: The (default) directory for all favorite files is
           $HOME/Nanorex/Favorites/ProteinDisplayStyle.
    """
    _ext = "txt"

    # Make favorite filename (i.e. ~/Nanorex/Favorites/ProteinDisplayStyleFavorites/basename.txt)
    from platform.PlatformDependent import find_or_make_Nanorex_subdir
    _dir = find_or_make_Nanorex_subdir('Favorites/ProteinDisplayStyle')
    return os.path.join(_dir, "%s.%s" % (basename, _ext))

def writeDnaFavoriteFile( filename ):
    """
    Writes a favorite file to I{filename}.
    """

    f = open(filename, 'w')

    # Write header
    f.write ('!\n! Protein display style favorite file')
    f.write ('\n!Created by NanoEngineer-1 on ')
    timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    f.write(timestr)

    #write preference list in file without the NE version
    for pref_key in proteinDisplayStylePrefsList:
        val = env.prefs[pref_key]

        pref_keyArray = pref_key.split("/")
        pref_key = pref_keyArray[1]

        if isinstance(val, int):
            f.write("%s = %d\n" % (pref_key, val))
        elif isinstance(val, float):
            f.write("%s = %-6.2f\n" % (pref_key, val))
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

    if line != "! DNA display style favorite file\n":
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

            # check if pref_value is an integer or float. Booleans currently
            # stored as integer as well.

            try:
                int(pref_value)
                pref_valueToStore = int(pref_value)

            except ValueError:
                pref_valueToStore = float(pref_value)


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
    Matches prefence key in the proteinDisplayStylePrefsList with pref_keyString
    from the favorte file that we intend to load.


    @param pref_keyString: preference from the favorite file to be loaded.
    @type  pref_keyString: string

    @note: very inefficient since worst case time taken is proportional to the
    size of the list. If original preference strings are in a dictionary, access
    can be done in constant time

    """

    for keys in proteinDisplayStylePrefsList:
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

    @param savePath: ~/Nanorex/Favorites/DnaDisplayStyle/$FAV_NAME.txt
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

class ProteinDisplayStyle_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The ProteinDisplayStyle_PropertyManager class provides a Property Manager 
    for the B{Display Style} command on the flyout toolbar in the 
    Build > Protein mode. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Edit Protein Display Style"
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
        self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]
        
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)

        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Modify the protein display settings below."
        self.updateMessage(msg)

    def connect_or_disconnect_signals(self, isConnect = True):
        
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
        
        #Display group box signal slot connections
        change_connect(self.proteinStyleComboBox,
                       SIGNAL("currentIndexChanged(int)"),
                       self.changeProteinDisplayStyle)
        
        change_connect(self.smoothingCheckBox,
                       SIGNAL("stateChanged(int)"),
                       self.smoothProteinDisplay)
        change_connect(self.scaleComboBox,
                       SIGNAL("currentIndexChanged(int)"),
                       self.changeProteinDisplayScale)
        change_connect(self.splineDoubleSpinBox,
                       SIGNAL("valueChanged(double)"),
                       self.changeProteinSplineValue)
        change_connect(self.scaleFactorDoubleSpinBox,
                       SIGNAL("valueChanged(double)"),
                       self.changeProteinScaleFactor)
        
        #color groupbox
        change_connect(self.proteinComponentComboBox,
                       SIGNAL("valueChanged(int)"),
                       self.chooseProteinComponent)
        
        change_connect(self.proteinAuxComponentComboBox,
                       SIGNAL("valueChanged(int)"),
                       self.chooseAuxilliaryProteinComponent)
        
        
        change_connect(self.customColorComboBox,
                       SIGNAL("editingFinished()"),
                       self.chooseCustomColor)
        
        change_connect(self.auxColorComboBox,
                       SIGNAL("editingFinished()"),
                       self.chooseAuxilliaryColor)
        
        change_connect(self.discColorCheckBox,
                       SIGNAL("stateChanged(int)"),
                       self.setDiscreteColors)
        
        change_connect(self.helixColorComboBox,
                       SIGNAL("editingFinished()"),
                       self.chooseHelixColor)
        
        change_connect(self.strandColorComboBox,
                       SIGNAL("editingFinished()"),
                       self.chooseStrandColor)
        
        change_connect(self.coilColorComboBox,
                       SIGNAL("editingFinished()"),
                       self.chooseCoilColor)

    #Protein Display methods         
        
    def  changeProteinDisplayStyle(self, idx):
        env.prefs[proteinStyle_prefs_key] = idx
        return
    
    def  changeProteinDisplayQuality(self, idx):
        env.prefs[proteinStyleQuality_prefs_key] = idx
        return
    
    def  smoothProteinDisplay(self, state):
        if state == Qt.Checked:
            env.prefs[proteinStyleSmooth_prefs_key] = True
        else:
            env.prefs[proteinStyleSmooth_prefs_key] = False
        return
    
    def  changeProteinDisplayScale(self, idx):
        env.prefs[proteinStyleScaling_prefs_key] = idx
        return
    
    def changeProteinSplineValue(self, val):
        env.prefs[proteinStyleQuality_prefs_key] = val
        return
    
    def changeProteinScaleFactor(self, val):
        env.prefs[proteinStyleScaleFactor_prefs_key] = val
        return
    
    def chooseProteinComponent(self, idx):
        env.prefs[proteinStyleColors_prefs_key] = idx
        return
    
    def chooseAuxilliaryProteinComponent(self, idx):
        env.prefs[proteinStyleAuxColors_prefs_key] = idx
        return
    
    def chooseCustomColor(self):
        color = self.customColorComboBox.getColor()
        env.prefs[proteinStyleCustomColor_prefs_key] = color
        return
    
    def chooseAuxilliaryColor(self):
        color = self.auxColorComboBox.getColor()
        env.prefs[proteinStyleAuxCustomColors_prefs_key] = color
        return  
    
        
    def chooseHelixColor(self):
        color = self.helixColorComboBox.getColor()
        env.prefs[proteinStyleHelixColor_prefs_key] = color
        return
    
    def chooseStrandColor(self):
        color = self.strandColorComboBox.getColor()
        env.prefs[proteinStyleStrandColor_prefs_key] = color
        return     
    
    def chooseCoilColor(self):
        color = self.coilColorComboBox.getColor()
        env.prefs[proteinStyleCoilColor_prefs_key] = color
        return     
    
    def setDiscreteColors(self, state):
        if state == Qt.Checked:
            env.prefs[proteinStyleColorsDiscrete_prefs_key] = True
        else:
            env.prefs[proteinStyleColorsDiscrete_prefs_key] = False
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

        #Not required for Proteins
        # Force the Global Display Style to "DNA Cylinder" so the user
        # can see the display style setting effects on any DNA in the current
        # model. The current global display style will be restored when leaving
        # this command (via self.close()).
        #self.originalDisplayStyle = self.o.getGlobalDisplayStyle()
        #self.o.setGlobalDisplayStyle(diDNACYLINDER)

        # Update all PM widgets, then establish their signal-slot connections.
        # note: It is important to update the widgets *first* since doing
        # it in the reverse order will generate signals when updating
        # the PM widgets (via updateDnaDisplayStyleWidgets()), causing
        # unneccessary repaints of the model view.
        self.updateProteinDisplayStyleWidgets()
        self.connect_or_disconnect_signals(isConnect = True)

    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        self.connect_or_disconnect_signals(False)
        PM_Dialog.close(self)

        #Not required for proteins
        # Restore the original global display style.
        #self.o.setGlobalDisplayStyle(self.originalDisplayStyle)

    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Favorites")
        self._loadGroupBox1( self._pmGroupBox1 )

        self._pmGroupBox2 = PM_GroupBox( self,
                                         title = "Display")
        self._loadGroupBox2( self._pmGroupBox2 )

        self._pmGroupBox3 = PM_GroupBox( self,
                                         title = "Color")
        self._loadGroupBox3( self._pmGroupBox3 )

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        # Other info
        # Not only loads the factory default settings but also all the favorite
        # files stored in the ~/Nanorex/Favorites/ProteinDisplayStyle directory

        favoriteChoices = ['Factory default settings']

        #look for all the favorite files in the favorite folder and add them to
        # the list
        from platform.PlatformDependent import find_or_make_Nanorex_subdir
        _dir = find_or_make_Nanorex_subdir('Favorites/ProteinDisplayStyle')


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

        self.favoritesComboBox.setWhatsThis(
            """<b> List of Favorites </b>

            <p>
            Creates a list of favorite Protein display styles. Once favorite
            styles have been added to the list using the Add Favorite button,
            the list will display the chosen favorites.
            To change the current favorite, select a current favorite from
            the list, and push the Apply Favorite button.""")

        # PM_ToolButtonRow ===============

        # Button list to create a toolbutton row.
        # Format:
        # - QToolButton, buttonId, buttonText,
        # - iconPath,
        # - tooltip, shortcut, column

        BUTTON_LIST = [
            ( "QToolButton", 1,  "APPLY_FAVORITE","ui/actions/Properties Manager/ApplyPeptideDisplayStyleFavorite.png",
              "Apply Favorite", "", 0),   
            ( "QToolButton", 2,  "ADD_FAVORITE",
              "ui/actions/Properties Manager/AddFavorite.png","Add Favorite", "", 1),
            ( "QToolButton", 3,  "DELETE_FAVORITE", "ui/actions/Properties Manager/DeleteFavorite.png",
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
        proteinStyleChoices = ['Main chain - wire', 
                               'Main chain - cylinder', 
                               'Main chain - ball and stick',
                               'Spline',
                               'Tue',
                               'Strand',
                               'Flat ribbon',
                               'Solid ribbon',
                               'Cartoons',
                               'Ladder',
                               'Peptide tiles'
                               ]

        self.proteinStyleComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Style:",
                         choices       =  proteinStyleChoices,
                         setAsDefault  =  True)

        self.splineDoubleSpinBox = \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Spline:",
                              value         =  5,
                              setAsDefault  =  True,
                              minimum       =  1,
                              maximum       =  20,
                              decimals      =  0,
                              singleStep    =  1 )
            
        
        self.smoothingCheckBox = \
            PM_CheckBox( pmGroupBox,
                         text         = "Smoothing",
                         setAsDefault = True)

        scaleChoices = ['Constant', 'Secondary structure', 'B-factor']


        self.scaleComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Scaling:",
                         choices       =  scaleChoices,
                         setAsDefault  =  True)
        self.scaleFactorDoubleSpinBox = \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Scaling factor:",
                              value         =  1.00,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  5.0,
                              decimals      =  1,
                              singleStep    =  0.1 )
   
    def _loadGroupBox3(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        colorChoices = ['Chunk', 'Chain', 'Order', 'Hydropathy', 'Polarity',
                        'Acidity', 'Size', 'Character', 'Number of contacts',
                        'Secondary structure type', 'Secondary structure order',
                        'B-factor', 'Occupancy', 'Custom']

        self.proteinComponentComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Color:",
                         choices       =  colorChoices,
                         setAsDefault  =  True)

        colorList = [orange, yellow, red, magenta, 
                       cyan, blue, white, black, gray]
        colorNames = ["Orange(default)", "Yellow", "Red", "Magenta", 
                        "Cyan", "Blue", "White", "Black", "Other color..."]
    
        
        self.customColorComboBox = \
            PM_ColorComboBox(pmGroupBox,
                            colorList = colorList,
                            colorNames = colorNames,
                            label      = "Custom color:",
                            color      = orange,
                            setAsDefault  =  True)
                            
        colorChoices1 = [ 'Same as main color', 'Chunk', 'Chain', 'Order', 'Hydropathy', 'Polarity',
                        'Acidity', 'Size', 'Character', 'Number of contacts',
                        'Secondary structure type', 'Secondary structure order',
                        'B-factor', 'Occupancy', 'Custom']
        
        self.proteinAuxComponentComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Color:",
                         choices       =  colorChoices1,
                         setAsDefault  =  True)
        
        colorListAux = [orange, yellow, red, magenta,cyan, blue, white, black, gray]
        
        colorNamesAux = ["Orange(default)", "Yellow", "Red", "Magenta", "Cyan", 
                         "Blue", "White", "Black", "Other color..."]
        
        self.auxColorComboBox = \
            PM_ColorComboBox(pmGroupBox,
                             colorList = colorListAux,
                             colorNames = colorNamesAux, 
                             label = "Auxilliary color:",
                             color = gray,
                             setAsDefault  =  True)

        self.discColorCheckBox = \
            PM_CheckBox( pmGroupBox,
                         text = "Discrete color:",
                         setAsDefault = True
                         )

        colorListHelix = [red, yellow, gray, magenta, 
                          cyan, blue, white, black, orange]
        
        colorNamesHelix = ["Red(default)", "Yellow", "Gray", "Magenta", 
                           "Cyan", "Blue", "White", "Black", "Other color..."]
        self.helixColorComboBox = \
            PM_ColorComboBox(pmGroupBox,
                            colorList = colorListHelix,
                            colorNames = colorNamesHelix,  
                            label      = "Helix color:",
                            color      = red,
                            setAsDefault  =  True)
        
        colorListStrand = [cyan, yellow, gray, magenta, 
                           red, blue, white, black, orange]
        
        colorNamesStrand = ["Cyan(default)", "Yellow", "Gray", "Magenta", 
                            "Red", "Blue", "White", "Black", "Other color..."]
        
        self.strandColorComboBox = \
            PM_ColorComboBox(pmGroupBox,
                            colorList = colorListStrand,
                            colorNames = colorNamesStrand, 
                            label      = "Strand color:",
                            color      = cyan,
                            setAsDefault  =  True)

        self.coilColorComboBox = \
            PM_ColorComboBox(pmGroupBox,
                            colorList = colorListAux,
                            colorNames = colorNamesAux,
                            label      = "Coil color:",
                            color      = gray,
                            setAsDefault  =  True)

    def updateProteinDisplayStyleWidgets( self ):
        """
        Updates all the Protein Display style widgets based on the current pref keys
        values
        
        """
        self.proteinStyleComboBox.setCurrentIndex(env.prefs[proteinStyle_prefs_key]) 
        self.splineDoubleSpinBox.setValue(env.prefs[proteinStyleQuality_prefs_key])  
        if env.prefs[proteinStyleSmooth_prefs_key] == True:        
            self.smoothingCheckBox.setCheckState(Qt.Checked)
        else:
            self.smoothingCheckBox.setCheckState(Qt.Unchecked)
        self.scaleComboBox.setCurrentIndex(env.prefs[proteinStyleScaling_prefs_key])
        self.scaleFactorDoubleSpinBox.setValue(env.prefs[proteinStyleScaleFactor_prefs_key])         
        self.proteinComponentComboBox.setCurrentIndex(env.prefs[proteinStyleColors_prefs_key])         
        self.customColorComboBox.setColor(env.prefs[proteinStyleCustomColor_prefs_key])
        self.proteinAuxComponentComboBox.setCurrentIndex(env.prefs[proteinStyleAuxColors_prefs_key])        
        self.auxColorComboBox.setColor(env.prefs[proteinStyleAuxCustomColor_prefs_key])
        if env.prefs[proteinStyleColorsDiscrete_prefs_key] == True:        
            self.discColorCheckBox.setCheckState(Qt.Checked)  
        else:
            self.discColorCheckBox.setCheckState(Qt.Unchecked)   
        self.helixColorComboBox.setColor(env.prefs[proteinStyleHelixColor_prefs_key])
        self.strandColorComboBox.setColor(env.prefs[proteinStyleStrandColor_prefs_key])
        self.coilColorComboBox.setColor(env.prefs[proteinStyleCoilColor_prefs_key])    
                
        return

    def applyFavorite(self):
        
        # Rules and other info:
        # The user has to press the button related to this method when he loads
        # a previously saved favorite file

        current_favorite = self.favoritesComboBox.currentText()
        if current_favorite == 'Factory default settings':
            env.prefs.restore_defaults(proteinDisplayStylePrefsList)
        else:
            favfilepath = getFavoritePathFromBasename(current_favorite)
            loadFavoriteFile(favfilepath)

        self.updateProteinDisplayStyleWidgets()
        return

    def addFavorite(self):
        
        # Rules and other info:

        # - The new favorite is defined by the current Protein display style 

        #  settings.

        # - The user is prompted to type in a name for the new
        #    favorite.
        # - The DNA display style settings are written to a file in a special
        #    directory on the disk
        # (i.e. $HOME/Nanorex/Favorites/ProteinDisplayStyle/$FAV_NAME.txt).
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
            # $HOME/Nanorex/Favorites/DnaDisplayStyle/ directory

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
                    ok2, text = writeProteinDisplayStyleSettingsToFavoritesFile(name)
                    indexOfDuplicateItem = self.favoritesComboBox.findText(name)
                    self.favoritesComboBox.removeItem(indexOfDuplicateItem)
                    print "Add Favorite: removed duplicate favorite item."
                else:
                    env.history.message("Add Favorite: cancelled overwriting favorite item.")
                    return

            else:
                ok2, text = writeProteinDisplayStyleSettingsToFavoritesFile(name)
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
        

        cmd = greenmsg("Save Favorite File: ")
        env.history.message(greenmsg("Save Favorite File:"))
        current_favorite = self.favoritesComboBox.currentText()
        favfilepath = getFavoritePathFromBasename(current_favorite)

        formats = \
                "Favorite (*.txt);;"\
                "All Files (*.*)"
                    
         
        directory = self.currentWorkingDirectory
        saveLocation = directory + "/" + current_favorite + ".txt"
        

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
                        ok2, text = writeProteinDisplayStyleSettingsToFavoritesFile(name)
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
                        env.prefs.restore_defaults(proteinDisplayStylePrefsList)

                        env.history.message("Cancelled overwriting favorite file.")
                        return
                else:
                    self.favoritesComboBox.addItem(name)
                    _lastItem = self.favoritesComboBox.count()
                    self.favoritesComboBox.setCurrentIndex(_lastItem - 1)
                    msg = "Loaded favorite [%s]." % (name)

                    env.history.message(msg) 
         
                self.updateProteinDisplayStyleWidgets()  

        return

    def _addWhatsThisText( self ):
        
        from ne1_ui.WhatsThisText_for_PropertyManagers import WhatsThis_EditDnaDisplayStyle_PropertyManager
        WhatsThis_EditDnaDisplayStyle_PropertyManager(self)

    def _addToolTipText(self):
        

        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_EditProteinDisplayStyle_PropertyManager 
        ToolTip_EditProteinDisplayStyle_PropertyManager(self)



