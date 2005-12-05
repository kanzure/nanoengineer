# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
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

# Selection Behavior Options
A7_SELECTION_BEHAVIOR = 0
A6_SELECTION_BEHAVIOR = 1

# ==

# Keys for user preferences
# (the string constants should start with the first released version they'll appear in)

# General prefs
displayCompass_prefs_key = 'A6/Display Compass'
compassPosition_prefs_key = 'A6/Compass Position'
displayOriginAxis_prefs_key = 'A6/Display Origin Axis'
displayPOVAxis_prefs_key = 'A6/Display POV Axis'
defaultProjection_prefs_key = 'A7/Default Projection'
selectionBehavior_prefs_key = 'A7/Selection Behavior'
animateStandardViews_prefs_key = 'A7/Animate Standard Views'

# Atom prefs
atomHighlightColor_prefs_key = 'A6/Atom Highlight Color'
freeValenceColor_prefs_key = 'A6/Free Valence Color'
atomHotspotColor_prefs_key = 'A6/Atom Hotspot Color'
defaultDisplayMode_prefs_key = 'A6/Default Display Mode'
#CPK atom radius (percentage), mark 051003
cpkAtomRadius_prefs_key = 'A7/CPK Atom Radius Percentage'

# Bond prefs
bondHighlightColor_prefs_key = 'A6/Bond Highlight Color'
bondStretchColor_prefs_key = 'A6/Bond Stretch Color'
bondVaneColor_prefs_key = 'A6/Bond Vane Color'
bondCPKColor_prefs_key = 'A6/Bond CPK Color'
pibondStyle_prefs_key = 'A6/Pi Bond Style'
pibondLetters_prefs_key = 'A6/Pi Bond Letters'
showValenceErrors_prefs_key = 'A6/Show Valence Errors'
#display lines mode line thickness, mark 050831
linesDisplayModeThickness_prefs_key = 'A7/Line Thickness for Lines Display Mode'
#CPK cylinder radius (percentage), mark 051003
cpkCylinderRadius_prefs_key = 'A7/CPK Cylinder Radius Percentage'

# Modes prefs [added by mark 050910]
# The background style and color for each mode is initialized in init_prefs()
# of the superclass basicMode (modes.py).
startupMode_prefs_key = 'A7/Startup Mode'
defaultMode_prefs_key = 'A7/Default Mode'

# Lighting prefs [added by mark 051124]
light1Color_prefs_key = 'A7/Light1 Color'
light2Color_prefs_key = 'A7/Light2 Color'
light3Color_prefs_key = 'A7/Light3 Color'
specular_highlights_prefs_key = 'A7/Specular Highlights'
whiteness_prefs_key = 'A7/Whiteness' # To be changed to 'material_finish'
shininess_prefs_key = 'A7/Shininess' # To be changed to 'material_shininess'
material_brightness_prefs_key = 'A7/Material Brightness'

# File management / filename / URL preferences [tentative category, added by bruce 051130, more comments below]
wiki_help_prefix_prefs_key = 'A7/Wiki Help Prefix'

# Plug-ins prefs [added by mark 050918]
gmspath_prefs_key = 'A6/GAMESS Path'
gamess_enabled_prefs_key = 'A7/GAMESS Enabled'
nanohive_path_prefs_key = 'A7/Nano-Hive Executable Path'
nanohive_enabled_prefs_key = 'A7/Nano-Hive Enabled'

# Caption prefs
captionPrefix_prefs_key = 'A6/Caption Prefix'
captionSuffix_prefs_key = 'A6/Caption Suffix'
captionFullPath_prefs_key = 'A6/Caption Full Path'

# History prefs
historyHeight_prefs_key = 'A6/History Height'
historyMsgSerialNumber_prefs_key = 'A6/History Message Serial Number'
historyMsgTimestamp_prefs_key = 'A6/History Message Timestamp'

# Bug-workaround prefs, Mac-specific

QToolButton_MacOSX_Tiger_workaround_prefs_key = 'A6/QToolButton MacOSX Tiger workaround' #bruce 050810

# Table of internal attribute names, default values, types, and prefs-db formats for some of these preferences.
# (This needs to be defined in a central place, and set up by code in preferences.py
#  before any code can ask for preference values, so the default values can come from here.)

# computed default values; some of these names are also directly used by external code
# which is not yet fully revised to get the values from the prefs db.

_default_HICOLOR_real_atom = ave_colors( 0.8, orange, black)
HICOLOR_singlet = LEDon ## pink [not yet in prefs db]

_default_HICOLOR_real_bond = ave_colors( 0.8, blue, black)

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

# the actual table (for doc, see the code that interprets it, in preferences.py)

prefs_table = (
    # entries are: (attribute name, prefs type-and-db-format code, prefs key, optional default value)
    ##e add categories or tags?
    
    # General preferences [added to this table by mark 050919]

    ('display_compass', 'boolean', displayCompass_prefs_key, True),
    ('display_position', 'int', compassPosition_prefs_key, UPPER_RIGHT),
    ('display_origin_axis', 'boolean', displayOriginAxis_prefs_key, True),
    ('display_pov_axis', 'boolean', displayPOVAxis_prefs_key, True),
    ('default_projection', 'int', defaultProjection_prefs_key, ORTHOGRAPHIC), # Changed to Ortho. Mark 051029.
    ('selection_behavior', 'int', selectionBehavior_prefs_key, A7_SELECTION_BEHAVIOR), # Mark 051122.
    ('animate_std_views', 'boolean', animateStandardViews_prefs_key, True), # Mark 051110.

    # Atom preferences - colors (other than element colors, handled separately)
    
    ('atom_highlight_color',         'color', atomHighlightColor_prefs_key, _default_HICOLOR_real_atom ),
##    ('freevalence_color',            'color', freeValenceColor_prefs_key, red ), ###k red; ### use it --
##        ## freevalence_color is problematic, so not yet implemented -- it's treated internally as an "element color"
    ## ('openbond_highlight_color',  'color', xxx_prefs_key, HICOLOR_singlet ), ## pink [not yet in prefs db]
    ('atom_hotspot_color',           'color', atomHotspotColor_prefs_key, ave_colors( 0.8, green, black) ), #bruce 050808

    # Atom preferences - other
    
    ('cpk_atom_radius', 'float', cpkAtomRadius_prefs_key, 1.0), #mark 051003
    ('display_mode', 'int', defaultDisplayMode_prefs_key, diVDW),

    # Bond preferences - colors
    
    ('bond_highlight_color',         'color', bondHighlightColor_prefs_key, _default_HICOLOR_real_bond),
    ('bond_stretch_color',           'color', bondStretchColor_prefs_key, _default_toolong_color),
    ## ('bond_stretch_highlight_color', 'color', xxx_prefs_key, _default_toolong_hicolor), ## [not yet in prefs db]
    ('pi_vane_color',                'color', bondVaneColor_prefs_key, _default_bondVaneColor),
    ('bond_CPK_color',               'color', bondCPKColor_prefs_key, _default_bondColor),

    # Bond preferences - other

    ('pi_bond_style',   ['multicyl','vane','ribbon'],  pibondStyle_prefs_key,   'multicyl' ),
    ('pi_bond_letters', 'boolean',                     pibondLetters_prefs_key, False ),
    ('show_valence_errors',        'boolean', showValenceErrors_prefs_key,   True ), #bruce 050806 made this up
    ('', 'int', linesDisplayModeThickness_prefs_key, 1), #mark 050831 made this up
    ('cpk_cylinder_radius', 'float', cpkCylinderRadius_prefs_key, 1.0), #mark 051003
    
    # Modes preferences [added to this table by mark 050910]
    
    ('startup_mode', 'string', startupMode_prefs_key,   '$DEFAULT_MODE' ),
    ('default_mode', 'string', defaultMode_prefs_key,   'DEPOSIT' ), # as suggested by Eric.  Mark 051028.
    
    # Lighting preferences [added to this table by mark 051124]
    # If any default light colors are changed here, you must also change the color of 
    # the light in '_lights' in GLPane to keep them synchronized.  Mark 051204.
    ('light1_color', 'color', light1Color_prefs_key, white ),
    ('light2_color', 'color', light2Color_prefs_key, white ),
    ('light3_color', 'color', light3Color_prefs_key, white ), 
    ('specular_highlights', 'boolean', specular_highlights_prefs_key, True),
    ('whiteness', 'float', whiteness_prefs_key, 0.5), # Change this to 'material_finish' later. Mark.
    ('shininess', 'float', shininess_prefs_key, 35.0), # Change this to 'material_shininess' later.  Mark.
    ('material_brightness', 'float', material_brightness_prefs_key, 1.0), #bruce 051203 bugfix: default value should be 1.0

    # File management / filename / URL preferences [added by bruce 051130; category is a guess, doesn't have prefs UI page yet]

    ('', 'string', wiki_help_prefix_prefs_key, "http://www.nanoengineer-1.net/mediawiki/index.php?title=" ),

    # Plug-ins preferences [added to this table by mark 050919]
    
    ('gamess_exe_path', 'string', gmspath_prefs_key, "" ),
    ('gamess_enabled', 'boolean', gamess_enabled_prefs_key, False ),
    ('nanohive_exe_path', 'string', nanohive_path_prefs_key, "" ),
    ('nanohive_enabled', 'boolean', nanohive_enabled_prefs_key, False ),

    # Caption preferences [added to this table by bruce 050810]

    ('', 'string', captionPrefix_prefs_key, "" ),
    ('', 'string', captionSuffix_prefs_key, "*" ),
    ('', 'boolean', captionFullPath_prefs_key, False ),

    # History preferences [added to this table by bruce 050810]

    ('', 'boolean', historyMsgSerialNumber_prefs_key, True),
    ('', 'boolean', historyMsgTimestamp_prefs_key, True),
    
    # ...

    ('', 'boolean', QToolButton_MacOSX_Tiger_workaround_prefs_key, False ), #bruce 050810

)

# end