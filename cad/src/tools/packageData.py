# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
packageData.py -- data about modules and packages, for PackageDependency.py

@author: Eric M, Bruce
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


# NFR: @@@
#
# missing modules should be classified as themselves, so they are very visible in the graph
# and so the arcs you see help you classify them properly.
#
# ne1 package, for overall layout of ne1 as opposed some other app made from same pieces incl ui pieces
# (eg a small app for testing or script-running)
#
# use codetype/topic and have an option to ignore the /topic part when graphing
#
### simulation package, subdirs for gromacs, gamess, nd1, general? runsim too. some io code not separated.
# replaces some "operations" classifications; essentially a type of ops and io combined.
# levels: sim over ops over model, but we expect arcs in all directions in there, for now.

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
    "Assembly_API"                     : "foundation_api", # not legit to be used below foundation
    "AtomGenerator"                    : "ui/controller",
    "AtomGeneratorPropertyManager"     : "ui/propmgr",
    "atomtypes"                        : "model", # or chemistry?
    "bonds"                            : "model", # Bond
    "bonds_from_atoms"                 : "operation",
    "bond_chains"                      : "operation",
    "bond_constants"                   : "model",
    "bond_drawer"                      : "graphics",
    "bond_updater"                     : "model_updater",
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
    "CoNTubGenerator"                  : "ui/controller",###?? @@@

    "CookieCtrlPanel"                  : "ui",
    "cookieMode"                       : "ui",
    "CookiePropertyManager"            : "ui/propmgr",
    "CookieShape"                      : "command", # see docstring for reasons and caveats

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
    "DnaGenerator"                     : "ui/controller", # obs?
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
    "ESPImage"                         : "model", # for ESP package?
    "ESPImageProp"                     : "ui/dialog", # question: is this a property manager? are ui/dialog and ui/propmgr the same?
    "ESPImagePropDialog"               : "ui/dialog", # for ESP package?
    "example_expr_command"             : "examples",#?
    "ExecSubDir"                       : "top_level",
    "extensions"                       : "top_level", # (someday, find a way to move it into a subdir)
    "extrudeMode"                      : "ui",
    "ExtrudePropertyManager"           : "ui/propmgr",
    "fileIO"                           : "graphics_io", # should be split into files_mdl and files_povray
    "files_gms"                        : "io", # for a gamess package
    "files_mmp"                        : "io", # perhaps for an mmp_io package, along with a sibling doc file?
    "files_nh"                         : "io", # for a nanohive esp package
    "files_pdb"                        : "io", # perhaps for a pdb_io package, if any other files would be in it
    "Font3D"                           : "graphics",
    "fusechunksMode"                   : "ui",
    "FusePropertyManager"              : "ui/propmgr",
    "GamessJob"                        : "simulation", # for a gamess package; contains operations and io
    "GamessProp"                       : "ui/dialog", # for a gamess package
    "GamessPropDialog"                 : "ui/dialog", # for a gamess package
    "GeneratorBaseClass"               : "ui/propmgr", # or as itself, so whatever imports it won't import propmgr just from that??
        # should split subclasses so this can be superceded by EditController and EditController_PM
    "GeneratorController"              : "ui/controller", #? @@@ ui/controller that are subclassing ui/propmgr may need reclassification
    "generator_button_images"          : "ui/dialog", #?
    "geometry"                         : "geometry",
    "GlobalPreferences"                : "utilities", #? - imports debug_prefs & prefs_constants, dubious for utilities; or constants??
    "global_model_changedicts"         : "model",
    "GLPane"                           : "graphics_widgets",
    "GLPane_minimal"                   : "graphics_widgets",
    "gpl_only"                         : "platform",
    "GrapheneGenerator"                : "ui/controller",
    "GrapheneGeneratorPropertyManager" : "ui/propmgr",
    "GraphicsMode"                     : "graphics_mode",
    "GraphicsMode_API"                 : "ui_api", # not legit to be needed by anything below ui, i think
    "GridPlaneProp"                    : "ui/dialog",
    "GridPlanePropDialog"              : "ui/dialog",
    "GROMACS"                          : "simulation", #? - old demo code. runs a GROMACS process. contains io. for gromacs package.
    "Group"                            : "foundation", # some model code?
    "GroupButtonMixin"                 : "PM", # (deprecated, and its only callers should use things from PM instead)
    "GroupProp"                        : "ui/dialog",
    "GroupPropDialog"                  : "ui/dialog",
    "handles"                          : "graphics_behavior", # graphical handles (for Extrude, but could be general)
    "help"                             : "ui/dialog", # ui_help package?
    "HelpDialog"                       : "ui/dialog", # ui_help package?
    "HistoryWidget"                    : "ui", # for History package (as a major ui component)?
    "icon_utilities"                   : "io", #? - could be considered utilities, io, or platform, or maybe images
    "ImageUtils"                       : "graphics_images", # graphics_images? images?
    "_import_roots"                    : "top_level",
    "Initialize"                       : "utilities",
    "inval"                            : "foundation",
    "jigmakers_Mixin"                  : "operations", # tells Part how to create & edit various Jigs (some ui?)
    "JigProp"                          : "ui/propmgr", #? - guess
    "JigPropDialog"                    : "ui/propmgr",
    "jigs"                             : "model", # class Jig, and a few subclasses
    "jigs_measurements"                : "model",
    "jigs_motors"                      : "model",
    "jigs_planes"                      : "model",
    "jig_Gamess"                       : "model", # for gamess package?
    "JobManager"                       : "ui", # ui/operations/io; scratch; needs refactoring; job_manager package?
    "JobManagerDialog"                 : "ui", 
    "Line"                             : "model",
    "LinearMotorEditController"        : "ui/controller",
    "LinearMotorPropertyManager"       : "ui/propmgr",
    "LineMode"                         : "ui/temporary_mode",#? a temporary command and gm...
    "main"                             : "top_level",
    "MainWindowUI"                     : "ui",
    "master_model_updater"             : "model_updater",
    "mdldata"                          : "graphics_io",
    "MinimizeEnergyProp"               : "ui",#?
    "MinimizeEnergyPropDialog"         : "ui",#?
    "modelTree"                        : "model_tree", # for model_tree package; a model which implems the api class for modelTreeGui
    "modelTreeGui"                     : "model_tree", # for model_tree package; a widget with view & maybe some control code
    "modes"                            : "ui",
    "modifyMode"                       : "ui",
    "MotorPropertyManager"             : "ui/propmgr",
    "MovePropertyManager"              : "ui/propmgr",
    "movie"                            : "simulation", #? hold simparams, or open moviefile - internal model, some ui/control/ops/io
    "moviefile"                        : "io",
    "movieMode"                        : "ui",
    "MoviePropertyManager"             : "ui/propmgr",
    "MWsemantics"                      : "ui",
    
    "NanoHive"                         : "ui", # for ESP package; ui/control/ops for running ESP (etc?) calcs using NanoHive. ui for now.
    "NanoHiveDialog"                   : "ui", # for ESP package
    "NanoHiveUtils"                    : "simulation", # for ESP package; Mostly control & io code. Some model & ui code (via assy arg & assy.w).
    "NanoHive_SimParameters"           : "model", # for ESP package

    "NanotubeGenerator"                : "ui/controller",
    "NanotubeGeneratorPropertyManager" : "ui/propmgr",
    "NE1ToolBar"                       : "ui/widgets", # Variant of QToolBar
    "Node_as_MT_DND_Target"            : "model_tree", # controller for model_tree package
    "node_indices"                     : "foundation",

    "objectBrowse"                     : "utilities", # debug
    "ops_atoms"                        : "operations",
    "ops_connected"                    : "operations",
    "ops_copy"                         : "operations", # parts may be foundation
    "ops_files"                        : "operations", # also has some io
    "ops_motion"                       : "operations",
    "ops_rechunk"                      : "operations",
    "ops_select"                       : "operations", # for a selection package??
    "ops_view"                         : "operations", # for a view package???
    "op_select_doubly"                 : "operations",
    
    "PanMode"                          : "ui",
    "ParameterDialog"                  : "ui",
    "parse_utils"                      : "utilities",
    "part"                             : "model", #? - foundation (if clipboard is), but knows lots of model & operations too
    "PartLibPropertyManager"           : "ui/propmgr",
    "PartLibraryMode"                  : "ui",
    "PartProp"                         : "ui",
    "PartPropDialog"                   : "ui",
    "pastables"                        : "operations", # supports pasting operations
    "PasteMode"                        : "ui",
    "PastePropertyManager"             : "ui/propmgr",
    
    "pi_bond_sp_chain"                 : "model",
    "Plane"                            : "model",
    "PlaneEditController"              : "ui/controller",
    "PlanePropertyManager"             : "ui/propmgr",
    "platform"                         : "utilities", # debug; rename platform.atom_debug -> debug_flags.debug ??
    "PlatformDependent"                : "platform", # ok, but really it's a mix of platform, utilities, io.
    "PlotTool"                         : "ui",
    "PlotToolDialog"                   : "ui",
    "Plugins"                          : "ui", # ui, operations or utility, and io;
        # relates to "external processes" - we might add a classification for that
    
    "povheader"                        : "graphics_io", # for povray package
    "povray"                           : "graphics_io", # also has ui code; for povray package, maybe
    "PovrayScene"                      : "model", # for povray package, maybe
    "PovraySceneProp"                  : "ui", # for povray package, maybe
    "PovrayScenePropDialog"            : "ui", # for povray package, maybe
    
    "preferences"                      : "foundation", # see module docstring for explanation
    "prefsTree"                        : "model", # see docstring for caveats
    "prefs_constants"                  : "utilities", # or constants? see module docstring for explanation

    "prefs_widgets"                    : "ui/widgets", #? - might not work -- needs splitting, some goes in foundation
    "Process"                          : "io",
    "PropMgr_Constants"                : "PM",
    "pyrex_test"                       : "top_level", #? I don't know if this matters - pyrex_test only exists as .c and .pyx and .so
    
    "qt4transition"                    : "utilities",
    "qutemol"                          : "io", # graphics_io?? for a qutemol package?
        # relates to "external processes" - we might add a classification for that
    
    "QuteMolPropertyManager"           : "ui/propmgr", # for a qutemol package??
    
    "ReferenceGeometry"                : "model", 
    "reposition_baggage"               : "operations",
    "ResizeHandle"                     : "graphics_behavior", # (a DragHandler)
    "RotaryMotorEditController"        : "ui/controller",
    "RotaryMotorPropertyManager"       : "ui/propmgr",
    "RotateMode"                       : "ui",
    "runSim"                           : "simulation", # includes perhaps ui, controller, io
    
    "selectAtomsMode"                  : "unsplit_mode",
    "SelectAtoms_Command.py"           : "command",
    "SelectAtoms_GraphicsMode.py"      : "graphics_mode",
    "SelectChunks_Command.py"          : "command",
    "SelectChunks_GraphicsMode.py"     : "graphics_mode",
    "selectMode"                       : "unsplit_mode",
    "selectMolsMode"                   : "unsplit_mode",
    "Select_Command.py"                : "command",
    "Select_GraphicsMode.py"           : "graphics_mode",
    "Select_GraphicsMode_DrawMethod_preMixin.py" : "graphics_mode",
    "Select_GraphicsMode_MouseHelpers_preMixin.py" : "graphics_mode",
    
    "Selobj"                           : "graphics_behavior_api", # (revisit when done)
    
    "SequenceEditor"                   : "ui", # a major ui component, and maybe a widget (guess, didn't look at code)
    
    "ServerManager"                    : "ui",
    "ServerManagerDialog"              : "ui",
    
    "setup"                            : "tools", # build (part of tools)
    "setup2"                           : "tools", # build
    
    "shape"                            : "graphics_behavior", # tentative, maybe risky; see docstring
    "Slab"                             : "geometry",

    # @@@ where i am in file is up to here, and paper too

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
    "test_commands_init"               : "test", # all these test* modules might be reclassified @@@
    "test_command_PMs"                 : "ui/propmgr", # for test/example/scratch?
    "test_connectWithState"            : "test",
    "test_connectWithState_constants"  : "test",
    "test_connectWithState_PM"         : "ui/propmgr", # for test/example/scratch?
    
    "texture_fonts"                    : "graphics",
    "texture_helpers"                  : "graphics",
    
    "ThermoProp"                       : "ui",
    "ThermoPropDialog"                 : "ui",
    
    "ThumbView"                        : "graphics_widgets",
    
    "Ui_BuildAtomsPropertyManager"     : "ui/propmgr",
    "Ui_BuildStructuresMenu"           : "ui",
    "Ui_BuildStructuresToolBar"        : "ui",
    "Ui_BuildToolsMenu"                : "ui",
    "Ui_BuildToolsToolBar"             : "ui",
    "Ui_CommandManager"                : "ui",
    "Ui_CookiePropertyManager"         : "ui/propmgr",
    "Ui_DimensionsMenu"                : "ui",
    "Ui_DnaFlyout"                     : "ui",
    "Ui_EditMenu"                      : "ui",
    "Ui_ExtrudePropertyManager"        : "ui/propmgr",
    "Ui_FileMenu"                      : "ui",
    "Ui_HelpMenu"                      : "ui",
    "Ui_InsertMenu"                    : "ui",
    "Ui_MovePropertyManager"           : "ui/propmgr",
    "Ui_MoviePropertyManager"          : "ui/propmgr",
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
    
    "version"                          : "utilities", # or constants? see docstring for caveats
    "ViewOrientationWindow"            : "ui",
    "VQT"                              : "geometry",
    
    "whatsthis"                        : "ui",
    "widgets"                          : "ui",
    "widget_controllers"               : "ui",
    "wiki_help"                        : "ui", # some io?
    
    "ZoomMode"                         : "ui",
    }

# end
