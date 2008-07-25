# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
packageData.py -- data about modules and packages, for PackageDependency.py

@author: Eric M, Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.


# NFRs for packageDependency.py: @@@


# unrecognized modules should be classified as alone in a package,
# so they are very visible in the graph
# and so the arcs you see help you classify them properly.


# classification can be "layer|topic", e.g. "model|GAMESS",
# with options to use either or both parts (before/after the '|') as part of the package name;
# if no "|" then assume it's just the layer;
# the layers are what we have now (ui, model, etc)
# but note that in the current table [bruce 071217 2pm] I've also used ui/whatever in the layer
# in an experimental way re finer layer divisions.
#
# layer = general type of code;
# topic = topic of feature re user point of view (ie "which plugin it would be part of")
#
# interaction with colors: just use the layer in the color table, i think.
# (at least do that if the whole thing, layer|topic, is not listed there;
#  might fall back to topic for color lookup if necessary)
#
# interaction with good/bad arcs (packageLevel): ideally we have a separate table of levels
# for layer and topic, and each one is a partial order or specific DAG.
# But for now, numerical scheme only makes sense for layer, not for topic, so just use layer for this.


# lower priority: warnings based on the "disallowed" tables below
"""

# disallowed names

# NIM: warn or enforce the non-use of the following names (case-insensitively?)
# We don't list every possible disallowed name,
# just the ones that we might be tempted to use otherwise.
#
# Note: on Mac, python import seems to be case-sensitive even though you can't
# have two filesystem-directory entries differing only by case.
#
# If we can rely
# on this, we can change the rules which use the names below to permit a package
# named opengl, even though OpenGL is an extension module.

# Unfortunately, we'd still have
# to rule out a toplevel package named Build, since build is a reserved
# directory name -- import might not be confused, but the code which wants
# to locally create and use the "build" subdirectory would be.

# Package names we can't use at the top level:
disallowedToplevelPackageNames = {
    "build"        : "temporary directory for compiling some .pyx files", # can this be renamed? (see setup*.py or extensions.py)
    "ui"           : "name of subdirectory for icons/images", # should be renamed, but hard to do
    "main"         : "reserved for main.py",
}

# Package names we can't use at any level:
disallowedPackageNames = {
    "globals"      : "python built-in function",
    "global"       : "python keyword",
    "CVS"          : "name of CVS control directory",
    "scratch"      : "our convention for a scratch-file directory",
    "outtakes"     : "our convention for an outtakes directory",
    "experimental" : "our convention for an experimental-code directory",
    "sim"          : "import sim is reserved for sim.so/dll, even if it's missing",
    "OpenGL"       : "extension module",
    "Numeric"      : "extension module",
    "Image"        : "extension module",
    "math"         : "Python library module",
}

# Module names we can't use at the top level:
disallowedToplevelModuleNames = {
}

# Module names we can't use at any level:
# NOTE: It turns out we also can't use any toplevel package name
# as a module name. [bruce 080202]
disallowedModuleNames = {
    "globals"      : "python built-in function",
    "global"       : "python keyword",
    "sim"          : "import sim is reserved for sim.so/dll, even if it's missing",
    "OpenGL"       : "extension module",
    "Numeric"      : "extension module",
    "Image"        : "extension module",
    "math"         : "Python library module",
}


# ===

# status of packageMapping as of 071210:

# virtual packages named below but not yet listed above:
# "?" - unclassified [maybe none at present]
# "operation" - tentative, for ops on model, could be model or controller
# "tools"

# names of existing Python packages (in theory all should appear above)
# - appearing above: exprs, PM, utilities, model
# - not yet appearing above: startup, dna_model, dna_updater, gui

# modules listed below but no longer output at toplevel by AllPyFiles.sh:
#   assembly - now in model/
#   whatsthis - now in gui/



# plans for specific classifications:

# ne1 package, for overall layout of ne1, as opposed some other app made from same pieces incl ui pieces
# (eg a small app for testing or script-running)

# simulation or analysis package, subdirs for GROMACS, GAMESS, ND-1(?), general? runsim too. some io code not separated.
# replaces some "operations" classifications; essentially a type of ops and io combined.
# levels: sim over ops over model, but we expect arcs in all directions in there, for now.


# update, 071217 2pm:
# the layer|topic is only used in a few entries; the others are "layer" with topic mentioned in the comment.
# look for @@@ to see a few things to review, and the place i got to in my overall scan.
# when done i need to review all at once the "simulation", *mode*, "ui", and *dialog entries.


packageColors = { # needs geometry, platform, and whatever new classifications we add below
    "ui"              : "#8050ff",
    "PM"              : "#8070ff",
    "graphics"        : "#80a0ff",
    "geometry"        : "#8040ff",

    "model"           : "#80ff50",
    "foundation"      : "#80ff70",
    "exprs"           : "#80ffa0",
    "commands"        : "#80ff20",

    "io"              : "#ffff80",
    "utilities"       : "#ffa080",
    "platform"        : "#ffc080",

    "prototype"       : "#ffffff",
##    "examples"        : "#ff3030",
##    "test"            : "#ff3060",
    
    "top_level"       : "#ff3090",
    "root"            : "#ff3090",
    "startup"         : "#ff3090",
    "top"             : "#ff3090",
    
    }

# ==

packageLevels = {
    # plan: for each entry, review it, revise subclassifications. @@@
    # put in basic topics like dna...
    "top_level"   : 7, # files that need to stay at top level for technical reasons (we'll put them at top of import graph)
    "top"         : 7, # files that need to stay at top level for technical reasons (we'll put them at top of import graph)
    "root"        : 7, # other files that belong at top of import graph (but that might be moved into subdirs)
    "startup"     : 7, # other files that belong at top of import graph (but that might be moved into subdirs)
##    "test"        : 7, ### none left!
##    "examples"    : 7, ### DEPRECATED as a layer, revise it (could be a topic but not sure if we have any yet) @@@
    "ui"          : 6, # has 137 instances - half the modules. (not counting new ones like command, unsplit_mode, simulation)
    "commands"    : 6,
    "PM"          : 6,
    "io"          : 5, #? hmm, so high?
    "model"       : 4, #k wants subdivision? not urgent...
    "graphics"    : 4,
    "foundation"  : 3,
    "exprs"       : 3,
    "geometry"    : 3,
    "utilities"   : 2,
    "platform"    : 1,
    }

_levels_highest_first = [ # TODO: finish, then use this to compute the above; in future make it a general DAG (not urgent)
    ["top_level",
     "root",
##     "test",
##     "examples",
     ],

    ["ui",
     "PM",
     ],

    ["io",
     ],
    # ... more
 ]

# ==

###doc these; anything with '?' is unfinalized; anything with '!' indicates an error in input

layer_aliases = {
    # standardize to plural form
    "graphics_behavior" : "graphics_behaviors",
    "graphics_drawable" : "graphics_drawables",
    "graphics_mode"     : "graphics_modes",
    "graphics_view"     : "graphics_views", # should rename right here to graphics_display_styles
    "graphics_widget"   : "graphics_widgets",
    "operation"         : "operations",
    "temporary_command" : "temporary_commands",
    "widget"            : "widgets",
 }

topic_mapping = {
    # default topics for layers
    "graphics_behaviors": "graphics/behaviors",
    "graphics_drawables": "graphics/drawables",
    "graphics_drawing"  : "graphics/drawing",
    "graphics_images"   : "graphics/images",
    "graphics_io"       : "graphics/io!", # deprecated, all to be refiled
    "graphics_modes"    : "graphics/modes!", # deprecated
    "graphics_views"    : "graphics/display_styles", ###
    "graphics_widgets"  : "graphics/widgets",

    "ui/menu"           : "ne1_ui/menus",
    "ui/toolbar"        : "ne1_ui/toolbars",

    # layers which are deprecated when used directly for topics
    "graphics"          : "graphics!", # all have been refiled (I think)
    "io"                : "io!", # all have been refiled (I think)
    "ui"                : "ui!", # all have been refiled (I think)
    "unsplit_mode"      : "unsplit_mode!",  # all have been refiled (I think)

    # expand topic abbrevs into actual pathnames
    "ESP"               : "analysis/ESP", # refactoring: maybe io part (if more general) would be processes/NanoHive
    "GAMESS"            : "analysis/GAMESS",    
    "GROMACS"           : "simulation/GROMACS",
    "DnaSequenceEditor"    : "dna/DnaSequenceEditor",

    # add notes to certain topics -- for that see subdir_notes below
 }

# ==

packageMapping_for_packages = {
    # existing packages (in each case so far, all files now in them have the same fate)
    # (in two cases, gui and startup, they should first just be renamed, then new files moved into them)

    "dna_model"                        : "model|dna/model",
    "dna_updater"                      : "model_updater|dna/updater", ###?? be consistent with what we do for other model_updater code
    "exprs"                            : "exprs", # (someday will be refactored and split)
    "gui"                              : "ui|ne1_ui", # along with other files (or into a whatsthis subpackage?)
    "model"                            : "model", # along with other files
    "PM"                               : "widgets|PM",
    "startup"                          : "root|ne1_startup",
    "utilities"                        : "utilities",
}

packageMapping_for_files = {
    # files presently at toplevel (except for a few that are already moved)
    
    # Note: of these modules, platform.py is in the way of proposed new package names,
    # so it needs to be renamed, but it is listed here in the usual way.
    # We also want to rename main.py -> ne1_main.py, but that's not urgent.
    # For all other module renamings, we can wait a bit; see a wiki page about them.
    
    "assembly"                         : "model", # (some foundation, but knows part.py which knows lots of ops & model constructors)
                                                  # (also: knows about selection, undo state, change counting, open file)
    "Assembly_API"                     : "model_api|foundation", # since not legit to be used below foundation
    "AtomGenerator"                    : "command|commands/BuildAtom",
    "AtomGeneratorPropertyManager"     : "ui/propmgr|commands/BuildAtom",
    "atomtypes"                        : "model", # or chemistry?
    "bonds"                            : "model", # Bond
    "bonds_from_atoms"                 : "operation",
    "bond_chains"                      : "operation",
    "bond_constants"                   : "model",
    "bond_drawer"                      : "graphics_drawing",
    "bond_updater"                     : "model_updater",
    "bond_utils"                       : "operation", # maybe also some ui
    "BoundingBox"                      : "geometry", # mostly geometry, some graphics, some hardcoded distance constants from model
    "BreakStrands_Command"             : "command|dna/commands/BreakStrands", # plural BreakStrands to match featurename as of 080104
    "BreakStrands_PropertyManager"     : "ui/propmgr|dna/commands/BreakStrands",
    "BuildAtomsPropertyManager"        : "ui/propmgr|commands/BuildAtoms",
    "BuildAtoms_Command"               : "command|commands/BuildAtoms",
    "BuildAtoms_GraphicsMode"          : "graphics_mode|commands/BuildAtoms",
    "BuildDna_EditCommand"             : "command|dna/commands/BuildDna",
    "BuildDna_GraphicsMode"            : "graphics_mode|dna/commands/BuildDna",
    "BuildDna_PropertyManager"         : "ui/propmgr|dna/commands/BuildDna",
    "build_utils"                      : "operation|commands/BuildAtoms", # AtomDepositionTool
    "builtin_command_loaders"          : "operations|commandSequencer",
    "changedicts"                      : "foundation",
    "changes"                          : "foundation",
    "chem"                             : "model",
    "chem_patterns"                    : "operation",
    "chunk"                            : "model",
    "ChunkProp"                        : "ui|commands/ChunkProperties?", #?? guess, probably wrong featurename
    "ChunkPropDialog"                  : "ui|commands/ChunkProperties?",
    "CommandToolbar_Constants"         : "widget|commandToolbar", # see module docstring for why
    "Command"                          : "command|command_support",
    "CommandToolbar"                   : "widget|commandToolbar", # controls the main hierarchical toolbar
    "CommandSequencer"                 : "operations|commandSequencer",
    "Comment"                          : "model",
    "CommentProp"                      : "ui/dialog|commands/CommentProperties?",
    "CommentPropDialog"                : "ui/dialog|commands/CommentProperties?",
    "confirmation_corner"              : "graphics_behavior",#? a MouseEventHandler; like a GraphicsMode or DragHandler; graphics_what?
    "constants"                        : "utilities",
    "CoNTubGenerator"                  : "command|commands/InsertHeterojunction",###?? @@@

    "CookieCtrlPanel"                  : "ui|commands/BuildCrystal",
    "cookieMode"                       : "unsplit_mode|commands/BuildCrystal",
    "CookiePropertyManager"            : "ui/propmgr|commands/BuildCrystal",
    "CookieShape"                      : "command|commands/BuildCrystal", # see docstring for reasons and caveats

    "crossovers"                       : "operation|dna/operations",
    "cursors"                          : "ui|ne1_ui",
    "CylinderChunks"                   : "graphics_view", # a ChunkDisplayMode
    "debug"                            : "utilities",
    "DebugMenuMixin"                   : "ui|widgets", # standard debug menu, used by multiple widgets
    "debug_prefs"                      : "utilities",
    "depositMode"                      : "unsplit_mode|commands/BuildAtoms", # Build Atoms Command and GraphicsMode
    "dimensions"                       : "graphics_drawing", # graphics output, not opengl-specific in principle
    "DirectionArrow"                   : "graphics_drawable", # a kind of DragHandler (drawable with behavior)
    "displaymodes"                     : "graphics_view", # ChunkDisplayMode
    "DnaCylinderChunks"                : "graphics_view", # a ChunkDisplayMode
    "DnaDuplex"                        : "operation|dna/commands/BuildDuplex", # class to help construct model objects defined elsewhere
    "DnaDuplex_EditCommand"            : "command|dna/commands/BuildDuplex",
    "DnaDuplexPropertyManager"         : "ui/propmgr|dna/commands/BuildDuplex",
    "DnaGenerator"                     : "command|dna/commands/BuildDuplex_old",
    "DnaGeneratorPropertyManager"      : "ui/propmgr|dna/commands/BuildDuplex_old",
    "DnaGenHelper"                     : "operation|dna/commands/BuildDuplex_old",
    "DnaLineMode"                      : "temporary_command|dna/temporary_commands", #?
    "DnaSegment_EditCommand"           : "command|dna/commands/DnaSegment",
    "DnaSegment_GraphicsMode"          : "graphics_mode|dna/commands/DnaSegment",
    "DnaSegment_PropertyManager"       : "ui/propmgr|dna/commands/DnaSegment",
    "DnaSegment_ResizeHandle"          : "graphics_drawable|dna/commands/DnaSegment", # [bruce 080207 reclassified to stay with command]
    "DnaSequenceEditor"                : "widget|DnaSequenceEditor", # a major ui component, and maybe a widget (guess, didn't look at code)
    "DnaStrand_EditCommand"            : "command|dna/commands/DnaStrand",
    "DnaStrand_GraphicsMode"           : "graphics_mode|dna/commands/DnaStrand",
    "DnaStrand_PropertyManager"        : "ui/propmgr|dna/commands/DnaStrand",
    "DnaStrand_ResizeHandle"           : "graphics_drawable|dna/commands/DnaStrand",
    "Dna_Constants"                    : "model|dna/model", # (since used by lots of files in several dna-related commands)
    "DragHandler"                      : "graphics_drawable",
    "drawNanotubeLadder"               : "graphics_drawing",
    "drawDnaRibbons"                   : "graphics_drawing",
    "drawDnaLadder"                    : "graphics_drawing",
    "drawing_globals"                  : "graphics_drawing",
    "glprefs"                          : "graphics_drawing",
    "setup_draw"                       : "graphics_drawing",
    "shape_vertices"                   : "graphics_drawing",
    "ColorSorter"                      : "graphics_drawing",
    "CS_workers"                       : "graphics_drawing",
    "CS_ShapeList"                     : "graphics_drawing",
    "CS_draw_primitives"               : "graphics_drawing",
    "drawers"                          : "graphics_drawing",
    "draw_bond_vanes"                  : "graphics_drawing",
    "draw_grid_lines"                  : "graphics_drawing",
    "DynamicTip"                       : "graphics_widgets", # but some should be refactored into GraphicsMode
    "EditCommand"                      : "command|command_support",
    "EditCommand_PM"                   : "ui/propmgr|command_support",
    "Elem"                             : "model", # chemistry?
    "elementColors"                    : "ui/dialog|commands/ElementColors?",
    "ElementColorsDialog"              : "ui/dialog|commands/ElementColors?",
    "elements"                         : "model", # class PeriodicTable, and our specific one??
    "elementSelector"                  : "ui/dialog|commands/ElementSelector?",
    "ElementSelectorDialog"            : "ui/dialog|commands/ElementSelector?",
    "elements_data"                    : "model", # model_data? like some constants?
    "elements_data_PAM3"               : "model|dna/model",
    "elements_data_PAM5"               : "model|dna/model",
    "EndUser"                          : "utilities",
    "env"                              : "foundation", # not utilities - only meant to be used from foundation or above
    
    "ESPImage"                         : "model|ESP", # (but all ESPImage code should be refactored for more general images)
    "ESPImageProp"                     : "ui/dialog|ESP", # question: is this a property manager? are ui/dialog and ui/propmgr the same?
    "ESPImagePropDialog"               : "ui/dialog|ESP",
    
    "example_expr_command"             : "command|prototype",
    
    "ExecSubDir"                       : "top_level",
    "extrudeMode"                      : "unsplit_mode|commands/Extrude",
    "ExtrudePropertyManager"           : "ui/propmgr|commands/Extrude",
    "fileIO"                           : "graphics_io|graphics/rendering", # should be split into files_mdl and files_povray
    "files_gms"                        : "io|GAMESS", 
    "files_mmp"                        : "io|files/mmp", # along with a sibling doc file, files_mmp_format_version.txt
    "files_mmp_registration"           : "foundation|files/mmp",
    "files_mmp_writing"                : "io|files/mmp",
    "files_nh"                         : "io|ESP", 
    "files_pdb"                        : "io|files/pdb",
    "Font3D"                           : "graphics_drawing",
    
    "FuseChunks_Command"               : "command|commands/Fuse",
    "FuseChunks_GraphicsMode"          : "graphics_mode|commands/Fuse",
    "fusechunksMode"                   : "unsplit_mode|commands/Fuse",
    "FusePropertyManager"              : "ui/propmgr|commands/Fuse",
    
    "GamessJob"                        : "operations|GAMESS", # contains operations and io
    "GamessProp"                       : "ui|GAMESS",
    "GamessPropDialog"                 : "ui|GAMESS",
    "GeneratorBaseClass"               : "ui/propmgr|command_support",
        # or as itself, so import implications are clearer in package import graph?
        # todo in code: split subclasses so this can be superceded by EditCommand and EditCommand_PM
    "GeneratorController"              : "ui/propmgr|command_support", # code type is a guess, but doesn't matter for now
    "generator_button_images"          : "ui/dialog|command_support",
    "geometry"                         : "geometry",
    "GlobalPreferences"                : "utilities", #? - imports debug_prefs & prefs_constants, dubious for utilities; or constants??
    "global_model_changedicts"         : "model",
    
    "GLPane"                           : "graphics_widgets",
    "GLPane_minimal"                   : "graphics_widgets",
    "glselect_name_dict"               : "graphics_drawing", #bruce 080223; really an "OpenGL drawing utility"
    
    "gpl_only"                         : "platform",
    "GrapheneGenerator"                : "command|commands/InsertGraphene",
    "GrapheneGeneratorPropertyManager" : "ui/propmgr|commands/InsertGraphene",
    "GraphicsMode"                     : "graphics_mode|command_support",
    "GraphicsMode_API"                 : "ui_api|command_support", # not legit to be needed by anything below ui, i think
    "GridPlaneProp"                    : "ui/dialog|commands/GridPlaneProperties?",
    "GridPlanePropDialog"              : "ui/dialog|commands/GridPlaneProperties?",
    "GROMACS"                          : "io|GROMACS", #? - old demo code. runs a GROMACS process. contains io.
    "Group"                            : "foundation", # some model code?
    "GroupButtonMixin"                 : "PM", # (deprecated, and its only callers should use things from PM instead)
    "GroupProp"                        : "ui/dialog|commands/GroupProperties?",
    "GroupPropDialog"                  : "ui/dialog|commands/GroupProperties?",
    "Guides"                           : "graphics_drawing", # drawing code for rulers 
    "handles"                          : "graphics_drawable", # graphical handles (for Extrude, but could be general)
    "help"                             : "ui/dialog|ne1_ui/help",
    "HelpDialog"                       : "ui/dialog|ne1_ui/help",
    "HistoryWidget"                    : "ui|history", # the history subsystem (should be split into several files)
    "icon_utilities"                   : "io|utilities", #? - could be considered utilities, io, or platform, or maybe images
    "ImageUtils"                       : "graphics_images", # graphics_images? images? graphics? graphics_io? (only use of graphics_images)
    "_import_roots"                    : "top_level",
    "Initialize"                       : "utilities",
    "inval"                            : "foundation",
    "jigmakers_Mixin"                  : "operations", # tells Part how to create & edit various Jigs (some ui?)
    
    "JigProp"                          : "ui/propmgr|command_support", # used directly for simple jigs, but clearest if treated as class
    "JigPropDialog"                    : "ui/propmgr|command_support", # (and pkg name/loc should not look like a command name)
    
    "jigs"                             : "model", # class Jig, and a few subclasses
    "jigs_measurements"                : "model",
    "jigs_motors"                      : "model",
    "jigs_planes"                      : "model",
    "jig_Gamess"                       : "model|GAMESS",
    "JobManager"                       : "ui|GAMESS", # ui/operations/io; scratch; needs refactoring; job_manager package?
        # note: this is in GAMESS only due to an import cycle issue. It should be in processes or in its own toplevel package.
    "JobManagerDialog"                 : "ui|GAMESS", # same package as JobManager (wrong now, see its note for why)
    "JoinStrands_Command"              : "command|dna/commands/JoinStrands",
    "JoinStrands_PropertyManager"      : "ui/propmgr|dna/commands/JoinStrands",
    "Line"                             : "model",
    "LinearMotor_EditCommand"          : "command|commands/LinearMotorProperties?",
    "LinearMotorPropertyManager"       : "ui/propmgr|commands/LinearMotorProperties?",
    "LineMode"                         : "temporary_command", #?? a temporary command and gm... apparently can be used directly?

    "main"                             : "top_level", # someday to be renamed to ne1_main
    "master_model_updater"             : "model_updater",
    "mdldata"                          : "graphics_io|graphics/rendering/mdl",
    "menu_helpers"                     : "widgets",
    "MinimizeEnergyProp"               : "ui/dialog|commands/MinimizeEnergy",
    "MinimizeEnergyPropDialog"         : "ui/dialog|commands/MinimizeEnergy",
    "ModelTree"                        : "model|modelTree", # a model which implems the api class for modelTreeGui (rename modelTree.py to modelTree/ModelTree.py)
    "modelTreeGui"                     : "widget|modelTree", # a widget with view & maybe some control code
    "modes"                            : "unsplit_mode|command_support",
    "modifyMode"                       : "unsplit_mode|commands/Move", #? MoveChunks?? probably not, we'll deemphasize Chunks to users
    "MotorPropertyManager"             : "ui/propmgr|command_support", # and rename to EditMotor_PM.py? but we don't have EditMotor.py ...
    "Move_Command"                     : "command|commands/Move",
    "Move_GraphicsMode"                : "graphics_mode|commands/Move",
    "MovePropertyManager"              : "ui/propmgr|commands/Move",
    "movie"                            : "simulation", #? hold simparams, or open moviefile - internal model, some ui/control/ops/io
    "moviefile"                        : "io|files/dpb_trajectory",
    "movieMode"                        : "unsplit_mode|commands/PlayMovie",
    "MoviePropertyManager"             : "ui/propmgr|commands/PlayMovie",
    "MWsemantics"                      : "ui|ne1_ui",
    
    "NamedView"                        : "model", # was Csys
    
    "NanoHive"                         : "ui|ESP", # ui/control/ops for running ESP (etc?) calcs using NanoHive. ui for now.
    "NanoHiveDialog"                   : "ui|ESP",
    "NanoHiveUtils"                    : "?|ESP", # Mostly control & io code. Some model & ui code (via assy arg & assy.w).
    "NanoHive_SimParameters"           : "model|ESP",

    "NE1ToolBar"                       : "widget", # Variant of QToolBar
    "NE1_QToolBar"                     : "widget", # New main toolbar class for the NE1 main window.
    "Node_as_MT_DND_Target"            : "controller|modelTree",
    "node_indices"                     : "foundation",
    "NodeWithAtomContents"             : "foundation",

    "objectBrowse"                     : "utilities", # debug
    "ops_atoms"                        : "operations",
    "ops_connected"                    : "operations",
    "ops_copy"                         : "operations", # parts may be foundation
    "ops_files"                        : "operations", # also has some io
    "ops_motion"                       : "operations",
    "ops_rechunk"                      : "operations",
    "ops_select"                       : "operations", # for a selection package??
    "ops_view"                         : "operations", # for a view package???
    "ops_display"                      : "operations",
    "ops_modify"                       : "operations",
    "op_select_doubly"                 : "operations",
    
    "PanMode"                          : "temporary_command",
    "ParameterDialog"                  : "widget|command_support", #?
    "parse_utils"                      : "utilities",
    "part"                             : "model", #? - foundation (if clipboard is), but knows lots of model & operations too
    "PartLibPropertyManager"           : "ui/propmgr|commands/PartLibrary",
    "PartLibraryMode"                  : "unsplit_mode|commands/PartLibrary",
    "PartProp"                         : "ui/dialog|commands/PartProperties?",
    "PartPropDialog"                   : "ui/dialog|commands/PartProperties?",
    "pastables"                        : "operations", # supports pasting operations
    "PasteMode"                        : "unsplit_mode|commands/Paste",
    "PastePropertyManager"             : "ui/propmgr|commands/Paste",
    
    "pi_bond_sp_chain"                 : "model",
    "Plane"                            : "model",
    "Plane_EditCommand"                : "command|commands/PlaneProperties?",
    "PlanePropertyManager"             : "ui/propmgr|commands/PlaneProperties?",
    "PlatformDependent"                : "platform", # ok, but really it's a mix of platform, utilities, io.
    "PlotTool"                         : "ui/dialog|commands/Plot?",
    "PlotToolDialog"                   : "ui/dialog|commands/Plot?",
    "Plugins"                          : "ui|processes", # ui, operations or utility, and io;
        # relates to "external processes" - we might add a classification for that
    
    "povheader"                        : "graphics_io|graphics/rendering/povray",
    "povray"                           : "graphics_io|graphics/rendering/povray", # also has ui code
    "PovrayScene"                      : "model", # for povray package, maybe
    "PovraySceneProp"                  : "ui/dialog|commands/PovraySceneProperties?", # for povray package, maybe
    "PovrayScenePropDialog"            : "ui/dialog|commands/PovraySceneProperties?", # for povray package, maybe
    
    "preferences"                      : "foundation", # see module docstring for explanation
    "prefsTree"                        : "model", # see docstring for caveats
    "prefs_constants"                  : "utilities", # or constants? see module docstring for explanation

    "prefs_widgets"                    : "widgets", #? - might not work -- ### needs splitting, some goes in foundation
    "Process"                          : "io|processes",
    "ProteinChunks"                    : "graphics_view",
    "PyrexSimulator"                   : "io|simulation",
    
    "qt4transition"                    : "utilities",
    
    "qutemol"                          : "graphics_io|graphics/rendering/qutemol",
    "QuteMolPropertyManager"           : "ui/propmgr|commands/QuteMol?", # commandname? (or, for a qutemol package??)
        # it's a single-file Command, View->QuteMol, with a launch (external renderer) button and maybe some options...
        # but what is the VerbNoun form? Does it have a featurename now? Wiki & whatsthis say Feature:QuteMol, so I went with that.
    
    "ReferenceGeometry"                : "model", 
    "reposition_baggage"               : "operations",
    "ResizeHandle"                     : "graphics_drawable", # (a DragHandler)
    "RotaryMotor_EditCommand"          : "command|commands/RotaryMotorProperties?", ###?? to fit VerbNoun, and not conflict with model class @@@
    "RotaryMotorPropertyManager"       : "ui/propmgr|commands/RotaryMotorProperties?",
    "RotateMode"                       : "temporary_command",
    "RotationHandle"                   : "graphics_drawable",#? needs reclassification?
    "runSim"                           : "simulation", # includes perhaps ui, controller, io
    
    "SelectAtoms_Command"              : "command|commands/SelectAtoms", # even though only used as a superclass now
    "SelectAtoms_GraphicsMode"         : "graphics_mode|commands/SelectAtoms",
    "selectAtomsMode"                  : "unsplit_mode|commands/SelectAtoms",
    
    "SelectChunks_Command"             : "command|commands/SelectChunks", # used directly, as well as as a superclass
    "SelectChunks_GraphicsMode"        : "graphics_mode|commands/SelectChunks",
    "selectMolsMode"                   : "unsplit_mode|commands/SelectChunks",
    
    "Select_Command"                   : "command|commands/Select",
    "Select_GraphicsMode"              : "graphics_mode|commands/Select",
    "Select_GraphicsMode_DrawMethod_preMixin"    : "graphics_mode|commands/Select",
    "Select_GraphicsMode_MouseHelpers_preMixin"    : "graphics_mode|commands/Select",
    "selectMode"                       : "unsplit_mode|commands/Select",
    
    "Selobj"                           : "graphics_drawable", #bruce 080116/080202 revised this (would be _api if we had that)
    
    "ServerManager"                    : "ui|processes", #? specific to GAMESS? maybe, but shouldn't. persistent db/UI for servers list
    "ServerManagerDialog"              : "ui|processes",
        
    "shape"                            : "graphics_behavior", # tentative, maybe risky; see docstring
    "Slab"                             : "geometry",

    "SimJob"                           : "model|simulation", #? only subclass is GamessJob; unclear whether specific to GAMESS; io too
    "SimServer"                        : "model|simulation", # hold attrs for a sim server (unclear whether specific to GAMESS); io too
    "SimSetup"                         : "ui|simulation",
    "SimSetupDialog"                   : "ui|simulation",
    "Sponsors"                         : "ui|sponsors", # the Sponsors subsystem (lots of kinds of code; exports widgets)

    "state_constants"                  : "foundation",
    "state_utils"                      : "foundation", # note: utilities/Comparison.py and samevals.c might go with this too
    
    "StatProp"                         : "ui/dialog|commands/ThermostatProperties?",
    "StatPropDialog"                   : "ui/dialog|commands/ThermostatProperties?",
    "StatusBar"                        : "widget", # used as a specific part of the NE1 main window, but general-purpose code
    "SurfaceChunks"                    : "graphics_view",
    
    "TemporaryCommand"                 : "temporary_commands", # or command_support??
    
    "testdraw"                         : "graphics_mode|exprs", # (mostly prototype, but also has some exprs framework code)
    "testmode"                         : "unsplit_mode|exprs", # (ditto)
    
    "test_commands"                    : "command|prototype",
    "test_commands_init"               : "command|prototype",
    "test_command_PMs"                 : "ui/propmgr|prototype",
    "test_connectWithState"            : "command|prototype",
    "test_connectWithState_constants"  : "command|prototype",
    "test_connectWithState_PM"         : "ui/propmgr|prototype",
    
    "texture_fonts"                    : "graphics_drawing",
    "texture_helpers"                  : "graphics_drawing", #? also graphics_io - split it?
    
    "ThermoProp"                       : "ui/dialog|commands/ThermometerProperties?",
    "ThermoPropDialog"                 : "ui/dialog|commands/ThermometerProperties?",
    
    "ThumbView"                        : "graphics_widgets",
    "Trackball"                        : "graphics_behavior",
    "TranslateChunks_Command"          : "command|commands/Translate",
    "TranslateChunks_GraphicsMode"     : "graphics_mode|commands/Translate",
    "RotateChunks_Command"             : "command|commands/Rotate",
    "RotateChunks_GraphicsMode"        : "graphics_mode|commands/Rotate",

    # Note: many of the following (and of the other modules slated for ne1_ui)
    # ought to get refactored, with some parts not remaining in ne1_ui.
    # Also, some of them might be best off in specific subpackages of ne1_ui,
    # but I'm not yet trying to classify anything in ne1_ui that finely,
    # partly since some of them need too much refactoring for that
    # to make sense just yet, and partly since I don't know them well,
    # and Mark is presently doing some refactoring within them.
    # The only exception is ne1_ui/help, which may not be complete,
    # but seems obvious enough and worth doing.
    # [bruce 080101]
    
    "Ui_BuildAtomsPropertyManager"     : "ui/propmgr|commands/BuildAtoms",
    "Ui_BuildStructuresMenu"           : "ui/menu",
    "Ui_BuildStructuresToolBar"        : "ui/toolbar",
    "Ui_BuildToolsMenu"                : "ui/menu",
    "Ui_BuildToolsToolBar"             : "ui/toolbar",
    "Ui_CommandToolbar"                : "ui/toolbar|ne1_ui/toolbars", # UI and content/layout for Command Toolbar
    "Ui_CookiePropertyManager"         : "ui/propmgr|commands/BuildCrystal",
    "Ui_DimensionsMenu"                : "ui/menu",#?
    "Ui_DisplayStylesToolBar"          : "ui/toolbar|ne1_ui/toolbars",
    "Ui_NanotubeFlyout"                     : "ui/toolbar|ne1_ui/toolbars", # I'm guessing this has to be in ne1_ui, not dna
    "Ui_DnaFlyout"                     : "ui/toolbar|ne1_ui/toolbars", # I'm guessing this has to be in ne1_ui, not dna
    "Ui_EditMenu"                      : "ui/menu",
    "Ui_ExtrudePropertyManager"        : "ui/propmgr|commands/Extrude",
    "Ui_FileMenu"                      : "ui/menu",
    "Ui_HelpMenu"                      : "ui/menu|ne1_ui/help", #??? ne1_ui/menus?
    "Ui_InsertMenu"                    : "ui/menu",
    "Ui_MainWindow"                    : "ui|ne1_ui",
    "Ui_MainWindowWidgets"             : "ui|ne1_ui",
    "Ui_MainWindowWidgetConnections"   : "ui|ne1_ui",
    "Ui_MovePropertyManager"           : "ui/propmgr|commands/Move",
    "Ui_MoviePropertyManager"          : "ui/propmgr|commands/PlayMovie",
    "Ui_PartWindow"                    : "widget|ne1_ui", #?
    "Ui_RenderingMenu"                 : "ui/menu",
    "Ui_RenderingToolBar"              : "ui/toolbar",
    "Ui_ReportsDockWidget"             : "widget|ne1_ui",
    "Ui_SelectMenu"                    : "ui/menu",
    "Ui_SelectToolBar"                 : "ui/toolbar",
    "Ui_DnaSequenceEditor"             : "widget|DnaSequenceEditor", # in dna/  ??
    "Ui_SimulationMenu"                : "ui/menu",
    "Ui_SimulationToolBar"             : "ui/toolbar",
    "Ui_StandardToolBar"               : "ui/toolbar",
    "Ui_StandardViewsToolBar"          : "ui/toolbar",
    "Ui_ToolsMenu"                     : "ui/menu",
    "Ui_ViewMenu"                      : "ui/menu",
    "Ui_ViewOrientation"               : "ui|ne1_ui",
    "Ui_ViewToolBar"                   : "ui/toolbar",
    
    "undo_internals"                   : "foundation",
    "undo_archive"                     : "foundation",
    "undo_manager"                     : "foundation",
    "undo_UI"                          : "operations", # or operations/undo?
    
    "UserPrefs"                        : "ui|ne1_ui",
    "UserPrefsDialog"                  : "ui|ne1_ui",
    "Utility"                          : "foundation", # some model code?
    
    "version"                          : "utilities", # or constants? see docstring for caveats
    "ViewOrientationWindow"            : "widget|ne1_ui",
    "VQT"                              : "geometry",
    
    "whatsthis_utilities"              : "foundation", #? or utilities?
        # (imports of this file are foundation or above)
        # this file imports env (for win; could be refactored to not do so, eg use an arg), nothing else high up.
    "widget_helpers"                   : "widgets", # soon to be renamed to this from widgets.py
    "widget_controllers"               : "widgets",

    "wiki_help"                        : "ui|foundation", # mostly ui, some io.
        # conclusion, bruce 080101: if we have a help module outside ne1_ui, put it there;
        # if we don't, it probably belongs in something like foundation.
        # (Note: if we want a toplevel help package, we'd need to rename help.py first.
        #  Guess: for now just put this into foundation; probably "help" makes more sense
        #  as a subpackage of foundation than as something independent and toplevel, anyway.)
    
    "ZoomToAreaMode"                   : "temporary_command",
    "ZoomInOutMode"                    : "temporary_command",
    }

# ==

# now combine those into one dict for use by current code in packageDependency.py

for package_name in packageMapping_for_packages.keys():
    assert not packageMapping_for_files.has_key( package_name)

packageMapping = dict( packageMapping_for_files)

packageMapping.update( packageMapping_for_packages)

packageGroupMapping = {
    "analysis.ESP"                    : "model",
    "analysis.GAMESS"                 : "model",
    "cnt.commands.BuildNanotube"      : "commands",
    "cnt.commands.NanotubeSegment"    : "commands",
    "cnt.commands.InsertNanotube"     : "commands",
    "cnt.model"                       : "model",
    "cnt.temporary_commands"          : "commands",
    "cnt.updater"                     : "model",
    "commands.BuildAtom"              : "commands",
    "commands.BuildAtoms"             : "commands",
    "commands.BuildCrystal"           : "commands",
    "commands.ChunkProperties"        : "commands",
    "commands.CommentProperties"      : "commands",
    "commands.ElementColors"          : "commands",
    "commands.ElementSelector"        : "commands",
    "commandSequencer"                : "commands",
    "commands.Extrude"                : "commands",
    "commands.Fuse"                   : "commands",
    "commands.GridPlaneProperties"    : "commands",
    "commands.GroupProperties"        : "commands",
    "commands.InsertGraphene"         : "commands",
    "commands.InsertHeterojunction"   : "commands",
    "commands.InsertNanotube"         : "commands",
    "commands.InsertPeptide"          : "commands",
    "commands.LinearMotorProperties"  : "commands",
    "commands.MinimizeEnergy"         : "commands",
    "commands.Move"                   : "commands",
    "commands.PartLibrary"            : "commands",
    "commands.PartProperties"         : "commands",
    "commands.Paste"                  : "commands",
    "commands.PlaneProperties"        : "commands",
    "commands.PlayMovie"              : "commands",
    "commands.Plot"                   : "commands",
    "commands.PovraySceneProperties"  : "commands",
    "commands.QuteMol"                : "commands",
    "commands.RotaryMotorProperties"  : "commands",
    "commands.Rotate"                 : "commands",
    "commands.SelectAtoms"            : "commands",
    "commands.SelectChunks"           : "commands",
    "commands.Select"                 : "commands",
    "commands.ThermometerProperties"  : "commands",
    "commands.ThermostatProperties"   : "commands",
    "commands.Translate"              : "commands",
    "command_support"                 : "commands",
    "commandToolbar"                  : "commands",
    "dna.commands.BreakStrands"       : "commands",
    "dna.commands.BuildDna"           : "commands",
    "dna.commands.BuildDuplex"        : "commands",
    "dna.commands.BuildDuplex_old"    : "commands",
    "dna.commands.DnaSegment"         : "commands",
    "dna.commands.DnaStrand"          : "commands",
    "dna.commands.JoinStrands"        : "commands",
    "dna.DnaSequenceEditor"           : "ui",
    "dna.model"                       : "model",
    "dna.operations"                  : "model",
    "dna.temporary_commands"          : "commands",
    "dna.updater"                     : "model",
    "exprs"                           : "exprs",
    "files.dpb_trajectory"            : "io",
    "files.mmp"                       : "io",
    "files.pdb"                       : "io",
    "foundation"                      : "foundation",
    "geometry"                        : "geometry",
    "graphics.behaviors"              : "graphics",
    "graphics.display_styles"         : "graphics",
    "graphics.drawables"              : "graphics",
    "graphics.drawing"                : "graphics",
    "graphics.images"                 : "graphics",
    "graphics.rendering"              : "graphics",
    "graphics.rendering.mdl"          : "graphics",
    "graphics.rendering.povray"       : "graphics",
    "graphics.rendering.qutemol"      : "graphics",
    "graphics.widgets"                : "graphics",
    "history"                         : "utilities",
    "modelTree"                       : "ui",
    "model_updater"                   : "model",
    "ne1_startup"                     : "startup",
    "ne1_ui.help"                     : "ui",
    "ne1_ui.menus"                    : "ui",
    "ne1_ui"                          : "ui",
    "ne1_ui.toolbars"                 : "ui",
    "operations"                      : "model",
    "platform"                        : "platform",
    "PM"                              : "ui",
    "processes"                       : "ui",
    "simulation.GROMACS"              : "io",
    "simulation"                      : "io",
    "sponsors"                        : "ui",
    "temporary_commands"              : "commands",
    "widgets"                         : "ui",
    }

# ==

# these definitions are to make the listing done by packageData_checker more informative.

# lists of highly desirable renamings and/or refactorings, needed for understandability of classification

needs_renaming_for_clarity = { # just suggestions, not yet discussed/decided
    "bond_utils" : "bond_menu_helpers",
    "cursors"    : "load_custom_cursors?",
    "fileIO"     : "povray/files_povray and mdl/files_mdl (split it)", # also needs_refactoring
    "GROMACS"    : "GROMACS_demo?", # temporary demo of atomic-level-DNA GROMACS simulation (maybe for outtakes?)
    "help"       : "Ne1HelpDialog or HelpDialog",
    "HelpDialog" : "Ui_HelpDialog",
    "Line"       : "ReferenceLine?", # Line should be reserved for pure geometry
    "main"       : "ne1_main (hard, not urgent)",
    "movie"      : "what?", # it's an object for a set of sim params, and optionally the results file made by using them
    "moviefile"  : "files_dpb?",
    "Plane"      : "ReferencePlane?", # Plane should be reserved for pure geometry
    "platform"   : "debug_flags",
    "Selobj"     : "Selobj_API for now", # not urgent; not the correct new name
    "shape"      : "what?", # also needs_refactoring
    "StatProp"   : "ThermostatProperties?", # disambiguate Thermometer and Thermostat
    "ThermoProp" : "ThermometerProperties?", # disambiguate Thermometer and Thermostat
    "Utility"    : "Node",
    "qutemol"    : "qutemol_io?",

    # deprecated files
    "GroupButtonMixin"  : "GroupButtonMixin_deprecated?",

##    # kluge: use fake renamings to add notes for the listing
##    "JobManager" : "(should be processes or own package -- import cycle issue)",
##    "JobManagerDialog" : "(should stay with JobManager)",
 }

needs_refactoring = [
    "fileIO", # needs splitting in two, each part renamed; exports writepovfile, writemdlfile
    "GLPane", # needs splitting into several classes, some for general use and some for "main graphics area"
        # (also needs to not be the same object as the CommandSequencer)
    "HistoryWidget", # needs split into a few cooperating objects (archive, widget, io, storage ops)
    "JobManager", # import cycle issue - GamessJob used in two places: value in jobType, constructor in __createJobs
    "PlatformDependent", # needs split
    "prefs_widgets", # needs connectWithState stuff (and more?) split out into foundation
    "shape", # needs splitting
    "version", # split/register: ne1_ui part to supply data, foundation part for access
 ]

# listing order for toplevel packages, outer to inner
# (will be related to permitted import order, when that's implemented, but not equal to it, e.g. "less important later")
# (a string here matches itself, or itself + " " + anything, to permit added notes in topic_mapping)
# (nfr: permit inserted note strings to be printed before sets of toplevel dirs?)

listing_order = [ ### should be complete, but not yet properly ordered
    "ne1_startup",
    "ne1_ui",
    # commands
    "command_support",
    "commands",
    "temporary_commands",
    # major subsystems (order?)
    "history",
    "modelTree",
    "commandSequencer",
    "commandToolbar",
    "sponsors",

    # functional areas
    "dna",
    "simulation",
    "analysis",
    
    # kinds of operations
    "model_updater",
    "operations",

    # other kinds of code (order?)
    "model",
    "graphics",
    
    "widgets",
    "processes",
    "files",
    "PM",

    "exprs",
    "foundation",
    "geometry",
    "platform",
    "utilities",

    # special kinds
    "top_level",
    "prototype",
 ]

# notes for specific subdirs, to include in the listing (with word-wrapping)

subdir_notes = {
    "analysis/GAMESS" : "JobManager doesn't belong here, but is here for now "\
                        "to work around an import cycle issue. Probably easy to fix "\
                        "when it matters.",
    "commands" : "command package names ending with '?' need discussion",
    "files" : "should we de-abbreviate file extensions used in directory names, "\
              "e.g. ProteinDataBank, MolecularMachinePart, DifferentialPositionBytes? [-- EricM]",
    "graphics/rendering" : "(this is only about rendering by external programs; rename it?)",
    "ne1_ui" : "could define more (or fewer, or different) subpackages if desired",
    "ne1_ui/help" : "(not sure about Ui_HelpMenu being in here)",
    "PM"    : "should PM be renamed to PropertyManager? [-- EricM]",
    "top_level" : "(these files can't presently be moved into subdirectories, for technical reasons)",
 }

# ==

# some topics above:
# todo: review:
# - processes
# - io
# eg povray
# - simulation
# - exprs/prototype
# - prototype

# end
