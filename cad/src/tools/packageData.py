# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
packageData.py -- data about modules and packages, for PackageDependency.py

@author: Eric M
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

packageColors = { # needs geometry, platform
    "ui"              : "#8050ff",
    "PM"              : "#8070ff",
    "graphics"        : "#80a0ff",

    "model"           : "#80ff50",
    "foundation"      : "#80ff70",
    "exprs"           : "#80ffa0",

    "io"              : "#ffff80",
    "utilities"       : "#ffa080",

    "examples"        : "#ff3030",
    "test"            : "#ff3060",
    "top"             : "#ff3090",
    }

packageLevels = {
    "top"         : 7,
    "test"        : 7,
    "examples"    : 7,
    "ui"          : 6,
    "PM"          : 6,
    "io"          : 5,
    "model"       : 4,
    "graphics"    : 4,
    "foundation"  : 3,
    "exprs"       : 3,
    "geometry"    : 3,
    "utilities"   : 2,
    "platform"    : 1,
    }

# NIM: warn or enforce the non-use of the following names (case-insensitively?)
# We don't list every possible disallowed name,
# just the ones that we might be tempted to use otherwise.
#
# Note: on Mac, python import seems to be case-sensitive even though you can't
# have two filesystem-directory entries differing only by case. If we can rely
# on this, we can permit ourselves to have packages named opengl and Build,
# even though OpenGL is an extension module and build is a reserved directory
# name.

# Package names we can't use at the top level:
disallowedToplevelPackageNames = {
    "build"        : "temporary directory for compiling some .pyx files", # probably ok except at toplevel, and we might want Build
    "ui"           : "name of subdirectory for icons/images", # should be renamed
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
disallowedModuleNames = {
    "globals"      : "python built-in function",
    "global"       : "python keyword",
    "sim"          : "import sim is reserved for sim.so/dll, even if it's missing",
    "OpenGL"       : "extension module",
    "Numeric"      : "extension module",
    "Image"        : "extension module",
    "math"         : "Python library module",
}


# status as of 071210:

# virtual packages named below but not yet listed above:
# "?" - unclassified [maybe none at present]
# "operation" - tentative, for ops on model, could be model or controller
# "tools"
# "top_level"

# ... listed above but not yet used below (and not a Python package):
# "top"

# names of existing Python packages (in theory all should appear above)
# - appearing above: exprs, PM, utilities, model
# - not yet appearing above: startup, dna_model, dna_updater, gui

# modules listed below but no longer output at toplevel by AllPyFiles.sh:
#   assembly - now in model/
#   pyrex_test - exists as .c .pyx .so but not as .py
#   whatsthis - now in gui/

packageMapping = {
    "assembly"                         : "model", # (some foundation, but knows part.py which knows lots of ops & model constructors)
                                                  # (also: knows about selection, undo state, change counting, open file)
    "Assembly_API"                     : "foundation", # put all _API in foundation for now
    "AtomGenerator"                    : "ui/command/generator",
    "AtomGeneratorPropertyManager"     : "ui/propmgr",
    "atomtypes"                        : "model", # or chemistry?
    "bonds"                            : "model", # Bond
    "bonds_from_atoms"                 : "operation",
    "bond_chains"                      : "operation",
    "bond_constants"                   : "model",
    "bond_drawer"                      : "graphics",
    "bond_updater"                     : "updater",
    "bond_utils"                       : "operation", # maybe also some ui
    "BoundingBox"                      : "model", # mostly geometry, some graphics, some hardcoded distance constants
    "BuildAtomsPropertyManager"        : "ui/propmgr",
    "build_utils"                      : "operation", # AtomDepositionTool
    "changedicts"                      : "foundation",
    "changes"                          : "foundation",
    "chem"                             : "model",
    "chem_patterns"                    : "operation",
    "chunk"                            : "model",
    "ChunkProp"                        : "ui",
    "ChunkPropDialog"                  : "ui",
    "CmdMgr_Constants"                 : "ui",
    "Command"                          : "ui",
    "CommandManager"                   : "ui",
    "CommandSequencer"                 : "ui",
    "Comment"                          : "model",
    "CommentProp"                      : "ui",
    "CommentPropDialog"                : "ui",
    "confirmation_corner"              : "graphics_behavior",#? a MouseEventHandler; like a GraphicsMode or DragHandler; graphics_what?
    "constants"                        : "utilities",
    "CoNTubGenerator"                  : "ui",
    "CookieCtrlPanel"                  : "ui",
    "cookieMode"                       : "ui",
    "CookiePropertyManager"            : "ui",
    "crossovers"                       : "operation",
    "Csys"                             : "model",
    "cursors"                          : "ui",
    "CylinderChunks"                   : "graphics_view",#? a ChunkDisplayMode; graphics_what? _view? _style?
    "debug"                            : "utilities",
    "DebugMenuMixin"                   : "ui", # menu spec and ops for debug menu
    "debug_prefs"                      : "utilities", # (foundation? nah)
    "depositMode"                      : "ui", # Build Atoms Command and GraphicsMode
    "dimensions"                       : "graphics", # graphics output, not opengl-specific in principle
    "DirectionArrow"                   : "graphics_behavior", # a kind of DragHandler (drawable with behavior); graphics_what?
    "displaymodes"                     : "graphics_view", # ChunkDisplayMode; graphics_what?
    "Dna"                              : "operation", # obs?
    "DnaDuplex"                        : "operation", # class to help construct model objects defined elsewhere
    "DnaDuplexEditController"          : "ui/controller",
    "DnaDuplexPropertyManager"         : "ui/propmgr",
    "DnaGenerator"                     : "ui", # obs?
    "DnaGeneratorPropertyManager"      : "ui/propmgr", # obs?
    "DnaLineMode"                      : "ui",#?
    "Dna_Constants"                    : "model",#?
    "DragHandler"                      : "graphics_behavior",
    "drawer"                           : "graphics",
    "draw_bond_vanes"                  : "graphics",
    "draw_grid_lines"                  : "graphics",
    "DynamicTip"                       : "graphics_widgets", # but some should be refactored into GraphicsMode
    "EditController"                   : "ui/controller",
    "EditController_PM"                : "ui/propmgr",
    "Elem"                             : "model", # chemistry?
    "elementColors"                    : "ui/dialog",
    "ElementColorsDialog"              : "ui/dialog",
    "elements"                         : "model", # class PeriodicTable, and our specific one??
    "elementSelector"                  : "ui/dialog",
    "ElementSelectorDialog"            : "ui/dialog",
    "elements_data"                    : "model", # model_data? like some constants?
    "elements_data_PAM3"               : "model", # in dna
    "elements_data_PAM5"               : "model", # in dna
    "EndUser"                          : "utilities",
    "env"                              : "foundation", # not utilities - only meant to be used from foundation or above
    "ESPImageProp"                     : "ui/dialog", # question: is this a property manager? are ui/dialog and ui/propmgr the same?
    "ESPImagePropDialog"               : "ui/dialog", 
    "example_expr_command"             : "examples",#?
    "ExecSubDir"                       : "top_level",
    "extensions"                       : "top_level", # (someday, find a way to move it into a subdir)
    "extrudeMode"                      : "ui",
    "ExtrudePropertyManager"           : "ui/propmgr",
    "fileIO"                           : "graphics_io", # should be split into files_mdl and files_povray
    "files_gms"                        : "io", # for a gamess package
    "files_mmp"                        : "io", # perhaps for an mmp_io package?
    "files_nh"                         : "io", # for a nanohive esp package
    "files_pdb"                        : "io",
    "Font3D"                           : "graphics",
    "fusechunksMode"                   : "ui",
    "FusePropertyManager"              : "ui",
    "GamessJob"                        : "io",
    "GamessProp"                       : "ui",
    "GamessPropDialog"                 : "ui",
    "GeneratorBaseClass"               : "ui",
    "GeneratorController"              : "ui",
    "generator_button_images"          : "ui",
    "geometry"                         : "geometry",
    "GlobalPreferences"                : "utilities",
    "global_model_changedicts"         : "model", #?
    "GLPane"                           : "graphics",
    "GLPane_minimal"                   : "graphics",
    "gpl_only"                         : "platform",
    "GrapheneGenerator"                : "ui",
    "GrapheneGeneratorPropertyManager" : "ui",
    "GraphicsMode"                     : "ui",
    "GraphicsMode_API"                 : "ui",
    "GridPlaneProp"                    : "ui",
    "GridPlanePropDialog"              : "ui",
    "GROMACS"                          : "io",
    "Group"                            : "foundation", # some model code?
    "GroupButtonMixin"                 : "ui",
    "GroupProp"                        : "ui",
    "GroupPropDialog"                  : "ui",
    "handles"                          : "ui",
    "help"                             : "ui",
    "HelpDialog"                       : "ui",
    "HistoryWidget"                    : "ui",
    "icon_utilities"                   : "io",
    "ImageUtils"                       : "io",
    "_import_roots"                    : "top_level",
    "Initialize"                       : "utilities",
    "inval"                            : "foundation",
    "jigmakers_Mixin"                  : "model", # tells Part how to create & edit various Jigs (some ui?)
    "JigProp"                          : "ui",
    "JigPropDialog"                    : "ui",
    "jigs"                             : "model",
    "jigs_measurements"                : "model",
    "jigs_motors"                      : "model",
    "jigs_planes"                      : "model",
    "jig_Gamess"                       : "model",
    "JobManager"                       : "ui",
    "JobManagerDialog"                 : "ui",
    "Line"                             : "ui", # geometry, model?
    "LinearMotorEditController"        : "ui",
    "LinearMotorPropertyManager"       : "ui",
    "LineMode"                         : "ui",
    "main"                             : "top_level",
    "MainWindowUI"                     : "ui",
    "master_model_updater"             : "model",
    "mdldata"                          : "io",
    "MinimizeEnergyProp"               : "ui",
    "MinimizeEnergyPropDialog"         : "ui",
    "modelTree"                        : "ui",
    "modelTreeGui"                     : "ui",
    "modes"                            : "ui",
    "modifyMode"                       : "ui",
    "MotorPropertyManager"             : "ui",
    "MovePropertyManager"              : "ui",
    "movie"                            : "ui", # mixture of stuff
    "moviefile"                        : "io",
    "movieMode"                        : "ui",
    "MoviePropertyManager"             : "ui",
    "MWsemantics"                      : "ui",
    "NanoHive"                         : "ui",
    "NanoHiveDialog"                   : "ui",
    "NanoHiveUtils"                    : "io",
    "NanotubeGenerator"                : "ui",
    "NanotubeGeneratorPropertyManager" : "ui",
    "NE1ToolBar"                       : "ui",
    "Node_as_MT_DND_Target"            : "ui",
    "node_indices"                     : "foundation",
    "objectBrowse"                     : "utilities",
    "ops_atoms"                        : "model",
    "ops_connected"                    : "model",
    "ops_copy"                         : "model", # parts may be foundation
    "ops_files"                        : "io",
    "ops_motion"                       : "model",
    "ops_rechunk"                      : "model",
    "ops_select"                       : "model",
    "ops_view"                         : "ui", # parts may be graphics
    "op_select_doubly"                 : "model",
    "PanMode"                          : "ui",
    "ParameterDialog"                  : "ui",
    "parse_utils"                      : "io",
    "part"                             : "foundation", # model, graphics?
    "PartLibPropertyManager"           : "ui",
    "PartLibraryMode"                  : "ui",
    "PartProp"                         : "ui",
    "PartPropDialog"                   : "ui",
    "pastables"                        : "model", # supports pasting operations
    "PasteMode"                        : "ui",
    "PastePropertyManager"             : "ui",
    "pi_bond_sp_chain"                 : "model",
    "Plane"                            : "ui", # geometry, model? [model]
    "PlaneEditController"              : "ui",
    "PlanePropertyManager"             : "ui",
    "platform"                         : "utilities",
    "PlatformDependent"                : "platform",
    "PlotTool"                         : "ui",
    "PlotToolDialog"                   : "ui",
    "Plugins"                          : "ui", # ?
    "povheader"                        : "io",
    "povray"                           : "io",
    "PovrayScene"                      : "model", # ?
    "PovraySceneProp"                  : "ui",
    "PovrayScenePropDialog"            : "ui",
    "preferences"                      : "utilities",
    "prefsTree"                        : "ui",
    "prefs_constants"                  : "utilities",
    "prefs_widgets"                    : "ui",
    "Process"                          : "io",
    "PropMgr_Constants"                : "PM",
    "pyrex_test"                       : "top_level",
    "qt4transition"                    : "utilities",
    "qutemol"                          : "io",
    "QuteMolPropertyManager"           : "ui",
    "ReferenceGeometry"                : "ui", # geometry, model?
    "reposition_baggage"               : "model",
    "ResizeHandle"                     : "ui", # interactive graphics - package will be revised
    "RotaryMotorEditController"        : "ui",
    "RotaryMotorPropertyManager"       : "ui",
    "RotateMode"                       : "ui",
    "runSim"                           : "io",
    "selectAtomsMode"                  : "ui",
    "selectMode"                       : "ui",
    "selectMolsMode"                   : "ui",
    "Selobj"                           : "ui", # graphics?
    "SequenceEditor"                   : "ui",
    "ServerManager"                    : "ui",
    "ServerManagerDialog"              : "ui",
    "setup"                            : "tools",
    "setup2"                           : "tools",
    "shape"                            : "ui", # geometry, graphics?
    "SimJob"                           : "io",
    "SimServer"                        : "io",
    "SimSetup"                         : "ui",
    "SimSetupDialog"                   : "ui",
    "Sponsors"                         : "ui",
    "state_constants"                  : "foundation",
    "state_utils"                      : "foundation",
    "state_utils_unset"                : "foundation",
    "StatProp"                         : "ui",
    "StatPropDialog"                   : "ui",
    "StatusBar"                        : "ui",
    "SurfaceChunks"                    : "geometry",
    "TemporaryCommand"                 : "ui",
    "testdraw"                         : "test",
    "testmode"                         : "test",
    "test_commands"                    : "test",
    "test_commands_init"               : "test", # all these test* modules might be reclassified
    "test_command_PMs"                 : "test",
    "test_connectWithState"            : "test",
    "test_connectWithState_constants"  : "test",
    "test_connectWithState_PM"         : "test",
    "texture_fonts"                    : "graphics",
    "texture_helpers"                  : "graphics",
    "ThermoProp"                       : "ui",
    "ThermoPropDialog"                 : "ui",
    "ThumbView"                        : "graphics",
    "Ui_BuildAtomsPropertyManager"     : "ui",
    "Ui_BuildStructuresMenu"           : "ui",
    "Ui_BuildStructuresToolBar"        : "ui",
    "Ui_BuildToolsMenu"                : "ui",
    "Ui_BuildToolsToolBar"             : "ui",
    "Ui_CommandManager"                : "ui",
    "Ui_CookiePropertyManager"         : "ui",
    "Ui_DimensionsMenu"                : "ui",
    "Ui_DnaFlyout"                     : "ui",
    "Ui_EditMenu"                      : "ui",
    "Ui_ExtrudePropertyManager"        : "ui",
    "Ui_FileMenu"                      : "ui",
    "Ui_HelpMenu"                      : "ui",
    "Ui_InsertMenu"                    : "ui",
    "Ui_MovePropertyManager"           : "ui",
    "Ui_MoviePropertyManager"          : "ui",
    "Ui_PartWindow"                    : "ui",
    "Ui_SelectMenu"                    : "ui",
    "Ui_SelectToolBar"                 : "ui",
    "Ui_SequenceEditor"                : "ui",
    "Ui_SimulationMenu"                : "ui",
    "Ui_SimulationToolBar"             : "ui",
    "Ui_StandardToolBar"               : "ui",
    "Ui_ToolsMenu"                     : "ui",
    "Ui_ViewMenu"                      : "ui",
    "Ui_ViewOrientation"               : "ui",
    "Ui_ViewToolBar"                   : "ui",
    "undo"                             : "foundation",
    "undo_archive"                     : "foundation",
    "undo_manager"                     : "foundation",
    "undo_UI"                          : "ui",
    "UserPrefs"                        : "ui",
    "UserPrefsDialog"                  : "ui",
    "Utility"                          : "foundation", # some model code?
    "version"                          : "utilities",
    "ViewOrientationWindow"            : "ui",
    "VQT"                              : "geometry",
    "whatsthis"                        : "ui",
    "widgets"                          : "ui",
    "widget_controllers"               : "ui",
    "wiki_help"                        : "ui", # some io?
    "ZoomMode"                         : "ui",
    }

# end
