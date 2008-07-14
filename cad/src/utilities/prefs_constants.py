# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
prefs_constants.py

Constants and utilities related to user preferences,
which need to be defined immediately upon startup.

@author: Mark, Bruce, Ninad
@version: $Id$
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

### do no imports that would not be ok for constants.py to do! ###

from utilities.constants import yellow, pink, red, black, magenta, mustard
from utilities.constants import blue, gray, white, green, orange
from utilities.constants import lightgray, lightblue, lightgreen
from utilities.constants import darkred, darkblue, darkgreen
from utilities.constants import ave_colors, diBALL, bgEVENING_SKY

import sys, os # for getDefaultWorkingDirectory

# ==

# constants related to user chosen hover highlight and selection color

# HH = Hover Highlighting (color) Style
HHS_HALO = 'HALO'# default
HHS_SOLID = 'SOLID'
HHS_SCREENDOOR1 = 'SCREENDOOR1'
HHS_CROSSHATCH1 = 'CROSSHATCH1'
HHS_BW_PATTERN = 'BW_PATTERN'
HHS_POLYGON_EDGES = 'POLYGON_EDGES'
HHS_DISABLED = 'DISABLED'

HHS_INDEXES = [HHS_HALO, HHS_SOLID, HHS_SCREENDOOR1, HHS_CROSSHATCH1, 
               ## russ 080604 NIMs: HHS_BW_PATTERN, HHS_POLYGON_EDGES, HHS_DISABLED]
               HHS_POLYGON_EDGES]

HHS_OPTIONS = ["Colored halo (default)",
               "Solid color",
               "Screendoor pattern",
               "Crosshatch pattern",
               ## russ 080604 NIM: "Black-and-white pattern",
               "Colored polygon edges",
               ## russ 080604 NIM: "Disable highlighting"
               ]

# SS = Selection (color) Style
SS_HALO = 'HALO'# default
SS_SOLID = 'SOLID'
SS_SCREENDOOR1 = 'SCREENDOOR1'
SS_CROSSHATCH1 = 'CROSSHATCH1'
SS_BW_PATTERN = 'BW_PATTERN'
SS_POLYGON_EDGES = 'POLYGON_EDGES'

SS_INDEXES = [SS_HALO, SS_SOLID, SS_SCREENDOOR1, SS_CROSSHATCH1, 
              ## russ 080604 NIM: SS_BW_PATTERN,
              SS_POLYGON_EDGES]

SS_OPTIONS = ["Colored halo (default)",
              "Solid color",
              "Screendoor pattern",
              "Crosshatch pattern",
              ## russ 080604 NIM: "Black-and-white pattern",
              "Colored polygon edges"]

# Compass position constants.  These are used to preserve the preference value
# for the compass position and relate directly to the radio button group values for the options 
# presented in the Preferences/General dialog.  Do not change the value of these 4 constants!
# Mark 050919.
# (Note: they are also used for other, analogous purposes. [bruce 071215 comment])
# UPPER_RIGHT will conflict with the Confirmation Corner when it is implemented in A10.
UPPER_RIGHT = 0 # May need to remove this option in A10. Mark 2007-05-07.
UPPER_LEFT = 1
LOWER_LEFT = 2 # New default. Mark 2007-05-07
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

# these match the indexes in minimize_engine_combobox in
# MinimizeEnergyPropDialog and UserPrefsDialog
MINIMIZE_ENGINE_UNSPECIFIED = -1
MINIMIZE_ENGINE_ND1_FOREGROUND = 0
MINIMIZE_ENGINE_GROMACS_FOREGROUND = 1
MINIMIZE_ENGINE_GROMACS_BACKGROUND = 2

# ==

# Keys for user preferences
# (the string constants should start with the first released version they'll appear in)

# General prefs
displayCompass_prefs_key = 'A6/Display Compass'
displayCompassLabels_prefs_key = 'A7/Display Compass Label'
compassPosition_prefs_key = 'A6/Compass Position'
displayOriginAxis_prefs_key = 'A6/Display Origin Axis'
originAxisColor_prefs_key = 'V111/Origin Axis Color'
displayPOVAxis_prefs_key = 'A6/Display POV Axis'
povAxisColor_prefs_key = 'V111/Point of View Axis Color'
displayConfirmationCorner_prefs_key = 'V111/Display POV Axis'
defaultProjection_prefs_key = 'A7/Default Projection'
animateHighQualityGraphics_prefs_key = 'A7/Animate with High Quality Graphics' #mark 060315. NIY.
animateStandardViews_prefs_key = 'A7/Animate Standard Views'
animateMaximumTime_prefs_key = 'A7/Maximum Animation Time'
workingDirectory_prefs_key = 'WorkingDirectory' # Moved here from startup_funcs.py. Mark 060726.

mouseSpeedDuringRotation_prefs_key = 'A9/Mouse Speed During Rotation' #Ninad 060906
displayOriginAsSmallAxis_prefs_key = 'A9/Display Origin As Small Axis' #Ninad 060920
displayRulers_prefs_key = 'A10/Display rulers'
displayVertRuler_prefs_key = 'A10/Display vertical ruler'
displayHorzRuler_prefs_key = 'A10/Display horizontal ruler'
rulerPosition_prefs_key = 'A10/Ruler Position'
rulerColor_prefs_key = 'A10/Ruler Color'
rulerOpacity_prefs_key = 'A10/Ruler Opacity'
showRulersInPerspectiveView_prefs_key = 'A10/Show Rulers In Perspective View'
fogEnabled_prefs_key = "V110/Enable fog"


#General preferences for copy-paste operation (see ops_copy_mixin._pasteGroup
#for detail) Feature introduced in v1.1.0, on 2008-06-06
pasteOffsetScaleFactorForChunks_prefs_key = 'V110/Scale factor is used to offset chunks to be pasted w.r.t. original chunks'
pasteOffsetScaleFactorForDnaObjects_prefs_key = 'V110/Scale factor is used to offset dna objects to be pasted w.r.t. original dna objects'


# Color prefs (for "Color" page).
backgroundColor_prefs_key = 'A9/Background Color'
backgroundGradient_prefs_key = 'V111/Background Gradient'
hoverHighlightingColorStyle_prefs_key = 'V110/3D hover highlighting color style rev1'
hoverHighlightingColor_prefs_key = 'V110/3D hover highlighting color'
selectionColorStyle_prefs_key = 'V110/3D selection color style rev1'
selectionColor_prefs_key = 'V110/3D selection color'
haloWidth_prefs_key = 'V110/halo width in pixels'

# Special colors pref key(s).
# DarkBackgroundContrastColor_prefs_key provides a dark color (black or
# some dark shade of gray) that is guaranteed to contrast well with the current
# background color.
DarkBackgroundContrastColor_prefs_key = 'V111/Dark Background Contrast Color'
# LightBackgroundContrastColor_prefs_key provides a light color (white or
# some light shade of gray) that is guaranteed to contrast well with the current
# background color.
LightBackgroundContrastColor_prefs_key = 'V111/Light Background Contrast Color'

# Mouse wheel Prefs
mouseWheelDirection_prefs_key = 'A10/Mouse Wheel Direction'
zoomInAboutScreenCenter_prefs_key  = 'A10/Mouse Wheel Zoom In To Screen Center'
zoomOutAboutScreenCenter_prefs_key = 'A10/Mouse Wheel Zoom Out To Screen Center'
mouseWheelTimeoutInterval_prefs_key = 'V110/Mouse Wheel Event Timeout Interval'


#GLpane scale preferences
#GLPane scale preferences . As of 2008-04-07, the GLPane_scale_* preferece 
#can not be set by the user. Its just used internally. 
#@see: GLPane_Minimial.__init__() and GLPane._adjust_GLPane_scale_if_needed()
#for more implementation details

#The GLPane scale setup initially (at startup) i.e. while starting a new 
#(empty) model
startup_GLPane_scale_prefs_key = 'A10/GLPane Scale at startup'

#Preferred GLPane scale is user starts with an empty model and directly enters
#commands such as Build Atoms. 
GLPane_scale_for_atom_commands_prefs_key = 'A10/ Initial GLPane scale for Atom commands'

#Preferred GLPane scale if user starts with an empty model and without changing 
#the initial scale, directly enters a Dna command (such as BuildDna) 
GLPane_scale_for_dna_commands_prefs_key = 'A10/Initial GLPane Scale for Dna commands'


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

neighborSearchingInGromacs_prefs_key = 'A110/Neighbor Searching in GROMACS' # Eric M 20080515

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
startupGlobalDisplayStyle_prefs_key = 'A6/Default Display Mode'
diBALL_AtomRadius_prefs_key = 'A7/CPK Atom Radius Percentage' # this is about diBALL which as of 060307 is called Ball and Stick in UI
    #bruce 060607 renamed cpkAtomRadius_prefs_key -> diBALL_AtomRadius_prefs_key ###DOIT
cpkScaleFactor_prefs_key = 'A7/CPK Scale Factor' # this is about diTrueCPK which as of 060307 is called CPK in UI
levelOfDetail_prefs_key = 'A7/Level Of Detail'
keepBondsDuringTransmute_prefs_key = 'A9/Keep Bonds During Transmute'
reshapeAtomsSelection_prefs_key = 'A10/Reshape Atoms Selection in Build Atoms'
indicateOverlappingAtoms_prefs_key = "A10/GLPane: indicate overlapping atoms? "

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

#== DNA PREFERENCES ============================================================
adnaBasesPerTurn_prefs_key = 'A10/A-DNA bases per turn' # Twist computed from this.
adnaRise_prefs_key = 'A10/A-DNA rise step'
bdnaBasesPerTurn_prefs_key = 'A10/B-DNA bases per turn' # Twist computed from this.
bdnaRise_prefs_key = 'A10/B-DNA rise step'
zdnaBasesPerTurn_prefs_key = 'A10/Z-DNA bases per turn' # Twist computed from this.
zdnaRise_prefs_key = 'A10/Z-DNA rise step'
dnaDefaultStrand1Color_prefs_key = 'V110/DNA default strand1 color'
dnaDefaultStrand2Color_prefs_key = 'V110/DNA default strand2 color'
dnaDefaultSegmentColor_prefs_key = 'A10/DNA default segment color'
dnaStrutScaleFactor_prefs_key = 'A10/DNA strut scale factor'
arrowsOnBackBones_prefs_key = 'A9/ Show arrows on all directional bonds' 
arrowsOnThreePrimeEnds_prefs_key = 'A9/ Show three prime ends as out arrow heads'
arrowsOnFivePrimeEnds_prefs_key = 'A9/ Show five prime ends as in arrow heads'
useCustomColorForThreePrimeArrowheads_prefs_key = 'A111/ Use custom color for three-prime arrowheads/spheres'
dnaStrandThreePrimeArrowheadsCustomColor_prefs_key = 'A111/ Custom color for strand three-prime arrowheads/spheres'
useCustomColorForFivePrimeArrowheads_prefs_key = 'A111/ Use custom color for five-prime arrowheads/spheres'
dnaStrandFivePrimeArrowheadsCustomColor_prefs_key = 'A111/ Custom color for five-prime strand arrowheads/spheres'
#Join strands command prefs 

joinStrandsCommand_arrowsOnThreePrimeEnds_prefs_key = 'A110/ While in Join strands command, show three prime ends as out arrow heads'
joinStrandsCommand_arrowsOnFivePrimeEnds_prefs_key = 'A110/ While in Join strands command, show five prime ends as in arrow heads'
joinStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key = 'A110/ While in Join strands command, use custom color for three-prime arrowheads/spheres'
joinStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key = 'A110/ While in Join strands command, Custom color for strand three-prime arrowheads/spheres'
joinStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key = 'A110/ While in Join strands command,use custom color for five-prime arrowheads/spheres'
joinStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key = 'A110/ While in Join strands command, Custom color for strand five-prime arrowheads/spheres'

#Urmi 20080617: display grid in Plane Property Manager pref keys
PlanePM_showGrid_prefs_key = 'V111/Show Grid on the Plane'
PlanePM_showGridLabels_prefs_key = 'V111/Show Grid Labels on the Plane'

#Break strands command prefs
breakStrandsCommand_arrowsOnThreePrimeEnds_prefs_key = 'A110/ While in Break strands command, show three prime ends as out arrow heads'
breakStrandsCommand_arrowsOnFivePrimeEnds_prefs_key = 'A110/ While in Break strands command, show five prime ends as in arrow heads'
breakStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key = 'A110/ While in Break strands command, use custom color for three-prime arrowheads/spheres'
breakStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key = 'A110/ While in Break strands command, Custom color for strand three-prime arrowheads/spheres'
breakStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key = 'A110/ While in Break strands command,use custom color for five-prime arrowheads/spheres'
breakStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key = 'A110/ While in Break strands command, Custom color for strand five-prime arrowheads/spheres'
breakStrandsCommand_numberOfBasesBeforeNextBreak_prefs_key  = 'A111/Number of bases before the next break site'

#Various cursor text prefs =======================
dnaDuplexEditCommand_showCursorTextCheckBox_prefs_key = 'A110/Show cursor text while drawing the duplex'
dnaDuplexEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key = 'A110/Show number of basepair info in cursor text while in DnaDulex_Editcommand'
dnaDuplexEditCommand_cursorTextCheckBox_numberOfTurns_prefs_key = 'A110/Show number of turns info in cursor text while in DnaDulex_Editcommand'
dnaDuplexEditCommand_cursorTextCheckBox_length_prefs_key = 'A110/Show duplex length info in cursor text while in DnaDulex_Editcommand'
dnaDuplexEditCommand_cursorTextCheckBox_angle_prefs_key = 'A110/Show angle info in cursor text while in DnaDulex_Editcommand'

dnaSegmentEditCommand_showCursorTextCheckBox_prefs_key = 'A110/Show cursor text while drawing the duplex in DnaSegment EditCommand'
dnaSegmentEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key = 'A110/Show number of basepair info in cursor text while in DnaSegment_Editcommand'
dnaSegmentEditCommand_cursorTextCheckBox_length_prefs_key = 'A110/Show duplex length info in cursor text while in DnaSegment_Editcommand'
dnaSegmentEditCommand_cursorTextCheckBox_changedBasePairs_prefs_key = 'A110/Show changed number of basepairs info in cursor text while in DnaSegment_Editcommand'

#DnaSegment_ResizeHandle preferences
dnaSegmentResizeHandle_discRadius_prefs_key = 'V111/Radius of the disc component of the DnaSegment resize handle'
dnaSegmentResizeHandle_discThickness_prefs_key = 'V111/Thickness of the disc component of the DnaSegment resize handle'

dnaStrandEditCommand_showCursorTextCheckBox_prefs_key = 'A110/Show cursor text while drawing the duplex in DnaStrand_EditCommand'
dnaStrandEditCommand_cursorTextCheckBox_numberOfBases_prefs_key = 'A110/Show number of bases info in cursor text while in DnaStrand_Editcommand'
dnaStrandEditCommand_cursorTextCheckBox_changedBases_prefs_key = 'A110/Show changed number of basepairs info in cursor text while in DnaStrand_Editcommand'


makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key = 'A110/search for crossover sites between the given dna segments only'
# DNA Minor Groove Error Indicator prefs
dnaDisplayMinorGrooveErrorIndicators_prefs_key = 'A10/Display DNA minor groove error indicators'
dnaMinMinorGrooveAngle_prefs_key = 'A10/DNA minimum minor groove angle'
dnaMaxMinorGrooveAngle_prefs_key = 'A10/DNA maximum minor groove angle'
dnaMinorGrooveErrorIndicatorColor_prefs_key = 'A10/DNA minor groove error indicator color'

# DNA renditions prefs. Mark 2008-05-15
dnaRendition_prefs_key = 'A110/DNA rendition' 

# DNA style prefs piotr 080310
dnaStyleStrandsShape_prefs_key = 'A10/DNA style strands shape' 
dnaStyleStrandsColor_prefs_key = 'A10/DNA style strands color'
dnaStyleStrandsScale_prefs_key = 'A10/DNA style strands scale'
dnaStyleStrandsArrows_prefs_key = 'A10/DNA style strands arrows'
dnaStyleAxisShape_prefs_key = 'A10/DNA style axis shape'
dnaStyleAxisColor_prefs_key = 'A10/DNA style axis color'
dnaStyleAxisScale_prefs_key = 'A10/DNA style axis scale'
dnaStyleAxisEndingStyle_prefs_key = 'A10/DNA style axis ending style'
dnaStyleStrutsShape_prefs_key = 'A10/DNA style struts shape'
dnaStyleStrutsColor_prefs_key = 'A10/DNA style struts color'
dnaStyleStrutsScale_prefs_key = 'A10/DNA style struts scale'
dnaStyleBasesShape_prefs_key = 'A10/DNA style bases shape'
dnaStyleBasesColor_prefs_key = 'A10/DNA style bases color'
dnaStyleBasesScale_prefs_key = 'A10/DNA style bases scale'
assignColorToBrokenDnaStrands_prefs_key = 'A10/Assign color to broken DNA strands'

# DNA labels and base orientation preferences. 080325 piotr
dnaStrandLabelsEnabled_prefs_key = 'A10/DNA strand labels enabled'
dnaStrandLabelsColor_prefs_key = 'A10/DNA strand labels color'
dnaStrandLabelsColorMode_prefs_key = 'A10/DNA strand labels color mode'
dnaBaseIndicatorsEnabled_prefs_key = 'A10/DNA base orientation indicators enabled'
dnaBaseInvIndicatorsEnabled_prefs_key = 'A10/DNA base inverse orientation indicators enabled'
dnaBaseIndicatorsAngle_prefs_key = 'A10/DNA base orientation indicators angle'
dnaBaseIndicatorsColor_prefs_key = 'A10/DNA base orientation indicators color'
dnaBaseInvIndicatorsColor_prefs_key = 'A10/DNA base inverse orientation indicators color'
dnaBaseIndicatorsDistance_prefs_key = 'A10/DNA base orientation indicators distance'
dnaStyleBasesDisplayLetters_prefs_key = 'A10/DNA base letters enabled'
dnaBaseIndicatorsPlaneNormal_prefs_key = 'V110/DNA base orientation indicators plane option'



#Nanotube cursor texts ============
insertNanotubeEditCommand_showCursorTextCheckBox_prefs_key = 'A110/Show cursor text while drawing the nanotube in InsertNanotube_EditCommand'
insertNanotubeEditCommand_cursorTextCheckBox_length_prefs_key = 'A110/Show nanotube length info in cursor text while in InsertNanotube_Editcommand'
insertNanotubeEditCommand_cursorTextCheckBox_angle_prefs_key = 'A110/Show angle info in cursor text while in InsertNanotube_Editcommand'

nanotubeSegmentEditCommand_showCursorTextCheckBox_prefs_key = 'A110/Show cursor text while resizing the nanotube in NanotubeSegment_EditCommand'
nanotubeSegmentEditCommand_cursorTextCheckBox_length_prefs_key = 'A110/Show nanotube length info in cursor text while in NanotubeSegment_EditCommand'


# stereo view preferences [added by piotr 080516]
stereoViewMode_prefs_key = 'Stereo view mode'
stereoViewSeparation_prefs_key = 'Stereo view separation'
stereoViewAngle_prefs_key = 'Stereo view angle'

# Modes prefs [added by mark 050910]
# The background style and color for each mode is initialized in init_prefs()
# of the superclass basicMode (modes.py).
## startupMode_prefs_key = 'A7/Startup Mode' #bruce 080709 commented out, not used since A9
## defaultMode_prefs_key = 'A7/Default Mode'
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
rosetta_path_prefs_key = 'V111/Rosetta Path'
rosetta_enabled_prefs_key = 'V111/Rosetta Enabled'
rosetta_database_prefs_key = 'V111/Rosetta Database'
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
toolbar_state_prefs_key = 'V111/ Toolbar State ' #this was introduce in A10 but the value (string) changed in V111 to fix a bug in Qt4.3.5
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

# Protein display style preferences
# piotr 080625

proteinStyle_prefs_key = 'V111/Protein display style'
proteinStyleSmooth_prefs_key = 'V111/Protein display style smoothness'
proteinStyleQuality_prefs_key = 'V111/Protein display style quality'
proteinStyleScaling_prefs_key = 'V111/Protein scaling'
proteinStyleScaleFactor_prefs_key = 'V111/Protein scale factor'
proteinStyleColors_prefs_key = 'V111/Protein colors'
proteinStyleAuxColors_prefs_key = 'V111/Protein aux colors'
proteinStyleCustomColor_prefs_key ='V111/Protein custom color'
proteinStyleAuxCustomColor_prefs_key ='V111/Protein aux custom color'
proteinStyleColorsDiscrete_prefs_key = 'V111/Protein discrete colors'
proteinStyleHelixColor_prefs_key ='V111/Protein helix color'
proteinStyleStrandColor_prefs_key ='V111/Protein strand color'
proteinStyleCoilColor_prefs_key ='V111/Protein coil color'

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
_default_HICOLOR_delete_atom = red
_default_HICOLOR_delete_bond = red
_default_HICOLOR_bondpoint = pink


_default_toolong_color = ave_colors( 0.8, red, black) #bruce 050727 changed this from pure red; 050805 even for lines mode
_default_toolong_hicolor = ave_colors( 0.8, magenta, black) ## not yet in prefs db

_default_strandLabelsColor = black # piotr 080325 added these default colors
_default_baseIndicatorsColor = white
_default_baseInvIndicatorsColor = black

def _compute_default_bondVaneColor():
    ord_pi_for_color = 0.5
        # was ord_pi, when we let the color vary with ord_pi;
        # if we later want that, then define two colors here and use them as endpoints of a range
    color = ave_colors(ord_pi_for_color, blue, gray)
    return ave_colors(0.8, color, black)

_default_bondVaneColor = _compute_default_bondVaneColor()

_default_bondColor = (0.25, 0.25, 0.25)

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

prefs_table = (
    # entries are: (attribute name, prefs type-and-db-format code, prefs key, optional default value)
    ##e add categories or tags?

    # General preferences [added to this table by mark 050919] 

    ('display_compass', 'boolean', displayCompass_prefs_key, True),
    ('display_compass_labels', 'boolean', displayCompassLabels_prefs_key, True),
    ('display_position', 'int', compassPosition_prefs_key, LOWER_LEFT), # Mark 2007-0507.
    ('display_origin_axis', 'boolean', displayOriginAxis_prefs_key, True),
    ('', 'color', originAxisColor_prefs_key, lightblue),
    ('display_pov_axis', 'boolean', displayPOVAxis_prefs_key, False),
    ('', 'color', povAxisColor_prefs_key, darkgreen),
    ('', 'boolean', displayConfirmationCorner_prefs_key, True),
    ('default_projection', 'int', defaultProjection_prefs_key, ORTHOGRAPHIC), # Changed to Ortho. Mark 051029.
    ('animate_high_quality', 'boolean', animateHighQualityGraphics_prefs_key, True), # Mark 060315. NIY.
    ('animate_std_views', 'boolean', animateStandardViews_prefs_key, True), # Mark 051110.
    ('animate_max_time', 'float', animateMaximumTime_prefs_key, 1.0), # 1 second.  Mark 060124.
    ('working_directory', 'string', workingDirectory_prefs_key,  _default_workingDirectory ), # Mark 060726.
    ('startup_display_style', 'int', startupGlobalDisplayStyle_prefs_key, diBALL), # Mark 060815 diTUBES; revised Ninad 080423 diBALL
    ('mouse_speed_during_rotation', 'float', mouseSpeedDuringRotation_prefs_key, 0.6), # Ninad 060906. 
    ('display origin as small axis', 'boolean', displayOriginAsSmallAxis_prefs_key, True), #Ninad 060920

    #Paste offset scale factor preferences (see Ops_copy_Mixin._pasteGroup)
    ('paste offset scale for chunks', 'float', 
     pasteOffsetScaleFactorForChunks_prefs_key, 0.1),

    ('paste offset scale for dna objects' , 'float', 
     pasteOffsetScaleFactorForDnaObjects_prefs_key, 3.0),

    # Color (page) preferences
    ('', 'int',   backgroundGradient_prefs_key, bgEVENING_SKY),
    ('', 'color', backgroundColor_prefs_key, white),
    ('', 'string',   hoverHighlightingColorStyle_prefs_key, HHS_HALO),
    ('', 'color', hoverHighlightingColor_prefs_key, yellow),
    ('', 'string',   selectionColorStyle_prefs_key, SS_HALO),
    ('', 'color', selectionColor_prefs_key, darkgreen),
    ('', 'int',   haloWidth_prefs_key, 5),
    
    # Special colors. Mark 2008-07-10
    ('', 'color', DarkBackgroundContrastColor_prefs_key, black),
    ('', 'color', LightBackgroundContrastColor_prefs_key, white),

    # stereo view settings added by piotr 080516
    ('stereo_view_mode', 'int', stereoViewMode_prefs_key, 1), 
    ('stereo_view_separation', 'int', stereoViewSeparation_prefs_key, 50), 
    ('stereo_view_angle', 'int', stereoViewAngle_prefs_key, 50), 

    # Fog setting. Mark 2008-05-21
    ('', 'boolean', fogEnabled_prefs_key, False),

    #GLPane scale preferences . As of 2008-04-07, the GLPane_scale_* preferece 
    #can not be set by the user. Its just used internally. 
    #@see: GLPane_Minimial.__init__() and GLPane._adjust_GLPane_scale_if_needed()
    #for more implementation details
    ('', 'float', startup_GLPane_scale_prefs_key, 10.0),
    ('', 'float', GLPane_scale_for_atom_commands_prefs_key, 10.0),
    ('', 'float', GLPane_scale_for_dna_commands_prefs_key, 50.0),

    # Mouse wheel prefs. Mark 2008-04-07
    ('', 'int', mouseWheelDirection_prefs_key,      0),
    ('', 'int', zoomInAboutScreenCenter_prefs_key,  0),
    ('', 'int', zoomOutAboutScreenCenter_prefs_key, 1),
    ('', 'float', mouseWheelTimeoutInterval_prefs_key, 0.5),

    # Ruler prefs. Mark 2008-02-12
    # Ruler constants defined in Constants_Rulers.py. 
    ('', 'boolean', displayRulers_prefs_key, True),
    ('', 'boolean', displayVertRuler_prefs_key, True),
    ('', 'boolean', displayHorzRuler_prefs_key, True),
    ('', 'string', rulerPosition_prefs_key, 0), # 0 = lower left
    ('', 'color', rulerColor_prefs_key, mustard),
    ('', 'float', rulerOpacity_prefs_key, 0.7),
    ('', 'boolean', showRulersInPerspectiveView_prefs_key, False),

    #Ninad 20070509 Adjust,Minimize and Simulation(Dynamics)preferences for DNA 
    #reduced model(enable or disable elecrostatics)
    ('Electrostatics for Dna During Adjust','boolean',
     electrostaticsForDnaDuringAdjust_prefs_key, False),
    ('Electrostatics For Dna During Minimize', 'boolean',
     electrostaticsForDnaDuringMinimize_prefs_key, True),
    ('Electrostatics For Dna During Simulation', 'boolean',
     electrostaticsForDnaDuringDynamics_prefs_key, True),

    ('', 'boolean', neighborSearchingInGromacs_prefs_key, True), # Eric M 20080515

    # Minimize prefs (some are in General prefs pane, some are in dialogs)
    # [mark 060627, revised & extended by bruce 060628, 060705 for A8]
    # (none yet are specific to Adjust Atoms aka Local Minimize)

    ('', 'boolean', Adjust_watchRealtimeMinimization_prefs_key, True),
    ('', 'float', Adjust_endRMS_prefs_key, 100.0), # WARNING: this value may also be hardcoded in runSim.py
    ('', 'float', Adjust_endMax_prefs_key, -1.0), # -1.0 means blank lineedit widget, and actual value is computed from other prefs
    ('', 'float', Adjust_cutoverRMS_prefs_key, -1.0),
    ('', 'float', Adjust_cutoverMax_prefs_key, -1.0),

    ('', 'int', Adjust_minimizationEngine_prefs_key, MINIMIZE_ENGINE_ND1_FOREGROUND),

    ('', 'boolean', Minimize_watchRealtimeMinimization_prefs_key, True), 
    ('', 'float', Minimize_endRMS_prefs_key, +1.0), # WARNING: this value may also be hardcoded in runSim.py
    ('', 'float', Minimize_endMax_prefs_key, -1.0), 
    ('', 'float', Minimize_cutoverRMS_prefs_key, -1.0), 
    ('', 'float', Minimize_cutoverMax_prefs_key, -1.0), 

    ('', 'int', Minimize_minimizationEngine_prefs_key, MINIMIZE_ENGINE_ND1_FOREGROUND),

    # preference for adding potential energy to trace file

    ('', 'boolean', Potential_energy_tracefile_prefs_key, False),

    # Atom preferences - colors (other than element colors, handled separately)

    ('atom_highlight_color', 'color', atomHighlightColor_prefs_key, _default_HICOLOR_real_atom ),
    ('delete_atom_highlight_color', 'color', deleteAtomHighlightColor_prefs_key, _default_HICOLOR_delete_atom ),
    ('bondpoint_highlight_color', 'color', bondpointHighlightColor_prefs_key, _default_HICOLOR_bondpoint),
    ('bondpoint_hotspot_color', 'color', bondpointHotspotColor_prefs_key, ave_colors( 0.8, green, black) ), #bruce 050808

    ## ('openbond_highlight_color',  'color', xxx_prefs_key, HICOLOR_singlet ), ## pink [not yet in prefs db]

    # Atom preferences - other

    ('', 'float', diBALL_AtomRadius_prefs_key, 1.0), #mark 051003 [about Ball and Stick]
    ('cpk_scale_factor', 'float', cpkScaleFactor_prefs_key, 0.775), #mark 060307 [about diTrueCPK, called CPK in UI as of now]
    ('level_of_detail', 'int', levelOfDetail_prefs_key, -1), # -1 = Variable . mark & bruce 060215.
    # Preference to force to keep bonds while transmuting atoms 
    ('keep_bonds_during_transmute', 'boolean', keepBondsDuringTransmute_prefs_key, False),
    ('', 'boolean', reshapeAtomsSelection_prefs_key, False), # --Mark 2008-04-06
    ('', 'boolean', indicateOverlappingAtoms_prefs_key, False),

    # Bond preferences - colors

    ('bond_highlight_color', 'color', bondHighlightColor_prefs_key, _default_HICOLOR_real_bond),
    ('delete_bond_highlight_color', 'color', deleteBondHighlightColor_prefs_key, _default_HICOLOR_delete_bond),
    ('bond_stretch_color', 'color', bondStretchColor_prefs_key, _default_toolong_color),
    ## ('bond_stretch_highlight_color', 'color', xxx_prefs_key, _default_toolong_hicolor), ## [not yet in prefs db]
    ('pi_vane_color',  'color', bondVaneColor_prefs_key, _default_bondVaneColor),
    ('',               'color', diBALL_bondcolor_prefs_key, _default_bondColor),

    # Bond preferences - other

    #ninad 070430 Enable or disable display of bond stretch indicators --
    ('show_bond_stretch_indicators', 'boolean', 
     showBondStretchIndicators_prefs_key, True),   

    ('pi_bond_style',   ['multicyl','vane','ribbon'],  pibondStyle_prefs_key,   'multicyl' ),
    ('pi_bond_letters', 'boolean',                     pibondLetters_prefs_key, False ),
    ('show_valence_errors', 'boolean', showValenceErrors_prefs_key,   True ), #bruce 050806 made this up
    ('', 'int', linesDisplayModeThickness_prefs_key, 1),
    ('', 'float', diBALL_BondCylinderRadius_prefs_key, 1.0),
    ('', 'float', diDNACYLINDER_BondCylinderRadius_prefs_key, 1.0),

    # DNA preferences
    # All DNA default values need to be confirmed by Eric D and Paul R.
    # Mark 2008-01-31.
    ('', 'float', adnaBasesPerTurn_prefs_key, 10.0),
    ('', 'float', adnaRise_prefs_key, 3.391),
    ('', 'float', bdnaBasesPerTurn_prefs_key, 10.0),
    ('', 'float', bdnaRise_prefs_key, 3.180),
    ('', 'float', zdnaBasesPerTurn_prefs_key, 10.0),
    ('', 'float', zdnaRise_prefs_key, 3.715),
    ('', 'color', dnaDefaultStrand1Color_prefs_key, darkred),
    ('', 'color', dnaDefaultStrand2Color_prefs_key, darkblue),
    ('', 'color', dnaDefaultSegmentColor_prefs_key, gray),
    ('', 'float', dnaStrutScaleFactor_prefs_key, 1.0),

    # Strand arrowheads display option prefs.
    ('', 'boolean', arrowsOnBackBones_prefs_key, True), 
    ('', 'boolean', arrowsOnThreePrimeEnds_prefs_key, True), 
    ('', 'boolean', arrowsOnFivePrimeEnds_prefs_key, False), 
    #custom color for arrowheads -- default changed to False in v1.1.0
    ('', 'boolean', useCustomColorForThreePrimeArrowheads_prefs_key, False),
    ('', 'color', dnaStrandThreePrimeArrowheadsCustomColor_prefs_key, green),
    ('', 'boolean', useCustomColorForFivePrimeArrowheads_prefs_key, False),
    ('', 'color', dnaStrandFivePrimeArrowheadsCustomColor_prefs_key, green),

    #Join strands command arrowhead display pref.(should it override global pref)
    ('', 'boolean', joinStrandsCommand_arrowsOnThreePrimeEnds_prefs_key, True), 
    ('', 'boolean', joinStrandsCommand_arrowsOnFivePrimeEnds_prefs_key, True), 
    ('', 'boolean', joinStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key, True),
    ('', 'color', joinStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key, green),
    ('', 'boolean', joinStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key, True),
    ('', 'color', joinStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key, green),

    #Urmi 20080617: Plane_PM display grid prefs
    ('','boolean',PlanePM_showGrid_prefs_key, False),
    ('','boolean',PlanePM_showGridLabels_prefs_key, False),

    #Break strands command preferences 
      #=== arrowhead display pref.(should it override global pref)

    ('', 'boolean', breakStrandsCommand_arrowsOnThreePrimeEnds_prefs_key, True), 
    ('', 'boolean', breakStrandsCommand_arrowsOnFivePrimeEnds_prefs_key, True), 
    ('', 'boolean', breakStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key, True),
    ('', 'color', breakStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key, green),
    ('', 'boolean', breakStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key, True),
    ('', 'color', breakStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key, red),
    
    ('', 'int', breakStrandsCommand_numberOfBasesBeforeNextBreak_prefs_key, 5),

    #DNA cursor text preferences 

    #Cursor text prefs while in DnaDuplex_EditCommand 
    ('', 'boolean',
     dnaDuplexEditCommand_showCursorTextCheckBox_prefs_key, True),

    ('',  'boolean',
     dnaDuplexEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key, True),
    ('',  'boolean',
     dnaDuplexEditCommand_cursorTextCheckBox_numberOfTurns_prefs_key, True),

    ('', 'boolean',
     dnaDuplexEditCommand_cursorTextCheckBox_length_prefs_key, True), 

    ('', 'boolean',
     dnaDuplexEditCommand_cursorTextCheckBox_angle_prefs_key, True), 

    #DnaSegment_EditCommand

    ('',  'boolean',
     dnaSegmentEditCommand_showCursorTextCheckBox_prefs_key, True),

    ('', 'boolean',
     dnaSegmentEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key, True),

    ('', 'boolean',
     dnaSegmentEditCommand_cursorTextCheckBox_length_prefs_key, True),

    ('', 'boolean',
     dnaSegmentEditCommand_cursorTextCheckBox_changedBasePairs_prefs_key, True),
    
    #DnaSegment_ResizeHandle preferences
    ('', 'float', dnaSegmentResizeHandle_discRadius_prefs_key, 12.5), 
    ('', 'float', dnaSegmentResizeHandle_discThickness_prefs_key, 0.25),


    #DnaStrand_EditCommand
    ('',  'boolean',
     dnaStrandEditCommand_showCursorTextCheckBox_prefs_key, True),

    ('', 'boolean',
     dnaStrandEditCommand_cursorTextCheckBox_numberOfBases_prefs_key, True),

    ('', 'boolean',
     dnaStrandEditCommand_cursorTextCheckBox_changedBases_prefs_key, True),


    #Make crossovers command 
    ('', 'boolean',
     makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key,
     True),    


    #Nanotube cursor text prefs
    ('', 'boolean', 
     insertNanotubeEditCommand_cursorTextCheckBox_angle_prefs_key, True),

    ('', 'boolean',
     insertNanotubeEditCommand_cursorTextCheckBox_length_prefs_key, True),

    ('', 'boolean',
     insertNanotubeEditCommand_showCursorTextCheckBox_prefs_key, True),

    #NanotubeSegment_EditCommand cursor texts
    ('', 'boolean',
     nanotubeSegmentEditCommand_cursorTextCheckBox_length_prefs_key, True),

    ('', 'boolean',
     nanotubeSegmentEditCommand_showCursorTextCheckBox_prefs_key, True),

    # DNA minor groove error indicator prefs.
    ('', 'boolean', dnaDisplayMinorGrooveErrorIndicators_prefs_key, True),
    ('', 'int', dnaMinMinorGrooveAngle_prefs_key,  60), # revised per Eric D [bruce 080326]
    ('', 'int', dnaMaxMinorGrooveAngle_prefs_key, 150), # ditto
    ('', 'color', dnaMinorGrooveErrorIndicatorColor_prefs_key, orange),

    # Only used in "Break Strands" PM.
    ('', 'boolean', assignColorToBrokenDnaStrands_prefs_key, True),

    # DNA style preferences 080310 piotr
    # updated on 080408
    ('', 'int', dnaRendition_prefs_key, 0),
    ('', 'int', dnaStyleStrandsShape_prefs_key, 2),
    ('', 'int', dnaStyleStrandsColor_prefs_key, 0),
    ('', 'float', dnaStyleStrandsScale_prefs_key, 1.0),
    ('', 'int', dnaStyleStrandsArrows_prefs_key, 2),
    ('', 'int', dnaStyleAxisShape_prefs_key, 1),
    ('', 'int', dnaStyleAxisColor_prefs_key, 0),
    ('', 'float', dnaStyleAxisScale_prefs_key, 1.1),
    ('', 'int', dnaStyleAxisEndingStyle_prefs_key, 0),
    ('', 'int', dnaStyleStrutsShape_prefs_key, 1),
    ('', 'int', dnaStyleStrutsColor_prefs_key, 0),
    ('', 'float', dnaStyleStrutsScale_prefs_key, 1.0),
    ('', 'int', dnaStyleBasesShape_prefs_key, 0),
    ('', 'int', dnaStyleBasesColor_prefs_key, 3),
    ('', 'float', dnaStyleBasesScale_prefs_key, 1.7),
    ('', 'boolean', dnaStyleBasesDisplayLetters_prefs_key, False),

    # protein style preferences
    # piotr 080625
    ('', 'int', proteinStyle_prefs_key, 0),
    ('', 'boolean', proteinStyleSmooth_prefs_key, True),
    ('', 'int', proteinStyleQuality_prefs_key, 10),
    ('', 'int', proteinStyleScaling_prefs_key, 0),
    ('', 'float', proteinStyleScaleFactor_prefs_key, 1.0),
    ('', 'int', proteinStyleColors_prefs_key, 0),
    ('', 'int', proteinStyleAuxColors_prefs_key, 0),
    ('', 'color', proteinStyleCustomColor_prefs_key, gray),
    ('', 'color', proteinStyleAuxCustomColor_prefs_key, gray),
    ('', 'boolean', proteinStyleColorsDiscrete_prefs_key, True),
    ('', 'color', proteinStyleHelixColor_prefs_key, red),
    ('', 'color', proteinStyleStrandColor_prefs_key, blue),
    ('', 'color', proteinStyleCoilColor_prefs_key, gray),

    # DNA angle and base indicators 080325 piotr
    ('', 'boolean', dnaStrandLabelsEnabled_prefs_key, False),
    ('', 'color', dnaStrandLabelsColor_prefs_key, _default_strandLabelsColor),
    ('', 'int', dnaStrandLabelsColorMode_prefs_key, 0),
    ('', 'boolean', dnaBaseIndicatorsEnabled_prefs_key, False),
    ('', 'boolean', dnaBaseInvIndicatorsEnabled_prefs_key, False),
    ('', 'color', dnaBaseIndicatorsColor_prefs_key, _default_baseIndicatorsColor),
    ('', 'color', dnaBaseInvIndicatorsColor_prefs_key, _default_baseInvIndicatorsColor),
    ('', 'float', dnaBaseIndicatorsAngle_prefs_key, 30.0),
    ('', 'int', dnaBaseIndicatorsDistance_prefs_key, 0),
    ('', 'int', dnaBaseIndicatorsPlaneNormal_prefs_key, 0),

    # Modes preferences [added to this table by mark 050910]

    #bruce 080709 commented these out, not used since A9:
    ## ('startup_mode', 'string', startupMode_prefs_key,   '$DEFAULT_MODE' ),
    ## ('default_mode', 'string', defaultMode_prefs_key,   'DEPOSIT' ), # as suggested by Eric.  Mark 051028.
    ## #ninad070430:  made select chunks mode the only startup and default option 
    ## #for A9 based on discussion
    ## ('default_mode', 'string', defaultMode_prefs_key,   'SELECTMOLS' ),
    
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

    ('qutemol_exe_path', 'string', qutemol_path_prefs_key, "" ),
    ('qutemol_enabled', 'boolean', qutemol_enabled_prefs_key, False ),
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
    ('gromacs_exe_path', 'string', gromacs_path_prefs_key, "" ),
    ('gromacs_enabled', 'boolean', gromacs_enabled_prefs_key, False ),
    #Urmi 20080709: since this is not in the pref dialog as yet, we'll hard code
    # for testing purposes
    ('rosetta_exe_path', 'string', rosetta_path_prefs_key, "/Users/marksims/Nanorex/Rosetta/rosetta++/rosetta.mactel" ),
    ('rosetta_enabled', 'boolean', rosetta_enabled_prefs_key, True ),
    ('rosetta_database_path', 'string', rosetta_database_prefs_key, '/Users/marksims/Nanorex/Rosetta/rosetta_database'),
    ('cpp_exe_path', 'string', cpp_path_prefs_key, "" ),
    ('cpp_enabled', 'boolean', cpp_enabled_prefs_key, False ),
    ('nv1_exe_path', 'string', nv1_path_prefs_key, "" ),
    ('nv1_enabled', 'boolean', nv1_enabled_prefs_key, False ),

    # Undo and History preferences [added to this table by bruce 050810]
    ('', 'boolean', undoRestoreView_prefs_key, False), # mark 060314
    ('', 'boolean', undoAutomaticCheckpoints_prefs_key, True), # mark 060314
    ('', 'int', undoStackMemoryLimit_prefs_key, 100), # mark 060327
    ('', 'boolean', historyMsgSerialNumber_prefs_key, True),
    ('', 'boolean', historyMsgTimestamp_prefs_key, True),
    ('history_height', 'int', historyHeight_prefs_key, 4), # ninad 060904

    # Window preferences [added to this table by bruce 050810]

    ('', 'boolean', rememberWinPosSize_prefs_key, False), # mark 060315. NIY.
    ('', 'string', captionPrefix_prefs_key, "" ),
    ('', 'string', captionSuffix_prefs_key, "*" ),
    ('', 'boolean', captionFullPath_prefs_key, False ),
    ('', 'boolean', useSelectedFont_prefs_key, False ),
    ('', 'string', displayFont_prefs_key, "defaultFont"),
    ('', 'int', displayFontPointSize_prefs_key, -1), # will be reset by the actual default font size.
    ("", 'color', mtColor_prefs_key, white ), # Model Tree bg color. Mark 2007-06-04
    #('', 'string', colorTheme_prefs_key, "defaultColorTheme"), # Gray for A9. Mark 2007-05-27.
    #Following saves the toolbar and dockwidget positions between NE1 sessions
    ('toolbar_state', 'string' , toolbar_state_prefs_key, 'defaultToolbarState'),
    ('', 'boolean', displayReportsWidget_prefs_key, True),
    # ...    
    ('', 'boolean', sponsor_download_permission_prefs_key, False ),
    ('', 'boolean', sponsor_permanent_permission_prefs_key, False ),
    ('', 'boolean', sponsor_md5_mismatch_flag_key, True ),

    # Dynamic Tooltip preferences [added to this table by ninad 060818]
    ('wake_up_delay', 'float', dynamicToolTipWakeUpDelay_prefs_key, 1.0), # 1 second. Mark 060817.
    ('atom_distance_precision', 'int', dynamicToolTipAtomDistancePrecision_prefs_key, 3), # number of decimal places  ninad 060821
    ('bend_angle_precision', 'int', dynamicToolTipBendAnglePrecision_prefs_key, 3), # number of decimal places 

    ('atom_chunk_info', 'boolean', dynamicToolTipAtomChunkInfo_prefs_key, False), # checkbox for displaying chunk name an atom belongs to
    ('bond_chunk_info', 'boolean', dynamicToolTipBondChunkInfo_prefs_key, False), # checkbox -chunk name(s) of the two atoms in the bond
    ('atom_position', 'boolean', dynamicToolTipAtomPosition_prefs_key, False), #checkbox for displaying xyz pos
    ('atom_distance_deltas', 'boolean', dynamicToolTipAtomDistanceDeltas_prefs_key, False), # check box to display xyz deltas
    ('bond_length', 'boolean', dynamicToolTipBondLength_prefs_key, False), # displays the bond length (precision determined by atom distance precision) @@@ ninad060823: It only returns the nuclear distance between the bonded atoms doesn't return covalent bond length.
    ('atom_mass', 'boolean', dynamicToolTipAtomMass_prefs_key, False), #displays mass of the atom ninad060829

    #This preference adds VDW radii of the two atoms to the distance 
    #in the 'distance between atoms' information given by the dynamic tooltip.
    ('vdw_radii_in_atom_distance', 'boolean',
     dynamicToolTipVdwRadiiInAtomDistance_prefs_key,
     False),

    #=== Start of NIYs ninad060822===#
    ('torsion_angle_precision', 'int', dynamicToolTipTorsionAnglePrecision_prefs_key, 3), # number of decimal places 
    #===End of NIYs ninad060822 ===#

)

# end
