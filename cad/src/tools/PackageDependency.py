#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
   PackageDependency.py

   $Id$

   Takes a list of python files as arguments, writes a list of
   packages that each imports on stdout.  This information is in a
   format suitable for use with the GraphViz package.

   To use, run this on a list of all python files you're interested
   in, redirecting stdout to a file like depend.dot.  Stderr will
   recieve a list of modules with in and out arc counts for that node
   in the final graph.

   The program first reduces the tree to the graph of cycles.  It does
   this by removing nodes with either no incoming arcs, or no outgoing
   arcs, or those which only reference modules not in the argument
   list.  It performs this pruning repeatedly until no new exclusions
   are produced by an iteration.

   At that point, the output consists of only the cycles in the
   dependency graph.  This can be plotted with the dot program from
   the GraphViz package.

   To see the entire graph, comment out the pruneTree() loop.
from exprs import b, c as q, d # with a comment
"""

import sys
import re
import os.path

try:
    set
except NameError:
    # Define 'set', for versions of Python too old to define the builtin 'set',
    # but which have an almost-compatible sets module in their standard library
    # (which includes some versions we still run NE1 on, like 2.3). The only
    # incompatibility that affects this script is the need for an explicit
    # set(list2) coercion in set1.difference(set(list2)), when using sets.py.
    from sets import Set as set
    pass

fromImportLineRegex = re.compile(r'^\s*from\s+(\S+)\s+import\s+([^#]*)')
importLineRegex = re.compile(r'^\s*import\s+([^#]+)')
asRegex = re.compile(r'^(\S+)\s+as\s+')

pruneModules = []
"""
   The pruneModules list are those modules which didn't import any
   modules excluded in any of the module lists.  These are
   the leaves of the dependency tree.  At each stage, you prune off
   the leaves and expose a new layer of modules which no longer import
   any non-excluded modules.
"""

unreferencedModules = []
"""
   The unreferencedModules list are those which none of the
   non-excluded modules import.  These are roots of the dependency
   tree.
"""

externalModules = []
"""
   The externalModules list are those which are referenced, but are
   not in the set of arguments.
"""

rootsToKeep = set([
    "_import_roots",
    ])

libraryReferences = [
    "os",
    "os.path",
    "re",
    "sys",
    "time",
    "datetime",
    "math",
    "code",
    "types",
    "struct",
    "string",
    "pprint",
    "random",
    "inspect",
    "traceback",
    "exceptions",
    "shutil",
    "glob",
    "socket",
    "tokenize",
    "cPickle",
    "bsddb",
    "shelve",
    "doctest",
    "base64",
    "md5",
    "threading",
    "webbrowser",
    "urllib",
    "xml.dom.minidom",
    "hotshot",
    "profile",
    "distutils.core",
    "distutils.extension",
    "Pyrex.Distutils",
    "Pyrex",
    "Numeric",
    "LinearAlgebra",
    "Image",
    "ImageOps",
    "PngImagePlugin",
    "idlelib.Delegator",
    "OpenGL.GL",
    "OpenGL.GLU",
    "OpenGL.GLE",
    "OpenGL._GLE",
    "PyQt4",
    "PyQt4.Qt",
    "PyQt4.QtGui",
    "PyQt4.QtCore",
    "demo_trans",
    "sim",
    "atombase",
    "quux",
    "xxx",
    "bearing_data",
    "samevals",
    "psurface",
    ]

packageMapping = {
    "assembly"                     : "model",
    "AtomGeneratorPropertyManager" : "ui",
    "AtomGenerator"                : "ui",
    "atomtypes"                    : "model",
    "bond_constants"               : "model",
    "bond_drawer"                  : "graphics",
    "bonds_from_atoms"             : "model",
    "bonds"                        : "model",
    "bond_updater"                 : "model",
    "bond_utils"                   : "model",
    "BuildAtomsPropertyManager"    : "ui",
    "build_utils"                  : "ui",
    "changes"                      : "foundation",
    "chem_patterns"                : "model",
    "chem"                         : "model",
    "ChunkPropDialog"              : "ui",
    "ChunkProp"                    : "ui",
    "chunk"                        : "model",
    "CmdMgr_Constants"             : "ui",
    "CommandManager"               : "ui",
    "Command"                      : "ui",
    "CommentPropDialog"            : "ui",
    "CommentProp"                  : "ui",
    "Comment"                      : "model",
    "confirmation_corner"          : "ui",
    "constants"                    : "utilities",
    "CoNTubGenerator"              : "ui",
    "CookieCtrlPanel"              : "ui",
    "cookieMode"                   : "ui",
    "CookiePropertyManager"        : "ui",
    "crossovers"                   : "model",
    "cursors"                      : "ui",
    "CylinderChunks"               : "graphics",
    "DebugMenuMixin"               : "ui",
    "debug_prefs"                  : "utilities",
    "debug"                        : "utilities",
    "depositMode"                  : "ui",
    "dimensions"                   : "graphics",
    "DirectionArrow"               : "ui",
    "displaymodes"                 : "ui",
    "Dna_Constants"                : "model",
    "DnaGeneratorPropertyManager"  : "ui",
    "DnaGenerator"                 : "ui",
    "Dna"                          : "model",
    "DragHandler"                  : "ui",
    "draw_bond_vanes"              : "graphics",
    "drawer"                       : "graphics",
    "DynamicTip"                   : "ui",
    "EditController_PM"            : "ui",
    "EditController"               : "ui",
    "ElementColorsDialog"          : "ui",
    "elementColors"                : "ui",
    "ElementSelectorDialog"        : "ui",
    "elementSelector"              : "ui",
    "elements"                     : "model",
    "EndUser"                      : "utilities",
    "env"                          : "utilities",
    "ESPImagePropDialog"           : "ui",
    "ESPImageProp"                 : "ui",
    "example_expr_command"         : "examples",
    "extensions"                   : "top_level",
    "extrudeMode"                  : "ui",
    "ExtrudePropertyManager"       : "ui",
    "fileIO"                       : "io",
    "files_gms"                    : "io",
    "files_mmp"                    : "io",
    "files_nh"                     : "io",
    "files_pdb"                    : "io",
    "fusechunksMode"               : "ui",
    "FusePropertyManager"          : "ui",
    "GamessJob"                    : "io",
    "GamessPropDialog"             : "ui",
    "GamessProp"                   : "ui",
    "GeneratorBaseClass"           : "ui",
    "generator_button_images"      : "ui",
    "GeneratorController"          : "ui",
    "geometry"                     : "geometry",
    "GlobalPreferences"            : "utilities",
    "GLPane_minimal"               : "graphics",
    "GLPane"                       : "graphics",
    "gpl_only"                     : "platform",
    "GrapheneGeneratorPropertyManager"
                                   : "ui",
    "GrapheneGenerator"            : "ui",
    "GraphicsMode"                 : "ui",
    "GridPlanePropDialog"          : "ui",
    "GridPlaneProp"                : "ui",
    "GROMACS"                      : "io",
    "GroupButtonMixin"             : "ui",
    "GroupPropDialog"              : "ui",
    "GroupProp"                    : "ui",
    "handles"                      : "ui",
    "HelpDialog"                   : "ui",
    "help"                         : "ui",
    "HistoryWidget"                : "ui",
    "icon_utilities"               : "io",
    "ImageUtils"                   : "io",
    "_import_roots"                : "top_level",
    "Initialize"                   : "utilities",
    "inval"                        : "foundation",
    "jig_Gamess"                   : "model",
    "JigPropDialog"                : "ui",
    "JigProp"                      : "ui",
    "jigs_measurements"            : "model",
    "jigs_motors"                  : "model",
    "jigs_planes"                  : "model",
    "jigs"                         : "model",
    "JobManagerDialog"             : "ui",
    "JobManager"                   : "ui",
    "LinearMotorEditController"    : "ui",
    "LinearMotorPropertyManager"   : "ui",
    "Line"                         : "ui", # geometry, model?
    "main"                         : "top_level",
    "MainWindowUI"                 : "ui",
    "mdldata"                      : "io",
    "MinimizeEnergyPropDialog"     : "ui",
    "MinimizeEnergyProp"           : "ui",
    "modelTreeGui"                 : "ui",
    "modelTree"                    : "ui",
    "CommandSequencer"             : "ui",
    "modes"                        : "ui",
    "modifyMode"                   : "ui",
    "MotorPropertyManager"         : "ui",
    "MovePropertyManager"          : "ui",
    "moviefile"                    : "io",
    "movieMode"                    : "ui",
    "MoviePropertyManager"         : "ui",
    "movie"                        : "ui", # mixture of stuff
    "MWsemantics"                  : "ui",
    "NanoHiveDialog"               : "ui",
    "NanoHive"                     : "ui",
    "NanoHiveUtils"                : "io",
    "NanotubeGeneratorPropertyManager"
                                   : "ui",
    "NanotubeGenerator"            : "ui",
    "NE1ToolBar"                   : "ui",
    "node_indices"                 : "foundation",
    "ops_atoms"                    : "model",
    "ops_connected"                : "model",
    "ops_copy"                     : "model", # parts may be foundation
    "op_select_doubly"             : "model",
    "ops_files"                    : "io",
    "ops_motion"                   : "model",
    "ops_rechunk"                  : "model",
    "ops_select"                   : "model",
    "ops_view"                     : "ui", # parts may be graphics
    "PanMode"                      : "ui",
    "ParameterDialog"              : "ui",
    "parse_utils"                  : "io",
    "PartLibPropertyManager"       : "ui",
    "PartLibraryMode"              : "ui",
    "PartPropDialog"               : "ui",
    "PartProp"                     : "ui",
    "part"                         : "foundation", # model, graphics?
    "PasteMode"                    : "ui",
    "PastePropertyManager"         : "ui",
    "pi_bond_sp_chain"             : "model",
    "PlaneEditController"          : "ui",
    "PlanePropertyManager"         : "ui",
    "Plane"                        : "ui", # geometry, model?
    "PlatformDependent"            : "platform",
    "platform"                     : "utilities",
    "PlotToolDialog"               : "ui",
    "PlotTool"                     : "ui",
    "povheader"                    : "io",
    "povray"                       : "io",
    "PovrayScenePropDialog"        : "ui",
    "PovraySceneProp"              : "ui",
    "PovrayScene"                  : "model", # ?
    "preferences"                  : "utilities",
    "prefs_constants"              : "utilities",
    "prefsTree"                    : "ui",
    "prefs_widgets"                : "ui",
    "Process"                      : "io",
    "PropMgr_Constants"            : "PM",
    "pyrex_test"                   : "top_level",
    "qt4transition"                : "utilities",
    "qutemol"                      : "io",
    "ReferenceGeometry"            : "ui", # geometry, model?
    "reposition_baggage"           : "model",
    "RotaryMotorEditController"    : "ui",
    "RotaryMotorPropertyManager"   : "ui",
    "RotateMode"                   : "ui",
    "runSim"                       : "io",
    "selectAtomsMode"              : "ui",
    "selectMode"                   : "ui",
    "selectMolsMode"               : "ui",
    "Selobj"                       : "ui", # graphics?
    "ServerManagerDialog"          : "ui",
    "ServerManager"                : "ui",
    "setup2"                       : "tools",
    "setup"                        : "tools",
    "shape"                        : "ui", # geometry, graphics?
    "SimJob"                       : "io",
    "SimServer"                    : "io",
    "SimSetupDialog"               : "ui",
    "SimSetup"                     : "ui",
    "Sponsors"                     : "ui",
    "state_constants"              : "foundation",
    "state_utils"                  : "foundation",
    "state_utils_unset"            : "foundation",
    "StatPropDialog"               : "ui",
    "StatProp"                     : "ui",
    "StatusBar"                    : "ui",
    "SurfaceChunks"                : "geometry",
    "TemporaryCommand"             : "ui",
    "test_command_PMs"             : "test",
    "test_commands"                : "test",
    "test_connectWithState_constants"
                                   : "test",
    "test_connectWithState_PM"     : "test",
    "test_connectWithState"        : "test",
    "testdraw"                     : "test",
    "testmode"                     : "test",
    "ThermoPropDialog"             : "ui",
    "ThermoProp"                   : "ui",
    "ThumbView"                    : "graphics",
    "Ui_BuildAtomsPropertyManager" : "ui",
    "Ui_BuildStructuresMenu"       : "ui",
    "Ui_BuildStructuresToolBar"    : "ui",
    "Ui_BuildToolsMenu"            : "ui",
    "Ui_BuildToolsToolBar"         : "ui",
    "Ui_CommandManager"            : "ui",
    "Ui_CookiePropertyManager"     : "ui",
    "Ui_DimensionsMenu"            : "ui",
    "Ui_EditMenu"                  : "ui",
    "Ui_ExtrudePropertyManager"    : "ui",
    "Ui_FileMenu"                  : "ui",
    "Ui_HelpMenu"                  : "ui",
    "Ui_InsertMenu"                : "ui",
    "Ui_MovePropertyManager"       : "ui",
    "Ui_MoviePropertyManager"      : "ui",
    "Ui_PartWindow"                : "ui",
    "Ui_SelectMenu"                : "ui",
    "Ui_SelectToolBar"             : "ui",
    "Ui_SimulationMenu"            : "ui",
    "Ui_SimulationToolBar"         : "ui",
    "Ui_StandardToolBar"           : "ui",
    "Ui_ToolsMenu"                 : "ui",
    "Ui_ViewMenu"                  : "ui",
    "Ui_ViewOrientation"           : "ui",
    "Ui_ViewToolBar"               : "ui",
    "undo_archive"                 : "foundation",
    "undo_manager"                 : "foundation",
    "undo"                         : "foundation",
    "UserPrefsDialog"              : "ui",
    "UserPrefs"                    : "ui",
    "Utility"                      : "foundation", # some model code?
    "version"                      : "utilities",
    "ViewOrientationWindow"        : "ui",
    "VQT"                          : "geometry",
    "whatsthis"                    : "ui",
    "widget_controllers"           : "ui",
    "widgets"                      : "ui",
    "wiki_help"                    : "ui", # some io?
    "ZoomMode"                     : "ui",
    }

packageColors = {
    "ui"          : "#8060ff",
    "PM"          : "#8080ff",
    "graphics"    : "#80a0ff",

    "model"       : "#80ff60",
    "foundation"  : "#80ff80",
    "exprs"       : "#80ffa0",

    "io"          : "#ffff80",
    "utilities"   : "#ffe080",

    "examples"    : "#ff4040",
    "test"        : "#ff4080",
    "top"         : "#ff40a0",
    }

filesToProcess = []
optionPrintUnreferenced = False
optionPrintTables = False
optionJustCycles = False
optionByPackage = False
optionDontPrune = False
optionColorPackages = False

moduleNameToImportList = {}

# these four are set in initializeGlobals()
allProcessedModules = None
referencedModules = None
fromModuleCount = None
toModuleCount = None

def isPackage(moduleName):
    possiblePackageName = moduleName.replace(".", "/")
    if (os.path.isdir(possiblePackageName)):
        return True
    return False

def fileNameToModuleName(fileName):
    if (fileName.startswith("./")):
        fileName = fileName[2:]
    if (fileName.startswith("src/")):
        fileName = fileName[4:]
    if (fileName.endswith(".py")):
        fileName = fileName[:-3]
    fileName = fileName.replace("/", ".")
    return fileName

def dotReplacement(moduleName):
    ret = moduleName.replace(".", "_")
    ret = ret.replace("-", "_")
    return ret
    
def moduleToDotNode(moduleName, returnPackageName):
    if (returnPackageName):
        if (moduleName in libraryReferences):
            return "library"
        if (packageMapping.has_key(moduleName)):
            return packageMapping[moduleName]
        if (isPackage(moduleName)):
            return moduleName
        mod = moduleName
        while (True):
            i = mod.rfind(".")
            if (i < 0):
                return "top"
            mod = mod[:i]
            if (isPackage(mod)):
                return mod
    return moduleName

def printPackage(fromPackageName, toPackageName, fromModuleName, toModuleName):
    if (optionByPackage):
        if (toPackageName != "library" and toPackageName != "tools"):
            print >>sys.stderr, "%s -> %s, %s -> %s" % (fromPackageName, toPackageName, fromModuleName, toModuleName)

def importsInFile(fileName):
    importSet = set([])
    fromModuleName = fileNameToModuleName(fileName)
    fromModule = moduleToDotNode(fromModuleName, optionByPackage)
    f = open(fileName)
    for line in f:
        m = fromImportLineRegex.match(line)
        if (m):
            if (isPackage(m.group(1))):
                packageName = m.group(1)
                moduleImportList = m.group(2).strip().split(',')
                for toModuleName in moduleImportList:
                    toModuleName = toModuleName.strip()
                    m = asRegex.match(toModuleName)
                    if (m):
                        toModuleName = m.group(1)
                    toModuleName = packageName + "." + toModuleName
                    toModule = moduleToDotNode(toModuleName, optionByPackage)
                    if (toModule != fromModule):
                        importSet.add(toModule)
                        printPackage(fromModule, toModule, fromModuleName, toModuleName)
            else:
                toModule = moduleToDotNode(m.group(1), optionByPackage)
                if (toModule != fromModule):
                    importSet.add(toModule)
                    printPackage(fromModule, toModule, fromModuleName, m.group(1))
            continue
        m = importLineRegex.match(line)
        if (m):
            toModuleList = m.group(1).strip().split(',')
            for toModuleName in toModuleList:
                toModuleName = toModuleName.strip()
                m = asRegex.match(toModuleName)
                if (m):
                    toModuleName = m.group(1)
                toModule = moduleToDotNode(toModuleName, optionByPackage)
                if (toModule != fromModule):
                    importSet.add(toModule)
                    printPackage(fromModule, toModule, fromModuleName, toModuleName)
    f.close()
    if (moduleNameToImportList.has_key(fromModule)):
        # this happens if we're operating by package
        importSet = importSet.union(moduleNameToImportList[fromModule])
    importList = list(importSet)
    importList.sort()
    moduleNameToImportList[fromModule] = importList

nodeColors = {}

packageNodes = []

def createNode(name, fullModuleName):
    if (optionByPackage or not optionColorPackages or nodeColors.has_key(name)):
        return
    packageName = moduleToDotNode(fullModuleName, True)
    if (packageColors.has_key(packageName)):
        nodeColors[name] = packageColors[packageName]
        print '    %s [fillcolor="%s"];' % (name, nodeColors[name])
    else:
        print >>sys.stderr, "undefined package color: " + packageName

def printEdge(fromNode, toNode):
    fn = dotReplacement(fromNode)
    tn = dotReplacement(toNode)
    createNode(fn, fromNode)
    createNode(tn, toNode)
    print "    %s -> %s;" % (fn, tn)
    

def dependenciesInFile(fromModuleName, printing):
    if (fromModuleName in pruneModules or fromModuleName in unreferencedModules):
        return None
    allProcessedModules.add(fromModuleName)
    importList = moduleNameToImportList[fromModuleName]
    referencedModules.update(importList)
    outCount = 0
    for toModuleName in importList:
        if (toModuleName in externalModules or toModuleName in pruneModules or toModuleName in unreferencedModules):
            continue

        if (printing and toModuleName != "library" and toModuleName != "top" and toModuleName != "tools"):
            printEdge(fromModuleName, toModuleName)

        if (fromModuleCount.has_key(fromModuleName)):
            fromModuleCount[fromModuleName] += 1
        else:
            fromModuleCount[fromModuleName] = 1
        if (toModuleCount.has_key(toModuleName)):
            toModuleCount[toModuleName] += 1
        else:
            toModuleCount[toModuleName] = 1
        outCount = outCount + 1
    if (outCount < 1):
        return fromModuleName
    return None

def scanForImports():
    for sourceFile in filesToProcess:
        importsInFile(sourceFile)

def initializeGlobals():
    global allProcessedModules
    global referencedModules
    global fromModuleCount
    global toModuleCount
    
    allProcessedModules = set([])
    referencedModules = set([])

    fromModuleCount = {}
    toModuleCount = {}
    

def pruneTree():
    global pruneModules
    global unreferencedModules
    global externalModules

    initializeGlobals()
    pruneCount = 0
    pruneModulesLen = 0
    prunedModuleList = []

    alreadyProcessed = []
    for sourceFile in filesToProcess:
        fromModuleName = moduleToDotNode(fileNameToModuleName(sourceFile), optionByPackage)
        if (not fromModuleName in alreadyProcessed):
            alreadyProcessed += [fromModuleName]
            prunedModule = dependenciesInFile(fromModuleName, False)
            if (prunedModule):
                prunedModuleList += [prunedModule]
    pruneModules += prunedModuleList
    pruneCount += len(prunedModuleList)
    
    unreferencedModulesList = allProcessedModules.difference(referencedModules)
    if (optionPrintUnreferenced):
        unreferencedModulesList = unreferencedModulesList.difference(rootsToKeep)
    unreferencedModules += unreferencedModulesList
    pruneCount += len(unreferencedModulesList)

    externalModulesList = referencedModules.difference(allProcessedModules)
    externalModulesList = externalModulesList.difference(set(externalModules))
    externalModulesList = externalModulesList.difference(set(pruneModules))
    externalModules += externalModulesList
    pruneCount += len(externalModulesList)

    return pruneCount

inThisCycle = set([])
inAnyCycle = set([])
visited = {}

debugCycle = False

def isInCycle(moduleName, cycleRoot, debugPrefix):
    global visited

    if (moduleName == cycleRoot):
        if (debugCycle):
            print debugPrefix + "Got to root"
        return True
    if (visited.has_key(moduleName)):
        if (debugCycle):
            print debugPrefix + "Already visited %s, returning %s" % (moduleName, visited[moduleName])
        return visited[moduleName]
    if (moduleName in pruneModules or moduleName in unreferencedModules or moduleName in externalModules):
        if (debugCycle):
            print debugPrefix + "Pruning " + moduleName
        return False
    importList = moduleNameToImportList[moduleName]
    visited[moduleName] = False
    for toModuleName in importList:
        if (debugCycle):
            print debugPrefix + "Descending to " + toModuleName
        if (isInCycle(toModuleName, cycleRoot, debugPrefix + " ")):
            visited[moduleName] = True
            if (debugCycle):
                print debugPrefix + "Part of cycle: %s -> %s" %(moduleName, toModuleName)
            return True
    if (debugCycle):
        print debugPrefix + "Not in cycle: " + moduleName
    return False

def scanForCycles(cycleRoot):
    global visited
    global debugCycle

#    debugCycle = (cycleRoot == "pick a node")

    if (moduleName in pruneModules or moduleName in unreferencedModules or moduleName in externalModules):
        if (debugCycle):
            print "returning right away"
        return
    
    removeArcs = []
    importList = moduleNameToImportList[cycleRoot]
    for toModuleName in importList:
        visited = {}
        if (debugCycle):
            print "------- starting to scan: " + toModuleName
        if (isInCycle(toModuleName, cycleRoot, "")):
            if (debugCycle):
                print "in cycle: " + toModuleName
            pass
        else:
            removeArcs += [toModuleName]
            if (debugCycle):
                print "NOT in cycle: " + toModuleName
    for toModuleName in removeArcs:
        importList.remove(toModuleName)
    moduleNameToImportList[moduleName] = importList
    return

def printTree():
    initializeGlobals()
    print "digraph G {"
    if (optionColorPackages):
        print "    node [style=filled];"
        print '    node [fillcolor="#ff4040"];'
    alreadyProcessed = []
    for sourceFile in filesToProcess:
        fromModuleName = moduleToDotNode(fileNameToModuleName(sourceFile), optionByPackage)
        if (not fromModuleName in alreadyProcessed):
            alreadyProcessed += [fromModuleName]
            dependenciesInFile(fromModuleName, True)
    print "}"
    if (not optionByPackage):
        for key in fromModuleCount.keys():
            if (not toModuleCount.has_key(key)):
                toModuleCount[key] = 0
            print >>sys.stderr, "%06d %06d %s" % (toModuleCount[key], fromModuleCount[key], key)

if (__name__ == '__main__'):
    for opt in sys.argv[1:]:
        if (opt == "--noPrune"):
            optionDontPrune = True
        elif (opt == "--printUnreferenced"):
            optionPrintUnreferenced = True
        elif (opt == "--printTables"):
            optionPrintTables = True
        elif (opt == "--justCycles"):
            optionJustCycles = True
        elif (opt == "--byPackage"):
            optionByPackage = True
        elif (opt == "--colorPackages"):
            optionColorPackages = True
        else:
            filesToProcess += [opt]
    scanForImports()
    if (not optionDontPrune):
        while (pruneTree()):
            pass
    if (optionPrintUnreferenced):
        unreferencedModules.sort()
        for module in unreferencedModules:
            if (not module.endswith("__init__")):
                print module
    elif (optionPrintTables):
        print "\n   Prune\n"
        pruneModules.sort()
        for module in pruneModules:
            print module
        print "\n   Unreferenced\n"
        unreferencedModules.sort()
        for module in unreferencedModules:
            print module
        print "\n   External\n"
        externalModules.sort()
        for module in externalModules:
            print module
    else:
        if (optionJustCycles):
            alreadyProcessed = []
            for sourceFile in filesToProcess:
                moduleName = moduleToDotNode(fileNameToModuleName(sourceFile), optionByPackage)
                if (not moduleName in alreadyProcessed):
                    alreadyProcessed += [moduleName]
                    scanForCycles(moduleName)
            while (pruneTree()):
                pass
        printTree()
