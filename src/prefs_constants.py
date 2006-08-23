# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
prefs_constants.py

Constants and utilities related to user preferences,
which need to be defined immediately upon startup.

$Id$

History:

Mark 050629 moved some A6 prefs keys he had earlier defined and organized
in UserPrefs.py, into constants.py.

Bruce 050805 moved those into this new file, and added more.

'''
__author__ = ['Mark', 'Bruce']

### do no imports that would not be ok for constants.py to do! ###

from constants import *

# ==

# Compass position constants.  These are used to preserve the preference value
# for the compass position and relate directly to the radio button group values for the options 
# presented in the Prefences/General dialog.  Do not change the value of these 4 constants!
# Mark 050919.
UPPER_RIGHT = 0
UPPER_LEFT = 1
LOWER_LEFT = 2
LOWER_RIGHT = 3

# View Projection Types
PERSPECTIVE = 0
ORTHOGRAPHIC = 1

# Grid Plan Grid Line Types
NO_LINE = 0
SOLID_LINE = 1
DASHED_LINE = 2
DOTTED_LINE = 3

# Grid Plane Grid Types
SQUARE_GRID = 0
SiC_GRID = 1

# ==

# Keys for user preferences
# (the string constants should start with the first released version they'll appear in)

# General prefs
displayCompass_prefs_key = 'A6/Display Compass'
displayCompassLabels_prefs_key = 'A7/Display Compass Label'
compassPosition_prefs_key = 'A6/Compass Position'
displayOriginAxis_prefs_key = 'A6/Display Origin Axis'
displayPOVAxis_prefs_key = 'A6/Display POV Axis'
defaultProjection_prefs_key = 'A7/Default Projection'
animateHighQualityGraphics_prefs_key = 'A7/Animate with High Quality Graphics' #mark 060315. NIY.
animateStandardViews_prefs_key = 'A7/Animate Standard Views'
animateMaximumTime_prefs_key = 'A7/Maximum Animation Time'
workingDirectory_prefs_key = 'WorkingDirectory' # Moved here from startup_funcs.py. Mark 060726.
backgroundColor_prefs_key = 'A9/Background Color' # Mark 060814.
backgroundGradient_prefs_key = 'A9/Background Gradient' # Mark 060814.
defaultDisplayMode_prefs_key = 'A9/Default Display Mode' # Mark 060815.

dynamicToolTipWakeUpDelay_prefs_key = 'A9/DynamicToolTip Wake Up Delay'
dynamicToolTipAtomDistancePrecision_prefs_key = 'A9/DynamicToolTip Atom Distance Precision'
dynamicToolTipBendAnglePrecision_prefs_key = 'A9/DynamicToolTip Bend Angle Precision'
dynamicToolTipTorsionAnglePrecision_prefs_key = 'A9/DynamicToolTip Torsion Angle Precision'
dynamicToolTipAtomChunkInfo_prefs_key = 'A9/DynamicToolTip Atom Chunk Info'
dynamicToolTipBondChunkInfo_prefs_key = 'A9/DynamicToolTip Bond Chunk Info'
dynamicToolTipAtomPosition_prefs_key = 'A9/DynamicToolTip Atom Position'
dynamicToolTipAtomDistanceDeltas_prefs_key = 'A9/DynamicToolTip Atom Distance Deltas'
dynamicToolTipBondLength_prefs_key = 'A9/DynamicToolTip Bond Length'

# Minimize prefs for Adjust All and Adjust Selection (presently on General prefs pane)
# (note, Adjust Atoms does not yet have its own prefs -- its values are derived from these
#  but differently than for Adjust All/Sel)
#mark 060627, revised by bruce 060628, 060705 for A8
Adjust_watchRealtimeMinimization_prefs_key = 'A7/Watch Realtime Minimization' # same key as in A7
Adjust_endRMS_prefs_key = 'A8/End RMS Adjust'
Adjust_endMax_prefs_key = 'A8/End Max Adjust'
Adjust_cutoverRMS_prefs_key = 'A8/Cutover RMS Adjust'
Adjust_cutoverMax_prefs_key = 'A8/Cutover Max Adjust'

# Minimize prefs for Minimize Energy dialog (independent settings, different defaults) [bruce 060705]
Minimize_watchRealtimeMinimization_prefs_key = 'A8/Watch Realtime Minimization Minimize'
Minimize_endRMS_prefs_key = 'A8/End RMS Minimize' 
Minimize_endMax_prefs_key = 'A8/End Max Minimize'
Minimize_cutoverRMS_prefs_key = 'A8/Cutover RMS Minimize'
Minimize_cutoverMax_prefs_key = 'A8/Cutover Max Minimize'

# Atom prefs
atomHighlightColor_prefs_key = 'A6/Atom Highlight Color'
bondpointHighlightColor_prefs_key = 'A7/Bondpoint Highlight Color'
bondpointHotspotColor_prefs_key = 'A6/Atom Hotspot Color'
defaultDisplayMode_prefs_key = 'A6/Default Display Mode'
diBALL_AtomRadius_prefs_key = 'A7/CPK Atom Radius Percentage' # this is about diBALL which as of 060307 is called Ball and Stick in UI
    #bruce 060607 renamed cpkAtomRadius_prefs_key -> diBALL_AtomRadius_prefs_key ###DOIT
cpkScaleFactor_prefs_key = 'A7/CPK Scale Factor' # this is about diTrueCPK which as of 060307 is called CPK in UI
levelOfDetail_prefs_key = 'A7/Level Of Detail'

# Bond prefs
bondHighlightColor_prefs_key = 'A6/Bond Highlight Color'
bondStretchColor_prefs_key = 'A6/Bond Stretch Color'
bondVaneColor_prefs_key = 'A6/Bond Vane Color'
diBALL_bondcolor_prefs_key = 'A6/Bond CPK Color' # this is about diBALL, not CPK [bruce 060607 comment]
    #bruce 060607 renamed bondCPKColor_prefs_key -> diBALL_bondcolor_prefs_key ###DOIT
pibondStyle_prefs_key = 'A6/Pi Bond Style'
pibondLetters_prefs_key = 'A6/Pi Bond Letters'
showValenceErrors_prefs_key = 'A6/Show Valence Errors'
#display lines mode line thickness, mark 050831
linesDisplayModeThickness_prefs_key = 'A7/Line Thickness for Lines Display Mode'
#CPK cylinder radius (percentage), mark 051003
diBALL_BondCylinderRadius_prefs_key = 'A7/CPK Cylinder Radius Percentage' # about diBALL, called Ball and Stick as of 060307
    #bruce 060607 renamed cpkCylinderRadius_prefs_key -> diBALL_BondCylinderRadius_prefs_key ###DOIT

# Modes prefs [added by mark 050910]
# The background style and color for each mode is initialized in init_prefs()
# of the superclass basicMode (modes.py).
startupMode_prefs_key = 'A7/Startup Mode'
defaultMode_prefs_key = 'A7/Default Mode'
buildModeAutobondEnabled_prefs_key = 'A7/Build Mode Autobond Enabled' # mark 060203.
buildModeWaterEnabled_prefs_key = 'A7/Build Mode Water Enabled' # mark 060203.
buildModeHighlightingEnabled_prefs_key = 'A7/Build Mode Highlighting Enabled' # mark 060203.
buildModeSelectAtomsOfDepositedObjEnabled_prefs_key = 'A7/Build Mode Select Atoms of Deposited Obj Enabled' # mark 060304.

# Lighting prefs [most added by mark 051124 or later]
## old_glpane_lights_prefs_key = "glpane lighting" #bruce 051206 moved this here from GLPane;
    # it was hardcoded in two methods in GLPane; maybe dates from before prefs_constants module;
    # in the next commit it was abandoned and changed as a fix of bug 1181; see comments near its uses in GLPane.
glpane_lights_prefs_key = 'A7/glpane lighting' #bruce 051206 introduced this key to fix bug 1181
light1Color_prefs_key = 'A7/Light1 Color' #bruce 051206 comment: this looks redundant with elements in GLPane._lights; why?
light2Color_prefs_key = 'A7/Light2 Color'
light3Color_prefs_key = 'A7/Light3 Color'
material_specular_highlights_prefs_key = 'A7/Material Specular Highlights'
material_specular_finish_prefs_key = 'A7/Material Specular Finish'
material_specular_shininess_prefs_key = 'A7/Material Specular Shininess'
material_specular_brightness_prefs_key = 'A7/Material Specular Brightness'

# File management / filename / URL preferences [tentative category, added by bruce 051130, more comments below]
wiki_help_prefix_prefs_key = 'A7/Wiki Help Prefix'

# Plug-ins prefs [added by mark 050918]
nanohive_path_prefs_key = 'A7/Nano-Hive Executable Path'
nanohive_enabled_prefs_key = 'A7/Nano-Hive Enabled'
povray_path_prefs_key = 'A8/POV-Ray Executable Path'
povray_enabled_prefs_key = 'A8/POV-Ray Enabled'
megapov_path_prefs_key = 'A8/MegaPOV Executable Path'
megapov_enabled_prefs_key = 'A8/MegaPOV Enabled'
povdir_path_prefs_key = 'A8/POV Include Directory' # only in Mac A8, for Windows will be in A8.1 (Linux??) [bruce 060710]
povdir_enabled_prefs_key = 'A8/POV Include Directory Enabled' # ditto, and might not end up being used [bruce 060710]
gmspath_prefs_key = 'A6/GAMESS Path'
gamess_enabled_prefs_key = 'A7/GAMESS Enabled'


# Undo and History prefs
undoRestoreView_prefs_key = 'A7/Undo Restore View'
undoAutomaticCheckpoints_prefs_key = 'A7/Undo Automatic Checkpoints'
undoStackMemoryLimit_prefs_key = 'A7/Undo Stack Memory Limit'
historyHeight_prefs_key = 'A6/History Height'
historyMsgSerialNumber_prefs_key = 'A6/History Message Serial Number'
historyMsgTimestamp_prefs_key = 'A6/History Message Timestamp'

# Window prefs (used to be called Caption prefs)
rememberWinPosSize_prefs_key = "A7/Remember Window Pos and Size" #mark 060315. NIY.
mainwindow_geometry_prefs_key_prefix = "main window/geometry" #bruce 051218 moved this from debug.py
captionPrefix_prefs_key = 'A6/Caption Prefix'
captionSuffix_prefs_key = 'A6/Caption Suffix'
captionFullPath_prefs_key = 'A6/Caption Full Path'

# Bug-workaround prefs, Mac-specific

QToolButton_MacOSX_Tiger_workaround_prefs_key = 'A6/QToolButton MacOSX Tiger workaround' #bruce 050810
sponsor_download_permission_prefs_key = 'A8/Sponsor download permission'
sponsor_permanent_permission_prefs_key = 'A8/Sponsor download permission is permanent'

#==

# List of prefs keys (strings, not _prefs_key global variable names)
# which got stored into developers or users prefs dbs (since they were saved in code committed to cvs),
# but are no longer used now.
#   This list is not yet used by the code, and when it is, its format might be revised,
# but for now, make sure each line has a comment which gives complete info
# about whether or not a released version ever stored prefs using the given keys
# (and if so, exactly which released versions);
# also, each line should be signed with a name and date of the abandonment of that key.

###@@@ THIS IS NOT COMPLETE since I didn't have time to add the ones I removed from cvs rev 1.62 just before A8.
# I also forgot to remove some recently when I renamed them from A8 devel to A8 devel2. -- bruce 060705

_abandoned_prefs_keys = [
    'A7/Specular Highlights', # never released, superceded by 'A7/Material Specular Highlights' [mark 051205]
    'A7/Whiteness', # never released, superceded by 'A7/Material Specular Finish' [mark 051205]
    'A7/Shininess', # never released, superceded by 'A7/Material Specular Shininess' [mark 051205]
    'A7/Material Brightness', # never released, superceded by 'A7/Material Specular Brightness' [mark 051205]
    'glpane lighting', # was released in A6 and maybe some prior versions; superceded by 'A7/glpane lighting' [bruce 051206]
    'A7/Selection Behavior', # only released in pre-release snapshots of A7. [mark 060304]
    'A7/Select Atoms Mode Highlighting Enabled' # only released in pre-release snapshots of A7. [mark 060404]
    ]

#==

# Table of internal attribute names, default values, types, and prefs-db formats for some of these preferences.
# (This needs to be defined in a central place, and set up by code in preferences.py
#  before any code can ask for preference values, so the default values can come from here.)

# computed default values; some of these names are also directly used by external code
# which is not yet fully revised to get the values from the prefs db.

_default_HICOLOR_real_atom = yellow
_default_HICOLOR_real_bond = yellow
_default_HICOLOR_bondpoint = LEDon ## pink


_default_toolong_color = ave_colors( 0.8, red, black) #bruce 050727 changed this from pure red; 050805 even for lines mode
_default_toolong_hicolor = ave_colors( 0.8, magenta, black) ## not yet in prefs db

def _compute_default_bondVaneColor():
    ord_pi_for_color = 0.5
        # was ord_pi, when we let the color vary with ord_pi;
        # if we later want that, then define two colors here and use them as endpoints of a range
    color = ave_colors(ord_pi_for_color, blue, gray)
    return ave_colors(0.8, color, black)

_default_bondVaneColor = _compute_default_bondVaneColor()

_default_bondColor = (0.25, 0.25, 0.25)

# Do not move getDefaultWorkingDirectory() to platform.py since it might create a recursive import problem. 
# Mark 060730.
def getDefaultWorkingDirectory(): 
    """Returns the default Working Directory.
    """
    import sys, os
    wd = ''
    if sys.platform == 'win32': # Windows
        # e.g. "C:\Documents and Settings\Mark\My Documents"
        wd = os.path.normpath(os.path.expanduser("~/My Documents"))
        # Check <wd> since some Windows OSes (i.e. Win95) may not have "~\My Documents".
        if not os.path.isdir(wd): 
            wd = os.path.normpath(os.path.expanduser("~"))
    else: # Linux and MacOS
        # e.g. "/usr/mark"
        wd = os.path.normpath(os.path.expanduser("~"))
    if os.path.isdir(wd):
        return wd
    else:
        print "getDefaultWorkingDirectory(): default working directory [", \
              wd , "] does not exist. Setting default working directory to [.]"
        return "."

_default_workingDirectory = getDefaultWorkingDirectory()

# the actual table (for doc, see the code that interprets it, in preferences.py)

prefs_table = (
    # entries are: (attribute name, prefs type-and-db-format code, prefs key, optional default value)
    ##e add categories or tags?
    
    # General preferences [added to this table by mark 050919] 

    ('display_compass', 'boolean', displayCompass_prefs_key, True),
    ('display_compass_labels', 'boolean', displayCompassLabels_prefs_key, True),
    ('display_position', 'int', compassPosition_prefs_key, UPPER_RIGHT),
    ('display_origin_axis', 'boolean', displayOriginAxis_prefs_key, True),
    ('display_pov_axis', 'boolean', displayPOVAxis_prefs_key, True),
    ('default_projection', 'int', defaultProjection_prefs_key, ORTHOGRAPHIC), # Changed to Ortho. Mark 051029.
    ('animate_high_quality', 'boolean', animateHighQualityGraphics_prefs_key, True), # Mark 060315. NIY.
    ('animate_std_views', 'boolean', animateStandardViews_prefs_key, True), # Mark 051110.
    ('animate_max_time', 'float', animateMaximumTime_prefs_key, 1.0), # 1 second.  Mark 060124.
    ('working_directory', 'string', workingDirectory_prefs_key,  _default_workingDirectory ), # Mark 060726.
    ('background_color', 'color', backgroundColor_prefs_key, white),
    ('background_gradient', 'int', backgroundGradient_prefs_key, 1), # 1 = Sky Blue . Mark 060814.
    ('default_display_mode', 'int', defaultDisplayMode_prefs_key, diTUBES), # Mark 060815.

    # Minimize prefs (some are in General prefs pane, some are in dialogs)
    # [mark 060627, revised & extended by bruce 060628, 060705 for A8]
    # (none yet are specific to Adjust Atoms aka Local Minimize)
    
    ('', 'boolean', Adjust_watchRealtimeMinimization_prefs_key, True),
    ('', 'float', Adjust_endRMS_prefs_key, 100.0), # WARNING: this value may also be hardcoded in runSim.py
    ('', 'float', Adjust_endMax_prefs_key, -1.0), # -1.0 means blank lineedit widget, and actual value is computed from other prefs
    ('', 'float', Adjust_cutoverRMS_prefs_key, -1.0),
    ('', 'float', Adjust_cutoverMax_prefs_key, -1.0),
    
    ('', 'boolean', Minimize_watchRealtimeMinimization_prefs_key, True), 
    ('', 'float', Minimize_endRMS_prefs_key, +1.0), # WARNING: this value may also be hardcoded in runSim.py
    ('', 'float', Minimize_endMax_prefs_key, -1.0), 
    ('', 'float', Minimize_cutoverRMS_prefs_key, -1.0), 
    ('', 'float', Minimize_cutoverMax_prefs_key, -1.0), 
    
    # Atom preferences - colors (other than element colors, handled separately)

    ('atom_highlight_color', 'color', atomHighlightColor_prefs_key, _default_HICOLOR_real_atom ),
    ('bondpoint_highlight_color', 'color', bondpointHighlightColor_prefs_key, _default_HICOLOR_bondpoint),
    ('bondpoint_hotspot_color', 'color', bondpointHotspotColor_prefs_key, ave_colors( 0.8, green, black) ), #bruce 050808
    
    ## ('openbond_highlight_color',  'color', xxx_prefs_key, HICOLOR_singlet ), ## pink [not yet in prefs db]
    
    # Atom preferences - other
    
    ('', 'float', diBALL_AtomRadius_prefs_key, 1.0), #mark 051003 [about Ball and Stick]
    ('cpk_scale_factor', 'float', cpkScaleFactor_prefs_key, 0.775), #mark 060307 [about diTrueCPK, called CPK in UI as of now]
    ('display_mode', 'int', defaultDisplayMode_prefs_key, diTUBES), # Changed from diTrueCPK to diTUBES. mark 060218.
    ('level_of_detail', 'int', levelOfDetail_prefs_key, -1), # -1 = Variable . mark & bruce 060215.
    
    # Bond preferences - colors
    
    ('bond_highlight_color',         'color', bondHighlightColor_prefs_key, _default_HICOLOR_real_bond),
    ('bond_stretch_color',           'color', bondStretchColor_prefs_key, _default_toolong_color),
    ## ('bond_stretch_highlight_color', 'color', xxx_prefs_key, _default_toolong_hicolor), ## [not yet in prefs db]
    ('pi_vane_color',                'color', bondVaneColor_prefs_key, _default_bondVaneColor),
    ('',               'color', diBALL_bondcolor_prefs_key, _default_bondColor),

    # Bond preferences - other

    ('pi_bond_style',   ['multicyl','vane','ribbon'],  pibondStyle_prefs_key,   'multicyl' ),
    ('pi_bond_letters', 'boolean',                     pibondLetters_prefs_key, False ),
    ('show_valence_errors',        'boolean', showValenceErrors_prefs_key,   True ), #bruce 050806 made this up
    ('', 'int', linesDisplayModeThickness_prefs_key, 1), #mark 050831 made this up
    ('', 'float', diBALL_BondCylinderRadius_prefs_key, 1.0), #mark 051003
    
    # Modes preferences [added to this table by mark 050910]
    
    ('startup_mode', 'string', startupMode_prefs_key,   '$DEFAULT_MODE' ),
    ('default_mode', 'string', defaultMode_prefs_key,   'DEPOSIT' ), # as suggested by Eric.  Mark 051028.
    ('buildmode_autobond', 'boolean', buildModeAutobondEnabled_prefs_key, True ), # mark 060203.
    ('buildmode_water', 'boolean', buildModeWaterEnabled_prefs_key, False ), # mark 060218.
    ('buildmode_highlighting', 'boolean', buildModeHighlightingEnabled_prefs_key, True ), # mark 060203.
    ('buildmode_selectatomsdepositobj', 'boolean', buildModeSelectAtomsOfDepositedObjEnabled_prefs_key, False ), # mark 060310.
    
    # Lighting preferences [added to this table by mark 051124]
    # If any default light colors are changed here, you must also change the color of 
    # the light in '_lights' in GLPane to keep them synchronized.  Mark 051204.
    ('light1_color', 'color', light1Color_prefs_key, white ),
    ('light2_color', 'color', light2Color_prefs_key, white ),
    ('light3_color', 'color', light3Color_prefs_key, white ),
    # Material specular properties.
    ('ms_highlights', 'boolean', material_specular_highlights_prefs_key, True),
    ('ms_finish', 'float', material_specular_finish_prefs_key, 0.5),
    ('ms_shininess', 'float', material_specular_shininess_prefs_key, 35.0), 
    ('ms_brightness', 'float', material_specular_brightness_prefs_key, 1.0), #bruce 051203 bugfix: default value should be 1.0

    # File management / filename / URL preferences [added by bruce 051130; category is a guess, doesn't have prefs UI page yet]

    ('', 'string', wiki_help_prefix_prefs_key, "http://www.nanoengineer-1.net/mediawiki/index.php?title=" ),

    # Plug-ins preferences [added to this table by mark 050919]
    
    ('nanohive_exe_path', 'string', nanohive_path_prefs_key, "" ),
    ('nanohive_enabled', 'boolean', nanohive_enabled_prefs_key, False ),
    ('povray_exe_path', 'string', povray_path_prefs_key, "" ),
    ('povray_enabled', 'boolean', povray_enabled_prefs_key, False ),
    ('megapov_exe_path', 'string', megapov_path_prefs_key, "" ),
    ('megapov_enabled', 'boolean', megapov_enabled_prefs_key, False ),
    ('povdir_path', 'string', povdir_path_prefs_key, "" ), #bruce 060710
    ('povdir_enabled', 'boolean', povdir_enabled_prefs_key, False ), #bruce 060710
    ('gamess_exe_path', 'string', gmspath_prefs_key, "" ),
    ('gamess_enabled', 'boolean', gamess_enabled_prefs_key, False ),
    

    # Undo and History preferences [added to this table by bruce 050810]
    ('', 'boolean', undoRestoreView_prefs_key, False), # mark 060314
    ('', 'boolean', undoAutomaticCheckpoints_prefs_key, True), # mark 060314
    ('', 'int', undoStackMemoryLimit_prefs_key, 100), # mark 060327
    ('', 'boolean', historyMsgSerialNumber_prefs_key, True),
    ('', 'boolean', historyMsgTimestamp_prefs_key, True),
    
    # Window preferences [added to this table by bruce 050810]
    
    ('', 'boolean', rememberWinPosSize_prefs_key, False), # mark 060315. NIY.
    ('', 'string', captionPrefix_prefs_key, "" ),
    ('', 'string', captionSuffix_prefs_key, "*" ),
    ('', 'boolean', captionFullPath_prefs_key, False ),
    
    # ...

    ('', 'boolean', QToolButton_MacOSX_Tiger_workaround_prefs_key, False ), #bruce 050810
    ('', 'boolean', sponsor_download_permission_prefs_key, False ),
    ('', 'boolean', sponsor_permanent_permission_prefs_key, False ),
    
    # Dynamic Tooltip preferences [added to this table by ninad 060818
    ('wake_up_delay', 'float', dynamicToolTipWakeUpDelay_prefs_key, 1.0), # 1 second. Mark 060817.
    ('atom_distance_precision', 'int', dynamicToolTipAtomDistancePrecision_prefs_key, 3), # number of decimal places  ninad 060821
    ('bend_angle_precision', 'int', dynamicToolTipBendAnglePrecision_prefs_key, 3), # number of decimal places 
    
    #Make the following false by default ninad060818. True - For testing only
     ('atom_chunk_info', 'boolean', dynamicToolTipAtomChunkInfo_prefs_key, True), # checkbox for displaying chunk name an atom belongs to
     ('bond_chunk_info', 'boolean', dynamicToolTipBondChunkInfo_prefs_key, True), # checkbox -chunk name(s) of the two atoms in the bond
     
     #Make the following false by default ninad060818. True - For testing only
     ('atom_position', 'boolean', dynamicToolTipAtomPosition_prefs_key, True), #checkbox for displaying xyz pos
     ('atom_distance_deltas', 'boolean', dynamicToolTipAtomDistanceDeltas_prefs_key, True), # check box to display xyz deltas
      ('bond_length', 'boolean', dynamicToolTipBondLength_prefs_key, True), # displays the bond length (precision determined by atom distance precision) @@@ ninad060823: It only returns the nuclear distance between the bonded atoms doesn't return covalent bond length.
      
     #=== Start of NIYs ninad060822===#
    ('torsion_angle_precision', 'int', dynamicToolTipTorsionAnglePrecision_prefs_key, 3), # number of decimal places 
    #===End of NIYs ninad060822 ===#

)

# end