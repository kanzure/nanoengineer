# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
UserPrefs.py

@author: Mark
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Created by Mark.

Modified somewhat by Bruce 050805 for bond color prefs,
and 050810 to fix bugs 785 (partly in MWsemantics.py) and 881 for Alpha6.

Many mods since then by Mark, Bruce, Ninad, perhaps others.
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

from outtakes.UserPrefsDialog import Ui_UserPrefsDialog
import foundation.preferences as preferences
from utilities.debug import print_compact_traceback
from utilities.debug_prefs import debug_pref, Choice_boolean_False
import foundation.env as env
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf
from widgets.widget_helpers import double_fixup
from widgets.prefs_widgets import connect_colorpref_to_colorframe, connect_checkbox_with_boolean_pref
from utilities import debug_flags
from platform_dependent.PlatformDependent import screen_pos_size
from platform_dependent.PlatformDependent import get_rootdir
from platform_dependent.Paths import get_default_plugin_path
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

# Mouse wheel prefs
from utilities.prefs_constants import mouseWheelDirection_prefs_key
from utilities.prefs_constants import zoomInAboutScreenCenter_prefs_key
from utilities.prefs_constants import zoomOutAboutScreenCenter_prefs_key

# DNA prefs
from utilities.prefs_constants import bdnaBasesPerTurn_prefs_key
from utilities.prefs_constants import bdnaRise_prefs_key
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

    filename = str(QFileDialog.getOpenFileName(
        parent,
        caption,
        get_rootdir(), # '/' on Mac or Linux, something else on Windows
    ))

    if not filename: # Cancelled.
        return None

    # Save filename in prefs db.
    prefs = preferences.prefs_context()
    prefs[prefs_key] = os.path.normpath(str(filename))

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

    filename = str(QFileDialog.getExistingDirectory(
        parent,### if this was None, it might fix the Mac bug where you can't drag the dialog around [bruce 060710]
        caption,
        get_rootdir(), # '/' on Mac or Linux -- maybe not the best choice if they've chosen one before?
    ))

    if not filename: # Cancelled.
        return None

    # Save filename in prefs db.
    prefs = preferences.prefs_context()
    prefs[prefs_key] = str(filename)

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
    ((x0,y0),(w,h)) = screen
    x1 = x0 + w
    y1 = y0 + h

    pos, size = _get_prefs_for_window_pos_size( win, keyprefix, defaults)
    # now use pos and size, within limits set by screen
    px,py = pos
    sx,sy = size
    if sx > w: sx = w
    if sy > h: sy = h
    if px < x0: px = x0
    if py < y0: py = y0
    if px > x1 - sx: px = x1 - sx
    if py > y1 - sy: py = y1 - sy
    env.history.message("restoring last-saved window position %r and size %r" % ((px,py),(sx,sy)))
    win.resize(sx,sy)
    win.move(px,py)
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
    px,py = dpos # check correctness of args, even if not used later
    sx,sy = dsize
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

class UserPrefs(QDialog, Ui_UserPrefsDialog):
    """
    The User Preferences dialog used for accessing and changing user
    preferences.
    """

    def __init__(self, assy):
        QDialog.__init__(self)
        self.setupUi(self)

        # Some standard attrs.
        self.glpane = assy.o
        self.w = assy.w
        self.assy = assy

        #NOTE: THE FOLLOWING HIDES SOME WIDGETS (e.g. GAMESS plugin,
        #ESP Image plugin (nanohive) path widgets.(under plugins tab)
        #This is for the rattlesnake spring backlog item
        #"disable the items that aren't used too much (GAMESS, CoNTub, ESP/NH1)"
        #See also: Ui_SimulationMenu.py where the coresponding commands are hidden
        #or shown based on a debug pref.
        self._hideOrShowTheseWidgetsInUserPreferenceDialog()

        self.resetMouseSpeedDuringRotation_btn.setIcon(
            geticon('ui/dialogs/Reset.png'))
        self.reset_cpk_scale_factor_btn.setIcon(
            geticon('ui/dialogs/Reset.png'))
        self.whatsThisToolButton.setIcon(
            geticon("ui/actions/Help/WhatsThis.png"))
        #this is for solid background color frame. It is important to
        #setAutofillBackground to True in order for it to work.
        #ideally should be done in UserPrefsDialog.py -- ninad070430
        self.bg1_color_frame.setAutoFillBackground(True)

        self.setWindowTitle("Preferences")
        self.setWindowIcon(geticon("ui/actions/Tools/Options.png"))

        #@ WHAT IS THIS? Mark
        #self.update_btngrp_group = QButtonGroup()
        #self.update_btngrp_group.setExclusive(True)

        #for obj in self.update_btngrp.children():
        #    if isinstance(obj, QAbstractButton):
        #        self.update_btngrp_group.addButton(obj)

        # Default Projection Groupbox in General tab (as of 070430)
        self.default_projection_btngrp = QButtonGroup()
        self.default_projection_btngrp.setExclusive(True)
        objId = 0
        for obj in self.default_projection_grpBox.children():
            if isinstance(obj, QAbstractButton):
                self.default_projection_btngrp.addButton(obj)
                self.default_projection_btngrp.setId(obj, objId)
                objId +=1

        if env.prefs[defaultProjection_prefs_key] == 0:
            self.perspective_radioButton.setChecked(True)
        else:
            self.orthographic_radioButton.setChecked(True)

        #Default atom Display groupbox in Modes tab (as of 070430)
        self.default_display_btngrp = QButtonGroup()
        self.default_display_btngrp.setExclusive(True)

        #self.cpk_rbtn --> diTrueCPK which has id 2 (defined in constants.py)
        self.default_display_btngrp.addButton(self.cpk_rbtn)
        self.default_display_btngrp.setId(self.cpk_rbtn, 2)

        #self.lines_rbtn is the 'Lines' display mode
        self.default_display_btngrp.addButton(self.lines_rbtn)
        self.default_display_btngrp.setId(self.lines_rbtn, 3)

        #self.ballNstick_rbtn is the 'Ball and Stick' display mode
        self.default_display_btngrp.addButton(self.ballNstick_rbtn)
        self.default_display_btngrp.setId(self.ballNstick_rbtn, 4)

        #self.tubes_rbtn is the 'Tubes' display mode
        self.default_display_btngrp.addButton(self.tubes_rbtn)
        self.default_display_btngrp.setId(self.tubes_rbtn, 5)

        self.high_order_bond_display_btngrp = QButtonGroup()
        self.high_order_bond_display_btngrp.setExclusive(True)

        objId = 0
        for obj in [self.multCyl_radioButton, self.vanes_radioButton,
                    self.ribbons_radioButton]:
            self.high_order_bond_display_btngrp.addButton(obj)
            self.high_order_bond_display_btngrp.setId(obj, objId)
            objId +=1

        # Sponsor logos download permission in General tab
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
        self.setUI_LogoDownloadPermissions()

        self.connect(self.whatsThisToolButton,SIGNAL("clicked()"),QWhatsThis.enterWhatsThisMode)

        self.connect(self.animation_speed_slider,SIGNAL("sliderReleased()"),self.change_view_animation_speed)
        self.connect(self.rulerDisplayComboBox,SIGNAL("currentIndexChanged(int)"),self.set_ruler_display)
        self.connect(self.rulerPositionComboBox,SIGNAL("currentIndexChanged(int)"),self.set_ruler_position)
        self.connect(self.ruler_color_btn,SIGNAL("clicked()"),self.change_ruler_color)
        self.connect(self.rulerOpacitySpinBox,SIGNAL("valueChanged(int)"),self.change_ruler_opacity)
        self.connect(self.atom_hilite_color_btn,SIGNAL("clicked()"),self.change_atom_hilite_color)
        self.connect(self.ballstick_bondcolor_btn,SIGNAL("clicked()"),self.change_ballstick_bondcolor)
        self.connect(self.bond_hilite_color_btn,SIGNAL("clicked()"),self.change_bond_hilite_color)
        self.connect(self.bond_line_thickness_spinbox,SIGNAL("valueChanged(int)"),self.change_bond_line_thickness)
        self.connect(self.bond_stretch_color_btn,SIGNAL("clicked()"),self.change_bond_stretch_color)
        self.connect(self.bond_vane_color_btn,SIGNAL("clicked()"),self.change_bond_vane_color)
        self.connect(self.bondpoint_hilite_color_btn,SIGNAL("clicked()"),self.change_bondpoint_hilite_color)

        # Mouse wheel prefs signal-slot connections.
        self.connect(self.mouseWheelDirectionComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.set_mouse_wheel_direction)
        self.connect(self.mouseWheelZoomInPointComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.set_mouse_wheel_zoom_in_position)
        self.connect(self.mouseWheelZoomOutPointComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.set_mouse_wheel_zoom_out_position)

        # DNA page signal-slot connections.
        self.connect(self.dnaBasesPerTurnDoubleSpinBox,SIGNAL("valueChanged(double)"),self.save_dnaBasesPerTurn)
        self.connect(self.dnaRiseDoubleSpinBox,SIGNAL("valueChanged(double)"),self.save_dnaRise)
        self.connect(self.dnaRestoreFactoryDefaultsPushButton,SIGNAL("clicked()"),self.dnaRestoreFactoryDefaults)
        self.connect(self.dnaDefaultSegmentColorPushButton,SIGNAL("clicked()"),self.changeDnaDefaultSegmentColor)

        self.connect(self.strandThreePrimeArrowheadsCustomColorPushButton,
                     SIGNAL("clicked()"),
                     self.change_dnaStrandThreePrimeArrowheadCustomColor)

        self.connect(self.strandFivePrimeArrowheadsCustomColorPushButton,
                     SIGNAL("clicked()"),
                     self.change_dnaStrandFivePrimeArrowheadCustomColor)

        self.connect(self.strandThreePrimeArrowheadsCustomColorCheckBox,
                     SIGNAL("toggled(bool)"),
                     self.update_dnaStrandThreePrimeArrowheadCustomColorWidgets)

        self.connect(self.strandFivePrimeArrowheadsCustomColorCheckBox,
                     SIGNAL("toggled(bool)"),
                     self.update_dnaStrandFivePrimeArrowheadCustomColorWidgets)

        # DNA Minor Groove Error Indicator signal/slot connections.
        self.connect(self.dnaMinGrooveAngleSpinBox,
                     SIGNAL("valueChanged(int)"),
                     self.save_dnaMinMinorGrooveAngles)
        self.connect(self.dnaMaxGrooveAngleSpinBox,
                     SIGNAL("valueChanged(int)"),
                     self.save_dnaMaxMinorGrooveAngles)
        self.connect(self.dnaGrooveIndicatorColorButton,
                     SIGNAL("clicked()"),
                     self.change_dnaMinorGrooveErrorIndicatorColor)
        self.connect(self.dnaMinorGrooveRestoreFactoryDefaultsPushButton,
                     SIGNAL("clicked()"),
                     self._restore_dnaMinorGrooveFactoryDefaults)

        # piotr 080325
        self.connect(self.dnaDisplayBaseOrientationIndicatorsGroupBox,SIGNAL("toggled(bool)"),self.toggle_dnaDisplayBaseOrientationIndicatorsGroupBox)
        self.connect(self.dnaBaseOrientationIndicatorsInverseCheckBox,SIGNAL("toggled(bool)"),self.toggle_dnaDisplayBaseOrientationInvIndicatorsCheckBox)
        self.connect(self.dnaBaseOrientationIndicatorsThresholdSpinBox,SIGNAL("valueChanged(double)"),self.change_dnaBaseIndicatorsAngle)
        self.connect(self.dnaBaseOrientationIndicatorsTerminalDistanceSpinBox,SIGNAL("valueChanged(double)"),self.change_dnaBaseIndicatorsDistance)
        self.connect(self.dnaChooseBaseOrientationIndicatorsColorButton,SIGNAL("clicked()"),self.change_dnaBaseIndicatorsColor)
        self.connect(self.dnaChooseBaseOrientationIndicatorsInvColorButton,SIGNAL("clicked()"),self.change_dnaBaseInvIndicatorsColor)
        self.connect(self.dnaBaseIndicatorsPlaneNormalComboBox,SIGNAL("activated(int)"),self.change_dnaBaseOrientIndicatorsPlane)

        self.connect(self.caption_fullpath_checkbox,SIGNAL("stateChanged(int)"),self.set_caption_fullpath)
        self.connect(self.change_element_colors_btn,SIGNAL("clicked()"),self.change_element_colors)
        self.connect(self.compass_position_combox,SIGNAL("activated(int)"),self.set_compass_position)
        self.connect(self.cpk_atom_rad_spinbox,SIGNAL("valueChanged(int)"),self.change_ballstick_atom_radius)
        self.connect(self.cpk_cylinder_rad_spinbox,SIGNAL("valueChanged(int)"),self.change_ballstick_cylinder_radius)
        self.connect(self.cpk_scale_factor_slider,SIGNAL("sliderReleased()"),self.save_cpk_scale_factor)
        self.connect(self.cpk_scale_factor_slider,SIGNAL("valueChanged(int)"),self.change_cpk_scale_factor)
        self.connect(self.current_height_spinbox,SIGNAL("valueChanged(int)"),self.change_window_size)
        self.connect(self.current_width_spinbox,SIGNAL("valueChanged(int)"),self.change_window_size)
        self.connect(self.cutovermax_linedit,SIGNAL("textChanged(const QString&)"),self.change_cutovermax)
        self.connect(self.cutoverrms_linedit,SIGNAL("textChanged(const QString&)"),self.change_cutoverrms)
        self.connect(self.default_display_btngrp,SIGNAL("buttonClicked(int)"),
                     self.set_default_display_mode)
        #ninad070430 : For A9, there is only one default and startup mode
        #(which is Select Chunbks mode) So disabling the following.
        ##self.connect(self.default_mode_combox,SIGNAL("activated(int)"),
                ##self.change_default_mode)
        ##self.connect(self.startup_mode_combox,
                ##SIGNAL("activated(const QString&)"),self.change_startup_mode)
        self.connect(self.default_projection_btngrp,SIGNAL("buttonClicked(int)"),self.set_default_projection)
        self.connect(self.compassGroupBox,SIGNAL("stateChanged(int)"),self.display_compass)
        self.connect(self.endmax_linedit,SIGNAL("textChanged(const QString&)"),self.change_endmax)
        self.connect(self.endrms_linedit,SIGNAL("textChanged(const QString&)"),self.change_endrms)
        self.connect(self.minimize_engine_combobox,SIGNAL("activated(int)"),self.set_adjust_minimization_engine)
        self.connect(self.logosDownloadPermissionBtnGroup,
                     SIGNAL("buttonClicked(int)"),
                     self.setPrefsLogoDownloadPermissions)

        self.connect(self.high_order_bond_display_btngrp,SIGNAL("buttonClicked(int)"),self.change_high_order_bond_display)
        self.connect(self.hotspot_color_btn,SIGNAL("clicked()"),self.change_hotspot_color)
        self.connect(self.level_of_detail_combox,SIGNAL("activated(int)"),self.change_level_of_detail)
        self.connect(self.light_ambient_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_ambient_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_checkbox,SIGNAL("toggled(bool)"),self.toggle_light)
        self.connect(self.light_color_btn,SIGNAL("clicked()"),self.change_light_color)
        self.connect(self.light_combobox,SIGNAL("activated(int)"),self.change_active_light)
        self.connect(self.light_diffuse_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_diffuse_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_specularity_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_specularity_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_x_linedit,SIGNAL("returnPressed()"),self.save_lighting)
        self.connect(self.light_y_linedit,SIGNAL("returnPressed()"),self.save_lighting)
        self.connect(self.light_z_linedit,SIGNAL("returnPressed()"),self.save_lighting)
        self.connect(self.lighting_restore_defaults_btn,SIGNAL("clicked()"),self.restore_default_lighting)
        self.connect(self.ms_brightness_slider,SIGNAL("sliderReleased()"),self.change_material_brightness_stop)
        self.connect(self.ms_brightness_slider,SIGNAL("valueChanged(int)"),self.change_material_brightness)
        self.connect(self.ms_brightness_slider,SIGNAL("sliderPressed()"),self.change_material_brightness_start)
        self.connect(self.ms_finish_slider,SIGNAL("valueChanged(int)"),self.change_material_finish)
        self.connect(self.ms_finish_slider,SIGNAL("sliderReleased()"),self.change_material_finish_stop)
        self.connect(self.ms_finish_slider,SIGNAL("sliderPressed()"),self.change_material_finish_start)
        self.connect(self.ms_on_checkbox,SIGNAL("toggled(bool)"),self.toggle_material_specularity)
        self.connect(self.ms_shininess_slider,SIGNAL("sliderReleased()"),self.change_material_shininess_stop)
        self.connect(self.ms_shininess_slider,SIGNAL("sliderPressed()"),self.change_material_shininess_start)
        self.connect(self.ms_shininess_slider,SIGNAL("valueChanged(int)"),self.change_material_shininess)

        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)

        self.connect(self.prefs_tab,SIGNAL("selected(const QString&)"),self.setup_current_page)
        self.connect(self.reset_atom_colors_btn,SIGNAL("clicked()"),self.reset_atom_colors)
        self.connect(self.reset_bond_colors_btn,SIGNAL("clicked()"),self.reset_bond_colors)
        self.connect(self.reset_cpk_scale_factor_btn,SIGNAL("clicked()"),self.reset_cpk_scale_factor)
        self.connect(self.restore_saved_size_btn,SIGNAL("clicked()"),self.restore_saved_size)
        self.connect(self.save_current_btn,SIGNAL("clicked()"),self.save_current_win_pos_and_size)
        self.connect(self.show_bond_labels_checkbox,SIGNAL("toggled(bool)"),self.change_bond_labels)
        self.connect(self.show_valence_errors_checkbox,SIGNAL("toggled(bool)"),self.change_show_valence_errors)

        # Connections for font widgets (in "Windows" page). Mark 2007-05-27.
        self.connect(self.selectedFontGroupBox,SIGNAL("toggled(bool)"), self.change_use_selected_font)
        self.connect(self.fontComboBox,SIGNAL("currentFontChanged (const QFont &)"), self.change_font)
        self.connect(self.fontSizeSpinBox,SIGNAL("valueChanged(int)"), self.change_fontsize)
        self.connect(self.makeDefaultFontPushButton,SIGNAL("clicked()"), self.change_selected_font_to_default_font)

        # Connections for color theme.
        self.connect(self.colorThemeComboBox,SIGNAL("currentIndexChanged(const QString&)"),self.change_color_theme)

        self.connect(self.undo_stack_memory_limit_spinbox,SIGNAL("valueChanged(int)"),self.change_undo_stack_memory_limit)
        self.connect(self.update_number_spinbox,SIGNAL("valueChanged(int)"),self.update_number_spinbox_valueChanged)
        self.connect(self.fill_type_combox,SIGNAL("activated(const QString&)"),self.change_fill_type)
        self.connect(self.restore_bgcolor_btn,SIGNAL("clicked()"),self.restore_default_bgcolor)
        self.connect(self.choose_bg1_color_btn,SIGNAL("clicked()"),self.change_bg1_color)
        self.connect(self.dynamicToolTipAtomDistancePrecision_spinbox,SIGNAL("valueChanged(int)"),self.change_dynamicToolTipAtomDistancePrecision)
        self.connect(self.dynamicToolTipBendAnglePrecision_spinbox,SIGNAL("valueChanged(int)"),self.change_dynamicToolTipBendAnglePrecision)
        self.connect(self.historyHeight_spinbox,SIGNAL("valueChanged(int)"),self.change_historyHeight)
        self.connect(self.mouseSpeedDuringRotation_slider,SIGNAL("valueChanged(int)"),self.change_mouseSpeedDuringRotation)
        self.connect(self.resetMouseSpeedDuringRotation_btn,SIGNAL("clicked()"),self.reset_mouseSpeedDuringRotation)

        #mark 060627
        # Validator for the linedit widgets. [WARNING: bruce 060705 copied this into MinimizeEnergyProp.py]
        self.endrms_validator = QDoubleValidator(self)
        self.endrms_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0.0 to 100, 2 decimal places
        self.endrms_linedit.setValidator(self.endrms_validator)

        self.endmax_validator = QDoubleValidator(self)
        self.endmax_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.endmax_linedit.setValidator(self.endmax_validator)

        self.cutoverrms_validator = QDoubleValidator(self)
        self.cutoverrms_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.cutoverrms_linedit.setValidator(self.cutoverrms_validator)

        self.cutovermax_validator = QDoubleValidator(self)
        self.cutovermax_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.cutovermax_linedit.setValidator(self.cutovermax_validator)

        #ninad20070509 setup general page. The items on the general page don't
        #work properly if the current index of UserPrefs dialog is set as 0
        #(which is 'General' page) . The following call makes sure that
        #this won't happen.

        self._setup_general_page()

        #bruce 050811 added these:
        self._setup_window_page() # make sure the LineEdits are initialized before we hear their signals
        self._setup_caption_signals()
        self._setup_plugin_signals() #bruce 060710

        # This is where What's This descriptions should go for UserPrefs.
        # Mark 050831.
        from ne1_ui.WhatsThisText_for_MainWindow import create_whats_this_descriptions_for_UserPrefs_dialog
        create_whats_this_descriptions_for_UserPrefs_dialog(self)

        self.display_origin_axis_checkbox.setWhatsThis("""<p><b>Display Origin Axis</b></p>Shows/Hides the Origin Axis""")
        self.display_pov_axis_checkbox.setWhatsThis("""<p><b>Display Point of View Axis</b></p>Shows/Hides the Point
                                                of View Axis""")
        self.compassGroupBox.setWhatsThis("""<p><b>Display Compass</b></p>Shows/Hides the Display Compass""")
        self.display_compass_labels_checkbox.setWhatsThis("""<p><b>Display Compass</b></p>Shows/Hides the Display Compass""")
        self.update_btngrp.setWhatsThis("""<p><b>Watch motion in real time</b></p>Enables/disables real
                                    time graphical updates during adjust operations when using <b>Adjust All</b> or <b>Adjust Selection</b>""")
        self.update_number_spinbox.setWhatsThis("""<b>Update every <i>n units.</u></b>
                                                <p>Specify how often to update
the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
        self.update_units_combobox.setWhatsThis("""<b>Update every <i>n units.</u></b>
                                                <p>Specify how often to update
the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
        self.update_every_rbtn.setWhatsThis("""<b>Update every <i>n units.</u></b>
                                            <p>Specify how often to update
the model during the adjustment. This allows the user to monitor results during adjustments.</p>""")
        self.update_asap_rbtn.setWhatsThis("""<b>Update as fast as possible</b>
                                           <p>
Update every 2 seconds,
or faster (up to 20x/sec) if it doesn't slow adjustments by more than 20%</p>""")
        self.endrms_lbl.setWhatsThis("""<b>EndRMS</b>
                                 <p>Continue until this RMS force is reached.</p>""")
        self.endmax_lbl.setWhatsThis("""<b>EndMax</b>
                                 <p>Continue until no interaction exceeds this force.</p>""")
        self.endmax_linedit.setWhatsThis("""<b>EndMax</b>
                                     <p>Continue until no interaction exceeds this force.</p>""")
        self.endrms_linedit.setWhatsThis("""<b>EndRMS</b>
                                     <p>Continue until this RMS force is reached.</p>""")
        self.cutovermax_lbl.setWhatsThis("""<b>CutoverMax</b>
                                         <p>Use steepest descent until no interaction
exceeds this force.</p>""")
        self.cutovermax_linedit.setWhatsThis("""<b>CutoverMax</b>
                                             <p>Use steepest descent until no interaction
exceeds this force.</p>""")
        self.cutoverrms_linedit.setWhatsThis("""<b>CutoverRMS</b>
                                             <p>Use steepest descent until this RMS force
is reached.</p>""")
        self.cutoverrms_lbl.setWhatsThis("""<b>CutoverRMS</b>
                                         <p>Use steepest descent until this RMS force
is reached.</p>""")
        self.groupBox14.setWhatsThis("""<b>Settings for Adjust</b>
                                     <p>This group of settings affect the
behavior of <b>Adjust All</b> and <b>Adjust Selection</b>.</p>""")

        # Sponsor Logos Download Permission
        self.sponsorLogosGroupBox.setWhatsThis("""<b>Sponsor Logos Download Permission</b>
                                               <p>This group of buttons sets the permission for downloading sponsor
logos.</p>""")
        self.logoAlwaysAskRadioBtn.setWhatsThis("""<b>Always ask before downloading</b>
                                                <p>When sponsor logos have been updated, ask permission to download
them.</p>""")
        self.logoNeverAskRadioBtn.setWhatsThis("""<b>Never ask before downloading</b>
                                               <p>When sponsor logos have been updated, download them without asking
permission to do so.</p>""")
        self.logoNeverDownLoadRadioBtn.setWhatsThis("""<b>Never download</b>
                                                    <p>Don't ask permission to download sponsor logos and don't download
them.</p>""")

        self.animate_views_checkbox.setWhatsThis("""<p><b>Animate Between Views</b></p><p>Enables/disables animation
                                             when switching between the current view and a new view.</p>""")
        self.animation_speed_slider.setWhatsThis("""<p><b>View Animation Speed</b></p><p>Sets the animation speed when
                                                 animating between view (i.e. Front View to Right View).  It is recommended that this be set to Fast when working on large
models.</p>""")
        self.textLabel1_7.setWhatsThis("""<p><b>Level of Detail</b></p><p>Sets the <b>Level of Detail</b>
                                       for atoms and bonds.<br><br>  <b>High</b> = Best graphics quality (slowest rendering speed)<br><b>Medium</b> = Good graphics
quality<br> <b>Low</b> = Poor graphics quality (fastest rendering speed) <br><b>Variable</b> automatically switches between
High, Medium and Low based on the model size (number of atoms).</p>""")
        self.level_of_detail_combox.setWhatsThis("""<p><b>Level of Detail</b></p>Sets the graphics quality for atoms
                                                 (and bonds)<br><br>  <b>High</b> = Best graphics quality (slowest rendering speed)<br><b>Medium</b> = Good graphics quality<br>
<b>Low</b> = Poor graphics quality (fastest rendering speed) <br><b>Variable</b> automatically switches between High, Medium
and Low based on the number of atoms in the current part.""")
        self.textLabel1_3_2.setWhatsThis("""<p><b>Ball and Stick Atom Scale</b></p>Sets the Ball and Stick
                                     Atom Scale factor. It is best to change the scale factor while the current model is displayed in Ball and Stick mode.""")
        self.cpk_atom_rad_spinbox.setWhatsThis("""<p><b>Ball and Stick Atom Scale</b></p>Sets the Ball and Stick
                                           Atom Scale factor. It is best to change the scale factor while the current model is displayed in Ball and Stick mode.""")
        self.textLabel1_3_2_2.setWhatsThis("""<p><b>CPK Atom Scale</b></p>Changes the CPK Atom Scale factor.
                                       It is best to change the scale factor while in CPK display mode so you can see the graphical effect of changing the scale.""")
        self.cpk_scale_factor_linedit.setWhatsThis("""Displays the value of the CPK Atom Scale""")
        self.cpk_scale_factor_slider.setWhatsThis("""<p><b>CPK Atom Scale</b></p>Slider control for chaning the CPK
                                                  Atom Scale factor. It is best to change the scale factor while in CPK display mode so you can see the graphical effect of
changing the scale.""")
        self.reset_cpk_scale_factor_btn.setWhatsThis("""Restore the default value of the CPK Scale Factor""")
        self.multCyl_radioButton.setWhatsThis("""<p><b>Multiple Cylinders</b></p>
                                              <p><b>High Order Bonds</b> are
displayed using <b>Multiple Cylinders.</b></p>
<b>Double bonds</b> are drawn with two cylinders.<br>
<b>Triple bonds</b>
are drawn with three cylinders.<br>
<b>Aromatic bonds</b> are drawn as a single cylinder with a short green cylinder in the
middle.""")
        self.vanes_radioButton.setWhatsThis("""<p><b>Vanes</b></p>
                                            <p><i>High Order Bonds</i> are displayed
using <b>Vanes.</b></p>
<p>Vanes represent <i>pi systems</i> in high order bonds and are rendered as rectangular polygons.
The orientation of the vanes approximates the orientation of the pi system(s).</p>
<p>Create an acetylene or ethene molecule
and select this option to see how vanes are rendered.</p>""")
        self.ribbons_radioButton.setWhatsThis("""<p><b>Ribbons</b></p>
                                              <p><i>High Order Bonds</i> are displayed
using <b>Ribbons.</b></p>
<p>Ribbons represent <i>pi systems</i> in high order bonds and are rendered as ribbons. The orientation of the ribbons approximates the orientation of the pi system.</p>
<p>Create an acetylene or ethene molecule and select this option to see how ribbons are rendered.</p>""")
        self.show_bond_labels_checkbox.setWhatsThis("""<p><b>Show Bond Type Letters</b></p>
                                                    <p>Shows/Hides Bond Type
letters (labels) on top of bonds.</p>
<u>Bond Type Letters:</u><br>
<b>2</b> = Double bond<br>
<b>3</b> = Triple bond<br>
<b>A</b>
= Aromatic bond<br>
<b>G</b> = Graphitic bond<br>""")
        self.show_valence_errors_checkbox.setWhatsThis("""<p><b>Show Valence Errors</b></p><p>Enables/Disables Valence
                                                       Error Checker.</p>When enabled, atoms with valence errors are displayed with a pink wireframe sphere. This indicates
that one or more of the atom's bonds are not of the correct order (type), or that the atom has the wrong number of bonds,
or (for PAM DNA pseudoatoms) that there is some error in bond directions or in which PAM elements are bonded. The error details can be seen in the tooltip for the atom.""")
        self.textLabel1_3.setWhatsThis("""<p><b>Ball and Stick Bond Scale</b></p>Set scale (size) factor for the cylinder representing bonds in Ball and Stick display mode""")
        self.textLabel1.setWhatsThis("""<p><b>Bond Line Thickness</b></p>Bond thickness (in pixels) for Lines Display Style""")
        self.cpk_cylinder_rad_spinbox.setWhatsThis("""<p><b>Ball and Stick Bond Scale</b></p>Set scale (size) factor
                                               for the cylinder representing bonds in Ball and Stick display mode""")
        self.bond_line_thickness_spinbox.setWhatsThis("""<p><b>Bond Line Thickness</b></p>Bond thickness (in pixels) for
                                                  Lines Display Style""")
        self.fill_type_combox.setWhatsThis("""<p><b>Fill Type</b></p>
                                       <p>Sets the fill type of the background. Each mode can have a different color, if desired.</p>""")
        self.cpk_rbtn.setWhatsThis("""<u><b>CPK (Space Filling)</b></u><br>
                                   <p>Changes the <i>Default Display Style</i>  to <b>CPK</b> mode.
Atoms are rendered as space filling spheres. Bonds are not rendered.</p>""")
        self.ballNstick_rbtn.setWhatsThis("""<u><b>Ball and Stick</b></u><br>
                                          <p>Changes the <i>Default Display Style</i> to <b>Ball and Stick</b> mode. Atoms are rendered  as spheres (balls) and bonds are rendered as narrow cylinders
(sticks).</p>""")
        self.lines_rbtn.setWhatsThis("""<u><b>Lines</b></u><br>
                                 <p>Changes the <i>Default Display Style</i> to <b>Lines</b> mode. Bonds are rendered as lines. Atoms are not rendered.</p>""")
        self.tubes_rbtn.setWhatsThis("""<u><b>Tubes</b></u><br>
                                 <p>Changes the <i>Default Display Style</i> to <b>Tubes</b> mode.Atoms and bonds are rendered as colored tubes.</p>""")
        self.autobond_checkbox.setWhatsThis("""Build mode's default setting for Autobonding at startup (enabled/disabled)""")
        self.water_checkbox.setWhatsThis("""Build mode's default setting for Water at startup (enabled/disabled)""")
        self.buildmode_select_atoms_checkbox.setWhatsThis("""<p><b>Select Atoms of Deposited Object</b></p>
                                                      When depositing atoms, clipboard chunks or library parts, their atoms will automatically be selected.""")
        self.buildmode_highlighting_checkbox.setWhatsThis("""Build mode's default setting for Highlighting at startup (enabled/disabled)""")

        self.gromacs_label.setWhatsThis("""Enable GROMACS and choose the mdrun executable path to use.""")
        self.gromacs_checkbox.setWhatsThis("""This enables GROMACS as a plug-in. GROMACS is a free rendering program available from http://www.gromacs.org/. GROMACS must be installed on your computer before you can enable the GROMACS plug-in.  Check this and choose the the path to the mdrun executable from your GROMACS distribution.""")
        self.gromacs_path_lineedit.setWhatsThis("""The full path to the mdrun executable file for GROMACS.""")
        self.gromacs_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                         location of the GROMACS executable (mdrun).""")

        self.cpp_label.setWhatsThis("""Specify the C-preprocessor (cpp) for GROMACS to use.""")
        self.cpp_checkbox.setWhatsThis("""Specify the C-preprocessor (cpp) for GROMACS to use.""")
        self.cpp_path_lineedit.setWhatsThis("""The full path to the C-preprocessor (cpp) executable file for GROMACS to use.""")
        self.cpp_choose_btn.setWhatsThis("""Allows you to choose the path to the C-preprocessor (cpp) executable file for GROMACS to use.""")

        self.povray_checkbox.setWhatsThis("""This enables POV-Ray as a plug-in. POV-Ray is a free raytracing program available from http://www.povray.org/. POV-Ray must be installed on your computer before you can enable the POV-Ray plug-in.""")
        self.povray_lbl.setWhatsThis("""This enables POV-Ray as a plug-in. POV-Ray is a free raytracing program available from http://www.povray.org/. POV-Ray must be installed on your computer before you can enable the POV-Ray plug-in.""")

        self.qutemol_lbl.setWhatsThis("""This enables QuteMolX as a plug-in. QuteMolX is available for download from http://nanoengineer-1.com/QuteMolX. QuteMolX must be installed on your computer before you can enable this plug-in.""")
        self.qutemol_checkbox.setWhatsThis("""This enables QuteMolX as a plug-in. QuteMolX is available for download from http://nanoengineer-1.com/QuteMolX. QuteMolX must be installed on your computer before you can enable the this plug-in.""")

        self.nanohive_lbl.setWhatsThis("""This enables Nano-Hive as a plug-in. Nano-Hive is available for download from  http://www.nano-hive.com/. Nano-Hive must be installed on your computer before you can enable the Nano-Hive plug-in.""")
        self.nanohive_checkbox.setWhatsThis("""This enables Nano-Hive as a plug-in. Nano-Hive is available for download from http://www.nano-hive.com/. Nano-Hive must be installed on your computer before you can enable the Nano-Hive plug-in.""")

        self.povray_path_lineedit.setWhatsThis("""The full path to the POV-Ray executable file.""")
        self.qutemol_path_lineedit.setWhatsThis("""The full path to the QuteMolX executable file.""")
        self.nanohive_path_lineedit.setWhatsThis("""The full path to the Nano-Hive executable file.""")
        self.gamess_lbl.setWhatsThis("""<p>This enables PC-GAMESS (Windows) or GAMESS (Linux or MacOS) as a plug-in. </p>
                                     <p>For Windows users, PC-GAMESS is available for download from http://classic.chem.msu.su/gran/gamess/.
PC-GAMESS must be installed on your computer before you can enable the PC-GAMESS plug-in.</p>
<p>For Linux and MacOS users,
GAMESS is available for download from http://www.msg.ameslab.gov/GAMESS/GAMESS.html. GAMESS must be installed on your computer before you can enable the GAMESS plug-in.</p>""")
        self.megapov_path_lineedit.setWhatsThis("""The full path to the MegaPOV executable file (megapov.exe).""")
        self.megapov_checkbox.setWhatsThis("""This enables MegaPOV as a plug-in. MegaPOV is a free addon raytracing program available from http://megapov.inetart.net/. Both MegaPOV and POV-Ray must be installed on your computer before you can enable the MegaPOV plug-in. MegaPOV allows rendering to happen silently on Windows (i.e. no POV_Ray GUI is displayed while rendering).""")
        self.gamess_path_lineedit.setWhatsThis("""The gamess executable file. Usually it's called gamess.??.x or
                                           ??gamess.exe.""")
        self.gamess_checkbox.setWhatsThis("""<p>This enables PC-GAMESS (Windows) or GAMESS (Linux or MacOS)
                                          as a plug-in. </p>
<p>For Windows users, PC-GAMESS is available for download from http://classic.chem.msu.su/gran/gamess/.
PC-GAMESS must be installed on your computer before you can enable the PC-GAMESS plug-in.</p>
<p>For Linux and MacOS users,
GAMESS is available for download from http://www.msg.ameslab.gov/GAMESS/GAMESS.html. GAMESS must be installed on your computer before you can enable the GAMESS plug-in.</p>""")
        self.povdir_lineedit.setWhatsThis("""Specify a directory for where to find POV-Ray or MegaPOV include
                                      files such as transforms.inc.""")


        self.qutemol_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                         location of the QuteMolX executable.""")
        self.nanohive_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                          location of the Nano-Hive executable.""")
        self.povray_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                        location of the POV-Ray executable.""")
        self.megapov_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                         location of the MegaPOV executable (megapov.exe).""")
        self.gamess_choose_btn.setWhatsThis("""This opens up a file chooser dialog so that you can specify the
                                        location of the GAMESS or PC-GAMESS executable.""")
        self.megapov_lbl.setWhatsThis("""This enables MegaPOV as a plug-in. MegaPOV is a free addon raytracing program available from http://megapov.inetart.net/. Both MegaPOV and POV-Ray must be installed on your computer before you can enable the MegaPOV plug-in. MegaPOV allows rendering to happen silently on Windows (i.e. no POV_Ray GUI is displayed while rendering).""")
        self.povdir_checkbox.setWhatsThis("""Select a user-customized directory for POV-Ray and MegaPOV include files, such as transforms.inc.""")
        self.undo_automatic_checkpoints_checkbox.setWhatsThis("""<p><b>Automatic Checkpoints</b></p>Specifies whether <b>Automatic
                                                              Checkpointing</b> is enabled/disabled during program startup only.  It does not enable/disable <b>Automatic Checkpointing</b>
when the program is running.
<p><b>Automatic Checkpointing</b> can be enabled/disabled by the user at any time from <b>Edit > Automatic Checkpointing</b>. When enabled, the program maintains the Undo stack automatically.  When disabled, the user is required to manually set Undo checkpoints using the <b>Set Checkpoint</b> button in the Edit Toolbar/Menu.</p>
<p><b>Automatic Checkpointing</b> can impact program performance. By disabling Automatic Checkpointing, the program will run faster.</p><p><b><i>Remember to you must set your own Undo checkpoints manually when Automatic Checkpointing is disabled.</i></b></p>""")
        self.undo_restore_view_checkbox.setWhatsThis("""<p><b>Restore View when Undoing Structural Changes</b></p>
                                                     <p>When checked, the current view is stored along with each <b><i>structural change</i></b> on the undo stack.  The view is then
restored when the user undoes a structural change.</p>
<p><b><i>Structural changes</i></b> include any operation that modifies the model. Examples include adding, deleting or moving an atom, chunk or jig. </p>
<p>Selection (picking/unpicking) and view changes are examples of operations that do not modify the model (i.e. are not structural changes).</p>""")
        self.groupBox3.setWhatsThis("""Format Prefix and Suffix text the delimits the part name in the caption in window border.""")
        self.save_current_btn.setWhatsThis("""Saves the main window's current position and size for the next time the program starts.""")
        self.restore_saved_size_btn.setWhatsThis("""Saves the main window's current position and size for the next time the program starts.""")
        return


    def _setup_caption_signals(self):
        # caption_prefix signals
        self.connect( self.caption_prefix_linedit, SIGNAL("textChanged ( const QString & ) "), \
                      self.caption_prefix_linedit_textChanged )
        self.connect( self.caption_prefix_linedit, SIGNAL("returnPressed()"), \
                      self.caption_prefix_linedit_returnPressed )
        # caption_suffix signals
        self.connect( self.caption_suffix_linedit, SIGNAL("textChanged ( const QString & ) "), \
                      self.caption_suffix_linedit_textChanged )
        self.connect( self.caption_suffix_linedit, SIGNAL("returnPressed()"), \
                      self.caption_suffix_linedit_returnPressed )
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

    def _setup_plugin_signals(self):
        """
        Signal-slot connections for all widgets on the 'Plugins' page.
        """

        # QuteMolX signal-slot connections.
        self.connect(self.qutemol_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_qutemol)
        self.connect( self.qutemol_path_lineedit,
                      SIGNAL("textEdited (const QString&) "), \
                      self.set_qutemol_path)
        self.connect(self.qutemol_choose_btn,
                     SIGNAL("clicked()"),
                     self.choose_qutemol_path)

        # NanoHive-1 signal-slot connections.
        self.connect(self.nanohive_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_nanohive)
        self.connect( self.nanohive_path_lineedit,
                      SIGNAL("textEdited (const QString&) "), \
                      self.set_nanohive_path)
        self.connect(self.nanohive_choose_btn,
                     SIGNAL("clicked()"),
                     self.choose_nanohive_path)

        # POV-Ray signal-slot connections.
        self.connect(self.povray_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_povray)
        self.connect( self.povray_path_lineedit,
                      SIGNAL("textEdited (const QString&) "), \
                      self.set_povray_path)
        self.connect(self.povray_choose_btn,
                     SIGNAL("clicked()"),
                     self.choose_povray_path)

        # POV dir signal-slot connections.
        self.connect(self.povdir_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_povdir)
        self.connect( self.povdir_lineedit,
                      SIGNAL("textEdited (const QString&) "), \
                      self.povdir_lineedit_textChanged )
        self.connect(self.povdir_choose_btn,
                     SIGNAL("clicked()"),
                     self.set_povdir)
        self.connect( self.povdir_lineedit,
                      SIGNAL("returnPressed()"), \
                      self.povdir_lineedit_returnPressed )

        # MegaPOV signal-slot connections.
        self.connect(self.megapov_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_megapov)
        self.connect( self.megapov_path_lineedit,
                      SIGNAL("textEdited (const QString&) "), \
                      self.set_megapov_path )
        self.connect(self.megapov_choose_btn,
                     SIGNAL("clicked()"),
                     self.choose_megapov_path)

        # GAMESS signal-slot connections.
        self.connect(self.gamess_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_gamess)
        self.connect(self.gamess_path_lineedit,
                     SIGNAL("textEdited(const QString&)"),
                     self.set_gamess_path)
        self.connect(self.gamess_choose_btn,
                     SIGNAL("clicked()"),
                     self.choose_gamess_path)

        # GROMACS signal-slot connections.
        self.connect(self.gromacs_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_gromacs)
        self.connect(self.gromacs_path_lineedit,
                     SIGNAL("textEdited(const QString&)"),
                     self.set_gromacs_path)
        self.connect(self.gromacs_choose_btn,
                     SIGNAL("clicked()"),
                     self.choose_gromacs_path)

        # cpp signal-slot connections.
        self.connect(self.cpp_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_cpp)
        self.connect(self.cpp_path_lineedit,
                     SIGNAL("textEdited(const QString&)"),
                     self.set_cpp_path)
        self.connect(self.cpp_choose_btn,
                     SIGNAL("clicked()"),
                     self.choose_cpp_path)

        # NanoVision-1 signal-slots connections.
        self.connect(self.nv1_checkbox,
                     SIGNAL("toggled(bool)"),
                     self.enable_nv1)
        self.connect(self.nv1_path_lineedit,
                     SIGNAL("textEdited(const QString&)"),
                     self.set_nv1_path)
        self.connect(self.nv1_choose_btn,
                     SIGNAL("clicked()"),
                     self.choose_nv1_path)

    def showDialog(self, pagename = 'General'):
        """
        Display the Preferences dialog with page I{pagename}.

        @param pagename: name of the Preferences page. Default is "General".
        @type  pagename: text
        """

        # Added to fix bug 894.  Mark.
        # [circa 050817, adds bruce; what's new is the pagename argument]
        if pagename == 'General': # Default
            self.prefs_tab.setCurrentIndex(0)
        elif pagename == 'Atoms':
            self.prefs_tab.setCurrentIndex(1)
        elif pagename == 'Bonds':
            self.prefs_tab.setCurrentIndex(2)
        elif pagename == 'DNA':
            self.prefs_tab.setCurrentIndex(3)
        elif pagename == 'Modes':
            self.prefs_tab.setCurrentIndex(4)
        elif pagename == 'Lighting':
            self.prefs_tab.setCurrentIndex(5)
        elif pagename == 'Plug-ins':
            self.prefs_tab.setCurrentIndex(6)
        elif pagename == 'Undo':
            self.prefs_tab.setCurrentIndex(7)
        elif pagename == 'Caption':
            #bruce 051216 comment: I don't know if it's safe to change this string to 'Window' to match tab text
            self.prefs_tab.setCurrentIndex(8)
        elif pagename == 'ToolTips':
            self.prefs_tab.setCurrentIndex(9)
        else:
            print 'Error: Preferences page unknown: ', pagename

        self.setUI_LogoDownloadPermissions()

        self.exec_()
        # bruce comment 050811: using exec_ rather than show forces this dialog to be modal.
        # For now, it's probably still only correct if it's modal, so I won't change this for A6.
        return

    ###### Private methods ###############################
    def _hideOrShowTheseWidgetsInUserPreferenceDialog(self):
        """
        2007-11-16:
        THIS METHOD PERMANENTLY HIDES SOME WIDGETS in UserPrefs tab
        #(e.g. GAMESS plugin,
        #ESP Image plugin (nanohive) path widgets.(under plugins tab)
        #This is for the rattlesnake spring backlog item
        #'disable the items that aren't used too much (GAMESS, CoNTub, ESP/NH1)'

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


    def _setup_general_page(self):
        """
        Setup widgets to initial (default or defined) values on the General page.
        """
        connect_checkbox_with_boolean_pref( self.compassGroupBox, displayCompass_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_compass_labels_checkbox, displayCompassLabels_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_origin_axis_checkbox, displayOriginAxis_prefs_key )
        connect_checkbox_with_boolean_pref( self.display_pov_axis_checkbox, displayPOVAxis_prefs_key )
        self.compass_position_combox.setCurrentIndex(self.glpane.compassPosition)

        #Mouse wheel combo boxes
        self.mouseWheelDirectionComboBox.setCurrentIndex(
            env.prefs[mouseWheelDirection_prefs_key])
        self.mouseWheelZoomInPointComboBox.setCurrentIndex(
            env.prefs[zoomInAboutScreenCenter_prefs_key])
        self.mouseWheelZoomOutPointComboBox.setCurrentIndex(
            env.prefs[zoomOutAboutScreenCenter_prefs_key])

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

        if env.prefs[defaultProjection_prefs_key] == 0:
            self.perspective_radioButton.setChecked(True)
        else:
            self.orthographic_radioButton.setChecked(True)

        connect_checkbox_with_boolean_pref( self.animate_views_checkbox, animateStandardViews_prefs_key )

        # This has been removed for A9. It has never been implemented anyway. Mark 060815.
        # connect_checkbox_with_boolean_pref( self.high_quality_graphics_checkbox, animateHighQualityGraphics_prefs_key )

        speed = int (env.prefs[animateMaximumTime_prefs_key] * -100)
        self.animation_speed_slider.setValue(speed)

        #mouse speed during rotation slider - ninad060906
        mouseSpeedDuringRotation = int(env.prefs[mouseSpeedDuringRotation_prefs_key]*100)

        if mouseSpeedDuringRotation == 60:
            self.resetMouseSpeedDuringRotation_btn.setEnabled(0)
        else:
            self.resetMouseSpeedDuringRotation_btn.setEnabled(1)

        self.mouseSpeedDuringRotation_slider.setValue(mouseSpeedDuringRotation) # generates signal

        # Set "Global Display Style at start-up" option.
        startup_display_style = env.prefs[startupGlobalDisplayStyle_prefs_key]
        if startup_display_style == 2:
            self.cpk_rbtn.setChecked(True)
        elif startup_display_style == 4:
            self.ballNstick_rbtn.setChecked(True)
        elif startup_display_style == 3:
            self.lines_rbtn.setChecked(True)
        elif startup_display_style == 5:
            self.tubes_rbtn.setChecked(True)

            # bruce comments:
            # - it's wrong to use any other data source here than the prefs db, e.g. via env.prefs. Fixed, 050810.
            # - the codes for the buttons are (by experiment) 2,4,5,3 from top to bottom. Apparently these
            #   match our internal display style codes, and are set by buttongroup.insert in the pyuic output file,
            #   but for some reason the buttons are inserted in a different order than they're shown.
            # - this is only sufficient because nothing outside this dialog can change env.prefs[startupGlobalDisplayStyle_prefs_key]
            #   while the dialog is shown.

        # Build Atoms Default Settings.  mark 060203.
        connect_checkbox_with_boolean_pref( self.autobond_checkbox, buildModeAutobondEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.water_checkbox, buildModeWaterEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.buildmode_highlighting_checkbox, buildModeHighlightingEnabled_prefs_key )
        connect_checkbox_with_boolean_pref( self.buildmode_select_atoms_checkbox, buildModeSelectAtomsOfDepositedObjEnabled_prefs_key )

        if 0:
            # bruce 070424: comment out this code which doesn't yet work in Qt4
            self.update_originAxis_btngroup.setEnabled(env.prefs[displayOriginAxis_prefs_key]) #ninad060920

            #@@@ ninad060920 In the dialog box, I have made the axis related radio buttons exclusive
            #but still I need to supply the following condition , otherwise, if the Small Axis Radio button is False
            #and user restarts the session, both the radio buttons are set to false.  Not sure why this is happening
            if env.prefs[displayOriginAsSmallAxis_prefs_key ]:
                self.displayOriginAsSmallAxis_rbtn.setChecked(True)
            else:
                self.displayOriginAsCrossWires_rbtn.setChecked(True)

        # Setup Background Color widgets.
        if self.glpane.backgroundGradient:
            self.bg_gradient_setup()
        else:
            self.bg_solid_setup()

        self.setUI_LogoDownloadPermissions()

    def _setup_plugins_page(self):
        """
        Setup widgets to initial (default or defined) values on the Plug-ins page.
        """

        # GAMESS label.
        if sys.platform == 'win32': # Windows
            self.gamess_lbl.setText("PC GAMESS :")
        else:
            self.gamess_lbl.setText("GAMESS :")

        # QuteMolX executable path.
        self.qutemol_checkbox.setChecked(env.prefs[qutemol_enabled_prefs_key])
        self.qutemol_path_lineedit.setText(env.prefs[qutemol_path_prefs_key])

        # Nano-Hive executable path.
        self.nanohive_checkbox.setChecked(env.prefs[nanohive_enabled_prefs_key])
        self.nanohive_path_lineedit.setText(env.prefs[nanohive_path_prefs_key])

        # POV-Ray executable path.
        self.povray_checkbox.setChecked(env.prefs[povray_enabled_prefs_key])
        self.povray_path_lineedit.setText(env.prefs[povray_path_prefs_key])

        # MegaPOV executable path.
        self.megapov_checkbox.setChecked(env.prefs[megapov_enabled_prefs_key])
        self.megapov_path_lineedit.setText(env.prefs[megapov_path_prefs_key])

        # POV include dir (directory for POV-Ray or MegaPOV include files, or "" to get the default choice)
        # Added by Will & Bruce 060710 for Mac A8 release, not present in Windows A8,
        # since needed to support use of Unix compiles of those programs on the Mac,
        # which is the only way to get a command-line version which NE1 can call. [bruce 060710]
        self.povdir_checkbox.setChecked(env.prefs[povdir_enabled_prefs_key])
        self.povdir_lineedit.setText(env.prefs[povdir_path_prefs_key])

        self._update_povdir_enables() #bruce 060710

        # GAMESS executable path.
        self.gamess_checkbox.setChecked(env.prefs[gamess_enabled_prefs_key])
        self.gamess_path_lineedit.setText(env.prefs[gmspath_prefs_key])

        # GROMACS executable path.
        self.gromacs_checkbox.setChecked(env.prefs[gromacs_enabled_prefs_key])
        self.gromacs_path_lineedit.setText(env.prefs[gromacs_path_prefs_key])

        # cpp executable path.
        self.cpp_checkbox.setChecked(env.prefs[cpp_enabled_prefs_key])
        self.cpp_path_lineedit.setText(env.prefs[cpp_path_prefs_key])

        # NV1 executable path.
        self.nv1_checkbox.setChecked(env.prefs[nv1_enabled_prefs_key])
        self.nv1_path_lineedit.setText(env.prefs[nv1_path_prefs_key])

    def _setup_adjust_page(self):
        """
        Setup widgets to initial (default or defined) values on the Modes page.
        """

        # "Settings for Adjust" groupbox. ###########################

        # Adjust Engine combobox.
        self.minimize_engine_combobox.setCurrentIndex(
            env.prefs[Adjust_minimizationEngine_prefs_key])
        # Watch motion in real time checkbox.
        connect_checkbox_with_boolean_pref(
            self.update_btngrp,
            Adjust_watchRealtimeMinimization_prefs_key )
        #Preference for enabling/disabling electrostatics during Adjustment
        #for the DNA reduced model. Ninad 20070809
        connect_checkbox_with_boolean_pref(
            self.electrostaticsForDnaDuringAdjust_checkBox,
            electrostaticsForDnaDuringAdjust_prefs_key)

        # "Update..." radio btngroup
        self.update_btngrp.setEnabled(
            env.prefs[Adjust_watchRealtimeMinimization_prefs_key])

        # Convergence Criteria groupbox
        # [WARNING: bruce 060705 copied this into MinimizeEnergyProp.py]
        self.endrms = get_pref_or_optval(Adjust_endRMS_prefs_key, -1.0, '')
        self.endrms_linedit.setText(str(self.endrms))

        self.endmax = get_pref_or_optval(Adjust_endMax_prefs_key, -1.0, '')
        self.endmax_linedit.setText(str(self.endmax))

        self.cutoverrms = get_pref_or_optval(Adjust_cutoverRMS_prefs_key, -1.0, '')
        self.cutoverrms_linedit.setText(str(self.cutoverrms))

        self.cutovermax = get_pref_or_optval(Adjust_cutoverMax_prefs_key, -1.0, '')
        self.cutovermax_linedit.setText(str(self.cutovermax))

    # == Let's reorder all these _setup methods in order of appearance soon. Mark 051124.

    def _setup_lighting_page(self, lights = None): #mark 051124
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
        self.disconnect(self.light_ambient_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.disconnect(self.light_diffuse_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.disconnect(self.light_specularity_slider,SIGNAL("valueChanged(int)"),self.change_lighting)

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
        self.connect(self.light_ambient_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_diffuse_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_specularity_slider,SIGNAL("valueChanged(int)"),self.change_lighting)

        self._setup_material_group()

    # _setup_material_group() should be folded back into _setup_lighting_page(). Mark 051204.
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

    def _setup_atoms_page(self):
        """
        Setup widgets to initial (default or defined) values on the atoms page.
        """
        # Set colors for atom color swatches
##        self.atom_hilite_color_frame.setPaletteBackgroundColor(RGBf_to_QColor(orange))

        #bruce 050805 new way (see comment in _setup_bonds_page):
        connect_colorpref_to_colorframe( atomHighlightColor_prefs_key, self.atom_hilite_color_frame)
        connect_colorpref_to_colorframe( bondpointHighlightColor_prefs_key, self.bondpoint_hilite_color_frame)
        connect_colorpref_to_colorframe( bondpointHotspotColor_prefs_key, self.hotspot_color_frame)

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

        # Set Ball & Stick Atom radius (percentage).  Mark 051003.
        self.cpk_atom_rad_spinbox.setValue(int (env.prefs[diBALL_AtomRadius_prefs_key] * 100.0))

        cpk_sf = env.prefs[cpkScaleFactor_prefs_key]
        # This slider generate signals whenever its 'setValue()' slot is called (below).
        # This creates problems (bugs) for us, so we disconnect it temporarily.
        self.disconnect(self.cpk_scale_factor_slider,SIGNAL("valueChanged(int)"),self.change_cpk_scale_factor)
        self.cpk_scale_factor_slider.setValue(int (cpk_sf * 200.0)) # generates signal
        self.connect(self.cpk_scale_factor_slider,SIGNAL("valueChanged(int)"),self.change_cpk_scale_factor)
        self.cpk_scale_factor_linedit.setText(str(cpk_sf))

        connect_checkbox_with_boolean_pref(
            self.keepBondsTransmuteCheckBox, keepBondsDuringTransmute_prefs_key)

        # I couldn't figure out a way to get a pref's default value without changing its current value.
        # Something like this would be very handy:
        #   default_cpk_sf = env.prefs.get_default_value(cpkScaleFactor_prefs_key)
        # Talk to Bruce about this. mark 060309.
        #
        # (I think there is a way, but I forget the details -- see some
        #  "restore defaults" code to look for a use of it. -- bruce 070831)

        if cpk_sf == 0.775: # Hardcoded for now.
            # Disable the reset button if the CPK Scale Factor is currently the default value.
            self.reset_cpk_scale_factor_btn.setEnabled(0)
        else:
            self.reset_cpk_scale_factor_btn.setEnabled(1)

        return

    def _setup_bonds_page(self):
        """
        Setup widgets to initial (default or defined) values on the bonds page.
        """
        # Set colors for bond color swatches


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

    def _setup_dna_page(self):
        """
        Setup widgets to initial (default or defined) values on the DNA page.
        """

        self.dnaBasesPerTurnDoubleSpinBox.setValue(
            env.prefs[bdnaBasesPerTurn_prefs_key])
        self.dnaRiseDoubleSpinBox.setValue(
            env.prefs[bdnaRise_prefs_key])

        connect_colorpref_to_colorframe(
            dnaDefaultSegmentColor_prefs_key, self.dnaDefaultSegmentColorFrame)

        # DNA strand arrowheads preferences
        connect_checkbox_with_boolean_pref(
            self.arrowsOnBackBones_checkBox,
            arrowsOnBackBones_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.arrowsOnThreePrimeEnds_checkBox,
            arrowsOnThreePrimeEnds_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.arrowsOnFivePrimeEnds_checkBox,
            arrowsOnFivePrimeEnds_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.strandThreePrimeArrowheadsCustomColorCheckBox,
            useCustomColorForThreePrimeArrowheads_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.strandFivePrimeArrowheadsCustomColorCheckBox,
            useCustomColorForFivePrimeArrowheads_prefs_key)

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

    def _setup_undo_page(self):
        """
        Setup widgets to initial (default or defined) values on the Undo page.
        """

        connect_checkbox_with_boolean_pref( self.undo_restore_view_checkbox, undoRestoreView_prefs_key )
        connect_checkbox_with_boolean_pref( self.undo_automatic_checkpoints_checkbox, undoAutomaticCheckpoints_prefs_key )
        self.undo_stack_memory_limit_spinbox.setValue( env.prefs[undoStackMemoryLimit_prefs_key] )

        # Hiding Undo Stack Memory Limit label and spinbox until Bruce hooks up the spinbox. mark 060406
        self.undo_stack_memory_limit_label.hide()
        self.undo_stack_memory_limit_spinbox.hide()

        #& History height widgets have been removed for A7, to be reinstituted at a later time, probably A8. mark 060314.
        #& self.history_height_lbl.hide()
        #& self.history_height_spinbox.hide()

        ## self.history_height_spinbox.setValue(self.history.history_height) #bruce 050810 removed this

        connect_checkbox_with_boolean_pref( self.msg_serial_number_checkbox, historyMsgSerialNumber_prefs_key )
        connect_checkbox_with_boolean_pref( self.msg_timestamp_checkbox, historyMsgTimestamp_prefs_key )

        #ninad060904
        self.historyHeight_spinbox.setValue(env.prefs[historyHeight_prefs_key] )

        return

    def _setup_window_page(self): #bruce 050810 revised this, and also call it from __init__ to be safe
        """
        Setup widgets to initial (default or defined) values on the window page.
        """

        # Update the max value of the Current Size Spinboxes
        screen = screen_pos_size()
        ((x0,y0),(w,h)) = screen
        self.current_width_spinbox.setRange(1,w)
        self.current_height_spinbox.setRange(1,h)

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

        return

    def _setup_tooltips_page(self): #Ninad 060830
        """
        Setup widgets to initialize (default or defined) values on the tooltips
        page.
        """
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
        prefix = str(self.caption_prefix_linedit.text())
        prefix = prefix.strip()
        if prefix:
            prefix = prefix + ' '
        env.prefs[captionPrefix_prefs_key] = prefix

        suffix = str(self.caption_suffix_linedit.text())
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

    def set_default_projection(self, projection):
        """
        Set the projection.

        @param projection: The projection, where:
                           - 0 = Perspective
                           - 1 = Orthographic
        @type  projection: int
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

    def change_mouseSpeedDuringRotation(self, val):
        """
        Slot that sets the factor controlling rotation speed during middle
        mouse drag 0.3(slow) and 1(fast).
        """
        env.prefs[mouseSpeedDuringRotation_prefs_key] = \
           self.mouseSpeedDuringRotation_slider.value() / 100.0

        val = self.mouseSpeedDuringRotation_slider.value()
        if val == 60:
            self.resetMouseSpeedDuringRotation_btn.setEnabled(0)
        else:
            self.resetMouseSpeedDuringRotation_btn.setEnabled(1)

    def reset_mouseSpeedDuringRotation(self):
        """
        Slot called when pressing the Mouse speed during rotation reset button.
        Restores the default value of the mouse speed.
        """
        env.prefs.restore_defaults([mouseSpeedDuringRotation_prefs_key])
        self.mouseSpeedDuringRotation_slider.setValue(int (env.prefs[mouseSpeedDuringRotation_prefs_key] * 100.0))
        self.resetMouseSpeedDuringRotation_btn.setEnabled(0)

    # [WARNING: bruce 060705 copied some of the following methods into MinimizeEnergyProp.py]
    def change_endrms(self, text):
        """
        Slot for EndRMS.
        This gets called each time a user types anything into the widget.
        """
        try:
            endrms_str = double_fixup(self.endrms_validator, self.endrms_linedit.text(), self.endrms)
            self.endrms_linedit.setText(endrms_str)
            if endrms_str:
                env.prefs[Adjust_endRMS_prefs_key] = float(str(endrms_str))
            else:
                env.prefs[Adjust_endRMS_prefs_key] = -1.0
            self.endrms = endrms_str
        except:
            print_compact_traceback("bug in change_endrms ignored: ") #bruce 060627

    def change_endmax(self, text):
        """
        Slot for EndMax.
        This gets called each time a user types anything into the widget.
        """
        try:
            endmax_str = double_fixup(self.endmax_validator, self.endmax_linedit.text(), self.endmax)
            self.endmax_linedit.setText(endmax_str)
            if endmax_str:
                env.prefs[Adjust_endMax_prefs_key] = float(str(endmax_str))
            else:
                env.prefs[Adjust_endMax_prefs_key] = -1.0
            self.endmax = endmax_str
        except:
            print_compact_traceback("bug in change_endmax ignored: ") #bruce 060627

    def change_cutoverrms(self, text):
        """
        Slot for Cutover RMS.
        This gets called each time a user types anything into the widget.
        """
        try:
            cutoverrms_str = double_fixup(self.cutoverrms_validator, self.cutoverrms_linedit.text(), self.cutoverrms)
            self.cutoverrms_linedit.setText(cutoverrms_str)
            if cutoverrms_str:
                env.prefs[Adjust_cutoverRMS_prefs_key] = float(str(cutoverrms_str))
            else:
                env.prefs[Adjust_cutoverRMS_prefs_key] = -1.0
            self.cutoverrms = cutoverrms_str
        except:
            print_compact_traceback("bug in change_cutoverrms ignored: ") #bruce 060627

    def change_cutovermax(self, text):
        """
        Slot for Cutover Max.
        This gets called each time a user types anything into the widget.
        """
        try:
            cutovermax_str = double_fixup(self.cutovermax_validator, self.cutovermax_linedit.text(), self.cutovermax)
            self.cutovermax_linedit.setText(cutovermax_str)
            if cutovermax_str:
                env.prefs[Adjust_cutoverMax_prefs_key] = float(str(cutovermax_str))
            else:
                env.prefs[Adjust_cutoverMax_prefs_key] = -1.0
            self.cutovermax = cutovermax_str
        except:
            print_compact_traceback("bug in change_cutovermax ignored: ") #bruce 060627


    def set_adjust_minimization_engine(self, engine):
        """
        Combobox action, sets Adjust_minimizationEngine preference
        """
        env.prefs[Adjust_minimizationEngine_prefs_key] = engine

    def setPrefsLogoDownloadPermissions(self, permission):
        """
        Set the sponsor logos download permissions in the persistent user
                preferences database.

        0 = Always ask before downloading, 1 = Never ask before downloading
        2 = Never download
        """
        if permission == 1:
            env.prefs[sponsor_permanent_permission_prefs_key] = True
            env.prefs[sponsor_download_permission_prefs_key] = True

        elif permission == 2:
            env.prefs[sponsor_permanent_permission_prefs_key] = True
            env.prefs[sponsor_download_permission_prefs_key] = False

        else:
            env.prefs[sponsor_permanent_permission_prefs_key] = False


    ########### BG Color slots ############

    def change_fill_type(self, ftype):
        """
        Slot called when the user changes the Fill Type.
        """
        if ftype == 'Solid':
            self.bg_solid_setup()
        else: # 'Blue Sky'
            self.bg_gradient_setup()

        self.glpane.gl_update()

    def bg_solid_setup(self):
        """
        Setup the BG color page for a solid fill type.
        """

        self.bg1_color_lbl.setEnabled(True)
        self.bg1_color_frame.setEnabled(True)
        self.choose_bg1_color_btn.setEnabled(True)

        self.fill_type_combox.setCurrentIndex(0) # Solid

        # Get the bg color rgb values of the glpane.

        plt = QtGui.QPalette()
        plt.setColor(QtGui.QPalette.Active,QtGui.QPalette.Window,
                     RGBf_to_QColor(self.glpane.backgroundColor))
        plt.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.Window,
                     RGBf_to_QColor(self.glpane.backgroundColor))
        plt.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.Window,
                     RGBf_to_QColor(self.glpane.backgroundColor))

        self.bg1_color_frame.setPalette(plt)

        self.glpane.setBackgroundGradient(False) # This also stores the pref in the db.
        self.glpane.setBackgroundColor(self.glpane.backgroundColor)

    def bg_gradient_setup(self):
        """
        Setup the Modes page for the background gradient fill type.
        """
        self.bg1_color_lbl.setEnabled(False)
        self.bg1_color_frame.setEnabled(False)
        self.choose_bg1_color_btn.setEnabled(False)

        self.fill_type_combox.setCurrentIndex(1) # Gradient

        # Get the bg color rgb values of the mode selected in the "Mode" combo box.

        plt = QtGui.QPalette()
        plt.setColor(QtGui.QPalette.Active,QtGui.QPalette.Window,
                     RGBf_to_QColor(self.glpane.backgroundColor))
        plt.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.Window,
                     RGBf_to_QColor(self.glpane.backgroundColor))
        plt.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.Window,
                     RGBf_to_QColor(self.glpane.backgroundColor))

        self.bg1_color_frame.setPalette(plt)


        self.glpane.setBackgroundGradient(True) # This also stores the pref in the db.

    def change_bg1_color(self):
        """
        Change a mode\'s primary background color.
        """
        # Allow user to select a new background color and set it.
        self.glpane.setBackgroundRole(QPalette.Window)

        ##self.bg1_color_frame.setBackgroundRole(QPalette.Window)
        c = QColorDialog.getColor(self.bg1_color_frame.palette().color(QPalette.Window), self)
        if c.isValid():
            plt = QtGui.QPalette()
            plt.setColor(QtGui.QPalette.Active,QtGui.QPalette.Window,c)
            plt.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.Window,c)
            plt.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.Window,c)
            self.bg1_color_frame.setPalette(plt)

            self.glpane.backgroundColor = QColor_to_RGBf(c)
            self.bg_solid_setup()

        self.glpane.gl_update()

    def restore_default_bgcolor(self):
        """
        Slot for "Restore Default Color" button, which restores the bg color
        and fill type.
        """

        self.glpane.restoreDefaultBackground()

        # Now update the UI.
        if self.glpane.backgroundGradient:
            self.bg_gradient_setup()
        else:
            self.bg_solid_setup()

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

    def setUI_LogoDownloadPermissions(self):
        """
        Set the sponsor logos download permissions in the user interface.
        """
        if env.prefs[sponsor_permanent_permission_prefs_key]:
            if env.prefs[sponsor_download_permission_prefs_key]:
                self.logoNeverAskRadioBtn.setChecked(True)
            else:
                self.logoNeverDownLoadRadioBtn.setChecked(True)
        else:
            self.logoAlwaysAskRadioBtn.setChecked(True)


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

    def change_ballstick_atom_radius(self, val):
        """
        Change the CPK (Ball and Stick) atom radius by % value <val>.
        """
        #bruce 060607 renamed change_cpk_atom_radius -> change_ballstick_atom_radius in this file and the .py/.ui dialog files.
        env.prefs[diBALL_AtomRadius_prefs_key] = val * .01
        self.glpane.gl_update() #k this gl_update is probably not needed and sometimes a slowdown [bruce 060607]

    def change_cpk_scale_factor(self, val):
        """
        Slot called when moving the slider.
        Change the % value displayed in the LineEdit widget for CPK Scale Factor.
        """
        sf = val * .005
        self.cpk_scale_factor_linedit.setText(str(sf))

    def save_cpk_scale_factor(self):
        """
        Slot called when releasing the slider.
        Saves the CPK (VdW) scale factor.
        """
        env.prefs[cpkScaleFactor_prefs_key] = self.cpk_scale_factor_slider.value() * .005
        self.glpane.gl_update()
        self.reset_cpk_scale_factor_btn.setEnabled(1)

    def reset_cpk_scale_factor(self):
        """
        Slot called when pressing the CPK Scale Factor reset button.
        Restores the default value of the CPK Scale Factor.
        """
        env.prefs.restore_defaults([cpkScaleFactor_prefs_key])
        self.cpk_scale_factor_slider.setValue(int (env.prefs[cpkScaleFactor_prefs_key] * 200.0))
            # generates signal (good), which calls slot save_cpk_scale_factor().
        self.reset_cpk_scale_factor_btn.setEnabled(0)

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
            dnaDefaultSegmentColor_prefs_key
        ])

        # These generate signals (good), which calls slots
        # save_dnaBasesPerTurn() and save_dnaRise()
        self.dnaBasesPerTurnDoubleSpinBox.setValue(env.prefs[bdnaBasesPerTurn_prefs_key])
        self.dnaRiseDoubleSpinBox.setValue(env.prefs[bdnaRise_prefs_key])

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

    ########## End of slot methods for "DNA" page widgets ###########

    ########## Slot methods for "Modes" page widgets ################

    def change_startup_mode(self, option):
        """
        Slot for the combobox that sets the Startup Mode.
        """
        env.prefs[ startupMode_prefs_key ] = startup_modes[self.startup_mode_combox.currentIndex()]
        return

    def change_default_mode(self, val):
        """
        Slot for the combobox that sets the Default Mode.
        """
        env.prefs[ defaultMode_prefs_key ] = default_modes[self.default_mode_combox.currentIndex()]
        self.glpane.currentCommand.UpdateDashboard() # Update Done button on dashboard.
        return

    def set_default_display_mode(self, display_style): #bruce 050810 revised this to set the pref immediately
        """
        Set the global display style at start up to I{display_style}.

        This also changes the global display style of the glpane to
        <display_style>.
        """
        if display_style == env.prefs[startupGlobalDisplayStyle_prefs_key]:
            return
        # set the pref
        env.prefs[startupGlobalDisplayStyle_prefs_key] = display_style

        # Set the current display mode in the glpane.
        # (This will be noticed later by chunk.draw of affected chunks.)
        self.glpane.setDisplay(display_style, True)
        self.glpane.gl_update()
        # (Note: no mt_update is needed, since per-node display style icons
        #  have not changed.)
        return

    ########## End of slot methods for "Modes" page widgets ###########

    ########## Slot methods for "Lighting" page widgets ################

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
        self._setup_lighting_page()

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
        # This has issues.  I intend to remove the Reset button for A7.  Confirm with Bruce.  Mark 051204.
        self._setup_material_group(reset = True)
        self._setup_lighting_page(self.original_lights)
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

        self._setup_lighting_page()
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
        env.prefs[gamess_path_prefs_key] = str(newValue)

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
        env.prefs[gromacs_path_prefs_key] = str(newValue)

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
                    "C:\\GROMACS_3.3.2+HDF5_p2\\bin\\mdrun.exe", \
                    "/Applications/GROMACS_3.3.2+HDF5_p2/bin/mdrun",
                    "/usr/local/GROMCAS_3.3.2+HDF5_p2/bin/mdrun")

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
        env.prefs[cpp_path_prefs_key] = str(newValue)

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
                    "C:\\GROMACS_3.3.2+HDF5_p2\\MCPP\\bin\\mcpp.exe", \
                    "/Applications/GROMACS_3.3.2+HDF5_p2/mcpp/bin/mcpp", \
                    "/usr/local/GROMACS_3.3.2+HDF5_p2/mcpp/bin/mcpp")

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
        env.prefs[nv1_path_prefs_key] = str(newValue)

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
        env.prefs[qutemol_path_prefs_key] = str(newValue)

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
        env.prefs[nanohive_path_prefs_key] = str(newValue)

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
        env.prefs[povray_path_prefs_key] = str(newValue)

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
        env.prefs[megapov_path_prefs_key] = str(newValue)

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
            env.prefs[povdir_path_prefs_key] = path = str( self.povdir_lineedit.text() ).strip()
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

    def change_use_selected_font(self, use_selected_font):
        """
        Slot for "Use Selected Font" checkbox on the groupbox.
        Called when the checkbox is toggled.
        """
        env.prefs[useSelectedFont_prefs_key] = use_selected_font
        self.set_font()

    def change_font(self, font):
        """
        Slot for the Font combobox.
        Called whenever the font is changed.
        """
        env.prefs[displayFont_prefs_key] = str(font.family())
        self.set_font()

    def change_fontsize(self, pointsize):
        """
        Slot for the Font size spinbox.
        """
        env.prefs[displayFontPointSize_prefs_key] = pointsize
        self.set_font()

    def change_selected_font_to_default_font(self):
        """
        Slot for "Make the selected font the default font" button.
        The default font will be displayed in the Font and Size
        widgets.
        """
        font = self.w.defaultFont
        env.prefs[displayFont_prefs_key] = str(font.family())
        env.prefs[displayFontPointSize_prefs_key] = font.pointSize()
        self.set_font_widgets(setFontFromPrefs = True) # Also sets the current display font.

        if debug_flags.atom_debug:
            print "change_selected_font_to_default_font(): " \
                  "Button clicked. Default font: ", font.family(), \
                  ", size=", font.pointSize()

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
            font_family = str(font.family())
                # note: this str() prevents NE1 from running on some international systems.
                # we should leave it in place until we can reproduce the bug,
                # then fix it. (Not necessarily by replacing it with unicode(),
                # since ideally we'd use str if it works, unicode if it doesn't.
                # Does string() do that??)
                # [bruce comment 080514]
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

        self.disconnect(self.selectedFontGroupBox,SIGNAL("toggled(bool)"), self.change_use_selected_font)
        self.disconnect(self.fontComboBox,SIGNAL("currentFontChanged (const QFont &)"), self.change_font)
        self.disconnect(self.fontSizeSpinBox,SIGNAL("valueChanged(int)"), self.change_fontsize)
        self.disconnect(self.makeDefaultFontPushButton,SIGNAL("clicked()"), self.change_selected_font_to_default_font)

        self.selectedFontGroupBox.setChecked(env.prefs[useSelectedFont_prefs_key]) # Generates signal!
        self.fontComboBox.setCurrentFont(font) # Generates signal!
        self.fontSizeSpinBox.setValue(font_size) # Generates signal!

        self.connect(self.selectedFontGroupBox,SIGNAL("toggled(bool)"), self.change_use_selected_font)
        self.connect(self.fontComboBox,SIGNAL("currentFontChanged (const QFont &)"), self.change_font)
        self.connect(self.fontSizeSpinBox,SIGNAL("valueChanged(int)"), self.change_fontsize)
        self.connect(self.makeDefaultFontPushButton,SIGNAL("clicked()"), self.change_selected_font_to_default_font)

        if setFontFromPrefs:
            self.set_font()

    def set_font(self):
        """
        Set the current display font using the font prefs.
        """

        use_selected_font = env.prefs[useSelectedFont_prefs_key]

        if use_selected_font:
            font = self.fontComboBox.currentFont()
            font_family = str(font.family())
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

    def change_color_theme(self, color_theme):
        """
        Slot for Color Theme combobox.
        Not implemented yet. Mark 2007-05-27.
        """
        print "change_color_theme(): Color theme = ", color_theme
        print "Not implemented yet."

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

    ########## Slot methods for "Undo" page widgets ################

    def set_history_height(self, height):
        print 'set_history_height: height =', height
        # HistoryWidget needs a new method to properly set the height of the widget given 'height'.
        # Needs research - not obvious how to do this.  Mark 050729.
        # self.history.set_height(height)

    ########## Slot methods for top level widgets ################

    def setup_current_page(self, pagename):
        #bruce 050817 fix new A6 bug introduced by Mark's fix of bug 894
        # (which was: lack of showing general page could reset gamess path to ""):
        # always call self._setup_general_page regardless of argument,
        # as well as the page named in the argument.
        try:
            if pagename != 'General':
                self._setup_general_page()
            # end of bruce 050817 fix

            if pagename == 'General':
                self._setup_general_page()
            elif pagename == 'Atoms':
                self._setup_atoms_page()
            elif pagename == 'Bonds':
                self._setup_bonds_page()
            elif pagename == 'DNA':
                self._setup_dna_page()
            elif pagename == 'Adjust':
                self._setup_adjust_page()
            elif pagename == 'Lighting':
                self._setup_lighting_page()
            elif pagename == 'Plug-ins':
                self._setup_plugins_page()
            elif pagename == 'Undo':
                self._setup_undo_page()
            elif pagename == 'Window':
                self._setup_window_page()
            elif pagename == 'ToolTips':
                self._setup_tooltips_page()

            else:
                print 'Error: Preferences page unknown: ', pagename
        except:
            print_compact_traceback("bug in setup_current_page ignored: ") #bruce 060627

    def accept(self):
        """
        The slot method for the 'OK' button.
        """
        # self._update_prefs() # Mark 050919
        QDialog.accept(self)

    def reject(self):
        """
        The slot method for the "Cancel" button.
        """
        # The Cancel button has been removed, but this still gets called
        # when the user hits the dialog's "Close" button in the dialog's window border (upper right X).
        # Since I've not implemented 'Cancel', it is safer to go ahead and
        # save all preferences anyway.  Otherwise, any changed preferences
        # will not be persistent (after this session).
        # This will need to be removed when we implement a true cancel function.
        # Mark 050629.
        # self._update_prefs() # Removed by Mark 050919.
        QDialog.reject(self)

    pass # end of class UserPrefs

# end
