# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
LightingScheme_PropertyManager.py

 The LightingScheme_PropertyManager class provides a Property Manager
 for controlling light settings and creating favorites.

@author: Kyle
@version: $Id$
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""
import os, time, fnmatch
import foundation.env as env

from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.Log import greenmsg

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QFileDialog, QString, QMessageBox
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_ToolButtonRow import PM_ToolButtonRow
from PM.PM_ColorComboBox import PM_ColorComboBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON

from utilities.debug import print_compact_traceback

from utilities.prefs_constants import material_specular_highlights_prefs_key
from utilities.prefs_constants import material_specular_shininess_prefs_key
from utilities.prefs_constants import material_specular_brightness_prefs_key
from utilities.prefs_constants import material_specular_finish_prefs_key

from utilities.prefs_constants import light1Color_prefs_key
from utilities.prefs_constants import light2Color_prefs_key
from utilities.prefs_constants import light3Color_prefs_key
from utilities.prefs_constants import glpane_lights_prefs_key
import foundation.preferences as preferences


lightingSchemePrefsList = \
                     [light1Color_prefs_key,
                      light2Color_prefs_key,
                      light3Color_prefs_key,
                      material_specular_highlights_prefs_key,
                      material_specular_finish_prefs_key,
                      material_specular_shininess_prefs_key,
                      material_specular_brightness_prefs_key
                      ]

# =
# Lighting Scheme Favorite File I/O functions.

def writeLightingSchemeToFavoritesFile( basename ):
    """
    Writes a "favorite file" (with a .txt extension) to store all the
    lighting scheme settings (pref keys and their current values).

    @param base: The filename (without the .txt extension) to write.
    @type  basename: string

    @note: The favorite file is written to the directory
            $HOME/Nanorex/Favorites/LightingScheme.
    """

    if not basename:
        return 0, "No name given."

    # Get filename and write the favorite file.
    favfilepath = getFavoritePathFromBasename(basename)
    writeLightingSchemeFavoriteFile(favfilepath)

    # msg = "Problem writing file [%s]" % favfilepath

    return 1, basename


def getFavoritePathFromBasename( basename ):
    """
    Returns the full path to the favorite file given a basename.

    @param basename: The favorite filename (without the .txt extension).
    @type  basename: string

    @note: The (default) directory for all favorite files is
           $HOME/Nanorex/Favorites/LightingScheme.
    """
    _ext = "txt"

    # Make favorite filename (i.e. ~/Nanorex/Favorites/LightingScheme/basename.txt)
    from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
    _dir = find_or_make_Nanorex_subdir('Favorites/LightingScheme')
    return os.path.join(_dir, "%s.%s" % (basename, _ext))

def getFavoriteTempFilename():
    """
    Returns the full path to the single Lighting Scheme favorite temporary file.

    @note: The fullpath returned is
           $HOME/Nanorex/temp/LightingSchemeTempfile.txt.
    """
    _basename = "LightingSchemeTempfile"
    _ext = "txt"

    # Make favorite filename (i.e. ~/Nanorex/Favorites/LightingScheme/basename.txt)
    from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
    _dir = find_or_make_Nanorex_subdir('temp')
    return os.path.join(_dir, "%s.%s" % (_basename, _ext))

def getLights():
    """
    return lighting values from the standard preferences database, if possible;
    if correct values were loaded, start using them, and do gl_update unless option for that is False;
    return True if you loaded new values, False if that failed
    """

    # code below copied from GLPane.loadLighting()

    try:
        prefs = preferences.prefs_context()
        key = glpane_lights_prefs_key
        try:
            val = prefs[key]
        except KeyError:
            # none were saved; not an error and not even worthy of a message
            # since this is called on startup and it's common for nothing to be saved.
            # Return with no changes.
            return False
        # At this point, you have a saved prefs val, and if this is wrong it's an error.
        # val format is described (partly implicitly) in saveLighting method.
        res = [] # will become new argument to pass to self.setLighting method, if we succeed
        for name in ['light0','light1','light2']:
            params = val[name] # a dict of ambient, diffuse, specular, x, y, z, enabled
            color = params['color'] # light color (r,g,b)
            a = params['ambient_intensity'] # ambient intensity
            d = params['diffuse_intensity'] # diffuse intensity
            s = params['specular_intensity'] # specular intensity
            x = params['xpos'] # X position
            y = params['ypos'] # Y position
            z = params['zpos'] # Z position
            e = params['enabled'] # boolean

            res.append( (color,a,d,s,x,y,z,e) )
        return True, res
    except:
        print_compact_traceback("bug: exception in getLights: ")
        #e redmsg?
        return False, res
    pass

def writeLightingSchemeFavoriteFile( filename ):
    """
    Writes a favorite file to I{filename}.
    """

    f = open(filename, 'w')

    # Write header
    f.write ('!\n! Lighting Scheme favorite file')
    f.write ('\n!Created by NanoEngineer-1 on ')
    timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
    f.write(timestr)
    # get the current three lights
    ok, lights = getLights()
    if not ok:
        print "error getting lights"
        return
    # write lights to the favorites file
    for (i, light) in zip(range(3),lights):
        name = "light%d" % i
        print name, light
        f.write("%s = %s\n" % (name, light))
    #write preference list in file without the NE version
    for pref_key in lightingSchemePrefsList:
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
        elif isinstance(val, float):
            f.write("%s = %f\n" % (pref_key, val))
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

    if line != "! Lighting Scheme favorite file\n":
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
                if light1Color_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = tuple(map(float, pref_value[1:-1].split(',')))
                elif light2Color_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = tuple(map(float, pref_value[1:-1].split(',')))
                elif light3Color_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = tuple(map(float, pref_value[1:-1].split(',')))
                elif material_specular_highlights_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = int(pref_value)
                elif material_specular_finish_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = float(pref_value)
                elif material_specular_shininess_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = float(pref_value)
                elif material_specular_brightness_prefs_key.endswith(pref_keyString):
                    pref_valueToStore = float(pref_value)
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
    Matches prefence key in the lightingSchemePrefsList with pref_keyString
    from the favorte file that we intend to load.


    @param pref_keyString: preference from the favorite file to be loaded.
    @type  pref_keyString: string

    @note: very inefficient since worst case time taken is proportional to the
    size of the list. If original preference strings are in a dictionary, access
    can be done in constant time

    """

    for keys in lightingSchemePrefsList:
        #split keys in lightingSchemePrefsList into version number and pref_key

        pref_array= keys.split("/")
        if pref_array[1] == pref_keyString:
            return keys

    return None

def saveFavoriteFile( savePath, fromPath ):
    """
    Save favorite file to anywhere in the disk

    @param savePath: full path for the location where the favorite file is to be saved.
    @type  savePath: string

    @param fromPath: ~/Nanorex/Favorites/LightingScheme/$FAV_NAME.txt
    @type  fromPath: string

    """
    fromPath = getFavoriteTempFilename()
    writeLightingSchemeFavoriteFile(fromPath)

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
from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager
class LightingScheme_PropertyManager(Command_PropertyManager):
    """
    The LightingScheme_PropertyManager class provides a Property Manager
    for changing light properties as well as material properties.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Lighting Scheme"
    pmName        =  title
    iconPath      =  "ui/actions/View/LightingScheme.png"


    def __init__( self, command ):
        """
        Constructor for the property manager.
        """

        _superclass.__init__(self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Edit the lighting scheme for NE1. Includes turning lights on and off, "\
            "changing light colors, changing the position of lights as well as,"\
            "changing the ambient, diffuse, and specular properites."
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

        # Directional Lighting Properties
        change_connect(self.ambientDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)
        change_connect(self.lightColorComboBox, SIGNAL("editingFinished()"), self.changeLightColor)
        change_connect(self.enableLightCheckBox, SIGNAL("toggled(bool)"), self.toggle_light)
        change_connect(self.lightComboBox, SIGNAL("activated(int)"), self.change_active_light)
        change_connect(self.diffuseDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)
        change_connect(self.specularDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)
        change_connect(self.xDoubleSpinBox, SIGNAL("editingFinished()"), self.save_lighting)
        change_connect(self.yDoubleSpinBox, SIGNAL("editingFinished()"), self.save_lighting)
        change_connect(self.zDoubleSpinBox, SIGNAL("editingFinished()"), self.save_lighting)
        # Material Specular Properties
        change_connect(self.brightnessDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_material_brightness)
        change_connect(self.finishDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_material_finish)
        change_connect(self.enableMaterialPropertiesComboBox, SIGNAL("toggled(bool)"), self.toggle_material_specularity)
        change_connect(self.shininessDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_material_shininess)
        self._setup_material_group()
        return

    def _updatePage_Lighting(self, lights = None): #mark 051124
        """
        Setup widgets to initial (default or defined) values on the Lighting page.
        """
        if not lights:
            self.lights = self.original_lights = self.win.glpane.getLighting()
        else:
            self.lights = lights

        light_num = self.lightComboBox.currentIndex()


        # Move lc_prefs_keys upstairs.  Mark.
        lc_prefs_keys = [light1Color_prefs_key, light2Color_prefs_key, light3Color_prefs_key]
        self.current_light_key = lc_prefs_keys[light_num] # Get prefs key for current light color.
        self.lightColorComboBox.setColor(env.prefs[self.current_light_key])
        self.light_color = env.prefs[self.current_light_key]

        # These sliders generate signals whenever their 'setValue()' slot is called (below).
        # This creates problems (bugs) for us, so we disconnect them temporarily.
        self.disconnect(self.ambientDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)
        self.disconnect(self.diffuseDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)
        self.disconnect(self.specularDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)

        # self.lights[light_num][0] contains 'color' attribute.
        # We already have it (self.light_color) from the prefs key (above).
        a = self.lights[light_num][1] # ambient intensity
        d = self.lights[light_num][2] # diffuse intensity
        s = self.lights[light_num][3] # specular intensity
        g = self.lights[light_num][4] # xpos
        h = self.lights[light_num][5] # ypos
        k = self.lights[light_num][6] # zpos


        self.ambientDoubleSpinBox.setValue(a)# generates signal
        self.diffuseDoubleSpinBox.setValue(d) # generates signal
        self.specularDoubleSpinBox.setValue(s) # generates signal
        self.xDoubleSpinBox.setValue(g) # generates signal
        self.yDoubleSpinBox.setValue(h) # generates signal
        self.zDoubleSpinBox.setValue(k) # generates signal

        self.enableLightCheckBox.setChecked(self.lights[light_num][7])

        # Reconnect the slots to the light sliders.
        self.connect(self.ambientDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)
        self.connect(self.diffuseDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)
        self.connect(self.specularDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_lighting)

        self.update_light_combobox_items()
        self.save_lighting()
        self._setup_material_group()
        return

    def _setup_material_group(self, reset = False):
        """
        Setup Material Specularity widgets to initial (default or defined) values on the Lighting page.
        If reset = False, widgets are reset from the prefs db.
        If reset = True, widgets are reset from their previous values.
        """

        if reset:
            self.material_specularity = self.original_material_specularity
            self.whiteness = self.original_whiteness
            self.shininess = self.original_shininess
            self.brightness = self.original_brightness
        else:
            self.material_specularity = self.original_material_specularity = \
                env.prefs[material_specular_highlights_prefs_key]
            self.whiteness = self.original_whiteness = \
                env.prefs[material_specular_finish_prefs_key]
            self.shininess = self.original_shininess = \
                env.prefs[material_specular_shininess_prefs_key]
            self.brightness = self.original_brightness= \
                env.prefs[material_specular_brightness_prefs_key]

        # Enable/disable material specularity properites.
        self.enableMaterialPropertiesComboBox.setChecked(self.material_specularity)

        # For whiteness, the stored range is 0.0 (Plastic) to 1.0 (Metal).
        self.finishDoubleSpinBox.setValue(self.whiteness) # generates signal

        # For shininess, the range is 15 (low) to 60 (high).  Mark. 051129.
        self.shininessDoubleSpinBox.setValue(self.shininess) # generates signal

        # For brightness, the range is 0.0 (low) to 1.0 (high).  Mark. 051203.
        self.brightnessDoubleSpinBox.setValue(self.brightness) # generates signal
        return

    def toggle_material_specularity(self, val):
        """
        This is the slot for the Material Specularity Enabled checkbox.
        """
        env.prefs[material_specular_highlights_prefs_key] = val

    def change_material_finish(self, finish):
        """
        This is the slot for the Material Finish spin box.
        'finish' is between 0.0 and 1.0.
        Saves finish parameter to pref db.
        """
        # For whiteness, the stored range is 0.0 (Metal) to 1.0 (Plastic).
        env.prefs[material_specular_finish_prefs_key] = finish

    def change_material_shininess(self, shininess):
        """
        This is the slot for the Material Shininess spin box.
        'shininess' is between 15 (low) and 60 (high).
        """
        env.prefs[material_specular_shininess_prefs_key] = shininess

    def change_material_brightness(self, brightness):
        """
        This is the slot for the Material Brightness sping box.
        'brightness' is between 0.0 (low) and 1.0 (high).
        """
        env.prefs[material_specular_brightness_prefs_key] = brightness

    def toggle_light(self, on):
        """
        Slot for light 'On' checkbox.
        It updates the current item in the light combobox with '(On)' or
        '(Off)' label.
        """
        if on:
            txt = "%d (On)" % (self.lightComboBox.currentIndex()+1)
        else:
            txt = "%d (Off)" % (self.lightComboBox.currentIndex()+1)
        self.lightComboBox.setItemText(self.lightComboBox.currentIndex(),txt)

        self.save_lighting()

    def change_lighting(self, specularityValueJunk = None):
        """
        Updates win.glpane lighting using the current lighting parameters from
        the light checkboxes and sliders. This is also the slot for the light
        spin boxes.
        @param specularityValueJunk: This value from the spin box is not used
                     We are interested in valueChanged signal only
        @type specularityValueJunk = int or None

        """

        light_num = self.lightComboBox.currentIndex()

        light1, light2, light3 = self.win.glpane.getLighting()

        a = self.ambientDoubleSpinBox.value()
        d = self.diffuseDoubleSpinBox.value()
        s = self.specularDoubleSpinBox.value()
        g = self.xDoubleSpinBox.value()
        h = self.yDoubleSpinBox.value()
        k = self.zDoubleSpinBox.value()

        new_light = [  self.light_color, a, d, s, g, h, k,\
                       self.enableLightCheckBox.isChecked()]

        # This is a kludge.  I'm certain there is a more elegant way.  Mark 051204.
        if light_num == 0:
            self.win.glpane.setLighting([new_light, light2, light3])
        elif light_num == 1:
            self.win.glpane.setLighting([light1, new_light, light3])
        elif light_num == 2:
            self.win.glpane.setLighting([light1, light2, new_light])
        else:
            print "Unsupported light # ", light_num,". No lighting change made."

    def change_active_light(self, currentIndexJunk = None):
        """
        Slot for the Light number combobox.  This changes the current light.
        @param currentIndexJunk: This index value from the combobox is not used
            We are interested in 'activated' signal only
        @type currentIndexJunk = int or None
        """
        self._updatePage_Lighting()

    def reset_lighting(self):
        """
        Slot for Reset button.
        """
        # This has issues.
        # I intend to remove the Reset button for A7.  Confirm with Bruce.  Mark 051204.
        self._setup_material_group(reset = True)
        self._updatePage_Lighting(self.original_lights)
        self.win.glpane.saveLighting()

    def save_lighting(self):
        """
        Saves lighting parameters (but not material specularity parameters)
        to pref db. This is also the slot for light sliders (only when
        released).
        """
        self.change_lighting()
        self.win.glpane.saveLighting()

    def restore_default_lighting(self):
        """
        Slot for Restore Defaults button.
        """

        self.win.glpane.restoreDefaultLighting()

        # Restore defaults for the Material Specularity properties
        env.prefs.restore_defaults([
            material_specular_highlights_prefs_key,
            material_specular_shininess_prefs_key,
            material_specular_finish_prefs_key,
            material_specular_brightness_prefs_key, #bruce 051203 bugfix
        ])

        self._updatePage_Lighting()
        self.save_lighting()

    def show(self):
        """
        Shows the Property Manager. extends superclass method.
        """
        _superclass.show(self)

        self._updateAllWidgets()


    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Favorites")
        self._loadGroupBox1( self._pmGroupBox1 )

        self._pmGroupBox2 = PM_GroupBox( self,
                                         title = "Directional Lights")
        self._loadGroupBox2( self._pmGroupBox2 )

        self._pmGroupBox3 = PM_GroupBox( self,
                                         title = "Material Properties")
        self._loadGroupBox3( self._pmGroupBox3 )

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        favoriteChoices = ['Factory default settings']

        #look for all the favorite files in the favorite folder and add them to
        # the list
        from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
        _dir = find_or_make_Nanorex_subdir('Favorites/LightingScheme')


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
              "ui/actions/Properties Manager/ApplyLightingSchemeFavorite.png",
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

        self.lightComboBox  = \
            PM_ComboBox( pmGroupBox,
                         choices = ["1", "2", "3"],
                         label     =  "Light:")

        self.enableLightCheckBox = \
            PM_CheckBox( pmGroupBox, text = "On" )

        self.lightColorComboBox = \
            PM_ColorComboBox(pmGroupBox)
        self.ambientDoubleSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             maximum = 1.0,
                             minimum = 0.0,
                             decimals = 2,
                             singleStep = .1,
                             label = "Ambient:")
        self.diffuseDoubleSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             maximum = 1.0,
                             minimum = 0.0,
                             decimals = 2,
                             singleStep = .1,
                             label = "Diffuse:")
        self.specularDoubleSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             maximum = 1.0,
                             minimum = 0.0,
                             decimals = 2,
                             singleStep = .1,
                             label = "Specular:")

        self.positionGroupBox = \
            PM_GroupBox( pmGroupBox,
                         title = "Position:")

        self.xDoubleSpinBox = \
            PM_DoubleSpinBox(self.positionGroupBox,
                             maximum = 1000,
                             minimum = -1000,
                             decimals = 1,
                             singleStep = 10,
                             label = "X:")
        self.yDoubleSpinBox = \
            PM_DoubleSpinBox(self.positionGroupBox,
                             maximum = 1000,
                             minimum = -1000,
                             decimals = 1,
                             singleStep = 10,
                             label = "Y:")
        self.zDoubleSpinBox = \
            PM_DoubleSpinBox(self.positionGroupBox,
                             maximum = 1000,
                             minimum = -1000,
                             decimals = 1,
                             singleStep = 10,
                             label = "Z:")
        return

    def _loadGroupBox3(self, pmGroupBox):
        """
        Load widgets in group box.
        """

        self.enableMaterialPropertiesComboBox = \
            PM_CheckBox( pmGroupBox, text = "On")
        self.finishDoubleSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             maximum = 1.0,
                             minimum = 0.0,
                             decimals = 2,
                             singleStep = .1,
                             label = "Finish:")
        self.shininessDoubleSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             maximum = 60,
                             minimum = 15,
                             decimals = 2,
                             label = "Shininess:")
        self.brightnessDoubleSpinBox = \
            PM_DoubleSpinBox(pmGroupBox,
                             maximum = 1.0,
                             minimum = 0.0,
                             decimals = 2,
                             singleStep = .1,
                             label = "Brightness:")
        return

    def _updateAllWidgets(self):
        """
        Update all the PM widgets. This is typically called after applying
        a favorite.
        """
        self._updatePage_Lighting()
        return

    def update_light_combobox_items(self):
        """
        Updates all light combobox items with '(On)' or '(Off)' label.
        """
        for i in range(3):
            if self.lights[i][7]:
                txt = "%d (On)" % (i+1)
            else:
                txt = "%d (Off)" % (i+1)
            self.lightComboBox.setItemText(i, txt)
        return

    def changeLightColor(self):
        """
        Slot method for the ColorComboBox
        """
        color = self.lightColorComboBox.getColor()
        env.prefs[self.current_light_key] = color
        self.light_color = env.prefs[self.current_light_key]
        self.save_lighting()
        return

    def applyFavorite(self):
        """
        Apply the lighting scheme settings stored in the current favorite
        (selected in the combobox) to the current lighting scheme settings.
        """
        # Rules and other info:
        # The user has to press the button related to this method when he loads
        # a previously saved favorite file

        current_favorite = self.favoritesComboBox.currentText()
        if current_favorite == 'Factory default settings':
            #env.prefs.restore_defaults(lightingSchemePrefsList)
            self.restore_default_lighting()
        else:
            favfilepath = getFavoritePathFromBasename(current_favorite)
            loadFavoriteFile(favfilepath)
        self._updateAllWidgets()
        self.win.glpane.gl_update()
        return

    def addFavorite(self):
        """
        Adds a new favorite to the user's list of favorites.
        """
        # Rules and other info:
        # - The new favorite is defined by the current lighting scheme
        #    settings.

        # - The user is prompted to type in a name for the new
        #    favorite.
        # - The lighting scheme settings are written to a file in a special
        #    directory on the disk
        # (i.e. $HOME/Nanorex/Favorites/LightingScheme/$FAV_NAME.txt).
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
            # $HOME/Nanorex/Favorites/LightingScheme/ directory

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
                    ok2, text = writeLightingSchemeToFavoritesFile(name)
                    indexOfDuplicateItem = self.favoritesComboBox.findText(name)
                    self.favoritesComboBox.removeItem(indexOfDuplicateItem)
                    print "Add Favorite: removed duplicate favorite item."
                else:
                    env.history.message("Add Favorite: cancelled overwriting favorite item.")
                    return

            else:
                ok2, text = writeLightingSchemeToFavoritesFile(name)
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
                        ok2, text = writeLightingSchemeToFavoritesFile(name)
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
                        env.prefs.restore_defaults(lightingSchemePrefsList)
                        self.win.glpane.gl_update()
                        env.history.message("Cancelled overwriting favorite file.")
                        return
                else:
                    self.favoritesComboBox.addItem(name)
                    _lastItem = self.favoritesComboBox.count()
                    self.favoritesComboBox.setCurrentIndex(_lastItem - 1)
                    msg = "Loaded favorite [%s]." % (name)
                    env.history.message(msg)
                self.win.glpane.gl_update()
        return

    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the Lighting Scheme Property Manager.
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import WhatsThis_LightingScheme_PropertyManager
        WhatsThis_LightingScheme_PropertyManager(self)
        return

    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the Lighting Scheme Property Manager.
        """
        #modify this for lighting schemes
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_LightingScheme_PropertyManager
        ToolTip_LightingScheme_PropertyManager(self)
        return


