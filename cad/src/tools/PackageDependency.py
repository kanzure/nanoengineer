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

   http://www.graphviz.org
   
"""

import sys
import re
import os.path

from packageData import packageColors
from packageData import packageLevels
from packageData import packageGroupMapping

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
    "bsddb3",
    "bsddb3.dbshelve",
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
    "sim",
    "atombase",
    "quux",
    "xxx",
    "bearing_data",
    "samevals",
    "psurface",
    "zipfile",
    "colorsys",
    ]

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
    # node and edge are reserved words in .dot files
    if (ret == "node"):
        return "_node"
    if (ret == "edge"):
        return "_edge"
    return ret
    
def moduleToDotNode(moduleName, returnPackageName):
    if (returnPackageName):
        if (moduleName in libraryReferences):
            return "library"
        if (isPackage(moduleName)):
            if (packageGroupMapping.has_key(moduleName)):
                return packageGroupMapping[moduleName]
            return moduleName
        mod = moduleName
        while (True):
            i = mod.rfind(".")
            if (i < 0):
                return "top"
            mod = mod[:i]
            if (isPackage(mod)):
                if (packageGroupMapping.has_key(mod)):
                    return packageGroupMapping[mod]
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
    continuationWarning = False
    f = open(fileName)
    for line in f:
        m = fromImportLineRegex.match(line)
        if (m):
            if (continuationWarning or line.rstrip().endswith("\\")):
                continuationWarning = True
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
            if (continuationWarning or line.rstrip().endswith("\\")):
                continuationWarning = True
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
    if (continuationWarning):
        print >>sys.stderr, "WARNING: continued import statement in " + fileName
    if (moduleNameToImportList.has_key(fromModule)):
        # this happens if we're operating by package
        importSet = importSet.union(moduleNameToImportList[fromModule])
    importList = list(importSet)
    importList.sort()
    moduleNameToImportList[fromModule] = importList

nodeColors = {}

packageNodes = []

def createNode(name, fullModuleName):
    if (not optionColorPackages or nodeColors.has_key(name)):
        return
    if (optionByPackage):
        packageName = name
    else:
        packageName = moduleToDotNode(fullModuleName, True)
    if (packageColors.has_key(packageName)):
        nodeColors[name] = packageColors[packageName]
        print '    %s [fillcolor="%s"];' % (name, nodeColors[name])
    else:
        print >>sys.stderr, "undefined package color: " + packageName

def getPackageLevel(packageName):
    if (packageLevels.has_key(packageName)):
        return packageLevels[packageName]
    print >>sys.stderr, "undefined package level: " + packageName
    return 9

def printEdge(fromNode, toNode):
    fn = dotReplacement(fromNode)
    tn = dotReplacement(toNode)
    createNode(fn, fromNode)
    createNode(tn, toNode)
    if (optionByPackage and optionColorPackages):
        fromLevel = getPackageLevel(fromNode)
        toLevel = getPackageLevel(toNode)
        if (fromLevel < toLevel):
            color = "red"
        else:
            color = "black"
        print "    %s -> %s [color=%s];" % (fn, tn, color)
    else:
        print "    %s -> %s;" % (fn, tn)

excludeFromEdges = [
    "prototype",
    ]

excludeToEdges = [
    "library",
    "tools",
    "top",    # only excluded to prevent required relative imports and spurious library references from showing up
    "prototype",
    ]

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

        if (printing and fromModuleName not in excludeFromEdges and toModuleName not in excludeToEdges):
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
