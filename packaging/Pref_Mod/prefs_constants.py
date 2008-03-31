# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
prefs_constants.py

Constants and utilities related to user preferences,
which need to be defined immediately upon startup.

@author: Mark, Bruce, Ninad
@version: $Id: prefs_constants.py 11951 2008-03-14 04:44:50Z ericmessick $
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

Mark 050629 moved some A6 prefs keys he had earlier defined and organized
in UserPrefs.py, into constants.py.

Bruce 050805 moved those into this new file, and added more.

Module classification:

"utilities" or perhaps "constants" for now, even though it can be
thought of as containing app-specific knowledge; for reasons and caveats
and desirable refactoring, see preferences.py docstring. The reason it
is even lower than foundation is to avoid package import cycles, e.g. if
foundation -> io -> this, or if utilities.GlobalPreferences imports this.
[bruce 071215]

Refactoring needed:

- See preferences.py docstring.

- Has a few functions that ought to be split out, like
getDefaultWorkingDirectory.
"""

import sys, os # for getDefaultWorkingDirectory


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
##defaultDisplayMode_prefs_key = 'A9/Default Display Mode' # Mark 060815.
    # [disabled since assigned differently below -- bruce 080212]
mouseSpeedDuringRotation_prefs_key = 'A9/Mouse Speed During Rotation' #Ninad 060906
displayOriginAsSmallAxis_prefs_key = 'A9/Display Origin As Small Axis' #Ninad 060920
zoomAboutScreenCenter_prefs_key = 'A9/Zoom To Screen Center' #Ninad 060926
displayRulers_prefs_key = 'A10/Display rulers'
displayVertRuler_prefs_key = 'A10/Display vertical ruler'
displayHorzRuler_prefs_key = 'A10/Display horizontal ruler'
rulerPosition_prefs_key = 'A10/Ruler Position'
rulerColor_prefs_key = 'A10/Ruler Color'
rulerOpacity_prefs_key = 'A10/Ruler Opacity'
showRulersInPerspectiveView_prefs_key = 'A10/Show Rulers In Perspective View'

#ToolTip Prefs
dynamicToolTipWakeUpDelay_prefs_key = 'A9/DynamicToolTip Wake Up Delay'
dynamicToolTipAtomDistancePrecision_prefs_key = 'A9/DynamicToolTip Atom Distance Precision'
dynamicToolTipBendAnglePrecision_prefs_key = 'A9/DynamicToolTip Bend Angle Precision'
dynamicToolTipTorsionAnglePrecision_prefs_key = 'A9/DynamicToolTip Torsion Angle Precision'
dynamicToolTipAtomChunkInfo_prefs_key = 'A9/DynamicToolTip Atom Chunk Info'
dynamicToolTipBondChunkInfo_prefs_key = 'A9/DynamicToolTip Bond Chunk Info'
dynamicToolTipAtomPosition_prefs_key = 'A9/DynamicToolTip Atom Position'
dynamicToolTipAtomDistanceDeltas_prefs_key = 'A9/DynamicToolTip Atom Distance Deltas'
dynamicToolTipBondLength_prefs_key = 'A9/DynamicToolTip Bond Length'
dynamicToolTipAtomMass_prefs_key = 'A9/DynamicToolTip Atom Mass'
dynamicToolTipVdwRadiiInAtomDistance_prefs_key = 'A10/tooltip Vdw Radii In Atom Distance'


# Minimize prefs for Adjust All and Adjust Selection (presently on General prefs pane)
# (note, Adjust Atoms does not yet have its own prefs -- its values are derived from these
#  but differently than for Adjust All/Sel)
#mark 060627, revised by bruce 060628, 060705 for A8
Adjust_watchRealtimeMinimization_prefs_key = 'A7/Watch Realtime Minimization' # same key as in A7
Adjust_endRMS_prefs_key = 'A8/End RMS Adjust'
Adjust_endMax_prefs_key = 'A8/End Max Adjust'
Adjust_cutoverRMS_prefs_key = 'A8/Cutover RMS Adjust'
Adjust_cutoverMax_prefs_key = 'A8/Cutover Max Adjust'

Adjust_minimizationEngine_prefs_key = 'A10/Adjust Minimization Engine'

#Ninad 20070509 Adjust , Minimize and Simulation(Dynamics) Preferences for DNA 
#reduced model(Enable or disable elecrostatics)
electrostaticsForDnaDuringAdjust_prefs_key = 'A9/ Electrostatics for Dna During Adjust'
electrostaticsForDnaDuringMinimize_prefs_key = 'A9/ Electrostatics For Dna During Minimize'
electrostaticsForDnaDuringDynamics_prefs_key = 'A9/ Electrostatics For Dna During Simulation'

# Minimize prefs for Minimize Energy dialog (independent settings, different defaults) [bruce 060705]
Minimize_watchRealtimeMinimization_prefs_key = 'A8/Watch Realtime Minimization Minimize'
Minimize_endRMS_prefs_key = 'A8/End RMS Minimize' 
Minimize_endMax_prefs_key = 'A8/End Max Minimize'
Minimize_cutoverRMS_prefs_key = 'A8/Cutover RMS Minimize'
Minimize_cutoverMax_prefs_key = 'A8/Cutover Max Minimize'

Minimize_minimizationEngine_prefs_key = 'A10/Minimize Minimization Engine'

# Pref to add potential energy to trace file
Potential_energy_tracefile_prefs_key = 'A8/Potential energy checkbox'

# Atom prefs
atomHighlightColor_prefs_key = 'A6/Atom Highlight Color'
deleteAtomHighlightColor_prefs_key = 'A10/Delete Atom Highlight Color'
bondpointHighlightColor_prefs_key = 'A7/Bondpoint Highlight Color'
bondpointHotspotColor_prefs_key = 'A6/Atom Hotspot Color'
defaultDisplayMode_prefs_key = 'A6/Default Display Mode'
diBALL_AtomRadius_prefs_key = 'A7/CPK Atom Radius Percentage' # this is about diBALL which as of 060307 is called Ball and Stick in UI
    #bruce 060607 renamed cpkAtomRadius_prefs_key -> diBALL_AtomRadius_prefs_key ###DOIT
cpkScaleFactor_prefs_key = 'A7/CPK Scale Factor' # this is about diTrueCPK which as of 060307 is called CPK in UI
levelOfDetail_prefs_key = 'A7/Level Of Detail'
keepBondsDuringTransmute_prefs_key = 'A9/Keep Bonds During Transmute'

# Bond prefs
bondHighlightColor_prefs_key = 'A6/Bond Highlight Color'
deleteBondHighlightColor_prefs_key = 'A10/Delete Bond Highlight Color'
bondStretchColor_prefs_key = 'A6/Bond Stretch Color'
bondVaneColor_prefs_key = 'A6/Bond Vane Color'
diBALL_bondcolor_prefs_key = 'A6/Bond CPK Color' # this is about diBALL, not CPK [bruce 060607 comment]
    #bruce 060607 renamed bondCPKColor_prefs_key -> diBALL_bondcolor_prefs_key ###DOIT
showBondStretchIndicators_prefs_key = 'A9/ Show Bond Stretch Indicators'
pibondStyle_prefs_key = 'A6/Pi Bond Style'
pibondLetters_prefs_key = 'A6/Pi Bond Letters'
showValenceErrors_prefs_key = 'A6/Show Valence Errors'
#display lines mode line thickness, mark 050831
linesDisplayModeThickness_prefs_key = 'A7/Line Thickness for Lines Display Mode'
#CPK cylinder radius (percentage), mark 051003
diBALL_BondCylinderRadius_prefs_key = 'A7/CPK Cylinder Radius Percentage' # about diBALL, called Ball and Stick as of 060307
    #bruce 060607 renamed cpkCylinderRadius_prefs_key -> diBALL_BondCylinderRadius_prefs_key ###DOIT
diDNACYLINDER_BondCylinderRadius_prefs_key = 'A10/DNA Cylinder Bond Radius Percentage' 

# DNA prefs
adnaBasesPerTurn_prefs_key = 'A10/A-DNA bases per turn' # Twist computed from this.
adnaRise_prefs_key = 'A10/A-DNA rise step'
bdnaBasesPerTurn_prefs_key = 'A10/B-DNA bases per turn' # Twist computed from this.
bdnaRise_prefs_key = 'A10/B-DNA rise step'
zdnaBasesPerTurn_prefs_key = 'A10/Z-DNA bases per turn' # Twist computed from this.
zdnaRise_prefs_key = 'A10/Z-DNA rise step'
dnaDefaultSegmentColor_prefs_key = 'A10/DNA default segment color'
dnaColorBasesBy_prefs_key = 'A10/DNA color bases by'
dnaStrutScaleFactor_prefs_key = 'A10/DNA strut scale factor'
arrowsOnBackBones_prefs_key = 'A9/ Show arrows on all directional bonds' 
arrowsOnThreePrimeEnds_prefs_key = 'A9/ Show three prime ends as out arrow heads'
arrowsOnFivePrimeEnds_prefs_key = 'A9/ Show five prime ends as in arrow heads'
dnaStyleStrandsShape_prefs_key = 'A10/DNA style strands shape' # DNA style prefs piotr 080310
dnaStyleStrandsColor_prefs_key = 'A10/DNA style strands color'
dnaStyleStrandsScale_prefs_key = 'A10/DNA style strands scale'
dnaStyleStrandsArrows_prefs_key = 'A10/DNA style strands arrows'
dnaStyleAxisShape_prefs_key = 'A10/DNA style axis shape'
dnaStyleAxisColor_prefs_key = 'A10/DNA style axis color'
dnaStyleAxisScale_prefs_key = 'A10/DNA style axis scale'
dnaStyleAxisTaper_prefs_key = 'A10/DNA style axis taper'
dnaStyleStrutsShape_prefs_key = 'A10/DNA style struts shape'
dnaStyleStrutsColor_prefs_key = 'A10/DNA style struts color'
dnaStyleStrutsScale_prefs_key = 'A10/DNA style struts scale'
dnaStyleBasesShape_prefs_key = 'A10/DNA style bases shape'
dnaStyleBasesColor_prefs_key = 'A10/DNA style bases color'
dnaStyleBasesScale_prefs_key = 'A10/DNA style bases scale'

# Modes prefs [added by mark 050910]
# The background style and color for each mode is initialized in init_prefs()
# of the superclass basicMode (modes.py).
startupMode_prefs_key = 'A7/Startup Mode'
defaultMode_prefs_key = 'A7/Default Mode'
buildModeAutobondEnabled_prefs_key = 'A7/Build Mode Autobond Enabled' # mark 060203.
buildModeWaterEnabled_prefs_key = 'A7/Build Mode Water Enabled' # mark 060203.
buildModeHighlightingEnabled_prefs_key = 'A7/Build Mode Highlighting Enabled' # mark 060203.
buildModeSelectAtomsOfDepositedObjEnabled_prefs_key = 'A7/Build Mode Select Atoms of Deposited Obj Enabled' # mark 060304.

# Selection Behavior
permit_atom_chunk_coselection_prefs_key = 'A9 devel2/permit_atom_chunk_coselection'

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
qutemol_path_prefs_key = 'A9/QuteMol Path'
qutemol_enabled_prefs_key = 'A9/QuteMol Enabled'
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
gromacs_path_prefs_key = 'A10/GROMACS Path'
gromacs_enabled_prefs_key = 'A10/GROMACS Enabled'
cpp_path_prefs_key = 'A10/cpp Path'
cpp_enabled_prefs_key = 'A10/cpp Enabled'
nv1_path_prefs_key = 'A10/NanoVision-1 Path'
nv1_enabled_prefs_key = 'A10/NanoVision-1 Enabled'

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
useSelectedFont_prefs_key = 'A9/Use Selected Font'
displayFont_prefs_key = 'A9/Display Font'
displayFontPointSize_prefs_key = 'A9/Display Font Point Size'
mtColor_prefs_key = 'A9/Model Tree Background Color' # Not yet in Preferences. Mark 2007-06-04
toolbar_state_prefs_key = 'A10/ Toolbar State '
displayReportsWidget_prefs_key = 'A10/Display Reports Widget'
#colorTheme_prefs_key = 'A9/Color Theme'

# Sponsor prefs
sponsor_download_permission_prefs_key   = 'A8/Sponsor download permission'
sponsor_permanent_permission_prefs_key  = 'A8/Sponsor download permission is permanent'

# The following key is not a user preference, it's a state variable that is used
# to keep track of when the sponsor logos files change. This will go away once
# Sponsors.py is re-written to incorporate a thread-safe main program
# event/command queue that can be utilized to throw up a download-permission
# dialog at the same time new logos files are detected.
#
sponsor_md5_mismatch_flag_key           = 'A9/Sponsor md5 file mismatch'

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


# Do not move getDefaultWorkingDirectory() to platform.py since it might
# create a recursive import problem. [Mark 060730.]
# [However, it probably doesn't belong in this file either.
#  Sometime try putting it into a file in a platform-dependent package.
#  bruce 071215 comment]
def getDefaultWorkingDirectory(): 
    """
    Get the default Working Directory.
    
    @return: The default working directory, which is platform dependent:
    - Windows: $HOME\My Documents
    - MacOS and Linux: $HOME
    If the default working directory doesn't exist, return ".".
    @rtype: string
    """
    wd = ""
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

# end
