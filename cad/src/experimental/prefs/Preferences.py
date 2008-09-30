# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Preferences.py

@author: Mark
@version: $Id: Preferences.py 14197 2008-09-11 04:52:29Z brucesmith $
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:
-Mark 2008-05-20: Created by Mark from a copy of UserPrefs.py
"""

import os, sys

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QDialog
from PyQt4.Qt import QFileDialog
from PyQt4.Qt import QMessageBox
from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QAbstractButton
from PyQt4.Qt import QDoubleValidator
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QPalette
from PyQt4.Qt import QColorDialog
from PyQt4.Qt import QString
from PyQt4.Qt import QFont
from PyQt4.Qt import Qt
from PyQt4.Qt import QWhatsThis
from PyQt4.Qt import QTreeWidget
from PyQt4.Qt import QSize
import string

from PreferencesDialog import PreferencesDialog
import foundation.preferences as preferences
from utilities.debug import print_compact_traceback
from utilities.debug_prefs import debug_pref, Choice_boolean_False
import foundation.env as env
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf
from widgets.widget_helpers import double_fixup
from widgets.prefs_widgets import connect_colorpref_to_colorframe, \
     connect_checkbox_with_boolean_pref, connect_comboBox_with_pref, \
     connect_doubleSpinBox_with_pref, connect_spinBox_with_pref
from utilities import debug_flags
from utilities.constants import str_or_unicode
from platform_dependent.PlatformDependent import screen_pos_size
from platform_dependent.PlatformDependent import get_rootdir
from platform_dependent.Paths import get_default_plugin_path
from utilities.icon_utilities import geticon

from utilities.prefs_constants import displayCompass_prefs_key
from utilities.prefs_constants import displayCompassLabels_prefs_key
from utilities.prefs_constants import displayPOVAxis_prefs_key
from utilities.prefs_constants import displayConfirmationCorner_prefs_key
from utilities.prefs_constants import enableAntiAliasing_prefs_key
from utilities.prefs_constants import animateStandardViews_prefs_key
from utilities.prefs_constants import displayVertRuler_prefs_key
from utilities.prefs_constants import displayHorzRuler_prefs_key
from utilities.prefs_constants import rulerPosition_prefs_key
from utilities.prefs_constants import rulerColor_prefs_key
from utilities.prefs_constants import rulerOpacity_prefs_key
from utilities.prefs_constants import showRulersInPerspectiveView_prefs_key
from utilities.prefs_constants import Adjust_watchRealtimeMinimization_prefs_key
from utilities.prefs_constants import Adjust_minimizationEngine_prefs_key
from utilities.prefs_constants import electrostaticsForDnaDuringAdjust_prefs_key
from utilities.prefs_constants import Adjust_cutoverRMS_prefs_key
from utilities.prefs_constants import qutemol_enabled_prefs_key
from utilities.prefs_constants import qutemol_path_prefs_key
from utilities.prefs_constants import nanohive_enabled_prefs_key
from utilities.prefs_constants import nanohive_path_prefs_key
from utilities.prefs_constants import povray_enabled_prefs_key
from utilities.prefs_constants import povray_path_prefs_key
from utilities.prefs_constants import megapov_enabled_prefs_key
from utilities.prefs_constants import megapov_path_prefs_key
from utilities.prefs_constants import povdir_enabled_prefs_key
from utilities.prefs_constants import gamess_enabled_prefs_key
from utilities.prefs_constants import gmspath_prefs_key
from utilities.prefs_constants import gromacs_enabled_prefs_key
from utilities.prefs_constants import gromacs_path_prefs_key
from utilities.prefs_constants import cpp_enabled_prefs_key
from utilities.prefs_constants import cpp_path_prefs_key
from utilities.prefs_constants import rosetta_enabled_prefs_key
from utilities.prefs_constants import rosetta_path_prefs_key
from utilities.prefs_constants import rosetta_database_enabled_prefs_key
from utilities.prefs_constants import rosetta_dbdir_prefs_key
from utilities.prefs_constants import nv1_enabled_prefs_key
from utilities.prefs_constants import nv1_path_prefs_key
from utilities.prefs_constants import startupGlobalDisplayStyle_prefs_key
from utilities.prefs_constants import buildModeAutobondEnabled_prefs_key
from utilities.prefs_constants import buildModeWaterEnabled_prefs_key
from utilities.prefs_constants import buildModeHighlightingEnabled_prefs_key
from utilities.prefs_constants import buildModeSelectAtomsOfDepositedObjEnabled_prefs_key
from utilities.prefs_constants import light1Color_prefs_key
from utilities.prefs_constants import light2Color_prefs_key
from utilities.prefs_constants import light3Color_prefs_key
from utilities.prefs_constants import atomHighlightColor_prefs_key
from utilities.prefs_constants import bondpointHighlightColor_prefs_key
from utilities.prefs_constants import levelOfDetail_prefs_key
from utilities.prefs_constants import diBALL_AtomRadius_prefs_key
from utilities.prefs_constants import cpkScaleFactor_prefs_key
from utilities.prefs_constants import showBondStretchIndicators_prefs_key
from utilities.prefs_constants import showValenceErrors_prefs_key

#General  page prefs - paste offset scale for chunk and dna pasting prefs key
from utilities.prefs_constants import pasteOffsetScaleFactorForChunks_prefs_key
from utilities.prefs_constants import pasteOffsetScaleFactorForDnaObjects_prefs_key

# Color (page) prefs
from utilities.prefs_constants import backgroundColor_prefs_key
from utilities.prefs_constants import backgroundGradient_prefs_key
from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import haloWidth_prefs_key

# Mouse wheel prefs
from utilities.prefs_constants import mouseWheelDirection_prefs_key
from utilities.prefs_constants import zoomInAboutScreenCenter_prefs_key
from utilities.prefs_constants import zoomOutAboutScreenCenter_prefs_key
from utilities.prefs_constants import mouseWheelTimeoutInterval_prefs_key

# DNA prefs
from utilities.prefs_constants import bdnaBasesPerTurn_prefs_key
from utilities.prefs_constants import bdnaRise_prefs_key
from utilities.prefs_constants import dnaDefaultStrand1Color_prefs_key
from utilities.prefs_constants import dnaDefaultStrand2Color_prefs_key
from utilities.prefs_constants import dnaDefaultSegmentColor_prefs_key
from utilities.prefs_constants import dnaStrutScaleFactor_prefs_key
from utilities.prefs_constants import arrowsOnBackBones_prefs_key
from utilities.prefs_constants import arrowsOnThreePrimeEnds_prefs_key
from utilities.prefs_constants import arrowsOnFivePrimeEnds_prefs_key
from utilities.prefs_constants import useCustomColorForThreePrimeArrowheads_prefs_key
from utilities.prefs_constants import dnaStrandThreePrimeArrowheadsCustomColor_prefs_key
from utilities.prefs_constants import useCustomColorForFivePrimeArrowheads_prefs_key
from utilities.prefs_constants import dnaStrandFivePrimeArrowheadsCustomColor_prefs_key

# DNA Minor Groove Error Indicator prefs
from utilities.prefs_constants import dnaDisplayMinorGrooveErrorIndicators_prefs_key
from utilities.prefs_constants import dnaMinMinorGrooveAngle_prefs_key
from utilities.prefs_constants import dnaMaxMinorGrooveAngle_prefs_key
from utilities.prefs_constants import dnaMinorGrooveErrorIndicatorColor_prefs_key

# DNA style prefs 080310 piotr
from utilities.prefs_constants import dnaStyleStrandsShape_prefs_key
from utilities.prefs_constants import dnaStyleStrandsColor_prefs_key
from utilities.prefs_constants import dnaStyleStrandsScale_prefs_key
from utilities.prefs_constants import dnaStyleStrandsArrows_prefs_key
from utilities.prefs_constants import dnaStyleAxisShape_prefs_key
from utilities.prefs_constants import dnaStyleAxisColor_prefs_key
from utilities.prefs_constants import dnaStyleAxisScale_prefs_key
from utilities.prefs_constants import dnaStyleAxisEndingStyle_prefs_key
from utilities.prefs_constants import dnaStyleStrutsShape_prefs_key
from utilities.prefs_constants import dnaStyleStrutsColor_prefs_key
from utilities.prefs_constants import dnaStyleStrutsScale_prefs_key
from utilities.prefs_constants import dnaStyleBasesShape_prefs_key
from utilities.prefs_constants import dnaStyleBasesColor_prefs_key
from utilities.prefs_constants import dnaStyleBasesScale_prefs_key

# DNA labels and base indicators. 080325 piotr
from utilities.prefs_constants import dnaStrandLabelsEnabled_prefs_key
from utilities.prefs_constants import dnaStrandLabelsColor_prefs_key
from utilities.prefs_constants import dnaStrandLabelsColorMode_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsEnabled_prefs_key
from utilities.prefs_constants import dnaBaseInvIndicatorsEnabled_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsAngle_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsColor_prefs_key
from utilities.prefs_constants import dnaBaseInvIndicatorsColor_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsDistance_prefs_key
from utilities.prefs_constants import dnaStyleBasesDisplayLetters_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsPlaneNormal_prefs_key

# Undo prefs
from utilities.prefs_constants import undoRestoreView_prefs_key
from utilities.prefs_constants import undoAutomaticCheckpoints_prefs_key
from utilities.prefs_constants import undoStackMemoryLimit_prefs_key
from utilities.prefs_constants import historyMsgSerialNumber_prefs_key
from utilities.prefs_constants import historyMsgTimestamp_prefs_key
from utilities.prefs_constants import historyHeight_prefs_key
from utilities.prefs_constants import rememberWinPosSize_prefs_key
from utilities.prefs_constants import captionFullPath_prefs_key
from utilities.prefs_constants import dynamicToolTipAtomChunkInfo_prefs_key
from utilities.prefs_constants import dynamicToolTipAtomMass_prefs_key
from utilities.prefs_constants import dynamicToolTipAtomPosition_prefs_key
from utilities.prefs_constants import dynamicToolTipAtomDistanceDeltas_prefs_key
from utilities.prefs_constants import dynamicToolTipBondLength_prefs_key
from utilities.prefs_constants import dynamicToolTipBondChunkInfo_prefs_key
from utilities.prefs_constants import dynamicToolTipAtomDistancePrecision_prefs_key
from utilities.prefs_constants import captionPrefix_prefs_key
from utilities.prefs_constants import captionSuffix_prefs_key
from utilities.prefs_constants import compassPosition_prefs_key
from utilities.prefs_constants import defaultProjection_prefs_key
from utilities.prefs_constants import displayOriginAsSmallAxis_prefs_key
from utilities.prefs_constants import displayOriginAxis_prefs_key
from utilities.prefs_constants import animateMaximumTime_prefs_key
from utilities.prefs_constants import mouseSpeedDuringRotation_prefs_key
from utilities.prefs_constants import Adjust_endRMS_prefs_key
from utilities.prefs_constants import Adjust_endMax_prefs_key
from utilities.prefs_constants import Adjust_cutoverMax_prefs_key
from utilities.prefs_constants import sponsor_permanent_permission_prefs_key
from utilities.prefs_constants import sponsor_download_permission_prefs_key
from utilities.prefs_constants import bondpointHotspotColor_prefs_key
from utilities.prefs_constants import diBALL_bondcolor_prefs_key
from utilities.prefs_constants import bondHighlightColor_prefs_key
from utilities.prefs_constants import bondStretchColor_prefs_key
from utilities.prefs_constants import bondVaneColor_prefs_key
from utilities.prefs_constants import pibondStyle_prefs_key
from utilities.prefs_constants import pibondLetters_prefs_key
from utilities.prefs_constants import linesDisplayModeThickness_prefs_key
from utilities.prefs_constants import diBALL_BondCylinderRadius_prefs_key
from utilities.prefs_constants import material_specular_highlights_prefs_key
from utilities.prefs_constants import material_specular_shininess_prefs_key
from utilities.prefs_constants import material_specular_brightness_prefs_key
from utilities.prefs_constants import material_specular_finish_prefs_key
from utilities.prefs_constants import povdir_path_prefs_key
from utilities.prefs_constants import dynamicToolTipBendAnglePrecision_prefs_key
from utilities.prefs_constants import dynamicToolTipVdwRadiiInAtomDistance_prefs_key
from utilities.prefs_constants import displayFontPointSize_prefs_key
from utilities.prefs_constants import useSelectedFont_prefs_key
from utilities.prefs_constants import displayFont_prefs_key
from utilities.prefs_constants import keepBondsDuringTransmute_prefs_key
from utilities.prefs_constants import indicateOverlappingAtoms_prefs_key
from utilities.prefs_constants import fogEnabled_prefs_key

# Cursor text prefs.
from utilities.prefs_constants import cursorTextFontSize_prefs_key
from utilities.prefs_constants import cursorTextColor_prefs_key

#global display preferences
from utilities.constants import diDEFAULT ,diTrueCPK, diLINES
from utilities.constants import diBALL, diTUBES, diDNACYLINDER

from utilities.constants import black, white, gray
from widgets.prefs_widgets import connect_doubleSpinBox_with_pref
# =
# Preferences widgets constants. I suggest that these be moved to another
# file (i.e. prefs_constants.py or another file). Discuss with Bruce. -Mark

# Setting some Qt constants just to make things more sane
CHECKED = Qt.Checked
UNCHECKED = Qt.Unchecked

# Widget constants for the "Graphics Area" page.

BG_EVENING_SKY = 0
BG_BLUE_SKY = 1
BG_SEAGREEN = 2
BG_BLACK = 3
BG_WHITE = 4
BG_GRAY = 5
BG_CUSTOM = 6

# GDS = global display style
from PreferencesDialog import GDS_NAMES, GDS_ICONS, GDS_INDEXES

from PreferencesDialog import HIGH_ORDER_BOND_STYLES
   
# Widget constants for the "Colors" page.

# HHS = hover highlighting styles
from utilities.prefs_constants import HHS_HALO
from utilities.prefs_constants import HHS_SOLID
from utilities.prefs_constants import HHS_SCREENDOOR1
from utilities.prefs_constants import HHS_CROSSHATCH1
from utilities.prefs_constants import HHS_BW_PATTERN
from utilities.prefs_constants import HHS_POLYGON_EDGES
from utilities.prefs_constants import HHS_DISABLED
from utilities.prefs_constants import HHS_INDEXES
from utilities.prefs_constants import HHS_OPTIONS

# SS = selection styles
from utilities.prefs_constants import SS_HALO
from utilities.prefs_constants import SS_SOLID
from utilities.prefs_constants import SS_SCREENDOOR1
from utilities.prefs_constants import SS_CROSSHATCH1
from utilities.prefs_constants import SS_BW_PATTERN
from utilities.prefs_constants import SS_POLYGON_EDGES
from utilities.prefs_constants import SS_INDEXES
from utilities.prefs_constants import SS_OPTIONS

# = end of Preferences widgets constants.

debug_sliders = False # Do not commit as True
DEBUG = True # Do not commit as True
CURSOR_TEXT_KEY = True

def debug_povdir_signals():
    return 0 and env.debug()

# This list of mode names correspond to the names listed in the modes combo box.
# [TODO: It needs to be renamed, since "modes" is too generic to search for
#  as a global name, which in theory could referenced from other modules.]
modes = ['SELECTMOLS', 'MODIFY', 'DEPOSIT', 'CRYSTAL', 'EXTRUDE', 'FUSECHUNKS', 'MOVIE']
    ### REVIEW: is this constant still used anywhere?
    # If not, it should be removed.
    # [bruce 080815 question]

def parentless_open_dialog_pref(): #bruce 060710 for Mac A8
    # see if setting this True fixes the Mac-specific bugs in draggability of this dialog, and CPU usage while it's up
    from utilities.debug_prefs import debug_pref, Choice_boolean_False
    return debug_pref("parentless open file dialogs?", Choice_boolean_False,
                      prefs_key = "A8.1 devel/parentless open file dialogs")

parentless_open_dialog_pref()

def get_filename_and_save_in_prefs(parent, prefs_key, caption=''):
    """
    Present user with the Qt file chooser to select a file.
    prefs_key is the key to save the filename in the prefs db
    caption is the string for the dialog caption.
    """
    # see also get_dirname_and_save_in_prefs, which has similar code

    if parentless_open_dialog_pref():
        parent = None

    filename = str_or_unicode(QFileDialog.getOpenFileName(
        parent,
        caption,
        get_rootdir(), # '/' on Mac or Linux, something else on Windows
    ))

    if not filename: # Cancelled.
        return None

    # Save filename in prefs db.
    prefs = preferences.prefs_context()
    prefs[prefs_key] = os.path.normpath(filename)

    return filename

def get_dirname_and_save_in_prefs(parent, prefs_key, caption=''): #bruce 060710 for Mac A8
    """
    Present user with the Qt file chooser to select an existing directory.
    If they do that, and if prefs_key is not null, save its full pathname in
    env.prefs[prefs_key].

    @param prefs_key: the pref_key to save the pathname.
    @type  prefs_key: text

    @param caption: the string for the dialog caption.
    @type  caption: text
    """
    # see also get_filename_and_save_in_prefs, which has similar code

    if parentless_open_dialog_pref():
        parent = None

    filename = str_or_unicode(QFileDialog.getExistingDirectory(
        parent,### if this was None, it might fix the Mac bug where you can't drag the dialog around [bruce 060710]
        caption,
        get_rootdir(), # '/' on Mac or Linux -- maybe not the best choice if they've chosen one before?
    ))

    if not filename: # Cancelled.
        return None

    # Save filename in prefs db.
    prefs = preferences.prefs_context()
    prefs[prefs_key] = filename

    return filename

# main window layout save/restore

def _fullkey(keyprefix, *subkeys): #e this func belongs in preferences.py
    res = keyprefix
    for subkey in subkeys:
        res += "/" + subkey
    return res

def _size_pos_keys( keyprefix):
    return _fullkey(keyprefix, "geometry", "size"), _fullkey(keyprefix, "geometry", "pos")

def _tupleFromQPoint(qpoint):
    return qpoint.x(), qpoint.y()

def _tupleFromQSize(qsize):
    return qsize.width(), qsize.height()

def _get_window_pos_size(win):
    size = _tupleFromQSize( win.size())
    pos = _tupleFromQPoint( win.pos())
    return pos, size

def save_window_pos_size( win, keyprefix): #bruce 050913 removed histmessage arg
    """
    Save the size and position of the given main window, win,
    in the preferences database, using keys based on the given keyprefix,
    which caller ought to reserve for geometry aspects of the main window.
    (#e Someday, maybe save more aspects like dock layout and splitter bar
    positions??)
    """
##    from preferences import prefs_context
##    prefs = prefs_context()
    ksize, kpos = _size_pos_keys( keyprefix)
    pos, size = _get_window_pos_size(win)
    changes = { ksize: size, kpos: pos }
    env.prefs.update( changes) # use update so it only opens/closes dbfile once
    env.history.message("saved window position %r and size %r" % (pos,size))
    return

def load_window_pos_size( win, keyprefix, defaults = None, screen = None): #bruce 050913 removed histmessage arg; 060517 revised
    """
    Load the last-saved size and position of the given main window, win,
    from the preferences database, using keys based on the given keyprefix,
    which caller ought to reserve for geometry aspects of the main window.
    (If no prefs have been stored, return reasonable or given defaults.)
       Then set win's actual position and size (using supplied defaults, and
    limited by supplied screen size, both given as ((pos_x,pos_y),(size_x,size_y)).
    (#e Someday, maybe restore more aspects like dock layout and splitter bar
    positions??)
    """
    if screen is None:
        screen = screen_pos_size()
    ((x0, y0), (w, h)) = screen
    x1 = x0 + w
    y1 = y0 + h

    pos, size = _get_prefs_for_window_pos_size( win, keyprefix, defaults)
    # now use pos and size, within limits set by screen
    px, py = pos
    sx, sy = size
    if sx > w: sx = w
    if sy > h: sy = h
    if px < x0: px = x0
    if py < y0: py = y0
    if px > x1 - sx: px = x1 - sx
    if py > y1 - sy: py = y1 - sy
    env.history.message("restoring last-saved window position %r and size %r" \
                        % ((px, py),(sx, sy)))
    win.resize(sx, sy)
    win.move(px, py)
    return

def _get_prefs_for_window_pos_size( win, keyprefix, defaults = None):
    """
    Load and return the last-saved size and position of the given main window, win,
    from the preferences database, using keys based on the given keyprefix,
    which caller ought to reserve for geometry aspects of the main window.
    (If no prefs have been stored, return reasonable or given defaults.)
    """
    #bruce 060517 split this out of load_window_pos_size
    if defaults is None:
        defaults = _get_window_pos_size(win)
    dpos, dsize = defaults
    px, py = dpos # check correctness of args, even if not used later
    sx, sy = dsize
    import foundation.preferences as preferences
    prefs = preferences.prefs_context()
    ksize, kpos = _size_pos_keys( keyprefix)
    pos = prefs.get(kpos, dpos)
    size = prefs.get(ksize, dsize)
    return pos, size

def get_pref_or_optval(key, val, optval):
    """
    Return <key>'s value. If <val> is equal to <key>'s value, return <optval>
    instead.
    """
    if env.prefs[key] == val:
        return optval
    else:
        return env.prefs[key]

#class Preferences(QDialog, PreferencesDialog):
class Preferences(PreferencesDialog):
    """
    The Preferences dialog used for accessing and changing user
    preferences.
    """
    pagenameList = [] # List of page names in prefsStackedWidget.

#    def __init__(self, assy):
    def __init__(self):
        QDialog.__init__(self)
        super(Preferences, self).__init__()
#        self.setupUi(self)

        # Some important attrs.
 #       self.glpane = assy.o
 #       self.w = assy.w
 #       self.assy = assy
        self.pagenameList = self.getPagenameList()
        if DEBUG:
            print self.pagenameList
        self.changeKey = 0
        # Start of dialog setup.
        #self._setupDialog_TopLevelWidgets()
        self._setupPage_General()
        #self._setupPage_Color()
        self._setupPage_Graphics_Area()
        self._setupPage_Zoom_Pan_and_Rotate()
        self._setupPage_Rulers()
        self._setupPage_Atoms()
        self._setupPage_Bonds()
        self._setupPage_DNA()
        self._setupPage_DNA_Minor_Groove_Error_Indicator()
        self._setupPage_DNA_Base_Orientation_Indicators()
        self._setupPage_Adjust()
        #self._setupPage_Lighting()
        self._setupPage_Plugins()
        self._setupPage_Undo()
        self._setupPage_Window()
        self._setupPage_Reports()
        self._setupPage_Tooltips()

        # Assign "What's This" text for all widgets.
        #from ne1_ui.prefs.WhatsThisText_for_PreferencesDialog import whatsThis_PreferencesDialog
        #whatsThis_PreferencesDialog(self)

        #self._hideOrShowWidgets()
        self.show()
        return
    # End of _init_()


    # PAGE: GENERAL    
    def _setupPage_General(self):
        """
        Setup the General page.
        """
        if env.prefs[sponsor_permanent_permission_prefs_key]:
            if env.prefs[sponsor_download_permission_prefs_key]:
                _myID = 1
            else:
                _myID = 2
        else:
            _myID = 0
        self.logo_download_RadioButtonList.setDefaultCheckedId(_myID)
        _checkedButton = self.logo_download_RadioButtonList.getButtonById(_myID)
        _checkedButton.setChecked(True)

        self.connect(self.logo_download_RadioButtonList.buttonGroup, SIGNAL("buttonClicked(int)"), self.setPrefsLogoDownloadPermissions)

        # Build Atoms option connections.
        connect_checkbox_with_boolean_pref( self.autobondCheckBox, buildModeAutobondEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.hoverHighlightCheckBox, buildModeHighlightingEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.waterCheckBox, buildModeWaterEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.autoSelectAtomsCheckBox, buildModeSelectAtomsOfDepositedObjEnabled_prefs_key )
        
        self.pasteOffsetForChunks_doublespinbox.setValue(\
            env.prefs[pasteOffsetScaleFactorForChunks_prefs_key])

        self.pasteOffsetForDNA_doublespinbox.setValue(
            env.prefs[pasteOffsetScaleFactorForDnaObjects_prefs_key])

        self.connect(self.pasteOffsetForChunks_doublespinbox,
                     SIGNAL("valueChanged(double)"),
                     self.change_pasteOffsetScaleFactorForChunks)
        self.connect(self.pasteOffsetForDNA_doublespinbox,
                     SIGNAL("valueChanged(double)"),
                     self.change_pasteOffsetScaleFactorForDnaObjects)
        return

    def setPrefsLogoDownloadPermissions(self, permission):
        """
        Set the sponsor logos download permissions in the persistent user
        preferences database.

        @param permission: The permission, where:
                        0 = Always ask before downloading
                        1 = Never ask before downloading
                        2 = Never download
        @type  permission: int
        """
        _permanentValue = False
        _downloadValue = True
        if permission == 1:
            _permanentValue = True
            _downloadValue = True

        elif permission == 2:
            _permanentValue = True
            _downloadValue = False

        else:
            _permanentValue = False

        env.prefs[sponsor_permanent_permission_prefs_key] = _permanentValue
        env.prefs[sponsor_download_permission_prefs_key] = _downloadValue
        return

    def setGlobalDisplayStyleAtStartUp(self, junk):
        """
        Slot method for the "Global Display Style at Start-up" combo box in
        the Preferences dialog (and not the combobox in the status bar of
        the main window).

        @param gdsIndexUnused: The current index of the combobox. It is unused.
        @type  gdsIndexUnused: int

        @note: This changes the global display style of the glpane.
        """

        # Get the GDS index from the current combox box index.
        display_style = GDS_INDEXES[self.globalDisplayStyleStartupComboBox.currentIndex()]

        if display_style == env.prefs[startupGlobalDisplayStyle_prefs_key]:
            return

        # set the pref
        env.prefs[startupGlobalDisplayStyle_prefs_key] = display_style

        # Set the current display style in the glpane.
        # (This will be noticed later by chunk.draw of affected chunks.)
#UNCOMMENT LATER
#        self.glpane.setGlobalDisplayStyle(display_style)
#        self.glpane.gl_update()
        return

    # PAGE: GRAPHICS AREA
    def _setupPage_Graphics_Area(self):
        """
        Setup the Graphics Area page
        """
        
        display_style = env.prefs[ startupGlobalDisplayStyle_prefs_key ]
        self.globalDisplayStyleStartupComboBox.setCurrentIndex(GDS_INDEXES.index(display_style))
        self.connect(self.globalDisplayStyleStartupComboBox, SIGNAL("currentIndexChanged(int)"), self.setGlobalDisplayStyleAtStartUp)
        
        # GROUPBOX: Compass display settings
        # Check if the compass is set to display
        if env.prefs[displayCompass_prefs_key]:
            self.display_compass_CheckBox.setCheckState(CHECKED)
        else:
            self.display_compass_CheckBox.setCheckState(UNCHECKED)
        # Call the display_compass function no matter what it know's what to do.
        self.display_compass(env.prefs[displayCompass_prefs_key])
        self.connect(self.display_compass_CheckBox, SIGNAL("toggled(bool)"), self.display_compass)
        connect_comboBox_with_pref(self.compass_location_ComboBox, compassPosition_prefs_key)
        connect_checkbox_with_boolean_pref(self.display_compass_labels_checkbox, displayCompassLabels_prefs_key)
        
        # GROUPBOX: Axes
        connect_checkbox_with_boolean_pref(self.display_origin_axis_checkbox, displayOriginAxis_prefs_key)
        connect_checkbox_with_boolean_pref(self.display_pov_axis_checkbox, displayPOVAxis_prefs_key)
        
        # GROUPBOX: Cursor text settings
        #if CURSOR_TEXT_KEY:
            #self.cursor_text_CheckBox.setCheckState(CHECKED)
        #else:
            #self.cursor_text_CheckBox.setCheckState(UNCHECKED)
        #self.cursor_text_enable_fields(CURSOR_TEXT_KEY)
        connect_doubleSpinBox_with_pref(self.cursor_text_font_size_SpinBox, cursorTextFontSize_prefs_key)
        self.connect(self.cursor_text_reset_Button, SIGNAL("clicked()"), self.reset_cursor_text_font_size)
        self.cursor_text_color_ComboBox.setColor(env.prefs[cursorTextColor_prefs_key], default = True)
        self.connect(self.cursor_text_color_ComboBox, SIGNAL("editingFinished()"), self.set_cursor_text_color)

        # GROUPBOX: Other graphics options groupbox
        connect_checkbox_with_boolean_pref(self.display_confirmation_corner_CheckBox, displayConfirmationCorner_prefs_key)
        connect_checkbox_with_boolean_pref(self.anti_aliasing_CheckBox, enableAntiAliasing_prefs_key)
        return
 
    def reset_cursor_text_font_size(self):
        if not env.prefs.has_default_value(cursorTextFontSize_prefs_key):
            _tmp = env.prefs.get_default_value(cursorTextFontSize_prefs_key)
            self.cursor_text_font_size_SpinBox.setValue(_tmp)
            env.prefs[cursorTextFontSize_prefs_key] = _tmp
        return
    
    def set_cursor_text_color(self):
        _newColor = self.cursor_text_color_ComboBox.getColor()
        env.prefs[cursorTextColor_prefs_key] = _newColor
        return

# Code for dealing with cursor text checkbox (removed)
#    def cursor_text_enable_fields(self, val):
#        return
    
    def display_compass(self, val):
        """
        Slot for the Display Compass checkbox, which enables/disables the
        Display Compass Labels checkbox.
        """
        val = not not val
        # Enable or disable the appropriate things
        self.compass_location_ComboBox.setEnabled(val)
        self.compass_location_ComboBox.labelWidget.setEnabled(val)
        self.display_compass_labels_checkbox.setEnabled(val)
        # If the value is different from the saved value, then save the new one.
        # This method is called at startup, so this could be used simply to
        # set the initial state of the 
        if val != env.prefs[displayCompass_prefs_key]:
            env.prefs[displayCompass_prefs_key] = val
        return
    
    #PAGE: ZOOM, PAN, AND ROTATE
    def _setupPage_Zoom_Pan_and_Rotate(self):
        """
        Setup the Zoom, Pan and Rotate page.
        """
        # GROUPBOX: View rotation settings
        connect_checkbox_with_boolean_pref(self.animate_views_CheckBox, animateStandardViews_prefs_key)
        self.view_animation_speed_Slider.setValue(int (env.prefs[animateMaximumTime_prefs_key] * -100))
        self.mouse_rotation_speed_Slider.setValue(int (env.prefs[mouseSpeedDuringRotation_prefs_key] * 100))
        if env.prefs.has_default_value(animateMaximumTime_prefs_key):
            self.view_animation_speed_reset_ToolButton.setEnabled(False)
        if env.prefs.has_default_value(mouseSpeedDuringRotation_prefs_key):
            self.mouse_rotation_speed_reset_ToolButton.setEnabled(False)
        self.connect(self.view_animation_speed_Slider, SIGNAL("sliderReleased()"), self.set_view_animation_speed)
        self.connect(self.view_animation_speed_reset_ToolButton, SIGNAL("clicked()"), self.reset_view_animation_speed)
        self.connect(self.mouse_rotation_speed_Slider, SIGNAL("sliderReleased()"), self.set_mouse_rotation_speed)
        self.connect(self.mouse_rotation_speed_reset_ToolButton, SIGNAL("clicked()"), self.reset_mouse_rotation_speed)

        # GROUPBOX: Mouse wheel zoom settings
        connect_comboBox_with_pref(self.zoom_directon_ComboBox, mouseWheelDirection_prefs_key)
        connect_comboBox_with_pref(self.zoom_in_center_ComboBox, zoomInAboutScreenCenter_prefs_key)
        connect_comboBox_with_pref(self.zoom_out_center_ComboBox, zoomOutAboutScreenCenter_prefs_key)
        connect_doubleSpinBox_with_pref(self.hover_highlighting_timeout_SpinBox, mouseWheelTimeoutInterval_prefs_key)
        return
    
    def set_view_animation_speed(self):
        env.prefs[animateMaximumTime_prefs_key] = \
           self.view_animation_speed_Slider.value() / -100.0
        self.view_animation_speed_reset_ToolButton.setEnabled(True)
        return
    
    def reset_view_animation_speed(self):
        env.prefs.restore_defaults([animateMaximumTime_prefs_key])
        self.view_animation_speed_Slider.setValue(int (env.prefs[animateMaximumTime_prefs_key] * -100))
        self.view_animation_speed_reset_ToolButton.setEnabled(False)
    
    def set_mouse_rotation_speed(self):
        env.prefs[mouseSpeedDuringRotation_prefs_key] = \
           self.mouse_rotation_speed_Slider.value() / 100.0
        self.mouse_rotation_speed_reset_ToolButton.setEnabled(True)
        return
    
    def reset_mouse_rotation_speed(self):
        env.prefs.restore_defaults([mouseSpeedDuringRotation_prefs_key])
        self.mouse_rotation_speed_Slider.setValue(int (env.prefs[mouseSpeedDuringRotation_prefs_key] * 100))
        self.mouse_rotation_speed_reset_ToolButton.setEnabled(False)

    # PAGE: RULERS
    
    def _setupPage_Rulers(self):
        """
        Setup the "Rulers" page.
        """
        # GROUPBOX: Rulers
        if env.prefs[displayVertRuler_prefs_key] and env.prefs[displayHorzRuler_prefs_key]:
            self.display_rulers_ComboBox.setCurrentIndex(0)
        elif not env.prefs[displayHorzRuler_prefs_key]:
            self.display_rulers_ComboBox.setCurrentIndex(1)
        elif not env.prefs[displayVertRuler_prefs_key]:
            self.display_rulers_ComboBox.setCurrentIndex(2)

        self.connect(self.display_rulers_ComboBox, SIGNAL("currentIndexChanged(int)"), self.set_ruler_display)
        connect_comboBox_with_pref(self.origin_rulers_ComboBox, rulerPosition_prefs_key)
        self.ruler_color_ColorComboBox.setColor(env.prefs[rulerColor_prefs_key], default = True)
        self.connect(self.ruler_color_ColorComboBox, SIGNAL("editingFinished()"), self.set_ruler_color)
        connect_spinBox_with_pref(self.ruler_opacity_SpinBox, rulerOpacity_prefs_key)
        connect_checkbox_with_boolean_pref(self.show_rulers_in_perspective_view_CheckBox,\
                                           showRulersInPerspectiveView_prefs_key)
        return

    def set_ruler_display(self, indx):
        if indx == 0:
            env.prefs[displayVertRuler_prefs_key] = True
            env.prefs[displayHorzRuler_prefs_key] = True
        elif indx == 1:
            env.prefs[displayVertRuler_prefs_key] = True
            env.prefs[displayHorzRuler_prefs_key] = False
        else:
            env.prefs[displayVertRuler_prefs_key] = False
            env.prefs[displayHorzRuler_prefs_key] = True
        return
    
    def set_ruler_color(self):
        _newColor = self.ruler_color_ComboBox.getColor()
        env.prefs[rulerColor_prefs_key] = _newColor
        return

    
    # PAGE: ATOMS ============================================================
    def _setupPage_Atoms(self):
        """
        Setup the "Atoms" page.
        """

        # "Change Element Colors" button.
        self.connect(self.change_element_colors_PushButton, SIGNAL("clicked()"), self.change_element_colors)
        
        # GROUPBOX: Colors sub
        self.atom_highlighting_ColorComboBox.setColor(env.prefs[atomHighlightColor_prefs_key], default = True)
        self.connect(self.atom_highlighting_ColorComboBox, SIGNAL("editingFinished()"), self.set_atom_highlighting_color)
        self.bondpoint_highlighting_ColorComboBox.setColor(env.prefs[bondpointHighlightColor_prefs_key], default = True)
        self.connect(self.bondpoint_highlighting_ColorComboBox, SIGNAL("editingFinished()"), self.set_bondpoint_highlighting_color)
        self.bondpoint_hotspots_ColorComboBox.setColor(env.prefs[bondpointHotspotColor_prefs_key], default = True)
        self.connect(self.bondpoint_hotspots_ColorComboBox, SIGNAL("editingFinished()"), self.set_bondpoint_hotspots_color)
        self.connect(self.restore_element_colors_PushButton, SIGNAL("clicked()"), self.reset_atom_and_bondpoint_colors)
        
        lod = env.prefs[levelOfDetail_prefs_key]
        if lod == -1:
            lod = 3
        self.detail_level_ComboBox.setCurrentIndex(lod)
        self.connect(self.detail_level_ComboBox, SIGNAL("currentIndexChanged(int)"), self.set_level_of_detail)
        self.set_ball_and_stick_atom_scale(env.prefs[diBALL_AtomRadius_prefs_key])
        self.set_CPK_atom_scale(env.prefs[cpkScaleFactor_prefs_key])
        self.ball_and_stick_atom_scale_SpinBox.setValue(round(env.prefs[diBALL_AtomRadius_prefs_key] * 100.0))
        self.CPK_atom_scale_doubleSpinBox.setValue(env.prefs[cpkScaleFactor_prefs_key])
        self.connect(self.ball_and_stick_atom_scale_SpinBox,
                     SIGNAL("valueChanged(int)"),self.set_ball_and_stick_atom_scale)
        self.connect(self.CPK_atom_scale_doubleSpinBox,
                     SIGNAL("valueChanged(double)"),self.set_CPK_atom_scale)
        self.connect(self.ball_and_stick_atom_scale_reset_ToolButton,
                     SIGNAL("clicked()"),self.reset_ball_and_stick_atom_scale)
        self.connect(self.CPK_atom_scale_reset_ToolButton,
                     SIGNAL("clicked()"),self.reset_CPK_atom_scale)
        connect_checkbox_with_boolean_pref(self.overlapping_atom_indicators_CheckBox,
                                           indicateOverlappingAtoms_prefs_key)
        connect_checkbox_with_boolean_pref(self.force_to_keep_bonds_during_transmute_CheckBox,
                                           keepBondsDuringTransmute_prefs_key)
        return

    def set_atom_highlighting_color(self):
        _newColor = self.atom_highlighting_ColorComboBox.getColor()
        env.prefs[atomHighlightColor_prefs_key] = _newColor
        return

    def set_bondpoint_highlighting_color(self):
        _newColor = self.bondpoint_highlighting_ColorComboBox.getColor()
        env.prefs[bondpointHighlightColor_prefs_key] = _newColor
        return

    def set_bondpoint_hotspots_color(self):
        _newColor = self.bondpoint_hotspots_ColorComboBox.getColor()
        env.prefs[bondpointHotspotColor_prefs_key] = _newColor
        return

    def reset_atom_and_bondpoint_colors(self):
        env.prefs.restore_defaults([atomHighlightColor_prefs_key, 
                                    bondpointHighlightColor_prefs_key, 
                                    bondpointHotspotColor_prefs_key])
        self.atom_highlighting_ColorComboBox.setColor(env.prefs.get_default_value(atomHighlightColor_prefs_key))
        self.bondpoint_highlighting_ColorComboBox.setColor(env.prefs.get_default_value(bondpointHighlightColor_prefs_key))
        self.bondpoint_hotspots_ColorComboBox.setColor(env.prefs.get_default_value(bondpointHotspotColor_prefs_key))
        return
    
    def change_element_colors(self):
        """
        Display the Element Color Settings Dialog.
        """
        # Since the prefs dialog is modal, the element color settings dialog must be modal.
        self.w.showElementColorSettings(self)
        return

    def set_level_of_detail(self, level_of_detail_item): #bruce 060215 revised this
        """
        Change the level of detail, where <level_of_detail_item> is a value
        between 0 and 3 where:
            - 0 = low
            - 1 = medium
            - 2 = high
            - 3 = variable (based on number of atoms in the part)

        @note: the prefs db value for 'variable' is -1, to allow for higher LOD
               levels in the future.
        """
        lod = level_of_detail_item
        if level_of_detail_item == 3:
            lod = -1
        env.prefs[levelOfDetail_prefs_key] = lod
#        self.glpane.gl_update()
        # the redraw this causes will (as of tonight) always recompute the correct drawLevel (in Part._recompute_drawLevel),
        # and chunks will invalidate their display lists as needed to accomodate the change. [bruce 060215]
        return

    def set_ball_and_stick_atom_scale(self, value):
        if env.prefs[diBALL_AtomRadius_prefs_key] != value:
            env.prefs[diBALL_AtomRadius_prefs_key] = round(float(value) / 100.0, 2)
        if env.prefs.has_default_value(diBALL_AtomRadius_prefs_key):
            self.ball_and_stick_atom_scale_reset_ToolButton.setEnabled(False)
        else:
            self.ball_and_stick_atom_scale_reset_ToolButton.setEnabled(True)
        return
    
    def set_CPK_atom_scale(self, value):
        if env.prefs[cpkScaleFactor_prefs_key] != value:
            env.prefs[cpkScaleFactor_prefs_key] = value
        # direct comparison with has_default_value didn't work on this level
        # of precision
        if round(env.prefs.get_default_value(cpkScaleFactor_prefs_key), 3 ) \
           == round(value, 3):
            self.CPK_atom_scale_reset_ToolButton.setEnabled(False)
        else:
            self.CPK_atom_scale_reset_ToolButton.setEnabled(True)
        return
    
    def reset_ball_and_stick_atom_scale(self):
        _resetValue = env.prefs.get_default_value(diBALL_AtomRadius_prefs_key)
        _resetValue = int((_resetValue + .005) * 100)
        self.set_ball_and_stick_atom_scale(_resetValue)
        self.ball_and_stick_atom_scale_SpinBox.setValue(_resetValue, 
                                                              blockSignals = True)
        return

    def reset_CPK_atom_scale(self):
        _resetValue = env.prefs.get_default_value(cpkScaleFactor_prefs_key)
        self.set_CPK_atom_scale(_resetValue)
        self.CPK_atom_scale_doubleSpinBox.setValue(_resetValue,
                                                   blockSignals = True)
        return
    
    # PAGE: BONDS ============================================================
    
    def _setupPage_Bonds(self):
        """
        Setup the "Bonds" page.
        """
        # GROUPBOX Colors
        self.bond_highlighting_ColorComboBox.setColor(env.prefs[bondHighlightColor_prefs_key])
        self.connect(self.bond_highlighting_ColorComboBox, SIGNAL("editingFinished()"), self.set_bond_highlighting_color)
        self.ball_and_stick_cylinder_ColorComboBox.setColor(env.prefs[diBALL_bondcolor_prefs_key])
        self.connect(self.ball_and_stick_cylinder_ColorComboBox, SIGNAL("editingFinished()"), self.set_ball_and_stick_cylinder_color)
        self.bond_stretch_ColorComboBox.setColor(env.prefs[bondStretchColor_prefs_key])
        self.connect(self.bond_stretch_ColorComboBox, SIGNAL("editingFinished()"), self.set_bond_stretch_color)
        self.vane_ribbon_ColorComboBox.setColor(env.prefs[bondVaneColor_prefs_key])
        self.connect(self.vane_ribbon_ColorComboBox, SIGNAL("editingFinished()"), self.set_vane_ribbon_color)
        self.connect(self.restore_bond_colors_PushButton, SIGNAL("clicked()"), self.reset_default_colors)
        # GROUPBOX Miscellaneous bond settings
        self.set_ball_and_stick_bond_scale(env.prefs[diBALL_BondCylinderRadius_prefs_key] * 100)
        self.set_bond_line_thickness(env.prefs[linesDisplayModeThickness_prefs_key])
        self.ball_and_stick_bond_scale_SpinBox.setValue(round(env.prefs[diBALL_BondCylinderRadius_prefs_key] * 100))
        self.bond_line_thickness_SpinBox.setValue(env.prefs[linesDisplayModeThickness_prefs_key])
        self.connect(self.ball_and_stick_bond_scale_SpinBox,
                     SIGNAL("valueChanged(int)"),self.set_ball_and_stick_bond_scale)
        self.connect(self.bond_line_thickness_SpinBox,
                     SIGNAL("valueChanged(int)"),self.set_bond_line_thickness)
        # GROUPBOX: High order bonds
        if env.prefs[pibondStyle_prefs_key] == "multicyl":
            _myID = 0
        elif env.prefs[pibondStyle_prefs_key] == "vane":
            _myID = 1
        else:
            _myID = 2
        _checkedButton = self.high_order_bonds_RadioButtonList.getButtonById(_myID)
        _checkedButton.setChecked(True)
        self.connect(self.high_order_bonds_RadioButtonList.buttonGroup, SIGNAL("buttonClicked(int)"), self.set_high_order_bonds)
        connect_checkbox_with_boolean_pref(self.show_bond_type_letters_CheckBox, pibondLetters_prefs_key)
        connect_checkbox_with_boolean_pref(self.show_valence_errors_CheckBox, showValenceErrors_prefs_key)
        connect_checkbox_with_boolean_pref(self.show_bond_stretch_indicators_CheckBox, showBondStretchIndicators_prefs_key)
        return

    def set_bond_highlighting_color(self):
        _newColor = self.bond_highlighting_ColorComboBox.getColor()
        env.prefs[bondHighlightColor_prefs_key] = _newColor
        return
    
    def set_ball_and_stick_cylinder_color(self):
        _newColor = self.ball_and_stick_cylinder_ColorComboBox.getColor()
        env.prefs[diBALL_bondcolor_prefs_key] = _newColor
        return
    
    def set_bond_stretch_color(self):
        _newColor = self.bond_stretch_ColorComboBox.getColor()
        env.prefs[bondStretchColor_prefs_key] = _newColor
        return
    
    def set_vane_ribbon_color(self):
        _newColor = self.vane_ribbon_ColorComboBox.getColor()
        env.prefs[bondVaneColor_prefs_key] = _newColor
        return

    def reset_default_colors(self):
        env.prefs.restore_defaults([bondHighlightColor_prefs_key,
                                    bondStretchColor_prefs_key,
                                    bondVaneColor_prefs_key,
                                    diBALL_bondcolor_prefs_key])
        self.bond_highlighting_ColorComboBox.setColor(env.prefs.get_default_value(bondHighlightColor_prefs_key))
        self.ball_and_stick_cylinder_ColorComboBox.setColor(env.prefs.get_default_value(diBALL_bondcolor_prefs_key))
        self.bond_stretch_ColorComboBox.setColor(env.prefs.get_default_value(bondStretchColor_prefs_key))
        self.vane_ribbon_ColorComboBox.setColor(env.prefs.get_default_value(bondVaneColor_prefs_key))
        return
    
    def set_ball_and_stick_bond_scale(self, value):
        if env.prefs[diBALL_BondCylinderRadius_prefs_key] != value:
            env.prefs[diBALL_BondCylinderRadius_prefs_key] = round(float(value) / 100.0, 2)
        #if env.prefs.has_default_value(diBALL_BondCylinderRadius_prefs_key):
            #self.ball_and_stick_atom_scale_reset_ToolButton.setEnabled(False)
        #else:
            #self.ball_and_stick_atom_scale_reset_ToolButton.setEnabled(True)
        return

    def set_bond_line_thickness(self, value):
        if env.prefs[linesDisplayModeThickness_prefs_key] != value:
            env.prefs[linesDisplayModeThickness_prefs_key] = value
        #if env.prefs.has_default_value(linesDisplayModeThickness_prefs_key):
            #self.ball_and_stick_atom_scale_reset_ToolButton.setEnabled(False)
        #else:
            #self.ball_and_stick_atom_scale_reset_ToolButton.setEnabled(True)
        return
    
    def set_high_order_bonds(self, value):
        env.prefs[pibondStyle_prefs_key] = HIGH_ORDER_BOND_STYLES[value][3]
        return

    # PAGE: DNA ==============================================================
    def _setupPage_DNA(self):
        """
        Setup the "DNA" page.
        """
        # GROUPBOX: DNA default values
        # Uncomment next line when a DB Pref is made for it.
        #connect_comboBox_with_pref(self.conformation_ComboBox, <SOME_VALUE>)
        
        connect_doubleSpinBox_with_pref(self.bases_per_turn_DoubleSpinBox,
                                        bdnaBasesPerTurn_prefs_key)
        connect_doubleSpinBox_with_pref(self.rise_DoubleSpinBox, bdnaRise_prefs_key)
        self.strand1_ColorComboBox.setColor(env.prefs[dnaDefaultStrand1Color_prefs_key])
        self.connect(self.strand1_ColorComboBox, SIGNAL("editingFinished()"), self.set_strand1_color)
        self.strand2_ColorComboBox.setColor(env.prefs[dnaDefaultStrand2Color_prefs_key])
        self.connect(self.strand1_ColorComboBox, SIGNAL("editingFinished()"), self.set_strand2_color)
        self.segment_ColorComboBox.setColor(env.prefs[dnaDefaultSegmentColor_prefs_key])
        self.connect(self.segment_ColorComboBox, SIGNAL("editingFinished()"), self.set_segment_color)
        self.connect(self.restore_DNA_colors_PushButton, SIGNAL("clicked()"), self.reset_DNA_colors)
        # GROUPBOX: Strand arrowhead display options
        connect_checkbox_with_boolean_pref(self.show_arrows_on_backbones_CheckBox,
                                           arrowsOnBackBones_prefs_key)
        connect_checkbox_with_boolean_pref(self.show_arrows_on_3prime_ends_CheckBox,
                                           arrowsOnThreePrimeEnds_prefs_key)
        connect_checkbox_with_boolean_pref(self.show_arrows_on_5prime_ends_CheckBox,
                                           arrowsOnFivePrimeEnds_prefs_key)
        self.three_prime_end_custom_ColorComboBox.setColor(env.prefs[dnaStrandThreePrimeArrowheadsCustomColor_prefs_key])
        self.connect(self.three_prime_end_custom_ColorComboBox, SIGNAL("editingFinished()"), self.set_three_prime_end_color)
        self.five_prime_end_custom_ColorComboBox.setColor(env.prefs[dnaStrandFivePrimeArrowheadsCustomColor_prefs_key])
        self.connect(self.five_prime_end_custom_ColorComboBox, SIGNAL("editingFinished()"), self.set_five_prime_end_color)
        return
    
    def set_strand1_color(self):
        _newColor = self.strand1_ColorComboBox.getColor()
        env.prefs[dnaDefaultStrand1Color_prefs_key] = _newColor
        return
    
    def set_strand2_color(self):
        _newColor = self.strand2_ColorComboBox.getColor()
        env.prefs[dnaDefaultStrand2Color_prefs_key] = _newColor
        return
    
    def set_segment_color(self):
        _newColor = self.segment_ColorComboBox.getColor()
        env.prefs[dnaDefaultSegmentColor_prefs_key] = _newColor
        return

    def reset_DNA_colors(self):
        env.prefs.restore_defaults([dnaDefaultStrand1Color_prefs_key,
                                    dnaDefaultStrand2Color_prefs_key,
                                    dnaDefaultSegmentColor_prefs_key])
        self.strand1_ColorComboBox.setColor(env.prefs.get_default_value(dnaDefaultStrand1Color_prefs_key))
        self.strand2_ColorComboBox.setColor(env.prefs.get_default_value(dnaDefaultStrand2Color_prefs_key))
        self.segment_ColorComboBox.setColor(env.prefs.get_default_value(dnaDefaultSegmentColor_prefs_key))
        return

    def set_three_prime_end_color(self):
        _newColor = self.three_prime_end_custom_ColorComboBox.getColor()
        env.prefs[dnaStrandThreePrimeArrowheadsCustomColor_prefs_key] = _newColor
        return
    
    def set_five_prime_end_color(self):
        _newColor = self.five_prime_end_custom_ColorComboBox.getColor()
        env.prefs[dnaStrandFivePrimeArrowheadsCustomColor_prefs_key] = _newColor
        return
    
    # PAGE: DNA MINOR GROOVE ERROR INDICATOR
    def _setupPage_DNA_Minor_Groove_Error_Indicator(self):
        """
        Setup the "DNA Minor_Groove Error Indicator" page.
        """
        self.set_DNA_minor_groove_error_indicator_status()
        self.connect(self.minor_groove_error_indicatiors_CheckBox, 
                     SIGNAL("toggled(bool)"), 
                     self.set_DNA_minor_groove_error_indicator_status)
        connect_spinBox_with_pref(self.minor_groove_error_minimum_angle_SpinBox,
                                  dnaMinMinorGrooveAngle_prefs_key)
        connect_spinBox_with_pref(self.minor_groove_error_maximum_angle_SpinBox,
                                  dnaMaxMinorGrooveAngle_prefs_key)
        self.minor_groove_error_color_ColorComboBox.setColor(env.prefs[dnaMinorGrooveErrorIndicatorColor_prefs_key])
        self.connect(self.minor_groove_error_color_ColorComboBox, 
                     SIGNAL("editingFinished()"), 
                     self.set_minor_groove_error_color)
        self.connect(self.minor_groove_error_reset_PushButton, 
                     SIGNAL("clicked()"),
                     self.reset_minor_groove_error_prefs)
        return
    
    def set_DNA_minor_groove_error_indicator_status(self, status = None):
        if (status == None and env.prefs[dnaDisplayMinorGrooveErrorIndicators_prefs_key]) \
           or status:
            self.minor_groove_error_parameters_GroupBox.setEnabled(True)
            self.minor_groove_error_indicatiors_CheckBox.setCheckState(CHECKED)
            env.prefs[dnaDisplayMinorGrooveErrorIndicators_prefs_key] = True
        else:
            self.minor_groove_error_parameters_GroupBox.setEnabled(False)
            self.minor_groove_error_indicatiors_CheckBox.setCheckState(UNCHECKED)
            env.prefs[dnaDisplayMinorGrooveErrorIndicators_prefs_key] = False
        return

    def set_minor_groove_error_color(self):
        _newColor = self.minor_groove_error_color_ColorComboBox.getColor()
        env.prefs[dnaMinorGrooveErrorIndicatorColor_prefs_key] = _newColor
        return
    
    def reset_minor_groove_error_prefs(self):
        self.minor_groove_error_color_ColorComboBox.setColor(env.prefs.get_default_value(dnaMinorGrooveErrorIndicatorColor_prefs_key))
        self.minor_groove_error_minimum_angle_SpinBox.setValue(env.prefs.get_default_value(dnaMinMinorGrooveAngle_prefs_key))
        self.minor_groove_error_maximum_angle_SpinBox.setValue(env.prefs.get_default_value(dnaMaxMinorGrooveAngle_prefs_key))
        env.prefs.restore_defaults([dnaMinorGrooveErrorIndicatorColor_prefs_key,
                                    dnaMinMinorGrooveAngle_prefs_key,
                                    dnaMaxMinorGrooveAngle_prefs_key])
        return

    # PAGE: DNA BASE ORIENTATION INDICATORS
    def _setupPage_DNA_Base_Orientation_Indicators(self):
        self.set_DNA_base_orientation_indicator_status()
        self.connect(self.base_orientation_indicatiors_CheckBox, 
                     SIGNAL("toggled(bool)"), 
                     self.set_DNA_base_orientation_indicator_status)
        connect_comboBox_with_pref(self.plane_normal_ComboBox,
                                   dnaBaseIndicatorsPlaneNormal_prefs_key)
        self.indicators_color_ColorComboBox.setColor(env.prefs[dnaBaseIndicatorsColor_prefs_key])
        self.connect(self.indicators_color_ColorComboBox, 
                     SIGNAL("editingFinished()"), 
                     self.set_indicators_color)
        self.inverse_indicators_color_ColorComboBox.setColor(env.prefs[dnaBaseInvIndicatorsColor_prefs_key])
        self.connect(self.inverse_indicators_color_ColorComboBox, 
                     SIGNAL("editingFinished()"), 
                     self.set_inverse_indicators_color)
        connect_checkbox_with_boolean_pref(self.enable_inverse_indicatiors_CheckBox,
                                           dnaBaseInvIndicatorsEnabled_prefs_key)
        connect_doubleSpinBox_with_pref(self.angle_threshold_DoubleSpinBox,
                                        dnaBaseIndicatorsAngle_prefs_key)
        connect_spinBox_with_pref(self.terminal_base_distance_SpinBox,
                                  dnaBaseIndicatorsDistance_prefs_key)
        return
    
    def set_DNA_base_orientation_indicator_status(self, status = None):
        if (status == None and env.prefs[dnaBaseIndicatorsEnabled_prefs_key]) \
           or status:
            self.base_orientation_GroupBox.setEnabled(True)
            self.base_orientation_indicatiors_CheckBox.setCheckState(CHECKED)
            env.prefs[dnaBaseIndicatorsEnabled_prefs_key] = True
        else:
            self.base_orientation_GroupBox.setEnabled(False)
            self.base_orientation_indicatiors_CheckBox.setCheckState(UNCHECKED)
            env.prefs[dnaBaseIndicatorsEnabled_prefs_key] = False
        return
    
    def set_indicators_color(self):
        _newColor = self.indicators_color_ColorComboBox.getColor()
        env.prefs[dnaBaseIndicatorsColor_prefs_key] = _newColor
        return

    def set_inverse_indicators_color(self):
        _newColor = self.inverse_indicators_color_ColorComboBox.getColor()
        env.prefs[dnaBaseInvIndicatorsColor_prefs_key] = _newColor
        return
    
    # PAGE: ADJUST
    def _setupPage_Adjust(self):
        """
        Setup the "Adjust" page.
        """
        connect_comboBox_with_pref(self.physics_engine_choice_ComboBox,
                                   Adjust_minimizationEngine_prefs_key)
        connect_checkbox_with_boolean_pref(self.enable_electrostatics_CheckBox,
            electrostaticsForDnaDuringAdjust_prefs_key)
        connect_checkbox_with_boolean_pref(
            self.watch_motion_in_realtime_CheckBox,
            Adjust_watchRealtimeMinimization_prefs_key)
        connect_doubleSpinBox_with_pref(self.endRMS_DoubleSpinBox,
                                        Adjust_endRMS_prefs_key)
        connect_doubleSpinBox_with_pref(self.endmax_DoubleSpinBox,
                                        Adjust_endMax_prefs_key)
        connect_doubleSpinBox_with_pref(self.cutoverRMS_DoubleSpinBox,
                                        Adjust_cutoverRMS_prefs_key)
        connect_doubleSpinBox_with_pref(self.cutoverMax_DoubleSpinBox,
                                        Adjust_cutoverMax_prefs_key)
        self.endRMS_DoubleSpinBox.setSpecialValueText("Automatic")
        self.endmax_DoubleSpinBox.setSpecialValueText("Automatic")
        self.cutoverRMS_DoubleSpinBox.setSpecialValueText("Automatic")
        self.cutoverMax_DoubleSpinBox.setSpecialValueText("Automatic")
        return
    
    # PAGE: PLUGINS ==========================================================
    def _setupPage_Plugins(self):
        """
        Setup the "Plug-ins" page.
        """
        pluginList = [ "QuteMolX", \
                       "POV-Ray", \
                       "MegaPOV", \
                       "POV include dir", \
                       "GROMACS", \
                       "cpp",
                       "Rosetta",
                       "Rosetta DB"]

        # signal-slot connections.
        for name in pluginList:
            _pluginFunctionName = "".join([ x for x in name.lower().replace(" ","_") \
                                              if (x in string.ascii_letters or\
                                                  x in string.digits \
                                                  or x == "_") ])
            _fname = "enable_%s" % _pluginFunctionName
            if hasattr(self, _fname):
                fcall = getattr(self, _fname)
                if callable(fcall):
                    if DEBUG:
                        print "method defined: %s" % _fname
                    self.connect(self.checkboxes[name], \
                                                 SIGNAL("toggled(bool)"), \
                                                 fcall)
                else:
                    print "Attribute %s exists, but is not a callable method."
            else:
                if DEBUG:
                    print "method missing: %s" % _fname
            #_fname = "set_%s_path" % _pluginFunctionName
            #if hasattr(self, _fname):
                #fcall = getattr(self, _fname)
                #if callable(fcall):
                    #if DEBUG:
                        #print "method defined: %s" % _fname
                    #self.connect(self.choosers[name].lineEdit,\
                                               #SIGNAL("edtingFinished()"), \
                                               #fcall)
                #else:
                    #print "Attribute %s exists, but is not a callable method."
            #else:
                #if DEBUG:
                    #print "method missing: %s" % _fname

        self.connect( self.choosers["QuteMolX"].lineEdit, SIGNAL("editingFinished()"), self.set_qutemolx_path)
        self.connect( self.choosers["POV-Ray"].lineEdit, SIGNAL("editingFinished()"), self.set_povray_path)
        self.connect( self.choosers["MegaPOV"].lineEdit, SIGNAL("editingFinished()"), self.set_megapov_path)
        self.connect( self.choosers["POV include dir"].lineEdit, SIGNAL("editingFinished()"), self.set_pov_include_dir)
        self.connect( self.choosers["GROMACS"].lineEdit, SIGNAL("editingFinished()"), self.set_gromacs_path)
        self.connect( self.choosers["cpp"].lineEdit, SIGNAL("editingFinished()"), self.set_cpp_path)
        self.connect( self.choosers["Rosetta"].lineEdit, SIGNAL("editingFinished()"), self.set_rosetta_path)
        self.connect( self.choosers["Rosetta DB"].lineEdit, SIGNAL("editingFinished()"), self.set_rosetta_db_path)
        return


    def _hideOrShowWidgets(self):
        """
        Permanently hides some widgets in the Preferences dialog.
        This provides an easy and convenient way of hiding widgets that have
        been added but not fully implemented. It is also possible to
        show hidden widgets that have a debug pref set to enable them.
        """
        gms_and_esp_widgetList = [self.nanohive_lbl,
                                  self.nanohive_checkbox,
                                  self.nanohive_path_lineedit,
                                  self.nanohive_choose_btn,
                                  self.gamess_checkbox,
                                  self.gamess_lbl,
                                  self.gamess_path_lineedit,
                                  self.gamess_choose_btn]
        
        for widget in gms_and_esp_widgetList:
            if debug_pref("Show GAMESS and ESP Image UI options",
                          Choice_boolean_False,
                          prefs_key = True):
                widget.show()
            else:
                widget.hide()
        
        # NanoVision-1 
        nv1_widgetList = [self.nv1_checkbox,
                          self.nv1_label,
                          self.nv1_path_lineedit,
                          self.nv1_choose_btn]
        
        for widget in nv1_widgetList:
            widget.hide()
        
        # Rosetta 
        rosetta_widgetList = [self.rosetta_checkbox,
                              self.rosetta_label,
                              self.rosetta_path_lineedit,
                              self.rosetta_choose_btn,
                              self.rosetta_db_checkbox,
                              self.rosetta_db_label,
                              self.rosetta_db_path_lineedit,
                              self.rosetta_db_choose_btn]

        from utilities.GlobalPreferences import ENABLE_PROTEINS
        for widget in rosetta_widgetList:
            if ENABLE_PROTEINS:
                widget.show()
            else:
                widget.hide()
        return


    ########## Slot methods for "Plug-ins" page widgets ################

    # GROMACS slots #######################################

    def set_gromacs_path(self):
        """
        Slot for GROMACS path line editor.
        """
        setPath = str_or_unicode(self.choosers["GROMACS"].text)
        env.prefs[gromacs_path_prefs_key] = setPath
        prefs = preferences.prefs_context()
        prefs[gromacs_path_prefs_key] = setPath
        return setPath

    def enable_gromacs(self, enable = True):
        """
        If True, GROMACS path is set in Preferences>Plug-ins

        @param enable: Is the path set?
        @type  enable: bool
        """

        state = self.checkboxes["GROMACS"].checkState()
        if enable:
            if (state != Qt.Checked):
                self.checkboxes["GROMACS"].setCheckState(Qt.Checked)
            self.choosers["GROMACS"].setEnabled(True)
            env.prefs[gromacs_enabled_prefs_key] = True

            # Sets the GROMACS (executable) path to the standard location, if it exists.
            if not env.prefs[gromacs_path_prefs_key]:
                env.prefs[gromacs_path_prefs_key] = get_default_plugin_path( \
                    "C:\\GROMACS_3.3.3\\bin\\mdrun.exe", \
                    "/Applications/GROMACS_3.3.3/bin/mdrun",
                    "/usr/local/GROMCAS_3.3.3/bin/mdrun")

            self.choosers["GROMACS"].setText(env.prefs[gromacs_path_prefs_key])

        else:
            if (state != Qt.Unchecked):
                self.checkboxes["GROMACS"].setCheckState(Qt.Unchecked)
            self.choosers["GROMACS"].setEnabled(False)
            #self.gromacs_path_lineedit.setText("")
            #env.prefs[gromacs_path_prefs_key] = ''
            env.prefs[gromacs_enabled_prefs_key] = False

    # cpp slots #######################################

    def set_cpp_path(self):
        """
        Slot for cpp path line editor.
        """
        setPath = str_or_unicode(self.choosers["cpp"].text)
        env.prefs[cpp_path_prefs_key] = setPath
        prefs = preferences.prefs_context()
        prefs[cpp_path_prefs_key] = setPath
        return setPath

    def enable_cpp(self, enable = True):
        """
        Enables/disables cpp plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        state = self.checkboxes["cpp"].checkState()
        if enable:
            if (state != Qt.Checked):
                self.checkboxes["cpp"].setCheckState(Qt.Checked)
            self.choosers["cpp"].setEnabled(True)
            env.prefs[cpp_enabled_prefs_key] = True

            # Sets the cpp path to the standard location, if it exists.
            if not env.prefs[cpp_path_prefs_key]:
                env.prefs[cpp_path_prefs_key] = get_default_plugin_path( \
                    "C:\\GROMACS_3.3.3\\MCPP\\bin\\mcpp.exe", \
                    "/Applications/GROMACS_3.3.3/mcpp/bin/mcpp", \
                    "/usr/local/GROMACS_3.3.3/mcpp/bin/mcpp")

            self.choosers["cpp"].setText(env.prefs[cpp_path_prefs_key])

        else:
            if (state != Qt.Unchecked):
                self.checkboxes["cpp"].setCheckState(Qt.Unchecked)
            self.choosers["cpp"].setEnabled(False)
            #self.cpp_path_lineedit.setText("")
            #env.prefs[cpp_path_prefs_key] = ''
            env.prefs[cpp_enabled_prefs_key] = False

    
    # Rosetta slots #######################################

    def set_rosetta_path(self):
        """
        Slot for Rosetta path line editor.
        """
        setPath = str_or_unicode(self.choosers["Rosetta"].text)
        env.prefs[rosetta_path_prefs_key] = setPath
        prefs = preferences.prefs_context()
        prefs[rosetta_path_prefs_key] = setPath
        return setPath

    def enable_rosetta(self, enable = True):
        """
        If True, rosetta path is set in Preferences > Plug-ins

        @param enable: Is the path set?
        @type  enable: bool
        """

        state = self.checkboxes["Rosetta"].checkState()
        if enable:
            if (state != Qt.Checked):
                self.checkboxes["Rosetta"].setCheckState(Qt.Checked)
            self.choosers["Rosetta"].setEnabled(True)
            env.prefs[rosetta_enabled_prefs_key] = True

            # Sets the rosetta (executable) path to the standard location, if it exists.
            if not env.prefs[rosetta_path_prefs_key]:
                env.prefs[rosetta_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Rosetta\\rosetta.exe", \
                    "/Users/marksims/Nanorex/Rosetta/rosetta++/rosetta.mactel", \
                    "/usr/local/Rosetta/Rosetta")

            self.choosers["Rosetta"].setText(env.prefs[rosetta_path_prefs_key])

        else:
            if (state != Qt.Unchecked):
                self.checkboxes["Rosetta"].setCheckState(Qt.Unchecked)
            self.choosers["Rosetta"].setEnabled(False)
            env.prefs[rosetta_enabled_prefs_key] = False
        return
    
    # Rosetta DB slots #######################################
    
    def set_rosetta_db_path(self):
        """
        Slot for Rosetta db path line editor.
        """
        setPath = str_or_unicode(self.choosers["Rosetta DB"].text)
        env.prefs[rosetta_dbdir_prefs_key] = setPath
        prefs = preferences.prefs_context()
        prefs[rosetta_dbdir_prefs_key] = setPath
        return setPath

    def enable_rosetta_db(self, enable = True):
        """
        If True, rosetta db path is set in Preferences > Plug-ins

        @param enable: Is the path set?
        @type  enable: bool
        """

        state = self.checkboxes["Rosetta DB"].checkState()
        if enable:
            if (state != Qt.Checked):
                self.checkboxes["Rosetta DB"].setCheckState(Qt.Checked)
            self.choosers["Rosetta DB"].setEnabled(True)
            env.prefs[rosetta_database_enabled_prefs_key] = True

            # Sets the rosetta (executable) path to the standard location, if it exists.
            if not env.prefs[rosetta_dbdir_prefs_key]:
                env.prefs[rosetta_dbdir_prefs_key] = get_default_plugin_path( \
                    "C:\\Rosetta\\rosetta_database", \
                    "/Users/marksims/Nanorex/Rosetta/Rosetta_database", \
                    "/usr/local/Rosetta/Rosetta_database")

            self.choosers["Rosetta DB"].setText(env.prefs[rosetta_dbdir_prefs_key])

        else:
            if (state != Qt.Unchecked):
                self.checkboxes["Rosetta DB"].setCheckState(Qt.Unchecked)
            self.choosers["Rosetta DB"].setEnabled(False)
            env.prefs[rosetta_database_enabled_prefs_key] = False
        return

    # QuteMolX slots #######################################

    def set_qutemolx_path(self):
        """
        Slot for QuteMolX path "Choose" button.
        """
        setPath = str_or_unicode(self.choosers["QuteMolX"].text)
        env.prefs[qutemol_path_prefs_key] = setPath
        prefs = preferences.prefs_context()
        prefs[qutemol_path_prefs_key] = setPath

        return setPath

    def enable_qutemolx(self, enable = True):
        """
        Enables/disables QuteMolX plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        if enable:
            self.choosers["QuteMolX"].setEnabled(1)
            env.prefs[qutemol_enabled_prefs_key] = True

            # Sets the QuteMolX (executable) path to the standard location, if it exists.
            if not env.prefs[qutemol_path_prefs_key]:
                env.prefs[qutemol_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\Nanorex\\QuteMolX\\QuteMolX.exe", \
                    "/Applications/Nanorex/QuteMolX 0.5.0/QuteMolX.app", \
                    "/usr/local/Nanorex/QuteMolX 0.5.0/QuteMolX")

            self.choosers["QuteMolX"].setText(env.prefs[qutemol_path_prefs_key])

        else:
            self.choosers["QuteMolX"].setEnabled(0)
            #env.prefs[qutemol_path_prefs_key] = ''
            env.prefs[qutemol_enabled_prefs_key] = False

    # POV-Ray slots #####################################

    def set_povray_path(self):
        """
        Slot for POV-Ray path line editor.
        """
        setPath = str_or_unicode(self.choosers["POV-Ray"].text)
        env.prefs[povray_path_prefs_key] = setPath
        prefs = preferences.prefs_context()
        prefs[povray_path_prefs_key] = setPath
        return setPath

    def enable_povray(self, enable = True):
        """
        Enables/disables POV-Ray plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        if enable:
            self.choosers["POV-Ray"].setEnabled(1)
            env.prefs[povray_enabled_prefs_key] = True

            # Sets the POV-Ray (executable) path to the standard location, if it exists.
            if not env.prefs[povray_path_prefs_key]:
                env.prefs[povray_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\POV-Ray for Windows v3.6\\bin\\pvengine.exe", \
                    "/usr/local/bin/pvengine", \
                    "/usr/local/bin/pvengine")

            self.choosers["POV-Ray"].setText(env.prefs[povray_path_prefs_key])

        else:
            self.choosers["POV-Ray"].setEnabled(0)
            #self.povray_path_lineedit.setText("")
            #env.prefs[povray_path_prefs_key] = ''
            env.prefs[povray_enabled_prefs_key] = False
        self._update_povdir_enables() #bruce 060710

    # MegaPOV slots #####################################

    def set_megapov_path(self):
        """
        Slot for MegaPOV path line editor.
        """
        setPath = str_or_unicode(self.choosers["MegaPOV"].text)
        env.prefs[megapov_path_prefs_key] = setPath
        prefs = preferences.prefs_context()
        prefs[megapov_path_prefs_key] = setPath
        return setPath

    def enable_megapov(self, enable = True):
        """
        Enables/disables MegaPOV plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        if enable:
            self.choosers["MegaPOV"].setEnabled(1)
            env.prefs[megapov_enabled_prefs_key] = True

            # Sets the MegaPOV (executable) path to the standard location, if it exists.
            if not env.prefs[megapov_path_prefs_key]:
                env.prefs[megapov_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\POV-Ray for Windows v3.6\\bin\\megapov.exe", \
                    "/usr/local/bin/megapov", \
                    "/usr/local/bin/megapov")

            self.choosers["MegaPOV"].setText(env.prefs[megapov_path_prefs_key])

        else:
            self.choosers["MegaPOV"].setEnabled(0)
            #self.megapov_path_lineedit.setText("")
            #env.prefs[megapov_path_prefs_key] = ''
            env.prefs[megapov_enabled_prefs_key] = False
        self._update_povdir_enables() #bruce 060710

    # POV-Ray include slots #######################################

    # pov include directory [bruce 060710 for Mac A8; will be A8.1 in Windows, not sure about Linux]

    def _update_povdir_enables(self): #bruce 060710
        """
        [private method]
        Call this whenever anything changes regarding when to enable the povdir checkbox, line edit, or choose button.
        We enable the checkbox when either of the POV-Ray or MegaPOV plugins is enabled.
        We enable the line edit and choose button when that condition holds and when the checkbox is checked.
        We update this when any relevant checkbox changes, or when showing this page.
        This will work by reading prefs values, so only call it from slot methods after they have updated prefs values.
        """
        enable_checkbox = env.prefs[povray_enabled_prefs_key] or env.prefs[megapov_enabled_prefs_key]
        self.checkboxes["POV include dir"].setEnabled(enable_checkbox)
        self.choosers["POV include dir"].setEnabled(enable_checkbox)
        enable_edits = enable_checkbox and env.prefs[povdir_enabled_prefs_key]
            # note: that prefs value should and presumably does agree with self.povdir_checkbox.isChecked()
        return

    def enable_pov_include_dir(self, enable = True): #bruce 060710
        """
        Slot method for povdir checkbox.
        povdir is enabled when enable = True.
        povdir is disabled when enable = False.
        """
        env.prefs[povdir_enabled_prefs_key] = not not enable
        self._update_povdir_enables()
        if enable:
            self.choosers["POV include dir"].setEnabled(1)
            env.prefs[povdir_enabled_prefs_key] = True

            # Sets the MegaPOV (executable) path to the standard location, if it exists.
            #if not env.prefs[povdir_path_prefs_key]:
                #env.prefs[povdir_path_prefs_key] = get_default_plugin_path( \
                    #"C:\\Program Files\\POV-Ray for Windows v3.6\\bin\\megapov.exe", \
                    #"/usr/local/bin/megapov", \
                    #"/usr/local/bin/megapov")

            self.choosers["POV include dir"].setText(env.prefs[povdir_path_prefs_key])

        else:
            self.choosers["POV include dir"].setEnabled(0)
            #self.megapov_path_lineedit.setText("")
            #env.prefs[megapov_path_prefs_key] = ''
            env.prefs[povdir_enabled_prefs_key] = False#        self.povdir_lineedit.setText(env.prefs[povdir_path_prefs_key])
        return

    def set_pov_include_dir(self): #bruce 060710
        """
        Slot for Pov include dir "Choose" button.
        """
        setPath = str_or_unicode(self.choosers["POV include dir"].text)
        env.prefs[povdir_path_prefs_key] = setPath
        prefs = preferences.prefs_context()
        prefs[povdir_path_prefs_key] = setPath
        return setPath
        #povdir_path = get_dirname_and_save_in_prefs(self, povdir_path_prefs_key, 'Choose Custom POV-Ray Include directory')
        ## note: return value can't be ""; if user cancels, value is None;
        ## to set "" you have to edit the lineedit text directly, but this doesn't work since
        ## no signal is caught to save that into the prefs db!
        ## ####@@@@ we ought to catch that signal... is it returnPressed?? would that be sent if they were editing it, then hit ok?
        ## or if they clicked elsewhere? (currently that fails to remove focus from the lineedits, on Mac, a minor bug IMHO)
        ## (or uncheck the checkbox for the same effect). (#e do we want a "clear" button, for A8.1?)

        #if povdir_path:
            #self.povdir_lineedit.setText(env.prefs[povdir_path_prefs_key])
            ## the function above already saved it in prefs, under the same condition
        #return

    def povdir_lineedit_textChanged(self, *args): #bruce 060710
        if debug_povdir_signals():
            print "povdir_lineedit_textChanged",args
            # this happens on programmatic changes, such as when the page is shown or the choose button slot sets the text
        try:
            # note: Ideally we'd only do this when return was pressed, mouse was clicked elsewhere (with that also removing keyfocus),
            # other keyfocus removals, including dialog ok or cancel. That is mostly nim,
            # so we have to do it all the time for now -- this is the only way for the user to set the text to "".
            # (This even runs on programmatic sets of the text. Hope that's ok.)
            env.prefs[povdir_path_prefs_key] = path = str_or_unicode( self.povdir_lineedit.text() ).strip()
            if debug_povdir_signals():
                print "debug fyi: set pov include dir to [%s]" % (path,)
        except:
            if env.debug():
                print_compact_traceback("bug, ignored: ")
        return

    def povdir_lineedit_returnPressed(self, *args): #bruce 060710
        if debug_povdir_signals():
            print "povdir_lineedit_returnPressed",args
            # this happens when return is pressed in the widget, but NOT when user clicks outside it
            # or presses OK on the dialog -- which means it's useless when taken alone,
            # in case user edits text and then presses ok without ever pressing return.

    ########## End of slot methods for "Plug-ins" page widgets ###########

    ########## Slot methods for "General" (former name "Caption") page widgets ################

    def change_pasteOffsetScaleFactorForChunks(self, val):
        """
        Slot method for the I{Paste offset scale for chunks} doublespinbox.
        @param val: The timeout interval in seconds.
        @type  val: double
        @see ops_copy_Mixin._pasteGroup()
        """
        env.prefs[pasteOffsetScaleFactorForChunks_prefs_key] = val

    def change_pasteOffsetScaleFactorForDnaObjects(self, val):
        """
        Slot method for the I{Paste offset scale for dna objects} doublespinbox.
        @param val: The timeout interval in seconds.
        @type  val: double
        """
        env.prefs[pasteOffsetScaleFactorForDnaObjects_prefs_key] = val
    
    # PAGE: UNDO
    
    def _setupPage_Undo(self):
        connect_checkbox_with_boolean_pref(self.undo_restore_view_CheckBox,
                                           undoRestoreView_prefs_key)
        connect_checkbox_with_boolean_pref(
            self.undo_automatic_checkpoints_CheckBox,
            undoAutomaticCheckpoints_prefs_key)
        connect_spinBox_with_pref(self.undo_stack_memory_limit_SpinBox,
                                  undoStackMemoryLimit_prefs_key)
        return
    
    # PAGE: WINDOW
    def _setupPage_Window(self):
        return
    
    # PAGE: REPORTS
    def _setupPage_Reports(self):
        connect_checkbox_with_boolean_pref(
            self.history_include_message_serial_CheckBox,
            historyMsgSerialNumber_prefs_key)
        connect_checkbox_with_boolean_pref(
            self.history_include_message_timestamp_CheckBox,
            historyMsgTimestamp_prefs_key)
        return
    
    # PAGE: TOOLTIPS
    def _setupPage_Tooltips(self):
        connect_checkbox_with_boolean_pref(self.atom_chunk_information_CheckBox,
                                           dynamicToolTipAtomChunkInfo_prefs_key)
        connect_checkbox_with_boolean_pref(self.atom_mass_information_CheckBox,
                                           dynamicToolTipAtomMass_prefs_key)
        connect_checkbox_with_boolean_pref(self.atom_XYZ_coordinates_CheckBox,
                                           dynamicToolTipAtomPosition_prefs_key)
        connect_checkbox_with_boolean_pref(self.atom_XYZ_distance_CheckBox,
                                           dynamicToolTipAtomDistanceDeltas_prefs_key)
        connect_checkbox_with_boolean_pref(self.atom_include_vdw_CheckBox,
                                           dynamicToolTipVdwRadiiInAtomDistance_prefs_key)
        connect_spinBox_with_pref(self.atom_distance_precision_SpinBox,
                                  dynamicToolTipAtomDistancePrecision_prefs_key)
        connect_spinBox_with_pref(self.atom_angle_precision_SpinBox,
                                  dynamicToolTipBendAnglePrecision_prefs_key)
        connect_checkbox_with_boolean_pref(
            self.bond_distance_between_atoms_CheckBox,
           dynamicToolTipBondLength_prefs_key) 
        connect_checkbox_with_boolean_pref(self.bond_chunk_information_CheckBox,
                                           dynamicToolTipBondChunkInfo_prefs_key)
        return

    ########## Slot methods for top level widgets ################

    def getPagenameList(self):
        """
        Returns a list of page names (i.e. the "stack of widgets") inside
        prefsStackedWidget.

        @return: List of page names.
        @rtype:  List

        @attention: Qt Designer assigns the QStackedWidget property
                    "currentPageName" (which is not a formal attr)
                    to the QWidget (page) attr "objectName".

        @see: U{B{QStackedWidget}<http://doc.trolltech.com/4/qstackedwidget.html>}.
        """
        _pagenameList = []

        for _widgetIndex in range(self.prefsStackedWidget.count()):
            _widget = self.prefsStackedWidget.widget(_widgetIndex)
            _pagename = str(_widget.objectName())
            _pagenameList.append(_pagename)

        return _pagenameList

    def accept(self):
        """
        The slot method for the 'OK' button.
        """
        QDialog.accept(self)
        return

    def reject(self):
        """
        The slot method for the "Cancel" button.
        """
        # The Cancel button has been removed, but this still gets called
        # when the user hits the dialog's "Close" button in the dialog's
        # window border (upper right X).
        # Since I've not implemented 'Cancel', it is safer to go ahead and
        # save all preferences anyway.  Otherwise, any changed preferences
        # will not be persistent (after this session).
        # This will need to be removed when we implement a true cancel function.
        # Mark 050629.
        QDialog.reject(self)
        return

    pass # end of class Preferences

# end

if __name__ == "__main__":
    _iconprefix = "/Users/derrickhendricks/trunks/trunk/cad/src"
    app = QtGui.QApplication(sys.argv)
    p = Preferences()
    sys.exit(app.exec_())