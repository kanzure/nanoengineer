# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Preferences.py

@author: Mark
@version: $Id$
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

from ne1_ui.prefs.PreferencesDialog import Ui_PreferencesDialog
import foundation.preferences as preferences
from utilities.debug import print_compact_traceback
from utilities.debug_prefs import debug_pref, Choice_boolean_False
import foundation.env as env
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf
from widgets.widget_helpers import double_fixup
from widgets.prefs_widgets import connect_colorpref_to_colorframe, connect_checkbox_with_boolean_pref
from utilities import debug_flags
from utilities.constants import str_or_unicode
from platform.PlatformDependent import screen_pos_size
from platform.PlatformDependent import get_rootdir
from platform.Paths import get_default_plugin_path
from utilities.icon_utilities import geticon

from utilities.prefs_constants import displayCompass_prefs_key
from utilities.prefs_constants import displayCompassLabels_prefs_key
from utilities.prefs_constants import displayPOVAxis_prefs_key
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
from utilities.prefs_constants import pasteOffsetScaleFactorForChunks_pref_key
from utilities.prefs_constants import pasteOffsetScaleFactorForDnaObjects_pref_key

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
from utilities.prefs_constants import mouseWheelTimeoutInterval_pref_key

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
from utilities.prefs_constants import startupMode_prefs_key
from utilities.prefs_constants import defaultMode_prefs_key
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
from utilities.prefs_constants import indicateOverlappingAtoms_pref_key
from utilities.prefs_constants import fogEnabled_prefs_key

#global display preferences
from utilities.constants import diDEFAULT ,diTrueCPK, diLINES
from utilities.constants import diBALL, diTUBES, diDNACYLINDER

from utilities.constants import black, white, gray

# =
# Preferences widgets constants. I suggest that these be moved to another
# file (i.e. prefs_constants.py or another file). Discuss with Bruce. -Mark

# Widget constants for the "Model View" page.

BG_BLUE_SKY = 0
BG_EVENING_SKY = 1
BG_SEAGREEN = 2
BG_BLACK = 3
BG_WHITE = 4
BG_GRAY = 5
BG_CUSTOM = 6

# GDS = global display style
GDS_INDEXES = [diLINES, diTUBES, diBALL, diTrueCPK, diDNACYLINDER]
GDS_NAMES   = ["Lines", "Tubes", "Ball and Stick", "CPK", "DNA Cylinder"]
GDS_ICONS   = ["Lines", "Tubes", "Ball_and_Stick", "CPK", "DNACylinder" ]

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

def debug_povdir_signals():
    return 0 and env.debug()

# This list of mode names correspond to the names listed in the modes combo box.
modes = ['SELECTMOLS', 'MODIFY', 'DEPOSIT', 'COOKIE', 'EXTRUDE', 'FUSECHUNKS', 'MOVIE']

# List of Default Modes and Startup Modes.  Mark 050921.
# [bruce 060403 guesses these need to correspond to certain combobox indices.]

#ninad070430, 070501 For A9 , startup mode = default mode = SELECTMOLS mode
#but not changing the values in the list per Bruc's suggestions.
#instead, default_commandName and startup_commandName will return 'SELMOLS'
#Although the following lists contain "illegal values",
#there is code that cares about their indices in the lists.

default_modes = ['SELECTMOLS', 'MODIFY', 'DEPOSIT']
startup_modes = ['$DEFAULT_MODE', 'DEPOSIT']

def fix_commandName_pref( commandName, commandName_list, commandName_fallback = None): #bruce 060403
    """
    commandName came from prefs db; if it's in commandName_list, return it unchanged,
    but if not, return one of the commandNames in commandName_list to be used in place of it, or commandName_fallback.
    This is REQUIRED for decoding any commandName-valued prefs value.
    """
    assert len(commandName_list) > 0 or commandName_fallback
    if commandName in commandName_list:
        return commandName
    # handle SELECTATOMS being superseded by DEPOSIT
    if commandName == 'SELECTATOMS' and 'DEPOSIT' in commandName_list:
        return 'DEPOSIT'
    # handle future modes not yet supported by current code
    # (at this point it might be better to return the user's default mode;
    #  callers wanting this can pass it as commandName_fallback)
    return commandName_fallback or commandName_list[-1]
        # could use any arbitrary element rather than the last one (at -1),
        # but in the list constants above, the last choices seem to be best

def default_commandName(): #bruce 060403
    """
    Return the commandName string of the user's default mode.
    External code should use this, rather than directly using env.prefs[ defaultMode_prefs_key ].
    """
    #ninad070501 For A9 , startup mode = default mode = SELECTMOLS mode
    return 'SELECTMOLS'
    ##return fix_commandName_pref( env.prefs[ defaultMode_prefs_key ], default_modes)

def startup_commandName(): #bruce 060403
    """
    Return the commandName string (literal or symbolic, e.g. '$DEFAULT_MODE')
    of the user's startup mode. External code should use this, rather than
    directly using env.prefs[ startupMode_prefs_key ].
    """
    #ninad 070501 For A9 , startup mode = default mode = SELECTMOLS mode
    return 'SELECTMOLS'
    ##return fix_commandName_pref( env.prefs[ startupMode_prefs_key ], startup_modes, startup_modes[0] )

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

def validate_gamess_path(parent, gmspath):
    """
    Checks that gmspath (GAMESS executable) exists.  If not, the user is asked
    if they want to use the File Chooser to select the GAMESS executable.
    This function does not check whether the GAMESS path is actually GAMESS
    or if it is the correct version of GAMESS for this platform (i.e. PC GAMESS
    for Windows).

    @return:  "gmspath" if it is validated or if the user does not want to
              change it for any reason, or
              "new_gmspath" if gmspath is invalid and the user selected a new
              GAMESS executable. Return value might be "".
    """

    if not gmspath: # It is OK if gmspath is empty.
        return ""
    elif os.path.exists(gmspath):
        return gmspath
    else:
        ret = QMessageBox.warning( parent, "GAMESS Executable Path",
                                   gmspath + " does not exist.\nDo you want to use the File Chooser to browse for the GAMESS executable?",
                                   "&Yes", "&No", "",
                                   0, 1 )

        if ret == 0: # Yes
            new_gmspath = get_gamess_path(parent)
            if not new_gmspath:
                return gmspath # Cancelled from file chooser.  Just return the original gmspath.
            else:
                return new_gmspath

        else: # No
            return gmspath

def get_pref_or_optval(key, val, optval):
    """
    Return <key>'s value. If <val> is equal to <key>'s value, return <optval>
    instead.
    """
    if env.prefs[key] == val:
        return optval
    else:
        return env.prefs[key]

class Preferences(QDialog, Ui_PreferencesDialog):
    """
    The Preferences dialog used for accessing and changing user
    preferences.
    """
    pagenameList = [] # List of page names in prefsStackedWidget.

    def __init__(self, assy):
        QDialog.__init__(self)
        self.setupUi(self)

        # Some important attrs.
        self.glpane = assy.o
        self.w = assy.w
        self.assy = assy
        self.pagenameList = self.getPagenameList()

        # Start of dialog setup.
        self._setupDialog_TopLevelWidgets()
        self._setupPage_General()
        self._setupPage_Color()
        self._setupPage_ModelView()
        self._setupPage_ZoomPanRotate()
        self._setupPage_Rulers()
        self._setupPage_Atoms()
        self._setupPage_Bonds()
        self._setupPage_Dna()
        self._setupPage_DnaMinorGrooveErrorIndicator()
        self._setupPage_DnaBaseOrientationIndicators()
        self._setupPage_Adjust()
        self._setupPage_Lighting()
        self._setupPage_Plugins()
        self._setupPage_Undo()
        self._setupPage_Window()
        self._setupPage_Reports()
        self._setupPage_Tooltips()

        # Assign "What's This" text for all widgets.
        from ne1_ui.prefs.WhatsThisText_for_PreferencesDialog import whatsThis_PreferencesDialog
        whatsThis_PreferencesDialog(self)

        self._hideOrShowWidgets()
        return
    # End of _init_()

    def _setupDialog_TopLevelWidgets(self):
        """
        Setup all the main dialog widgets and their signal-slot connection(s).
        """

        self.setWindowIcon(geticon("ui/actions/Tools/Options.png"))

        # This connects the "itemSelectedChanged" signal generated when the
        # user selects an item in the "Category" QTreeWidget on the left
        # side of the Preferences dialog (inside the "Systems Option" tab)
        # to the slot for turning to the correct page in the QStackedWidget
        # on the right side.
        self.connect(self.categoryTreeWidget, SIGNAL("itemSelectionChanged()"), self.showPage)

        # Connections for OK and What's This buttons at the bottom of the dialog.
        self.connect(self.okButton, SIGNAL("clicked()"), self.accept)
        self.connect(self.whatsThisToolButton, SIGNAL("clicked()"),QWhatsThis.enterWhatsThisMode)

        self.whatsThisToolButton.setIcon(
            geticon("ui/actions/Properties Manager/WhatsThis.png"))
        self.whatsThisToolButton.setIconSize(QSize(22, 22))
        self.whatsThisToolButton.setToolTip('Enter "What\'s This?" help mode')

        # Set the margin and spacing for these two gridlayouts:
        # gridlayout  = grid layout for the Preference dialog
        # gridlayout1 = grid layout for the System Options tab
        self.gridlayout.setMargin(2)
        self.gridlayout.setSpacing(2)

        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(0)
        return

    def _setupPage_General(self):
        """
        Setup the "General" page.
        """
        # Sponsor logos download permission options in General tab
        self.logosDownloadPermissionBtnGroup = QButtonGroup()
        self.logosDownloadPermissionBtnGroup.setExclusive(True)
        for button in self.sponsorLogosGroupBox.children():
            if isinstance(button, QAbstractButton):
                self.logosDownloadPermissionBtnGroup.addButton(button)
                buttonId = 0
                if button.text().startsWith("Never ask"):
                    buttonId = 1
                elif button.text().startsWith("Never download"):
                    buttonId = 2
                self.logosDownloadPermissionBtnGroup.setId(button, buttonId)

        # Check the correct permission radio button.
        if env.prefs[sponsor_permanent_permission_prefs_key]:
            if env.prefs[sponsor_download_permission_prefs_key]:
                self.logoNeverAskRadioBtn.setChecked(True)
            else:
                self.logoNeverDownLoadRadioBtn.setChecked(True)
        else:
            self.logoAlwaysAskRadioBtn.setChecked(True)

        self.connect(self.logosDownloadPermissionBtnGroup, SIGNAL("buttonClicked(int)"), self.setPrefsLogoDownloadPermissions)

        # Build Chunks option connections.
        connect_checkbox_with_boolean_pref( self.autobond_checkbox, buildModeAutobondEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.water_checkbox, buildModeWaterEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.buildmode_highlighting_checkbox, buildModeHighlightingEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.buildmode_select_atoms_checkbox, buildModeSelectAtomsOfDepositedObjEnabled_prefs_key )

        #Scale factor for copy-paste operation (see ops_copy_Mixin._pasteGroup())

        self.pasteOffsetScaleFactorForChunks_doubleSpinBox.setValue(
            env.prefs[pasteOffsetScaleFactorForChunks_pref_key])

        self.pasteOffsetScaleFactorForDnaObjects_doubleSpinBox.setValue(
            env.prefs[pasteOffsetScaleFactorForDnaObjects_pref_key])



        self.connect(self.pasteOffsetScaleFactorForChunks_doubleSpinBox,
                     SIGNAL("valueChanged(double)"),
                     self.change_pasteOffsetScaleFactorForChunks)
        self.connect(self.pasteOffsetScaleFactorForDnaObjects_doubleSpinBox,
                     SIGNAL("valueChanged(double)"),
                     self.change_pasteOffsetScaleFactorForDnaObjects)
        return

    def _setupPage_Color(self):
        """
        Setup the "Color" page.
        """
        # Background color widgets and connection(s).
        self._loadBackgroundColorItems()
        self.connect(self.backgroundColorComboBox, SIGNAL("activated(int)"), self.changeBackgroundColor)

        # Fog checkbox
        connect_checkbox_with_boolean_pref( self.enableFogCheckBox, fogEnabled_prefs_key )
        self.connect(self.enableFogCheckBox, SIGNAL("toggled(bool)"), self.enable_fog)

        # Hover highlighting color style widgets and connection(s).
        self._loadHoverHighlightingColorStylesItems()
        self.hoverHighlightingStyleComboBox.setCurrentIndex(HHS_INDEXES.index(env.prefs[hoverHighlightingColorStyle_prefs_key]))
        self.connect(self.hoverHighlightingStyleComboBox, SIGNAL("activated(int)"), self._change_hhStyle)
        connect_colorpref_to_colorframe( hoverHighlightingColor_prefs_key, self.hoverHighlightingColorFrame)
        self.connect(self.hoverHighlightingColorButton, SIGNAL("clicked()"), self._change_hhColor)

        # Selection color style widgets and connection(s).
        self._loadSelectionColorStylesItems()
        self.selectionStyleComboBox.setCurrentIndex(SS_INDEXES.index(env.prefs[selectionColorStyle_prefs_key]))
        self.connect(self.selectionStyleComboBox, SIGNAL("activated(int)"), self._change_selectionStyle)
        connect_colorpref_to_colorframe( selectionColor_prefs_key, self.selectionColorFrame)
        self.connect(self.selectionColorButton, SIGNAL("clicked()"), self._change_selectionColor)

        # Halo width spinbox.
        self.connect(self.haloWidthSpinBox, SIGNAL("valueChanged(int)"), self.change_haloWidth)
        self.connect(self.haloWidthResetButton, SIGNAL("clicked()"), self.reset_haloWidth)

        self.haloWidthResetButton.setIcon(geticon('ui/dialogs/Reset.png'))
        self.haloWidthSpinBox.setValue(env.prefs[haloWidth_prefs_key])
        self.change_haloWidth(env.prefs[haloWidth_prefs_key]) # Needed to update the reset button.

        return

    def _setupPage_ModelView(self):
        """
        Setup widgets to initial (default or defined) values on the
        'Model View' page.
        """
        # Setup the Global Display Style at start-up combobox
        self._setupGlobalDisplayStyleAtStartup_ComboBox()


        self.connect(self.compassGroupBox, SIGNAL("stateChanged(int)"), self.display_compass)
        self.connect(self.compass_position_combox, SIGNAL("activated(int)"), self.set_compass_position)

        connect_checkbox_with_boolean_pref( self.compassGroupBox, displayCompass_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_compass_labels_checkbox, displayCompassLabels_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_origin_axis_checkbox, displayOriginAxis_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_pov_axis_checkbox, displayPOVAxis_prefs_key )
        self.compass_position_combox.setCurrentIndex(self.glpane.compassPosition)

        return

    def _setupPage_ZoomPanRotate(self):
        """
        Setup widgets to initial (default or defined) values on the
        'Zoom, Pan Rotate' page.
        """

        # Animation speed checkbox and slider.
        connect_checkbox_with_boolean_pref( self.animate_views_checkbox, animateStandardViews_prefs_key )

        self.resetAnimationSpeed_btn.setIcon(
            geticon('ui/dialogs/Reset.png'))

        self.connect(self.animation_speed_slider, SIGNAL("sliderReleased()"), self.change_view_animation_speed)
        self.connect(self.resetAnimationSpeed_btn, SIGNAL("clicked()"), self.reset_animationSpeed)

        speed = int (env.prefs[animateMaximumTime_prefs_key] * -100)
        self.animation_speed_slider.setValue(speed)
        self._updateResetButton(self.resetAnimationSpeed_btn, animateMaximumTime_prefs_key)

        #mouse speed during rotation slider - ninad060906
        self.resetMouseSpeedDuringRotation_btn.setIcon(
            geticon('ui/dialogs/Reset.png'))

        self.connect(self.mouseSpeedDuringRotation_slider, SIGNAL("sliderReleased()"), self.change_mouseSpeedDuringRotation)
        self.connect(self.resetMouseSpeedDuringRotation_btn, SIGNAL("clicked()"), self.reset_mouseSpeedDuringRotation)

        mouseSpeedDuringRotation = int(env.prefs[mouseSpeedDuringRotation_prefs_key] * 100)
        self.mouseSpeedDuringRotation_slider.setValue(mouseSpeedDuringRotation)
        self._updateResetButton(self.resetMouseSpeedDuringRotation_btn, mouseSpeedDuringRotation_prefs_key)

        # Mouse wheel zoom settings combo boxes
        self.mouseWheelDirectionComboBox.setCurrentIndex(
            env.prefs[mouseWheelDirection_prefs_key])
        self.mouseWheelZoomInPointComboBox.setCurrentIndex(
            env.prefs[zoomInAboutScreenCenter_prefs_key])
        self.mouseWheelZoomOutPointComboBox.setCurrentIndex(
            env.prefs[zoomOutAboutScreenCenter_prefs_key])

        self.hhTimeoutIntervalDoubleSpinBox.setValue(env.prefs[mouseWheelTimeoutInterval_pref_key])

        # Connections for "Mouse controls" page.
        self.connect(self.mouseWheelDirectionComboBox, SIGNAL("currentIndexChanged(int)"), self.set_mouse_wheel_direction)
        self.connect(self.mouseWheelZoomInPointComboBox, SIGNAL("currentIndexChanged(int)"), self.set_mouse_wheel_zoom_in_position)
        self.connect(self.mouseWheelZoomOutPointComboBox, SIGNAL("currentIndexChanged(int)"), self.set_mouse_wheel_zoom_out_position)
        self.connect(self.hhTimeoutIntervalDoubleSpinBox, SIGNAL("valueChanged(double)"), self.set_mouse_wheel_timeout_interval)
        return

    def _setupPage_Rulers(self):
        """
        Setup the "Rulers" page.
        """

        self.connect(self.rulerDisplayComboBox, SIGNAL("currentIndexChanged(int)"), self.set_ruler_display)
        self.connect(self.rulerPositionComboBox, SIGNAL("currentIndexChanged(int)"), self.set_ruler_position)
        self.connect(self.ruler_color_btn, SIGNAL("clicked()"), self.change_ruler_color)
        self.connect(self.rulerOpacitySpinBox, SIGNAL("valueChanged(int)"), self.change_ruler_opacity)

        if env.prefs[displayVertRuler_prefs_key] and env.prefs[displayHorzRuler_prefs_key]:
            self.rulerDisplayComboBox.setCurrentIndex(0)
        elif not env.prefs[displayHorzRuler_prefs_key]:
            self.rulerDisplayComboBox.setCurrentIndex(1)
        elif not env.prefs[displayVertRuler_prefs_key]:
            self.rulerDisplayComboBox.setCurrentIndex(2)

        self.rulerPositionComboBox.setCurrentIndex(env.prefs[rulerPosition_prefs_key])
        connect_colorpref_to_colorframe( rulerColor_prefs_key, self.ruler_color_frame)
        self.rulerOpacitySpinBox.setValue(int(env.prefs[rulerOpacity_prefs_key] * 100))
        connect_checkbox_with_boolean_pref( self.showRulersInPerspectiveViewCheckBox, showRulersInPerspectiveView_prefs_key )
        return

    def _setupPage_Atoms(self):
        """
        Setup the "Atoms" page.
        """

        # "Change Element Colors" button.
        self.connect(self.change_element_colors_btn, SIGNAL("clicked()"), self.change_element_colors)

        # Atom colors
        connect_colorpref_to_colorframe( atomHighlightColor_prefs_key, self.atom_hilite_color_frame)
        connect_colorpref_to_colorframe( bondpointHighlightColor_prefs_key, self.bondpoint_hilite_color_frame)
        connect_colorpref_to_colorframe( bondpointHotspotColor_prefs_key, self.hotspot_color_frame)
        self.connect(self.atom_hilite_color_btn, SIGNAL("clicked()"), self.change_atom_hilite_color)
        self.connect(self.bondpoint_hilite_color_btn, SIGNAL("clicked()"), self.change_bondpoint_hilite_color)
        self.connect(self.hotspot_color_btn, SIGNAL("clicked()"), self.change_hotspot_color)
        self.connect(self.reset_atom_colors_btn, SIGNAL("clicked()"), self.reset_atom_colors)

        # Level of detail.
        self.connect(self.level_of_detail_combox, SIGNAL("activated(int)"), self.change_level_of_detail)

        lod = env.prefs[ levelOfDetail_prefs_key ]
        lod = int(lod)
        loditem = lod # index of corresponding spinbox item -- this is only correct for 0,1,2; other cases handled below
        if lod <= -1: # 'variable' (only -1 is used now, but other negative values might be used in future)
            # [bruce 060215 changed prefs value for 'variable' from 3 to -1, in case we have more LOD levels in the future]
            # [bruce 060317 fixed bug 1551 (in two files) by removing lod == 3 case from if/elif statement.]
            loditem = 3 # index of the spinbox item that says "variable"
        elif lod > 2:
            loditem = 2
        self.level_of_detail_combox.setCurrentIndex(loditem)

        # Ball and Stick atom scale factor.
        self.connect(self.ballStickAtomScaleFactorSpinBox, SIGNAL("valueChanged(int)"), self.change_ballStickAtomScaleFactor)
        self.connect(self.reset_ballstick_scale_factor_btn, SIGNAL("clicked()"), self.reset_ballStickAtomScaleFactor)

        self.reset_ballstick_scale_factor_btn.setIcon(
            geticon('ui/dialogs/Reset.png'))
        _sf = int (env.prefs[diBALL_AtomRadius_prefs_key] * 100.0)
        self.ballStickAtomScaleFactorSpinBox.setValue(_sf)
        self.change_ballStickAtomScaleFactor(_sf) # Needed to update the reset button.

        # CPK atom scale factor.
        self.connect(self.cpkAtomScaleFactorDoubleSpinBox, SIGNAL("valueChanged(double)"), self.change_cpkAtomScaleFactor)
        self.connect(self.reset_cpk_scale_factor_btn, SIGNAL("clicked()"), self.reset_cpkAtomScaleFactor)

        self.reset_cpk_scale_factor_btn.setIcon(
            geticon('ui/dialogs/Reset.png'))
        self.cpkAtomScaleFactorDoubleSpinBox.setValue(env.prefs[cpkScaleFactor_prefs_key])
        self.change_cpkAtomScaleFactor(env.prefs[cpkScaleFactor_prefs_key]) # Needed to update the reset button.

        # Checkboxes.
        connect_checkbox_with_boolean_pref( self.overlappingAtomIndicatorsCheckBox, indicateOverlappingAtoms_pref_key )
        connect_checkbox_with_boolean_pref( self.keepBondsTransmuteCheckBox, keepBondsDuringTransmute_prefs_key)
        return

    def _setupPage_Bonds(self):
        """
        Setup the "Bonds" page.
        """

        # Create "High order bond display" button group, which lives inside
        # of self.high_order_bond_display_groupbox (a QGroupBox).
        self.high_order_bond_display_btngrp = QButtonGroup()
        self.high_order_bond_display_btngrp.setExclusive(True)

        objId = 0
        for obj in [self.multCyl_radioButton, self.vanes_radioButton,
                    self.ribbons_radioButton]:
            self.high_order_bond_display_btngrp.addButton(obj)
            self.high_order_bond_display_btngrp.setId(obj, objId)
            objId +=1

        self.connect(self.high_order_bond_display_btngrp, SIGNAL("buttonClicked(int)"), self.change_high_order_bond_display)
        self.connect(self.reset_bond_colors_btn, SIGNAL("clicked()"), self.reset_bond_colors)
        self.connect(self.show_bond_labels_checkbox, SIGNAL("toggled(bool)"), self.change_bond_labels)
        self.connect(self.show_valence_errors_checkbox, SIGNAL("toggled(bool)"), self.change_show_valence_errors)
        self.connect(self.ballstick_bondcolor_btn, SIGNAL("clicked()"), self.change_ballstick_bondcolor)
        self.connect(self.bond_hilite_color_btn, SIGNAL("clicked()"), self.change_bond_hilite_color)
        self.connect(self.bond_line_thickness_spinbox, SIGNAL("valueChanged(int)"), self.change_bond_line_thickness)
        self.connect(self.bond_stretch_color_btn, SIGNAL("clicked()"), self.change_bond_stretch_color)
        self.connect(self.bond_vane_color_btn, SIGNAL("clicked()"), self.change_bond_vane_color)


        self.connect(self.cpk_cylinder_rad_spinbox, SIGNAL("valueChanged(int)"), self.change_ballstick_cylinder_radius)

        #bruce 050805 here's the new way: subscribe to the preference value,
        # but make sure to only have one such subs (for one widget's bgcolor) at a time.
        # The colors in these frames will now automatically update whenever the prefs value changes.
        ##e (should modify this code to share its prefskey list with the one for restore_defaults)
        connect_colorpref_to_colorframe(
            bondHighlightColor_prefs_key, self.bond_hilite_color_frame)
        connect_colorpref_to_colorframe(
            bondStretchColor_prefs_key, self.bond_stretch_color_frame)
        connect_colorpref_to_colorframe(
            bondVaneColor_prefs_key, self.bond_vane_color_frame)
        connect_colorpref_to_colorframe(
            diBALL_bondcolor_prefs_key, self.ballstick_bondcolor_frame)
        connect_checkbox_with_boolean_pref(
            self.showBondStretchIndicators_checkBox,
            showBondStretchIndicators_prefs_key)

        # also handle the non-color prefs on this page:
        #  ('pi_bond_style',   ['multicyl','vane','ribbon'],  pibondStyle_prefs_key,   'multicyl' ),
        pibondstyle_sym = env.prefs[ pibondStyle_prefs_key]
        button_code = { 'multicyl':0,'vane':1, 'ribbon':2 }.get( pibondstyle_sym, 0)
            # Errors in prefs db are not detected -- we just use the first button because (we happen to know) it's the default.
            # This int encoding is specific to this buttongroup.
            # The prefs db and the rest of the code uses the symbolic strings listed above.
        if button_code == 0:
            self.multCyl_radioButton.setChecked(True)
        elif button_code ==1:
            self.vanes_radioButton.setChecked(True)
        else:
            self.ribbons_radioButton.setChecked(True)

        #  ('pi_bond_letters', 'boolean',                     pibondLetters_prefs_key, False ),
        self.show_bond_labels_checkbox.setChecked( env.prefs[ pibondLetters_prefs_key] )
            # I don't know whether this sends the signal as if the user changed it
            # (and even if Qt doc says no, this needs testing since I've seen it be wrong about those things before),
            # but in the present code it doesn't matter unless it causes storing default value explicitly into prefs db
            # (I can't recall whether or not it does). Later this might matter more, e.g. if we have prefs-value modtimes.
            # [bruce 050806]

        # ('show_valence_errors',        'boolean', showValenceErrors_prefs_key,   True ),
        # (This is a per-atom warning, but I decided to put it on the Bonds page since you need it when
        #  working on high order bonds. And, since I could fit that into the UI more easily.)

        if hasattr(self, 'show_valence_errors_checkbox'):
            self.show_valence_errors_checkbox.setChecked( env.prefs[ showValenceErrors_prefs_key] )
            # note: this does cause the checkbox to send its "toggled(bool)" signal to our slot method.

        # Set Lines Dislplay Mode line thickness.  Mark 050831.
        self.update_bond_line_thickness_suffix()
        self.bond_line_thickness_spinbox.setValue( env.prefs[linesDisplayModeThickness_prefs_key] )

        # Set CPK Cylinder radius (percentage).  Mark 051003.
        self.cpk_cylinder_rad_spinbox.setValue(int (env.prefs[diBALL_BondCylinderRadius_prefs_key] * 100.0))
        return


    def _setupPage_Dna(self):
        """
        Setup the "DNA" page.
        """
        # Connections for "DNA defaults" groupbox widgets.
        self.connect(self.dnaBasesPerTurnDoubleSpinBox, SIGNAL("valueChanged(double)"), self.save_dnaBasesPerTurn)
        self.connect(self.dnaRiseDoubleSpinBox, SIGNAL("valueChanged(double)"), self.save_dnaRise)
        self.connect(self.dnaRestoreFactoryDefaultsPushButton, SIGNAL("clicked()"), self.dnaRestoreFactoryDefaults)

        connect_colorpref_to_colorframe(dnaDefaultStrand1Color_prefs_key, self.dnaDefaultStrand1ColorFrame)
        self.connect(self.dnaDefaultStrand1ColorPushButton, SIGNAL("clicked()"), self.changeDnaDefaultStrand1Color)

        connect_colorpref_to_colorframe(dnaDefaultStrand2Color_prefs_key, self.dnaDefaultStrand2ColorFrame)
        self.connect(self.dnaDefaultStrand2ColorPushButton, SIGNAL("clicked()"), self.changeDnaDefaultStrand2Color)

        connect_colorpref_to_colorframe(dnaDefaultSegmentColor_prefs_key, self.dnaDefaultSegmentColorFrame)
        self.connect(self.dnaDefaultSegmentColorPushButton, SIGNAL("clicked()"), self.changeDnaDefaultSegmentColor)

        self.dnaBasesPerTurnDoubleSpinBox.setValue(env.prefs[bdnaBasesPerTurn_prefs_key])
        self.dnaRiseDoubleSpinBox.setValue(env.prefs[bdnaRise_prefs_key])

        # Connections for "DNA Strand Arrowheads" groupbox widgets.
        self.connect(self.strandThreePrimeArrowheadsCustomColorPushButton, SIGNAL("clicked()"), self.change_dnaStrandThreePrimeArrowheadCustomColor)
        self.connect(self.strandFivePrimeArrowheadsCustomColorPushButton, SIGNAL("clicked()"), self.change_dnaStrandFivePrimeArrowheadCustomColor)
        self.connect(self.strandThreePrimeArrowheadsCustomColorCheckBox, SIGNAL("toggled(bool)"), self.update_dnaStrandThreePrimeArrowheadCustomColorWidgets)
        self.connect(self.strandFivePrimeArrowheadsCustomColorCheckBox, SIGNAL("toggled(bool)"), self.update_dnaStrandFivePrimeArrowheadCustomColorWidgets)

        # DNA strand arrowheads preferences
        connect_checkbox_with_boolean_pref(self.arrowsOnBackBones_checkBox, arrowsOnBackBones_prefs_key)
        connect_checkbox_with_boolean_pref(self.arrowsOnThreePrimeEnds_checkBox, arrowsOnThreePrimeEnds_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.arrowsOnFivePrimeEnds_checkBox,
            arrowsOnFivePrimeEnds_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.strandThreePrimeArrowheadsCustomColorCheckBox,
            useCustomColorForThreePrimeArrowheads_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.strandFivePrimeArrowheadsCustomColorCheckBox,
            useCustomColorForFivePrimeArrowheads_prefs_key)

        #Join strands command may override global strand arrow head options

        connect_colorpref_to_colorframe(
            dnaStrandThreePrimeArrowheadsCustomColor_prefs_key,
            self.strandThreePrimeArrowheadsCustomColorFrame)

        connect_colorpref_to_colorframe(
            dnaStrandFivePrimeArrowheadsCustomColor_prefs_key,
            self.strandFivePrimeArrowheadsCustomColorFrame)


        self.update_dnaStrandThreePrimeArrowheadCustomColorWidgets(
            env.prefs[useCustomColorForThreePrimeArrowheads_prefs_key])

        self.update_dnaStrandFivePrimeArrowheadCustomColorWidgets(
            env.prefs[useCustomColorForFivePrimeArrowheads_prefs_key])

    def _setupPage_DnaMinorGrooveErrorIndicator(self):
        """
        Setup the "DNA Minor Groove Error Indicator" page.
        """
        # Connections for "DNA Minor Groove Error Indicator" groupbox widgets.
        self.connect(self.dnaMinGrooveAngleSpinBox, SIGNAL("valueChanged(int)"), self.save_dnaMinMinorGrooveAngles)
        self.connect(self.dnaMaxGrooveAngleSpinBox, SIGNAL("valueChanged(int)"), self.save_dnaMaxMinorGrooveAngles)
        self.connect(self.dnaGrooveIndicatorColorButton, SIGNAL("clicked()"), self.change_dnaMinorGrooveErrorIndicatorColor)
        self.connect(self.dnaMinorGrooveRestoreFactoryDefaultsPushButton, SIGNAL("clicked()"), self._restore_dnaMinorGrooveFactoryDefaults)

        # Display Minor Groove Error Indicator groupbox widgets.

        connect_checkbox_with_boolean_pref(
            self.dnaDisplayMinorGrooveErrorGroupBox,
            dnaDisplayMinorGrooveErrorIndicators_prefs_key)

        self.dnaMinGrooveAngleSpinBox.setValue(
            env.prefs[dnaMinMinorGrooveAngle_prefs_key])

        self.dnaMaxGrooveAngleSpinBox.setValue(
            env.prefs[dnaMaxMinorGrooveAngle_prefs_key])

        connect_colorpref_to_colorframe(
            dnaMinorGrooveErrorIndicatorColor_prefs_key,
            self.dnaGrooveIndicatorColorFrame)

    def _setupPage_DnaBaseOrientationIndicators(self):
        """
        Setup the "DNA Base Orientation Indicators" page.
        """
        # Connections for "DNA base orientation indicator" groupbox widgets.
        self.connect(self.dnaDisplayBaseOrientationIndicatorsGroupBox, SIGNAL("toggled(bool)"), self.toggle_dnaDisplayBaseOrientationIndicatorsGroupBox)
        self.connect(self.dnaBaseOrientationIndicatorsInverseCheckBox, SIGNAL("toggled(bool)"), self.toggle_dnaDisplayBaseOrientationInvIndicatorsCheckBox)
        self.connect(self.dnaBaseOrientationIndicatorsThresholdSpinBox, SIGNAL("valueChanged(double)"), self.change_dnaBaseIndicatorsAngle)
        self.connect(self.dnaBaseOrientationIndicatorsTerminalDistanceSpinBox, SIGNAL("valueChanged(double)"), self.change_dnaBaseIndicatorsDistance)
        self.connect(self.dnaChooseBaseOrientationIndicatorsColorButton, SIGNAL("clicked()"), self.change_dnaBaseIndicatorsColor)
        self.connect(self.dnaChooseBaseOrientationIndicatorsInvColorButton, SIGNAL("clicked()"), self.change_dnaBaseInvIndicatorsColor)
        self.connect(self.dnaBaseIndicatorsPlaneNormalComboBox, SIGNAL("activated(int)"), self.change_dnaBaseOrientIndicatorsPlane)

        # DNA Base Orientation Indicator stuff.
        self.dnaDisplayBaseOrientationIndicatorsGroupBox.setChecked(
            env.prefs[dnaBaseIndicatorsEnabled_prefs_key])
        self.dnaBaseIndicatorsPlaneNormalComboBox.setCurrentIndex(
            env.prefs[dnaBaseIndicatorsPlaneNormal_prefs_key])
        self.dnaBaseOrientationIndicatorsInverseCheckBox.setChecked(
            env.prefs[dnaBaseInvIndicatorsEnabled_prefs_key])
        self.update_dnaBaseIndicatorsAngle()
        self.update_dnaBaseIndicatorsDistance()
        connect_colorpref_to_colorframe(dnaBaseIndicatorsColor_prefs_key,
                                        self.dnaBaseOrientationIndicatorsColorFrame)
        connect_colorpref_to_colorframe(dnaBaseInvIndicatorsColor_prefs_key,
                                        self.dnaBaseOrientationIndicatorsInvColorFrame)

    def _setupPage_Adjust(self):
        """
        Setup the "Adjust" page.
        """
        self.connect(self.adjustEngineCombobox, SIGNAL("activated(int)"), self.set_adjust_minimization_engine)
        self.connect(self.endRmsDoubleSpinBox, SIGNAL("valueChanged(double)"), self.changeEndRms)
        self.connect(self.endMaxDoubleSpinBox, SIGNAL("valueChanged(double)"), self.changeEndMax)
        self.connect(self.cutoverRmsDoubleSpinBox, SIGNAL("valueChanged(double)"), self.changeCutoverRms)
        self.connect(self.cutoverMaxDoubleSpinBox, SIGNAL("valueChanged(double)"), self.changeCutoverMax)

        self.endRmsDoubleSpinBox.setSpecialValueText("Automatic")
        self.endMaxDoubleSpinBox.setSpecialValueText("Automatic")
        self.cutoverRmsDoubleSpinBox.setSpecialValueText("Automatic")
        self.cutoverMaxDoubleSpinBox.setSpecialValueText("Automatic")

        # "Settings for Adjust" groupbox. ###########################

        # Adjust Engine combobox.
        self.adjustEngineCombobox.setCurrentIndex(
            env.prefs[Adjust_minimizationEngine_prefs_key])

        # Watch motion in real time checkbox.
        connect_checkbox_with_boolean_pref(
            self.watch_motion_groupbox,
            Adjust_watchRealtimeMinimization_prefs_key )

        self.watch_motion_groupbox.setEnabled(
            env.prefs[Adjust_watchRealtimeMinimization_prefs_key])

        # "Watch motion..." radio btngroup
        self.watch_motion_buttongroup = QButtonGroup()
        self.watch_motion_buttongroup.setExclusive(True)
        for obj in self.watch_motion_groupbox.children():
            if isinstance(obj, QAbstractButton):
                self.watch_motion_buttongroup.addButton(obj)

        #Preference for enabling/disabling electrostatics during Adjustment
        #for the DNA reduced model. Ninad 20070809
        connect_checkbox_with_boolean_pref(
            self.electrostaticsForDnaDuringAdjust_checkBox,
            electrostaticsForDnaDuringAdjust_prefs_key)

        # Convergence Criteria groupbox
        # [WARNING: bruce 060705 copied this into MinimizeEnergyProp.py]
        self.endrms = get_pref_or_optval(Adjust_endRMS_prefs_key, -1.0, 0.0)
        self.endRmsDoubleSpinBox.setValue(self.endrms)

        self.endmax = get_pref_or_optval(Adjust_endMax_prefs_key, -1.0, 0.0)
        self.endMaxDoubleSpinBox.setValue(self.endmax)

        self.cutoverrms = get_pref_or_optval(Adjust_cutoverRMS_prefs_key, -1.0, 0.0)
        self.cutoverRmsDoubleSpinBox.setValue(self.cutoverrms)

        self.cutovermax = get_pref_or_optval(Adjust_cutoverMax_prefs_key, -1.0, 0.0)
        self.cutoverMaxDoubleSpinBox.setValue(self.cutovermax)

        return

    def _setupPage_Lighting(self):
        """
        Setup the "Lighting" page.
        """
        # Connections for "Lighting" page.
        self.connect(self.light_ambient_slider, SIGNAL("valueChanged(int)"), self.change_lighting)
        self.connect(self.light_ambient_slider, SIGNAL("sliderReleased()"), self.save_lighting)
        self.connect(self.light_checkbox, SIGNAL("toggled(bool)"), self.toggle_light)
        self.connect(self.light_color_btn, SIGNAL("clicked()"), self.change_light_color)
        self.connect(self.light_combobox, SIGNAL("activated(int)"), self.change_active_light)
        self.connect(self.light_diffuse_slider, SIGNAL("sliderReleased()"), self.save_lighting)
        self.connect(self.light_diffuse_slider, SIGNAL("valueChanged(int)"), self.change_lighting)
        self.connect(self.light_specularity_slider, SIGNAL("valueChanged(int)"), self.change_lighting)
        self.connect(self.light_specularity_slider, SIGNAL("sliderReleased()"), self.save_lighting)
        self.connect(self.light_x_linedit, SIGNAL("returnPressed()"), self.save_lighting)
        self.connect(self.light_y_linedit, SIGNAL("returnPressed()"), self.save_lighting)
        self.connect(self.light_z_linedit, SIGNAL("returnPressed()"), self.save_lighting)
        self.connect(self.lighting_restore_defaults_btn, SIGNAL("clicked()"), self.restore_default_lighting)
        self.connect(self.ms_brightness_slider, SIGNAL("sliderReleased()"), self.change_material_brightness_stop)
        self.connect(self.ms_brightness_slider, SIGNAL("valueChanged(int)"), self.change_material_brightness)
        self.connect(self.ms_brightness_slider, SIGNAL("sliderPressed()"), self.change_material_brightness_start)
        self.connect(self.ms_finish_slider, SIGNAL("valueChanged(int)"), self.change_material_finish)
        self.connect(self.ms_finish_slider, SIGNAL("sliderReleased()"), self.change_material_finish_stop)
        self.connect(self.ms_finish_slider, SIGNAL("sliderPressed()"), self.change_material_finish_start)
        self.connect(self.ms_on_checkbox, SIGNAL("toggled(bool)"), self.toggle_material_specularity)
        self.connect(self.ms_shininess_slider, SIGNAL("sliderReleased()"), self.change_material_shininess_stop)
        self.connect(self.ms_shininess_slider, SIGNAL("sliderPressed()"), self.change_material_shininess_start)
        self.connect(self.ms_shininess_slider, SIGNAL("valueChanged(int)"), self.change_material_shininess)

        self._updatePage_Lighting()
        return

    def _updatePage_Lighting(self, lights = None): #mark 051124
        """
        Setup widgets to initial (default or defined) values on the Lighting page.
        """
        if not lights:
            self.lights = self.original_lights = self.glpane.getLighting()
        else:
            self.lights = lights

        light_num = self.light_combobox.currentIndex()

        self.update_light_combobox_items()

        # Move lc_prefs_keys upstairs.  Mark.
        lc_prefs_keys = [light1Color_prefs_key, light2Color_prefs_key, light3Color_prefs_key]
        self.current_light_key = lc_prefs_keys[light_num] # Get prefs key for current light color.
        connect_colorpref_to_colorframe(self.current_light_key, self.light_color_frame)
        self.light_color = env.prefs[self.current_light_key]

        # These sliders generate signals whenever their 'setValue()' slot is called (below).
        # This creates problems (bugs) for us, so we disconnect them temporarily.
        self.disconnect(self.light_ambient_slider, SIGNAL("valueChanged(int)"), self.change_lighting)
        self.disconnect(self.light_diffuse_slider, SIGNAL("valueChanged(int)"), self.change_lighting)
        self.disconnect(self.light_specularity_slider, SIGNAL("valueChanged(int)"), self.change_lighting)

        # self.lights[light_num][0] contains 'color' attribute.
        # We already have it (self.light_color) from the prefs key (above).
        a = self.lights[light_num][1] # ambient intensity
        d = self.lights[light_num][2] # diffuse intensity
        s = self.lights[light_num][3] # specular intensity

        self.light_ambient_slider.setValue(int (a * 100)) # generates signal
        self.light_diffuse_slider.setValue(int (d * 100)) # generates signal
        self.light_specularity_slider.setValue(int (s * 100)) # generates signal

        self.light_ambient_linedit.setText(str(a))
        self.light_diffuse_linedit.setText(str(d))
        self.light_specularity_linedit.setText(str(s))

        self.light_x_linedit.setText(str (self.lights[light_num][4]))
        self.light_y_linedit.setText(str (self.lights[light_num][5]))
        self.light_z_linedit.setText(str (self.lights[light_num][6]))
        self.light_checkbox.setChecked(self.lights[light_num][7])

        # Reconnect the slots to the light sliders.
        self.connect(self.light_ambient_slider, SIGNAL("valueChanged(int)"), self.change_lighting)
        self.connect(self.light_diffuse_slider, SIGNAL("valueChanged(int)"), self.change_lighting)
        self.connect(self.light_specularity_slider, SIGNAL("valueChanged(int)"), self.change_lighting)

        self._setup_material_group()
        return

    # _setup_material_group() should be folded back into _updatePage_Lighting(). Mark 051204.
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
                int(env.prefs[material_specular_finish_prefs_key] * 100)
            self.shininess = self.original_shininess = \
                int(env.prefs[material_specular_shininess_prefs_key])
            self.brightness = self.original_brightness= \
                int(env.prefs[material_specular_brightness_prefs_key] * 100)

        # Enable/disable specular highlights.
        self.ms_on_checkbox.setChecked(self.material_specularity )

        # For whiteness, the stored range is 0.0 (Plastic) to 1.0 (Metal).  The Qt slider range
        # is 0 - 100, so we multiply by 100 (above) to set the slider.  Mark. 051129.
        self.ms_finish_slider.setValue(self.whiteness) # generates signal
        self.ms_finish_linedit.setText(str(self.whiteness * .01))

        # For shininess, the range is 15 (low) to 60 (high).  Mark. 051129.
        self.ms_shininess_slider.setValue(self.shininess) # generates signal
        self.ms_shininess_linedit.setText(str(self.shininess))

        # For brightness, the range is 0.0 (low) to 1.0 (high).  Mark. 051203.
        self.ms_brightness_slider.setValue(self.brightness) # generates signal
        self.ms_brightness_linedit.setText(str(self.brightness * .01))
        return

    def _setupPage_Plugins(self):
        """
        Setup the "Plug-ins" page.
        """
        # QuteMolX signal-slot connections.
        self.connect(self.qutemol_checkbox, SIGNAL("toggled(bool)"), self.enable_qutemol)
        self.connect( self.qutemol_path_lineedit, SIGNAL("textEdited (const QString&) "), self.set_qutemol_path)
        self.connect(self.qutemol_choose_btn, SIGNAL("clicked()"), self.choose_qutemol_path)

        # NanoHive-1 signal-slot connections.
        self.connect(self.nanohive_checkbox, SIGNAL("toggled(bool)"), self.enable_nanohive)
        self.connect( self.nanohive_path_lineedit, SIGNAL("textEdited (const QString&) "), self.set_nanohive_path)
        self.connect(self.nanohive_choose_btn, SIGNAL("clicked()"), self.choose_nanohive_path)

        # POV-Ray signal-slot connections.
        self.connect(self.povray_checkbox, SIGNAL("toggled(bool)"), self.enable_povray)
        self.connect( self.povray_path_lineedit, SIGNAL("textEdited (const QString&) "), self.set_povray_path)
        self.connect(self.povray_choose_btn, SIGNAL("clicked()"), self.choose_povray_path)

        # POV dir signal-slot connections.
        self.connect(self.povdir_checkbox, SIGNAL("toggled(bool)"), self.enable_povdir)
        self.connect( self.povdir_lineedit, SIGNAL("textEdited (const QString&) "), self.povdir_lineedit_textChanged )
        self.connect(self.povdir_choose_btn, SIGNAL("clicked()"), self.set_povdir)
        self.connect( self.povdir_lineedit, SIGNAL("returnPressed()"), self.povdir_lineedit_returnPressed )

        # MegaPOV signal-slot connections.
        self.connect(self.megapov_checkbox, SIGNAL("toggled(bool)"), self.enable_megapov)
        self.connect( self.megapov_path_lineedit, SIGNAL("textEdited (const QString&) "), self.set_megapov_path )
        self.connect(self.megapov_choose_btn, SIGNAL("clicked()"), self.choose_megapov_path)

        # GAMESS signal-slot connections.
        self.connect(self.gamess_checkbox, SIGNAL("toggled(bool)"), self.enable_gamess)
        self.connect(self.gamess_path_lineedit, SIGNAL("textEdited(const QString&)"), self.set_gamess_path)
        self.connect(self.gamess_choose_btn, SIGNAL("clicked()"), self.choose_gamess_path)

        # GROMACS signal-slot connections.
        self.connect(self.gromacs_checkbox, SIGNAL("toggled(bool)"), self.enable_gromacs)
        self.connect(self.gromacs_path_lineedit, SIGNAL("textEdited(const QString&)"), self.set_gromacs_path)
        self.connect(self.gromacs_choose_btn, SIGNAL("clicked()"), self.choose_gromacs_path)

        # cpp signal-slot connections.
        self.connect(self.cpp_checkbox, SIGNAL("toggled(bool)"), self.enable_cpp)
        self.connect(self.cpp_path_lineedit, SIGNAL("textEdited(const QString&)"), self.set_cpp_path)
        self.connect(self.cpp_choose_btn, SIGNAL("clicked()"), self.choose_cpp_path)

        # NanoVision-1 signal-slots connections.
        self.connect(self.nv1_checkbox, SIGNAL("toggled(bool)"), self.enable_nv1)
        self.connect(self.nv1_path_lineedit, SIGNAL("textEdited(const QString&)"), self.set_nv1_path)
        self.connect(self.nv1_choose_btn, SIGNAL("clicked()"), self.choose_nv1_path)
        return

    def _setupPage_Undo(self):
        """
        Setup the "Undo" page.
        """
        # Connections for "Undo" page.
        self.connect(self.undo_stack_memory_limit_spinbox, SIGNAL("valueChanged(int)"), self.change_undo_stack_memory_limit)
        self.connect(self.update_number_spinbox, SIGNAL("valueChanged(int)"), self.update_number_spinbox_valueChanged)
        return

    def _setupPage_Window(self):
        """
        Setup the "Window" page.
        """
        # Connections for "Window" page.
        self.connect(self.caption_fullpath_checkbox, SIGNAL("stateChanged(int)"), self.set_caption_fullpath)
        self.connect(self.current_height_spinbox, SIGNAL("valueChanged(int)"), self.change_window_size)
        self.connect(self.current_width_spinbox, SIGNAL("valueChanged(int)"), self.change_window_size)
        self.connect(self.restore_saved_size_btn, SIGNAL("clicked()"), self.restore_saved_size)
        self.connect(self.save_current_btn, SIGNAL("clicked()"), self.save_current_win_pos_and_size)

        # Connections for font widgets (in "Windows" page). Mark 2007-05-27.
        self.connect(self.selectedFontGroupBox, SIGNAL("toggled(bool)"), self.change_use_selected_font)
        self.connect(self.fontComboBox, SIGNAL("currentFontChanged (const QFont &)"), self.change_font)
        self.connect(self.fontSizeSpinBox, SIGNAL("valueChanged(int)"), self.change_fontsize)
        self.connect(self.makeDefaultFontPushButton, SIGNAL("clicked()"), self.change_selected_font_to_default_font)

        # Update the max value of the Current Size spinboxes
        screen = screen_pos_size()
        ((x0, y0), (w, h)) = screen
        self.current_width_spinbox.setRange(1, w)
        self.current_height_spinbox.setRange(1, h)

        # Set value of the Current Size Spinboxes
        pos, size = _get_window_pos_size(self.w)
        self.current_width_spinbox.setValue(size[0])
        self.current_height_spinbox.setValue(size[1])

        # Set string of Saved Size Lineedits
        from utilities.prefs_constants import mainwindow_geometry_prefs_key_prefix
        keyprefix = mainwindow_geometry_prefs_key_prefix
        pos, size = _get_prefs_for_window_pos_size( self.w, keyprefix)
        self.update_saved_size(size[0], size[1])

        connect_checkbox_with_boolean_pref( self.remember_win_pos_and_size_checkbox, rememberWinPosSize_prefs_key )

        self.caption_prefix_linedit.setText(env.prefs[captionPrefix_prefs_key])
        self.caption_suffix_linedit.setText(env.prefs[captionSuffix_prefs_key])
            ##e someday we should make a 2-way connector function for LineEdits too
        connect_checkbox_with_boolean_pref( self.caption_fullpath_checkbox, captionFullPath_prefs_key )

        # Update Display Font widgets
        self.set_font_widgets(setFontFromPrefs = True) # Also sets the current display font.

        # Connect all QLineEdit widgets last. Otherwise they'll generate signals.
        self.connect( self.caption_prefix_linedit, SIGNAL("textChanged ( const QString & ) "), self.caption_prefix_linedit_textChanged )
        self.connect( self.caption_prefix_linedit, SIGNAL("returnPressed()"), self.caption_prefix_linedit_returnPressed )
        self.connect( self.caption_suffix_linedit, SIGNAL("textChanged ( const QString & ) "), self.caption_suffix_linedit_textChanged )
        self.connect( self.caption_suffix_linedit, SIGNAL("returnPressed()"), self.caption_suffix_linedit_returnPressed )
        return

    def _setupPage_Reports(self):
        """
        Setup the "Reports" page.
        """
        connect_checkbox_with_boolean_pref( self.msg_serial_number_checkbox, historyMsgSerialNumber_prefs_key )
        connect_checkbox_with_boolean_pref( self.msg_timestamp_checkbox, historyMsgTimestamp_prefs_key )
        return

    def _setupPage_Tooltips(self):
        """
        Setup the "Tooltips" page.
        """
        # Connections for "Tooltips" page.
        self.connect(self.dynamicToolTipAtomDistancePrecision_spinbox, SIGNAL("valueChanged(int)"), self.change_dynamicToolTipAtomDistancePrecision)
        self.connect(self.dynamicToolTipBendAnglePrecision_spinbox, SIGNAL("valueChanged(int)"), self.change_dynamicToolTipBendAnglePrecision)

        #Atom related Dynamic tooltip preferences
        connect_checkbox_with_boolean_pref(self.dynamicToolTipAtomChunkInfo_checkbox, dynamicToolTipAtomChunkInfo_prefs_key)
        connect_checkbox_with_boolean_pref(self.dynamicToolTipAtomMass_checkbox, dynamicToolTipAtomMass_prefs_key)
        connect_checkbox_with_boolean_pref(self.dynamicToolTipAtomPosition_checkbox, dynamicToolTipAtomPosition_prefs_key)
        connect_checkbox_with_boolean_pref(self.dynamicToolTipAtomDistanceDeltas_checkbox, dynamicToolTipAtomDistanceDeltas_prefs_key)
        connect_checkbox_with_boolean_pref(
            self.includeVdwRadiiInAtomDistanceInfo,
            dynamicToolTipVdwRadiiInAtomDistance_prefs_key)

        #Bond related dynamic tool tip preferences
        connect_checkbox_with_boolean_pref(self.dynamicToolTipBondLength_checkbox, dynamicToolTipBondLength_prefs_key)
        connect_checkbox_with_boolean_pref(self.dynamicToolTipBondChunkInfo_checkbox, dynamicToolTipBondChunkInfo_prefs_key)

        self.dynamicToolTipAtomDistancePrecision_spinbox.setValue(env.prefs[ dynamicToolTipAtomDistancePrecision_prefs_key ] )
        self.dynamicToolTipBendAnglePrecision_spinbox.setValue(env.prefs[ dynamicToolTipBendAnglePrecision_prefs_key ] )
        return

    def _hideOrShowWidgets(self):
        """
        Permanently hides some widgets in the Preferences dialog.
        This provides an easy and convenient way of hiding widgets that have
        been added but not fully implemented. It is also possible to
        show hidden widgets that have a debug pref set to enable them.
        """
        widgetList = [self.nanohive_lbl,
                      self.nanohive_checkbox,
                      self.nanohive_path_lineedit,
                      self.nanohive_choose_btn,
                      self.gamess_checkbox,
                      self.gamess_lbl,
                      self.gamess_path_lineedit,
                      self.gamess_choose_btn]

        for widget in widgetList:
            if debug_pref("Show GAMESS and ESP Image UI options",
                          Choice_boolean_False,
                          prefs_key = True):
                widget.show()
            else:
                widget.hide()
        return

    # caption_prefix slot methods [#e should probably refile these with other slot methods?]
    def caption_prefix_linedit_textChanged(self, qstring):
        ## print "caption_prefix_linedit_textChanged: %r" % str(qstring) # this works
        self.any_caption_text_changed()

    def caption_prefix_linedit_returnPressed(self):
        ## print "caption_prefix_linedit_returnPressed"
            # This works, but the Return press also closes the dialog!
            # [later, bruce 060710 -- probably due to a Qt Designer property on the button, fixable by .setAutoDefault(0) ###@@@]
            # (Both for the lineedit whose signal we're catching, and the one whose signal catching is initially nim.)
            # Certainly that makes it a good idea to catch it, though it'd be better to somehow "capture" it
            # so it would not close the dialog.
        self.any_caption_text_changed()

    # caption_suffix slot methods can be equivalent to the ones for caption_prefix
    caption_suffix_linedit_textChanged = caption_prefix_linedit_textChanged
    caption_suffix_linedit_returnPressed = caption_prefix_linedit_returnPressed

    ###### Private methods ###############################

    def _loadBackgroundColorItems(self):
        """
        Load the background color combobox with all the color options and sets
        the current background color
        """
        backgroundIndexes = [BG_BLUE_SKY, BG_EVENING_SKY, BG_SEAGREEN,
                             BG_BLACK, BG_WHITE, BG_GRAY, BG_CUSTOM]

        backgroundNames   = ["Blue Sky (default)", "Evening Sky", "Sea Green",
                             "Black", "White", "Gray", "Custom..."]

        backgroundIcons   = ["Background_BlueSky", "Background_EveningSky",
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

        self._updateBackgroundColorComboBoxIndex()
        return

    def _updateBackgroundColorComboBoxIndex(self):
        """
        Set current index in the background color combobox.
        """
        if self.glpane.backgroundGradient:
            self.backgroundColorComboBox.setCurrentIndex(self.glpane.backgroundGradient - 1)
        else:
            if (env.prefs[ backgroundColor_prefs_key ] == black):
                self.backgroundColorComboBox.setCurrentIndex(BG_BLACK)
            elif (env.prefs[ backgroundColor_prefs_key ] == white):
                self.backgroundColorComboBox.setCurrentIndex(BG_WHITE)
            elif (env.prefs[ backgroundColor_prefs_key ] == gray):
                self.backgroundColorComboBox.setCurrentIndex(BG_GRAY)
            else:
                self.backgroundColorComboBox.setCurrentIndex(BG_CUSTOM)
        return

    def _loadHoverHighlightingColorStylesItems(self):
        """
        Load the hover highlighting style combobox with items.
        """
        for hoverHighlightingStyle in HHS_OPTIONS:
            self.hoverHighlightingStyleComboBox.addItem(hoverHighlightingStyle)
        return

    def _loadSelectionColorStylesItems(self):
        """
        Load the selection color style combobox with items.
        """
        for selectionStyle in SS_OPTIONS:
            self.selectionStyleComboBox.addItem(selectionStyle)
        return

    # = Methods for the "Model View" page.

    def _setupGlobalDisplayStyleAtStartup_ComboBox(self):
        """
        Loads the global display style combobox with all the display options
        and sets the current display style
        """
        gdsIconDist = dict(zip(GDS_NAMES, GDS_ICONS))

        for gdsName in GDS_NAMES: # gds = global display style
            basename = gdsIconDist[gdsName] + ".png"
            iconPath = os.path.join("ui/actions/View/Display/",
                                    basename)
            self.globalDisplayStyleStartupComboBox.addItem(geticon(iconPath), gdsName)

        display_style = env.prefs[ startupGlobalDisplayStyle_prefs_key ]
        self.globalDisplayStyleStartupComboBox.setCurrentIndex(GDS_INDEXES.index(display_style))

        self.connect(self.globalDisplayStyleStartupComboBox, SIGNAL("activated(int)"), self.setGlobalDisplayStyleAtStartUp)

    def setGlobalDisplayStyleAtStartUp(self, gdsIndexUnused):
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
        self.glpane.setDisplay(display_style, True)
        self.glpane.gl_update()
        return

    #e this is really a slot method -- should refile it
    def any_caption_text_changed(self):
        # Update Caption prefs
        # The prefix and suffix updates should be done via slots [bruce 050811 doing that now] and include a validator.
        # Will do later.  Mark 050716.

        # (in theory, only one of these has changed, and even though we resave prefs for both,
        #  only the changed one will trigger any formulas watching the prefs value for changes. [bruce 050811])
        #bruce 070503 Qt4 bugfix (prefix and suffix): str().strip() rather than QString().stripWhiteSpace()
        # (but, like the old code, still only allows one space char on the side that can have one,
        #  in order to most easily require at least one on that side; if mot for that, we'd use rstrip and lstrip)
        prefix = str_or_unicode(self.caption_prefix_linedit.text())
        prefix = prefix.strip()
        if prefix:
            prefix = prefix + ' '
        env.prefs[captionPrefix_prefs_key] = prefix

        suffix = str_or_unicode(self.caption_suffix_linedit.text())
        suffix = suffix.strip()
        if suffix:
            suffix = ' ' + suffix
        env.prefs[captionSuffix_prefs_key] = suffix
        return

    ###### End of private methods. ########################

    ########## Slot methods for "General" page widgets ################

    def display_compass(self, val):
        """
        Slot for the Display Compass checkbox, which enables/disables the
        Display Compass Labels checkbox.
        """
        self.display_compass_labels_checkbox.setEnabled(val)

    def set_compass_position(self, val):
        """
        Set position of compass.

        @param val: The position, where:
                    - 0 = upper right
                    - 1 = upper left
                    - 2 = lower left
                    - 3 = lower right
        @type  val: int
        """
        # set the pref
        env.prefs[compassPosition_prefs_key] = val
        # update the glpane
        self.glpane.compassPosition = val
        self.glpane.gl_update()

    def change_pasteOffsetScaleFactorForChunks(self, val):
        """
        Slot method for the I{Paste offset scale for chunks} doublespinbox.
        @param val: The timeout interval in seconds.
        @type  val: double
        @see ops_copy_Mixin._pasteGroup()
        """
        env.prefs[pasteOffsetScaleFactorForChunks_pref_key] = val

    def change_pasteOffsetScaleFactorForDnaObjects(self, val):
        """
        Slot method for the I{Paste offset scale for dna objects} doublespinbox.
        @param val: The timeout interval in seconds.
        @type  val: double
        """
        env.prefs[pasteOffsetScaleFactorForDnaObjects_pref_key] = val

    def enable_fog(self, val):
        """
        Switches fog.
        """
        self.glpane.gl_update()

    def set_default_projection_OBSOLETE(self, projection):
        """
        Set the projection.

        @param projection: The projection, where:
                           - 0 = Perspective
                           - 1 = Orthographic
        @type  projection: int

        @deprecated: I'm removing this from the Preferences dialog.
        The defaultProjection_prefs_key will be set instead by the
        main window UI (View > Display menu). -Mark 2008-05-20
        """
        # set the pref
        env.prefs[defaultProjection_prefs_key] = projection
        self.glpane.setViewProjection(projection)

    def change_displayOriginAsSmallAxis(self, value):
        """"
        This sets the preference to view origin as small axis so that it is
        sticky across sessions.
        """
        #set the preference
        env.prefs[displayOriginAsSmallAxis_prefs_key] = value
            #niand060920 This condition might not be necessary as we are disabling the btn_grp
            #for the oridin axis radiobuttons
        if env.prefs[displayOriginAxis_prefs_key]:
            self.glpane.gl_update()

    def change_high_quality_graphics(self, state): #mark 060315.
        """
        Enable/disable high quality graphics during view animations.

        @attention: This has never been implemented. The checkbox has been
                    removed from the UI file for A9. Mark 060815.
        """
        # Let the user know this is NIY. Addresses bug 1249 for A7. mark 060314.
        msg = "High Quality Graphics is not implemented yet."
        from utilities.Log import orangemsg
        env.history.message(orangemsg(msg))

    def change_view_animation_speed(self):
        """
        Sets the view animation speed between .25 (fast) and 3.0 (slow) seconds.
        """
        # To change the range, edit the maxValue and minValue attr for the slider.
        # For example, if you want the fastest animation time to be .1 seconds,
        # change maxValue to -10.  If you want the slowest time to be 4.0 seconds,
        # change minValue to -400.  mark 060124.
        env.prefs[animateMaximumTime_prefs_key] = \
           self.animation_speed_slider.value() / -100.0

        self._updateResetButton(self.resetAnimationSpeed_btn, animateMaximumTime_prefs_key)
        return

    def _updateResetButton(self, resetButton, key):
        """
        Enables/disables I{resetButton} if I{key} is not equal/equal to its
        default value.
        """
        if env.prefs.has_default_value(key):
            resetButton.setEnabled(0)
        else:
            resetButton.setEnabled(1)
        return

    def reset_animationSpeed(self):
        """
        Slot called when pressing the Animation speed reset button.
        Restores the default value of the animation speed.
        """
        env.prefs.restore_defaults([animateMaximumTime_prefs_key])
        self.animation_speed_slider.setValue(int (env.prefs[animateMaximumTime_prefs_key] * -100))
        self.resetAnimationSpeed_btn.setEnabled(0)
        return

    def change_mouseSpeedDuringRotation(self):
        """
        Slot that sets the speed factor controlling rotation speed during mouse button drags.
        0.3 = slow and 1.0 = fast.
        """
        env.prefs[mouseSpeedDuringRotation_prefs_key] = \
           self.mouseSpeedDuringRotation_slider.value() / 100.0

        self._updateResetButton(self.resetMouseSpeedDuringRotation_btn, mouseSpeedDuringRotation_prefs_key)
        return

    def reset_mouseSpeedDuringRotation(self):
        """
        Slot called when pressing the Mouse speed during rotation reset button.
        Restores the default value of the mouse speed.
        """
        env.prefs.restore_defaults([mouseSpeedDuringRotation_prefs_key])
        self.mouseSpeedDuringRotation_slider.setValue(int (env.prefs[mouseSpeedDuringRotation_prefs_key] * 100.0))
        self.resetMouseSpeedDuringRotation_btn.setEnabled(0)

    def changeEndRms(self, endRms):
        """
        Slot for EndRMS.
        """
        if endRms:
            env.prefs[Adjust_endRMS_prefs_key] = endRms
        else:
            env.prefs[Adjust_endRMS_prefs_key] = -1.0

    def changeEndMax(self, endMax):
        """
        Slot for EndMax.
        """
        if endMax:
            env.prefs[Adjust_endMax_prefs_key] = endMax
        else:
            env.prefs[Adjust_endMax_prefs_key] = -1.0

    def changeCutoverRms(self, cutoverRms):
        """
        Slot for CutoverRMS.
        """
        if cutoverRms:
            env.prefs[Adjust_cutoverRMS_prefs_key] = cutoverRms
        else:
            env.prefs[Adjust_cutoverRMS_prefs_key] = -1.0

    def changeCutoverMax(self, cutoverMax):
        """
        Slot for CutoverMax.
        """
        if cutoverMax:
            env.prefs[Adjust_cutoverMax_prefs_key] = cutoverMax
        else:
            env.prefs[Adjust_cutoverMax_prefs_key] = -1.0

    def set_adjust_minimization_engine(self, engine):
        """
        Combobox action, sets Adjust_minimizationEngine preference
        """
        env.prefs[Adjust_minimizationEngine_prefs_key] = engine

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
        if permission == 1:
            env.prefs[sponsor_permanent_permission_prefs_key] = True
            env.prefs[sponsor_download_permission_prefs_key] = True

        elif permission == 2:
            env.prefs[sponsor_permanent_permission_prefs_key] = True
            env.prefs[sponsor_download_permission_prefs_key] = False

        else:
            env.prefs[sponsor_permanent_permission_prefs_key] = False

    # = BG color slot methods

    def changeBackgroundColor(self, idx):
        """
        Slot method for the background color combobox.

        @note: the pref_keys are set in setBackgroundGradient()
               and setBackgroundColor().
        """
        #print "changeBackgroundColor(): Slot method called. Idx =", idx

        if idx == BG_BLUE_SKY:
            self.glpane.setBackgroundGradient(idx + 1)
        elif idx == BG_EVENING_SKY:
            self.glpane.setBackgroundGradient(idx + 1)
        elif idx == BG_SEAGREEN:
            self.glpane.setBackgroundGradient(idx + 1)
        elif idx == BG_BLACK:
            self.glpane.setBackgroundColor(black)
        elif idx == BG_WHITE:
            self.glpane.setBackgroundColor(white)
        elif idx == BG_GRAY:
            self.glpane.setBackgroundColor(gray)
        elif idx == BG_CUSTOM:
            #change background color to Custom Color
            self.chooseCustomBackgroundColor()
        else:
            msg = "Unknown color idx=", idx
            print_compact_traceback(msg)

        self.glpane.gl_update() # Needed!
        return

    def chooseCustomBackgroundColor(self):
        """
        Choose a custom background color.
        """
        c = QColorDialog.getColor(RGBf_to_QColor(self.glpane.getBackgroundColor()), self)
        if c.isValid():
            self.glpane.setBackgroundColor(QColor_to_RGBf(c))
        else:
            # User cancelled. Reset the combobox to the previous item.
            self._updateBackgroundColorComboBoxIndex()

    def _change_hhStyle(self, idx):
        """
        Slot method for Hover Highlighting combobox.
        Change the (3D) hover highlighting style.
        """
        env.prefs[hoverHighlightingColorStyle_prefs_key] = HHS_INDEXES[idx]

    def _change_hhColor(self):
        """
        Change the 3D hover highlighting color.
        """
        self.usual_change_color(hoverHighlightingColor_prefs_key)

    def _change_selectionStyle(self, idx):
        """
        Slot method for Selection Style combobox used to
        Change the (3D) selection color style.
        """
        env.prefs[selectionColorStyle_prefs_key] = SS_INDEXES[idx]

    def _change_selectionColor(self):
        """
        Change the 3D selection color.
        """
        self.usual_change_color(selectionColor_prefs_key)

    def change_haloWidth(self, width):
        """
        Change the halo style width.

        @param width: The width in pixels.
        @type  width: int
        """
        env.prefs[haloWidth_prefs_key] = width
        self._updateResetButton(self.haloWidthResetButton, haloWidth_prefs_key)

        return

    def reset_haloWidth(self):
        """
        Slot called when pressing the Halo width reset button.
        Restores the default value of the halo width.
        """
        env.prefs.restore_defaults([haloWidth_prefs_key])
        self.haloWidthSpinBox.setValue(env.prefs[haloWidth_prefs_key])

    def set_mouse_wheel_direction(self, direction):
        """
        Slot for Mouse Wheel Direction combo box.

        @param direction: The mouse wheel direction for zooming in.
                          0 = Pull (default), 1 = Push
        @type  direction: int
        """
        env.prefs[mouseWheelDirection_prefs_key] = direction
        self.w.updateMouseWheelSettings()
        return

    def set_mouse_wheel_zoom_in_position(self, position):
        """
        Slot for Mouse Wheel "Zoom In Position" combo box.

        @param position: The mouse wheel zoom in position, where:
                        0 = Cursor position (default)
                        1 = Graphics area center
        @type  position: int
        """
        env.prefs[zoomInAboutScreenCenter_prefs_key] = position
        self.w.updateMouseWheelSettings()
        return

    def set_mouse_wheel_zoom_out_position(self, position):
        """
        Slot for Mouse Wheel "Zoom Out Position" combo box.

        @param position: The mouse wheel zoom out position, where:
                        0 = Cursor position (default)
                        1 = Graphics area center
        @type  position: int
        """
        env.prefs[zoomOutAboutScreenCenter_prefs_key] = position
        self.w.updateMouseWheelSettings()
        return

    def set_mouse_wheel_timeout_interval(self, interval):
        """
        Slot method for the I{Hover highlighting timeout interval} spinbox.
        @param interval: The timeout interval in seconds.
        @type  interval: double
        """
        env.prefs[mouseWheelTimeoutInterval_pref_key] = interval

    # = Ruler slot methods

    def set_ruler_display(self, display):
        """
        Set display of individual rulers.

        @param display: The ruler display, where:
                    - 0 = display both rulers
                    - 1 = display vertical ruler only
                    - 2 = display horizontal ruler only

        @type  display: int
        """
        env.prefs[displayVertRuler_prefs_key] = True
        env.prefs[displayHorzRuler_prefs_key] = True

        if display == 1:
            env.prefs[displayHorzRuler_prefs_key] = False

        elif display == 2:
            env.prefs[displayVertRuler_prefs_key] = False

        # update the glpane
        self.glpane.gl_update()

    def set_ruler_position(self, position):
        """
        Set position of ruler(s).

        @param position: The ruler position, where:
                    - 0 = lower left
                    - 1 = upper left
                    - 2 = lower right
                    - 3 = upper right

        @type  position: int
        """
        # set the pref
        env.prefs[rulerPosition_prefs_key] = position

        # update the glpane
        self.glpane.gl_update()

    def change_ruler_color(self):
        """
        Change the ruler color.
        """
        self.usual_change_color( rulerColor_prefs_key)

    def change_ruler_opacity(self, opacity):
        """
        Change the ruler opacity.
        """
        env.prefs[rulerOpacity_prefs_key] = opacity * 0.01

    ########## End of slot methods for "General" page widgets ###########

    ########## Slot methods for "Atoms" page widgets ################

    def change_element_colors(self):
        """
        Display the Element Color Settings Dialog.
        """
        # Since the prefs dialog is modal, the element color settings dialog must be modal.
        self.w.showElementColorSettings(self)

    def usual_change_color(self, prefs_key, caption = "choose"): #bruce 050805
        from widgets.prefs_widgets import colorpref_edit_dialog
        colorpref_edit_dialog( self, prefs_key, caption = caption)

    def change_atom_hilite_color(self):
        """
        Change the atom highlight color.
        """
        self.usual_change_color( atomHighlightColor_prefs_key)

    def change_bondpoint_hilite_color(self):
        """
        Change the bondpoint highlight color.
        """
        self.usual_change_color( bondpointHighlightColor_prefs_key)

    def change_hotspot_color(self): #bruce 050808 implement new slot which Mark recently added to .ui file
        """
        Change the free valence hotspot color.
        """
        #e fyi, we might rename hotspot to something like "bonding point" someday...
        self.usual_change_color( bondpointHotspotColor_prefs_key)

    def reset_atom_colors(self):
        #bruce 050805 let's try it like this:
        env.prefs.restore_defaults([ #e this list should be defined in a more central place.
                                     atomHighlightColor_prefs_key,
                                     bondpointHighlightColor_prefs_key,
                                     bondpointHotspotColor_prefs_key
                                     ])

    def change_level_of_detail(self, level_of_detail_item): #bruce 060215 revised this
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
        self.glpane.gl_update()
        # the redraw this causes will (as of tonight) always recompute the correct drawLevel (in Part._recompute_drawLevel),
        # and chunks will invalidate their display lists as needed to accomodate the change. [bruce 060215]
        return

    def change_ballStickAtomScaleFactor(self, scaleFactor):
        """
        Change the Ball and Stick atom scale factor.

        @param scaleFactor: The scale factor (%).
        @type  scaleFactor: int
        """

        env.prefs[diBALL_AtomRadius_prefs_key] = scaleFactor * .01
        self._updateResetButton(self.reset_ballstick_scale_factor_btn, diBALL_AtomRadius_prefs_key)
        return

    def reset_ballStickAtomScaleFactor(self):
        """
        Slot called when pressing the CPK Atom Scale Factor reset button.
        Restores the default value of the CPK Atom Scale Factor.
        """
        env.prefs.restore_defaults([diBALL_AtomRadius_prefs_key])
        self.ballStickAtomScaleFactorSpinBox.setValue(int (env.prefs[diBALL_AtomRadius_prefs_key] * 100.0))
        return

    def change_cpkAtomScaleFactor(self, scaleFactor):
        """
        Change the atom scale factor for CPK display style.

        @param scaleFactor: The scale factor (between 0.5 and 1.0).
        @type  scaleFactor: float
        """
        env.prefs[cpkScaleFactor_prefs_key] = scaleFactor
        self._updateResetButton(self.reset_cpk_scale_factor_btn, cpkScaleFactor_prefs_key)
        return

    def reset_cpkAtomScaleFactor(self):
        """
        Slot called when pressing the CPK Atom Scale Factor reset button.
        Restores the default value of the CPK Atom Scale Factor.
        """
        env.prefs.restore_defaults([cpkScaleFactor_prefs_key])
        self.cpkAtomScaleFactorDoubleSpinBox.setValue(env.prefs[cpkScaleFactor_prefs_key])

    ########## End of slot methods for "Atoms" page widgets ###########

    ########## Slot methods for "Bonds" page widgets ################

    def change_bond_hilite_color(self):
        """
        Change the bond highlight color.
        """
        self.usual_change_color( bondHighlightColor_prefs_key)

    def change_bond_stretch_color(self):
        """
        Change the bond stretch color.
        """
        self.usual_change_color( bondStretchColor_prefs_key)

    def change_bond_vane_color(self):
        """
        Change the bond vane color for pi orbitals.
        """
        self.usual_change_color( bondVaneColor_prefs_key)

    def change_ballstick_bondcolor(self): #bruce 060607 renamed this in this file and .ui/.py dialog files
        """
        Change the bond cylinder color used in Ball & Stick display mode.
        """
        self.usual_change_color( diBALL_bondcolor_prefs_key)

    def reset_bond_colors(self):
        #bruce 050805 let's try it like this:
        env.prefs.restore_defaults([ #e this list should be defined in a more central place.
                                     bondHighlightColor_prefs_key,
                                     bondStretchColor_prefs_key,
                                     bondVaneColor_prefs_key,
                                     diBALL_bondcolor_prefs_key,
                                     ])

    def change_high_order_bond_display(self, val): #bruce 050806 filled this in
        """
        Slot for the button group that sets the high order bond display.
        """
        #  ('pi_bond_style',   ['multicyl','vane','ribbon'],  pibondStyle_prefs_key,   'multicyl' ),
        try:
            symbol = {0:'multicyl', 1:'vane', 2:'ribbon'}[val]
            # note: this decoding must use the same (arbitrary) int->symbol mapping as the button group does.
            # It's just a coincidence that the order is the same as in the prefs-type listed above.
        except KeyError: #bruce 060627 added specific exception class (untested)
            print "bug in change_high_order_bond_display: unknown val ignored:", val
        else:
            env.prefs[ pibondStyle_prefs_key ] = symbol
        return

    def change_bond_labels(self, val): #bruce 050806 filled this in
        """
        Slot for the checkbox that turns Pi Bond Letters on/off.
        """
        # (BTW, these are not "labels" -- someday we might add user-settable longer bond labels,
        #  and the term "labels" should refer to that. These are just letters indicating the bond type. [bruce 050806])
        env.prefs[ pibondLetters_prefs_key ] = not not val
        # See also the other use of pibondLetters_prefs_key, where the checkbox is kept current when first shown.
        return

    def change_show_valence_errors(self, val): #bruce 050806 made this up
        """
        Slot for the checkbox that turns Show Valence Errors on/off.
        """
        env.prefs[ showValenceErrors_prefs_key ] = not not val
##        if debug_flags.atom_debug:
##            print showValenceErrors_prefs_key, env.prefs[ showValenceErrors_prefs_key ] #k prints true, from our initial setup of page
        return

    def change_bond_line_thickness(self, pixel_thickness): #mark 050831
        """
        Set the default bond line thickness for Lines display.
        pixel_thickness can be 1, 2 or 3.
        """
        env.prefs[linesDisplayModeThickness_prefs_key] = pixel_thickness
        self.update_bond_line_thickness_suffix()

    def update_bond_line_thickness_suffix(self):
        """
        Updates the suffix for the bond line thickness spinbox.
        """
        if env.prefs[linesDisplayModeThickness_prefs_key] == 1:
            self.bond_line_thickness_spinbox.setSuffix(' pixel')
        else:
            self.bond_line_thickness_spinbox.setSuffix(' pixels')

    def change_ballstick_cylinder_radius(self, val):
        """
        Change the CPK (Ball and Stick) cylinder radius by % value <val>.
        """
        #bruce 060607 renamed change_cpk_cylinder_radius -> change_ballstick_cylinder_radius (in this file and .ui/.py dialog files)
        env.prefs[diBALL_BondCylinderRadius_prefs_key] = val *.01

        # Bruce wrote:
        #k gl_update is probably not needed and in some cases is a slowdown [bruce 060607 comment]
        # so I tested it and confirmed that gl_update() isn't needed.
        # Mark 2008-01-31
        #self.glpane.gl_update()

    ########## End of slot methods for "Bonds" page widgets ###########

    ########## Slot methods for "DNA" page widgets ################

    def save_dnaBasesPerTurn(self, bases_per_turn):
        """
        Slot for I{Bases per turn} spinbox.
        @param bases_per_turn: The number of bases per turn.
        @type  bases_per_turn: double
        """
        env.prefs[bdnaBasesPerTurn_prefs_key] = bases_per_turn

    def save_dnaRise(self, rise):
        """
        Slot for B{Rise} spinbox.
        @param rise: The rise.
        @type  rise: double
        """
        env.prefs[bdnaRise_prefs_key] = rise

    def dnaRestoreFactoryDefaults(self):
        """
        Slot for I{Restore Factory Defaults} button.
        """
        env.prefs.restore_defaults([
            bdnaBasesPerTurn_prefs_key,
            bdnaRise_prefs_key,
            dnaDefaultStrand1Color_prefs_key,
            dnaDefaultStrand2Color_prefs_key,
            dnaDefaultSegmentColor_prefs_key
        ])

        # These generate signals (good), which calls slots
        # save_dnaBasesPerTurn() and save_dnaRise()
        self.dnaBasesPerTurnDoubleSpinBox.setValue(env.prefs[bdnaBasesPerTurn_prefs_key])
        self.dnaRiseDoubleSpinBox.setValue(env.prefs[bdnaRise_prefs_key])

    def changeDnaDefaultStrand1Color(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA default strand1 color.
        """
        self.usual_change_color( dnaDefaultStrand1Color_prefs_key )

    def changeDnaDefaultStrand2Color(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA default strand2 color.
        """
        self.usual_change_color( dnaDefaultStrand2Color_prefs_key )

    def changeDnaDefaultSegmentColor(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA default segment color.
        """
        self.usual_change_color( dnaDefaultSegmentColor_prefs_key )

    def save_dnaStrutScale(self, scale_factor):
        """
        Slot for B{Strut Scale Factor} spinbox.
        @param scale_factor: The struct scale factor.
        @type  scale_factor: int
        """
        env.prefs[dnaStrutScaleFactor_prefs_key] = scale_factor * .01

    def update_dnaStrandThreePrimeArrowheadCustomColorWidgets(self, enabled_flag):
        """
        Slot for the "Custom color" checkbox,for three prime arrowhead
        used to disable/enable thecolor related widgets (frame and choose button).
        """
        self.strandThreePrimeArrowheadsCustomColorFrame.setEnabled(enabled_flag)
        self.strandThreePrimeArrowheadsCustomColorPushButton.setEnabled(enabled_flag)
        return

    def update_dnaStrandFivePrimeArrowheadCustomColorWidgets(self, enabled_flag):
        """
        Slot for the "Custom color" checkbox, used to disable/enable the
        color related widgets (frame and choose button).
        """
        self.strandFivePrimeArrowheadsCustomColorFrame.setEnabled(enabled_flag)
        self.strandFivePrimeArrowheadsCustomColorPushButton.setEnabled(enabled_flag)
        return

    def change_dnaStrandThreePrimeArrowheadCustomColor(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA strand three prime arrowhead color.
        """
        self.usual_change_color( dnaStrandThreePrimeArrowheadsCustomColor_prefs_key )

    def change_dnaStrandFivePrimeArrowheadCustomColor(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA strand five prime arrowhead color.
        """
        self.usual_change_color( dnaStrandFivePrimeArrowheadsCustomColor_prefs_key )

    def save_dnaMinMinorGrooveAngles(self, minAngle):
        """
        Slot for minimum minor groove angle spinboxes.

        @param minAngle: The minimum angle.
        @type  minAngle: int
        """
        env.prefs[dnaMinMinorGrooveAngle_prefs_key] = minAngle

    def save_dnaMaxMinorGrooveAngles(self, maxAngle):
        """
        Slot for maximum minor groove angle spinboxes.

        @param maxAngle: The maximum angle.
        @type  maxAngle: int
        """
        env.prefs[dnaMaxMinorGrooveAngle_prefs_key] = maxAngle

    def change_dnaMinorGrooveErrorIndicatorColor(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA minor groove error indicator color.
        """
        self.usual_change_color( dnaMinorGrooveErrorIndicatorColor_prefs_key )

    def _restore_dnaMinorGrooveFactoryDefaults(self):
        """
        Slot for Minor Groove Error Indicator I{Restore Factory Defaults}
        button.
        """
        env.prefs.restore_defaults([
            dnaMinMinorGrooveAngle_prefs_key,
            dnaMaxMinorGrooveAngle_prefs_key,
            dnaMinorGrooveErrorIndicatorColor_prefs_key,
        ])

        # These generate signals!
        self.dnaMinGrooveAngleSpinBox.setValue(
            env.prefs[dnaMinMinorGrooveAngle_prefs_key])
        self.dnaMaxGrooveAngleSpinBox.setValue(
            env.prefs[dnaMaxMinorGrooveAngle_prefs_key])

    # DNA display style piotr 080310
    def change_dnaStyleStrandsColor(self, value):
        """
        Changes DNA Style strands color.

        @param color: The color mode:
                    - 0 = color same as chunk
                    - 1 = base oder
                    - 2 = strand order
        @type color: int
        """
        env.prefs[dnaStyleStrandsColor_prefs_key] = value

    def change_dnaStyleStrutsColor(self, color):
        """
        Changes DNA Style struts color.

        @param color: The color mode:
                    - 0 = color same as chunk
                    - 1 = strand order
                    - 2 = base type

        @type color: int
        """
        env.prefs[dnaStyleStrutsColor_prefs_key] = color

    def change_dnaStyleAxisColor(self, color):
        """
        Changes DNA Style axis color.

        @param color: The color mode:
                    - 0 = color same as chunk
                    - 0 = color same as chunk
                    - 1 = base oder
                    - 2 = discrete bse order
                    - 3 = base type
                    - 4 = strand order

        @type color: int
        """
        env.prefs[dnaStyleAxisColor_prefs_key] = color

    def change_dnaStyleBasesColor(self, color):
        """
        Changes DNA Style bases color.

        @param color: The color mode:
                    - 0 = color same as chunk
                    - 1 = base order
                    - 2 = strand order
                    - 3 = base type

        @type color: int
        """
        env.prefs[dnaStyleBasesColor_prefs_key] = color

    def change_dnaStyleStrandsShape(self, shape):
        """
        Changes DNA Style strands shape.

        @param shape: The shape mode:
                    - 0 = none (hidden)
                    - 1 = cylinders
                    - 2 = tube

        @type shape: int
        """
        env.prefs[dnaStyleStrandsShape_prefs_key] = shape

    def change_dnaStyleStrutsShape(self, shape):
        """
        Changes DNA Style strands shape.

        @param shape: The shape mode:
                    - 0 = none (hidden)
                    - 1 = base-axis-base
                    - 2 = straight cylinders

        @type shape: int
        """
        env.prefs[dnaStyleStrutsShape_prefs_key] = shape

    def change_dnaStyleAxisShape(self, shape):
        """
        Changes DNA Style strands shape.

        @param shape: The shape mode:
                    - 0 = none (hidden)
                    - 1 = wide tube
                    - 2 = narrow tube

        @type shape: int
        """
        env.prefs[dnaStyleAxisShape_prefs_key] = shape

    def change_dnaStyleBasesShape(self, shape):
        """
        Changes DNA Style strands shape.

        @param shape: The shape mode:
                    - 0 = none (hidden)
                    - 1 = spheres
                    - 2 = cartoon-like

        @type shape: int
        """
        env.prefs[dnaStyleBasesShape_prefs_key] = shape

    def change_dnaStyleStrandsScale(self, scale_factor):
        """
        @param scale_factor: The strands scale factor.
        @type  scale_factor: float
        """
        env.prefs[dnaStyleStrandsScale_prefs_key] = scale_factor
        #self.update_dnaStyleStrandsScale()

    def update_dnaStyleStrandsScale(self):
        """
        Updates the DNA Style Strands Scale spin box.
        """
        # Set strands scale.

        self.dnaStyleStrandsScaleSpinBox.setValue(
            float(env.prefs[dnaStyleStrandsScale_prefs_key]))

    def change_dnaStyleStrutsScale(self, scale_factor):
        """
        @param scale_factor: The struts scale factor.
        @type  scale_factor: float
        """
        env.prefs[dnaStyleStrutsScale_prefs_key] = scale_factor

    def change_dnaStyleAxisScale(self, scale_factor):
        """
        @param scale_factor: The axis scale factor.
        @type  scale_factor: float
        """
        env.prefs[dnaStyleAxisScale_prefs_key] = scale_factor

    def change_dnaStyleBasesScale(self, scale_factor):
        """
        @param scale_factor: The bases scale factor.
        @type  scale_factor: float
        """
        env.prefs[dnaStyleBasesScale_prefs_key] = scale_factor
        #self.update_dnaStyleBasesScale()

    def update_dnaStyleBasesScale(self):
        """
        Updates the DNA Style bases scale spin box.
        """
        # Set axis scale.
        self.dnaStyleBasesScaleSpinBox.setValue(
            float(env.prefs[dnaStyleBasesScale_prefs_key]))

    def change_dnaBaseIndicatorsAngle(self, angle):
        """
        @param angle: The angular threshold for DNA base indicators.
        @type  angle: double
        """
        print "angle (set) = ", angle
        env.prefs[dnaBaseIndicatorsAngle_prefs_key] = angle
        self.update_dnaBaseIndicatorsAngle()

    def update_dnaBaseIndicatorsAngle(self):
        """
        Updates the DNA base orientation indicators angular threshold spinbox.
        """
        self.dnaBaseOrientationIndicatorsThresholdSpinBox.setValue(
            float(env.prefs[dnaBaseIndicatorsAngle_prefs_key]))

    def change_dnaBaseIndicatorsDistance(self, distance):
        """
        @param distance: The distance threshold for DNA base indicators.
        @type  distance: double
        """
        env.prefs[dnaBaseIndicatorsDistance_prefs_key] = distance
        self.update_dnaBaseIndicatorsDistance()

    def update_dnaBaseIndicatorsDistance(self):
        """
        Updates the DNA base orientation indicators distance threshold spinbox.
        """
        self.dnaBaseOrientationIndicatorsTerminalDistanceSpinBox.setValue(
            int(env.prefs[dnaBaseIndicatorsDistance_prefs_key]))

    def change_dnaStyleStrandsArrows(self, shape):
        """
        Changes DNA Style strands shape.

        @param shape: The shape mode:
                    - 0 = none (hidden)

        @type shape: int
        """
        env.prefs[dnaStyleStrandsArrows_prefs_key] = shape

    def change_dnaStyleAxisEndingStyle(self, shape):
        """
        Changes DNA Style strands ends.

        @param shape: The ending style shape:
                    - 0 = flat
                    - 1 = taper beginning
                    - 2 = taper ending
                    - 3 = taper both ends
                    - 4 = spherical

        @type shape: int
        """
        env.prefs[dnaStyleAxisEndingStyle_prefs_key] = shape

    def toggle_dnaDisplayStrandLabelsGroupBox(self, state):
        """
        Toggles DNA Strand Labels GroupBox.

        @param state: Is the GroupBox enabled?
                    - True = on
                    - False = off
        @type state: boolean
        """
        env.prefs[dnaStrandLabelsEnabled_prefs_key] = state

    def toggle_dnaDisplayBaseOrientationIndicatorsGroupBox(self, state):
        """
        Toggles DNA Base Orientation Indicators GroupBox.

        @param state: Is the GroupBox enabled?
                    - True = on
                    - False = off
        @type state: boolean
        """
        env.prefs[dnaBaseIndicatorsEnabled_prefs_key] = state

    def toggle_dnaDisplayBaseOrientationInvIndicatorsCheckBox(self, state):
        """
        Toggles DNA Base Orientation Inverse Indicators CheckBox.

        @param state: Is the CheckBox enabled?
                    - True = on
                    - False = off
        @type state: boolean
        """
        env.prefs[dnaBaseInvIndicatorsEnabled_prefs_key] = state

    def toggle_dnaStyleBasesDisplayLettersCheckBox(self, state):
        """
        Toggles DNA Base Letters.

        @param state: Is the CheckBox enabled?
                    - True = on
                    - False = off
        @type state: boolean
        """
        env.prefs[dnaStyleBasesDisplayLetters_prefs_key] = state

    def change_dnaBaseOrientIndicatorsPlane(self, idx):
        """
        Slot for the "Plane" combobox for changing the
        DNA base indicators plane.
        """
        env.prefs[dnaBaseIndicatorsPlaneNormal_prefs_key] = idx

    def change_dnaBaseIndicatorsColor(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA base indicators color.
        """
        self.usual_change_color( dnaBaseIndicatorsColor_prefs_key )

    def change_dnaBaseInvIndicatorsColor(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA base inverse indicators color.
        """
        self.usual_change_color( dnaBaseInvIndicatorsColor_prefs_key )

    def change_dnaStrandLabelsColor(self):
        """
        Slot for the I{Choose...} button for changing the
        DNA strand labels color.
        """
        self.usual_change_color( dnaStrandLabelsColor_prefs_key )

    def change_dnaStrandLabelsColorMode(self, mode):
        """
        Changes DNA Style strand labels color mode.

        @param mode: The color mode:
                    - 0 = same as chunk
                    - 1 = black
                    - 2 = white
                    - 3 = custom

        @type mode: int
        """
        env.prefs[dnaStrandLabelsColorMode_prefs_key] = mode

    # == End of slot methods for "DNA" page widgets ==

    # == Slot methods for "Lighting" page widgets ==

    def change_lighting(self, specularityValueJunk = None):
        """
        Updates glpane lighting using the current lighting parameters from
        the light checkboxes and sliders. This is also the slot for the light
        sliders.
        @param specularityValueJunk: This value from the slider is not used
                                     We are interested in valueChanged signal
                                     only
        @type specularityValueJunk = int or None

        """

        light_num = self.light_combobox.currentIndex()

        light1, light2, light3 = self.glpane.getLighting()

        a = self.light_ambient_slider.value() * .01
        d = self.light_diffuse_slider.value() * .01
        s = self.light_specularity_slider.value()  * .01

        self.light_ambient_linedit.setText(str(a))
        self.light_diffuse_linedit.setText(str(d))
        self.light_specularity_linedit.setText(str(s))

        new_light = [  self.light_color, a, d, s, \
                       float(str(self.light_x_linedit.text())), \
                       float(str(self.light_y_linedit.text())), \
                       float(str(self.light_z_linedit.text())), \
                       self.light_checkbox.isChecked()]

        # This is a kludge.  I'm certain there is a more elegant way.  Mark 051204.
        if light_num == 0:
            self.glpane.setLighting([new_light, light2, light3])
        elif light_num == 1:
            self.glpane.setLighting([light1, new_light, light3])
        elif light_num == 2:
            self.glpane.setLighting([light1, light2, new_light])
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

    def change_light_color(self):
        """
        Slot for light color "Choose" button.  Saves the new color in the
        prefs db.

        Changes the current Light color in the graphics area and the light
        color swatch in the UI.
        """
        self.usual_change_color(self.current_light_key)
        self.light_color = env.prefs[self.current_light_key]
        self.save_lighting()

    def update_light_combobox_items(self):
        """Updates all light combobox items with '(On)' or '(Off)' label.
        """
        for i in range(3):
            if self.lights[i][7]:
                txt = "%d (On)" % (i+1)
            else:
                txt = "%d (Off)" % (i+1)
            self.light_combobox.setItemText(i, txt)

    def toggle_light(self, on):
        """
        Slot for light 'On' checkbox.
        It updates the current item in the light combobox with '(On)' or
        '(Off)' label.
        """
        if on:
            txt = "%d (On)" % (self.light_combobox.currentIndex()+1)
        else:
            txt = "%d (Off)" % (self.light_combobox.currentIndex()+1)
        self.light_combobox.setItemText(self.light_combobox.currentIndex(),txt)

        self.save_lighting()

    def save_lighting(self):
        """
        Saves lighting parameters (but not material specularity parameters)
        to pref db. This is also the slot for light sliders (only when
        released).
        """
        self.change_lighting()
        self.glpane.saveLighting()

    def toggle_material_specularity(self, val):
        """
        This is the slot for the Material Specularity Enabled checkbox.
        """
        env.prefs[material_specular_highlights_prefs_key] = val

    def change_material_finish(self, finish):
        """
        This is the slot for the Material Finish slider.
        'finish' is between 0 and 100.
        Saves finish parameter to pref db.
        """
        # For whiteness, the stored range is 0.0 (Metal) to 1.0 (Plastic).
        # The Qt slider range is 0 - 100, so we multiply by 100 to set the slider.  Mark. 051129.
        env.prefs[material_specular_finish_prefs_key] = float(finish * 0.01)
        self.ms_finish_linedit.setText(str(finish * 0.01))

    def change_material_shininess(self, shininess):
        """
        This is the slot for the Material Shininess slider.
        'shininess' is between 15 (low) and 60 (high).
        """
        env.prefs[material_specular_shininess_prefs_key] = float(shininess)
        self.ms_shininess_linedit.setText(str(shininess))

    def change_material_brightness(self, brightness):
        """
        This is the slot for the Material Brightness slider.
        'brightness' is between 0 (low) and 100 (high).
        """
        env.prefs[material_specular_brightness_prefs_key] = float(brightness * 0.01)
        self.ms_brightness_linedit.setText(str(brightness * 0.01))

    def change_material_finish_start(self):
        if debug_sliders: print "Finish slider pressed"
        env.prefs.suspend_saving_changes() #bruce 051205 new prefs feature - keep updating to glpane but not (yet) to disk

    def change_material_finish_stop(self):
        if debug_sliders: print "Finish slider released"
        env.prefs.resume_saving_changes() #bruce 051205 new prefs feature - save accumulated changes now

    def change_material_shininess_start(self):
        if debug_sliders: print "Shininess slider pressed"
        env.prefs.suspend_saving_changes()

    def change_material_shininess_stop(self):
        if debug_sliders: print "Shininess slider released"
        env.prefs.resume_saving_changes()

    def change_material_brightness_start(self):
        if debug_sliders: print "Brightness slider pressed"
        env.prefs.suspend_saving_changes()

    def change_material_brightness_stop(self):
        if debug_sliders: print "Brightness slider released"
        env.prefs.resume_saving_changes()

    def reset_lighting(self):
        """
        Slot for Reset button.
        """
        # This has issues.
        # I intend to remove the Reset button for A7.  Confirm with Bruce.  Mark 051204.
        self._setup_material_group(reset = True)
        self._updatePage_Lighting(self.original_lights)
        self.glpane.saveLighting()

    def restore_default_lighting(self):
        """
        Slot for Restore Defaults button.
        """

        self.glpane.restoreDefaultLighting()

        # Restore defaults for the Material Specularity properties
        env.prefs.restore_defaults([
            material_specular_highlights_prefs_key,
            material_specular_shininess_prefs_key,
            material_specular_finish_prefs_key,
            material_specular_brightness_prefs_key, #bruce 051203 bugfix
        ])

        self._updatePage_Lighting()
        self.save_lighting()

    ########## End of slot methods for "Lighting" page widgets ###########

    ########## Slot methods for "Plug-ins" page widgets ################

    def choose_gamess_path(self):
        """
        Slot for GAMESS path "Choose" button.
        """
        gamess_exe = get_filename_and_save_in_prefs(self,
                                                    gmspath_prefs_key,
                                                    'Choose GAMESS Executable')

        if gamess_exe:
            self.gamess_path_lineedit.setText(env.prefs[gmspath_prefs_key])

    def set_gamess_path(self, newValue):
        """
        Slot for GAMESS path line editor.
        """
        env.prefs[gamess_path_prefs_key] = str_or_unicode(newValue)

    def enable_gamess(self, enable = True):
        """
        Enables/disables GAMESS plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        if enable:
            self.gamess_path_lineedit.setEnabled(1)
            self.gamess_choose_btn.setEnabled(1)
            env.prefs[gamess_enabled_prefs_key] = True

        else:
            self.gamess_path_lineedit.setEnabled(0)
            self.gamess_choose_btn.setEnabled(0)
            #self.gamess_path_lineedit.setText("")
            #env.prefs[gmspath_prefs_key] = ''
            env.prefs[gamess_enabled_prefs_key] = False

    # GROMACS slots #######################################

    def choose_gromacs_path(self):
        """
        Slot for GROMACS path "Choose" button.
        """

        mdrun_executable = \
                         get_filename_and_save_in_prefs(self,
                                                        gromacs_path_prefs_key,
                                                        'Choose mdrun executable (GROMACS)')

        if mdrun_executable:
            self.gromacs_path_lineedit.setText(env.prefs[gromacs_path_prefs_key])

    def set_gromacs_path(self, newValue):
        """
        Slot for GROMACS path line editor.
        """
        env.prefs[gromacs_path_prefs_key] = str_or_unicode(newValue)

    def enable_gromacs(self, enable = True):
        """
        If True, GROMACS path is set in Preferences>Plug-ins

        @param enable: Is the path set?
        @type  enable: bool
        """

        state = self.gromacs_checkbox.checkState()
        if enable:
            if (state != Qt.Checked):
                self.gromacs_checkbox.setCheckState(Qt.Checked)
            self.gromacs_path_lineedit.setEnabled(True)
            self.gromacs_choose_btn.setEnabled(True)
            env.prefs[gromacs_enabled_prefs_key] = True

            # Sets the GROMACS (executable) path to the standard location, if it exists.
            if not env.prefs[gromacs_path_prefs_key]:
                env.prefs[gromacs_path_prefs_key] = get_default_plugin_path( \
                    "C:\\GROMACS_3.3.3\\bin\\mdrun.exe", \
                    "/Applications/GROMACS_3.3.3/bin/mdrun",
                    "/usr/local/GROMCAS_3.3.3/bin/mdrun")

            self.gromacs_path_lineedit.setText(env.prefs[gromacs_path_prefs_key])

        else:
            if (state != Qt.Unchecked):
                self.gromacs_checkbox.setCheckState(Qt.Unchecked)
            self.gromacs_path_lineedit.setEnabled(False)
            self.gromacs_choose_btn.setEnabled(False)
            #self.gromacs_path_lineedit.setText("")
            #env.prefs[gromacs_path_prefs_key] = ''
            env.prefs[gromacs_enabled_prefs_key] = False

    # cpp slots #######################################

    def choose_cpp_path(self):
        """
        Sets the path to cpp (C pre-processor)
        """

        cpp_executable = get_filename_and_save_in_prefs(self,
                                                        cpp_path_prefs_key,
                                                        'Choose cpp Executable (used by GROMACS)')

        if cpp_executable:
            self.cpp_path_lineedit.setText(env.prefs[cpp_path_prefs_key])

    def set_cpp_path(self, newValue):
        """
        Slot for cpp path line editor.
        """
        env.prefs[cpp_path_prefs_key] = str_or_unicode(newValue)

    def enable_cpp(self, enable = True):
        """
        Enables/disables cpp plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        state = self.cpp_checkbox.checkState()
        if enable:
            if (state != Qt.Checked):
                self.cpp_checkbox.setCheckState(Qt.Checked)
            self.cpp_path_lineedit.setEnabled(True)
            self.cpp_choose_btn.setEnabled(True)
            env.prefs[cpp_enabled_prefs_key] = True

            # Sets the cpp path to the standard location, if it exists.
            if not env.prefs[cpp_path_prefs_key]:
                env.prefs[cpp_path_prefs_key] = get_default_plugin_path( \
                    "C:\\GROMACS_3.3.3\\MCPP\\bin\\mcpp.exe", \
                    "/Applications/GROMACS_3.3.3/mcpp/bin/mcpp", \
                    "/usr/local/GROMACS_3.3.3/mcpp/bin/mcpp")

            self.cpp_path_lineedit.setText(env.prefs[cpp_path_prefs_key])

        else:
            if (state != Qt.Unchecked):
                self.cpp_checkbox.setCheckState(Qt.Unchecked)
            self.cpp_path_lineedit.setEnabled(False)
            self.cpp_choose_btn.setEnabled(False)
            #self.cpp_path_lineedit.setText("")
            #env.prefs[cpp_path_prefs_key] = ''
            env.prefs[cpp_enabled_prefs_key] = False

    # NanoVision-1 slots #######################################

    def choose_nv1_path(self):
        """
        Slot for NanoVision-1 path "Choose" button.
        """

        nv1_executable = get_filename_and_save_in_prefs(self,
                                                        nv1_path_prefs_key,
                                                        'Choose NanoVision-1 Executable')

        if nv1_executable:
            self.nv1_path_lineedit.setText(env.prefs[nv1_path_prefs_key])

    def set_nv1_path(self, newValue):
        """
        Slot for NanoVision-1 path line editor.
        """
        env.prefs[nv1_path_prefs_key] = str_or_unicode(newValue)

    def enable_nv1(self, enable = True):
        """
        If True, NV1 path is set in Preferences>Plug-ins

        @param enable: Is the path set?
        @type  enable: bool
        """

        state = self.nv1_checkbox.checkState()
        if enable:
            if (state != Qt.Checked):
                self.nv1_checkbox.setCheckState(Qt.Checked)
            self.nv1_path_lineedit.setEnabled(True)
            self.nv1_choose_btn.setEnabled(True)
            env.prefs[nv1_enabled_prefs_key] = True

            # Sets the NV1 (executable) path to the standard location, if it exists.
            if not env.prefs[nv1_path_prefs_key]:
                env.prefs[nv1_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\Nanorex\\NanoVision-1\\NanoVision-1.exe", \
                    "/Applications/Nanorex/NanoVision-1 0.1.0/NanoVision-1.app", \
                    "/usr/local/Nanorex/NanoVision-1 0.1.0/NanoVision-1")

            self.nv1_path_lineedit.setText(env.prefs[nv1_path_prefs_key])

        else:
            if (state != Qt.Unchecked):
                self.nv1_checkbox.setCheckState(Qt.Unchecked)
            self.nv1_path_lineedit.setEnabled(False)
            self.nv1_choose_btn.setEnabled(False)
            #self.nv1_path_lineedit.setText("")
            #env.prefs[nv1_path_prefs_key] = ''
            env.prefs[nv1_enabled_prefs_key] = False

    # QuteMolX slots #######################################

    def choose_qutemol_path(self):
        """
        Slot for QuteMolX path "Choose" button.
        """
        qp = get_filename_and_save_in_prefs(self,
                                            qutemol_path_prefs_key,
                                            'Choose QuteMolX Executable')

        if qp:
            self.qutemol_path_lineedit.setText(qp)

    def set_qutemol_path(self, newValue):
        """
        Slot for QuteMol path line editor.
        """
        env.prefs[qutemol_path_prefs_key] = str_or_unicode(newValue)

    def enable_qutemol(self, enable = True):
        """
        Enables/disables QuteMolX plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        if enable:
            self.qutemol_path_lineedit.setEnabled(1)
            self.qutemol_choose_btn.setEnabled(1)
            env.prefs[qutemol_enabled_prefs_key] = True

            # Sets the QuteMolX (executable) path to the standard location, if it exists.
            if not env.prefs[qutemol_path_prefs_key]:
                env.prefs[qutemol_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\Nanorex\\QuteMolX\\QuteMolX.exe", \
                    "/Applications/Nanorex/QuteMolX 0.5.0/QuteMolX.app", \
                    "/usr/local/Nanorex/QuteMolX 0.5.0/QuteMolX")

            self.qutemol_path_lineedit.setText(env.prefs[qutemol_path_prefs_key])

        else:
            self.qutemol_path_lineedit.setEnabled(0)
            self.qutemol_choose_btn.setEnabled(0)
            #self.qutemol_path_lineedit.setText("")
            #env.prefs[qutemol_path_prefs_key] = ''
            env.prefs[qutemol_enabled_prefs_key] = False

    # NanoHive-1 slots #####################################

    def choose_nanohive_path(self):
        """
        Slot for Nano-Hive path "Choose" button.
        """

        nh = get_filename_and_save_in_prefs(self,
                                            nanohive_path_prefs_key,
                                            'Choose Nano-Hive Executable')

        if nh:
            self.nanohive_path_lineedit.setText(nh)

    def set_nanohive_path(self, newValue):
        """
        Slot for NanoHive path line editor.
        """
        env.prefs[nanohive_path_prefs_key] = str_or_unicode(newValue)

    def enable_nanohive(self, enable = True):
        """
        Enables/disables NanoHive-1 plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool

        @attention: This is disabled since the NH1 plugin doesn't work yet.
        """
        if enable:
            self.nanohive_path_lineedit.setEnabled(1)
            self.nanohive_choose_btn.setEnabled(1)
            # Leave Nano-Hive action button/menu hidden for A7.  Mark 2006-01-04.
            # self.w.simNanoHiveAction.setVisible(1)

            # Sets the Nano-Hive (executable) path to the standard location, if it exists.
            if not env.prefs[nanohive_path_prefs_key]:
                env.prefs[nanohive_path_prefs_key] = get_default_plugin_path(
                    "C:\\Program Files\\Nano-Hive\\bin\\win32-x86\\NanoHive.exe", \
                    "/usr/local/bin/NanoHive", \
                    "/usr/local/bin/NanoHive")


            env.prefs[nanohive_enabled_prefs_key] = True
            self.nanohive_path_lineedit.setText(env.prefs[nanohive_path_prefs_key])

            # Create the Nano-Hive dialog widget.
            # Not needed for A7.  Mark 2006-01-05.
            #if not self.w.nanohive:
            #    from NanoHive import NanoHive
            #    self.w.nanohive = NanoHive(self.assy)

        else:
            self.nanohive_path_lineedit.setEnabled(0)
            self.nanohive_choose_btn.setEnabled(0)
            self.w.nanohive = None
            self.w.simNanoHiveAction.setVisible(0)
            #self.nanohive_path_lineedit.setText("")
            #env.prefs[nanohive_path_prefs_key] = ''
            env.prefs[nanohive_enabled_prefs_key] = False

    # POV-Ray slots #####################################

    def choose_povray_path(self):
        """
        Slot for POV-Ray path "Choose" button.
        """
        povray_exe = get_filename_and_save_in_prefs(self,
                                                    povray_path_prefs_key,
                                                    'Choose POV-Ray Executable')

        if povray_exe:
            self.povray_path_lineedit.setText(povray_exe)

    def set_povray_path(self, newValue):
        """
        Slot for POV-Ray path line editor.
        """
        env.prefs[povray_path_prefs_key] = str_or_unicode(newValue)

    def enable_povray(self, enable = True):
        """
        Enables/disables POV-Ray plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        if enable:
            self.povray_path_lineedit.setEnabled(1)
            self.povray_choose_btn.setEnabled(1)
            env.prefs[povray_enabled_prefs_key] = True

            # Sets the POV-Ray (executable) path to the standard location, if it exists.
            if not env.prefs[povray_path_prefs_key]:
                env.prefs[povray_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\POV-Ray for Windows v3.6\\bin\\pvengine.exe", \
                    "/usr/local/bin/pvengine", \
                    "/usr/local/bin/pvengine")

            self.povray_path_lineedit.setText(env.prefs[povray_path_prefs_key])

        else:
            self.povray_path_lineedit.setEnabled(0)
            self.povray_choose_btn.setEnabled(0)
            #self.povray_path_lineedit.setText("")
            #env.prefs[povray_path_prefs_key] = ''
            env.prefs[povray_enabled_prefs_key] = False
        self._update_povdir_enables() #bruce 060710

    # MegaPOV slots #####################################

    def choose_megapov_path(self):
        """
        Slot for MegaPOV path "Choose" button.
        """
        megapov_exe = get_filename_and_save_in_prefs(self, megapov_path_prefs_key, 'Choose MegaPOV Executable')

        if megapov_exe:
            self.megapov_path_lineedit.setText(megapov_exe)

    def set_megapov_path(self, newValue):
        """
        Slot for MegaPOV path line editor.
        """
        env.prefs[megapov_path_prefs_key] = str_or_unicode(newValue)

    def enable_megapov(self, enable = True):
        """
        Enables/disables MegaPOV plugin.

        @param enable: Enabled when True. Disables when False.
        @type  enable: bool
        """
        if enable:
            self.megapov_path_lineedit.setEnabled(1)
            self.megapov_choose_btn.setEnabled(1)
            env.prefs[megapov_enabled_prefs_key] = True

            # Sets the MegaPOV (executable) path to the standard location, if it exists.
            if not env.prefs[megapov_path_prefs_key]:
                env.prefs[megapov_path_prefs_key] = get_default_plugin_path( \
                    "C:\\Program Files\\POV-Ray for Windows v3.6\\bin\\megapov.exe", \
                    "/usr/local/bin/megapov", \
                    "/usr/local/bin/megapov")

            self.megapov_path_lineedit.setText(env.prefs[megapov_path_prefs_key])

        else:
            self.megapov_path_lineedit.setEnabled(0)
            self.megapov_choose_btn.setEnabled(0)
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
        self.povdir_checkbox.setEnabled(enable_checkbox)
        self.povdir_lbl.setEnabled(enable_checkbox)
        enable_edits = enable_checkbox and env.prefs[povdir_enabled_prefs_key]
            # note: that prefs value should and presumably does agree with self.povdir_checkbox.isChecked()
        self.povdir_lineedit.setEnabled(enable_edits)
        self.povdir_choose_btn.setEnabled(enable_edits)
        return

    def enable_povdir(self, enable = True): #bruce 060710
        """
        Slot method for povdir checkbox.
        povdir is enabled when enable = True.
        povdir is disabled when enable = False.
        """
        env.prefs[povdir_enabled_prefs_key] = not not enable
        self._update_povdir_enables()
##        self.povdir_lineedit.setText(env.prefs[povdir_path_prefs_key])
        return

    def set_povdir(self): #bruce 060710
        """
        Slot for Pov include dir "Choose" button.
        """
        povdir_path = get_dirname_and_save_in_prefs(self, povdir_path_prefs_key, 'Choose Custom POV-Ray Include directory')
        # note: return value can't be ""; if user cancels, value is None;
        # to set "" you have to edit the lineedit text directly, but this doesn't work since
        # no signal is caught to save that into the prefs db!
        # ####@@@@ we ought to catch that signal... is it returnPressed?? would that be sent if they were editing it, then hit ok?
        # or if they clicked elsewhere? (currently that fails to remove focus from the lineedits, on Mac, a minor bug IMHO)
        # (or uncheck the checkbox for the same effect). (#e do we want a "clear" button, for A8.1?)

        if povdir_path:
            self.povdir_lineedit.setText(env.prefs[povdir_path_prefs_key])
            # the function above already saved it in prefs, under the same condition
        return

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

    ########## Slot methods for "Undo" (former name "Caption") page widgets ################

    def change_undo_stack_memory_limit(self, mb_val):
        """
        Slot for 'Undo Stack Memory Limit' spinbox.
        Sets the RAM limit for the Undo Stack.
        <mb-val> can range from 0-99999 (MB).
        """
        env.prefs[undoStackMemoryLimit_prefs_key] = mb_val

    def change_historyHeight(self, value):
        """
        Slot for  history height spinbox.
        """
        env.prefs[ historyHeight_prefs_key] = value

    ########## End of slot methods for "Undo" page widgets ###########

    ########## Start slot methods for "ToolTips" page widgets ###########
    def change_dynamicToolTipAtomDistancePrecision(self, value):
        """
        Update the atom distance precision for the dynamic tool tip.
        """
        env.prefs[ dynamicToolTipAtomDistancePrecision_prefs_key ] = value

    def change_dynamicToolTipBendAnglePrecision(self, value):
        """
        Update the bend angle precision for the dynamic tool tip.
        """
        env.prefs[ dynamicToolTipBendAnglePrecision_prefs_key ] = value

    ########## End of slot methods for "ToolTips" page widgets ###########

    ########## Slot methods for "Window" (former name "Caption") page widgets ################

    #e there are some new slot methods for this in other places, which should be refiled here. [bruce 050811]

    def change_window_size(self, val = 0):
        """
        Slot for both the width and height spinboxes that change the current
        window size.

        Also called from other slots to change the window size based on new
        values in spinboxes. <val> is not used.
        """
        w = self.current_width_spinbox.value()
        h = self.current_height_spinbox.value()
        self.w.resize(w,h)

    def update_saved_size(self, w, h):
        """
        Update the saved width and height text.
        """
        self.saved_width_lineedit.setText(QString(str(w) + " pixels"))
        self.saved_height_lineedit.setText(QString(str(h) + " pixels"))

    def save_current_win_pos_and_size(self): #bruce 051218; see also debug.py's _debug_save_window_layout
        from utilities.prefs_constants import mainwindow_geometry_prefs_key_prefix
        keyprefix = mainwindow_geometry_prefs_key_prefix
        save_window_pos_size( self.w, keyprefix) # prints history message
        size = self.w.size()
        self.update_saved_size(size.width(), size.height())
        return

    def restore_saved_size(self):
        """
        Restore the window size, but not the position, from the prefs db.
        """
        from utilities.prefs_constants import mainwindow_geometry_prefs_key_prefix
        keyprefix = mainwindow_geometry_prefs_key_prefix
        pos, size = _get_prefs_for_window_pos_size( self.w, keyprefix)
        w = size[0]
        h = size[1]
        self.update_saved_size(w, h)
        self.current_width_spinbox.setValue(w)
        self.current_height_spinbox.setValue(h)
        self.change_window_size()
        return

    def change_use_selected_font(self, use_selected_font):
        """
        Slot for "Use Selected Font" checkbox on the groupbox.
        Called when the checkbox is toggled.
        """
        env.prefs[useSelectedFont_prefs_key] = use_selected_font
        self.set_font()
        return

    def change_font(self, font):
        """
        Slot for the Font combobox.
        Called whenever the font is changed.
        """
        env.prefs[displayFont_prefs_key] = str_or_unicode(font.family())
        self.set_font()
        return

    def change_fontsize(self, pointsize):
        """
        Slot for the Font size spinbox.
        """
        env.prefs[displayFontPointSize_prefs_key] = pointsize
        self.set_font()
        return

    def change_selected_font_to_default_font(self):
        """
        Slot for "Make the selected font the default font" button.
        The default font will be displayed in the Font and Size
        widgets.
        """
        font = self.w.defaultFont
        env.prefs[displayFont_prefs_key] = str_or_unicode(font.family())
        env.prefs[displayFontPointSize_prefs_key] = font.pointSize()
        self.set_font_widgets(setFontFromPrefs = True) # Also sets the current display font.

        if debug_flags.atom_debug:
            print "change_selected_font_to_default_font(): " \
                  "Button clicked. Default font: ", font.family(), \
                  ", size=", font.pointSize()
        return

    def set_font_widgets(self, setFontFromPrefs = True):
        """
        Update font widgets based on font prefs.
        Unconnects signals from slots, updates widgets, then reconnects slots.

        @param setFontFromPrefs: when True (default), sets the display font
                                (based on font prefs).
        @type  setFontFromPrefs: bool
        """

        if debug_flags.atom_debug:
            print "set_font_widgets(): Here!"


        if env.prefs[displayFont_prefs_key] == "defaultFont":
            # Set the font and point size prefs to the application's default font.
            # This code only called the first time NE1 is run (or the prefs db does not exist)
            font = self.w.defaultFont
            font_family = str_or_unicode(font.family())
                # Note: when this used str() rather than str_or_unicode(),
                # it prevented NE1 from running on some international systems
                # (when it had never run before and needed to initialize this
                #  prefs value).
                # We can now reproduce the bug (see bug 2883 for details),
                # so I am using str_or_unicode to try to fix it. [bruce 080529]
            font_size = font.pointSize()
            env.prefs[displayFont_prefs_key] = font_family
            env.prefs[displayFontPointSize_prefs_key] = font_size
            if debug_flags.atom_debug:
                print "set_font_widgets(): No prefs db. " \
                      "Using default font: ", font.family(), \
                      ", size=", font.pointSize()

        else:
            font_family = env.prefs[displayFont_prefs_key]
            font_size = env.prefs[displayFontPointSize_prefs_key]
            font = QFont(font_family, font_size)

        self.disconnect(self.selectedFontGroupBox, SIGNAL("toggled(bool)"), self.change_use_selected_font)
        self.disconnect(self.fontComboBox, SIGNAL("currentFontChanged (const QFont &)"), self.change_font)
        self.disconnect(self.fontSizeSpinBox, SIGNAL("valueChanged(int)"), self.change_fontsize)
        self.disconnect(self.makeDefaultFontPushButton, SIGNAL("clicked()"), self.change_selected_font_to_default_font)

        self.selectedFontGroupBox.setChecked(env.prefs[useSelectedFont_prefs_key]) # Generates signal!
        self.fontComboBox.setCurrentFont(font) # Generates signal!
        self.fontSizeSpinBox.setValue(font_size) # Generates signal!

        self.connect(self.selectedFontGroupBox, SIGNAL("toggled(bool)"), self.change_use_selected_font)
        self.connect(self.fontComboBox, SIGNAL("currentFontChanged (const QFont &)"), self.change_font)
        self.connect(self.fontSizeSpinBox, SIGNAL("valueChanged(int)"), self.change_fontsize)
        self.connect(self.makeDefaultFontPushButton, SIGNAL("clicked()"), self.change_selected_font_to_default_font)

        if setFontFromPrefs:
            self.set_font()
        return

    def set_font(self):
        """
        Set the current display font using the font prefs.
        """

        use_selected_font = env.prefs[useSelectedFont_prefs_key]

        if use_selected_font:
            font = self.fontComboBox.currentFont()
            font_family = str_or_unicode(font.family())
            fontsize = self.fontSizeSpinBox.value()
            font.setPointSize(fontsize)
            env.prefs[displayFont_prefs_key] = font_family
            env.prefs[displayFontPointSize_prefs_key] = fontsize
            if debug_flags.atom_debug:
                print "set_font(): Using selected font: ", font.family(), ", size=", font.pointSize()

        else: # Use default font
            font = self.w.defaultFont
            if debug_flags.atom_debug:
                print "set_font(): Using default font: ", font.family(), ", size=", font.pointSize()

        # Set font
        self.w.setFont(font)
        return

    def set_caption_fullpath(self, val): #bruce 050810 revised this
        # there is now a separate connection which sets the pref, so this is not needed:
        ## self.win.caption_fullpath = val
        # and there is now a Formula in MWsemantics which makes the following no longer needed:
        ## self.win.update_mainwindow_caption(self.win.assy.has_changed())
        pass

    def update_number_spinbox_valueChanged(self,a0):
        # some day we'll use this to set a user preferences, for now it's a no-op
        pass

    ########## End of slot methods for "Window" page widgets ###########

    ########## Slot methods for top level widgets ################

    def show(self, pagename = ""):
        """
        Display the Preferences dialog with page I{pagename}.

        @param pagename: Name of the Preferences page. Default is "General".
        @type  pagename: string
        """
        self.showPage(pagename)

        # Must use exec_() and not show() with self.modal=True. I tried it and
        # it doesn't work whenever the user is prompted by NE1 to enable
        # a plug-in via the Preferences dialog. -Mark 2008-05-22
        self.exec_()
        return

    def showPage(self, pagename = ""):
        """
        Show the current page of the Preferences dialog. If no page is
        selected from the Category tree widget, show the "General" page.

        @param pagename: Name of the Preferences page. Default is "General".
                         Only names found in self.pagenameList are allowed.
        @type  pagename: string

        @note: This is the slot method for the "Category" QTreeWidget.
        """

        if not pagename:
            selectedItemsList = self.categoryTreeWidget.selectedItems()
            if selectedItemsList:
                selectedItem = selectedItemsList[0]
                pagename = str(selectedItem.text(0))
            else:
                pagename = 'General'

        # Strip whitespaces, commas and dashes from pagename just before
        # checking for it in self.pagenameList.
        pagename = pagename.replace(" ", "")
        pagename = pagename.replace(",", "")
        pagename = pagename.replace("-", "")

        if not pagename in self.pagenameList:
            msg = 'Preferences page unknown: pagename =%s\n' \
                'pagename must be one of the following:\n%r\n' \
                % (pagename, self.pagenameList)
            print_compact_traceback(msg)

        try:
            # Show page <pagename>.
            self.prefsStackedWidget.setCurrentIndex(self.pagenameList.index(pagename))
        except:
            print_compact_traceback("Bug in showPage() ignored: ")

        self.setWindowTitle("Preferences - %s" % pagename)
        return

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
